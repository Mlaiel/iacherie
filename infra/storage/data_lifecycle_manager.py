# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Data Lifecycle Manager

Enterprise data lifecycle management system for automated data governance.
Provides comprehensive data lifecycle policies, retention management, and compliance.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import boto3
from google.cloud import storage as gcs
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential


class DataClassification(Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class DataState(Enum):
    """Data lifecycle states"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PURGED = "purged"


class RetentionTrigger(Enum):
    """Retention policy triggers"""
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
    SIZE_BASED = "size_based"
    ACCESS_BASED = "access_based"
    COMPLIANCE_BASED = "compliance_based"


class DataAction(Enum):
    """Data lifecycle actions"""
    MIGRATE = "migrate"
    ARCHIVE = "archive"
    DELETE = "delete"
    PURGE = "purge"
    ENCRYPT = "encrypt"
    ANONYMIZE = "anonymize"
    BACKUP = "backup"
    COMPRESS = "compress"


@dataclass
class DataLifecyclePolicy:
    """Data lifecycle policy definition"""
    id: str
    name: str
    description: str
    data_classification: DataClassification
    scope: str  # Storage location or pattern
    triggers: List[RetentionTrigger]
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]  # Action type and parameters
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_modified: datetime = field(default_factory=datetime.utcnow)
    compliance_frameworks: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class DataAsset:
    """Data asset representation"""
    id: str
    path: str
    name: str
    data_type: str
    classification: DataClassification
    state: DataState
    size_bytes: int
    created_at: datetime
    last_accessed: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    owner: Optional[str] = None
    department: Optional[str] = None
    applied_policies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    compliance_status: Dict[str, bool] = field(default_factory=dict)
    encryption_status: bool = False
    backup_status: bool = False
    archive_location: Optional[str] = None


@dataclass
class LifecycleAction:
    """Lifecycle action execution record"""
    id: str
    policy_id: str
    asset_id: str
    action_type: DataAction
    triggered_by: RetentionTrigger
    scheduled_at: datetime
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed
    error_message: Optional[str] = None
    result_metadata: Dict[str, Any] = field(default_factory=dict)


class DataLifecycleManager:
    """
    Enterprise data lifecycle management system
    
    Provides comprehensive data lifecycle management including:
    - Automated data classification and tagging
    - Retention policy management
    - Compliance-driven data governance
    - Automated archival and deletion
    - Data anonymization and encryption
    - Multi-cloud storage optimization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Data management
        self.policies: Dict[str, DataLifecyclePolicy] = {}
        self.assets: Dict[str, DataAsset] = {}
        self.pending_actions: Dict[str, LifecycleAction] = {}
        self.action_history: List[LifecycleAction] = []
        
        # Configuration
        self.scan_interval = self.config.get('scan_interval', 3600)  # 1 hour
        self.max_concurrent_actions = self.config.get('max_concurrent_actions', 10)
        self.dry_run_mode = self.config.get('dry_run_mode', False)
        
        # Initialize cloud clients
        self._initialize_cloud_clients()
        
        # Load default policies
        self._load_default_policies()
        
        # Background task tracking
        self.running_tasks: Set[str] = set()
    
    def _initialize_cloud_clients(self):
        """Initialize cloud storage clients"""
        
        # AWS S3 client
        try:
            aws_config = self.config.get('aws', {})
            self.s3_client = boto3.client(
                's3',
                region_name=aws_config.get('region', 'us-east-1'),
                aws_access_key_id=aws_config.get('access_key_id'),
                aws_secret_access_key=aws_config.get('secret_access_key')
            )
            self.logger.info("AWS S3 client initialized")
        except Exception as e:
            self.logger.warning(f"Failed to initialize AWS S3 client: {str(e)}")
            self.s3_client = None
        
        # GCP Storage client
        try:
            gcp_config = self.config.get('gcp', {})
            if gcp_config.get('project_id'):
                self.gcs_client = gcs.Client(project=gcp_config['project_id'])
                self.logger.info("GCP Storage client initialized")
            else:
                self.gcs_client = None
        except Exception as e:
            self.logger.warning(f"Failed to initialize GCP Storage client: {str(e)}")
            self.gcs_client = None
        
        # Azure Blob Storage client
        try:
            azure_config = self.config.get('azure', {})
            if azure_config.get('account_name'):
                credential = DefaultAzureCredential()
                self.blob_client = BlobServiceClient(
                    account_url=f"https://{azure_config['account_name']}.blob.core.windows.net",
                    credential=credential
                )
                self.logger.info("Azure Blob Storage client initialized")
            else:
                self.blob_client = None
        except Exception as e:
            self.logger.warning(f"Failed to initialize Azure Blob client: {str(e)}")
            self.blob_client = None
    
    def _load_default_policies(self):
        """Load default data lifecycle policies"""
        
        # GDPR Compliance Policy
        gdpr_policy = DataLifecyclePolicy(
            id="gdpr_compliance",
            name="GDPR Data Retention Policy",
            description="Automated data retention and deletion for GDPR compliance",
            data_classification=DataClassification.CONFIDENTIAL,
            scope="**/personal_data/**",
            triggers=[RetentionTrigger.TIME_BASED, RetentionTrigger.COMPLIANCE_BASED],
            conditions={
                "max_retention_days": 2555,  # 7 years
                "delete_after_days": 2920,   # 8 years maximum
                "anonymize_after_days": 1095  # 3 years
            },
            actions=[
                {"type": DataAction.ANONYMIZE, "after_days": 1095},
                {"type": DataAction.DELETE, "after_days": 2920}
            ],
            compliance_frameworks=["GDPR", "EU_DPA"]
        )
        
        # Financial Records Policy
        financial_policy = DataLifecyclePolicy(
            id="financial_records",
            name="Financial Records Retention",
            description="Financial data retention for regulatory compliance",
            data_classification=DataClassification.RESTRICTED,
            scope="**/financial/**",
            triggers=[RetentionTrigger.TIME_BASED],
            conditions={
                "archive_after_days": 365,   # 1 year to archive
                "delete_after_days": 2555    # 7 years retention
            },
            actions=[
                {"type": DataAction.ARCHIVE, "after_days": 365, "storage_class": "glacier"},
                {"type": DataAction.DELETE, "after_days": 2555}
            ],
            compliance_frameworks=["SOX", "IFRS"]
        )
        
        # Log Data Policy
        log_policy = DataLifecyclePolicy(
            id="log_data_retention",
            name="Log Data Lifecycle",
            description="Automated log data management and cleanup",
            data_classification=DataClassification.INTERNAL,
            scope="**/logs/**",
            triggers=[RetentionTrigger.TIME_BASED, RetentionTrigger.SIZE_BASED],
            conditions={
                "archive_after_days": 90,
                "delete_after_days": 365,
                "max_size_gb": 1000
            },
            actions=[
                {"type": DataAction.COMPRESS, "after_days": 30},
                {"type": DataAction.ARCHIVE, "after_days": 90, "storage_class": "ia"},
                {"type": DataAction.DELETE, "after_days": 365}
            ]
        )
        
        # Medical Records Policy
        medical_policy = DataLifecyclePolicy(
            id="medical_records",
            name="Medical Records Lifecycle",
            description="Healthcare data retention for HIPAA compliance",
            data_classification=DataClassification.RESTRICTED,
            scope="**/medical/**",
            triggers=[RetentionTrigger.TIME_BASED, RetentionTrigger.COMPLIANCE_BASED],
            conditions={
                "encrypt_immediately": True,
                "archive_after_days": 1095,   # 3 years
                "delete_after_days": 10950    # 30 years for medical records
            },
            actions=[
                {"type": DataAction.ENCRYPT, "immediately": True},
                {"type": DataAction.ARCHIVE, "after_days": 1095},
                {"type": DataAction.DELETE, "after_days": 10950}
            ],
            compliance_frameworks=["HIPAA", "HITECH"]
        )
        
        # Store default policies
        self.add_policy(gdpr_policy)
        self.add_policy(financial_policy)
        self.add_policy(log_policy)
        self.add_policy(medical_policy)
    
    def add_policy(self, policy: DataLifecyclePolicy):
        """Add a data lifecycle policy"""
        
        # Validate policy
        self._validate_policy(policy)
        
        # Store policy
        self.policies[policy.id] = policy
        
        self.logger.info(f"Added data lifecycle policy: {policy.name} ({policy.id})")
    
    def _validate_policy(self, policy: DataLifecyclePolicy):
        """Validate data lifecycle policy"""
        
        # Validate scope pattern
        if not policy.scope:
            raise ValueError("Policy scope cannot be empty")
        
        # Validate triggers and conditions alignment
        if RetentionTrigger.TIME_BASED in policy.triggers:
            required_conditions = ['max_retention_days', 'delete_after_days', 'archive_after_days']
            if not any(cond in policy.conditions for cond in required_conditions):
                raise ValueError("Time-based trigger requires time-based conditions")
        
        # Validate actions
        for action in policy.actions:
            if 'type' not in action:
                raise ValueError("Action must have a type")
            
            action_type = action['type']
            if isinstance(action_type, str):
                try:
                    DataAction(action_type)
                except ValueError:
                    raise ValueError(f"Invalid action type: {action_type}")
    
    def remove_policy(self, policy_id: str):
        """Remove a data lifecycle policy"""
        
        if policy_id not in self.policies:
            raise ValueError(f"Policy {policy_id} not found")
        
        policy_name = self.policies[policy_id].name
        del self.policies[policy_id]
        
        self.logger.info(f"Removed data lifecycle policy: {policy_name} ({policy_id})")
    
    async def discover_data_assets(self, storage_locations: List[str]) -> List[DataAsset]:
        """
        Discover and catalog data assets in specified storage locations
        
        Args:
            storage_locations: List of storage paths to scan
            
        Returns:
            List of discovered data assets
        """
        discovered_assets = []
        
        for location in storage_locations:
            self.logger.info(f"Discovering data assets in: {location}")
            
            try:
                if location.startswith('s3://'):
                    assets = await self._discover_s3_assets(location)
                elif location.startswith('gs://'):
                    assets = await self._discover_gcs_assets(location)
                elif location.startswith('https://') and 'blob.core.windows.net' in location:
                    assets = await self._discover_azure_assets(location)
                else:
                    assets = await self._discover_local_assets(location)
                
                discovered_assets.extend(assets)
                
            except Exception as e:
                self.logger.error(f"Error discovering assets in {location}: {str(e)}")
        
        # Store discovered assets
        for asset in discovered_assets:
            self.assets[asset.id] = asset
        
        self.logger.info(f"Discovered {len(discovered_assets)} data assets")
        
        return discovered_assets
    
    async def _discover_s3_assets(self, s3_path: str) -> List[DataAsset]:
        """Discover data assets in S3"""
        
        if not self.s3_client:
            return []
        
        assets = []
        
        try:
            # Parse S3 path
            bucket_name = s3_path.replace('s3://', '').split('/')[0]
            prefix = '/'.join(s3_path.replace('s3://', '').split('/')[1:]) if '/' in s3_path.replace('s3://', '') else ''
            
            # List objects
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
            
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        # Get object metadata
                        try:
                            head_response = self.s3_client.head_object(
                                Bucket=bucket_name,
                                Key=obj['Key']
                            )
                            
                            asset = DataAsset(
                                id=hashlib.sha256(f"s3://{bucket_name}/{obj['Key']}".encode()).hexdigest()[:16],
                                path=f"s3://{bucket_name}/{obj['Key']}",
                                name=obj['Key'].split('/')[-1],
                                data_type=self._infer_data_type(obj['Key']),
                                classification=self._classify_data(obj['Key']),
                                state=DataState.ACTIVE,
                                size_bytes=obj['Size'],
                                created_at=obj['LastModified'],
                                last_modified=obj['LastModified'],
                                last_accessed=head_response.get('LastModified'),
                                metadata=head_response.get('Metadata', {}),
                                encryption_status=head_response.get('ServerSideEncryption') is not None
                            )
                            
                            assets.append(asset)
                            
                        except Exception as e:
                            self.logger.warning(f"Error getting metadata for {obj['Key']}: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"Error discovering S3 assets: {str(e)}")
        
        return assets
    
    async def _discover_gcs_assets(self, gcs_path: str) -> List[DataAsset]:
        """Discover data assets in Google Cloud Storage"""
        
        if not self.gcs_client:
            return []
        
        assets = []
        
        try:
            # Parse GCS path
            bucket_name = gcs_path.replace('gs://', '').split('/')[0]
            prefix = '/'.join(gcs_path.replace('gs://', '').split('/')[1:]) if '/' in gcs_path.replace('gs://', '') else ''
            
            bucket = self.gcs_client.bucket(bucket_name)
            blobs = bucket.list_blobs(prefix=prefix)
            
            for blob in blobs:
                asset = DataAsset(
                    id=hashlib.sha256(f"gs://{bucket_name}/{blob.name}".encode()).hexdigest()[:16],
                    path=f"gs://{bucket_name}/{blob.name}",
                    name=blob.name.split('/')[-1],
                    data_type=self._infer_data_type(blob.name),
                    classification=self._classify_data(blob.name),
                    state=DataState.ACTIVE,
                    size_bytes=blob.size or 0,
                    created_at=blob.time_created,
                    last_modified=blob.updated,
                    metadata=blob.metadata or {},
                    encryption_status=blob.kms_key_name is not None
                )
                
                assets.append(asset)
        
        except Exception as e:
            self.logger.error(f"Error discovering GCS assets: {str(e)}")
        
        return assets
    
    async def _discover_azure_assets(self, azure_path: str) -> List[DataAsset]:
        """Discover data assets in Azure Blob Storage"""
        
        if not self.blob_client:
            return []
        
        assets = []
        
        try:
            # Parse Azure path to get container and blob prefix
            # Simplified parsing for demonstration
            container_name = "default-container"
            prefix = ""
            
            container_client = self.blob_client.get_container_client(container_name)
            blobs = container_client.list_blobs(name_starts_with=prefix)
            
            for blob in blobs:
                asset = DataAsset(
                    id=hashlib.sha256(f"azure://{container_name}/{blob.name}".encode()).hexdigest()[:16],
                    path=f"azure://{container_name}/{blob.name}",
                    name=blob.name.split('/')[-1],
                    data_type=self._infer_data_type(blob.name),
                    classification=self._classify_data(blob.name),
                    state=DataState.ACTIVE,
                    size_bytes=blob.size or 0,
                    created_at=blob.creation_time,
                    last_modified=blob.last_modified,
                    metadata=blob.metadata or {},
                    encryption_status=blob.encryption_scope is not None
                )
                
                assets.append(asset)
        
        except Exception as e:
            self.logger.error(f"Error discovering Azure assets: {str(e)}")
        
        return assets
    
    async def _discover_local_assets(self, local_path: str) -> List[DataAsset]:
        """Discover data assets in local filesystem"""
        
        assets = []
        
        try:
            import os
            import stat
            
            for root, dirs, files in os.walk(local_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_stat = os.stat(file_path)
                    
                    asset = DataAsset(
                        id=hashlib.sha256(file_path.encode()).hexdigest()[:16],
                        path=file_path,
                        name=file,
                        data_type=self._infer_data_type(file),
                        classification=self._classify_data(file_path),
                        state=DataState.ACTIVE,
                        size_bytes=file_stat.st_size,
                        created_at=datetime.fromtimestamp(file_stat.st_ctime),
                        last_modified=datetime.fromtimestamp(file_stat.st_mtime),
                        last_accessed=datetime.fromtimestamp(file_stat.st_atime)
                    )
                    
                    assets.append(asset)
        
        except Exception as e:
            self.logger.error(f"Error discovering local assets: {str(e)}")
        
        return assets
    
    def _infer_data_type(self, file_path: str) -> str:
        """Infer data type from file path/extension"""
        
        extension = file_path.split('.')[-1].lower() if '.' in file_path else 'unknown'
        
        type_mapping = {
            'json': 'structured',
            'xml': 'structured',
            'csv': 'structured',
            'parquet': 'structured',
            'avro': 'structured',
            'txt': 'unstructured',
            'log': 'log',
            'pdf': 'document',
            'doc': 'document',
            'docx': 'document',
            'jpg': 'image',
            'jpeg': 'image',
            'png': 'image',
            'gif': 'image',
            'mp4': 'video',
            'avi': 'video',
            'mp3': 'audio',
            'wav': 'audio',
            'sql': 'database',
            'db': 'database'
        }
        
        return type_mapping.get(extension, 'unknown')
    
    def _classify_data(self, file_path: str) -> DataClassification:
        """Classify data based on file path patterns"""
        
        path_lower = file_path.lower()
        
        # Check for sensitive data patterns
        sensitive_patterns = [
            'personal', 'pii', 'ssn', 'credit_card', 'medical', 'health',
            'confidential', 'secret', 'private', 'financial', 'banking'
        ]
        
        if any(pattern in path_lower for pattern in sensitive_patterns):
            return DataClassification.CONFIDENTIAL
        
        # Check for restricted patterns
        restricted_patterns = ['admin', 'security', 'audit', 'compliance']
        if any(pattern in path_lower for pattern in restricted_patterns):
            return DataClassification.RESTRICTED
        
        # Check for internal patterns
        internal_patterns = ['internal', 'employee', 'hr', 'payroll']
        if any(pattern in path_lower for pattern in internal_patterns):
            return DataClassification.INTERNAL
        
        # Default to public
        return DataClassification.PUBLIC
    
    async def evaluate_lifecycle_policies(self) -> List[LifecycleAction]:
        """
        Evaluate all assets against lifecycle policies and generate actions
        
        Returns:
            List of lifecycle actions to be executed
        """
        self.logger.info("Evaluating lifecycle policies for all assets")
        
        actions_to_schedule = []
        
        for asset_id, asset in self.assets.items():
            for policy_id, policy in self.policies.items():
                if not policy.enabled:
                    continue
                
                # Check if policy applies to this asset
                if self._policy_applies_to_asset(policy, asset):
                    # Evaluate policy conditions
                    triggered_actions = self._evaluate_policy_conditions(policy, asset)
                    
                    for action_config in triggered_actions:
                        action = LifecycleAction(
                            id=hashlib.sha256(f"{policy_id}_{asset_id}_{action_config['type']}_{datetime.utcnow()}".encode()).hexdigest()[:16],
                            policy_id=policy_id,
                            asset_id=asset_id,
                            action_type=DataAction(action_config['type']),
                            triggered_by=action_config.get('triggered_by', RetentionTrigger.TIME_BASED),
                            scheduled_at=action_config.get('scheduled_at', datetime.utcnow())
                        )
                        
                        actions_to_schedule.append(action)
        
        # Store scheduled actions
        for action in actions_to_schedule:
            self.pending_actions[action.id] = action
        
        self.logger.info(f"Scheduled {len(actions_to_schedule)} lifecycle actions")
        
        return actions_to_schedule
    
    def _policy_applies_to_asset(self, policy: DataLifecyclePolicy, asset: DataAsset) -> bool:
        """Check if a policy applies to an asset"""
        
        # Check data classification
        if asset.classification != policy.data_classification and policy.data_classification != DataClassification.PUBLIC:
            # Policy applies if asset classification is same or higher
            classification_levels = {
                DataClassification.PUBLIC: 0,
                DataClassification.INTERNAL: 1,
                DataClassification.CONFIDENTIAL: 2,
                DataClassification.RESTRICTED: 3,
                DataClassification.TOP_SECRET: 4
            }
            
            if classification_levels[asset.classification] < classification_levels[policy.data_classification]:
                return False
        
        # Check scope pattern
        import fnmatch
        if not fnmatch.fnmatch(asset.path, policy.scope):
            return False
        
        return True
    
    def _evaluate_policy_conditions(self, policy: DataLifecyclePolicy, asset: DataAsset) -> List[Dict[str, Any]]:
        """Evaluate policy conditions against an asset"""
        
        triggered_actions = []
        current_time = datetime.utcnow()
        
        for action_config in policy.actions:
            action_type = action_config['type']
            
            # Time-based evaluation
            if RetentionTrigger.TIME_BASED in policy.triggers:
                if 'after_days' in action_config:
                    days_since_creation = (current_time - asset.created_at).days
                    
                    if days_since_creation >= action_config['after_days']:
                        triggered_actions.append({
                            'type': action_type,
                            'triggered_by': RetentionTrigger.TIME_BASED,
                            'scheduled_at': current_time,
                            **action_config
                        })
                        continue
                
                if 'immediately' in action_config and action_config['immediately']:
                    triggered_actions.append({
                        'type': action_type,
                        'triggered_by': RetentionTrigger.TIME_BASED,
                        'scheduled_at': current_time,
                        **action_config
                    })
                    continue
            
            # Size-based evaluation
            if RetentionTrigger.SIZE_BASED in policy.triggers:
                if 'max_size_gb' in policy.conditions:
                    max_size_bytes = policy.conditions['max_size_gb'] * 1024 * 1024 * 1024
                    if asset.size_bytes > max_size_bytes:
                        triggered_actions.append({
                            'type': action_type,
                            'triggered_by': RetentionTrigger.SIZE_BASED,
                            'scheduled_at': current_time,
                            **action_config
                        })
                        continue
            
            # Access-based evaluation
            if RetentionTrigger.ACCESS_BASED in policy.triggers:
                if asset.last_accessed:
                    days_since_access = (current_time - asset.last_accessed).days
                    if 'no_access_days' in policy.conditions:
                        if days_since_access >= policy.conditions['no_access_days']:
                            triggered_actions.append({
                                'type': action_type,
                                'triggered_by': RetentionTrigger.ACCESS_BASED,
                                'scheduled_at': current_time,
                                **action_config
                            })
                            continue
        
        return triggered_actions
    
    async def execute_lifecycle_actions(self, max_concurrent: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute pending lifecycle actions
        
        Args:
            max_concurrent: Maximum number of concurrent actions
            
        Returns:
            Execution summary
        """
        max_concurrent = max_concurrent or self.max_concurrent_actions
        
        pending_actions = list(self.pending_actions.values())
        
        if not pending_actions:
            return {'total_actions': 0, 'executed': 0, 'failed': 0}
        
        self.logger.info(f"Executing {len(pending_actions)} lifecycle actions (max concurrent: {max_concurrent})")
        
        # Sort actions by priority (delete/purge first, then archive, etc.)
        action_priority = {
            DataAction.PURGE: 1,
            DataAction.DELETE: 2,
            DataAction.ARCHIVE: 3,
            DataAction.MIGRATE: 4,
            DataAction.ENCRYPT: 5,
            DataAction.ANONYMIZE: 6,
            DataAction.COMPRESS: 7,
            DataAction.BACKUP: 8
        }
        
        pending_actions.sort(key=lambda a: action_priority.get(a.action_type, 10))
        
        # Execute actions in batches
        executed = 0
        failed = 0
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_action(action):
            async with semaphore:
                try:
                    await self._execute_single_action(action)
                    return True
                except Exception as e:
                    self.logger.error(f"Failed to execute action {action.id}: {str(e)}")
                    action.status = "failed"
                    action.error_message = str(e)
                    return False
        
        # Execute all actions concurrently with semaphore limiting
        tasks = [execute_action(action) for action in pending_actions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count results
        for result in results:
            if isinstance(result, bool):
                if result:
                    executed += 1
                else:
                    failed += 1
            else:
                failed += 1
        
        self.logger.info(f"Lifecycle actions completed: {executed} executed, {failed} failed")
        
        return {
            'total_actions': len(pending_actions),
            'executed': executed,
            'failed': failed,
            'success_rate': (executed / len(pending_actions) * 100) if pending_actions else 0
        }
    
    async def _execute_single_action(self, action: LifecycleAction):
        """Execute a single lifecycle action"""
        
        action.status = "running"
        action.executed_at = datetime.utcnow()
        
        try:
            asset = self.assets.get(action.asset_id)
            if not asset:
                raise ValueError(f"Asset {action.asset_id} not found")
            
            if self.dry_run_mode:
                self.logger.info(f"DRY RUN: Would execute {action.action_type.value} on {asset.path}")
                action.status = "completed"
                action.completed_at = datetime.utcnow()
                return
            
            # Execute based on action type
            if action.action_type == DataAction.DELETE:
                await self._delete_asset(asset)
                asset.state = DataState.DELETED
            
            elif action.action_type == DataAction.ARCHIVE:
                await self._archive_asset(asset, action)
                asset.state = DataState.ARCHIVED
            
            elif action.action_type == DataAction.ENCRYPT:
                await self._encrypt_asset(asset)
                asset.encryption_status = True
            
            elif action.action_type == DataAction.ANONYMIZE:
                await self._anonymize_asset(asset)
            
            elif action.action_type == DataAction.COMPRESS:
                await self._compress_asset(asset)
            
            elif action.action_type == DataAction.BACKUP:
                await self._backup_asset(asset)
                asset.backup_status = True
            
            elif action.action_type == DataAction.MIGRATE:
                await self._migrate_asset(asset, action)
            
            elif action.action_type == DataAction.PURGE:
                await self._purge_asset(asset)
                asset.state = DataState.PURGED
                del self.assets[action.asset_id]
            
            action.status = "completed"
            action.completed_at = datetime.utcnow()
            
            # Move to history
            self.action_history.append(action)
            if action.id in self.pending_actions:
                del self.pending_actions[action.id]
            
            self.logger.info(f"Completed {action.action_type.value} on {asset.path}")
        
        except Exception as e:
            action.status = "failed"
            action.error_message = str(e)
            action.completed_at = datetime.utcnow()
            raise
    
    async def _delete_asset(self, asset: DataAsset):
        """Delete a data asset"""
        
        if asset.path.startswith('s3://'):
            await self._delete_s3_asset(asset)
        elif asset.path.startswith('gs://'):
            await self._delete_gcs_asset(asset)
        elif asset.path.startswith('azure://'):
            await self._delete_azure_asset(asset)
        else:
            await self._delete_local_asset(asset)
    
    async def _delete_s3_asset(self, asset: DataAsset):
        """Delete S3 object"""
        
        if not self.s3_client:
            raise RuntimeError("S3 client not available")
        
        # Parse S3 path
        path_parts = asset.path.replace('s3://', '').split('/')
        bucket = path_parts[0]
        key = '/'.join(path_parts[1:])
        
        self.s3_client.delete_object(Bucket=bucket, Key=key)
    
    async def _delete_gcs_asset(self, asset: DataAsset):
        """Delete GCS object"""
        
        if not self.gcs_client:
            raise RuntimeError("GCS client not available")
        
        # Parse GCS path
        path_parts = asset.path.replace('gs://', '').split('/')
        bucket_name = path_parts[0]
        blob_name = '/'.join(path_parts[1:])
        
        bucket = self.gcs_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.delete()
    
    async def _delete_azure_asset(self, asset: DataAsset):
        """Delete Azure blob"""
        
        if not self.blob_client:
            raise RuntimeError("Azure Blob client not available")
        
        # Simplified deletion for demonstration
        # Would need proper path parsing in real implementation
        pass
    
    async def _delete_local_asset(self, asset: DataAsset):
        """Delete local file"""
        
        import os
        os.remove(asset.path)
    
    async def _archive_asset(self, asset: DataAsset, action: LifecycleAction):
        """Archive a data asset"""
        
        # Implementation would depend on the target archive storage
        self.logger.info(f"Archiving asset {asset.path}")
        
        # Set archive location in metadata
        archive_location = f"archive://{asset.id}"
        asset.archive_location = archive_location
        asset.metadata['archived_at'] = datetime.utcnow().isoformat()
    
    async def _encrypt_asset(self, asset: DataAsset):
        """Encrypt a data asset"""
        
        self.logger.info(f"Encrypting asset {asset.path}")
        # Implementation would use appropriate encryption methods
        asset.metadata['encrypted_at'] = datetime.utcnow().isoformat()
    
    async def _anonymize_asset(self, asset: DataAsset):
        """Anonymize a data asset"""
        
        self.logger.info(f"Anonymizing asset {asset.path}")
        # Implementation would apply anonymization techniques
        asset.metadata['anonymized_at'] = datetime.utcnow().isoformat()
    
    async def _compress_asset(self, asset: DataAsset):
        """Compress a data asset"""
        
        self.logger.info(f"Compressing asset {asset.path}")
        # Implementation would compress the data
        asset.metadata['compressed_at'] = datetime.utcnow().isoformat()
    
    async def _backup_asset(self, asset: DataAsset):
        """Backup a data asset"""
        
        self.logger.info(f"Backing up asset {asset.path}")
        # Implementation would create backup copy
        asset.metadata['backed_up_at'] = datetime.utcnow().isoformat()
    
    async def _migrate_asset(self, asset: DataAsset, action: LifecycleAction):
        """Migrate a data asset"""
        
        self.logger.info(f"Migrating asset {asset.path}")
        # Implementation would move data to new location
        asset.metadata['migrated_at'] = datetime.utcnow().isoformat()
    
    async def _purge_asset(self, asset: DataAsset):
        """Permanently purge a data asset"""
        
        self.logger.info(f"Purging asset {asset.path}")
        # Implementation would permanently delete all copies
        # This is irreversible
    
    async def start_continuous_lifecycle_management(self):
        """Start continuous lifecycle management"""
        
        self.logger.info("Starting continuous data lifecycle management")
        
        while True:
            try:
                # Evaluate policies and execute actions
                await self.evaluate_lifecycle_policies()
                await self.execute_lifecycle_actions()
                
                # Clean up old action history
                await self._cleanup_action_history()
                
                # Sleep until next cycle
                await asyncio.sleep(self.scan_interval)
                
            except Exception as e:
                self.logger.error(f"Error in lifecycle management cycle: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _cleanup_action_history(self):
        """Clean up old action history"""
        
        cutoff_time = datetime.utcnow() - timedelta(days=90)  # Keep 90 days of history
        
        self.action_history = [
            action for action in self.action_history
            if action.executed_at and action.executed_at >= cutoff_time
        ]
    
    def get_policies(self) -> List[DataLifecyclePolicy]:
        """Get all lifecycle policies"""
        return list(self.policies.values())
    
    def get_policy(self, policy_id: str) -> Optional[DataLifecyclePolicy]:
        """Get specific lifecycle policy"""
        return self.policies.get(policy_id)
    
    def get_assets(
        self,
        classification: Optional[DataClassification] = None,
        state: Optional[DataState] = None,
        data_type: Optional[str] = None
    ) -> List[DataAsset]:
        """Get data assets with optional filters"""
        
        assets = list(self.assets.values())
        
        if classification:
            assets = [a for a in assets if a.classification == classification]
        
        if state:
            assets = [a for a in assets if a.state == state]
        
        if data_type:
            assets = [a for a in assets if a.data_type == data_type]
        
        return assets
    
    def get_lifecycle_summary(self) -> Dict[str, Any]:
        """Get data lifecycle management summary"""
        
        total_assets = len(self.assets)
        total_policies = len(self.policies)
        pending_actions = len(self.pending_actions)
        
        # Asset breakdown by state
        state_counts = {}
        for state in DataState:
            state_counts[state.value] = len([a for a in self.assets.values() if a.state == state])
        
        # Classification breakdown
        classification_counts = {}
        for classification in DataClassification:
            classification_counts[classification.value] = len([
                a for a in self.assets.values() if a.classification == classification
            ])
        
        # Policy compliance
        compliant_assets = 0
        for asset in self.assets.values():
            if asset.applied_policies:
                compliant_assets += 1
        
        compliance_rate = (compliant_assets / total_assets * 100) if total_assets > 0 else 0
        
        # Action statistics
        completed_actions = len([a for a in self.action_history if a.status == "completed"])
        failed_actions = len([a for a in self.action_history if a.status == "failed"])
        
        return {
            'total_assets': total_assets,
            'total_policies': total_policies,
            'pending_actions': pending_actions,
            'asset_state_breakdown': state_counts,
            'classification_breakdown': classification_counts,
            'compliance_rate': compliance_rate,
            'action_statistics': {
                'completed': completed_actions,
                'failed': failed_actions,
                'pending': pending_actions
            }
        }


# Export main classes
__all__ = ['DataLifecycleManager', 'DataLifecyclePolicy', 'DataAsset', 'LifecycleAction', 'DataClassification', 'DataState', 'RetentionTrigger', 'DataAction']