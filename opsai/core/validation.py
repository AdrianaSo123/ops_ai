from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ValidationError, Field, field_validator
from .prompts import SYSTEM_PROMPT # We can use the prompt definitions for some hints if needed
from ..models import OrchestrationStatus, StepType


class IntentValidation(BaseModel):
    intent: OrchestrationStatus
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
    @staticmethod
    def validate_interpretation(data: Dict[str, Any]) -> bool:
        """
        Validates the output of the Interpretation Layer.
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
        """
        # Minimum requirement: each payload has step_id and payload content
        try:
            for item in data:
                if "step_id" not in item or "payload" not in item:
                    return False
            return True
        except Exception:
            return False
