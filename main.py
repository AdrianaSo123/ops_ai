from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse, JSONResponse
def error_response(type_: str, message: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "type": type_,
                "message": message
            }
        }
    )

# Custom exception handler for HTTPException to standardize error format
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler

app = FastAPI(title="OpsAI - System of Record", lifespan=lifespan)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return error_response("HTTPException", detail, status_code=exc.status_code)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response("ValidationError", str(exc), status_code=422)
from sqlmodel import Session
from dotenv import load_dotenv
from opsai.utils.log_config import configure_logging
import json
import asyncio

load_dotenv()
configure_logging()
from contextlib import asynccontextmanager
from opsai.database import create_db_and_tables, get_session, engine
from opsai.models import Orchestration, OrchestrationStatus, StepStatus, WorkflowInstance
from fastapi.encoders import jsonable_encoder
# --- Orchestration List Endpoint ---
@app.get("/api/orchestrations")
async def list_orchestrations(session: Session = Depends(get_session)):
    orchestrations = session.exec(select(Orchestration)).all()
    return jsonable_encoder(orchestrations)

# --- Orchestration Detail & Step History Endpoint ---
@app.get("/api/orchestrations/{orchestration_id}")
async def orchestration_detail(orchestration_id: str, session: Session = Depends(get_session)):
    orchestration = session.get(Orchestration, orchestration_id)
    if not orchestration:
        return error_response("NotFound", "Orchestration not found", status_code=404)
    # Get workflow instance and step history
    workflow = session.exec(select(WorkflowInstance).where(WorkflowInstance.orchestration_id == orchestration_id)).first()
    steps = session.exec(select(StepStatus).where(StepStatus.orchestration_id == orchestration_id)).all()
    return {
        "orchestration": jsonable_encoder(orchestration),
        "workflow": jsonable_encoder(workflow),
        "steps": jsonable_encoder(steps)
    }
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
        return error_response("NotFound", "Orchestration not found", status_code=404)
    
    if orchestration.status != OrchestrationStatus.PENDING_APPROVAL:
        return error_response("InvalidState", f"Cannot approve orchestration in state {orchestration.status}", status_code=400)

    # 1. Staleness Check (Re-run Validation)
    validator = ValidationService()
    if not orchestration.workflow or not validator.validate_workflow(orchestration.workflow.steps):
        orchestration.status = OrchestrationStatus.FAILED
        session.add(orchestration)
        session.commit()
        return error_response("StalenessCheckFailed", "Workflow is no longer valid.", status_code=422)

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
        return error_response("NotFound", "Orchestration not found", status_code=404)
    
    if orchestration.status != OrchestrationStatus.PENDING_APPROVAL:
        return error_response("InvalidState", "Only pending orchestrations can be rejected", status_code=400)

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
        return error_response("NotFound", "Orchestration not found", status_code=404)

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
