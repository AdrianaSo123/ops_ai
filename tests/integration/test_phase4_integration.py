import pytest
from opsai.core.decision_engine import DecisionEngine
from opsai.core.retry_handler import RetryHandler
from opsai.core.escalation_handler import EscalationHandler
from opsai.core.persistence import PersistenceRepository, PersistenceService
import tempfile
import shutil
import os

def test_decision_engine_integration():
    engine = DecisionEngine()
    step = {
        "on_success": "step2",
        "retry_policy": {"max_retries": 1},
        "on_failure": "escalate",
        "conditions": [{"if": "retry_count > 0", "then": "escalate"}]
    }
    context = {"retry_count": 1}
    assert engine.evaluate_step(step, "FAILED", context) == "escalate"

def test_retry_handler_integration():
    handler = RetryHandler()
    policy = {"strategy": "exponential_backoff", "base_delay_seconds": 1}
    assert handler.get_delay(policy, 2) == 4

def test_escalation_handler_integration():
    called = []
    def create_task(context):
        called.append("task")
        return "task created"
    handler = EscalationHandler({"create_task": create_task})
    escalation = {"actions": [{"type": "create_task"}]}
    results = handler.escalate(escalation, {})
    assert results == ["task created"]
    assert called == ["task"]

def test_persistence_integration():
    temp_dir = tempfile.mkdtemp()
    try:
        repo = PersistenceRepository(base_dir=temp_dir)
        service = PersistenceService(repo)
        workflow_id = "integration123"
        state = {"workflow_id": workflow_id, "steps": [1], "status": "running"}
        service.save_state(workflow_id, state)
        loaded = service.load_state(workflow_id)
        assert loaded == state
    finally:
        shutil.rmtree(temp_dir)

def test_edge_case_retry_exceeds_max():
    engine = DecisionEngine()
    step = {"retry_policy": {"max_retries": 1}, "on_failure": "escalate"}
    context = {"retry_count": 2}
    assert engine.evaluate_step(step, "FAILED", context) == "escalate"

def test_edge_case_missing_step():
    engine = DecisionEngine()
    step = {}
    assert engine.evaluate_step(step, "SUCCESS") == "end"

def test_edge_case_corrupted_state():
    temp_dir = tempfile.mkdtemp()
    try:
        repo = PersistenceRepository(base_dir=temp_dir)
        service = PersistenceService(repo)
        workflow_id = "corrupt"
        file_path = os.path.join(temp_dir, f"{workflow_id}.json")
        with open(file_path, "w") as f:
            f.write("not a json")
        assert service.load_state(workflow_id) is None
    finally:
        shutil.rmtree(temp_dir)
