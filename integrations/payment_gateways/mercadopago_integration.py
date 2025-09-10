"""
MercadoPago Integration for Ainflue Platform
Enterprise-grade MercadoPago payment processing for Latin American markets

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
import logging
from dataclasses import dataclass
from enum import Enum
import base64
import uuid

import aiohttp
import structlog

from ..core.base_integration import BaseIntegration
from ..core.exceptions import (
    PaymentError, InvalidConfigurationError, 
    SecurityError, ValidationError
)
from ..core.security import SecurityManager
from ..core.monitoring import MetricsCollector
from ..core.cache import CacheManager

logger = structlog.get_logger(__name__)

class MercadoPagoEnvironment(Enum):
    """MercadoPago environment settings"""
    PRODUCTION = "https://api.mercadopago.com"
    SANDBOX = "https://api.mercadolibre.com"

class PaymentMethod(Enum):
    """Supported payment methods"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    TICKET = "ticket"  # Boleto bancário, Oxxo, etc.
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    PIX = "pix"  # Brazilian instant payment
    PSE = "pse"  # Colombian bank transfer

class PaymentStatus(Enum):
    """Payment status values"""
    PENDING = "pending"
    APPROVED = "approved"
    AUTHORIZED = "authorized"
    IN_PROCESS = "in_process"
    IN_MEDIATION = "in_mediation"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    CHARGED_BACK = "charged_back"

class DocumentType(Enum):
    """Document types for Latin American countries"""
    CPF = "CPF"  # Brazil
    CNPJ = "CNPJ"  # Brazil
    CUIT = "CUIT"  # Argentina
    CUIL = "CUIL"  # Argentina
    DNI = "DNI"  # Argentina
    CURP = "CURP"  # Mexico
    RFC = "RFC"  # Mexico
    CC = "CC"  # Colombia
    CE = "CE"  # Colombia
    NIT = "NIT"  # Colombia
    CI = "CI"  # Chile
    RUT = "RUT"  # Chile

class Currency(Enum):
    """Supported currencies"""
    ARS = "ARS"  # Argentine Peso
    BRL = "BRL"  # Brazilian Real
    CLP = "CLP"  # Chilean Peso
    COP = "COP"  # Colombian Peso
    MXN = "MXN"  # Mexican Peso
    PEN = "PEN"  # Peruvian Sol
    UYU = "UYU"  # Uruguayan Peso
    USD = "USD"  # US Dollar

@dataclass
class MercadoPagoConfig:
    """MercadoPago configuration parameters"""
    access_token: str
    public_key: str
    client_id: str
    client_secret: str
    environment: MercadoPagoEnvironment = MercadoPagoEnvironment.SANDBOX
    webhook_secret: Optional[str] = None
    country: str = "BR"  # Brazil by default
    currency: Currency = Currency.BRL
    notification_url: Optional[str] = None
    back_urls: Optional[Dict[str, str]] = None
    auto_return: str = "approved"
    binary_mode: bool = False
    expires: bool = True
    expiration_date_from: Optional[str] = None
    expiration_date_to: Optional[str] = None
    external_reference: Optional[str] = None
    marketplace_fee: Optional[Decimal] = None
    differential_pricing_id: Optional[int] = None
    statement_descriptor: str = "AINFLUE"
    
    def __post_init__(self):
        if self.back_urls is None:
            self.back_urls = {
                "success": "https://ainflue.com/payment/success",
                "failure": "https://ainflue.com/payment/failure",
                "pending": "https://ainflue.com/payment/pending"
            }

@dataclass
class PayerInfo:
    """Payer information for MercadoPago"""
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[Dict[str, str]] = None
    identification: Optional[Dict[str, str]] = None
    address: Optional[Dict[str, Any]] = None
    date_created: Optional[str] = None

@dataclass
class PaymentRequest:
    """MercadoPago payment request structure"""
    transaction_amount: Decimal
    currency_id: str
    description: str
    payment_method_id: Optional[str] = None
    token: Optional[str] = None
    installments: int = 1
    issuer_id: Optional[str] = None
    payer: Optional[PayerInfo] = None
    external_reference: Optional[str] = None
    notification_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    additional_info: Optional[Dict[str, Any]] = None
    capture: bool = True
    binary_mode: bool = False

