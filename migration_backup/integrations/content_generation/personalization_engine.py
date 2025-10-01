"""
Personalization Engine - Content Generation Module
===============================================
User-specific content adaptation with behavioral analysis.
AI-powered personalization for enhanced engagement and conversion.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Integrations
Version: 1.0 Production
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)

class PersonalizationType(Enum):
    """Types of personalization."""
    CONTENT_RECOMMENDATION = "content_recommendation"
    STYLE_ADAPTATION = "style_adaptation"
    TIMING_OPTIMIZATION = "timing_optimization"
    PLATFORM_OPTIMIZATION = "platform_optimization"
    DEMOGRAPHIC_TARGETING = "demographic_targeting"
    BEHAVIORAL_ADAPTATION = "behavioral_adaptation"

class UserSegment(Enum):
    """User segment categories."""
    CASUAL_VIEWER = "casual_viewer"
    POWER_USER = "power_user"
    CREATOR = "creator"
    BUSINESS_USER = "business_user"
    INFLUENCER = "influencer"
    ENTERPRISE = "enterprise"

class ContentPreference(Enum):
    """Content preference categories."""
    ENTERTAINMENT = "entertainment"
    EDUCATIONAL = "educational"
    NEWS = "news"
    LIFESTYLE = "lifestyle"
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    CREATIVE = "creative"
    SPORTS = "sports"

class EngagementPattern(Enum):
    """User engagement patterns."""
    HIGH_ENGAGEMENT = "high_engagement"
    MODERATE_ENGAGEMENT = "moderate_engagement"
    LOW_ENGAGEMENT = "low_engagement"
    IRREGULAR_ENGAGEMENT = "irregular_engagement"
    PEAK_TIME_USER = "peak_time_user"
    BINGE_CONSUMER = "binge_consumer"

@dataclass
class UserProfile:
    """User profile for personalization."""
    user_id: str
    demographics: Dict[str, Any] = field(default_factory=dict)
    preferences: List[ContentPreference] = field(default_factory=list)
    engagement_pattern: EngagementPattern = EngagementPattern.MODERATE_ENGAGEMENT
    user_segment: UserSegment = UserSegment.CASUAL_VIEWER
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    platform_usage: Dict[str, float] = field(default_factory=dict)  # Platform -> usage percentage
    peak_activity_times: List[int] = field(default_factory=list)  # Hours of day (0-23)
    content_performance: Dict[str, float] = field(default_factory=dict)  # Content type -> engagement score

@dataclass
class PersonalizationRequest:
    """Personalization request configuration."""
    request_id: str
    user_profile: UserProfile
    content_id: str
    content_type: str
    content_url: str
    personalization_types: List[PersonalizationType]
    target_platform: Optional[str] = None
    optimization_goals: List[str] = field(default_factory=list)  # e.g., ["engagement", "conversion", "retention"]
    a_b_test_variant: Optional[str] = None
    custom_parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PersonalizationResult:
    """Personalization result."""
    personalization_id: str
    user_id: str
    original_content_id: str
    personalized_content_url: str
    personalization_applied: List[str]
    engagement_prediction: float
    conversion_prediction: float
    relevance_score: float
    processing_time: float
    metadata: Dict[str, Any]
    success: bool = True
    error_message: Optional[str] = None

class PersonalizationAgent:
    """Base class for personalization agents."""
    
    def __init__(self, agent_name: str, specialization: str, personalization_types: List[PersonalizationType]):
        self.agent_name = agent_name
        self.specialization = specialization
        self.personalization_types = personalization_types
        self.agent_id = str(uuid.uuid4())
        self.performance_metrics = {
            'personalization_count': 0,
            'average_engagement_lift': 0.0,
            'average_relevance_score': 0.0,
            'average_processing_time': 0.0,
            'accuracy_rate': 0.0
        }
    
    async def personalize_content(self, request: PersonalizationRequest) -> PersonalizationResult:
        """Personalize content for user."""
        start_time = datetime.now()
        
        try:
            # Validate personalization type compatibility
            if not any(pt in self.personalization_types for pt in request.personalization_types):
                raise ValueError(f"Agent {self.agent_name} cannot handle requested personalization types")
            
            # Analyze user profile
            user_analysis = await self._analyze_user_profile(request.user_profile)
            
            # Generate personalization strategy
            strategy = await self._generate_personalization_strategy(request, user_analysis)
            
            # Apply personalization
            personalized_url = await self._apply_personalization(request, strategy)
            
            # Calculate prediction metrics
            engagement_prediction = self._predict_engagement(request, user_analysis, strategy)
            conversion_prediction = self._predict_conversion(request, user_analysis, strategy)
            relevance_score = self._calculate_relevance_score(request, user_analysis, strategy)
            
            result = PersonalizationResult(
                personalization_id=f"pers_{self.agent_name}_{uuid.uuid4().hex[:8]}",
                user_id=request.user_profile.user_id,
                original_content_id=request.content_id,
                personalized_content_url=personalized_url,
                personalization_applied=[pt.value for pt in request.personalization_types if pt in self.personalization_types],
                engagement_prediction=engagement_prediction,
                conversion_prediction=conversion_prediction,
                relevance_score=relevance_score,
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={
                    'agent': self.agent_name,
                    'user_segment': request.user_profile.user_segment.value,
                    'engagement_pattern': request.user_profile.engagement_pattern.value,
                    'target_platform': request.target_platform,
                    'strategy': strategy,
                    'user_analysis': user_analysis,
                    'processing_date': datetime.now().isoformat()
                }
            )
            
            self._update_metrics(result)
            return result
            
        except Exception as e:
            logger.error(f"Personalization failed for agent {self.agent_name}: {str(e)}")
            return PersonalizationResult(
                personalization_id="",
                user_id=request.user_profile.user_id,
                original_content_id=request.content_id,
                personalized_content_url="",
                personalization_applied=[],
                engagement_prediction=0.0,
                conversion_prediction=0.0,
                relevance_score=0.0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={},
                success=False,
                error_message=str(e)
            )
    
    async def _analyze_user_profile(self, profile: UserProfile) -> Dict[str, Any]:
        """Analyze user profile for personalization insights."""
        await asyncio.sleep(0.03)  # Simulate analysis time
        
        analysis = {
            'engagement_level': self._assess_engagement_level(profile),
            'content_affinity': self._analyze_content_affinity(profile),
            'platform_preference': self._determine_platform_preference(profile),
            'optimal_timing': self._analyze_optimal_timing(profile),
            'personalization_receptivity': self._assess_personalization_receptivity(profile)
        }
        
        return analysis
    
    def _assess_engagement_level(self, profile: UserProfile) -> str:
        """Assess user's engagement level."""
        engagement_mapping = {
            EngagementPattern.HIGH_ENGAGEMENT: "high",
            EngagementPattern.MODERATE_ENGAGEMENT: "moderate",
            EngagementPattern.LOW_ENGAGEMENT: "low",
            EngagementPattern.IRREGULAR_ENGAGEMENT: "irregular",
            EngagementPattern.PEAK_TIME_USER: "time_sensitive",
            EngagementPattern.BINGE_CONSUMER: "intensive"
        }
        
        return engagement_mapping.get(profile.engagement_pattern, "moderate")
    
    def _analyze_content_affinity(self, profile: UserProfile) -> Dict[str, float]:
        """Analyze user's content type affinities."""
        affinities = {}
        
        # Base affinities from preferences
        for preference in profile.preferences:
            affinities[preference.value] = 0.8
        
        # Historical performance influences
        for content_type, performance in profile.content_performance.items():
            if content_type in affinities:
                affinities[content_type] = (affinities[content_type] + performance) / 2
            else:
                affinities[content_type] = performance * 0.6
        
        return affinities
    
    def _determine_platform_preference(self, profile: UserProfile) -> str:
        """Determine user's preferred platform."""
        if not profile.platform_usage:
            return "unknown"
        
        return max(profile.platform_usage, key=profile.platform_usage.get)
    
    def _analyze_optimal_timing(self, profile: UserProfile) -> Dict[str, Any]:
        """Analyze optimal timing for content delivery."""
        if not profile.peak_activity_times:
            return {'hours': [9, 12, 18, 21], 'confidence': 0.3}  # Default times
        
        return {
            'hours': profile.peak_activity_times,
            'confidence': 0.9,
            'pattern': profile.engagement_pattern.value
        }
    
    def _assess_personalization_receptivity(self, profile: UserProfile) -> float:
        """Assess how receptive user is to personalization."""
        base_receptivity = 0.7
        
        # Power users and creators are more receptive
        if profile.user_segment in [UserSegment.POWER_USER, UserSegment.CREATOR, UserSegment.INFLUENCER]:
            base_receptivity += 0.2
        
        # High engagement users are more receptive
        if profile.engagement_pattern == EngagementPattern.HIGH_ENGAGEMENT:
            base_receptivity += 0.1
        
        return min(1.0, base_receptivity)
    
    async def _generate_personalization_strategy(self, request: PersonalizationRequest, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalization strategy based on analysis."""
        await asyncio.sleep(0.02)  # Simulate strategy generation
        
        strategy = {
            'primary_focus': self._determine_primary_focus(request, analysis),
            'secondary_optimizations': self._identify_secondary_optimizations(request, analysis),
            'content_adjustments': self._plan_content_adjustments(request, analysis),
            'timing_recommendations': analysis.get('optimal_timing', {}),
            'platform_optimizations': self._plan_platform_optimizations(request, analysis)
        }
        
        return strategy
    
    def _determine_primary_focus(self, request: PersonalizationRequest, analysis: Dict[str, Any]) -> str:
        """Determine the primary personalization focus."""
        if "engagement" in request.optimization_goals:
            return "engagement_optimization"
        elif "conversion" in request.optimization_goals:
            return "conversion_optimization"
        elif "retention" in request.optimization_goals:
            return "retention_optimization"
        else:
            return "relevance_optimization"
    
    def _identify_secondary_optimizations(self, request: PersonalizationRequest, analysis: Dict[str, Any]) -> List[str]:
        """Identify secondary optimization opportunities."""
        optimizations = []
        
        # Platform-specific optimization
        if request.target_platform and request.target_platform in analysis.get('platform_preference', ''):
            optimizations.append("platform_alignment")
        
        # Timing optimization
        if analysis.get('optimal_timing', {}).get('confidence', 0) > 0.7:
            optimizations.append("timing_optimization")
        
        # Content affinity alignment
        content_affinities = analysis.get('content_affinity', {})
        if content_affinities and max(content_affinities.values()) > 0.8:
            optimizations.append("content_affinity_boost")
        
        return optimizations
    
    def _plan_content_adjustments(self, request: PersonalizationRequest, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Plan specific content adjustments."""
        adjustments = {
            'style_modifications': [],
            'format_optimizations': [],
            'personalized_elements': []
        }
        
        user_profile = request.user_profile
        
        # Style modifications based on user segment
        if user_profile.user_segment == UserSegment.BUSINESS_USER:
            adjustments['style_modifications'].append('professional_tone')
        elif user_profile.user_segment == UserSegment.CASUAL_VIEWER:
            adjustments['style_modifications'].append('casual_friendly')
        
        # Format optimizations based on engagement pattern
        if user_profile.engagement_pattern == EngagementPattern.BINGE_CONSUMER:
            adjustments['format_optimizations'].append('extended_format')
        elif user_profile.engagement_pattern == EngagementPattern.LOW_ENGAGEMENT:
            adjustments['format_optimizations'].append('concise_format')
        
        # Personalized elements
        adjustments['personalized_elements'].append('user_name_integration')
        adjustments['personalized_elements'].append('preference_based_examples')
        
        return adjustments
    
    def _plan_platform_optimizations(self, request: PersonalizationRequest, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Plan platform-specific optimizations."""
        if not request.target_platform:
            return {}
        
        platform_optimizations = {
            'youtube': {
                'thumbnail_optimization': True,
                'title_optimization': True,
                'description_seo': True
            },
            'tiktok': {
                'vertical_format': True,
                'trend_integration': True,
                'hook_optimization': True
            },
            'instagram': {
                'visual_optimization': True,
                'story_adaptation': True,
                'hashtag_optimization': True
            },
            'linkedin': {
                'professional_tone': True,
                'business_focus': True,
                'industry_relevance': True
            }
        }
        
        return platform_optimizations.get(request.target_platform.lower(), {})
    
    async def _apply_personalization(self, request: PersonalizationRequest, strategy: Dict[str, Any]) -> str:
        """Apply personalization strategy to content."""
        # Simulate processing time based on complexity
        complexity_score = len(request.personalization_types) * 0.02
        await asyncio.sleep(complexity_score)
        
        # Generate personalized content URL
        personalized_url = f"https://personalized-content.ainflue.com/{request.content_id}_pers_{request.user_profile.user_id}_{self.agent_name}.mp4"
        
        return personalized_url
    
    def _predict_engagement(self, request: PersonalizationRequest, analysis: Dict[str, Any], strategy: Dict[str, Any]) -> float:
        """Predict engagement likelihood."""
        base_engagement = 0.5
        
        # User engagement level influence
        engagement_level = analysis.get('engagement_level', 'moderate')
        engagement_multipliers = {
            'high': 1.4,
            'moderate': 1.0,
            'low': 0.6,
            'irregular': 0.8,
            'time_sensitive': 1.2,
            'intensive': 1.3
        }
        
        base_engagement *= engagement_multipliers.get(engagement_level, 1.0)
        
        # Content affinity boost
        content_affinities = analysis.get('content_affinity', {})
        if content_affinities and request.content_type in content_affinities:
            affinity_boost = content_affinities[request.content_type] * 0.3
            base_engagement += affinity_boost
        
        # Platform alignment bonus
        if 'platform_alignment' in strategy.get('secondary_optimizations', []):
            base_engagement += 0.1
        
        # Personalization receptivity factor
        receptivity = analysis.get('personalization_receptivity', 0.7)
        base_engagement *= (0.7 + receptivity * 0.3)
        
        return min(1.0, max(0.0, base_engagement))
    
    def _predict_conversion(self, request: PersonalizationRequest, analysis: Dict[str, Any], strategy: Dict[str, Any]) -> float:
        """Predict conversion likelihood."""
        base_conversion = 0.15
        
        # Business users and enterprise have higher conversion potential
        if request.user_profile.user_segment in [UserSegment.BUSINESS_USER, UserSegment.ENTERPRISE]:
            base_conversion += 0.2
        
        # Engagement prediction influences conversion
        engagement_pred = self._predict_engagement(request, analysis, strategy)
        base_conversion += engagement_pred * 0.3
        
        # Conversion-focused optimization
        if strategy.get('primary_focus') == 'conversion_optimization':
            base_conversion += 0.15
        
        return min(1.0, max(0.0, base_conversion))
    
    def _calculate_relevance_score(self, request: PersonalizationRequest, analysis: Dict[str, Any], strategy: Dict[str, Any]) -> float:
        """Calculate content relevance score."""
        base_relevance = 0.6
        
        # Content affinity alignment
        content_affinities = analysis.get('content_affinity', {})
        if content_affinities and request.content_type in content_affinities:
            base_relevance += content_affinities[request.content_type] * 0.3
        
        # Platform preference alignment
        platform_pref = analysis.get('platform_preference', '')
        if request.target_platform and request.target_platform.lower() == platform_pref.lower():
            base_relevance += 0.1
        
        # Personalization depth bonus
        personalization_depth = len(request.personalization_types) / len(PersonalizationType)
        base_relevance += personalization_depth * 0.1
        
        return min(1.0, max(0.0, base_relevance))
    
    def _update_metrics(self, result: PersonalizationResult):
        """Update agent performance metrics."""
        self.performance_metrics['personalization_count'] += 1
        count = self.performance_metrics['personalization_count']
        
        # Calculate engagement lift (predicted vs baseline)
        baseline_engagement = 0.3  # Assumed baseline
        engagement_lift = max(0, result.engagement_prediction - baseline_engagement)
        
        # Update average engagement lift
        current_avg_lift = self.performance_metrics['average_engagement_lift']
        self.performance_metrics['average_engagement_lift'] = (
            (current_avg_lift * (count - 1) + engagement_lift) / count
        )
        
        # Update average relevance score
        current_avg_relevance = self.performance_metrics['average_relevance_score']
        self.performance_metrics['average_relevance_score'] = (
            (current_avg_relevance * (count - 1) + result.relevance_score) / count
        )
        
        # Update average processing time
        current_avg_time = self.performance_metrics['average_processing_time']
        self.performance_metrics['average_processing_time'] = (
            (current_avg_time * (count - 1) + result.processing_time) / count
        )
        
        # Update accuracy rate (high relevance = high accuracy)
        accurate_predictions = self.performance_metrics['accuracy_rate'] * (count - 1)
        if result.relevance_score > 0.8:
            accurate_predictions += 1
        
        self.performance_metrics['accuracy_rate'] = accurate_predictions / count

class PersonalizationEngine:
    """
    Enterprise personalization engine with intelligent user adaptation.
    
    Features:
    - User preference learning and behavioral analysis
    - Content recommendation algorithms based on engagement patterns
    - Demographic and psychographic targeting
    - A/B testing automation for optimization
    - Real-time personalization with performance tracking
    """
    
    def __init__(self):
        self.engine_id = str(uuid.uuid4())
        self.agents = self._initialize_agents()
        self.total_personalizations = 0
        self.engine_metrics = {
            'total_personalizations': 0,
            'average_engagement_lift': 0.0,
            'average_relevance_score': 0.0,
            'average_conversion_lift': 0.0,
            'success_rate': 1.0
        }
        logger.info(f"PersonalizationEngine initialized with {len(self.agents)} specialized agents")
    
    def _initialize_agents(self) -> Dict[str, PersonalizationAgent]:
        """Initialize personalization agents."""
        agents = {
            'recommendation': PersonalizationAgent(
                "recommendation_agent",
                "Content recommendation and preference matching",
                [PersonalizationType.CONTENT_RECOMMENDATION, PersonalizationType.BEHAVIORAL_ADAPTATION]
            ),
            'style_adaptation': PersonalizationAgent(
                "style_adaptation_agent",
                "Content style adaptation based on user preferences",
                [PersonalizationType.STYLE_ADAPTATION, PersonalizationType.DEMOGRAPHIC_TARGETING]
            ),
            'timing_optimization': PersonalizationAgent(
                "timing_optimization_agent",
                "Optimal timing and scheduling based on user behavior",
                [PersonalizationType.TIMING_OPTIMIZATION, PersonalizationType.BEHAVIORAL_ADAPTATION]
            ),
            'platform_optimization': PersonalizationAgent(
                "platform_optimization_agent",
                "Platform-specific content optimization",
                [PersonalizationType.PLATFORM_OPTIMIZATION, PersonalizationType.DEMOGRAPHIC_TARGETING]
            )
        }
        return agents
    
    async def personalize_content(self, request: PersonalizationRequest) -> PersonalizationResult:
        """
        Personalize content for specific user.
        
        Args:
            request: Personalization configuration
            
        Returns:
            PersonalizationResult with personalized content
        """
        start_time = datetime.now()
        
        try:
            # Select appropriate agent based on personalization types
            agent = self._select_agent(request)
            
            logger.info(f"Personalizing content with agent: {agent.agent_name}")
            
            # Apply personalization using selected agent
            result = await agent.personalize_content(request)
            
            if result.success:
                # Apply post-processing enhancements
                result = await self._apply_post_processing(result, request)
                
                # Update engine metrics
                self._update_engine_metrics(result)
                
                logger.info(f"Content personalization completed: {result.personalization_id}")
            else:
                logger.error(f"Content personalization failed: {result.error_message}")
            
            return result
            
        except Exception as e:
            logger.error(f"Personalization engine error: {str(e)}")
            return PersonalizationResult(
                personalization_id="",
                user_id=request.user_profile.user_id,
                original_content_id=request.content_id,
                personalized_content_url="",
                personalization_applied=[],
                engagement_prediction=0.0,
                conversion_prediction=0.0,
                relevance_score=0.0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={},
                success=False,
                error_message=str(e)
            )
    
    def _select_agent(self, request: PersonalizationRequest) -> PersonalizationAgent:
        """Select the most appropriate agent based on personalization types."""
        # Count capabilities for each agent
        agent_scores = {}
        
        for agent_name, agent in self.agents.items():
            score = sum(1 for pt in request.personalization_types if pt in agent.personalization_types)
            agent_scores[agent_name] = score
        
        # Select agent with highest capability score
        best_agent_name = max(agent_scores, key=agent_scores.get) if agent_scores else 'recommendation'
        return self.agents[best_agent_name]
    
    async def _apply_post_processing(self, result: PersonalizationResult, request: PersonalizationRequest) -> PersonalizationResult:
        """Apply post-processing enhancements."""
        try:
            await asyncio.sleep(0.01)  # Simulate post-processing
            
            # Enhance scores based on comprehensive personalization
            if len(result.personalization_applied) > 2:
                result.engagement_prediction += 0.05
                result.relevance_score += 0.03
            
            # Add post-processing metadata
            result.metadata['post_processing'] = {
                'comprehensive_personalization': len(result.personalization_applied) > 2,
                'a_b_test_variant': request.a_b_test_variant,
                'optimization_goals': request.optimization_goals
            }
            
            # A/B testing considerations
            if request.a_b_test_variant:
                result.metadata['a_b_testing'] = {
                    'variant': request.a_b_test_variant,
                    'baseline_comparison': True
                }
            
            return result
            
        except Exception as e:
            logger.warning(f"Personalization post-processing failed: {str(e)}")
            return result
    
    def _update_engine_metrics(self, result: PersonalizationResult):
        """Update engine-level performance metrics."""
        self.total_personalizations += 1
        
        # Calculate engagement lift
        baseline_engagement = 0.3
        engagement_lift = max(0, result.engagement_prediction - baseline_engagement)
        
        # Update average engagement lift
        current_avg_engagement_lift = self.engine_metrics['average_engagement_lift']
        self.engine_metrics['average_engagement_lift'] = (
            (current_avg_engagement_lift * (self.total_personalizations - 1) + engagement_lift) / self.total_personalizations
        )
        
        # Update average relevance score
        current_avg_relevance = self.engine_metrics['average_relevance_score']
        self.engine_metrics['average_relevance_score'] = (
            (current_avg_relevance * (self.total_personalizations - 1) + result.relevance_score) / self.total_personalizations
        )
        
        # Calculate conversion lift
        baseline_conversion = 0.05
        conversion_lift = max(0, result.conversion_prediction - baseline_conversion)
        
        # Update average conversion lift
        current_avg_conversion_lift = self.engine_metrics['average_conversion_lift']
        self.engine_metrics['average_conversion_lift'] = (
            (current_avg_conversion_lift * (self.total_personalizations - 1) + conversion_lift) / self.total_personalizations
        )
        
        # Update success rate
        successful_personalizations = self.engine_metrics['total_personalizations']
        if result.success:
            successful_personalizations += 1
        
        self.engine_metrics['total_personalizations'] = successful_personalizations
        self.engine_metrics['success_rate'] = successful_personalizations / self.total_personalizations
    
    async def batch_personalize(self, requests: List[PersonalizationRequest]) -> List[PersonalizationResult]:
        """Personalize multiple content items concurrently."""
        tasks = [self.personalize_content(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch personalization failed for request {i}: {str(result)}")
                processed_results.append(PersonalizationResult(
                    personalization_id="",
                    user_id=requests[i].user_profile.user_id,
                    original_content_id=requests[i].content_id,
                    personalized_content_url="",
                    personalization_applied=[],
                    engagement_prediction=0.0,
                    conversion_prediction=0.0,
                    relevance_score=0.0,
                    processing_time=0.0,
                    metadata={},
                    success=False,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get comprehensive engine statistics."""
        return {
            'engine_id': self.engine_id,
            'total_agents': len(self.agents),
            'engine_metrics': self.engine_metrics,
            'agent_performance': {
                name: agent.performance_metrics 
                for name, agent in self.agents.items()
            }
        }
    
    def get_supported_personalization_types(self) -> List[str]:
        """Get list of supported personalization types."""
        return [pt.value for pt in PersonalizationType]
    
    def get_supported_user_segments(self) -> List[str]:
        """Get list of supported user segments."""
        return [segment.value for segment in UserSegment]

# Export main class
__all__ = ['PersonalizationEngine', 'PersonalizationRequest', 'PersonalizationResult', 'UserProfile']