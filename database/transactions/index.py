"""Transaction Index - Unified Transaction Management Interface

Comprehensive transaction management interface providing a single entry point
for all transaction operations, coordination, and monitoring across the
IA Influencer Agent platform.

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
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Union, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone

from .transaction_coordinator import TransactionCoordinator, TransactionContext, TransactionPriority
from .distributed_transactions import DistributedTransactionManager, DistributedTransaction
from .atomicity_manager import AtomicityManager, AtomicOperationType
from .performance_monitor import PerformanceMonitor, TransactionMetrics
from .security_manager import TransactionSecurityManager, SecurityContext, SecurityLevel

logger = logging.getLogger(__name__)


@dataclass
class TransactionConfig:
    """
Transaction configuration settings"""
    coordinator_max_concurrent: int = 1000
    distributed_redis_url: str = "redis://localhost:6379"
    atomicity_max_operations: int = 100
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    performance_monitoring: bool = True
    audit_logging: bool = True
    encryption_enabled: bool = True
    timeout_seconds: int = 300
    max_retries: int = 3


class TransactionManager:
    """
    Unified transaction management system providing enterprise-grade transaction
    coordination, security, monitoring, and compliance for the IA Influencer platform.
    
    Features:
    - Unified transaction interface
    - ACID compliance across distributed systems
    - Real-time performance monitoring
    - Advanced security controls
    - Comprehensive audit logging
    - Multi-database coordination
    - Microservices transaction support
    - Creator economy business logic integration
    """
    
    def __init__(self, config: Optional[TransactionConfig] = None):
        self.config = config or TransactionConfig()
        
        # Core transaction components
        self.coordinator = TransactionCoordinator(self.config.coordinator_max_concurrent)
        self.distributed_manager = DistributedTransactionManager(self.config.distributed_redis_url)
        self.atomicity_manager = AtomicityManager(self.config.atomicity_max_operations)
        self.performance_monitor = PerformanceMonitor() if self.config.performance_monitoring else None
        self.security_manager = TransactionSecurityManager()
        
        # Transaction registry
        self.active_transactions: Dict[str, Dict[str, Any]] = {}
        
        # Business logic handlers
        self.business_handlers: Dict[str, Callable] = {}
        
        self._initialized = False
        self._shutdown = False
        
        logger.info("TransactionManager created with config: %s", self.config)
    
    async def initialize(self) -> None:
        """Initialize all transaction components"""
        if self._initialized:
            return
        
        try:
            # Initialize distributed transaction manager
            await self.distributed_manager.initialize()
            
            # Start performance monitoring
            if self.performance_monitor:
                self.performance_monitor.start_monitoring()
            
            # Register default business logic handlers
            self._register_default_handlers()
            
            # Start background cleanup tasks
            asyncio.create_task(self._cleanup_completed_transactions())
            
            self._initialized = True
            logger.info("TransactionManager initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize TransactionManager: %s", str(e))
            raise
    
    async def begin_creator_transaction(
        self,
        creator_id: str,
        transaction_type: str,
        content_data: Optional[Dict[str, Any]] = None,
        security_context: Optional[SecurityContext] = None,
        priority: TransactionPriority = TransactionPriority.NORMAL,
        timeout: int = 300
    ) -> str:
        """
        Begin a new creator-specific transaction for content operations
        
        This is the main entry point for creator economy transactions including:
        - Content upload and processing
        - AI fingerprinting and protection
        - Monetization setup
        - Revenue tracking
        - Collaboration matching
        """
        
        if not self._initialized:
            await self.initialize()
        
        # Validate security context
        if security_context and not self._validate_creator_access(creator_id, security_context):
            raise PermissionError(f"Access denied for creator {creator_id}")
        
        # Start performance monitoring
        metrics = None
        if self.performance_monitor:
            metrics = self.performance_monitor.start_transaction(
                f"creator_{creator_id}_{int(time.time())}",
                transaction_type
            )
        
        try:
            # Begin coordinated transaction
            context = await self.coordinator.begin_transaction(
                priority=priority,
                timeout=timeout,
                metadata={
                    'creator_id': creator_id,
                    'transaction_type': transaction_type,
                    'content_data': content_data,
                    'business_context': 'creator_economy'
                }
            )
            
            # Register transaction
            self.active_transactions[context.transaction_id] = {
                'type': 'creator_transaction',
                'creator_id': creator_id,
                'transaction_type': transaction_type,
                'context': context,
                'metrics': metrics,
                'security_context': security_context,
                'created_at': datetime.now(timezone.utc)
            }
            
            logger.info("Creator transaction started: %s (creator=%s, type=%s)",
                       context.transaction_id, creator_id, transaction_type)
            
            return context.transaction_id
            
        except Exception as e:
            if metrics and self.performance_monitor:
                self.performance_monitor.end_transaction(metrics.transaction_id, success=False)
            logger.error("Failed to start creator transaction: %s", str(e))
            raise
    
    async def execute_content_protection_workflow(
        self,
        transaction_id: str,
        content_file: bytes,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute complete content protection workflow
        
        Workflow: Upload → Fingerprint → Vector Storage → Protection Registration
        """
        
        transaction_info = self.active_transactions.get(transaction_id)
        if not transaction_info:
            raise ValueError(f"Transaction not found: {transaction_id}")
        
        # Create atomic operation group
        group_id = await self.atomicity_manager.create_operation_group()
        
        try:
            # Add fingerprinting operation
            fingerprint_op_id = await self.atomicity_manager.add_operation(
                group_id=group_id,
                execute_func=lambda: self._generate_content_fingerprint(content_file, content_type),
                rollback_func=lambda: self._cleanup_fingerprint_data(transaction_id),
                operation_type=AtomicOperationType.CUSTOM,
                metadata={'step': 'fingerprinting', 'content_type': content_type}
            )
            
            # Add vector storage operation
            vector_op_id = await self.atomicity_manager.add_operation(
                group_id=group_id,
                execute_func=lambda: self._store_content_vectors(transaction_id),
                rollback_func=lambda: self._cleanup_vector_data(transaction_id),
                operation_type=AtomicOperationType.DATABASE_WRITE,
                dependencies=[fingerprint_op_id],
                metadata={'step': 'vector_storage'}
            )
            
            # Add protection registration operation
            protection_op_id = await self.atomicity_manager.add_operation(
                group_id=group_id,
                execute_func=lambda: self._register_content_protection(transaction_id, metadata),
                rollback_func=lambda: self._cleanup_protection_registration(transaction_id),
                operation_type=AtomicOperationType.DATABASE_WRITE,
                dependencies=[vector_op_id],
                metadata={'step': 'protection_registration'}
            )
            
            # Execute atomic operations
            success = await self.atomicity_manager.execute_atomic_group(group_id)
            
            if not success:
                raise RuntimeError("Content protection workflow failed")
            
            # Update transaction metrics
            if transaction_info['metrics'] and self.performance_monitor:
                self.performance_monitor.update_transaction_metric(
                    transaction_info['metrics'].transaction_id,
                    'content_protected',
                    True
                )
            
            logger.info("Content protection workflow completed: %s", transaction_id)
            
            return {
                'transaction_id': transaction_id,
                'fingerprint_generated': True,
                'vectors_stored': True,
                'protection_registered': True,
                'workflow_completed': True
            }
            
        except Exception as e:
            logger.error("Content protection workflow failed: %s", str(e))
            raise
    
    async def execute_monetization_setup(
        self,
        transaction_id: str,
        content_id: str,
        revenue_settings: Dict[str, Any],
        platform_integrations: List[str]
    ) -> Dict[str, Any]:
        """
        Execute monetization setup workflow
        
        Workflow: Revenue Config → Platform Setup → Payment Integration → Analytics Setup
        """
        
        transaction_info = self.active_transactions.get(transaction_id)
        if not transaction_info:
            raise ValueError(f"Transaction not found: {transaction_id}")
        
        # Use distributed transaction for cross-service coordination
        participants = []
        
        # Add revenue service participant
        participants.append({
            'service_id': 'revenue_service',
            'endpoint': 'http://revenue-service/api/v1',
            'metadata': {'content_id': content_id, 'settings': revenue_settings}
        })
        
        # Add platform integration participants
        for platform in platform_integrations:
            participants.append({
                'service_id': f'platform_{platform}',
                'endpoint': f'http://platform-{platform}/api/v1',
                'metadata': {'content_id': content_id, 'platform': platform}
            })
        
        # Add payment service participant
        participants.append({
            'service_id': 'payment_service',
            'endpoint': 'http://payment-service/api/v1',
            'metadata': {'content_id': content_id, 'revenue_settings': revenue_settings}
        })
        
        try:
            # Begin distributed transaction
            distributed_tx = await self.distributed_manager.begin_distributed_transaction(
                participants=participants,
                timeout=300
            )
            
            # Execute two-phase commit
            success = await self.distributed_manager.execute_two_phase_commit(
                distributed_tx.transaction_id
            )
            
            if not success:
                raise RuntimeError("Monetization setup failed")
            
            logger.info("Monetization setup completed: %s", transaction_id)
            
            return {
                'transaction_id': transaction_id,
                'distributed_transaction_id': distributed_tx.transaction_id,
                'revenue_configured': True,
                'platforms_integrated': platform_integrations,
                'payment_setup': True,
                'monetization_active': True
            }
            
        except Exception as e:
            logger.error("Monetization setup failed: %s", str(e))
            raise
    
    async def commit_creator_transaction(self, transaction_id: str) -> bool:
        """Commit creator transaction with full workflow completion"""
        
        transaction_info = self.active_transactions.get(transaction_id)
        if not transaction_info:
            raise ValueError(f"Transaction not found: {transaction_id}")
        
        try:
            context = transaction_info['context']
            
            # Prepare transaction
            if not await self.coordinator.prepare_transaction(transaction_id):
                raise RuntimeError("Transaction preparation failed")
            
            # Commit transaction
            success = await self.coordinator.commit_transaction(transaction_id)
            
            if success:
                # Complete performance monitoring
                if transaction_info['metrics'] and self.performance_monitor:
                    self.performance_monitor.end_transaction(
                        transaction_info['metrics'].transaction_id,
                        success=True
                    )
                
                # Execute business logic completion handlers
                await self._execute_completion_handlers(transaction_info)
                
                logger.info("Creator transaction committed successfully: %s", transaction_id)
            
            return success
            
        except Exception as e:
            logger.error("Failed to commit creator transaction %s: %s", transaction_id, str(e))
            await self.rollback_creator_transaction(transaction_id)
            return False
        finally:
            # Cleanup transaction
            self.active_transactions.pop(transaction_id, None)
    
    async def rollback_creator_transaction(self, transaction_id: str) -> bool:
        """Rollback creator transaction with cleanup"""
        
        transaction_info = self.active_transactions.get(transaction_id)
        if not transaction_info:
            logger.warning("Transaction not found for rollback: %s", transaction_id)
            return False
        
        try:
            # Rollback coordinated transaction
            success = await self.coordinator.rollback_transaction(transaction_id)
            
            # Complete performance monitoring with failure
            if transaction_info['metrics'] and self.performance_monitor:
                self.performance_monitor.end_transaction(
                    transaction_info['metrics'].transaction_id,
                    success=False
                )
            
            # Execute rollback handlers
            await self._execute_rollback_handlers(transaction_info)
            
            logger.info("Creator transaction rolled back: %s", transaction_id)
            return success
            
        except Exception as e:
            logger.error("Failed to rollback creator transaction %s: %s", transaction_id, str(e))
            return False
        finally:
            # Cleanup transaction
            self.active_transactions.pop(transaction_id, None)
    
    @asynccontextmanager
    async def creator_transaction_context(
        self,
        creator_id: str,
        transaction_type: str,
        content_data: Optional[Dict[str, Any]] = None,
        security_context: Optional[SecurityContext] = None,
        priority: TransactionPriority = TransactionPriority.NORMAL
    ):
        """Context manager for creator transactions with automatic commit/rollback"""
        
        transaction_id = await self.begin_creator_transaction(
            creator_id=creator_id,
            transaction_type=transaction_type,
            content_data=content_data,
            security_context=security_context,
            priority=priority
        )
        
        try:
            yield transaction_id
            
            # Auto-commit on successful completion
            success = await self.commit_creator_transaction(transaction_id)
            if not success:
                raise RuntimeError("Transaction commit failed")
                
        except Exception as e:
            # Auto-rollback on error
            await self.rollback_creator_transaction(transaction_id)
            raise e
    
    async def get_transaction_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive transaction status"""
        
        transaction_info = self.active_transactions.get(transaction_id)
        if not transaction_info:
            return None
        
        # Get coordinator status
        coordinator_status = await self.coordinator.get_transaction_status(transaction_id)
        
        # Get performance metrics
        performance_metrics = None
        if transaction_info['metrics'] and self.performance_monitor:
            performance_metrics = self.performance_monitor.get_transaction_details(
                transaction_info['metrics'].transaction_id
            )
        
        return {
            'transaction_id': transaction_id,
            'creator_id': transaction_info['creator_id'],
            'transaction_type': transaction_info['transaction_type'],
            'created_at': transaction_info['created_at'].isoformat(),
            'coordinator_status': coordinator_status,
            'performance_metrics': performance_metrics,
            'business_context': 'creator_economy'
        }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """
