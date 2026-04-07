import os
import uuid

UPLOAD_DIR = "uploads"


def save_file(file_bytes: bytes, file_name: str):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_id = str(uuid.uuid4())
    extension = os.path.splitext(file_name)[1]
    file_path = os.path.join(UPLOAD_DIR, file_id + extension)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return file_path, file_id
