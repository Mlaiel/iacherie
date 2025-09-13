"""
Automated Model Retraining with Intelligent Triggers
Implements intelligent retraining system based on performance and drift detection
"""

import asyncio
import time
import warnings
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from pathlib import Path

# Optional dependencies
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    warnings.warn("schedule not available. Install with: pip install schedule")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    warnings.warn("pandas not available. Some features will be limited.")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    warnings.warn("numpy not available. Some features will be limited.")

# Optional local imports
try:
    from mlops.model_versioning.model_registry import ModelRegistry
    MODEL_REGISTRY_AVAILABLE = True
except ImportError:
    MODEL_REGISTRY_AVAILABLE = False
    warnings.warn("ModelRegistry not available")

try:
    from mlops.model_monitoring.performance_monitor import ComprehensiveModelMonitor, AlertSeverity, DriftType
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    warnings.warn("ModelMonitoring not available")

# Add mock implementations for missing dependencies
if PANDAS_AVAILABLE:
    from pandas import DataFrame
else:
    from typing import Any
    DataFrame = Any  # Fallback when pandas not available
    # Create mock pandas for basic compatibility
    class MockPandas:
        DataFrame = Any
        @staticmethod
        def DataFrame(*args, **kwargs):
            return {}
    pd = MockPandas()

logger = logging.getLogger(__name__)


class RetrainingTrigger(Enum):
    """Types of retraining triggers"""
    SCHEDULED = "scheduled"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    MANUAL = "manual"
    DATA_VOLUME = "data_volume"
    BUSINESS_RULE = "business_rule"


