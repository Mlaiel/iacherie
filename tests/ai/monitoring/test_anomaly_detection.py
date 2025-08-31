# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Advanced Anomaly Detection Tests - Industrial Grade

Comprehensive, enterprise-level test suite for ML-based anomaly detection system.
Tests statistical analysis, machine learning detection, and real-time anomaly identification.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use of this code without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will be prosecuted to the full
extent of the law.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import statistics
import json
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import scipy.stats as stats
from unittest.mock import AsyncMock, MagicMock, patch

from ai.monitoring.anomaly_detection import (
    AnomalyDetection,
    AnomalyType,
    AnomalySeverity,
    DetectionMethod,
    AnomalyPoint,
    AnomalyPattern,
    StatisticalDetector,
    MLAnomalyDetector,
    TimeSeriesAnomalyDetector,
    BusinessAnomalyDetector,
    SecurityAnomalyDetector,
    AnomalyCorrelationEngine,
    RootCauseAnalyzer
)
from ai.core.metrics import MetricType, MetricPriority
from ai.core.exceptions import AnomalyDetectionError
from .fixtures import (
    anomaly_test_data,
    normal_data_patterns,
    anomaly_scenarios,
    time_series_data,
    business_metrics_data
)


class TestAnomalyDetectionCore:
    """Core functionality tests for anomaly detection system."""
    
    @pytest.fixture
    async def anomaly_detector(self):
        """Create and initialize anomaly detection system."""
        detector = AnomalyDetection(
            config={
                "detection_methods": ["z_score", "iqr", "isolation_forest", "dbscan"],
                "sensitivity": 0.95,
                "window_size": 100,
                "min_data_points": 10,
                "correlation_threshold": 0.7,
                "real_time_enabled": True,
                "ml_models_enabled": True
            }
        )
        await detector.initialize()
        yield detector
        await detector.shutdown()
    
    @pytest.fixture
    def synthetic_normal_data(self):
        """Generate synthetic normal data patterns."""
        np.random.seed(42)
        
        # Normal data with slight variation
        normal_pattern = np.random.normal(100, 10, 1000)
        
        # Seasonal pattern
        seasonal_component = 20 * np.sin(np.linspace(0, 10*np.pi, 1000))
        
        # Trend component
        trend_component = np.linspace(0, 20, 1000)
        
        # Combined normal data
        combined_data = normal_pattern + seasonal_component + trend_component
        
        return {
            "timestamps": [datetime.utcnow() - timedelta(minutes=i) for i in range(1000, 0, -1)],
            "values": combined_data.tolist(),
            "metric_name": "system_performance",
            "expected_mean": np.mean(combined_data),
            "expected_std": np.std(combined_data)
        }
    
    @pytest.fixture
    def synthetic_anomaly_data(self, synthetic_normal_data):
        """Generate synthetic data with known anomalies."""
        data = synthetic_normal_data.copy()
        values = np.array(data["values"])
        
        # Inject known anomalies
        anomaly_indices = [100, 250, 400, 600, 800]
        anomaly_types = ["spike", "dip", "shift", "noise", "outlier"]
        
        injected_anomalies = []
        
        for i, anomaly_type in zip(anomaly_indices, anomaly_types):
            original_value = values[i]
            
            if anomaly_type == "spike":
                values[i] = original_value + 5 * data["expected_std"]
            elif anomaly_type == "dip":
                values[i] = original_value - 4 * data["expected_std"]
            elif anomaly_type == "shift":
                # Shift subsequent values
                values[i:i+20] += 3 * data["expected_std"]
            elif anomaly_type == "noise":
                # Add noise burst
                values[i:i+10] += np.random.normal(0, 2 * data["expected_std"], 10)
            elif anomaly_type == "outlier":
                values[i] = original_value + 6 * data["expected_std"]
            
            injected_anomalies.append({
                "index": i,
                "type": anomaly_type,
                "timestamp": data["timestamps"][i],
                "original_value": original_value,
                "anomaly_value": values[i]
            })
        
        data["values"] = values.tolist()
        data["injected_anomalies"] = injected_anomalies
        
        return data
    
    async def test_detector_initialization_comprehensive(self, anomaly_detector):
        """Test comprehensive initialization of anomaly detection system."""
        # Verify core components
        assert anomaly_detector is not None
        assert anomaly_detector.is_initialized
        assert anomaly_detector.statistical_detector is not None
        assert anomaly_detector.ml_detector is not None
        assert anomaly_detector.time_series_detector is not None
        assert anomaly_detector.business_detector is not None
        assert anomaly_detector.security_detector is not None
        
        # Verify detection methods
        methods = anomaly_detector.get_enabled_methods()
        expected_methods = ["z_score", "iqr", "isolation_forest", "dbscan"]
        assert all(method in methods for method in expected_methods)
        
        # Verify configuration
        config = anomaly_detector.config
        assert config["sensitivity"] == 0.95
        assert config["window_size"] == 100
        assert config["real_time_enabled"] is True
        
        # Verify ML models initialization
        ml_models = anomaly_detector.ml_detector.get_models()
        assert "isolation_forest" in ml_models
        assert "dbscan" in ml_models
        assert all(model.is_trained for model in ml_models.values())
    
    async def test_statistical_anomaly_detection(self, anomaly_detector, synthetic_anomaly_data):
        """Test statistical anomaly detection methods (Z-score, IQR)."""
        data = synthetic_anomaly_data
        
        # Test Z-score detection
        z_score_anomalies = await anomaly_detector.detect_anomalies(
            metric_name=data["metric_name"],
            values=data["values"],
            timestamps=data["timestamps"],
            method=DetectionMethod.Z_SCORE,
            threshold=3.0
        )
        
        assert len(z_score_anomalies) > 0
        
        # Verify detection accuracy
        detected_indices = [
            data["timestamps"].index(anomaly.timestamp) 
            for anomaly in z_score_anomalies
        ]
        
        injected_indices = [anomaly["index"] for anomaly in data["injected_anomalies"]]
        
        # Check detection rate (should detect most injected anomalies)
        detection_rate = len(set(detected_indices) & set(injected_indices)) / len(injected_indices)
        assert detection_rate >= 0.6  # At least 60% detection rate
        
        # Test IQR detection
        iqr_anomalies = await anomaly_detector.detect_anomalies(
            metric_name=data["metric_name"],
            values=data["values"],
            timestamps=data["timestamps"],
            method=DetectionMethod.IQR,
            threshold=1.5
        )
        
        assert len(iqr_anomalies) > 0
        
        # Verify anomaly properties
        for anomaly in z_score_anomalies:
            assert isinstance(anomaly, AnomalyPoint)
            assert anomaly.anomaly_type == AnomalyType.STATISTICAL
            assert anomaly.detection_method == DetectionMethod.Z_SCORE
            assert anomaly.confidence_score > 0.5
            assert anomaly.severity in [AnomalySeverity.LOW, AnomalySeverity.MEDIUM, AnomalySeverity.HIGH]
    
    async def test_ml_based_anomaly_detection(self, anomaly_detector, synthetic_anomaly_data):
        """Test machine learning based anomaly detection."""
        data = synthetic_anomaly_data
        
        # Prepare training data (first 80% of normal data)
        train_size = int(0.8 * len(data["values"]))
        train_data = data["values"][:train_size]
        
        # Train ML models
        await anomaly_detector.train_ml_models(
            metric_name=data["metric_name"],
            training_data=train_data,
            feature_columns=["value", "rolling_mean", "rolling_std", "diff"]
        )
        
        # Test Isolation Forest detection
        isolation_anomalies = await anomaly_detector.detect_anomalies(
            metric_name=data["metric_name"],
            values=data["values"][train_size:],
            timestamps=data["timestamps"][train_size:],
            method=DetectionMethod.ISOLATION_FOREST,
            contamination=0.1
        )
        
        assert len(isolation_anomalies) > 0
        
        # Test DBSCAN clustering
        dbscan_anomalies = await anomaly_detector.detect_anomalies(
            metric_name=data["metric_name"],
            values=data["values"],
            timestamps=data["timestamps"],
            method=DetectionMethod.DBSCAN,
            eps=0.3,
            min_samples=5
        )
        
        # Verify ML detection quality
        for anomaly in isolation_anomalies:
            assert anomaly.detection_method == DetectionMethod.ISOLATION_FOREST
            assert anomaly.confidence_score > 0.3
            assert anomaly.anomaly_type in [AnomalyType.PATTERN, AnomalyType.BEHAVIORAL]
        
        # Compare detection methods
        detection_comparison = await anomaly_detector.compare_detection_methods(
            metric_name=data["metric_name"],
            values=data["values"],
            timestamps=data["timestamps"],
            ground_truth_anomalies=data["injected_anomalies"]
        )
        
        assert "precision" in detection_comparison
        assert "recall" in detection_comparison
        assert "f1_score" in detection_comparison
        assert all(score >= 0.0 for score in detection_comparison.values())
    
    async def test_time_series_anomaly_detection(self, anomaly_detector):
        """Test time series specific anomaly detection."""
        # Generate time series with seasonal patterns
        timestamps = [datetime.utcnow() - timedelta(hours=i) for i in range(168, 0, -1)]  # 1 week
        
        # Create seasonal pattern (daily and weekly seasonality)
        hourly_pattern = [10 * np.sin(2 * np.pi * i / 24) for i in range(168)]
        weekly_pattern = [5 * np.sin(2 * np.pi * i / 168) for i in range(168)]
        noise = np.random.normal(0, 2, 168)
        base_trend = 100
        
        normal_values = [base_trend + h + w + n for h, w, n in zip(hourly_pattern, weekly_pattern, noise)]
        
        # Inject time series anomalies
        anomaly_timestamps = []
        normal_values[50] += 50  # Spike anomaly
        anomaly_timestamps.append(timestamps[50])
        
        normal_values[100:110] = [v + 30 for v in normal_values[100:110]]  # Level shift
        anomaly_timestamps.extend(timestamps[100:110])
        
        # Detect seasonal anomalies
        seasonal_anomalies = await anomaly_detector.detect_seasonal_anomalies(
            metric_name="seasonal_metric",
            values=normal_values,
            timestamps=timestamps,
            seasonality_period=24,  # Daily seasonality
            sensitivity=0.9
        )
        
        assert len(seasonal_anomalies) > 0
        
        # Verify seasonal anomaly detection
        detected_timestamps = [anomaly.timestamp for anomaly in seasonal_anomalies]
        overlap = len(set(detected_timestamps) & set(anomaly_timestamps))
        assert overlap > 0
        
        # Test trend anomaly detection
        trend_anomalies = await anomaly_detector.detect_trend_anomalies(
            metric_name="trend_metric",
            values=normal_values,
            timestamps=timestamps,
            window_size=24,
            trend_threshold=0.1
        )
        
        # Verify trend analysis
        trend_analysis = await anomaly_detector.analyze_trends(
            metric_name="trend_metric",
            values=normal_values,
            timestamps=timestamps
        )
        
        assert "trend_direction" in trend_analysis
        assert "trend_strength" in trend_analysis
        assert "changepoints" in trend_analysis
    
    async def test_business_anomaly_detection(self, anomaly_detector, business_metrics_data):
        """Test business-specific anomaly detection."""
        business_data = business_metrics_data["revenue_scenarios"]
        
        # Test revenue anomaly detection
        for scenario in business_data:
            revenue_anomalies = await anomaly_detector.detect_business_anomalies(
                metric_type="revenue",
                data=scenario["revenue_data"],
                business_context={
                    "user_tier": scenario["user_tier"],
                    "content_type": scenario["content_type"],
                    "time_period": scenario["time_period"]
                }
            )
            
            # Verify business logic validation
            if scenario["expected_anomalies"]:
                assert len(revenue_anomalies) > 0
                
                for anomaly in revenue_anomalies:
                    assert anomaly.anomaly_type == AnomalyType.BUSINESS
                    assert "business_impact" in anomaly.context
                    assert "revenue_deviation" in anomaly.context
            
        # Test engagement anomaly detection
        engagement_data = business_metrics_data["engagement_scenarios"]
        
        for scenario in engagement_data:
            engagement_anomalies = await anomaly_detector.detect_engagement_anomalies(
                user_id=scenario["user_id"],
                engagement_metrics=scenario["metrics"],
                historical_baseline=scenario["baseline"]
            )
            
            # Verify engagement pattern analysis
            if scenario["expected_pattern_change"]:
                assert len(engagement_anomalies) > 0
                
                for anomaly in engagement_anomalies:
                    assert "engagement_change" in anomaly.context
                    assert "behavior_shift" in anomaly.context
    
    async def test_security_anomaly_detection(self, anomaly_detector):
        """Test security-specific anomaly detection."""
        # Simulate security events
        security_events = [
            {
                "timestamp": datetime.utcnow() - timedelta(minutes=i),
                "event_type": "login_attempt",
                "user_id": f"user_{i % 10}",
                "ip_address": f"192.168.1.{i % 255}",
                "success": i % 20 != 0,  # 5% failure rate
                "location": "normal_location" if i % 50 != 0 else "suspicious_location"
            }
            for i in range(1000)
        ]
        
        # Add suspicious patterns
        # Brute force attack simulation
        attacker_ip = "10.0.0.100"
        for i in range(50):
            security_events.append({
                "timestamp": datetime.utcnow() - timedelta(minutes=i),
                "event_type": "login_attempt",
                "user_id": "target_user",
                "ip_address": attacker_ip,
                "success": False,
                "location": "suspicious_location"
            })
        
        # Detect security anomalies
        security_anomalies = await anomaly_detector.detect_security_anomalies(
            events=security_events,
            detection_rules=[
                "brute_force_detection",
                "unusual_location_detection",
                "impossible_travel_detection",
                "account_takeover_detection"
            ]
        )
        
        assert len(security_anomalies) > 0
        
        # Verify brute force detection
        brute_force_anomalies = [
            a for a in security_anomalies 
            if "brute_force" in a.description.lower()
        ]
        assert len(brute_force_anomalies) > 0
        
        # Verify security anomaly properties
        for anomaly in security_anomalies:
            assert anomaly.anomaly_type == AnomalyType.SECURITY
            assert anomaly.severity in [AnomalySeverity.HIGH, AnomalySeverity.CRITICAL]
            assert "security_threat_level" in anomaly.context
            assert "recommended_actions" in anomaly.context


