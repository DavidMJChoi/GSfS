# GSfS — RSS Feed Collector & Markdown Digest Generator

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![PyPI Version](https://img.shields.io/badge/version-0.1.0-green.svg)](pyproject.toml)

GSfS collects, processes and scores items from RSS feeds and generates human-readable Markdown digests. It combines a configurable RSS fetcher, local persistence (SQLite), optional web scraping with Playwright, an LLM-based scorer, and a Markdown writer to produce daily or on-demand digests.

**Status:** Under development — core components implemented, no polished UI.

**Repository layout (key files):**
- `app.py` — orchestrates fetch → process → scrape → convert → score → write workflow.
- `src/rss_reader.py` — fetches RSS feeds listed in `data/feeds.json` and saves to DB.
- `src/content_processor.py` — filters, deduplicates and sorts articles (used by `app.py`).
- `src/scraper/PlaywrightRenderedScraper.py` — Playwright scraper used to fetch rendered HTML.
- `src/llm_scorer.py` — calls an LLM (configured via env var) to score or analyze article content.
- `src/md_writer.py` — converts JSON/DB records into a Markdown digest (`data/output/`).
- `data/` — feeds, pages (html/md/json), DB and output files.
- `h2m/` — small Go-based HTML→Markdown converter used in the pipeline.

**Why use GSfS?**
- Produce compact, categorized Markdown digests from many RSS sources.
- Persist articles locally to avoid duplicates and allow historical analysis.
- Use configurable filters to tailor the digest to your interests.
- (Experimental) Use an LLM to score/annotate articles for prioritization.

**Security / privacy note:** the project can send article content to an external LLM service. Do not enable this on sensitive content unless you trust the service and have appropriate API keys configured.

**Table of contents**
- **Introduction**
- **Key Features**
- **How to get started**
- **Where to get help**
- **Who maintains & contributing**
- **Evaluation**
- **Conclusion**

## Introduction

GSfS is a developer-focused tool that automates gathering RSS feeds, processing them, optionally scraping full article HTML, scoring with a language model, and producing Markdown digests suitable for email, notes, or static publishing.

## Key Features

- **Configurable RSS feeds** (`data/feeds.json`) with categories and names.
- **Local persistence** via SQLite database (`data/rss_collector.db`).
- **Processing pipeline** supporting duplicate removal, include/exclude keyword filters, recency limits and sorting (see `config.json`).
- **Playwright scraping** for dynamic pages (`src/scraper/PlaywrightRenderedScraper.py`).
- **LLM scoring** via `src/llm_scorer.py` — currently configured to use a Deepseek/OpenAI-compatible client driven by the `DEEPSEEK_API_KEY` environment variable.
- **Markdown output** via `src/md_writer.py` producing digests under `data/output/`.
- **Extensible** — implement new scrapers, scoring strategies or output formats.

## How users can get started

Prerequisites
- Python 3.12+
- Go (for the included `h2m` converter binary) — optional if you don't use HTML→MD conversion
- `playwright` (browser binaries required for scraping)

Installation

1. Clone the repo and install (editable install recommended):

```bash
git clone https://github.com/DavidMJChoi/GSfS.git
cd GSfS
python -m pip install -e .
```

2. Install Playwright browsers (one-time):

```bash
playwright install
```

3. Set the LLM API key (example using fish shell):

```fish
set -x DEEPSEEK_API_KEY "your_api_key_here"
```

Basic usage

1. Add/edit RSS feeds in `data/feeds.json` (each feed needs `name`, `url`, `category`).
2. Configure processing in `config.json` (see fields `processing.include_keywords`, `max_age_hours`, etc.).
3. Run the pipeline:

```bash
python app.py
```

Outputs
- Generated Markdown digests are written to `data/output/` and intermediate JSON/MD files live under `data/pages/`.

Running tests

If you want to run the existing tests:

```bash
pip install -e .[dev]
pytest -q
```

## Where users can get help

- Source code: browse `src/` for implementation details.
- Configuration examples: `config.json`, `data/feeds.json`.
- Prompts and helper notes: `docs/prompt.md`.
- Open an issue in this repository for bugs or feature requests.

## Who maintains and contributes

- **Maintainer:** `dmc` (author email in `pyproject.toml`).
- Contributions: please open issues or pull requests. For larger changes, create an issue first to discuss the design.
- Suggested files to add: `CONTRIBUTING.md` (not included) — see `docs/` for developer notes.

## Evaluation

How outputs are evaluated
- The project uses `src/llm_scorer.py` which sends article text to an LLM and expects structured JSON back. `src/md_writer.py` converts that JSON into the final digest.

Known issues and caveats
- LLM token limits: large documents may exceed a model's maximum context length (example error seen in logs). To avoid this, reduce the document passed to the scorer or use chunking.
- The scoring client is configured to read `DEEPSEEK_API_KEY` and use `deepseek-chat` model endpoints by default — change `src/llm_scorer.py` if you use a different provider.
- Playwright scraping requires installed browser binaries and may fail on sites with aggressive bot protections.

Quality of results
- The digest quality depends on feed selection, processing rules in `config.json`, and the LLM scoring prompt at `src/prompt.py`. Tuning these yields better, more relevant digests.

## Conclusion

GSfS is a developer-oriented pipeline for converting RSS signals into prioritized Markdown digests. It's a good starting point if you want an extensible, scriptable way to collect, filter and annotate feed content. If you'd like, I can:

- Add a `CONTRIBUTING.md` and a sample CI workflow.
- Improve chunking in `src/llm_scorer.py` to avoid token-limit errors.
- Provide Docker/Makefile wrappers for reproducible runs.

---

If you'd like, I can now run the tests, update `src/llm_scorer.py` to add chunking and handle token errors, or add a `CONTRIBUTING.md`. Which would you prefer next?

