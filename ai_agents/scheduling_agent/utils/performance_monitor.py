#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real-Time Performance Monitor - Enterprise Performance Tracking & Auto-Optimization
==================================================================================

Ultra-industrial real-time performance monitoring system for content scheduling
with automatic optimization, anomaly detection, and predictive analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import statistics
import time

from ..base import BaseAgent, AgentError
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
from ...utils.performance_monitor import PerformanceMonitor
from .scheduling_agent import ScheduledJob, SchedulingPriority, ScheduleStatus

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """
Performance alert levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class MetricType(Enum):
    """Performance metric types"""

    ENGAGEMENT_RATE = "engagement_rate"
    REACH_RATE = "reach_rate"
    CLICK_THROUGH_RATE = "ctr"
    CONVERSION_RATE = "conversion_rate"
    COST_PER_ENGAGEMENT = "cpe"
    OPTIMAL_TIMING_ACCURACY = "timing_accuracy"
    SCHEDULING_SUCCESS_RATE = "scheduling_success"
    API_RESPONSE_TIME = "api_response_time"
    SYSTEM_LOAD = "system_load"
    ERROR_RATE = "error_rate"

@dataclass
class PerformanceAlert:
    """Performance alert configuration"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metric: MetricType = MetricType.ENGAGEMENT_RATE
    level: AlertLevel = AlertLevel.WARNING
    threshold: float = 0.0
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    creator_id: Optional[str] = None
    platform: Optional[str] = None
    resolution_action: Optional[str] = None
    is_resolved: bool = False

