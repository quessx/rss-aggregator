"""Tests for rss_processor module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.feed_parser_utils import FeedParserDict
from src.models import FeedMetadata, ProcessedRSSEntry
from src.rss_processor import RSSProcessor


class TestRSSProcessor:
    """Test RSSProcessor class."""

    def test_init(self) -> None:
        """Test processor initialization."""
        processor = RSSProcessor(
            keywords=["AI", "tech"],
            enable_summarization=True,
            delay_between_feeds=2.0,
        )
        assert processor.keywords == ["AI", "tech"]
        assert processor.enable_summarization is True
        assert processor.delay_between_feeds == 2.0

    def test_matches_keywords_true(self) -> None:
        """Test keyword matching returns True."""
        processor = RSSProcessor(keywords=["AI"])
        entry = MagicMock()
        entry.title = "AI breakthrough in machine learning"
        # Mock get_entry_text_content
        with patch(
            "src.rss_processor.get_entry_text_content", return_value="ai breakthrough"
        ):
            assert processor._matches_keywords(entry) is True

    def test_matches_keywords_false(self) -> None:
        """Test keyword matching returns False."""
        processor = RSSProcessor(keywords=["quantum"])
        entry = MagicMock()
        entry.title = "AI breakthrough"
        with patch(
            "src.rss_processor.get_entry_text_content", return_value="ai breakthrough"
        ):
            assert processor._matches_keywords(entry) is False

    def test_matches_keywords_no_keywords(self) -> None:
        """Test keyword matching with no keywords returns True."""
        processor = RSSProcessor(keywords=[])
        entry = MagicMock()
        assert processor._matches_keywords(entry) is True

    @patch("src.rss_processor.get_entry_title", return_value="Test Article")
    @patch("src.rss_processor.get_entry_link", return_value="https://example.com")
    @patch("src.rss_processor.get_entry_author", return_value="John Doe")
    @patch("src.rss_processor.get_entry_published_date", return_value="2024-01-01")
    @patch("src.rss_processor.get_entry_tags", return_value=["tech"])
    @patch("src.rss_processor.get_entry_summary", return_value="Test summary")
    def test_process_entry_success(
        self,
        mock_summary: MagicMock,
        mock_tags: MagicMock,
        mock_date: MagicMock,
        mock_author: MagicMock,
        mock_link: MagicMock,
        mock_title: MagicMock,
    ) -> None:
        """Test processing entry successfully."""
        processor = RSSProcessor(enable_summarization=True)
        entry = MagicMock()
        feed_metadata = FeedMetadata(title="Test Feed", url="https://example.com/feed")

        with patch.object(processor, "_matches_keywords", return_value=True):
            result = processor._process_entry(entry, feed_metadata)

        assert result is not None
        assert isinstance(result, ProcessedRSSEntry)
        assert result.title == "Test Article"
        assert result.link == "https://example.com"
        assert result.summary == "Test summary"

    @patch("src.rss_processor.get_entry_title", return_value="")
    @patch("src.rss_processor.get_entry_link", return_value="https://example.com")
    def test_process_entry_missing_title(
        self, mock_link: MagicMock, mock_title: MagicMock
    ) -> None:
        """Test processing entry with missing title returns None."""
        processor = RSSProcessor()
        entry = MagicMock()
        feed_metadata = FeedMetadata(title="Feed", url="https://example.com/feed")

        with patch.object(processor, "_matches_keywords", return_value=True):
            result = processor._process_entry(entry, feed_metadata)

        assert result is None

    @patch("src.rss_processor.get_entry_title", return_value="Test")
    @patch("src.rss_processor.get_entry_link", return_value="")
    def test_process_entry_missing_link(
        self, mock_link: MagicMock, mock_title: MagicMock
    ) -> None:
        """Test processing entry with missing link returns None."""
        processor = RSSProcessor()
        entry = MagicMock()
        feed_metadata = FeedMetadata(title="Feed", url="https://example.com/feed")

        with patch.object(processor, "_matches_keywords", return_value=True):
            result = processor._process_entry(entry, feed_metadata)

        assert result is None

    def test_process_entry_no_keyword_match(self) -> None:
        """Test processing entry that doesn't match keywords returns None."""
        processor = RSSProcessor(keywords=["quantum"])
        entry = MagicMock()
        feed_metadata = FeedMetadata(title="Feed", url="https://example.com/feed")

        with patch.object(processor, "_matches_keywords", return_value=False):
            result = processor._process_entry(entry, feed_metadata)

        assert result is None

    @pytest.mark.asyncio
    @patch("src.rss_processor.feedparser.parse")
    @patch("src.rss_processor.get_feed_title", return_value="Test Feed")
    @patch("src.rss_processor.get_entry_title", return_value="Test Article")
    @patch("src.rss_processor.get_entry_link", return_value="https://example.com")
    @patch("src.rss_processor.get_entry_author", return_value="")
    @patch("src.rss_processor.get_entry_published_date", return_value="2024-01-01")
    @patch("src.rss_processor.get_entry_tags", return_value=[])
    @patch("src.rss_processor.get_entry_summary", return_value="Summary")
    async def test_process_feed_success(
        self,
        mock_summary: MagicMock,
        mock_tags: MagicMock,
        mock_date: MagicMock,
        mock_author: MagicMock,
        mock_link: MagicMock,
        mock_title: MagicMock,
        mock_feed_title: MagicMock,
        mock_parse: MagicMock,
    ) -> None:
        """Test processing feed successfully."""
        # Mock feedparser result
        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.feed = MagicMock()
        mock_entry = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed

        processor = RSSProcessor(enable_summarization=True)

        with patch.object(processor, "_process_entry") as mock_process:
            mock_process.return_value = ProcessedRSSEntry(
                title="Test",
                link="https://example.com",
                published="2024-01-01",
                summary="Summary",
                feed_title="Feed",
                feed_url="https://example.com/feed",
                author=None,
                tags=[],
            )

            result = await processor.process_feed("https://example.com/feed", max_entries=10)

            assert len(result) == 1
            assert isinstance(result[0], ProcessedRSSEntry)

    @pytest.mark.asyncio
    @patch("src.rss_processor.feedparser.parse")
    async def test_process_feed_error(self, mock_parse: MagicMock) -> None:
        """Test processing feed with error returns empty list."""
        mock_parse.side_effect = Exception("Network error")

        processor = RSSProcessor()
        result = await processor.process_feed("https://example.com/feed")

        assert result == []

    @pytest.mark.asyncio
    async def test_process_feeds_with_delay(self) -> None:
        """Test processing multiple feeds with delay."""
        processor = RSSProcessor(delay_between_feeds=1.0)

        async def mock_process_feed_side_effect(*args: object, **kwargs: object) -> list[ProcessedRSSEntry]:
            return []

        with patch.object(processor, "process_feed", side_effect=mock_process_feed_side_effect) as mock_process_feed:
            # Mock asyncio.sleep by patching it where it's used
            with patch("src.rss_processor.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                await processor.process_feeds(
                    ["https://feed1.com", "https://feed2.com"], max_entries_per_feed=10
                )

                # Should sleep once (between feeds)
                assert mock_sleep.call_count == 1
                assert mock_process_feed.call_count == 2

