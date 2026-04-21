import asyncio
import uuid
import json
from opsai.database import create_db_and_tables, Session, engine
from opsai.models import Orchestration
from opsai.core.orchestrator import Orchestrator
from dotenv import load_dotenv

load_dotenv("opsai/.env")

async def test_full_orchestration():
    # Setup DB
    create_db_and_tables()
    
    # 1. Create Orchestration Record
    raw_input = "We signed Acme Corp. They need onboarding."
    with Session(engine) as session:
        orchestration = Orchestration(raw_input=raw_input)
        session.add(orchestration)
        session.commit()
        session.refresh(orchestration)
        orchestration_id = orchestration.id

    # 2. Run Orchestrator
    print(f"--- Running Full Orchestration for ID: {orchestration_id} ---")
    orchestrator = Orchestrator(orchestration_id)
    
    async for update in orchestrator.run(raw_input):
        print(f"Update: {json.dumps(update, indent=2)}")
        if update["status"] == "FAILED":
            print(f"❌ Pipeline Failed at stage {update['stage']}: {update.get('reason')}")
            return

    # 3. Final Verification
    with Session(engine) as session:
        final_orch = session.get(Orchestration, orchestration_id)
        print(f"Final DB Status: {final_orch.status}")
        assert final_orch.status == "COMPLETED"

    print("✅ Sprint 6 - Full Pipeline Orchestration Success")

if __name__ == "__main__":
    try:
        asyncio.run(test_full_orchestration())
    except Exception as e:
        print(f"❌ Test Failed: {e}")
