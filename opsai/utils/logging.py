import logging
import uuid
from typing import Any, Dict

class ContextLogger:
    def __init__(self, orchestration_id: uuid.UUID) -> None:
        self.orchestration_id: uuid.UUID = orchestration_id
        self.logger: logging.Logger = logging.getLogger("opsai")

    def info(self, stage: str, message: str, extra: Dict[str, Any] = None) -> None:
        self.logger.info(message, extra={
            'orchestration_id': str(self.orchestration_id),
            'stage': stage,
            'extra': extra or {}
        })

    def error(self, stage: str, message: str, error: Exception = None) -> None:
        self.logger.error(message, extra={
            'orchestration_id': str(self.orchestration_id),
            'stage': stage,
            'error': str(error) if error else None
        })
