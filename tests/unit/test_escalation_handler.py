import pytest
from opsai.core.escalation_handler import EscalationHandler

def test_escalation_handler_executes_actions():
    called = []
    def create_task(context):
        called.append("task")
        return "task created"
    def log_incident(context):
        called.append("log")
        return "incident logged"
    handler = EscalationHandler({"create_task": create_task, "log_incident": log_incident})
    escalation = {"actions": [{"type": "create_task"}, {"type": "log_incident"}]}
    results = handler.escalate(escalation, {})
    assert results == ["task created", "incident logged"]
    assert called == ["task", "log"]

def test_escalation_handler_unknown_action():
    handler = EscalationHandler({})
    escalation = {"actions": [{"type": "unknown"}]}
    results = handler.escalate(escalation, {})
    assert results == ["Unknown action: unknown"]
