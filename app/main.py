"""
The 55 App - FastAPI entry point

A real-time facilitation tool for leadership alignment diagnostics.
"""

import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.db.database import Base, engine, get_db
from app.routers import images_router, auth_router, admin_router, teams_router, members_router, sessions_router, participant_router, qr_router, demo_router, analytics_router


# Define paths
APP_DIR = Path(__file__).parent
BASE_DIR = APP_DIR.parent  # Parent of app/ is the site root
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup: create database tables
    Base.metadata.create_all(bind=engine)

    # Process library images (resize for web if needed)
    from app.services.image_processor import run_on_startup
    run_on_startup()

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
app.include_router(qr_router)
app.include_router(demo_router)
app.include_router(analytics_router)


# Custom exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: StarletteHTTPException):
    """Custom 404 page for browser requests."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request},
            status_code=404
        )
    # Return JSON for API requests
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found"}
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception):
    """Custom 500 page for browser requests."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return templates.TemplateResponse(
            "errors/500.html",
            {"request": request},
            status_code=500
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.get("/")
def root(request: Request):
    """Landing page with links to main functions."""
    from fastapi.responses import HTMLResponse
    from pathlib import Path

    template_path = TEMPLATES_DIR / "landing.html"
    html_content = template_path.read_text()
    return HTMLResponse(content=html_content)


@app.post("/api/track-email")
async def track_email_click(request: Request, db: Session = Depends(get_db)):
    """Track email CTA click before mailto opens."""
    from app.db.models import ConversionEvent, EventType

    # Try to parse request body for source context
    try:
        body = await request.json()
        source = body.get("source", "unknown")
    except:
        source = "unknown"

    event = ConversionEvent(
        event_type=EventType.EMAIL_CLICK,
        event_data=json.dumps({"source": source})
    )
    db.add(event)
    db.commit()
    return {"status": "tracked"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
