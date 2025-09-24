"""Camada de acesso a dados para comentários armazenados em MongoDB."""
from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - usado apenas para tipagem
    from pymongo.collection import Collection
else:
    Collection = Any


class CommentRepository:
    """Executa consultas específicas sobre comentários de publicações."""

    def __init__(self, colecao: Optional[Collection] = None) -> None:
        self._colecao = colecao

    def listar_por_shortcode(self, shortcode: str) -> List[dict]:
        """Recupera comentários associados ao shortcode informado."""

        if self._colecao is None:
            return []
        cursor = self._colecao.find({"shortcode": shortcode}).sort("created_at", 1)
        return list(cursor)
