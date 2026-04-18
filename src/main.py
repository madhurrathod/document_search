import sys
from models.tf_idf import TfidfSearch
from preprocess import PDFPreprocessor

if "--rebuild" in sys.argv:
    processor = PDFPreprocessor("temporary_docs")
    processor.run()
    print("Dataset rebuilt!")

search_engine = TfidfSearch("dataset.csv")
print(search_engine.search("human interaction with llm"))