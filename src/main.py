"""RSS Aggregator and Processor Actor.

This Actor aggregates RSS feeds from various sources, processes them
(filtering, summarization), and outputs structured data to Apify dataset.
"""

from __future__ import annotations

from apify import Actor

from .ai_summarizer import SummarizationStrategy
from .rss_processor import RSSProcessor
from .types import ActorInput
from .validators import InputValidationError, log_input_summary, validate_input


async def main() -> None:
    """Main entry point for the RSS Aggregator Actor.

    Fetches RSS feeds, processes entries (filtering, summarization),
    and pushes results to Apify dataset.
    """
    async with Actor:
        try:
            # Get and validate input
            raw_input: ActorInput | None = await Actor.get_input()
            input_data: ActorInput = validate_input(raw_input)

            # Log input summary
            log_input_summary(input_data)

            # Extract input parameters
            rss_feeds: list[str] = input_data["rssFeeds"]
            max_entries_per_feed: int = input_data["maxEntriesPerFeed"]
            keywords: list[str] = input_data["keywords"]
            enable_summarization: bool = input_data["enableSummarization"]
            delay_between_feeds: float = input_data["delayBetweenFeeds"]
            enable_ai_summarization: bool = input_data.get(
                "enableAISummarization", False
            )
            ai_model_name: str = input_data.get(
                "aiModelName", "facebook/bart-large-cnn"
            )
            ai_max_length: int = input_data.get("aiMaxLength", 1024)
            ai_min_length: int = input_data.get("aiMinLength", 50)
            ai_max_summary_length: int = input_data.get(
                "aiMaxSummaryLength", 150
            )

            # Initialize summarization strategy if AI is enabled
            summarization_strategy: SummarizationStrategy | None = None
            if enable_ai_summarization and enable_summarization:
                summarization_strategy = SummarizationStrategy(
                    enable_ai_summarization=True,
                    ai_model_name=ai_model_name,
                    ai_max_length=ai_max_length,
                    ai_min_length=ai_min_length,
                    ai_max_summary_length=ai_max_summary_length,
                )

            # Initialize processor
            processor = RSSProcessor(
                keywords=keywords,
                enable_summarization=enable_summarization,
                delay_between_feeds=delay_between_feeds,
                summarization_strategy=summarization_strategy,
            )

            # Process all feeds
            all_entries = await processor.process_feeds(
                feed_urls=rss_feeds, max_entries_per_feed=max_entries_per_feed
            )

            # Push results to dataset
            if all_entries:
                Actor.log.info(f"Pushing {len(all_entries)} entries to dataset...")
                for entry in all_entries:
                    entry_dict = entry.to_dict()
                    await Actor.push_data(entry_dict)
                Actor.log.info(f"Successfully processed {len(all_entries)} entries")
            else:
                Actor.log.warning("No entries found matching the criteria")

            Actor.log.info("RSS aggregation completed successfully")

        except InputValidationError as e:
            Actor.log.error(f"Input validation failed: {e}")
            await Actor.exit(exit_code=1)
        except Exception as e:
            Actor.log.error(f"Unexpected error: {e}")
            await Actor.exit(exit_code=1)
