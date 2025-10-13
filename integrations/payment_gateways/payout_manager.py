"""Payout Manager Integration
==========================

Enterprise-grade automated creator payout system for multi-gateway revenue distribution,
tax compliance, and creator economy monetization optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
import decimal
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
import uuid

# Configure logger
logger = logging.getLogger(__name__)

class PayoutStatus(Enum):
    """Payout status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    HELD = "held"

class PayoutMethod(Enum):
    """Payout method enumeration"""
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE_EXPRESS = "stripe_express"
    WISE = "wise"
    CRYPTOCURRENCY = "cryptocurrency"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"

class TaxStatus(Enum):
    """Tax status enumeration"""
    COMPLIANT = "compliant"
    PENDING_DOCUMENTS = "pending_documents"
    UNDER_REVIEW = "under_review"
    NON_COMPLIANT = "non_compliant"

class CreatorProfile:
    """Creator profile for payout management"""
    
    def __init__(self, creator_id: str, username: str, email: str):
        self.creator_id = creator_id
        self.username = username
        self.email = email
        self.display_name = ""
        self.country = ""
        self.currency = "USD"
        self.tax_id = ""
        self.tax_status = TaxStatus.PENDING_DOCUMENTS
        self.preferred_payout_method = PayoutMethod.STRIPE_EXPRESS
        self.minimum_payout_amount = decimal.Decimal('25.00')
        self.payout_schedule = "weekly"
        self.total_earnings = decimal.Decimal('0.00')
        self.available_balance = decimal.Decimal('0.00')
        self.pending_balance = decimal.Decimal('0.00')

class PayoutTransaction:
    """Individual payout transaction"""
    
    def __init__(self, transaction_id: str, creator_id: str, amount: decimal.Decimal):
        self.transaction_id = transaction_id
        self.creator_id = creator_id
        self.amount = amount
        self.currency = "USD"
        self.status = PayoutStatus.PENDING
        self.method = PayoutMethod.STRIPE_EXPRESS
        self.gateway = "stripe"
        self.gateway_transaction_id = ""
        self.created_at = datetime.utcnow()
        self.processed_at = None
        self.completed_at = None
        self.fees = decimal.Decimal('0.00')
        self.net_amount = amount
        self.metadata = {}
        self.error_message = ""

class RevenueSource:
    """Revenue source tracking"""
    
    def __init__(self, source_id: str, source_type: str, platform: str):
        self.source_id = source_id
        self.source_type = source_type  # 'subscription', 'one_time', 'tips', 'ads'
        self.platform = platform  # 'youtube', 'twitch', 'substack', etc.
        self.amount = decimal.Decimal('0.00')
        self.creator_share = decimal.Decimal('0.00')
        self.platform_fee = decimal.Decimal('0.00')
        self.tax_withholding = decimal.Decimal('0.00')
        self.timestamp = datetime.utcnow()

class PayoutManagerError(Exception):
    """Custom exception for Payout Manager errors"""
    pass

