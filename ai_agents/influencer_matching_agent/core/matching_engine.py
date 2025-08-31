"""
Influencer Matching Engine - Core processing engine for creator-brand pairing

Advanced matching capabilities with AI-powered compatibility analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class MatchingJob:
    """Influencer matching job configuration"""
    job_id: str
    brand_profile: Dict[str, Any]
    campaign_requirements: Dict[str, Any]
    matching_criteria: Dict[str, Any]
    status: str = "pending"
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class MatchingResult:
    """Influencer matching result"""
    influencer_id: str
    influencer_name: str
    compatibility_score: float
    audience_match_score: float
    engagement_rate: float
    estimated_reach: int
    collaboration_potential: str
    recommended_budget: Dict[str, float]
    match_reasons: List[str] = None
    
    def __post_init__(self):
        if self.match_reasons is None:
            self.match_reasons = []

class MatchingEngine:
    """Core influencer matching processing engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.is_running = False
        
        # Matching databases and caches
        self.influencer_profiles = {}
        self.brand_profiles = {}
        self.matching_history = {}
        self.audience_analytics = {}
        
        # Processing queues
        self.pending_jobs = asyncio.Queue()
        self.active_jobs = {}
        
        # Matching algorithms configuration
        self.compatibility_weights = {
            "niche_alignment": 0.25,
            "audience_demographics": 0.20,
            "engagement_quality": 0.20,
            "brand_safety": 0.15,
            "content_style": 0.10,
            "collaboration_history": 0.10
        }
        
        logger.info("MatchingEngine initialized")

    async def start(self):
        """Start the matching engine"""
        if not self.is_running:
            self.is_running = True
            # Start background tasks
            asyncio.create_task(self._process_matching_jobs())
            await self._load_influencer_database()
            logger.info("MatchingEngine started")

    async def stop(self):
        """Stop the matching engine"""
        if self.is_running:
            self.is_running = False
            logger.info("MatchingEngine stopped")

    async def find_matching_influencers(self, brand_profile: Dict[str, Any], campaign_requirements: Dict[str, Any]) -> List[MatchingResult]:
        """Find matching influencers for a brand campaign"""
        
        # Load influencer database
        available_influencers = await self._get_available_influencers(campaign_requirements)
        
        # Score each influencer
        matches = []
        for influencer in available_influencers:
            compatibility_score = await self._calculate_compatibility_score(
                brand_profile, influencer, campaign_requirements
            )
            
            if compatibility_score >= campaign_requirements.get('min_compatibility_score', 0.6):
                match_result = await self._create_match_result(
                    influencer, brand_profile, campaign_requirements, compatibility_score
                )
                matches.append(match_result)
        
        # Sort by compatibility score
        matches.sort(key=lambda x: x.compatibility_score, reverse=True)
        
        # Return top matches
        max_matches = campaign_requirements.get('max_matches', 20)
        return matches[:max_matches]

    async def analyze_audience_overlap(self, influencer_id: str, brand_target_audience: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audience overlap between influencer and brand target"""
        
        influencer_audience = await self._get_influencer_audience_data(influencer_id)
        
        # Demographics overlap
        demographics_overlap = await self._calculate_demographics_overlap(
            influencer_audience.get('demographics', {}),
            brand_target_audience.get('demographics', {})
        )
        
        # Interest overlap
        interests_overlap = await self._calculate_interests_overlap(
            influencer_audience.get('interests', []),
            brand_target_audience.get('interests', [])
        )
        
        # Geographic overlap
        geographic_overlap = await self._calculate_geographic_overlap(
            influencer_audience.get('locations', []),
            brand_target_audience.get('target_locations', [])
        )
        
        overall_overlap = (demographics_overlap + interests_overlap + geographic_overlap) / 3
        
        return {
            "overall_overlap_score": round(overall_overlap, 2),
            "demographics_overlap": round(demographics_overlap, 2),
            "interests_overlap": round(interests_overlap, 2),
            "geographic_overlap": round(geographic_overlap, 2),
            "audience_size": influencer_audience.get('total_followers', 0),
            "expected_reach": int(influencer_audience.get('total_followers', 0) * overall_overlap),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }

    async def calculate_collaboration_budget(self, influencer_id: str, campaign_type: str, deliverables: List[str]) -> Dict[str, float]:
        """Calculate recommended collaboration budget"""
        
        influencer_profile = await self._get_influencer_profile(influencer_id)
        
        # Base rates by follower count and engagement
        follower_count = influencer_profile.get('follower_count', 0)
        engagement_rate = influencer_profile.get('engagement_rate', 0.03)
        
        # Calculate base rate per post
        if follower_count < 10000:  # Micro-influencer
            base_rate = follower_count * 0.01
        elif follower_count < 100000:  # Mid-tier influencer
            base_rate = follower_count * 0.02
        elif follower_count < 1000000:  # Macro influencer
            base_rate = follower_count * 0.03
        else:  # Celebrity/Mega influencer
            base_rate = follower_count * 0.05
        
        # Adjust for engagement rate
        engagement_multiplier = max(0.5, min(2.0, engagement_rate / 0.03))
        base_rate *= engagement_multiplier
        
        # Calculate costs for different deliverables
        deliverable_rates = {
            "instagram_post": base_rate,
            "instagram_story": base_rate * 0.3,
            "instagram_reel": base_rate * 1.2,
            "youtube_video": base_rate * 2.0,
            "tiktok_video": base_rate * 0.8,
            "twitter_post": base_rate * 0.2,
            "blog_post": base_rate * 1.5,
            "product_review": base_rate * 1.3,
            "brand_mention": base_rate * 0.5
        }
        
        total_cost = 0
        itemized_costs = {}
        
        for deliverable in deliverables:
            cost = deliverable_rates.get(deliverable, base_rate)
            itemized_costs[deliverable] = round(cost, 2)
            total_cost += cost
        
        # Add campaign type multipliers
        campaign_multipliers = {
            "product_launch": 1.3,
            "brand_awareness": 1.0,
            "sales_campaign": 1.2,
            "event_promotion": 1.1,
            "seasonal_campaign": 1.1,
            "long_term_partnership": 0.9
        }
        
        multiplier = campaign_multipliers.get(campaign_type, 1.0)
        total_cost *= multiplier
        
        return {
            "total_budget": round(total_cost, 2),
            "itemized_costs": itemized_costs,
            "campaign_multiplier": multiplier,
            "base_rate_per_post": round(base_rate, 2),
            "engagement_adjustment": round(engagement_multiplier, 2),
            "budget_range": {
                "minimum": round(total_cost * 0.8, 2),
                "recommended": round(total_cost, 2),
                "maximum": round(total_cost * 1.2, 2)
            }
        }

    async def assess_brand_safety(self, influencer_id: str, brand_guidelines: Dict[str, Any]) -> Dict[str, Any]:
        """Assess brand safety compatibility"""
        
        influencer_profile = await self._get_influencer_profile(influencer_id)
        content_history = await self._get_influencer_content_history(influencer_id)
        
        # Content analysis
        content_safety = await self._analyze_content_safety(content_history, brand_guidelines)
        
        # Controversy check
        controversy_score = await self._check_controversy_history(influencer_id)
        
        # Alignment with brand values
        values_alignment = await self._assess_values_alignment(
            influencer_profile.get('values', []),
            brand_guidelines.get('brand_values', [])
        )
        
        # Language and behavior analysis
        behavior_score = await self._analyze_behavior_patterns(content_history)
        
        # Overall brand safety score
        safety_score = (content_safety + values_alignment + behavior_score) / 3
        safety_score = max(0, safety_score - controversy_score)  # Reduce for controversies
        
        return {
            "overall_safety_score": round(safety_score, 2),
            "content_safety_score": round(content_safety, 2),
            "values_alignment_score": round(values_alignment, 2),
            "behavior_score": round(behavior_score, 2),
            "controversy_risk": round(controversy_score, 2),
            "safety_level": self._get_safety_level(safety_score),
            "recommendations": await self._get_safety_recommendations(safety_score, content_safety),
            "assessment_timestamp": datetime.utcnow().isoformat()
        }

    async def predict_campaign_performance(self, influencer_id: str, campaign_details: Dict[str, Any]) -> Dict[str, Any]:
        """Predict campaign performance metrics"""
        
        influencer_profile = await self._get_influencer_profile(influencer_id)
        historical_performance = await self._get_historical_performance(influencer_id)
        
        # Base metrics from influencer profile
        follower_count = influencer_profile.get('follower_count', 0)
        engagement_rate = influencer_profile.get('engagement_rate', 0.03)
        
        # Campaign type adjustments
        campaign_type = campaign_details.get('campaign_type', 'brand_awareness')
        type_multipliers = {
            "product_launch": {"reach": 1.2, "engagement": 1.3, "conversion": 1.5},
            "brand_awareness": {"reach": 1.4, "engagement": 1.0, "conversion": 0.8},
            "sales_campaign": {"reach": 1.0, "engagement": 1.1, "conversion": 2.0},
            "event_promotion": {"reach": 1.3, "engagement": 1.2, "conversion": 1.2}
        }
        
        multipliers = type_multipliers.get(campaign_type, {"reach": 1.0, "engagement": 1.0, "conversion": 1.0})
        
        # Predicted metrics
        predicted_reach = int(follower_count * 0.3 * multipliers["reach"])  # 30% organic reach
        predicted_impressions = int(predicted_reach * 2.5)  # Multiple views per user
        predicted_engagements = int(predicted_impressions * engagement_rate * multipliers["engagement"])
        predicted_clicks = int(predicted_engagements * 0.1)  # 10% of engagements click through
        predicted_conversions = int(predicted_clicks * 0.02 * multipliers["conversion"])  # 2% conversion rate
        
        # Performance confidence based on historical data
        confidence_score = await self._calculate_prediction_confidence(
            historical_performance, campaign_details
        )
        
        return {
            "predicted_metrics": {
                "reach": predicted_reach,
                "impressions": predicted_impressions,
                "engagements": predicted_engagements,
                "clicks": predicted_clicks,
                "conversions": predicted_conversions,
                "estimated_ctr": round(predicted_clicks / predicted_impressions * 100, 2),
                "estimated_conversion_rate": round(predicted_conversions / predicted_clicks * 100, 2)
            },
            "confidence_score": round(confidence_score, 2),
            "performance_tier": await self._classify_performance_tier(predicted_engagements, follower_count),
            "optimization_suggestions": await self._get_performance_optimization_tips(
                campaign_details, influencer_profile
            ),
            "prediction_timestamp": datetime.utcnow().isoformat()
        }

    # Helper methods for matching calculations

    async def _get_available_influencers(self, campaign_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get available influencers based on campaign requirements"""
        # Simulate influencer database
        mock_influencers = []
        
        for i in range(50):  # Generate 50 mock influencers
            influencer = {
                "influencer_id": f"inf_{i:03d}",
                "name": f"Influencer {i+1}",
                "follower_count": 10000 * (i + 1),
                "engagement_rate": 0.02 + (i % 10) * 0.005,
                "niche": ["lifestyle", "tech", "fashion", "fitness", "food"][i % 5],
                "platforms": ["instagram", "tiktok", "youtube"],
                "audience_demographics": {
                    "age_groups": {"18-24": 0.3, "25-34": 0.4, "35-44": 0.2, "45+": 0.1},
                    "gender": {"female": 0.6, "male": 0.4},
                    "locations": ["US", "UK", "CA", "AU"]
                },
                "content_style": ["professional", "casual", "artistic"][i % 3],
                "collaboration_rating": 4.0 + (i % 10) * 0.1
            }
            mock_influencers.append(influencer)
        
        # Filter based on campaign requirements
        filtered_influencers = []
        min_followers = campaign_requirements.get('min_followers', 0)
        max_followers = campaign_requirements.get('max_followers', float('inf'))
        required_platforms = campaign_requirements.get('platforms', [])
        target_niche = campaign_requirements.get('niche', None)
        
        for influencer in mock_influencers:
            # Check follower count
            if not (min_followers <= influencer['follower_count'] <= max_followers):
                continue
            
            # Check platforms
            if required_platforms and not any(platform in influencer['platforms'] for platform in required_platforms):
                continue
            
            # Check niche
            if target_niche and influencer['niche'] != target_niche:
                continue
            
            filtered_influencers.append(influencer)
        
        return filtered_influencers

    async def _calculate_compatibility_score(self, brand_profile: Dict[str, Any], influencer: Dict[str, Any], campaign_requirements: Dict[str, Any]) -> float:
        """Calculate compatibility score between brand and influencer"""
        
        scores = {}
        
        # Niche alignment
        brand_industry = brand_profile.get('industry', '')
        influencer_niche = influencer.get('niche', '')
        niche_compatibility = await self._calculate_niche_compatibility(brand_industry, influencer_niche)
        scores['niche_alignment'] = niche_compatibility
        
        # Audience demographics match
        brand_target = brand_profile.get('target_audience', {})
        influencer_audience = influencer.get('audience_demographics', {})
        demographics_match = await self._calculate_demographics_match(brand_target, influencer_audience)
        scores['audience_demographics'] = demographics_match
        
        # Engagement quality
        engagement_rate = influencer.get('engagement_rate', 0)
        engagement_quality = min(1.0, engagement_rate / 0.05)  # Normalize to 5% max
        scores['engagement_quality'] = engagement_quality
        
        # Brand safety (simplified)
        brand_safety_score = 0.8  # Assume good safety for mock data
        scores['brand_safety'] = brand_safety_score
        
        # Content style match
        content_style_match = 0.7  # Default moderate match
        scores['content_style'] = content_style_match
        
        # Collaboration history (new influencers get neutral score)
        collaboration_rating = influencer.get('collaboration_rating', 3.5)
        collaboration_score = min(1.0, collaboration_rating / 5.0)
        scores['collaboration_history'] = collaboration_score
        
        # Calculate weighted score
        total_score = 0
        for factor, weight in self.compatibility_weights.items():
            total_score += scores[factor] * weight
        
        return round(total_score, 3)

    async def _create_match_result(self, influencer: Dict[str, Any], brand_profile: Dict[str, Any], campaign_requirements: Dict[str, Any], compatibility_score: float) -> MatchingResult:
        """Create a match result object"""
        
        # Calculate audience match score
        audience_match = await self._calculate_demographics_match(
            brand_profile.get('target_audience', {}),
            influencer.get('audience_demographics', {})
        )
        
        # Estimate reach
        follower_count = influencer.get('follower_count', 0)
        estimated_reach = int(follower_count * 0.3 * audience_match)  # 30% reach adjusted for audience match
        
        # Determine collaboration potential
        if compatibility_score >= 0.9:
            collaboration_potential = "excellent"
        elif compatibility_score >= 0.8:
            collaboration_potential = "very_good"
        elif compatibility_score >= 0.7:
            collaboration_potential = "good"
        else:
            collaboration_potential = "moderate"
        
        # Calculate recommended budget
        budget_result = await self.calculate_collaboration_budget(
            influencer['influencer_id'],
            campaign_requirements.get('campaign_type', 'brand_awareness'),
            campaign_requirements.get('deliverables', ['instagram_post'])
        )
        
        # Generate match reasons
        match_reasons = []
        if compatibility_score >= 0.8:
            match_reasons.append("High overall compatibility")
        if audience_match >= 0.7:
            match_reasons.append("Strong audience alignment")
        if influencer.get('engagement_rate', 0) >= 0.04:
            match_reasons.append("Above-average engagement rate")
        if influencer.get('collaboration_rating', 0) >= 4.5:
            match_reasons.append("Excellent collaboration history")
        
        return MatchingResult(
            influencer_id=influencer['influencer_id'],
            influencer_name=influencer['name'],
            compatibility_score=compatibility_score,
            audience_match_score=round(audience_match, 2),
            engagement_rate=influencer.get('engagement_rate', 0),
            estimated_reach=estimated_reach,
            collaboration_potential=collaboration_potential,
            recommended_budget=budget_result,
            match_reasons=match_reasons
        )

    async def _calculate_niche_compatibility(self, brand_industry: str, influencer_niche: str) -> float:
        """Calculate niche compatibility score"""
        # Define niche compatibility matrix
        compatibility_matrix = {
            "technology": {"tech": 1.0, "lifestyle": 0.7, "fashion": 0.4, "fitness": 0.3, "food": 0.2},
            "fashion": {"fashion": 1.0, "lifestyle": 0.8, "tech": 0.3, "fitness": 0.6, "food": 0.2},
            "fitness": {"fitness": 1.0, "lifestyle": 0.8, "food": 0.7, "fashion": 0.6, "tech": 0.3},
            "food": {"food": 1.0, "lifestyle": 0.8, "fitness": 0.7, "fashion": 0.3, "tech": 0.2},
            "lifestyle": {"lifestyle": 1.0, "fashion": 0.8, "fitness": 0.8, "food": 0.8, "tech": 0.7}
        }
        
        return compatibility_matrix.get(brand_industry, {}).get(influencer_niche, 0.5)

    async def _calculate_demographics_match(self, brand_target: Dict[str, Any], influencer_audience: Dict[str, Any]) -> float:
        """Calculate demographics match score"""
        if not brand_target or not influencer_audience:
            return 0.5  # Default neutral score
        
        # Age group overlap
        brand_age = brand_target.get('age_groups', {})
        influencer_age = influencer_audience.get('age_groups', {})
        age_overlap = await self._calculate_overlap_score(brand_age, influencer_age)
        
        # Gender overlap
        brand_gender = brand_target.get('gender', {})
        influencer_gender = influencer_audience.get('gender', {})
        gender_overlap = await self._calculate_overlap_score(brand_gender, influencer_gender)
        
        # Location overlap
        brand_locations = set(brand_target.get('locations', []))
        influencer_locations = set(influencer_audience.get('locations', []))
        location_overlap = len(brand_locations.intersection(influencer_locations)) / max(len(brand_locations), 1)
        
        # Weighted average
        total_match = (age_overlap * 0.4 + gender_overlap * 0.3 + location_overlap * 0.3)
        return round(total_match, 2)

    async def _calculate_overlap_score(self, target_dist: Dict[str, float], audience_dist: Dict[str, float]) -> float:
        """Calculate overlap score between two distributions"""
        if not target_dist or not audience_dist:
            return 0.5
        
        overlap = 0.0
        total_target = sum(target_dist.values())
        total_audience = sum(audience_dist.values())
        
        if total_target == 0 or total_audience == 0:
            return 0.5
        
        # Normalize distributions
        norm_target = {k: v/total_target for k, v in target_dist.items()}
        norm_audience = {k: v/total_audience for k, v in audience_dist.items()}
        
        # Calculate overlap
        for category in norm_target:
            if category in norm_audience:
                overlap += min(norm_target[category], norm_audience[category])
        
        return round(overlap, 2)

    async def get_status(self) -> Dict[str, Any]:
        """Get engine status"""
        return {
            "status": "running" if self.is_running else "stopped",
            "active_jobs": len(self.active_jobs),
            "total_influencer_profiles": len(self.influencer_profiles),
            "total_brand_profiles": len(self.brand_profiles),
            "matching_history_count": len(self.matching_history),
            "metrics": {
                "influencer_database_size": len(self.influencer_profiles),
                "brand_database_size": len(self.brand_profiles),
                "audience_analytics_size": len(self.audience_analytics)
            }
        }

    async def _load_influencer_database(self):
        """Load influencer database"""
        # Simulate loading influencer data
        logger.info("Influencer database loaded")

    async def _process_matching_jobs(self):
        """Background job processing"""
        while self.is_running:
            try:
                if not self.pending_jobs.empty():
                    job = await self.pending_jobs.get()
                    await self._execute_matching_job(job)
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error processing matching jobs: {e}")

    async def _execute_matching_job(self, job: MatchingJob):
        """Execute a matching job"""
        try:
            job.status = "running"
            self.active_jobs[job.job_id] = job
            
            # Job execution logic here
            await asyncio.sleep(1)  # Simulate processing
            
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            
        except Exception as e:
            job.status = "failed"
            logger.error(f"Matching job {job.job_id} failed: {e}")
        finally:
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]

    # Placeholder methods for full implementation
    async def _get_influencer_audience_data(self, influencer_id: str) -> Dict[str, Any]:
        """Get influencer audience data"""
        return {
            "total_followers": 50000,
            "demographics": {"age_groups": {"18-24": 0.3, "25-34": 0.5, "35+": 0.2}},
            "interests": ["technology", "lifestyle", "entertainment"],
            "locations": ["US", "UK", "CA"]
        }

    async def _calculate_demographics_overlap(self, aud1: Dict[str, Any], aud2: Dict[str, Any]) -> float:
        """Calculate demographics overlap"""
        return 0.75  # Mock overlap score

    async def _calculate_interests_overlap(self, interests1: List[str], interests2: List[str]) -> float:
        """Calculate interests overlap"""
        if not interests1 or not interests2:
            return 0.5
        
        overlap = len(set(interests1).intersection(set(interests2)))
        total_unique = len(set(interests1).union(set(interests2)))
        return overlap / total_unique if total_unique > 0 else 0.5

    async def _calculate_geographic_overlap(self, locations1: List[str], locations2: List[str]) -> float:
        """Calculate geographic overlap"""
        if not locations1 or not locations2:
            return 0.5
        
        overlap = len(set(locations1).intersection(set(locations2)))
        return overlap / max(len(locations1), len(locations2))

    async def _get_influencer_profile(self, influencer_id: str) -> Dict[str, Any]:
        """Get influencer profile"""
        return {
            "influencer_id": influencer_id,
            "follower_count": 75000,
            "engagement_rate": 0.045,
            "values": ["sustainability", "authenticity", "innovation"]
        }

    async def _get_influencer_content_history(self, influencer_id: str) -> List[Dict[str, Any]]:
        """Get influencer content history"""
        return [
            {"type": "post", "content": "Sample content", "engagement": 1500},
            {"type": "story", "content": "Sample story", "engagement": 800}
        ]

    async def _analyze_content_safety(self, content_history: List[Dict[str, Any]], guidelines: Dict[str, Any]) -> float:
        """Analyze content safety"""
        return 0.85  # Mock safety score

    async def _check_controversy_history(self, influencer_id: str) -> float:
        """Check controversy history"""
        return 0.1  # Low controversy risk

    async def _assess_values_alignment(self, influencer_values: List[str], brand_values: List[str]) -> float:
        """Assess values alignment"""
        if not influencer_values or not brand_values:
            return 0.5
        
        overlap = len(set(influencer_values).intersection(set(brand_values)))
        return overlap / max(len(brand_values), 1)

    async def _analyze_behavior_patterns(self, content_history: List[Dict[str, Any]]) -> float:
        """Analyze behavior patterns"""
        return 0.8  # Mock behavior score

    def _get_safety_level(self, safety_score: float) -> str:
        """Get safety level from score"""
        if safety_score >= 0.8:
            return "high"
        elif safety_score >= 0.6:
            return "medium"
        else:
            return "low"

    async def _get_safety_recommendations(self, safety_score: float, content_score: float) -> List[str]:
        """Get safety recommendations"""
        recommendations = []
        
        if safety_score < 0.7:
            recommendations.append("Review content guidelines with influencer")
        if content_score < 0.6:
            recommendations.append("Request content pre-approval")
        
        return recommendations

    async def _get_historical_performance(self, influencer_id: str) -> Dict[str, Any]:
        """Get historical performance data"""
        return {
            "average_engagement_rate": 0.04,
            "campaign_success_rate": 0.8,
            "brand_satisfaction_score": 4.2
        }

    async def _calculate_prediction_confidence(self, historical_data: Dict[str, Any], campaign_details: Dict[str, Any]) -> float:
        """Calculate prediction confidence"""
        return 0.75  # Mock confidence score

    async def _classify_performance_tier(self, predicted_engagements: int, follower_count: int) -> str:
        """Classify performance tier"""
        engagement_rate = predicted_engagements / follower_count if follower_count > 0 else 0
        
        if engagement_rate >= 0.06:
            return "high_performer"
        elif engagement_rate >= 0.03:
            return "average_performer"
        else:
            return "low_performer"

    async def _get_performance_optimization_tips(self, campaign_details: Dict[str, Any], influencer_profile: Dict[str, Any]) -> List[str]:
        """Get performance optimization tips"""
        return [
            "Post during peak audience hours",
            "Use trending hashtags relevant to campaign",
            "Include clear call-to-action",
            "Encourage audience interaction"
        ]