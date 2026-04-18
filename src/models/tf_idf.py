import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

data = pd.read_csv("dataset.csv")
data['text'] = data['text'].fillna("").astype(str)
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data['text'])

def search(query, top_k=3):
    q = vectorizer.transform([query])
    sims = cosine_similarity(q, X)[0]

    temp = data.copy()
    temp['score'] = sims

    top_docs = (
        temp.groupby('label')['score']
        .max()
        .sort_values(ascending=False)
        .head(top_k)
    )

    return top_docs

print(search("attention mechanism in transformers"))