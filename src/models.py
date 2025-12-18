"""Data models for RSS feed processing.

This module defines data classes and structures for RSS feed entries
and feed metadata.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeedMetadata:
    """Metadata about an RSS feed source."""

    title: str
    url: str


@dataclass(frozen=True)
class ProcessedRSSEntry:
    """Processed RSS entry with all extracted fields.

    This is an immutable data class representing a fully processed
    RSS entry ready for output.
    """

    title: str
    link: str
    published: str
    summary: str | None
    feed_title: str
    feed_url: str
    author: str | None
    tags: list[str]

    def to_dict(self) -> dict[str, str | None | list[str]]:
        """Convert to dictionary format for Apify dataset.

        Returns:
            Dictionary with camelCase keys matching output schema
        """
        return {
            "title": self.title,
            "link": self.link,
            "published": self.published,
            "summary": self.summary,
            "feedTitle": self.feed_title,
            "feedUrl": self.feed_url,
            "author": self.author,
            "tags": self.tags,
        }
