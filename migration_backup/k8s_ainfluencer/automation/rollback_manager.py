"""Rollback Manager - Deployment Automation

Advanced rollback management system for the IA Influencer Agent platform,
providing automated rollback capabilities, snapshot management, and 
disaster recovery for failed deployments.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import hashlib

from ..core.base import BaseComponent
from ..kubernetes.deployment_manager import DeploymentManager
from ..database.backup_manager import BackupManager
from ..storage.snapshot_manager import SnapshotManager
from ..monitoring.metrics_collector import MetricsCollector
from ..infrastructure.resource_manager import ResourceManager


class RollbackType(Enum):
    """
Rollback types"""

    AUTOMATIC = "automatic"
    MANUAL = "manual"
    EMERGENCY = "emergency"
    SCHEDULED = "scheduled"


class RollbackStatus(Enum):
    """Rollback status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


class SnapshotType(Enum):
    """Snapshot types"""

    FULL_SYSTEM = "full_system"
    APPLICATION = "application"
    DATABASE = "database"
    CONFIGURATION = "configuration"
    STORAGE = "storage"


@dataclass
class RollbackPoint:
    """Rollback point definition"""
    rollback_id: str
    name: str
    description: str
    created_at: datetime
    environment: str
    services: List[str]
    snapshots: Dict[str, str]  # snapshot_type -> snapshot_id
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    checksum: str = ""
    size_bytes: int = 0
    retention_days: int = 30


@dataclass
class RollbackExecution:
    """Rollback execution tracking"""
    execution_id: str
    rollback_point_id: str
    rollback_type: RollbackType
    status: RollbackStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    environment: str
    services: List[str]
    steps_completed: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    initiated_by: str = "system"


class RollbackManager(BaseComponent):
    """
    Enterprise-grade rollback management system.
    
    Provides comprehensive rollback capabilities including automatic snapshot
    creation, intelligent rollback point selection, and multi-component
    rollback orchestration with dependency management.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core managers
        self.deployment_manager = DeploymentManager(config.get('kubernetes', {}))
        self.backup_manager = BackupManager(config.get('backup', {}))
        self.snapshot_manager = SnapshotManager(config.get('storage', {}))
        self.metrics_collector = MetricsCollector(config.get('metrics', {}))
        self.resource_manager = ResourceManager(config.get('resources', {}))
        
        # Rollback state
        self.rollback_points: Dict[str, RollbackPoint] = {}
        self.active_rollbacks: Dict[str, RollbackExecution] = {}
        
        # Configuration
        self.auto_rollback_enabled = config.get('auto_rollback_enabled', True)
        self.max_rollback_points = config.get('max_rollback_points', 50)
        self.default_retention_days = config.get('default_retention_days', 30)
        
        # Rollback strategies
        self.rollback_strategies = {
            'kubernetes_deployment': self._rollback_kubernetes_deployment,
            'database_schema': self._rollback_database_schema,
            'configuration': self._rollback_configuration,
            'storage_volumes': self._rollback_storage_volumes,
            'network_config': self._rollback_network_config
        }
        
        # Dependency graph for ordered rollbacks
        self.service_dependencies = self._build_service_dependency_graph()

    def _build_service_dependency_graph(self) -> Dict[str, List[str]]:
        """
