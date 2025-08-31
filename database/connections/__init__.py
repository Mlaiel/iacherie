"""Database Connections Module - IA Influencer Agent + Content Protection Platform

This module provides comprehensive database connection management for the multi-database
architecture supporting content creators, AI processing, protection, and monetization.

Architecture Components:
- PostgreSQL: Primary relational data (users, content, revenue tracking)
- Redis: Caching, sessions, real-time operations
- MongoDB: Content metadata, fingerprints, analytics data
- Elasticsearch: Search indexing, logs, content discovery
- FAISS: Vector similarity search for content fingerprinting
- MinIO/S3: Object storage for content files

Connection Features:
- Connection pooling and load balancing
- Health monitoring and auto-recovery
- Transaction management across databases
- Encryption and security compliance
- Multi-tenant data isolation
- Performance optimization and caching

Business Logic Flow:
User (creator) → Upload content → AI fingerprinting → Protection monitoring → 
Revenue tracking → Collaboration matching → Multi-platform distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""from .manager import DatabaseConnectionManager, get_connection_manager
from .postgresql import PostgreSQLConnectionHandler
from .redis import RedisConnectionHandler  
from .mongodb import MongoDBConnectionHandler
from .elasticsearch import ElasticsearchConnectionHandler
from .vector_stores import VectorStoreConnectionHandler
from .object_storage import ObjectStorageConnectionHandler
from .health_monitor import DatabaseHealthMonitor
from .pool_manager import ConnectionPoolManager
from .transaction_manager import TransactionManager
from .session_manager import SessionManager
from .failover import FailoverManager
from .load_balancer import DatabaseLoadBalancer
from .config_manager import ConnectionConfigManager
from .factory import ConnectionFactory
from .tenant_manager import TenantConnectionManager, TenantType, TenantConfig
from .content_protection import ContentProtectionConnections, ContentFingerprint, ProtectionAlert
from .monetization import MonetizationConnections, RevenueRecord, PayoutRequest, LicenseAgreement
from .index import DatabaseConnectionsIndex, get_database_index


# Export all main components for easy access
__all__ = [
    # Core managers
    "DatabaseConnectionManager", 
    "get_connection_manager",
    "DatabaseConnectionsIndex",
    "get_database_index",
    
    # Connection handlers
    "PostgreSQLConnectionHandler",
    "RedisConnectionHandler", 
    "MongoDBConnectionHandler",
    "ElasticsearchConnectionHandler",
    "VectorStoreConnectionHandler",
    "ObjectStorageConnectionHandler",
    
    # Infrastructure components
    "DatabaseHealthMonitor",
    "ConnectionPoolManager",
    "TransactionManager",
    "SessionManager",
    "FailoverManager",
    "DatabaseLoadBalancer",
    "ConnectionConfigManager",
    "ConnectionFactory",
    
    # Multi-tenant support
    "TenantConnectionManager",
    "TenantType",
    "TenantConfig",
    
    # Specialized business logic connections
    "ContentProtectionConnections",
    "ContentFingerprint",
    "ProtectionAlert",
    "MonetizationConnections",
    "RevenueRecord",
    "PayoutRequest",
    "LicenseAgreement"
]
from .config_manager import DatabaseConfigurationManager
from .encryption import ConnectionEncryption
from .tenant_manager import TenantConnectionManager

# Connection factory and utilities
from .factory import DatabaseConnectionFactory
from .registry import ConnectionRegistry
from .balancer import LoadBalancer
from .metrics import ConnectionMetrics

__all__ = [
    # Core connection management
    "DatabaseConnectionManager",
    "get_connection_manager",
    
    # Database handlers
    "PostgreSQLConnectionHandler",
    "RedisConnectionHandler", 
    "MongoDBConnectionHandler",
    "ElasticsearchConnectionHandler",
    "VectorStoreConnectionHandler",
    "ObjectStorageConnectionHandler",
    
    # Infrastructure components
    "DatabaseHealthMonitor",
    "ConnectionPoolManager",
    "TransactionManager", 
    "SessionManager",
    "FailoverManager",
    "DatabaseLoadBalancer",
    "DatabaseConfigurationManager",
    "ConnectionEncryption",
    "TenantConnectionManager",
    
    # Factory and utilities
    "DatabaseConnectionFactory",
    "ConnectionRegistry",
    "LoadBalancer",
    "ConnectionMetrics"
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"