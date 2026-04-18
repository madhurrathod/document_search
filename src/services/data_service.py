import os
from preprocess import PDFPreprocessor

class DataService:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        
    def rebuild(self):
        processor = PDFPreprocessor(self.folder_path)
        processor.run()
        
    def list_docs(self):
        return [f.replace(".pdf","") for f in os.listdir(self.folder_path) if f.endswith(".pdf")]