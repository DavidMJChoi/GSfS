import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.rss_reader import RSSReader

def test_rss_reader():
    reader = RSSReader()
    
    # Test on RSS source loading
    print("Loaded RSS Source:")
    for feed in reader.feeds:
        print(f" - {feed['name']}: {feed['url']}")
    
    # Test on feeds fetching
    articles = reader.fetch_all_feeds()
    print(f"\nFetched {len(articles)} article(s)")
    
    for article in articles:
        print(f"\nTitle :\t {article['title']}")
        print(f"Source:\t {article['source']}")
        print(f"Link  :\t {article['link']}")

if __name__ == "__main__":
    test_rss_reader()