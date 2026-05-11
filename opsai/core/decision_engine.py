"""
decision_engine.py — Decision Engine for OpsAI Phase 4
Evaluates step outcomes, applies conditional logic, and determines next action.
Follows SOLID principles and is fully type-annotated and documented.
"""
from typing import Dict, Any, Optional

from typing import Dict, Any, Optional

class DecisionEngine:
    """
    Decision engine for workflow steps. Determines next action based on result, conditions, and policy.
    """

    def evaluate_step(
        self,
        step: Dict[str, Any],
        result: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Evaluate the outcome of a step and determine the next action.

        Args:
            step (Dict[str, Any]): The step definition.
            result (str): The result of the step execution ('SUCCESS', 'FAILED', etc.).
            context (Optional[Dict[str, Any]]): Additional context for evaluation.

        Returns:
            str: The next action ('next_step_id', 'retry', 'escalate', or 'end').
        """
        # Evaluate conditions first (override default behavior)
        if step.get("conditions"):
            for cond in step["conditions"]:
                if self._evaluate_condition(cond, context or {}):
                    return cond["then"]
        if result == "SUCCESS":
            return step.get("on_success") or "end"
        elif result == "FAILED":
            retry_policy = step.get("retry_policy", {})
            retries = (context or {}).get("retry_count", 0)
            if retries < retry_policy.get("max_retries", 0):
                return "retry"
            else:
                return step.get("on_failure") or "escalate"
        return "end"

    def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition dict against the context.

        Example: {"if": "retry_count > 2", "then": "escalate"}

        Args:
            condition (Dict[str, Any]): The condition to evaluate.
            context (Dict[str, Any]): The context for evaluation.

        Returns:
            bool: True if the condition is met, False otherwise.
        """
        try:
            return eval(condition["if"], {}, context)
        except Exception:
            return False
