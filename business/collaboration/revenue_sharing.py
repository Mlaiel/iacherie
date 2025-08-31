"""Advanced Revenue Sharing Engine for IA Influencer Agent
Professional revenue management and distribution system for collaborations

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator
from decimal import Decimal, ROUND_HALF_UP
import asyncio
import logging
import uuid
import json

logger = logging.getLogger(__name__)


class RevenueStreamType(Enum):
    """Types of revenue streams in collaborations"""
    STREAMING_ROYALTIES = "streaming_royalties"
    LICENSING_FEES = "licensing_fees"
    BRAND_SPONSORSHIP = "brand_sponsorship"
    MERCHANDISE_SALES = "merchandise_sales"
    LIVE_PERFORMANCE = "live_performance"
    ADVERTISING_REVENUE = "advertising_revenue"
    SUBSCRIPTION_FEES = "subscription_fees"
    DIGITAL_SALES = "digital_sales"
    AFFILIATE_COMMISSIONS = "affiliate_commissions"
    CONTENT_LICENSING = "content_licensing"


class PaymentStatus(Enum):
    """Payment processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    HELD = "held"
    CANCELLED = "cancelled"


class RevenueShareModel(Enum):
    """Revenue sharing models"""
    EQUAL_SPLIT = "equal_split"
    PERCENTAGE_BASED = "percentage_based"
    CONTRIBUTION_BASED = "contribution_based"
    ROLE_BASED = "role_based"
    PERFORMANCE_BASED = "performance_based"
    TIERED_SPLITS = "tiered_splits"
    HYBRID_MODEL = "hybrid_model"


@dataclass
class CollaboratorShare:
    """Individual collaborator revenue share configuration"""
    collaborator_id: str
    collaborator_name: str
    share_percentage: Decimal
    role: str
    contribution_details: Dict[str, Any] = field(default_factory=dict)
    minimum_payout: Decimal = Decimal('10.00')
    payment_method: str = "bank_transfer"
    payment_details: Dict[str, Any] = field(default_factory=dict)
    tax_information: Dict[str, Any] = field(default_factory=dict)
    special_terms: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RevenueMetrics:
    """Revenue performance metrics"""
    total_revenue: Decimal = Decimal('0.00')
    revenue_per_stream: Dict[RevenueStreamType, Decimal] = field(default_factory=dict)
    growth_rate: Decimal = Decimal('0.00')
    conversion_rate: Decimal = Decimal('0.00')
    average_transaction_value: Decimal = Decimal('0.00')
    revenue_per_collaborator: Dict[str, Decimal] = field(default_factory=dict)
    roi_percentage: Decimal = Decimal('0.00')
    profit_margin: Decimal = Decimal('0.00')


class RevenueTransaction(BaseModel):
    """Individual revenue transaction record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    collaboration_id: str
    revenue_stream: RevenueStreamType
    
    # Transaction details
    gross_amount: Decimal = Field(..., decimal_places=2)
    platform_fees: Decimal = Field(default=Decimal('0.00'), decimal_places=2)
    service_fees: Decimal = Field(default=Decimal('0.00'), decimal_places=2)
    taxes: Decimal = Field(default=Decimal('0.00'), decimal_places=2)
    net_amount: Decimal = Field(decimal_places=2)
    
    # Source information
    platform_source: str
    source_content_id: Optional[str] = None
    transaction_reference: Optional[str] = None
    external_transaction_id: Optional[str] = None
    
    # Timing
    transaction_date: datetime
    reporting_period: str  # e.g., "2025-01", "2025-Q1"
    
    # Metadata
    currency: str = "EUR"
    exchange_rate: Decimal = Decimal('1.00')
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('net_amount', pre=True, always=True)
    def calculate_net_amount(cls, v, values):
        if v is None:
            gross = values.get('gross_amount', Decimal('0.00'))
            platform_fees = values.get('platform_fees', Decimal('0.00'))
            service_fees = values.get('service_fees', Decimal('0.00'))
            taxes = values.get('taxes', Decimal('0.00'))
            return gross - platform_fees - service_fees - taxes
        return v


class RevenueSharingAgreement(BaseModel):
    """Revenue sharing agreement model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    collaboration_id: str
    agreement_name: str = Field(..., min_length=5, max_length=200)
    
    # Sharing configuration
    sharing_model: RevenueShareModel
    collaborator_shares: List[CollaboratorShare]
    
    # Revenue streams included
    included_streams: Set[RevenueStreamType] = Field(default_factory=set)
    excluded_streams: Set[RevenueStreamType] = Field(default_factory=set)
    
    # Terms and conditions
    agreement_start_date: datetime
    agreement_end_date: Optional[datetime] = None
    automatic_renewal: bool = False
    termination_notice_days: int = 30
    
    # Payment configuration
    payout_frequency: str = "monthly"  # monthly, quarterly, annually
    minimum_payout_threshold: Decimal = Field(default=Decimal('50.00'), decimal_places=2)
    payment_processing_delay_days: int = 7
    
    # Fee structure
    platform_commission: Decimal = Field(default=Decimal('0.05'), decimal_places=4)  # 5%
    processing_fee: Decimal = Field(default=Decimal('0.02'), decimal_places=4)  # 2%
    
    # Legal and compliance
    governing_law: str = "DE"  # Germany by default
    dispute_resolution: str = "arbitration"
    tax_handling: str = "individual_responsibility"
    
    # Status and tracking
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('collaborator_shares')
    def validate_share_percentages(cls, v):
        total_percentage = sum(share.share_percentage for share in v)
        if abs(total_percentage - Decimal('100.00')) > Decimal('0.01'):
            raise ValueError(f"Share percentages must total 100%, got {total_percentage}%")
        return v


