"""Utility functions for file validation and mime guessing."""

import mimetypes
from typing import Tuple

ALLOWED_MIME = {
    "audio/mpeg": "audio",
    "audio/wav": "audio",
    "image/jpeg": "image",
    "image/png": "image",
    "video/mp4": "video",
    "text/plain": "text",
    "application/pdf": "text",
}


def guess_media_type(filename: str) -> Tuple[str, str]:
    mime, _ = mimetypes.guess_type(filename)
    media_type = ALLOWED_MIME.get(mime or "", "text")
    return media_type, mime or "application/octet-stream"
