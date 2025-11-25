import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.rss_reader import RSSReader
from src.md_writer import MDWriter

def test_integration():
    """测试整个流程的集成"""
    print("🧪 开始集成测试...")
    
    # 初始化
    reader = RSSReader()
    writer = MDWriter()
    
    # 获取文章
    articles = reader.fetch_all_feeds()
    print(f"获取到 {len(articles)} 篇文章")
    
    if articles:
        # 生成Markdown
        output_file = writer.write_to_markdown(articles, "test_output.md")
        print(f"测试文件生成: {output_file}")
        
        # 显示前3篇文章的标题
        print("\n前3篇文章:")
        for i, article in enumerate(articles[:3]):
            print(f"{i+1}. {article['title'][:50]}...")
    else:
        print("❌ 没有获取到文章，请检查网络或RSS源")

if __name__ == "__main__":
    test_integration()