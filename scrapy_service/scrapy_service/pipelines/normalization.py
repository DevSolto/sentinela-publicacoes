"""Pipelines responsible for normalizing and enriching scraped data."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

ISO_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}(?:[T\s]\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)?")


def _parse_iso_datetime(value: str | None) -> Optional[datetime]:
    """Best effort parsing for ISO8601 timestamps."""
    if not value:
        return None

    candidate = value.strip()
    if not ISO_DATE_RE.match(candidate):
        return None

    # Normalise to full ISO format with timezone awareness
    try:
        dt = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
    except ValueError:
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _normalise_identifier(*parts: str) -> str:
    normalised: Iterable[str] = (
        part.strip().lower().replace("::", "_") for part in parts if part
    )
    return "::".join(normalised)


@dataclass(slots=True)
class BaseDTO:
    """Common behaviour shared by DTO representations."""

    raw: Dict[str, Any] = field(default_factory=dict)

    def serialise(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload.pop("raw", None)
        return payload


@dataclass(slots=True)
class ProfileDTO(BaseDTO):
    profile_id: str = ""
    external_id: str = ""
    display_name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_item(cls, item: Dict[str, Any]) -> "ProfileDTO":
        profile_id = _normalise_identifier(item.get("source"), item.get("profile_id"))
        external_id = item.get("profile_id", "")
        display_name = (item.get("display_name") or "").strip()
        metadata = {k: v for k, v in item.items() if k not in {"entity", "profile_id", "display_name", "source"}}
        return cls(raw=item, profile_id=profile_id, external_id=external_id, display_name=display_name, metadata=metadata)


@dataclass(slots=True)
class PostDTO(BaseDTO):
    post_id: str = ""
    profile_id: str = ""
    created_at: Optional[str] = None
    body: str = ""
    stats: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_item(cls, item: Dict[str, Any]) -> "PostDTO":
        profile_id = _normalise_identifier(item.get("source"), item.get("profile_id"))
        post_id = _normalise_identifier(profile_id, item.get("post_id") or item.get("id"))
        created_at = _parse_iso_datetime(item.get("created_at"))
        body = (item.get("body") or item.get("text") or "").strip()
        stats = item.get("stats") or {}
        normalised = created_at.isoformat() if created_at else None
        return cls(raw=item, post_id=post_id, profile_id=profile_id, created_at=normalised, body=body, stats=stats)


@dataclass(slots=True)
class CommentDTO(BaseDTO):
    comment_id: str = ""
    post_id: str = ""
    profile_id: str = ""
    created_at: Optional[str] = None
    body: str = ""

    @classmethod
    def from_item(cls, item: Dict[str, Any]) -> "CommentDTO":
        profile_id = _normalise_identifier(item.get("source"), item.get("profile_id"))
        post_id = _normalise_identifier(profile_id, item.get("post_id"))
        comment_id = _normalise_identifier(post_id, item.get("comment_id") or item.get("id"))
        created_at = _parse_iso_datetime(item.get("created_at"))
        body = (item.get("body") or item.get("text") or "").strip()
        normalised = created_at.isoformat() if created_at else None
        return cls(
            raw=item,
            comment_id=comment_id,
            post_id=post_id,
            profile_id=profile_id,
            created_at=normalised,
            body=body,
        )


class NormalizationPipeline:
    """Pipeline that converts items into DTOs and ensures deterministic identifiers."""

    def process_item(self, item: Dict[str, Any], spider: Any) -> Dict[str, Any]:
        entity = (item.get("entity") or "").lower()
        dto: BaseDTO

        if entity == "profile":
            dto = ProfileDTO.from_item(item)
        elif entity == "post":
            dto = PostDTO.from_item(item)
        elif entity in {"comment", "reply"}:
            dto = CommentDTO.from_item(item)
        else:
            spider.logger.debug("Unknown entity '%s'; skipping normalisation", entity)
            return item

        normalised = dto.serialise()
        normalised["entity"] = entity
        return normalised


__all__ = [
    "NormalizationPipeline",
    "ProfileDTO",
    "PostDTO",
    "CommentDTO",
]
