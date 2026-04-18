import sys, os
import streamlit as st
import pandas as pd
from models.tf_idf import TfidfSearch
from preprocess import PDFPreprocessor

st.title("Document Search")

if st.button("Rebuild Dataset"):
    processor = PDFPreprocessor("temporary_docs")
    processor.run()
    st.success("Dataset rebuilt!")

st.subheader("All documents")
data = pd.read_csv("dataset.csv")
docs = [f.replace(".pdf","") for f in os.listdir("temporary_docs")]
for d in docs:
    st.write(d)
    
search_engine = TfidfSearch("dataset.csv")
query = st.text_input("Give me the context")

if st.button("Search"):
    if query:
        results = search_engine.search(query)
        
        st.subheader("Matching Documents:")
        for label,score in results.items():
            st.write(label, "->", round(score,4))