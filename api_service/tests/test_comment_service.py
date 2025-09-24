"""Testes para o serviço de comentários."""
from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

from api_service.schemas.posts import ComentarioPublicacao
from api_service.services.comments import CommentService


def test_listar_por_shortcode_converte_registros():
    repositorio = MagicMock()
    repositorio.listar_por_shortcode.return_value = [
        {
            "id": 1,
            "text": "Comentário",
            "user": "sentinela",
            "created_at": datetime(2024, 1, 1),
        }
    ]

    servico = CommentService(repositorio)
    comentarios = servico.listar_por_shortcode("abc")

    repositorio.listar_por_shortcode.assert_called_once_with("abc")
    assert len(comentarios) == 1
    comentario: ComentarioPublicacao = comentarios[0]
    assert isinstance(comentario, ComentarioPublicacao)
    assert comentario.usuario == "sentinela"
