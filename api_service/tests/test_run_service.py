"""Testes para o serviço de execuções."""
from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from api_service.schemas.runs import ExecucaoMonitoramento
from api_service.services.runs import RunService


def test_listar_execucoes_converte_registros():
    repositorio = MagicMock()
    repositorio.listar_execucoes.return_value = [
        {
            "identificador": 1,
            "iniciado_em": datetime(2024, 1, 1, 10, 0),
            "finalizado_em": datetime(2024, 1, 1, 11, 0),
            "status": "sucesso",
            "total_publicacoes": 5,
        },
        SimpleNamespace(
            identificador=2,
            iniciado_em=datetime(2024, 1, 2, 10, 0),
            finalizado_em=None,
            status="executando",
            total_publicacoes=0,
        ),
    ]

    servico = RunService(repositorio)
    execucoes = servico.listar_execucoes(limite=5)

    repositorio.listar_execucoes.assert_called_once_with(limite=5)
    assert len(execucoes) == 2
    assert isinstance(execucoes[0], ExecucaoMonitoramento)
    assert execucoes[1].status == "executando"
