"""Content Repository - Database Operations for Content Management
==============================================================

Enterprise-grade database operations for content management with
comprehensive CRUD operations, metadata handling, and analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
import hashlib

# Simple base repository class for this implementation
class BaseRepository:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        
    async def execute_query(self, query: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute database query (mock implementation)"""
        # This would normally execute the query against the database
        # For now, return empty list
        return []

logger = logging.getLogger(__name__)


class ContentRepository(BaseRepository):
    """
    Content database repository
    
    Handles all database operations for content management including
    storage, retrieval, metadata management, and analytics.
    """
    
    def __init__(self, db_connection=None):
        """Initialize content repository"""
        super().__init__(db_connection)
        self.table_name = "content"
        
        # Cache for frequently accessed content
        self.content_cache: Dict[int, Dict[str, Any]] = {}
        self.cache_ttl = 600  # 10 minutes
        self.cache_timestamps: Dict[int, datetime] = {}
        
        # Mock content data for testing
        self._initialize_mock_data()
        
    def _initialize_mock_data(self):
        """Initialize mock content data for testing"""
        self.mock_content = {
            1: {
                "id": 1,
                "user_id": 1,
                "user_name": "Content Creator",
                "title": "Sample Audio Track",
                "content_type": "audio",
                "file_path": "/content/audio/sample.mp3",
                "file_size": 5242880,  # 5MB
                "duration": 180,  # 3 minutes
                "metadata": {
                    "title": "Sample Audio Track",
                    "artist": "Content Creator",
                    "genre": "Electronic",
                    "description": "A sample electronic music track",
                    "tags": ["electronic", "music", "sample"],
                    "quality": {
                        "bitrate": 320,
                        "format": "MP3",
                        "sample_rate": 44100
                    }
                },
                "fingerprint": "fp_audio_sample_123",
                "created_at": datetime.utcnow() - timedelta(days=10),
                "updated_at": datetime.utcnow() - timedelta(days=5),
                "status": "active",
                "visibility": "public",
                "license_type": "standard"
            },
            2: {
                "id": 2,
                "user_id": 2,
                "user_name": "Video Producer",
                "title": "Marketing Video",
                "content_type": "video",
                "file_path": "/content/video/marketing.mp4",
                "file_size": 52428800,  # 50MB
                "duration": 120,  # 2 minutes
                "metadata": {
                    "title": "Marketing Video",
                    "creator": "Video Producer",
                    "category": "Marketing",
                    "description": "A professional marketing video",
                    "tags": ["marketing", "business", "promo"],
                    "quality": {
                        "resolution": "1920x1080",
                        "format": "MP4",
                        "frame_rate": 30,
                        "codec": "H.264"
                    }
                },
                "fingerprint": "fp_video_marketing_456",
                "created_at": datetime.utcnow() - timedelta(days=15),
                "updated_at": datetime.utcnow() - timedelta(days=8),
                "status": "active",
                "visibility": "public",
                "license_type": "premium"
            }
        }
    
    async def get_content(self, content_id: int) -> Optional[Dict[str, Any]]:
        """
        Get content by ID
        
        Args:
            content_id: Content ID
            
        Returns:
            Dict: Content data or None if not found
        """
        try:
            # Check cache first
            if self._is_cached_and_valid(content_id):
                return self.content_cache[content_id].copy()
            
            # Query database
            if self.db_connection:
                query = """
                SELECT c.*, u.username as user_name
                FROM content c
                LEFT JOIN users u ON c.user_id = u.id
                WHERE c.id = %(content_id)s AND c.status != 'deleted'
                """
                
                result = await self.execute_query(query, {"content_id": content_id})
                
                if result:
                    content_data = self._format_content_data(result[0])
                    # Cache the result
                    self.content_cache[content_id] = content_data
                    self.cache_timestamps[content_id] = datetime.utcnow()
                    
                    return content_data
            else:
                # Mock implementation
                if content_id in self.mock_content:
                    content_data = self.mock_content[content_id].copy()
                    self.content_cache[content_id] = content_data
                    self.cache_timestamps[content_id] = datetime.utcnow()
                    return content_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting content {content_id}: {e}")
            return None
    
    async def create_content(self, content_data: Dict[str, Any]) -> int:
        """
        Create new content record
        
        Args:
            content_data: Content information
            
        Returns:
            int: Content ID
        """
        try:
            # Prepare content data for database
            db_data = {
                "user_id": content_data["user_id"],
                "title": content_data.get("title", "Untitled"),
                "content_type": content_data["content_type"],
                "file_path": content_data.get("file_path", ""),
                "file_size": content_data.get("file_size", 0),
                "duration": content_data.get("duration", 0),
                "metadata": json.dumps(content_data.get("metadata", {})),
                "fingerprint": content_data.get("fingerprint", ""),
                "status": content_data.get("status", "active"),
                "visibility": content_data.get("visibility", "public"),
                "license_type": content_data.get("license_type", "standard"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert into database
            if self.db_connection:
                query = """
                INSERT INTO content (
                    user_id, title, content_type, file_path, file_size,
                    duration, metadata, fingerprint, status, visibility,
                    license_type, created_at, updated_at
                ) VALUES (
                    %(user_id)s, %(title)s, %(content_type)s, %(file_path)s, %(file_size)s,
                    %(duration)s, %(metadata)s, %(fingerprint)s, %(status)s, %(visibility)s,
                    %(license_type)s, %(created_at)s, %(updated_at)s
                ) RETURNING id
                """
                
                result = await self.execute_query(query, db_data)
                content_id = result[0]["id"] if result else None
            else:
                # Mock implementation
                content_id = max(self.mock_content.keys()) + 1 if self.mock_content else 1
                db_data["id"] = content_id
                self.mock_content[content_id] = db_data
                self.content_cache[content_id] = db_data
                self.cache_timestamps[content_id] = datetime.utcnow()
            
            if content_id:
                logger.info(f"Content created: {content_id}")
                return content_id
            else:
                raise Exception("Failed to create content")
                
        except Exception as e:
            logger.error(f"Error creating content: {e}")
            raise
    
    async def update_content(
        self,
        content_id: int,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update content record
        
        Args:
            content_id: Content ID
            updates: Fields to update
            
        Returns:
            bool: True if updated successfully
        """
        try:
            # Add update timestamp
            updates["updated_at"] = datetime.utcnow()
            
            if self.db_connection:
                # Build dynamic update query
                set_clauses = []
                query_params = {"content_id": content_id}
                
                for key, value in updates.items():
                    if key == "metadata" and isinstance(value, dict):
                        value = json.dumps(value)
                    set_clauses.append(f"{key} = %({key})s")
                    query_params[key] = value
                
                query = f"""
                UPDATE content 
                SET {', '.join(set_clauses)}
                WHERE id = %(content_id)s
                """
                
                await self.execute_query(query, query_params)
            else:
                # Mock implementation
                if content_id in self.mock_content:
                    self.mock_content[content_id].update(updates)
                elif content_id in self.content_cache:
                    self.content_cache[content_id].update(updates)
            
            # Invalidate cache
            if content_id in self.content_cache:
                del self.content_cache[content_id]
                del self.cache_timestamps[content_id]
            
            logger.info(f"Content updated: {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating content {content_id}: {e}")
            return False
    
    async def delete_content(self, content_id: int) -> bool:
        """
        Soft delete content (mark as deleted)
        
        Args:
            content_id: Content ID
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            return await self.update_content(content_id, {
                "status": "deleted",
                "deleted_at": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"Error deleting content {content_id}: {e}")
            return False
    
    async def get_user_content(
        self,
        user_id: int,
        content_type: Optional[str] = None,
        status: str = "active",
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get content by user
        
        Args:
            user_id: User ID
            content_type: Filter by content type
            status: Filter by status
            limit: Maximum results
            offset: Results offset
            
        Returns:
            List[Dict]: User's content
        """
        try:
            if self.db_connection:
                # Build dynamic query
                where_conditions = ["user_id = %(user_id)s", "status = %(status)s"]
                query_params = {"user_id": user_id, "status": status}
                
                if content_type:
                    where_conditions.append("content_type = %(content_type)s")
                    query_params["content_type"] = content_type
                
                where_clause = " AND ".join(where_conditions)
                
                query = f"""
                SELECT c.*, u.username as user_name
                FROM content c
                LEFT JOIN users u ON c.user_id = u.id
                WHERE {where_clause}
                ORDER BY c.created_at DESC
                LIMIT %(limit)s OFFSET %(offset)s
                """
                
                query_params.update({"limit": limit, "offset": offset})
                
                result = await self.execute_query(query, query_params)
                
                return [self._format_content_data(row) for row in result]
            else:
                # Mock implementation
                user_content = []
                for content_data in self.mock_content.values():
                    if (content_data.get("user_id") == user_id and
                        content_data.get("status") == status):
                        
                        if not content_type or content_data.get("content_type") == content_type:
                            user_content.append(content_data.copy())
                
                # Sort by created_at descending
                user_content.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
                
                # Apply limit and offset
                return user_content[offset:offset+limit]
            
        except Exception as e:
            logger.error(f"Error getting user content: {e}")
            return []
    
    async def search_content(
        self,
        search_params: Dict[str, Any],
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search content with various filters
        
        Args:
            search_params: Search parameters
            limit: Maximum results
            offset: Results offset
            
        Returns:
            List[Dict]: Matching content
        """
        try:
            if self.db_connection:
                # Build dynamic search query
                where_conditions = ["status != 'deleted'"]
                query_params = {}
                
                if "query" in search_params:
                    where_conditions.append("(title ILIKE %(query)s OR metadata::text ILIKE %(query)s)")
                    query_params["query"] = f"%{search_params['query']}%"
                
                if "content_type" in search_params:
                    where_conditions.append("content_type = %(content_type)s")
                    query_params["content_type"] = search_params["content_type"]
                
                if "user_id" in search_params:
                    where_conditions.append("user_id = %(user_id)s")
                    query_params["user_id"] = search_params["user_id"]
                
                if "license_type" in search_params:
                    where_conditions.append("license_type = %(license_type)s")
                    query_params["license_type"] = search_params["license_type"]
                
                if "min_duration" in search_params:
                    where_conditions.append("duration >= %(min_duration)s")
                    query_params["min_duration"] = search_params["min_duration"]
                
                if "max_duration" in search_params:
                    where_conditions.append("duration <= %(max_duration)s")
                    query_params["max_duration"] = search_params["max_duration"]
                
                if "tags" in search_params:
                    where_conditions.append("metadata->'tags' ?| %(tags)s")
                    query_params["tags"] = search_params["tags"]
                
                where_clause = " AND ".join(where_conditions)
                
                # Determine sort order
                order_by = "created_at DESC"
                if search_params.get("sort_by") == "title":
                    order_by = "title ASC"
                elif search_params.get("sort_by") == "duration":
                    order_by = "duration DESC"
                elif search_params.get("sort_by") == "file_size":
                    order_by = "file_size DESC"
                
                query = f"""
                SELECT c.*, u.username as user_name
                FROM content c
                LEFT JOIN users u ON c.user_id = u.id
                WHERE {where_clause}
                ORDER BY {order_by}
                LIMIT %(limit)s OFFSET %(offset)s
                """
                
                query_params.update({"limit": limit, "offset": offset})
                
                result = await self.execute_query(query, query_params)
                
                return [self._format_content_data(row) for row in result]
            else:
                # Mock implementation
                matching_content = []
                
                for content_data in self.mock_content.values():
                    if content_data.get("status") == "deleted":
                        continue
                    
                    matches = True
                    
                    # Text search
                    if "query" in search_params:
                        query = search_params["query"].lower()
                        title = content_data.get("title", "").lower()
                        metadata_text = json.dumps(content_data.get("metadata", {})).lower()
                        
                        if query not in title and query not in metadata_text:
                            matches = False
                    
                    # Filter checks
                    for key, value in search_params.items():
                        if key in ["query", "sort_by"]:
                            continue
                        
                        if key in content_data and content_data[key] != value:
                            matches = False
                            break
                    
                    if matches:
                        matching_content.append(content_data.copy())
                
                # Apply sorting
                if search_params.get("sort_by") == "title":
                    matching_content.sort(key=lambda x: x.get("title", ""))
                elif search_params.get("sort_by") == "duration":
                    matching_content.sort(key=lambda x: x.get("duration", 0), reverse=True)
                else:
                    matching_content.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
                
                # Apply limit and offset
                return matching_content[offset:offset+limit]
            
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            return []
    
    async def get_content_statistics(
        self,
        period_start: datetime,
        period_end: datetime,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get content statistics for a period
        
        Args:
            period_start: Start of period
            period_end: End of period
            user_id: Optional user filter
            
        Returns:
            Dict: Content statistics
        """
        try:
            if self.db_connection:
                # Base statistics query
                where_conditions = ["created_at BETWEEN %(period_start)s AND %(period_end)s"]
                query_params = {"period_start": period_start, "period_end": period_end}
                
                if user_id:
                    where_conditions.append("user_id = %(user_id)s")
                    query_params["user_id"] = user_id
                
                where_clause = " AND ".join(where_conditions)
                
                query = f"""
                SELECT 
                    COUNT(*) as total_content,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_content,
                    COUNT(CASE WHEN content_type = 'audio' THEN 1 END) as audio_content,
                    COUNT(CASE WHEN content_type = 'video' THEN 1 END) as video_content,
                    COUNT(CASE WHEN content_type = 'image' THEN 1 END) as image_content,
                    COUNT(CASE WHEN content_type = 'text' THEN 1 END) as text_content,
                    SUM(file_size) as total_file_size,
                    AVG(file_size) as avg_file_size,
                    SUM(duration) as total_duration,
                    AVG(duration) as avg_duration,
                    COUNT(DISTINCT user_id) as unique_creators
                FROM content 
                WHERE {where_clause}
                """
                
                result = await self.execute_query(query, query_params)
                stats = result[0] if result else {}
                
                # License type breakdown
                license_query = f"""
                SELECT license_type, COUNT(*) as count
                FROM content 
                WHERE {where_clause}
                GROUP BY license_type
                """
                
                license_result = await self.execute_query(license_query, query_params)
                license_breakdown = {row["license_type"]: row["count"] for row in license_result}
                
                return {
                    **stats,
                    "license_type_breakdown": license_breakdown,
                    "period": {
                        "start": period_start.isoformat(),
                        "end": period_end.isoformat()
                    }
                }
            else:
                # Mock implementation
                relevant_content = []
                for content_data in self.mock_content.values():
                    created_at = content_data.get("created_at")
                    if created_at and period_start <= created_at <= period_end:
                        if not user_id or content_data.get("user_id") == user_id:
                            relevant_content.append(content_data)
                
                total_content = len(relevant_content)
                active_content = len([c for c in relevant_content if c.get("status") == "active"])
                audio_content = len([c for c in relevant_content if c.get("content_type") == "audio"])
                video_content = len([c for c in relevant_content if c.get("content_type") == "video"])
                
                total_file_size = sum(c.get("file_size", 0) for c in relevant_content)
                total_duration = sum(c.get("duration", 0) for c in relevant_content)
                
                return {
                    "total_content": total_content,
                    "active_content": active_content,
                    "audio_content": audio_content,
                    "video_content": video_content,
                    "total_file_size": total_file_size,
                    "total_duration": total_duration,
                    "period": {
                        "start": period_start.isoformat(),
                        "end": period_end.isoformat()
                    }
                }
            
        except Exception as e:
            logger.error(f"Error getting content statistics: {e}")
            return {}
    
    async def get_popular_content(
        self,
        content_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get popular content based on usage metrics
        
        Args:
            content_type: Filter by content type
            limit: Maximum results
            
        Returns:
            List[Dict]: Popular content
        """
        try:
            if self.db_connection:
                # Join with usage statistics to find popular content
                where_conditions = ["c.status = 'active'"]
                query_params = {}
                
                if content_type:
                    where_conditions.append("c.content_type = %(content_type)s")
                    query_params["content_type"] = content_type
                
                where_clause = " AND ".join(where_conditions)
                
                query = f"""
                SELECT c.*, u.username as user_name, 
                       COALESCE(SUM(ls.usage_count), 0) as total_usage
                FROM content c
                LEFT JOIN users u ON c.user_id = u.id
                LEFT JOIN license_usage_stats ls ON c.id = ls.content_id
                WHERE {where_clause}
                GROUP BY c.id, u.username
                ORDER BY total_usage DESC, c.created_at DESC
                LIMIT %(limit)s
                """
                
                query_params["limit"] = limit
                
                result = await self.execute_query(query, query_params)
                
                return [self._format_content_data(row) for row in result]
            else:
                # Mock implementation - return recent content as "popular"
                popular_content = []
                for content_data in self.mock_content.values():
                    if content_data.get("status") == "active":
                        if not content_type or content_data.get("content_type") == content_type:
                            popular_content.append(content_data.copy())
                
                # Sort by created_at (newest first) as proxy for popularity
                popular_content.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
                
                return popular_content[:limit]
            
        except Exception as e:
            logger.error(f"Error getting popular content: {e}")
            return []
    
    def _is_cached_and_valid(self, content_id: int) -> bool:
        """Check if content is cached and valid"""
        if content_id not in self.content_cache:
            return False
        
        if content_id not in self.cache_timestamps:
            return False
        
        cache_age = (datetime.utcnow() - self.cache_timestamps[content_id]).seconds
        return cache_age < self.cache_ttl
    
    def _format_content_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format content data for consumption"""
        try:
            formatted_data = raw_data.copy()
            
            # Parse JSON metadata field
            if "metadata" in formatted_data and isinstance(formatted_data["metadata"], str):
                formatted_data["metadata"] = json.loads(formatted_data["metadata"])
            
            # Ensure metadata exists
            if "metadata" not in formatted_data:
                formatted_data["metadata"] = {}
            
            # Add computed fields
            if "file_size" in formatted_data:
                formatted_data["file_size_mb"] = round(formatted_data["file_size"] / (1024 * 1024), 2)
            
            if "duration" in formatted_data and formatted_data["duration"]:
                minutes = formatted_data["duration"] // 60
                seconds = formatted_data["duration"] % 60
                formatted_data["duration_formatted"] = f"{minutes}:{seconds:02d}"
            
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error formatting content data: {e}")
            return raw_data
    
    async def cleanup_cache(self) -> None:
        """Clean up expired cache entries"""
        try:
            current_time = datetime.utcnow()
            expired_ids = []
            
            for content_id, timestamp in self.cache_timestamps.items():
                if (current_time - timestamp).seconds > self.cache_ttl:
                    expired_ids.append(content_id)
            
            for content_id in expired_ids:
                del self.content_cache[content_id]
                del self.cache_timestamps[content_id]
            
            if expired_ids:
                logger.debug(f"Cleaned up {len(expired_ids)} expired cache entries")
                
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
    
    def get_repository_stats(self) -> Dict[str, Any]:
        """Get repository statistics"""
        return {
            "cache_size": len(self.content_cache),
            "mock_content_size": len(self.mock_content),
            "cache_hit_ratio": 0.75,  # Mock value
            "supported_content_types": ["audio", "video", "image", "text"],
            "supported_operations": [
                "create", "read", "update", "delete", "search", "statistics"
            ]
        }