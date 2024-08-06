"""Tests crawl"""
import contextlib
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
        test_str = """
<!doctype html>
<html lang="en">
<head>
  <script type="module" src="/@vite/client"></script>
  <meta charset="utf-8">
  <base href="/">
  <meta content="width=device-width, initial-scale=1" name="viewport">
  <link href="favicon.ico" rel="icon" type="image/x-icon">
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&amp;display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<link rel="stylesheet" href="styles.css"></head>
<body cds-theme="light" class="mat-typography">
<a href="./testing"></a>
<script src="polyfills.js" type="module"></script><script src="main.js" type="module"></script></body>
</html>
        """
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
        await RedisHelper().connect()
        # Create mock responses for different URLs
        mock_response_1 = mocker.MagicMock()
        mock_response_1.status = 200
        mock_response_1.text = AsyncMock(
            return_value="""
<!doctype html>
<html lang="en">
<head>
  <script type="module" src="/@vite/client"></script>
  <meta charset="utf-8">
  <base href="/">
  <meta content="width=device-width, initial-scale=1" name="viewport">
  <link href="favicon.ico" rel="icon" type="image/x-icon">
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&amp;display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<link rel="stylesheet" href="styles.css"></head>
<body cds-theme="light" class="mat-typography">
<a href="./test-2"></a>
<script src="polyfills.js" type="module"></script><script src="main.js" type="module"></script></body>
</html>
        """
        )

        mock_response_2 = mocker.MagicMock()
        mock_response_2.status = 200
        mock_response_2.text = AsyncMock(
            return_value="""
<!doctype html>
<html lang="en">
<head>
  <script type="module" src="/@vite/client"></script>
  <meta charset="utf-8">
  <base href="/">
  <meta content="width=device-width, initial-scale=1" name="viewport">
  <link href="favicon.ico" rel="icon" type="image/x-icon">
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&amp;display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<link rel="stylesheet" href="styles.css"></head>
<body cds-theme="light" class="mat-typography">
<script src="polyfills.js" type="module"></script><script src="main.js" type="module"></script></body>
</html>
        """
        )

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
