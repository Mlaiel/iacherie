"""
 Takedown Manager - IA Influencer Agent Surveillance Module
============================================================

Automated takedown notice management system for copyright infringement
enforcement across multiple digital platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)


class TakedownStatus(Enum):
    """Status of takedown requests"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


class TakedownType(Enum):
    """Types of takedown requests"""
    DMCA = "dmca"
    COPYRIGHT_CLAIM = "copyright_claim"
    TRADEMARK_VIOLATION = "trademark_violation"
    PLATFORM_ABUSE = "platform_abuse"
    MANUAL_REVIEW = "manual_review"


@dataclass
class TakedownRequest:
    """Takedown request structure"""
    request_id: str
    creator_id: str
    content_id: str
    infringement_url: str
    platform: str
    takedown_type: TakedownType
    status: TakedownStatus
    priority: str  # low, normal, high, critical
    
    # Request details
    infringement_description: str
    original_content_url: Optional[str] = None
    similarity_score: float = 0.0
    estimated_damage: float = 0.0
    
    # Contact information
    creator_contact: Dict[str, str] = field(default_factory=dict)
    legal_representative: Optional[Dict[str, str]] = None
    
    # Platform-specific data
    platform_specific_data: Dict[str, Any] = field(default_factory=dict)
    
    # Tracking information
    submission_attempts: int = 0
    max_attempts: int = 3
    last_attempt: Optional[datetime] = None
    response_received: Optional[str] = None
    platform_reference_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    deadline: Optional[datetime] = None
    
    success: bool = False
    error_message: Optional[str] = None


@dataclass
class TakedownTemplate:
    """Template for takedown notices"""
    template_id: str
    takedown_type: TakedownType
    platform: str
    title: str
    body_template: str
    required_fields: List[str]
    legal_basis: str
    language: str = "en"
    active: bool = True


class PlatformTakedownHandler:
    """Base class for platform-specific takedown handlers"""
    
    def __init__(self, platform: str, config: Dict[str, Any]):
        self.platform = platform
        self.config = config
        self.api_endpoint = config.get(f"{platform}_takedown_endpoint")
        self.api_credentials = config.get(f"{platform}_api_credentials", {})
    
    async def submit_takedown(self, request: TakedownRequest) -> bool:
        """Submit takedown request to platform"""
        # Default implementation for platforms without takedown support
        logging.warning(f"Takedown submission not implemented for {self.platform}")
        return False
    
    async def check_status(self, request: TakedownRequest) -> TakedownStatus:
        """Check status of submitted takedown request"""
        # Default implementation for platforms without status checking
        logging.warning(f"Takedown status checking not implemented for {self.platform}")
        return TakedownStatus.UNKNOWN
    
    async def format_request(self, request: TakedownRequest) -> Dict[str, Any]:
        """Format request for platform-specific submission"""
        # Default implementation providing basic request format
        return {
            "platform": self.platform,
            "content_url": request.content_url,
            "infringement_type": request.infringement_type,
            "description": request.description,
            "contact_info": request.contact_info
        }


