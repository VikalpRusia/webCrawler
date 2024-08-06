"""Holds the crawl controller class"""
import logging
import re
import traceback
from urllib.parse import urljoin, urlparse

import aiohttp

from config.constants import EXTENSIONS_TO_FILTER
from helper.redis_helper import RedisHelper

logger = logging.getLogger(__name__)


class CrawlController:
    """Holds the business logic for crawling websites"""

    def __init__(self):
        self.redis_helper = RedisHelper()
        logger.info(id(self.redis_helper))

    async def crawl(self, url: str):
        """Crawls a website"""
        domain = urlparse(url).netloc
        visited = set()
        sitemap = {}
        errors = {}
        await self.crawl_page(url, visited, domain, sitemap, errors)
        return sitemap, errors

    async def crawl_page(
        self, url: str, visited: set, domain: str, sitemap: dict, errors: dict
    ):
        """Recursively calling website using DFS in graph"""
        if url in visited or domain not in urlparse(url).netloc:
            # if page is already visited return
            return
        logger.debug(f"Crawling {url}")
        visited.add(url)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        # broken link saving error for partial result
                        logger.error(f"Failed to crawl {url}: status {response.status}")
                        errors[url] = f"Failed with status code {response.status}"
                        return
                    sitemap[url] = []
                    html = await response.text()
                    links = self.extract_links(html, url)
                    for full_url in links:
                        # check domain is a subset or original one
                        # if exact match is needed can be replaced with ==
                        if domain in urlparse(full_url).netloc:
                            sitemap[url].append(full_url)
                            await self.crawl_page(
                                full_url, visited, domain, sitemap, errors
                            )
        except Exception as e:
            logger.error(f"Failed to crawl {url}: {e}")
            logger.error(traceback.format_exc())
            errors[url] = f"Failed with exception {str(e)}"

    def extract_links(self, html, base_url):
        """
        Extracts links from HTML
        :param html:
        :param base_url:
        :return:
        """
        # Regex to find all href attributes in the HTML
        links = re.findall(r'href=["\'](.*?)["\']', html)
        # Remove fragment identifiers and query params
        cleaned_urls = [
            urlparse(url)
            ._replace(
                query="",
                fragment="",
            )
            .geturl()
            for url in links
        ]
        # Resolve relative URLs to absolute URLs
        full_urls = []
        for link in cleaned_urls:
            # generate absolute urls
            cleaned_complete_link = urljoin(base_url, link)
            # remove links to images,css etc.
            if not cleaned_complete_link.endswith(EXTENSIONS_TO_FILTER):
                full_urls.append(cleaned_complete_link)
        return full_urls
