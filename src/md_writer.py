import os
from datetime import datetime
from typing import List, Dict
from src.database import DBManager

class MDWriter:
    def __init__(self, output_dir: str = "./data/output"):
        self.output_dir = output_dir
        self.ensure_output_dir()
        self.db = DBManager()
    
    def ensure_output_dir(self):
        """
        Helper: ensure that the output directory exists
        """
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_filename(self) -> str:
        """
        Helper: generate output file name
        """
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H-%M")
        return f"rss_digest_{date_str}_{time_str}.md"
    
    def format_article(self, article: Dict) -> str:
        """
        Format an article (JSON) into readable markdown
        """
        # Publish date and time
        published = article.get('published', '')
        if published:
            try:
                # Parse and format date and time
                from dateutil import parser
                dt = parser.parse(published)
                published = dt.strftime("%Y-%m-%d %H:%M")
            except:
                published = published[:16] # first 16 characters
        
        # Contruct markdown (string)
        markdown = f"## {article['title']}\n\n"
        
        if published:
            markdown += f"**Published time**: {published}  \n"
        
        markdown += f"**Source**: {article['source']}  \n"
        markdown += f"**Category**: {article['category']}  \n"
        markdown += f"**Link**: [Original article]({article['link']})  \n\n"
        
        summary = article.get('summary', '')
        if summary:
            # HTML tags cleanup
            import re
            summary = re.sub('<[^<]+?>', '', summary)
            summary = summary.strip()
            if summary:
                markdown += f"**Summary**: {summary}\n\n"
        
        markdown += "---\n\n"
        return markdown
    
    def generate_markdown_content(self, articles: List[Dict]) -> str:
        """
        Generate a list of formatted article basic information and statistics
        """
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M")
        
        # Categorize
        articles_by_category = {}
        for article in articles:
            category = article['category']
            if category not in articles_by_category:
                articles_by_category[category] = []
            articles_by_category[category].append(article)
        
        # Construct markdown
        content = f"# RSS Digest\n\n"
        content += f"**Date and Time**: {date_str}  \n"
        content += f"**Article Count**: {len(articles)}  \n\n"
        
        # Category
        for category, category_articles in articles_by_category.items():
            content += f"## {category.upper()} ({len(category_articles)} article(s))\n\n"
            
            for article in category_articles:
                content += self.format_article(article)
        
        # Statistics
        content += "## Statistics\n\n"
        content += f"- In total: {len(articles)} article(s)\n"
        for category in articles_by_category:
            count = len(articles_by_category[category])
            content += f"- {category}: {count} article(s)\n"
        
        return content
    
    def write_to_markdown(self, articles: List[Dict], filename: str = None) -> str:
        """
        Write to markdown file
        """
        if not filename:
            filename = self.generate_filename()
        
        filepath = os.path.join(self.output_dir, filename)
        
        markdown_content = self.generate_markdown_content(articles)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Feeds list generated: {filepath}")
        return filepath

    def generate_digest_from_db(self, limit: int = 50, category: str | None = None) -> str:
        """Generate digest from database articles"""
        articles = writer.db.get_recent_articles(limit, category)
        return self.write_to_markdown(articles)

# Simple unit test
if __name__ == "__main__":
    # Test data
    # test_articles = [
    #     {
    #         'title': 'Python 3.12 新特性发布',
    #         'source': 'Python官方博客',
    #         'category': 'programming',
    #         'link': 'https://example.com/python-3-12',
    #         'published': '2024-01-15T10:00:00Z',
    #         'summary': 'Python 3.12 带来了许多性能改进和新特性...'
    #     },
    #     {
    #         'title': '人工智能的最新进展',
    #         'source': 'Tech News',
    #         'category': 'tech',
    #         'link': 'https://example.com/ai-advances',
    #         'published': '2024-01-15T09:00:00Z',
    #         'summary': '研究人员在自然语言处理领域取得了突破...'
    #     }
    # ]
    
    writer = MDWriter()
    # output_file = writer.write_to_markdown(test_articles)
    output_file = writer.generate_digest_from_db()
    print(f"Test file generated: {output_file}")