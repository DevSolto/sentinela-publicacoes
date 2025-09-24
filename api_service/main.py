"""Aplicação FastAPI principal do serviço de publicações."""
from __future__ import annotations

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from api_service.logging_config import configure_logging
from api_service.middleware import RunIdMiddleware
from api_service.routers import comments, posts, profiles, runs

configure_logging()

app = FastAPI(
    title="Sentinela Publicações",
    description=(
        "API responsável por disponibilizar informações de publicações, "
        "comentários, perfis e execuções de coletas."
    ),
    version="0.1.0",
)

app.add_middleware(RunIdMiddleware)

Instrumentator().instrument(app).expose(app, include_in_schema=False)

app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(profiles.router)
app.include_router(runs.router)


@app.get("/health", tags=["Utilidades"], summary="Verificação de saúde")
def health_check() -> dict[str, str]:
    """Endpoint simples para verificação de saúde da aplicação."""
    return {"status": "ok"}
