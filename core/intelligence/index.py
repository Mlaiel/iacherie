"""
🎯 Intelligence Index - IA Influencer Agent
==========================================

Main entry point and orchestrator for the Intelligence Core Module.
Provides unified access to all AI intelligence capabilities and manages
the coordination between different intelligence engines.

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE PROHIBITED
====================================================
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright © 2025 Fahed Mlaiel - All rights reserved
WARNING: Any unauthorized copying, modification, distribution or use of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Core Intelligence Engines
from .content_recommendation import ContentRecommendationEngine, PersonalizationEngine
from .monetization_intelligence import MonetizationIntelligence, RevenueOptimizer
from .collaboration_matcher import CollaborationMatcher, CreatorMatchingEngine
from .trend_analyzer import TrendAnalyzer, ViralPredictionEngine, MarketIntelligence
from .sentiment_analyzer import SentimentAnalyzer, AudienceInsightEngine
from .performance_predictor import PerformancePredictor, SuccessMetricsEngine

# Core Dependencies
from ..cache.redis_cache import RedisCache
from ..storage.intelligence_storage import IntelligenceStorage
from ..analytics.performance_analytics import PerformanceAnalytics
from ..config.intelligence_config import IntelligenceConfig


@dataclass
class IntelligenceRequest:
    """Intelligence processing request"""
    request_id: str
    creator_id: str
    content_data: Dict[str, Any]
    intelligence_types: List[str]
    priority: str = "normal"  # low, normal, high, critical
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntelligenceResponse:
    """Intelligence processing response"""
    request_id: str
    creator_id: str
    processing_time: float
    results: Dict[str, Any]
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class IntelligenceMetrics:
    """Intelligence system metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_processing_time: float = 0.0
    peak_requests_per_minute: int = 0
    active_engines: Dict[str, bool] = field(default_factory=dict)
    system_health: str = "healthy"
    last_updated: datetime = field(default_factory=datetime.now)


