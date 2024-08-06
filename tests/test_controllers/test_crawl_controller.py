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
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "html", "file-1.html")
        with open(file_path, mode="r", encoding="utf-8") as file:
            test_str = file.read()
            links = self.crawl_controller.extract_links(test_str, ".")
            assert links == [
                "/",
                "https://fonts.googleapis.com/css2",
                "https://fonts.googleapis.com/icon",
                "testing",
            ]

            links = self.crawl_controller.extract_links(test_str, "www.foo.bar.com/")
            assert links == [
                "/",
                "https://fonts.googleapis.com/css2",
                "https://fonts.googleapis.com/icon",
                "www.foo.bar.com/testing",
            ]

    @pytest.mark.asyncio
    async def test_crawl(self, mocker: MockerFixture):
        # connect redis client
        await RedisHelper().connect()
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "html", "file-2.html")

        # Create mock responses for different URLs
        mock_response_1 = mocker.MagicMock()
        mock_response_1.status = 200
        with open(file_path, mode="r", encoding="utf-8") as file:
            mock_response_1.text = AsyncMock(return_value=file.read())

        file_path = os.path.join(current_dir, "html", "file-3.html")
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
            if url == "https://foo.com/test-1":
                yield mock_response_1
            elif url == "https://foo.com/test-2":
                yield mock_response_2
            else:
                yield mocker.MagicMock()  # Default mock

        mocker.patch("aiohttp.ClientSession.get", wraps=mock_get_side_effect)
        sitemap, errors = await self.crawl_controller.crawl("https://foo.com/test-1")
        assert sitemap == {
            "https://foo.com/test-1": ["https://foo.com/", "https://foo.com/test-2"],
            "https://foo.com/test-2": ["https://foo.com/"],
        }
