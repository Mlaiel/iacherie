"""IA Influencer Agent - Marketplace Matching System
Enterprise-grade matching engine for creators, content, and collaborations.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent
Copyright: All rights reserved - Unauthorized use strictly prohibited

WARNING: This code and concept are proprietary to Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Legal action will be taken against violators.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import numpy as np
from scipy.spatial.distance import cosine
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import BaseModel
from ...core.cache import CacheManager
from ...ai.content_analysis import ContentAnalyzer
from ...ai.recommendation_engine import RecommendationEngine
from ...ml.matching_algorithms import MatchingEngine


class MatchingStrategy(Enum):
    """
Matching strategy enumeration."""

    CONTENT_BASED = "content_based"
    COLLABORATIVE = "collaborative"
    HYBRID = "hybrid"
    AI_POWERED = "ai_powered"
    PERSONALITY_BASED = "personality_based"


class CollaborationType(Enum):
    """Collaboration type enumeration."""

    JOINT_CONTENT = "joint_content"
    CROSS_PROMOTION = "cross_promotion"
    SKILL_EXCHANGE = "skill_exchange"
    BRAND_PARTNERSHIP = "brand_partnership"
    EVENT_COLLABORATION = "event_collaboration"
    MENTORSHIP = "mentorship"


@dataclass
class MatchingCriteria:
    """Matching criteria configuration."""
    strategy: MatchingStrategy
    weights: Dict[str, float]
    filters: Dict[str, Any]
    minimum_score: float
    max_results: int
    include_explanations: bool = True


@dataclass
class CollaborationRequest:
    """
