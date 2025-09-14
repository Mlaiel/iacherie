"""
Wallet Config module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Wallet Configuration Module
import asyncio

====================================

Enterprise-grade digital wallet configuration for the Ainflue platform.
Comprehensive wallet management with multi-currency support, transaction
processing, security features, and advanced analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved
"""

import os
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

class WalletType(str, Enum):
    """Types of wallets"""
    PERSONAL = "personal"                   # Personal wallet
    BUSINESS = "business"                   # Business wallet
    SHARED = "shared"                       # Shared wallet
    ESCROW = "escrow"                       # Escrow wallet
    SAVINGS = "savings"                     # Savings wallet
    PROMOTIONAL = "promotional"             # Promotional credits wallet
    REWARD = "reward"                       # Reward points wallet
    CASHBACK = "cashback"                   # Cashback wallet

class WalletStatus(str, Enum):
    """Wallet status"""
    ACTIVE = "active"                       # Active wallet
    INACTIVE = "inactive"                   # Inactive wallet
    SUSPENDED = "suspended"                 # Suspended wallet
    FROZEN = "frozen"                       # Frozen wallet
    CLOSED = "closed"                       # Closed wallet
    PENDING_VERIFICATION = "pending_verification"  # Pending verification
    RESTRICTED = "restricted"               # Restricted access

class TransactionType(str, Enum):
    """Transaction types"""
    DEPOSIT = "deposit"                     # Deposit to wallet
    WITHDRAWAL = "withdrawal"               # Withdrawal from wallet
    TRANSFER_IN = "transfer_in"            # Transfer from another wallet
    TRANSFER_OUT = "transfer_out"          # Transfer to another wallet
    PAYMENT = "payment"                     # Payment to merchant
    REFUND = "refund"                       # Refund received
    CASHBACK = "cashback"                   # Cashback earned
    REWARD = "reward"                       # Reward received
    FEE = "fee"                            # Fee charged
    ADJUSTMENT = "adjustment"               # Balance adjustment

class TransactionStatus(str, Enum):
    """Transaction status"""
    PENDING = "pending"                     # Pending processing
    PROCESSING = "processing"               # Being processed
    COMPLETED = "completed"                 # Successfully completed
    FAILED = "failed"                       # Failed transaction
    CANCELLED = "cancelled"                 # Cancelled transaction
    EXPIRED = "expired"                     # Expired transaction
    DISPUTED = "disputed"                   # Under dispute

class CurrencyType(str, Enum):
    """Currency types"""
    FIAT = "fiat"                          # Fiat currency (EUR, USD, etc.)
    CRYPTO = "crypto"                      # Cryptocurrency
    TOKEN = "token"                        # Platform token
    POINTS = "points"                      # Reward points
    CREDITS = "credits"                    # Platform credits

