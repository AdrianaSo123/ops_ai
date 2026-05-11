from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ValidationError, Field, field_validator
from .prompts import SYSTEM_PROMPT # We can use the prompt definitions for some hints if needed
from ..models import OrchestrationStatus, StepType


class IntentValidation(BaseModel):
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    entities: Dict[str, Any]


class WorkflowStep(BaseModel):
    step_id: str
    type: StepType
    action: str
    owner: str
    priority: str

class WorkflowValidation(BaseModel):
    workflow: List[WorkflowStep]

class ValidationService:
    """
    Provides validation utilities for interpretation, workflow, and execution payloads.
    """

    @staticmethod
    def validate_interpretation(data: Dict[str, Any]) -> bool:
        """
        Validates the output of the Interpretation Layer.

        Args:
            data (Dict[str, Any]): The interpretation data to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            IntentValidation(**data)
            return True
        except ValidationError:
            return False

    @staticmethod
    def validate_workflow(data: List[Dict[str, Any]]) -> bool:
        """
        Validates the output of the Planning Layer.

        Args:
            data (List[Dict[str, Any]]): The workflow data to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            WorkflowValidation(workflow=data)
            return True
        except ValidationError:
            return False

    @staticmethod
    def validate_payloads(data: List[Dict[str, Any]]) -> bool:
        """
        Validates the output of the Execution Layer.

        Args:
            data (List[Dict[str, Any]]): The payloads to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        # Minimum requirement: each payload has step_id and payload content
        try:
            for item in data:
                if "step_id" not in item or "payload" not in item:
                    return False
            return True
        except Exception:
            return False

    @staticmethod
    def workflow_payload_issues(steps: List[Dict[str, Any]]) -> List[str]:
        """
        Returns blocking issues for hydrated workflow payloads.

        Args:
            steps (List[Dict[str, Any]]): The workflow steps to check.

        Returns:
            List[str]: List of blocking issues found.
        """
        issues: List[str] = []
        for step in steps:
            step_type = step.get("type")
            if step_type == StepType.COMMUNICATION:
                payload = step.get("payload") or {}
                if not payload.get("to"):
                    step_id = step.get("step_id", "unknown")
                    issues.append(f'Step "{step_id}" is missing recipient email.')
        return issues