Get comprehensive system performance metrics"""
        
        metrics = {
            'active_transactions': len(self.active_transactions),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Add coordinator metrics
        metrics['coordinator'] = await self.coordinator.get_performance_metrics()
        
        # Add atomicity manager metrics
        metrics['atomicity'] = await self.atomicity_manager.get_performance_metrics()
        
        # Add performance monitoring metrics
        if self.performance_monitor:
            metrics['performance'] = self.performance_monitor.get_current_metrics()
        
        return metrics
    
    def _validate_creator_access(self, creator_id: str, security_context: SecurityContext) -> bool:
        """
Validate creator access permissions"""
        
        # Check if user has access to this creator account
        if security_context.user_id != creator_id:
            # Check if user has admin permissions or is authorized for this creator
            required_permissions = {'creator_admin', f'creator_access_{creator_id}'}
            if not required_permissions.intersection(security_context.permissions):
                return False
        
        return True
    
    async def _generate_content_fingerprint(self, content_file: bytes, content_type: str) -> Dict[str, Any]:
        """
Generate content fingerprint (placeholder for actual implementation)"""
        # This would integrate with the actual fingerprinting engines
        await asyncio.sleep(0.1)  # Simulate processing
        return {
            'fingerprint_hash': f'fp_{hash(content_file)}',
            'content_type': content_type,
            'size': len(content_file)
        }
    
    async def _store_content_vectors(self, transaction_id: str) -> bool:
        """
