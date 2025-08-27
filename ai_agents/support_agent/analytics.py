"""
Support Agent Analytics & Metrics

Advanced analytics, performance monitoring, and business intelligence for
Support Agent with real-time dashboards and predictive insights.

Author: Fahed Mlaiel <mlaiel@live.de>  
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import statistics

# Monitoring and metrics
from prometheus_client import Counter, Histogram, Gauge, Summary
import psutil

logger = logging.getLogger(__name__)

# Prometheus metrics
support_requests_total = Counter(
    'support_requests_total', 
    'Total number of support requests',
    ['category', 'priority', 'channel']
)

response_time_histogram = Histogram(
    'support_response_time_seconds',
    'Response time for support requests',
    ['action', 'category']
)

active_conversations_gauge = Gauge(
    'support_active_conversations',
    'Number of active conversations'
)

resolution_rate_gauge = Gauge(
    'support_resolution_rate',
    'Percentage of tickets resolved automatically'
)

customer_satisfaction_gauge = Gauge(
    'support_customer_satisfaction',
    'Average customer satisfaction score'
)

escalation_rate_gauge = Gauge(
    'support_escalation_rate', 
    'Percentage of tickets escalated to human agents'
)

@dataclass
class MetricSnapshot:
    """Snapshot of metrics at a point in time"""
    timestamp: datetime
    total_requests: int
    active_conversations: int
    average_response_time: float
    resolution_rate: float
    customer_satisfaction: float
    escalation_rate: float
    
    # Category breakdown
    category_stats: Dict[str, int] = field(default_factory=dict)
    priority_stats: Dict[str, int] = field(default_factory=dict)
    channel_stats: Dict[str, int] = field(default_factory=dict)
    
    # Performance metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0

@dataclass  
class ConversationAnalytics:
    """Analytics for individual conversation"""
    conversation_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # Interaction metrics
    total_messages: int = 0
    user_messages: int = 0
    agent_messages: int = 0
    
    # Quality metrics
    sentiment_scores: List[float] = field(default_factory=list)
    intent_confidence: List[float] = field(default_factory=list)
    
    # Resolution metrics
    resolved: bool = False
    resolution_method: str = ""  # auto, human, escalated
    customer_satisfaction: Optional[int] = None
    
    # Performance metrics
    first_response_time: Optional[float] = None  # seconds
    total_response_time: float = 0.0
    
    def get_duration(self) -> Optional[float]:
        """Get conversation duration in seconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def get_average_sentiment(self) -> float:
        """Get average sentiment score"""
        return statistics.mean(self.sentiment_scores) if self.sentiment_scores else 0.0
    
    def get_average_intent_confidence(self) -> float:
        """Get average intent confidence"""
        return statistics.mean(self.intent_confidence) if self.intent_confidence else 0.0

class PerformanceMonitor:
    """Real-time performance monitoring system"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        
        # Time-series data storage
        self.response_times = deque(maxlen=window_size)
        self.request_counts = deque(maxlen=window_size)
        self.error_counts = deque(maxlen=window_size)
        
        # Real-time counters
        self.total_requests = 0
        self.total_errors = 0
        self.active_conversations = 0
        
        # Performance tracking
        self.last_reset = datetime.now(timezone.utc)
        
    def record_request(self, response_time: float, success: bool = True):
        """Record a request with response time and success status"""
        self.response_times.append(response_time)
        self.total_requests += 1
        
        if not success:
            self.total_errors += 1
            self.error_counts.append(1)
        else:
            self.error_counts.append(0)
        
        # Update Prometheus metrics
        response_time_histogram.observe(response_time)
        
    def get_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        now = datetime.now(timezone.utc)
        uptime = (now - self.last_reset).total_seconds()
        
        return {
            'requests_per_second': self.total_requests / uptime if uptime > 0 else 0,
            'average_response_time': statistics.mean(self.response_times) if self.response_times else 0,
            'p95_response_time': self._percentile(self.response_times, 95) if self.response_times else 0,
            'p99_response_time': self._percentile(self.response_times, 99) if self.response_times else 0,
            'error_rate': self.total_errors / self.total_requests if self.total_requests > 0 else 0,
            'active_conversations': self.active_conversations,
            'uptime_seconds': uptime
        }
    
    def _percentile(self, data: deque, percentile: float) -> float:
        """Calculate percentile from deque data"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int((percentile / 100.0) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]