Collaboration request structure."""
    requester_id: str
    collaboration_type: CollaborationType
    project_description: str
    required_skills: List[str]
    preferred_audience: Dict[str, Any]
    timeline: Dict[str, datetime]
    budget_range: Optional[Tuple[float, float]]
    geographic_preferences: Optional[List[str]]


class CollaborationMatcher:
    """
    Enterprise collaboration matching system.
    Matches creators for various types of collaborations using advanced AI algorithms.
    """
    
    def __init__(
        self,
        db_session: AsyncSession,
        cache_manager: CacheManager,
        matching_engine: MatchingEngine,
        content_analyzer: ContentAnalyzer
    ):
        self.db = db_session
        self.cache = cache_manager
        self.matching_engine = matching_engine
        self.analyzer = content_analyzer
        self.logger = logging.getLogger(__name__)
    
    async def find_collaboration_matches(
        self,
        request: CollaborationRequest,
        criteria: MatchingCriteria
    ) -> Dict[str, Any]:
        """
        Find collaboration matches based on request and criteria.
        
        Args:
            request: Collaboration request details
            criteria: Matching criteria and configuration
            
        Returns:
            Matching results with scores and explanations
        """
        try:
            cache_key = f"collab_matches:{hash(str(request))}:{hash(str(criteria))}"
            
            # Check cache
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get requester profile
            requester_profile = await self._get_creator_profile(request.requester_id)
            
            if not requester_profile:
                raise ValueError(f"Requester profile not found: {request.requester_id}")
            
            # Find potential matches based on strategy
            potential_matches = await self._find_potential_matches(
                request, criteria, requester_profile
            )
            
            # Calculate compatibility scores
            scored_matches = await self._calculate_compatibility_scores(
                request, potential_matches, requester_profile
            )
            
            # Apply filters and ranking
            filtered_matches = await self._apply_matching_filters(
                scored_matches, criteria
            )
            
            # Generate explanations if requested
            if criteria.include_explanations:
                filtered_matches = await self._add_match_explanations(
                    filtered_matches, request, requester_profile
                )
            
            result = {
                'matches': filtered_matches[:criteria.max_results],
                'total_found': len(filtered_matches),
                'request_id': f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.requester_id}",
                'generated_at': datetime.now().isoformat(),
                'strategy': criteria.strategy.value
            }
            
            # Cache results
            await self.cache.set(cache_key, result, ttl=3600)
            
            self.logger.info(
                f"Found {len(filtered_matches)} collaboration matches for {request.requester_id}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Collaboration matching failed: {str(e)}")
            return {'matches': [], 'total_found': 0, 'error': str(e)}
    
    async def evaluate_collaboration_potential(
        self,
        creator_a_id: str,
        creator_b_id: str,
        collaboration_type: CollaborationType
    ) -> Dict[str, Any]:
        """
        Evaluate collaboration potential between two specific creators.
        
        Args:
            creator_a_id: First creator ID
            creator_b_id: Second creator ID
            collaboration_type: Type of collaboration
            
        Returns:
            Collaboration potential analysis
        """
        try:
            cache_key = f"collab_eval:{creator_a_id}:{creator_b_id}:{collaboration_type.value}"
            
            # Check cache
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get creator profiles
            creator_a = await self._get_creator_profile(creator_a_id)
            creator_b = await self._get_creator_profile(creator_b_id)
            
            if not creator_a or not creator_b:
                raise ValueError("One or both creator profiles not found")
            
            # Calculate compatibility metrics
            compatibility = await self._calculate_detailed_compatibility(
                creator_a, creator_b, collaboration_type
            )
            
            # Analyze potential synergies
            synergies = await self._analyze_collaboration_synergies(
                creator_a, creator_b, collaboration_type
            )
            
            # Identify potential challenges
            challenges = await self._identify_collaboration_challenges(
                creator_a, creator_b, collaboration_type
            )
            
            # Generate recommendations
            recommendations = await self._generate_collaboration_recommendations(
                creator_a, creator_b, collaboration_type, compatibility
            )
            
            result = {
                'compatibility_score': compatibility['overall_score'],
                'compatibility_breakdown': compatibility['breakdown'],
                'synergies': synergies,
                'challenges': challenges,
                'recommendations': recommendations,
                'collaboration_type': collaboration_type.value,
                'evaluated_at': datetime.now().isoformat()
            }
            
            # Cache evaluation
            await self.cache.set(cache_key, result, ttl=7200)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Collaboration evaluation failed: {str(e)}")
            return {'compatibility_score': 0.0, 'error': str(e)}
    
    async def suggest_collaboration_types(
        self,
        creator_id: str,
        target_creator_ids: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Suggest optimal collaboration types for creator pairs.
        
        Args:
            creator_id: Source creator ID
            target_creator_ids: List of target creator IDs
            
        Returns:
            Collaboration type suggestions for each pair
        """
        try:
            suggestions = {}
            
            # Get source creator profile
            source_creator = await self._get_creator_profile(creator_id)
            
            if not source_creator:
                return {}
            
            # Analyze each potential collaboration
            for target_id in target_creator_ids:
                target_creator = await self._get_creator_profile(target_id)
                
                if not target_creator:
                    continue
                
                # Evaluate all collaboration types
                type_evaluations = []
                
                for collab_type in CollaborationType:
                    evaluation = await self.evaluate_collaboration_potential(
                        creator_id, target_id, collab_type
                    )
                    
                    type_evaluations.append({
                        'type': collab_type.value,
                        'score': evaluation.get('compatibility_score', 0.0),
                        'synergies': evaluation.get('synergies', []),
                        'recommended': evaluation.get('compatibility_score', 0.0) > 0.7
                    })
                
                # Sort by compatibility score
                type_evaluations.sort(
                    key=lambda x: x['score'], 
                    reverse=True
                )
                
                suggestions[target_id] = type_evaluations[:3]  # Top 3 suggestions
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Collaboration type suggestion failed: {str(e)}")
            return {}
    
    async def _find_potential_matches(
        self,
        request: CollaborationRequest,
        criteria: MatchingCriteria,
        requester_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find potential collaboration matches based on strategy."""
        if criteria.strategy == MatchingStrategy.CONTENT_BASED:
            return await self._content_based_matching(request, requester_profile)
        elif criteria.strategy == MatchingStrategy.COLLABORATIVE:
            return await self._collaborative_filtering_matching(request, requester_profile)
        elif criteria.strategy == MatchingStrategy.AI_POWERED:
            return await self._ai_powered_matching(request, requester_profile)
        elif criteria.strategy == MatchingStrategy.PERSONALITY_BASED:
            return await self._personality_based_matching(request, requester_profile)
        else:  # HYBRID
            return await self._hybrid_matching(request, requester_profile)
    
    async def _content_based_matching(
        self,
        request: CollaborationRequest,
        requester_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
Content-based matching using content similarity."""
        # Analyze requester's content characteristics
        content_profile = await self._analyze_creator_content(request.requester_id)
        
        # Find creators with complementary content
        similar_creators = await self._find_content_similar_creators(
            content_profile, request.required_skills
        )
        
        return similar_creators
    
    async def _collaborative_filtering_matching(
        self,
        request: CollaborationRequest,
        requester_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
Collaborative filtering based on past collaborations."""
        # Get collaboration history
        collaboration_history = await self._get_collaboration_history(request.requester_id)
        
        # Find creators who collaborated with similar creators
        collaborative_matches = await self._find_collaborative_matches(
            collaboration_history, request
        )
        
        return collaborative_matches
    
    async def _ai_powered_matching(
        self,
        request: CollaborationRequest,
        requester_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
AI-powered matching using machine learning models."""
        # Use ML model for matching
        ml_matches = await self.matching_engine.predict_matches(
            requester_profile=requester_profile,
            collaboration_request=request.__dict__
        )
        
        return ml_matches
    
    async def _personality_based_matching(
        self,
        request: CollaborationRequest,
        requester_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
Personality-based matching using creator personality profiles."""
        # Get personality profile
        personality_profile = await self._get_personality_profile(request.requester_id)
        
        # Find compatible personalities
        personality_matches = await self._find_personality_compatible_creators(
            personality_profile, request
        )
        
        return personality_matches
    
    async def _hybrid_matching(
        self,
        request: CollaborationRequest,
        requester_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
Hybrid matching combining multiple strategies."""
        # Run multiple matching strategies
        matching_results = await asyncio.gather(
            self._content_based_matching(request, requester_profile),
            self._collaborative_filtering_matching(request, requester_profile),
            self._ai_powered_matching(request, requester_profile),
            return_exceptions=True
        )
        
        # Combine and weight results
        combined_matches = await self._combine_matching_results(
            matching_results, weights=[0.4, 0.3, 0.3]
        )
        
        return combined_matches
    
    async def _calculate_compatibility_scores(
        self,
        request: CollaborationRequest,
        potential_matches: List[Dict[str, Any]],
        requester_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
Calculate detailed compatibility scores for matches."""
        scored_matches = []
        
        for match in potential_matches:
            # Calculate multiple compatibility dimensions
            skill_compatibility = await self._calculate_skill_compatibility(
                request.required_skills, match.get('skills', [])
            )
            
            audience_compatibility = await self._calculate_audience_compatibility(
                requester_profile.get('audience', {}),
                match.get('audience', {})
            )
            
            schedule_compatibility = await self._calculate_schedule_compatibility(
                request.timeline, match.get('availability', {})
            )
            
            value_compatibility = await self._calculate_value_compatibility(
                requester_profile.get('values', {}),
                match.get('values', {})
            )
            
            # Calculate overall score
            overall_score = (
                skill_compatibility * 0.3 +
                audience_compatibility * 0.25 +
                schedule_compatibility * 0.25 +
                value_compatibility * 0.2
            )
            
            match.update({
                'compatibility_score': overall_score,
                'skill_compatibility': skill_compatibility,
                'audience_compatibility': audience_compatibility,
                'schedule_compatibility': schedule_compatibility,
                'value_compatibility': value_compatibility
            })
            
            scored_matches.append(match)
        
        # Sort by overall compatibility score
        scored_matches.sort(
            key=lambda x: x['compatibility_score'],
            reverse=True
        )
        
        return scored_matches
    
    async def _apply_matching_filters(
        self,
        scored_matches: List[Dict[str, Any]],
        criteria: MatchingCriteria
    ) -> List[Dict[str, Any]]:
        """
Apply filters to matching results."""
        filtered_matches = []
        
        for match in scored_matches:
            # Apply minimum score filter
            if match['compatibility_score'] < criteria.minimum_score:
                continue
            
            # Apply custom filters
            passes_filters = True
            
            for filter_key, filter_value in criteria.filters.items():
                if filter_key == 'min_followers' and match.get('follower_count', 0) < filter_value:
                    passes_filters = False
                    break
                elif filter_key == 'verified_only' and filter_value and not match.get('verified', False):
                    passes_filters = False
                    break
                elif filter_key == 'location' and match.get('location') not in filter_value:
                    passes_filters = False
                    break
            
            if passes_filters:
                filtered_matches.append(match)
        
        return filtered_matches
    
    async def _add_match_explanations(
        self,
        matches: List[Dict[str, Any]],
        request: CollaborationRequest,
        requester_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
Add explanations for why matches were suggested."""
        for match in matches:
            explanations = []
            
            # Skill-based explanations
            if match.get('skill_compatibility', 0) > 0.8:
                explanations.append("Strong skill complementarity detected")
            
            # Audience explanations
            if match.get('audience_compatibility', 0) > 0.7:
                explanations.append("Overlapping target audience with cross-appeal potential")
            
            # Engagement explanations
            if match.get('engagement_rate', 0) > 0.05:
                explanations.append("High engagement rate indicates active audience")
            
            # Collaboration history explanations
            if match.get('successful_collaborations', 0) > 5:
                explanations.append("Proven track record in collaborations")
            
            match['match_explanations'] = explanations
        
        return matches
    
    async def _calculate_detailed_compatibility(
        self,
        creator_a: Dict[str, Any],
        creator_b: Dict[str, Any],
        collaboration_type: CollaborationType
    ) -> Dict[str, Any]:
        """Calculate detailed compatibility metrics between two creators."""
        # Calculate various compatibility dimensions
        content_compatibility = await self._calculate_content_compatibility(creator_a, creator_b)
        brand_compatibility = await self._calculate_brand_compatibility(creator_a, creator_b)
        communication_compatibility = await self._calculate_communication_compatibility(creator_a, creator_b)
        workflow_compatibility = await self._calculate_workflow_compatibility(creator_a, creator_b)
        
        # Weight based on collaboration type
        weights = self._get_collaboration_type_weights(collaboration_type)
        
        overall_score = (
            content_compatibility * weights['content'] +
            brand_compatibility * weights['brand'] +
            communication_compatibility * weights['communication'] +
            workflow_compatibility * weights['workflow']
        )
        
        return {
            'overall_score': overall_score,
            'breakdown': {
                'content': content_compatibility,
                'brand': brand_compatibility,
                'communication': communication_compatibility,
                'workflow': workflow_compatibility
            }
        }
    
    def _get_collaboration_type_weights(
        self, 
        collaboration_type: CollaborationType
    ) -> Dict[str, float]:
        """
Get weights for different collaboration types."""
        weights_map = {
            CollaborationType.JOINT_CONTENT: {
                'content': 0.4, 'brand': 0.3, 'communication': 0.2, 'workflow': 0.1
            },
            CollaborationType.CROSS_PROMOTION: {
                'content': 0.2, 'brand': 0.5, 'communication': 0.2, 'workflow': 0.1
            },
            CollaborationType.SKILL_EXCHANGE: {
                'content': 0.3, 'brand': 0.1, 'communication': 0.3, 'workflow': 0.3
            },
            CollaborationType.BRAND_PARTNERSHIP: {
                'content': 0.2, 'brand': 0.6, 'communication': 0.1, 'workflow': 0.1
            },
            CollaborationType.EVENT_COLLABORATION: {
                'content': 0.2, 'brand': 0.2, 'communication': 0.3, 'workflow': 0.3
            },
            CollaborationType.MENTORSHIP: {
                'content': 0.3, 'brand': 0.1, 'communication': 0.4, 'workflow': 0.2
            }
        }
        
        return weights_map.get(collaboration_type, {
            'content': 0.25, 'brand': 0.25, 'communication': 0.25, 'workflow': 0.25
        })


class ContentMatcher:
    """
    Enterprise content matching system.
    Matches content with creators, audiences, and distribution opportunities.
    """
    
    def __init__(
        self,
        db_session: AsyncSession,
        cache_manager: CacheManager,
        content_analyzer: ContentAnalyzer
    ):
        self.db = db_session
        self.cache = cache_manager
        self.analyzer = content_analyzer
        self.logger = logging.getLogger(__name__)
    
    async def match_content_to_creators(
        self,
        content_id: str,
        matching_criteria: Dict[str, Any] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Match content to suitable creators for promotion or collaboration.
        
        Args:
            content_id: Content identifier
            matching_criteria: Matching criteria and filters
            limit: Maximum matches
            
        Returns:
            Creator matches for content
        """
        try:
            cache_key = f"content_creator_matches:{content_id}:{hash(str(matching_criteria))}"
            
            # Check cache
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get content analysis
            content_data = await self._get_content_analysis(content_id)
            
            if not content_data:
                raise ValueError(f"Content not found: {content_id}")
            
            # Find matching creators
            creator_matches = await self._find_content_suitable_creators(
                content_data, matching_criteria, limit
            )
            
            # Calculate match scores
            scored_matches = await self._calculate_content_creator_scores(
                content_data, creator_matches
            )
            
            result = {
                'matches': scored_matches,
                'content_id': content_id,
                'total_matches': len(scored_matches),
                'generated_at': datetime.now().isoformat()
            }
            
            # Cache results
            await self.cache.set(cache_key, result, ttl=3600)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Content-creator matching failed: {str(e)}")
            return {'matches': [], 'total_matches': 0, 'error': str(e)}
    
    async def match_content_to_audiences(
        self,
        content_id: str,
        demographic_filters: Dict[str, Any] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Match content to target audiences based on demographics and interests.
        
        Args:
            content_id: Content identifier
            demographic_filters: Audience demographic filters
            limit: Maximum audience segments
            
        Returns:
            Audience matches for content
        """
        try:
            cache_key = f"content_audience_matches:{content_id}:{hash(str(demographic_filters))}"
            
            # Check cache
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get content analysis
            content_data = await self._get_content_analysis(content_id)
            
            if not content_data:
                raise ValueError(f"Content not found: {content_id}")
            
            # Analyze content for audience appeal
            audience_appeal = await self.analyzer.analyze_audience_appeal(content_data)
            
            # Find matching audience segments
            audience_matches = await self._find_target_audiences(
                audience_appeal, demographic_filters, limit
            )
            
            # Calculate engagement predictions
            engagement_predictions = await self._predict_audience_engagement(
                content_data, audience_matches
            )
            
            result = {
                'audience_segments': audience_matches,
                'engagement_predictions': engagement_predictions,
                'content_id': content_id,
                'generated_at': datetime.now().isoformat()
            }
            
            # Cache results
            await self.cache.set(cache_key, result, ttl=7200)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Content-audience matching failed: {str(e)}")
            return {'audience_segments': [], 'error': str(e)}
    
    async def recommend_content_improvements(
        self,
        content_id: str,
        target_audience: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recommend improvements to content for better audience matching.
        
        Args:
            content_id: Content identifier
            target_audience: Target audience characteristics
            
        Returns:
            Content improvement recommendations
        """
        try:
            # Get content analysis
            content_data = await self._get_content_analysis(content_id)
            
            if not content_data:
                raise ValueError(f"Content not found: {content_id}")
            
            # Analyze content-audience gap
            gap_analysis = await self._analyze_content_audience_gap(
                content_data, target_audience
            )
            
            # Generate improvement recommendations
            improvements = await self._generate_improvement_recommendations(
                content_data, target_audience, gap_analysis
            )
            
            result = {
                'recommendations': improvements,
                'gap_analysis': gap_analysis,
                'content_id': content_id,
                'target_audience': target_audience,
                'generated_at': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Content improvement recommendations failed: {str(e)}")
            return {'recommendations': [], 'error': str(e)}


class InfluencerMatcher:
    """
    Enterprise influencer matching system.
    Matches brands with suitable influencers for campaigns and partnerships.
    """
    
    def __init__(
        self,
        db_session: AsyncSession,
        cache_manager: CacheManager,
        recommendation_engine: RecommendationEngine
    ):
        self.db = db_session
        self.cache = cache_manager
        self.recommender = recommendation_engine
        self.logger = logging.getLogger(__name__)
    
    async def match_brand_to_influencers(
        self,
        brand_profile: Dict[str, Any],
        campaign_requirements: Dict[str, Any],
        matching_criteria: MatchingCriteria,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Match brand with suitable influencers for campaigns.
        
        Args:
            brand_profile: Brand profile and characteristics
            campaign_requirements: Campaign requirements and goals
            matching_criteria: Matching criteria and filters
            limit: Maximum matches
            
        Returns:
            Influencer matches for brand campaign
        """
        try:
            cache_key = f"brand_influencer_matches:{hash(str(brand_profile))}:{hash(str(campaign_requirements))}"
            
            # Check cache
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Find potential influencers
            potential_influencers = await self._find_brand_suitable_influencers(
                brand_profile, campaign_requirements, matching_criteria
            )
            
            # Calculate brand-influencer fit scores
            fit_scores = await self._calculate_brand_influencer_fit(
                brand_profile, campaign_requirements, potential_influencers
            )
            
            # Apply campaign-specific filters
            filtered_matches = await self._apply_campaign_filters(
                fit_scores, campaign_requirements, matching_criteria
            )
            
            # Generate campaign recommendations
            campaign_recs = await self._generate_campaign_recommendations(
                brand_profile, filtered_matches[:limit]
            )
            
            result = {
                'influencer_matches': filtered_matches[:limit],
                'campaign_recommendations': campaign_recs,
                'total_matches': len(filtered_matches),
                'brand_profile': brand_profile.get('name', 'Unknown'),
                'generated_at': datetime.now().isoformat()
            }
            
            # Cache results
            await self.cache.set(cache_key, result, ttl=3600)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Brand-influencer matching failed: {str(e)}")
            return {'influencer_matches': [], 'total_matches': 0, 'error': str(e)}
    
    async def evaluate_influencer_brand_fit(
        self,
        influencer_id: str,
        brand_profile: Dict[str, Any],
        campaign_type: str
    ) -> Dict[str, Any]:
        """
        Evaluate fit between specific influencer and brand for campaign.
        
        Args:
            influencer_id: Influencer identifier
            brand_profile: Brand profile data
            campaign_type: Type of campaign
            
        Returns:
            Detailed fit evaluation
        """
        try:
            # Get influencer profile
            influencer_profile = await self._get_creator_profile(influencer_id)
            
            if not influencer_profile:
                raise ValueError(f"Influencer not found: {influencer_id}")
            
            # Calculate multiple fit dimensions
            brand_alignment = await self._calculate_brand_alignment(
                influencer_profile, brand_profile
            )
            
            audience_match = await self._calculate_audience_brand_match(
                influencer_profile.get('audience', {}), 
                brand_profile.get('target_audience', {})
            )
            
            authenticity_score = await self._calculate_authenticity_score(
                influencer_profile, brand_profile, campaign_type
            )
            
            performance_prediction = await self._predict_campaign_performance(
                influencer_profile, brand_profile, campaign_type
            )
            
            # Calculate overall fit score
            overall_fit = (
                brand_alignment * 0.3 +
                audience_match * 0.3 +
                authenticity_score * 0.2 +
                performance_prediction['score'] * 0.2
            )
            
            result = {
                'overall_fit_score': overall_fit,
                'brand_alignment': brand_alignment,
                'audience_match': audience_match,
                'authenticity_score': authenticity_score,
                'performance_prediction': performance_prediction,
                'recommendation': 'strong_fit' if overall_fit > 0.8 else 'moderate_fit' if overall_fit > 0.6 else 'weak_fit',
                'evaluated_at': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Influencer-brand fit evaluation failed: {str(e)}")
            return {'overall_fit_score': 0.0, 'error': str(e)}
