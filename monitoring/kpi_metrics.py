"""Industrial KPI Metrics System
==================================

Comprehensive KPI tracking system for technical and business metrics
aligned with industrialization success targets.

Technical KPIs:
- Uptime SLA (99.9% target)
- API Response Time (<200ms P95 target)
- Error Rate (<0.1% target)
- MTTR (<15 minutes target)
- Deployment Frequency (>10/day target)
- Security Score (A+ 95%+ target)
- Code Coverage (>90% target)
- Technical Debt Ratio (<5% target)

Business KPIs:
- Time to Market (<1 day target)
- Customer Satisfaction (>4.5/5 target)
- Cost per Transaction (<€0.10 target)
- Revenue Growth (+20% MoM target)
- User Retention (>85% target)
- Support Ticket Volume (<100/day target)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import json
import logging
import psutil
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, Info
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

logger = logging.getLogger(__name__)


class KPICategory(Enum):
    """KPI Categories"""
    TECHNICAL = "technical"
    BUSINESS = "business"


class KPIStatus(Enum):
    """KPI Status relative to targets"""
    EXCELLENT = "excellent"  # Exceeding target
    GOOD = "good"           # Meeting target
    WARNING = "warning"     # Close to missing target
    CRITICAL = "critical"   # Missing target


@dataclass
class KPITarget:
    """KPI Target definition"""
    name: str
    category: KPICategory
    target_value: float
    comparison: str  # ">=", "<=", "==", ">"", "<"
    unit: str
    description: str
    warning_threshold: float  # Threshold for warning status
    critical_threshold: float  # Threshold for critical status


@dataclass
class KPIMetric:
    """KPI Metric data point"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    status: KPIStatus
    target: KPITarget
    metadata: Dict[str, Any] = field(default_factory=dict)


