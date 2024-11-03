from io import BytesIO, StringIO
from pathlib import Path

from fastapi import UploadFile

UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

def upload_file(filename: str, file: UploadFile):
    filepath = UPLOAD_DIRECTORY / f"{filename}.pdf"

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    return f"{filepath}"

def load_file(filepath: str) -> BytesIO:

    file_io = BytesIO()
    with open(filepath, "rb") as f:
        file_io.write(f.read())

    return file_io

