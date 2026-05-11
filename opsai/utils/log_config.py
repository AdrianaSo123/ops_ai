import logging
import os
import sys
import json
from typing import Any, TextIO


from .logging import redact_pii

class JsonFormatter(logging.Formatter):
    def format(self, record) -> str:
        log_record: dict[str, Any] = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        if hasattr(record, 'orchestration_id'):
            log_record['orchestration_id'] = record.orchestration_id
        if hasattr(record, 'stage'):
            log_record['stage'] = record.stage
        if hasattr(record, 'trace_id'):
            log_record['trace_id'] = record.trace_id
        if hasattr(record, 'extra'):
            log_record['extra'] = redact_pii(record.extra)
        if hasattr(record, 'error'):
            log_record['error'] = record.error
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def configure_logging() -> None:
    log_level: str = os.getenv('OPSAI_LOG_LEVEL', 'INFO').upper()
    log_format: str = os.getenv('OPSAI_LOG_FORMAT', 'json')
    root_logger: logging.Logger = logging.getLogger()
    root_logger.handlers.clear()
    handler: logging.StreamHandler[TextIO | Any] = logging.StreamHandler(sys.stdout)
    if log_format == 'json':
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)
