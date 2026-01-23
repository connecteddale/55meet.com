"""
Images API router - serves paginated image list with session-seeded randomization.

v2.1: Updated for auto-discovery and 200+ image support.
"""

from typing import Optional

from fastapi import APIRouter, Query

from app.services.images import get_image_library

router = APIRouter(prefix="/api", tags=["images"])


@router.get("/images")
async def list_images(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    per_page: int = Query(42, ge=1, le=100, description="Images per page"),
    seed: Optional[int] = Query(None, description="Random seed for consistent ordering (typically session_id)")
):
    """
    Return paginated list of available images.

    When seed is provided, images are shuffled in a deterministic order.
    Same seed always produces same order, enabling consistent navigation.

    Args:
        page: Page number (1-indexed, default 1)
        per_page: Images per page (default 42, max 100)
        seed: Random seed for shuffling (optional, typically session_id)

    Returns:
        {
            images: [{id, filename, url}, ...],
            total: int,
            page: int,
            per_page: int,
            total_pages: int
        }
    """
    library = get_image_library()

    if seed is not None:
        return library.get_paginated_images(seed, page, per_page)
    else:
        # No seed = return in discovery order (sorted by filename)
        images = library.discover_images()
        total = len(images)
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1
        page = max(1, min(page, total_pages))
        start = (page - 1) * per_page
        end = start + per_page

        return {
            "images": images[start:end],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }


@router.get("/images/count")
async def image_count():
    """Return total number of available images."""
    library = get_image_library()
    return {"count": library.count}
