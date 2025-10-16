from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes.chat import router as chat_router
from app.api.routes.file import router as file_router
from app.api.routes.cliente import router as cliente_router
from app.database import connect_to_mongo, close_mongo_connection
from app.api.routes.rag import router as rag_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown  
    await close_mongo_connection()

app = FastAPI(
    title="Harmonização API (Groq + FastAPI + MongoDB)", 
    version="1.0.0",
    lifespan=lifespan
)

if settings.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(chat_router)
app.include_router(file_router, prefix="/file", tags="file")
app.include_router(cliente_router)
app.include_router(rag_router, tags=["rag"])