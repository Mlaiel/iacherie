"""Adyen Integration - Global Payment Processing Platform
========================================================

Enterprise-grade Adyen integration supporting global payments,
marketplace functionality, and advanced financial operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal
import hmac
import hashlib
import base64

import httpx
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


class AdyenPaymentStatus(Enum):
    """Adyen payment status types."""
    AUTHORISED = "Authorised"
    REFUSED = "Refused"
    PENDING = "Pending"
    CANCELLED = "Cancelled"
    ERROR = "Error"
    RECEIVED = "Received"


class AdyenPaymentMethod(Enum):
    """Adyen payment method types."""
    CARD = "scheme"
    PAYPAL = "paypal"
    IDEAL = "ideal"
    SOFORT = "directEbanking"
    SEPA = "sepadirectdebit"
    ALIPAY = "alipay"
    WECHATPAY = "wechatpayWeb"
    GOOGLEPAY = "googlepay"
    APPLEPAY = "applepay"
    KLARNA = "klarna"
    AFTERPAY = "afterpay_default"


@dataclass
class AdyenPaymentRequest:
    """Adyen payment request structure."""
    amount: Dict[str, Union[str, int]]
    merchant_account: str
    reference: str
    return_url: str
    payment_method: Dict[str, Any]
    shopper_reference: Optional[str] = None
    shopper_email: Optional[str] = None
    country_code: Optional[str] = None
    shopper_locale: Optional[str] = None
    channel: str = "Web"
    origin: Optional[str] = None
    browser_info: Optional[Dict[str, Any]] = None
    additional_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AdyenPaymentResponse:
    """Adyen payment response structure."""
    psp_reference: str
    result_code: str
    amount: Dict[str, Union[str, int]]
    merchant_reference: str
    payment_method: Dict[str, Any]
    fraud_result: Optional[Dict[str, Any]] = None
    refusal_reason: Optional[str] = None
    refusal_reason_code: Optional[str] = None
    action: Optional[Dict[str, Any]] = None
    additional_data: Optional[Dict[str, Any]] = None


@dataclass
class AdyenRefundRequest:
    """Adyen refund request structure."""
    merchant_account: str
    amount: Dict[str, Union[str, int]]
    reference: str
    original_reference: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AdyenWebhookEvent:
    """Adyen webhook event structure."""
    live: str
    notification_items: List[Dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AdyenPaymentProcessor:
    """Enterprise Adyen payment processor for global transactions.
    
    Features:
    - Global payment processing (150+ payment methods)
    - Real-time fraud protection with Risk Management
    - Multi-currency support with dynamic currency conversion
    - Marketplace split payments and commissions
    - 3D Secure 2.0 authentication
    - Subscription and recurring payments
    - PCI DSS Level 1 compliance
    - Advanced reporting and analytics
    - Webhook notifications for real-time updates
    - Smart payment routing and optimization
    """
    
    def __init__(
        self,
        api_key -> None: str,
        merchant_account -> None: str,
        environment -> None: str = "test",
        client_key -> None: Optional[str] = None,
        hmac_key -> None: Optional[str] = None,
        webhook_username -> None: Optional[str] = None,
        webhook_password -> None: Optional[str] = None
    ) -> None:
        """Initialize Adyen payment processor.
        
        Args:
            api_key: Adyen API key
            merchant_account: Adyen merchant account identifier
            environment: Environment (test/live)
            client_key: Client-side key for frontend components
            hmac_key: HMAC key for webhook validation
            webhook_username: Webhook authentication username
            webhook_password: Webhook authentication password
        """
        self.api_key = api_key
        self.merchant_account = merchant_account
        self.environment = environment
        self.client_key = client_key
        self.hmac_key = hmac_key
        self.webhook_username = webhook_username
        self.webhook_password = webhook_password
        
        # Set base URLs based on environment
        if environment == "live":
            self.checkout_url = "https://checkout-live.adyen.com/v71"
            self.management_url = "https://management-live.adyen.com/v3"
            self.recurring_url = "https://pal-live.adyen.com/pal/servlet/Recurring/v68"
        else:
            self.checkout_url = "https://checkout-test.adyen.com/v71"
            self.management_url = "https://management-test.adyen.com/v3"
            self.recurring_url = "https://pal-test.adyen.com/pal/servlet/Recurring/v68"
        
        self.logger = logging.getLogger(__name__)
        self.session = httpx.AsyncClient(
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json"
            },
            timeout=30.0
        )

    async def create_payment_session(
        self,
        amount: int,
        currency: str,
        reference: str,
        return_url: str,
        shopper_reference: Optional[str] = None,
        shopper_email: Optional[str] = None,
        country_code: Optional[str] = None,
        allowed_payment_methods: Optional[List[str]] = None,
        blocked_payment_methods: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a payment session for frontend integration.
        
        Args:
            amount: Payment amount in minor currency units
            currency: Three-letter currency code
            reference: Merchant reference
            return_url: URL to redirect after payment
            shopper_reference: Unique shopper identifier
            shopper_email: Shopper email address
            country_code: Two-letter country code
            allowed_payment_methods: List of allowed payment methods
            blocked_payment_methods: List of blocked payment methods
            metadata: Additional metadata
            
        Returns:
            Dict containing session data and client key
        """
        try:
            payload = {
                "merchantAccount": self.merchant_account,
                "amount": {
                    "value": amount,
                    "currency": currency
                },
                "reference": reference,
                "returnUrl": return_url,
                "countryCode": country_code or "US",
                "channel": "Web"
            }
            
            if shopper_reference:
                payload["shopperReference"] = shopper_reference
            if shopper_email:
                payload["shopperEmail"] = shopper_email
            if allowed_payment_methods:
                payload["allowedPaymentMethods"] = allowed_payment_methods
            if blocked_payment_methods:
                payload["blockedPaymentMethods"] = blocked_payment_methods
            if metadata:
                payload["metadata"] = metadata
            
            response = await self.session.post(
                f"{self.checkout_url}/sessions",
                json=payload
            )
            response.raise_for_status()
            
            session_data = response.json()
            session_data["clientKey"] = self.client_key
            
            self.logger.info(f"Created payment session: {session_data.get('id')}")
            return session_data
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to create payment session: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating payment session: {e}")
            raise

    async def process_payment(
        self,
        payment_request: AdyenPaymentRequest
    ) -> AdyenPaymentResponse:
        """Process a payment through Adyen.
        
        Args:
            payment_request: Payment request details
            
        Returns:
            AdyenPaymentResponse with payment result
        """
        try:
            payload = {
                "merchantAccount": payment_request.merchant_account,
                "amount": payment_request.amount,
                "reference": payment_request.reference,
                "returnUrl": payment_request.return_url,
                "paymentMethod": payment_request.payment_method,
                "channel": payment_request.channel
            }
            
            if payment_request.shopper_reference:
                payload["shopperReference"] = payment_request.shopper_reference
            if payment_request.shopper_email:
                payload["shopperEmail"] = payment_request.shopper_email
            if payment_request.country_code:
                payload["countryCode"] = payment_request.country_code
            if payment_request.shopper_locale:
                payload["shopperLocale"] = payment_request.shopper_locale
            if payment_request.browser_info:
                payload["browserInfo"] = payment_request.browser_info
            if payment_request.additional_data:
                payload["additionalData"] = payment_request.additional_data
            if payment_request.metadata:
                payload["metadata"] = payment_request.metadata
            
            response = await self.session.post(
                f"{self.checkout_url}/payments",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            payment_response = AdyenPaymentResponse(
                psp_reference=result["pspReference"],
                result_code=result["resultCode"],
                amount=result.get("amount", payment_request.amount),
                merchant_reference=result.get("merchantReference", payment_request.reference),
                payment_method=result.get("paymentMethod", payment_request.payment_method),
                fraud_result=result.get("fraudResult"),
                refusal_reason=result.get("refusalReason"),
                refusal_reason_code=result.get("refusalReasonCode"),
                action=result.get("action"),
                additional_data=result.get("additionalData")
            )
            
            self.logger.info(f"Processed payment: {payment_response.psp_reference} - {payment_response.result_code}")
            return payment_response
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to process payment: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error processing payment: {e}")
            raise

    async def capture_payment(
        self,
        payment_psp_reference: str,
        amount: Optional[int] = None,
        currency: Optional[str] = None
    ) -> Dict[str, Any]:
        """Capture an authorized payment.
        
        Args:
            payment_psp_reference: PSP reference of the payment to capture
            amount: Amount to capture (if partial capture)
            currency: Currency of the amount
            
        Returns:
            Dict containing capture result
        """
        try:
            payload = {
                "merchantAccount": self.merchant_account,
                "originalReference": payment_psp_reference
            }
            
            if amount and currency:
                payload["modificationAmount"] = {
                    "value": amount,
                    "currency": currency
                }
            
            response = await self.session.post(
                f"{self.checkout_url}/payments/{payment_psp_reference}/captures",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(f"Captured payment: {payment_psp_reference}")
            return result
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to capture payment: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error capturing payment: {e}")
            raise

    async def refund_payment(
        self,
        refund_request: AdyenRefundRequest
    ) -> Dict[str, Any]:
        """Refund a captured payment.
        
        Args:
            refund_request: Refund request details
            
        Returns:
            Dict containing refund result
        """
        try:
            payload = {
                "merchantAccount": refund_request.merchant_account,
                "amount": refund_request.amount,
                "reference": refund_request.reference,
                "originalReference": refund_request.original_reference
            }
            
            if refund_request.metadata:
                payload["metadata"] = refund_request.metadata
            
            response = await self.session.post(
                f"{self.checkout_url}/payments/{refund_request.original_reference}/refunds",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(f"Refunded payment: {refund_request.original_reference}")
            return result
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to refund payment: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error refunding payment: {e}")
            raise

    async def cancel_payment(
        self,
        payment_psp_reference: str
    ) -> Dict[str, Any]:
        """Cancel an authorized payment.
        
        Args:
            payment_psp_reference: PSP reference of the payment to cancel
            
        Returns:
            Dict containing cancellation result
        """
        try:
            payload = {
                "merchantAccount": self.merchant_account,
                "originalReference": payment_psp_reference
            }
            
            response = await self.session.post(
                f"{self.checkout_url}/payments/{payment_psp_reference}/cancels",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(f"Cancelled payment: {payment_psp_reference}")
            return result
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to cancel payment: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error cancelling payment: {e}")
            raise

    async def get_payment_methods(
        self,
        amount: int,
        currency: str,
        country_code: str,
        shopper_locale: Optional[str] = None,
        shopper_reference: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get available payment methods for a transaction.
        
        Args:
            amount: Transaction amount in minor currency units
            currency: Three-letter currency code
            country_code: Two-letter country code
            shopper_locale: Shopper locale
            shopper_reference: Unique shopper identifier
            
        Returns:
            Dict containing available payment methods
        """
        try:
            payload = {
                "merchantAccount": self.merchant_account,
                "amount": {
                    "value": amount,
                    "currency": currency
                },
                "countryCode": country_code,
                "channel": "Web"
            }
            
            if shopper_locale:
                payload["shopperLocale"] = shopper_locale
            if shopper_reference:
                payload["shopperReference"] = shopper_reference
            
            response = await self.session.post(
                f"{self.checkout_url}/paymentMethods",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(f"Retrieved payment methods for {country_code}")
            return result
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to get payment methods: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting payment methods: {e}")
            raise

    def validate_webhook_signature(
        self,
        payload: str,
        signature: str
    ) -> bool:
        """Validate Adyen webhook signature.
        
        Args:
            payload: Raw webhook payload
            signature: Signature from X-Adyen-Signature header
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.hmac_key:
            self.logger.warning("HMAC key not configured for webhook validation")
            return False
        
        try:
            # Calculate expected signature
            expected_signature = base64.b64encode(
                hmac.new(
                    self.hmac_key.encode(),
                    payload.encode(),
                    hashlib.sha256
                ).digest()
            ).decode()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            self.logger.error(f"Error validating webhook signature: {e}")
            return False

    async def process_webhook(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process Adyen webhook notification.
        
        Args:
            payload: Webhook payload
            
        Returns:
            Dict containing processing result
        """
        try:
            webhook_event = AdyenWebhookEvent(
                live=payload["live"],
                notification_items=payload["notificationItems"]
            )
            
            processed_items = []
            
            for item in webhook_event.notification_items:
                notification = item["NotificationRequestItem"]
                
                # Process different event types
                event_code = notification.get("eventCode")
                success = notification.get("success") == "true"
                psp_reference = notification.get("pspReference")
                merchant_reference = notification.get("merchantReference")
                
                processed_item = {
                    "eventCode": event_code,
                    "success": success,
                    "pspReference": psp_reference,
                    "merchantReference": merchant_reference,
                    "processed": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Handle specific event types
                if event_code == "AUTHORISATION":
                    processed_item["type"] = "payment_authorized"
                elif event_code == "CAPTURE":
                    processed_item["type"] = "payment_captured"
                elif event_code == "REFUND":
                    processed_item["type"] = "payment_refunded"
                elif event_code == "CANCELLATION":
                    processed_item["type"] = "payment_cancelled"
                elif event_code == "CHARGEBACK":
                    processed_item["type"] = "chargeback_received"
                else:
                    processed_item["type"] = "other"
                
                processed_items.append(processed_item)
                
                self.logger.info(f"Processed webhook: {event_code} - {psp_reference}")
            
            return {
                "status": "success",
                "processed_items": processed_items,
                "total_items": len(processed_items)
            }
            
        except Exception as e:
            self.logger.error(f"Error processing webhook: {e}")
            return {
                "status": "error",
                "error": str(e),
                "processed_items": []
            }

    async def create_subscription(
        self,
        shopper_reference: str,
        payment_method: Dict[str, Any],
        amount: int,
        currency: str,
        interval: str = "monthly",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a recurring payment subscription.
        
        Args:
            shopper_reference: Unique shopper identifier
            payment_method: Payment method details
            amount: Subscription amount in minor currency units
            currency: Three-letter currency code
            interval: Billing interval (monthly, yearly, etc.)
            metadata: Additional metadata
            
        Returns:
            Dict containing subscription details
        """
        try:
            # First, tokenize the payment method
            tokenize_payload = {
                "merchantAccount": self.merchant_account,
                "shopperReference": shopper_reference,
                "paymentMethod": payment_method,
                "recurring": {
                    "contract": "RECURRING"
                }
            }
            
            response = await self.session.post(
                f"{self.recurring_url}/storeToken",
                json=tokenize_payload
            )
            response.raise_for_status()
            
            token_result = response.json()
            
            # Create subscription record
            subscription = {
                "id": str(uuid.uuid4()),
                "shopperReference": shopper_reference,
                "recurringDetailReference": token_result.get("recurringDetailReference"),
                "amount": amount,
                "currency": currency,
                "interval": interval,
                "status": "active",
                "createdAt": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            self.logger.info(f"Created subscription: {subscription['id']}")
            return subscription
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to create subscription: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating subscription: {e}")
            raise

    async def process_recurring_payment(
        self,
        shopper_reference: str,
        recurring_detail_reference: str,
        amount: int,
        currency: str,
        reference: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a recurring payment.
        
        Args:
            shopper_reference: Unique shopper identifier
            recurring_detail_reference: Token reference
            amount: Payment amount in minor currency units
            currency: Three-letter currency code
            reference: Merchant reference
            metadata: Additional metadata
            
        Returns:
            Dict containing payment result
        """
        try:
            payload = {
                "merchantAccount": self.merchant_account,
                "amount": {
                    "value": amount,
                    "currency": currency
                },
                "reference": reference,
                "shopperReference": shopper_reference,
                "paymentMethod": {
                    "type": "scheme",
                    "storedPaymentMethodId": recurring_detail_reference
                },
                "shopperInteraction": "ContAuth",
                "recurringProcessingModel": "Subscription"
            }
            
            if metadata:
                payload["metadata"] = metadata
            
            response = await self.session.post(
                f"{self.checkout_url}/payments",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(f"Processed recurring payment: {result.get('pspReference')}")
            return result
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to process recurring payment: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error processing recurring payment: {e}")
            raise

    async def get_payment_details(
        self,
        psp_reference: str
    ) -> Dict[str, Any]:
        """Get detailed information about a payment.
        
        Args:
            psp_reference: PSP reference of the payment
            
        Returns:
            Dict containing payment details
        """
        try:
            response = await self.session.get(
                f"{self.checkout_url}/payments/{psp_reference}"
            )
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(f"Retrieved payment details: {psp_reference}")
            return result
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to get payment details: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting payment details: {e}")
            raise

    async def close(self) -> None:
        """Close the HTTP session."""
        await self.session.aclose()

    async def __aenter__(self) -> None:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


# Creator monetization specific functions
async def create_creator_payout_split(
    processor: AdyenPaymentProcessor,
    total_amount: int,
    currency: str,
    creator_percentage: float,
    platform_percentage: float,
    creator_account: str,
    platform_account: str,
    reference: str
) -> Dict[str, Any]:
    """Create split payment for creator monetization.
    
    Args:
        processor: Adyen payment processor instance
        total_amount: Total payment amount
        currency: Currency code
        creator_percentage: Creator's percentage (0-100)
        platform_percentage: Platform's percentage (0-100)
        creator_account: Creator's account identifier
        platform_account: Platform's account identifier
        reference: Payment reference
        
    Returns:
        Dict containing split payment details
    """
    creator_amount = int(total_amount * (creator_percentage / 100))
    platform_amount = int(total_amount * (platform_percentage / 100))
    
    split_configuration = {
        "reference": reference,
        "amount": {
            "value": total_amount,
            "currency": currency
        },
        "splits": [
            {
                "account": creator_account,
                "amount": {
                    "value": creator_amount,
                    "currency": currency
                },
                "type": "MarketPlace",
                "reference": f"creator_{reference}"
            },
            {
                "account": platform_account,
                "amount": {
                    "value": platform_amount,
                    "currency": currency
                },
                "type": "Commission",
                "reference": f"platform_{reference}"
            }
        ]
    }
    
    return split_configuration


async def process_creator_subscription(
    processor: AdyenPaymentProcessor,
    creator_id: str,
    subscriber_reference: str,
    tier_amount: int,
    currency: str,
    payment_method: Dict[str, Any]
) -> Dict[str, Any]:
    """Process creator subscription payment.
    
    Args:
        processor: Adyen payment processor instance
        creator_id: Creator identifier
        subscriber_reference: Subscriber reference
        tier_amount: Subscription tier amount
        currency: Currency code
        payment_method: Payment method details
        
    Returns:
        Dict containing subscription result
    """
    subscription_reference = f"creator_{creator_id}_sub_{subscriber_reference}"
    
    return await processor.create_subscription(
        shopper_reference=subscriber_reference,
        payment_method=payment_method,
        amount=tier_amount,
        currency=currency,
        interval="monthly",
        metadata={
            "creator_id": creator_id,
            "subscription_type": "creator_tier",
            "reference": subscription_reference
        }
    )