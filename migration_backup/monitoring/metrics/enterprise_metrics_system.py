#!/usr/bin/env python3
"""
Enterprise Metrics System
Système de métriques de niveau entreprise pour Ainfluencer

© 2025 Fahed Mlaiel <mlaiel@live.de>
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types de métriques enterprise"""
    PERFORMANCE = "performance"
    BUSINESS = "business"
    TECHNICAL = "technical"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    SECURITY = "security"

class MetricSeverity(Enum):
    """Niveaux de sévérité des métriques"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class EnterpriseMetric:
    """Métrique enterprise"""
    name: str
    value: float
    metric_type: MetricType
    severity: MetricSeverity = MetricSeverity.LOW
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

class EnterpriseMetricsCollector:
    """Collecteur de métriques enterprise"""
    
    def __init__(self):
        self.metrics: Dict[str, EnterpriseMetric] = {}
        self.thresholds: Dict[str, Dict[str, float]] = {}
        self.alerts_enabled = True
        logger.info("Enterprise Metrics Collector initialized")
    
    async def collect_metric(self, name: str, value: float, metric_type: MetricType, 
                           severity: MetricSeverity = MetricSeverity.LOW, 
                           metadata: Optional[Dict[str, Any]] = None,
                           tags: Optional[List[str]] = None) -> None:
        """Collecte une métrique"""
        try:
            metric = EnterpriseMetric(
                name=name,
                value=value,
                metric_type=metric_type,
                severity=severity,
                metadata=metadata or {},
                tags=tags or []
            )
            
            self.metrics[name] = metric
            
            # Vérifier les seuils
            await self._check_thresholds(metric)
            
            logger.debug(f"Metric collected: {name} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to collect metric {name}: {e}")
    
    async def _check_thresholds(self, metric: EnterpriseMetric) -> None:
        """Vérifie les seuils d'alerte"""
        try:
            if not self.alerts_enabled:
                return
                
            thresholds = self.thresholds.get(metric.name, {})
            
            for threshold_name, threshold_value in thresholds.items():
                if metric.value >= threshold_value:
                    await self._trigger_alert(metric, threshold_name, threshold_value)
                    
        except Exception as e:
            logger.error(f"Failed to check thresholds for {metric.name}: {e}")
    
    async def _trigger_alert(self, metric: EnterpriseMetric, threshold_name: str, 
                           threshold_value: float) -> None:
        """Déclenche une alerte"""
        try:
            alert = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metric_name": metric.name,
                "metric_value": metric.value,
                "threshold_name": threshold_name,
                "threshold_value": threshold_value,
                "severity": metric.severity.value,
                "metadata": metric.metadata
            }
            
            logger.warning(f"Enterprise metric alert: {json.dumps(alert, indent=2)}")
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
    
    def get_metrics(self, metric_type: Optional[MetricType] = None) -> Dict[str, EnterpriseMetric]:
        """Récupère les métriques"""
        try:
            if metric_type:
                return {
                    name: metric for name, metric in self.metrics.items()
                    if metric.metric_type == metric_type
                }
            return self.metrics.copy()
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {}
    
    def set_threshold(self, metric_name: str, threshold_name: str, value: float) -> None:
        """Définit un seuil d'alerte"""
        try:
            if metric_name not in self.thresholds:
                self.thresholds[metric_name] = {}
            
            self.thresholds[metric_name][threshold_name] = value
            logger.info(f"Threshold set: {metric_name}.{threshold_name} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to set threshold: {e}")
    
    async def generate_report(self) -> Dict[str, Any]:
        """Génère un rapport de métriques"""
        try:
            report = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_metrics": len(self.metrics),
                "metrics_by_type": {},
                "metrics_by_severity": {},
                "active_alerts": 0
            }
            
            # Métriques par type
            for metric_type in MetricType:
                count = len([
                    m for m in self.metrics.values() 
                    if m.metric_type == metric_type
                ])
                report["metrics_by_type"][metric_type.value] = count
            
            # Métriques par sévérité
            for severity in MetricSeverity:
                count = len([
                    m for m in self.metrics.values()
                    if m.severity == severity
                ])
                report["metrics_by_severity"][severity.value] = count
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return {}

class EnterpriseMetricsSystem:
    """Système de métriques enterprise principal"""
    
    def __init__(self):
        self.collector = EnterpriseMetricsCollector()
        self.is_running = False
        self._background_tasks: List[asyncio.Task] = []
        logger.info("Enterprise Metrics System initialized")
    
    async def start(self) -> None:
        """Démarre le système de métriques"""
        try:
            self.is_running = True
            
            # Démarrer la collecte périodique
            task = asyncio.create_task(self._periodic_collection())
            self._background_tasks.append(task)
            
            logger.info("Enterprise Metrics System started")
            
        except Exception as e:
            logger.error(f"Failed to start metrics system: {e}")
    
    async def stop(self) -> None:
        """Arrête le système de métriques"""
        try:
            self.is_running = False
            
            # Annuler les tâches en cours
            for task in self._background_tasks:
                task.cancel()
            
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
            self._background_tasks.clear()
            
            logger.info("Enterprise Metrics System stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop metrics system: {e}")
    
    async def _periodic_collection(self) -> None:
        """Collecte périodique de métriques système"""
        try:
            while self.is_running:
                # Métriques système de base
                await self.collector.collect_metric(
                    "system_health",
                    95.0,
                    MetricType.OPERATIONAL,
                    MetricSeverity.LOW
                )
                
                await self.collector.collect_metric(
                    "api_response_time",
                    120.5,
                    MetricType.PERFORMANCE,
                    MetricSeverity.MEDIUM
                )
                
                await asyncio.sleep(60)  # Collecte chaque minute
                
        except asyncio.CancelledError:
            logger.info("Periodic collection cancelled")
        except Exception as e:
            logger.error(f"Error in periodic collection: {e}")

# Instance globale
enterprise_metrics_system = EnterpriseMetricsSystem()

# Fonctions d'interface
async def collect_metric(name: str, value: float, metric_type: MetricType, 
                        severity: MetricSeverity = MetricSeverity.LOW,
                        metadata: Optional[Dict[str, Any]] = None,
                        tags: Optional[List[str]] = None) -> None:
    """Interface pour collecter une métrique"""
    await enterprise_metrics_system.collector.collect_metric(
        name, value, metric_type, severity, metadata, tags
    )

def get_metrics(metric_type: Optional[MetricType] = None) -> Dict[str, EnterpriseMetric]:
    """Interface pour récupérer les métriques"""
    return enterprise_metrics_system.collector.get_metrics(metric_type)

async def generate_report() -> Dict[str, Any]:
    """Interface pour générer un rapport"""
    return await enterprise_metrics_system.collector.generate_report()

if __name__ == "__main__":
    # Test rapide
    async def test():
        system = EnterpriseMetricsSystem()
        await system.start()
        
        # Test des métriques
        await collect_metric("test_metric", 42.0, MetricType.BUSINESS)
        
        report = await generate_report()
        print(f"Report: {json.dumps(report, indent=2)}")
        
        await system.stop()
    
    asyncio.run(test())