"""User Support SLA Monitoring System
Enterprise-grade user support performance tracking for Creator Economy Platform

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
from enum import Enum
import json

class SupportChannelType(Enum):
    """Types of support channels"""
    EMAIL = "email"
    LIVE_CHAT = "live_chat"
    PHONE = "phone"
    TICKET_SYSTEM = "ticket_system"
    KNOWLEDGE_BASE = "knowledge_base"
    COMMUNITY_FORUM = "community_forum"
    VIDEO_CALL = "video_call"
    SOCIAL_MEDIA = "social_media"

class TicketPriority(Enum):
    """Support ticket priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TicketCategory(Enum):
    """Support ticket categories"""
    ACCOUNT_ISSUES = "account_issues"
    PAYMENT_BILLING = "payment_billing"
    CONTENT_UPLOAD = "content_upload"
    TECHNICAL_ISSUES = "technical_issues"
    FEATURE_REQUEST = "feature_request"
    COLLABORATION = "collaboration"
    COPYRIGHT_DMCA = "copyright_dmca"
    PLATFORM_BUG = "platform_bug"
    CREATOR_TOOLS = "creator_tools"
    API_INTEGRATION = "api_integration"

@dataclass
class SupportMetric:
    """User support metric definition"""
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
class SupportTarget:
    """User support performance targets for Creator Economy Platform"""
    # Core Support Performance Targets
    first_response_time_ms: float = 3600000.0  # <1h first response
    resolution_time_critical_ms: float = 86400000.0  # <24h critical resolution
    resolution_time_high_ms: float = 172800000.0  # <48h high priority resolution
    resolution_time_medium_ms: float = 259200000.0  # <72h medium priority resolution
    resolution_time_low_ms: float = 604800000.0  # <7 days low priority resolution
    
    # Support Quality Targets
    creator_satisfaction_score: float = 95.0  # >95% creator satisfaction
    first_contact_resolution_rate: float = 80.0  # 80% first contact resolution
    support_channel_availability: float = 99.9  # 99.9% channel availability (24/7)
    knowledge_base_accuracy: float = 95.0  # 95% KB accuracy
    support_agent_utilization: float = 85.0  # 85% agent utilization
    
    # Channel Performance Targets
    live_chat_response_time_ms: float = 30000.0  # <30s live chat response
    email_response_time_ms: float = 7200000.0  # <2h email response
    phone_answer_time_ms: float = 20000.0  # <20s phone answer
    ticket_creation_time_ms: float = 5000.0  # <5s ticket creation
    escalation_time_ms: float = 1800000.0  # <30min escalation time

