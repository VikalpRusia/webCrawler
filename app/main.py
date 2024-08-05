from fastapi import FastAPI
from api import router as api_router


app = FastAPI(docs_url="/")
app.include_router(api_router)
