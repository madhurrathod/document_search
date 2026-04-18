from models.tf_idf import TfidfSearch

class SearchService:
    def __init__(self,csv_path):
        self.search_engine = TfidfSearch(csv_path)
    
    def search(self,query):
        return self.search_engine.search(query)