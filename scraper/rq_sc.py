import gzip
import zlib
import random
import requests
from bs4 import BeautifulSoup
from typing import Optional

from scbase import ProxyConfig, ScraperResult


# rq scraper

try:
    import brotli
except ImportError:
    brotli = None


class RequestsScraper:
    def __init__(self, proxies: Optional[dict] = None):
        self.session = requests.Session()
        self.session.proxies = proxies or {}
        self._init_headers()

    def _init_headers(self):
        """动态生成浏览器级请求头"""
        self.headers = {
            'User-Agent': self._random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',  # 明确声明支持的压缩格式
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://www.google.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1'
        }

    def _random_user_agent(self):
        """生成随机现代浏览器UA"""
        chrome_versions = [
            (122, 0, 6261), (121, 0, 6167), (120, 0, 6099),
            (119, 0, 6045), (118, 0, 5993)
        ]
        version = random.choice(chrome_versions)
        return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version[0]}.0.{version[1]}.{version[2]} Safari/537.36"

    def _decode_response(self, response: requests.Response, content: bytes) -> str:
        """统一手动处理所有解压逻辑"""
        content_encoding = response.headers.get('Content-Encoding', '').lower()
        encodings = [e.strip() for e in content_encoding.split(',') if e.strip()]

        # 根据RFC标准，解压顺序应与编码顺序相反
        for encoding in reversed(encodings):
            if encoding == 'br':
                if not brotli:
                    raise RuntimeError("Brotli压缩格式需要安装brotli库")
                try:
                    content = brotli.decompress(content)
                except Exception as e:
                    print(f"Brotli解压失败: {e}")
                    break
            elif encoding == 'gzip':
                try:
                    content = gzip.decompress(content)
                except Exception as e:
                    print(f"Gzip解压失败: {e}")
                    break
            elif encoding == 'deflate':
                try:
                    # 尝试使用zlib（含负窗口大小处理）
                    content = zlib.decompress(content, -zlib.MAX_WBITS)
                except zlib.error:
                    try:
                        # 回退到原始deflate格式
                        content = zlib.decompress(content)
                    except Exception as e:
                        print(f"Deflate解压失败: {e}")
                        break
            else:
                print(f"不支持的压缩格式: {encoding}")
                break

        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            return content.decode('latin-1', errors='replace')

    def set_proxies(self, proxies: dict):
        self.session.proxies = proxies

    def fetch(self, url, timeout=15) -> Optional[str]:
        try:
            # 启用stream模式并禁用自动解压
            response = self.session.get(
                url,
                headers=self.headers,
                timeout=timeout,
                allow_redirects=True,
                stream=True,
                verify=False            # TODO: Fix certs issue
            )
            response.raise_for_status()

            # 强制禁用自动解压并读取原始内容
            response.raw.decode_content = False
            raw_content = response.raw.read()

            # 更新Referer头
            self.headers['Referer'] = url

            return self._decode_response(response, raw_content)
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {str(e)}")
        except Exception as e:
            print(f"意外错误: {str(e)}")
        return None


def check_content_quality(html: str, format: str, target_keywords=None):
    """
    网页内容质量评估系统
    返回：tuple (is_valid, score, issues)
    evaluate if a page is static -> is_valid == True
    """
    soup = BeautifulSoup(html, format)
    report = {'score': 100, 'issues': []}

    # 基础结构检测（网页6/7的完整性标准）
    # if the content is dynamic, body will not be detected
    if not soup.find('body') or not soup.find('html'):
        report['issues'].append('Missing essential HTML tags')
        report['score'] -= 40

    # 主要内容容器检测（网页3/7的架构建议）
    main_content = soup.find(['main', 'div#content', 'article', 'div.container'])
    if not main_content:
        report['issues'].append('Missing main content container')
        report['score'] -= 30

    # 数据密度分析（网页6的内容丰富性标准）
    text_length = len(soup.get_text(strip=True))
    tag_count = len(soup.find_all())
    if tag_count > 0:
        text_ratio = text_length / tag_count
        if text_ratio < 0.3:  # 文本/标签比阈值
            report['issues'].append('Low text density (possible ads/spam)')
            report['score'] -= 25

    # 反爬机制检测（网页3/5的异常识别）
    anti_scraping_phrases = [
        'enable javascript', 'access denied',
        'cloudflare security', 'captcha'
    ]
    page_text = soup.get_text().lower()
    if any(phrase in page_text for phrase in anti_scraping_phrases):
        report['issues'].append('Anti-scraping mechanism detected')
        report['score'] -= 50

    # 动态内容检测（网页1/3的SPA识别）
    if soup.find('noscript') or soup.find('div', class_='loading'):
        report['issues'].append('Dynamic content placeholders found')
        report['score'] -= 20

    # 关键词覆盖检测（网页6/7的相关性标准）
    if target_keywords:
        matched_keywords = sum(
            1 for kw in target_keywords if kw.lower() in page_text
        )
        coverage = matched_keywords / len(target_keywords)
        if coverage < 0.6:
            report['issues'].append(f'Low keyword coverage ({coverage:.0%})')
            report['score'] -= 15 * (1 - coverage)

    # 最终结果判定
    is_valid = (
            report['score'] >= 70
            and 'Anti-scraping mechanism detected' not in report['issues']
    )

    return is_valid, max(report['score'], 0), report['issues']


def fetch_content(
    url: str,
    timeout_ms: int,
    proxy: Optional[ProxyConfig] = None,
    format: str = 'xml',
    **kwargs
) -> ScraperResult:
    """
    The same as base.
    :param url: The same as base.
    :param timeout_ms: The same as base.
    :param proxy: Format: The same as base.
    :param format: Specify format to check.
    :return: The same as base.
    """

    scraper = RequestsScraper(proxy)
    html_content = scraper.fetch(url, int(timeout_ms / 1000))
    if html_content:
        is_valid, score, issues = check_content_quality(html_content, format)
        return {
            'content': html_content,
            'errors': issues,
            'valid': is_valid,
            'score': score,
        }
    else:
        return {
            'content': '',
            'errors': [],
        }


# ----------------------------------------------------------------------------------------------------------------------

def main():
    proxies = {
        "http": "socks5://user:password@proxy_host:port",
        "https": "socks5://user:password@proxy_host:port"
    }

    # result = fetch_content('https://www.cbc.ca/news/world/israel-gaza-aid-military-1.7538495?cmp=rss', 30000)
    
    # an example static page
    result = fetch_content("https://www3.pioneer.com/argentina/PETWS/test.html",30000)

    if result['content']:
        print(f'Content : {result["content"]}')
        print('')
        print(f'Valid : {result["valid"]}')
        print(f'Score : {result["score"]}')
    print(f'Errors : {result["errors"]}')

if __name__ == "__main__":
    main()