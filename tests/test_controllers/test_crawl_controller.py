"""Tests crawl"""

import contextlib
import os
from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from controllers.crawl_controller import CrawlController
from helper.redis_helper import RedisHelper


class TestCrawlController:
    """Test Crawl Controller"""

    @classmethod
    def setup_class(cls):
        """setup any state specific to the execution of the given class (which
        usually contains tests).
        """
        cls.crawl_controller = CrawlController()

    def test_extract_links(self):
        """
        Tests link extraction logic
        :return:
        """
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(
            current_dir, "html", "external-and-internal-links.html"
        )
        with open(file_path, mode="r", encoding="utf-8") as file:
            test_str = file.read()
            links = self.crawl_controller.extract_links(test_str, ".")
            assert links == [
                "/",
                "https://fonts.googleapis.com/css2",
                "https://fonts.googleapis.com/icon",
                "external-links-only",
            ]

            links = self.crawl_controller.extract_links(test_str, "www.foo.bar.com/")
            assert links == [
                "/",
                "https://fonts.googleapis.com/css2",
                "https://fonts.googleapis.com/icon",
                "www.foo.bar.com/external-links-only",
            ]

    @pytest.mark.asyncio
    async def test_crawl(self, mocker: MockerFixture):
        """
        Tests the crawl logic
        :param mocker:
        :return:
        """
        # connect redis client
        await RedisHelper().connect()
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(
            current_dir, "html", "external-and-internal-links.html"
        )

        # Create mock responses for different URLs
        mock_response_1 = mocker.MagicMock()
        mock_response_1.status = 200
        with open(file_path, mode="r", encoding="utf-8") as file:
            mock_response_1.text = AsyncMock(return_value=file.read())

        file_path = os.path.join(current_dir, "html", "external-links-only.html")
        mock_response_2 = mocker.MagicMock()
        mock_response_2.status = 200
        with open(file_path, mode="r", encoding="utf-8") as file:
            mock_response_2.text = AsyncMock(return_value=file.read())

        @contextlib.asynccontextmanager
        async def mock_get_side_effect(url):
            """
            mock the async request
            :param url:
            :return:
            """
            if url == "https://foo.com/external-and-internal-links":
                yield mock_response_1
            elif url == "https://foo.com/external-links-only":
                yield mock_response_2
            else:
                yield mocker.MagicMock()  # Default mock

        mocker.patch("aiohttp.ClientSession.get", wraps=mock_get_side_effect)
        sitemap, errors = await self.crawl_controller.crawl(
            "https://foo.com/external-and-internal-links"
        )
        assert sitemap == {
            "https://foo.com/external-and-internal-links": [
                "https://foo.com/",
                "https://foo.com/external-links-only",
            ],
            "https://foo.com/external-links-only": ["https://foo.com/"],
        }
        # since home page is unreachable as status code is undefined
        assert len(errors) == 1
