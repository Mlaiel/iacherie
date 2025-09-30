"""Stripe Connect Integration - Multi-Party Payment Processing
===========================================================

Professional Stripe Connect integration for marketplace payments,
multi-party transactions, and platform revenue splitting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
import json
import aiohttp
import hashlib
import hmac

logger = logging.getLogger(__name__)


class AccountType(str, Enum):
    """Stripe Connect account types."""
    STANDARD = "standard"
    EXPRESS = "express" 
    CUSTOM = "custom"


class AccountStatus(str, Enum):
    """Account verification status."""
    PENDING = "pending"
    ENABLED = "enabled"
    REJECTED = "rejected"
    RESTRICTED = "restricted"


class TransferStatus(str, Enum):
    """Transfer status."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELED = "canceled"


class PayoutStatus(str, Enum):
    """Payout status."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELED = "canceled"


@dataclass
class ConnectedAccount:
    """Stripe Connected Account."""
    account_id: str
    type: AccountType
    status: AccountStatus
    email: str
    business_profile: Dict[str, Any]
    capabilities: Dict[str, str]
    requirements: Dict[str, Any]
    payouts_enabled: bool
    charges_enabled: bool
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class PaymentIntent:
    """Stripe Payment Intent with Connect."""
    intent_id: str
    amount: int
    currency: str
    status: str
    application_fee_amount: Optional[int]
    on_behalf_of: Optional[str]
    transfer_data: Optional[Dict[str, Any]]
    client_secret: str
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class Transfer:
    """Stripe Transfer."""
    transfer_id: str
    amount: int
    currency: str
    destination: str
    status: TransferStatus
    description: Optional[str]
    source_transaction: Optional[str]
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class Payout:
    """Stripe Payout."""
    payout_id: str
    amount: int
    currency: str
    destination: str
    status: PayoutStatus
    arrival_date: datetime
    description: Optional[str]
    created_at: datetime
    metadata: Dict[str, Any]


class StripeConnectIntegration:
    """Professional Stripe Connect integration."""
    
    def __init__(
        self,
        secret_key: str,
        publishable_key: str,
        webhook_secret: Optional[str] = None,
        base_url: str = "https://api.stripe.com/v1",
        timeout: int = 30
    ):
        self.secret_key = secret_key
        self.publishable_key = publishable_key
        self.webhook_secret = webhook_secret
        self.base_url = base_url
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Usage tracking
        self.transaction_count = 0
        self.total_volume = Decimal('0')
        self.fee_collected = Decimal('0')
        self.request_count = 0
        
        logger.info("Stripe Connect integration initialized")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if self.session is None or self.session.closed:
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Ainflue/1.0",
                "Stripe-Version": "2023-10-16"
            }
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
    
    async def close(self):
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def create_account(
        self,
        account_type: AccountType,
        email: str,
        country: str,
        business_type: str = "individual",
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConnectedAccount:
        """Create a new connected account."""
        await self._ensure_session()
        
        data = {
            "type": account_type.value,
            "email": email,
            "country": country,
            "business_type": business_type
        }
        
        if metadata:
            for key, value in metadata.items():
                data[f"metadata[{key}]"] = str(value)
        
        try:
            async with self.session.post(
                f"{self.base_url}/accounts",
                data=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Stripe Connect account creation error: {error_data}")
                
                result = await response.json()
                
                account = ConnectedAccount(
                    account_id=result["id"],
                    type=AccountType(result["type"]),
                    status=AccountStatus(result.get("status", "pending")),
                    email=result["email"],
                    business_profile=result.get("business_profile", {}),
                    capabilities=result.get("capabilities", {}),
                    requirements=result.get("requirements", {}),
                    payouts_enabled=result.get("payouts_enabled", False),
                    charges_enabled=result.get("charges_enabled", False),
                    created_at=datetime.fromtimestamp(result["created"]),
                    metadata=result.get("metadata", {})
                )
                
                self.request_count += 1
                logger.info(f"Connected account created: {account.account_id}")
                return account
        
        except Exception as e:
            logger.error(f"Account creation failed: {e}")
            raise
    
    async def get_account(self, account_id: str) -> ConnectedAccount:
        """Get connected account details."""
        await self._ensure_session()
        
        try:
            async with self.session.get(f"{self.base_url}/accounts/{account_id}") as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Stripe Connect account retrieval error: {error_data}")
                
                result = await response.json()
                
                account = ConnectedAccount(
                    account_id=result["id"],
                    type=AccountType(result["type"]),
                    status=AccountStatus(result.get("status", "pending")),
                    email=result["email"],
                    business_profile=result.get("business_profile", {}),
                    capabilities=result.get("capabilities", {}),
                    requirements=result.get("requirements", {}),
                    payouts_enabled=result.get("payouts_enabled", False),
                    charges_enabled=result.get("charges_enabled", False),
                    created_at=datetime.fromtimestamp(result["created"]),
                    metadata=result.get("metadata", {})
                )
                
                self.request_count += 1
                return account
        
        except Exception as e:
            logger.error(f"Account retrieval failed: {e}")
            raise
    
    async def create_account_link(
        self,
        account_id: str,
        refresh_url: str,
        return_url: str,
        type: str = "account_onboarding"
    ) -> str:
        """Create account link for onboarding."""
        await self._ensure_session()
        
        data = {
            "account": account_id,
            "refresh_url": refresh_url,
            "return_url": return_url,
            "type": type
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/account_links",
                data=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Stripe Connect link creation error: {error_data}")
                
                result = await response.json()
                
                self.request_count += 1
                logger.info(f"Account link created for: {account_id}")
                return result["url"]
        
        except Exception as e:
            logger.error(f"Account link creation failed: {e}")
            raise
    
    async def create_payment_intent(
        self,
        amount: int,
        currency: str,
        connected_account_id: str,
        application_fee_amount: Optional[int] = None,
        transfer_data: Optional[Dict[str, Any]] = None,
        on_behalf_of: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentIntent:
        """Create payment intent with Connect."""
        await self._ensure_session()
        
        data = {
            "amount": amount,
            "currency": currency,
            "automatic_payment_methods[enabled]": "true"
        }
        
        if application_fee_amount:
            data["application_fee_amount"] = application_fee_amount
        
        if on_behalf_of:
            data["on_behalf_of"] = on_behalf_of
        
        if transfer_data:
            for key, value in transfer_data.items():
                data[f"transfer_data[{key}]"] = str(value)
        
        if metadata:
            for key, value in metadata.items():
                data[f"metadata[{key}]"] = str(value)
        
        # Set connected account header
        headers = {"Stripe-Account": connected_account_id}
        
        try:
            async with self.session.post(
                f"{self.base_url}/payment_intents",
                data=data,
                headers=headers
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Stripe Connect payment intent error: {error_data}")
                
                result = await response.json()
                
                payment_intent = PaymentIntent(
                    intent_id=result["id"],
                    amount=result["amount"],
                    currency=result["currency"],
                    status=result["status"],
                    application_fee_amount=result.get("application_fee_amount"),
                    on_behalf_of=result.get("on_behalf_of"),
                    transfer_data=result.get("transfer_data"),
                    client_secret=result["client_secret"],
                    created_at=datetime.fromtimestamp(result["created"]),
                    metadata=result.get("metadata", {})
                )
                
                self.request_count += 1
                self.transaction_count += 1
                self.total_volume += Decimal(str(amount)) / 100
                
                if application_fee_amount:
                    self.fee_collected += Decimal(str(application_fee_amount)) / 100
                
                logger.info(f"Payment intent created: {payment_intent.intent_id}")
                return payment_intent
        
        except Exception as e:
            logger.error(f"Payment intent creation failed: {e}")
            raise
    
    async def create_transfer(
        self,
        amount: int,
        currency: str,
        destination_account: str,
        description: Optional[str] = None,
        source_transaction: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Transfer:
        """Create transfer to connected account."""
        await self._ensure_session()
        
        data = {
            "amount": amount,
            "currency": currency,
            "destination": destination_account
        }
        
        if description:
            data["description"] = description
        
        if source_transaction:
            data["source_transaction"] = source_transaction
        
        if metadata:
            for key, value in metadata.items():
                data[f"metadata[{key}]"] = str(value)
        
        try:
            async with self.session.post(
                f"{self.base_url}/transfers",
                data=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Stripe Connect transfer error: {error_data}")
                
                result = await response.json()
                
                transfer = Transfer(
                    transfer_id=result["id"],
                    amount=result["amount"],
                    currency=result["currency"],
                    destination=result["destination"],
                    status=TransferStatus(result.get("status", "pending")),
                    description=result.get("description"),
                    source_transaction=result.get("source_transaction"),
                    created_at=datetime.fromtimestamp(result["created"]),
                    metadata=result.get("metadata", {})
                )
                
                self.request_count += 1
                logger.info(f"Transfer created: {transfer.transfer_id}")
                return transfer
        
        except Exception as e:
            logger.error(f"Transfer creation failed: {e}")
            raise
    
    async def list_accounts(
        self,
        limit: int = 10,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None
    ) -> List[ConnectedAccount]:
        """List connected accounts."""
        await self._ensure_session()
        
        params = {"limit": limit}
        
        if created_after:
            params["created[gte]"] = int(created_after.timestamp())
        
        if created_before:
            params["created[lte]"] = int(created_before.timestamp())
        
        try:
            async with self.session.get(
                f"{self.base_url}/accounts",
                params=params
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Stripe Connect accounts list error: {error_data}")
                
                result = await response.json()
                accounts = []
                
                for account_data in result["data"]:
                    account = ConnectedAccount(
                        account_id=account_data["id"],
                        type=AccountType(account_data["type"]),
                        status=AccountStatus(account_data.get("status", "pending")),
                        email=account_data["email"],
                        business_profile=account_data.get("business_profile", {}),
                        capabilities=account_data.get("capabilities", {}),
                        requirements=account_data.get("requirements", {}),
                        payouts_enabled=account_data.get("payouts_enabled", False),
                        charges_enabled=account_data.get("charges_enabled", False),
                        created_at=datetime.fromtimestamp(account_data["created"]),
                        metadata=account_data.get("metadata", {})
                    )
                    accounts.append(account)
                
                self.request_count += 1
                logger.info(f"Retrieved {len(accounts)} accounts")
                return accounts
        
        except Exception as e:
            logger.error(f"Accounts listing failed: {e}")
            raise
    
    async def get_balance(self, account_id: str) -> Dict[str, Any]:
        """Get account balance."""
        await self._ensure_session()
        
        headers = {"Stripe-Account": account_id}
        
        try:
            async with self.session.get(
                f"{self.base_url}/balance",
                headers=headers
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Stripe Connect balance error: {error_data}")
                
                result = await response.json()
                
                self.request_count += 1
                logger.info(f"Balance retrieved for account: {account_id}")
                return result
        
        except Exception as e:
            logger.error(f"Balance retrieval failed: {e}")
            raise
    
    async def create_payout(
        self,
        amount: int,
        currency: str,
        account_id: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Payout:
        """Create payout for connected account."""
        await self._ensure_session()
        
        data = {
            "amount": amount,
            "currency": currency
        }
        
        if description:
            data["description"] = description
        
        if metadata:
            for key, value in metadata.items():
                data[f"metadata[{key}]"] = str(value)
        
        headers = {"Stripe-Account": account_id}
        
        try:
            async with self.session.post(
                f"{self.base_url}/payouts",
                data=data,
                headers=headers
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Stripe Connect payout error: {error_data}")
                
                result = await response.json()
                
                payout = Payout(
                    payout_id=result["id"],
                    amount=result["amount"],
                    currency=result["currency"],
                    destination=result["destination"],
                    status=PayoutStatus(result.get("status", "pending")),
                    arrival_date=datetime.fromtimestamp(result["arrival_date"]),
                    description=result.get("description"),
                    created_at=datetime.fromtimestamp(result["created"]),
                    metadata=result.get("metadata", {})
                )
                
                self.request_count += 1
                logger.info(f"Payout created: {payout.payout_id}")
                return payout
        
        except Exception as e:
            logger.error(f"Payout creation failed: {e}")
            raise
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature_header: str,
        tolerance: int = 300
    ) -> bool:
        """Verify Stripe webhook signature."""
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured")
            return False
        
        try:
            elements = signature_header.split(',')
            signature_dict = {}
            
            for element in elements:
                key, value = element.split('=')
                signature_dict[key] = value
            
            timestamp = int(signature_dict.get('t', '0'))
            signatures = signature_dict.get('v1', '').split(' ')
            
            # Check timestamp tolerance
            current_time = int(datetime.now().timestamp())
            if abs(current_time - timestamp) > tolerance:
                logger.warning("Webhook timestamp outside tolerance")
                return False
            
            # Verify signature
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                f"{timestamp}.".encode('utf-8') + payload,
                hashlib.sha256
            ).hexdigest()
            
            return expected_signature in signatures
        
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return False
    
    async def handle_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming webhook event."""
        event_type = event_data.get("type")
        event_object = event_data.get("data", {}).get("object", {})
        
        logger.info(f"Processing webhook event: {event_type}")
        
        handlers = {
            "account.updated": self._handle_account_updated,
            "payment_intent.succeeded": self._handle_payment_succeeded,
            "transfer.created": self._handle_transfer_created,
            "payout.paid": self._handle_payout_paid,
            "capability.updated": self._handle_capability_updated
        }
        
        handler = handlers.get(event_type)
        if handler:
            return await handler(event_object)
        else:
            logger.info(f"No handler for event type: {event_type}")
            return {"status": "ignored"}
    
    async def _handle_account_updated(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle account updated event."""
        account_id = account_data.get("id")
        logger.info(f"Account updated: {account_id}")
        return {"status": "processed", "account_id": account_id}
    
    async def _handle_payment_succeeded(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment succeeded event."""
        payment_id = payment_data.get("id")
        amount = payment_data.get("amount", 0)
        logger.info(f"Payment succeeded: {payment_id}, amount: {amount}")
        return {"status": "processed", "payment_id": payment_id}
    
    async def _handle_transfer_created(self, transfer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle transfer created event."""
        transfer_id = transfer_data.get("id")
        logger.info(f"Transfer created: {transfer_id}")
        return {"status": "processed", "transfer_id": transfer_id}
    
    async def _handle_payout_paid(self, payout_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payout paid event."""
        payout_id = payout_data.get("id")
        logger.info(f"Payout paid: {payout_id}")
        return {"status": "processed", "payout_id": payout_id}
    
    async def _handle_capability_updated(self, capability_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle capability updated event."""
        account_id = capability_data.get("account")
        capability = capability_data.get("id")
        status = capability_data.get("status")
        logger.info(f"Capability updated: {account_id}, {capability}, {status}")
        return {"status": "processed", "account_id": account_id}
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_requests": self.request_count,
            "total_transactions": self.transaction_count,
            "total_volume": float(self.total_volume),
            "fees_collected": float(self.fee_collected),
            "average_transaction": float(self.total_volume / max(self.transaction_count, 1))
        }


# Utility functions
async def create_stripe_connect_integration(
    secret_key: str,
    publishable_key: str,
    webhook_secret: Optional[str] = None
) -> StripeConnectIntegration:
    """Create and initialize Stripe Connect integration."""
    integration = StripeConnectIntegration(
        secret_key=secret_key,
        publishable_key=publishable_key,
        webhook_secret=webhook_secret
    )
    await integration._ensure_session()
    return integration


async def create_marketplace_payment(
    amount: int,
    currency: str,
    platform_fee_percent: float,
    connected_account_id: str,
    secret_key: str,
    publishable_key: str
) -> PaymentIntent:
    """Quick marketplace payment creation."""
    application_fee = int(amount * platform_fee_percent / 100)
    
    async with StripeConnectIntegration(secret_key, publishable_key) as stripe:
        return await stripe.create_payment_intent(
            amount=amount,
            currency=currency,
            connected_account_id=connected_account_id,
            application_fee_amount=application_fee
        )


if __name__ == "__main__":
    # Example usage
    async def main():
        import os
        secret_key = os.getenv("STRIPE_SECRET_KEY")
        publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
        
        if not all([secret_key, publishable_key]):
            print("Please set STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY")
            return
        
        async with StripeConnectIntegration(secret_key, publishable_key) as stripe:
            # Test create account
            account = await stripe.create_account(
                account_type=AccountType.EXPRESS,
                email="creator@example.com",
                country="US"
            )
            print(f"Created account: {account.account_id}")
            
            # Test usage stats
            stats = stripe.get_usage_stats()
            print(f"Usage stats: {stats}")
    
    asyncio.run(main())