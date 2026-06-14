from app.services.export_service import build_docx

# .docx files are zip archives, which start with the bytes "PK".
_ZIP_MAGIC = b"PK"


def test_build_docx_returns_valid_document():
    data = build_docx(
        title="Marketing Plan",
        content="## Strategy\n- point one\n- point two\n**Bold** statement.",
        subtitle="GreenBean",
    )

    assert isinstance(data, bytes)
    assert len(data) > 1000
    assert data[:2] == _ZIP_MAGIC


def test_build_docx_handles_empty_content():
    data = build_docx(title="Empty", content="")
    assert data[:2] == _ZIP_MAGIC
