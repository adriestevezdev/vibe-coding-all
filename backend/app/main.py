"""
Main FastAPI application module.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import time
from loguru import logger
from app.core.config import settings
from app.core.logging import setup_logging

# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting up Vibe Coding application...")
    yield
    # Shutdown
    logger.info("Shutting down Vibe Coding application...")


# Create FastAPI instance
app = FastAPI(
    title="Vibe Coding API",
    description="Backend API for Vibe Coding platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.vibe-coding.com"]
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to track request processing time."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {process_time:.3f}s")
    return response

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Vibe Coding API", "version": "1.0.0"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "vibe-coding-api"}

# Import and include routers
from app.routers import auth, projects, prompts, share
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(projects.router, prefix="/api", tags=["projects"])
app.include_router(prompts.router, prefix="/api", tags=["prompts"])
app.include_router(share.router, prefix="/api", tags=["share"])

# TODO: Add more routers as needed
# from app.api import users, ai
# app.include_router(users.router, prefix="/api/users", tags=["users"])
# app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
