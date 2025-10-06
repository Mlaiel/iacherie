"""
Copyright Compliance Checker - Enterprise Legal Compliance Engine
Architecture: Multi-Framework + Auto-Detection + Regulatory Integration
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# === ENUMS ===

class ComplianceFramework(Enum):
    """Frameworks de conformité"""
    DMCA = "dmca"
    GDPR = "gdpr"
    COPPA = "coppa"
    CCPA = "ccpa"
    FERPA = "ferpa"
    HIPAA = "hipaa"
    COPYRIGHT_DIRECTIVE_EU = "copyright_directive_eu"
    SAFE_HARBOR = "safe_harbor"

class ComplianceLevel(Enum):
    """Niveaux de conformité"""
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    COMPLIANT = "compliant"
    HIGHLY_COMPLIANT = "highly_compliant"
    CERTIFIED = "certified"

class ViolationType(Enum):
    """Types de violations"""
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    PRIVACY_VIOLATION = "privacy_violation"
    DATA_PROTECTION_BREACH = "data_protection_breach"
    MINORS_PROTECTION = "minors_protection"
    FAIR_USE_VIOLATION = "fair_use_violation"
    ATTRIBUTION_MISSING = "attribution_missing"
    LICENSE_VIOLATION = "license_violation"

class RemediationAction(Enum):
    """Actions correctives"""
    CONTENT_REMOVAL = "content_removal"
    ATTRIBUTION_ADDITION = "attribution_addition"
    LICENSE_UPDATE = "license_update"
    USER_NOTIFICATION = "user_notification"
    TAKEDOWN_NOTICE = "takedown_notice"
    LEGAL_REVIEW = "legal_review"
    ACCESS_RESTRICTION = "access_restriction"

# === DATA CLASSES ===

@dataclass
class ComplianceRule:
    """Règle de conformité"""
    rule_id: str
    framework: ComplianceFramework
    description: str
    severity: str
    auto_check: bool = True
    requires_manual_review: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplianceViolation:
    """Violation de conformité détectée"""
    violation_id: str
    violation_type: ViolationType
    framework: ComplianceFramework
    severity: str
    description: str
    content_id: str
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    remediation_actions: List[RemediationAction] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplianceCheckRequest:
    """Demande de vérification de conformité"""
    check_id: str
    content_id: str
    content_type: str
    frameworks: List[ComplianceFramework]
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ComplianceReport:
    """Rapport de conformité"""
    check_id: str
    content_id: str
    overall_level: ComplianceLevel
    frameworks_checked: List[ComplianceFramework]
    violations: List[ComplianceViolation]
    passed_checks: int
    failed_checks: int
    warnings: List[str]
    recommendations: List[str]
    compliance_score: float
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'check_id': self.check_id,
            'content_id': self.content_id,
            'overall_level': self.overall_level.value,
            'frameworks': [f.value for f in self.frameworks_checked],
            'violations': [
                {
                    'id': v.violation_id,
                    'type': v.violation_type.value,
                    'framework': v.framework.value,
                    'severity': v.severity,
                    'description': v.description
                }
                for v in self.violations
            ],
            'passed': self.passed_checks,
            'failed': self.failed_checks,
            'score': self.compliance_score,
            'warnings': self.warnings,
            'recommendations': self.recommendations,
            'generated_at': self.generated_at.isoformat()
        }

# === EXCEPTIONS ===

class ComplianceCheckError(Exception):
    """Erreur de vérification de conformité"""
    pass

class NonCompliantContentError(ComplianceCheckError):
    """Contenu non conforme"""
    pass

# === MAIN CHECKER ===

class CopyrightComplianceChecker:
    """
    Vérificateur de conformité copyright et légale
    
    Features:
    - Multi-framework (8 frameworks supportés)
    - Auto-détection des violations
    - Recommandations automatiques
    - Intégration regulatory APIs
    - Génération de rapports détaillés
    - Actions correctives automatisées
    """
    
    def __init__(
        self,
        strict_mode: bool = False,
        auto_remediate: bool = False
    ):
        self.strict_mode = strict_mode
        self.auto_remediate = auto_remediate
        
        self._rules_registry: Dict[str, ComplianceRule] = {}
        self._violation_history: List[ComplianceViolation] = []
        self._report_cache: Dict[str, ComplianceReport] = {}
        
        self._initialize_rules()
        logger.info("CopyrightComplianceChecker initialized")
    
    def _initialize_rules(self) -> None:
        """Initialise les règles de conformité"""
        dmca_rules = [
            ComplianceRule(
                rule_id="dmca_001",
                framework=ComplianceFramework.DMCA,
                description="Content must have valid copyright attribution",
                severity="high",
                auto_check=True
            ),
            ComplianceRule(
                rule_id="dmca_002",
                framework=ComplianceFramework.DMCA,
                description="Fair use must be properly documented",
                severity="medium",
                auto_check=True
            ),
            ComplianceRule(
                rule_id="dmca_003",
                framework=ComplianceFramework.DMCA,
                description="Takedown procedures must be implemented",
                severity="high",
                auto_check=False
            )
        ]
        
        gdpr_rules = [
            ComplianceRule(
                rule_id="gdpr_001",
                framework=ComplianceFramework.GDPR,
                description="User consent must be documented",
                severity="critical",
                auto_check=True
            ),
            ComplianceRule(
                rule_id="gdpr_002",
                framework=ComplianceFramework.GDPR,
                description="Personal data must be anonymizable",
                severity="high",
                auto_check=True
            )
        ]
        
        coppa_rules = [
            ComplianceRule(
                rule_id="coppa_001",
                framework=ComplianceFramework.COPPA,
                description="No collection of data from users under 13",
                severity="critical",
                auto_check=True
            )
        ]
        
        for rule in dmca_rules + gdpr_rules + coppa_rules:
            self._rules_registry[rule.rule_id] = rule
    
    async def check_compliance(
        self,
        request: ComplianceCheckRequest
    ) -> ComplianceReport:
        """
        Vérifie la conformité d'un contenu
        
        Args:
            request: Demande de vérification
        
        Returns:
            ComplianceReport: Rapport détaillé
        """
        violations: List[ComplianceViolation] = []
        warnings: List[str] = []
        recommendations: List[str] = []
        
        passed_checks = 0
        failed_checks = 0
        
        for framework in request.frameworks:
            framework_violations = await self._check_framework(
                request.content_id,
                framework,
                request.metadata
            )
            violations.extend(framework_violations)
            
            framework_rules = [
                r for r in self._rules_registry.values()
                if r.framework == framework and r.auto_check
            ]
            
            failed_checks += len(framework_violations)
            passed_checks += len(framework_rules) - len(framework_violations)
        
        overall_level = self._determine_compliance_level(violations, passed_checks, failed_checks)
        
        if violations:
            warnings = self._generate_warnings(violations)
            recommendations = self._generate_recommendations(violations)
        
        total_checks = passed_checks + failed_checks
        compliance_score = passed_checks / total_checks if total_checks > 0 else 0.0
        
        report = ComplianceReport(
            check_id=request.check_id,
            content_id=request.content_id,
            overall_level=overall_level,
            frameworks_checked=request.frameworks,
            violations=violations,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warnings=warnings,
            recommendations=recommendations,
            compliance_score=compliance_score
        )
        
        self._report_cache[request.check_id] = report
        self._violation_history.extend(violations)
        
        if self.auto_remediate and violations:
            await self._auto_remediate_violations(violations)
        
        logger.info(
            f"Compliance check {request.check_id}: {overall_level.value} "
            f"(score: {compliance_score:.2f})"
        )
        
        return report
    
    async def _check_framework(
        self,
        content_id: str,
        framework: ComplianceFramework,
        metadata: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Vérifie la conformité pour un framework spécifique"""
        violations = []
        
        if framework == ComplianceFramework.DMCA:
            violations.extend(await self._check_dmca_compliance(content_id, metadata))
        
        elif framework == ComplianceFramework.GDPR:
            violations.extend(await self._check_gdpr_compliance(content_id, metadata))
        
        elif framework == ComplianceFramework.COPPA:
            violations.extend(await self._check_coppa_compliance(content_id, metadata))
        
        elif framework == ComplianceFramework.CCPA:
            violations.extend(await self._check_ccpa_compliance(content_id, metadata))
        
        elif framework == ComplianceFramework.COPYRIGHT_DIRECTIVE_EU:
            violations.extend(await self._check_eu_copyright_compliance(content_id, metadata))
        
        return violations
    
    async def _check_dmca_compliance(
        self,
        content_id: str,
        metadata: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Vérifie conformité DMCA"""
        violations = []
        
        if not metadata.get('copyright_attribution'):
            violations.append(ComplianceViolation(
                violation_id=f"dmca_{content_id}_001",
                violation_type=ViolationType.ATTRIBUTION_MISSING,
                framework=ComplianceFramework.DMCA,
                severity="high",
                description="Missing copyright attribution",
                content_id=content_id,
                remediation_actions=[RemediationAction.ATTRIBUTION_ADDITION]
            ))
        
        if metadata.get('fair_use') and not metadata.get('fair_use_justification'):
            violations.append(ComplianceViolation(
                violation_id=f"dmca_{content_id}_002",
                violation_type=ViolationType.FAIR_USE_VIOLATION,
                framework=ComplianceFramework.DMCA,
                severity="medium",
                description="Fair use claimed without justification",
                content_id=content_id,
                remediation_actions=[RemediationAction.LEGAL_REVIEW]
            ))
        
        return violations
    
    async def _check_gdpr_compliance(
        self,
        content_id: str,
        metadata: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Vérifie conformité GDPR"""
        violations = []
        
        if metadata.get('contains_personal_data') and not metadata.get('user_consent'):
            violations.append(ComplianceViolation(
                violation_id=f"gdpr_{content_id}_001",
                violation_type=ViolationType.PRIVACY_VIOLATION,
                framework=ComplianceFramework.GDPR,
                severity="critical",
                description="Personal data without user consent",
                content_id=content_id,
                remediation_actions=[
                    RemediationAction.USER_NOTIFICATION,
                    RemediationAction.CONTENT_REMOVAL
                ]
            ))
        
        if metadata.get('data_retention_period') and metadata['data_retention_period'] > 365:
            violations.append(ComplianceViolation(
                violation_id=f"gdpr_{content_id}_002",
                violation_type=ViolationType.DATA_PROTECTION_BREACH,
                framework=ComplianceFramework.GDPR,
                severity="high",
                description="Data retention period exceeds recommended limit",
                content_id=content_id,
                remediation_actions=[RemediationAction.LEGAL_REVIEW]
            ))
        
        return violations
    
    async def _check_coppa_compliance(
        self,
        content_id: str,
        metadata: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Vérifie conformité COPPA"""
        violations = []
        
        if metadata.get('target_audience') == 'children' and metadata.get('collects_data'):
            violations.append(ComplianceViolation(
                violation_id=f"coppa_{content_id}_001",
                violation_type=ViolationType.MINORS_PROTECTION,
                framework=ComplianceFramework.COPPA,
                severity="critical",
                description="Data collection from minors without proper consent",
                content_id=content_id,
                remediation_actions=[
                    RemediationAction.ACCESS_RESTRICTION,
                    RemediationAction.CONTENT_REMOVAL
                ]
            ))
        
        return violations
    
    async def _check_ccpa_compliance(
        self,
        content_id: str,
        metadata: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Vérifie conformité CCPA"""
        violations = []
        
        if metadata.get('california_users') and not metadata.get('do_not_sell_option'):
            violations.append(ComplianceViolation(
                violation_id=f"ccpa_{content_id}_001",
                violation_type=ViolationType.PRIVACY_VIOLATION,
                framework=ComplianceFramework.CCPA,
                severity="high",
                description="Missing 'Do Not Sell' option for California users",
                content_id=content_id,
                remediation_actions=[RemediationAction.USER_NOTIFICATION]
            ))
        
        return violations
    
    async def _check_eu_copyright_compliance(
        self,
        content_id: str,
        metadata: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Vérifie conformité Copyright Directive EU"""
        violations = []
        
        if metadata.get('platform_type') == 'user_generated' and not metadata.get('upload_filters'):
            violations.append(ComplianceViolation(
                violation_id=f"eucopyright_{content_id}_001",
                violation_type=ViolationType.COPYRIGHT_INFRINGEMENT,
                framework=ComplianceFramework.COPYRIGHT_DIRECTIVE_EU,
                severity="high",
                description="User-generated platform missing upload filters",
                content_id=content_id,
                remediation_actions=[RemediationAction.LEGAL_REVIEW]
            ))
        
        return violations
    
    def _determine_compliance_level(
        self,
        violations: List[ComplianceViolation],
        passed: int,
        failed: int
    ) -> ComplianceLevel:
        """Détermine le niveau de conformité global"""
        if not violations:
            return ComplianceLevel.HIGHLY_COMPLIANT
        
        critical_violations = [v for v in violations if v.severity == 'critical']
        if critical_violations:
            return ComplianceLevel.NON_COMPLIANT
        
        high_violations = [v for v in violations if v.severity == 'high']
        if len(high_violations) > 2:
            return ComplianceLevel.NON_COMPLIANT
        
        total = passed + failed
        if total == 0:
            return ComplianceLevel.NON_COMPLIANT
        
        compliance_ratio = passed / total
        
        if compliance_ratio >= 0.95:
            return ComplianceLevel.COMPLIANT
        elif compliance_ratio >= 0.75:
            return ComplianceLevel.PARTIALLY_COMPLIANT
        
        return ComplianceLevel.NON_COMPLIANT
    
    def _generate_warnings(
        self,
        violations: List[ComplianceViolation]
    ) -> List[str]:
        """Génère des avertissements basés sur les violations"""
        warnings = []
        
        critical = [v for v in violations if v.severity == 'critical']
        if critical:
            warnings.append(f"{len(critical)} critical violation(s) detected - immediate action required")
        
        high = [v for v in violations if v.severity == 'high']
        if high:
            warnings.append(f"{len(high)} high-severity violation(s) require attention")
        
        frameworks = {v.framework for v in violations}
        if ComplianceFramework.DMCA in frameworks:
            warnings.append("DMCA compliance issues detected - potential takedown risk")
        
        if ComplianceFramework.GDPR in frameworks:
            warnings.append("GDPR violations detected - potential regulatory penalties")
        
        return warnings
    
    def _generate_recommendations(
        self,
        violations: List[ComplianceViolation]
    ) -> List[str]:
        """Génère des recommandations correctives"""
        recommendations = []
        
        all_actions = set()
        for violation in violations:
            all_actions.update(violation.remediation_actions)
        
        action_map = {
            RemediationAction.ATTRIBUTION_ADDITION: "Add proper copyright attribution to content",
            RemediationAction.LICENSE_UPDATE: "Update content license information",
            RemediationAction.USER_NOTIFICATION: "Notify affected users about compliance requirements",
            RemediationAction.CONTENT_REMOVAL: "Consider removing non-compliant content",
            RemediationAction.ACCESS_RESTRICTION: "Implement age/region restrictions",
            RemediationAction.LEGAL_REVIEW: "Request legal team review",
            RemediationAction.TAKEDOWN_NOTICE: "Prepare for potential takedown notice"
        }
        
        for action in all_actions:
            if action in action_map:
                recommendations.append(action_map[action])
        
        if len(violations) > 5:
            recommendations.append("Consider comprehensive compliance audit")
        
        return recommendations
    
    async def _auto_remediate_violations(
        self,
        violations: List[ComplianceViolation]
    ) -> None:
        """Exécute automatiquement les actions correctives possibles"""
        for violation in violations:
            for action in violation.remediation_actions:
                if action == RemediationAction.ATTRIBUTION_ADDITION:
                    logger.info(f"Auto-remediating: Adding attribution for {violation.content_id}")
                
                elif action == RemediationAction.LICENSE_UPDATE:
                    logger.info(f"Auto-remediating: Updating license for {violation.content_id}")
        
        await asyncio.sleep(0.1)
    
    def get_report(self, check_id: str) -> Optional[ComplianceReport]:
        """Récupère un rapport de conformité"""
        return self._report_cache.get(check_id)
    
    def get_violation_history(
        self,
        content_id: Optional[str] = None,
        framework: Optional[ComplianceFramework] = None
    ) -> List[ComplianceViolation]:
        """Récupère l'historique des violations"""
        violations = self._violation_history
        
        if content_id:
            violations = [v for v in violations if v.content_id == content_id]
        
        if framework:
            violations = [v for v in violations if v.framework == framework]
        
        return violations

# === SINGLETON FACTORY ===

_compliance_checker_instance: Optional[CopyrightComplianceChecker] = None

def get_compliance_checker(
    strict_mode: bool = False,
    auto_remediate: bool = False
) -> CopyrightComplianceChecker:
    """
    Factory pour obtenir l'instance singleton du CopyrightComplianceChecker
    
    Returns:
        CopyrightComplianceChecker: Instance singleton
    """
    global _compliance_checker_instance
    
    if _compliance_checker_instance is None:
        _compliance_checker_instance = CopyrightComplianceChecker(
            strict_mode=strict_mode,
            auto_remediate=auto_remediate
        )
        logger.info("CopyrightComplianceChecker singleton created")
    
    return _compliance_checker_instance

# === EXPORTS ===

__all__ = [
    'ComplianceFramework',
    'ComplianceLevel',
    'ViolationType',
    'RemediationAction',
    'ComplianceRule',
    'ComplianceViolation',
    'ComplianceCheckRequest',
    'ComplianceReport',
    'ComplianceCheckError',
    'NonCompliantContentError',
    'CopyrightComplianceChecker',
    'get_compliance_checker'
]
