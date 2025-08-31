"""Anomaly Detection Engine - Advanced Statistical Anomaly Detection

Sophisticated anomaly detection system using machine learning and statistical methods
for identifying unusual patterns in user behavior and system interactions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
import redis.asyncio as aioredis

try:
    from core.exceptions import AnomalyDetectionError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    AnomalyDetectionError = globals().get('AnomalyDetectionError', Exception)
from ...utils.statistical_analyzer import StatisticalAnalyzer
from ...data.models.user_behavior import BehaviorMetrics

logger = logging.getLogger(__name__)

class AnomalyType(Enum):
    """Types of anomalies that can be detected"""    STATISTICAL_OUTLIER = "statistical_outlier"
    BEHAVIORAL_DRIFT = "behavioral_drift"
    VOLUME_ANOMALY = "volume_anomaly"
    TEMPORAL_ANOMALY = "temporal_anomaly"
    CLUSTER_DEVIATION = "cluster_deviation"
    SEQUENCE_ANOMALY = "sequence_anomaly"
    CONTEXTUAL_ANOMALY = "contextual_anomaly"
    COLLECTIVE_ANOMALY = "collective_anomaly"

@dataclass
class AnomalyResult:
    """Individual anomaly detection result"""    anomaly_type: AnomalyType
    severity: float
    confidence: float
    description: str
    evidence: Dict[str, Any]
    timestamp: datetime
    affected_metrics: List[str]

@dataclass
class AnomalyDetectionOutput:
    """Comprehensive anomaly detection output"""    anomaly_score: float
    anomalies: List[AnomalyResult]
    baseline_comparison: Dict[str, float]
    risk_assessment: str
    recommended_actions: List[str]
    detection_metadata: Dict[str, Any]

class AnomalyDetectionEngine:
    """    Advanced Anomaly Detection Engine
    
    Detects anomalies through:
    - Statistical outlier detection
    - Machine learning clustering
    - Time series analysis
    - Behavioral drift detection
    - Contextual anomaly identification
    """    
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self.redis_client = redis_client
        self.statistical_analyzer = StatisticalAnalyzer()
        
        # ML models for anomaly detection
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.dbscan_clusterer = DBSCAN(eps=0.5, min_samples=5)
        self.pca_transformer = PCA(n_components=0.95)  # Retain 95% variance
        
        # Scalers for different feature types
        self.standard_scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
        
        # Anomaly detection thresholds
        self.anomaly_thresholds = {
            AnomalyType.STATISTICAL_OUTLIER: 0.7,
            AnomalyType.BEHAVIORAL_DRIFT: 0.6,
            AnomalyType.VOLUME_ANOMALY: 0.8,
            AnomalyType.TEMPORAL_ANOMALY: 0.65,
            AnomalyType.CLUSTER_DEVIATION: 0.75,
            AnomalyType.SEQUENCE_ANOMALY: 0.7,
            AnomalyType.CONTEXTUAL_ANOMALY: 0.6,
            AnomalyType.COLLECTIVE_ANOMALY: 0.8
        }
        
        # Feature importance weights
        self.feature_weights = {
            'session_duration': 0.15,
            'action_frequency': 0.20,
            'error_rate': 0.25,
            'response_time': 0.15,
            'resource_usage': 0.10,
            'geographic_location': 0.10,
            'device_consistency': 0.05
        }
        
        logger.info("Anomaly Detection Engine initialized successfully")

    async def detect_anomalies(
        self,
        user_id: str,
        current_session: Dict[str, Any],
        historical_baseline: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Comprehensive anomaly detection analysis
        
        Args:
            user_id: User identifier
            current_session: Current session data
            historical_baseline: Historical baseline data for comparison
            
        Returns:
            Comprehensive anomaly detection results
        """        try:
            # Extract feature vectors
            current_features = await self._extract_feature_vector(current_session)
            baseline_features = await self._get_baseline_features(user_id, historical_baseline)
            
            # Run parallel anomaly detection methods
            detection_tasks = await asyncio.gather(
                self._detect_statistical_outliers(current_features, baseline_features),
                self._detect_behavioral_drift(current_features, baseline_features),
                self._detect_volume_anomalies(current_session, historical_baseline),
                self._detect_temporal_anomalies(current_session, historical_baseline),
                self._detect_cluster_deviations(current_features, user_id),
                self._detect_sequence_anomalies(current_session),
                self._detect_contextual_anomalies(current_session, historical_baseline),
                return_exceptions=True
            )
            
            # Collect anomaly results
            all_anomalies = []
            for task_result in detection_tasks:
                if not isinstance(task_result, Exception) and task_result:
                    if isinstance(task_result, list):
                        all_anomalies.extend(task_result)
                    else:
                        all_anomalies.append(task_result)
            
            # Calculate composite anomaly score
            anomaly_score = await self._calculate_composite_anomaly_score(all_anomalies)
            
            # Filter and rank anomalies
            significant_anomalies = [
                anomaly for anomaly in all_anomalies 
                if anomaly.severity >= self.anomaly_thresholds.get(anomaly.anomaly_type, 0.5)
            ]
            significant_anomalies.sort(key=lambda a: a.severity * a.confidence, reverse=True)
            
            # Generate baseline comparison
            baseline_comparison = await self._generate_baseline_comparison(
                current_features, baseline_features
            )
            
            # Assess risk level
            risk_assessment = self._assess_risk_level(anomaly_score, significant_anomalies)
            
            # Generate recommendations
            recommendations = await self._generate_anomaly_recommendations(
                significant_anomalies, anomaly_score
            )
            
            # Update anomaly history
            await self._update_anomaly_history(user_id, significant_anomalies, anomaly_score)
            
            result = {
                'anomaly_score': anomaly_score,
                'anomalies': [
                    {
                        'type': anomaly.anomaly_type.value,
                        'severity': anomaly.severity,
                        'confidence': anomaly.confidence,
                        'description': anomaly.description,
                        'affected_metrics': anomaly.affected_metrics,
                        'evidence': anomaly.evidence
                    }
                    for anomaly in significant_anomalies
                ],
                'baseline_comparison': baseline_comparison,
                'risk_assessment': risk_assessment,
                'recommended_actions': recommendations,
                'detection_metadata': {
                    'total_anomalies_detected': len(all_anomalies),
                    'significant_anomalies': len(significant_anomalies),
                    'user_id': user_id,
                    'detection_timestamp': datetime.now().isoformat(),
                    'feature_vector_size': len(current_features)
                }
            }
            
            logger.info(
                f"Anomaly detection completed for user {user_id}: "
                f"score={anomaly_score:.3f}, anomalies={len(significant_anomalies)}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Anomaly detection failed for user {user_id}: {str(e)}")
            raise AnomalyDetectionError(f"Anomaly detection failed: {str(e)}")

    async def _extract_feature_vector(self, session_data: Dict[str, Any]) -> np.ndarray:
        """Extract numerical feature vector from session data"""        features = []
        
        # Session duration (minutes)
        session_start = session_data.get('start_time', datetime.now())
        session_duration = (datetime.now() - session_start).total_seconds() / 60
        features.append(session_duration)
        
        # Action frequency (actions per minute)
        actions = session_data.get('actions', [])
        action_frequency = len(actions) / max(session_duration, 1)
        features.append(action_frequency)
        
        # Error rate
        errors = session_data.get('errors', [])
        error_rate = len(errors) / max(len(actions), 1)
        features.append(error_rate)
        
        # Average response time
        response_times = session_data.get('response_times', [1000])  # Default 1s
        avg_response_time = np.mean(response_times) if response_times else 1000
        features.append(avg_response_time)
        
        # Resource usage metrics
        cpu_usage = session_data.get('cpu_usage', 0.1)
        memory_usage = session_data.get('memory_usage', 0.1)
        network_usage = session_data.get('network_usage', 0.1)
        features.extend([cpu_usage, memory_usage, network_usage])
        
        # Geographic stability
        locations = session_data.get('locations', [])
        location_variance = np.var([loc.get('latitude', 0) for loc in locations]) if locations else 0
        features.append(location_variance)
        
        # Device consistency score
        device_fingerprints = session_data.get('device_fingerprints', [])
        device_consistency = 1.0 if len(set(device_fingerprints)) <= 1 else 0.5
        features.append(device_consistency)
        
        # Content interaction metrics
        content_views = session_data.get('content_views', 0)
        content_uploads = session_data.get('content_uploads', 0)
        social_interactions = session_data.get('social_interactions', 0)
        features.extend([content_views, content_uploads, social_interactions])
        
        return np.array(features)

    async def _get_baseline_features(
        self, 
        user_id: str, 
        historical_baseline: Dict[str, Any]
    ) -> np.ndarray:
        """Get baseline feature vector for user"""        try:
            # Try to get from cache first
            cache_key = f"baseline_features:{user_id}"
            cached_features = await self.redis_client.get(cache_key)
            
            if cached_features:
                return np.array(eval(cached_features))
                
            # Calculate from historical baseline
            baseline_features = [
                historical_baseline.get('avg_session_duration', 30),  # 30 minutes
                historical_baseline.get('avg_action_frequency', 2.0),  # 2 actions/min
                historical_baseline.get('avg_error_rate', 0.05),  # 5% error rate
                historical_baseline.get('avg_response_time', 500),  # 500ms
                historical_baseline.get('avg_cpu_usage', 0.2),  # 20% CPU
                historical_baseline.get('avg_memory_usage', 0.3),  # 30% memory
                historical_baseline.get('avg_network_usage', 0.1),  # 10% network
                historical_baseline.get('location_variance', 0.001),  # Low variance
                historical_baseline.get('device_consistency', 0.9),  # High consistency
                historical_baseline.get('avg_content_views', 10),
                historical_baseline.get('avg_content_uploads', 1),
                historical_baseline.get('avg_social_interactions', 5)
            ]
            
            baseline_array = np.array(baseline_features)
            
            # Cache for future use
            await self.redis_client.setex(cache_key, 7200, str(baseline_array.tolist()))
            
            return baseline_array
            
        except Exception as e:
            logger.error(f"Failed to get baseline features for user {user_id}: {str(e)}")
            # Return default baseline
            return np.array([30, 2.0, 0.05, 500, 0.2, 0.3, 0.1, 0.001, 0.9, 10, 1, 5])

    async def _detect_statistical_outliers(
        self,
        current_features: np.ndarray,
        baseline_features: np.ndarray
    ) -> Optional[AnomalyResult]:
        """Detect statistical outliers using various methods"""        try:
            # Z-score based outlier detection
            z_scores = np.abs((current_features - baseline_features) / (np.std(baseline_features) + 1e-6))
            max_z_score = np.max(z_scores)
            
            # Modified Z-score using median
            median_baseline = np.median(baseline_features)
            mad = np.median(np.abs(baseline_features - median_baseline))
            modified_z_scores = 0.6745 * (current_features - median_baseline) / (mad + 1e-6)
            max_modified_z = np.max(np.abs(modified_z_scores))
            
            # Determine if outlier
            is_outlier = max_z_score > 3.0 or max_modified_z > 3.5
            
            if is_outlier:
                # Find which features are outliers
                outlier_indices = np.where((z_scores > 3.0) | (np.abs(modified_z_scores) > 3.5))[0]
                feature_names = [
                    'session_duration', 'action_frequency', 'error_rate', 'response_time',
                    'cpu_usage', 'memory_usage', 'network_usage', 'location_variance',
                    'device_consistency', 'content_views', 'content_uploads', 'social_interactions'
                ]
                
                outlier_features = [feature_names[i] for i in outlier_indices if i < len(feature_names)]
                
                severity = min(1.0, max(max_z_score / 10, max_modified_z / 10))
                confidence = min(1.0, (max_z_score + max_modified_z) / 14)
                
                return AnomalyResult(
                    anomaly_type=AnomalyType.STATISTICAL_OUTLIER,
                    severity=severity,
                    confidence=confidence,
                    description=f"Statistical outliers detected in {len(outlier_features)} features",
                    evidence={
                        'max_z_score': max_z_score,
                        'max_modified_z_score': max_modified_z,
                        'outlier_features': outlier_features,
                        'z_scores': z_scores.tolist(),
                        'current_values': current_features.tolist(),
                        'baseline_values': baseline_features.tolist()
                    },
                    timestamp=datetime.now(),
                    affected_metrics=outlier_features
                )
                
            return None
            
        except Exception as e:
            logger.error(f"Statistical outlier detection failed: {str(e)}")
            return None

    async def _detect_behavioral_drift(
        self,
        current_features: np.ndarray,
        baseline_features: np.ndarray
    ) -> Optional[AnomalyResult]:
        """Detect gradual behavioral drift"""        try:
            # Calculate euclidean distance between current and baseline
            euclidean_distance = np.linalg.norm(current_features - baseline_features)
            
            # Calculate cosine similarity
            dot_product = np.dot(current_features, baseline_features)
            norms = np.linalg.norm(current_features) * np.linalg.norm(baseline_features)
            cosine_similarity = dot_product / (norms + 1e-6)
            
            # Calculate percentage changes
            percentage_changes = np.abs((current_features - baseline_features) / (baseline_features + 1e-6))
            max_percentage_change = np.max(percentage_changes)
            
            # Determine drift severity
            normalized_distance = euclidean_distance / (np.linalg.norm(baseline_features) + 1e-6)
            similarity_score = 1 - cosine_similarity
            
            drift_score = (normalized_distance + similarity_score + max_percentage_change) / 3
            
            if drift_score > 0.3:  # Threshold for behavioral drift
                # Find features with highest drift
                high_drift_indices = np.where(percentage_changes > 0.2)[0]
                feature_names = [
                    'session_duration', 'action_frequency', 'error_rate', 'response_time',
                    'cpu_usage', 'memory_usage', 'network_usage', 'location_variance',
                    'device_consistency', 'content_views', 'content_uploads', 'social_interactions'
                ]
                
                drift_features = [feature_names[i] for i in high_drift_indices if i < len(feature_names)]
                
                return AnomalyResult(
                    anomaly_type=AnomalyType.BEHAVIORAL_DRIFT,
                    severity=min(1.0, drift_score),
                    confidence=0.8,
                    description=f"Behavioral drift detected across {len(drift_features)} features",
                    evidence={
                        'drift_score': drift_score,
                        'euclidean_distance': euclidean_distance,
                        'cosine_similarity': cosine_similarity,
                        'max_percentage_change': max_percentage_change,
                        'drift_features': drift_features,
                        'percentage_changes': percentage_changes.tolist()
                    },
                    timestamp=datetime.now(),
                    affected_metrics=drift_features
                )
                
            return None
            
        except Exception as e:
            logger.error(f"Behavioral drift detection failed: {str(e)}")
            return None

    async def _detect_volume_anomalies(
        self,
        current_session: Dict[str, Any],
        historical_baseline: Dict[str, Any]
    ) -> Optional[AnomalyResult]:
        """Detect unusual volume patterns"""        try:
            # Current session metrics
            actions_count = len(current_session.get('actions', []))
            content_interactions = current_session.get('content_views', 0) + current_session.get('content_uploads', 0)
            errors_count = len(current_session.get('errors', []))
            
            # Baseline comparisons
            baseline_actions = historical_baseline.get('avg_actions_per_session', 50)
            baseline_content = historical_baseline.get('avg_content_interactions', 15)
            baseline_errors = historical_baseline.get('avg_errors_per_session', 2)
            
            # Calculate volume ratios
            action_ratio = actions_count / max(baseline_actions, 1)
            content_ratio = content_interactions / max(baseline_content, 1)
            error_ratio = errors_count / max(baseline_errors, 1)
            
            # Detect significant volume changes
            volume_anomalies = []
            if action_ratio > 5 or action_ratio < 0.1:  # 5x increase or 90% decrease
                volume_anomalies.append(('actions', action_ratio))
                
            if content_ratio > 10 or content_ratio < 0.05:  # 10x increase or 95% decrease
                volume_anomalies.append(('content_interactions', content_ratio))
                
            if error_ratio > 20:  # 20x increase in errors
                volume_anomalies.append(('errors', error_ratio))
                
            if volume_anomalies:
                max_ratio = max(ratio for _, ratio in volume_anomalies)
                severity = min(1.0, np.log10(max_ratio + 1) / 2)  # Logarithmic scaling
                
                return AnomalyResult(
                    anomaly_type=AnomalyType.VOLUME_ANOMALY,
                    severity=severity,
                    confidence=0.9,
                    description=f"Volume anomalies detected in {len(volume_anomalies)} categories",
                    evidence={
                        'volume_anomalies': {metric: ratio for metric, ratio in volume_anomalies},
                        'current_counts': {
                            'actions': actions_count,
                            'content_interactions': content_interactions,
                            'errors': errors_count
                        },
                        'baseline_counts': {
                            'actions': baseline_actions,
                            'content_interactions': baseline_content,
                            'errors': baseline_errors
                        }
                    },
                    timestamp=datetime.now(),
                    affected_metrics=[metric for metric, _ in volume_anomalies]
                )
                
            return None
            
        except Exception as e:
            logger.error(f"Volume anomaly detection failed: {str(e)}")
            return None

    async def _detect_temporal_anomalies(
        self,
        current_session: Dict[str, Any],
        historical_baseline: Dict[str, Any]
    ) -> Optional[AnomalyResult]:
        """Detect temporal pattern anomalies"""        try:
            # Extract timestamps from session actions
            actions = current_session.get('actions', [])
            if len(actions) < 5:  # Need sufficient data
                return None
                
            timestamps = [action.get('timestamp', 0) for action in actions]
            timestamps.sort()
            
            # Calculate inter-arrival times
            intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
            
            if not intervals:
                return None
                
            # Statistical analysis of intervals
            mean_interval = np.mean(intervals)
            std_interval = np.std(intervals)
            cv_interval = std_interval / (mean_interval + 1e-6)  # Coefficient of variation
            
            # Compare with baseline
            baseline_mean_interval = historical_baseline.get('avg_action_interval', 30)  # 30 seconds
            baseline_cv = historical_baseline.get('action_interval_cv', 0.5)  # 50% CV
            
            # Detect anomalies
            temporal_anomalies = []
            
            # Extremely regular patterns (bot-like)
            if cv_interval < 0.1 and len(intervals) > 10:
                temporal_anomalies.append('extremely_regular_pattern')
                
            # Extremely irregular patterns
            if cv_interval > 2.0:
                temporal_anomalies.append('extremely_irregular_pattern')
                
            # Significant change in timing
            interval_ratio = mean_interval / max(baseline_mean_interval, 1)
            if interval_ratio > 5 or interval_ratio < 0.2:
                temporal_anomalies.append('timing_pattern_change')
                
            # Burst patterns
            burst_count = sum(1 for interval in intervals if interval < 1)  # < 1 second
            if burst_count > len(intervals) * 0.8:  # 80% burst actions
                temporal_anomalies.append('burst_pattern')
                
            if temporal_anomalies:
                severity = min(1.0, len(temporal_anomalies) * 0.3 + abs(cv_interval - baseline_cv))
                
                return AnomalyResult(
                    anomaly_type=AnomalyType.TEMPORAL_ANOMALY,
                    severity=severity,
                    confidence=0.8,
                    description=f"Temporal anomalies detected: {', '.join(temporal_anomalies)}",
                    evidence={
                        'temporal_anomalies': temporal_anomalies,
                        'mean_interval': mean_interval,
                        'coefficient_of_variation': cv_interval,
                        'baseline_mean_interval': baseline_mean_interval,
                        'baseline_cv': baseline_cv,
                        'total_intervals': len(intervals),
                        'burst_count': burst_count
                    },
                    timestamp=datetime.now(),
                    affected_metrics=['action_timing', 'temporal_patterns']
                )
                
            return None
            
        except Exception as e:
            logger.error(f"Temporal anomaly detection failed: {str(e)}")
            return None

    async def _detect_cluster_deviations(
        self,
        current_features: np.ndarray,
        user_id: str
    ) -> Optional[AnomalyResult]:
        """Detect deviations from user's typical behavior cluster"""        try:
            # Get historical feature vectors for clustering
            cluster_features = await self._get_cluster_features(user_id)
            
            if len(cluster_features) < 10:  # Need sufficient historical data
                return None
                
            # Normalize features
            all_features = np.vstack([cluster_features, current_features.reshape(1, -1)])
            normalized_features = self.standard_scaler.fit_transform(all_features)
            
            # Perform clustering
            clusters = self.dbscan_clusterer.fit_predict(normalized_features)
            
            # Check if current session is an outlier
            current_cluster = clusters[-1]  # Last item is current session
            
            if current_cluster == -1:  # DBSCAN outlier
                # Calculate distance to nearest cluster
                cluster_centers = []
                unique_clusters = set(clusters[:-1])  # Exclude current session
                unique_clusters.discard(-1)  # Remove outlier label
                
                for cluster_id in unique_clusters:
                    cluster_points = normalized_features[clusters == cluster_id]
                    if len(cluster_points) > 0:
                        cluster_centers.append(np.mean(cluster_points, axis=0))
                        
                if cluster_centers:
                    current_point = normalized_features[-1]
                    distances = [np.linalg.norm(current_point - center) for center in cluster_centers]
                    min_distance = min(distances)
                    
                    # Normalize distance for severity calculation
                    severity = min(1.0, min_distance / 3.0)
                    
                    return AnomalyResult(
                        anomaly_type=AnomalyType.CLUSTER_DEVIATION,
                        severity=severity,
                        confidence=0.85,
                        description="Current session deviates significantly from typical behavior clusters",
                        evidence={
                            'cluster_label': current_cluster,
                            'distance_to_nearest_cluster': min_distance,
                            'total_clusters': len(unique_clusters),
                            'historical_sessions': len(cluster_features)
                        },
                        timestamp=datetime.now(),
                        affected_metrics=['behavioral_cluster']
                    )
                    
            return None
            
        except Exception as e:
            logger.error(f"Cluster deviation detection failed: {str(e)}")
            return None

    async def _detect_sequence_anomalies(
        self, 
        current_session: Dict[str, Any]
    ) -> Optional[AnomalyResult]:
        """Detect anomalous action sequences"""        try:
            actions = current_session.get('actions', [])
            
            if len(actions) < 5:
                return None
                
            # Extract action sequence
            action_types = [action.get('type', 'unknown') for action in actions]
            
            # Look for unusual sequences
            sequence_anomalies = []
            
            # Repetitive sequences (potential bot behavior)
            for i in range(len(action_types) - 2):
                sequence = tuple(action_types[i:i+3])
                count = 0
                for j in range(len(action_types) - 2):
                    if tuple(action_types[j:j+3]) == sequence:
                        count += 1
                        
                if count > len(action_types) * 0.3:  # 30% of all sequences are the same
                    sequence_anomalies.append(f"repetitive_sequence: {sequence}")
                    
            # Unusual action combinations
            unusual_combinations = [
                ('login', 'delete_account'),
                ('upload', 'delete', 'upload'),  # Upload, delete, upload again quickly
                ('admin_access', 'bulk_download')
            ]
            
            for combo in unusual_combinations:
                if all(action in action_types for action in combo):
                    # Check if they occur in sequence within reasonable time
                    indices = [i for i, action in enumerate(action_types) if action in combo]
                    if max(indices) - min(indices) < 10:  # Within 10 actions
                        sequence_anomalies.append(f"unusual_combination: {combo}")
                        
            if sequence_anomalies:
                severity = min(1.0, len(sequence_anomalies) * 0.4)
                
                return AnomalyResult(
                    anomaly_type=AnomalyType.SEQUENCE_ANOMALY,
                    severity=severity,
                    confidence=0.75,
                    description=f"Unusual action sequences detected: {len(sequence_anomalies)} patterns",
                    evidence={
                        'sequence_anomalies': sequence_anomalies,
                        'action_sequence': action_types,
                        'total_actions': len(actions)
                    },
                    timestamp=datetime.now(),
                    affected_metrics=['action_sequences', 'behavioral_patterns']
                )
                
            return None
            
        except Exception as e:
            logger.error(f"Sequence anomaly detection failed: {str(e)}")
            return None

    async def _detect_contextual_anomalies(
        self,
        current_session: Dict[str, Any],
        historical_baseline: Dict[str, Any]
    ) -> Optional[AnomalyResult]:
        """Detect contextual anomalies based on external factors"""        try:
            contextual_anomalies = []
            
            # Time-based contextual anomalies
            current_time = datetime.now()
            session_hour = current_time.hour
            
            # Check if session is at unusual time
            typical_hours = historical_baseline.get('typical_hours', list(range(9, 18)))  # 9 AM - 6 PM
            if session_hour not in typical_hours:
                contextual_anomalies.append(f"unusual_time: {session_hour}:00")
                
            # Geographic context
            current_location = current_session.get('location', {})
            typical_locations = historical_baseline.get('typical_locations', [])
            
            if current_location and typical_locations:
                current_coords = (current_location.get('latitude', 0), current_location.get('longitude', 0))
                
                # Check if location is far from typical locations
                is_typical_location = False
                for typical_loc in typical_locations:
                    typical_coords = (typical_loc.get('latitude', 0), typical_loc.get('longitude', 0))
                    distance = self._calculate_distance(current_coords, typical_coords)
                    
                    if distance < 50:  # Within 50 km
                        is_typical_location = True
                        break
                        
                if not is_typical_location:
                    contextual_anomalies.append("unusual_geographic_location")
                    
            # Device context
            current_device = current_session.get('device_type', 'unknown')
            typical_devices = historical_baseline.get('typical_devices', [])
            
            if current_device not in typical_devices and typical_devices:
                contextual_anomalies.append(f"unusual_device: {current_device}")
                
            # Platform context
            current_platform = current_session.get('platform', 'unknown')
            typical_platforms = historical_baseline.get('typical_platforms', [])
            
            if current_platform not in typical_platforms and typical_platforms:
                contextual_anomalies.append(f"unusual_platform: {current_platform}")
                
            if contextual_anomalies:
                severity = min(1.0, len(contextual_anomalies) * 0.25)
                
                return AnomalyResult(
                    anomaly_type=AnomalyType.CONTEXTUAL_ANOMALY,
                    severity=severity,
                    confidence=0.7,
                    description=f"Contextual anomalies detected: {len(contextual_anomalies)} factors",
                    evidence={
                        'contextual_anomalies': contextual_anomalies,
                        'session_context': {
                            'time': current_time.isoformat(),
                            'location': current_location,
                            'device': current_device,
                            'platform': current_platform
                        },
                        'typical_context': {
                            'hours': typical_hours,
                            'locations': typical_locations[:3],  # Limit for privacy
                            'devices': typical_devices,
                            'platforms': typical_platforms
                        }
                    },
                    timestamp=datetime.now(),
                    affected_metrics=['contextual_factors']
                )
                
            return None
            
        except Exception as e:
            logger.error(f"Contextual anomaly detection failed: {str(e)}")
            return None

    async def _get_cluster_features(self, user_id: str) -> np.ndarray:
        """Get historical feature vectors for clustering"""        try:
            cache_key = f"cluster_features:{user_id}"
            cached_features = await self.redis_client.get(cache_key)
            
            if cached_features:
                import json
                features_list = json.loads(cached_features)
                return np.array(features_list)
                
            # Return empty array if no historical data
            return np.array([])
            
        except Exception as e:
            logger.error(f"Failed to get cluster features for user {user_id}: {str(e)}")
            return np.array([])

    def _calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate distance between two geographic coordinates in km"""        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Haversine formula
        R = 6371  # Earth's radius in km
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        delta_lat = np.radians(lat2 - lat1)
        delta_lon = np.radians(lon2 - lon1)
        
        a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c

    async def _calculate_composite_anomaly_score(self, anomalies: List[AnomalyResult]) -> float:
        """Calculate composite anomaly score from all detected anomalies"""        if not anomalies:
            return 0.0
            
        # Weight by severity and confidence
        weighted_scores = []
        for anomaly in anomalies:
            weighted_score = anomaly.severity * anomaly.confidence
            weighted_scores.append(weighted_score)
            
        # Use maximum score with diminishing returns for additional anomalies
        sorted_scores = sorted(weighted_scores, reverse=True)
        composite_score = sorted_scores[0] if sorted_scores else 0.0
        
        # Add diminishing contribution from additional anomalies
        for i, score in enumerate(sorted_scores[1:], 1):
            composite_score += score * (0.5 ** i)
            
        return min(1.0, composite_score)

    async def _generate_baseline_comparison(
        self,
        current_features: np.ndarray,
        baseline_features: np.ndarray
    ) -> Dict[str, float]:
        """Generate comparison metrics between current and baseline features"""        feature_names = [
            'session_duration', 'action_frequency', 'error_rate', 'response_time',
            'cpu_usage', 'memory_usage', 'network_usage', 'location_variance',
            'device_consistency', 'content_views', 'content_uploads', 'social_interactions'
        ]
        
        comparison = {}
        
        for i, feature_name in enumerate(feature_names):
            if i < len(current_features) and i < len(baseline_features):
                current_value = current_features[i]
                baseline_value = baseline_features[i]
                
                # Calculate percentage change
                percentage_change = ((current_value - baseline_value) / (baseline_value + 1e-6)) * 100
                comparison[feature_name] = {
                    'current': float(current_value),
                    'baseline': float(baseline_value),
                    'percentage_change': float(percentage_change)
                }
                
        return comparison

    def _assess_risk_level(self, anomaly_score: float, anomalies: List[AnomalyResult]) -> str:
        """Assess overall risk level based on anomaly score and types"""        if anomaly_score >= 0.8:
            return "CRITICAL"
        elif anomaly_score >= 0.6:
            return "HIGH"
        elif anomaly_score >= 0.4:
            return "MEDIUM"
        elif anomaly_score >= 0.2:
            return "LOW"
        else:
            return "MINIMAL"

    async def _generate_anomaly_recommendations(
        self,
        anomalies: List[AnomalyResult],
        anomaly_score: float
    ) -> List[str]:
        """Generate recommended actions based on detected anomalies"""        recommendations = []
        
        if anomaly_score >= 0.8:
            recommendations.extend([
                "Immediately investigate user activity",
                "Consider temporary account restrictions",
                "Alert security team for manual review"
            ])
        elif anomaly_score >= 0.6:
            recommendations.extend([
                "Increase monitoring frequency",
                "Flag for enhanced review",
                "Request additional user verification"
            ])
        elif anomaly_score >= 0.4:
            recommendations.extend([
                "Monitor for pattern persistence",
                "Log for trend analysis",
                "Consider user notification if appropriate"
            ])
            
        # Specific recommendations based on anomaly types
        anomaly_types = {anomaly.anomaly_type for anomaly in anomalies}
        
        if AnomalyType.STATISTICAL_OUTLIER in anomaly_types:
            recommendations.append("Investigate unusual metric values")
            
        if AnomalyType.BEHAVIORAL_DRIFT in anomaly_types:
            recommendations.append("Analyze long-term behavioral changes")
            
        if AnomalyType.VOLUME_ANOMALY in anomaly_types:
            recommendations.append("Review activity volume patterns")
            
        if AnomalyType.TEMPORAL_ANOMALY in anomaly_types:
            recommendations.append("Examine timing patterns for automation")
            
        if AnomalyType.CLUSTER_DEVIATION in anomaly_types:
            recommendations.append("Compare with user's historical behavior")
            
        if AnomalyType.SEQUENCE_ANOMALY in anomaly_types:
            recommendations.append("Investigate action sequence patterns")
            
        if AnomalyType.CONTEXTUAL_ANOMALY in anomaly_types:
            recommendations.append("Verify user context and environment")
            
        return list(set(recommendations))  # Remove duplicates

    async def _update_anomaly_history(
        self,
        user_id: str,
        anomalies: List[AnomalyResult],
        anomaly_score: float
    ):
        """Update user's anomaly detection history"""        try:
            history_key = f"anomaly_history:{user_id}"
            
            anomaly_record = {
                'timestamp': datetime.now().isoformat(),
                'anomaly_score': anomaly_score,
                'anomaly_count': len(anomalies),
                'anomaly_types': [anomaly.anomaly_type.value for anomaly in anomalies],
                'max_severity': max([anomaly.severity for anomaly in anomalies], default=0.0)
            }
            
            # Add to history (keep last 50 records)
            import json
            await self.redis_client.lpush(history_key, json.dumps(anomaly_record))
            await self.redis_client.ltrim(history_key, 0, 49)
            await self.redis_client.expire(history_key, 86400 * 30)  # 30 days
            
        except Exception as e:
            logger.error(f"Failed to update anomaly history for user {user_id}: {str(e)}")

    async def get_anomaly_trends(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get anomaly trends for a user over time"""        try:
            history_key = f"anomaly_history:{user_id}"
            history_records = await self.redis_client.lrange(history_key, 0, -1)
            
            if not history_records:
                return {
                    'trends': [],
                    'analysis': 'No anomaly history available'
                }
                
            # Parse records
            import json
            parsed_records = []
            for record in history_records:
                try:
                    parsed_records.append(json.loads(record))
                except:
                    continue
                    
            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_records = [
                record for record in parsed_records
                if datetime.fromisoformat(record['timestamp']) > cutoff_date
            ]
            
            if not recent_records:
                return {
                    'trends': [],
                    'analysis': f'No anomalies in the last {days} days'
                }
                
            # Calculate trends
            anomaly_scores = [r['anomaly_score'] for r in recent_records]
            anomaly_counts = [r['anomaly_count'] for r in recent_records]
            
            # Count anomaly types
            all_types = []
            for record in recent_records:
                all_types.extend(record.get('anomaly_types', []))
                
            from collections import Counter
            type_counts = Counter(all_types)
            
            trends = {
                'average_anomaly_score': np.mean(anomaly_scores),
                'max_anomaly_score': max(anomaly_scores),
                'total_anomalies': sum(anomaly_counts),
                'anomaly_frequency': len([s for s in anomaly_scores if s > 0.3]),
                'most_common_types': dict(type_counts.most_common(5)),
                'trend_direction': self._calculate_score_trend(
                    [datetime.fromisoformat(r['timestamp']) for r in recent_records],
                    anomaly_scores
                )
            }
            
            return {
                'trends': trends,
                'data_points': len(recent_records),
                'time_range_days': days,
                'analysis': 'Trends calculated successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to get anomaly trends for user {user_id}: {str(e)}")
            return {'error': str(e)}

    def _calculate_score_trend(self, timestamps: List[datetime], scores: List[float]) -> float:
        """Calculate trend direction for anomaly scores over time"""        if len(timestamps) < 2 or len(scores) < 2:
            return 0.0
            
        # Convert timestamps to numeric values
        numeric_times = [(t - timestamps[0]).total_seconds() for t in timestamps]
        
        # Calculate correlation coefficient
        correlation_matrix = np.corrcoef(numeric_times, scores)
        correlation = correlation_matrix[0, 1]
        
        return correlation if not np.isnan(correlation) else 0.0
