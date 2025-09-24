"""Persistence pipeline responsible for persisting entities in storage backends."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from psycopg import Connection, connect


@dataclass(slots=True)
class PersistenceConfig:
    mongo_uri: str
    mongo_db: str
    postgres_dsn: str
    checkpoint_table: str = "scrapy_checkpoints"


class PersistencePipeline:
    """Persist posts/comments in MongoDB and checkpoints in PostgreSQL."""

    def __init__(self, config: PersistenceConfig) -> None:
        self.config = config
        self.mongo_client: MongoClient | None = None
        self.mongo_posts: Collection | None = None
        self.mongo_comments: Collection | None = None
        self.pg_conn: Connection | None = None

    @classmethod
    def from_crawler(cls, crawler: Any) -> "PersistencePipeline":
        settings = crawler.settings
        config = PersistenceConfig(
            mongo_uri=settings.get("MONGO_URI", "mongodb://localhost:27017"),
            mongo_db=settings.get("MONGO_DATABASE", "scrapy"),
            postgres_dsn=settings.get("POSTGRES_DSN", "postgresql://postgres:postgres@localhost:5432/postgres"),
            checkpoint_table=settings.get("CHECKPOINT_TABLE", "scrapy_checkpoints"),
        )
        return cls(config)

    # ----- Lifecycle -----------------------------------------------------
    def open_spider(self, spider: Any) -> None:
        self._setup_mongo()
        self._setup_postgres()
        spider.logger.info("Persistence pipeline initialised")

    def close_spider(self, spider: Any) -> None:
        if self.mongo_client:
            self.mongo_client.close()
        if self.pg_conn:
            self.pg_conn.close()

    # ----- Setup helpers -------------------------------------------------
    def _setup_mongo(self) -> None:
        self.mongo_client = MongoClient(self.config.mongo_uri)
        database = self.mongo_client[self.config.mongo_db]
        self.mongo_posts = database["posts"]
        self.mongo_comments = database["comments"]
        self.mongo_posts.create_index("_id", unique=True)
        self.mongo_comments.create_index("_id", unique=True)

    def _setup_postgres(self) -> None:
        self.pg_conn = connect(self.config.postgres_dsn)
        with self.pg_conn.cursor() as cursor:
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.config.checkpoint_table} (
                    profile_id TEXT PRIMARY KEY,
                    marker JSONB,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            self.pg_conn.commit()

    # ----- Processing ----------------------------------------------------
    def process_item(self, item: Dict[str, Any], spider: Any) -> Dict[str, Any]:
        entity = item.get("entity")
        if entity == "post":
            self._upsert_post(item, spider)
        elif entity == "comment":
            self._upsert_comment(item, spider)

        profile_id = item.get("profile_id")
        checkpoint_marker = item.get("checkpoint")
        if profile_id and checkpoint_marker:
            self._persist_checkpoint(profile_id, checkpoint_marker)
        return item

    # ----- Mongo helpers -------------------------------------------------
    def _upsert_post(self, item: Dict[str, Any], spider: Any) -> None:
        if not self.mongo_posts:
            raise RuntimeError("MongoDB not initialised")
        payload = {key: value for key, value in item.items() if key != "entity"}
        payload.setdefault("updated_at", datetime.now(timezone.utc).isoformat())
        payload.setdefault("_id", item.get("post_id"))
        try:
            self.mongo_posts.update_one({"_id": payload["_id"]}, {"$set": payload}, upsert=True)
        except PyMongoError as exc:
            spider.logger.error("Failed to upsert post %s: %s", payload.get("_id"), exc, exc_info=True)

    def _upsert_comment(self, item: Dict[str, Any], spider: Any) -> None:
        if not self.mongo_comments:
            raise RuntimeError("MongoDB not initialised")
        payload = {key: value for key, value in item.items() if key != "entity"}
        payload.setdefault("updated_at", datetime.now(timezone.utc).isoformat())
        payload.setdefault("_id", item.get("comment_id"))
        try:
            self.mongo_comments.update_one({"_id": payload["_id"]}, {"$set": payload}, upsert=True)
        except PyMongoError as exc:
            spider.logger.error("Failed to upsert comment %s: %s", payload.get("_id"), exc, exc_info=True)

    # ----- Postgres helpers ---------------------------------------------
    def _persist_checkpoint(self, profile_id: str, marker: Any) -> None:
        if not self.pg_conn:
            raise RuntimeError("PostgreSQL not initialised")
        with self.pg_conn.cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO {self.config.checkpoint_table} (profile_id, marker)
                VALUES (%s, %s)
                ON CONFLICT (profile_id)
                DO UPDATE SET marker = EXCLUDED.marker, updated_at = NOW()
                """,
                (profile_id, json.dumps(marker)),
            )
            self.pg_conn.commit()


__all__ = ["PersistencePipeline", "PersistenceConfig"]
