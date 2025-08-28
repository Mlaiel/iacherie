"""
Base Payment Processor - Abstract Foundation

Abstract base class defining the standard interface and common functionality
for all payment processors in the IA Influencer payment ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import uuid
import hashlib
import hmac

logger = logging.getLogger(__name__)


@dataclass
class PaymentResult:
    """Standard payment processing result structure."""
    success: bool
    transaction_id: Optional[str] = None
    external_id: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    status: str = "unknown"
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    fees: Optional[Decimal] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PayoutResult:
    """Standard payout processing result structure."""
    success: bool
    payout_id: Optional[str] = None
    external_id: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    status: str = "unknown"
    estimated_arrival: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    fees: Optional[Decimal] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class BalanceResult:
    """Account balance result structure."""
    available: Decimal
    pending: Decimal
    currency: str
    last_updated: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseProcessor(ABC):
    """
    Abstract base class for all payment processors.
    
    Defines the standard interface and provides common functionality
    for payment processing, payouts, balance checks, and webhooks.
    """
    
    def __init__(
        self,
        name: str,
        api_key: str,
        environment: str = "production",
        timeout: int = 30,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize base processor with common configuration.
        
        Args:
            name: Processor name identifier
            api_key: API authentication key
            environment: Environment (production, sandbox, test)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.name = name
        self.api_key = api_key
        self.environment = environment
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Performance metrics
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "average_response_time": 0.0,
            "last_health_check": None
        }
        
        # Configuration
        self.config = kwargs
        
        # Initialize processor-specific settings
        self._initialize()
    
    def _initialize(self):
        """Initialize processor-specific configuration."""
        pass
    
    async def process_payment(
        self,
        amount: Union[Decimal, float],
        currency: str,
        payment_method: str,
        customer_id: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentResult:
        """
        Process a payment transaction with comprehensive error handling and validation.
        
        Args:
            amount: Payment amount
            currency: Currency code (EUR, USD, etc.)
            payment_method: Payment method identifier
            customer_id: Customer/creator identifier
            description: Payment description
            metadata: Additional transaction metadata
            
        Returns:
            PaymentResult with transaction details
        """
        # Basic implementation with validation - to be overridden by specific processors
        start_time = datetime.utcnow()
        
        try:
            # Validate inputs
            if not isinstance(amount, (Decimal, int, float)) or amount <= 0:
                raise ValueError("Amount must be a positive number")
            
            if not currency or len(currency) != 3:
                raise ValueError("Currency must be a valid 3-letter code")
            
            if not payment_method:
                raise ValueError("Payment method is required")
            
            if not customer_id:
                raise ValueError("Customer ID is required")
            
            # Convert amount to Decimal for precision
            amount_decimal = Decimal(str(amount))
            
            # Check supported currencies
            supported_currencies = await self.get_supported_currencies()
            if currency.upper() not in supported_currencies:
                raise ValueError(f"Currency {currency} not supported. Supported: {supported_currencies}")
            
            # Estimate fees
            fee_breakdown = await self.estimate_fees(amount_decimal, currency, payment_method)
            
            # For base implementation, return a mock successful result
            # Specific processors should override this method with actual payment processing
            transaction_id = f"{self.name}_{uuid.uuid4().hex[:12]}"
            
            # Update metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._update_metrics(success=True, response_time=duration)
            
            return PaymentResult(
                success=True,
                transaction_id=transaction_id,
                external_id=f"ext_{transaction_id}",
                amount=amount_decimal,
                currency=currency.upper(),
                status="completed",
                fees=fee_breakdown.get("total_fee"),
                metadata={
                    "processor": self.name,
                    "customer_id": customer_id,
                    "payment_method": payment_method,
                    "description": description or "",
                    "processed_at": datetime.utcnow().isoformat(),
                    "fee_breakdown": fee_breakdown,
                    "custom_metadata": metadata or {}
                }
            )
            
        except Exception as e:
            # Update metrics for failure
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._update_metrics(success=False, response_time=duration)
            
            logger.error(f"Payment processing failed for {self.name}: {str(e)}")
            return PaymentResult(
                success=False,
                amount=Decimal(str(amount)) if amount else None,
                currency=currency.upper() if currency else None,
                status="failed",
                error_code="PROCESSING_ERROR",
                error_message=str(e),
                metadata={
                    "processor": self.name,
                    "failed_at": datetime.utcnow().isoformat(),
                    "error_details": str(e)
                }
            )
    
    async def execute_payout(
        self,
        amount: Union[Decimal, float],
        currency: str,
        payment_method: str,
        recipient_id: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PayoutResult:
        """
        Execute a payout to recipient with validation and error handling.
        
        Args:
            amount: Payout amount
            currency: Currency code
            payment_method: Payout method identifier
            recipient_id: Recipient identifier
            description: Payout description
            metadata: Additional payout metadata
            
        Returns:
            PayoutResult with payout details
        """
        start_time = datetime.utcnow()
        
        try:
            # Validate inputs
            if not isinstance(amount, (Decimal, int, float)) or amount <= 0:
                raise ValueError("Amount must be a positive number")
            
            if not currency or len(currency) != 3:
                raise ValueError("Currency must be a valid 3-letter code")
            
            if not payment_method:
                raise ValueError("Payment method is required")
            
            if not recipient_id:
                raise ValueError("Recipient ID is required")
            
            # Convert amount to Decimal
            amount_decimal = Decimal(str(amount))
            
            # Check account balance (basic implementation)
            try:
                balance = await self.get_balance(currency)
                if balance.available < amount_decimal:
                    raise ValueError(f"Insufficient balance. Available: {balance.available}, Required: {amount_decimal}")
            except NotImplementedError:
                # If balance check not implemented, continue
                pass
            
            # Estimate payout fees
            fee_breakdown = await self.estimate_fees(amount_decimal, currency, payment_method)
            total_amount = amount_decimal + fee_breakdown.get("total_fee", Decimal("0"))
            
            # For base implementation, return a mock result
            payout_id = f"{self.name}_payout_{uuid.uuid4().hex[:12]}"
            estimated_arrival = datetime.utcnow() + timedelta(days=1)  # Next business day
            
            # Update metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._update_metrics(success=True, response_time=duration)
            
            return PayoutResult(
                success=True,
                payout_id=payout_id,
                external_id=f"ext_{payout_id}",
                amount=amount_decimal,
                currency=currency.upper(),
                status="processing",
                estimated_arrival=estimated_arrival,
                fees=fee_breakdown.get("total_fee"),
                metadata={
                    "processor": self.name,
                    "recipient_id": recipient_id,
                    "payment_method": payment_method,
                    "description": description or "",
                    "initiated_at": datetime.utcnow().isoformat(),
                    "total_amount": total_amount,
                    "fee_breakdown": fee_breakdown,
                    "custom_metadata": metadata or {}
                }
            )
            
        except Exception as e:
            # Update metrics for failure
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._update_metrics(success=False, response_time=duration)
            
            logger.error(f"Payout processing failed for {self.name}: {str(e)}")
            return PayoutResult(
                success=False,
                amount=Decimal(str(amount)) if amount else None,
                currency=currency.upper() if currency else None,
                status="failed",
                error_code="PAYOUT_ERROR",
                error_message=str(e),
                metadata={
                    "processor": self.name,
                    "failed_at": datetime.utcnow().isoformat(),
                    "error_details": str(e)
                }
            )
    
    async def get_balance(
        self,
        currency: str = "EUR"
    ) -> BalanceResult:
        """
        Get account balance for currency with basic mock implementation.
        
        Args:
            currency: Currency code
            
        Returns:
            BalanceResult with balance information
        """
        # Base implementation returns mock balance - should be overridden
        logger.warning(f"Using mock balance for {self.name} processor")
        
        return BalanceResult(
            available=Decimal("1000.00"),
            pending=Decimal("50.00"),
            currency=currency.upper(),
            last_updated=datetime.utcnow(),
            metadata={
                "processor": self.name,
                "account_type": "test",
                "note": "Mock balance - implement actual balance retrieval in subclass"
            }
        )
    
    async def verify_webhook(
        self,
        payload: str,
        signature: str,
        secret: Optional[str] = None
    ) -> bool:
        """
        Verify webhook signature authenticity using basic validation.
        
        Args:
            payload: Raw webhook payload
            signature: Webhook signature
            secret: Webhook secret for verification
            
        Returns:
            True if signature is valid
        """
        try:
            # Basic implementation - should be overridden with actual signature verification
            if not payload or not signature:
                return False
            
            # For demo purposes, accept any non-empty signature
            # Real implementations should use HMAC verification
            import hashlib
            import hmac
            
            if secret:
                # Basic HMAC verification
                expected_signature = hmac.new(
                    secret.encode('utf-8'),
                    payload.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                
                return hmac.compare_digest(signature, expected_signature)
            else:
                # Without secret, just check signature is not empty
                return len(signature.strip()) > 0
                
        except Exception as e:
            logger.error(f"Webhook verification failed for {self.name}: {str(e)}")
            return False
    
    async def parse_webhook(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse webhook payload into standard format.
        
        Args:
            payload: Webhook payload
            
        Returns:
            Standardized webhook data
        """
        try:
            # Basic webhook parsing - should be overridden for specific processor formats
            return {
                "processor": self.name,
                "event_type": payload.get("type", "unknown"),
                "event_id": payload.get("id", str(uuid.uuid4())),
                "created": payload.get("created", datetime.utcnow().timestamp()),
                "data": payload.get("data", {}),
                "object_type": payload.get("object", "unknown"),
                "parsed_at": datetime.utcnow().isoformat(),
                "raw_payload": payload
            }
            
        except Exception as e:
            logger.error(f"Webhook parsing failed for {self.name}: {str(e)}")
            return {
                "processor": self.name,
                "event_type": "parse_error",
                "error": str(e),
                "parsed_at": datetime.utcnow().isoformat(),
                "raw_payload": payload
            }
    
    async def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[Union[Decimal, float]] = None,
        reason: Optional[str] = None
    ) -> PaymentResult:
        """
        Refund a payment transaction.
        
        Args:
            transaction_id: Original transaction ID
            amount: Refund amount (None for full refund)
            reason: Refund reason
            
        Returns:
            PaymentResult with refund details
        """
        # Default implementation - can be overridden
        logger.warning(f"Refunds not implemented for {self.name}")
        return PaymentResult(
            success=False,
            transaction_id=transaction_id,
            error_message=f"Refund functionality not implemented for {self.name}",
            details={
                "refund_requested": amount,
                "reason": reason,
                "status": "not_implemented"
            }
        )
    
    async def get_transaction(
        self,
        transaction_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get transaction details by ID.
        
        Args:
            transaction_id: Transaction identifier
            
        Returns:
            Transaction details or None if not found
        """
        # Default implementation - can be overridden
        logger.warning(f"Transaction lookup not implemented for {self.name}")
        return {
            "transaction_id": transaction_id,
            "status": "not_implemented",
            "message": f"Transaction lookup not available for {self.name}",
            "error": "Method not implemented"
        }
    
    async def list_payment_methods(
        self,
        customer_id: str
    ) -> List[Dict[str, Any]]:
        """
        List available payment methods for customer.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            List of payment methods
        """
        # Default implementation - can be overridden
        return []
    
    async def create_payment_method(
        self,
        customer_id: str,
        method_type: str,
        method_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create new payment method for customer.
        
        Args:
            customer_id: Customer identifier
            method_type: Payment method type
            method_data: Payment method details
            
        Returns:
            Created payment method details
        """
        # Default implementation - can be overridden
        logger.warning(f"Payment method creation not implemented for {self.name}")
        return {
            "success": False,
            "payment_method_id": None,
            "error_message": f"Payment method creation not implemented for {self.name}",
            "status": "not_implemented",
            "processor": self.name
        }
    
    async def health_check(self) -> bool:
        """
        Perform health check on payment processor.
        
        Returns:
            True if processor is healthy
        """
        try:
            start_time = datetime.utcnow()
            
            # Default health check - attempt balance lookup
            await self.get_balance()
            
            # Update metrics
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            
            self._update_metrics(success=True, response_time=response_time)
            self.metrics["last_health_check"] = end_time
            
            logger.info(f"Health check passed for {self.name} processor")
            return True
            
        except Exception as e:
            self._update_metrics(success=False)
            logger.error(f"Health check failed for {self.name} processor: {str(e)}")
            return False
    
    async def get_supported_currencies(self) -> List[str]:
        """
        Get list of supported currencies.
        
        Returns:
            List of supported currency codes
        """
        # Default implementation - can be overridden
        return ["EUR", "USD", "GBP"]
    
    async def get_supported_countries(self) -> List[str]:
        """
        Get list of supported countries.
        
        Returns:
            List of supported country codes
        """
        # Default implementation - can be overridden
        return ["DE", "US", "GB", "FR", "NL", "CH"]
    
    async def estimate_fees(
        self,
        amount: Union[Decimal, float],
        currency: str,
        payment_method: str
    ) -> Dict[str, Decimal]:
        """
        Estimate fees for payment processing.
        
        Args:
            amount: Payment amount
            currency: Currency code
            payment_method: Payment method
            
        Returns:
            Fee breakdown dictionary
        """
        # Default implementation - can be overridden
        amount_decimal = Decimal(str(amount))
        
        # Basic fee calculation (2.9% + 0.30)
        percentage_fee = (amount_decimal * Decimal("0.029")).quantize(Decimal("0.01"))
        fixed_fee = Decimal("0.30")
        total_fee = percentage_fee + fixed_fee
        
        return {
            "percentage_fee": percentage_fee,
            "fixed_fee": fixed_fee,
            "total_fee": total_fee
        }
    
    def _update_metrics(
        self,
        success: bool,
        response_time: Optional[float] = None
    ):
        """Update processor performance metrics."""
        self.metrics["requests_total"] += 1
        
        if success:
            self.metrics["requests_success"] += 1
        else:
            self.metrics["requests_failed"] += 1
        
        if response_time is not None:
            # Calculate rolling average
            current_avg = self.metrics["average_response_time"]
            total_requests = self.metrics["requests_total"]
            
            if total_requests == 1:
                self.metrics["average_response_time"] = response_time
            else:
                # Exponential moving average
                alpha = 0.1
                self.metrics["average_response_time"] = (
                    alpha * response_time + (1 - alpha) * current_avg
                )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get processor performance metrics."""
        success_rate = 0.0
        if self.metrics["requests_total"] > 0:
            success_rate = (
                self.metrics["requests_success"] / self.metrics["requests_total"]
            ) * 100
        
        return {
            "processor": self.name,
            "environment": self.environment,
            "requests_total": self.metrics["requests_total"],
            "requests_success": self.metrics["requests_success"],
            "requests_failed": self.metrics["requests_failed"],
            "success_rate": round(success_rate, 2),
            "average_response_time": round(self.metrics["average_response_time"], 3),
            "last_health_check": self.metrics["last_health_check"]
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass
    
    def __str__(self) -> str:
        """String representation of processor."""
        return f"{self.name}Processor(environment={self.environment})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"environment='{self.environment}', "
            f"timeout={self.timeout})"
        )
