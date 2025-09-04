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

"""Performance Tracker Tests

Comprehensive tests for performance tracking system that monitors
content performance, engagement metrics, and optimization insights.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import the module to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend"))

from ai.content_generation.performance_tracker import (
    PerformanceTracker, 
    MetricsCollector
)
from ai.content_generation.content_models import Platform, ContentType


class TestPerformanceTracker:
    """Test suite for PerformanceTracker"""
    
    @pytest.fixture
    def performance_tracker(self):
        """Create a performance tracker instance"""
        return PerformanceTracker()
    
    @pytest.fixture
    def sample_content_data(self):
        """Create sample content performance data"""
        return {
            "content_id": "content_12345",
            "title": "10 AI Tools Every Content Creator Should Know",
            "platform": Platform.LINKEDIN,
            "content_type": ContentType.ARTICLE,
            "published_date": "2025-01-31T10:00:00Z",
            "author": "Fahed Mlaiel",
            "tags": ["AI", "Content Creation", "Tools", "Productivity"],
            "metrics": {
                "views": 15420,
                "likes": 892,
                "shares": 156,
                "comments": 78,
                "clicks": 1245,
                "saves": 234,
                "engagement_rate": 5.67,
                "reach": 28450,
                "impressions": 45230
            },
            "demographics": {
                "age_groups": {
                    "25-34": 0.35,
                    "35-44": 0.28,
                    "45-54": 0.22,
                    "18-24": 0.15
                },
                "locations": {
                    "United States": 0.45,
                    "United Kingdom": 0.15,
                    "Canada": 0.12,
                    "Australia": 0.08,
                    "Germany": 0.10,
                    "Other": 0.10
                },
                "industries": {
                    "Marketing": 0.32,
                    "Technology": 0.25,
                    "Consulting": 0.18,
                    "Education": 0.15,
                    "Other": 0.10
                }
            }
        }
    
    @pytest.fixture
    def campaign_data(self):
        """Create sample campaign performance data"""
        return {
            "campaign_id": "campaign_67890",
            "campaign_name": "AI Content Course Launch",
            "start_date": "2025-01-15T00:00:00Z",
            "end_date": "2025-02-15T23:59:59Z",
            "budget": 25000,
            "spent": 18750,
            "platforms": [Platform.FACEBOOK, Platform.LINKEDIN, Platform.INSTAGRAM],
            "content_pieces": 45,
            "overall_metrics": {
                "total_reach": 234500,
                "total_impressions": 567800,
                "total_clicks": 8920,
                "total_conversions": 445,
                "cost_per_click": 2.10,
                "cost_per_conversion": 42.13,
                "conversion_rate": 4.99,
                "return_on_ad_spend": 4.25
            }
        }
    
    def test_performance_tracker_initialization(self, performance_tracker):
        """Test performance tracker initialization"""
        assert performance_tracker is not None
        assert hasattr(performance_tracker, 'metrics_data')
        assert hasattr(performance_tracker, 'performance_history')
        assert hasattr(performance_tracker, 'platform_benchmarks')
        assert hasattr(performance_tracker, 'performance_thresholds')
        
        # Check default data structures exist
        assert isinstance(performance_tracker.metrics_data, dict)
    
    @pytest.mark.asyncio
    async def test_track_content_performance(self, performance_tracker, sample_content_data):
        """Test content performance tracking"""
        with patch.object(performance_tracker, '_collect_metrics') as mock_collect:
            mock_collect.return_value = {
                "success": True,
                "metrics_collected": {
                    "engagement_metrics": {
                        "likes": 892,
                        "shares": 156,
                        "comments": 78,
                        "saves": 234,
                        "total_engagement": 1360,
                        "engagement_rate": 5.67,
                        "engagement_velocity": 2.3
                    },
                    "reach_metrics": {
                        "organic_reach": 21340,
                        "paid_reach": 7110,
                        "total_reach": 28450,
                        "reach_rate": 62.9,
                        "frequency": 1.59
                    },
                    "conversion_metrics": {
                        "clicks": 1245,
                        "click_through_rate": 2.75,
                        "conversions": 67,
                        "conversion_rate": 5.38,
                        "cost_per_conversion": 15.25
                    },
                    "quality_metrics": {
                        "relevance_score": 8.9,
                        "quality_score": 9.2,
                        "authenticity_score": 9.5,
                        "sentiment_score": 0.78
                    }
                },
                "benchmark_comparison": {
                    "industry_average": {
                        "engagement_rate": 3.2,
                        "click_through_rate": 1.8,
                        "conversion_rate": 3.1
                    },
                    "performance_vs_average": {
                        "engagement_rate": "+77.2%",
                        "click_through_rate": "+52.8%",
                        "conversion_rate": "+73.5%"
                    }
                },
                "optimization_insights": [
                    "Content performing 77% above industry average",
                    "High save rate indicates valuable content",
                    "Strong conversion rate suggests effective CTA",
                    "Consider amplifying with paid promotion"
                ]
            }
            
            result = await performance_tracker.track_content_performance(
                content_data=sample_content_data,
                real_time=True,
                include_benchmarks=True
            )
            
            assert result["success"] is True
            assert result["metrics_collected"]["engagement_metrics"]["engagement_rate"] > 5.0
            assert "+77.2%" in result["benchmark_comparison"]["performance_vs_average"]["engagement_rate"]
            assert len(result["optimization_insights"]) >= 4
    
    @pytest.mark.asyncio
    async def test_real_time_monitoring(self, performance_tracker, sample_content_data):
        """Test real-time performance monitoring"""
        with patch.object(performance_tracker, '_monitor_real_time') as mock_monitor:
            mock_monitor.return_value = {
                "success": True,
                "monitoring_session": {
                    "session_id": "monitor_001",
                    "content_id": "content_12345",
                    "start_time": "2025-01-31T10:00:00Z",
                    "duration_minutes": 120,
                    "update_frequency": 30,  # seconds
                    "status": "active"
                },
                "real_time_metrics": {
                    "current_views": 15420,
                    "views_per_minute": 128.5,
                    "engagement_velocity": 2.3,
                    "viral_coefficient": 1.15,
                    "trending_score": 8.7,
                    "momentum_indicator": "rising"
                },
                "performance_alerts": [
                    {
                        "alert_id": "alert_001",
                        "type": "engagement_spike",
                        "severity": AlertSeverity.MEDIUM,
                        "message": "Engagement rate increased 150% in last 30 minutes",
                        "triggered_at": "2025-01-31T11:30:00Z",
                        "action_required": "Consider boosting with paid promotion"
                    },
                    {
                        "alert_id": "alert_002",
                        "type": "viral_potential",
                        "severity": AlertSeverity.HIGH,
                        "message": "Content showing viral potential - viral coefficient 1.15",
                        "triggered_at": "2025-01-31T11:45:00Z",
                        "action_required": "Immediate amplification recommended"
                    }
                ],
                "predictions": {
                    "24_hour_reach": 45000,
                    "final_engagement": 2500,
                    "peak_performance_time": "2025-01-31T14:30:00Z",
                    "virality_probability": 0.73
                }
            }
            
            result = await performance_tracker.start_real_time_monitoring(
                content_id=sample_content_data["content_id"],
                duration_hours=2,
                alert_thresholds={"engagement_spike": 1.5, "viral_coefficient": 1.1}
            )
            
            assert result["success"] is True
            assert result["real_time_metrics"]["viral_coefficient"] > 1.1
            assert len(result["performance_alerts"]) == 2
            assert result["predictions"]["virality_probability"] > 0.7
    
    @pytest.mark.asyncio
    async def test_campaign_analytics(self, performance_tracker, campaign_data):
        """Test campaign performance analytics"""
        with patch.object(performance_tracker, '_analyze_campaign') as mock_analyze:
            mock_analyze.return_value = {
                "success": True,
                "campaign_analysis": {
                    "overview": {
                        "campaign_name": "AI Content Course Launch",
                        "duration_days": 31,
                        "budget_utilization": 0.75,
                        "total_content_pieces": 45,
                        "average_performance_score": 8.7
                    },
                    "performance_by_platform": {
                        "facebook": {
                            "reach": 145000,
                            "engagement_rate": 4.2,
                            "cost_per_click": 1.85,
                            "conversion_rate": 5.8,
                            "roi": 4.5
                        },
                        "linkedin": {
                            "reach": 56000,
                            "engagement_rate": 6.7,
                            "cost_per_click": 3.20,
                            "conversion_rate": 8.2,
                            "roi": 5.1
                        },
                        "instagram": {
                            "reach": 33500,
                            "engagement_rate": 7.9,
                            "cost_per_click": 2.10,
                            "conversion_rate": 3.4,
                            "roi": 3.8
                        }
                    },
                    "content_performance": {
                        "top_performing": [
                            {
                                "content_id": "content_12345",
                                "title": "10 AI Tools Every Content Creator Should Know",
                                "platform": "linkedin",
                                "engagement_score": 9.5,
                                "conversion_score": 8.8
                            },
                            {
                                "content_id": "content_12346",
                                "title": "AI Content Creation: Before vs After",
                                "platform": "facebook",
                                "engagement_score": 9.2,
                                "conversion_score": 9.1
                            }
                        ],
                        "underperforming": [
                            {
                                "content_id": "content_12347",
                                "title": "Technical AI Implementation Guide",
                                "platform": "instagram",
                                "engagement_score": 3.2,
                                "conversion_score": 2.8,
                                "issues": ["too_technical", "wrong_platform", "poor_visual"]
                            }
                        ]
                    },
                    "optimization_recommendations": [
                        "Increase LinkedIn budget allocation by 15%",
                        "Reduce technical content on Instagram",
                        "A/B test video content on Facebook",
                        "Expand successful content formats",
                        "Optimize posting times for better reach"
                    ]
                },
                "financial_analysis": {
                    "total_revenue": 189000,
                    "customer_acquisition_cost": 42.13,
                    "lifetime_value": 847,
                    "roi": 4.25,
                    "break_even_point": 8,
                    "profit_margin": 0.76
                }
            }
            
            result = await performance_tracker.analyze_campaign_performance(
                campaign_data=campaign_data,
                include_financial_analysis=True,
                detailed_breakdown=True
            )
            
            assert result["success"] is True
            assert result["campaign_analysis"]["overview"]["average_performance_score"] > 8.0
            assert result["financial_analysis"]["roi"] > 4.0
            assert len(result["campaign_analysis"]["optimization_recommendations"]) >= 5
    
    @pytest.mark.asyncio
    async def test_competitor_analysis(self, performance_tracker):
        """Test competitor performance analysis"""
        competitor_data = {
            "competitors": ["ai_content_pro", "content_ai_master", "smart_content_hub"],
            "analysis_period": "30_days",
            "metrics_to_compare": ["engagement_rate", "posting_frequency", "content_quality"]
        }
        
        with patch.object(performance_tracker, '_analyze_competitors') as mock_competitor:
            mock_competitor.return_value = {
                "success": True,
                "competitive_analysis": {
                    "market_position": {
                        "your_ranking": 2,
                        "total_competitors": 3,
                        "market_share": 0.35,
                        "growth_rate": 0.25
                    },
                    "competitor_metrics": {
                        "ai_content_pro": {
                            "engagement_rate": 4.8,
                            "posting_frequency": 12,
                            "content_quality_score": 8.1,
                            "follower_growth": 0.18,
                            "strengths": ["consistent_posting", "high_quality_visuals"],
                            "weaknesses": ["low_engagement", "limited_content_variety"]
                        },
                        "content_ai_master": {
                            "engagement_rate": 6.2,
                            "posting_frequency": 8,
                            "content_quality_score": 9.2,
                            "follower_growth": 0.32,
                            "strengths": ["thought_leadership", "expert_content"],
                            "weaknesses": ["low_posting_frequency", "limited_platforms"]
                        },
                        "smart_content_hub": {
                            "engagement_rate": 5.1,
                            "posting_frequency": 15,
                            "content_quality_score": 7.8,
                            "follower_growth": 0.22,
                            "strengths": ["high_volume", "multi_platform"],
                            "weaknesses": ["inconsistent_quality", "generic_content"]
                        }
                    },
                    "your_performance": {
                        "engagement_rate": 5.7,
                        "posting_frequency": 10,
                        "content_quality_score": 8.9,
                        "follower_growth": 0.28,
                        "competitive_advantages": [
                            "Above average engagement rate",
                            "High content quality score",
                            "Strong follower growth"
                        ]
                    },
                    "opportunities": [
                        "Increase posting frequency to match market leaders",
                        "Expand to additional platforms",
                        "Focus on thought leadership content",
                        "Improve visual content quality"
                    ],
                    "threats": [
                        "content_ai_master gaining market share rapidly",
                        "smart_content_hub's high volume strategy",
                        "Increasing competition in AI content space"
                    ]
                }
            }
            
            result = await performance_tracker.analyze_competitor_performance(
                competitor_data=competitor_data,
                include_swot_analysis=True
            )
            
            assert result["success"] is True
            assert result["competitive_analysis"]["market_position"]["your_ranking"] <= 3
            assert len(result["competitive_analysis"]["opportunities"]) >= 4
            assert len(result["competitive_analysis"]["threats"]) >= 3
    
    @pytest.mark.asyncio
    async def test_performance_alerts(self, performance_tracker):
        """Test performance alert system"""
        with patch.object(performance_tracker, '_check_alerts') as mock_alerts:
            mock_alerts.return_value = {
                "success": True,
                "active_alerts": [
                    {
                        "alert_id": "alert_performance_001",
                        "type": "engagement_drop",
                        "severity": AlertSeverity.HIGH,
                        "content_id": "content_12348",
                        "message": "Engagement rate dropped 65% compared to average",
                        "current_value": 1.2,
                        "expected_value": 3.4,
                        "triggered_at": "2025-01-31T09:15:00Z",
                        "recommendations": [
                            "Review content relevance",
                            "Check posting time optimization",
                            "Consider content format changes"
                        ]
                    },
                    {
                        "alert_id": "alert_performance_002",
                        "type": "budget_overspend",
                        "severity": AlertSeverity.MEDIUM,
                        "campaign_id": "campaign_67890",
                        "message": "Campaign spending 15% above daily budget",
                        "current_spend": 1150,
                        "budget_limit": 1000,
                        "triggered_at": "2025-01-31T10:30:00Z",
                        "recommendations": [
                            "Reduce bid amounts",
                            "Pause underperforming ads",
                            "Adjust targeting parameters"
                        ]
                    },
                    {
                        "alert_id": "alert_performance_003",
                        "type": "viral_opportunity",
                        "severity": AlertSeverity.LOW,
                        "content_id": "content_12349",
                        "message": "Content showing high virality potential",
                        "viral_score": 8.5,
                        "growth_rate": 2.3,
                        "triggered_at": "2025-01-31T11:00:00Z",
                        "recommendations": [
                            "Boost with paid promotion",
                            "Cross-promote on other platforms",
                            "Engage with early commenters"
                        ]
                    }
                ],
                "alert_summary": {
                    "total_alerts": 3,
                    "high_severity": 1,
                    "medium_severity": 1,
                    "low_severity": 1,
                    "new_alerts_today": 2
                }
            }
            
            result = await performance_tracker.check_performance_alerts(
                time_range="24_hours",
                severity_filter=None
            )
            
            assert result["success"] is True
            assert result["alert_summary"]["total_alerts"] == 3
            assert len(result["active_alerts"]) == 3
            assert any(alert["type"] == "viral_opportunity" for alert in result["active_alerts"])
    
    @pytest.mark.asyncio
    async def test_generate_performance_report(self, performance_tracker, campaign_data):
        """Test performance report generation"""
        with patch.object(performance_tracker, '_generate_report') as mock_report:
            mock_report.return_value = {
                "success": True,
                "performance_report": {
                    "report_id": "report_001",
                    "generated_at": "2025-01-31T12:00:00Z",
                    "report_period": "2025-01-01 to 2025-01-31",
                    "executive_summary": {
                        "key_achievements": [
                            "425% ROI on AI content campaign",
                            "89% above industry engagement rates",
                            "15,000 new qualified leads generated"
                        ],
                        "total_reach": 567800,
                        "total_engagement": 28450,
                        "total_conversions": 445,
                        "overall_performance_score": 9.2
                    },
                    "detailed_metrics": {
                        "content_performance": {
                            "total_content_published": 45,
                            "average_engagement_rate": 5.67,
                            "top_performing_content_type": "educational_posts",
                            "best_performing_platform": "linkedin",
                            "content_quality_score": 8.9
                        },
                        "audience_insights": {
                            "primary_demographics": "Marketing professionals, 25-44",
                            "top_locations": ["US", "UK", "Canada"],
                            "engagement_patterns": "Highest on Tuesday-Thursday, 9-11 AM",
                            "audience_growth_rate": 0.28
                        },
                        "financial_performance": {
                            "total_investment": 25000,
                            "total_revenue": 189000,
                            "roi": 4.25,
                            "cost_per_acquisition": 42.13,
                            "customer_lifetime_value": 847
                        }
                    },
                    "trend_analysis": {
                        "growth_trends": [
                            "Engagement rates trending up 15% month-over-month",
                            "Video content showing 40% higher engagement",
                            "LinkedIn proving most profitable platform"
                        ],
                        "seasonal_patterns": [
                            "Higher engagement during weekdays",
                            "B2B content performs better morning hours",
                            "Educational content peaks mid-week"
                        ]
                    },
                    "recommendations": {
                        "immediate_actions": [
                            "Increase video content production by 50%",
                            "Allocate more budget to LinkedIn advertising",
                            "Test live content formats"
                        ],
                        "strategic_initiatives": [
                            "Develop advanced AI content series",
                            "Build community platform for engaged users",
                            "Create enterprise content packages"
                        ],
                        "optimization_opportunities": [
                            "Improve mobile content experience",
                            "Enhance email nurture sequences",
                            "Expand to TikTok for younger demographics"
                        ]
                    }
                },
                "report_format": "comprehensive",
                "visualizations": [
                    "engagement_trends_chart",
                    "platform_performance_comparison",
                    "roi_progression_graph",
                    "audience_demographics_pie"
                ]
            }
            
            result = await performance_tracker.generate_performance_report(
                campaign_data=campaign_data,
                report_type="comprehensive",
                include_visualizations=True
            )
            
            assert result["success"] is True
            assert result["performance_report"]["executive_summary"]["overall_performance_score"] > 9.0
            assert result["performance_report"]["detailed_metrics"]["financial_performance"]["roi"] > 4.0
            assert len(result["performance_report"]["recommendations"]["immediate_actions"]) >= 3


class TestMetricsCollector:
    """Test suite for MetricsCollector"""
    
    @pytest.fixture
    def metrics_collector(self):
        """Create a metrics collector instance"""
        return MetricsCollector()
    
    def test_metrics_collector_initialization(self, metrics_collector):
        """Test metrics collector initialization"""
        assert metrics_collector is not None
        assert hasattr(metrics_collector, 'platform_connectors')
        assert hasattr(metrics_collector, 'data_processors')
        assert hasattr(metrics_collector, 'metric_validators')
    
    @pytest.mark.asyncio
    async def test_collect_platform_metrics(self, metrics_collector):
        """Test collecting metrics from different platforms"""
        platforms = [Platform.LINKEDIN, Platform.FACEBOOK, Platform.INSTAGRAM]
        
        with patch.object(metrics_collector, '_collect_from_platforms') as mock_collect:
            mock_collect.return_value = {
                "success": True,
                "metrics_by_platform": {
                    "linkedin": {
                        "reach": 56000,
                        "impressions": 89500,
                        "engagement_rate": 6.7,
                        "clicks": 2340,
                        "shares": 145
                    },
                    "facebook": {
                        "reach": 145000,
                        "impressions": 234500,
                        "engagement_rate": 4.2,
                        "clicks": 3450,
                        "shares": 289
                    },
                    "instagram": {
                        "reach": 33500,
                        "impressions": 67200,
                        "engagement_rate": 7.9,
                        "clicks": 1120,
                        "shares": 78
                    }
                },
                "collection_timestamp": "2025-01-31T12:00:00Z",
                "data_quality_score": 95.5
            }
            
            result = await metrics_collector.collect_metrics(
                platforms=platforms,
                time_range="24_hours"
            )
            
            assert result["success"] is True
            assert len(result["metrics_by_platform"]) == 3
            assert result["data_quality_score"] > 95.0


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
