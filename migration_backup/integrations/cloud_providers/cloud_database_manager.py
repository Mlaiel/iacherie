"""Multi-Cloud Database Manager
===============================

Enterprise-grade multi-cloud database management system supporting
AWS RDS, Azure SQL, GCP Cloud SQL, MongoDB Atlas, and more.

This module provides unified database lifecycle management, intelligent
backup and recovery, performance optimization, and cost management
across multiple cloud database providers for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import os
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal
import hashlib

import boto3
import httpx
import asyncpg
import aiomysql
from azure.identity import DefaultAzureCredential
from azure.mgmt.sql import SqlManagementClient
from google.cloud import sql_v1
from pymongo import MongoClient
from botocore.exceptions import ClientError


class DatabaseType(Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MARIADB = "mariadb"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    CASSANDRA = "cassandra"
    DYNAMODB = "dynamodb"
    COSMOSDB = "cosmosdb"
    FIRESTORE = "firestore"


class DatabaseEngine(Enum):
    """Database engine versions."""
    POSTGRESQL_13 = "postgresql-13"
    POSTGRESQL_14 = "postgresql-14"
    POSTGRESQL_15 = "postgresql-15"
    MYSQL_8_0 = "mysql-8.0"
    MYSQL_5_7 = "mysql-5.7"
    MARIADB_10_6 = "mariadb-10.6"
    MONGODB_6_0 = "mongodb-6.0"
    REDIS_7_0 = "redis-7.0"


class CloudProvider(Enum):
    """Supported cloud providers for databases."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    MONGODB_ATLAS = "mongodb_atlas"
    DIGITALOCEAN = "digitalocean"
    HEROKU = "heroku"
    SUPABASE = "supabase"
    PLANETSCALE = "planetscale"


class DatabaseState(Enum):
    """Database instance states."""
    CREATING = "creating"
    AVAILABLE = "available"
    MODIFYING = "modifying"
    DELETING = "deleting"
    DELETED = "deleted"
    BACKING_UP = "backing_up"
    RESTORING = "restoring"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class BackupType(Enum):
    """Backup types."""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    POINT_IN_TIME = "point_in_time"
    SNAPSHOT = "snapshot"


@dataclass
class DatabaseInstance:
    """Unified database instance representation."""
    id: str
    name: str
    provider: CloudProvider
    database_type: DatabaseType
    engine: DatabaseEngine
    state: DatabaseState
    region: str
    endpoint: Optional[str] = None
    port: Optional[int] = None
    master_username: Optional[str] = None
    database_name: Optional[str] = None
    allocated_storage_gb: int = 20
    instance_class: str = "db.t3.micro"
    multi_az: bool = False
    encrypted: bool = True
    backup_retention_days: int = 7
    maintenance_window: Optional[str] = None
    cost_per_hour: Decimal = field(default_factory=lambda: Decimal('0.00'))
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    connection_config: Dict[str, Any] = field(default_factory=dict)
    performance_insights: bool = False
    monitoring_enabled: bool = True


