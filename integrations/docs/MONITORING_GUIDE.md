# Integration Monitoring Guide - Enterprise Platform
===================================================

## Table of Contents
- [Monitoring Architecture](#monitoring-architecture)
- [Key Metrics and KPIs](#key-metrics-and-kpis)
- [Real-time Monitoring](#real-time-monitoring)
- [Alerting System](#alerting-system)
- [Performance Tracking](#performance-tracking)
- [Health Checks](#health-checks)
- [Dashboard Configuration](#dashboard-configuration)
- [Troubleshooting Guide](#troubleshooting-guide)

## Monitoring Architecture

### Overview

The Ainflue integration monitoring system provides comprehensive observability across all third-party integrations, ensuring high availability, performance, and reliability.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Integration   │───▶│   Monitoring    │───▶│   Alerting      │
│   Services      │    │   Collector     │    │   System        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         │                        ▼                        ▼
         │               ┌─────────────────┐    ┌─────────────────┐
         │               │   Metrics       │    │   Notification  │
         │               │   Storage       │    │   Channels      │
         │               └─────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Health Check  │    │   Analytics     │    │   Incident      │
│   Endpoints     │    │   Dashboard     │    │   Management    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

#### 1. Metrics Collection

```python
import time
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class Metric:
    """Individual metric data point"""
    name: str
    value: float
    metric_type: MetricType
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
class MetricsCollector:
    """Centralized metrics collection system"""
    
    def __init__(self):
        self.metrics: Dict[str, List[Metric]] = {}
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = {}
        self.logger = logging.getLogger(__name__)
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        key = self._get_metric_key(name, labels)
        self.counters[key] = self.counters.get(key, 0) + value
        
        metric = Metric(
            name=name,
            value=self.counters[key],
            metric_type=MetricType.COUNTER,
            labels=labels or {}
        )
        self._store_metric(metric)
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric value"""
        key = self._get_metric_key(name, labels)
        self.gauges[key] = value
        
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            labels=labels or {}
        )
        self._store_metric(metric)
    
    def record_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a histogram value"""
        key = self._get_metric_key(name, labels)
        if key not in self.histograms:
            self.histograms[key] = []
        
        self.histograms[key].append(value)
        
        # Keep only last 1000 values to prevent memory issues
        if len(self.histograms[key]) > 1000:
            self.histograms[key] = self.histograms[key][-1000:]
        
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            labels=labels or {}
        )
        self._store_metric(metric)
    
    def _get_metric_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """Generate unique key for metric"""
        if not labels:
            return name
        
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def _store_metric(self, metric: Metric):
        """Store metric for retrieval"""
        if metric.name not in self.metrics:
            self.metrics[metric.name] = []
        
        self.metrics[metric.name].append(metric)
        
        # Keep only last 1000 metrics per name
        if len(self.metrics[metric.name]) > 1000:
            self.metrics[metric.name] = self.metrics[metric.name][-1000:]
```

#### 2. Integration Health Monitoring

```python
import aiohttp
from datetime import datetime, timedelta

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class HealthCheckResult:
    """Health check result"""
    provider: str
    status: HealthStatus
    response_time: float
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class IntegrationHealthMonitor:
    """Monitor health of all integrations"""
    
    def __init__(self, integrations_config: Dict[str, Any]):
        self.config = integrations_config
        self.health_results: Dict[str, HealthCheckResult] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.check_interval = 60  # seconds
        self.timeout = 30  # seconds
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        
        # Start background health check task
        asyncio.create_task(self._continuous_health_checks())
    
    async def stop_monitoring(self):
        """Stop monitoring and cleanup"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _continuous_health_checks(self):
        """Run health checks continuously"""
        while True:
            try:
                await self.run_all_health_checks()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logging.error(f"Health check error: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def run_all_health_checks(self):
        """Run health checks for all configured integrations"""
        tasks = []
        
        for provider, config in self.config.items():
            if config.get('health_check_enabled', True):
                task = asyncio.create_task(
                    self.check_provider_health(provider, config)
                )
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def check_provider_health(self, provider: str, config: Dict[str, Any]) -> HealthCheckResult:
        """Check health of specific provider"""
        start_time = time.time()
        
        try:
            if provider == 'twilio':
                result = await self._check_twilio_health(config)
            elif provider == 'sendgrid':
                result = await self._check_sendgrid_health(config)
            elif provider == 'stripe':
                result = await self._check_stripe_health(config)
            elif provider == 'google_analytics':
                result = await self._check_google_analytics_health(config)
            else:
                result = await self._check_generic_health(provider, config)
            
            response_time = time.time() - start_time
            
            health_result = HealthCheckResult(
                provider=provider,
                status=result.get('status', HealthStatus.UNKNOWN),
                response_time=response_time,
                error_message=result.get('error'),
                metadata=result.get('metadata', {})
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            health_result = HealthCheckResult(
                provider=provider,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                error_message=str(e)
            )
        
        # Store result
        self.health_results[provider] = health_result
        
        # Record metrics
        metrics_collector.set_gauge(
            "integration_health_status",
            1.0 if health_result.status == HealthStatus.HEALTHY else 0.0,
            {"provider": provider}
        )
        metrics_collector.record_histogram(
            "integration_response_time",
            health_result.response_time,
            {"provider": provider}
        )
        
        return health_result
    
    async def _check_twilio_health(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check Twilio API health"""
        url = f"https://api.twilio.com/2010-04-01/Accounts/{config['account_sid']}.json"
        
        auth = aiohttp.BasicAuth(config['account_sid'], config['auth_token'])
        
        async with self.session.get(url, auth=auth) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    'status': HealthStatus.HEALTHY,
                    'metadata': {
                        'account_status': data.get('status'),
                        'account_type': data.get('type')
                    }
                }
            else:
                return {
                    'status': HealthStatus.UNHEALTHY,
                    'error': f"HTTP {response.status}: {await response.text()}"
                }
    
    async def _check_sendgrid_health(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check SendGrid API health"""
        url = "https://api.sendgrid.com/v3/user/account"
        
        headers = {
            'Authorization': f"Bearer {config['api_key']}",
            'Content-Type': 'application/json'
        }
        
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    'status': HealthStatus.HEALTHY,
                    'metadata': {
                        'account_type': data.get('type'),
                        'reputation': data.get('reputation')
                    }
                }
            else:
                return {
                    'status': HealthStatus.UNHEALTHY,
                    'error': f"HTTP {response.status}: {await response.text()}"
                }
    
    async def _check_stripe_health(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check Stripe API health"""
        url = "https://api.stripe.com/v1/account"
        
        auth = aiohttp.BasicAuth(config['secret_key'], '')
        
        async with self.session.get(url, auth=auth) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    'status': HealthStatus.HEALTHY,
                    'metadata': {
                        'country': data.get('country'),
                        'business_type': data.get('business_type')
                    }
                }
            else:
                return {
                    'status': HealthStatus.UNHEALTHY,
                    'error': f"HTTP {response.status}: {await response.text()}"
                }
    
    async def _check_generic_health(self, provider: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generic health check for providers without specific checks"""
        health_url = config.get('health_check_url')
        
        if not health_url:
            return {
                'status': HealthStatus.UNKNOWN,
                'error': 'No health check URL configured'
            }
        
        headers = config.get('health_check_headers', {})
        
        async with self.session.get(health_url, headers=headers) as response:
            if 200 <= response.status < 300:
                return {'status': HealthStatus.HEALTHY}
            elif 300 <= response.status < 500:
                return {'status': HealthStatus.DEGRADED}
            else:
                return {
                    'status': HealthStatus.UNHEALTHY,
                    'error': f"HTTP {response.status}"
                }
```

## Key Metrics and KPIs

### Integration Performance Metrics

```python
class IntegrationMetrics:
    """Key performance indicators for integrations"""
    
    # Availability Metrics
    UPTIME_PERCENTAGE = "integration_uptime_percentage"
    DOWNTIME_DURATION = "integration_downtime_duration"
    AVAILABILITY_SLA = "integration_availability_sla"
    
    # Performance Metrics
    REQUEST_DURATION = "integration_request_duration"
    RESPONSE_TIME_P50 = "integration_response_time_p50"
    RESPONSE_TIME_P95 = "integration_response_time_p95"
    RESPONSE_TIME_P99 = "integration_response_time_p99"
    
    # Reliability Metrics
    SUCCESS_RATE = "integration_success_rate"
    ERROR_RATE = "integration_error_rate"
    RETRY_RATE = "integration_retry_rate"
    TIMEOUT_RATE = "integration_timeout_rate"
    
    # Throughput Metrics
    REQUESTS_PER_SECOND = "integration_requests_per_second"
    REQUESTS_PER_MINUTE = "integration_requests_per_minute"
    DAILY_REQUEST_VOLUME = "integration_daily_request_volume"
    
    # Business Metrics
    COST_PER_REQUEST = "integration_cost_per_request"
    REVENUE_IMPACT = "integration_revenue_impact"
    USER_EXPERIENCE_SCORE = "integration_user_experience_score"

class MetricsCalculator:
    """Calculate derived metrics from raw data"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector
    
    def calculate_success_rate(self, provider: str, time_window: int = 3600) -> float:
        """Calculate success rate over time window"""
        success_key = f"integration_requests_success{{provider={provider}}}"
        error_key = f"integration_requests_error{{provider={provider}}}"
        
        success_count = self.collector.counters.get(success_key, 0)
        error_count = self.collector.counters.get(error_key, 0)
        total_requests = success_count + error_count
        
        return (success_count / total_requests * 100) if total_requests > 0 else 0.0
    
    def calculate_percentiles(self, provider: str, metric_name: str) -> Dict[str, float]:
        """Calculate response time percentiles"""
        key = f"{metric_name}{{provider={provider}}}"
        values = self.collector.histograms.get(key, [])
        
        if not values:
            return {'p50': 0.0, 'p95': 0.0, 'p99': 0.0}
        
        sorted_values = sorted(values)
        length = len(sorted_values)
        
        return {
            'p50': sorted_values[int(length * 0.5)],
            'p95': sorted_values[int(length * 0.95)],
            'p99': sorted_values[int(length * 0.99)]
        }
    
    def calculate_availability(self, provider: str, time_window: int = 86400) -> float:
        """Calculate availability percentage"""
        # Get health check results for the time window
        health_results = self.collector.metrics.get('integration_health_status', [])
        
        provider_results = [
            r for r in health_results 
            if r.labels.get('provider') == provider and
            time.time() - r.timestamp < time_window
        ]
        
        if not provider_results:
            return 0.0
        
        healthy_count = sum(1 for r in provider_results if r.value == 1.0)
        return (healthy_count / len(provider_results)) * 100
```

### Business Impact Metrics

```python
class BusinessMetrics:
    """Business-focused integration metrics"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector
    
    def calculate_revenue_impact(self, provider: str) -> Dict[str, float]:
        """Calculate revenue impact of integration performance"""
        success_rate = self.calculate_success_rate(provider)
        
        # Business rules for revenue impact
        if success_rate >= 99.5:
            impact_multiplier = 1.0
        elif success_rate >= 99.0:
            impact_multiplier = 0.98
        elif success_rate >= 95.0:
            impact_multiplier = 0.90
        else:
            impact_multiplier = 0.75
        
        # Calculate based on provider importance
        provider_weights = {
            'stripe': 0.4,  # Payment is critical
            'sendgrid': 0.2,  # Email is important
            'twilio': 0.15,  # SMS is important
            'google_analytics': 0.1,  # Analytics is useful
            'default': 0.05
        }
        
        weight = provider_weights.get(provider, provider_weights['default'])
        
        return {
            'impact_multiplier': impact_multiplier,
            'weight': weight,
            'revenue_factor': impact_multiplier * weight
        }
    
    def calculate_cost_efficiency(self, provider: str) -> Dict[str, float]:
        """Calculate cost efficiency metrics"""
        total_requests = self.collector.counters.get(
            f"integration_requests_total{{provider={provider}}}", 0
        )
        total_cost = self.collector.gauges.get(
            f"integration_cost_total{{provider={provider}}}", 0
        )
        
        cost_per_request = total_cost / total_requests if total_requests > 0 else 0
        
        # Industry benchmarks (example values)
        benchmarks = {
            'stripe': 0.029,  # 2.9% + $0.30
            'sendgrid': 0.00095,  # $0.0095 per 100 emails
            'twilio': 0.0075,  # $0.0075 per SMS
            'default': 0.01
        }
        
        benchmark = benchmarks.get(provider, benchmarks['default'])
        efficiency = (benchmark / cost_per_request) if cost_per_request > 0 else 1.0
        
        return {
            'cost_per_request': cost_per_request,
            'benchmark': benchmark,
            'efficiency_ratio': efficiency,
            'efficiency_percentage': min(efficiency * 100, 200)  # Cap at 200%
        }
```

## Real-time Monitoring

### Live Metrics Dashboard

```python
import asyncio
import json
from typing import AsyncGenerator

class RealTimeMonitor:
    """Real-time metrics streaming"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector
        self.subscribers: List[asyncio.Queue] = []
        self.update_interval = 1.0  # seconds
    
    async def start_streaming(self):
        """Start real-time metrics streaming"""
        asyncio.create_task(self._stream_metrics())
    
    async def subscribe(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Subscribe to real-time metrics stream"""
        queue = asyncio.Queue()
        self.subscribers.append(queue)
        
        try:
            while True:
                metrics_update = await queue.get()
                yield metrics_update
        finally:
            self.subscribers.remove(queue)
    
    async def _stream_metrics(self):
        """Stream metrics to all subscribers"""
        while True:
            try:
                # Collect current metrics
                current_metrics = self._collect_current_metrics()
                
                # Send to all subscribers
                for queue in self.subscribers:
                    try:
                        queue.put_nowait(current_metrics)
                    except asyncio.QueueFull:
                        # Skip if queue is full
                        pass
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logging.error(f"Metrics streaming error: {e}")
                await asyncio.sleep(self.update_interval)
    
    def _collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current state of all metrics"""
        return {
            'timestamp': time.time(),
            'counters': dict(self.collector.counters),
            'gauges': dict(self.collector.gauges),
            'health_status': {
                provider: result.status.value
                for provider, result in health_monitor.health_results.items()
            },
            'summary': {
                'total_integrations': len(self.collector.gauges),
                'healthy_integrations': sum(
                    1 for result in health_monitor.health_results.values()
                    if result.status == HealthStatus.HEALTHY
                ),
                'total_requests_last_minute': self._get_requests_last_minute()
            }
        }
    
    def _get_requests_last_minute(self) -> int:
        """Get total requests in last minute"""
        # Implementation would track requests in time windows
        return sum(
            count for key, count in self.collector.counters.items()
            if 'requests_total' in key
        )
```

### WebSocket Monitoring API

```python
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()
real_time_monitor = RealTimeMonitor(metrics_collector)

@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics"""
    await websocket.accept()
    
    try:
        async for metrics in real_time_monitor.subscribe():
            await websocket.send_json(metrics)
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/metrics/dashboard")
async def metrics_dashboard():
    """Serve real-time metrics dashboard"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ainflue Integration Monitoring</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .metric-card { 
                border: 1px solid #ddd; 
                padding: 15px; 
                margin: 10px; 
                border-radius: 5px; 
                display: inline-block; 
                width: 300px; 
            }
            .healthy { border-color: #4CAF50; }
            .degraded { border-color: #FF9800; }
            .unhealthy { border-color: #f44336; }
        </style>
    </head>
    <body>
        <h1>Integration Monitoring Dashboard</h1>
        <div id="metrics-container"></div>
        
        <script>
            const ws = new WebSocket('ws://localhost:8000/ws/metrics');
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            function updateDashboard(metrics) {
                const container = document.getElementById('metrics-container');
                container.innerHTML = '';
                
                // Display health status
                for (const [provider, status] of Object.entries(metrics.health_status)) {
                    const card = document.createElement('div');
                    card.className = `metric-card ${status}`;
                    card.innerHTML = `
                        <h3>${provider}</h3>
                        <p>Status: ${status}</p>
                        <p>Requests: ${metrics.counters[provider + '_requests_total'] || 0}</p>
                    `;
                    container.appendChild(card);
                }
            }
        </script>
    </body>
    </html>
    """)
```

## Alerting System

### Alert Configuration

```python
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Any

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertChannel(Enum):
    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    description: str
    condition: Callable[[Dict[str, Any]], bool]
    severity: AlertSeverity
    channels: List[AlertChannel]
    threshold: float
    evaluation_window: int  # seconds
    cooldown_period: int = 300  # 5 minutes
    enabled: bool = True

class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.active_alerts: Dict[str, datetime] = {}
        self.notification_handlers = {
            AlertChannel.EMAIL: self._send_email_alert,
            AlertChannel.SLACK: self._send_slack_alert,
            AlertChannel.PAGERDUTY: self._send_pagerduty_alert,
            AlertChannel.WEBHOOK: self._send_webhook_alert
        }
    
    def add_rule(self, rule: AlertRule):
        """Add alert rule"""
        self.rules.append(rule)
    
    async def evaluate_alerts(self, metrics: Dict[str, Any]):
        """Evaluate all alert rules against current metrics"""
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            try:
                if rule.condition(metrics):
                    await self._trigger_alert(rule, metrics)
                else:
                    # Check if we should clear an active alert
                    if rule.name in self.active_alerts:
                        await self._clear_alert(rule)
                        
            except Exception as e:
                logging.error(f"Alert evaluation error for {rule.name}: {e}")
    
    async def _trigger_alert(self, rule: AlertRule, metrics: Dict[str, Any]):
        """Trigger an alert"""
        now = datetime.utcnow()
        
        # Check cooldown
        if rule.name in self.active_alerts:
            last_alert = self.active_alerts[rule.name]
            if (now - last_alert).total_seconds() < rule.cooldown_period:
                return
        
        # Record alert
        self.active_alerts[rule.name] = now
        
        # Send notifications
        for channel in rule.channels:
            handler = self.notification_handlers.get(channel)
            if handler:
                await handler(rule, metrics)
    
    async def _clear_alert(self, rule: AlertRule):
        """Clear an active alert"""
        if rule.name in self.active_alerts:
            del self.active_alerts[rule.name]
            
            # Send recovery notification
            for channel in rule.channels:
                handler = self.notification_handlers.get(channel)
                if handler:
                    await handler(rule, {}, is_recovery=True)
    
    async def _send_email_alert(self, rule: AlertRule, metrics: Dict[str, Any], is_recovery: bool = False):
        """Send email alert"""
        subject = f"{'RECOVERY' if is_recovery else 'ALERT'}: {rule.name}"
        body = f"""
        Alert: {rule.name}
        Severity: {rule.severity.value}
        Description: {rule.description}
        
        Current Metrics:
        {json.dumps(metrics, indent=2)}
        
        Time: {datetime.utcnow().isoformat()}
        """
        
        # Implementation would use email service
        logging.info(f"EMAIL ALERT: {subject}")
    
    async def _send_slack_alert(self, rule: AlertRule, metrics: Dict[str, Any], is_recovery: bool = False):
        """Send Slack alert"""
        color = "good" if is_recovery else "danger" if rule.severity == AlertSeverity.CRITICAL else "warning"
        
        message = {
            "attachments": [{
                "color": color,
                "title": f"{'RECOVERY' if is_recovery else 'ALERT'}: {rule.name}",
                "text": rule.description,
                "fields": [
                    {"title": "Severity", "value": rule.severity.value, "short": True},
                    {"title": "Time", "value": datetime.utcnow().isoformat(), "short": True}
                ]
            }]
        }
        
        # Implementation would use Slack webhook
        logging.info(f"SLACK ALERT: {rule.name}")

# Predefined alert rules
def setup_default_alerts(alert_manager: AlertManager):
    """Setup default alert rules"""
    
    # High error rate alert
    alert_manager.add_rule(AlertRule(
        name="high_error_rate",
        description="Integration error rate above threshold",
        condition=lambda m: any(
            m.get('gauges', {}).get(f'integration_error_rate{{provider={p}}}', 0) > 5.0
            for p in ['stripe', 'sendgrid', 'twilio']
        ),
        severity=AlertSeverity.WARNING,
        channels=[AlertChannel.SLACK, AlertChannel.EMAIL],
        threshold=5.0,
        evaluation_window=300
    ))
    
    # Integration down alert
    alert_manager.add_rule(AlertRule(
        name="integration_down",
        description="Critical integration is unhealthy",
        condition=lambda m: any(
            m.get('health_status', {}).get(p) == 'unhealthy'
            for p in ['stripe', 'sendgrid']  # Critical providers
        ),
        severity=AlertSeverity.CRITICAL,
        channels=[AlertChannel.PAGERDUTY, AlertChannel.SLACK, AlertChannel.EMAIL],
        threshold=1,
        evaluation_window=60
    ))
    
    # High response time alert
    alert_manager.add_rule(AlertRule(
        name="high_response_time",
        description="Integration response time above threshold",
        condition=lambda m: any(
            m.get('gauges', {}).get(f'integration_response_time_p95{{provider={p}}}', 0) > 5000
            for p in m.get('health_status', {}).keys()
        ),
        severity=AlertSeverity.WARNING,
        channels=[AlertChannel.SLACK],
        threshold=5000,  # 5 seconds
        evaluation_window=600
    ))
```

## Performance Tracking

### SLA Monitoring

```python
class SLAMonitor:
    """Service Level Agreement monitoring"""
    
    def __init__(self):
        self.sla_targets = {
            'availability': 99.9,  # 99.9% uptime
            'response_time_p95': 2000,  # 2 seconds for 95th percentile
            'error_rate': 1.0,  # Max 1% error rate
            'success_rate': 99.0  # Min 99% success rate
        }
        
        self.monthly_sla_status = {}
    
    def calculate_sla_compliance(self, provider: str, period: str = 'monthly') -> Dict[str, Any]:
        """Calculate SLA compliance for provider"""
        metrics = self._get_period_metrics(provider, period)
        
        compliance = {}
        for sla_metric, target in self.sla_targets.items():
            actual_value = metrics.get(sla_metric, 0)
            
            if sla_metric in ['availability', 'success_rate']:
                # Higher is better
                compliance[sla_metric] = {
                    'target': target,
                    'actual': actual_value,
                    'compliant': actual_value >= target,
                    'difference': actual_value - target
                }
            else:
                # Lower is better
                compliance[sla_metric] = {
                    'target': target,
                    'actual': actual_value,
                    'compliant': actual_value <= target,
                    'difference': target - actual_value
                }
        
        # Overall compliance
        overall_compliant = all(c['compliant'] for c in compliance.values())
        
        return {
            'provider': provider,
            'period': period,
            'overall_compliant': overall_compliant,
            'metrics': compliance,
            'sla_score': self._calculate_sla_score(compliance)
        }
    
    def _calculate_sla_score(self, compliance: Dict[str, Any]) -> float:
        """Calculate overall SLA score (0-100)"""
        scores = []
        
        for metric, data in compliance.items():
            if data['compliant']:
                scores.append(100.0)
            else:
                # Calculate partial score based on how far off target
                if metric in ['availability', 'success_rate']:
                    # For percentage metrics
                    penalty = abs(data['difference']) * 10  # 10x penalty
                else:
                    # For time/rate metrics
                    penalty = (abs(data['difference']) / data['target']) * 100
                
                scores.append(max(0, 100 - penalty))
        
        return sum(scores) / len(scores) if scores else 0.0
```

### Performance Trending

```python
class PerformanceTrends:
    """Track performance trends over time"""
    
    def __init__(self):
        self.historical_data: Dict[str, List[Dict[str, Any]]] = {}
    
    def record_performance_snapshot(self, provider: str, metrics: Dict[str, Any]):
        """Record performance snapshot"""
        if provider not in self.historical_data:
            self.historical_data[provider] = []
        
        snapshot = {
            'timestamp': datetime.utcnow(),
            'metrics': metrics.copy()
        }
        
        self.historical_data[provider].append(snapshot)
        
        # Keep only last 30 days
        cutoff = datetime.utcnow() - timedelta(days=30)
        self.historical_data[provider] = [
            s for s in self.historical_data[provider]
            if s['timestamp'] > cutoff
        ]
    
    def analyze_trends(self, provider: str, metric: str, period_days: int = 7) -> Dict[str, Any]:
        """Analyze trends for specific metric"""
        if provider not in self.historical_data:
            return {'error': 'No data available'}
        
        cutoff = datetime.utcnow() - timedelta(days=period_days)
        recent_data = [
            s for s in self.historical_data[provider]
            if s['timestamp'] > cutoff
        ]
        
        if len(recent_data) < 2:
            return {'error': 'Insufficient data for trend analysis'}
        
        values = [s['metrics'].get(metric, 0) for s in recent_data]
        timestamps = [s['timestamp'] for s in recent_data]
        
        # Calculate trend
        trend_direction = self._calculate_trend_direction(values)
        trend_strength = self._calculate_trend_strength(values)
        
        return {
            'provider': provider,
            'metric': metric,
            'period_days': period_days,
            'data_points': len(values),
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            'current_value': values[-1] if values else 0,
            'average_value': sum(values) / len(values) if values else 0,
            'min_value': min(values) if values else 0,
            'max_value': max(values) if values else 0,
            'volatility': self._calculate_volatility(values)
        }
    
    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'unknown'
        
        # Simple linear trend
        increases = 0
        decreases = 0
        
        for i in range(1, len(values)):
            if values[i] > values[i-1]:
                increases += 1
            elif values[i] < values[i-1]:
                decreases += 1
        
        if increases > decreases:
            return 'increasing'
        elif decreases > increases:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_trend_strength(self, values: List[float]) -> float:
        """Calculate trend strength (0-1)"""
        if len(values) < 2:
            return 0.0
        
        # Calculate correlation coefficient with time
        n = len(values)
        x = list(range(n))
        y = values
        
        # Simple correlation calculation
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        x_var = sum((x[i] - x_mean) ** 2 for i in range(n))
        y_var = sum((y[i] - y_mean) ** 2 for i in range(n))
        
        if x_var == 0 or y_var == 0:
            return 0.0
        
        correlation = numerator / (x_var * y_var) ** 0.5
        return abs(correlation)
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (standard deviation)"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
```

---

## Dashboard Configuration

### Grafana Integration

```json
{
  "dashboard": {
    "title": "Ainflue Integration Monitoring",
    "panels": [
      {
        "title": "Integration Health Status",
        "type": "stat",
        "targets": [
          {
            "expr": "integration_health_status",
            "legendFormat": "{{provider}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 0.5},
                {"color": "green", "value": 1}
              ]
            }
          }
        }
      },
      {
        "title": "Response Time (95th Percentile)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "integration_response_time_p95",
            "legendFormat": "{{provider}}"
          }
        ]
      },
      {
        "title": "Success Rate",
        "type": "timeseries",
        "targets": [
          {
            "expr": "integration_success_rate",
            "legendFormat": "{{provider}}"
          }
        ]
      },
      {
        "title": "Request Volume",
        "type": "timeseries",
        "targets": [
          {
            "expr": "rate(integration_requests_total[5m])",
            "legendFormat": "{{provider}}"
          }
        ]
      }
    ]
  }
}
```

---

**© 2025 Fahed Mlaiel. All rights reserved.**  
**Contact**: mlaiel@live.de  
**Legal**: This documentation is part of the Ainflue platform and is protected by international copyright law.