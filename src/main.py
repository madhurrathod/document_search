import sys
import streamlit as st
import pandas as pd
from models.tf_idf import TfidfSearch
from preprocess import PDFPreprocessor

st.title("Document Search")

if "--rebuild" in sys.argv:
    processor = PDFPreprocessor("temporary_docs")
    processor.run()
    print("Dataset rebuilt!")

search_engine = TfidfSearch("dataset.csv")
print(search_engine.search("human interaction with llm"))