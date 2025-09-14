"""
Service Monitor module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Service Monitor - Enterprise Microservice Health Monitoring
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Advanced service monitoring for Ainflue Platform:
- Real-time microservice health monitoring
- Service discovery and registration
- Performance metrics collection
- Automated alerting and escalation
- Health dashboard and reporting
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
try:
    import aiohttp
    import psutil
    HAS_MONITORING_LIBS = True
except ImportError:
    HAS_MONITORING_LIBS = False
    aiohttp = None
    psutil = None
import subprocess
from dataclasses import dataclass, asdict
from enum import Enum

# Configure enterprise logging
log_dir = '/tmp/ainflue_logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/service_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """ServiceStatus class implementation"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DOWN = "down"
    UNKNOWN = "unknown"

class AlertLevel(Enum):
    """AlertLevel class implementation"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    name: str
    url: str
    method: str = "GET"
    expected_status: int = 200
    timeout: int = 10
    headers: Dict[str, str] = None
    auth: Dict[str, str] = None

@dataclass
class ServiceMetrics:
    """Service health metrics"""
    service_name: str
    timestamp: datetime
    status: ServiceStatus
    response_time: float
    cpu_usage: float
    memory_usage: float
    error_rate: float
    throughput: float
    custom_metrics: Dict[str, Any] = None

@dataclass
class Alert:
    """Service alert"""
    alert_id: str
    service_name: str
    level: AlertLevel
    message: str
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None

class ServiceMonitor:
    """
    Enterprise microservice health monitoring system
    
    Features:
    - Continuous health checks for all services
    - Performance metrics collection
    - Automated alerting and escalation
    - Service discovery and registration
    - Real-time dashboard data
    """
    
    def __init__(self, config_path -> None: str = "/etc/ainflue/services.json") -> None:
        self.config_path = config_path
        self.services: Dict[str, ServiceEndpoint] = {}
        self.metrics_history: List[ServiceMetrics] = []
        self.active_alerts: List[Alert] = []
        self.service_registry: Dict[str, Dict] = {}
        
    async def load_service_configuration(self) -> None:
        """Load service monitoring configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            for service_config in config.get('services', []):
                endpoint = ServiceEndpoint(**service_config)
                self.services[endpoint.name] = endpoint
            
            logger.info(f"Loaded {len(self.services)} services for monitoring")
            
        except FileNotFoundError:
            # Create default configuration for Ainflue services
            default_services = [
                {
                    "name": "api-gateway",
                    "url": "http://localhost:8080/health",
                    "timeout": 5
                },
                {
                    "name": "auth-service", 
                    "url": "http://localhost:8081/health",
                    "timeout": 5
                },
                {
                    "name": "content-service",
                    "url": "http://localhost:8082/health",
                    "timeout": 10
                },
                {
                    "name": "ai-processing-service",
                    "url": "http://localhost:8083/health",
                    "timeout": 30
                },
                {
                    "name": "media-service",
                    "url": "http://localhost:8084/health",
                    "timeout": 15
                },
                {
                    "name": "notification-service",
                    "url": "http://localhost:8085/health",
                    "timeout": 5
                },
                {
                    "name": "analytics-service",
                    "url": "http://localhost:8086/health",
                    "timeout": 10
                },
                {
                    "name": "payment-service",
                    "url": "http://localhost:8087/health",
                    "timeout": 15
                },
                {
                    "name": "collaboration-service",
                    "url": "http://localhost:8088/health",
                    "timeout": 10
                },
                {
                    "name": "seo-service",
                    "url": "http://localhost:8089/health",
                    "timeout": 10
                }
            ]
            
            for service_config in default_services:
                endpoint = ServiceEndpoint(**service_config)
                self.services[endpoint.name] = endpoint
            
            logger.info("Created default service configuration")
    
    async def check_service_health(self, service: ServiceEndpoint) -> ServiceMetrics:
        """Check health of a single service"""
        start_time = time.time()
        
        if not HAS_MONITORING_LIBS:
            # Fallback implementation without aiohttp
            logger.warning("Monitoring libraries not available, using fallback")
            return ServiceMetrics(
                service_name=service.name,
                timestamp=datetime.now(),
                status=ServiceStatus.UNKNOWN,
                response_time=0.0,
                cpu_usage=0.0,
                memory_usage=0.0,
                error_rate=0.0,
                throughput=0.0
            )
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = service.headers or {}
                auth = None
                
                if service.auth:
                    auth = aiohttp.BasicAuth(
                        service.auth.get('username'),
                        service.auth.get('password')
                    )
                
                async with session.request(
                    service.method,
                    service.url,
                    headers=headers,
                    auth=auth,
                    timeout=aiohttp.ClientTimeout(total=service.timeout)
                ) as response:
                    response_time = time.time() - start_time
                    
                    # Determine service status
                    if response.status == service.expected_status:
                        status = ServiceStatus.HEALTHY
                    elif 200 <= response.status < 300:
                        status = ServiceStatus.DEGRADED
                    else:
                        status = ServiceStatus.UNHEALTHY
                    
                    # Try to get additional metrics from response
                    custom_metrics = {}
                    try:
                        if response.content_type == 'application/json':
                            data = await response.json()
                            custom_metrics = data.get('metrics', {})
                    except:
                        pass
                    
                    # Get system metrics
                    cpu_usage, memory_usage = await self._get_system_metrics(service.name)
                    
                    metrics = ServiceMetrics(
                        service_name=service.name,
                        timestamp=datetime.now(),
                        status=status,
                        response_time=response_time * 1000,  # Convert to ms
                        cpu_usage=cpu_usage,
                        memory_usage=memory_usage,
                        error_rate=0.0,  # Calculate from history
                        throughput=0.0,  # Calculate from metrics
                        custom_metrics=custom_metrics
                    )
                    
                    return metrics
                    
        except asyncio.TimeoutError:
            logger.warning(f"Health check timeout for {service.name}")
            return ServiceMetrics(
                service_name=service.name,
                timestamp=datetime.now(),
                status=ServiceStatus.DOWN,
                response_time=service.timeout * 1000,
                cpu_usage=0.0,
                memory_usage=0.0,
                error_rate=1.0,
                throughput=0.0
            )
            
        except Exception as e:
            logger.error(f"Health check failed for {service.name}: {e}")
            return ServiceMetrics(
                service_name=service.name,
                timestamp=datetime.now(),
                status=ServiceStatus.UNKNOWN,
                response_time=0.0,
                cpu_usage=0.0,
                memory_usage=0.0,
                error_rate=1.0,
                throughput=0.0
            )
    
    async def _get_system_metrics(self, service_name: str) -> tuple:
        """Get system-level metrics for service"""
        try:
            # Try to find process by service name
            cpu_usage = 0.0
            memory_usage = 0.0
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if service_name.lower() in ' '.join(proc.info['cmdline']).lower():
                        proc_obj = psutil.Process(proc.info['pid'])
                        cpu_usage = proc_obj.cpu_percent()
                        memory_usage = proc_obj.memory_percent()
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return cpu_usage, memory_usage
            
        except Exception as e:
            logger.debug(f"System metrics collection failed for {service_name}: {e}")
            return 0.0, 0.0
    
    async def monitor_all_services(self, interval -> None: int = 30, duration -> None: int = 3600) -> None:
        """Monitor all services continuously"""
        logger.info(f"Starting service monitoring (interval: {interval}s, duration: {duration}s)")
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                # Check all services concurrently
                tasks = []
                for service in self.services.values():
                    task = asyncio.create_task(self.check_service_health(service))
                    tasks.append(task)
                
                metrics_batch = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for metrics in metrics_batch:
                    if isinstance(metrics, ServiceMetrics):
                        self.metrics_history.append(metrics)
                        
                        # Check for alerts
                        await self._check_alert_conditions(metrics)
                        
                        logger.info(
                            f"{metrics.service_name}: {metrics.status.value} "
                            f"({metrics.response_time:.1f}ms)"
                        )
                    elif isinstance(metrics, Exception):
                        logger.error(f"Service check failed: {metrics}")
                
                # Clean up old metrics (keep last 24 hours)
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.metrics_history = [
                    m for m in self.metrics_history 
                    if m.timestamp > cutoff_time
                ]
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Monitoring cycle failed: {e}")
                await asyncio.sleep(interval)
        
        logger.info("Service monitoring completed")
    
    async def _check_alert_conditions(self, metrics -> None: ServiceMetrics) -> None:
        """Check if metrics trigger any alerts"""
        alerts_to_create = []
        
        # Service down/unhealthy
        if metrics.status in [ServiceStatus.DOWN, ServiceStatus.UNHEALTHY]:
            alerts_to_create.append({
                'level': AlertLevel.CRITICAL,
                'message': f"Service {metrics.service_name} is {metrics.status.value}"
            })
        
        # High response time
        if metrics.response_time > 5000:  # 5 seconds
            alerts_to_create.append({
                'level': AlertLevel.WARNING,
                'message': f"High response time for {metrics.service_name}: {metrics.response_time:.1f}ms"
            })
        
        # High CPU usage
        if metrics.cpu_usage > 80:
            alerts_to_create.append({
                'level': AlertLevel.WARNING,
                'message': f"High CPU usage for {metrics.service_name}: {metrics.cpu_usage:.1f}%"
            })
        
        # High memory usage
        if metrics.memory_usage > 90:
            alerts_to_create.append({
                'level': AlertLevel.CRITICAL,
                'message': f"High memory usage for {metrics.service_name}: {metrics.memory_usage:.1f}%"
            })
        
        # Create alerts
        for alert_info in alerts_to_create:
            await self._create_alert(
                metrics.service_name,
                alert_info['level'],
                alert_info['message']
            )
    
    async def _create_alert(self, service_name -> None: str, level -> None: AlertLevel, message -> None: str) -> None:
        """Create a new alert"""
        # Check if similar alert already exists
        for alert in self.active_alerts:
            if (alert.service_name == service_name and 
                alert.message == message and 
                not alert.resolved):
                return  # Alert already exists
        
        alert = Alert(
            alert_id=f"alert_{service_name}_{int(time.time())}",
            service_name=service_name,
            level=level,
            message=message,
            timestamp=datetime.now()
        )
        
        self.active_alerts.append(alert)
        
        logger.warning(f"ALERT [{level.value.upper()}] {service_name}: {message}")
        
        # Send notifications (implementation would include email/Slack/SMS)
        await self._send_alert_notification(alert)
    
    async def _send_alert_notification(self, alert -> None: Alert) -> None:
        """Send alert notification"""
        # Implementation would send to configured channels
        logger.info(f"Alert notification sent: {alert.alert_id}")
    
    async def resolve_alert(self, alert_id -> None: str) -> None:
        """Resolve an active alert"""
        for alert in self.active_alerts:
            if alert.alert_id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolution_time = datetime.now()
                logger.info(f"Alert resolved: {alert_id}")
                return True
        return False
    
    async def get_service_status_summary(self) -> Dict[str, Any]:
        """Get current status summary for all services"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_services': len(self.services),
            'healthy_services': 0,
            'degraded_services': 0,
            'unhealthy_services': 0,
            'down_services': 0,
            'active_alerts': len([a for a in self.active_alerts if not a.resolved]),
            'services': {}
        }
        
        # Get latest metrics for each service
        for service_name in self.services.keys():
            latest_metrics = None
            for metrics in reversed(self.metrics_history):
                if metrics.service_name == service_name:
                    latest_metrics = metrics
                    break
            
            if latest_metrics:
                summary['services'][service_name] = {
                    'status': latest_metrics.status.value,
                    'response_time': latest_metrics.response_time,
                    'cpu_usage': latest_metrics.cpu_usage,
                    'memory_usage': latest_metrics.memory_usage,
                    'last_check': latest_metrics.timestamp.isoformat()
                }
                
                # Update counters
                if latest_metrics.status == ServiceStatus.HEALTHY:
                    summary['healthy_services'] += 1
                elif latest_metrics.status == ServiceStatus.DEGRADED:
                    summary['degraded_services'] += 1
                elif latest_metrics.status == ServiceStatus.UNHEALTHY:
                    summary['unhealthy_services'] += 1
                elif latest_metrics.status == ServiceStatus.DOWN:
                    summary['down_services'] += 1
            else:
                summary['services'][service_name] = {
                    'status': 'unknown',
                    'message': 'No metrics available'
                }
        
        return summary
    
    async def get_service_metrics_history(self, service_name: str, 
                                        hours: int = 24) -> List[ServiceMetrics]:
        """Get metrics history for a specific service"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            metrics for metrics in self.metrics_history
            if (metrics.service_name == service_name and 
                metrics.timestamp > cutoff_time)
        ]
    
    async def discover_services(self) -> None:
        """Discover services automatically"""
        logger.info("Starting service discovery")
        
        # Check for common service ports
        service_ports = {
            8080: "api-gateway",
            8081: "auth-service",
            8082: "content-service",
            8083: "ai-processing-service",
            8084: "media-service",
            8085: "notification-service",
            8086: "analytics-service",
            8087: "payment-service",
            8088: "collaboration-service",
            8089: "seo-service"
        }
        
        discovered_services = {}
        
        for port, service_name in service_ports.items():
            try:
                # Try to connect to port
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    discovered_services[service_name] = {
                        'name': service_name,
                        'url': f'http://localhost:{port}/health',
                        'port': port,
                        'discovered_at': datetime.now().isoformat()
                    }
                    
                    # Add to service registry if not already monitored
                    if service_name not in self.services:
                        endpoint = ServiceEndpoint(
                            name=service_name,
                            url=f'http://localhost:{port}/health'
                        )
                        self.services[service_name] = endpoint
                        logger.info(f"Discovered service: {service_name} on port {port}")
                        
            except Exception as e:
                logger.debug(f"Service discovery failed for port {port}: {e}")
        
        self.service_registry.update(discovered_services)
        logger.info(f"Service discovery completed. Found {len(discovered_services)} services")
        
        return discovered_services
    
    async def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        report = {
            'report_id': f"health_report_{int(time.time())}",
            'timestamp': datetime.now().isoformat(),
            'summary': await self.get_service_status_summary(),
            'alerts': {
                'active': [asdict(alert) for alert in self.active_alerts if not alert.resolved],
                'resolved_last_24h': [
                    asdict(alert) for alert in self.active_alerts
                    if (alert.resolved and alert.resolution_time and 
                        alert.resolution_time > datetime.now() - timedelta(hours=24))
                ]
            },
            'performance_trends': {},
            'recommendations': []
        }
        
        # Add performance trends for each service
        for service_name in self.services.keys():
            recent_metrics = await self.get_service_metrics_history(service_name, 24)
            
            if recent_metrics:
                avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
                avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
                avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
                
                report['performance_trends'][service_name] = {
                    'avg_response_time_24h': avg_response_time,
                    'avg_cpu_usage_24h': avg_cpu,
                    'avg_memory_usage_24h': avg_memory,
                    'total_checks': len(recent_metrics),
                    'uptime_percentage': len([m for m in recent_metrics 
                                            if m.status == ServiceStatus.HEALTHY]) / len(recent_metrics) * 100
                }
        
        # Generate recommendations
        if report['summary']['down_services'] > 0:
            report['recommendations'].append("Investigate and restart down services immediately")
        
        if report['summary']['active_alerts'] > 5:
            report['recommendations'].append("High number of active alerts - review system capacity")
        
        for service_name, trends in report['performance_trends'].items():
            if trends['avg_response_time_24h'] > 1000:
                report['recommendations'].append(f"Optimize response time for {service_name}")
            
            if trends['uptime_percentage'] < 99:
                report['recommendations'].append(f"Improve reliability for {service_name}")
        
        return report

async def main() -> None:
    """CLI entry point for service monitor"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ainflue Service Monitor')
    parser.add_argument('--monitor', action='store_true', help='Start monitoring')
    parser.add_argument('--duration', type=int, default=3600, help='Monitoring duration (seconds)')
    parser.add_argument('--interval', type=int, default=30, help='Check interval (seconds)')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--discover', action='store_true', help='Discover services')
    parser.add_argument('--report', action='store_true', help='Generate health report')
    parser.add_argument('--config', default='/etc/ainflue/services.json', help='Configuration file')
    
    args = parser.parse_args()
    
    monitor = ServiceMonitor(args.config)
    await monitor.load_service_configuration()
    
    try:
        if args.discover:
            services = await monitor.discover_services()
            print(f"Discovered {len(services)} services")
            for name, info in services.items():
                print(f"  {name}: {info['url']}")
        
        if args.monitor:
            await monitor.monitor_all_services(args.interval, args.duration)
        
        if args.status:
            summary = await monitor.get_service_status_summary()
            print(json.dumps(summary, indent=2, default=str))
        
        if args.report:
            report = await monitor.generate_health_report()
            print(json.dumps(report, indent=2, default=str))
    
    except Exception as e:
        logger.error(f"Service monitor failed: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())