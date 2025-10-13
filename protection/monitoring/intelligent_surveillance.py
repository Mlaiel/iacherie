#!/usr/bin/env python3
"""
Intelligent Surveillance System
Système de surveillance intelligente pour la protection de contenu

© 2025 Fahed Mlaiel <mlaiel@live.de>
"""

import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Niveaux de menace"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatSeverity(Enum):
    """Alias pour ThreatLevel (compatibilité)"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SurveillanceEvent(Enum):
    """Types d'événements de surveillance"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    CONTENT_VIOLATION = "content_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SYSTEM_ANOMALY = "system_anomaly"
    SECURITY_BREACH = "security_breach"

@dataclass
class SurveillanceAlert:
    """Alerte de surveillance"""
    id: str
    event_type: SurveillanceEvent
    threat_level: ThreatLevel
    message: str
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================================

# Main class alias (often used as IntelligentSurveillance in other modules)
IntelligentSurveillance = lambda: IntelligentSurveillanceEngine()


class IntelligentSurveillanceEngine:
    """Moteur de surveillance intelligente"""
    
    def __init__(self):
        self.active_alerts: Dict[str, SurveillanceAlert] = {}
        self.blocked_ips: Set[str] = set()
        self.suspicious_users: Set[str] = set()
        self.surveillance_rules: Dict[str, Any] = {}
        self.is_monitoring = False
        self._setup_default_rules()
        logger.info("Intelligent Surveillance Engine initialized")
    
    def _setup_default_rules(self) -> None:
        """Configure les règles de surveillance par défaut"""
        try:
            self.surveillance_rules = {
                "max_failed_logins": 5,
                "suspicious_ip_threshold": 10,
                "content_scan_interval": 300,  # 5 minutes
                "anomaly_detection_enabled": True,
                "auto_block_enabled": True
            }
        except Exception as e:
            logger.error(f"Failed to setup surveillance rules: {e}")
    
    async def start_monitoring(self) -> None:
        """Démarre la surveillance"""
        try:
            self.is_monitoring = True
            logger.info("Intelligent surveillance monitoring started")
            
            # Démarrer les tâches de surveillance
            asyncio.create_task(self._monitor_system_health())
            asyncio.create_task(self._monitor_user_activity())
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
    
    async def stop_monitoring(self) -> None:
        """Arrête la surveillance"""
        try:
            self.is_monitoring = False
            logger.info("Intelligent surveillance monitoring stopped")
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
    
    async def _monitor_system_health(self) -> None:
        """Surveille la santé du système"""
        try:
            while self.is_monitoring:
                # Simulation de surveillance système
                await asyncio.sleep(60)  # Vérification chaque minute
                
        except Exception as e:
            logger.error(f"System health monitoring error: {e}")
    
    async def _monitor_user_activity(self) -> None:
        """Surveille l'activité des utilisateurs"""
        try:
            while self.is_monitoring:
                # Simulation de surveillance utilisateur
                await asyncio.sleep(30)  # Vérification toutes les 30 secondes
                
        except Exception as e:
            logger.error(f"User activity monitoring error: {e}")
    
    async def create_alert(self, event_type: SurveillanceEvent, threat_level: ThreatLevel,
                          message: str, source_ip: Optional[str] = None,
                          user_id: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """Crée une nouvelle alerte de surveillance"""
        try:
            alert_id = f"alert_{datetime.now(timezone.utc).timestamp()}"
            
            alert = SurveillanceAlert(
                id=alert_id,
                event_type=event_type,
                threat_level=threat_level,
                message=message,
                source_ip=source_ip,
                user_id=user_id,
                metadata=metadata or {}
            )
            
            self.active_alerts[alert_id] = alert
            
            # Actions automatiques selon le niveau de menace
            if threat_level == ThreatLevel.CRITICAL:
                await self._handle_critical_threat(alert)
            elif threat_level == ThreatLevel.HIGH:
                await self._handle_high_threat(alert)
            
            logger.warning(f"Surveillance alert created: {alert_id} - {message}")
            return alert_id
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            return ""
    
    async def _handle_critical_threat(self, alert: SurveillanceAlert) -> None:
        """Gère les menaces critiques"""
        try:
            if alert.source_ip and self.surveillance_rules.get("auto_block_enabled"):
                self.blocked_ips.add(alert.source_ip)
                logger.warning(f"IP blocked due to critical threat: {alert.source_ip}")
            
            if alert.user_id:
                self.suspicious_users.add(alert.user_id)
                logger.warning(f"User marked as suspicious: {alert.user_id}")
                
        except Exception as e:
            logger.error(f"Failed to handle critical threat: {e}")
    
    async def _handle_high_threat(self, alert: SurveillanceAlert) -> None:
        """Gère les menaces élevées"""
        try:
            if alert.source_ip:
                # Augmenter le niveau de surveillance pour cette IP
                logger.info(f"Increased surveillance for IP: {alert.source_ip}")
                
        except Exception as e:
            logger.error(f"Failed to handle high threat: {e}")
    
    def get_active_alerts(self, threat_level: Optional[ThreatLevel] = None) -> List[SurveillanceAlert]:
        """Récupère les alertes actives"""
        try:
            alerts = list(self.active_alerts.values())
            
            if threat_level:
                alerts = [alert for alert in alerts if alert.threat_level == threat_level]
            
            return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Vérifie si une IP est bloquée"""
        return ip_address in self.blocked_ips
    
    def is_user_suspicious(self, user_id: str) -> bool:
        """Vérifie si un utilisateur est suspect"""
        return user_id in self.suspicious_users
    
    async def analyze_content(self, content: str, content_type: str = "text") -> Dict[str, Any]:
        """Analyse le contenu pour détecter des violations"""
        try:
            # Simulation d'analyse de contenu
            analysis_result = {
                "is_safe": True,
                "risk_score": 0.1,
                "detected_issues": [],
                "content_type": content_type,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Simulation de détection de problèmes
            if "spam" in content.lower():
                analysis_result["is_safe"] = False
                analysis_result["risk_score"] = 0.8
                analysis_result["detected_issues"].append("spam_content")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            return {"is_safe": False, "error": str(e)}
    
    async def get_surveillance_stats(self) -> Dict[str, Any]:
        """Statistiques de surveillance"""
        try:
            stats = {
                "total_alerts": len(self.active_alerts),
                "alerts_by_threat_level": {},
                "blocked_ips": len(self.blocked_ips),
                "suspicious_users": len(self.suspicious_users),
                "monitoring_status": self.is_monitoring,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Compter les alertes par niveau de menace
            for threat_level in ThreatLevel:
                count = len([
                    alert for alert in self.active_alerts.values()
                    if alert.threat_level == threat_level
                ])
                stats["alerts_by_threat_level"][threat_level.value] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get surveillance stats: {e}")
            return {}

# Instance globale
intelligent_surveillance = IntelligentSurveillanceEngine()

# Fonctions d'interface
async def start_surveillance() -> None:
    """Démarre la surveillance intelligente"""
    await intelligent_surveillance.start_monitoring()

async def stop_surveillance() -> None:
    """Arrête la surveillance intelligente"""
    await intelligent_surveillance.stop_monitoring()

async def create_surveillance_alert(event_type: SurveillanceEvent, threat_level: ThreatLevel,
                                  message: str, source_ip: Optional[str] = None,
                                  user_id: Optional[str] = None) -> str:
    """Crée une alerte de surveillance"""
    return await intelligent_surveillance.create_alert(
        event_type, threat_level, message, source_ip, user_id
    )

def get_surveillance_alerts(threat_level: Optional[ThreatLevel] = None) -> List[SurveillanceAlert]:
    """Récupère les alertes de surveillance"""
    return intelligent_surveillance.get_active_alerts(threat_level)

async def analyze_content_surveillance(content: str, content_type: str = "text") -> Dict[str, Any]:
    """Analyse le contenu avec surveillance"""
    return await intelligent_surveillance.analyze_content(content, content_type)

if __name__ == "__main__":
    # Test rapide
    async def test():
        engine = IntelligentSurveillanceEngine()
        await engine.start_monitoring()
        
        alert_id = await engine.create_alert(
            SurveillanceEvent.SUSPICIOUS_ACTIVITY,
            ThreatLevel.MEDIUM,
            "Test surveillance alert"
        )
        
        stats = await engine.get_surveillance_stats()
        print(f"Surveillance stats: {stats}")
        
        await engine.stop_monitoring()
    
    asyncio.run(test())