class PayoutRecord(BaseModel):
    """Individual payout record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    collaboration_id: str
    collaborator_id: str
    
    # Payout details
    payout_amount: Decimal = Field(..., decimal_places=2)
    currency: str = "EUR"
    payout_period: str  # e.g., "2025-01"
    
    # Payment information
    payment_method: str
    payment_reference: str
    payment_status: PaymentStatus = PaymentStatus.PENDING
    
    # Transaction breakdown
    gross_earnings: Decimal = Field(decimal_places=2)
    deductions: Dict[str, Decimal] = Field(default_factory=dict)
    net_payout: Decimal = Field(decimal_places=2)
    
    # Timing
    payout_date: datetime
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Additional information
    included_transactions: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RevenueSharingEngine:
    """
    Advanced Revenue Sharing Engine
    Manages revenue collection, calculation, distribution, and reporting
    for collaborative content creation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.active_agreements: Dict[str, RevenueSharingAgreement] = {}
        self.revenue_transactions: List[RevenueTransaction] = []
        self.payout_history: List[PayoutRecord] = []
        self.payment_processors = {}
        self.tax_calculators = {}
        self.compliance_validators = {}
        
        # Initialize engine
        asyncio.create_task(self._initialize_engine())
    
    async def _initialize_engine(self):
        """Initialize revenue sharing engine"""
        try:
            await self._setup_payment_processors()
            await self._initialize_tax_calculators()
            await self._setup_compliance_validators()
            await self._load_exchange_rate_providers()
            await self._initialize_analytics_tracking()
            
            logger.info("Revenue sharing engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing revenue sharing engine: {str(e)}")
            raise
    
    async def create_revenue_agreement(
        self,
        agreement_data: Dict[str, Any]
    ) -> RevenueSharingAgreement:
        """
        Create a new revenue sharing agreement
        """
        try:
            # Validate agreement data
            validated_data = await self._validate_agreement_data(agreement_data)
            
            # Create agreement
            agreement = RevenueSharingAgreement(**validated_data)
            
            # Store agreement
            self.active_agreements[agreement.id] = agreement
            
            # Setup automated tracking
            await self._setup_automated_tracking(agreement)
            
            # Generate agreement documentation
            documentation = await self._generate_agreement_documentation(agreement)
            
            logger.info(f"Created revenue sharing agreement: {agreement.id}")
            
            return agreement
            
        except Exception as e:
            logger.error(f"Error creating revenue agreement: {str(e)}")
            raise
    
    async def record_revenue_transaction(
        self,
        transaction_data: Dict[str, Any]
    ) -> RevenueTransaction:
        """
        Record a new revenue transaction
        """
        try:
            # Validate transaction data
            validated_data = await self._validate_transaction_data(transaction_data)
            
            # Create transaction record
            transaction = RevenueTransaction(**validated_data)
            
            # Store transaction
            self.revenue_transactions.append(transaction)
            
            # Process revenue sharing
            await self._process_revenue_sharing(transaction)
            
            # Update metrics
            await self._update_revenue_metrics(transaction)
            
            # Check payout thresholds
            await self._check_payout_thresholds(transaction.collaboration_id)
            
            logger.info(f"Recorded revenue transaction: {transaction.id}")
            
            return transaction
            
        except Exception as e:
            logger.error(f"Error recording revenue transaction: {str(e)}")
            raise
    
    async def calculate_revenue_shares(
        self,
        collaboration_id: str,
        period: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate revenue shares for a collaboration
        """
        try:
            if collaboration_id not in self.active_agreements:
                raise ValueError(f"No active agreement found for collaboration {collaboration_id}")
            
            agreement = self.active_agreements[collaboration_id]
            
            # Get relevant transactions
            transactions = await self._get_transactions_for_period(
                collaboration_id, period
            )
            
            # Calculate total revenue
            total_revenue = sum(
                transaction.net_amount for transaction in transactions
            )
            
            # Calculate individual shares
            collaborator_shares = {}
            for collaborator in agreement.collaborator_shares:
                share_amount = total_revenue * (collaborator.share_percentage / Decimal('100'))
                collaborator_shares[collaborator.collaborator_id] = {
                    'collaborator_name': collaborator.collaborator_name,
                    'share_percentage': collaborator.share_percentage,
                    'share_amount': share_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                    'role': collaborator.role,
                    'transaction_count': len(transactions)
                }
            
            # Generate detailed breakdown
            breakdown = await self._generate_revenue_breakdown(
                transactions, agreement
            )
            
            return {
                'collaboration_id': collaboration_id,
                'period': period,
                'total_revenue': total_revenue,
                'collaborator_shares': collaborator_shares,
                'revenue_breakdown': breakdown,
                'calculated_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error calculating revenue shares: {str(e)}")
            return {
                'collaboration_id': collaboration_id,
                'error': str(e),
                'calculated_at': datetime.utcnow()
            }
    
    async def process_payouts(
        self,
        collaboration_id: str,
        payout_period: str
    ) -> Dict[str, Any]:
        """
        Process payouts for a collaboration period
        """
        try:
            # Calculate current shares
            shares_calculation = await self.calculate_revenue_shares(
                collaboration_id, payout_period
            )
            
            if 'error' in shares_calculation:
                return shares_calculation
            
            agreement = self.active_agreements[collaboration_id]
            payout_results = []
            
            # Process individual payouts
            for collaborator_id, share_data in shares_calculation['collaborator_shares'].items():
                share_amount = share_data['share_amount']
                
                # Check minimum payout threshold
                collaborator_config = next(
                    (c for c in agreement.collaborator_shares if c.collaborator_id == collaborator_id),
                    None
                )
                
                if collaborator_config and share_amount >= collaborator_config.minimum_payout:
                    payout_result = await self._process_individual_payout(
                        collaboration_id, collaborator_id, share_amount, 
                        payout_period, collaborator_config
                    )
                    payout_results.append(payout_result)
                else:
                    # Amount below threshold, carry forward
                    payout_results.append({
                        'collaborator_id': collaborator_id,
                        'status': 'carried_forward',
                        'amount': share_amount,
                        'reason': 'Below minimum payout threshold'
                    })
            
            # Update agreement status
            agreement.updated_at = datetime.utcnow()
            
            return {
                'collaboration_id': collaboration_id,
                'payout_period': payout_period,
                'total_payouts_processed': len([p for p in payout_results if p['status'] == 'processed']),
                'total_amount_paid': sum(
                    p.get('amount', Decimal('0.00')) 
                    for p in payout_results 
                    if p['status'] == 'processed'
                ),
                'payout_results': payout_results,
                'processed_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error processing payouts: {str(e)}")
            return {
                'collaboration_id': collaboration_id,
                'error': str(e),
                'processed_at': datetime.utcnow()
            }
    
    async def generate_revenue_report(
        self,
        collaboration_id: str,
        report_period: str,
        report_type: str = "detailed"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive revenue report
        """
        try:
            # Get agreement and transactions
            agreement = self.active_agreements.get(collaboration_id)
            if not agreement:
                raise ValueError(f"No agreement found for collaboration {collaboration_id}")
            
            transactions = await self._get_transactions_for_period(
                collaboration_id, report_period
            )
            
            # Calculate metrics
            metrics = await self._calculate_period_metrics(transactions, agreement)
            
            # Generate visualizations data
            chart_data = await self._generate_chart_data(transactions, report_period)
            
            # Create detailed breakdown
            breakdown = await self._generate_detailed_breakdown(
                transactions, agreement, report_type
            )
            
            # Generate insights and recommendations
            insights = await self._generate_revenue_insights(metrics, transactions)
            
            return {
                'collaboration_id': collaboration_id,
                'report_period': report_period,
                'report_type': report_type,
                'metrics': metrics,
                'chart_data': chart_data,
                'breakdown': breakdown,
                'insights': insights,
                'generated_at': datetime.utcnow(),
                'agreement_summary': {
                    'sharing_model': agreement.sharing_model.value,
                    'collaborator_count': len(agreement.collaborator_shares),
                    'revenue_streams': len(agreement.included_streams)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating revenue report: {str(e)}")
            return {
                'collaboration_id': collaboration_id,
                'error': str(e),
                'generated_at': datetime.utcnow()
            }
    
    async def get_collaborator_earnings(
        self,
        collaborator_id: str,
        time_period: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Get earnings summary for a specific collaborator
        """
        try:
            # Find all collaborations for this collaborator
            collaborator_agreements = [
                agreement for agreement in self.active_agreements.values()
                if any(c.collaborator_id == collaborator_id for c in agreement.collaborator_shares)
            ]
            
            total_earnings = Decimal('0.00')
            collaboration_earnings = []
            
            for agreement in collaborator_agreements:
                # Get collaborator's share configuration
                collaborator_config = next(
                    c for c in agreement.collaborator_shares 
                    if c.collaborator_id == collaborator_id
                )
                
                # Calculate earnings for this collaboration
                collab_earnings = await self._calculate_collaborator_earnings(
                    agreement.collaboration_id, collaborator_id, time_period
                )
                
                collaboration_earnings.append({
                    'collaboration_id': agreement.collaboration_id,
                    'collaboration_name': agreement.agreement_name,
                    'share_percentage': collaborator_config.share_percentage,
                    'earnings': collab_earnings['total_earnings'],
                    'transaction_count': collab_earnings['transaction_count'],
                    'last_payout': collab_earnings.get('last_payout_date')
                })
                
                total_earnings += collab_earnings['total_earnings']
            
            # Get pending payouts
            pending_payouts = await self._get_pending_payouts(collaborator_id)
            
            # Generate performance insights
            performance_insights = await self._generate_collaborator_insights(
                collaborator_id, collaboration_earnings
            )
            
            return {
                'collaborator_id': collaborator_id,
                'time_period': time_period,
                'total_earnings': total_earnings,
                'collaboration_count': len(collaboration_earnings),
                'collaboration_earnings': collaboration_earnings,
                'pending_payouts': pending_payouts,
                'performance_insights': performance_insights,
                'generated_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting collaborator earnings: {str(e)}")
            return {
                'collaborator_id': collaborator_id,
                'error': str(e),
                'generated_at': datetime.utcnow()
            }
    
    # Private helper methods
    async def _setup_payment_processors(self):
        """Setup payment processing integrations"""
        self.payment_processors = {
            'stripe': {'initialized': True, 'supported_currencies': ['EUR', 'USD', 'GBP']},
            'paypal': {'initialized': True, 'supported_currencies': ['EUR', 'USD', 'GBP']},
            'wise': {'initialized': True, 'supported_currencies': ['EUR', 'USD', 'GBP', 'CAD']},
            'bank_transfer': {'initialized': True, 'supported_currencies': ['EUR']}
        }
    
    async def _initialize_tax_calculators(self):
        """Initialize tax calculation systems"""
        self.tax_calculators = {
            'DE': {'vat_rate': Decimal('0.19'), 'income_tax_rates': [0.14, 0.42, 0.45]},
            'US': {'sales_tax': Decimal('0.08'), 'income_tax_rates': [0.10, 0.22, 0.24]},
            'GB': {'vat_rate': Decimal('0.20'), 'income_tax_rates': [0.20, 0.40, 0.45]}
        }
    
    async def _setup_compliance_validators(self):
        """Setup compliance validation systems"""
        self.compliance_validators = {
            'gdpr': {'enabled': True, 'data_retention_days': 2555},  # 7 years
            'aml': {'enabled': True, 'transaction_threshold': Decimal('10000.00')},
            'kyc': {'enabled': True, 'verification_required': True}
        }
    
    async def _load_exchange_rate_providers(self):
        """Load exchange rate providers"""
        # Mock implementation
        pass
    
    async def _initialize_analytics_tracking(self):
        """Initialize analytics tracking"""
        # Mock implementation
        pass
    
    async def _validate_agreement_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate revenue sharing agreement data"""
        # Add comprehensive validation logic
        return data
    
    async def _validate_transaction_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate transaction data"""
        # Add comprehensive validation logic
        return data
    
    async def _setup_automated_tracking(self, agreement: RevenueSharingAgreement):
        """Setup automated revenue tracking for agreement"""
        # Implementation would setup automated tracking
        pass
    
    async def _generate_agreement_documentation(
        self, 
        agreement: RevenueSharingAgreement
    ) -> Dict[str, Any]:
        """Generate legal agreement documentation"""
        return {
            'agreement_document_url': f'/agreements/{agreement.id}/document.pdf',
            'terms_summary': 'Revenue sharing agreement with automated distribution',
            'legal_status': 'valid'
        }
    
    async def _process_revenue_sharing(self, transaction: RevenueTransaction):
        """Process revenue sharing for transaction"""
        # Implementation would handle the sharing logic
        pass
    
    async def _update_revenue_metrics(self, transaction: RevenueTransaction):
        """Update revenue metrics with new transaction"""
        # Implementation would update metrics
        pass
    
    async def _check_payout_thresholds(self, collaboration_id: str):
        """Check if payout thresholds are met"""
        # Implementation would check thresholds and trigger payouts
        pass
    
    async def _get_transactions_for_period(
        self, 
        collaboration_id: str, 
        period: Optional[str]
    ) -> List[RevenueTransaction]:
        """Get transactions for specific period"""
        transactions = [
            t for t in self.revenue_transactions 
            if t.collaboration_id == collaboration_id
        ]
        
        if period:
            # Filter by period (simplified)
            transactions = [t for t in transactions if t.reporting_period == period]
        
        return transactions
    
    async def _generate_revenue_breakdown(
        self, 
        transactions: List[RevenueTransaction], 
        agreement: RevenueSharingAgreement
    ) -> Dict[str, Any]:
        """Generate detailed revenue breakdown"""
        return {
            'by_stream': {},
            'by_platform': {},
            'by_month': {},
            'fees_breakdown': {'platform_fees': Decimal('0.00'), 'service_fees': Decimal('0.00')}
        }
    
    async def _process_individual_payout(
        self,
        collaboration_id: str,
        collaborator_id: str,
        amount: Decimal,
        period: str,
        config: CollaboratorShare
    ) -> Dict[str, Any]:
        """Process payout for individual collaborator"""
        try:
            # Create payout record
            payout = PayoutRecord(
                collaboration_id=collaboration_id,
                collaborator_id=collaborator_id,
                payout_amount=amount,
                payout_period=period,
                payment_method=config.payment_method,
                payment_reference=f"PAY_{collaboration_id}_{collaborator_id}_{period}",
                gross_earnings=amount,
                net_payout=amount,
                payout_date=datetime.utcnow()
            )
            
            # Process payment (mock)
            await asyncio.sleep(0.1)  # Simulate processing time
            payout.payment_status = PaymentStatus.COMPLETED
            payout.processed_at = datetime.utcnow()
            payout.completed_at = datetime.utcnow()
            
            # Store payout record
            self.payout_history.append(payout)
            
            return {
                'collaborator_id': collaborator_id,
                'status': 'processed',
                'amount': amount,
                'payout_id': payout.id,
                'payment_reference': payout.payment_reference
            }
            
        except Exception as e:
            return {
                'collaborator_id': collaborator_id,
                'status': 'failed',
                'amount': amount,
                'error': str(e)
            }
    
    async def _calculate_period_metrics(
        self, 
        transactions: List[RevenueTransaction], 
        agreement: RevenueSharingAgreement
    ) -> RevenueMetrics:
        """Calculate metrics for a specific period"""
        total_revenue = sum(t.net_amount for t in transactions)
        
        return RevenueMetrics(
            total_revenue=total_revenue,
            growth_rate=Decimal('0.15'),  # Mock data
            conversion_rate=Decimal('0.035'),
            average_transaction_value=total_revenue / len(transactions) if transactions else Decimal('0.00'),
            roi_percentage=Decimal('0.25'),
            profit_margin=Decimal('0.30')
        )
    
    async def _generate_chart_data(
        self, 
        transactions: List[RevenueTransaction], 
        period: str
    ) -> Dict[str, Any]:
        """Generate data for revenue charts"""
        return {
            'revenue_over_time': {'labels': [], 'data': []},
            'revenue_by_stream': {'labels': [], 'data': []},
            'collaborator_contributions': {'labels': [], 'data': []}
        }
    
    async def _generate_detailed_breakdown(
        self,
        transactions: List[RevenueTransaction],
        agreement: RevenueSharingAgreement,
        report_type: str
    ) -> Dict[str, Any]:
        """Generate detailed revenue breakdown"""
        return {
            'transaction_summary': {
                'total_transactions': len(transactions),
                'successful_transactions': len(transactions),
                'failed_transactions': 0
            },
            'stream_analysis': {},
            'platform_performance': {},
            'fee_analysis': {}
        }
    
    async def _generate_revenue_insights(
        self, 
        metrics: RevenueMetrics, 
        transactions: List[RevenueTransaction]
    ) -> List[str]:
        """Generate actionable revenue insights"""
        insights = []
        
        if metrics.growth_rate > Decimal('0.10'):
            insights.append("Revenue showing strong growth - consider scaling successful strategies")
        
        if len(transactions) > 100:
            insights.append("High transaction volume - optimize for efficiency")
        
        insights.append("Diversify revenue streams to reduce dependency")
        
        return insights
    
    async def _calculate_collaborator_earnings(
        self,
        collaboration_id: str,
        collaborator_id: str,
        time_period: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Calculate earnings for specific collaborator"""
        # Get relevant transactions
        transactions = await self._get_transactions_for_period(collaboration_id, None)
        
        # Filter by time period if provided
        if time_period:
            start_date, end_date = time_period
            transactions = [
                t for t in transactions 
                if start_date <= t.transaction_date <= end_date
            ]
        
        # Get agreement
        agreement = self.active_agreements[collaboration_id]
        collaborator_config = next(
            c for c in agreement.collaborator_shares 
            if c.collaborator_id == collaborator_id
        )
        
        # Calculate total earnings
        total_revenue = sum(t.net_amount for t in transactions)
        collaborator_earnings = total_revenue * (collaborator_config.share_percentage / Decimal('100'))
        
        # Get last payout
        collaborator_payouts = [
            p for p in self.payout_history 
            if p.collaborator_id == collaborator_id and p.collaboration_id == collaboration_id
        ]
        last_payout = max(collaborator_payouts, key=lambda p: p.payout_date) if collaborator_payouts else None
        
        return {
            'total_earnings': collaborator_earnings,
            'transaction_count': len(transactions),
            'last_payout_date': last_payout.payout_date if last_payout else None,
            'last_payout_amount': last_payout.payout_amount if last_payout else Decimal('0.00')
        }
    
    async def _get_pending_payouts(self, collaborator_id: str) -> List[Dict[str, Any]]:
        """Get pending payouts for collaborator"""
        pending = [
            {
                'collaboration_id': p.collaboration_id,
                'amount': p.payout_amount,
                'period': p.payout_period,
                'status': p.payment_status.value
            }
            for p in self.payout_history
            if p.collaborator_id == collaborator_id and p.payment_status == PaymentStatus.PENDING
        ]
        
        return pending
    
    async def _generate_collaborator_insights(
        self, 
        collaborator_id: str, 
        earnings_data: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate insights for collaborator performance"""
        insights = []
        
        if len(earnings_data) > 1:
            insights.append("Active in multiple collaborations - diversified income")
        
        total_earnings = sum(e['earnings'] for e in earnings_data)
        if total_earnings > Decimal('1000.00'):
            insights.append("Strong earning potential - consider expanding portfolio")
        
        insights.append("Regular payout schedule maintained")
        
        return insights