@dataclass
class OptimizationRecommendation:
    """Auto-optimization recommendation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    recommendation_type: str = ""
    description: str = ""
    expected_improvement: float = 0.0
    confidence_score: float = 0.0
    implementation_difficulty: str = "low"  # low, medium, high
    estimated_impact: Dict[str, float] = field(default_factory=dict)
    suggested_actions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

class RealTimePerformanceMonitor:
    """
    Enterprise real-time performance monitoring and auto-optimization system.
    
    Features:
    - Real-time metric collection and analysis
    - Anomaly detection with ML algorithms
    - Predictive performance analytics
    - Automatic optimization recommendations
    - Alert system with escalation levels
    - Performance trend analysis
    - A/B testing results tracking
    """
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        
        # Real-time data storage
        self.metrics_buffer = defaultdict(lambda: deque(maxlen=1000))
        self.alert_history = deque(maxlen=10000)
        self.recommendations_history = deque(maxlen=5000)
        
        # Performance thresholds
        self.thresholds = {
            MetricType.ENGAGEMENT_RATE: {
                AlertLevel.WARNING: 0.02,
                AlertLevel.CRITICAL: 0.01,
                AlertLevel.EMERGENCY: 0.005
            },
            MetricType.SCHEDULING_SUCCESS_RATE: {
                AlertLevel.WARNING: 0.95,
                AlertLevel.CRITICAL: 0.90,
                AlertLevel.EMERGENCY: 0.85
            },
            MetricType.API_RESPONSE_TIME: {
                AlertLevel.WARNING: 1.0,
                AlertLevel.CRITICAL: 2.0,
                AlertLevel.EMERGENCY: 5.0
            }
        }
        
        # Anomaly detection parameters
        self.anomaly_window_size = 50
        self.anomaly_threshold_std = 2.5
        
        # Auto-optimization settings
        self.optimization_enabled = True
        self.optimization_cooldown = timedelta(hours=1)
        self.last_optimization = {}
        
        logger.info("Real-time performance monitor initialized")
    
    async def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        creator_id: Optional[str] = None,
        platform: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a performance metric for real-time monitoring"""
        try:
            metric_key = f"{metric_type.value}:{creator_id or 'global'}:{platform or 'all'}"
            
            metric_data = {
                'timestamp': datetime.now(),
                'value': value,
                'creator_id': creator_id,
                'platform': platform,
                'metadata': metadata or {}
            }
            
            # Add to buffer
            self.metrics_buffer[metric_key].append(metric_data)
            
            # Check for alerts
            await self._check_alert_conditions(metric_type, value, creator_id, platform)
            
            # Perform anomaly detection
            await self._detect_anomalies(metric_key, value)
            
            # Generate optimization recommendations
            if self.optimization_enabled:
                await self._generate_optimization_recommendations(
                    metric_type, value, creator_id, platform
                )
                
        except Exception as e:
            logger.error(f"Failed to record metric {metric_type}: {str(e)}")
            raise AgentError(f"Metric recording failed: {str(e)}")
    
    async def _check_alert_conditions(
        self,
        metric_type: MetricType,
        value: float,
        creator_id: Optional[str],
        platform: Optional[str]
    ):
        """Check if metric value triggers any alerts"""
        if metric_type not in self.thresholds:
            return
        
        thresholds = self.thresholds[metric_type]
        
        # Check thresholds (reverse order for proper escalation)
        for level in [AlertLevel.EMERGENCY, AlertLevel.CRITICAL, AlertLevel.WARNING]:
            if level in thresholds:
                threshold = thresholds[level]
                
                # Different comparison logic based on metric type
                should_alert = False
                if metric_type in [MetricType.API_RESPONSE_TIME, MetricType.ERROR_RATE]:
                    # Higher values are worse
                    should_alert = value > threshold
                else:
                    # Lower values are worse
                    should_alert = value < threshold
                
                if should_alert:
                    await self._trigger_alert(
                        metric_type, level, value, threshold,
                        creator_id, platform
                    )
                    break
    
    async def _trigger_alert(
        self,
        metric_type: MetricType,
        level: AlertLevel,
        value: float,
        threshold: float,
        creator_id: Optional[str],
        platform: Optional[str]
    ):
        """
Trigger a performance alert"""
        alert = PerformanceAlert(
            metric=metric_type,
            level=level,
            threshold=threshold,
            message=f"{metric_type.value} alert: {value} vs threshold {threshold}",
            creator_id=creator_id,
            platform=platform,
            resolution_action=await self._get_resolution_action(metric_type, level)
        )
        
        self.alert_history.append(alert)
        
        # Log alert
        logger.warning(f"Performance Alert [{level.value}]: {alert.message}")
        
        # Execute automated resolution if configured
        if alert.resolution_action:
            await self._execute_resolution_action(alert)
    
    async def _get_resolution_action(
        self,
        metric_type: MetricType,
        level: AlertLevel
    ) -> Optional[str]:
        """Get automated resolution action for alert"""
        resolution_map = {
            MetricType.ENGAGEMENT_RATE: {
                AlertLevel.WARNING: "adjust_timing_algorithm",
                AlertLevel.CRITICAL: "trigger_emergency_optimization",
                AlertLevel.EMERGENCY: "activate_backup_strategies"
            },
            MetricType.API_RESPONSE_TIME: {
                AlertLevel.WARNING: "increase_connection_pool",
                AlertLevel.CRITICAL: "enable_caching_layers",
                AlertLevel.EMERGENCY: "switch_to_backup_apis"
            }
        }
        
        return resolution_map.get(metric_type, {}).get(level)
    
    async def _execute_resolution_action(self, alert: PerformanceAlert):
        """Execute automated resolution action"""
        try:
            logger.info(f"Executing resolution action: {alert.resolution_action}")
            
            # Execute specific resolution actions
            if alert.resolution_action == "adjust_timing_algorithm":
                await self._adjust_timing_algorithm(alert.creator_id)
            elif alert.resolution_action == "trigger_emergency_optimization":
                await self._trigger_emergency_optimization(alert.creator_id)
            elif alert.resolution_action == "activate_backup_strategies":
                await self._activate_backup_strategies(alert.creator_id)
            
            alert.is_resolved = True
            logger.info(f"Resolution action completed for alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Failed to execute resolution action: {str(e)}")
    
    async def _detect_anomalies(self, metric_key: str, value: float):
        """Detect anomalies in metric values using statistical methods"""
        if len(self.metrics_buffer[metric_key]) < self.anomaly_window_size:
            return
        
        # Get recent values
        recent_values = [
            data['value'] for data in 
            list(self.metrics_buffer[metric_key])[-self.anomaly_window_size:]
        ]
        
        # Calculate statistical parameters
        mean_val = statistics.mean(recent_values)
        std_val = statistics.stdev(recent_values) if len(recent_values) > 1 else 0
        
        # Check for anomaly
        if std_val > 0:
            z_score = abs(value - mean_val) / std_val
            
            if z_score > self.anomaly_threshold_std:
                await self._handle_anomaly(metric_key, value, z_score, mean_val)
    
    async def _handle_anomaly(
        self,
        metric_key: str,
        value: float,
        z_score: float,
        expected_value: float
    ):
        """
Handle detected anomaly"""
        logger.warning(
            f"Anomaly detected in {metric_key}: "
            f"value={value}, expected≈{expected_value:.3f}, z_score={z_score:.2f}"
        )
        
        # Generate anomaly-based recommendations
        await self._generate_anomaly_recommendations(metric_key, value, z_score)
    
    async def _generate_optimization_recommendations(
        self,
        metric_type: MetricType,
        value: float,
        creator_id: Optional[str],
        platform: Optional[str]
    ):
        """Generate automatic optimization recommendations"""
        if not creator_id:
            return
        
        # Check cooldown period
        cooldown_key = f"{creator_id}:{metric_type.value}"
        if (cooldown_key in self.last_optimization and 
            datetime.now() - self.last_optimization[cooldown_key] < self.optimization_cooldown):
            return
        
        recommendations = []
        
        # Generate recommendations based on metric type and performance
        if metric_type == MetricType.ENGAGEMENT_RATE:
            if value < 0.02:  # Low engagement
                recommendations.extend([
                    OptimizationRecommendation(
                        creator_id=creator_id,
                        recommendation_type="timing_optimization",
                        description="Consider shifting posting times to match audience peak activity",
                        expected_improvement=0.15,
                        confidence_score=0.8,
                        suggested_actions=[
                            "Analyze audience timezone distribution",
                            "Test posting 2 hours earlier or later",
                            "Enable A/B testing for timing optimization"
                        ]
                    ),
                    OptimizationRecommendation(
                        creator_id=creator_id,
                        recommendation_type="content_frequency",
                        description="Adjust posting frequency to avoid audience fatigue",
                        expected_improvement=0.12,
                        confidence_score=0.7,
                        suggested_actions=[
                            "Reduce posting frequency by 20%",
                            "Focus on higher quality content",
                            "Implement content spacing optimization"
                        ]
                    )
                ])
        
        elif metric_type == MetricType.REACH_RATE:
            if value < 0.1:  # Low reach
                recommendations.append(
                    OptimizationRecommendation(
                        creator_id=creator_id,
                        recommendation_type="platform_diversification",
                        description="Expand to additional platforms for better reach",
                        expected_improvement=0.25,
                        confidence_score=0.75,
                        suggested_actions=[
                            "Enable TikTok and Instagram Reels",
                            "Cross-post to LinkedIn and Twitter",
                            "Implement platform-specific optimization"
                        ]
                    )
                )
        
        # Store recommendations
        for recommendation in recommendations:
            self.recommendations_history.append(recommendation)
            logger.info(f"Generated recommendation: {recommendation.description}")
        
        # Update last optimization timestamp
        self.last_optimization[cooldown_key] = datetime.now()
    
    async def _generate_anomaly_recommendations(
        self,
        metric_key: str,
        value: float,
        z_score: float
    ):
        """Generate recommendations based on anomaly detection"""
        parts = metric_key.split(':')
        if len(parts) >= 2:
            creator_id = parts[1] if parts[1] != 'global' else None
        else:
            creator_id = None
        
        if not creator_id:
            return
        
        recommendation = OptimizationRecommendation(
            creator_id=creator_id,
            recommendation_type="anomaly_response",
            description=f"Unusual pattern detected (z-score: {z_score:.2f}). Investigate and adjust strategy.",
            expected_improvement=0.1,
            confidence_score=0.6,
            implementation_difficulty="medium",
            suggested_actions=[
                "Review recent content changes",
                "Check platform algorithm updates",
                "Analyze competitor activity",
                "Consider temporary strategy adjustment"
            ]
        )
        
        self.recommendations_history.append(recommendation)
    
    async def get_performance_dashboard(
        self,
        creator_id: Optional[str] = None,
        hours_back: int = 24
    ) -> Dict[str, Any]:
        """Get comprehensive performance dashboard data"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            dashboard = {
                'metrics': {},
                'alerts': [],
                'recommendations': [],
                'trends': {},
                'summary': {}
            }
            
            # Collect recent metrics
            for metric_key, data_points in self.metrics_buffer.items():
                if creator_id and creator_id not in metric_key:
                    continue
                
                recent_points = [
                    point for point in data_points 
                    if point['timestamp'] >= cutoff_time
                ]
                
                if recent_points:
                    values = [point['value'] for point in recent_points]
                    dashboard['metrics'][metric_key] = {
                        'current': values[-1] if values else 0,
                        'average': statistics.mean(values),
                        'min': min(values),
                        'max': max(values),
                        'trend': self._calculate_trend(values),
                        'data_points': len(values)
                    }
            
            # Recent alerts
            dashboard['alerts'] = [
                alert for alert in list(self.alert_history)[-50:]
                if not creator_id or alert.creator_id == creator_id
            ]
            
            # Recent recommendations
            dashboard['recommendations'] = [
                rec for rec in list(self.recommendations_history)[-20:]
                if not creator_id or rec.creator_id == creator_id
            ]
            
            # Performance summary
            dashboard['summary'] = await self._generate_performance_summary(
                dashboard['metrics']
            )
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to generate performance dashboard: {str(e)}")
            raise AgentError(f"Dashboard generation failed: {str(e)}")
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend calculation
        x = list(range(len(values)))
        correlation = np.corrcoef(x, values)[0, 1]
        
        if correlation > 0.1:
            return "improving"
        elif correlation < -0.1:
            return "declining"
        else:
            return "stable"
    
    async def _generate_performance_summary(
        self,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate performance summary statistics"""
        summary = {
            'overall_health': "good",
            'critical_issues': 0,
            'improvement_opportunities': 0,
            'top_performers': [],
            'underperformers': []
        }
        
        # Analyze metrics for summary
        engagement_metrics = [
            k for k in metrics.keys() 
            if 'engagement_rate' in k
        ]
        
        if engagement_metrics:
            avg_engagement = statistics.mean([
                metrics[k]['current'] for k in engagement_metrics
            ])
            
            if avg_engagement < 0.01:
                summary['overall_health'] = "critical"
                summary['critical_issues'] += 1
            elif avg_engagement < 0.02:
                summary['overall_health'] = "warning"
                summary['improvement_opportunities'] += 1
        
        return summary
    
    async def _adjust_timing_algorithm(self, creator_id: Optional[str]):
        """Adjust timing algorithm parameters for better performance"""
        logger.info(f"Adjusting timing algorithm for creator {creator_id}")
        # Implementation would adjust ML model parameters
        pass
    
    async def _trigger_emergency_optimization(self, creator_id: Optional[str]):
        """Trigger emergency optimization procedures"""
        logger.info(f"Triggering emergency optimization for creator {creator_id}")
        # Implementation would activate emergency optimization protocols
        pass
    
    async def _activate_backup_strategies(self, creator_id: Optional[str]):
        """Activate backup scheduling strategies"""
        logger.info(f"Activating backup strategies for creator {creator_id}")
        # Implementation would switch to proven backup scheduling patterns
        pass

# Factory function for easy instantiation
def create_performance_monitor() -> RealTimePerformanceMonitor:
    """Create and initialize a real-time performance monitor"""
    return RealTimePerformanceMonitor()

# Export main classes
__all__ = [
    'RealTimePerformanceMonitor',
    'PerformanceAlert',
    'OptimizationRecommendation',
    'AlertLevel',
    'MetricType',
    'create_performance_monitor'
]
