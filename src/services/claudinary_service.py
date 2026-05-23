import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_pdf(file_bytes: bytes, filename: str) -> dict:
    result = cloudinary.uploader.upload(
        file_bytes,
        resource_type="raw",
        public_id=f"documents/{filename}",
        overwrite=True
    )
    return {
        "secure_url": result["secure_url"],
        "public_id": result["public_id"]
    }

def delete_pdf(public_id: str) -> bool:
    result = cloudinary.uploader.destroy(public_id, resource_type="raw")
    return result.get("result") == "ok"

