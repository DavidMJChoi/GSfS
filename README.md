# GSfS: An Integrated System for Personalized RSS Digests
[![Ask DeepWiki](https://devin.ai/assets/askdeepwiki.png)](https://deepwiki.com/DavidMJChoi/GSfS)

This file was originally generated using [GitRead](https://www.gitread.dev/).

## 🚧 UNDER DEVELOPMENT 🚧
This project is under development. Some functionalities have been implemented, but the whole system is not ready to be used. There is no any usable user interface neither.

## Introduction

GSfS (Gold-Seeker-from-S***) is a (not so) comprehensive RSS feed aggregation and processing tool designed to fetch articles from multiple sources, process them according to user-defined rules, and generate a clean, readable Markdown digest.

This is a toy project for one of my course in University of Macau.

## Workflow

The core workflow of the application is as follows:
1.  **RSS Reader**: Fetches articles from a list of RSS sources defined in `data/feeds.json`.
2.  **Database Storage**: Saves all fetched articles into a local SQLite database to prevent data loss and enable historical lookups.
3.  **Content Processor**: Retrieves recent articles from the database and applies a series of processing steps:
    *   Duplicate removal
    *   Keyword-based filtering (inclusion and exclusion)
    *   Recency filtering (e.g., only articles from the last 24 hours)
    *   Sorting (by time, title, or source)
4.  **Web Scraper**: For each processed article, a Playwright-based scraper fetches the full, rendered HTML content from the original link.
5.  **Markdown Writer**: Generates a formatted Markdown digest (`.md` file) from the final list of articles, categorized and sorted for easy reading.

## Features

*   **Configurable RSS Feeds**: Easily add, remove, or categorize RSS feeds by editing the `data/feeds.json` file.
*   **Persistent Storage**: Uses SQLite (`data/rss_collector.db`) to store all fetched articles, providing a persistent record and preventing re-processing of old entries.
*   **Advanced Content Processing**: Filter articles by keywords, age, and remove duplicates to create a highly relevant digest. All processing rules are configurable in `config.json`.
*   **Powerful Web Scraping**: Utilizes Playwright to fetch full-page HTML, capable of rendering JavaScript-heavy websites to capture dynamic content.
*   **Automated Markdown Digests**: Creates well-structured Markdown files containing a summary of the processed articles, grouped by category.
*   **Logging**: All operations are logged to `logs/rss-collector.log` for debugging and monitoring.

## Getting Started

### Prerequisites

*   Python 3.12+
*   Go
*   An OpenAI API Key (or access to full-power LLM)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/DavidMJChoi/GSfS.git
    cd GSfS
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -e .
    ```

3.  **Install Playwright browser binaries:**
    This is a one-time setup to download the necessary headless browser files.
    ```bash
    playwright install
    ```

4. **Configure the API Key in your system's environment variables**
   

### Usage

1.  **Configure Feeds**:
    Add the RSS feeds you want to follow to `data/feeds.json`. Define a `name`, `url`, and `category` for each feed.
    ```json
    {
        "feeds": [
            {
                "name": "Hacker News",
                "url": "https://news.ycombinator.com/rss",
                "category": "tech"
            }
        ]
    }
    ```

2.  **Configure Processing Rules**:
    Modify `config.json` to set your preferences for filtering and sorting articles.
    ```json
    {
        "processing": {
            "remove_duplicates": true,
            "max_age_hours": 48,
            "sort_by": "time",
            "include_keywords": ["python", "ai", "machine learning"],
            "exclude_keywords": ["sports", "politics"]
        }
    }
    ```

3.  **Run the application:**
    ```bash
    python app.py
    ```

4.  **Check the output:**
    ...