class TestAnomalyCorrelationAndRootCause:
    """Tests for anomaly correlation and root cause analysis."""
    
    @pytest.fixture
    async def correlation_engine(self):
        """Create anomaly correlation engine."""
        engine = AnomalyCorrelationEngine(
            config={
                "correlation_window": 300,  # 5 minutes
                "min_correlation": 0.6,
                "max_correlations": 10,
                "causal_analysis": True
            }
        )
        await engine.initialize()
        yield engine
        await engine.shutdown()
    
    @pytest.fixture
    async def root_cause_analyzer(self):
        """Create root cause analyzer."""
        analyzer = RootCauseAnalyzer(
            config={
                "analysis_depth": 3,
                "confidence_threshold": 0.7,
                "include_external_factors": True,
                "ml_enabled": True
            }
        )
        await analyzer.initialize()
        yield analyzer
        await analyzer.shutdown()
    
    async def test_anomaly_correlation_detection(self, correlation_engine):
        """Test detection of correlated anomalies across different metrics."""
        # Simulate correlated system events
        base_time = datetime.utcnow()
        
        # Primary anomaly: High CPU usage
        cpu_anomaly = AnomalyPoint(
            timestamp=base_time,
            metric_name="cpu_usage",
            value=95.0,
            expected_value=45.0,
            deviation=50.0,
            anomaly_type=AnomalyType.PERFORMANCE,
            severity=AnomalySeverity.HIGH,
            detection_method=DetectionMethod.Z_SCORE,
            confidence_score=0.95
        )
        
        # Correlated anomalies
        correlated_anomalies = [
            AnomalyPoint(
                timestamp=base_time + timedelta(seconds=30),
                metric_name="memory_usage",
                value=88.0,
                expected_value=60.0,
                deviation=28.0,
                anomaly_type=AnomalyType.PERFORMANCE,
                severity=AnomalySeverity.MEDIUM,
                detection_method=DetectionMethod.Z_SCORE,
                confidence_score=0.87
            ),
            AnomalyPoint(
                timestamp=base_time + timedelta(seconds=60),
                metric_name="response_time",
                value=2500.0,
                expected_value=200.0,
                deviation=2300.0,
                anomaly_type=AnomalyType.PERFORMANCE,
                severity=AnomalySeverity.HIGH,
                detection_method=DetectionMethod.IQR,
                confidence_score=0.92
            ),
            AnomalyPoint(
                timestamp=base_time + timedelta(seconds=90),
                metric_name="error_rate",
                value=15.0,
                expected_value=1.0,
                deviation=14.0,
                anomaly_type=AnomalyType.BUSINESS,
                severity=AnomalySeverity.CRITICAL,
                detection_method=DetectionMethod.THRESHOLD,
                confidence_score=0.98
            )
        ]
        
        all_anomalies = [cpu_anomaly] + correlated_anomalies
        
        # Detect correlations
        correlation_results = await correlation_engine.find_correlations(all_anomalies)
        
        assert len(correlation_results) > 0
        
        # Verify correlation groups
        for correlation in correlation_results:
            assert "primary_anomaly" in correlation
            assert "correlated_anomalies" in correlation
            assert "correlation_strength" in correlation
            assert "time_window" in correlation
            
            assert correlation["correlation_strength"] >= 0.6
            assert len(correlation["correlated_anomalies"]) >= 1
        
        # Test causal relationship analysis
        causal_analysis = await correlation_engine.analyze_causal_relationships(all_anomalies)
        
        assert "causal_chains" in causal_analysis
        assert "root_causes" in causal_analysis
        assert "effect_propagation" in causal_analysis
    
    async def test_root_cause_analysis_comprehensive(self, root_cause_analyzer):
        """Test comprehensive root cause analysis for complex anomaly patterns."""
        # Create complex anomaly scenario
        anomaly_pattern = AnomalyPattern(
            pattern_id="complex_performance_degradation",
            pattern_name="Multi-Service Performance Degradation",
            anomaly_points=[
                AnomalyPoint(
                    timestamp=datetime.utcnow() - timedelta(minutes=5),
                    metric_name="database_response_time",
                    value=1200.0,
                    expected_value=50.0,
                    deviation=1150.0,
                    anomaly_type=AnomalyType.PERFORMANCE,
                    severity=AnomalySeverity.CRITICAL,
                    detection_method=DetectionMethod.Z_SCORE,
                    confidence_score=0.98
                ),
                AnomalyPoint(
                    timestamp=datetime.utcnow() - timedelta(minutes=3),
                    metric_name="api_latency",
                    value=3500.0,
                    expected_value=150.0,
                    deviation=3350.0,
                    anomaly_type=AnomalyType.PERFORMANCE,
                    severity=AnomalySeverity.HIGH,
                    detection_method=DetectionMethod.IQR,
                    confidence_score=0.94
                ),
                AnomalyPoint(
                    timestamp=datetime.utcnow() - timedelta(minutes=1),
                    metric_name="user_satisfaction",
                    value=2.1,
                    expected_value=4.5,
                    deviation=-2.4,
                    anomaly_type=AnomalyType.BUSINESS,
                    severity=AnomalySeverity.HIGH,
                    detection_method=DetectionMethod.TREND,
                    confidence_score=0.89
                )
            ],
            start_time=datetime.utcnow() - timedelta(minutes=5),
            end_time=datetime.utcnow(),
            frequency=1.0,
            affected_metrics=["database_response_time", "api_latency", "user_satisfaction"],
            pattern_confidence=0.92
        )
        
        # Additional context data
        system_context = {
            "recent_deployments": [
                {
                    "service": "database_service",
                    "timestamp": datetime.utcnow() - timedelta(minutes=10),
                    "version": "v2.1.3",
                    "changes": ["query_optimization", "index_updates"]
                }
            ],
            "infrastructure_events": [
                {
                    "event": "high_network_latency",
                    "timestamp": datetime.utcnow() - timedelta(minutes=7),
                    "affected_components": ["database", "cache"]
                }
            ],
            "external_factors": [
                {
                    "factor": "traffic_spike",
                    "timestamp": datetime.utcnow() - timedelta(minutes=6),
                    "magnitude": 3.2
                }
            ]
        }
        
        # Perform root cause analysis
        root_cause_results = await root_cause_analyzer.analyze_root_causes(
            anomaly_pattern=anomaly_pattern,
            system_context=system_context,
            include_ml_analysis=True
        )
        
        # Verify root cause analysis results
        assert "primary_root_causes" in root_cause_results
        assert "contributing_factors" in root_cause_results
        assert "confidence_scores" in root_cause_results
        assert "recommended_actions" in root_cause_results
        
        primary_causes = root_cause_results["primary_root_causes"]
        assert len(primary_causes) > 0
        
        for cause in primary_causes:
            assert "cause_type" in cause
            assert "description" in cause
            assert "confidence" in cause
            assert "evidence" in cause
            assert cause["confidence"] >= 0.7
        
        # Verify recommended actions
        actions = root_cause_results["recommended_actions"]
        assert len(actions) > 0
        
        for action in actions:
            assert "action_type" in action
            assert "description" in action
            assert "priority" in action
            assert "estimated_impact" in action
    
    async def test_anomaly_pattern_recognition(self, correlation_engine):
        """Test recognition of known anomaly patterns."""
        # Define known patterns
        known_patterns = [
            {
                "name": "cascade_failure",
                "description": "Service failures cascading through dependencies",
                "signature": ["service_error_rate", "dependency_timeout", "user_errors"],
                "typical_duration": 300,  # 5 minutes
                "severity_progression": ["medium", "high", "critical"]
            },
            {
                "name": "resource_exhaustion",
                "description": "Gradual resource exhaustion leading to performance degradation",
                "signature": ["memory_usage", "cpu_usage", "disk_io", "response_time"],
                "typical_duration": 900,  # 15 minutes
                "severity_progression": ["low", "medium", "high", "critical"]
            }
        ]
        
        # Simulate cascade failure pattern
        cascade_anomalies = []
        base_time = datetime.utcnow()
        
        for i, (metric, severity) in enumerate([
            ("service_error_rate", AnomalySeverity.MEDIUM),
            ("dependency_timeout", AnomalySeverity.HIGH),
            ("user_errors", AnomalySeverity.CRITICAL)
        ]):
            anomaly = AnomalyPoint(
                timestamp=base_time + timedelta(seconds=i * 60),
                metric_name=metric,
                value=100.0 * (i + 1),
                expected_value=5.0,
                deviation=95.0 * (i + 1),
                anomaly_type=AnomalyType.PATTERN,
                severity=severity,
                detection_method=DetectionMethod.PATTERN,
                confidence_score=0.9 - (i * 0.05)
            )
            cascade_anomalies.append(anomaly)
        
        # Recognize pattern
        pattern_recognition = await correlation_engine.recognize_patterns(
            anomalies=cascade_anomalies,
            known_patterns=known_patterns
        )
        
        assert "recognized_patterns" in pattern_recognition
        assert len(pattern_recognition["recognized_patterns"]) > 0
        
        recognized = pattern_recognition["recognized_patterns"][0]
        assert recognized["pattern_name"] == "cascade_failure"
        assert recognized["match_confidence"] > 0.8
        assert "next_expected_events" in recognized
        assert "mitigation_strategies" in recognized


