from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.core.deps import get_db
from app.db.events import register_listeners
from app.middleware import RequestLogger
from app.middleware.instrumentation import add_instrumentation


@asynccontextmanager
async def lifespan(app: FastAPI):
    register_listeners()
    yield

app = FastAPI(lifespan=lifespan, root_path=settings.ROOT_PATH)

add_instrumentation(app)

app.include_router(api_router)
app.add_middleware(RequestLogger)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root(db=Depends(get_db)):
    return {"message": "Hello World"}
