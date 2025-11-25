import sqlite3
import hashlib
from typing import List, Dict

import logging
from src.utils.logger_config import setup_logging

class DBManager:
    def __init__(self, db_path: str = "data/rss_collector.db"):
        self.db_path = db_path

        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        self.init_database()
        

    def init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create articles table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        hash TEXT UNIQUE NOT NULL,
                        title TEXT NOT NULL,
                        link TEXT NOT NULL,
                        source TEXT NOT NULL,
                        category TEXT NOT NULL,
                        content_hash TEXT NOT NULL,
                        published TEXT,
                        summary TEXT,
                        feed_title TEXT,
                        feed_link TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Create feed_status table to track feed processing
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS feed_status (
                        feed_url TEXT PRIMARY KEY,
                        last_processed TIMESTAMP,
                        article_count INTEGER DEFAULT 0,
                        last_error TEXT
                    )
                ''')

                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_hash ON articles(hash)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_created ON articles(created_at)')

                conn.commit()
                self.logger.info("Database initialized successfully")

        except sqlite3.Error as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise

    def calculate_article_hash(self, article: Dict) -> str:
        """Calculate unique hash for article based on title and link"""
        content = f"{article['title']}_{article['link']}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def calculate_content_hash(self, article: Dict) -> str:
        """Calculate content hash for duplicate detection"""
        content = f"{article['title']}_{article.get('summary', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def article_exists(self, article_hash: str) -> bool:
        """Check if article already exists in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM articles WHERE hash = ?', (article_hash,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            self.logger.error(f"Error checking article existence: {e}")
            return False

    def save_article(self, article: Dict) -> bool:
        """Save article to database if not exists"""
        article_hash = self.calculate_article_hash(article)
        content_hash = self.calculate_content_hash(article)

        if self.article_exists(article_hash):
            self.logger.info(f"Article already exists: {article['title'][:50]}...")
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO articles
                    (hash, title, link, source, category, content_hash, published, summary, feed_title, feed_link)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article_hash,
                    article['title'],
                    article['link'],
                    article['source'],
                    article['category'],
                    content_hash,
                    article.get('published', ''),
                    article.get('summary', ''),
                    article.get('feed_title', ''),
                    article.get('feed_link', '')
                ))

                conn.commit()
                self.logger.info(f"Article saved: {article['title'][:50]}...")
                return True

        except sqlite3.Error as e:
            self.logger.error(f"Error saving article: {e}")
            return False

    def save_articles_batch(self, articles: List[Dict]) -> int:
        """Save multiple articles to database, return count of new articles"""
        new_count = 0
        for article in articles:
            if self.save_article(article):
                new_count += 1

        self.logger.info(f"Saved {new_count} new articles from {len(articles)} processed")
        return new_count

    def get_recent_articles(self, limit: int = 50, category: str | None = None) -> List[Dict]:
        """Get recent articles from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                if category:
                    cursor.execute('''
                        SELECT * FROM articles
                        WHERE category = ?
                        ORDER BY created_at DESC
                        LIMIT ?
                    ''', (category, limit))
                else:
                    cursor.execute('''
                        SELECT * FROM articles
                        ORDER BY created_at DESC
                        LIMIT ?
                    ''', (limit,))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except sqlite3.Error as e:
            self.logger.error(f"Error fetching recent articles: {e}")
            return []

    def get_articles_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get articles within date range"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT * FROM articles
                    WHERE DATE(created_at) BETWEEN ? AND ?
                    ORDER BY created_at DESC
                ''', (start_date, end_date))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except sqlite3.Error as e:
            self.logger.error(f"Error fetching articles by date range: {e}")
            return []

    def get_article_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total articles
                cursor.execute('SELECT COUNT(*) FROM articles')
                total_articles = cursor.fetchone()[0]

                # Articles by category
                cursor.execute('SELECT category, COUNT(*) FROM articles GROUP BY category')
                by_category = dict(cursor.fetchall())

                # Articles by source
                cursor.execute('SELECT source, COUNT(*) FROM articles GROUP BY source')
                by_source = dict(cursor.fetchall())

                # Latest article date
                cursor.execute('SELECT MAX(created_at) FROM articles')
                latest_date = cursor.fetchone()[0]

                return {
                    'total_articles': total_articles,
                    'by_category': by_category,
                    'by_source': by_source,
                    'latest_article': latest_date
                }

        except sqlite3.Error as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}

    def cleanup_old_articles(self, days_old: int = 30) -> int:
        """Remove articles older than specified days, return count deleted"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    DELETE FROM articles
                    WHERE created_at < datetime('now', '-' || ? || ' days')
                ''', (days_old,))

                deleted_count = cursor.rowcount
                conn.commit()

                if deleted_count > 0:
                    self.logger.info(f"Cleaned up {deleted_count} articles older than {days_old} days")

                return deleted_count

        except sqlite3.Error as e:
            self.logger.error(f"Error cleaning up old articles: {e}")
            return 0

# Simple unit test
if __name__ == "__main__":
    db = DBManager()

    # Test article
    test_article = {
        'title': 'Test Article',
        'link': '<https://example.com/test>',
        'source': 'Test Source',
        'category': 'test',
        'summary': 'This is a test article summary',
        'published': '2024-01-15T10:00:00Z',
        'feed_title': 'Test Feed',
        'feed_link': '<https://example.com/feed>'
    }

    # Save test article
    db.save_article(test_article)

    # Get stats
    stats = db.get_article_stats()
    print(f"Database stats: {stats}")
