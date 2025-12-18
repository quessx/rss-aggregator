# 🌐 RSS Aggregator: AI-Powered RSS Aggregator & Summarizer

Enterprise-grade RSS aggregator with AI-powered summarization. Collects, filters, and processes feeds from any source. Ideal for content analysis, news monitoring, and AI training. Features keyword filtering, metadata extraction, and structured output in JSON/CSV. Built with Hugging Face for advanced summaries.

**High-quality RSS Feed Aggregator & Processor for Content Teams, Researchers, and AI Engineers**

Automatically aggregates RSS feeds, filters by keywords, extracts summaries, and optionally generates AI-powered summaries — clean, structured, ready for analysis or AI.

**Built for:**

- Content aggregators & news monitoring teams
- Researchers tracking academic papers and publications
- AI/ML engineers building content datasets
- Marketing teams monitoring industry trends
- Data analysts processing feed data

✅ **Smart keyword filtering**  
✅ **AI-powered summarization** (Hugging Face transformers)  
✅ **Multiple feed support** (1-5 feeds recommended)  
✅ **Rich metadata extraction** (date, author, tags, description)  
✅ **Rate limiting & respectful crawling**  
✅ **AI-ready structured output**

👉 **Runs on Apify • No code required**

## 🚀 Why This Aggregator

✔ **Purpose-Built for RSS Processing**  
Intelligently aggregates and processes RSS feeds from any source — news sites, academic journals, blogs, corporate feeds.

✔ **AI Summarization Ready**  
Optional integration with Hugging Face transformers (BART, Pegasus) for advanced AI-powered summarization of feed entries.

✔ **Clean & Structured Output**  
Extracts only meaningful content — title, link, summary, author, tags, publication date — ready for analysis.

✔ **Smart Keyword Filtering**  
Filter entries by custom keywords (case-insensitive) across title, summary, and tags for relevance.

✔ **AI & ML Ready**  
Structured JSON/CSV output perfect for RAG systems, LLM fine-tuning, or training datasets.

✔ **Fast & Efficient**  
Powered by feedparser — excellent for RSS/Atom feeds. Lightweight and fast processing.

✔ **Safe & Controlled Processing**  
Configurable rate limiting, entry limits per feed, and graceful error handling.

✔ **Proxy Support**  
Optional Apify Proxy integration to avoid IP blocking and access feeds from different geographies.

## 💼 Use Cases

- **News monitoring** — Track industry news and trends from multiple sources
- **Academic research** — Aggregate papers from arXiv, PubMed, and other academic feeds
- **Content curation** — Collect and filter relevant content for newsletters or blogs
- **AI training data** — Generate clean datasets for LLM fine-tuning or RAG systems
- **Competitive intelligence** — Monitor competitor blogs and news feeds
- **Market research** — Track product announcements and industry updates

## 📊 Supported Sources

- **News feeds** — TechCrunch, Reuters, BBC, Guardian, etc.
- **Academic feeds** — arXiv, PubMed, academic journals
- **Blog feeds** — Medium, WordPress, custom blog RSS
- **Corporate feeds** — Company blogs, press releases, announcements
- **Any RSS/Atom feed** — Standard-compliant feeds

## ⚙️ How It Works

1. Provide RSS feed URLs (1-5 feeds recommended)
2. Set custom keywords and processing options
3. Optionally enable AI summarization
4. Run the Actor
5. Download clean, structured RSS datasets

## 🧩 Input Configuration

### Example JSON Input

```json
{
  "rssFeeds": [
    "https://arxiv.org/rss/cs.AI",
    "https://techcrunch.com/feed/"
  ],
  "maxEntriesPerFeed": 10,
  "keywords": [
    "AI",
    "machine learning",
    "artificial intelligence"
  ],
  "enableSummarization": true,
  "enableAISummarization": true,
  "aiModelName": "facebook/bart-large-cnn",
  "aiMaxLength": 1024,
  "aiMinLength": 50,
  "aiMaxSummaryLength": 150,
  "delayBetweenFeeds": 1.0,
  "proxyConfiguration": {
    "useApifyProxy": true
  }
}
```

### Key Options

