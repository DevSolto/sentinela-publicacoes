"""Spider responsible for collecting posts metadata from profile timelines."""
from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List

import scrapy
from scrapy import Request
from scrapy.selector import Selector
from scrapy_playwright.page import PageMethod


class ProfilesSpider(scrapy.Spider):
    name = "profiles"
    custom_settings = {
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60000,
    }

    def __init__(
        self,
        profiles: str | None = None,
        scroll_limit: int = 10,
        scroll_delay: float = 0.75,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        if profiles:
            self.profiles = json.loads(profiles)
        else:
            self.profiles = []
        self.scroll_limit = int(scroll_limit)
        self.scroll_delay = float(scroll_delay)

    def start_requests(self) -> Iterable[Request]:
        for profile in self.profiles:
            url = profile["url"]
            profile_id = profile.get("id") or profile.get("profile_id")
            meta = self._build_meta(profile_id, profile)
            cb_kwargs = {"profile": profile}
            yield Request(url, callback=self.parse, meta=meta, cb_kwargs=cb_kwargs)

    def _build_meta(self, profile_id: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        limit = profile.get("scroll_limit", self.scroll_limit)
        delay = profile.get("scroll_delay", self.scroll_delay)
        meta = {
            "playwright": True,
            "playwright_include_page": True,
            "profile_id": profile_id,
            "wait_for_selector": profile.get("wait_for_selector"),
            "scroll_target": profile.get("scroll_to_selector"),
            "scroll_limit": limit,
            "scroll_delay": delay,
        }
        meta["playwright_page_methods"] = [
            PageMethod("wait_for_load_state", "domcontentloaded"),
            PageMethod(
                "evaluate",
                "async (limit, delay) => {\n"
                "  for (let i = 0; i < limit; i++) {\n"
                "    window.scrollTo(0, document.body.scrollHeight);\n"
                "    await new Promise(r => setTimeout(r, delay * 1000));\n"
                "  }\n"
                "}",
                limit,
                delay,
            ),
        ]
        return meta

    async def parse(self, response: scrapy.http.Response, profile: Dict[str, Any]):
        page = response.meta.get("playwright_page")
        profile_id = response.meta.get("profile_id")
        wait_for_selector = response.meta.get("wait_for_selector")
        if wait_for_selector:
            try:
                await page.wait_for_selector(wait_for_selector, timeout=30000)
            except Exception as exc:  # pragma: no cover - best effort synchronisation
                self.logger.warning("Selector %s not found for %s: %s", wait_for_selector, profile_id, exc)
        scroll_target = response.meta.get("scroll_target")
        if scroll_target:
            try:
                await page.locator(scroll_target).scroll_into_view_if_needed()
            except Exception as exc:  # pragma: no cover
                self.logger.debug("Failed to scroll to %s: %s", scroll_target, exc)

        html = await page.content()
        await page.close()

        selector = Selector(text=html)
        for payload in self._extract_post_payloads(selector, profile):
            meta = {
                "playwright": True,
                "playwright_include_page": False,
                "profile_id": profile_id,
                "payload": payload["body"],
            }
            headers = payload.get("headers") or {"Content-Type": "application/json"}
            yield Request(
                url=payload["endpoint"],
                method="POST",
                body=json.dumps(payload["body"]),
                headers=headers,
                callback=self.parse_posts,
                meta=meta,
                dont_filter=True,
            )

    def _extract_post_payloads(
        self, selector: Selector, profile: Dict[str, Any]
    ) -> Iterable[Dict[str, Any]]:
        posts: List[Dict[str, Any]] = []
        for node in selector.css("[data-post-endpoint]"):
            endpoint = node.attrib.get("data-post-endpoint")
            if not endpoint:
                continue
            payload = json.loads(node.attrib.get("data-post-payload", "{}"))
            headers = json.loads(node.attrib.get("data-post-headers", "{}"))
            posts.append({"endpoint": endpoint, "body": payload, "headers": headers})
        if not posts and profile.get("api_endpoint"):
            posts.append(
                {
                    "endpoint": profile["api_endpoint"],
                    "body": profile.get("api_payload", {}),
                    "headers": profile.get("api_headers", {}),
                }
            )
        return posts

    def parse_posts(self, response: scrapy.http.Response):
        try:
            data = json.loads(response.text or "{}")
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload received from %s", response.url)
            return

        posts = data.get("posts") or data.get("results") or []
        profile_id = response.meta.get("profile_id")
        source = data.get("source") or self.settings.get("BOT_NAME")
        for post in posts:
            post.setdefault("entity", "post")
            post.setdefault("profile_id", profile_id)
            post.setdefault("source", source)
            yield post

            comments_endpoint = post.get("comments_endpoint")
            if comments_endpoint:
                comments_payload = post.get("comments_payload", {"post_id": post.get("post_id")})
                yield Request(
                    url=comments_endpoint,
                    method="POST",
                    body=json.dumps(comments_payload),
                    headers={"Content-Type": "application/json"},
                    callback=self._schedule_comments,
                    meta={
                        "playwright": True,
                        "profile_id": profile_id,
                        "post_id": post.get("post_id"),
                        "payload": comments_payload,
                    },
                    dont_filter=True,
                )

    def _schedule_comments(self, response: scrapy.http.Response):
        """Convert comment API responses into tasks for PostsSpider."""
        post_id = response.meta.get("post_id")
        profile_id = response.meta.get("profile_id")
        try:
            data = json.loads(response.text or "{}")
        except json.JSONDecodeError:
            self.logger.error("Invalid comments payload for %s", post_id)
            return
        comments = data.get("comments") or []
        for comment in comments:
            comment.update(
                {
                    "entity": "comment",
                    "post_id": post_id,
                    "profile_id": profile_id,
                    "source": self.settings.get("BOT_NAME"),
                }
            )
            yield comment
