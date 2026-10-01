from agentic_career_lab.services.resume_parser import ResumeParser


def test_parse_txt_file():
    parser = ResumeParser()
    content = b"This is a test resume."
    parsed = parser.parse_uploaded_file(content, "test.txt")
    assert parsed.text == "This is a test resume."
    assert parsed.file_type == "txt"
    assert parsed.character_count == len("This is a test resume.")
    assert len(parsed.extraction_warnings) == 0


def test_parse_empty_txt():
    parser = ResumeParser()
    content = b"   "
    parsed = parser.parse_uploaded_file(content, "test.txt")
    assert parsed.text == ""
    assert "Extracted text is empty." in parsed.extraction_warnings


def test_parse_unsupported():
    parser = ResumeParser()
    content = b"some content"
    parsed = parser.parse_uploaded_file(content, "test.exe")
    assert "Unsupported file type." in parsed.extraction_warnings
    assert parsed.file_type == "exe"


# We won't test complex binary PDF/DOCX structures here as we mock or skip them typically,
# but we know pypdf/docx works because it's standard library.