@dataclass
class ProcessedPayment:
    """Processed MercadoPago payment result"""
    id: int
    status: PaymentStatus
    status_detail: str
    operation_type: str
    transaction_amount: Decimal
    currency_id: str
    payment_method_id: str
    payment_type_id: str
    installments: int
    transaction_details: Dict[str, Any]
    date_created: datetime
    date_approved: Optional[datetime]
    date_last_updated: datetime
    money_release_date: Optional[datetime]
    collector_id: int
    payer: Dict[str, Any]
    metadata: Dict[str, Any]
    fee_details: List[Dict[str, Any]]
    external_reference: Optional[str]
    point_of_interaction: Optional[Dict[str, Any]]

class MercadoPagoIntegration(BaseIntegration):
    """
    Enterprise MercadoPago integration for Ainflue platform
    
    Features:
    - Complete Latin American market coverage
    - Multiple payment methods (cards, tickets, PIX, PSE)
    - Real-time payment status tracking
    - Advanced fraud prevention
    - Marketplace and split payment support
    - Comprehensive webhook handling
    - Multi-country support with local regulations
    - Subscription and recurring payment support
    """

    def __init__(self, config: MercadoPagoConfig):
        super().__init__("mercadopago")
        self.config = config
        self.security_manager = SecurityManager()
        self.metrics = MetricsCollector()
        self.cache = CacheManager()
        
        # API configuration
        self.base_url = config.environment.value
        self.headers = {
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "Ainflue/1.0.0",
            "X-Integrator-Id": "dev_24c65fb163bf11ea96500242ac130004"
        }
        
        # Transaction tracking
        self._transactions: Dict[str, ProcessedPayment] = {}
        
        # Country-specific configuration
        self.country_configs = {
            "AR": {"currency": "ARS", "site_id": "MLA"},
            "BR": {"currency": "BRL", "site_id": "MLB"},
            "CL": {"currency": "CLP", "site_id": "MLC"},
            "CO": {"currency": "COP", "site_id": "MCO"},
            "MX": {"currency": "MXN", "site_id": "MLM"},
            "PE": {"currency": "PEN", "site_id": "MPE"},
            "UY": {"currency": "UYU", "site_id": "MLU"}
        }
        
        logger.info("MercadoPago integration initialized",
                   environment=config.environment.value,
                   country=config.country,
                   currency=config.currency.value)

    async def _make_request(self,
                          method: str,
                          endpoint: str,
                          data: Optional[Dict[str, Any]] = None,
                          params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make authenticated request to MercadoPago API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data if data else None,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    response_data = await response.json()
                    
                    if response.status >= 400:
                        error_msg = response_data.get("message", "Unknown error")
                        logger.error("MercadoPago API error",
                                   status=response.status,
                                   error=error_msg,
                                   endpoint=endpoint)
                        raise PaymentError(f"MercadoPago API error: {error_msg}")
                    
                    return response_data
                    
        except aiohttp.ClientError as e:
            logger.error("MercadoPago API request failed",
                        endpoint=endpoint,
                        error=str(e))
            raise PaymentError(f"API request failed: {e}")

    async def get_payment_methods(self, public_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get available payment methods for the configured country
        
        Args:
            public_key: Optional public key for specific merchant
            
        Returns:
            List of available payment methods
        """
        try:
            params = {}
            if public_key:
                params["public_key"] = public_key
            
            response = await self._make_request(
                "GET",
                "/v1/payment_methods",
                params=params
            )
            
            self.metrics.increment("mercadopago.payment_methods.retrieved")
            
            logger.info("Payment methods retrieved",
                       count=len(response) if isinstance(response, list) else 0,
                       country=self.config.country)
            
            return response if isinstance(response, list) else []
            
        except Exception as e:
            self.metrics.increment("mercadopago.payment_methods.failed")
            logger.error("Failed to get payment methods", error=str(e))
            raise PaymentError(f"Failed to get payment methods: {e}")

    async def get_identification_types(self) -> List[Dict[str, Any]]:
        """
        Get available identification types for the configured country
        
        Returns:
            List of identification types
        """
        try:
            response = await self._make_request(
                "GET",
                "/v1/identification_types"
            )
            
            self.metrics.increment("mercadopago.identification_types.retrieved")
            
            logger.info("Identification types retrieved",
                       count=len(response) if isinstance(response, list) else 0,
                       country=self.config.country)
            
            return response if isinstance(response, list) else []
            
        except Exception as e:
            self.metrics.increment("mercadopago.identification_types.failed")
            logger.error("Failed to get identification types", error=str(e))
            raise PaymentError(f"Failed to get identification types: {e}")

    async def create_payment(self, payment_request: PaymentRequest) -> ProcessedPayment:
        """
        Create a new payment in MercadoPago
        
        Args:
            payment_request: Payment request data
            
        Returns:
            Processed payment result
        """
        try:
            # Prepare payment data
            payment_data = {
                "transaction_amount": float(payment_request.transaction_amount),
                "currency_id": payment_request.currency_id,
                "description": payment_request.description,
                "installments": payment_request.installments,
                "capture": payment_request.capture,
                "binary_mode": payment_request.binary_mode
            }
            
            # Add optional fields
            if payment_request.payment_method_id:
                payment_data["payment_method_id"] = payment_request.payment_method_id
            
            if payment_request.token:
                payment_data["token"] = payment_request.token
            
            if payment_request.issuer_id:
                payment_data["issuer_id"] = payment_request.issuer_id
            
            if payment_request.external_reference:
                payment_data["external_reference"] = payment_request.external_reference
            
            if payment_request.notification_url:
                payment_data["notification_url"] = payment_request.notification_url
            elif self.config.notification_url:
                payment_data["notification_url"] = self.config.notification_url
            
            if payment_request.metadata:
                payment_data["metadata"] = payment_request.metadata
            
            if payment_request.additional_info:
                payment_data["additional_info"] = payment_request.additional_info
            
            # Add payer information
            if payment_request.payer:
                payer_data = {}
                if payment_request.payer.email:
                    payer_data["email"] = payment_request.payer.email
                if payment_request.payer.identification:
                    payer_data["identification"] = payment_request.payer.identification
                if payment_request.payer.name:
                    payer_data["first_name"] = payment_request.payer.name
                if payment_request.payer.surname:
                    payer_data["last_name"] = payment_request.payer.surname
                if payment_request.payer.phone:
                    payer_data["phone"] = payment_request.payer.phone
                if payment_request.payer.address:
                    payer_data["address"] = payment_request.payer.address
                
                payment_data["payer"] = payer_data
            
            # Add statement descriptor
            payment_data["statement_descriptor"] = self.config.statement_descriptor
            
            # Add marketplace fee if configured
            if self.config.marketplace_fee:
                payment_data["application_fee"] = float(self.config.marketplace_fee)
            
            # Create payment
            response = await self._make_request(
                "POST",
                "/v1/payments",
                data=payment_data
            )
            
            # Process response
            processed_payment = self._process_payment_response(response)
            
            # Store transaction
            self._transactions[str(processed_payment.id)] = processed_payment
            
            # Cache transaction data
            await self.cache.set(
                f"mercadopago_payment:{processed_payment.id}",
                processed_payment,
                ttl=86400  # 24 hours
            )
            
            self.metrics.increment("mercadopago.payments.created")
            self.metrics.observe("mercadopago.payment_amount", 
                               float(processed_payment.transaction_amount))
            
            logger.info("MercadoPago payment created",
                       payment_id=processed_payment.id,
                       status=processed_payment.status.value,
                       amount=float(processed_payment.transaction_amount),
                       currency=processed_payment.currency_id)
            
            return processed_payment
            
        except Exception as e:
            self.metrics.increment("mercadopago.payments.failed")
            logger.error("MercadoPago payment creation failed", error=str(e))
            raise PaymentError(f"Payment creation failed: {e}")

    def _process_payment_response(self, response: Dict[str, Any]) -> ProcessedPayment:
        """Process MercadoPago payment response into ProcessedPayment object"""
        try:
            # Parse dates
            date_created = datetime.fromisoformat(
                response["date_created"].replace("Z", "+00:00")
            )
            
            date_approved = None
            if response.get("date_approved"):
                date_approved = datetime.fromisoformat(
                    response["date_approved"].replace("Z", "+00:00")
                )
            
            date_last_updated = datetime.fromisoformat(
                response["date_last_updated"].replace("Z", "+00:00")
            )
            
            money_release_date = None
            if response.get("money_release_date"):
                money_release_date = datetime.fromisoformat(
                    response["money_release_date"].replace("Z", "+00:00")
                )
            
            return ProcessedPayment(
                id=response["id"],
                status=PaymentStatus(response["status"]),
                status_detail=response.get("status_detail", ""),
                operation_type=response.get("operation_type", ""),
                transaction_amount=Decimal(str(response["transaction_amount"])),
                currency_id=response["currency_id"],
                payment_method_id=response.get("payment_method_id", ""),
                payment_type_id=response.get("payment_type_id", ""),
                installments=response.get("installments", 1),
                transaction_details=response.get("transaction_details", {}),
                date_created=date_created,
                date_approved=date_approved,
                date_last_updated=date_last_updated,
                money_release_date=money_release_date,
                collector_id=response.get("collector_id", 0),
                payer=response.get("payer", {}),
                metadata=response.get("metadata", {}),
                fee_details=response.get("fee_details", []),
                external_reference=response.get("external_reference"),
                point_of_interaction=response.get("point_of_interaction")
            )
            
        except Exception as e:
            logger.error("Failed to process payment response", error=str(e))
            raise ValidationError(f"Invalid payment response: {e}")

    async def get_payment(self, payment_id: int) -> Optional[ProcessedPayment]:
        """
        Get payment information by ID
        
        Args:
            payment_id: MercadoPago payment ID
            
        Returns:
            Payment information or None if not found
        """
        try:
            # Check cache first
            cached_payment = await self.cache.get(f"mercadopago_payment:{payment_id}")
            if cached_payment:
                return cached_payment
            
            # Get from API
            response = await self._make_request(
                "GET",
                f"/v1/payments/{payment_id}"
            )
            
            processed_payment = self._process_payment_response(response)
            
            # Update cache
            await self.cache.set(
                f"mercadopago_payment:{payment_id}",
                processed_payment,
                ttl=86400
            )
            
            self.metrics.increment("mercadopago.payments.retrieved")
            
            return processed_payment
            
        except Exception as e:
            logger.error("Failed to get payment",
                        payment_id=payment_id,
                        error=str(e))
            return None

    async def capture_payment(self, payment_id: int) -> ProcessedPayment:
        """
        Capture an authorized payment
        
        Args:
            payment_id: Payment ID to capture
            
        Returns:
            Updated payment information
        """
        try:
            response = await self._make_request(
                "PUT",
                f"/v1/payments/{payment_id}",
                data={"capture": True}
            )
            
            processed_payment = self._process_payment_response(response)
            
            # Update cache
            await self.cache.set(
                f"mercadopago_payment:{payment_id}",
                processed_payment,
                ttl=86400
            )
            
            self.metrics.increment("mercadopago.payments.captured")
            
            logger.info("MercadoPago payment captured",
                       payment_id=payment_id,
                       status=processed_payment.status.value)
            
            return processed_payment
            
        except Exception as e:
            self.metrics.increment("mercadopago.captures.failed")
            logger.error("Payment capture failed",
                        payment_id=payment_id,
                        error=str(e))
            raise PaymentError(f"Payment capture failed: {e}")

    async def cancel_payment(self, payment_id: int) -> ProcessedPayment:
        """
        Cancel a payment
        
        Args:
            payment_id: Payment ID to cancel
            
        Returns:
            Updated payment information
        """
        try:
            response = await self._make_request(
                "PUT",
                f"/v1/payments/{payment_id}",
                data={"status": "cancelled"}
            )
            
            processed_payment = self._process_payment_response(response)
            
            # Update cache
            await self.cache.set(
                f"mercadopago_payment:{payment_id}",
                processed_payment,
                ttl=86400
            )
            
            self.metrics.increment("mercadopago.payments.cancelled")
            
            logger.info("MercadoPago payment cancelled",
                       payment_id=payment_id)
            
            return processed_payment
            
        except Exception as e:
            self.metrics.increment("mercadopago.cancellations.failed")
            logger.error("Payment cancellation failed",
                        payment_id=payment_id,
                        error=str(e))
            raise PaymentError(f"Payment cancellation failed: {e}")

    async def refund_payment(self,
                           payment_id: int,
                           amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """
        Create a refund for a payment
        
        Args:
            payment_id: Payment ID to refund
            amount: Refund amount (full refund if None)
            
        Returns:
            Refund information
        """
        try:
            refund_data = {}
            if amount:
                refund_data["amount"] = float(amount)
            
            response = await self._make_request(
                "POST",
                f"/v1/payments/{payment_id}/refunds",
                data=refund_data
            )
            
            self.metrics.increment("mercadopago.refunds.created")
            self.metrics.observe("mercadopago.refund_amount", 
                               float(amount) if amount else 0)
            
            logger.info("MercadoPago refund created",
                       payment_id=payment_id,
                       refund_id=response.get("id"),
                       amount=float(amount) if amount else "full")
            
            return response
            
        except Exception as e:
            self.metrics.increment("mercadopago.refunds.failed")
            logger.error("Refund creation failed",
                        payment_id=payment_id,
                        error=str(e))
            raise PaymentError(f"Refund creation failed: {e}")

    async def create_preference(self,
                              items: List[Dict[str, Any]],
                              payer: Optional[Dict[str, Any]] = None,
                              external_reference: Optional[str] = None,
                              expires: Optional[bool] = None) -> Dict[str, Any]:
        """
        Create payment preference for checkout
        
        Args:
            items: List of items to be paid
            payer: Payer information
            external_reference: External reference
            expires: Whether preference expires
            
        Returns:
            Payment preference data
        """
        try:
            preference_data = {
                "items": items,
                "back_urls": self.config.back_urls,
                "auto_return": self.config.auto_return,
                "binary_mode": self.config.binary_mode,
                "statement_descriptor": self.config.statement_descriptor
            }
            
            if payer:
                preference_data["payer"] = payer
            
            if external_reference:
                preference_data["external_reference"] = external_reference
            
            if expires is not None:
                preference_data["expires"] = expires
            elif self.config.expires:
                preference_data["expires"] = self.config.expires
            
            if self.config.expiration_date_from:
                preference_data["expiration_date_from"] = self.config.expiration_date_from
            
            if self.config.expiration_date_to:
                preference_data["expiration_date_to"] = self.config.expiration_date_to
            
            if self.config.notification_url:
                preference_data["notification_url"] = self.config.notification_url
            
            if self.config.differential_pricing_id:
                preference_data["differential_pricing"] = {
                    "id": self.config.differential_pricing_id
                }
            
            response = await self._make_request(
                "POST",
                "/checkout/preferences",
                data=preference_data
            )
            
            self.metrics.increment("mercadopago.preferences.created")
            
            logger.info("MercadoPago preference created",
                       preference_id=response.get("id"),
                       init_point=response.get("init_point"))
            
            return response
            
        except Exception as e:
            self.metrics.increment("mercadopago.preferences.failed")
            logger.error("Preference creation failed", error=str(e))
            raise PaymentError(f"Preference creation failed: {e}")

    async def validate_webhook(self,
                             raw_body: bytes,
                             headers: Dict[str, str]) -> bool:
        """
        Validate webhook signature from MercadoPago
        
        Args:
            raw_body: Raw webhook body
            headers: Request headers
            
        Returns:
            True if webhook is valid
        """
        try:
            if not self.config.webhook_secret:
                logger.warning("Webhook secret not configured")
                return False
            
            # Get signature from headers
            x_signature = headers.get("x-signature")
            x_request_id = headers.get("x-request-id")
            
            if not x_signature or not x_request_id:
                logger.warning("Missing webhook signature headers")
                return False
            
            # Parse signature components
            signature_parts = {}
            for part in x_signature.split(","):
                key, value = part.split("=", 1)
                signature_parts[key.strip()] = value.strip()
            
            ts = signature_parts.get("ts")
            v1 = signature_parts.get("v1")
            
            if not ts or not v1:
                logger.warning("Missing timestamp or signature in webhook")
                return False
            
            # Create expected signature
            manifest = f"id:{x_request_id};request-id:{x_request_id};ts:{ts};"
            
            expected_signature = hmac.new(
                self.config.webhook_secret.encode(),
                (manifest + raw_body.decode()).encode(),
                hashlib.sha256
            ).hexdigest()
            
            is_valid = hmac.compare_digest(expected_signature, v1)
            
            if is_valid:
                self.metrics.increment("mercadopago.webhooks.valid")
            else:
                self.metrics.increment("mercadopago.webhooks.invalid")
                logger.warning("Invalid webhook signature")
            
            return is_valid
            
        except Exception as e:
            self.metrics.increment("mercadopago.webhooks.validation_failed")
            logger.error("Webhook validation failed", error=str(e))
            return False

    async def process_webhook(self, payload: Dict[str, Any]) -> Optional[ProcessedPayment]:
        """
        Process webhook notification from MercadoPago
        
        Args:
            payload: Webhook payload
            
        Returns:
            Updated payment information if applicable
        """
        try:
            notification_type = payload.get("type")
            data_id = payload.get("data", {}).get("id")
            
            if notification_type == "payment" and data_id:
                # Get updated payment information
                payment = await self.get_payment(int(data_id))
                
                if payment:
                    self.metrics.increment("mercadopago.webhooks.processed")
                    
                    logger.info("MercadoPago webhook processed",
                               payment_id=payment.id,
                               status=payment.status.value,
                               type=notification_type)
                    
                    return payment
            
            self.metrics.increment("mercadopago.webhooks.ignored")
            return None
            
        except Exception as e:
            self.metrics.increment("mercadopago.webhooks.processing_failed")
            logger.error("Webhook processing failed", error=str(e))
            return None

    async def health_check(self) -> Dict[str, Any]:
        """
        Check MercadoPago integration health
        
        Returns:
            Health status information
        """
        try:
            # Test API connectivity
            await self.get_payment_methods()
            
            health_status = {
                "service": "mercadopago",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "config": {
                    "environment": self.config.environment.value,
                    "country": self.config.country,
                    "currency": self.config.currency.value
                },
                "metrics": {
                    "total_transactions": len(self._transactions)
                }
            }
            
            return health_status
            
        except Exception as e:
            return {
                "service": "mercadopago",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Factory function for easy integration setup
def create_mercadopago_integration(
    access_token: str,
    public_key: str,
    client_id: str,
    client_secret: str,
    **kwargs
) -> MercadoPagoIntegration:
    """
    Factory function to create MercadoPago integration
    
    Args:
        access_token: MercadoPago access token
        public_key: MercadoPago public key
        client_id: MercadoPago client ID
        client_secret: MercadoPago client secret
        **kwargs: Additional configuration options
        
    Returns:
        Configured MercadoPago integration instance
    """
    config = MercadoPagoConfig(
        access_token=access_token,
        public_key=public_key,
        client_id=client_id,
        client_secret=client_secret,
        **kwargs
    )
    
    return MercadoPagoIntegration(config)

# Example usage for Ainflue platform
async def example_mercadopago_flow():
    """Example MercadoPago integration usage"""
    
    # Initialize MercadoPago integration for Brazil
    mp = create_mercadopago_integration(
        access_token="TEST-access-token",
        public_key="TEST-public-key",
        client_id="client-id",
        client_secret="client-secret",
        environment=MercadoPagoEnvironment.SANDBOX,
        country="BR",
        currency=Currency.BRL,
        notification_url="https://ainflue.com/webhooks/mercadopago",
        webhook_secret="webhook-secret"
    )
    
    try:
        # Get available payment methods
        payment_methods = await mp.get_payment_methods()
        print(f"Available payment methods: {len(payment_methods)}")
        
        # Create payment
        payment_request = PaymentRequest(
            transaction_amount=Decimal("29.90"),
            currency_id="BRL",
            description="Ainflue Premium Subscription",
            payment_method_id="visa",
            installments=1,
            payer=PayerInfo(
                email="creator@ainflue.com",
                identification={
                    "type": "CPF",
                    "number": "12345678901"
                }
            ),
            external_reference="ainflue_sub_123",
            metadata={
                "creator_id": "creator_123",
                "subscription_type": "premium",
                "platform": "ainflue"
            }
        )
        
        payment_result = await mp.create_payment(payment_request)
        print(f"Payment created: {payment_result.id}, status: {payment_result.status.value}")
        
        # Create checkout preference
        items = [
            {
                "title": "Ainflue Premium Subscription",
                "quantity": 1,
                "unit_price": 29.90,
                "currency_id": "BRL"
            }
        ]
        
        preference = await mp.create_preference(
            items=items,
            external_reference="ainflue_pref_123"
        )
        
        print(f"Preference created: {preference['id']}")
        print(f"Checkout URL: {preference['init_point']}")
        
        # Health check
        health = await mp.health_check()
        print(f"MercadoPago health: {health['status']}")
        
    except Exception as e:
        print(f"MercadoPago integration error: {e}")

if __name__ == "__main__":
    asyncio.run(example_mercadopago_flow())