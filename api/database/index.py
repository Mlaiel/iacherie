"""Database Index - IA Influencer Agent Platform
Main entry point for all database services and utilities

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""
# Database connections and session management
from .connection import (
    DatabaseConnection,
    ConnectionPool,
    SessionManager,
    TransactionManager,
    ReadReplicaManager
)

# Repository pattern implementations
from .repositories import (
    UserRepository,
    CreatorRepository,
    ContentRepository,
    MediaRepository,
    CopyrightRepository,
    LicenseRepository,
    CollaborationRepository,
    ProjectRepository,
    RevenueRepository,
    DistributionRepository,
    AnalyticsRepository,
    NotificationRepository
)

# Database migrations and schema management
from .migrations import (
    MigrationManager,
    SchemaManager,
    DatabaseSeeder,
    DataMigrator,
    BackupManager
)

# Query builders and ORM utilities
from .query_builders import (
    QueryBuilder,
    AdvancedQueryBuilder,
    AggregationQueryBuilder,
    JoinQueryBuilder,
    SubQueryBuilder
)

# Database utilities
from .utils import (
    DatabaseUtils,
    TableUtils,
    IndexUtils,
    ConstraintUtils,
    PerformanceAnalyzer
)

# Caching and optimization
from .cache import (
    DatabaseCache,
    RedisCache,
    MemoryCache,
    QueryCache,
    ResultSetCache,
    get_cache,
    cache_get,
    cache_set,
    cache_delete
)

# Database monitoring and health
from .monitoring import (
    DatabaseMonitor,
    PerformanceMonitor,
    HealthChecker,
    PostgreSQLMetricsCollector,
    RedisMetricsCollector,
    AlertManager,
    get_database_monitor,
    get_performance_monitor,
    get_health_checker
)

# Advanced transaction management
from .transactions import (
    TransactionManager,
    TransactionExecutor,
    TransactionConfig,
    TransactionContext,
    TransactionOperation,
    DatabaseOperation,
    DistributedTransactionCoordinator,
    get_transaction_manager,
    simple_transaction,
    saga_transaction,
    distributed_transaction,
    retry_transaction
)

# Database security
from .security import (
    DatabaseSecurity,
    DatabaseEncryption,
    PasswordSecurity,
    QuerySanitizer,
    DatabaseAuditor,
    AccessControlManager,
    SecurityPolicy,
    AccessPermission,
    AuditEvent,
    get_database_security,
    secure_password_hash,
    verify_password,
    encrypt_sensitive_field,
    decrypt_sensitive_field
)

# Database optimization
from .optimization import (
    DatabaseOptimizer,
    QueryAnalyzer,
    IndexOptimizer,
    QueryProfile,
    IndexRecommendation,
    OptimizationRecommendation,
    get_database_optimizer,
    analyze_query_performance,
    get_optimization_recommendations,
    get_index_recommendations
)


def get_database_connection():
    """Get the main database connection"""    return DatabaseConnection.get_instance()


def get_session_manager():
    """Get the database session manager"""    return SessionManager()


def get_transaction_manager():
    """Get the database transaction manager"""    return TransactionManager()


def get_transaction_manager():
    """Get the database transaction manager"""    return TransactionManager()


def get_database_security():
    """Get the database security manager"""    return DatabaseSecurity()


def get_database_optimizer():
    """Get the database optimizer"""    return DatabaseOptimizer()


def get_query_analyzer():
    """Get the query analyzer"""    return QueryAnalyzer()


def get_index_optimizer():
    """Get the index optimizer"""    return IndexOptimizer()


def get_database_cache():
    """Get the database cache manager"""    return DatabaseCache()


def get_database_monitor():
    """Get the database monitor"""    return DatabaseMonitor()


def get_performance_monitor():
    """Get the performance monitor"""    return PerformanceMonitor()


def get_health_checker():
    """Get the health checker"""    return HealthChecker()


def get_database_auditor():
    """Get the database auditor"""    return DatabaseAuditor()


def get_access_control_manager():
    """Get the access control manager"""    return AccessControlManager()


async def initialize_database_services():
    """Initialize all database services"""    logger.info("Initializing database services...")
    
    try:
        # Initialize core connection
        connection = await get_database_connection()
        
        # Initialize cache
        cache = await get_cache()
        
        # Initialize security
        security = await get_database_security()
        
        # Initialize monitoring
        monitor = await get_database_monitor()
        
        # Initialize optimizer
        optimizer = await get_database_optimizer()
        
        # Initialize transaction manager
        tx_manager = await get_transaction_manager()
        
        logger.info("All database services initialized successfully")
        
        return {
            'connection': connection,
            'cache': cache,
            'security': security,
            'monitor': monitor,
            'optimizer': optimizer,
            'transaction_manager': tx_manager
        }
        
    except Exception as e:
        logger.error(f"Failed to initialize database services: {e}")
        raise


async def setup_database_middleware():
    """Setup database middleware and event handlers"""    logger.info("Setting up database middleware...")
    
    try:
        # Initialize all services
        services = await initialize_database_services()
        
        # Setup event handlers and middleware
        # This would integrate with your web framework middleware
        
        logger.info("Database middleware setup completed")
        return services
        
    except Exception as e:
        logger.error(f"Database middleware setup failed: {e}")
        raise


async def check_database_health():
    """Comprehensive database health check"""    try:
        health_checker = await get_health_checker()
        health_report = await health_checker.comprehensive_health_check()
        
        return health_report
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            'overall_status': 'critical',
            'error': str(e),
            'timestamp': datetime.utcnow()
        }


async def optimize_database_performance():
    """Run database performance optimization"""    try:
        optimizer = await get_database_optimizer()
        analysis = await optimizer.perform_comprehensive_analysis()
        
        return analysis
        
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        return {
            'error': str(e),
            'timestamp': datetime.utcnow()
        }


def get_creator_repository():
    """Get the creator repository"""    return CreatorRepository()


def get_content_repository():
    """Get the content repository"""    return ContentRepository()


def get_media_repository():
    """Get the media repository"""    return MediaRepository()


def get_copyright_repository():
    """Get the copyright repository"""    return CopyrightRepository()


def get_license_repository():
    """Get the license repository"""    return LicenseRepository()


def get_collaboration_repository():
    """Get the collaboration repository"""    return CollaborationRepository()


def get_project_repository():
    """Get the project repository"""    return ProjectRepository()


def get_revenue_repository():
    """Get the revenue repository"""    return RevenueRepository()


def get_distribution_repository():
    """Get the distribution repository"""    return DistributionRepository()


def get_analytics_repository():
    """Get the analytics repository"""    return AnalyticsRepository()


def get_notification_repository():
    """Get the notification repository"""    return NotificationRepository()


def get_all_repositories():
    """Get all repository instances"""    return {
        'user': get_user_repository(),
        'creator': get_creator_repository(),
        'content': get_content_repository(),
        'media': get_media_repository(),
        'copyright': get_copyright_repository(),
        'license': get_license_repository(),
        'collaboration': get_collaboration_repository(),
        'project': get_project_repository(),
        'revenue': get_revenue_repository(),
        'distribution': get_distribution_repository(),
        'analytics': get_analytics_repository(),
        'notification': get_notification_repository()
    }


def get_migration_manager():
    """Get the database migration manager"""    return MigrationManager()


def get_schema_manager():
    """Get the database schema manager"""    return SchemaManager()


def get_backup_manager():
    """Get the database backup manager"""    return BackupManager()


def get_query_builder():
    """Get the standard query builder"""    return QueryBuilder()


def get_advanced_query_builder():
    """Get the advanced query builder"""    return AdvancedQueryBuilder()


def get_database_cache():
    """Get the database cache manager"""    return DatabaseCache()


def get_database_monitor():
    """Get the database monitoring service"""    return DatabaseMonitor()


def initialize_database_services():
    """    Initialize all database services with proper configuration
    
    Returns:
        Dictionary containing all database services
    """    services = {
        'connection': get_database_connection(),
        'session_manager': get_session_manager(),
        'transaction_manager': get_transaction_manager(),
        'repositories': get_all_repositories(),
        'migration_manager': get_migration_manager(),
        'schema_manager': get_schema_manager(),
        'backup_manager': get_backup_manager(),
        'query_builder': get_query_builder(),
        'advanced_query_builder': get_advanced_query_builder(),
        'cache': get_database_cache(),
        'monitor': get_database_monitor()
    }
    
    # Initialize cross-service integrations
    for service_name, service in services.items():
        if hasattr(service, 'initialize_integrations') and service_name != 'repositories':
            service.initialize_integrations(services)
    
    # Initialize repository integrations
    repositories = services['repositories']
    for repo_name, repo in repositories.items():
        if hasattr(repo, 'initialize_integrations'):
            repo.initialize_integrations(services)
    
    return services


def setup_database_middleware():
    """    Setup all database middleware for the application
    
    Returns:
        List of configured middleware instances
    """    middleware = [
        SessionManager(),
        TransactionManager(),
        DatabaseCache(),
        PerformanceMonitor()
    ]
    
    return middleware


def create_database_backup(backup_type: str = 'full'):
    """    Create a database backup
    
    Args:
        backup_type: Type of backup (full, incremental, differential)
        
    Returns:
        Backup result information
    """    backup_manager = get_backup_manager()
    return backup_manager.create_backup(backup_type)


def restore_database_backup(backup_id: str):
    """    Restore database from backup
    
    Args:
        backup_id: ID of the backup to restore
        
    Returns:
        Restoration result information
    """    backup_manager = get_backup_manager()
    return backup_manager.restore_backup(backup_id)


def run_database_migrations():
    """    Run pending database migrations
    
    Returns:
        Migration execution results
    """    migration_manager = get_migration_manager()
    return migration_manager.run_migrations()


def check_database_health():
    """    Perform comprehensive database health check
    
    Returns:
        Health check results
    """    monitor = get_database_monitor()
    health_checker = HealthChecker()
    
    return {
        'connection_status': monitor.check_connection(),
        'performance_metrics': monitor.get_performance_metrics(),
        'disk_usage': monitor.get_disk_usage(),
        'active_connections': monitor.get_active_connections(),
        'slow_queries': monitor.get_slow_queries(),
        'table_health': health_checker.check_all_tables(),
        'index_health': health_checker.check_all_indexes(),
        'constraint_health': health_checker.check_all_constraints()
    }


def optimize_database_performance():
    """    Run database optimization procedures
    
    Returns:
        Optimization results
    """    performance_analyzer = PerformanceAnalyzer()
    
    return {
        'index_recommendations': performance_analyzer.analyze_indexes(),
        'query_optimization': performance_analyzer.analyze_slow_queries(),
        'table_optimization': performance_analyzer.analyze_table_structure(),
        'partition_recommendations': performance_analyzer.analyze_partitioning(),
        'cache_optimization': performance_analyzer.analyze_cache_usage()
    }


def get_database_statistics():
    """    Get comprehensive database statistics
    
    Returns:
        Database statistics and metrics
    """    monitor = get_database_monitor()
    metrics_collector = MetricsCollector()
    
    return {
        'table_sizes': metrics_collector.get_table_sizes(),
        'row_counts': metrics_collector.get_row_counts(),
        'index_usage': metrics_collector.get_index_usage(),
        'query_performance': monitor.get_query_performance_stats(),
        'connection_pool_stats': monitor.get_connection_pool_stats(),
        'cache_hit_ratios': monitor.get_cache_statistics(),
        'transaction_stats': monitor.get_transaction_statistics(),
        'lock_statistics': monitor.get_lock_statistics()
    }


__all__ = [
    # Connection and Session Management
    'DatabaseConnection',
    'ConnectionPool',
    'SessionManager',
    'TransactionManager',
    'ReadReplicaManager',
    
    # Repositories
    'UserRepository',
    'CreatorRepository',
    'ContentRepository',
    'MediaRepository',
    'CopyrightRepository',
    'LicenseRepository',
    'CollaborationRepository',
    'ProjectRepository',
    'RevenueRepository',
    'DistributionRepository',
    'AnalyticsRepository',
    'NotificationRepository',
    
    # Migrations and Schema
    'MigrationManager',
    'SchemaManager',
    'DatabaseSeeder',
    'DataMigrator',
    'BackupManager',
    
    # Query Builders
    'QueryBuilder',
    'AdvancedQueryBuilder',
    'AggregationQueryBuilder',
    'JoinQueryBuilder',
    'SubQueryBuilder',
    
    # Utilities
    'DatabaseUtils',
    'TableUtils',
    'IndexUtils',
    'ConstraintUtils',
    'PerformanceAnalyzer',
    
    # Caching
    'DatabaseCache',
    'RedisCache',
    'MemcachedCache',
    'QueryCache',
    'ResultSetCache',
    
    # Monitoring
    'DatabaseMonitor',
    'PerformanceMonitor',
    'HealthChecker',
    'MetricsCollector',
    'AlertManager',
    
    # Factory Functions
    'get_database_connection',
    'get_session_manager',
    'get_transaction_manager',
    'get_user_repository',
    'get_creator_repository',
    'get_content_repository',
    'get_media_repository',
    'get_copyright_repository',
    'get_license_repository',
    'get_collaboration_repository',
    'get_project_repository',
    'get_revenue_repository',
    'get_distribution_repository',
    'get_analytics_repository',
    'get_notification_repository',
    'get_all_repositories',
    'get_migration_manager',
    'get_schema_manager',
    'get_backup_manager',
    'get_query_builder',
    'get_advanced_query_builder',
    'get_database_cache',
    'get_database_monitor',
    
    # Service Management
    'initialize_database_services',
    'setup_database_middleware',
    
    # Operations
    'create_database_backup',
    'restore_database_backup',
    'run_database_migrations',
    'check_database_health',
    'optimize_database_performance',
    'get_database_statistics'
]