class TechnicalKPICollector:
    """Technical KPI metrics collector"""
    
    def __init__(self, prometheus_collector=None):
        self.prometheus = prometheus_collector
        self.logger = logging.getLogger(__name__)
        self.start_time = time.time()
        self.downtime_start = None
        self.total_downtime = 0
        self.total_requests = 0
        self.error_requests = 0
        self.response_times = []
        self.deployments_today = 0
        self.incidents = []
        self.last_deployment = None
        
        # Define technical KPI targets
        self.targets = {
            "uptime_sla": KPITarget(
                name="uptime_sla",
                category=KPICategory.TECHNICAL,
                target_value=99.9,
                comparison=">=",
                unit="%",
                description="System uptime SLA",
                warning_threshold=99.5,
                critical_threshold=99.0
            ),
            "api_response_time_p95": KPITarget(
                name="api_response_time_p95",
                category=KPICategory.TECHNICAL,
                target_value=200,
                comparison="<=",
                unit="ms",
                description="API Response Time P95",
                warning_threshold=180,
                critical_threshold=200
            ),
            "error_rate": KPITarget(
                name="error_rate",
                category=KPICategory.TECHNICAL,
                target_value=0.1,
                comparison="<=",
                unit="%",
                description="System error rate",
                warning_threshold=0.08,
                critical_threshold=0.1
            ),
            "mttr": KPITarget(
                name="mttr",
                category=KPICategory.TECHNICAL,
                target_value=15,
                comparison="<=",
                unit="minutes",
                description="Mean Time to Repair",
                warning_threshold=12,
                critical_threshold=15
            ),
            "deployment_frequency": KPITarget(
                name="deployment_frequency",
                category=KPICategory.TECHNICAL,
                target_value=10,
                comparison=">=",
                unit="deployments/day",
                description="Daily deployment frequency",
                warning_threshold=8,
                critical_threshold=10
            ),
            "security_score": KPITarget(
                name="security_score",
                category=KPICategory.TECHNICAL,
                target_value=95,
                comparison=">=",
                unit="%",
                description="Security compliance score",
                warning_threshold=90,
                critical_threshold=95
            ),
            "code_coverage": KPITarget(
                name="code_coverage",
                category=KPICategory.TECHNICAL,
                target_value=90,
                comparison=">=",
                unit="%",
                description="Code test coverage",
                warning_threshold=85,
                critical_threshold=90
            ),
            "technical_debt_ratio": KPITarget(
                name="technical_debt_ratio",
                category=KPICategory.TECHNICAL,
                target_value=5,
                comparison="<=",
                unit="%",
                description="Technical debt ratio",
                warning_threshold=4,
                critical_threshold=5
            )
        }
        
        self._initialize_prometheus_metrics()
    
    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics for technical KPIs"""
        if not HAS_PROMETHEUS or not self.prometheus:
            return
        
        try:
            # Register KPI gauges with Prometheus
            for target_name, target in self.targets.items():
                if not hasattr(self.prometheus, f'kpi_{target_name}'):
                    setattr(self.prometheus, f'kpi_{target_name}', 
                           Gauge(f'kpi_{target_name}', target.description))
                    setattr(self.prometheus, f'kpi_{target_name}_status',
                           Info(f'kpi_{target_name}_status', f'{target.description} status'))
        except Exception as e:
            self.logger.error(f"Failed to initialize Prometheus metrics: {str(e)}")
    
    def record_request(self, response_time_ms: float, status_code: int):
        """Record API request metrics"""
        self.total_requests += 1
        self.response_times.append(response_time_ms)
        
        if status_code >= 400:
            self.error_requests += 1
        
        # Keep only last 1000 response times for P95 calculation
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def record_incident(self, incident_start: datetime, incident_end: datetime):
        """Record system incident"""
        duration = (incident_end - incident_start).total_seconds() / 60  # minutes
        self.incidents.append({
            'start': incident_start,
            'end': incident_end,
            'duration_minutes': duration
        })
    
    def record_deployment(self):
        """Record a deployment"""
        self.deployments_today += 1
        self.last_deployment = datetime.utcnow()
    
    def record_downtime_start(self):
        """Record start of downtime"""
        if self.downtime_start is None:
            self.downtime_start = time.time()
    
    def record_downtime_end(self):
        """Record end of downtime"""
        if self.downtime_start is not None:
            self.total_downtime += time.time() - self.downtime_start
            self.downtime_start = None
    
    def calculate_uptime_sla(self) -> float:
        """Calculate current uptime SLA percentage"""
        total_time = time.time() - self.start_time
        current_downtime = self.total_downtime
        
        # Add current downtime if system is currently down
        if self.downtime_start is not None:
            current_downtime += time.time() - self.downtime_start
        
        if total_time == 0:
            return 100.0
        
        uptime_percentage = ((total_time - current_downtime) / total_time) * 100
        return round(uptime_percentage, 3)
    
    def calculate_response_time_p95(self) -> float:
        """Calculate P95 response time"""
        if not self.response_times:
            return 0.0
        
        sorted_times = sorted(self.response_times)
        p95_index = int(len(sorted_times) * 0.95)
        return sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
    
    def calculate_error_rate(self) -> float:
        """Calculate error rate percentage"""
        if self.total_requests == 0:
            return 0.0
        
        return (self.error_requests / self.total_requests) * 100
    
    def calculate_mttr(self) -> float:
        """Calculate Mean Time to Repair"""
        if not self.incidents:
            return 0.0
        
        total_duration = sum(incident['duration_minutes'] for incident in self.incidents)
        return total_duration / len(self.incidents)
    
    def get_security_score(self) -> float:
        """Get security compliance score (placeholder implementation)"""
        # This would integrate with actual security scanning tools
        # For now, return a mock score based on system health
        base_score = 95.0
        
        # Reduce score based on error rate
        error_rate = self.calculate_error_rate()
        if error_rate > 0.1:
            base_score -= min(error_rate * 10, 20)
        
        return max(base_score, 0.0)
    
    def get_code_coverage(self) -> float:
        """Get code coverage percentage (placeholder implementation)"""
        # This would integrate with actual code coverage tools
        # For now, return a mock coverage based on system stability
        base_coverage = 92.0
        
        # Adjust based on error rate
        error_rate = self.calculate_error_rate()
        if error_rate > 0.1:
            base_coverage -= min(error_rate * 50, 10)
        
        return max(base_coverage, 0.0)
    
    def get_technical_debt_ratio(self) -> float:
        """Get technical debt ratio (placeholder implementation)"""
        # This would integrate with actual code quality tools
        # For now, return a mock ratio based on system metrics
        base_debt = 3.5
        
        # Increase debt based on MTTR
        mttr = self.calculate_mttr()
        if mttr > 15:
            base_debt += min((mttr - 15) * 0.1, 2)
        
        return min(base_debt, 10.0)
    
    def _determine_status(self, value: float, target: KPITarget) -> KPIStatus:
        """Determine KPI status based on value and target"""
        if target.comparison in [">=", ">"]:
            if value >= target.target_value:
                return KPIStatus.EXCELLENT
            elif value >= target.warning_threshold:
                return KPIStatus.GOOD
            elif value >= target.critical_threshold:
                return KPIStatus.WARNING
            else:
                return KPIStatus.CRITICAL
        else:  # "<=", "<"
            if value <= target.target_value:
                return KPIStatus.EXCELLENT
            elif value <= target.warning_threshold:
                return KPIStatus.GOOD
            elif value <= target.critical_threshold:
                return KPIStatus.WARNING
            else:
                return KPIStatus.CRITICAL
    
    async def collect_all_metrics(self) -> List[KPIMetric]:
        """Collect all technical KPI metrics"""
        metrics = []
        timestamp = datetime.utcnow()
        
        # Uptime SLA
        uptime = self.calculate_uptime_sla()
        metrics.append(KPIMetric(
            name="uptime_sla",
            value=uptime,
            unit="%",
            timestamp=timestamp,
            status=self._determine_status(uptime, self.targets["uptime_sla"]),
            target=self.targets["uptime_sla"]
        ))
        
        # API Response Time P95
        response_time = self.calculate_response_time_p95()
        metrics.append(KPIMetric(
            name="api_response_time_p95",
            value=response_time,
            unit="ms",
            timestamp=timestamp,
            status=self._determine_status(response_time, self.targets["api_response_time_p95"]),
            target=self.targets["api_response_time_p95"]
        ))
        
        # Error Rate
        error_rate = self.calculate_error_rate()
        metrics.append(KPIMetric(
            name="error_rate",
            value=error_rate,
            unit="%",
            timestamp=timestamp,
            status=self._determine_status(error_rate, self.targets["error_rate"]),
            target=self.targets["error_rate"]
        ))
        
        # MTTR
        mttr = self.calculate_mttr()
        metrics.append(KPIMetric(
            name="mttr",
            value=mttr,
            unit="minutes",
            timestamp=timestamp,
            status=self._determine_status(mttr, self.targets["mttr"]),
            target=self.targets["mttr"]
        ))
        
        # Deployment Frequency
        metrics.append(KPIMetric(
            name="deployment_frequency",
            value=self.deployments_today,
            unit="deployments/day",
            timestamp=timestamp,
            status=self._determine_status(self.deployments_today, self.targets["deployment_frequency"]),
            target=self.targets["deployment_frequency"]
        ))
        
        # Security Score
        security_score = self.get_security_score()
        metrics.append(KPIMetric(
            name="security_score",
            value=security_score,
            unit="%",
            timestamp=timestamp,
            status=self._determine_status(security_score, self.targets["security_score"]),
            target=self.targets["security_score"]
        ))
        
        # Code Coverage
        code_coverage = self.get_code_coverage()
        metrics.append(KPIMetric(
            name="code_coverage",
            value=code_coverage,
            unit="%",
            timestamp=timestamp,
            status=self._determine_status(code_coverage, self.targets["code_coverage"]),
            target=self.targets["code_coverage"]
        ))
        
        # Technical Debt Ratio
        tech_debt = self.get_technical_debt_ratio()
        metrics.append(KPIMetric(
            name="technical_debt_ratio",
            value=tech_debt,
            unit="%",
            timestamp=timestamp,
            status=self._determine_status(tech_debt, self.targets["technical_debt_ratio"]),
            target=self.targets["technical_debt_ratio"]
        ))
        
        # Update Prometheus metrics
        await self._update_prometheus_metrics(metrics)
        
        return metrics
    
    async def _update_prometheus_metrics(self, metrics: List[KPIMetric]):
        """Update Prometheus metrics"""
        if not HAS_PROMETHEUS or not self.prometheus:
            return
        
        try:
            for metric in metrics:
                # Update gauge value
                gauge = getattr(self.prometheus, f'kpi_{metric.name}', None)
                if gauge:
                    gauge.set(metric.value)
                
                # Update status info
                status_info = getattr(self.prometheus, f'kpi_{metric.name}_status', None)
                if status_info:
                    status_info.info({
                        'status': metric.status.value,
                        'target': str(metric.target.target_value),
                        'unit': metric.unit
                    })
        except Exception as e:
            self.logger.error(f"Failed to update Prometheus metrics: {str(e)}")


class BusinessKPICollector:
    """Business KPI metrics collector"""
    
    def __init__(self, prometheus_collector=None):
        self.prometheus = prometheus_collector
        self.logger = logging.getLogger(__name__)
        self.feature_deployments = []
        self.customer_ratings = []
        self.transactions = []
        self.revenue_history = []
        self.user_cohorts = {}
        self.support_tickets_today = 0
        
        # Define business KPI targets
        self.targets = {
            "time_to_market": KPITarget(
                name="time_to_market",
                category=KPICategory.BUSINESS,
                target_value=1,
                comparison="<=",
                unit="days",
                description="Feature time to market",
                warning_threshold=0.8,
                critical_threshold=1.0
            ),
            "customer_satisfaction": KPITarget(
                name="customer_satisfaction",
                category=KPICategory.BUSINESS,
                target_value=4.5,
                comparison=">=",
                unit="rating",
                description="Customer satisfaction score",
                warning_threshold=4.2,
                critical_threshold=4.5
            ),
            "cost_per_transaction": KPITarget(
                name="cost_per_transaction",
                category=KPICategory.BUSINESS,
                target_value=0.10,
                comparison="<=",
                unit="€",
                description="Cost per transaction",
                warning_threshold=0.08,
                critical_threshold=0.10
            ),
            "revenue_growth": KPITarget(
                name="revenue_growth",
                category=KPICategory.BUSINESS,
                target_value=20,
                comparison=">=",
                unit="% MoM",
                description="Monthly revenue growth",
                warning_threshold=15,
                critical_threshold=20
            ),
            "user_retention": KPITarget(
                name="user_retention",
                category=KPICategory.BUSINESS,
                target_value=85,
                comparison=">=",
                unit="%",
                description="User retention rate",
                warning_threshold=80,
                critical_threshold=85
            ),
            "support_ticket_volume": KPITarget(
                name="support_ticket_volume",
                category=KPICategory.BUSINESS,
                target_value=100,
                comparison="<=",
                unit="tickets/day",
                description="Daily support ticket volume",
                warning_threshold=80,
                critical_threshold=100
            )
        }
        
        self._initialize_prometheus_metrics()
    
    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics for business KPIs"""
        if not HAS_PROMETHEUS or not self.prometheus:
            return
        
        try:
            for target_name, target in self.targets.items():
                if not hasattr(self.prometheus, f'kpi_{target_name}'):
                    setattr(self.prometheus, f'kpi_{target_name}', 
                           Gauge(f'kpi_{target_name}', target.description))
                    setattr(self.prometheus, f'kpi_{target_name}_status',
                           Info(f'kpi_{target_name}_status', f'{target.description} status'))
        except Exception as e:
            self.logger.error(f"Failed to initialize Prometheus metrics: {str(e)}")
    
    def record_feature_deployment(self, feature_name: str, start_time: datetime, end_time: datetime):
        """Record feature deployment time"""
        duration_days = (end_time - start_time).total_seconds() / (24 * 3600)
        self.feature_deployments.append({
            'feature': feature_name,
            'duration_days': duration_days,
            'deployed_at': end_time
        })
    
    def record_customer_rating(self, rating: float):
        """Record customer satisfaction rating"""
        self.customer_ratings.append({
            'rating': rating,
            'timestamp': datetime.utcnow()
        })
        
        # Keep only last 100 ratings for calculation
        if len(self.customer_ratings) > 100:
            self.customer_ratings = self.customer_ratings[-100:]
    
    def record_transaction(self, transaction_cost: float, revenue: float):
        """Record transaction data"""
        self.transactions.append({
            'cost': transaction_cost,
            'revenue': revenue,
            'timestamp': datetime.utcnow()
        })
    
    def record_revenue(self, amount: float, period: str = "monthly"):
        """Record revenue data"""
        self.revenue_history.append({
            'amount': amount,
            'period': period,
            'timestamp': datetime.utcnow()
        })
    
    def record_user_activity(self, user_id: str, activity_date: datetime):
        """Record user activity for retention calculation"""
        if user_id not in self.user_cohorts:
            self.user_cohorts[user_id] = {'first_seen': activity_date, 'last_seen': activity_date}
        else:
            self.user_cohorts[user_id]['last_seen'] = activity_date
    
    def record_support_ticket(self):
        """Record support ticket"""
        self.support_tickets_today += 1
    
    def calculate_time_to_market(self) -> float:
        """Calculate average time to market"""
        if not self.feature_deployments:
            return 0.0
        
        recent_deployments = [d for d in self.feature_deployments 
                            if (datetime.utcnow() - d['deployed_at']).days <= 30]
        
        if not recent_deployments:
            return 0.0
        
        total_duration = sum(d['duration_days'] for d in recent_deployments)
        return total_duration / len(recent_deployments)
    
    def calculate_customer_satisfaction(self) -> float:
        """Calculate average customer satisfaction"""
        if not self.customer_ratings:
            return 0.0
        
        total_rating = sum(r['rating'] for r in self.customer_ratings)
        return total_rating / len(self.customer_ratings)
    
    def calculate_cost_per_transaction(self) -> float:
        """Calculate average cost per transaction"""
        if not self.transactions:
            return 0.0
        
        total_cost = sum(t['cost'] for t in self.transactions)
        return total_cost / len(self.transactions)
    
    def calculate_revenue_growth(self) -> float:
        """Calculate month-over-month revenue growth"""
        if len(self.revenue_history) < 2:
            return 0.0
        
        # Get last two months of revenue
        sorted_revenue = sorted(self.revenue_history, key=lambda x: x['timestamp'])
        current_month = sorted_revenue[-1]['amount']
        previous_month = sorted_revenue[-2]['amount'] if len(sorted_revenue) > 1 else current_month
        
        if previous_month == 0:
            return 0.0
        
        growth = ((current_month - previous_month) / previous_month) * 100
        return growth
    
    def calculate_user_retention(self) -> float:
        """Calculate user retention rate"""
        if not self.user_cohorts:
            return 0.0
        
        now = datetime.utcnow()
        thirty_days_ago = now - timedelta(days=30)
        
        # Users who were active in the last 30 days
        active_users = [user_id for user_id, data in self.user_cohorts.items()
                       if data['last_seen'] >= thirty_days_ago]
        
        # Users who joined more than 30 days ago
        cohort_users = [user_id for user_id, data in self.user_cohorts.items()
                       if data['first_seen'] <= thirty_days_ago]
        
        if not cohort_users:
            return 0.0
        
        # Retention = active users from cohort / total cohort users
        retained_users = [user_id for user_id in active_users if user_id in cohort_users]
        return (len(retained_users) / len(cohort_users)) * 100
    
    def _determine_status(self, value: float, target: KPITarget) -> KPIStatus:
        """Determine KPI status based on value and target"""
        if target.comparison in [">=", ">"]:
            if value >= target.target_value:
                return KPIStatus.EXCELLENT
            elif value >= target.warning_threshold:
                return KPIStatus.GOOD
            elif value >= target.critical_threshold:
                return KPIStatus.WARNING
            else:
                return KPIStatus.CRITICAL
        else:  # "<=", "<"
            if value <= target.target_value:
                return KPIStatus.EXCELLENT
            elif value <= target.warning_threshold:
                return KPIStatus.GOOD
            elif value <= target.critical_threshold:
                return KPIStatus.WARNING
            else:
                return KPIStatus.CRITICAL
    
    async def collect_all_metrics(self) -> List[KPIMetric]:
        """Collect all business KPI metrics"""
        metrics = []
        timestamp = datetime.utcnow()
        
        # Time to Market
        ttm = self.calculate_time_to_market()
        metrics.append(KPIMetric(
            name="time_to_market",
            value=ttm,
            unit="days",
            timestamp=timestamp,
            status=self._determine_status(ttm, self.targets["time_to_market"]),
            target=self.targets["time_to_market"]
        ))
        
        # Customer Satisfaction
        satisfaction = self.calculate_customer_satisfaction()
        metrics.append(KPIMetric(
            name="customer_satisfaction",
            value=satisfaction,
            unit="rating",
            timestamp=timestamp,
            status=self._determine_status(satisfaction, self.targets["customer_satisfaction"]),
            target=self.targets["customer_satisfaction"]
        ))
        
        # Cost per Transaction
        cost_per_tx = self.calculate_cost_per_transaction()
        metrics.append(KPIMetric(
            name="cost_per_transaction",
            value=cost_per_tx,
            unit="€",
            timestamp=timestamp,
            status=self._determine_status(cost_per_tx, self.targets["cost_per_transaction"]),
            target=self.targets["cost_per_transaction"]
        ))
        
        # Revenue Growth
        revenue_growth = self.calculate_revenue_growth()
        metrics.append(KPIMetric(
            name="revenue_growth",
            value=revenue_growth,
            unit="% MoM",
            timestamp=timestamp,
            status=self._determine_status(revenue_growth, self.targets["revenue_growth"]),
            target=self.targets["revenue_growth"]
        ))
        
        # User Retention
        retention = self.calculate_user_retention()
        metrics.append(KPIMetric(
            name="user_retention",
            value=retention,
            unit="%",
            timestamp=timestamp,
            status=self._determine_status(retention, self.targets["user_retention"]),
            target=self.targets["user_retention"]
        ))
        
        # Support Ticket Volume
        metrics.append(KPIMetric(
            name="support_ticket_volume",
            value=self.support_tickets_today,
            unit="tickets/day",
            timestamp=timestamp,
            status=self._determine_status(self.support_tickets_today, self.targets["support_ticket_volume"]),
            target=self.targets["support_ticket_volume"]
        ))
        
        # Update Prometheus metrics
        await self._update_prometheus_metrics(metrics)
        
        return metrics
    
    async def _update_prometheus_metrics(self, metrics: List[KPIMetric]):
        """Update Prometheus metrics"""
        if not HAS_PROMETHEUS or not self.prometheus:
            return
        
        try:
            for metric in metrics:
                # Update gauge value
                gauge = getattr(self.prometheus, f'kpi_{metric.name}', None)
                if gauge:
                    gauge.set(metric.value)
                
                # Update status info
                status_info = getattr(self.prometheus, f'kpi_{metric.name}_status', None)
                if status_info:
                    status_info.info({
                        'status': metric.status.value,
                        'target': str(metric.target.target_value),
                        'unit': metric.unit
                    })
        except Exception as e:
            self.logger.error(f"Failed to update Prometheus metrics: {str(e)}")


