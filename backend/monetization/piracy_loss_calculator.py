"""Piracy Loss Calculator - Revenue Loss Assessment Engine
========================================================

Enterprise-grade piracy impact assessment system providing intelligent
revenue loss calculation, market impact analysis, and financial damage
assessment for content piracy and unauthorized distribution.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/piracy_loss_calculator.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import math
from statistics import mean, median

logger = logging.getLogger(__name__)


class PiracyType(str, Enum):
    """Types of content piracy."""
    UNAUTHORIZED_DOWNLOAD = "unauthorized_download"
    STREAMING_PIRACY = "streaming_piracy"
    REDISTRIBUTION = "redistribution"
    COUNTERFEIT_SALES = "counterfeit_sales"
    SUBSCRIPTION_SHARING = "subscription_sharing"
    API_ABUSE = "api_abuse"
    CONTENT_SCRAPING = "content_scraping"
    DEEPFAKE_IMPERSONATION = "deepfake_impersonation"


class LossCategory(str, Enum):
    """Categories of revenue loss."""
    DIRECT_SALES_LOSS = "direct_sales_loss"
    SUBSCRIPTION_LOSS = "subscription_loss"
    ADVERTISING_LOSS = "advertising_loss"
    LICENSING_LOSS = "licensing_loss"
    BRAND_DAMAGE = "brand_damage"
    MARKET_SHARE_LOSS = "market_share_loss"
    OPPORTUNITY_COST = "opportunity_cost"


class CalculationMethod(str, Enum):
    """Loss calculation methodologies."""
    DIRECT_SUBSTITUTION = "direct_substitution"  # 1:1 piracy to lost sale
    MARKET_ANALYSIS = "market_analysis"          # Based on market data
    STATISTICAL_SAMPLING = "statistical_sampling" # Sample-based extrapolation
    ECONOMETRIC_MODEL = "econometric_model"      # Economic modeling
    HYBRID_APPROACH = "hybrid_approach"          # Multiple methods combined


@dataclass
class PiracyInstance:
    """Individual piracy instance details."""
    instance_id: str
    content_id: str
    piracy_type: PiracyType
    detection_date: datetime
    platform: str
    piracy_url: Optional[str]
    estimated_downloads: int
    estimated_views: int
    estimated_shares: int
    geographic_data: Dict[str, int]  # Country -> count
    quality_level: str  # "low", "medium", "high", "original"
    monetization_present: bool  # If pirate site has ads/monetization
    removal_status: str  # "active", "removed", "pending"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LossAssessment:
    """Revenue loss assessment result."""
    assessment_id: str
    creator_id: str
    content_id: str
    assessment_period: Tuple[datetime, datetime]
    piracy_instances: List[PiracyInstance]
    total_piracy_volume: int
    estimated_revenue_loss: Decimal
    loss_breakdown: Dict[LossCategory, Decimal]
    calculation_method: CalculationMethod
    confidence_level: float
    market_impact_score: float
    brand_damage_assessment: Dict[str, Any]
    recovery_potential: Decimal
    prevention_recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MarketData:
    """Market data for loss calculations."""
    content_type: str
    average_sale_price: Decimal
    conversion_rate: float
    market_penetration: float
    competition_factor: float
    price_elasticity: float
    seasonal_factors: Dict[str, float]
    geographic_pricing: Dict[str, Decimal]


@dataclass
class PiracyTrends:
    """Piracy trend analysis."""
    creator_id: str
    trend_period: Tuple[datetime, datetime]
    total_instances: int
    growth_rate: float
    platform_distribution: Dict[str, int]
    geographic_hotspots: List[str]
    peak_periods: List[str]
    most_targeted_content: List[str]
    trend_analysis: str


class PiracyLossCalculator:
    """
    Advanced piracy loss calculation engine.
    
    Provides intelligent revenue loss assessment using multiple
    calculation methodologies and market intelligence.
    """
    
    def __init__(self):
        """Initialize the piracy loss calculator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.piracy_instances: Dict[str, List[PiracyInstance]] = {}
        self.loss_assessments: Dict[str, List[LossAssessment]] = {}
        self.market_data_cache: Dict[str, MarketData] = {}
        self.conversion_models: Dict[str, Dict[str, float]] = {}
        self.initialized = False
        
        self.logger.info("PiracyLossCalculator initialized")
    
    async def initialize(self) -> bool:
        """Initialize the piracy loss calculator."""
        try:
            await self._load_market_data()
            await self._initialize_conversion_models()
            await self._load_calculation_parameters()
            
            self.initialized = True
            self.logger.info("PiracyLossCalculator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PiracyLossCalculator: {e}")
            return False
    
    async def _load_market_data(self):
        """Load market data for calculations."""
        # Sample market data
        self.market_data_cache = {
            "music": MarketData(
                content_type="music",
                average_sale_price=Decimal("1.29"),
                conversion_rate=0.05,
                market_penetration=0.75,
                competition_factor=0.8,
                price_elasticity=-1.2,
                seasonal_factors={"q1": 0.9, "q2": 1.0, "q3": 1.1, "q4": 1.3},
                geographic_pricing={"US": Decimal("1.29"), "EU": Decimal("1.19"), "ASIA": Decimal("0.99")}
            ),
            "video": MarketData(
                content_type="video",
                average_sale_price=Decimal("3.99"),
                conversion_rate=0.03,
                market_penetration=0.65,
                competition_factor=0.7,
                price_elasticity=-0.8,
                seasonal_factors={"q1": 0.85, "q2": 1.05, "q3": 1.15, "q4": 1.4},
                geographic_pricing={"US": Decimal("3.99"), "EU": Decimal("3.49"), "ASIA": Decimal("2.99")}
            ),
            "software": MarketData(
                content_type="software",
                average_sale_price=Decimal("49.99"),
                conversion_rate=0.08,
                market_penetration=0.45,
                competition_factor=0.6,
                price_elasticity=-1.5,
                seasonal_factors={"q1": 1.1, "q2": 0.9, "q3": 0.8, "q4": 1.2},
                geographic_pricing={"US": Decimal("49.99"), "EU": Decimal("45.99"), "ASIA": Decimal("29.99")}
            ),
            "ebook": MarketData(
                content_type="ebook",
                average_sale_price=Decimal("9.99"),
                conversion_rate=0.06,
                market_penetration=0.55,
                competition_factor=0.75,
                price_elasticity=-1.0,
                seasonal_factors={"q1": 1.0, "q2": 0.9, "q3": 0.95, "q4": 1.15},
                geographic_pricing={"US": Decimal("9.99"), "EU": Decimal("8.99"), "ASIA": Decimal("6.99")}
            )
        }
        
        self.logger.info("Market data loaded")
    
    async def _initialize_conversion_models(self):
        """Initialize piracy-to-loss conversion models."""
        # Different piracy types have different conversion rates
        self.conversion_models = {
            PiracyType.UNAUTHORIZED_DOWNLOAD.value: {
                "high_quality": 0.25,    # 25% would have bought
                "medium_quality": 0.15,  # 15% would have bought
                "low_quality": 0.08      # 8% would have bought
            },
            PiracyType.STREAMING_PIRACY.value: {
                "high_quality": 0.12,    # Lower conversion for streaming
                "medium_quality": 0.08,
                "low_quality": 0.04
            },
            PiracyType.REDISTRIBUTION.value: {
                "high_quality": 0.30,    # Higher impact for redistribution
                "medium_quality": 0.20,
                "low_quality": 0.12
            },
            PiracyType.COUNTERFEIT_SALES.value: {
                "high_quality": 0.40,    # Highest impact - direct sales competition
                "medium_quality": 0.30,
                "low_quality": 0.20
            },
            PiracyType.SUBSCRIPTION_SHARING.value: {
                "high_quality": 0.35,    # High impact on subscription revenue
                "medium_quality": 0.25,
                "low_quality": 0.15
            },
            PiracyType.API_ABUSE.value: {
                "high_quality": 0.20,
                "medium_quality": 0.12,
                "low_quality": 0.06
            }
        }
        
        self.logger.info("Conversion models initialized")
    
    async def _load_calculation_parameters(self):
        """Load calculation parameters and thresholds."""
        self.calculation_parameters = {
            "confidence_thresholds": {
                "high": 0.85,
                "medium": 0.65,
                "low": 0.40
            },
            "quality_multipliers": {
                "original": 1.0,
                "high": 0.8,
                "medium": 0.5,
                "low": 0.2
            },
            "platform_risk_factors": {
                "torrent": 1.2,
                "streaming": 0.8,
                "file_sharing": 1.0,
                "social_media": 0.6,
                "direct_download": 1.1
            },
            "geographic_risk_multipliers": {
                "US": 1.0,
                "EU": 0.9,
                "ASIA": 0.7,
                "OTHER": 0.5
            }
        }
        
        self.logger.info("Calculation parameters loaded")
    
    async def register_piracy_instance(
        self,
        content_id: str,
        piracy_type: PiracyType,
        platform: str,
        estimated_downloads: int = 0,
        estimated_views: int = 0,
        estimated_shares: int = 0,
        quality_level: str = "medium",
        piracy_url: Optional[str] = None,
        geographic_data: Optional[Dict[str, int]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register a new piracy instance."""
        try:
            instance_id = str(uuid4())
            
            instance = PiracyInstance(
                instance_id=instance_id,
                content_id=content_id,
                piracy_type=piracy_type,
                detection_date=datetime.now(),
                platform=platform,
                piracy_url=piracy_url,
                estimated_downloads=estimated_downloads,
                estimated_views=estimated_views,
                estimated_shares=estimated_shares,
                geographic_data=geographic_data or {},
                quality_level=quality_level,
                monetization_present=await self._detect_monetization(piracy_url, platform),
                removal_status="active",
                metadata=metadata or {}
            )
            
            if content_id not in self.piracy_instances:
                self.piracy_instances[content_id] = []
            
            self.piracy_instances[content_id].append(instance)
            
            self.logger.info(f"Registered piracy instance {instance_id} for content {content_id}")
            return instance_id
            
        except Exception as e:
            self.logger.error(f"Error registering piracy instance: {e}")
            raise
    
    async def _detect_monetization(self, piracy_url: Optional[str], platform: str) -> bool:
        """Detect if piracy site has monetization."""
        # In production, this would analyze the site for ads/monetization
        # For now, use platform-based heuristics
        monetized_platforms = ["streaming", "file_sharing", "direct_download"]
        return any(platform_type in platform.lower() for platform_type in monetized_platforms)
    
    async def calculate_revenue_loss(
        self,
        creator_id: str,
        content_id: str,
        content_type: str,
        assessment_period_days: int = 30,
        calculation_method: CalculationMethod = CalculationMethod.HYBRID_APPROACH
    ) -> LossAssessment:
        """Calculate revenue loss from piracy for content."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Get assessment period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=assessment_period_days)
            
            # Get piracy instances for the period
            content_instances = self.piracy_instances.get(content_id, [])
            period_instances = [
                instance for instance in content_instances
                if start_date <= instance.detection_date <= end_date
            ]
            
            if not period_instances:
                return await self._create_empty_assessment(
                    creator_id, content_id, (start_date, end_date), calculation_method
                )
            
            # Calculate loss based on method
            if calculation_method == CalculationMethod.DIRECT_SUBSTITUTION:
                loss_result = await self._calculate_direct_substitution_loss(
                    period_instances, content_type
                )
            elif calculation_method == CalculationMethod.MARKET_ANALYSIS:
                loss_result = await self._calculate_market_analysis_loss(
                    period_instances, content_type
                )
            elif calculation_method == CalculationMethod.STATISTICAL_SAMPLING:
                loss_result = await self._calculate_statistical_sampling_loss(
                    period_instances, content_type
                )
            elif calculation_method == CalculationMethod.ECONOMETRIC_MODEL:
                loss_result = await self._calculate_econometric_loss(
                    period_instances, content_type
                )
            else:  # HYBRID_APPROACH
                loss_result = await self._calculate_hybrid_loss(
                    period_instances, content_type
                )
            
            # Calculate additional metrics
            market_impact_score = await self._calculate_market_impact(period_instances, content_type)
            brand_damage = await self._assess_brand_damage(period_instances)
            recovery_potential = await self._calculate_recovery_potential(loss_result["total_loss"])
            recommendations = await self._generate_prevention_recommendations(period_instances)
            
            assessment = LossAssessment(
                assessment_id=str(uuid4()),
                creator_id=creator_id,
                content_id=content_id,
                assessment_period=(start_date, end_date),
                piracy_instances=period_instances,
                total_piracy_volume=sum(
                    instance.estimated_downloads + instance.estimated_views 
                    for instance in period_instances
                ),
                estimated_revenue_loss=loss_result["total_loss"],
                loss_breakdown=loss_result["breakdown"],
                calculation_method=calculation_method,
                confidence_level=loss_result["confidence"],
                market_impact_score=market_impact_score,
                brand_damage_assessment=brand_damage,
                recovery_potential=recovery_potential,
                prevention_recommendations=recommendations
            )
            
            # Store assessment
            if creator_id not in self.loss_assessments:
                self.loss_assessments[creator_id] = []
            self.loss_assessments[creator_id].append(assessment)
            
            self.logger.info(f"Calculated revenue loss for {content_id}: ${loss_result['total_loss']}")
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error calculating revenue loss: {e}")
            raise
    
    async def _create_empty_assessment(
        self,
        creator_id: str,
        content_id: str,
        period: Tuple[datetime, datetime],
        method: CalculationMethod
    ) -> LossAssessment:
        """Create empty assessment when no piracy instances found."""
        return LossAssessment(
            assessment_id=str(uuid4()),
            creator_id=creator_id,
            content_id=content_id,
            assessment_period=period,
            piracy_instances=[],
            total_piracy_volume=0,
            estimated_revenue_loss=Decimal("0"),
            loss_breakdown={},
            calculation_method=method,
            confidence_level=1.0,
            market_impact_score=0.0,
            brand_damage_assessment={},
            recovery_potential=Decimal("0"),
            prevention_recommendations=[]
        )
    
    async def _calculate_direct_substitution_loss(
        self,
        instances: List[PiracyInstance],
        content_type: str
    ) -> Dict[str, Any]:
        """Calculate loss using direct substitution method (1:1 piracy to lost sale)."""
        market_data = self.market_data_cache.get(content_type)
        if not market_data:
            market_data = self.market_data_cache["video"]  # Default
        
        total_loss = Decimal("0")
        breakdown = {}
        
        for instance in instances:
            # Get conversion rate based on piracy type and quality
            conversion_model = self.conversion_models.get(instance.piracy_type.value, {})
            conversion_rate = conversion_model.get(instance.quality_level, 0.10)
            
            # Calculate volume impact
            total_impact = instance.estimated_downloads + (instance.estimated_views * 0.1)  # Views count less
            
            # Apply conversion rate
            estimated_lost_sales = total_impact * conversion_rate
            
            # Calculate monetary loss
            price = market_data.average_sale_price
            instance_loss = Decimal(str(estimated_lost_sales)) * price
            
            # Apply quality multiplier
            quality_multiplier = self.calculation_parameters["quality_multipliers"].get(
                instance.quality_level, 0.5
            )
            instance_loss *= Decimal(str(quality_multiplier))
            
            total_loss += instance_loss
            
            # Categorize loss
            if instance.piracy_type in [PiracyType.UNAUTHORIZED_DOWNLOAD, PiracyType.COUNTERFEIT_SALES]:
                category = LossCategory.DIRECT_SALES_LOSS
            elif instance.piracy_type == PiracyType.SUBSCRIPTION_SHARING:
                category = LossCategory.SUBSCRIPTION_LOSS
            elif instance.piracy_type == PiracyType.STREAMING_PIRACY:
                category = LossCategory.ADVERTISING_LOSS
            else:
                category = LossCategory.LICENSING_LOSS
            
            if category not in breakdown:
                breakdown[category] = Decimal("0")
            breakdown[category] += instance_loss
        
        # Calculate confidence based on data quality
        confidence = min(0.9, 0.6 + (len(instances) * 0.05))  # Higher confidence with more data
        
        return {
            "total_loss": total_loss,
            "breakdown": breakdown,
            "confidence": confidence
        }
    
    async def _calculate_market_analysis_loss(
        self,
        instances: List[PiracyInstance],
        content_type: str
    ) -> Dict[str, Any]:
        """Calculate loss using market analysis method."""
        market_data = self.market_data_cache.get(content_type)
        if not market_data:
            market_data = self.market_data_cache["video"]
        
        # Market analysis considers broader market impact
        total_piracy_volume = sum(
            instance.estimated_downloads + instance.estimated_views
            for instance in instances
        )
        
        # Apply market penetration factor
        market_adjusted_volume = total_piracy_volume * market_data.market_penetration
        
        # Apply competition factor (less loss if many alternatives exist)
        competition_adjusted_volume = market_adjusted_volume * market_data.competition_factor
        
        # Apply conversion rate
        converted_volume = competition_adjusted_volume * market_data.conversion_rate
        
        # Calculate monetary loss
        total_loss = Decimal(str(converted_volume)) * market_data.average_sale_price
        
        # Apply price elasticity (higher elasticity = lower loss)
        elasticity_factor = 1 + (market_data.price_elasticity * 0.1)  # Moderate elasticity impact
        total_loss *= Decimal(str(elasticity_factor))
        
        # Breakdown by category
        breakdown = {
            LossCategory.DIRECT_SALES_LOSS: total_loss * Decimal("0.6"),
            LossCategory.MARKET_SHARE_LOSS: total_loss * Decimal("0.25"),
            LossCategory.OPPORTUNITY_COST: total_loss * Decimal("0.15")
        }
        
        confidence = 0.75  # Market analysis typically has medium-high confidence
        
        return {
            "total_loss": total_loss,
            "breakdown": breakdown,
            "confidence": confidence
        }
    
    async def _calculate_statistical_sampling_loss(
        self,
        instances: List[PiracyInstance],
        content_type: str
    ) -> Dict[str, Any]:
        """Calculate loss using statistical sampling method."""
        # Use representative sample to extrapolate total loss
        sample_size = min(len(instances), 10)  # Sample up to 10 instances
        sample_instances = instances[:sample_size]
        
        # Calculate loss for sample
        sample_result = await self._calculate_direct_substitution_loss(sample_instances, content_type)
        
        # Extrapolate to full population
        if sample_size > 0:
            extrapolation_factor = len(instances) / sample_size
            total_loss = sample_result["total_loss"] * Decimal(str(extrapolation_factor))
            
            # Apply confidence penalty for extrapolation
            confidence = sample_result["confidence"] * (0.8 + (sample_size * 0.02))
        else:
            total_loss = Decimal("0")
            confidence = 0.0
        
        # Scale breakdown
        breakdown = {
            category: amount * Decimal(str(extrapolation_factor))
            for category, amount in sample_result["breakdown"].items()
        }
        
        return {
            "total_loss": total_loss,
            "breakdown": breakdown,
            "confidence": confidence
        }
    
    async def _calculate_econometric_loss(
        self,
        instances: List[PiracyInstance],
        content_type: str
    ) -> Dict[str, Any]:
        """Calculate loss using econometric modeling."""
        market_data = self.market_data_cache.get(content_type)
        if not market_data:
            market_data = self.market_data_cache["video"]
        
        # Econometric model considers multiple factors
        total_volume = sum(
            instance.estimated_downloads + instance.estimated_views
            for instance in instances
        )
        
        # Base loss calculation
        base_loss = Decimal(str(total_volume * market_data.conversion_rate)) * market_data.average_sale_price
        
        # Apply econometric adjustments
        
        # 1. Market saturation effect (diminishing returns)
        saturation_factor = 1 / (1 + (total_volume / 100000))  # Saturation at 100k volume
        
        # 2. Network effects (piracy can reduce network value)
        network_effect = min(0.2, total_volume / 500000)  # Up to 20% additional loss
        
        # 3. Time decay (older piracy has less impact)
        time_weights = []
        now = datetime.now()
        for instance in instances:
            days_old = (now - instance.detection_date).days
            weight = max(0.1, 1 - (days_old / 365))  # Decay over a year
            time_weights.append(weight)
        
        avg_time_weight = mean(time_weights) if time_weights else 1.0
        
        # Apply all factors
        adjusted_loss = base_loss * Decimal(str(saturation_factor)) * Decimal(str(1 + network_effect)) * Decimal(str(avg_time_weight))
        
        # Breakdown
        breakdown = {
            LossCategory.DIRECT_SALES_LOSS: adjusted_loss * Decimal("0.5"),
            LossCategory.MARKET_SHARE_LOSS: adjusted_loss * Decimal("0.2"),
            LossCategory.BRAND_DAMAGE: adjusted_loss * Decimal("0.15"),
            LossCategory.OPPORTUNITY_COST: adjusted_loss * Decimal("0.15")
        }
        
        confidence = 0.85  # Econometric models typically high confidence
        
        return {
            "total_loss": adjusted_loss,
            "breakdown": breakdown,
            "confidence": confidence
        }
    
    async def _calculate_hybrid_loss(
        self,
        instances: List[PiracyInstance],
        content_type: str
    ) -> Dict[str, Any]:
        """Calculate loss using hybrid approach (combines multiple methods)."""
        
        # Calculate using different methods
        direct_result = await self._calculate_direct_substitution_loss(instances, content_type)
        market_result = await self._calculate_market_analysis_loss(instances, content_type)
        econometric_result = await self._calculate_econometric_loss(instances, content_type)
        
        # Weight the results based on data quality and instance count
        weights = {
            "direct": 0.4,
            "market": 0.3,
            "econometric": 0.3
        }
        
        # Adjust weights based on instance count
        if len(instances) < 5:
            weights["direct"] = 0.6  # Rely more on direct method for small samples
            weights["market"] = 0.25
            weights["econometric"] = 0.15
        elif len(instances) > 50:
            weights["econometric"] = 0.5  # Rely more on econometric for large samples
            weights["market"] = 0.3
            weights["direct"] = 0.2
        
        # Calculate weighted average
        weighted_loss = (
            direct_result["total_loss"] * Decimal(str(weights["direct"])) +
            market_result["total_loss"] * Decimal(str(weights["market"])) +
            econometric_result["total_loss"] * Decimal(str(weights["econometric"]))
        )
        
        # Combine breakdowns
        all_categories = set()
        all_categories.update(direct_result["breakdown"].keys())
        all_categories.update(market_result["breakdown"].keys())
        all_categories.update(econometric_result["breakdown"].keys())
        
        weighted_breakdown = {}
        for category in all_categories:
            direct_amount = direct_result["breakdown"].get(category, Decimal("0"))
            market_amount = market_result["breakdown"].get(category, Decimal("0"))
            econometric_amount = econometric_result["breakdown"].get(category, Decimal("0"))
            
            weighted_amount = (
                direct_amount * Decimal(str(weights["direct"])) +
                market_amount * Decimal(str(weights["market"])) +
                econometric_amount * Decimal(str(weights["econometric"]))
            )
            
            if weighted_amount > 0:
                weighted_breakdown[category] = weighted_amount
        
        # Calculate weighted confidence
        weighted_confidence = (
            direct_result["confidence"] * weights["direct"] +
            market_result["confidence"] * weights["market"] +
            econometric_result["confidence"] * weights["econometric"]
        )
        
        return {
            "total_loss": weighted_loss,
            "breakdown": weighted_breakdown,
            "confidence": weighted_confidence
        }
    
    async def _calculate_market_impact(self, instances: List[PiracyInstance], content_type: str) -> float:
        """Calculate market impact score (0-1)."""
        if not instances:
            return 0.0
        
        # Factors affecting market impact
        total_volume = sum(instance.estimated_downloads + instance.estimated_views for instance in instances)
        platform_diversity = len(set(instance.platform for instance in instances))
        geographic_spread = len(set().union(*[instance.geographic_data.keys() for instance in instances]))
        
        # Normalize factors
        volume_score = min(1.0, total_volume / 100000)  # Normalize to 100k
        platform_score = min(1.0, platform_diversity / 10)  # Normalize to 10 platforms
        geographic_score = min(1.0, geographic_spread / 20)  # Normalize to 20 countries
        
        # Calculate weighted impact
        impact_score = (volume_score * 0.5 + platform_score * 0.3 + geographic_score * 0.2)
        
        return impact_score
    
    async def _assess_brand_damage(self, instances: List[PiracyInstance]) -> Dict[str, Any]:
        """Assess brand damage from piracy."""
        if not instances:
            return {}
        
        # Factors contributing to brand damage
        low_quality_instances = sum(1 for instance in instances if instance.quality_level == "low")
        monetized_instances = sum(1 for instance in instances if instance.monetization_present)
        
        damage_score = (
            (low_quality_instances / len(instances)) * 0.6 +  # Low quality hurts brand
            (monetized_instances / len(instances)) * 0.4      # Monetized piracy hurts more
        )
        
        return {
            "damage_score": damage_score,
            "reputation_impact": "high" if damage_score > 0.7 else "medium" if damage_score > 0.4 else "low",
            "quality_degradation_risk": low_quality_instances / len(instances),
            "unauthorized_monetization_risk": monetized_instances / len(instances)
        }
    
    async def _calculate_recovery_potential(self, total_loss: Decimal) -> Decimal:
        """Calculate potential recoverable amount."""
        # Recovery rates vary by loss amount and type
        if total_loss > Decimal("10000"):
            recovery_rate = 0.4  # 40% for large losses (worth legal action)
        elif total_loss > Decimal("1000"):
            recovery_rate = 0.25  # 25% for medium losses
        else:
            recovery_rate = 0.1   # 10% for small losses
        
        return total_loss * Decimal(str(recovery_rate))
    
    async def _generate_prevention_recommendations(self, instances: List[PiracyInstance]) -> List[str]:
        """Generate recommendations to prevent future piracy."""
        recommendations = []
        
        if not instances:
            return ["Implement proactive content monitoring", "Use content fingerprinting technology"]
        
        # Analyze piracy patterns
        platforms = [instance.platform for instance in instances]
        piracy_types = [instance.piracy_type for instance in instances]
        
        # Platform-specific recommendations
        if "torrent" in platforms:
            recommendations.append("Implement torrent monitoring and takedown automation")
        
        if "streaming" in platforms:
            recommendations.append("Deploy streaming site detection and content blocking")
        
        if "social_media" in platforms:
            recommendations.append("Set up social media content monitoring and DMCA automation")
        
        # Type-specific recommendations
        if PiracyType.UNAUTHORIZED_DOWNLOAD in piracy_types:
            recommendations.append("Implement digital watermarking and download tracking")
        
        if PiracyType.SUBSCRIPTION_SHARING in piracy_types:
            recommendations.append("Deploy account sharing detection and prevention measures")
        
        if PiracyType.API_ABUSE in piracy_types:
            recommendations.append("Implement API rate limiting and abuse detection")
        
        # General recommendations
        if len(instances) > 10:
            recommendations.append("Consider legal action for systematic infringement")
        
        recommendations.append("Implement content release strategy to minimize piracy window")
        recommendations.append("Use blockchain or DRM technology for content protection")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def get_piracy_trends(
        self,
        creator_id: str,
        trend_period_days: int = 90
    ) -> PiracyTrends:
        """Analyze piracy trends for a creator."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=trend_period_days)
        
        # Get all instances for creator content
        all_instances = []
        for content_id, instances in self.piracy_instances.items():
            period_instances = [
                instance for instance in instances
                if start_date <= instance.detection_date <= end_date
            ]
            all_instances.extend(period_instances)
        
        if not all_instances:
            return PiracyTrends(
                creator_id=creator_id,
                trend_period=(start_date, end_date),
                total_instances=0,
                growth_rate=0.0,
                platform_distribution={},
                geographic_hotspots=[],
                peak_periods=[],
                most_targeted_content=[],
                trend_analysis="No piracy detected in this period"
            )
        
        # Calculate growth rate
        mid_date = start_date + timedelta(days=trend_period_days//2)
        first_half = [i for i in all_instances if i.detection_date < mid_date]
        second_half = [i for i in all_instances if i.detection_date >= mid_date]
        
        if len(first_half) > 0:
            growth_rate = (len(second_half) - len(first_half)) / len(first_half)
        else:
            growth_rate = 1.0 if len(second_half) > 0 else 0.0
        
        # Platform distribution
        platform_counts = {}
        for instance in all_instances:
            platform_counts[instance.platform] = platform_counts.get(instance.platform, 0) + 1
        
        # Geographic analysis
        geographic_data = {}
        for instance in all_instances:
            for country, count in instance.geographic_data.items():
                geographic_data[country] = geographic_data.get(country, 0) + count
        
        geographic_hotspots = sorted(geographic_data.keys(), key=geographic_data.get, reverse=True)[:5]
        
        # Content analysis
        content_counts = {}
        for instance in all_instances:
            content_counts[instance.content_id] = content_counts.get(instance.content_id, 0) + 1
        
        most_targeted = sorted(content_counts.keys(), key=content_counts.get, reverse=True)[:3]
        
        # Generate trend analysis
        if growth_rate > 0.2:
            trend_analysis = f"⚠️ Piracy incidents increasing rapidly ({growth_rate:.1%} growth)"
        elif growth_rate > 0:
            trend_analysis = f"📈 Moderate increase in piracy incidents ({growth_rate:.1%} growth)"
        elif growth_rate < -0.2:
            trend_analysis = f"📉 Significant decrease in piracy incidents ({growth_rate:.1%} change)"
        else:
            trend_analysis = "📊 Piracy levels stable"
        
        return PiracyTrends(
            creator_id=creator_id,
            trend_period=(start_date, end_date),
            total_instances=len(all_instances),
            growth_rate=growth_rate,
            platform_distribution=platform_counts,
            geographic_hotspots=geographic_hotspots,
            peak_periods=[],  # Would need more sophisticated analysis
            most_targeted_content=most_targeted,
            trend_analysis=trend_analysis
        )
    
    async def get_loss_summary(
        self,
        creator_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get loss summary for creator."""
        assessments = self.loss_assessments.get(creator_id, [])
        
        # Filter to period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        period_assessments = [
            assessment for assessment in assessments
            if assessment.assessment_period[1] >= start_date
        ]
        
        if not period_assessments:
            return {
                "total_loss": 0.0,
                "recovery_potential": 0.0,
                "assessments_count": 0,
                "average_confidence": 0.0
            }
        
        total_loss = sum(assessment.estimated_revenue_loss for assessment in period_assessments)
        total_recovery_potential = sum(assessment.recovery_potential for assessment in period_assessments)
        avg_confidence = mean([assessment.confidence_level for assessment in period_assessments])
        
        return {
            "total_loss": float(total_loss),
            "recovery_potential": float(total_recovery_potential),
            "assessments_count": len(period_assessments),
            "average_confidence": avg_confidence,
            "period_days": period_days
        }


# Global instance
_piracy_loss_calculator = None


async def get_piracy_loss_calculator() -> PiracyLossCalculator:
    """Get the global piracy loss calculator instance."""
    global _piracy_loss_calculator
    
    if _piracy_loss_calculator is None:
        _piracy_loss_calculator = PiracyLossCalculator()
        await _piracy_loss_calculator.initialize()
    
    return _piracy_loss_calculator


# Example usage
async def main():
    """Example usage of PiracyLossCalculator."""
    calculator = await get_piracy_loss_calculator()
    
    creator_id = "creator_123"
    content_id = "music_track_456"
    
    # Register piracy instances
    instance1_id = await calculator.register_piracy_instance(
        content_id=content_id,
        piracy_type=PiracyType.UNAUTHORIZED_DOWNLOAD,
        platform="torrent",
        estimated_downloads=5000,
        estimated_views=0,
        estimated_shares=200,
        quality_level="high",
        geographic_data={"US": 2000, "EU": 1500, "ASIA": 1500}
    )
    
    instance2_id = await calculator.register_piracy_instance(
        content_id=content_id,
        piracy_type=PiracyType.STREAMING_PIRACY,
        platform="streaming",
        estimated_downloads=0,
        estimated_views=15000,
        estimated_shares=500,
        quality_level="medium",
        geographic_data={"US": 6000, "EU": 4000, "ASIA": 5000}
    )
    
    print(f"Registered piracy instances: {instance1_id[:8]}, {instance2_id[:8]}")
    
    # Calculate revenue loss
    assessment = await calculator.calculate_revenue_loss(
        creator_id=creator_id,
        content_id=content_id,
        content_type="music",
        assessment_period_days=30,
        calculation_method=CalculationMethod.HYBRID_APPROACH
    )
    
    print(f"\n💰 Revenue Loss Assessment for {content_id}")
    print(f"Total Estimated Loss: ${assessment.estimated_revenue_loss:,.2f}")
    print(f"Calculation Method: {assessment.calculation_method.value}")
    print(f"Confidence Level: {assessment.confidence_level:.1%}")
    print(f"Market Impact Score: {assessment.market_impact_score:.2f}")
    print(f"Recovery Potential: ${assessment.recovery_potential:,.2f}")
    
    print(f"\n📊 Loss Breakdown:")
    for category, amount in assessment.loss_breakdown.items():
        print(f"  • {category.value.replace('_', ' ').title()}: ${amount:,.2f}")
    
    print(f"\n⚠️ Brand Damage Assessment:")
    for key, value in assessment.brand_damage_assessment.items():
        print(f"  • {key.replace('_', ' ').title()}: {value}")
    
    print(f"\n💡 Prevention Recommendations:")
    for i, rec in enumerate(assessment.prevention_recommendations, 1):
        print(f"  {i}. {rec}")
    
    # Get piracy trends
    trends = await calculator.get_piracy_trends(creator_id, trend_period_days=30)
    
    print(f"\n📈 Piracy Trends (Last 30 days):")
    print(f"Total Instances: {trends.total_instances}")
    print(f"Growth Rate: {trends.growth_rate:+.1%}")
    print(f"Analysis: {trends.trend_analysis}")
    
    print(f"\nTop Platforms:")
    for platform, count in list(trends.platform_distribution.items())[:3]:
        print(f"  • {platform}: {count} instances")
    
    print(f"\nGeographic Hotspots:")
    for hotspot in trends.geographic_hotspots[:3]:
        print(f"  • {hotspot}")
    
    # Get loss summary
    summary = await calculator.get_loss_summary(creator_id, period_days=30)
    print(f"\n📋 Loss Summary (Last 30 days):")
    print(f"Total Loss: ${summary['total_loss']:,.2f}")
    print(f"Recovery Potential: ${summary['recovery_potential']:,.2f}")
    print(f"Assessments: {summary['assessments_count']}")
    print(f"Average Confidence: {summary['average_confidence']:.1%}")


if __name__ == "__main__":
    asyncio.run(main())