import logging

from fastapi import FastAPI
from api import router as api_router

# set the logging level
logging.basicConfig(level=logging.DEBUG)

app = FastAPI(docs_url="/")
app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
