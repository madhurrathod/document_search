# Main purpose of this file is to convert the PDF file's content that we'll upload, in the format where all the sentences of that file gets a label of name of that file.

import read
import numpy as np

doc = read.ReadDoc("temporary_docs/Attention Is All You Need.pdf")
size = doc.pageCount()

# wholeArr = np.array([])
Page = doc.getPageContent(0)
removeSlashN = Page.replace("\n", " ")
splitSentences = removeSlashN.split(".")
# nparr = np.array(splitSentences)
# print(nparr)


doc_label = "Attention Is All You Need"
import pandas as pd
df = pd.DataFrame(splitSentences)
label = pd.array(data = doc_label,dtype="string" )

