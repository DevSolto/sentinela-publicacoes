"""Serviços que concentram regras de negócio de comentários."""
from __future__ import annotations

from typing import List

from api_service.repositories.comments import CommentRepository
from api_service.schemas.posts import ComentarioPublicacao


class CommentService:
    """Orquestra a recuperação e transformação de comentários."""

    def __init__(self, repository: CommentRepository) -> None:
        self._repository = repository

    def listar_por_shortcode(self, shortcode: str) -> List[ComentarioPublicacao]:
        """Retorna os comentários convertidos para o esquema público."""

        registros = self._repository.listar_por_shortcode(shortcode)
        return [
            ComentarioPublicacao(
                identificador=str(item.get("id")),
                texto=item.get("text", ""),
                usuario=item.get("user", ""),
                criado_em=item.get("created_at"),
            )
            for item in registros
            if item
        ]
