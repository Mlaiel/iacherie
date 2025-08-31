"""
🏦 Plaid Banking Integration - US/EU Bank Account Connections
==========================================================

Enterprise-grade Plaid banking integration for secure bank account 
connections, balance checks, transaction history, and ACH transfers
for US and European users.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

🚨 CRITICAL LEGAL WARNING:
This code and all associated intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, modification, distribution, or commercialization 
is STRICTLY PROHIBITED and will result in immediate legal action.

Features:
- Secure bank account linking via Plaid Link
- Real-time balance checking
- Transaction history retrieval
- Identity verification
- ACH transfer initiation
- Multi-country support (US/EU)
- Webhook handling for account updates
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import json
import os
from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.auth_get_request import AuthGetRequest
from plaid.model.identity_get_request import IdentityGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.model.item_get_request import ItemGetRequest
from plaid.configuration import Configuration
from plaid.api_client import ApiClient

logger = logging.getLogger(__name__)


class PlaidEnvironment(Enum):
    """Plaid API environments"""
    SANDBOX = "sandbox"
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class AccountType(Enum):
    """Bank account types supported by Plaid"""
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"
    LOAN = "loan"
    MORTGAGE = "mortgage"
    INVESTMENT = "investment"
    OTHER = "other"


class AccountSubtype(Enum):
    """Bank account subtypes"""
    CHECKING = "checking"
    SAVINGS = "savings"
    MONEY_MARKET = "money market"
    CD = "cd"
    CREDIT_CARD = "credit card"
    PAYPAL = "paypal"


class TransactionCategory(Enum):
    """Transaction categories"""
    TRANSFER = "Transfer"
    DEPOSIT = "Deposit"
    WITHDRAWAL = "Withdrawal"
    PAYMENT = "Payment"
    PURCHASE = "Purchase"
    FEE = "Fee"
    INTEREST = "Interest"
    OTHER = "Other"


@dataclass
class PlaidConfiguration:
    """Plaid API configuration"""
    client_id: str
    secret: str
    environment: PlaidEnvironment
    webhook_url: Optional[str] = None
    country_codes: List[str] = None
    
    def __post_init__(self):
        if self.country_codes is None:
            self.country_codes = ['US', 'GB', 'ES', 'NL', 'FR', 'IE', 'DE']


@dataclass
class BankAccount:
    """Bank account information from Plaid"""
    account_id: str
    name: str
    official_name: Optional[str]
    type: AccountType
    subtype: Optional[AccountSubtype]
    mask: Optional[str]
    currency: str
    balance_available: Optional[Decimal]
    balance_current: Optional[Decimal]
    balance_limit: Optional[Decimal]
    institution_id: str
    institution_name: str
    last_updated: datetime
    
    @classmethod
    def from_plaid_account(cls, plaid_account, institution_name: str):
        """Create BankAccount from Plaid API response"""
        balances = plaid_account.get('balances', {})
        
        return cls(
            account_id=plaid_account['account_id'],
            name=plaid_account['name'],
            official_name=plaid_account.get('official_name'),
            type=AccountType(plaid_account['type'].lower()),
            subtype=AccountSubtype(plaid_account.get('subtype', '').lower()) if plaid_account.get('subtype') else None,
            mask=plaid_account.get('mask'),
            currency=balances.get('iso_currency_code', 'USD'),
            balance_available=Decimal(str(balances.get('available', 0))) if balances.get('available') else None,
            balance_current=Decimal(str(balances.get('current', 0))) if balances.get('current') else None,
            balance_limit=Decimal(str(balances.get('limit', 0))) if balances.get('limit') else None,
            institution_id=plaid_account.get('institution_id', ''),
            institution_name=institution_name,
            last_updated=datetime.utcnow()
        )


@dataclass
class BankTransaction:
    """Bank transaction from Plaid"""
    transaction_id: str
    account_id: str
    amount: Decimal
    currency: str
    date: datetime
    description: str
    merchant_name: Optional[str]
    category: List[str]
    category_id: str
    transaction_type: str
    pending: bool
    account_owner: Optional[str]
    location: Optional[Dict[str, Any]]
    payment_meta: Optional[Dict[str, Any]]
    
    @classmethod
    def from_plaid_transaction(cls, plaid_transaction):
        """Create BankTransaction from Plaid API response"""
        return cls(
            transaction_id=plaid_transaction['transaction_id'],
            account_id=plaid_transaction['account_id'],
            amount=Decimal(str(plaid_transaction['amount'])),
            currency=plaid_transaction.get('iso_currency_code', 'USD'),
            date=datetime.fromisoformat(plaid_transaction['date']),
            description=plaid_transaction['name'],
            merchant_name=plaid_transaction.get('merchant_name'),
            category=plaid_transaction.get('category', []),
            category_id=plaid_transaction.get('category_id', ''),
            transaction_type=plaid_transaction.get('transaction_type', 'place'),
            pending=plaid_transaction.get('pending', False),
            account_owner=plaid_transaction.get('account_owner'),
            location=plaid_transaction.get('location'),
            payment_meta=plaid_transaction.get('payment_meta')
        )


@dataclass
class PlaidLinkResult:
    """Result from Plaid Link token exchange"""
    access_token: str
    item_id: str
    institution_id: str
    institution_name: str
    accounts: List[BankAccount]
    webhook_verification_key: Optional[str] = None


class PlaidBankingProcessor:
    """
    Enterprise Plaid banking processor for secure bank connections and operations
    
    Provides comprehensive banking functionality including:
    - Secure account linking via Plaid Link
    - Real-time balance and transaction data
    - Identity verification
    - ACH transfer capabilities
    - Multi-country support for US and EU
    """
    
    def __init__(self, config: PlaidConfiguration):
        """Initialize Plaid banking processor"""
        self.config = config
        self.client = self._create_plaid_client()
        
        # Rate limiting and retry configuration
        self.max_retries = 3
        self.retry_delay = 1.0
        
        logger.info(f"Initialized Plaid banking processor for {config.environment.value} environment")
    
    def _create_plaid_client(self) -> plaid_api.PlaidApi:
        """Create and configure Plaid API client"""
        # Determine Plaid environment URL
        env_urls = {
            PlaidEnvironment.SANDBOX: 'https://sandbox.plaidapi.com',
            PlaidEnvironment.DEVELOPMENT: 'https://development.plaidapi.com',
            PlaidEnvironment.PRODUCTION: 'https://production.plaidapi.com'
        }
        
        configuration = Configuration(
            host=env_urls[self.config.environment],
            api_key={
                'clientId': self.config.client_id,
                'secret': self.config.secret,
                'plaidVersion': '2020-09-14'
            }
        )
        
        api_client = ApiClient(configuration)
        return plaid_api.PlaidApi(api_client)
    
    async def create_link_token(self, user_id: str, user_name: str, webhook_url: Optional[str] = None) -> str:
        """
        Create a Plaid Link token for bank account connection
        
        Args:
            user_id: Unique user identifier
            user_name: User's name for Plaid Link
            webhook_url: Optional webhook URL for account updates
            
        Returns:
            Link token for frontend Plaid Link initialization
        """
        try:
            # Convert country codes to Plaid CountryCode objects
            country_codes = [CountryCode(code) for code in self.config.country_codes]
            
            # Products to enable
            products = [Products('auth'), Products('identity'), Products('transactions')]
            
            request = LinkTokenCreateRequest(
                products=products,
                client_name="Ainflue Banking",
                country_codes=country_codes,
                language='en',
                webhook=webhook_url or self.config.webhook_url,
                user=LinkTokenCreateRequestUser(client_user_id=str(user_id))
            )
            
            response = self.client.link_token_create(request)
            link_token = response['link_token']
            
            logger.info(f"Created Plaid Link token for user {user_id}")
            return link_token
            
        except Exception as e:
            logger.error(f"Failed to create Plaid Link token: {str(e)}")
            raise Exception(f"Link token creation failed: {str(e)}")
    
    async def exchange_public_token(self, public_token: str) -> PlaidLinkResult:
        """
        Exchange public token for access token after successful Link
        
        Args:
            public_token: Public token from Plaid Link success
            
        Returns:
            PlaidLinkResult with access token and account information
        """
        try:
            # Exchange public token for access token
            exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
            exchange_response = self.client.item_public_token_exchange(exchange_request)
            
            access_token = exchange_response['access_token']
            item_id = exchange_response['item_id']
            
            # Get item information (institution)
            item_request = ItemGetRequest(access_token=access_token)
            item_response = self.client.item_get(item_request)
            institution_id = item_response['item']['institution_id']
            
            # Get accounts
            accounts_request = AccountsGetRequest(access_token=access_token)
            accounts_response = self.client.accounts_get(accounts_request)
            
            # Convert Plaid accounts to our BankAccount objects
            institution_name = item_response['item'].get('institution_name', 'Unknown Bank')
            accounts = [
                BankAccount.from_plaid_account(acc, institution_name)
                for acc in accounts_response['accounts']
            ]
            
            result = PlaidLinkResult(
                access_token=access_token,
                item_id=item_id,
                institution_id=institution_id,
                institution_name=institution_name,
                accounts=accounts
            )
            
            logger.info(f"Successfully exchanged public token, found {len(accounts)} accounts")
            return result
            
        except Exception as e:
            logger.error(f"Failed to exchange public token: {str(e)}")
            raise Exception(f"Token exchange failed: {str(e)}")
    
    async def get_accounts(self, access_token: str) -> List[BankAccount]:
        """
        Get all bank accounts for a connected item
        
        Args:
            access_token: Plaid access token
            
        Returns:
            List of bank accounts
        """
        try:
            request = AccountsGetRequest(access_token=access_token)
            response = self.client.accounts_get(request)
            
            # Get institution name
            item_request = ItemGetRequest(access_token=access_token)
            item_response = self.client.item_get(item_request)
            institution_name = item_response['item'].get('institution_name', 'Unknown Bank')
            
            accounts = [
                BankAccount.from_plaid_account(acc, institution_name)
                for acc in response['accounts']
            ]
            
            logger.info(f"Retrieved {len(accounts)} accounts")
            return accounts
            
        except Exception as e:
            logger.error(f"Failed to get accounts: {str(e)}")
            raise Exception(f"Account retrieval failed: {str(e)}")
    
    async def get_account_balance(self, access_token: str, account_id: str) -> BankAccount:
        """
        Get current balance for a specific account
        
        Args:
            access_token: Plaid access token
            account_id: Specific account ID
            
        Returns:
            Updated BankAccount with current balance
        """
        try:
            request = AccountsGetRequest(access_token=access_token, options={'account_ids': [account_id]})
            response = self.client.accounts_get(request)
            
            if not response['accounts']:
                raise Exception(f"Account {account_id} not found")
            
            # Get institution name
            item_request = ItemGetRequest(access_token=access_token)
            item_response = self.client.item_get(item_request)
            institution_name = item_response['item'].get('institution_name', 'Unknown Bank')
            
            account = BankAccount.from_plaid_account(response['accounts'][0], institution_name)
            
            logger.info(f"Retrieved balance for account {account_id}: {account.balance_current}")
            return account
            
        except Exception as e:
            logger.error(f"Failed to get account balance: {str(e)}")
            raise Exception(f"Balance retrieval failed: {str(e)}")
    
    async def get_transactions(
        self, 
        access_token: str, 
        start_date: datetime, 
        end_date: datetime,
        account_ids: Optional[List[str]] = None,
        count: int = 100,
        offset: int = 0
    ) -> List[BankTransaction]:
        """
        Get transactions for specified date range and accounts
        
        Args:
            access_token: Plaid access token
            start_date: Transaction start date
            end_date: Transaction end date
            account_ids: Optional list of specific account IDs
            count: Number of transactions to retrieve (max 500)
            offset: Offset for pagination
            
        Returns:
            List of bank transactions
        """
        try:
            options = {
                'count': min(count, 500),  # Plaid max is 500
                'offset': offset
            }
            
            if account_ids:
                options['account_ids'] = account_ids
            
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date.date(),
                end_date=end_date.date(),
                options=options
            )
            
            response = self.client.transactions_get(request)
            
            transactions = [
                BankTransaction.from_plaid_transaction(txn)
                for txn in response['transactions']
            ]
            
            logger.info(f"Retrieved {len(transactions)} transactions")
            return transactions
            
        except Exception as e:
            logger.error(f"Failed to get transactions: {str(e)}")
            raise Exception(f"Transaction retrieval failed: {str(e)}")
    
    async def get_identity(self, access_token: str) -> Dict[str, Any]:
        """
        Get identity information for account holder
        
        Args:
            access_token: Plaid access token
            
        Returns:
            Dictionary with identity information
        """
        try:
            request = IdentityGetRequest(access_token=access_token)
            response = self.client.identity_get(request)
            
            identity_data = {
                'accounts': [],
                'item': response.get('item', {})
            }
            
            for account in response.get('accounts', []):
                account_identity = {
                    'account_id': account['account_id'],
                    'owners': []
                }
                
                for owner in account.get('owners', []):
                    owner_info = {
                        'names': owner.get('names', []),
                        'phone_numbers': owner.get('phone_numbers', []),
                        'emails': owner.get('emails', []),
                        'addresses': owner.get('addresses', [])
                    }
                    account_identity['owners'].append(owner_info)
                
                identity_data['accounts'].append(account_identity)
            
            logger.info("Retrieved identity information")
            return identity_data
            
        except Exception as e:
            logger.error(f"Failed to get identity: {str(e)}")
            raise Exception(f"Identity retrieval failed: {str(e)}")
    
    async def get_auth_data(self, access_token: str) -> Dict[str, Any]:
        """
        Get account and routing numbers for ACH transfers
        
        Args:
            access_token: Plaid access token
            
        Returns:
            Dictionary with auth data for ACH transfers
        """
        try:
            request = AuthGetRequest(access_token=access_token)
            response = self.client.auth_get(request)
            
            auth_data = {
                'accounts': [],
                'numbers': response.get('numbers', {})
            }
            
            for account in response.get('accounts', []):
                account_auth = {
                    'account_id': account['account_id'],
                    'name': account['name'],
                    'type': account['type'],
                    'subtype': account.get('subtype'),
                    'mask': account.get('mask')
                }
                auth_data['accounts'].append(account_auth)
            
            logger.info("Retrieved auth data for ACH transfers")
            return auth_data
            
        except Exception as e:
            logger.error(f"Failed to get auth data: {str(e)}")
            raise Exception(f"Auth data retrieval failed: {str(e)}")
    
    async def handle_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Plaid webhook notifications
        
        Args:
            webhook_data: Webhook payload from Plaid
            
        Returns:
            Dictionary with processed webhook information
        """
        try:
            webhook_type = webhook_data.get('webhook_type')
            webhook_code = webhook_data.get('webhook_code')
            item_id = webhook_data.get('item_id')
            
            logger.info(f"Processing Plaid webhook: {webhook_type}.{webhook_code} for item {item_id}")
            
            processed_data = {
                'webhook_type': webhook_type,
                'webhook_code': webhook_code,
                'item_id': item_id,
                'timestamp': datetime.utcnow(),
                'processed': True
            }
            
            # Handle different webhook types
            if webhook_type == 'TRANSACTIONS':
                if webhook_code == 'DEFAULT_UPDATE':
                    # New transactions available
                    processed_data['action'] = 'fetch_new_transactions'
                elif webhook_code == 'HISTORICAL_UPDATE':
                    # Historical transactions updated
                    processed_data['action'] = 'fetch_historical_transactions'
                elif webhook_code == 'INITIAL_UPDATE':
                    # Initial transaction fetch complete
                    processed_data['action'] = 'initial_transactions_ready'
                    
            elif webhook_type == 'ITEM':
                if webhook_code == 'ERROR':
                    # Item error occurred
                    processed_data['action'] = 'handle_item_error'
                    processed_data['error'] = webhook_data.get('error')
                elif webhook_code == 'PENDING_EXPIRATION':
                    # Access token expiring
                    processed_data['action'] = 'refresh_access_token'
                    
            elif webhook_type == 'AUTH':
                if webhook_code == 'DEFAULT_UPDATE':
                    # Auth data updated
                    processed_data['action'] = 'refresh_auth_data'
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process webhook: {str(e)}")
            raise Exception(f"Webhook processing failed: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert processor to dictionary representation"""
        return {
            'processor_type': 'plaid_banking',
            'environment': self.config.environment.value,
            'supported_countries': self.config.country_codes,
            'features': [
                'bank_account_linking',
                'balance_checking',
                'transaction_history',
                'identity_verification',
                'ach_auth_data',
                'real_time_webhooks'
            ]
        }


# Export key classes and functions
__all__ = [
    'PlaidBankingProcessor',
    'PlaidConfiguration', 
    'BankAccount',
    'BankTransaction',
    'PlaidLinkResult',
    'PlaidEnvironment',
    'AccountType',
    'AccountSubtype',
    'TransactionCategory'
]