class UserSupportSLA:
    """
    Enterprise User Support SLA Monitoring
    Tracks support performance and customer satisfaction for Creator Economy Platform
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.support_targets = SupportTarget()
        self.metrics: Dict[str, SupportMetric] = {}
        self.support_tickets: deque = deque(maxlen=50000)
        self.support_interactions: deque = deque(maxlen=100000)
        self.satisfaction_surveys: deque = deque(maxlen=10000)
        self.channel_metrics: Dict[str, deque] = {
            channel.value: deque(maxlen=10000) 
            for channel in SupportChannelType
        }
        self.alerts: List[Dict[str, Any]] = []
        self.monitoring_active = False
        
        # Initialize support performance metrics
        self._initialize_support_metrics()
        
    def _initialize_support_metrics(self):
        """Initialize user support metrics with targets"""
        self.metrics = {
            "first_response_time": SupportMetric(
                name="First Response Time",
                target_value=self.support_targets.first_response_time_ms,
                unit="ms",
                threshold_critical=7200000.0,  # 2x target (2h)
                threshold_warning=5400000.0,   # 1.5x target (1.5h)
                measurement_window_minutes=60
            ),
            "critical_resolution_time": SupportMetric(
                name="Critical Issue Resolution Time",
                target_value=self.support_targets.resolution_time_critical_ms,
                unit="ms",
                threshold_critical=172800000.0,  # 2x target (48h)
                threshold_warning=129600000.0,   # 1.5x target (36h)
                measurement_window_minutes=1440  # Daily
            ),
            "creator_satisfaction_score": SupportMetric(
                name="Creator Satisfaction Score",
                target_value=self.support_targets.creator_satisfaction_score,
                unit="%",
                threshold_critical=85.0,   # Below 85%
                threshold_warning=90.0,    # Below 90%
                measurement_window_minutes=1440  # Daily
            ),
            "first_contact_resolution_rate": SupportMetric(
                name="First Contact Resolution Rate",
                target_value=self.support_targets.first_contact_resolution_rate,
                unit="%",
                threshold_critical=60.0,   # Below 60%
                threshold_warning=70.0,    # Below 70%
                measurement_window_minutes=1440  # Daily
            ),
            "support_channel_availability": SupportMetric(
                name="Support Channel Availability",
                target_value=self.support_targets.support_channel_availability,
                unit="%",
                threshold_critical=99.0,   # Below 99%
                threshold_warning=99.5,    # Below 99.5%
                measurement_window_minutes=60
            ),
            "live_chat_response_time": SupportMetric(
                name="Live Chat Response Time",
                target_value=self.support_targets.live_chat_response_time_ms,
                unit="ms",
                threshold_critical=60000.0,   # 2x target (1min)
                threshold_warning=45000.0,    # 1.5x target (45s)
                measurement_window_minutes=15
            ),
            "email_response_time": SupportMetric(
                name="Email Response Time",
                target_value=self.support_targets.email_response_time_ms,
                unit="ms",
                threshold_critical=14400000.0,  # 2x target (4h)
                threshold_warning=10800000.0,   # 1.5x target (3h)
                measurement_window_minutes=240  # 4 hours
            ),
            "knowledge_base_accuracy": SupportMetric(
                name="Knowledge Base Accuracy",
                target_value=self.support_targets.knowledge_base_accuracy,
                unit="%",
                threshold_critical=85.0,   # Below 85%
                threshold_warning=90.0,    # Below 90%
                measurement_window_minutes=1440  # Daily
            ),
            "support_agent_utilization": SupportMetric(
                name="Support Agent Utilization",
                target_value=self.support_targets.support_agent_utilization,
                unit="%",
                threshold_critical=95.0,   # Above 95% (overloaded)
                threshold_warning=90.0,    # Above 90%
                measurement_window_minutes=480  # 8 hours
            )
        }
        
    async def record_support_ticket(self, ticket_id: str, priority: TicketPriority,
                                  category: TicketCategory, channel: SupportChannelType,
                                  creator_id: str, created_at: datetime):
        """Record new support ticket creation"""
        timestamp = datetime.now()
        
        # Record ticket
        ticket_data = {
            'timestamp': timestamp,
            'ticket_id': ticket_id,
            'priority': priority.value,
            'category': category.value,
            'channel': channel.value,
            'creator_id': creator_id,
            'created_at': created_at,
            'status': 'open',
            'first_response_time': None,
            'resolution_time': None
        }
        
        self.support_tickets.append(ticket_data)
        
        self.logger.info(f"Support ticket created: {ticket_id}, priority: {priority.value}")
        
    async def record_first_response(self, ticket_id: str, response_time_ms: float,
                                  agent_id: str, channel: SupportChannelType):
        """Record first response to support ticket"""
        timestamp = datetime.now()
        
        # Find and update ticket
        for ticket in reversed(self.support_tickets):
            if ticket['ticket_id'] == ticket_id:
                ticket['first_response_time'] = response_time_ms
                ticket['responding_agent'] = agent_id
                break
        
        # Record interaction
        self.support_interactions.append({
            'timestamp': timestamp,
            'ticket_id': ticket_id,
            'interaction_type': 'first_response',
            'channel': channel.value,
            'response_time': response_time_ms,
            'agent_id': agent_id
        })
        
        # Update channel-specific metrics
        self.channel_metrics[channel.value].append({
            'timestamp': timestamp,
            'response_time': response_time_ms,
            'type': 'first_response'
        })
        
        # Update metrics
        self.metrics["first_response_time"].current_value = response_time_ms
        self.metrics["first_response_time"].last_updated = timestamp
        
        if channel == SupportChannelType.LIVE_CHAT:
            self.metrics["live_chat_response_time"].current_value = response_time_ms
            self.metrics["live_chat_response_time"].last_updated = timestamp
        elif channel == SupportChannelType.EMAIL:
            self.metrics["email_response_time"].current_value = response_time_ms
            self.metrics["email_response_time"].last_updated = timestamp
        
        await self._check_sla_violations()
        
        self.logger.info(f"First response recorded: {ticket_id}, {response_time_ms}ms")
        
    async def record_ticket_resolution(self, ticket_id: str, resolution_time_ms: float,
                                     resolved_at_first_contact: bool, 
                                     resolution_type: str):
        """Record support ticket resolution"""
        timestamp = datetime.now()
        
        # Find and update ticket
        ticket_priority = None
        for ticket in reversed(self.support_tickets):
            if ticket['ticket_id'] == ticket_id:
                ticket['resolution_time'] = resolution_time_ms
                ticket['status'] = 'resolved'
                ticket['resolved_at_first_contact'] = resolved_at_first_contact
                ticket['resolution_type'] = resolution_type
                ticket_priority = ticket['priority']
                break
        
        # Record interaction
        self.support_interactions.append({
            'timestamp': timestamp,
            'ticket_id': ticket_id,
            'interaction_type': 'resolution',
            'resolution_time': resolution_time_ms,
            'first_contact_resolution': resolved_at_first_contact
        })
        
        # Update priority-specific resolution time metrics
        if ticket_priority == TicketPriority.CRITICAL.value:
            self.metrics["critical_resolution_time"].current_value = resolution_time_ms
            self.metrics["critical_resolution_time"].last_updated = timestamp
        
        # Update first contact resolution rate
        await self._update_first_contact_resolution_rate()
        
        await self._check_sla_violations()
        
        self.logger.info(f"Ticket resolved: {ticket_id}, {resolution_time_ms}ms")
        
    async def record_satisfaction_survey(self, ticket_id: str, creator_id: str,
                                       satisfaction_score: float, feedback: str,
                                       would_recommend: bool):
        """Record creator satisfaction survey"""
        timestamp = datetime.now()
        
        # Record satisfaction
        self.satisfaction_surveys.append({
            'timestamp': timestamp,
            'ticket_id': ticket_id,
            'creator_id': creator_id,
            'satisfaction_score': satisfaction_score,
            'feedback': feedback,
            'would_recommend': would_recommend
        })
        
        # Update satisfaction metrics
        await self._update_satisfaction_metrics()
        
        await self._check_sla_violations()
        
        self.logger.info(f"Satisfaction survey: {ticket_id}, score: {satisfaction_score}")
        
    async def record_channel_availability(self, channel: SupportChannelType,
                                        availability_percentage: float,
                                        downtime_minutes: float):
        """Record support channel availability"""
        timestamp = datetime.now()
        
        # Record channel performance
        self.channel_metrics[channel.value].append({
            'timestamp': timestamp,
            'availability': availability_percentage,
            'downtime_minutes': downtime_minutes,
            'type': 'availability'
        })
        
        # Update overall channel availability
        await self._update_channel_availability()
        
        await self._check_sla_violations()
        
    async def record_knowledge_base_interaction(self, article_id: str, creator_id: str,
                                              helpful: bool, search_query: str,
                                              time_spent_seconds: float):
        """Record knowledge base interaction for accuracy tracking"""
        timestamp = datetime.now()
        
        # Record KB interaction (would typically store in separate collection)
        kb_interaction = {
            'timestamp': timestamp,
            'article_id': article_id,
            'creator_id': creator_id,
            'helpful': helpful,
            'search_query': search_query,
            'time_spent': time_spent_seconds
        }
        
        # Update KB accuracy (simplified calculation)
        await self._update_knowledge_base_accuracy(helpful)
        
        await self._check_sla_violations()
        
    async def record_agent_utilization(self, agent_id: str, active_tickets: int,
                                     total_capacity: int, shift_hours: float):
        """Record support agent utilization metrics"""
        timestamp = datetime.now()
        
        utilization_percentage = (active_tickets / total_capacity * 100) if total_capacity > 0 else 0
        
        # Update agent utilization metric
        self.metrics["support_agent_utilization"].current_value = utilization_percentage
        self.metrics["support_agent_utilization"].last_updated = timestamp
        self.metrics["support_agent_utilization"].metadata = {
            'agent_id': agent_id,
            'active_tickets': active_tickets,
            'total_capacity': total_capacity,
            'shift_hours': shift_hours
        }
        
        await self._check_sla_violations()
        
    async def _update_first_contact_resolution_rate(self):
        """Update first contact resolution rate"""
        now = datetime.now()
        start_24h = now - timedelta(hours=24)
        
        # Get recent resolved tickets
        recent_resolved = [
            ticket for ticket in self.support_tickets
            if (ticket['status'] == 'resolved' and 
                ticket['timestamp'] >= start_24h and
                'resolved_at_first_contact' in ticket)
        ]
        
        if recent_resolved:
            first_contact_resolved = sum(
                1 for ticket in recent_resolved 
                if ticket['resolved_at_first_contact']
            )
            
            fcr_rate = (first_contact_resolved / len(recent_resolved)) * 100
            
            self.metrics["first_contact_resolution_rate"].current_value = fcr_rate
            self.metrics["first_contact_resolution_rate"].last_updated = now
        
    async def _update_satisfaction_metrics(self):
        """Update creator satisfaction metrics"""
        now = datetime.now()
        start_7d = now - timedelta(days=7)
        
        # Get recent satisfaction surveys
        recent_surveys = [
            survey for survey in self.satisfaction_surveys
            if survey['timestamp'] >= start_7d
        ]
        
        if recent_surveys:
            avg_satisfaction = statistics.mean([
                survey['satisfaction_score'] for survey in recent_surveys
            ])
            
            # Convert to percentage (assuming score is 1-10, convert to 0-100)
            satisfaction_percentage = (avg_satisfaction / 10) * 100
            
            self.metrics["creator_satisfaction_score"].current_value = satisfaction_percentage
            self.metrics["creator_satisfaction_score"].last_updated = now
        
    async def _update_channel_availability(self):
        """Update overall support channel availability"""
        now = datetime.now()
        start_24h = now - timedelta(hours=24)
        
        channel_availabilities = []
        
        for channel_type, metrics in self.channel_metrics.items():
            recent_metrics = [
                metric for metric in metrics
                if (metric['timestamp'] >= start_24h and 
                    metric.get('type') == 'availability')
            ]
            
            if recent_metrics:
                avg_availability = statistics.mean([
                    metric['availability'] for metric in recent_metrics
                ])
                channel_availabilities.append(avg_availability)
        
        if channel_availabilities:
            overall_availability = statistics.mean(channel_availabilities)
            
            self.metrics["support_channel_availability"].current_value = overall_availability
            self.metrics["support_channel_availability"].last_updated = now
        
    async def _update_knowledge_base_accuracy(self, helpful: bool):
        """Update knowledge base accuracy metric"""
        # This is a simplified implementation
        # In production, would track detailed KB analytics
        current_accuracy = self.metrics["knowledge_base_accuracy"].current_value
        
        # Simple weighted update (would be more sophisticated in production)
        if helpful:
            new_accuracy = min(current_accuracy + 0.1, 100.0)
        else:
            new_accuracy = max(current_accuracy - 0.5, 0.0)
        
        self.metrics["knowledge_base_accuracy"].current_value = new_accuracy
        self.metrics["knowledge_base_accuracy"].last_updated = datetime.now()
        
    async def _check_sla_violations(self):
        """Check for support SLA violations and generate alerts"""
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
                    'sla_type': 'USER_SUPPORT'
                })
            elif self._is_warning_violation(metric):
                violations.append({
                    'level': 'WARNING',
                    'metric': metric_name,
                    'current_value': metric.current_value,
                    'target_value': metric.target_value,
                    'threshold': metric.threshold_warning,
                    'timestamp': datetime.now(),
                    'sla_type': 'USER_SUPPORT'
                })
                
        # Process violations
        for violation in violations:
            await self._process_sla_violation(violation)
            
    def _is_critical_violation(self, metric: SupportMetric) -> bool:
        """Check if metric is in critical violation"""
        time_metrics = [
            "First Response Time", "Critical Issue Resolution Time", 
            "Live Chat Response Time", "Email Response Time"
        ]
        
        rate_metrics = [
            "Creator Satisfaction Score", "First Contact Resolution Rate",
            "Support Channel Availability", "Knowledge Base Accuracy"
        ]
        
        utilization_metrics = [
            "Support Agent Utilization"
        ]
        
        if metric.name in time_metrics:
            return metric.current_value > metric.threshold_critical
        elif metric.name in rate_metrics:
            return metric.current_value < metric.threshold_critical
        elif metric.name in utilization_metrics:
            return metric.current_value > metric.threshold_critical  # High utilization is bad
        
        return False
        
    def _is_warning_violation(self, metric: SupportMetric) -> bool:
        """Check if metric is in warning state"""
        time_metrics = [
            "First Response Time", "Critical Issue Resolution Time", 
            "Live Chat Response Time", "Email Response Time"
        ]
        
        rate_metrics = [
            "Creator Satisfaction Score", "First Contact Resolution Rate",
            "Support Channel Availability", "Knowledge Base Accuracy"
        ]
        
        utilization_metrics = [
            "Support Agent Utilization"
        ]
        
        if metric.name in time_metrics:
            return metric.current_value > metric.threshold_warning
        elif metric.name in rate_metrics:
            return metric.current_value < metric.threshold_warning
        elif metric.name in utilization_metrics:
            return metric.current_value > metric.threshold_warning  # High utilization is bad
        
        return False
        
    async def _process_sla_violation(self, violation: Dict[str, Any]):
        """Process support SLA violation and generate alert"""
        self.alerts.append(violation)
        
        self.logger.error(
            f"Support SLA {violation['level']} VIOLATION: {violation['metric']} = "
            f"{violation['current_value']:.2f} (target: {violation['target_value']:.2f})"
        )
        
        # TODO: Integrate with alerting systems (Slack, PagerDuty, email)
        
    async def get_support_sla_status(self) -> Dict[str, Any]:
        """Get current support SLA status and compliance"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'sla_type': 'USER_SUPPORT',
            'overall_compliance': True,
            'metrics': {},
            'violations': len([a for a in self.alerts if a['level'] == 'CRITICAL']),
            'warnings': len([a for a in self.alerts if a['level'] == 'WARNING']),
            'support_summary': {
                'open_tickets': len([
                    t for t in self.support_tickets 
                    if t['status'] == 'open'
                ]),
                'tickets_today': len([
                    t for t in self.support_tickets
                    if t['timestamp'].date() == datetime.now().date()
                ]),
                'avg_satisfaction_score': statistics.mean([
                    s['satisfaction_score'] for s in list(self.satisfaction_surveys)[-50:]
                ]) if self.satisfaction_surveys else 0,
                'total_interactions_24h': len([
                    i for i in self.support_interactions
                    if i['timestamp'] >= datetime.now() - timedelta(hours=24)
                ])
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
        
    async def get_support_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive support performance report"""
        now = datetime.now()
        
        # Calculate statistics for last 7 days
        start_7d = now - timedelta(days=7)
        
        recent_tickets = [
            t for t in self.support_tickets
            if t['timestamp'] >= start_7d
        ]
        
        recent_interactions = [
            i for i in self.support_interactions
            if i['timestamp'] >= start_7d
        ]
        
        recent_surveys = [
            s for s in self.satisfaction_surveys
            if s['timestamp'] >= start_7d
        ]
        
        report = {
            'report_timestamp': now.isoformat(),
            'period': '7_days',
            'support_performance_summary': {
                'ticket_metrics': {
                    'total_tickets': len(recent_tickets),
                    'resolved_tickets': len([t for t in recent_tickets if t['status'] == 'resolved']),
                    'avg_first_response_time': statistics.mean([
                        t['first_response_time'] for t in recent_tickets 
                        if t['first_response_time'] is not None
                    ]) if recent_tickets else 0,
                    'avg_resolution_time': statistics.mean([
                        t['resolution_time'] for t in recent_tickets 
                        if t['resolution_time'] is not None
                    ]) if recent_tickets else 0,
                    'priority_distribution': self._get_priority_distribution(recent_tickets),
                    'category_distribution': self._get_category_distribution(recent_tickets)
                },
                'channel_performance': self._get_channel_performance_summary(start_7d),
                'satisfaction_metrics': {
                    'total_surveys': len(recent_surveys),
                    'avg_satisfaction_score': statistics.mean([
                        s['satisfaction_score'] for s in recent_surveys
                    ]) if recent_surveys else 0,
                    'recommendation_rate': (sum(1 for s in recent_surveys if s['would_recommend']) / len(recent_surveys) * 100) if recent_surveys else 0
                },
                'agent_performance': {
                    'total_interactions': len(recent_interactions),
                    'unique_agents': len(set([
                        i.get('agent_id') for i in recent_interactions 
                        if i.get('agent_id')
                    ])),
                    'avg_agent_utilization': self.metrics["support_agent_utilization"].current_value
                }
            },
            'sla_compliance': await self.get_support_sla_status(),
            'support_insights': await self._generate_support_insights(recent_tickets, recent_surveys)
        }
        
        return report
        
    def _get_priority_distribution(self, tickets: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of ticket priorities"""
        distribution = defaultdict(int)
        for ticket in tickets:
            distribution[ticket['priority']] += 1
        return dict(distribution)
        
    def _get_category_distribution(self, tickets: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of ticket categories"""
        distribution = defaultdict(int)
        for ticket in tickets:
            distribution[ticket['category']] += 1
        return dict(distribution)
        
    def _get_channel_performance_summary(self, start_date: datetime) -> Dict[str, Any]:
        """Get channel performance summary"""
        channel_summary = {}
        
        for channel_type, metrics in self.channel_metrics.items():
            recent_metrics = [
                metric for metric in metrics
                if metric['timestamp'] >= start_date
            ]
            
            if recent_metrics:
                response_times = [
                    metric['response_time'] for metric in recent_metrics 
                    if 'response_time' in metric
                ]
                
                availabilities = [
                    metric['availability'] for metric in recent_metrics 
                    if 'availability' in metric
                ]
                
                channel_summary[channel_type] = {
                    'total_interactions': len(recent_metrics),
                    'avg_response_time': statistics.mean(response_times) if response_times else 0,
                    'avg_availability': statistics.mean(availabilities) if availabilities else 100
                }
        
        return channel_summary
        
    async def _generate_support_insights(self, tickets: List[Dict[str, Any]], 
                                       surveys: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate support insights from recent data"""
        insights = {
            'performance_trends': {},
            'common_issues': [],
            'improvement_opportunities': []
        }
        
        if tickets:
            # Performance trends
            resolved_tickets = [t for t in tickets if t['status'] == 'resolved']
            if len(resolved_tickets) > 1:
                recent_resolution_times = [t['resolution_time'] for t in resolved_tickets[-10:] if t['resolution_time']]
                earlier_resolution_times = [t['resolution_time'] for t in resolved_tickets[:-10] if t['resolution_time']]
                
                if recent_resolution_times and earlier_resolution_times:
                    recent_avg = statistics.mean(recent_resolution_times)
                    earlier_avg = statistics.mean(earlier_resolution_times)
                    
                    insights['performance_trends']['resolution_time_trend'] = (
                        'improving' if recent_avg < earlier_avg else 'stable'
                    )
            
            # Common issues
            category_counts = defaultdict(int)
            for ticket in tickets:
                category_counts[ticket['category']] += 1
            
            sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
            insights['common_issues'] = [cat[0] for cat in sorted_categories[:5]]
        
        if surveys:
            # Satisfaction trend
            if len(surveys) > 1:
                recent_satisfaction = statistics.mean([s['satisfaction_score'] for s in surveys[-10:]])
                earlier_satisfaction = statistics.mean([s['satisfaction_score'] for s in surveys[:-10]])
                
                insights['performance_trends']['satisfaction_trend'] = (
                    'improving' if recent_satisfaction > earlier_satisfaction else 'stable'
                )
        
        # Improvement opportunities
        current_status = await self.get_support_sla_status()
        for metric_name, metric_data in current_status['metrics'].items():
            if not metric_data['compliance']:
                insights['improvement_opportunities'].append({
                    'metric': metric_name,
                    'current_performance': metric_data['current_value'],
                    'target': metric_data['target_value'],
                    'gap': abs(metric_data['current_value'] - metric_data['target_value'])
                })
        
        return insights
        
    async def optimize_support_performance(self) -> Dict[str, Any]:
        """Generate support performance optimization recommendations"""
        recommendations = {
            'timestamp': datetime.now().isoformat(),
            'optimization_recommendations': [],
            'priority_actions': [],
            'support_insights': {}
        }
        
        # Analyze current performance
        current_status = await self.get_support_sla_status()
        
        for metric_name, metric_data in current_status['metrics'].items():
            if not metric_data['compliance']:
                if metric_name == "first_response_time":
                    recommendations['optimization_recommendations'].append({
                        'category': 'Response Time',
                        'issue': 'First response time exceeding target',
                        'recommendation': 'Implement auto-responses, optimize agent routing',
                        'priority': 'HIGH'
                    })
                elif metric_name == "creator_satisfaction_score":
                    recommendations['optimization_recommendations'].append({
                        'category': 'Satisfaction',
                        'issue': 'Low creator satisfaction scores',
                        'recommendation': 'Enhance agent training, improve resolution quality',
                        'priority': 'CRITICAL'
                    })
                elif metric_name == "support_agent_utilization":
                    recommendations['optimization_recommendations'].append({
                        'category': 'Resource Management',
                        'issue': 'High agent utilization indicating overload',
                        'recommendation': 'Hire additional agents, implement workload balancing',
                        'priority': 'HIGH'
                    })
        
        # Support insights
        recommendations['support_insights'] = {
            'busiest_support_channels': self._analyze_channel_usage(),
            'peak_support_hours': self._analyze_support_patterns(),
            'most_challenging_categories': self._analyze_resolution_difficulty()
        }
        
        return recommendations
        
    def _analyze_channel_usage(self) -> List[str]:
        """Analyze which support channels are used most"""
        channel_usage = defaultdict(int)
        
        for ticket in self.support_tickets:
            channel_usage[ticket['channel']] += 1
        
        sorted_channels = sorted(channel_usage.items(), key=lambda x: x[1], reverse=True)
        return [c[0] for c in sorted_channels[:3]]
        
    def _analyze_support_patterns(self) -> List[int]:
        """Analyze peak support hours"""
        hourly_tickets = defaultdict(int)
        
        for ticket in self.support_tickets:
            hourly_tickets[ticket['timestamp'].hour] += 1
        
        sorted_hours = sorted(hourly_tickets.items(), key=lambda x: x[1], reverse=True)
        return [h[0] for h in sorted_hours[:3]]
        
    def _analyze_resolution_difficulty(self) -> List[str]:
        """Analyze which categories take longest to resolve"""
        category_resolution_times = defaultdict(list)
        
        for ticket in self.support_tickets:
            if ticket['status'] == 'resolved' and ticket['resolution_time']:
                category_resolution_times[ticket['category']].append(ticket['resolution_time'])
        
        category_avg_times = {
            category: statistics.mean(times) 
            for category, times in category_resolution_times.items()
        }
        
        sorted_categories = sorted(category_avg_times.items(), key=lambda x: x[1], reverse=True)
        return [c[0] for c in sorted_categories[:3]]

# Global user support SLA instance
user_support_sla = UserSupportSLA()