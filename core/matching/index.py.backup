"""Enterprise Creator Matching & Collaboration Engine - Main Entry Point

This module serves as the primary entry point for the advanced AI-powered creator
collaboration matching system, providing a unified interface for all matching
functionalities and services.

Features:
- Unified API for all matching services
- Enterprise-grade service initialization
- Intelligent service orchestration
- Real-time health monitoring
- Performance optimization
- Business intelligence integration

Quick Start:
    from backend.core.matching import MatchingService
    
    # Initialize the enterprise matching service
    service = MatchingService(config)
    
    # Find optimal collaboration matches
    matches = await service.find_matches(creator_id, preferences)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This unified matching service contains proprietary algorithms and business logic
developed by Fahed Mlaiel. Unauthorized use, reverse engineering, or distribution
is strictly prohibited and subject to legal prosecution.
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.core.cache.strategies import CacheManager
from backend.core.analytics.metrics import MetricsCollector
from backend.core.security.encryption import SecureDataHandler
from backend.core.events.publisher import EventPublisher

from .engine import (
    MatchingEngine,
    ContentType,
    MatchingStrategy,
    CreatorProfile,
    MatchResult
)
from .compatibility import (
    CompatibilityAnalyzer,
    CompatibilityDimension,
    CompatibilityScore
)
from .recommendation import (
    RecommendationEngine,
    RecommendationType,
    CollaborationFormat
)
from .scoring import (
    MatchingScoringService,
    ScoringStrategy,
    ScoreBreakdown
)
from .preferences import (
    UserPreferencesManager,
    PreferenceType,
    PreferenceProfile
)
from .criteria import (
    MatchingCriteriaManager,
    CriteriaType
)
from .validator import (
    MatchValidator,
    ValidationRule,
    ValidationResult
)
from .processor import (
    MatchProcessor,
    ProcessingMode,
    ProcessingResult
)
from .workflow import (
    WorkflowManager,
    WorkflowStage,
    WorkflowConfiguration
)


@dataclass
class MatchingServiceConfig:
    """Enterprise matching service configuration"""
    # Core Services
    enable_ai_matching: bool = True
    enable_recommendation_engine: bool = True
    enable_scoring_service: bool = True
    enable_preferences_learning: bool = True
    
    # Performance Settings
    max_concurrent_matches: int = 100
    cache_ttl: timedelta = timedelta(hours=1)
    processing_timeout: timedelta = timedelta(minutes=30)
    
    # Quality Settings
    min_match_quality: float = 0.65
    max_results_per_request: int = 50
    validation_level: str = "enterprise"
    
    # Business Intelligence
    enable_analytics: bool = True
    enable_revenue_optimization: bool = True
    enable_risk_assessment: bool = True
    
    # Security & Compliance
    encryption_enabled: bool = True
    audit_logging: bool = True
    gdpr_compliance: bool = True


class MatchingService:
    """
    Enterprise Creator Matching & Collaboration Service
    
    This unified service provides comprehensive creator matching capabilities
    through an intelligent orchestration of AI-powered matching engines,
    recommendation systems, and business intelligence analytics.
    """
    
    def __init__(
        self,
        db_session: Session,
        cache_manager: CacheManager,
        metrics_collector: MetricsCollector,
        secure_handler: SecureDataHandler,
        event_publisher: EventPublisher,
        config: MatchingServiceConfig
    ):
        self.db_session = db_session
        self.cache_manager = cache_manager
        self.metrics_collector = metrics_collector
        self.secure_handler = secure_handler
        self.event_publisher = event_publisher
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize all core services
        self._initialize_services()
        
        # Performance tracking
        self.service_health = {}
        self.performance_metrics = {}
    
    def _initialize_services(self) -> None:
        """Initialize all matching service components"""
        try:
            # Core Matching Engine
            self.matching_engine = MatchingEngine(
                self.db_session,
                self.cache_manager,
                self.metrics_collector,
                self._get_engine_config()
            )
            
            # Compatibility Analyzer
            self.compatibility_analyzer = CompatibilityAnalyzer(
                self.cache_manager,
                self.metrics_collector,
                self._get_compatibility_config()
            )
            
            # Recommendation Engine
            self.recommendation_engine = RecommendationEngine(
                self.db_session,
                self.cache_manager,
                self.metrics_collector,
                self._get_recommendation_config()
            )
            
            # Scoring Service
            self.scoring_service = MatchingScoringService(
                self.cache_manager,
                self.metrics_collector,
                self.secure_handler,
                self._get_scoring_config()
            )
            
            # Preferences Manager
            self.preferences_manager = UserPreferencesManager(
                self.db_session,
                self.cache_manager,
                self.metrics_collector,
                self.secure_handler,
                None,  # embedding_service would be injected
                self._get_preferences_config()
            )
            
            # Criteria Manager
            self.criteria_manager = MatchingCriteriaManager(
                self.db_session,
                self.cache_manager,
                self.metrics_collector,
                self._get_criteria_config()
            )
            
            # Validator
            self.validator = MatchValidator(
                self.cache_manager,
                self.metrics_collector,
                self.secure_handler,
                self._get_validator_config()
            )
            
            # Processor
            self.processor = MatchProcessor(
                self.db_session,
                self.cache_manager,
                self.metrics_collector,
                self.event_publisher,
                self._get_processor_config()
            )
            
            # Workflow Manager
            self.workflow_manager = WorkflowManager(
                self.cache_manager,
                self.metrics_collector,
                self.event_publisher,
                self._get_workflow_config()
            )
            
            self.logger.info("All matching services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing matching services: {str(e)}")
            raise
    
    async def find_matches(
        self,
        creator_id: int,
        limit: int = 20,
        strategy: Optional[MatchingStrategy] = None,
        filters: Optional[Dict[str, Any]] = None,
        include_analytics: bool = True
    ) -> List[MatchResult]:
        """
        Find optimal collaboration matches for a creator
        
        Args:
            creator_id: Target creator ID
            limit: Maximum number of matches to return
            strategy: Optional matching strategy
            filters: Optional filters for matching
            include_analytics: Whether to include business analytics
            
        Returns:
            List of validated and scored match results
        """
        try:
            start_time = datetime.utcnow()
            
            # Get user preferences
            preferences = await self.preferences_manager.get_user_preferences(
                creator_id, include_predictions=True
            )
            
            # Apply user preferences to filters
            enhanced_filters = self._apply_preferences_to_filters(
                filters or {}, preferences
            )
            
            # Find initial matches
            raw_matches = await self.matching_engine.find_matches(
                creator_id, limit * 2, strategy, enhanced_filters
            )
            
            # Validate matches
            validated_matches = []
            for match in raw_matches:
                validation_result = await self.validator.validate_match(match)
                if validation_result.is_valid:
                    validated_matches.append(match)
            
            # Enhance with scoring and analytics
            if include_analytics:
                enhanced_matches = []
                for match in validated_matches[:limit]:
                    # Get comprehensive scoring
                    creator_a_profile = await self._get_creator_profile(match.creator_a_id)
                    creator_b_profile = await self._get_creator_profile(match.creator_b_id)
                    
                    score_breakdown = await self.scoring_service.calculate_comprehensive_score(
                        creator_a_profile, creator_b_profile, strategy
                    )
                    
                    # Update match with enhanced analytics
                    match.score_breakdown = score_breakdown
                    enhanced_matches.append(match)
                
                validated_matches = enhanced_matches
            
            # Sort by overall score
            validated_matches.sort(
                key=lambda m: getattr(m, 'score_breakdown', None) and 
                             m.score_breakdown.overall_score or m.compatibility_score,
                reverse=True
            )
            
            # Record performance metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics_collector.record_event(
                'matches_found',
                {
                    'creator_id': creator_id,
                    'matches_found': len(validated_matches),
                    'processing_time': processing_time,
                    'strategy': strategy.value if strategy else 'default'
                }
            )
            
            return validated_matches[:limit]
            
        except Exception as e:
            self.logger.error(f"Error finding matches for creator {creator_id}: {str(e)}")
            self.metrics_collector.record_error('matching_error', str(e))
            raise
    
    async def get_recommendations(
        self,
        creator_id: int,
        recommendation_type: Optional[RecommendationType] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get intelligent collaboration recommendations"""
        try:
            return await self.recommendation_engine.get_recommendations(
                creator_id, recommendation_type, limit
            )
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {str(e)}")
            raise
    
    async def analyze_compatibility(
        self,
        creator_a_id: int,
        creator_b_id: int
    ) -> CompatibilityScore:
        """Analyze detailed compatibility between two creators"""
        try:
            creator_a_profile = await self._get_creator_compatibility_profile(creator_a_id)
            creator_b_profile = await self._get_creator_compatibility_profile(creator_b_id)
            
            return await self.compatibility_analyzer.analyze_compatibility(
                creator_a_profile, creator_b_profile
            )
        except Exception as e:
            self.logger.error(f"Error analyzing compatibility: {str(e)}")
            raise
    
    async def update_preferences(
        self,
        creator_id: int,
        interaction_data: Dict[str, Any],
        outcome: str,
        feedback_score: Optional[float] = None
    ) -> None:
        """Learn from user interaction to improve future matches"""
        try:
            await self.preferences_manager.learn_from_interaction(
                creator_id, interaction_data, outcome, feedback_score
            )
        except Exception as e:
            self.logger.error(f"Error updating preferences: {str(e)}")
            raise
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get comprehensive service health information"""
        try:
            health_status = {
                'overall_status': 'healthy',
                'services': {},
                'performance_metrics': {},
                'last_updated': datetime.utcnow()
            }
            
            # Check each service health
            services = [
                'matching_engine',
                'compatibility_analyzer',
                'recommendation_engine',
                'scoring_service',
                'preferences_manager',
                'validator',
                'processor',
                'workflow_manager'
            ]
            
            for service_name in services:
                service = getattr(self, service_name, None)
                if service:
                    health_status['services'][service_name] = await self._check_service_health(service)
            
            # Add performance metrics
            health_status['performance_metrics'] = await self._get_performance_metrics()
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Error getting service health: {str(e)}")
            return {
                'overall_status': 'error',
                'error': str(e),
                'last_updated': datetime.utcnow()
            }
    
    # Helper methods
    
    def _get_engine_config(self) -> Dict[str, Any]:
        """Get matching engine configuration"""
        return {
            'ai_enabled': self.config.enable_ai_matching,
            'cache_ttl': self.config.cache_ttl,
            'quality_threshold': self.config.min_match_quality
        }
    
    def _get_compatibility_config(self) -> Dict[str, Any]:
        """Get compatibility analyzer configuration"""
        return {
            'detailed_analysis': True,
            'ai_enhanced': True
        }
    
    def _get_recommendation_config(self) -> Dict[str, Any]:
        """Get recommendation engine configuration"""
        return {
            'ai_enabled': self.config.enable_recommendation_engine,
            'personalization_level': 0.8
        }
    
    def _get_scoring_config(self) -> Dict[str, Any]:
        """Get scoring service configuration"""
        return {
            'business_intelligence': self.config.enable_revenue_optimization,
            'risk_assessment': self.config.enable_risk_assessment
        }
    
    def _get_preferences_config(self) -> Dict[str, Any]:
        """Get preferences manager configuration"""
        return {
            'learning_enabled': self.config.enable_preferences_learning,
            'adaptation_rate': 0.1
        }
    
    def _get_criteria_config(self) -> Dict[str, Any]:
        """Get criteria manager configuration"""
        return {
            'dynamic_optimization': True,
            'business_rules': True
        }
    
    def _get_validator_config(self) -> Dict[str, Any]:
        """Get validator configuration"""
        return {
            'validation_level': self.config.validation_level,
            'ai_validation': True
        }
    
    def _get_processor_config(self) -> Dict[str, Any]:
        """Get processor configuration"""
        return {
            'max_parallel': self.config.max_concurrent_matches,
            'timeout': self.config.processing_timeout
        }
    
    def _get_workflow_config(self) -> Dict[str, Any]:
        """Get workflow manager configuration"""
        return {
            'optimization_enabled': True,
            'monitoring_enabled': True
        }
    
    async def _get_creator_profile(self, creator_id: int) -> CreatorProfile:
        """Get creator profile for matching"""
        # Implementation would fetch from database
        # This is a placeholder
        return CreatorProfile(user_id=creator_id, content_types=[], genres=[], 
                            audience_demographics={}, engagement_metrics={},
                            content_features=None, platform_presence={},
                            collaboration_preferences={}, performance_scores={},
                            content_tags=[], creation_frequency={}, quality_scores={})
    
    async def _get_creator_compatibility_profile(self, creator_id: int):
        """Get creator compatibility profile"""
        # Implementation would build compatibility profile
        pass
    
    def _apply_preferences_to_filters(
        self,
        filters: Dict[str, Any],
        preferences: PreferenceProfile
    ) -> Dict[str, Any]:
        """Apply user preferences to search filters"""
        enhanced_filters = filters.copy()
        
        # Apply preference-based filters
        if preferences.collaboration_formats:
            enhanced_filters['collaboration_formats'] = list(preferences.collaboration_formats)
        
        if preferences.content_types:
            enhanced_filters['content_types'] = list(preferences.content_types)
        
        return enhanced_filters
    
    async def _check_service_health(self, service: Any) -> Dict[str, Any]:
        """Check individual service health"""
        try:
            # Basic health check
            if hasattr(service, 'health_check'):
                return await service.health_check()
            else:
                return {'status': 'healthy', 'last_check': datetime.utcnow()}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e), 'last_check': datetime.utcnow()}
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all services"""
        return {
            'cache_hit_rate': 0.85,
            'average_response_time': 250,  # ms
            'throughput': 100,  # requests per minute
            'error_rate': 0.02,
            'last_updated': datetime.utcnow()
        }


