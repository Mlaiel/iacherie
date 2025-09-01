"""🚨 Unified Alert Coordinator - Central Intelligent Alert System
===============================================================

Central coordinator that unifies Business, Technical, and AI alerts into a
comprehensive intelligent alert management system for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

from .intelligent_alert_manager import IntelligentAlertManager, AlertCategory, AlertSeverity, IntelligentAlert
from .business_alerts import BusinessAlertManager, BusinessMetrics
from .technical_alerts import TechnicalAlertManager, TechnicalMetrics, SecurityEvent
from .ai_alerts import AIAlertManager, ModelMetrics

logger = logging.getLogger(__name__)


class SystemHealthStatus(Enum):
    """
Overall system health status"""

    HEALTHY = "healthy"
    WARNING = "warning" 
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class UnifiedAlertSummary:
    """Unified alert summary across all categories"""
    timestamp: datetime
    system_health: SystemHealthStatus
    total_active_alerts: int
    alerts_by_category: Dict[str, int]
    alerts_by_severity: Dict[str, int]
    business_health: Dict[str, Any]
    technical_health: Dict[str, Any]
    ai_health: Dict[str, Any]
    trending_issues: List[str]
    recommendations: List[str]


class AlertCoordinator:
    """
    Unified Alert Coordinator - Central Intelligence for Alert Management
    
    Features:
    - Coordinates Business, Technical, and AI alert managers
    - Provides unified alert correlation and prioritization
    - Manages cross-category alert relationships
    - Offers comprehensive system health assessment
    - Handles escalation coordination
    - Provides unified reporting and dashboards
    """
    
    def __init__(self):
        """
