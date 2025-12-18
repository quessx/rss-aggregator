"""Tests for models module."""

from __future__ import annotations

import pytest

from src.models import FeedMetadata, ProcessedRSSEntry


class TestFeedMetadata:
    """Test FeedMetadata dataclass."""

    def test_create_feed_metadata(self) -> None:
        """Test creating FeedMetadata."""
        metadata = FeedMetadata(title="Test Feed", url="https://example.com/feed.xml")
        assert metadata.title == "Test Feed"
        assert metadata.url == "https://example.com/feed.xml"

    def test_feed_metadata_immutable(self) -> None:
        """Test FeedMetadata is immutable."""
        metadata = FeedMetadata(title="Test", url="https://example.com")
        # Should raise AttributeError when trying to modify
        with pytest.raises(AttributeError):
            metadata.title = "New Title"  # type: ignore[misc]


class TestProcessedRSSEntry:
    """Test ProcessedRSSEntry dataclass."""

    def test_create_entry(self) -> None:
        """Test creating ProcessedRSSEntry."""
        entry = ProcessedRSSEntry(
            title="Test Article",
            link="https://example.com/article",
            published="2024-01-01T00:00:00",
            summary="Test summary",
            feed_title="Test Feed",
            feed_url="https://example.com/feed.xml",
            author="John Doe",
            tags=["tech", "ai"],
        )
        assert entry.title == "Test Article"
        assert entry.link == "https://example.com/article"
        assert entry.summary == "Test summary"
        assert entry.tags == ["tech", "ai"]

    def test_entry_to_dict(self) -> None:
        """Test converting entry to dictionary."""
        entry = ProcessedRSSEntry(
            title="Test Article",
            link="https://example.com/article",
            published="2024-01-01T00:00:00",
            summary="Test summary",
            feed_title="Test Feed",
            feed_url="https://example.com/feed.xml",
            author=None,
            tags=[],
        )
        entry_dict = entry.to_dict()
        assert entry_dict["title"] == "Test Article"
        assert entry_dict["feedTitle"] == "Test Feed"
        assert entry_dict["feedUrl"] == "https://example.com/feed.xml"
        assert entry_dict["author"] is None
        assert entry_dict["tags"] == []

    def test_entry_with_none_summary(self) -> None:
        """Test entry with None summary."""
        entry = ProcessedRSSEntry(
            title="Test",
            link="https://example.com",
            published="2024-01-01",
            summary=None,
            feed_title="Feed",
            feed_url="https://example.com/feed.xml",
            author=None,
            tags=[],
        )
        assert entry.summary is None
        entry_dict = entry.to_dict()
        assert entry_dict["summary"] is None

