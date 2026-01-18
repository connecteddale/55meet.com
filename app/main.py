"""
The 55 App - FastAPI entry point

A real-time facilitation tool for leadership alignment diagnostics.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db.database import Base, engine
from app.routers import images_router, auth_router, admin_router, teams_router, members_router, sessions_router, participant_router


# Define paths
APP_DIR = Path(__file__).parent
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup: create database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: cleanup if needed


# Create FastAPI app
app = FastAPI(
    title="The 55",
    description="Leadership alignment diagnostics - 55 minutes, once a month",
    version="2.0.0",
    lifespan=lifespan,
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Configure templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# Include routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(teams_router)
app.include_router(members_router)
app.include_router(sessions_router)
app.include_router(images_router)
app.include_router(participant_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
