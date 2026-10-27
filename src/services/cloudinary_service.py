import streamlit as st
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=st.secrets["cloudinary"]["cloud_name"],
    api_key=st.secrets["cloudinary"]["api_key"],
    api_secret=st.secrets["cloudinary"]["api_secret"],
    secure=True,
)

def upload_pdf(file_bytes: bytes, public_id: str) -> dict:
    # public_id includes a content hash, so different files never collide
    # and overwrite=False can't destroy an existing document.
    result = cloudinary.uploader.upload(
        file_bytes,
        resource_type="raw",
        public_id=public_id,
        overwrite=False
    )
    return {
        "secure_url": result["secure_url"],
        "public_id": result["public_id"]
    }

def delete_pdf(public_id: str) -> bool:
    result = cloudinary.uploader.destroy(public_id, resource_type="raw")
    return result.get("result") == "ok"