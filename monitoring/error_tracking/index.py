"""
Error Tracking Orchestrator - Main Entry Point for Ainflue Creator Economy
Production-ready error tracking orchestration with AI-powered intelligence

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json

from .sentry_integration import SentryErrorTracker, ErrorContext, error_tracker
from .error_aggregator import ErrorAggregator, ErrorEvent, error_aggregator
from .error_analyzer import ErrorAnalyzer, error_analyzer
from .creator_economy_error_intelligence import CreatorEconomyErrorIntelligence
from .ai_processing_error_monitoring_engine import AIProcessingErrorMonitoringEngine
from .creator_workflow_error_tracker import CreatorWorkflowErrorTracker
from .multi_format_content_error_analyzer import MultiFormatContentErrorAnalyzer

logger = logging.getLogger(__name__)


class CreatorTier(Enum):
    """Creator tier enumeration for differentiated error tracking"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class ErrorTrackingMode(Enum):
    """Error tracking operational modes"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    HYBRID = "hybrid"
    ANALYSIS_ONLY = "analysis_only"


@dataclass
class CreatorErrorContext:
    """Enhanced error context for Creator Economy"""
    creator_id: str
    creator_tier: CreatorTier
    content_type: str
    workflow_stage: str
    business_context: str
    monetization_tier: Optional[str] = None
    collaboration_context: Optional[Dict[str, Any]] = None
    ai_processing_context: Optional[Dict[str, Any]] = None
    platform_context: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None


@dataclass
class ErrorTrackingConfiguration:
    """Error tracking system configuration"""
    mode: ErrorTrackingMode = ErrorTrackingMode.HYBRID
    real_time_enabled: bool = True
    ai_analysis_enabled: bool = True
    creator_intelligence_enabled: bool = True
    predictive_analysis_enabled: bool = True
    recovery_automation_enabled: bool = True
    cross_platform_sync_enabled: bool = True
    enterprise_reporting_enabled: bool = True
    retention_hours: int = 168  # 7 days
    max_events_memory: int = 50000
    alert_thresholds: Dict[str, int] = None
    
    def __post_init__(self):
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                "error_spike": 100,
                "service_errors": 50,
                "workflow_errors": 30,
                "creator_tier_errors": 20
            }


class ErrorTrackingOrchestrator:
    """
    Main Error Tracking Orchestrator for Creator Economy
    Coordinates all error tracking systems with intelligent routing
    """
    
    def __init__(self, config: Optional[ErrorTrackingConfiguration] = None):
        """
        Initialize error tracking orchestrator
        
        Args:
            config: Error tracking configuration
        """
        self.config = config or ErrorTrackingConfiguration()
        self._initialized = False
        self._components = {}
        self._startup_time = datetime.utcnow()
        self._active_sessions = {}
        self._error_routing_cache = {}
        
        # Initialize core components
        self._initialize_components()
        
        logger.info("ErrorTrackingOrchestrator initialized for Creator Economy")
    
    def _initialize_components(self):
        """Initialize all error tracking components"""
        try:
            # Core components (already initialized globally)
            self._components['sentry'] = error_tracker
            self._components['aggregator'] = error_aggregator
            self._components['analyzer'] = error_analyzer
            
            # Creator Economy specific components
            self._components['creator_intelligence'] = CreatorEconomyErrorIntelligence()
            self._components['ai_monitoring'] = AIProcessingErrorMonitoringEngine()
            self._components['workflow_tracker'] = CreatorWorkflowErrorTracker()
            self._components['content_analyzer'] = MultiFormatContentErrorAnalyzer()
            
            # Advanced components (will be initialized when other modules are created)
            self._components['monetization_detector'] = None
            self._components['tier_orchestrator'] = None
            self._components['real_time_automation'] = None
            self._components['performance_correlator'] = None
            self._components['platform_sync_hub'] = None
            self._components['prediction_engine'] = None
            self._components['impact_assessor'] = None
            self._components['reporting_intelligence'] = None
            self._components['recovery_orchestrator'] = None
            
            self._initialized = True
            logger.info("All error tracking components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize error tracking components: {e}")
            raise
    
    async def track_creator_error(self, 
                                 error: Exception,
                                 creator_context: CreatorErrorContext,
                                 severity: str = "error",
                                 auto_analyze: bool = True,
                                 auto_recover: bool = True) -> str:
        """
        Track Creator Economy error with intelligent routing
        
        Args:
            error: Exception to track
            creator_context: Creator-specific context
            severity: Error severity level
            auto_analyze: Enable automatic analysis
            auto_recover: Enable automatic recovery
            
        Returns:
            Error tracking session ID
        """
        if not self._initialized:
            raise RuntimeError("Error tracking orchestrator not initialized")
        
        session_id = f"creator_{creator_context.creator_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            # Create enhanced error context
            error_context = self._create_error_context(creator_context)
            
            # Route error to appropriate tracking systems
            tracking_results = await self._route_error_tracking(
                error, creator_context, error_context, severity, session_id
            )
            
            # Store session information
            self._active_sessions[session_id] = {
                "creator_context": creator_context,
                "error": str(error),
                "severity": severity,
                "timestamp": datetime.utcnow(),
                "tracking_results": tracking_results,
                "auto_analyze": auto_analyze,
                "auto_recover": auto_recover
            }
            
            # Trigger automatic analysis if enabled
            if auto_analyze:
                asyncio.create_task(self._analyze_error_async(session_id))
            
            # Trigger automatic recovery if enabled and severity is high
            if auto_recover and severity in ['error', 'critical', 'emergency']:
                asyncio.create_task(self._attempt_recovery_async(session_id))
            
            logger.info(f"Creator error tracked successfully: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to track creator error: {e}")
            raise
    
    def _create_error_context(self, creator_context: CreatorErrorContext) -> ErrorContext:
        """Create enhanced error context from creator context"""
        additional_data = {
            "creator_tier": creator_context.creator_tier.value,
            "content_type": creator_context.content_type,
            "monetization_tier": creator_context.monetization_tier,
            "collaboration_context": creator_context.collaboration_context,
            "ai_processing_context": creator_context.ai_processing_context,
            "platform_context": creator_context.platform_context,
            "performance_metrics": creator_context.performance_metrics
        }
        
        return ErrorContext(
            user_id=creator_context.creator_id,
            service_name="creator_economy",
            business_context=creator_context.business_context,
            workflow_stage=creator_context.workflow_stage,
            additional_data=additional_data
        )
    
    async def _route_error_tracking(self, 
                                   error: Exception,
                                   creator_context: CreatorErrorContext,
                                   error_context: ErrorContext,
                                   severity: str,
                                   session_id: str) -> Dict[str, Any]:
        """Route error to appropriate tracking systems based on context"""
        results = {}
        
        # Always track to Sentry for centralized logging
        sentry_id = self._components['sentry'].capture_error(
            error, error_context, severity
        )
        results['sentry_event_id'] = sentry_id
        
        # Track to aggregator for statistics
        self._components['aggregator'].add_error(
            error_type=error.__class__.__name__,
            error_message=str(error),
            service_name="creator_economy",
            workflow_stage=creator_context.workflow_stage,
            user_id=creator_context.creator_id,
            severity=severity,
            context=asdict(creator_context),
            event_id=session_id
        )
        results['aggregated'] = True
        
        # Route to Creator Economy intelligence
        creator_intelligence_result = await self._components['creator_intelligence'].analyze_creator_error(
            error, creator_context
        )
        results['creator_intelligence'] = creator_intelligence_result
        
        # Route to AI processing monitoring if AI-related
        if (creator_context.ai_processing_context or 
            'ai' in creator_context.workflow_stage.lower() or
            'processing' in creator_context.workflow_stage.lower()):
            ai_monitoring_result = await self._components['ai_monitoring'].monitor_ai_error(
                error, creator_context
            )
            results['ai_monitoring'] = ai_monitoring_result
        
        # Route to workflow tracker
        workflow_result = await self._components['workflow_tracker'].track_workflow_error(
            error, creator_context
        )
        results['workflow_tracking'] = workflow_result
        
        # Route to content analyzer based on content type
        if creator_context.content_type in ['audio', 'video', 'image', 'text']:
            content_analysis_result = await self._components['content_analyzer'].analyze_content_error(
                error, creator_context
            )
            results['content_analysis'] = content_analysis_result
        
        return results
    
    async def _analyze_error_async(self, session_id: str):
        """Perform asynchronous error analysis"""
        try:
            session = self._active_sessions.get(session_id)
            if not session:
                return
            
            # Get recent events for analysis
            events = self._components['aggregator'].events[-100:]  # Last 100 events
            
            # Perform comprehensive analysis
            analysis_result = self._components['analyzer'].analyze_errors(events, 24)
            
            # Store analysis results
            session['analysis_result'] = analysis_result
            session['analyzed_at'] = datetime.utcnow()
            
            logger.info(f"Error analysis completed for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error analysis failed for session {session_id}: {e}")
    
    async def _attempt_recovery_async(self, session_id: str):
        """Attempt automatic error recovery"""
        try:
            session = self._active_sessions.get(session_id)
            if not session or not self.config.recovery_automation_enabled:
                return
            
            creator_context = session['creator_context']
            
            # Attempt workflow-specific recovery
            recovery_result = await self._components['workflow_tracker'].attempt_recovery(
                creator_context
            )
            
            # Store recovery results
            session['recovery_result'] = recovery_result
            session['recovery_attempted_at'] = datetime.utcnow()
            
            logger.info(f"Recovery attempted for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Recovery attempt failed for session {session_id}: {e}")
    
    def get_creator_error_statistics(self, 
                                   creator_id: str,
                                   time_period: str = "24h") -> Dict[str, Any]:
        """
        Get error statistics for specific creator
        
        Args:
            creator_id: Creator identifier
            time_period: Time period for statistics
            
        Returns:
            Creator-specific error statistics
        """
        try:
            # Filter events for specific creator
            creator_events = [
                event for event in self._components['aggregator'].events
                if event.user_id == creator_id
            ]
            
            if not creator_events:
                return {
                    "creator_id": creator_id,
                    "total_errors": 0,
                    "time_period": time_period,
                    "workflows_affected": [],
                    "content_types_affected": [],
                    "severity_breakdown": {},
                    "recent_patterns": []
                }
            
            # Analyze creator-specific patterns
            creator_analysis = self._components['creator_intelligence'].analyze_creator_patterns(
                creator_id, creator_events
            )
            
            # Get workflow statistics
            workflow_stats = self._components['workflow_tracker'].get_creator_workflow_stats(
                creator_id, time_period
            )
            
            # Combine results
            return {
                "creator_id": creator_id,
                "total_errors": len(creator_events),
                "time_period": time_period,
                "creator_analysis": creator_analysis,
                "workflow_statistics": workflow_stats,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get creator error statistics: {e}")
            return {"error": str(e)}
    
    def get_creator_tier_insights(self, 
                                 creator_tier: CreatorTier,
                                 time_period: str = "24h") -> Dict[str, Any]:
        """
        Get error insights by creator tier
        
        Args:
            creator_tier: Creator tier to analyze
            time_period: Time period for analysis
            
        Returns:
            Tier-specific error insights
        """
        try:
            # Filter events by creator tier
            tier_events = []
            for event in self._components['aggregator'].events:
                if (event.context and 
                    isinstance(event.context, dict) and
                    event.context.get('creator_tier') == creator_tier.value):
                    tier_events.append(event)
            
            if not tier_events:
                return {
                    "creator_tier": creator_tier.value,
                    "total_errors": 0,
                    "time_period": time_period
                }
            
            # Analyze tier-specific patterns
            tier_analysis = self._components['creator_intelligence'].analyze_tier_patterns(
                creator_tier, tier_events
            )
            
            return {
                "creator_tier": creator_tier.value,
                "total_errors": len(tier_events),
                "time_period": time_period,
                "tier_analysis": tier_analysis,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get creator tier insights: {e}")
            return {"error": str(e)}
    
    def get_system_health_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive system health dashboard
        
        Returns:
            System health dashboard data
        """
        try:
            # Get overall statistics
            overall_stats = self._components['aggregator'].get_statistics("24h")
            
            # Get critical alerts
            alerts = self._components['aggregator'].get_critical_alerts()
            
            # Get analysis insights
            recent_events = self._components['aggregator'].events[-500:]  # Last 500 events
            analysis = self._components['analyzer'].analyze_errors(recent_events, 24)
            
            # Get component health
            component_health = self._check_component_health()
            
            return {
                "system_overview": {
                    "uptime_hours": (datetime.utcnow() - self._startup_time).total_seconds() / 3600,
                    "active_sessions": len(self._active_sessions),
                    "components_healthy": sum(1 for status in component_health.values() if status == "healthy"),
                    "total_components": len(component_health)
                },
                "error_statistics": asdict(overall_stats),
                "critical_alerts": alerts,
                "analysis_insights": analysis,
                "component_health": component_health,
                "configuration": asdict(self.config),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate system health dashboard: {e}")
            return {"error": str(e)}
    
    def _check_component_health(self) -> Dict[str, str]:
        """Check health of all components"""
        health_status = {}
        
        for component_name, component in self._components.items():
            try:
                if component is None:
                    health_status[component_name] = "not_initialized"
                elif hasattr(component, 'health_check'):
                    health_status[component_name] = component.health_check()
                else:
                    # Basic health check - component exists and has expected methods
                    expected_methods = {
                        'sentry': ['capture_error'],
                        'aggregator': ['add_error', 'get_statistics'],
                        'analyzer': ['analyze_errors'],
                        'creator_intelligence': ['analyze_creator_error'],
                        'ai_monitoring': ['monitor_ai_error'],
                        'workflow_tracker': ['track_workflow_error'],
                        'content_analyzer': ['analyze_content_error']
                    }
                    
                    if component_name in expected_methods:
                        methods = expected_methods[component_name]
                        if all(hasattr(component, method) for method in methods):
                            health_status[component_name] = "healthy"
                        else:
                            health_status[component_name] = "degraded"
                    else:
                        health_status[component_name] = "unknown"
                        
            except Exception as e:
                health_status[component_name] = f"error: {str(e)[:50]}"
        
        return health_status
    
    async def shutdown(self):
        """Graceful shutdown of error tracking orchestrator"""
        try:
            logger.info("Shutting down error tracking orchestrator...")
            
            # Flush any pending Sentry events
            if self._components.get('sentry'):
                self._components['sentry'].flush(timeout=5)
            
            # Clear active sessions
            self._active_sessions.clear()
            
            # Clear routing cache
            self._error_routing_cache.clear()
            
            logger.info("Error tracking orchestrator shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Global orchestrator instance
orchestrator = ErrorTrackingOrchestrator()


# Convenience functions for easy access
def track_creator_error(error: Exception, 
                       creator_context: CreatorErrorContext,
                       severity: str = "error") -> str:
    """
    Convenience function to track creator error synchronously
    
    Args:
        error: Exception to track
        creator_context: Creator-specific context
        severity: Error severity level
        
    Returns:
        Error tracking session ID
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If in async context, create task
            task = asyncio.create_task(
                orchestrator.track_creator_error(error, creator_context, severity)
            )
            return f"async_task_{id(task)}"
        else:
            # Run in new event loop
            return asyncio.run(
                orchestrator.track_creator_error(error, creator_context, severity)
            )
    except Exception as e:
        logger.error(f"Failed to track creator error: {e}")
        # Fallback to basic Sentry tracking
        error_context = ErrorContext(
            user_id=creator_context.creator_id,
            service_name="creator_economy",
            business_context=creator_context.business_context,
            workflow_stage=creator_context.workflow_stage
        )
        return error_tracker.capture_error(error, error_context, severity) or "fallback"


def get_creator_dashboard(creator_id: str) -> Dict[str, Any]:
    """
    Get creator-specific error dashboard
    
    Args:
        creator_id: Creator identifier
        
    Returns:
        Creator error dashboard data
    """
    return orchestrator.get_creator_error_statistics(creator_id)


def get_system_dashboard() -> Dict[str, Any]:
    """
    Get system-wide error dashboard
    
    Returns:
        System error dashboard data
    """
    return orchestrator.get_system_health_dashboard()