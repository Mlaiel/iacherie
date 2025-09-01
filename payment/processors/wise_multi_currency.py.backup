"""🌍 Wise Multi-Currency Payment Processor
========================================

Advanced Wise (formerly TransferWise) payment processor for international
multi-currency transactions with real-time exchange rates and low fees.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import uuid
import hashlib
import hmac
import json

logger = logging.getLogger(__name__)


class WiseEnvironment(Enum):
    """Wise environment types"""
    SANDBOX = "sandbox"
    LIVE = "live"


class WiseAccountType(Enum):
    """Wise account types"""
    PERSONAL = "personal"
    BUSINESS = "business"


class WiseProfileType(Enum):
    """Wise profile types"""
    PERSONAL = "personal"
    BUSINESS = "business"


class TransferPurpose(Enum):
    """Transfer purpose codes"""
    VERIFICATION_OF_DEPOSIT = "verification.of.deposit"
    FAMILY_SUPPORT = "family.support"
    EDUCATION = "education"
    BUSINESS_SERVICES = "business.services"
    LICENSING_FEES = "licensing.fees"
    ROYALTIES = "royalties"
    DIGITAL_SERVICES = "digital.services"


class WiseCurrency:
    """Supported Wise currencies with metadata"""
    CURRENCIES = {
        "USD": {"name": "US Dollar", "symbol": "$", "decimals": 2},
        "EUR": {"name": "Euro", "symbol": "€", "decimals": 2},
        "GBP": {"name": "British Pound", "symbol": "£", "decimals": 2},
        "CAD": {"name": "Canadian Dollar", "symbol": "C$", "decimals": 2},
        "AUD": {"name": "Australian Dollar", "symbol": "A$", "decimals": 2},
        "JPY": {"name": "Japanese Yen", "symbol": "¥", "decimals": 0},
        "CHF": {"name": "Swiss Franc", "symbol": "CHF", "decimals": 2},
        "SEK": {"name": "Swedish Krona", "symbol": "SEK", "decimals": 2},
        "NOK": {"name": "Norwegian Krone", "symbol": "NOK", "decimals": 2},
        "DKK": {"name": "Danish Krone", "symbol": "DKK", "decimals": 2},
        "PLN": {"name": "Polish Zloty", "symbol": "PLN", "decimals": 2},
        "CZK": {"name": "Czech Koruna", "symbol": "CZK", "decimals": 2},
        "HUF": {"name": "Hungarian Forint", "symbol": "HUF", "decimals": 2},
        "BGN": {"name": "Bulgarian Lev", "symbol": "BGN", "decimals": 2},
        "RON": {"name": "Romanian Leu", "symbol": "RON", "decimals": 2},
        "HRK": {"name": "Croatian Kuna", "symbol": "HRK", "decimals": 2},
        "TRY": {"name": "Turkish Lira", "symbol": "TRY", "decimals": 2},
        "BRL": {"name": "Brazilian Real", "symbol": "R$", "decimals": 2},
        "MXN": {"name": "Mexican Peso", "symbol": "MX$", "decimals": 2},
        "ARS": {"name": "Argentine Peso", "symbol": "ARS", "decimals": 2},
        "INR": {"name": "Indian Rupee", "symbol": "₹", "decimals": 2},
        "CNY": {"name": "Chinese Yuan", "symbol": "¥", "decimals": 2},
        "HKD": {"name": "Hong Kong Dollar", "symbol": "HK$", "decimals": 2},
        "SGD": {"name": "Singapore Dollar", "symbol": "S$", "decimals": 2},
        "KRW": {"name": "South Korean Won", "symbol": "₩", "decimals": 0},
        "THB": {"name": "Thai Baht", "symbol": "฿", "decimals": 2},
        "IDR": {"name": "Indonesian Rupiah", "symbol": "Rp", "decimals": 2},
        "MYR": {"name": "Malaysian Ringgit", "symbol": "RM", "decimals": 2},
        "PHP": {"name": "Philippine Peso", "symbol": "₱", "decimals": 2},
        "ZAR": {"name": "South African Rand", "symbol": "R", "decimals": 2},
        "EGP": {"name": "Egyptian Pound", "symbol": "E£", "decimals": 2},
        "AED": {"name": "UAE Dirham", "symbol": "AED", "decimals": 2},
        "SAR": {"name": "Saudi Riyal", "symbol": "SAR", "decimals": 2},
        "ILS": {"name": "Israeli Shekel", "symbol": "₪", "decimals": 2},
        "RUB": {"name": "Russian Ruble", "symbol": "₽", "decimals": 2},
        "UAH": {"name": "Ukrainian Hryvnia", "symbol": "₴", "decimals": 2}
    }


@dataclass
class WiseProfile:
    """Wise profile information"""
    id: int
    type: WiseProfileType
    details: Dict[str, Any]


@dataclass
class WiseAccount:
    """Wise account details"""
    id: int
    profile_id: int
    account_holder_name: str
    currency: str
    country: str
    type: str
    details: Dict[str, Any]


@dataclass
class WiseExchangeRate:
    """Real-time exchange rate"""
    source: str
    target: str
    rate: Decimal
    time: datetime
    type: str = "FIXED"


@dataclass
class WiseTransfer:
    """Wise transfer details"""
    id: int
    profile_id: int
    account_id: int
    quote_id: str
    status: str
    reference: str
    rate: Decimal
    created: datetime
    business: Optional[str] = None
    transfer_request: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    has_active_issues: bool = False
    source_currency: str = ""
    target_currency: str = ""
    source_value: Decimal = Decimal("0")
    target_value: Decimal = Decimal("0")
    fee: Decimal = Decimal("0")


class WiseMultiCurrencyProcessor:
    """
    Wise Multi-Currency payment processor
    
    Handles international transfers, currency conversion, and multi-currency
    account management with real-time exchange rates and minimal fees.
    """
    
    def __init__(
        self,
        api_token: str,
        environment: WiseEnvironment = WiseEnvironment.SANDBOX,
        webhook_secret: Optional[str] = None
    ):
        """Initialize Wise Multi-Currency processor"""
        self.api_token = api_token
        self.environment = environment
        self.webhook_secret = webhook_secret
        self.logger = logging.getLogger(__name__)
        
        # Wise fee structure (percentage-based)
        self.base_fee_percent = Decimal("0.0035")  # 0.35% base fee
        self.min_fee = Decimal("0.50")  # Minimum fee $0.50
        self.max_fee = Decimal("15.00")  # Maximum fee $15.00
        
        # Base URLs
        self.base_urls = {
            WiseEnvironment.SANDBOX: "https://api.sandbox.transferwise.tech",
            WiseEnvironment.LIVE: "https://api.transferwise.com"
        }
    
    async def get_profiles(self) -> List[WiseProfile]:
        """Get user profiles"""
        try:
            # Simulate API call
            await asyncio.sleep(0.1)
            
            # Mock profile data
            profiles = [
                WiseProfile(
                    id=123456,
                    type=WiseProfileType.BUSINESS,
                    details={
                        "firstName": "Ainflue",
                        "lastName": "Platform",
                        "businessName": "Ainflue Inc.",
                        "businessCategory": "SOFTWARE_DEVELOPMENT",
                        "companyType": "LIMITED"
                    }
                )
            ]
            
            return profiles
            
        except Exception as e:
            self.logger.error(f"Failed to get Wise profiles: {e}")
            raise
    
    async def get_accounts(self, profile_id: int) -> List[WiseAccount]:
        """Get borderless accounts for a profile"""
        try:
            # Simulate API call
            await asyncio.sleep(0.1)
            
            # Mock account data for major currencies
            accounts = []
            for currency in ["USD", "EUR", "GBP", "CAD", "AUD"]:
                account = WiseAccount(
                    id=int(f"{profile_id}{hash(currency) % 1000}"),
                    profile_id=profile_id,
                    account_holder_name="Ainflue Platform",
                    currency=currency,
                    country="US" if currency == "USD" else "GB",
                    type="checking",
                    details={
                        "account_number": f"ACC{uuid.uuid4().hex[:10].upper()}",
                        "routing_number": "026073150" if currency == "USD" else None,
                        "iban": f"GB{uuid.uuid4().hex[:10].upper()}" if currency != "USD" else None,
                        "bic": "TRWIGB2L" if currency != "USD" else None
                    }
                )
                accounts.append(account)
            
            return accounts
            
        except Exception as e:
            self.logger.error(f"Failed to get Wise accounts: {e}")
            raise
    
    async def get_exchange_rate(
        self,
        source_currency: str,
        target_currency: str,
        amount: Optional[Decimal] = None
    ) -> WiseExchangeRate:
        """Get real-time exchange rate"""
        try:
            # Simulate API call
            await asyncio.sleep(0.05)
            
            # Mock exchange rates (in production, use real Wise API)
            mock_rates = {
                ("USD", "EUR"): Decimal("0.8456"),
                ("EUR", "USD"): Decimal("1.1826"),
                ("USD", "GBP"): Decimal("0.7342"),
                ("GBP", "USD"): Decimal("1.3621"),
                ("EUR", "GBP"): Decimal("0.8689"),
                ("GBP", "EUR"): Decimal("1.1509"),
                ("USD", "CAD"): Decimal("1.3245"),
                ("CAD", "USD"): Decimal("0.7550"),
                ("USD", "AUD"): Decimal("1.4578"),
                ("AUD", "USD"): Decimal("0.6860"),
                ("USD", "JPY"): Decimal("149.25"),
                ("JPY", "USD"): Decimal("0.0067"),
                ("EUR", "JPY"): Decimal("162.45"),
                ("JPY", "EUR"): Decimal("0.0062")
            }
            
            rate = mock_rates.get((source_currency, target_currency), Decimal("1.0"))
            
            # Add small random variation to simulate real-time rates
            import random
            variation = Decimal(str(random.uniform(-0.001, 0.001)))
            rate = rate + (rate * variation)
            rate = rate.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            
            exchange_rate = WiseExchangeRate(
                source=source_currency,
                target=target_currency,
                rate=rate,
                time=datetime.now(),
                type="FIXED"
            )
            
            return exchange_rate
            
        except Exception as e:
            self.logger.error(f"Failed to get exchange rate: {e}")
            raise
    
    async def create_quote(
        self,
        profile_id: int,
        source_currency: str,
        target_currency: str,
        source_amount: Optional[Decimal] = None,
        target_amount: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Create a transfer quote"""
        try:
            if not source_amount and not target_amount:
                raise ValueError("Either source_amount or target_amount must be specified")
            
            # Get current exchange rate
            exchange_rate = await self.get_exchange_rate(source_currency, target_currency)
            
            # Calculate amounts and fees
            if source_amount:
                fee = self.calculate_fee(source_amount, source_currency, target_currency)
                amount_after_fee = source_amount - fee
                target_amount = amount_after_fee * exchange_rate.rate
            else:
                # Calculate backwards from target amount
                temp_source = target_amount / exchange_rate.rate
                fee = self.calculate_fee(temp_source, source_currency, target_currency)
                source_amount = temp_source + fee
                amount_after_fee = source_amount - fee
            
            quote_id = f"QUOTE-{uuid.uuid4().hex[:13].upper()}"
            
            quote = {
                "id": quote_id,
                "source": source_currency,
                "target": target_currency,
                "sourceAmount": float(source_amount),
                "targetAmount": float(target_amount),
                "fee": float(fee),
                "rate": float(exchange_rate.rate),
                "created": datetime.now().isoformat(),
                "rateExpiryTime": (datetime.now() + timedelta(minutes=30)).isoformat(),
                "profile": profile_id,
                "rateType": "FIXED",
                "deliveryEstimate": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            
            self.logger.info(f"Created Wise quote: {quote_id}")
            return quote
            
        except Exception as e:
            self.logger.error(f"Failed to create Wise quote: {e}")
            raise
    
    async def create_transfer(
        self,
        quote_id: str,
        target_account: int,
        reference: str,
        transfer_purpose: TransferPurpose = TransferPurpose.DIGITAL_SERVICES
    ) -> WiseTransfer:
        """Create a transfer from quote"""
        try:
            transfer_id = int(f"1{uuid.uuid4().hex[:8]}", 16) % 10000000
            
            transfer = WiseTransfer(
                id=transfer_id,
                profile_id=123456,  # Mock profile ID
                account_id=target_account,
                quote_id=quote_id,
                status="incoming_payment_waiting",
                reference=reference,
                rate=Decimal("0.8456"),  # Mock rate
                created=datetime.now(),
                business=transfer_purpose.value,
                details={
                    "reference": reference,
                    "transferPurpose": transfer_purpose.value,
                    "sourceOfFunds": "verification.of.deposit"
                }
            )
            
            self.logger.info(f"Created Wise transfer: {transfer_id}")
            return transfer
            
        except Exception as e:
            self.logger.error(f"Failed to create Wise transfer: {e}")
            raise
    
    async def fund_transfer(
        self,
        transfer_id: int,
        profile_id: int
    ) -> Dict[str, Any]:
        """Fund a transfer (simulate bank transfer or card payment)"""
        try:
            # Simulate funding process
            await asyncio.sleep(0.2)
            
            # In production, this would handle actual funding
            # For now, simulate immediate funding success
            
            return {
                "success": True,
                "transfer_id": transfer_id,
                "status": "processing",
                "funding_method": "balance",
                "funding_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to fund Wise transfer: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_transfer_status(self, transfer_id: int) -> Dict[str, Any]:
        """Get current transfer status"""
        try:
            # Simulate API call
            await asyncio.sleep(0.1)
            
            # Mock transfer status progression
            statuses = [
                "incoming_payment_waiting",
                "processing",
                "funds_converted",
                "outgoing_payment_sent",
                "delivered"
            ]
            
            # Simulate random status for demo
            import random
            status = random.choice(statuses)
            
            return {
                "id": transfer_id,
                "status": status,
                "rate": 0.8456,
                "created": datetime.now().isoformat(),
                "business": "digital.services",
                "hasActiveIssues": False,
                "sourceCurrency": "USD",
                "targetCurrency": "EUR",
                "sourceValue": 100.00,
                "targetValue": 84.56,
                "fee": 0.65
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get transfer status: {e}")
            raise
    
    async def cancel_transfer(self, transfer_id: int) -> Dict[str, Any]:
        """Cancel a transfer (if still possible)"""
        try:
            # Check if transfer can be cancelled
            status = await self.get_transfer_status(transfer_id)
            
            if status["status"] in ["delivered", "outgoing_payment_sent"]:
                return {
                    "success": False,
                    "error": "Transfer cannot be cancelled at this stage"
                }
            
            return {
                "success": True,
                "transfer_id": transfer_id,
                "status": "cancelled",
                "cancelled_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to cancel Wise transfer: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_webhook(self, headers: Dict[str, str], body: str) -> Dict[str, Any]:
        """Handle Wise webhook events"""
        try:
            # Verify webhook signature
            if not self._verify_webhook_signature(headers, body):
                return {"success": False, "error": "Invalid webhook signature"}
            
            event = json.loads(body)
            event_type = event.get("event_type")
            
            # Handle different event types
            if event_type == "transfers#state-change":
                return await self._handle_transfer_state_change(event["data"])
            elif event_type == "transfers#active-cases":
                return await self._handle_transfer_issues(event["data"])
            elif event_type == "balances#credit":
                return await self._handle_balance_credit(event["data"])
            elif event_type == "balances#debit":
                return await self._handle_balance_debit(event["data"])
            else:
                return {"success": True, "message": f"Unhandled event: {event_type}"}
                
        except Exception as e:
            self.logger.error(f"Wise webhook handling failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _verify_webhook_signature(self, headers: Dict[str, str], body: str) -> bool:
        """Verify Wise webhook signature"""
        try:
            if not self.webhook_secret:
                return True  # Skip verification if no secret configured
            
            signature = headers.get("X-Signature-SHA256", "")
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                body.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            self.logger.error(f"Wise signature verification failed: {e}")
            return False
    
    async def _handle_transfer_state_change(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle transfer status change event"""
        transfer_id = data.get("resource", {}).get("id")
        new_status = data.get("current_state")
        
        self.logger.info(f"Wise transfer {transfer_id} status changed to: {new_status}")
        return {"success": True, "action": "transfer_status_updated"}
    
    async def _handle_transfer_issues(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle transfer issues event"""
        transfer_id = data.get("resource", {}).get("id")
        
        self.logger.warning(f"Wise transfer {transfer_id} has active issues")
        return {"success": True, "action": "transfer_issues_detected"}
    
    async def _handle_balance_credit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle balance credit event"""
        self.logger.info("Wise account balance credited")
        return {"success": True, "action": "balance_credited"}
    
    async def _handle_balance_debit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle balance debit event"""
        self.logger.info("Wise account balance debited")
        return {"success": True, "action": "balance_debited"}
    
    def calculate_fee(
        self,
        amount: Decimal,
        source_currency: str,
        target_currency: str
    ) -> Decimal:
        """Calculate Wise transfer fee"""
        # Base percentage fee
        fee = amount * self.base_fee_percent
        
        # Apply minimum and maximum fee limits
        fee = max(fee, self.min_fee)
        fee = min(fee, self.max_fee)
        
        # Additional fees for certain currency pairs
        exotic_currencies = {"THB", "IDR", "PHP", "MYR", "ZAR", "EGP", "AED", "SAR"}
        if source_currency in exotic_currencies or target_currency in exotic_currencies:
            fee += amount * Decimal("0.002")  # Additional 0.2% for exotic currencies
        
        return fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    def get_supported_currencies(self) -> Dict[str, Dict[str, Any]]:
        """Get all supported currencies"""
        return WiseCurrency.CURRENCIES


# Export the main class
__all__ = [
    "WiseMultiCurrencyProcessor", 
    "WiseProfile", 
    "WiseAccount", 
    "WiseExchangeRate", 
    "WiseTransfer",
    "WiseCurrency"
]