"""Testes para o serviço de publicações."""
from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

from api_service.schemas.posts import ComentarioPublicacao, PostDetalhado
from api_service.services.posts import PostService


def test_listar_posts_converte_registros_em_modelos():
    post_repo = MagicMock()
    comment_service = MagicMock()
    post_repo.listar_posts.return_value = [
        {
            "shortcode": "abc",
            "caption": "Legenda",
            "hashtags": ["dados"],
            "taken_at": datetime(2024, 1, 1),
            "media_urls": ["http://imagem"],
        }
    ]
    comment_service.listar_por_shortcode.return_value = [
        ComentarioPublicacao(
            identificador="1",
            texto="Ótimo conteúdo",
            usuario="sentinela",
            criado_em=datetime(2024, 1, 2),
        )
    ]

    servico = PostService(post_repo, comment_service)
    resultado = servico.listar_posts(
        capturado_inicio=datetime(2023, 12, 31),
        capturado_fim=datetime(2024, 1, 3),
        hashtags=["dados"],
        pagina=2,
        tamanho_pagina=10,
        ordenar_decrescente=False,
    )

    post_repo.listar_posts.assert_called_once_with(
        capturado_inicio=datetime(2023, 12, 31),
        capturado_fim=datetime(2024, 1, 3),
        hashtags=["dados"],
        pagina=2,
        tamanho_pagina=10,
        ordenar_decrescente=False,
    )
    comment_service.listar_por_shortcode.assert_called_once_with("abc")
    assert len(resultado) == 1
    post: PostDetalhado = resultado[0]
    assert isinstance(post, PostDetalhado)
    assert post.shortcode == "abc"
    assert post.legenda == "Legenda"
    assert post.comentarios[0].texto == "Ótimo conteúdo"


def test_obter_post_por_shortcode_quando_inexistente():
    post_repo = MagicMock()
    comment_service = MagicMock()
    post_repo.buscar_por_shortcode.return_value = None

    servico = PostService(post_repo, comment_service)
    assert servico.obter_post_por_shortcode("abc") is None
