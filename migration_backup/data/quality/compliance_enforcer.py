"""
⚖️ COMPLIANCE ENFORCER - REGULATORY COMPLIANCE & GOVERNANCE
Data Quality Module - Phase 3 Implementation

🚨 PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel - TOUS DROITS RÉSERVÉS
Toute utilisation non autorisée sera poursuivie en justice.

Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from pathlib import Path

# Data analysis
import pandas as pd


class ComplianceStandard(str, Enum):
    """Standards de conformité"""
    GDPR = "gdpr"  # General Data Protection Regulation
    CCPA = "ccpa"  # California Consumer Privacy Act
    DMCA = "dmca"  # Digital Millennium Copyright Act
    SOC2 = "soc2"  # Service Organization Control 2
    ISO27001 = "iso27001"  # Information Security Management
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    OWASP = "owasp"  # Open Web Application Security Project
    NIST = "nist"  # National Institute of Standards and Technology


class ComplianceLevel(str, Enum):
    """Niveaux de conformité"""
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    REQUIRES_REVIEW = "requires_review"
    UNKNOWN = "unknown"


class ViolationType(str, Enum):
    """Types de violations"""
    DATA_PROTECTION = "data_protection"
    PRIVACY = "privacy"
    SECURITY = "security"
    COPYRIGHT = "copyright"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    DOCUMENTATION = "documentation"


@dataclass
class ComplianceRule:
    """Règle de conformité"""
    rule_id: str
    standard: ComplianceStandard
    title: str
    description: str
    requirements: List[str]
    validation_function: str
    severity: str = "medium"
    applicable_data_types: List[str] = field(default_factory=list)
    remediation_steps: List[str] = field(default_factory=list)


@dataclass
class ComplianceViolation:
    """Violation de conformité"""
    violation_id: str
    rule: ComplianceRule
    violation_type: ViolationType
    severity: str
    description: str
    evidence: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data_subject: Optional[str] = None
    remediation_required: bool = True
    deadline: Optional[datetime] = None


@dataclass
class ComplianceResult:
    """Résultat d'évaluation de conformité"""
    standard: ComplianceStandard
    level: ComplianceLevel
    score: float
    violations: List[ComplianceViolation]
    recommendations: List[str]
    evaluation_timestamp: datetime = field(default_factory=datetime.utcnow)
    next_review_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class GDPREnforcer:
    """Enforceur GDPR"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rules = self._initialize_gdpr_rules()
    
    def _initialize_gdpr_rules(self) -> List[ComplianceRule]:
        """Initialisation des règles GDPR"""
        return [
            ComplianceRule(
                rule_id="GDPR-01",
                standard=ComplianceStandard.GDPR,
                title="Consentement explicite requis",
                description="Le traitement de données personnelles nécessite un consentement explicite",
                requirements=[
                    "Obtenir consentement explicite avant traitement",
                    "Documenter la base juridique du traitement",
                    "Permettre retrait du consentement"
                ],
                validation_function="validate_consent",
                severity="high",
                applicable_data_types=["personal_data"],
                remediation_steps=[
                    "Implémenter système de consentement",
                    "Documenter base juridique",
                    "Créer processus de retrait"
                ]
            ),
            ComplianceRule(
                rule_id="GDPR-02",
                standard=ComplianceStandard.GDPR,
                title="Droit à l'effacement",
                description="Les individus ont le droit de demander l'effacement de leurs données",
                requirements=[
                    "Implémenter fonctionnalité d'effacement",
                    "Traiter demandes dans 30 jours",
                    "Notifier les tiers si applicable"
                ],
                validation_function="validate_right_to_erasure",
                severity="high",
                applicable_data_types=["personal_data"],
                remediation_steps=[
                    "Créer processus d'effacement",
                    "Former équipe sur procédures",
                    "Mettre en place suivi des demandes"
                ]
            ),
            ComplianceRule(
                rule_id="GDPR-03",
                standard=ComplianceStandard.GDPR,
                title="Notification de violation",
                description="Les violations de données doivent être notifiées dans 72h",
                requirements=[
                    "Détecter violations dans 24h",
                    "Notifier autorité dans 72h",
                    "Notifier individus si risque élevé"
                ],
                validation_function="validate_breach_notification",
                severity="critical",
                applicable_data_types=["personal_data"],
                remediation_steps=[
                    "Mettre en place monitoring",
                    "Créer processus de notification",
                    "Former équipe réponse incidents"
                ]
            )
        ]
    
    def validate_consent(self, data: Dict[str, Any]) -> List[ComplianceViolation]:
        """Validation du consentement GDPR"""
        violations = []
        
        # Vérification présence consentement
        if 'consent' not in data or not data['consent']:
            violations.append(ComplianceViolation(
                violation_id=f"GDPR-01-{int(datetime.utcnow().timestamp())}",
                rule=next(r for r in self.rules if r.rule_id == "GDPR-01"),
                violation_type=ViolationType.PRIVACY,
                severity="high",
                description="Consentement manquant pour traitement données personnelles",
                evidence={"consent_present": False, "data_keys": list(data.keys())},
                data_subject=data.get('user_id'),
                deadline=datetime.utcnow() + timedelta(days=7)
            ))
        
        # Vérification consentement explicite
        if data.get('consent') == 'implicit':
            violations.append(ComplianceViolation(
                violation_id=f"GDPR-01-{int(datetime.utcnow().timestamp())}-2",
                rule=next(r for r in self.rules if r.rule_id == "GDPR-01"),
                violation_type=ViolationType.PRIVACY,
                severity="medium",
                description="Consentement implicite non suffisant sous GDPR",
                evidence={"consent_type": "implicit"},
                data_subject=data.get('user_id'),
                deadline=datetime.utcnow() + timedelta(days=14)
            ))
        
        # Vérification spécificité du consentement
        if 'consent_purposes' not in data or not data['consent_purposes']:
            violations.append(ComplianceViolation(
                violation_id=f"GDPR-01-{int(datetime.utcnow().timestamp())}-3",
                rule=next(r for r in self.rules if r.rule_id == "GDPR-01"),
                violation_type=ViolationType.PRIVACY,
                severity="medium",
                description="Consentement doit être spécifique aux finalités",
                evidence={"purposes_specified": False},
                data_subject=data.get('user_id'),
                deadline=datetime.utcnow() + timedelta(days=14)
            ))
        
        return violations
    
    def validate_right_to_erasure(self, data: Dict[str, Any]) -> List[ComplianceViolation]:
        """Validation droit à l'effacement"""
        violations = []
        
        # Vérification mécanisme d'effacement
        if 'erasure_mechanism' not in data or not data['erasure_mechanism']:
            violations.append(ComplianceViolation(
                violation_id=f"GDPR-02-{int(datetime.utcnow().timestamp())}",
                rule=next(r for r in self.rules if r.rule_id == "GDPR-02"),
                violation_type=ViolationType.PRIVACY,
                severity="high",
                description="Mécanisme d'effacement des données manquant",
                evidence={"erasure_mechanism_present": False},
                deadline=datetime.utcnow() + timedelta(days=30)
            ))
        
        # Vérification délai de traitement
        if data.get('erasure_response_time_days', 0) > 30:
            violations.append(ComplianceViolation(
                violation_id=f"GDPR-02-{int(datetime.utcnow().timestamp())}-2",
                rule=next(r for r in self.rules if r.rule_id == "GDPR-02"),
                violation_type=ViolationType.OPERATIONAL,
                severity="medium",
                description="Délai de réponse effacement dépasse 30 jours",
                evidence={"response_time": data.get('erasure_response_time_days')},
                deadline=datetime.utcnow() + timedelta(days=14)
            ))
        
        return violations
    
    def validate_breach_notification(self, data: Dict[str, Any]) -> List[ComplianceViolation]:
        """Validation notification de violation"""
        violations = []
        
        # Vérification système de détection
        if 'breach_detection' not in data or not data['breach_detection']:
            violations.append(ComplianceViolation(
                violation_id=f"GDPR-03-{int(datetime.utcnow().timestamp())}",
                rule=next(r for r in self.rules if r.rule_id == "GDPR-03"),
                violation_type=ViolationType.SECURITY,
                severity="critical",
                description="Système de détection de violation manquant",
                evidence={"breach_detection_present": False},
                deadline=datetime.utcnow() + timedelta(days=3)
            ))
        
        # Vérification délai de notification
        if data.get('breach_notification_hours', 0) > 72:
            violations.append(ComplianceViolation(
                violation_id=f"GDPR-03-{int(datetime.utcnow().timestamp())}-2",
                rule=next(r for r in self.rules if r.rule_id == "GDPR-03"),
                violation_type=ViolationType.OPERATIONAL,
                severity="critical",
                description="Délai notification violation dépasse 72h",
                evidence={"notification_hours": data.get('breach_notification_hours')},
                deadline=datetime.utcnow() + timedelta(days=1)
            ))
        
        return violations


