"""
🎛️ MLOps Model Governance Orchestrator - Enterprise Architecture
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

Orchestrateur principal gouvernance modèles IA Creator Economy
Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager

# Core governance imports
from .model_governance import ModelGovernanceCore
from .model_registry import ModelRegistry, ModelStatus, ModelType
from .access_control_engine import AccessControlEngine
from .audit_logger import AuditLogger
from .dependency_resolver import DependencyResolver
from .model_poisoning_detector import ModelPoisoningDetector
from .vulnerability_scanner import VulnerabilityScanner

logger = logging.getLogger(__name__)


class OrchestrationMode(Enum):
    """Orchestration execution modes"""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    BATCH = "batch"
    STREAMING = "streaming"
    ENTERPRISE = "enterprise"


class GovernanceLevel(Enum):
    """Governance strictness levels"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ENTERPRISE = "enterprise"
    CRITICAL = "critical"


@dataclass
class GovernancePolicy:
    """Governance policy configuration"""
    name: str
    level: GovernanceLevel
    auto_approval: bool = False
    risk_threshold: float = 0.7
    compliance_checks: List[str] = field(default_factory=list)
    creator_tier_restrictions: Dict[str, List[str]] = field(default_factory=dict)
    monitoring_interval: int = 300  # seconds
    retention_days: int = 90
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary"""
        return {
            "name": self.name,
            "level": self.level.value,
            "auto_approval": self.auto_approval,
            "risk_threshold": self.risk_threshold,
            "compliance_checks": self.compliance_checks,
            "creator_tier_restrictions": self.creator_tier_restrictions,
            "monitoring_interval": self.monitoring_interval,
            "retention_days": self.retention_days
        }


@dataclass
class OrchestrationResult:
    """Result of orchestration operation"""
    operation_id: str
    success: bool
    components_affected: List[str]
    execution_time: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "operation_id": self.operation_id,
            "success": self.success,
            "components_affected": self.components_affected,
            "execution_time": self.execution_time,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata
        }


class ModelGovernanceOrchestrator:
    """
    🎛️ Orchestrateur central gouvernance modèles IA Creator Economy
    
    Enterprise-grade orchestration engine for ML governance with:
    - Factory pattern component instantiation
    - Real-time governance dashboard coordination  
    - Creator Economy business rules integration
    - Compliance automation workflow
    - Performance monitoring orchestration
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        mode: OrchestrationMode = OrchestrationMode.ENTERPRISE
    ):
        """
        Initialize governance orchestrator
        
        Args:
            config: Orchestrator configuration
            mode: Execution mode for orchestration
        """
        self.config = config or self._get_default_config()
        self.mode = mode
        self.operation_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        
        # Component registry
        self._components: Dict[str, Any] = {}
        self._policies: Dict[str, GovernancePolicy] = {}
        self._active_workflows: Dict[str, Any] = {}
        
        # Performance metrics
        self._metrics = {
            "operations_total": 0,
            "operations_success": 0,
            "operations_failed": 0,
            "avg_execution_time": 0.0,
            "components_initialized": 0
        }
        
        # Initialize core components using factory pattern
        self._initialize_components()
        
        logger.info(f"🎛️ ModelGovernanceOrchestrator initialized in {mode.value} mode")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default orchestrator configuration"""
        return {
            "tracking_uri": "file://./mlflow_runs",
            "experiment_name": "iacherie_governance",
            "governance_level": GovernanceLevel.ENTERPRISE.value,
            "creator_economy": {
                "enabled": True,
                "tier_system": True,
                "permission_matrix": True,
                "revenue_tracking": True
            },
            "compliance": {
                "standards": ["GDPR", "CCPA", "SOC2", "ISO27001"],
                "auto_validation": True,
                "audit_trail": True
            },
            "monitoring": {
                "real_time": True,
                "performance_alerts": True,
                "drift_detection": True,
                "business_metrics": True
            },
            "security": {
                "access_control": "RBAC",
                "encryption": "AES256",
                "vulnerability_scanning": True,
                "threat_detection": True
            }
        }
    
    def _initialize_components(self) -> None:
        """Initialize governance components using factory pattern"""
        try:
            logger.info("🏭 Initializing governance components...")
            
            # Core governance
            self._components["governance_core"] = ModelGovernanceCore(self.config)
            
            # Model registry with enterprise features
            self._components["model_registry"] = ModelRegistry(
                tracking_uri=self.config.get("tracking_uri"),
                experiment_name=self.config.get("experiment_name")
            )
            
            # Security and access control
            self._components["access_control"] = AccessControlEngine(
                config=self.config.get("security", {})
            )
            
            # Enterprise audit system
            self._components["audit_logger"] = AuditLogger(
                config=self.config.get("compliance", {})
            )
            
            # Dependency management
            self._components["dependency_resolver"] = DependencyResolver(
                config=self.config.get("dependencies", {})
            )
            
            # Security scanners
            self._components["poisoning_detector"] = ModelPoisoningDetector(
                config=self.config.get("security", {})
            )
            
            self._components["vulnerability_scanner"] = VulnerabilityScanner(
                config=self.config.get("security", {})
            )
            
            self._metrics["components_initialized"] = len(self._components)
            
            logger.info(f"✅ {len(self._components)} governance components initialized")
            
        except Exception as e:
            logger.error(f"❌ Component initialization failed: {str(e)}")
            raise
    
    async def orchestrate_model_lifecycle(
        self,
        model_name: str,
        model_data: Dict[str, Any],
        target_stage: ModelStatus,
        creator_context: Optional[Dict[str, Any]] = None
    ) -> OrchestrationResult:
        """
        Orchestrate complete model lifecycle transition
        
        Args:
            model_name: Name of the model
            model_data: Model data and metadata
            target_stage: Target lifecycle stage
            creator_context: Creator-specific context
            
        Returns:
            Orchestration result with detailed status
        """
        operation_start = datetime.now()
        operation_id = str(uuid.uuid4())
        components_affected = []
        errors = []
        warnings = []
        
        try:
            logger.info(f"🔄 Orchestrating {model_name} lifecycle → {target_stage.value}")
            
            # 1. Validate creator permissions
            if creator_context:
                permission_result = await self._validate_creator_permissions(
                    model_name, creator_context, target_stage
                )
                if not permission_result["allowed"]:
                    errors.append(f"Creator permission denied: {permission_result['reason']}")
                    return OrchestrationResult(
                        operation_id=operation_id,
                        success=False,
                        components_affected=["access_control"],
                        execution_time=(datetime.now() - operation_start).total_seconds(),
                        errors=errors
                    )
                components_affected.append("access_control")
            
            # 2. Security and vulnerability scanning
            security_result = await self._run_security_scans(model_name, model_data)
            components_affected.extend(["poisoning_detector", "vulnerability_scanner"])
            
            if not security_result["passed"]:
                errors.extend(security_result["issues"])
                if target_stage in [ModelStatus.PRODUCTION, ModelStatus.STAGING]:
                    return OrchestrationResult(
                        operation_id=operation_id,
                        success=False,
                        components_affected=components_affected,
                        execution_time=(datetime.now() - operation_start).total_seconds(),
                        errors=errors
                    )
                else:
                    warnings.extend(security_result["issues"])
            
            # 3. Dependency resolution and validation
            dependency_result = await self._resolve_dependencies(model_name, model_data)
            components_affected.append("dependency_resolver")
            
            if not dependency_result["resolved"]:
                errors.extend(dependency_result["conflicts"])
                return OrchestrationResult(
                    operation_id=operation_id,
                    success=False,
                    components_affected=components_affected,
                    execution_time=(datetime.now() - operation_start).total_seconds(),
                    errors=errors
                )
            
            # 4. Model registration and versioning
            registry_result = await self._register_model_version(
                model_name, model_data, target_stage
            )
            components_affected.append("model_registry")
            
            if not registry_result["success"]:
                errors.append(f"Model registration failed: {registry_result['error']}")
                return OrchestrationResult(
                    operation_id=operation_id,
                    success=False,
                    components_affected=components_affected,
                    execution_time=(datetime.now() - operation_start).total_seconds(),
                    errors=errors
                )
            
            # 5. Audit logging
            await self._log_orchestration_audit(
                operation_id, model_name, target_stage, creator_context
            )
            components_affected.append("audit_logger")
            
            execution_time = (datetime.now() - operation_start).total_seconds()
            
            # Update metrics
            self._metrics["operations_total"] += 1
            self._metrics["operations_success"] += 1
            self._metrics["avg_execution_time"] = (
                (self._metrics["avg_execution_time"] * (self._metrics["operations_total"] - 1) + execution_time)
                / self._metrics["operations_total"]
            )
            
            logger.info(f"✅ Model {model_name} lifecycle orchestration completed in {execution_time:.2f}s")
            
            return OrchestrationResult(
                operation_id=operation_id,
                success=True,
                components_affected=components_affected,
                execution_time=execution_time,
                errors=errors,
                warnings=warnings,
                metadata={
                    "model_name": model_name,
                    "target_stage": target_stage.value,
                    "registry_run_id": registry_result["run_id"],
                    "creator_context": creator_context
                }
            )
            
        except Exception as e:
            execution_time = (datetime.now() - operation_start).total_seconds()
            self._metrics["operations_total"] += 1
            self._metrics["operations_failed"] += 1
            
            logger.error(f"❌ Orchestration failed for {model_name}: {str(e)}")
            
            return OrchestrationResult(
                operation_id=operation_id,
                success=False,
                components_affected=components_affected,
                execution_time=execution_time,
                errors=[str(e)]
            )
    
    async def _validate_creator_permissions(
        self,
        model_name: str,
        creator_context: Dict[str, Any],
        target_stage: ModelStatus
    ) -> Dict[str, Any]:
        """Validate creator permissions for model operation"""
        try:
            access_control = self._components["access_control"]
            
            creator_id = creator_context.get("creator_id")
            creator_tier = creator_context.get("tier", "basic")
            creator_permissions = creator_context.get("permissions", [])
            
            # Check tier restrictions
            tier_restrictions = self.config.get("creator_economy", {}).get("tier_restrictions", {})
            if target_stage.value in tier_restrictions.get(creator_tier, []):
                return {
                    "allowed": False,
                    "reason": f"Creator tier '{creator_tier}' not allowed for {target_stage.value} stage"
                }
            
            # Check specific permissions
            required_permission = f"model:{target_stage.value}"
            if required_permission not in creator_permissions:
                return {
                    "allowed": False,
                    "reason": f"Missing required permission: {required_permission}"
                }
            
            return {"allowed": True, "reason": "Permission granted"}
            
        except Exception as e:
            logger.error(f"Permission validation error: {str(e)}")
            return {"allowed": False, "reason": f"Validation error: {str(e)}"}
    
    async def _run_security_scans(
        self,
        model_name: str,
        model_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run comprehensive security scans"""
        try:
            issues = []
            
            # Model poisoning detection
            poisoning_detector = self._components["poisoning_detector"]
            poisoning_result = poisoning_detector.detect_model_poisoning(
                model_data.get("model"), model_data.get("training_data")
            )
            
            if not poisoning_result["is_clean"]:
                issues.extend([f"Poisoning: {threat}" for threat in poisoning_result["threats"]])
            
            # Vulnerability scanning
            vulnerability_scanner = self._components["vulnerability_scanner"]
            vuln_result = vulnerability_scanner.scan_model_vulnerabilities(
                model_data.get("model"), model_data.get("dependencies", [])
            )
            
            if vuln_result["vulnerabilities"]:
                issues.extend([f"Vulnerability: {vuln}" for vuln in vuln_result["vulnerabilities"]])
            
            return {
                "passed": len(issues) == 0,
                "issues": issues,
                "poisoning_score": poisoning_result.get("confidence_score", 0.0),
                "vulnerability_count": len(vuln_result.get("vulnerabilities", []))
            }
            
        except Exception as e:
            logger.error(f"Security scan error: {str(e)}")
            return {"passed": False, "issues": [f"Security scan failed: {str(e)}"]}
    
    async def _resolve_dependencies(
        self,
        model_name: str,
        model_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve and validate model dependencies"""
        try:
            dependency_resolver = self._components["dependency_resolver"]
            
            dependencies = model_data.get("dependencies", [])
            resolution_result = dependency_resolver.resolve_dependencies(
                model_name, dependencies
            )
            
            return {
                "resolved": resolution_result["success"],
                "conflicts": resolution_result.get("conflicts", []),
                "resolved_dependencies": resolution_result.get("resolved", [])
            }
            
        except Exception as e:
            logger.error(f"Dependency resolution error: {str(e)}")
            return {"resolved": False, "conflicts": [f"Resolution failed: {str(e)}"]}
    
    async def _register_model_version(
        self,
        model_name: str,
        model_data: Dict[str, Any],
        target_stage: ModelStatus
    ) -> Dict[str, Any]:
        """Register model version in registry"""
        try:
            model_registry = self._components["model_registry"]
            
            run_id = model_registry.register_model(
                model=model_data.get("model"),
                model_name=model_name,
                model_version=model_data.get("version", "1.0.0"),
                metrics=model_data.get("metrics", {}),
                parameters=model_data.get("parameters", {}),
                artifacts=model_data.get("artifacts"),
                tags={"target_stage": target_stage.value},
                description=model_data.get("description")
            )
            
            return {"success": True, "run_id": run_id}
            
        except Exception as e:
            logger.error(f"Model registration error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _log_orchestration_audit(
        self,
        operation_id: str,
        model_name: str,
        target_stage: ModelStatus,
        creator_context: Optional[Dict[str, Any]]
    ) -> None:
        """Log orchestration audit trail"""
        try:
            audit_logger = self._components["audit_logger"]
            
            audit_data = {
                "operation_id": operation_id,
                "operation_type": "model_lifecycle_orchestration",
                "model_name": model_name,
                "target_stage": target_stage.value,
                "creator_context": creator_context,
                "timestamp": datetime.now().isoformat(),
                "orchestrator_mode": self.mode.value
            }
            
            audit_logger.log_governance_event(
                event_type="model_orchestration",
                details=audit_data,
                user_id=creator_context.get("creator_id") if creator_context else "system",
                model_name=model_name
            )
            
        except Exception as e:
            logger.error(f"Audit logging error: {str(e)}")
    
    def register_governance_policy(self, policy: GovernancePolicy) -> bool:
        """Register a new governance policy"""
        try:
            self._policies[policy.name] = policy
            logger.info(f"📋 Governance policy '{policy.name}' registered")
            return True
        except Exception as e:
            logger.error(f"Policy registration error: {str(e)}")
            return False
    
    def get_orchestration_metrics(self) -> Dict[str, Any]:
        """Get orchestrator performance metrics"""
        return {
            **self._metrics,
            "uptime": (datetime.now() - self.start_time).total_seconds(),
            "components_count": len(self._components),
            "policies_count": len(self._policies),
            "active_workflows": len(self._active_workflows),
            "mode": self.mode.value
        }
    
    def get_component_health(self) -> Dict[str, str]:
        """Get health status of all components"""
        health_status = {}
        
        for name, component in self._components.items():
            try:
                # Check if component has health check method
                if hasattr(component, 'health_check'):
                    health_status[name] = component.health_check()
                else:
                    health_status[name] = "OPERATIONAL"
            except Exception as e:
                health_status[name] = f"ERROR: {str(e)}"
        
        return health_status
    
    @asynccontextmanager
    async def governance_context(self, context_data: Dict[str, Any]):
        """Context manager for governance operations"""
        context_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            logger.info(f"🎯 Starting governance context {context_id}")
            yield context_id
        finally:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"🏁 Governance context {context_id} completed in {execution_time:.2f}s")
    
    def shutdown(self) -> None:
        """Gracefully shutdown orchestrator"""
        try:
            logger.info("🛑 Shutting down ModelGovernanceOrchestrator...")
            
            # Close component connections
            for name, component in self._components.items():
                if hasattr(component, 'close'):
                    component.close()
                    logger.info(f"📴 {name} component closed")
            
            # Clear internal state
            self._components.clear()
            self._policies.clear()
            self._active_workflows.clear()
            
            logger.info("✅ ModelGovernanceOrchestrator shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {str(e)}")


# Factory function for orchestrator instantiation
def create_governance_orchestrator(
    config: Optional[Dict[str, Any]] = None,
    mode: OrchestrationMode = OrchestrationMode.ENTERPRISE
) -> ModelGovernanceOrchestrator:
    """
    Factory function to create ModelGovernanceOrchestrator instance
    
    Args:
        config: Orchestrator configuration
        mode: Orchestration mode
        
    Returns:
        Configured orchestrator instance
    """
    try:
        orchestrator = ModelGovernanceOrchestrator(config=config, mode=mode)
        logger.info("🏭 ModelGovernanceOrchestrator created via factory")
        return orchestrator
    except Exception as e:
        logger.error(f"❌ Factory creation failed: {str(e)}")
        raise


# Export main orchestrator class and factory
__all__ = [
    "ModelGovernanceOrchestrator",
    "GovernancePolicy", 
    "OrchestrationResult",
    "OrchestrationMode",
    "GovernanceLevel",
    "create_governance_orchestrator"
]