"""Tests for feed_parser_utils module."""

from __future__ import annotations

from unittest.mock import MagicMock

from src.feed_parser_utils import (
    get_entry_author,
    get_entry_link,
    get_entry_published_date,
    get_entry_summary,
    get_entry_tags,
    get_entry_text_content,
    get_entry_title,
    get_feed_title,
)


class TestGetFeedTitle:
    """Test get_feed_title function."""

    def test_get_title_from_feed(self) -> None:
        """Test extracting title from feed."""
        feed = MagicMock()
        feed.title = "Test Feed"
        result = get_feed_title(feed, "Fallback")
        assert result == "Test Feed"

    def test_fallback_when_no_title(self) -> None:
        """Test fallback when feed has no title."""
        feed = MagicMock()
        del feed.title
        result = get_feed_title(feed, "Fallback Feed")
        assert result == "Fallback Feed"

    def test_strip_whitespace(self) -> None:
        """Test whitespace is stripped."""
        feed = MagicMock()
        feed.title = "  Test Feed  "
        result = get_feed_title(feed, "Fallback")
        assert result == "Test Feed"


class TestGetEntryTitle:
    """Test get_entry_title function."""

    def test_get_title(self) -> None:
        """Test extracting title."""
        entry = MagicMock()
        entry.title = "Test Article"
        assert get_entry_title(entry) == "Test Article"

    def test_empty_when_no_title(self) -> None:
        """Test returns empty string when no title."""
        entry = MagicMock()
        del entry.title
        assert get_entry_title(entry) == ""


class TestGetEntryLink:
    """Test get_entry_link function."""

    def test_get_link(self) -> None:
        """Test extracting link."""
        entry = MagicMock()
        entry.link = "https://example.com/article"
        assert get_entry_link(entry) == "https://example.com/article"

    def test_empty_when_no_link(self) -> None:
        """Test returns empty string when no link."""
        entry = MagicMock()
        del entry.link
        assert get_entry_link(entry) == ""


class TestGetEntryAuthor:
    """Test get_entry_author function."""

    def test_get_author(self) -> None:
        """Test extracting author."""
        entry = MagicMock()
        entry.author = "John Doe"
        assert get_entry_author(entry) == "John Doe"

    def test_empty_when_no_author(self) -> None:
        """Test returns empty string when no author."""
        entry = MagicMock()
        del entry.author
        assert get_entry_author(entry) == ""


class TestGetEntrySummary:
    """Test get_entry_summary function."""

    def test_get_summary_string(self) -> None:
        """Test extracting summary as string."""
        entry = MagicMock()
        entry.summary = "Test summary text"
        assert get_entry_summary(entry) == "Test summary text"

    def test_get_description_when_no_summary(self) -> None:
        """Test extracting description when summary not available."""
        entry = MagicMock()
        del entry.summary
        entry.description = "Test description"
        assert get_entry_summary(entry) == "Test description"

    def test_get_content_list(self) -> None:
        """Test extracting content from list."""
        entry = MagicMock()
        del entry.summary
        del entry.description
        entry.content = [{"value": "Content text"}]
        assert get_entry_summary(entry) == "Content text"

    def test_empty_when_no_content(self) -> None:
        """Test returns empty string when no content."""
        entry = MagicMock()
        del entry.summary
        del entry.description
        del entry.content
        assert get_entry_summary(entry) == ""


class TestGetEntryTags:
    """Test get_entry_tags function."""

    def test_get_tags_from_tags_field(self) -> None:
        """Test extracting tags from tags field."""
        tag1 = MagicMock()
        tag1.term = "tech"
        tag2 = MagicMock()
        tag2.term = "ai"
        entry = MagicMock()
        entry.tags = [tag1, tag2]
        tags = get_entry_tags(entry)
        assert "tech" in tags
        assert "ai" in tags

    def test_get_tags_from_category_string(self) -> None:
        """Test extracting tags from category string."""
        entry = MagicMock()
        del entry.tags
        entry.category = "technology"
        tags = get_entry_tags(entry)
        assert "technology" in tags

    def test_get_tags_from_category_list(self) -> None:
        """Test extracting tags from category list."""
        entry = MagicMock()
        del entry.tags
        entry.category = ["tech", "ai"]
        tags = get_entry_tags(entry)
        assert "tech" in tags
        assert "ai" in tags

    def test_empty_when_no_tags(self) -> None:
        """Test returns empty list when no tags."""
        entry = MagicMock()
        del entry.tags
        del entry.category
        assert get_entry_tags(entry) == []


class TestGetEntryPublishedDate:
    """Test get_entry_published_date function."""

    def test_get_parsed_date(self) -> None:
        """Test extracting parsed date."""
        from datetime import datetime

        entry = MagicMock()
        entry.published_parsed = (2024, 1, 1, 0, 0, 0, 0, 0, 0)
        result = get_entry_published_date(entry)
        assert "2024-01-01" in result

    def test_get_string_date_when_no_parsed(self) -> None:
        """Test extracting string date when parsed not available."""
        entry = MagicMock()
        del entry.published_parsed
        entry.published = "Mon, 01 Jan 2024 00:00:00 GMT"
        result = get_entry_published_date(entry)
        assert result == "Mon, 01 Jan 2024 00:00:00 GMT"

    def test_empty_when_no_date(self) -> None:
        """Test returns empty string when no date."""
        entry = MagicMock()
        del entry.published_parsed
        del entry.published
        assert get_entry_published_date(entry) == ""


class TestGetEntryTextContent:
    """Test get_entry_text_content function."""

    def test_combines_title_summary_tags(self) -> None:
        """Test combines title, summary, and tags."""
        entry = MagicMock()
        entry.title = "Test Article"
        entry.summary = "Test summary"
        tag = MagicMock()
        tag.term = "tech"
        entry.tags = [tag]
        result = get_entry_text_content(entry)
        assert "test article" in result.lower()
        assert "test summary" in result.lower()
        assert "tech" in result.lower()

