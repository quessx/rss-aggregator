"""Utilities for working with feedparser objects.

This module provides type-safe wrappers and utilities for extracting
data from feedparser FeedParserDict objects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from feedparser import FeedParserDict
else:
    # Runtime fallback - FeedParserDict is essentially a dict-like object
    FeedParserDict = dict[str, object]  # type: ignore[misc,assignment]


def get_feed_title(feed: FeedParserDict, fallback: str) -> str:
    """Extract title from feedparser feed object.

    Args:
        feed: Feedparser feed object
        fallback: Fallback title if feed title is not available

    Returns:
        Feed title or fallback
    """
    if hasattr(feed, "title") and feed.title:
        return str(feed.title).strip()
    return fallback


def get_entry_title(entry: FeedParserDict) -> str:
    """Extract title from feedparser entry object.

    Args:
        entry: Feedparser entry object

    Returns:
        Entry title or empty string
    """
    if hasattr(entry, "title") and entry.title:
        return str(entry.title).strip()
    return ""


def get_entry_link(entry: FeedParserDict) -> str:
    """Extract link from feedparser entry object.

    Args:
        entry: Feedparser entry object

    Returns:
        Entry link or empty string
    """
    if hasattr(entry, "link") and entry.link:
        return str(entry.link).strip()
    return ""


def get_entry_author(entry: FeedParserDict) -> str:
    """Extract author from feedparser entry object.

    Args:
        entry: Feedparser entry object

    Returns:
        Entry author or empty string
    """
    if hasattr(entry, "author") and entry.author:
        return str(entry.author).strip()
    return ""


def get_entry_summary(entry: FeedParserDict) -> str:
    """Extract summary/description from feedparser entry object.

    Tries multiple fields: summary, description, content.

    Args:
        entry: Feedparser entry object

    Returns:
        Entry summary or empty string
    """
    summary_fields = ["summary", "description", "content"]
    for field in summary_fields:
        if hasattr(entry, field):
            value = getattr(entry, field)
            if isinstance(value, list) and len(value) > 0:
                # Handle content as list of dictionaries
                if isinstance(value[0], dict) and "value" in value[0]:
                    summary = str(value[0]["value"]).strip()
                    if summary:
                        return summary
                summary = str(value[0]).strip()
                if summary:
                    return summary
            elif isinstance(value, str):
                summary = value.strip()
                if summary:
                    return summary
    return ""


def get_entry_tags(entry: FeedParserDict) -> list[str]:
    """Extract tags/categories from feedparser entry object.

    Args:
        entry: Feedparser entry object

    Returns:
        List of tag strings (non-empty)
    """
    tags: list[str] = []

    # Try tags field
    if hasattr(entry, "tags") and isinstance(entry.tags, list):
        for tag in entry.tags:
            if hasattr(tag, "term"):
                tag_value = str(tag.term).strip()
                if tag_value:
                    tags.append(tag_value)
            elif isinstance(tag, str):
                tag_value = tag.strip()
                if tag_value:
                    tags.append(tag_value)

    # Try category field
    if hasattr(entry, "category"):
        if isinstance(entry.category, list):
            for cat in entry.category:
                if isinstance(cat, str):
                    cat_value = cat.strip()
                    if cat_value:
                        tags.append(cat_value)
        elif isinstance(entry.category, str):
            cat_value = entry.category.strip()
            if cat_value:
                tags.append(cat_value)

    return tags


def get_entry_published_date(entry: FeedParserDict) -> str:
    """Extract published date from feedparser entry object.

    Args:
        entry: Feedparser entry object

    Returns:
        ISO 8601 formatted date string or empty string
    """
    from datetime import datetime

    # Try parsed date first
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            # published_parsed is a time.struct_time tuple
            dt = datetime(*entry.published_parsed[:6])
            return dt.isoformat()
        except (ValueError, TypeError, IndexError):
            pass

    # Fallback to published string
    if hasattr(entry, "published") and entry.published:
        return str(entry.published).strip()

    return ""


def get_entry_text_content(entry: FeedParserDict) -> str:
    """Get all text content from entry for keyword matching.

    Combines title, summary, and tags into a single searchable string.

    Args:
        entry: Feedparser entry object

    Returns:
        Combined lowercase text for searching
    """
    texts: list[str] = []

    title = get_entry_title(entry)
    if title:
        texts.append(title.lower())

    summary = get_entry_summary(entry)
    if summary:
        texts.append(summary.lower())

    tags = get_entry_tags(entry)
    if tags:
        texts.extend([tag.lower() for tag in tags])

    return " ".join(texts)

