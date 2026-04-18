from models.tf_idf import TfidfSearch

search_engine = TfidfSearch("dataset.csv")
print(search_engine.search("attention mechanism"))