- **rssFeeds** — List of RSS feed URLs to aggregate (required, 1-5 recommended)
- **maxEntriesPerFeed** — Maximum entries per feed (0 = unlimited, default: 10)
- **keywords** — Custom keywords for filtering entries (case-insensitive, empty = all entries)
- **enableSummarization** — Extract summary/description from feeds (default: true)
- **enableAISummarization** — Use Hugging Face AI for advanced summarization (default: false)
- **aiModelName** — Hugging Face model identifier (default: "facebook/bart-large-cnn")
- **aiMaxLength** — Maximum input length for AI model (default: 1024 tokens)
- **aiMinLength** — Minimum summary length (default: 50 tokens)
- **aiMaxSummaryLength** — Maximum summary length (default: 150 tokens)
- **delayBetweenFeeds** — Delay in seconds between feeds for rate limiting (default: 1.0)
- **proxyConfiguration** — Proxy settings for accessing RSS feeds (optional)
- **useApifyProxy** — Use Apify Proxy to avoid IP blocking and access feeds from different geographies (default: false)
- See [Apify Proxy documentation](https://docs.apify.com/platform/proxy) for advanced configuration

## 📂 Output Dataset

All entries are stored in the default Apify dataset with the following structure:

### Example Output Record

```json
{
  "title": "Adobe hit with proposed class-action, accused of misusing authors' work in AI training",
  "link": "https://techcrunch.com/2025/12/17/adobe-hit-with-proposed-class-action-accused-of-misusing-authors-work-in-ai-training/",
  "published": "2025-12-18T00:44:55",
  "summary": "The lawsuit is just the latest in a string of copyright-related legal complaints aimed at the AI industry.",
  "feedTitle": "TechCrunch",
  "feedUrl": "https://techcrunch.com/feed/",
  "author": "Lucas Ropek",
  "tags": [
    "AI",
    "Adobe",
    "Anthropic",
    "artificial intelligence"
  ]
}
```

### With AI Summarization

When `enableAISummarization: true`, the `summary` field contains AI-generated summaries:

```json
{
  "title": "Breakthrough in Quantum Computing",
  "link": "https://example.com/quantum-breakthrough",
  "published": "2025-12-15T10:30:00",
  "summary": "Researchers achieve significant milestone in quantum error correction, bringing practical quantum computing closer to reality. The new method reduces error rates by 50%...",
  "feedTitle": "Science News",
  "feedUrl": "https://example.com/feed.xml",
  "author": "Dr. Jane Smith",
  "tags": ["quantum computing", "research", "technology"]
}
```

## 🤖 AI Summarization Models

Supported Hugging Face models for summarization:

- **facebook/bart-large-cnn** (default) — Best for news articles and general content
- **google/pegasus-xsum** — Optimized for news summaries
- **Any summarization model** — Compatible with Hugging Face transformers

The Actor automatically falls back to basic extraction if AI summarization fails or is unavailable.

## 🏁 Getting Started

### Quick Start on Apify

1. Click **"Try for free"** on Apify
2. Paste RSS feed URLs (e.g., `https://techcrunch.com/feed/`)
3. Customize keywords and options
4. Optionally enable AI summarization
5. Run and download your dataset

## 📈 Performance

- **Processing Speed** — ~1-2 seconds per feed (depending on entries)
- **Rate Limiting** — Configurable delay between feeds (default: 1s)
- **Memory Efficient** — Processes feeds sequentially
- **Scalability** — Handles 1-5 feeds optimally (can process more)

## 🔧 Advanced Configuration

### Custom AI Models

You can use any Hugging Face summarization model:

```json
{
  "enableAISummarization": true,
  "aiModelName": "google/pegasus-xsum",
  "aiMaxLength": 2048,
  "aiMinLength": 100,
  "aiMaxSummaryLength": 200
}
```

## 📧 Support

- **Email**: **kidaxxb@gmail.com**
- **Response** within 24 hours
- **Issues**: Use Apify Issues tab

**Tags:** RSS, feed aggregator, content processing, AI summarization, Hugging Face, news aggregation, feed parser, content analysis, RAG, LLM training, data extraction

---

**Built with ❤️ on Apify**