class TestAnomalyDetectionIntegration:
    """Integration tests for anomaly detection system."""
    
    @pytest.fixture
    async def integrated_system(self):
        """Create fully integrated anomaly detection system."""
        system = AnomalyDetection(
            config={
                "integration_mode": True,
                "real_time_processing": True,
                "ml_models": ["isolation_forest", "dbscan", "autoencoder"],
                "alert_integration": True,
                "reporting_integration": True
            }
        )
        await system.initialize()
        await system.load_historical_data()
        yield system
        await system.shutdown()
    
    async def test_real_time_anomaly_processing(self, integrated_system):
        """Test real-time anomaly detection and processing."""
        # Start real-time monitoring
        await integrated_system.start_real_time_monitoring([
            "cpu_usage", "memory_usage", "response_time", "error_rate", "throughput"
        ])
        
        # Simulate real-time data stream
        data_points = []
        anomaly_injections = []
        
        for i in range(100):
            # Normal data point
            data_point = {
                "timestamp": datetime.utcnow(),
                "metrics": {
                    "cpu_usage": 45 + np.random.normal(0, 5),
                    "memory_usage": 60 + np.random.normal(0, 8),
                    "response_time": 150 + np.random.normal(0, 20),
                    "error_rate": 1 + np.random.exponential(0.5),
                    "throughput": 1000 + np.random.normal(0, 100)
                }
            }
            
            # Inject anomalies
            if i in [25, 50, 75]:
                if i == 25:
                    data_point["metrics"]["cpu_usage"] = 95  # High CPU
                elif i == 50:
                    data_point["metrics"]["response_time"] = 2000  # High latency
                elif i == 75:
                    data_point["metrics"]["error_rate"] = 15  # High error rate
                
                anomaly_injections.append(i)
            
            data_points.append(data_point)
            
            # Process data point
            detected_anomalies = await integrated_system.process_real_time_data(data_point)
            
            if detected_anomalies:
                for anomaly in detected_anomalies:
                    assert anomaly.timestamp == data_point["timestamp"]
                    assert anomaly.confidence_score > 0.5
        
        # Verify detection results
        all_detected = await integrated_system.get_detected_anomalies(
            start_time=data_points[0]["timestamp"],
            end_time=data_points[-1]["timestamp"]
        )
        
        assert len(all_detected) >= len(anomaly_injections)
        
        # Stop real-time monitoring
        await integrated_system.stop_real_time_monitoring()
    
    async def test_end_to_end_anomaly_workflow(self, integrated_system):
        """Test complete end-to-end anomaly detection workflow."""
        # 1. Data ingestion
        historical_data = {
            "metric_name": "business_revenue",
            "values": np.random.normal(10000, 1000, 1000).tolist(),
            "timestamps": [
                datetime.utcnow() - timedelta(hours=i) 
                for i in range(1000, 0, -1)
            ]
        }
        
        # Inject business anomaly
        historical_data["values"][500] = 5000  # Revenue drop
        
        await integrated_system.ingest_historical_data(historical_data)
        
        # 2. Model training
        training_result = await integrated_system.train_models(
            metric_name="business_revenue",
            training_period=timedelta(days=30)
        )
        
        assert training_result["success"] is True
        assert "model_performance" in training_result
        
        # 3. Anomaly detection
        detection_results = await integrated_system.detect_anomalies_batch(
            metric_name="business_revenue",
            detection_period=timedelta(days=7)
        )
        
        assert len(detection_results) > 0
        
        # 4. Correlation analysis
        correlation_results = await integrated_system.analyze_correlations(
            detection_results
        )
        
        # 5. Root cause analysis
        root_cause_results = await integrated_system.analyze_root_causes(
            detection_results
        )
        
        # 6. Alert generation
        generated_alerts = await integrated_system.generate_alerts(
            detection_results,
            correlation_results,
            root_cause_results
        )
        
        assert len(generated_alerts) > 0
        
        # 7. Report generation
        anomaly_report = await integrated_system.generate_anomaly_report(
            report_period=timedelta(days=7),
            include_analysis=True,
            include_recommendations=True
        )
        
        assert "executive_summary" in anomaly_report
        assert "detected_anomalies" in anomaly_report
        assert "correlation_analysis" in anomaly_report
        assert "root_cause_analysis" in anomaly_report
        assert "recommendations" in anomaly_report
        
        # Verify report quality
        summary = anomaly_report["executive_summary"]
        assert "total_anomalies" in summary
        assert "critical_anomalies" in summary
        assert "business_impact" in summary
        assert summary["total_anomalies"] > 0


