"""Business Notification Processors - Specialized Business Logic Processors

Business-specific notification processors for IA Influencer Agent platform.
Each processor handles specialized business logic for different notification types
including content protection, collaboration matching, monetization opportunities,
SEO optimization, and distribution management.

Processors:
- ContentProtectionProcessor: Copyright infringement and rights management
- CollaborationProcessor: Partnership and collaboration opportunities  
- MonetizationProcessor: Revenue opportunities and financial alerts
- SEOProcessor: Search optimization and performance tracking
- DistributionProcessor: Multi-platform content distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime, timezone
from abc import ABC, abstractmethod

from .notification_models import NotificationRequest, NotificationContent
from .config import NotificationConfig
from .constants import BUSINESS_RULES, NOTIFICATION_TYPES

logger = logging.getLogger(__name__)


class BaseBusinessProcessor(ABC):
    """Base class for business notification processors."""
    
    def __init__(self, config: NotificationConfig):
        """Initialize processor with configuration."""
        self.config = config
        self.processor_name = self.__class__.__name__
        self.business_rules = BUSINESS_RULES
        self.processing_stats = {
            "total_processed": 0,
            "successful_processing": 0,
            "failed_processing": 0,
            "average_processing_time": 0.0
        }
        
        logger.info(f"{self.processor_name} initialized")
    
    @abstractmethod
    async def process_notification(self, request: NotificationRequest) -> NotificationRequest:
        """Process notification with business-specific logic."""
        pass
    
    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """Get list of supported notification types."""
        pass
    
    def _enhance_content_with_business_context(
        self,
        content: NotificationContent,
        business_context: Dict[str, Any]
    ) -> NotificationContent:
        """Enhance notification content with business context."""
        try:
            # Add business-specific variables to content
            if business_context:
                # Update message with business context variables
                message = content.message
                for key, value in business_context.items():
                    placeholder = f"{{{key}}}"
                    if placeholder in message:
                        message = message.replace(placeholder, str(value))
                
                content.message = message
                
                # Add business context to metadata
                if not content.metadata:
                    content.metadata = {}
                content.metadata.update(business_context)
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to enhance content with business context: {e}")
            return content
    
    def _apply_business_rules(
        self,
        request: NotificationRequest,
        rule_category: str
    ) -> NotificationRequest:
        """Apply business rules to notification request."""
        try:
            rules = self.business_rules.get(rule_category, {})
            
            # Apply priority rules
            if "priority" in rules:
                request.priority = rules["priority"]
            
            # Apply channel preferences
            if "notification_channels" in rules:
                request.channels = rules["notification_channels"]
            
            # Apply delivery timing
            if rules.get("immediate_delivery", False):
                request.delivery_time = "immediate"
            elif rules.get("time_sensitive", False):
                request.delivery_time = "priority"
            
            # Add business rule metadata
            if not request.metadata:
                request.metadata = {}
            request.metadata["applied_business_rules"] = rule_category
            request.metadata["rule_config"] = rules
            
            return request
            
        except Exception as e:
            logger.error(f"Failed to apply business rules: {e}")
            return request
    
    async def _update_processing_stats(self, processing_time: float, success: bool):
        """Update processor statistics."""
        self.processing_stats["total_processed"] += 1
        
        if success:
            self.processing_stats["successful_processing"] += 1
        else:
            self.processing_stats["failed_processing"] += 1
        
        # Update average processing time
        total = self.processing_stats["total_processed"]
        current_avg = self.processing_stats["average_processing_time"]
        self.processing_stats["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processor statistics."""
        return self.processing_stats.copy()


