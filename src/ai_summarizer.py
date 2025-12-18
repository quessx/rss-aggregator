"""AI-powered summarization module using Hugging Face transformers.

This module provides AI summarization capabilities using pre-trained
transformer models from Hugging Face. Falls back to basic extraction
if models are unavailable or summarization fails.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from apify import Actor

if TYPE_CHECKING:
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


class AISummarizer:
    """AI-powered text summarizer using Hugging Face transformers."""

    def __init__(
        self,
        model_name: str = "facebook/bart-large-cnn",
        max_length: int = 1024,
        min_length: int = 50,
        max_summary_length: int = 150,
    ) -> None:
        """Initialize AI summarizer.

        Args:
            model_name: Hugging Face model identifier for summarization
            max_length: Maximum input length for the model
            min_length: Minimum summary length
            max_summary_length: Maximum summary length
        """
        self.model_name: str = model_name
        self.max_length: int = max_length
        self.min_length: int = min_length
        self.max_summary_length: int = max_summary_length
        self._tokenizer: AutoTokenizer | None = None
        self._model: AutoModelForSeq2SeqLM | None = None
        self._initialized: bool = False

    def _initialize_model(self) -> bool:
        """Initialize the transformer model and tokenizer.

        Returns:
            True if initialization successful, False otherwise
        """
        if self._initialized:
            return self._model is not None and self._tokenizer is not None

        try:
            Actor.log.info(f"Loading AI summarization model: {self.model_name}")

            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)

            # Set model to evaluation mode
            self._model.eval()

            self._initialized = True
            Actor.log.info("AI summarization model loaded successfully")
            return True

        except ImportError:
            Actor.log.warning(
                "transformers library not available. "
                "Install it with: pip install transformers torch"
            )
            return False
        except Exception as e:
            Actor.log.error(f"Failed to load AI summarization model: {e}")
            return False

    def summarize(self, text: str) -> str | None:
        """Summarize text using AI model.

        Args:
            text: Text to summarize

        Returns:
            Summarized text or None if summarization fails
        """
        if not text or not text.strip():
            return None

        # Initialize model if needed
        if not self._initialize_model():
            return None

        if self._tokenizer is None or self._model is None:
            return None

        try:
            # Truncate text if too long
            text_length = len(text)
            if text_length > self.max_length * 4:  # Rough estimate
                text = text[: self.max_length * 4]
                Actor.log.debug(
                    f"Truncated text from {text_length} to {len(text)} characters"
                )

            # Tokenize input
            inputs = self._tokenizer(
                text,
                max_length=self.max_length,
                truncation=True,
                padding="max_length",
                return_tensors="pt",
            )

            # Generate summary
            summary_ids = self._model.generate(
                inputs["input_ids"],
                max_length=self.max_summary_length,
                min_length=self.min_length,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True,
            )

            # Decode summary
            summary = self._tokenizer.decode(summary_ids[0], skip_special_tokens=True)

            if summary and summary.strip():
                return summary.strip()

            return None

        except Exception as e:
            Actor.log.warning(f"AI summarization failed: {e}")
            return None

    def is_available(self) -> bool:
        """Check if AI summarization is available.

        Returns:
            True if model can be initialized, False otherwise
        """
        return self._initialize_model()


class SummarizationStrategy:
    """Strategy pattern for summarization with fallback support."""

    def __init__(
        self,
        enable_ai_summarization: bool = False,
        ai_model_name: str = "facebook/bart-large-cnn",
        ai_max_length: int = 1024,
        ai_min_length: int = 50,
        ai_max_summary_length: int = 150,
    ) -> None:
        """Initialize summarization strategy.

        Args:
            enable_ai_summarization: Whether to use AI summarization
            ai_model_name: Hugging Face model name for AI summarization
            ai_max_length: Maximum input length for AI model
            ai_min_length: Minimum summary length for AI
            ai_max_summary_length: Maximum summary length for AI
        """
        self.enable_ai_summarization: bool = enable_ai_summarization
        self._ai_summarizer: AISummarizer | None = None

        if enable_ai_summarization:
            self._ai_summarizer = AISummarizer(
                model_name=ai_model_name,
                max_length=ai_max_length,
                min_length=ai_min_length,
                max_summary_length=ai_max_summary_length,
            )

    def summarize(self, text: str, fallback_summary: str | None = None) -> str | None:
        """Summarize text using the configured strategy.

        Args:
            text: Text to summarize
            fallback_summary: Fallback summary if AI summarization fails

        Returns:
            Summarized text or fallback summary
        """
        if not text or not text.strip():
            return fallback_summary

        # Try AI summarization if enabled
        if self.enable_ai_summarization and self._ai_summarizer:
            ai_summary = self._ai_summarizer.summarize(text)
            if ai_summary:
                Actor.log.debug("Using AI-generated summary")
                return ai_summary
            else:
                Actor.log.debug("AI summarization failed, using fallback")

        # Use fallback summary
        return fallback_summary

    def is_ai_available(self) -> bool:
        """Check if AI summarization is available.

        Returns:
            True if AI summarization is enabled and available
        """
        if not self.enable_ai_summarization or self._ai_summarizer is None:
            return False
        return self._ai_summarizer.is_available()

