"""Input validation module.

This module provides functions for validating and normalizing
Actor input data.
"""

from __future__ import annotations

from apify import Actor

from .types import ActorInput


class InputValidationError(Exception):
    """Raised when input validation fails."""

    pass


def validate_input(input_data: ActorInput | None) -> ActorInput:
    """Validate and normalize Actor input.

    Args:
        input_data: Raw input data from Actor.get_input()

    Returns:
        Validated and normalized input data

    Raises:
        InputValidationError: If required fields are missing or invalid
    """
    if input_data is None:
        raise InputValidationError("Input data is required")

    # Validate required field
    if "rssFeeds" not in input_data:
        raise InputValidationError("rssFeeds field is required")

    rss_feeds = input_data["rssFeeds"]
    if not isinstance(rss_feeds, list) or len(rss_feeds) == 0:
        raise InputValidationError("rssFeeds must be a non-empty list")

    # Validate all URLs are strings
    for i, feed_url in enumerate(rss_feeds):
        if not isinstance(feed_url, str) or not feed_url.strip():
            raise InputValidationError(
                f"rssFeeds[{i}] must be a non-empty string URL"
            )

    # Normalize and validate optional fields
    validated_input: ActorInput = {
        "rssFeeds": rss_feeds,
        "maxEntriesPerFeed": input_data.get("maxEntriesPerFeed", 10),
        "keywords": input_data.get("keywords", []),
        "enableSummarization": input_data.get("enableSummarization", True),
        "delayBetweenFeeds": input_data.get("delayBetweenFeeds", 1.0),
        "enableAISummarization": input_data.get("enableAISummarization", False),
        "aiModelName": input_data.get("aiModelName", "facebook/bart-large-cnn"),
        "aiMaxLength": input_data.get("aiMaxLength", 1024),
        "aiMinLength": input_data.get("aiMinLength", 50),
        "aiMaxSummaryLength": input_data.get("aiMaxSummaryLength", 150),
    }

    # Add proxyConfiguration if provided (optional, no validation needed)
    proxy_config = input_data.get("proxyConfiguration")
    if proxy_config:
        validated_input["proxyConfiguration"] = proxy_config

    # Validate maxEntriesPerFeed
    max_entries = validated_input["maxEntriesPerFeed"]
    if not isinstance(max_entries, int) or max_entries < 0:
        raise InputValidationError(
            "maxEntriesPerFeed must be a non-negative integer"
        )

    # Validate keywords
    keywords = validated_input["keywords"]
    if not isinstance(keywords, list):
        raise InputValidationError("keywords must be a list")
    for i, keyword in enumerate(keywords):
        if not isinstance(keyword, str):
            raise InputValidationError(f"keywords[{i}] must be a string")

    # Validate enableSummarization
    enable_summarization = validated_input["enableSummarization"]
    if not isinstance(enable_summarization, bool):
        raise InputValidationError("enableSummarization must be a boolean")

    # Validate delayBetweenFeeds
    delay = validated_input["delayBetweenFeeds"]
    if not isinstance(delay, (int, float)) or delay < 0:
        raise InputValidationError(
            "delayBetweenFeeds must be a non-negative number"
        )

    # Validate AI summarization parameters
    enable_ai_summarization = validated_input["enableAISummarization"]
    if not isinstance(enable_ai_summarization, bool):
        raise InputValidationError("enableAISummarization must be a boolean")

    ai_model_name = validated_input["aiModelName"]
    if not isinstance(ai_model_name, str) or not ai_model_name.strip():
        raise InputValidationError("aiModelName must be a non-empty string")

    ai_max_length = validated_input["aiMaxLength"]
    if not isinstance(ai_max_length, int) or ai_max_length < 1:
        raise InputValidationError("aiMaxLength must be a positive integer")

    ai_min_length = validated_input["aiMinLength"]
    if not isinstance(ai_min_length, int) or ai_min_length < 1:
        raise InputValidationError("aiMinLength must be a positive integer")

    ai_max_summary_length = validated_input["aiMaxSummaryLength"]
    if not isinstance(ai_max_summary_length, int) or ai_max_summary_length < 1:
        raise InputValidationError(
            "aiMaxSummaryLength must be a positive integer"
        )

    if ai_min_length >= ai_max_summary_length:
        raise InputValidationError(
            "aiMinLength must be less than aiMaxSummaryLength"
        )

    return validated_input


def log_input_summary(input_data: ActorInput) -> None:
    """Log a summary of the input configuration.

    Args:
        input_data: Validated input data
    """
    rss_feeds = input_data["rssFeeds"]
    max_entries = input_data["maxEntriesPerFeed"]
    keywords = input_data["keywords"]
    enable_ai_summarization = input_data.get("enableAISummarization", False)
    ai_model_name = input_data.get("aiModelName", "facebook/bart-large-cnn")

    Actor.log.info(
        f"Starting RSS aggregation: {len(rss_feeds)} feed(s), "
        f"max {max_entries} entries per feed"
    )

    if len(rss_feeds) > 5:
        Actor.log.warning(
            f"More than 5 feeds provided ({len(rss_feeds)}). "
            "Consider limiting to 1-5 feeds for optimal performance."
        )

    if keywords:
        Actor.log.info(f"Filtering by keywords: {', '.join(keywords)}")

    if enable_ai_summarization:
        Actor.log.info(f"AI summarization enabled with model: {ai_model_name}")
    else:
        Actor.log.info("Using basic summarization (extract from feed)")

