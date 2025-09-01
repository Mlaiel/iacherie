"""Enterprise Content Discovery Manager

Advanced content discovery and metadata management for crawling
operations with intelligent categorization and analysis.

PROTECTION NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security Expert
Copyright: All rights reserved
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from uuid import uuid4
import json
import hashlib
from enum import Enum

from ..core.base import DatabaseManager
from ..models.crawling_models import (
    ContentDiscovery,
    DiscoveryStatus,
    ContentType,
    DiscoverySource
)
from ..core.exceptions import (
    DatabaseError,
    ValidationError,
    ContentDiscoveryError
)


class DiscoveryCategory(Enum):
    """
Content discovery categories."""

    ORIGINAL_CONTENT = 'original_content'
    DERIVATIVE_CONTENT = 'derivative_content'
    POTENTIAL_INFRINGEMENT = 'potential_infringement'
    COLLABORATION_OPPORTUNITY = 'collaboration_opportunity'
    TRENDING_CONTENT = 'trending_content'
    COMPETITOR_CONTENT = 'competitor_content'


class ConfidenceLevel(Enum):
    """
Confidence levels for content matching."""

    VERY_LOW = 'very_low'      # 0-20%
    LOW = 'low'                # 21-40%
    MEDIUM = 'medium'          # 41-60%
    HIGH = 'high'              # 61-80%
    VERY_HIGH = 'very_high'    # 81-100%


class ContentDiscoveryManager(DatabaseManager):
    """
    Enterprise-grade content discovery manager for crawling operations.
    
    Handles:
    - Content discovery storage and indexing
    - Intelligent content categorization
    - Duplicate detection and deduplication
    - Content analysis and metadata extraction
    - Discovery analytics and reporting
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize content discovery manager.
        
        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(db_session)
        self.table = ContentDiscovery
    
    async def store_discovery(
        self,
        session_id: str,
        job_id: str,
        content_data: Dict[str, Any],
        platform: str,
        source_url: Optional[str] = None,
        discovery_source: str = DiscoverySource.CRAWLER.value
    ) -> Dict[str, Any]:
        """
        Store discovered content with comprehensive metadata analysis.
        
        Args:
            session_id: Crawling session identifier
            job_id: Job identifier that discovered content
            content_data: Raw content data and metadata
            platform: Platform where content was discovered
            source_url: Optional source URL of content
            discovery_source: Source of discovery (crawler, api, manual)
            
        Returns:
            Dict containing stored discovery information
            
        Raises:
            ContentDiscoveryError: If storage fails
            ValidationError: If content data invalid
        """
        try:
            # Generate unique discovery ID
            discovery_id = str(uuid4())
            
            # Extract and validate content metadata
            content_metadata = await self._extract_content_metadata(content_data, platform)
            
            # Calculate content hash for duplicate detection
            content_hash = await self._calculate_content_hash(content_data)
            
            # Check for existing duplicate
            existing_discovery = await self._check_for_duplicate(content_hash, platform)
            if existing_discovery:
                return await self._handle_duplicate_discovery(
                    existing_discovery, session_id, job_id, content_data
                )
            
            # Analyze content and determine category
            analysis_result = await self._analyze_content(content_data, platform)
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(
                content_data, analysis_result
            )
            
            # Determine content type
            content_type = await self._determine_content_type(content_data)
            
            # Prepare discovery data
            discovery_data = {
                'discovery_id': discovery_id,
                'session_id': session_id,
                'job_id': job_id,
                'platform': platform,
                'content_type': content_type,
                'content_hash': content_hash,
                'source_url': source_url,
                'discovery_source': discovery_source,
                'status': DiscoveryStatus.DISCOVERED.value,
                'category': analysis_result.get('category', DiscoveryCategory.ORIGINAL_CONTENT.value),
                'confidence_score': confidence_score,
                'raw_content': json.dumps(content_data),
                'extracted_metadata': json.dumps(content_metadata),
                'analysis_results': json.dumps(analysis_result),
                'discovered_at': datetime.utcnow(),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'views_count': content_metadata.get('views_count', 0),
                'likes_count': content_metadata.get('likes_count', 0),
                'shares_count': content_metadata.get('shares_count', 0),
                'comments_count': content_metadata.get('comments_count', 0),
                'author_info': json.dumps(content_metadata.get('author_info', {})),
                'keywords': json.dumps(content_metadata.get('keywords', [])),
                'language': content_metadata.get('language', 'unknown')
            }
            
            # Create discovery record
            discovery = ContentDiscovery(**discovery_data)
            self.db.add(discovery)
            await self.db.commit()
            await self.db.refresh(discovery)
            
            # Index content for search
            await self._index_discovery_for_search(discovery_id, content_metadata)
            
            return {
                'discovery_id': discovery_id,
                'content_type': content_type,
                'platform': platform,
                'category': analysis_result.get('category'),
                'confidence_score': confidence_score,
                'discovered_at': discovery_data['discovered_at'],
                'metadata': content_metadata,
                'is_duplicate': False
            }
            
        except Exception as e:
            await self.db.rollback()
            if isinstance(e, (ValidationError, ContentDiscoveryError)):
                raise
            raise ContentDiscoveryError(f"Failed to store discovery: {str(e)}")
    
    async def _extract_content_metadata(
        self,
        content_data: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """
        Extract standardized metadata from raw content data.
        
        Args:
            content_data: Raw content data
            platform: Source platform
            
        Returns:
            Dict containing extracted metadata
        """
        try:
            metadata = {}
            
            # Extract common fields
            metadata['title'] = content_data.get('title', content_data.get('caption', ''))
            metadata['description'] = content_data.get('description', content_data.get('text', ''))
            metadata['author_username'] = content_data.get('author', content_data.get('username', ''))
            metadata['publish_date'] = content_data.get('publish_date', content_data.get('created_at'))
            
            # Extract engagement metrics
            metadata['views_count'] = self._safe_int(content_data.get('views', content_data.get('view_count', 0)))
            metadata['likes_count'] = self._safe_int(content_data.get('likes', content_data.get('like_count', 0)))
            metadata['shares_count'] = self._safe_int(content_data.get('shares', content_data.get('share_count', 0)))
            metadata['comments_count'] = self._safe_int(content_data.get('comments', content_data.get('comment_count', 0)))
            
            # Extract author information
            metadata['author_info'] = {
                'username': metadata['author_username'],
                'follower_count': self._safe_int(content_data.get('author_followers', 0)),
                'verified': content_data.get('author_verified', False),
                'profile_url': content_data.get('author_url', '')
            }
            
            # Platform-specific extractions
            if platform == 'youtube':
                metadata['duration'] = content_data.get('duration', 0)
                metadata['channel_id'] = content_data.get('channel_id', '')
                metadata['video_quality'] = content_data.get('quality', '')
                
            elif platform == 'tiktok':
                metadata['sound_info'] = content_data.get('music', {})
                metadata['effects'] = content_data.get('effects', [])
                metadata['hashtags'] = content_data.get('hashtags', [])
                
            elif platform == 'instagram':
                metadata['post_type'] = content_data.get('media_type', 'photo')
                metadata['location'] = content_data.get('location', {})
                metadata['tagged_users'] = content_data.get('tagged_users', [])
                
            elif platform == 'twitter':
                metadata['tweet_type'] = content_data.get('tweet_type', 'original')
                metadata['retweet_count'] = self._safe_int(content_data.get('retweet_count', 0))
                metadata['reply_count'] = self._safe_int(content_data.get('reply_count', 0))
            
            # Extract keywords and tags
            metadata['keywords'] = self._extract_keywords(metadata['title'], metadata['description'])
            metadata['hashtags'] = content_data.get('hashtags', [])
            
            # Detect language
            metadata['language'] = await self._detect_language(
                metadata['title'] + ' ' + metadata['description']
            )
            
            # Calculate engagement rate
            total_engagements = (
                metadata['likes_count'] + 
                metadata['shares_count'] + 
                metadata['comments_count']
            )
            if metadata['views_count'] > 0:
                metadata['engagement_rate'] = (total_engagements / metadata['views_count']) * 100
            else:
                metadata['engagement_rate'] = 0.0
            
            return metadata
            
        except Exception as e:
            raise ContentDiscoveryError(f"Failed to extract metadata: {str(e)}")
    
    def _safe_int(self, value: Any) -> int:
        """Safely convert value to integer."""
        try:
            if isinstance(value, str):
                # Handle values like "1.2K", "3.5M"
                value = value.replace(',', '').strip()
                if 'K' in value.upper():
                    return int(float(value.upper().replace('K', '')) * 1000)
                elif 'M' in value.upper():
                    return int(float(value.upper().replace('M', '')) * 1000000)
            return int(float(value))
        except (ValueError, TypeError, AttributeError):
            return 0
    
    async def _calculate_content_hash(self, content_data: Dict[str, Any]) -> str:
        """
        Calculate unique hash for content to detect duplicates.
        
        Args:
            content_data: Content data
            
        Returns:
            Content hash string
        """
        try:
            # Create normalized content for hashing
            hash_content = {
                'title': content_data.get('title', '').strip().lower(),
                'description': content_data.get('description', '').strip().lower(),
                'author': content_data.get('author', '').strip().lower(),
                'duration': content_data.get('duration', 0)
            }
            
            # Add media-specific identifiers
            if 'url' in content_data:
                hash_content['url'] = content_data['url']
            if 'media_id' in content_data:
                hash_content['media_id'] = content_data['media_id']
            
            # Create hash
            content_string = json.dumps(hash_content, sort_keys=True)
            return hashlib.sha256(content_string.encode()).hexdigest()
            
        except Exception as e:
            # Fallback to timestamp-based hash
            return hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()
    
    async def _check_for_duplicate(
        self,
        content_hash: str,
        platform: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check if content already exists based on hash.
        
        Args:
            content_hash: Content hash to check
            platform: Source platform
            
        Returns:
            Existing discovery data or None
        """
        try:
            result = await self.db.execute(
                text("""
                SELECT discovery_id, session_id, job_id, discovered_at, confidence_score
                FROM content_discoveries
                WHERE content_hash = :content_hash
                  AND platform = :platform
                  AND status != :deleted_status
                ORDER BY discovered_at DESC
                LIMIT 1
                """),
                {
                    'content_hash': content_hash,
                    'platform': platform,
                    'deleted_status': DiscoveryStatus.DELETED.value
                }
            )
            
            duplicate_row = result.first()
            if duplicate_row:
                return {
                    'discovery_id': duplicate_row.discovery_id,
                    'session_id': duplicate_row.session_id,
                    'job_id': duplicate_row.job_id,
                    'discovered_at': duplicate_row.discovered_at,
                    'confidence_score': duplicate_row.confidence_score
                }
            
            return None
            
        except Exception as e:
            # Don't fail on duplicate check errors
            return None
    
    async def _handle_duplicate_discovery(
        self,
        existing_discovery: Dict[str, Any],
        session_id: str,
        job_id: str,
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle duplicate content discovery by updating existing record.
        
        Args:
            existing_discovery: Existing discovery data
            session_id: Current session ID
            job_id: Current job ID
            content_data: New content data
            
        Returns:
            Updated discovery information
        """
        try:
            discovery_id = existing_discovery['discovery_id']
            
            # Update duplicate count and last seen
            await self.db.execute(
                text("""
                UPDATE content_discoveries 
                SET duplicate_count = COALESCE(duplicate_count, 0) + 1,
                    last_seen_at = :now,
                    updated_at = :now
                WHERE discovery_id = :discovery_id
                """),
                {
                    'discovery_id': discovery_id,
                    'now': datetime.utcnow()
                }
            )
            
            # Log duplicate discovery
            await self._log_duplicate_discovery(discovery_id, session_id, job_id)
            
            await self.db.commit()
            
            return {
                'discovery_id': discovery_id,
                'content_type': content_data.get('type', 'unknown'),
                'platform': existing_discovery.get('platform', 'unknown'),
                'confidence_score': existing_discovery.get('confidence_score', 0.0),
                'discovered_at': existing_discovery['discovered_at'],
                'metadata': {},
                'is_duplicate': True,
                'original_discovery_id': discovery_id
            }
            
        except Exception as e:
            await self.db.rollback()
            raise ContentDiscoveryError(f"Failed to handle duplicate: {str(e)}")
    
    async def _analyze_content(
        self,
        content_data: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """
        Analyze content to determine category and characteristics.
        
        Args:
            content_data: Content data to analyze
            platform: Source platform
            
        Returns:
            Dict containing analysis results
        """
        try:
            analysis = {
                'category': DiscoveryCategory.ORIGINAL_CONTENT.value,
                'characteristics': [],
                'risk_factors': [],
                'opportunities': []
            }
            
            # Basic content analysis
            title = content_data.get('title', '').lower()
            description = content_data.get('description', '').lower()
            content_text = f"{title} {description}"
            
            # Check for trending indicators
            trending_keywords = ['viral', 'trending', 'popular', 'hot', 'breaking']
            if any(keyword in content_text for keyword in trending_keywords):
                analysis['category'] = DiscoveryCategory.TRENDING_CONTENT.value
                analysis['characteristics'].append('trending_content')
            
            # Check for collaboration keywords
            collab_keywords = ['collab', 'collaboration', 'featuring', 'with', 'ft.', 'duet']
            if any(keyword in content_text for keyword in collab_keywords):
                analysis['opportunities'].append('collaboration_opportunity')
                if analysis['category'] == DiscoveryCategory.ORIGINAL_CONTENT.value:
                    analysis['category'] = DiscoveryCategory.COLLABORATION_OPPORTUNITY.value
            
            # Check for potential copyright issues
            copyright_keywords = ['cover', 'remix', 'reaction', 'review', 'parody']
            if any(keyword in content_text for keyword in copyright_keywords):
                analysis['risk_factors'].append('potential_copyright_issue')
                analysis['category'] = DiscoveryCategory.DERIVATIVE_CONTENT.value
            
            # Analyze engagement metrics
            views = content_data.get('views', 0)
            likes = content_data.get('likes', 0)
            
            if isinstance(views, (int, float)) and views > 0:
                engagement_rate = (likes / views) * 100 if likes else 0
                
                if engagement_rate > 10:
                    analysis['characteristics'].append('high_engagement')
                elif engagement_rate > 5:
                    analysis['characteristics'].append('medium_engagement')
                else:
                    analysis['characteristics'].append('low_engagement')
            
            # Platform-specific analysis
            if platform == 'tiktok':
                if 'hashtags' in content_data:
                    hashtag_count = len(content_data['hashtags'])
                    if hashtag_count > 10:
                        analysis['characteristics'].append('hashtag_heavy')
                    
            elif platform == 'youtube':
                duration = content_data.get('duration', 0)
                if duration > 600:  # 10 minutes
                    analysis['characteristics'].append('long_form_content')
                elif duration < 60:  # 1 minute
                    analysis['characteristics'].append('short_form_content')
            
            return analysis
            
        except Exception as e:
            # Return default analysis on error
            return {
                'category': DiscoveryCategory.ORIGINAL_CONTENT.value,
                'characteristics': [],
                'risk_factors': [],
                'opportunities': [],
                'analysis_error': str(e)
            }
    
    async def _calculate_confidence_score(
        self,
        content_data: Dict[str, Any],
        analysis_result: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score for content discovery.
        
        Args:
            content_data: Content data
            analysis_result: Content analysis results
            
        Returns:
            Confidence score (0.0 - 100.0)
        """
        try:
            base_score = 50.0  # Start with medium confidence
            
            # Boost score for complete metadata
            if content_data.get('title'):
                base_score += 10
            if content_data.get('description'):
                base_score += 10
            if content_data.get('author'):
                base_score += 10
            if content_data.get('views', 0) > 0:
                base_score += 10
            
            # Boost score for engagement
            if 'high_engagement' in analysis_result.get('characteristics', []):
                base_score += 15
            elif 'medium_engagement' in analysis_result.get('characteristics', []):
                base_score += 10
            
            # Reduce score for risk factors
            risk_count = len(analysis_result.get('risk_factors', []))
            base_score -= (risk_count * 5)
            
            # Platform-specific adjustments
            platform_confidence = {
                'youtube': 5,    # High API reliability
                'twitter': 5,    # High API reliability
                'instagram': 0,  # Medium reliability
                'tiktok': -5,    # Lower reliability due to scraping
                'generic': -10   # Lowest reliability
            }
            
            platform = content_data.get('platform', 'generic')
            base_score += platform_confidence.get(platform, 0)
            
            # Ensure score is within bounds
            return max(0.0, min(100.0, base_score))
            
        except Exception:
            return 50.0  # Default medium confidence
    
    async def _determine_content_type(self, content_data: Dict[str, Any]) -> str:
        """
        Determine content type from content data.
        
        Args:
            content_data: Content data
            
        Returns:
            Content type string
        """
        # Check explicit type first
        if 'type' in content_data:
            return content_data['type']
        
        # Infer from platform and content
        if 'duration' in content_data or 'video_url' in content_data:
            return ContentType.VIDEO.value
        elif 'image_url' in content_data or 'photo' in str(content_data).lower():
            return ContentType.IMAGE.value
        elif 'audio_url' in content_data or 'sound' in content_data:
            return ContentType.AUDIO.value
        elif len(content_data.get('description', '')) > 0:
            return ContentType.TEXT.value
        else:
            return ContentType.MIXED.value
    
    def _extract_keywords(self, title: str, description: str) -> List[str]:
        """
        Extract keywords from title and description.
        
        Args:
            title: Content title
            description: Content description
            
        Returns:
            List of extracted keywords
        """
        try:
            import re
            
            # Combine text
            text = f"{title} {description}".lower()
            
            # Remove special characters and split
            words = re.findall(r'\b\w+\b', text)
            
            # Filter out common stop words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are',
                'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
                'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
                'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
                'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
            }
            
            # Filter and get unique keywords with minimum length
            keywords = list(set([
                word for word in words 
                if len(word) > 2 and word not in stop_words
            ]))
            
            # Return top 20 keywords
            return keywords[:20]
            
        except Exception:
            return []
    
    async def _detect_language(self, text: str) -> str:
        """
        Detect language of content text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (e.g., 'en', 'fr', 'de')
        """
        try:
            # Simple language detection based on common words
            # In production, use a proper language detection library
            
            if not text or len(text.strip()) < 10:
                return 'unknown'
            
            text_lower = text.lower()
            
            # English indicators
            english_words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all']
            english_count = sum(1 for word in english_words if word in text_lower)
            
            # French indicators
            french_words = ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et']
            french_count = sum(1 for word in french_words if word in text_lower)
            
            # German indicators
            german_words = ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das']
            german_count = sum(1 for word in german_words if word in text_lower)
            
            # Determine language based on highest count
            if english_count >= french_count and english_count >= german_count:
                return 'en'
            elif french_count >= german_count:
                return 'fr'
            elif german_count > 0:
                return 'de'
            else:
                return 'unknown'
                
        except Exception:
            return 'unknown'
    
    async def _index_discovery_for_search(
        self,
        discovery_id: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Index discovery for search functionality.
        
        Args:
            discovery_id: Discovery identifier
            metadata: Content metadata
        """
        try:
            # In production, this would index to Elasticsearch or similar
            # For now, we'll create a simple search index record
            
            search_data = {
                'discovery_id': discovery_id,
                'title': metadata.get('title', ''),
                'description': metadata.get('description', ''),
                'keywords': ' '.join(metadata.get('keywords', [])),
                'author': metadata.get('author_username', ''),
                'indexed_at': datetime.utcnow()
            }
            
            # Store in search index table (would be implemented separately)
            # await self._store_search_index(search_data)
            
        except Exception:
            # Don't fail discovery storage if indexing fails
            pass
    
    async def _log_duplicate_discovery(
        self,
        discovery_id: str,
        session_id: str,
        job_id: str
    ) -> None:
        """
        Log duplicate discovery event.
        
        Args:
            discovery_id: Original discovery ID
            session_id: Session that found duplicate
            job_id: Job that found duplicate
        """
        try:
            # Log duplicate discovery for analytics
            duplicate_log = {
                'original_discovery_id': discovery_id,
                'duplicate_session_id': session_id,
                'duplicate_job_id': job_id,
                'detected_at': datetime.utcnow()
            }
            
            # Store in duplicate log table (would be implemented separately)
            # await self._store_duplicate_log(duplicate_log)
            
        except Exception:
            # Don't fail on logging errors
            pass
    
    async def get_user_discoveries(
        self,
        user_id: str,
        since: Optional[datetime] = None,
        limit: int = 50,
        platform: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get discoveries for a specific user with filters.
        
        Args:
            user_id: User identifier
            since: Optional start date filter
            limit: Maximum number of results
            platform: Optional platform filter
            content_type: Optional content type filter
            
        Returns:
            List of discovery dictionaries
        """
        try:
            # Build query conditions
            conditions = ["cs.user_id = :user_id"]
            params = {'user_id': user_id, 'limit': limit}
            
            if since:
                conditions.append("cd.discovered_at >= :since")
                params['since'] = since
            
            if platform:
                conditions.append("cd.platform = :platform")
                params['platform'] = platform
            
            if content_type:
                conditions.append("cd.content_type = :content_type")
                params['content_type'] = content_type
            
            query = f"""
            SELECT 
                cd.discovery_id, cd.platform, cd.content_type, cd.category,
                cd.confidence_score, cd.discovered_at, cd.views_count,
                cd.likes_count, cd.shares_count, cd.comments_count,
                cd.extracted_metadata, cd.source_url
            FROM content_discoveries cd
            JOIN crawling_sessions cs ON cd.session_id = cs.session_id
            WHERE {' AND '.join(conditions)}
            ORDER BY cd.discovered_at DESC
            LIMIT :limit
            """
            
            result = await self.db.execute(text(query), params)
            
            discoveries = []
            for row in result:
                metadata = json.loads(row.extracted_metadata) if row.extracted_metadata else {}
                
                discoveries.append({
                    'discovery_id': row.discovery_id,
                    'platform': row.platform,
                    'content_type': row.content_type,
                    'category': row.category,
                    'confidence_score': row.confidence_score,
                    'discovered_at': row.discovered_at.isoformat(),
                    'title': metadata.get('title', ''),
                    'author': metadata.get('author_username', ''),
                    'engagement': {
                        'views': row.views_count,
                        'likes': row.likes_count,
                        'shares': row.shares_count,
                        'comments': row.comments_count
                    },
                    'source_url': row.source_url
                })
            
            return discoveries
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user discoveries: {str(e)}")
    
    async def archive_session_discoveries(self, session_id: str) -> int:
        """
        Archive discoveries for a specific session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Number of discoveries archived
        """
        try:
            result = await self.db.execute(
                text("""
                UPDATE content_discoveries 
                SET status = :archived_status,
                    updated_at = :now
                WHERE session_id = :session_id
                  AND status != :archived_status
                """),
                {
                    'session_id': session_id,
                    'archived_status': DiscoveryStatus.ARCHIVED.value,
                    'now': datetime.utcnow()
                }
            )
            
            await self.db.commit()
            return result.rowcount
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to archive session discoveries: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of content discovery system.
        
        Returns:
            Dict containing health status
        """
        try:
            # Check recent discoveries
            recent_discoveries = await self.db.query(func.count(ContentDiscovery.discovery_id)).filter(
                ContentDiscovery.discovered_at >= datetime.utcnow() - timedelta(hours=24)
            ).scalar()
            
            # Check discovery success rate
            total_recent = await self.db.query(func.count(ContentDiscovery.discovery_id)).filter(
                ContentDiscovery.discovered_at >= datetime.utcnow() - timedelta(hours=24)
            ).scalar()
            
            failed_recent = await self.db.query(func.count(ContentDiscovery.discovery_id)).filter(
                and_(
                    ContentDiscovery.discovered_at >= datetime.utcnow() - timedelta(hours=24),
                    ContentDiscovery.status == DiscoveryStatus.FAILED.value
                )
            ).scalar()
            
            success_rate = ((total_recent - failed_recent) / max(total_recent, 1)) * 100
            
            # Determine health status
            status = 'healthy'
            if success_rate < 80:
                status = 'degraded'
            if success_rate < 60:
                status = 'unhealthy'
            
            return {
                'status': status,
                'recent_discoveries_24h': recent_discoveries,
                'success_rate_24h': success_rate,
                'failed_discoveries_24h': failed_recent,
                'last_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }


# Export main class
__all__ = ['ContentDiscoveryManager', 'DiscoveryCategory', 'ConfidenceLevel']
