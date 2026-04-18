import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TfidfSearch:
    def __init__(self, csv_path):
        self.data = pd.read_csv(csv_path)
        self.data["text"] = self.data["text"].fillna("").astype(str)
        
        self.vectorizer = TfidfVectorizer()
        self.X = self.vectorizer.fit_transform(self.data["text"])
    
    def search(self, query, top_k =3):
        q = self.vectorizer.transform([query])
        sims = cosine_similarity(q,self.X)[0]
        
        temp = self.data.copy()
        temp["score"] = sims
        
        top_docs = (
            temp.groupby("label")["score"]
            .max()
            .sort_values(ascending=False)
            .head(top_k)
        )
        return top_docs
        