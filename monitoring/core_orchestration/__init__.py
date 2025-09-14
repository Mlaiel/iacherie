"""
🚀 Core Orchestration - Enterprise Monitoring Ainflue
=====================================================

Module central d'orchestration pour le système de surveillance enterprise.
Coordonne tous les agents de monitoring et fournit l'intelligence globale.

Architecture: monitoring/core_orchestration/ (NIVEAU 2)
Responsabilité: Orchestration maître et coordination intelligente

© 2025 Fahed Mlaiel - Architecture Monitoring Propriétaire Ultra-Avancée
"""

from .index import (
    EnterpriseMonitoringHub,
    MonitoringConfig,
    MonitoringEvent,
    MonitoringEventType,
    create_monitoring_app
)

__all__ = [
    'EnterpriseMonitoringHub',
    'MonitoringConfig', 
    'MonitoringEvent',
    'MonitoringEventType',
    'create_monitoring_app'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"