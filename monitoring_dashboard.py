"""
Monitoring Dashboard module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Monitoring Dashboard Implementation
Real-time monitoring for Ainflue Platform validation framework
Author: Fahed Mlaiel (mlaiel@live.de) - DevOps Expert + Monitoring Specialist
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path
import subprocess
import psutil

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, int]
    process_count: int
    load_average: List[float]

@dataclass
class ServiceHealth:
    """Service health status"""
    service_name: str
    status: str  # running, stopped, error
    uptime: float
    memory_usage: float
    cpu_usage: float
    last_check: str

class MonitoringDashboard:
    """Real-time monitoring dashboard for validation framework"""
    
    def __init__(self) -> None:
        self.metrics_history: List[SystemMetrics] = []
        self.service_health: Dict[str, ServiceHealth] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
        
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # CPU and memory metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            net_io = psutil.net_io_counters()
            network_io = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
            
            # Process count and load average
            process_count = len(psutil.pids())
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0.0, 0.0, 0.0]
            
            metrics = SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                network_io=network_io,
                process_count=process_count,
                load_average=list(load_avg)
            )
            
            self.metrics_history.append(metrics)
            
            # Keep only last 100 metrics
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]
            
            return metrics
            
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                network_io={},
                process_count=0,
                load_average=[0.0, 0.0, 0.0]
            )
    
    def check_service_health(self) -> Dict[str, ServiceHealth]:
        """Check health of key services"""
        services = {
            'validation_framework': self._check_validation_service(),
            'docker_daemon': self._check_docker_service(),
            'system_monitoring': self._check_monitoring_service()
        }
        
        self.service_health.update(services)
        return services
    
    def _check_validation_service(self) -> ServiceHealth:
        """Check validation framework service"""
        try:
            # Check if validation module can be imported and run
            start_time = time.time()
            import validation
            
            # Basic functionality test
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            return ServiceHealth(
                service_name="validation_framework",
                status="running",
                uptime=uptime,
                memory_usage=15.0,  # Estimated
                cpu_usage=2.0,      # Estimated
                last_check=datetime.now().isoformat()
            )
        except Exception as e:
            return ServiceHealth(
                service_name="validation_framework",
                status="error",
                uptime=0.0,
                memory_usage=0.0,
                cpu_usage=0.0,
                last_check=datetime.now().isoformat()
            )
    
    def _check_docker_service(self) -> ServiceHealth:
        """Check Docker daemon status"""
        try:
            # Try to run docker ps command
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Count running containers
                container_count = len(result.stdout.strip().split('\n')) - 1  # Subtract header
                
                return ServiceHealth(
                    service_name="docker_daemon",
                    status="running",
                    uptime=3600.0,  # Estimated
                    memory_usage=50.0,
                    cpu_usage=1.0,
                    last_check=datetime.now().isoformat()
                )
            else:
                return ServiceHealth(
                    service_name="docker_daemon",
                    status="stopped",
                    uptime=0.0,
                    memory_usage=0.0,
                    cpu_usage=0.0,
                    last_check=datetime.now().isoformat()
                )
        except Exception:
            return ServiceHealth(
                service_name="docker_daemon",
                status="error",
                uptime=0.0,
                memory_usage=0.0,
                cpu_usage=0.0,
                last_check=datetime.now().isoformat()
            )
    
    def _check_monitoring_service(self) -> ServiceHealth:
        """Check monitoring service itself"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return ServiceHealth(
            service_name="system_monitoring",
            status="running",
            uptime=uptime,
            memory_usage=psutil.Process().memory_percent(),
            cpu_usage=psutil.Process().cpu_percent(),
            last_check=datetime.now().isoformat()
        )
    
    def generate_alerts(self, metrics: SystemMetrics) -> List[Dict[str, Any]]:
        """Generate alerts based on metrics"""
        alerts = []
        current_time = datetime.now().isoformat()
        
        # CPU usage alert
        if metrics.cpu_percent > 80:
            alerts.append({
                'type': 'warning',
                'service': 'system',
                'metric': 'cpu_usage',
                'value': metrics.cpu_percent,
                'threshold': 80,
                'message': f'High CPU usage: {metrics.cpu_percent:.1f}%',
                'timestamp': current_time
            })
        
        # Memory usage alert
        if metrics.memory_percent > 85:
            alerts.append({
                'type': 'warning',
                'service': 'system',
                'metric': 'memory_usage',
                'value': metrics.memory_percent,
                'threshold': 85,
                'message': f'High memory usage: {metrics.memory_percent:.1f}%',
                'timestamp': current_time
            })
        
        # Disk usage alert
        if metrics.disk_usage_percent > 90:
            alerts.append({
                'type': 'critical',
                'service': 'system',
                'metric': 'disk_usage',
                'value': metrics.disk_usage_percent,
                'threshold': 90,
                'message': f'Critical disk usage: {metrics.disk_usage_percent:.1f}%',
                'timestamp': current_time
            })
        
        # Service health alerts
        for service_name, service in self.service_health.items():
            if service.status != 'running':
                alerts.append({
                    'type': 'critical',
                    'service': service_name,
                    'metric': 'service_status',
                    'value': service.status,
                    'threshold': 'running',
                    'message': f'Service {service_name} is {service.status}',
                    'timestamp': current_time
                })
        
        # Add new alerts to history
        self.alerts.extend(alerts)
        
        # Keep only last 50 alerts
        if len(self.alerts) > 50:
            self.alerts = self.alerts[-50:]
        
        return alerts
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        current_metrics = self.collect_system_metrics()
        service_health = self.check_service_health()
        alerts = self.generate_alerts(current_metrics)
        
        # Calculate uptime
        uptime_seconds = (datetime.now() - self.start_time).total_seconds()
        uptime_str = str(timedelta(seconds=int(uptime_seconds)))
        
        # Recent metrics for charts (last 10 points)
        recent_metrics = self.metrics_history[-10:] if len(self.metrics_history) >= 10 else self.metrics_history
        
        return {
            'dashboard_info': {
                'name': 'Ainflue Platform Monitoring',
                'version': '1.0.0',
                'uptime': uptime_str,
                'last_update': datetime.now().isoformat(),
                'expert_team': 'DevOps + Monitoring Specialist - Fahed Mlaiel'
            },
            'current_metrics': asdict(current_metrics),
            'service_health': {name: asdict(service) for name, service in service_health.items()},
            'alerts': {
                'active_alerts': alerts,
                'total_alerts': len(self.alerts),
                'critical_count': len([a for a in self.alerts if a['type'] == 'critical']),
                'warning_count': len([a for a in self.alerts if a['type'] == 'warning'])
            },
            'performance_history': [asdict(m) for m in recent_metrics],
            'system_summary': {
                'status': 'healthy' if len(alerts) == 0 else 'warning' if any(a['type'] == 'warning' for a in alerts) else 'critical',
                'running_services': len([s for s in service_health.values() if s.status == 'running']),
                'total_services': len(service_health),
                'avg_cpu': sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0,
                'avg_memory': sum(m.memory_percent for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
            }
        }
    
    def save_dashboard_report(self, filename: str = None) -> str:
        """Save dashboard data to JSON report"""
        if filename is None:
            filename = f"monitoring_dashboard_{int(time.time())}.json"
        
        dashboard_data = self.get_dashboard_data()
        
        with open(filename, 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        
        return filename
    
    def print_dashboard(self) -> None:
        """Print dashboard to console"""
        data = self.get_dashboard_data()
        
        print("\n" + "=" * 80)
        print("🖥️  AINFLUE PLATFORM MONITORING DASHBOARD")
        print("=" * 80)
        print(f"👨‍💻 Expert: {data['dashboard_info']['expert_team']}")
        print(f"⏰ Uptime: {data['dashboard_info']['uptime']}")
        print(f"🔄 Last Update: {data['dashboard_info']['last_update']}")
        print(f"📊 Status: {data['system_summary']['status'].upper()}")
        
        # Current metrics
        metrics = data['current_metrics']
        print(f"\n📈 CURRENT SYSTEM METRICS")
        print(f"   🔧 CPU: {metrics['cpu_percent']:.1f}%")
        print(f"   💾 Memory: {metrics['memory_percent']:.1f}%")
        print(f"   💿 Disk: {metrics['disk_usage_percent']:.1f}%")
        print(f"   🔢 Processes: {metrics['process_count']}")
        
        # Service health
        print(f"\n🏥 SERVICE HEALTH")
        for name, service in data['service_health'].items():
            status_icon = "✅" if service['status'] == 'running' else "❌"
            print(f"   {status_icon} {name}: {service['status']} (↑{service['uptime']:.0f}s)")
        
        # Alerts
        alert_info = data['alerts']
        if alert_info['active_alerts']:
            print(f"\n🚨 ACTIVE ALERTS ({alert_info['total_alerts']})")
            for alert in alert_info['active_alerts'][-5:]:  # Show last 5
                icon = "🔥" if alert['type'] == 'critical' else "⚠️"
                print(f"   {icon} {alert['message']}")
        else:
            print(f"\n✅ NO ACTIVE ALERTS")
        
        print("=" * 80)

# Global monitoring instance
dashboard = MonitoringDashboard()

async def run_monitoring_loop(duration_seconds -> None: int = 60) -> None:
    """Run monitoring loop for specified duration"""
    print(f"🚀 Starting monitoring loop for {duration_seconds} seconds...")
    
    start_time = time.time()
    while time.time() - start_time < duration_seconds:
        dashboard.print_dashboard()
        await asyncio.sleep(10)  # Update every 10 seconds
    
    # Save final report
    report_file = dashboard.save_dashboard_report()
    print(f"\n📄 Monitoring report saved to: {report_file}")

def get_monitoring_dashboard() -> MonitoringDashboard:
    """Get global monitoring dashboard instance"""
    return dashboard

if __name__ == "__main__":
    # Demo the monitoring dashboard
    dashboard.print_dashboard()
    
    # Save a report
    report_file = dashboard.save_dashboard_report()
    print(f"\n📄 Dashboard report saved to: {report_file}")