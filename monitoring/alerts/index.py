"""🚨 Alerts System Orchestrator - Creator Economy Enterprise
=========================================================

Main orchestrator for the complete enterprise alerts system specialized for
Creator Economy business logic with intelligent routing and coordination.

Features:
- Factory pattern for all alert components instantiation
- Centralized configuration and routing for Creator-specific alerts
- Multi-type alerts coordination (business/technical/AI/creator-specific)
- Real-time dashboard integration for Creator Economy metrics
- Enterprise-grade error handling and monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code owned by Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Team training provided
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Type, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from contextlib import asynccontextmanager

# Import existing alert managers
from .intelligent_alert_manager import IntelligentAlertManager, AlertCategory, AlertSeverity
from .alert_coordinator import AlertCoordinator, SystemHealthStatus
from .business_alerts import BusinessAlertManager
from .technical_alerts import TechnicalAlertManager
from .ai_alerts import AIAlertManager

logger = logging.getLogger(__name__)


class CreatorType(Enum):
    """Creator types for specialized alert routing"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    VIDEO_CREATOR = "video_creator"
    ARTIST = "artist"


class CreatorTier(Enum):
    """Creator tiers for priority-based alert handling"""
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    STANDARD = "standard"
    STARTER = "starter"


@dataclass
class CreatorContext:
    """Creator context for alert personalization"""
    creator_id: str
    creator_type: CreatorType
    creator_tier: CreatorTier
    revenue_tier: str
    engagement_score: float
    content_formats: List[str]
    collaboration_active: bool = False
    gamification_level: int = 1
    seo_score: float = 0.0
    distribution_channels: List[str] = field(default_factory=list)


@dataclass
class AlertsSystemConfig:
    """Configuration for the alerts system orchestrator"""
    enable_creator_specific_alerts: bool = True
    enable_collaboration_alerts: bool = True
    enable_gamification_alerts: bool = True
    enable_seo_alerts: bool = True
    enable_distribution_alerts: bool = True
    enable_content_protection_alerts: bool = True
    enable_monetization_intelligence: bool = True
    
    # Performance settings
    max_concurrent_alerts: int = 1000
    alert_processing_timeout: int = 30
    batch_processing_size: int = 50
    
    # Creator-specific settings
    premium_creator_response_time: int = 15  # seconds
    professional_creator_response_time: int = 60  # seconds
    standard_creator_response_time: int = 300  # seconds
    
    # Integration settings
    dashboard_update_interval: int = 10  # seconds
    metrics_collection_interval: int = 60  # seconds


