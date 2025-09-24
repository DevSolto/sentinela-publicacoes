from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, MutableMapping, Optional

from pymongo import ASCENDING, DESCENDING, IndexModel


@dataclass(slots=True)
class Owner:
    """Representa informações básicas do proprietário de um post ou comentário."""

    id: str
    username: str


@dataclass(slots=True)
class Post:
    """Modelo de postagem armazenada no MongoDB."""

    id: str
    shortcode: str
    owner: Owner
    taken_at: datetime
    like_count: int
    comment_count: int
    caption: Optional[str] = None
    media_url: Optional[str] = None
    hashtags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    __collection__ = "posts"
    __indexes__ = [
        IndexModel([("shortcode", ASCENDING)], unique=True, name="idx_posts_shortcode"),
        IndexModel([("owner.username", ASCENDING)], name="idx_posts_owner_username"),
        IndexModel([("taken_at", DESCENDING)], name="idx_posts_taken_at"),
        IndexModel([("hashtags", ASCENDING)], name="idx_posts_hashtags"),
    ]

    def to_document(self) -> Dict[str, Any]:
        document: MutableMapping[str, Any] = asdict(self)
        document["updated_at"] = datetime.utcnow()
        document["hashtags"] = sorted(set(self.hashtags))
        return dict(document)


@dataclass(slots=True)
class Comment:
    """Modelo de comentário armazenado no MongoDB."""

    comment_id: str
    shortcode: str
    owner: Owner
    text: str
    taken_at: datetime
    like_count: int
    hashtags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    __collection__ = "comments"
    __indexes__ = [
        IndexModel([("shortcode", ASCENDING)], name="idx_comments_shortcode"),
        IndexModel([("owner.username", ASCENDING)], name="idx_comments_owner_username"),
        IndexModel([("taken_at", DESCENDING)], name="idx_comments_taken_at"),
        IndexModel([("hashtags", ASCENDING)], name="idx_comments_hashtags"),
        IndexModel(
            [("shortcode", ASCENDING), ("comment_id", ASCENDING)],
            unique=True,
            name="idx_comments_unique_per_post",
        ),
    ]

    def to_document(self) -> Dict[str, Any]:
        document: MutableMapping[str, Any] = asdict(self)
        document["updated_at"] = datetime.utcnow()
        document["hashtags"] = sorted(set(self.hashtags))
        return dict(document)
