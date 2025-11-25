"""
Declaration of modification:
    No change.
"""

"""
All scraper MUST provide the same interface and the same result format.
"""
from urllib.parse import quote, unquote
from typing import Optional, TypedDict, List


class ProxyConfig(TypedDict):
    http: str
    https: str


class ScraperResult(TypedDict):
    content: str
    errors: List[str]


def fetch_content(
    url: str,
    timeout_ms: int,
    proxy: Optional[ProxyConfig] = None,
    **kwargs
) -> ScraperResult:
    """
    Fetch web content from the specified url.
    :param url: The url to fetch.
    :param timeout_ms: The timeout in ms.
    :param proxy: The proxy setting. In requests format.
        {
            "http": "socks5://user:password@proxy_host:port",
            "https": "socks5://user:password@proxy_host:port"
        }
    :return:
        {
            'content': 'web content',           # The content in str. If it's an empty string, that means scrap fail.
            'errors': ['error description'],    # The error list of str
            'other optional fields': Any        # Any other extra fields that depends on scraper itself.
        }
    """
    return {
        'content': '',
        'errors': ['This is just an example of scraper implementation,']
    }
