import streamlit as st

from services.document_service import process_uploaded_document, backfill_missing_embeddings
from db.db_service import get_all_documents
from db.database import init_db
from services.search_service import SearchService
from services.rag_service import RagService

st.set_page_config(page_title="Document Search", page_icon="📄", layout="wide")


@st.cache_resource(show_spinner="Connecting to database...")
def setup_database():
    # Streamlit reruns this file on every click/keystroke; schema setup only
    # needs to happen once per server process.
    init_db()
    return True


try:
    setup_database()
except Exception as e:
    # Previously init_db() ran outside any try block, so an unreachable DB
    # (e.g. a Supabase free project paused after 7 days idle) crashed the
    # whole page with a traceback.
    st.error(f"Database connection failed: {e}")
    st.stop()

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

if st.button("Rebuild missing embeddings"):
    try:
        updated = backfill_missing_embeddings()
        if updated:
            st.success(f"Embedded {updated} chunk(s) that were missing vectors.")
        else:
            st.info("All chunks already have embeddings.")
    except Exception as e:
        st.error(f"Backfill error: {e}")

try:
    docs = get_all_documents()
except Exception as e:
    # The schema setup above is cached, so it won't catch the DB going
    # away later (e.g. Supabase pausing an idle project) — check here too.
    st.error(f"Database connection failed: {e}")
    st.stop()

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
                
                
st.subheader("Semantic Search")

query = st.text_input("Ask about document content")
top_k = st.slider("Number of results", min_value=1, max_value=10, value=5)

if query.strip():
    try:
        search_service = SearchService()
        results = search_service.search(query, top_k=top_k)

        if not results:
            st.info("No matching results found.")
        else:
            for result in results:
                with st.container(border=True):
                    st.write(f"**Document:** {result['filename']}")
                    st.write(f"**Page:** {result['page_number']}")
                    st.write(f"**Similarity Score:** {result['score']:.4f}")
                    st.write(result["snippet"])
                    page_url = f"{result['cloudinary_url']}#page={result['page_number']}"
                    st.link_button("View Matched Page", page_url)
    except Exception as e:
        st.error(f"Search error: {e}")
        
        
st.subheader("Questions about document")

test_query = st.text_input("insert your query")

if st.button("Enter"):
    if not test_query.strip():
        st.warning("Type a question first.")
    else:
        try:
            rag_service = RagService()
            response = rag_service.answer_query(test_query)

            st.write("### Answer")
            st.write(response["answer"])

            # Show where the answer came from, so it can be checked.
            if response["sources"]:
                st.write("**Sources**")
                for source in response["sources"]:
                    page_url = f"{source['cloudinary_url']}#page={source['page_number']}"
                    st.markdown(
                        f"- [{source['filename']}, page {source['page_number']}]({page_url})"
                        f" (similarity {source['score']:.2f})"
                    )

        except Exception as e:
            st.error(f"RAG error: {e}")
