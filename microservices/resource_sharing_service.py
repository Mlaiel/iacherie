"""
Resource Sharing Service module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🤝 RESOURCE SHARING SERVICE
==========================

Advanced resource sharing and collaborative management service for the Ainflue platform.
Handles asset sharing, collaborative resource allocation, and team resource optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import redis.asyncio as redis
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """Resource type enumeration"""
    DIGITAL_ASSET = "digital_asset"
    TEMPLATE = "template"
    MUSIC_TRACK = "music_track"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    PRESET = "preset"
    PLUGIN = "plugin"
    SAMPLE = "sample"
    EQUIPMENT = "equipment"

class AccessLevel(Enum):
    """Resource access level enumeration"""
    PUBLIC = "public"
    TEAM = "team"
    COLLABORATORS = "collaborators"
    PRIVATE = "private"
    RESTRICTED = "restricted"

class ShareStatus(Enum):
    """Resource sharing status"""
    AVAILABLE = "available"
    IN_USE = "in_use"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"
    EXPIRED = "expired"

@dataclass
class Resource:
    """Shared resource definition"""
    id: str
    name: str
    description: str
    resource_type: ResourceType
    owner_id: str
    access_level: AccessLevel
    status: ShareStatus = ShareStatus.AVAILABLE
    file_path: Optional[str] = None
    file_size: int = 0
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None
    usage_count: int = 0
    rating: float = 0.0
    rating_count: int = 0
    
    def __post_init__(self) -> None:
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

@dataclass
class ResourceShare:
    """Resource sharing instance"""
    id: str
    resource_id: str
    shared_by: str
    shared_with: List[str]
    share_type: str  # "individual", "team", "public"
    permissions: List[str]  # "view", "download", "edit", "share"
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    usage_limit: Optional[int] = None
    usage_count: int = 0
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class ResourceUsage:
    """Resource usage tracking"""
    id: str
    resource_id: str
    user_id: str
    action: str  # "view", "download", "edit"
    timestamp: datetime = None
    session_duration: Optional[int] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SharingMetrics:
    """Resource sharing metrics"""
    total_resources: int = 0
    shared_resources: int = 0
    active_shares: int = 0
    total_downloads: int = 0
    avg_rating: float = 0.0
    popular_resources: List[str] = None
    top_sharers: List[str] = None
    
    def __post_init__(self) -> None:
        if self.popular_resources is None:
            self.popular_resources = []
        if self.top_sharers is None:
            self.top_sharers = []

class ResourceSharingService:
    """Enterprise resource sharing service"""
    
    def __init__(self, redis_url -> None: str = "redis -> None://localhost -> None:6379") -> None:
        self.redis_url = redis_url
        self.resources: Dict[str, Resource] = {}
        self.shares: Dict[str, ResourceShare] = {}
        self.usage_history: List[ResourceUsage] = []
        self.user_permissions: Dict[str, Set[str]] = defaultdict(set)
        self.metrics = SharingMetrics()
        self.running = False
        self.redis_client = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def start(self) -> None:
        """Start the resource sharing service"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            self.running = True
            self.logger.info("🚀 Resource Sharing Service started")
            
            # Start background tasks
            asyncio.create_task(self._cleanup_expired_shares())
            asyncio.create_task(self._metrics_collector())
            
        except Exception as e:
            self.logger.error(f"❌ Error starting resource sharing service: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the resource sharing service"""
        try:
            self.running = False
            if self.redis_client:
                await self.redis_client.close()
            
            self.logger.info("🛑 Resource Sharing Service stopped")
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping resource sharing service: {e}")
    
    async def create_resource(
        self,
        name: str,
        description: str,
        resource_type: ResourceType,
        owner_id: str,
        file_path: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new shareable resource"""
        try:
            resource_id = str(uuid.uuid4())
            
            resource = Resource(
                id=resource_id,
                name=name,
                description=description,
                resource_type=resource_type,
                owner_id=owner_id,
                access_level=AccessLevel.PRIVATE,
                file_path=file_path,
                tags=tags or [],
                metadata=metadata or {}
            )
            
            self.resources[resource_id] = resource
            
            # Cache in Redis
            if self.redis_client:
                await self.redis_client.setex(
                    f"resource:{resource_id}",
                    86400,  # 24 hours
                    json.dumps(asdict(resource), default=str)
                )
            
            self.logger.info(f"✅ Created resource {resource_id}: {name}")
            return resource_id
            
        except Exception as e:
            self.logger.error(f"❌ Error creating resource: {e}")
            raise
    
    async def share_resource(
        self,
        resource_id: str,
        shared_by: str,
        shared_with: List[str],
        permissions: List[str],
        share_type: str = "individual",
        expires_in_hours: Optional[int] = None,
        usage_limit: Optional[int] = None
    ) -> str:
        """Share a resource with users or teams"""
        try:
            # Verify resource exists and user has permission
            resource = self.resources.get(resource_id)
            if not resource:
                raise ValueError(f"Resource {resource_id} not found")
            
            if resource.owner_id != shared_by and not await self._has_permission(shared_by, resource_id, "share"):
                raise PermissionError("User doesn't have permission to share this resource")
            
            share_id = str(uuid.uuid4())
            expires_at = None
            if expires_in_hours:
                expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
            
            share = ResourceShare(
                id=share_id,
                resource_id=resource_id,
                shared_by=shared_by,
                shared_with=shared_with,
                share_type=share_type,
                permissions=permissions,
                expires_at=expires_at,
                usage_limit=usage_limit
            )
            
            self.shares[share_id] = share
            
            # Update resource access level if sharing publicly
            if share_type == "public":
                resource.access_level = AccessLevel.PUBLIC
            elif share_type == "team":
                resource.access_level = AccessLevel.TEAM
            
            # Grant permissions to recipients
            for user_id in shared_with:
                for permission in permissions:
                    self.user_permissions[user_id].add(f"{resource_id}:{permission}")
            
            # Cache in Redis
            if self.redis_client:
                await self.redis_client.setex(
                    f"share:{share_id}",
                    86400,  # 24 hours
                    json.dumps(asdict(share), default=str)
                )
            
            self.logger.info(f"✅ Shared resource {resource_id} with {len(shared_with)} users")
            return share_id
            
        except Exception as e:
            self.logger.error(f"❌ Error sharing resource: {e}")
            raise
    
    async def access_resource(
        self,
        resource_id: str,
        user_id: str,
        action: str = "view"
    ) -> Dict[str, Any]:
        """Access a shared resource"""
        try:
            # Check if user has permission
            if not await self._has_permission(user_id, resource_id, action):
                raise PermissionError(f"User {user_id} doesn't have {action} permission for resource {resource_id}")
            
            resource = self.resources.get(resource_id)
            if not resource:
                raise ValueError(f"Resource {resource_id} not found")
            
            if resource.status != ShareStatus.AVAILABLE:
                raise ValueError(f"Resource is not available (status: {resource.status})")
            
            # Record usage
            usage = ResourceUsage(
                id=str(uuid.uuid4()),
                resource_id=resource_id,
                user_id=user_id,
                action=action
            )
            self.usage_history.append(usage)
            
            # Update resource usage count
            resource.usage_count += 1
            resource.updated_at = datetime.utcnow()
            
            # Update share usage if applicable
            for share in self.shares.values():
                if share.resource_id == resource_id and user_id in share.shared_with:
                    share.usage_count += 1
                    
                    # Check usage limit
                    if share.usage_limit and share.usage_count >= share.usage_limit:
                        # Revoke access
                        for permission in share.permissions:
                            self.user_permissions[user_id].discard(f"{resource_id}:{permission}")
                        
                        self.logger.info(f"⚠️ Usage limit reached for share {share.id}")
            
            self.logger.info(f"✅ User {user_id} accessed resource {resource_id} ({action})")
            
            return {
                "resource": asdict(resource),
                "access_granted": True,
                "file_path": resource.file_path if action in ["download", "view"] else None
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error accessing resource: {e}")
            raise
    
    async def _has_permission(self, user_id: str, resource_id: str, action: str) -> bool:
        """Check if user has permission for resource action"""
        try:
            # Owner always has all permissions
            resource = self.resources.get(resource_id)
            if resource and resource.owner_id == user_id:
                return True
            
            # Check explicit permissions
            permission_key = f"{resource_id}:{action}"
            if permission_key in self.user_permissions[user_id]:
                return True
            
            # Check public access
            if resource and resource.access_level == AccessLevel.PUBLIC and action in ["view", "download"]:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error checking permissions: {e}")
            return False
    
    async def rate_resource(self, resource_id: str, user_id: str, rating: float) -> bool:
        """Rate a shared resource"""
        try:
            if not 1.0 <= rating <= 5.0:
                raise ValueError("Rating must be between 1.0 and 5.0")
            
            resource = self.resources.get(resource_id)
            if not resource:
                raise ValueError(f"Resource {resource_id} not found")
            
            # Update rating (simple average for now)
            total_rating = resource.rating * resource.rating_count
            resource.rating_count += 1
            resource.rating = (total_rating + rating) / resource.rating_count
            resource.updated_at = datetime.utcnow()
            
            self.logger.info(f"✅ User {user_id} rated resource {resource_id}: {rating}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error rating resource: {e}")
            return False
    
    async def search_resources(
        self,
        query: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
        tags: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search shared resources"""
        try:
            results = []
            
            for resource in self.resources.values():
                # Filter by access permissions
                if user_id and not await self._has_permission(user_id, resource.id, "view"):
                    continue
                
                # Apply filters
                if resource_type and resource.resource_type != resource_type:
                    continue
                
                if min_rating and resource.rating < min_rating:
                    continue
                
                if tags and not any(tag in resource.tags for tag in tags):
                    continue
                
                if query and query.lower() not in resource.name.lower() and query.lower() not in resource.description.lower():
                    continue
                
                results.append({
                    "id": resource.id,
                    "name": resource.name,
                    "description": resource.description,
                    "type": resource.resource_type.value,
                    "rating": resource.rating,
                    "usage_count": resource.usage_count,
                    "tags": resource.tags
                })
            
            # Sort by rating and usage
            results.sort(key=lambda x: (x["rating"], x["usage_count"]), reverse=True)
            
            self.logger.info(f"🔍 Found {len(results)} resources for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error searching resources: {e}")
            return []
    
    async def get_user_resources(self, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get resources owned and shared with user"""
        try:
            owned = []
            shared_with_user = []
            
            for resource in self.resources.values():
                if resource.owner_id == user_id:
                    owned.append(asdict(resource))
                elif await self._has_permission(user_id, resource.id, "view"):
                    shared_with_user.append(asdict(resource))
            
            return {
                "owned": owned,
                "shared_with_user": shared_with_user
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting user resources: {e}")
            return {"owned": [], "shared_with_user": []}
    
    async def _cleanup_expired_shares(self) -> None:
        """Clean up expired resource shares"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                expired_shares = []
                
                for share_id, share in self.shares.items():
                    if share.expires_at and share.expires_at <= current_time:
                        expired_shares.append(share_id)
                
                # Remove expired shares and revoke permissions
                for share_id in expired_shares:
                    share = self.shares[share_id]
                    
                    # Revoke permissions
                    for user_id in share.shared_with:
                        for permission in share.permissions:
                            self.user_permissions[user_id].discard(f"{share.resource_id}:{permission}")
                    
                    del self.shares[share_id]
                    self.logger.info(f"🧹 Cleaned up expired share {share_id}")
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"❌ Error in cleanup task: {e}")
                await asyncio.sleep(60)
    
    async def _metrics_collector(self) -> None:
        """Collect resource sharing metrics"""
        while self.running:
            try:
                # Update metrics
                self.metrics.total_resources = len(self.resources)
                self.metrics.shared_resources = sum(1 for r in self.resources.values() 
                                                  if r.access_level != AccessLevel.PRIVATE)
                self.metrics.active_shares = len(self.shares)
                self.metrics.total_downloads = sum(r.usage_count for r in self.resources.values())
                
                # Calculate average rating
                rated_resources = [r for r in self.resources.values() if r.rating_count > 0]
                if rated_resources:
                    self.metrics.avg_rating = sum(r.rating for r in rated_resources) / len(rated_resources)
                
                # Popular resources (top 10 by usage)
                popular = sorted(self.resources.values(), key=lambda x: x.usage_count, reverse=True)[:10]
                self.metrics.popular_resources = [r.id for r in popular]
                
                # Top sharers (users with most shared resources)
                sharer_counts = defaultdict(int)
                for resource in self.resources.values():
                    if resource.access_level != AccessLevel.PRIVATE:
                        sharer_counts[resource.owner_id] += 1
                
                top_sharers = sorted(sharer_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                self.metrics.top_sharers = [user_id for user_id, _ in top_sharers]
                
                # Store metrics in Redis
                if self.redis_client:
                    await self.redis_client.setex(
                        "resource_sharing:metrics",
                        300,  # 5 minutes
                        json.dumps(asdict(self.metrics), default=str)
                    )
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"❌ Error collecting metrics: {e}")
                await asyncio.sleep(60)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get resource sharing metrics"""
        return asdict(self.metrics)
    
    async def get_resource_analytics(self, resource_id: str) -> Dict[str, Any]:
        """Get analytics for a specific resource"""
        try:
            resource = self.resources.get(resource_id)
            if not resource:
                raise ValueError(f"Resource {resource_id} not found")
            
            # Usage analytics
            usage_by_action = defaultdict(int)
            usage_by_date = defaultdict(int)
            unique_users = set()
            
            for usage in self.usage_history:
                if usage.resource_id == resource_id:
                    usage_by_action[usage.action] += 1
                    usage_by_date[usage.timestamp.date().isoformat()] += 1
                    unique_users.add(usage.user_id)
            
            # Share analytics
            active_shares = [s for s in self.shares.values() if s.resource_id == resource_id]
            total_shared_with = sum(len(s.shared_with) for s in active_shares)
            
            return {
                "resource_id": resource_id,
                "total_usage": resource.usage_count,
                "unique_users": len(unique_users),
                "rating": resource.rating,
                "rating_count": resource.rating_count,
                "usage_by_action": dict(usage_by_action),
                "usage_by_date": dict(usage_by_date),
                "active_shares": len(active_shares),
                "total_shared_with": total_shared_with
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting resource analytics: {e}")
            return {}


# Example usage and testing
async def main() -> None:
    """Test the resource sharing service"""
    service = ResourceSharingService()
    
    try:
        await service.start()
        
        # Create some test resources
        music_id = await service.create_resource(
            "Epic Beat Track",
            "High-energy electronic music track",
            ResourceType.MUSIC_TRACK,
            "creator_123",
            "/assets/music/epic_beat.mp3",
            ["electronic", "energetic", "royalty-free"]
        )
        
        template_id = await service.create_resource(
            "Instagram Story Template",
            "Professional Instagram story template",
            ResourceType.TEMPLATE,
            "designer_456",
            "/assets/templates/ig_story.psd",
            ["instagram", "social", "template"]
        )
        
        # Share resources
        await service.share_resource(
            music_id,
            "creator_123",
            ["collaborator_789", "team_leader_101"],
            ["view", "download"],
            "individual",
            expires_in_hours=24
        )
        
        await service.share_resource(
            template_id,
            "designer_456",
            ["public"],
            ["view", "download"],
            "public"
        )
        
        # Access resources
        result = await service.access_resource(music_id, "collaborator_789", "download")
        print(f"Access Result: {result['access_granted']}")
        
        # Rate resource
        await service.rate_resource(music_id, "collaborator_789", 4.5)
        
        # Search resources
        results = await service.search_resources(
            query="template",
            user_id="collaborator_789"
        )
        print(f"Search Results: {len(results)} resources found")
        
        # Get analytics
        analytics = await service.get_resource_analytics(music_id)
        print(f"Analytics: {analytics}")
        
        # Get metrics
        metrics = await service.get_metrics()
        print(f"Metrics: {metrics}")
        
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())