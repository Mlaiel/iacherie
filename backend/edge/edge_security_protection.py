"""Edge Security Protection
=========================

Protection sécurité edge ultra-sécurisée pour créateurs Ainflue.
Consolidation de tous les composants security en un système unifié.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, field
import uuid
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class ComplianceFramework(str, Enum):
    """Frameworks de conformité."""
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"


class ComplianceLevel(str, Enum):
    """Niveaux de conformité."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"


@dataclass
class ComplianceRule:
    """Règle de conformité."""
    rule_id: str
    framework: ComplianceFramework
    title: str
    description: str
    severity: str
    check_function: str
    remediation_steps: List[str]


class ComplianceValidationEngine:
    """Moteur validation conformité."""
    
    def __init__(self) -> None:
        self.rules: Dict[str, ComplianceRule] = {}
        self.violations = {}
        self.audit_log = deque(maxlen=1000)
        self._load_default_rules()
    
    def _load_default_rules(self) -> None:
        """Charge les règles de conformité par défaut."""
        default_rules = [
            ComplianceRule(
                rule_id="gdpr_data_encryption",
                framework=ComplianceFramework.GDPR,
                title="Data Encryption at Rest",
                description="All personal data must be encrypted at rest",
                severity="high",
                check_function="check_encryption",
                remediation_steps=["Enable encryption", "Update data handling policies"]
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.rule_id] = rule
    
    async def validate_compliance(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valide la conformité d'une ressource."""
        resource_id = resource_data.get("resource_id", "unknown")
        violations = []
        
        for rule in self.rules.values():
            is_compliant = await self._check_rule_compliance(rule, resource_data)
            
            if not is_compliant:
                violations.append({
                    "rule_id": rule.rule_id,
                    "severity": rule.severity,
                    "description": f"Non-compliance with {rule.title}"
                })
        
        # Calculate compliance score
        total_rules = len(self.rules)
        violations_count = len(violations)
        compliance_score = max(0, (total_rules - violations_count) / total_rules)
        
        result = {
            "resource_id": resource_id,
            "compliance_score": compliance_score,
            "status": ComplianceLevel.COMPLIANT.value if compliance_score >= 0.9 else 
                     ComplianceLevel.PARTIALLY_COMPLIANT.value if compliance_score >= 0.7 else
                     ComplianceLevel.NON_COMPLIANT.value,
            "violations": violations,
            "total_violations": len(violations),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return result
    
    async def _check_rule_compliance(self, rule: ComplianceRule, resource_data: Dict[str, Any]) -> bool:
        """Vérifie la conformité d'une règle."""
        check_function = rule.check_function
        
        if check_function == "check_encryption":
            return resource_data.get("encrypted", False)
        elif check_function == "check_retention":
            retention_days = resource_data.get("retention_days", 0)
            return retention_days <= 365
        
        return True


class DDoSAttackType(str, Enum):
    """Types d'attaques DDoS."""
    VOLUMETRIC = "volumetric"
    PROTOCOL = "protocol"
    APPLICATION = "application"


class MitigationStrategy(str, Enum):
    """Stratégies de mitigation."""
    RATE_LIMITING = "rate_limiting"
    IP_BLOCKING = "ip_blocking"
    TRAFFIC_FILTERING = "traffic_filtering"


@dataclass
class DDoSAttack:
    """Attaque DDoS détectée."""
    attack_id: str
    attack_type: DDoSAttackType
    source_ips: List[str]
    target_ip: str
    start_time: datetime
    peak_traffic: float
    current_traffic: float
    status: str = "active"
    mitigation_applied: List[MitigationStrategy] = field(default_factory=list)


class DDoSProtectionAdvanced:
    """Protection DDoS avancée."""
    
    def __init__(self) -> None:
        self.detection_thresholds = {
            "requests_per_second": 1000,
            "bandwidth_mbps": 100,
            "connection_count": 10000
        }
        self.active_attacks: Dict[str, DDoSAttack] = {}
        self.blocked_ips: Set[str] = set()
        self.rate_limits: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.traffic_patterns = defaultdict(list)
        self.mitigation_stats = defaultdict(int)
    
    async def detect_ddos_attack(self, traffic_data: Dict[str, Any]) -> Optional[DDoSAttack]:
        """Détecte une attaque DDoS."""
        source_ip = traffic_data.get("source_ip", "unknown")
        request_rate = traffic_data.get("requests_per_second", 0)
        bandwidth = traffic_data.get("bandwidth_mbps", 0)
        
        # Detection logic
        attack_type = None
        
        if request_rate > self.detection_thresholds["requests_per_second"]:
            attack_type = DDoSAttackType.APPLICATION
        elif bandwidth > self.detection_thresholds["bandwidth_mbps"]:
            attack_type = DDoSAttackType.VOLUMETRIC
        
        if attack_type:
            attack = DDoSAttack(
                attack_id=str(uuid.uuid4()),
                attack_type=attack_type,
                source_ips=[source_ip],
                target_ip=traffic_data.get("target_ip", "unknown"),
                start_time=datetime.utcnow(),
                peak_traffic=bandwidth,
                current_traffic=bandwidth
            )
            
            self.active_attacks[attack.attack_id] = attack
            logger.warning(f"DDoS attack detected: {attack_type.value} from {source_ip}")
            
            return attack
        
        return None
    
    async def mitigate_ddos_attack(self, attack_id: str) -> Dict[str, Any]:
        """Mitigue une attaque DDoS."""
        if attack_id not in self.active_attacks:
            return {"error": "Attack not found"}
        
        attack = self.active_attacks[attack_id]
        mitigation_results = []
        
        # Apply mitigation strategies
        if attack.attack_type == DDoSAttackType.APPLICATION:
            await self._apply_rate_limiting(attack)
            mitigation_results.append("rate_limiting_applied")
            attack.mitigation_applied.append(MitigationStrategy.RATE_LIMITING)
        
        elif attack.attack_type == DDoSAttackType.VOLUMETRIC:
            await self._apply_ip_blocking(attack)
            mitigation_results.append("ip_blocking_applied")
            attack.mitigation_applied.append(MitigationStrategy.IP_BLOCKING)
        
        attack.status = "mitigated"
        self.mitigation_stats[attack.attack_type.value] += 1
        
        return {
            "attack_id": attack_id,
            "mitigation_applied": mitigation_results,
            "status": "mitigated",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _apply_rate_limiting(self, attack -> None: DDoSAttack) -> None:
        """Applique la limitation de débit."""
        for ip in attack.source_ips:
            self.rate_limits[ip] = {
                "max_requests": 10,
                "window": 1,
                "applied_at": datetime.utcnow()
            }
    
    async def _apply_ip_blocking(self, attack -> None: DDoSAttack) -> None:
        """Applique le blocage d'IP."""
        for ip in attack.source_ips:
            self.blocked_ips.add(ip)
    
    async def get_protection_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de protection."""
        return {
            "active_attacks": len(self.active_attacks),
            "blocked_ips": len(self.blocked_ips),
            "mitigation_stats": dict(self.mitigation_stats),
            "rate_limited_ips": len(self.rate_limits),
            "protection_status": "active"
        }


class EdgeSecurityProtection:
    """Protection sécurité edge ultra-sécurisée."""
    
    def __init__(self) -> None:
        self.compliance_engine = ComplianceValidationEngine()
        self.ddos_protection = DDoSProtectionAdvanced()
        
        self.security_metrics = {
            "total_threats_blocked": 0,
            "security_score": 95.0,
            "compliance_score": 90.0,
            "active_protections": 2
        }
    
    async def validate_compliance(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valide la conformité."""
        result = await self.compliance_engine.validate_compliance(resource_data)
        self.security_metrics["compliance_score"] = result["compliance_score"] * 100
        return result
    
    async def protect_against_ddos(self, traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Protège contre les attaques DDoS."""
        attack = await self.ddos_protection.detect_ddos_attack(traffic_data)
        
        if attack:
            mitigation_result = await self.ddos_protection.mitigate_ddos_attack(attack.attack_id)
            self.security_metrics["total_threats_blocked"] += 1
            return {
                "attack_detected": True,
                "attack_type": attack.attack_type.value,
                "mitigation": mitigation_result
            }
        
        return {"attack_detected": False, "status": "clean"}
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de sécurité globales."""
        compliance_stats = await self.compliance_engine.validate_compliance({"resource_id": "global"})
        ddos_stats = await self.ddos_protection.get_protection_stats()
        
        return {
            "global_metrics": self.security_metrics,
            "compliance": {
                "score": compliance_stats["compliance_score"] * 100,
                "status": compliance_stats["status"]
            },
            "ddos_protection": ddos_stats,
            "overall_security_posture": "strong" if self.security_metrics["security_score"] >= 90 else
                                       "good" if self.security_metrics["security_score"] >= 80 else
                                       "needs_improvement"
        }
    
    async def shutdown(self) -> None:
        """Arrête le système de protection."""
        logger.info("Shutting down EdgeSecurityProtection")


def create_edge_security_protection() -> EdgeSecurityProtection:
    """Factory function pour créer une instance de protection sécurité."""
    return EdgeSecurityProtection()


__all__ = [
    "EdgeSecurityProtection",
    "ComplianceValidationEngine",
    "DDoSProtectionAdvanced", 
    "ComplianceFramework",
    "ComplianceLevel",
    "DDoSAttackType",
    "MitigationStrategy",
    "create_edge_security_protection"
]
