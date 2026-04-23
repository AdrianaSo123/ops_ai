import pytest
from opsai.core.decision_engine import DecisionEngine

def test_success_branch():
    engine = DecisionEngine()
    step = {"on_success": "step2"}
    assert engine.evaluate_step(step, "SUCCESS") == "step2"

def test_failure_with_retry():
    engine = DecisionEngine()
    step = {"retry_policy": {"max_retries": 2}, "on_failure": "escalate"}
    context = {"retry_count": 1}
    assert engine.evaluate_step(step, "FAILED", context) == "retry"

def test_failure_escalate():
    engine = DecisionEngine()
    step = {"retry_policy": {"max_retries": 2}, "on_failure": "escalate"}
    context = {"retry_count": 2}
    assert engine.evaluate_step(step, "FAILED", context) == "escalate"

def test_condition_override():
    engine = DecisionEngine()
    step = {
        "conditions": [{"if": "retry_count > 2", "then": "escalate"}],
        "on_failure": "retry"
    }
    context = {"retry_count": 3}
    assert engine.evaluate_step(step, "FAILED", context) == "escalate"
