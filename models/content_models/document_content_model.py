"""📄 Document Content Model - Enterprise Document Management"""
from typing import Dict, Any
from datetime import datetime
from enum import Enum

class DocumentFormat(Enum):
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"

class DocumentContent:
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id")
        self.title = data.get("title")
        self.format = data.get("format", DocumentFormat.PDF.value)
        self.created_at = datetime.utcnow()

class DocumentContentModel:
    @staticmethod
    def create_content(content_data: Dict[str, Any]) -> DocumentContent:
        return DocumentContent(content_data)
