"""Testes para o serviço de perfis."""
from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from api_service.schemas.profiles import PerfilDetalhado
from api_service.services.profiles import ProfileService


def test_obter_por_username_com_dicionario():
    repositorio = MagicMock()
    repositorio.buscar_por_username.return_value = {
        "username": "sentinela",
        "nome_completo": "Sentinela Dados",
        "descricao": "Monitoramento",
        "seguidores": 10,
        "seguindo": 5,
        "publicacoes": 3,
        "atualizado_em": datetime(2024, 1, 1),
    }

    servico = ProfileService(repositorio)
    perfil = servico.obter_por_username("sentinela")

    repositorio.buscar_por_username.assert_called_once_with("sentinela")
    assert isinstance(perfil, PerfilDetalhado)
    assert perfil.username == "sentinela"


def test_obter_por_username_com_objeto():
    repositorio = MagicMock()
    repositorio.buscar_por_username.return_value = SimpleNamespace(
        username="sentinela",
        nome_completo="Sentinela Dados",
        descricao="Monitoramento",
        seguidores=10,
        seguindo=5,
        publicacoes=3,
        atualizado_em=datetime(2024, 1, 1),
    )

    servico = ProfileService(repositorio)
    perfil = servico.obter_por_username("sentinela")

    assert isinstance(perfil, PerfilDetalhado)
    assert perfil.seguidores == 10


def test_obter_por_username_inexistente():
    repositorio = MagicMock()
    repositorio.buscar_por_username.return_value = None

    servico = ProfileService(repositorio)
    assert servico.obter_por_username("nada") is None
