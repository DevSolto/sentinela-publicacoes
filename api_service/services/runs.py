"""Serviços que tratam informações de execuções de monitoramento."""
from __future__ import annotations

from time import perf_counter
from typing import Any, Dict, Iterable, List

from api_service.metrics import RUNS_LIST_FAILURES, RUNS_LIST_LATENCY, RUNS_LIST_REQUESTS
from api_service.repositories.runs import RunRepository
from api_service.schemas.runs import ExecucaoMonitoramento


class RunService:
    """Responsável por aplicar regras de negócio às execuções."""

    def __init__(self, repository: RunRepository) -> None:
        self._repository = repository

    def listar_execucoes(self, limite: int = 50) -> List[ExecucaoMonitoramento]:
        """Lista execuções respeitando o limite informado."""
        RUNS_LIST_REQUESTS.inc()
        inicio = perf_counter()
        try:
            registros: Iterable = self._repository.listar_execucoes(limite=limite)
            resultado = [
                ExecucaoMonitoramento(**self._converter_para_dict(registro))
                for registro in registros
            ]
        except Exception:
            RUNS_LIST_FAILURES.inc()
            raise
        finally:
            RUNS_LIST_LATENCY.observe(perf_counter() - inicio)
        return resultado

    def _converter_para_dict(self, registro: Any) -> Dict[str, Any]:
        if isinstance(registro, dict):
            dados: Dict[str, Any] = {}
            for campo, aliases in {
                "identificador": ["identificador", "id"],
                "iniciado_em": ["iniciado_em", "started_at"],
                "finalizado_em": ["finalizado_em", "finished_at"],
                "status": ["status"],
                "total_publicacoes": ["total_publicacoes", "items_collected"],
                "mensagem_erro": ["mensagem_erro", "error_message"],
            }.items():
                for alias in aliases:
                    if alias in registro:
                        dados[campo] = registro[alias]
                        break
            return dados

        dados: Dict[str, Any] = {}
        aliases = {
            "identificador": ["identificador", "id"],
            "iniciado_em": ["iniciado_em", "started_at"],
            "finalizado_em": ["finalizado_em", "finished_at"],
            "status": ["status"],
            "total_publicacoes": ["total_publicacoes", "items_collected"],
            "mensagem_erro": ["mensagem_erro", "error_message"],
        }
        for campo in ExecucaoMonitoramento.model_fields:
            candidatos = aliases.get(campo, [campo])
            for alias in candidatos:
                if hasattr(registro, alias):
                    dados[campo] = getattr(registro, alias)
                    break
        return dados
