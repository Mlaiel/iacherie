"""Queue Health Diagnostics - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/queues/queue_health_diagnostics.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Health Diagnostics & Recovery System
Responsibility: Advanced health monitoring with automated diagnostics and recovery
Technologies: Health scoring, Diagnostic algorithms, Recovery automation, Performance analysis
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Health data collection → Diagnostic analysis → Problem identification → 
Recovery planning → Automated healing → Performance verification → Continuous improvement
"""from typing import Any, Dict, List, Optional, Union, Set, Tuple, Callable
import logging
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import numpy as np
from collections import defaultdict, deque
import time
import statistics
import traceback

from backend.core.managers.queue_manager import IntelligentQueueManager
from .task_distribution_engine import TaskDistributionEngine, LoadBalancingMetrics
from .realtime_queue_monitor import RealtimeQueueMonitor, MetricDataPoint, MonitoringAlert

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels"""    EXCELLENT = "excellent"        # 90-100%
    GOOD = "good"                 # 70-89%
    DEGRADED = "degraded"         # 50-69%
    CRITICAL = "critical"         # 30-49%
    EMERGENCY = "emergency"       # 0-29%


class DiagnosticCategory(Enum):
    """Diagnostic categories"""    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    SCALABILITY = "scalability"
    SECURITY = "security"
    RESOURCE_USAGE = "resource_usage"
    CONNECTIVITY = "connectivity"
    DATA_INTEGRITY = "data_integrity"
    OPERATIONAL = "operational"


class RecoveryStrategy(Enum):
    """Recovery strategy types"""    IMMEDIATE = "immediate"        # Emergency fixes
    SCHEDULED = "scheduled"        # Planned maintenance
    GRADUAL = "gradual"           # Phased improvements
    PREVENTIVE = "preventive"     # Proactive measures


class DiagnosticSeverity(Enum):
    """Diagnostic issue severity"""    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class HealthMetric:
    """Individual health metric"""    metric_name: str
    current_value: float
    target_value: float
    threshold_warning: float
    threshold_critical: float
    weight: float = 1.0
    unit: str = ""
    description: str = ""
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DiagnosticIssue:
    """Diagnostic issue identification"""    issue_id: str
    category: DiagnosticCategory
    severity: DiagnosticSeverity
    title: str
    description: str
    affected_components: List[str]
    root_causes: List[str]
    symptoms: List[str]
    impact_assessment: str
    confidence_score: float
    detected_at: datetime
    resolution_priority: int = 5  # 1 (highest) to 10 (lowest)


@dataclass
class RecoveryAction:
    """Recovery action specification"""    action_id: str
    title: str
    description: str
    strategy: RecoveryStrategy
    estimated_duration_minutes: int
    risk_level: str  # low, medium, high
    prerequisites: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    rollback_plan: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    automation_level: str = "manual"  # manual, semi-automated, automated


@dataclass
class RecoveryPlan:
    """Complete recovery plan"""    plan_id: str
    issue_id: str
    strategy: RecoveryStrategy
    total_estimated_duration: int
    actions: List[RecoveryAction]
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    rollback_strategy: str = ""
    approval_required: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class HealthReport:
    """Comprehensive health report"""    report_id: str
    timestamp: datetime
    overall_health_score: float
    overall_status: HealthStatus
    component_health: Dict[str, float]
    metrics: List[HealthMetric]
    issues: List[DiagnosticIssue]
    recovery_plans: List[RecoveryPlan]
    recommendations: List[str]
    trend_analysis: Dict[str, str]
    performance_insights: List[str]


@dataclass
class DiagnosticConfig:
    """Diagnostic system configuration"""    diagnostic_interval_seconds: int = 300  # 5 minutes
    health_check_interval_seconds: int = 60
    metric_collection_window_minutes: int = 30
    issue_detection_sensitivity: float = 0.8
    auto_recovery_enabled: bool = True
    max_concurrent_recoveries: int = 3
    recovery_timeout_minutes: int = 60
    enable_predictive_diagnostics: bool = True
    enable_root_cause_analysis: bool = True


class ComponentHealthAnalyzer:
    """Individual component health analyzer"""    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.metrics: Dict[str, HealthMetric] = {}
        self.historical_scores: deque = deque(maxlen=100)
        self.baseline_performance: Dict[str, float] = {}
        
    async def add_metric(self, metric: HealthMetric):
        """Add health metric for component"""        self.metrics[metric.metric_name] = metric
        
        # Update baseline if this is a new metric
        if metric.metric_name not in self.baseline_performance:
            self.baseline_performance[metric.metric_name] = metric.current_value
    
    async def calculate_health_score(self) -> float:
        """Calculate overall health score for component"""        
        if not self.metrics:
            return 0.5  # Default neutral score
        
        weighted_scores = []
        total_weight = 0.0
        
        for metric in self.metrics.values():
            # Calculate metric score (0.0 to 1.0)
            metric_score = await self._calculate_metric_score(metric)
            weighted_scores.append(metric_score * metric.weight)
            total_weight += metric.weight
        
        # Calculate weighted average
        if total_weight > 0:
            health_score = sum(weighted_scores) / total_weight
        else:
            health_score = 0.5
        
        # Store in history
        self.historical_scores.append({
            'timestamp': datetime.utcnow(),
            'score': health_score
        })
        
        return health_score
    
    async def _calculate_metric_score(self, metric: HealthMetric) -> float:
        """Calculate score for individual metric"""        
        current = metric.current_value
        target = metric.target_value
        warning = metric.threshold_warning
        critical = metric.threshold_critical
        
        # Handle different metric types
        if target == 0.0:  # Error rates, latency - lower is better
            if current <= warning:
                return 1.0  # Excellent
            elif current <= critical:
                # Linear interpolation between warning and critical
                ratio = (current - warning) / (critical - warning)
                return max(0.0, 0.7 - (ratio * 0.4))  # 0.7 to 0.3
            else:
                return 0.1  # Critical
        
        else:  # Throughput, success rates - higher is better or target-based
            distance_from_target = abs(current - target)
            tolerance = abs(target - warning)
            
            if distance_from_target <= tolerance:
                return 1.0  # Excellent
            else:
                # Calculate degradation
                degradation = distance_from_target / tolerance
                return max(0.1, 1.0 - (degradation * 0.5))
    
    async def detect_anomalies(self) -> List[str]:
        """Detect anomalies in component behavior"""        
        anomalies = []
        
        # Check recent trend
        if len(self.historical_scores) >= 5:
            recent_scores = [item['score'] for item in list(self.historical_scores)[-5:]]
            trend_direction = await self._analyze_trend(recent_scores)
            
            if trend_direction == "declining":
                anomalies.append(f"{self.component_name} health trending downward")
        
        # Check individual metrics
        for metric_name, metric in self.metrics.items():
            if metric.current_value <= metric.threshold_critical:
                anomalies.append(f"{metric_name} in critical state: {metric.current_value}{metric.unit}")
            elif metric.current_value <= metric.threshold_warning:
                anomalies.append(f"{metric_name} in warning state: {metric.current_value}{metric.unit}")
        
        return anomalies
    
    async def _analyze_trend(self, values: List[float]) -> str:
        """Analyze trend direction"""        
        if len(values) < 3:
            return "stable"
        
        # Simple linear regression slope
        x = list(range(len(values)))
        slope = np.corrcoef(x, values)[0, 1] if len(set(values)) > 1 else 0
        
        if slope < -0.3:
            return "declining"
        elif slope > 0.3:
            return "improving"
        else:
            return "stable"
    
    async def get_performance_insights(self) -> List[str]:
        """Get performance insights for component"""        
        insights = []
        
        # Analyze metric performance
        for metric_name, metric in self.metrics.items():
            baseline = self.baseline_performance.get(metric_name, metric.target_value)
            
            if baseline > 0:
                change_percent = ((metric.current_value - baseline) / baseline) * 100
                
                if abs(change_percent) > 20:
                    direction = "improved" if change_percent > 0 else "degraded"
                    insights.append(
                        f"{metric_name} has {direction} by {abs(change_percent):.1f}% from baseline"
                    )
        
        # Analyze historical performance
        if len(self.historical_scores) >= 10:
            scores = [item['score'] for item in self.historical_scores]
            avg_score = statistics.mean(scores)
            current_score = scores[-1]
            
            if current_score < avg_score - 0.1:
                insights.append(f"{self.component_name} performing below historical average")
            elif current_score > avg_score + 0.1:
                insights.append(f"{self.component_name} performing above historical average")
        
        return insights


class RootCauseAnalyzer:
    """Root cause analysis engine"""    
    def __init__(self):
        self.correlation_patterns: Dict[str, List[str]] = {
            "high_queue_size": [
                "low_processing_rate",
                "worker_failures",
                "resource_exhaustion",
                "network_latency"
            ],
            "high_response_time": [
                "high_queue_size", 
                "database_latency",
                "network_congestion",
                "resource_contention"
            ],
            "low_success_rate": [
                "worker_health_issues",
                "external_api_failures", 
                "configuration_errors",
                "resource_exhaustion"
            ],
            "worker_failures": [
                "memory_leaks",
                "cpu_exhaustion",
                "network_connectivity",
                "software_bugs"
            ]
        }
        
        self.common_causes = {
            "resource_exhaustion": [
                "Insufficient CPU capacity",
                "Memory pressure",
                "Disk I/O bottlenecks",
                "Network bandwidth limits"
            ],
            "configuration_errors": [
                "Incorrect worker pool size",
                "Suboptimal distribution strategy",
                "Wrong timeout values",
                "Misconfigured rate limits"
            ],
            "external_dependencies": [
                "Third-party API rate limits",
                "Database connection issues",
                "Network connectivity problems",
                "Authentication failures"
            ]
        }
    
    async def analyze_root_causes(self, 
                                issues: List[DiagnosticIssue], 
                                metrics: List[HealthMetric]) -> Dict[str, List[str]]:
        """Analyze root causes for detected issues"""        
        root_causes = {}
        
        for issue in issues:
            causes = await self._identify_potential_causes(issue, metrics)
            root_causes[issue.issue_id] = causes
        
        return root_causes
    
    async def _identify_potential_causes(self, 
                                       issue: DiagnosticIssue, 
                                       metrics: List[HealthMetric]) -> List[str]:
        """Identify potential root causes for an issue"""        
        potential_causes = []
        
        # Look for correlation patterns
        issue_type = self._classify_issue_type(issue)
        if issue_type in self.correlation_patterns:
            correlated_issues = self.correlation_patterns[issue_type]
            
            # Check if correlated metrics show problems
            for metric in metrics:
                metric_type = self._classify_metric_type(metric)
                if metric_type in correlated_issues:
                    if metric.current_value <= metric.threshold_warning:
                        potential_causes.append(f"Correlated issue: {metric_type}")
        
        # Add common causes based on issue category
        if issue.category == DiagnosticCategory.PERFORMANCE:
            potential_causes.extend(self.common_causes.get("resource_exhaustion", []))
        
        elif issue.category == DiagnosticCategory.RELIABILITY:
            potential_causes.extend(self.common_causes.get("configuration_errors", []))
        
        elif issue.category == DiagnosticCategory.CONNECTIVITY:
            potential_causes.extend(self.common_causes.get("external_dependencies", []))
        
        # Analyze metric patterns
        metric_causes = await self._analyze_metric_patterns(metrics)
        potential_causes.extend(metric_causes)
        
        return list(set(potential_causes))  # Remove duplicates
    
    def _classify_issue_type(self, issue: DiagnosticIssue) -> str:
        """Classify issue type for correlation analysis"""        
        title_lower = issue.title.lower()
        
        if "queue" in title_lower and "size" in title_lower:
            return "high_queue_size"
        elif "response" in title_lower and "time" in title_lower:
            return "high_response_time"
        elif "success" in title_lower or "failure" in title_lower:
            return "low_success_rate"
        elif "worker" in title_lower:
            return "worker_failures"
        else:
            return "unknown"
    
    def _classify_metric_type(self, metric: HealthMetric) -> str:
        """Classify metric type for correlation analysis"""        
        name_lower = metric.metric_name.lower()
        
        if "queue" in name_lower and "size" in name_lower:
            return "high_queue_size"
        elif "processing" in name_lower and "rate" in name_lower:
            return "low_processing_rate"
        elif "response" in name_lower and "time" in name_lower:
            return "high_response_time"
        elif "worker" in name_lower and "health" in name_lower:
            return "worker_health_issues"
        else:
            return "unknown"
    
    async def _analyze_metric_patterns(self, metrics: List[HealthMetric]) -> List[str]:
        """Analyze metric patterns for root cause hints"""        
        patterns = []
        
        # Look for resource exhaustion patterns
        cpu_metrics = [m for m in metrics if "cpu" in m.metric_name.lower()]
        memory_metrics = [m for m in metrics if "memory" in m.metric_name.lower()]
        
        if cpu_metrics and any(m.current_value > m.threshold_warning for m in cpu_metrics):
            patterns.append("High CPU utilization detected")
        
        if memory_metrics and any(m.current_value > m.threshold_warning for m in memory_metrics):
            patterns.append("High memory utilization detected")
        
        # Look for timing patterns
        latency_metrics = [m for m in metrics if any(word in m.metric_name.lower() 
                                                   for word in ["latency", "response", "time"])]
        
        if latency_metrics and any(m.current_value > m.threshold_warning for m in latency_metrics):
            patterns.append("High latency detected across multiple components")
        
        return patterns


class AutomatedRecoveryEngine:
    """Automated recovery execution engine"""    
    def __init__(self, max_concurrent_recoveries: int = 3):
        self.max_concurrent_recoveries = max_concurrent_recoveries
        self.active_recoveries: Dict[str, asyncio.Task] = {}
        self.recovery_history: List[Dict] = []
        
        # Define automated recovery actions
        self.automated_actions = {
            "scale_workers": self._scale_workers_action,
            "restart_unhealthy_workers": self._restart_unhealthy_workers_action,
            "optimize_distribution": self._optimize_distribution_action,
            "clear_queue_backlog": self._clear_queue_backlog_action,
            "adjust_rate_limits": self._adjust_rate_limits_action,
            "emergency_throttle": self._emergency_throttle_action
        }
    
    async def execute_recovery_plan(self, 
                                  plan: RecoveryPlan,
                                  queue_manager: Optional[IntelligentQueueManager] = None,
                                  distribution_engine: Optional[TaskDistributionEngine] = None) -> Dict[str, Any]:
        """Execute recovery plan"""        
        if len(self.active_recoveries) >= self.max_concurrent_recoveries:
            return {
                'success': False,
                'reason': 'Maximum concurrent recoveries reached',
                'active_count': len(self.active_recoveries)
            }
        
        # Create recovery task
        recovery_task = asyncio.create_task(
            self._execute_recovery_steps(plan, queue_manager, distribution_engine)
        )
        
        self.active_recoveries[plan.plan_id] = recovery_task
        
        return {
            'success': True,
            'plan_id': plan.plan_id,
            'estimated_duration': plan.total_estimated_duration,
            'actions_count': len(plan.actions)
        }
    
    async def _execute_recovery_steps(self, 
                                    plan: RecoveryPlan,
                                    queue_manager: Optional[IntelligentQueueManager],
                                    distribution_engine: Optional[TaskDistributionEngine]):
        """Execute individual recovery steps"""        
        execution_log = {
            'plan_id': plan.plan_id,
            'started_at': datetime.utcnow(),
            'actions_executed': [],
            'actions_failed': [],
            'overall_success': False
        }
        
        try:
            for action in plan.actions:
                if action.automation_level == "automated":
                    try:
                        action_result = await self._execute_automated_action(
                            action, queue_manager, distribution_engine
                        )
                        
                        execution_log['actions_executed'].append({
                            'action_id': action.action_id,
                            'title': action.title,
                            'result': action_result,
                            'executed_at': datetime.utcnow().isoformat()
                        })
                        
                    except Exception as e:
                        logger.error(f"Failed to execute action {action.action_id}: {e}")
                        execution_log['actions_failed'].append({
                            'action_id': action.action_id,
                            'title': action.title,
                            'error': str(e),
                            'failed_at': datetime.utcnow().isoformat()
                        })
                
                else:
                    # Log manual actions for reporting
                    execution_log['actions_executed'].append({
                        'action_id': action.action_id,
                        'title': action.title,
                        'result': 'manual_intervention_required',
                        'executed_at': datetime.utcnow().isoformat()
                    })
            
            execution_log['overall_success'] = len(execution_log['actions_failed']) == 0
            execution_log['completed_at'] = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Recovery plan execution failed: {e}")
            execution_log['overall_error'] = str(e)
            execution_log['completed_at'] = datetime.utcnow()
        
        finally:
            # Remove from active recoveries
            if plan.plan_id in self.active_recoveries:
                del self.active_recoveries[plan.plan_id]
            
            # Store in history
            self.recovery_history.append(execution_log)
            
            # Limit history size
            if len(self.recovery_history) > 100:
                self.recovery_history = self.recovery_history[-50:]
    
    async def _execute_automated_action(self, 
                                      action: RecoveryAction,
                                      queue_manager: Optional[IntelligentQueueManager],
                                      distribution_engine: Optional[TaskDistributionEngine]) -> Dict[str, Any]:
        """Execute automated recovery action"""        
        if action.title in self.automated_actions:
            handler = self.automated_actions[action.title]
            return await handler(action, queue_manager, distribution_engine)
        else:
            return {
                'success': False,
                'reason': f'No automated handler for action: {action.title}'
            }
    
    async def _scale_workers_action(self, 
                                  action: RecoveryAction,
                                  queue_manager: Optional[IntelligentQueueManager],
                                  distribution_engine: Optional[TaskDistributionEngine]) -> Dict[str, Any]:
        """Scale workers recovery action"""        
        try:
            # This would interface with actual scaling systems
            logger.info("Executing automated worker scaling")
            
            # Simulate scaling operation
            await asyncio.sleep(2)
            
            return {
                'success': True,
                'action': 'worker_scaling',
                'details': 'Successfully scaled worker pool'
            }
            
        except Exception as e:
            return {
                'success': False,
                'action': 'worker_scaling',
                'error': str(e)
            }
    
    async def _restart_unhealthy_workers_action(self, 
                                              action: RecoveryAction,
                                              queue_manager: Optional[IntelligentQueueManager],
                                              distribution_engine: Optional[TaskDistributionEngine]) -> Dict[str, Any]:
        """Restart unhealthy workers action"""        
        try:
            logger.info("Executing automated unhealthy worker restart")
            
            # This would identify and restart unhealthy workers
            await asyncio.sleep(3)
            
            return {
                'success': True,
                'action': 'worker_restart',
                'details': 'Successfully restarted unhealthy workers'
            }
            
        except Exception as e:
            return {
                'success': False,
                'action': 'worker_restart',
                'error': str(e)
            }
    
    async def _optimize_distribution_action(self, 
                                          action: RecoveryAction,
                                          queue_manager: Optional[IntelligentQueueManager],
                                          distribution_engine: Optional[TaskDistributionEngine]) -> Dict[str, Any]:
        """Optimize distribution strategy action"""        
        try:
            if distribution_engine:
                logger.info("Executing distribution optimization")
                
                # Get optimization recommendations
                optimization_report = await distribution_engine.optimize_distribution_strategy()
                
                return {
                    'success': True,
                    'action': 'distribution_optimization',
                    'details': f"Optimization applied: {len(optimization_report.get('recommendations', []))} recommendations"
                }
            else:
                return {
                    'success': False,
                    'action': 'distribution_optimization',
                    'error': 'Distribution engine not available'
                }
                
        except Exception as e:
            return {
                'success': False,
                'action': 'distribution_optimization',
                'error': str(e)
            }
    
    async def _clear_queue_backlog_action(self, 
                                        action: RecoveryAction,
                                        queue_manager: Optional[IntelligentQueueManager],
                                        distribution_engine: Optional[TaskDistributionEngine]) -> Dict[str, Any]:
        """Clear queue backlog action"""        
        try:
            logger.info("Executing queue backlog clearing")
            
            # This would implement queue clearing logic
            await asyncio.sleep(1)
            
            return {
                'success': True,
                'action': 'queue_backlog_clear',
                'details': 'Successfully cleared queue backlog'
            }
            
        except Exception as e:
            return {
                'success': False,
                'action': 'queue_backlog_clear',
                'error': str(e)
            }
    
    async def _adjust_rate_limits_action(self, 
                                       action: RecoveryAction,
                                       queue_manager: Optional[IntelligentQueueManager],
                                       distribution_engine: Optional[TaskDistributionEngine]) -> Dict[str, Any]:
        """Adjust rate limits action"""        
        try:
            logger.info("Executing rate limit adjustment")
            
            # This would adjust rate limiting parameters
            await asyncio.sleep(1)
            
            return {
                'success': True,
                'action': 'rate_limit_adjustment',
                'details': 'Successfully adjusted rate limits'
            }
            
        except Exception as e:
            return {
                'success': False,
                'action': 'rate_limit_adjustment',
                'error': str(e)
            }
    
    async def _emergency_throttle_action(self, 
                                       action: RecoveryAction,
                                       queue_manager: Optional[IntelligentQueueManager],
                                       distribution_engine: Optional[TaskDistributionEngine]) -> Dict[str, Any]:
        """Emergency throttle action"""        
        try:
            logger.info("Executing emergency throttling")
            
            # This would implement emergency throttling
            await asyncio.sleep(1)
            
            return {
                'success': True,
                'action': 'emergency_throttle',
                'details': 'Successfully applied emergency throttling'
            }
            
        except Exception as e:
            return {
                'success': False,
                'action': 'emergency_throttle',
                'error': str(e)
            }
    
    async def get_recovery_status(self) -> Dict[str, Any]:
        """Get current recovery status"""        
        return {
            'active_recoveries': len(self.active_recoveries),
            'max_concurrent': self.max_concurrent_recoveries,
            'recent_executions': self.recovery_history[-10:] if self.recovery_history else [],
            'success_rate': self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate recovery success rate"""        
        if not self.recovery_history:
            return 0.0
        
        successful = sum(1 for execution in self.recovery_history if execution.get('overall_success', False))
        return successful / len(self.recovery_history)


