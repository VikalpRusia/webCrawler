"""Combines all router of v1 apis"""

from fastapi import APIRouter

from .crawl_api import router as crawl_router

router = APIRouter(prefix="/v1", tags=["v1"])

router.include_router(crawl_router)
