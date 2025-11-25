#!/usr/bin/env python3

"""
RSS Collection - main
"""

"""
workflow: 
rss_reader -> fetch from RSS sources -> store into db
get articles from db -> content processor -> processed articles -> md writer -> digest.md
"""

import json

from src.rss_reader import RSSReader
from src.md_writer import MDWriter
from src.content_processor import ContentProcessor

def main():
    r = RSSReader() 
    w = MDWriter()
    # db = DBManager()

    config = load_config()
    processing_config = config.get('processing', {})
    p = ContentProcessor()

    # fetch articles
    print("Fetching from RSS sources...")
    _ = r.fetch_all_feeds(save_to_db=True)

    articles = r.db.get_recent_articles()
    if not articles:
        print("Unable to fetch any article. Shutting down...")
        return
    print(f"Fetched {len(articles)} article(s).")

    # processing 
    print("Processing articles...")
    processed_articles = p.process_articles(
        articles,
        remove_duplicates=processing_config.get('remove_duplicates', True),
        include_keywords=processing_config.get('include_keywords'),
        exclude_keywords=processing_config.get('exclude_keywords'),
        max_age_hours=processing_config.get('max_age_hours', 24),
        sort_by=processing_config.get('sort_by', 'time')
    )
    if not processed_articles:
        print("No article left based on current processing configuration.")
        return

    # generate md digest
    print("Generating article digest...")
    output_file = w.write_to_markdown(processed_articles)

    categories = {}
    for article in processed_articles:
        category = article['category']
        categories[category] = categories.get(category, 0) + 1
    
    print(f"After processing: {len(processed_articles)} article(s)")
    for category, count in categories.items():
        print(f"   - {category}: {count}")

    print(f"Article digest in {output_file}")

def load_config():
    """
    load config.json
    """
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("config.json not found.")
        return {}
    except json.JSONDecodeError:
        print("config.json decode error.")
        return {}

if __name__ == "__main__":
    main()