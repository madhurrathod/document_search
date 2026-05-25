import streamlit as st
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=st.secrets["cloudinary"]["cloud_name"],
    api_key=st.secrets["cloudinary"]["api_key"],
    api_secret=st.secrets["cloudinary"]["api_secret"],
    secure=True,
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