class YouTubeTakedownHandler(PlatformTakedownHandler):
    """YouTube-specific takedown handler"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("youtube", config)
        self.copyright_match_tool_url = "https://www.youtube.com/copyright_match_tool"
    
    async def submit_takedown(self, request: TakedownRequest) -> bool:
        """Submit takedown request to YouTube"""



        try:
            # Format request for YouTube
            formatted_request = await self.format_request(request)
            
            # In production, this would use YouTube's Content ID API or
            # submit through the Copyright Match Tool
            await asyncio.sleep(1)  # Simulate API call
            
            # Simulate successful submission
            request.platform_reference_id = f"YT-{uuid.uuid4().hex[:8].upper()}"
            request.status = TakedownStatus.SUBMITTED
            request.last_attempt = datetime.now(timezone.utc)
            request.submission_attempts += 1
            
            logger.info(f"YouTube takedown submitted: {request.request_id}")
            return True
            
        except Exception as e:
            logger.error(f"YouTube takedown submission failed: {e}")
            request.error_message = str(e)
            request.status = TakedownStatus.FAILED
            return False
    
    async def check_status(self, request: TakedownRequest) -> TakedownStatus:
        """Check YouTube takedown status"""



        try:
            if not request.platform_reference_id:
                return TakedownStatus.PENDING
            
            # Simulate status check
            await asyncio.sleep(0.5)
            
            # Simulate status progression over time
            hours_since_submission = (datetime.now(timezone.utc) - request.created_at).total_seconds() / 3600
            
            if hours_since_submission < 1:
                return TakedownStatus.SUBMITTED
            elif hours_since_submission < 6:
                return TakedownStatus.IN_REVIEW
            elif hours_since_submission < 24:
                return TakedownStatus.ACKNOWLEDGED
            else:
                # Simulate 85% success rate
                import random
                if random.random() < 0.85:
                    return TakedownStatus.COMPLETED
                else:
                    return TakedownStatus.REJECTED
            
        except Exception as e:
            logger.error(f"YouTube status check failed: {e}")
            return TakedownStatus.FAILED
    
    async def format_request(self, request: TakedownRequest) -> Dict[str, Any]:
        """Format request for YouTube submission"""



        return {
            "video_url": request.infringement_url,
            "original_content_url": request.original_content_url,
            "infringement_type": "copyright",
            "description": request.infringement_description,
            "contact_email": request.creator_contact.get("email"),
            "contact_name": request.creator_contact.get("name"),
            "similarity_evidence": {
                "similarity_score": request.similarity_score,
                "analysis_details": request.platform_specific_data.get("analysis_details", {})
            }
        }


class TikTokTakedownHandler(PlatformTakedownHandler):
    """TikTok-specific takedown handler"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("tiktok", config)
    
    async def submit_takedown(self, request: TakedownRequest) -> bool:
        """Submit takedown request to TikTok"""



        try:
            formatted_request = await self.format_request(request)
            
            # Simulate TikTok API submission
            await asyncio.sleep(1)
            
            request.platform_reference_id = f"TT-{uuid.uuid4().hex[:8].upper()}"
            request.status = TakedownStatus.SUBMITTED
            request.last_attempt = datetime.now(timezone.utc)
            request.submission_attempts += 1
            
            logger.info(f"TikTok takedown submitted: {request.request_id}")
            return True
            
        except Exception as e:
            logger.error(f"TikTok takedown submission failed: {e}")
            request.error_message = str(e)
            request.status = TakedownStatus.FAILED
            return False
    
    async def check_status(self, request: TakedownRequest) -> TakedownStatus:
        """Check TikTok takedown status"""



        try:
            if not request.platform_reference_id:
                return TakedownStatus.PENDING
            
            await asyncio.sleep(0.5)
            
            # TikTok typically processes takedowns faster
            hours_since_submission = (datetime.now(timezone.utc) - request.created_at).total_seconds() / 3600
            
            if hours_since_submission < 0.5:
                return TakedownStatus.SUBMITTED
            elif hours_since_submission < 2:
                return TakedownStatus.IN_REVIEW
            elif hours_since_submission < 12:
                return TakedownStatus.ACKNOWLEDGED
            else:
                import random
                if random.random() < 0.90:  # TikTok has higher success rate
                    return TakedownStatus.COMPLETED
                else:
                    return TakedownStatus.REJECTED
            
        except Exception as e:
            logger.error(f"TikTok status check failed: {e}")
            return TakedownStatus.FAILED
    
    async def format_request(self, request: TakedownRequest) -> Dict[str, Any]:
        """Format request for TikTok submission"""



        return {
            "video_url": request.infringement_url,
            "original_content": request.original_content_url,
            "infringement_reason": request.infringement_description,
            "contact_info": request.creator_contact,
            "evidence": {
                "similarity_score": request.similarity_score,
                "damage_estimate": request.estimated_damage
            }
        }


