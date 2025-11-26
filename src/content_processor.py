import hashlib
from typing import List, Dict
from datetime import datetime

class ContentProcessor:
    def __init__(self):
        self.processed_hashes = set()
    
    def calculate_article_hash(self, article: Dict) -> str:
        """
        Calculate article hash for removing duplicates
        md5 is used
        """
        content = f"{article['title']}_{article['link']}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """
        Remove duplicated articles
        """
        unique_articles = []
        seen_hashes = set()
        
        for article in articles:
            article_hash = self.calculate_article_hash(article)
            
            if article_hash not in seen_hashes:
                seen_hashes.add(article_hash)
                unique_articles.append(article)
            else:
                print(f"Removing duplicates: {article['title'][:50]}...")
        
        print(f"{len(unique_articles)}/{len(articles)} articles after duplicates removal.")
        return unique_articles
    
    def filter_by_keywords(self, articles: List[Dict], include_keywords: List[str] = None, 
                          exclude_keywords: List[str] = None) -> List[Dict]:
        """
        Keyword-based filtering
        """
        if not include_keywords and not exclude_keywords:
            return articles
        
        filtered_articles = []
        
        for article in articles:
            title = article['title'].lower()
            summary = article.get('summary', '').lower()
            content = f"{title} {summary}"
            
            # exclude
            if exclude_keywords:
                if any(keyword.lower() in content for keyword in exclude_keywords):
                    continue
            
            # include
            if include_keywords:
                if any(keyword.lower() in content for keyword in include_keywords):
                    filtered_articles.append(article)
            else:
                filtered_articles.append(article)
        
        print(f"{len(filtered_articles)}/{len(articles)} articles after keyword-based filtering")
        return filtered_articles
    
    def filter_by_recency(self, articles: List[Dict], hours: int = 24) -> List[Dict]:
        """
        filter by recency
        """
        if hours <= 0:
            return articles
        
        recent_articles = []
        now = datetime.now()
        
        for article in articles:
            published = article.get('published', '')
            if not published:
                # keep those without published date
                recent_articles.append(article)
                continue
            
            try:
                from dateutil import parser
                publish_time = parser.parse(published)
                time_diff = now - publish_time
                
                if time_diff.total_seconds() <= hours * 3600:
                    recent_articles.append(article)
            except:
                # keep articles when parse error
                recent_articles.append(article)
        
        print(f"Within ({hours} hours): {len(recent_articles)}/{len(articles)} articles")
        return recent_articles
    
    def sort_articles(self, articles: List[Dict], sort_by: str = "time") -> List[Dict]:
        """
        sort articles
        """
        if sort_by == "time":
            # sort by time, newest first
            return sorted(articles, 
                         key=lambda x: x.get('published', ''), 
                         reverse=True)
        elif sort_by == "title":
            # sort by title, dictionary order
            return sorted(articles, 
                         key=lambda x: x.get('title', '').lower())
        else:
            # sort by source, then the title
            return sorted(articles, 
                         key=lambda x: (x.get('source', ''), x.get('title', '')))
    
    def process_articles(self, articles: List[Dict], 
                        remove_duplicates: bool = True,
                        include_keywords: List[str] = None,
                        exclude_keywords: List[str] = None,
                        max_age_hours: int = 24,
                        sort_by: str = "time") -> List[Dict]:
        
        processed = articles.copy()
        
        print(f"Processing {len(processed)} articles...")
        
        if remove_duplicates:
            processed = self.remove_duplicates(processed)
        
        if include_keywords or exclude_keywords:
            processed = self.filter_by_keywords(processed, include_keywords, exclude_keywords)
        
        if max_age_hours > 0:
            processed = self.filter_by_recency(processed, max_age_hours)
        
        processed = self.sort_articles(processed, sort_by)
        
        print(f"Done: {len(processed)} articles")
        return processed

# Simple unit test
if __name__ == "__main__":
    processor = ContentProcessor()
    
    test_articles = [
        {'title': 'Python Tutorial', 'link': 'http://example.com/1', 'published': '2024-01-15T10:00:00Z'},
        {'title': 'Python Tutorial', 'link': 'http://example.com/1', 'published': '2024-01-15T10:00:00Z'}, 
        {'title': 'AI News', 'link': 'http://example.com/2', 'published': '2024-01-14T10:00:00Z'},
        {'title': 'Java Programming', 'link': 'http://example.com/3', 'published': '2024-01-13T10:00:00Z'},
    ]
    
    processed = processor.process_articles(
        test_articles,
        include_keywords=['python'],
        exclude_keywords=['java'],
        max_age_hours=48
    )
    
    print(f"Result: {len(processed)} articles")