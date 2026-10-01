import io

from docx import Document
from pydantic import BaseModel
from pypdf import PdfReader


class ParsedResume(BaseModel):
    text: str
    file_name: str
    file_type: str
    character_count: int
    extraction_warnings: list[str]


class ResumeParser:
    def parse_uploaded_file(self, file_content: bytes, file_name: str) -> ParsedResume:
        warnings = []
        text = ""
        ext = file_name.lower().split(".")[-1]

        if ext == "pdf":
            try:
                reader = PdfReader(io.BytesIO(file_content))
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            except Exception as e:
                warnings.append(f"Failed to read PDF: {e}")

        elif ext == "docx":
            try:
                doc = Document(io.BytesIO(file_content))
                text = "\n".join([para.text for para in doc.paragraphs])
            except Exception as e:
                warnings.append(f"Failed to read DOCX: {e}")

        elif ext == "txt":
            try:
                text = file_content.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    text = file_content.decode("latin-1")
                    warnings.append("Decoded as latin-1, some characters may be wrong.")
                except Exception as e:
                    warnings.append(f"Failed to decode TXT: {e}")
        else:
            warnings.append("Unsupported file type.")

        text = text.strip()
        if not text and not warnings:
            if ext == "pdf":
                warnings.append(
                    "This PDF does not contain readable text. Try uploading a text-based PDF, DOCX, or paste the resume text."
                )
            else:
                warnings.append("Extracted text is empty.")

        return ParsedResume(
            text=text,
            file_name=file_name,
            file_type=ext,
            character_count=len(text),
            extraction_warnings=warnings,
        )
