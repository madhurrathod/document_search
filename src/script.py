from pypdf import PdfReader
class ReadDoc:
    def __init__(self, url):
        self.url = url
        try:
            self.reader = PdfReader(url)
        except:
            print("Incorrect URL")
    
    def getPageContent(self, pageNo):
        try:
            pageObj = self.reader.pages[pageNo]
        except:
            return "Page Not Found"
        else:
            content = pageObj.extract_text()
            return content
        
url = "temporary_docs/Attention Is Allou Need.pdf"
doc1 = ReadDoc(url)
print(doc1.getPageContent(100))
        
        
        


