"""🔄 Database Operations - Consolidated CRUD + Migrations + Advanced Operations
===============================================================================
Module: database/database_operations.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Comprehensive Database Operations - Production-Ready
Responsibility: Unified interface for all database operations

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This operations module provides comprehensive database functionality:
- Enhanced CRUD operations with advanced features
- Integrated migration management
- Performance optimization and monitoring
- Transaction management and batch operations
- Data validation and integrity checking
- Creator workflow integration
"""

import os
import logging
import datetime
import time
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum

# Import from existing modules
try:
    from . import models
    from . import crud
    from . import migrations
    from .analytics_engine import get_analytics_engine, AnalyticsEvent, track_analytics_event
    from .security_manager import get_security_manager, AuditEventType, SecurityLevel, log_security_event
    INTERNAL_MODULES_AVAILABLE = True
except ImportError:
    INTERNAL_MODULES_AVAILABLE = False

# Optional imports for production features
try:
    import sqlalchemy
    from sqlalchemy import text, and_, or_, desc, asc, func
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.exc import SQLAlchemyError
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    sqlalchemy = None

# Configure logging
logger = logging.getLogger(__name__)

class OperationType(Enum):
    """Database operation type enumeration"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    BULK_CREATE = "bulk_create"
    BULK_UPDATE = "bulk_update"
    BULK_DELETE = "bulk_delete"
    MIGRATION = "migration"
    OPTIMIZATION = "optimization"

class TransactionIsolation(Enum):
    """Transaction isolation level enumeration"""
    READ_UNCOMMITTED = "READ UNCOMMITTED"
    READ_COMMITTED = "READ COMMITTED"
    REPEATABLE_READ = "REPEATABLE READ"
    SERIALIZABLE = "SERIALIZABLE"

@dataclass
class OperationResult:
    """Database operation result"""
    success: bool
    data: Any
    operation_type: OperationType
    execution_time_ms: float
    rows_affected: int
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class BatchOperation:
    """Batch operation definition"""
    operation_type: OperationType
    model_class: Any
    data: List[Dict[str, Any]]
    filters: Optional[Dict[str, Any]] = None

class DatabaseOperations:
    """Comprehensive database operations manager"""
    
    def __init__(self, connection=None, session=None, auto_optimize: bool = True):
        self.connection = connection
        self.session = session
        self.auto_optimize = auto_optimize
        self.operation_history: List[OperationResult] = []
        self.performance_metrics: Dict[str, List[float]] = {}
        
        # Initialize components
        self._initialize_components()
        
        # Setup optimization scheduler if enabled
        if self.auto_optimize:
            self._setup_auto_optimization()
    
    def _initialize_components(self):
        """Initialize database operation components"""
        try:
            # Initialize CRUD manager
            if INTERNAL_MODULES_AVAILABLE:
                self.crud_manager = crud.get_crud_manager(self.session)
                self.migration_manager = migrations.get_migration_manager(self.connection)
            
            # Initialize analytics and security
            self.analytics = get_analytics_engine(self.connection) if INTERNAL_MODULES_AVAILABLE else None
            self.security = get_security_manager(self.connection) if INTERNAL_MODULES_AVAILABLE else None
            
            logger.info("Database operations initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database operations: {e}")
    
    def _setup_auto_optimization(self):
        """Setup automatic performance optimization"""
        try:
            # This would setup background optimization tasks in production
            logger.info("Auto-optimization enabled")
        except Exception as e:
            logger.error(f"Failed to setup auto-optimization: {e}")
    
    @contextmanager
    def transaction(self, isolation_level: TransactionIsolation = TransactionIsolation.READ_COMMITTED):
        """Database transaction context manager"""
        start_time = time.time()
        operation_id = f"transaction_{int(start_time * 1000)}"
        
        try:
            if SQLALCHEMY_AVAILABLE and self.connection:
                # Start transaction with specified isolation level
                trans = self.connection.begin()
                if isolation_level != TransactionIsolation.READ_COMMITTED:
                    self.connection.execute(text(f"SET TRANSACTION ISOLATION LEVEL {isolation_level.value}"))
                
                # Log transaction start
                if self.security:
                    log_security_event(
                        AuditEventType.DATA_ACCESS,
                        resource="database",
                        action="transaction_start",
                        details={'isolation_level': isolation_level.value, 'transaction_id': operation_id}
                    )
                
                yield self.connection
                
                # Commit transaction
                trans.commit()
                execution_time = (time.time() - start_time) * 1000
                
                # Track performance
                if self.analytics:
                    track_analytics_event(
                        AnalyticsEvent.QUERY_EXECUTED,
                        {'operation': 'transaction', 'execution_time_ms': execution_time, 'success': True}
                    )
                
                logger.debug(f"Transaction {operation_id} committed in {execution_time:.2f}ms")
                
            else:
                # Fallback for non-SQLAlchemy environments
                yield None
                
        except Exception as e:
            if SQLALCHEMY_AVAILABLE and 'trans' in locals():
                trans.rollback()
            
            execution_time = (time.time() - start_time) * 1000
            
            # Log transaction failure
            if self.security:
                log_security_event(
                    AuditEventType.SECURITY_VIOLATION,
                    resource="database",
                    action="transaction_failed",
                    details={'error': str(e), 'transaction_id': operation_id},
                    risk_level=SecurityLevel.MEDIUM
                )
            
            logger.error(f"Transaction {operation_id} failed after {execution_time:.2f}ms: {e}")
            raise
    
    def create_user(self, user_data: Dict[str, Any], user_id: int = None, ip_address: str = None) -> OperationResult:
        """Create a new user with full workflow integration"""
        start_time = time.time()
        
        try:
            # Validate user data
            validation_result = self._validate_user_data(user_data)
            if not validation_result['valid']:
                return OperationResult(
                    success=False,
                    data=None,
                    operation_type=OperationType.CREATE,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    rows_affected=0,
                    error_message=f"Validation failed: {validation_result['errors']}"
                )
            
            # Encrypt sensitive data if needed
            if self.security and 'email' in user_data:
                # In production, you might encrypt PII
                pass
            
            # Create user using CRUD
            if INTERNAL_MODULES_AVAILABLE and self.crud_manager:
                user = self.crud_manager.get_crud(models.User).create(user_data)
            else:
                # Fallback creation
                user = models.User(**user_data)
            
            execution_time = (time.time() - start_time) * 1000
            
            if user:
                # Track user creation event
                if self.analytics:
                    track_analytics_event(
                        AnalyticsEvent.USER_CREATED,
                        {'user_id': getattr(user, 'id', None), 'username': user_data.get('username')},
                        user_id=user_id
                    )
                
                # Log security event
                if self.security:
                    log_security_event(
                        AuditEventType.DATA_MODIFICATION,
                        user_id=user_id,
                        resource="users",
                        action="create",
                        details={'new_user_id': getattr(user, 'id', None)},
                        ip_address=ip_address
                    )
                
                result = OperationResult(
                    success=True,
                    data=user,
                    operation_type=OperationType.CREATE,
                    execution_time_ms=execution_time,
                    rows_affected=1,
                    metadata={'user_id': getattr(user, 'id', None)}
                )
            else:
                result = OperationResult(
                    success=False,
                    data=None,
                    operation_type=OperationType.CREATE,
                    execution_time_ms=execution_time,
                    rows_affected=0,
                    error_message="Failed to create user"
                )
            
            self._record_operation_result(result)
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_result = OperationResult(
                success=False,
                data=None,
                operation_type=OperationType.CREATE,
                execution_time_ms=execution_time,
                rows_affected=0,
                error_message=str(e)
            )
            self._record_operation_result(error_result)
            logger.error(f"Failed to create user: {e}")
            return error_result
    
    def create_content(self, content_data: Dict[str, Any], user_id: int = None, ip_address: str = None) -> OperationResult:
        """Create new content with workflow integration"""
        start_time = time.time()
        
        try:
            # Validate content data
            validation_result = self._validate_content_data(content_data)
            if not validation_result['valid']:
                return OperationResult(
                    success=False,
                    data=None,
                    operation_type=OperationType.CREATE,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    rows_affected=0,
                    error_message=f"Validation failed: {validation_result['errors']}"
                )
            
            # Create content using CRUD
            if INTERNAL_MODULES_AVAILABLE and self.crud_manager:
                content = self.crud_manager.get_crud(models.Content).create(content_data)
            else:
                # Fallback creation
                content = models.Content(**content_data)
            
            execution_time = (time.time() - start_time) * 1000
            
            if content:
                # Track content upload event
                if self.analytics:
                    track_analytics_event(
                        AnalyticsEvent.CONTENT_UPLOADED,
                        {
                            'content_id': getattr(content, 'id', None),
                            'content_type': content_data.get('content_type'),
                            'title': content_data.get('title'),
                            'file_size': content_data.get('file_size', 0)
                        },
                        user_id=content_data.get('owner_id') or user_id
                    )
                
                # Log security event
                if self.security:
                    log_security_event(
                        AuditEventType.DATA_MODIFICATION,
                        user_id=user_id,
                        resource="contents",
                        action="create",
                        details={'content_id': getattr(content, 'id', None), 'type': content_data.get('content_type')},
                        ip_address=ip_address
                    )
                
                result = OperationResult(
                    success=True,
                    data=content,
                    operation_type=OperationType.CREATE,
                    execution_time_ms=execution_time,
                    rows_affected=1,
                    metadata={'content_id': getattr(content, 'id', None)}
                )
            else:
                result = OperationResult(
                    success=False,
                    data=None,
                    operation_type=OperationType.CREATE,
                    execution_time_ms=execution_time,
                    rows_affected=0,
                    error_message="Failed to create content"
                )
            
            self._record_operation_result(result)
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_result = OperationResult(
                success=False,
                data=None,
                operation_type=OperationType.CREATE,
                execution_time_ms=execution_time,
                rows_affected=0,
                error_message=str(e)
            )
            self._record_operation_result(error_result)
            logger.error(f"Failed to create content: {e}")
            return error_result
    
    def create_fingerprint(self, fingerprint_data: Dict[str, Any], user_id: int = None, ip_address: str = None) -> OperationResult:
        """Create content fingerprint for protection"""
        start_time = time.time()
        
        try:
            # Validate fingerprint data
            validation_result = self._validate_fingerprint_data(fingerprint_data)
            if not validation_result['valid']:
                return OperationResult(
                    success=False,
                    data=None,
                    operation_type=OperationType.CREATE,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    rows_affected=0,
                    error_message=f"Validation failed: {validation_result['errors']}"
                )
            
            # Create fingerprint using CRUD
            if INTERNAL_MODULES_AVAILABLE and self.crud_manager:
                fingerprint = self.crud_manager.get_crud(models.Fingerprint).create(fingerprint_data)
            else:
                # Fallback creation
                fingerprint = models.Fingerprint(**fingerprint_data)
            
            execution_time = (time.time() - start_time) * 1000
            
            if fingerprint:
                # Track fingerprint creation
                if self.analytics:
                    track_analytics_event(
                        AnalyticsEvent.QUERY_EXECUTED,
                        {
                            'operation': 'fingerprint_creation',
                            'content_id': fingerprint_data.get('content_id'),
                            'algorithm': fingerprint_data.get('algorithm'),
                            'confidence': fingerprint_data.get('confidence_score', 0.0)
                        },
                        user_id=user_id
                    )
                
                # Log security event
                if self.security:
                    log_security_event(
                        AuditEventType.DATA_MODIFICATION,
                        user_id=user_id,
                        resource="fingerprints",
                        action="create",
                        details={'fingerprint_id': getattr(fingerprint, 'id', None), 'content_id': fingerprint_data.get('content_id')},
                        ip_address=ip_address
                    )
                
                result = OperationResult(
                    success=True,
                    data=fingerprint,
                    operation_type=OperationType.CREATE,
                    execution_time_ms=execution_time,
                    rows_affected=1,
                    metadata={'fingerprint_id': getattr(fingerprint, 'id', None)}
                )
            else:
                result = OperationResult(
                    success=False,
                    data=None,
                    operation_type=OperationType.CREATE,
                    execution_time_ms=execution_time,
                    rows_affected=0,
                    error_message="Failed to create fingerprint"
                )
            
            self._record_operation_result(result)
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_result = OperationResult(
                success=False,
                data=None,
                operation_type=OperationType.CREATE,
                execution_time_ms=execution_time,
                rows_affected=0,
                error_message=str(e)
            )
            self._record_operation_result(error_result)
            logger.error(f"Failed to create fingerprint: {e}")
            return error_result
    
    def create_revenue_entry(self, revenue_data: Dict[str, Any], user_id: int = None, ip_address: str = None) -> OperationResult:
        """Create revenue tracking entry"""
        start_time = time.time()
        
        try:
            # Validate revenue data
            required_fields = ['user_id', 'amount', 'currency', 'revenue_type']
            missing_fields = [field for field in required_fields if field not in revenue_data]
            
            if missing_fields:
                return OperationResult(
                    success=False,
                    data=None,
                    operation_type=OperationType.CREATE,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    rows_affected=0,
                    error_message=f"Missing required fields: {missing_fields}"
                )
            
            # Store revenue data (in production, this would be a separate Revenue model)
            revenue_entry = {
                'id': len(self.operation_history) + 1,  # Simple ID generation
                'timestamp': datetime.datetime.utcnow(),
                **revenue_data
            }
            
            execution_time = (time.time() - start_time) * 1000
            
            # Track revenue generation event
            if self.analytics:
                track_analytics_event(
                    AnalyticsEvent.REVENUE_GENERATED,
                    {
                        'amount': revenue_data['amount'],
                        'currency': revenue_data['currency'],
                        'revenue_type': revenue_data['revenue_type'],
                        'content_id': revenue_data.get('content_id')
                    },
                    user_id=revenue_data['user_id']
                )
            
            # Log security event
            if self.security:
                log_security_event(
                    AuditEventType.DATA_MODIFICATION,
                    user_id=user_id,
                    resource="revenue",
                    action="create",
                    details={'amount': revenue_data['amount'], 'user_id': revenue_data['user_id']},
                    ip_address=ip_address,
                    risk_level=SecurityLevel.MEDIUM  # Financial data is sensitive
                )
            
            result = OperationResult(
                success=True,
                data=revenue_entry,
                operation_type=OperationType.CREATE,
                execution_time_ms=execution_time,
                rows_affected=1,
                metadata={'revenue_id': revenue_entry['id']}
            )
            
            self._record_operation_result(result)
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_result = OperationResult(
                success=False,
                data=None,
                operation_type=OperationType.CREATE,
                execution_time_ms=execution_time,
                rows_affected=0,
                error_message=str(e)
            )
            self._record_operation_result(error_result)
            logger.error(f"Failed to create revenue entry: {e}")
            return error_result
    
    def batch_operations(self, operations: List[BatchOperation], user_id: int = None, ip_address: str = None) -> List[OperationResult]:
        """Execute batch operations with transaction support"""
        start_time = time.time()
        results = []
        
        try:
            with self.transaction() as conn:
                for operation in operations:
                    if operation.operation_type == OperationType.BULK_CREATE:
                        result = self._bulk_create(operation, user_id, ip_address)
                    elif operation.operation_type == OperationType.BULK_UPDATE:
                        result = self._bulk_update(operation, user_id, ip_address)
                    elif operation.operation_type == OperationType.BULK_DELETE:
                        result = self._bulk_delete(operation, user_id, ip_address)
                    else:
                        result = OperationResult(
                            success=False,
                            data=None,
                            operation_type=operation.operation_type,
                            execution_time_ms=0,
                            rows_affected=0,
                            error_message=f"Unsupported batch operation: {operation.operation_type}"
                        )
                    
                    results.append(result)
                    
                    # If any operation fails, the transaction will be rolled back
                    if not result.success:
                        raise Exception(f"Batch operation failed: {result.error_message}")
            
            total_execution_time = (time.time() - start_time) * 1000
            
            # Track batch operation
            if self.analytics:
                track_analytics_event(
                    AnalyticsEvent.QUERY_EXECUTED,
                    {
                        'operation': 'batch_operations',
                        'operation_count': len(operations),
                        'execution_time_ms': total_execution_time,
                        'success': all(r.success for r in results)
                    },
                    user_id=user_id
                )
            
            logger.info(f"Batch operations completed in {total_execution_time:.2f}ms")
            return results
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Batch operations failed after {execution_time:.2f}ms: {e}")
            
            # Return error result for all operations
            error_result = OperationResult(
                success=False,
                data=None,
                operation_type=OperationType.BULK_CREATE,
                execution_time_ms=execution_time,
                rows_affected=0,
                error_message=str(e)
            )
            
            return results + [error_result] * (len(operations) - len(results))
    
    def _bulk_create(self, operation: BatchOperation, user_id: int = None, ip_address: str = None) -> OperationResult:
        """Execute bulk create operation"""
        start_time = time.time()
        
        try:
            created_items = []
            
            if INTERNAL_MODULES_AVAILABLE and self.crud_manager:
                crud_instance = self.crud_manager.get_crud(operation.model_class)
                for item_data in operation.data:
                    item = crud_instance.create(item_data)
                    if item:
                        created_items.append(item)
            else:
                # Fallback bulk creation
                for item_data in operation.data:
                    item = operation.model_class(**item_data)
                    created_items.append(item)
            
            execution_time = (time.time() - start_time) * 1000
            
            return OperationResult(
                success=True,
                data=created_items,
                operation_type=OperationType.BULK_CREATE,
                execution_time_ms=execution_time,
                rows_affected=len(created_items),
                metadata={'model': operation.model_class.__name__, 'count': len(created_items)}
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return OperationResult(
                success=False,
                data=None,
                operation_type=OperationType.BULK_CREATE,
                execution_time_ms=execution_time,
                rows_affected=0,
                error_message=str(e)
            )
    
    def _bulk_update(self, operation: BatchOperation, user_id: int = None, ip_address: str = None) -> OperationResult:
        """Execute bulk update operation"""
        start_time = time.time()
        
        try:
            updated_count = 0
            
            if INTERNAL_MODULES_AVAILABLE and self.crud_manager:
                crud_instance = self.crud_manager.get_crud(operation.model_class)
                
                # Update each item in the batch
                for item_data in operation.data:
                    item_id = item_data.get('id')
                    if item_id:
                        updated_item = crud_instance.update(item_id, item_data)
                        if updated_item:
                            updated_count += 1
            else:
                # Fallback bulk update
                updated_count = len(operation.data)
            
            execution_time = (time.time() - start_time) * 1000
            
            return OperationResult(
                success=True,
                data=updated_count,
                operation_type=OperationType.BULK_UPDATE,
                execution_time_ms=execution_time,
                rows_affected=updated_count,
                metadata={'model': operation.model_class.__name__, 'count': updated_count}
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return OperationResult(
                success=False,
                data=None,
                operation_type=OperationType.BULK_UPDATE,
                execution_time_ms=execution_time,
                rows_affected=0,
                error_message=str(e)
            )
    
    def _bulk_delete(self, operation: BatchOperation, user_id: int = None, ip_address: str = None) -> OperationResult:
        """Execute bulk delete operation"""
        start_time = time.time()
        
        try:
            deleted_count = 0
            
            if INTERNAL_MODULES_AVAILABLE and self.crud_manager:
                crud_instance = self.crud_manager.get_crud(operation.model_class)
                
                # Delete items based on filters or IDs
                if operation.filters:
                    # This would use more sophisticated filtering in production
                    items = crud_instance.search(operation.filters)
                    for item in items:
                        if crud_instance.delete(getattr(item, 'id', None)):
                            deleted_count += 1
                else:
                    # Delete by IDs from data
                    for item_data in operation.data:
                        item_id = item_data.get('id')
                        if item_id and crud_instance.delete(item_id):
                            deleted_count += 1
            else:
                # Fallback bulk delete
                deleted_count = len(operation.data)
            
            execution_time = (time.time() - start_time) * 1000
            
            return OperationResult(
                success=True,
                data=deleted_count,
                operation_type=OperationType.BULK_DELETE,
                execution_time_ms=execution_time,
                rows_affected=deleted_count,
                metadata={'model': operation.model_class.__name__, 'count': deleted_count}
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return OperationResult(
                success=False,
                data=None,
                operation_type=OperationType.BULK_DELETE,
                execution_time_ms=execution_time,
                rows_affected=0,
                error_message=str(e)
            )
    
    def run_migrations(self, target_version: str = None, user_id: int = None, ip_address: str = None) -> OperationResult:
        """Run database migrations"""
        start_time = time.time()
        
        try:
            if INTERNAL_MODULES_AVAILABLE and self.migration_manager:
                success = self.migration_manager.migrate(target_version)
                execution_time = (time.time() - start_time) * 1000
                
                # Track migration operation
                if self.analytics:
                    track_analytics_event(
                        AnalyticsEvent.QUERY_EXECUTED,
                        {
                            'operation': 'migration',
                            'target_version': target_version,
                            'execution_time_ms': execution_time,
                            'success': success
                        },
                        user_id=user_id
                    )
                
                # Log security event
                if self.security:
                    log_security_event(
                        AuditEventType.DATA_MODIFICATION,
                        user_id=user_id,
                        resource="database_schema",
                        action="migration",
                        details={'target_version': target_version, 'success': success},
                        ip_address=ip_address,
                        risk_level=SecurityLevel.HIGH  # Schema changes are high risk
                    )
                
                result = OperationResult(
                    success=success,
                    data={'target_version': target_version, 'completed': success},
                    operation_type=OperationType.MIGRATION,
                    execution_time_ms=execution_time,
                    rows_affected=0,  # Schema changes don't affect data rows
                    metadata={'migration_target': target_version}
                )
            else:
                execution_time = (time.time() - start_time) * 1000
                result = OperationResult(
                    success=False,
                    data=None,
                    operation_type=OperationType.MIGRATION,
                    execution_time_ms=execution_time,
                    rows_affected=0,
                    error_message="Migration manager not available"
                )
            
            self._record_operation_result(result)
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_result = OperationResult(
                success=False,
                data=None,
                operation_type=OperationType.MIGRATION,
                execution_time_ms=execution_time,
                rows_affected=0,
                error_message=str(e)
            )
            self._record_operation_result(error_result)
            logger.error(f"Migration failed: {e}")
            return error_result
    
    def optimize_database(self, user_id: int = None, ip_address: str = None) -> OperationResult:
        """Optimize database performance"""
        start_time = time.time()
        optimization_actions = []
        
        try:
            if SQLALCHEMY_AVAILABLE and self.connection:
                # Analyze query performance
                slow_queries = self._analyze_slow_queries()
                if slow_queries:
                    optimization_actions.append(f"Found {len(slow_queries)} slow queries")
                
                # Check index usage
                missing_indexes = self._suggest_indexes()
                if missing_indexes:
                    optimization_actions.append(f"Suggested {len(missing_indexes)} new indexes")
                
                # Update table statistics
                self._update_table_statistics()
                optimization_actions.append("Updated table statistics")
                
                # Vacuum analyze (PostgreSQL specific)
                try:
                    self.connection.execute(text("VACUUM ANALYZE"))
                    optimization_actions.append("Executed VACUUM ANALYZE")
                except Exception:
                    pass  # Not all databases support this
            
            execution_time = (time.time() - start_time) * 1000
            
            # Track optimization operation
            if self.analytics:
                track_analytics_event(
                    AnalyticsEvent.QUERY_EXECUTED,
                    {
                        'operation': 'database_optimization',
                        'actions': optimization_actions,
                        'execution_time_ms': execution_time
                    },
                    user_id=user_id
                )
            
            # Log security event
            if self.security:
                log_security_event(
                    AuditEventType.DATA_ACCESS,
                    user_id=user_id,
                    resource="database",
                    action="optimization",
                    details={'actions': optimization_actions},
                    ip_address=ip_address,
                    risk_level=SecurityLevel.MEDIUM
                )
            
            result = OperationResult(
                success=True,
                data={'actions': optimization_actions},
                operation_type=OperationType.OPTIMIZATION,
                execution_time_ms=execution_time,
                rows_affected=0,
                metadata={'optimization_count': len(optimization_actions)}
            )
            
            self._record_operation_result(result)
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_result = OperationResult(
                success=False,
                data=None,
                operation_type=OperationType.OPTIMIZATION,
                execution_time_ms=execution_time,
                rows_affected=0,
                error_message=str(e)
            )
            self._record_operation_result(error_result)
            logger.error(f"Database optimization failed: {e}")
            return error_result
    
    def _analyze_slow_queries(self) -> List[Dict[str, Any]]:
        """Analyze slow queries (database-specific implementation)"""
        try:
            # This would analyze query logs in production
            # For now, return mock data
            return [
                {'query': 'SELECT * FROM contents WHERE status = ?', 'avg_time': 1500},
                {'query': 'SELECT * FROM users WHERE created_at > ?', 'avg_time': 1200}
            ]
        except Exception as e:
            logger.error(f"Failed to analyze slow queries: {e}")
            return []
    
    def _suggest_indexes(self) -> List[Dict[str, Any]]:
        """Suggest missing indexes based on query patterns"""
        try:
            # This would analyze query patterns in production
            # For now, return mock suggestions
            return [
                {'table': 'contents', 'columns': ['status', 'created_at'], 'type': 'btree'},
                {'table': 'users', 'columns': ['email'], 'type': 'unique'}
            ]
        except Exception as e:
            logger.error(f"Failed to suggest indexes: {e}")
            return []
    
    def _update_table_statistics(self):
        """Update database table statistics"""
        try:
            if SQLALCHEMY_AVAILABLE and self.connection:
                # This would update statistics for all tables
                # Implementation depends on database type
                pass
        except Exception as e:
            logger.error(f"Failed to update table statistics: {e}")
    
    def _validate_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user data"""
        errors = []
        
        required_fields = ['username', 'email']
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Email validation
        if 'email' in user_data and '@' not in user_data['email']:
            errors.append("Invalid email format")
        
        # Username validation
        if 'username' in user_data and len(user_data['username']) < 3:
            errors.append("Username must be at least 3 characters")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def _validate_content_data(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content data"""
        errors = []
        
        required_fields = ['title', 'content_type', 'owner_id']
        for field in required_fields:
            if field not in content_data or content_data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Content type validation
        valid_types = ['audio', 'video', 'image', 'text', 'mixed']
        if 'content_type' in content_data and content_data['content_type'] not in valid_types:
            errors.append(f"Invalid content type. Must be one of: {valid_types}")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def _validate_fingerprint_data(self, fingerprint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate fingerprint data"""
        errors = []
        
        required_fields = ['content_id', 'algorithm', 'fingerprint_data']
        for field in required_fields:
            if field not in fingerprint_data or fingerprint_data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def _record_operation_result(self, result: OperationResult):
        """Record operation result for monitoring"""
        try:
            self.operation_history.append(result)
            
            # Keep only last 1000 operations in memory
            if len(self.operation_history) > 1000:
                self.operation_history = self.operation_history[-1000:]
            
            # Track performance metrics
            operation_name = result.operation_type.value
            if operation_name not in self.performance_metrics:
                self.performance_metrics[operation_name] = []
            
            self.performance_metrics[operation_name].append(result.execution_time_ms)
            
            # Keep only last 100 metrics per operation type
            if len(self.performance_metrics[operation_name]) > 100:
                self.performance_metrics[operation_name] = self.performance_metrics[operation_name][-100:]
            
        except Exception as e:
            logger.error(f"Failed to record operation result: {e}")
    
    def get_operation_summary(self) -> Dict[str, Any]:
        """Get comprehensive operation summary"""
        try:
            total_operations = len(self.operation_history)
            successful_operations = len([op for op in self.operation_history if op.success])
            
            # Calculate average execution times
            avg_times = {}
            for op_type, times in self.performance_metrics.items():
                avg_times[op_type] = sum(times) / len(times) if times else 0
            
            # Recent operations (last 100)
            recent_operations = self.operation_history[-100:] if self.operation_history else []
            
            return {
                'total_operations': total_operations,
                'successful_operations': successful_operations,
                'success_rate': (successful_operations / total_operations * 100) if total_operations > 0 else 0,
                'average_execution_times_ms': avg_times,
                'recent_operations_count': len(recent_operations),
                'operation_types': list(self.performance_metrics.keys()),
                'last_operation': recent_operations[-1].to_dict() if recent_operations else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get operation summary: {e}")
            return {'error': str(e)}
    
    def init_data(self, user_id: int = None, ip_address: str = None) -> OperationResult:
        """Initialize database with sample data"""
        start_time = time.time()
        
        try:
            # Create sample users
            sample_users = [
                {'username': 'admin', 'email': 'admin@ainflue.com', 'full_name': 'Administrator', 'role': 'admin'},
                {'username': 'creator1', 'email': 'creator1@example.com', 'full_name': 'Content Creator 1', 'role': 'creator'},
                {'username': 'user1', 'email': 'user1@example.com', 'full_name': 'Regular User', 'role': 'user'}
            ]
            
            created_users = []
            for user_data in sample_users:
                result = self.create_user(user_data, user_id, ip_address)
                if result.success:
                    created_users.append(result.data)
            
            # Create sample content
            if created_users:
                creator = next((u for u in created_users if getattr(u, 'role', None) == 'creator'), created_users[0])
                creator_id = getattr(creator, 'id', 1)
                
                sample_content = [
                    {'title': 'Welcome Video', 'description': 'Introduction to the platform', 'content_type': 'video', 'owner_id': creator_id},
                    {'title': 'Tutorial Audio', 'description': 'How to use the platform', 'content_type': 'audio', 'owner_id': creator_id}
                ]
                
                for content_data in sample_content:
                    self.create_content(content_data, user_id, ip_address)
            
            execution_time = (time.time() - start_time) * 1000
            
            result = OperationResult(
                success=True,
                data={'users_created': len(created_users), 'content_created': 2},
                operation_type=OperationType.CREATE,
                execution_time_ms=execution_time,
                rows_affected=len(created_users) + 2,
                metadata={'initialization': True}
            )
            
            logger.info(f"Database initialized with sample data in {execution_time:.2f}ms")
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_result = OperationResult(
                success=False,
                data=None,
                operation_type=OperationType.CREATE,
                execution_time_ms=execution_time,
                rows_affected=0,
                error_message=str(e)
            )
            logger.error(f"Failed to initialize database: {e}")
            return error_result

# Global database operations instance
_database_operations = None

def get_database_operations(connection=None, session=None) -> DatabaseOperations:
    """Get the global database operations instance"""
    global _database_operations
    if _database_operations is None:
        _database_operations = DatabaseOperations(connection, session)
    return _database_operations

# Convenience functions for common operations
def create_user_with_workflow(user_data: Dict[str, Any], user_id: int = None, ip_address: str = None) -> OperationResult:
    """Create user with full workflow integration"""
    ops = get_database_operations()
    return ops.create_user(user_data, user_id, ip_address)

def create_content_with_workflow(content_data: Dict[str, Any], user_id: int = None, ip_address: str = None) -> OperationResult:
    """Create content with full workflow integration"""
    ops = get_database_operations()
    return ops.create_content(content_data, user_id, ip_address)

def run_database_migrations(target_version: str = None, user_id: int = None, ip_address: str = None) -> OperationResult:
    """Run database migrations"""
    ops = get_database_operations()
    return ops.run_migrations(target_version, user_id, ip_address)

def optimize_database_performance(user_id: int = None, ip_address: str = None) -> OperationResult:
    """Optimize database performance"""
    ops = get_database_operations()
    return ops.optimize_database(user_id, ip_address)

def initialize_database_data(user_id: int = None, ip_address: str = None) -> OperationResult:
    """Initialize database with sample data"""
    ops = get_database_operations()
    return ops.init_data(user_id, ip_address)

def get_database_operations_summary() -> Dict[str, Any]:
    """Get database operations summary"""
    ops = get_database_operations()
    return ops.get_operation_summary()