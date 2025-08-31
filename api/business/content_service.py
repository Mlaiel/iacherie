"""Content business service for IA Influencer Agent platform.

This service handles all content-related business logic including upload,
processing, protection, and distribution for multi-format content.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""
import uuid
import os
import shutil
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import logging
import asyncio

from ..core.config import get_settings
from ..core.database import get_db
from ..models.content import Content, ContentCreate, ContentUpdate, ContentMetadata
from ..models.user import User
from ..utils.file_handler import FileHandler
from ..utils.content_validator import ContentValidator
from ..utils.thumbnail_generator import ThumbnailGenerator
from ..services.analytics import AnalyticsService

logger = logging.getLogger(__name__)
settings = get_settings()

class ContentService:
    """    Comprehensive content management service for multi-format content creators.
    
    Handles: Audio, Video, Images, Text, Documents
    Features: Upload, Processing, Protection, Analytics, Distribution
    """    
    def __init__(self):
        self.file_handler = FileHandler()
        self.content_validator = ContentValidator()
        self.thumbnail_generator = ThumbnailGenerator()
        self.analytics = AnalyticsService()
    
    async def create_content(self, content_data: ContentCreate, db: Session = None) -> Content:
        """        Create new content entry with comprehensive metadata.
        
        Args:
            content_data: Content creation data
            db: Database session
            
        Returns:
            Created content instance
        """        try:
            if not db:
                db = next(get_db())
            
            # Validate content data
            validation_result = await self.content_validator.validate_content_create(content_data)
            if not validation_result.is_valid:
                raise ValueError(f"Invalid content data: {validation_result.errors}")
            
            # Create content instance
            content = Content(
                id=uuid.uuid4(),
                title=content_data.title,
                description=content_data.description,
                file_path=content_data.file_path,
                file_type=content_data.file_type,
                file_size=content_data.file_size,
                original_filename=content_data.original_filename,
                category=content_data.category,
                privacy_level=content_data.privacy_level,
                enable_collaboration=content_data.enable_collaboration,
                tags=content_data.tags,
                metadata=content_data.metadata,
                owner_id=content_data.owner_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                ai_processing_status="pending",
                protection_status="pending",
                view_count=0,
                like_count=0,
                download_count=0,
                is_active=True
            )
            
            # Generate content hash for integrity
            content.content_hash = await self.file_handler.calculate_file_hash(content_data.file_path)
            
            # Save to database
            db.add(content)
            db.commit()
            db.refresh(content)
            
            # Start background tasks
            asyncio.create_task(self._post_creation_tasks(str(content.id)))
            
            logger.info(f"Content created: {content.id} by owner {content.owner_id}")
            return content
            
        except Exception as e:
            logger.error(f"Content creation error: {str(e)}")
            if db:
                db.rollback()
            raise
    
    async def get_content_by_id(self, content_id: str, db: Session = None) -> Optional[Content]:
        """Get content by ID with owner information"""        try:
            if not db:
                db = next(get_db())
            
            return db.query(Content).filter(
                and_(Content.id == content_id, Content.is_active == True)
            ).first()
            
        except Exception as e:
            logger.error(f"Get content by ID error: {str(e)}")
            return None
    
    async def get_user_content(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 50,
        category: Optional[str] = None,
        file_type: Optional[str] = None,
        db: Session = None
    ) -> List[Content]:
        """        Get user's content with filtering and pagination.
        """        try:
            if not db:
                db = next(get_db())
            
            query = db.query(Content).filter(
                and_(Content.owner_id == user_id, Content.is_active == True)
            )
            
            # Apply filters
            if category:
                query = query.filter(Content.category == category)
            if file_type:
                query = query.filter(Content.file_type == file_type)
            
            # Order by creation date (newest first)
            query = query.order_by(desc(Content.created_at))
            
            return query.offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Get user content error: {str(e)}")
            return []
    
    async def update_content(self, content_id: str, content_update: ContentUpdate, db: Session = None) -> Optional[Content]:
        """        Update content metadata and settings.
        """        try:
            if not db:
                db = next(get_db())
            
            content = db.query(Content).filter(Content.id == content_id).first()
            if not content:
                return None
            
            # Apply updates
            update_data = content_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(content, field):
                    setattr(content, field, value)
            
            content.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(content)
            
            logger.info(f"Content updated: {content_id}")
            return content
            
        except Exception as e:
            logger.error(f"Content update error: {str(e)}")
            if db:
                db.rollback()
            raise
    
    async def delete_content(self, content_id: str, db: Session = None) -> bool:
        """        Soft delete content and cleanup associated files.
        """        try:
            if not db:
                db = next(get_db())
            
            content = db.query(Content).filter(Content.id == content_id).first()
            if not content:
                return False
            
            # Soft delete
            content.is_active = False
            content.deleted_at = datetime.utcnow()
            
            # Schedule file cleanup (background task)
            asyncio.create_task(self._cleanup_content_files(str(content.id), content.file_path))
            
            db.commit()
            
            logger.info(f"Content deleted: {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Content deletion error: {str(e)}")
            if db:
                db.rollback()
            return False
    
    async def check_content_access(self, content: Content, user: Optional[User]) -> bool:
        """        Check if user has access to content based on privacy settings.
        """        try:
            # Public content is accessible to everyone
            if content.privacy_level == "public":
                return True
            
            # Private content requires authentication and ownership
            if content.privacy_level == "private":
                return user is not None and str(user.id) == str(content.owner_id)
            
            # Unlisted content is accessible with direct link
            if content.privacy_level == "unlisted":
                return True
            
            # Collaboration content requires collaboration membership
            if content.privacy_level == "collaboration":
                if not user:
                    return False
                # Check if user is in collaboration (implement this based on collaboration model)
                return await self._check_collaboration_access(str(content.id), str(user.id))
            
            return False
            
        except Exception as e:
            logger.error(f"Content access check error: {str(e)}")
            return False
    
    async def increment_view_count(self, content_id: str, db: Session = None) -> None:
        """Increment content view count"""        try:
            if not db:
                db = next(get_db())
            
            content = db.query(Content).filter(Content.id == content_id).first()
            if content:
                content.view_count += 1
                db.commit()
                
                # Track analytics
                await self.analytics.track_content_view(content_id)
                
        except Exception as e:
            logger.error(f"Increment view count error: {str(e)}")
    
    async def toggle_like(self, content_id: str, user_id: str, db: Session = None) -> Dict[str, Any]:
        """        Toggle like/unlike for content.
        """        try:
            if not db:
                db = next(get_db())
            
            # Check if user already liked this content
            # This would require a separate likes table - simplified for now
            content = db.query(Content).filter(Content.id == content_id).first()
            if not content:
                raise ValueError("Content not found")
            
            # For simplicity, we'll track likes in a simple way
            # In production, use a separate ContentLike table
            liked = await self._toggle_user_like(content_id, user_id, db)
            
            if liked:
                content.like_count += 1
            else:
                content.like_count = max(0, content.like_count - 1)
            
            db.commit()
            
            # Track analytics
            await self.analytics.track_content_like(content_id, user_id, liked)
            
            return {
                "liked": liked,
                "total_likes": content.like_count
            }
            
        except Exception as e:
            logger.error(f"Toggle like error: {str(e)}")
            raise
    
    async def search_content(
        self,
        query: str,
        category: Optional[str] = None,
        file_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 20,
        user_id: Optional[str] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """        Search public content with full-text search and filters.
        """        try:
            if not db:
                db = next(get_db())
            
            # Base query for public content only
            base_query = db.query(Content).filter(
                and_(
                    Content.is_active == True,
                    Content.privacy_level == "public"
                )
            )
            
            # Apply text search
            if query:
                search_filter = or_(
                    Content.title.ilike(f"%{query}%"),
                    Content.description.ilike(f"%{query}%"),
                    Content.tags.contains([query])
                )
                base_query = base_query.filter(search_filter)
            
            # Apply filters
            if category:
                base_query = base_query.filter(Content.category == category)
            if file_type:
                base_query = base_query.filter(Content.file_type == file_type)
            if tags:
                for tag in tags:
                    base_query = base_query.filter(Content.tags.contains([tag]))
            
            # Order by relevance (views + likes + recency)
            base_query = base_query.order_by(
                desc(Content.view_count + Content.like_count),
                desc(Content.created_at)
            )
            
            # Get total count
            total = base_query.count()
            
            # Get results with pagination
            results = base_query.offset(skip).limit(limit).all()
            
            # Format results
            formatted_results = []
            for content in results:
                result = {
                    "content_id": str(content.id),
                    "title": content.title,
                    "description": content.description,
                    "file_type": content.file_type,
                    "category": content.category,
                    "tags": content.tags,
                    "created_at": content.created_at,
                    "view_count": content.view_count,
                    "like_count": content.like_count,
                    "owner": {
                        "username": content.owner.username,
                        "role": content.owner.role
                    } if content.owner else None
                }
                
                # Add thumbnail if available
                if content.thumbnail_path:
                    result["thumbnail_url"] = f"/content/thumbnail/{content.id}"
                
                formatted_results.append(result)
            
            return {
                "results": formatted_results,
                "total": total
            }
            
        except Exception as e:
            logger.error(f"Content search error: {str(e)}")
            return {"results": [], "total": 0}
    
    async def get_trending_content(
        self,
        timeframe: str = "week",
        category: Optional[str] = None,
        limit: int = 20,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """        Get trending content based on engagement metrics.
        """        try:
            if not db:
                db = next(get_db())
            
            # Calculate time threshold
            now = datetime.utcnow()
            if timeframe == "day":
                time_threshold = now - timedelta(days=1)
            elif timeframe == "week":
                time_threshold = now - timedelta(weeks=1)
            elif timeframe == "month":
                time_threshold = now - timedelta(days=30)
            else:
                time_threshold = now - timedelta(weeks=1)
            
            # Query trending content
            query = db.query(Content).filter(
                and_(
                    Content.is_active == True,
                    Content.privacy_level == "public",
                    Content.created_at >= time_threshold
                )
            )
            
            if category:
                query = query.filter(Content.category == category)
            
            # Calculate trending score (views + likes * 2 + downloads * 3)
            trending_score = (
                Content.view_count + 
                (Content.like_count * 2) + 
                (Content.download_count * 3)
            )
            
            # Order by trending score
            results = query.order_by(desc(trending_score)).limit(limit).all()
            
            # Format results
            trending_content = []
            for content in results:
                trending_item = {
                    "content_id": str(content.id),
                    "title": content.title,
                    "description": content.description,
                    "file_type": content.file_type,
                    "category": content.category,
                    "created_at": content.created_at,
                    "metrics": {
                        "views": content.view_count,
                        "likes": content.like_count,
                        "downloads": content.download_count,
                        "trending_score": content.view_count + (content.like_count * 2) + (content.download_count * 3)
                    },
                    "owner": {
                        "username": content.owner.username,
                        "role": content.owner.role
                    } if content.owner else None
                }
                
                if content.thumbnail_path:
                    trending_item["thumbnail_url"] = f"/content/thumbnail/{content.id}"
                
                trending_content.append(trending_item)
            
            return trending_content
            
        except Exception as e:
            logger.error(f"Get trending content error: {str(e)}")
            return []
    
    async def generate_thumbnail(self, content_id: str, db: Session = None) -> Optional[str]:
        """        Generate thumbnail for content if applicable.
        """        try:
            if not db:
                db = next(get_db())
            
            content = db.query(Content).filter(Content.id == content_id).first()
            if not content:
                return None
            
            # Generate thumbnail based on file type
            thumbnail_path = None
            if content.file_type in ["image", "video"]:
                thumbnail_path = await self.thumbnail_generator.generate_thumbnail(
                    content.file_path, content.file_type
                )
            elif content.file_type == "audio":
                # Generate audio waveform thumbnail
                thumbnail_path = await self.thumbnail_generator.generate_audio_waveform(
                    content.file_path
                )
            
            # Update content with thumbnail path
            if thumbnail_path:
                content.thumbnail_path = thumbnail_path
                db.commit()
            
            return thumbnail_path
            
        except Exception as e:
            logger.error(f"Generate thumbnail error: {str(e)}")
            return None
    
    async def track_download(self, content_id: str, user_id: str, db: Session = None) -> None:
        """Track content download"""        try:
            if not db:
                db = next(get_db())
            
            content = db.query(Content).filter(Content.id == content_id).first()
            if content:
                content.download_count += 1
                db.commit()
                
                # Track analytics
                await self.analytics.track_content_download(content_id, user_id)
                
        except Exception as e:
            logger.error(f"Track download error: {str(e)}")
    
    async def get_content_statistics(self, content_id: str, db: Session = None) -> Dict[str, Any]:
        """Get detailed content statistics"""        try:
            if not db:
                db = next(get_db())
            
            content = db.query(Content).filter(Content.id == content_id).first()
            if not content:
                return {}
            
            stats = {
                "views": content.view_count,
                "likes": content.like_count,
                "downloads": content.download_count,
                "created_at": content.created_at,
                "file_size_mb": round(content.file_size / (1024 * 1024), 2),
                "engagement_rate": self._calculate_engagement_rate(content),
                "performance_score": self._calculate_performance_score(content)
            }
            
            # Get time-based analytics
            time_stats = await self.analytics.get_content_time_stats(content_id)
            stats.update(time_stats)
            
            return stats
            
        except Exception as e:
            logger.error(f"Get content statistics error: {str(e)}")
            return {}
    
    async def get_ai_analysis_results(self, content_id: str, db: Session = None) -> Dict[str, Any]:
        """Get AI analysis results for content"""        try:
            if not db:
                db = next(get_db())
            
            content = db.query(Content).filter(Content.id == content_id).first()
            if not content or not content.ai_analysis_results:
                return {}
            
            return content.ai_analysis_results
            
        except Exception as e:
            logger.error(f"Get AI analysis results error: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _post_creation_tasks(self, content_id: str) -> None:
        """Background tasks after content creation"""        try:
            # Generate thumbnail
            await self.generate_thumbnail(content_id)
            
            # Update search index (if using external search engine)
            await self._update_search_index(content_id)
            
        except Exception as e:
            logger.error(f"Post creation tasks error: {str(e)}")
    
    async def _cleanup_content_files(self, content_id: str, file_path: str) -> None:
        """Cleanup content files after deletion"""        try:
            # Wait a bit before cleanup (grace period)
            await asyncio.sleep(3600)  # 1 hour
            
            # Delete files from storage
            await self.file_handler.delete_file(file_path)
            
            logger.info(f"Files cleaned up for content: {content_id}")
            
        except Exception as e:
            logger.error(f"File cleanup error: {str(e)}")
    
    async def _check_collaboration_access(self, content_id: str, user_id: str) -> bool:
        """Check if user has collaboration access to content"""        # This would integrate with the collaboration service
        # Simplified for now
        return False
    
    async def _toggle_user_like(self, content_id: str, user_id: str, db: Session) -> bool:
        """Toggle user like status (simplified implementation)"""        # In production, use a separate ContentLike table
        # For now, return a simple toggle based on some logic
        return True  # Simplified
    
    async def _update_search_index(self, content_id: str) -> None:
        """Update external search index"""        try:
            # This would integrate with Elasticsearch or similar
            # Simplified for now
            pass
        except Exception as e:
            logger.error(f"Search index update error: {str(e)}")
    
    def _calculate_engagement_rate(self, content: Content) -> float:
        """Calculate content engagement rate"""        if content.view_count == 0:
            return 0.0
        
        engagement = (content.like_count + content.download_count) / content.view_count
        return round(engagement * 100, 2)
    
    def _calculate_performance_score(self, content: Content) -> int:
        """Calculate overall content performance score"""        base_score = content.view_count + (content.like_count * 2) + (content.download_count * 3)
        
        # Age factor (newer content gets bonus)
        age_days = (datetime.utcnow() - content.created_at).days
        age_factor = max(0.5, 1 - (age_days / 365))  # Reduce score by age
        
        return int(base_score * age_factor)
