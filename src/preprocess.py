# Main purpose of this file is to convert the PDF file's content that we'll upload, in the format where all the sentences of that file gets a label of name of that file.

import read
import numpy as np
import pandas as pd

doc = read.ReadDoc("temporary_docs/Attention Is All You Need.pdf")
total_pages = doc.pageCount()

def cleanPage(page):
    removeSlashN = page.replace("\n", " ")
    splitSentences = removeSlashN.split(".")
    return splitSentences

All_sentences = []
for i in range(total_pages):
    page = doc.getPageContent(i)
    sentences = cleanPage(page)
    All_sentences = All_sentences + sentences

print(len(All_sentences))
    