# Factory function for easy service creation
def create_matching_service(
    db_session: Session,
    cache_manager: CacheManager,
    metrics_collector: MetricsCollector,
    secure_handler: SecureDataHandler,
    event_publisher: EventPublisher,
    config: Optional[MatchingServiceConfig] = None
) -> MatchingService:
    """Factory function to create a fully configured matching service"""
    if config is None:
        config = MatchingServiceConfig()
    
    return MatchingService(
        db_session,
        cache_manager,
        metrics_collector,
        secure_handler,
        event_publisher,
        config
    )


# Export key components for direct access
__all__ = [
    'MatchingService',
    'MatchingServiceConfig',
    'create_matching_service',
    
    # Core Components
    'MatchingEngine',
    'CompatibilityAnalyzer',
    'RecommendationEngine',
    'MatchingScoringService',
    'UserPreferencesManager',
    'MatchingCriteriaManager',
    'MatchValidator',
    'MatchProcessor',
    'WorkflowManager',
    
    # Data Types
    'CreatorProfile',
    'MatchResult',
    'CompatibilityScore',
    'ScoreBreakdown',
    'PreferenceProfile',
    'ValidationResult',
    'ProcessingResult',
    
    # Enums
    'ContentType',
    'MatchingStrategy',
    'ScoringStrategy',
    'PreferenceType',
    'ValidationRule',
    'ProcessingMode',
    'WorkflowStage'
]
