from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, JSON, Column
import uuid

class OrchestrationStatus(str, Enum):
    PENDING = "PENDING"
    INTERPRETING = "INTERPRETING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class StepType(str, Enum):
    COMMUNICATION = "COMMUNICATION"
    COORDINATION = "COORDINATION"
    TASK_CREATION = "TASK_CREATION"
    DATA_RETRIEVAL = "DATA_RETRIEVAL"

class Orchestration(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(index=True)
    user_id: uuid.UUID = Field(index=True)
    raw_input: str
    intent: Optional[str] = None
    status: OrchestrationStatus = Field(default=OrchestrationStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    workflow: Optional["WorkflowInstance"] = Relationship(back_populates="orchestration")
    snapshots: List["ContextSnapshot"] = Relationship(back_populates="orchestration")
    step_history: List["StepStatus"] = Relationship(back_populates="orchestration")

class StepStatus(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    orchestration_id: uuid.UUID = Field(foreign_key="orchestration.id")
    step_id: str
    status: str # PENDING, EXECUTING, SUCCESS, FAILED
    result: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    orchestration: Orchestration = Relationship(back_populates="step_history")

class WorkflowInstance(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    orchestration_id: uuid.UUID = Field(foreign_key="orchestration.id", unique=True)
    steps: List[Dict[str, Any]] = Field(sa_column=Column(JSON))
    version: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    orchestration: Orchestration = Relationship(back_populates="workflow")

class ContextSnapshot(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    orchestration_id: uuid.UUID = Field(foreign_key="orchestration.id")
    stage: OrchestrationStatus
    data: Dict[str, Any] = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    orchestration: Orchestration = Relationship(back_populates="snapshots")
