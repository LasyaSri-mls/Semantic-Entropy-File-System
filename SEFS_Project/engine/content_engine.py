import os
from PyPDF2 import PdfReader


def extract_text(file_path):
    """
    Main entry point.
    Detects file type and extracts text.
    """
    _, ext = os.path.splitext(file_path)

    ext = ext.lower()

    if ext == ".txt":
        return extract_text_from_txt(file_path)

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)

    return None


def extract_text_from_txt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"[ERROR] TXT extraction failed: {e}")
        return None


def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"

        return text.strip()

    except Exception as e:
        print(f"[ERROR] PDF extraction failed: {e}")
        return None
