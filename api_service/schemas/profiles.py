"""Esquemas Pydantic relacionados aos perfis monitorados."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PerfilDetalhado(BaseModel):
    """Representação das informações públicas de um perfil."""

    username: str = Field(..., description="Nome de usuário do perfil")
    nome_completo: Optional[str] = Field(
        None, description="Nome completo apresentado pelo perfil"
    )
    descricao: Optional[str] = Field(
        None, description="Biografia ou descrição do perfil"
    )
    seguidores: int = Field(0, ge=0, description="Número de seguidores")
    seguindo: int = Field(0, ge=0, description="Quantidade de perfis acompanhados")
    publicacoes: int = Field(0, ge=0, description="Total de publicações realizadas")
    atualizado_em: Optional[datetime] = Field(
        None, description="Momento da última atualização das informações"
    )
