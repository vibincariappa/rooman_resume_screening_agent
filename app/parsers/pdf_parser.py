import fitz  # PyMuPDF
from pathlib import Path

def parse_pdf(file_path: Path) -> str:
    """
    Parses a PDF file and returns its raw text contents.
    Raises FileNotFoundError if file does not exist.
    Raises ValueError if document is corrupted or empty.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise ValueError(f"Corrupted or invalid PDF file: {e}")
        
    try:
        text_parts = []
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text_parts.append(page_text)
        
        raw_text = "\n".join(text_parts)
    finally:
        doc.close()
        
    if not raw_text.strip():
        raise ValueError("Empty or unreadable PDF document.")
        
    return raw_text
