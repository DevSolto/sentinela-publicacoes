"""Utility responsible for publishing tasks that trigger the PostsSpider."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import redis


@dataclass(slots=True)
class PostsTask:
    """Encapsulates the payload that will be consumed by PostsSpider."""

    url: str
    profile_id: str
    post_id: str
    meta: Dict[str, Any]

    def serialise(self) -> str:
        payload = {
            "url": self.url,
            "profile_id": self.profile_id,
            "post_id": self.post_id,
            "meta": self.meta,
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
        }
        return json.dumps(payload)


class PostsQueueProducer:
    """Simple Redis backed producer for PostsSpider tasks."""

    def __init__(self, redis_url: str, queue_name: str = "scrapy:posts") -> None:
        self.redis = redis.Redis.from_url(redis_url)
        self.queue_name = queue_name

    def enqueue(
        self,
        url: str,
        profile_id: str,
        post_id: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        meta = meta or {}
        task = PostsTask(url=url, profile_id=profile_id, post_id=post_id, meta=meta)
        self.redis.lpush(self.queue_name, task.serialise())

    def size(self) -> int:
        return int(self.redis.llen(self.queue_name))


__all__ = ["PostsQueueProducer", "PostsTask"]

