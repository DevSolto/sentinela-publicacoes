"""Camada de acesso a dados para execuções utilizando Postgres."""
from __future__ import annotations

from typing import Iterable, Optional, Type


class RunRepository:
    """Responsável por consultas sobre execuções de monitoramento."""

    def __init__(self, sessao, modelo_execucao: Optional[Type] = None) -> None:
        self._sessao = sessao
        self._modelo = modelo_execucao

    def listar_execucoes(self, limite: int = 50) -> Iterable:
        """Retorna as execuções mais recentes respeitando o limite informado."""

        if self._sessao is None or self._modelo is None:
            return []

        return (
            self._sessao.query(self._modelo)
            .order_by(self._modelo.iniciado_em.desc())
            .limit(limite)
            .all()
        )
