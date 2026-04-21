from typing import Dict, Any, Optional
from datetime import datetime
import uuid
from sqlmodel import Session, select
from ..models import ContextSnapshot, OrchestrationStatus, Orchestration
from ..database import engine

class ContextManager:
    def __init__(self, orchestration_id: uuid.UUID, engine):
        self.orchestration_id = orchestration_id
        self.session = Session(engine)

    def save_snapshot(self, stage: OrchestrationStatus, data: Dict[str, Any]):
        """
        Creates an immutable snapshot of the context at a specific stage.
        """
        snapshot = ContextSnapshot(
            orchestration_id=self.orchestration_id,
            stage=stage,
            data=data,
            created_at=datetime.utcnow()
        )
        self.session.add(snapshot)
        
        # Update orchestration status and updated_at
        orchestration = self.session.get(Orchestration, self.orchestration_id)
        if orchestration:
            orchestration.status = stage
            orchestration.updated_at = datetime.utcnow()
            self.session.add(orchestration)
            
        self.session.commit()
        return snapshot

    def get_latest_context(self) -> Dict[str, Any]:
        """
        Retrieves the most recent context snapshot for the orchestration.
        """
        statement = (
            select(ContextSnapshot)
            .where(ContextSnapshot.orchestration_id == self.orchestration_id)
            .order_by(ContextSnapshot.created_at.desc())
        )
        snapshot = self.session.exec(statement).first()
        return snapshot.data if snapshot else {}

    def close(self):
        self.session.close()
