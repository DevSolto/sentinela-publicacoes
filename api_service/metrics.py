"""Coletores Prometheus específicos do domínio da API."""
from __future__ import annotations

from prometheus_client import Counter, Histogram

RUNS_LIST_REQUESTS = Counter(
    "api_runs_list_requests_total",
    "Quantidade de chamadas ao endpoint de listagem de execuções.",
)
RUNS_LIST_FAILURES = Counter(
    "api_runs_list_failures_total",
    "Quantidade de falhas ao listar execuções.",
)
RUNS_LIST_LATENCY = Histogram(
    "api_runs_list_latency_seconds",
    "Latência observada ao listar execuções.",
)

__all__ = [
    "RUNS_LIST_REQUESTS",
    "RUNS_LIST_FAILURES",
    "RUNS_LIST_LATENCY",
]
