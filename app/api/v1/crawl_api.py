from typing import Annotated

from fastapi import APIRouter, Body
from fastapi_restful.cbv import cbv

from schemas.crawl_request import CrawlRequest

router = APIRouter(prefix="/crawl", tags=["crawl"])

@cbv(router)
class CrawlAPI:
    """
    Holds the crawler api routes
    """

    @router.post("/crawl")
    async def crawl(self, request:CrawlRequest):
        """Generate a sitemap"""
        pass
