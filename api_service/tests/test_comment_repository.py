"""Testes do repositório de comentários."""
from __future__ import annotations

from unittest.mock import MagicMock

from api_service.repositories.comments import CommentRepository


def test_listar_por_shortcode_ordena_por_data_crescente():
    colecao = MagicMock()
    cursor = MagicMock()
    cursor.sort.return_value = [
        {"id": 1, "text": "Olá", "created_at": 1},
        {"id": 2, "text": "Mundo", "created_at": 2},
    ]
    colecao.find.return_value = cursor

    repositorio = CommentRepository(colecao)
    resultado = repositorio.listar_por_shortcode("abc")

    colecao.find.assert_called_once_with({"shortcode": "abc"})
    cursor.sort.assert_called_once_with("created_at", 1)
    assert resultado == cursor.sort.return_value


def test_listar_por_shortcode_sem_colecao():
    repositorio = CommentRepository()
    assert repositorio.listar_por_shortcode("qualquer") == []
