import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import feedparser
import requests
from bs4 import BeautifulSoup
import time


@dataclass
class Article:
    """Data class to represent an article with all required fields."""
    title: str
    publish_date: datetime
    link: str
    content: str
    feed_name: str


class RSSProcessor:
    """
    A class to process RSS feeds from a JSON configuration file and download article content.
    
    Attributes:
        config_path (str): Path to the JSON configuration file
        timeout (int): Request timeout in seconds
        retry_attempts (int): Number of retry attempts for failed requests
    """
    
    def __init__(self, config_path: str, timeout: int = 10, retry_attempts: int = 3):
        self.config_path = config_path
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for the RSS processor."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def read_config_file(self) -> Dict:
        """
        Read and parse the JSON configuration file.
        
        Returns:
            Dict: Parsed configuration data
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file contains invalid JSON
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config_data = json.load(file)
                self.logger.info(f"Successfully loaded config file: {self.config_path}")
                return config_data
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
            raise
    
    def fetch_feed_entries(self, feed_url: str, feed_name: str) -> List[Dict]:
        """
        Fetch all entries from a single RSS feed.
        
        Args:
            feed_url (str): URL of the RSS feed
            feed_name (str): Name identifier for the feed
            
        Returns:
            List[Dict]: List of feed entries
        """
        self.logger.info(f"Fetching feed: {feed_name} from {feed_url}")
        
        for attempt in range(self.retry_attempts):
            try:
                feed_data = feedparser.parse(feed_url)
                
                if feed_data.bozo:  # bozo flag indicates parsing issues
                    raise ValueError(f"Feed parsing error: {feed_data.bozo_exception}")
                
                self.logger.info(f"Successfully fetched {len(feed_data.entries)} entries from {feed_name}")
                return feed_data.entries
                
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {feed_name}: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"All attempts failed for {feed_name}")
                    return []
        
        return []
    
    def download_article_content(self, article_url: str) -> str:
        """
        Download and extract main content from an article URL.
        
        Args:
            article_url (str): URL of the article to download
            
        Returns:
            str: Extracted article content
        """
        self.logger.info(f"Downloading article content from: {article_url}")
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.get(article_url, timeout=self.timeout)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Try to find main content - common selectors for article content
                content_selectors = [
                    'article',
                    '.article-content',
                    '.post-content',
                    '.entry-content',
                    'main',
                    '.content',
                    '#content'
                ]
                
                content_element = None
                for selector in content_selectors:
                    content_element = soup.select_one(selector)
                    if content_element:
                        break
                
                # If no specific content element found, use body
                if not content_element:
                    content_element = soup.find('body') or soup
                
                # Get text and clean it up
                content = content_element.get_text(separator='\n', strip=True)
                content = '\n'.join(line.strip() for line in content.splitlines() if line.strip())
                
                self.logger.info(f"Successfully downloaded content from {article_url}")
                return content
                
            except requests.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {article_url}: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)
                else:
                    self.logger.error(f"All attempts failed for {article_url}")
                    return f"Failed to download content: {e}"
            except Exception as e:
                self.logger.error(f"Unexpected error processing {article_url}: {e}")
                return f"Error processing content: {e}"
        
        return "Failed to download content after all retry attempts"
    
    def process_feed_entry(self, entry: Dict, feed_name: str) -> Optional[Article]:
        """
        Process a single feed entry and create an Article object.
        
        Args:
            entry (Dict): Feed entry data
            feed_name (str): Name of the feed source
            
        Returns:
            Optional[Article]: Processed article or None if processing fails
        """
        try:
            title = entry.get('title', 'No Title')
            link = entry.get('link', '')
            
            # Handle publish date
            publish_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                publish_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                publish_date = datetime(*entry.updated_parsed[:6])
            else:
                publish_date = datetime.now()
            
            # Get content - prefer content, then summary, then description
            content = ''
            if hasattr(entry, 'content') and entry.content:
                content = entry.content[0].value
            elif hasattr(entry, 'summary'):
                content = entry.summary
            elif hasattr(entry, 'description'):
                content = entry.description
            
            # If no content in feed, download from article URL
            if not content.strip() and link:
                content = self.download_article_content(link)
            
            return Article(
                title=title,
                publish_date=publish_date,
                link=link,
                content=content,
                feed_name=feed_name
            )
            
        except Exception as e:
            self.logger.error(f"Error processing entry {entry.get('title', 'Unknown')}: {e}")
            return None
    
    def process_all_feeds(self) -> List[Article]:
        """
        Main method to process all feeds from the configuration file.
        
        Returns:
            List[Article]: List of all processed articles
        """
        try:
            config = self.read_config_file()
            feeds = config.get('feeds', {})
            articles = []
            
            self.logger.info(f"Starting to process {len(feeds)} feeds")
            
            for feed_name, feed_url in feeds.items():
                entries = self.fetch_feed_entries(feed_url, feed_name)
                
                for entry in entries:
                    article = self.process_feed_entry(entry, feed_name)
                    if article:
                        articles.append(article)
            
            self.logger.info(f"Successfully processed {len(articles)} articles")
            return articles
            
        except Exception as e:
            self.logger.error(f"Error processing all feeds: {e}")
            return []
    
    def save_articles_to_json(self, articles: List[Article], output_path: str) -> None:
        """
        Save processed articles to a JSON file.
        
        Args:
            articles (List[Article]): List of articles to save
            output_path (str): Path for output JSON file
        """
        try:
            serializable_articles = []
            for article in articles:
                serializable_articles.append({
                    'title': article.title,
                    'publish_date': article.publish_date.isoformat(),
                    'link': article.link,
                    'content': article.content,
                    'feed_name': article.feed_name
                })
            
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(serializable_articles, file, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Successfully saved {len(articles)} articles to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving articles to {output_path}: {e}")
            raise


# Example usage and test function
def main():
    """Example usage of the RSSProcessor class."""
    processor = RSSProcessor('feeds_config.json')
    
    try:
        articles = processor.process_all_feeds()
        
        # Print summary
        print(f"Processed {len(articles)} articles:")
        for article in articles[:3]:  # Show first 3 as sample
            print(f"- {article.feed_name}: {article.title}")
        
        # Save to file
        processor.save_articles_to_json(articles, 'processed_articles.json')
        
    except Exception as e:
        print(f"Error in main execution: {e}")


if __name__ == "__main__":
    main()