class RetrainingStatus(Enum):
    """Retraining job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class RetrainingJob:
    """Represents a retraining job"""
    job_id: str
    model_name: str
    trigger_type: RetrainingTrigger
    trigger_reason: str
    status: RetrainingStatus = RetrainingStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    training_data_size: Optional[int] = None
    validation_metrics: Optional[Dict[str, float]] = None
    new_model_version: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrainingConfig:
    """Configuration for automated retraining"""
    model_name: str
    
    # Performance thresholds
    performance_degradation_threshold: float = 0.05  # 5% degradation
    min_samples_for_retraining: int = 1000
    
    # Schedule configuration
    scheduled_retraining_enabled: bool = True
    retraining_frequency_days: int = 30
    retraining_time: str = "02:00"  # 2 AM
    
    # Drift thresholds
    drift_detection_enabled: bool = True
    drift_threshold: float = 0.1
    consecutive_drift_alerts: int = 3
    
    # Data volume triggers
    data_volume_trigger_enabled: bool = True
    new_data_threshold: int = 10000
    
    # Training configuration
    training_pipeline: Optional[str] = None
    hyperparameter_optimization: bool = True
    cross_validation_folds: int = 5
    early_stopping_patience: int = 10
    
    # Approval workflow
    require_approval: bool = True
    auto_deploy_threshold: float = 0.02  # Auto-deploy if 2% improvement
    
    # Resource limits
    max_training_time_minutes: int = 240  # 4 hours
    max_concurrent_jobs: int = 2


class IntelligentRetrainingSystem:
    """Intelligent automated retraining system"""
    
    def __init__(
        self,
        model_registry: ModelRegistry,
        monitoring_system: ComprehensiveModelMonitor,
        config: RetrainingConfig
    ):
        self.model_registry = model_registry
        self.monitoring_system = monitoring_system
        self.config = config
        self.retraining_jobs: Dict[str, RetrainingJob] = {}
        self.training_data_cache: Dict[str, DataFrame] = {}
        self.running_jobs: Dict[str, asyncio.Task] = {}
        self.scheduler_running = False
        
        # Callbacks for training pipeline
        self.training_pipeline_callback: Optional[Callable] = None
        self.data_loader_callback: Optional[Callable] = None
        self.model_evaluator_callback: Optional[Callable] = None
        
    def register_training_pipeline(self, callback: Callable):
        """Register training pipeline callback"""
        self.training_pipeline_callback = callback
        logger.info("Training pipeline callback registered")
    
    def register_data_loader(self, callback: Callable):
        """Register data loader callback"""
        self.data_loader_callback = callback
        logger.info("Data loader callback registered")
    
    def register_model_evaluator(self, callback: Callable):
        """Register model evaluator callback"""
        self.model_evaluator_callback = callback
        logger.info("Model evaluator callback registered")
    
    async def start_monitoring(self):
        """Start the monitoring and retraining system"""
        logger.info(f"Starting intelligent retraining system for {self.config.model_name}")
        
        # Setup scheduled retraining
        if self.config.scheduled_retraining_enabled:
            schedule.every(self.config.retraining_frequency_days).days.at(
                self.config.retraining_time
            ).do(self._trigger_scheduled_retraining)
        
        self.scheduler_running = True
        
        # Start monitoring loop
        while self.scheduler_running:
            try:
                # Run scheduled jobs
                schedule.run_pending()
                
                # Check for trigger conditions
                await self._check_retraining_triggers()
                
                # Clean up completed jobs
                self._cleanup_jobs()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(60)
    
    async def stop_monitoring(self):
        """Stop the monitoring system"""
        self.scheduler_running = False
        
        # Cancel running jobs
        for job_id, task in self.running_jobs.items():
            task.cancel()
            logger.info(f"Cancelled retraining job {job_id}")
        
        logger.info("Stopped intelligent retraining system")
    
    async def trigger_retraining(
        self,
        trigger_type: RetrainingTrigger,
        reason: str,
        force: bool = False,
        metadata: Optional[Dict] = None
    ) -> str:
        """Trigger a retraining job"""
        
        # Check if retraining is needed
        if not force and not self._should_trigger_retraining(trigger_type):
            logger.info(f"Retraining not triggered: {reason}")
            return None
        
        # Check concurrent job limits
        running_count = len([j for j in self.retraining_jobs.values() 
                           if j.status == RetrainingStatus.RUNNING])
        
        if running_count >= self.config.max_concurrent_jobs:
            logger.warning(f"Maximum concurrent jobs ({self.config.max_concurrent_jobs}) reached")
            return None
        
        # Create retraining job
        job_id = f"retrain_{self.config.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        job = RetrainingJob(
            job_id=job_id,
            model_name=self.config.model_name,
            trigger_type=trigger_type,
            trigger_reason=reason,
            metadata=metadata or {}
        )
        
        self.retraining_jobs[job_id] = job
        
        # Start retraining task
        task = asyncio.create_task(self._execute_retraining_job(job))
        self.running_jobs[job_id] = task
        
        logger.info(f"Triggered retraining job {job_id}: {reason}")
        return job_id
    
    async def _execute_retraining_job(self, job: RetrainingJob):
        """Execute a retraining job"""
        try:
            job.status = RetrainingStatus.RUNNING
            job.started_at = datetime.now()
            
            logger.info(f"Starting retraining job {job.job_id}")
            
            # Load training data
            training_data = await self._load_training_data(job)
            if training_data is None or len(training_data) < self.config.min_samples_for_retraining:
                raise ValueError(f"Insufficient training data: {len(training_data) if training_data is not None else 0}")
            
            job.training_data_size = len(training_data)
            
            # Train new model
            new_model, validation_metrics = await self._train_model(job, training_data)
            
            job.validation_metrics = validation_metrics
            
            # Register new model version
            new_version = await self._register_new_model(job, new_model, validation_metrics)
            job.new_model_version = new_version
            
            # Evaluate model performance
            should_deploy = await self._evaluate_new_model(job, new_model, validation_metrics)
            
            if should_deploy:
                if self.config.require_approval and not self._meets_auto_deploy_criteria(validation_metrics):
                    logger.info(f"Model {new_version} requires manual approval for deployment")
                    job.metadata["requires_approval"] = True
                else:
                    # Auto-deploy
                    await self._deploy_model(job, new_version)
                    job.metadata["auto_deployed"] = True
            
            job.status = RetrainingStatus.COMPLETED
            job.completed_at = datetime.now()
            
            logger.info(f"Completed retraining job {job.job_id}")
            
        except Exception as e:
            job.status = RetrainingStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
            
            logger.error(f"Failed retraining job {job.job_id}: {str(e)}")
        
        finally:
            # Clean up running job reference
            if job.job_id in self.running_jobs:
                del self.running_jobs[job.job_id]
    
    async def _check_retraining_triggers(self):
        """Check for automatic retraining triggers"""
        
        # Check performance degradation
        if await self._check_performance_degradation():
            await self.trigger_retraining(
                RetrainingTrigger.PERFORMANCE_DEGRADATION,
                "Model performance degradation detected"
            )
        
        # Check data drift
        if self.config.drift_detection_enabled and await self._check_data_drift():
            await self.trigger_retraining(
                RetrainingTrigger.DATA_DRIFT,
                "Data drift detected"
            )
        
        # Check data volume
        if self.config.data_volume_trigger_enabled and await self._check_data_volume():
            await self.trigger_retraining(
                RetrainingTrigger.DATA_VOLUME,
                "Sufficient new data available"
            )
    
    async def _check_performance_degradation(self) -> bool:
        """Check if model performance has degraded"""
        try:
            performance_trends = self.monitoring_system.performance_monitor.get_performance_trends()
            
            # Check key metrics for degradation
            for metric_name in ["accuracy", "f1_score"]:
                if metric_name in performance_trends:
                    trend = performance_trends[metric_name]
                    current_value = trend.get("current_value", 0)
                    
                    # Compare with baseline
                    baseline_metrics = self.monitoring_system.performance_monitor.baseline_metrics
                    if baseline_metrics and metric_name in baseline_metrics:
                        baseline_value = baseline_metrics[metric_name]
                        degradation = (baseline_value - current_value) / baseline_value
                        
                        if degradation > self.config.performance_degradation_threshold:
                            logger.warning(f"Performance degradation detected in {metric_name}: {degradation:.3f}")
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking performance degradation: {str(e)}")
            return False
    
    async def _check_data_drift(self) -> bool:
        """Check for data drift"""
        try:
            drift_summary = self.monitoring_system.data_drift_monitor.get_drift_summary(days_back=7)
            
            if "drift_detected_count" in drift_summary:
                drift_rate = drift_summary["drift_detected_count"] / max(drift_summary["total_checks"], 1)
                
                if drift_rate > self.config.drift_threshold:
                    logger.warning(f"High drift rate detected: {drift_rate:.3f}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking data drift: {str(e)}")
            return False
    
    async def _check_data_volume(self) -> bool:
        """Check if sufficient new data is available"""
        try:
            # This would typically check your data pipeline
            # For now, simulate check
            if self.data_loader_callback:
                new_data_count = await self.data_loader_callback(count_only=True)
                return new_data_count >= self.config.new_data_threshold
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking data volume: {str(e)}")
            return False
    
    async def _load_training_data(self, job: RetrainingJob) -> Optional[DataFrame]:
        """Load training data for retraining"""
        try:
            if self.data_loader_callback:
                training_data = await self.data_loader_callback(
                    model_name=job.model_name,
                    min_samples=self.config.min_samples_for_retraining
                )
                return training_data
            else:
                logger.error("No data loader callback registered")
                return None
                
        except Exception as e:
            logger.error(f"Error loading training data: {str(e)}")
            return None
    
    async def _train_model(self, job: RetrainingJob, training_data: DataFrame) -> tuple:
        """Train a new model"""
        try:
            if self.training_pipeline_callback:
                model, metrics = await self.training_pipeline_callback(
                    training_data=training_data,
                    model_name=job.model_name,
                    config={
                        "hyperparameter_optimization": self.config.hyperparameter_optimization,
                        "cross_validation_folds": self.config.cross_validation_folds,
                        "early_stopping_patience": self.config.early_stopping_patience
                    }
                )
                return model, metrics
            else:
                logger.error("No training pipeline callback registered")
                return None, None
                
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
    
    async def _register_new_model(self, job: RetrainingJob, model: Any, metrics: Dict) -> str:
        """Register the new model version"""
        try:
            new_version = f"auto_retrain_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            run_id = self.model_registry.register_model(
                model=model,
                model_name=job.model_name,
                model_version=new_version,
                metrics=metrics,
                parameters={
                    "retraining_trigger": job.trigger_type.value,
                    "trigger_reason": job.trigger_reason,
                    "training_data_size": job.training_data_size,
                    "auto_retrained": True
                },
                tags={
                    "retraining_job_id": job.job_id,
                    "trigger_type": job.trigger_type.value,
                    "automated": "true"
                },
                description=f"Automatically retrained model - {job.trigger_reason}"
            )
            
            logger.info(f"Registered new model version {new_version} with run_id {run_id}")
            return new_version
            
        except Exception as e:
            logger.error(f"Error registering new model: {str(e)}")
            raise
    
    async def _evaluate_new_model(self, job: RetrainingJob, model: Any, validation_metrics: Dict) -> bool:
        """Evaluate if the new model should be deployed"""
        try:
            if self.model_evaluator_callback:
                evaluation_result = await self.model_evaluator_callback(
                    model=model,
                    model_name=job.model_name,
                    validation_metrics=validation_metrics
                )
                return evaluation_result.get("should_deploy", False)
            
            # Default evaluation: check if metrics improved
            baseline_metrics = self.monitoring_system.performance_monitor.baseline_metrics
            if baseline_metrics:
                for metric_name in ["accuracy", "f1_score"]:
                    if metric_name in validation_metrics and metric_name in baseline_metrics:
                        improvement = (validation_metrics[metric_name] - baseline_metrics[metric_name]) / baseline_metrics[metric_name]
                        if improvement > 0.01:  # 1% improvement
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating new model: {str(e)}")
            return False
    
    def _meets_auto_deploy_criteria(self, validation_metrics: Dict) -> bool:
        """Check if model meets auto-deployment criteria"""
        baseline_metrics = self.monitoring_system.performance_monitor.baseline_metrics
        if not baseline_metrics:
            return False
        
        for metric_name in ["accuracy", "f1_score"]:
            if metric_name in validation_metrics and metric_name in baseline_metrics:
                improvement = (validation_metrics[metric_name] - baseline_metrics[metric_name]) / baseline_metrics[metric_name]
                if improvement >= self.config.auto_deploy_threshold:
                    return True
        
        return False
    
    async def _deploy_model(self, job: RetrainingJob, model_version: str):
        """Deploy the new model version"""
        try:
            # Transition to staging first
            self.model_registry.transition_model_stage(job.model_name, model_version, "Staging")
            
            # If auto-deploy criteria met, transition to production
            if job.metadata.get("auto_deployed", False):
                self.model_registry.transition_model_stage(job.model_name, model_version, "Production")
                logger.info(f"Auto-deployed model {job.model_name} v{model_version} to production")
            else:
                logger.info(f"Deployed model {job.model_name} v{model_version} to staging")
                
        except Exception as e:
            logger.error(f"Error deploying model: {str(e)}")
            raise
    
    def _should_trigger_retraining(self, trigger_type: RetrainingTrigger) -> bool:
        """Check if retraining should be triggered based on recent history"""
        
        # Check if there's already a recent retraining job
        recent_jobs = [
            job for job in self.retraining_jobs.values()
            if job.trigger_type == trigger_type and
            (datetime.now() - job.created_at).hours < 24 and
            job.status in [RetrainingStatus.RUNNING, RetrainingStatus.COMPLETED]
        ]
        
        if recent_jobs:
            logger.info(f"Recent {trigger_type.value} retraining found, skipping")
            return False
        
        return True
    
    def _trigger_scheduled_retraining(self):
        """Trigger scheduled retraining"""
        asyncio.create_task(self.trigger_retraining(
            RetrainingTrigger.SCHEDULED,
            "Scheduled retraining"
        ))
    
    def _cleanup_jobs(self):
        """Clean up old completed jobs"""
        cutoff_time = datetime.now() - timedelta(days=7)  # Keep jobs for 7 days
        
        jobs_to_remove = [
            job_id for job_id, job in self.retraining_jobs.items()
            if job.completed_at and job.completed_at < cutoff_time
        ]
        
        for job_id in jobs_to_remove:
            del self.retraining_jobs[job_id]
            logger.debug(f"Cleaned up old job {job_id}")
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get status of a retraining job"""
        if job_id not in self.retraining_jobs:
            return None
        
        job = self.retraining_jobs[job_id]
        return {
            "job_id": job.job_id,
            "model_name": job.model_name,
            "status": job.status.value,
            "trigger_type": job.trigger_type.value,
            "trigger_reason": job.trigger_reason,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "training_data_size": job.training_data_size,
            "validation_metrics": job.validation_metrics,
            "new_model_version": job.new_model_version,
            "error_message": job.error_message,
            "metadata": job.metadata
        }
    
    def get_all_jobs(self, limit: int = 50) -> List[Dict]:
        """Get all retraining jobs"""
        jobs = sorted(
            self.retraining_jobs.values(),
            key=lambda x: x.created_at,
            reverse=True
        )[:limit]
        
        return [self.get_job_status(job.job_id) for job in jobs]
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running retraining job"""
        if job_id not in self.retraining_jobs:
            return False
        
        job = self.retraining_jobs[job_id]
        
        if job.status == RetrainingStatus.RUNNING:
            if job_id in self.running_jobs:
                self.running_jobs[job_id].cancel()
                del self.running_jobs[job_id]
            
            job.status = RetrainingStatus.CANCELLED
            job.completed_at = datetime.now()
            logger.info(f"Cancelled retraining job {job_id}")
            return True
        
        return False


class RetrainingScheduler:
    """Scheduler for managing multiple model retraining systems"""
    
    def __init__(self):
        self.retraining_systems: Dict[str, IntelligentRetrainingSystem] = {}
        self.global_config = {
            "max_concurrent_retraining": 3,
            "resource_monitoring": True,
            "notification_enabled": True
        }
    
    def register_model(
        self,
        model_name: str,
        retraining_system: IntelligentRetrainingSystem
    ):
        """Register a model for automated retraining"""
        self.retraining_systems[model_name] = retraining_system
        logger.info(f"Registered model {model_name} for automated retraining")
    
    async def start_all(self):
        """Start all retraining systems"""
        tasks = []
        for model_name, system in self.retraining_systems.items():
            task = asyncio.create_task(system.start_monitoring())
            tasks.append(task)
            logger.info(f"Started retraining system for {model_name}")
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in retraining scheduler: {str(e)}")
    
    async def stop_all(self):
        """Stop all retraining systems"""
        for model_name, system in self.retraining_systems.items():
            await system.stop_monitoring()
            logger.info(f"Stopped retraining system for {model_name}")
    
    def get_global_status(self) -> Dict:
        """Get global status of all retraining systems"""
        status = {
            "total_models": len(self.retraining_systems),
            "active_jobs": 0,
            "completed_jobs_today": 0,
            "failed_jobs_today": 0,
            "model_statuses": {}
        }
        
        today = datetime.now().date()
        
        for model_name, system in self.retraining_systems.items():
            jobs = system.get_all_jobs()
            
            active_jobs = len([j for j in jobs if j["status"] == "running"])
            completed_today = len([j for j in jobs 
                                 if j["status"] == "completed" and 
                                 datetime.fromisoformat(j["created_at"]).date() == today])
            failed_today = len([j for j in jobs 
                              if j["status"] == "failed" and 
                              datetime.fromisoformat(j["created_at"]).date() == today])
            
            status["active_jobs"] += active_jobs
            status["completed_jobs_today"] += completed_today
            status["failed_jobs_today"] += failed_today
            
            status["model_statuses"][model_name] = {
                "active_jobs": active_jobs,
                "completed_today": completed_today,
                "failed_today": failed_today,
                "last_retraining": jobs[0]["created_at"] if jobs else None
            }
        
        return status