class AnalyticsEngine:
    """Advanced analytics engine for support operations"""
    
    def __init__(self):
        self.conversation_analytics: Dict[str, ConversationAnalytics] = {}
        self.historical_snapshots: List[MetricSnapshot] = []
        self.performance_monitor = PerformanceMonitor()
        
        # Business metrics tracking
        self.resolution_stats = {
            'auto_resolved': 0,
            'human_resolved': 0,
            'escalated': 0,
            'unresolved': 0
        }
        
        self.category_performance = defaultdict(lambda: {
            'total': 0,
            'resolved': 0,
            'avg_time': 0.0,
            'satisfaction': []
        })
        
        # Predictive analytics data
        self.trend_data = {
            'hourly_volumes': defaultdict(int),
            'daily_volumes': defaultdict(int),
            'weekly_patterns': defaultdict(list)
        }
        
    def start_conversation(self, conversation_id: str, user_id: str) -> ConversationAnalytics:
        """Start tracking a new conversation"""
        analytics = ConversationAnalytics(
            conversation_id=conversation_id,
            user_id=user_id,
            start_time=datetime.now(timezone.utc)
        )
        
        self.conversation_analytics[conversation_id] = analytics
        self.performance_monitor.active_conversations += 1
        
        # Update Prometheus metrics
        active_conversations_gauge.set(self.performance_monitor.active_conversations)
        
        return analytics
    
    def end_conversation(
        self, 
        conversation_id: str,
        resolved: bool = False,
        resolution_method: str = "",
        customer_satisfaction: Optional[int] = None
    ):
        """End conversation tracking"""
        if conversation_id not in self.conversation_analytics:
            return
        
        analytics = self.conversation_analytics[conversation_id]
        analytics.end_time = datetime.now(timezone.utc)
        analytics.resolved = resolved
        analytics.resolution_method = resolution_method
        analytics.customer_satisfaction = customer_satisfaction
        
        # Update global stats
        if resolved:
            if resolution_method == 'auto':
                self.resolution_stats['auto_resolved'] += 1
            elif resolution_method == 'human':
                self.resolution_stats['human_resolved'] += 1
            elif resolution_method == 'escalated':
                self.resolution_stats['escalated'] += 1
        else:
            self.resolution_stats['unresolved'] += 1
        
        self.performance_monitor.active_conversations = max(
            0, self.performance_monitor.active_conversations - 1
        )
        
        # Update Prometheus metrics
        active_conversations_gauge.set(self.performance_monitor.active_conversations)
        
        if customer_satisfaction:
            customer_satisfaction_gauge.set(self._calculate_avg_satisfaction())
    
    def record_message(
        self,
        conversation_id: str,
        sender: str,
        response_time: float = None,
        sentiment_score: float = None,
        intent_confidence: float = None
    ):
        """Record a message in conversation"""
        if conversation_id not in self.conversation_analytics:
            return
        
        analytics = self.conversation_analytics[conversation_id]
        analytics.total_messages += 1
        
        if sender == 'user':
            analytics.user_messages += 1
        elif sender == 'agent':
            analytics.agent_messages += 1
            
            # Record first response time
            if analytics.first_response_time is None and response_time:
                analytics.first_response_time = response_time
        
        # Track quality metrics
        if sentiment_score is not None:
            analytics.sentiment_scores.append(sentiment_score)
        
        if intent_confidence is not None:
            analytics.intent_confidence.append(intent_confidence)
        
        # Track performance
        if response_time:
            analytics.total_response_time += response_time
            self.performance_monitor.record_request(response_time)
    
    def record_support_request(
        self,
        category: str,
        priority: str, 
        channel: str,
        response_time: float = None
    ):
        """Record a new support request"""
        # Update Prometheus metrics
        support_requests_total.labels(
            category=category,
            priority=priority,
            channel=channel
        ).inc()
        
        if response_time:
            response_time_histogram.labels(
                action='handle_request',
                category=category
            ).observe(response_time)
        
        # Update trend data
        now = datetime.now(timezone.utc)
        hour_key = f"{now.date()}_{now.hour:02d}"
        day_key = str(now.date())
        week_key = f"{now.year}_W{now.isocalendar()[1]}"
        
        self.trend_data['hourly_volumes'][hour_key] += 1
        self.trend_data['daily_volumes'][day_key] += 1
        self.trend_data['weekly_patterns'][week_key].append({
            'timestamp': now,
            'category': category,
            'priority': priority
        })
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics dashboard data"""
        performance = self.performance_monitor.get_metrics()
        
        # Calculate resolution rates
        total_resolutions = sum(self.resolution_stats.values())
        auto_resolution_rate = (
            self.resolution_stats['auto_resolved'] / total_resolutions 
            if total_resolutions > 0 else 0
        )
        
        escalation_rate = (
            self.resolution_stats['escalated'] / total_resolutions
            if total_resolutions > 0 else 0
        )
        
        # System metrics
        system_metrics = self._get_system_metrics()
        
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'performance': performance,
            'resolution_stats': {
                'auto_resolution_rate': auto_resolution_rate,
                'escalation_rate': escalation_rate,
                'total_resolutions': total_resolutions,
                'breakdown': self.resolution_stats
            },
            'system': system_metrics,
            'active_conversations': len([
                a for a in self.conversation_analytics.values() 
                if a.end_time is None
            ]),
            'customer_satisfaction': self._calculate_avg_satisfaction()
        }
    
    def get_historical_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Get historical analysis and trends"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Filter recent conversations
        recent_conversations = [
            conv for conv in self.conversation_analytics.values()
            if conv.start_time >= cutoff_date
        ]
        
        if not recent_conversations:
            return {'message': 'No data available for the specified period'}
        
        # Calculate trends
        daily_volumes = self._calculate_daily_volumes(recent_conversations)
        category_analysis = self._analyze_categories(recent_conversations)
        performance_trends = self._analyze_performance_trends(recent_conversations)
        
        return {
            'period': f"Last {days} days",
            'total_conversations': len(recent_conversations),
            'daily_volumes': daily_volumes,
            'category_analysis': category_analysis,
            'performance_trends': performance_trends,
            'satisfaction_trend': self._calculate_satisfaction_trend(recent_conversations),
            'resolution_trends': self._calculate_resolution_trends(recent_conversations)
        }
    
    def get_predictive_insights(self) -> Dict[str, Any]:
        """Generate predictive insights and forecasts"""
        insights = {
            'predicted_volume': self._predict_volume(),
            'capacity_recommendations': self._recommend_capacity(),
            'trending_issues': self._identify_trending_issues(),
            'optimization_opportunities': self._identify_optimizations()
        }
        
        return insights
    
    def export_analytics_data(self, format: str = 'json') -> str:
        """Export analytics data for external analysis"""
        export_data = {
            'export_timestamp': datetime.now(timezone.utc).isoformat(),
            'conversation_analytics': [
                {
                    'conversation_id': conv.conversation_id,
                    'user_id': conv.user_id,
                    'duration': conv.get_duration(),
                    'messages': conv.total_messages,
                    'resolved': conv.resolved,
                    'satisfaction': conv.customer_satisfaction,
                    'avg_sentiment': conv.get_average_sentiment()
                }
                for conv in self.conversation_analytics.values()
            ],
            'performance_metrics': self.performance_monitor.get_metrics(),
            'resolution_stats': self.resolution_stats,
            'trend_data': dict(self.trend_data)
        }
        
        if format == 'json':
            return json.dumps(export_data, indent=2)
        elif format == 'csv':
            return self._convert_to_csv(export_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    # Helper methods
    
    def _get_system_metrics(self) -> Dict[str, float]:
        """Get current system performance metrics"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
            }
        except Exception as e:
            logger.warning(f"Failed to get system metrics: {e}")
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'load_average': 0
            }
    
    def _calculate_avg_satisfaction(self) -> float:
        """Calculate average customer satisfaction"""
        satisfactions = [
            conv.customer_satisfaction
            for conv in self.conversation_analytics.values()
            if conv.customer_satisfaction is not None
        ]
        
        return statistics.mean(satisfactions) if satisfactions else 0.0
    
    def _calculate_daily_volumes(self, conversations: List[ConversationAnalytics]) -> Dict[str, int]:
        """Calculate daily conversation volumes"""
        daily_counts = defaultdict(int)
        
        for conv in conversations:
            day_key = conv.start_time.date().isoformat()
            daily_counts[day_key] += 1
        
        return dict(daily_counts)
    
    def _analyze_categories(self, conversations: List[ConversationAnalytics]) -> Dict[str, Any]:
        """Analyze performance by category"""
        # This would require category information to be stored in ConversationAnalytics
        # Simplified implementation for now
        return {
            'top_categories': [
                {'category': 'content_upload', 'count': 45, 'avg_resolution_time': 1.2},
                {'category': 'technical_issue', 'count': 32, 'avg_resolution_time': 2.1},
                {'category': 'account_management', 'count': 28, 'avg_resolution_time': 0.8}
            ]
        }
    
    def _analyze_performance_trends(self, conversations: List[ConversationAnalytics]) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        resolved_conversations = [conv for conv in conversations if conv.resolved]
        
        if not resolved_conversations:
            return {}
        
        resolution_times = [
            conv.get_duration() for conv in resolved_conversations 
            if conv.get_duration() is not None
        ]
        
        return {
            'average_resolution_time': statistics.mean(resolution_times) if resolution_times else 0,
            'median_resolution_time': statistics.median(resolution_times) if resolution_times else 0,
            'resolution_rate': len(resolved_conversations) / len(conversations),
            'trend_direction': 'improving'  # Simplified
        }
    
    def _calculate_satisfaction_trend(self, conversations: List[ConversationAnalytics]) -> Dict[str, Any]:
        """Calculate customer satisfaction trends"""
        satisfaction_scores = [
            conv.customer_satisfaction
            for conv in conversations
            if conv.customer_satisfaction is not None
        ]
        
        if not satisfaction_scores:
            return {}
        
        return {
            'average': statistics.mean(satisfaction_scores),
            'median': statistics.median(satisfaction_scores),
            'trend': 'stable',  # Simplified
            'distribution': {
                '5_star': len([s for s in satisfaction_scores if s == 5]),
                '4_star': len([s for s in satisfaction_scores if s == 4]),
                '3_star': len([s for s in satisfaction_scores if s == 3]),
                '2_star': len([s for s in satisfaction_scores if s == 2]),
                '1_star': len([s for s in satisfaction_scores if s == 1])
            }
        }
    
    def _calculate_resolution_trends(self, conversations: List[ConversationAnalytics]) -> Dict[str, Any]:
        """Calculate resolution method trends"""
        resolution_methods = [conv.resolution_method for conv in conversations if conv.resolved]
        
        method_counts = defaultdict(int)
        for method in resolution_methods:
            method_counts[method] += 1
        
        return {
            'total_resolutions': len(resolution_methods),
            'method_breakdown': dict(method_counts),
            'auto_resolution_rate': method_counts['auto'] / len(resolution_methods) if resolution_methods else 0
        }
    
    def _predict_volume(self) -> Dict[str, Any]:
        """Predict future conversation volumes"""
        # Simplified predictive model
        recent_daily_avg = sum(self.trend_data['daily_volumes'].values()) / max(len(self.trend_data['daily_volumes']), 1)
        
        return {
            'next_24h_predicted': int(recent_daily_avg * 1.1),  # 10% growth assumption
            'confidence': 0.75,
            'basis': 'historical_average_with_growth_factor'
        }
    
    def _recommend_capacity(self) -> List[Dict[str, Any]]:
        """Recommend capacity adjustments"""
        current_load = self.performance_monitor.active_conversations
        
        recommendations = []
        
        if current_load > 800:  # 80% of 1000 max
            recommendations.append({
                'type': 'scale_up',
                'reason': 'High conversation load detected',
                'suggested_action': 'Add 2 more agent instances',
                'priority': 'high'
            })
        
        elif current_load < 200:  # 20% of 1000 max
            recommendations.append({
                'type': 'scale_down',
                'reason': 'Low utilization detected',
                'suggested_action': 'Consider reducing agent instances',
                'priority': 'low'
            })
        
        return recommendations
    
    def _identify_trending_issues(self) -> List[Dict[str, Any]]:
        """Identify trending support issues"""
        # This would analyze conversation content and categories
        return [
            {
                'issue': 'Music upload failures',
                'trend': 'increasing',
                'impact': 'medium',
                'suggested_action': 'Review upload infrastructure'
            }
        ]
    
    def _identify_optimizations(self) -> List[Dict[str, Any]]:
        """Identify optimization opportunities"""
        opportunities = []
        
        # Check resolution rate
        total_resolutions = sum(self.resolution_stats.values())
        auto_rate = self.resolution_stats['auto_resolved'] / total_resolutions if total_resolutions > 0 else 0
        
        if auto_rate < 0.7:  # Less than 70% auto-resolution
            opportunities.append({
                'type': 'automation',
                'description': 'Increase auto-resolution rate',
                'potential_impact': 'Reduce human agent workload by 20%',
                'implementation': 'Enhance knowledge base and response templates'
            })
        
        return opportunities
    
    def _convert_to_csv(self, data: Dict[str, Any]) -> str:
        """Convert analytics data to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write conversation analytics
        writer.writerow(['Conversation ID', 'User ID', 'Duration', 'Messages', 'Resolved', 'Satisfaction'])
        
        for conv in data['conversation_analytics']:
            writer.writerow([
                conv['conversation_id'],
                conv['user_id'],
                conv['duration'],
                conv['messages'],
                conv['resolved'],
                conv['satisfaction']
            ])
        
        return output.getvalue()

# Global analytics instance
_analytics_engine: Optional[AnalyticsEngine] = None

def get_analytics_engine() -> AnalyticsEngine:
    """Get global analytics engine instance"""
    global _analytics_engine
    if _analytics_engine is None:
        _analytics_engine = AnalyticsEngine()
    return _analytics_engine