class ContentProtectionProcessor(BaseBusinessProcessor):
    """Processor for content protection and copyright notifications."""
    
    def get_supported_types(self) -> List[str]:
        """Get supported notification types."""
        return [
            "content_protection",
            "copyright_infringement", 
            "protection_alert",
            "rights_violation",
            "dmca_takedown",
            "content_fingerprint"
        ]
    
    async def process_notification(self, request: NotificationRequest) -> NotificationRequest:
        """Process content protection notification."""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Apply content protection business rules
            request = self._apply_business_rules(request, "content_protection")
            
            # Enhance with protection-specific context
            business_context = await self._get_protection_context(request)
            request.content = self._enhance_content_with_business_context(
                request.content, business_context
            )
            
            # Add protection-specific metadata
            request.metadata = request.metadata or {}
            request.metadata.update({
                "protection_category": "copyright",
                "urgency_level": "high",
                "legal_implications": True,
                "requires_documentation": True,
                "escalation_path": ["user", "legal_team", "platform_abuse"]
            })
            
            # Set high priority for protection alerts
            if request.notification_type in ["copyright_infringement", "rights_violation"]:
                request.priority = "urgent"
                request.urgency_score = 4.0
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_processing_stats(processing_time, True)
            
            logger.info(f"Content protection notification processed: {request.notification_id}")
            return request
            
        except Exception as e:
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_processing_stats(processing_time, False)
            logger.error(f"Content protection processing failed: {e}")
            return request
    
    async def _get_protection_context(self, request: NotificationRequest) -> Dict[str, Any]:
        """Get protection-specific context."""
        business_context = request.business_context or {}
        
        context = {
            "content_type": business_context.get("content_type", "unknown"),
            "platform": business_context.get("platform", "unknown"),
            "infringement_type": business_context.get("infringement_type", "copyright"),
            "severity_level": business_context.get("severity_level", "medium"),
            "evidence_available": business_context.get("evidence_available", True),
            "automated_detection": business_context.get("automated_detection", True),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "protection_score": business_context.get("protection_score", 85.0)
        }
        
        # Add creator-specific context
        if request.recipient.user_type:
            context["creator_type"] = request.recipient.user_type
            context["content_category"] = self._get_content_category_for_creator(request.recipient.user_type)
        
        return context
    
    def _get_content_category_for_creator(self, user_type: str) -> str:
        """Get content category based on creator type."""
        category_map = {
            "musician": "audio",
            "blogger": "text",
            "photographer": "image",
            "influencer": "mixed_media",
            "comedian": "video"
        }
        return category_map.get(user_type, "mixed_media")


class CollaborationProcessor(BaseBusinessProcessor):
    """Processor for collaboration and partnership notifications."""
    
    def get_supported_types(self) -> List[str]:
        """Get supported notification types."""
        return [
            "collaboration_match",
            "partnership_opportunity", 
            "collaboration_request",
            "partnership_proposal",
            "collaboration_accepted",
            "collaboration_completed",
            "match_recommendation"
        ]
    
    async def process_notification(self, request: NotificationRequest) -> NotificationRequest:
        """Process collaboration notification."""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Apply collaboration business rules
            request = self._apply_business_rules(request, "collaboration_matching")
            
            # Enhance with collaboration-specific context
            business_context = await self._get_collaboration_context(request)
            request.content = self._enhance_content_with_business_context(
                request.content, business_context
            )
            
            # Add collaboration-specific metadata
            request.metadata = request.metadata or {}
            request.metadata.update({
                "collaboration_category": "partnership",
                "match_quality": business_context.get("match_score", 75.0),
                "collaboration_type": business_context.get("collaboration_type", "content"),
                "estimated_value": business_context.get("estimated_value", 0),
                "requires_approval": True,
                "personalization_enabled": True
            })
            
            # Enable A/B testing for collaboration notifications
            if self.config.get("business_rules.collaboration_matching.ab_testing_enabled", True):
                request.metadata["ab_testing_enabled"] = True
                request.metadata["test_variant"] = self._get_ab_test_variant(request)
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_processing_stats(processing_time, True)
            
            logger.info(f"Collaboration notification processed: {request.notification_id}")
            return request
            
        except Exception as e:
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_processing_stats(processing_time, False)
            logger.error(f"Collaboration processing failed: {e}")
            return request
    
    async def _get_collaboration_context(self, request: NotificationRequest) -> Dict[str, Any]:
        """Get collaboration-specific context."""
        business_context = request.business_context or {}
        
        context = {
            "collaboration_type": business_context.get("collaboration_type", "content_creation"),
            "match_score": business_context.get("match_score", 75.0),
            "estimated_value": business_context.get("estimated_value", 0),
            "collaboration_duration": business_context.get("duration", "1 month"),
            "skills_match": business_context.get("skills_match", []),
            "audience_overlap": business_context.get("audience_overlap", 0.0),
            "geographic_compatibility": business_context.get("geographic_compatibility", True),
            "collaboration_history": business_context.get("previous_collaborations", 0),
            "success_probability": business_context.get("success_probability", 70.0)
        }
        
        # Add partner information if available
        if "partner_info" in business_context:
            partner_info = business_context["partner_info"]
            context.update({
                "partner_name": partner_info.get("name", "Unknown"),
                "partner_type": partner_info.get("user_type", "creator"),
                "partner_rating": partner_info.get("rating", 4.0),
                "partner_followers": partner_info.get("followers", 0)
            })
        
        return context
    
    def _get_ab_test_variant(self, request: NotificationRequest) -> str:
        """Get A/B test variant for collaboration notification."""
        # Simple hash-based variant assignment
        import hashlib
        hash_input = f"{request.recipient.user_id}_{request.notification_type}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        
        variants = ["standard", "detailed", "concise", "visual"]
        return variants[hash_value % len(variants)]


