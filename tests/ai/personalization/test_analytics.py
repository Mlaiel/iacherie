# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Analytics and Metrics Tests

Comprehensive tests for analytics, metrics computation, and performance monitoring.
Tests recommendation metrics, user engagement analytics, and system performance.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest import IsolatedAsyncioTestCase
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import time
import os
import sys
from collections import defaultdict

# Import the analytics modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from ai.personalization.analytics import (
    PersonalizationAnalytics,
    UserJourneyAnalyzer,
    EngagementPredictor,
    PersonalizationMetrics,
    ABTestingEngine,
    PersonalizationReporter,
    MetricType,
    AnalyticsPeriod,
    PersonalizationMetric,
    UserJourneyEvent,
    EngagementPrediction
)


class TestAnalyticsEngine(IsolatedAsyncioTestCase):
    """Comprehensive tests for AnalyticsEngine"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.engine = AnalyticsEngine(
            metrics_window=timedelta(days=30),
            sampling_rate=0.1,
            real_time_processing=True
        )
        self.analytics_data = self._generate_analytics_data()

    def _generate_analytics_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate comprehensive analytics data"""
        now = datetime.utcnow()
        
        # User interactions
        interactions = []
        for i in range(1000):
            interactions.append({
                'user_id': f'user_{i % 100}',
                'item_id': f'track_{i % 200}',
                'action': np.random.choice(['play', 'skip', 'like', 'share']),
                'timestamp': now - timedelta(days=np.random.randint(0, 30)),
                'duration': np.random.randint(30, 300),
                'session_id': f'session_{i // 10}',
                'context': {
                    'device': np.random.choice(['mobile', 'desktop', 'smart_speaker']),
                    'location': np.random.choice(['home', 'work', 'commute']),
                    'time_of_day': np.random.randint(0, 24)
                }
            })
        
        # Recommendations
        recommendations = []
        for i in range(500):
            recommendations.append({
                'recommendation_id': f'rec_{i}',
                'user_id': f'user_{i % 100}',
                'items': [f'track_{j}' for j in range(i % 10, (i % 10) + 10)],
                'algorithm': np.random.choice(['collaborative', 'content_based', 'hybrid']),
                'timestamp': now - timedelta(days=np.random.randint(0, 30)),
                'response': {
                    'clicks': np.random.randint(0, 10),
                    'plays': np.random.randint(0, 8),
                    'likes': np.random.randint(0, 3),
                    'skips': np.random.randint(0, 5)
                }
            })
        
        # System metrics
        system_metrics = []
        for i in range(720):  # 30 days * 24 hours
            system_metrics.append({
                'timestamp': now - timedelta(hours=i),
                'response_time': np.random.normal(200, 50),  # milliseconds
                'memory_usage': np.random.normal(70, 10),    # percentage
                'cpu_usage': np.random.normal(45, 15),       # percentage
                'active_users': np.random.randint(500, 2000),
                'requests_per_second': np.random.randint(100, 500)
            })
        
        return {
            'interactions': interactions,
            'recommendations': recommendations,
            'system_metrics': system_metrics
        }

    async def test_engine_initialization(self):
        """Test analytics engine initialization"""
        self.assertIsNotNone(self.engine.metrics_window)
        self.assertEqual(self.engine.sampling_rate, 0.1)
        self.assertTrue(self.engine.real_time_processing)

    async def test_data_ingestion(self):
        """Test data ingestion into analytics engine"""
        # Ingest interaction data
        await self.engine.ingest_interactions(self.analytics_data['interactions'])
        
        # Ingest recommendation data
        await self.engine.ingest_recommendations(self.analytics_data['recommendations'])
        
        # Ingest system metrics
        await self.engine.ingest_system_metrics(self.analytics_data['system_metrics'])
        
        # Verify data ingestion
        stats = await self.engine.get_ingestion_stats()
        
        self.assertGreater(stats['interactions_count'], 0)
        self.assertGreater(stats['recommendations_count'], 0)
        self.assertGreater(stats['system_metrics_count'], 0)

    async def test_real_time_analytics(self):
        """Test real-time analytics processing"""
        await self.engine.ingest_interactions(self.analytics_data['interactions'])
        
        # Process real-time metrics
        real_time_metrics = await self.engine.compute_real_time_metrics()
        
        self.assertIsInstance(real_time_metrics, dict)
        self.assertIn('active_users_last_hour', real_time_metrics)
        self.assertIn('interactions_per_minute', real_time_metrics)
        self.assertIn('average_session_length', real_time_metrics)

    async def test_batch_analytics(self):
        """Test batch analytics processing"""
        await self.engine.ingest_interactions(self.analytics_data['interactions'])
        await self.engine.ingest_recommendations(self.analytics_data['recommendations'])
        
        # Process batch analytics
        batch_results = await self.engine.compute_batch_analytics(
            start_date=datetime.utcnow() - timedelta(days=7),
            end_date=datetime.utcnow()
        )
        
        self.assertIsInstance(batch_results, dict)
        self.assertIn('user_engagement', batch_results)
        self.assertIn('recommendation_performance', batch_results)
        self.assertIn('content_popularity', batch_results)


