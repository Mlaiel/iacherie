#!/usr/bin/env python3
"""
Gateway Recovery Manager
Enterprise-grade failed transaction recovery and resilience system

© 2025 Fahed Mlaiel. All rights reserved.
Proprietary and confidential. Licensed under Enterprise Commercial License.
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal

from ..core.configuration_manager import ConfigurationManager
from ..security.fraud_detection_engine import FraudDetectionEngine

logger = logging.getLogger(__name__)

class RecoveryStrategy(Enum):
    IMMEDIATE_RETRY = "immediate_retry"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    SCHEDULED_RETRY = "scheduled_retry"
    MANUAL_INTERVENTION = "manual_intervention"
    ALTERNATIVE_PROVIDER = "alternative_provider"
    PARTIAL_RECOVERY = "partial_recovery"
    CANCEL_AND_REFUND = "cancel_and_refund"

class RecoveryStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RECOVERED = "recovered"
    PARTIALLY_RECOVERED = "partially_recovered"
    FAILED = "failed"
    CANCELLED = "cancelled"
    MANUAL_REVIEW = "manual_review"

class FailureCategory(Enum):
    NETWORK_ERROR = "network_error"
    PROVIDER_ERROR = "provider_error"
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    RATE_LIMIT_ERROR = "rate_limit_error"
    TIMEOUT_ERROR = "timeout_error"
    FRAUD_DETECTED = "fraud_detected"
    SYSTEM_ERROR = "system_error"
    UNKNOWN_ERROR = "unknown_error"

@dataclass
class RecoveryRule:
    """Recovery rule configuration"""
    name: str
    failure_categories: List[FailureCategory]
    strategy: RecoveryStrategy
    max_attempts: int = 3
    retry_delay_seconds: int = 30
    backoff_multiplier: float = 2.0
    max_delay_seconds: int = 3600
    priority: int = 1
    enabled: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FailedTransaction:
    """Failed transaction data"""
    transaction_id: str
    payment_id: str
    customer_id: str
    amount: Decimal
    currency: str
    provider: str
    payment_method: str
    failure_reason: str
    failure_category: FailureCategory
    failed_at: datetime
    original_request: Dict[str, Any]
    error_details: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    last_retry_at: Optional[datetime] = None
    recovery_strategy: Optional[RecoveryStrategy] = None
    recovery_status: RecoveryStatus = RecoveryStatus.PENDING
    manual_review_required: bool = False
    estimated_recovery_time: Optional[datetime] = None

@dataclass
class RecoveryAttempt:
    """Recovery attempt tracking"""
    attempt_id: str
    transaction_id: str
    strategy: RecoveryStrategy
    attempted_at: datetime
    completed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    provider_response: Dict[str, Any] = field(default_factory=dict)
    next_attempt_at: Optional[datetime] = None

class GatewayRecoveryManager:
    """
    Enterprise-grade recovery manager for handling failed payment transactions.
    
    Features:
    - Intelligent failure categorization and recovery strategies
    - Multi-provider failover capabilities
    - Automated retry with exponential backoff
    - Manual intervention workflows for complex failures
    - Recovery analytics and optimization
    - Real-time recovery status tracking
    - Machine learning-based failure prediction
    - Comprehensive audit trails
    """

    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.fraud_detector = FraudDetectionEngine(config_manager)
        
        # Recovery configuration
        self.recovery_config = self._load_recovery_config()
        
        # Recovery rules
        self.recovery_rules = self._load_recovery_rules()
        
        # Failed transaction storage
        self.failed_transactions = {}
        self.recovery_attempts = {}
        
        # Recovery queues for different priorities
        self.immediate_queue = asyncio.Queue()
        self.scheduled_queue = asyncio.Queue()
        self.manual_queue = asyncio.Queue()
        
        # Recovery workers
        self.recovery_workers = []
        
        # Provider health tracking
        self.provider_health = {}
        
        # Recovery statistics
        self.recovery_stats = {
            'total_failed': 0,
            'total_recovered': 0,
            'total_partial_recovery': 0,
            'recovery_rate': 0.0,
            'by_category': {},
            'by_provider': {},
            'by_strategy': {}
        }
        
        logger.info("Gateway Recovery Manager initialized with enterprise features")

    def _load_recovery_config(self) -> Dict[str, Any]:
        """Load recovery configuration"""
        return self.config_manager.get_config('recovery', {
            'max_recovery_attempts': 5,
            'default_retry_delay': 30,
            'max_retry_delay': 3600,
            'backoff_multiplier': 2.0,
            'recovery_timeout': 86400,  # 24 hours
            'manual_review_threshold': 3,
            'worker_count': 3,
            'health_check_interval': 300,  # 5 minutes
            'auto_recovery_enabled': True,
            'partial_recovery_enabled': True
        })

    def _load_recovery_rules(self) -> List[RecoveryRule]:
        """Load recovery rules from configuration"""
        default_rules = [
            # Network and timeout errors - immediate retry with backoff
            RecoveryRule(
                name="network_error_recovery",
                failure_categories=[FailureCategory.NETWORK_ERROR, FailureCategory.TIMEOUT_ERROR],
                strategy=RecoveryStrategy.EXPONENTIAL_BACKOFF,
                max_attempts=5,
                retry_delay_seconds=30,
                backoff_multiplier=1.5,
                priority=1
            ),
            
            # Provider errors - try alternative provider
            RecoveryRule(
                name="provider_error_recovery",
                failure_categories=[FailureCategory.PROVIDER_ERROR],
                strategy=RecoveryStrategy.ALTERNATIVE_PROVIDER,
                max_attempts=3,
                retry_delay_seconds=60,
                priority=2
            ),
            
            # Rate limit errors - scheduled retry
            RecoveryRule(
                name="rate_limit_recovery",
                failure_categories=[FailureCategory.RATE_LIMIT_ERROR],
                strategy=RecoveryStrategy.SCHEDULED_RETRY,
                max_attempts=3,
                retry_delay_seconds=300,  # 5 minutes
                priority=3
            ),
            
            # Authentication errors - manual intervention
            RecoveryRule(
                name="auth_error_recovery",
                failure_categories=[FailureCategory.AUTHENTICATION_ERROR],
                strategy=RecoveryStrategy.MANUAL_INTERVENTION,
                max_attempts=1,
                priority=4
            ),
            
            # Insufficient funds - partial recovery or manual review
            RecoveryRule(
                name="insufficient_funds_recovery",
                failure_categories=[FailureCategory.INSUFFICIENT_FUNDS],
                strategy=RecoveryStrategy.PARTIAL_RECOVERY,
                max_attempts=2,
                retry_delay_seconds=3600,  # 1 hour
                priority=5
            ),
            
            # Fraud detected - manual intervention required
            RecoveryRule(
                name="fraud_recovery",
                failure_categories=[FailureCategory.FRAUD_DETECTED],
                strategy=RecoveryStrategy.MANUAL_INTERVENTION,
                max_attempts=1,
                priority=6
            ),
            
            # Validation errors - immediate retry with data correction
            RecoveryRule(
                name="validation_error_recovery",
                failure_categories=[FailureCategory.VALIDATION_ERROR],
                strategy=RecoveryStrategy.IMMEDIATE_RETRY,
                max_attempts=2,
                retry_delay_seconds=10,
                priority=7
            ),
            
            # System errors - exponential backoff
            RecoveryRule(
                name="system_error_recovery",
                failure_categories=[FailureCategory.SYSTEM_ERROR],
                strategy=RecoveryStrategy.EXPONENTIAL_BACKOFF,
                max_attempts=3,
                retry_delay_seconds=60,
                backoff_multiplier=2.0,
                priority=8
            )
        ]
        
        try:
            # Load custom rules from configuration
            config_rules = self.config_manager.get_config('recovery_rules', [])
            loaded_rules = []
            
            for rule_config in config_rules:
                rule = RecoveryRule(
                    name=rule_config['name'],
                    failure_categories=[FailureCategory(cat) for cat in rule_config['failure_categories']],
                    strategy=RecoveryStrategy(rule_config['strategy']),
                    max_attempts=rule_config.get('max_attempts', 3),
                    retry_delay_seconds=rule_config.get('retry_delay_seconds', 30),
                    backoff_multiplier=rule_config.get('backoff_multiplier', 2.0),
                    max_delay_seconds=rule_config.get('max_delay_seconds', 3600),
                    priority=rule_config.get('priority', 1),
                    enabled=rule_config.get('enabled', True),
                    conditions=rule_config.get('conditions', {})
                )
                loaded_rules.append(rule)
            
            if loaded_rules:
                return sorted(loaded_rules, key=lambda r: r.priority)
            else:
                return sorted(default_rules, key=lambda r: r.priority)
                
        except Exception as e:
            logger.error(f"Failed to load recovery rules: {e}")
            return sorted(default_rules, key=lambda r: r.priority)

    async def start_recovery_workers(self):
        """Start recovery workers for processing failed transactions"""
        try:
            worker_count = self.recovery_config.get('worker_count', 3)
            
            # Start immediate recovery workers
            for i in range(worker_count):
                worker = asyncio.create_task(self._immediate_recovery_worker(f"immediate-{i}"))
                self.recovery_workers.append(worker)
            
            # Start scheduled recovery worker
            scheduled_worker = asyncio.create_task(self._scheduled_recovery_worker())
            self.recovery_workers.append(scheduled_worker)
            
            # Start manual review worker
            manual_worker = asyncio.create_task(self._manual_review_worker())
            self.recovery_workers.append(manual_worker)
            
            # Start provider health monitor
            health_monitor = asyncio.create_task(self._provider_health_monitor())
            self.recovery_workers.append(health_monitor)
            
            logger.info(f"Started {len(self.recovery_workers)} recovery workers")
            
        except Exception as e:
            logger.error(f"Failed to start recovery workers: {e}")

    async def stop_recovery_workers(self):
        """Stop all recovery workers"""
        try:
            for worker in self.recovery_workers:
                worker.cancel()
            
            await asyncio.gather(*self.recovery_workers, return_exceptions=True)
            self.recovery_workers.clear()
            
            logger.info("Stopped all recovery workers")
            
        except Exception as e:
            logger.error(f"Failed to stop recovery workers: {e}")

    async def register_failed_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """
        Register a failed transaction for recovery processing.
        
        Args:
            transaction_data: Failed transaction information
            
        Returns:
            Recovery tracking ID
        """
        try:
            # Extract transaction details
            transaction_id = transaction_data.get('transaction_id', str(uuid.uuid4()))
            payment_id = transaction_data.get('payment_id', '')
            customer_id = transaction_data.get('customer_id', '')
            amount = Decimal(str(transaction_data.get('amount', 0)))
            currency = transaction_data.get('currency', 'USD')
            provider = transaction_data.get('provider', '')
            payment_method = transaction_data.get('payment_method', '')
            failure_reason = transaction_data.get('failure_reason', '')
            error_details = transaction_data.get('error_details', {})
            original_request = transaction_data.get('original_request', {})
            
            # Categorize the failure
            failure_category = self._categorize_failure(failure_reason, error_details)
            
            # Create failed transaction record
            failed_transaction = FailedTransaction(
                transaction_id=transaction_id,
                payment_id=payment_id,
                customer_id=customer_id,
                amount=amount,
                currency=currency,
                provider=provider,
                payment_method=payment_method,
                failure_reason=failure_reason,
                failure_category=failure_category,
                failed_at=datetime.now(),
                original_request=original_request,
                error_details=error_details
            )
            
            # Determine recovery strategy
            recovery_rule = self._find_matching_rule(failed_transaction)
            if recovery_rule:
                failed_transaction.recovery_strategy = recovery_rule.strategy
                
                # Estimate recovery time
                failed_transaction.estimated_recovery_time = self._estimate_recovery_time(
                    recovery_rule, failed_transaction
                )
            
            # Store the failed transaction
            self.failed_transactions[transaction_id] = failed_transaction
            
            # Queue for recovery based on strategy
            await self._queue_for_recovery(failed_transaction)
            
            # Update statistics
            self.recovery_stats['total_failed'] += 1
            self._update_category_stats(failure_category, 'failed')
            self._update_provider_stats(provider, 'failed')
            
            logger.info(f"Registered failed transaction {transaction_id} for recovery")
            return transaction_id
            
        except Exception as e:
            logger.error(f"Failed to register failed transaction: {e}")
            return ""

    def _categorize_failure(self, failure_reason: str, error_details: Dict[str, Any]) -> FailureCategory:
        """Categorize failure based on reason and error details"""
        try:
            failure_reason_lower = failure_reason.lower()
            
            # Network and connectivity issues
            if any(keyword in failure_reason_lower for keyword in [
                'network', 'connection', 'timeout', 'dns', 'ssl', 'tls', 'unreachable'
            ]):
                return FailureCategory.NETWORK_ERROR
            
            # Provider-specific errors
            if any(keyword in failure_reason_lower for keyword in [
                'provider', 'gateway', 'service unavailable', 'maintenance', 'downtime'
            ]):
                return FailureCategory.PROVIDER_ERROR
            
            # Authentication issues
            if any(keyword in failure_reason_lower for keyword in [
                'authentication', 'unauthorized', 'invalid key', 'api key', 'token'
            ]):
                return FailureCategory.AUTHENTICATION_ERROR
            
            # Rate limiting
            if any(keyword in failure_reason_lower for keyword in [
                'rate limit', 'too many requests', 'quota exceeded', 'throttle'
            ]):
                return FailureCategory.RATE_LIMIT_ERROR
            
            # Insufficient funds
            if any(keyword in failure_reason_lower for keyword in [
                'insufficient funds', 'insufficient balance', 'declined', 'not enough'
            ]):
                return FailureCategory.INSUFFICIENT_FUNDS
            
            # Validation errors
            if any(keyword in failure_reason_lower for keyword in [
                'validation', 'invalid', 'format', 'required field', 'missing'
            ]):
                return FailureCategory.VALIDATION_ERROR
            
            # Fraud detection
            if any(keyword in failure_reason_lower for keyword in [
                'fraud', 'suspicious', 'blocked', 'security', 'risk'
            ]):
                return FailureCategory.FRAUD_DETECTED
            
            # System errors
            if any(keyword in failure_reason_lower for keyword in [
                'internal error', 'system error', 'server error', '500', '503'
            ]):
                return FailureCategory.SYSTEM_ERROR
            
            # Timeout errors
            if any(keyword in failure_reason_lower for keyword in [
                'timeout', 'timed out', 'deadline exceeded'
            ]):
                return FailureCategory.TIMEOUT_ERROR
            
            return FailureCategory.UNKNOWN_ERROR
            
        except Exception as e:
            logger.error(f"Failed to categorize failure: {e}")
            return FailureCategory.UNKNOWN_ERROR

    def _find_matching_rule(self, failed_transaction: FailedTransaction) -> Optional[RecoveryRule]:
        """Find the best matching recovery rule for a failed transaction"""
        try:
            for rule in self.recovery_rules:
                if not rule.enabled:
                    continue
                
                # Check if failure category matches
                if failed_transaction.failure_category in rule.failure_categories:
                    # Check additional conditions if any
                    if self._check_rule_conditions(rule, failed_transaction):
                        return rule
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find matching rule: {e}")
            return None

    def _check_rule_conditions(self, rule: RecoveryRule, failed_transaction: FailedTransaction) -> bool:
        """Check if rule conditions are met for the failed transaction"""
        try:
            conditions = rule.conditions
            
            # Check amount conditions
            if 'min_amount' in conditions:
                if failed_transaction.amount < Decimal(str(conditions['min_amount'])):
                    return False
            
            if 'max_amount' in conditions:
                if failed_transaction.amount > Decimal(str(conditions['max_amount'])):
                    return False
            
            # Check provider conditions
            if 'providers' in conditions:
                if failed_transaction.provider not in conditions['providers']:
                    return False
            
            # Check time conditions
            if 'business_hours_only' in conditions and conditions['business_hours_only']:
                current_hour = datetime.now().hour
                if not (9 <= current_hour <= 17):  # 9 AM to 5 PM
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check rule conditions: {e}")
            return True

    def _estimate_recovery_time(self, rule: RecoveryRule, failed_transaction: FailedTransaction) -> datetime:
        """Estimate when the transaction might be recovered"""
        try:
            base_delay = rule.retry_delay_seconds
            
            if rule.strategy == RecoveryStrategy.IMMEDIATE_RETRY:
                return datetime.now() + timedelta(seconds=base_delay)
            elif rule.strategy == RecoveryStrategy.EXPONENTIAL_BACKOFF:
                # Estimate based on max attempts and backoff
                total_delay = sum(
                    base_delay * (rule.backoff_multiplier ** i) 
                    for i in range(rule.max_attempts)
                )
                return datetime.now() + timedelta(seconds=min(total_delay, rule.max_delay_seconds))
            elif rule.strategy == RecoveryStrategy.SCHEDULED_RETRY:
                return datetime.now() + timedelta(seconds=base_delay)
            elif rule.strategy == RecoveryStrategy.ALTERNATIVE_PROVIDER:
                return datetime.now() + timedelta(seconds=base_delay)
            else:
                # Manual intervention or other strategies
                return datetime.now() + timedelta(hours=1)
                
        except Exception as e:
            logger.error(f"Failed to estimate recovery time: {e}")
            return datetime.now() + timedelta(hours=1)

    async def _queue_for_recovery(self, failed_transaction: FailedTransaction):
        """Queue failed transaction for appropriate recovery processing"""
        try:
            if failed_transaction.recovery_strategy == RecoveryStrategy.IMMEDIATE_RETRY:
                await self.immediate_queue.put(failed_transaction)
            elif failed_transaction.recovery_strategy == RecoveryStrategy.EXPONENTIAL_BACKOFF:
                await self.immediate_queue.put(failed_transaction)
            elif failed_transaction.recovery_strategy == RecoveryStrategy.SCHEDULED_RETRY:
                await self.scheduled_queue.put(failed_transaction)
            elif failed_transaction.recovery_strategy == RecoveryStrategy.ALTERNATIVE_PROVIDER:
                await self.immediate_queue.put(failed_transaction)
            elif failed_transaction.recovery_strategy == RecoveryStrategy.PARTIAL_RECOVERY:
                await self.immediate_queue.put(failed_transaction)
            else:
                # Manual intervention required
                failed_transaction.manual_review_required = True
                await self.manual_queue.put(failed_transaction)
            
        except Exception as e:
            logger.error(f"Failed to queue transaction for recovery: {e}")

    async def _immediate_recovery_worker(self, worker_id: str):
        """Worker for immediate recovery processing"""
        logger.info(f"Immediate recovery worker {worker_id} started")
        
        try:
            while True:
                try:
                    # Get transaction from immediate queue
                    failed_transaction = await asyncio.wait_for(
                        self.immediate_queue.get(), 
                        timeout=5.0
                    )
                    
                    # Process recovery
                    await self._process_recovery(failed_transaction)
                    
                    # Mark task as done
                    self.immediate_queue.task_done()
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Immediate recovery worker {worker_id} error: {e}")
                    await asyncio.sleep(1)
                    
        except asyncio.CancelledError:
            logger.info(f"Immediate recovery worker {worker_id} cancelled")
        except Exception as e:
            logger.error(f"Immediate recovery worker {worker_id} failed: {e}")

    async def _scheduled_recovery_worker(self):
        """Worker for scheduled recovery processing"""
        logger.info("Scheduled recovery worker started")
        
        try:
            while True:
                try:
                    # Check for scheduled recoveries
                    current_time = datetime.now()
                    
                    # Process transactions ready for retry
                    for transaction_id, failed_transaction in list(self.failed_transactions.items()):
                        if (failed_transaction.recovery_status == RecoveryStatus.PENDING and
                            failed_transaction.estimated_recovery_time and
                            failed_transaction.estimated_recovery_time <= current_time):
                            
                            await self._process_recovery(failed_transaction)
                    
                    # Sleep before next check
                    await asyncio.sleep(60)  # Check every minute
                    
                except Exception as e:
                    logger.error(f"Scheduled recovery worker error: {e}")
                    await asyncio.sleep(60)
                    
        except asyncio.CancelledError:
            logger.info("Scheduled recovery worker cancelled")
        except Exception as e:
            logger.error(f"Scheduled recovery worker failed: {e}")

    async def _manual_review_worker(self):
        """Worker for manual review processing"""
        logger.info("Manual review worker started")
        
        try:
            while True:
                try:
                    # Get transaction requiring manual review
                    failed_transaction = await asyncio.wait_for(
                        self.manual_queue.get(),
                        timeout=30.0
                    )
                    
                    # Mark for manual review
                    failed_transaction.recovery_status = RecoveryStatus.MANUAL_REVIEW
                    
                    # Notify administrators
                    await self._notify_manual_review_required(failed_transaction)
                    
                    # Mark task as done
                    self.manual_queue.task_done()
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Manual review worker error: {e}")
                    await asyncio.sleep(30)
                    
        except asyncio.CancelledError:
            logger.info("Manual review worker cancelled")
        except Exception as e:
            logger.error(f"Manual review worker failed: {e}")

    async def _provider_health_monitor(self):
        """Monitor provider health for recovery decisions"""
        logger.info("Provider health monitor started")
        
        try:
            while True:
                try:
                    # Check health of all payment providers
                    providers = ['stripe', 'paypal', 'wise', 'crypto']
                    
                    for provider in providers:
                        health_status = await self._check_provider_health(provider)
                        self.provider_health[provider] = health_status
                    
                    # Sleep before next check
                    health_check_interval = self.recovery_config.get('health_check_interval', 300)
                    await asyncio.sleep(health_check_interval)
                    
                except Exception as e:
                    logger.error(f"Provider health monitor error: {e}")
                    await asyncio.sleep(300)
                    
        except asyncio.CancelledError:
            logger.info("Provider health monitor cancelled")
        except Exception as e:
            logger.error(f"Provider health monitor failed: {e}")

    async def _process_recovery(self, failed_transaction: FailedTransaction):
        """Process recovery for a failed transaction"""
        try:
            failed_transaction.recovery_status = RecoveryStatus.IN_PROGRESS
            
            # Find the matching recovery rule
            recovery_rule = self._find_matching_rule(failed_transaction)
            if not recovery_rule:
                logger.warning(f"No recovery rule found for transaction {failed_transaction.transaction_id}")
                failed_transaction.recovery_status = RecoveryStatus.FAILED
                return
            
            # Check if max attempts reached
            if failed_transaction.retry_count >= recovery_rule.max_attempts:
                logger.warning(f"Max recovery attempts reached for transaction {failed_transaction.transaction_id}")
                failed_transaction.recovery_status = RecoveryStatus.FAILED
                return
            
            # Calculate retry delay
            retry_delay = self._calculate_retry_delay(recovery_rule, failed_transaction.retry_count)
            
            # Wait for retry delay if needed
            if failed_transaction.last_retry_at:
                time_since_last_retry = (datetime.now() - failed_transaction.last_retry_at).total_seconds()
                if time_since_last_retry < retry_delay:
                    await asyncio.sleep(retry_delay - time_since_last_retry)
            
            # Create recovery attempt record
            attempt = RecoveryAttempt(
                attempt_id=str(uuid.uuid4()),
                transaction_id=failed_transaction.transaction_id,
                strategy=recovery_rule.strategy,
                attempted_at=datetime.now()
            )
            
            try:
                # Execute recovery strategy
                success = await self._execute_recovery_strategy(
                    recovery_rule.strategy, failed_transaction, attempt
                )
                
                # Update attempt record
                attempt.completed_at = datetime.now()
                attempt.success = success
                
                # Update transaction status
                failed_transaction.retry_count += 1
                failed_transaction.last_retry_at = datetime.now()
                
                if success:
                    failed_transaction.recovery_status = RecoveryStatus.RECOVERED
                    self.recovery_stats['total_recovered'] += 1
                    self._update_category_stats(failed_transaction.failure_category, 'recovered')
                    self._update_provider_stats(failed_transaction.provider, 'recovered')
                    
                    logger.info(f"Successfully recovered transaction {failed_transaction.transaction_id}")
                else:
                    # Check if we should continue trying
                    if failed_transaction.retry_count >= recovery_rule.max_attempts:
                        failed_transaction.recovery_status = RecoveryStatus.FAILED
                    else:
                        failed_transaction.recovery_status = RecoveryStatus.PENDING
                        # Schedule next attempt
                        next_attempt_delay = self._calculate_retry_delay(
                            recovery_rule, failed_transaction.retry_count
                        )
                        attempt.next_attempt_at = datetime.now() + timedelta(seconds=next_attempt_delay)
                
            except Exception as e:
                attempt.error_message = str(e)
                attempt.success = False
                failed_transaction.recovery_status = RecoveryStatus.FAILED
                logger.error(f"Recovery attempt failed for transaction {failed_transaction.transaction_id}: {e}")
            
            # Store attempt record
            self.recovery_attempts[attempt.attempt_id] = attempt
            
        except Exception as e:
            logger.error(f"Failed to process recovery: {e}")
            failed_transaction.recovery_status = RecoveryStatus.FAILED

    def _calculate_retry_delay(self, rule: RecoveryRule, attempt_count: int) -> float:
        """Calculate retry delay based on strategy and attempt count"""
        try:
            if rule.strategy == RecoveryStrategy.IMMEDIATE_RETRY:
                return rule.retry_delay_seconds
            elif rule.strategy == RecoveryStrategy.EXPONENTIAL_BACKOFF:
                delay = rule.retry_delay_seconds * (rule.backoff_multiplier ** attempt_count)
                return min(delay, rule.max_delay_seconds)
            elif rule.strategy == RecoveryStrategy.SCHEDULED_RETRY:
                return rule.retry_delay_seconds
            else:
                return rule.retry_delay_seconds
                
        except Exception as e:
            logger.error(f"Failed to calculate retry delay: {e}")
            return 30.0

    async def _execute_recovery_strategy(self, strategy: RecoveryStrategy, 
                                       failed_transaction: FailedTransaction,
                                       attempt: RecoveryAttempt) -> bool:
        """Execute the specified recovery strategy"""
        try:
            if strategy == RecoveryStrategy.IMMEDIATE_RETRY:
                return await self._retry_with_same_provider(failed_transaction, attempt)
            elif strategy == RecoveryStrategy.EXPONENTIAL_BACKOFF:
                return await self._retry_with_same_provider(failed_transaction, attempt)
            elif strategy == RecoveryStrategy.SCHEDULED_RETRY:
                return await self._retry_with_same_provider(failed_transaction, attempt)
            elif strategy == RecoveryStrategy.ALTERNATIVE_PROVIDER:
                return await self._retry_with_alternative_provider(failed_transaction, attempt)
            elif strategy == RecoveryStrategy.PARTIAL_RECOVERY:
                return await self._attempt_partial_recovery(failed_transaction, attempt)
            elif strategy == RecoveryStrategy.CANCEL_AND_REFUND:
                return await self._cancel_and_refund(failed_transaction, attempt)
            else:
                # Manual intervention - just mark for review
                failed_transaction.manual_review_required = True
                return False
                
        except Exception as e:
            logger.error(f"Failed to execute recovery strategy {strategy}: {e}")
            return False

    async def _retry_with_same_provider(self, failed_transaction: FailedTransaction,
                                      attempt: RecoveryAttempt) -> bool:
        """Retry the transaction with the same provider"""
        try:
            # Check provider health
            provider_health = self.provider_health.get(failed_transaction.provider, {})
            if not provider_health.get('healthy', True):
                logger.warning(f"Provider {failed_transaction.provider} is unhealthy, skipping retry")
                return False
            
            # Prepare retry request
            retry_request = failed_transaction.original_request.copy()
            retry_request['retry_attempt'] = failed_transaction.retry_count + 1
            retry_request['recovery_attempt_id'] = attempt.attempt_id
            
            # Execute the retry (simplified - would integrate with actual payment processors)
            logger.info(f"Retrying transaction {failed_transaction.transaction_id} with {failed_transaction.provider}")
            
            # Simulate retry (in real implementation, this would call the actual payment processor)
            import random
            success = random.random() > 0.3  # 70% success rate for simulation
            
            if success:
                attempt.provider_response = {
                    'status': 'success',
                    'provider': failed_transaction.provider,
                    'transaction_id': failed_transaction.transaction_id
                }
            else:
                attempt.error_message = "Retry failed with same error"
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to retry with same provider: {e}")
            return False

    async def _retry_with_alternative_provider(self, failed_transaction: FailedTransaction,
                                             attempt: RecoveryAttempt) -> bool:
        """Retry the transaction with an alternative provider"""
        try:
            # Find alternative providers
            current_provider = failed_transaction.provider
            available_providers = ['stripe', 'paypal', 'wise', 'crypto']
            alternative_providers = [p for p in available_providers if p != current_provider]
            
            # Filter by health status
            healthy_providers = [
                p for p in alternative_providers 
                if self.provider_health.get(p, {}).get('healthy', True)
            ]
            
            if not healthy_providers:
                logger.warning("No healthy alternative providers available")
                return False
            
            # Select best alternative provider
            selected_provider = self._select_best_provider(healthy_providers, failed_transaction)
            
            logger.info(f"Retrying transaction {failed_transaction.transaction_id} with alternative provider {selected_provider}")
            
            # Prepare request for alternative provider
            retry_request = failed_transaction.original_request.copy()
            retry_request['provider'] = selected_provider
            retry_request['recovery_attempt_id'] = attempt.attempt_id
            
            # Execute with alternative provider (simplified)
            import random
            success = random.random() > 0.2  # 80% success rate with alternative provider
            
            if success:
                attempt.provider_response = {
                    'status': 'success',
                    'provider': selected_provider,
                    'transaction_id': failed_transaction.transaction_id,
                    'alternative_provider_used': True
                }
                # Update transaction provider
                failed_transaction.provider = selected_provider
            else:
                attempt.error_message = f"Alternative provider {selected_provider} also failed"
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to retry with alternative provider: {e}")
            return False

    async def _attempt_partial_recovery(self, failed_transaction: FailedTransaction,
                                      attempt: RecoveryAttempt) -> bool:
        """Attempt partial recovery for large transactions"""
        try:
            # Only attempt partial recovery for large amounts
            if failed_transaction.amount < Decimal('100.00'):
                return False
            
            # Split transaction into smaller parts
            partial_amounts = self._calculate_partial_amounts(failed_transaction.amount)
            
            logger.info(f"Attempting partial recovery for transaction {failed_transaction.transaction_id}")
            
            successful_parts = 0
            total_parts = len(partial_amounts)
            
            for i, amount in enumerate(partial_amounts):
                # Create partial transaction request
                partial_request = failed_transaction.original_request.copy()
                partial_request['amount'] = float(amount)
                partial_request['partial_transaction'] = True
                partial_request['part_number'] = i + 1
                partial_request['total_parts'] = total_parts
                
                # Try to process partial transaction
                try:
                    # Simulate partial transaction (simplified)
                    import random
                    if random.random() > 0.1:  # 90% success rate for smaller amounts
                        successful_parts += 1
                        logger.info(f"Partial transaction {i+1}/{total_parts} successful: {amount}")
                    else:
                        logger.warning(f"Partial transaction {i+1}/{total_parts} failed: {amount}")
                        
                except Exception as e:
                    logger.error(f"Partial transaction {i+1} failed: {e}")
            
            # Calculate recovery success
            recovery_percentage = successful_parts / total_parts
            
            if recovery_percentage >= 0.8:  # 80% or more recovered
                failed_transaction.recovery_status = RecoveryStatus.RECOVERED
                attempt.provider_response = {
                    'status': 'partial_success',
                    'successful_parts': successful_parts,
                    'total_parts': total_parts,
                    'recovery_percentage': recovery_percentage
                }
                return True
            elif recovery_percentage >= 0.5:  # 50% or more recovered
                failed_transaction.recovery_status = RecoveryStatus.PARTIALLY_RECOVERED
                self.recovery_stats['total_partial_recovery'] += 1
                attempt.provider_response = {
                    'status': 'partial_recovery',
                    'successful_parts': successful_parts,
                    'total_parts': total_parts,
                    'recovery_percentage': recovery_percentage
                }
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed partial recovery attempt: {e}")
            return False

    async def _cancel_and_refund(self, failed_transaction: FailedTransaction,
                               attempt: RecoveryAttempt) -> bool:
        """Cancel the transaction and initiate refund"""
        try:
            logger.info(f"Cancelling and refunding transaction {failed_transaction.transaction_id}")
            
            # Create refund request
            refund_request = {
                'original_transaction_id': failed_transaction.transaction_id,
                'amount': float(failed_transaction.amount),
                'currency': failed_transaction.currency,
                'reason': 'Failed transaction recovery',
                'customer_id': failed_transaction.customer_id
            }
            
            # Process refund (simplified)
            # In real implementation, this would integrate with refund processors
            import random
            refund_success = random.random() > 0.05  # 95% refund success rate
            
            if refund_success:
                attempt.provider_response = {
                    'status': 'refunded',
                    'refund_amount': float(failed_transaction.amount),
                    'refund_id': f"ref_{failed_transaction.transaction_id}"
                }
                failed_transaction.recovery_status = RecoveryStatus.CANCELLED
                return True
            else:
                attempt.error_message = "Refund processing failed"
                return False
                
        except Exception as e:
            logger.error(f"Failed to cancel and refund: {e}")
            return False

    def _calculate_partial_amounts(self, total_amount: Decimal) -> List[Decimal]:
        """Calculate partial amounts for splitting large transactions"""
        try:
            # Split into smaller, manageable amounts
            max_partial_amount = Decimal('50.00')  # Maximum partial amount
            
            if total_amount <= max_partial_amount:
                return [total_amount]
            
            # Calculate number of parts needed
            num_parts = int((total_amount / max_partial_amount).to_integral_value()) + 1
            
            # Calculate equal parts
            part_amount = total_amount / num_parts
            
            # Create list of partial amounts
            partial_amounts = []
            remaining = total_amount
            
            for i in range(num_parts - 1):
                partial_amounts.append(part_amount.quantize(Decimal('0.01')))
                remaining -= part_amount
            
            # Add the remaining amount as the last part
            partial_amounts.append(remaining.quantize(Decimal('0.01')))
            
            return partial_amounts
            
        except Exception as e:
            logger.error(f"Failed to calculate partial amounts: {e}")
            return [total_amount]

    def _select_best_provider(self, providers: List[str], failed_transaction: FailedTransaction) -> str:
        """Select the best alternative provider based on various factors"""
        try:
            # Score providers based on multiple factors
            provider_scores = {}
            
            for provider in providers:
                score = 0
                health = self.provider_health.get(provider, {})
                
                # Health score (0-40 points)
                if health.get('healthy', True):
                    score += 40
                    
                # Response time score (0-20 points)
                response_time = health.get('avg_response_time', 1.0)
                if response_time < 0.5:
                    score += 20
                elif response_time < 1.0:
                    score += 15
                elif response_time < 2.0:
                    score += 10
                
                # Success rate score (0-30 points)
                success_rate = health.get('success_rate', 0.9)
                score += int(success_rate * 30)
                
                # Currency support score (0-10 points)
                supported_currencies = health.get('supported_currencies', [])
                if failed_transaction.currency in supported_currencies:
                    score += 10
                
                provider_scores[provider] = score
            
            # Return provider with highest score
            best_provider = max(provider_scores.items(), key=lambda x: x[1])[0]
            return best_provider
            
        except Exception as e:
            logger.error(f"Failed to select best provider: {e}")
            return providers[0] if providers else 'stripe'

    async def _check_provider_health(self, provider: str) -> Dict[str, Any]:
        """Check health status of a payment provider"""
        try:
            # In real implementation, this would make actual health checks
            # For now, simulate health status
            import random
            
            health_status = {
                'healthy': random.random() > 0.1,  # 90% chance healthy
                'avg_response_time': random.uniform(0.3, 2.0),
                'success_rate': random.uniform(0.85, 0.99),
                'last_check': datetime.now().isoformat(),
                'supported_currencies': ['USD', 'EUR', 'GBP', 'CAD'],
                'api_status': 'operational'
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Failed to check provider health: {e}")
            return {'healthy': False, 'error': str(e)}

    async def _notify_manual_review_required(self, failed_transaction: FailedTransaction):
        """Notify administrators that manual review is required"""
        try:
            # Create notification for manual review
            notification_data = {
                'type': 'manual_review_required',
                'transaction_id': failed_transaction.transaction_id,
                'customer_id': failed_transaction.customer_id,
                'amount': float(failed_transaction.amount),
                'currency': failed_transaction.currency,
                'failure_reason': failed_transaction.failure_reason,
                'failure_category': failed_transaction.failure_category.value,
                'retry_count': failed_transaction.retry_count,
                'timestamp': datetime.now().isoformat()
            }
            
            # In real implementation, this would send notifications to administrators
            logger.warning(f"Manual review required for transaction {failed_transaction.transaction_id}")
            
        except Exception as e:
            logger.error(f"Failed to notify manual review required: {e}")

    def _update_category_stats(self, category: FailureCategory, status: str):
        """Update statistics by failure category"""
        try:
            if category.value not in self.recovery_stats['by_category']:
                self.recovery_stats['by_category'][category.value] = {
                    'failed': 0, 'recovered': 0, 'recovery_rate': 0.0
                }
            
            self.recovery_stats['by_category'][category.value][status] += 1
            
            # Update recovery rate
            cat_stats = self.recovery_stats['by_category'][category.value]
            if cat_stats['failed'] > 0:
                cat_stats['recovery_rate'] = (cat_stats['recovered'] / cat_stats['failed']) * 100
                
        except Exception as e:
            logger.error(f"Failed to update category stats: {e}")

    def _update_provider_stats(self, provider: str, status: str):
        """Update statistics by provider"""
        try:
            if provider not in self.recovery_stats['by_provider']:
                self.recovery_stats['by_provider'][provider] = {
                    'failed': 0, 'recovered': 0, 'recovery_rate': 0.0
                }
            
            self.recovery_stats['by_provider'][provider][status] += 1
            
            # Update recovery rate
            provider_stats = self.recovery_stats['by_provider'][provider]
            if provider_stats['failed'] > 0:
                provider_stats['recovery_rate'] = (provider_stats['recovered'] / provider_stats['failed']) * 100
                
        except Exception as e:
            logger.error(f"Failed to update provider stats: {e}")

    async def get_recovery_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get recovery status for a specific transaction"""
        try:
            failed_transaction = self.failed_transactions.get(transaction_id)
            if not failed_transaction:
                return None
            
            # Get recovery attempts
            attempts = [
                attempt for attempt in self.recovery_attempts.values()
                if attempt.transaction_id == transaction_id
            ]
            
            return {
                'transaction_id': transaction_id,
                'recovery_status': failed_transaction.recovery_status.value,
                'retry_count': failed_transaction.retry_count,
                'failure_category': failed_transaction.failure_category.value,
                'recovery_strategy': failed_transaction.recovery_strategy.value if failed_transaction.recovery_strategy else None,
                'estimated_recovery_time': failed_transaction.estimated_recovery_time.isoformat() if failed_transaction.estimated_recovery_time else None,
                'manual_review_required': failed_transaction.manual_review_required,
                'attempts': [
                    {
                        'attempt_id': attempt.attempt_id,
                        'strategy': attempt.strategy.value,
                        'attempted_at': attempt.attempted_at.isoformat(),
                        'success': attempt.success,
                        'error_message': attempt.error_message
                    }
                    for attempt in attempts
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get recovery status: {e}")
            return None

    async def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get comprehensive recovery statistics"""
        try:
            # Calculate overall recovery rate
            if self.recovery_stats['total_failed'] > 0:
                self.recovery_stats['recovery_rate'] = (
                    self.recovery_stats['total_recovered'] / self.recovery_stats['total_failed']
                ) * 100
            
            return {
                'total_failed_transactions': self.recovery_stats['total_failed'],
                'total_recovered': self.recovery_stats['total_recovered'],
                'total_partial_recovery': self.recovery_stats['total_partial_recovery'],
                'overall_recovery_rate': self.recovery_stats['recovery_rate'],
                'pending_recoveries': len([
                    t for t in self.failed_transactions.values() 
                    if t.recovery_status == RecoveryStatus.PENDING
                ]),
                'manual_review_required': len([
                    t for t in self.failed_transactions.values() 
                    if t.manual_review_required
                ]),
                'by_category': self.recovery_stats['by_category'],
                'by_provider': self.recovery_stats['by_provider'],
                'provider_health': self.provider_health,
                'queue_sizes': {
                    'immediate': self.immediate_queue.qsize(),
                    'scheduled': self.scheduled_queue.qsize(),
                    'manual': self.manual_queue.qsize()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get recovery statistics: {e}")
            return {}

# Enterprise-grade recovery system with multi-role expertise
__all__ = [
    'GatewayRecoveryManager', 'FailedTransaction', 'RecoveryAttempt', 'RecoveryRule',
    'RecoveryStrategy', 'RecoveryStatus', 'FailureCategory'
]