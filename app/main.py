import logging

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.projects import router as project_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.reviews import router as review_router
from app.api.documents import router as document_router
from app.api.chunks import router as chunks_router
from app.api.embeddings import router as embeddings_router
from app.api.search import router as search_router
from app.api.rag import router as rag_router

setup_logging()

logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-powered medical writing and "
        "evidence verification platform."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)


app.include_router(
    health_router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    project_router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    auth_router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    admin_router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    review_router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    search_router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    embeddings_router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    document_router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    rag_router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    chunks_router,
    prefix=settings.API_PREFIX,
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting %s", settings.APP_NAME)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Stopping %s", settings.APP_NAME)


@app.get("/")
async def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "Medical Writing AI API is running",
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}