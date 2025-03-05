import pymupdf as fitz  # For PDFs
from docx import Document  # For DOCX

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file and return it as a string."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def extract_text_from_doc(doc_path):
    """Extract text from a DOCX file and return it as a string."""
    try:
        doc = Document(doc_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return None

# Example usage:
pdf_text = extract_text_from_pdf("C:/Users/aitha/Downloads/RFP Football Club Website and App.pdf")
# doc_text = extract_text_from_doc("C:/Users/aitha/Downloads/RFP Football Club Website and App.pdf")

print("Extracted PDF Text:\n", pdf_text)
# print("\nExtracted DOCX Text:\n", doc_text)