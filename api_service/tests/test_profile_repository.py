"""Testes do repositório de perfis."""
from __future__ import annotations

from unittest.mock import MagicMock

from api_service.repositories.profiles import ProfileRepository


def test_buscar_por_username_utiliza_consulta_do_sqlalchemy():
    sessao = MagicMock()
    modelo = MagicMock()
    query = sessao.query.return_value
    filtro = query.filter.return_value
    filtro.one_or_none.return_value = {"username": "sentinela"}

    repositorio = ProfileRepository(sessao=sessao, modelo_perfil=modelo)
    resultado = repositorio.buscar_por_username("sentinela")

    sessao.query.assert_called_once_with(modelo)
    query.filter.assert_called_once()
    filtro.one_or_none.assert_called_once()
    assert resultado == {"username": "sentinela"}


def test_buscar_por_username_sem_sessao():
    repositorio = ProfileRepository(sessao=None, modelo_perfil=None)
    assert repositorio.buscar_por_username("qualquer") is None