class InstagramTakedownHandler(PlatformTakedownHandler):
    """Instagram-specific takedown handler"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("instagram", config)
    
    async def submit_takedown(self, request: TakedownRequest) -> bool:
        """Submit takedown request to Instagram"""



        try:
            formatted_request = await self.format_request(request)
            
            # Simulate Instagram/Meta API submission
            await asyncio.sleep(1)
            
            request.platform_reference_id = f"IG-{uuid.uuid4().hex[:8].upper()}"
            request.status = TakedownStatus.SUBMITTED
            request.last_attempt = datetime.now(timezone.utc)
            request.submission_attempts += 1
            
            logger.info(f"Instagram takedown submitted: {request.request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Instagram takedown submission failed: {e}")
            request.error_message = str(e)
            request.status = TakedownStatus.FAILED
            return False
    
    async def check_status(self, request: TakedownRequest) -> TakedownStatus:
        """Check Instagram takedown status"""



        try:
            if not request.platform_reference_id:
                return TakedownStatus.PENDING
            
            await asyncio.sleep(0.5)
            
            hours_since_submission = (datetime.now(timezone.utc) - request.created_at).total_seconds() / 3600
            
            if hours_since_submission < 2:
                return TakedownStatus.SUBMITTED
            elif hours_since_submission < 8:
                return TakedownStatus.IN_REVIEW
            elif hours_since_submission < 48:
                return TakedownStatus.ACKNOWLEDGED
            else:
                import random
                if random.random() < 0.80:
                    return TakedownStatus.COMPLETED
                else:
                    return TakedownStatus.REJECTED
            
        except Exception as e:
            logger.error(f"Instagram status check failed: {e}")
            return TakedownStatus.FAILED
    
    async def format_request(self, request: TakedownRequest) -> Dict[str, Any]:
        """Format request for Instagram submission"""



        return {
            "post_url": request.infringement_url,
            "original_content_url": request.original_content_url,
            "violation_type": "copyright",
            "description": request.infringement_description,
            "reporter_info": request.creator_contact,
            "evidence": {
                "similarity_analysis": request.platform_specific_data.get("analysis_details", {}),
                "estimated_impact": request.estimated_damage
            }
        }


class GenericTakedownHandler(PlatformTakedownHandler):
    """Generic takedown handler for other platforms"""
    
    def __init__(self, platform: str, config: Dict[str, Any]):
        super().__init__(platform, config)
    
    async def submit_takedown(self, request: TakedownRequest) -> bool:
        """Submit generic takedown request"""



        try:
            # Generic submission process
            formatted_request = await self.format_request(request)
            
            await asyncio.sleep(1)  # Simulate processing
            
            request.platform_reference_id = f"GEN-{uuid.uuid4().hex[:8].upper()}"
            request.status = TakedownStatus.SUBMITTED
            request.last_attempt = datetime.now(timezone.utc)
            request.submission_attempts += 1
            
            logger.info(f"Generic takedown submitted for {self.platform}: {request.request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Generic takedown submission failed for {self.platform}: {e}")
            request.error_message = str(e)
            request.status = TakedownStatus.FAILED
            return False
    
    async def check_status(self, request: TakedownRequest) -> TakedownStatus:
        """Check generic takedown status"""



        try:
            if not request.platform_reference_id:
                return TakedownStatus.PENDING
            
            await asyncio.sleep(0.5)
            
            # Generic platforms typically take longer
            hours_since_submission = (datetime.now(timezone.utc) - request.created_at).total_seconds() / 3600
            
            if hours_since_submission < 4:
                return TakedownStatus.SUBMITTED
            elif hours_since_submission < 24:
                return TakedownStatus.IN_REVIEW
            elif hours_since_submission < 72:
                return TakedownStatus.ACKNOWLEDGED
            else:
                import random
                if random.random() < 0.70:  # Lower success rate for generic platforms
                    return TakedownStatus.COMPLETED
                else:
                    return TakedownStatus.REJECTED
            
        except Exception as e:
            logger.error(f"Generic status check failed for {self.platform}: {e}")
            return TakedownStatus.FAILED
    
    async def format_request(self, request: TakedownRequest) -> Dict[str, Any]:
        """Format generic takedown request"""



        return {
            "platform": self.platform,
            "infringing_url": request.infringement_url,
            "original_url": request.original_content_url,
            "infringement_details": request.infringement_description,
            "contact": request.creator_contact,
            "evidence": request.platform_specific_data
        }


class TakedownManager:
    """
    Central takedown management system for automated copyright enforcement
    across multiple digital platforms
    """
    
    def __init__(self, surveillance_config):
        self.config = surveillance_config
        self.handlers: Dict[str, PlatformTakedownHandler] = {}
        self.active_requests: Dict[str, TakedownRequest] = {}
        self.templates: Dict[str, TakedownTemplate] = {}
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize takedown manager and platform handlers"""



        try:
            # Initialize platform-specific handlers
            handler_config = {
                "max_attempts": 3,
                "timeout": 30,
                "retry_delay": 3600  # 1 hour
            }
            
            # Add major platform handlers
            if "youtube" in self.config.enabled_platforms:
                self.handlers["youtube"] = YouTubeTakedownHandler(handler_config)
            
            if "tiktok" in self.config.enabled_platforms:
                self.handlers["tiktok"] = TikTokTakedownHandler(handler_config)
            
            if "instagram" in self.config.enabled_platforms:
                self.handlers["instagram"] = InstagramTakedownHandler(handler_config)
            
            # Add generic handlers for other platforms
            for platform in self.config.enabled_platforms:
                if platform not in self.handlers:
                    self.handlers[platform] = GenericTakedownHandler(platform, handler_config)
            
            # Load takedown templates
            await self._load_takedown_templates()
            
            self.initialized = True
            logger.info(f"Takedown Manager initialized with {len(self.handlers)} platform handlers")
            
        except Exception as e:
            logger.error(f"Failed to initialize Takedown Manager: {e}")
            raise
    
    async def create_takedown_request(
        self,
        creator_id: str,
        content_id: str,
        infringement_data: Any,
        priority: str = "normal"
    ) -> TakedownRequest:
        """Create a new takedown request from infringement data"""
        request_id = f"takedown_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Extract infringement information
        infringement_url = getattr(infringement_data, 'infringing_url', '')
        platform = getattr(infringement_data, 'platform', '')
        similarity_score = getattr(infringement_data, 'similarity_score', 0.0)
        estimated_damage = getattr(infringement_data, 'estimated_revenue_loss', 0.0)
        
        # Create takedown request
        request = TakedownRequest(
            request_id=request_id,
            creator_id=creator_id,
            content_id=content_id,
            infringement_url=infringement_url,
            platform=platform,
            takedown_type=TakedownType.DMCA,  # Default to DMCA
            status=TakedownStatus.PENDING,
            priority=priority,
            infringement_description=self._generate_infringement_description(infringement_data),
            similarity_score=similarity_score,
            estimated_damage=estimated_damage,
            creator_contact=self._get_creator_contact(creator_id),
            platform_specific_data=self._extract_platform_data(infringement_data)
        )
        
        # Set deadline based on priority
        request.deadline = self._calculate_deadline(priority)
        
        try:
            # Submit takedown request
            success = await self._submit_takedown_request(request)
            request.success = success
            
            # Store active request
            self.active_requests[request_id] = request
            
            logger.info(f"Takedown request created: {request_id} (success: {success})")
            
        except Exception as e:
            logger.error(f"Failed to create takedown request: {e}")
            request.error_message = str(e)
            request.success = False
        
        return request
    
    async def _submit_takedown_request(self, request: TakedownRequest) -> bool:
        """Submit takedown request using appropriate platform handler"""
        platform = request.platform.lower()
        
        if platform not in self.handlers:
            logger.warning(f"No handler available for platform: {platform}")
            return False
        
        handler = self.handlers[platform]
        
        try:
            success = await handler.submit_takedown(request)
            
            if success:
                logger.info(f"Takedown request submitted successfully: {request.request_id}")
            else:
                logger.warning(f"Takedown request submission failed: {request.request_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Takedown submission error: {e}")
            request.error_message = str(e)
            return False
    
    async def check_request_status(self, request_id: str) -> Optional[TakedownStatus]:
        """Check status of a specific takedown request"""
        if request_id not in self.active_requests:
            logger.warning(f"Takedown request not found: {request_id}")
            return None
        
        request = self.active_requests[request_id]
        
        if request.platform not in self.handlers:
            return request.status
        
        try:
            handler = self.handlers[request.platform]
            current_status = await handler.check_status(request)
            
            # Update request status if changed
            if current_status != request.status:
                request.status = current_status
                request.updated_at = datetime.now(timezone.utc)
                
                logger.info(f"Status updated for {request_id}: {current_status.value}")
            
            return current_status
            
        except Exception as e:
            logger.error(f"Status check failed for {request_id}: {e}")
            return request.status
    
    async def check_all_active_requests(self) -> Dict[str, TakedownStatus]:
        """Check status of all active takedown requests"""
        status_results = {}
        
        for request_id in list(self.active_requests.keys()):
            status = await self.check_request_status(request_id)
            if status:
                status_results[request_id] = status
                
                # Remove completed or failed requests from active list
                if status in [TakedownStatus.COMPLETED, TakedownStatus.FAILED, TakedownStatus.REJECTED]:
                    # Archive the request (in production, save to database)
                    archived_request = self.active_requests.pop(request_id)
                    logger.info(f"Archived completed request: {request_id} (status: {status.value})")
        
        return status_results
    
    async def retry_failed_requests(self) -> Dict[str, bool]:
        """Retry failed takedown requests that haven't exceeded max attempts"""
        retry_results = {}
        
        for request_id, request in list(self.active_requests.items()):
            if (request.status == TakedownStatus.FAILED and 
                request.submission_attempts < request.max_attempts):
                
                # Check if enough time has passed since last attempt
                if (request.last_attempt and 
                    datetime.now(timezone.utc) - request.last_attempt < timedelta(hours=1)):
                    continue
                
                logger.info(f"Retrying failed takedown request: {request_id}")
                
                # Reset status and retry
                request.status = TakedownStatus.PENDING
                request.error_message = None
                
                success = await self._submit_takedown_request(request)
                retry_results[request_id] = success
                
                if not success and request.submission_attempts >= request.max_attempts:
                    logger.error(f"Takedown request exhausted all attempts: {request_id}")
        
        return retry_results
    
    def _generate_infringement_description(self, infringement_data: Any) -> str:
        """Generate detailed infringement description"""
        infringement_type = getattr(infringement_data, 'infringement_type', 'unknown')
        similarity_score = getattr(infringement_data, 'similarity_score', 0.0)
        
        description = f"Copyright infringement detected - {infringement_type.value if hasattr(infringement_type, 'value') else infringement_type}. "
        description += f"Similarity analysis shows {similarity_score:.1%} match with original content. "
        description += "This unauthorized use violates copyright and causes economic harm to the creator."
        
        return description
    
    def _get_creator_contact(self, creator_id: str) -> Dict[str, str]:
        """Get creator contact information"""
        # In production, this would fetch from database
        return {
            "name": f"Creator {creator_id}",
            "email": f"creator_{creator_id}@example.com",
            "phone": "+1234567890"
        }
    
    def _extract_platform_data(self, infringement_data: Any) -> Dict[str, Any]:
        """Extract platform-specific data from infringement"""



        return {
            "detected_features": getattr(infringement_data, 'detected_features', {}),
            "uploader_info": getattr(infringement_data, 'uploader_info', {}),
            "engagement_metrics": getattr(infringement_data, 'engagement_metrics', {}),
            "analysis_details": {
                "confidence_score": getattr(infringement_data, 'confidence_score', 0.0),
                "risk_level": getattr(infringement_data, 'risk_level', 'unknown')
            }
        }
    
    def _calculate_deadline(self, priority: str) -> datetime:
        """Calculate deadline based on priority"""
        hours_map = {
            "critical": 4,
            "high": 24,
            "normal": 72,
            "low": 168  # 1 week
        }
        
        hours = hours_map.get(priority, 72)
        return datetime.now(timezone.utc) + timedelta(hours=hours)
    
    async def _load_takedown_templates(self) -> None:
        """Load takedown notice templates"""
        # Default DMCA template
        dmca_template = TakedownTemplate(
            template_id="dmca_standard",
            takedown_type=TakedownType.DMCA,
            platform="generic",
            title="DMCA Takedown Notice",
            body_template="""
I am writing to notify you of copyright infringement occurring on your platform.

Original Content: {original_content_url}
Infringing Content: {infringing_url}
Infringement Description: {infringement_description}

I have a good faith belief that the use of the copyrighted material described above is not authorized by the copyright owner, its agent, or the law.

I swear, under penalty of perjury, that the information in the notification is accurate and that I am the copyright owner or am authorized to act on behalf of the owner.

Contact Information:
{contact_name}
{contact_email}

Signature: {signature}
Date: {date}
            """.strip(),
            required_fields=["original_content_url", "infringing_url", "infringement_description", "contact_name", "contact_email"],
            legal_basis="Digital Millennium Copyright Act (DMCA)"
        )
        
        self.templates["dmca_standard"] = dmca_template
        logger.info("Takedown templates loaded")
    
    async def get_request_details(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a takedown request"""
        if request_id not in self.active_requests:
            return None
        
        request = self.active_requests[request_id]
        
        return {
            "request_id": request.request_id,
            "creator_id": request.creator_id,
            "content_id": request.content_id,
            "platform": request.platform,
            "status": request.status.value,
            "priority": request.priority,
            "infringement_url": request.infringement_url,
            "similarity_score": request.similarity_score,
            "estimated_damage": request.estimated_damage,
            "platform_reference_id": request.platform_reference_id,
            "submission_attempts": request.submission_attempts,
            "created_at": request.created_at.isoformat(),
            "updated_at": request.updated_at.isoformat(),
            "deadline": request.deadline.isoformat() if request.deadline else None,
            "error_message": request.error_message
        }
    
    async def get_takedown_statistics(self, creator_id: Optional[str] = None) -> Dict[str, Any]:
        """Get takedown statistics"""
        all_requests = list(self.active_requests.values())
        
        # Filter by creator if specified
        if creator_id:
            all_requests = [req for req in all_requests if req.creator_id == creator_id]
        
        # Calculate statistics
        total_requests = len(all_requests)
        status_counts = {}
        platform_counts = {}
        priority_counts = {}
        
        total_estimated_damage = 0.0
        successful_requests = 0
        
        for request in all_requests:
            # Status distribution
            status = request.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Platform distribution
            platform = request.platform
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            # Priority distribution
            priority = request.priority
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            # Financial metrics
            total_estimated_damage += request.estimated_damage
            
            if request.status == TakedownStatus.COMPLETED:
                successful_requests += 1
        
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "success_rate": round(success_rate, 2),
            "total_estimated_damage": round(total_estimated_damage, 2),
            "status_distribution": status_counts,
            "platform_distribution": platform_counts,
            "priority_distribution": priority_counts,
            "successful_requests": successful_requests,
            "active_requests": len([req for req in all_requests if req.status not in [
                TakedownStatus.COMPLETED, TakedownStatus.FAILED, TakedownStatus.REJECTED
            ]])
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on takedown manager"""
        health_status = {
            "manager": "healthy" if self.initialized else "unhealthy",
            "active_requests": len(self.active_requests),
            "handlers": {},
            "templates_loaded": len(self.templates),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        for platform, handler in self.handlers.items():
            health_status["handlers"][platform] = "ready"
        
        return health_status
    
    async def shutdown(self) -> None:
        """Gracefully shutdown takedown manager"""
        logger.info("Shutting down Takedown Manager")
        
        # Archive all active requests
        for request_id, request in self.active_requests.items():
            logger.info(f"Archiving active request: {request_id} (status: {request.status.value})")
        
        self.active_requests.clear()
        self.initialized = False
        logger.info("Takedown Manager shutdown complete")


# Export main components
__all__ = [
    "TakedownManager",
    "TakedownRequest",
    "TakedownTemplate",
    "TakedownStatus",
    "TakedownType",
    "PlatformTakedownHandler",
    "YouTubeTakedownHandler",
    "TikTokTakedownHandler",
    "InstagramTakedownHandler",
    "GenericTakedownHandler"
]
