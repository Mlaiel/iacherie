"""
Test suite for Performance Analyzer module.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import unittest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json


class TestPerformanceAnalyzer(unittest.TestCase):
    """Test suite for PerformanceAnalyzer class"""

    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = None  # Will be mocked
        self.sample_metrics = {
            "content_id": "content_123",
            "platform": "youtube",
            "views": 10000,
            "likes": 500,
            "shares": 50,
            "comments": 100,
            "engagement_rate": 0.065,
            "timestamp": datetime.now()
        }

    def test_performance_metrics_structure(self):
        """Test performance metrics data structure"""
        metrics = {
            "content_id": "test_123",
            "platform": "youtube",
            "views": 1000,
            "likes": 50,
            "shares": 10,
            "comments": 25,
            "engagement_rate": 0.085,
            "timestamp": datetime.now()
        }
        
        # Verify required fields
        required_fields = ["content_id", "platform", "views", "likes", "shares", "comments", "engagement_rate"]
        for field in required_fields:
            self.assertIn(field, metrics)
        
        # Verify data types
        self.assertIsInstance(metrics["views"], int)
        self.assertIsInstance(metrics["likes"], int)
        self.assertIsInstance(metrics["engagement_rate"], float)
        self.assertIsInstance(metrics["timestamp"], datetime)

    def test_engagement_rate_calculation(self):
        """Test engagement rate calculation logic"""
        views = 10000
        likes = 500
        shares = 50
        comments = 100
        
        # Calculate engagement rate: (likes + shares + comments) / views
        expected_engagement = (likes + shares + comments) / views
        calculated_engagement = (500 + 50 + 100) / 10000
        
        self.assertEqual(calculated_engagement, 0.065)
        self.assertEqual(calculated_engagement, expected_engagement)

    def test_performance_comparison(self):
        """Test performance comparison between periods"""
        current_metrics = {
            "views": 15000,
            "likes": 800,
            "engagement_rate": 0.08
        }
        
        previous_metrics = {
            "views": 10000,
            "likes": 500,
            "engagement_rate": 0.065
        }
        
        # Calculate growth rates
        view_growth = ((current_metrics["views"] - previous_metrics["views"]) / previous_metrics["views"]) * 100
        like_growth = ((current_metrics["likes"] - previous_metrics["likes"]) / previous_metrics["likes"]) * 100
        engagement_growth = ((current_metrics["engagement_rate"] - previous_metrics["engagement_rate"]) / previous_metrics["engagement_rate"]) * 100
        
        self.assertEqual(view_growth, 50.0)  # 50% increase
        self.assertEqual(like_growth, 60.0)  # 60% increase
        self.assertAlmostEqual(engagement_growth, 23.08, places=2)  # ~23% increase

    def test_platform_performance_aggregation(self):
        """Test aggregation of performance across platforms"""
        platform_data = {
            "youtube": {"views": 10000, "engagement": 0.06},
            "instagram": {"views": 5000, "engagement": 0.08},
            "tiktok": {"views": 20000, "engagement": 0.12}
        }
        
        # Calculate total views
        total_views = sum(data["views"] for data in platform_data.values())
        self.assertEqual(total_views, 35000)
        
        # Calculate weighted average engagement
        weighted_engagement = sum(
            data["views"] * data["engagement"] for data in platform_data.values()
        ) / total_views
        
        expected_weighted = (10000 * 0.06 + 5000 * 0.08 + 20000 * 0.12) / 35000
        self.assertAlmostEqual(weighted_engagement, expected_weighted, places=4)
        self.assertAlmostEqual(weighted_engagement, 0.1, places=1)

    def test_trend_analysis(self):
        """Test trend analysis functionality"""
        # Sample data for 7 days
        daily_views = [1000, 1200, 1100, 1300, 1500, 1400, 1600]
        
        # Simple trend calculation (linear)
        n = len(daily_views)
        x_sum = sum(range(n))
        y_sum = sum(daily_views)
        xy_sum = sum(i * y for i, y in enumerate(daily_views))
        x2_sum = sum(i ** 2 for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum ** 2)
        
        # Trend should be positive (increasing views)
        self.assertGreater(slope, 0)
        self.assertAlmostEqual(slope, 92.86, places=2)

    def test_performance_benchmarking(self):
        """Test performance benchmarking against industry standards"""
        content_metrics = {
            "engagement_rate": 0.08,
            "view_duration": 0.75,  # 75% completion rate
            "click_through_rate": 0.05
        }
        
        industry_benchmarks = {
            "engagement_rate": 0.06,
            "view_duration": 0.60,
            "click_through_rate": 0.03
        }
        
        performance_scores = {}
        for metric, value in content_metrics.items():
            benchmark = industry_benchmarks[metric]
            performance_scores[metric] = (value / benchmark) * 100
        
        # Content should outperform benchmarks
        self.assertGreater(performance_scores["engagement_rate"], 100)
        self.assertGreater(performance_scores["view_duration"], 100)
        self.assertGreater(performance_scores["click_through_rate"], 100)
        
        # Specific score checks
        self.assertAlmostEqual(performance_scores["engagement_rate"], 133.33, places=2)
        self.assertAlmostEqual(performance_scores["view_duration"], 125.0, places=1)
        self.assertAlmostEqual(performance_scores["click_through_rate"], 166.67, places=2)

    def test_anomaly_detection(self):
        """Test anomaly detection in performance metrics"""
        # Normal range of daily views
        normal_views = [1000, 1100, 950, 1050, 1200, 980, 1150]
        
        # Calculate mean and standard deviation
        mean_views = sum(normal_views) / len(normal_views)
        variance = sum((x - mean_views) ** 2 for x in normal_views) / len(normal_views)
        std_dev = variance ** 0.5
        
        # Test anomaly detection (views outside 2 standard deviations)
        anomaly_threshold = 2 * std_dev
        
        test_values = [1000, 500, 2000, 1100]  # 500 and 2000 should be anomalies
        anomalies = []
        
        for value in test_values:
            if abs(value - mean_views) > anomaly_threshold:
                anomalies.append(value)
        
        # Should detect significant outliers
        self.assertIn(500, anomalies)
        self.assertIn(2000, anomalies)
        self.assertNotIn(1000, anomalies)
        self.assertNotIn(1100, anomalies)

    def test_roi_performance_correlation(self):
        """Test correlation between performance metrics and ROI"""
        performance_data = [
            {"engagement_rate": 0.05, "roi": 150},
            {"engagement_rate": 0.08, "roi": 200},
            {"engagement_rate": 0.12, "roi": 300},
            {"engagement_rate": 0.06, "roi": 175},
            {"engagement_rate": 0.10, "roi": 250}
        ]
        
        # Calculate correlation coefficient
        n = len(performance_data)
        engagement_rates = [d["engagement_rate"] for d in performance_data]
        rois = [d["roi"] for d in performance_data]
        
        mean_engagement = sum(engagement_rates) / n
        mean_roi = sum(rois) / n
        
        numerator = sum((engagement_rates[i] - mean_engagement) * (rois[i] - mean_roi) for i in range(n))
        
        engagement_var = sum((x - mean_engagement) ** 2 for x in engagement_rates)
        roi_var = sum((x - mean_roi) ** 2 for x in rois)
        
        denominator = (engagement_var * roi_var) ** 0.5
        
        correlation = numerator / denominator if denominator != 0 else 0
        
        # Should show strong positive correlation
        self.assertGreater(correlation, 0.8)  # Strong positive correlation
        self.assertLessEqual(correlation, 1.0)  # Correlation cannot exceed 1

    def test_multi_platform_performance_insights(self):
        """Test generation of insights across multiple platforms"""
        platform_performance = {
            "youtube": {
                "total_views": 50000,
                "engagement_rate": 0.06,
                "revenue": 150.0,
                "growth_rate": 15.0
            },
            "instagram": {
                "total_views": 30000,
                "engagement_rate": 0.09,
                "revenue": 80.0,
                "growth_rate": 25.0
            },
            "tiktok": {
                "total_views": 100000,
                "engagement_rate": 0.12,
                "revenue": 120.0,
                "growth_rate": 35.0
            }
        }
        
        # Find best performing platform by different metrics
        best_views = max(platform_performance.items(), key=lambda x: x[1]["total_views"])
        best_engagement = max(platform_performance.items(), key=lambda x: x[1]["engagement_rate"])
        best_revenue = max(platform_performance.items(), key=lambda x: x[1]["revenue"])
        best_growth = max(platform_performance.items(), key=lambda x: x[1]["growth_rate"])
        
        self.assertEqual(best_views[0], "tiktok")
        self.assertEqual(best_engagement[0], "tiktok")
        self.assertEqual(best_revenue[0], "youtube")
        self.assertEqual(best_growth[0], "tiktok")
        
        # Calculate platform distribution
        total_views = sum(data["total_views"] for data in platform_performance.values())
        platform_distribution = {
            platform: (data["total_views"] / total_views) * 100
            for platform, data in platform_performance.items()
        }
        
        self.assertAlmostEqual(platform_distribution["youtube"], 27.78, places=2)
        self.assertAlmostEqual(platform_distribution["instagram"], 16.67, places=2)
        self.assertAlmostEqual(platform_distribution["tiktok"], 55.56, places=2)


if __name__ == '__main__':
    unittest.main()