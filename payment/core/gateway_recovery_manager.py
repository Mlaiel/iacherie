"""💳 Gateway Recovery Manager
============================

Enterprise recovery system for failed payment transactions with intelligent
retry logic, backoff strategies, manual intervention workflows, and recovery analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    """Recovery strategy types"""
    IMMEDIATE_RETRY = "immediate_retry"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    PROVIDER_FAILOVER = "provider_failover"
    MANUAL_INTERVENTION = "manual_intervention"
    CUSTOMER_CONTACT = "customer_contact"
    ALTERNATIVE_PAYMENT = "alternative_payment"


class FailureCategory(Enum):
    """Payment failure categories"""
    NETWORK_ERROR = "network_error"
    PROVIDER_ERROR = "provider_error"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    DECLINED_CARD = "declined_card"
    EXPIRED_CARD = "expired_card"
    AUTHENTICATION_FAILED = "authentication_failed"
    FRAUD_DETECTED = "fraud_detected"
    LIMIT_EXCEEDED = "limit_exceeded"
    INVALID_DATA = "invalid_data"
    SYSTEM_ERROR = "system_error"
    TIMEOUT = "timeout"
    UNKNOWN_ERROR = "unknown_error"


class RecoveryStatus(Enum):
    """Recovery attempt status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    ABANDONED = "abandoned"
    MANUAL_REVIEW = "manual_review"
    CUSTOMER_ACTION_REQUIRED = "customer_action_required"


class InterventionType(Enum):
    """Manual intervention types"""
    ADMIN_REVIEW = "admin_review"
    CUSTOMER_CONTACT = "customer_contact"
    PROVIDER_ESCALATION = "provider_escalation"
    FRAUD_INVESTIGATION = "fraud_investigation"
    TECHNICAL_ANALYSIS = "technical_analysis"


@dataclass
class FailedTransaction:
    """Failed transaction record"""
    transaction_id: str
    original_amount: Decimal
    currency: str
    customer_id: str
    merchant_id: str
    provider: str
    failure_category: FailureCategory
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    failed_at: datetime = field(default_factory=datetime.now)
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryAttempt:
    """Recovery attempt record"""
    attempt_id: str
    transaction_id: str
    strategy: RecoveryStrategy
    status: RecoveryStatus
    attempted_at: datetime
    completed_at: Optional[datetime] = None
    success: bool = False
    new_transaction_id: Optional[str] = None
    error_message: Optional[str] = None
    provider_used: Optional[str] = None
    amount_recovered: Optional[Decimal] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ManualIntervention:
    """Manual intervention request"""
    intervention_id: str
    transaction_id: str
    intervention_type: InterventionType
    assigned_to: Optional[str] = None
    priority: int = 1  # 1=low, 5=critical
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None
    status: str = "open"


@dataclass
class RecoveryConfiguration:
    """Recovery configuration for different failure types"""
    failure_category: FailureCategory
    strategies: List[RecoveryStrategy]
    max_retries: int = 3
    retry_delays: List[int] = field(default_factory=lambda: [5, 30, 300])  # seconds
    enable_provider_failover: bool = True
    require_manual_review: bool = False
    customer_notification: bool = True
    recovery_timeout_hours: int = 24


