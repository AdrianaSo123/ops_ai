"""
escalation_handler.py — Escalation Handler for OpsAI Phase 4
Executes escalation actions (create_task, log_incident, send_alert).
Follows SOLID principles and is fully type-annotated and documented.
"""
from typing import Dict, Any, List

from typing import Dict, Any, List, Callable

class EscalationHandler:
    """
    Handles escalation actions for workflow steps. Actions are injected for testability.
    """
    actions: Dict[str, Callable[[Dict[str, Any]], str]]

    def __init__(self, actions: Dict[str, Callable[[Dict[str, Any]], str]]) -> None:
        """
        Initialize the EscalationHandler.
        Args:
            actions (Dict[str, Callable]): Mapping of action type to callable.
        """
        self.actions = actions

    def escalate(self, escalation: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """
        Execute escalation actions. Returns list of results.

        Args:
            escalation (Dict[str, Any]): Escalation definition with actions.
            context (Dict[str, Any]): Context for action execution.

        Returns:
            List[str]: Results of escalation actions.
        """
        results: List[str] = []
        for action in escalation.get("actions", []):
            action_type = action["type"]
            handler = self.actions.get(action_type)
            if handler:
                results.append(handler(context))
            else:
                results.append(f"Unknown action: {action_type}")
        return results