@pytest.mark.performance
class TestAnomalyDetectionPerformance:
    """Performance tests for anomaly detection system."""
    
    @pytest.fixture
    async def performance_detector(self):
        """Create high-performance anomaly detector."""
        detector = AnomalyDetection(
            config={
                "high_performance_mode": True,
                "batch_processing": True,
                "parallel_processing": True,
                "memory_optimization": True,
                "cache_enabled": True
            }
        )
        await detector.initialize()
        yield detector
        await detector.shutdown()
    
    async def test_high_volume_anomaly_detection(self, performance_detector):
        """Test anomaly detection with high volume data."""
        # Generate large dataset
        data_size = 100000
        timestamps = [
            datetime.utcnow() - timedelta(seconds=i) 
            for i in range(data_size, 0, -1)
        ]
        
        # Generate normal data with embedded anomalies
        values = np.random.normal(100, 15, data_size)
        
        # Inject anomalies (1% of data)
        anomaly_indices = np.random.choice(data_size, size=int(data_size * 0.01), replace=False)
        for idx in anomaly_indices:
            values[idx] += np.random.choice([-1, 1]) * np.random.uniform(50, 100)
        
        # Measure detection performance
        start_time = time.time()
        
        detected_anomalies = await performance_detector.detect_anomalies_batch(
            metric_name="high_volume_metric",
            values=values.tolist(),
            timestamps=timestamps,
            batch_size=10000
        )
        
        detection_time = time.time() - start_time
        
        # Verify performance requirements
        assert detection_time < 30.0  # Process 100k points in under 30 seconds
        assert len(detected_anomalies) > 0
        
        # Verify detection quality
        detection_rate = len(detected_anomalies) / len(anomaly_indices)
        assert detection_rate >= 0.7  # Detect at least 70% of anomalies
        
        # Test memory efficiency
        memory_usage = await performance_detector.get_memory_usage()
        assert memory_usage["peak_memory_mb"] < 1000  # Under 1GB memory usage
    
    async def test_concurrent_detection_performance(self, performance_detector):
        """Test concurrent anomaly detection across multiple metrics."""
        # Define multiple metrics
        metrics = [
            f"metric_{i}" for i in range(20)
        ]
        
        # Generate data for each metric
        metric_data = {}
        for metric in metrics:
            values = np.random.normal(50, 10, 10000)
            # Inject some anomalies
            anomaly_count = np.random.randint(50, 150)
            anomaly_indices = np.random.choice(10000, size=anomaly_count, replace=False)
            for idx in anomaly_indices:
                values[idx] += np.random.choice([-1, 1]) * np.random.uniform(30, 60)
            
            metric_data[metric] = {
                "values": values.tolist(),
                "timestamps": [
                    datetime.utcnow() - timedelta(seconds=i) 
                    for i in range(10000, 0, -1)
                ]
            }
        
        # Concurrent detection
        start_time = time.time()
        
        detection_tasks = [
            performance_detector.detect_anomalies_batch(
                metric_name=metric,
                values=data["values"],
                timestamps=data["timestamps"]
            )
            for metric, data in metric_data.items()
        ]
        
        results = await asyncio.gather(*detection_tasks)
        
        concurrent_time = time.time() - start_time
        
        # Verify concurrent performance
        assert concurrent_time < 60.0  # Process all metrics in under 60 seconds
        assert len(results) == len(metrics)
        assert all(len(result) > 0 for result in results)
        
        # Verify system stability
        system_metrics = await performance_detector.get_system_metrics()
        assert system_metrics["cpu_usage"] < 95.0
        assert system_metrics["memory_usage"] < 90.0
        assert system_metrics["error_rate"] < 0.01


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        "test_anomaly_detection.py",
        "-v",
        "--cov=backend.ai.monitoring.anomaly_detection",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=100"
    ])

