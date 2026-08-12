from pathlib import Path
import re
from app.models.schemas import ResumeDocument
from app.parsers.pdf_parser import parse_pdf
from app.parsers.docx_parser import parse_docx
from app.parsers.txt_parser import parse_txt

def normalize_text(text: str) -> str:
    """
    Normalizes whitespace and removes obvious repeated blank lines.
    Preserves structural paragraphs by converting multi-line breaks to double newlines.
    """
    # Replace CRLF/CR with LF
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    
    # Strip spaces from lines
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)
    
    # Replace 3 or more consecutive newlines with 2 newlines (double newlines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def parse_document(file_path: Path) -> ResumeDocument:
    """
    Parses document from file path, extracts text based on extension,
    normalizes the whitespace/newlines, and returns a ResumeDocument.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    suffix = file_path.suffix.lower()
    
    if suffix == ".pdf":
        raw_text = parse_pdf(file_path)
        file_type = "pdf"
    elif suffix == ".docx":
        raw_text = parse_docx(file_path)
        file_type = "docx"
    elif suffix in [".txt", ".md"]:
        raw_text = parse_txt(file_path)
        file_type = "txt"
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
        
    normalized = normalize_text(raw_text)
    
    return ResumeDocument(
        filename=file_path.name,
        file_type=file_type,
        raw_text=raw_text,
        normalized_text=normalized,
        character_count=len(normalized),
        word_count=len(normalized.split())
    )

__all__ = ["parse_pdf", "parse_docx", "parse_txt", "normalize_text", "parse_document"]
