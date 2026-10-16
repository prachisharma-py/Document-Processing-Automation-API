from pathlib import Path

import pymupdf


def extract_text_from_pdf(file_path):
    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"PDF file not found: {file_path.name}"
        )
    
    with pymupdf.open(file_path) as pdf:
        extracted_pages = [
            page.get_text()
            for page in pdf
        ]
    return "\n".join(extracted_pages).strip()
