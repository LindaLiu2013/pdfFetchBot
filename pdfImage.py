import pytesseract
from pathlib import Path
from pdf2image import convert_from_path
from PyPDF2 import PdfMerger, PdfWriter

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

try:
    pages = convert_from_path(".\\doc\\HeadLease01_22005.pdf",  fmt='jpeg',poppler_path= r'.\\poppler-24.07.0\\Library\\bin')
    print(enumerate(pages))

    i = 0
    for page in enumerate(pages):
        print(page)
        pdf = pytesseract.image_to_pdf_or_hocr(page[1],lang='eng', extension='pdf')
             
        with open(f'.\\output\\test_{i}.pdf', 'a+b') as the_file:
            the_file.write(pdf)
            the_file.flush()
        
        i+=1
    
    writer = PdfMerger()
    reports_dir = Path("output")

    for path in reports_dir.glob("*.pdf"):
        writer.append(path)

    writer.write("merged-pdf.pdf")
    writer.close()
   
except Exception as e:
    print(e)