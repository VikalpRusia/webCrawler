"""Crawl request schema"""
from pydantic import BaseModel, Field


class CrawlRequest(BaseModel):
    """Crawl request model"""

    # pylint: disable=too-few-public-methods
    url: str = Field(..., pattern="^https?://")
