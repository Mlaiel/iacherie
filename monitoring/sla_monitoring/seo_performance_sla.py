"""SEO Performance SLA Monitoring System
Enterprise-grade SEO performance tracking and optimization for Creator Economy Platform

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Propriété intellectuelle exclusive
"""

import asyncio
import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import deque, defaultdict
import aiohttp
import json
from urllib.parse import urljoin

@dataclass
class SEOMetric:
    """SEO performance metric definition"""
    name: str
    target_value: float
    current_value: float = 0.0
    unit: str = ""
    threshold_critical: float = 0.0
    threshold_warning: float = 0.0
    measurement_window_minutes: int = 60
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SEOTarget:
    """SEO performance targets for Creator Economy Platform"""
    # Core SEO Performance Targets
    seo_analysis_time_ms: float = 30000.0  # <30s SEO analysis
    keyword_optimization_time_ms: float = 3600000.0  # <1h keyword optimization
    seo_reporting_time_ms: float = 300000.0  # <5min SEO reporting
    search_ranking_improvement_percent: float = 15.0  # 15% ranking improvement target
    organic_traffic_growth_percent: float = 20.0  # 20% organic traffic growth
    
    # Content SEO Targets
    content_seo_score_min: float = 85.0  # Minimum 85/100 SEO score
    meta_optimization_accuracy: float = 95.0  # 95% meta data accuracy
    schema_markup_coverage: float = 90.0  # 90% schema markup coverage
    page_speed_score: float = 90.0  # 90+ Google PageSpeed score
    mobile_optimization_score: float = 95.0  # 95+ mobile optimization
    
    # Technical SEO Targets
    crawl_error_rate: float = 1.0  # <1% crawl error rate
    index_coverage: float = 95.0  # 95% index coverage
    sitemap_freshness_hours: float = 24.0  # <24h sitemap updates
    backlink_quality_score: float = 80.0  # 80+ backlink quality
    domain_authority_target: float = 60.0  # 60+ domain authority

