import io
import pdfplumber
import sys

def extract_pdf_raw(data):
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"--- PAGE {i+1} ---")
            print(page.extract_text())

if __name__ == "__main__":
    pdf_path = r"c:\Users\AMARJEET KUMAR\Desktop\Placement_Assist\Backend\uploads\resume-1773402835613-178786213.pdf"
    with open(pdf_path, "rb") as f:
        extract_pdf_raw(f.read())
