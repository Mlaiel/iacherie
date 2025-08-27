"""
Blockchain Module Monitoring and Metrics
Professional monitoring, alerting, and performance metrics for blockchain operations

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Any unauthorized use, reproduction, or distribution
of this code without explicit written permission is strictly prohibited.

Project Team Specialties:
- Lead AI Developer & Backend Senior: Fahed Mlaiel
- ML Engineer & Blockchain Specialist: Advanced IA Processing
- Database Administrator & Security Expert: Data Protection
- Microservices Architect & Audio Processing: Multi-format Support  
- DevOps Engineer & IA Prompt Engineer: Production Deployment

⚠️ STRONG WARNING ⚠️
Any attempt to steal, copy, reproduce, or use this concept, idea, or code 
without explicit written authorization from Fahed Mlaiel is strictly 
prohibited and will result in legal action.

Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import time
import json
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics collected"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Individual metric data point"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class Alert:
    """Alert definition and state"""
    name: str
    condition: str
    level: AlertLevel
    threshold: float
    message: str
    enabled: bool = True
    triggered: bool = False
    last_triggered: Optional[datetime] = None
    count: int = 0


class MetricsCollector:
    """Collects and aggregates blockchain metrics"""
    
    def __init__(self, retention_hours: int = 24):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.retention_hours = retention_hours
        self.last_cleanup = datetime.utcnow()
        
        # Performance counters
        self.counters: Dict[str, int] = defaultdict(int)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        
    def record_metric(self, metric: Metric):
        """Record a metric data point"""
        self.metrics[metric.name].append(metric)
        
        # Update counters and timers
        if metric.metric_type == MetricType.COUNTER:
            self.counters[metric.name] += metric.value
        elif metric.metric_type == MetricType.TIMER:
            self.timers[metric.name].append(metric.value)
            
        # Cleanup old metrics periodically
        if (datetime.utcnow() - self.last_cleanup).total_seconds() > 3600:
            self._cleanup_old_metrics()
    
    def increment_counter(self, name: str, value: float = 1, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            timestamp=datetime.utcnow(),
            labels=labels or {}
        )
        self.record_metric(metric)
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric value"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            timestamp=datetime.utcnow(),
            labels=labels or {}
        )
        self.record_metric(metric)
    
    def record_timer(self, name: str, duration: float, labels: Dict[str, str] = None):
        """Record a timer metric"""
        metric = Metric(
            name=name,
            value=duration,
            metric_type=MetricType.TIMER,
            timestamp=datetime.utcnow(),
            labels=labels or {}
        )
        self.record_metric(metric)
    
    def get_metric_summary(self, name: str, hours: int = 1) -> Dict[str, Any]:
        """Get statistical summary of a metric"""
        if name not in self.metrics:
            return {}
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics[name] 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        values = [m.value for m in recent_metrics]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0,
            'sum': sum(values),
            'latest': values[-1] if values else 0,
            'time_range': {
                'start': recent_metrics[0].timestamp.isoformat(),
                'end': recent_metrics[-1].timestamp.isoformat()
            }
        }
    
    def _cleanup_old_metrics(self):
        """Remove metrics older than retention period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)
        
        for name, metric_deque in self.metrics.items():
            # Remove old metrics from the front of the deque
            while metric_deque and metric_deque[0].timestamp < cutoff_time:
                metric_deque.popleft()
        
        self.last_cleanup = datetime.utcnow()


class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, collector: MetricsCollector, metric_name: str, labels: Dict[str, str] = None):
        self.collector = collector
        self.metric_name = metric_name
        self.labels = labels or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.collector.record_timer(self.metric_name, duration, self.labels)


