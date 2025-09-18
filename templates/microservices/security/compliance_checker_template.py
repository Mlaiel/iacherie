"""
⚠️ AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Compliance Checker Template for Ainflue Creator Economy Platform
Automated compliance verification and monitoring for GDPR, SOC2, HIPAA, PCI-DSS and other frameworks
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import re
import hashlib

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, validator
from redis import Redis
import logging
from prometheus_client import Counter, Histogram, Gauge


class ComplianceFramework(str, Enum):
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    SOC2 = "soc2"
    NIST = "nist"
    FedRAMP = "fedramp"


class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNKNOWN = "unknown"
    PENDING_REVIEW = "pending_review"


class ViolationSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ControlCategory(str, Enum):
    ACCESS_CONTROL = "access_control"
    DATA_PROTECTION = "data_protection"
    INCIDENT_RESPONSE = "incident_response"
    RISK_MANAGEMENT = "risk_management"
    AUDIT_LOGGING = "audit_logging"
    ENCRYPTION = "encryption"
    NETWORK_SECURITY = "network_security"
    PERSONNEL_SECURITY = "personnel_security"
    PHYSICAL_SECURITY = "physical_security"
    BUSINESS_CONTINUITY = "business_continuity"


@dataclass
class ComplianceConfig:
    """Configuration du vérificateur de conformité"""
    enabled_frameworks: List[ComplianceFramework] = field(
        default_factory=lambda: [ComplianceFramework.GDPR, ComplianceFramework.SOC2]
    )
    
    # Monitoring
    continuous_monitoring: bool = True
    check_interval_hours: int = 24
    real_time_alerts: bool = True
    
    # Reporting
    generate_reports: bool = True
    report_frequency_days: int = 30
    
    # Data scanning
    scan_sensitive_data: bool = True
    scan_retention_policies: bool = True
    scan_access_patterns: bool = True
    
    # Thresholds
    max_data_retention_days: int = 2555  # 7 years default
    max_access_failures_per_hour: int = 5
    required_password_strength: int = 8
    
    # Integration
    audit_service_url: str = "http://localhost:8001"
    security_service_url: str = "http://localhost:8002"


class ComplianceControl(BaseModel):
    """Contrôle de conformité"""
    control_id: str
    framework: ComplianceFramework
    category: ControlCategory
    title: str
    description: str
    requirements: List[str]
    validation_rules: List[str]
    severity: ViolationSeverity = ViolationSeverity.MEDIUM
    automated_check: bool = True


class ComplianceViolation(BaseModel):
    """Violation de conformité"""
    violation_id: str
    control_id: str
    framework: ComplianceFramework
    severity: ViolationSeverity
    title: str
    description: str
    affected_resources: List[str] = []
    remediation_steps: List[str] = []
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    status: str = "open"
    risk_score: float = 0.0


class ComplianceAssessment(BaseModel):
    """Évaluation de conformité"""
    assessment_id: str
    framework: ComplianceFramework
    assessed_at: datetime
    overall_status: ComplianceStatus
    compliance_score: float  # 0-100
    
    # Results by category
    category_scores: Dict[ControlCategory, float] = {}
    
    # Violations
    total_violations: int = 0
    critical_violations: int = 0
    high_violations: int = 0
    medium_violations: int = 0
    low_violations: int = 0
    
    # Controls
    total_controls: int = 0
    compliant_controls: int = 0
    non_compliant_controls: int = 0
    
    violations: List[ComplianceViolation] = []
    recommendations: List[str] = []


class ComplianceCheckerTemplate:
    """
    Template de vérificateur de conformité enterprise pour Ainflue
    
    Fonctionnalités:
    - Vérification automatisée multi-framework
    - Monitoring continu de la conformité
    - Détection en temps réel des violations
    - Évaluation des risques et scoring
    - Rapports de conformité détaillés
    - Recommandations de remédiation
    - Intégration avec services d'audit
    - Alertes et notifications
    """
    
    def __init__(self, config: ComplianceConfig = None):
        self.config = config or ComplianceConfig()
        self.app = FastAPI(
            title="Ainflue Compliance Checker",
            description="Automated compliance verification and monitoring",
            version="1.0.0"
        )
        
        # Redis pour cache et coordination
        self.redis = Redis(host='localhost', port=6379, db=7, decode_responses=True)
        
        # Contrôles de conformité par framework
        self.compliance_controls: Dict[ComplianceFramework, List[ComplianceControl]] = {}
        
        # Cache des évaluations
        self.assessment_cache: Dict[str, ComplianceAssessment] = {}
        
        # Métriques Prometheus
        self.compliance_checks = Counter('compliance_checks_total', ['framework', 'status'])
        self.violations_detected = Counter('compliance_violations_total', ['framework', 'severity'])
        self.compliance_score_gauge = Gauge('compliance_score', ['framework'])
        self.check_duration = Histogram('compliance_check_duration_seconds', ['framework'])
        
        # Setup
        self._initialize_compliance_controls()
        self._setup_routes()
        
        if self.config.continuous_monitoring:
            self._start_continuous_monitoring()
        
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _initialize_compliance_controls(self):
        """Initialise les contrôles de conformité pour chaque framework"""
        
        # GDPR Controls
        gdpr_controls = [
            ComplianceControl(
                control_id="GDPR-ART-6",
                framework=ComplianceFramework.GDPR,
                category=ControlCategory.DATA_PROTECTION,
                title="Lawful Basis for Processing",
                description="Personal data processing must have a lawful basis",
                requirements=[
                    "Consent must be documented",
                    "Legitimate interest assessment completed",
                    "Processing purpose clearly defined"
                ],
                validation_rules=[
                    "consent_documented",
                    "purpose_limitation_enforced",
                    "data_minimization_applied"
                ],
                severity=ViolationSeverity.CRITICAL
            ),
            ComplianceControl(
                control_id="GDPR-ART-17",
                framework=ComplianceFramework.GDPR,
                category=ControlCategory.DATA_PROTECTION,
                title="Right to Erasure",
                description="Data subjects have the right to request deletion of personal data",
                requirements=[
                    "Deletion process implemented",
                    "Response within 30 days",
                    "Complete data removal verified"
                ],
                validation_rules=[
                    "deletion_process_exists",
                    "response_time_compliant",
                    "data_removal_verified"
                ],
                severity=ViolationSeverity.HIGH
            ),
            ComplianceControl(
                control_id="GDPR-ART-32",
                framework=ComplianceFramework.GDPR,
                category=ControlCategory.ENCRYPTION,
                title="Security of Processing",
                description="Appropriate technical and organisational measures for data security",
                requirements=[
                    "Encryption in transit and at rest",
                    "Access controls implemented",
                    "Regular security testing"
                ],
                validation_rules=[
                    "encryption_enabled",
                    "access_controls_active",
                    "security_tests_current"
                ],
                severity=ViolationSeverity.CRITICAL
            )
        ]
        
        # SOC2 Controls
        soc2_controls = [
            ComplianceControl(
                control_id="SOC2-CC6.1",
                framework=ComplianceFramework.SOC2,
                category=ControlCategory.ACCESS_CONTROL,
                title="Logical and Physical Access Controls",
                description="Access to system resources is restricted to authorized users",
                requirements=[
                    "User access reviews performed quarterly",
                    "Privileged access monitored",
                    "Access termination process enforced"
                ],
                validation_rules=[
                    "access_reviews_quarterly",
                    "privileged_access_monitored",
                    "termination_process_enforced"
                ],
                severity=ViolationSeverity.HIGH
            ),
            ComplianceControl(
                control_id="SOC2-CC7.1",
                framework=ComplianceFramework.SOC2,
                category=ControlCategory.AUDIT_LOGGING,
                title="System Monitoring",
                description="System activities are monitored and logged",
                requirements=[
                    "Comprehensive logging enabled",
                    "Log integrity protected",
                    "Monitoring alerts configured"
                ],
                validation_rules=[
                    "logging_comprehensive",
                    "log_integrity_protected",
                    "monitoring_alerts_active"
                ],
                severity=ViolationSeverity.MEDIUM
            )
        ]
        
        # PCI-DSS Controls
        pci_dss_controls = [
            ComplianceControl(
                control_id="PCI-DSS-3.4",
                framework=ComplianceFramework.PCI_DSS,
                category=ControlCategory.ENCRYPTION,
                title="Protect Cardholder Data",
                description="Cardholder data must be encrypted during transmission",
                requirements=[
                    "Strong encryption protocols used",
                    "Encryption keys properly managed",
                    "No unencrypted transmission"
                ],
                validation_rules=[
                    "strong_encryption_used",
                    "key_management_proper",
                    "no_unencrypted_transmission"
                ],
                severity=ViolationSeverity.CRITICAL
            )
        ]
        
        self.compliance_controls[ComplianceFramework.GDPR] = gdpr_controls
        self.compliance_controls[ComplianceFramework.SOC2] = soc2_controls
        self.compliance_controls[ComplianceFramework.PCI_DSS] = pci_dss_controls

    def _start_continuous_monitoring(self):
        """Démarre le monitoring continu"""
        async def monitoring_loop():
            while True:
                try:
                    for framework in self.config.enabled_frameworks:
                        await self._run_compliance_check(framework)
                    
                    # Attendre interval
                    await asyncio.sleep(self.config.check_interval_hours * 3600)
                    
                except Exception as e:
                    self.logger.error(f"Continuous monitoring error: {str(e)}")
                    await asyncio.sleep(300)  # Retry in 5 minutes
        
        # Démarrer en arrière-plan
        asyncio.create_task(monitoring_loop())

    def _setup_routes(self):
        """Configuration des routes du service"""
        
        @self.app.post("/compliance/check/{framework}")
        async def run_compliance_check(framework: ComplianceFramework, background_tasks: BackgroundTasks):
            """Exécuter vérification de conformité pour un framework"""
            try:
                assessment = await self._run_compliance_check(framework)
                
                # Générer rapport si violations critiques
                if assessment.critical_violations > 0:
                    background_tasks.add_task(self._send_critical_alert, assessment)
                
                return assessment
                
            except Exception as e:
                self.logger.error(f"Compliance check failed for {framework}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Compliance check failed: {str(e)}")

        @self.app.get("/compliance/status")
        async def get_compliance_status():
            """Statut global de conformité"""
            try:
                status = {}
                
                for framework in self.config.enabled_frameworks:
                    latest_assessment = await self._get_latest_assessment(framework)
                    if latest_assessment:
                        status[framework.value] = {
                            "status": latest_assessment.overall_status.value,
                            "score": latest_assessment.compliance_score,
                            "last_check": latest_assessment.assessed_at.isoformat(),
                            "violations": latest_assessment.total_violations
                        }
                    else:
                        status[framework.value] = {
                            "status": "never_assessed",
                            "score": 0,
                            "violations": 0
                        }
                
                return {"compliance_status": status}
                
            except Exception as e:
                self.logger.error(f"Failed to get compliance status: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to get compliance status")

        @self.app.get("/compliance/violations")
        async def get_active_violations(framework: Optional[ComplianceFramework] = None):
            """Récupérer violations actives"""
            try:
                violations = await self._get_active_violations(framework)
                return {"violations": violations}
                
            except Exception as e:
                self.logger.error(f"Failed to get violations: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to get violations")

        @self.app.post("/compliance/violations/{violation_id}/resolve")
        async def resolve_violation(violation_id: str, resolution_notes: str = ""):
            """Marquer une violation comme résolue"""
            try:
                await self._resolve_violation(violation_id, resolution_notes)
                return {"message": "Violation resolved successfully"}
                
            except Exception as e:
                self.logger.error(f"Failed to resolve violation: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to resolve violation")

        @self.app.get("/compliance/controls/{framework}")
        async def get_compliance_controls(framework: ComplianceFramework):
            """Récupérer contrôles de conformité pour un framework"""
            try:
                controls = self.compliance_controls.get(framework, [])
                return {"controls": [control.dict() for control in controls]}
                
            except Exception as e:
                self.logger.error(f"Failed to get controls: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to get controls")

        @self.app.get("/compliance/report/{framework}")
        async def generate_compliance_report(
            framework: ComplianceFramework,
            days_back: int = 30
        ):
            """Générer rapport de conformité détaillé"""
            try:
                report = await self._generate_detailed_report(framework, days_back)
                return report
                
            except Exception as e:
                self.logger.error(f"Failed to generate report: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to generate report")

        @self.app.get("/compliance/dashboard")
        async def compliance_dashboard():
            """Dashboard de conformité"""
            try:
                dashboard_data = await self._generate_dashboard_data()
                return dashboard_data
                
            except Exception as e:
                self.logger.error(f"Failed to generate dashboard: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to generate dashboard")

        @self.app.get("/health")
        async def health_check():
            """Health check"""
            try:
                await self.redis.ping()
                return {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "enabled_frameworks": [f.value for f in self.config.enabled_frameworks],
                    "continuous_monitoring": self.config.continuous_monitoring
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

    async def _run_compliance_check(self, framework: ComplianceFramework) -> ComplianceAssessment:
        """Exécuter vérification complète pour un framework"""
        with self.check_duration.labels(framework=framework.value).time():
            try:
                assessment_id = f"{framework.value}_{int(datetime.utcnow().timestamp())}"
                
                controls = self.compliance_controls.get(framework, [])
                violations = []
                category_scores = {}
                
                compliant_controls = 0
                total_controls = len(controls)
                
                # Vérifier chaque contrôle
                for control in controls:
                    is_compliant = await self._check_control_compliance(control)
                    
                    if is_compliant:
                        compliant_controls += 1
                    else:
                        violation = await self._create_violation(control)
                        violations.append(violation)
                        
                        # Métriques
                        self.violations_detected.labels(
                            framework=framework.value,
                            severity=violation.severity.value
                        ).inc()
                    
                    # Score par catégorie
                    if control.category not in category_scores:
                        category_scores[control.category] = []
                    category_scores[control.category].append(1 if is_compliant else 0)
                
                # Calculer scores
                overall_score = (compliant_controls / total_controls * 100) if total_controls > 0 else 100
                
                for category, scores in category_scores.items():
                    category_scores[category] = sum(scores) / len(scores) * 100
                
                # Déterminer statut global
                overall_status = self._determine_compliance_status(overall_score, violations)
                
                # Compter violations par sévérité
                violation_counts = {
                    "critical": len([v for v in violations if v.severity == ViolationSeverity.CRITICAL]),
                    "high": len([v for v in violations if v.severity == ViolationSeverity.HIGH]),
                    "medium": len([v for v in violations if v.severity == ViolationSeverity.MEDIUM]),
                    "low": len([v for v in violations if v.severity == ViolationSeverity.LOW])
                }
                
                # Créer évaluation
                assessment = ComplianceAssessment(
                    assessment_id=assessment_id,
                    framework=framework,
                    assessed_at=datetime.utcnow(),
                    overall_status=overall_status,
                    compliance_score=overall_score,
                    category_scores=category_scores,
                    total_violations=len(violations),
                    critical_violations=violation_counts["critical"],
                    high_violations=violation_counts["high"],
                    medium_violations=violation_counts["medium"],
                    low_violations=violation_counts["low"],
                    total_controls=total_controls,
                    compliant_controls=compliant_controls,
                    non_compliant_controls=total_controls - compliant_controls,
                    violations=violations,
                    recommendations=await self._generate_recommendations(framework, violations)
                )
                
                # Stocker évaluation
                await self._store_assessment(assessment)
                
                # Mettre à jour métriques
                self.compliance_checks.labels(framework=framework.value, status="success").inc()
                self.compliance_score_gauge.labels(framework=framework.value).set(overall_score)
                
                self.logger.info(f"Compliance check completed for {framework.value}: {overall_score:.1f}% compliant")
                
                return assessment
                
            except Exception as e:
                self.compliance_checks.labels(framework=framework.value, status="error").inc()
                self.logger.error(f"Compliance check failed for {framework.value}: {str(e)}")
                raise

    async def _check_control_compliance(self, control: ComplianceControl) -> bool:
        """Vérifier conformité d'un contrôle spécifique"""
        try:
            # Vérifier chaque règle de validation
            for rule in control.validation_rules:
                if not await self._validate_rule(rule, control):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Control compliance check failed for {control.control_id}: {str(e)}")
            return False

    async def _validate_rule(self, rule: str, control: ComplianceControl) -> bool:
        """Valider une règle spécifique"""
        try:
            # Règles d'encryption
            if rule == "encryption_enabled":
                return await self._check_encryption_enabled()
            
            elif rule == "strong_encryption_used":
                return await self._check_strong_encryption()
            
            # Règles d'accès
            elif rule == "access_controls_active":
                return await self._check_access_controls()
            
            elif rule == "access_reviews_quarterly":
                return await self._check_access_reviews()
            
            # Règles de logging
            elif rule == "logging_comprehensive":
                return await self._check_comprehensive_logging()
            
            elif rule == "log_integrity_protected":
                return await self._check_log_integrity()
            
            # Règles GDPR
            elif rule == "consent_documented":
                return await self._check_consent_documentation()
            
            elif rule == "deletion_process_exists":
                return await self._check_deletion_process()
            
            # Règle par défaut
            else:
                self.logger.warning(f"Unknown validation rule: {rule}")
                return False
                
        except Exception as e:
            self.logger.error(f"Rule validation failed for {rule}: {str(e)}")
            return False

    async def _check_encryption_enabled(self) -> bool:
        """Vérifier que le chiffrement est activé"""
        # Vérifier configuration du service de chiffrement
        try:
            # Simuler vérification (en production, appeler le service réel)
            encryption_config = await self.redis.get("encryption_service_config")
            if encryption_config:
                config = json.loads(encryption_config)
                return config.get("encryption_enabled", False)
            return False
        except:
            return False

    async def _check_access_controls(self) -> bool:
        """Vérifier contrôles d'accès"""
        try:
            # Vérifier service RBAC
            rbac_status = await self.redis.get("rbac_service_status")
            return rbac_status == "active"
        except:
            return False

    async def _check_comprehensive_logging(self) -> bool:
        """Vérifier logging complet"""
        try:
            # Vérifier service d'audit
            audit_events_count = await self.redis.llen("audit_events")
            return audit_events_count > 0
        except:
            return False

    async def _check_consent_documentation(self) -> bool:
        """Vérifier documentation du consentement"""
        try:
            # Vérifier enregistrements de consentement
            consent_records = await self.redis.get("consent_records_count")
            return int(consent_records or 0) > 0
        except:
            return False

    async def _check_deletion_process(self) -> bool:
        """Vérifier processus de suppression"""
        try:
            # Vérifier existence du processus
            deletion_process = await self.redis.get("data_deletion_process")
            return deletion_process == "implemented"
        except:
            return False

    async def _create_violation(self, control: ComplianceControl) -> ComplianceViolation:
        """Créer violation de conformité"""
        violation_id = f"violation_{control.control_id}_{int(datetime.utcnow().timestamp())}"
        
        # Déterminer ressources affectées
        affected_resources = await self._identify_affected_resources(control)
        
        # Génerer étapes de remédiation
        remediation_steps = await self._generate_remediation_steps(control)
        
        # Calculer score de risque
        risk_score = self._calculate_risk_score(control)
        
        violation = ComplianceViolation(
            violation_id=violation_id,
            control_id=control.control_id,
            framework=control.framework,
            severity=control.severity,
            title=f"Non-compliance with {control.title}",
            description=f"Control {control.control_id} is not compliant: {control.description}",
            affected_resources=affected_resources,
            remediation_steps=remediation_steps,
            detected_at=datetime.utcnow(),
            risk_score=risk_score
        )
        
        # Stocker violation
        await self._store_violation(violation)
        
        return violation

    def _calculate_risk_score(self, control: ComplianceControl) -> float:
        """Calculer score de risque d'une violation"""
        base_scores = {
            ViolationSeverity.CRITICAL: 9.0,
            ViolationSeverity.HIGH: 7.0,
            ViolationSeverity.MEDIUM: 5.0,
            ViolationSeverity.LOW: 3.0
        }
        
        base_score = base_scores.get(control.severity, 5.0)
        
        # Ajustements selon la catégorie
        category_multipliers = {
            ControlCategory.DATA_PROTECTION: 1.2,
            ControlCategory.ENCRYPTION: 1.1,
            ControlCategory.ACCESS_CONTROL: 1.1,
            ControlCategory.AUDIT_LOGGING: 1.0
        }
        
        multiplier = category_multipliers.get(control.category, 1.0)
        
        return min(base_score * multiplier, 10.0)

    def _determine_compliance_status(self, score: float, violations: List[ComplianceViolation]) -> ComplianceStatus:
        """Déterminer statut de conformité global"""
        critical_violations = [v for v in violations if v.severity == ViolationSeverity.CRITICAL]
        
        if critical_violations:
            return ComplianceStatus.NON_COMPLIANT
        elif score >= 95:
            return ComplianceStatus.COMPLIANT
        elif score >= 80:
            return ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            return ComplianceStatus.NON_COMPLIANT

    async def _generate_recommendations(self, framework: ComplianceFramework, violations: List[ComplianceViolation]) -> List[str]:
        """Générer recommandations basées sur les violations"""
        recommendations = []
        
        critical_violations = [v for v in violations if v.severity == ViolationSeverity.CRITICAL]
        if critical_violations:
            recommendations.append("Address critical compliance violations immediately")
        
        # Recommandations par framework
        if framework == ComplianceFramework.GDPR:
            data_violations = [v for v in violations if "data" in v.description.lower()]
            if data_violations:
                recommendations.append("Review data processing activities and ensure proper consent management")
        
        elif framework == ComplianceFramework.SOC2:
            access_violations = [v for v in violations if "access" in v.description.lower()]
            if access_violations:
                recommendations.append("Strengthen access controls and implement regular access reviews")
        
        # Recommandations générales
        if len(violations) > 5:
            recommendations.append("Implement compliance automation to reduce manual oversight")
        
        return recommendations

    async def _store_assessment(self, assessment: ComplianceAssessment):
        """Stocker évaluation de conformité"""
        try:
            # Cache en mémoire
            self.assessment_cache[assessment.assessment_id] = assessment
            
            # Redis
            await self.redis.setex(
                f"assessment:{assessment.framework.value}:latest",
                86400 * 30,  # 30 days
                json.dumps(assessment.dict(), default=str)
            )
            
            # Historique
            await self.redis.lpush(
                f"assessment_history:{assessment.framework.value}",
                json.dumps(assessment.dict(), default=str)
            )
            await self.redis.ltrim(f"assessment_history:{assessment.framework.value}", 0, 99)  # Keep last 100
            
        except Exception as e:
            self.logger.error(f"Failed to store assessment: {str(e)}")

    async def _store_violation(self, violation: ComplianceViolation):
        """Stocker violation"""
        try:
            await self.redis.setex(
                f"violation:{violation.violation_id}",
                86400 * 365,  # 1 year
                json.dumps(violation.dict(), default=str)
            )
            
            # Index des violations actives
            await self.redis.sadd("active_violations", violation.violation_id)
            
        except Exception as e:
            self.logger.error(f"Failed to store violation: {str(e)}")

    def get_app(self) -> FastAPI:
        """Retourne instance FastAPI"""
        return self.app


def create_compliance_checker(config: ComplianceConfig = None) -> FastAPI:
    """
    Factory pour créer vérificateur de conformité
    
    Args:
        config: Configuration personnalisée
        
    Returns:
        FastAPI: Instance du service configuré
    """
    compliance_checker = ComplianceCheckerTemplate(config)
    return compliance_checker.get_app()


if __name__ == "__main__":
    import uvicorn
    
    config = ComplianceConfig(
        enabled_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.SOC2],
        continuous_monitoring=True,
        check_interval_hours=24
    )
    
    app = create_compliance_checker(config)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )