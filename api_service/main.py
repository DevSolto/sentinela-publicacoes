"""Aplicação FastAPI principal do serviço de publicações."""
from fastapi import FastAPI

from api_service.routers import comments, posts, profiles, runs

app = FastAPI(
    title="Sentinela Publicações",
    description=(
        "API responsável por disponibilizar informações de publicações, "
        "comentários, perfis e execuções de coletas."
    ),
    version="0.1.0",
)

app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(profiles.router)
app.include_router(runs.router)


@app.get("/health", tags=["Utilidades"], summary="Verificação de saúde")
def health_check() -> dict[str, str]:
    """Endpoint simples para verificação de saúde da aplicação."""
    return {"status": "ok"}
