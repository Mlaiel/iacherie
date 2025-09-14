"""Payment Gateways Integration - Multi-Gateway Payment Processing
=============================================================

Professional integration for multiple payment gateways including
PayPal, Wise, Bank transfers, and Cryptocurrency payments.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
import json
import aiohttp
import hashlib
import hmac
import base64
import uuid

logger = logging.getLogger(__name__)


class PaymentGateway(str, Enum):
    """Supported payment gateways."""
    PAYPAL = "paypal"
    WISE = "wise"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    ALIPAY = "alipay"
    WECHAT_PAY = "wechat_pay"


class PaymentMethod(str, Enum):
    """Payment method types."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_ACCOUNT = "bank_account"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"
    DIRECT_DEBIT = "direct_debit"
    WIRE_TRANSFER = "wire_transfer"


class PaymentStatus(str, Enum):
    """Payment status across gateways."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class CurrencyCode(str, Enum):
    """Supported currency codes."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"
    BTC = "BTC"
    ETH = "ETH"


class TransactionType(str, Enum):
    """Transaction types."""
    PAYMENT = "payment"
    REFUND = "refund"
    PAYOUT = "payout"
    TRANSFER = "transfer"
    CONVERSION = "conversion"
    FEE = "fee"


@dataclass
class PaymentAccount:
    """Payment gateway account configuration."""
    gateway: PaymentGateway
    account_id: str
    account_name: str
    currency: CurrencyCode
    credentials: Dict[str, str]
    is_active: bool
    is_verified: bool
    supported_methods: List[PaymentMethod]
    fee_structure: Dict[str, Decimal]
    limits: Dict[str, Decimal]
    metadata: Dict[str, Any]


@dataclass
class PaymentTransaction:
    """Payment transaction data."""
    transaction_id: str
    gateway: PaymentGateway
    transaction_type: TransactionType
    amount: Decimal
    currency: CurrencyCode
    status: PaymentStatus
    payment_method: PaymentMethod
    sender_info: Dict[str, Any]
    recipient_info: Dict[str, Any]
    fees: Dict[str, Decimal]
    exchange_rate: Optional[Decimal]
    reference_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]


@dataclass
class PayoutRequest:
    """Payout request data."""
    payout_id: str
    gateway: PaymentGateway
    recipient_account: str
    amount: Decimal
    currency: CurrencyCode
    status: PaymentStatus
    scheduled_at: Optional[datetime]
    processed_at: Optional[datetime]
    fees: Dict[str, Decimal]
    exchange_info: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]


@dataclass
class ExchangeRate:
    """Currency exchange rate data."""
    from_currency: CurrencyCode
    to_currency: CurrencyCode
    rate: Decimal
    timestamp: datetime
    source: str
    fees: Decimal
    metadata: Dict[str, Any]


