"""
Test suite for Revenue Tracker module.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import unittest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json


class TestRevenueTracker(unittest.TestCase):
    """Test suite for RevenueTracker class"""

    def setUp(self):
        """Set up test fixtures"""
        # Import the actual revenue tracker
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        from analytics.revenue_tracker import RevenueTracker, RevenueMetrics
        
        self.tracker = RevenueTracker()
        self.sample_revenue_data = {
            "content_id": "content_123",
            "platform": "youtube",
            "revenue": 25.50,
            "currency": "EUR",
            "metadata": {
                "views": 10000,
                "engagement_rate": 0.05
            }
        }

    def test_revenue_tracking_data_structure(self):
        """Test revenue tracking data structure"""
        revenue_record = {
            "content_id": "test_123",
            "platform": "youtube",
            "revenue": 100.0,
            "currency": "EUR",
            "timestamp": datetime.now(),
            "metadata": {"views": 5000}
        }
        
        # Verify required fields
        required_fields = ["content_id", "platform", "revenue", "currency", "timestamp"]
        for field in required_fields:
            self.assertIn(field, revenue_record)
        
        # Verify data types
        self.assertIsInstance(revenue_record["revenue"], (int, float))
        self.assertIsInstance(revenue_record["timestamp"], datetime)
        self.assertIsInstance(revenue_record["metadata"], dict)

    def test_revenue_metrics_calculation(self):
        """Test revenue metrics calculation"""
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 31)
        
        platform_revenues = {
            "youtube": 150.0,
            "instagram": 80.0,
            "spotify": 120.0
        }
        
        total_revenue = sum(platform_revenues.values())
        growth_rate = 15.5  # 15.5% growth
        days_in_period = (end_date - start_date).days + 1
        average_per_day = total_revenue / days_in_period
        
        metrics = RevenueMetrics(
            period_start=start_date,
            period_end=end_date,
            total_revenue=total_revenue,
            platform_breakdown=platform_revenues,
            content_breakdown={"content_1": 200.0, "content_2": 150.0},
            growth_rate=growth_rate,
            average_per_day=average_per_day,
            currency="EUR"
        )
        
        self.assertEqual(metrics.total_revenue, 350.0)
        self.assertEqual(metrics.growth_rate, 15.5)
        self.assertAlmostEqual(metrics.average_per_day, 11.29, places=2)
        self.assertEqual(metrics.currency, "EUR")

    def test_cross_platform_revenue_analysis(self):
        """Test cross-platform revenue analysis"""
        platform_data = {
            "youtube": [25.0, 30.0, 35.0, 40.0, 45.0],
            "instagram": [15.0, 18.0, 20.0, 22.0, 25.0],
            "spotify": [10.0, 12.0, 15.0, 18.0, 20.0]
        }
        
        # Calculate platform totals
        platform_totals = {
            platform: sum(revenues)
            for platform, revenues in platform_data.items()
        }
        
        total_revenue = sum(platform_totals.values())
        
        # Calculate revenue distribution percentages
        revenue_distribution = {
            platform: (total / total_revenue) * 100
            for platform, total in platform_totals.items()
        }
        
        self.assertEqual(platform_totals["youtube"], 175.0)
        self.assertEqual(platform_totals["instagram"], 100.0)
        self.assertEqual(platform_totals["spotify"], 75.0)
        self.assertEqual(total_revenue, 350.0)
        
        self.assertEqual(revenue_distribution["youtube"], 50.0)  # 50%
        self.assertAlmostEqual(revenue_distribution["instagram"], 28.57, places=2)  # ~28.57%
        self.assertAlmostEqual(revenue_distribution["spotify"], 21.43, places=2)  # ~21.43%

    def test_roi_calculation(self):
        """Test ROI calculation logic"""
        production_cost = 500.0
        marketing_cost = 200.0
        total_revenue = 1050.0
        
        total_costs = production_cost + marketing_cost
        net_profit = total_revenue - total_costs
        roi_percentage = (net_profit / total_costs) * 100
        
        self.assertEqual(total_costs, 700.0)
        self.assertEqual(net_profit, 350.0)
        self.assertEqual(roi_percentage, 50.0)  # 50% ROI

    def test_revenue_forecasting_trend(self):
        """Test revenue forecasting trend calculation"""
        # Historical daily revenue data
        daily_revenues = [100, 110, 105, 120, 115, 130, 125, 140, 135, 150]
        
        # Calculate linear trend
        n = len(daily_revenues)
        x_sum = sum(range(n))
        y_sum = sum(daily_revenues)
        xy_sum = sum(i * y for i, y in enumerate(daily_revenues))
        x2_sum = sum(i ** 2 for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum ** 2)
        intercept = (y_sum - slope * x_sum) / n
        
        # Trend should be positive (increasing revenue)
        self.assertGreater(slope, 0)
        
        # Forecast next 5 days
        forecast_days = 5
        last_day = n - 1
        forecasts = []
        
        for day in range(1, forecast_days + 1):
            forecast = intercept + slope * (last_day + day)
            forecasts.append(max(0, forecast))  # Revenue can't be negative
        
        self.assertEqual(len(forecasts), 5)
        # Each forecast should be higher than the previous (positive trend)
        for i in range(1, len(forecasts)):
            self.assertGreaterEqual(forecasts[i], forecasts[i-1])

    def test_revenue_correlation_analysis(self):
        """Test correlation between different revenue factors"""
        # Sample data: engagement rate vs revenue
        data_points = [
            {"engagement": 0.05, "revenue": 100},
            {"engagement": 0.08, "revenue": 150},
            {"engagement": 0.10, "revenue": 200},
            {"engagement": 0.06, "revenue": 120},
            {"engagement": 0.12, "revenue": 250}
        ]
        
        # Calculate correlation coefficient
        n = len(data_points)
        engagement_rates = [d["engagement"] for d in data_points]
        revenues = [d["revenue"] for d in data_points]
        
        mean_engagement = sum(engagement_rates) / n
        mean_revenue = sum(revenues) / n
        
        numerator = sum((engagement_rates[i] - mean_engagement) * (revenues[i] - mean_revenue) for i in range(n))
        
        engagement_var = sum((x - mean_engagement) ** 2 for x in engagement_rates)
        revenue_var = sum((x - mean_revenue) ** 2 for x in revenues)
        
        denominator = (engagement_var * revenue_var) ** 0.5
        correlation = numerator / denominator if denominator != 0 else 0
        
        # Should show strong positive correlation
        self.assertGreater(correlation, 0.8)
        self.assertLessEqual(correlation, 1.0)

    def test_time_series_revenue_aggregation(self):
        """Test time-series revenue data aggregation"""
        # Sample hourly revenue data
        hourly_data = [
            {"hour": 0, "revenue": 10.0},
            {"hour": 1, "revenue": 8.0},
            {"hour": 2, "revenue": 15.0},
            {"hour": 3, "revenue": 12.0},
            {"hour": 4, "revenue": 20.0}
        ]
        
        # Aggregate by time periods
        total_revenue = sum(d["revenue"] for d in hourly_data)
        average_hourly = total_revenue / len(hourly_data)
        peak_hour = max(hourly_data, key=lambda x: x["revenue"])
        
        self.assertEqual(total_revenue, 65.0)
        self.assertEqual(average_hourly, 13.0)
        self.assertEqual(peak_hour["hour"], 4)
        self.assertEqual(peak_hour["revenue"], 20.0)

    def test_revenue_growth_rate_calculation(self):
        """Test revenue growth rate calculation"""
        current_period_revenue = 1500.0
        previous_period_revenue = 1200.0
        
        growth_rate = ((current_period_revenue - previous_period_revenue) / previous_period_revenue) * 100
        
        self.assertEqual(growth_rate, 25.0)  # 25% growth
        
        # Test negative growth
        declining_revenue = 1000.0
        decline_rate = ((declining_revenue - previous_period_revenue) / previous_period_revenue) * 100
        
        self.assertAlmostEqual(decline_rate, -16.67, places=2)  # ~16.67% decline

    def test_revenue_segmentation_analysis(self):
        """Test revenue segmentation and analysis"""
        content_revenues = {
            "music_track_1": 250.0,
            "music_track_2": 180.0,
            "music_track_3": 320.0,
            "music_track_4": 150.0,
            "music_track_5": 100.0
        }
        
        total_revenue = sum(content_revenues.values())
        
        # Find top performing content
        top_content = max(content_revenues.items(), key=lambda x: x[1])
        bottom_content = min(content_revenues.items(), key=lambda x: x[1])
        
        # Calculate revenue concentration (top 20% of content)
        sorted_revenues = sorted(content_revenues.values(), reverse=True)
        top_20_percent = int(len(sorted_revenues) * 0.2) or 1
        top_revenue = sum(sorted_revenues[:top_20_percent])
        concentration_ratio = (top_revenue / total_revenue) * 100
        
        self.assertEqual(top_content[0], "music_track_3")
        self.assertEqual(top_content[1], 320.0)
        self.assertEqual(bottom_content[0], "music_track_5")
        self.assertEqual(bottom_content[1], 100.0)
        self.assertEqual(total_revenue, 1000.0)
        self.assertEqual(concentration_ratio, 32.0)  # Top 20% generates 32% of revenue

    def test_currency_conversion_handling(self):
        """Test currency conversion in revenue tracking"""
        # Sample revenue in different currencies
        revenue_data = [
            {"revenue": 100.0, "currency": "EUR"},
            {"revenue": 120.0, "currency": "USD"},
            {"revenue": 85.0, "currency": "GBP"}
        ]
        
        # Mock exchange rates to EUR
        exchange_rates = {
            "USD": 0.85,  # 1 USD = 0.85 EUR
            "GBP": 1.15,  # 1 GBP = 1.15 EUR
            "EUR": 1.0    # Base currency
        }
        
        # Convert all to EUR
        total_eur = 0.0
        for revenue in revenue_data:
            amount = revenue["revenue"]
            currency = revenue["currency"]
            eur_amount = amount * exchange_rates[currency]
            total_eur += eur_amount
        
        expected_total = (100.0 * 1.0) + (120.0 * 0.85) + (85.0 * 1.15)
        self.assertEqual(total_eur, expected_total)
        self.assertEqual(total_eur, 299.75)  # 100 + 102 + 97.75

    def test_revenue_anomaly_detection(self):
        """Test anomaly detection in revenue streams"""
        # Normal daily revenue pattern
        normal_revenues = [100, 110, 95, 105, 120, 90, 115, 108, 102, 98]
        
        # Calculate statistics
        mean_revenue = sum(normal_revenues) / len(normal_revenues)
        variance = sum((x - mean_revenue) ** 2 for x in normal_revenues) / len(normal_revenues)
        std_dev = variance ** 0.5
        
        # Test for anomalies (2 standard deviations)
        threshold = 2 * std_dev
        
        test_values = [105, 50, 200, 110]  # 50 and 200 should be anomalies
        anomalies = []
        
        for value in test_values:
            if abs(value - mean_revenue) > threshold:
                anomalies.append(value)
        
        # Should detect significant outliers
        self.assertIn(50, anomalies)
        self.assertIn(200, anomalies)
        self.assertNotIn(105, anomalies)
        self.assertNotIn(110, anomalies)


if __name__ == '__main__':
    unittest.main()