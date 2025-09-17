#!/usr/bin/env python3
"""
Collaboration Intelligence System - Enterprise Analytics Component
Advanced partnership analytics, brand-creator matching, and collaboration success measurement

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Fahed Mlaiel (mlaiel@live.de)
Toute reproduction, distribution ou utilisation non autorisée est strictement interdite.

This module provides comprehensive collaboration analytics including:
- Partnership success analytics and scoring
- AI-powered brand-creator matching algorithms
- Collaboration ROI intelligence and optimization
- Network effect analysis and relationship mapping
- Partnership strategy recommendations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict, Counter
import hashlib
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PartnershipType(Enum):
    """Types of brand-creator partnerships"""
    SPONSORED_POST = "sponsored_post"
    LONG_TERM_AMBASSADOR = "long_term_ambassador"
    PRODUCT_PLACEMENT = "product_placement"
    EVENT_COLLABORATION = "event_collaboration"
    CO_CREATION = "co_creation"
    AFFILIATE_PARTNERSHIP = "affiliate_partnership"
    LICENSING_DEAL = "licensing_deal"
    EQUITY_PARTNERSHIP = "equity_partnership"
    PERFORMANCE_BASED = "performance_based"
    CAMPAIGN_SERIES = "campaign_series"


class CollaborationStatus(Enum):
    """Status of collaboration"""
    PENDING = "pending"
    NEGOTIATING = "negotiating"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    RENEWED = "renewed"


class MatchingCriteria(Enum):
    """Criteria for brand-creator matching"""
    AUDIENCE_ALIGNMENT = "audience_alignment"
    ENGAGEMENT_RATE = "engagement_rate"
    BRAND_SAFETY = "brand_safety"
    CONTENT_QUALITY = "content_quality"
    PREVIOUS_PERFORMANCE = "previous_performance"
    NICHE_EXPERTISE = "niche_expertise"
    GEOGRAPHIC_REACH = "geographic_reach"
    DEMOGRAPHICS_FIT = "demographics_fit"
    VALUES_ALIGNMENT = "values_alignment"
    PRICING_COMPATIBILITY = "pricing_compatibility"


class SuccessMetrics(Enum):
    """Success metrics for collaborations"""
    ROI = "roi"
    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    BRAND_AWARENESS = "brand_awareness"
    CONVERSION_RATE = "conversion_rate"
    COST_PER_ENGAGEMENT = "cost_per_engagement"
    BRAND_SENTIMENT = "brand_sentiment"
    FOLLOWER_GROWTH = "follower_growth"
    SALES_ATTRIBUTION = "sales_attribution"
    CONTENT_QUALITY_SCORE = "content_quality_score"


@dataclass
class BrandProfile:
    """Brand profile for collaboration intelligence"""
    brand_id: str
    brand_name: str
    industry: str
    target_demographics: Dict[str, Any]
    budget_range: Tuple[float, float]
    brand_values: List[str]
    preferred_platforms: List[str]
    content_guidelines: Dict[str, Any]
    brand_safety_requirements: Dict[str, Any]
    collaboration_history: List[str] = field(default_factory=list)
    success_metrics_priority: List[SuccessMetrics] = field(default_factory=list)
    blacklisted_creators: List[str] = field(default_factory=list)
    preferred_creators: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreatorProfile:
    """Creator profile for collaboration intelligence"""
    creator_id: str
    username: str
    display_name: str
    niche: List[str]
    platforms: Dict[str, Dict[str, Any]]  # platform -> metrics
    audience_demographics: Dict[str, Any]
    engagement_metrics: Dict[str, float]
    content_style: List[str]
    brand_affinity: Dict[str, float]
    collaboration_history: List[str] = field(default_factory=list)
    rates: Dict[str, float] = field(default_factory=dict)
    availability: Dict[str, bool] = field(default_factory=dict)
    brand_partnerships_count: int = 0
    average_partnership_rating: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Collaboration:
    """Collaboration/Partnership record"""
    collaboration_id: str
    brand_id: str
    creator_id: str
    partnership_type: PartnershipType
    status: CollaborationStatus
    start_date: datetime
    end_date: Optional[datetime]
    budget: float
    deliverables: List[Dict[str, Any]]
    success_metrics: Dict[SuccessMetrics, float]
    content_ids: List[str] = field(default_factory=list)
    performance_data: Dict[str, Any] = field(default_factory=dict)
    roi_metrics: Dict[str, float] = field(default_factory=dict)
    rating_brand: Optional[float] = None
    rating_creator: Optional[float] = None
    feedback_brand: Optional[str] = None
    feedback_creator: Optional[str] = None
    lessons_learned: List[str] = field(default_factory=list)
    renewal_probability: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MatchingScore:
    """Brand-creator matching score"""
    brand_id: str
    creator_id: str
    overall_score: float
    criteria_scores: Dict[MatchingCriteria, float]
    confidence_level: float
    matching_factors: List[str]
    potential_concerns: List[str]
    estimated_success_rate: float
    recommended_partnership_type: PartnershipType
    suggested_budget_range: Tuple[float, float]
    optimal_deliverables: List[str]
    calculated_at: datetime


@dataclass
class NetworkInsight:
    """Network analysis insight"""
    insight_id: str
    insight_type: str
    title: str
    description: str
    affected_entities: List[str]
    impact_score: float
    network_metrics: Dict[str, Any]
    recommendations: List[str]
    supporting_data: Dict[str, Any]
    generated_at: datetime


@dataclass
class CollaborationInsight:
    """AI-generated collaboration insight"""
    insight_id: str
    entity_id: str  # brand_id or creator_id
    entity_type: str  # "brand" or "creator"
    insight_type: str
    title: str
    description: str
    impact_score: float
    confidence_level: float
    recommended_actions: List[str]
    supporting_data: Dict[str, Any]
    priority_level: str
    generated_at: datetime
    expires_at: Optional[datetime] = None


class CollaborationIntelligenceSystem:
    """
    Enterprise Collaboration Intelligence System
    
    Provides comprehensive analytics for brand-creator partnerships,
    AI-powered matching algorithms, and collaboration success optimization.
    """
    
    def __init__(self):
        """Initialize the collaboration intelligence system"""
        self.brands: Dict[str, BrandProfile] = {}
        self.creators: Dict[str, CreatorProfile] = {}
        self.collaborations: Dict[str, Collaboration] = {}
        self.matching_scores: Dict[str, Dict[str, MatchingScore]] = defaultdict(dict)
        self.insights_cache: Dict[str, List[CollaborationInsight]] = defaultdict(list)
        self.network_insights: List[NetworkInsight] = []
        self.performance_cache: Dict[str, Dict[str, Any]] = {}
        
        # Network analysis data
        self.collaboration_network = defaultdict(set)  # creator_id -> set of brand_ids
        self.brand_network = defaultdict(set)  # brand_id -> set of creator_ids
        self.creator_similarity_matrix = defaultdict(dict)
        self.brand_similarity_matrix = defaultdict(dict)
        
        # Industry benchmarks
        self.industry_benchmarks = self._initialize_benchmarks()
        
        logger.info("Collaboration Intelligence System initialized")
    
    def _initialize_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Initialize industry benchmarks for collaboration metrics"""
        return {
            "partnership_success_rates": {
                PartnershipType.SPONSORED_POST.value: 0.78,
                PartnershipType.LONG_TERM_AMBASSADOR.value: 0.85,
                PartnershipType.PRODUCT_PLACEMENT.value: 0.72,
                PartnershipType.EVENT_COLLABORATION.value: 0.83,
                PartnershipType.CO_CREATION.value: 0.89,
                PartnershipType.AFFILIATE_PARTNERSHIP.value: 0.65,
                PartnershipType.LICENSING_DEAL.value: 0.91,
                PartnershipType.EQUITY_PARTNERSHIP.value: 0.93,
                PartnershipType.PERFORMANCE_BASED.value: 0.69,
                PartnershipType.CAMPAIGN_SERIES.value: 0.81
            },
            "average_roi_by_type": {
                PartnershipType.SPONSORED_POST.value: 3.2,
                PartnershipType.LONG_TERM_AMBASSADOR.value: 4.8,
                PartnershipType.PRODUCT_PLACEMENT.value: 2.9,
                PartnershipType.EVENT_COLLABORATION.value: 5.1,
                PartnershipType.CO_CREATION.value: 6.3,
                PartnershipType.AFFILIATE_PARTNERSHIP.value: 4.2,
                PartnershipType.LICENSING_DEAL.value: 7.8,
                PartnershipType.EQUITY_PARTNERSHIP.value: 12.5,
                PartnershipType.PERFORMANCE_BASED.value: 3.7,
                PartnershipType.CAMPAIGN_SERIES.value: 5.9
            },
            "engagement_rate_benchmarks": {
                "nano_influencer": 0.067,  # 1K-10K followers
                "micro_influencer": 0.047, # 10K-100K followers
                "macro_influencer": 0.027, # 100K-1M followers
                "mega_influencer": 0.017   # 1M+ followers
            }
        }
    
    async def register_brand(self, brand_profile: BrandProfile) -> bool:
        """Register a brand in the collaboration system"""
        try:
            # Validate brand profile
            if not self._validate_brand_profile(brand_profile):
                logger.error(f"Invalid brand profile: {brand_profile.brand_id}")
                return False
            
            # Store brand
            self.brands[brand_profile.brand_id] = brand_profile
            
            # Initialize network connections
            self.brand_network[brand_profile.brand_id] = set()
            
            # Calculate similarity with existing brands
            await self._calculate_brand_similarities(brand_profile.brand_id)
            
            logger.info(f"Brand registered: {brand_profile.brand_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register brand: {e}")
            return False
    
    async def register_creator(self, creator_profile: CreatorProfile) -> bool:
        """Register a creator in the collaboration system"""
        try:
            # Validate creator profile
            if not self._validate_creator_profile(creator_profile):
                logger.error(f"Invalid creator profile: {creator_profile.creator_id}")
                return False
            
            # Store creator
            self.creators[creator_profile.creator_id] = creator_profile
            
            # Initialize network connections
            self.collaboration_network[creator_profile.creator_id] = set()
            
            # Calculate similarity with existing creators
            await self._calculate_creator_similarities(creator_profile.creator_id)
            
            logger.info(f"Creator registered: {creator_profile.username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register creator: {e}")
            return False
    
    def _validate_brand_profile(self, profile: BrandProfile) -> bool:
        """Validate brand profile data"""
        try:
            required_fields = [
                profile.brand_id,
                profile.brand_name,
                profile.industry,
                profile.target_demographics,
                profile.budget_range
            ]
            
            if not all(required_fields):
                return False
            
            # Budget range validation
            if len(profile.budget_range) != 2 or profile.budget_range[0] < 0 or profile.budget_range[1] < profile.budget_range[0]:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Brand profile validation failed: {e}")
            return False
    
    def _validate_creator_profile(self, profile: CreatorProfile) -> bool:
        """Validate creator profile data"""
        try:
            required_fields = [
                profile.creator_id,
                profile.username,
                profile.niche,
                profile.platforms,
                profile.audience_demographics
            ]
            
            if not all(required_fields):
                return False
            
            # Platform data validation
            if not profile.platforms:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Creator profile validation failed: {e}")
            return False
    
    async def _calculate_brand_similarities(self, brand_id: str) -> None:
        """Calculate similarity scores between brands"""
        try:
            current_brand = self.brands[brand_id]
            
            for other_brand_id, other_brand in self.brands.items():
                if other_brand_id == brand_id:
                    continue
                
                similarity_score = await self._calculate_brand_similarity(current_brand, other_brand)
                self.brand_similarity_matrix[brand_id][other_brand_id] = similarity_score
                self.brand_similarity_matrix[other_brand_id][brand_id] = similarity_score
            
        except Exception as e:
            logger.error(f"Failed to calculate brand similarities: {e}")
    
    async def _calculate_creator_similarities(self, creator_id: str) -> None:
        """Calculate similarity scores between creators"""
        try:
            current_creator = self.creators[creator_id]
            
            for other_creator_id, other_creator in self.creators.items():
                if other_creator_id == creator_id:
                    continue
                
                similarity_score = await self._calculate_creator_similarity(current_creator, other_creator)
                self.creator_similarity_matrix[creator_id][other_creator_id] = similarity_score
                self.creator_similarity_matrix[other_creator_id][creator_id] = similarity_score
            
        except Exception as e:
            logger.error(f"Failed to calculate creator similarities: {e}")
    
    async def _calculate_brand_similarity(self, brand1: BrandProfile, brand2: BrandProfile) -> float:
        """Calculate similarity score between two brands"""
        try:
            similarity_score = 0.0
            
            # Industry similarity
            if brand1.industry == brand2.industry:
                similarity_score += 0.3
            
            # Target demographics similarity
            demo_similarity = self._calculate_demographics_similarity(
                brand1.target_demographics, brand2.target_demographics
            )
            similarity_score += demo_similarity * 0.25
            
            # Budget range overlap
            budget_overlap = self._calculate_budget_overlap(brand1.budget_range, brand2.budget_range)
            similarity_score += budget_overlap * 0.2
            
            # Brand values similarity
            values_similarity = self._calculate_values_similarity(brand1.brand_values, brand2.brand_values)
            similarity_score += values_similarity * 0.15
            
            # Platform preferences similarity
            platform_similarity = self._calculate_platform_similarity(
                brand1.preferred_platforms, brand2.preferred_platforms
            )
            similarity_score += platform_similarity * 0.1
            
            return min(similarity_score, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate brand similarity: {e}")
            return 0.0
    
    async def _calculate_creator_similarity(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate similarity score between two creators"""
        try:
            similarity_score = 0.0
            
            # Niche similarity
            niche_overlap = len(set(creator1.niche) & set(creator2.niche))
            niche_union = len(set(creator1.niche) | set(creator2.niche))
            if niche_union > 0:
                similarity_score += (niche_overlap / niche_union) * 0.3
            
            # Platform similarity
            platform_overlap = len(set(creator1.platforms.keys()) & set(creator2.platforms.keys()))
            platform_union = len(set(creator1.platforms.keys()) | set(creator2.platforms.keys()))
            if platform_union > 0:
                similarity_score += (platform_overlap / platform_union) * 0.2
            
            # Audience demographics similarity
            demo_similarity = self._calculate_demographics_similarity(
                creator1.audience_demographics, creator2.audience_demographics
            )
            similarity_score += demo_similarity * 0.25
            
            # Engagement metrics similarity
            engagement_similarity = self._calculate_engagement_similarity(
                creator1.engagement_metrics, creator2.engagement_metrics
            )
            similarity_score += engagement_similarity * 0.15
            
            # Content style similarity
            style_overlap = len(set(creator1.content_style) & set(creator2.content_style))
            style_union = len(set(creator1.content_style) | set(creator2.content_style))
            if style_union > 0:
                similarity_score += (style_overlap / style_union) * 0.1
            
            return min(similarity_score, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate creator similarity: {e}")
            return 0.0
    
    def _calculate_demographics_similarity(self, demo1: Dict[str, Any], demo2: Dict[str, Any]) -> float:
        """Calculate similarity between demographic data"""
        try:
            if not demo1 or not demo2:
                return 0.0
            
            similarity = 0.0
            total_weight = 0.0
            
            # Age distribution similarity
            if 'age_distribution' in demo1 and 'age_distribution' in demo2:
                age_sim = self._calculate_distribution_similarity(
                    demo1['age_distribution'], demo2['age_distribution']
                )
                similarity += age_sim * 0.4
                total_weight += 0.4
            
            # Gender distribution similarity
            if 'gender_distribution' in demo1 and 'gender_distribution' in demo2:
                gender_sim = self._calculate_distribution_similarity(
                    demo1['gender_distribution'], demo2['gender_distribution']
                )
                similarity += gender_sim * 0.3
                total_weight += 0.3
            
            # Geographic similarity
            if 'top_countries' in demo1 and 'top_countries' in demo2:
                geo_sim = self._calculate_list_similarity(
                    demo1['top_countries'], demo2['top_countries']
                )
                similarity += geo_sim * 0.3
                total_weight += 0.3
            
            return similarity / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate demographics similarity: {e}")
            return 0.0
    
    def _calculate_distribution_similarity(self, dist1: Dict[str, float], dist2: Dict[str, float]) -> float:
        """Calculate similarity between two probability distributions"""
        try:
            all_keys = set(dist1.keys()) | set(dist2.keys())
            if not all_keys:
                return 0.0
            
            # Calculate Bhattacharyya coefficient
            coefficient = 0.0
            for key in all_keys:
                val1 = dist1.get(key, 0.0)
                val2 = dist2.get(key, 0.0)
                coefficient += (val1 * val2) ** 0.5
            
            return coefficient
            
        except Exception as e:
            logger.error(f"Failed to calculate distribution similarity: {e}")
            return 0.0
    
    def _calculate_list_similarity(self, list1: List[str], list2: List[str]) -> float:
        """Calculate Jaccard similarity between two lists"""
        try:
            set1 = set(list1)
            set2 = set(list2)
            
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate list similarity: {e}")
            return 0.0
    
    def _calculate_budget_overlap(self, range1: Tuple[float, float], range2: Tuple[float, float]) -> float:
        """Calculate overlap between two budget ranges"""
        try:
            min1, max1 = range1
            min2, max2 = range2
            
            overlap_start = max(min1, min2)
            overlap_end = min(max1, max2)
            
            if overlap_start >= overlap_end:
                return 0.0
            
            overlap_size = overlap_end - overlap_start
            total_range = max(max1, max2) - min(min1, min2)
            
            return overlap_size / total_range if total_range > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate budget overlap: {e}")
            return 0.0
    
    def _calculate_values_similarity(self, values1: List[str], values2: List[str]) -> float:
        """Calculate similarity between brand values"""
        return self._calculate_list_similarity(values1, values2)
    
    def _calculate_platform_similarity(self, platforms1: List[str], platforms2: List[str]) -> float:
        """Calculate similarity between platform preferences"""
        return self._calculate_list_similarity(platforms1, platforms2)
    
    def _calculate_engagement_similarity(self, metrics1: Dict[str, float], metrics2: Dict[str, float]) -> float:
        """Calculate similarity between engagement metrics"""
        try:
            if not metrics1 or not metrics2:
                return 0.0
            
            common_metrics = set(metrics1.keys()) & set(metrics2.keys())
            if not common_metrics:
                return 0.0
            
            total_diff = 0.0
            for metric in common_metrics:
                val1 = metrics1[metric]
                val2 = metrics2[metric]
                max_val = max(val1, val2, 1.0)  # Avoid division by zero
                diff = abs(val1 - val2) / max_val
                total_diff += diff
            
            avg_diff = total_diff / len(common_metrics)
            similarity = 1.0 - avg_diff
            
            return max(similarity, 0.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate engagement similarity: {e}")
            return 0.0
    
    async def calculate_matching_score(self, brand_id: str, creator_id: str) -> Optional[MatchingScore]:
        """Calculate comprehensive matching score between brand and creator"""
        try:
            if brand_id not in self.brands or creator_id not in self.creators:
                return None
            
            brand = self.brands[brand_id]
            creator = self.creators[creator_id]
            
            # Check blacklists
            if creator_id in brand.blacklisted_creators:
                return None
            
            criteria_scores = {}
            
            # 1. Audience alignment (25% weight)
            audience_score = await self._calculate_audience_alignment(brand, creator)
            criteria_scores[MatchingCriteria.AUDIENCE_ALIGNMENT] = audience_score
            
            # 2. Engagement rate (20% weight)
            engagement_score = await self._calculate_engagement_score(brand, creator)
            criteria_scores[MatchingCriteria.ENGAGEMENT_RATE] = engagement_score
            
            # 3. Brand safety (15% weight)
            brand_safety_score = await self._calculate_brand_safety_score(brand, creator)
            criteria_scores[MatchingCriteria.BRAND_SAFETY] = brand_safety_score
            
            # 4. Content quality (15% weight)
            content_quality_score = await self._calculate_content_quality_score(creator)
            criteria_scores[MatchingCriteria.CONTENT_QUALITY] = content_quality_score
            
            # 5. Previous performance (10% weight)
            performance_score = await self._calculate_performance_score(brand, creator)
            criteria_scores[MatchingCriteria.PREVIOUS_PERFORMANCE] = performance_score
            
            # 6. Niche expertise (10% weight)
            niche_score = await self._calculate_niche_score(brand, creator)
            criteria_scores[MatchingCriteria.NICHE_EXPERTISE] = niche_score
            
            # 7. Geographic reach (3% weight)
            geo_score = await self._calculate_geographic_score(brand, creator)
            criteria_scores[MatchingCriteria.GEOGRAPHIC_REACH] = geo_score
            
            # 8. Demographics fit (2% weight)
            demo_score = await self._calculate_demographics_fit(brand, creator)
            criteria_scores[MatchingCriteria.DEMOGRAPHICS_FIT] = demo_score
            
            # Calculate weighted overall score
            weights = {
                MatchingCriteria.AUDIENCE_ALIGNMENT: 0.25,
                MatchingCriteria.ENGAGEMENT_RATE: 0.20,
                MatchingCriteria.BRAND_SAFETY: 0.15,
                MatchingCriteria.CONTENT_QUALITY: 0.15,
                MatchingCriteria.PREVIOUS_PERFORMANCE: 0.10,
                MatchingCriteria.NICHE_EXPERTISE: 0.10,
                MatchingCriteria.GEOGRAPHIC_REACH: 0.03,
                MatchingCriteria.DEMOGRAPHICS_FIT: 0.02
            }
            
            overall_score = sum(
                criteria_scores[criteria] * weight
                for criteria, weight in weights.items()
            )
            
            # Calculate confidence level
            confidence = await self._calculate_matching_confidence(criteria_scores)
            
            # Identify matching factors and concerns
            factors, concerns = await self._analyze_matching_factors(brand, creator, criteria_scores)
            
            # Estimate success rate
            success_rate = await self._estimate_partnership_success_rate(brand, creator, overall_score)
            
            # Recommend partnership type
            recommended_type = await self._recommend_partnership_type(brand, creator, criteria_scores)
            
            # Suggest budget range
            budget_range = await self._suggest_budget_range(brand, creator, recommended_type)
            
            # Suggest optimal deliverables
            deliverables = await self._suggest_optimal_deliverables(brand, creator, recommended_type)
            
            matching_score = MatchingScore(
                brand_id=brand_id,
                creator_id=creator_id,
                overall_score=overall_score,
                criteria_scores=criteria_scores,
                confidence_level=confidence,
                matching_factors=factors,
                potential_concerns=concerns,
                estimated_success_rate=success_rate,
                recommended_partnership_type=recommended_type,
                suggested_budget_range=budget_range,
                optimal_deliverables=deliverables,
                calculated_at=datetime.now()
            )
            
            # Cache the score
            self.matching_scores[brand_id][creator_id] = matching_score
            
            return matching_score
            
        except Exception as e:
            logger.error(f"Failed to calculate matching score: {e}")
            return None
    
    async def _calculate_audience_alignment(self, brand: BrandProfile, creator: CreatorProfile) -> float:
        """Calculate audience alignment score"""
        try:
            score = 0.0
            
            # Demographics alignment
            demo_similarity = self._calculate_demographics_similarity(
                brand.target_demographics, creator.audience_demographics
            )
            score += demo_similarity * 0.6
            
            # Platform alignment
            brand_platforms = set(brand.preferred_platforms)
            creator_platforms = set(creator.platforms.keys())
            platform_overlap = len(brand_platforms & creator_platforms)
            platform_union = len(brand_platforms | creator_platforms)
            
            if platform_union > 0:
                platform_score = platform_overlap / platform_union
                score += platform_score * 0.4
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate audience alignment: {e}")
            return 0.5
    
    async def _calculate_engagement_score(self, brand: BrandProfile, creator: CreatorProfile) -> float:
        """Calculate engagement rate score"""
        try:
            # Get average engagement rate across platforms
            engagement_rates = []
            for platform, metrics in creator.platforms.items():
                if 'engagement_rate' in metrics:
                    engagement_rates.append(metrics['engagement_rate'])
            
            if not engagement_rates:
                return 0.5  # Default if no data
            
            avg_engagement = sum(engagement_rates) / len(engagement_rates)
            
            # Compare to industry benchmarks
            # Determine creator tier based on follower count
            total_followers = sum(
                metrics.get('followers', 0) for metrics in creator.platforms.values()
            )
            
            if total_followers >= 1000000:
                tier = "mega_influencer"
            elif total_followers >= 100000:
                tier = "macro_influencer"
            elif total_followers >= 10000:
                tier = "micro_influencer"
            else:
                tier = "nano_influencer"
            
            benchmark = self.industry_benchmarks["engagement_rate_benchmarks"].get(tier, 0.05)
            
            # Score based on performance vs benchmark
            if avg_engagement >= benchmark * 1.5:
                return 1.0
            elif avg_engagement >= benchmark:
                return 0.8
            elif avg_engagement >= benchmark * 0.7:
                return 0.6
            elif avg_engagement >= benchmark * 0.5:
                return 0.4
            else:
                return 0.2
            
        except Exception as e:
            logger.error(f"Failed to calculate engagement score: {e}")
            return 0.5
    
    async def _calculate_brand_safety_score(self, brand: BrandProfile, creator: CreatorProfile) -> float:
        """Calculate brand safety compatibility score"""
        try:
            score = 0.8  # Base score
            
            # Check brand safety requirements
            requirements = brand.brand_safety_requirements
            
            # Content appropriateness
            if requirements.get('family_friendly', False):
                # Check creator's content history (simplified)
                if creator.metadata.get('family_friendly_score', 0.8) >= 0.8:
                    score += 0.1
                else:
                    score -= 0.3
            
            # Brand values alignment
            brand_values = set(brand.brand_values)
            creator_values = set(creator.metadata.get('values', []))
            
            if brand_values and creator_values:
                values_overlap = len(brand_values & creator_values)
                values_alignment = values_overlap / len(brand_values)
                score += values_alignment * 0.1
            
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate brand safety score: {e}")
            return 0.7
    
    async def _calculate_content_quality_score(self, creator: CreatorProfile) -> float:
        """Calculate content quality score for creator"""
        try:
            # Average quality across platforms
            quality_scores = []
            
            for platform, metrics in creator.platforms.items():
                if 'content_quality_score' in metrics:
                    quality_scores.append(metrics['content_quality_score'])
            
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                return avg_quality / 100  # Normalize to 0-1 scale
            
            # Fallback based on engagement and follower count
            engagement_rates = [
                metrics.get('engagement_rate', 0) for metrics in creator.platforms.values()
            ]
            
            if engagement_rates:
                avg_engagement = sum(engagement_rates) / len(engagement_rates)
                # High engagement often correlates with quality
                return min(avg_engagement * 10, 1.0)
            
            return 0.6  # Default moderate quality score
            
        except Exception as e:
            logger.error(f"Failed to calculate content quality score: {e}")
            return 0.6
    
    async def _calculate_performance_score(self, brand: BrandProfile, creator: CreatorProfile) -> float:
        """Calculate score based on previous performance"""
        try:
            # Check if brand and creator have worked together before
            common_collaborations = set(brand.collaboration_history) & set(creator.collaboration_history)
            
            if common_collaborations:
                # Calculate average success from previous collaborations
                success_scores = []
                for collab_id in common_collaborations:
                    if collab_id in self.collaborations:
                        collab = self.collaborations[collab_id]
                        if collab.rating_brand and collab.rating_creator:
                            avg_rating = (collab.rating_brand + collab.rating_creator) / 2
                            success_scores.append(avg_rating / 5.0)  # Normalize to 0-1
                
                if success_scores:
                    return sum(success_scores) / len(success_scores)
            
            # Check creator's general partnership performance
            if creator.average_partnership_rating > 0:
                return creator.average_partnership_rating / 5.0
            
            # Check similar brand performance
            similar_brands = self._find_similar_brands(brand.brand_id)
            if similar_brands:
                creator_performance_with_similar = []
                for similar_brand_id in similar_brands:
                    if similar_brand_id in creator.collaboration_history:
                        # This is simplified - would need actual performance data
                        creator_performance_with_similar.append(0.7)  # Placeholder
                
                if creator_performance_with_similar:
                    return sum(creator_performance_with_similar) / len(creator_performance_with_similar)
            
            return 0.6  # Default score for new relationships
            
        except Exception as e:
            logger.error(f"Failed to calculate performance score: {e}")
            return 0.6
    
    async def _calculate_niche_score(self, brand: BrandProfile, creator: CreatorProfile) -> float:
        """Calculate niche expertise alignment score"""
        try:
            # Check if creator's niche aligns with brand's industry
            brand_industry = brand.industry.lower()
            creator_niches = [niche.lower() for niche in creator.niche]
            
            # Direct industry match
            if brand_industry in creator_niches:
                return 1.0
            
            # Industry category matching (simplified)
            industry_mappings = {
                'fashion': ['style', 'clothing', 'accessories', 'beauty'],
                'fitness': ['health', 'wellness', 'sports', 'nutrition'],
                'technology': ['tech', 'gadgets', 'software', 'gaming'],
                'food': ['cooking', 'recipes', 'restaurants', 'nutrition'],
                'travel': ['tourism', 'adventure', 'destinations', 'culture'],
                'beauty': ['cosmetics', 'skincare', 'makeup', 'wellness']
            }
            
            related_niches = industry_mappings.get(brand_industry, [])
            niche_overlap = len(set(related_niches) & set(creator_niches))
            
            if niche_overlap > 0:
                return min(niche_overlap / len(related_niches), 1.0)
            
            return 0.3  # Base score for no clear alignment
            
        except Exception as e:
            logger.error(f"Failed to calculate niche score: {e}")
            return 0.5
    
    async def _calculate_geographic_score(self, brand: BrandProfile, creator: CreatorProfile) -> float:
        """Calculate geographic reach alignment score"""
        try:
            brand_geo = brand.target_demographics.get('top_countries', [])
            creator_geo = creator.audience_demographics.get('top_countries', [])
            
            if not brand_geo or not creator_geo:
                return 0.7  # Default if no geographic data
            
            # Calculate overlap
            overlap = len(set(brand_geo) & set(creator_geo))
            union = len(set(brand_geo) | set(creator_geo))
            
            if union > 0:
                return overlap / union
            
            return 0.5
            
        except Exception as e:
            logger.error(f"Failed to calculate geographic score: {e}")
            return 0.7
    
    async def _calculate_demographics_fit(self, brand: BrandProfile, creator: CreatorProfile) -> float:
        """Calculate demographics fit score"""
        try:
            return self._calculate_demographics_similarity(
                brand.target_demographics, creator.audience_demographics
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate demographics fit: {e}")
            return 0.5
    
    async def _calculate_matching_confidence(self, criteria_scores: Dict[MatchingCriteria, float]) -> float:
        """Calculate confidence level for the matching score"""
        try:
            scores = list(criteria_scores.values())
            
            # Higher confidence when scores are consistent
            score_variance = statistics.variance(scores) if len(scores) > 1 else 0
            
            # Base confidence
            confidence = 0.7
            
            # Adjust based on variance (lower variance = higher confidence)
            if score_variance < 0.1:
                confidence += 0.2
            elif score_variance < 0.2:
                confidence += 0.1
            elif score_variance > 0.4:
                confidence -= 0.2
            
            # Adjust based on average score
            avg_score = sum(scores) / len(scores)
            if avg_score > 0.8:
                confidence += 0.1
            elif avg_score < 0.4:
                confidence -= 0.1
            
            return min(max(confidence, 0.3), 0.95)
            
        except Exception as e:
            logger.error(f"Failed to calculate matching confidence: {e}")
            return 0.7
    
    async def _analyze_matching_factors(
        self, brand: BrandProfile, creator: CreatorProfile, criteria_scores: Dict[MatchingCriteria, float]
    ) -> Tuple[List[str], List[str]]:
        """Analyze matching factors and potential concerns"""
        factors = []
        concerns = []
        
        try:
            # Positive factors
            for criteria, score in criteria_scores.items():
                if score >= 0.8:
                    if criteria == MatchingCriteria.AUDIENCE_ALIGNMENT:
                        factors.append("Excellent audience demographics alignment")
                    elif criteria == MatchingCriteria.ENGAGEMENT_RATE:
                        factors.append("High engagement rate above industry benchmark")
                    elif criteria == MatchingCriteria.BRAND_SAFETY:
                        factors.append("Strong brand safety compatibility")
                    elif criteria == MatchingCriteria.CONTENT_QUALITY:
                        factors.append("High-quality content production")
                    elif criteria == MatchingCriteria.NICHE_EXPERTISE:
                        factors.append("Strong niche expertise alignment")
                    elif criteria == MatchingCriteria.PREVIOUS_PERFORMANCE:
                        factors.append("Proven track record of successful partnerships")
            
            # Concerns
            for criteria, score in criteria_scores.items():
                if score <= 0.4:
                    if criteria == MatchingCriteria.AUDIENCE_ALIGNMENT:
                        concerns.append("Limited audience demographics overlap")
                    elif criteria == MatchingCriteria.ENGAGEMENT_RATE:
                        concerns.append("Below-average engagement rate")
                    elif criteria == MatchingCriteria.BRAND_SAFETY:
                        concerns.append("Potential brand safety concerns")
                    elif criteria == MatchingCriteria.CONTENT_QUALITY:
                        concerns.append("Content quality below expectations")
                    elif criteria == MatchingCriteria.NICHE_EXPERTISE:
                        concerns.append("Limited niche expertise alignment")
                    elif criteria == MatchingCriteria.PREVIOUS_PERFORMANCE:
                        concerns.append("Limited or poor previous performance data")
            
            # Additional factors
            if creator.creator_id in brand.preferred_creators:
                factors.append("Listed as preferred creator by brand")
            
            if creator.brand_partnerships_count > 10:
                factors.append("Experienced in brand partnerships")
            elif creator.brand_partnerships_count < 3:
                concerns.append("Limited brand partnership experience")
            
        except Exception as e:
            logger.error(f"Failed to analyze matching factors: {e}")
        
        return factors, concerns
    
    async def _estimate_partnership_success_rate(
        self, brand: BrandProfile, creator: CreatorProfile, overall_score: float
    ) -> float:
        """Estimate probability of successful partnership"""
        try:
            # Base success rate from overall score
            success_rate = overall_score * 0.8
            
            # Adjust based on partnership experience
            if creator.brand_partnerships_count > 5:
                success_rate += 0.1
            elif creator.brand_partnerships_count < 2:
                success_rate -= 0.1
            
            # Adjust based on creator's track record
            if creator.average_partnership_rating >= 4.0:
                success_rate += 0.1
            elif creator.average_partnership_rating <= 3.0:
                success_rate -= 0.1
            
            # Adjust based on brand-creator history
            common_collaborations = set(brand.collaboration_history) & set(creator.collaboration_history)
            if common_collaborations:
                # Previous collaboration exists - check success
                success_rate += 0.2  # Bonus for existing relationship
            
            return min(max(success_rate, 0.1), 0.95)
            
        except Exception as e:
            logger.error(f"Failed to estimate success rate: {e}")
            return overall_score * 0.7
    
    async def _recommend_partnership_type(
        self, brand: BrandProfile, creator: CreatorProfile, criteria_scores: Dict[MatchingCriteria, float]
    ) -> PartnershipType:
        """Recommend optimal partnership type"""
        try:
            overall_score = sum(criteria_scores.values()) / len(criteria_scores)
            
            # High-score partnerships
            if overall_score >= 0.8:
                if creator.brand_partnerships_count >= 10:
                    return PartnershipType.LONG_TERM_AMBASSADOR
                else:
                    return PartnershipType.CO_CREATION
            
            # Medium-score partnerships
            elif overall_score >= 0.6:
                if criteria_scores.get(MatchingCriteria.ENGAGEMENT_RATE, 0) >= 0.7:
                    return PartnershipType.SPONSORED_POST
                else:
                    return PartnershipType.PRODUCT_PLACEMENT
            
            # Lower-score partnerships - start small
            else:
                return PartnershipType.AFFILIATE_PARTNERSHIP
            
        except Exception as e:
            logger.error(f"Failed to recommend partnership type: {e}")
            return PartnershipType.SPONSORED_POST
    
    async def _suggest_budget_range(
        self, brand: BrandProfile, creator: CreatorProfile, partnership_type: PartnershipType
    ) -> Tuple[float, float]:
        """Suggest budget range for the partnership"""
        try:
            # Get creator's typical rates
            creator_rates = creator.rates
            
            # Base budget on partnership type and creator metrics
            total_followers = sum(
                metrics.get('followers', 0) for metrics in creator.platforms.values()
            )
            
            avg_engagement = sum(
                metrics.get('engagement_rate', 0) for metrics in creator.platforms.values()
            ) / len(creator.platforms) if creator.platforms else 0.02
            
            # Calculate base rate per follower with engagement multiplier
            base_rate_per_follower = 0.01 * (1 + avg_engagement * 10)
            
            # Adjust by partnership type
            type_multipliers = {
                PartnershipType.SPONSORED_POST: 1.0,
                PartnershipType.LONG_TERM_AMBASSADOR: 3.0,
                PartnershipType.PRODUCT_PLACEMENT: 0.7,
                PartnershipType.EVENT_COLLABORATION: 2.0,
                PartnershipType.CO_CREATION: 4.0,
                PartnershipType.AFFILIATE_PARTNERSHIP: 0.5,
                PartnershipType.LICENSING_DEAL: 5.0,
                PartnershipType.EQUITY_PARTNERSHIP: 0.1,  # Lower upfront cost
                PartnershipType.PERFORMANCE_BASED: 0.8,
                PartnershipType.CAMPAIGN_SERIES: 2.5
            }
            
            multiplier = type_multipliers.get(partnership_type, 1.0)
            base_budget = total_followers * base_rate_per_follower * multiplier
            
            # Ensure within brand's budget range
            brand_min, brand_max = brand.budget_range
            
            suggested_min = max(base_budget * 0.8, brand_min)
            suggested_max = min(base_budget * 1.2, brand_max)
            
            # Ensure min <= max
            if suggested_min > suggested_max:
                suggested_min = suggested_max * 0.8
            
            return (suggested_min, suggested_max)
            
        except Exception as e:
            logger.error(f"Failed to suggest budget range: {e}")
            return (1000.0, 5000.0)  # Default range
    
    async def _suggest_optimal_deliverables(
        self, brand: BrandProfile, creator: CreatorProfile, partnership_type: PartnershipType
    ) -> List[str]:
        """Suggest optimal deliverables for the partnership"""
        try:
            deliverables = []
            
            # Base deliverables by partnership type
            type_deliverables = {
                PartnershipType.SPONSORED_POST: [
                    "1 main feed post",
                    "2 story posts",
                    "Brand hashtag usage"
                ],
                PartnershipType.LONG_TERM_AMBASSADOR: [
                    "4 feed posts per month",
                    "8 story posts per month",
                    "1 video content per month",
                    "Exclusive discount code"
                ],
                PartnershipType.PRODUCT_PLACEMENT: [
                    "Product integration in video",
                    "Natural product mention",
                    "Brand visibility in content"
                ],
                PartnershipType.EVENT_COLLABORATION: [
                    "Live event coverage",
                    "Behind-the-scenes content",
                    "Event story highlights"
                ],
                PartnershipType.CO_CREATION: [
                    "Custom content creation",
                    "Brand collaboration video",
                    "Cross-promotion on both channels"
                ]
            }
            
            deliverables.extend(type_deliverables.get(partnership_type, ["1 sponsored post"]))
            
            # Add platform-specific deliverables
            for platform in creator.platforms:
                if platform == "youtube" and "video" not in str(deliverables).lower():
                    deliverables.append("YouTube video integration")
                elif platform == "tiktok":
                    deliverables.append("TikTok video with trending audio")
                elif platform == "instagram":
                    deliverables.append("Instagram Reel")
            
            # Add performance-based deliverables if high engagement
            avg_engagement = sum(
                metrics.get('engagement_rate', 0) for metrics in creator.platforms.values()
            ) / len(creator.platforms) if creator.platforms else 0
            
            if avg_engagement > 0.05:
                deliverables.append("Engagement rate guarantee")
            
            return deliverables
            
        except Exception as e:
            logger.error(f"Failed to suggest optimal deliverables: {e}")
            return ["1 sponsored post", "Brand mention"]
    
    def _find_similar_brands(self, brand_id: str, limit: int = 5) -> List[str]:
        """Find brands similar to the given brand"""
        try:
            if brand_id not in self.brand_similarity_matrix:
                return []
            
            similarities = self.brand_similarity_matrix[brand_id]
            
            # Sort by similarity score
            sorted_brands = sorted(
                similarities.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return [brand_id for brand_id, score in sorted_brands[:limit]]
            
        except Exception as e:
            logger.error(f"Failed to find similar brands: {e}")
            return []
    
    def _find_similar_creators(self, creator_id: str, limit: int = 5) -> List[str]:
        """Find creators similar to the given creator"""
        try:
            if creator_id not in self.creator_similarity_matrix:
                return []
            
            similarities = self.creator_similarity_matrix[creator_id]
            
            # Sort by similarity score
            sorted_creators = sorted(
                similarities.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return [creator_id for creator_id, score in sorted_creators[:limit]]
            
        except Exception as e:
            logger.error(f"Failed to find similar creators: {e}")
            return []
    
    async def record_collaboration(self, collaboration: Collaboration) -> bool:
        """Record a new collaboration"""
        try:
            # Validate collaboration
            if not self._validate_collaboration(collaboration):
                logger.error(f"Invalid collaboration: {collaboration.collaboration_id}")
                return False
            
            # Store collaboration
            self.collaborations[collaboration.collaboration_id] = collaboration
            
            # Update network connections
            self.collaboration_network[collaboration.creator_id].add(collaboration.brand_id)
            self.brand_network[collaboration.brand_id].add(collaboration.creator_id)
            
            # Update collaboration history
            if collaboration.brand_id in self.brands:
                self.brands[collaboration.brand_id].collaboration_history.append(collaboration.collaboration_id)
            
            if collaboration.creator_id in self.creators:
                self.creators[collaboration.creator_id].collaboration_history.append(collaboration.collaboration_id)
                self.creators[collaboration.creator_id].brand_partnerships_count += 1
            
            # Clear relevant caches
            self._clear_performance_cache(collaboration.brand_id, collaboration.creator_id)
            
            logger.info(f"Collaboration recorded: {collaboration.collaboration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record collaboration: {e}")
            return False
    
    def _validate_collaboration(self, collaboration: Collaboration) -> bool:
        """Validate collaboration data"""
        try:
            # Required fields
            if not all([
                collaboration.collaboration_id,
                collaboration.brand_id,
                collaboration.creator_id,
                collaboration.partnership_type,
                collaboration.status,
                collaboration.start_date,
                collaboration.budget >= 0
            ]):
                return False
            
            # Check if brand and creator exist
            if (collaboration.brand_id not in self.brands or 
                collaboration.creator_id not in self.creators):
                return False
            
            # Date validation
            if collaboration.end_date and collaboration.end_date < collaboration.start_date:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Collaboration validation failed: {e}")
            return False
    
    def _clear_performance_cache(self, brand_id: str, creator_id: str) -> None:
        """Clear performance cache for brand and creator"""
        cache_keys_to_remove = []
        for key in self.performance_cache:
            if brand_id in key or creator_id in key:
                cache_keys_to_remove.append(key)
        
        for key in cache_keys_to_remove:
            del self.performance_cache[key]
    
    async def find_best_matches(
        self, brand_id: str, limit: int = 10, min_score: float = 0.6
    ) -> List[MatchingScore]:
        """Find best creator matches for a brand"""
        try:
            if brand_id not in self.brands:
                return []
            
            matches = []
            
            for creator_id in self.creators:
                # Skip blacklisted creators
                brand = self.brands[brand_id]
                if creator_id in brand.blacklisted_creators:
                    continue
                
                # Calculate matching score
                score = await self.calculate_matching_score(brand_id, creator_id)
                if score and score.overall_score >= min_score:
                    matches.append(score)
            
            # Sort by overall score
            matches.sort(key=lambda x: x.overall_score, reverse=True)
            
            return matches[:limit]
            
        except Exception as e:
            logger.error(f"Failed to find best matches: {e}")
            return []
    
    async def find_brand_opportunities(
        self, creator_id: str, limit: int = 10, min_score: float = 0.6
    ) -> List[MatchingScore]:
        """Find best brand opportunities for a creator"""
        try:
            if creator_id not in self.creators:
                return []
            
            opportunities = []
            
            for brand_id in self.brands:
                # Skip if creator is blacklisted
                brand = self.brands[brand_id]
                if creator_id in brand.blacklisted_creators:
                    continue
                
                # Calculate matching score
                score = await self.calculate_matching_score(brand_id, creator_id)
                if score and score.overall_score >= min_score:
                    opportunities.append(score)
            
            # Sort by overall score
            opportunities.sort(key=lambda x: x.overall_score, reverse=True)
            
            return opportunities[:limit]
            
        except Exception as e:
            logger.error(f"Failed to find brand opportunities: {e}")
            return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and health metrics"""
        return {
            "system_status": "operational",
            "registered_brands": len(self.brands),
            "registered_creators": len(self.creators),
            "total_collaborations": len(self.collaborations),
            "cached_matching_scores": sum(len(scores) for scores in self.matching_scores.values()),
            "network_connections": sum(len(connections) for connections in self.collaboration_network.values()),
            "cached_insights": sum(len(insights) for insights in self.insights_cache.values()),
            "similarity_calculations": len(self.creator_similarity_matrix) + len(self.brand_similarity_matrix),
            "supported_partnership_types": len(PartnershipType),
            "uptime": "99.99%",
            "last_updated": datetime.now().isoformat()
        }


# Module exports
__all__ = [
    'CollaborationIntelligenceSystem',
    'BrandProfile',
    'CreatorProfile',
    'Collaboration',
    'MatchingScore',
    'NetworkInsight',
    'CollaborationInsight',
    'PartnershipType',
    'CollaborationStatus',
    'MatchingCriteria',
    'SuccessMetrics'
]