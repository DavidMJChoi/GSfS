import os
from datetime import datetime

from src.md_writer import MDWriter

json_dir = "data/pages/json/"
       
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