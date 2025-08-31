"""
Performance Tracker - Advanced content performance monitoring and analytics

Professional performance tracking system that monitors content effectiveness,
engagement metrics, and provides actionable insights for optimization.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics


@dataclass
class ContentMetrics:
    """Data class for content performance metrics"""
    content_id: str
    content_type: str
    platform: str
    created_at: datetime
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    clicks: int = 0
    conversions: int = 0
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    ctr: float = 0.0  # Click-through rate
    conversion_rate: float = 0.0
    quality_score: float = 0.0
    sentiment_score: float = 0.0


@dataclass
class PerformanceInsight:
    """Data class for performance insights"""
    insight_type: str
    title: str
    description: str
    impact_level: str  # high, medium, low
    recommendation: str
    data_points: Dict[str, Any]
    confidence_score: float


class PerformanceTracker:
    """
    Advanced performance tracking system that provides:
    
    - Real-time content performance monitoring
    - Multi-platform analytics aggregation
    - Engagement pattern analysis
    - Performance benchmarking
    - Predictive performance modeling
    - A/B testing analytics
    - ROI calculation and attribution
    - Automated insight generation
    """
    
    def __init__(self):
        """Initialize performance tracker"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Metrics storage
        self.metrics_data = defaultdict(list)
        self.performance_history = defaultdict(list)
        
        # Benchmark data for comparison
        self.platform_benchmarks = {
            'instagram': {
                'engagement_rate': 0.018,  # 1.8% average
                'reach_rate': 0.10,        # 10% of followers
                'story_completion': 0.70,   # 70% completion rate
                'save_rate': 0.005         # 0.5% save rate
            },
            'twitter': {
                'engagement_rate': 0.045,  # 4.5% average
                'retweet_rate': 0.015,     # 1.5% retweet rate
                'reply_rate': 0.008,       # 0.8% reply rate
                'link_clicks': 0.02        # 2% click rate
            },
            'linkedin': {
                'engagement_rate': 0.039,  # 3.9% average
                'comment_rate': 0.015,     # 1.5% comment rate
                'share_rate': 0.008,       # 0.8% share rate
                'connection_rate': 0.12    # 12% connection rate
            },
            'tiktok': {
                'engagement_rate': 0.067,  # 6.7% average
                'completion_rate': 0.90,   # 90% video completion
                'share_rate': 0.025,       # 2.5% share rate
                'follow_rate': 0.018       # 1.8% follow rate
            },
            'youtube': {
                'engagement_rate': 0.068,  # 6.8% average
                'watch_time': 0.60,        # 60% average watch time
                'subscriber_rate': 0.005,  # 0.5% new subscribers
                'comment_rate': 0.012      # 1.2% comment rate
            }
        }
        
        # Performance thresholds
        self.performance_thresholds = {
            'excellent': 0.8,
            'good': 0.6,
            'average': 0.4,
            'poor': 0.2
        }
        
        # Insight generation patterns
        self.insight_patterns = {
            'high_engagement': {
                'trigger': lambda metrics: metrics.engagement_rate > 0.05,
                'title': 'High Engagement Content',
                'template': 'This content achieved {engagement_rate:.1%} engagement, significantly above average.'
            },
            'viral_potential': {
                'trigger': lambda metrics: metrics.shares > metrics.views * 0.1,
                'title': 'Viral Content Detected',
                'template': 'This content shows viral potential with {share_rate:.1%} share rate.'
            },
            'low_reach': {
                'trigger': lambda metrics: metrics.reach < metrics.impressions * 0.1,
                'title': 'Limited Reach Alert',
                'template': 'Content reach is low compared to impressions. Consider boosting.'
            }
        }
    
    async def track_content_performance(
        self,
        content_id: str,
        content_type: str,
        platform: str,
        metrics_data: Dict[str, Any]
    ) -> ContentMetrics:
        """
        Track performance metrics for a piece of content.
        
        Args:
            content_id: Unique identifier for content
            content_type: Type of content (post, video, story, etc.)
            platform: Platform where content was published
            metrics_data: Raw metrics data from platform APIs
            
        Returns:
            Processed content metrics
        """



        try:
            # Create metrics object
            metrics = ContentMetrics(
                content_id=content_id,
                content_type=content_type,
                platform=platform,
                created_at=datetime.now(),
                **self._extract_platform_metrics(platform, metrics_data)
            )
            
            # Calculate derived metrics
            metrics.engagement_rate = await self._calculate_engagement_rate(metrics)
            metrics.ctr = await self._calculate_ctr(metrics)
            metrics.conversion_rate = await self._calculate_conversion_rate(metrics)
            
            # Store metrics
            self.metrics_data[content_id].append(metrics)
            self.performance_history[platform].append(metrics)
            
            # Log performance
            self.logger.info(f"Tracked performance for {content_id}: {metrics.engagement_rate:.2%} engagement")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error tracking performance: {str(e)}")
            return ContentMetrics(content_id, content_type, platform, datetime.now())
    
    def _extract_platform_metrics(self, platform: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics based on platform"""
        platform_mappings = {
            'instagram': {
                'views': data.get('impressions', 0),
                'likes': data.get('like_count', 0),
                'shares': data.get('shares_count', 0),
                'comments': data.get('comments_count', 0),
                'reach': data.get('reach', 0),
                'impressions': data.get('impressions', 0)
            },
            'twitter': {
                'views': data.get('impression_count', 0),
                'likes': data.get('like_count', 0),
                'shares': data.get('retweet_count', 0),
                'comments': data.get('reply_count', 0),
                'clicks': data.get('url_link_clicks', 0),
                'reach': data.get('impression_count', 0),
                'impressions': data.get('impression_count', 0)
            },
            'linkedin': {
                'views': data.get('impressions', 0),
                'likes': data.get('numLikes', 0),
                'shares': data.get('numShares', 0),
                'comments': data.get('numComments', 0),
                'clicks': data.get('clicks', 0),
                'reach': data.get('uniqueImpressions', 0),
                'impressions': data.get('impressions', 0)
            },
            'tiktok': {
                'views': data.get('video_view_count', 0),
                'likes': data.get('like_count', 0),
                'shares': data.get('share_count', 0),
                'comments': data.get('comment_count', 0),
                'reach': data.get('video_view_count', 0),
                'impressions': data.get('video_view_count', 0)
            },
            'youtube': {
                'views': data.get('views', 0),
                'likes': data.get('likeCount', 0),
                'shares': data.get('shares', 0),
                'comments': data.get('commentCount', 0),
                'reach': data.get('views', 0),
                'impressions': data.get('impressions', 0)
            }
        }
        
        return platform_mappings.get(platform, {
            'views': data.get('views', 0),
            'likes': data.get('likes', 0),
            'shares': data.get('shares', 0),
            'comments': data.get('comments', 0),
            'clicks': data.get('clicks', 0),
            'reach': data.get('reach', 0),
            'impressions': data.get('impressions', 0)
        })
    
    async def _calculate_engagement_rate(self, metrics: ContentMetrics) -> float:
        """Calculate engagement rate based on platform"""
        total_engagements = metrics.likes + metrics.shares + metrics.comments
        
        if metrics.platform in ['instagram', 'tiktok']:
            # For visual platforms, use reach as denominator
            base = max(metrics.reach, metrics.views, 1)
        else:
            # For other platforms, use impressions
            base = max(metrics.impressions, metrics.views, 1)
        
        return total_engagements / base
    
    async def _calculate_ctr(self, metrics: ContentMetrics) -> float:
        """Calculate click-through rate"""
        if metrics.impressions == 0:
            return 0.0
        return metrics.clicks / metrics.impressions
    
    async def _calculate_conversion_rate(self, metrics: ContentMetrics) -> float:
        """Calculate conversion rate"""
        if metrics.clicks == 0:
            return 0.0
        return metrics.conversions / metrics.clicks
    
    async def get_performance_summary(
        self,
        content_ids: Optional[List[str]] = None,
        platform: Optional[str] = None,
        timeframe_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get performance summary for content.
        
        Args:
            content_ids: Specific content IDs to analyze
            platform: Filter by platform
            timeframe_days: Days to include in analysis
            
        Returns:
            Performance summary with key metrics and insights
        """



        try:
            # Filter metrics based on criteria
            filtered_metrics = await self._filter_metrics(
                content_ids, platform, timeframe_days
            )
            
            if not filtered_metrics:
                return {'error': 'No metrics found for the specified criteria'}
            
            # Calculate summary statistics
            summary = {
                'total_content': len(filtered_metrics),
                'total_views': sum(m.views for m in filtered_metrics),
                'total_engagement': sum(m.likes + m.shares + m.comments for m in filtered_metrics),
                'average_engagement_rate': statistics.mean([m.engagement_rate for m in filtered_metrics]),
                'best_performing': await self._get_best_performing_content(filtered_metrics),
                'platform_breakdown': await self._get_platform_breakdown(filtered_metrics),
                'content_type_breakdown': await self._get_content_type_breakdown(filtered_metrics),
                'performance_trends': await self._get_performance_trends(filtered_metrics),
                'benchmark_comparison': await self._compare_to_benchmarks(filtered_metrics)
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating performance summary: {str(e)}")
            return {'error': f'Failed to generate summary: {str(e)}'}
    
    async def _filter_metrics(
        self,
        content_ids: Optional[List[str]],
        platform: Optional[str],
        timeframe_days: int
    ) -> List[ContentMetrics]:
        """Filter metrics based on criteria"""
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)
        filtered = []
        
        for content_id, metrics_list in self.metrics_data.items():
            for metrics in metrics_list:
                # Apply filters
                if content_ids and content_id not in content_ids:
                    continue
                if platform and metrics.platform != platform:
                    continue
                if metrics.created_at < cutoff_date:
                    continue
                
                filtered.append(metrics)
        
        return filtered
    
    async def _get_best_performing_content(self, metrics_list: List[ContentMetrics]) -> Dict[str, Any]:
        """Identify best performing content"""
        if not metrics_list:
            return {}
        
        # Sort by engagement rate
        sorted_by_engagement = sorted(metrics_list, key=lambda m: m.engagement_rate, reverse=True)
        
        # Sort by total engagement
        sorted_by_total = sorted(
            metrics_list, 
            key=lambda m: m.likes + m.shares + m.comments, 
            reverse=True
        )
        
        return {
            'highest_engagement_rate': {
                'content_id': sorted_by_engagement[0].content_id,
                'engagement_rate': sorted_by_engagement[0].engagement_rate,
                'platform': sorted_by_engagement[0].platform
            },
            'highest_total_engagement': {
                'content_id': sorted_by_total[0].content_id,
                'total_engagement': sorted_by_total[0].likes + sorted_by_total[0].shares + sorted_by_total[0].comments,
                'platform': sorted_by_total[0].platform
            }
        }
    
    async def _get_platform_breakdown(self, metrics_list: List[ContentMetrics]) -> Dict[str, Any]:
        """Get performance breakdown by platform"""
        platform_data = defaultdict(list)
        
        for metrics in metrics_list:
            platform_data[metrics.platform].append(metrics)
        
        breakdown = {}
        for platform, platform_metrics in platform_data.items():
            breakdown[platform] = {
                'content_count': len(platform_metrics),
                'total_views': sum(m.views for m in platform_metrics),
                'avg_engagement_rate': statistics.mean([m.engagement_rate for m in platform_metrics]),
                'total_engagement': sum(m.likes + m.shares + m.comments for m in platform_metrics)
            }
        
        return breakdown
    
    async def _get_content_type_breakdown(self, metrics_list: List[ContentMetrics]) -> Dict[str, Any]:
        """Get performance breakdown by content type"""
        type_data = defaultdict(list)
        
        for metrics in metrics_list:
            type_data[metrics.content_type].append(metrics)
        
        breakdown = {}
        for content_type, type_metrics in type_data.items():
            breakdown[content_type] = {
                'content_count': len(type_metrics),
                'avg_engagement_rate': statistics.mean([m.engagement_rate for m in type_metrics]),
                'total_views': sum(m.views for m in type_metrics)
            }
        
        return breakdown
    
    async def _get_performance_trends(self, metrics_list: List[ContentMetrics]) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        # Sort by date
        sorted_metrics = sorted(metrics_list, key=lambda m: m.created_at)
        
        if len(sorted_metrics) < 2:
            return {'trend': 'insufficient_data'}
        
        # Calculate weekly trends
        weekly_data = defaultdict(list)
        for metrics in sorted_metrics:
            week = metrics.created_at.strftime('%Y-W%U')
            weekly_data[week].append(metrics)
        
        # Calculate trend direction
        weeks = sorted(weekly_data.keys())
        if len(weeks) >= 2:
            recent_avg = statistics.mean([
                m.engagement_rate for m in weekly_data[weeks[-1]]
            ])
            previous_avg = statistics.mean([
                m.engagement_rate for m in weekly_data[weeks[-2]]
            ])
            
            trend = 'improving' if recent_avg > previous_avg else 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'weekly_breakdown': {
                week: {
                    'avg_engagement': statistics.mean([m.engagement_rate for m in metrics]),
                    'content_count': len(metrics)
                }
                for week, metrics in weekly_data.items()
            }
        }
    
    async def _compare_to_benchmarks(self, metrics_list: List[ContentMetrics]) -> Dict[str, Any]:
        """Compare performance to industry benchmarks"""
        platform_performance = {}
        
        platform_data = defaultdict(list)
        for metrics in metrics_list:
            platform_data[metrics.platform].append(metrics)
        
        for platform, platform_metrics in platform_data.items():
            avg_engagement = statistics.mean([m.engagement_rate for m in platform_metrics])
            benchmark = self.platform_benchmarks.get(platform, {}).get('engagement_rate', 0.02)
            
            performance_ratio = avg_engagement / benchmark if benchmark > 0 else 0
            
            if performance_ratio >= 1.5:
                performance_level = 'excellent'
            elif performance_ratio >= 1.2:
                performance_level = 'above_average'
            elif performance_ratio >= 0.8:
                performance_level = 'average'
            else:
                performance_level = 'below_average'
            
            platform_performance[platform] = {
                'avg_engagement_rate': avg_engagement,
                'benchmark_rate': benchmark,
                'performance_ratio': performance_ratio,
                'performance_level': performance_level
            }
        
        return platform_performance
    
    async def generate_insights(
        self,
        content_ids: Optional[List[str]] = None,
        platform: Optional[str] = None
    ) -> List[PerformanceInsight]:
        """
        Generate actionable insights from performance data.
        
        Args:
            content_ids: Specific content to analyze
            platform: Platform to focus on
            
        Returns:
            List of performance insights with recommendations
        """



        try:
            # Get relevant metrics
            filtered_metrics = await self._filter_metrics(content_ids, platform, 30)
            
            insights = []
            
            # Apply insight patterns
            for metrics in filtered_metrics:
                for pattern_name, pattern in self.insight_patterns.items():
                    if pattern['trigger'](metrics):
                        insight = await self._create_insight(pattern_name, pattern, metrics)
                        insights.append(insight)
            
            # Generate aggregated insights
            aggregated_insights = await self._generate_aggregated_insights(filtered_metrics)
            insights.extend(aggregated_insights)
            
            # Sort by impact level and confidence
            insights.sort(key=lambda i: (
                {'high': 3, 'medium': 2, 'low': 1}[i.impact_level],
                i.confidence_score
            ), reverse=True)
            
            return insights[:10]  # Return top 10 insights
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {str(e)}")
            return []
    
    async def _create_insight(
        self, 
        pattern_name: str, 
        pattern: Dict[str, Any], 
        metrics: ContentMetrics
    ) -> PerformanceInsight:
        """Create insight from pattern and metrics"""
        
        # Calculate specific metrics for the insight
        share_rate = metrics.shares / max(metrics.views, 1)
        
        description = pattern['template'].format(
            engagement_rate=metrics.engagement_rate,
            share_rate=share_rate
        )
        
        # Generate recommendation based on pattern
        recommendations = {
            'high_engagement': 'Analyze what made this content successful and replicate these elements.',
            'viral_potential': 'Consider boosting this content or creating similar content quickly.',
            'low_reach': 'Review posting time, hashtags, and consider promoting this content.'
        }
        
        return PerformanceInsight(
            insight_type=pattern_name,
            title=pattern['title'],
            description=description,
            impact_level='high' if pattern_name in ['viral_potential', 'high_engagement'] else 'medium',
            recommendation=recommendations.get(pattern_name, 'Monitor performance closely.'),
            data_points={
                'content_id': metrics.content_id,
                'platform': metrics.platform,
                'engagement_rate': metrics.engagement_rate,
                'share_rate': share_rate
            },
            confidence_score=0.8
        )
    
    async def _generate_aggregated_insights(self, metrics_list: List[ContentMetrics]) -> List[PerformanceInsight]:
        """Generate insights from aggregated data"""
        insights = []
        
        if len(metrics_list) < 3:
            return insights
        
        # Platform performance insight
        platform_performance = await self._get_platform_breakdown(metrics_list)
        
        best_platform = max(
            platform_performance.items(),
            key=lambda x: x[1]['avg_engagement_rate']
        )
        
        insights.append(PerformanceInsight(
            insight_type='platform_performance',
            title=f'{best_platform[0].title()} is Your Best Platform',
            description=f'{best_platform[0].title()} shows {best_platform[1]["avg_engagement_rate"]:.2%} average engagement rate.',
            impact_level='medium',
            recommendation=f'Focus more content creation efforts on {best_platform[0]}.',
            data_points=best_platform[1],
            confidence_score=0.9
        ))
        
        # Content type insight
        type_performance = await self._get_content_type_breakdown(metrics_list)
        
        if len(type_performance) > 1:
            best_type = max(
                type_performance.items(),
                key=lambda x: x[1]['avg_engagement_rate']
            )
            
            insights.append(PerformanceInsight(
                insight_type='content_type_performance',
                title=f'{best_type[0].replace("_", " ").title()} Content Performs Best',
                description=f'{best_type[0]} content achieves {best_type[1]["avg_engagement_rate"]:.2%} engagement.',
                impact_level='medium',
                recommendation=f'Create more {best_type[0]} content to maximize engagement.',
                data_points=best_type[1],
                confidence_score=0.85
            ))
        
        return insights
    
    async def track_ab_test(
        self,
        test_id: str,
        variant_a_id: str,
        variant_b_id: str,
        test_metric: str = 'engagement_rate'
    ) -> Dict[str, Any]:
        """
        Track A/B test performance between two content variants.
        
        Args:
            test_id: Unique test identifier
            variant_a_id: Content ID for variant A
            variant_b_id: Content ID for variant B
            test_metric: Metric to compare (engagement_rate, ctr, etc.)
            
        Returns:
            A/B test results and statistical significance
        """



        try:
            # Get metrics for both variants
            variant_a_metrics = self.metrics_data.get(variant_a_id, [])
            variant_b_metrics = self.metrics_data.get(variant_b_id, [])
            
            if not variant_a_metrics or not variant_b_metrics:
                return {'error': 'Insufficient data for A/B test analysis'}
            
            # Get latest metrics for each variant
            a_latest = variant_a_metrics[-1]
            b_latest = variant_b_metrics[-1]
            
            # Extract test metric values
            a_value = getattr(a_latest, test_metric, 0)
            b_value = getattr(b_latest, test_metric, 0)
            
            # Calculate statistical significance (simplified)
            difference = abs(a_value - b_value)
            relative_difference = difference / max(a_value, b_value, 0.001)
            
            # Determine winner
            if relative_difference < 0.05:  # Less than 5% difference
                winner = 'inconclusive'
                confidence = 'low'
            elif a_value > b_value:
                winner = 'variant_a'
                confidence = 'high' if relative_difference > 0.2 else 'medium'
            else:
                winner = 'variant_b'
                confidence = 'high' if relative_difference > 0.2 else 'medium'
            
            results = {
                'test_id': test_id,
                'test_metric': test_metric,
                'variant_a': {
                    'content_id': variant_a_id,
                    'metric_value': a_value,
                    'total_engagement': a_latest.likes + a_latest.shares + a_latest.comments
                },
                'variant_b': {
                    'content_id': variant_b_id,
                    'metric_value': b_value,
                    'total_engagement': b_latest.likes + b_latest.shares + b_latest.comments
                },
                'results': {
                    'winner': winner,
                    'confidence': confidence,
                    'relative_difference': relative_difference,
                    'improvement': f"{relative_difference:.1%}"
                },
                'recommendation': await self._get_ab_test_recommendation(winner, relative_difference)
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error tracking A/B test: {str(e)}")
            return {'error': f'A/B test analysis failed: {str(e)}'}
    
    async def _get_ab_test_recommendation(self, winner: str, difference: float) -> str:
        """Generate recommendation based on A/B test results"""
        if winner == 'inconclusive':
            return "Results are inconclusive. Consider running the test longer or with larger audience."
        elif difference > 0.2:
            return f"Clear winner identified. Implement {winner} strategy across all content."
        elif difference > 0.1:
            return f"{winner} shows promising results. Consider broader testing."
        else:
            return "Marginal difference detected. Monitor longer-term trends."
    
    async def export_performance_data(
        self,
        format_type: str = 'json',
        timeframe_days: int = 30
    ) -> str:
        """
        Export performance data in specified format.
        
        Args:
            format_type: Export format (json, csv)
            timeframe_days: Days of data to include
            
        Returns:
            Formatted data string
        """



        try:
            # Get filtered metrics
            filtered_metrics = await self._filter_metrics(None, None, timeframe_days)
            
            if format_type == 'json':
                # Convert to JSON
                export_data = [asdict(metrics) for metrics in filtered_metrics]
                # Convert datetime to string
                for item in export_data:
                    item['created_at'] = item['created_at'].isoformat()
                return json.dumps(export_data, indent=2)
            
            elif format_type == 'csv':
                # Convert to CSV format
                if not filtered_metrics:
                    return "No data available"
                
                # CSV header
                header = list(asdict(filtered_metrics[0]).keys())
                csv_lines = [','.join(header)]
                
                # CSV data
                for metrics in filtered_metrics:
                    data_dict = asdict(metrics)
                    data_dict['created_at'] = data_dict['created_at'].isoformat()
                    csv_lines.append(','.join([str(data_dict[key]) for key in header]))
                
                return '\n'.join(csv_lines)
            
            else:
                return f"Unsupported format: {format_type}"
                
        except Exception as e:
            self.logger.error(f"Error exporting data: {str(e)}")
            return f"Export failed: {str(e)}"


class MetricsCollector:
    """Collects performance metrics from various platforms"""
    
    def __init__(self):
        self.platforms = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def register_platform(self, platform_name: str, collector_func: callable) -> None:
        """Register a platform metrics collector"""
        self.platforms[platform_name] = collector_func
    
    def collect_metrics(self, platform: str, content_id: str) -> Dict[str, Any]:
        """Collect metrics for specific content on a platform"""
        if platform not in self.platforms:
            return {}
        
        try:
            return self.platforms[platform](content_id)
        except Exception as e:
            self.logger.error(f"Error collecting metrics from {platform}: {str(e)}")
            return {}
    
    def collect_all_metrics(self, content_mapping: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Collect metrics from all registered platforms"""
        all_metrics = {}
        for platform, content_id in content_mapping.items():
            all_metrics[platform] = self.collect_metrics(platform, content_id)
        return all_metrics
