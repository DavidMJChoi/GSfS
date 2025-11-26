import os
from openai import OpenAI

import src.prompt

class LLMScorer():
    def __init__(self):
        self.client = OpenAI(
            api_key = os.environ.get('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com"
        )

    def score(self, doc_path):

        # read doc
        with open(doc_path, 'r', encoding='utf-8') as f:
            doc_content = f.read()

        if not doc_content:
            return "NO DOC"

        full_prompt = f"{src.prompt.ANALYSIS_PROMPT}\n\n Document Content:\n{doc_content}"

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages = [
                {"role": "user", "content": full_prompt}
            ]
        )

        return response.choices[0].message.content

if __name__ == "__main__":
    s = LLMScorer()

    output = s.score("./data/pages/md/Python_is_not_a_great_language_for_data_science.md")

    with open("temp.txt", "w", encoding='utf-8') as f:
        f.write(output)