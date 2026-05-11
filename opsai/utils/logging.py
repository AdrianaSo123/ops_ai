import logging
import uuid
from typing import Any, Dict

import random
import string

def redact_pii(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: redact_pii(v) for k, v in data.items() if not k.lower() in {"email", "password", "token", "ssn", "phone", "address"}}
    if isinstance(data, list):
        return [redact_pii(v) for v in data]
    if isinstance(data, str) and ("@" in data or len(data) > 30):
        return "[REDACTED]"
    return data

def generate_trace_id() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

class ContextLogger:
    def __init__(self, orchestration_id: uuid.UUID) -> None:
        self.orchestration_id: uuid.UUID = orchestration_id
        self.logger: logging.Logger = logging.getLogger("opsai")

    def info(self, stage: str, message: str, extra: Dict[str, Any] = None, trace_id: str = None) -> None:
        trace_id = trace_id or generate_trace_id()
        self.logger.info(message, extra={
            'orchestration_id': str(self.orchestration_id),
            'stage': stage,
            'trace_id': trace_id,
            'extra': redact_pii(extra or {})
        })

    def error(self, stage: str, message: str, error: Exception = None, trace_id: str = None) -> None:
        trace_id = trace_id or generate_trace_id()
        self.logger.error(message, extra={
            'orchestration_id': str(self.orchestration_id),
            'stage': stage,
            'trace_id': trace_id,
            'error': str(error) if error else None
        })
