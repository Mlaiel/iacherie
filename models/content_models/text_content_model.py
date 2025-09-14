"""📝 Text Content Model - Enterprise Text Content Management"""
from typing import Dict, Any
from datetime import datetime
from enum import Enum

class TextFormat(Enum):
    PLAIN = "plain"
    MARKDOWN = "markdown"
    HTML = "html"

class TextContent:
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id")
        self.title = data.get("title")
        self.content = data.get("content", "")
        self.format = data.get("format", TextFormat.PLAIN.value)
        self.word_count = len(self.content.split())
        self.created_at = datetime.utcnow()

class TextContentModel:
    @staticmethod
    def create_content(content_data: Dict[str, Any]) -> TextContent:
        return TextContent(content_data)
    
    @staticmethod
    def process(content: TextContent) -> Dict[str, Any]:
        return {"processed": True, "content_id": content.id}
