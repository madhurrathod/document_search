# Main purpose of this file is to convert the PDF file's content that we'll upload, in the format where all the sentences of that file gets a label of name of that file.

import script

doc1 = script.ReadDoc("temporary_docs/Attention Is All You Need.pdf")
print(doc1.getPageContent(9))
