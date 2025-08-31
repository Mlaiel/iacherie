"""Content Guidance Index - Central Business Logic Coordinator
==========================================================

This module serves as the central coordinator for all content guidance operations,
providing unified access to all content strategy, optimization, and analytics services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use prohibited and legally prosecuted.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from backend.core.logging import get_logger
from backend.core.config import get_settings

# Import all content guidance engines
from .content_optimizer import ContentOptimizer, OptimizationResult
from .platform_recommendations import PlatformRecommendationEngine, PlatformStrategy
from .monetization_guidance import MonetizationGuidanceEngine, MonetizationStrategy
from .trend_analyzer import TrendAnalyzer, TrendAnalysis
from .audience_insights import AudienceInsightsEngine, AudienceInsight
from .brand_safety import BrandSafetyEngine, SafetyAnalysis
from .collaboration_finder import CollaborationFinder, CollaborationOpportunity
from .content_scheduler import ContentScheduler, SchedulingRecommendation
from .creative_assistant import CreativeAssistant, CreativeIdea
from .performance_tracker import PerformanceTracker, PerformanceReport

logger = get_logger(__name__)
settings = get_settings()


class ContentGuidanceServiceType(Enum):
    """Types of content guidance services."""
    OPTIMIZATION = "optimization"
    PLATFORM_STRATEGY = "platform_strategy"
    MONETIZATION = "monetization"
    TREND_ANALYSIS = "trend_analysis"
    AUDIENCE_INSIGHTS = "audience_insights"
    BRAND_SAFETY = "brand_safety"
    COLLABORATION = "collaboration"
    SCHEDULING = "scheduling"
    CREATIVE_ASSISTANCE = "creative_assistance"
    PERFORMANCE_TRACKING = "performance_tracking"


@dataclass
class ContentGuidanceRequest:
    """Unified request structure for content guidance services."""
    creator_id: str
    content_id: Optional[str] = None
    content_type: Optional[str] = None
    content_url: Optional[str] = None
    content_text: Optional[str] = None
    platforms: List[str] = None
    target_audience: Optional[str] = None
    objectives: List[str] = None
    budget_range: Optional[Tuple[float, float]] = None
    timeframe: Optional[str] = None
    preferences: Dict[str, Any] = None
    metadata: Dict[str, Any] = None


@dataclass
class ContentGuidanceResponse:
    """Unified response structure for content guidance services."""
    request_id: str
    creator_id: str
    service_type: ContentGuidanceServiceType
    recommendations: List[Dict[str, Any]]
    insights: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    confidence_score: float
    processing_time: float
    next_steps: List[str]
    warnings: List[str] = None
    errors: List[str] = None
    metadata: Dict[str, Any] = None


class ContentGuidanceOrchestrator:
    """
    Central orchestrator for all content guidance services providing unified access
    to content optimization, platform strategies, monetization, analytics, and more.
    """
    
    def __init__(self):
        """Initialize the content guidance orchestrator."""
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize all service engines
        self.content_optimizer = ContentOptimizer()
        self.platform_engine = PlatformRecommendationEngine()
        self.monetization_engine = MonetizationGuidanceEngine()
        self.trend_analyzer = TrendAnalyzer()
        self.audience_engine = AudienceInsightsEngine()
        self.brand_safety_engine = BrandSafetyEngine()
        self.collaboration_finder = CollaborationFinder()
        self.content_scheduler = ContentScheduler()
        self.creative_assistant = CreativeAssistant()
        self.performance_tracker = PerformanceTracker()
        
        # Service registry
        self.services = {
            ContentGuidanceServiceType.OPTIMIZATION: self.content_optimizer,
            ContentGuidanceServiceType.PLATFORM_STRATEGY: self.platform_engine,
            ContentGuidanceServiceType.MONETIZATION: self.monetization_engine,
            ContentGuidanceServiceType.TREND_ANALYSIS: self.trend_analyzer,
            ContentGuidanceServiceType.AUDIENCE_INSIGHTS: self.audience_engine,
            ContentGuidanceServiceType.BRAND_SAFETY: self.brand_safety_engine,
            ContentGuidanceServiceType.COLLABORATION: self.collaboration_finder,
            ContentGuidanceServiceType.SCHEDULING: self.content_scheduler,
            ContentGuidanceServiceType.CREATIVE_ASSISTANCE: self.creative_assistant,
            ContentGuidanceServiceType.PERFORMANCE_TRACKING: self.performance_tracker
        }
    
    async def process_comprehensive_guidance(
        self, 
        request: ContentGuidanceRequest
    ) -> Dict[ContentGuidanceServiceType, ContentGuidanceResponse]:
        """
        Process comprehensive content guidance across all services.
        
        This is the main entry point for the complete content guidance workflow
        following the business logic: Content Input → AI Analysis → Multi-service 
        Processing → Unified Recommendations → Action Plan.
        """
        
        start_time = datetime.now()
        self.logger.info(f"Starting comprehensive guidance for creator {request.creator_id}")
        
        try:
            # Phase 1: Content Analysis & Safety Check
            safety_result = await self._analyze_content_safety(request)
            if not safety_result["is_safe"]:
                return self._create_safety_error_response(request, safety_result)
            
            # Phase 2: Parallel Processing of All Services
            guidance_tasks = {
                service_type: self._process_service_guidance(service_type, request)
                for service_type in ContentGuidanceServiceType
            }
            
            # Execute all services concurrently
            guidance_results = await asyncio.gather(
                *guidance_tasks.values(),
                return_exceptions=True
            )
            
            # Phase 3: Compile Results
            compiled_results = {}
            for service_type, result in zip(guidance_tasks.keys(), guidance_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Service {service_type} failed: {result}")
                    compiled_results[service_type] = self._create_error_response(
                        request, service_type, str(result)
                    )
                else:
                    compiled_results[service_type] = result
            
            # Phase 4: Cross-Service Optimization
            optimized_results = await self._optimize_cross_service_recommendations(
                compiled_results, request
            )
            
            # Phase 5: Generate Unified Action Plan
            action_plan = await self._generate_unified_action_plan(
                optimized_results, request
            )
            
            # Add action plan to all responses
            for response in optimized_results.values():
                response.next_steps.extend(action_plan)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"Comprehensive guidance completed for {request.creator_id} "
                f"in {processing_time:.2f} seconds"
            )
            
            return optimized_results
            
        except Exception as e:
            self.logger.error(f"Comprehensive guidance failed for {request.creator_id}: {e}")
            raise
    
    async def process_single_service_guidance(
        self,
        service_type: ContentGuidanceServiceType,
        request: ContentGuidanceRequest
    ) -> ContentGuidanceResponse:
        """Process guidance for a single service type."""
        
        start_time = datetime.now()
        self.logger.info(f"Processing {service_type.value} guidance for {request.creator_id}")
        
        try:
            # Safety check for content-related services
            if service_type in [
                ContentGuidanceServiceType.OPTIMIZATION,
                ContentGuidanceServiceType.BRAND_SAFETY,
                ContentGuidanceServiceType.CREATIVE_ASSISTANCE
            ]:
                safety_result = await self._analyze_content_safety(request)
                if not safety_result["is_safe"]:
                    return self._create_safety_error_response(request, safety_result, service_type)
            
            # Process the specific service
            result = await self._process_service_guidance(service_type, request)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            
            self.logger.info(
                f"Service {service_type.value} completed for {request.creator_id} "
                f"in {processing_time:.2f} seconds"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Service {service_type.value} failed for {request.creator_id}: {e}")
            raise
    
    async def _process_service_guidance(
        self,
        service_type: ContentGuidanceServiceType,
        request: ContentGuidanceRequest
    ) -> ContentGuidanceResponse:
        """Process guidance for a specific service type."""
        
        service = self.services[service_type]
        request_id = f"{request.creator_id}_{service_type.value}_{datetime.now().timestamp()}"
        
        try:
            if service_type == ContentGuidanceServiceType.OPTIMIZATION:
                result = await self._process_content_optimization(service, request)
            
            elif service_type == ContentGuidanceServiceType.PLATFORM_STRATEGY:
                result = await self._process_platform_recommendations(service, request)
            
            elif service_type == ContentGuidanceServiceType.MONETIZATION:
                result = await self._process_monetization_guidance(service, request)
            
            elif service_type == ContentGuidanceServiceType.TREND_ANALYSIS:
                result = await self._process_trend_analysis(service, request)
            
            elif service_type == ContentGuidanceServiceType.AUDIENCE_INSIGHTS:
                result = await self._process_audience_insights(service, request)
            
            elif service_type == ContentGuidanceServiceType.BRAND_SAFETY:
                result = await self._process_brand_safety(service, request)
            
            elif service_type == ContentGuidanceServiceType.COLLABORATION:
                result = await self._process_collaboration_finding(service, request)
            
            elif service_type == ContentGuidanceServiceType.SCHEDULING:
                result = await self._process_content_scheduling(service, request)
            
            elif service_type == ContentGuidanceServiceType.CREATIVE_ASSISTANCE:
                result = await self._process_creative_assistance(service, request)
            
            elif service_type == ContentGuidanceServiceType.PERFORMANCE_TRACKING:
                result = await self._process_performance_tracking(service, request)
            
            else:
                raise ValueError(f"Unknown service type: {service_type}")
            
            return ContentGuidanceResponse(
                request_id=request_id,
                creator_id=request.creator_id,
                service_type=service_type,
                recommendations=result.get("recommendations", []),
                insights=result.get("insights", []),
                metrics=result.get("metrics", {}),
                confidence_score=result.get("confidence_score", 0.8),
                processing_time=0.0,  # Will be set by caller
                next_steps=result.get("next_steps", []),
                warnings=result.get("warnings", []),
                errors=result.get("errors", []),
                metadata=result.get("metadata", {})
            )
            
        except Exception as e:
            self.logger.error(f"Service processing failed for {service_type.value}: {e}")
            return self._create_error_response(request, service_type, str(e))
    
    async def _process_content_optimization(
        self, 
        service: ContentOptimizer, 
        request: ContentGuidanceRequest
    ) -> Dict[str, Any]:
        """Process content optimization guidance."""
        
        # Analyze content for optimization opportunities
        if request.content_text:
            optimization_result = await service.optimize_text_content(
                request.content_text, 
                request.platforms or ["general"],
                request.target_audience
            )
        elif request.content_url:
            optimization_result = await service.optimize_media_content(
                request.content_url,
                request.platforms or ["general"]
            )
        else:
            # Generate optimization recommendations based on creator profile
            optimization_result = await service.generate_optimization_strategy(
                request.creator_id,
                request.platforms or ["general"]
            )
        
        return {
            "recommendations": optimization_result.recommendations,
            "insights": [
                {"type": "content_quality", "data": optimization_result.quality_analysis},
                {"type": "seo_opportunities", "data": optimization_result.seo_suggestions},
                {"type": "platform_alignment", "data": optimization_result.platform_optimization}
            ],
            "metrics": {
                "optimization_score": optimization_result.optimization_score,
                "potential_reach_increase": optimization_result.predicted_reach_increase,
                "engagement_improvement": optimization_result.predicted_engagement_improvement
            },
            "confidence_score": optimization_result.confidence_level,
            "next_steps": optimization_result.action_items,
            "metadata": {"optimization_type": optimization_result.optimization_type}
        }
    
    async def _process_platform_recommendations(
        self, 
        service: PlatformRecommendationEngine, 
        request: ContentGuidanceRequest
    ) -> Dict[str, Any]:
        """Process platform recommendation guidance."""
        
        # Analyze platform strategy
        strategy = await service.generate_platform_strategy(
            request.creator_id,
            request.content_type,
            request.target_audience,
            request.objectives or []
        )
        
        # Get platform-specific recommendations
        platform_recs = await service.recommend_optimal_platforms(
            request.creator_id,
            request.content_type
        )
        
        return {
            "recommendations": [
                {"type": "platform_strategy", "data": strategy},
                {"type": "platform_selection", "data": platform_recs}
            ],
            "insights": [
                {"type": "audience_platform_alignment", "data": strategy.audience_analysis},
                {"type": "content_platform_fit", "data": strategy.content_optimization},
                {"type": "growth_opportunities", "data": strategy.growth_potential}
            ],
            "metrics": {
                "strategy_score": strategy.overall_score,
                "platform_coverage": len(platform_recs),
                "expected_reach": strategy.projected_reach
            },
            "confidence_score": strategy.confidence_level,
            "next_steps": strategy.implementation_steps,
            "metadata": {"strategy_type": strategy.strategy_type}
        }
    
    async def _process_monetization_guidance(
        self, 
        service: MonetizationGuidanceEngine, 
        request: ContentGuidanceRequest
    ) -> Dict[str, Any]:
        """Process monetization guidance."""
        
        # Generate monetization strategy
        monetization_strategy = await service.generate_monetization_strategy(
            request.creator_id,
            request.platforms or [],
            request.budget_range
        )
        
        # Find brand partnership opportunities
        brand_opportunities = await service.find_brand_partnerships(
            request.creator_id,
            request.content_type
        )
        
        return {
            "recommendations": [
                {"type": "monetization_strategy", "data": monetization_strategy},
                {"type": "brand_partnerships", "data": brand_opportunities}
            ],
            "insights": [
                {"type": "revenue_potential", "data": monetization_strategy.revenue_analysis},
                {"type": "market_opportunities", "data": monetization_strategy.market_analysis},
                {"type": "optimization_areas", "data": monetization_strategy.optimization_opportunities}
            ],
            "metrics": {
                "revenue_potential": monetization_strategy.estimated_monthly_revenue,
                "partnership_score": len(brand_opportunities),
                "monetization_readiness": monetization_strategy.readiness_score
            },
            "confidence_score": monetization_strategy.confidence_level,
            "next_steps": monetization_strategy.action_plan,
            "metadata": {"strategy_focus": monetization_strategy.primary_revenue_streams}
        }
    
    async def _process_trend_analysis(
        self, 
        service: TrendAnalyzer, 
        request: ContentGuidanceRequest
    ) -> Dict[str, Any]:
        """Process trend analysis guidance."""
        
        # Analyze current trends
        trend_analysis = await service.analyze_trending_content(
            request.platforms or ["all"],
            request.content_type
        )
        
        # Get trend-based recommendations
        trend_opportunities = await service.identify_trend_opportunities(
            request.creator_id,
            request.content_type
        )
        
        return {
            "recommendations": [
                {"type": "trending_topics", "data": trend_analysis.trending_topics},
                {"type": "trend_opportunities", "data": trend_opportunities}
            ],
            "insights": [
                {"type": "viral_potential", "data": trend_analysis.viral_patterns},
                {"type": "content_gaps", "data": trend_analysis.content_gaps},
                {"type": "timing_recommendations", "data": trend_analysis.optimal_timing}
            ],
            "metrics": {
                "trend_alignment_score": trend_analysis.alignment_score,
                "viral_potential": trend_analysis.viral_probability,
                "trend_coverage": len(trend_analysis.relevant_trends)
            },
            "confidence_score": trend_analysis.confidence_level,
            "next_steps": trend_analysis.action_recommendations,
            "metadata": {"analysis_timeframe": trend_analysis.timeframe}
        }
    
    async def _process_audience_insights(
        self, 
        service: AudienceInsightsEngine, 
        request: ContentGuidanceRequest
    ) -> Dict[str, Any]:
        """Process audience insights guidance."""
        
        # Generate comprehensive audience insights
        audience_insights = await service.generate_audience_insights(
            request.creator_id,
            request.platforms or [],
            "30d"
        )
        
        # Analyze audience growth potential
        growth_analysis = await service.analyze_audience_growth(
            request.creator_id,
            "90d"
        )
        
        return {
            "recommendations": [
                {"type": "audience_targeting", "data": audience_insights[:5]},
                {"type": "growth_strategies", "data": growth_analysis.growth_opportunities}
            ],
            "insights": [
                {"type": "demographic_analysis", "data": [insight for insight in audience_insights if insight.insight_type == "demographic"]},
                {"type": "engagement_patterns", "data": [insight for insight in audience_insights if insight.insight_type == "engagement"]},
                {"type": "growth_analysis", "data": growth_analysis}
            ],
            "metrics": {
                "audience_health_score": sum(insight.significance_score for insight in audience_insights[:10]) / 10,
                "growth_rate": growth_analysis.growth_rate,
                "retention_rate": growth_analysis.retention_rate
            },
            "confidence_score": sum(insight.confidence_level for insight in audience_insights[:5]) / 5,
            "next_steps": [rec for insight in audience_insights[:3] for rec in insight.actionable_recommendations[:2]],
            "metadata": {"insights_count": len(audience_insights)}
        }
    
    async def _process_brand_safety(
        self, 
        service: BrandSafetyEngine, 
        request: ContentGuidanceRequest
    ) -> Dict[str, Any]:
        """Process brand safety guidance."""
        
        if request.content_text:
            safety_analysis = await service.analyze_text_content(
                request.content_text,
                request.platforms or ["general"]
            )
        elif request.content_url:
            safety_analysis = await service.analyze_media_content(
                request.content_url
            )
        else:
            # Analyze creator's overall brand safety profile
            safety_analysis = await service.analyze_creator_safety_profile(
                request.creator_id
            )
        
        return {
            "recommendations": safety_analysis.recommendations,
            "insights": [
                {"type": "safety_assessment", "data": safety_analysis.safety_assessment},
                {"type": "compliance_status", "data": safety_analysis.compliance_status},
                {"type": "risk_factors", "data": safety_analysis.risk_factors}
            ],
            "metrics": {
                "safety_score": safety_analysis.overall_safety_score,
                "compliance_score": safety_analysis.compliance_score,
                "risk_level": safety_analysis.risk_level.value
            },
            "confidence_score": safety_analysis.confidence_level,
            "next_steps": safety_analysis.improvement_actions,
            "warnings": safety_analysis.safety_warnings,
            "metadata": {"analysis_type": safety_analysis.analysis_type}
        }
    
    async def _process_collaboration_finding(
        self, 
        service: CollaborationFinder, 
        request: ContentGuidanceRequest
    ) -> Dict[str, Any]:
        """Process collaboration finding guidance."""
        
        # Find collaboration opportunities
        collaboration_opportunities = await service.find_collaboration_opportunities(
            request.creator_id,
            request.content_type,
            request.platforms or []
        )
        
        # Analyze collaboration potential
        collaboration_analysis = await service.analyze_collaboration_potential(
            request.creator_id
        )
        
        return {
            "recommendations": [
                {"type": "collaboration_opportunities", "data": collaboration_opportunities},
                {"type": "collaboration_strategy", "data": collaboration_analysis.strategy_recommendations}
            ],
            "insights": [
                {"type": "network_analysis", "data": collaboration_analysis.network_insights},
                {"type": "compatibility_factors", "data": collaboration_analysis.compatibility_analysis},
                {"type": "success_predictors", "data": collaboration_analysis.success_factors}
            ],
            "metrics": {
                "collaboration_score": collaboration_analysis.collaboration_readiness,
                "opportunity_count": len(collaboration_opportunities),
                "network_strength": collaboration_analysis.network_score
            },
            "confidence_score": collaboration_analysis.confidence_level,
            "next_steps": collaboration_analysis.action_plan,
            "metadata": {"analysis_scope": collaboration_analysis.scope}
        }
    
    async def _process_content_scheduling(
        self, 
        service: ContentScheduler, 
        request: ContentGuidanceRequest
    ) -> Dict[str, Any]:
        """Process content scheduling guidance."""
        
        # Generate optimal posting schedule
        schedule_recommendations = await service.generate_optimal_schedule(
            request.creator_id,
            request.platforms or [],
            request.timeframe or "weekly"
        )
        
        # Analyze posting patterns
        timing_analysis = await service.analyze_optimal_timing(
            request.creator_id,
            request.platforms or []
        )
        
        return {
            "recommendations": [
                {"type": "posting_schedule", "data": schedule_recommendations},
                {"type": "timing_optimization", "data": timing_analysis.timing_recommendations}
            ],
            "insights": [
                {"type": "audience_activity", "data": timing_analysis.audience_activity_patterns},
                {"type": "platform_timing", "data": timing_analysis.platform_specific_timing},
                {"type": "content_cadence", "data": timing_analysis.optimal_frequency}
            ],
            "metrics": {
                "scheduling_score": timing_analysis.optimization_score,
                "expected_reach_improvement": timing_analysis.projected_reach_increase,
                "optimal_posting_slots": len(schedule_recommendations)
            },
            "confidence_score": timing_analysis.confidence_level,
            "next_steps": timing_analysis.implementation_steps,
            "metadata": {"schedule_type": timing_analysis.schedule_type}
        }
    
    async def _process_creative_assistance(
        self, 
        service: CreativeAssistant, 
        request: ContentGuidanceRequest
    ) -> Dict[str, Any]:
        """Process creative assistance guidance."""
        
        # Generate creative ideas
        creative_ideas = await service.generate_content_ideas(
            request.creator_id,
            request.content_type,
            request.platforms or [],
            count=10
        )
        
        # Provide creative optimization suggestions
        creative_optimization = await service.optimize_creative_strategy(
            request.creator_id,
            request.content_type
        )
        
        return {
            "recommendations": [
                {"type": "content_ideas", "data": creative_ideas},
                {"type": "creative_optimization", "data": creative_optimization.optimization_suggestions}
            ],
            "insights": [
                {"type": "creative_trends", "data": creative_optimization.trend_insights},
                {"type": "format_recommendations", "data": creative_optimization.format_suggestions},
                {"type": "inspiration_sources", "data": creative_optimization.inspiration_sources}
            ],
            "metrics": {
                "creativity_score": creative_optimization.creativity_score,
                "idea_diversity": len(set(idea.category for idea in creative_ideas)),
                "trend_alignment": creative_optimization.trend_alignment_score
            },
            "confidence_score": creative_optimization.confidence_level,
            "next_steps": creative_optimization.action_steps,
            "metadata": {"creative_focus": creative_optimization.primary_themes}
        }
    
    async def _process_performance_tracking(
        self, 
        service: PerformanceTracker, 
        request: ContentGuidanceRequest
    ) -> Dict[str, Any]:
        """Process performance tracking guidance."""
        
        # Generate performance report
        performance_report = await service.generate_performance_report(
            request.creator_id,
            request.platforms or [],
            "30d"
        )
        
        # Analyze performance trends
        performance_analysis = await service.analyze_performance_trends(
            request.creator_id,
            "90d"
        )
        
        return {
            "recommendations": [
                {"type": "performance_optimization", "data": performance_report.optimization_recommendations},
                {"type": "growth_strategies", "data": performance_analysis.growth_recommendations}
            ],
            "insights": [
                {"type": "performance_metrics", "data": performance_report.key_metrics},
                {"type": "trend_analysis", "data": performance_analysis.trend_insights},
                {"type": "competitive_position", "data": performance_analysis.competitive_analysis}
            ],
            "metrics": {
                "overall_performance_score": performance_report.overall_score,
                "growth_rate": performance_analysis.growth_rate,
                "engagement_trend": performance_analysis.engagement_trend
            },
            "confidence_score": performance_report.confidence_level,
            "next_steps": performance_report.action_recommendations,
            "metadata": {"reporting_period": performance_report.period}
        }
    
    async def _analyze_content_safety(self, request: ContentGuidanceRequest) -> Dict[str, Any]:
        """Analyze content safety before processing."""
        
        if not (request.content_text or request.content_url):
            return {"is_safe": True, "safety_score": 1.0}
        
        try:
            if request.content_text:
                safety_result = await self.brand_safety_engine.analyze_text_content(
                    request.content_text,
                    request.platforms or ["general"]
                )
            else:
                safety_result = await self.brand_safety_engine.analyze_media_content(
                    request.content_url
                )
            
            is_safe = safety_result.overall_safety_score >= 0.7
            
            return {
                "is_safe": is_safe,
                "safety_score": safety_result.overall_safety_score,
                "risk_factors": safety_result.risk_factors,
                "recommendations": safety_result.recommendations
            }
            
        except Exception as e:
            self.logger.error(f"Safety analysis failed: {e}")
            return {"is_safe": False, "safety_score": 0.0, "error": str(e)}
    
    async def _optimize_cross_service_recommendations(
        self,
        results: Dict[ContentGuidanceServiceType, ContentGuidanceResponse],
        request: ContentGuidanceRequest
    ) -> Dict[ContentGuidanceServiceType, ContentGuidanceResponse]:
        """Optimize recommendations across services to avoid conflicts."""
        
        # Identify conflicting recommendations
        conflicts = self._identify_recommendation_conflicts(results)
        
        # Resolve conflicts based on priority and confidence scores
        if conflicts:
            resolved_results = self._resolve_recommendation_conflicts(results, conflicts)
            return resolved_results
        
        return results
    
    def _identify_recommendation_conflicts(
        self,
        results: Dict[ContentGuidanceServiceType, ContentGuidanceResponse]
    ) -> List[Dict[str, Any]]:
        """Identify conflicting recommendations across services."""
        
        conflicts = []
        
        # Example: Check for timing conflicts between scheduling and trend recommendations
        schedule_service = results.get(ContentGuidanceServiceType.SCHEDULING)
        trend_service = results.get(ContentGuidanceServiceType.TREND_ANALYSIS)
        
        if schedule_service and trend_service:
            # Check for conflicting timing recommendations
            schedule_times = self._extract_posting_times(schedule_service.recommendations)
            trend_times = self._extract_posting_times(trend_service.recommendations)
            
            if schedule_times and trend_times:
                time_conflicts = self._find_time_conflicts(schedule_times, trend_times)
                if time_conflicts:
                    conflicts.append({
                        "type": "timing_conflict",
                        "services": [ContentGuidanceServiceType.SCHEDULING, ContentGuidanceServiceType.TREND_ANALYSIS],
                        "details": time_conflicts
                    })
        
        return conflicts
    
    def _resolve_recommendation_conflicts(
        self,
        results: Dict[ContentGuidanceServiceType, ContentGuidanceResponse],
        conflicts: List[Dict[str, Any]]
    ) -> Dict[ContentGuidanceServiceType, ContentGuidanceResponse]:
        """Resolve identified conflicts by prioritizing higher confidence recommendations."""
        
        resolved_results = results.copy()
        
        for conflict in conflicts:
            if conflict["type"] == "timing_conflict":
                # Prioritize the service with higher confidence score
                services = conflict["services"]
                service_scores = {
                    service: results[service].confidence_score 
                    for service in services
                }
                
                primary_service = max(service_scores.items(), key=lambda x: x[1])[0]
                secondary_service = min(service_scores.items(), key=lambda x: x[1])[0]
                
                # Add warning to secondary service
                warning = f"Timing recommendations adjusted due to conflict with {primary_service.value}"
                if resolved_results[secondary_service].warnings:
                    resolved_results[secondary_service].warnings.append(warning)
                else:
                    resolved_results[secondary_service].warnings = [warning]
        
        return resolved_results
    
    async def _generate_unified_action_plan(
        self,
        results: Dict[ContentGuidanceServiceType, ContentGuidanceResponse],
        request: ContentGuidanceRequest
    ) -> List[str]:
        """Generate a unified action plan across all services."""
        
        # Collect all next steps
        all_next_steps = []
        for response in results.values():
            all_next_steps.extend(response.next_steps)
        
        # Prioritize and deduplicate
        prioritized_steps = self._prioritize_action_steps(all_next_steps, results)
        
        # Create unified plan
        unified_plan = [
            "Review all recommendations and identify top priorities",
            "Implement safety recommendations if any critical issues found",
            "Start with quick wins from content optimization",
            "Develop long-term strategy based on audience insights",
            "Schedule content implementation based on timing recommendations"
        ]
        
        # Add top prioritized steps
        unified_plan.extend(prioritized_steps[:5])
        
        return unified_plan
    
    def _prioritize_action_steps(
        self, 
        steps: List[str], 
        results: Dict[ContentGuidanceServiceType, ContentGuidanceResponse]
    ) -> List[str]:
        """Prioritize action steps based on confidence scores and impact."""
        
        # Score each step based on the confidence of its source service
        step_scores = {}
        
        for service_type, response in results.items():
            service_confidence = response.confidence_score
            for step in response.next_steps:
                if step in step_scores:
                    step_scores[step] = max(step_scores[step], service_confidence)
                else:
                    step_scores[step] = service_confidence
        
        # Sort by score and return deduplicated list
        prioritized = sorted(step_scores.items(), key=lambda x: x[1], reverse=True)
        return [step for step, score in prioritized]
    
    def _extract_posting_times(self, recommendations: List[Dict[str, Any]]) -> List[str]:
        """Extract posting times from recommendations."""
        times = []
        for rec in recommendations:
            if rec.get("type") == "posting_schedule" and "data" in rec:
                schedule_data = rec["data"]
                if isinstance(schedule_data, dict) and "optimal_times" in schedule_data:
                    times.extend(schedule_data["optimal_times"])
        return times
    
    def _find_time_conflicts(self, times1: List[str], times2: List[str]) -> List[Dict[str, Any]]:
        """Find conflicts between two sets of posting times."""
        conflicts = []
        
        # Simple implementation - in practice would be more sophisticated
        common_times = set(times1) & set(times2)
        if len(common_times) < min(len(times1), len(times2)) // 2:
            conflicts.append({
                "issue": "Low overlap between recommended posting times",
                "times1": times1,
                "times2": times2,
                "overlap": list(common_times)
            })
        
        return conflicts
    
    def _create_error_response(
        self, 
        request: ContentGuidanceRequest, 
        service_type: ContentGuidanceServiceType, 
        error_message: str
    ) -> ContentGuidanceResponse:
        """Create an error response for a failed service."""
        
        return ContentGuidanceResponse(
            request_id=f"{request.creator_id}_{service_type.value}_error",
            creator_id=request.creator_id,
            service_type=service_type,
            recommendations=[],
            insights=[],
            metrics={},
            confidence_score=0.0,
            processing_time=0.0,
            next_steps=[f"Retry {service_type.value} service", "Contact support if issue persists"],
            errors=[error_message]
        )
    
    def _create_safety_error_response(
        self, 
        request: ContentGuidanceRequest, 
        safety_result: Dict[str, Any],
        service_type: ContentGuidanceServiceType = None
    ) -> Union[ContentGuidanceResponse, Dict[ContentGuidanceServiceType, ContentGuidanceResponse]]:
        """Create a safety error response."""
        
        error_response = ContentGuidanceResponse(
            request_id=f"{request.creator_id}_safety_error",
            creator_id=request.creator_id,
            service_type=service_type or ContentGuidanceServiceType.BRAND_SAFETY,
            recommendations=safety_result.get("recommendations", []),
            insights=[{"type": "safety_violation", "data": safety_result}],
            metrics={"safety_score": safety_result.get("safety_score", 0.0)},
            confidence_score=1.0,
            processing_time=0.0,
            next_steps=["Address safety concerns before proceeding", "Review content guidelines"],
            warnings=["Content failed safety analysis"],
            errors=["Content contains potentially unsafe elements"]
        )
        
        if service_type:
            return error_response
        else:
            # Return error for all services
            return {
                service_type: error_response 
                for service_type in ContentGuidanceServiceType
            }


# Global orchestrator instance
content_guidance_orchestrator = ContentGuidanceOrchestrator()


# Convenience functions for common operations
async def get_comprehensive_content_guidance(
    creator_id: str,
    content_id: str = None,
    content_type: str = None,
    content_url: str = None,
    content_text: str = None,
    platforms: List[str] = None,
    target_audience: str = None,
    objectives: List[str] = None
) -> Dict[ContentGuidanceServiceType, ContentGuidanceResponse]:
    """Get comprehensive content guidance across all services."""
    
    request = ContentGuidanceRequest(
        creator_id=creator_id,
        content_id=content_id,
        content_type=content_type,
        content_url=content_url,
        content_text=content_text,
        platforms=platforms or [],
        target_audience=target_audience,
        objectives=objectives or []
    )
    
    return await content_guidance_orchestrator.process_comprehensive_guidance(request)


async def get_specific_content_guidance(
    service_type: ContentGuidanceServiceType,
    creator_id: str,
    **kwargs
) -> ContentGuidanceResponse:
    """Get guidance for a specific service type."""
    
    request = ContentGuidanceRequest(
        creator_id=creator_id,
        **kwargs
    )
    
    return await content_guidance_orchestrator.process_single_service_guidance(service_type, request)


# Export main classes and functions
__all__ = [
    "ContentGuidanceOrchestrator",
    "ContentGuidanceRequest", 
    "ContentGuidanceResponse",
    "ContentGuidanceServiceType",
    "content_guidance_orchestrator",
    "get_comprehensive_content_guidance",
    "get_specific_content_guidance"
]