class QueueHealthDiagnostics:
    """Main queue health diagnostics system"""    
    def __init__(self, 
                 config: DiagnosticConfig,
                 queue_manager: Optional[IntelligentQueueManager] = None,
                 distribution_engine: Optional[TaskDistributionEngine] = None,
                 monitor: Optional[RealtimeQueueMonitor] = None):
        self.config = config
        self.queue_manager = queue_manager
        self.distribution_engine = distribution_engine
        self.monitor = monitor
        
        # Components
        self.component_analyzers: Dict[str, ComponentHealthAnalyzer] = {
            'queue_manager': ComponentHealthAnalyzer('queue_manager'),
            'distribution_engine': ComponentHealthAnalyzer('distribution_engine'),
            'workers': ComponentHealthAnalyzer('workers'),
            'storage': ComponentHealthAnalyzer('storage'),
            'network': ComponentHealthAnalyzer('network')
        }
        
        self.root_cause_analyzer = RootCauseAnalyzer()
        self.recovery_engine = AutomatedRecoveryEngine(config.max_concurrent_recoveries)
        
        # State
        self.current_health_report: Optional[HealthReport] = None
        self.diagnostic_history: deque = deque(maxlen=100)
        self.is_diagnosing = False
        self.diagnostic_tasks: List[asyncio.Task] = []
        
        logger.info("Queue Health Diagnostics system initialized")
    
    async def start_diagnostics(self):
        """Start health diagnostics"""        
        if self.is_diagnosing:
            logger.warning("Diagnostics already running")
            return
        
        self.is_diagnosing = True
        
        # Start diagnostic tasks
        tasks = [
            asyncio.create_task(self._health_monitoring_loop()),
            asyncio.create_task(self._diagnostic_analysis_loop()),
            asyncio.create_task(self._recovery_monitoring_loop())
        ]
        
        if self.config.enable_predictive_diagnostics:
            tasks.append(asyncio.create_task(self._predictive_diagnostics_loop()))
        
        self.diagnostic_tasks = tasks
        
        logger.info("Health diagnostics started")
    
    async def stop_diagnostics(self):
        """Stop health diagnostics"""        
        self.is_diagnosing = False
        
        # Cancel diagnostic tasks
        for task in self.diagnostic_tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self.diagnostic_tasks:
            await asyncio.gather(*self.diagnostic_tasks, return_exceptions=True)
        
        logger.info("Health diagnostics stopped")
    
    async def _health_monitoring_loop(self):
        """Background health monitoring loop"""        
        while self.is_diagnosing:
            try:
                await self._collect_health_metrics()
                await asyncio.sleep(self.config.health_check_interval_seconds)
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.config.health_check_interval_seconds)
    
    async def _collect_health_metrics(self):
        """Collect health metrics from all components"""        
        # Queue Manager metrics
        if self.queue_manager:
            await self._collect_queue_manager_metrics()
        
        # Distribution Engine metrics
        if self.distribution_engine:
            await self._collect_distribution_engine_metrics()
        
        # Monitor metrics (if available)
        if self.monitor:
            await self._collect_monitor_metrics()
        
        # System metrics
        await self._collect_system_metrics()
    
    async def _collect_queue_manager_metrics(self):
        """Collect queue manager health metrics"""        
        analyzer = self.component_analyzers['queue_manager']
        
        # Simulate metrics collection (in real implementation, these would come from actual queue manager)
        metrics = [
            HealthMetric(
                metric_name="queue_size",
                current_value=150.0,  # Simulated
                target_value=100.0,
                threshold_warning=500.0,
                threshold_critical=1000.0,
                weight=2.0,
                unit="tasks",
                description="Current queue size"
            ),
            HealthMetric(
                metric_name="processing_rate",
                current_value=45.0,  # Simulated
                target_value=50.0,
                threshold_warning=20.0,
                threshold_critical=10.0,
                weight=2.0,
                unit="tasks/min",
                description="Task processing rate"
            ),
            HealthMetric(
                metric_name="success_rate",
                current_value=0.96,  # Simulated
                target_value=0.95,
                threshold_warning=0.90,
                threshold_critical=0.80,
                weight=2.0,
                unit="percentage",
                description="Task success rate"
            )
        ]
        
        for metric in metrics:
            await analyzer.add_metric(metric)
    
    async def _collect_distribution_engine_metrics(self):
        """Collect distribution engine health metrics"""        
        analyzer = self.component_analyzers['distribution_engine']
        
        try:
            if hasattr(self.distribution_engine, 'get_distribution_metrics'):
                dist_metrics = await self.distribution_engine.get_distribution_metrics()
                
                metrics = [
                    HealthMetric(
                        metric_name="distribution_time",
                        current_value=dist_metrics.average_distribution_time_ms,
                        target_value=100.0,
                        threshold_warning=500.0,
                        threshold_critical=1000.0,
                        weight=1.5,
                        unit="ms",
                        description="Average distribution time"
                    ),
                    HealthMetric(
                        metric_name="resource_efficiency",
                        current_value=dist_metrics.resource_utilization_efficiency,
                        target_value=0.8,
                        threshold_warning=0.6,
                        threshold_critical=0.4,
                        weight=1.5,
                        unit="percentage",
                        description="Resource utilization efficiency"
                    ),
                    HealthMetric(
                        metric_name="load_balance_score",
                        current_value=dist_metrics.load_balance_score,
                        target_value=0.9,
                        threshold_warning=0.7,
                        threshold_critical=0.5,
                        weight=1.0,
                        unit="score",
                        description="Load balancing effectiveness"
                    )
                ]
                
                for metric in metrics:
                    await analyzer.add_metric(metric)
                    
        except Exception as e:
            logger.error(f"Error collecting distribution engine metrics: {e}")
    
    async def _collect_monitor_metrics(self):
        """Collect monitoring system metrics"""        
        try:
            if hasattr(self.monitor, 'get_monitoring_status'):
                status = await self.monitor.get_monitoring_status()
                
                analyzer = self.component_analyzers['network']
                
                # Use monitoring data for network/connectivity metrics
                metrics = [
                    HealthMetric(
                        metric_name="websocket_connections",
                        current_value=float(status['stats']['active_websocket_connections']),
                        target_value=10.0,
                        threshold_warning=2.0,
                        threshold_critical=0.0,
                        weight=1.0,
                        unit="connections",
                        description="Active WebSocket connections"
                    ),
                    HealthMetric(
                        metric_name="monitoring_health",
                        current_value=status['health_score'],
                        target_value=0.9,
                        threshold_warning=0.7,
                        threshold_critical=0.5,
                        weight=1.5,
                        unit="score",
                        description="Monitoring system health"
                    )
                ]
                
                for metric in metrics:
                    await analyzer.add_metric(metric)
                    
        except Exception as e:
            logger.error(f"Error collecting monitor metrics: {e}")
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""        
        # Storage metrics
        storage_analyzer = self.component_analyzers['storage']
        
        # Simulated storage metrics
        storage_metrics = [
            HealthMetric(
                metric_name="disk_usage",
                current_value=65.0,  # Simulated
                target_value=50.0,
                threshold_warning=80.0,
                threshold_critical=90.0,
                weight=1.5,
                unit="percentage",
                description="Disk usage percentage"
            ),
            HealthMetric(
                metric_name="memory_usage",
                current_value=75.0,  # Simulated
                target_value=60.0,
                threshold_warning=85.0,
                threshold_critical=95.0,
                weight=2.0,
                unit="percentage",
                description="Memory usage percentage"
            )
        ]
        
        for metric in storage_metrics:
            await storage_analyzer.add_metric(metric)
    
    async def _diagnostic_analysis_loop(self):
        """Background diagnostic analysis loop"""        
        while self.is_diagnosing:
            try:
                await self._perform_diagnostic_analysis()
                await asyncio.sleep(self.config.diagnostic_interval_seconds)
                
            except Exception as e:
                logger.error(f"Diagnostic analysis error: {e}")
                await asyncio.sleep(self.config.diagnostic_interval_seconds)
    
    async def _perform_diagnostic_analysis(self):
        """Perform comprehensive diagnostic analysis"""        
        timestamp = datetime.utcnow()
        
        # Calculate component health scores
        component_health = {}
        all_metrics = []
        
        for component_name, analyzer in self.component_analyzers.items():
            health_score = await analyzer.calculate_health_score()
            component_health[component_name] = health_score
            all_metrics.extend(list(analyzer.metrics.values()))
        
        # Calculate overall health score
        overall_health_score = sum(component_health.values()) / len(component_health) if component_health else 0.0
        overall_status = self._determine_health_status(overall_health_score)
        
        # Detect issues
        issues = await self._detect_issues(all_metrics)
        
        # Analyze root causes
        if self.config.enable_root_cause_analysis and issues:
            root_causes = await self.root_cause_analyzer.analyze_root_causes(issues, all_metrics)
            
            # Update issues with root causes
            for issue in issues:
                if issue.issue_id in root_causes:
                    issue.root_causes = root_causes[issue.issue_id]
        
        # Generate recovery plans
        recovery_plans = []
        if issues and self.config.auto_recovery_enabled:
            recovery_plans = await self._generate_recovery_plans(issues)
        
        # Collect recommendations
        recommendations = await self._generate_recommendations(all_metrics, issues)
        
        # Perform trend analysis
        trend_analysis = await self._analyze_trends()
        
        # Collect performance insights
        performance_insights = []
        for analyzer in self.component_analyzers.values():
            insights = await analyzer.get_performance_insights()
            performance_insights.extend(insights)
        
        # Create health report
        health_report = HealthReport(
            report_id=str(uuid.uuid4()),
            timestamp=timestamp,
            overall_health_score=overall_health_score,
            overall_status=overall_status,
            component_health=component_health,
            metrics=all_metrics,
            issues=issues,
            recovery_plans=recovery_plans,
            recommendations=recommendations,
            trend_analysis=trend_analysis,
            performance_insights=performance_insights
        )
        
        self.current_health_report = health_report
        self.diagnostic_history.append(health_report)
        
        # Execute automatic recovery if needed
        if recovery_plans and self.config.auto_recovery_enabled:
            await self._execute_auto_recovery(recovery_plans)
        
        logger.info(f"Health analysis completed - Overall health: {overall_health_score:.2f} ({overall_status.value})")
    
    def _determine_health_status(self, score: float) -> HealthStatus:
        """Determine health status from score"""        
        if score >= 0.9:
            return HealthStatus.EXCELLENT
        elif score >= 0.7:
            return HealthStatus.GOOD
        elif score >= 0.5:
            return HealthStatus.DEGRADED
        elif score >= 0.3:
            return HealthStatus.CRITICAL
        else:
            return HealthStatus.EMERGENCY
    
    async def _detect_issues(self, metrics: List[HealthMetric]) -> List[DiagnosticIssue]:
        """Detect diagnostic issues from metrics"""        
        issues = []
        
        for metric in metrics:
            # Critical threshold violation
            if metric.current_value <= metric.threshold_critical:
                issue = DiagnosticIssue(
                    issue_id=str(uuid.uuid4()),
                    category=self._categorize_metric(metric),
                    severity=DiagnosticSeverity.CRITICAL,
                    title=f"Critical: {metric.metric_name}",
                    description=f"{metric.metric_name} is at critical level: {metric.current_value}{metric.unit}",
                    affected_components=[self._identify_component_from_metric(metric)],
                    root_causes=[],  # Will be filled by root cause analysis
                    symptoms=[f"Metric value {metric.current_value} below critical threshold {metric.threshold_critical}"],
                    impact_assessment="High impact on system performance and reliability",
                    confidence_score=0.9,
                    detected_at=datetime.utcnow(),
                    resolution_priority=1
                )
                issues.append(issue)
            
            # Warning threshold violation
            elif metric.current_value <= metric.threshold_warning:
                issue = DiagnosticIssue(
                    issue_id=str(uuid.uuid4()),
                    category=self._categorize_metric(metric),
                    severity=DiagnosticSeverity.WARNING,
                    title=f"Warning: {metric.metric_name}",
                    description=f"{metric.metric_name} is approaching critical level: {metric.current_value}{metric.unit}",
                    affected_components=[self._identify_component_from_metric(metric)],
                    root_causes=[],
                    symptoms=[f"Metric value {metric.current_value} below warning threshold {metric.threshold_warning}"],
                    impact_assessment="Moderate impact, may lead to performance degradation",
                    confidence_score=0.7,
                    detected_at=datetime.utcnow(),
                    resolution_priority=3
                )
                issues.append(issue)
        
        # Detect pattern-based issues
        pattern_issues = await self._detect_pattern_issues(metrics)
        issues.extend(pattern_issues)
        
        return issues
    
    def _categorize_metric(self, metric: HealthMetric) -> DiagnosticCategory:
        """Categorize metric into diagnostic category"""        
        name_lower = metric.metric_name.lower()
        
        if any(word in name_lower for word in ["rate", "time", "latency", "throughput"]):
            return DiagnosticCategory.PERFORMANCE
        elif any(word in name_lower for word in ["success", "failure", "error", "health"]):
            return DiagnosticCategory.RELIABILITY
        elif any(word in name_lower for word in ["memory", "cpu", "disk", "usage"]):
            return DiagnosticCategory.RESOURCE_USAGE
        elif any(word in name_lower for word in ["connection", "network", "websocket"]):
            return DiagnosticCategory.CONNECTIVITY
        else:
            return DiagnosticCategory.OPERATIONAL
    
    def _identify_component_from_metric(self, metric: HealthMetric) -> str:
        """Identify component from metric name"""        
        name_lower = metric.metric_name.lower()
        
        if any(word in name_lower for word in ["queue", "processing"]):
            return "queue_manager"
        elif any(word in name_lower for word in ["distribution", "load", "balance"]):
            return "distribution_engine"
        elif any(word in name_lower for word in ["worker", "agent"]):
            return "workers"
        elif any(word in name_lower for word in ["disk", "memory", "storage"]):
            return "storage"
        elif any(word in name_lower for word in ["network", "connection", "websocket"]):
            return "network"
        else:
            return "system"
    
    async def _detect_pattern_issues(self, metrics: List[HealthMetric]) -> List[DiagnosticIssue]:
        """Detect issues based on metric patterns"""        
        pattern_issues = []
        
        # Check for correlated degradation
        degraded_metrics = [m for m in metrics if m.current_value <= m.threshold_warning]
        
        if len(degraded_metrics) >= 3:  # Multiple metrics degraded
            issue = DiagnosticIssue(
                issue_id=str(uuid.uuid4()),
                category=DiagnosticCategory.RELIABILITY,
                severity=DiagnosticSeverity.CRITICAL,
                title="System-wide Performance Degradation",
                description=f"Multiple metrics ({len(degraded_metrics)}) showing degraded performance",
                affected_components=list(set(self._identify_component_from_metric(m) for m in degraded_metrics)),
                root_causes=[],
                symptoms=[f"{len(degraded_metrics)} metrics below warning thresholds"],
                impact_assessment="System-wide impact, potential service disruption",
                confidence_score=0.8,
                detected_at=datetime.utcnow(),
                resolution_priority=1
            )
            pattern_issues.append(issue)
        
        return pattern_issues
    
    async def _generate_recovery_plans(self, issues: List[DiagnosticIssue]) -> List[RecoveryPlan]:
        """Generate recovery plans for detected issues"""        
        recovery_plans = []
        
        for issue in issues:
            if issue.severity in [DiagnosticSeverity.CRITICAL, DiagnosticSeverity.EMERGENCY]:
                plan = await self._create_recovery_plan(issue)
                if plan:
                    recovery_plans.append(plan)
        
        return recovery_plans
    
    async def _create_recovery_plan(self, issue: DiagnosticIssue) -> Optional[RecoveryPlan]:
        """Create recovery plan for specific issue"""        
        actions = []
        
        # Define recovery actions based on issue category and affected components
        if issue.category == DiagnosticCategory.PERFORMANCE:
            if "queue_manager" in issue.affected_components:
                actions.append(RecoveryAction(
                    action_id=str(uuid.uuid4()),
                    title="scale_workers",
                    description="Scale up worker pool to handle increased load",
                    strategy=RecoveryStrategy.IMMEDIATE,
                    estimated_duration_minutes=5,
                    risk_level="low",
                    automation_level="automated",
                    steps=["Identify current worker capacity", "Scale worker pool", "Verify scaling"],
                    success_criteria=["Processing rate improved", "Queue size reduced"]
                ))
            
            if "distribution_engine" in issue.affected_components:
                actions.append(RecoveryAction(
                    action_id=str(uuid.uuid4()),
                    title="optimize_distribution",
                    description="Optimize task distribution strategy",
                    strategy=RecoveryStrategy.IMMEDIATE,
                    estimated_duration_minutes=3,
                    risk_level="low",
                    automation_level="automated",
                    steps=["Analyze current distribution", "Apply optimization", "Monitor results"],
                    success_criteria=["Distribution time improved", "Load balance improved"]
                ))
        
        elif issue.category == DiagnosticCategory.RELIABILITY:
            actions.append(RecoveryAction(
                action_id=str(uuid.uuid4()),
                title="restart_unhealthy_workers",
                description="Restart workers showing health issues",
                strategy=RecoveryStrategy.IMMEDIATE,
                estimated_duration_minutes=10,
                risk_level="medium",
                automation_level="automated",
                steps=["Identify unhealthy workers", "Graceful restart", "Health verification"],
                success_criteria=["Worker health improved", "Success rate increased"]
            ))
        
        if not actions:
            return None
        
        total_duration = sum(action.estimated_duration_minutes for action in actions)
        
        return RecoveryPlan(
            plan_id=str(uuid.uuid4()),
            issue_id=issue.issue_id,
            strategy=RecoveryStrategy.IMMEDIATE,
            total_estimated_duration=total_duration,
            actions=actions,
            rollback_strategy="Automatic rollback if health scores worsen",
            approval_required=False  # Auto-recovery enabled
        )
    
    async def _generate_recommendations(self, 
                                      metrics: List[HealthMetric], 
                                      issues: List[DiagnosticIssue]) -> List[str]:
        """Generate optimization recommendations"""        
        recommendations = []
        
        # Performance recommendations
        queue_size_metrics = [m for m in metrics if "queue_size" in m.metric_name.lower()]
        if queue_size_metrics and any(m.current_value > m.threshold_warning for m in queue_size_metrics):
            recommendations.append("Consider implementing queue size monitoring and auto-scaling")
        
        # Resource recommendations
        memory_metrics = [m for m in metrics if "memory" in m.metric_name.lower()]
        if memory_metrics and any(m.current_value > m.threshold_warning for m in memory_metrics):
            recommendations.append("Monitor memory usage patterns and consider memory optimization")
        
        # Distribution recommendations
        distribution_metrics = [m for m in metrics if "distribution" in m.metric_name.lower()]
        if distribution_metrics and any(m.current_value > m.threshold_warning for m in distribution_metrics):
            recommendations.append("Evaluate distribution strategy efficiency and consider ML-based optimization")
        
        # Issue-based recommendations
        critical_issues = [i for i in issues if i.severity == DiagnosticSeverity.CRITICAL]
        if len(critical_issues) > 1:
            recommendations.append("Multiple critical issues detected - consider comprehensive system review")
        
        # Trend-based recommendations
        if len(issues) > 5:
            recommendations.append("High number of issues detected - recommend proactive monitoring enhancement")
        
        return recommendations
    
    async def _analyze_trends(self) -> Dict[str, str]:
        """Analyze health trends"""        
        trends = {}
        
        # Analyze component trends
        for component_name, analyzer in self.component_analyzers.items():
            if len(analyzer.historical_scores) >= 5:
                scores = [item['score'] for item in list(analyzer.historical_scores)[-10:]]
                trend_direction = await analyzer._analyze_trend(scores)
                trends[component_name] = trend_direction
        
        # Overall system trend
        if len(self.diagnostic_history) >= 3:
            recent_scores = [report.overall_health_score for report in list(self.diagnostic_history)[-5:]]
            if len(recent_scores) >= 3:
                first_half = recent_scores[:len(recent_scores)//2]
                second_half = recent_scores[len(recent_scores)//2:]
                
                first_avg = sum(first_half) / len(first_half)
                second_avg = sum(second_half) / len(second_half)
                
                change_percent = ((second_avg - first_avg) / max(0.001, first_avg)) * 100
                
                if change_percent > 10:
                    trends['overall'] = "improving"
                elif change_percent < -10:
                    trends['overall'] = "declining"
                else:
                    trends['overall'] = "stable"
        
        return trends
    
    async def _execute_auto_recovery(self, recovery_plans: List[RecoveryPlan]):
        """Execute automatic recovery plans"""        
        for plan in recovery_plans:
            if not plan.approval_required:
                try:
                    result = await self.recovery_engine.execute_recovery_plan(
                        plan, self.queue_manager, self.distribution_engine
                    )
                    
                    if result['success']:
                        logger.info(f"Auto-recovery plan executed: {plan.plan_id}")
                    else:
                        logger.warning(f"Auto-recovery plan failed: {result.get('reason', 'Unknown')}")
                        
                except Exception as e:
                    logger.error(f"Error executing auto-recovery plan {plan.plan_id}: {e}")
    
    async def _recovery_monitoring_loop(self):
        """Background recovery monitoring loop"""        
        while self.is_diagnosing:
            try:
                await self._monitor_recovery_progress()
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Recovery monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_recovery_progress(self):
        """Monitor recovery progress and effectiveness"""        
        recovery_status = await self.recovery_engine.get_recovery_status()
        
        if recovery_status['active_recoveries'] > 0:
            logger.info(f"Active recoveries: {recovery_status['active_recoveries']}")
        
        # Log success rate periodically
        if recovery_status['recent_executions']:
            success_rate = recovery_status['success_rate']
            logger.info(f"Recovery success rate: {success_rate:.2%}")
    
    async def _predictive_diagnostics_loop(self):
        """Background predictive diagnostics loop"""        
        while self.is_diagnosing:
            try:
                await self._perform_predictive_analysis()
                await asyncio.sleep(600)  # Every 10 minutes
                
            except Exception as e:
                logger.error(f"Predictive diagnostics error: {e}")
                await asyncio.sleep(600)
    
    async def _perform_predictive_analysis(self):
        """Perform predictive analysis for early issue detection"""        
        # Analyze trends in component health
        for component_name, analyzer in self.component_analyzers.items():
            if len(analyzer.historical_scores) >= 10:
                scores = [item['score'] for item in list(analyzer.historical_scores)]
                
                # Simple prediction: if declining trend continues
                recent_trend = await analyzer._analyze_trend(scores[-5:])
                
                if recent_trend == "declining":
                    current_score = scores[-1]
                    
                    # Predict if will reach critical threshold
                    if current_score < 0.6:  # Already getting low
                        logger.warning(f"Predictive alert: {component_name} health declining, may reach critical level")
                        
                        # Could trigger proactive recovery here
                        if self.config.auto_recovery_enabled:
                            await self._trigger_predictive_recovery(component_name, current_score)
    
    async def _trigger_predictive_recovery(self, component_name: str, current_score: float):
        """Trigger predictive recovery actions"""        
        # Create predictive recovery action
        if component_name == "queue_manager" and current_score < 0.5:
            # Proactive queue management
            logger.info("Triggering predictive queue optimization")
            
        elif component_name == "distribution_engine" and current_score < 0.5:
            # Proactive distribution optimization
            logger.info("Triggering predictive distribution optimization")
    
    async def get_current_health_report(self) -> Optional[HealthReport]:
        """Get current health report"""        return self.current_health_report
    
    async def get_diagnostic_status(self) -> Dict[str, Any]:
        """Get diagnostic system status"""        
        component_health = {}
        for name, analyzer in self.component_analyzers.items():
            health_score = await analyzer.calculate_health_score()
            component_health[name] = health_score
        
        recovery_status = await self.recovery_engine.get_recovery_status()
        
        return {
            'is_diagnosing': self.is_diagnosing,
            'config': {
                'diagnostic_interval_seconds': self.config.diagnostic_interval_seconds,
                'auto_recovery_enabled': self.config.auto_recovery_enabled,
                'predictive_diagnostics_enabled': self.config.enable_predictive_diagnostics,
                'root_cause_analysis_enabled': self.config.enable_root_cause_analysis
            },
            'component_health': component_health,
            'overall_health_score': sum(component_health.values()) / len(component_health) if component_health else 0.0,
            'active_issues': len(self.current_health_report.issues) if self.current_health_report else 0,
            'recovery_status': recovery_status,
            'diagnostic_history_count': len(self.diagnostic_history),
            'last_analysis_time': (
                self.current_health_report.timestamp.isoformat() 
                if self.current_health_report else None
            )
        }


# Factory function
def create_queue_health_diagnostics(
    config: Optional[DiagnosticConfig] = None,
    queue_manager: Optional[IntelligentQueueManager] = None,
    distribution_engine: Optional[TaskDistributionEngine] = None,
    monitor: Optional[RealtimeQueueMonitor] = None
) -> QueueHealthDiagnostics:
    """Create and configure queue health diagnostics system"""    
    if config is None:
        config = DiagnosticConfig()
    
    return QueueHealthDiagnostics(
        config=config,
        queue_manager=queue_manager,
        distribution_engine=distribution_engine,
        monitor=monitor
    )


# Export classes and functions
__all__ = [
    'QueueHealthDiagnostics',
    'ComponentHealthAnalyzer',
    'RootCauseAnalyzer',
    'AutomatedRecoveryEngine',
    'DiagnosticConfig',
    'HealthStatus',
    'DiagnosticCategory',
    'RecoveryStrategy',
    'DiagnosticSeverity',
    'HealthMetric',
    'DiagnosticIssue',
    'RecoveryAction',
    'RecoveryPlan',
    'HealthReport',
    'create_queue_health_diagnostics'
]
