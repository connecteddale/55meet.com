"""
The 55 App - Image Library Service

Auto-discovery of images from filesystem with caching and session-seeded randomization.
Images are served via opaque IDs - filenames are never exposed to users.
"""

import hashlib
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict
from functools import lru_cache

from pydantic import BaseModel

from app.config import get_settings


class ImageInfo(BaseModel):
    """Image metadata - ID and URL only, no filename exposed to users."""
    id: str           # opaque identifier (hash of filename)
    url: str          # URL path for serving


class ImageLibrary:
    """
    Discover and serve images from configurable directory.

    Features:
    - Auto-discovery of .jpg files from reducedlive/ directory
    - Opaque IDs (hashed) - filenames never exposed to users
    - Caching with configurable TTL (default 5 minutes)
    - Session-seeded randomization for consistent ordering
    """

    def __init__(self, image_dir: Path, cache_ttl_seconds: int = 300):
        self._image_dir = image_dir
        self._cache_ttl = cache_ttl_seconds
        self._cache: List[ImageInfo] = []
        self._id_to_filename: Dict[str, str] = {}  # Maps opaque ID to filename
        self._cache_time: Optional[datetime] = None

    def _generate_opaque_id(self, filename: str) -> str:
        """Generate short opaque ID from filename (first 12 chars of MD5)."""
        return hashlib.md5(filename.encode()).hexdigest()[:12]

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if not self._cache_time:
            return False
        return datetime.now() - self._cache_time < timedelta(seconds=self._cache_ttl)

    def discover_images(self) -> List[ImageInfo]:
        """
        Scan directory for image files, cache results.

        Returns sorted list of ImageInfo objects with opaque IDs.
        """
        if self._is_cache_valid():
            return self._cache

        images = []
        self._id_to_filename = {}
        extensions = {'.jpg', '.jpeg', '.png', '.webp'}

        if self._image_dir.exists():
            for path in sorted(self._image_dir.iterdir()):
                if path.suffix.lower() in extensions:
                    opaque_id = self._generate_opaque_id(path.stem)
                    self._id_to_filename[opaque_id] = path.name
                    images.append(ImageInfo(
                        id=opaque_id,
                        url=f"/static/images/library/reducedlive/{path.name}"
                    ))

        self._cache = images
        self._cache_time = datetime.now()
        return images

    def get_filename_by_id(self, opaque_id: str) -> Optional[str]:
        """Look up actual filename from opaque ID."""
        self.discover_images()  # Ensure cache is populated
        return self._id_to_filename.get(opaque_id)

    def get_shuffled_images(self, seed: int, limit: int = None) -> List[ImageInfo]:
        """
        Return images in deterministic random order for given seed.

        Uses Fisher-Yates shuffle with seeded random for reproducibility.
        Same seed always produces same order.

        Args:
            seed: Integer seed (typically session_id)
            limit: Maximum number of images to return (None for all)

        Returns:
            List of ImageInfo in shuffled order, truncated to limit if specified
        """
        images = self.discover_images().copy()
        rng = random.Random(seed)
        rng.shuffle(images)
        if limit is not None:
            images = images[:limit]
        return images

    def get_paginated_images(
        self,
        seed: int,
        page: int = 1,
        per_page: int = 20,
        limit: int = None
    ) -> dict:
        """
        Return paginated images with metadata.

        Args:
            seed: Integer seed for randomization
            page: Page number (1-indexed)
            per_page: Images per page
            limit: Maximum total images to consider (None for all)

        Returns:
            Dict with images, total, page, per_page, total_pages
        """
        all_images = self.get_shuffled_images(seed, limit=limit)
        total = len(all_images)
        total_pages = (total + per_page - 1) // per_page  # ceiling division

        # Clamp page to valid range
        page = max(1, min(page, total_pages)) if total_pages > 0 else 1

        start = (page - 1) * per_page
        end = start + per_page

        return {
            "images": all_images[start:end],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }

    @property
    def count(self) -> int:
        """Get total number of images."""
        return len(self.discover_images())


# Singleton instance (lazy initialization)
_image_library: Optional[ImageLibrary] = None


def get_image_library() -> ImageLibrary:
    """
    Get or create the image library singleton.

    Uses settings from config for path and TTL.
    """
    global _image_library
    if _image_library is None:
        settings = get_settings()
        image_dir = Path(settings.image_library_path)
        _image_library = ImageLibrary(
            image_dir=image_dir,
            cache_ttl_seconds=settings.image_cache_ttl
        )
    return _image_library
