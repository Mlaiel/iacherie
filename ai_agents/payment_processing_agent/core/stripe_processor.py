"""Stripe Payment Processor - Industrial Stripe Integration

Complete Stripe payment processor implementation with advanced features,
error handling, webhook processing, and comprehensive payment method support.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""import asyncio
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
import aiohttp

from .base_processor import BaseProcessor, PaymentResult, PayoutResult, BalanceResult
from ..exceptions import PaymentProcessingError, InvalidPaymentMethodError

logger = logging.getLogger(__name__)


class StripeProcessor(BaseProcessor):
    """    Advanced Stripe payment processor for creators and influencers.
    
    Supports payments, payouts, Connect accounts, marketplace functionality,
    and comprehensive webhook handling for the IA Influencer platform.
    """    
    def __init__(
        self,
        api_key: str,
        webhook_secret: Optional[str] = None,
        environment: str = "production",
        connect_enabled: bool = True,
        **kwargs
    ):
        """        Initialize Stripe processor with advanced configuration.
        
        Args:
            api_key: Stripe secret key
            webhook_secret: Webhook endpoint secret
            environment: Environment (production, test)
            connect_enabled: Enable Stripe Connect for payouts
        """        super().__init__(
            name="stripe",
            api_key=api_key,
            environment=environment,
            **kwargs
        )
        
        self.webhook_secret = webhook_secret
        self.connect_enabled = connect_enabled
        
        # Stripe API configuration
        self.base_url = "https://api.stripe.com/v1"
        self.api_version = "2023-10-16"
        
        # Initialize session
        self.session = None
        
    def _initialize(self):
        """Initialize Stripe-specific configuration."""        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Stripe-Version": self.api_version,
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "IA-Influencer-Agent/1.0.0"
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=timeout
            )
        return self.session
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Stripe API."""        session = await self._get_session()
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with session.get(url, params=params) as response:
                    result = await response.json()
            else:
                # Convert data to form-encoded format for Stripe
                form_data = aiohttp.FormData()
                if data:
                    self._flatten_data(form_data, data)
                
                async with session.post(url, data=form_data) as response:
                    result = await response.json()
            
            if response.status >= 400:
                error_msg = result.get("error", {}).get("message", "Unknown error")
                error_code = result.get("error", {}).get("code", "unknown")
                raise PaymentProcessingError(f"Stripe API error: {error_msg} ({error_code})")
            
            self._update_metrics(success=True)
            return result
            
        except aiohttp.ClientError as e:
            self._update_metrics(success=False)
            raise PaymentProcessingError(f"Stripe request failed: {str(e)}")
    
    def _flatten_data(self, form_data: aiohttp.FormData, data: Dict[str, Any], prefix: str = ""):
        """Flatten nested data for Stripe API form encoding."""        for key, value in data.items():
            full_key = f"{prefix}[{key}]" if prefix else key
            
            if isinstance(value, dict):
                self._flatten_data(form_data, value, full_key)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._flatten_data(form_data, item, f"{full_key}[{i}]")
                    else:
                        form_data.add_field(f"{full_key}[{i}]", str(item))
            else:
                form_data.add_field(full_key, str(value))
    
    async def process_payment(
        self,
        amount: Union[Decimal, float],
        currency: str,
        payment_method: str,
        customer_id: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentResult:
        """        Process payment through Stripe.
        
        Args:
            amount: Payment amount
            currency: Currency code
            payment_method: Stripe payment method ID
            customer_id: Stripe customer ID
            description: Payment description
            metadata: Additional metadata
            
        Returns:
            PaymentResult with Stripe payment details
        """        try:
            # Convert amount to cents (Stripe requirement)
            amount_cents = int(Decimal(str(amount)) * 100)
            
            # Prepare payment data
            payment_data = {
                "amount": amount_cents,
                "currency": currency.lower(),
                "payment_method": payment_method,
                "customer": customer_id,
                "confirmation_method": "automatic",
                "confirm": True,
                "return_url": "https://ia-influencer.com/payment/return"
            }
            
            if description:
                payment_data["description"] = description
                
            if metadata:
                payment_data["metadata"] = metadata
            
            # Create payment intent
            result = await self._make_request("POST", "payment_intents", payment_data)
            
            # Parse result
            success = result.get("status") in ["succeeded", "processing"]
            
            return PaymentResult(
                success=success,
                transaction_id=result.get("id"),
                external_id=result.get("id"),
                amount=Decimal(str(amount)),
                currency=currency,
                status=result.get("status", "unknown"),
                fees=self._calculate_stripe_fees(amount_cents, currency),
                metadata={
                    "stripe_payment_intent": result.get("id"),
                    "client_secret": result.get("client_secret"),
                    "payment_method_type": result.get("payment_method", {}).get("type"),
                    "created": result.get("created")
                }
            )
            
        except Exception as e:
            logger.error(f"Stripe payment processing failed: {str(e)}")
            return PaymentResult(
                success=False,
                error_message=str(e)
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
        """        Execute payout through Stripe Connect.
        
        Args:
            amount: Payout amount
            currency: Currency code
            payment_method: Bank account or debit card ID
            recipient_id: Stripe Connect account ID
            description: Payout description
            metadata: Additional metadata
            
        Returns:
            PayoutResult with payout details
        """        try:
            if not self.connect_enabled:
                raise PaymentProcessingError("Stripe Connect not enabled for payouts")
            
            # Convert amount to cents
            amount_cents = int(Decimal(str(amount)) * 100)
            
            # Prepare payout data
            payout_data = {
                "amount": amount_cents,
                "currency": currency.lower(),
                "method": "instant" if payment_method.startswith("card_") else "standard"
            }
            
            if description:
                payout_data["statement_descriptor"] = description[:22]  # Stripe limit
                
            if metadata:
                payout_data["metadata"] = metadata
            
            # Execute payout to connected account
            headers = self.headers.copy()
            headers["Stripe-Account"] = recipient_id
            
            session = await self._get_session()
            url = f"{self.base_url}/payouts"
            
            form_data = aiohttp.FormData()
            self._flatten_data(form_data, payout_data)
            
            async with session.post(url, data=form_data, headers=headers) as response:
                result = await response.json()
            
            if response.status >= 400:
                error_msg = result.get("error", {}).get("message", "Payout failed")
                raise PaymentProcessingError(f"Stripe payout error: {error_msg}")
            
            # Estimate arrival time
            estimated_arrival = None
            if result.get("arrival_date"):
                estimated_arrival = datetime.fromtimestamp(result["arrival_date"])
            
            return PayoutResult(
                success=True,
                payout_id=result.get("id"),
                external_id=result.get("id"),
                amount=Decimal(str(amount)),
                currency=currency,
                status=result.get("status", "unknown"),
                estimated_arrival=estimated_arrival,
                fees=self._calculate_payout_fees(amount_cents, currency),
                metadata={
                    "stripe_payout_id": result.get("id"),
                    "method": result.get("method"),
                    "type": result.get("type"),
                    "created": result.get("created")
                }
            )
            
        except Exception as e:
            logger.error(f"Stripe payout failed: {str(e)}")
            return PayoutResult(
                success=False,
                error_message=str(e)
            )
    
    async def get_balance(self, currency: str = "eur") -> BalanceResult:
        """        Get Stripe account balance.
        
        Args:
            currency: Currency code
            
        Returns:
            BalanceResult with balance information
        """        try:
            result = await self._make_request("GET", "balance")
            
            # Find balance for specified currency
            available = Decimal("0.00")
            pending = Decimal("0.00")
            
            for balance_item in result.get("available", []):
                if balance_item.get("currency") == currency.lower():
                    available = Decimal(str(balance_item.get("amount", 0))) / 100
                    break
            
            for balance_item in result.get("pending", []):
                if balance_item.get("currency") == currency.lower():
                    pending = Decimal(str(balance_item.get("amount", 0))) / 100
                    break
            
            return BalanceResult(
                available=available,
                pending=pending,
                currency=currency.upper(),
                last_updated=datetime.utcnow(),
                metadata={
                    "stripe_balance": result,
                    "connect_reserved": result.get("connect_reserved", [])
                }
            )
            
        except Exception as e:
            logger.error(f"Stripe balance lookup failed: {str(e)}")
            raise PaymentProcessingError(f"Failed to get balance: {str(e)}")
    
    async def verify_webhook(
        self,
        payload: str,
        signature: str,
        secret: Optional[str] = None
    ) -> bool:
        """        Verify Stripe webhook signature.
        
        Args:
            payload: Raw webhook payload
            signature: Stripe signature header
            secret: Webhook secret (uses instance secret if None)
            
        Returns:
            True if signature is valid
        """        try:
            webhook_secret = secret or self.webhook_secret
            if not webhook_secret:
                raise ValueError("Webhook secret not configured")
            
            # Parse signature header
            sig_parts = dict(part.split("=") for part in signature.split(","))
            timestamp = sig_parts.get("t")
            v1_signature = sig_parts.get("v1")
            
            if not timestamp or not v1_signature:
                return False
            
            # Create expected signature
            signed_payload = f"{timestamp}.{payload}"
            expected_signature = hmac.new(
                webhook_secret.encode(),
                signed_payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Verify signature
            return hmac.compare_digest(v1_signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Stripe webhook verification failed: {str(e)}")
            return False
    
    async def parse_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """        Parse Stripe webhook into standard format.
        
        Args:
            payload: Stripe webhook payload
            
        Returns:
            Standardized webhook data
        """        event_type = payload.get("type", "")
        event_data = payload.get("data", {}).get("object", {})
        
        # Map Stripe events to standard events
        event_mapping = {
            "payment_intent.succeeded": "payment_completed",
            "payment_intent.payment_failed": "payment_failed",
            "payout.created": "payout_created",
            "payout.paid": "payout_completed",
            "payout.failed": "payout_failed",
            "invoice.payment_succeeded": "subscription_payment",
            "customer.subscription.created": "subscription_created"
        }
        
        standard_event = event_mapping.get(event_type, event_type)
        
        return {
            "event_id": payload.get("id"),
            "event_type": standard_event,
            "original_type": event_type,
            "processor": "stripe",
            "created": datetime.fromtimestamp(payload.get("created", 0)),
            "livemode": payload.get("livemode", False),
            "data": event_data,
            "metadata": {
                "api_version": payload.get("api_version"),
                "request_id": payload.get("request", {}).get("id")
            }
        }
    
    async def create_connect_account(
        self,
        email: str,
        country: str,
        account_type: str = "express",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Create Stripe Connect account for creator payouts.
        
        Args:
            email: Creator email address
            country: Creator country code
            account_type: Account type (express, standard, custom)
            metadata: Additional metadata
            
        Returns:
            Created account details
        """        try:
            account_data = {
                "type": account_type,
                "email": email,
                "country": country.upper(),
                "capabilities": {
                    "transfers": {"requested": True}
                }
            }
            
            if metadata:
                account_data["metadata"] = metadata
            
            result = await self._make_request("POST", "accounts", account_data)
            
            return {
                "account_id": result.get("id"),
                "type": result.get("type"),
                "email": result.get("email"),
                "country": result.get("country"),
                "charges_enabled": result.get("charges_enabled"),
                "payouts_enabled": result.get("payouts_enabled"),
                "onboarding_url": None,  # Will be created separately
                "metadata": result.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Stripe Connect account creation failed: {str(e)}")
            raise PaymentProcessingError(f"Failed to create Connect account: {str(e)}")
    
    async def create_account_link(
        self,
        account_id: str,
        refresh_url: str,
        return_url: str,
        link_type: str = "account_onboarding"
    ) -> str:
        """        Create account link for Connect onboarding.
        
        Args:
            account_id: Connect account ID
            refresh_url: URL to refresh if expired
            return_url: URL to return after onboarding
            link_type: Link type (account_onboarding, account_update)
            
        Returns:
            Account link URL
        """        try:
            link_data = {
                "account": account_id,
                "refresh_url": refresh_url,
                "return_url": return_url,
                "type": link_type
            }
            
            result = await self._make_request("POST", "account_links", link_data)
            
            return result.get("url")
            
        except Exception as e:
            logger.error(f"Stripe account link creation failed: {str(e)}")
            raise PaymentProcessingError(f"Failed to create account link: {str(e)}")
    
    def _calculate_stripe_fees(self, amount_cents: int, currency: str) -> Decimal:
        """Calculate Stripe processing fees."""        # Standard Stripe fees: 2.9% + €0.30 for European cards
        percentage_fee = Decimal(str(amount_cents)) * Decimal("0.029") / 100
        fixed_fee = Decimal("0.30")
        
        return (percentage_fee + fixed_fee).quantize(Decimal("0.01"))
    
    def _calculate_payout_fees(self, amount_cents: int, currency: str) -> Decimal:
        """Calculate Stripe payout fees."""        # Instant payouts: 1% for debit cards, standard payouts are free
        return Decimal("0.00")  # Assuming standard payouts
    
    async def get_supported_currencies(self) -> List[str]:
        """Get Stripe supported currencies."""        return [
            "EUR", "USD", "GBP", "CHF", "SEK", "NOK", "DKK",
            "CAD", "AUD", "JPY", "PLN", "CZK", "HUF"
        ]
    
    async def get_supported_countries(self) -> List[str]:
        """Get Stripe supported countries."""        return [
            "AD", "AE", "AT", "AU", "BE", "BG", "BR", "CA", "CH", "CY",
            "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GB", "GR", "HK",
            "HR", "HU", "IE", "IN", "IT", "JP", "LI", "LT", "LU", "LV",
            "MT", "MX", "NL", "NO", "NZ", "PL", "PT", "RO", "SE", "SG",
            "SI", "SK", "TH", "US"
        ]
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close HTTP session on exit."""        if self.session and not self.session.closed:
            await self.session.close()
