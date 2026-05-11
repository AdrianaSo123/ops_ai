from typing import Dict, Any, Optional
from datetime import datetime
import uuid
from sqlmodel import Session, select
from sqlmodel.sql._expression_select_cls import SelectOfScalar
from ..models import ContextSnapshot, OrchestrationStatus, Orchestration
from ..database import engine

class ContextManager:
    """
    Manages the orchestration context lifecycle, including saving and retrieving context snapshots for auditability.
    """
    orchestration_id: uuid.UUID
    session: Session

    def __init__(self, orchestration_id: uuid.UUID, engine) -> None:
        """
        Initialize the ContextManager.
        Args:
            orchestration_id (uuid.UUID): The orchestration this context is for.
            engine: SQLModel database engine.
        """
        self.orchestration_id = orchestration_id
        self.session = Session(engine)

    def save_snapshot(self, stage: OrchestrationStatus, data: Dict[str, Any]) -> ContextSnapshot:
        """
        Creates an immutable snapshot of the context at a specific stage.
        Args:
            stage (OrchestrationStatus): The pipeline stage.
            data (Dict[str, Any]): The context data to snapshot.
        Returns:
            ContextSnapshot: The created snapshot instance.
        """
        snapshot = ContextSnapshot(
            orchestration_id=self.orchestration_id,
            stage=stage,
            data=data,
            created_at=datetime.utcnow()
        )
        self.session.add(snapshot)
        # Update orchestration status and updated_at
        orchestration: Orchestration | None = self.session.get(Orchestration, self.orchestration_id)
        if orchestration:
            orchestration.status = stage
            orchestration.updated_at = datetime.utcnow()
            self.session.add(orchestration)
        self.session.commit()
        return snapshot

    def get_latest_context(self) -> Dict[str, Any]:
        """
        Retrieves the most recent context snapshot for the orchestration.
        Returns:
            Dict[str, Any]: The latest context data, or empty dict if none found.
        """
        statement: SelectOfScalar[ContextSnapshot] = (
            select(ContextSnapshot)
            .where(ContextSnapshot.orchestration_id == self.orchestration_id)
            .order_by(ContextSnapshot.created_at.desc())
        )
        snapshot: ContextSnapshot | None = self.session.exec(statement).first()
        return snapshot.data if snapshot else {}

    def close(self) -> None:
        """
        Closes the database session.
        """
        self.session.close()
