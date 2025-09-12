#!/usr/bin/env python3
"""
Payment Gateway Validator
Enterprise-grade request validation and business rule enforcement

© 2025 Fahed Mlaiel. All rights reserved.
Proprietary and confidential. Licensed under Enterprise Commercial License.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, timedelta
import asyncio
from enum import Enum

from ..core.configuration_manager import ConfigurationManager
from ..security.fraud_detection_engine import FraudDetectionEngine

logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ValidationResult:
    """Validation result with detailed feedback"""
    is_valid: bool
    severity: ValidationSeverity
    code: str
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class PaymentGatewayValidator:
    """
    Enterprise payment gateway validator with comprehensive validation rules.
    
    Features:
    - Request validation and sanitization
    - Business rule validation  
    - Compliance checking
    - Error handling and messaging
    - Multi-provider validation
    - Real-time fraud checks
    """

    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.fraud_detector = FraudDetectionEngine(config_manager)
        self.validation_rules = self._load_validation_rules()
        self.business_rules = self._load_business_rules()
        
        # Validation thresholds
        self.max_amount_single_transaction = Decimal('1000000.00')  # $1M
        self.max_amount_daily_user = Decimal('50000.00')  # $50K
        self.max_transactions_per_minute = 60
        self.min_amount = Decimal('0.01')
        
        # Compliance patterns
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.phone_pattern = re.compile(r'^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$')
        self.card_patterns = {
            'visa': re.compile(r'^4[0-9]{12}(?:[0-9]{3})?$'),
            'mastercard': re.compile(r'^5[1-5][0-9]{14}$'),
            'amex': re.compile(r'^3[47][0-9]{13}$'),
            'discover': re.compile(r'^6(?:011|5[0-9]{2})[0-9]{12}$')
        }
        
        logger.info("Payment Gateway Validator initialized with enterprise rules")

    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules from configuration"""
        return {
            'required_fields': {
                'payment_request': ['customer_id', 'amount', 'currency', 'payment_method'],
                'customer': ['customer_id', 'email'],
                'billing_address': ['country', 'postal_code']
            },
            'field_lengths': {
                'customer_id': (1, 100),
                'description': (0, 255),
                'reference_id': (1, 50),
                'metadata_key': (1, 40),
                'metadata_value': (0, 500)
            },
            'amount_ranges': {
                'USD': (Decimal('0.50'), Decimal('999999.99')),
                'EUR': (Decimal('0.50'), Decimal('999999.99')),
                'GBP': (Decimal('0.30'), Decimal('999999.99')),
                'CAD': (Decimal('0.50'), Decimal('999999.99')),
                'BTC': (Decimal('0.00001'), Decimal('100.0')),
                'ETH': (Decimal('0.001'), Decimal('1000.0'))
            }
        }

    def _load_business_rules(self) -> Dict[str, Any]:
        """Load business-specific validation rules"""
        return {
            'creator_revenue_rules': {
                'min_payout_threshold': Decimal('25.00'),
                'max_revenue_split_percentage': 95,
                'min_revenue_split_percentage': 60,
                'collaboration_max_participants': 10
            },
            'content_monetization_rules': {
                'min_content_quality_score': 75,
                'max_pricing_per_view': Decimal('5.00'),
                'min_pricing_per_view': Decimal('0.01'),
                'max_subscription_price': Decimal('999.99')
            },
            'platform_compliance_rules': {
                'required_age_verification': True,
                'kyc_threshold': Decimal('10000.00'),
                'aml_transaction_limit': Decimal('3000.00'),
                'max_failed_attempts': 3
            }
        }

    async def validate_payment_request(self, request_data: Dict[str, Any]) -> List[ValidationResult]:
        """
        Comprehensive payment request validation
        
        Args:
            request_data: Payment request data to validate
            
        Returns:
            List of validation results
        """
        results = []
        
        try:
            # Basic structure validation
            results.extend(await self._validate_required_fields(request_data, 'payment_request'))
            
            # Amount validation
            if 'amount' in request_data:
                results.extend(await self._validate_amount(request_data.get('amount'), request_data.get('currency', 'USD')))
            
            # Currency validation
            if 'currency' in request_data:
                results.extend(await self._validate_currency(request_data['currency']))
            
            # Customer validation
            if 'customer_id' in request_data:
                results.extend(await self._validate_customer(request_data['customer_id']))
            
            # Payment method validation
            if 'payment_method' in request_data:
                results.extend(await self._validate_payment_method(request_data['payment_method']))
            
            # Business rule validation
            results.extend(await self._validate_business_rules(request_data))
            
            # Fraud detection
            fraud_results = await self.fraud_detector.analyze_transaction(request_data)
            if fraud_results.get('risk_score', 0) > 0.8:
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.CRITICAL,
                    code="FRAUD_RISK_HIGH",
                    message="Transaction flagged as high fraud risk",
                    suggestion="Require additional verification"
                ))
            
            # Compliance validation
            results.extend(await self._validate_compliance(request_data))
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                code="VALIDATION_ERROR",
                message=f"Validation failed: {str(e)}"
            ))
        
        return results

    async def _validate_required_fields(self, data: Dict[str, Any], validation_type: str) -> List[ValidationResult]:
        """Validate required fields are present"""
        results = []
        required_fields = self.validation_rules['required_fields'].get(validation_type, [])
        
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    code="MISSING_REQUIRED_FIELD",
                    message=f"Required field '{field}' is missing or empty",
                    field=field,
                    suggestion=f"Please provide a valid value for {field}"
                ))
        
        return results

    async def _validate_amount(self, amount: Union[str, float, Decimal], currency: str) -> List[ValidationResult]:
        """Validate payment amount"""
        results = []
        
        try:
            amount_decimal = Decimal(str(amount))
            
            # Check minimum amount
            if amount_decimal < self.min_amount:
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    code="AMOUNT_TOO_LOW",
                    message=f"Amount {amount_decimal} is below minimum {self.min_amount}",
                    field="amount",
                    suggestion=f"Minimum amount is {self.min_amount}"
                ))
            
            # Check maximum amount
            if amount_decimal > self.max_amount_single_transaction:
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    code="AMOUNT_TOO_HIGH",
                    message=f"Amount {amount_decimal} exceeds maximum {self.max_amount_single_transaction}",
                    field="amount",
                    suggestion="Contact support for large transactions"
                ))
            
            # Currency-specific validation
            if currency in self.validation_rules['amount_ranges']:
                min_amount, max_amount = self.validation_rules['amount_ranges'][currency]
                if not (min_amount <= amount_decimal <= max_amount):
                    results.append(ValidationResult(
                        is_valid=False,
                        severity=ValidationSeverity.ERROR,
                        code="AMOUNT_OUT_OF_RANGE",
                        message=f"Amount {amount_decimal} not in valid range for {currency}",
                        field="amount",
                        suggestion=f"Amount must be between {min_amount} and {max_amount} for {currency}"
                    ))
            
        except (ValueError, TypeError) as e:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                code="INVALID_AMOUNT_FORMAT",
                message=f"Invalid amount format: {amount}",
                field="amount",
                suggestion="Amount must be a valid decimal number"
            ))
        
        return results

    async def _validate_currency(self, currency: str) -> List[ValidationResult]:
        """Validate currency code"""
        results = []
        
        valid_currencies = ['USD', 'EUR', 'GBP', 'CAD', 'JPY', 'AUD', 'CHF', 'BTC', 'ETH', 'LTC']
        
        if currency not in valid_currencies:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                code="INVALID_CURRENCY",
                message=f"Currency '{currency}' is not supported",
                field="currency",
                suggestion=f"Supported currencies: {', '.join(valid_currencies)}"
            ))
        
        return results

    async def _validate_customer(self, customer_id: str) -> List[ValidationResult]:
        """Validate customer information"""
        results = []
        
        # Customer ID format validation
        if not isinstance(customer_id, str) or len(customer_id) < 3:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                code="INVALID_CUSTOMER_ID",
                message="Customer ID must be at least 3 characters",
                field="customer_id"
            ))
        
        return results

    async def _validate_payment_method(self, payment_method: Dict[str, Any]) -> List[ValidationResult]:
        """Validate payment method details"""
        results = []
        
        if not isinstance(payment_method, dict):
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                code="INVALID_PAYMENT_METHOD",
                message="Payment method must be an object",
                field="payment_method"
            ))
            return results
        
        method_type = payment_method.get('type')
        if method_type == 'card':
            results.extend(await self._validate_card_details(payment_method))
        elif method_type == 'bank_account':
            results.extend(await self._validate_bank_account(payment_method))
        elif method_type == 'crypto':
            results.extend(await self._validate_crypto_wallet(payment_method))
        
        return results

    async def _validate_card_details(self, card_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate credit card details"""
        results = []
        
        card_number = card_data.get('number', '').replace(' ', '').replace('-', '')
        
        # Luhn algorithm validation
        if not self._validate_luhn(card_number):
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                code="INVALID_CARD_NUMBER",
                message="Invalid card number",
                field="payment_method.number"
            ))
        
        # Card brand validation
        brand = self._detect_card_brand(card_number)
        if not brand:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                code="UNKNOWN_CARD_BRAND",
                message="Unable to detect card brand",
                field="payment_method.number"
            ))
        
        # Expiry validation
        exp_month = card_data.get('exp_month')
        exp_year = card_data.get('exp_year')
        if exp_month and exp_year:
            try:
                exp_date = datetime(int(exp_year), int(exp_month), 1)
                if exp_date < datetime.now():
                    results.append(ValidationResult(
                        is_valid=False,
                        severity=ValidationSeverity.ERROR,
                        code="CARD_EXPIRED",
                        message="Card has expired",
                        field="payment_method.expiry"
                    ))
            except ValueError:
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    code="INVALID_EXPIRY_DATE",
                    message="Invalid expiry date format",
                    field="payment_method.expiry"
                ))
        
        return results

    async def _validate_bank_account(self, bank_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate bank account details"""
        results = []
        
        routing_number = bank_data.get('routing_number')
        account_number = bank_data.get('account_number')
        
        if routing_number and len(str(routing_number)) != 9:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                code="INVALID_ROUTING_NUMBER",
                message="Routing number must be 9 digits",
                field="payment_method.routing_number"
            ))
        
        if account_number and (len(str(account_number)) < 4 or len(str(account_number)) > 17):
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                code="INVALID_ACCOUNT_NUMBER",
                message="Account number must be 4-17 digits",
                field="payment_method.account_number"
            ))
        
        return results

    async def _validate_crypto_wallet(self, crypto_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate cryptocurrency wallet details"""
        results = []
        
        wallet_address = crypto_data.get('wallet_address')
        crypto_type = crypto_data.get('crypto_type', '').upper()
        
        if crypto_type == 'BTC':
            if not self._validate_bitcoin_address(wallet_address):
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    code="INVALID_BTC_ADDRESS",
                    message="Invalid Bitcoin wallet address",
                    field="payment_method.wallet_address"
                ))
        elif crypto_type == 'ETH':
            if not self._validate_ethereum_address(wallet_address):
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    code="INVALID_ETH_ADDRESS",
                    message="Invalid Ethereum wallet address",
                    field="payment_method.wallet_address"
                ))
        
        return results

    async def _validate_business_rules(self, request_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate business-specific rules"""
        results = []
        
        # Creator revenue validation
        if 'creator_revenue_split' in request_data:
            split_percentage = request_data['creator_revenue_split']
            min_split = self.business_rules['creator_revenue_rules']['min_revenue_split_percentage']
            max_split = self.business_rules['creator_revenue_rules']['max_revenue_split_percentage']
            
            if not (min_split <= split_percentage <= max_split):
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    code="INVALID_REVENUE_SPLIT",
                    message=f"Revenue split must be between {min_split}% and {max_split}%",
                    field="creator_revenue_split"
                ))
        
        # Content monetization validation
        if 'content_pricing' in request_data:
            pricing = Decimal(str(request_data['content_pricing']))
            min_price = self.business_rules['content_monetization_rules']['min_pricing_per_view']
            max_price = self.business_rules['content_monetization_rules']['max_pricing_per_view']
            
            if not (min_price <= pricing <= max_price):
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    code="INVALID_CONTENT_PRICING",
                    message=f"Content pricing must be between {min_price} and {max_price}",
                    field="content_pricing"
                ))
        
        return results

    async def _validate_compliance(self, request_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate compliance requirements"""
        results = []
        
        amount = Decimal(str(request_data.get('amount', 0)))
        
        # AML compliance
        if amount > self.business_rules['platform_compliance_rules']['aml_transaction_limit']:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                code="AML_REVIEW_REQUIRED",
                message="Transaction requires AML review",
                suggestion="Additional documentation may be required"
            ))
        
        # KYC compliance
        if amount > self.business_rules['platform_compliance_rules']['kyc_threshold']:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                code="KYC_VERIFICATION_REQUIRED",
                message="Transaction requires KYC verification",
                suggestion="Complete identity verification before proceeding"
            ))
        
        return results

    def _validate_luhn(self, card_number: str) -> bool:
        """Validate credit card number using Luhn algorithm"""
        if not card_number.isdigit():
            return False
        
        digits = [int(d) for d in card_number[::-1]]
        for i in range(1, len(digits), 2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        
        return sum(digits) % 10 == 0

    def _detect_card_brand(self, card_number: str) -> Optional[str]:
        """Detect credit card brand from number"""
        for brand, pattern in self.card_patterns.items():
            if pattern.match(card_number):
                return brand
        return None

    def _validate_bitcoin_address(self, address: str) -> bool:
        """Validate Bitcoin wallet address format"""
        if not address:
            return False
        
        # Basic Bitcoin address validation (simplified)
        if address.startswith(('1', '3', 'bc1')) and 26 <= len(address) <= 62:
            return True
        return False

    def _validate_ethereum_address(self, address: str) -> bool:
        """Validate Ethereum wallet address format"""
        if not address:
            return False
        
        # Basic Ethereum address validation
        if address.startswith('0x') and len(address) == 42:
            try:
                int(address[2:], 16)
                return True
            except ValueError:
                return False
        return False

    async def sanitize_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize input data to prevent injection attacks"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Remove potentially dangerous characters
                sanitized[key] = re.sub(r'[<>"\';]', '', value.strip())
            elif isinstance(value, dict):
                sanitized[key] = await self.sanitize_input(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    re.sub(r'[<>"\';]', '', str(item).strip()) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized

    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate validation summary from results"""
        total_issues = len(results)
        critical_issues = len([r for r in results if r.severity == ValidationSeverity.CRITICAL])
        error_issues = len([r for r in results if r.severity == ValidationSeverity.ERROR])
        warning_issues = len([r for r in results if r.severity == ValidationSeverity.WARNING])
        
        is_valid = critical_issues == 0 and error_issues == 0
        
        return {
            'is_valid': is_valid,
            'total_issues': total_issues,
            'issues_by_severity': {
                'critical': critical_issues,
                'error': error_issues,
                'warning': warning_issues,
                'info': total_issues - critical_issues - error_issues - warning_issues
            },
            'can_proceed': critical_issues == 0,
            'requires_manual_review': critical_issues > 0 or error_issues > 2,
            'validation_results': [
                {
                    'code': r.code,
                    'message': r.message,
                    'severity': r.severity.value,
                    'field': r.field,
                    'suggestion': r.suggestion
                }
                for r in results
            ]
        }

    async def validate_batch_requests(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate multiple payment requests in batch"""
        batch_results = []
        
        for i, request in enumerate(requests):
            try:
                results = await self.validate_payment_request(request)
                summary = self.get_validation_summary(results)
                batch_results.append({
                    'request_index': i,
                    'validation_summary': summary
                })
            except Exception as e:
                batch_results.append({
                    'request_index': i,
                    'error': str(e),
                    'validation_summary': {'is_valid': False, 'total_issues': 1}
                })
        
        total_valid = len([r for r in batch_results if r.get('validation_summary', {}).get('is_valid', False)])
        
        return {
            'total_requests': len(requests),
            'valid_requests': total_valid,
            'invalid_requests': len(requests) - total_valid,
            'batch_validation_results': batch_results
        }

# Enterprise-grade validation with multi-role expertise demonstration
__all__ = ['PaymentGatewayValidator', 'ValidationResult', 'ValidationSeverity']