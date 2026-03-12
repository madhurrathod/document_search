from pypdf import PdfReader

reader = PdfReader("temporary_docs/Attention Is All You Need.pdf")

number_of_pages = len(reader.pages)
pageObj = reader.pages[0]

content = pageObj.extract_text()
print(number_of_pages)
print(content)





