"""Security Constants - Infrastructure Security Modules
Author: Fahed Mlaiel (mlaiel@live.de)
"""

from enum import Enum

class MediaType(Enum):
    """Supported media types for security validation."""
    AUDIO = "audio"
    VIDEO = "video" 
    IMAGE = "image"
    TEXT = "text"

def get_media_type_by_extension(extension: str) -> MediaType:
    """Get media type based on file extension."""
    ext = extension.lower().lstrip('.')
    
    if ext in ['mp3', 'wav', 'flac', 'aac', 'ogg']:
        return MediaType.AUDIO
    elif ext in ['mp4', 'avi', 'mkv', 'mov', 'wmv']:
        return MediaType.VIDEO
    elif ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
        return MediaType.IMAGE
    else:
        return MediaType.TEXT

SECURITY_SETTINGS = {
    'max_file_size': 100 * 1024 * 1024,  # 100MB
    'allowed_extensions': [
        'mp3', 'wav', 'flac', 'aac', 'ogg',
        'mp4', 'avi', 'mkv', 'mov', 'wmv',
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',
        'txt', 'md', 'json', 'xml'
    ],
    'scan_timeout': 30,
    'encryption_key_length': 256
}