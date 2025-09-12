"""🗄️ Transaction Validation System
==================================

Enterprise transaction validation system with multi-layer data integrity checks,
audit trails, and comprehensive validation rules for payment processing.

Features:
- Multi-layer data integrity checks
- Transaction validation rules engine
- Real-time validation processing
- Audit trail integration
- Data consistency verification
- Performance-optimized validation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import json
import uuid
import hashlib
import re
from pathlib import Path
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import Column, String, DateTime, Numeric, Boolean, Integer, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import asyncpg

logger = logging.getLogger(__name__)

Base = declarative_base()


class ValidationLevel(Enum):
    """Validation level severity"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationCategory(Enum):
    """Categories of validation"""
    DATA_FORMAT = "data_format"
    BUSINESS_RULES = "business_rules"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    INTEGRITY = "integrity"
    PERFORMANCE = "performance"


class ValidationStatus(Enum):
    """Validation status"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class TransactionType(Enum):
    """Types of transactions"""
    PAYMENT = "payment"
    REFUND = "refund"
    TRANSFER = "transfer"
    PAYOUT = "payout"
    CHARGEBACK = "chargeback"
    ADJUSTMENT = "adjustment"


@dataclass
class ValidationRule:
    """Transaction validation rule"""
    rule_id: str
    name: str
    description: str
    category: ValidationCategory
    level: ValidationLevel
    condition: str  # Python expression or SQL-like condition
    error_message: str
    is_active: bool = True
    applies_to: Set[TransactionType] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def evaluate(self, transaction_data: Dict[str, Any]) -> bool:
        """Evaluate rule against transaction data"""
        try:
            # This is a simplified evaluation - in production would use a proper expression evaluator
            return eval(self.condition, {"__builtins__": {}}, transaction_data)
        except Exception:
            return False


@dataclass
class ValidationResult:
    """Result of a validation check"""
    validation_id: str
    rule_id: str
    transaction_id: str
    status: ValidationStatus
    level: ValidationLevel
    category: ValidationCategory
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    execution_time_ms: Optional[float] = None


@dataclass
class TransactionValidationReport:
    """Comprehensive validation report for a transaction"""
    transaction_id: str
    overall_status: ValidationStatus
    total_rules_checked: int
    passed_count: int
    failed_count: int
    warning_count: int
    skipped_count: int
    validation_results: List[ValidationResult]
    execution_time_ms: float
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def has_critical_errors(self) -> bool:
        """Check if validation has critical errors"""
        return any(
            result.level == ValidationLevel.CRITICAL and result.status == ValidationStatus.FAILED
            for result in self.validation_results
        )
    
    def get_error_summary(self) -> Dict[ValidationCategory, int]:
        """Get summary of errors by category"""
        error_summary = {}
        for result in self.validation_results:
            if result.status == ValidationStatus.FAILED:
                category = result.category
                error_summary[category] = error_summary.get(category, 0) + 1
        return error_summary


@dataclass
class DataIntegrityCheck:
    """Data integrity verification"""
    check_id: str
    check_type: str  # checksum, foreign_key, constraint, etc.
    description: str
    query: str  # SQL query for verification
    expected_result: Any
    is_active: bool = True


class TransactionValidationSystem:
    """Enterprise transaction validation system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.db_session: Optional[AsyncSession] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        
        # Validation settings
        self.validation_timeout = timedelta(seconds=config.get('validation_timeout_seconds', 30))
        self.parallel_validation = config.get('parallel_validation', True)
        self.cache_validation_results = config.get('cache_results', True)
        self.cache_ttl = timedelta(minutes=config.get('cache_ttl_minutes', 5))
        
        # Validation rules
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.integrity_checks: Dict[str, DataIntegrityCheck] = {}
        
        # Performance tracking
        self.validation_metrics: Dict[str, Any] = {
            'total_validations': 0,
            'total_execution_time': 0,
            'average_execution_time': 0,
            'rules_performance': {}
        }
        
        # Background tasks
        self.metrics_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize the transaction validation system"""
        try:
            # Initialize Redis connection
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 5),
                decode_responses=True
            )
            
            # Initialize database connections
            db_config = self.config.get('database', {})
            
            # SQLAlchemy async session
            db_url = f"postgresql+asyncpg://{db_config.get('user')}:{db_config.get('password')}@{db_config.get('host')}:{db_config.get('port')}/{db_config.get('database')}"
            engine = create_async_engine(db_url, pool_size=20, max_overflow=30)
            async_session = sessionmaker(engine, class_=AsyncSession)
            self.db_session = async_session()
            
            # Direct asyncpg pool for performance-critical operations
            self.db_pool = await asyncpg.create_pool(
                host=db_config.get('host'),
                port=db_config.get('port'),
                user=db_config.get('user'),
                password=db_config.get('password'),
                database=db_config.get('database'),
                min_size=10,
                max_size=20
            )
            
            # Load validation rules and integrity checks
            await self._load_validation_rules()
            await self._load_integrity_checks()
            
            # Create default validation rules
            await self._create_default_validation_rules()
            
            # Start background tasks
            self.metrics_task = asyncio.create_task(self._periodic_metrics_update())
            
            logger.info("Transaction validation system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize transaction validation system: {e}")
            raise
    
    async def validate_transaction(
        self,
        transaction_data: Dict[str, Any],
        transaction_type: TransactionType,
        validation_level: Optional[ValidationLevel] = None
    ) -> TransactionValidationReport:
        """Validate a transaction comprehensively"""
        start_time = datetime.utcnow()
        transaction_id = transaction_data.get('transaction_id', str(uuid.uuid4()))
        
        try:
            # Get applicable validation rules
            applicable_rules = self._get_applicable_rules(transaction_type, validation_level)
            
            # Check cache for recent validation
            if self.cache_validation_results:
                cached_result = await self._get_cached_validation(transaction_id)
                if cached_result:
                    return cached_result
            
            # Perform validations
            validation_results = []
            
            if self.parallel_validation:
                # Run validations in parallel
                validation_tasks = [
                    self._execute_validation_rule(rule, transaction_data, transaction_id)
                    for rule in applicable_rules
                ]
                
                validation_results = await asyncio.gather(*validation_tasks, return_exceptions=True)
                
                # Filter out exceptions and log them
                filtered_results = []
                for result in validation_results:
                    if isinstance(result, Exception):
                        logger.error(f"Validation rule failed with exception: {result}")
                    else:
                        filtered_results.append(result)
                validation_results = filtered_results
            else:
                # Run validations sequentially
                for rule in applicable_rules:
                    try:
                        result = await self._execute_validation_rule(rule, transaction_data, transaction_id)
                        validation_results.append(result)
                    except Exception as e:
                        logger.error(f"Validation rule {rule.rule_id} failed: {e}")
            
            # Determine overall status
            overall_status = self._determine_overall_status(validation_results)
            
            # Count results by status
            status_counts = self._count_results_by_status(validation_results)
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Create validation report
            report = TransactionValidationReport(
                transaction_id=transaction_id,
                overall_status=overall_status,
                total_rules_checked=len(applicable_rules),
                passed_count=status_counts.get(ValidationStatus.PASSED, 0),
                failed_count=status_counts.get(ValidationStatus.FAILED, 0),
                warning_count=status_counts.get(ValidationStatus.WARNING, 0),
                skipped_count=status_counts.get(ValidationStatus.SKIPPED, 0),
                validation_results=validation_results,
                execution_time_ms=execution_time
            )
            
            # Cache result if enabled
            if self.cache_validation_results:
                await self._cache_validation_result(report)
            
            # Store validation report
            await self._store_validation_report(report)
            
            # Update metrics
            await self._update_validation_metrics(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to validate transaction {transaction_id}: {e}")
            # Return error report
            return TransactionValidationReport(
                transaction_id=transaction_id,
                overall_status=ValidationStatus.FAILED,
                total_rules_checked=0,
                passed_count=0,
                failed_count=1,
                warning_count=0,
                skipped_count=0,
                validation_results=[
                    ValidationResult(
                        validation_id=str(uuid.uuid4()),
                        rule_id="system_error",
                        transaction_id=transaction_id,
                        status=ValidationStatus.FAILED,
                        level=ValidationLevel.CRITICAL,
                        category=ValidationCategory.INTEGRITY,
                        message=f"System error during validation: {str(e)}"
                    )
                ],
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
    
    async def validate_data_integrity(
        self,
        check_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive data integrity validation"""
        try:
            start_time = datetime.utcnow()
            
            # Get integrity checks to run
            checks_to_run = []
            if check_ids:
                checks_to_run = [self.integrity_checks[check_id] for check_id in check_ids if check_id in self.integrity_checks]
            else:
                checks_to_run = [check for check in self.integrity_checks.values() if check.is_active]
            
            # Execute integrity checks
            integrity_results = []
            
            for check in checks_to_run:
                try:
                    result = await self._execute_integrity_check(check)
                    integrity_results.append(result)
                except Exception as e:
                    logger.error(f"Integrity check {check.check_id} failed: {e}")
                    integrity_results.append({
                        'check_id': check.check_id,
                        'status': 'error',
                        'message': str(e),
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            # Calculate summary
            passed_checks = sum(1 for result in integrity_results if result.get('status') == 'passed')
            failed_checks = sum(1 for result in integrity_results if result.get('status') == 'failed')
            error_checks = sum(1 for result in integrity_results if result.get('status') == 'error')
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            integrity_report = {
                'validation_id': str(uuid.uuid4()),
                'timestamp': datetime.utcnow().isoformat(),
                'execution_time_ms': execution_time,
                'summary': {
                    'total_checks': len(checks_to_run),
                    'passed': passed_checks,
                    'failed': failed_checks,
                    'errors': error_checks,
                    'overall_status': 'passed' if failed_checks == 0 and error_checks == 0 else 'failed'
                },
                'results': integrity_results
            }
            
            # Store integrity report
            await self._store_integrity_report(integrity_report)
            
            return integrity_report
            
        except Exception as e:
            logger.error(f"Failed to validate data integrity: {e}")
            return {
                'validation_id': str(uuid.uuid4()),
                'timestamp': datetime.utcnow().isoformat(),
                'summary': {'overall_status': 'error'},
                'error': str(e)
            }
    
    async def add_validation_rule(self, rule_data: Dict[str, Any]) -> ValidationRule:
        """Add a new validation rule"""
        try:
            rule = ValidationRule(
                rule_id=rule_data.get('rule_id', f"rule_{uuid.uuid4().hex[:8]}"),
                name=rule_data['name'],
                description=rule_data['description'],
                category=ValidationCategory(rule_data['category']),
                level=ValidationLevel(rule_data['level']),
                condition=rule_data['condition'],
                error_message=rule_data['error_message'],
                is_active=rule_data.get('is_active', True),
                applies_to=set(TransactionType(t) for t in rule_data.get('applies_to', []))
            )
            
            # Validate the rule condition syntax
            if not self._validate_rule_condition(rule.condition):
                raise ValueError(f"Invalid rule condition: {rule.condition}")
            
            # Store rule
            self.validation_rules[rule.rule_id] = rule
            await self._store_validation_rule(rule)
            
            logger.info(f"Added validation rule: {rule.name}")
            return rule
            
        except Exception as e:
            logger.error(f"Failed to add validation rule: {e}")
            raise
    
    async def _execute_validation_rule(
        self,
        rule: ValidationRule,
        transaction_data: Dict[str, Any],
        transaction_id: str
    ) -> ValidationResult:
        """Execute a single validation rule"""
        start_time = datetime.utcnow()
        
        try:
            # Prepare transaction data for rule evaluation
            safe_data = self._prepare_data_for_rule(transaction_data)
            
            # Evaluate rule condition
            is_valid = rule.evaluate(safe_data)
            
            # Determine status
            if is_valid:
                status = ValidationStatus.PASSED
                message = f"Validation passed: {rule.name}"
            else:
                status = ValidationStatus.FAILED if rule.level in [ValidationLevel.ERROR, ValidationLevel.CRITICAL] else ValidationStatus.WARNING
                message = rule.error_message
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return ValidationResult(
                validation_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                transaction_id=transaction_id,
                status=status,
                level=rule.level,
                category=rule.category,
                message=message,
                details={'rule_name': rule.name, 'condition': rule.condition},
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return ValidationResult(
                validation_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                transaction_id=transaction_id,
                status=ValidationStatus.FAILED,
                level=ValidationLevel.ERROR,
                category=rule.category,
                message=f"Rule execution error: {str(e)}",
                details={'error': str(e), 'rule_name': rule.name},
                execution_time_ms=execution_time
            )
    
    async def _execute_integrity_check(self, check: DataIntegrityCheck) -> Dict[str, Any]:
        """Execute a data integrity check"""
        try:
            if not self.db_pool:
                raise RuntimeError("Database pool not initialized")
            
            async with self.db_pool.acquire() as conn:
                # Execute integrity check query
                result = await conn.fetchval(check.query)
                
                # Compare with expected result
                is_valid = result == check.expected_result
                
                return {
                    'check_id': check.check_id,
                    'check_type': check.check_type,
                    'description': check.description,
                    'status': 'passed' if is_valid else 'failed',
                    'actual_result': result,
                    'expected_result': check.expected_result,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                'check_id': check.check_id,
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _get_applicable_rules(
        self,
        transaction_type: TransactionType,
        validation_level: Optional[ValidationLevel] = None
    ) -> List[ValidationRule]:
        """Get validation rules applicable to transaction type and level"""
        applicable_rules = []
        
        for rule in self.validation_rules.values():
            if not rule.is_active:
                continue
            
            # Check if rule applies to transaction type
            if rule.applies_to and transaction_type not in rule.applies_to:
                continue
            
            # Check validation level filter
            if validation_level and rule.level.value != validation_level.value:
                continue
            
            applicable_rules.append(rule)
        
        return applicable_rules
    
    def _determine_overall_status(self, validation_results: List[ValidationResult]) -> ValidationStatus:
        """Determine overall validation status"""
        if not validation_results:
            return ValidationStatus.SKIPPED
        
        # Check for critical failures
        for result in validation_results:
            if result.status == ValidationStatus.FAILED and result.level == ValidationLevel.CRITICAL:
                return ValidationStatus.FAILED
        
        # Check for any failures
        has_failures = any(result.status == ValidationStatus.FAILED for result in validation_results)
        if has_failures:
            return ValidationStatus.FAILED
        
        # Check for warnings
        has_warnings = any(result.status == ValidationStatus.WARNING for result in validation_results)
        if has_warnings:
            return ValidationStatus.WARNING
        
        return ValidationStatus.PASSED
    
    def _count_results_by_status(self, validation_results: List[ValidationResult]) -> Dict[ValidationStatus, int]:
        """Count validation results by status"""
        counts = {}
        for result in validation_results:
            counts[result.status] = counts.get(result.status, 0) + 1
        return counts
    
    def _prepare_data_for_rule(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare transaction data for safe rule evaluation"""
        # Create a safe copy with type conversions
        safe_data = {}
        
        for key, value in transaction_data.items():
            # Convert to appropriate types for rule evaluation
            if isinstance(value, str) and value.replace('.', '', 1).isdigit():
                safe_data[key] = float(value)
            elif isinstance(value, (int, float, Decimal)):
                safe_data[key] = float(value)
            elif isinstance(value, bool):
                safe_data[key] = value
            elif isinstance(value, datetime):
                safe_data[key] = value
            else:
                safe_data[key] = str(value)
        
        return safe_data
    
    def _validate_rule_condition(self, condition: str) -> bool:
        """Validate rule condition syntax"""
        try:
            # Basic syntax validation
            compile(condition, '<string>', 'eval')
            
            # Check for dangerous operations
            dangerous_keywords = ['import', 'exec', 'eval', 'open', '__', 'globals', 'locals']
            for keyword in dangerous_keywords:
                if keyword in condition:
                    return False
            
            return True
        except SyntaxError:
            return False
    
    async def _load_validation_rules(self):
        """Load validation rules from storage"""
        # Placeholder for database loading
        pass
    
    async def _load_integrity_checks(self):
        """Load integrity checks from storage"""
        # Placeholder for database loading
        pass
    
    async def _create_default_validation_rules(self):
        """Create default validation rules"""
        default_rules = [
            {
                'name': 'Amount Validation',
                'description': 'Validate transaction amount is positive and within limits',
                'category': 'business_rules',
                'level': 'error',
                'condition': 'amount > 0 and amount <= 100000',
                'error_message': 'Transaction amount must be positive and not exceed $100,000',
                'applies_to': ['payment', 'transfer']
            },
            {
                'name': 'Currency Code Validation',
                'description': 'Validate currency code format',
                'category': 'data_format',
                'level': 'error',
                'condition': 'len(currency) == 3 and currency.isupper()',
                'error_message': 'Currency code must be a 3-letter uppercase code',
                'applies_to': ['payment', 'transfer', 'refund']
            },
            {
                'name': 'User ID Validation',
                'description': 'Validate user ID is present and valid format',
                'category': 'data_format',
                'level': 'critical',
                'condition': 'user_id and len(user_id) > 0',
                'error_message': 'User ID is required and cannot be empty',
                'applies_to': ['payment', 'transfer', 'payout']
            },
            {
                'name': 'Email Format Validation',
                'description': 'Validate email format if present',
                'category': 'data_format',
                'level': 'warning',
                'condition': 'not email or "@" in email',
                'error_message': 'Email format is invalid',
                'applies_to': ['payment']
            }
        ]
        
        for rule_data in default_rules:
            # Check if rule already exists
            rule_exists = any(rule.name == rule_data['name'] for rule in self.validation_rules.values())
            if not rule_exists:
                try:
                    await self.add_validation_rule(rule_data)
                except Exception as e:
                    logger.error(f"Failed to create default rule {rule_data['name']}: {e}")
    
    async def _get_cached_validation(self, transaction_id: str) -> Optional[TransactionValidationReport]:
        """Get cached validation result"""
        if not self.redis_client:
            return None
        
        try:
            cached_data = await self.redis_client.get(f"validation:{transaction_id}")
            if cached_data:
                return TransactionValidationReport(**json.loads(cached_data))
        except Exception:
            pass
        
        return None
    
    async def _cache_validation_result(self, report: TransactionValidationReport):
        """Cache validation result"""
        if not self.redis_client:
            return
        
        try:
            # Convert report to dict for JSON serialization
            report_dict = {
                'transaction_id': report.transaction_id,
                'overall_status': report.overall_status.value,
                'total_rules_checked': report.total_rules_checked,
                'passed_count': report.passed_count,
                'failed_count': report.failed_count,
                'warning_count': report.warning_count,
                'skipped_count': report.skipped_count,
                'execution_time_ms': report.execution_time_ms,
                'created_at': report.created_at.isoformat(),
                'validation_results': [
                    {
                        'validation_id': result.validation_id,
                        'rule_id': result.rule_id,
                        'status': result.status.value,
                        'level': result.level.value,
                        'category': result.category.value,
                        'message': result.message,
                        'timestamp': result.timestamp.isoformat()
                    }
                    for result in report.validation_results
                ]
            }
            
            await self.redis_client.setex(
                f"validation:{report.transaction_id}",
                int(self.cache_ttl.total_seconds()),
                json.dumps(report_dict)
            )
        except Exception as e:
            logger.error(f"Failed to cache validation result: {e}")
    
    async def _store_validation_report(self, report: TransactionValidationReport):
        """Store validation report in database"""
        # Placeholder for database storage
        pass
    
    async def _store_integrity_report(self, report: Dict[str, Any]):
        """Store integrity report in database"""
        # Placeholder for database storage
        pass
    
    async def _store_validation_rule(self, rule: ValidationRule):
        """Store validation rule in database"""
        # Placeholder for database storage
        pass
    
    async def _update_validation_metrics(self, report: TransactionValidationReport):
        """Update validation performance metrics"""
        self.validation_metrics['total_validations'] += 1
        self.validation_metrics['total_execution_time'] += report.execution_time_ms
        self.validation_metrics['average_execution_time'] = (
            self.validation_metrics['total_execution_time'] / 
            self.validation_metrics['total_validations']
        )
        
        # Update rule-specific metrics
        for result in report.validation_results:
            rule_id = result.rule_id
            if rule_id not in self.validation_metrics['rules_performance']:
                self.validation_metrics['rules_performance'][rule_id] = {
                    'executions': 0,
                    'total_time': 0,
                    'failures': 0
                }
            
            rule_metrics = self.validation_metrics['rules_performance'][rule_id]
            rule_metrics['executions'] += 1
            rule_metrics['total_time'] += result.execution_time_ms or 0
            
            if result.status == ValidationStatus.FAILED:
                rule_metrics['failures'] += 1
    
    async def _periodic_metrics_update(self):
        """Periodically update metrics in Redis"""
        while True:
            try:
                await asyncio.sleep(60)  # Update every minute
                
                if self.redis_client:
                    await self.redis_client.hset(
                        "validation_metrics",
                        mapping={
                            key: json.dumps(value) if isinstance(value, dict) else str(value)
                            for key, value in self.validation_metrics.items()
                        }
                    )
                
            except Exception as e:
                logger.error(f"Error updating validation metrics: {e}")
    
    def get_validation_metrics(self) -> Dict[str, Any]:
        """Get validation system metrics"""
        return {
            **self.validation_metrics,
            "total_rules": len(self.validation_rules),
            "active_rules": len([r for r in self.validation_rules.values() if r.is_active]),
            "total_integrity_checks": len(self.integrity_checks),
            "active_integrity_checks": len([c for c in self.integrity_checks.values() if c.is_active]),
            "cache_enabled": self.cache_validation_results,
            "parallel_validation": self.parallel_validation,
            "validation_timeout_seconds": int(self.validation_timeout.total_seconds())
        }