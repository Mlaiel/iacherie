"""
Database Package - IA Influencer Agent Platform
Enterprise-grade database services and utilities

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead AI Developer, Senior Backend Engineer, ML Engineer, 
Database Administrator, Security Expert, Microservices Architect, Audio Engineer, 
DevOps Engineer, AI Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

from .index import *

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Core database services
    "initialize_database_services",
    "setup_database_middleware", 
    "get_database_connection",
    "get_session_manager",
    "get_transaction_manager",
    "check_database_health",
    "optimize_database_performance",
    
    # Repository pattern
    "get_all_repositories",
    "UserRepository",
    "CreatorRepository", 
    "ContentRepository",
    "MediaRepository",
    "CopyrightRepository",
    "LicenseRepository",
    "CollaborationRepository",
    "ProjectRepository",
    "RevenueRepository",
    "DistributionRepository",
    "AnalyticsRepository",
    "NotificationRepository",
    
    # Caching services
    "get_database_cache",
    "DatabaseCache",
    "QueryCache",
    "ResultSetCache",
    "cache_get",
    "cache_set", 
    "cache_delete",
    
    # Security services
    "get_database_security",
    "DatabaseSecurity",
    "DatabaseEncryption", 
    "DatabaseAuditor",
    "AccessControlManager",
    "secure_password_hash",
    "verify_password",
    "encrypt_sensitive_field",
    "decrypt_sensitive_field",
    
    # Monitoring services
    "get_database_monitor",
    "get_performance_monitor",
    "get_health_checker",
    "DatabaseMonitor",
    "PerformanceMonitor",
    "HealthChecker",
    
    # Optimization services
    "get_database_optimizer",
    "get_query_analyzer",
    "get_index_optimizer", 
    "DatabaseOptimizer",
    "QueryAnalyzer",
    "IndexOptimizer",
    "analyze_query_performance",
    "get_optimization_recommendations",
    "get_index_recommendations",
    
    # Transaction management
    "simple_transaction",
    "saga_transaction", 
    "distributed_transaction",
    "retry_transaction",
    "TransactionManager",
    "TransactionExecutor",
    "TransactionConfig",
    "TransactionContext"
]
