from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from dotenv import load_dotenv
import json
import asyncio

# Load environment once at the entry point
load_dotenv()
from contextlib import asynccontextmanager
from opsai.database import create_db_and_tables, get_session, engine
from opsai.models import Orchestration, OrchestrationStatus
from opsai.core.orchestrator import Orchestrator
from opsai.core.dispatcher import Dispatcher
from opsai.core.validation import ValidationService
from opsai.core.drivers.registry import driver_startup_check, registry
import uuid

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: Initialize DB and Check Driver Health
    create_db_and_tables()
    driver_startup_check()
    yield
    # Shutdown logic (optional)

app = FastAPI(title="OpsAI - System of Record", lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "calm", "system": "OpsAI"}

@app.post("/api/orchestrate", response_model=Orchestration)
async def create_orchestration(
    input_text: str, 
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    orchestration = Orchestration(
        raw_input=input_text, 
        organization_id=organization_id,
        user_id=user_id,
        status=OrchestrationStatus.PENDING
    )
    session.add(orchestration)
    session.commit()
    session.refresh(orchestration)
    return orchestration

@app.post("/api/orchestrate/{orchestration_id}/approve")
async def approve_orchestration(
    orchestration_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    orchestration = session.get(Orchestration, orchestration_id)
    if not orchestration:
        raise HTTPException(status_code=404, detail="Orchestration not found")
    
    if orchestration.status != OrchestrationStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=400, detail=f"Cannot approve orchestration in state {orchestration.status}")

    # 1. Staleness Check (Re-run Validation)
    validator = ValidationService()
    if not orchestration.workflow or not validator.validate_workflow(orchestration.workflow.steps):
        orchestration.status = OrchestrationStatus.FAILED
        session.add(orchestration)
        session.commit()
        raise HTTPException(status_code=422, detail="Staleness check failed: Workflow is no longer valid.")

    # 2. Update Status
    orchestration.status = OrchestrationStatus.EXECUTING
    session.add(orchestration)
    session.commit()

    # 3. Trigger Dispatcher in Background
    dispatcher = Dispatcher(orchestration_id, engine, registry)
    background_tasks.add_task(dispatcher.run_pipeline)
    
    return {"status": "SUCCESS", "message": "Orchestration approved and execution started."}

@app.post("/api/orchestrate/{orchestration_id}/reject")
async def reject_orchestration(
    orchestration_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    orchestration = session.get(Orchestration, orchestration_id)
    if not orchestration:
        raise HTTPException(status_code=404, detail="Orchestration not found")
    
    if orchestration.status != OrchestrationStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=400, detail="Only pending orchestrations can be rejected")

    orchestration.status = OrchestrationStatus.REJECTED
    session.add(orchestration)
    session.commit()
    
    return {"status": "SUCCESS", "message": "Orchestration rejected."}

@app.get("/api/orchestrate/{orchestration_id}/stream")
async def stream_orchestration(
    orchestration_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    orchestration = session.get(Orchestration, orchestration_id)
    if not orchestration:
        raise HTTPException(status_code=404, detail="Orchestration not found")

    async def event_generator():
        try:
            orchestrator = Orchestrator(orchestration_id, engine)
            async for update in orchestrator.run(orchestration.raw_input):
                yield f"data: {json.dumps(update)}\n\n"
                await asyncio.sleep(0.1)
        except Exception as e:
            # This will show up in your server terminal
            print(f"CRITICAL STREAM ERROR: {e}")
            yield f"data: {json.dumps({'stage': 'PIPELINE', 'status': 'FAILED', 'reason': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
