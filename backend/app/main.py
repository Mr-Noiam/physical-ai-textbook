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
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "services": {
            "api": "operational",
            "database": "pending",  # Will update after DB connection
            "qdrant": "pending",    # Will update after Qdrant connection
        }
    }


# API routers
from app.api.v1 importms chatbot

app.include_router(chatbot.router, tags=["chatbot"])

# Future routers:
# from app.api.v1 import auth, personalize, translate
# app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
# app.include_router(personalize.router, prefix="/api/v1", tags=["personalize"])
# app.include_router(translate.router, prefix="/api/v1", tags=["translate"])