Initialize the unified alert coordinator"""
        # Initialize core alert manager
        self.alert_manager = IntelligentAlertManager()
        
        # Initialize category-specific managers
        self.business_manager = BusinessAlertManager(self.alert_manager)
        self.technical_manager = TechnicalAlertManager(self.alert_manager)
        self.ai_manager = AIAlertManager(self.alert_manager)
        
        # Coordinator state
        self.last_evaluation = {}
        self.system_trends = []
        self.cross_category_correlations = []
        
        # Unified thresholds for system health
        self.system_health_thresholds = {
            "emergency_alert_count": 1,      # Any emergency alert = emergency status
            "critical_alert_count": 3,       # 3+ critical alerts = critical status
            "warning_alert_count": 10,       # 10+ warning alerts = warning status
            "correlation_significance": 0.7,  # Correlation threshold
        }
        
        logger.info("AlertCoordinator initialized with unified alert management")
    
    async def evaluate_all_metrics(self, 
                                 business_metrics: Optional[BusinessMetrics] = None,
                                 technical_metrics: Optional[TechnicalMetrics] = None,
                                 ai_metrics: Optional[List[ModelMetrics]] = None) -> UnifiedAlertSummary:
        """
        Evaluate all metrics across categories and provide unified alert management
        """
        try:
            start_time = datetime.utcnow()
            all_triggered_alerts = []
            
            # Evaluate business alerts
            business_alerts = []
            if business_metrics:
                business_alerts = await self.business_manager.evaluate_business_metrics(business_metrics)
                all_triggered_alerts.extend(business_alerts)
                logger.debug(f"Business evaluation: {len(business_alerts)} alerts")
            
            # Evaluate technical alerts
            technical_alerts = []
            if technical_metrics:
                technical_alerts = await self.technical_manager.evaluate_technical_metrics(technical_metrics)
                all_triggered_alerts.extend(technical_alerts)
                logger.debug(f"Technical evaluation: {len(technical_alerts)} alerts")
            
            # Evaluate AI alerts
            ai_alerts = []
            if ai_metrics:
                for model_metrics in ai_metrics:
                    model_alerts = await self.ai_manager.evaluate_model_metrics(model_metrics)
                    ai_alerts.extend(model_alerts)
                all_triggered_alerts.extend(ai_alerts)
                logger.debug(f"AI evaluation: {len(ai_alerts)} alerts")
            
            # Process cross-category correlations
            correlated_alerts = await self._process_cross_category_correlations(
                business_alerts, technical_alerts, ai_alerts
            )
            
            # Calculate system health
            system_health = await self._calculate_system_health()
            
            # Generate trending issues and recommendations
            trending_issues = await self._identify_trending_issues()
            recommendations = await self._generate_recommendations(system_health, all_triggered_alerts)
            
            # Create unified summary
            summary = await self._create_unified_summary(
                system_health, all_triggered_alerts, trending_issues, recommendations
            )
            
            # Update evaluation history
            self.last_evaluation = {
                "timestamp": start_time,
                "business_metrics": business_metrics,
                "technical_metrics": technical_metrics,
                "ai_metrics": ai_metrics,
                "alerts_count": len(all_triggered_alerts),
                "system_health": system_health
            }
            
            evaluation_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Unified alert evaluation completed in {evaluation_time:.3f}s - "
                       f"{len(all_triggered_alerts)} alerts, system health: {system_health.value}")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in unified alert evaluation: {e}")
            return await self._create_error_summary(str(e))
    
    async def process_security_event(self, event: SecurityEvent) -> List[IntelligentAlert]:
        """Process security event through the technical manager"""
        try:
            return await self.technical_manager.process_security_event(event)
        except Exception as e:
            logger.error(f"Error processing security event: {e}")
            return []
    
    async def process_training_failure(self, model_id: str, model_name: str, 
                                     failure_details: Dict[str, Any]) -> List[IntelligentAlert]:
        """Process AI training failure through the AI manager"""
        try:
            return await self.ai_manager.process_training_failure(model_id, model_name, failure_details)
        except Exception as e:
            logger.error(f"Error processing training failure: {e}")
            return []
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert across all managers"""
        try:
            return await self.alert_manager.acknowledge_alert(alert_id, acknowledged_by)
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str, auto_resolved: bool = False) -> bool:
        """Resolve an alert across all managers"""
        try:
            return await self.alert_manager.resolve_alert(alert_id, auto_resolved)
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False
    
    async def get_active_alerts(self, category: Optional[AlertCategory] = None,
                              severity: Optional[AlertSeverity] = None) -> List[IntelligentAlert]:
        """Get active alerts with optional filtering"""
        try:
            active_alerts = list(self.alert_manager.active_alerts.values())
            
            if category:
                active_alerts = [alert for alert in active_alerts if alert.category == category]
            
            if severity:
                active_alerts = [alert for alert in active_alerts if alert.severity == severity]
            
            # Sort by severity and timestamp
            severity_order = {
                AlertSeverity.EMERGENCY: 0,
                AlertSeverity.CRITICAL: 1,
                AlertSeverity.WARNING: 2,
                AlertSeverity.INFO: 3
            }
            
            active_alerts.sort(key=lambda x: (severity_order[x.severity], x.timestamp), reverse=True)
            
            return active_alerts
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    async def get_alert_history(self, hours: int = 24, 
                              category: Optional[AlertCategory] = None) -> List[IntelligentAlert]:
        """Get alert history with optional filtering"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            history = [
                alert for alert in self.alert_manager.alert_history
                if alert.timestamp >= cutoff_time
            ]
            
            if category:
                history = [alert for alert in history if alert.category == category]
            
            return sorted(history, key=lambda x: x.timestamp, reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting alert history: {e}")
            return []
    
    async def _process_cross_category_correlations(self, 
                                                 business_alerts: List[IntelligentAlert],
                                                 technical_alerts: List[IntelligentAlert],
                                                 ai_alerts: List[IntelligentAlert]) -> List[Dict[str, Any]]:
        """Process correlations between different alert categories"""
        correlations = []
        
        try:
            # Example correlations:
            # 1. Revenue drop + Service down = High correlation
            # 2. AI accuracy drop + Technical performance issues = Medium correlation
            # 3. Security breach + AI model issues = Potential attack
            
            # Check for revenue drop + technical issues
            revenue_alerts = [a for a in business_alerts if "revenue" in a.title.lower()]
            service_alerts = [a for a in technical_alerts if "service" in a.title.lower() or "down" in a.title.lower()]
            
            if revenue_alerts and service_alerts:
                correlation = {
                    "type": "business_technical",
                    "description": "Revenue impact potentially caused by technical issues",
                    "business_alerts": [a.alert_id for a in revenue_alerts],
                    "technical_alerts": [a.alert_id for a in service_alerts],
                    "correlation_score": 0.8,
                    "recommended_action": "Prioritize technical issue resolution to restore revenue"
                }
                correlations.append(correlation)
            
            # Check for AI performance + technical resource issues
            ai_performance_alerts = [a for a in ai_alerts if "accuracy" in a.title.lower() or "drift" in a.title.lower()]
            resource_alerts = [a for a in technical_alerts if "resource" in a.title.lower() or "cpu" in a.title.lower()]
            
            if ai_performance_alerts and resource_alerts:
                correlation = {
                    "type": "ai_technical",
                    "description": "AI model issues potentially caused by resource constraints",
                    "ai_alerts": [a.alert_id for a in ai_performance_alerts],
                    "technical_alerts": [a.alert_id for a in resource_alerts],
                    "correlation_score": 0.7,
                    "recommended_action": "Scale resources and retrain models if necessary"
                }
                correlations.append(correlation)
            
            # Store correlations for trending analysis
            self.cross_category_correlations.extend(correlations)
            
            # Keep only recent correlations
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            self.cross_category_correlations = [
                c for c in self.cross_category_correlations
                if c.get("timestamp", datetime.utcnow()) >= cutoff_time
            ]
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error processing cross-category correlations: {e}")
            return []
    
    async def _calculate_system_health(self) -> SystemHealthStatus:
        """Calculate overall system health status"""
        try:
            active_alerts = self.alert_manager.active_alerts.values()
            
            # Count alerts by severity
            emergency_count = sum(1 for a in active_alerts if a.severity == AlertSeverity.EMERGENCY)
            critical_count = sum(1 for a in active_alerts if a.severity == AlertSeverity.CRITICAL)
            warning_count = sum(1 for a in active_alerts if a.severity == AlertSeverity.WARNING)
            
            # Determine system health based on alert counts
            if emergency_count >= self.system_health_thresholds["emergency_alert_count"]:
                return SystemHealthStatus.EMERGENCY
            elif critical_count >= self.system_health_thresholds["critical_alert_count"]:
                return SystemHealthStatus.CRITICAL
            elif warning_count >= self.system_health_thresholds["warning_alert_count"]:
                return SystemHealthStatus.WARNING
            else:
                return SystemHealthStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"Error calculating system health: {e}")
            return SystemHealthStatus.WARNING
    
    async def _identify_trending_issues(self) -> List[str]:
        """Identify trending issues across the system"""
        trending_issues = []
        
        try:
            # Analyze recent alert patterns
            recent_alerts = [
                alert for alert in self.alert_manager.alert_history
                if alert.timestamp >= datetime.utcnow() - timedelta(hours=6)
            ]
            
            # Count alert types
            alert_type_counts = {}
            for alert in recent_alerts:
                alert_type = alert.alert_type.value
                alert_type_counts[alert_type] = alert_type_counts.get(alert_type, 0) + 1
            
            # Identify trends
            for alert_type, count in alert_type_counts.items():
                if count >= 3:  # 3+ alerts of same type in 6 hours
                    trending_issues.append(f"Recurring {alert_type.replace('_', ' ')} issues ({count} occurrences)")
            
            # Check for cross-category trends
            if len(self.cross_category_correlations) >= 2:
                trending_issues.append("Multiple cross-category alert correlations detected")
            
            # Check for escalation trends
            escalated_alerts = [a for a in recent_alerts if a.escalation_level > 0]
            if len(escalated_alerts) >= 2:
                trending_issues.append(f"Alert escalation trend: {len(escalated_alerts)} alerts escalated")
            
            return trending_issues
            
        except Exception as e:
            logger.error(f"Error identifying trending issues: {e}")
            return ["Error analyzing trends"]
    
    async def _generate_recommendations(self, system_health: SystemHealthStatus, 
                                      alerts: List[IntelligentAlert]) -> List[str]:
        """Generate actionable recommendations based on system state"""
        recommendations = []
        
        try:
            if system_health == SystemHealthStatus.EMERGENCY:
                recommendations.extend([
                    "🚨 EMERGENCY: Activate incident response team immediately",
                    "📞 Contact on-call engineers and management",
                    "🔍 Focus on resolving emergency-level alerts first",
                    "📊 Prepare for potential customer communication"
                ])
            
            elif system_health == SystemHealthStatus.CRITICAL:
                recommendations.extend([
                    "🔴 CRITICAL: Prioritize critical alert resolution",
                    "👥 Escalate to senior engineering team",
                    "📈 Monitor system closely for degradation",
                    "⚡ Consider scaling resources if applicable"
                ])
            
            elif system_health == SystemHealthStatus.WARNING:
                recommendations.extend([
                    "🟡 WARNING: Review and address warning alerts",
                    "📊 Monitor trends to prevent escalation",
                    "🔧 Perform preventive maintenance if needed"
                ])
            
            # Category-specific recommendations
            business_alerts = [a for a in alerts if a.category == AlertCategory.BUSINESS]
            technical_alerts = [a for a in alerts if a.category == AlertCategory.TECHNICAL]
            ai_alerts = [a for a in alerts if a.category == AlertCategory.AI_ML]
            
            if business_alerts:
                recommendations.append(f"💰 Business Impact: {len(business_alerts)} business alerts require attention")
                
            if technical_alerts:
                recommendations.append(f"🔧 Technical Issues: {len(technical_alerts)} infrastructure/security alerts need resolution")
                
            if ai_alerts:
                recommendations.append(f"🤖 AI/ML Health: {len(ai_alerts)} model alerts require review")
            
            # Cross-category recommendations
            if len(self.cross_category_correlations) > 0:
                recommendations.append("🔗 Review cross-category alert correlations for root cause analysis")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"]
    
    async def _create_unified_summary(self, system_health: SystemHealthStatus,
                                    alerts: List[IntelligentAlert],
                                    trending_issues: List[str],
                                    recommendations: List[str]) -> UnifiedAlertSummary:
        """Create comprehensive unified alert summary"""
        try:
            # Count active alerts
            active_alerts = list(self.alert_manager.active_alerts.values())
            
            # Categorize alerts
            alerts_by_category = {}
            alerts_by_severity = {}
            
            for alert in active_alerts:
                # By category
                category = alert.category.value
                alerts_by_category[category] = alerts_by_category.get(category, 0) + 1
                
                # By severity
                severity = alert.severity.value
                alerts_by_severity[severity] = alerts_by_severity.get(severity, 0) + 1
            
            # Get subsystem health
            business_health = await self.business_manager.get_business_alert_summary()
            technical_health = await self.technical_manager.get_technical_alert_summary()
            ai_health = await self.ai_manager.get_ai_alert_summary()
            
            return UnifiedAlertSummary(
                timestamp=datetime.utcnow(),
                system_health=system_health,
                total_active_alerts=len(active_alerts),
                alerts_by_category=alerts_by_category,
                alerts_by_severity=alerts_by_severity,
                business_health=business_health,
                technical_health=technical_health,
                ai_health=ai_health,
                trending_issues=trending_issues,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error creating unified summary: {e}")
            return await self._create_error_summary(str(e))
    
    async def _create_error_summary(self, error_message: str) -> UnifiedAlertSummary:
        """Create error summary when evaluation fails"""
        return UnifiedAlertSummary(
            timestamp=datetime.utcnow(),
            system_health=SystemHealthStatus.WARNING,
            total_active_alerts=0,
            alerts_by_category={"error": 1},
            alerts_by_severity={"warning": 1},
            business_health={"error": error_message},
            technical_health={"error": error_message},
            ai_health={"error": error_message},
            trending_issues=[f"Alert system error: {error_message}"],
            recommendations=["🔧 Investigate alert system error", "📞 Contact platform administrators"]
        )
    
    async def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive system status across all categories"""
        try:
            # Get unified summary with current state
            current_summary = await self._create_unified_summary(
                await self._calculate_system_health(),
                [],  # Current alerts handled by summary
                await self._identify_trending_issues(),
                []   # Recommendations handled by summary
            )
            
            # Get detailed statistics
            alert_stats = await self.alert_manager.get_alert_statistics()
            
            # Get subsystem summaries
            business_summary = await self.business_manager.get_business_alert_summary()
            technical_summary = await self.technical_manager.get_technical_alert_summary()
            ai_summary = await self.ai_manager.get_ai_alert_summary()
            
            return {
                "system_overview": {
                    "timestamp": current_summary.timestamp.isoformat(),
                    "system_health": current_summary.system_health.value,
                    "total_active_alerts": current_summary.total_active_alerts,
                    "alerts_by_category": current_summary.alerts_by_category,
                    "alerts_by_severity": current_summary.alerts_by_severity
                },
                "alert_statistics": alert_stats,
                "subsystem_health": {
                    "business": business_summary,
                    "technical": technical_summary,
                    "ai_ml": ai_summary
                },
                "trending_issues": current_summary.trending_issues,
                "recommendations": current_summary.recommendations,
                "cross_category_correlations": len(self.cross_category_correlations),
                "last_evaluation": self.last_evaluation.get("timestamp"),
                "coordinator_status": "operational"
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive status: {e}")
            return {
                "error": str(e),
                "coordinator_status": "error",
                "timestamp": datetime.utcnow().isoformat()
            }


# Create global instance for easy access
alert_coordinator = AlertCoordinator()


# Export the main classes and global instance
__all__ = [
    "AlertCoordinator", 
    "UnifiedAlertSummary", 
    "SystemHealthStatus",
    "alert_coordinator"  # Global instance
]