from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ValidationError, Field, field_validator
from .prompts import SYSTEM_PROMPT # We can use the prompt definitions for some hints if needed

class IntentValidation(BaseModel):
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    entities: Dict[str, Any]

    @field_validator("intent")
    @classmethod
    def validate_intent(cls, v: str) -> str:
        valid_intents = ["CLIENT_ONBOARDING", "MEETING_COORDINATION", "FOLLOW_UP_MANAGEMENT", "AMBIGUOUS_INPUT", "OUT_OF_SCOPE"]
        if v not in valid_intents:
            raise ValueError(f"Invalid intent: {v}")
        return v

class WorkflowStep(BaseModel):
    step_id: str
    type: str
    action: str
    owner: str
    priority: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid_types = ["COMMUNICATION", "COORDINATION", "TASK_CREATION", "DATA_RETRIEVAL"]
        if v not in valid_types:
            raise ValueError(f"Invalid step type: {v}")
        return v

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