class IntelligenceOrchestrator:
    """
    Central orchestrator for all AI intelligence capabilities
    
    Manages and coordinates all intelligence engines to provide
    comprehensive AI-powered insights and recommendations for creators.
    
    Features:
    - Unified intelligence processing pipeline
    - Multi-engine coordination and optimization
    - Real-time performance monitoring
    - Intelligent caching and optimization
    - Error handling and fallback mechanisms
    - Scalable concurrent processing
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize intelligence orchestrator"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.cache = RedisCache(config.get('redis', {}))
        self.storage = IntelligenceStorage(config.get('storage', {}))
        self.analytics = PerformanceAnalytics(config.get('analytics', {}))
        
        # Initialize intelligence engines
        self.engines = {}
        self.engine_configs = config.get('engines', {})
        
        # System metrics
        self.metrics = IntelligenceMetrics()
        self.request_queue = asyncio.Queue()
        self.processing_pool = ThreadPoolExecutor(
            max_workers=config.get('max_workers', 10)
        )
        
        # Performance settings
        self.max_concurrent_requests = config.get('max_concurrent_requests', 50)
        self.request_timeout = config.get('request_timeout', 300)  # 5 minutes
        self.cache_ttl = config.get('cache_ttl', 3600)  # 1 hour
        
        self._initialize_engines()
        self._start_monitoring()
    
    def _initialize_engines(self):
        """Initialize all intelligence engines"""
        try:
            self.logger.info("Initializing intelligence engines...")
            
            # Content Recommendation Engine
            recommendation_config = self.engine_configs.get('content_recommendation', {})
            self.engines['content_recommendation'] = ContentRecommendationEngine(recommendation_config)
            self.engines['personalization'] = PersonalizationEngine(recommendation_config)
            
            # Monetization Intelligence
            monetization_config = self.engine_configs.get('monetization', {})
            self.engines['monetization_intelligence'] = MonetizationIntelligence(monetization_config)
            self.engines['revenue_optimizer'] = RevenueOptimizer(monetization_config)
            
            # Collaboration Matcher
            collaboration_config = self.engine_configs.get('collaboration', {})
            self.engines['collaboration_matcher'] = CollaborationMatcher(collaboration_config)
            self.engines['creator_matching'] = CreatorMatchingEngine(collaboration_config)
            
            # Trend Analyzer
            trend_config = self.engine_configs.get('trend_analysis', {})
            self.engines['trend_analyzer'] = TrendAnalyzer(trend_config)
            self.engines['viral_prediction'] = ViralPredictionEngine(trend_config)
            self.engines['market_intelligence'] = MarketIntelligence(trend_config)
            
            # Sentiment Analyzer
            sentiment_config = self.engine_configs.get('sentiment', {})
            self.engines['sentiment_analyzer'] = SentimentAnalyzer(sentiment_config)
            self.engines['audience_insights'] = AudienceInsightEngine(sentiment_config)
            
            # Performance Predictor
            performance_config = self.engine_configs.get('performance', {})
            self.engines['performance_predictor'] = PerformancePredictor(performance_config)
            self.engines['success_metrics'] = SuccessMetricsEngine(performance_config)
            
            # Update metrics
            self.metrics.active_engines = {
                name: True for name in self.engines.keys()
            }
            
            self.logger.info(f"Successfully initialized {len(self.engines)} intelligence engines")
            
        except Exception as e:
            self.logger.error(f"Error initializing intelligence engines: {e}")
            raise
    
    def _start_monitoring(self):
        """Start system monitoring"""
        asyncio.create_task(self._monitor_system_health())
        asyncio.create_task(self._process_request_queue())
    
    async def _monitor_system_health(self):
        """Monitor system health and performance"""
        while True:
            try:
                # Update system metrics
                await self._update_system_metrics()
                
                # Check engine health
                await self._check_engine_health()
                
                # Clean up cache if needed
                await self._cleanup_cache()
                
                # Sleep for monitoring interval
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in system monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def process_intelligence_request(
        self,
        creator_id: str,
        content_data: Dict[str, Any],
        intelligence_types: List[str] = None,
        priority: str = "normal"
    ) -> IntelligenceResponse:
        """
        Process comprehensive intelligence request
        
        Args:
            creator_id: ID of the content creator
            content_data: Content metadata and features
            intelligence_types: Specific intelligence types to process
            priority: Request priority level
            
        Returns:
            Complete intelligence analysis results
        """
        start_time = time.time()
        request_id = self._generate_request_id()
        
        try:
            self.logger.info(f"Processing intelligence request {request_id} for creator {creator_id}")
            
            # Default intelligence types
            if not intelligence_types:
                intelligence_types = [
                    'content_recommendation',
                    'monetization_analysis',
                    'collaboration_matching',
                    'trend_analysis',
                    'sentiment_analysis',
                    'performance_prediction'
                ]
            
            # Create request
            request = IntelligenceRequest(
                request_id=request_id,
                creator_id=creator_id,
                content_data=content_data,
                intelligence_types=intelligence_types,
                priority=priority
            )
            
            # Check cache first
            cache_key = f"intelligence:{creator_id}:{hashlib.md5(str(content_data).encode()).hexdigest()}"
            cached_result = await self.cache.get(cache_key)
            
            if cached_result and self._is_cache_valid(cached_result):
                self.logger.info(f"Returning cached result for request {request_id}")
                cached_result['request_id'] = request_id
                return IntelligenceResponse(**cached_result)
            
            # Process intelligence request
            results = await self._process_intelligence_request(request)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create response
            response = IntelligenceResponse(
                request_id=request_id,
                creator_id=creator_id,
                processing_time=processing_time,
                results=results,
                success=True
            )
            
            # Cache results
            await self.cache.set(cache_key, response.__dict__, ttl=self.cache_ttl)
            
            # Update metrics
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.metrics.average_processing_time = (
                (self.metrics.average_processing_time * (self.metrics.total_requests - 1) + processing_time) /
                self.metrics.total_requests
            )
            
            # Store results
            await self.storage.store_intelligence_results(response)
            
            self.logger.info(f"Successfully processed request {request_id} in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Error processing intelligence request {request_id}: {e}")
            
            # Update error metrics
            self.metrics.total_requests += 1
            self.metrics.failed_requests += 1
            
            return IntelligenceResponse(
                request_id=request_id,
                creator_id=creator_id,
                processing_time=processing_time,
                results={},
                success=False,
                errors=[str(e)]
            )
    
    async def _process_intelligence_request(self, request: IntelligenceRequest) -> Dict[str, Any]:
        """Process intelligence request using multiple engines"""
        results = {}
        tasks = []
        
        try:
            # Create tasks for each intelligence type
            for intelligence_type in request.intelligence_types:
                task = self._create_intelligence_task(intelligence_type, request)
                if task:
                    tasks.append(task)
            
            # Process tasks concurrently
            if tasks:
                completed_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Collect results
                for i, result in enumerate(completed_results):
                    intelligence_type = request.intelligence_types[i]
                    
                    if isinstance(result, Exception):
                        self.logger.error(f"Error in {intelligence_type}: {result}")
                        results[intelligence_type] = {
                            'error': str(result),
                            'success': False
                        }
                    else:
                        results[intelligence_type] = result
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing intelligence request: {e}")
            return {'error': str(e)}
    
    async def _create_intelligence_task(self, intelligence_type: str, request: IntelligenceRequest):
        """Create intelligence processing task"""
        try:
            if intelligence_type == 'content_recommendation':
                return await self._process_content_recommendation(request)
            elif intelligence_type == 'monetization_analysis':
                return await self._process_monetization_analysis(request)
            elif intelligence_type == 'collaboration_matching':
                return await self._process_collaboration_matching(request)
            elif intelligence_type == 'trend_analysis':
                return await self._process_trend_analysis(request)
            elif intelligence_type == 'sentiment_analysis':
                return await self._process_sentiment_analysis(request)
            elif intelligence_type == 'performance_prediction':
                return await self._process_performance_prediction(request)
            else:
                self.logger.warning(f"Unknown intelligence type: {intelligence_type}")
                return None
        except Exception as e:
            self.logger.error(f"Error creating task for {intelligence_type}: {e}")
            return None
    
    async def _process_content_recommendation(self, request: IntelligenceRequest) -> Dict[str, Any]:
        """Process content recommendation request"""
        try:
            engine = self.engines.get('content_recommendation')
            if not engine:
                raise ValueError("Content recommendation engine not available")
            
            # Get personalized recommendations
            recommendations = await engine.get_personalized_recommendations(
                creator_id=request.creator_id,
                content_preferences=request.content_data.get('preferences', {}),
                performance_history=request.content_data.get('performance_history', {}),
                target_audience=request.content_data.get('target_audience', 'general')
            )
            
            # Get content optimization suggestions
            optimization = await engine.optimize_content_strategy(
                creator_id=request.creator_id,
                current_content=request.content_data,
                performance_goals=request.content_data.get('goals', {})
            )
            
            return {
                'recommendations': recommendations,
                'optimization': optimization,
                'success': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in content recommendation: {e}")
            return {'error': str(e), 'success': False}
    
    async def _process_monetization_analysis(self, request: IntelligenceRequest) -> Dict[str, Any]:
        """Process monetization analysis request"""
        try:
            engine = self.engines.get('monetization_intelligence')
            if not engine:
                raise ValueError("Monetization intelligence engine not available")
            
            # Analyze monetization opportunities
            opportunities = await engine.analyze_monetization_opportunities(
                creator_id=request.creator_id,
                content_data=request.content_data,
                audience_data=request.content_data.get('audience_data', {}),
                platform_data=request.content_data.get('platform_data', {})
            )
            
            # Get revenue optimization recommendations
            revenue_optimizer = self.engines.get('revenue_optimizer')
            if revenue_optimizer:
                optimization = await revenue_optimizer.optimize_revenue_strategy(
                    creator_profile=request.content_data.get('creator_profile', {}),
                    content_portfolio=request.content_data.get('content_portfolio', {}),
                    market_conditions=request.content_data.get('market_conditions', {})
                )
            else:
                optimization = {}
            
            return {
                'opportunities': opportunities,
                'revenue_optimization': optimization,
                'success': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in monetization analysis: {e}")
            return {'error': str(e), 'success': False}
    
    async def _process_collaboration_matching(self, request: IntelligenceRequest) -> Dict[str, Any]:
        """Process collaboration matching request"""
        try:
            engine = self.engines.get('collaboration_matcher')
            if not engine:
                raise ValueError("Collaboration matcher engine not available")
            
            # Find collaboration opportunities
            collaborations = await engine.find_collaboration_opportunities(
                creator_id=request.creator_id,
                creator_profile=request.content_data.get('creator_profile', {}),
                content_style=request.content_data.get('content_style', {}),
                audience_data=request.content_data.get('audience_data', {}),
                collaboration_preferences=request.content_data.get('collaboration_preferences', {})
            )
            
            return {
                'collaborations': collaborations,
                'success': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in collaboration matching: {e}")
            return {'error': str(e), 'success': False}
    
    async def _process_trend_analysis(self, request: IntelligenceRequest) -> Dict[str, Any]:
        """Process trend analysis request"""
        try:
            engine = self.engines.get('trend_analyzer')
            viral_engine = self.engines.get('viral_prediction')
            market_engine = self.engines.get('market_intelligence')
            
            if not engine:
                raise ValueError("Trend analyzer engine not available")
            
            # Analyze current trends
            trends = await engine.analyze_current_trends(
                platforms=request.content_data.get('platforms', ['instagram', 'tiktok']),
                content_categories=request.content_data.get('categories', []),
                geographic_region=request.content_data.get('region', 'global')
            )
            
            # Predict viral potential
            viral_prediction = {}
            if viral_engine and 'content_metadata' in request.content_data:
                viral_prediction = await viral_engine.predict_viral_potential(
                    content_data=request.content_data['content_metadata'],
                    creator_profile=request.content_data.get('creator_profile', {}),
                    trend_context=trends
                )
            
            # Market intelligence
            market_insights = {}
            if market_engine:
                market_insights = await market_engine.analyze_market_opportunities(
                    creator_niche=request.content_data.get('niche', 'general'),
                    target_demographics=request.content_data.get('demographics', {}),
                    competitive_landscape=request.content_data.get('competitors', [])
                )
            
            return {
                'trends': trends,
                'viral_prediction': viral_prediction,
                'market_insights': market_insights,
                'success': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in trend analysis: {e}")
            return {'error': str(e), 'success': False}
    
    async def _process_sentiment_analysis(self, request: IntelligenceRequest) -> Dict[str, Any]:
        """Process sentiment analysis request"""
        try:
            engine = self.engines.get('sentiment_analyzer')
            insights_engine = self.engines.get('audience_insights')
            
            if not engine:
                raise ValueError("Sentiment analyzer engine not available")
            
            # Analyze content sentiment
            content_sentiment = {}
            if 'content_text' in request.content_data:
                content_sentiment = await engine.analyze_content_sentiment(
                    content_text=request.content_data['content_text'],
                    content_metadata=request.content_data.get('content_metadata', {})
                )
            
            # Analyze audience sentiment
            audience_sentiment = {}
            if 'audience_feedback' in request.content_data:
                audience_sentiment = await engine.analyze_audience_sentiment(
                    feedback_data=request.content_data['audience_feedback'],
                    creator_id=request.creator_id
                )
            
            # Generate audience insights
            audience_insights = {}
            if insights_engine:
                audience_insights = await insights_engine.generate_audience_insights(
                    creator_id=request.creator_id,
                    sentiment_data={'content': content_sentiment, 'audience': audience_sentiment},
                    engagement_data=request.content_data.get('engagement_data', {})
                )
            
            return {
                'content_sentiment': content_sentiment,
                'audience_sentiment': audience_sentiment,
                'audience_insights': audience_insights,
                'success': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {e}")
            return {'error': str(e), 'success': False}
    
    async def _process_performance_prediction(self, request: IntelligenceRequest) -> Dict[str, Any]:
        """Process performance prediction request"""
        try:
            engine = self.engines.get('performance_predictor')
            metrics_engine = self.engines.get('success_metrics')
            
            if not engine:
                raise ValueError("Performance predictor engine not available")
            
            # Predict content performance
            performance_prediction = await engine.predict_content_performance(
                content_data=request.content_data.get('content_metadata', {}),
                creator_profile=request.content_data.get('creator_profile', {})
            )
            
            # Analyze success metrics
            success_metrics = {}
            if metrics_engine:
                success_metrics = await metrics_engine.analyze_success_metrics(
                    creator_id=request.creator_id,
                    timeframe=request.content_data.get('timeframe', '30d'),
                    benchmark_group=request.content_data.get('benchmark_group', 'similar_creators')
                )
            
            return {
                'performance_prediction': performance_prediction,
                'success_metrics': success_metrics,
                'success': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in performance prediction: {e}")
            return {'error': str(e), 'success': False}
    
    async def get_intelligence_summary(self, creator_id: str, timeframe: str = "7d") -> Dict[str, Any]:
        """Get comprehensive intelligence summary for creator"""
        try:
            # Get recent intelligence results
            recent_results = await self.storage.get_recent_intelligence_results(
                creator_id=creator_id,
                timeframe=timeframe
            )
            
            # Aggregate insights
            summary = {
                'creator_id': creator_id,
                'timeframe': timeframe,
                'total_analyses': len(recent_results),
                'key_insights': [],
                'recommendations': [],
                'performance_trends': {},
                'monetization_opportunities': [],
                'collaboration_matches': [],
                'trend_alignment': {},
                'audience_sentiment_trend': {},
                'generated_at': datetime.now().isoformat()
            }
            
            # Process recent results
            for result in recent_results:
                if result.success and result.results:
                    # Extract key insights from each analysis type
                    self._extract_summary_insights(result.results, summary)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating intelligence summary: {e}")
            return {'error': str(e), 'creator_id': creator_id}
    
    def _extract_summary_insights(self, results: Dict[str, Any], summary: Dict[str, Any]):
        """Extract key insights from intelligence results"""
        # Content recommendations
        if 'content_recommendation' in results:
            rec_data = results['content_recommendation']
            if 'recommendations' in rec_data:
                summary['recommendations'].extend(rec_data['recommendations'][:3])
        
        # Monetization insights
        if 'monetization_analysis' in results:
            mon_data = results['monetization_analysis']
            if 'opportunities' in mon_data:
                summary['monetization_opportunities'].extend(mon_data['opportunities'][:3])
        
        # Collaboration matches
        if 'collaboration_matching' in results:
            col_data = results['collaboration_matching']
            if 'collaborations' in col_data:
                summary['collaboration_matches'].extend(col_data['collaborations'][:3])
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and health metrics"""
        return {
            'status': 'operational' if self.metrics.system_health == 'healthy' else 'degraded',
            'metrics': self.metrics.__dict__,
            'engines': {
                name: 'active' if active else 'inactive' 
                for name, active in self.metrics.active_engines.items()
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return f"intel_{int(time.time())}_{hashlib.md5(str(hash(self)).encode()).hexdigest()[:8]}"
    
    def _is_cache_valid(self, cached_data: Dict[str, Any]) -> bool:
        """Check if cached data is still valid"""
        if 'created_at' not in cached_data:
            return False
        
        created_at = datetime.fromisoformat(cached_data['created_at'])
        return datetime.now() - created_at < timedelta(seconds=self.cache_ttl)
    
    async def _update_system_metrics(self):
        """Update system performance metrics"""
        # This would update various system metrics
        self.metrics.last_updated = datetime.now()
    
    async def _check_engine_health(self):
        """Check health of all intelligence engines"""
        for engine_name in self.engines:
            try:
                # Perform health check on each engine
                # This is a placeholder - real implementation would test engine functionality
                self.metrics.active_engines[engine_name] = True
            except Exception as e:
                self.logger.error(f"Health check failed for {engine_name}: {e}")
                self.metrics.active_engines[engine_name] = False
    
    async def _cleanup_cache(self):
        """Clean up expired cache entries"""
        try:
            await self.cache.cleanup_expired()
        except Exception as e:
            self.logger.error(f"Error cleaning up cache: {e}")
    
    async def _process_request_queue(self):
        """Process requests from the queue"""
        while True:
            try:
                # This would process queued requests
                await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Error processing request queue: {e}")


# Global intelligence orchestrator instance
_orchestrator = None

def get_intelligence_orchestrator(config: Dict[str, Any] = None) -> IntelligenceOrchestrator:
    """Get or create intelligence orchestrator instance"""
    global _orchestrator
    
    if _orchestrator is None:
        if config is None:
            config = IntelligenceConfig.get_default_config()
        _orchestrator = IntelligenceOrchestrator(config)
    
    return _orchestrator


# Main entry point functions
async def process_intelligence(
    creator_id: str,
    content_data: Dict[str, Any],
    intelligence_types: List[str] = None,
    priority: str = "normal"
) -> IntelligenceResponse:
    """
    Main entry point for intelligence processing
    
    Args:
        creator_id: ID of the content creator
        content_data: Content metadata and features
        intelligence_types: Specific intelligence types to process
        priority: Request priority level
        
    Returns:
        Complete intelligence analysis results
    """
    orchestrator = get_intelligence_orchestrator()
    return await orchestrator.process_intelligence_request(
        creator_id=creator_id,
        content_data=content_data,
        intelligence_types=intelligence_types,
        priority=priority
    )


async def get_creator_intelligence_summary(creator_id: str, timeframe: str = "7d") -> Dict[str, Any]:
    """
    Get comprehensive intelligence summary for a creator
    
    Args:
        creator_id: ID of the content creator
        timeframe: Analysis timeframe (e.g., "7d", "30d")
        
    Returns:
        Comprehensive intelligence summary
    """
    orchestrator = get_intelligence_orchestrator()
    return await orchestrator.get_intelligence_summary(creator_id, timeframe)


async def get_system_health() -> Dict[str, Any]:
    """
    Get current system health and status
    
    Returns:
        System health metrics and status
    """
    orchestrator = get_intelligence_orchestrator()
    return await orchestrator.get_system_status()


# CLI interface for testing and administration
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="IA Influencer Agent Intelligence System")
    parser.add_argument("--test", action="store_true", help="Run system tests")
    parser.add_argument("--health", action="store_true", help="Check system health")
    parser.add_argument("--creator-id", help="Creator ID for testing")
    
    args = parser.parse_args()
    
    async def main():
        if args.health:
            status = await get_system_health()
            print(json.dumps(status, indent=2))
        
        elif args.test and args.creator_id:
            test_content = {
                'content_type': 'video',
                'title': 'Test Content',
                'description': 'Test description for intelligence processing',
                'creator_profile': {
                    'follower_count': 10000,
                    'engagement_rate': 0.05
                }
            }
            
            result = await process_intelligence(
                creator_id=args.creator_id,
                content_data=test_content
            )
            
            print(json.dumps(result.__dict__, indent=2, default=str))
        
        else:
            print("IA Influencer Agent Intelligence System is running...")
            print("Use --health to check system status or --test with --creator-id to run tests")
    
    asyncio.run(main())
