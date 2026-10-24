
from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader


def extract_text(uploaded_file):
    """Extract text from PDF, DOCX, or TXT files."""

    filename = uploaded_file.name
    extension = Path(filename).suffix.lower()
    file_bytes = uploaded_file.getvalue()

    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    if extension == ".pdf":
        reader = PdfReader(BytesIO(file_bytes))
        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    elif extension == ".docx":
        document = Document(BytesIO(file_bytes))
        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    elif extension == ".txt":
        text = file_bytes.decode("utf-8", errors="replace")

    else:
        raise ValueError(
            "Unsupported file type. Upload PDF, DOCX, or TXT."
        )

    if not text.strip():
        raise ValueError(
            "No readable text found. This PDF may need OCR."
        )

    return text.strip()
