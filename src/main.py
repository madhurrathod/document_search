import os
import streamlit as st
from services.search_service import SearchService
from services.data_service import DataService
from services.document_service import process_uploaded_document
from services.db_service import get_all_documents


st.title("Document Search")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
MAX_FILE_SIZE_MB = 10
if uploaded_file is not None:
    st.write("Selected file:", uploaded_file.name)

    if st.button("Save Document"):
        try:
            doc_id = process_uploaded_document(uploaded_file)
            st.success(f"Saved successfully! Document ID: {doc_id}")
        except Exception as e:
            st.error(f"Error: {e}")




st.subheader("All documents")
docs = get_all_documents()

with st.container(height=250, border=True):
    for doc in docs:
        st.markdown(
            f"""
            <div style="padding:10px; margin-bottom:10px; border:1px solid #ccc; border-radius:10px;">
                <p style="margin:0; font-weight:600;">{doc["filename"]}</p>
                <a href="{doc["cloudinary_url"]}" target="_blank">View PDF</a>
            </div>
            """,
            unsafe_allow_html=True
        )


query = st.text_input("Give me the context")

# if st.button("Search") and query:
#     results = search_service.search(query)

#     st.subheader("Matching Documents:")
#     for label, score in results.items():
#         st.write(label, "->", round(score, 4))