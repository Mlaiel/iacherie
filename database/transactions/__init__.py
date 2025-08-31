"""Database Transactions Module - Core Components

Enterprise-grade transaction management system providing distributed transaction
coordination, ACID compliance, performance monitoring, and security controls.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""from .transaction_coordinator import TransactionCoordinator, TransactionContext
from .distributed_transactions import DistributedTransactionManager, DistributedTransaction
from .atomicity_manager import AtomicityManager, AtomicOperation
from .isolation_controller import IsolationController, IsolationLevel
from .durability_manager import DurabilityManager, PersistenceStrategy
from .performance_monitor import PerformanceMonitor, TransactionMetrics
from .audit_system import AuditSystem, TransactionLog
from .conflict_resolver import ConflictResolver, DeadlockDetector
from .health_checker import TransactionHealthChecker, HealthStatus
from .security_manager import TransactionSecurityManager, SecurityPolicy
from .encryption_handler import TransactionEncryption, EncryptionConfig
from .compliance_tracker import ComplianceTracker, ComplianceReport

__version__ = "2.1.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

# Core transaction components
__all__ = [
    # Main coordination
    "TransactionCoordinator",
    "TransactionContext",
    
    # Distributed transactions
    "DistributedTransactionManager", 
    "DistributedTransaction",
    
    # ACID properties
    "AtomicityManager",
    "AtomicOperation",
    "IsolationController",
    "IsolationLevel",
    "DurabilityManager",
    "PersistenceStrategy",
    
    # Monitoring and health
    "PerformanceMonitor",
    "TransactionMetrics",
    "TransactionHealthChecker",
    "HealthStatus",
    
    # Auditing and logging
    "AuditSystem",
    "TransactionLog",
    
    # Conflict resolution
    "ConflictResolver",
    "DeadlockDetector",
    
    # Security and compliance
    "TransactionSecurityManager",
    "SecurityPolicy",
    "TransactionEncryption",
    "EncryptionConfig",
    "ComplianceTracker",
    "ComplianceReport",
]

# Module configuration
TRANSACTION_CONFIG = {
    "default_timeout": 30,  # seconds
    "max_retries": 3,
    "isolation_level": "READ_COMMITTED",
    "enable_monitoring": True,
    "enable_encryption": True,
    "audit_level": "FULL",
    "performance_tracking": True,
    "health_check_interval": 5,  # seconds
}

# Performance targets
PERFORMANCE_TARGETS = {
    "max_transaction_time": 1.0,  # seconds
    "throughput_target": 100000,  # transactions per second
    "error_rate_threshold": 0.01,  # 1%
    "availability_target": 0.9999,  # 99.99%
}

# Security configuration
SECURITY_CONFIG = {
    "encryption_algorithm": "AES-256-GCM",
    "key_rotation_interval": 86400,  # 24 hours
    "audit_retention": 2592000,  # 30 days
    "access_control": "RBAC",
    "session_timeout": 3600,  # 1 hour
}
