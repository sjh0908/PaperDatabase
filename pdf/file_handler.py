import hashlib
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename

def compute_file_sha256(file_path): #FILEPATH -> hash

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:

        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()

def get_file_extension(filename):
    suffix = Path(filename).suffix.lower()

    if suffix.startswith("."):
        return suffix[1:]

    return ""

def generate_unique_filename(filename):
    ext = get_file_extension(filename)

    if ext == "":
        raise ValueError("文件缺少扩展名")

    return f"{uuid.uuid4()}.{ext}"

def sanitize_filename(filename):
    safe_name = secure_filename(filename)

    if safe_name == "":
        return "uploaded_file"

    return safe_name