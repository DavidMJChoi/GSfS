import feedparser
import json
from datetime import datetime
from typing import List, Dict

class RSSReader:
    def __init__(self):
        self.feeds = self.load_feeds()
    
    def load_feeds(self) -> List[Dict]:
        """
        Load RSS sources from a JSON file
        """
        try:
            with open('data/feeds.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('feeds', [])
        except FileNotFoundError:
            print("Warning: data/feeds.json not found.")
            return []
    
    def fetch_feed(self, feed_url: str) -> Dict:
        """
        Fetch from a single RSS source
        """
        try:
            print(f"Fetching: {feed_url}")
            d = feedparser.parse(feed_url)
            
            if d.bozo:
                print(f"Parse error: {feed_url}")
                return None
                
            return {
                'title': d.feed.get('title', 'untitled'),
                'entries': d.entries[:5] # get only the first 5 entries
            }
        except Exception as e:
            print(f"Error while fetching {feed_url}: {e}")
            return None
    
    def fetch_all_feeds(self) -> List[Dict]:
        """
        Fetch from all RSS sources
        """
        articles = []
        
        for feed in self.feeds:
            result = self.fetch_feed(feed['url'])
            if result:
                for entry in result['entries']:
                    article = {
                        'source': feed['name'],
                        'category': feed['category'],
                        'title': entry.get('title', 'untitled'),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'summary': entry.get('summary', '')
                    }
                    articles.append(article)
        
        return articles

# Simple unit test
if __name__ == "__main__":
    r = RSSReader()
    articles = r.fetch_all_feeds()
    print(f"Fetched {len(articles)} article(s).")
    print(json.dumps(articles, indent=2, ensure_ascii=False))