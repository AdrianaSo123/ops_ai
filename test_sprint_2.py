import uuid
from opsai.database import create_db_and_tables, Session, engine
from opsai.models import Orchestration, OrchestrationStatus
from opsai.core.context import ContextManager

def test_context_snapshotting():
    # Setup DB
    create_db_and_tables()
    
    with Session(engine) as session:
        # 1. Create Orchestration with required fields
        orchestration = Orchestration(
            raw_input="Test input",
            organization_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            status=OrchestrationStatus.PENDING
        )
        session.add(orchestration)
        session.commit()
        session.refresh(orchestration)
        orchestration_id = orchestration.id

    # 2. Use ContextManager to save snapshot
    mgr = ContextManager(orchestration_id)
    test_data = {"intent": "CLIENT_ONBOARDING", "client": "Acme Corp"}
    
    print(f"--- Saving Snapshot for Stage: {OrchestrationStatus.INTERPRETING} ---")
    mgr.save_snapshot(OrchestrationStatus.INTERPRETING, test_data)
    
    # 3. Verify
    latest = mgr.get_latest_context()
    print(f"Latest Context: {latest}")
    assert latest["client"] == "Acme Corp"
    
    # Check DB status
    with Session(engine) as session:
        db_orch = session.get(Orchestration, orchestration_id)
        print(f"Orchestration Status: {db_orch.status}")
        assert db_orch.status == OrchestrationStatus.INTERPRETING
    
    mgr.close()
    print("✅ Sprint 2 - Context Snapshots Success")

if __name__ == "__main__":
    try:
        test_context_snapshotting()
    except Exception as e:
        print(f"❌ Test Failed: {e}")
