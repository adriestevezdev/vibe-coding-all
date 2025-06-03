"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers (to be created)
# from src.routes import auth, projects, prompts, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up Vibe Coding API...")
    # Initialize database connection, etc.
    yield
    # Shutdown
    print("Shutting down Vibe Coding API...")

# Create FastAPI app
app = FastAPI(
    title="Vibe Coding API",
    description="API for Vibe Coding SaaS platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Vibe Coding API", "version": "1.0.0"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
# app.include_router(prompts.router, prefix="/api/prompts", tags=["prompts"])
# app.include_router(users.router, prefix="/api/users", tags=["users"])
