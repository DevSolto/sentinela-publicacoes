"""Custom downloader middlewares used across the Scrapy service."""
from __future__ import annotations

import json
from collections import defaultdict
from http.cookies import SimpleCookie
from itertools import cycle
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from scrapy import Request
from scrapy.crawler import Crawler
from scrapy.downloadermiddlewares.retry import RetryMiddleware


class ProxyRotationMiddleware:
    """Rotate proxies for each outgoing request."""

    def __init__(self, proxies: Iterable[str] | None = None) -> None:
        proxies = list(proxies or [])
        self._proxies = proxies
        self._cycle = cycle(proxies) if proxies else None

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "ProxyRotationMiddleware":
        return cls(crawler.settings.getlist("PROXY_LIST"))

    def process_request(self, request: Request, spider: Any) -> None:
        if not self._cycle or request.meta.get("proxy"):
            return
        proxy = next(self._cycle)
        request.meta["proxy"] = proxy
        spider.logger.debug("Proxy assigned: %s", proxy)


class ExponentialBackoffRetryMiddleware(RetryMiddleware):
    """Retry middleware that increases the delay exponentially."""

    def __init__(self, settings: Any) -> None:
        super().__init__(settings)
        self.base_delay = settings.getfloat("RETRY_BACKOFF_BASE", 1.0)
        self.max_delay = settings.getfloat("RETRY_BACKOFF_MAX", 60.0)

    def _retry(self, request: Request, reason: Any, spider: Any) -> Optional[Request]:
        new_request = super()._retry(request, reason, spider)
        if not new_request:
            return None

        retries = new_request.meta.get("retry_times", 0)
        delay = min(self.base_delay * (2 ** max(retries - 1, 0)), self.max_delay)
        new_request.meta["download_delay"] = delay
        new_request.meta.setdefault("retry_schedule", []).append(delay)
        spider.logger.debug(
            "Retrying %s (%s) with delay %.2fs", new_request.url, retries, delay
        )
        return new_request


class _CookieStorage:
    """Persist cookies per profile on disk so they survive spider restarts."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def load(self, profile_id: str) -> List[Dict[str, Any]]:
        if profile_id in self._cache:
            return self._cache[profile_id]
        path = self.directory / f"{profile_id}.json"
        if path.exists():
            cookies = json.loads(path.read_text())
        else:
            cookies = []
        self._cache[profile_id] = cookies
        return cookies

    def merge(self, profile_id: str, cookies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        existing = {cookie["name"]: cookie for cookie in self.load(profile_id)}
        for cookie in cookies:
            existing[cookie["name"]] = cookie
        merged = list(existing.values())
        self._cache[profile_id] = merged
        path = self.directory / f"{profile_id}.json"
        path.write_text(json.dumps(merged))
        return merged

    def storage_state_path(self, profile_id: str) -> str:
        path = self.directory / f"{profile_id}.state.json"
        if not path.exists():
            path.write_text(json.dumps({"cookies": self.load(profile_id)}))
        return path.as_posix()


class ProfileCookieMiddleware:
    """Persist cookies per profile and reuse them across requests."""

    def __init__(self, storage: _CookieStorage) -> None:
        self.storage = storage

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "ProfileCookieMiddleware":
        storage_dir = crawler.settings.get("COOKIE_STORAGE_DIR", ".scrapy_cookies")
        return cls(_CookieStorage(storage_dir))

    def process_request(self, request: Request, spider: Any) -> None:
        profile_id = request.meta.get("profile_id")
        if not profile_id:
            return
        cookies = self.storage.load(profile_id)
        if cookies:
            request.cookies = {cookie["name"]: cookie.get("value", "") for cookie in cookies}
        request.meta.setdefault("playwright_context", f"profile-{profile_id}")
        request.meta.setdefault("playwright_context_kwargs", {})
        request.meta["playwright_context_kwargs"][
            "storage_state"
        ] = self.storage.storage_state_path(profile_id)

    def process_response(self, request: Request, response: Any, spider: Any) -> Any:
        profile_id = request.meta.get("profile_id")
        if not profile_id:
            return response
        cookie_headers = response.headers.getlist(b"Set-Cookie")
        if not cookie_headers:
            return response
        parsed: List[Dict[str, Any]] = []
        for header in cookie_headers:
            cookie = SimpleCookie()
            cookie.load(header.decode("utf-8"))
            for morsel in cookie.values():
                parsed.append(
                    {
                        "name": morsel.key,
                        "value": morsel.value,
                        "domain": morsel["domain"] or response.url,
                        "path": morsel["path"] or "/",
                    }
                )
        if parsed:
            merged = self.storage.merge(profile_id, parsed)
            state_path = self.storage.storage_state_path(profile_id)
            Path(state_path).write_text(json.dumps({"cookies": merged}))
        return response


__all__ = [
    "ProxyRotationMiddleware",
    "ExponentialBackoffRetryMiddleware",
    "ProfileCookieMiddleware",
]
