"""Wise Integration - International Payment Processing
=================================================

Comprehensive Wise API integration for international money transfers,
multi-currency support, and creator payouts for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import hmac
import base64
from decimal import Decimal

import aiohttp
import aiofiles
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

logger = logging.getLogger(__name__)


class WiseAccountType(Enum):
    """Wise account types."""
    PERSONAL = "personal"
    BUSINESS = "business"


class WiseTransferStatus(Enum):
    """Wise transfer status."""
    INCOMING_PAYMENT_WAITING = "incoming_payment_waiting"
    PROCESSING = "processing"
    FUNDS_CONVERTED = "funds_converted"
    OUTGOING_PAYMENT_SENT = "outgoing_payment_sent"
    CANCELLED = "cancelled"
    FUNDS_REFUNDED = "funds_refunded"


class WiseRecipientType(Enum):
    """Wise recipient types."""
    EMAIL = "email"
    BANK_ACCOUNT = "bank_account"
    CARD = "card"
    MOBILE_MONEY = "mobile_money"


@dataclass
class WiseProfile:
    """Wise user profile."""
    id: int
    type: WiseAccountType
    details: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class WiseCurrency:
    """Wise currency information."""
    code: str
    name: str
    symbol: str
    decimal_places: int
    supported_transfer_types: List[str]


@dataclass
class WiseExchangeRate:
    """Wise exchange rate."""
    source_currency: str
    target_currency: str
    rate: Decimal
    timestamp: datetime
    fee_percentage: Decimal
    expires_at: datetime


@dataclass
class WiseRecipient:
    """Wise transfer recipient."""
    id: int
    profile: int
    account_holder_name: str
    currency: str
    country: str
    type: WiseRecipientType
    details: Dict[str, Any]
    created_at: datetime


@dataclass
class WiseQuote:
    """Wise transfer quote."""
    id: str
    source_currency: str
    target_currency: str
    source_amount: Optional[Decimal]
    target_amount: Optional[Decimal]
    exchange_rate: Decimal
    fee: Decimal
    created_at: datetime
    expires_at: datetime
    profile_id: int


@dataclass
class WiseTransfer:
    """Wise money transfer."""
    id: int
    user: int
    target_account: int
    quote_uuid: str
    status: WiseTransferStatus
    reference: str
    rate: Decimal
    created_at: datetime
    business: Optional[int] = None
    transfer_request: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class WiseBalance:
    """Wise account balance."""
    id: int
    profile_id: int
    currency: str
    type: str
    name: str
    icon: str
    amount: Decimal
    reserved_amount: Decimal
    available_amount: Decimal


class WiseAPIClient:
    """Wise API client for payment processing."""
    
    def __init__(self, api_token -> None: str, sandbox -> None: bool = False, webhook_secret -> None: Optional[str] = None) -> None:
        self.api_token = api_token
        self.webhook_secret = webhook_secret
        self.base_url = "https://api.sandbox.transferwise.tech" if sandbox else "https://api.wise.com"
        self.session = None
        
        # Rate limiting
        self.rate_limit_requests = 0
        self.rate_limit_reset = time.time()
        self.max_requests_per_minute = 600
        
        # Cache
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def __aenter__(self) -> None:
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
                "User-Agent": "Ainflue-Integration/1.0"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Wise API."""
        await self._check_rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                self._update_rate_limit(response.headers)
                
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited by Wise API, waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    return await self._make_request(method, endpoint, **kwargs)
                
                response_data = await response.json()
                
                if response.status >= 400:
                    error_msg = response_data.get('message', f'HTTP {response.status}')
                    logger.error(f"Wise API error: {error_msg}")
                    raise Exception(f"Wise API error: {error_msg}")
                
                return response_data
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    async def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting."""
        current_time = time.time()
        
        if current_time > self.rate_limit_reset:
            self.rate_limit_requests = 0
            self.rate_limit_reset = current_time + 60
        
        if self.rate_limit_requests >= self.max_requests_per_minute:
            sleep_time = self.rate_limit_reset - current_time
            if sleep_time > 0:
                logger.warning(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
    
    def _update_rate_limit(self, headers -> None: Dict[str, str]) -> None:
        """Update rate limit tracking from response headers."""
        self.rate_limit_requests += 1
        
        if 'X-RateLimit-Remaining' in headers:
            remaining = int(headers['X-RateLimit-Remaining'])
            if remaining == 0 and 'X-RateLimit-Reset' in headers:
                self.rate_limit_reset = int(headers['X-RateLimit-Reset'])
    
    async def get_profiles(self) -> List[WiseProfile]:
        """Get user profiles."""
        try:
            response = await self._make_request("GET", "/v1/profiles")
            
            profiles = []
            for profile_data in response:
                profile = WiseProfile(
                    id=profile_data['id'],
                    type=WiseAccountType(profile_data['type']),
                    details=profile_data.get('details', {}),
                    created_at=datetime.fromisoformat(profile_data['createdAt'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(profile_data['updatedAt'].replace('Z', '+00:00'))
                )
                profiles.append(profile)
            
            return profiles
            
        except Exception as e:
            logger.error(f"Failed to get profiles: {str(e)}")
            raise
    
    async def get_currencies(self) -> List[WiseCurrency]:
        """Get supported currencies."""
        cache_key = "currencies"
        
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_data
        
        try:
            response = await self._make_request("GET", "/v1/currencies")
            
            currencies = []
            for currency_data in response:
                currency = WiseCurrency(
                    code=currency_data['code'],
                    name=currency_data['name'],
                    symbol=currency_data.get('symbol', ''),
                    decimal_places=currency_data.get('decimalPlaces', 2),
                    supported_transfer_types=currency_data.get('supportedTransferTypes', [])
                )
                currencies.append(currency)
            
            self.cache[cache_key] = (currencies, time.time())
            return currencies
            
        except Exception as e:
            logger.error(f"Failed to get currencies: {str(e)}")
            raise
    
    async def get_exchange_rates(self, source: str, target: str) -> WiseExchangeRate:
        """Get exchange rates between currencies."""
        cache_key = f"exchange_rate_{source}_{target}"
        
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < 60:  # Cache for 1 minute
                return cached_data
        
        try:
            params = {"source": source, "target": target}
            response = await self._make_request("GET", "/v1/rates", params=params)
            
            rate_data = response[0]  # Get first rate
            
            exchange_rate = WiseExchangeRate(
                source_currency=source,
                target_currency=target,
                rate=Decimal(str(rate_data['rate'])),
                timestamp=datetime.fromisoformat(rate_data['time'].replace('Z', '+00:00')),
                fee_percentage=Decimal(str(rate_data.get('fee', 0))),
                expires_at=datetime.utcnow() + timedelta(minutes=15)  # Estimate
            )
            
            self.cache[cache_key] = (exchange_rate, time.time())
            return exchange_rate
            
        except Exception as e:
            logger.error(f"Failed to get exchange rates: {str(e)}")
            raise
    
    async def create_recipient(self, profile_id: int, currency: str, 
                             recipient_type: WiseRecipientType, 
                             account_holder_name: str,
                             details: Dict[str, Any]) -> WiseRecipient:
        """Create a transfer recipient."""
        try:
            payload = {
                "currency": currency,
                "type": recipient_type.value,
                "profile": profile_id,
                "accountHolderName": account_holder_name,
                "details": details
            }
            
            response = await self._make_request("POST", "/v1/accounts", json=payload)
            
            recipient = WiseRecipient(
                id=response['id'],
                profile=response['profile'],
                account_holder_name=response['accountHolderName'],
                currency=response['currency'],
                country=response.get('country', ''),
                type=WiseRecipientType(response['type']),
                details=response.get('details', {}),
                created_at=datetime.fromisoformat(response['createdAt'].replace('Z', '+00:00'))
            )
            
            return recipient
            
        except Exception as e:
            logger.error(f"Failed to create recipient: {str(e)}")
            raise
    
    async def create_quote(self, profile_id: int, source_currency: str, 
                         target_currency: str, source_amount: Optional[Decimal] = None,
                         target_amount: Optional[Decimal] = None) -> WiseQuote:
        """Create a transfer quote."""
        try:
            payload = {
                "profile": profile_id,
                "source": source_currency,
                "target": target_currency,
                "rateType": "FIXED"
            }
            
            if source_amount:
                payload["sourceAmount"] = float(source_amount)
            elif target_amount:
                payload["targetAmount"] = float(target_amount)
            else:
                raise ValueError("Either source_amount or target_amount must be provided")
            
            response = await self._make_request("POST", "/v3/profiles/{}/quotes".format(profile_id), json=payload)
            
            quote = WiseQuote(
                id=response['id'],
                source_currency=response['source'],
                target_currency=response['target'],
                source_amount=Decimal(str(response.get('sourceAmount', 0))),
                target_amount=Decimal(str(response.get('targetAmount', 0))),
                exchange_rate=Decimal(str(response['rate'])),
                fee=Decimal(str(response['fee'])),
                created_at=datetime.fromisoformat(response['createdAt'].replace('Z', '+00:00')),
                expires_at=datetime.fromisoformat(response['expiresAt'].replace('Z', '+00:00')),
                profile_id=profile_id
            )
            
            return quote
            
        except Exception as e:
            logger.error(f"Failed to create quote: {str(e)}")
            raise
    
    async def create_transfer(self, target_account_id: int, quote_id: str, 
                            reference: str, details: Optional[Dict[str, Any]] = None) -> WiseTransfer:
        """Create a money transfer."""
        try:
            payload = {
                "targetAccount": target_account_id,
                "quote": quote_id,
                "customerTransactionId": hashlib.md5(f"{quote_id}_{time.time()}".encode()).hexdigest(),
                "details": {
                    "reference": reference,
                    "transferPurpose": "verification.transfers.purpose.pay.bills",
                    "sourceOfFunds": "verification.source.of.funds.other"
                }
            }
            
            if details:
                payload["details"].update(details)
            
            response = await self._make_request("POST", "/v1/transfers", json=payload)
            
            transfer = WiseTransfer(
                id=response['id'],
                user=response['user'],
                target_account=response['targetAccount'],
                quote_uuid=response['quote'],
                status=WiseTransferStatus(response['status']),
                reference=response['details']['reference'],
                rate=Decimal(str(response['rate'])),
                created_at=datetime.fromisoformat(response['created'].replace('Z', '+00:00')),
                business=response.get('business'),
                transfer_request=response.get('transferRequest'),
                details=response.get('details')
            )
            
            return transfer
            
        except Exception as e:
            logger.error(f"Failed to create transfer: {str(e)}")
            raise
    
    async def fund_transfer(self, profile_id: int, transfer_id: int) -> Dict[str, Any]:
        """Fund a transfer (for business accounts)."""
        try:
            payload = {"type": "BALANCE"}
            
            response = await self._make_request(
                "POST", 
                f"/v3/profiles/{profile_id}/transfers/{transfer_id}/payments",
                json=payload
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to fund transfer: {str(e)}")
            raise
    
    async def get_transfer_status(self, transfer_id: int) -> WiseTransfer:
        """Get transfer status."""
        try:
            response = await self._make_request("GET", f"/v1/transfers/{transfer_id}")
            
            transfer = WiseTransfer(
                id=response['id'],
                user=response['user'],
                target_account=response['targetAccount'],
                quote_uuid=response['quote'],
                status=WiseTransferStatus(response['status']),
                reference=response['details']['reference'],
                rate=Decimal(str(response['rate'])),
                created_at=datetime.fromisoformat(response['created'].replace('Z', '+00:00')),
                business=response.get('business'),
                transfer_request=response.get('transferRequest'),
                details=response.get('details')
            )
            
            return transfer
            
        except Exception as e:
            logger.error(f"Failed to get transfer status: {str(e)}")
            raise
    
    async def get_balances(self, profile_id: int) -> List[WiseBalance]:
        """Get account balances."""
        try:
            response = await self._make_request("GET", f"/v4/profiles/{profile_id}/balances")
            
            balances = []
            for balance_data in response:
                balance = WiseBalance(
                    id=balance_data['id'],
                    profile_id=profile_id,
                    currency=balance_data['currency'],
                    type=balance_data['type'],
                    name=balance_data['name'],
                    icon=balance_data.get('icon', ''),
                    amount=Decimal(str(balance_data['amount']['value'])),
                    reserved_amount=Decimal(str(balance_data['reservedAmount']['value'])),
                    available_amount=Decimal(str(balance_data['availableAmount']['value']))
                )
                balances.append(balance)
            
            return balances
            
        except Exception as e:
            logger.error(f"Failed to get balances: {str(e)}")
            raise
    
    async def cancel_transfer(self, transfer_id: int) -> bool:
        """Cancel a transfer."""
        try:
            await self._make_request("PUT", f"/v1/transfers/{transfer_id}/cancel")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel transfer: {str(e)}")
            return False
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature."""
        if not self.webhook_secret:
            logger.warning("No webhook secret configured")
            return False
        
        try:
            expected_signature = base64.b64encode(
                hmac.new(
                    self.webhook_secret.encode(),
                    payload,
                    hashlib.sha256
                ).digest()
            ).decode()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Failed to verify webhook signature: {str(e)}")
            return False