@dataclass
class WalletBalance:
    """Wallet balance for a specific currency"""
    currency: str
    currency_type: CurrencyType
    available_balance: Decimal = Decimal('0')
    pending_balance: Decimal = Decimal('0')
    reserved_balance: Decimal = Decimal('0')
    total_balance: Decimal = Decimal('0')
    last_updated: datetime = field(default_factory=datetime.now)
    
    def calculate_total_balance(self) -> Decimal:
        """Calculate total balance"""
        self.total_balance = self.available_balance + self.pending_balance + self.reserved_balance
        self.last_updated = datetime.now()
        return self.total_balance
    
    def update_balance(self, amount: Decimal, balance_type: str = "available") -> bool:
        """Update balance"""
        try:
            if balance_type == "available":
                self.available_balance += amount
            elif balance_type == "pending":
                self.pending_balance += amount
            elif balance_type == "reserved":
                self.reserved_balance += amount
            
            self.calculate_total_balance()
            return True
        except Exception:
            return False
    
    def can_debit(self, amount: Decimal) -> bool:
        """Check if amount can be debited"""
        return self.available_balance >= amount
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert balance to dictionary"""
        return {
            "currency": self.currency,
            "currency_type": self.currency_type.value,
            "available_balance": float(self.available_balance),
            "pending_balance": float(self.pending_balance),
            "reserved_balance": float(self.reserved_balance),
            "total_balance": float(self.total_balance),
            "last_updated": self.last_updated.isoformat()
        }

@dataclass
class WalletTransaction:
    """Wallet transaction record"""
    transaction_id: str
    wallet_id: str
    transaction_type: TransactionType
    currency: str
    amount: Decimal
    fee: Decimal = Decimal('0')
    net_amount: Decimal = Decimal('0')
    status: TransactionStatus = TransactionStatus.PENDING
    description: str = ""
    reference_id: Optional[str] = None
    from_wallet_id: Optional[str] = None
    to_wallet_id: Optional[str] = None
    external_reference: Optional[str] = None
    created_date: datetime = field(default_factory=datetime.now)
    processed_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_net_amount(self) -> Decimal:
        """Calculate net amount after fees"""
        if self.transaction_type in [TransactionType.DEPOSIT, TransactionType.TRANSFER_IN, 
                                   TransactionType.REFUND, TransactionType.CASHBACK, TransactionType.REWARD]:
            self.net_amount = self.amount - self.fee
        else:
            self.net_amount = self.amount + self.fee
        return self.net_amount
    
    def update_status(self, new_status: TransactionStatus, notes: str = "") -> None:
        """Update transaction status"""
        self.status = new_status
        
        if new_status == TransactionStatus.PROCESSING:
            self.processed_date = datetime.now()
        elif new_status == TransactionStatus.COMPLETED:
            self.completed_date = datetime.now()
        
        if notes:
            if "notes" not in self.metadata:
                self.metadata["notes"] = []
            self.metadata["notes"].append({
                "timestamp": datetime.now().isoformat(),
                "status": new_status.value,
                "note": notes
            })
    
    def get_processing_time(self) -> Optional[int]:
        """Get processing time in seconds"""
        if self.completed_date and self.created_date:
            return int((self.completed_date - self.created_date).total_seconds())
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary"""
        return {
            "transaction_id": self.transaction_id,
            "wallet_id": self.wallet_id,
            "transaction_type": self.transaction_type.value,
            "currency": self.currency,
            "amount": float(self.amount),
            "fee": float(self.fee),
            "net_amount": float(self.net_amount),
            "status": self.status.value,
            "description": self.description,
            "reference_id": self.reference_id,
            "from_wallet_id": self.from_wallet_id,
            "to_wallet_id": self.to_wallet_id,
            "external_reference": self.external_reference,
            "created_date": self.created_date.isoformat(),
            "processed_date": self.processed_date.isoformat() if self.processed_date else None,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "processing_time_seconds": self.get_processing_time(),
            "metadata": self.metadata
        }

@dataclass
class DigitalWallet:
    """Digital wallet"""
    wallet_id: str
    user_id: str
    wallet_type: WalletType
    wallet_name: str
    status: WalletStatus = WalletStatus.ACTIVE
    balances: Dict[str, WalletBalance] = field(default_factory=dict)
    daily_limit: Decimal = Decimal('10000.0')    # EUR equivalent
    monthly_limit: Decimal = Decimal('100000.0')  # EUR equivalent
    transaction_limit: Decimal = Decimal('5000.0') # EUR equivalent
    created_date: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    verification_level: int = 1  # 1-5 verification levels
    settings: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_currency(self, currency: str, currency_type: CurrencyType) -> WalletBalance:
        """Add currency to wallet"""
        if currency not in self.balances:
            self.balances[currency] = WalletBalance(
                currency=currency,
                currency_type=currency_type
            )
        return self.balances[currency]
    
    def get_balance(self, currency: str) -> Optional[WalletBalance]:
        """Get balance for currency"""
        return self.balances.get(currency)
    
    def get_total_balance_usd(self, exchange_rates: Dict[str, Decimal]) -> Decimal:
        """Get total balance in USD equivalent"""
        total_usd = Decimal('0')
        
        for currency, balance in self.balances.items():
            rate = exchange_rates.get(currency, Decimal('1'))
            total_usd += balance.total_balance * rate
        
        return total_usd
    
    def can_transact(self, amount: Decimal, currency: str, transaction_type: TransactionType) -> Dict[str, Any]:
        """Check if transaction is allowed"""
        check_result = {
            "allowed": False,
            "reason": None
        }
        
        # Check wallet status
        if self.status != WalletStatus.ACTIVE:
            check_result["reason"] = f"Wallet status is {self.status.value}"
            return check_result
        
        # Check balance for outgoing transactions
        if transaction_type in [TransactionType.WITHDRAWAL, TransactionType.TRANSFER_OUT, TransactionType.PAYMENT]:
            balance = self.get_balance(currency)
            if not balance or not balance.can_debit(amount):
                check_result["reason"] = "Insufficient balance"
                return check_result
        
        # Check transaction limits
        if amount > self.transaction_limit:
            check_result["reason"] = "Transaction limit exceeded"
            return check_result
        
        # Check daily/monthly limits (simplified)
        # In real implementation, would check actual daily/monthly usage
        
        check_result["allowed"] = True
        return check_result
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get wallet summary"""
        return {
            "wallet_id": self.wallet_id,
            "user_id": self.user_id,
            "wallet_type": self.wallet_type.value,
            "wallet_name": self.wallet_name,
            "status": self.status.value,
            "currencies_count": len(self.balances),
            "total_currencies": list(self.balances.keys()),
            "verification_level": self.verification_level,
            "created_date": self.created_date.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "balances": {currency: balance.to_dict() for currency, balance in self.balances.items()}
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert wallet to dictionary"""
        return {
            "wallet_id": self.wallet_id,
            "user_id": self.user_id,
            "wallet_type": self.wallet_type.value,
            "wallet_name": self.wallet_name,
            "status": self.status.value,
            "balances": {currency: balance.to_dict() for currency, balance in self.balances.items()},
            "daily_limit": float(self.daily_limit),
            "monthly_limit": float(self.monthly_limit),
            "transaction_limit": float(self.transaction_limit),
            "created_date": self.created_date.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "verification_level": self.verification_level,
            "settings": self.settings,
            "metadata": self.metadata
        }

