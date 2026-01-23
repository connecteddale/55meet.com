"""
Image Processor Service

Reduces original library images for web/mobile display.
- Resizes to max 800x800 while maintaining aspect ratio
- Corrects EXIF orientation (rotates images right-way-up)
- Compresses to web-friendly size (~100-200KB)
- Skips images already processed

Source: /static/images/library/
Output: /static/images/library/reducedlive/
"""

import os
from pathlib import Path
from PIL import Image, ExifTags

# Configuration
MAX_SIZE = (800, 800)  # Max dimensions
JPEG_QUALITY = 85  # Balance of quality vs file size
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

# Paths relative to app
BASE_DIR = Path(__file__).resolve().parent.parent
LIBRARY_DIR = BASE_DIR / "static" / "images" / "library"
OUTPUT_DIR = LIBRARY_DIR / "reducedlive"


def get_exif_orientation(image: Image.Image) -> int:
    """Get EXIF orientation tag value."""
    try:
        exif = image._getexif()
        if exif:
            for tag, value in exif.items():
                if ExifTags.TAGS.get(tag) == 'Orientation':
                    return value
    except (AttributeError, KeyError, IndexError):
        pass
    return 1  # Default: no rotation needed


def apply_exif_orientation(image: Image.Image) -> Image.Image:
    """Rotate image based on EXIF orientation tag."""
    orientation = get_exif_orientation(image)

    # Orientation values and their required transformations
    if orientation == 2:
        return image.transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation == 3:
        return image.rotate(180, expand=True)
    elif orientation == 4:
        return image.transpose(Image.FLIP_TOP_BOTTOM)
    elif orientation == 5:
        return image.transpose(Image.FLIP_LEFT_RIGHT).rotate(270, expand=True)
    elif orientation == 6:
        return image.rotate(270, expand=True)
    elif orientation == 7:
        return image.transpose(Image.FLIP_LEFT_RIGHT).rotate(90, expand=True)
    elif orientation == 8:
        return image.rotate(90, expand=True)

    return image  # orientation == 1, no change needed


def process_image(source_path: Path, output_path: Path) -> bool:
    """
    Process a single image: resize, correct orientation, save.

    Returns True if processed, False if skipped or error.
    """
    try:
        with Image.open(source_path) as img:
            # Convert to RGB if necessary (for PNG with transparency, etc.)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Apply EXIF orientation correction
            img = apply_exif_orientation(img)

            # Resize maintaining aspect ratio
            img.thumbnail(MAX_SIZE, Image.LANCZOS)

            # Save as JPEG with optimization
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Always save as .jpg for consistency
            output_jpg = output_path.with_suffix('.jpg')
            img.save(output_jpg, 'JPEG', quality=JPEG_QUALITY, optimize=True)

            return True

    except Exception as e:
        print(f"Error processing {source_path.name}: {e}")
        return False


def get_output_path(source_path: Path) -> Path:
    """Get the output path for a source image (always .jpg)."""
    return OUTPUT_DIR / source_path.with_suffix('.jpg').name


def needs_processing(source_path: Path) -> bool:
    """Check if image needs to be processed."""
    output_path = get_output_path(source_path)

    if not output_path.exists():
        return True

    # Re-process if source is newer than output
    return source_path.stat().st_mtime > output_path.stat().st_mtime


def process_library() -> dict:
    """
    Process all images in the library directory.

    Returns dict with counts: processed, skipped, errors
    """
    results = {'processed': 0, 'skipped': 0, 'errors': 0}

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Find all image files in library (excluding reducedlive subdirectory)
    for item in LIBRARY_DIR.iterdir():
        # Skip directories (including reducedlive)
        if item.is_dir():
            continue

        # Skip non-image files
        if item.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        # Check if processing needed
        if not needs_processing(item):
            results['skipped'] += 1
            continue

        # Process the image
        output_path = get_output_path(item)
        if process_image(item, output_path):
            results['processed'] += 1
            print(f"Processed: {item.name}")
        else:
            results['errors'] += 1

    return results


def run_on_startup():
    """
    Entry point for app startup.
    Processes library images if needed.
    """
    print("Image processor: Checking library images...")
    results = process_library()

    total = results['processed'] + results['skipped'] + results['errors']
    print(f"Image processor: {total} images checked")
    print(f"  - Processed: {results['processed']}")
    print(f"  - Skipped (already done): {results['skipped']}")
    if results['errors']:
        print(f"  - Errors: {results['errors']}")


if __name__ == "__main__":
    # Can be run directly for testing
    run_on_startup()
