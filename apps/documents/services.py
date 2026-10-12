import pymupdf

def extract_text_from_pdf(file_path):
    with pymupdf.open(file_path) as pdf:
        extracted_pages = [
            page.get_text()
            for page in pdf
        ]
    return "\n".join(extracted_pages).strip()
