"""Contexto compartilhado para propagação do run_id."""
from __future__ import annotations

import contextvars
from contextlib import contextmanager
from typing import Iterator

_run_id = contextvars.ContextVar("run_id", default="unknown")


def get_run_id() -> str:
    return _run_id.get()


def set_run_id(value: str) -> contextvars.Token[str]:
    return _run_id.set(value)


def reset_run_id(token: contextvars.Token[str]) -> None:
    _run_id.reset(token)


@contextmanager
def bind_run_id(value: str) -> Iterator[None]:
    token = set_run_id(value)
    try:
        yield
    finally:
        reset_run_id(token)
