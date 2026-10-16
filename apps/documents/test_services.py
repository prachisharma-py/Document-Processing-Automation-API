import pymupdf

import pytest

from apps.documents.services import extract_text_from_pdf


def test_extract_text_from_pdf(tmp_path):
    pdf_path = tmp_path / "test_document.pdf"

    with pymupdf.open() as pdf:
        page = pdf.new_page()
        page.insert_text((72, 72), "Document Processing API Test")
        pdf.save(str(pdf_path))

    extracted_text = extract_text_from_pdf(str(pdf_path))

    assert extracted_text == "Document Processing API Test"


def test_extract_text_fron_pdf_raises_error_when_file_missing(tmp_path):
    missing_pdf_path = tmp_path / "missing_document.pdf"

    with pytest.raises(FileNotFoundError, match="missing_document.pdf"):
        extract_text_from_pdf(str(missing_pdf_path))
