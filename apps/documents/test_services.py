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


def test_extract_text_from_pdf_raises_error_for_invalid_pdf(tmp_path):
    invalid_pdf_path = tmp_path / "invalid_document.pdf"
    invalid_pdf_path.write_bytes(b"This is not a valid PDF file.")

    with pytest.raises(pymupdf.FileDataError):
        extract_text_from_pdf(str(invalid_pdf_path))


def test_extract_text_from_pdf_returns_emptty_string_when_no_text(tmp_path):
    pdf_path = tmp_path / "empty_text.pdf"

    with pymupdf.open() as pdf:
        pdf.new_page()
        pdf.save(str(pdf_path))

    extracted_text = extract_text_from_pdf(str(pdf_path))

    assert extracted_text == ""