class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.alerts: Dict[str, Alert] = {}
        self.alert_handlers: List[Callable] = []
        self.check_interval = 60  # seconds
        self.running = False
    
    def add_alert(self, alert: Alert):
        """Add an alert definition"""
        self.alerts[alert.name] = alert
        logger.info(f"Alert added: {alert.name}")
    
    def add_alert_handler(self, handler: Callable[[Alert, float], None]):
        """Add an alert handler function"""
        self.alert_handlers.append(handler)
    
    async def start_monitoring(self):
        """Start alert monitoring loop"""
        self.running = True
        logger.info("Alert monitoring started")
        
        while self.running:
            try:
                await self._check_alerts()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
                await asyncio.sleep(30)
    
    def stop_monitoring(self):
        """Stop alert monitoring"""
        self.running = False
        logger.info("Alert monitoring stopped")
    
    async def _check_alerts(self):
        """Check all alerts against current metrics"""
        for alert_name, alert in self.alerts.items():
            if not alert.enabled:
                continue
            
            try:
                # Get metric value for alert condition
                metric_value = self._evaluate_alert_condition(alert)
                
                # Check if threshold is exceeded
                if self._threshold_exceeded(alert, metric_value):
                    if not alert.triggered:
                        # New alert trigger
                        alert.triggered = True
                        alert.last_triggered = datetime.utcnow()
                        alert.count += 1
                        
                        # Execute alert handlers
                        for handler in self.alert_handlers:
                            try:
                                await handler(alert, metric_value)
                            except Exception as e:
                                logger.error(f"Alert handler error: {e}")
                        
                        logger.warning(f"Alert triggered: {alert.name} (value: {metric_value})")
                else:
                    # Alert condition not met
                    if alert.triggered:
                        alert.triggered = False
                        logger.info(f"Alert resolved: {alert.name}")
                        
            except Exception as e:
                logger.error(f"Error checking alert {alert_name}: {e}")
    
    def _evaluate_alert_condition(self, alert: Alert) -> float:
        """Evaluate alert condition and return metric value"""
        # Parse condition string (e.g., "transaction_failures_per_hour")
        metric_name = alert.condition
        summary = self.metrics_collector.get_metric_summary(metric_name, hours=1)
        
        if not summary:
            return 0.0
        
        # Return appropriate value based on alert type
        if "rate" in metric_name or "per_hour" in metric_name:
            return summary.get('count', 0)
        elif "latency" in metric_name or "duration" in metric_name:
            return summary.get('mean', 0)
        else:
            return summary.get('latest', 0)
    
    def _threshold_exceeded(self, alert: Alert, value: float) -> bool:
        """Check if alert threshold is exceeded"""
        if alert.level in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
            return value >= alert.threshold
        else:
            return value >= alert.threshold


