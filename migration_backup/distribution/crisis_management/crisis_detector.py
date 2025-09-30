"""Crisis Detector - Real-time Crisis Detection Engine

AI-powered crisis detection system that monitors content performance,
sentiment, and social signals to identify potential reputation crises.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Crisis alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class CrisisAlert:
    """Crisis detection alert"""
    alert_id: str
    severity: AlertSeverity
    crisis_type: str
    detected_at: datetime
    content_id: str
    platforms_affected: List[str]
    indicators: Dict[str, Any]
    confidence_score: float
    immediate_actions: List[str]
    monitoring_recommendations: List[str]


class CrisisDetector:
    """Real-time crisis detection and alerting engine"""
    
    def __init__(self):
        """Initialize crisis detector"""
        self.detection_models = self._load_detection_models()
        self.monitoring_thresholds = self._load_monitoring_thresholds()
        self.active_monitoring = {}
        
    async def monitor_for_crisis(
        self,
        content_id: str,
        monitoring_data: Dict[str, Any],
        detection_sensitivity: float = 0.8
    ) -> Optional[CrisisAlert]:
        """Monitor content for crisis indicators"""
        logger.info(f"Monitoring content for crisis: {content_id}")
        
        try:
            # Analyze sentiment trends
            sentiment_analysis = await self._analyze_sentiment_trends(monitoring_data)
            
            # Check engagement anomalies
            engagement_anomalies = await self._detect_engagement_anomalies(monitoring_data)
            
            # Monitor negative mentions
            negative_mentions = await self._monitor_negative_mentions(monitoring_data)
            
            # Check viral negativity
            viral_negativity = await self._check_viral_negativity(monitoring_data)
            
            # Analyze comment sentiment
            comment_sentiment = await self._analyze_comment_sentiment(monitoring_data)
            
            # Check for coordinated attacks
            coordinated_attacks = await self._detect_coordinated_attacks(monitoring_data)
            
            # Compile crisis indicators
            crisis_indicators = {
                'sentiment_decline': sentiment_analysis['decline_detected'],
                'engagement_anomalies': engagement_anomalies['anomalies_detected'],
                'negative_mentions_spike': negative_mentions['spike_detected'],
                'viral_negativity': viral_negativity['risk_level'],
                'comment_sentiment': comment_sentiment['negative_ratio'],
                'coordinated_attacks': coordinated_attacks['attack_detected']
            }
            
            # Calculate crisis probability
            crisis_probability = await self._calculate_crisis_probability(crisis_indicators)
            
            # Check if crisis threshold exceeded
            if crisis_probability >= detection_sensitivity:
                # Determine crisis type
                crisis_type = await self._determine_crisis_type(crisis_indicators)
                
                # Assess severity
                severity = await self._assess_alert_severity(crisis_probability, crisis_indicators)
                
                # Generate immediate actions
                immediate_actions = await self._generate_immediate_actions(severity, crisis_type)
                
                # Create monitoring recommendations
                monitoring_recommendations = await self._create_monitoring_recommendations(
                    severity, crisis_type
                )
                
                # Identify affected platforms
                platforms_affected = await self._identify_affected_platforms(monitoring_data)
                
                alert_id = f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                
                return CrisisAlert(
                    alert_id=alert_id,
                    severity=severity,
                    crisis_type=crisis_type,
                    detected_at=datetime.utcnow(),
                    content_id=content_id,
                    platforms_affected=platforms_affected,
                    indicators=crisis_indicators,
                    confidence_score=crisis_probability,
                    immediate_actions=immediate_actions,
                    monitoring_recommendations=monitoring_recommendations
                )
            
            return None  # No crisis detected
            
        except Exception as e:
            logger.error(f"Error monitoring for crisis: {str(e)}")
            raise
    
    def _load_detection_models(self) -> Dict[str, Any]:
        """Load crisis detection ML models"""
        return {
            'sentiment_analyzer': None,     # Would load actual sentiment model
            'anomaly_detector': None,       # Would load anomaly detection model
            'attack_detector': None,        # Would load coordinated attack model
            'crisis_classifier': None       # Would load crisis classification model
        }
    
    def _load_monitoring_thresholds(self) -> Dict[str, float]:
        """Load monitoring thresholds for different indicators"""
        return {
            'sentiment_decline_threshold': -0.3,
            'engagement_anomaly_threshold': 2.0,  # Standard deviations
            'negative_mentions_threshold': 0.6,
            'viral_negativity_threshold': 0.7,
            'comment_negativity_threshold': 0.5,
            'coordinated_attack_threshold': 0.8
        }
    
    async def _analyze_sentiment_trends(self, data: Dict) -> Dict[str, Any]:
        """Analyze sentiment trends for decline detection"""
        current_sentiment = data.get('current_sentiment', 0.5)
        previous_sentiment = data.get('previous_sentiment', 0.5)
        sentiment_change = current_sentiment - previous_sentiment
        
        decline_detected = sentiment_change < self.monitoring_thresholds['sentiment_decline_threshold']
        
        return {
            'current_sentiment': current_sentiment,
            'sentiment_change': sentiment_change,
            'decline_detected': decline_detected,
            'decline_severity': abs(sentiment_change) if decline_detected else 0
        }
    
    async def _detect_engagement_anomalies(self, data: Dict) -> Dict[str, Any]:
        """Detect unusual engagement patterns"""
        current_engagement = data.get('current_engagement_rate', 0.05)
        baseline_engagement = data.get('baseline_engagement_rate', 0.05)
        
        if baseline_engagement > 0:
            engagement_ratio = current_engagement / baseline_engagement
            anomaly_detected = engagement_ratio < 0.5 or engagement_ratio > 2.0
        else:
            anomaly_detected = False
            engagement_ratio = 1.0
        
        return {
            'current_engagement': current_engagement,
            'baseline_engagement': baseline_engagement,
            'engagement_ratio': engagement_ratio,
            'anomalies_detected': anomaly_detected
        }
    
    async def _monitor_negative_mentions(self, data: Dict) -> Dict[str, Any]:
        """Monitor for spikes in negative mentions"""
        negative_mentions = data.get('negative_mentions_count', 0)
        total_mentions = data.get('total_mentions_count', 1)
        negative_ratio = negative_mentions / total_mentions if total_mentions > 0 else 0
        
        spike_detected = negative_ratio > self.monitoring_thresholds['negative_mentions_threshold']
        
        return {
            'negative_mentions': negative_mentions,
            'total_mentions': total_mentions,
            'negative_ratio': negative_ratio,
            'spike_detected': spike_detected
        }
    
    async def _check_viral_negativity(self, data: Dict) -> Dict[str, Any]:
        """Check for viral negative content spread"""
        share_velocity = data.get('negative_share_velocity', 0)
        comment_velocity = data.get('negative_comment_velocity', 0)
        
        # Simplified risk calculation
        risk_level = min((share_velocity + comment_velocity) / 2, 1.0)
        high_risk = risk_level > self.monitoring_thresholds['viral_negativity_threshold']
        
        return {
            'share_velocity': share_velocity,
            'comment_velocity': comment_velocity,
            'risk_level': risk_level,
            'high_risk_detected': high_risk
        }
    
    async def _analyze_comment_sentiment(self, data: Dict) -> Dict[str, Any]:
        """Analyze sentiment of comments and responses"""
        comments_data = data.get('comments_sentiment', {})
        negative_comments = comments_data.get('negative_count', 0)
        total_comments = comments_data.get('total_count', 1)
        negative_ratio = negative_comments / total_comments if total_comments > 0 else 0
        
        return {
            'negative_comments': negative_comments,
            'total_comments': total_comments,
            'negative_ratio': negative_ratio,
            'threshold_exceeded': negative_ratio > self.monitoring_thresholds['comment_negativity_threshold']
        }
    
    async def _detect_coordinated_attacks(self, data: Dict) -> Dict[str, Any]:
        """Detect coordinated attacks or bot activity"""
        # Simplified detection - would use sophisticated ML models
        suspicious_patterns = data.get('suspicious_activity_score', 0)
        attack_detected = suspicious_patterns > self.monitoring_thresholds['coordinated_attack_threshold']
        
        return {
            'suspicious_score': suspicious_patterns,
            'attack_detected': attack_detected,
            'attack_indicators': data.get('attack_indicators', [])
        }
    
    async def _calculate_crisis_probability(self, indicators: Dict[str, Any]) -> float:
        """Calculate overall crisis probability from indicators"""
        # Weighted scoring of different indicators
        weights = {
            'sentiment_decline': 0.25,
            'engagement_anomalies': 0.15,
            'negative_mentions_spike': 0.20,
            'viral_negativity': 0.20,
            'comment_sentiment': 0.15,
            'coordinated_attacks': 0.05
        }
        
        total_score = 0
        for indicator, weight in weights.items():
            indicator_value = indicators.get(indicator, 0)
            if isinstance(indicator_value, bool):
                indicator_value = 1.0 if indicator_value else 0.0
            elif isinstance(indicator_value, str):
                indicator_value = 0.8 if indicator_value == 'high' else 0.4 if indicator_value == 'medium' else 0.0
            
            total_score += indicator_value * weight
        
        return min(total_score, 1.0)
    
    async def _determine_crisis_type(self, indicators: Dict) -> str:
        """Determine the type of crisis based on indicators"""
        if indicators.get('coordinated_attacks'):
            return 'coordinated_attack'
        elif indicators.get('viral_negativity', 0) > 0.8:
            return 'viral_backlash'
        elif indicators.get('sentiment_decline'):
            return 'reputation_damage'
        else:
            return 'engagement_crisis'
    
    async def _assess_alert_severity(self, probability: float, indicators: Dict) -> AlertSeverity:
        """Assess the severity of the crisis alert"""
        if probability >= 0.9:
            return AlertSeverity.EMERGENCY
        elif probability >= 0.8:
            return AlertSeverity.CRITICAL
        elif probability >= 0.6:
            return AlertSeverity.WARNING
        else:
            return AlertSeverity.INFO
    
    async def _generate_immediate_actions(self, severity: AlertSeverity, crisis_type: str) -> List[str]:
        """Generate immediate action recommendations"""
        actions = []
        
        if severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
            actions.extend([
                'Pause all scheduled content',
                'Activate crisis response team',
                'Monitor all platforms continuously'
            ])
        
        if crisis_type == 'coordinated_attack':
            actions.append('Report suspicious activity to platforms')
        elif crisis_type == 'viral_backlash':
            actions.append('Prepare public response statement')
        
        return actions
    
    async def _create_monitoring_recommendations(self, severity: AlertSeverity, crisis_type: str) -> List[str]:
        """Create monitoring recommendations"""
        recommendations = [
            'Increase monitoring frequency to every 5 minutes',
            'Track sentiment across all platforms',
            'Monitor competitor activity'
        ]
        
        if severity == AlertSeverity.EMERGENCY:
            recommendations.append('Activate 24/7 monitoring')
        
        return recommendations
    
    async def _identify_affected_platforms(self, data: Dict) -> List[str]:
        """Identify which platforms are affected by the crisis"""
        platform_data = data.get('platform_metrics', {})
        affected_platforms = []
        
        for platform, metrics in platform_data.items():
            if metrics.get('negative_sentiment', 0) > 0.6:
                affected_platforms.append(platform)
        
        return affected_platforms if affected_platforms else ['unknown']


__all__ = ['CrisisDetector', 'CrisisAlert', 'AlertSeverity']