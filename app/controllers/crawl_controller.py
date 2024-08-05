import logging
import re
from urllib.parse import urljoin, urlparse

import aiohttp

logger = logging.getLogger(__name__)


class CrawlController:
    async def crawl(self, url: str):
        domain = urlparse(url).netloc
        visited = set()
        sitemap = {}
        errors = {}
        await self.crawl_page(url, visited, domain, sitemap, errors)
        return sitemap, errors

    async def crawl_page(
        self, url: str, visited: set, domain: str, sitemap: dict, errors: dict
    ):
        if url in visited or domain not in urlparse(url).netloc:
            return
        logger.debug(f"Crawling {url}")
        visited.add(url)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to crawl {url}: status {response.status}")
                        errors[url] = f"Failed with status code {response.status}"
                        return
                    sitemap[url] = []
                    html = await response.text()
                    links = self.extract_links(html, url)
                    for full_url in links:
                        if domain in urlparse(full_url).netloc:
                            sitemap[url].append(full_url)
                            await self.crawl_page(
                                full_url, visited, domain, sitemap, errors
                            )
        except Exception as e:
            logger.error(f"Failed to crawl {url}: {e}")
            errors[url] = f"Failed with exception {str(e)}"

    def extract_links(self, html, base_url):
        # Regex to find all href attributes in the HTML
        links = re.findall(r'href=["\'](.*?)["\']', html)
        # Remove fragment identifiers
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
            cleaned_complete_link = urljoin(base_url, link)
            if not cleaned_complete_link.endswith((".png", ".css", ".ico")):
                full_urls.append(cleaned_complete_link)
        return full_urls