class PayoutManager:
    """
    Comprehensive automated creator payout management system.
    
    Features:
    - Multi-gateway payout distribution
    - Automated tax compliance and reporting
    - Creator revenue optimization
    - Real-time balance tracking
    - Fraud prevention and security
    - International payment support
    - Revenue source consolidation
    - Performance analytics and insights
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.gateways = {}
        self.session = None
        self.rate_limits = {
            'requests_per_minute': 100,
            'requests_made': 0,
            'minute_start': datetime.utcnow().minute
        }
        
        # Initialize payment gateways
        self._initialize_gateways()
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _initialize_gateways(self):
        """Initialize payment gateway connections"""
        gateway_configs = self.config.get('gateways', {})
        
        for gateway_name, gateway_config in gateway_configs.items():
            self.gateways[gateway_name] = {
                'config': gateway_config,
                'enabled': gateway_config.get('enabled', True),
                'priority': gateway_config.get('priority', 1),
                'supported_countries': gateway_config.get('supported_countries', []),
                'supported_currencies': gateway_config.get('supported_currencies', ['USD']),
                'fees': gateway_config.get('fees', {})
            }
        
        logger.info(f"Initialized {len(self.gateways)} payment gateways")

    # Creator Profile Management
    async def register_creator(self, creator_data: Dict[str, Any]) -> CreatorProfile:
        """
        Register a new creator for payout management.
        
        Args:
            creator_data: Creator registration information
            
        Returns:
            Created CreatorProfile object
        """
        required_fields = ['creator_id', 'username', 'email', 'country']
        for field in required_fields:
            if field not in creator_data:
                raise PayoutManagerError(f"Missing required field: {field}")
        
        creator = CreatorProfile(
            creator_id=creator_data['creator_id'],
            username=creator_data['username'],
            email=creator_data['email']
        )
        
        creator.display_name = creator_data.get('display_name', creator_data['username'])
        creator.country = creator_data['country']
        creator.currency = creator_data.get('currency', 'USD')
        creator.tax_id = creator_data.get('tax_id', '')
        creator.preferred_payout_method = PayoutMethod(creator_data.get('payout_method', 'stripe_express'))
        creator.minimum_payout_amount = decimal.Decimal(str(creator_data.get('minimum_payout', 25.00)))
        creator.payout_schedule = creator_data.get('payout_schedule', 'weekly')
        
        # Validate creator information
        await self._validate_creator_profile(creator)
        
        # Setup tax compliance
        await self._setup_tax_compliance(creator)
        
        # Initialize payout method
        await self._setup_payout_method(creator)
        
        logger.info(f"Registered creator: {creator.creator_id}")
        return creator

    async def get_creator_profile(self, creator_id: str) -> CreatorProfile:
        """
        Get creator profile with current balance and status.
        
        Args:
            creator_id: Creator ID
            
        Returns:
            CreatorProfile object
        """
        # This would fetch from database
        creator = await self._fetch_creator_profile(creator_id)
        
        # Update balance information
        creator.available_balance = await self._calculate_available_balance(creator_id)
        creator.pending_balance = await self._calculate_pending_balance(creator_id)
        creator.total_earnings = await self._calculate_total_earnings(creator_id)
        
        return creator

    async def update_creator_profile(self, creator_id: str, updates: Dict[str, Any]) -> CreatorProfile:
        """
        Update creator profile information.
        
        Args:
            creator_id: Creator ID
            updates: Profile updates
            
        Returns:
            Updated CreatorProfile object
        """
        creator = await self.get_creator_profile(creator_id)
        
        # Apply updates
        for field, value in updates.items():
            if hasattr(creator, field):
                if field == 'preferred_payout_method':
                    creator.preferred_payout_method = PayoutMethod(value)
                elif field == 'minimum_payout_amount':
                    creator.minimum_payout_amount = decimal.Decimal(str(value))
                else:
                    setattr(creator, field, value)
        
        # Validate updates
        await self._validate_creator_profile(creator)
        
        # Update payout method if changed
        if 'preferred_payout_method' in updates:
            await self._setup_payout_method(creator)
        
        # Update tax compliance if relevant fields changed
        if any(field in updates for field in ['country', 'tax_id']):
            await self._setup_tax_compliance(creator)
        
        logger.info(f"Updated creator profile: {creator_id}")
        return creator

    # Revenue Management
    async def record_revenue(self, creator_id: str, revenue_data: Dict[str, Any]) -> RevenueSource:
        """
        Record revenue from various sources.
        
        Args:
            creator_id: Creator ID
            revenue_data: Revenue information
            
        Returns:
            Created RevenueSource object
        """
        required_fields = ['source_type', 'platform', 'amount']
        for field in required_fields:
            if field not in revenue_data:
                raise PayoutManagerError(f"Missing required field: {field}")
        
        revenue = RevenueSource(
            source_id=revenue_data.get('source_id', str(uuid.uuid4())),
            source_type=revenue_data['source_type'],
            platform=revenue_data['platform']
        )
        
        revenue.amount = decimal.Decimal(str(revenue_data['amount']))
        
        # Calculate fees and creator share
        platform_fee_rate = self._get_platform_fee_rate(revenue.platform, revenue.source_type)
        revenue.platform_fee = revenue.amount * platform_fee_rate
        
        # Calculate tax withholding
        creator = await self.get_creator_profile(creator_id)
        tax_rate = await self._calculate_tax_withholding_rate(creator, revenue)
        revenue.tax_withholding = revenue.amount * tax_rate
        
        # Calculate creator share
        revenue.creator_share = revenue.amount - revenue.platform_fee - revenue.tax_withholding
        
        # Validate minimum amounts
        if revenue.creator_share <= 0:
            raise PayoutManagerError("Creator share must be positive")
        
        # Store revenue record
        await self._store_revenue_record(creator_id, revenue)
        
        # Update creator balance
        await self._update_creator_balance(creator_id, revenue.creator_share)
        
        # Check for automatic payout trigger
        await self._check_automatic_payout_trigger(creator_id)
        
        logger.info(f"Recorded revenue: {revenue.source_id} for creator {creator_id}")
        return revenue

    async def get_creator_revenue(self, creator_id: str, period: str = 'monthly') -> Dict[str, Any]:
        """
        Get comprehensive revenue analytics for creator.
        
        Args:
            creator_id: Creator ID
            period: Time period ('daily', 'weekly', 'monthly', 'yearly')
            
        Returns:
            Revenue analytics data
        """
        # Calculate date range
        end_date = datetime.utcnow()
        if period == 'daily':
            start_date = end_date - timedelta(days=1)
        elif period == 'weekly':
            start_date = end_date - timedelta(weeks=1)
        elif period == 'monthly':
            start_date = end_date - timedelta(days=30)
        elif period == 'yearly':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Fetch revenue records
        revenue_records = await self._fetch_revenue_records(creator_id, start_date, end_date)
        
        # Calculate analytics
        total_revenue = sum(r.amount for r in revenue_records)
        total_creator_share = sum(r.creator_share for r in revenue_records)
        total_platform_fees = sum(r.platform_fee for r in revenue_records)
        total_tax_withholding = sum(r.tax_withholding for r in revenue_records)
        
        # Group by platform
        platform_breakdown = {}
        for record in revenue_records:
            if record.platform not in platform_breakdown:
                platform_breakdown[record.platform] = {
                    'revenue': decimal.Decimal('0.00'),
                    'creator_share': decimal.Decimal('0.00'),
                    'fees': decimal.Decimal('0.00'),
                    'count': 0
                }
            platform_breakdown[record.platform]['revenue'] += record.amount
            platform_breakdown[record.platform]['creator_share'] += record.creator_share
            platform_breakdown[record.platform]['fees'] += record.platform_fee
            platform_breakdown[record.platform]['count'] += 1
        
        # Group by source type
        source_type_breakdown = {}
        for record in revenue_records:
            if record.source_type not in source_type_breakdown:
                source_type_breakdown[record.source_type] = {
                    'revenue': decimal.Decimal('0.00'),
                    'creator_share': decimal.Decimal('0.00'),
                    'count': 0
                }
            source_type_breakdown[record.source_type]['revenue'] += record.amount
            source_type_breakdown[record.source_type]['creator_share'] += record.creator_share
            source_type_breakdown[record.source_type]['count'] += 1
        
        analytics = {
            'creator_id': creator_id,
            'period': period,
            'summary': {
                'total_revenue': float(total_revenue),
                'total_creator_share': float(total_creator_share),
                'total_platform_fees': float(total_platform_fees),
                'total_tax_withholding': float(total_tax_withholding),
                'revenue_count': len(revenue_records),
                'average_revenue': float(total_revenue / len(revenue_records)) if revenue_records else 0
            },
            'platform_breakdown': {
                platform: {
                    'revenue': float(data['revenue']),
                    'creator_share': float(data['creator_share']),
                    'fees': float(data['fees']),
                    'count': data['count'],
                    'percentage': float(data['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
                }
                for platform, data in platform_breakdown.items()
            },
            'source_type_breakdown': {
                source_type: {
                    'revenue': float(data['revenue']),
                    'creator_share': float(data['creator_share']),
                    'count': data['count'],
                    'percentage': float(data['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
                }
                for source_type, data in source_type_breakdown.items()
            },
            'growth_metrics': await self._calculate_revenue_growth_metrics(creator_id, period),
            'optimization_insights': await self._generate_revenue_optimization_insights(creator_id, revenue_records)
        }
        
        return analytics

    # Payout Processing
    async def process_payout(self, creator_id: str, amount: Optional[decimal.Decimal] = None, 
                           method: Optional[PayoutMethod] = None) -> PayoutTransaction:
        """
        Process a payout for a creator.
        
        Args:
            creator_id: Creator ID
            amount: Optional specific amount (defaults to available balance)
            method: Optional payout method override
            
        Returns:
            Created PayoutTransaction object
        """
        creator = await self.get_creator_profile(creator_id)
        
        # Determine payout amount
        if amount is None:
            amount = creator.available_balance
        
        # Validate payout amount
        if amount <= 0:
            raise PayoutManagerError("Payout amount must be positive")
        
        if amount > creator.available_balance:
            raise PayoutManagerError("Insufficient available balance")
        
        if amount < creator.minimum_payout_amount:
            raise PayoutManagerError(f"Amount below minimum payout threshold: {creator.minimum_payout_amount}")
        
        # Determine payout method
        if method is None:
            method = creator.preferred_payout_method
        
        # Validate payout method
        await self._validate_payout_method(creator, method)
        
        # Create payout transaction
        transaction = PayoutTransaction(
            transaction_id=str(uuid.uuid4()),
            creator_id=creator_id,
            amount=amount
        )
        
        transaction.currency = creator.currency
        transaction.method = method
        transaction.gateway = await self._select_optimal_gateway(creator, method, amount)
        
        # Calculate fees
        transaction.fees = await self._calculate_payout_fees(creator, transaction)
        transaction.net_amount = amount - transaction.fees
        
        try:
            # Process payment through selected gateway
            gateway_result = await self._process_gateway_payout(transaction)
            
            transaction.gateway_transaction_id = gateway_result['transaction_id']
            transaction.status = PayoutStatus.PROCESSING
            transaction.processed_at = datetime.utcnow()
            
            # Update creator balance
            await self._deduct_from_balance(creator_id, amount)
            
            # Store transaction
            await self._store_payout_transaction(transaction)
            
            # Setup status monitoring
            await self._setup_payout_monitoring(transaction)
            
            logger.info(f"Initiated payout: {transaction.transaction_id} for creator {creator_id}")
            return transaction
            
        except Exception as e:
            transaction.status = PayoutStatus.FAILED
            transaction.error_message = str(e)
            await self._store_payout_transaction(transaction)
            
            logger.error(f"Payout failed: {transaction.transaction_id} - {e}")
            raise PayoutManagerError(f"Payout processing failed: {e}")

    async def get_payout_history(self, creator_id: str, limit: int = 50, status: Optional[PayoutStatus] = None) -> List[PayoutTransaction]:
        """
        Get payout history for a creator.
        
        Args:
            creator_id: Creator ID
            limit: Maximum number of transactions to return
            status: Optional status filter
            
        Returns:
            List of PayoutTransaction objects
        """
        transactions = await self._fetch_payout_transactions(creator_id, limit, status)
        return transactions

    async def get_payout_transaction(self, transaction_id: str) -> PayoutTransaction:
        """
        Get details of a specific payout transaction.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            PayoutTransaction object
        """
        transaction = await self._fetch_payout_transaction(transaction_id)
        
        # Update status if needed
        if transaction.status == PayoutStatus.PROCESSING:
            await self._update_transaction_status(transaction)
        
        return transaction

    # Automated Payout Management
    async def setup_automatic_payouts(self, creator_id: str, schedule_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Setup automatic payout scheduling for creator.
        
        Args:
            creator_id: Creator ID
            schedule_config: Automatic payout configuration
            
        Returns:
            Configuration confirmation
        """
        creator = await self.get_creator_profile(creator_id)
        
        # Validate schedule configuration
        valid_schedules = ['daily', 'weekly', 'monthly']
        schedule = schedule_config.get('schedule', 'weekly')
        if schedule not in valid_schedules:
            raise PayoutManagerError(f"Invalid schedule. Must be one of: {valid_schedules}")
        
        minimum_amount = decimal.Decimal(str(schedule_config.get('minimum_amount', creator.minimum_payout_amount)))
        
        # Store automatic payout configuration
        auto_config = {
            'creator_id': creator_id,
            'enabled': schedule_config.get('enabled', True),
            'schedule': schedule,
            'minimum_amount': minimum_amount,
            'payout_method': schedule_config.get('payout_method', creator.preferred_payout_method.value),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        await self._store_automatic_payout_config(auto_config)
        
        logger.info(f"Setup automatic payouts for creator: {creator_id}")
        return auto_config

    async def process_scheduled_payouts(self) -> Dict[str, Any]:
        """
        Process all scheduled automatic payouts.
        
        Returns:
            Processing summary
        """
        # Get all creators with automatic payouts enabled
        auto_configs = await self._fetch_automatic_payout_configs()
        
        processed = 0
        failed = 0
        total_amount = decimal.Decimal('0.00')
        
        for config in auto_configs:
            try:
                creator_id = config['creator_id']
                
                # Check if payout is due
                if await self._is_payout_due(config):
                    creator = await self.get_creator_profile(creator_id)
                    
                    # Check if minimum amount is met
                    if creator.available_balance >= config['minimum_amount']:
                        transaction = await self.process_payout(creator_id)
                        processed += 1
                        total_amount += transaction.amount
                        
                        logger.info(f"Processed automatic payout: {transaction.transaction_id}")
                    
            except Exception as e:
                failed += 1
                logger.error(f"Failed to process automatic payout for creator {config['creator_id']}: {e}")
        
        summary = {
            'processed_count': processed,
            'failed_count': failed,
            'total_amount': float(total_amount),
            'processed_at': datetime.utcnow()
        }
        
        logger.info(f"Processed scheduled payouts: {processed} successful, {failed} failed")
        return summary

    # Tax Compliance and Reporting
    async def generate_tax_report(self, creator_id: str, tax_year: int) -> Dict[str, Any]:
        """
        Generate comprehensive tax report for creator.
        
        Args:
            creator_id: Creator ID
            tax_year: Tax year
            
        Returns:
            Tax report data
        """
        # Calculate date range for tax year
        start_date = datetime(tax_year, 1, 1)
        end_date = datetime(tax_year, 12, 31, 23, 59, 59)
        
        # Fetch all revenue and payout data
        revenue_records = await self._fetch_revenue_records(creator_id, start_date, end_date)
        payout_transactions = await self._fetch_payout_transactions_by_date(creator_id, start_date, end_date)
        
        # Calculate totals
        total_gross_income = sum(r.amount for r in revenue_records)
        total_net_income = sum(r.creator_share for r in revenue_records)
        total_platform_fees = sum(r.platform_fee for r in revenue_records)
        total_tax_withholding = sum(r.tax_withholding for r in revenue_records)
        total_payouts = sum(t.amount for t in payout_transactions if t.status == PayoutStatus.COMPLETED)
        total_payout_fees = sum(t.fees for t in payout_transactions if t.status == PayoutStatus.COMPLETED)
        
        # Group by platform for detailed breakdown
        platform_income = {}
        for record in revenue_records:
            if record.platform not in platform_income:
                platform_income[record.platform] = {
                    'gross_income': decimal.Decimal('0.00'),
                    'net_income': decimal.Decimal('0.00'),
                    'fees': decimal.Decimal('0.00'),
                    'tax_withholding': decimal.Decimal('0.00')
                }
            platform_income[record.platform]['gross_income'] += record.amount
            platform_income[record.platform]['net_income'] += record.creator_share
            platform_income[record.platform]['fees'] += record.platform_fee
            platform_income[record.platform]['tax_withholding'] += record.tax_withholding
        
        # Generate tax forms data
        creator = await self.get_creator_profile(creator_id)
        tax_forms = await self._generate_tax_forms_data(creator, revenue_records, payout_transactions)
        
        tax_report = {
            'creator_id': creator_id,
            'tax_year': tax_year,
            'creator_info': {
                'name': creator.display_name,
                'tax_id': creator.tax_id,
                'country': creator.country,
                'currency': creator.currency
            },
            'income_summary': {
                'total_gross_income': float(total_gross_income),
                'total_net_income': float(total_net_income),
                'total_platform_fees': float(total_platform_fees),
                'total_tax_withholding': float(total_tax_withholding),
                'total_payouts_received': float(total_payouts),
                'total_payout_fees': float(total_payout_fees)
            },
            'platform_breakdown': {
                platform: {
                    'gross_income': float(data['gross_income']),
                    'net_income': float(data['net_income']),
                    'fees': float(data['fees']),
                    'tax_withholding': float(data['tax_withholding'])
                }
                for platform, data in platform_income.items()
            },
            'tax_forms': tax_forms,
            'deductions': await self._calculate_allowable_deductions(creator, payout_transactions),
            'compliance_status': await self._check_tax_compliance_status(creator),
            'generated_at': datetime.utcnow()
        }
        
        return tax_report

    # Analytics and Insights
    async def get_payout_analytics(self, creator_id: str = None, period: str = 'monthly') -> Dict[str, Any]:
        """
        Get comprehensive payout analytics.
        
        Args:
            creator_id: Optional creator ID (system-wide if None)
            period: Time period for analytics
            
        Returns:
            Payout analytics data
        """
        if creator_id:
            # Creator-specific analytics
            return await self._get_creator_payout_analytics(creator_id, period)
        else:
            # System-wide analytics
            return await self._get_system_payout_analytics(period)

    # Helper Methods for Enhanced Functionality
    async def _validate_creator_profile(self, creator: CreatorProfile) -> None:
        """Validate creator profile information"""
        if not creator.email or '@' not in creator.email:
            raise PayoutManagerError("Valid email address required")
        
        if not creator.country or len(creator.country) != 2:
            raise PayoutManagerError("Valid country code required")
        
        if creator.minimum_payout_amount < decimal.Decimal('1.00'):
            raise PayoutManagerError("Minimum payout amount must be at least $1.00")

    async def _setup_tax_compliance(self, creator: CreatorProfile) -> None:
        """Setup tax compliance for creator"""
        # Check country-specific tax requirements
        tax_requirements = await self._get_tax_requirements(creator.country)
        
        if tax_requirements['requires_tax_id'] and not creator.tax_id:
            creator.tax_status = TaxStatus.PENDING_DOCUMENTS
        else:
            creator.tax_status = TaxStatus.COMPLIANT

    async def _setup_payout_method(self, creator: CreatorProfile) -> None:
        """Setup payout method for creator"""
        # Validate payout method is supported in creator's country
        supported_methods = await self._get_supported_payout_methods(creator.country)
        
        if creator.preferred_payout_method not in supported_methods:
            # Fall back to most common supported method
            creator.preferred_payout_method = supported_methods[0] if supported_methods else PayoutMethod.BANK_TRANSFER

    async def _calculate_available_balance(self, creator_id: str) -> decimal.Decimal:
        """Calculate creator's available balance"""
        # This would query the database for the creator's current balance
        return decimal.Decimal('125.50')  # Sample value

    async def _calculate_pending_balance(self, creator_id: str) -> decimal.Decimal:
        """Calculate creator's pending balance"""
        # This would calculate balance from pending revenue sources
        return decimal.Decimal('45.25')  # Sample value

    async def _calculate_total_earnings(self, creator_id: str) -> decimal.Decimal:
        """Calculate creator's total lifetime earnings"""
        # This would sum all historical earnings
        return decimal.Decimal('2500.75')  # Sample value

    def _get_platform_fee_rate(self, platform: str, source_type: str) -> decimal.Decimal:
        """Get platform fee rate"""
        platform_fees = self.config.get('platform_fees', {})
        return decimal.Decimal(str(platform_fees.get(platform, {}).get(source_type, 0.05)))  # Default 5%

    async def _calculate_tax_withholding_rate(self, creator: CreatorProfile, revenue: RevenueSource) -> decimal.Decimal:
        """Calculate tax withholding rate"""
        # This would implement country-specific tax calculations
        if creator.country == 'US':
            return decimal.Decimal('0.24')  # 24% for US creators
        else:
            return decimal.Decimal('0.30')  # 30% for international creators

    async def _select_optimal_gateway(self, creator: CreatorProfile, method: PayoutMethod, amount: decimal.Decimal) -> str:
        """Select optimal payment gateway"""
        # Evaluate gateways based on fees, speed, and reliability
        best_gateway = None
        lowest_fee = decimal.Decimal('999999.99')
        
        for gateway_name, gateway_config in self.gateways.items():
            if not gateway_config['enabled']:
                continue
            
            if creator.country not in gateway_config.get('supported_countries', []):
                continue
            
            if creator.currency not in gateway_config.get('supported_currencies', []):
                continue
            
            # Calculate fees for this gateway
            fee = await self._calculate_gateway_fees(gateway_name, amount, creator.country)
            
            if fee < lowest_fee:
                lowest_fee = fee
                best_gateway = gateway_name
        
        return best_gateway or 'stripe'  # Default fallback

    # Additional helper methods for comprehensive functionality would continue here...

# Example usage and testing
async def main():
    """Example usage of Payout Manager integration"""
    
    # Initialize the Payout Manager
    config = {
        'gateways': {
            'stripe': {
                'enabled': True,
                'priority': 1,
                'supported_countries': ['US', 'CA', 'GB', 'AU'],
                'supported_currencies': ['USD', 'CAD', 'GBP', 'AUD'],
                'fees': {'fixed': 0.30, 'percentage': 0.029}
            },
            'paypal': {
                'enabled': True,
                'priority': 2,
                'supported_countries': ['US', 'CA', 'GB', 'AU', 'DE', 'FR'],
                'supported_currencies': ['USD', 'CAD', 'GBP', 'AUD', 'EUR'],
                'fees': {'fixed': 0.00, 'percentage': 0.035}
            }
        },
        'platform_fees': {
            'youtube': {'ads': 0.45, 'subscriptions': 0.30},
            'twitch': {'subscriptions': 0.50, 'tips': 0.05},
            'substack': {'subscriptions': 0.10}
        }
    }
    
    payout_manager = PayoutManager(config)
    
    async with payout_manager:
        try:
            # Register a creator
            creator_data = {
                'creator_id': 'creator_123',
                'username': 'test_creator',
                'email': 'creator@example.com',
                'country': 'US',
                'currency': 'USD',
                'payout_method': 'stripe_express',
                'minimum_payout': 25.00
            }
            
            creator = await payout_manager.register_creator(creator_data)
            print(f"Registered creator: {creator.username}")
            
            # Record some revenue
            revenue_data = {
                'source_type': 'subscription',
                'platform': 'youtube',
                'amount': 100.00
            }
            
            revenue = await payout_manager.record_revenue(creator.creator_id, revenue_data)
            print(f"Recorded revenue: ${revenue.creator_share}")
            
            # Process a payout
            # payout = await payout_manager.process_payout(creator.creator_id)
            # print(f"Processed payout: ${payout.amount}")
            
            # Get revenue analytics
            analytics = await payout_manager.get_creator_revenue(creator.creator_id)
            print(f"Total revenue: ${analytics['summary']['total_revenue']}")
            
            logger.info("Payout Manager integration example completed successfully")
            
        except PayoutManagerError as e:
            logger.error(f"Payout Manager error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run example
    asyncio.run(main())