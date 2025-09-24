"""Rotas responsáveis por expor publicações."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from api_service.repositories.comments import CommentRepository
from api_service.repositories.posts import PostRepository
from api_service.schemas.posts import PostDetalhado
from api_service.services.comments import CommentService
from api_service.services.posts import PostService

router = APIRouter(prefix="/posts", tags=["Publicações"])


def obter_servico_posts() -> PostService:
    """Instancia o serviço de publicações com repositórios padrão."""

    return PostService(
        PostRepository(),
        CommentService(CommentRepository()),
    )


@router.get("/", response_model=List[PostDetalhado], summary="Listar publicações")
def listar_posts(
    taken_at_inicio: Optional[datetime] = Query(
        None,
        description="Filtra publicações capturadas a partir da data informada",
    ),
    taken_at_fim: Optional[datetime] = Query(
        None, description="Filtra publicações capturadas até a data informada"
    ),
    hashtags: List[str] = Query(
        default_factory=list,
        description="Hashtags que devem estar presentes na publicação",
    ),
    ordenacao: str = Query(
        "desc",
        pattern="^(asc|desc)$",
        description="Define a ordenação da data de captura (asc ou desc)",
    ),
    pagina: int = Query(1, ge=1, description="Número da página solicitada"),
    tamanho_pagina: int = Query(
        20, ge=1, le=100, description="Quantidade de itens por página"
    ),
    servico: PostService = Depends(obter_servico_posts),
) -> List[PostDetalhado]:
    """Retorna publicações com filtros por data, hashtags e ordenação."""

    ordenar_descrescente = ordenacao != "asc"
    return servico.listar_posts(
        capturado_inicio=taken_at_inicio,
        capturado_fim=taken_at_fim,
        hashtags=hashtags,
        pagina=pagina,
        tamanho_pagina=tamanho_pagina,
        ordenar_decrescente=ordenar_descrescente,
    )


@router.get(
    "/{shortcode}",
    response_model=PostDetalhado,
    summary="Detalhar publicação",
)
def obter_post(
    shortcode: str, servico: PostService = Depends(obter_servico_posts)
) -> PostDetalhado:
    """Retorna os detalhes de uma publicação única."""

    post = servico.obter_post_por_shortcode(shortcode)
    if post is None:
        raise HTTPException(status_code=404, detail="Publicação não encontrada")
    return post
