from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import os

from app.api.routes import documents, chat
from app.core.config import settings
from app.core.logging import logger
from app.db.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up DocMind backend...")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    yield
    
    # Shutdown
    logger.info("Shutting down DocMind backend...")
    await engine.dispose()

app = FastAPI(
    title="DocMind API",
    description="Backend API for DocMind RAG Chatbot",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(f"Global exception handler caught: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": type(exc).__name__,
                "detail": str(exc),
                "timestamp": str(time.time())
            }
        )
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(documents.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "vector_store_type": settings.VECTOR_STORE_TYPE,
        "db_connected": True # Should really check DB, but keeping simple
    }