class DMCAEnforcer:
    """Enforceur DMCA"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rules = self._initialize_dmca_rules()
    
    def _initialize_dmca_rules(self) -> List[ComplianceRule]:
        """Initialisation des règles DMCA"""
        return [
            ComplianceRule(
                rule_id="DMCA-01",
                standard=ComplianceStandard.DMCA,
                title="Processus de retrait DMCA",
                description="Système de retrait de contenu protégé par copyright",
                requirements=[
                    "Processus de notification DMCA",
                    "Retrait rapide contenu signalé",
                    "Processus de contre-notification"
                ],
                validation_function="validate_takedown_process",
                severity="high",
                applicable_data_types=["content", "media"],
                remediation_steps=[
                    "Implémenter système DMCA",
                    "Former équipe modération",
                    "Créer processus légal"
                ]
            ),
            ComplianceRule(
                rule_id="DMCA-02",
                standard=ComplianceStandard.DMCA,
                title="Agent DMCA désigné",
                description="Agent désigné pour recevoir notifications DMCA",
                requirements=[
                    "Désigner agent DMCA",
                    "Publier informations contact",
                    "Enregistrer auprès Copyright Office"
                ],
                validation_function="validate_dmca_agent",
                severity="high",
                applicable_data_types=["organizational"],
                remediation_steps=[
                    "Désigner agent officiel",
                    "Publier coordonnées",
                    "Effectuer enregistrement"
                ]
            )
        ]
    
    def validate_takedown_process(self, data: Dict[str, Any]) -> List[ComplianceViolation]:
        """Validation processus de retrait DMCA"""
        violations = []
        
        # Vérification processus de notification
        if 'dmca_notification_process' not in data or not data['dmca_notification_process']:
            violations.append(ComplianceViolation(
                violation_id=f"DMCA-01-{int(datetime.utcnow().timestamp())}",
                rule=next(r for r in self.rules if r.rule_id == "DMCA-01"),
                violation_type=ViolationType.COPYRIGHT,
                severity="high",
                description="Processus de notification DMCA manquant",
                evidence={"notification_process_present": False},
                deadline=datetime.utcnow() + timedelta(days=14)
            ))
        
        # Vérification délai de retrait
        if data.get('takedown_response_hours', 0) > 24:
            violations.append(ComplianceViolation(
                violation_id=f"DMCA-01-{int(datetime.utcnow().timestamp())}-2",
                rule=next(r for r in self.rules if r.rule_id == "DMCA-01"),
                violation_type=ViolationType.OPERATIONAL,
                severity="medium",
                description="Délai de retrait DMCA trop long (>24h)",
                evidence={"takedown_hours": data.get('takedown_response_hours')},
                deadline=datetime.utcnow() + timedelta(days=7)
            ))
        
        return violations
    
    def validate_dmca_agent(self, data: Dict[str, Any]) -> List[ComplianceViolation]:
        """Validation agent DMCA"""
        violations = []
        
        # Vérification agent désigné
        if 'dmca_agent' not in data or not data['dmca_agent']:
            violations.append(ComplianceViolation(
                violation_id=f"DMCA-02-{int(datetime.utcnow().timestamp())}",
                rule=next(r for r in self.rules if r.rule_id == "DMCA-02"),
                violation_type=ViolationType.OPERATIONAL,
                severity="high",
                description="Agent DMCA non désigné",
                evidence={"dmca_agent_present": False},
                deadline=datetime.utcnow() + timedelta(days=30)
            ))
        
        # Vérification informations publiques
        if 'dmca_contact_public' not in data or not data['dmca_contact_public']:
            violations.append(ComplianceViolation(
                violation_id=f"DMCA-02-{int(datetime.utcnow().timestamp())}-2",
                rule=next(r for r in self.rules if r.rule_id == "DMCA-02"),
                violation_type=ViolationType.DOCUMENTATION,
                severity="medium",
                description="Informations contact agent DMCA non publiques",
                evidence={"contact_info_public": False},
                deadline=datetime.utcnow() + timedelta(days=14)
            ))
        
        return violations


class SOC2Enforcer:
    """Enforceur SOC 2"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rules = self._initialize_soc2_rules()
    
    def _initialize_soc2_rules(self) -> List[ComplianceRule]:
        """Initialisation des règles SOC 2"""
        return [
            ComplianceRule(
                rule_id="SOC2-01",
                standard=ComplianceStandard.SOC2,
                title="Contrôles d'accès logique",
                description="Contrôles d'accès appropriés aux systèmes",
                requirements=[
                    "Authentification multi-facteurs",
                    "Principe du moindre privilège",
                    "Révision périodique des accès"
                ],
                validation_function="validate_access_controls",
                severity="high",
                applicable_data_types=["system_access"],
                remediation_steps=[
                    "Implémenter MFA",
                    "Réviser privilèges",
                    "Documenter contrôles"
                ]
            ),
            ComplianceRule(
                rule_id="SOC2-02",
                standard=ComplianceStandard.SOC2,
                title="Surveillance système",
                description="Monitoring et logging des activités système",
                requirements=[
                    "Logs d'activité complets",
                    "Monitoring temps réel",
                    "Alertes automatisées"
                ],
                validation_function="validate_system_monitoring",
                severity="medium",
                applicable_data_types=["system_logs"],
                remediation_steps=[
                    "Activer logging complet",
                    "Configurer monitoring",
                    "Paramétrer alertes"
                ]
            )
        ]
    
    def validate_access_controls(self, data: Dict[str, Any]) -> List[ComplianceViolation]:
        """Validation contrôles d'accès SOC 2"""
        violations = []
        
        # Vérification MFA
        if 'mfa_enabled' not in data or not data['mfa_enabled']:
            violations.append(ComplianceViolation(
                violation_id=f"SOC2-01-{int(datetime.utcnow().timestamp())}",
                rule=next(r for r in self.rules if r.rule_id == "SOC2-01"),
                violation_type=ViolationType.SECURITY,
                severity="high",
                description="Authentification multi-facteurs non activée",
                evidence={"mfa_enabled": False},
                deadline=datetime.utcnow() + timedelta(days=14)
            ))
        
        # Vérification principe moindre privilège
        if data.get('privilege_level', 'high') == 'high':
            violations.append(ComplianceViolation(
                violation_id=f"SOC2-01-{int(datetime.utcnow().timestamp())}-2",
                rule=next(r for r in self.rules if r.rule_id == "SOC2-01"),
                violation_type=ViolationType.SECURITY,
                severity="medium",
                description="Privilèges excessifs détectés",
                evidence={"privilege_level": data.get('privilege_level')},
                deadline=datetime.utcnow() + timedelta(days=21)
            ))
        
        return violations
    
    def validate_system_monitoring(self, data: Dict[str, Any]) -> List[ComplianceViolation]:
        """Validation surveillance système SOC 2"""
        violations = []
        
        # Vérification logging
        if 'logging_enabled' not in data or not data['logging_enabled']:
            violations.append(ComplianceViolation(
                violation_id=f"SOC2-02-{int(datetime.utcnow().timestamp())}",
                rule=next(r for r in self.rules if r.rule_id == "SOC2-02"),
                violation_type=ViolationType.OPERATIONAL,
                severity="medium",
                description="Logging système non activé",
                evidence={"logging_enabled": False},
                deadline=datetime.utcnow() + timedelta(days=7)
            ))
        
        # Vérification monitoring temps réel
        if 'real_time_monitoring' not in data or not data['real_time_monitoring']:
            violations.append(ComplianceViolation(
                violation_id=f"SOC2-02-{int(datetime.utcnow().timestamp())}-2",
                rule=next(r for r in self.rules if r.rule_id == "SOC2-02"),
                violation_type=ViolationType.OPERATIONAL,
                severity="medium",
                description="Monitoring temps réel non configuré",
                evidence={"real_time_monitoring": False},
                deadline=datetime.utcnow() + timedelta(days=14)
            ))
        
        return violations


