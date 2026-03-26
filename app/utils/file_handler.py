import os
import uuid

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_file(file_bytes:bytes,file_name:str):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return file_id, file_path