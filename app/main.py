import logging

from api import router as api_router
from fastapi import FastAPI

# set the logging level
logging.basicConfig(level=logging.DEBUG)

app = FastAPI(docs_url="/")
app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health():
    """Health api"""
    # required for k8 to check whether pod is alive or not
    # docs api can also be used
    return {"status": "healthy"}
