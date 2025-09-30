"""Live Performance Monitor

Real-time monitoring system for content performance across all platforms
with advanced metrics collection and alert generation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of performance metrics"""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    VELOCITY = "velocity"
    CONVERSION = "conversion"
    SENTIMENT = "sentiment"
    VIRAL_POTENTIAL = "viral_potential"


@dataclass
class PerformanceMetrics:
    """Real-time performance metrics"""
    content_id: str
    platform: str
    timestamp: datetime
    metrics: Dict[str, float]
    trend_direction: str  # up, down, stable
    velocity: float
    engagement_rate: float
    reach_growth: float
    conversion_rate: float
    sentiment_score: float
    viral_potential: float
    alert_level: str  # normal, warning, critical, emergency


@dataclass
class PerformanceAlert:
    """Performance alert data"""
    alert_id: str
    content_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    platform: str
    metrics: Dict[str, Any]
    recommended_actions: List[str]


class LivePerformanceMonitor:
    """Real-time content performance monitoring system"""
    
    def __init__(self):
        """Initialize live performance monitor"""
        self.monitoring_active = False
        self.monitored_content = {}
        self.performance_history = {}
        self.alert_thresholds = self._init_alert_thresholds()
        
    def _init_alert_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize alert thresholds for different metrics"""
        return {
            "engagement": {
                "critical_low": 0.005,
                "warning_low": 0.01,
                "warning_high": 0.8,
                "critical_high": 0.95
            },
            "reach_velocity": {
                "critical_low": 0.1,
                "warning_low": 0.5,
                "warning_high": 5.0,
                "critical_high": 10.0
            },
            "sentiment": {
                "critical_low": 0.2,
                "warning_low": 0.4,
                "normal_min": 0.6,
                "good": 0.8
            },
            "viral_potential": {
                "opportunity": 0.7,
                "high_opportunity": 0.8,
                "viral_alert": 0.9
            }
        }
    
    async def start_monitoring(self, content_list: List[Dict[str, Any]]) -> bool:
        """Start monitoring content performance"""
        logger.info(f"Starting live performance monitoring for {len(content_list)} items")
        
        try:
            self.monitoring_active = True
            
            for content in content_list:
                content_id = content.get('id')
                if content_id:
                    self.monitored_content[content_id] = {
                        'content': content,
                        'platforms': content.get('platforms', []),
                        'start_time': datetime.utcnow(),
                        'last_check': None
                    }
            
            # Start monitoring task
            asyncio.create_task(self._monitoring_loop())
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting performance monitoring: {str(e)}")
            return False
    
    async def stop_monitoring(self, content_id: Optional[str] = None) -> bool:
        """Stop monitoring for specific content or all content"""
        try:
            if content_id:
                if content_id in self.monitored_content:
                    del self.monitored_content[content_id]
                    logger.info(f"Stopped monitoring for content: {content_id}")
                    return True
                return False
            else:
                self.monitoring_active = False
                self.monitored_content.clear()
                logger.info("Stopped all performance monitoring")
                return True
                
        except Exception as e:
            logger.error(f"Error stopping performance monitoring: {str(e)}")
            return False
    
    async def get_real_time_metrics(
        self, 
        content_id: str, 
        platform: Optional[str] = None
    ) -> Optional[PerformanceMetrics]:
        """Get real-time performance metrics for content"""
        try:
            if content_id not in self.monitored_content:
                return None
            
            content_data = self.monitored_content[content_id]
            platforms = [platform] if platform else content_data['platforms']
            
            # Collect metrics from all platforms
            aggregated_metrics = await self._collect_platform_metrics(content_id, platforms)
            
            # Calculate derived metrics
            engagement_rate = await self._calculate_engagement_rate(aggregated_metrics)
            reach_growth = await self._calculate_reach_growth(content_id, aggregated_metrics)
            velocity = await self._calculate_velocity(content_id, aggregated_metrics)
            conversion_rate = await self._calculate_conversion_rate(aggregated_metrics)
            sentiment_score = await self._calculate_sentiment_score(aggregated_metrics)
            viral_potential = await self._calculate_viral_potential(aggregated_metrics)
            
            # Determine trend direction
            trend_direction = await self._determine_trend_direction(content_id, aggregated_metrics)
            
            # Determine alert level
            alert_level = await self._determine_alert_level(
                engagement_rate, velocity, sentiment_score, viral_potential
            )
            
            metrics = PerformanceMetrics(
                content_id=content_id,
                platform=platform or 'aggregated',
                timestamp=datetime.utcnow(),
                metrics=aggregated_metrics,
                trend_direction=trend_direction,
                velocity=velocity,
                engagement_rate=engagement_rate,
                reach_growth=reach_growth,
                conversion_rate=conversion_rate,
                sentiment_score=sentiment_score,
                viral_potential=viral_potential,
                alert_level=alert_level
            )
            
            # Store in history
            await self._store_metrics_history(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {str(e)}")
            return None
    
    async def check_performance_alerts(self, content_id: str) -> List[PerformanceAlert]:
        """Check for performance alerts and anomalies"""
        try:
            metrics = await self.get_real_time_metrics(content_id)
            if not metrics:
                return []
            
            alerts = []
            
            # Check engagement alerts
            engagement_alerts = await self._check_engagement_alerts(metrics)
            alerts.extend(engagement_alerts)
            
            # Check velocity alerts
            velocity_alerts = await self._check_velocity_alerts(metrics)
            alerts.extend(velocity_alerts)
            
            # Check sentiment alerts
            sentiment_alerts = await self._check_sentiment_alerts(metrics)
            alerts.extend(sentiment_alerts)
            
            # Check viral opportunity alerts
            viral_alerts = await self._check_viral_opportunity_alerts(metrics)
            alerts.extend(viral_alerts)
            
            # Check anomaly alerts
            anomaly_alerts = await self._check_anomaly_alerts(metrics)
            alerts.extend(anomaly_alerts)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking performance alerts: {str(e)}")
            return []
    
    async def get_performance_dashboard_data(self, content_ids: List[str]) -> Dict[str, Any]:
        """Get comprehensive dashboard data for multiple content items"""
        try:
            dashboard_data = {
                'timestamp': datetime.utcnow(),
                'content_metrics': {},
                'platform_summary': {},
                'alerts_summary': {},
                'trending_opportunities': []
            }
            
            all_alerts = []
            platform_totals = {}
            
            for content_id in content_ids:
                # Get metrics
                metrics = await self.get_real_time_metrics(content_id)
                if metrics:
                    dashboard_data['content_metrics'][content_id] = metrics
                    
                    # Aggregate platform data
                    for platform in self.monitored_content.get(content_id, {}).get('platforms', []):
                        if platform not in platform_totals:
                            platform_totals[platform] = {
                                'total_views': 0,
                                'total_engagement': 0,
                                'content_count': 0
                            }
                        
                        platform_metrics = metrics.metrics.get(platform, {})
                        platform_totals[platform]['total_views'] += platform_metrics.get('views', 0)
                        platform_totals[platform]['total_engagement'] += platform_metrics.get('engagement', 0)
                        platform_totals[platform]['content_count'] += 1
                    
                    # Get alerts
                    content_alerts = await self.check_performance_alerts(content_id)
                    all_alerts.extend(content_alerts)
            
            # Process platform summary
            dashboard_data['platform_summary'] = platform_totals
            
            # Process alerts summary
            dashboard_data['alerts_summary'] = await self._process_alerts_summary(all_alerts)
            
            # Find trending opportunities
            dashboard_data['trending_opportunities'] = await self._find_trending_opportunities(content_ids)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return {}
    
    # Private methods for monitoring operations
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                for content_id in list(self.monitored_content.keys()):
                    # Update metrics and check alerts
                    await self.get_real_time_metrics(content_id)
                    alerts = await self.check_performance_alerts(content_id)
                    
                    # Process critical alerts
                    for alert in alerts:
                        if alert.severity in ['critical', 'emergency']:
                            await self._handle_critical_alert(alert)
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _collect_platform_metrics(self, content_id: str, platforms: List[str]) -> Dict[str, Any]:
        """Collect metrics from all platforms"""
        # Placeholder implementation - would integrate with actual platform APIs
        return {
            'total_views': 50000,
            'total_engagement': 2500,
            'total_shares': 150,
            'total_comments': 300,
            'platform_breakdown': {
                platform: {
                    'views': 10000,
                    'engagement': 500,
                    'shares': 30,
                    'comments': 60
                } for platform in platforms
            }
        }
    
    async def _calculate_engagement_rate(self, metrics: Dict[str, Any]) -> float:
        """Calculate engagement rate"""
        total_views = metrics.get('total_views', 1)
        total_engagement = metrics.get('total_engagement', 0)
        return total_engagement / total_views if total_views > 0 else 0.0
    
    async def _calculate_reach_growth(self, content_id: str, metrics: Dict[str, Any]) -> float:
        """Calculate reach growth rate"""
        # Compare with historical data
        history = self.performance_history.get(content_id, [])
        if len(history) < 2:
            return 0.0
        
        current_views = metrics.get('total_views', 0)
        previous_views = history[-1].get('total_views', 0)
        
        return (current_views - previous_views) / previous_views if previous_views > 0 else 0.0
    
    async def _calculate_velocity(self, content_id: str, metrics: Dict[str, Any]) -> float:
        """Calculate content velocity (views per minute)"""
        content_data = self.monitored_content.get(content_id, {})
        start_time = content_data.get('start_time')
        
        if not start_time:
            return 0.0
        
        time_elapsed = (datetime.utcnow() - start_time).total_seconds() / 60  # minutes
        total_views = metrics.get('total_views', 0)
        
        return total_views / time_elapsed if time_elapsed > 0 else 0.0
    
    async def _calculate_conversion_rate(self, metrics: Dict[str, Any]) -> float:
        """Calculate conversion rate"""
        # Placeholder - would track actual conversions
        return 0.02
    
    async def _calculate_sentiment_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate sentiment score from comments and reactions"""
        # Placeholder - would use sentiment analysis
        return 0.75
    
    async def _calculate_viral_potential(self, metrics: Dict[str, Any]) -> float:
        """Calculate viral potential score"""
        # Complex algorithm considering engagement rate, velocity, shares
        engagement_rate = await self._calculate_engagement_rate(metrics)
        shares = metrics.get('total_shares', 0)
        views = metrics.get('total_views', 1)
        
        share_rate = shares / views if views > 0 else 0
        viral_score = (engagement_rate * 0.4 + share_rate * 0.6) * 10
        
        return min(viral_score, 1.0)
    
    async def _determine_trend_direction(self, content_id: str, metrics: Dict[str, Any]) -> str:
        """Determine if metrics are trending up, down, or stable"""
        # Compare with recent history
        return "up"  # Placeholder
    
    async def _determine_alert_level(
        self, 
        engagement_rate: float, 
        velocity: float, 
        sentiment_score: float, 
        viral_potential: float
    ) -> str:
        """Determine overall alert level"""
        if engagement_rate < self.alert_thresholds["engagement"]["critical_low"]:
            return "critical"
        elif sentiment_score < self.alert_thresholds["sentiment"]["critical_low"]:
            return "critical"
        elif viral_potential > self.alert_thresholds["viral_potential"]["viral_alert"]:
            return "opportunity"
        elif engagement_rate < self.alert_thresholds["engagement"]["warning_low"]:
            return "warning"
        else:
            return "normal"
    
    async def _store_metrics_history(self, metrics: PerformanceMetrics):
        """Store metrics in history for trend analysis"""
        content_id = metrics.content_id
        if content_id not in self.performance_history:
            self.performance_history[content_id] = []
        
        self.performance_history[content_id].append({
            'timestamp': metrics.timestamp,
            'total_views': metrics.metrics.get('total_views', 0),
            'engagement_rate': metrics.engagement_rate,
            'velocity': metrics.velocity,
            'sentiment_score': metrics.sentiment_score,
            'viral_potential': metrics.viral_potential
        })
        
        # Keep only last 100 entries
        if len(self.performance_history[content_id]) > 100:
            self.performance_history[content_id] = self.performance_history[content_id][-100:]
    
    async def _check_engagement_alerts(self, metrics: PerformanceMetrics) -> List[PerformanceAlert]:
        """Check for engagement-related alerts"""
        alerts = []
        engagement_rate = metrics.engagement_rate
        thresholds = self.alert_thresholds["engagement"]
        
        if engagement_rate < thresholds["critical_low"]:
            alerts.append(PerformanceAlert(
                alert_id=f"eng_critical_{metrics.content_id}_{int(datetime.utcnow().timestamp())}",
                content_id=metrics.content_id,
                alert_type="engagement_critical",
                severity="critical",
                message=f"Critical low engagement rate: {engagement_rate:.4f}",
                timestamp=datetime.utcnow(),
                platform=metrics.platform,
                metrics={"engagement_rate": engagement_rate},
                recommended_actions=["boost_content", "revise_strategy", "emergency_promotion"]
            ))
        elif engagement_rate < thresholds["warning_low"]:
            alerts.append(PerformanceAlert(
                alert_id=f"eng_warning_{metrics.content_id}_{int(datetime.utcnow().timestamp())}",
                content_id=metrics.content_id,
                alert_type="engagement_warning",
                severity="warning",
                message=f"Low engagement rate: {engagement_rate:.4f}",
                timestamp=datetime.utcnow(),
                platform=metrics.platform,
                metrics={"engagement_rate": engagement_rate},
                recommended_actions=["optimize_content", "adjust_timing", "review_hashtags"]
            ))
        
        return alerts
    
    async def _check_velocity_alerts(self, metrics: PerformanceMetrics) -> List[PerformanceAlert]:
        """Check for velocity-related alerts"""
        # Placeholder implementation
        return []
    
    async def _check_sentiment_alerts(self, metrics: PerformanceMetrics) -> List[PerformanceAlert]:
        """Check for sentiment-related alerts"""
        # Placeholder implementation
        return []
    
    async def _check_viral_opportunity_alerts(self, metrics: PerformanceMetrics) -> List[PerformanceAlert]:
        """Check for viral opportunity alerts"""
        alerts = []
        viral_potential = metrics.viral_potential
        thresholds = self.alert_thresholds["viral_potential"]
        
        if viral_potential > thresholds["viral_alert"]:
            alerts.append(PerformanceAlert(
                alert_id=f"viral_opportunity_{metrics.content_id}_{int(datetime.utcnow().timestamp())}",
                content_id=metrics.content_id,
                alert_type="viral_opportunity",
                severity="opportunity",
                message=f"High viral potential detected: {viral_potential:.3f}",
                timestamp=datetime.utcnow(),
                platform=metrics.platform,
                metrics={"viral_potential": viral_potential},
                recommended_actions=["amplify_promotion", "cross_platform_boost", "influencer_outreach"]
            ))
        
        return alerts
    
    async def _check_anomaly_alerts(self, metrics: PerformanceMetrics) -> List[PerformanceAlert]:
        """Check for performance anomalies"""
        # Placeholder implementation
        return []
    
    async def _process_alerts_summary(self, alerts: List[PerformanceAlert]) -> Dict[str, Any]:
        """Process alerts into summary format"""
        summary = {
            'total_alerts': len(alerts),
            'by_severity': {},
            'by_type': {},
            'critical_count': 0,
            'opportunity_count': 0
        }
        
        for alert in alerts:
            # Count by severity
            severity = alert.severity
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            
            # Count by type
            alert_type = alert.alert_type
            summary['by_type'][alert_type] = summary['by_type'].get(alert_type, 0) + 1
            
            # Special counters
            if severity == 'critical':
                summary['critical_count'] += 1
            elif severity == 'opportunity':
                summary['opportunity_count'] += 1
        
        return summary
    
    async def _find_trending_opportunities(self, content_ids: List[str]) -> List[Dict[str, Any]]:
        """Find trending opportunities across content"""
        # Placeholder implementation
        return [
            {
                'content_id': content_ids[0] if content_ids else 'unknown',
                'opportunity_type': 'trending_hashtag',
                'description': 'High engagement hashtag detected',
                'priority': 'high'
            }
        ]
    
    async def _handle_critical_alert(self, alert: PerformanceAlert):
        """Handle critical alerts with immediate action"""
        logger.critical(f"Critical alert: {alert.message}")
        # Would trigger emergency response protocols


__all__ = ['LivePerformanceMonitor', 'PerformanceMetrics', 'PerformanceAlert', 'MetricType']