class PaymentGatewaysIntegration:
    """Professional multi-gateway payment processing integration."""
    
    def __init__(
        self,
        # PayPal credentials
        paypal_client_id -> None: Optional[str] = None,
        paypal_client_secret -> None: Optional[str] = None,
        paypal_webhook_id -> None: Optional[str] = None,
        # Wise credentials
        wise_api_token -> None: Optional[str] = None,
        wise_profile_id -> None: Optional[str] = None,
        # Bank transfer settings
        bank_routing_number -> None: Optional[str] = None,
        bank_account_number -> None: Optional[str] = None,
        swift_code -> None: Optional[str] = None,
        # Crypto settings
        crypto_api_key -> None: Optional[str] = None,
        crypto_secret -> None: Optional[str] = None,
        # Environment settings
        environment -> None: str = "sandbox",
        timeout -> None: int = 30
    ) -> None:
        # Credentials storage
        self.paypal_client_id = paypal_client_id
        self.paypal_client_secret = paypal_client_secret
        self.paypal_webhook_id = paypal_webhook_id
        self.wise_api_token = wise_api_token
        self.wise_profile_id = wise_profile_id
        self.bank_routing_number = bank_routing_number
        self.bank_account_number = bank_account_number
        self.swift_code = swift_code
        self.crypto_api_key = crypto_api_key
        self.crypto_secret = crypto_secret
        
        self.environment = environment
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Connected accounts storage
        self.payment_accounts: Dict[str, PaymentAccount] = {}
        
        # Usage tracking
        self.total_transactions = 0
        self.total_volume = Decimal('0')
        self.total_fees = Decimal('0')
        self.request_count = 0
        self.gateway_usage = {}
        
        # Gateway base URLs
        self.gateway_urls = {
            PaymentGateway.PAYPAL: {
                "sandbox": "https://api-m.sandbox.paypal.com",
                "live": "https://api-m.paypal.com"
            },
            PaymentGateway.WISE: {
                "sandbox": "https://api.sandbox.transferwise.tech",
                "live": "https://api.wise.com"
            },
            PaymentGateway.CRYPTO: {
                "sandbox": "https://api.sandbox.coinbase.com",
                "live": "https://api.coinbase.com"
            }
        }
        
        logger.info("Payment Gateways integration initialized")
    
    async def __aenter__(self) -> None:
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self) -> None:
        """Ensure HTTP session is available."""
        if self.session is None or self.session.closed:
            headers = {
                "User-Agent": "Ainflue/1.0 Payment Gateway Hub",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
    
    async def close(self) -> None:
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def initialize_paypal_account(self) -> PaymentAccount:
        """Initialize PayPal payment account."""
        await self._ensure_session()
        
        if not self.paypal_client_id or not self.paypal_client_secret:
            raise ValueError("PayPal credentials not configured")
        
        try:
            # Get PayPal access token
            access_token = await self._get_paypal_access_token()
            
            # Get account information
            headers = {"Authorization": f"Bearer {access_token}"}
            base_url = self.gateway_urls[PaymentGateway.PAYPAL][self.environment]
            
            async with self.session.get(
                f"{base_url}/v1/identity/oauth2/userinfo?schema=paypalv1.1",
                headers=headers
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"PayPal account info error: {error_data}")
                
                account_info = await response.json()
                
                account = PaymentAccount(
                    gateway=PaymentGateway.PAYPAL,
                    account_id=account_info.get("user_id", "unknown"),
                    account_name=account_info.get("name", "PayPal Account"),
                    currency=CurrencyCode.USD,
                    credentials={"access_token": access_token},
                    is_active=True,
                    is_verified=account_info.get("verified_account", False),
                    supported_methods=[PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD, PaymentMethod.DIGITAL_WALLET],
                    fee_structure={"transaction": Decimal("0.029"), "fixed": Decimal("0.30")},
                    limits={"daily": Decimal("10000"), "monthly": Decimal("100000")},
                    metadata={"account_info": account_info}
                )
                
                self.payment_accounts[f"{PaymentGateway.PAYPAL}_{account.account_id}"] = account
                self.gateway_usage[PaymentGateway.PAYPAL] = 0
                self.request_count += 2
                
                logger.info(f"PayPal account initialized: {account.account_id}")
                return account
        
        except Exception as e:
            logger.error(f"PayPal account initialization failed: {e}")
            raise
    
    async def _get_paypal_access_token(self) -> str:
        """Get PayPal access token."""
        credentials = base64.b64encode(
            f"{self.paypal_client_id}:{self.paypal_client_secret}".encode()
        ).decode()
        
        headers = {
            "Authorization": f"Basic {credentials}",
            "Accept": "application/json",
            "Accept-Language": "en_US",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = "grant_type=client_credentials"
        base_url = self.gateway_urls[PaymentGateway.PAYPAL][self.environment]
        
        async with self.session.post(
            f"{base_url}/v1/oauth2/token",
            data=data,
            headers=headers
        ) as response:
            if response.status != 200:
                error_data = await response.json()
                raise Exception(f"PayPal token error: {error_data}")
            
            token_data = await response.json()
            return token_data["access_token"]
    
    async def initialize_wise_account(self) -> PaymentAccount:
        """Initialize Wise payment account."""
        await self._ensure_session()
        
        if not self.wise_api_token:
            raise ValueError("Wise API token not configured")
        
        try:
            headers = {"Authorization": f"Bearer {self.wise_api_token}"}
            base_url = self.gateway_urls[PaymentGateway.WISE][self.environment]
            
            # Get user profile
            async with self.session.get(
                f"{base_url}/v1/profiles",
                headers=headers
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Wise profile error: {error_data}")
                
                profiles = await response.json()
                profile = profiles[0] if profiles else {}
                
                account = PaymentAccount(
                    gateway=PaymentGateway.WISE,
                    account_id=str(profile.get("id", "unknown")),
                    account_name=profile.get("details", {}).get("firstName", "") + " " + 
                               profile.get("details", {}).get("lastName", ""),
                    currency=CurrencyCode.USD,
                    credentials={"api_token": self.wise_api_token},
                    is_active=True,
                    is_verified=profile.get("details", {}).get("status") == "verified",
                    supported_methods=[PaymentMethod.BANK_ACCOUNT, PaymentMethod.WIRE_TRANSFER],
                    fee_structure={"percentage": Decimal("0.005"), "minimum": Decimal("1.00")},
                    limits={"daily": Decimal("50000"), "monthly": Decimal("500000")},
                    metadata={"profile": profile}
                )
                
                self.payment_accounts[f"{PaymentGateway.WISE}_{account.account_id}"] = account
                self.gateway_usage[PaymentGateway.WISE] = 0
                self.request_count += 1
                
                logger.info(f"Wise account initialized: {account.account_id}")
                return account
        
        except Exception as e:
            logger.error(f"Wise account initialization failed: {e}")
            raise
    
    async def initialize_crypto_account(self) -> PaymentAccount:
        """Initialize cryptocurrency payment account."""
        await self._ensure_session()
        
        if not self.crypto_api_key or not self.crypto_secret:
            raise ValueError("Crypto API credentials not configured")
        
        try:
            # This is a simplified example - actual crypto integration would vary by provider
            account = PaymentAccount(
                gateway=PaymentGateway.CRYPTO,
                account_id="crypto_main",
                account_name="Cryptocurrency Wallet",
                currency=CurrencyCode.BTC,
                credentials={"api_key": self.crypto_api_key},
                is_active=True,
                is_verified=True,
                supported_methods=[PaymentMethod.CRYPTOCURRENCY],
                fee_structure={"network": Decimal("0.0005"), "exchange": Decimal("0.015")},
                limits={"daily": Decimal("10"), "monthly": Decimal("100")},  # In BTC
                metadata={"supported_currencies": ["BTC", "ETH", "LTC"]}
            )
            
            self.payment_accounts[f"{PaymentGateway.CRYPTO}_{account.account_id}"] = account
            self.gateway_usage[PaymentGateway.CRYPTO] = 0
            
            logger.info(f"Crypto account initialized: {account.account_id}")
            return account
        
        except Exception as e:
            logger.error(f"Crypto account initialization failed: {e}")
            raise
    
    async def process_payment(
        self,
        gateway: PaymentGateway,
        amount: Decimal,
        currency: CurrencyCode,
        payment_method: PaymentMethod,
        sender_info: Dict[str, Any],
        recipient_info: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentTransaction:
        """Process payment through specified gateway."""
        await self._ensure_session()
        
        transaction_id = str(uuid.uuid4())
        
        if gateway == PaymentGateway.PAYPAL:
            return await self._process_paypal_payment(
                transaction_id, amount, currency, payment_method, 
                sender_info, recipient_info, metadata
            )
        elif gateway == PaymentGateway.WISE:
            return await self._process_wise_payment(
                transaction_id, amount, currency, payment_method,
                sender_info, recipient_info, metadata
            )
        elif gateway == PaymentGateway.CRYPTO:
            return await self._process_crypto_payment(
                transaction_id, amount, currency, payment_method,
                sender_info, recipient_info, metadata
            )
        else:
            raise ValueError(f"Unsupported gateway: {gateway}")
    
    async def _process_paypal_payment(
        self,
        transaction_id: str,
        amount: Decimal,
        currency: CurrencyCode,
        payment_method: PaymentMethod,
        sender_info: Dict[str, Any],
        recipient_info: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> PaymentTransaction:
        """Process PayPal payment."""
        try:
            access_token = await self._get_paypal_access_token()
            headers = {"Authorization": f"Bearer {access_token}"}
            base_url = self.gateway_urls[PaymentGateway.PAYPAL][self.environment]
            
            payment_data = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": currency.value,
                        "value": str(amount)
                    },
                    "description": metadata.get("description", "Payment via Ainflue")
                }],
                "payment_source": {
                    "paypal": {
                        "experience_context": {
                            "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                            "brand_name": "Ainflue",
                            "locale": "en-US",
                            "user_action": "PAY_NOW"
                        }
                    }
                }
            }
            
            async with self.session.post(
                f"{base_url}/v2/checkout/orders",
                json=payment_data,
                headers=headers
            ) as response:
                if response.status not in [200, 201]:
                    error_data = await response.json()
                    raise Exception(f"PayPal payment error: {error_data}")
                
                result = await response.json()
                
                # Calculate fees
                fee_rate = self.payment_accounts.get(f"{PaymentGateway.PAYPAL}_unknown", {}).get("fee_structure", {})
                transaction_fee = amount * fee_rate.get("transaction", Decimal("0.029"))
                fixed_fee = fee_rate.get("fixed", Decimal("0.30"))
                total_fees = transaction_fee + fixed_fee
                
                transaction = PaymentTransaction(
                    transaction_id=result["id"],
                    gateway=PaymentGateway.PAYPAL,
                    transaction_type=TransactionType.PAYMENT,
                    amount=amount,
                    currency=currency,
                    status=PaymentStatus.PENDING,
                    payment_method=payment_method,
                    sender_info=sender_info,
                    recipient_info=recipient_info,
                    fees={"transaction": transaction_fee, "fixed": fixed_fee, "total": total_fees},
                    exchange_rate=None,
                    reference_id=transaction_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    completed_at=None,
                    metadata=metadata or {}
                )
                
                self.total_transactions += 1
                self.total_volume += amount
                self.total_fees += total_fees
                self.request_count += 2
                self.gateway_usage[PaymentGateway.PAYPAL] = self.gateway_usage.get(PaymentGateway.PAYPAL, 0) + 1
                
                logger.info(f"PayPal payment created: {transaction.transaction_id}")
                return transaction
        
        except Exception as e:
            logger.error(f"PayPal payment processing failed: {e}")
            raise
    
    async def _process_wise_payment(
        self,
        transaction_id: str,
        amount: Decimal,
        currency: CurrencyCode,
        payment_method: PaymentMethod,
        sender_info: Dict[str, Any],
        recipient_info: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> PaymentTransaction:
        """Process Wise payment."""
        try:
            headers = {"Authorization": f"Bearer {self.wise_api_token}"}
            base_url = self.gateway_urls[PaymentGateway.WISE][self.environment]
            
            # Create quote first
            quote_data = {
                "sourceCurrency": currency.value,
                "targetCurrency": currency.value,
                "sourceAmount": float(amount),
                "profile": int(self.wise_profile_id) if self.wise_profile_id else None
            }
            
            async with self.session.post(
                f"{base_url}/v2/quotes",
                json=quote_data,
                headers=headers
            ) as response:
                if response.status not in [200, 201]:
                    error_data = await response.json()
                    raise Exception(f"Wise quote error: {error_data}")
                
                quote = await response.json()
                
                # Calculate fees
                fee_structure = self.payment_accounts.get(f"{PaymentGateway.WISE}_unknown", {}).get("fee_structure", {})
                transaction_fee = amount * fee_structure.get("percentage", Decimal("0.005"))
                minimum_fee = fee_structure.get("minimum", Decimal("1.00"))
                total_fees = max(transaction_fee, minimum_fee)
                
                transaction = PaymentTransaction(
                    transaction_id=str(quote["id"]),
                    gateway=PaymentGateway.WISE,
                    transaction_type=TransactionType.TRANSFER,
                    amount=amount,
                    currency=currency,
                    status=PaymentStatus.PENDING,
                    payment_method=payment_method,
                    sender_info=sender_info,
                    recipient_info=recipient_info,
                    fees={"transaction": transaction_fee, "total": total_fees},
                    exchange_rate=Decimal(str(quote.get("rate", 1.0))),
                    reference_id=transaction_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    completed_at=None,
                    metadata=metadata or {}
                )
                
                self.total_transactions += 1
                self.total_volume += amount
                self.total_fees += total_fees
                self.request_count += 1
                self.gateway_usage[PaymentGateway.WISE] = self.gateway_usage.get(PaymentGateway.WISE, 0) + 1
                
                logger.info(f"Wise payment created: {transaction.transaction_id}")
                return transaction
        
        except Exception as e:
            logger.error(f"Wise payment processing failed: {e}")
            raise
    
    async def _process_crypto_payment(
        self,
        transaction_id: str,
        amount: Decimal,
        currency: CurrencyCode,
        payment_method: PaymentMethod,
        sender_info: Dict[str, Any],
        recipient_info: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> PaymentTransaction:
        """Process cryptocurrency payment."""
        try:
            # This is a simplified example - actual implementation would vary by crypto provider
            
            # Calculate network and exchange fees
            fee_structure = self.payment_accounts.get(f"{PaymentGateway.CRYPTO}_crypto_main", {}).get("fee_structure", {})
            network_fee = fee_structure.get("network", Decimal("0.0005"))
            exchange_fee = amount * fee_structure.get("exchange", Decimal("0.015"))
            total_fees = network_fee + exchange_fee
            
            transaction = PaymentTransaction(
                transaction_id=transaction_id,
                gateway=PaymentGateway.CRYPTO,
                transaction_type=TransactionType.PAYMENT,
                amount=amount,
                currency=currency,
                status=PaymentStatus.PENDING,
                payment_method=payment_method,
                sender_info=sender_info,
                recipient_info=recipient_info,
                fees={"network": network_fee, "exchange": exchange_fee, "total": total_fees},
                exchange_rate=None,
                reference_id=transaction_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                completed_at=None,
                metadata=metadata or {}
            )
            
            self.total_transactions += 1
            self.total_volume += amount
            self.total_fees += total_fees
            self.gateway_usage[PaymentGateway.CRYPTO] = self.gateway_usage.get(PaymentGateway.CRYPTO, 0) + 1
            
            logger.info(f"Crypto payment created: {transaction.transaction_id}")
            return transaction
        
        except Exception as e:
            logger.error(f"Crypto payment processing failed: {e}")
            raise
    
    async def create_payout(
        self,
        gateway: PaymentGateway,
        recipient_account: str,
        amount: Decimal,
        currency: CurrencyCode,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PayoutRequest:
        """Create payout request."""
        await self._ensure_session()
        
        payout_id = str(uuid.uuid4())
        
        if gateway == PaymentGateway.PAYPAL:
            return await self._create_paypal_payout(payout_id, recipient_account, amount, currency, metadata)
        elif gateway == PaymentGateway.WISE:
            return await self._create_wise_payout(payout_id, recipient_account, amount, currency, metadata)
        elif gateway == PaymentGateway.CRYPTO:
            return await self._create_crypto_payout(payout_id, recipient_account, amount, currency, metadata)
        else:
            raise ValueError(f"Unsupported gateway for payout: {gateway}")
    
    async def _create_paypal_payout(
        self,
        payout_id: str,
        recipient_account: str,
        amount: Decimal,
        currency: CurrencyCode,
        metadata: Dict[str, Any]
    ) -> PayoutRequest:
        """Create PayPal payout."""
        try:
            access_token = await self._get_paypal_access_token()
            headers = {"Authorization": f"Bearer {access_token}"}
            base_url = self.gateway_urls[PaymentGateway.PAYPAL][self.environment]
            
            payout_data = {
                "sender_batch_header": {
                    "sender_batch_id": payout_id,
                    "email_subject": "You have a payout!",
                    "email_message": "You have received a payout from Ainflue!"
                },
                "items": [{
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": str(amount),
                        "currency": currency.value
                    },
                    "receiver": recipient_account,
                    "sender_item_id": f"item_{payout_id}",
                    "note": metadata.get("note", "Payout from Ainflue")
                }]
            }
            
            async with self.session.post(
                f"{base_url}/v1/payments/payouts",
                json=payout_data,
                headers=headers
            ) as response:
                if response.status not in [200, 201]:
                    error_data = await response.json()
                    raise Exception(f"PayPal payout error: {error_data}")
                
                result = await response.json()
                
                # Calculate fees
                fee_rate = Decimal("0.02")  # PayPal payout fee
                fees = amount * fee_rate
                
                payout = PayoutRequest(
                    payout_id=result["batch_header"]["payout_batch_id"],
                    gateway=PaymentGateway.PAYPAL,
                    recipient_account=recipient_account,
                    amount=amount,
                    currency=currency,
                    status=PaymentStatus.PENDING,
                    scheduled_at=None,
                    processed_at=None,
                    fees={"payout": fees, "total": fees},
                    exchange_info=None,
                    metadata=metadata or {}
                )
                
                self.request_count += 2
                logger.info(f"PayPal payout created: {payout.payout_id}")
                return payout
        
        except Exception as e:
            logger.error(f"PayPal payout creation failed: {e}")
            raise
    
    async def _create_wise_payout(
        self,
        payout_id: str,
        recipient_account: str,
        amount: Decimal,
        currency: CurrencyCode,
        metadata: Dict[str, Any]
    ) -> PayoutRequest:
        """Create Wise payout."""
        try:
            headers = {"Authorization": f"Bearer {self.wise_api_token}"}
            base_url = self.gateway_urls[PaymentGateway.WISE][self.environment]
            
            # Create recipient first (simplified)
            recipient_data = {
                "profile": int(self.wise_profile_id) if self.wise_profile_id else None,
                "accountHolderName": metadata.get("recipient_name", "Unknown"),
                "currency": currency.value,
                "type": "email",
                "details": {
                    "email": recipient_account
                }
            }
            
            async with self.session.post(
                f"{base_url}/v1/accounts",
                json=recipient_data,
                headers=headers
            ) as response:
                if response.status not in [200, 201]:
                    error_data = await response.json()
                    raise Exception(f"Wise recipient error: {error_data}")
                
                recipient = await response.json()
                
                # Calculate fees
                fee_structure = self.payment_accounts.get(f"{PaymentGateway.WISE}_unknown", {}).get("fee_structure", {})
                fees = amount * fee_structure.get("percentage", Decimal("0.005"))
                
                payout = PayoutRequest(
                    payout_id=payout_id,
                    gateway=PaymentGateway.WISE,
                    recipient_account=recipient_account,
                    amount=amount,
                    currency=currency,
                    status=PaymentStatus.PENDING,
                    scheduled_at=None,
                    processed_at=None,
                    fees={"transfer": fees, "total": fees},
                    exchange_info=None,
                    metadata=metadata or {}
                )
                
                self.request_count += 1
                logger.info(f"Wise payout created: {payout.payout_id}")
                return payout
        
        except Exception as e:
            logger.error(f"Wise payout creation failed: {e}")
            raise
    
    async def _create_crypto_payout(
        self,
        payout_id: str,
        recipient_account: str,
        amount: Decimal,
        currency: CurrencyCode,
        metadata: Dict[str, Any]
    ) -> PayoutRequest:
        """Create cryptocurrency payout."""
        try:
            # Calculate network fees
            network_fee = Decimal("0.0005")  # BTC network fee example
            
            payout = PayoutRequest(
                payout_id=payout_id,
                gateway=PaymentGateway.CRYPTO,
                recipient_account=recipient_account,
                amount=amount,
                currency=currency,
                status=PaymentStatus.PENDING,
                scheduled_at=None,
                processed_at=None,
                fees={"network": network_fee, "total": network_fee},
                exchange_info=None,
                metadata=metadata or {}
            )
            
            logger.info(f"Crypto payout created: {payout.payout_id}")
            return payout
        
        except Exception as e:
            logger.error(f"Crypto payout creation failed: {e}")
            raise
    
    async def get_exchange_rates(
        self,
        from_currency: CurrencyCode,
        to_currency: CurrencyCode,
        amount: Optional[Decimal] = None
    ) -> ExchangeRate:
        """Get current exchange rates between currencies."""
        await self._ensure_session()
        
        try:
            # Using a free exchange rate API (example)
            async with self.session.get(
                f"https://api.exchangerate-api.com/v4/latest/{from_currency.value}"
            ) as response:
                if response.status != 200:
                    raise Exception("Exchange rate API error")
                
                data = await response.json()
                rate = Decimal(str(data["rates"].get(to_currency.value, 1.0)))
                
                # Calculate conversion fees (0.5% example)
                fee_rate = Decimal("0.005")
                fees = (amount or Decimal("1")) * fee_rate if amount else Decimal("0")
                
                exchange_rate = ExchangeRate(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=rate,
                    timestamp=datetime.now(),
                    source="exchangerate-api.com",
                    fees=fees,
                    metadata={"raw_data": data}
                )
                
                self.request_count += 1
                logger.info(f"Exchange rate retrieved: {from_currency} -> {to_currency}: {rate}")
                return exchange_rate
        
        except Exception as e:
            logger.error(f"Exchange rate retrieval failed: {e}")
            raise
    
    async def convert_currency(
        self,
        amount: Decimal,
        from_currency: CurrencyCode,
        to_currency: CurrencyCode,
        gateway: PaymentGateway = PaymentGateway.WISE
    ) -> PaymentTransaction:
        """Convert currency using specified gateway."""
        if from_currency == to_currency:
            raise ValueError("Source and target currencies must be different")
        
        exchange_rate = await self.get_exchange_rates(from_currency, to_currency, amount)
        converted_amount = amount * exchange_rate.rate
        
        transaction_id = str(uuid.uuid4())
        
        transaction = PaymentTransaction(
            transaction_id=transaction_id,
            gateway=gateway,
            transaction_type=TransactionType.CONVERSION,
            amount=converted_amount,
            currency=to_currency,
            status=PaymentStatus.COMPLETED,
            payment_method=PaymentMethod.DIGITAL_WALLET,
            sender_info={"currency": from_currency.value, "amount": str(amount)},
            recipient_info={"currency": to_currency.value, "amount": str(converted_amount)},
            fees={"conversion": exchange_rate.fees, "total": exchange_rate.fees},
            exchange_rate=exchange_rate.rate,
            reference_id=transaction_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            completed_at=datetime.now(),
            metadata={"exchange_source": exchange_rate.source}
        )
        
        self.total_transactions += 1
        self.total_volume += converted_amount
        self.total_fees += exchange_rate.fees
        
        logger.info(f"Currency conversion: {amount} {from_currency} -> {converted_amount} {to_currency}")
        return transaction
    
    async def get_transaction_status(
        self,
        gateway: PaymentGateway,
        transaction_id: str
    ) -> PaymentStatus:
        """Get transaction status from gateway."""
        await self._ensure_session()
        
        if gateway == PaymentGateway.PAYPAL:
            return await self._get_paypal_transaction_status(transaction_id)
        elif gateway == PaymentGateway.WISE:
            return await self._get_wise_transaction_status(transaction_id)
        elif gateway == PaymentGateway.CRYPTO:
            return await self._get_crypto_transaction_status(transaction_id)
        else:
            raise ValueError(f"Unsupported gateway: {gateway}")
    
    async def _get_paypal_transaction_status(self, transaction_id: str) -> PaymentStatus:
        """Get PayPal transaction status."""
        try:
            access_token = await self._get_paypal_access_token()
            headers = {"Authorization": f"Bearer {access_token}"}
            base_url = self.gateway_urls[PaymentGateway.PAYPAL][self.environment]
            
            async with self.session.get(
                f"{base_url}/v2/checkout/orders/{transaction_id}",
                headers=headers
            ) as response:
                if response.status != 200:
                    return PaymentStatus.FAILED
                
                data = await response.json()
                status = data.get("status", "").upper()
                
                status_mapping = {
                    "CREATED": PaymentStatus.PENDING,
                    "SAVED": PaymentStatus.PENDING,
                    "APPROVED": PaymentStatus.PROCESSING,
                    "VOIDED": PaymentStatus.CANCELLED,
                    "COMPLETED": PaymentStatus.COMPLETED,
                    "PAYER_ACTION_REQUIRED": PaymentStatus.PENDING
                }
                
                self.request_count += 2
                return status_mapping.get(status, PaymentStatus.FAILED)
        
        except Exception as e:
            logger.error(f"PayPal status check failed: {e}")
            return PaymentStatus.FAILED
    
    async def _get_wise_transaction_status(self, transaction_id: str) -> PaymentStatus:
        """Get Wise transaction status."""
        try:
            headers = {"Authorization": f"Bearer {self.wise_api_token}"}
            base_url = self.gateway_urls[PaymentGateway.WISE][self.environment]
            
            async with self.session.get(
                f"{base_url}/v1/transfers/{transaction_id}",
                headers=headers
            ) as response:
                if response.status != 200:
                    return PaymentStatus.FAILED
                
                data = await response.json()
                status = data.get("status", "").lower()
                
                status_mapping = {
                    "incoming_payment_waiting": PaymentStatus.PENDING,
                    "processing": PaymentStatus.PROCESSING,
                    "funds_converted": PaymentStatus.PROCESSING,
                    "outgoing_payment_sent": PaymentStatus.COMPLETED,
                    "cancelled": PaymentStatus.CANCELLED,
                    "funds_refunded": PaymentStatus.REFUNDED
                }
                
                self.request_count += 1
                return status_mapping.get(status, PaymentStatus.FAILED)
        
        except Exception as e:
            logger.error(f"Wise status check failed: {e}")
            return PaymentStatus.FAILED
    
    async def _get_crypto_transaction_status(self, transaction_id: str) -> PaymentStatus:
        """Get cryptocurrency transaction status."""
        try:
            # This would check blockchain or exchange API
            # Simplified example
            return PaymentStatus.PENDING
        
        except Exception as e:
            logger.error(f"Crypto status check failed: {e}")
            return PaymentStatus.FAILED
    
    async def get_payment_accounts(self) -> List[PaymentAccount]:
        """Get all configured payment accounts."""
        return list(self.payment_accounts.values())
    
    async def optimize_payout_routing(
        self,
        amount: Decimal,
        currency: CurrencyCode,
        destination_country: str,
        speed_priority: str = "standard"  # "instant", "fast", "standard", "economy"
    ) -> Dict[str, Any]:
        """Optimize payout routing based on cost, speed, and reliability."""
        
        # Route optimization logic
        routes = []
        
        # PayPal route
        if PaymentGateway.PAYPAL in self.gateway_usage:
            paypal_fee = amount * Decimal("0.02")
            routes.append({
                "gateway": PaymentGateway.PAYPAL,
                "fee": paypal_fee,
                "speed_hours": 24,
                "reliability_score": 0.95,
                "total_cost": paypal_fee
            })
        
        # Wise route
        if PaymentGateway.WISE in self.gateway_usage:
            wise_fee = max(amount * Decimal("0.005"), Decimal("1.00"))
            routes.append({
                "gateway": PaymentGateway.WISE,
                "fee": wise_fee,
                "speed_hours": 48,
                "reliability_score": 0.98,
                "total_cost": wise_fee
            })
        
        # Sort routes by optimization criteria
        if speed_priority == "instant":
            routes.sort(key=lambda x: x["speed_hours"])
        elif speed_priority == "economy":
            routes.sort(key=lambda x: x["total_cost"])
        else:
            # Balanced optimization
            routes.sort(key=lambda x: (x["total_cost"] * 0.5 + x["speed_hours"] * 0.3 - x["reliability_score"] * 0.2))
        
        recommendation = routes[0] if routes else None
        
        logger.info(f"Payout routing optimized for {amount} {currency} - Recommended: {recommendation}")
        
        return {
            "recommended_route": recommendation,
            "all_routes": routes,
            "optimization_criteria": speed_priority,
            "savings_potential": max([r["total_cost"] for r in routes]) - min([r["total_cost"] for r in routes]) if routes else 0
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get payment processing usage statistics."""
        return {
            "total_requests": self.request_count,
            "total_transactions": self.total_transactions,
            "total_volume": float(self.total_volume),
            "total_fees": float(self.total_fees),
            "average_transaction_size": float(self.total_volume / max(self.total_transactions, 1)),
            "gateway_usage": dict(self.gateway_usage),
            "connected_accounts": len(self.payment_accounts),
            "fee_percentage": float((self.total_fees / max(self.total_volume, 1)) * 100)
        }


# Utility functions
async def create_payment_gateways_integration(
    paypal_client_id: Optional[str] = None,
    paypal_client_secret: Optional[str] = None,
    wise_api_token: Optional[str] = None,
    environment: str = "sandbox"
) -> PaymentGatewaysIntegration:
    """Create and initialize payment gateways integration."""
    integration = PaymentGatewaysIntegration(
        paypal_client_id=paypal_client_id,
        paypal_client_secret=paypal_client_secret,
        wise_api_token=wise_api_token,
        environment=environment
    )
    await integration._ensure_session()
    return integration


async def process_multi_gateway_payment(
    integration: PaymentGatewaysIntegration,
    amount: Decimal,
    currency: CurrencyCode,
    recipient_info: Dict[str, Any],
    backup_gateways: List[PaymentGateway] = None
) -> PaymentTransaction:
    """Process payment with automatic failover to backup gateways."""
    primary_gateway = PaymentGateway.PAYPAL
    backup_gateways = backup_gateways or [PaymentGateway.WISE, PaymentGateway.CRYPTO]
    
    gateways_to_try = [primary_gateway] + backup_gateways
    
    for gateway in gateways_to_try:
        try:
            transaction = await integration.process_payment(
                gateway=gateway,
                amount=amount,
                currency=currency,
                payment_method=PaymentMethod.DIGITAL_WALLET,
                sender_info={"source": "ainflue_platform"},
                recipient_info=recipient_info
            )
            
            logger.info(f"Payment successful via {gateway}: {transaction.transaction_id}")
            return transaction
        
        except Exception as e:
            logger.warning(f"Payment failed via {gateway}: {e}")
            continue
    
    raise Exception("All payment gateways failed")


if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        import os
        
        async with PaymentGatewaysIntegration(
            paypal_client_id=os.getenv("PAYPAL_CLIENT_ID"),
            paypal_client_secret=os.getenv("PAYPAL_CLIENT_SECRET"),
            wise_api_token=os.getenv("WISE_API_TOKEN"),
            environment="sandbox"
        ) as gateways:
            # Initialize accounts
            try:
                paypal_account = await gateways.initialize_paypal_account()
                print(f"PayPal account: {paypal_account.account_name}")
            except Exception as e:
                print(f"PayPal initialization failed: {e}")
            
            # Get exchange rates
            try:
                rate = await gateways.get_exchange_rates(CurrencyCode.USD, CurrencyCode.EUR)
                print(f"USD to EUR rate: {rate.rate}")
            except Exception as e:
                print(f"Exchange rate failed: {e}")
            
            # Check usage stats
            stats = gateways.get_usage_stats()
            print(f"Usage stats: {stats}")
    
    asyncio.run(main())