class AlertsSystemOrchestrator:
    """
    Enterprise alerts system orchestrator for Creator Economy
    
    Provides centralized coordination of all alert types with Creator-specific
    business logic, intelligent routing, and real-time monitoring.
    """
    
    def __init__(self, config: AlertsSystemConfig):
        self.config = config
        self.is_running = False
        self._shutdown_event = asyncio.Event()
        
        # Core alert managers
        self.intelligent_manager = IntelligentAlertManager()
        self.coordinator = AlertCoordinator()
        self.business_manager = BusinessAlertManager(self.intelligent_manager)
        self.technical_manager = TechnicalAlertManager(self.intelligent_manager)
        self.ai_manager = AIAlertManager(self.intelligent_manager)
        
        # Creator-specific managers (will be initialized when components are created)
        self.creator_specific_engine = None
        self.collaboration_system = None
        self.gamification_monitor = None
        self.seo_tracker = None
        self.distribution_manager = None
        self.content_protection_engine = None
        self.creator_tier_prioritization = None
        self.multi_format_analyzer = None
        self.creator_engagement_system = None
        self.monetization_intelligence = None
        
        # Metrics and monitoring
        self.metrics = {
            'total_alerts_processed': 0,
            'alerts_by_creator_type': {},
            'alerts_by_tier': {},
            'response_times': [],
            'error_count': 0,
            'uptime_start': datetime.now()
        }
        
        logger.info(f"AlertsSystemOrchestrator initialized with config: {config}")
    
    async def initialize(self) -> None:
        """Initialize all alert system components"""
        try:
            logger.info("Initializing Alerts System Orchestrator...")
            
            # Initialize core managers
            await self.intelligent_manager.initialize()
            await self.coordinator.initialize()
            await self.business_manager.initialize()
            await self.technical_manager.initialize()
            await self.ai_manager.initialize()
            
            # Initialize Creator-specific components when available
            await self._initialize_creator_components()
            
            # Set up monitoring and metrics collection
            await self._setup_monitoring()
            
            self.is_running = True
            logger.info("Alerts System Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AlertsSystemOrchestrator: {e}")
            raise
    
    async def _initialize_creator_components(self) -> None:
        """Initialize Creator Economy specific components"""
        try:
            # These will be initialized as the components are implemented
            if self.config.enable_creator_specific_alerts:
                logger.info("Creator-specific alert engine will be initialized when available")
            
            if self.config.enable_collaboration_alerts:
                logger.info("Collaboration alert system will be initialized when available")
            
            if self.config.enable_gamification_alerts:
                logger.info("Gamification alert monitor will be initialized when available")
            
            if self.config.enable_seo_alerts:
                logger.info("SEO performance tracker will be initialized when available")
            
            if self.config.enable_distribution_alerts:
                logger.info("Distribution channel manager will be initialized when available")
            
            if self.config.enable_content_protection_alerts:
                logger.info("Content protection engine will be initialized when available")
                
            if self.config.enable_monetization_intelligence:
                logger.info("Monetization intelligence will be initialized when available")
                
        except Exception as e:
            logger.error(f"Error initializing creator components: {e}")
    
    async def _setup_monitoring(self) -> None:
        """Set up internal monitoring and metrics collection"""
        # Start background tasks for monitoring
        asyncio.create_task(self._metrics_collector())
        asyncio.create_task(self._health_monitor())
        logger.info("Monitoring and metrics collection started")
    
    async def process_creator_alert(
        self, 
        alert_data: Dict[str, Any], 
        creator_context: CreatorContext
    ) -> Dict[str, Any]:
        """
        Process alert with Creator Economy context
        
        Args:
            alert_data: Raw alert data
            creator_context: Creator-specific context for personalization
            
        Returns:
            Processed alert result with routing and priority information
        """
        start_time = datetime.now()
        
        try:
            # Enrich alert with creator context
            enriched_alert = await self._enrich_alert_with_creator_context(
                alert_data, creator_context
            )
            
            # Determine alert routing based on creator type and tier
            routing_info = await self._determine_alert_routing(
                enriched_alert, creator_context
            )
            
            # Process through appropriate managers
            result = await self._route_alert_to_managers(
                enriched_alert, routing_info
            )
            
            # Update metrics
            await self._update_processing_metrics(creator_context, start_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing creator alert: {e}")
            self.metrics['error_count'] += 1
            raise
    
    async def _enrich_alert_with_creator_context(
        self, 
        alert_data: Dict[str, Any], 
        creator_context: CreatorContext
    ) -> Dict[str, Any]:
        """Enrich alert data with Creator Economy context"""
        enriched = alert_data.copy()
        
        enriched.update({
            'creator_id': creator_context.creator_id,
            'creator_type': creator_context.creator_type.value,
            'creator_tier': creator_context.creator_tier.value,
            'revenue_tier': creator_context.revenue_tier,
            'engagement_score': creator_context.engagement_score,
            'content_formats': creator_context.content_formats,
            'collaboration_active': creator_context.collaboration_active,
            'gamification_level': creator_context.gamification_level,
            'seo_score': creator_context.seo_score,
            'distribution_channels': creator_context.distribution_channels,
            'processing_timestamp': datetime.now().isoformat()
        })
        
        return enriched
    
    async def _determine_alert_routing(
        self, 
        enriched_alert: Dict[str, Any], 
        creator_context: CreatorContext
    ) -> Dict[str, Any]:
        """Determine intelligent routing based on creator context"""
        routing = {
            'priority': self._calculate_priority(creator_context),
            'response_time_sla': self._get_response_time_sla(creator_context.creator_tier),
            'escalation_path': self._get_escalation_path(creator_context),
            'notification_channels': self._get_notification_channels(creator_context),
            'specialized_handlers': []
        }
        
        # Add specialized handlers based on alert type and creator context
        alert_type = enriched_alert.get('type', '')
        
        if 'revenue' in alert_type.lower() or 'monetization' in alert_type.lower():
            routing['specialized_handlers'].append('monetization_intelligence')
        
        if 'collaboration' in alert_type.lower() and creator_context.collaboration_active:
            routing['specialized_handlers'].append('collaboration_system')
        
        if 'seo' in alert_type.lower() or 'search' in alert_type.lower():
            routing['specialized_handlers'].append('seo_tracker')
        
        if 'distribution' in alert_type.lower():
            routing['specialized_handlers'].append('distribution_manager')
        
        if 'gamification' in alert_type.lower():
            routing['specialized_handlers'].append('gamification_monitor')
        
        if 'content' in alert_type.lower() and 'protection' in alert_type.lower():
            routing['specialized_handlers'].append('content_protection_engine')
        
        return routing
    
    def _calculate_priority(self, creator_context: CreatorContext) -> int:
        """Calculate alert priority based on creator context"""
        base_priority = {
            CreatorTier.PREMIUM: 10,
            CreatorTier.PROFESSIONAL: 7,
            CreatorTier.STANDARD: 5,
            CreatorTier.STARTER: 3
        }.get(creator_context.creator_tier, 1)
        
        # Adjust based on engagement and revenue
        engagement_boost = min(int(creator_context.engagement_score / 10), 5)
        
        return min(base_priority + engagement_boost, 15)
    
    def _get_response_time_sla(self, creator_tier: CreatorTier) -> int:
        """Get response time SLA based on creator tier"""
        return {
            CreatorTier.PREMIUM: self.config.premium_creator_response_time,
            CreatorTier.PROFESSIONAL: self.config.professional_creator_response_time,
            CreatorTier.STANDARD: self.config.standard_creator_response_time,
            CreatorTier.STARTER: 600  # 10 minutes for starter tier
        }.get(creator_tier, 600)
    
    def _get_escalation_path(self, creator_context: CreatorContext) -> List[str]:
        """Get escalation path based on creator context"""
        if creator_context.creator_tier == CreatorTier.PREMIUM:
            return ['support_premium', 'manager_premium', 'executive']
        elif creator_context.creator_tier == CreatorTier.PROFESSIONAL:
            return ['support_professional', 'manager_professional']
        else:
            return ['support_general', 'manager_general']
    
    def _get_notification_channels(self, creator_context: CreatorContext) -> List[str]:
        """Get notification channels based on creator context"""
        channels = ['email', 'dashboard']
        
        if creator_context.creator_tier in [CreatorTier.PREMIUM, CreatorTier.PROFESSIONAL]:
            channels.extend(['sms', 'slack'])
        
        if creator_context.creator_tier == CreatorTier.PREMIUM:
            channels.append('phone')
        
        return channels
    
    async def _route_alert_to_managers(
        self, 
        enriched_alert: Dict[str, Any], 
        routing_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route alert to appropriate managers based on routing information"""
        results = []
        
        # Always process through intelligent manager
        intelligent_result = await self.intelligent_manager.process_alert(enriched_alert)
        results.append(('intelligent_manager', intelligent_result))
        
        # Route to appropriate specialized managers
        alert_category = enriched_alert.get('category', '').lower()
        
        if 'business' in alert_category:
            business_result = await self.business_manager.process_alert(enriched_alert)
            results.append(('business_manager', business_result))
        
        if 'technical' in alert_category:
            technical_result = await self.technical_manager.process_alert(enriched_alert)
            results.append(('technical_manager', technical_result))
        
        if 'ai' in alert_category or 'ml' in alert_category:
            ai_result = await self.ai_manager.process_alert(enriched_alert)
            results.append(('ai_manager', ai_result))
        
        # Process through specialized handlers (when available)
        specialized_handlers = routing_info.get('specialized_handlers', [])
        for handler in specialized_handlers:
            if hasattr(self, handler) and getattr(self, handler) is not None:
                handler_result = await getattr(self, handler).process_alert(enriched_alert)
                results.append((handler, handler_result))
        
        return {
            'alert_id': enriched_alert.get('id', 'unknown'),
            'processing_results': results,
            'routing_info': routing_info,
            'status': 'processed',
            'timestamp': datetime.now().isoformat()
        }
    
    async def _update_processing_metrics(
        self, 
        creator_context: CreatorContext, 
        start_time: datetime
    ) -> None:
        """Update processing metrics"""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        self.metrics['total_alerts_processed'] += 1
        self.metrics['response_times'].append(processing_time)
        
        # Keep only last 1000 response times for memory efficiency
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]
        
        # Update creator type metrics
        creator_type = creator_context.creator_type.value
        if creator_type not in self.metrics['alerts_by_creator_type']:
            self.metrics['alerts_by_creator_type'][creator_type] = 0
        self.metrics['alerts_by_creator_type'][creator_type] += 1
        
        # Update tier metrics
        creator_tier = creator_context.creator_tier.value
        if creator_tier not in self.metrics['alerts_by_tier']:
            self.metrics['alerts_by_tier'][creator_tier] = 0
        self.metrics['alerts_by_tier'][creator_tier] += 1
    
    async def _metrics_collector(self) -> None:
        """Background task for metrics collection"""
        while not self._shutdown_event.is_set():
            try:
                # Collect and log metrics periodically
                if self.metrics['total_alerts_processed'] > 0:
                    avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
                    uptime = (datetime.now() - self.metrics['uptime_start']).total_seconds()
                    
                    logger.info(f"Alerts System Metrics - "
                              f"Total: {self.metrics['total_alerts_processed']}, "
                              f"Avg Response: {avg_response_time:.2f}s, "
                              f"Errors: {self.metrics['error_count']}, "
                              f"Uptime: {uptime:.0f}s")
                
                await asyncio.sleep(self.config.metrics_collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collector: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _health_monitor(self) -> None:
        """Background task for health monitoring"""
        while not self._shutdown_event.is_set():
            try:
                # Perform health checks on all components
                health_status = await self._perform_health_check()
                
                if health_status['overall_status'] != 'healthy':
                    logger.warning(f"Health check failed: {health_status}")
                
                await asyncio.sleep(30)  # Health check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(60)
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            'overall_status': 'healthy',
            'components': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Check core components
        components = [
            ('intelligent_manager', self.intelligent_manager),
            ('coordinator', self.coordinator),
            ('business_manager', self.business_manager),
            ('technical_manager', self.technical_manager),
            ('ai_manager', self.ai_manager)
        ]
        
        for component_name, component in components:
            try:
                if hasattr(component, 'health_check'):
                    component_health = await component.health_check()
                else:
                    component_health = 'healthy'  # Assume healthy if no health check method
                
                health_status['components'][component_name] = component_health
                
                if component_health != 'healthy':
                    health_status['overall_status'] = 'degraded'
                    
            except Exception as e:
                health_status['components'][component_name] = f'error: {str(e)}'
                health_status['overall_status'] = 'unhealthy'
        
        return health_status
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        metrics = self.metrics.copy()
        
        if metrics['response_times']:
            metrics['avg_response_time'] = sum(metrics['response_times']) / len(metrics['response_times'])
            metrics['max_response_time'] = max(metrics['response_times'])
            metrics['min_response_time'] = min(metrics['response_times'])
        
        metrics['uptime_seconds'] = (datetime.now() - metrics['uptime_start']).total_seconds()
        metrics['health_status'] = await self._perform_health_check()
        
        return metrics
    
    async def shutdown(self) -> None:
        """Graceful shutdown of the alerts system"""
        logger.info("Starting graceful shutdown of Alerts System Orchestrator...")
        
        self._shutdown_event.set()
        self.is_running = False
        
        # Shutdown all components
        components = [
            self.intelligent_manager,
            self.coordinator,
            self.business_manager,
            self.technical_manager,
            self.ai_manager
        ]
        
        for component in components:
            try:
                if hasattr(component, 'shutdown'):
                    await component.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down component {component}: {e}")
        
        logger.info("Alerts System Orchestrator shutdown complete")


# Factory function for easy instantiation
def create_alerts_system_orchestrator(
    config: Optional[AlertsSystemConfig] = None
) -> AlertsSystemOrchestrator:
    """
    Factory function to create a properly configured AlertsSystemOrchestrator
    
    Args:
        config: Optional configuration, uses defaults if not provided
        
    Returns:
        Configured AlertsSystemOrchestrator instance
    """
    if config is None:
        config = AlertsSystemConfig()
    
    return AlertsSystemOrchestrator(config)


# Context manager for proper lifecycle management
@asynccontextmanager
async def alerts_system_context(
    config: Optional[AlertsSystemConfig] = None
):
    """
    Async context manager for alerts system lifecycle management
    
    Usage:
        async with alerts_system_context() as orchestrator:
            # Use orchestrator
            result = await orchestrator.process_creator_alert(alert_data, creator_context)
    """
    orchestrator = create_alerts_system_orchestrator(config)
    
    try:
        await orchestrator.initialize()
        yield orchestrator
    finally:
        await orchestrator.shutdown()


# Export main classes and functions
__all__ = [
    'AlertsSystemOrchestrator',
    'AlertsSystemConfig', 
    'CreatorContext',
    'CreatorType',
    'CreatorTier',
    'create_alerts_system_orchestrator',
    'alerts_system_context'
]