"""Recommendation Agent Index - Ultra-Advanced AI Personalization System Entry Point

This module provides the main entry point and orchestration layer for the 
enterprise-grade recommendation system within the IA Influencer platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Core Capabilities:
- Multi-strategy recommendation generation and optimization
- Real-time personalization with continuous learning
- Enterprise-grade performance monitoring and analytics
- Cross-platform content discovery and creator collaboration
- Advanced monetization intelligence and trend analysis
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
import json

from .recommendation_agent import (
    RecommendationAgent,
    RecommendationAgentManager,
    RecommendationLoadBalancer,
    RecommendationPerformanceMonitor,
    RecommendationExplainer,
    RecommendationPrivacyManager,
    RecommendationType,
    RecommendationStrategy,
    PersonalizationLevel,
    RecommendationItem,
    RecommendationSet
)

from .config import (
    get_config,
    validate_config,
    get_environment_config,
    DEVELOPMENT_CONFIG,
    PRODUCTION_CONFIG,
    ENTERPRISE_CONFIG
)

from ..base import AgentRequest, AgentResponse

logger = logging.getLogger(__name__)

class RecommendationSystemOrchestrator:
    """
    Main orchestrator for the recommendation system providing high-level
    coordination of all recommendation components and services.
    """
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.config = get_config(environment)
        self.agent_manager = RecommendationAgentManager()
        self.load_balancer = RecommendationLoadBalancer()
        self.performance_monitor = RecommendationPerformanceMonitor()
        self.explainer = RecommendationExplainer()
        self.privacy_manager = RecommendationPrivacyManager()
        
        self.active_agents: Dict[str, RecommendationAgent] = {}
        self.system_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'active_users': 0,
            'recommendations_generated': 0
        }
        
        self._initialized = False
        logger.info(f"RecommendationSystemOrchestrator initialized for {environment}")
    
    async def initialize(self) -> bool:
        """
        Initialize the recommendation system orchestrator
        
        Returns:
            True if initialization successful
        """
        try:
            # Validate configuration
            validate_config(self.config)
            
            # Initialize core agent manager
            await self.agent_manager.initialize()
            
            # Initialize performance monitoring
            await self.performance_monitor.initialize()
            
            # Create default recommendation agents
            await self._create_default_agents()
            
            # Setup monitoring and health checks
            await self._setup_monitoring()
            
            self._initialized = True
            logger.info("Recommendation system orchestrator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize recommendation system: {e}")
            return False
    
    async def _create_default_agents(self):
        """Create default recommendation agents based on configuration"""
        
        default_agents = [
            {
                'agent_id': 'content_discovery_agent',
                'specialization': RecommendationType.CONTENT_DISCOVERY,
                'strategy': RecommendationStrategy.HYBRID
            },
            {
                'agent_id': 'collaboration_agent', 
                'specialization': RecommendationType.CREATOR_MATCHING,
                'strategy': RecommendationStrategy.GRAPH_BASED
            },
            {
                'agent_id': 'monetization_agent',
                'specialization': RecommendationType.MONETIZATION_OPPORTUNITIES,
                'strategy': RecommendationStrategy.DEEP_LEARNING
            },
            {
                'agent_id': 'trending_agent',
                'specialization': RecommendationType.TREND_OPPORTUNITIES,
                'strategy': RecommendationStrategy.REINFORCEMENT_LEARNING
            }
        ]
        
        for agent_config in default_agents:
            try:
                agent = await self.agent_manager.create_agent(
                    agent_config['agent_id'],
                    {
                        **self.config,
                        'specialization': agent_config['specialization'],
                        'default_strategy': agent_config['strategy']
                    }
                )
                self.active_agents[agent_config['agent_id']] = agent
                logger.info(f"Created agent: {agent_config['agent_id']}")
                
            except Exception as e:
                logger.error(f"Failed to create agent {agent_config['agent_id']}: {e}")
    
    async def _setup_monitoring(self):
        """Setup system monitoring and health checks"""
        
        # Register all agents for monitoring
        for agent in self.active_agents.values():
            await self.performance_monitor.register_agent(agent)
        
        # Start background monitoring tasks
        asyncio.create_task(self._periodic_health_check())
        asyncio.create_task(self._periodic_metrics_collection())
        asyncio.create_task(self._periodic_model_optimization())
        
        logger.info("Monitoring and health checks initialized")
    
    async def generate_recommendations(
        self,
        user_id: str,
        recommendation_type: Union[str, RecommendationType] = RecommendationType.CONTENT_DISCOVERY,
        count: int = 20,
        strategy: Union[str, RecommendationStrategy] = RecommendationStrategy.HYBRID,
        context: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized recommendations
        
        Args:
            user_id: User identifier
            recommendation_type: Type of recommendation to generate
            count: Number of recommendations to generate
            strategy: Recommendation strategy to use
            context: Additional context for recommendations
            agent_id: Specific agent ID to use (optional)
            
        Returns:
            Dictionary containing recommendations and metadata
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Convert string enums to proper types
            if isinstance(recommendation_type, str):
                recommendation_type = RecommendationType(recommendation_type)
            if isinstance(strategy, str):
                strategy = RecommendationStrategy(strategy)
            
            # Create request
            request = AgentRequest(
                action="generate_recommendations",
                data={
                    "user_id": user_id,
                    "type": recommendation_type,
                    "count": count,
                    "strategy": strategy,
                    "context": context or {}
                }
            )
            
            # Process request through agent manager
            response = await self.agent_manager.process_recommendation_request(
                request, agent_id
            )
            
            # Apply privacy filtering
            if response.success:
                response.data = await self.privacy_manager.filter_recommendations(
                    response.data, user_id
                )
                
                # Add explanations
                response.data = await self.explainer.add_explanations(
                    response.data, user_id, strategy
                )
            
            # Update metrics
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_request_metrics(response.success, processing_time)
            
            return self._format_api_response(response, processing_time)
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            await self._update_request_metrics(False, 0)
            return {
                'success': False,
                'error': str(e),
                'error_code': 'RECOMMENDATION_GENERATION_ERROR',
                'recommendations': [],
                'processing_time_ms': (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            }
    
    async def suggest_collaborations(
        self,
        user_id: str,
        collaboration_types: List[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Suggest collaboration opportunities
        
        Args:
            user_id: User identifier
            collaboration_types: Types of collaborations to suggest
            context: Additional context
            
        Returns:
            Dictionary containing collaboration suggestions
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            request = AgentRequest(
                action="suggest_collaborations",
                data={
                    "user_id": user_id,
                    "types": collaboration_types or ["music", "content", "cross_promotion"],
                    "context": context or {}
                }
            )
            
            response = await self.agent_manager.process_recommendation_request(
                request, "collaboration_agent"
            )
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_request_metrics(response.success, processing_time)
            
            return self._format_api_response(response, processing_time)
            
        except Exception as e:
            logger.error(f"Error suggesting collaborations: {e}")
            return {
                'success': False,
                'error': str(e),
                'collaboration_suggestions': {},
                'processing_time_ms': (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            }
    
    async def analyze_monetization_opportunities(
        self,
        user_id: str,
        financial_goals: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze monetization opportunities
        
        Args:
            user_id: User identifier
            financial_goals: User's financial objectives
            context: Additional context
            
        Returns:
            Dictionary containing monetization analysis
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            request = AgentRequest(
                action="get_monetization_recommendations",
                data={
                    "user_id": user_id,
                    "financial_goals": financial_goals or {},
                    "context": context or {}
                }
            )
            
            response = await self.agent_manager.process_recommendation_request(
                request, "monetization_agent"
            )
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_request_metrics(response.success, processing_time)
            
            return self._format_api_response(response, processing_time)
            
        except Exception as e:
            logger.error(f"Error analyzing monetization opportunities: {e}")
            return {
                'success': False,
                'error': str(e),
                'monetization_opportunities': {},
                'processing_time_ms': (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            }
    
    async def identify_trending_opportunities(
        self,
        user_id: str,
        timeframe: str = "7d",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Identify trending opportunities
        
        Args:
            user_id: User identifier
            timeframe: Time period for trend analysis
            context: Additional context
            
        Returns:
            Dictionary containing trending opportunities
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            request = AgentRequest(
                action="identify_trends",
                data={
                    "user_id": user_id,
                    "timeframe": timeframe,
                    "context": context or {}
                }
            )
            
            response = await self.agent_manager.process_recommendation_request(
                request, "trending_agent"
            )
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_request_metrics(response.success, processing_time)
            
            return self._format_api_response(response, processing_time)
            
        except Exception as e:
            logger.error(f"Error identifying trending opportunities: {e}")
            return {
                'success': False,
                'error': str(e),
                'trending_opportunities': {},
                'processing_time_ms': (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            }
    
    async def get_cross_platform_strategies(
        self,
        user_id: str,
        platforms: List[str] = None,
        performance_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get cross-platform optimization strategies
        
        Args:
            user_id: User identifier
            platforms: List of target platforms
            performance_data: Current performance data
            
        Returns:
            Dictionary containing cross-platform strategies
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            request = AgentRequest(
                action="get_cross_platform_recommendations",
                data={
                    "user_id": user_id,
                    "platforms": platforms or ["spotify", "youtube", "instagram", "tiktok"],
                    "performance_data": performance_data or {}
                }
            )
            
            # Use content discovery agent for cross-platform analysis
            response = await self.agent_manager.process_recommendation_request(
                request, "content_discovery_agent"
            )
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_request_metrics(response.success, processing_time)
            
            return self._format_api_response(response, processing_time)
            
        except Exception as e:
            logger.error(f"Error getting cross-platform strategies: {e}")
            return {
                'success': False,
                'error': str(e),
                'platform_strategies': {},
                'processing_time_ms': (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            }
    
    async def record_user_feedback(
        self,
        user_id: str,
        item_id: str,
        feedback_type: str,
        rating: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record user feedback for recommendation learning
        
        Args:
            user_id: User identifier
            item_id: Item being rated
            feedback_type: Type of feedback (like, dislike, click, skip, etc.)
            rating: Numerical rating if applicable
            context: Additional context
            
        Returns:
            Dictionary confirming feedback recording
        """
        try:
            request = AgentRequest(
                action="record_interaction",
                data={
                    "user_id": user_id,
                    "item_id": item_id,
                    "interaction_type": feedback_type,
                    "rating": rating,
                    "context": context or {}
                }
            )
            
            # Record feedback with all active agents for learning
            results = []
            for agent_id, agent in self.active_agents.items():
                try:
                    response = await agent.process(request)
                    results.append({
                        'agent_id': agent_id,
                        'success': response.success
                    })
                except Exception as e:
                    logger.error(f"Error recording feedback with agent {agent_id}: {e}")
                    results.append({
                        'agent_id': agent_id,
                        'success': False,
                        'error': str(e)
                    })
            
            return {
                'success': True,
                'message': 'Feedback recorded successfully',
                'agent_results': results
            }
            
        except Exception as e:
            logger.error(f"Error recording user feedback: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to record feedback'
            }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get comprehensive system health information
        
        Returns:
            Dictionary containing system health metrics
        """
        try:
            # Get agent manager health
            agent_health = await self.agent_manager.get_system_health()
            
            # Get performance monitoring data
            performance_data = await self.performance_monitor.get_performance_summary()
            
            # System-wide metrics
            system_status = {
                'status': 'healthy' if self._initialized else 'initializing',
                'environment': self.environment,
                'active_agents': len(self.active_agents),
                'system_metrics': self.system_metrics,
                'uptime_seconds': (datetime.now(timezone.utc) - getattr(self, '_start_time', datetime.now(timezone.utc))).total_seconds(),
                'configuration': {
                    'max_recommendations': self.config['performance']['max_recommendations'],
                    'default_strategy': 'hybrid',
                    'caching_enabled': self.config.get('caching', {}).get('recommendation_ttl', 0) > 0,
                    'ab_testing_enabled': self.config.get('ab_testing_config', {}).get('enabled', False)
                }
            }
            
            return {
                'system_status': system_status,
                'agent_health': agent_health,
                'performance_data': performance_data,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                'system_status': {
                    'status': 'error',
                    'error': str(e)
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _update_request_metrics(self, success: bool, processing_time: float):
        """Update system request metrics"""
        self.system_metrics['total_requests'] += 1
        if success:
            self.system_metrics['successful_requests'] += 1
        else:
            self.system_metrics['failed_requests'] += 1
        
        # Update average response time
        total_requests = self.system_metrics['total_requests']
        current_avg = self.system_metrics['average_response_time']
        self.system_metrics['average_response_time'] = (
            (current_avg * (total_requests - 1) + processing_time) / total_requests
        )
    
    def _format_api_response(self, response: AgentResponse, processing_time: float) -> Dict[str, Any]:
        """Format agent response for API consumption"""
        return {
            'success': response.success,
            'data': response.data if response.success else {},
            'error': response.error if not response.success else None,
            'error_code': response.error_code if not response.success else None,
            'message': response.message,
            'agent_type': response.agent_type,
            'processing_time_ms': processing_time * 1000,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'system_version': 'v2.1.0'
        }
    
    async def _periodic_health_check(self):
        """Periodic health check for all system components"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Check agent health
                unhealthy_agents = []
                for agent_id, agent in self.active_agents.items():
                    if not hasattr(agent, '_initialized') or not agent._initialized:
                        unhealthy_agents.append(agent_id)
                
                if unhealthy_agents:
                    logger.warning(f"Unhealthy agents detected: {unhealthy_agents}")
                
                # Check system resources
                await self._check_system_resources()
                
            except Exception as e:
                logger.error(f"Error in periodic health check: {e}")
    
    async def _periodic_metrics_collection(self):
        """Periodic metrics collection and reporting"""
        while True:
            try:
                await asyncio.sleep(60)  # Collect every minute
                
                # Collect performance metrics from all agents
                await self.performance_monitor.collect_metrics()
                
                # Log key metrics
                if self.system_metrics['total_requests'] > 0:
                    success_rate = (self.system_metrics['successful_requests'] / 
                                  self.system_metrics['total_requests']) * 100
                    logger.info(f"System metrics - Success rate: {success_rate:.2f}%, "
                              f"Avg response time: {self.system_metrics['average_response_time']:.3f}s")
                
            except Exception as e:
                logger.error(f"Error in periodic metrics collection: {e}")
    
    async def _periodic_model_optimization(self):
        """Periodic model optimization and retraining"""
        while True:
            try:
                await asyncio.sleep(3600)  # Optimize every hour
                
                # Trigger model optimization for all agents
                for agent_id, agent in self.active_agents.items():
                    if hasattr(agent, 'optimize_models'):
                        try:
                            await agent.optimize_models()
                            logger.info(f"Models optimized for agent: {agent_id}")
                        except Exception as e:
                            logger.error(f"Error optimizing models for agent {agent_id}: {e}")
                
            except Exception as e:
                logger.error(f"Error in periodic model optimization: {e}")
    
    async def _check_system_resources(self):
        """Check system resource usage"""
        try:
            import psutil
            
            # Check memory usage
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 85:
                logger.warning(f"High memory usage: {memory_percent}%")
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                logger.warning(f"High CPU usage: {cpu_percent}%")
                
        except ImportError:
            # psutil not available, skip resource checking
            pass
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")

