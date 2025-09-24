"""Testes do repositório de execuções."""
from __future__ import annotations

from unittest.mock import MagicMock

from api_service.repositories.runs import RunRepository


def test_listar_execucoes_ordena_por_data_desc():
    sessao = MagicMock()
    modelo = MagicMock()
    query = sessao.query.return_value
    ordenado = query.order_by.return_value
    limitado = ordenado.limit.return_value
    limitado.all.return_value = [
        {"identificador": 1},
        {"identificador": 2},
    ]

    repositorio = RunRepository(sessao=sessao, modelo_execucao=modelo)
    resultado = repositorio.listar_execucoes(limite=10)

    sessao.query.assert_called_once_with(modelo)
    query.order_by.assert_called_once()
    ordenado.limit.assert_called_once_with(10)
    limitado.all.assert_called_once()
    assert resultado == limitado.all.return_value


def test_listar_execucoes_sem_sessao():
    repositorio = RunRepository(sessao=None, modelo_execucao=None)
    assert repositorio.listar_execucoes() == []