class SEOPerformanceSLA:
    """
    Enterprise SEO Performance SLA Monitoring
    Tracks SEO performance metrics for Creator Economy Platform
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.seo_targets = SEOTarget()
        self.metrics: Dict[str, SEOMetric] = {}
        self.seo_analysis_times: deque = deque(maxlen=1000)
        self.keyword_performance: deque = deque(maxlen=5000)
        self.ranking_history: List[Dict[str, Any]] = []
        self.traffic_analytics: deque = deque(maxlen=10000)
        self.alerts: List[Dict[str, Any]] = []
        self.monitoring_active = False
        
        # Initialize SEO performance metrics
        self._initialize_seo_metrics()
        
    def _initialize_seo_metrics(self):
        """Initialize SEO performance metrics with targets"""
        self.metrics = {
            "seo_analysis_time": SEOMetric(
                name="SEO Analysis Time",
                target_value=self.seo_targets.seo_analysis_time_ms,
                unit="ms",
                threshold_critical=45000.0,  # 50% over target
                threshold_warning=40000.0,   # 33% over target
                measurement_window_minutes=15
            ),
            "keyword_optimization_time": SEOMetric(
                name="Keyword Optimization Time",
                target_value=self.seo_targets.keyword_optimization_time_ms,
                unit="ms",
                threshold_critical=5400000.0,  # 50% over target (1.5h)
                threshold_warning=4800000.0,   # 33% over target (1.33h)
                measurement_window_minutes=60
            ),
            "seo_reporting_time": SEOMetric(
                name="SEO Reporting Time",
                target_value=self.seo_targets.seo_reporting_time_ms,
                unit="ms",
                threshold_critical=450000.0,  # 50% over target (7.5min)
                threshold_warning=400000.0,   # 33% over target (6.67min)
                measurement_window_minutes=10
            ),
            "search_ranking_improvement": SEOMetric(
                name="Search Ranking Improvement",
                target_value=self.seo_targets.search_ranking_improvement_percent,
                unit="%",
                threshold_critical=5.0,    # Below 5% improvement
                threshold_warning=10.0,    # Below 10% improvement
                measurement_window_minutes=1440  # Daily measurement
            ),
            "organic_traffic_growth": SEOMetric(
                name="Organic Traffic Growth",
                target_value=self.seo_targets.organic_traffic_growth_percent,
                unit="%",
                threshold_critical=5.0,    # Below 5% growth
                threshold_warning=15.0,    # Below 15% growth
                measurement_window_minutes=10080  # Weekly measurement
            ),
            "content_seo_score": SEOMetric(
                name="Content SEO Score",
                target_value=self.seo_targets.content_seo_score_min,
                unit="score",
                threshold_critical=70.0,   # Below 70/100
                threshold_warning=80.0,    # Below 80/100
                measurement_window_minutes=60
            ),
            "page_speed_score": SEOMetric(
                name="Page Speed Score",
                target_value=self.seo_targets.page_speed_score,
                unit="score",
                threshold_critical=70.0,   # Below 70
                threshold_warning=85.0,    # Below 85
                measurement_window_minutes=30
            ),
            "mobile_optimization": SEOMetric(
                name="Mobile Optimization Score",
                target_value=self.seo_targets.mobile_optimization_score,
                unit="score",
                threshold_critical=80.0,   # Below 80
                threshold_warning=90.0,    # Below 90
                measurement_window_minutes=60
            )
        }
        
    async def record_seo_analysis(self, analysis_time_ms: float, content_id: str, 
                                 seo_score: float, recommendations: List[str]):
        """Record SEO analysis performance"""
        timestamp = datetime.now()
        
        # Record analysis time
        self.seo_analysis_times.append({
            'timestamp': timestamp,
            'analysis_time': analysis_time_ms,
            'content_id': content_id,
            'seo_score': seo_score,
            'recommendations_count': len(recommendations)
        })
        
        # Update metrics
        self.metrics["seo_analysis_time"].current_value = analysis_time_ms
        self.metrics["seo_analysis_time"].last_updated = timestamp
        
        self.metrics["content_seo_score"].current_value = seo_score
        self.metrics["content_seo_score"].last_updated = timestamp
        
        # Check SLA violations
        await self._check_sla_violations()
        
        self.logger.info(f"SEO analysis recorded: {analysis_time_ms}ms, score: {seo_score}")
        
    async def record_keyword_optimization(self, optimization_time_ms: float, 
                                        keywords: List[str], success_rate: float):
        """Record keyword optimization performance"""
        timestamp = datetime.now()
        
        # Record keyword performance
        self.keyword_performance.append({
            'timestamp': timestamp,
            'optimization_time': optimization_time_ms,
            'keywords_count': len(keywords),
            'success_rate': success_rate,
            'keywords': keywords
        })
        
        # Update metrics
        self.metrics["keyword_optimization_time"].current_value = optimization_time_ms
        self.metrics["keyword_optimization_time"].last_updated = timestamp
        
        await self._check_sla_violations()
        
        self.logger.info(f"Keyword optimization: {optimization_time_ms}ms, {len(keywords)} keywords")
        
    async def record_ranking_update(self, keywords: Dict[str, Dict[str, Any]]):
        """Record search ranking updates"""
        timestamp = datetime.now()
        
        ranking_data = {
            'timestamp': timestamp,
            'keywords': keywords,
            'average_position': statistics.mean([
                kw_data.get('position', 100) for kw_data in keywords.values()
            ]) if keywords else 100
        }
        
        self.ranking_history.append(ranking_data)
        
        # Calculate ranking improvement
        if len(self.ranking_history) >= 2:
            current_avg = ranking_data['average_position']
            previous_avg = self.ranking_history[-2]['average_position']
            
            # Lower position number means better ranking
            improvement = ((previous_avg - current_avg) / previous_avg) * 100
            
            self.metrics["search_ranking_improvement"].current_value = improvement
            self.metrics["search_ranking_improvement"].last_updated = timestamp
        
        await self._check_sla_violations()
        
    async def record_traffic_analytics(self, organic_traffic: int, total_traffic: int, 
                                     sessions: int, bounce_rate: float):
        """Record organic traffic analytics"""
        timestamp = datetime.now()
        
        # Calculate organic traffic percentage
        organic_percentage = (organic_traffic / total_traffic * 100) if total_traffic > 0 else 0
        
        traffic_data = {
            'timestamp': timestamp,
            'organic_traffic': organic_traffic,
            'total_traffic': total_traffic,
            'organic_percentage': organic_percentage,
            'sessions': sessions,
            'bounce_rate': bounce_rate
        }
        
        self.traffic_analytics.append(traffic_data)
        
        # Calculate traffic growth (weekly)
        week_ago = timestamp - timedelta(days=7)
        recent_traffic = [
            t for t in self.traffic_analytics 
            if t['timestamp'] >= week_ago
        ]
        
        if len(recent_traffic) >= 2:
            current_avg = statistics.mean([t['organic_traffic'] for t in recent_traffic[-7:]])
            previous_avg = statistics.mean([t['organic_traffic'] for t in recent_traffic[:-7]]) if len(recent_traffic) > 7 else current_avg
            
            growth = ((current_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0
            
            self.metrics["organic_traffic_growth"].current_value = growth
            self.metrics["organic_traffic_growth"].last_updated = timestamp
        
        await self._check_sla_violations()
        
    async def record_page_speed_analysis(self, url: str, desktop_score: float, 
                                       mobile_score: float, metrics: Dict[str, float]):
        """Record page speed analysis results"""
        timestamp = datetime.now()
        
        # Use average of desktop and mobile scores
        overall_score = (desktop_score + mobile_score) / 2
        
        self.metrics["page_speed_score"].current_value = overall_score
        self.metrics["page_speed_score"].last_updated = timestamp
        self.metrics["page_speed_score"].metadata = {
            'url': url,
            'desktop_score': desktop_score,
            'mobile_score': mobile_score,
            'metrics': metrics
        }
        
        self.metrics["mobile_optimization"].current_value = mobile_score
        self.metrics["mobile_optimization"].last_updated = timestamp
        
        await self._check_sla_violations()
        
        self.logger.info(f"Page speed analysis: {url}, scores: {desktop_score}/{mobile_score}")
        
    async def _check_sla_violations(self):
        """Check for SEO SLA violations and generate alerts"""
        violations = []
        
        for metric_name, metric in self.metrics.items():
            if self._is_critical_violation(metric):
                violations.append({
                    'level': 'CRITICAL',
                    'metric': metric_name,
                    'current_value': metric.current_value,
                    'target_value': metric.target_value,
                    'threshold': metric.threshold_critical,
                    'timestamp': datetime.now(),
                    'sla_type': 'SEO_PERFORMANCE'
                })
            elif self._is_warning_violation(metric):
                violations.append({
                    'level': 'WARNING',
                    'metric': metric_name,
                    'current_value': metric.current_value,
                    'target_value': metric.target_value,
                    'threshold': metric.threshold_warning,
                    'timestamp': datetime.now(),
                    'sla_type': 'SEO_PERFORMANCE'
                })
                
        # Process violations
        for violation in violations:
            await self._process_sla_violation(violation)
            
    def _is_critical_violation(self, metric: SEOMetric) -> bool:
        """Check if metric is in critical violation"""
        if metric.name in ["SEO Analysis Time", "Keyword Optimization Time", "SEO Reporting Time"]:
            return metric.current_value > metric.threshold_critical
        elif metric.name in ["Search Ranking Improvement", "Organic Traffic Growth", 
                           "Content SEO Score", "Page Speed Score", "Mobile Optimization Score"]:
            return metric.current_value < metric.threshold_critical
        return False
        
    def _is_warning_violation(self, metric: SEOMetric) -> bool:
        """Check if metric is in warning state"""
        if metric.name in ["SEO Analysis Time", "Keyword Optimization Time", "SEO Reporting Time"]:
            return metric.current_value > metric.threshold_warning
        elif metric.name in ["Search Ranking Improvement", "Organic Traffic Growth", 
                           "Content SEO Score", "Page Speed Score", "Mobile Optimization Score"]:
            return metric.current_value < metric.threshold_warning
        return False
        
    async def _process_sla_violation(self, violation: Dict[str, Any]):
        """Process SEO SLA violation and generate alert"""
        self.alerts.append(violation)
        
        self.logger.error(
            f"SEO SLA {violation['level']} VIOLATION: {violation['metric']} = "
            f"{violation['current_value']:.2f} (target: {violation['target_value']:.2f})"
        )
        
        # TODO: Integrate with alerting systems (Slack, PagerDuty, email)
        
    async def get_seo_sla_status(self) -> Dict[str, Any]:
        """Get current SEO SLA status and compliance"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'sla_type': 'SEO_PERFORMANCE',
            'overall_compliance': True,
            'metrics': {},
            'violations': len([a for a in self.alerts if a['level'] == 'CRITICAL']),
            'warnings': len([a for a in self.alerts if a['level'] == 'WARNING']),
            'performance_summary': {
                'avg_analysis_time': statistics.mean([
                    a['analysis_time'] for a in list(self.seo_analysis_times)[-10:]
                ]) if self.seo_analysis_times else 0,
                'avg_seo_score': statistics.mean([
                    a['seo_score'] for a in list(self.seo_analysis_times)[-10:]
                ]) if self.seo_analysis_times else 0,
                'keyword_success_rate': statistics.mean([
                    k['success_rate'] for k in list(self.keyword_performance)[-10:]
                ]) if self.keyword_performance else 0
            }
        }
        
        for metric_name, metric in self.metrics.items():
            compliance = not (self._is_critical_violation(metric) or self._is_warning_violation(metric))
            if not compliance:
                status['overall_compliance'] = False
                
            status['metrics'][metric_name] = {
                'current_value': metric.current_value,
                'target_value': metric.target_value,
                'unit': metric.unit,
                'compliance': compliance,
                'last_updated': metric.last_updated.isoformat(),
                'metadata': metric.metadata
            }
            
        return status
        
    async def get_seo_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive SEO performance report"""
        now = datetime.now()
        
        # Calculate statistics for last 7 days
        start_7d = now - timedelta(days=7)
        
        recent_analyses = [
            a for a in self.seo_analysis_times
            if a['timestamp'] >= start_7d
        ]
        
        recent_keywords = [
            k for k in self.keyword_performance
            if k['timestamp'] >= start_7d
        ]
        
        recent_traffic = [
            t for t in self.traffic_analytics
            if t['timestamp'] >= start_7d
        ]
        
        report = {
            'report_timestamp': now.isoformat(),
            'period': '7_days',
            'seo_performance_summary': {
                'analysis_performance': {
                    'total_analyses': len(recent_analyses),
                    'avg_analysis_time': statistics.mean([a['analysis_time'] for a in recent_analyses]) if recent_analyses else 0,
                    'avg_seo_score': statistics.mean([a['seo_score'] for a in recent_analyses]) if recent_analyses else 0,
                    'max_analysis_time': max([a['analysis_time'] for a in recent_analyses]) if recent_analyses else 0
                },
                'keyword_optimization': {
                    'total_optimizations': len(recent_keywords),
                    'avg_optimization_time': statistics.mean([k['optimization_time'] for k in recent_keywords]) if recent_keywords else 0,
                    'avg_success_rate': statistics.mean([k['success_rate'] for k in recent_keywords]) if recent_keywords else 0,
                    'total_keywords_optimized': sum([k['keywords_count'] for k in recent_keywords])
                },
                'traffic_analytics': {
                    'avg_organic_traffic': statistics.mean([t['organic_traffic'] for t in recent_traffic]) if recent_traffic else 0,
                    'avg_organic_percentage': statistics.mean([t['organic_percentage'] for t in recent_traffic]) if recent_traffic else 0,
                    'avg_bounce_rate': statistics.mean([t['bounce_rate'] for t in recent_traffic]) if recent_traffic else 0,
                    'total_sessions': sum([t['sessions'] for t in recent_traffic])
                }
            },
            'sla_compliance': await self.get_seo_sla_status(),
            'ranking_trends': self.ranking_history[-30:] if len(self.ranking_history) > 30 else self.ranking_history
        }
        
        return report
        
    async def optimize_seo_performance(self) -> Dict[str, Any]:
        """Generate SEO performance optimization recommendations"""
        recommendations = {
            'timestamp': datetime.now().isoformat(),
            'optimization_recommendations': [],
            'priority_actions': [],
            'performance_insights': {}
        }
        
        # Analyze current performance
        current_status = await self.get_seo_sla_status()
        
        for metric_name, metric_data in current_status['metrics'].items():
            if not metric_data['compliance']:
                if metric_name == "seo_analysis_time":
                    recommendations['optimization_recommendations'].append({
                        'category': 'Performance',
                        'issue': 'SEO analysis taking too long',
                        'recommendation': 'Optimize SEO analysis algorithms, implement caching',
                        'priority': 'HIGH'
                    })
                elif metric_name == "content_seo_score":
                    recommendations['optimization_recommendations'].append({
                        'category': 'Content Quality',
                        'issue': 'Low content SEO scores',
                        'recommendation': 'Improve content templates, enhance SEO guidelines',
                        'priority': 'MEDIUM'
                    })
                elif metric_name == "page_speed_score":
                    recommendations['optimization_recommendations'].append({
                        'category': 'Technical',
                        'issue': 'Poor page speed performance',
                        'recommendation': 'Optimize images, implement CDN, minify resources',
                        'priority': 'HIGH'
                    })
        
        # Priority actions based on violations
        critical_violations = [a for a in self.alerts if a['level'] == 'CRITICAL']
        if critical_violations:
            recommendations['priority_actions'] = [
                f"Immediate attention required for {v['metric']}" 
                for v in critical_violations[-5:]
            ]
        
        return recommendations

# Global SEO performance SLA instance
seo_performance_sla = SEOPerformanceSLA()