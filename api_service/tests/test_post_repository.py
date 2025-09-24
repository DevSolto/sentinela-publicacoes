"""Testes unitários para o repositório de publicações."""
from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

from api_service.repositories.posts import PostRepository


def test_listar_posts_constroi_consulta_completa():
    colecao = MagicMock()
    cursor = MagicMock()
    cursor.sort.return_value = cursor
    cursor.skip.return_value = cursor
    cursor.limit.return_value = [
        {"shortcode": "abc", "taken_at": datetime(2024, 1, 1)}
    ]
    colecao.find.return_value = cursor

    repositorio = PostRepository(colecao)
    resultado = repositorio.listar_posts(
        capturado_inicio=datetime(2023, 12, 31),
        capturado_fim=datetime(2024, 1, 2),
        hashtags=["seguranca", "dados"],
        ordenar_decrescente=True,
        tamanho_pagina=5,
        pagina=3,
    )

    assert resultado == [
        {"shortcode": "abc", "taken_at": datetime(2024, 1, 1)}
    ]
    colecao.find.assert_called_once_with(
        {
            "taken_at": {"$gte": datetime(2023, 12, 31), "$lte": datetime(2024, 1, 2)},
            "hashtags": {"$all": ["seguranca", "dados"]},
        }
    )
    cursor.sort.assert_called_once_with("taken_at", -1)
    cursor.skip.assert_called_once_with(10)
    cursor.limit.assert_called_once_with(5)


def test_buscar_por_shortcode_quando_colecao_inexistente():
    repositorio = PostRepository()
    assert repositorio.buscar_por_shortcode("xyz") is None
