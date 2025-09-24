"""Middlewares auxiliares do serviço de API."""
from __future__ import annotations

import logging
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from api_service.run_context import bind_run_id

logger = logging.getLogger(__name__)


class RunIdMiddleware(BaseHTTPMiddleware):
    """Garante que toda requisição possua um run_id em contexto."""

    header_name = "X-Run-Id"

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        run_id = request.headers.get(self.header_name)
        if not run_id:
            run_id = str(uuid.uuid4())
        with bind_run_id(run_id):
            logger.debug("Processando requisição", extra={"path": request.url.path, "run_id": run_id})
            response = await call_next(request)
            response.headers[self.header_name] = run_id
            return response
