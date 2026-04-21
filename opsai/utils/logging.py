import logging
import json
import uuid
from typing import Any, Dict

class ContextLogger:
    def __init__(self, orchestration_id: uuid.UUID):
        self.orchestration_id = orchestration_id
        self.logger = logging.getLogger("opsai")
        self.logger.setLevel(logging.INFO)
        
        # Ensure we don't add multiple handlers if initialized twice
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, stage: str, message: str, extra: Dict[str, Any] = None):
        """
        Logs an info message with orchestration context.
        """
        log_data = {
            "orchestration_id": str(self.orchestration_id),
            "stage": stage,
            "message": message,
            "extra": extra or {}
        }
        self.logger.info(json.dumps(log_data))

    def error(self, stage: str, message: str, error: Exception = None):
        """
        Logs an error message with orchestration context.
        """
        log_data = {
            "orchestration_id": str(self.orchestration_id),
            "stage": stage,
            "message": message,
            "error": str(error) if error else None
        }
        self.logger.error(json.dumps(log_data))
