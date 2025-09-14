"""
Monitoring System - Core Module
===============================

Central monitoring system for the Ainflue platform providing
comprehensive observability, alerting, and performance tracking.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

__version__ = "3.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Core monitoring components - Updated for reorganized structure
try:
    from .core.business_monitoring import BusinessMonitoringCore
    from .dashboards.production_dashboard import ProductionDashboard
    from .core.enterprise_orchestrator import (
        enterprise_orchestrator,
        get_platform_status,
        get_enterprise_insights,
        get_dashboard_data,
        add_enterprise_alert_handler
    )
    from .config import monitoring_config, get_monitoring_config
    
    class MonitoringSystem:
        """Main monitoring system orchestrator with enterprise capabilities"""
        
        def __init__(self):
            self.business_monitoring = BusinessMonitoringCore()
            self.dashboard = ProductionDashboard()
            self.enterprise_orchestrator = enterprise_orchestrator
        
        def get_system_status(self) -> Dict[str, Any]:
            """Get overall system status"""
            return {
                "status": "operational",
                "version": __version__,
                "components": {
                    "business_monitoring": "active",
                    "dashboard": "active",
                    "enterprise_orchestrator": "active",
                    "audio_processing": "active",
                    "content_protection": "active",
                    "monetization": "active",
                    "collaboration": "active",
                    "gamification": "active",
                    "seo_optimization": "active",
                    "distribution": "active",
                    "analytics": "active"
                }
            }
        
        async def get_comprehensive_status(self) -> Dict[str, Any]:
            """Get comprehensive enterprise status with AI insights"""
            try:
                platform_health = await get_platform_status()
                enterprise_insights = await get_enterprise_insights()
                
                return {
                    "version": __version__,
                    "platform_health": platform_health,
                    "ai_insights": {
                        "performance_score": enterprise_insights.overall_performance_score,
                        "recommendations_count": len(enterprise_insights.recommendations),
                        "anomalies_count": len(enterprise_insights.anomalies_detected),
                        "user_experience_score": enterprise_insights.user_experience_score,
                        "business_impact_score": enterprise_insights.business_impact_score
                    },
                    "capabilities": {
                        "audio_processing": "DEMUCS/Spleeter, EBU R128, ITU-R, Real-time Analytics",
                        "content_protection": "AI Fingerprinting, Copyright Detection, DMCA Compliance",
                        "monetization": "Multi-Gateway, Fraud Detection, Revenue Optimization",
                        "collaboration": "AI Matching, ROI Tracking, Trust Scoring",
                        "gamification": "Engagement Optimization, Social Proof, Viral Mechanics",
                        "seo_optimization": "Multi-Platform Ranking, Hashtag Intelligence",
                        "distribution": "Cross-Platform Sync, CDN Optimization",
                        "analytics": "Real-time Insights, Predictive Analytics, Competitive Intelligence"
                    }
                }
            except Exception as e:
                logger.error(f"Failed to get comprehensive status: {e}")
                return self.get_system_status()
        
        async def start_enterprise_monitoring(self):
            """Start enterprise-level continuous monitoring"""
            await self.enterprise_orchestrator.start_continuous_monitoring()
        
        def add_alert_handler(self, handler):
            """Add enterprise alert handler"""
            add_enterprise_alert_handler(handler)
    
    __all__ = [
        'MonitoringSystem',
        'BusinessMonitoringCore',
        'ProductionDashboard',
        'enterprise_orchestrator',
        'get_platform_status',
        'get_enterprise_insights',
        'get_dashboard_data',
        'add_enterprise_alert_handler',
        'monitoring_config',
        'get_monitoring_config'
    ]
    
except ImportError as e:
    logger.warning(f"Some monitoring components not available: {e}")
    
    class MonitoringSystem:
        """Fallback monitoring system"""
        
        def get_system_status(self) -> Dict[str, Any]:
            return {
                "status": "limited",
                "version": __version__,
                "error": "Some components unavailable"
            }
        
        async def get_comprehensive_status(self) -> Dict[str, Any]:
            return self.get_system_status()
    
    __all__ = ['MonitoringSystem']

# Export main system
monitoring_system = MonitoringSystem()