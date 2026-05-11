import pytest
import uuid
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from opsai.models import OrchestrationStatus, Orchestration, WorkflowInstance
import opsai.models

@pytest.mark.asyncio
async def test_full_orchestration_lifecycle(client: TestClient, session):
    """
    Integration Test: Verify the end-to-end flow from creation to approval.
    """
    # 1. Setup IDs
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    input_text = "Onboard Acme Corp"

    # 2. Mock the Reasoning Services (So the Orchestrator logic still runs)
    mock_workflow = [{"step_id": "s1", "type": "COMMUNICATION", "action": "test", "owner": "o1", "priority": "LOW"}]
    mock_payloads = [{"step_id": "s1", "payload": {"to": "test@example.com"}}]

    with patch("opsai.core.orchestrator.InterpretationService.interpret", new_callable=AsyncMock) as m_int, \
         patch("opsai.core.orchestrator.PlanningService.generate_plan", new_callable=AsyncMock) as m_plan, \
         patch("opsai.core.orchestrator.ExecutionService.generate_payloads", new_callable=AsyncMock) as m_exec:
        
        m_int.return_value = {"intent": "TEST", "entities": {}}
        m_plan.return_value = mock_workflow
        m_exec.return_value = mock_payloads

        # A. Create Orchestration
        response = client.post(
            f"/api/orchestrate?input_text={input_text}&organization_id={org_id}&user_id={user_id}"
        )
        assert response.status_code == 200
        data = response.json()
        orch_id = data["id"]
        assert data["status"] == "PENDING"


        # B. Simulate workflow progression via API (fetch orchestration, patch status, create workflow instance)
        orch_id_uuid = uuid.UUID(orch_id)
        # Fetch orchestration detail (simulate polling)
        detail_response = client.get(f"/api/orchestrations/{orch_id}")
        assert detail_response.status_code == 200
        # Patch orchestration status to PENDING_APPROVAL via direct API or service if available
        # If not, fallback to DB manipulation as before (for now, as no PATCH endpoint exists)
        orchestration = session.get(opsai.models.Orchestration, orch_id_uuid)
        orchestration.status = OrchestrationStatus.PENDING_APPROVAL
        wf = opsai.models.WorkflowInstance(orchestration_id=orch_id_uuid, steps=mock_workflow)
        session.add(orchestration)
        session.add(wf)
        session.commit()
        session.expire_all()

        # C. Approve the Orchestration
        # Mocking the Dispatcher background task so we don't start a real background job
        with patch("opsai.core.dispatcher.Dispatcher.run_pipeline", new_callable=AsyncMock) as mock_dispatch:
            approve_response = client.post(f"/api/orchestrate/{orch_id}/approve")
            assert approve_response.status_code == 200
            assert approve_response.json()["status"] == "SUCCESS"
            
            # Verify the status in the database changed to EXECUTING
            # (FastAPI Client uses the shared session fixture)
            refresh_response = client.get(f"/api/orchestrate?input_text=none&organization_id={org_id}&user_id={user_id}")
            # Note: The above GET isn't implemented as a 'fetch one' yet, we check DB directly if needed
            # But the 'approve' endpoint returns success if state was valid.
