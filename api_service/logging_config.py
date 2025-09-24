"""Configuração de logging estruturado para o serviço FastAPI."""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

from api_service.run_context import get_run_id


class JsonFormatter(logging.Formatter):
    """Formatter que produz logs em JSON com correlação de run_id."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401 - assinatura imposta
        payload: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "run_id": getattr(record, "run_id", get_run_id()),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)
        for key, value in record.__dict__.items():
            if key.startswith("_") or key in payload:
                continue
            if key in {"args", "msg", "message", "levelno", "levelname", "name"}:
                continue
            payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    """Instala um handler único com formatação JSON."""

    level = os.getenv("API_LOG_LEVEL", "INFO").upper()
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


__all__ = ["configure_logging", "JsonFormatter"]
