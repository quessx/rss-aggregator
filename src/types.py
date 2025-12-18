"""Type definitions for RSS Aggregator Actor.

This module defines all TypedDict structures for input/output data
to ensure type safety throughout the application.
"""

from __future__ import annotations

from typing import TypedDict


class ActorInput(TypedDict, total=False):
    """Input schema for the RSS Aggregator Actor.

    All fields are optional except rssFeeds, but the input schema
    validation ensures required fields are present.
    """

    rssFeeds: list[str]
    maxEntriesPerFeed: int
    keywords: list[str]
    enableSummarization: bool
    delayBetweenFeeds: float
    enableAISummarization: bool
    aiModelName: str
    aiMaxLength: int
    aiMinLength: int
    aiMaxSummaryLength: int


class RSSEntryData(TypedDict, total=False):
    """Structured RSS entry data output.

    Represents a single processed RSS entry with all available fields.
    """

    title: str
    link: str
    published: str
    summary: str | None
    feedTitle: str
    feedUrl: str
    author: str | None
    tags: list[str]

