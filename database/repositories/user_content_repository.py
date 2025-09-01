"""User Content Repository Module

Enterprise-grade repository for user content management with multi-format support,
metadata handling, versioning, and content lifecycle management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc, text
from datetime import datetime, timedelta
import uuid
import hashlib
from ..models.user_content import (
    UserContent,
    ContentType,
    ContentStatus,
    ContentGenre,
    ContentMood,
    QualityLevel,
    PrivacyLevel,
    ContentCategory
)
from ..models.content_fingerprints import ContentFingerprint
from .base_repository import BaseRepository, RepositoryException
import logging

logger = logging.getLogger(__name__)

class UserContentRepository(BaseRepository[UserContent]):
    """
    Repository for user content operations with advanced content management,
    metadata extraction, version control, and content optimization features.
    """
    
    def __init__(self, db_session: Session):
        """
Initialize user content repository"""
        super().__init__(db_session, UserContent)
        
    def create_content(self,
                      user_id: int,
                      title: str,
                      content_type: ContentType,
                      file_path: str,
                      file_size: int,
                      duration: Optional[float] = None,
                      description: Optional[str] = None,
                      tags: Optional[List[str]] = None,
                      genre: Optional[ContentGenre] = None,
                      mood: Optional[ContentMood] = None,
                      quality_level: QualityLevel = QualityLevel.HIGH,
                      privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE,
                      content_category: ContentCategory = ContentCategory.ORIGINAL,
                      metadata: Optional[Dict[str, Any]] = None) -> UserContent:
        """
        Create user content with comprehensive metadata and validation
        
        Args:
            user_id: Owner user ID
            title: Content title
            content_type: Type of content
            file_path: Storage file path
            file_size: File size in bytes
            duration: Content duration (for audio/video)
            description: Content description
            tags: Content tags for discovery
            genre: Content genre
            mood: Content mood
            quality_level: Content quality assessment
            privacy_level: Privacy settings
            content_category: Content category
            metadata: Additional metadata
            
        Returns:
            Created UserContent instance
        """
        try:
            # Generate content ID and hash
            content_id = str(uuid.uuid4())
            file_hash = self._calculate_file_hash(file_path)
            
            # Check for duplicate content
            existing_content = self.get_by_file_hash(file_hash)
            if existing_content and existing_content.user_id == user_id:
                raise RepositoryException(f"Content already exists: {existing_content.title}")
            
            content_data = {
                'user_id': user_id,
                'title': title,
                'content_type': content_type,
                'file_path': file_path,
                'file_size': file_size,
                'file_hash': file_hash,
                'duration': duration,
                'description': description,
                'tags': tags or [],
                'genre': genre,
                'mood': mood,
                'quality_level': quality_level,
                'privacy_level': privacy_level,
                'content_category': content_category,
                'status': ContentStatus.UPLOADED,
                'metadata': metadata or {},
                'content_id': content_id,
                'upload_date': datetime.utcnow(),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            content = self.create(**content_data)
            
            self.logger.info(
                f"Created {content_type.value} content: {title} for user {user_id}"
            )
            
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to create user content: {str(e)}")
            raise RepositoryException(f"Content creation failed: {str(e)}")
            
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of file for deduplication
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA-256 hash string
        """
        try:
            # In production, this would read the actual file
            # For now, create a hash based on the path
            return hashlib.sha256(file_path.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Failed to calculate file hash: {str(e)}")
            return hashlib.sha256(f"fallback_{datetime.utcnow()}".encode()).hexdigest()
            
    def get_by_file_hash(self, file_hash: str) -> Optional[UserContent]:
        """
        Get content by file hash for deduplication
        
        Args:
            file_hash: File hash to search for
            
        Returns:
            UserContent instance or None
        """
        try:
            return self.db_session.query(UserContent).filter(
                UserContent.file_hash == file_hash
            ).first()
            
        except Exception as e:
            self.logger.error(f"Failed to get content by hash: {str(e)}")
            return None
            
    def get_user_content(self,
                        user_id: int,
                        content_type: Optional[ContentType] = None,
                        status: Optional[ContentStatus] = None,
                        genre: Optional[ContentGenre] = None,
                        privacy_level: Optional[PrivacyLevel] = None,
                        limit: Optional[int] = None,
                        offset: Optional[int] = None,
                        include_fingerprints: bool = False) -> List[UserContent]:
        """
        Get user content with comprehensive filtering and optional fingerprint data
        
        Args:
            user_id: User ID to filter by
            content_type: Optional content type filter
            status: Optional status filter
            genre: Optional genre filter
            privacy_level: Optional privacy level filter
            limit: Maximum number of results
            offset: Number of results to skip
            include_fingerprints: Whether to include fingerprint data
            
        Returns:
            List of UserContent instances
        """
        try:
            query = self.db_session.query(UserContent).filter(
                UserContent.user_id == user_id
            )
            
            # Include fingerprints if requested
            if include_fingerprints:
                query = query.options(
                    joinedload(UserContent.fingerprints)
                )
            
            # Apply filters
            if content_type:
                query = query.filter(UserContent.content_type == content_type)
            if status:
                query = query.filter(UserContent.status == status)
            if genre:
                query = query.filter(UserContent.genre == genre)
            if privacy_level:
                query = query.filter(UserContent.privacy_level == privacy_level)
            
            # Apply pagination
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
                
            # Order by upload date (most recent first)
            query = query.order_by(UserContent.upload_date.desc())
            
            content_list = query.all()
            
            self.logger.debug(
                f"Retrieved {len(content_list)} content items for user {user_id}"
            )
            
            return content_list
            
        except Exception as e:
            self.logger.error(f"Failed to get user content: {str(e)}")
            return []
            
    def search_content(self,
                      user_id: int,
                      search_query: str,
                      content_type: Optional[ContentType] = None,
                      limit: int = 20) -> List[UserContent]:
        """
        Search user content by title, description, and tags
        
        Args:
            user_id: User ID to search within
            search_query: Search query string
            content_type: Optional content type filter
            limit: Maximum number of results
            
        Returns:
            List of matching UserContent instances
        """
        try:
            # Create search conditions
            search_pattern = f"%{search_query.lower()}%"
            
            query = self.db_session.query(UserContent).filter(
                and_(
                    UserContent.user_id == user_id,
                    or_(
                        func.lower(UserContent.title).like(search_pattern),
                        func.lower(UserContent.description).like(search_pattern),
                        UserContent.tags.op('&&')(text(f"ARRAY['{search_query.lower()}']"))
                    )
                )
            )
            
            if content_type:
                query = query.filter(UserContent.content_type == content_type)
            
            # Order by relevance (title match first, then description, then tags)
            query = query.order_by(
                func.lower(UserContent.title).like(search_pattern).desc(),
                func.lower(UserContent.description).like(search_pattern).desc(),
                UserContent.upload_date.desc()
            ).limit(limit)
            
            results = query.all()
            
            self.logger.debug(
                f"Found {len(results)} content items matching '{search_query}' for user {user_id}"
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search content: {str(e)}")
            return []
            
    def update_content_status(self,
                            content_id: int,
                            new_status: ContentStatus,
                            status_reason: Optional[str] = None) -> Optional[UserContent]:
        """
        Update content status with history tracking
        
        Args:
            content_id: Content ID to update
            new_status: New status to set
            status_reason: Optional reason for status change
            
        Returns:
            Updated UserContent instance
        """
        try:
            content = self.get_by_id(content_id)
            if not content:
                return None
            
            # Update metadata with status history
            metadata = content.metadata or {}
            metadata['status_history'] = metadata.get('status_history', [])
            metadata['status_history'].append({
                'previous_status': content.status.value,
                'new_status': new_status.value,
                'timestamp': datetime.utcnow().isoformat(),
                'reason': status_reason
            })
            
            update_data = {
                'status': new_status,
                'metadata': metadata,
                'updated_at': datetime.utcnow()
            }
            
            # Set processing timestamps
            if new_status == ContentStatus.PROCESSING:
                update_data['processing_started'] = datetime.utcnow()
            elif new_status == ContentStatus.PUBLISHED:
                update_data['published_at'] = datetime.utcnow()
            elif new_status == ContentStatus.ARCHIVED:
                update_data['archived_at'] = datetime.utcnow()
            
            updated_content = self.update(content_id, **update_data)
            
            self.logger.info(
                f"Updated content {content_id} status: {content.status.value} → {new_status.value}"
            )
            
            return updated_content
            
        except Exception as e:
            self.logger.error(f"Failed to update content status: {str(e)}")
            raise RepositoryException(f"Content status update failed: {str(e)}")
            
    def get_content_analytics(self,
                            user_id: int,
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get comprehensive content analytics for user
        
        Args:
            user_id: User ID to analyze
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary containing content analytics
        """
        try:
            query = self.db_session.query(UserContent).filter(
                UserContent.user_id == user_id
            )
            
            # Apply date filters
            if start_date:
                query = query.filter(UserContent.upload_date >= start_date)
            if end_date:
                query = query.filter(UserContent.upload_date <= end_date)
            
            content_items = query.all()
            
            if not content_items:
                return {
                    'user_id': user_id,
                    'total_content': 0,
                    'content_types': {},
                    'status_distribution': {},
                    'quality_distribution': {},
                    'total_storage_used': 0,
                    'average_file_size': 0
                }
            
            # Basic statistics
            total_content = len(content_items)
            total_storage = sum(item.file_size for item in content_items)
            avg_file_size = total_storage / total_content
            
            # Content type distribution
            type_distribution = {}
            for item in content_items:
                content_type = item.content_type.value
                type_distribution[content_type] = type_distribution.get(content_type, 0) + 1
            
            # Status distribution
            status_distribution = {}
            for item in content_items:
                status = item.status.value
                status_distribution[status] = status_distribution.get(status, 0) + 1
            
            # Quality distribution
            quality_distribution = {}
            for item in content_items:
                quality = item.quality_level.value
                quality_distribution[quality] = quality_distribution.get(quality, 0) + 1
            
            # Genre distribution (for content with genres)
            genre_distribution = {}
            for item in content_items:
                if item.genre:
                    genre = item.genre.value
                    genre_distribution[genre] = genre_distribution.get(genre, 0) + 1
            
            # Privacy distribution
            privacy_distribution = {}
            for item in content_items:
                privacy = item.privacy_level.value
                privacy_distribution[privacy] = privacy_distribution.get(privacy, 0) + 1
            
            # Upload trends (last 30 days by day)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_content = [
                item for item in content_items 
                if item.upload_date >= thirty_days_ago
            ]
            
            # Group by date
            upload_trends = {}
            for item in recent_content:
                date_key = item.upload_date.date().isoformat()
                upload_trends[date_key] = upload_trends.get(date_key, 0) + 1
            
            # Most used tags
            all_tags = []
            for item in content_items:
                if item.tags:
                    all_tags.extend(item.tags)
            
            tag_frequency = {}
            for tag in all_tags:
                tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
            
            # Top 10 most used tags
            top_tags = sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
            
            analytics = {
                'user_id': user_id,
                'summary': {
                    'total_content': total_content,
                    'total_storage_bytes': total_storage,
                    'total_storage_mb': round(total_storage / (1024 * 1024), 2),
                    'average_file_size_mb': round(avg_file_size / (1024 * 1024), 2),
                    'content_uploaded_last_30_days': len(recent_content)
                },
                'distributions': {
                    'content_types': type_distribution,
                    'status': status_distribution,
                    'quality_levels': quality_distribution,
                    'genres': genre_distribution,
                    'privacy_levels': privacy_distribution
                },
                'trends': {
                    'daily_uploads_last_30_days': upload_trends,
                    'top_tags': [{'tag': tag, 'count': count} for tag, count in top_tags]
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get content analytics: {str(e)}")
            return {'error': str(e), 'user_id': user_id}
            
    def get_content_with_fingerprints(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get user content with associated fingerprint data
        
        Args:
            user_id: User ID to get content for
            
        Returns:
            List of content dictionaries with fingerprint data
        """
        try:
            # Join with ContentFingerprint to get protection status
            query = self.db_session.query(
                UserContent, ContentFingerprint
            ).outerjoin(
                ContentFingerprint,
                UserContent.id == ContentFingerprint.content_id
            ).filter(
                UserContent.user_id == user_id
            ).order_by(UserContent.upload_date.desc())
            
            results = query.all()
            
            # Group results by content
            content_data = {}
            for content, fingerprint in results:
                if content.id not in content_data:
                    content_data[content.id] = {
                        'content': content,
                        'fingerprints': [],
                        'protection_status': 'unprotected',
                        'similarity_matches': 0
                    }
                
                if fingerprint:
                    content_data[content.id]['fingerprints'].append(fingerprint)
                    content_data[content.id]['protection_status'] = 'protected'
            
            # Convert to list and add protection analytics
            content_list = []
            for content_info in content_data.values():
                fingerprints = content_info['fingerprints']
                
                # Calculate protection metrics
                if fingerprints:
                    active_fingerprints = sum(
                        1 for fp in fingerprints 
                        if fp.status.value == 'active'
                    )
                    protection_coverage = (active_fingerprints / len(fingerprints)) * 100
                else:
                    active_fingerprints = 0
                    protection_coverage = 0
                
                content_info.update({
                    'protection_metrics': {
                        'total_fingerprints': len(fingerprints),
                        'active_fingerprints': active_fingerprints,
                        'protection_coverage_percent': round(protection_coverage, 2)
                    }
                })
                
                content_list.append(content_info)
            
            self.logger.debug(
                f"Retrieved {len(content_list)} content items with fingerprint data for user {user_id}"
            )
            
            return content_list
            
        except Exception as e:
            self.logger.error(f"Failed to get content with fingerprints: {str(e)}")
            return []
            
    def bulk_update_privacy_level(self,
                                content_ids: List[int],
                                new_privacy_level: PrivacyLevel,
                                user_id: int) -> int:
        """
        Bulk update privacy level for multiple content items
        
        Args:
            content_ids: List of content IDs to update
            new_privacy_level: New privacy level to set
            user_id: User ID for ownership verification
            
        Returns:
            Number of updated content items
        """
        try:
            updated_count = self.db_session.query(UserContent).filter(
                and_(
                    UserContent.id.in_(content_ids),
                    UserContent.user_id == user_id
                )
            ).update(
                {
                    'privacy_level': new_privacy_level,
                    'updated_at': datetime.utcnow()
                },
                synchronize_session=False
            )
            
            with self.transaction():
                pass  # Commit in transaction context
                
            self.logger.info(
                f"Bulk updated privacy level for {updated_count} content items to {new_privacy_level.value}"
            )
            
            return updated_count
            
        except Exception as e:
            self.logger.error(f"Failed to bulk update privacy level: {str(e)}")
            raise RepositoryException(f"Bulk privacy update failed: {str(e)}")
            
    def cleanup_orphaned_content(self, days_old: int = 30) -> int:
        """
        Clean up orphaned or old temporary content
        
        Args:
            days_old: Number of days after which temporary content is considered orphaned
            
        Returns:
            Number of cleaned up content items
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Find orphaned temporary content
            orphaned_content = self.db_session.query(UserContent).filter(
                and_(
                    UserContent.status == ContentStatus.TEMPORARY,
                    UserContent.upload_date < cutoff_date
                )
            )
            
            # Soft delete by updating status
            cleanup_count = orphaned_content.update(
                {
                    'status': ContentStatus.DELETED,
                    'updated_at': datetime.utcnow()
                },
                synchronize_session=False
            )
            
            with self.transaction():
                pass  # Commit in transaction context
                
            self.logger.info(
                f"Cleaned up {cleanup_count} orphaned content items older than {days_old} days"
            )
            
            return cleanup_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup orphaned content: {str(e)}")
            raise RepositoryException(f"Content cleanup failed: {str(e)}")

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