@dataclass
class WalletSecurityConfig:
    """Wallet security configuration"""
    enabled: bool = True
    
    # Authentication
    authentication: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "multi_factor_auth": True,
        "biometric_auth": True,
        "pin_protection": True,
        "session_timeout": 1800,  # 30 minutes
        "login_attempts_limit": 5,
        "account_lockout_duration": 3600,  # 1 hour
        "password_complexity": True
    })
    
    # Transaction security
    transaction_security: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "transaction_verification": True,
        "high_value_confirmation": True,
        "fraud_detection": True,
        "velocity_checking": True,
        "geographic_restrictions": True,
        "device_binding": True,
        "time_based_restrictions": True
    })
    
    # Encryption
    encryption: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "data_encryption": True,
        "transmission_encryption": True,
        "key_management": True,
        "hsm_integration": True,
        "field_level_encryption": True,
        "backup_encryption": True
    })
    
    # Privacy
    privacy: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "data_anonymization": True,
        "pii_protection": True,
        "gdpr_compliance": True,
        "data_retention": True,
        "consent_management": True,
        "data_portability": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get wallet security configuration"""
        return {
            "enabled": self.enabled,
            "authentication": self.authentication,
            "transaction_security": self.transaction_security,
            "encryption": self.encryption,
            "privacy": self.privacy
        }

@dataclass
class WalletFeaturesConfig:
    """Wallet features configuration"""
    enabled: bool = True
    
    # Core features
    core_features: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "multi_currency": True,
        "cryptocurrency_support": True,
        "real_time_balance": True,
        "transaction_history": True,
        "spending_analytics": True,
        "budget_management": True,
        "savings_goals": True
    })
    
    # Advanced features
    advanced_features: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "auto_conversion": True,
        "scheduled_payments": True,
        "recurring_transactions": True,
        "investment_options": True,
        "lending_borrowing": True,
        "staking_rewards": True,
        "yield_farming": True
    })
    
    # Social features
    social_features: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "peer_to_peer_transfers": True,
        "split_payments": True,
        "group_wallets": True,
        "gift_cards": True,
        "charitable_donations": True,
        "social_payments": True
    })
    
    # Business features
    business_features: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "invoice_management": True,
        "payment_requests": True,
        "bulk_payments": True,
        "expense_tracking": True,
        "tax_reporting": True,
        "api_access": True,
        "webhook_notifications": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get wallet features configuration"""
        return {
            "enabled": self.enabled,
            "core_features": self.core_features,
            "advanced_features": self.advanced_features,
            "social_features": self.social_features,
            "business_features": self.business_features
        }

