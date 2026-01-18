"""
The 55 App - FastAPI entry point

A real-time facilitation tool for leadership alignment diagnostics.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# Define paths
APP_DIR = Path(__file__).parent
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    yield
    # Shutdown


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


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
