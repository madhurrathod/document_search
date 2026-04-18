# Main purpose of this file is to convert the PDF file's content that we'll upload, in the format where all the sentences of that file gets a label of name of that file.

import read
import pandas as pd
import os

class PDFPreprocessor:
    def __init__(self, folder_path, output_csv="dataset.csv"):
        self.folder_path = folder_path
        self.output_csv = output_csv
        self.data = []
    
    def clean_page(self, page):
        page = page.replace("\n", " ")
        sentences = page.split(".")
        return sentences 
    
    def process_file(self, file_path, label):
        doc = read.ReadDoc(file_path)
        total_pages = doc.pageCount()

        for i in range(total_pages):
            page = doc.getPageContent(i)
            sentences = self.clean_page(page)

            for sentence in sentences:
                self.data.append({
                    "text": sentence,
                    "label": label
                })

    def process_all(self):
        for file in os.listdir(self.folder_path):
            if file.endswith(".pdf"):
                label = file.replace(".pdf", "")
                file_path = os.path.join(self.folder_path, file)

                self.process_file(file_path, label)
    
    def save(self):
        df = pd.DataFrame(self.data)
        df.to_csv(self.output_csv, index=False)
        print(f"Saved {len(df)} rows to {self.output_csv}")

    def run(self):
        self.process_all()
        self.save()