@dataclass
class WalletAnalyticsConfig:
    """Wallet analytics configuration"""
    enabled: bool = True
    
    # Analytics engine
    analytics_engine: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "real_time_analytics": True,
        "historical_analysis": True,
        "predictive_analytics": True,
        "behavioral_analysis": True,
        "spending_patterns": True,
        "transaction_categorization": True,
        "fraud_detection": True
    })
    
    # Reporting
    reporting: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "automated_reports": True,
        "custom_reports": True,
        "financial_statements": True,
        "tax_reports": True,
        "compliance_reports": True,
        "performance_dashboards": True,
        "executive_summaries": True
    })
    
    # Insights
    insights: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "spending_insights": True,
        "saving_recommendations": True,
        "investment_advice": True,
        "cashflow_optimization": True,
        "budget_alerts": True,
        "goal_tracking": True,
        "financial_health_score": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get wallet analytics configuration"""
        return {
            "enabled": self.enabled,
            "analytics_engine": self.analytics_engine,
            "reporting": self.reporting,
            "insights": self.insights
        }

class WalletConfiguration:
    """Main wallet configuration manager"""
    
    def __init__(self) -> None:
        """Initialize wallet configuration"""
        # Configuration components
        self.wallet_security = WalletSecurityConfig()
        self.wallet_features = WalletFeaturesConfig()
        self.wallet_analytics = WalletAnalyticsConfig()
        
        # Data storage
        self.wallets: List[DigitalWallet] = []
        self.transactions: List[WalletTransaction] = []
        
        # Global wallet settings
        self.wallet_system_enabled = True
        self.multi_currency_enabled = True
        self.cryptocurrency_enabled = True
        self.auto_conversion_enabled = True
        
        # Default limits
        self.default_limits = {
            "daily_limit": Decimal('10000.0'),     # EUR
            "monthly_limit": Decimal('100000.0'),   # EUR
            "transaction_limit": Decimal('5000.0'), # EUR
            "withdrawal_limit": Decimal('2000.0')   # EUR
        }
        
        # Transaction fees
        self.transaction_fees = {
            TransactionType.DEPOSIT: Decimal('0'),
            TransactionType.WITHDRAWAL: Decimal('2.50'),    # EUR
            TransactionType.TRANSFER_IN: Decimal('0'),
            TransactionType.TRANSFER_OUT: Decimal('1.00'),  # EUR
            TransactionType.PAYMENT: Decimal('0.50'),       # EUR
            TransactionType.ADJUSTMENT: Decimal('0')
        }
        
        # Supported currencies
        self.supported_currencies = {
            "fiat": ["EUR", "USD", "GBP", "CHF", "JPY", "CAD", "AUD"],
            "crypto": ["BTC", "ETH", "LTC", "ADA", "DOT", "USDT", "USDC"],
            "tokens": ["AINF", "CREATOR", "INFLUENCE"],
            "points": ["REWARD_POINTS", "LOYALTY_POINTS"],
            "credits": ["PLATFORM_CREDITS", "PROMO_CREDITS"]
        }
        
        # Exchange rate providers
        self.exchange_providers = {
            "fiat_rates": "exchangerate-api.com",
            "crypto_rates": "coinapi.io",
            "update_frequency": 300  # 5 minutes
        }
        
        # Verification levels
        self.verification_levels = {
            1: {"daily_limit": 1000.0, "monthly_limit": 10000.0},
            2: {"daily_limit": 5000.0, "monthly_limit": 50000.0},
            3: {"daily_limit": 10000.0, "monthly_limit": 100000.0},
            4: {"daily_limit": 25000.0, "monthly_limit": 250000.0},
            5: {"daily_limit": 100000.0, "monthly_limit": 1000000.0}
        }
        
        # Security settings
        self.security_settings = {
            "session_timeout": 1800,        # 30 minutes
            "max_login_attempts": 5,
            "lockout_duration": 3600,       # 1 hour
            "require_mfa": True,
            "require_biometric": False
        }
        
        # Integration settings
        self.integration_settings = {
            "banking_integration": True,
            "card_integration": True,
            "crypto_exchange_integration": True,
            "payment_gateway_integration": True,
            "merchant_integration": True
        }
    
    def create_wallet(self, wallet_data: Dict[str, Any]) -> DigitalWallet:
        """Create new wallet"""
        
        wallet = DigitalWallet(
            wallet_id=f"wallet_{uuid.uuid4().hex[:12]}",
            user_id=wallet_data.get("user_id", ""),
            wallet_type=WalletType(wallet_data.get("wallet_type", "personal")),
            wallet_name=wallet_data.get("wallet_name", "Default Wallet"),
            daily_limit=Decimal(str(wallet_data.get("daily_limit", str(self.default_limits["daily_limit"])))),
            monthly_limit=Decimal(str(wallet_data.get("monthly_limit", str(self.default_limits["monthly_limit"])))),
            transaction_limit=Decimal(str(wallet_data.get("transaction_limit", str(self.default_limits["transaction_limit"])))),
            verification_level=wallet_data.get("verification_level", 1),
            settings=wallet_data.get("settings", {}),
            metadata=wallet_data.get("metadata", {})
        )
        
        # Add default currencies
        default_currencies = wallet_data.get("default_currencies", ["EUR"])
        for currency in default_currencies:
            currency_type = self._get_currency_type(currency)
            wallet.add_currency(currency, currency_type)
        
        self.wallets.append(wallet)
        return wallet
    
    async def process_transaction(self, transaction_data: Dict[str, Any]) -> WalletTransaction:
        """Process wallet transaction"""
        
        transaction = WalletTransaction(
            transaction_id=f"txn_{uuid.uuid4().hex[:12]}",
            wallet_id=transaction_data.get("wallet_id", ""),
            transaction_type=TransactionType(transaction_data.get("transaction_type", "deposit")),
            currency=transaction_data.get("currency", "EUR"),
            amount=Decimal(str(transaction_data.get("amount", "0"))),
            fee=Decimal(str(transaction_data.get("fee", "0"))),
            description=transaction_data.get("description", ""),
            reference_id=transaction_data.get("reference_id"),
            from_wallet_id=transaction_data.get("from_wallet_id"),
            to_wallet_id=transaction_data.get("to_wallet_id"),
            external_reference=transaction_data.get("external_reference"),
            metadata=transaction_data.get("metadata", {})
        )
        
        # Calculate transaction fee if not provided
        if transaction.fee == 0:
            transaction.fee = self.transaction_fees.get(transaction.transaction_type, Decimal('0'))
        
        # Calculate net amount
        transaction.calculate_net_amount()
        
        # Validate transaction
        validation_result = await self._validate_transaction(transaction)
        if not validation_result["valid"]:
            transaction.update_status(TransactionStatus.FAILED, validation_result["reason"])
            self.transactions.append(transaction)
            return transaction
        
        # Process transaction
        processing_result = await self._execute_transaction(transaction)
        
        if processing_result["success"]:
            transaction.update_status(TransactionStatus.COMPLETED, "Transaction completed successfully")
        else:
            transaction.update_status(TransactionStatus.FAILED, processing_result.get("error", "Transaction failed"))
        
        self.transactions.append(transaction)
        return transaction
    
    async def transfer_between_wallets(self, transfer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transfer funds between wallets"""
        
        transfer_result = {
            "transfer_id": f"transfer_{uuid.uuid4().hex[:8]}",
            "success": False,
            "transactions": [],
            "error": None
        }
        
        try:
            from_wallet_id = transfer_data.get("from_wallet_id")
            to_wallet_id = transfer_data.get("to_wallet_id")
            amount = Decimal(str(transfer_data.get("amount", "0")))
            currency = transfer_data.get("currency", "EUR")
            
            # Get wallets
            from_wallet = self._get_wallet_by_id(from_wallet_id)
            to_wallet = self._get_wallet_by_id(to_wallet_id)
            
            if not from_wallet or not to_wallet:
                transfer_result["error"] = "Invalid wallet ID(s)"
                return transfer_result
            
            # Create outgoing transaction
            outgoing_txn = await self.process_transaction({
                "wallet_id": from_wallet_id,
                "transaction_type": "transfer_out",
                "currency": currency,
                "amount": str(amount),
                "description": f"Transfer to {to_wallet_id}",
                "to_wallet_id": to_wallet_id,
                "reference_id": transfer_result["transfer_id"]
            })
            
            transfer_result["transactions"].append(outgoing_txn.to_dict())
            
            if outgoing_txn.status == TransactionStatus.COMPLETED:
                # Create incoming transaction
                incoming_txn = await self.process_transaction({
                    "wallet_id": to_wallet_id,
                    "transaction_type": "transfer_in",
                    "currency": currency,
                    "amount": str(outgoing_txn.net_amount),
                    "description": f"Transfer from {from_wallet_id}",
                    "from_wallet_id": from_wallet_id,
                    "reference_id": transfer_result["transfer_id"]
                })
                
                transfer_result["transactions"].append(incoming_txn.to_dict())
                
                if incoming_txn.status == TransactionStatus.COMPLETED:
                    transfer_result["success"] = True
                else:
                    transfer_result["error"] = "Incoming transaction failed"
            else:
                transfer_result["error"] = "Outgoing transaction failed"
            
        except Exception as e:
            transfer_result["error"] = str(e)
        
        return transfer_result
    
    def get_wallet_balance(self, wallet_id: str, currency: str = None) -> Dict[str, Any]:
        """Get wallet balance"""
        
        wallet = self._get_wallet_by_id(wallet_id)
        if not wallet:
            return {"error": "Wallet not found"}
        
        if currency:
            balance = wallet.get_balance(currency)
            if balance:
                return balance.to_dict()
            else:
                return {"error": f"Currency {currency} not found in wallet"}
        else:
            # Return all balances
            return {
                "wallet_id": wallet_id,
                "balances": {currency: balance.to_dict() for currency, balance in wallet.balances.items()}
            }
    
    def get_transaction_history(self, wallet_id: str, 
                              date_from: datetime = None,
                              date_to: datetime = None,
                              transaction_type: TransactionType = None,
                              limit: int = 100) -> Dict[str, Any]:
        """Get transaction history"""
        
        date_from = date_from or (datetime.now() - timedelta(days=30))
        date_to = date_to or datetime.now()
        
        wallet_transactions = []
        
        for transaction in self.transactions:
            if transaction.wallet_id == wallet_id:
                if date_from <= transaction.created_date <= date_to:
                    if not transaction_type or transaction.transaction_type == transaction_type:
                        wallet_transactions.append(transaction.to_dict())
        
        # Sort by date (newest first) and limit
        wallet_transactions.sort(key=lambda x: x["created_date"], reverse=True)
        wallet_transactions = wallet_transactions[:limit]
        
        return {
            "wallet_id": wallet_id,
            "period_start": date_from.isoformat(),
            "period_end": date_to.isoformat(),
            "transaction_count": len(wallet_transactions),
            "transactions": wallet_transactions
        }
    
    def get_wallet_statistics(self) -> Dict[str, Any]:
        """Get wallet statistics"""
        
        stats = {
            "total_wallets": len(self.wallets),
            "wallets_by_type": {},
            "wallets_by_status": {},
            "total_transactions": len(self.transactions),
            "transactions_by_type": {},
            "transactions_by_status": {},
            "total_volume": {},
            "active_currencies": set()
        }
        
        # Wallet statistics
        for wallet in self.wallets:
            # Count by type
            wallet_type = wallet.wallet_type.value
            stats["wallets_by_type"][wallet_type] = stats["wallets_by_type"].get(wallet_type, 0) + 1
            
            # Count by status
            status = wallet.status.value
            stats["wallets_by_status"][status] = stats["wallets_by_status"].get(status, 0) + 1
            
            # Add currencies
            stats["active_currencies"].update(wallet.balances.keys())
        
        # Transaction statistics
        for transaction in self.transactions:
            # Count by type
            txn_type = transaction.transaction_type.value
            stats["transactions_by_type"][txn_type] = stats["transactions_by_type"].get(txn_type, 0) + 1
            
            # Count by status
            status = transaction.status.value
            stats["transactions_by_status"][status] = stats["transactions_by_status"].get(status, 0) + 1
            
            # Volume by currency
            currency = transaction.currency
            if currency not in stats["total_volume"]:
                stats["total_volume"][currency] = 0.0
            stats["total_volume"][currency] += float(transaction.amount)
        
        stats["active_currencies"] = list(stats["active_currencies"])
        
        return stats
    
    def search_wallets(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search wallets"""
        
        matching_wallets = []
        
        for wallet in self.wallets:
            if self._matches_wallet_criteria(wallet, search_criteria):
                matching_wallets.append(wallet.get_summary())
        
        return matching_wallets
    
    # Helper methods
    def _get_wallet_by_id(self, wallet_id: str) -> Optional[DigitalWallet]:
        """Get wallet by ID"""
        for wallet in self.wallets:
            if wallet.wallet_id == wallet_id:
                return wallet
        return None
    
    def _get_currency_type(self, currency: str) -> CurrencyType:
        """Get currency type"""
        for currency_type, currencies in self.supported_currencies.items():
            if currency in currencies:
                if currency_type == "fiat":
                    return CurrencyType.FIAT
                elif currency_type == "crypto":
                    return CurrencyType.CRYPTO
                elif currency_type == "tokens":
                    return CurrencyType.TOKEN
                elif currency_type == "points":
                    return CurrencyType.POINTS
                elif currency_type == "credits":
                    return CurrencyType.CREDITS
        
        return CurrencyType.FIAT  # Default
    
    async def _validate_transaction(self, transaction: WalletTransaction) -> Dict[str, Any]:
        """Validate transaction"""
        validation = {
            "valid": True,
            "reason": None
        }
        
        # Get wallet
        wallet = self._get_wallet_by_id(transaction.wallet_id)
        if not wallet:
            validation["valid"] = False
            validation["reason"] = "Wallet not found"
            return validation
        
        # Check if wallet can transact
        can_transact = wallet.can_transact(transaction.amount, transaction.currency, transaction.transaction_type)
        if not can_transact["allowed"]:
            validation["valid"] = False
            validation["reason"] = can_transact["reason"]
            return validation
        
        return validation
    
    async def _execute_transaction(self, transaction: WalletTransaction) -> Dict[str, Any]:
        """Execute transaction"""
        execution_result = {
            "success": False,
            "error": None
        }
        
        try:
            wallet = self._get_wallet_by_id(transaction.wallet_id)
            balance = wallet.get_balance(transaction.currency)
            
            if not balance:
                # Add currency if not exists
                currency_type = self._get_currency_type(transaction.currency)
                balance = wallet.add_currency(transaction.currency, currency_type)
            
            # Update balance based on transaction type
            if transaction.transaction_type in [TransactionType.DEPOSIT, TransactionType.TRANSFER_IN,
                                              TransactionType.REFUND, TransactionType.CASHBACK, TransactionType.REWARD]:
                # Credit transaction
                balance.update_balance(transaction.net_amount, "available")
            elif transaction.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.TRANSFER_OUT,
                                                TransactionType.PAYMENT, TransactionType.FEE]:
                # Debit transaction
                balance.update_balance(-transaction.amount, "available")
            
            wallet.update_activity()
            execution_result["success"] = True
            
        except Exception as e:
            execution_result["error"] = str(e)
        
        return execution_result
    
    def _matches_wallet_criteria(self, wallet: DigitalWallet, criteria: Dict[str, Any]) -> bool:
        """Check if wallet matches search criteria"""
        # Implement search logic
        return True
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete wallet configuration"""
        return {
            "wallet_statistics": self.get_wallet_statistics(),
            "wallet_security": self.wallet_security.get_config(),
            "wallet_features": self.wallet_features.get_config(),
            "wallet_analytics": self.wallet_analytics.get_config(),
            "wallets_count": len(self.wallets),
            "transactions_count": len(self.transactions),
            "global_settings": {
                "wallet_system_enabled": self.wallet_system_enabled,
                "multi_currency_enabled": self.multi_currency_enabled,
                "cryptocurrency_enabled": self.cryptocurrency_enabled,
                "auto_conversion_enabled": self.auto_conversion_enabled
            },
            "default_limits": {k: float(v) for k, v in self.default_limits.items()},
            "transaction_fees": {k.value: float(v) for k, v in self.transaction_fees.items()},
            "supported_currencies": self.supported_currencies,
            "exchange_providers": self.exchange_providers,
            "verification_levels": self.verification_levels,
            "security_settings": self.security_settings,
            "integration_settings": self.integration_settings
        }

# Global wallet configuration instance
wallet_config = WalletConfiguration()

# Export main classes
__all__ = [
    "WalletConfiguration",
    "WalletType",
    "WalletStatus",
    "TransactionType",
    "TransactionStatus",
    "CurrencyType",
    "WalletBalance",
    "WalletTransaction",
    "DigitalWallet",
    "WalletSecurityConfig",
    "WalletFeaturesConfig",
    "WalletAnalyticsConfig",
    "wallet_config"
]
