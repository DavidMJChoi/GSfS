import datetime
from dataclasses import dataclass
import json
import logging
import pathlib
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class Article:
    """
    Data class to represent an article
    """
    title: str
    pub_date: datetime
    link: str
    content: str
    feed_name: str

class RSSProcessor:
    """
    An RSS processor which 
    1. processes feeds from a JSON configuration file.
    2. download article contents.

    Attributes:
        config_path (str): path to the JSON config file
        timeout (int): request timeout in seconds
        retry_attempts (int): number of retry attemps for failed requests
    """

    def __init__(self, config_path: str, timeout: int=10, retry_attempts: int=3):
        self.config_path = config_path
        self.timeout = int(timeout)
        self.retry_attempts = int(retry_attempts)

        # logger
        self.logger = logging.getLogger(__name__)

        # HTTP session with retries and a sensible User-Agent
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.retry_attempts,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "POST", "HEAD", "OPTIONS"])
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({"User-Agent": "GSfS-RSS-Collector/1.0"})

        # config and feed list
        self.config = {}
        self.feeds = []
        try:
            with open(self.config_path, "r", encoding="utf-8") as fh:
                self.config = json.load(fh) or {}
                self.feeds = self.config.get("feeds", [])
        except FileNotFoundError:
            self.logger.debug("Config file not found: %s", self.config_path)
        except Exception as e:
            self.logger.debug("Failed to load config %s: %s", self.config_path, e)

        # cache directory
        default_cache = pathlib.Path.home() / ".cache" / "rss_collector"
        self.cache_dir = pathlib.Path(self.config.get("cache_dir", default_cache))
        self.cache_dir.mkdir(parents=True, exist_ok=True)