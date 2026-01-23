"""
The 55 App - QR Code Router

Generates QR codes for team join URLs.
"""

import io
import qrcode

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse

from app.dependencies import AuthDep, DbDep
from app.db.models import Team

router = APIRouter(prefix="/admin/qr", tags=["qr"])


def get_base_url(request: Request) -> str:
    """Get base URL from request, handling proxies."""
    # Check for forwarded proto (behind nginx/proxy)
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host", request.url.netloc)
    return f"{proto}://{host}"


@router.get("/team/{team_id}")
async def generate_qr(
    request: Request,
    team_id: int,
    auth: AuthDep,
    db: DbDep
):
    """Generate QR code PNG for team join URL (500x500 pixels)."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Build join URL
    base_url = get_base_url(request)
    join_url = f"{base_url}/join?code={team.code}"

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(join_url)
    qr.make(fit=True)

    # Create image and resize to exactly 500x500
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((500, 500))

    # Return as PNG
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": f"inline; filename=qr-{team.code}.png",
            "Cache-Control": "max-age=3600"  # Cache for 1 hour
        }
    )


@router.get("/team/{team_id}/download")
async def download_qr(
    request: Request,
    team_id: int,
    auth: AuthDep,
    db: DbDep
):
    """Download QR code PNG for team join URL."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Build join URL
    base_url = get_base_url(request)
    join_url = f"{base_url}/join?code={team.code}"

    # Generate QR code - larger for printing
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for printing
        box_size=15,  # Larger for print
        border=4,
    )
    qr.add_data(join_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename=the55-qr-{team.code}.png"
        }
    )
