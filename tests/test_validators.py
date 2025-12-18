"""Tests for validators module."""

from __future__ import annotations

import pytest

from src.validators import InputValidationError, validate_input
from src.types import ActorInput


class TestValidateInput:
    """Test input validation."""

    def test_valid_input(self) -> None:
        """Test validation with valid input."""
        input_data: ActorInput = {
            "rssFeeds": ["https://example.com/feed.xml"],
            "maxEntriesPerFeed": 10,
            "keywords": ["AI", "tech"],
            "enableSummarization": True,
            "delayBetweenFeeds": 1.0,
        }
        result = validate_input(input_data)
        assert result["rssFeeds"] == ["https://example.com/feed.xml"]
        assert result["maxEntriesPerFeed"] == 10

    def test_missing_rss_feeds(self) -> None:
        """Test validation fails when rssFeeds is missing."""
        input_data: ActorInput = {}
        with pytest.raises(InputValidationError, match="rssFeeds field is required"):
            validate_input(input_data)

    def test_empty_rss_feeds(self) -> None:
        """Test validation fails when rssFeeds is empty."""
        input_data: ActorInput = {"rssFeeds": []}
        with pytest.raises(InputValidationError, match="non-empty list"):
            validate_input(input_data)

    def test_invalid_rss_feed_url(self) -> None:
        """Test validation fails when RSS feed URL is invalid."""
        input_data: ActorInput = {"rssFeeds": [""]}
        with pytest.raises(InputValidationError):
            validate_input(input_data)

    def test_default_values(self) -> None:
        """Test default values are applied."""
        input_data: ActorInput = {"rssFeeds": ["https://example.com/feed.xml"]}
        result = validate_input(input_data)
        assert result["maxEntriesPerFeed"] == 10
        assert result["enableSummarization"] is True
        assert result["delayBetweenFeeds"] == 1.0
        assert result["keywords"] == []

    def test_invalid_max_entries(self) -> None:
        """Test validation fails with invalid maxEntriesPerFeed."""
        input_data: ActorInput = {
            "rssFeeds": ["https://example.com/feed.xml"],
            "maxEntriesPerFeed": -1,
        }
        with pytest.raises(InputValidationError, match="non-negative integer"):
            validate_input(input_data)

    def test_invalid_keywords(self) -> None:
        """Test validation fails with invalid keywords."""
        input_data: ActorInput = {
            "rssFeeds": ["https://example.com/feed.xml"],
            "keywords": ["valid", 123],  # type: ignore[list-item]
        }
        with pytest.raises(InputValidationError):
            validate_input(input_data)

    def test_ai_summarization_parameters(self) -> None:
        """Test AI summarization parameters validation."""
        input_data: ActorInput = {
            "rssFeeds": ["https://example.com/feed.xml"],
            "enableAISummarization": True,
            "aiModelName": "facebook/bart-large-cnn",
            "aiMaxLength": 1024,
            "aiMinLength": 50,
            "aiMaxSummaryLength": 150,
        }
        result = validate_input(input_data)
        assert result["enableAISummarization"] is True
        assert result["aiModelName"] == "facebook/bart-large-cnn"

    def test_invalid_ai_min_max_lengths(self) -> None:
        """Test validation fails when min >= max summary length."""
        input_data: ActorInput = {
            "rssFeeds": ["https://example.com/feed.xml"],
            "aiMinLength": 150,
            "aiMaxSummaryLength": 100,
        }
        with pytest.raises(InputValidationError, match="less than"):
            validate_input(input_data)

    def test_none_input(self) -> None:
        """Test validation fails with None input."""
        with pytest.raises(InputValidationError, match="required"):
            validate_input(None)

