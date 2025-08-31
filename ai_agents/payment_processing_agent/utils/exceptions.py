"""Payment Processing Exceptions - Industrial Error Handling

Comprehensive exception classes for payment processing, fraud detection,
compliance violations, and provider-specific errors.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
from typing import Optional, Dict, Any


class PaymentProcessingError(Exception):
    """Base exception for payment processing errors."""    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.original_error = original_error


class InsufficientFundsError(PaymentProcessingError):
    """Exception raised when account has insufficient funds."""    
    def __init__(
        self,
        message: str = "Insufficient funds for transaction",
        available_balance: Optional[str] = None,
        requested_amount: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="insufficient_funds", **kwargs)
        self.available_balance = available_balance
        self.requested_amount = requested_amount


class InvalidPaymentMethodError(PaymentProcessingError):
    """Exception raised for invalid or expired payment methods."""    
    def __init__(
        self,
        message: str = "Invalid or expired payment method",
        payment_method_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="invalid_payment_method", **kwargs)
        self.payment_method_id = payment_method_id


class FraudDetectedError(PaymentProcessingError):
    """Exception raised when fraud is detected."""    
    def __init__(
        self,
        message: str = "Fraudulent activity detected",
        fraud_score: Optional[float] = None,
        risk_factors: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(message, error_code="fraud_detected", **kwargs)
        self.fraud_score = fraud_score
        self.risk_factors = risk_factors or {}


class ComplianceError(PaymentProcessingError):
    """Exception raised for compliance violations."""    
    def __init__(
        self,
        message: str = "Compliance requirement not met",
        compliance_type: Optional[str] = None,
        required_documents: Optional[list] = None,
        **kwargs
    ):
        super().__init__(message, error_code="compliance_violation", **kwargs)
        self.compliance_type = compliance_type
        self.required_documents = required_documents or []


class PaymentDeclinedError(PaymentProcessingError):
    """Exception raised when payment is declined by provider."""    
    def __init__(
        self,
        message: str = "Payment was declined",
        decline_code: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="payment_declined", **kwargs)
        self.decline_code = decline_code


class PayoutFailedError(PaymentProcessingError):
    """Exception raised when payout fails."""    
    def __init__(
        self,
        message: str = "Payout processing failed",
        payout_id: Optional[str] = None,
        failure_reason: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="payout_failed", **kwargs)
        self.payout_id = payout_id
        self.failure_reason = failure_reason


class RateLimitExceededError(PaymentProcessingError):
    """Exception raised when rate limits are exceeded."""    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, error_code="rate_limit_exceeded", **kwargs)
        self.retry_after = retry_after


class WebhookVerificationError(PaymentProcessingError):
    """Exception raised when webhook verification fails."""    
    def __init__(
        self,
        message: str = "Webhook signature verification failed",
        **kwargs
    ):
        super().__init__(message, error_code="webhook_verification_failed", **kwargs)


class CurrencyNotSupportedError(PaymentProcessingError):
    """Exception raised for unsupported currency operations."""    
    def __init__(
        self,
        message: str = "Currency not supported",
        currency: Optional[str] = None,
        supported_currencies: Optional[list] = None,
        **kwargs
    ):
        super().__init__(message, error_code="currency_not_supported", **kwargs)
        self.currency = currency
        self.supported_currencies = supported_currencies or []


class PaymentMethodNotSupportedError(PaymentProcessingError):
    """Exception raised for unsupported payment methods."""    
    def __init__(
        self,
        message: str = "Payment method not supported",
        payment_method: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="payment_method_not_supported", **kwargs)
        self.payment_method = payment_method


class ConfigurationError(PaymentProcessingError):
    """Exception raised for configuration errors."""    
    def __init__(
        self,
        message: str = "Payment processor configuration error",
        **kwargs
    ):
        super().__init__(message, error_code="configuration_error", **kwargs)


class ExternalServiceError(PaymentProcessingError):
    """Exception raised when external payment service fails."""    
    def __init__(
        self,
        message: str = "External payment service error",
        service_name: Optional[str] = None,
        service_error: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="external_service_error", **kwargs)
        self.service_name = service_name
        self.service_error = service_error


class TransactionNotFoundError(PaymentProcessingError):
    """Exception raised when transaction cannot be found."""    
    def __init__(
        self,
        message: str = "Transaction not found",
        transaction_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="transaction_not_found", **kwargs)
        self.transaction_id = transaction_id
