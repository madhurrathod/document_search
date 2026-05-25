import streamlit as st

from services.document_service import process_uploaded_document
from db.db_service import get_all_documents

st.set_page_config(page_title="Document Search", page_icon="📄", layout="wide")

st.title("Document Search")

MAX_FILE_SIZE_MB = 10

with st.form("upload_form", clear_on_submit=False):
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    submitted = st.form_submit_button("Save Document")

if submitted:
    if uploaded_file is None:
        st.warning("Please upload a PDF first.")
    else:
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)

        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error(f"File is too large. Max allowed size is {MAX_FILE_SIZE_MB} MB.")
        else:
            try:
                doc_id = process_uploaded_document(uploaded_file)
                st.success(f"Saved successfully! Document ID: {doc_id}")
            except Exception as e:
                st.error(f"Error: {e}")

st.subheader("All documents")
docs = get_all_documents()

if not docs:
    st.info("No documents uploaded yet.")
else:
    with st.container(height=320, border=True):
        for doc in docs:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{doc['filename']}**")
            with col2:
                st.link_button("View PDF", doc["cloudinary_url"])