"""Joint Campaign Manager - Multi-Creator Campaign Orchestration

Enterprise-grade joint campaign management system for coordinating multi-creator
collaborative campaigns. Handles campaign planning, execution, monitoring, and
optimization across multiple creators and platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
from pydantic import BaseModel, Field, validator


class CampaignType(str, Enum):
    """Types of joint campaigns"""
    CROSS_PROMOTION = "cross_promotion"
    COLLABORATIVE_CONTENT = "collaborative_content"
    SYNCHRONIZED_LAUNCH = "synchronized_launch"
    CONTEST_CHALLENGE = "contest_challenge"
    BRAND_PARTNERSHIP = "brand_partnership"
    CHARITY_FUNDRAISER = "charity_fundraiser"
    EDUCATIONAL_SERIES = "educational_series"
    VIRAL_CHALLENGE = "viral_challenge"


class CampaignStatus(str, Enum):
    """Campaign execution status"""
    PLANNING = "planning"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ANALYZING = "analyzing"


class CreatorRole(str, Enum):
    """Creator roles in joint campaigns"""
    LEAD_CREATOR = "lead_creator"
    CO_CREATOR = "co_creator"
    SUPPORTING_CREATOR = "supporting_creator"
    GUEST_CREATOR = "guest_creator"
    AMPLIFIER = "amplifier"


@dataclass
class CreatorParticipant:
    """Creator participating in joint campaign"""
    creator_id: str
    creator_name: str
    role: CreatorRole
    platforms: List[str]
    audience_size: Dict[str, int]
    engagement_rate: Dict[str, float]
    contribution_percentage: float
    content_requirements: List[str]
    scheduling_preferences: Dict[str, Any]
    revenue_share: float
    status: str = "invited"
    joined_at: Optional[datetime] = None


@dataclass
class CampaignObjective:
    """Campaign objective with metrics"""
    objective_name: str
    target_metric: str
    target_value: float
    current_value: float = 0.0
    weight: float = 1.0
    measurement_period: str = "campaign_duration"
    achieved: bool = False


@dataclass
class ContentDeliverable:
    """Content deliverable for campaign"""
    deliverable_id: str
    creator_id: str
    content_type: str
    platform: str
    requirements: Dict[str, Any]
    deadline: datetime
    status: str = "pending"
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class CampaignStrategy:
    """Comprehensive campaign strategy"""
    campaign_id: str
    campaign_name: str
    campaign_type: CampaignType
    description: str
    
    # Timeline
    start_date: datetime
    end_date: datetime
    preparation_period: timedelta
    
    # Participants
    participants: List[CreatorParticipant]
    target_audience: Dict[str, Any]
    
    # Objectives and KPIs
    objectives: List[CampaignObjective]
    success_metrics: Dict[str, float]
    
    # Content strategy
    content_themes: List[str]
    deliverables: List[ContentDeliverable]
    publishing_schedule: Dict[str, datetime]
    
    # Resource allocation
    budget_allocation: Dict[str, float]
    resource_requirements: Dict[str, Any]
    
    # Risk management
    risk_factors: List[str]
    mitigation_strategies: List[str]
    contingency_plans: List[str]
    
    # Analytics and optimization
    tracking_parameters: Dict[str, Any]
    optimization_triggers: List[str]
    
    # Status and metadata
    status: CampaignStatus = CampaignStatus.PLANNING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class JointCampaignManager:
    """Enterprise joint campaign management system"""
    
    def __init__(self,
                 max_campaign_participants: int = 10,
                 min_campaign_duration_days: int = 1,
                 max_campaign_duration_days: int = 90,
                 auto_optimization_enabled: bool = True):
        self.max_campaign_participants = max_campaign_participants
        self.min_campaign_duration_days = min_campaign_duration_days
        self.max_campaign_duration_days = max_campaign_duration_days
        self.auto_optimization_enabled = auto_optimization_enabled
        
        # Campaign management
        self.active_campaigns: Dict[str, CampaignStrategy] = {}
        self.campaign_history: Dict[str, CampaignStrategy] = {}
        self.campaign_templates: Dict[CampaignType, Dict[str, Any]] = {}
        
        # Analytics and optimization
        self.performance_analytics = self._initialize_analytics_engine()
        self.optimization_engine = self._initialize_optimization_engine()
        self.collaboration_matcher = self._initialize_collaboration_matcher()
        
        # Monitoring and alerts
        self.monitoring_active = True
        self.alert_thresholds = self._initialize_alert_thresholds()
        
        # Performance tracking
        self.manager_stats = {
            "total_campaigns_managed": 0,
            "successful_campaigns": 0,
            "average_campaign_performance": 0.0,
            "total_creators_coordinated": 0,
            "revenue_generated": 0.0
        }
        
        self.logger = logging.getLogger(__name__)
    
    def _initialize_analytics_engine(self) -> Dict[str, Any]:
        """Initialize campaign analytics engine"""
        return {
            "performance_tracker": {
                "metrics_collection": True,
                "real_time_monitoring": True,
                "predictive_analytics": True,
                "roi_calculation": True
            },
            "audience_analytics": {
                "overlap_analysis": True,
                "engagement_patterns": True,
                "demographic_insights": True,
                "behavior_tracking": True
            },
            "content_analytics": {
                "performance_comparison": True,
                "viral_potential_scoring": True,
                "content_optimization": True,
                "trend_analysis": True
            }
        }
    
    def _initialize_optimization_engine(self) -> Dict[str, Any]:
        """Initialize campaign optimization engine"""
        return {
            "real_time_optimization": {
                "enabled": True,
                "adjustment_threshold": 0.15,
                "optimization_frequency": "hourly"
            },
            "content_optimization": {
                "timing_adjustment": True,
                "hashtag_optimization": True,
                "cross_promotion_timing": True,
                "audience_targeting": True
            },
            "resource_optimization": {
                "budget_reallocation": True,
                "creator_workload_balancing": True,
                "platform_prioritization": True
            }
        }
    
    def _initialize_collaboration_matcher(self) -> Dict[str, Any]:
        """Initialize collaboration matching system"""
        return {
            "compatibility_algorithm": "advanced_ml_matching",
            "matching_factors": [
                "audience_overlap", "content_synergy", "engagement_compatibility",
                "brand_alignment", "scheduling_compatibility", "performance_history"
            ],
            "success_prediction_accuracy": 0.87
        }
    
    def _initialize_alert_thresholds(self) -> Dict[str, float]:
        """Initialize alerting thresholds"""
        return {
            "engagement_drop_threshold": 0.25,
            "audience_overlap_max": 0.70,
            "content_delivery_delay_hours": 24,
            "budget_overspend_threshold": 0.10,
            "performance_underperformance_threshold": 0.20
        }
    
    async def create_joint_campaign(self,
                                   campaign_config: Dict[str, Any],
                                   creator_list: List[Dict[str, Any]]) -> CampaignStrategy:
        """Create a new joint campaign with multiple creators"""
        
        try:
            # Validate campaign configuration
            await self._validate_campaign_config(campaign_config)
            
            # Process and validate creators
            participants = await self._process_creator_participants(creator_list)
            
            # Generate campaign ID
            campaign_id = f"campaign_{int(time.time())}_{len(self.active_campaigns)}"
            
            # Analyze creator compatibility
            compatibility_analysis = await self._analyze_creator_compatibility(participants)
            
            # Generate campaign objectives
            objectives = await self._generate_campaign_objectives(
                campaign_config, participants, compatibility_analysis
            )
            
            # Create content deliverables
            deliverables = await self._create_content_deliverables(
                campaign_config, participants
            )
            
            # Calculate resource allocation
            budget_allocation = await self._calculate_budget_allocation(
                campaign_config, participants
            )
            
            # Generate publishing schedule
            publishing_schedule = await self._generate_publishing_schedule(
                campaign_config, participants, deliverables
            )
            
            # Create campaign strategy
            strategy = CampaignStrategy(
                campaign_id=campaign_id,
                campaign_name=campaign_config["name"],
                campaign_type=CampaignType(campaign_config["type"]),
                description=campaign_config["description"],
                start_date=datetime.fromisoformat(campaign_config["start_date"]),
                end_date=datetime.fromisoformat(campaign_config["end_date"]),
                preparation_period=timedelta(days=campaign_config.get("preparation_days", 7)),
                participants=participants,
                target_audience=campaign_config.get("target_audience", {}),
                objectives=objectives,
                success_metrics=campaign_config.get("success_metrics", {}),
                content_themes=campaign_config.get("content_themes", []),
                deliverables=deliverables,
                publishing_schedule=publishing_schedule,
                budget_allocation=budget_allocation,
                resource_requirements=campaign_config.get("resource_requirements", {}),
                risk_factors=await self._identify_risk_factors(participants, campaign_config),
                mitigation_strategies=await self._generate_mitigation_strategies(participants),
                contingency_plans=await self._create_contingency_plans(campaign_config),
                tracking_parameters=self._setup_tracking_parameters(campaign_config),
                optimization_triggers=self._setup_optimization_triggers(campaign_config)
            )
            
            # Store campaign
            self.active_campaigns[campaign_id] = strategy
            
            # Initialize monitoring
            await self._initialize_campaign_monitoring(campaign_id)
            
            # Send invitations to creators
            await self._send_creator_invitations(strategy)
            
            # Log campaign creation
            self.logger.info(f"Created joint campaign {campaign_id} with {len(participants)} creators")
            self._update_manager_stats("campaign_created", participants)
            
            return strategy
            
        except Exception as e:
            self.logger.error(f"Failed to create joint campaign: {e}")
            raise
    
    async def _validate_campaign_config(self, config: Dict[str, Any]):
        """Validate campaign configuration"""
        required_fields = ["name", "type", "description", "start_date", "end_date"]
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate campaign type
        if config["type"] not in [t.value for t in CampaignType]:
            raise ValueError(f"Invalid campaign type: {config['type']}")
        
        # Validate dates
        start_date = datetime.fromisoformat(config["start_date"])
        end_date = datetime.fromisoformat(config["end_date"])
        
        if start_date >= end_date:
            raise ValueError("End date must be after start date")
        
        duration = (end_date - start_date).days
        if duration < self.min_campaign_duration_days:
            raise ValueError(f"Campaign duration must be at least {self.min_campaign_duration_days} days")
        
        if duration > self.max_campaign_duration_days:
            raise ValueError(f"Campaign duration cannot exceed {self.max_campaign_duration_days} days")
    
    async def _process_creator_participants(self, creator_list: List[Dict[str, Any]]) -> List[CreatorParticipant]:
        """Process and validate creator participants"""
        if len(creator_list) > self.max_campaign_participants:
            raise ValueError(f"Too many participants. Maximum allowed: {self.max_campaign_participants}")
        
        participants = []
        total_contribution = 0.0
        
        for creator_data in creator_list:
            participant = CreatorParticipant(
                creator_id=creator_data["creator_id"],
                creator_name=creator_data["name"],
                role=CreatorRole(creator_data.get("role", "co_creator")),
                platforms=creator_data["platforms"],
                audience_size=creator_data.get("audience_size", {}),
                engagement_rate=creator_data.get("engagement_rate", {}),
                contribution_percentage=creator_data.get("contribution_percentage", 0.0),
                content_requirements=creator_data.get("content_requirements", []),
                scheduling_preferences=creator_data.get("scheduling_preferences", {}),
                revenue_share=creator_data.get("revenue_share", 0.0)
            )
            
            participants.append(participant)
            total_contribution += participant.contribution_percentage
        
        # Validate contribution percentages
        if abs(total_contribution - 100.0) > 0.01:
            # Auto-balance if not specified
            if total_contribution == 0.0:
                equal_share = 100.0 / len(participants)
                for participant in participants:
                    participant.contribution_percentage = equal_share
            else:
                raise ValueError("Contribution percentages must sum to 100%")
        
        return participants
    
    async def _analyze_creator_compatibility(self, participants: List[CreatorParticipant]) -> Dict[str, Any]:
        """Analyze compatibility between creators"""
        compatibility_analysis = {
            "overall_compatibility_score": 0.0,
            "audience_overlap_analysis": {},
            "content_synergy_score": 0.0,
            "scheduling_compatibility": 0.0,
            "engagement_compatibility": 0.0,
            "potential_conflicts": [],
            "optimization_opportunities": []
        }
        
        # Calculate audience overlap
        overlap_scores = []
        for i, creator1 in enumerate(participants):
            for j, creator2 in enumerate(participants[i+1:], i+1):
                overlap = await self._calculate_audience_overlap(creator1, creator2)
                overlap_scores.append(overlap)
                
                key = f"{creator1.creator_name}_{creator2.creator_name}"
                compatibility_analysis["audience_overlap_analysis"][key] = overlap
                
                # Check for excessive overlap
                if overlap > self.alert_thresholds["audience_overlap_max"]:
                    compatibility_analysis["potential_conflicts"].append(
                        f"High audience overlap ({overlap:.2%}) between {creator1.creator_name} and {creator2.creator_name}"
                    )
        
        # Calculate overall compatibility scores
        compatibility_analysis["overall_compatibility_score"] = np.mean(overlap_scores) if overlap_scores else 0.0
        compatibility_analysis["content_synergy_score"] = await self._calculate_content_synergy(participants)
        compatibility_analysis["scheduling_compatibility"] = self._calculate_scheduling_compatibility(participants)
        compatibility_analysis["engagement_compatibility"] = self._calculate_engagement_compatibility(participants)
        
        # Identify optimization opportunities
        if compatibility_analysis["overall_compatibility_score"] < 0.6:
            compatibility_analysis["optimization_opportunities"].append(
                "Consider creator substitution to improve compatibility"
            )
        
        if compatibility_analysis["content_synergy_score"] > 0.8:
            compatibility_analysis["optimization_opportunities"].append(
                "High content synergy detected - leverage for viral potential"
            )
        
        return compatibility_analysis
    
    async def _calculate_audience_overlap(self, creator1: CreatorParticipant, creator2: CreatorParticipant) -> float:
        """Calculate audience overlap between two creators"""
        # Simplified overlap calculation based on platforms and audience size
        common_platforms = set(creator1.platforms) & set(creator2.platforms)
        
        if not common_platforms:
            return 0.0
        
        # Calculate weighted overlap based on audience sizes
        overlap_scores = []
        for platform in common_platforms:
            size1 = creator1.audience_size.get(platform, 0)
            size2 = creator2.audience_size.get(platform, 0)
            
            if size1 > 0 and size2 > 0:
                # Estimate overlap based on platform characteristics
                # In production, this would use actual audience data
                platform_overlap_rates = {
                    "youtube": 0.15,
                    "instagram": 0.25,
                    "tiktok": 0.20,
                    "twitter": 0.30,
                    "facebook": 0.35
                }
                
                base_overlap = platform_overlap_rates.get(platform.lower(), 0.20)
                
                # Adjust based on audience size similarity
                size_ratio = min(size1, size2) / max(size1, size2)
                adjusted_overlap = base_overlap * size_ratio
                
                overlap_scores.append(adjusted_overlap)
        
        return np.mean(overlap_scores) if overlap_scores else 0.0
    
    async def _calculate_content_synergy(self, participants: List[CreatorParticipant]) -> float:
        """Calculate content synergy score between creators"""
        # Simplified synergy calculation based on content requirements
        if len(participants) < 2:
            return 1.0
        
        synergy_factors = []
        
        for i, creator1 in enumerate(participants):
            for creator2 in participants[i+1:]:
                # Calculate requirement overlap
                req1 = set(creator1.content_requirements)
                req2 = set(creator2.content_requirements)
                
                if req1 or req2:
                    overlap = len(req1 & req2) / len(req1 | req2)
                    synergy_factors.append(overlap)
        
        return np.mean(synergy_factors) if synergy_factors else 0.5
    
    def _calculate_scheduling_compatibility(self, participants: List[CreatorParticipant]) -> float:
        """Calculate scheduling compatibility score"""
        # Simplified scheduling compatibility based on preferences
        timezone_compatibility = 0.8  # Assume good timezone compatibility
        availability_overlap = 0.7     # Assume reasonable availability overlap
        
        return (timezone_compatibility + availability_overlap) / 2
    
    def _calculate_engagement_compatibility(self, participants: List[CreatorParticipant]) -> float:
        """Calculate engagement rate compatibility"""
        if len(participants) < 2:
            return 1.0
        
        # Calculate engagement rate variance across creators
        engagement_rates = []
        for participant in participants:
            avg_engagement = np.mean(list(participant.engagement_rate.values())) if participant.engagement_rate else 0.05
            engagement_rates.append(avg_engagement)
        
        if not engagement_rates:
            return 0.5
        
        # Lower variance = higher compatibility
        variance = np.var(engagement_rates)
        compatibility = max(0.0, 1.0 - variance * 10)  # Scale variance to 0-1
        
        return min(compatibility, 1.0)
    
    async def _generate_campaign_objectives(self,
                                          config: Dict[str, Any],
                                          participants: List[CreatorParticipant],
                                          compatibility: Dict[str, Any]) -> List[CampaignObjective]:
        """Generate campaign objectives based on configuration and participants"""
        objectives = []
        
        # Calculate potential reach
        total_reach = sum(
            sum(participant.audience_size.values()) 
            for participant in participants
        )
        
        # Adjust for audience overlap
        overlap_factor = 1 - (compatibility["overall_compatibility_score"] * 0.3)
        adjusted_reach = total_reach * overlap_factor
        
        # Default objectives based on campaign type
        campaign_type = CampaignType(config["type"])
        
        if campaign_type == CampaignType.CROSS_PROMOTION:
            objectives.extend([
                CampaignObjective(
                    objective_name="Cross-Platform Reach",
                    target_metric="total_reach",
                    target_value=adjusted_reach * 0.8,
                    weight=1.0
                ),
                CampaignObjective(
                    objective_name="Engagement Rate",
                    target_metric="avg_engagement_rate",
                    target_value=0.05,
                    weight=0.8
                )
            ])
        
        elif campaign_type == CampaignType.VIRAL_CHALLENGE:
            objectives.extend([
                CampaignObjective(
                    objective_name="Viral Spread",
                    target_metric="share_rate",
                    target_value=0.15,
                    weight=1.0
                ),
                CampaignObjective(
                    objective_name="User Generated Content",
                    target_metric="ugc_count",
                    target_value=1000,
                    weight=0.9
                )
            ])
        
        elif campaign_type == CampaignType.BRAND_PARTNERSHIP:
            objectives.extend([
                CampaignObjective(
                    objective_name="Conversion Rate",
                    target_metric="conversion_rate",
                    target_value=0.03,
                    weight=1.0
                ),
                CampaignObjective(
                    objective_name="Brand Awareness",
                    target_metric="brand_mention_rate",
                    target_value=0.20,
                    weight=0.7
                )
            ])
        
        # Add custom objectives from config
        custom_objectives = config.get("custom_objectives", [])
        for obj_config in custom_objectives:
            objectives.append(CampaignObjective(
                objective_name=obj_config["name"],
                target_metric=obj_config["metric"],
                target_value=obj_config["target"],
                weight=obj_config.get("weight", 1.0)
            ))
        
        return objectives
    
    async def _create_content_deliverables(self,
                                         config: Dict[str, Any],
                                         participants: List[CreatorParticipant]) -> List[ContentDeliverable]:
        """Create content deliverables for campaign"""
        deliverables = []
        deliverable_id_counter = 1
        
        campaign_start = datetime.fromisoformat(config["start_date"])
        campaign_end = datetime.fromisoformat(config["end_date"])
        
        # Create deliverables for each participant
        for participant in participants:
            for platform in participant.platforms:
                # Determine content requirements based on campaign type and role
                content_types = self._determine_content_types(
                    CampaignType(config["type"]), participant.role, platform
                )
                
                for content_type in content_types:
                    # Calculate deadline based on publishing schedule
                    deadline = self._calculate_content_deadline(
                        campaign_start, campaign_end, content_type
                    )
                    
                    deliverable = ContentDeliverable(
                        deliverable_id=f"deliv_{deliverable_id_counter:04d}",
                        creator_id=participant.creator_id,
                        content_type=content_type,
                        platform=platform,
                        requirements=self._generate_content_requirements(
                            content_type, platform, config
                        ),
                        deadline=deadline
                    )
                    
                    deliverables.append(deliverable)
                    deliverable_id_counter += 1
        
        return deliverables
    
    def _determine_content_types(self, 
                               campaign_type: CampaignType, 
                               creator_role: CreatorRole, 
                               platform: str) -> List[str]:
        """Determine required content types for creator role and platform"""
        
        base_content_types = {
            CampaignType.CROSS_PROMOTION: ["post", "story"],
            CampaignType.COLLABORATIVE_CONTENT: ["collaborative_post", "behind_scenes"],
            CampaignType.VIRAL_CHALLENGE: ["challenge_video", "reaction_video"],
            CampaignType.BRAND_PARTNERSHIP: ["sponsored_post", "review_video"],
            CampaignType.EDUCATIONAL_SERIES: ["tutorial_video", "educational_post"]
        }
        
        role_multipliers = {
            CreatorRole.LEAD_CREATOR: 1.5,
            CreatorRole.CO_CREATOR: 1.0,
            CreatorRole.SUPPORTING_CREATOR: 0.7,
            CreatorRole.AMPLIFIER: 0.5
        }
        
        platform_content_types = {
            "youtube": ["video", "short", "community_post"],
            "instagram": ["post", "story", "reel", "igtv"],
            "tiktok": ["video", "duet", "trend_participation"],
            "twitter": ["tweet", "thread", "space"],
            "facebook": ["post", "story", "live_video"]
        }
        
        # Get base content types for campaign
        content_types = base_content_types.get(campaign_type, ["post"])
        
        # Filter by platform capabilities
        platform_types = platform_content_types.get(platform.lower(), ["post"])
        filtered_types = [ct for ct in content_types if any(pt in ct for pt in platform_types)]
        
        # Adjust based on creator role
        role_multiplier = role_multipliers.get(creator_role, 1.0)
        final_count = max(1, int(len(filtered_types) * role_multiplier))
        
        return filtered_types[:final_count]
    
    def _calculate_content_deadline(self, 
                                  campaign_start: datetime, 
                                  campaign_end: datetime, 
                                  content_type: str) -> datetime:
        """Calculate content submission deadline"""
        
        # Content type specific lead times (days before campaign start)
        lead_times = {
            "video": 5,
            "collaborative_post": 3,
            "post": 2,
            "story": 1
        }
        
        # Find applicable lead time
        lead_time_days = 2  # Default
        for content_key, days in lead_times.items():
            if content_key in content_type.lower():
                lead_time_days = days
                break
        
        return campaign_start - timedelta(days=lead_time_days)
    
    def _generate_content_requirements(self, 
                                     content_type: str, 
                                     platform: str, 
                                     config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content requirements for specific content type and platform"""
        
        base_requirements = {
            "content_themes": config.get("content_themes", []),
            "hashtags": config.get("required_hashtags", []),
            "mentions": config.get("required_mentions", []),
            "call_to_action": config.get("call_to_action", ""),
            "brand_guidelines": config.get("brand_guidelines", {})
        }
        
        # Platform-specific requirements
        platform_requirements = {
            "youtube": {
                "min_duration_seconds": 60 if "video" in content_type else 0,
                "thumbnail_required": "video" in content_type,
                "description_min_length": 100
            },
            "instagram": {
                "aspect_ratios": ["1:1", "4:5", "9:16"],
                "caption_max_length": 2200,
                "hashtag_limit": 30
            },
            "tiktok": {
                "max_duration_seconds": 60,
                "trending_sounds_encouraged": True,
                "hashtag_limit": 10
            }
        }
        
        # Merge requirements
        requirements = base_requirements.copy()
        if platform.lower() in platform_requirements:
            requirements.update(platform_requirements[platform.lower()])
        
        return requirements
    
    async def _calculate_budget_allocation(self,
                                         config: Dict[str, Any],
                                         participants: List[CreatorParticipant]) -> Dict[str, float]:
        """Calculate budget allocation across participants and activities"""
        
        total_budget = config.get("total_budget", 0.0)
        
        allocation = {
            "total_budget": total_budget,
            "creator_payments": {},
            "platform_advertising": {},
            "content_production": {},
            "management_fee": total_budget * 0.10,  # 10% management fee
            "contingency": total_budget * 0.15      # 15% contingency
        }
        
        # Calculate creator payments based on contribution and audience size
        available_for_creators = total_budget * 0.60  # 60% for creator payments
        
        total_weighted_contribution = sum(
            participant.contribution_percentage * sum(participant.audience_size.values())
            for participant in participants
        )
        
        if total_weighted_contribution > 0:
            for participant in participants:
                weighted_contribution = (
                    participant.contribution_percentage * 
                    sum(participant.audience_size.values())
                )
                
                creator_payment = (
                    (weighted_contribution / total_weighted_contribution) * 
                    available_for_creators
                )
                
                allocation["creator_payments"][participant.creator_id] = creator_payment
        
        # Platform advertising allocation (15% of budget)
        advertising_budget = total_budget * 0.15
        platform_audiences = {}
        
        for participant in participants:
            for platform, audience_size in participant.audience_size.items():
                platform_audiences[platform] = platform_audiences.get(platform, 0) + audience_size
        
        total_platform_audience = sum(platform_audiences.values())
        if total_platform_audience > 0:
            for platform, audience_size in platform_audiences.items():
                platform_allocation = (audience_size / total_platform_audience) * advertising_budget
                allocation["platform_advertising"][platform] = platform_allocation
        
        return allocation
    
    async def _generate_publishing_schedule(self,
                                          config: Dict[str, Any],
                                          participants: List[CreatorParticipant],
                                          deliverables: List[ContentDeliverable]) -> Dict[str, datetime]:
        """Generate optimized publishing schedule"""
        
        campaign_start = datetime.fromisoformat(config["start_date"])
        campaign_end = datetime.fromisoformat(config["end_date"])
        campaign_duration = (campaign_end - campaign_start).days
        
        schedule = {}
        
        # Group deliverables by content type and platform
        content_groups = {}
        for deliverable in deliverables:
            key = f"{deliverable.content_type}_{deliverable.platform}"
            if key not in content_groups:
                content_groups[key] = []
            content_groups[key].append(deliverable)
        
        # Schedule content with optimal timing
        for group_key, group_deliverables in content_groups.items():
            content_type, platform = group_key.split('_', 1)
            
            # Determine optimal posting times for platform
            optimal_times = self._get_optimal_posting_times(platform)
            
            # Distribute content across campaign duration
            posts_count = len(group_deliverables)
            if posts_count == 1:
                # Single post - use campaign start + optimal time
                optimal_hour = optimal_times[0] if optimal_times else 12
                publish_time = campaign_start.replace(hour=optimal_hour, minute=0, second=0)
                schedule[group_deliverables[0].deliverable_id] = publish_time
            else:
                # Multiple posts - distribute evenly with optimal timing
                interval_days = max(1, campaign_duration // posts_count)
                
                for i, deliverable in enumerate(group_deliverables):
                    days_offset = i * interval_days
                    optimal_hour = optimal_times[i % len(optimal_times)] if optimal_times else 12
                    
                    publish_time = campaign_start + timedelta(days=days_offset)
                    publish_time = publish_time.replace(hour=optimal_hour, minute=0, second=0)
                    
                    schedule[deliverable.deliverable_id] = publish_time
        
        return schedule
    
    def _get_optimal_posting_times(self, platform: str) -> List[int]:
        """Get optimal posting hours for platform"""
        
        optimal_times = {
            "youtube": [14, 20, 22],      # 2PM, 8PM, 10PM
            "instagram": [11, 13, 17, 19], # 11AM, 1PM, 5PM, 7PM
            "tiktok": [6, 10, 18, 21],     # 6AM, 10AM, 6PM, 9PM
            "twitter": [9, 12, 15, 18],    # 9AM, 12PM, 3PM, 6PM
            "facebook": [9, 13, 15]        # 9AM, 1PM, 3PM
        }
        
        return optimal_times.get(platform.lower(), [12, 18])  # Default to noon and 6PM
    
    async def monitor_campaign_progress(self, campaign_id: str) -> Dict[str, Any]:
        """Monitor and analyze campaign progress"""
        
        if campaign_id not in self.active_campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        campaign = self.active_campaigns[campaign_id]
        
        # Collect current metrics
        current_metrics = await self._collect_campaign_metrics(campaign)
        
        # Analyze progress against objectives
        objective_progress = self._analyze_objective_progress(campaign, current_metrics)
        
        # Check for optimization opportunities
        optimizations = await self._identify_optimization_opportunities(campaign, current_metrics)
        
        # Generate alerts if needed
        alerts = self._generate_campaign_alerts(campaign, current_metrics)
        
        # Update campaign status if needed
        await self._update_campaign_status(campaign, current_metrics)
        
        progress_report = {
            "campaign_id": campaign_id,
            "campaign_name": campaign.campaign_name,
            "status": campaign.status.value,
            "progress_percentage": self._calculate_overall_progress(campaign),
            "current_metrics": current_metrics,
            "objective_progress": objective_progress,
            "optimization_opportunities": optimizations,
            "alerts": alerts,
            "next_milestones": self._get_next_milestones(campaign),
            "recommendations": await self._generate_recommendations(campaign, current_metrics)
        }
        
        return progress_report
    
    async def _collect_campaign_metrics(self, campaign: CampaignStrategy) -> Dict[str, float]:
        """Collect current campaign performance metrics"""
        
        # In a real implementation, this would collect actual metrics from platforms
        # For demonstration, using simulated metrics
        
        metrics = {
            "total_reach": 0,
            "total_impressions": 0,
            "total_engagement": 0,
            "avg_engagement_rate": 0.0,
            "click_through_rate": 0.0,
            "conversion_rate": 0.0,
            "share_rate": 0.0,
            "sentiment_score": 0.0,
            "brand_mention_count": 0,
            "ugc_count": 0,
            "revenue_generated": 0.0
        }
        
        # Simulate metrics based on campaign progress and participant performance
        days_running = (datetime.now(timezone.utc) - campaign.start_date).days
        campaign_duration = (campaign.end_date - campaign.start_date).days
        
        if days_running > 0:
            progress_ratio = min(days_running / campaign_duration, 1.0)
            
            # Calculate total potential reach
            total_audience = sum(
                sum(participant.audience_size.values())
                for participant in campaign.participants
            )
            
            # Simulate progressive metrics accumulation
            metrics["total_reach"] = int(total_audience * progress_ratio * 0.6)  # 60% reach rate
            metrics["total_impressions"] = int(metrics["total_reach"] * 1.8)     # 1.8x impression multiplier
            metrics["total_engagement"] = int(metrics["total_reach"] * 0.05)     # 5% engagement rate
            metrics["avg_engagement_rate"] = 0.05
            metrics["click_through_rate"] = 0.02
            metrics["conversion_rate"] = 0.01
            metrics["share_rate"] = 0.08
            metrics["sentiment_score"] = 0.75
            metrics["brand_mention_count"] = int(metrics["total_reach"] * 0.01)
            metrics["ugc_count"] = int(metrics["total_engagement"] * 0.1)
            metrics["revenue_generated"] = metrics["total_reach"] * 0.001  # $0.001 per reach
        
        return metrics
    
    def _analyze_objective_progress(self, 
                                  campaign: CampaignStrategy, 
                                  current_metrics: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """Analyze progress against campaign objectives"""
        
        progress = {}
        
        for objective in campaign.objectives:
            current_value = current_metrics.get(objective.target_metric, 0.0)
            progress_percentage = (current_value / objective.target_value) * 100 if objective.target_value > 0 else 0.0
            
            # Determine status
            if progress_percentage >= 100:
                status = "achieved"
                objective.achieved = True
            elif progress_percentage >= 80:
                status = "on_track"
            elif progress_percentage >= 50:
                status = "needs_attention"
            else:
                status = "at_risk"
            
            progress[objective.objective_name] = {
                "target_value": objective.target_value,
                "current_value": current_value,
                "progress_percentage": progress_percentage,
                "status": status,
                "weight": objective.weight
            }
        
        return progress
    
    def _calculate_overall_progress(self, campaign: CampaignStrategy) -> float:
        """Calculate overall campaign progress percentage"""
        
        # Time-based progress
        now = datetime.now(timezone.utc)
        if now < campaign.start_date:
            return 0.0
        elif now > campaign.end_date:
            return 100.0
        else:
            total_duration = (campaign.end_date - campaign.start_date).total_seconds()
            elapsed_duration = (now - campaign.start_date).total_seconds()
            time_progress = (elapsed_duration / total_duration) * 100
            
            return min(time_progress, 100.0)
    
    def get_campaign_stats(self) -> Dict[str, Any]:
        """Get campaign manager performance statistics"""
        return self.manager_stats.copy()
    
    def _update_manager_stats(self, action: str, participants: List[CreatorParticipant]):
        """Update manager performance statistics"""
        
        if action == "campaign_created":
            self.manager_stats["total_campaigns_managed"] += 1
            self.manager_stats["total_creators_coordinated"] += len(participants)


# Factory function for easy instantiation
def create_joint_campaign_manager(**kwargs) -> JointCampaignManager:
    """Create and configure a JointCampaignManager instance"""
    return JointCampaignManager(**kwargs)