import pytest
import uuid
import hashlib
from unittest.mock import MagicMock
from sqlmodel import Session
from opsai.core.drivers.communication.gmail import GmailDriver
from opsai.core.dispatcher import Dispatcher
from opsai.models import StepStatus, OrchestrationStatus

def test_gmail_pii_redaction():
    """Verify that sensitive emails are hashed in audit logs."""
    driver = GmailDriver()
    raw_data = {"provider": "Gmail", "to": "secret@example.com"}
    sanitized = driver.sanitize(raw_data.copy())
    
    assert sanitized["to"] != "secret@example.com"
    assert "REDACTED_" in sanitized["to"]
    assert sanitized["provider"] == "Gmail"

@pytest.mark.asyncio
async def test_dispatcher_idempotency(session: Session):
    """Verify that the dispatcher skips already successful steps."""
    orch_id = uuid.uuid4()
    step_id = "test_step_1"
    
    # 1. Manually create a SUCCESS record in the DB
    success_record = StepStatus(
        orchestration_id=orch_id,
        step_id=step_id,
        status="SUCCESS"
    )
    session.add(success_record)
    session.commit()
    
    # 2. Setup Dispatcher
    mock_registry = MagicMock()
    dispatcher = Dispatcher(orch_id, session.bind, mock_registry)
    
    # 3. Call _process_single_step
    # Note: We pass a Dummy orchestration object
    mock_orch = MagicMock()
    step_data = {"step_id": step_id, "type": "COMMUNICATION"}
    
    result = await dispatcher._process_single_step(session, mock_orch, step_data)
    
    # 4. Assert
    assert result is True # Should succeed immediately
    # Ensure registry.get_driver was NOT called (proving the step was skipped)
    mock_registry.get_driver.assert_not_called()
