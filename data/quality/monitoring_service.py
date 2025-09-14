"""
🔍 MONITORING SERVICE - REAL-TIME QUALITY MONITORING
Data Quality Module - Phase 2 Implementation

🚨 PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel - TOUS DROITS RÉSERVÉS
Toute utilisation non autorisée sera poursuivie en justice.

Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from contextlib import asynccontextmanager

# Enterprise monitoring dependencies
import psutil
import aioredis
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from pydantic import BaseModel, Field


class MonitoringLevel(str, Enum):
    """Niveaux de monitoring qualité"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"
    CRITICAL = "critical"


class AlertSeverity(str, Enum):
    """Niveaux de sévérité des alertes"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class QualityMetric:
    """Métrique de qualité en temps réel"""
    name: str
    value: float
    threshold: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: str = "normal"
    trend: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Évaluation automatique du statut"""
        if self.value >= self.threshold:
            self.status = "good"
        elif self.value >= self.threshold * 0.8:
            self.status = "warning"
        else:
            self.status = "critical"


@dataclass
class SystemMetric:
    """Métrique système en temps réel"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_system(cls) -> 'SystemMetric':
        """Collecte métriques système actuelles"""
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        net_io = psutil.net_io_counters()
        network = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
        
        return cls(
            cpu_usage=cpu,
            memory_usage=memory,
            disk_usage=disk,
            network_io=network
        )


class PerformanceMonitor:
    """Moniteur de performance temps réel"""
    
    def __init__(self, monitoring_level -> None: MonitoringLevel = MonitoringLevel.ENTERPRISE) -> None:
        self.monitoring_level = monitoring_level
        self.metrics_history: List[SystemMetric] = []
        self.max_history = 1000
        
        # Prometheus metrics
        self.response_time_histogram = Histogram(
            'ainflue_response_time_seconds',
            'Response time of Ainflue operations',
            ['operation', 'status']
        )
        
        self.quality_score_gauge = Gauge(
            'ainflue_quality_score',
            'Current quality score',
            ['component', 'metric']
        )
        
        self.alert_counter = Counter(
            'ainflue_alerts_total',
            'Total number of alerts',
            ['severity', 'component']
        )
        
        self.logger = logging.getLogger(__name__)
    
    async def collect_system_metrics(self) -> SystemMetric:
        """Collecte métriques système"""
        try:
            metric = SystemMetric.from_system()
            
            # Stockage historique
            self.metrics_history.append(metric)
            if len(self.metrics_history) > self.max_history:
                self.metrics_history.pop(0)
            
            # Mise à jour Prometheus
            self.quality_score_gauge.labels(
                component='system', 
                metric='cpu'
            ).set(metric.cpu_usage)
            
            self.quality_score_gauge.labels(
                component='system', 
                metric='memory'
            ).set(metric.memory_usage)
            
            self.quality_score_gauge.labels(
                component='system', 
                metric='disk'
            ).set(metric.disk_usage)
            
            return metric
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            raise
    
    def analyze_performance_trend(self, window_minutes: int = 10) -> Dict[str, Any]:
        """Analyse des tendances de performance"""
        if len(self.metrics_history) < 2:
            return {"status": "insufficient_data"}
        
        # Filtrage fenêtre temporelle
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp >= cutoff_time
        ]
        
        if len(recent_metrics) < 2:
            return {"status": "insufficient_recent_data"}
        
        # Calcul tendances
        cpu_values = [m.cpu_usage for m in recent_metrics]
        memory_values = [m.memory_usage for m in recent_metrics]
        
        cpu_trend = "increasing" if cpu_values[-1] > cpu_values[0] else "decreasing"
        memory_trend = "increasing" if memory_values[-1] > memory_values[0] else "decreasing"
        
        return {
            "status": "analyzed",
            "window_minutes": window_minutes,
            "metrics_count": len(recent_metrics),
            "trends": {
                "cpu": {
                    "direction": cpu_trend,
                    "current": cpu_values[-1],
                    "average": sum(cpu_values) / len(cpu_values),
                    "peak": max(cpu_values)
                },
                "memory": {
                    "direction": memory_trend,
                    "current": memory_values[-1],
                    "average": sum(memory_values) / len(memory_values),
                    "peak": max(memory_values)
                }
            }
        }


class QualityMonitor:
    """Moniteur de qualité des données"""
    
    def __init__(self, monitoring_level -> None: MonitoringLevel = MonitoringLevel.ENTERPRISE) -> None:
        self.monitoring_level = monitoring_level
        self.quality_metrics: Dict[str, QualityMetric] = {}
        self.alert_thresholds = {
            AlertSeverity.WARNING: 0.8,
            AlertSeverity.ERROR: 0.6,
            AlertSeverity.CRITICAL: 0.4,
            AlertSeverity.EMERGENCY: 0.2
        }
        self.logger = logging.getLogger(__name__)
    
    async def assess_content_quality(self, content_data: Dict[str, Any]) -> QualityMetric:
        """Évaluation qualité contenu en temps réel"""
        try:
            # Métriques de base
            completeness = self._calculate_completeness(content_data)
            accuracy = self._calculate_accuracy(content_data)
            consistency = self._calculate_consistency(content_data)
            
            # Score global pondéré
            overall_score = (
                completeness * 0.4 +
                accuracy * 0.35 +
                consistency * 0.25
            )
            
            quality_metric = QualityMetric(
                name="content_quality",
                value=overall_score,
                threshold=0.85,
                unit="score"
            )
            
            self.quality_metrics["content_quality"] = quality_metric
            
            # Génération alerte si nécessaire
            if overall_score < 0.7:
                await self._trigger_quality_alert(quality_metric)
            
            return quality_metric
            
        except Exception as e:
            self.logger.error(f"Error assessing content quality: {e}")
            raise
    
    def _calculate_completeness(self, content_data: Dict[str, Any]) -> float:
        """Calcul complétude des données"""
        required_fields = ['title', 'content', 'format', 'metadata']
        present_fields = sum(1 for field in required_fields if content_data.get(field))
        return present_fields / len(required_fields)
    
    def _calculate_accuracy(self, content_data: Dict[str, Any]) -> float:
        """Calcul précision des données"""
        accuracy_score = 1.0
        
        # Validation format
        if content_data.get('format') not in ['audio', 'video', 'image', 'text']:
            accuracy_score -= 0.2
        
        # Validation métadonnées
        metadata = content_data.get('metadata', {})
        if not metadata.get('timestamp'):
            accuracy_score -= 0.1
        
        if not metadata.get('source'):
            accuracy_score -= 0.1
        
        return max(0.0, accuracy_score)
    
    def _calculate_consistency(self, content_data: Dict[str, Any]) -> float:
        """Calcul cohérence des données"""
        # Vérification cohérence format/contenu
        format_type = content_data.get('format', '')
        content = content_data.get('content', '')
        
        if format_type == 'audio' and not content.endswith(('.mp3', '.wav', '.flac')):
            return 0.6
        
        if format_type == 'video' and not content.endswith(('.mp4', '.avi', '.mkv')):
            return 0.6
        
        return 1.0
    
    async def _trigger_quality_alert(self, metric -> None: QualityMetric) -> None:
        """Déclenchement alerte qualité"""
        severity = self._determine_alert_severity(metric.value)
        
        alert_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "severity": severity.value,
            "metric_name": metric.name,
            "current_value": metric.value,
            "threshold": metric.threshold,
            "status": metric.status,
            "message": f"Quality metric {metric.name} below threshold"
        }
        
        self.logger.warning(f"Quality alert: {alert_data}")
        
        # Envoi vers système d'alertes
        # await self._send_alert_to_external_system(alert_data)
    
    def _determine_alert_severity(self, value: float) -> AlertSeverity:
        """Détermination sévérité alerte"""
        for severity, threshold in self.alert_thresholds.items():
            if value <= threshold:
                return severity
        return AlertSeverity.INFO


class RealTimeMonitoringService:
    """Service de monitoring temps réel enterprise"""
    
    def __init__(self, 
                 monitoring_level -> None: MonitoringLevel = MonitoringLevel.ENTERPRISE,
                 redis_url -> None: str = "redis -> None://localhost -> None:6379") -> None:
        self.monitoring_level = monitoring_level
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Composants monitoring
        self.performance_monitor = PerformanceMonitor(monitoring_level)
        self.quality_monitor = QualityMonitor(monitoring_level)
        
        # Configuration monitoring
        self.monitoring_interval = self._get_monitoring_interval()
        self.is_running = False
        self.logger = logging.getLogger(__name__)
    
    def _get_monitoring_interval(self) -> float:
        """Intervalle monitoring selon niveau"""
        intervals = {
            MonitoringLevel.BASIC: 60.0,      # 1 minute
            MonitoringLevel.STANDARD: 30.0,   # 30 secondes
            MonitoringLevel.ADVANCED: 10.0,   # 10 secondes
            MonitoringLevel.ENTERPRISE: 5.0,  # 5 secondes
            MonitoringLevel.CRITICAL: 1.0     # 1 seconde
        }
        return intervals.get(self.monitoring_level, 30.0)
    
    async def start_monitoring(self) -> None:
        """Démarrage service monitoring"""
        try:
            # Connexion Redis
            self.redis_client = aioredis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            self.is_running = True
            self.logger.info(f"Monitoring service started - Level: {self.monitoring_level}")
            
            # Lancement monitoring en arrière-plan
            asyncio.create_task(self._monitoring_loop())
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring service: {e}")
            raise
    
    async def stop_monitoring(self) -> None:
        """Arrêt service monitoring"""
        self.is_running = False
        if self.redis_client:
            await self.redis_client.close()
        self.logger.info("Monitoring service stopped")
    
    async def _monitoring_loop(self) -> None:
        """Boucle principale de monitoring"""
        while self.is_running:
            try:
                # Collecte métriques système
                system_metrics = await self.performance_monitor.collect_system_metrics()
                
                # Stockage Redis
                await self._store_metrics_redis("system", system_metrics.__dict__)
                
                # Analyse tendances
                trends = self.performance_monitor.analyze_performance_trend()
                await self._store_metrics_redis("trends", trends)
                
                # Attente avant prochaine collecte
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _store_metrics_redis(self, key -> None: str, data -> None: Dict[str, Any]) -> None:
        """Stockage métriques dans Redis"""
        if not self.redis_client:
            return
        
        try:
            # Sérialisation JSON avec gestion datetime
            json_data = json.dumps(data, default=self._json_serializer)
            
            # Stockage avec TTL
            await self.redis_client.setex(
                f"ainflue:monitoring:{key}:{int(time.time())}", 
                3600,  # 1 heure TTL
                json_data
            )
            
        except Exception as e:
            self.logger.error(f"Error storing metrics in Redis: {e}")
    
    def _json_serializer(self, obj) -> None:
        """Sérialiseur JSON pour datetime"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Récupération métriques actuelles"""
        try:
            # Métriques système récentes
            system_metric = await self.performance_monitor.collect_system_metrics()
            
            # Tendances performance
            trends = self.performance_monitor.analyze_performance_trend()
            
            # Métriques qualité
            quality_metrics = {
                name: {
                    "value": metric.value,
                    "threshold": metric.threshold,
                    "status": metric.status,
                    "timestamp": metric.timestamp.isoformat()
                }
                for name, metric in self.quality_monitor.quality_metrics.items()
            }
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "monitoring_level": self.monitoring_level.value,
                "system": {
                    "cpu_usage": system_metric.cpu_usage,
                    "memory_usage": system_metric.memory_usage,
                    "disk_usage": system_metric.disk_usage,
                    "network_io": system_metric.network_io
                },
                "performance_trends": trends,
                "quality_metrics": quality_metrics,
                "service_status": "running" if self.is_running else "stopped"
            }
            
        except Exception as e:
            self.logger.error(f"Error getting current metrics: {e}")
            return {"error": str(e)}
    
    @asynccontextmanager
    async def monitor_operation(self, operation_name -> None: str) -> None:
        """Context manager pour monitoring d'opération"""
        start_time = time.time()
        try:
            yield
            # Succès
            duration = time.time() - start_time
            self.performance_monitor.response_time_histogram.labels(
                operation=operation_name, 
                status='success'
            ).observe(duration)
            
        except Exception as e:
            # Échec
            duration = time.time() - start_time
            self.performance_monitor.response_time_histogram.labels(
                operation=operation_name, 
                status='error'
            ).observe(duration)
            
            # Alerte
            self.performance_monitor.alert_counter.labels(
                severity='error',
                component=operation_name
            ).inc()
            
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification santé service"""
        checks = {}
        
        # Vérification Redis
        try:
            if self.redis_client:
                await self.redis_client.ping()
                checks["redis"] = "healthy"
            else:
                checks["redis"] = "not_connected"
        except Exception:
            checks["redis"] = "unhealthy"
        
        # Vérification monitoring
        checks["monitoring"] = "running" if self.is_running else "stopped"
        
        # Vérification métriques
        checks["metrics_collection"] = "active" if len(self.performance_monitor.metrics_history) > 0 else "inactive"
        
        # Score santé global
        healthy_checks = sum(1 for status in checks.values() if status in ["healthy", "running", "active"])
        health_score = healthy_checks / len(checks)
        
        return {
            "health_score": health_score,
            "status": "healthy" if health_score >= 0.8 else "degraded" if health_score >= 0.5 else "unhealthy",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }


# Service singleton pour utilisation globale
monitoring_service = RealTimeMonitoringService()


async def get_monitoring_service() -> RealTimeMonitoringService:
    """Factory function pour service monitoring"""
    if not monitoring_service.is_running:
        await monitoring_service.start_monitoring()
    return monitoring_service


# Export des classes principales
__all__ = [
    'RealTimeMonitoringService',
    'QualityMonitor', 
    'PerformanceMonitor',
    'MonitoringLevel',
    'AlertSeverity',
    'QualityMetric',
    'SystemMetric',
    'monitoring_service',
    'get_monitoring_service'
]


# Exemple d'utilisation
if __name__ == "__main__":
    async def main() -> None:
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        
        # Initialisation service
        service = RealTimeMonitoringService(MonitoringLevel.ENTERPRISE)
        
        try:
            # Démarrage monitoring
            await service.start_monitoring()
            
            # Test monitoring opération
            async with service.monitor_operation("test_operation"):
                await asyncio.sleep(0.1)  # Simulation traitement
            
            # Récupération métriques
            metrics = await service.get_current_metrics()
            print(f"Current metrics: {json.dumps(metrics, indent=2)}")
            
            # Vérification santé
            health = await service.health_check()
            print(f"Health check: {json.dumps(health, indent=2)}")
            
            # Test évaluation qualité
            sample_content = {
                "title": "Test Content",
                "content": "test_audio.mp3",
                "format": "audio",
                "metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "test_upload"
                }
            }
            
            quality_metric = await service.quality_monitor.assess_content_quality(sample_content)
            print(f"Quality assessment: {quality_metric}")
            
        finally:
            await service.stop_monitoring()
    
    # Exécution test
    asyncio.run(main())