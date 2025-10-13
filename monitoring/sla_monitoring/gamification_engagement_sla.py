"""Gamification Engagement SLA Monitoring System
Enterprise-grade gamification and engagement tracking for Creator Economy Platform

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
import math

class AchievementType(Enum):
    """Types of achievements in gamification system"""
    CONTENT_CREATION = "content_creation"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    COLLABORATION = "collaboration"
    QUALITY = "quality"
    CONSISTENCY = "consistency"
    INNOVATION = "innovation"
    COMMUNITY = "community"

class RewardType(Enum):
    """Types of rewards in the system"""
    POINTS = "points"
    BADGE = "badge"
    LEVEL = "level"
    ACHIEVEMENT = "achievement"
    PREMIUM_FEATURE = "premium_feature"
    MONETARY = "monetary"
    RECOGNITION = "recognition"

@dataclass
class GamificationMetric:
    """Gamification engagement metric definition"""
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
class GamificationTarget:
    """Gamification engagement targets for Creator Economy Platform"""
    # Core Performance Targets
    achievement_processing_time_ms: float = 1000.0  # <1s achievement processing
    leaderboard_update_time_ms: float = 5000.0  # <5s leaderboard update
    reward_distribution_time_ms: float = 10000.0  # <10s reward distribution
    engagement_calculation_time_ms: float = 30000.0  # <30s engagement calculation
    system_uptime_percentage: float = 99.99  # 99.99% uptime
    
    # Engagement Targets
    daily_active_users_percentage: float = 65.0  # 65% DAU target
    user_retention_7day_percentage: float = 70.0  # 70% 7-day retention
    user_retention_30day_percentage: float = 40.0  # 40% 30-day retention
    average_session_duration_minutes: float = 25.0  # 25min average session
    user_engagement_score: float = 8.0  # 8/10 engagement score
    
    # Gamification Targets
    achievement_completion_rate: float = 80.0  # 80% achievement completion
    reward_redemption_rate: float = 90.0  # 90% reward redemption
    leaderboard_participation_rate: float = 60.0  # 60% leaderboard participation
    social_interaction_rate: float = 50.0  # 50% social interaction
    content_quality_improvement: float = 25.0  # 25% quality improvement

class GamificationEngagementSLA:
    """
    Enterprise Gamification Engagement SLA Monitoring
    Tracks gamification metrics and user engagement for Creator Economy Platform
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.gamification_targets = GamificationTarget()
        self.metrics: Dict[str, GamificationMetric] = {}
        self.achievement_processing_times: deque = deque(maxlen=10000)
        self.leaderboard_updates: deque = deque(maxlen=5000)
        self.reward_distributions: deque = deque(maxlen=5000)
        self.engagement_calculations: deque = deque(maxlen=1000)
        self.user_activities: deque = deque(maxlen=50000)
        self.gamification_events: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []
        self.monitoring_active = False
        
        # Initialize gamification engagement metrics
        self._initialize_gamification_metrics()
        
    def _initialize_gamification_metrics(self):
        """Initialize gamification engagement metrics with targets"""
        self.metrics = {
            "achievement_processing_time": GamificationMetric(
                name="Achievement Processing Time",
                target_value=self.gamification_targets.achievement_processing_time_ms,
                unit="ms",
                threshold_critical=2000.0,  # 2x target
                threshold_warning=1500.0,   # 1.5x target
                measurement_window_minutes=5
            ),
            "leaderboard_update_time": GamificationMetric(
                name="Leaderboard Update Time",
                target_value=self.gamification_targets.leaderboard_update_time_ms,
                unit="ms",
                threshold_critical=10000.0,  # 2x target
                threshold_warning=7500.0,    # 1.5x target
                measurement_window_minutes=10
            ),
            "reward_distribution_time": GamificationMetric(
                name="Reward Distribution Time",
                target_value=self.gamification_targets.reward_distribution_time_ms,
                unit="ms",
                threshold_critical=20000.0,  # 2x target
                threshold_warning=15000.0,   # 1.5x target
                measurement_window_minutes=15
            ),
            "engagement_calculation_time": GamificationMetric(
                name="Engagement Calculation Time",
                target_value=self.gamification_targets.engagement_calculation_time_ms,
                unit="ms",
                threshold_critical=60000.0,  # 2x target (1min)
                threshold_warning=45000.0,   # 1.5x target (45s)
                measurement_window_minutes=30
            ),
            "system_uptime": GamificationMetric(
                name="Gamification System Uptime",
                target_value=self.gamification_targets.system_uptime_percentage,
                unit="%",
                threshold_critical=99.9,   # Below 99.9%
                threshold_warning=99.95,   # Below 99.95%
                measurement_window_minutes=60
            ),
            "daily_active_users": GamificationMetric(
                name="Daily Active Users",
                target_value=self.gamification_targets.daily_active_users_percentage,
                unit="%",
                threshold_critical=50.0,   # Below 50%
                threshold_warning=60.0,    # Below 60%
                measurement_window_minutes=1440  # Daily
            ),
            "user_retention_7day": GamificationMetric(
                name="7-Day User Retention",
                target_value=self.gamification_targets.user_retention_7day_percentage,
                unit="%",
                threshold_critical=50.0,   # Below 50%
                threshold_warning=65.0,    # Below 65%
                measurement_window_minutes=10080  # Weekly
            ),
            "user_engagement_score": GamificationMetric(
                name="User Engagement Score",
                target_value=self.gamification_targets.user_engagement_score,
                unit="score",
                threshold_critical=6.0,    # Below 6/10
                threshold_warning=7.5,     # Below 7.5/10
                measurement_window_minutes=60
            ),
            "achievement_completion_rate": GamificationMetric(
                name="Achievement Completion Rate",
                target_value=self.gamification_targets.achievement_completion_rate,
                unit="%",
                threshold_critical=60.0,   # Below 60%
                threshold_warning=75.0,    # Below 75%
                measurement_window_minutes=1440  # Daily
            )
        }
        
    async def record_achievement_processing(self, processing_time_ms: float, 
                                          achievement_type: AchievementType,
                                          user_id: str, success: bool = True):
        """Record achievement processing performance"""
        timestamp = datetime.now()
        
        # Record processing time
        self.achievement_processing_times.append({
            'timestamp': timestamp,
            'processing_time': processing_time_ms,
            'achievement_type': achievement_type.value,
            'user_id': user_id,
            'success': success
        })
        
        # Update metrics
        self.metrics["achievement_processing_time"].current_value = processing_time_ms
        self.metrics["achievement_processing_time"].last_updated = timestamp
        
        # Check SLA violations
        await self._check_sla_violations()
        
        self.logger.info(f"Achievement processing: {processing_time_ms}ms, type: {achievement_type.value}")
        
    async def record_leaderboard_update(self, update_time_ms: float, 
                                      leaderboard_type: str, affected_users: int):
        """Record leaderboard update performance"""
        timestamp = datetime.now()
        
        # Record update performance
        self.leaderboard_updates.append({
            'timestamp': timestamp,
            'update_time': update_time_ms,
            'leaderboard_type': leaderboard_type,
            'affected_users': affected_users
        })
        
        # Update metrics
        self.metrics["leaderboard_update_time"].current_value = update_time_ms
        self.metrics["leaderboard_update_time"].last_updated = timestamp
        
        await self._check_sla_violations()
        
        self.logger.info(f"Leaderboard update: {update_time_ms}ms, {affected_users} users")
        
    async def record_reward_distribution(self, distribution_time_ms: float,
                                       reward_type: RewardType, recipients: int,
                                       total_value: float):
        """Record reward distribution performance"""
        timestamp = datetime.now()
        
        # Record distribution performance
        self.reward_distributions.append({
            'timestamp': timestamp,
            'distribution_time': distribution_time_ms,
            'reward_type': reward_type.value,
            'recipients': recipients,
            'total_value': total_value
        })
        
        # Update metrics
        self.metrics["reward_distribution_time"].current_value = distribution_time_ms
        self.metrics["reward_distribution_time"].last_updated = timestamp
        
        await self._check_sla_violations()
        
        self.logger.info(f"Reward distribution: {distribution_time_ms}ms, {recipients} recipients")
        
    async def record_engagement_calculation(self, calculation_time_ms: float,
                                          users_processed: int, 
                                          average_engagement_score: float):
        """Record engagement calculation performance"""
        timestamp = datetime.now()
        
        # Record calculation performance
        self.engagement_calculations.append({
            'timestamp': timestamp,
            'calculation_time': calculation_time_ms,
            'users_processed': users_processed,
            'average_engagement_score': average_engagement_score
        })
        
        # Update metrics
        self.metrics["engagement_calculation_time"].current_value = calculation_time_ms
        self.metrics["engagement_calculation_time"].last_updated = timestamp
        
        self.metrics["user_engagement_score"].current_value = average_engagement_score
        self.metrics["user_engagement_score"].last_updated = timestamp
        
        await self._check_sla_violations()
        
        self.logger.info(f"Engagement calculation: {calculation_time_ms}ms, score: {average_engagement_score}")
        
    async def record_user_activity(self, user_id: str, activity_type: str,
                                 session_duration_minutes: float, 
                                 engagement_actions: int):
        """Record user activity for engagement tracking"""
        timestamp = datetime.now()
        
        # Record user activity
        self.user_activities.append({
            'timestamp': timestamp,
            'user_id': user_id,
            'activity_type': activity_type,
            'session_duration': session_duration_minutes,
            'engagement_actions': engagement_actions
        })
        
        # Update daily active users metric
        await self._update_daily_active_users()
        
        # Update user retention metrics
        await self._update_retention_metrics()
        
        await self._check_sla_violations()
        
    async def record_achievement_completion(self, user_id: str, achievement_id: str,
                                          completion_time: datetime, 
                                          difficulty_level: int):
        """Record achievement completion for completion rate tracking"""
        timestamp = datetime.now()
        
        completion_data = {
            'timestamp': timestamp,
            'user_id': user_id,
            'achievement_id': achievement_id,
            'completion_time': completion_time,
            'difficulty_level': difficulty_level
        }
        
        self.gamification_events.append(completion_data)
        
        # Update achievement completion rate
        await self._update_achievement_completion_rate()
        
        await self._check_sla_violations()
        
    async def _update_daily_active_users(self):
        """Update daily active users metric"""
        now = datetime.now()
        start_24h = now - timedelta(hours=24)
        
        # Count unique users in last 24 hours
        recent_activities = [
            activity for activity in self.user_activities
            if activity['timestamp'] >= start_24h
        ]
        
        unique_users_24h = len(set(activity['user_id'] for activity in recent_activities))
        
        # Estimate total registered users (would come from user service in real implementation)
        estimated_total_users = max(unique_users_24h * 2, 1000)  # Rough estimate
        
        dau_percentage = (unique_users_24h / estimated_total_users) * 100
        
        self.metrics["daily_active_users"].current_value = dau_percentage
        self.metrics["daily_active_users"].last_updated = now
        
    async def _update_retention_metrics(self):
        """Update user retention metrics"""
        now = datetime.now()
        start_7d = now - timedelta(days=7)
        start_14d = now - timedelta(days=14)
        
        # Get users from 7-14 days ago (cohort)
        cohort_users = set(
            activity['user_id'] for activity in self.user_activities
            if start_14d <= activity['timestamp'] < start_7d
        )
        
        # Get users from last 7 days
        recent_users = set(
            activity['user_id'] for activity in self.user_activities
            if activity['timestamp'] >= start_7d
        )
        
        # Calculate 7-day retention
        if cohort_users:
            retained_users = cohort_users.intersection(recent_users)
            retention_7d = (len(retained_users) / len(cohort_users)) * 100
            
            self.metrics["user_retention_7day"].current_value = retention_7d
            self.metrics["user_retention_7day"].last_updated = now
        
    async def _update_achievement_completion_rate(self):
        """Update achievement completion rate"""
        now = datetime.now()
        start_24h = now - timedelta(hours=24)
        
        # Count recent achievement attempts vs completions
        recent_events = [
            event for event in self.gamification_events
            if event['timestamp'] >= start_24h
        ]
        
        if recent_events:
            # In real implementation, would track attempts vs completions
            completion_rate = len(recent_events) * 5  # Simulated rate
            completion_rate = min(completion_rate, 100.0)
            
            self.metrics["achievement_completion_rate"].current_value = completion_rate
            self.metrics["achievement_completion_rate"].last_updated = now
        
    async def _check_sla_violations(self):
        """Check for gamification SLA violations and generate alerts"""
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
                    'sla_type': 'GAMIFICATION_ENGAGEMENT'
                })
            elif self._is_warning_violation(metric):
                violations.append({
                    'level': 'WARNING',
                    'metric': metric_name,
                    'current_value': metric.current_value,
                    'target_value': metric.target_value,
                    'threshold': metric.threshold_warning,
                    'timestamp': datetime.now(),
                    'sla_type': 'GAMIFICATION_ENGAGEMENT'
                })
                
        # Process violations
        for violation in violations:
            await self._process_sla_violation(violation)
            
    def _is_critical_violation(self, metric: GamificationMetric) -> bool:
        """Check if metric is in critical violation"""
        performance_metrics = [
            "Achievement Processing Time", "Leaderboard Update Time",
            "Reward Distribution Time", "Engagement Calculation Time"
        ]
        
        if metric.name in performance_metrics:
            return metric.current_value > metric.threshold_critical
        else:
            # For percentage and score metrics, below threshold is violation
            return metric.current_value < metric.threshold_critical
        
    def _is_warning_violation(self, metric: GamificationMetric) -> bool:
        """Check if metric is in warning state"""
        performance_metrics = [
            "Achievement Processing Time", "Leaderboard Update Time",
            "Reward Distribution Time", "Engagement Calculation Time"
        ]
        
        if metric.name in performance_metrics:
            return metric.current_value > metric.threshold_warning
        else:
            # For percentage and score metrics, below threshold is violation
            return metric.current_value < metric.threshold_warning
        
    async def _process_sla_violation(self, violation: Dict[str, Any]):
        """Process gamification SLA violation and generate alert"""
        self.alerts.append(violation)
        
        self.logger.error(
            f"Gamification SLA {violation['level']} VIOLATION: {violation['metric']} = "
            f"{violation['current_value']:.2f} (target: {violation['target_value']:.2f})"
        )
        
        # TODO: Integrate with alerting systems (Slack, PagerDuty, email)
        
    async def get_gamification_sla_status(self) -> Dict[str, Any]:
        """Get current gamification SLA status and compliance"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'sla_type': 'GAMIFICATION_ENGAGEMENT',
            'overall_compliance': True,
            'metrics': {},
            'violations': len([a for a in self.alerts if a['level'] == 'CRITICAL']),
            'warnings': len([a for a in self.alerts if a['level'] == 'WARNING']),
            'engagement_summary': {
                'total_users_today': len(set(
                    activity['user_id'] for activity in list(self.user_activities)[-1000:]
                )),
                'avg_session_duration': statistics.mean([
                    activity['session_duration'] for activity in list(self.user_activities)[-100:]
                ]) if self.user_activities else 0,
                'total_achievements_processed': len(self.achievement_processing_times),
                'total_rewards_distributed': len(self.reward_distributions)
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
        
    async def get_gamification_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive gamification performance report"""
        now = datetime.now()
        
        # Calculate statistics for last 24 hours
        start_24h = now - timedelta(hours=24)
        
        recent_achievements = [
            a for a in self.achievement_processing_times
            if a['timestamp'] >= start_24h
        ]
        
        recent_rewards = [
            r for r in self.reward_distributions
            if r['timestamp'] >= start_24h
        ]
        
        recent_activities = [
            a for a in self.user_activities
            if a['timestamp'] >= start_24h
        ]
        
        report = {
            'report_timestamp': now.isoformat(),
            'period': '24_hours',
            'gamification_performance_summary': {
                'achievement_processing': {
                    'total_processed': len(recent_achievements),
                    'avg_processing_time': statistics.mean([a['processing_time'] for a in recent_achievements]) if recent_achievements else 0,
                    'success_rate': (sum(1 for a in recent_achievements if a['success']) / len(recent_achievements) * 100) if recent_achievements else 0,
                    'max_processing_time': max([a['processing_time'] for a in recent_achievements]) if recent_achievements else 0
                },
                'reward_distribution': {
                    'total_distributions': len(recent_rewards),
                    'avg_distribution_time': statistics.mean([r['distribution_time'] for r in recent_rewards]) if recent_rewards else 0,
                    'total_recipients': sum([r['recipients'] for r in recent_rewards]),
                    'total_value_distributed': sum([r['total_value'] for r in recent_rewards])
                },
                'user_engagement': {
                    'unique_active_users': len(set(a['user_id'] for a in recent_activities)),
                    'avg_session_duration': statistics.mean([a['session_duration'] for a in recent_activities]) if recent_activities else 0,
                    'total_engagement_actions': sum([a['engagement_actions'] for a in recent_activities]),
                    'avg_actions_per_user': statistics.mean([a['engagement_actions'] for a in recent_activities]) if recent_activities else 0
                }
            },
            'sla_compliance': await self.get_gamification_sla_status(),
            'engagement_trends': {
                'achievement_types_distribution': self._get_achievement_type_distribution(recent_achievements),
                'reward_types_distribution': self._get_reward_type_distribution(recent_rewards),
                'activity_patterns': self._get_activity_patterns(recent_activities)
            }
        }
        
        return report
        
    def _get_achievement_type_distribution(self, achievements: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of achievement types"""
        distribution = defaultdict(int)
        for achievement in achievements:
            distribution[achievement['achievement_type']] += 1
        return dict(distribution)
        
    def _get_reward_type_distribution(self, rewards: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of reward types"""
        distribution = defaultdict(int)
        for reward in rewards:
            distribution[reward['reward_type']] += 1
        return dict(distribution)
        
    def _get_activity_patterns(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user activity patterns"""
        if not activities:
            return {}
            
        hourly_distribution = defaultdict(int)
        for activity in activities:
            hour = activity['timestamp'].hour
            hourly_distribution[hour] += 1
            
        return {
            'hourly_distribution': dict(hourly_distribution),
            'peak_activity_hour': max(hourly_distribution, key=hourly_distribution.get) if hourly_distribution else 0,
            'activity_spread': len(hourly_distribution)
        }
        
    async def optimize_gamification_performance(self) -> Dict[str, Any]:
        """Generate gamification performance optimization recommendations"""
        recommendations = {
            'timestamp': datetime.now().isoformat(),
            'optimization_recommendations': [],
            'priority_actions': [],
            'engagement_insights': {}
        }
        
        # Analyze current performance
        current_status = await self.get_gamification_sla_status()
        
        for metric_name, metric_data in current_status['metrics'].items():
            if not metric_data['compliance']:
                if metric_name == "achievement_processing_time":
                    recommendations['optimization_recommendations'].append({
                        'category': 'Performance',
                        'issue': 'Achievement processing taking too long',
                        'recommendation': 'Optimize achievement algorithms, implement background processing',
                        'priority': 'HIGH'
                    })
                elif metric_name == "daily_active_users":
                    recommendations['optimization_recommendations'].append({
                        'category': 'Engagement',
                        'issue': 'Low daily active user percentage',
                        'recommendation': 'Enhance onboarding, add more engaging features',
                        'priority': 'CRITICAL'
                    })
                elif metric_name == "user_engagement_score":
                    recommendations['optimization_recommendations'].append({
                        'category': 'User Experience',
                        'issue': 'Low user engagement scores',
                        'recommendation': 'Redesign gamification mechanics, add social features',
                        'priority': 'HIGH'
                    })
        
        # Add engagement insights
        recommendations['engagement_insights'] = {
            'most_effective_achievement_types': self._analyze_achievement_effectiveness(),
            'optimal_reward_distribution_times': self._analyze_reward_timing(),
            'user_activity_patterns': self._analyze_user_patterns()
        }
        
        return recommendations
        
    def _analyze_achievement_effectiveness(self) -> List[str]:
        """Analyze which achievement types are most effective"""
        if not self.achievement_processing_times:
            return []
            
        type_performance = defaultdict(list)
        for achievement in self.achievement_processing_times:
            if achievement['success']:
                type_performance[achievement['achievement_type']].append(achievement['processing_time'])
        
        # Rank by average processing time (faster = more effective)
        ranked_types = sorted(
            type_performance.items(),
            key=lambda x: statistics.mean(x[1])
        )
        
        return [t[0] for t in ranked_types[:3]]  # Top 3
        
    def _analyze_reward_timing(self) -> List[int]:
        """Analyze optimal times for reward distribution"""
        if not self.reward_distributions:
            return []
            
        hourly_success = defaultdict(list)
        for reward in self.reward_distributions:
            hour = reward['timestamp'].hour
            # Faster distribution = better timing
            hourly_success[hour].append(1 / max(reward['distribution_time'], 1))
        
        # Rank hours by average success rate
        ranked_hours = sorted(
            hourly_success.items(),
            key=lambda x: statistics.mean(x[1]),
            reverse=True
        )
        
        return [h[0] for h in ranked_hours[:3]]  # Top 3 hours
        
    def _analyze_user_patterns(self) -> Dict[str, Any]:
        """Analyze user activity patterns for optimization"""
        if not self.user_activities:
            return {}
            
        pattern_analysis = {
            'avg_session_duration': statistics.mean([a['session_duration'] for a in self.user_activities]),
            'peak_activity_hours': [],
            'high_engagement_activities': []
        }
        
        # Find peak activity hours
        hourly_activity = defaultdict(int)
        for activity in self.user_activities:
            hourly_activity[activity['timestamp'].hour] += 1
            
        sorted_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)
        pattern_analysis['peak_activity_hours'] = [h[0] for h in sorted_hours[:3]]
        
        # Find high engagement activities
        activity_engagement = defaultdict(list)
        for activity in self.user_activities:
            activity_engagement[activity['activity_type']].append(activity['engagement_actions'])
            
        for activity_type, actions in activity_engagement.items():
            if statistics.mean(actions) > 5:  # High engagement threshold
                pattern_analysis['high_engagement_activities'].append(activity_type)
        
        return pattern_analysis

# Global gamification engagement SLA instance
gamification_engagement_sla = GamificationEngagementSLA()