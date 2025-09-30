"""
🔒 Content Moderation Microservice
AI-powered content moderation and safety service

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import asyncio
import uuid
import logging

logger = logging.getLogger(__name__)


class ModerationStatus(str, Enum):
    """Content moderation status"""
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    FLAGGED = "flagged"
    REVIEW_REQUIRED = "review_required"


class ContentType(str, Enum):
    """Content type for moderation"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    LINK = "link"


class ModerationResult(BaseModel):
    """Moderation result structure"""
    content_id: str
    status: ModerationStatus
    confidence_score: float = Field(ge=0.0, le=1.0)
    flags: List[str] = Field(default_factory=list)
    reasons: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reviewer_id: Optional[str] = None


class ContentModerationService:
    """Main Content Moderation Service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.moderation_history: Dict[str, ModerationResult] = {}
        self.logger.info("✅ ContentModerationService initialized")
    
    async def moderate_content(
        self, 
        content_id: str, 
        content_type: ContentType,
        content_data: Union[str, bytes],
        metadata: Optional[Dict[str, Any]] = None
    ) -> ModerationResult:
        """Moderate content and return result"""
        
        try:
            # Simulate AI moderation analysis
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Simple content analysis (in production, use real AI models)
            flags = []
            reasons = []
            confidence = 0.95
            
            if content_type == ContentType.TEXT:
                text_content = content_data if isinstance(content_data, str) else content_data.decode('utf-8')
                
                # Check for inappropriate content
                inappropriate_words = ['spam', 'hate', 'violence', 'inappropriate']
                text_lower = text_content.lower()
                
                for word in inappropriate_words:
                    if word in text_lower:
                        flags.append(f"inappropriate_language_{word}")
                        reasons.append(f"Contains inappropriate content: {word}")
            
            # Determine status based on flags
            if not flags:
                status = ModerationStatus.APPROVED
            elif len(flags) <= 2:
                status = ModerationStatus.FLAGGED
            else:
                status = ModerationStatus.REJECTED
                confidence = 0.99
            
            result = ModerationResult(
                content_id=content_id,
                status=status,
                confidence_score=confidence,
                flags=flags,
                reasons=reasons
            )
            
            # Store result
            self.moderation_history[content_id] = result
            
            self.logger.info(f"Moderated content {content_id}: {status}")
            return result
            
        except Exception as e:
            self.logger.error(f"Moderation failed for {content_id}: {str(e)}")
            
            # Return safe default
            return ModerationResult(
                content_id=content_id,
                status=ModerationStatus.REVIEW_REQUIRED,
                confidence_score=0.5,
                flags=["moderation_error"],
                reasons=[f"Moderation service error: {str(e)}"]
            )
    
    async def get_moderation_result(self, content_id: str) -> Optional[ModerationResult]:
        """Get previous moderation result"""
        return self.moderation_history.get(content_id)
    
    async def bulk_moderate(self, content_items: List[Dict[str, Any]]) -> List[ModerationResult]:
        """Moderate multiple content items"""
        results = []
        
        for item in content_items:
            result = await self.moderate_content(
                content_id=item.get('content_id'),
                content_type=ContentType(item.get('content_type', 'text')),
                content_data=item.get('content_data', ''),
                metadata=item.get('metadata', {})
            )
            results.append(result)
        
        return results
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "ContentModerationService",
            "status": "healthy",
            "total_moderated": len(self.moderation_history),
            "timestamp": datetime.utcnow().isoformat()
        }


__all__ = ['ContentModerationService', 'ModerationStatus', 'ContentType', 'ModerationResult']