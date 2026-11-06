import pymupdf

def extract_text_from_pdf(file_object):
    with pymupdf.open(
        stream=file_object.read(),
        filetype="pdf",
    ) as pdf:
        extracted_pages = [
            page.get_text()
            for page in pdf
        ]

    return "\n".join(extracted_pages).strip()