class AdvancedComplianceEnforcer:
    """Enforceur de conformité avancé enterprise"""
    
    def __init__(self, enabled_standards: Optional[List[ComplianceStandard]] = None):
        self.enabled_standards = enabled_standards or [
            ComplianceStandard.GDPR,
            ComplianceStandard.DMCA,
            ComplianceStandard.SOC2,
            ComplianceStandard.OWASP
        ]
        
        # Enforceurs spécialisés
        self.gdpr_enforcer = GDPREnforcer()
        self.dmca_enforcer = DMCAEnforcer()
        self.soc2_enforcer = SOC2Enforcer()
        
        # Registre des évaluations
        self.compliance_history: List[ComplianceResult] = []
        
        self.logger = logging.getLogger(__name__)
    
    async def evaluate_compliance(self, data: Dict[str, Any], 
                                standards: Optional[List[ComplianceStandard]] = None) -> Dict[ComplianceStandard, ComplianceResult]:
        """Évaluation complète de conformité"""
        standards_to_check = standards or self.enabled_standards
        results = {}
        
        for standard in standards_to_check:
            try:
                result = await self._evaluate_standard(standard, data)
                results[standard] = result
                self.compliance_history.append(result)
                
            except Exception as e:
                self.logger.error(f"Error evaluating {standard.value}: {e}")
                results[standard] = ComplianceResult(
                    standard=standard,
                    level=ComplianceLevel.UNKNOWN,
                    score=0.0,
                    violations=[],
                    recommendations=[f"Erreur d'évaluation: {str(e)}"]
                )
        
        return results
    
    async def _evaluate_standard(self, standard: ComplianceStandard, 
                                data: Dict[str, Any]) -> ComplianceResult:
        """Évaluation d'un standard spécifique"""
        violations = []
        recommendations = []
        
        if standard == ComplianceStandard.GDPR:
            violations.extend(self.gdpr_enforcer.validate_consent(data))
            violations.extend(self.gdpr_enforcer.validate_right_to_erasure(data))
            violations.extend(self.gdpr_enforcer.validate_breach_notification(data))
            
        elif standard == ComplianceStandard.DMCA:
            violations.extend(self.dmca_enforcer.validate_takedown_process(data))
            violations.extend(self.dmca_enforcer.validate_dmca_agent(data))
            
        elif standard == ComplianceStandard.SOC2:
            violations.extend(self.soc2_enforcer.validate_access_controls(data))
            violations.extend(self.soc2_enforcer.validate_system_monitoring(data))
        
        # Calcul score et niveau conformité
        critical_violations = [v for v in violations if v.severity == "critical"]
        high_violations = [v for v in violations if v.severity == "high"]
        
        if critical_violations:
            level = ComplianceLevel.NON_COMPLIANT
            score = 0.0
        elif high_violations:
            level = ComplianceLevel.PARTIALLY_COMPLIANT
            score = 0.5
        elif violations:
            level = ComplianceLevel.REQUIRES_REVIEW
            score = 0.8
        else:
            level = ComplianceLevel.COMPLIANT
            score = 1.0
        
        # Recommandations
        if violations:
            recommendations.append(f"Corriger {len(violations)} violations identifiées")
            recommendations.append("Implémenter mesures correctives dans délais")
            recommendations.append("Programmer revue de conformité dans 30 jours")
        else:
            recommendations.append("Maintenir pratiques de conformité actuelles")
            recommendations.append("Programmer audit annuel")
        
        return ComplianceResult(
            standard=standard,
            level=level,
            score=score,
            violations=violations,
            recommendations=recommendations,
            next_review_date=datetime.utcnow() + timedelta(days=90),
            metadata={
                "total_rules_checked": self._get_rules_count(standard),
                "data_types_assessed": list(data.keys())
            }
        )
    
    def _get_rules_count(self, standard: ComplianceStandard) -> int:
        """Nombre de règles par standard"""
        counts = {
            ComplianceStandard.GDPR: len(self.gdpr_enforcer.rules),
            ComplianceStandard.DMCA: len(self.dmca_enforcer.rules),
            ComplianceStandard.SOC2: len(self.soc2_enforcer.rules)
        }
        return counts.get(standard, 0)
    
    def generate_compliance_report(self, period_days: int = 30) -> Dict[str, Any]:
        """Génération rapport de conformité"""
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        recent_evaluations = [
            eval for eval in self.compliance_history 
            if eval.evaluation_timestamp >= cutoff_date
        ]
        
        if not recent_evaluations:
            return {
                "period_days": period_days,
                "message": "Aucune évaluation récente",
                "recommendation": "Effectuer évaluation de conformité"
            }
        
        # Statistiques par standard
        by_standard = {}
        for eval in recent_evaluations:
            standard = eval.standard.value
            if standard not in by_standard:
                by_standard[standard] = {
                    "evaluations": 0,
                    "average_score": 0.0,
                    "compliance_level": ComplianceLevel.UNKNOWN.value,
                    "total_violations": 0
                }
            
            by_standard[standard]["evaluations"] += 1
            by_standard[standard]["average_score"] += eval.score
            by_standard[standard]["total_violations"] += len(eval.violations)
            by_standard[standard]["compliance_level"] = eval.level.value
        
        # Calcul moyennes
        for standard_data in by_standard.values():
            if standard_data["evaluations"] > 0:
                standard_data["average_score"] /= standard_data["evaluations"]
        
        # Violations par type
        all_violations = []
        for eval in recent_evaluations:
            all_violations.extend(eval.violations)
        
        violations_by_type = {}
        for violation in all_violations:
            v_type = violation.violation_type.value
            violations_by_type[v_type] = violations_by_type.get(v_type, 0) + 1
        
        # Score global
        total_score = sum(eval.score for eval in recent_evaluations)
        global_score = total_score / len(recent_evaluations) if recent_evaluations else 0
        
        # Niveau global
        if global_score >= 0.9:
            global_level = ComplianceLevel.COMPLIANT.value
        elif global_score >= 0.7:
            global_level = ComplianceLevel.PARTIALLY_COMPLIANT.value
        else:
            global_level = ComplianceLevel.NON_COMPLIANT.value
        
        return {
            "report_period": {
                "days": period_days,
                "start_date": cutoff_date.isoformat(),
                "end_date": datetime.utcnow().isoformat()
            },
            "global_compliance": {
                "level": global_level,
                "score": round(global_score, 3),
                "total_evaluations": len(recent_evaluations),
                "total_violations": len(all_violations)
            },
            "by_standard": by_standard,
            "violations_analysis": {
                "by_type": violations_by_type,
                "critical_count": len([v for v in all_violations if v.severity == "critical"]),
                "high_count": len([v for v in all_violations if v.severity == "high"]),
                "medium_count": len([v for v in all_violations if v.severity == "medium"])
            },
            "recommendations": [
                "Traiter violations critiques en priorité",
                "Mettre en place actions correctives",
                "Programmer formations équipe",
                "Réviser politiques de conformité"
            ],
            "next_actions": [
                "Audit complet dans 30 jours",
                "Revue des processus de conformité",
                "Mise à jour documentation"
            ]
        }
    
    def get_pending_violations(self) -> List[ComplianceViolation]:
        """Récupération violations en attente"""
        pending = []
        for eval in self.compliance_history:
            for violation in eval.violations:
                if violation.remediation_required and violation.deadline:
                    if violation.deadline > datetime.utcnow():
                        pending.append(violation)
        
        # Tri par deadline
        pending.sort(key=lambda x: x.deadline or datetime.utcnow())
        return pending
    
    def mark_violation_resolved(self, violation_id: str) -> bool:
        """Marquer violation comme résolue"""
        for eval in self.compliance_history:
            for violation in eval.violations:
                if violation.violation_id == violation_id:
                    violation.remediation_required = False
                    self.logger.info(f"Violation {violation_id} marked as resolved")
                    return True
        return False
    
    async def schedule_compliance_review(self, standard: ComplianceStandard, 
                                       review_date: datetime) -> Dict[str, Any]:
        """Planification revue conformité"""
        return {
            "standard": standard.value,
            "review_date": review_date.isoformat(),
            "status": "scheduled",
            "reminder_date": (review_date - timedelta(days=7)).isoformat(),
            "preparation_checklist": [
                "Préparer documentation conformité",
                "Réviser politiques et procédures",
                "Identifier changements réglementaires",
                "Planifier formation équipe"
            ]
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification santé du système de conformité"""
        pending_violations = self.get_pending_violations()
        overdue_violations = [
            v for v in pending_violations 
            if v.deadline and v.deadline < datetime.utcnow()
        ]
        
        return {
            "status": "unhealthy" if overdue_violations else "healthy",
            "enabled_standards": [s.value for s in self.enabled_standards],
            "total_evaluations": len(self.compliance_history),
            "pending_violations": len(pending_violations),
            "overdue_violations": len(overdue_violations),
            "last_evaluation": max(
                [e.evaluation_timestamp for e in self.compliance_history], 
                default=datetime.utcnow()
            ).isoformat() if self.compliance_history else None,
            "recommendations": [
                "Traiter violations en retard" if overdue_violations else "Continuer surveillance",
                "Maintenir évaluations régulières",
                "Former équipe aux nouveaux règlements"
            ]
        }


# Service singleton
compliance_enforcer = AdvancedComplianceEnforcer()


async def get_compliance_enforcer() -> AdvancedComplianceEnforcer:
    """Factory function pour enforceur conformité"""
    return compliance_enforcer


# Export des classes principales
__all__ = [
    'AdvancedComplianceEnforcer',
    'GDPREnforcer',
    'DMCAEnforcer',
    'SOC2Enforcer',
    'ComplianceStandard',
    'ComplianceLevel',
    'ViolationType',
    'ComplianceRule',
    'ComplianceViolation',
    'ComplianceResult',
    'compliance_enforcer',
    'get_compliance_enforcer'
]


# Exemple d'utilisation
if __name__ == "__main__":
    async def main():
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        
        # Initialisation enforceur
        enforcer = AdvancedComplianceEnforcer()
        
        # Données de test
        test_data = {
            "consent": "explicit",
            "consent_purposes": ["marketing", "analytics"],
            "erasure_mechanism": True,
            "erasure_response_time_days": 25,
            "breach_detection": True,
            "breach_notification_hours": 48,
            "dmca_notification_process": True,
            "takedown_response_hours": 12,
            "dmca_agent": "legal@company.com",
            "dmca_contact_public": True,
            "mfa_enabled": True,
            "privilege_level": "medium",
            "logging_enabled": True,
            "real_time_monitoring": False,
            "user_id": "user123"
        }
        
        try:
            # Évaluation conformité
            results = await enforcer.evaluate_compliance(test_data)
            
            print("=== RÉSULTATS CONFORMITÉ ===")
            for standard, result in results.items():
                print(f"\n{standard.value.upper()}:")
                print(f"  Niveau: {result.level.value}")
                print(f"  Score: {result.score:.2f}")
                print(f"  Violations: {len(result.violations)}")
                
                for violation in result.violations[:3]:  # Top 3
                    print(f"    - {violation.description}")
            
            # Rapport de conformité
            compliance_report = enforcer.generate_compliance_report()
            print(f"\n=== RAPPORT CONFORMITÉ ===")
            print(f"Score global: {compliance_report['global_compliance']['score']:.2f}")
            print(f"Niveau: {compliance_report['global_compliance']['level']}")
            print(f"Total violations: {compliance_report['global_compliance']['total_violations']}")
            
            # Violations en attente
            pending = enforcer.get_pending_violations()
            print(f"\nViolations en attente: {len(pending)}")
            
            # Vérification santé
            health = await enforcer.health_check()
            print(f"Statut système: {health['status']}")
            
        except Exception as e:
            print(f"Error in compliance test: {e}")
    
    # Exécution test
    asyncio.run(main())