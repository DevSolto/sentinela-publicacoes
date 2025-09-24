"""Camada de acesso a dados para publicações em MongoDB."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional, TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - usado apenas para tipagem
    from pymongo.collection import Collection
else:
    Collection = Any


class PostRepository:
    """Responsável por executar consultas relacionadas às publicações."""

    def __init__(self, colecao: Optional[Collection] = None) -> None:
        self._colecao = colecao

    def listar_posts(
        self,
        capturado_inicio: Optional[datetime] = None,
        capturado_fim: Optional[datetime] = None,
        hashtags: Optional[Iterable[str]] = None,
        ordenar_decrescente: bool = True,
        tamanho_pagina: int = 20,
        pagina: int = 1,
    ) -> List[dict]:
        """Retorna publicações considerando filtros e paginação."""

        if self._colecao is None:
            return []

        consulta: dict = {}
        if capturado_inicio or capturado_fim:
            intervalo: dict[str, datetime] = {}
            if capturado_inicio:
                intervalo["$gte"] = capturado_inicio
            if capturado_fim:
                intervalo["$lte"] = capturado_fim
            consulta["taken_at"] = intervalo

        if hashtags:
            consulta["hashtags"] = {"$all": list(hashtags)}

        direcao = -1 if ordenar_decrescente else 1
        salto = (max(pagina, 1) - 1) * tamanho_pagina

        cursor = (
            self._colecao.find(consulta)
            .sort("taken_at", direcao)
            .skip(salto)
            .limit(tamanho_pagina)
        )
        return list(cursor)

    def buscar_por_shortcode(self, shortcode: str) -> Optional[dict]:
        """Busca uma única publicação através do shortcode."""

        if self._colecao is None:
            return None
        return self._colecao.find_one({"shortcode": shortcode})
