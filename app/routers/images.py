"""Images API router - serves image list for participant flow."""

from fastapi import APIRouter
from pathlib import Path

router = APIRouter(prefix="/api", tags=["images"])

IMAGES_DIR = Path(__file__).parent.parent / "static" / "images" / "55"


@router.get("/images")
async def list_images():
    """Return list of available images."""
    images = sorted([
        {
            "number": int(f.stem),
            "filename": f.name,
            "url": f"/static/images/55/{f.name}"
        }
        for f in IMAGES_DIR.glob("*.svg")
    ], key=lambda x: x["number"])
    return {"images": images, "count": len(images)}
