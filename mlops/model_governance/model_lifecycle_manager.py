"""
📋 Model Lifecycle Manager - Enterprise ML Engineering
© 2025 Fahed Mlaiel <mlaiel@live.de> - Tous droits réservés

⚠️ AVERTISSEMENT LÉGAL:
==========================================
TOUS DROITS RÉSERVÉS - Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE: Licence entreprise disponible sur demande
📧 Contact: mlaiel@live.de

Gestionnaire cycle de vie complet modèles IA Creator Economy
Expertise: ML Engineer + Backend Senior + DevOps + DBA
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class LifecyclePhase(Enum):
    """Model lifecycle phases"""
    DEVELOPMENT = "development"
    TESTING = "testing" 
    VALIDATION = "validation"
    STAGING = "staging"
    PRE_PRODUCTION = "pre_production"
    PRODUCTION = "production"
    MONITORING = "monitoring"
    DEPRECATION = "deprecation"
    RETIREMENT = "retirement"
    ARCHIVED = "archived"


class TransitionTrigger(Enum):
    """Lifecycle transition triggers"""
    MANUAL = "manual"
    AUTOMATED = "automated"
    SCHEDULED = "scheduled"
    PERFORMANCE_BASED = "performance_based"
    COMPLIANCE_DRIVEN = "compliance_driven"
    CREATOR_REQUESTED = "creator_requested"


class QualityGate(Enum):
    """Quality gates for phase transitions"""
    UNIT_TESTS = "unit_tests"
    INTEGRATION_TESTS = "integration_tests"
    PERFORMANCE_TESTS = "performance_tests"
    SECURITY_SCAN = "security_scan"
    COMPLIANCE_CHECK = "compliance_check"
    BUSINESS_VALIDATION = "business_validation"
    CREATOR_APPROVAL = "creator_approval"
    STAKEHOLDER_REVIEW = "stakeholder_review"


@dataclass
class LifecycleMetrics:
    """Metrics for lifecycle phase"""
    phase: LifecyclePhase
    entry_time: datetime
    exit_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    quality_score: float = 0.0
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    creator_satisfaction: Optional[float] = None
    business_impact: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "phase": self.phase.value,
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "duration_seconds": self.duration_seconds,
            "quality_score": self.quality_score,
            "performance_metrics": self.performance_metrics,
            "resource_usage": self.resource_usage,
            "creator_satisfaction": self.creator_satisfaction,
            "business_impact": self.business_impact
        }


@dataclass
class TransitionCriteria:
    """Criteria for phase transition"""
    source_phase: LifecyclePhase
    target_phase: LifecyclePhase
    required_gates: List[QualityGate]
    performance_thresholds: Dict[str, float] = field(default_factory=dict)
    approval_requirements: List[str] = field(default_factory=list)
    automated_checks: List[str] = field(default_factory=list)
    creator_tier_restrictions: Dict[str, List[str]] = field(default_factory=dict)
    minimum_duration: Optional[timedelta] = None
    maximum_duration: Optional[timedelta] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert criteria to dictionary"""
        return {
            "source_phase": self.source_phase.value,
            "target_phase": self.target_phase.value,
            "required_gates": [gate.value for gate in self.required_gates],
            "performance_thresholds": self.performance_thresholds,
            "approval_requirements": self.approval_requirements,
            "automated_checks": self.automated_checks,
            "creator_tier_restrictions": self.creator_tier_restrictions,
            "minimum_duration": self.minimum_duration.total_seconds() if self.minimum_duration else None,
            "maximum_duration": self.maximum_duration.total_seconds() if self.maximum_duration else None
        }


