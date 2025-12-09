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
import os
import subprocess
from datetime import datetime

from src.rss_reader import RSSReader
from src.md_writer import MDWriter
from src.content_processor import ContentProcessor
import src.scraper.PlaywrightRenderedScraper as scraper
from src.llm_scorer import LLMScorer

def main():
    
    config = load_config()



    # fetch articles
    r = RSSReader()
    print("Fetching from RSS sources...")
    _ = r.fetch_all_feeds(save_to_db=True, max_articles_per_feed=100)

    articles = r.db.get_recent_articles()
    if not articles:
        print("Unable to fetch any article. Shutting down...")
        return
    print(f"Fetched {len(articles)} articles.")



    # processing 
    p = ContentProcessor()
    processing_config = config.get('processing', {})
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
    # scraping
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



    # LLM Scoring
    print("Scoring...")
    s = LLMScorer()
    md_dir = "data/pages/md/"
    json_dir = "data/pages/json/"

    with os.scandir(md_dir) as entries:
        for entry in entries:
            doc_path = md_dir+entry.name
            out_path = json_dir + entry.name[:-3] +".json"
        
            output = s.score(doc_path)

            with open(out_path, "w+", encoding='utf-8') as f:

                # get valid json
                # since LLM returns a md code block like ```json ... ```
                f.write(output[8:-3])

    def remove_files_in_folder(folder_path):
        """移除指定文件夹下的所有文件"""
        try:
            # 检查文件夹是否存在
            if not os.path.isdir(folder_path):
                print(f"错误：'{folder_path}' 不是一个有效的文件夹路径")
                return False
            
            # 获取文件夹下所有文件和子文件夹
            items = os.listdir(folder_path)
            
            # 统计文件数量
            files_count = 0
            for item in items:
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    files_count += 1
            
            if files_count == 0:
                print(f"文件夹 '{folder_path}' 中没有任何文件")
                return True
            
            # 显示警告信息
            print(f"警告：这将删除 '{folder_path}' 文件夹中的所有文件（共 {files_count} 个文件）")
            print("此操作不可恢复！")
            
            # 获取用户确认
            confirmation = input("确认删除？(输入 'yes' 继续): ").strip().lower()
            
            if confirmation == 'yes':
                # 遍历并删除文件
                deleted_count = 0
                for item in items:
                    item_path = os.path.join(folder_path, item)
                    try:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                            deleted_count += 1
                    except Exception as e:
                        print(f"删除文件 '{item}' 时出错: {e}")
                
                print(f"成功删除 {deleted_count} 个文件")
                return True
            else:
                print("操作已取消")
                return False
                
        except Exception as e:
            print(f"操作出错: {e}")
            return False

    remove_files_in_folder("data/pages/md")

    # Generate markdown digest
    w = MDWriter()
    print("Generating digest...")

    markdown_content = f'''# RSS Digest
    **Time Generated**: {datetime.today().strftime("%Y-%m-%d %H:%M")}
    '''

    article_lst = []
    with os.scandir(json_dir) as entries:
        for entry in entries:
            doc_path = json_dir + entry.name
            # print(doc_path)
            
            article_lst.append(w.json_to_markdown(doc_path))
            # print(article_summary)
            # print(article_score)
            
    article_lst.sort(key=lambda t: t[1], reverse=True)
    for t in article_lst:
        markdown_content += t[0]
        

    with open("data/output/RSS Digest.md", 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print("Done. Digest in data/output/RSS Digest.md")

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