# Main purpose of this file is to convert the PDF file's content that we'll upload, in the format where all the sentences of that file gets a label of name of that file.

import read
import numpy as np
import pandas as pd
import os

def cleanPage(page):
    removeSlashN = page.replace("\n", " ")
    splitSentences = removeSlashN.split(".")
    return splitSentences

folder_path = "temporary_docs"
data = []

for file in os.listdir(folder_path):
    if file.endswith(".pdf"):
        label = file.replace(".pdf","")
        doc = read.ReadDoc(os.path.join(folder_path, file))
        total_pages = doc.pageCount()
            
        for i in range(total_pages):
            page = doc.getPageContent(i)
            sentences = cleanPage(page)
            for sentence in sentences:
                data.append({"text":sentence, "label":label})

df = pd.DataFrame(data)
df.to_csv("dataset.csv", index=False)


