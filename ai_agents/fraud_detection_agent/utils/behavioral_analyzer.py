"""Behavioral Analyzer - Advanced User Behavior Analysis for Fraud Detection

Sophisticated behavioral pattern analysis system for detecting fraudulent user behavior
through machine learning, statistical analysis, and real-time monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import redis.asyncio as aioredis

try:
    from core.exceptions import BehaviorAnalysisError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    BehaviorAnalysisError = globals().get('BehaviorAnalysisError', Exception)
from ...utils.statistical_analyzer import StatisticalAnalyzer
from ...data.models.user_behavior import UserBehavior, BehaviorPattern

logger = logging.getLogger(__name__)

@dataclass
class BehaviorMetrics:
    """Comprehensive user behavior metrics"""    session_duration: float
    action_frequency: float
    click_patterns: List[float]
    navigation_patterns: List[str]
    typing_cadence: List[float]
    mouse_movement_entropy: float
    device_consistency: float
    geolocation_stability: float
    time_zone_consistency: float
    platform_switching_rate: float
    content_interaction_rate: float
    social_engagement_score: float

@dataclass
class BehaviorAnomalies:
    """Detected behavioral anomalies"""    velocity_anomalies: List[str]
    pattern_deviations: List[str]
    temporal_inconsistencies: List[str]
    geographic_anomalies: List[str]
    device_inconsistencies: List[str]
    interaction_anomalies: List[str]

class BehaviorAnalyzer:
    """    Advanced Behavioral Analysis Engine
    
    Analyzes user behavior patterns to detect fraud through:
    - Machine learning anomaly detection
    - Statistical pattern analysis
    - Temporal behavior modeling
    - Geographic consistency checking
    - Device fingerprint analysis
    """    
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self.redis_client = redis_client
        self.statistical_analyzer = StatisticalAnalyzer()
        
        # ML models for behavior analysis
        self.anomaly_detector = RandomForestClassifier(
            n_estimators=100, 
            random_state=42,
            class_weight='balanced'
        )
        self.cluster_analyzer = DBSCAN(eps=0.5, min_samples=5)
        self.scaler = StandardScaler()
        
        # Behavior baseline thresholds
        self.normal_thresholds = {
            'session_duration': (300, 7200),  # 5 min to 2 hours
            'action_frequency': (0.1, 10.0),  # Actions per minute
            'mouse_entropy': (0.3, 0.9),      # Mouse movement entropy
            'typing_cadence': (50, 200),      # WPM range
            'geo_radius': 50,                 # km radius for normal location
            'device_switches': 3,             # Max device switches per day
            'platform_switches': 5           # Max platform switches per session
        }
        
        # Anomaly detection weights
        self.anomaly_weights = {
            'velocity': 0.25,
            'pattern': 0.20,
            'temporal': 0.15,
            'geographic': 0.15,
            'device': 0.15,
            'interaction': 0.10
        }
        
        logger.info("Behavior Analyzer initialized successfully")

    async def analyze_behavior(
        self,
        user_id: str,
        session_info: Dict[str, Any],
        historical_data: Dict[str, Any],
        geolocation: Dict[str, Any],
        device_fingerprint: str
    ) -> Dict[str, Any]:
        """        Comprehensive behavioral analysis for fraud detection
        
        Args:
            user_id: User identifier
            session_info: Current session data
            historical_data: User's historical behavior data
            geolocation: Current geolocation data
            device_fingerprint: Device fingerprint data
            
        Returns:
            Behavioral analysis results with risk score
        """        try:
            # Extract behavior metrics
            current_metrics = await self._extract_behavior_metrics(
                session_info, geolocation, device_fingerprint
            )
            
            # Get historical baselines
            historical_baselines = await self._get_historical_baselines(
                user_id, historical_data
            )
            
            # Detect behavioral anomalies
            anomalies = await self._detect_behavior_anomalies(
                current_metrics, historical_baselines, user_id
            )
            
            # Calculate risk score
            risk_score = await self._calculate_behavior_risk_score(
                current_metrics, anomalies, historical_baselines
            )
            
            # Generate behavior profile
            behavior_profile = await self._generate_behavior_profile(
                current_metrics, historical_baselines
            )
            
            # Update user behavior history
            await self._update_behavior_history(user_id, current_metrics)
            
            result = {
                'risk_score': risk_score,
                'anomalies': [
                    *anomalies.velocity_anomalies,
                    *anomalies.pattern_deviations,
                    *anomalies.temporal_inconsistencies,
                    *anomalies.geographic_anomalies,
                    *anomalies.device_inconsistencies,
                    *anomalies.interaction_anomalies
                ],
                'behavior_profile': behavior_profile,
                'current_metrics': current_metrics.__dict__,
                'deviation_score': await self._calculate_deviation_score(
                    current_metrics, historical_baselines
                ),
                'trust_indicators': await self._extract_trust_indicators(
                    current_metrics, historical_baselines
                ),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            logger.info(
                f"Behavior analysis completed for user {user_id}: "
                f"risk_score={risk_score:.3f}, anomalies_count={len(result['anomalies'])}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Behavior analysis failed for user {user_id}: {str(e)}")
            raise BehaviorAnalysisError(f"Behavior analysis failed: {str(e)}")

    async def _extract_behavior_metrics(
        self,
        session_info: Dict[str, Any],
        geolocation: Dict[str, Any], 
        device_fingerprint: str
    ) -> BehaviorMetrics:
        """Extract comprehensive behavior metrics from session data"""        
        # Session metrics
        session_start = session_info.get('start_time', datetime.now())
        session_duration = (datetime.now() - session_start).total_seconds()
        
        # Action metrics
        actions = session_info.get('actions', [])
        action_frequency = len(actions) / max(session_duration / 60, 1)  # Actions per minute
        
        # Interaction patterns
        click_patterns = self._analyze_click_patterns(session_info.get('clicks', []))
        navigation_patterns = self._analyze_navigation_patterns(session_info.get('page_visits', []))
        
        # Input analysis
        typing_data = session_info.get('typing_data', [])
        typing_cadence = self._analyze_typing_cadence(typing_data)
        
        mouse_movements = session_info.get('mouse_movements', [])
        mouse_entropy = self._calculate_mouse_entropy(mouse_movements)
        
        # Device and location metrics
        device_consistency = self._calculate_device_consistency(device_fingerprint)
        geo_stability = self._calculate_geolocation_stability(geolocation)
        timezone_consistency = self._analyze_timezone_consistency(session_info, geolocation)
        
        # Platform behavior
        platform_switches = len(set(session_info.get('platform_visits', [])))
        platform_switching_rate = platform_switches / max(session_duration / 3600, 1)
        
        # Content interaction
        content_interactions = session_info.get('content_interactions', [])
        content_interaction_rate = len(content_interactions) / max(session_duration / 60, 1)
        
        # Social engagement
        social_actions = session_info.get('social_actions', [])
        social_engagement_score = self._calculate_social_engagement_score(social_actions)
        
        return BehaviorMetrics(
            session_duration=session_duration,
            action_frequency=action_frequency,
            click_patterns=click_patterns,
            navigation_patterns=navigation_patterns,
            typing_cadence=typing_cadence,
            mouse_movement_entropy=mouse_entropy,
            device_consistency=device_consistency,
            geolocation_stability=geo_stability,
            time_zone_consistency=timezone_consistency,
            platform_switching_rate=platform_switching_rate,
            content_interaction_rate=content_interaction_rate,
            social_engagement_score=social_engagement_score
        )

    def _analyze_click_patterns(self, clicks: List[Dict]) -> List[float]:
        """Analyze click timing patterns for bot detection"""        if len(clicks) < 2:
            return [0.0]
            
        intervals = []
        for i in range(1, len(clicks)):
            prev_time = clicks[i-1].get('timestamp', 0)
            curr_time = clicks[i].get('timestamp', 0)
            intervals.append(curr_time - prev_time)
            
        # Calculate statistical measures
        if intervals:
            return [
                np.mean(intervals),
                np.std(intervals),
                np.median(intervals),
                len([i for i in intervals if i < 0.1])  # Suspiciously fast clicks
            ]
        return [0.0]

    def _analyze_navigation_patterns(self, page_visits: List[Dict]) -> List[str]:
        """Analyze page navigation patterns"""        if len(page_visits) < 2:
            return []
            
        patterns = []
        
        # Sequential patterns
        sequences = [visit.get('page_type', '') for visit in page_visits]
        
        # Detect unusual navigation sequences
        if len(set(sequences)) == 1 and len(sequences) > 5:
            patterns.append('repetitive_navigation')
            
        # Rapid page switching
        rapid_switches = 0
        for i in range(1, len(page_visits)):
            prev_time = page_visits[i-1].get('timestamp', 0)
            curr_time = page_visits[i].get('timestamp', 0)
            if curr_time - prev_time < 1:  # Less than 1 second
                rapid_switches += 1
                
        if rapid_switches > len(page_visits) * 0.3:
            patterns.append('rapid_page_switching')
            
        return patterns

    def _analyze_typing_cadence(self, typing_data: List[Dict]) -> List[float]:
        """Analyze typing patterns for human vs bot detection"""        if not typing_data:
            return [0.0]
            
        keystroke_intervals = []
        for entry in typing_data:
            intervals = entry.get('keystroke_intervals', [])
            keystroke_intervals.extend(intervals)
            
        if keystroke_intervals:
            return [
                np.mean(keystroke_intervals),
                np.std(keystroke_intervals),
                len([i for i in keystroke_intervals if i < 0.05]),  # Inhuman speed
                len([i for i in keystroke_intervals if i > 2.0])    # Unusual pauses
            ]
        return [0.0]

    def _calculate_mouse_entropy(self, mouse_movements: List[Dict]) -> float:
        """Calculate entropy of mouse movements"""        if len(mouse_movements) < 10:
            return 0.0
            
        # Extract x, y coordinates
        coordinates = [(m.get('x', 0), m.get('y', 0)) for m in mouse_movements]
        
        # Calculate movement vectors
        movements = []
        for i in range(1, len(coordinates)):
            dx = coordinates[i][0] - coordinates[i-1][0]
            dy = coordinates[i][1] - coordinates[i-1][1]
            movements.append((dx, dy))
            
        # Calculate entropy of movement directions
        if movements:
            angles = [np.arctan2(dy, dx) for dx, dy in movements if dx != 0 or dy != 0]
            if angles:
                # Discretize angles into bins
                bins = np.linspace(-np.pi, np.pi, 16)
                hist, _ = np.histogram(angles, bins)
                # Normalize
                hist = hist / np.sum(hist)
                # Calculate entropy
                entropy = -np.sum(hist * np.log2(hist + 1e-10))
                return entropy / np.log2(len(bins))  # Normalize to [0,1]
                
        return 0.0

    def _calculate_device_consistency(self, device_fingerprint: str) -> float:
        """Calculate device fingerprint consistency score"""        # This would compare against historical device fingerprints
        # For now, return a placeholder score
        return 0.8

    def _calculate_geolocation_stability(self, geolocation: Dict[str, Any]) -> float:
        """Calculate geolocation stability score"""        # Check for reasonable location consistency
        latitude = geolocation.get('latitude', 0)
        longitude = geolocation.get('longitude', 0)
        accuracy = geolocation.get('accuracy', 1000)
        
        # Higher accuracy (lower value) = higher stability
        stability_score = max(0, 1 - (accuracy / 1000))
        
        return stability_score

    def _analyze_timezone_consistency(
        self, 
        session_info: Dict[str, Any], 
        geolocation: Dict[str, Any]
    ) -> float:
        """Analyze timezone consistency with location"""        session_timezone = session_info.get('timezone', '')
        geo_timezone = geolocation.get('timezone', '')
        
        if session_timezone and geo_timezone:
            return 1.0 if session_timezone == geo_timezone else 0.0
        return 0.5  # Unknown consistency

    def _calculate_social_engagement_score(self, social_actions: List[Dict]) -> float:
        """Calculate social engagement authenticity score"""        if not social_actions:
            return 0.0
            
        # Analyze timing patterns of social actions
        timestamps = [action.get('timestamp', 0) for action in social_actions]
        
        if len(timestamps) < 2:
            return 0.5
            
        # Calculate intervals between social actions
        intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        
        # Human-like social engagement should have varied intervals
        interval_variance = np.var(intervals) if intervals else 0
        
        # Normalize score based on variance (higher variance = more human-like)
        return min(1.0, interval_variance / 10000)  # Normalize appropriately

    async def _get_historical_baselines(
        self, 
        user_id: str, 
        historical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get user's historical behavior baselines"""        try:
            # Try to get from cache first
            cache_key = f"behavior_baseline:{user_id}"
            cached_baseline = await self.redis_client.get(cache_key)
            
            if cached_baseline:
                return eval(cached_baseline)
                
            # Calculate from historical data
            baseline = {
                'avg_session_duration': historical_data.get('avg_session_duration', 1800),
                'avg_action_frequency': historical_data.get('avg_action_frequency', 2.0),
                'typical_devices': historical_data.get('devices', []),
                'typical_locations': historical_data.get('locations', []),
                'typical_platforms': historical_data.get('platforms', []),
                'social_engagement_baseline': historical_data.get('social_engagement', 0.5)
            }
            
            # Cache for future use
            await self.redis_client.setex(cache_key, 3600, str(baseline))
            
            return baseline
            
        except Exception as e:
            logger.error(f"Failed to get historical baselines for user {user_id}: {str(e)}")
            return {}

    async def _detect_behavior_anomalies(
        self,
        current_metrics: BehaviorMetrics,
        historical_baselines: Dict[str, Any],
        user_id: str
    ) -> BehaviorAnomalies:
        """Detect various types of behavioral anomalies"""        
        velocity_anomalies = []
        pattern_deviations = []
        temporal_inconsistencies = []
        geographic_anomalies = []
        device_inconsistencies = []
        interaction_anomalies = []
        
        # Velocity anomalies (suspiciously fast actions)
        if current_metrics.action_frequency > self.normal_thresholds['action_frequency'][1]:
            velocity_anomalies.append('excessive_action_frequency')
            
        if any(interval < 0.05 for interval in current_metrics.click_patterns):
            velocity_anomalies.append('inhuman_click_speed')
            
        # Pattern deviations
        if current_metrics.mouse_movement_entropy < 0.1:
            pattern_deviations.append('robotic_mouse_patterns')
            
        if 'repetitive_navigation' in current_metrics.navigation_patterns:
            pattern_deviations.append('repetitive_navigation')
            
        # Temporal inconsistencies
        baseline_duration = historical_baselines.get('avg_session_duration', 1800)
        if abs(current_metrics.session_duration - baseline_duration) > baseline_duration * 2:
            temporal_inconsistencies.append('unusual_session_duration')
            
        # Geographic anomalies
        if current_metrics.geolocation_stability < 0.3:
            geographic_anomalies.append('unstable_geolocation')
            
        if current_metrics.time_zone_consistency < 0.5:
            geographic_anomalies.append('timezone_location_mismatch')
            
        # Device inconsistencies  
        if current_metrics.device_consistency < 0.5:
            device_inconsistencies.append('unusual_device_fingerprint')
            
        # Interaction anomalies
        baseline_engagement = historical_baselines.get('social_engagement_baseline', 0.5)
        if abs(current_metrics.social_engagement_score - baseline_engagement) > 0.7:
            interaction_anomalies.append('abnormal_social_engagement')
            
        return BehaviorAnomalies(
            velocity_anomalies=velocity_anomalies,
            pattern_deviations=pattern_deviations,
            temporal_inconsistencies=temporal_inconsistencies,
            geographic_anomalies=geographic_anomalies,
            device_inconsistencies=device_inconsistencies,
            interaction_anomalies=interaction_anomalies
        )

    async def _calculate_behavior_risk_score(
        self,
        current_metrics: BehaviorMetrics,
        anomalies: BehaviorAnomalies,
        historical_baselines: Dict[str, Any]
    ) -> float:
        """Calculate comprehensive behavioral risk score"""        
        risk_components = {}
        
        # Velocity risk
        velocity_score = len(anomalies.velocity_anomalies) * 0.3
        risk_components['velocity'] = min(1.0, velocity_score)
        
        # Pattern risk  
        pattern_score = len(anomalies.pattern_deviations) * 0.25
        risk_components['pattern'] = min(1.0, pattern_score)
        
        # Temporal risk
        temporal_score = len(anomalies.temporal_inconsistencies) * 0.2
        risk_components['temporal'] = min(1.0, temporal_score)
        
        # Geographic risk
        geo_score = len(anomalies.geographic_anomalies) * 0.3
        risk_components['geographic'] = min(1.0, geo_score)
        
        # Device risk
        device_score = len(anomalies.device_inconsistencies) * 0.4
        risk_components['device'] = min(1.0, device_score)
        
        # Interaction risk
        interaction_score = len(anomalies.interaction_anomalies) * 0.2
        risk_components['interaction'] = min(1.0, interaction_score)
        
        # Calculate weighted composite risk score
        composite_risk = sum(
            risk_components[component] * self.anomaly_weights[component]
            for component in risk_components
        )
        
        return min(1.0, composite_risk)

    async def _generate_behavior_profile(
        self,
        current_metrics: BehaviorMetrics,
        historical_baselines: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive behavior profile"""        return {
            'session_characteristics': {
                'duration_minutes': current_metrics.session_duration / 60,
                'activity_level': 'high' if current_metrics.action_frequency > 5 else 'normal',
                'interaction_style': 'automated' if current_metrics.mouse_movement_entropy < 0.2 else 'human'
            },
            'consistency_scores': {
                'device': current_metrics.device_consistency,
                'location': current_metrics.geolocation_stability,
                'timezone': current_metrics.time_zone_consistency
            },
            'engagement_metrics': {
                'content_interaction_rate': current_metrics.content_interaction_rate,
                'social_engagement_score': current_metrics.social_engagement_score,
                'platform_switching_rate': current_metrics.platform_switching_rate
            }
        }

    async def _calculate_deviation_score(
        self,
        current_metrics: BehaviorMetrics,
        historical_baselines: Dict[str, Any]
    ) -> float:
        """Calculate deviation score from historical baselines"""        deviations = []
        
        # Session duration deviation
        baseline_duration = historical_baselines.get('avg_session_duration', 1800)
        duration_deviation = abs(current_metrics.session_duration - baseline_duration) / baseline_duration
        deviations.append(min(1.0, duration_deviation))
        
        # Action frequency deviation
        baseline_frequency = historical_baselines.get('avg_action_frequency', 2.0)
        frequency_deviation = abs(current_metrics.action_frequency - baseline_frequency) / baseline_frequency
        deviations.append(min(1.0, frequency_deviation))
        
        # Social engagement deviation
        baseline_engagement = historical_baselines.get('social_engagement_baseline', 0.5)
        engagement_deviation = abs(current_metrics.social_engagement_score - baseline_engagement) / (baseline_engagement + 0.1)
        deviations.append(min(1.0, engagement_deviation))
        
        return np.mean(deviations) if deviations else 0.0

    async def _extract_trust_indicators(
        self,
        current_metrics: BehaviorMetrics,
        historical_baselines: Dict[str, Any]
    ) -> List[str]:
        """Extract positive trust indicators from behavior"""        trust_indicators = []
        
        # Consistent device usage
        if current_metrics.device_consistency > 0.8:
            trust_indicators.append('consistent_device_usage')
            
        # Stable geolocation
        if current_metrics.geolocation_stability > 0.7:
            trust_indicators.append('stable_location_patterns')
            
        # Human-like mouse movements
        if current_metrics.mouse_movement_entropy > 0.5:
            trust_indicators.append('natural_mouse_movements')
            
        # Reasonable session duration
        if 300 <= current_metrics.session_duration <= 7200:
            trust_indicators.append('normal_session_duration')
            
        # Consistent timezone
        if current_metrics.time_zone_consistency > 0.8:
            trust_indicators.append('timezone_consistency')
            
        return trust_indicators

    async def _update_behavior_history(self, user_id: str, metrics: BehaviorMetrics):
        """Update user's behavior history for future baseline calculations"""        try:
            history_key = f"behavior_history:{user_id}"
            
            # Store current metrics
            behavior_record = {
                'timestamp': datetime.now().isoformat(),
                'session_duration': metrics.session_duration,
                'action_frequency': metrics.action_frequency,
                'mouse_entropy': metrics.mouse_movement_entropy,
                'device_consistency': metrics.device_consistency,
                'geo_stability': metrics.geolocation_stability,
                'social_engagement': metrics.social_engagement_score
            }
            
            # Add to history list (keep last 100 records)
            await self.redis_client.lpush(history_key, str(behavior_record))
            await self.redis_client.ltrim(history_key, 0, 99)
            await self.redis_client.expire(history_key, 86400 * 30)  # 30 days
            
        except Exception as e:
            logger.error(f"Failed to update behavior history for user {user_id}: {str(e)}")

    async def learn_normal_behavior(
        self, 
        user_id: str, 
        behavior_samples: List[Dict[str, Any]]
    ):
        """Learn and update normal behavior patterns for a user"""        try:
            if len(behavior_samples) < 5:
                logger.warning(f"Insufficient behavior samples for user {user_id}")
                return
                
            # Extract features from samples
            features = []
            for sample in behavior_samples:
                feature_vector = [
                    sample.get('session_duration', 0),
                    sample.get('action_frequency', 0),
                    sample.get('mouse_entropy', 0),
                    sample.get('device_consistency', 0),
                    sample.get('geo_stability', 0),
                    sample.get('social_engagement', 0)
                ]
                features.append(feature_vector)
                
            features_array = np.array(features)
            
            # Update user's behavior baseline
            baseline = {
                'avg_session_duration': np.mean(features_array[:, 0]),
                'avg_action_frequency': np.mean(features_array[:, 1]),
                'avg_mouse_entropy': np.mean(features_array[:, 2]),
                'avg_device_consistency': np.mean(features_array[:, 3]),
                'avg_geo_stability': np.mean(features_array[:, 4]),
                'social_engagement_baseline': np.mean(features_array[:, 5])
            }
            
            # Cache updated baseline
            cache_key = f"behavior_baseline:{user_id}"
            await self.redis_client.setex(cache_key, 86400, str(baseline))
            
            logger.info(f"Updated behavior baseline for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to learn normal behavior for user {user_id}: {str(e)}")

    async def get_behavior_trends(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get behavior trends over time for a user"""        try:
            history_key = f"behavior_history:{user_id}"
            history_records = await self.redis_client.lrange(history_key, 0, -1)
            
            if not history_records:
                return {'trends': [], 'analysis': 'Insufficient historical data'}
                
            # Parse historical records
            parsed_records = []
            for record in history_records:
                try:
                    parsed_records.append(eval(record))
                except:
                    continue
                    
            # Filter by time range
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_records = [
                record for record in parsed_records
                if datetime.fromisoformat(record['timestamp']) > cutoff_date
            ]
            
            if not recent_records:
                return {'trends': [], 'analysis': 'No recent behavior data'}
                
            # Calculate trends
            timestamps = [datetime.fromisoformat(r['timestamp']) for r in recent_records]
            session_durations = [r.get('session_duration', 0) for r in recent_records]
            action_frequencies = [r.get('action_frequency', 0) for r in recent_records]
            
            trends = {
                'session_duration_trend': self._calculate_trend(timestamps, session_durations),
                'action_frequency_trend': self._calculate_trend(timestamps, action_frequencies),
                'consistency_trend': np.mean([r.get('device_consistency', 0) for r in recent_records]),
                'stability_trend': np.mean([r.get('geo_stability', 0) for r in recent_records])
            }
            
            return {
                'trends': trends,
                'data_points': len(recent_records),
                'time_range_days': days,
                'analysis': 'Trends calculated successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to get behavior trends for user {user_id}: {str(e)}")
            return {'trends': {}, 'analysis': f'Error: {str(e)}'}

    def _calculate_trend(self, timestamps: List[datetime], values: List[float]) -> float:
        """Calculate trend direction (-1 to 1) for a time series"""        if len(timestamps) < 2:
            return 0.0
            
        # Convert timestamps to numeric values
        numeric_times = [(t - timestamps[0]).total_seconds() for t in timestamps]
        
        # Calculate linear regression slope
        if len(numeric_times) == len(values):
            correlation_matrix = np.corrcoef(numeric_times, values)
            correlation = correlation_matrix[0, 1]
            return correlation if not np.isnan(correlation) else 0.0
        
        return 0.0
