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
import subprocess

from src.rss_reader import RSSReader
from src.md_writer import MDWriter
from src.content_processor import ContentProcessor
import src.scraper.PlaywrightRenderedScraper as scraper

def main():
    r = RSSReader() 
    w = MDWriter()
    p = ContentProcessor()

    config = load_config()
    processing_config = config.get('processing', {})

    # fetch articles
    print("Fetching from RSS sources...")
    _ = r.fetch_all_feeds(save_to_db=True, max_articles_per_feed=100)

    articles = r.db.get_recent_articles()
    if not articles:
        print("Unable to fetch any article. Shutting down...")
        return
    print(f"Fetched {len(articles)} articles.")

    # processing 
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
    

    # process article title -> legal file name
    def title_to_filename(title):
        import re
        
        # Replace spaces with underscores
        filename = title.replace(' ', '_')
        
        # Remove characters not allowed in Linux/macOS filenames
        # Not allowed: / (forward slash), \ (backslash), and null character
        filename = re.sub(r'[\/\\]', '', filename)
        
        # Remove any other potentially problematic characters
        # This includes control characters and reserved characters
        filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
        
        # Collapse multiple consecutive underscores
        filename = re.sub(r'_+', '_', filename)
        
        # Remove leading and trailing underscores
        filename = filename.strip('_')
        
        # If result is empty, return a default filename
        if not filename:
            return 'untitled'
        
        return filename

    print("Scraping html...")
    for article in processed_articles:
        title = title_to_filename(article['title'])
        html = scraper.fetch_content(article['link'], 20000)['content']
        if html:
            with open('data/pages/html/'+title+'.html', 'wt', encoding='utf-8') as f:
                f.write(html)

    # subprocess: invoke h2m (Go) to convert html to md
    try:
        subprocess.run(
            ["./h2m/bin/h2m"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed at invoking h2m: {e}: {e.stderr}")



    # TODO: mod: generate md digest
    # print("Generating article digest...")
    # output_file = w.write_to_markdown(processed_articles)

    # categories = {}
    # for article in processed_articles:
    #     category = article['category']
    #     categories[category] = categories.get(category, 0) + 1
    
    # print(f"After processing: {len(processed_articles)} articles")
    # for category, count in categories.items():
    #     print(f"   - {category}: {count}")

    # print(f"Article digest in {output_file}")

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