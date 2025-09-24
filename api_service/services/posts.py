"""Serviços que concentram as regras de negócio para publicações."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional

from api_service.repositories.posts import PostRepository
from api_service.schemas.posts import FiltroConsultaPosts, PostDetalhado
from api_service.services.comments import CommentService


class PostService:
    """Orquestra a busca e preparação dos dados de publicações."""

    def __init__(
        self,
        post_repository: PostRepository,
        comment_service: CommentService,
    ) -> None:
        self._post_repository = post_repository
        self._comment_service = comment_service

    def listar_posts(
        self,
        capturado_inicio: Optional[datetime] = None,
        capturado_fim: Optional[datetime] = None,
        hashtags: Optional[Iterable[str]] = None,
        pagina: int = 1,
        tamanho_pagina: int = 20,
        ordenar_decrescente: bool = True,
    ) -> List[PostDetalhado]:
        """Realiza a busca paginada das publicações com filtros aplicados."""

        filtros = FiltroConsultaPosts(
            capturado_inicio=capturado_inicio,
            capturado_fim=capturado_fim,
            hashtags=list(hashtags or []),
            pagina=pagina,
            tamanho_pagina=tamanho_pagina,
            ordenar_decrescente=ordenar_decrescente,
        )
        registros = self._post_repository.listar_posts(
            capturado_inicio=filtros.capturado_inicio,
            capturado_fim=filtros.capturado_fim,
            hashtags=filtros.hashtags,
            pagina=filtros.pagina,
            tamanho_pagina=filtros.tamanho_pagina,
            ordenar_decrescente=filtros.ordenar_decrescente,
        )

        return [self._mapear_post(registro) for registro in registros]

    def obter_post_por_shortcode(self, shortcode: str) -> Optional[PostDetalhado]:
        """Recupera uma publicação específica juntamente com seus comentários."""

        registro = self._post_repository.buscar_por_shortcode(shortcode)
        if not registro:
            return None
        return self._mapear_post(registro)

    def _mapear_post(self, registro: dict) -> PostDetalhado:
        comentarios = self._comment_service.listar_por_shortcode(
            registro.get("shortcode", "")
        )
        return PostDetalhado(
            shortcode=registro.get("shortcode"),
            legenda=registro.get("caption"),
            hashtags=registro.get("hashtags", []),
            capturado_em=registro.get("taken_at"),
            url_midias=registro.get("media_urls", []),
            comentarios=comentarios,
        )
