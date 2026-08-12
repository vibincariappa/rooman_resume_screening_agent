from pathlib import Path

def parse_txt(file_path: Path) -> str:
    """
    Parses a TXT file and returns its raw text contents.
    Raises FileNotFoundError if file does not exist.
    Raises ValueError if document is corrupted or empty.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()
    except Exception as e:
        raise ValueError(f"Failed to read TXT file: {e}")
        
    if not raw_text.strip():
        raise ValueError("Empty or unreadable TXT document.")
        
    return raw_text
