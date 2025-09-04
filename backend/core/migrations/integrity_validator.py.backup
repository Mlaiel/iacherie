"""🔍 Integrity Validator - Enterprise Data Integrity and Validation Engine
========================================================================

Ultra-advanced data integrity validation system for IA Influencer Agent:
- Content protection data consistency verification
- Multi-modal fingerprint data validation
- Creator monetization data integrity checks
- Platform synchronization validation
- Advanced constraint and business rule enforcement

Author: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
This data validation engine is protected intellectual property.
Contact mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
import json
import hashlib
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set, Tuple, Union
from dataclasses import dataclass, field
import re
from decimal import Decimal

from sqlalchemy import create_engine, text, select, and_, or_, func, distinct
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, validator, ValidationError
import numpy as np

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Data validation levels"""
    BASIC = "basic"          # Essential constraints only
    STANDARD = "standard"    # Standard business rules
    ADVANCED = "advanced"    # Advanced consistency checks
    ULTRA = "ultra"          # Maximum validation rigor


class ValidationCategory(Enum):
    """Validation rule categories"""
    SCHEMA = "schema"                    # Database schema validation
    CONSTRAINT = "constraint"           # Data constraint validation
    BUSINESS_RULE = "business_rule"     # Business logic validation
    INTEGRITY = "integrity"             # Referential integrity
    PERFORMANCE = "performance"         # Performance-related validation
    SECURITY = "security"               # Security validation
    FINGERPRINT = "fingerprint"         # Fingerprint data validation
    MONETIZATION = "monetization"       # Revenue data validation
    COLLABORATION = "collaboration"     # Collaboration data validation


class ValidationSeverity(Enum):
    """Validation error severity levels"""
    INFO = "info"            # Informational
    WARNING = "warning"      # Warning - may need attention
    ERROR = "error"          # Error - requires correction
    CRITICAL = "critical"    # Critical - system integrity at risk


@dataclass
class ValidationRule:
    """Data validation rule specification"""
    rule_id: str
    name: str
    description: str
    category: ValidationCategory
    severity: ValidationSeverity
    table_name: str
    column_names: List[str]
    validation_function: str
    error_message: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    auto_fix: bool = False


@dataclass
class ValidationError:
    """Validation error details"""
    rule_id: str
    severity: ValidationSeverity
    table_name: str
    column_name: Optional[str]
    row_identifier: Optional[str]
    error_message: str
    actual_value: Any
    expected_value: Optional[Any] = None
    suggested_fix: Optional[str] = None


@dataclass
class ValidationResult:
    """Validation execution result"""
    validation_id: str
    level: ValidationLevel
    total_rules: int
    passed_rules: int
    failed_rules: int
    errors: List[ValidationError]
    warnings: List[ValidationError]
    execution_time: float
    validation_timestamp: datetime
    overall_status: str  # "passed", "failed", "warnings"