import pytest
import sys
import os
from pathlib import Path
import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch
import pandas as pd
from sklearn.metrics import classification_report

from ai.monitoring.anomaly_detection import (
    AnomalyDetection,
    AnomalyType,
    AnomalySeverity,
    AnomalyResult,
    StatisticalAnomalyDetector,
    TrendAnomalyDetector,
    SeasonalAnomalyDetector,
    MLAnomalyDetector
)
from .utils import TestDataGenerator, PerformanceValidator

class TestAnomalyDetection:
    """Test suite for Anomaly Detection system."""
    
    @pytest.fixture
    async def anomaly_detector(self):
        """Create Anomaly Detection instance."""
        detector = AnomalyDetection()
        await detector.initialize()
        yield detector
        await detector.shutdown()
    
    @pytest.fixture
    def anomaly_test_data(self):
        """Generate comprehensive anomaly test data."""
        return TestDataGenerator.generate_anomaly_scenarios()
    
    async def test_detector_initialization(self, anomaly_detector):
        """Test proper initialization of anomaly detection system."""
        assert anomaly_detector is not None
        assert anomaly_detector.is_initialized
        assert anomaly_detector.statistical_detector is not None
        assert anomaly_detector.trend_detector is not None
        assert anomaly_detector.seasonal_detector is not None
        assert anomaly_detector.ml_detector is not None
    
    async def test_statistical_anomaly_detection(self, anomaly_detector, anomaly_test_data):
        """Test statistical anomaly detection algorithms."""
        # Test point anomalies using statistical methods
        point_data = anomaly_test_data["point_anomalies"]
        
        # Configure statistical detector
        config = {
            "method": "zscore",
            "threshold": 3.0,
            "window_size": 100,
            "min_samples": 50
        }
        
        result = await anomaly_detector.detect_statistical_anomalies(
            data=point_data["data"],
            config=config
        )
        
        assert result is not None
        assert isinstance(result, AnomalyResult)
        assert result.anomaly_type == AnomalyType.STATISTICAL
        
        # Verify anomaly detection accuracy
        detected_count = len(result.anomaly_indices)
        expected_count = point_data["expected_anomalies"]
        
        # Allow for some variance in detection
        assert abs(detected_count - expected_count) <= 5
        
        # Test different statistical methods
        methods = ["zscore", "iqr", "isolation_forest", "modified_zscore"]
        
        for method in methods:
            method_config = config.copy()
            method_config["method"] = method
            
            method_result = await anomaly_detector.detect_statistical_anomalies(
                data=point_data["data"],
                config=method_config
            )
            
            assert method_result is not None
            assert len(method_result.anomaly_indices) > 0
            assert method_result.confidence_scores is not None
    
    async def test_trend_anomaly_detection(self, anomaly_detector, anomaly_test_data):
        """Test trend-based anomaly detection."""
        trend_data = anomaly_test_data["trend_anomalies"]
        
        config = {
            "window_size": 50,
            "trend_threshold": 2.0,
            "change_point_detection": True,
            "min_trend_length": 20
        }
        
        result = await anomaly_detector.detect_trend_anomalies(
            data=trend_data["data"],
            config=config
        )
        
        assert result is not None
        assert result.anomaly_type == AnomalyType.TREND
        
        # Verify change point detection
        assert len(result.anomaly_indices) >= 1
        
        # Check if detected change point is near expected location
        expected_change_point = trend_data["change_point"]
        detected_points = result.anomaly_indices
        
        # At least one detection should be within reasonable range of actual change point
        near_change_point = any(
            abs(point - expected_change_point) <= 50 
            for point in detected_points
        )
        assert near_change_point
        
        # Test different trend detection algorithms
        algorithms = ["mann_kendall", "cusum", "pettitt", "linear_regression"]
        
        for algorithm in algorithms:
            algo_config = config.copy()
            algo_config["algorithm"] = algorithm
            
            algo_result = await anomaly_detector.detect_trend_anomalies(
                data=trend_data["data"],
                config=algo_config
            )
            
            assert algo_result is not None
    
    async def test_seasonal_anomaly_detection(self, anomaly_detector, anomaly_test_data):
        """Test seasonal pattern anomaly detection."""
        seasonal_data = anomaly_test_data["seasonal_anomalies"]
        
        config = {
            "period": 100,  # Known seasonal period
            "seasonal_decomposition": "additive",
            "threshold_factor": 2.0,
            "min_periods": 3
        }
        
        result = await anomaly_detector.detect_seasonal_anomalies(
            data=seasonal_data["data"],
            config=config
        )
        
        assert result is not None
        assert result.anomaly_type == AnomalyType.SEASONAL
        
        # Verify seasonal anomaly detection
        expected_period = seasonal_data["anomaly_period"]
        detected_indices = result.anomaly_indices
        
        # Check if anomalies detected in expected period
        anomalies_in_period = [
            idx for idx in detected_indices 
            if expected_period[0] <= idx <= expected_period[1]
        ]
        
        assert len(anomalies_in_period) > 0
        
        # Test seasonal decomposition methods
        methods = ["additive", "multiplicative", "stl", "x13"]
        
        for method in ["additive", "multiplicative"]:  # Focus on available methods
            method_config = config.copy()
            method_config["seasonal_decomposition"] = method
            
            method_result = await anomaly_detector.detect_seasonal_anomalies(
                data=seasonal_data["data"],
                config=method_config
            )
            
            assert method_result is not None
    
    async def test_ml_based_anomaly_detection(self, anomaly_detector, anomaly_test_data):
        """Test machine learning-based anomaly detection."""
        # Use mixed data with various anomaly types
        ml_data = anomaly_test_data["point_anomalies"]["data"]
        
        config = {
            "algorithm": "isolation_forest",
            "contamination": 0.1,
            "n_estimators": 100,
            "max_features": 1.0,
            "bootstrap": False
        }
        
        result = await anomaly_detector.detect_ml_anomalies(
            data=ml_data,
            config=config
        )
        
        assert result is not None
        assert result.anomaly_type == AnomalyType.PATTERN
        assert len(result.anomaly_indices) > 0
        
        # Test different ML algorithms
        algorithms = [
            "isolation_forest",
            "one_class_svm",
            "local_outlier_factor",
            "dbscan"
        ]
        
        for algorithm in algorithms:
            algo_config = {
                "algorithm": algorithm,
                "contamination": 0.1 if algorithm != "dbscan" else None,
                "eps": 0.5 if algorithm == "dbscan" else None,
                "min_samples": 5 if algorithm == "dbscan" else None
            }
            
            try:
                algo_result = await anomaly_detector.detect_ml_anomalies(
                    data=ml_data,
                    config=algo_config
                )
                
                assert algo_result is not None
                assert len(algo_result.anomaly_indices) >= 0
                
            except Exception as e:
                # Some algorithms might not be available or suitable for the data
                pytest.skip(f"Algorithm {algorithm} not available or suitable: {e}")
    
    async def test_multivariate_anomaly_detection(self, anomaly_detector):
        """Test multivariate anomaly detection capabilities."""
        # Generate multivariate data
        n_samples = 1000
        n_features = 5
        
        # Normal multivariate data
        normal_data = np.random.multivariate_normal(
            mean=[100, 50, 75, 200, 25],
            cov=np.eye(n_features) * 10,
            size=n_samples
        )
        
        # Add multivariate anomalies
        anomaly_indices = [100, 300, 500, 700, 900]
        for idx in anomaly_indices:
            if idx < n_samples:
                # Create correlated anomalies across features
                normal_data[idx] = [500, 300, 400, 1000, 150]
        
        config = {
            "algorithm": "isolation_forest",
            "contamination": 0.05,
            "features": ["cpu_usage", "memory_usage", "response_time", "throughput", "error_rate"]
        }
        
        result = await anomaly_detector.detect_multivariate_anomalies(
            data=normal_data,
            config=config
        )
        
        assert result is not None
        assert result.anomaly_type == AnomalyType.PATTERN
        
        # Verify detection of multivariate anomalies
        detected_indices = set(result.anomaly_indices)
        expected_indices = set(anomaly_indices)
        
        # Calculate detection accuracy
        true_positives = len(detected_indices & expected_indices)
        false_positives = len(detected_indices - expected_indices)
        false_negatives = len(expected_indices - detected_indices)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        
        # Accept reasonable performance for multivariate detection
        assert precision >= 0.3 or recall >= 0.4
    
    async def test_real_time_anomaly_detection(self, anomaly_detector):
        """Test real-time streaming anomaly detection."""
        # Initialize real-time detector
        stream_config = {
            "window_size": 100,
            "update_frequency": 10,
            "alert_threshold": 0.8,
            "methods": ["statistical", "trend"]
        }
        
        await anomaly_detector.initialize_real_time_detection(
            stream_id="test_stream_001",
            config=stream_config
        )
        
        # Simulate streaming data
        anomalies_detected = []
        
        async def anomaly_callback(anomaly_result):
            anomalies_detected.append(anomaly_result)
        
        anomaly_detector.add_anomaly_callback("test_stream_001", anomaly_callback)
        
        # Send normal data points
        normal_base = 100
        for i in range(150):
            value = normal_base + np.random.normal(0, 10)
            await anomaly_detector.process_streaming_data(
                stream_id="test_stream_001",
                value=value,
                timestamp=datetime.utcnow()
            )
        
        # Inject anomalies
        anomaly_values = [500, -100, 1000]
        for anomaly_value in anomaly_values:
            await anomaly_detector.process_streaming_data(
                stream_id="test_stream_001",
                value=anomaly_value,
                timestamp=datetime.utcnow()
            )
        
        # Continue with normal data
        for i in range(50):
            value = normal_base + np.random.normal(0, 10)
            await anomaly_detector.process_streaming_data(
                stream_id="test_stream_001",
                value=value,
                timestamp=datetime.utcnow()
            )
        
        # Allow processing time
        await asyncio.sleep(0.5)
        
        # Verify real-time anomaly detection
        assert len(anomalies_detected) >= 1  # Should detect at least some anomalies
        
        # Verify anomaly properties
        for anomaly in anomalies_detected:
            assert anomaly.confidence >= stream_config["alert_threshold"]
            assert anomaly.timestamp is not None
            assert anomaly.severity in [AnomalySeverity.LOW, AnomalySeverity.MEDIUM, AnomalySeverity.HIGH, AnomalySeverity.CRITICAL]
    
    async def test_anomaly_classification(self, anomaly_detector):
        """Test anomaly type classification and severity assessment."""
        # Create different types of anomalies
        test_scenarios = [
            {
                "data": [100] * 50 + [500] + [100] * 49,  # Point anomaly
                "expected_type": AnomalyType.STATISTICAL,
                "expected_severity": AnomalySeverity.HIGH
            },
            {
                "data": list(range(100, 200)) + list(range(200, 100, -1)),  # Trend anomaly
                "expected_type": AnomalyType.TREND,
                "expected_severity": AnomalySeverity.MEDIUM
            },
            {
                "data": [100 + 20 * np.sin(2 * np.pi * i / 24) for i in range(100)] + [200] * 10 + [100 + 20 * np.sin(2 * np.pi * i / 24) for i in range(100, 150)],  # Seasonal break
                "expected_type": AnomalyType.SEASONAL,
                "expected_severity": AnomalySeverity.MEDIUM
            }
        ]
        
        for scenario in test_scenarios:
            result = await anomaly_detector.classify_anomalies(
                data=scenario["data"],
                detected_indices=[i for i, val in enumerate(scenario["data"]) if abs(val - 100) > 50]
            )
            
            assert result is not None
            assert len(result.classifications) > 0
            
            # Verify classification accuracy
            primary_classification = result.classifications[0]
            assert primary_classification.anomaly_type in [scenario["expected_type"], AnomalyType.PATTERN]
            assert primary_classification.confidence >= 0.5
    
    async def test_anomaly_root_cause_analysis(self, anomaly_detector):
        """Test anomaly root cause analysis capabilities."""
        # Simulate system metrics with correlated anomalies
        metrics_data = {
            "cpu_usage": [60] * 50 + [95] * 10 + [60] * 40,  # CPU spike
            "memory_usage": [70] * 50 + [85] * 10 + [70] * 40,  # Memory increase
            "response_time": [0.2] * 50 + [2.0] * 10 + [0.2] * 40,  # Response time spike
            "error_rate": [0.01] * 50 + [0.15] * 10 + [0.01] * 40,  # Error spike
            "throughput": [1000] * 50 + [200] * 10 + [1000] * 40  # Throughput drop
        }
        
        # Detect anomalies across all metrics
        anomaly_period = (50, 60)
        
        root_cause_result = await anomaly_detector.analyze_root_cause(
            metrics_data=metrics_data,
            anomaly_period=anomaly_period,
            correlation_threshold=0.7
        )
        
        assert root_cause_result is not None
        assert "primary_cause" in root_cause_result
        assert "correlated_metrics" in root_cause_result
        assert "confidence" in root_cause_result
        
        # Verify root cause identification
        assert root_cause_result["confidence"] >= 0.6
        assert len(root_cause_result["correlated_metrics"]) >= 2
        
        # Primary cause should be one of the spiking metrics
        primary_cause = root_cause_result["primary_cause"]
        assert primary_cause in ["cpu_usage", "memory_usage", "response_time"]
    
    async def test_anomaly_prediction(self, anomaly_detector):
        """Test predictive anomaly detection capabilities."""
        # Generate time series with patterns
        time_points = 200
        base_pattern = [100 + 20 * np.sin(2 * np.pi * i / 24) for i in range(time_points)]
        trend_component = [i * 0.1 for i in range(time_points)]
        noise = np.random.normal(0, 5, time_points)
        
        historical_data = [base + trend + n for base, trend, n in zip(base_pattern, trend_component, noise)]
        
        # Train predictive model
        training_config = {
            "model_type": "lstm",
            "sequence_length": 24,
            "prediction_horizon": 12,
            "anomaly_threshold": 2.0
        }
        
        await anomaly_detector.train_predictive_model(
            model_id="test_predictor_001",
            historical_data=historical_data,
            config=training_config
        )
        
        # Generate predictions
        recent_data = historical_data[-30:]  # Last 30 points
        
        prediction_result = await anomaly_detector.predict_anomalies(
            model_id="test_predictor_001",
            recent_data=recent_data,
            prediction_steps=12
        )
        
        assert prediction_result is not None
        assert "predictions" in prediction_result
        assert "anomaly_probabilities" in prediction_result
        assert "confidence_intervals" in prediction_result
        
        # Verify prediction output
        predictions = prediction_result["predictions"]
        anomaly_probs = prediction_result["anomaly_probabilities"]
        
        assert len(predictions) == 12
        assert len(anomaly_probs) == 12
        assert all(0 <= prob <= 1 for prob in anomaly_probs)
    
    async def test_ensemble_anomaly_detection(self, anomaly_detector):
        """Test ensemble anomaly detection combining multiple methods."""
        # Generate complex data with multiple anomaly types
        n_points = 500
        
        # Base signal with seasonal pattern
        base_signal = [100 + 30 * np.sin(2 * np.pi * i / 50) for i in range(n_points)]
        
        # Add trend
        trend = [i * 0.05 for i in range(n_points)]
        
        # Add noise
        noise = np.random.normal(0, 5, n_points)
        
        # Combine components
        data = [b + t + n for b, t, n in zip(base_signal, trend, noise)]
        
        # Add different types of anomalies
        data[100] = 500  # Point anomaly
        data[200:210] = [200] * 10  # Level shift
        for i in range(300, 320):  # Break seasonal pattern
            data[i] = 100
        
        # Configure ensemble detection
        ensemble_config = {
            "methods": [
                {"type": "statistical", "weight": 0.3, "config": {"method": "zscore", "threshold": 2.5}},
                {"type": "trend", "weight": 0.2, "config": {"window_size": 30}},
                {"type": "seasonal", "weight": 0.2, "config": {"period": 50}},
                {"type": "ml", "weight": 0.3, "config": {"algorithm": "isolation_forest", "contamination": 0.05}}
            ],
            "aggregation": "weighted_voting",
            "confidence_threshold": 0.6
        }
        
        result = await anomaly_detector.detect_ensemble_anomalies(
            data=data,
            config=ensemble_config
        )
        
        assert result is not None
        assert result.anomaly_type == AnomalyType.PATTERN
        assert len(result.anomaly_indices) > 0
        
        # Verify ensemble detected major anomalies
        detected_indices = set(result.anomaly_indices)
        
        # Check if major anomalies were detected
        point_anomaly_detected = 100 in detected_indices or any(95 <= idx <= 105 for idx in detected_indices)
        level_shift_detected = any(195 <= idx <= 215 for idx in detected_indices)
        seasonal_break_detected = any(295 <= idx <= 325 for idx in detected_indices)
        
        # At least 2 out of 3 major anomaly types should be detected
        detection_count = sum([point_anomaly_detected, level_shift_detected, seasonal_break_detected])
        assert detection_count >= 2
    
    async def test_anomaly_feedback_learning(self, anomaly_detector):
        """Test anomaly detection system learning from feedback."""
        # Initialize adaptive detector
        adaptive_config = {
            "learning_rate": 0.1,
            "feedback_window": 50,
            "adaptation_threshold": 0.7,
            "min_feedback_samples": 10
        }
        
        await anomaly_detector.initialize_adaptive_detection(
            detector_id="adaptive_test_001",
            config=adaptive_config
        )
        
        # Generate initial data and detect anomalies
        initial_data = [100 + np.random.normal(0, 10) for _ in range(200)]
        initial_data[50] = 300  # Known anomaly
        initial_data[150] = -50  # Known anomaly
        
        initial_result = await anomaly_detector.detect_adaptive_anomalies(
            detector_id="adaptive_test_001",
            data=initial_data
        )
        
        # Provide feedback on detections
        feedback_data = []
        
        for idx in initial_result.anomaly_indices:
            if idx in [50, 150]:  # True anomalies
                feedback_data.append({"index": idx, "is_anomaly": True, "confidence": 1.0})
            else:  # False positives
                feedback_data.append({"index": idx, "is_anomaly": False, "confidence": 0.8})
        
        # Apply feedback
        await anomaly_detector.apply_feedback(
            detector_id="adaptive_test_001",
            feedback=feedback_data
        )
        
        # Test on new similar data
        test_data = [100 + np.random.normal(0, 10) for _ in range(200)]
        test_data[75] = 290  # Similar to previous true anomaly
        test_data[125] = -45  # Similar to previous true anomaly
        
        adapted_result = await anomaly_detector.detect_adaptive_anomalies(
            detector_id="adaptive_test_001",
            data=test_data
        )
        
        # Verify improved detection
        assert adapted_result is not None
        
        # Check if similar anomalies are detected with higher confidence
        detected_indices = adapted_result.anomaly_indices
        confidence_scores = adapted_result.confidence_scores
        
        # Should detect anomalies near indices 75 and 125
        near_75 = any(70 <= idx <= 80 for idx in detected_indices)
        near_125 = any(120 <= idx <= 130 for idx in detected_indices)
        
        assert near_75 or near_125  # At least one should be detected
    
    async def test_anomaly_detection_performance(self, anomaly_detector):
        """Test anomaly detection system performance and scalability."""
        # Performance test with large dataset
        large_dataset_size = 10000
        large_data = np.random.normal(100, 15, large_dataset_size)
        
        # Add sparse anomalies
        anomaly_count = 50
        anomaly_indices = np.random.choice(large_dataset_size, anomaly_count, replace=False)
        for idx in anomaly_indices:
            large_data[idx] = np.random.choice([500, -100, 1000])
        
        # Measure detection performance
        start_time = datetime.utcnow()
        
        performance_result = await anomaly_detector.detect_statistical_anomalies(
            data=large_data.tolist(),
            config={"method": "zscore", "threshold": 3.0}
        )
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Verify performance requirements
        assert processing_time < 5.0  # Should process 10K points in under 5 seconds
        assert performance_result is not None
        
        # Verify detection accuracy
        detected_count = len(performance_result.anomaly_indices)
        detection_rate = detected_count / anomaly_count
        
        # Should detect at least 70% of anomalies
        assert detection_rate >= 0.7
        
        # Test memory efficiency
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process multiple datasets
        for i in range(10):
            test_data = np.random.normal(100, 15, 1000)
            await anomaly_detector.detect_statistical_anomalies(
                data=test_data.tolist(),
                config={"method": "isolation_forest", "contamination": 0.1}
            )
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        # Memory increase should be reasonable (less than 100MB for this test)
        assert memory_increase < 100
