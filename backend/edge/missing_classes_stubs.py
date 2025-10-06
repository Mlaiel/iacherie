"""
🔧 MISSING CLASSES STUBS - TEMPORARY COMPATIBILITY LAYER
==========================================================

Ce fichier contient des stubs (classes vides) pour toutes les classes
manquantes dans le module edge, permettant aux imports de fonctionner
pendant que les implémentations complètes sont ajoutées progressivement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


# ============================================================================
# ALERTING & MONITORING CLASSES
# ============================================================================

class AlertingSyst:
    """Système d'alerting stub."""
    def __init__(self):
        self.alerts = []
    
    async def send_alert(self, *args, **kwargs):
        pass
    
    def add_rule(self, *args, **kwargs):
        pass


# Alias
AlertingSystem = AlertingSyst


class MetricsCollector:
    """Collecteur de métriques stub."""
    def __init__(self):
        self.metrics = {}
    
    async def collect(self, *args, **kwargs):
        return {}
    
    def get_metrics(self):
        return self.metrics


class PerformanceAnalyzer:
    """Analyseur de performance stub."""
    def __init__(self):
        pass
    
    async def analyze(self, *args, **kwargs):
        return {"status": "ok"}


class LogAggregator:
    """Agrégateur de logs stub."""
    def __init__(self):
        self.logs = []
    
    async def aggregate(self, *args, **kwargs):
        return []


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "AlertingSystem",
    "AlertingSyst",
    "MetricsCollector",
    "PerformanceAnalyzer",
    "LogAggregator"
]
