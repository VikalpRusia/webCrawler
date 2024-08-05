"""Main module starts the server"""
from fastapi import FastAPI
from fastapi.middleware import Middleware

from api import router as api_router
from middlewares.time_taken_middleware import TimeTakenMiddleware
from middlewares.uuid_middleware import UUIDMiddleware
from setup import setup_logger

setup_logger()

# setup_logger()
middlewares = [
    Middleware(UUIDMiddleware),
    Middleware(TimeTakenMiddleware),
]

app = FastAPI(docs_url="/", middleware=middlewares)
app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health():
    """Health api"""
    # required for k8 to check whether pod is alive or not
    # docs api can also be used
    return {"status": "healthy"}