class TestMetricsCalculator(IsolatedAsyncioTestCase):
    """Comprehensive tests for MetricsCalculator"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.calculator = MetricsCalculator()
        self.metrics_data = self._generate_metrics_data()

    def _generate_metrics_data(self) -> Dict[str, Any]:
        """Generate data for metrics calculation"""
        # Recommendation performance data
        actual_interactions = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1]  # Binary relevance
        predicted_scores = [0.9, 0.3, 0.8, 0.7, 0.2, 0.85, 0.1, 0.4, 0.75, 0.65]
        
        # User engagement data
        user_sessions = []
        for i in range(100):
            session = {
                'user_id': f'user_{i % 50}',
                'session_length': np.random.randint(10, 120),  # minutes
                'tracks_played': np.random.randint(5, 50),
                'skip_rate': np.random.uniform(0.1, 0.4),
                'like_rate': np.random.uniform(0.05, 0.2),
                'return_probability': np.random.uniform(0.6, 0.95)
            }
            user_sessions.append(session)
        
        return {
            'actual_interactions': actual_interactions,
            'predicted_scores': predicted_scores,
            'user_sessions': user_sessions
        }

    async def test_recommendation_metrics(self):
        """Test recommendation quality metrics"""
        metrics = await self.calculator.calculate_recommendation_metrics(
            actual=self.metrics_data['actual_interactions'],
            predicted=self.metrics_data['predicted_scores'],
            k=5
        )
        
        self.assertIsInstance(metrics, RecommendationMetrics)
        self.assertIn('precision_at_k', metrics.__dict__)
        self.assertIn('recall_at_k', metrics.__dict__)
        self.assertIn('ndcg_at_k', metrics.__dict__)
        self.assertIn('map_score', metrics.__dict__)
        
        # Verify metric ranges
        self.assertGreaterEqual(metrics.precision_at_k, 0.0)
        self.assertLessEqual(metrics.precision_at_k, 1.0)
        self.assertGreaterEqual(metrics.recall_at_k, 0.0)
        self.assertLessEqual(metrics.recall_at_k, 1.0)

    async def test_engagement_metrics(self):
        """Test user engagement metrics"""
        metrics = await self.calculator.calculate_engagement_metrics(
            self.metrics_data['user_sessions']
        )
        
        self.assertIsInstance(metrics, EngagementMetrics)
        self.assertIn('average_session_length', metrics.__dict__)
        self.assertIn('user_retention_rate', metrics.__dict__)
        self.assertIn('content_consumption_rate', metrics.__dict__)
        
        # Verify reasonable values
        self.assertGreater(metrics.average_session_length, 0)
        self.assertGreaterEqual(metrics.user_retention_rate, 0.0)
        self.assertLessEqual(metrics.user_retention_rate, 1.0)

    async def test_diversity_metrics(self):
        """Test recommendation diversity metrics"""
        recommendations = [
            ['track_1', 'track_2', 'track_3'],  # User 1 recommendations
            ['track_2', 'track_4', 'track_5'],  # User 2 recommendations
            ['track_1', 'track_3', 'track_6']   # User 3 recommendations
        ]
        
        # Mock item features for diversity calculation
        item_features = {
            'track_1': {'genre': 'pop', 'energy': 0.8},
            'track_2': {'genre': 'rock', 'energy': 0.9},
            'track_3': {'genre': 'pop', 'energy': 0.6},
            'track_4': {'genre': 'electronic', 'energy': 0.7},
            'track_5': {'genre': 'jazz', 'energy': 0.4},
            'track_6': {'genre': 'classical', 'energy': 0.3}
        }
        
        diversity_metrics = await self.calculator.calculate_diversity_metrics(
            recommendations, item_features
        )
        
        self.assertIsInstance(diversity_metrics, dict)
        self.assertIn('intra_list_diversity', diversity_metrics)
        self.assertIn('inter_list_diversity', diversity_metrics)
        self.assertIn('catalog_coverage', diversity_metrics)

    async def test_novelty_metrics(self):
        """Test recommendation novelty metrics"""
        user_history = {
            'user_1': ['track_1', 'track_2'],
            'user_2': ['track_3', 'track_4'],
            'user_3': ['track_5']
        }
        
        recommendations = {
            'user_1': ['track_6', 'track_7', 'track_8'],
            'user_2': ['track_9', 'track_10', 'track_3'],  # track_3 is not novel
            'user_3': ['track_11', 'track_12', 'track_13']
        }
        
        novelty_score = await self.calculator.calculate_novelty_metrics(
            recommendations, user_history
        )
        
        self.assertIsInstance(novelty_score, float)
        self.assertGreaterEqual(novelty_score, 0.0)
        self.assertLessEqual(novelty_score, 1.0)

    async def test_serendipity_metrics(self):
        """Test recommendation serendipity metrics"""
        user_profiles = {
            'user_1': {'preferred_genres': ['pop', 'rock'], 'energy_preference': 0.8},
            'user_2': {'preferred_genres': ['jazz'], 'energy_preference': 0.4}
        }
        
        recommendations = {
            'user_1': ['classical_track_1', 'pop_track_1'],  # Classical is unexpected
            'user_2': ['electronic_track_1', 'jazz_track_1']  # Electronic is unexpected
        }
        
        item_features = {
            'classical_track_1': {'genre': 'classical', 'energy': 0.3},
            'pop_track_1': {'genre': 'pop', 'energy': 0.8},
            'electronic_track_1': {'genre': 'electronic', 'energy': 0.9},
            'jazz_track_1': {'genre': 'jazz', 'energy': 0.4}
        }
        
        serendipity_score = await self.calculator.calculate_serendipity_metrics(
            recommendations, user_profiles, item_features
        )
        
        self.assertIsInstance(serendipity_score, float)
        self.assertGreaterEqual(serendipity_score, 0.0)
        self.assertLessEqual(serendipity_score, 1.0)

    async def test_business_metrics(self):
        """Test business KPI metrics"""
        business_data = {
            'user_acquisition': {'new_users': 1500, 'period_days': 30},
            'user_retention': {'returning_users': 8500, 'total_users': 10000},
            'revenue': {'subscription_revenue': 45000, 'ad_revenue': 12000},
            'engagement': {'daily_active_users': 5000, 'monthly_active_users': 15000}
        }
        
        business_metrics = await self.calculator.calculate_business_metrics(business_data)
        
        self.assertIsInstance(business_metrics, dict)
        self.assertIn('user_acquisition_rate', business_metrics)
        self.assertIn('user_retention_rate', business_metrics)
        self.assertIn('revenue_per_user', business_metrics)
        self.assertIn('dau_mau_ratio', business_metrics)


class TestPerformanceMonitor(IsolatedAsyncioTestCase):
    """Comprehensive tests for PerformanceMonitor"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.monitor = PerformanceMonitor(
            monitoring_interval=timedelta(minutes=5),
            alert_thresholds={
                'response_time': 1000,  # ms
                'memory_usage': 80,     # %
                'error_rate': 0.05      # 5%
            }
        )
        self.performance_data = self._generate_performance_data()

    def _generate_performance_data(self) -> List[Dict[str, Any]]:
        """Generate performance monitoring data"""
        data = []
        now = datetime.utcnow()
        
        for i in range(288):  # 24 hours * 12 (5-minute intervals)
            timestamp = now - timedelta(minutes=i * 5)
            
            # Simulate performance degradation during peak hours
            hour = timestamp.hour
            is_peak_hour = 18 <= hour <= 22
            
            base_response_time = 250 if not is_peak_hour else 400
            base_memory = 60 if not is_peak_hour else 75
            
            data.append({
                'timestamp': timestamp,
                'response_time': max(50, np.random.normal(base_response_time, 100)),
                'memory_usage': np.clip(np.random.normal(base_memory, 10), 30, 95),
                'cpu_usage': np.clip(np.random.normal(45, 15), 10, 90),
                'active_users': np.random.randint(1000, 5000),
                'requests_per_second': np.random.randint(50, 300),
                'error_count': np.random.poisson(2),
                'cache_hit_rate': np.random.uniform(0.8, 0.95)
            })
        
        return data

    async def test_performance_monitoring(self):
        """Test performance monitoring functionality"""
        await self.monitor.ingest_performance_data(self.performance_data)
        
        # Get current performance status
        status = await self.monitor.get_performance_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('overall_health', status)
        self.assertIn('response_time_avg', status)
        self.assertIn('memory_usage_avg', status)
        self.assertIn('alerts', status)

    async def test_alert_generation(self):
        """Test alert generation for performance issues"""
        # Create data with performance issues
        problematic_data = []
        for i in range(10):
            problematic_data.append({
                'timestamp': datetime.utcnow() - timedelta(minutes=i),
                'response_time': 1500,  # Above threshold
                'memory_usage': 85,     # Above threshold
                'cpu_usage': 95,
                'error_count': 50,      # High error count
                'requests_per_second': 100
            })
        
        await self.monitor.ingest_performance_data(problematic_data)
        
        alerts = await self.monitor.check_alerts()
        
        self.assertIsInstance(alerts, list)
        self.assertGreater(len(alerts), 0)
        
        for alert in alerts:
            self.assertIn('type', alert)
            self.assertIn('severity', alert)
            self.assertIn('message', alert)
            self.assertIn('timestamp', alert)

    async def test_performance_trends(self):
        """Test performance trend analysis"""
        await self.monitor.ingest_performance_data(self.performance_data)
        
        trends = await self.monitor.analyze_performance_trends(
            metric='response_time',
            time_window=timedelta(hours=24)
        )
        
        self.assertIsInstance(trends, dict)
        self.assertIn('trend_direction', trends)
        self.assertIn('trend_strength', trends)
        self.assertIn('predicted_values', trends)

    async def test_capacity_planning(self):
        """Test capacity planning recommendations"""
        await self.monitor.ingest_performance_data(self.performance_data)
        
        capacity_report = await self.monitor.generate_capacity_report()
        
        self.assertIsInstance(capacity_report, dict)
        self.assertIn('current_utilization', capacity_report)
        self.assertIn('projected_growth', capacity_report)
        self.assertIn('scaling_recommendations', capacity_report)

    async def test_anomaly_detection(self):
        """Test performance anomaly detection"""
        # Add anomalous data points
        anomalous_data = self.performance_data.copy()
        
        # Insert clear anomalies
        for i in range(5):
            anomalous_data.append({
                'timestamp': datetime.utcnow() - timedelta(minutes=i),
                'response_time': 5000,  # Very high
                'memory_usage': 95,     # Very high
                'cpu_usage': 98,
                'requests_per_second': 10,  # Very low
                'error_count': 100
            })
        
        await self.monitor.ingest_performance_data(anomalous_data)
        
        anomalies = await self.monitor.detect_anomalies()
        
        self.assertIsInstance(anomalies, list)
        self.assertGreater(len(anomalies), 0)
        
        for anomaly in anomalies:
            self.assertIn('metric', anomaly)
            self.assertIn('anomaly_score', anomaly)
            self.assertIn('timestamp', anomaly)


