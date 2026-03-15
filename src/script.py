from pypdf import PdfReader
class ReadDoc:
    def __init__(self, url):
        self.url = url
        self.reader = PdfReader(url)
    
    def getPageContent(self, pageNo):
        try:
            pageObj = self.reader.pages[pageNo]
        except:
            print("Page not Found")
        else:
            content = pageObj.extract_text()
            return content
        
url = "temporary_docs/Attention Is All You Need.pdf"
doc1 = ReadDoc(url)
print(doc1.getPageContent(0))
        
        
        


