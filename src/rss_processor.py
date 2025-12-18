"""RSS feed processing module.

This module provides functionality for fetching, parsing, and processing RSS feeds.
Designed to be extensible for future enhancements like AI summarization.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, cast

import feedparser
from apify import Actor

from .ai_summarizer import SummarizationStrategy
from .feed_parser_utils import (
    FeedParserDict,
    get_entry_author,
    get_entry_link,
    get_entry_published_date,
    get_entry_summary,
    get_entry_tags,
    get_entry_text_content,
    get_entry_title,
    get_feed_title,
)
from .models import FeedMetadata, ProcessedRSSEntry


class RSSProcessor:
    """Processes RSS feeds with filtering and summarization capabilities."""

    def __init__(
        self,
        keywords: list[str] | None = None,
        enable_summarization: bool = True,
        delay_between_feeds: float = 1.0,
        summarization_strategy: SummarizationStrategy | None = None,
    ) -> None:
        """Initialize RSS processor.

        Args:
            keywords: Optional list of keywords to filter entries (case-insensitive)
            enable_summarization: Whether to extract summaries from entries
            delay_between_feeds: Delay in seconds between processing feeds
            summarization_strategy: Strategy for summarization (AI or basic)
        """
        self.keywords: list[str] = keywords or []
        self.enable_summarization: bool = enable_summarization
        self.delay_between_feeds: float = delay_between_feeds
        self.summarization_strategy: SummarizationStrategy | None = (
            summarization_strategy
        )

    def _matches_keywords(self, entry: FeedParserDict) -> bool:
        """Check if entry matches any of the filter keywords.

        Args:
            entry: Feedparser entry object

        Returns:
            True if matches keywords or no keywords specified, False otherwise
        """
        if not self.keywords:
            return True

        # Get all text content from entry
        combined_text = get_entry_text_content(entry)

        # Check if any keyword matches
        for keyword in self.keywords:
            if keyword.lower() in combined_text:
                return True

        return False

    def _process_entry(
        self, entry: FeedParserDict, feed_metadata: FeedMetadata
    ) -> ProcessedRSSEntry | None:
        """Process a single RSS entry into structured data.

        Args:
            entry: Feedparser entry object
            feed_metadata: Metadata about the source RSS feed

        Returns:
            Processed entry object or None if entry doesn't match filters
        """
        # Filter by keywords
        if not self._matches_keywords(entry):
            return None

        # Extract basic fields
        title = get_entry_title(entry)
        link = get_entry_link(entry)

        if not title or not link:
            Actor.log.warning(
                f"Skipping entry with missing title or link from feed: {feed_metadata.url}"
            )
            return None

        # Extract optional fields
        author = get_entry_author(entry)
        published = get_entry_published_date(entry)
        tags = get_entry_tags(entry)

        # Extract summary if enabled
        summary: str | None = None
        if self.enable_summarization:
            # Get basic summary from feed
            basic_summary = get_entry_summary(entry)

            # Use AI summarization strategy if available
            if self.summarization_strategy:
                # Get full text content for AI summarization
                # Prefer content field, then summary, then description
                full_text = ""
                if hasattr(entry, "content") and entry.content:
                    if isinstance(entry.content, list) and len(entry.content) > 0:
                        if isinstance(entry.content[0], dict) and "value" in entry.content[0]:
                            full_text = str(entry.content[0]["value"])
                        else:
                            full_text = str(entry.content[0])
                    elif isinstance(entry.content, str):
                        full_text = entry.content

                # Fallback to summary/description if content not available
                if not full_text or len(full_text.strip()) < 100:
                    full_text = basic_summary if basic_summary else ""
                    # Try description as well
                    if hasattr(entry, "description") and entry.description:
                        desc_text = str(entry.description).strip()
                        if len(desc_text) > len(full_text):
                            full_text = desc_text

                # Use title + full text for better context
                if title:
                    full_text = f"{title}. {full_text}".strip()

                summary = self.summarization_strategy.summarize(
                    full_text, fallback_summary=basic_summary
                )
            else:
                summary = basic_summary if basic_summary else None

        # Build processed entry
        return ProcessedRSSEntry(
            title=title,
            link=link,
            published=published,
            summary=summary,
            feed_title=feed_metadata.title,
            feed_url=feed_metadata.url,
            author=author if author else None,
            tags=tags,
        )

    async def process_feed(
        self, feed_url: str, max_entries: int = 0
    ) -> list[ProcessedRSSEntry]:
        """Process a single RSS feed.

        Args:
            feed_url: URL of the RSS feed
            max_entries: Maximum number of entries to process (0 = unlimited)

        Returns:
            List of processed entry objects
        """
        Actor.log.info(f"Processing feed: {feed_url}")

        try:
            # Parse feed
            parsed_feed = feedparser.parse(feed_url)
            feed: FeedParserDict = cast(FeedParserDict, parsed_feed)

            # Check for parsing errors
            if hasattr(feed, "bozo") and feed.bozo:
                bozo_exception = getattr(feed, "bozo_exception", None)
                if bozo_exception:
                    Actor.log.warning(
                        f"Feed parsing warning for {feed_url}: {bozo_exception}"
                    )

            # Extract feed metadata
            feed_title = get_feed_title(feed.feed, feed_url)
            feed_metadata = FeedMetadata(title=feed_title, url=feed_url)

            # Process entries
            entries: list[ProcessedRSSEntry] = []
            entries_to_process = (
                feed.entries[:max_entries] if max_entries > 0 else feed.entries
            )

            for entry in entries_to_process:
                processed_entry = self._process_entry(entry, feed_metadata)
                if processed_entry:
                    entries.append(processed_entry)

            Actor.log.info(
                f"Processed {len(entries)} entries from {feed_title} ({feed_url})"
            )

            return entries

        except Exception as e:
            Actor.log.error(f"Error processing feed {feed_url}: {e}")
            return []

    async def process_feeds(
        self, feed_urls: list[str], max_entries_per_feed: int = 0
    ) -> list[ProcessedRSSEntry]:
        """Process multiple RSS feeds with rate limiting.

        Args:
            feed_urls: List of RSS feed URLs
            max_entries_per_feed: Maximum entries per feed (0 = unlimited)

        Returns:
            Combined list of all processed entries
        """
        all_entries: list[ProcessedRSSEntry] = []

        for i, feed_url in enumerate(feed_urls):
            if i > 0 and self.delay_between_feeds > 0:
                Actor.log.info(
                    f"Waiting {self.delay_between_feeds}s before next feed..."
                )
                await asyncio.sleep(self.delay_between_feeds)

            entries = await self.process_feed(feed_url, max_entries_per_feed)
            all_entries.extend(entries)

        return all_entries
