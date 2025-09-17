#!/usr/bin/env python3
"""
Creator Tier Log Analytics Engine - Creator Economy Enterprise
============================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import uuid
from pathlib import Path
from collections import defaultdict


class CreatorTier(Enum):
    """Creator tier levels"""
    NEWCOMER = "newcomer"
    RISING = "rising"
    ESTABLISHED = "established"
    PROFESSIONAL = "professional"
    ELITE = "elite"
    LEGENDARY = "legendary"
    ENTERPRISE = "enterprise"


class TierEvent(Enum):
    """Tier-related events"""
    TIER_UPGRADE = "tier_upgrade"
    TIER_DOWNGRADE = "tier_downgrade"
    TIER_MILESTONE = "tier_milestone"
    TIER_REVIEW = "tier_review"
    TIER_BENEFIT_UNLOCKED = "tier_benefit_unlocked"
    TIER_PERFORMANCE_UPDATE = "tier_performance_update"
    TIER_REQUIREMENT_MET = "tier_requirement_met"
    TIER_REQUIREMENT_MISSED = "tier_requirement_missed"


@dataclass
class TierMetrics:
    """Tier performance metrics"""
    tier: CreatorTier
    creator_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Content metrics
    content_count: int = 0
    content_quality_score: float = 0.0
    upload_frequency: float = 0.0
    
    # Engagement metrics
    total_views: int = 0
    total_likes: int = 0
    total_comments: int = 0
    total_shares: int = 0
    engagement_rate: float = 0.0
    
    # Audience metrics
    subscriber_count: int = 0
    follower_growth_rate: float = 0.0
    audience_retention_rate: float = 0.0
    
    # Revenue metrics
    total_revenue: Decimal = Decimal('0.00')
    monthly_revenue: Decimal = Decimal('0.00')
    revenue_growth_rate: float = 0.0
    
    # Collaboration metrics
    collaboration_count: int = 0
    partnership_count: int = 0
    collaboration_success_rate: float = 0.0
    
    # Platform metrics
    platform_diversity: float = 0.0
    cross_platform_performance: float = 0.0
    
    # Tier score
    tier_score: float = 0.0
    tier_progress: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "tier": self.tier.value,
            "creator_id": self.creator_id,
            "timestamp": self.timestamp.isoformat(),
            "content_count": self.content_count,
            "content_quality_score": self.content_quality_score,
            "upload_frequency": self.upload_frequency,
            "total_views": self.total_views,
            "total_likes": self.total_likes,
            "total_comments": self.total_comments,
            "total_shares": self.total_shares,
            "engagement_rate": self.engagement_rate,
            "subscriber_count": self.subscriber_count,
            "follower_growth_rate": self.follower_growth_rate,
            "audience_retention_rate": self.audience_retention_rate,
            "total_revenue": str(self.total_revenue),
            "monthly_revenue": str(self.monthly_revenue),
            "revenue_growth_rate": self.revenue_growth_rate,
            "collaboration_count": self.collaboration_count,
            "partnership_count": self.partnership_count,
            "collaboration_success_rate": self.collaboration_success_rate,
            "platform_diversity": self.platform_diversity,
            "cross_platform_performance": self.cross_platform_performance,
            "tier_score": self.tier_score,
            "tier_progress": self.tier_progress
        }


@dataclass
class TierRequirement:
    """Requirements for tier advancement"""
    tier: CreatorTier
    min_subscriber_count: int = 0
    min_content_count: int = 0
    min_monthly_revenue: Decimal = Decimal('0.00')
    min_engagement_rate: float = 0.0
    min_quality_score: float = 0.0
    min_upload_frequency: float = 0.0
    min_collaboration_count: int = 0
    min_platform_diversity: float = 0.0
    required_milestones: List[str] = field(default_factory=list)
    
    def check_requirements(self, metrics: TierMetrics) -> Tuple[bool, List[str]]:
        """Check if metrics meet tier requirements"""
        missing_requirements = []
        
        if metrics.subscriber_count < self.min_subscriber_count:
            missing_requirements.append(f"subscriber_count: {metrics.subscriber_count}/{self.min_subscriber_count}")
        
        if metrics.content_count < self.min_content_count:
            missing_requirements.append(f"content_count: {metrics.content_count}/{self.min_content_count}")
        
        if metrics.monthly_revenue < self.min_monthly_revenue:
            missing_requirements.append(f"monthly_revenue: {metrics.monthly_revenue}/{self.min_monthly_revenue}")
        
        if metrics.engagement_rate < self.min_engagement_rate:
            missing_requirements.append(f"engagement_rate: {metrics.engagement_rate:.2f}/{self.min_engagement_rate}")
        
        if metrics.content_quality_score < self.min_quality_score:
            missing_requirements.append(f"quality_score: {metrics.content_quality_score:.2f}/{self.min_quality_score}")
        
        if metrics.upload_frequency < self.min_upload_frequency:
            missing_requirements.append(f"upload_frequency: {metrics.upload_frequency:.2f}/{self.min_upload_frequency}")
        
        if metrics.collaboration_count < self.min_collaboration_count:
            missing_requirements.append(f"collaboration_count: {metrics.collaboration_count}/{self.min_collaboration_count}")
        
        if metrics.platform_diversity < self.min_platform_diversity:
            missing_requirements.append(f"platform_diversity: {metrics.platform_diversity:.2f}/{self.min_platform_diversity}")
        
        return len(missing_requirements) == 0, missing_requirements


class CreatorTierLogAnalyticsEngine:
    """
    Moteur analytics logs tier créateurs enterprise
    
    Features:
    - Creator tier log analytics comprehensive
    - Creator tier progression log tracking
    - Tier-specific Creator log analysis
    - Creator tier performance log correlation
    - Creator tier optimization log insights
    - Creator tier log intelligence analytics
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Redis connection for caching
        self._redis_client: Optional[redis.Redis] = None
        
        # Analytics state
        self._creator_metrics: Dict[str, TierMetrics] = {}
        self._tier_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._tier_analytics: Dict[str, Dict[str, Any]] = {}
        
        # Tier requirements configuration
        self._tier_requirements = self._initialize_tier_requirements()
        
        # Processing metrics
        self._analytics_metrics = {
            "creators_analyzed": 0,
            "tier_changes_processed": 0,
            "milestones_tracked": 0,
            "analytics_generated": 0,
            "errors_encountered": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Analytics rules
        self._analytics_rules = {
            "tier_evaluation_interval": 86400,  # 24 hours
            "history_retention_days": 365,
            "minimum_data_points": 5,
            "trend_analysis_window": 30,  # days
            "performance_thresholds": {
                "excellent": 0.9,
                "good": 0.7,
                "average": 0.5,
                "poor": 0.3
            }
        }
        
        # Initialize components
        self._initialized = False
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for tier analytics engine"""
        logger = logging.getLogger(f"{__name__}.CreatorTierLogAnalyticsEngine")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _initialize_tier_requirements(self) -> Dict[CreatorTier, TierRequirement]:
        """Initialize tier requirements"""
        return {
            CreatorTier.NEWCOMER: TierRequirement(
                tier=CreatorTier.NEWCOMER,
                min_subscriber_count=0,
                min_content_count=0,
                min_monthly_revenue=Decimal('0.00'),
                min_engagement_rate=0.0,
                min_quality_score=0.0
            ),
            CreatorTier.RISING: TierRequirement(
                tier=CreatorTier.RISING,
                min_subscriber_count=100,
                min_content_count=5,
                min_monthly_revenue=Decimal('10.00'),
                min_engagement_rate=0.02,
                min_quality_score=0.6,
                min_upload_frequency=1.0  # per week
            ),
            CreatorTier.ESTABLISHED: TierRequirement(
                tier=CreatorTier.ESTABLISHED,
                min_subscriber_count=1000,
                min_content_count=25,
                min_monthly_revenue=Decimal('100.00'),
                min_engagement_rate=0.05,
                min_quality_score=0.7,
                min_upload_frequency=2.0,
                min_collaboration_count=2
            ),
            CreatorTier.PROFESSIONAL: TierRequirement(
                tier=CreatorTier.PROFESSIONAL,
                min_subscriber_count=10000,
                min_content_count=100,
                min_monthly_revenue=Decimal('1000.00'),
                min_engagement_rate=0.08,
                min_quality_score=0.8,
                min_upload_frequency=3.0,
                min_collaboration_count=5,
                min_platform_diversity=0.3
            ),
            CreatorTier.ELITE: TierRequirement(
                tier=CreatorTier.ELITE,
                min_subscriber_count=100000,
                min_content_count=500,
                min_monthly_revenue=Decimal('10000.00'),
                min_engagement_rate=0.10,
                min_quality_score=0.85,
                min_upload_frequency=4.0,
                min_collaboration_count=10,
                min_platform_diversity=0.5
            ),
            CreatorTier.LEGENDARY: TierRequirement(
                tier=CreatorTier.LEGENDARY,
                min_subscriber_count=1000000,
                min_content_count=1000,
                min_monthly_revenue=Decimal('50000.00'),
                min_engagement_rate=0.12,
                min_quality_score=0.9,
                min_upload_frequency=5.0,
                min_collaboration_count=25,
                min_platform_diversity=0.7
            ),
            CreatorTier.ENTERPRISE: TierRequirement(
                tier=CreatorTier.ENTERPRISE,
                min_subscriber_count=10000000,
                min_content_count=2000,
                min_monthly_revenue=Decimal('100000.00'),
                min_engagement_rate=0.15,
                min_quality_score=0.95,
                min_upload_frequency=7.0,
                min_collaboration_count=50,
                min_platform_diversity=0.8
            )
        }
    
    async def initialize(self) -> bool:
        """Initialize tier analytics engine"""
        try:
            self.logger.info("🎯 Initializing Creator Tier Log Analytics Engine...")
            
            # Initialize Redis connection
            await self._initialize_redis()
            
            # Load cached data
            await self._load_cached_data()
            
            # Validate configuration
            self._validate_configuration()
            
            self._initialized = True
            self.logger.info("✅ Creator Tier Log Analytics Engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize engine: {e}")
            return False
    
    async def _initialize_redis(self):
        """Initialize Redis connection for caching"""
        try:
            redis_config = self.config.get("redis", {})
            self._redis_client = redis.Redis(
                host=redis_config.get("host", "localhost"),
                port=redis_config.get("port", 6379),
                decode_responses=True
            )
            await self._redis_client.ping()
            self.logger.info("✅ Redis connection established")
        except Exception as e:
            self.logger.warning(f"⚠️ Redis connection failed: {e}")
            self._redis_client = None
    
    async def _load_cached_data(self):
        """Load cached tier analytics data"""
        if not self._redis_client:
            return
            
        try:
            # Load creator metrics cache
            metrics_keys = await self._redis_client.keys("tier_analytics:metrics:*")
            for key in metrics_keys:
                creator_id = key.split(":")[-1]
                metrics_data = await self._redis_client.get(key)
                if metrics_data:
                    data = json.loads(metrics_data)
                    self._creator_metrics[creator_id] = self._dict_to_tier_metrics(data)
            
            # Load tier history cache
            history_keys = await self._redis_client.keys("tier_analytics:history:*")
            for key in history_keys:
                creator_id = key.split(":")[-1]
                history_data = await self._redis_client.get(key)
                if history_data:
                    self._tier_history[creator_id] = json.loads(history_data)
            
            self.logger.info(f"📊 Loaded {len(self._creator_metrics)} creator metrics from cache")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load cached data: {e}")
    
    def _dict_to_tier_metrics(self, data: Dict[str, Any]) -> TierMetrics:
        """Convert dictionary to TierMetrics object"""
        return TierMetrics(
            tier=CreatorTier(data["tier"]),
            creator_id=data["creator_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            content_count=data.get("content_count", 0),
            content_quality_score=data.get("content_quality_score", 0.0),
            upload_frequency=data.get("upload_frequency", 0.0),
            total_views=data.get("total_views", 0),
            total_likes=data.get("total_likes", 0),
            total_comments=data.get("total_comments", 0),
            total_shares=data.get("total_shares", 0),
            engagement_rate=data.get("engagement_rate", 0.0),
            subscriber_count=data.get("subscriber_count", 0),
            follower_growth_rate=data.get("follower_growth_rate", 0.0),
            audience_retention_rate=data.get("audience_retention_rate", 0.0),
            total_revenue=Decimal(str(data.get("total_revenue", "0.00"))),
            monthly_revenue=Decimal(str(data.get("monthly_revenue", "0.00"))),
            revenue_growth_rate=data.get("revenue_growth_rate", 0.0),
            collaboration_count=data.get("collaboration_count", 0),
            partnership_count=data.get("partnership_count", 0),
            collaboration_success_rate=data.get("collaboration_success_rate", 0.0),
            platform_diversity=data.get("platform_diversity", 0.0),
            cross_platform_performance=data.get("cross_platform_performance", 0.0),
            tier_score=data.get("tier_score", 0.0),
            tier_progress=data.get("tier_progress", 0.0)
        )
    
    def _validate_configuration(self):
        """Validate analytics configuration"""
        required_config = ["output_path", "analytics_interval"]
        for key in required_config:
            if key not in self.config:
                self.logger.warning(f"⚠️ Missing configuration key: {key}")
    
    async def analyze_creator_tier(self, creator_id: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze creator tier from log data"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Parse metrics from log data
            metrics = await self._parse_tier_metrics(creator_id, log_data)
            if not metrics:
                return {"success": False, "error": "Failed to parse metrics"}
            
            # Calculate tier score
            await self._calculate_tier_score(metrics)
            
            # Evaluate tier progression
            tier_change = await self._evaluate_tier_progression(metrics)
            
            # Update analytics
            await self._update_tier_analytics(metrics, tier_change)
            
            # Cache metrics
            await self._cache_tier_metrics(metrics)
            
            # Generate insights
            insights = await self._generate_tier_insights(metrics)
            
            # Log tier analytics
            await self._log_tier_analytics(metrics, tier_change, insights)
            
            self._analytics_metrics["creators_analyzed"] += 1
            
            result = {
                "success": True,
                "creator_id": creator_id,
                "current_tier": metrics.tier.value,
                "tier_score": metrics.tier_score,
                "tier_progress": metrics.tier_progress,
                "tier_change": tier_change,
                "insights": insights,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"✅ Analyzed tier for creator {creator_id}: {metrics.tier.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing creator tier: {e}")
            self._analytics_metrics["errors_encountered"] += 1
            return {"success": False, "error": str(e)}
    
    async def _parse_tier_metrics(self, creator_id: str, log_data: Dict[str, Any]) -> Optional[TierMetrics]:
        """Parse tier metrics from log data"""
        try:
            # Get existing metrics or create new
            existing_metrics = self._creator_metrics.get(creator_id)
            
            # Parse current tier
            current_tier_str = log_data.get("tier", "newcomer")
            try:
                current_tier = CreatorTier(current_tier_str)
            except ValueError:
                current_tier = CreatorTier.NEWCOMER
            
            # Create metrics object
            metrics = TierMetrics(
                tier=current_tier,
                creator_id=creator_id,
                timestamp=datetime.utcnow()
            )
            
            # Update metrics from log data
            metrics.content_count = log_data.get("content_count", existing_metrics.content_count if existing_metrics else 0)
            metrics.content_quality_score = log_data.get("content_quality_score", existing_metrics.content_quality_score if existing_metrics else 0.0)
            metrics.upload_frequency = log_data.get("upload_frequency", existing_metrics.upload_frequency if existing_metrics else 0.0)
            metrics.total_views = log_data.get("total_views", existing_metrics.total_views if existing_metrics else 0)
            metrics.total_likes = log_data.get("total_likes", existing_metrics.total_likes if existing_metrics else 0)
            metrics.total_comments = log_data.get("total_comments", existing_metrics.total_comments if existing_metrics else 0)
            metrics.total_shares = log_data.get("total_shares", existing_metrics.total_shares if existing_metrics else 0)
            metrics.subscriber_count = log_data.get("subscriber_count", existing_metrics.subscriber_count if existing_metrics else 0)
            metrics.collaboration_count = log_data.get("collaboration_count", existing_metrics.collaboration_count if existing_metrics else 0)
            metrics.partnership_count = log_data.get("partnership_count", existing_metrics.partnership_count if existing_metrics else 0)
            
            # Calculate derived metrics
            if metrics.total_views > 0:
                metrics.engagement_rate = (metrics.total_likes + metrics.total_comments + metrics.total_shares) / metrics.total_views
            
            # Update revenue metrics
            if "total_revenue" in log_data:
                metrics.total_revenue = Decimal(str(log_data["total_revenue"]))
            elif existing_metrics:
                metrics.total_revenue = existing_metrics.total_revenue
            
            if "monthly_revenue" in log_data:
                metrics.monthly_revenue = Decimal(str(log_data["monthly_revenue"]))
            elif existing_metrics:
                metrics.monthly_revenue = existing_metrics.monthly_revenue
            
            # Calculate growth rates if we have historical data
            if existing_metrics:
                time_diff = (metrics.timestamp - existing_metrics.timestamp).total_seconds() / 86400  # days
                if time_diff > 0:
                    metrics.follower_growth_rate = (metrics.subscriber_count - existing_metrics.subscriber_count) / time_diff
                    if existing_metrics.monthly_revenue > 0:
                        metrics.revenue_growth_rate = float((metrics.monthly_revenue - existing_metrics.monthly_revenue) / existing_metrics.monthly_revenue)
            
            # Calculate platform diversity
            platforms = log_data.get("platforms", [])
            if platforms:
                metrics.platform_diversity = len(platforms) / 10.0  # Normalize to 10 possible platforms
            
            # Store updated metrics
            self._creator_metrics[creator_id] = metrics
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing tier metrics: {e}")
            return None
    
    async def _calculate_tier_score(self, metrics: TierMetrics):
        """Calculate overall tier score"""
        try:
            # Weights for different metrics
            weights = {
                "content": 0.20,
                "engagement": 0.25,
                "audience": 0.20,
                "revenue": 0.20,
                "collaboration": 0.10,
                "platform": 0.05
            }
            
            # Normalize metrics to 0-1 scale
            content_score = min(1.0, (metrics.content_quality_score * 0.7 + min(1.0, metrics.upload_frequency / 7.0) * 0.3))
            
            engagement_score = min(1.0, metrics.engagement_rate * 10)  # Assuming 10% is excellent
            
            audience_score = min(1.0, np.log10(max(1, metrics.subscriber_count)) / 7)  # Log scale up to 10M
            
            revenue_score = min(1.0, float(metrics.monthly_revenue) / 100000)  # Up to $100k
            
            collaboration_score = min(1.0, metrics.collaboration_count / 50)  # Up to 50 collaborations
            
            platform_score = metrics.platform_diversity
            
            # Calculate weighted score
            metrics.tier_score = (
                content_score * weights["content"] +
                engagement_score * weights["engagement"] +
                audience_score * weights["audience"] +
                revenue_score * weights["revenue"] +
                collaboration_score * weights["collaboration"] +
                platform_score * weights["platform"]
            )
            
            # Calculate tier progress
            current_tier_req = self._tier_requirements[metrics.tier]
            next_tier = self._get_next_tier(metrics.tier)
            
            if next_tier:
                next_tier_req = self._tier_requirements[next_tier]
                requirements_met, _ = next_tier_req.check_requirements(metrics)
                
                if requirements_met:
                    metrics.tier_progress = 1.0
                else:
                    # Calculate partial progress
                    progress_scores = []
                    
                    if next_tier_req.min_subscriber_count > 0:
                        progress_scores.append(min(1.0, metrics.subscriber_count / next_tier_req.min_subscriber_count))
                    
                    if next_tier_req.min_content_count > 0:
                        progress_scores.append(min(1.0, metrics.content_count / next_tier_req.min_content_count))
                    
                    if next_tier_req.min_monthly_revenue > 0:
                        progress_scores.append(min(1.0, float(metrics.monthly_revenue / next_tier_req.min_monthly_revenue)))
                    
                    if progress_scores:
                        metrics.tier_progress = sum(progress_scores) / len(progress_scores)
                    else:
                        metrics.tier_progress = metrics.tier_score
            else:
                metrics.tier_progress = 1.0  # Already at highest tier
                
        except Exception as e:
            self.logger.error(f"❌ Error calculating tier score: {e}")
            metrics.tier_score = 0.0
            metrics.tier_progress = 0.0
    
    def _get_next_tier(self, current_tier: CreatorTier) -> Optional[CreatorTier]:
        """Get the next tier level"""
        tier_order = [
            CreatorTier.NEWCOMER,
            CreatorTier.RISING,
            CreatorTier.ESTABLISHED,
            CreatorTier.PROFESSIONAL,
            CreatorTier.ELITE,
            CreatorTier.LEGENDARY,
            CreatorTier.ENTERPRISE
        ]
        
        try:
            current_index = tier_order.index(current_tier)
            if current_index < len(tier_order) - 1:
                return tier_order[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    async def _evaluate_tier_progression(self, metrics: TierMetrics) -> Optional[Dict[str, Any]]:
        """Evaluate if creator should change tier"""
        try:
            current_tier = metrics.tier
            tier_change = None
            
            # Check for tier upgrade
            next_tier = self._get_next_tier(current_tier)
            if next_tier:
                next_tier_req = self._tier_requirements[next_tier]
                requirements_met, missing = next_tier_req.check_requirements(metrics)
                
                if requirements_met:
                    tier_change = {
                        "type": "upgrade",
                        "from_tier": current_tier.value,
                        "to_tier": next_tier.value,
                        "reason": "All requirements met",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    metrics.tier = next_tier  # Update metrics
                    self._analytics_metrics["tier_changes_processed"] += 1
            
            # Check for tier downgrade (if performance drops significantly)
            if not tier_change and current_tier != CreatorTier.NEWCOMER:
                tier_order = [CreatorTier.NEWCOMER, CreatorTier.RISING, CreatorTier.ESTABLISHED, 
                             CreatorTier.PROFESSIONAL, CreatorTier.ELITE, CreatorTier.LEGENDARY, CreatorTier.ENTERPRISE]
                current_index = tier_order.index(current_tier)
                
                if current_index > 0:
                    previous_tier = tier_order[current_index - 1]
                    current_tier_req = self._tier_requirements[current_tier]
                    requirements_met, missing = current_tier_req.check_requirements(metrics)
                    
                    if not requirements_met and len(missing) >= 3:  # Multiple requirements missed
                        tier_change = {
                            "type": "downgrade",
                            "from_tier": current_tier.value,
                            "to_tier": previous_tier.value,
                            "reason": f"Requirements not met: {', '.join(missing[:3])}",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        metrics.tier = previous_tier  # Update metrics
                        self._analytics_metrics["tier_changes_processed"] += 1
            
            return tier_change
            
        except Exception as e:
            self.logger.error(f"❌ Error evaluating tier progression: {e}")
            return None
    
    async def _update_tier_analytics(self, metrics: TierMetrics, tier_change: Optional[Dict[str, Any]]):
        """Update tier analytics data"""
        try:
            creator_id = metrics.creator_id
            
            # Update tier history
            history_entry = {
                "timestamp": metrics.timestamp.isoformat(),
                "tier": metrics.tier.value,
                "tier_score": metrics.tier_score,
                "tier_progress": metrics.tier_progress,
                "subscriber_count": metrics.subscriber_count,
                "monthly_revenue": str(metrics.monthly_revenue),
                "engagement_rate": metrics.engagement_rate
            }
            
            if tier_change:
                history_entry["tier_change"] = tier_change
            
            self._tier_history[creator_id].append(history_entry)
            
            # Keep only recent history
            retention_days = self._analytics_rules["history_retention_days"]
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            self._tier_history[creator_id] = [
                entry for entry in self._tier_history[creator_id]
                if datetime.fromisoformat(entry["timestamp"]) > cutoff_date
            ]
            
            self._analytics_metrics["analytics_generated"] += 1
            
        except Exception as e:
            self.logger.error(f"❌ Error updating tier analytics: {e}")
    
    async def _generate_tier_insights(self, metrics: TierMetrics) -> Dict[str, Any]:
        """Generate tier insights and recommendations"""
        try:
            insights = {
                "tier_assessment": self._assess_tier_performance(metrics),
                "growth_opportunities": self._identify_growth_opportunities(metrics),
                "recommendations": self._generate_recommendations(metrics),
                "milestones": self._identify_milestones(metrics),
                "trends": self._analyze_trends(metrics.creator_id)
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"❌ Error generating tier insights: {e}")
            return {}
    
    def _assess_tier_performance(self, metrics: TierMetrics) -> Dict[str, Any]:
        """Assess current tier performance"""
        performance_level = "poor"
        if metrics.tier_score >= self._analytics_rules["performance_thresholds"]["excellent"]:
            performance_level = "excellent"
        elif metrics.tier_score >= self._analytics_rules["performance_thresholds"]["good"]:
            performance_level = "good"
        elif metrics.tier_score >= self._analytics_rules["performance_thresholds"]["average"]:
            performance_level = "average"
        
        return {
            "current_tier": metrics.tier.value,
            "tier_score": metrics.tier_score,
            "performance_level": performance_level,
            "tier_progress": metrics.tier_progress,
            "strengths": self._identify_strengths(metrics),
            "weaknesses": self._identify_weaknesses(metrics)
        }
    
    def _identify_strengths(self, metrics: TierMetrics) -> List[str]:
        """Identify creator strengths"""
        strengths = []
        
        if metrics.engagement_rate > 0.1:
            strengths.append("High engagement rate")
        
        if metrics.content_quality_score > 0.8:
            strengths.append("High content quality")
        
        if metrics.upload_frequency > 3.0:
            strengths.append("Consistent content creation")
        
        if metrics.collaboration_count > 10:
            strengths.append("Strong collaboration network")
        
        if metrics.platform_diversity > 0.5:
            strengths.append("Multi-platform presence")
        
        if float(metrics.monthly_revenue) > 1000:
            strengths.append("Strong monetization")
        
        return strengths
    
    def _identify_weaknesses(self, metrics: TierMetrics) -> List[str]:
        """Identify areas for improvement"""
        weaknesses = []
        
        if metrics.engagement_rate < 0.02:
            weaknesses.append("Low engagement rate")
        
        if metrics.content_quality_score < 0.6:
            weaknesses.append("Content quality needs improvement")
        
        if metrics.upload_frequency < 1.0:
            weaknesses.append("Inconsistent content creation")
        
        if metrics.collaboration_count < 2:
            weaknesses.append("Limited collaboration network")
        
        if metrics.platform_diversity < 0.3:
            weaknesses.append("Single platform dependency")
        
        if float(metrics.monthly_revenue) < 100:
            weaknesses.append("Monetization opportunities unexplored")
        
        return weaknesses
    
    def _identify_growth_opportunities(self, metrics: TierMetrics) -> List[str]:
        """Identify growth opportunities"""
        opportunities = []
        
        next_tier = self._get_next_tier(metrics.tier)
        if next_tier:
            next_tier_req = self._tier_requirements[next_tier]
            requirements_met, missing = next_tier_req.check_requirements(metrics)
            
            if not requirements_met:
                for requirement in missing[:3]:  # Top 3 missing requirements
                    opportunities.append(f"Improve {requirement.split(':')[0]}")
        
        return opportunities
    
    def _generate_recommendations(self, metrics: TierMetrics) -> List[str]:
        """Generate specific recommendations"""
        recommendations = []
        
        if metrics.engagement_rate < 0.05:
            recommendations.append("Focus on audience engagement through interactive content")
        
        if metrics.upload_frequency < 2.0:
            recommendations.append("Establish a consistent content upload schedule")
        
        if metrics.collaboration_count < 5:
            recommendations.append("Seek collaboration opportunities with other creators")
        
        if metrics.platform_diversity < 0.4:
            recommendations.append("Expand to additional content platforms")
        
        if float(metrics.monthly_revenue) < 500:
            recommendations.append("Explore monetization strategies and revenue streams")
        
        return recommendations
    
    def _identify_milestones(self, metrics: TierMetrics) -> List[str]:
        """Identify upcoming milestones"""
        milestones = []
        
        # Subscriber milestones
        if metrics.subscriber_count < 1000:
            milestones.append("Reach 1,000 subscribers")
        elif metrics.subscriber_count < 10000:
            milestones.append("Reach 10,000 subscribers")
        elif metrics.subscriber_count < 100000:
            milestones.append("Reach 100,000 subscribers")
        
        # Revenue milestones
        if float(metrics.monthly_revenue) < 100:
            milestones.append("Reach $100 monthly revenue")
        elif float(metrics.monthly_revenue) < 1000:
            milestones.append("Reach $1,000 monthly revenue")
        elif float(metrics.monthly_revenue) < 10000:
            milestones.append("Reach $10,000 monthly revenue")
        
        return milestones
    
    def _analyze_trends(self, creator_id: str) -> Dict[str, Any]:
        """Analyze creator trends from history"""
        if creator_id not in self._tier_history or len(self._tier_history[creator_id]) < 2:
            return {"trend": "insufficient_data"}
        
        history = self._tier_history[creator_id]
        recent_entries = history[-5:]  # Last 5 entries
        
        # Analyze subscriber growth trend
        subscriber_counts = [entry["subscriber_count"] for entry in recent_entries]
        subscriber_trend = "stable"
        if len(subscriber_counts) >= 2:
            if subscriber_counts[-1] > subscriber_counts[0] * 1.1:
                subscriber_trend = "growing"
            elif subscriber_counts[-1] < subscriber_counts[0] * 0.9:
                subscriber_trend = "declining"
        
        # Analyze revenue trend
        revenues = [float(entry["monthly_revenue"]) for entry in recent_entries]
        revenue_trend = "stable"
        if len(revenues) >= 2:
            if revenues[-1] > revenues[0] * 1.1:
                revenue_trend = "growing"
            elif revenues[-1] < revenues[0] * 0.9:
                revenue_trend = "declining"
        
        return {
            "subscriber_trend": subscriber_trend,
            "revenue_trend": revenue_trend,
            "data_points": len(recent_entries),
            "analysis_period": "recent"
        }
    
    async def _cache_tier_metrics(self, metrics: TierMetrics):
        """Cache tier metrics"""
        if not self._redis_client:
            return
        
        try:
            # Cache metrics
            metrics_key = f"tier_analytics:metrics:{metrics.creator_id}"
            await self._redis_client.setex(
                metrics_key,
                86400 * 7,  # 7 days
                json.dumps(metrics.to_dict())
            )
            
            # Cache history
            history_key = f"tier_analytics:history:{metrics.creator_id}"
            await self._redis_client.setex(
                history_key,
                86400 * 30,  # 30 days
                json.dumps(self._tier_history[metrics.creator_id])
            )
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to cache tier metrics: {e}")
    
    async def _log_tier_analytics(self, metrics: TierMetrics, tier_change: Optional[Dict[str, Any]], insights: Dict[str, Any]):
        """Log tier analytics data"""
        try:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "log_type": "tier_analytics",
                "creator_id": metrics.creator_id,
                "metrics": metrics.to_dict(),
                "tier_change": tier_change,
                "insights": insights,
                "processor": "CreatorTierLogAnalyticsEngine",
                "version": "1.0.0"
            }
            
            # Log to structured format
            log_format = self.config.get("log_format", "json")
            if log_format == "json":
                self.logger.info(json.dumps(log_data))
            else:
                self.logger.info(f"TIER_ANALYTICS: {metrics.creator_id} | Tier: {metrics.tier.value} | Score: {metrics.tier_score:.2f}")
                
        except Exception as e:
            self.logger.error(f"❌ Error logging tier analytics: {e}")
    
    async def get_creator_tier_analytics(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive tier analytics for creator"""
        if creator_id not in self._creator_metrics:
            return None
        
        metrics = self._creator_metrics[creator_id]
        insights = await self._generate_tier_insights(metrics)
        
        return {
            "creator_id": creator_id,
            "current_metrics": metrics.to_dict(),
            "insights": insights,
            "history": self._tier_history.get(creator_id, []),
            "last_updated": metrics.timestamp.isoformat()
        }
    
    async def get_tier_distribution(self) -> Dict[str, Any]:
        """Get tier distribution analytics"""
        tier_counts = defaultdict(int)
        total_creators = len(self._creator_metrics)
        
        for metrics in self._creator_metrics.values():
            tier_counts[metrics.tier.value] += 1
        
        distribution = {}
        for tier in CreatorTier:
            count = tier_counts[tier.value]
            percentage = (count / total_creators * 100) if total_creators > 0 else 0
            distribution[tier.value] = {
                "count": count,
                "percentage": round(percentage, 2)
            }
        
        return {
            "total_creators": total_creators,
            "distribution": distribution,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_analytics_metrics(self) -> Dict[str, Any]:
        """Get analytics processing metrics"""
        metrics = self._analytics_metrics.copy()
        metrics["cached_creators"] = len(self._creator_metrics)
        metrics["total_history_entries"] = sum(len(history) for history in self._tier_history.values())
        metrics["uptime"] = "active"
        return metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        health = {
            "status": "healthy" if self._initialized else "unhealthy",
            "initialized": self._initialized,
            "redis_connected": self._redis_client is not None,
            "metrics": await self.get_analytics_metrics(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self._redis_client:
            try:
                await self._redis_client.ping()
                health["redis_status"] = "connected"
            except:
                health["redis_status"] = "disconnected"
        
        return health
    
    async def shutdown(self):
        """Shutdown analytics engine gracefully"""
        self.logger.info("🔄 Shutting down Creator Tier Log Analytics Engine...")
        
        if self._redis_client:
            await self._redis_client.close()
        
        self.logger.info("✅ Analytics engine shutdown complete")


# Example usage and testing
async def main():
    """Main function for testing"""
    engine = CreatorTierLogAnalyticsEngine({
        "output_path": "/tmp/tier_analytics",
        "analytics_interval": 3600,
        "log_format": "json",
        "redis": {"host": "localhost", "port": 6379}
    })
    
    # Test analytics
    test_log_data = {
        "creator_id": "creator_123",
        "tier": "rising",
        "subscriber_count": 1500,
        "content_count": 30,
        "monthly_revenue": "150.00",
        "engagement_rate": 0.06,
        "content_quality_score": 0.75,
        "upload_frequency": 2.5,
        "collaboration_count": 3,
        "platforms": ["youtube", "tiktok", "instagram"]
    }
    
    result = await engine.analyze_creator_tier("creator_123", test_log_data)
    print(f"Analysis result: {result}")
    
    # Get analytics
    analytics = await engine.get_creator_tier_analytics("creator_123")
    print(f"Creator analytics: {analytics}")
    
    # Get tier distribution
    distribution = await engine.get_tier_distribution()
    print(f"Tier distribution: {distribution}")
    
    # Health check
    health = await engine.health_check()
    print(f"Health check: {health}")
    
    await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())