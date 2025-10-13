"""
File Validator
Validates uploaded files for size, type, and content
"""

import os
import magic
from typing import Optional, List


class FileValidator:
    """Validate uploaded files"""
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'image': 10 * 1024 * 1024,      # 10 MB
        'document': 50 * 1024 * 1024,   # 50 MB
        'video': 500 * 1024 * 1024,     # 500 MB
        'default': 100 * 1024 * 1024    # 100 MB
    }
    
    # Allowed MIME types by category
    ALLOWED_TYPES = {
        'image': [
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
            'image/webp', 'image/svg+xml'
        ],
        'document': [
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain', 'text/csv'
        ],
        'video': [
            'video/mp4', 'video/mpeg', 'video/quicktime',
            'video/x-msvideo', 'video/webm'
        ],
        'audio': [
            'audio/mpeg', 'audio/wav', 'audio/webm', 'audio/ogg'
        ]
    }
    
    def __init__(self):
        pass
    
    def validate_file(
        self,
        file_content: bytes,
        file_name: str,
        allowed_categories: Optional[List[str]] = None,
        max_size: Optional[int] = None
    ) -> dict:
        """
        Validate file content and metadata
        
        Args:
            file_content: File binary content
            file_name: Original file name
            allowed_categories: List of allowed categories (image, document, video, audio)
            max_size: Maximum file size in bytes
            
        Returns:
            Dict with validation result and error message
        """
        # Check file size
        file_size = len(file_content)
        
        if max_size and file_size > max_size:
            return {
                'valid': False,
                'error': f'File size exceeds maximum allowed: {max_size} bytes'
            }
        
        # Detect MIME type from content
        try:
            mime = magic.Magic(mime=True)
            detected_mime = mime.from_buffer(file_content)
        except:
            # Fallback: guess from extension
            import mimetypes
            detected_mime, _ = mimetypes.guess_type(file_name)
            if not detected_mime:
                detected_mime = 'application/octet-stream'
        
        # Determine file category
        file_category = self._get_file_category(detected_mime)
        
        # Check if category is allowed
        if allowed_categories and file_category not in allowed_categories:
            return {
                'valid': False,
                'error': f'File type not allowed. Allowed categories: {", ".join(allowed_categories)}'
            }
        
        # Check if MIME type is in allowed list
        if file_category and not self._is_mime_allowed(detected_mime, file_category):
            return {
                'valid': False,
                'error': f'MIME type {detected_mime} not allowed for category {file_category}'
            }
        
        # Check category-specific size limits
        category_max_size = self.MAX_FILE_SIZES.get(file_category, self.MAX_FILE_SIZES['default'])
        if file_size > category_max_size:
            return {
                'valid': False,
                'error': f'File size exceeds maximum for {file_category}: {category_max_size} bytes'
            }
        
        return {
            'valid': True,
            'mime_type': detected_mime,
            'category': file_category,
            'size': file_size
        }
    
    def _get_file_category(self, mime_type: str) -> Optional[str]:
        """Determine file category from MIME type"""
        for category, types in self.ALLOWED_TYPES.items():
            if mime_type in types:
                return category
        
        # Check by prefix
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
        
        return None
    
    def _is_mime_allowed(self, mime_type: str, category: str) -> bool:
        """Check if MIME type is allowed for category"""
        allowed_types = self.ALLOWED_TYPES.get(category, [])
        return mime_type in allowed_types or mime_type.startswith(f'{category}/')
    
    def validate_image(self, file_content: bytes, file_name: str) -> dict:
        """Validate image file"""
        return self.validate_file(
            file_content, 
            file_name, 
            allowed_categories=['image'],
            max_size=self.MAX_FILE_SIZES['image']
        )
    
    def validate_document(self, file_content: bytes, file_name: str) -> dict:
        """Validate document file"""
        return self.validate_file(
            file_content,
            file_name,
            allowed_categories=['document'],
            max_size=self.MAX_FILE_SIZES['document']
        )
    
    def validate_video(self, file_content: bytes, file_name: str) -> dict:
        """Validate video file"""
        return self.validate_file(
            file_content,
            file_name,
            allowed_categories=['video'],
            max_size=self.MAX_FILE_SIZES['video']
        )
