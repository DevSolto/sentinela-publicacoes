"""Esquemas Pydantic relacionados às publicações e comentários."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ComentarioPublicacao(BaseModel):
    """Representação de um comentário associado a uma publicação."""

    identificador: str = Field(..., description="Identificador único do comentário")
    texto: str = Field(..., description="Conteúdo textual do comentário")
    usuario: str = Field(..., description="Nome do usuário que realizou o comentário")
    criado_em: datetime = Field(..., description="Data e hora da criação do comentário")


class PostResumo(BaseModel):
    """Modelo enxuto com dados essenciais da publicação."""

    shortcode: str = Field(..., description="Identificador curto da publicação")
    legenda: Optional[str] = Field(
        None, description="Texto da legenda associado à publicação"
    )
    hashtags: List[str] = Field(
        default_factory=list, description="Lista de hashtags identificadas"
    )
    capturado_em: datetime = Field(..., description="Data de captura da publicação")


class PostDetalhado(PostResumo):
    """Modelo completo de publicação contendo comentários."""

    url_midias: List[str] = Field(
        default_factory=list, description="Endereços das mídias da publicação"
    )
    comentarios: List[ComentarioPublicacao] = Field(
        default_factory=list,
        description="Comentários públicos vinculados à publicação",
    )


class FiltroConsultaPosts(BaseModel):
    """Parâmetros aceitos para filtragem de publicações."""

    capturado_inicio: Optional[datetime] = Field(
        None, description="Filtrar publicações capturadas a partir desta data"
    )
    capturado_fim: Optional[datetime] = Field(
        None, description="Filtrar publicações capturadas até esta data"
    )
    hashtags: List[str] = Field(
        default_factory=list, description="Filtrar publicações que contenham todas as hashtags informadas"
    )
    pagina: int = Field(1, ge=1, description="Número da página da paginação")
    tamanho_pagina: int = Field(20, ge=1, le=100, description="Quantidade de itens por página")
    ordenar_decrescente: bool = Field(
        True, description="Define se a ordenação por data será decrescente"
    )
