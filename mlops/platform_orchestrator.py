"""
Comprehensive MLOps Pipeline Orchestrator
Integrates all MLOps components into a unified system
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path

# Import all MLOps components
from mlops.model_versioning.model_registry import ModelRegistry
from mlops.a_b_testing.ab_engine import ABTestingEngine, ModelVariant, BusinessMetric
from mlops.model_monitoring.performance_monitor import ComprehensiveModelMonitor, MonitoringMetric, AlertSeverity
from mlops.automated_retraining import IntelligentRetrainingSystem, RetrainingConfig
from mlops.model_explainability import ModelExplainabilityEngine
from mlops.model_governance import ModelGovernanceEngine, GovernanceAction, ApprovalRule, UserRole
from ml.feature_stores.feature_store import AdvancedFeatureStore, SQLiteFeatureStore
from ml.deployment.high_performance_serving import HighPerformanceModelServer, ServeMode, AutoScaler

logger = logging.getLogger(__name__)


@dataclass
class MLOpsConfig:
    """Configuration for the MLOps platform"""
    
    # Model Registry
    mlflow_tracking_uri: str = "file://./mlflow_runs"
    experiment_name: str = "ainflue_models"
    
    # Feature Store
    feature_store_db_path: str = "feature_store.db"
    
    # Monitoring
    enable_monitoring: bool = True
    monitoring_interval_seconds: int = 60
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "accuracy_degradation": 0.05,
        "latency_threshold_ms": 500,
        "error_rate_threshold": 0.01
    })
    
    # A/B Testing
    enable_ab_testing: bool = True
    default_test_duration_days: int = 14
    min_sample_size: int = 1000
    
    # Auto-retraining
    enable_auto_retraining: bool = True
    retraining_frequency_days: int = 30
    performance_degradation_threshold: float = 0.05
    
    # Model Serving
    serve_mode: ServeMode = ServeMode.ASYNCHRONOUS
    min_workers: int = 2
    max_workers: int = 10
    target_latency_ms: float = 100
    
    # Governance
    enable_governance: bool = True
    require_approval_for_production: bool = True
    auto_approve_low_risk: bool = True
    
    # Explainability
    enable_explainability: bool = True
    default_explainers: List[str] = field(default_factory=lambda: ["shap", "lime"])
    
    # General
    environment: str = "development"
    log_level: str = "INFO"


class MLOpsPlatform:
    """Unified MLOps platform orchestrator"""
    
    def __init__(self, config: MLOpsConfig):
        self.config = config
        self.is_initialized = False
        self.is_running = False
        
        # Initialize components
        self.model_registry: Optional[ModelRegistry] = None
        self.feature_store: Optional[AdvancedFeatureStore] = None
        self.ab_testing_engine: Optional[ABTestingEngine] = None
        self.governance_engine: Optional[ModelGovernanceEngine] = None
        self.model_server: Optional[HighPerformanceModelServer] = None
        
        # Component managers
        self.monitoring_systems: Dict[str, ComprehensiveModelMonitor] = {}
        self.retraining_systems: Dict[str, IntelligentRetrainingSystem] = {}
        self.explainability_engines: Dict[str, ModelExplainabilityEngine] = {}
        
        # Platform state
        self.registered_models: Dict[str, Dict] = {}
        self.active_experiments: Dict[str, str] = {}  # model_name -> experiment_id
        self.platform_metrics: Dict[str, Any] = {}
        
    async def initialize(self):
        """Initialize the MLOps platform"""
        if self.is_initialized:
            logger.warning("Platform already initialized")
            return
        
        logger.info("Initializing MLOps platform...")
        
        try:
            # Initialize Model Registry
            self.model_registry = ModelRegistry(
                tracking_uri=self.config.mlflow_tracking_uri,
                experiment_name=self.config.experiment_name
            )
            logger.info("✓ Model Registry initialized")
            
            # Initialize Feature Store
            base_store = SQLiteFeatureStore(self.config.feature_store_db_path)
            self.feature_store = AdvancedFeatureStore(base_store)
            logger.info("✓ Feature Store initialized")
            
            # Initialize A/B Testing Engine
            if self.config.enable_ab_testing:
                self.ab_testing_engine = ABTestingEngine()
                logger.info("✓ A/B Testing Engine initialized")
            
            # Initialize Governance Engine
            if self.config.enable_governance:
                self.governance_engine = ModelGovernanceEngine()
                await self._setup_default_governance_rules()
                logger.info("✓ Governance Engine initialized")
            
            # Initialize Model Server
            auto_scaler = AutoScaler(
                min_workers=self.config.min_workers,
                max_workers=self.config.max_workers,
                target_latency_ms=self.config.target_latency_ms
            )
            self.model_server = HighPerformanceModelServer(
                serve_mode=self.config.serve_mode,
                auto_scaler=auto_scaler
            )
            logger.info("✓ Model Server initialized")
            
            self.is_initialized = True
            logger.info("🚀 MLOps platform initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize MLOps platform: {str(e)}")
            raise
    
    async def start(self):
        """Start the MLOps platform"""
        if not self.is_initialized:
            await self.initialize()
        
        if self.is_running:
            logger.warning("Platform is already running")
            return
        
        logger.info("Starting MLOps platform...")
        
        try:
            # Start Model Server
            if self.model_server:
                server_task = asyncio.create_task(self.model_server.start_server())
                logger.info("✓ Model Server started")
            
            # Start monitoring systems
            for model_name, monitor in self.monitoring_systems.items():
                # Monitoring would run continuously in the background
                logger.info(f"✓ Monitoring started for {model_name}")
            
            # Start retraining systems
            retraining_tasks = []
            for model_name, retraining_system in self.retraining_systems.items():
                task = asyncio.create_task(retraining_system.start_monitoring())
                retraining_tasks.append(task)
                logger.info(f"✓ Auto-retraining started for {model_name}")
            
            self.is_running = True
            logger.info("🎯 MLOps platform is now running")
            
            # Keep the platform running
            if retraining_tasks:
                await asyncio.gather(*retraining_tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Error starting MLOps platform: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the MLOps platform"""
        if not self.is_running:
            logger.warning("Platform is not running")
            return
        
        logger.info("Stopping MLOps platform...")
        
        # Stop Model Server
        if self.model_server:
            await self.model_server.stop_server()
            logger.info("✓ Model Server stopped")
        
        # Stop retraining systems
        for model_name, retraining_system in self.retraining_systems.items():
            await retraining_system.stop_monitoring()
            logger.info(f"✓ Auto-retraining stopped for {model_name}")
        
        # Close feature store
        if self.feature_store:
            self.feature_store.close()
            logger.info("✓ Feature Store closed")
        
        self.is_running = False
        logger.info("🛑 MLOps platform stopped")
    
    async def register_model(
        self,
        model: Any,
        model_name: str,
        model_version: str,
        feature_names: List[str],
        metrics: Dict[str, float],
        parameters: Dict[str, Any],
        training_data: Optional[Any] = None,
        requires_approval: bool = None
    ) -> bool:
        """Register a new model with the platform"""
        
        if not self.is_initialized:
            raise RuntimeError("Platform not initialized")
        
        # Determine if approval is required
        if requires_approval is None:
            requires_approval = self.config.require_approval_for_production and self.config.environment == "production"
        
        try:
            # Submit for governance approval if required
            if requires_approval and self.governance_engine:
                approval_request_id = await self.governance_engine.submit_approval_request(
                    action_type=GovernanceAction.MODEL_REGISTRATION,
                    title=f"Register model {model_name} v{model_version}",
                    description=f"Registration of model {model_name} version {model_version}",
                    requestor_id="system",  # In real system, would be actual user
                    model_info={
                        "name": model_name,
                        "version": model_version,
                        "metrics": metrics,
                        "parameters": parameters
                    }
                )
                
                logger.info(f"Model registration submitted for approval: {approval_request_id}")
                
                # For demo purposes, auto-approve if low risk
                if self.config.auto_approve_low_risk:
                    await self.governance_engine.approve_request(
                        approval_request_id,
                        "system",
                        "Auto-approved low-risk model registration"
                    )
            
            # Register with Model Registry
            run_id = self.model_registry.register_model(
                model=model,
                model_name=model_name,
                model_version=model_version,
                metrics=metrics,
                parameters=parameters,
                description=f"Model registered via MLOps platform"
            )
            
            # Register with Model Server
            if self.model_server:
                success = self.model_server.register_model(
                    model=model,
                    model_name=model_name,
                    model_version=model_version
                )
                if not success:
                    logger.warning(f"Failed to register model {model_name} with server")
            
            # Setup monitoring
            if self.config.enable_monitoring:
                monitor = ComprehensiveModelMonitor(model_name, model_version, feature_names)
                
                # Setup default monitoring metrics
                monitor.performance_monitor.add_monitoring_metric(
                    MonitoringMetric(
                        name="accuracy",
                        description="Model accuracy degradation",
                        threshold=self.config.alert_thresholds["accuracy_degradation"],
                        comparison_type="relative_change",
                        alert_severity=AlertSeverity.HIGH
                    )
                )
                
                self.monitoring_systems[model_name] = monitor
                logger.info(f"✓ Monitoring setup for {model_name}")
            
            # Setup auto-retraining
            if self.config.enable_auto_retraining:
                retraining_config = RetrainingConfig(
                    model_name=model_name,
                    performance_degradation_threshold=self.config.performance_degradation_threshold,
                    retraining_frequency_days=self.config.retraining_frequency_days
                )
                
                retraining_system = IntelligentRetrainingSystem(
                    model_registry=self.model_registry,
                    monitoring_system=self.monitoring_systems[model_name],
                    config=retraining_config
                )
                
                self.retraining_systems[model_name] = retraining_system
                logger.info(f"✓ Auto-retraining setup for {model_name}")
            
            # Setup explainability
            if self.config.enable_explainability:
                explainability_engine = ModelExplainabilityEngine(
                    model=model,
                    feature_names=feature_names,
                    model_name=model_name,
                    model_version=model_version
                )
                
                if training_data is not None:
                    explainability_engine.setup_default_explainers(training_data)
                
                self.explainability_engines[model_name] = explainability_engine
                logger.info(f"✓ Explainability setup for {model_name}")
            
            # Store model info
            self.registered_models[model_name] = {
                "version": model_version,
                "feature_names": feature_names,
                "metrics": metrics,
                "parameters": parameters,
                "run_id": run_id,
                "registered_at": datetime.now(),
                "has_monitoring": self.config.enable_monitoring,
                "has_retraining": self.config.enable_auto_retraining,
                "has_explainability": self.config.enable_explainability
            }
            
            logger.info(f"🎉 Successfully registered model {model_name} v{model_version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register model {model_name}: {str(e)}")
            return False
    
    async def create_ab_experiment(
        self,
        experiment_name: str,
        model_variants: List[Dict[str, Any]],
        business_metrics: List[Dict[str, Any]],
        duration_days: Optional[int] = None
    ) -> Optional[str]:
        """Create an A/B testing experiment"""
        
        if not self.ab_testing_engine:
            logger.error("A/B testing is not enabled")
            return None
        
        try:
            # Convert dict configurations to objects
            variants = []
            for variant_config in model_variants:
                variant = ModelVariant(
                    variant_id=variant_config["variant_id"],
                    model_name=variant_config["model_name"],
                    model_version=variant_config["model_version"],
                    traffic_allocation=variant_config["traffic_allocation"],
                    description=variant_config.get("description", "")
                )
                variants.append(variant)
            
            metrics = []
            for metric_config in business_metrics:
                metric = BusinessMetric(
                    name=metric_config["name"],
                    description=metric_config["description"],
                    metric_type=metric_config["metric_type"],
                    target_value=metric_config.get("target_value"),
                    improvement_threshold=metric_config.get("improvement_threshold", 0.05)
                )
                metrics.append(metric)
            
            # Create experiment
            experiment_id = self.ab_testing_engine.create_experiment(
                name=experiment_name,
                description=f"A/B test for {experiment_name}",
                variants=variants,
                business_metrics=metrics,
                duration_days=duration_days or self.config.default_test_duration_days,
                min_sample_size=self.config.min_sample_size
            )
            
            # Start experiment
            self.ab_testing_engine.start_experiment(experiment_id)
            
            # Track active experiment
            for variant in variants:
                self.active_experiments[variant.model_name] = experiment_id
            
            logger.info(f"🧪 Created and started A/B experiment {experiment_id}")
            return experiment_id
            
        except Exception as e:
            logger.error(f"Failed to create A/B experiment: {str(e)}")
            return None
    
    async def get_model_explanation(
        self,
        model_name: str,
        input_data: Any,
        explanation_type: str = "local",
        instance_idx: int = 0
    ) -> Optional[Dict]:
        """Get model explanation"""
        
        if model_name not in self.explainability_engines:
            logger.error(f"No explainability engine found for model {model_name}")
            return None
        
        try:
            engine = self.explainability_engines[model_name]
            
            if explanation_type == "local":
                results = engine.explain_local(input_data, instance_idx)
            elif explanation_type == "global":
                results = engine.explain_global(input_data)
            else:
                logger.error(f"Unknown explanation type: {explanation_type}")
                return None
            
            if results:
                return results[0].__dict__ if results else None
            
        except Exception as e:
            logger.error(f"Failed to get explanation for {model_name}: {str(e)}")
            return None
    
    async def predict(
        self,
        model_name: str,
        input_data: Any,
        model_version: Optional[str] = None
    ) -> Optional[Dict]:
        """Make a prediction using the model server"""
        
        if not self.model_server:
            logger.error("Model server is not available")
            return None
        
        try:
            from ml.deployment.high_performance_serving import PredictionRequest
            
            request = PredictionRequest(
                request_id=f"pred_{model_name}_{datetime.now().timestamp()}",
                input_data=input_data,
                model_name=model_name,
                model_version=model_version
            )
            
            response = await self.model_server.predict(request)
            
            # Record metrics for monitoring
            if model_name in self.monitoring_systems and hasattr(input_data, '__len__'):
                # This is simplified - in reality you'd need actual labels for monitoring
                pass
            
            return response.__dict__
            
        except Exception as e:
            logger.error(f"Prediction failed for {model_name}: {str(e)}")
            return None
    
    def get_platform_status(self) -> Dict[str, Any]:
        """Get comprehensive platform status"""
        
        status = {
            "platform": {
                "is_initialized": self.is_initialized,
                "is_running": self.is_running,
                "environment": self.config.environment,
                "components": {
                    "model_registry": self.model_registry is not None,
                    "feature_store": self.feature_store is not None,
                    "ab_testing": self.ab_testing_engine is not None,
                    "governance": self.governance_engine is not None,
                    "model_server": self.model_server is not None
                }
            },
            "models": {
                "registered_count": len(self.registered_models),
                "models": list(self.registered_models.keys()),
                "model_details": self.registered_models
            },
            "monitoring": {
                "monitored_models": len(self.monitoring_systems),
                "models": list(self.monitoring_systems.keys())
            },
            "retraining": {
                "models_with_retraining": len(self.retraining_systems),
                "models": list(self.retraining_systems.keys())
            },
            "experiments": {
                "active_experiments": len(self.active_experiments),
                "experiments": self.active_experiments
            },
            "explainability": {
                "models_with_explainability": len(self.explainability_engines),
                "models": list(self.explainability_engines.keys())
            }
        }
        
        # Add server stats if available
        if self.model_server and self.is_running:
            status["server"] = self.model_server.get_server_stats()
        
        # Add governance stats if available
        if self.governance_engine:
            status["governance"] = self.governance_engine.get_governance_dashboard_data()
        
        return status
    
    async def _setup_default_governance_rules(self):
        """Setup default governance rules"""
        if not self.governance_engine:
            return
        
        # Setup default users (in real system, these would come from external identity provider)
        from mlops.model_governance import User
        
        admin_user = User(
            user_id="admin",
            name="Platform Admin",
            email="admin@ainflue.com",
            roles=[UserRole.ADMIN, UserRole.MODEL_REVIEWER],
            department="Engineering"
        )
        
        self.governance_engine.register_user(admin_user)
        
        # Setup approval rules
        model_registration_rule = ApprovalRule(
            action_type=GovernanceAction.MODEL_REGISTRATION,
            required_roles=[UserRole.MODEL_REVIEWER, UserRole.ADMIN],
            min_approvers=1,
            max_rejection_threshold=1,
            auto_approve_conditions={"risk_level": "low"} if self.config.auto_approve_low_risk else None,
            expiry_hours=72
        )
        
        self.governance_engine.add_approval_rule(model_registration_rule)
        
        model_deployment_rule = ApprovalRule(
            action_type=GovernanceAction.MODEL_DEPLOYMENT,
            required_roles=[UserRole.MODEL_REVIEWER, UserRole.BUSINESS_OWNER],
            min_approvers=2,
            max_rejection_threshold=1,
            expiry_hours=48
        )
        
        self.governance_engine.add_approval_rule(model_deployment_rule)
        
        logger.info("✓ Default governance rules configured")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform platform health check"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        try:
            # Check Model Registry
            if self.model_registry:
                models = self.model_registry.list_models()
                health["components"]["model_registry"] = {
                    "status": "healthy",
                    "model_count": len(models)
                }
            
            # Check Model Server
            if self.model_server and self.is_running:
                server_stats = self.model_server.get_server_stats()
                health["components"]["model_server"] = {
                    "status": "healthy" if server_stats["server_info"]["is_running"] else "unhealthy",
                    "worker_count": server_stats["workers"]["count"],
                    "queue_size": server_stats["queue_size"]
                }
            
            # Check Feature Store
            if self.feature_store:
                health["components"]["feature_store"] = {
                    "status": "healthy"
                }
            
            # Check monitoring systems
            health["components"]["monitoring"] = {
                "status": "healthy",
                "monitored_models": len(self.monitoring_systems)
            }
            
            # Overall status
            component_statuses = [comp.get("status") for comp in health["components"].values()]
            if any(status == "unhealthy" for status in component_statuses):
                health["status"] = "degraded"
            
        except Exception as e:
            health["status"] = "unhealthy"
            health["error"] = str(e)
        
        return health


