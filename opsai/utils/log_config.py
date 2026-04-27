import logging
import os
import sys
import json
from typing import Any, TextIO

class JsonFormatter(logging.Formatter):
    def format(self, record) -> str:
        log_record: dict[str, str] = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        if hasattr(record, 'orchestration_id'):
            log_record['orchestration_id'] = record.orchestration_id
        if hasattr(record, 'stage'):
            log_record['stage'] = record.stage
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
