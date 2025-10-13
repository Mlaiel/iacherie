"""🏆 Creator Tier Alert Prioritization - SLA & Priority Management
==================================================================

Advanced alert prioritization system based on creator tiers, revenue impact,
engagement levels, and business value for optimal resource allocation in
the Creator Economy platform.

Features:
- Multi-tier creator classification with dynamic scoring
- Revenue-based priority weighting
- SLA management with tier-specific response times
- Intelligent escalation paths based on creator value
- Resource allocation optimization
- Performance tracking and analytics
- Customer satisfaction correlation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code owned by Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Team training provided
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import statistics
import json
from collections import defaultdict

from .alert_manager import (
    IntelligentAlertManager, AlertCategory, AlertSeverity, 
    AlertType, AlertRule, IntelligentAlert
)

logger = logging.getLogger(__name__)


class CreatorTier(Enum):
    """Creator tier classifications with priority levels"""
    ENTERPRISE = "enterprise"          # Highest priority (1-10 minutes SLA)
    PREMIUM_PLUS = "premium_plus"      # VIP treatment (5-15 minutes SLA)
    PREMIUM = "premium"                # Premium support (10-30 minutes SLA)
    PROFESSIONAL = "professional"     # Business support (30-60 minutes SLA)
    STANDARD = "standard"              # Standard support (1-4 hours SLA)
    BASIC = "basic"                    # Basic support (4-24 hours SLA)
    STARTER = "starter"                # Community support (24-72 hours SLA)


class AlertPriorityLevel(Enum):
    """Alert priority levels for processing"""
    P0_CRITICAL = "p0_critical"        # Immediate response required
    P1_HIGH = "p1_high"               # Response within SLA tier limits
    P2_MEDIUM = "p2_medium"           # Normal priority processing
    P3_LOW = "p3_low"                 # Low priority, batch processing
    P4_INFORMATIONAL = "p4_info"      # Information only


class ResourceType(Enum):
    """Types of resources for allocation"""
    SUPPORT_AGENT = "support_agent"
    TECHNICAL_SPECIALIST = "technical_specialist"
    LEGAL_COUNSEL = "legal_counsel"
    ACCOUNT_MANAGER = "account_manager"
    EXECUTIVE_ESCALATION = "executive_escalation"
    AUTOMATED_SYSTEM = "automated_system"


@dataclass
class CreatorProfile:
    """Comprehensive creator profile for tier classification"""
    creator_id: str
    tier: CreatorTier
    
    # Revenue metrics
    monthly_revenue: float
    annual_revenue: float
    revenue_growth_rate: float
    revenue_per_content: float
    
    # Engagement metrics
    total_followers: int
    engagement_rate: float
    content_views: int
    content_interactions: int
    
    # Business metrics
    account_age_months: int
    content_frequency: float
    collaboration_count: int
    platform_count: int
    
    # Service metrics
    support_tickets_count: int
    satisfaction_score: float
    churn_risk_score: float
    
    # Tier calculation factors
    tier_score: float = 0.0
    tier_last_updated: datetime = field(default_factory=datetime.now)
    tier_override: Optional[str] = None
    tier_override_reason: Optional[str] = None


@dataclass
class SLAConfiguration:
    """SLA configuration for each creator tier"""
    tier: CreatorTier
    response_time_minutes: int
    escalation_time_minutes: int
    resolution_time_hours: int
    availability_percentage: float
    dedicated_resources: List[ResourceType]
    notification_channels: List[str]
    auto_escalation_enabled: bool = True
    priority_boost_factor: float = 1.0


@dataclass
class AlertPriorityScore:
    """Calculated priority score for an alert"""
    alert_id: str
    creator_id: str
    base_priority: AlertPriorityLevel
    calculated_priority: AlertPriorityLevel
    priority_score: float
    
    # Factors contributing to priority
    tier_factor: float
    revenue_factor: float
    engagement_factor: float
    urgency_factor: float
    business_impact_factor: float
    
    # SLA information
    sla_response_time: int  # minutes
    sla_resolution_time: int  # hours
    assigned_resources: List[ResourceType]
    
    # Tracking
    calculation_timestamp: datetime = field(default_factory=datetime.now)
    escalation_schedule: List[datetime] = field(default_factory=list)


@dataclass
class PrioritizationMetrics:
    """Metrics for prioritization system performance"""
    timestamp: datetime
    
    # Processing metrics
    total_alerts_processed: int
    alerts_by_tier: Dict[str, int]
    alerts_by_priority: Dict[str, int]
    avg_processing_time_by_tier: Dict[str, float]
    
    # SLA metrics
    sla_met_percentage: float
    avg_response_time: float
    escalation_rate: float
    customer_satisfaction: float
    
    # Resource metrics
    resource_utilization: Dict[str, float]
    workload_distribution: Dict[str, int]
    bottleneck_analysis: Dict[str, Any]


class CreatorTierAlertPrioritization:
    """
    Advanced alert prioritization system for Creator Economy
    
    Manages tier-based priority assignment, SLA enforcement, resource allocation,
    and escalation management for optimal creator experience.
    """
    
    def __init__(self):
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.sla_configurations: Dict[CreatorTier, SLAConfiguration] = {}
        self.priority_queue: List[AlertPriorityScore] = []
        self.metrics: PrioritizationMetrics = self._initialize_metrics()
        
        # Initialize SLA configurations
        self._initialize_sla_configurations()
        
        # Resource management
        self.resource_capacity: Dict[ResourceType, int] = {}
        self.resource_allocation: Dict[ResourceType, List[str]] = defaultdict(list)
        
        logger.info("CreatorTierAlertPrioritization initialized")
    
    def _initialize_metrics(self) -> PrioritizationMetrics:
        """Initialize empty metrics structure"""
        return PrioritizationMetrics(
            timestamp=datetime.now(),
            total_alerts_processed=0,
            alerts_by_tier={tier.value: 0 for tier in CreatorTier},
            alerts_by_priority={priority.value: 0 for priority in AlertPriorityLevel},
            avg_processing_time_by_tier={tier.value: 0.0 for tier in CreatorTier},
            sla_met_percentage=100.0,
            avg_response_time=0.0,
            escalation_rate=0.0,
            customer_satisfaction=10.0,
            resource_utilization={resource.value: 0.0 for resource in ResourceType},
            workload_distribution={tier.value: 0 for tier in CreatorTier},
            bottleneck_analysis={}
        )
    
    def _initialize_sla_configurations(self) -> None:
        """Initialize SLA configurations for each creator tier"""
        self.sla_configurations = {
            CreatorTier.ENTERPRISE: SLAConfiguration(
                tier=CreatorTier.ENTERPRISE,
                response_time_minutes=1,
                escalation_time_minutes=5,
                resolution_time_hours=1,
                availability_percentage=99.99,
                dedicated_resources=[
                    ResourceType.ACCOUNT_MANAGER,
                    ResourceType.TECHNICAL_SPECIALIST,
                    ResourceType.LEGAL_COUNSEL,
                    ResourceType.EXECUTIVE_ESCALATION
                ],
                notification_channels=['phone', 'sms', 'email', 'slack', 'teams'],
                priority_boost_factor=5.0
            ),
            CreatorTier.PREMIUM_PLUS: SLAConfiguration(
                tier=CreatorTier.PREMIUM_PLUS,
                response_time_minutes=5,
                escalation_time_minutes=10,
                resolution_time_hours=2,
                availability_percentage=99.9,
                dedicated_resources=[
                    ResourceType.ACCOUNT_MANAGER,
                    ResourceType.TECHNICAL_SPECIALIST,
                    ResourceType.SUPPORT_AGENT
                ],
                notification_channels=['phone', 'sms', 'email', 'slack'],
                priority_boost_factor=4.0
            ),
            CreatorTier.PREMIUM: SLAConfiguration(
                tier=CreatorTier.PREMIUM,
                response_time_minutes=10,
                escalation_time_minutes=20,
                resolution_time_hours=4,
                availability_percentage=99.5,
                dedicated_resources=[
                    ResourceType.SUPPORT_AGENT,
                    ResourceType.TECHNICAL_SPECIALIST
                ],
                notification_channels=['phone', 'email', 'slack'],
                priority_boost_factor=3.0
            ),
            CreatorTier.PROFESSIONAL: SLAConfiguration(
                tier=CreatorTier.PROFESSIONAL,
                response_time_minutes=30,
                escalation_time_minutes=60,
                resolution_time_hours=8,
                availability_percentage=99.0,
                dedicated_resources=[
                    ResourceType.SUPPORT_AGENT,
                    ResourceType.TECHNICAL_SPECIALIST
                ],
                notification_channels=['email', 'slack'],
                priority_boost_factor=2.0
            ),
            CreatorTier.STANDARD: SLAConfiguration(
                tier=CreatorTier.STANDARD,
                response_time_minutes=120,
                escalation_time_minutes=240,
                resolution_time_hours=24,
                availability_percentage=98.0,
                dedicated_resources=[
                    ResourceType.SUPPORT_AGENT
                ],
                notification_channels=['email'],
                priority_boost_factor=1.5
            ),
            CreatorTier.BASIC: SLAConfiguration(
                tier=CreatorTier.BASIC,
                response_time_minutes=240,
                escalation_time_minutes=480,
                resolution_time_hours=48,
                availability_percentage=95.0,
                dedicated_resources=[
                    ResourceType.SUPPORT_AGENT,
                    ResourceType.AUTOMATED_SYSTEM
                ],
                notification_channels=['email'],
                priority_boost_factor=1.0
            ),
            CreatorTier.STARTER: SLAConfiguration(
                tier=CreatorTier.STARTER,
                response_time_minutes=1440,  # 24 hours
                escalation_time_minutes=2880,  # 48 hours
                resolution_time_hours=72,
                availability_percentage=90.0,
                dedicated_resources=[
                    ResourceType.AUTOMATED_SYSTEM
                ],
                notification_channels=['email'],
                priority_boost_factor=0.5
            )
        }
        
        logger.info(f"Initialized SLA configurations for {len(self.sla_configurations)} tiers")
    
    async def register_creator(
        self, 
        creator_id: str, 
        creator_data: Dict[str, Any]
    ) -> CreatorProfile:
        """
        Register or update creator profile with tier calculation
        
        Args:
            creator_id: Unique creator identifier
            creator_data: Creator data for tier calculation
            
        Returns:
            Updated creator profile with calculated tier
        """
        try:
            # Create or update creator profile
            profile = CreatorProfile(
                creator_id=creator_id,
                tier=CreatorTier.STARTER,  # Default, will be calculated
                monthly_revenue=creator_data.get('monthly_revenue', 0.0),
                annual_revenue=creator_data.get('annual_revenue', 0.0),
                revenue_growth_rate=creator_data.get('revenue_growth_rate', 0.0),
                revenue_per_content=creator_data.get('revenue_per_content', 0.0),
                total_followers=creator_data.get('total_followers', 0),
                engagement_rate=creator_data.get('engagement_rate', 0.0),
                content_views=creator_data.get('content_views', 0),
                content_interactions=creator_data.get('content_interactions', 0),
                account_age_months=creator_data.get('account_age_months', 0),
                content_frequency=creator_data.get('content_frequency', 0.0),
                collaboration_count=creator_data.get('collaboration_count', 0),
                platform_count=creator_data.get('platform_count', 1),
                support_tickets_count=creator_data.get('support_tickets_count', 0),
                satisfaction_score=creator_data.get('satisfaction_score', 5.0),
                churn_risk_score=creator_data.get('churn_risk_score', 0.0),
                tier_override=creator_data.get('tier_override'),
                tier_override_reason=creator_data.get('tier_override_reason')
            )
            
            # Calculate tier
            calculated_tier, tier_score = await self._calculate_creator_tier(profile)
            profile.tier = calculated_tier
            profile.tier_score = tier_score
            profile.tier_last_updated = datetime.now()
            
            # Store profile
            self.creator_profiles[creator_id] = profile
            
            logger.info(f"Registered creator {creator_id} with tier {calculated_tier.value} (score: {tier_score:.2f})")
            return profile
            
        except Exception as e:
            logger.error(f"Error registering creator {creator_id}: {e}")
            raise
    
    async def _calculate_creator_tier(
        self, 
        profile: CreatorProfile
    ) -> Tuple[CreatorTier, float]:
        """
        Calculate creator tier based on multiple factors
        
        Returns:
            (calculated_tier, tier_score)
        """
        # Check for manual override
        if profile.tier_override:
            try:
                override_tier = CreatorTier(profile.tier_override)
                logger.info(f"Using tier override for {profile.creator_id}: {override_tier.value}")
                return override_tier, 10.0  # Max score for overrides
            except ValueError:
                logger.warning(f"Invalid tier override '{profile.tier_override}' for {profile.creator_id}")
        
        # Calculate weighted score based on multiple factors
        score_factors = {
            'revenue': self._calculate_revenue_score(profile),
            'engagement': self._calculate_engagement_score(profile),
            'business_value': self._calculate_business_value_score(profile),
            'loyalty': self._calculate_loyalty_score(profile),
            'growth': self._calculate_growth_score(profile)
        }
        
        # Weighted calculation
        weights = {
            'revenue': 0.35,
            'engagement': 0.20,
            'business_value': 0.20,
            'loyalty': 0.15,
            'growth': 0.10
        }
        
        total_score = sum(
            score_factors[factor] * weights[factor]
            for factor in score_factors
        )
        
        # Map score to tier
        tier = self._score_to_tier(total_score)
        
        logger.debug(f"Tier calculation for {profile.creator_id}: {score_factors} -> {total_score:.2f} -> {tier.value}")
        
        return tier, total_score
    
    def _calculate_revenue_score(self, profile: CreatorProfile) -> float:
        """Calculate revenue-based score (0-10)"""
        monthly_revenue = profile.monthly_revenue
        
        if monthly_revenue >= 100000:  # $100k+/month
            return 10.0
        elif monthly_revenue >= 50000:  # $50k-100k/month
            return 9.0
        elif monthly_revenue >= 25000:  # $25k-50k/month
            return 8.0
        elif monthly_revenue >= 10000:  # $10k-25k/month
            return 7.0
        elif monthly_revenue >= 5000:   # $5k-10k/month
            return 6.0
        elif monthly_revenue >= 2500:   # $2.5k-5k/month
            return 5.0
        elif monthly_revenue >= 1000:   # $1k-2.5k/month
            return 4.0
        elif monthly_revenue >= 500:    # $500-1k/month
            return 3.0
        elif monthly_revenue >= 100:    # $100-500/month
            return 2.0
        elif monthly_revenue > 0:       # Any revenue
            return 1.0
        else:
            return 0.0
    
    def _calculate_engagement_score(self, profile: CreatorProfile) -> float:
        """Calculate engagement-based score (0-10)"""
        followers = profile.total_followers
        engagement_rate = profile.engagement_rate
        
        # Base score from follower count
        if followers >= 10000000:  # 10M+ followers
            follower_score = 10.0
        elif followers >= 1000000:  # 1M-10M followers
            follower_score = 9.0
        elif followers >= 500000:   # 500k-1M followers
            follower_score = 8.0
        elif followers >= 100000:   # 100k-500k followers
            follower_score = 7.0
        elif followers >= 50000:    # 50k-100k followers
            follower_score = 6.0
        elif followers >= 10000:    # 10k-50k followers
            follower_score = 5.0
        elif followers >= 5000:     # 5k-10k followers
            follower_score = 4.0
        elif followers >= 1000:     # 1k-5k followers
            follower_score = 3.0
        elif followers >= 500:      # 500-1k followers
            follower_score = 2.0
        elif followers > 0:         # Any followers
            follower_score = 1.0
        else:
            follower_score = 0.0
        
        # Engagement rate bonus/penalty
        if engagement_rate >= 10.0:     # 10%+ engagement
            engagement_multiplier = 1.5
        elif engagement_rate >= 5.0:    # 5-10% engagement
            engagement_multiplier = 1.2
        elif engagement_rate >= 2.0:    # 2-5% engagement
            engagement_multiplier = 1.0
        elif engagement_rate >= 1.0:    # 1-2% engagement
            engagement_multiplier = 0.8
        else:                           # <1% engagement
            engagement_multiplier = 0.6
        
        return min(10.0, follower_score * engagement_multiplier)
    
    def _calculate_business_value_score(self, profile: CreatorProfile) -> float:
        """Calculate business value score (0-10)"""
        platform_count = profile.platform_count
        collaboration_count = profile.collaboration_count
        content_frequency = profile.content_frequency
        
        # Multi-platform presence
        platform_score = min(3.0, platform_count * 0.5)
        
        # Collaboration activity
        collaboration_score = min(3.0, collaboration_count * 0.1)
        
        # Content frequency (posts per week)
        if content_frequency >= 10:      # 10+ posts/week
            frequency_score = 4.0
        elif content_frequency >= 5:     # 5-10 posts/week
            frequency_score = 3.5
        elif content_frequency >= 3:     # 3-5 posts/week
            frequency_score = 3.0
        elif content_frequency >= 1:     # 1-3 posts/week
            frequency_score = 2.0
        elif content_frequency >= 0.5:   # 2+ posts/month
            frequency_score = 1.0
        else:
            frequency_score = 0.0
        
        return platform_score + collaboration_score + frequency_score
    
    def _calculate_loyalty_score(self, profile: CreatorProfile) -> float:
        """Calculate loyalty/satisfaction score (0-10)"""
        account_age = profile.account_age_months
        satisfaction = profile.satisfaction_score
        churn_risk = profile.churn_risk_score
        
        # Account age factor
        if account_age >= 36:           # 3+ years
            age_score = 4.0
        elif account_age >= 24:         # 2-3 years
            age_score = 3.0
        elif account_age >= 12:         # 1-2 years
            age_score = 2.0
        elif account_age >= 6:          # 6-12 months
            age_score = 1.0
        else:
            age_score = 0.5
        
        # Satisfaction factor (0-10 scale)
        satisfaction_score = satisfaction
        
        # Churn risk penalty (0-10 scale, lower is better)
        churn_penalty = churn_risk * 0.5
        
        return max(0.0, min(10.0, age_score + satisfaction_score - churn_penalty))
    
    def _calculate_growth_score(self, profile: CreatorProfile) -> float:
        """Calculate growth trajectory score (0-10)"""
        revenue_growth = profile.revenue_growth_rate
        
        if revenue_growth >= 100:       # 100%+ growth
            return 10.0
        elif revenue_growth >= 50:      # 50-100% growth
            return 8.0
        elif revenue_growth >= 25:      # 25-50% growth
            return 6.0
        elif revenue_growth >= 10:      # 10-25% growth
            return 4.0
        elif revenue_growth >= 0:       # Positive growth
            return 2.0
        elif revenue_growth >= -10:     # Small decline
            return 1.0
        else:                          # Significant decline
            return 0.0
    
    def _score_to_tier(self, score: float) -> CreatorTier:
        """Map calculated score to creator tier"""
        if score >= 9.0:
            return CreatorTier.ENTERPRISE
        elif score >= 8.0:
            return CreatorTier.PREMIUM_PLUS
        elif score >= 7.0:
            return CreatorTier.PREMIUM
        elif score >= 5.5:
            return CreatorTier.PROFESSIONAL
        elif score >= 3.5:
            return CreatorTier.STANDARD
        elif score >= 1.5:
            return CreatorTier.BASIC
        else:
            return CreatorTier.STARTER
    
    async def calculate_alert_priority(
        self, 
        alert_data: Dict[str, Any], 
        creator_id: str
    ) -> AlertPriorityScore:
        """
        Calculate priority score for an alert based on creator tier and alert characteristics
        
        Args:
            alert_data: Alert information
            creator_id: Creator who owns the affected resource
            
        Returns:
            Calculated priority score with resource allocation
        """
        try:
            # Get creator profile
            creator_profile = self.creator_profiles.get(creator_id)
            if not creator_profile:
                # Create default profile for unknown creator
                creator_profile = await self.register_creator(creator_id, {})
            
            # Get base alert priority
            base_priority = self._determine_base_priority(alert_data)
            
            # Calculate priority factors
            tier_factor = self._calculate_tier_factor(creator_profile)
            revenue_factor = self._calculate_revenue_factor(creator_profile, alert_data)
            engagement_factor = self._calculate_engagement_factor(creator_profile)
            urgency_factor = self._calculate_urgency_factor(alert_data)
            business_impact_factor = self._calculate_business_impact_factor(alert_data, creator_profile)
            
            # Calculate overall priority score
            priority_score = (
                tier_factor * 0.30 +
                revenue_factor * 0.25 +
                urgency_factor * 0.20 +
                business_impact_factor * 0.15 +
                engagement_factor * 0.10
            )
            
            # Determine final priority level
            calculated_priority = self._score_to_priority_level(priority_score)
            
            # Get SLA configuration
            sla_config = self.sla_configurations[creator_profile.tier]
            
            # Create priority score object
            alert_priority = AlertPriorityScore(
                alert_id=alert_data.get('id', 'unknown'),
                creator_id=creator_id,
                base_priority=base_priority,
                calculated_priority=calculated_priority,
                priority_score=priority_score,
                tier_factor=tier_factor,
                revenue_factor=revenue_factor,
                engagement_factor=engagement_factor,
                urgency_factor=urgency_factor,
                business_impact_factor=business_impact_factor,
                sla_response_time=sla_config.response_time_minutes,
                sla_resolution_time=sla_config.resolution_time_hours,
                assigned_resources=sla_config.dedicated_resources.copy()
            )
            
            # Calculate escalation schedule
            alert_priority.escalation_schedule = self._calculate_escalation_schedule(
                alert_priority, sla_config
            )
            
            # Add to priority queue
            self.priority_queue.append(alert_priority)
            self.priority_queue.sort(key=lambda x: x.priority_score, reverse=True)
            
            # Update metrics
            self._update_prioritization_metrics(alert_priority, creator_profile)
            
            logger.info(f"Calculated priority for alert {alert_priority.alert_id}: "
                       f"{calculated_priority.value} (score: {priority_score:.2f})")
            
            return alert_priority
            
        except Exception as e:
            logger.error(f"Error calculating alert priority for creator {creator_id}: {e}")
            raise
    
    def _determine_base_priority(self, alert_data: Dict[str, Any]) -> AlertPriorityLevel:
        """Determine base priority from alert data"""
        severity = alert_data.get('severity', '').lower()
        alert_type = alert_data.get('type', '').lower()
        
        # Critical system alerts
        if severity == 'emergency' or 'critical' in severity:
            return AlertPriorityLevel.P0_CRITICAL
        elif severity == 'critical' or 'high' in severity:
            return AlertPriorityLevel.P1_HIGH
        elif severity == 'warning' or 'medium' in severity:
            return AlertPriorityLevel.P2_MEDIUM
        elif severity == 'info' or 'low' in severity:
            return AlertPriorityLevel.P3_LOW
        else:
            return AlertPriorityLevel.P4_INFORMATIONAL
    
    def _calculate_tier_factor(self, creator_profile: CreatorProfile) -> float:
        """Calculate tier-based priority factor (0-10)"""
        tier_values = {
            CreatorTier.ENTERPRISE: 10.0,
            CreatorTier.PREMIUM_PLUS: 9.0,
            CreatorTier.PREMIUM: 8.0,
            CreatorTier.PROFESSIONAL: 6.0,
            CreatorTier.STANDARD: 4.0,
            CreatorTier.BASIC: 2.0,
            CreatorTier.STARTER: 1.0
        }
        
        return tier_values.get(creator_profile.tier, 1.0)
    
    def _calculate_revenue_factor(
        self, 
        creator_profile: CreatorProfile, 
        alert_data: Dict[str, Any]
    ) -> float:
        """Calculate revenue impact factor (0-10)"""
        monthly_revenue = creator_profile.monthly_revenue
        alert_type = alert_data.get('type', '').lower()
        
        # Base revenue factor
        if monthly_revenue >= 50000:
            base_factor = 10.0
        elif monthly_revenue >= 10000:
            base_factor = 8.0
        elif monthly_revenue >= 5000:
            base_factor = 6.0
        elif monthly_revenue >= 1000:
            base_factor = 4.0
        elif monthly_revenue > 0:
            base_factor = 2.0
        else:
            base_factor = 1.0
        
        # Revenue-critical alert types get boost
        if any(keyword in alert_type for keyword in ['revenue', 'payment', 'monetization', 'billing']):
            base_factor *= 1.5
        
        return min(10.0, base_factor)
    
    def _calculate_engagement_factor(self, creator_profile: CreatorProfile) -> float:
        """Calculate engagement-based factor (0-10)"""
        engagement_rate = creator_profile.engagement_rate
        followers = creator_profile.total_followers
        
        # High engagement creators get priority
        if engagement_rate >= 10.0 and followers >= 100000:
            return 10.0
        elif engagement_rate >= 5.0 and followers >= 50000:
            return 8.0
        elif engagement_rate >= 2.0 and followers >= 10000:
            return 6.0
        elif engagement_rate >= 1.0:
            return 4.0
        else:
            return 2.0
    
    def _calculate_urgency_factor(self, alert_data: Dict[str, Any]) -> float:
        """Calculate urgency factor based on alert characteristics (0-10)"""
        alert_type = alert_data.get('type', '').lower()
        impact_scope = alert_data.get('impact_scope', '').lower()
        
        urgency_score = 5.0  # Base urgency
        
        # High urgency alert types
        if any(keyword in alert_type for keyword in ['security', 'breach', 'fraud', 'legal']):
            urgency_score += 3.0
        elif any(keyword in alert_type for keyword in ['outage', 'failure', 'error']):
            urgency_score += 2.0
        elif any(keyword in alert_type for keyword in ['performance', 'latency']):
            urgency_score += 1.0
        
        # Impact scope factor
        if 'global' in impact_scope or 'all_users' in impact_scope:
            urgency_score += 2.0
        elif 'multiple_users' in impact_scope:
            urgency_score += 1.0
        
        return min(10.0, urgency_score)
    
    def _calculate_business_impact_factor(
        self, 
        alert_data: Dict[str, Any], 
        creator_profile: CreatorProfile
    ) -> float:
        """Calculate business impact factor (0-10)"""
        alert_type = alert_data.get('type', '').lower()
        affected_services = alert_data.get('affected_services', [])
        
        impact_score = 5.0  # Base impact
        
        # Critical business functions
        critical_keywords = ['monetization', 'payment', 'content_protection', 'collaboration']
        if any(keyword in alert_type for keyword in critical_keywords):
            impact_score += 3.0
        
        # High-value creator services
        if creator_profile.tier in [CreatorTier.ENTERPRISE, CreatorTier.PREMIUM_PLUS]:
            if any(service in str(affected_services) for service in ['premium', 'enterprise', 'dedicated']):
                impact_score += 2.0
        
        return min(10.0, impact_score)
    
    def _score_to_priority_level(self, score: float) -> AlertPriorityLevel:
        """Map priority score to priority level"""
        if score >= 8.5:
            return AlertPriorityLevel.P0_CRITICAL
        elif score >= 7.0:
            return AlertPriorityLevel.P1_HIGH
        elif score >= 5.0:
            return AlertPriorityLevel.P2_MEDIUM
        elif score >= 3.0:
            return AlertPriorityLevel.P3_LOW
        else:
            return AlertPriorityLevel.P4_INFORMATIONAL
    
    def _calculate_escalation_schedule(
        self, 
        alert_priority: AlertPriorityScore, 
        sla_config: SLAConfiguration
    ) -> List[datetime]:
        """Calculate escalation schedule based on SLA configuration"""
        now = datetime.now()
        schedule = []
        
        # Initial response time
        schedule.append(now + timedelta(minutes=sla_config.response_time_minutes))
        
        # Escalation time
        if sla_config.auto_escalation_enabled:
            schedule.append(now + timedelta(minutes=sla_config.escalation_time_minutes))
        
        # Resolution deadline
        schedule.append(now + timedelta(hours=sla_config.resolution_time_hours))
        
        return schedule
    
    def _update_prioritization_metrics(
        self, 
        alert_priority: AlertPriorityScore, 
        creator_profile: CreatorProfile
    ) -> None:
        """Update prioritization metrics"""
        self.metrics.total_alerts_processed += 1
        self.metrics.alerts_by_tier[creator_profile.tier.value] += 1
        self.metrics.alerts_by_priority[alert_priority.calculated_priority.value] += 1
        self.metrics.workload_distribution[creator_profile.tier.value] += 1
    
    async def get_next_priority_alert(self) -> Optional[AlertPriorityScore]:
        """Get the next highest priority alert from the queue"""
        if not self.priority_queue:
            return None
        
        # Return highest priority alert (queue is sorted by priority_score desc)
        return self.priority_queue.pop(0)
    
    async def get_creator_tier_info(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive tier information for a creator"""
        creator_profile = self.creator_profiles.get(creator_id)
        if not creator_profile:
            return None
        
        sla_config = self.sla_configurations[creator_profile.tier]
        
        return {
            'creator_id': creator_id,
            'tier': creator_profile.tier.value,
            'tier_score': creator_profile.tier_score,
            'tier_last_updated': creator_profile.tier_last_updated.isoformat(),
            'sla_response_time_minutes': sla_config.response_time_minutes,
            'sla_resolution_time_hours': sla_config.resolution_time_hours,
            'dedicated_resources': [r.value for r in sla_config.dedicated_resources],
            'notification_channels': sla_config.notification_channels,
            'priority_boost_factor': sla_config.priority_boost_factor
        }
    
    async def get_prioritization_metrics(self) -> PrioritizationMetrics:
        """Get current prioritization metrics"""
        return self.metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the prioritization system"""
        return {
            'status': 'healthy',
            'registered_creators': len(self.creator_profiles),
            'active_alerts_in_queue': len(self.priority_queue),
            'tier_configurations': len(self.sla_configurations),
            'total_alerts_processed': self.metrics.total_alerts_processed,
            'timestamp': datetime.now().isoformat()
        }


# Export main classes
__all__ = [
    'CreatorTierAlertPrioritization',
    'CreatorProfile',
    'SLAConfiguration',
    'AlertPriorityScore',
    'PrioritizationMetrics',
    'CreatorTier',
    'AlertPriorityLevel',
    'ResourceType'
]