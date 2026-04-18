import os
import streamlit as st
from services.search_service import SearchService
from services.data_service import DataService


st.title("Document Search")

data_service = DataService("temporary_docs") 
search_service = SearchService("dataset.csv")

if not os.path.exists("dataset.csv"):
    data_service.rebuild()
    
if st.button("Rebuild Dataset"):
    data_service.rebuild()
    st.success("Dataset rebuilt!")

st.subheader("All documents")
docs = data_service.list_docs()

# box for scrolling documents
box = '<div style="height:200px; overflow-y:auto; border:1px solid #ccc; padding:10px; border-radius:10px">'
for d in docs:
    box += f'<p style="padding:5px 10px 5px 10px;border:1px solid #ccc; border-radius:10px">{d}</p>'
box += "</div>"

st.markdown(box, unsafe_allow_html=True)

query = st.text_input("Give me the context")

if st.button("Search") and query:
        results = search_service.search(query)
        
        st.subheader("Matching Documents:")
        for label, score in results.items():
            st.write(label, "->", round(score,4))