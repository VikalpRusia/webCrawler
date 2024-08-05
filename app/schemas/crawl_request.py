from pydantic import BaseModel, Field


class CrawlRequest(BaseModel):
    url: str = Field(..., pattern="^https?://")
