import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from pypdf import PdfReader

# Windows Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    First tries normal PDF text extraction.
    If the PDF is scanned/image-based, it falls back to local OCR using Tesseract.
    """
    text = ""

    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"PDF text extraction failed, falling back to OCR: {e}")

    if len(text.strip()) > 50:
        print("Text-based PDF detected. OCR fallback not required.")
        return text

    print("Scanned PDF detected. Converting pages to images...")
    pages = convert_from_path(pdf_path, dpi=300)

    for i, page in enumerate(pages):
        print(f"OCR running locally on page {i + 1} using ben+eng...")
        page_text = pytesseract.image_to_string(page, lang="ben+eng")
        text += page_text + "\n"

    return text


def extract_text(file_path: str) -> str:
    """
    Extract text from PDF or image file.
    Supported image types: jpg, jpeg, png, bmp, tiff.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)

    print("Image file detected. Running local OCR...")
    image = Image.open(file_path)
    return pytesseract.image_to_string(image, lang="ben+eng")
