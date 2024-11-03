from contextlib import asynccontextmanager

from dotenv import load_dotenv

from fastapi import FastAPI, Request

from .db import create_db_and_tables
from .templates import templates

from .document.router import router as document_router

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(document_router, prefix="/documents")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Home"
    })
