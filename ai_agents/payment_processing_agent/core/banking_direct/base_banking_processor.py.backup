"""Base Banking Direct Processor - Abstract Foundation for Bank Integrations

Abstract base class for Banking Direct processors including Plaid, Open Banking,
and ACH Direct, providing common banking functionality and standardized interfaces.

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

from ..base_processor import BaseProcessor, PaymentResult, PayoutResult, BalanceResult

logger = logging.getLogger(__name__)


@dataclass
class BankAccount:
    """Bank account information structure."""
    account_id: str
    account_name: str
    account_type: str  # checking, savings, etc.
    routing_number: Optional[str] = None
    account_number_mask: Optional[str] = None  # Masked for security
    institution_name: str = ""
    institution_id: Optional[str] = None
    currency: str = "USD"
    balance: Optional[Decimal] = None
    available_balance: Optional[Decimal] = None
    is_active: bool = True
    verification_status: str = "unverified"  # unverified, pending, verified
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class BankConnectionResult:
    """Bank connection result structure."""
    success: bool
    connection_id: Optional[str] = None
    accounts: List[BankAccount] = None
    access_token: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    requires_verification: bool = False
    verification_url: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.accounts is None:
            self.accounts = []
        if self.metadata is None:
            self.metadata = {}


@dataclass  
class DirectDebitResult:
    """Direct debit setup and execution result."""
    success: bool
    mandate_id: Optional[str] = None
    debit_id: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: str = "USD"
    status: str = "unknown"
    scheduled_date: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseBankingProcessor(BaseProcessor):
    """
    Abstract base class for Banking Direct processors.
    
    Provides common functionality for bank account connections,
    balance checks, direct debits, and compliance features.
    """
    
    def __init__(
        self,
        name: str,
        api_key: str,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        environment: str = "production",
        supported_countries: List[str] = None,
        **kwargs
    ):
        """
        Initialize Banking Direct processor.
        
        Args:
            name: Processor name
            api_key: API key for banking service
            client_id: OAuth client ID (if applicable)
            client_secret: OAuth client secret (if applicable)
            environment: sandbox or production
            supported_countries: List of supported country codes
        """
        super().__init__(name, api_key, environment, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self.supported_countries = supported_countries or ["US", "CA", "GB", "FR", "DE", "ES", "IT", "NL"]
        
        # Banking-specific configuration
        self.compliance_enabled = kwargs.get('compliance_enabled', True)
        self.verification_required = kwargs.get('verification_required', True)
        self.max_transaction_amount = kwargs.get('max_transaction_amount', Decimal('10000.00'))
        
    @abstractmethod
    async def connect_bank_account(
        self,
        user_id: str,
        institution_id: Optional[str] = None,
        public_token: Optional[str] = None,
        **kwargs
    ) -> BankConnectionResult:
        """
        Connect a bank account for the user.
        
        Args:
            user_id: User identifier
            institution_id: Bank/institution identifier
            public_token: Public token from Link (Plaid) or OAuth flow
            **kwargs: Additional provider-specific parameters
            
        Returns:
            BankConnectionResult with connection details
        """
        pass
    
    @abstractmethod
    async def get_bank_accounts(self, user_id: str, connection_id: Optional[str] = None) -> List[BankAccount]:
        """
        Get connected bank accounts for user.
        
        Args:
            user_id: User identifier
            connection_id: Specific connection ID (optional)
            
        Returns:
            List of connected bank accounts
        """
        pass
    
    @abstractmethod
    async def verify_bank_account(self, user_id: str, account_id: str, verification_amounts: Optional[List[Decimal]] = None) -> bool:
        """
        Verify bank account ownership.
        
        Args:
            user_id: User identifier
            account_id: Bank account identifier
            verification_amounts: Micro-deposit amounts for verification
            
        Returns:
            True if verification successful
        """
        pass
    
    @abstractmethod
    async def setup_direct_debit(
        self,
        user_id: str,
        account_id: str,
        amount: Decimal,
        currency: str = "USD",
        frequency: str = "monthly",
        start_date: Optional[datetime] = None,
        **kwargs
    ) -> DirectDebitResult:
        """
        Setup recurring direct debit from bank account.
        
        Args:
            user_id: User identifier
            account_id: Bank account identifier
            amount: Debit amount
            currency: Currency code
            frequency: Debit frequency (monthly, weekly, etc.)
            start_date: First debit date
            **kwargs: Additional parameters
            
        Returns:
            DirectDebitResult with setup details
        """
        pass
    
    @abstractmethod
    async def execute_direct_debit(
        self,
        mandate_id: str,
        amount: Optional[Decimal] = None,
        **kwargs
    ) -> DirectDebitResult:
        """
        Execute a one-time or scheduled direct debit.
        
        Args:
            mandate_id: Direct debit mandate identifier
            amount: Override amount (if different from mandate)
            **kwargs: Additional parameters
            
        Returns:
            DirectDebitResult with execution details
        """
        pass
    
    async def get_account_balance(self, user_id: str, account_id: str) -> BalanceResult:
        """
        Get real-time account balance.
        
        Args:
            user_id: User identifier
            account_id: Bank account identifier
            
        Returns:
            BalanceResult with current balance
        """
        try:
            accounts = await self.get_bank_accounts(user_id)
            account = next((acc for acc in accounts if acc.account_id == account_id), None)
            
            if not account:
                return BalanceResult(
                    available=Decimal('0'),
                    pending=Decimal('0'),
                    currency="USD",
                    last_updated=datetime.now(),
                    metadata={"error": "Account not found"}
                )
            
            return BalanceResult(
                available=account.available_balance or Decimal('0'),
                pending=(account.balance or Decimal('0')) - (account.available_balance or Decimal('0')),
                currency=account.currency,
                last_updated=datetime.now(),
                metadata={
                    "account_type": account.account_type,
                    "institution": account.institution_name
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting account balance: {str(e)}")
            return BalanceResult(
                available=Decimal('0'),
                pending=Decimal('0'),
                currency="USD",
                last_updated=datetime.now(),
                metadata={"error": str(e)}
            )
    
    def _validate_transaction_limits(self, amount: Decimal, currency: str) -> bool:
        """
        Validate transaction against limits and compliance rules.
        
        Args:
            amount: Transaction amount
            currency: Currency code
            
        Returns:
            True if transaction is within limits
        """
        # Convert to USD for limit checking if needed
        usd_amount = amount  # Simplified - would need actual conversion
        
        if usd_amount > self.max_transaction_amount:
            return False
            
        # Add more compliance checks as needed
        return True
    
    def _mask_account_number(self, account_number: str) -> str:
        """
        Mask account number for security.
        
        Args:
            account_number: Full account number
            
        Returns:
            Masked account number
        """
        if len(account_number) <= 4:
            return "*" * len(account_number)
        return "*" * (len(account_number) - 4) + account_number[-4:]