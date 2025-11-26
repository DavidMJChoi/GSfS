---
marp: true

footer: "Github (https://github.com/DavidMJChoi/GSfS)"
---

# GSfS: An Integrated System for Personalized RSS Digests
## Combining RSS Collection with LLM-Based Ranking
### DC325951 Cai Mingjie

---

# Contents

* The Problem: Information Overload

* Introducing GSfS: Our Solution

* System Architecture & Workflow

* Deep Dive: Core Modules
    * RSS Collector & Scraper | Content Pre-Processor | LLM-Based Scorer & Ranker
  
* Implementation & Technical Stack

* Demonstration

* Evaluation & Challenges

* Conclusion & Future Work

---

# The Problem: Information Overload

* **Vast Information Streams**: The web generates an overwhelming volume of content daily.

* **User Pain Point**: Manually sifting through hundreds of articles is time-consuming and inefficient.

* **Core Question**: How can we surface the most relevant and interesting content for a user automatically?

---

# System Overview
* **Aggregate**: Collect articles from a configurable list of RSS feeds reliably.

* **Pre-process**: Clean, deduplicate, and filter content based on configurable rules.

* **Enrich**: Scrape full article text to enable deep content analysis.

* **Intelligently Rank**: Employ an LLM to score and rank articles based on perceived quality and relevance.

* **Deliver**: Generate a concise, personalized Markdown digest for the user.

--- 

# Workflow

[RSS Feeds] -> [RSS Reader Module] -> [SQLite Database]

[Database] -> [Content Processor] -> [Scraper Module] -> [HTML Files]

[HTML Files] -> [HTML-to-Markdown Converter (h2m)] -> [Markdown Files]

[Markdown Files] -> [LLM Scorer Module] -> [Ranked Article List]

[Ranked Article List] -> [Markdown Writer] -> [Final Digest.md]

---

# Workflow Phase I: Data Acquisition & Ingestion

*   **RSS Reader:**
    *   Fetches article metadata (title, link, date) from multiple RSS sources.
    *   Stores raw data in a SQLite database.
*   **Content Pre-Processor:**
    *   Applies initial filters (de-duplication, keyword inclusion/exclusion, recency).
    *   Prepares a candidate list of articles for deep analysis.

---

# Workflow Phase II: Content Enrichment & Conversion

*   **Scraper Module:**
    *   Uses `Playwright` to fetch the full HTML content of each article link.
    *   Handles JavaScript-rendered pages.
*   **HTML-to-Markdown Converter (h2m):**
    *   A custom Go utility to convert clean HTML into structured Markdown.
    *   Provides a clean, text-based format ideal for LLM processing.

---

# Workflow Phase III: Intelligent Ranking & Delivery

*   **LLM Scorer & Ranker:**
    *   The core of our IR system.
    *   Takes article Markdown and uses an LLM with a custom prompt to generate a relevance/quality score.
    *   Ranks articles based on these scores.
*   **Markdown Writer:**
    *   Generates the final output digest.
    *   Creates a well-formatted `digest.md` file with the top-ranked articles.

---

# Core Module I: RSS Reader & Database

*   **Function:** Orchestrates the initial data collection.
*   **Key Features:**
    *   Configurable feed list (`feeds.json`).
    *   Robust error handling and logging.
    *   SQLite database for persistent storage (`rss_collector.db`).
*   **IR Relevance:** Demonstrates the "Collection" step in the IR pipeline.

---

# Core Module II: Content Processor & Scraper

*   **Content Processor:**
    *   Applies classic IR pre-processing: filtering and deduplication.
*   **Scraper (PlaywrightRenderedScraper):**
    *   Solves the challenge of dynamic web content.
    *   Ensures we have the complete article text for accurate analysis, not just RSS snippets.

---

# Core Module III: LLM-Based Scorer

*   **The Ranking Engine:** This is where we move beyond traditional TF-IDF or BM25.
*   **Process:**
    1.  Input: Clean Markdown of an article.
    2.  A carefully engineered prompt is sent to the LLM API.
    3.  The LLM analyzes the content based on criteria like novelty, depth, and credibility.
    4.  Output: A numerical score.
*   **Result:** A semantic understanding of content quality.

---

# Prompt Design

*   **Sample Prompt Structure:**
    *   "You are a information retrieval assistant. Analyze the following article and provide a score from 1-10 based on:"
    *   **Criteria 1: Relevance to Tech/Startup scene.**
    *   **Criteria 2: Novelty and Insightfulness.**
    *   **Criteria 3: Depth of Analysis.**
    *   "Article: [Markdown text here]"
*   **Goal:** Guide the LLM to act as a personalized, intelligent ranking function.

---

# Technical Stack & Implementation


*   **Backend:** Python (RSS Reader, Processor, Scraper, LLM Client)
*   **Web Scraping:** Playwright for robust, rendered content fetching.
*   **Language Utility:** Go (for the high-performance `h2m` converter).
*   **Data Storage:** SQLite for metadata, File system for raw HTML/Markdown.
*   **AI:** DeepSeek API
*   **Configuration:** JSON files for easy customization.

---

# Project Structure & Organization


*   (This slide can show a simplified version of your tree)
*   `app.py` - Main application entry point.
*   `src/` - Core Python modules (reader, processor, scorer, etc.).
*   `src/scraper/` - Specialized scraping classes.
*   `data/` - Database, config, and processed outputs (HTML, MD, digests).
*   `h2m/` - Custom Go-based HTML-to-Markdown converter.
*   Highlights a clean, modular, and maintainable codebase.

---

# Live Demonstration


*   **Scenario:** Show the system running from start to finish.
*   **Step 1:** Run `app.py` and show logs of fetching and processing.
*   **Step 2:** Display a generated HTML file and its corresponding Markdown.
*   **Step 3:** Show the final `digest.md` output file.
*   **Focus:** Emphasize how the final list is ranked by the LLM's score, not just publish time.

---

# Evaluation & Challenges


*   **Evaluation:**
    *   Qualitative: The final digest is subjectively more interesting and relevant.
    *   Quantitative: Can measure user time saved or preference over a non-ranked list.
*   **Challenges:**
    *   **Latency:** LLM API calls are slower than traditional ranking.
    *   **Cost:** API usage can incur expenses.
    *   **LLM Bias:** Ranking is dependent on the model's inherent biases and prompt design.
    *   **Scalability:** Processing hundreds of articles requires efficient pipelines.

---

# Connection to Information Retrieval Concepts


*   **Classic IR:** Our system implements the standard pipeline: Collection -> Processing -> Indexing (in a way) -> Ranking -> Presentation.
*   **Beyond Keywords:** We replace traditional statistical ranking (TF-IDF) with a neural, semantic approach (LLMs).
*   **Re-Ranking:** This project can be seen as a sophisticated re-ranking system on top of an initial keyword/filter-based candidate set.

---

# Future Work
*   **Personalization:** Fine-tune ranking based on explicit user feedback (thumbs up/down).
*   **Multi-Modal Input:** Incorporate user's past reading history or saved articles.
*   **Caching & Optimization:** Cache LLM responses for identical articles to reduce cost/latency.
*   **Advanced Summarization:** Include LLM-generated summaries in the digest.
*   **Web Interface:** Replace the Markdown file with an interactive web UI.

---
# Thank You
*   Questions?
*   **Repository** https://github.com/DavidMJChoi/GSfS
*   Thank you to the professors and colleagues for your attention and feedback.