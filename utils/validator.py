import os

class FileValidator:
    ALLOWED_EXTENSIONS = {".log"}
    MAX_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB

    @staticmethod
    def _ext(filename: str) -> str:
        return os.path.splitext(filename)[1].lower()

    @classmethod
    def validate(cls, filename: str, size_bytes: int):
        ext = cls._ext(filename)
        if ext not in cls.ALLOWED_EXTENSIONS:
            return False, "Upload only valid file format (.log)"
        if size_bytes > cls.MAX_SIZE_BYTES:
            return False, f"File too large. Maximum allowed size is {cls.MAX_SIZE_BYTES} bytes"
        return True, None