class MonetizationProcessor(BaseBusinessProcessor):
    """Processor for monetization and revenue notifications."""
    
    def get_supported_types(self) -> List[str]:
        """Get supported notification types."""
        return [
            "monetization_opportunity",
            "revenue_alert",
            "payment_notification", 
            "earnings_update",
            "payout_processed",
            "revenue_milestone",
            "pricing_optimization"
        ]
    
    async def process_notification(self, request: NotificationRequest) -> NotificationRequest:
        """Process monetization notification."""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Apply monetization business rules
            request = self._apply_business_rules(request, "monetization_opportunities")
            
            # Enhance with monetization-specific context
            business_context = await self._get_monetization_context(request)
            request.content = self._enhance_content_with_business_context(
                request.content, business_context
            )
            
            # Add monetization-specific metadata
            request.metadata = request.metadata or {}
            request.metadata.update({
                "monetization_category": "revenue_opportunity",
                "revenue_potential": business_context.get("revenue_potential", 0.0),
                "time_sensitivity": business_context.get("time_sensitive", True),
                "requires_action": True,
                "financial_impact": "positive",
                "tracking_enabled": True
            })
            
            # Set high priority for high-value opportunities
            revenue_potential = business_context.get("revenue_potential", 0.0)
            if revenue_potential >= 1000:
                request.priority = "high"
                request.urgency_score = 3.5
            elif revenue_potential >= 100:
                request.priority = "medium"
                request.urgency_score = 2.5
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_processing_stats(processing_time, True)
            
            logger.info(f"Monetization notification processed: {request.notification_id}")
            return request
            
        except Exception as e:
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_processing_stats(processing_time, False)
            logger.error(f"Monetization processing failed: {e}")
            return request
    
    async def _get_monetization_context(self, request: NotificationRequest) -> Dict[str, Any]:
        """Get monetization-specific context."""
        business_context = request.business_context or {}
        
        context = {
            "opportunity_type": business_context.get("opportunity_type", "direct"),
            "revenue_potential": business_context.get("revenue_potential", 0.0),
            "time_sensitive": business_context.get("time_sensitive", True),
            "platform": business_context.get("platform", "multiple"),
            "content_type": business_context.get("content_type", "mixed"),
            "audience_size": business_context.get("audience_size", 0),
            "engagement_rate": business_context.get("engagement_rate", 0.0),
            "success_rate": business_context.get("historical_success_rate", 75.0),
            "currency": business_context.get("currency", "USD"),
            "payment_terms": business_context.get("payment_terms", "30 days")
        }
        
        # Calculate opportunity score
        context["opportunity_score"] = self._calculate_opportunity_score(context)
        
        # Add creator-specific monetization context
        if request.recipient.user_type:
            context["creator_monetization_profile"] = self._get_creator_monetization_profile(
                request.recipient.user_type
            )
        
        return context
    
    def _calculate_opportunity_score(self, context: Dict[str, Any]) -> float:
        """Calculate monetization opportunity score."""
        try:
            score = 50.0  # Base score
            
            # Revenue potential factor (40% weight)
            revenue = context.get("revenue_potential", 0.0)
            if revenue >= 1000:
                score += 40
            elif revenue >= 500:
                score += 30
            elif revenue >= 100:
                score += 20
            elif revenue >= 50:
                score += 10
            
            # Success rate factor (30% weight)
            success_rate = context.get("success_rate", 75.0)
            score += (success_rate - 50) * 0.6  # Normalize around 50%
            
            # Audience factor (20% weight)
            audience = context.get("audience_size", 0)
            if audience >= 100000:
                score += 20
            elif audience >= 10000:
                score += 15
            elif audience >= 1000:
                score += 10
            elif audience >= 100:
                score += 5
            
            # Engagement factor (10% weight)
            engagement = context.get("engagement_rate", 0.0)
            if engagement >= 10:
                score += 10
            elif engagement >= 5:
                score += 7
            elif engagement >= 2:
                score += 5
            elif engagement >= 1:
                score += 3
            
            return min(100.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"Failed to calculate opportunity score: {e}")
            return 50.0
    
    def _get_creator_monetization_profile(self, user_type: str) -> Dict[str, Any]:
        """Get creator-specific monetization profile."""
        profiles = {
            "musician": {
                "primary_channels": ["streaming", "licensing", "merchandise"],
                "avg_revenue_per_opportunity": 250.0,
                "typical_conversion_rate": 15.0
            },
            "blogger": {
                "primary_channels": ["affiliate", "sponsored_content", "courses"],
                "avg_revenue_per_opportunity": 150.0,
                "typical_conversion_rate": 12.0
            },
            "photographer": {
                "primary_channels": ["stock_photos", "prints", "commissions"],
                "avg_revenue_per_opportunity": 300.0,
                "typical_conversion_rate": 20.0
            },
            "influencer": {
                "primary_channels": ["brand_partnerships", "affiliate", "products"],
                "avg_revenue_per_opportunity": 500.0,
                "typical_conversion_rate": 25.0
            },
            "comedian": {
                "primary_channels": ["shows", "merchandise", "sponsorships"],
                "avg_revenue_per_opportunity": 200.0,
                "typical_conversion_rate": 18.0
            }
        }
        
        return profiles.get(user_type, {
            "primary_channels": ["general"],
            "avg_revenue_per_opportunity": 100.0,
            "typical_conversion_rate": 10.0
        })


