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
    def pageCount(self):
        return len(self.reader.pages)
        
        
        
        


