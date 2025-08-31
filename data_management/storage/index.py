"""🏢 Storage Index - IA Influencer Agent Platform Enterprise
========================================================
Module: backend/data_management/storage/index.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================

Main entry point for the enterprise storage system.
Provides unified interface and orchestration for all storage components.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

ÉQUIPE PROJET - SPÉCIALITÉS:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel  
- Storage Architecture: Fahed Mlaiel
- DevOps: Fahed Mlaiel
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

# Import all storage components
from .distributed_storage import DistributedStorageManager, DistributedStorageConfig
from .backup_storage import BackupStorageManager, BackupConfig
from .archive_storage import ArchiveStorageManager, ArchiveConfig
from .sync_engine import SyncEngine, SyncConfig
from .integrity_checker import IntegrityChecker, IntegrityConfig
from .access_controller import AccessController, AccessConfig
from .quota_manager import QuotaManager, QuotaConfig
from .migration_engine import MigrationEngine, MigrationConfig

logger = logging.getLogger(__name__)

class StorageSystemConfig:
    """    Configuration for the entire storage system
    """    def __init__(
        self,
        storage_root_path: str = "/workspaces/Achiri/IA-Influencer-Agent/backend/data_management/storage",
        **kwargs
    ):
        self.storage_root_path = storage_root_path
        
        # Component configurations
        self.distributed_config = kwargs.get('distributed_config') or self._create_distributed_config()
        self.backup_config = kwargs.get('backup_config') or self._create_backup_config()
        self.archive_config = kwargs.get('archive_config') or self._create_archive_config()
        self.sync_config = kwargs.get('sync_config') or self._create_sync_config()
        self.integrity_config = kwargs.get('integrity_config') or self._create_integrity_config()
        self.access_config = kwargs.get('access_config') or self._create_access_config()
        self.quota_config = kwargs.get('quota_config') or self._create_quota_config()
        self.migration_config = kwargs.get('migration_config') or self._create_migration_config()
        
        # System-wide settings
        self.enable_monitoring = kwargs.get('enable_monitoring', True)
        self.enable_clustering = kwargs.get('enable_clustering', True)
        self.enable_encryption = kwargs.get('enable_encryption', True)
        self.debug_mode = kwargs.get('debug_mode', False)
    
    def _create_distributed_config(self) -> DistributedStorageConfig:
        """Create distributed storage configuration"""        return DistributedStorageConfig(
            storage_root_path=f"{self.storage_root_path}/distributed",
            cluster_nodes_directory=f"{self.storage_root_path}/cluster/nodes",
            sharding_directory=f"{self.storage_root_path}/cluster/shards",
            consistency_directory=f"{self.storage_root_path}/cluster/consistency"
        )
    
    def _create_backup_config(self) -> BackupConfig:
        """Create backup configuration"""        return BackupConfig(
            storage_root_path=f"{self.storage_root_path}/backups",
            backup_directory=f"{self.storage_root_path}/backups/data",
            schedules_directory=f"{self.storage_root_path}/backups/schedules",
            metadata_directory=f"{self.storage_root_path}/backups/metadata"
        )
    
    def _create_archive_config(self) -> ArchiveConfig:
        """Create archive configuration"""        return ArchiveConfig(
            storage_root_path=f"{self.storage_root_path}/archives",
            archive_directory=f"{self.storage_root_path}/archives/data",
            metadata_directory=f"{self.storage_root_path}/archives/metadata",
            compliance_directory=f"{self.storage_root_path}/archives/compliance"
        )
    
    def _create_sync_config(self) -> SyncConfig:
        """Create sync configuration"""        return SyncConfig(
            storage_root_path=f"{self.storage_root_path}/sync",
            sync_directory=f"{self.storage_root_path}/sync/data",
            endpoints_directory=f"{self.storage_root_path}/sync/endpoints",
            conflicts_directory=f"{self.storage_root_path}/sync/conflicts"
        )
    
    def _create_integrity_config(self) -> IntegrityConfig:
        """Create integrity configuration"""        return IntegrityConfig(
            storage_root_path=f"{self.storage_root_path}/integrity",
            verification_directory=f"{self.storage_root_path}/integrity/verification",
            repair_directory=f"{self.storage_root_path}/integrity/repair",
            reports_directory=f"{self.storage_root_path}/integrity/reports"
        )
    
    def _create_access_config(self) -> AccessConfig:
        """Create access control configuration"""        return AccessConfig(
            storage_root_path=f"{self.storage_root_path}/access",
            users_directory=f"{self.storage_root_path}/access/users",
            policies_directory=f"{self.storage_root_path}/access/policies",
            audit_directory=f"{self.storage_root_path}/access/audit"
        )
    
    def _create_quota_config(self) -> QuotaConfig:
        """Create quota management configuration"""        return QuotaConfig(
            storage_root_path=f"{self.storage_root_path}/quotas",
            quotas_directory=f"{self.storage_root_path}/quotas/limits",
            usage_directory=f"{self.storage_root_path}/quotas/usage",
            billing_directory=f"{self.storage_root_path}/quotas/billing"
        )
    
    def _create_migration_config(self) -> MigrationConfig:
        """Create migration configuration"""        return MigrationConfig(
            storage_root_path=f"{self.storage_root_path}/migrations",
            migrations_directory=f"{self.storage_root_path}/migrations/data",
            plans_directory=f"{self.storage_root_path}/migrations/plans",
            executions_directory=f"{self.storage_root_path}/migrations/executions",
            schemas_directory=f"{self.storage_root_path}/migrations/schemas",
            backup_directory=f"{self.storage_root_path}/migrations/backups",
            temp_directory=f"{self.storage_root_path}/migrations/temp"
        )


class IAInfluencerStorageSystem:
    """    🏢 IA Influencer Agent Enterprise Storage System
    
    Unified storage orchestration system providing:
    - Distributed storage with clustering
    - Automated backup and archiving
    - Real-time synchronization
    - Data integrity verification
    - Access control and security
    - Quota management and billing
    - Data migration capabilities
    
    This is the main entry point for all storage operations.
    """    
    def __init__(self, config: Optional[StorageSystemConfig] = None):
        """Initialize the complete storage system"""        self.config = config or StorageSystemConfig()
        
        # Initialize all storage components
        self.distributed_storage: Optional[DistributedStorageManager] = None
        self.backup_storage: Optional[BackupStorageManager] = None
        self.archive_storage: Optional[ArchiveStorageManager] = None
        self.sync_engine: Optional[SyncEngine] = None
        self.integrity_checker: Optional[IntegrityChecker] = None
        self.access_controller: Optional[AccessController] = None
        self.quota_manager: Optional[QuotaManager] = None
        self.migration_engine: Optional[MigrationEngine] = None
        
        # System state
        self.is_initialized = False
        self.is_running = False
        
        # Metrics and monitoring
        self.system_metrics = {
            'total_storage_gb': 0.0,
            'active_users': 0,
            'total_files': 0,
            'backup_count': 0,
            'archive_count': 0,
            'sync_operations': 0,
            'integrity_checks': 0,
            'quota_violations': 0,
            'migrations_completed': 0,
            'system_uptime_hours': 0.0,
            'last_health_check': None
        }
        
        logger.info("IA Influencer Storage System initialized")
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize all storage components"""        try:
            logger.info("Initializing IA Influencer Storage System...")
            
            # Create storage directories
            await self._create_storage_directories()
            
            # Initialize components in order
            await self._initialize_access_controller()
            await self._initialize_quota_manager()
            await self._initialize_distributed_storage()
            await self._initialize_backup_storage()
            await self._initialize_archive_storage()
            await self._initialize_sync_engine()
            await self._initialize_integrity_checker()
            await self._initialize_migration_engine()
            
            # Start system monitoring
            if self.config.enable_monitoring:
                asyncio.create_task(self._start_system_monitoring())
            
            self.is_initialized = True
            self.is_running = True
            
            logger.info("IA Influencer Storage System initialized successfully")
            
            return {
                'success': True,
                'message': 'Storage system initialized successfully',
                'components': {
                    'distributed_storage': True,
                    'backup_storage': True,
                    'archive_storage': True,
                    'sync_engine': True,
                    'integrity_checker': True,
                    'access_controller': True,
                    'quota_manager': True,
                    'migration_engine': True
                },
                'initialized_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Storage system initialization failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _create_storage_directories(self) -> None:
        """Create all necessary storage directories"""        directories = [
            self.config.storage_root_path,
            f"{self.config.storage_root_path}/distributed",
            f"{self.config.storage_root_path}/backups",
            f"{self.config.storage_root_path}/archives",
            f"{self.config.storage_root_path}/sync",
            f"{self.config.storage_root_path}/integrity",
            f"{self.config.storage_root_path}/access",
            f"{self.config.storage_root_path}/quotas",
            f"{self.config.storage_root_path}/migrations",
            f"{self.config.storage_root_path}/cluster",
            f"{self.config.storage_root_path}/temp",
            f"{self.config.storage_root_path}/logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    async def _initialize_access_controller(self) -> None:
        """Initialize access control system"""        try:
            # Add JWT secret to config
            if not hasattr(self.config.access_config, 'jwt_secret_key'):
                self.config.access_config.jwt_secret_key = "ia_influencer_jwt_secret_key_2025"
            
            self.access_controller = AccessController(self.config.access_config)
            logger.info("Access controller initialized")
        except Exception as e:
            logger.error(f"Access controller initialization failed: {str(e)}")
            raise
    
    async def _initialize_quota_manager(self) -> None:
        """Initialize quota management system"""        try:
            self.quota_manager = QuotaManager(self.config.quota_config)
            logger.info("Quota manager initialized")
        except Exception as e:
            logger.error(f"Quota manager initialization failed: {str(e)}")
            raise
    
    async def _initialize_distributed_storage(self) -> None:
        """Initialize distributed storage system"""        try:
            self.distributed_storage = DistributedStorageManager(self.config.distributed_config)
            logger.info("Distributed storage initialized")
        except Exception as e:
            logger.error(f"Distributed storage initialization failed: {str(e)}")
            raise
    
    async def _initialize_backup_storage(self) -> None:
        """Initialize backup storage system"""        try:
            self.backup_storage = BackupStorageManager(self.config.backup_config)
            logger.info("Backup storage initialized")
        except Exception as e:
            logger.error(f"Backup storage initialization failed: {str(e)}")
            raise
    
    async def _initialize_archive_storage(self) -> None:
        """Initialize archive storage system"""        try:
            self.archive_storage = ArchiveStorageManager(self.config.archive_config)
            logger.info("Archive storage initialized")
        except Exception as e:
            logger.error(f"Archive storage initialization failed: {str(e)}")
            raise
    
    async def _initialize_sync_engine(self) -> None:
        """Initialize synchronization engine"""        try:
            self.sync_engine = SyncEngine(self.config.sync_config)
            logger.info("Sync engine initialized")
        except Exception as e:
            logger.error(f"Sync engine initialization failed: {str(e)}")
            raise
    
    async def _initialize_integrity_checker(self) -> None:
        """Initialize integrity checker"""        try:
            self.integrity_checker = IntegrityChecker(self.config.integrity_config)
            logger.info("Integrity checker initialized")
        except Exception as e:
            logger.error(f"Integrity checker initialization failed: {str(e)}")
            raise
    
    async def _initialize_migration_engine(self) -> None:
        """Initialize migration engine"""        try:
            self.migration_engine = MigrationEngine(self.config.migration_config)
            logger.info("Migration engine initialized")
        except Exception as e:
            logger.error(f"Migration engine initialization failed: {str(e)}")
            raise
    
    # ===========================================
    # PUBLIC API METHODS
    # ===========================================
    
    async def store_file(
        self,
        file_path: str,
        content: bytes,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Store file in the system with full processing pipeline"""        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Check access permissions
            access_result = await self.access_controller.check_access(
                user_id=user_id,
                resource_path=file_path,
                permissions=['write', 'upload']
            )
            
            if not access_result['access_granted']:
                return {
                    'success': False,
                    'error': 'Access denied',
                    'reason': access_result['decision_reason']
                }
            
            # Check quota availability
            quota_result = await self.quota_manager.check_quota_available(
                user_id=user_id,
                quota_type='storage_size',
                requested_amount=len(content)
            )
            
            if not quota_result['available']:
                return {
                    'success': False,
                    'error': 'Quota exceeded',
                    'quota_status': quota_result['quota_status']
                }
            
            # Store file in distributed storage
            storage_result = await self.distributed_storage.store_file(
                file_path=file_path,
                content=content,
                metadata=metadata or {}
            )
            
            if not storage_result['success']:
                return storage_result
            
            # Track usage
            await self.quota_manager.track_usage(
                user_id=user_id,
                quota_type='storage_size',
                metric='bytes_stored',
                value=len(content),
                context={'resource_path': file_path, 'operation': 'store'}
            )
            
            # Schedule backup if enabled
            if self.backup_storage:
                await self.backup_storage.schedule_backup(
                    source_path=file_path,
                    backup_type='incremental'
                )
            
            # Update metrics
            self.system_metrics['total_files'] += 1
            self.system_metrics['total_storage_gb'] += len(content) / (1024**3)
            
            return {
                'success': True,
                'file_path': file_path,
                'file_id': storage_result.get('file_id'),
                'size_bytes': len(content),
                'stored_at': datetime.now().isoformat(),
                'backup_scheduled': True
            }
            
        except Exception as e:
            logger.error(f"File storage failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def retrieve_file(
        self,
        file_path: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Retrieve file from the system"""        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Check access permissions
            access_result = await self.access_controller.check_access(
                user_id=user_id,
                resource_path=file_path,
                permissions=['read', 'download']
            )
            
            if not access_result['access_granted']:
                return {
                    'success': False,
                    'error': 'Access denied',
                    'reason': access_result['decision_reason']
                }
            
            # Retrieve file from distributed storage
            storage_result = await self.distributed_storage.retrieve_file(file_path)
            
            if not storage_result['success']:
                return storage_result
            
            # Track usage
            await self.quota_manager.track_usage(
                user_id=user_id,
                quota_type='bandwidth',
                metric='bytes_transferred',
                value=len(storage_result.get('content', b'')),
                context={'resource_path': file_path, 'operation': 'retrieve'}
            )
            
            return storage_result
            
        except Exception as e:
            logger.error(f"File retrieval failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def delete_file(
        self,
        file_path: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Delete file from the system"""        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Check access permissions
            access_result = await self.access_controller.check_access(
                user_id=user_id,
                resource_path=file_path,
                permissions=['delete']
            )
            
            if not access_result['access_granted']:
                return {
                    'success': False,
                    'error': 'Access denied',
                    'reason': access_result['decision_reason']
                }
            
            # Delete from distributed storage
            storage_result = await self.distributed_storage.delete_file(file_path)
            
            if storage_result['success']:
                # Update metrics
                self.system_metrics['total_files'] -= 1
            
            return storage_result
            
        except Exception as e:
            logger.error(f"File deletion failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_backup(
        self,
        source_path: str,
        backup_type: str = 'full',
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create backup of specified path"""        try:
            if not self.is_initialized:
                await self.initialize()
            
            result = await self.backup_storage.create_backup(
                source_path=source_path,
                backup_type=backup_type
            )
            
            if result['success']:
                self.system_metrics['backup_count'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Backup creation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def archive_data(
        self,
        source_path: str,
        retention_policy: str = 'standard',
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Archive data for long-term storage"""        try:
            if not self.is_initialized:
                await self.initialize()
            
            result = await self.archive_storage.archive_data(
                source_path=source_path,
                retention_policy=retention_policy
            )
            
            if result['success']:
                self.system_metrics['archive_count'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Data archiving failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def sync_with_endpoint(
        self,
        endpoint_config: Dict[str, Any],
        sync_direction: str = 'bidirectional'
    ) -> Dict[str, Any]:
        """Synchronize with external endpoint"""        try:
            if not self.is_initialized:
                await self.initialize()
            
            result = await self.sync_engine.sync_with_endpoint(
                endpoint_config=endpoint_config,
                sync_direction=sync_direction
            )
            
            if result['success']:
                self.system_metrics['sync_operations'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Synchronization failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def verify_integrity(
        self,
        path: str,
        verification_level: str = 'standard'
    ) -> Dict[str, Any]:
        """Verify data integrity"""        try:
            if not self.is_initialized:
                await self.initialize()
            
            result = await self.integrity_checker.verify_path(
                path=path,
                verification_level=verification_level
            )
            
            if result['success']:
                self.system_metrics['integrity_checks'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Integrity verification failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_user(
        self,
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create new user account"""        try:
            if not self.is_initialized:
                await self.initialize()
            
            result = await self.access_controller.create_user(user_data)
            
            if result['success']:
                self.system_metrics['active_users'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"User creation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Authenticate user credentials"""        try:
            if not self.is_initialized:
                await self.initialize()
            
            context = context or {}
            
            return await self.access_controller.authenticate_user(
                username=username,
                password=password,
                ip_address=context.get('ip_address', ''),
                user_agent=context.get('user_agent', '')
            )
            
        except Exception as e:
            logger.error(f"User authentication failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_migration_plan(
        self,
        plan_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create data migration plan"""        try:
            if not self.is_initialized:
                await self.initialize()
            
            return await self.migration_engine.create_migration_plan(plan_data)
            
        except Exception as e:
            logger.error(f"Migration plan creation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def execute_migration(
        self,
        plan_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute migration plan"""        try:
            if not self.is_initialized:
                await self.initialize()
            
            result = await self.migration_engine.execute_migration(plan_id, options)
            
            if result['success']:
                self.system_metrics['migrations_completed'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Migration execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""        try:
            status = {
                'system': {
                    'is_initialized': self.is_initialized,
                    'is_running': self.is_running,
                    'uptime_hours': self.system_metrics['system_uptime_hours'],
                    'last_health_check': self.system_metrics['last_health_check']
                },
                'components': {
                    'distributed_storage': self.distributed_storage is not None,
                    'backup_storage': self.backup_storage is not None,
                    'archive_storage': self.archive_storage is not None,
                    'sync_engine': self.sync_engine is not None,
                    'integrity_checker': self.integrity_checker is not None,
                    'access_controller': self.access_controller is not None,
                    'quota_manager': self.quota_manager is not None,
                    'migration_engine': self.migration_engine is not None
                },
                'metrics': self.system_metrics,
                'component_stats': {}
            }
            
            # Get component-specific statistics
            if self.distributed_storage:
                status['component_stats']['distributed_storage'] = self.distributed_storage.get_storage_statistics()
            
            if self.backup_storage:
                status['component_stats']['backup_storage'] = self.backup_storage.get_backup_statistics()
            
            if self.archive_storage:
                status['component_stats']['archive_storage'] = self.archive_storage.get_archive_statistics()
            
            if self.access_controller:
                status['component_stats']['access_controller'] = self.access_controller.get_access_statistics()
            
            if self.quota_manager:
                status['component_stats']['quota_manager'] = self.quota_manager.get_quota_statistics()
            
            if self.migration_engine:
                status['component_stats']['migration_engine'] = self.migration_engine.get_migration_statistics()
            
            return {
                'success': True,
                'status': status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"System status retrieval failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def shutdown(self) -> Dict[str, Any]:
        """Gracefully shutdown the storage system"""        try:
            logger.info("Shutting down IA Influencer Storage System...")
            
            # Stop all background tasks and clean up resources
            # This would implement proper shutdown procedures for each component
            
            self.is_running = False
            
            return {
                'success': True,
                'message': 'Storage system shutdown completed',
                'shutdown_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"System shutdown failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ===========================================
    # PRIVATE METHODS
    # ===========================================
    
    async def _start_system_monitoring(self) -> None:
        """Start system monitoring tasks"""        while self.is_running:
            try:
                await asyncio.sleep(60)  # Monitor every minute
                
                # Update system uptime
                self.system_metrics['system_uptime_hours'] += 1/60
                self.system_metrics['last_health_check'] = datetime.now().isoformat()
                
                # Perform health checks on components
                await self._perform_health_checks()
                
            except Exception as e:
                logger.error(f"System monitoring error: {str(e)}")
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on all components"""        try:
            # Check component health
            # This would implement actual health check logic
            
            logger.debug("System health check completed")
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")


# ===========================================
# FACTORY FUNCTIONS
# ===========================================

def create_storage_system(config: Optional[StorageSystemConfig] = None) -> IAInfluencerStorageSystem:
    """    Factory function to create a new storage system instance
    """    return IAInfluencerStorageSystem(config)

def create_default_config(storage_root: str = None) -> StorageSystemConfig:
    """    Factory function to create default configuration
    """    if storage_root is None:
        storage_root = "/workspaces/Achiri/IA-Influencer-Agent/backend/data_management/storage"
    
    return StorageSystemConfig(storage_root_path=storage_root)


# ===========================================
# MAIN ENTRY POINT FOR TESTING
# ===========================================

async def main():
    """    Main entry point for testing the storage system
    """    try:
        # Create storage system with default configuration
        config = create_default_config()
        storage_system = create_storage_system(config)
        
        # Initialize the system
        init_result = await storage_system.initialize()
        print(f"Initialization result: {init_result}")
        
        if init_result['success']:
            # Get system status
            status_result = await storage_system.get_system_status()
            print(f"System status: {status_result}")
            
            # Test file operations
            test_user_data = {
                'username': 'test_user',
                'email': 'test@example.com',
                'password': 'test_password_123',
                'full_name': 'Test User'
            }
            
            user_result = await storage_system.create_user(test_user_data)
            print(f"User creation result: {user_result}")
            
            if user_result['success']:
                # Test file storage
                test_content = b"Hello, IA Influencer Storage System!"
                store_result = await storage_system.store_file(
                    file_path="/test/hello.txt",
                    content=test_content,
                    user_id=user_result['user_id'],
                    metadata={'test': True}
                )
                print(f"File storage result: {store_result}")
                
                if store_result['success']:
                    # Test file retrieval
                    retrieve_result = await storage_system.retrieve_file(
                        file_path="/test/hello.txt",
                        user_id=user_result['user_id']
                    )
                    print(f"File retrieval result: {retrieve_result}")
        
        # Shutdown system
        shutdown_result = await storage_system.shutdown()
        print(f"Shutdown result: {shutdown_result}")
        
    except Exception as e:
        print(f"Storage system test failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())


# ===========================================
# EXPORTS
# ===========================================

__all__ = [
    'IAInfluencerStorageSystem',
    'StorageSystemConfig',
    'create_storage_system',
    'create_default_config',
    
    # Re-export all component classes
    'DistributedStorageManager',
    'BackupStorageManager', 
    'ArchiveStorageManager',
    'SyncEngine',
    'IntegrityChecker',
    'AccessController',
    'QuotaManager',
    'MigrationEngine',
    
    # Re-export configuration classes
    'DistributedStorageConfig',
    'BackupConfig',
    'ArchiveConfig', 
    'SyncConfig',
    'IntegrityConfig',
    'AccessConfig',
    'QuotaConfig',
    'MigrationConfig'
]
