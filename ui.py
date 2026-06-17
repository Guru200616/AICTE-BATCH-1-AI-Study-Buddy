"""File ingestion & text chunking utilities."""
from io import BytesIO
from typing import List

from pypdf import PdfReader

from config import CHUNK_SIZE_CHARS


def extract_text_from_upload(uploaded_file) -> str:
    """Extracts plain text from an uploaded .txt or .pdf file."""
    name = uploaded_file.name.lower()
    data = uploaded_file.read()

    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        reader = PdfReader(BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages)
        if not text.strip():
            raise ValueError(
                "Couldn't extract text from this PDF — it may be a scanned "
                "image without selectable text. Try pasting the text instead."
            )
        return text

    raise ValueError("Unsupported file type. Please upload a .txt or .pdf file.")


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE_CHARS) -> List[str]:
    """Splits text into chunks on paragraph boundaries, each close to chunk_size."""
    paragraphs = text.split("\n\n")
    chunks: List[str] = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current += para + "\n\n"
        else:
            if current.strip():
                chunks.append(current.strip())
            current = para + "\n\n"

    if current.strip():
        chunks.append(current.strip())

    return chunks or [text]
