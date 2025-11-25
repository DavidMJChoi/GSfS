import feedparser
import json
from typing import List, Dict
from src.database import DBManager

import logging
from src.utils.logger_config import setup_logging

class RSSReader:
    def __init__(self, feeds_file: str = "data/feeds.json"):
        self.feeds_file = feeds_file

        setup_logging()
        self.logger = logging.getLogger(__name__)

        self.db = DBManager()
        self.feeds = self.load_feeds()
    
    def load_feeds(self) -> List[Dict]:
        """
        Load RSS sources from a JSON file
        """
        try:
            with open('data/feeds.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                feeds = data.get('feeds', [])
                self.logger.info(f"Loaded {len(feeds)} RSS feeds")
                return feeds
        except FileNotFoundError:
            self.logger.error("Error: data/feeds.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON format in feeds file")
            return []
    
    # @retry(max_retries=2, delay=1.0)
    def fetch_feed(self, feed_url: str) -> Dict:
        """
        Fetch from a single RSS source
        """
        try:
            self.logger.info(f"Fetching: {feed_url}")
            
            d = feedparser.parse(feed_url)
            
            if d.bozo:  # Check for parsing errors
                self.logger.warning(f"Parse error: {feed_url}")
                return None
                
            return {
                'title': d.feed.get('title', 'untitled'),

                # may slice to determine how many entries to fetch
                'entries': d.entries[:]
            }
        except Exception as e:
            self.logger.error(f"Error fetching {feed_url}: {e}")
            return None
    
    def fetch_all_feeds(self, max_articles_per_feed: int = 10, save_to_db: bool = True) -> List[Dict]:
        """
        Fetch from all RSS sources
        """
        all_articles = []
        successful_feeds = 0

        for feed in self.feeds:
            result = self.fetch_feed(feed['url'])
            if result:
                successful_feeds += 1
                for entry in result['entries'][:max_articles_per_feed]:
                    article = {
                        'source': feed['name'],
                        'category': feed['category'],
                        'title': entry.get('title', 'No Title'),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'summary': entry.get('summary', entry.get('description', '')),
                        'feed_title': feed['name'],
                        'feed_link': feed['url']
                    }
                    all_articles.append(article)

        self.logger.debug(f"Successfully fetched {len(all_articles)} articles from {successful_feeds}/{len(self.feeds)} feeds")

        # Save to database if requested
        if save_to_db and all_articles:
            new_count = self.db.save_articles_batch(all_articles)
            self.logger.info(f"Database: {new_count} new articles saved")

        return all_articles
    
    def get_articles_from_db(self, limit: int = 50, category: str | None = None) -> List[Dict]:
        """Get articles from database"""
        return self.db.get_recent_articles(limit, category)
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        return self.db.get_article_stats()

# Simple unit test
if __name__ == "__main__":

    reader = RSSReader()

    # Test fetching and saving to database
    articles = reader.fetch_all_feeds(save_to_db=True)
    print(f"Fetched {len(articles)} articles")

    # Test retrieving from database
    db_articles = reader.get_articles_from_db(limit=5)
    print(f"Retrieved {len(db_articles)} articles from database")

    # Show stats
    stats = reader.get_database_stats()
    print(f"Database statistics: {stats}")