class BlockchainMonitor:
    """Main monitoring service for blockchain operations"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager(self.metrics_collector)
        self.initialized = False
        
        # Setup default alerts
        self._setup_default_alerts()
        
        # Setup default alert handlers
        self._setup_alert_handlers()
    
    async def initialize(self):
        """Initialize monitoring service"""
        try:
            # Start alert monitoring
            asyncio.create_task(self.alert_manager.start_monitoring())
            
            self.initialized = True
            logger.info("Blockchain monitoring initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring: {e}")
            return False
    
    def _setup_default_alerts(self):
        """Setup default alerts for blockchain operations"""
        alerts = [
            Alert(
                name="high_transaction_failure_rate",
                condition="transaction_failures_per_hour",
                level=AlertLevel.ERROR,
                threshold=10,
                message="High transaction failure rate detected"
            ),
            Alert(
                name="high_gas_prices",
                condition="average_gas_price_gwei",
                level=AlertLevel.WARNING,
                threshold=100,
                message="Gas prices are unusually high"
            ),
            Alert(
                name="slow_transaction_confirmation",
                condition="average_confirmation_time",
                level=AlertLevel.WARNING,
                threshold=300,  # 5 minutes
                message="Transaction confirmations are taking too long"
            ),
            Alert(
                name="blockchain_connection_errors",
                condition="connection_errors_per_hour",
                level=AlertLevel.CRITICAL,
                threshold=5,
                message="Multiple blockchain connection errors"
            ),
            Alert(
                name="low_wallet_balance",
                condition="wallet_balance_eth",
                level=AlertLevel.WARNING,
                threshold=0.1,  # 0.1 ETH
                message="Wallet balance is running low"
            )
        ]
        
        for alert in alerts:
            self.alert_manager.add_alert(alert)
    
    def _setup_alert_handlers(self):
        """Setup alert notification handlers"""
        self.alert_manager.add_alert_handler(self._log_alert)
        # Add additional handlers for Slack, email, etc.
    
    async def _log_alert(self, alert: Alert, value: float):
        """Log alert to system logger"""
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL
        }.get(alert.level, logging.WARNING)
        
        logger.log(
            log_level,
            f"ALERT: {alert.message} | Metric: {alert.condition} | "
            f"Value: {value} | Threshold: {alert.threshold}"
        )
    
    # Metric recording methods
    def record_transaction_success(self, network: str, tx_hash: str, gas_used: int, duration: float):
        """Record successful transaction"""
        labels = {'network': network, 'status': 'success'}
        
        self.metrics_collector.increment_counter('transactions_total', labels=labels)
        self.metrics_collector.record_timer('transaction_duration', duration, labels=labels)
        self.metrics_collector.set_gauge('gas_used', gas_used, labels=labels)
    
    def record_transaction_failure(self, network: str, error: str, duration: float):
        """Record failed transaction"""
        labels = {'network': network, 'status': 'failed', 'error': error}
        
        self.metrics_collector.increment_counter('transactions_total', labels=labels)
        self.metrics_collector.increment_counter('transaction_failures', labels=labels)
        self.metrics_collector.record_timer('transaction_duration', duration, labels=labels)
    
    def record_gas_price(self, network: str, gas_price_gwei: float):
        """Record current gas price"""
        labels = {'network': network}
        self.metrics_collector.set_gauge('gas_price_gwei', gas_price_gwei, labels=labels)
    
    def record_wallet_balance(self, network: str, address: str, balance: float):
        """Record wallet balance"""
        labels = {'network': network, 'address': address}
        self.metrics_collector.set_gauge('wallet_balance', balance, labels=labels)
    
    def record_nft_operation(self, operation: str, success: bool, duration: float):
        """Record NFT operation metrics"""
        labels = {'operation': operation, 'success': str(success)}
        
        self.metrics_collector.increment_counter('nft_operations_total', labels=labels)
        self.metrics_collector.record_timer('nft_operation_duration', duration, labels=labels)
    
    def record_defi_operation(self, protocol: str, operation: str, amount: float, success: bool):
        """Record DeFi operation metrics"""
        labels = {'protocol': protocol, 'operation': operation, 'success': str(success)}
        
        self.metrics_collector.increment_counter('defi_operations_total', labels=labels)
        self.metrics_collector.set_gauge('defi_amount', amount, labels=labels)
    
    def record_storage_operation(self, network: str, operation: str, size_bytes: int, success: bool):
        """Record distributed storage operation"""
        labels = {'network': network, 'operation': operation, 'success': str(success)}
        
        self.metrics_collector.increment_counter('storage_operations_total', labels=labels)
        self.metrics_collector.set_gauge('storage_size_bytes', size_bytes, labels=labels)
    
    # Query methods
    def get_transaction_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get transaction performance metrics"""
        return {
            'total_transactions': self.metrics_collector.get_metric_summary('transactions_total', hours),
            'failed_transactions': self.metrics_collector.get_metric_summary('transaction_failures', hours),
            'average_duration': self.metrics_collector.get_metric_summary('transaction_duration', hours),
            'gas_usage': self.metrics_collector.get_metric_summary('gas_used', hours)
        }
    
    def get_network_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get network performance metrics"""
        return {
            'gas_prices': self.metrics_collector.get_metric_summary('gas_price_gwei', hours),
            'confirmation_times': self.metrics_collector.get_metric_summary('confirmation_time', hours),
            'connection_errors': self.metrics_collector.get_metric_summary('connection_errors', hours)
        }
    
    def get_comprehensive_report(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive monitoring report"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'period_hours': hours,
            'transaction_metrics': self.get_transaction_metrics(hours),
            'network_metrics': self.get_network_metrics(hours),
            'active_alerts': [
                {
                    'name': alert.name,
                    'level': alert.level.value,
                    'triggered': alert.triggered,
                    'last_triggered': alert.last_triggered.isoformat() if alert.last_triggered else None,
                    'count': alert.count
                }
                for alert in self.alert_manager.alerts.values()
                if alert.triggered
            ],
            'system_health': {
                'monitoring_active': self.alert_manager.running,
                'metrics_collected': sum(len(deque) for deque in self.metrics_collector.metrics.values()),
                'uptime_hours': hours  # Would be calculated from service start time
            }
        }
    
    def timer(self, metric_name: str, labels: Dict[str, str] = None) -> PerformanceTimer:
        """Get a timer context manager for measuring operations"""
        return PerformanceTimer(self.metrics_collector, metric_name, labels)
    
    async def shutdown(self):
        """Shutdown monitoring service"""
        try:
            self.alert_manager.stop_monitoring()
            logger.info("Blockchain monitoring shutdown complete")
        except Exception as e:
            logger.error(f"Monitoring shutdown error: {e}")


# Global monitoring instance
blockchain_monitor = BlockchainMonitor()


async def get_blockchain_monitor() -> BlockchainMonitor:
    """Get the global blockchain monitoring instance"""
    if not blockchain_monitor.initialized:
        await blockchain_monitor.initialize()
    
    return blockchain_monitor


__all__ = [
    'BlockchainMonitor',
    'MetricsCollector',
    'AlertManager',
    'PerformanceTimer',
    'Metric',
    'Alert',
    'MetricType',
    'AlertLevel',
    'get_blockchain_monitor',
    'blockchain_monitor'
]
