"""Matching Engine - Ultra-Advanced Processing Engine

Core processing engine for influencer matching with AI-powered
creator analysis and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)

class MatchingCriteria(Enum):
    """Criteria for influencer matching"""
    AUDIENCE_DEMOGRAPHICS = "audience_demographics"
    CONTENT_STYLE = "content_style"
    ENGAGEMENT_RATE = "engagement_rate"
    NICHE_COMPATIBILITY = "niche_compatibility"
    BRAND_ALIGNMENT = "brand_alignment"
    BUDGET_RANGE = "budget_range"

class CollaborationType(Enum):
    """Types of collaboration"""
    SPONSORED_POST = "sponsored_post"
    PRODUCT_REVIEW = "product_review"
    BRAND_PARTNERSHIP = "brand_partnership"
    CONTENT_CREATION = "content_creation"

@dataclass
class MatchingJob:
    """Influencer matching job definition"""
    job_id: str
    brand_requirements: Dict[str, Any]
    collaboration_type: CollaborationType
    budget_range: Tuple[float, float]
    target_audience: Dict[str, Any]
    preferred_platforms: List[str]
    matching_criteria: List[MatchingCriteria]
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    
@dataclass 
class MatchingResult:
    """Influencer matching result"""
    job_id: str
    matched_creators: List[Dict[str, Any]]
    matching_scores: Dict[str, float]
    recommendations: List[str]
    success: bool = True
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    completed_at: datetime = field(default_factory=datetime.now)

class MatchingEngine:
    """
    Ultra-Advanced Influencer Matching Engine
    
    Provides enterprise-grade influencer matching with:
    - AI-powered creator analysis and compatibility scoring
    - Multi-platform creator discovery
    - Audience alignment analysis
    - Budget optimization recommendations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.active_jobs: Dict[str, MatchingJob] = {}
        self.job_results: Dict[str, MatchingResult] = {}
        
        # Sample creator database
        self.creator_database = self._initialize_sample_creators()
        
        self.logger.info("Matching Engine initialized")

    def _initialize_sample_creators(self) -> List[Dict[str, Any]]:
        """Initialize sample creator database"""
        return [
            {
                'creator_id': 'creator_001',
                'name': 'Tech Reviewer Pro',
                'handle': '@techreviewer',
                'platforms': ['youtube', 'instagram'],
                'follower_counts': {'youtube': 150000, 'instagram': 75000},
                'engagement_rates': {'youtube': 0.08, 'instagram': 0.12},
                'content_categories': ['technology', 'gadgets', 'reviews'],
                'rates': {'sponsored_post': 2500, 'product_review': 3000},
                'brand_safety_score': 0.95,
                'authenticity_score': 0.88
            },
            {
                'creator_id': 'creator_002',
                'name': 'Lifestyle Maven',
                'handle': '@lifestylemaven',
                'platforms': ['instagram', 'youtube'],
                'follower_counts': {'instagram': 250000, 'youtube': 80000},
                'engagement_rates': {'instagram': 0.14, 'youtube': 0.09},
                'content_categories': ['lifestyle', 'fashion', 'wellness'],
                'rates': {'sponsored_post': 4000, 'brand_partnership': 8000},
                'brand_safety_score': 0.92,
                'authenticity_score': 0.91
            }
        ]

    async def find_matching_creators(
        self,
        brand_requirements: Dict[str, Any],
        collaboration_type: str = "sponsored_post",
        options: Optional[Dict[str, Any]] = None
    ) -> MatchingResult:
        """Find creators that match brand requirements"""
        job_id = f"matching_{datetime.now().timestamp()}"
        options = options or {}
        
        job = MatchingJob(
            job_id=job_id,
            brand_requirements=brand_requirements,
            collaboration_type=CollaborationType(collaboration_type),
            budget_range=brand_requirements.get('budget_range', (1000, 10000)),
            target_audience=brand_requirements.get('target_audience', {}),
            preferred_platforms=brand_requirements.get('preferred_platforms', []),
            matching_criteria=[MatchingCriteria.NICHE_COMPATIBILITY]
        )
        
        self.active_jobs[job_id] = job
        job.status = "running"
        
        try:
            start_time = datetime.now()
            
            # Find matching creators
            matched_creators = await self._find_compatible_creators(brand_requirements)
            
            # Calculate matching scores
            matching_scores = await self._calculate_matching_scores(matched_creators, brand_requirements)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(matched_creators)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = MatchingResult(
                job_id=job_id,
                matched_creators=matched_creators,
                matching_scores=matching_scores,
                recommendations=recommendations,
                processing_time=processing_time
            )
            
            job.status = "completed"
            self.job_results[job_id] = result
            
            self.logger.info(f"Creator matching completed for job {job_id}")
            return result
            
        except Exception as e:
            job.status = "failed"
            error_result = MatchingResult(
                job_id=job_id,
                matched_creators=[],
                matching_scores={},
                recommendations=[],
                success=False,
                error_message=str(e)
            )
            self.job_results[job_id] = error_result
            self.logger.error(f"Creator matching failed for job {job_id}: {str(e)}")
            return error_result

    async def _find_compatible_creators(self, brand_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find creators compatible with brand requirements"""
        compatible_creators = []
        required_categories = brand_requirements.get('content_categories', [])
        budget_range = brand_requirements.get('budget_range', (0, float('inf')))
        
        for creator in self.creator_database:
            # Check content category compatibility
            if required_categories:
                category_match = any(cat in creator['content_categories'] for cat in required_categories)
                if not category_match:
                    continue
            
            # Check budget compatibility
            creator_rates = list(creator['rates'].values())
            if creator_rates:
                min_rate = min(creator_rates)
                if min_rate < budget_range[0] or min_rate > budget_range[1]:
                    continue
            
            compatible_creators.append(creator)
        
        return compatible_creators

    async def _calculate_matching_scores(self, creators: List[Dict[str, Any]], brand_requirements: Dict[str, Any]) -> Dict[str, float]:
        """Calculate compatibility scores for creators"""
        matching_scores = {}
        
        for creator in creators:
            score = 0.0
            
            # Engagement rate score (25%)
            avg_engagement = sum(creator['engagement_rates'].values()) / len(creator['engagement_rates'])
            engagement_score = min(1.0, avg_engagement / 0.15)
            score += engagement_score * 0.25
            
            # Brand safety score (30%)
            score += creator['brand_safety_score'] * 0.3
            
            # Authenticity score (25%)
            score += creator['authenticity_score'] * 0.25
            
            # Category alignment (20%)
            required_categories = brand_requirements.get('content_categories', [])
            if required_categories:
                category_overlap = len(set(required_categories) & set(creator['content_categories']))
                category_score = category_overlap / len(required_categories)
                score += category_score * 0.2
            
            matching_scores[creator['creator_id']] = round(score, 3)
        
        return matching_scores

    async def _generate_recommendations(self, creators: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on matching results"""
        recommendations = []
        
        if len(creators) == 0:
            recommendations.append("No creators found matching current criteria")
        elif len(creators) < 3:
            recommendations.append("Limited creator options found. Consider expanding requirements")
        else:
            recommendations.append(f"Found {len(creators)} compatible creators for your campaign")
        
        recommendations.extend([
            "Review creator authenticity scores for genuine engagement",
            "Consider running test campaigns with top creators",
            "Analyze previous brand collaborations for style alignment"
        ])
        
        return recommendations

    async def get_job_result(self, job_id: str) -> Optional[MatchingResult]:
        """Get the result of a completed matching job"""
        return self.job_results.get(job_id)