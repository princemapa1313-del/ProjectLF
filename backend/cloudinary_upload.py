"""
Lost & Finder — FastAPI Backend
cloudinary_upload.py: Helper for Cloudinary image uploads
"""
import cloudinary
import cloudinary.uploader
from config import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_SIZE_MB = 5

async def upload_image(file_bytes: bytes, content_type: str, folder: str = "lostfinder") -> dict:
    """
    Upload image bytes to Cloudinary.
    Returns dict with url, public_id, width, height.
    """
    if content_type not in ALLOWED_TYPES:
        raise ValueError(f"Invalid file type: {content_type}. Allowed: {ALLOWED_TYPES}")

    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise ValueError(f"File too large: {size_mb:.1f}MB. Max allowed: {MAX_SIZE_MB}MB")

    result = cloudinary.uploader.upload(
        file_bytes,
        folder=folder,
        resource_type="image",
        transformation=[
            {"width": 800, "height": 800, "crop": "limit"},
            {"quality": "auto:good"}
        ]
    )

    return {
        "url": result["secure_url"],
        "public_id": result["public_id"],
        "width": result.get("width"),
        "height": result.get("height")
    }

def delete_image(public_id: str) -> bool:
    """Delete image from Cloudinary by public_id."""
    result = cloudinary.uploader.destroy(public_id)
    return result.get("result") == "ok"