Store content vectors in vector database (placeholder)"""
        await asyncio.sleep(0.05)  # Simulate storage
        return True
    
    async def _register_content_protection(self, transaction_id: str, metadata: Optional[Dict[str, Any]]) -> bool:
        """
Register content for protection monitoring (placeholder)"""
        await asyncio.sleep(0.05)  # Simulate registration
        return True
    
    async def _cleanup_fingerprint_data(self, transaction_id: str) -> None:
        """
Cleanup fingerprint data on rollback"""
        logger.debug("Cleaning up fingerprint data for transaction: %s", transaction_id)
    
    async def _cleanup_vector_data(self, transaction_id: str) -> None:
        """Cleanup vector data on rollback"""
        logger.debug("Cleaning up vector data for transaction: %s", transaction_id)
    
    async def _cleanup_protection_registration(self, transaction_id: str) -> None:
        """Cleanup protection registration on rollback"""
        logger.debug("Cleaning up protection registration for transaction: %s", transaction_id)
    
    def _register_default_handlers(self) -> None:
        """Register default business logic handlers"""
        
        self.business_handlers.update({
            'content_upload': self._handle_content_upload,
            'monetization_setup': self._handle_monetization_setup,
            'collaboration_request': self._handle_collaboration_request,
            'revenue_distribution': self._handle_revenue_distribution,
        })
    
    async def _handle_content_upload(self, transaction_info: Dict[str, Any]) -> None:
        """