# Global orchestrator instance
_orchestrator_instance: Optional[RecommendationSystemOrchestrator] = None

async def get_orchestrator(environment: str = None) -> RecommendationSystemOrchestrator:
    """
    Get or create the global orchestrator instance
    
    Args:
        environment: Environment name (development, production, enterprise)
        
    Returns:
        RecommendationSystemOrchestrator instance
    """
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        if environment is None:
            import os
            environment = os.getenv("RECOMMENDATION_ENVIRONMENT", "development")
        
        _orchestrator_instance = RecommendationSystemOrchestrator(environment)
        await _orchestrator_instance.initialize()
    
    return _orchestrator_instance

# Convenience functions for direct API usage

async def generate_recommendations(
    user_id: str,
    recommendation_type: str = "content_discovery",
    count: int = 20,
    strategy: str = "hybrid",
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate recommendations using the global orchestrator
    
    Args:
        user_id: User identifier
        recommendation_type: Type of recommendation
        count: Number of recommendations
        strategy: Recommendation strategy
        context: Additional context
        
    Returns:
        Recommendations response
    """
    orchestrator = await get_orchestrator()
    return await orchestrator.generate_recommendations(
        user_id, recommendation_type, count, strategy, context
    )

async def suggest_collaborations(
    user_id: str,
    collaboration_types: List[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Suggest collaborations using the global orchestrator
    
    Args:
        user_id: User identifier
        collaboration_types: Types of collaborations
        context: Additional context
        
    Returns:
        Collaboration suggestions response
    """
    orchestrator = await get_orchestrator()
    return await orchestrator.suggest_collaborations(user_id, collaboration_types, context)

async def analyze_monetization_opportunities(
    user_id: str,
    financial_goals: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze monetization opportunities using the global orchestrator
    
    Args:
        user_id: User identifier
        financial_goals: Financial objectives
        context: Additional context
        
    Returns:
        Monetization analysis response
    """
    orchestrator = await get_orchestrator()
    return await orchestrator.analyze_monetization_opportunities(user_id, financial_goals, context)

async def record_user_feedback(
    user_id: str,
    item_id: str,
    feedback_type: str,
    rating: Optional[float] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Record user feedback using the global orchestrator
    
    Args:
        user_id: User identifier
        item_id: Item identifier
        feedback_type: Type of feedback
        rating: Numerical rating
        context: Additional context
        
    Returns:
        Feedback recording response
    """
    orchestrator = await get_orchestrator()
    return await orchestrator.record_user_feedback(user_id, item_id, feedback_type, rating, context)

# Export all main classes and functions
__all__ = [
    'RecommendationSystemOrchestrator',
    'RecommendationAgent',
    'RecommendationAgentManager',
    'RecommendationType',
    'RecommendationStrategy',
    'PersonalizationLevel',
    'RecommendationItem',
    'RecommendationSet',
    'get_orchestrator',
    'generate_recommendations',
    'suggest_collaborations',
    'analyze_monetization_opportunities',
    'record_user_feedback',
    'get_config',
    'validate_config',
    'DEVELOPMENT_CONFIG',
    'PRODUCTION_CONFIG',
    'ENTERPRISE_CONFIG'
]
