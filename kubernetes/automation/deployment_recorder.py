"""Deployment Recorder - Deployment Automation

Advanced deployment tracking and audit system for the IA Influencer Agent platform,
providing comprehensive deployment history, audit trails, and
analytics for deployment automation workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field, asdict
import json
import hashlib
import uuid
from pathlib import Path
import gzip
import pickle

from ..core.base import BaseComponent
from ..database.audit_manager import AuditManager
from ..storage.persistent_storage import PersistentStorage
from ..monitoring.metrics_collector import MetricsCollector


class DeploymentStatus(Enum):
    """Deployment status values"""    PENDING = "pending"
    INITIALIZING = "initializing"
    IN_PROGRESS = "in_progress"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


class DeploymentStrategy(Enum):
    """Deployment strategy types"""    ROLLING_UPDATE = "rolling_update"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"


class RecordType(Enum):
    """Record types for different aspects of deployment"""    DEPLOYMENT = "deployment"
    STEP = "step"
    HEALTH_CHECK = "health_check"
    ROLLBACK = "rollback"
    SCALING = "scaling"
    CONFIGURATION = "configuration"
    NOTIFICATION = "notification"
    METRIC = "metric"


@dataclass
class DeploymentStep:
    """Individual deployment step record"""    step_id: str
    step_name: str
    step_type: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    status: str = "pending"
    output: str = ""
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    checkpoints: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DeploymentEnvironment:
    """Deployment environment information"""    name: str
    namespace: str
    cluster: str
    region: str
    cloud_provider: str
    configuration_hash: str
    resources: Dict[str, Any] = field(default_factory=dict)
    network_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeploymentArtifact:
    """Deployment artifact information"""    artifact_id: str
    artifact_type: str  # docker_image, helm_chart, config_file, etc.
    name: str
    version: str
    checksum: str
    size_bytes: int
    location: str
    build_info: Dict[str, Any] = field(default_factory=dict)
    security_scan: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeploymentRecord:
    """Comprehensive deployment record"""    deployment_id: str
    workflow_id: str
    environment: DeploymentEnvironment
    strategy: DeploymentStrategy
    status: DeploymentStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Deployment details
    services: List[str] = field(default_factory=list)
    artifacts: List[DeploymentArtifact] = field(default_factory=list)
    steps: List[DeploymentStep] = field(default_factory=list)
    
    # User and trigger information
    initiated_by: str = "system"
    trigger_type: str = "manual"  # manual, scheduled, webhook, etc.
    trigger_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Change information
    changes: List[Dict[str, Any]] = field(default_factory=list)
    rollback_point_id: Optional[str] = None
    previous_deployment_id: Optional[str] = None
    
    # Quality and performance metrics
    success_metrics: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    health_checks: List[Dict[str, Any]] = field(default_factory=list)
    
    # Additional metadata
    tags: Dict[str, str] = field(default_factory=dict)
    notes: str = ""
    retention_policy: str = "default"


@dataclass
class DeploymentAnalytics:
    """Deployment analytics data"""    time_period: str
    total_deployments: int
    successful_deployments: int
    failed_deployments: int
    average_duration: float
    success_rate: float
    strategy_breakdown: Dict[str, int]
    service_breakdown: Dict[str, int]
    failure_reasons: Dict[str, int]
    trends: Dict[str, List[float]]


class DeploymentRecorder(BaseComponent):
    """    Enterprise-grade deployment recording and audit system.
    
    Provides comprehensive deployment tracking, audit trails, analytics,
    and historical data management for deployment automation workflows
    in the IA Influencer Agent platform.
    """    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.audit_manager = AuditManager(config.get('audit', {}))
        self.storage = PersistentStorage(config.get('storage', {}))
        self.metrics_collector = MetricsCollector(config.get('metrics', {}))
        
        # Recording state
        self.active_deployments: Dict[str, DeploymentRecord] = {}
        self.deployment_cache: Dict[str, DeploymentRecord] = {}
        
        # Configuration
        self.max_cache_size = config.get('max_cache_size', 1000)
        self.retention_days = config.get('retention_days', 90)
        self.compression_enabled = config.get('compression_enabled', True)
        self.real_time_analytics = config.get('real_time_analytics', True)
        
        # Storage paths
        self.base_storage_path = Path(config.get('storage_path', '/data/deployment-records'))
        self.base_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Analytics cache
        self.analytics_cache: Dict[str, DeploymentAnalytics] = {}
        self.analytics_cache_ttl = timedelta(minutes=15)
        self.last_analytics_update = datetime.utcnow()
        
        # Initialize storage structure
        asyncio.create_task(self._initialize_storage())

    async def _initialize_storage(self) -> None:
        """Initialize storage structure and load recent records"""        
        try:
            # Create storage directories
            (self.base_storage_path / "deployments").mkdir(exist_ok=True)
            (self.base_storage_path / "analytics").mkdir(exist_ok=True)
            (self.base_storage_path / "exports").mkdir(exist_ok=True)
            (self.base_storage_path / "archive").mkdir(exist_ok=True)
            
            # Load recent deployment records into cache
            await self._load_recent_records()
            
            # Start background tasks
            asyncio.create_task(self._periodic_storage_sync())
            asyncio.create_task(self._periodic_analytics_update())
            asyncio.create_task(self._periodic_cleanup())
            
            self.logger.info("Deployment recorder initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize deployment recorder: {str(e)}", exc_info=True)

    async def start_deployment_recording(
        self,
        workflow_id: str,
        environment: DeploymentEnvironment,
        strategy: DeploymentStrategy,
        services: List[str],
        context: Dict[str, Any]
    ) -> str:
        """        Start recording a new deployment.
        
        Args:
            workflow_id: Workflow identifier
            environment: Deployment environment
            strategy: Deployment strategy
            services: List of services being deployed
            context: Additional deployment context
            
        Returns:
            Deployment record ID
        """        
        deployment_id = f"deploy-{uuid.uuid4().hex[:12]}"
        
        # Create deployment record
        deployment_record = DeploymentRecord(
            deployment_id=deployment_id,
            workflow_id=workflow_id,
            environment=environment,
            strategy=strategy,
            status=DeploymentStatus.PENDING,
            created_at=datetime.utcnow(),
            services=services,
            initiated_by=context.get('initiated_by', 'system'),
            trigger_type=context.get('trigger_type', 'manual'),
            trigger_metadata=context.get('trigger_metadata', {}),
            tags=context.get('tags', {}),
            notes=context.get('notes', ''),
            retention_policy=context.get('retention_policy', 'default')
        )
        
        # Add artifacts if provided
        if 'artifacts' in context:
            deployment_record.artifacts = [
                DeploymentArtifact(**artifact) for artifact in context['artifacts']
            ]
        
        # Store in active deployments
        self.active_deployments[deployment_id] = deployment_record
        
        # Create audit trail entry
        await self.audit_manager.log_event(
            event_type="deployment_started",
            resource_id=deployment_id,
            user_id=deployment_record.initiated_by,
            details={
                'workflow_id': workflow_id,
                'environment': environment.name,
                'strategy': strategy.value,
                'services': services
            }
        )
        
        self.logger.info(f"Started deployment recording: {deployment_id}")
        
        return deployment_id

    async def update_deployment_status(
        self,
        deployment_id: str,
        status: DeploymentStatus,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update deployment status"""        
        if deployment_id not in self.active_deployments:
            raise ValueError(f"Deployment record not found: {deployment_id}")
        
        deployment_record = self.active_deployments[deployment_id]
        old_status = deployment_record.status
        deployment_record.status = status
        
        # Update timing
        if status == DeploymentStatus.IN_PROGRESS and not deployment_record.started_at:
            deployment_record.started_at = datetime.utcnow()
        elif status in [DeploymentStatus.COMPLETED, DeploymentStatus.FAILED, DeploymentStatus.CANCELLED]:
            deployment_record.completed_at = datetime.utcnow()
            if deployment_record.started_at:
                deployment_record.duration_seconds = (
                    deployment_record.completed_at - deployment_record.started_at
                ).total_seconds()
        
        # Add metadata
        if metadata:
            deployment_record.trigger_metadata.update(metadata)
        
        # Log status change
        await self.audit_manager.log_event(
            event_type="deployment_status_changed",
            resource_id=deployment_id,
            user_id=deployment_record.initiated_by,
            details={
                'old_status': old_status.value,
                'new_status': status.value,
                'metadata': metadata or {}
            }
        )
        
        self.logger.info(f"Updated deployment {deployment_id} status: {old_status.value} -> {status.value}")

    async def record_deployment_step(
        self,
        deployment_id: str,
        step_name: str,
        step_type: str,
        status: str = "started",
        output: str = "",
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record a deployment step"""        
        if deployment_id not in self.active_deployments:
            raise ValueError(f"Deployment record not found: {deployment_id}")
        
        step_id = f"step-{uuid.uuid4().hex[:8]}"
        
        deployment_step = DeploymentStep(
            step_id=step_id,
            step_name=step_name,
            step_type=step_type,
            started_at=datetime.utcnow(),
            status=status,
            output=output,
            error_message=error_message,
            metadata=metadata or {}
        )
        
        # Add step to deployment record
        deployment_record = self.active_deployments[deployment_id]
        
        # Find existing step or add new one
        existing_step_index = None
        for i, step in enumerate(deployment_record.steps):
            if step.step_name == step_name:
                existing_step_index = i
                break
        
        if existing_step_index is not None:
            # Update existing step
            existing_step = deployment_record.steps[existing_step_index]
            existing_step.status = status
            existing_step.output = output
            existing_step.error_message = error_message
            if status in ["completed", "failed"]:
                existing_step.completed_at = datetime.utcnow()
                existing_step.duration_seconds = (
                    existing_step.completed_at - existing_step.started_at
                ).total_seconds()
            if metadata:
                existing_step.metadata.update(metadata)
        else:
            # Add new step
            deployment_record.steps.append(deployment_step)
        
        # Log step event
        await self.audit_manager.log_event(
            event_type="deployment_step",
            resource_id=deployment_id,
            user_id=deployment_record.initiated_by,
            details={
                'step_id': step_id,
                'step_name': step_name,
                'step_type': step_type,
                'status': status,
                'error_message': error_message
            }
        )
        
        return step_id

    async def record_health_check(
        self,
        deployment_id: str,
        check_name: str,
        check_type: str,
        status: str,
        details: Dict[str, Any]
    ) -> None:
        """Record a health check result"""        
        if deployment_id not in self.active_deployments:
            raise ValueError(f"Deployment record not found: {deployment_id}")
        
        health_check = {
            'check_id': f"health-{uuid.uuid4().hex[:8]}",
            'check_name': check_name,
            'check_type': check_type,
            'status': status,
            'timestamp': datetime.utcnow(),
            'details': details
        }
        
        deployment_record = self.active_deployments[deployment_id]
        deployment_record.health_checks.append(health_check)
        
        # Log health check
        await self.audit_manager.log_event(
            event_type="health_check",
            resource_id=deployment_id,
            user_id=deployment_record.initiated_by,
            details={
                'check_name': check_name,
                'check_type': check_type,
                'status': status,
                'details': details
            }
        )

    async def record_performance_metrics(
        self,
        deployment_id: str,
        metrics: Dict[str, Any]
    ) -> None:
        """Record deployment performance metrics"""        
        if deployment_id not in self.active_deployments:
            raise ValueError(f"Deployment record not found: {deployment_id}")
        
        deployment_record = self.active_deployments[deployment_id]
        deployment_record.performance_metrics.update(metrics)
        
        # Also collect real-time metrics if enabled
        if self.real_time_analytics:
            await self.metrics_collector.record_deployment_metrics(
                deployment_id, metrics
            )

    async def record_deployment_changes(
        self,
        deployment_id: str,
        changes: List[Dict[str, Any]]
    ) -> None:
        """Record what changed in this deployment"""        
        if deployment_id not in self.active_deployments:
            raise ValueError(f"Deployment record not found: {deployment_id}")
        
        deployment_record = self.active_deployments[deployment_id]
        deployment_record.changes.extend(changes)
        
        # Log changes
        await self.audit_manager.log_event(
            event_type="deployment_changes",
            resource_id=deployment_id,
            user_id=deployment_record.initiated_by,
            details={'changes': changes}
        )

    async def complete_deployment_recording(
        self,
        deployment_id: str,
        final_status: DeploymentStatus,
        success_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Complete deployment recording and move to persistent storage.
        
        Args:
            deployment_id: Deployment identifier
            final_status: Final deployment status
            success_metrics: Success metrics and KPIs
            
        Returns:
            Deployment summary
        """        
        if deployment_id not in self.active_deployments:
            raise ValueError(f"Deployment record not found: {deployment_id}")
        
        deployment_record = self.active_deployments[deployment_id]
        
        # Update final status and timing
        deployment_record.status = final_status
        deployment_record.completed_at = datetime.utcnow()
        
        if deployment_record.started_at:
            deployment_record.duration_seconds = (
                deployment_record.completed_at - deployment_record.started_at
            ).total_seconds()
        
        # Add success metrics
        if success_metrics:
            deployment_record.success_metrics.update(success_metrics)
        
        # Calculate deployment summary
        summary = self._calculate_deployment_summary(deployment_record)
        
        # Store in persistent storage
        await self._store_deployment_record(deployment_record)
        
        # Move to cache and remove from active
        self.deployment_cache[deployment_id] = deployment_record
        del self.active_deployments[deployment_id]
        
        # Update analytics
        if self.real_time_analytics:
            await self._update_real_time_analytics(deployment_record)
        
        # Create final audit entry
        await self.audit_manager.log_event(
            event_type="deployment_completed",
            resource_id=deployment_id,
            user_id=deployment_record.initiated_by,
            details={
                'final_status': final_status.value,
                'duration_seconds': deployment_record.duration_seconds,
                'summary': summary
            }
        )
        
        self.logger.info(f"Completed deployment recording: {deployment_id}")
        
        return summary

    def _calculate_deployment_summary(self, deployment_record: DeploymentRecord) -> Dict[str, Any]:
        """Calculate deployment summary statistics"""        
        total_steps = len(deployment_record.steps)
        completed_steps = len([step for step in deployment_record.steps if step.status == "completed"])
        failed_steps = len([step for step in deployment_record.steps if step.status == "failed"])
        
        total_health_checks = len(deployment_record.health_checks)
        passed_health_checks = len([hc for hc in deployment_record.health_checks if hc['status'] == 'passed'])
        
        return {
            'deployment_id': deployment_record.deployment_id,
            'workflow_id': deployment_record.workflow_id,
            'environment': deployment_record.environment.name,
            'strategy': deployment_record.strategy.value,
            'status': deployment_record.status.value,
            'duration_seconds': deployment_record.duration_seconds,
            'services_count': len(deployment_record.services),
            'steps_summary': {
                'total': total_steps,
                'completed': completed_steps,
                'failed': failed_steps,
                'success_rate': (completed_steps / total_steps * 100) if total_steps > 0 else 0
            },
            'health_checks_summary': {
                'total': total_health_checks,
                'passed': passed_health_checks,
                'success_rate': (passed_health_checks / total_health_checks * 100) if total_health_checks > 0 else 0
            },
            'artifacts_count': len(deployment_record.artifacts),
            'changes_count': len(deployment_record.changes)
        }

    async def _store_deployment_record(self, deployment_record: DeploymentRecord) -> None:
        """Store deployment record to persistent storage"""        
        try:
            # Create storage path based on date
            date_path = deployment_record.created_at.strftime('%Y/%m/%d')
            storage_path = self.base_storage_path / "deployments" / date_path
            storage_path.mkdir(parents=True, exist_ok=True)
            
            # Create filename
            filename = f"{deployment_record.deployment_id}.json"
            if self.compression_enabled:
                filename += ".gz"
            
            file_path = storage_path / filename
            
            # Serialize record
            record_data = asdict(deployment_record)
            
            # Convert datetime objects to ISO format
            record_data = self._serialize_datetimes(record_data)
            
            # Store to file
            if self.compression_enabled:
                with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                    json.dump(record_data, f, indent=2)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(record_data, f, indent=2)
            
            # Also store in database for querying
            await self.storage.store_deployment_record(deployment_record)
            
            self.logger.info(f"Stored deployment record: {deployment_record.deployment_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to store deployment record: {str(e)}", exc_info=True)

    def _serialize_datetimes(self, data: Any) -> Any:
        """Recursively serialize datetime objects"""        
        if isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, dict):
            return {key: self._serialize_datetimes(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._serialize_datetimes(item) for item in data]
        else:
            return data

    async def _load_recent_records(self) -> None:
        """Load recent deployment records into cache"""        
        try:
            # Load records from the last 7 days
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            recent_records = await self.storage.get_deployment_records_since(cutoff_date)
            
            for record in recent_records:
                self.deployment_cache[record.deployment_id] = record
            
            # Limit cache size
            if len(self.deployment_cache) > self.max_cache_size:
                # Keep only the most recent records
                sorted_records = sorted(
                    self.deployment_cache.items(),
                    key=lambda x: x[1].created_at,
                    reverse=True
                )
                
                self.deployment_cache = dict(sorted_records[:self.max_cache_size])
            
            self.logger.info(f"Loaded {len(recent_records)} recent deployment records into cache")
            
        except Exception as e:
            self.logger.error(f"Failed to load recent records: {str(e)}")

    async def _periodic_storage_sync(self) -> None:
        """Periodically sync active deployments to storage"""        
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Store active deployments as checkpoints
                for deployment_id, record in self.active_deployments.items():
                    await self._store_deployment_checkpoint(record)
                
            except Exception as e:
                self.logger.error(f"Error in periodic storage sync: {str(e)}")

    async def _store_deployment_checkpoint(self, deployment_record: DeploymentRecord) -> None:
        """Store deployment checkpoint for recovery"""        
        try:
            checkpoint_path = self.base_storage_path / "checkpoints"
            checkpoint_path.mkdir(exist_ok=True)
            
            filename = f"{deployment_record.deployment_id}_checkpoint.json"
            file_path = checkpoint_path / filename
            
            record_data = asdict(deployment_record)
            record_data = self._serialize_datetimes(record_data)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(record_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to store checkpoint: {str(e)}")

    async def _periodic_analytics_update(self) -> None:
        """Periodically update analytics cache"""        
        while True:
            try:
                await asyncio.sleep(900)  # Every 15 minutes
                
                if datetime.utcnow() - self.last_analytics_update > self.analytics_cache_ttl:
                    await self._update_analytics_cache()
                    self.last_analytics_update = datetime.utcnow()
                
            except Exception as e:
                self.logger.error(f"Error in periodic analytics update: {str(e)}")

    async def _update_analytics_cache(self) -> None:
        """Update analytics cache with latest data"""        
        try:
            # Generate analytics for different time periods
            time_periods = ['1h', '24h', '7d', '30d']
            
            for period in time_periods:
                analytics = await self._calculate_analytics(period)
                self.analytics_cache[period] = analytics
            
            self.logger.info("Updated analytics cache")
            
        except Exception as e:
            self.logger.error(f"Failed to update analytics cache: {str(e)}")

    async def _calculate_analytics(self, time_period: str) -> DeploymentAnalytics:
        """Calculate deployment analytics for a time period"""        
        # Parse time period
        if time_period == '1h':
            cutoff = datetime.utcnow() - timedelta(hours=1)
        elif time_period == '24h':
            cutoff = datetime.utcnow() - timedelta(hours=24)
        elif time_period == '7d':
            cutoff = datetime.utcnow() - timedelta(days=7)
        elif time_period == '30d':
            cutoff = datetime.utcnow() - timedelta(days=30)
        else:
            cutoff = datetime.utcnow() - timedelta(hours=24)
        
        # Get deployment records in time period
        records = []
        
        # Check active deployments
        for record in self.active_deployments.values():
            if record.created_at >= cutoff:
                records.append(record)
        
        # Check cached deployments
        for record in self.deployment_cache.values():
            if record.created_at >= cutoff:
                records.append(record)
        
        # Get additional records from storage if needed
        storage_records = await self.storage.get_deployment_records_since(cutoff)
        records.extend(storage_records)
        
        # Remove duplicates
        unique_records = {record.deployment_id: record for record in records}
        records = list(unique_records.values())
        
        # Calculate analytics
        total_deployments = len(records)
        successful_deployments = len([r for r in records if r.status == DeploymentStatus.COMPLETED])
        failed_deployments = len([r for r in records if r.status == DeploymentStatus.FAILED])
        
        # Calculate average duration (only completed deployments)
        completed_records = [r for r in records if r.duration_seconds is not None]
        average_duration = (
            sum(r.duration_seconds for r in completed_records) / len(completed_records)
            if completed_records else 0
        )
        
        success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0
        
        # Strategy breakdown
        strategy_breakdown = {}
        for record in records:
            strategy = record.strategy.value
            strategy_breakdown[strategy] = strategy_breakdown.get(strategy, 0) + 1
        
        # Service breakdown
        service_breakdown = {}
        for record in records:
            for service in record.services:
                service_breakdown[service] = service_breakdown.get(service, 0) + 1
        
        # Failure reasons (from failed deployments)
        failure_reasons = {}
        for record in records:
            if record.status == DeploymentStatus.FAILED:
                failed_steps = [step for step in record.steps if step.status == "failed"]
                for step in failed_steps:
                    if step.error_message:
                        # Simple categorization of failure reasons
                        reason = self._categorize_failure_reason(step.error_message)
                        failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
        
        # Trends (simple implementation)
        trends = {
            'success_rate': [success_rate],
            'average_duration': [average_duration],
            'deployment_count': [total_deployments]
        }
        
        return DeploymentAnalytics(
            time_period=time_period,
            total_deployments=total_deployments,
            successful_deployments=successful_deployments,
            failed_deployments=failed_deployments,
            average_duration=average_duration,
            success_rate=success_rate,
            strategy_breakdown=strategy_breakdown,
            service_breakdown=service_breakdown,
            failure_reasons=failure_reasons,
            trends=trends
        )

    def _categorize_failure_reason(self, error_message: str) -> str:
        """Categorize failure reason from error message"""        
        error_lower = error_message.lower()
        
        if 'timeout' in error_lower:
            return 'timeout'
        elif 'connection' in error_lower or 'network' in error_lower:
            return 'network'
        elif 'resource' in error_lower or 'memory' in error_lower or 'cpu' in error_lower:
            return 'resource'
        elif 'permission' in error_lower or 'auth' in error_lower:
            return 'authorization'
        elif 'config' in error_lower:
            return 'configuration'
        elif 'health' in error_lower:
            return 'health_check'
        else:
            return 'other'

    async def _update_real_time_analytics(self, deployment_record: DeploymentRecord) -> None:
        """Update real-time analytics with new deployment"""        
        try:
            # Update analytics for current time periods
            for period in ['1h', '24h']:
                if period in self.analytics_cache:
                    analytics = self.analytics_cache[period]
                    
                    # Update counters
                    analytics.total_deployments += 1
                    
                    if deployment_record.status == DeploymentStatus.COMPLETED:
                        analytics.successful_deployments += 1
                    elif deployment_record.status == DeploymentStatus.FAILED:
                        analytics.failed_deployments += 1
                    
                    # Recalculate success rate
                    analytics.success_rate = (
                        analytics.successful_deployments / analytics.total_deployments * 100
                        if analytics.total_deployments > 0 else 0
                    )
                    
                    # Update strategy breakdown
                    strategy = deployment_record.strategy.value
                    analytics.strategy_breakdown[strategy] = (
                        analytics.strategy_breakdown.get(strategy, 0) + 1
                    )
                    
                    # Update service breakdown
                    for service in deployment_record.services:
                        analytics.service_breakdown[service] = (
                            analytics.service_breakdown.get(service, 0) + 1
                        )
        
        except Exception as e:
            self.logger.error(f"Failed to update real-time analytics: {str(e)}")

    async def _periodic_cleanup(self) -> None:
        """Periodically clean up old records and files"""        
        while True:
            try:
                await asyncio.sleep(86400)  # Every 24 hours
                
                # Clean up old checkpoint files
                await self._cleanup_checkpoints()
                
                # Archive old deployment records
                await self._archive_old_records()
                
                # Clean up cache
                await self._cleanup_cache()
                
            except Exception as e:
                self.logger.error(f"Error in periodic cleanup: {str(e)}")

    async def _cleanup_checkpoints(self) -> None:
        """Clean up old checkpoint files"""        
        try:
            checkpoint_path = self.base_storage_path / "checkpoints"
            if not checkpoint_path.exists():
                return
            
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            for file_path in checkpoint_path.glob("*.json"):
                if file_path.stat().st_mtime < cutoff_time.timestamp():
                    file_path.unlink()
            
            self.logger.info("Cleaned up old checkpoint files")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup checkpoints: {str(e)}")

    async def _archive_old_records(self) -> None:
        """Archive old deployment records"""        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            
            # Archive records older than retention period
            await self.storage.archive_deployment_records_before(cutoff_date)
            
            self.logger.info(f"Archived deployment records older than {self.retention_days} days")
            
        except Exception as e:
            self.logger.error(f"Failed to archive old records: {str(e)}")

    async def _cleanup_cache(self) -> None:
        """Clean up cache to maintain size limits"""        
        try:
            if len(self.deployment_cache) > self.max_cache_size:
                # Keep only the most recent records
                sorted_records = sorted(
                    self.deployment_cache.items(),
                    key=lambda x: x[1].created_at,
                    reverse=True
                )
                
                self.deployment_cache = dict(sorted_records[:self.max_cache_size])
                
                self.logger.info(f"Cleaned up cache, kept {self.max_cache_size} records")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup cache: {str(e)}")

    async def get_deployment_record(self, deployment_id: str) -> Optional[DeploymentRecord]:
        """Get deployment record by ID"""        
        # Check active deployments first
        if deployment_id in self.active_deployments:
            return self.active_deployments[deployment_id]
        
        # Check cache
        if deployment_id in self.deployment_cache:
            return self.deployment_cache[deployment_id]
        
        # Load from storage
        try:
            record = await self.storage.get_deployment_record(deployment_id)
            if record:
                # Add to cache for future access
                self.deployment_cache[deployment_id] = record
            return record
        except Exception as e:
            self.logger.error(f"Failed to load deployment record {deployment_id}: {str(e)}")
            return None

    async def get_deployment_analytics(self, time_period: str = '24h') -> Optional[DeploymentAnalytics]:
        """Get deployment analytics for a time period"""        
        # Check cache first
        if time_period in self.analytics_cache:
            cache_age = datetime.utcnow() - self.last_analytics_update
            if cache_age < self.analytics_cache_ttl:
                return self.analytics_cache[time_period]
        
        # Calculate fresh analytics
        try:
            analytics = await self._calculate_analytics(time_period)
            self.analytics_cache[time_period] = analytics
            return analytics
        except Exception as e:
            self.logger.error(f"Failed to calculate analytics: {str(e)}")
            return None

    async def search_deployments(
        self,
        filters: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> List[DeploymentRecord]:
        """Search deployment records with filters"""        
        try:
            return await self.storage.search_deployment_records(filters, limit, offset)
        except Exception as e:
            self.logger.error(f"Failed to search deployments: {str(e)}")
            return []

    async def export_deployment_data(
        self,
        format_type: str = 'json',
        time_range: Optional[tuple] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """        Export deployment data in specified format.
        
        Args:
            format_type: Export format (json, csv, excel)
            time_range: Optional time range (start, end)
            filters: Optional filters
            
        Returns:
            Path to exported file
        """        
        try:
            # Get records to export
            if time_range:
                start_date, end_date = time_range
                records = await self.storage.get_deployment_records_in_range(start_date, end_date)
            else:
                records = await self.storage.get_deployment_records_since(
                    datetime.utcnow() - timedelta(days=30)
                )
            
            # Apply filters if provided
            if filters:
                records = self._filter_records(records, filters)
            
            # Generate export filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            export_filename = f"deployment_export_{timestamp}.{format_type}"
            export_path = self.base_storage_path / "exports" / export_filename
            
            # Export data
            if format_type == 'json':
                await self._export_json(records, export_path)
            elif format_type == 'csv':
                await self._export_csv(records, export_path)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
            
            self.logger.info(f"Exported {len(records)} deployment records to {export_path}")
            
            return str(export_path)
            
        except Exception as e:
            self.logger.error(f"Failed to export deployment data: {str(e)}")
            raise

    def _filter_records(self, records: List[DeploymentRecord], filters: Dict[str, Any]) -> List[DeploymentRecord]:
        """Apply filters to deployment records"""        
        filtered_records = []
        
        for record in records:
            match = True
            
            if 'environment' in filters and record.environment.name != filters['environment']:
                match = False
            
            if 'status' in filters and record.status.value != filters['status']:
                match = False
            
            if 'strategy' in filters and record.strategy.value != filters['strategy']:
                match = False
            
            if 'service' in filters and filters['service'] not in record.services:
                match = False
            
            if 'initiated_by' in filters and record.initiated_by != filters['initiated_by']:
                match = False
            
            if match:
                filtered_records.append(record)
        
        return filtered_records

    async def _export_json(self, records: List[DeploymentRecord], export_path: Path) -> None:
        """Export records to JSON format"""        
        # Convert records to dictionaries
        export_data = []
        for record in records:
            record_dict = asdict(record)
            record_dict = self._serialize_datetimes(record_dict)
            export_data.append(record_dict)
        
        # Write to file
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)

    async def _export_csv(self, records: List[DeploymentRecord], export_path: Path) -> None:
        """Export records to CSV format"""        
        import csv
        
        if not records:
            return
        
        # Define CSV columns
        columns = [
            'deployment_id', 'workflow_id', 'environment', 'strategy', 'status',
            'created_at', 'started_at', 'completed_at', 'duration_seconds',
            'services', 'initiated_by', 'trigger_type', 'success_rate'
        ]
        
        with open(export_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            
            for record in records:
                # Calculate success rate for this deployment
                total_steps = len(record.steps)
                completed_steps = len([s for s in record.steps if s.status == "completed"])
                success_rate = (completed_steps / total_steps * 100) if total_steps > 0 else 0
                
                row = {
                    'deployment_id': record.deployment_id,
                    'workflow_id': record.workflow_id,
                    'environment': record.environment.name,
                    'strategy': record.strategy.value,
                    'status': record.status.value,
                    'created_at': record.created_at.isoformat(),
                    'started_at': record.started_at.isoformat() if record.started_at else '',
                    'completed_at': record.completed_at.isoformat() if record.completed_at else '',
                    'duration_seconds': record.duration_seconds or '',
                    'services': ', '.join(record.services),
                    'initiated_by': record.initiated_by,
                    'trigger_type': record.trigger_type,
                    'success_rate': f"{success_rate:.1f}%"
                }
                
                writer.writerow(row)
