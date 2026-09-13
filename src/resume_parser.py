from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import pymupdf
from docx import Document


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def extract_text_from_pdf(file_obj: BinaryIO) -> str:
    """Extract text from a PDF file object."""
    file_obj.seek(0)

    pdf_bytes = file_obj.read()
    document = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    try:
        pages = [page.get_text("text") for page in document]
    finally:
        document.close()

    return "\n".join(pages).strip()


def extract_text_from_docx(file_obj: BinaryIO) -> str:
    """Extract text from a DOCX file object."""
    file_obj.seek(0)

    document = Document(file_obj)

    paragraphs = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs).strip()


def extract_text_from_txt(file_obj: BinaryIO) -> str:
    """Extract text from a plain text file object."""
    file_obj.seek(0)

    raw_content = file_obj.read()

    if isinstance(raw_content, bytes):
        return raw_content.decode("utf-8", errors="ignore").strip()

    return str(raw_content).strip()


def extract_resume_text(file_obj: BinaryIO, filename: str) -> str:
    """
    Extract resume text based on the uploaded file extension.

    Supported formats:
    - PDF
    - DOCX
    - TXT
    """
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(
            f"Unsupported file format '{extension}'. "
            f"Supported formats: {supported}"
        )

    if extension == ".pdf":
        text = extract_text_from_pdf(file_obj)
    elif extension == ".docx":
        text = extract_text_from_docx(file_obj)
    elif extension == ".txt":
        text = extract_text_from_txt(file_obj)
    else:
        raise ValueError(f"Unsupported file format: {extension}")

    if not text:
        raise ValueError(
            "No readable text was found in the uploaded resume. "
            "Please upload a text-based PDF, DOCX, or TXT file."
        )

    return text


def clean_extracted_text(text: str) -> str:
    """Clean common formatting problems produced during extraction."""
    if not text:
        return ""

    lines = []

    for line in text.splitlines():
        cleaned_line = " ".join(line.split())

        if cleaned_line:
            lines.append(cleaned_line)

    return "\n".join(lines).strip()


def get_resume_statistics(text: str) -> dict:
    """Return basic statistics for the extracted resume text."""
    cleaned_text = clean_extracted_text(text)

    words = cleaned_text.split()
    lines = cleaned_text.splitlines()

    return {
        "characters": len(cleaned_text),
        "words": len(words),
        "lines": len(lines),
    }