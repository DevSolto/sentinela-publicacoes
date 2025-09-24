"""Global Scrapy settings for the scrapy_service project."""
from __future__ import annotations

import json
import os
from pathlib import Path

from scrapy_service.logging_config import configure_structured_logging
from scrapy_service.utils import metrics as _metrics  # noqa: F401 - importa para iniciar servidor

configure_structured_logging()

BOT_NAME = "scrapy_service"

SPIDER_MODULES = ["scrapy_service.spiders"]
NEWSPIDER_MODULE = "scrapy_service.spiders"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
FEED_EXPORT_ENCODING = "utf-8"
ROBOTSTXT_OBEY = False
LOG_LEVEL = os.getenv("SCRAPY_LOG_LEVEL", "INFO")

# ---------------------------------------------------------------------------
# Playwright integration
# ---------------------------------------------------------------------------
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
PLAYWRIGHT_BROWSER_TYPE = os.getenv("PLAYWRIGHT_BROWSER", "chromium")
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": json.loads(os.getenv("PLAYWRIGHT_HEADLESS", "true")),
    "timeout": int(os.getenv("PLAYWRIGHT_LAUNCH_TIMEOUT", "60000")),
}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = int(
    os.getenv("PLAYWRIGHT_NAVIGATION_TIMEOUT", "45000")
)
COOKIE_STORAGE_DIR = os.getenv("COOKIE_STORAGE_DIR", ".scrapy_cookies")

# ---------------------------------------------------------------------------
# Networking and retries
# ---------------------------------------------------------------------------
CONCURRENT_REQUESTS = int(os.getenv("SCRAPY_CONCURRENT_REQUESTS", "8"))
CONCURRENT_REQUESTS_PER_DOMAIN = int(
    os.getenv("SCRAPY_CONCURRENT_PER_DOMAIN", "4")
)
DOWNLOAD_DELAY = float(os.getenv("SCRAPY_DOWNLOAD_DELAY", "0"))
RETRY_ENABLED = True
RETRY_TIMES = int(os.getenv("SCRAPY_RETRY_TIMES", "5"))
RETRY_BACKOFF_BASE = float(os.getenv("SCRAPY_RETRY_BACKOFF_BASE", "1"))
RETRY_BACKOFF_MAX = float(os.getenv("SCRAPY_RETRY_BACKOFF_MAX", "60"))

PROXY_LIST = [proxy for proxy in os.getenv("SCRAPY_PROXIES", "").split(",") if proxy]

DOWNLOADER_MIDDLEWARES = {
    "scrapy_service.middlewares.ProxyRotationMiddleware": 310,
    "scrapy_service.middlewares.ProfileCookieMiddleware": 320,
    "scrapy_service.middlewares.ExponentialBackoffRetryMiddleware": 550,
    "scrapy_playwright.middleware.PlaywrightMiddleware": 800,
}

# ---------------------------------------------------------------------------
# Pipelines
# ---------------------------------------------------------------------------
ITEM_PIPELINES = {
    "scrapy_service.pipelines.normalization.NormalizationPipeline": 100,
    "scrapy_service.pipelines.persistence.PersistencePipeline": 200,
}

# ---------------------------------------------------------------------------
# Persistence configuration
# ---------------------------------------------------------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "scrapy_service")
POSTGRES_DSN = os.getenv(
    "POSTGRES_DSN",
    "postgresql://postgres:postgres@localhost:5432/postgres",
)
CHECKPOINT_TABLE = os.getenv("CHECKPOINT_TABLE", "scrapy_checkpoints")

# Directory for exported files/tests
DATA_DIR = Path(os.getenv("SCRAPY_DATA_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