class GatewayRecoveryManager:
    """Enterprise gateway recovery management system"""

    def __init__(self) -> None:
        self.failed_transactions: Dict[str, FailedTransaction] = {}
        self.recovery_attempts: Dict[str, List[RecoveryAttempt]] = {}
        self.manual_interventions: Dict[str, ManualIntervention] = {}
        
        # Recovery configurations by failure category
        self.recovery_configs = self._setup_default_configs()
        
        # Recovery workers
        self.recovery_queue: asyncio.Queue = asyncio.Queue()
        self.workers: List[asyncio.Task] = []
        self.worker_count = 3
        
        # Provider failover order
        self.provider_failover_order = {
            'stripe': ['paypal', 'wise'],
            'paypal': ['stripe', 'wise'],
            'wise': ['stripe', 'paypal'],
            'crypto': ['stripe', 'paypal']
        }
        
        # Statistics
        self.recovery_stats = {
            'total_failures': 0,
            'total_recoveries': 0,
            'success_rate': 0.0,
            'avg_recovery_time': 0.0
        }

    async def initialize(self) -> None:
        """Initialize recovery manager"""
        # Start recovery workers
        for i in range(self.worker_count):
            worker = asyncio.create_task(self._recovery_worker(f"recovery-worker-{i}"))
            self.workers.append(worker)
        
        # Start monitoring task
        monitor_task = asyncio.create_task(self._monitor_recovery_timeouts())
        self.workers.append(monitor_task)
        
        logger.info(f"Gateway recovery manager initialized with {self.worker_count} workers")

    async def register_failed_transaction(self, 
                                        transaction_id: str,
                                        amount: Decimal,
                                        currency: str,
                                        customer_id: str,
                                        merchant_id: str,
                                        provider: str,
                                        error_code: Optional[str] = None,
                                        error_message: Optional[str] = None,
                                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """Register a failed transaction for recovery"""
        
        # Categorize the failure
        failure_category = self._categorize_failure(error_code, error_message, provider)
        
        # Create failed transaction record
        failed_tx = FailedTransaction(
            transaction_id=transaction_id,
            original_amount=amount,
            currency=currency,
            customer_id=customer_id,
            merchant_id=merchant_id,
            provider=provider,
            failure_category=failure_category,
            error_code=error_code,
            error_message=error_message,
            metadata=metadata or {}
        )
        
        # Store failed transaction
        self.failed_transactions[transaction_id] = failed_tx
        self.recovery_attempts[transaction_id] = []
        
        # Get recovery configuration
        config = self.recovery_configs.get(failure_category)
        if config:
            failed_tx.max_retries = config.max_retries
        
        # Queue for recovery
        await self.recovery_queue.put(transaction_id)
        
        # Update statistics
        self.recovery_stats['total_failures'] += 1
        
        logger.info(f"Failed transaction {transaction_id} registered for recovery. Category: {failure_category}")
        
        return transaction_id

    async def _recovery_worker(self, worker_id -> None: str) -> None:
        """Recovery worker that processes failed transactions"""
        logger.info(f"Recovery worker {worker_id} started")
        
        while True:
            try:
                # Get failed transaction ID
                transaction_id = await self.recovery_queue.get()
                
                # Process recovery
                await self._process_recovery(transaction_id)
                
                self.recovery_queue.task_done()
                
            except Exception as e:
                logger.error(f"Recovery worker {worker_id} error: {e}")
                await asyncio.sleep(1)

    async def _process_recovery(self, transaction_id -> None: str) -> None:
        """Process recovery for a failed transaction"""
        
        failed_tx = self.failed_transactions.get(transaction_id)
        if not failed_tx:
            logger.warning(f"Failed transaction {transaction_id} not found")
            return
        
        # Check if max retries exceeded
        if failed_tx.retry_count >= failed_tx.max_retries:
            logger.info(f"Max retries exceeded for transaction {transaction_id}")
            await self._handle_max_retries_exceeded(transaction_id)
            return
        
        # Get recovery configuration
        config = self.recovery_configs.get(failed_tx.failure_category)
        if not config:
            logger.warning(f"No recovery config for category {failed_tx.failure_category}")
            return
        
        # Select recovery strategy
        strategy = self._select_recovery_strategy(failed_tx, config)
        
        # Execute recovery attempt
        attempt = await self._execute_recovery_attempt(transaction_id, strategy)
        
        # Store attempt
        self.recovery_attempts[transaction_id].append(attempt)
        failed_tx.retry_count += 1
        
        # Handle result
        if attempt.success:
            await self._handle_successful_recovery(transaction_id, attempt)
        else:
            await self._handle_failed_recovery(transaction_id, attempt)

    def _select_recovery_strategy(self, 
                                failed_tx: FailedTransaction, 
                                config: RecoveryConfiguration) -> RecoveryStrategy:
        """Select appropriate recovery strategy"""
        
        # If first retry, try immediate retry for network/timeout errors
        if (failed_tx.retry_count == 0 and 
            failed_tx.failure_category in [FailureCategory.NETWORK_ERROR, FailureCategory.TIMEOUT]):
            return RecoveryStrategy.IMMEDIATE_RETRY
        
        # For provider errors, try failover
        if (failed_tx.failure_category == FailureCategory.PROVIDER_ERROR and 
            config.enable_provider_failover):
            return RecoveryStrategy.PROVIDER_FAILOVER
        
        # For customer-related issues, require manual intervention
        if failed_tx.failure_category in [
            FailureCategory.INSUFFICIENT_FUNDS,
            FailureCategory.DECLINED_CARD,
            FailureCategory.EXPIRED_CARD
        ]:
            return RecoveryStrategy.CUSTOMER_CONTACT
        
        # For fraud detection, require manual review
        if failed_tx.failure_category == FailureCategory.FRAUD_DETECTED:
            return RecoveryStrategy.MANUAL_INTERVENTION
        
        # Default to exponential backoff
        return RecoveryStrategy.EXPONENTIAL_BACKOFF

    async def _execute_recovery_attempt(self, 
                                      transaction_id: str, 
                                      strategy: RecoveryStrategy) -> RecoveryAttempt:
        """Execute a recovery attempt"""
        
        attempt = RecoveryAttempt(
            attempt_id=str(uuid.uuid4()),
            transaction_id=transaction_id,
            strategy=strategy,
            status=RecoveryStatus.IN_PROGRESS,
            attempted_at=datetime.now()
        )
        
        try:
            if strategy == RecoveryStrategy.IMMEDIATE_RETRY:
                success = await self._immediate_retry(transaction_id, attempt)
            
            elif strategy == RecoveryStrategy.EXPONENTIAL_BACKOFF:
                success = await self._exponential_backoff_retry(transaction_id, attempt)
            
            elif strategy == RecoveryStrategy.PROVIDER_FAILOVER:
                success = await self._provider_failover(transaction_id, attempt)
            
            elif strategy == RecoveryStrategy.MANUAL_INTERVENTION:
                success = await self._request_manual_intervention(transaction_id, attempt)
            
            elif strategy == RecoveryStrategy.CUSTOMER_CONTACT:
                success = await self._initiate_customer_contact(transaction_id, attempt)
            
            else:
                logger.warning(f"Unsupported recovery strategy: {strategy}")
                success = False
            
            attempt.success = success
            attempt.status = RecoveryStatus.SUCCESSFUL if success else RecoveryStatus.FAILED
            
        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
            attempt.success = False
            attempt.status = RecoveryStatus.FAILED
            attempt.error_message = str(e)
        
        attempt.completed_at = datetime.now()
        return attempt

    async def _immediate_retry(self, transaction_id: str, attempt: RecoveryAttempt) -> bool:
        """Immediate retry with same parameters"""
        failed_tx = self.failed_transactions[transaction_id]
        
        # Simulate retry with original payment processor
        # In real implementation, this would call the actual payment processor
        
        logger.info(f"Immediate retry for transaction {transaction_id}")
        
        # Simulate success rate based on failure category
        if failed_tx.failure_category == FailureCategory.NETWORK_ERROR:
            success_rate = 0.7
        elif failed_tx.failure_category == FailureCategory.TIMEOUT:
            success_rate = 0.6
        else:
            success_rate = 0.3
        
        # Simulate processing delay
        await asyncio.sleep(1)
        
        # Simulate result
        import random
        success = random.random() < success_rate
        
        if success:
            attempt.new_transaction_id = f"retry_{transaction_id}_{attempt.attempt_id[:8]}"
            attempt.provider_used = failed_tx.provider
            attempt.amount_recovered = failed_tx.original_amount
        
        return success

    async def _exponential_backoff_retry(self, transaction_id: str, attempt: RecoveryAttempt) -> bool:
        """Retry with exponential backoff delay"""
        failed_tx = self.failed_transactions[transaction_id]
        
        # Calculate delay
        delay = min(300, 2 ** failed_tx.retry_count)  # Max 5 minutes
        
        logger.info(f"Exponential backoff retry for transaction {transaction_id}, delay: {delay}s")
        
        # Wait for backoff period
        await asyncio.sleep(delay)
        
        # Retry transaction
        return await self._immediate_retry(transaction_id, attempt)

    async def _provider_failover(self, transaction_id: str, attempt: RecoveryAttempt) -> bool:
        """Failover to alternative payment provider"""
        failed_tx = self.failed_transactions[transaction_id]
        
        # Get failover providers
        failover_providers = self.provider_failover_order.get(failed_tx.provider, [])
        
        if not failover_providers:
            logger.warning(f"No failover providers for {failed_tx.provider}")
            return False
        
        # Try each failover provider
        for provider in failover_providers:
            logger.info(f"Attempting failover to provider {provider} for transaction {transaction_id}")
            
            # Simulate provider call
            await asyncio.sleep(2)
            
            # Simulate success rate per provider
            success_rates = {'stripe': 0.8, 'paypal': 0.7, 'wise': 0.6}
            success_rate = success_rates.get(provider, 0.5)
            
            import random
            if random.random() < success_rate:
                attempt.new_transaction_id = f"failover_{transaction_id}_{provider}"
                attempt.provider_used = provider
                attempt.amount_recovered = failed_tx.original_amount
                return True
        
        return False

    async def _request_manual_intervention(self, transaction_id: str, attempt: RecoveryAttempt) -> bool:
        """Request manual intervention for complex cases"""
        failed_tx = self.failed_transactions[transaction_id]
        
        # Determine intervention type
        if failed_tx.failure_category == FailureCategory.FRAUD_DETECTED:
            intervention_type = InterventionType.FRAUD_INVESTIGATION
            priority = 4
        elif failed_tx.failure_category == FailureCategory.SYSTEM_ERROR:
            intervention_type = InterventionType.TECHNICAL_ANALYSIS
            priority = 3
        else:
            intervention_type = InterventionType.ADMIN_REVIEW
            priority = 2
        
        # Create intervention request
        intervention = ManualIntervention(
            intervention_id=str(uuid.uuid4()),
            transaction_id=transaction_id,
            intervention_type=intervention_type,
            priority=priority,
            description=f"Recovery required for {failed_tx.failure_category.value}: {failed_tx.error_message}"
        )
        
        # Store intervention
        self.manual_interventions[intervention.intervention_id] = intervention
        
        # Update attempt
        attempt.status = RecoveryStatus.MANUAL_REVIEW
        attempt.metadata['intervention_id'] = intervention.intervention_id
        
        logger.info(f"Manual intervention requested for transaction {transaction_id}")
        
        return False  # Manual intervention doesn't immediately resolve

    async def _initiate_customer_contact(self, transaction_id: str, attempt: RecoveryAttempt) -> bool:
        """Initiate customer contact for payment method issues"""
        failed_tx = self.failed_transactions[transaction_id]
        
        # Create customer contact task
        contact_task = {
            'transaction_id': transaction_id,
            'customer_id': failed_tx.customer_id,
            'issue': failed_tx.failure_category.value,
            'amount': str(failed_tx.original_amount),
            'currency': failed_tx.currency
        }
        
        # In real implementation, this would integrate with customer service system
        logger.info(f"Customer contact initiated for transaction {transaction_id}")
        
        # Update attempt
        attempt.status = RecoveryStatus.CUSTOMER_ACTION_REQUIRED
        attempt.metadata['contact_task'] = contact_task
        
        return False  # Customer contact doesn't immediately resolve

    async def _handle_successful_recovery(self, transaction_id -> None: str, attempt -> None: RecoveryAttempt) -> None:
        """Handle successful recovery"""
        self.recovery_stats['total_recoveries'] += 1
        self.recovery_stats['success_rate'] = (
            self.recovery_stats['total_recoveries'] / self.recovery_stats['total_failures']
        )
        
        logger.info(f"Transaction {transaction_id} successfully recovered with {attempt.strategy.value}")

    async def _handle_failed_recovery(self, transaction_id -> None: str, attempt -> None: RecoveryAttempt) -> None:
        """Handle failed recovery attempt"""
        failed_tx = self.failed_transactions[transaction_id]
        
        # If not at max retries, will be retried by worker
        if failed_tx.retry_count < failed_tx.max_retries:
            # Calculate next retry delay
            config = self.recovery_configs.get(failed_tx.failure_category)
            if config and len(config.retry_delays) > failed_tx.retry_count:
                delay = config.retry_delays[failed_tx.retry_count]
                
                # Schedule next retry
                await asyncio.sleep(delay)
                await self.recovery_queue.put(transaction_id)
        
        logger.info(f"Recovery attempt failed for transaction {transaction_id}. Retry {failed_tx.retry_count}/{failed_tx.max_retries}")

    async def _handle_max_retries_exceeded(self, transaction_id -> None: str) -> None:
        """Handle when max retries are exceeded"""
        failed_tx = self.failed_transactions[transaction_id]
        
        # Create manual intervention for review
        intervention = ManualIntervention(
            intervention_id=str(uuid.uuid4()),
            transaction_id=transaction_id,
            intervention_type=InterventionType.ADMIN_REVIEW,
            priority=3,
            description=f"Max retries exceeded. Original error: {failed_tx.error_message}"
        )
        
        self.manual_interventions[intervention.intervention_id] = intervention
        
        logger.warning(f"Max retries exceeded for transaction {transaction_id}. Manual review required.")

    async def _monitor_recovery_timeouts(self) -> None:
        """Monitor and handle recovery timeouts"""
        while True:
            try:
                current_time = datetime.now()
                timeout_transactions = []
                
                for transaction_id, failed_tx in self.failed_transactions.items():
                    # Check if recovery timeout exceeded
                    config = self.recovery_configs.get(failed_tx.failure_category)
                    if config:
                        timeout_hours = config.recovery_timeout_hours
                        if current_time - failed_tx.failed_at > timedelta(hours=timeout_hours):
                            timeout_transactions.append(transaction_id)
                
                # Handle timeouts
                for transaction_id in timeout_transactions:
                    await self._handle_recovery_timeout(transaction_id)
                
                # Sleep for 1 hour before next check
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Recovery timeout monitoring error: {e}")
                await asyncio.sleep(60)

    async def _handle_recovery_timeout(self, transaction_id -> None: str) -> None:
        """Handle recovery timeout"""
        logger.warning(f"Recovery timeout for transaction {transaction_id}")
        
        # Create timeout intervention
        intervention = ManualIntervention(
            intervention_id=str(uuid.uuid4()),
            transaction_id=transaction_id,
            intervention_type=InterventionType.ADMIN_REVIEW,
            priority=2,
            description="Recovery timeout - requires final disposition"
        )
        
        self.manual_interventions[intervention.intervention_id] = intervention

    def _categorize_failure(self, 
                          error_code: Optional[str], 
                          error_message: Optional[str], 
                          provider: str) -> FailureCategory:
        """Categorize payment failure based on error details"""
        
        error_msg = (error_message or "").lower()
        error_cd = (error_code or "").lower()
        
        # Network and timeout errors
        if any(term in error_msg for term in ['timeout', 'connection', 'network']):
            return FailureCategory.NETWORK_ERROR
        
        if any(term in error_msg for term in ['timeout']):
            return FailureCategory.TIMEOUT
        
        # Insufficient funds
        if any(term in error_msg for term in ['insufficient', 'balance', 'funds']):
            return FailureCategory.INSUFFICIENT_FUNDS
        
        # Card issues
        if any(term in error_msg for term in ['declined', 'reject']):
            return FailureCategory.DECLINED_CARD
        
        if any(term in error_msg for term in ['expired', 'expiry']):
            return FailureCategory.EXPIRED_CARD
        
        # Authentication
        if any(term in error_msg for term in ['authentication', 'auth', '3ds']):
            return FailureCategory.AUTHENTICATION_FAILED
        
        # Fraud
        if any(term in error_msg for term in ['fraud', 'suspicious', 'blocked']):
            return FailureCategory.FRAUD_DETECTED
        
        # Limits
        if any(term in error_msg for term in ['limit', 'exceed', 'quota']):
            return FailureCategory.LIMIT_EXCEEDED
        
        # Invalid data
        if any(term in error_msg for term in ['invalid', 'format', 'validation']):
            return FailureCategory.INVALID_DATA
        
        # Provider-specific categorization
        if 'stripe' in provider.lower() and 'api' in error_msg:
            return FailureCategory.PROVIDER_ERROR
        
        # Default to system error
        return FailureCategory.SYSTEM_ERROR

    def _setup_default_configs(self) -> Dict[FailureCategory, RecoveryConfiguration]:
        """Setup default recovery configurations"""
        return {
            FailureCategory.NETWORK_ERROR: RecoveryConfiguration(
                failure_category=FailureCategory.NETWORK_ERROR,
                strategies=[RecoveryStrategy.IMMEDIATE_RETRY, RecoveryStrategy.EXPONENTIAL_BACKOFF],
                max_retries=3,
                retry_delays=[5, 30, 300]
            ),
            FailureCategory.PROVIDER_ERROR: RecoveryConfiguration(
                failure_category=FailureCategory.PROVIDER_ERROR,
                strategies=[RecoveryStrategy.PROVIDER_FAILOVER, RecoveryStrategy.EXPONENTIAL_BACKOFF],
                max_retries=2,
                enable_provider_failover=True
            ),
            FailureCategory.INSUFFICIENT_FUNDS: RecoveryConfiguration(
                failure_category=FailureCategory.INSUFFICIENT_FUNDS,
                strategies=[RecoveryStrategy.CUSTOMER_CONTACT],
                max_retries=1,
                customer_notification=True
            ),
            FailureCategory.FRAUD_DETECTED: RecoveryConfiguration(
                failure_category=FailureCategory.FRAUD_DETECTED,
                strategies=[RecoveryStrategy.MANUAL_INTERVENTION],
                max_retries=0,
                require_manual_review=True
            ),
            FailureCategory.TIMEOUT: RecoveryConfiguration(
                failure_category=FailureCategory.TIMEOUT,
                strategies=[RecoveryStrategy.IMMEDIATE_RETRY, RecoveryStrategy.EXPONENTIAL_BACKOFF],
                max_retries=2,
                retry_delays=[10, 60]
            )
        }

    async def get_recovery_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get recovery status for transaction"""
        failed_tx = self.failed_transactions.get(transaction_id)
        if not failed_tx:
            return None
        
        attempts = self.recovery_attempts.get(transaction_id, [])
        
        return {
            'transaction_id': transaction_id,
            'failure_category': failed_tx.failure_category.value,
            'retry_count': failed_tx.retry_count,
            'max_retries': failed_tx.max_retries,
            'failed_at': failed_tx.failed_at.isoformat(),
            'attempts': [
                {
                    'attempt_id': attempt.attempt_id,
                    'strategy': attempt.strategy.value,
                    'status': attempt.status.value,
                    'attempted_at': attempt.attempted_at.isoformat(),
                    'success': attempt.success
                }
                for attempt in attempts
            ]
        }

    async def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        return {
            'total_failures': self.recovery_stats['total_failures'],
            'total_recoveries': self.recovery_stats['total_recoveries'],
            'success_rate': round(self.recovery_stats['success_rate'], 3),
            'pending_recoveries': self.recovery_queue.qsize(),
            'manual_interventions': len(self.manual_interventions),
            'active_workers': len(self.workers)
        }

    async def cleanup(self) -> None:
        """Cleanup recovery manager"""
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        logger.info("Gateway recovery manager cleanup completed")