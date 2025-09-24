"""Camada de acesso a dados para perfis utilizando Postgres."""
from __future__ import annotations

from typing import Optional, Type


class ProfileRepository:
    """Centraliza consultas relacionadas a perfis monitorados."""

    def __init__(self, sessao, modelo_perfil: Optional[Type] = None) -> None:
        self._sessao = sessao
        self._modelo = modelo_perfil

    def buscar_por_username(self, username: str):
        """Busca um perfil único pelo username informado."""

        if self._sessao is None or self._modelo is None:
            return None

        consulta = (
            self._sessao.query(self._modelo)
            .filter(self._modelo.username == username)
            .one_or_none()
        )
        return consulta