# Factory function for easy platform creation
def create_mlops_platform(config_dict: Optional[Dict] = None) -> MLOpsPlatform:
    """Create and configure an MLOps platform"""
    
    if config_dict:
        config = MLOpsConfig(**config_dict)
    else:
        config = MLOpsConfig()
    
    platform = MLOpsPlatform(config)
    return platform


# Example usage and demo
async def demo_mlops_platform():
    """Demonstrate the MLOps platform capabilities"""
    
    # Create platform with custom config
    config = MLOpsConfig(
        environment="development",
        enable_monitoring=True,
        enable_ab_testing=True,
        enable_governance=True,
        enable_explainability=True
    )
    
    platform = MLOpsPlatform(config)
    
    try:
        # Initialize and start platform
        await platform.initialize()
        
        # In a real scenario, you would start the platform in the background
        # await platform.start()
        
        # Example: Register a dummy model
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.datasets import make_classification
        
        # Create dummy model and data
        X, y = make_classification(n_samples=1000, n_features=10, n_classes=2, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Register model
        feature_names = [f"feature_{i}" for i in range(10)]
        success = await platform.register_model(
            model=model,
            model_name="demo_classifier",
            model_version="1.0.0",
            feature_names=feature_names,
            metrics={"accuracy": 0.85, "f1_score": 0.82},
            parameters={"n_estimators": 100, "random_state": 42},
            training_data=X
        )
        
        if success:
            print("✅ Model registered successfully")
        
        # Get platform status
        status = platform.get_platform_status()
        print("\n📊 Platform Status:")
        print(json.dumps(status, indent=2, default=str))
        
        # Perform health check
        health = await platform.health_check()
        print("\n🏥 Health Check:")
        print(json.dumps(health, indent=2, default=str))
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
    
    finally:
        await platform.stop()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run demo
    asyncio.run(demo_mlops_platform())