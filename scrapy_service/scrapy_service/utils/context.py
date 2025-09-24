"""Contexto compartilhado para execução do coletor."""
from __future__ import annotations

import contextvars
import os
from contextlib import contextmanager
from typing import Iterator

_run_id = contextvars.ContextVar("run_id", default=os.getenv("RUN_ID", "unknown"))


def get_run_id() -> str:
    """Retorna o identificador da execução em andamento."""

    return _run_id.get()


def set_run_id(value: str) -> contextvars.Token[str]:
    """Define o identificador da execução atual."""

    return _run_id.set(value)


@contextmanager
def bind_run_id(value: str) -> Iterator[None]:
    token = set_run_id(value)
    try:
        yield
    finally:
        _run_id.reset(token)
