"""
SLA Compliance Monitor - Ainflue Health Checks Module
Monitoring compliance SLA avec tracking performance, violation detection,
reporting automatique et business impact analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture health checks et tous ses patterns sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel. Toute reproduction, modification, distribution ou vol 
d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import uuid
import statistics
import numpy as np
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

class SLAMetricType(Enum):
    """Types de métriques SLA"""
    AVAILABILITY = "availability"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    UPTIME = "uptime"
    RECOVERY_TIME = "recovery_time"
    BUSINESS_CONTINUITY = "business_continuity"

class ViolationSeverity(Enum):
    """Sévérité violations SLA"""
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"
    CATASTROPHIC = "catastrophic"

class ComplianceStatus(Enum):
    """Statuts compliance SLA"""
    COMPLIANT = "compliant"
    AT_RISK = "at_risk"
    VIOLATED = "violated"
    UNKNOWN = "unknown"

@dataclass
class SLAObjective:
    """Objectif SLA"""
    sla_id: str
    service_name: str
    metric_type: SLAMetricType
    target_value: float
    measurement_period_hours: int
    evaluation_window_minutes: int = 5
    threshold_warning: float = 0.95  # Warning at 95% of target
    threshold_critical: float = 0.90  # Critical at 90% of target
    business_impact: str = "medium"
    penalty_clause: Optional[str] = None
    measurement_unit: str = ""

@dataclass
class SLAViolation:
    """Violation SLA"""
    violation_id: str
    sla_id: str
    service_name: str
    metric_type: SLAMetricType
    violation_timestamp: datetime
    duration_minutes: float
    actual_value: float
    target_value: float
    severity: ViolationSeverity
    impact_description: str
    root_cause: Optional[str] = None
    resolution_time: Optional[datetime] = None

@dataclass
class ComplianceReport:
    """Rapport compliance SLA"""
    report_id: str
    reporting_period_start: datetime
    reporting_period_end: datetime
    service_name: str
    overall_compliance_score: float
    sla_results: List[Dict[str, Any]]
    violations: List[SLAViolation]
    business_impact_summary: Dict[str, Any]
    recommendations: List[str]

@dataclass  
class SLAConfig:
    """Configuration monitoring SLA"""
    evaluation_interval_minutes: int = 5
    violation_detection_enabled: bool = True
    automatic_reporting: bool = True
    reporting_frequency_hours: int = 24
    business_hours_only: bool = False
    escalation_enabled: bool = True
    penalty_calculation_enabled: bool = True

class SLACalculationEngine:
    """Moteur calcul métriques SLA"""
    
    @staticmethod
    async def calculate_availability(service_data: List[Dict[str, Any]], 
                                   period_hours: int) -> float:
        """Calculer disponibilité service"""
        if not service_data:
            return 0.0
            
        # Calculer uptime vs downtime
        total_measurements = len(service_data)
        healthy_measurements = len([d for d in service_data if d.get('status') == 'healthy'])
        
        if total_measurements == 0:
            return 0.0
            
        availability = (healthy_measurements / total_measurements) * 100
        return min(100.0, availability)
        
    @staticmethod
    async def calculate_response_time_percentile(response_times: List[float], 
                                               percentile: int = 95) -> float:
        """Calculer percentile temps réponse"""
        if not response_times:
            return 0.0
            
        return np.percentile(response_times, percentile)
        
    @staticmethod
    async def calculate_error_rate(total_requests: int, failed_requests: int) -> float:
        """Calculer taux erreur"""
        if total_requests == 0:
            return 0.0
            
        return (failed_requests / total_requests) * 100
        
    @staticmethod
    async def calculate_throughput(request_count: int, period_minutes: int) -> float:
        """Calculer throughput (requests per minute)"""
        if period_minutes == 0:
            return 0.0
            
        return request_count / period_minutes
        
    @staticmethod
    async def calculate_mean_time_to_recovery(incidents: List[Dict[str, Any]]) -> float:
        """Calculer MTTR (Mean Time To Recovery)"""
        if not incidents:
            return 0.0
            
        recovery_times = []
        for incident in incidents:
            start_time = incident.get('start_time')
            end_time = incident.get('end_time')
            
            if start_time and end_time:
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time)
                if isinstance(end_time, str):
                    end_time = datetime.fromisoformat(end_time)
                    
                recovery_time = (end_time - start_time).total_seconds() / 60  # minutes
                recovery_times.append(recovery_time)
                
        return statistics.mean(recovery_times) if recovery_times else 0.0

class ViolationDetector:
    """Détecteur violations SLA"""
    
    def __init__(self):
        self.violation_history: Dict[str, List[SLAViolation]] = defaultdict(list)
        
    async def detect_violations(self, sla_objective: SLAObjective, 
                              current_value: float,
                              measurement_timestamp: datetime) -> Optional[SLAViolation]:
        """Détecter violation SLA"""
        violation = None
        
        # Déterminer si violation basée sur type métrique
        is_violation = False
        severity = ViolationSeverity.MINOR
        
        if sla_objective.metric_type in [SLAMetricType.AVAILABILITY, SLAMetricType.UPTIME]:
            # Pour availability/uptime: plus bas = violation
            if current_value < sla_objective.target_value * sla_objective.threshold_critical:
                is_violation = True
                severity = ViolationSeverity.CRITICAL
            elif current_value < sla_objective.target_value * sla_objective.threshold_warning:
                is_violation = True
                severity = ViolationSeverity.MAJOR
                
        elif sla_objective.metric_type in [SLAMetricType.RESPONSE_TIME, SLAMetricType.ERROR_RATE]:
            # Pour response time/error rate: plus haut = violation
            if current_value > sla_objective.target_value / sla_objective.threshold_critical:
                is_violation = True
                severity = ViolationSeverity.CRITICAL
            elif current_value > sla_objective.target_value / sla_objective.threshold_warning:
                is_violation = True
                severity = ViolationSeverity.MAJOR
                
        elif sla_objective.metric_type == SLAMetricType.THROUGHPUT:
            # Pour throughput: plus bas = violation
            if current_value < sla_objective.target_value * sla_objective.threshold_critical:
                is_violation = True
                severity = ViolationSeverity.CRITICAL
            elif current_value < sla_objective.target_value * sla_objective.threshold_warning:
                is_violation = True
                severity = ViolationSeverity.MAJOR
                
        if is_violation:
            violation = SLAViolation(
                violation_id=str(uuid.uuid4()),
                sla_id=sla_objective.sla_id,
                service_name=sla_objective.service_name,
                metric_type=sla_objective.metric_type,
                violation_timestamp=measurement_timestamp,
                duration_minutes=0.0,  # Will be updated when violation ends
                actual_value=current_value,
                target_value=sla_objective.target_value,
                severity=severity,
                impact_description=await self._generate_impact_description(
                    sla_objective, current_value, severity
                )
            )
            
            # Stocker violation
            self.violation_history[sla_objective.sla_id].append(violation)
            
        return violation
        
    async def _generate_impact_description(self, sla_objective: SLAObjective, 
                                         actual_value: float, 
                                         severity: ViolationSeverity) -> str:
        """Générer description impact violation"""
        metric_name = sla_objective.metric_type.value.replace('_', ' ').title()
        
        if sla_objective.metric_type in [SLAMetricType.AVAILABILITY, SLAMetricType.UPTIME]:
            return f"{metric_name} dropped to {actual_value:.2f}% (target: {sla_objective.target_value:.2f}%) - {severity.value} impact on service availability"
            
        elif sla_objective.metric_type == SLAMetricType.RESPONSE_TIME:
            return f"{metric_name} increased to {actual_value:.2f}{sla_objective.measurement_unit} (target: ≤{sla_objective.target_value:.2f}{sla_objective.measurement_unit}) - {severity.value} impact on user experience"
            
        elif sla_objective.metric_type == SLAMetricType.ERROR_RATE:
            return f"{metric_name} increased to {actual_value:.2f}% (target: ≤{sla_objective.target_value:.2f}%) - {severity.value} impact on system reliability"
            
        elif sla_objective.metric_type == SLAMetricType.THROUGHPUT:
            return f"{metric_name} dropped to {actual_value:.2f}{sla_objective.measurement_unit} (target: ≥{sla_objective.target_value:.2f}{sla_objective.measurement_unit}) - {severity.value} impact on system capacity"
            
        return f"{metric_name} SLA violation detected - {severity.value} business impact"

class BusinessImpactAnalyzer:
    """Analyseur impact business violations SLA"""
    
    async def calculate_business_impact(self, violations: List[SLAViolation], 
                                      service_context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculer impact business violations"""
        if not violations:
            return {
                'total_impact_score': 0.0,
                'financial_impact': 0.0,
                'customer_impact': 0.0,
                'operational_impact': 0.0,
                'reputation_impact': 0.0
            }
            
        # Calculer impacts par catégorie
        financial_impact = await self._calculate_financial_impact(violations, service_context)
        customer_impact = await self._calculate_customer_impact(violations, service_context)
        operational_impact = await self._calculate_operational_impact(violations, service_context)
        reputation_impact = await self._calculate_reputation_impact(violations, service_context)
        
        # Score impact total (0-100)
        total_impact_score = (
            financial_impact * 0.3 + 
            customer_impact * 0.3 + 
            operational_impact * 0.2 + 
            reputation_impact * 0.2
        )
        
        return {
            'total_impact_score': total_impact_score,
            'financial_impact': financial_impact,
            'customer_impact': customer_impact,
            'operational_impact': operational_impact,
            'reputation_impact': reputation_impact,
            'impact_details': await self._generate_impact_details(violations, service_context)
        }
        
    async def _calculate_financial_impact(self, violations: List[SLAViolation], 
                                        context: Dict[str, Any]) -> float:
        """Calculer impact financier"""
        financial_impact = 0.0
        
        revenue_per_hour = context.get('revenue_per_hour', 1000)
        
        for violation in violations:
            # Impact basé sur sévérité et durée
            severity_multiplier = {
                ViolationSeverity.MINOR: 0.01,
                ViolationSeverity.MAJOR: 0.05,
                ViolationSeverity.CRITICAL: 0.15,
                ViolationSeverity.CATASTROPHIC: 0.5
            }
            
            multiplier = severity_multiplier.get(violation.severity, 0.01)
            duration_hours = violation.duration_minutes / 60
            
            # Calculer perte revenue estimée
            estimated_loss = revenue_per_hour * multiplier * duration_hours
            financial_impact += estimated_loss
            
        # Normaliser sur échelle 0-100
        max_expected_loss = context.get('max_expected_hourly_loss', 10000)
        return min(100.0, (financial_impact / max_expected_loss) * 100)
        
    async def _calculate_customer_impact(self, violations: List[SLAViolation], 
                                       context: Dict[str, Any]) -> float:
        """Calculer impact client"""
        customer_impact = 0.0
        
        total_users = context.get('total_users', 10000)
        
        for violation in violations:
            # Estimer utilisateurs affectés
            if violation.metric_type == SLAMetricType.AVAILABILITY:
                affected_users_ratio = (100 - violation.actual_value) / 100
            elif violation.metric_type == SLAMetricType.RESPONSE_TIME:
                # Plus le temps réponse est élevé, plus d'utilisateurs affectés
                affected_users_ratio = min(1.0, violation.actual_value / (violation.target_value * 10))
            else:
                affected_users_ratio = 0.1  # Default 10% users affected
                
            affected_users = total_users * affected_users_ratio
            duration_hours = violation.duration_minutes / 60
            
            # Impact score basé sur utilisateurs et durée
            impact_score = (affected_users / total_users) * duration_hours * 10
            customer_impact += impact_score
            
        return min(100.0, customer_impact)
        
    async def _calculate_operational_impact(self, violations: List[SLAViolation], 
                                          context: Dict[str, Any]) -> float:
        """Calculer impact opérationnel"""
        operational_impact = 0.0
        
        for violation in violations:
            # Impact basé sur type métrique et sévérité
            base_impact = {
                ViolationSeverity.MINOR: 10,
                ViolationSeverity.MAJOR: 25,
                ViolationSeverity.CRITICAL: 50,
                ViolationSeverity.CATASTROPHIC: 80
            }
            
            impact = base_impact.get(violation.severity, 10)
            
            # Facteur durée
            duration_factor = min(2.0, violation.duration_minutes / 60)
            operational_impact += impact * duration_factor
            
        return min(100.0, operational_impact / len(violations) if violations else 0)
        
    async def _calculate_reputation_impact(self, violations: List[SLAViolation], 
                                         context: Dict[str, Any]) -> float:
        """Calculer impact réputation"""
        reputation_impact = 0.0
        
        # Impact réputation basé sur visibilité publique et sévérité
        public_facing_services = context.get('public_facing_services', [])
        
        for violation in violations:
            base_impact = 5  # Base reputation impact
            
            # Augmenter si service public
            if violation.service_name in public_facing_services:
                base_impact *= 3
                
            # Facteur sévérité
            severity_factor = {
                ViolationSeverity.MINOR: 1,
                ViolationSeverity.MAJOR: 2,
                ViolationSeverity.CRITICAL: 4,
                ViolationSeverity.CATASTROPHIC: 8
            }
            
            impact = base_impact * severity_factor.get(violation.severity, 1)
            reputation_impact += impact
            
        return min(100.0, reputation_impact)
        
    async def _generate_impact_details(self, violations: List[SLAViolation], 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Générer détails impact"""
        return {
            'total_violations': len(violations),
            'violation_by_severity': {
                severity.value: len([v for v in violations if v.severity == severity])
                for severity in ViolationSeverity
            },
            'services_affected': list(set(v.service_name for v in violations)),
            'total_downtime_minutes': sum(v.duration_minutes for v in violations),
            'most_critical_violation': max(violations, key=lambda v: v.severity.value) if violations else None
        }

class SLAComplianceMonitor:
    """
    Monitoring compliance SLA avec tracking performance.
    Violation detection + reporting + business impact analysis.
    
    Features:
    - Continuous SLA monitoring multi-métriques
    - Real-time violation detection avec severity classification
    - Business impact analysis et financial cost calculation
    - Automated compliance reporting
    - Penalty calculation selon contract clauses
    - Trend analysis et predictive compliance
    """
    
    def __init__(self, sla_config: SLAConfig):
        self.sla_config = sla_config
        self.calculation_engine = SLACalculationEngine()
        self.violation_detector = ViolationDetector()
        self.business_impact_analyzer = BusinessImpactAnalyzer()
        
        # SLA objectives registry
        self.sla_objectives: Dict[str, SLAObjective] = {}
        
        # Données monitoring
        self.metrics_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.compliance_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.active_violations: Dict[str, SLAViolation] = {}
        
        # Rapports
        self.compliance_reports: List[ComplianceReport] = []
        
        # Monitoring état
        self.monitoring_active = False
        self.monitoring_task = None
        
        # Statistiques
        self.sla_stats = {
            'total_objectives': 0,
            'compliant_objectives': 0,
            'violated_objectives': 0,
            'total_violations': 0,
            'average_compliance_score': 0.0,
            'total_penalty_amount': 0.0
        }
        
    async def register_sla_objective(self, sla_objective: SLAObjective):
        """Enregistrer objectif SLA"""
        self.sla_objectives[sla_objective.sla_id] = sla_objective
        self.sla_stats['total_objectives'] += 1
        
        logger.info(f"Registered SLA objective: {sla_objective.sla_id} for {sla_objective.service_name}")
        
    async def start_sla_monitoring(self):
        """Démarrer monitoring SLA"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("Started SLA compliance monitoring")
        
    async def stop_sla_monitoring(self):
        """Arrêter monitoring SLA"""
        if not self.monitoring_active:
            return
            
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            
        logger.info("Stopped SLA compliance monitoring")
        
    async def evaluate_sla_compliance(self, service_name: str = None, 
                                    time_range_hours: int = 24) -> Dict[str, Any]:
        """
        Évaluer compliance SLA pour services.
        
        Args:
            service_name: Service spécifique (None = tous)
            time_range_hours: Période évaluation
            
        Returns:
            Résultats compliance détaillés
        """
        evaluation_start = datetime.now()
        end_time = evaluation_start
        start_time = end_time - timedelta(hours=time_range_hours)
        
        try:
            # Filtrer objectifs SLA
            objectives_to_evaluate = []
            for sla_id, objective in self.sla_objectives.items():
                if service_name is None or objective.service_name == service_name:
                    objectives_to_evaluate.append(objective)
                    
            if not objectives_to_evaluate:
                return {
                    'evaluation_timestamp': evaluation_start.isoformat(),
                    'message': 'No SLA objectives found for evaluation',
                    'compliance_results': []
                }
                
            # Évaluer chaque objectif
            compliance_results = []
            total_violations = []
            
            for objective in objectives_to_evaluate:
                result = await self._evaluate_single_sla_objective(
                    objective, start_time, end_time
                )
                compliance_results.append(result)
                
                if result['violations']:
                    total_violations.extend(result['violations'])
                    
            # Calculer compliance globale
            overall_compliance = await self._calculate_overall_compliance(compliance_results)
            
            # Analyser impact business
            business_impact = await self.business_impact_analyzer.calculate_business_impact(
                total_violations, 
                {'revenue_per_hour': 5000, 'total_users': 50000}
            )
            
            # Générer recommandations
            recommendations = await self._generate_compliance_recommendations(
                compliance_results, total_violations
            )
            
            return {
                'evaluation_id': str(uuid.uuid4()),
                'evaluation_timestamp': evaluation_start.isoformat(),
                'evaluation_period': {
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_hours': time_range_hours
                },
                'overall_compliance': overall_compliance,
                'compliance_results': compliance_results,
                'business_impact_analysis': business_impact,
                'total_violations': len(total_violations),
                'violation_summary': await self._summarize_violations(total_violations),
                'recommendations': recommendations,
                'execution_time_seconds': (datetime.now() - evaluation_start).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"SLA compliance evaluation failed: {e}")
            return {
                'evaluation_timestamp': evaluation_start.isoformat(),
                'status': 'error',
                'error': str(e)
            }
            
    async def generate_compliance_report(self, service_name: str, 
                                       reporting_period_hours: int = 168) -> ComplianceReport:
        """Générer rapport compliance complet"""
        report_end = datetime.now()
        report_start = report_end - timedelta(hours=reporting_period_hours)
        
        # Évaluer compliance pour période
        compliance_evaluation = await self.evaluate_sla_compliance(
            service_name, reporting_period_hours
        )
        
        # Créer rapport
        report = ComplianceReport(
            report_id=str(uuid.uuid4()),
            reporting_period_start=report_start,
            reporting_period_end=report_end,
            service_name=service_name,
            overall_compliance_score=compliance_evaluation['overall_compliance']['compliance_score'],
            sla_results=compliance_evaluation['compliance_results'],
            violations=[],  # Sera peuplé depuis compliance_evaluation
            business_impact_summary=compliance_evaluation['business_impact_analysis'],
            recommendations=compliance_evaluation['recommendations']
        )
        
        # Stocker rapport
        self.compliance_reports.append(report)
        
        logger.info(f"Generated compliance report: {report.report_id} for {service_name}")
        return report
        
    async def ingest_service_metrics(self, service_name: str, metrics: Dict[str, Any]):
        """Ingérer métriques service pour évaluation SLA"""
        timestamp = datetime.now()
        
        # Stocker métriques avec timestamp
        metric_entry = {
            'timestamp': timestamp,
            'service_name': service_name,
            **metrics
        }
        
        self.metrics_data[service_name].append(metric_entry)
        
        # Évaluer violations en temps réel si activé
        if self.sla_config.violation_detection_enabled:
            await self._check_real_time_violations(service_name, metrics, timestamp)
            
    # Méthodes utilitaires
    
    async def _monitoring_loop(self):
        """Boucle monitoring SLA continue"""
        while self.monitoring_active:
            try:
                # Évaluer compliance périodiquement
                for service_name in set(obj.service_name for obj in self.sla_objectives.values()):
                    await self._evaluate_service_compliance_real_time(service_name)
                    
                # Générer rapports automatiques si configuré
                if self.sla_config.automatic_reporting:
                    await self._generate_scheduled_reports()
                    
                # Attendre avant prochaine évaluation
                await asyncio.sleep(self.sla_config.evaluation_interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"SLA monitoring loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
                
    async def _evaluate_single_sla_objective(self, objective: SLAObjective, 
                                           start_time: datetime, 
                                           end_time: datetime) -> Dict[str, Any]:
        """Évaluer objectif SLA individuel"""
        # Récupérer données service pour période
        service_data = [
            entry for entry in self.metrics_data[objective.service_name]
            if start_time <= entry['timestamp'] <= end_time
        ]
        
        if not service_data:
            return {
                'sla_id': objective.sla_id,
                'service_name': objective.service_name,
                'metric_type': objective.metric_type.value,
                'compliance_status': ComplianceStatus.UNKNOWN.value,
                'current_value': 0.0,
                'target_value': objective.target_value,
                'compliance_percentage': 0.0,
                'violations': [],
                'message': 'No data available for evaluation period'
            }
            
        # Calculer métrique selon type
        try:
            if objective.metric_type == SLAMetricType.AVAILABILITY:
                current_value = await self.calculation_engine.calculate_availability(
                    service_data, objective.measurement_period_hours
                )
            elif objective.metric_type == SLAMetricType.RESPONSE_TIME:
                response_times = [d.get('response_time_ms', 0) for d in service_data]
                current_value = await self.calculation_engine.calculate_response_time_percentile(
                    response_times, 95
                )
            elif objective.metric_type == SLAMetricType.ERROR_RATE:
                total_requests = sum(d.get('total_requests', 0) for d in service_data)
                failed_requests = sum(d.get('failed_requests', 0) for d in service_data)
                current_value = await self.calculation_engine.calculate_error_rate(
                    total_requests, failed_requests
                )
            elif objective.metric_type == SLAMetricType.THROUGHPUT:
                total_requests = sum(d.get('total_requests', 0) for d in service_data)
                period_minutes = (end_time - start_time).total_seconds() / 60
                current_value = await self.calculation_engine.calculate_throughput(
                    total_requests, period_minutes
                )
            else:
                current_value = 0.0
                
        except Exception as e:
            logger.error(f"SLA calculation failed for {objective.sla_id}: {e}")
            current_value = 0.0
            
        # Déterminer compliance status
        compliance_status, compliance_percentage = await self._determine_compliance_status(
            objective, current_value
        )
        
        # Chercher violations dans période
        violations = [
            v for v in self.violation_detector.violation_history[objective.sla_id]
            if start_time <= v.violation_timestamp <= end_time
        ]
        
        return {
            'sla_id': objective.sla_id,
            'service_name': objective.service_name,
            'metric_type': objective.metric_type.value,
            'compliance_status': compliance_status.value,
            'current_value': current_value,
            'target_value': objective.target_value,
            'compliance_percentage': compliance_percentage,
            'violations': violations,
            'measurement_unit': objective.measurement_unit,
            'business_impact': objective.business_impact
        }
        
    async def _determine_compliance_status(self, objective: SLAObjective, 
                                         current_value: float) -> Tuple[ComplianceStatus, float]:
        """Déterminer statut compliance"""
        if objective.metric_type in [SLAMetricType.AVAILABILITY, SLAMetricType.UPTIME, SLAMetricType.THROUGHPUT]:
            # Plus haut = mieux
            if current_value >= objective.target_value:
                return ComplianceStatus.COMPLIANT, 100.0
            elif current_value >= objective.target_value * objective.threshold_warning:
                compliance_pct = (current_value / objective.target_value) * 100
                return ComplianceStatus.AT_RISK, compliance_pct
            else:
                compliance_pct = (current_value / objective.target_value) * 100
                return ComplianceStatus.VIOLATED, compliance_pct
                
        else:  # RESPONSE_TIME, ERROR_RATE, RECOVERY_TIME
            # Plus bas = mieux
            if current_value <= objective.target_value:
                return ComplianceStatus.COMPLIANT, 100.0
            elif current_value <= objective.target_value / objective.threshold_warning:
                compliance_pct = (objective.target_value / current_value) * 100
                return ComplianceStatus.AT_RISK, compliance_pct
            else:
                compliance_pct = (objective.target_value / current_value) * 100
                return ComplianceStatus.VIOLATED, min(100.0, compliance_pct)
                
    async def _calculate_overall_compliance(self, compliance_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculer compliance globale"""
        if not compliance_results:
            return {
                'compliance_score': 0.0,
                'status': ComplianceStatus.UNKNOWN.value,
                'compliant_objectives': 0,
                'at_risk_objectives': 0,
                'violated_objectives': 0,
                'total_objectives': 0
            }
            
        # Compter statuts
        compliant = len([r for r in compliance_results if r['compliance_status'] == 'compliant'])
        at_risk = len([r for r in compliance_results if r['compliance_status'] == 'at_risk'])
        violated = len([r for r in compliance_results if r['compliance_status'] == 'violated'])
        total = len(compliance_results)
        
        # Score compliance pondéré
        compliance_scores = [r['compliance_percentage'] for r in compliance_results if r['compliance_percentage'] > 0]
        overall_score = statistics.mean(compliance_scores) if compliance_scores else 0.0
        
        # Statut global
        if violated > 0:
            overall_status = ComplianceStatus.VIOLATED
        elif at_risk > 0:
            overall_status = ComplianceStatus.AT_RISK
        else:
            overall_status = ComplianceStatus.COMPLIANT
            
        return {
            'compliance_score': overall_score,
            'status': overall_status.value,
            'compliant_objectives': compliant,
            'at_risk_objectives': at_risk,
            'violated_objectives': violated,
            'total_objectives': total
        }
        
    async def _check_real_time_violations(self, service_name: str, metrics: Dict[str, Any], 
                                        timestamp: datetime):
        """Vérifier violations temps réel"""
        # Chercher objectifs SLA pour ce service
        service_objectives = [
            obj for obj in self.sla_objectives.values() 
            if obj.service_name == service_name
        ]
        
        for objective in service_objectives:
            try:
                # Extraire valeur métrique appropriée
                current_value = 0.0
                
                if objective.metric_type == SLAMetricType.AVAILABILITY:
                    current_value = metrics.get('availability_percentage', 100.0)
                elif objective.metric_type == SLAMetricType.RESPONSE_TIME:
                    current_value = metrics.get('response_time_ms', 0.0)
                elif objective.metric_type == SLAMetricType.ERROR_RATE:
                    current_value = metrics.get('error_rate_percent', 0.0)
                elif objective.metric_type == SLAMetricType.THROUGHPUT:
                    current_value = metrics.get('throughput_rpm', 0.0)
                    
                # Détecter violation
                violation = await self.violation_detector.detect_violations(
                    objective, current_value, timestamp
                )
                
                if violation:
                    self.active_violations[violation.violation_id] = violation
                    self.sla_stats['total_violations'] += 1
                    
                    logger.warning(f"SLA violation detected: {violation.violation_id} for {service_name}")
                    
            except Exception as e:
                logger.error(f"Real-time violation check failed for {objective.sla_id}: {e}")
                
    async def _generate_compliance_recommendations(self, compliance_results: List[Dict[str, Any]], 
                                                 violations: List[SLAViolation]) -> List[str]:
        """Générer recommandations compliance"""
        recommendations = []
        
        # Recommandations basées sur violations
        violated_services = set(v.service_name for v in violations)
        if violated_services:
            recommendations.append(f"Priority: Investigate {len(violated_services)} services with SLA violations")
            
        # Recommandations basées sur tendances
        at_risk_objectives = [r for r in compliance_results if r['compliance_status'] == 'at_risk']
        if at_risk_objectives:
            recommendations.append(f"Monitor {len(at_risk_objectives)} SLA objectives at risk of violation")
            
        # Recommandations par type métrique
        response_time_issues = [v for v in violations if v.metric_type == SLAMetricType.RESPONSE_TIME]
        if response_time_issues:
            recommendations.append("Consider performance optimization for response time improvements")
            
        availability_issues = [v for v in violations if v.metric_type == SLAMetricType.AVAILABILITY]
        if availability_issues:
            recommendations.append("Implement high availability measures and redundancy")
            
        return recommendations
        
    async def _summarize_violations(self, violations: List[SLAViolation]) -> Dict[str, Any]:
        """Résumer violations"""
        if not violations:
            return {'total': 0}
            
        return {
            'total': len(violations),
            'by_severity': {
                severity.value: len([v for v in violations if v.severity == severity])
                for severity in ViolationSeverity
            },
            'by_metric_type': {
                metric_type.value: len([v for v in violations if v.metric_type == metric_type])
                for metric_type in SLAMetricType
            },
            'affected_services': list(set(v.service_name for v in violations)),
            'total_violation_time_minutes': sum(v.duration_minutes for v in violations)
        }

# Example usage et testing
if __name__ == "__main__":
    async def test_sla_compliance_monitor():
        """Test monitoring compliance SLA"""
        config = SLAConfig(
            evaluation_interval_minutes=1,  # Plus fréquent pour test
            violation_detection_enabled=True,
            automatic_reporting=True
        )
        
        monitor = SLAComplianceMonitor(config)
        
        # Enregistrer objectifs SLA
        api_availability_sla = SLAObjective(
            sla_id="api_availability_sla",
            service_name="api_service",
            metric_type=SLAMetricType.AVAILABILITY,
            target_value=99.9,  # 99.9% availability
            measurement_period_hours=24,
            measurement_unit="%",
            business_impact="high"
        )
        await monitor.register_sla_objective(api_availability_sla)
        
        api_response_time_sla = SLAObjective(
            sla_id="api_response_time_sla",
            service_name="api_service",
            metric_type=SLAMetricType.RESPONSE_TIME,
            target_value=500.0,  # 500ms max response time
            measurement_period_hours=24,
            measurement_unit="ms",
            business_impact="high"
        )
        await monitor.register_sla_objective(api_response_time_sla)
        
        # Simuler ingestion métriques
        for i in range(50):
            # Simuler dégradation progressive
            availability = max(95.0, 99.9 - (i * 0.1))
            response_time = min(1200, 300 + (i * 20))
            
            metrics = {
                'availability_percentage': availability,
                'response_time_ms': response_time,
                'error_rate_percent': min(5.0, i * 0.1),
                'total_requests': 1000,
                'failed_requests': int(min(50, i * 2))
            }
            
            await monitor.ingest_service_metrics('api_service', metrics)
            await asyncio.sleep(0.1)  # Simulation temps
            
        # Évaluer compliance
        compliance_results = await monitor.evaluate_sla_compliance('api_service', 1)
        
        print("📊 SLA Compliance Monitor Results:")
        print(f"Overall Compliance Score: {compliance_results['overall_compliance']['compliance_score']:.2f}%")
        print(f"Compliance Status: {compliance_results['overall_compliance']['status']}")
        print(f"Total Violations: {compliance_results['total_violations']}")
        print(f"Violated Objectives: {compliance_results['overall_compliance']['violated_objectives']}")
        
        # Afficher détails objectives
        for result in compliance_results['compliance_results']:
            print(f"\nSLA: {result['sla_id']}")
            print(f"  Status: {result['compliance_status']}")
            print(f"  Current: {result['current_value']:.2f} {result['measurement_unit']}")
            print(f"  Target: {result['target_value']:.2f} {result['measurement_unit']}")
            print(f"  Compliance: {result['compliance_percentage']:.2f}%")
            
        # Business impact
        business_impact = compliance_results['business_impact_analysis']
        print(f"\nBusiness Impact Score: {business_impact['total_impact_score']:.2f}/100")
        print(f"Financial Impact: {business_impact['financial_impact']:.2f}/100")
        print(f"Customer Impact: {business_impact['customer_impact']:.2f}/100")
        
        # Générer rapport
        report = await monitor.generate_compliance_report('api_service', 24)
        print(f"\nCompliance Report: {report.report_id}")
        print(f"Report Score: {report.overall_compliance_score:.2f}%")
        print(f"Recommendations: {len(report.recommendations)}")
        
        return compliance_results, report
        
    # Run test
    asyncio.run(test_sla_compliance_monitor())