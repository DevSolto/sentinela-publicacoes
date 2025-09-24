"""Rotas referentes às execuções de monitoramento."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query

from api_service.repositories.runs import RunRepository
from api_service.schemas.runs import ExecucaoMonitoramento
from api_service.services.runs import RunService

router = APIRouter(prefix="/runs", tags=["Execuções"])


def obter_servico_execucoes() -> RunService:
    """Instancia o serviço de execuções com repositório padrão."""

    return RunService(RunRepository(sessao=None, modelo_execucao=None))


@router.get(
    "/",
    response_model=List[ExecucaoMonitoramento],
    summary="Listar execuções de monitoramento",
)
def listar_execucoes(
    limite: int = Query(
        50, ge=1, le=200, description="Quantidade máxima de execuções retornadas"
    ),
    servico: RunService = Depends(obter_servico_execucoes),
) -> List[ExecucaoMonitoramento]:
    """Retorna a lista de execuções mais recentes."""

    return servico.listar_execucoes(limite=limite)
