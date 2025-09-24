"""Serviços que tratam informações de execuções de monitoramento."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List

from api_service.repositories.runs import RunRepository
from api_service.schemas.runs import ExecucaoMonitoramento


class RunService:
    """Responsável por aplicar regras de negócio às execuções."""

    def __init__(self, repository: RunRepository) -> None:
        self._repository = repository

    def listar_execucoes(self, limite: int = 50) -> List[ExecucaoMonitoramento]:
        """Lista execuções respeitando o limite informado."""

        registros: Iterable = self._repository.listar_execucoes(limite=limite)
        return [
            ExecucaoMonitoramento(**self._converter_para_dict(registro))
            for registro in registros
        ]

    def _converter_para_dict(self, registro: Any) -> Dict[str, Any]:
        if isinstance(registro, dict):
            return registro

        dados: Dict[str, Any] = {}
        for campo in ExecucaoMonitoramento.model_fields:
            if hasattr(registro, campo):
                dados[campo] = getattr(registro, campo)
        return dados