class SEOProcessor(BaseBusinessProcessor):
    """Processor for SEO optimization and performance notifications."""
    
    def get_supported_types(self) -> List[str]:
        """Get supported notification types."""
        return [
            "seo_optimization",
            "performance_alert",
            "ranking_update", 
            "analytics_report",
            "performance_milestone",
            "content_optimization",
            "keyword_ranking"
        ]
    
    async def process_notification(self, request: NotificationRequest) -> NotificationRequest:
        """Process SEO notification."""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Apply SEO business rules
            request = self._apply_business_rules(request, "seo_optimization")
            
            # Enhance with SEO-specific context
            business_context = await self._get_seo_context(request)
            request.content = self._enhance_content_with_business_context(
                request.content, business_context
            )
            
            # Add SEO-specific metadata
            request.metadata = request.metadata or {}
            request.metadata.update({
                "seo_category": "performance",
                "optimization_opportunity": business_context.get("optimization_score", 0.0),
                "performance_trend": business_context.get("trend", "stable"),
                "actionable_insights": True,
                "batch_processing": True,
                "analytics_enabled": True
            })
            
            # Batch processing for SEO notifications unless urgent
            if request.notification_type != "performance_alert":
                request.delivery_time = "batch"
                request.metadata["batch_category"] = "seo_updates"
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_processing_stats(processing_time, True)
            
            logger.info(f"SEO notification processed: {request.notification_id}")
            return request
            
        except Exception as e:
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_processing_stats(processing_time, False)
            logger.error(f"SEO processing failed: {e}")
            return request
    
    async def _get_seo_context(self, request: NotificationRequest) -> Dict[str, Any]:
        """Get SEO-specific context."""
        business_context = request.business_context or {}
        
        context = {
            "optimization_type": business_context.get("optimization_type", "general"),
            "current_ranking": business_context.get("current_ranking", 0),
            "previous_ranking": business_context.get("previous_ranking", 0),
            "keyword": business_context.get("keyword", ""),
            "search_volume": business_context.get("search_volume", 0),
            "competition_level": business_context.get("competition_level", "medium"),
            "optimization_score": business_context.get("optimization_score", 50.0),
            "improvement_potential": business_context.get("improvement_potential", 25.0),
            "trend": business_context.get("trend", "stable"),
            "time_period": business_context.get("time_period", "7 days")
        }
        
        # Calculate ranking change
        current = context.get("current_ranking", 0)
        previous = context.get("previous_ranking", 0)
        if current > 0 and previous > 0:
            context["ranking_change"] = previous - current  # Positive = improvement
            context["ranking_change_percentage"] = ((previous - current) / previous * 100)
        
        # Add recommendations based on creator type
        if request.recipient.user_type:
            context["recommendations"] = self._get_seo_recommendations(request.recipient.user_type)
        
        return context
    
    def _get_seo_recommendations(self, user_type: str) -> List[str]:
        """Get SEO recommendations based on creator type."""
        recommendations = {
            "musician": [
                "Optimize track titles with relevant keywords",
                "Use music genre tags effectively",
                "Create engaging album descriptions",
                "Build backlinks from music blogs"
            ],
            "blogger": [
                "Improve content structure with headers",
                "Optimize meta descriptions",
                "Use internal linking strategy",
                "Focus on long-tail keywords"
            ],
            "photographer": [
                "Optimize image alt text",
                "Use location-based keywords",
                "Create photography tutorials",
                "Build portfolio page SEO"
            ],
            "influencer": [
                "Optimize social media profiles",
                "Create SEO-friendly content titles",
                "Use trending hashtags strategically",
                "Build brand mention backlinks"
            ],
            "comedian": [
                "Optimize video titles and descriptions",
                "Use comedy-related keywords",
                "Create show listing pages",
                "Build entertainment industry backlinks"
            ]
        }
        
        return recommendations.get(user_type, [
            "Improve content quality and relevance",
            "Focus on user engagement metrics",
            "Build high-quality backlinks",
            "Optimize for mobile and speed"
        ])


