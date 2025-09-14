"""💳 Payment Gateway Validator
================================

Enterprise validation system for payment requests, business rules compliance,
and data sanitization with comprehensive error handling and security checks.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import uuid
import asyncio
from pydantic import BaseModel, validator, ValidationError

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation strictness levels"""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    ENTERPRISE = "enterprise"


class ValidationError(Exception):
    """Custom validation error"""
    pass


@dataclass
class ValidationResult:
    """Validation result container"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_data: Optional[Dict[str, Any]] = None
    validation_score: float = 0.0
    risk_indicators: List[str] = None

    def __post_init__(self) -> None:
        if self.risk_indicators is None:
            self.risk_indicators = []


class PaymentRequestModel(BaseModel):
    """Pydantic model for payment request validation"""
    transaction_id: str
    amount: Decimal
    currency: str
    payment_method: str
    customer_id: Optional[str] = None
    merchant_id: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('amount')
    def validate_amount(cls, v) -> None:
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v > Decimal('1000000'):
            raise ValueError('Amount exceeds maximum limit')
        return v.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @validator('currency')
    def validate_currency(cls, v) -> None:
        valid_currencies = {'USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'BTC', 'ETH', 'USDC'}
        if v.upper() not in valid_currencies:
            raise ValueError(f'Unsupported currency: {v}')
        return v.upper()

    @validator('transaction_id')
    def validate_transaction_id(cls, v) -> None:
        if not re.match(r'^[a-zA-Z0-9\-_]{10,50}$', v):
            raise ValueError('Invalid transaction ID format')
        return v


class PaymentGatewayValidator:
    """Enterprise payment gateway validation system"""

    def __init__(self, validation_level -> None: ValidationLevel = ValidationLevel.ENTERPRISE) -> None:
        self.validation_level = validation_level
        self.max_amount_limits = {
            'USD': Decimal('100000'),
            'EUR': Decimal('85000'),
            'GBP': Decimal('75000'),
            'BTC': Decimal('5'),
            'ETH': Decimal('50'),
            'USDC': Decimal('100000')
        }
        self.risk_patterns = [
            r'test|fake|dummy',
            r'fraud|scam|cheat',
            r'hack|exploit|breach'
        ]

    async def validate_payment_request(self, request_data: Dict[str, Any]) -> ValidationResult:
        """Comprehensive payment request validation"""
        errors = []
        warnings = []
        risk_indicators = []
        validation_score = 100.0

        try:
            # Basic structure validation
            structure_result = await self._validate_structure(request_data)
            errors.extend(structure_result.errors)
            warnings.extend(structure_result.warnings)
            validation_score -= len(structure_result.errors) * 10

            # Business rules validation
            business_result = await self._validate_business_rules(request_data)
            errors.extend(business_result.errors)
            warnings.extend(business_result.warnings)
            validation_score -= len(business_result.errors) * 15

            # Security validation
            security_result = await self._validate_security(request_data)
            errors.extend(security_result.errors)
            warnings.extend(security_result.warnings)
            risk_indicators.extend(security_result.risk_indicators)
            validation_score -= len(security_result.errors) * 20

            # Compliance validation
            compliance_result = await self._validate_compliance(request_data)
            errors.extend(compliance_result.errors)
            warnings.extend(compliance_result.warnings)
            validation_score -= len(compliance_result.errors) * 25

            # Data sanitization
            sanitized_data = await self._sanitize_data(request_data)

            validation_score = max(0.0, validation_score)
            is_valid = len(errors) == 0 and validation_score >= 70.0

            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                sanitized_data=sanitized_data,
                validation_score=validation_score,
                risk_indicators=risk_indicators
            )

        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation system error: {str(e)}"],
                warnings=[],
                validation_score=0.0
            )

    async def _validate_structure(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate data structure using Pydantic"""
        errors = []
        warnings = []

        try:
            PaymentRequestModel(**data)
        except ValidationError as e:
            for error in e.errors():
                field = error['loc'][0] if error['loc'] else 'unknown'
                message = error['msg']
                errors.append(f"Structure validation failed for {field}: {message}")

        # Check for missing optional but recommended fields
        if 'customer_id' not in data:
            warnings.append("Customer ID not provided - recommended for tracking")
        
        if 'description' not in data:
            warnings.append("Transaction description not provided - recommended for clarity")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)

    async def _validate_business_rules(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate business rules compliance"""
        errors = []
        warnings = []

        amount = Decimal(str(data.get('amount', 0)))
        currency = data.get('currency', '').upper()
        
        # Amount limits by currency
        if currency in self.max_amount_limits:
            if amount > self.max_amount_limits[currency]:
                errors.append(f"Amount {amount} {currency} exceeds maximum limit {self.max_amount_limits[currency]}")

        # Minimum amount validation
        min_amounts = {'USD': Decimal('0.50'), 'EUR': Decimal('0.50'), 'BTC': Decimal('0.00001')}
        if currency in min_amounts and amount < min_amounts[currency]:
            errors.append(f"Amount {amount} {currency} below minimum {min_amounts[currency]}")

        # Payment method validation
        payment_method = data.get('payment_method', '')
        valid_methods = ['credit_card', 'debit_card', 'bank_transfer', 'crypto_wallet', 'paypal', 'wise']
        if payment_method not in valid_methods:
            errors.append(f"Invalid payment method: {payment_method}")

        # Merchant validation
        merchant_id = data.get('merchant_id', '')
        if not merchant_id or len(merchant_id) < 5:
            errors.append("Valid merchant ID required")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)

    async def _validate_security(self, data: Dict[str, Any]) -> ValidationResult:
        """Security-focused validation"""
        errors = []
        warnings = []
        risk_indicators = []

        # Check for suspicious patterns
        description = data.get('description', '').lower()
        for pattern in self.risk_patterns:
            if re.search(pattern, description):
                risk_indicators.append(f"Suspicious pattern detected: {pattern}")

        # Transaction ID security check
        transaction_id = data.get('transaction_id', '')
        if transaction_id:
            # Check for sequential patterns (potential fraud)
            if re.search(r'(.)\1{4,}', transaction_id):
                risk_indicators.append("Sequential pattern in transaction ID")
            
            # Check for known bad patterns
            if re.search(r'(test|fake|demo)', transaction_id.lower()):
                risk_indicators.append("Test pattern in transaction ID")

        # Metadata security validation
        metadata = data.get('metadata', {})
        if isinstance(metadata, dict):
            for key, value in metadata.items():
                if isinstance(value, str) and len(value) > 1000:
                    warnings.append(f"Large metadata value for key {key}")
                
                # Check for script injection attempts
                if isinstance(value, str) and re.search(r'<script|javascript:|data:', value.lower()):
                    errors.append(f"Potential script injection in metadata key {key}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            risk_indicators=risk_indicators
        )

    async def _validate_compliance(self, data: Dict[str, Any]) -> ValidationResult:
        """Compliance and regulatory validation"""
        errors = []
        warnings = []

        # PCI DSS compliance checks
        if 'card_number' in data:
            errors.append("Raw card number detected - PCI DSS violation")

        if 'cvv' in data:
            errors.append("Raw CVV detected - PCI DSS violation")

        # GDPR compliance checks
        customer_id = data.get('customer_id')
        if customer_id and not self._validate_data_processing_consent(customer_id):
            warnings.append("Data processing consent not verified")

        # AML compliance for large amounts
        amount = Decimal(str(data.get('amount', 0)))
        if amount > Decimal('10000'):
            if not data.get('aml_verified'):
                warnings.append("Large transaction requires AML verification")

        # Cryptocurrency compliance
        currency = data.get('currency', '').upper()
        if currency in ['BTC', 'ETH', 'USDC']:
            if not data.get('crypto_compliance_verified'):
                warnings.append("Cryptocurrency transaction requires compliance verification")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)

    async def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize and normalize data"""
        sanitized = data.copy()

        # Normalize currency
        if 'currency' in sanitized:
            sanitized['currency'] = sanitized['currency'].upper().strip()

        # Sanitize description
        if 'description' in sanitized:
            # Remove HTML tags and normalize whitespace
            description = re.sub(r'<[^>]+>', '', str(sanitized['description']))
            description = re.sub(r'\s+', ' ', description).strip()
            sanitized['description'] = description[:500]  # Limit length

        # Normalize amount precision
        if 'amount' in sanitized:
            amount = Decimal(str(sanitized['amount']))
            sanitized['amount'] = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Sanitize metadata
        if 'metadata' in sanitized and isinstance(sanitized['metadata'], dict):
            clean_metadata = {}
            for key, value in sanitized['metadata'].items():
                # Clean key
                clean_key = re.sub(r'[^\w\-_]', '', str(key))[:50]
                # Clean value
                if isinstance(value, str):
                    clean_value = re.sub(r'[<>&"\'`]', '', value)[:1000]
                else:
                    clean_value = value
                clean_metadata[clean_key] = clean_value
            sanitized['metadata'] = clean_metadata

        return sanitized

    def _validate_data_processing_consent(self, customer_id: str) -> bool:
        """Check if customer has given data processing consent"""
        # In real implementation, this would check against a database
        # For now, return True as placeholder
        return True

    async def validate_batch_requests(self, requests: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Validate multiple payment requests in batch"""
        tasks = [self.validate_payment_request(request) for request in requests]
        return await asyncio.gather(*tasks)

    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate validation summary statistics"""
        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        
        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)
        total_risks = sum(len(r.risk_indicators) for r in results)
        
        avg_score = sum(r.validation_score for r in results) / total if total > 0 else 0

        return {
            'total_requests': total,
            'valid_requests': valid,
            'invalid_requests': total - valid,
            'success_rate': valid / total if total > 0 else 0,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'total_risk_indicators': total_risks,
            'average_validation_score': round(avg_score, 2)
        }