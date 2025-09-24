from __future__ import annotations

from datetime import datetime
from typing import Sequence

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo.results import UpdateResult

from infrastructure.models.mongo import Comment, Post


class MongoPostRepository:
    """Repositório responsável por operações na coleção de posts."""

    def __init__(self, database: AsyncIOMotorDatabase, auto_ensure_indexes: bool = False) -> None:
        self._collection: AsyncIOMotorCollection = database[Post.__collection__]
        self._index_models = Post.__indexes__
        self._auto_ensure_indexes = auto_ensure_indexes

    async def ensure_indexes(self) -> Sequence[str]:
        """Garante que os índices definidos no modelo existam na coleção."""
        return await self._collection.create_indexes(self._index_models)

    async def upsert_post(self, post: Post) -> UpdateResult:
        """Realiza um upsert idempotente de uma postagem baseada no shortcode."""
        if self._auto_ensure_indexes:
            await self.ensure_indexes()

        document = post.to_document()
        created_at = document.pop("created_at", datetime.utcnow())

        return await self._collection.update_one(
            {"shortcode": post.shortcode},
            {
                "$set": document,
                "$setOnInsert": {"created_at": created_at},
            },
            upsert=True,
        )


class MongoCommentRepository:
    """Repositório para leitura e escrita de comentários."""

    def __init__(self, database: AsyncIOMotorDatabase, auto_ensure_indexes: bool = False) -> None:
        self._collection: AsyncIOMotorCollection = database[Comment.__collection__]
        self._index_models = Comment.__indexes__
        self._auto_ensure_indexes = auto_ensure_indexes

    async def ensure_indexes(self) -> Sequence[str]:
        """Cria os índices definidos no modelo de comentário."""
        return await self._collection.create_indexes(self._index_models)

    async def upsert_comment(self, comment: Comment) -> UpdateResult:
        """Realiza um upsert idempotente de um comentário via chave composta."""
        if self._auto_ensure_indexes:
            await self.ensure_indexes()

        document = comment.to_document()
        created_at = document.pop("created_at", datetime.utcnow())

        return await self._collection.update_one(
            {"shortcode": comment.shortcode, "comment_id": comment.comment_id},
            {
                "$set": document,
                "$setOnInsert": {"created_at": created_at},
            },
            upsert=True,
        )
