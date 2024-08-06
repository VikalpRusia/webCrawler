"""Holds Crawler api class"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi_restful.cbv import cbv

from controllers.crawl_controller import CrawlController
from schemas.crawl_request import CrawlRequest

router = APIRouter(prefix="/crawl", tags=["crawl"])


@cbv(router)
class CrawlAPI:
    """
    Holds the crawler api routes
    """

    def __init__(self):
        self.crawl_controller = CrawlController()

    @router.post("/")
    async def crawl(self, request: CrawlRequest):
        """
        Generate a compressed site_map
        :param request:
        :return:
        """
        sitemap, errors = await self.crawl_controller.crawl(request.url)
        if errors:
            if sitemap:
                return JSONResponse(
                    status_code=status.HTTP_207_MULTI_STATUS,
                    content={
                        "status": "partial_success",
                        "sitemap": sitemap,
                        "errors": errors,
                    },
                )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "failure", "errors": errors},
            )
        return sitemap
