"""Esquemas Pydantic para execuções de monitoramento."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ExecucaoMonitoramento(BaseModel):
    """Informações sobre execuções de coleta de dados."""

    identificador: int = Field(..., description="Identificador único da execução")
    iniciado_em: datetime = Field(..., description="Data de início da execução")
    finalizado_em: Optional[datetime] = Field(
        None, description="Data de finalização da execução"
    )
    status: str = Field(..., description="Situação atual da execução")
    total_publicacoes: int = Field(
        0, ge=0, description="Quantidade de publicações processadas na execução"
    )
    mensagem_erro: Optional[str] = Field(
        None,
        description="Mensagem de erro capturada na execução, quando aplicável",
    )