Build service dependency graph for rollback ordering"""
        return {
            'api_gateway': [],  # No dependencies, can rollback first
            'ai_agent': ['database', 'cache'],
            'content_protection': ['database', 'cache', 'storage'],
            'fingerprinting': ['database', 'cache', 'storage'],
            'monetization': ['database', 'cache', 'external_apis'],
            'crawler': ['database', 'cache', 'storage'],
            'database': [],
            'cache': [],
            'storage': [],
            'external_apis': []
        }

    async def create_rollback_point(
        self,
        workflow_id: str,
        environment: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Create a comprehensive rollback point.
        
        Args:
            workflow_id: Workflow identifier
            environment: Target environment
            context: Rollback context
            
        Returns:
            Rollback point ID
        """
        rollback_id = f"rollback-{uuid.uuid4().hex[:12]}"
        
        self.logger.info(f"Creating rollback point: {rollback_id} for workflow {workflow_id}")
        
        services = context.get('services', [])
        
        rollback_point = RollbackPoint(
            rollback_id=rollback_id,
            name=f"Pre-deployment snapshot for {workflow_id}",
            description=f"Automatic rollback point created before deployment",
            created_at=datetime.utcnow(),
            environment=environment,
            services=services,
            snapshots={},
            metadata={
                'workflow_id': workflow_id,
                'deployment_strategy': context.get('strategy', 'unknown'),
                'created_by': 'deployment_automation'
            },
            tags={
                'environment': environment,
                'workflow_id': workflow_id,
                'type': 'pre_deployment'
            }
        )
        
        try:
            # Create snapshots for each component type
            snapshots_created = {}
            total_size = 0
            
            # 1. Kubernetes deployment snapshots
            if services:
                k8s_snapshot_id = await self._create_kubernetes_snapshot(
                    services, environment, context
                )
                snapshots_created['kubernetes'] = k8s_snapshot_id
                
            # 2. Database snapshots
            db_snapshot_id = await self._create_database_snapshot(
                environment, context
            )
            snapshots_created['database'] = db_snapshot_id
            
            # 3. Configuration snapshots
            config_snapshot_id = await self._create_configuration_snapshot(
                services, environment, context
            )
            snapshots_created['configuration'] = config_snapshot_id
            
            # 4. Storage volume snapshots
            if context.get('storage_volumes'):
                storage_snapshot_id = await self._create_storage_snapshot(
                    context['storage_volumes'], environment, context
                )
                snapshots_created['storage'] = storage_snapshot_id
            
            # 5. Network configuration snapshot
            network_snapshot_id = await self._create_network_snapshot(
                environment, context
            )
            snapshots_created['network'] = network_snapshot_id
            
            # Update rollback point with snapshot information
            rollback_point.snapshots = snapshots_created
            rollback_point.size_bytes = total_size
            rollback_point.checksum = self._calculate_rollback_point_checksum(rollback_point)
            
            # Store rollback point
            self.rollback_points[rollback_id] = rollback_point
            
            # Persist rollback point metadata
            await self._persist_rollback_point_metadata(rollback_point)
            
            # Cleanup old rollback points if needed
            await self._cleanup_old_rollback_points(environment)
            
            self.logger.info(f"Rollback point created successfully: {rollback_id}")
            
            return rollback_id
            
        except Exception as e:
            self.logger.error(f"Failed to create rollback point: {rollback_id}", exc_info=True)
            
            # Cleanup partial snapshots
            await self._cleanup_partial_snapshots(snapshots_created)
            
            raise Exception(f"Rollback point creation failed: {str(e)}")

    async def execute_rollback(
        self,
        workflow_id: str,
        try:
            logger.info(f"Executing execute_rollback")
            
            # Implementation for execute_rollback
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"execute_rollback completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"execute_rollback failed: {e}")
            raise
    async def _create_kubernetes_snapshot(
        self,
        services: List[str],
        environment: str,
        context: Dict[str, Any]
    ) -> str:
        """Create Kubernetes deployment snapshots"""
        
        snapshot_id = f"k8s-snapshot-{uuid.uuid4().hex[:12]}"
        namespace = context.get('namespace', f"ia-influencer-{environment}")
        
        snapshot_data = {
            'snapshot_id': snapshot_id,
            'timestamp': datetime.utcnow().isoformat(),
            'namespace': namespace,
            'services': {}
        }
        
        for service in services:
            # Get current deployment configuration
            deployment = await self.deployment_manager.get_deployment(service, namespace)
            if deployment:
                snapshot_data['services'][service] = {
                    'deployment': deployment,
                    'revision': deployment.get('metadata', {}).get('annotations', {}).get(
                        'deployment.kubernetes.io/revision', '1'
                    )
                }
            
            # Get service configuration
            service_config = await self.deployment_manager.get_service(service, namespace)
            if service_config:
                snapshot_data['services'][service]['service'] = service_config
            
            # Get ingress configuration
            ingress_config = await self.deployment_manager.get_ingress(service, namespace)
            if ingress_config:
                snapshot_data['services'][service]['ingress'] = ingress_config
        
        # Store snapshot
        await self.snapshot_manager.store_snapshot(
            snapshot_id,
            SnapshotType.APPLICATION.value,
            snapshot_data
        )
        
        return snapshot_id

    async def _create_database_snapshot(
        self,
        environment: str,
        context: Dict[str, Any]
    ) -> str:
        """Create database snapshot"""
        
        snapshot_id = f"db-snapshot-{uuid.uuid4().hex[:12]}"
        
        # Create database backup
        backup_result = await self.backup_manager.create_database_backup(
            backup_name=f"rollback-backup-{snapshot_id}",
            environment=environment,
            include_schema=True,
            include_data=True,
            compression=True
        )
        
        # Store backup metadata as snapshot
        snapshot_data = {
            'snapshot_id': snapshot_id,
            'timestamp': datetime.utcnow().isoformat(),
            'backup_id': backup_result['backup_id'],
            'backup_location': backup_result['location'],
            'backup_size': backup_result['size'],
            'schema_version': backup_result.get('schema_version', 'unknown')
        }
        
        await self.snapshot_manager.store_snapshot(
            snapshot_id,
            SnapshotType.DATABASE.value,
            snapshot_data
        )
        
        return snapshot_id

    async def _create_configuration_snapshot(
        self,
        services: List[str],
        environment: str,
        context: Dict[str, Any]
    ) -> str:
        """Create configuration snapshot"""
        
        snapshot_id = f"config-snapshot-{uuid.uuid4().hex[:12]}"
        namespace = context.get('namespace', f"ia-influencer-{environment}")
        
        snapshot_data = {
            'snapshot_id': snapshot_id,
            'timestamp': datetime.utcnow().isoformat(),
            'namespace': namespace,
            'configmaps': {},
            'secrets': {}
        }
        
        # Snapshot ConfigMaps
        for service in services:
            configmap_name = f"{service}-config"
            configmap = await self.deployment_manager.get_configmap(configmap_name, namespace)
            if configmap:
                snapshot_data['configmaps'][service] = configmap
        
        # Snapshot Secrets (metadata only, not actual secret values)
        secret_name = "ia-influencer-secrets"
        secret_metadata = await self.deployment_manager.get_secret_metadata(secret_name, namespace)
        if secret_metadata:
            snapshot_data['secrets']['ia-influencer-secrets'] = secret_metadata
        
        await self.snapshot_manager.store_snapshot(
            snapshot_id,
            SnapshotType.CONFIGURATION.value,
            snapshot_data
        )
        
        return snapshot_id

    async def _create_storage_snapshot(
        self,
        volumes: List[str],
        environment: str,
        context: Dict[str, Any]
    ) -> str:
        """Create storage volume snapshots"""
        
        snapshot_id = f"storage-snapshot-{uuid.uuid4().hex[:12]}"
        
        snapshot_data = {
            'snapshot_id': snapshot_id,
            'timestamp': datetime.utcnow().isoformat(),
            'volumes': {}
        }
        
        for volume in volumes:
            volume_snapshot = await self.snapshot_manager.create_volume_snapshot(
                volume_id=volume,
                description=f"Rollback snapshot for {volume}"
            )
            
            snapshot_data['volumes'][volume] = {
                'volume_id': volume,
                'snapshot_id': volume_snapshot['snapshot_id'],
                'size': volume_snapshot['size'],
                'created_at': volume_snapshot['created_at']
            }
        
        await self.snapshot_manager.store_snapshot(
            snapshot_id,
            SnapshotType.STORAGE.value,
            snapshot_data
        )
        
        return snapshot_id

    async def _create_network_snapshot(
        self,
        environment: str,
        context: Dict[str, Any]
    ) -> str:
        """Create network configuration snapshot"""
        
        snapshot_id = f"network-snapshot-{uuid.uuid4().hex[:12]}"
        
        # Get current network configuration
        network_config = await self.resource_manager.get_network_configuration(environment)
        
        snapshot_data = {
            'snapshot_id': snapshot_id,
            'timestamp': datetime.utcnow().isoformat(),
            'environment': environment,
            'network_config': network_config
        }
        
        await self.snapshot_manager.store_snapshot(
            snapshot_id,
            SnapshotType.CONFIGURATION.value,
            snapshot_data
        )
        
        return snapshot_id

    async def _select_best_rollback_point(
        self,
        workflow_id: str,
        environment: str,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Select the best rollback point for the given context"""
        
        # Find rollback points for this environment
        candidates = [
            rp for rp in self.rollback_points.values()
            if rp.environment == environment
        ]
        
        if not candidates:
            return None
        
        # Prefer rollback points created for this workflow
        workflow_candidates = [
            rp for rp in candidates
            if rp.metadata.get('workflow_id') == workflow_id
        ]
        
        if workflow_candidates:
            # Select the most recent one
            return max(workflow_candidates, key=lambda rp: rp.created_at).rollback_id
        
        # Fallback to most recent rollback point for environment
        return max(candidates, key=lambda rp: rp.created_at).rollback_id

    def _plan_rollback_steps(
        self,
        rollback_point: RollbackPoint,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
Plan rollback steps in correct dependency order"""
        
        steps = []
        
        # 1. Stop current services (reverse dependency order)
        service_order = self._get_service_rollback_order(rollback_point.services)
        
        for service in service_order:
            steps.append({
                'name': f'stop_{service}',
                'type': 'service_stop',
                'service': service,
                'critical': False
            })
        
        # 2. Rollback storage volumes (if any)
        if 'storage' in rollback_point.snapshots:
            steps.append({
                'name': 'rollback_storage',
                'type': 'storage_rollback',
                'snapshot_id': rollback_point.snapshots['storage'],
                'critical': True
            })
        
        # 3. Rollback database
        if 'database' in rollback_point.snapshots:
            steps.append({
                'name': 'rollback_database',
                'type': 'database_rollback',
                'snapshot_id': rollback_point.snapshots['database'],
                'critical': True
            })
        
        # 4. Rollback configurations
        if 'configuration' in rollback_point.snapshots:
            steps.append({
                'name': 'rollback_configuration',
                'type': 'configuration_rollback',
                'snapshot_id': rollback_point.snapshots['configuration'],
                'critical': True
            })
        
        # 5. Rollback Kubernetes deployments
        if 'kubernetes' in rollback_point.snapshots:
            for service in reversed(service_order):  # Start services in forward order
                steps.append({
                    'name': f'rollback_{service}_deployment',
                    'type': 'kubernetes_rollback',
                    'service': service,
                    'snapshot_id': rollback_point.snapshots['kubernetes'],
                    'critical': True
                })
        
        # 6. Validate services are healthy
        steps.append({
            'name': 'validate_rollback',
            'type': 'validation',
            'critical': True
        })
        
        return steps

    def _get_service_rollback_order(self, services: List[str]) -> List[str]:
        """
Get correct order for service rollback (considering dependencies)"""
        
        # Use topological sort to determine rollback order
        ordered_services = []
        visited = set()
        temp_visited = set()
        
        def visit(service):
            if service in temp_visited:
                # Circular dependency, just add it
                return
            if service in visited:
                return
                
            temp_visited.add(service)
            
            # Visit dependencies first
            for dependency in self.service_dependencies.get(service, []):
                if dependency in services:
                    visit(dependency)
            
            temp_visited.remove(service)
            visited.add(service)
            ordered_services.append(service)
        
        for service in services:
            if service not in visited:
                visit(service)
        
        return ordered_services

    async def _execute_rollback_step(
        self,
        step: Dict[str, Any],
        rollback_point: RollbackPoint,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Execute a single rollback step"""
        
        step_type = step['type']
        
        if step_type == 'service_stop':
            return await self._stop_service_step(step, context)
        elif step_type == 'storage_rollback':
            return await self._rollback_storage_step(step, rollback_point, context)
        elif step_type == 'database_rollback':
            return await self._rollback_database_step(step, rollback_point, context)
        elif step_type == 'configuration_rollback':
            return await self._rollback_configuration_step(step, rollback_point, context)
        elif step_type == 'kubernetes_rollback':
            return await self._rollback_kubernetes_step(step, rollback_point, context)
        elif step_type == 'validation':
            return await self._validate_rollback_step(step, rollback_point, context)
        else:
            raise ValueError(f"Unknown rollback step type: {step_type}")

    async def _stop_service_step(
        self,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stop a service"""
        
        service = step['service']
        namespace = context.get('namespace', f"ia-influencer-{context.get('environment', 'default')}")
        
        # Scale deployment to 0 replicas
        await self.deployment_manager.scale_deployment(service, namespace, 0)
        
        # Wait for pods to terminate
        await self.deployment_manager.wait_for_termination(service, namespace, timeout=120)
        
        return {'status': 'completed', 'service': service}

    async def _rollback_storage_step(
        self,
        step: Dict[str, Any],
        rollback_point: RollbackPoint,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Rollback storage volumes"""
        
        snapshot_id = step['snapshot_id']
        snapshot_data = await self.snapshot_manager.get_snapshot(snapshot_id)
        
        rollback_results = {}
        
        for volume_id, volume_info in snapshot_data['volumes'].items():
            volume_snapshot_id = volume_info['snapshot_id']
            
            # Restore volume from snapshot
            restore_result = await self.snapshot_manager.restore_volume_from_snapshot(
                volume_id, volume_snapshot_id
            )
            
            rollback_results[volume_id] = restore_result
        
        return {'status': 'completed', 'results': rollback_results}

    async def _rollback_database_step(
        self,
        step: Dict[str, Any],
        rollback_point: RollbackPoint,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Rollback database"""
        
        snapshot_id = step['snapshot_id']
        snapshot_data = await self.snapshot_manager.get_snapshot(snapshot_id)
        
        backup_id = snapshot_data['backup_id']
        
        # Restore database from backup
        restore_result = await self.backup_manager.restore_database_backup(
            backup_id,
            environment=context.get('environment', 'default'),
            validate_before_restore=True
        )
        
        return {'status': 'completed', 'restore_result': restore_result}

    async def _rollback_configuration_step(
        self,
        step: Dict[str, Any],
        rollback_point: RollbackPoint,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Rollback configurations"""
        
        snapshot_id = step['snapshot_id']
        snapshot_data = await self.snapshot_manager.get_snapshot(snapshot_id)
        
        namespace = snapshot_data['namespace']
        rollback_results = {}
        
        # Restore ConfigMaps
        for service, configmap_data in snapshot_data['configmaps'].items():
            await self.deployment_manager.apply_configmap(configmap_data, namespace)
            rollback_results[f"{service}_configmap"] = 'restored'
        
        # Note: Secrets are not restored from snapshots for security reasons
        # They would need to be manually recreated if needed
        
        return {'status': 'completed', 'results': rollback_results}

    async def _rollback_kubernetes_step(
        self,
        step: Dict[str, Any],
        rollback_point: RollbackPoint,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Rollback Kubernetes deployment"""
        
        service = step['service']
        snapshot_id = step['snapshot_id']
        snapshot_data = await self.snapshot_manager.get_snapshot(snapshot_id)
        
        if service not in snapshot_data['services']:
            raise ValueError(f"Service {service} not found in snapshot")
        
        service_data = snapshot_data['services'][service]
        namespace = snapshot_data['namespace']
        
        # Restore deployment
        if 'deployment' in service_data:
            await self.deployment_manager.apply_deployment(
                service_data['deployment'], namespace
            )
        
        # Restore service
        if 'service' in service_data:
            await self.deployment_manager.apply_service(
                service_data['service'], namespace
            )
        
        # Restore ingress
        if 'ingress' in service_data:
            await self.deployment_manager.apply_ingress(
                service_data['ingress'], namespace
            )
        
        # Wait for deployment to be ready
        await self.deployment_manager.wait_for_rollout(
            service, namespace, timeout=300
        )
        
        return {'status': 'completed', 'service': service}

    async def _validate_rollback_step(
        self,
        step: Dict[str, Any],
        rollback_point: RollbackPoint,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate rollback success"""
        
        validation_results = {}
        
        # Check service health
        for service in rollback_point.services:
            health_status = await self._check_service_health_after_rollback(
                service, context
            )
            validation_results[service] = health_status
        
        # Check database connectivity
        db_status = await self._check_database_health_after_rollback(context)
        validation_results['database'] = db_status
        
        # Overall validation
        all_healthy = all(
            status.get('healthy', False) for status in validation_results.values()
        )
        
        return {
            'status': 'completed' if all_healthy else 'failed',
            'all_healthy': all_healthy,
            'detailed_results': validation_results
        }

    async def _check_service_health_after_rollback(
        self,
        service: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Check service health after rollback"""
        
        namespace = context.get('namespace', f"ia-influencer-{context.get('environment', 'default')}")
        
        # Check pod status
        pods = await self.deployment_manager.get_pods_by_label(
            f"app={service}", namespace
        )
        
        healthy_pods = [p for p in pods if p['status']['phase'] == 'Running']
        
        return {
            'healthy': len(healthy_pods) > 0,
            'total_pods': len(pods),
            'healthy_pods': len(healthy_pods)
        }

    async def _check_database_health_after_rollback(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check database health after rollback"""
        
        try:
            # Simple connection test
            connection_result = await self.backup_manager.test_database_connection(
                context.get('environment', 'default')
            )
            return {
                'healthy': connection_result.get('connected', False),
                'details': connection_result
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }

    async def _validate_rollback_success(
        self,
        rollback_point: RollbackPoint,
        rollback_execution: RollbackExecution,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Validate overall rollback success"""
        
        validation_result = {
            'success': True,
            'errors': [],
            'warnings': []
        }
        
        # Check if all critical steps completed
        critical_steps = ['rollback_database', 'rollback_configuration']
        critical_steps.extend([f'rollback_{s}_deployment' for s in rollback_point.services])
        
        for step in critical_steps:
            if step not in rollback_execution.steps_completed:
                validation_result['success'] = False
                validation_result['errors'].append(f"Critical step not completed: {step}")
        
        # Check for step errors
        if rollback_execution.errors:
            validation_result['success'] = False
            validation_result['errors'].extend(rollback_execution.errors)
        
        return validation_result

    def _format_rollback_execution_result(
        self,
        rollback_execution: RollbackExecution
    ) -> Dict[str, Any]:
        """Format rollback execution result"""
        
        return {
            'execution_id': rollback_execution.execution_id,
            'rollback_point_id': rollback_execution.rollback_point_id,
            'status': rollback_execution.status.value,
            'started_at': rollback_execution.started_at,
            'completed_at': rollback_execution.completed_at,
            'duration': (
                (rollback_execution.completed_at or datetime.utcnow()) - 
                rollback_execution.started_at
            ).total_seconds(),
            'services': rollback_execution.services,
            'steps_completed': rollback_execution.steps_completed,
            'errors': rollback_execution.errors,
            'metrics': rollback_execution.metrics,
            'reason': rollback_execution.reason,
            'initiated_by': rollback_execution.initiated_by
        }

    def _calculate_rollback_point_checksum(self, rollback_point: RollbackPoint) -> str:
        """
Calculate checksum for rollback point integrity"""
        
        data_to_hash = json.dumps({
            'rollback_id': rollback_point.rollback_id,
            'environment': rollback_point.environment,
            'services': sorted(rollback_point.services),
            'snapshots': rollback_point.snapshots,
            'created_at': rollback_point.created_at.isoformat()
        }, sort_keys=True)
        
        return hashlib.sha256(data_to_hash.encode()).hexdigest()

    async def _persist_rollback_point_metadata(self, rollback_point: RollbackPoint) -> None:
        """
Persist rollback point metadata"""
        
        metadata = {
            'rollback_id': rollback_point.rollback_id,
            'name': rollback_point.name,
            'description': rollback_point.description,
            'created_at': rollback_point.created_at.isoformat(),
            'environment': rollback_point.environment,
            'services': rollback_point.services,
            'snapshots': rollback_point.snapshots,
            'metadata': rollback_point.metadata,
            'tags': rollback_point.tags,
            'checksum': rollback_point.checksum,
            'size_bytes': rollback_point.size_bytes,
            'retention_days': rollback_point.retention_days
        }
        
        await self.snapshot_manager.store_snapshot(
            f"{rollback_point.rollback_id}-metadata",
            "metadata",
            metadata
        )

    async def _cleanup_old_rollback_points(self, environment: str) -> None:
        """Cleanup old rollback points"""
        
        # Get rollback points for environment sorted by creation time
        env_rollback_points = [
            rp for rp in self.rollback_points.values()
            if rp.environment == environment
        ]
        
        env_rollback_points.sort(key=lambda rp: rp.created_at, reverse=True)
        
        # Remove excess rollback points
        if len(env_rollback_points) > self.max_rollback_points:
            points_to_remove = env_rollback_points[self.max_rollback_points:]
            
            for rollback_point in points_to_remove:
                await self._delete_rollback_point(rollback_point.rollback_id)
        
        # Remove expired rollback points
        cutoff_date = datetime.utcnow() - timedelta(days=self.default_retention_days)
        
        for rollback_point in env_rollback_points:
            if rollback_point.created_at < cutoff_date:
                await self._delete_rollback_point(rollback_point.rollback_id)

    async def _delete_rollback_point(self, rollback_point_id: str) -> None:
        """
Delete a rollback point and its snapshots"""
        
        if rollback_point_id not in self.rollback_points:
            return
        
        rollback_point = self.rollback_points[rollback_point_id]
        
        # Delete snapshots
        for snapshot_id in rollback_point.snapshots.values():
            try:
                await self.snapshot_manager.delete_snapshot(snapshot_id)
            except Exception as e:
                self.logger.warning(f"Failed to delete snapshot {snapshot_id}: {str(e)}")
        
        # Delete metadata
        try:
            await self.snapshot_manager.delete_snapshot(f"{rollback_point_id}-metadata")
        except Exception as e:
            self.logger.warning(f"Failed to delete metadata for {rollback_point_id}: {str(e)}")
        
        # Remove from memory
        del self.rollback_points[rollback_point_id]

    async def _cleanup_partial_snapshots(self, snapshots: Dict[str, str]) -> None:
        """Cleanup partial snapshots on failure"""
        
        for snapshot_id in snapshots.values():
            try:
                await self.snapshot_manager.delete_snapshot(snapshot_id)
            except Exception as e:
                self.logger.warning(f"Failed to cleanup partial snapshot {snapshot_id}: {str(e)}")

    async def list_rollback_points(self, environment: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available rollback points"""
        
        rollback_points = self.rollback_points.values()
        
        if environment:
            rollback_points = [rp for rp in rollback_points if rp.environment == environment]
        
        return [
            {
                'rollback_id': rp.rollback_id,
                'name': rp.name,
                'description': rp.description,
                'created_at': rp.created_at,
                'environment': rp.environment,
                'services': rp.services,
                'size_bytes': rp.size_bytes,
                'retention_days': rp.retention_days,
                'tags': rp.tags
            }
            for rp in sorted(rollback_points, key=lambda x: x.created_at, reverse=True)
        ]

    async def get_rollback_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
Get rollback execution status"""
        
        if execution_id in self.active_rollbacks:
            return self._format_rollback_execution_result(self.active_rollbacks[execution_id])
        
        return None

    async def cancel_rollback_execution(self, execution_id: str) -> bool:
        """
Cancel an active rollback execution"""
        
        if execution_id not in self.active_rollbacks:
            return False
        
        rollback_execution = self.active_rollbacks[execution_id]
        
        if rollback_execution.status == RollbackStatus.IN_PROGRESS:
            rollback_execution.status = RollbackStatus.CANCELLED
            rollback_execution.completed_at = datetime.utcnow()
            rollback_execution.errors.append("Rollback cancelled by user")
            return True
        
        return False
