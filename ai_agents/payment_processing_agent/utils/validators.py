"""Payment Validation Engine - Industrial Security & Compliance

Comprehensive validation system for payment data, fraud detection,
compliance checks, and security verification.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import re
import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
import hashlib
import hmac
import base64

from email_validator import validate_email, EmailNotValidError
from sqlalchemy.orm import Session

from .models import PaymentTransaction, PaymentMethod, PayoutSchedule
from .exceptions import (
    ValidationError,
    InvalidPaymentMethodError,
    ComplianceError,
    KYCError,
    AMLError,
    FraudDetectedError
)
from .config import PaymentConfig

logger = logging.getLogger(__name__)


class PaymentValidator:
    """    Industrial payment validation engine with comprehensive security checks.
    
    Validates payment data, performs compliance checks, fraud detection,
    and ensures data integrity for all payment operations.
    """
    def __init__(self, config: Optional[PaymentConfig] = None):
        """Initialize validator with configuration"""        self.config = config or PaymentConfig()
        
        # Validation patterns
        self.patterns = {
            "card_number": re.compile(r'^\d{13,19}$'),
            "cvv": re.compile(r'^\d{3,4}$'),
            "expiry": re.compile(r'^(0[1-9]|1[0-2])\/\d{2}$'),
            "iban": re.compile(r'^[A-Z]{2}\d{2}[A-Z0-9]{4,30}$'),
            "bic": re.compile(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$'),
            "bitcoin_address": re.compile(r'^[13][a-km-z A-HJ-NP-Z1-9]{25,34}$|^bc1[a-z0-9]{39,59}$'),
            "ethereum_address": re.compile(r'^0x[a-fA-F0-9]{40}$'),
            "phone": re.compile(r'^\+?[1-9]\d{1,14}$'),
            "postal_code": re.compile(r'^[A-Z0-9]{3,10}$'),
            "creator_id": re.compile(r'^[a-zA-Z0-9_-]{3,50}$')
        }
        
        # Blocked entities (example data - would be loaded from database/external service)
        self.blocked_countries = set(['IR', 'KP', 'SY', 'AF'])  # Sanctioned countries
        self.blocked_emails = set()
        self.blocked_ips = set()
        
        # Risk scoring weights
        self.risk_weights = {
            "amount_anomaly": 0.3,
            "frequency_anomaly": 0.25,
            "location_risk": 0.2,
            "account_age": 0.1,
            "payment_method_risk": 0.15
        }

    async def validate_payment_transaction(
        self,
        creator_id: str,
        amount: Union[Decimal, float, str],
        currency: str,
        payment_method: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Comprehensive payment transaction validation.
        
        Args:
            creator_id: Creator account identifier
            amount: Transaction amount
            currency: Currency code
            payment_method: Payment method identifier
            metadata: Additional transaction data
            
        Returns:
            Dict with validation results
            
        Raises:
            ValidationError: If validation fails
        """        try:
            validation_result = {
                "valid": True,
                "warnings": [],
                "risk_score": 0.0,
                "compliance_flags": []
            }
            
            # Basic field validation
            await self._validate_creator_id(creator_id)
            validated_amount = await self._validate_amount(amount, currency)
            await self._validate_currency(currency)
            
            # Payment method validation
            if payment_method:
                await self._validate_payment_method(creator_id, payment_method)
            
            # Amount limits validation
            await self._validate_amount_limits(creator_id, validated_amount, currency)
            
            # Frequency limits validation
            await self._validate_transaction_frequency(creator_id, validated_amount)
            
            # Risk assessment
            risk_score = await self._calculate_risk_score(
                creator_id, validated_amount, currency, payment_method, metadata
            )
            validation_result["risk_score"] = risk_score
            
            # Compliance checks
            compliance_flags = await self._check_compliance(creator_id, validated_amount, currency)
            validation_result["compliance_flags"] = compliance_flags
            
            # Final validation decision
            if risk_score > self.config.fraud_threshold:
                validation_result["valid"] = False
                validation_result["warnings"].append("High fraud risk detected")
                raise FraudDetectedError(
                    f"Transaction flagged for fraud: risk score {risk_score:.3f}"
                )
            
            logger.info(f"Transaction validation passed: {creator_id} - {amount} {currency}")
            return validation_result
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            raise ValidationError(f"Validation failed: {str(e)}")

    async def validate_revenue_processing(
        self,
        creator_id: str,
        content_id: str,
        amount: Union[Decimal, float, str],
        currency: str
    ) -> bool:
        """        Validate revenue processing request.
        
        Args:
            creator_id: Creator account identifier
            content_id: Content being monetized
            amount: Revenue amount
            currency: Currency code
            
        Returns:
            True if validation passes
            
        Raises:
            ValidationError: If validation fails
        """        try:
            # Basic validation
            await self._validate_creator_id(creator_id)
            await self._validate_content_id(content_id)
            validated_amount = await self._validate_amount(amount, currency)
            await self._validate_currency(currency)
            
            # Revenue-specific checks
            if validated_amount < Decimal("0.01"):
                raise ValidationError("Revenue amount must be at least 0.01")
            
            # Check for duplicate revenue entries
            await self._check_duplicate_revenue(creator_id, content_id, validated_amount)
            
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Revenue validation error: {str(e)}")
            raise ValidationError(f"Revenue validation failed: {str(e)}")

    async def validate_payout_request(
        self,
        creator_id: str,
        amount: Union[Decimal, float, str],
        currency: str,
        payment_method: str
    ) -> Dict[str, Any]:
        """        Validate payout request with comprehensive checks.
        
        Args:
            creator_id: Creator account identifier
            amount: Payout amount
            currency: Currency code
            payment_method: Payment method identifier
            
        Returns:
            Dict with validation results
            
        Raises:
            ValidationError: If validation fails
        """        try:
            validation_result = {
                "valid": True,
                "available_balance": Decimal("0.00"),
                "fees": Decimal("0.00"),
                "net_amount": Decimal("0.00")
            }
            
            # Basic validation
            await self._validate_creator_id(creator_id)
            validated_amount = await self._validate_amount(amount, currency)
            await self._validate_currency(currency)
            
            # Payment method validation
            payment_method_details = await self._validate_payment_method(creator_id, payment_method)
            
            # Minimum payout check
            if validated_amount < self.config.minimum_payout:
                raise ValidationError(
                    f"Amount {validated_amount} below minimum payout {self.config.minimum_payout}"
                )
            
            # Balance validation
            available_balance = await self._get_available_balance(creator_id, currency)
            if validated_amount > available_balance:
                raise ValidationError(
                    f"Insufficient balance: {available_balance} available, {validated_amount} requested"
                )
            
            # Calculate fees
            fees = await self._calculate_payout_fees(validated_amount, payment_method)
            net_amount = validated_amount - fees
            
            validation_result.update({
                "available_balance": available_balance,
                "fees": fees,
                "net_amount": net_amount
            })
            
            # KYC validation for large amounts
            if validated_amount > Decimal("1000.00"):
                await self._validate_kyc_status(creator_id)
            
            logger.info(f"Payout validation passed: {creator_id} - {validated_amount} {currency}")
            return validation_result
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Payout validation error: {str(e)}")
            raise ValidationError(f"Payout validation failed: {str(e)}")

    async def validate_webhook_signature(
        self,
        payload: str,
        signature: str,
        secret: str,
        provider: str = "stripe"
    ) -> bool:
        """        Validate webhook signature for security.
        
        Args:
            payload: Webhook payload
            signature: Provided signature
            secret: Webhook secret
            provider: Payment provider
            
        Returns:
            True if signature is valid
            
        Raises:
            ValidationError: If signature validation fails
        """        try:
            if provider == "stripe":
                return self._validate_stripe_signature(payload, signature, secret)
            elif provider == "wise":
                return self._validate_wise_signature(payload, signature, secret)
            elif provider == "paypal":
                return self._validate_paypal_signature(payload, signature, secret)
            else:
                return self._validate_generic_signature(payload, signature, secret)
                
        except Exception as e:
            logger.error(f"Webhook signature validation error: {str(e)}")
            raise ValidationError(f"Invalid webhook signature: {str(e)}")

    async def validate_compliance_status(
        self,
        creator_id: str,
        transaction_type: str,
        amount: Decimal,
        currency: str
    ) -> Dict[str, Any]:
        """        Validate compliance status for transaction.
        
        Args:
            creator_id: Creator account identifier
            transaction_type: Type of transaction
            amount: Transaction amount
            currency: Currency code
            
        Returns:
            Dict with compliance validation results
            
        Raises:
            ComplianceError: If compliance check fails
        """        try:
            compliance_result = {
                "compliant": True,
                "required_actions": [],
                "risk_level": "low"
            }
            
            # KYC status check
            kyc_status = await self._check_kyc_status(creator_id)
            if not kyc_status["verified"] and amount > Decimal("500.00"):
                compliance_result["compliant"] = False
                compliance_result["required_actions"].append("KYC verification required")
                compliance_result["risk_level"] = "high"
                
                raise KYCError(
                    "KYC verification required for high-value transactions",
                    kyc_status=kyc_status["status"]
                )
            
            # AML screening
            aml_status = await self._perform_aml_screening(creator_id)
            if aml_status["flagged"]:
                compliance_result["compliant"] = False
                compliance_result["required_actions"].append("AML review required")
                compliance_result["risk_level"] = "high"
                
                raise AMLError(
                    "AML screening flagged this transaction",
                    aml_flags=aml_status["flags"]
                )
            
            # Tax compliance
            if amount > Decimal("600.00"):  # US tax reporting threshold
                tax_status = await self._check_tax_reporting_status(creator_id)
                if not tax_status["compliant"]:
                    compliance_result["required_actions"].append("Tax information required")
            
            return compliance_result
            
        except (KYCError, AMLError):
            raise
        except Exception as e:
            logger.error(f"Compliance validation error: {str(e)}")
            raise ComplianceError(f"Compliance check failed: {str(e)}")

    # Private validation methods
    async def _validate_creator_id(self, creator_id: str):
        """Validate creator ID format and existence"""        if not creator_id or not isinstance(creator_id, str):
            raise ValidationError("Creator ID is required", field="creator_id")
        
        if not self.patterns["creator_id"].match(creator_id):
            raise ValidationError("Invalid creator ID format", field="creator_id")
        
        if len(creator_id) > 50:
            raise ValidationError("Creator ID too long (max 50 characters)", field="creator_id")

    async def _validate_content_id(self, content_id: str):
        """Validate content ID format"""        if not content_id or not isinstance(content_id, str):
            raise ValidationError("Content ID is required", field="content_id")
        
        if len(content_id) > 255:
            raise ValidationError("Content ID too long (max 255 characters)", field="content_id")

    async def _validate_amount(self, amount: Union[Decimal, float, str], currency: str) -> Decimal:
        """Validate and normalize amount"""        try:
            if isinstance(amount, str):
                amount = Decimal(amount)
            elif isinstance(amount, float):
                amount = Decimal(str(amount))
            elif not isinstance(amount, Decimal):
                raise ValidationError("Invalid amount type", field="amount")
            
            # Quantize to currency precision
            if currency in ["JPY", "KRW"]:  # No decimal places
                amount = amount.quantize(Decimal('1'))
            else:  # Two decimal places
                amount = amount.quantize(Decimal('0.01'))
            
            if amount <= 0:
                raise ValidationError("Amount must be positive", field="amount")
            
            if amount > Decimal("1000000.00"):  # 1M limit
                raise ValidationError("Amount exceeds maximum limit", field="amount")
            
            return amount
            
        except (InvalidOperation, ValueError) as e:
            raise ValidationError(f"Invalid amount: {str(e)}", field="amount")

    async def _validate_currency(self, currency: str):
        """Validate currency code"""        if not currency or not isinstance(currency, str):
            raise ValidationError("Currency is required", field="currency")
        
        if len(currency) != 3:
            raise ValidationError("Currency must be 3 characters", field="currency")
        
        if not self.config.validate_currency(currency.upper()):
            raise ValidationError(f"Currency {currency} not supported", field="currency")

    async def _validate_payment_method(self, creator_id: str, method_id: str) -> Dict[str, Any]:
        """Validate payment method exists and is active"""        # This would query the database for the payment method
        # For now, return mock validation
        return {
            "valid": True,
            "method_type": "bank_transfer",
            "verified": True
        }

    async def _validate_amount_limits(self, creator_id: str, amount: Decimal, currency: str):
        """Validate transaction amount against user limits"""        # Check daily limits
        daily_total = await self._get_daily_transaction_total(creator_id, currency)
        if daily_total + amount > self.config.daily_transaction_limit:
            raise ValidationError("Daily transaction limit exceeded")
        
        # Check monthly limits
        monthly_total = await self._get_monthly_transaction_total(creator_id, currency)
        if monthly_total + amount > self.config.monthly_transaction_limit:
            raise ValidationError("Monthly transaction limit exceeded")

    async def _validate_transaction_frequency(self, creator_id: str, amount: Decimal):
        """Validate transaction frequency for fraud detection"""        # Check recent transaction count
        recent_count = await self._get_recent_transaction_count(creator_id, hours=1)
        if recent_count > 10:  # Max 10 transactions per hour
            raise ValidationError("Transaction frequency limit exceeded")

    async def _calculate_risk_score(
        self,
        creator_id: str,
        amount: Decimal,
        currency: str,
        payment_method: Optional[str],
        metadata: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate fraud risk score"""        risk_score = 0.0
        
        # Amount anomaly detection
        avg_amount = await self._get_average_transaction_amount(creator_id, currency)
        if avg_amount > 0 and amount > avg_amount * 5:  # 5x normal amount
            risk_score += self.risk_weights["amount_anomaly"]
        
        # Frequency anomaly
        recent_count = await self._get_recent_transaction_count(creator_id, hours=24)
        if recent_count > 20:  # Unusual frequency
            risk_score += self.risk_weights["frequency_anomaly"]
        
        # Account age risk
        account_age = await self._get_account_age_days(creator_id)
        if account_age < 30:  # New account
            risk_score += self.risk_weights["account_age"]
        
        return min(risk_score, 1.0)  # Cap at 1.0

    async def _check_compliance(
        self,
        creator_id: str,
        amount: Decimal,
        currency: str
    ) -> List[str]:
        """Check compliance flags"""        flags = []
        
        # Large transaction flag
        if amount > Decimal("10000.00"):
            flags.append("large_transaction")
        
        # High-risk currency
        if currency in ["BTC", "ETH"]:
            flags.append("cryptocurrency")
        
        return flags

    def _validate_stripe_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Validate Stripe webhook signature"""        try:
            elements = signature.split(',')
            timestamp = None
            v1_signature = None
            
            for element in elements:
                key, value = element.split('=')
                if key == 't':
                    timestamp = int(value)
                elif key == 'v1':
                    v1_signature = value
            
            if not timestamp or not v1_signature:
                return False
            
            # Check timestamp tolerance (5 minutes)
            if abs(datetime.utcnow().timestamp() - timestamp) > 300:
                return False
            
            # Verify signature
            signed_payload = f"{timestamp}.{payload}"
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                signed_payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(v1_signature, expected_signature)
            
        except Exception:
            return False

    def _validate_wise_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Validate Wise webhook signature"""        try:
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha1
            ).digest()
            
            expected_signature_b64 = base64.b64encode(expected_signature).decode('utf-8')
            return hmac.compare_digest(signature, expected_signature_b64)
            
        except Exception:
            return False

    def _validate_paypal_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Validate PayPal webhook signature"""        try:
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature.lower(), expected_signature.lower())
            
        except Exception:
            return False

    def _validate_generic_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Validate generic HMAC signature"""        try:
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception:
            return False

    # Helper methods (would integrate with database and external services)
    async def _check_duplicate_revenue(self, creator_id: str, content_id: str, amount: Decimal):
        """Check for duplicate revenue entries"""        # Would query database for recent matching entries
        pass

    async def _get_available_balance(self, creator_id: str, currency: str) -> Decimal:
        """Get creator's available balance"""        # Would calculate from database
        return Decimal("1000.00")  # Mock value

    async def _calculate_payout_fees(self, amount: Decimal, payment_method: str) -> Decimal:
        """Calculate payout fees"""        # Would calculate based on payment method and provider
        return amount * Decimal("0.01")  # 1% fee

    async def _validate_kyc_status(self, creator_id: str):
        """Validate KYC status for high-value transactions"""        # Would check KYC status in database
        pass

    async def _check_kyc_status(self, creator_id: str) -> Dict[str, Any]:
        """Check KYC verification status"""        # Would query KYC service/database
        return {"verified": True, "status": "approved"}

    async def _perform_aml_screening(self, creator_id: str) -> Dict[str, Any]:
        """Perform AML screening"""        # Would integrate with AML service
        return {"flagged": False, "flags": []}

    async def _check_tax_reporting_status(self, creator_id: str) -> Dict[str, Any]:
        """Check tax reporting compliance"""        return {"compliant": True}

    async def _get_daily_transaction_total(self, creator_id: str, currency: str) -> Decimal:
        """Get daily transaction total"""        return Decimal("0.00")

    async def _get_monthly_transaction_total(self, creator_id: str, currency: str) -> Decimal:
        """Get monthly transaction total"""        return Decimal("0.00")

    async def _get_recent_transaction_count(self, creator_id: str, hours: int) -> int:
        """Get recent transaction count"""        return 0

    async def _get_average_transaction_amount(self, creator_id: str, currency: str) -> Decimal:
        """Get average transaction amount"""        return Decimal("100.00")

    async def _get_account_age_days(self, creator_id: str) -> int:
        """Get account age in days"""        return 365  # Mock value
