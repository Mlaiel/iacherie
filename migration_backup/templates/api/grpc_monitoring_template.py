#!/usr/bin/env python3
"""
⚡ Enterprise gRPC Monitoring Template - IA Chéries API Templates
Advanced production-ready gRPC monitoring and observability system

⚠️ PROTECTION INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Code propriétaire de Fahed Mlaiel
Utilisation commerciale INTERDITE sans autorisation écrite
Reverse engineering STRICTEMENT INTERDIT
Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence  
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import time
import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import grpc
from grpc import StatusCode
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary
import structlog
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor
import json


class GRPCMonitoringTemplate:
    """
    🚀 Enterprise gRPC Monitoring Template
    
    Fonctionnalités:
    - ✅ Métriques Prometheus intégrées
    - ✅ Monitoring performance en temps réel
    - ✅ Health checks automatisés
    - ✅ Alerting intelligent
    - ✅ Dashboards observabilité
    - ✅ SLA monitoring avancé
    - ✅ Error tracking détaillé
    - ✅ Resource monitoring système
    """
    
    def __init__(self, service_name: str = "ainflue_grpc_service"):
        self.service_name = service_name
        self.logger = structlog.get_logger(__name__)
        
        # Prometheus metrics
        self._setup_prometheus_metrics()
        
        # Performance tracking
        self.request_times = deque(maxlen=1000)
        self.error_rates = defaultdict(int)
        self.active_connections = 0
        
        # Health check system
        self.health_checks = {}
        self.health_status = {}
        
        # SLA tracking
        self.sla_config = {
            'response_time_p99': 1.0,  # 1 second
            'error_rate_threshold': 0.01,  # 1%
            'availability_target': 0.999  # 99.9%
        }
        
        # Resource monitoring
        self.resource_monitor = ResourceMonitor()
        
        # Alerting system
        self.alerting = AlertingSystem(service_name)
    
    def _setup_prometheus_metrics(self):
        """Initialise les métriques Prometheus"""
        self.metrics = {
            # Request metrics
            'requests_total': Counter(
                'grpc_requests_total',
                'Total gRPC requests',
                ['method', 'status', 'service']
            ),
            
            'request_duration': Histogram(
                'grpc_request_duration_seconds',
                'gRPC request duration',
                ['method', 'service'],
                buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
            ),
            
            'request_size': Histogram(
                'grpc_request_size_bytes',
                'gRPC request size',
                ['method', 'service']
            ),
            
            'response_size': Histogram(
                'grpc_response_size_bytes',
                'gRPC response size',
                ['method', 'service']
            ),
            
            # Connection metrics
            'active_connections': Gauge(
                'grpc_active_connections',
                'Active gRPC connections',
                ['service']
            ),
            
            'connection_duration': Histogram(
                'grpc_connection_duration_seconds',
                'gRPC connection duration',
                ['service']
            ),
            
            # Error metrics
            'errors_total': Counter(
                'grpc_errors_total',
                'Total gRPC errors',
                ['method', 'status_code', 'service']
            ),
            
            # Health metrics
            'health_check_status': Gauge(
                'grpc_health_check_status',
                'Health check status (1=healthy, 0=unhealthy)',
                ['check_name', 'service']
            ),
            
            # SLA metrics
            'sla_violations': Counter(
                'grpc_sla_violations_total',
                'SLA violations',
                ['violation_type', 'service']
            ),
            
            # Resource metrics
            'memory_usage': Gauge(
                'grpc_memory_usage_bytes',
                'Memory usage',
                ['service']
            ),
            
            'cpu_usage': Gauge(
                'grpc_cpu_usage_percent',
                'CPU usage percentage',
                ['service']
            )
        }
    
    def create_monitoring_interceptor(self):
        """Crée un intercepteur pour le monitoring automatique"""
        
        class MonitoringInterceptor(grpc.ServerInterceptor):
            def __init__(self, monitor: 'GRPCMonitoringTemplate'):
                self.monitor = monitor
            
            def intercept_service(self, continuation, handler_call_details):
                def wrapper(request, context):
                    start_time = time.time()
                    method = handler_call_details.method
                    
                    try:
                        # Métriques pré-requête
                        self.monitor.metrics['requests_total'].labels(
                            method=method,
                            status='started',
                            service=self.monitor.service_name
                        ).inc()
                        
                        # Taille de la requête
                        if hasattr(request, 'SerializeToString'):
                            request_size = len(request.SerializeToString())
                            self.monitor.metrics['request_size'].labels(
                                method=method,
                                service=self.monitor.service_name
                            ).observe(request_size)
                        
                        # Exécution de la requête
                        response = continuation(request, context)
                        
                        # Métriques post-requête
                        duration = time.time() - start_time
                        self.monitor.metrics['request_duration'].labels(
                            method=method,
                            service=self.monitor.service_name
                        ).observe(duration)
                        
                        # Taille de la réponse
                        if hasattr(response, 'SerializeToString'):
                            response_size = len(response.SerializeToString())
                            self.monitor.metrics['response_size'].labels(
                                method=method,
                                service=self.monitor.service_name
                            ).observe(response_size)
                        
                        # Status de succès
                        self.monitor.metrics['requests_total'].labels(
                            method=method,
                            status='success',
                            service=self.monitor.service_name
                        ).inc()
                        
                        # Tracking SLA
                        self.monitor._track_sla_metrics(method, duration, True)
                        
                        return response
                        
                    except grpc.RpcError as e:
                        # Métriques d'erreur
                        duration = time.time() - start_time
                        status_code = e.code().name if hasattr(e, 'code') else 'UNKNOWN'
                        
                        self.monitor.metrics['errors_total'].labels(
                            method=method,
                            status_code=status_code,
                            service=self.monitor.service_name
                        ).inc()
                        
                        self.monitor.metrics['requests_total'].labels(
                            method=method,
                            status='error',
                            service=self.monitor.service_name
                        ).inc()
                        
                        # Tracking SLA
                        self.monitor._track_sla_metrics(method, duration, False)
                        
                        # Logging détaillé
                        self.monitor.logger.error(
                            "gRPC error",
                            method=method,
                            status_code=status_code,
                            duration=duration,
                            error=str(e)
                        )
                        
                        raise
                    
                    except Exception as e:
                        # Erreurs non-gRPC
                        duration = time.time() - start_time
                        
                        self.monitor.metrics['errors_total'].labels(
                            method=method,
                            status_code='INTERNAL',
                            service=self.monitor.service_name
                        ).inc()
                        
                        self.monitor._track_sla_metrics(method, duration, False)
                        
                        self.monitor.logger.error(
                            "Unexpected error",
                            method=method,
                            duration=duration,
                            error=str(e)
                        )
                        
                        context.set_code(grpc.StatusCode.INTERNAL)
                        context.set_details(f"Internal server error: {str(e)}")
                        return None
                
                return grpc.unary_unary_rpc_method_handler(wrapper)
        
        return MonitoringInterceptor(self)
    
    def _track_sla_metrics(self, method: str, duration: float, success: bool):
        """Track SLA metrics et violations"""
        # Response time SLA
        if duration > self.sla_config['response_time_p99']:
            self.metrics['sla_violations'].labels(
                violation_type='response_time',
                service=self.service_name
            ).inc()
        
        # Error rate tracking
        if not success:
            self.error_rates[method] += 1
            
            # Check error rate SLA
            total_requests = len(self.request_times)
            if total_requests > 100:  # Minimum sample size
                error_rate = self.error_rates[method] / total_requests
                if error_rate > self.sla_config['error_rate_threshold']:
                    self.metrics['sla_violations'].labels(
                        violation_type='error_rate',
                        service=self.service_name
                    ).inc()
        
        # Store request time
        self.request_times.append({
            'timestamp': time.time(),
            'duration': duration,
            'success': success,
            'method': method
        })
    
    def add_health_check(self, name: str, check_func: Callable[[], bool]):
        """Ajoute un health check"""
        self.health_checks[name] = check_func
        self.health_status[name] = False
    
    async def run_health_checks(self):
        """Exécute tous les health checks"""
        results = {}
        
        for name, check_func in self.health_checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                
                results[name] = result
                self.health_status[name] = result
                
                # Mise à jour métrique Prometheus
                self.metrics['health_check_status'].labels(
                    check_name=name,
                    service=self.service_name
                ).set(1 if result else 0)
                
            except Exception as e:
                results[name] = False
                self.health_status[name] = False
                
                self.metrics['health_check_status'].labels(
                    check_name=name,
                    service=self.service_name
                ).set(0)
                
                self.logger.error(
                    "Health check failed",
                    check_name=name,
                    error=str(e)
                )
        
        return results
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques de performance actuelles"""
        recent_requests = [
            req for req in self.request_times
            if time.time() - req['timestamp'] < 3600  # Last hour
        ]
        
        if not recent_requests:
            return {}
        
        durations = [req['duration'] for req in recent_requests]
        success_count = sum(1 for req in recent_requests if req['success'])
        
        return {
            'total_requests': len(recent_requests),
            'success_rate': success_count / len(recent_requests),
            'avg_response_time': sum(durations) / len(durations),
            'p95_response_time': sorted(durations)[int(len(durations) * 0.95)],
            'p99_response_time': sorted(durations)[int(len(durations) * 0.99)],
            'active_connections': self.active_connections,
            'memory_usage': self.resource_monitor.get_memory_usage(),
            'cpu_usage': self.resource_monitor.get_cpu_usage()
        }
    
    def start_monitoring(self):
        """Démarre le monitoring en arrière-plan"""
        def monitoring_loop():
            while True:
                try:
                    # Mise à jour métriques resource
                    self.metrics['memory_usage'].labels(
                        service=self.service_name
                    ).set(self.resource_monitor.get_memory_usage())
                    
                    self.metrics['cpu_usage'].labels(
                        service=self.service_name
                    ).set(self.resource_monitor.get_cpu_usage())
                    
                    # Check alerting conditions
                    asyncio.run(self.alerting.check_alerts(self.get_performance_metrics()))
                    
                    time.sleep(30)  # Update every 30 seconds
                    
                except Exception as e:
                    self.logger.error("Monitoring loop error", error=str(e))
        
        thread = threading.Thread(target=monitoring_loop, daemon=True)
        thread.start()
        
        self.logger.info("gRPC monitoring started", service=self.service_name)


