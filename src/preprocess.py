# Main purpose of this file is to convert the PDF file's content that we'll upload, in the format where all the sentences of that file gets a label of name of that file.

import read

doc1 = read.ReadDoc("temporary_docs/Attention Is All You Need.pdf")
size = doc1.pageCount()
onePage = doc1.getPageContent(0)
onePageSplit = onePage.split(".")
print(onePageSplit)