Handle content upload completion"""
        logger.info("Content upload completed for transaction: %s", 
                   transaction_info['context'].transaction_id)
    
    async def _handle_monetization_setup(self, transaction_info: Dict[str, Any]) -> None:
        """Handle monetization setup completion"""
        logger.info("Monetization setup completed for transaction: %s", 
                   transaction_info['context'].transaction_id)
    
    async def _handle_collaboration_request(self, transaction_info: Dict[str, Any]) -> None:
        """Handle collaboration request completion"""
        logger.info("Collaboration request completed for transaction: %s", 
                   transaction_info['context'].transaction_id)
    
    async def _handle_revenue_distribution(self, transaction_info: Dict[str, Any]) -> None:
        """Handle revenue distribution completion"""
        logger.info("Revenue distribution completed for transaction: %s", 
                   transaction_info['context'].transaction_id)
    
    async def _execute_completion_handlers(self, transaction_info: Dict[str, Any]) -> None:
        """Execute business logic completion handlers"""
        
        transaction_type = transaction_info['transaction_type']
        handler = self.business_handlers.get(transaction_type)
        
        if handler:
            try:
                await handler(transaction_info)
            except Exception as e:
                logger.error("Completion handler failed for %s: %s", transaction_type, str(e))
    
    async def _execute_rollback_handlers(self, transaction_info: Dict[str, Any]) -> None:
        """Execute rollback cleanup handlers"""
        
        logger.info("Executing rollback handlers for transaction: %s", 
                   transaction_info['context'].transaction_id)
        
        # Implement specific rollback logic based on transaction type
        transaction_type = transaction_info['transaction_type']
        
        if transaction_type == 'content_upload':
            await self._cleanup_content_upload(transaction_info)
        elif transaction_type == 'monetization_setup':
            await self._cleanup_monetization_setup(transaction_info)
    
    async def _cleanup_content_upload(self, transaction_info: Dict[str, Any]) -> None:
        """Cleanup content upload on rollback"""
        logger.debug("Cleaning up content upload for transaction: %s", 
                    transaction_info['context'].transaction_id)
    
    async def _cleanup_monetization_setup(self, transaction_info: Dict[str, Any]) -> None:
        """Cleanup monetization setup on rollback"""
        logger.debug("Cleaning up monetization setup for transaction: %s", 
                    transaction_info['context'].transaction_id)
    
    async def _cleanup_completed_transactions(self) -> None:
        """Background task to cleanup completed transactions"""
        
        while not self._shutdown:
            try:
                cutoff_time = datetime.now(timezone.utc).timestamp() - 3600  # 1 hour ago
                
                completed_transactions = []
                for transaction_id, info in self.active_transactions.items():
                    if info['created_at'].timestamp() < cutoff_time:
                        coordinator_status = await self.coordinator.get_transaction_status(transaction_id)
                        if not coordinator_status:  # Transaction completed
                            completed_transactions.append(transaction_id)
                
                for transaction_id in completed_transactions:
                    self.active_transactions.pop(transaction_id, None)
                    logger.debug("Cleaned up completed transaction: %s", transaction_id)
                
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except Exception as e:
                logger.error("Error in transaction cleanup: %s", str(e))
                await asyncio.sleep(60)
    
    async def shutdown(self) -> None:
        """Graceful shutdown of transaction manager"""
        logger.info("Shutting down TransactionManager...")
        
        self._shutdown = True
        
        # Rollback all active transactions
        active_transaction_ids = list(self.active_transactions.keys())
        for transaction_id in active_transaction_ids:
            try:
                await self.rollback_creator_transaction(transaction_id)
            except Exception as e:
                logger.error("Error rolling back transaction %s during shutdown: %s", 
                           transaction_id, str(e))
        
        # Shutdown components
        await self.coordinator.shutdown()
        await self.distributed_manager.shutdown()
        await self.atomicity_manager.shutdown()
        
        if self.performance_monitor:
            await self.performance_monitor.shutdown()
        
        await self.security_manager.shutdown()
        
        logger.info("TransactionManager shutdown complete")


# Convenience functions for common operations
async def create_transaction_manager(config: Optional[TransactionConfig] = None) -> TransactionManager:
    """Create and initialize transaction manager"""
    manager = TransactionManager(config)
    await manager.initialize()
    return manager


# Global transaction manager instance (singleton pattern)
_global_transaction_manager: Optional[TransactionManager] = None


async def get_transaction_manager() -> TransactionManager:
    """
Get global transaction manager instance"""
    global _global_transaction_manager
    
    if _global_transaction_manager is None:
        _global_transaction_manager = await create_transaction_manager()
    
    return _global_transaction_manager