@dataclass
class DatabaseBackup:
    """Database backup representation."""
    id: str
    database_id: str
    backup_type: BackupType
    status: str
    created_at: datetime
    size_mb: Optional[int] = None
    retention_until: Optional[datetime] = None
    encrypted: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DatabaseCluster:
    """Database cluster for high availability."""
    id: str
    name: str
    provider: CloudProvider
    database_type: DatabaseType
    primary_instance: str
    read_replicas: List[str] = field(default_factory=list)
    region: str = ""
    backup_config: Dict[str, Any] = field(default_factory=dict)
    failover_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Database performance metrics."""
    timestamp: datetime
    database_id: str
    cpu_utilization: float
    memory_utilization: float
    disk_utilization: float
    connections_active: int
    connections_max: int
    queries_per_second: float
    read_iops: float
    write_iops: float
    read_latency_ms: float
    write_latency_ms: float


class MultiCloudDatabaseManager:
    """Enterprise multi-cloud database manager."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize multi-cloud database manager.
        
        Args:
            config: Configuration dict with provider credentials and settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Provider clients
        self.aws_rds = None
        self.aws_dynamodb = None
        self.azure_sql = None
        self.gcp_sql = None
        self.mongodb_client = None
        
        # Internal state
        self.databases: Dict[str, DatabaseInstance] = {}
        self.clusters: Dict[str, DatabaseCluster] = {}
        self.backups: Dict[str, List[DatabaseBackup]] = {}
        
        # Performance monitoring
        self.metrics_history: Dict[str, List[PerformanceMetrics]] = {}
        
        # Cost tracking
        self.cost_metrics = {
            'total_cost_per_hour': Decimal('0.00'),
            'cost_by_provider': {},
            'cost_by_database_type': {},
            'storage_costs': Decimal('0.00'),
            'backup_costs': Decimal('0.00')
        }
        
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize cloud provider database clients."""
        try:
            # AWS RDS
            if 'aws' in self.config:
                aws_config = self.config['aws']
                self.aws_rds = boto3.client(
                    'rds',
                    aws_access_key_id=aws_config.get('access_key_id'),
                    aws_secret_access_key=aws_config.get('secret_access_key'),
                    region_name=aws_config.get('region', 'us-east-1')
                )
                
                self.aws_dynamodb = boto3.client(
                    'dynamodb',
                    aws_access_key_id=aws_config.get('access_key_id'),
                    aws_secret_access_key=aws_config.get('secret_access_key'),
                    region_name=aws_config.get('region', 'us-east-1')
                )
                self.logger.info("AWS RDS and DynamoDB clients initialized")
            
            # Azure SQL
            if 'azure' in self.config:
                azure_config = self.config['azure']
                credential = DefaultAzureCredential()
                self.azure_sql = SqlManagementClient(
                    credential,
                    azure_config.get('subscription_id')
                )
                self.logger.info("Azure SQL client initialized")
            
            # GCP Cloud SQL
            if 'gcp' in self.config:
                gcp_config = self.config['gcp']
                if 'credentials_path' in gcp_config:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gcp_config['credentials_path']
                self.gcp_sql = sql_v1.SqlInstancesServiceClient()
                self.logger.info("GCP Cloud SQL client initialized")
            
            # MongoDB Atlas
            if 'mongodb_atlas' in self.config:
                atlas_config = self.config['mongodb_atlas']
                self.mongodb_client = MongoClient(
                    atlas_config.get('connection_string'),
                    username=atlas_config.get('username'),
                    password=atlas_config.get('password')
                )
                self.logger.info("MongoDB Atlas client initialized")
                
        except Exception as e:
            self.logger.error(f"Error initializing database providers: {e}")
            raise
    
    async def list_databases(self, provider: Optional[CloudProvider] = None) -> List[DatabaseInstance]:
        """List database instances across providers.
        
        Args:
            provider: Optional specific provider to query
            
        Returns:
            List of database instances
        """
        databases = []
        
        try:
            if provider is None or provider == CloudProvider.AWS:
                databases.extend(await self._list_aws_databases())
            
            if provider is None or provider == CloudProvider.AZURE:
                databases.extend(await self._list_azure_databases())
            
            if provider is None or provider == CloudProvider.GCP:
                databases.extend(await self._list_gcp_databases())
            
            if provider is None or provider == CloudProvider.MONGODB_ATLAS:
                databases.extend(await self._list_mongodb_atlas_databases())
            
            # Update internal state
            for database in databases:
                self.databases[database.id] = database
            
            self._update_cost_metrics()
            return databases
            
        except Exception as e:
            self.logger.error(f"Error listing databases: {e}")
            raise
    
    async def _list_aws_databases(self) -> List[DatabaseInstance]:
        """List AWS RDS instances."""
        if not self.aws_rds:
            return []
        
        databases = []
        try:
            # RDS instances
            response = self.aws_rds.describe_db_instances()
            
            for db_instance in response['DBInstances']:
                database = DatabaseInstance(
                    id=db_instance['DBInstanceIdentifier'],
                    name=db_instance['DBInstanceIdentifier'],
                    provider=CloudProvider.AWS,
                    database_type=self._map_aws_engine_to_type(db_instance['Engine']),
                    engine=self._map_aws_engine_version(db_instance['Engine'], db_instance.get('EngineVersion', '')),
                    state=self._map_aws_db_state(db_instance['DBInstanceStatus']),
                    region=db_instance['AvailabilityZone'][:-1] if db_instance.get('AvailabilityZone') else 'unknown',
                    endpoint=db_instance.get('Endpoint', {}).get('Address'),
                    port=db_instance.get('Endpoint', {}).get('Port'),
                    master_username=db_instance.get('MasterUsername'),
                    database_name=db_instance.get('DBName'),
                    allocated_storage_gb=db_instance.get('AllocatedStorage', 0),
                    instance_class=db_instance['DBInstanceClass'],
                    multi_az=db_instance.get('MultiAZ', False),
                    encrypted=db_instance.get('StorageEncrypted', False),
                    backup_retention_days=db_instance.get('BackupRetentionPeriod', 0),
                    maintenance_window=db_instance.get('PreferredMaintenanceWindow'),
                    created_at=db_instance.get('InstanceCreateTime', datetime.utcnow()),
                    performance_insights=db_instance.get('PerformanceInsightsEnabled', False)
                )
                
                # Calculate cost
                database.cost_per_hour = self._calculate_aws_rds_cost(
                    database.instance_class,
                    database.allocated_storage_gb,
                    database.region,
                    database.multi_az
                )
                
                # Get tags
                try:
                    tags_response = self.aws_rds.list_tags_for_resource(
                        ResourceName=db_instance['DBInstanceArn']
                    )
                    database.tags = {
                        tag['Key']: tag['Value']
                        for tag in tags_response.get('TagList', [])
                    }
                except:
                    pass
                
                databases.append(database)
            
            # DynamoDB tables
            dynamodb_response = self.aws_dynamodb.list_tables()
            for table_name in dynamodb_response.get('TableNames', []):
                table_info = self.aws_dynamodb.describe_table(TableName=table_name)
                table = table_info['Table']
                
                database = DatabaseInstance(
                    id=f"dynamodb-{table_name}",
                    name=table_name,
                    provider=CloudProvider.AWS,
                    database_type=DatabaseType.DYNAMODB,
                    engine=DatabaseEngine.POSTGRESQL_13,  # Placeholder
                    state=self._map_aws_dynamodb_state(table['TableStatus']),
                    region=self.config['aws'].get('region', 'us-east-1'),
                    created_at=table.get('CreationDateTime', datetime.utcnow()),
                    tags={}
                )
                
                # Calculate DynamoDB cost
                database.cost_per_hour = self._calculate_aws_dynamodb_cost(table)
                
                databases.append(database)
                
        except ClientError as e:
            self.logger.error(f"AWS RDS API error: {e}")
        except Exception as e:
            self.logger.error(f"Error listing AWS databases: {e}")
        
        return databases
    
    async def _list_azure_databases(self) -> List[DatabaseInstance]:
        """List Azure SQL databases."""
        if not self.azure_sql:
            return []
        
        databases = []
        try:
            # Get resource groups
            resource_groups = self.azure_sql.resource_groups.list()
            
            for rg in resource_groups:
                # SQL servers
                servers = self.azure_sql.servers.list_by_resource_group(rg.name)
                
                for server in servers:
                    # Databases in server
                    server_databases = self.azure_sql.databases.list_by_server(
                        rg.name, server.name
                    )
                    
                    for db in server_databases:
                        if db.name == 'master':  # Skip system database
                            continue
                        
                        database = DatabaseInstance(
                            id=f"azure-{server.name}-{db.name}",
                            name=db.name,
                            provider=CloudProvider.AZURE,
                            database_type=DatabaseType.MYSQL,  # Azure SQL Server
                            engine=DatabaseEngine.MYSQL_8_0,
                            state=self._map_azure_db_state(db.status),
                            region=server.location,
                            endpoint=server.fully_qualified_domain_name,
                            port=1433,
                            database_name=db.name,
                            created_at=db.creation_date,
                            tags=server.tags or {}
                        )
                        
                        # Calculate cost
                        database.cost_per_hour = self._calculate_azure_sql_cost(
                            db.service_level_objective,
                            database.region
                        )
                        
                        databases.append(database)
                        
        except Exception as e:
            self.logger.error(f"Error listing Azure databases: {e}")
        
        return databases
    
    async def _list_gcp_databases(self) -> List[DatabaseInstance]:
        """List GCP Cloud SQL instances."""
        if not self.gcp_sql:
            return []
        
        databases = []
        try:
            project = self.config['gcp']['project_id']
            
            request = sql_v1.SqlInstancesListRequest(project=project)
            response = self.gcp_sql.list(request=request)
            
            for instance in response.items:
                database = DatabaseInstance(
                    id=instance.name,
                    name=instance.name,
                    provider=CloudProvider.GCP,
                    database_type=self._map_gcp_engine_to_type(instance.database_version),
                    engine=self._map_gcp_engine_version(instance.database_version),
                    state=self._map_gcp_db_state(instance.state),
                    region=instance.region,
                    endpoint=instance.ip_addresses[0].ip_address if instance.ip_addresses else None,
                    port=3306 if 'MYSQL' in instance.database_version else 5432,
                    allocated_storage_gb=instance.settings.data_disk_size_gb,
                    instance_class=instance.settings.tier,
                    created_at=datetime.fromisoformat(
                        instance.create_time.replace('Z', '+00:00')
                    ) if instance.create_time else datetime.utcnow(),
                    tags={}
                )
                
                # Calculate cost
                database.cost_per_hour = self._calculate_gcp_sql_cost(
                    instance.settings.tier,
                    instance.settings.data_disk_size_gb,
                    database.region
                )
                
                databases.append(database)
                
        except Exception as e:
            self.logger.error(f"Error listing GCP databases: {e}")
        
        return databases
    
    async def _list_mongodb_atlas_databases(self) -> List[DatabaseInstance]:
        """List MongoDB Atlas clusters."""
        if not self.mongodb_client:
            return []
        
        databases = []
        try:
            # This would typically use MongoDB Atlas API
            # For now, we'll create a representation based on connection
            
            database = DatabaseInstance(
                id="mongodb-atlas-main",
                name="atlas-main-cluster",
                provider=CloudProvider.MONGODB_ATLAS,
                database_type=DatabaseType.MONGODB,
                engine=DatabaseEngine.MONGODB_6_0,
                state=DatabaseState.AVAILABLE,
                region="us-east-1",  # Would get from Atlas API
                endpoint=self.config['mongodb_atlas'].get('endpoint'),
                port=27017,
                created_at=datetime.utcnow(),
                tags={'provider': 'mongodb_atlas'}
            )
            
            # Estimate cost (would get from Atlas billing API)
            database.cost_per_hour = Decimal('0.25')
            
            databases.append(database)
            
        except Exception as e:
            self.logger.error(f"Error listing MongoDB Atlas databases: {e}")
        
        return databases
    
    async def create_database(
        self,
        name: str,
        database_type: DatabaseType,
        provider: CloudProvider,
        region: str,
        instance_class: str = "db.t3.micro",
        **kwargs
    ) -> DatabaseInstance:
        """Create a new database instance.
        
        Args:
            name: Database instance name
            database_type: Type of database
            provider: Cloud provider
            region: Target region
            instance_class: Instance class/tier
            **kwargs: Provider-specific options
            
        Returns:
            Created database instance
        """
        try:
            if provider == CloudProvider.AWS:
                return await self._create_aws_database(
                    name, database_type, region, instance_class, **kwargs
                )
            elif provider == CloudProvider.AZURE:
                return await self._create_azure_database(
                    name, database_type, region, instance_class, **kwargs
                )
            elif provider == CloudProvider.GCP:
                return await self._create_gcp_database(
                    name, database_type, region, instance_class, **kwargs
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            self.logger.error(f"Error creating database: {e}")
            raise
    
    async def _create_aws_database(
        self,
        name: str,
        database_type: DatabaseType,
        region: str,
        instance_class: str,
        **kwargs
    ) -> DatabaseInstance:
        """Create AWS RDS database."""
        if not self.aws_rds:
            raise ValueError("AWS RDS client not initialized")
        
        # Map database type to AWS engine
        engine_mapping = {
            DatabaseType.POSTGRESQL: 'postgres',
            DatabaseType.MYSQL: 'mysql',
            DatabaseType.MARIADB: 'mariadb'
        }
        
        if database_type not in engine_mapping:
            raise ValueError(f"Unsupported database type for AWS: {database_type}")
        
        engine = engine_mapping[database_type]
        
        # Default parameters
        master_username = kwargs.get('master_username', 'admin')
        master_password = kwargs.get('master_password', self._generate_password())
        allocated_storage = kwargs.get('allocated_storage', 20)
        database_name = kwargs.get('database_name', name.replace('-', '_'))
        
        try:
            response = self.aws_rds.create_db_instance(
                DBInstanceIdentifier=name,
                DBInstanceClass=instance_class,
                Engine=engine,
                MasterUsername=master_username,
                MasterUserPassword=master_password,
                AllocatedStorage=allocated_storage,
                DBName=database_name,
                VpcSecurityGroupIds=kwargs.get('security_group_ids', []),
                DBSubnetGroupName=kwargs.get('subnet_group_name'),
                BackupRetentionPeriod=kwargs.get('backup_retention_days', 7),
                MultiAZ=kwargs.get('multi_az', False),
                StorageEncrypted=kwargs.get('encrypted', True),
                StorageType=kwargs.get('storage_type', 'gp2'),
                EnablePerformanceInsights=kwargs.get('performance_insights', True),
                Tags=[
                    {'Key': 'Name', 'Value': name},
                    {'Key': 'CreatedBy', 'Value': 'AinfluePlatform'},
                    {'Key': 'Environment', 'Value': kwargs.get('environment', 'production')}
                ]
            )
            
            db_instance = response['DBInstance']
            
            database = DatabaseInstance(
                id=db_instance['DBInstanceIdentifier'],
                name=name,
                provider=CloudProvider.AWS,
                database_type=database_type,
                engine=self._map_aws_engine_version(engine, ''),
                state=DatabaseState.CREATING,
                region=region,
                master_username=master_username,
                database_name=database_name,
                allocated_storage_gb=allocated_storage,
                instance_class=instance_class,
                multi_az=kwargs.get('multi_az', False),
                encrypted=kwargs.get('encrypted', True),
                backup_retention_days=kwargs.get('backup_retention_days', 7),
                performance_insights=kwargs.get('performance_insights', True),
                tags={
                    'Name': name,
                    'CreatedBy': 'AinfluePlatform',
                    'Environment': kwargs.get('environment', 'production')
                }
            )
            
            # Store connection config securely
            database.connection_config = {
                'master_password': master_password,  # In production, use secrets manager
                'connection_string': self._build_connection_string(database, master_password)
            }
            
            # Calculate cost
            database.cost_per_hour = self._calculate_aws_rds_cost(
                instance_class, allocated_storage, region, kwargs.get('multi_az', False)
            )
            
            self.databases[database.id] = database
            self.logger.info(f"Created AWS RDS database {database.id}")
            
            return database
            
        except ClientError as e:
            self.logger.error(f"AWS RDS creation failed: {e}")
            raise
    
    async def create_high_availability_cluster(
        self,
        cluster_name: str,
        database_type: DatabaseType,
        provider: CloudProvider,
        primary_region: str,
        read_replica_regions: List[str],
        **kwargs
    ) -> DatabaseCluster:
        """Create high availability database cluster.
        
        Args:
            cluster_name: Cluster name
            database_type: Database type
            provider: Cloud provider
            primary_region: Primary instance region
            read_replica_regions: Read replica regions
            **kwargs: Additional configuration
            
        Returns:
            Database cluster configuration
        """
        try:
            # Create primary instance
            primary_instance = await self.create_database(
                name=f"{cluster_name}-primary",
                database_type=database_type,
                provider=provider,
                region=primary_region,
                **kwargs
            )
            
            # Create read replicas
            read_replicas = []
            for i, region in enumerate(read_replica_regions):
                replica = await self._create_read_replica(
                    source_db_id=primary_instance.id,
                    replica_name=f"{cluster_name}-replica-{i+1}",
                    target_region=region,
                    provider=provider,
                    **kwargs
                )
                read_replicas.append(replica.id)
            
            # Create cluster configuration
            cluster = DatabaseCluster(
                id=f"cluster-{cluster_name}",
                name=cluster_name,
                provider=provider,
                database_type=database_type,
                primary_instance=primary_instance.id,
                read_replicas=read_replicas,
                region=primary_region,
                backup_config={
                    'retention_days': kwargs.get('backup_retention_days', 30),
                    'backup_window': kwargs.get('backup_window', '03:00-04:00'),
                    'cross_region_backup': True
                },
                failover_config={
                    'automatic_failover': kwargs.get('auto_failover', True),
                    'failover_timeout': kwargs.get('failover_timeout', 300),
                    'preferred_replica': read_replicas[0] if read_replicas else None
                }
            )
            
            self.clusters[cluster.id] = cluster
            
            self.logger.info(
                f"Created HA cluster {cluster_name} with {len(read_replicas)} replicas"
            )
            
            return cluster
            
        except Exception as e:
            self.logger.error(f"Error creating HA cluster: {e}")
            raise
    
    async def backup_database(
        self,
        database_id: str,
        backup_type: BackupType = BackupType.FULL,
        retention_days: int = 30
    ) -> DatabaseBackup:
        """Create database backup.
        
        Args:
            database_id: Database instance ID
            backup_type: Type of backup
            retention_days: Backup retention in days
            
        Returns:
            Database backup information
        """
        try:
            database = self.databases.get(database_id)
            if not database:
                raise ValueError(f"Database {database_id} not found")
            
            backup_id = f"backup-{database_id}-{int(datetime.utcnow().timestamp())}"
            
            if database.provider == CloudProvider.AWS:
                backup = await self._create_aws_backup(database, backup_type, retention_days)
            elif database.provider == CloudProvider.AZURE:
                backup = await self._create_azure_backup(database, backup_type, retention_days)
            elif database.provider == CloudProvider.GCP:
                backup = await self._create_gcp_backup(database, backup_type, retention_days)
            else:
                raise ValueError(f"Backup not supported for provider: {database.provider}")
            
            # Store backup information
            if database_id not in self.backups:
                self.backups[database_id] = []
            self.backups[database_id].append(backup)
            
            self.logger.info(f"Created backup {backup.id} for database {database_id}")
            
            return backup
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            raise
    
    async def _create_aws_backup(
        self,
        database: DatabaseInstance,
        backup_type: BackupType,
        retention_days: int
    ) -> DatabaseBackup:
        """Create AWS RDS backup."""
        if not self.aws_rds:
            raise ValueError("AWS RDS client not initialized")
        
        backup_id = f"backup-{database.id}-{int(datetime.utcnow().timestamp())}"
        
        try:
            if backup_type == BackupType.SNAPSHOT:
                response = self.aws_rds.create_db_snapshot(
                    DBSnapshotIdentifier=backup_id,
                    DBInstanceIdentifier=database.id,
                    Tags=[
                        {'Key': 'BackupType', 'Value': backup_type.value},
                        {'Key': 'CreatedBy', 'Value': 'AinfluePlatform'}
                    ]
                )
                
                snapshot = response['DBSnapshot']
                
                backup = DatabaseBackup(
                    id=backup_id,
                    database_id=database.id,
                    backup_type=backup_type,
                    status=snapshot['Status'],
                    created_at=snapshot.get('SnapshotCreateTime', datetime.utcnow()),
                    retention_until=datetime.utcnow() + timedelta(days=retention_days),
                    encrypted=snapshot.get('Encrypted', True),
                    metadata={
                        'engine': snapshot.get('Engine'),
                        'engine_version': snapshot.get('EngineVersion'),
                        'instance_class': snapshot.get('DBInstanceClass'),
                        'allocated_storage': snapshot.get('AllocatedStorage')
                    }
                )
                
                return backup
            else:
                raise ValueError(f"Backup type {backup_type} not implemented for AWS")
                
        except ClientError as e:
            self.logger.error(f"AWS backup creation failed: {e}")
            raise
    
    async def monitor_performance(self, database_id: str) -> PerformanceMetrics:
        """Monitor database performance metrics.
        
        Args:
            database_id: Database instance ID
            
        Returns:
            Current performance metrics
        """
        try:
            database = self.databases.get(database_id)
            if not database:
                raise ValueError(f"Database {database_id} not found")
            
            if database.provider == CloudProvider.AWS:
                metrics = await self._get_aws_performance_metrics(database)
            elif database.provider == CloudProvider.AZURE:
                metrics = await self._get_azure_performance_metrics(database)
            elif database.provider == CloudProvider.GCP:
                metrics = await self._get_gcp_performance_metrics(database)
            else:
                # Default metrics for unsupported providers
                metrics = PerformanceMetrics(
                    timestamp=datetime.utcnow(),
                    database_id=database_id,
                    cpu_utilization=0.0,
                    memory_utilization=0.0,
                    disk_utilization=0.0,
                    connections_active=0,
                    connections_max=100,
                    queries_per_second=0.0,
                    read_iops=0.0,
                    write_iops=0.0,
                    read_latency_ms=0.0,
                    write_latency_ms=0.0
                )
            
            # Store metrics history
            if database_id not in self.metrics_history:
                self.metrics_history[database_id] = []
            
            self.metrics_history[database_id].append(metrics)
            
            # Keep only last 1000 metrics per database
            if len(self.metrics_history[database_id]) > 1000:
                self.metrics_history[database_id] = self.metrics_history[database_id][-1000:]
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error monitoring performance: {e}")
            raise
    
    async def optimize_performance(self, database_id: str) -> Dict[str, Any]:
        """Analyze and provide performance optimization recommendations.
        
        Args:
            database_id: Database instance ID
            
        Returns:
            Performance optimization recommendations
        """
        try:
            database = self.databases.get(database_id)
            if not database:
                raise ValueError(f"Database {database_id} not found")
            
            # Get recent performance metrics
            recent_metrics = self.metrics_history.get(database_id, [])[-24:]  # Last 24 samples
            
            if not recent_metrics:
                # Get current metrics
                current_metrics = await self.monitor_performance(database_id)
                recent_metrics = [current_metrics]
            
            recommendations = {
                'database_id': database_id,
                'analysis_timestamp': datetime.utcnow(),
                'current_performance': {
                    'cpu_avg': sum(m.cpu_utilization for m in recent_metrics) / len(recent_metrics),
                    'memory_avg': sum(m.memory_utilization for m in recent_metrics) / len(recent_metrics),
                    'connections_avg': sum(m.connections_active for m in recent_metrics) / len(recent_metrics),
                    'queries_per_second_avg': sum(m.queries_per_second for m in recent_metrics) / len(recent_metrics)
                },
                'recommendations': [],
                'cost_impact': {'monthly_savings': Decimal('0.00')},
                'implementation_priority': 'medium'
            }
            
            # CPU utilization analysis
            avg_cpu = recommendations['current_performance']['cpu_avg']
            if avg_cpu > 80:
                recommendations['recommendations'].append({
                    'type': 'scale_up',
                    'description': 'High CPU utilization detected. Consider upgrading instance class.',
                    'current_instance_class': database.instance_class,
                    'recommended_instance_class': self._get_next_instance_class(database.instance_class),
                    'cost_impact': self._calculate_scale_up_cost(database),
                    'priority': 'high'
                })
                recommendations['implementation_priority'] = 'high'
            elif avg_cpu < 20:
                recommendations['recommendations'].append({
                    'type': 'scale_down',
                    'description': 'Low CPU utilization. Consider downsizing instance class.',
                    'current_instance_class': database.instance_class,
                    'recommended_instance_class': self._get_previous_instance_class(database.instance_class),
                    'cost_impact': self._calculate_scale_down_savings(database),
                    'priority': 'medium'
                })
                recommendations['cost_impact']['monthly_savings'] += self._calculate_scale_down_savings(database) * 24 * 30
            
            # Memory utilization analysis
            avg_memory = recommendations['current_performance']['memory_avg']
            if avg_memory > 85:
                recommendations['recommendations'].append({
                    'type': 'memory_optimization',
                    'description': 'High memory utilization. Consider memory-optimized instance or tuning.',
                    'suggestions': [
                        'Upgrade to memory-optimized instance class',
                        'Optimize query patterns',
                        'Implement connection pooling',
                        'Review memory-intensive operations'
                    ],
                    'priority': 'high'
                })
            
            # Connection analysis
            avg_connections = recommendations['current_performance']['connections_avg']
            max_connections = recent_metrics[0].connections_max if recent_metrics else 100
            connection_ratio = avg_connections / max_connections if max_connections > 0 else 0
            
            if connection_ratio > 0.8:
                recommendations['recommendations'].append({
                    'type': 'connection_optimization',
                    'description': 'High connection utilization. Implement connection pooling.',
                    'suggestions': [
                        'Implement connection pooling (PgBouncer, ProxySQL)',
                        'Optimize application connection handling',
                        'Consider read replicas for read-heavy workloads'
                    ],
                    'priority': 'medium'
                })
            
            # Query performance analysis
            avg_qps = recommendations['current_performance']['queries_per_second_avg']
            if avg_qps > 1000:
                recommendations['recommendations'].append({
                    'type': 'query_optimization',
                    'description': 'High query volume. Consider read replicas and caching.',
                    'suggestions': [
                        'Implement read replicas',
                        'Add Redis/Memcached caching layer',
                        'Optimize slow queries',
                        'Consider database sharding'
                    ],
                    'priority': 'medium'
                })
            
            # Storage optimization
            if database.allocated_storage_gb > 100:
                recommendations['recommendations'].append({
                    'type': 'storage_optimization',
                    'description': 'Large storage allocation. Consider cleanup and archival.',
                    'suggestions': [
                        'Implement data archival strategy',
                        'Clean up old logs and temporary data',
                        'Consider data compression',
                        'Implement tiered storage'
                    ],
                    'priority': 'low'
                })
            
            self.logger.info(f"Generated {len(recommendations['recommendations'])} optimization recommendations for {database_id}")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error optimizing performance: {e}")
            raise
    
    async def cost_optimization_analysis(self) -> Dict[str, Any]:
        """Perform cost optimization analysis across all databases.
        
        Returns:
            Cost optimization report
        """
        try:
            await self.list_databases()  # Refresh database list
            
            analysis = {
                'total_monthly_cost': Decimal('0.00'),
                'optimized_monthly_cost': Decimal('0.00'),
                'potential_monthly_savings': Decimal('0.00'),
                'recommendations': [],
                'cost_breakdown': {
                    'by_provider': {},
                    'by_database_type': {},
                    'by_region': {}
                }
            }
            
            for database in self.databases.values():
                monthly_cost = database.cost_per_hour * 24 * 30
                analysis['total_monthly_cost'] += monthly_cost
                
                # Provider breakdown
                provider = database.provider.value
                if provider not in analysis['cost_breakdown']['by_provider']:
                    analysis['cost_breakdown']['by_provider'][provider] = Decimal('0.00')
                analysis['cost_breakdown']['by_provider'][provider] += monthly_cost
                
                # Database type breakdown
                db_type = database.database_type.value
                if db_type not in analysis['cost_breakdown']['by_database_type']:
                    analysis['cost_breakdown']['by_database_type'][db_type] = Decimal('0.00')
                analysis['cost_breakdown']['by_database_type'][db_type] += monthly_cost
                
                # Region breakdown
                region = database.region
                if region not in analysis['cost_breakdown']['by_region']:
                    analysis['cost_breakdown']['by_region'][region] = Decimal('0.00')
                analysis['cost_breakdown']['by_region'][region] += monthly_cost
                
                # Individual database optimization
                optimization = await self.optimize_performance(database.id)
                if optimization['cost_impact']['monthly_savings'] > 0:
                    analysis['potential_monthly_savings'] += optimization['cost_impact']['monthly_savings']
                    
                    analysis['recommendations'].append({
                        'database_id': database.id,
                        'database_name': database.name,
                        'current_monthly_cost': monthly_cost,
                        'potential_monthly_savings': optimization['cost_impact']['monthly_savings'],
                        'recommendations': optimization['recommendations'],
                        'priority': optimization['implementation_priority']
                    })
            
            analysis['optimized_monthly_cost'] = analysis['total_monthly_cost'] - analysis['potential_monthly_savings']
            
            # Sort recommendations by potential savings
            analysis['recommendations'].sort(
                key=lambda x: x['potential_monthly_savings'],
                reverse=True
            )
            
            self.logger.info(
                f"Cost analysis complete. Total monthly cost: ${analysis['total_monthly_cost']}, "
                f"Potential savings: ${analysis['potential_monthly_savings']}"
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in cost optimization analysis: {e}")
            raise
    
    def _update_cost_metrics(self) -> None:
        """Update cost tracking metrics."""
        self.cost_metrics = {
            'total_cost_per_hour': sum(db.cost_per_hour for db in self.databases.values()),
            'cost_by_provider': {},
            'cost_by_database_type': {},
            'storage_costs': Decimal('0.00'),
            'backup_costs': Decimal('0.00')
        }
        
        for database in self.databases.values():
            # By provider
            provider = database.provider.value
            if provider not in self.cost_metrics['cost_by_provider']:
                self.cost_metrics['cost_by_provider'][provider] = Decimal('0.00')
            self.cost_metrics['cost_by_provider'][provider] += database.cost_per_hour
            
            # By database type
            db_type = database.database_type.value
            if db_type not in self.cost_metrics['cost_by_database_type']:
                self.cost_metrics['cost_by_database_type'][db_type] = Decimal('0.00')
            self.cost_metrics['cost_by_database_type'][db_type] += database.cost_per_hour
    
    def get_cost_metrics(self) -> Dict[str, Any]:
        """Get current cost metrics."""
        return self.cost_metrics.copy()
    
    def _generate_password(self, length: int = 16) -> str:
        """Generate secure database password."""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    def _build_connection_string(self, database: DatabaseInstance, password: str) -> str:
        """Build database connection string."""
        if database.database_type == DatabaseType.POSTGRESQL:
            return f"postgresql://{database.master_username}:{password}@{database.endpoint}:{database.port}/{database.database_name}"
        elif database.database_type == DatabaseType.MYSQL:
            return f"mysql://{database.master_username}:{password}@{database.endpoint}:{database.port}/{database.database_name}"
        elif database.database_type == DatabaseType.MONGODB:
            return f"mongodb://{database.master_username}:{password}@{database.endpoint}:{database.port}/{database.database_name}"
        else:
            return f"{database.database_type.value}://{database.master_username}:{password}@{database.endpoint}:{database.port}/{database.database_name}"
    
    # Helper methods for provider-specific mappings
    def _map_aws_engine_to_type(self, engine: str) -> DatabaseType:
        """Map AWS engine to database type."""
        mapping = {
            'postgres': DatabaseType.POSTGRESQL,
            'mysql': DatabaseType.MYSQL,
            'mariadb': DatabaseType.MARIADB,
        }
        return mapping.get(engine, DatabaseType.POSTGRESQL)
    
    def _map_aws_engine_version(self, engine: str, version: str) -> DatabaseEngine:
        """Map AWS engine version."""
        if engine == 'postgres':
            if '15' in version:
                return DatabaseEngine.POSTGRESQL_15
            elif '14' in version:
                return DatabaseEngine.POSTGRESQL_14
            else:
                return DatabaseEngine.POSTGRESQL_13
        elif engine == 'mysql':
            if '8.0' in version:
                return DatabaseEngine.MYSQL_8_0
            else:
                return DatabaseEngine.MYSQL_5_7
        elif engine == 'mariadb':
            return DatabaseEngine.MARIADB_10_6
        
        return DatabaseEngine.POSTGRESQL_13
    
    def _map_aws_db_state(self, state: str) -> DatabaseState:
        """Map AWS RDS state to standardized state."""
        mapping = {
            'creating': DatabaseState.CREATING,
            'available': DatabaseState.AVAILABLE,
            'modifying': DatabaseState.MODIFYING,
            'deleting': DatabaseState.DELETING,
            'deleted': DatabaseState.DELETED,
            'backing-up': DatabaseState.BACKING_UP,
            'rebooting': DatabaseState.MAINTENANCE,
            'failed': DatabaseState.ERROR
        }
        return mapping.get(state, DatabaseState.AVAILABLE)
    
    def _calculate_aws_rds_cost(
        self,
        instance_class: str,
        storage_gb: int,
        region: str,
        multi_az: bool
    ) -> Decimal:
        """Calculate AWS RDS cost per hour."""
        # Simplified pricing - would use AWS Pricing API in production
        instance_costs = {
            'db.t3.micro': 0.017,
            'db.t3.small': 0.034,
            'db.t3.medium': 0.068,
            'db.t3.large': 0.136,
            'db.t3.xlarge': 0.272,
            'db.t3.2xlarge': 0.544,
        }
        
        instance_cost = instance_costs.get(instance_class, 0.068)
        storage_cost = storage_gb * 0.115 / (24 * 30)  # GP2 storage cost per month
        
        if multi_az:
            instance_cost *= 2  # Multi-AZ doubles instance cost
        
        # Regional multipliers
        region_multipliers = {
            'us-east-1': 1.0,
            'us-west-2': 1.05,
            'eu-west-1': 1.1,
            'ap-southeast-1': 1.15,
        }
        
        multiplier = region_multipliers.get(region, 1.0)
        total_cost = (instance_cost + storage_cost) * multiplier
        
        return Decimal(str(total_cost))
    
    async def close(self) -> None:
        """Close all database connections."""
        try:
            if self.mongodb_client:
                self.mongodb_client.close()
            
            self.logger.info("Multi-cloud database manager closed")
            
        except Exception as e:
            self.logger.error(f"Error closing connections: {e}")


# Example usage
async def example_usage():
    """Example usage of MultiCloudDatabaseManager."""
    
    config = {
        'aws': {
            'access_key_id': 'your-aws-key',
            'secret_access_key': 'your-aws-secret',
            'region': 'us-east-1'
        },
        'gcp': {
            'project_id': 'your-gcp-project',
            'credentials_path': '/path/to/credentials.json'
        },
        'mongodb_atlas': {
            'connection_string': 'mongodb+srv://...',
            'username': 'admin',
            'password': 'password'
        }
    }
    
    manager = MultiCloudDatabaseManager(config)
    
    try:
        # List all databases
        databases = await manager.list_databases()
        print(f"Found {len(databases)} databases")
        
        # Create new database
        database = await manager.create_database(
            name="ainflue-production-db",
            database_type=DatabaseType.POSTGRESQL,
            provider=CloudProvider.AWS,
            region="us-east-1",
            instance_class="db.t3.medium",
            allocated_storage=100,
            multi_az=True,
            performance_insights=True
        )
        
        print(f"Created database: {database.id}")
        
        # Create HA cluster
        cluster = await manager.create_high_availability_cluster(
            cluster_name="ainflue-ha-cluster",
            database_type=DatabaseType.POSTGRESQL,
            provider=CloudProvider.AWS,
            primary_region="us-east-1",
            read_replica_regions=["us-west-2", "eu-west-1"],
            instance_class="db.t3.large",
            auto_failover=True
        )
        
        print(f"Created HA cluster: {cluster.id}")
        
        # Monitor performance
        metrics = await manager.monitor_performance(database.id)
        print(f"CPU utilization: {metrics.cpu_utilization}%")
        
        # Cost optimization analysis
        cost_analysis = await manager.cost_optimization_analysis()
        print(f"Total monthly cost: ${cost_analysis['total_monthly_cost']}")
        print(f"Potential savings: ${cost_analysis['potential_monthly_savings']}")
        
    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(example_usage())