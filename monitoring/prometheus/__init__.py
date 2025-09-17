"""
⚠️ CONFIDENTIEL - Ainflue Creator Platform ⚠️

🔒 PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Fahed Mlaiel (mlaiel@live.de)

Ce module contient l'architecture Prometheus Monitoring Enterprise d'Ainflue.
Toute divulgation, reproduction ou distribution non autorisée est strictement 
interdite et passible de poursuites judiciaires.

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

# Version et metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary"

# Configuration principale
class PrometheusConfig:
    """Configuration centralisée pour Prometheus Enterprise Monitoring"""
    
    # Paths
    CONFIG_DIR = Path(__file__).parent
    PROMETHEUS_CONFIG = CONFIG_DIR / "prometheus.yml"
    ALERT_RULES = CONFIG_DIR / "alert_rules.yml"
    RECORDING_RULES = CONFIG_DIR / "recording_rules.yml"
    SLA_ALERTS = CONFIG_DIR / "sla_alerts.yml"
    PRODUCTION_ALERTS = CONFIG_DIR / "production_alert_rules.yml"
    
    # Métrics namespaces
    CREATOR_METRICS_PREFIX = "ainflue_creator"
    SYSTEM_METRICS_PREFIX = "ainflue_system"
    AI_METRICS_PREFIX = "ainflue_ai"
    SECURITY_METRICS_PREFIX = "ainflue_security"
    BUSINESS_METRICS_PREFIX = "ainflue_business"
    
    # Performance thresholds
    QUERY_TIMEOUT = 30
    MAX_CARDINALITY = 1000000
    RETENTION_DAYS = 15
    LONG_TERM_RETENTION_YEARS = 7

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Prometheus Enterprise Monitoring Module Initialized - v%s", __version__)