class TestABTestAnalyzer(IsolatedAsyncioTestCase):
    """Comprehensive tests for ABTestAnalyzer"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.analyzer = ABTestAnalyzer(
            confidence_level=0.95,
            minimum_sample_size=100,
            statistical_tests=['t_test', 'mann_whitney', 'chi_square']
        )
        self.ab_test_data = self._generate_ab_test_data()

    def _generate_ab_test_data(self) -> Dict[str, Any]:
        """Generate A/B test data"""
        # Test: New recommendation algorithm vs. baseline
        control_group = []
        treatment_group = []
        
        # Control group (baseline algorithm)
        for i in range(500):
            user_data = {
                'user_id': f'control_user_{i}',
                'group': 'control',
                'click_through_rate': np.random.normal(0.12, 0.03),
                'session_length': np.random.normal(25, 8),  # minutes
                'tracks_played': np.random.poisson(15),
                'user_satisfaction': np.random.normal(3.2, 0.8),  # 1-5 scale
                'conversion': np.random.binomial(1, 0.08)  # 8% conversion rate
            }
            control_group.append(user_data)
        
        # Treatment group (new algorithm - slightly better performance)
        for i in range(500):
            user_data = {
                'user_id': f'treatment_user_{i}',
                'group': 'treatment',
                'click_through_rate': np.random.normal(0.15, 0.03),  # 25% improvement
                'session_length': np.random.normal(28, 8),          # 12% improvement
                'tracks_played': np.random.poisson(17),             # 13% improvement
                'user_satisfaction': np.random.normal(3.5, 0.8),   # 9% improvement
                'conversion': np.random.binomial(1, 0.10)           # 25% improvement
            }
            treatment_group.append(user_data)
        
        return {
            'control_group': control_group,
            'treatment_group': treatment_group,
            'test_metadata': {
                'test_name': 'new_recommendation_algorithm',
                'start_date': datetime.utcnow() - timedelta(days=14),
                'end_date': datetime.utcnow(),
                'hypothesis': 'New algorithm improves user engagement',
                'primary_metric': 'click_through_rate',
                'secondary_metrics': ['session_length', 'user_satisfaction']
            }
        }

    async def test_ab_test_analysis(self):
        """Test A/B test statistical analysis"""
        result = await self.analyzer.analyze_ab_test(
            control_data=self.ab_test_data['control_group'],
            treatment_data=self.ab_test_data['treatment_group'],
            metrics=['click_through_rate', 'session_length', 'user_satisfaction']
        )
        
        self.assertIsInstance(result, ABTestResult)
        self.assertIn('statistical_significance', result.__dict__)
        self.assertIn('effect_size', result.__dict__)
        self.assertIn('confidence_intervals', result.__dict__)
        self.assertIn('p_values', result.__dict__)

    async def test_power_analysis(self):
        """Test statistical power analysis"""
        power_analysis = await self.analyzer.calculate_statistical_power(
            effect_size=0.1,
            sample_size=500,
            alpha=0.05
        )
        
        self.assertIsInstance(power_analysis, dict)
        self.assertIn('statistical_power', power_analysis)
        self.assertIn('minimum_detectable_effect', power_analysis)
        self.assertIn('recommended_sample_size', power_analysis)

    async def test_sample_size_calculation(self):
        """Test sample size calculation for A/B tests"""
        sample_size = await self.analyzer.calculate_required_sample_size(
            expected_effect_size=0.15,
            statistical_power=0.8,
            significance_level=0.05
        )
        
        self.assertIsInstance(sample_size, int)
        self.assertGreater(sample_size, 0)

    async def test_multiple_testing_correction(self):
        """Test multiple testing correction"""
        # Test multiple metrics simultaneously
        metrics = ['click_through_rate', 'session_length', 'tracks_played', 'user_satisfaction']
        
        corrected_results = await self.analyzer.apply_multiple_testing_correction(
            control_data=self.ab_test_data['control_group'],
            treatment_data=self.ab_test_data['treatment_group'],
            metrics=metrics,
            correction_method='bonferroni'
        )
        
        self.assertIsInstance(corrected_results, dict)
        self.assertIn('corrected_p_values', corrected_results)
        self.assertIn('significant_metrics', corrected_results)

    async def test_bayesian_analysis(self):
        """Test Bayesian A/B test analysis"""
        bayesian_result = await self.analyzer.bayesian_analysis(
            control_data=self.ab_test_data['control_group'],
            treatment_data=self.ab_test_data['treatment_group'],
            metric='click_through_rate',
            prior_params={'alpha': 1, 'beta': 1}
        )
        
        self.assertIsInstance(bayesian_result, dict)
        self.assertIn('probability_treatment_better', bayesian_result)
        self.assertIn('credible_interval', bayesian_result)
        self.assertIn('expected_loss', bayesian_result)

    async def test_segmentation_analysis(self):
        """Test A/B test results by user segments"""
        # Add segment information to test data
        for user in self.ab_test_data['control_group']:
            user['segment'] = np.random.choice(['new_users', 'power_users', 'casual_users'])
        
        for user in self.ab_test_data['treatment_group']:
            user['segment'] = np.random.choice(['new_users', 'power_users', 'casual_users'])
        
        segmented_results = await self.analyzer.analyze_by_segments(
            control_data=self.ab_test_data['control_group'],
            treatment_data=self.ab_test_data['treatment_group'],
            segment_column='segment',
            metric='click_through_rate'
        )
        
        self.assertIsInstance(segmented_results, dict)
        for segment in ['new_users', 'power_users', 'casual_users']:
            self.assertIn(segment, segmented_results)


class TestReportGenerator(IsolatedAsyncioTestCase):
    """Comprehensive tests for ReportGenerator"""

    async def asyncSetUp(self):
        """Set up test environment"""
        self.generator = ReportGenerator(
            report_formats=['json', 'html', 'pdf'],
            template_path='templates/',
            auto_export=True
        )

    async def test_engagement_report_generation(self):
        """Test user engagement report generation"""
        engagement_data = {
            'daily_active_users': [5000, 5200, 4800, 5100],
            'average_session_length': [25.5, 26.2, 24.8, 25.9],
            'user_retention_rates': {'day_1': 0.75, 'day_7': 0.45, 'day_30': 0.25},
            'content_consumption': {'total_plays': 150000, 'unique_tracks': 25000}
        }
        
        report = await self.generator.generate_engagement_report(
            data=engagement_data,
            period='weekly',
            format='json'
        )
        
        self.assertIsInstance(report, dict)
        self.assertIn('summary', report)
        self.assertIn('key_metrics', report)
        self.assertIn('trends', report)
        self.assertIn('recommendations', report)

    async def test_recommendation_performance_report(self):
        """Test recommendation performance report"""
        recommendation_data = {
            'algorithms': {
                'collaborative_filtering': {'precision': 0.25, 'recall': 0.18, 'ndcg': 0.32},
                'content_based': {'precision': 0.22, 'recall': 0.16, 'ndcg': 0.28},
                'hybrid': {'precision': 0.28, 'recall': 0.21, 'ndcg': 0.35}
            },
            'diversity_metrics': {'intra_list': 0.45, 'catalog_coverage': 0.68},
            'novelty_score': 0.72,
            'user_feedback': {'thumbs_up': 8500, 'thumbs_down': 1200}
        }
        
        report = await self.generator.generate_recommendation_report(
            data=recommendation_data,
            format='json'
        )
        
        self.assertIsInstance(report, dict)
        self.assertIn('algorithm_comparison', report)
        self.assertIn('diversity_analysis', report)
        self.assertIn('user_satisfaction', report)

    async def test_system_performance_report(self):
        """Test system performance report"""
        performance_data = {
            'response_times': [245, 250, 280, 265, 275],
            'memory_usage': [68, 72, 75, 70, 73],
            'error_rates': [0.02, 0.015, 0.018, 0.021, 0.019],
            'throughput': [250, 280, 275, 290, 285],
            'alerts_count': 5,
            'uptime_percentage': 99.8
        }
        
        report = await self.generator.generate_performance_report(
            data=performance_data,
            period='daily',
            format='json'
        )
        
        self.assertIsInstance(report, dict)
        self.assertIn('performance_summary', report)
        self.assertIn('sla_compliance', report)
        self.assertIn('capacity_utilization', report)

    async def test_business_intelligence_report(self):
        """Test business intelligence report"""
        business_data = {
            'revenue': {'monthly': 125000, 'growth_rate': 0.12},
            'user_metrics': {'new_users': 2500, 'churn_rate': 0.08},
            'content_metrics': {'new_content': 1500, 'popular_genres': ['Pop', 'Electronic']},
            'operational_costs': {'infrastructure': 15000, 'content_licensing': 45000}
        }
        
        report = await self.generator.generate_business_report(
            data=business_data,
            format='json'
        )
        
        self.assertIsInstance(report, dict)
        self.assertIn('financial_summary', report)
        self.assertIn('growth_metrics', report)
        self.assertIn('roi_analysis', report)

    async def test_automated_insights(self):
        """Test automated insights generation"""
        analytics_data = {
            'user_behavior': {
                'peak_usage_hours': [19, 20, 21],
                'popular_devices': ['mobile', 'desktop'],
                'session_patterns': 'evening_listening'
            },
            'content_trends': {
                'trending_genres': ['Lo-Fi', 'Indie'],
                'emerging_artists': ['Artist_A', 'Artist_B'],
                'seasonal_patterns': 'winter_chill'
            },
            'performance_insights': {
                'bottlenecks': ['recommendation_engine'],
                'optimization_opportunities': ['caching', 'preprocessing']
            }
        }
        
        insights = await self.generator.generate_automated_insights(analytics_data)
        
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
        
        for insight in insights:
            self.assertIn('category', insight)
            self.assertIn('description', insight)
            self.assertIn('impact', insight)
            self.assertIn('recommendation', insight)

    async def test_custom_dashboard_generation(self):
        """Test custom dashboard generation"""
        dashboard_config = {
            'widgets': [
                {'type': 'metric', 'title': 'Active Users', 'value': 15000},
                {'type': 'chart', 'title': 'Usage Trends', 'data': [100, 120, 115, 130]},
                {'type': 'table', 'title': 'Top Content', 'data': [['Track 1', 1000], ['Track 2', 850]]}
            ],
            'layout': 'grid',
            'refresh_interval': 300  # 5 minutes
        }
        
        dashboard = await self.generator.generate_custom_dashboard(
            config=dashboard_config,
            format='html'
        )
        
        self.assertIsInstance(dashboard, str)
        self.assertIn('Active Users', dashboard)
        self.assertIn('Usage Trends', dashboard)


class TestAnalyticsPerformanceAndScalability(IsolatedAsyncioTestCase):
    """Performance and scalability tests for analytics operations"""

    async def test_large_dataset_processing(self):
        """Test analytics processing on large datasets"""
        calculator = MetricsCalculator()
        
        # Generate large dataset
        n_interactions = 100000
        large_dataset = []
        
        for i in range(n_interactions):
            large_dataset.append({
                'user_id': f'user_{i % 10000}',
                'item_id': f'track_{i % 50000}',
                'action': np.random.choice(['play', 'skip', 'like']),
                'timestamp': datetime.utcnow() - timedelta(seconds=i),
                'duration': np.random.randint(30, 300)
            })
        
        # Measure processing time
        start_time = time.time()
        
        # Calculate engagement metrics on large dataset
        engagement_metrics = await calculator.calculate_engagement_metrics(large_dataset)
        
        processing_time = time.time() - start_time
        
        # Should process within reasonable time
        self.assertLess(processing_time, 30.0)  # 30 seconds max
        self.assertIsNotNone(engagement_metrics)

    async def test_real_time_analytics_throughput(self):
        """Test real-time analytics throughput"""
        engine = AnalyticsEngine(real_time_processing=True)
        
        # Simulate high-throughput data ingestion
        batch_size = 1000
        n_batches = 10
        
        start_time = time.time()
        
        for batch in range(n_batches):
            interactions = []
            for i in range(batch_size):
                interactions.append({
                    'user_id': f'user_{i}',
                    'item_id': f'track_{i % 100}',
                    'action': 'play',
                    'timestamp': datetime.utcnow()
                })
            
            await engine.ingest_interactions(interactions)
        
        total_time = time.time() - start_time
        throughput = (n_batches * batch_size) / total_time
        
        # Should handle at least 1000 events per second
        self.assertGreater(throughput, 1000)

    async def test_concurrent_analytics_operations(self):
        """Test concurrent analytics operations"""
        engine = AnalyticsEngine()
        
        async def analytics_task(task_id: int):
            # Simulate different analytics operations
            if task_id % 3 == 0:
                await engine.compute_real_time_metrics()
            elif task_id % 3 == 1:
                await engine.compute_batch_analytics(
                    start_date=datetime.utcnow() - timedelta(hours=1),
                    end_date=datetime.utcnow()
                )
            else:
                await engine.get_ingestion_stats()
        
        # Run concurrent analytics tasks
        tasks = [analytics_task(i) for i in range(20)]
        start_time = time.time()
        
        await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Should complete all tasks within reasonable time
        self.assertLess(total_time, 10.0)


# Test runner configuration
if __name__ == '__main__':
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--asyncio-mode=auto',
        '--maxfail=10'
    ])
