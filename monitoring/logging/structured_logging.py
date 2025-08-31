"""📊 Structured Logging - IA-Influencer-Agent Monitoring
==================================================================
Expert: DEVOPS_ENGINEER + SRE_SPECIALIST
Technologies: Prometheus + Grafana + ELK Stack + APM
Date: 2025-07-31 06:28:26

Monitoring et observabilité complète avec métriques temps réel.
==================================================================
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from functools import wraps
import json
import psutil
import threading

logger = logging.getLogger(__name__)

# =============== CONFIGURATION MONITORING ===============

@dataclass
class MonitoringConfig:
    """Configuration du monitoring"""    metrics_enabled: bool = True
    health_check_interval: int = 30
    performance_tracking: bool = True
    log_level: str = "INFO"
    retention_days: int = 30
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "cpu_percent": 80.0,
        "memory_percent": 85.0,
        "disk_percent": 90.0,
        "response_time_ms": 1000.0
    })

# =============== MÉTRIQUES SYSTÈME ===============

class SystemMetrics:
    """Collecteur de métriques système"""    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Statistiques système en temps réel"""        return {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - self.start_time,
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            },
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            }
        }
    
    def get_application_stats(self) -> Dict[str, Any]:
        """Statistiques applicatives"""        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "requests_total": self.request_count,
            "errors_total": self.error_count,
            "error_rate": (self.error_count / max(self.request_count, 1)) * 100,
            "avg_response_time_ms": avg_response_time,
            "active_threads": threading.active_count()
        }

# =============== HEALTH CHECKS ===============

class HealthChecker:
    """Vérificateur de santé des services"""    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.checks = {}
        self.last_check_results = {}
    
    def register_check(self, name: str, check_func: Callable) -> None:
        """Enregistrer une vérification de santé"""        self.checks[name] = check_func
        logger.info(f"✅ Health check enregistré: {name}")
    
    async def run_health_check(self, name: str) -> Dict[str, Any]:
        """Exécuter une vérification de santé"""        try:
            start_time = time.time()
            
            if name in self.checks:
                result = await self.checks[name]()
                response_time = (time.time() - start_time) * 1000
                
                check_result = {
                    "name": name,
                    "status": "healthy" if result else "unhealthy",
                    "response_time_ms": response_time,
                    "timestamp": datetime.now().isoformat(),
                    "details": result if isinstance(result, dict) else {"result": result}
                }
            else:
                check_result = {
                    "name": name,
                    "status": "not_found",
                    "error": "Health check non trouvé",
                    "timestamp": datetime.now().isoformat()
                }
            
            self.last_check_results[name] = check_result
            return check_result
            
        except Exception as e:
            error_result = {
                "name": name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.last_check_results[name] = error_result
            return error_result
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Exécuter toutes les vérifications"""        results = {}
        
        for name in self.checks.keys():
            results[name] = await self.run_health_check(name)
        
        # Statut global
        all_healthy = all(
            result.get("status") == "healthy" 
            for result in results.values()
        )
        
        return {
            "overall_status": "healthy" if all_healthy else "degraded",
            "checks": results,
            "timestamp": datetime.now().isoformat()
        }

# =============== PERFORMANCE TRACKING ===============

def track_performance(metric_name: str = None):
    """Décorateur pour tracker les performances"""    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                # Log performance
                logger.info(f"📊 {metric_name or func.__name__}: {execution_time:.2f}ms")
                
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger.error(f"❌ {metric_name or func.__name__}: {execution_time:.2f}ms - Erreur: {e}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                logger.info(f"📊 {metric_name or func.__name__}: {execution_time:.2f}ms")
                
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger.error(f"❌ {metric_name or func.__name__}: {execution_time:.2f}ms - Erreur: {e}")
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# =============== GESTIONNAIRE PRINCIPAL ===============

class StructuredLoggingManager:
    """Gestionnaire principal du monitoring"""    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.metrics = SystemMetrics()
        self.health_checker = HealthChecker(config)
        self.running = False
        self.monitoring_task = None
    
    async def start(self) -> bool:
        """Démarrage du monitoring"""        try:
            self.running = True
            
            # Enregistrer les health checks par défaut
            self.health_checker.register_check("system", self._system_health_check)
            self.health_checker.register_check("memory", self._memory_health_check)
            
            # Démarrer le monitoring en arrière-plan
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("🚀 Monitoring démarré")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage monitoring: {e}")
            return False
    
    async def stop(self) -> bool:
        """Arrêt du monitoring"""        try:
            self.running = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("⏹️ Monitoring arrêté")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt monitoring: {e}")
            return False
    
    async def _monitoring_loop(self):
        """Boucle de monitoring continue"""        while self.running:
            try:
                # Collecter les métriques
                system_stats = self.metrics.get_system_stats()
                app_stats = self.metrics.get_application_stats()
                
                # Vérifier les seuils d'alerte
                await self._check_alerts(system_stats)
                
                # Attendre l'intervalle suivant
                await asyncio.sleep(self.config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur boucle monitoring: {e}")
                await asyncio.sleep(5)
    
    async def _system_health_check(self) -> bool:
        """Health check système"""        stats = self.metrics.get_system_stats()
        return stats["cpu_percent"] < 95 and stats["memory"]["percent"] < 95
    
    async def _memory_health_check(self) -> bool:
        """Health check mémoire"""        stats = self.metrics.get_system_stats()
        return stats["memory"]["percent"] < self.config.alert_thresholds["memory_percent"]
    
    async def _check_alerts(self, stats: Dict[str, Any]):
        """Vérification des seuils d'alerte"""        alerts = []
        
        if stats["cpu_percent"] > self.config.alert_thresholds["cpu_percent"]:
            alerts.append(f"CPU élevé: {stats['cpu_percent']}%")
        
        if stats["memory"]["percent"] > self.config.alert_thresholds["memory_percent"]:
            alerts.append(f"Mémoire élevée: {stats['memory']['percent']}%")
        
        if alerts:
            logger.warning(f"🚨 ALERTES: {', '.join(alerts)}")

# =============== EXPORT MODULE ===============

__all__ = [
    "StructuredLoggingManager",
    "SystemMetrics",
    "HealthChecker",
    "MonitoringConfig",
    "track_performance"
]
