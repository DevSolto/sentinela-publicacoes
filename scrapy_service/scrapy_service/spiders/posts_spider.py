"""Spider that expands post details by interacting with modal dialogs."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

import scrapy
from scrapy import Request
from scrapy_playwright.page import PageMethod


def _parse_datetime(value: str | None) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class PostsSpider(scrapy.Spider):
    name = "posts"
    custom_settings = {
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60000,
    }

    def __init__(
        self,
        tasks: str | None = None,
        modal_trigger: str = "[data-action=\"open-modal\"]",
        view_all_selector: str = "text=Ver todos",
        comment_selector: str = "[data-comment-id]",
        next_selector: str = "button[data-action=\"next\"]",
        max_pages: int = 5,
        until: str | None = None,
        pagination_delay: float = 0.75,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.tasks = json.loads(tasks) if tasks else []
        self.modal_trigger = modal_trigger
        self.view_all_selector = view_all_selector
        self.comment_selector = comment_selector
        self.next_selector = next_selector
        self.max_pages = int(max_pages)
        self.pagination_delay = float(pagination_delay)
        self.until = _parse_datetime(until)

    def start_requests(self) -> Iterable[Request]:
        for task in self.tasks:
            url = task["url"]
            meta = {
                "playwright": True,
                "playwright_include_page": True,
                "profile_id": task.get("profile_id"),
                "post_id": task.get("post_id"),
            }
            meta.setdefault("playwright_page_methods", [PageMethod("wait_for_load_state", "domcontentloaded")])
            yield Request(url, callback=self.parse, meta=meta, cb_kwargs={"task": task}, dont_filter=True)

    async def parse(self, response: scrapy.http.Response, task: Dict[str, Any]):
        page = response.meta.get("playwright_page")
        profile_id = response.meta.get("profile_id")
        post_id = response.meta.get("post_id") or task.get("post_id")

        trigger_selector = task.get("modal_trigger") or self.modal_trigger
        view_all_selector = task.get("view_all_selector") or self.view_all_selector
        comment_selector = task.get("comment_selector") or self.comment_selector
        next_selector = task.get("next_selector") or self.next_selector
        await page.wait_for_selector(trigger_selector, timeout=30000)
        await page.click(trigger_selector)
        await page.wait_for_selector(view_all_selector, timeout=30000)
        await page.click(view_all_selector)

        page_index = 0
        reached_cutoff = False
        while True:
            comments = await page.query_selector_all(comment_selector)
            if not comments:
                break
            for element in comments:
                data = await element.evaluate(
                    "el => ({\n"
                    "  id: el.getAttribute('data-comment-id'),\n"
                    "  author: el.getAttribute('data-author'),\n"
                    "  created_at: el.getAttribute('data-created-at'),\n"
                    "  text: el.innerText\n"
                    "})"
                )
                created = _parse_datetime(data.get("created_at"))
                if self.until and created and created < self.until:
                    reached_cutoff = True
                    break
                yield {
                    "entity": "comment",
                    "comment_id": data.get("id"),
                    "post_id": post_id,
                    "profile_id": profile_id,
                    "source": self.settings.get("BOT_NAME"),
                    "author": data.get("author"),
                    "body": data.get("text", ""),
                    "created_at": created.isoformat() if created else None,
                }
            if reached_cutoff:
                break
            page_index += 1
            if self.max_pages and page_index >= self.max_pages:
                break
            next_button = await page.query_selector(next_selector)
            if not next_button:
                break
            await next_button.click()
            await page.wait_for_timeout(int(self.pagination_delay * 1000))

        await page.close()