class IndustrialKPISystem:
    """Comprehensive KPI system for industrialization metrics"""
    
    def __init__(self, prometheus_collector=None):
        self.technical_kpis = TechnicalKPICollector(prometheus_collector)
        self.business_kpis = BusinessKPICollector(prometheus_collector)
        self.logger = logging.getLogger(__name__)
        self.alerts_enabled = True
        self.alert_handlers = []
    
    def register_alert_handler(self, handler):
        """Register alert handler for KPI violations"""
        self.alert_handlers.append(handler)
    
    async def collect_all_kpis(self) -> Dict[str, List[KPIMetric]]:
        """Collect all KPIs from both technical and business collectors"""
        try:
            technical_metrics = await self.technical_kpis.collect_all_metrics()
            business_metrics = await self.business_kpis.collect_all_metrics()
            
            results = {
                'technical': technical_metrics,
                'business': business_metrics,
                'timestamp': datetime.utcnow().isoformat(),
                'summary': self._generate_summary(technical_metrics + business_metrics)
            }
            
            # Check for alerts
            if self.alerts_enabled:
                await self._check_kpi_alerts(technical_metrics + business_metrics)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to collect KPIs: {str(e)}")
            return {'technical': [], 'business': [], 'error': str(e)}
    
    def _generate_summary(self, all_metrics: List[KPIMetric]) -> Dict[str, Any]:
        """Generate KPI summary"""
        status_counts = {status.value: 0 for status in KPIStatus}
        category_counts = {category.value: 0 for category in KPICategory}
        
        for metric in all_metrics:
            status_counts[metric.status.value] += 1
            category_counts[metric.target.category.value] += 1
        
        # Calculate overall health score
        total_metrics = len(all_metrics)
        if total_metrics == 0:
            health_score = 0
        else:
            score = (
                status_counts['excellent'] * 100 +
                status_counts['good'] * 80 +
                status_counts['warning'] * 60 +
                status_counts['critical'] * 30
            ) / total_metrics
            health_score = round(score, 1)
        
        return {
            'total_kpis': total_metrics,
            'status_distribution': status_counts,
            'category_distribution': category_counts,
            'health_score': health_score,
            'health_grade': self._get_health_grade(health_score)
        }
    
    def _get_health_grade(self, score: float) -> str:
        """Get health grade based on score"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"
    
    async def _check_kpi_alerts(self, metrics: List[KPIMetric]):
        """Check for KPI alert conditions"""
        for metric in metrics:
            if metric.status in [KPIStatus.WARNING, KPIStatus.CRITICAL]:
                alert_data = {
                    'kpi_name': metric.name,
                    'current_value': metric.value,
                    'target_value': metric.target.target_value,
                    'status': metric.status.value,
                    'unit': metric.unit,
                    'category': metric.target.category.value,
                    'timestamp': metric.timestamp.isoformat()
                }
                
                for handler in self.alert_handlers:
                    try:
                        await handler(alert_data)
                    except Exception as e:
                        self.logger.error(f"Alert handler failed: {str(e)}")
    
    def get_kpi_dashboard_data(self) -> Dict[str, Any]:
        """Get formatted data for KPI dashboard"""
        return {
            'technical_targets': self.technical_kpis.targets,
            'business_targets': self.business_kpis.targets,
            'system_info': {
                'start_time': self.technical_kpis.start_time,
                'total_requests': self.technical_kpis.total_requests,
                'deployments_today': self.technical_kpis.deployments_today,
                'support_tickets_today': self.business_kpis.support_tickets_today
            }
        }


# Global KPI system instance
kpi_system = None


async def initialize_kpi_system(prometheus_collector=None) -> IndustrialKPISystem:
    """Initialize global KPI system"""
    global kpi_system
    
    if kpi_system is None:
        kpi_system = IndustrialKPISystem(prometheus_collector)
        logging.info("Industrial KPI system initialized")
    
    return kpi_system


def get_kpi_system() -> Optional[IndustrialKPISystem]:
    """Get global KPI system instance"""
    return kpi_system


# Convenience functions for recording metrics
async def record_api_request(response_time_ms: float, status_code: int):
    """Record API request for KPI tracking"""
    if kpi_system:
        kpi_system.technical_kpis.record_request(response_time_ms, status_code)


async def record_deployment():
    """Record deployment for KPI tracking"""
    if kpi_system:
        kpi_system.technical_kpis.record_deployment()


async def record_customer_feedback(rating: float):
    """Record customer feedback for KPI tracking"""
    if kpi_system:
        kpi_system.business_kpis.record_customer_rating(rating)


async def record_feature_deployment(feature_name: str, start_time: datetime, end_time: datetime):
    """Record feature deployment for time-to-market KPI"""
    if kpi_system:
        kpi_system.business_kpis.record_feature_deployment(feature_name, start_time, end_time)


async def record_support_ticket():
    """Record support ticket for KPI tracking"""
    if kpi_system:
        kpi_system.business_kpis.record_support_ticket()