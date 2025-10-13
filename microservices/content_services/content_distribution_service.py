"""
📤 Content Distribution Service
Multi-platform content distribution and syndication system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
import asyncio
import logging
import uuid
from enum import Enum

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Supported distribution platforms"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"
    PINTEREST = "pinterest"
    REDDIT = "reddit"


class DistributionStatus(Enum):
    """Content distribution status"""
    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    DRAFT = "draft"


class ContentDistributionService:
    """Multi-platform content distribution service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.distributions: Dict[str, Dict[str, Any]] = {}
        self.platform_configs: Dict[str, Dict[str, Any]] = {}
        self.scheduled_distributions: List[Dict[str, Any]] = []
        
        # Initialize platform configurations
        self._initialize_platform_configs()
        
        self.logger.info("✅ ContentDistributionService initialized")
    
    def _initialize_platform_configs(self):
        """Initialize platform-specific configurations"""
        self.platform_configs = {
            PlatformType.YOUTUBE.value: {
                "max_title_length": 100,
                "max_description_length": 5000,
                "supported_formats": ["mp4", "mov", "avi", "wmv"],
                "max_file_size_mb": 128000,  # 128GB
                "api_endpoint": "https://www.googleapis.com/youtube/v3/",
                "requires_oauth": True
            },
            PlatformType.INSTAGRAM.value: {
                "max_title_length": 2200,
                "max_description_length": 2200,
                "supported_formats": ["jpg", "png", "mp4", "mov"],
                "max_file_size_mb": 1000,  # 1GB for videos
                "api_endpoint": "https://graph.facebook.com/",
                "requires_oauth": True
            },
            PlatformType.TIKTOK.value: {
                "max_title_length": 150,
                "max_description_length": 2200,
                "supported_formats": ["mp4", "mov", "mpeg", "flv", "avi"],
                "max_file_size_mb": 500,
                "api_endpoint": "https://open-api.tiktok.com/",
                "requires_oauth": True
            },
            PlatformType.TWITTER.value: {
                "max_title_length": 280,
                "max_description_length": 280,
                "supported_formats": ["jpg", "png", "gif", "mp4", "mov"],
                "max_file_size_mb": 512,
                "api_endpoint": "https://api.twitter.com/2/",
                "requires_oauth": True
            },
            PlatformType.LINKEDIN.value: {
                "max_title_length": 200,
                "max_description_length": 3000,
                "supported_formats": ["jpg", "png", "mp4", "mov"],
                "max_file_size_mb": 200,
                "api_endpoint": "https://api.linkedin.com/v2/",
                "requires_oauth": True
            }
        }
    
    async def distribute_content(self, content_data: Dict[str, Any], platforms: List[str], schedule_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Distribute content to multiple platforms"""
        try:
            distribution_id = str(uuid.uuid4())
            
            # Validate platforms
            invalid_platforms = [p for p in platforms if p not in self.platform_configs]
            if invalid_platforms:
                return {
                    "success": False,
                    "error": f"Unsupported platforms: {invalid_platforms}",
                    "supported_platforms": list(self.platform_configs.keys())
                }
            
            # Create distribution record
            distribution = {
                "distribution_id": distribution_id,
                "content_id": content_data.get("content_id", str(uuid.uuid4())),
                "title": content_data.get("title", ""),
                "description": content_data.get("description", ""),
                "content_type": content_data.get("content_type", "text"),
                "file_path": content_data.get("file_path", ""),
                "platforms": platforms,
                "status": DistributionStatus.SCHEDULED.value if schedule_time else DistributionStatus.PENDING.value,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "scheduled_for": schedule_time.isoformat() if schedule_time else None,
                "platform_results": {}
            }
            
            if schedule_time and schedule_time > datetime.now(timezone.utc):
                # Schedule for later
                self.scheduled_distributions.append(distribution)
                self.distributions[distribution_id] = distribution
                
                return {
                    "success": True,
                    "distribution_id": distribution_id,
                    "status": "scheduled",
                    "scheduled_for": schedule_time.isoformat(),
                    "platforms": platforms,
                    "message": f"Content scheduled for distribution to {len(platforms)} platforms"
                }
            else:
                # Distribute immediately
                distribution["status"] = DistributionStatus.PROCESSING.value
                
                # Process each platform
                for platform in platforms:
                    platform_result = await self._distribute_to_platform(content_data, platform)
                    distribution["platform_results"][platform] = platform_result
                
                # Update overall status
                successful_distributions = sum(1 for result in distribution["platform_results"].values() 
                                             if result.get("success", False))
                
                if successful_distributions == len(platforms):
                    distribution["status"] = DistributionStatus.PUBLISHED.value
                elif successful_distributions > 0:
                    distribution["status"] = DistributionStatus.PUBLISHED.value  # Partial success
                else:
                    distribution["status"] = DistributionStatus.FAILED.value
                
                distribution["completed_at"] = datetime.now(timezone.utc).isoformat()
                self.distributions[distribution_id] = distribution
                
                return {
                    "success": successful_distributions > 0,
                    "distribution_id": distribution_id,
                    "status": distribution["status"],
                    "platforms_successful": successful_distributions,
                    "platforms_total": len(platforms),
                    "platform_results": distribution["platform_results"],
                    "message": f"Content distributed to {successful_distributions}/{len(platforms)} platforms successfully"
                }
            
        except Exception as e:
            self.logger.error(f"Content distribution failed: {str(e)}")
            return {
                "success": False,
                "error": "Distribution failed",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _distribute_to_platform(self, content_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Distribute content to a specific platform"""
        try:
            platform_config = self.platform_configs[platform]
            
            # Validate content for platform
            validation_result = await self._validate_content_for_platform(content_data, platform_config)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "platform": platform,
                    "error": "Validation failed",
                    "issues": validation_result["issues"]
                }
            
            # Adapt content for platform
            adapted_content = await self._adapt_content_for_platform(content_data, platform_config)
            
            # Simulate platform API call (replace with real API calls in production)
            success = await self._simulate_platform_upload(adapted_content, platform)
            
            if success:
                return {
                    "success": True,
                    "platform": platform,
                    "post_id": f"{platform}_{uuid.uuid4()}",
                    "post_url": f"https://{platform}.com/post/{uuid.uuid4()}",
                    "published_at": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "success": False,
                    "platform": platform,
                    "error": "Upload failed",
                    "message": "Platform API returned error"
                }
            
        except Exception as e:
            self.logger.error(f"Platform distribution failed for {platform}: {str(e)}")
            return {
                "success": False,
                "platform": platform,
                "error": "Platform distribution error",
                "message": str(e)
            }
    
    async def _validate_content_for_platform(self, content_data: Dict[str, Any], platform_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content meets platform requirements"""
        issues = []
        
        # Check title length
        title = content_data.get("title", "")
        max_title_length = platform_config["max_title_length"]
        if len(title) > max_title_length:
            issues.append(f"Title too long: {len(title)} chars (max: {max_title_length})")
        
        # Check description length
        description = content_data.get("description", "")
        max_description_length = platform_config["max_description_length"]
        if len(description) > max_description_length:
            issues.append(f"Description too long: {len(description)} chars (max: {max_description_length})")
        
        # Check file format
        file_path = content_data.get("file_path", "")
        if file_path:
            file_extension = file_path.split('.')[-1].lower()
            supported_formats = platform_config["supported_formats"]
            if file_extension not in supported_formats:
                issues.append(f"Unsupported format: {file_extension} (supported: {supported_formats})")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    async def _adapt_content_for_platform(self, content_data: Dict[str, Any], platform_config: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt content to platform specifications"""
        adapted_content = content_data.copy()
        
        # Trim title if too long
        title = adapted_content.get("title", "")
        max_title_length = platform_config["max_title_length"]
        if len(title) > max_title_length:
            adapted_content["title"] = title[:max_title_length-3] + "..."
        
        # Trim description if too long
        description = adapted_content.get("description", "")
        max_description_length = platform_config["max_description_length"]
        if len(description) > max_description_length:
            adapted_content["description"] = description[:max_description_length-3] + "..."
        
        return adapted_content
    
    async def _simulate_platform_upload(self, content: Dict[str, Any], platform: str) -> bool:
        """Simulate platform upload (replace with real API calls)"""
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Simulate 90% success rate
        import random
        return random.random() > 0.1
    
    async def get_distribution_status(self, distribution_id: str) -> Dict[str, Any]:
        """Get status of a content distribution"""
        if distribution_id not in self.distributions:
            return {
                "error": "Distribution not found",
                "distribution_id": distribution_id
            }
        
        return self.distributions[distribution_id]
    
    async def process_scheduled_distributions(self):
        """Process scheduled distributions that are due"""
        try:
            current_time = datetime.now(timezone.utc)
            due_distributions = []
            
            for distribution in self.scheduled_distributions:
                scheduled_time = datetime.fromisoformat(distribution["scheduled_for"])
                if scheduled_time <= current_time:
                    due_distributions.append(distribution)
            
            for distribution in due_distributions:
                # Remove from scheduled list
                self.scheduled_distributions.remove(distribution)
                
                # Process distribution
                content_data = {
                    "content_id": distribution["content_id"],
                    "title": distribution["title"],
                    "description": distribution["description"],
                    "content_type": distribution["content_type"],
                    "file_path": distribution["file_path"]
                }
                
                # Distribute to platforms
                distribution["status"] = DistributionStatus.PROCESSING.value
                
                for platform in distribution["platforms"]:
                    platform_result = await self._distribute_to_platform(content_data, platform)
                    distribution["platform_results"][platform] = platform_result
                
                # Update status
                successful_distributions = sum(1 for result in distribution["platform_results"].values() 
                                             if result.get("success", False))
                
                if successful_distributions == len(distribution["platforms"]):
                    distribution["status"] = DistributionStatus.PUBLISHED.value
                elif successful_distributions > 0:
                    distribution["status"] = DistributionStatus.PUBLISHED.value
                else:
                    distribution["status"] = DistributionStatus.FAILED.value
                
                distribution["completed_at"] = datetime.now(timezone.utc).isoformat()
                
                self.logger.info(f"Processed scheduled distribution {distribution['distribution_id']}")
            
            return len(due_distributions)
            
        except Exception as e:
            self.logger.error(f"Processing scheduled distributions failed: {str(e)}")
            return 0
    
    async def get_platform_analytics(self, platform: str, days: int = 30) -> Dict[str, Any]:
        """Get analytics for platform distributions"""
        try:
            platform_distributions = [
                dist for dist in self.distributions.values()
                if platform in dist.get("platform_results", {})
            ]
            
            successful_distributions = sum(
                1 for dist in platform_distributions
                if dist["platform_results"][platform].get("success", False)
            )
            
            return {
                "platform": platform,
                "period_days": days,
                "total_distributions": len(platform_distributions),
                "successful_distributions": successful_distributions,
                "success_rate": round((successful_distributions / max(1, len(platform_distributions))) * 100, 1),
                "analytics_generated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Platform analytics generation failed: {str(e)}")
            return {"error": "Analytics generation failed", "platform": platform}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "ContentDistributionService",
            "status": "healthy",
            "total_distributions": len(self.distributions),
            "scheduled_distributions": len(self.scheduled_distributions),
            "supported_platforms": len(self.platform_configs),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


__all__ = ['ContentDistributionService', 'PlatformType', 'DistributionStatus']