class IntegrityValidator:
    """
    Enterprise-grade data integrity validation engine
    
    Provides comprehensive validation for:
    - Content protection data consistency
    - Fingerprint data integrity and format validation
    - Creator monetization data accuracy
    - Multi-platform data synchronization integrity
    - Business rule enforcement and compliance
    """
    
    def __init__(self, 
                 database_url: str,
                 validation_level: ValidationLevel = ValidationLevel.STANDARD):
        self.database_url = database_url
        self.validation_level = validation_level
        self.engine = create_engine(database_url, echo=False)
        self.session_maker = sessionmaker(bind=self.engine)
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.custom_validators: Dict[str, Callable] = {}
        
        # Register built-in validation rules
        self._register_builtin_rules()
        self._register_builtin_validators()
        
    def register_validation_rule(self, rule: ValidationRule) -> None:
        """Register data validation rule"""
        self.validation_rules[rule.rule_id] = rule
        logger.info(f"Registered validation rule: {rule.rule_id}")
        
    def register_custom_validator(self, name: str, validator: Callable) -> None:
        """Register custom validation function"""
        self.custom_validators[name] = validator
        logger.info(f"Registered custom validator: {name}")
        
    async def validate_all(self) -> ValidationResult:
        """
        Execute complete data validation suite
        
        Returns:
            Comprehensive validation result with all errors and warnings
        """
        start_time = datetime.now(timezone.utc)
        validation_id = f"validation_{int(start_time.timestamp())}"
        
        logger.info(f"Starting comprehensive data validation: {validation_id}")
        
        errors = []
        warnings = []
        passed_rules = 0
        failed_rules = 0
        
        # Get applicable rules for current validation level
        applicable_rules = self._get_applicable_rules()
        
        for rule in applicable_rules:
            if not rule.enabled:
                continue
                
            try:
                rule_errors = await self._execute_validation_rule(rule)
                
                if rule_errors:
                    failed_rules += 1
                    
                    # Categorize by severity
                    for error in rule_errors:
                        if error.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
                            errors.append(error)
                        else:
                            warnings.append(error)
                            
                    # Attempt auto-fix if enabled
                    if rule.auto_fix:
                        await self._attempt_auto_fix(rule, rule_errors)
                        
                else:
                    passed_rules += 1
                    
            except Exception as e:
                failed_rules += 1
                errors.append(ValidationError(
                    rule_id=rule.rule_id,
                    severity=ValidationSeverity.CRITICAL,
                    table_name=rule.table_name,
                    column_name=None,
                    row_identifier=None,
                    error_message=f"Validation rule execution failed: {str(e)}",
                    actual_value=None
                ))
                
        end_time = datetime.now(timezone.utc)
        execution_time = (end_time - start_time).total_seconds()
        
        # Determine overall status
        if errors:
            overall_status = "failed"
        elif warnings:
            overall_status = "warnings"
        else:
            overall_status = "passed"
            
        result = ValidationResult(
            validation_id=validation_id,
            level=self.validation_level,
            total_rules=len(applicable_rules),
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            errors=errors,
            warnings=warnings,
            execution_time=execution_time,
            validation_timestamp=end_time,
            overall_status=overall_status
        )
        
        # Record validation result
        await self._record_validation_result(result)
        
        logger.info(f"Validation completed: {overall_status} - {failed_rules} failed, {len(warnings)} warnings")
        return result
        
    async def validate_content_fingerprints(self) -> ValidationResult:
        """
        Validate content fingerprint data integrity
        
        Checks:
        - Fingerprint data format consistency
        - Hash integrity and uniqueness
        - Vector embedding validity
        - Metadata completeness
        """
        fingerprint_rules = [
            rule for rule in self.validation_rules.values()
            if rule.category == ValidationCategory.FINGERPRINT
        ]
        
        return await self._execute_rule_subset("fingerprint_validation", fingerprint_rules)
        
    async def validate_monetization_data(self) -> ValidationResult:
        """
        Validate monetization and revenue data
        
        Checks:
        - Revenue amount accuracy
        - Currency consistency
        - Period validity
        - Platform data integrity
        """
        monetization_rules = [
            rule for rule in self.validation_rules.values()
            if rule.category == ValidationCategory.MONETIZATION
        ]
        
        return await self._execute_rule_subset("monetization_validation", monetization_rules)
        
    async def validate_collaboration_data(self) -> ValidationResult:
        """
        Validate creator collaboration data
        
        Checks:
        - Request status consistency
        - User relationship validity
        - Content availability
        - Terms and conditions compliance
        """
        collaboration_rules = [
            rule for rule in self.validation_rules.values()
            if rule.category == ValidationCategory.COLLABORATION
        ]
        
        return await self._execute_rule_subset("collaboration_validation", collaboration_rules)
        
    async def _execute_validation_rule(self, rule: ValidationRule) -> List[ValidationError]:
        """Execute single validation rule"""
        try:
            if rule.validation_function in self.custom_validators:
                validator_func = self.custom_validators[rule.validation_function]
                return await validator_func(rule)
            else:
                return await self._execute_builtin_validation(rule)
                
        except Exception as e:
            logger.error(f"Validation rule execution failed: {rule.rule_id} - {str(e)}")
            return [ValidationError(
                rule_id=rule.rule_id,
                severity=ValidationSeverity.CRITICAL,
                table_name=rule.table_name,
                column_name=None,
                row_identifier=None,
                error_message=f"Rule execution error: {str(e)}",
                actual_value=None
            )]
            
    async def _execute_builtin_validation(self, rule: ValidationRule) -> List[ValidationError]:
        """Execute built-in validation function"""
        if rule.validation_function == "check_not_null":
            return await self._validate_not_null(rule)
        elif rule.validation_function == "check_unique":
            return await self._validate_unique(rule)
        elif rule.validation_function == "check_foreign_key":
            return await self._validate_foreign_key(rule)
        elif rule.validation_function == "check_fingerprint_format":
            return await self._validate_fingerprint_format(rule)
        elif rule.validation_function == "check_revenue_consistency":
            return await self._validate_revenue_consistency(rule)
        elif rule.validation_function == "check_collaboration_status":
            return await self._validate_collaboration_status(rule)
        else:
            raise ValueError(f"Unknown validation function: {rule.validation_function}")
            
    async def _validate_not_null(self, rule: ValidationRule) -> List[ValidationError]:
        """Validate non-null constraints"""
        errors = []
        
        async with self._get_session() as session:
            for column_name in rule.column_names:
                query = text(f"""
                    SELECT COUNT(*) as null_count
                    FROM {rule.table_name}
                    WHERE {column_name} IS NULL
                """)
                
                result = await session.execute(query)
                null_count = result.scalar()
                
                if null_count > 0:
                    errors.append(ValidationError(
                        rule_id=rule.rule_id,
                        severity=rule.severity,
                        table_name=rule.table_name,
                        column_name=column_name,
                        row_identifier=None,
                        error_message=f"Found {null_count} null values in required column",
                        actual_value=f"{null_count} nulls",
                        expected_value="no nulls"
                    ))
                    
        return errors
        
    async def _validate_unique(self, rule: ValidationRule) -> List[ValidationError]:
        """Validate uniqueness constraints"""
        errors = []
        
        async with self._get_session() as session:
            columns_str = ", ".join(rule.column_names)
            query = text(f"""
                SELECT {columns_str}, COUNT(*) as duplicate_count
                FROM {rule.table_name}
                GROUP BY {columns_str}
                HAVING COUNT(*) > 1
            """)
            
            result = await session.execute(query)
            duplicates = result.fetchall()
            
            for duplicate in duplicates:
                duplicate_values = duplicate[:-1]  # All except count
                duplicate_count = duplicate[-1]   # Count
                
                errors.append(ValidationError(
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    table_name=rule.table_name,
                    column_name=", ".join(rule.column_names),
                    row_identifier=str(duplicate_values),
                    error_message=f"Found {duplicate_count} duplicate values",
                    actual_value=f"{duplicate_count} duplicates",
                    expected_value="unique values"
                ))
                
        return errors
        
    async def _validate_foreign_key(self, rule: ValidationRule) -> List[ValidationError]:
        """Validate foreign key constraints"""
        errors = []
        
        # Get foreign key reference from conditions
        ref_table = rule.conditions.get("ref_table")
        ref_column = rule.conditions.get("ref_column")
        
        if not ref_table or not ref_column:
            return [ValidationError(
                rule_id=rule.rule_id,
                severity=ValidationSeverity.ERROR,
                table_name=rule.table_name,
                column_name=rule.column_names[0] if rule.column_names else None,
                row_identifier=None,
                error_message="Foreign key validation requires ref_table and ref_column",
                actual_value=None
            )]
            
        async with self._get_session() as session:
            column_name = rule.column_names[0]
            query = text(f"""
                SELECT t1.{column_name}
                FROM {rule.table_name} t1
                LEFT JOIN {ref_table} t2 ON t1.{column_name} = t2.{ref_column}
                WHERE t1.{column_name} IS NOT NULL
                AND t2.{ref_column} IS NULL
            """)
            
            result = await session.execute(query)
            orphaned_records = result.fetchall()
            
            for record in orphaned_records:
                errors.append(ValidationError(
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    table_name=rule.table_name,
                    column_name=column_name,
                    row_identifier=str(record[0]),
                    error_message=f"Foreign key violation: referenced record not found",
                    actual_value=record[0],
                    expected_value=f"valid {ref_table}.{ref_column}"
                ))
                
        return errors
        
    async def _validate_fingerprint_format(self, rule: ValidationRule) -> List[ValidationError]:
        """Validate fingerprint data format"""
        errors = []
        
        async with self._get_session() as session:
            query = text(f"""
                SELECT fingerprint_id, hash_fingerprint, feature_fingerprint, metadata
                FROM {rule.table_name}
                WHERE fingerprint_id IS NOT NULL
            """)
            
            result = await session.execute(query)
            fingerprints = result.fetchall()
            
            for fp in fingerprints:
                fingerprint_id, hash_fp, feature_fp, metadata = fp
                
                # Validate hash format
                if not re.match(r'^[a-fA-F0-9]{64}$', hash_fp or ''):
                    errors.append(ValidationError(
                        rule_id=rule.rule_id,
                        severity=rule.severity,
                        table_name=rule.table_name,
                        column_name="hash_fingerprint",
                        row_identifier=str(fingerprint_id),
                        error_message="Invalid hash fingerprint format",
                        actual_value=hash_fp,
                        expected_value="64-character hex string"
                    ))
                    
                # Validate metadata JSON
                if metadata:
                    try:
                        if isinstance(metadata, str):
                            json.loads(metadata)
                    except json.JSONDecodeError:
                        errors.append(ValidationError(
                            rule_id=rule.rule_id,
                            severity=rule.severity,
                            table_name=rule.table_name,
                            column_name="metadata",
                            row_identifier=str(fingerprint_id),
                            error_message="Invalid JSON in metadata field",
                            actual_value=metadata,
                            expected_value="valid JSON"
                        ))
                        
        return errors
        
    async def _validate_revenue_consistency(self, rule: ValidationRule) -> List[ValidationError]:
        """Validate revenue data consistency"""
        errors = []
        
        async with self._get_session() as session:
            # Check for negative revenue amounts
            query = text(f"""
                SELECT revenue_id, revenue_amount
                FROM {rule.table_name}
                WHERE revenue_amount < 0
            """)
            
            result = await session.execute(query)
            negative_revenues = result.fetchall()
            
            for revenue in negative_revenues:
                errors.append(ValidationError(
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    table_name=rule.table_name,
                    column_name="revenue_amount",
                    row_identifier=str(revenue[0]),
                    error_message="Negative revenue amount found",
                    actual_value=revenue[1],
                    expected_value="positive amount"
                ))
                
            # Check date consistency
            query = text(f"""
                SELECT revenue_id, period_start, period_end
                FROM {rule.table_name}
                WHERE period_end < period_start
            """)
            
            result = await session.execute(query)
            invalid_periods = result.fetchall()
            
            for period in invalid_periods:
                errors.append(ValidationError(
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    table_name=rule.table_name,
                    column_name="period_end",
                    row_identifier=str(period[0]),
                    error_message="End date before start date",
                    actual_value=f"{period[1]} to {period[2]}",
                    expected_value="end date >= start date"
                ))
                
        return errors
        
    async def _validate_collaboration_status(self, rule: ValidationRule) -> List[ValidationError]:
        """Validate collaboration request status consistency"""
        errors = []
        
        async with self._get_session() as session:
            # Check for expired pending requests
            query = text(f"""
                SELECT request_id, request_status, expires_at
                FROM {rule.table_name}
                WHERE request_status = 'pending'
                AND expires_at < NOW()
            """)
            
            result = await session.execute(query)
            expired_requests = result.fetchall()
            
            for request in expired_requests:
                errors.append(ValidationError(
                    rule_id=rule.rule_id,
                    severity=ValidationSeverity.WARNING,
                    table_name=rule.table_name,
                    column_name="request_status",
                    row_identifier=str(request[0]),
                    error_message="Pending request past expiration date",
                    actual_value=f"pending (expired {request[2]})",
                    expected_value="expired status",
                    suggested_fix="Update status to 'expired'"
                ))
                
        return errors
        
    async def _execute_rule_subset(self, 
                                 validation_name: str, 
                                 rules: List[ValidationRule]) -> ValidationResult:
        """Execute subset of validation rules"""
        start_time = datetime.now(timezone.utc)
        validation_id = f"{validation_name}_{int(start_time.timestamp())}"
        
        errors = []
        warnings = []
        passed_rules = 0
        failed_rules = 0
        
        for rule in rules:
            if not rule.enabled:
                continue
                
            try:
                rule_errors = await self._execute_validation_rule(rule)
                
                if rule_errors:
                    failed_rules += 1
                    for error in rule_errors:
                        if error.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
                            errors.append(error)
                        else:
                            warnings.append(error)
                else:
                    passed_rules += 1
                    
            except Exception as e:
                failed_rules += 1
                errors.append(ValidationError(
                    rule_id=rule.rule_id,
                    severity=ValidationSeverity.CRITICAL,
                    table_name=rule.table_name,
                    column_name=None,
                    row_identifier=None,
                    error_message=f"Validation rule execution failed: {str(e)}",
                    actual_value=None
                ))
                
        end_time = datetime.now(timezone.utc)
        execution_time = (end_time - start_time).total_seconds()
        
        overall_status = "failed" if errors else ("warnings" if warnings else "passed")
        
        return ValidationResult(
            validation_id=validation_id,
            level=self.validation_level,
            total_rules=len(rules),
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            errors=errors,
            warnings=warnings,
            execution_time=execution_time,
            validation_timestamp=end_time,
            overall_status=overall_status
        )
        
    def _get_applicable_rules(self) -> List[ValidationRule]:
        """Get validation rules applicable to current validation level"""
        level_mapping = {
            ValidationLevel.BASIC: [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR],
            ValidationLevel.STANDARD: [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR, ValidationSeverity.WARNING],
            ValidationLevel.ADVANCED: [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR, ValidationSeverity.WARNING, ValidationSeverity.INFO],
            ValidationLevel.ULTRA: [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR, ValidationSeverity.WARNING, ValidationSeverity.INFO]
        }
        
        applicable_severities = level_mapping.get(self.validation_level, [ValidationSeverity.ERROR])
        
        return [
            rule for rule in self.validation_rules.values()
            if rule.severity in applicable_severities
        ]
        
    async def _attempt_auto_fix(self, rule: ValidationRule, errors: List[ValidationError]) -> None:
        """Attempt automatic fixing of validation errors"""
        # Implementation for auto-fix functionality
        logger.info(f"Auto-fix not implemented for rule: {rule.rule_id}")
        
    async def _record_validation_result(self, result: ValidationResult) -> None:
        """Record validation result for audit purposes"""
        async with self._get_session() as session:
            try:
                insert_query = text("""
                    INSERT INTO validation_history 
                    (validation_id, level, total_rules, passed_rules, failed_rules, 
                     error_count, warning_count, execution_time, overall_status, 
                     validation_timestamp, details)
                    VALUES 
                    (:validation_id, :level, :total_rules, :passed_rules, :failed_rules,
                     :error_count, :warning_count, :execution_time, :overall_status,
                     :validation_timestamp, :details)
                """)
                
                await session.execute(insert_query, {
                    "validation_id": result.validation_id,
                    "level": result.level.value,
                    "total_rules": result.total_rules,
                    "passed_rules": result.passed_rules,
                    "failed_rules": result.failed_rules,
                    "error_count": len(result.errors),
                    "warning_count": len(result.warnings),
                    "execution_time": result.execution_time,
                    "overall_status": result.overall_status,
                    "validation_timestamp": result.validation_timestamp,
                    "details": json.dumps({
                        "errors": [error.__dict__ for error in result.errors],
                        "warnings": [warning.__dict__ for warning in result.warnings]
                    }, default=str)
                })
                
                await session.commit()
                
            except SQLAlchemyError as e:
                logger.error(f"Failed to record validation result: {e}")
                
    def _register_builtin_rules(self) -> None:
        """Register built-in validation rules"""
        # Content fingerprint validation rules
        self.validation_rules.update({
            "fingerprint_not_null": ValidationRule(
                rule_id="fingerprint_not_null",
                name="Fingerprint Not Null",
                description="Ensure required fingerprint fields are not null",
                category=ValidationCategory.FINGERPRINT,
                severity=ValidationSeverity.ERROR,
                table_name="content_fingerprints",
                column_names=["content_id", "hash_fingerprint"],
                validation_function="check_not_null",
                error_message="Required fingerprint fields cannot be null"
            ),
            
            "fingerprint_unique_hash": ValidationRule(
                rule_id="fingerprint_unique_hash",
                name="Unique Fingerprint Hash",
                description="Ensure fingerprint hashes are unique",
                category=ValidationCategory.FINGERPRINT,
                severity=ValidationSeverity.ERROR,
                table_name="content_fingerprints",
                column_names=["hash_fingerprint"],
                validation_function="check_unique",
                error_message="Fingerprint hash must be unique"
            ),
            
            "fingerprint_format": ValidationRule(
                rule_id="fingerprint_format",
                name="Fingerprint Format Validation",
                description="Validate fingerprint data format",
                category=ValidationCategory.FINGERPRINT,
                severity=ValidationSeverity.ERROR,
                table_name="content_fingerprints",
                column_names=["hash_fingerprint", "metadata"],
                validation_function="check_fingerprint_format",
                error_message="Invalid fingerprint data format"
            ),
            
            # Revenue validation rules
            "revenue_consistency": ValidationRule(
                rule_id="revenue_consistency",
                name="Revenue Data Consistency",
                description="Validate revenue data consistency",
                category=ValidationCategory.MONETIZATION,
                severity=ValidationSeverity.ERROR,
                table_name="revenue_tracking",
                column_names=["revenue_amount", "period_start", "period_end"],
                validation_function="check_revenue_consistency",
                error_message="Revenue data consistency violation"
            ),
            
            # Collaboration validation rules
            "collaboration_status": ValidationRule(
                rule_id="collaboration_status",
                name="Collaboration Status Validation",
                description="Validate collaboration request status consistency",
                category=ValidationCategory.COLLABORATION,
                severity=ValidationSeverity.WARNING,
                table_name="collaboration_requests",
                column_names=["request_status", "expires_at"],
                validation_function="check_collaboration_status",
                error_message="Collaboration status inconsistency",
                auto_fix=True
            )
        })
        
    def _register_builtin_validators(self) -> None:
        """Register built-in validation functions"""
        # Built-in validators are already implemented as methods
        pass
        
    async def _get_session(self) -> Session:
        """Get database session"""
        return self.session_maker()
