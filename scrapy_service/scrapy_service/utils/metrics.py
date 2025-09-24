"""Coletores de métricas Prometheus para execuções do Scrapy."""
from __future__ import annotations

import os
import time
from contextlib import contextmanager
from typing import Iterator

from prometheus_client import Counter, Histogram, start_http_server

from scrapy_service.utils.context import get_run_id

SCRAPY_METRICS_PORT = int(os.getenv("SCRAPY_METRICS_PORT", "9101"))
SCRAPY_METRICS_ENABLED = os.getenv("SCRAPY_METRICS_ENABLED", "true").lower() in {
    "1",
    "true",
    "yes",
    "y",
}

if SCRAPY_METRICS_ENABLED:
    try:
        start_http_server(SCRAPY_METRICS_PORT)
    except OSError:
        # Servidor já iniciado em outro processo; evita crash em import múltiplo.
        pass

COLLECTED_ITEMS = Counter(
    "scrapy_collected_items_total",
    "Total de itens coletados por spider",
    labelnames=("spider", "run_id"),
)
RUN_DURATION = Histogram(
    "scrapy_run_duration_seconds",
    "Tempo total de execução do spider",
    labelnames=("spider", "run_id"),
)
RUN_FAILURES = Counter(
    "scrapy_run_failures_total",
    "Falhas registradas por spider",
    labelnames=("spider", "run_id"),
)


@contextmanager
def observe_run(spider_name: str) -> Iterator[None]:
    """Mede o tempo de execução completo de um spider."""

    run_id = get_run_id()
    start = time.perf_counter()
    try:
        yield
    except Exception:  # pragma: no cover - repropagado após métrica
        RUN_FAILURES.labels(spider=spider_name, run_id=run_id).inc()
        raise
    finally:
        elapsed = time.perf_counter() - start
        RUN_DURATION.labels(spider=spider_name, run_id=run_id).observe(elapsed)


def register_item(spider_name: str, amount: int = 1) -> None:
    """Incrementa a contagem de itens coletados."""

    if amount < 1:
        return
    COLLECTED_ITEMS.labels(spider=spider_name, run_id=get_run_id()).inc(amount)
