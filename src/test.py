from services.cloudinary_service import upload_pdf

with open("temporary_docs/Attention Is All You Need.pdf", "rb") as f:
    result = upload_pdf(f.read(), "sample.pdf")

print(result)