from models.tf_idf import TfidfSearch
from preprocess import PDFPreprocessor

processor = PDFPreprocessor("temporary_docs")
processor.run()

search_engine = TfidfSearch("dataset.csv")
print(search_engine.search("attention mechanism"))