@dataclass
class ResourceMonitor:
    """Moniteur de resources système"""
    
    def __init__(self):
        self.process = psutil.Process()
    
    def get_memory_usage(self) -> int:
        """Retourne l'utilisation mémoire en bytes"""
        return self.process.memory_info().rss
    
    def get_cpu_usage(self) -> float:
        """Retourne l'utilisation CPU en pourcentage"""
        return self.process.cpu_percent()
    
    def get_disk_usage(self) -> Dict[str, float]:
        """Retourne l'utilisation disque"""
        disk_usage = psutil.disk_usage('/')
        return {
            'total': disk_usage.total,
            'used': disk_usage.used,
            'free': disk_usage.free,
            'percent': (disk_usage.used / disk_usage.total) * 100
        }
    
    def get_network_stats(self) -> Dict[str, int]:
        """Retourne les statistiques réseau"""
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }


class AlertingSystem:
    """Système d'alerting intelligent"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = structlog.get_logger(__name__)
        self.alert_history = deque(maxlen=1000)
        
        # Configuration des seuils d'alerte
        self.thresholds = {
            'response_time_critical': 5.0,  # 5 seconds
            'response_time_warning': 2.0,   # 2 seconds
            'error_rate_critical': 0.05,    # 5%
            'error_rate_warning': 0.02,     # 2%
            'memory_critical': 0.90,        # 90%
            'memory_warning': 0.80,         # 80%
            'cpu_critical': 0.90,           # 90%
            'cpu_warning': 0.80             # 80%
        }
    
    async def check_alerts(self, metrics: Dict[str, Any]):
        """Vérifie les conditions d'alerte"""
        alerts = []
        
        # Response time alerts
        if 'p99_response_time' in metrics:
            if metrics['p99_response_time'] > self.thresholds['response_time_critical']:
                alerts.append(self._create_alert(
                    'CRITICAL',
                    'response_time',
                    f"P99 response time {metrics['p99_response_time']:.2f}s exceeds critical threshold"
                ))
            elif metrics['p99_response_time'] > self.thresholds['response_time_warning']:
                alerts.append(self._create_alert(
                    'WARNING',
                    'response_time',
                    f"P99 response time {metrics['p99_response_time']:.2f}s exceeds warning threshold"
                ))
        
        # Error rate alerts
        if 'success_rate' in metrics:
            error_rate = 1 - metrics['success_rate']
            if error_rate > self.thresholds['error_rate_critical']:
                alerts.append(self._create_alert(
                    'CRITICAL',
                    'error_rate',
                    f"Error rate {error_rate:.1%} exceeds critical threshold"
                ))
            elif error_rate > self.thresholds['error_rate_warning']:
                alerts.append(self._create_alert(
                    'WARNING',
                    'error_rate',
                    f"Error rate {error_rate:.1%} exceeds warning threshold"
                ))
        
        # Resource alerts
        if 'memory_usage' in metrics and 'cpu_usage' in metrics:
            # Simplistic check - would need actual memory/CPU percentages
            pass
        
        # Process alerts
        for alert in alerts:
            await self._process_alert(alert)
    
    def _create_alert(self, severity: str, alert_type: str, message: str) -> Dict[str, Any]:
        """Crée une alerte"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'service': self.service_name,
            'severity': severity,
            'type': alert_type,
            'message': message,
            'id': f"{self.service_name}_{alert_type}_{int(time.time())}"
        }
    
    async def _process_alert(self, alert: Dict[str, Any]):
        """Traite une alerte"""
        # Éviter les doublons récents
        recent_alerts = [
            a for a in self.alert_history
            if a['type'] == alert['type'] and 
               (datetime.utcnow() - datetime.fromisoformat(a['timestamp'])).seconds < 300
        ]
        
        if recent_alerts:
            return  # Déjà alerté récemment
        
        # Store alert
        self.alert_history.append(alert)
        
        # Log alert
        self.logger.warning(
            "Alert triggered",
            alert_id=alert['id'],
            severity=alert['severity'],
            type=alert['type'],
            message=alert['message']
        )
        
        # Here you would integrate with external alerting systems:
        # - PagerDuty
        # - Slack
        # - Email
        # - Webhook notifications


class GRPCDashboard:
    """Dashboard pour visualisation des métriques"""
    
    def __init__(self, monitor: GRPCMonitoringTemplate):
        self.monitor = monitor
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Génère les données pour le dashboard"""
        metrics = self.monitor.get_performance_metrics()
        health_status = self.monitor.health_status
        
        return {
            'service_info': {
                'name': self.monitor.service_name,
                'status': 'healthy' if all(health_status.values()) else 'unhealthy',
                'uptime': time.time() - self.monitor.start_time if hasattr(self.monitor, 'start_time') else 0
            },
            'performance': metrics,
            'health_checks': health_status,
            'alerts': list(self.monitor.alerting.alert_history)[-10:],  # Last 10 alerts
            'sla_status': self._calculate_sla_status(metrics)
        }
    
    def _calculate_sla_status(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule le status SLA"""
        sla_status = {}
        
        if 'p99_response_time' in metrics:
            sla_status['response_time'] = {
                'target': self.monitor.sla_config['response_time_p99'],
                'current': metrics['p99_response_time'],
                'status': 'ok' if metrics['p99_response_time'] <= self.monitor.sla_config['response_time_p99'] else 'violation'
            }
        
        if 'success_rate' in metrics:
            error_rate = 1 - metrics['success_rate']
            sla_status['error_rate'] = {
                'target': self.monitor.sla_config['error_rate_threshold'],
                'current': error_rate,
                'status': 'ok' if error_rate <= self.monitor.sla_config['error_rate_threshold'] else 'violation'
            }
        
        return sla_status


# Factory functions pour création simplifiée
def create_grpc_monitoring(service_name: str = "ainflue_grpc_service") -> GRPCMonitoringTemplate:
    """Factory pour créer un système de monitoring gRPC"""
    monitor = GRPCMonitoringTemplate(service_name)
    monitor.start_monitoring()
    return monitor


def setup_grpc_server_with_monitoring(
    server_class,
    service_name: str = "ainflue_grpc_service",
    port: int = 50051
):
    """Setup complet d'un serveur gRPC avec monitoring"""
    
    # Créer le monitoring
    monitor = create_grpc_monitoring(service_name)
    
    # Créer le serveur avec intercepteur de monitoring
    server = grpc.server(
        ThreadPoolExecutor(max_workers=10),
        interceptors=[monitor.create_monitoring_interceptor()]
    )
    
    # Ajouter le service
    server_class.add_to_server(server)
    
    # Health checks de base
    monitor.add_health_check("server_ready", lambda: True)
    monitor.add_health_check("port_available", lambda: True)
    
    # Configurer le port
    listen_addr = f'[::]:{port}'
    server.add_insecure_port(listen_addr)
    
    monitor.logger.info(
        "gRPC server configured with monitoring",
        service=service_name,
        port=port,
        address=listen_addr
    )
    
    return server, monitor


# Example usage
if __name__ == "__main__":
    # Créer un monitoring instance
    monitor = create_grpc_monitoring("example_service")
    
    # Ajouter des health checks
    monitor.add_health_check("database", lambda: True)
    monitor.add_health_check("cache", lambda: True)
    
    # Simuler quelques métriques
    import random
    
    async def simulate_requests():
        for i in range(100):
            # Simuler une requête
            duration = random.uniform(0.1, 2.0)
            success = random.random() > 0.1  # 90% success rate
            
            monitor._track_sla_metrics("TestMethod", duration, success)
            await asyncio.sleep(0.1)
    
    async def main():
        # Lancer les health checks
        health_results = await monitor.run_health_checks()
        print(f"Health checks: {health_results}")
        
        # Simuler du trafic
        await simulate_requests()
        
        # Obtenir les métriques
        metrics = monitor.get_performance_metrics()
        print(f"Performance metrics: {json.dumps(metrics, indent=2)}")
        
        # Générer dashboard data
        dashboard = GRPCDashboard(monitor)
        dashboard_data = dashboard.generate_dashboard_data()
        print(f"Dashboard data: {json.dumps(dashboard_data, indent=2)}")
    
    asyncio.run(main())