class WiseIntegration:
    """Main Wise integration for Ainflue platform."""
    
    def __init__(self, api_token -> None: str, sandbox -> None: bool = False, webhook_secret -> None: Optional[str] = None) -> None:
        self.api_token = api_token
        self.sandbox = sandbox
        self.webhook_secret = webhook_secret
        
        # Creator payout tracking
        self.pending_payouts: Dict[str, Dict] = {}
        self.completed_payouts: Dict[str, Dict] = {}
        
        # Supported currencies for creator payouts
        self.supported_payout_currencies = [
            'USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF', 'SEK', 'NOK', 'DKK',
            'PLN', 'CZK', 'HUF', 'BGN', 'RON', 'HRK', 'TRY', 'ZAR', 'SGD', 'HKD',
            'NZD', 'MXN', 'BRL', 'ARS', 'CLP', 'COP', 'PEN', 'UYU'
        ]
    
    async def initialize(self) -> bool:
        """Initialize Wise integration."""
        try:
            async with WiseAPIClient(self.api_token, self.sandbox, self.webhook_secret) as client:
                profiles = await client.get_profiles()
                if not profiles:
                    raise Exception("No Wise profiles found")
                
                currencies = await client.get_currencies()
                logger.info(f"Wise integration initialized with {len(currencies)} currencies")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize Wise integration: {str(e)}")
            return False
    
    async def create_creator_payout(self, creator_id: str, amount: Decimal, 
                                  currency: str, recipient_details: Dict[str, Any],
                                  reference: str = "") -> Dict[str, Any]:
        """Create a payout to a content creator."""
        try:
            if currency not in self.supported_payout_currencies:
                raise ValueError(f"Currency {currency} not supported for payouts")
            
            async with WiseAPIClient(self.api_token, self.sandbox, self.webhook_secret) as client:
                # Get business profile
                profiles = await client.get_profiles()
                business_profile = next((p for p in profiles if p.type == WiseAccountType.BUSINESS), None)
                
                if not business_profile:
                    raise Exception("Business profile required for creator payouts")
                
                # Create recipient
                recipient = await client.create_recipient(
                    profile_id=business_profile.id,
                    currency=currency,
                    recipient_type=WiseRecipientType.BANK_ACCOUNT,
                    account_holder_name=recipient_details.get('name', ''),
                    details=recipient_details
                )
                
                # Create quote
                quote = await client.create_quote(
                    profile_id=business_profile.id,
                    source_currency="USD",  # Ainflue primary currency
                    target_currency=currency,
                    source_amount=amount
                )
                
                # Create transfer
                transfer_reference = reference or f"Ainflue Creator Payout - {creator_id}"
                transfer = await client.create_transfer(
                    target_account_id=recipient.id,
                    quote_id=quote.id,
                    reference=transfer_reference,
                    details={
                        "creatorId": creator_id,
                        "platform": "ainflue",
                        "payoutType": "creator_earnings"
                    }
                )
                
                # Fund transfer
                funding_result = await client.fund_transfer(business_profile.id, transfer.id)
                
                payout_data = {
                    "payout_id": f"wise_{transfer.id}",
                    "creator_id": creator_id,
                    "transfer_id": transfer.id,
                    "recipient_id": recipient.id,
                    "quote_id": quote.id,
                    "amount": amount,
                    "currency": currency,
                    "exchange_rate": quote.exchange_rate,
                    "fee": quote.fee,
                    "status": transfer.status.value,
                    "reference": transfer_reference,
                    "created_at": transfer.created_at.isoformat(),
                    "funded": funding_result.get('status') == 'COMPLETED'
                }
                
                self.pending_payouts[payout_data["payout_id"]] = payout_data
                
                logger.info(f"Created Wise payout for creator {creator_id}: {amount} {currency}")
                return payout_data
                
        except Exception as e:
            logger.error(f"Failed to create creator payout: {str(e)}")
            raise
    
    async def get_payout_status(self, payout_id: str) -> Dict[str, Any]:
        """Get payout status."""
        try:
            if payout_id in self.completed_payouts:
                return self.completed_payouts[payout_id]
            
            if payout_id not in self.pending_payouts:
                raise ValueError(f"Payout {payout_id} not found")
            
            payout_data = self.pending_payouts[payout_id]
            transfer_id = payout_data["transfer_id"]
            
            async with WiseAPIClient(self.api_token, self.sandbox, self.webhook_secret) as client:
                transfer = await client.get_transfer_status(transfer_id)
                
                payout_data["status"] = transfer.status.value
                payout_data["updated_at"] = datetime.utcnow().isoformat()
                
                # Move to completed if transfer is done
                if transfer.status in [WiseTransferStatus.OUTGOING_PAYMENT_SENT, 
                                     WiseTransferStatus.CANCELLED, 
                                     WiseTransferStatus.FUNDS_REFUNDED]:
                    self.completed_payouts[payout_id] = payout_data
                    del self.pending_payouts[payout_id]
                
                return payout_data
                
        except Exception as e:
            logger.error(f"Failed to get payout status: {str(e)}")
            raise
    
    async def cancel_payout(self, payout_id: str) -> bool:
        """Cancel a pending payout."""
        try:
            if payout_id not in self.pending_payouts:
                raise ValueError(f"Payout {payout_id} not found or already completed")
            
            payout_data = self.pending_payouts[payout_id]
            transfer_id = payout_data["transfer_id"]
            
            async with WiseAPIClient(self.api_token, self.sandbox, self.webhook_secret) as client:
                success = await client.cancel_transfer(transfer_id)
                
                if success:
                    payout_data["status"] = "cancelled"
                    payout_data["cancelled_at"] = datetime.utcnow().isoformat()
                    self.completed_payouts[payout_id] = payout_data
                    del self.pending_payouts[payout_id]
                    
                    logger.info(f"Cancelled Wise payout {payout_id}")
                
                return success
                
        except Exception as e:
            logger.error(f"Failed to cancel payout: {str(e)}")
            return False
    
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Get current exchange rate."""
        try:
            async with WiseAPIClient(self.api_token, self.sandbox, self.webhook_secret) as client:
                rate = await client.get_exchange_rates(from_currency, to_currency)
                
                return {
                    "from_currency": rate.source_currency,
                    "to_currency": rate.target_currency,
                    "rate": float(rate.rate),
                    "fee_percentage": float(rate.fee_percentage),
                    "timestamp": rate.timestamp.isoformat(),
                    "expires_at": rate.expires_at.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get exchange rate: {str(e)}")
            raise
    
    async def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Handle Wise webhook."""
        try:
            async with WiseAPIClient(self.api_token, self.sandbox, self.webhook_secret) as client:
                if not client.verify_webhook_signature(payload, signature):
                    raise ValueError("Invalid webhook signature")
                
                webhook_data = json.loads(payload.decode())
                event_type = webhook_data.get('subscriptionName', '')
                
                if event_type == 'transfers#state-change':
                    return await self._handle_transfer_state_change(webhook_data)
                
                logger.info(f"Received Wise webhook: {event_type}")
                return {"status": "received", "event_type": event_type}
                
        except Exception as e:
            logger.error(f"Failed to handle webhook: {str(e)}")
            raise
    
    async def _handle_transfer_state_change(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle transfer state change webhook."""
        try:
            transfer_id = webhook_data['data']['resource']['id']
            new_status = webhook_data['data']['current_state']
            
            # Find payout by transfer ID
            payout_id = None
            for pid, payout in self.pending_payouts.items():
                if payout["transfer_id"] == transfer_id:
                    payout_id = pid
                    break
            
            if payout_id:
                await self.get_payout_status(payout_id)  # Update status
                logger.info(f"Updated payout {payout_id} status to {new_status}")
            
            return {
                "status": "processed",
                "transfer_id": transfer_id,
                "new_status": new_status,
                "payout_id": payout_id
            }
            
        except Exception as e:
            logger.error(f"Failed to handle transfer state change: {str(e)}")
            raise
    
    async def get_supported_countries(self) -> List[Dict[str, Any]]:
        """Get list of supported countries for transfers."""
        try:
            async with WiseAPIClient(self.api_token, self.sandbox, self.webhook_secret) as client:
                # This would typically come from a dedicated endpoint
                # For now, return common supported countries
                return [
                    {"code": "US", "name": "United States", "currencies": ["USD"]},
                    {"code": "GB", "name": "United Kingdom", "currencies": ["GBP"]},
                    {"code": "EU", "name": "European Union", "currencies": ["EUR"]},
                    {"code": "CA", "name": "Canada", "currencies": ["CAD"]},
                    {"code": "AU", "name": "Australia", "currencies": ["AUD"]},
                    {"code": "JP", "name": "Japan", "currencies": ["JPY"]},
                    {"code": "CH", "name": "Switzerland", "currencies": ["CHF"]},
                    {"code": "SG", "name": "Singapore", "currencies": ["SGD"]},
                    {"code": "HK", "name": "Hong Kong", "currencies": ["HKD"]},
                    {"code": "NZ", "name": "New Zealand", "currencies": ["NZD"]}
                ]
                
        except Exception as e:
            logger.error(f"Failed to get supported countries: {str(e)}")
            return []


# Example usage
async def main() -> None:
    """Example usage of Wise integration."""
    wise = WiseIntegration(
        api_token="your-wise-api-token",
        sandbox=True,
        webhook_secret="your-webhook-secret"
    )
    
    # Initialize
    if await wise.initialize():
        print("✅ Wise integration initialized")
        
        # Create creator payout
        payout = await wise.create_creator_payout(
            creator_id="creator_123",
            amount=Decimal("500.00"),
            currency="EUR",
            recipient_details={
                "name": "Creator Name",
                "iban": "DE89370400440532013000",
                "address": {
                    "country": "DE",
                    "city": "Berlin",
                    "postCode": "10115",
                    "firstLine": "Potsdamer Platz 1"
                }
            },
            reference="Monthly Earnings Payout"
        )
        
        print(f"💰 Created payout: {payout['payout_id']}")
        print(f"📊 Amount: {payout['amount']} {payout['currency']}")
        print(f"📈 Exchange rate: {payout['exchange_rate']}")
        print(f"💸 Fee: {payout['fee']}")
        
        # Check payout status
        status = await wise.get_payout_status(payout['payout_id'])
        print(f"📋 Status: {status['status']}")


if __name__ == "__main__":
    asyncio.run(main())