"""Rotas de acesso a comentários de publicações."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from api_service.repositories.comments import CommentRepository
from api_service.schemas.posts import ComentarioPublicacao
from api_service.services.comments import CommentService

router = APIRouter(prefix="/comments", tags=["Comentários"])


def obter_servico_comentarios() -> CommentService:
    """Instancia o serviço de comentários com repositório padrão."""

    return CommentService(CommentRepository())


@router.get(
    "/{shortcode}",
    response_model=List[ComentarioPublicacao],
    summary="Listar comentários de uma publicação",
)
def listar_comentarios(
    shortcode: str, servico: CommentService = Depends(obter_servico_comentarios)
) -> List[ComentarioPublicacao]:
    """Retorna os comentários associados ao shortcode informado."""

    return servico.listar_por_shortcode(shortcode)