@dataclass
class LifecycleTransition:
    """Model lifecycle transition record"""
    transition_id: str
    model_name: str
    model_version: str
    source_phase: LifecyclePhase
    target_phase: LifecyclePhase
    trigger: TransitionTrigger
    initiated_by: str
    initiated_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "pending"  # pending, in_progress, completed, failed, cancelled
    quality_gates_passed: List[QualityGate] = field(default_factory=list)
    quality_gates_failed: List[QualityGate] = field(default_factory=list)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    creator_context: Optional[Dict[str, Any]] = None
    business_impact: Dict[str, float] = field(default_factory=dict)
    rollback_available: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transition to dictionary"""
        return {
            "transition_id": self.transition_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "source_phase": self.source_phase.value,
            "target_phase": self.target_phase.value,
            "trigger": self.trigger.value,
            "initiated_by": self.initiated_by,
            "initiated_at": self.initiated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "quality_gates_passed": [gate.value for gate in self.quality_gates_passed],
            "quality_gates_failed": [gate.value for gate in self.quality_gates_failed],
            "validation_results": self.validation_results,
            "creator_context": self.creator_context,
            "business_impact": self.business_impact,
            "rollback_available": self.rollback_available
        }


class ModelLifecycleManager:
    """
    📋 Gestionnaire cycle de vie complet modèles IA
    
    Enterprise lifecycle management with:
    - Automated phase transitions with quality gates
    - Creator Economy business rules integration
    - Performance validation at each lifecycle stage
    - Comprehensive metrics collection and analysis
    - Rollback capabilities for production safety
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize lifecycle manager
        
        Args:
            config: Lifecycle management configuration
        """
        self.config = config or self._get_default_config()
        self.manager_id = str(uuid.uuid4())
        
        # Lifecycle tracking
        self._model_lifecycles: Dict[str, Dict[str, Any]] = {}
        self._transition_history: Dict[str, List[LifecycleTransition]] = {}
        self._phase_metrics: Dict[str, List[LifecycleMetrics]] = {}
        
        # Transition criteria registry
        self._transition_criteria: Dict[Tuple[LifecyclePhase, LifecyclePhase], TransitionCriteria] = {}
        
        # Active transitions
        self._active_transitions: Dict[str, LifecycleTransition] = {}
        
        # Quality gate validators
        self._quality_validators: Dict[QualityGate, Callable] = {}
        
        # Performance tracking
        self._performance_metrics = {
            "transitions_total": 0,
            "transitions_success": 0,
            "transitions_failed": 0,
            "avg_transition_time": 0.0,
            "models_managed": 0
        }
        
        # Initialize default transition criteria
        self._initialize_default_criteria()
        
        # Initialize quality gate validators
        self._initialize_quality_validators()
        
        logger.info(f"📋 ModelLifecycleManager initialized with ID: {self.manager_id}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default lifecycle manager configuration"""
        return {
            "creator_economy": {
                "enabled": True,
                "tier_based_transitions": True,
                "creator_approval_required": ["staging", "production"],
                "satisfaction_tracking": True
            },
            "quality_gates": {
                "enforcement_level": "strict",
                "parallel_execution": True,
                "timeout_seconds": 3600,
                "retry_attempts": 3
            },
            "performance_monitoring": {
                "enabled": True,
                "metrics_collection": True,
                "alerting": True,
                "threshold_violations": "block_transition"
            },
            "compliance": {
                "audit_trail": True,
                "retention_days": 365,
                "automated_reporting": True
            },
            "automation": {
                "auto_transitions": ["development->testing", "testing->validation"],
                "scheduled_checks": True,
                "check_interval_minutes": 15
            }
        }
    
    def _initialize_default_criteria(self) -> None:
        """Initialize default transition criteria"""
        
        # Development → Testing
        self._transition_criteria[(LifecyclePhase.DEVELOPMENT, LifecyclePhase.TESTING)] = TransitionCriteria(
            source_phase=LifecyclePhase.DEVELOPMENT,
            target_phase=LifecyclePhase.TESTING,
            required_gates=[QualityGate.UNIT_TESTS, QualityGate.SECURITY_SCAN],
            performance_thresholds={"unit_test_coverage": 0.8},
            automated_checks=["code_quality", "dependency_check"],
            minimum_duration=timedelta(hours=1)
        )
        
        # Testing → Validation
        self._transition_criteria[(LifecyclePhase.TESTING, LifecyclePhase.VALIDATION)] = TransitionCriteria(
            source_phase=LifecyclePhase.TESTING,
            target_phase=LifecyclePhase.VALIDATION,
            required_gates=[QualityGate.INTEGRATION_TESTS, QualityGate.PERFORMANCE_TESTS],
            performance_thresholds={"test_pass_rate": 0.95, "performance_score": 0.8},
            automated_checks=["integration_tests", "performance_benchmarks"],
            minimum_duration=timedelta(hours=4)
        )
        
        # Validation → Staging
        self._transition_criteria[(LifecyclePhase.VALIDATION, LifecyclePhase.STAGING)] = TransitionCriteria(
            source_phase=LifecyclePhase.VALIDATION,
            target_phase=LifecyclePhase.STAGING,
            required_gates=[QualityGate.BUSINESS_VALIDATION, QualityGate.COMPLIANCE_CHECK],
            performance_thresholds={"business_kpi_score": 0.7},
            approval_requirements=["business_analyst", "qa_lead"],
            automated_checks=["compliance_validation", "business_rules_check"],
            minimum_duration=timedelta(days=1)
        )
        
        # Staging → Production
        self._transition_criteria[(LifecyclePhase.STAGING, LifecyclePhase.PRODUCTION)] = TransitionCriteria(
            source_phase=LifecyclePhase.STAGING,
            target_phase=LifecyclePhase.PRODUCTION,
            required_gates=[
                QualityGate.STAKEHOLDER_REVIEW, 
                QualityGate.CREATOR_APPROVAL,
                QualityGate.SECURITY_SCAN,
                QualityGate.COMPLIANCE_CHECK
            ],
            performance_thresholds={
                "staging_success_rate": 0.99,
                "security_score": 0.9,
                "creator_satisfaction": 0.8
            },
            approval_requirements=["technical_lead", "business_owner", "security_team"],
            creator_tier_restrictions={
                "basic": ["requires_premium"],
                "premium": ["allowed"],
                "enterprise": ["allowed"]
            },
            minimum_duration=timedelta(days=3)
        )
        
        logger.info(f"📝 {len(self._transition_criteria)} default transition criteria initialized")
    
    def _initialize_quality_validators(self) -> None:
        """Initialize quality gate validators"""
        
        async def validate_unit_tests(model_data: Dict[str, Any]) -> Dict[str, Any]:
            """Validate unit tests"""
            try:
                test_results = model_data.get("test_results", {})
                coverage = test_results.get("coverage", 0.0)
                pass_rate = test_results.get("pass_rate", 0.0)
                
                passed = coverage >= 0.8 and pass_rate >= 0.95
                
                return {
                    "passed": passed,
                    "score": min(coverage, pass_rate),
                    "details": {
                        "coverage": coverage,
                        "pass_rate": pass_rate,
                        "threshold_coverage": 0.8,
                        "threshold_pass_rate": 0.95
                    }
                }
            except Exception as e:
                return {"passed": False, "error": str(e), "score": 0.0}
        
        async def validate_integration_tests(model_data: Dict[str, Any]) -> Dict[str, Any]:
            """Validate integration tests"""
            try:
                integration_results = model_data.get("integration_results", {})
                success_rate = integration_results.get("success_rate", 0.0)
                latency_p95 = integration_results.get("latency_p95", float('inf'))
                
                passed = success_rate >= 0.95 and latency_p95 <= 1000  # 1 second
                
                return {
                    "passed": passed,
                    "score": success_rate,
                    "details": {
                        "success_rate": success_rate,
                        "latency_p95": latency_p95,
                        "threshold_success": 0.95,
                        "threshold_latency": 1000
                    }
                }
            except Exception as e:
                return {"passed": False, "error": str(e), "score": 0.0}
        
        async def validate_performance_tests(model_data: Dict[str, Any]) -> Dict[str, Any]:
            """Validate performance tests"""
            try:
                perf_results = model_data.get("performance_results", {})
                throughput = perf_results.get("throughput", 0.0)
                accuracy = perf_results.get("accuracy", 0.0)
                memory_usage = perf_results.get("memory_usage_mb", float('inf'))
                
                passed = (
                    throughput >= 100 and  # 100 requests/second
                    accuracy >= 0.85 and
                    memory_usage <= 2048  # 2GB
                )
                
                score = min(throughput/100, accuracy, 2048/memory_usage) if memory_usage > 0 else 0
                
                return {
                    "passed": passed,
                    "score": score,
                    "details": {
                        "throughput": throughput,
                        "accuracy": accuracy,
                        "memory_usage_mb": memory_usage,
                        "thresholds": {
                            "min_throughput": 100,
                            "min_accuracy": 0.85,
                            "max_memory_mb": 2048
                        }
                    }
                }
            except Exception as e:
                return {"passed": False, "error": str(e), "score": 0.0}
        
        async def validate_security_scan(model_data: Dict[str, Any]) -> Dict[str, Any]:
            """Validate security scan"""
            try:
                security_results = model_data.get("security_results", {})
                vulnerabilities = security_results.get("vulnerabilities", [])
                security_score = security_results.get("security_score", 0.0)
                
                critical_vulns = [v for v in vulnerabilities if v.get("severity") == "critical"]
                high_vulns = [v for v in vulnerabilities if v.get("severity") == "high"]
                
                passed = len(critical_vulns) == 0 and len(high_vulns) <= 2 and security_score >= 0.8
                
                return {
                    "passed": passed,
                    "score": security_score,
                    "details": {
                        "total_vulnerabilities": len(vulnerabilities),
                        "critical_vulnerabilities": len(critical_vulns),
                        "high_vulnerabilities": len(high_vulns),
                        "security_score": security_score,
                        "thresholds": {
                            "max_critical": 0,
                            "max_high": 2,
                            "min_security_score": 0.8
                        }
                    }
                }
            except Exception as e:
                return {"passed": False, "error": str(e), "score": 0.0}
        
        async def validate_compliance_check(model_data: Dict[str, Any]) -> Dict[str, Any]:
            """Validate compliance requirements"""
            try:
                compliance_results = model_data.get("compliance_results", {})
                gdpr_compliant = compliance_results.get("gdpr_compliant", False)
                ccpa_compliant = compliance_results.get("ccpa_compliant", False)
                data_lineage_complete = compliance_results.get("data_lineage_complete", False)
                
                passed = gdpr_compliant and ccpa_compliant and data_lineage_complete
                score = sum([gdpr_compliant, ccpa_compliant, data_lineage_complete]) / 3.0
                
                return {
                    "passed": passed,
                    "score": score,
                    "details": {
                        "gdpr_compliant": gdpr_compliant,
                        "ccpa_compliant": ccpa_compliant,
                        "data_lineage_complete": data_lineage_complete
                    }
                }
            except Exception as e:
                return {"passed": False, "error": str(e), "score": 0.0}
        
        async def validate_business_validation(model_data: Dict[str, Any]) -> Dict[str, Any]:
            """Validate business requirements"""
            try:
                business_results = model_data.get("business_results", {})
                roi_projection = business_results.get("roi_projection", 0.0)
                user_acceptance = business_results.get("user_acceptance", 0.0)
                business_kpi_score = business_results.get("business_kpi_score", 0.0)
                
                passed = roi_projection >= 1.2 and user_acceptance >= 0.7 and business_kpi_score >= 0.7
                score = min(roi_projection/1.2, user_acceptance, business_kpi_score)
                
                return {
                    "passed": passed,
                    "score": score,
                    "details": {
                        "roi_projection": roi_projection,
                        "user_acceptance": user_acceptance,
                        "business_kpi_score": business_kpi_score,
                        "thresholds": {
                            "min_roi": 1.2,
                            "min_user_acceptance": 0.7,
                            "min_business_kpi": 0.7
                        }
                    }
                }
            except Exception as e:
                return {"passed": False, "error": str(e), "score": 0.0}
        
        async def validate_creator_approval(model_data: Dict[str, Any]) -> Dict[str, Any]:
            """Validate creator approval"""
            try:
                creator_data = model_data.get("creator_context", {})
                approval_status = creator_data.get("approval_status", "pending")
                creator_satisfaction = creator_data.get("satisfaction_score", 0.0)
                
                passed = approval_status == "approved" and creator_satisfaction >= 0.8
                
                return {
                    "passed": passed,
                    "score": creator_satisfaction,
                    "details": {
                        "approval_status": approval_status,
                        "creator_satisfaction": creator_satisfaction,
                        "creator_id": creator_data.get("creator_id"),
                        "threshold_satisfaction": 0.8
                    }
                }
            except Exception as e:
                return {"passed": False, "error": str(e), "score": 0.0}
        
        async def validate_stakeholder_review(model_data: Dict[str, Any]) -> Dict[str, Any]:
            """Validate stakeholder review"""
            try:
                review_data = model_data.get("stakeholder_review", {})
                approvals = review_data.get("approvals", [])
                required_approvals = review_data.get("required_approvals", [])
                
                approved_set = set(approvals)
                required_set = set(required_approvals)
                
                passed = required_set.issubset(approved_set)
                score = len(approved_set & required_set) / len(required_set) if required_set else 1.0
                
                return {
                    "passed": passed,
                    "score": score,
                    "details": {
                        "approvals_received": approvals,
                        "approvals_required": required_approvals,
                        "missing_approvals": list(required_set - approved_set)
                    }
                }
            except Exception as e:
                return {"passed": False, "error": str(e), "score": 0.0}
        
        # Register validators
        self._quality_validators = {
            QualityGate.UNIT_TESTS: validate_unit_tests,
            QualityGate.INTEGRATION_TESTS: validate_integration_tests,
            QualityGate.PERFORMANCE_TESTS: validate_performance_tests,
            QualityGate.SECURITY_SCAN: validate_security_scan,
            QualityGate.COMPLIANCE_CHECK: validate_compliance_check,
            QualityGate.BUSINESS_VALIDATION: validate_business_validation,
            QualityGate.CREATOR_APPROVAL: validate_creator_approval,
            QualityGate.STAKEHOLDER_REVIEW: validate_stakeholder_review
        }
        
        logger.info(f"🔍 {len(self._quality_validators)} quality gate validators initialized")
    
    async def initiate_transition(
        self,
        model_name: str,
        model_version: str,
        target_phase: LifecyclePhase,
        trigger: TransitionTrigger = TransitionTrigger.MANUAL,
        initiated_by: str = "system",
        creator_context: Optional[Dict[str, Any]] = None,
        model_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Initiate model lifecycle transition
        
        Args:
            model_name: Name of the model
            model_version: Version of the model
            target_phase: Target lifecycle phase
            trigger: Transition trigger type
            initiated_by: User/system initiating transition
            creator_context: Creator-specific context
            model_data: Model data for validation
            
        Returns:
            Transition ID
        """
        try:
            model_key = f"{model_name}:{model_version}"
            
            # Get current phase
            current_lifecycle = self._model_lifecycles.get(model_key, {})
            current_phase = LifecyclePhase(current_lifecycle.get("current_phase", "development"))
            
            # Validate transition
            transition_key = (current_phase, target_phase)
            if transition_key not in self._transition_criteria:
                raise ValueError(f"No transition criteria defined for {current_phase.value} → {target_phase.value}")
            
            criteria = self._transition_criteria[transition_key]
            
            # Check creator tier restrictions if applicable
            if creator_context and criteria.creator_tier_restrictions:
                creator_tier = creator_context.get("tier", "basic")
                if target_phase.value in criteria.creator_tier_restrictions.get(creator_tier, []):
                    raise ValueError(f"Creator tier '{creator_tier}' not allowed for {target_phase.value} phase")
            
            # Create transition record
            transition = LifecycleTransition(
                transition_id=str(uuid.uuid4()),
                model_name=model_name,
                model_version=model_version,
                source_phase=current_phase,
                target_phase=target_phase,
                trigger=trigger,
                initiated_by=initiated_by,
                initiated_at=datetime.now(),
                creator_context=creator_context,
                status="in_progress"
            )
            
            # Store active transition
            self._active_transitions[transition.transition_id] = transition
            
            logger.info(f"🔄 Initiated transition {transition.transition_id}: {model_name} {current_phase.value} → {target_phase.value}")
            
            # Execute transition asynchronously
            asyncio.create_task(self._execute_transition(transition, criteria, model_data or {}))
            
            return transition.transition_id
            
        except Exception as e:
            logger.error(f"❌ Failed to initiate transition: {str(e)}")
            raise
    
    async def _execute_transition(
        self,
        transition: LifecycleTransition,
        criteria: TransitionCriteria,
        model_data: Dict[str, Any]
    ) -> None:
        """Execute lifecycle transition with quality gates"""
        try:
            logger.info(f"⚡ Executing transition {transition.transition_id}")
            
            # Execute quality gates
            for gate in criteria.required_gates:
                if gate in self._quality_validators:
                    validator = self._quality_validators[gate]
                    validation_result = await validator(model_data)
                    
                    transition.validation_results[gate.value] = validation_result
                    
                    if validation_result["passed"]:
                        transition.quality_gates_passed.append(gate)
                        logger.info(f"✅ Quality gate {gate.value} passed for {transition.transition_id}")
                    else:
                        transition.quality_gates_failed.append(gate)
                        logger.warning(f"❌ Quality gate {gate.value} failed for {transition.transition_id}")
                else:
                    logger.warning(f"⚠️ No validator found for quality gate {gate.value}")
            
            # Check if all required gates passed
            all_gates_passed = len(transition.quality_gates_failed) == 0
            
            if all_gates_passed:
                # Complete transition
                await self._complete_transition(transition)
            else:
                # Fail transition
                await self._fail_transition(transition, "Quality gates failed")
                
        except Exception as e:
            logger.error(f"❌ Transition execution failed: {str(e)}")
            await self._fail_transition(transition, str(e))
    
    async def _complete_transition(self, transition: LifecycleTransition) -> None:
        """Complete successful transition"""
        try:
            model_key = f"{transition.model_name}:{transition.model_version}"
            
            # Update model lifecycle state
            if model_key not in self._model_lifecycles:
                self._model_lifecycles[model_key] = {
                    "model_name": transition.model_name,
                    "model_version": transition.model_version,
                    "created_at": datetime.now().isoformat(),
                    "phase_history": []
                }
            
            # Record phase change
            self._model_lifecycles[model_key]["current_phase"] = transition.target_phase.value
            self._model_lifecycles[model_key]["last_updated"] = datetime.now().isoformat()
            self._model_lifecycles[model_key]["phase_history"].append({
                "phase": transition.target_phase.value,
                "entered_at": datetime.now().isoformat(),
                "transition_id": transition.transition_id
            })
            
            # Complete transition record
            transition.completed_at = datetime.now()
            transition.status = "completed"
            
            # Add to history
            if model_key not in self._transition_history:
                self._transition_history[model_key] = []
            self._transition_history[model_key].append(transition)
            
            # Remove from active transitions
            if transition.transition_id in self._active_transitions:
                del self._active_transitions[transition.transition_id]
            
            # Update metrics
            self._performance_metrics["transitions_total"] += 1
            self._performance_metrics["transitions_success"] += 1
            
            execution_time = (transition.completed_at - transition.initiated_at).total_seconds()
            self._performance_metrics["avg_transition_time"] = (
                (self._performance_metrics["avg_transition_time"] * (self._performance_metrics["transitions_total"] - 1) + execution_time)
                / self._performance_metrics["transitions_total"]
            )
            
            logger.info(f"✅ Transition {transition.transition_id} completed successfully in {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to complete transition: {str(e)}")
            raise
    
    async def _fail_transition(self, transition: LifecycleTransition, reason: str) -> None:
        """Handle failed transition"""
        try:
            transition.completed_at = datetime.now()
            transition.status = "failed"
            transition.validation_results["failure_reason"] = reason
            
            model_key = f"{transition.model_name}:{transition.model_version}"
            
            # Add to history
            if model_key not in self._transition_history:
                self._transition_history[model_key] = []
            self._transition_history[model_key].append(transition)
            
            # Remove from active transitions
            if transition.transition_id in self._active_transitions:
                del self._active_transitions[transition.transition_id]
            
            # Update metrics
            self._performance_metrics["transitions_total"] += 1
            self._performance_metrics["transitions_failed"] += 1
            
            logger.error(f"❌ Transition {transition.transition_id} failed: {reason}")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle transition failure: {str(e)}")
    
    def get_model_lifecycle(self, model_name: str, model_version: str) -> Optional[Dict[str, Any]]:
        """Get current lifecycle state of a model"""
        model_key = f"{model_name}:{model_version}"
        return self._model_lifecycles.get(model_key)
    
    def get_transition_history(self, model_name: str, model_version: str) -> List[Dict[str, Any]]:
        """Get transition history for a model"""
        model_key = f"{model_name}:{model_version}"
        transitions = self._transition_history.get(model_key, [])
        return [t.to_dict() for t in transitions]
    
    def get_active_transitions(self) -> List[Dict[str, Any]]:
        """Get all active transitions"""
        return [t.to_dict() for t in self._active_transitions.values()]
    
    def get_lifecycle_metrics(self) -> Dict[str, Any]:
        """Get lifecycle management metrics"""
        return {
            **self._performance_metrics,
            "models_managed": len(self._model_lifecycles),
            "active_transitions": len(self._active_transitions),
            "transition_criteria": len(self._transition_criteria),
            "quality_validators": len(self._quality_validators)
        }
    
    def register_transition_criteria(self, criteria: TransitionCriteria) -> bool:
        """Register custom transition criteria"""
        try:
            key = (criteria.source_phase, criteria.target_phase)
            self._transition_criteria[key] = criteria
            logger.info(f"📝 Registered transition criteria: {criteria.source_phase.value} → {criteria.target_phase.value}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to register transition criteria: {str(e)}")
            return False
    
    def register_quality_validator(self, gate: QualityGate, validator: Callable) -> bool:
        """Register custom quality gate validator"""
        try:
            self._quality_validators[gate] = validator
            logger.info(f"🔍 Registered quality validator for {gate.value}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to register quality validator: {str(e)}")
            return False
    
    def health_check(self) -> str:
        """Health check for lifecycle manager"""
        try:
            # Check internal state
            if not self._transition_criteria:
                return "ERROR: No transition criteria configured"
            
            if not self._quality_validators:
                return "ERROR: No quality validators configured"
            
            # Check for stuck transitions
            now = datetime.now()
            stuck_transitions = [
                t for t in self._active_transitions.values()
                if (now - t.initiated_at).total_seconds() > 7200  # 2 hours
            ]
            
            if stuck_transitions:
                return f"WARNING: {len(stuck_transitions)} stuck transitions detected"
            
            return "OPERATIONAL"
            
        except Exception as e:
            return f"ERROR: {str(e)}"


# Export main class and enums
__all__ = [
    "ModelLifecycleManager",
    "LifecyclePhase",
    "TransitionTrigger", 
    "QualityGate",
    "LifecycleMetrics",
    "TransitionCriteria",
    "LifecycleTransition"
]