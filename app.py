#!/usr/bin/env python3

"""
RSS Collection - main
"""

from src.rss_reader import RSSReader
from src.md_writer import MarkdownWriter

def main():
    r = RSSReader() 
    w = MarkdownWriter()

    print("Fetching from RSS sources...")
    articles = r.fetch_all_feeds()

    if not articles:
        print("Unable to fetch any article. Shutting down...")
        return
    print(f"Fetched {len(articles)} article(s).")

    print("Digesting articles...")
    output_file = w.write_to_markdown(articles)
    print(f"Articles digest in {output_file}")

if __name__ == "__main__":
    main()