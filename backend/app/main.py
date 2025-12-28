"""
FastAPI application entry point for Physical AI & Humanoid Robotics textbook backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

# Create FastAPI app
app = FastAPI(
    title="Physical AI & Humanoid Robotics API",
    description="Backend API for AI-native interactive textbook with RAG chatbot",
    version="1.0.0",
)

# Configure CORS
origins = settings.cors_origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Physical AI & Humanoid Robotics API",
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    from sqlalchemy import text
    from app.db.neon import engine
    from app.db.qdrant import qdrant_service

    # Check database connection
    db_status = "unknown"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "operational"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"

    # Check Qdrant connection
    qdrant_status = "unknown"
    try:
        collections = qdrant_service.client.get_collections()
        if qdrant_service.collection_exists():
            qdrant_status = "operational (collection exists)"
        else:
            qdrant_status = "connected (collection not created)"
    except Exception as e:
        qdrant_status = f"error: {str(e)[:50]}"

    return {
        "status": "healthy",
        "environment": settings.environment,
        "services": {
            "api": "operational",
            "database": db_status,
            "qdrant": qdrant_status,
        },
    }


# API routers
from app.api.v1 import chatbot, debug

app.include_router(chatbot.router, tags=["chatbot"])
app.include_router(debug.router, tags=["debug"])  # TEMPORARY - for testing SMTP config

# Future routers:
# from app.api.v1 import personalize
# app.include_router(personalize.router, prefix="/api/v1", tags=["personalize"])