class DistributionProcessor(BaseBusinessProcessor):
    """Processor for distribution and platform management notifications."""
    
    def get_supported_types(self) -> List[str]:
        """Get supported notification types."""
        return [
            "distribution_status",
            "platform_sync",
            "content_published",
            "distribution_complete", 
            "platform_error",
            "sync_failure",
            "multi_platform_update"
        ]
    
    async def process_notification(self, request: NotificationRequest) -> NotificationRequest:
        """Process distribution notification."""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Apply distribution business rules
            request = self._apply_business_rules(request, "distribution_status")
            
            # Enhance with distribution-specific context
            business_context = await self._get_distribution_context(request)
            request.content = self._enhance_content_with_business_context(
                request.content, business_context
            )
            
            # Add distribution-specific metadata
            request.metadata = request.metadata or {}
            request.metadata.update({
                "distribution_category": "platform_sync",
                "platforms_affected": business_context.get("platforms", []),
                "sync_status": business_context.get("status", "unknown"),
                "requires_user_action": business_context.get("requires_action", False),
                "batch_processing": True,
                "digest_eligible": True
            })
            
            # Escalate errors to higher priority
            if request.notification_type in ["platform_error", "sync_failure"]:
                request.priority = "medium"
                request.urgency_score = 2.5
                request.metadata["requires_user_action"] = True
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_processing_stats(processing_time, True)
            
            logger.info(f"Distribution notification processed: {request.notification_id}")
            return request
            
        except Exception as e:
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_processing_stats(processing_time, False)
            logger.error(f"Distribution processing failed: {e}")
            return request
    
    async def _get_distribution_context(self, request: NotificationRequest) -> Dict[str, Any]:
        """Get distribution-specific context."""
        business_context = request.business_context or {}
        
        context = {
            "distribution_type": business_context.get("distribution_type", "content"),
            "platforms": business_context.get("platforms", []),
            "status": business_context.get("status", "unknown"),
            "content_type": business_context.get("content_type", "mixed"),
            "successful_platforms": business_context.get("successful_platforms", []),
            "failed_platforms": business_context.get("failed_platforms", []),
            "total_platforms": business_context.get("total_platforms", 0),
            "distribution_time": business_context.get("distribution_time", 0),
            "requires_action": business_context.get("requires_action", False),
            "retry_available": business_context.get("retry_available", True)
        }
        
        # Calculate success rate
        successful = len(context.get("successful_platforms", []))
        total = context.get("total_platforms", 1)
        context["success_rate"] = (successful / total * 100) if total > 0 else 0
        
        # Add platform-specific information
        context["platform_details"] = self._get_platform_details(context.get("platforms", []))
        
        # Add next steps based on status
        context["next_steps"] = self._get_next_steps(context)
        
        return context
    
    def _get_platform_details(self, platforms: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get detailed information for each platform."""
        platform_info = {
            "youtube": {"name": "YouTube", "type": "video", "audience": "global"},
            "instagram": {"name": "Instagram", "type": "image_video", "audience": "social"},
            "tiktok": {"name": "TikTok", "type": "video", "audience": "young"},
            "spotify": {"name": "Spotify", "type": "audio", "audience": "music"},
            "soundcloud": {"name": "SoundCloud", "type": "audio", "audience": "independent"},
            "facebook": {"name": "Facebook", "type": "mixed", "audience": "broad"},
            "twitter": {"name": "Twitter", "type": "text_media", "audience": "news"},
            "linkedin": {"name": "LinkedIn", "type": "professional", "audience": "business"},
            "pinterest": {"name": "Pinterest", "type": "image", "audience": "lifestyle"},
            "twitch": {"name": "Twitch", "type": "live_video", "audience": "gaming"}
        }
        
        return {
            platform: platform_info.get(platform, {"name": platform.title(), "type": "unknown", "audience": "general"})
            for platform in platforms
        }
    
    def _get_next_steps(self, context: Dict[str, Any]) -> List[str]:
        """Get recommended next steps based on distribution status."""
        status = context.get("status", "unknown")
        failed_platforms = context.get("failed_platforms", [])
        requires_action = context.get("requires_action", False)
        
        steps = []
        
        if status == "failed":
            steps.extend([
                "Check platform API status",
                "Verify account credentials",
                "Review content compliance",
                "Retry distribution process"
            ])
        elif status == "partial":
            if failed_platforms:
                steps.extend([
                    f"Investigate failed platforms: {', '.join(failed_platforms)}",
                    "Check platform-specific requirements",
                    "Retry failed distributions"
                ])
        elif status == "success":
            steps.extend([
                "Monitor content performance",
                "Engage with audience responses",
                "Schedule follow-up content"
            ])
        
        if requires_action:
            steps.insert(0, "Immediate user action required")
        
        return steps[:5]  # Limit to top 5 steps
