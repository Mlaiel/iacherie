"""Monetization interfaces for IA Influencer Agent.

Defines interfaces for revenue tracking, payment processing,
licensing, revenue sharing and financial reporting.

Author: Fahed Mlaiel <mlaiel@live.de>
© 2025 - All rights reserved. Unauthorized use prohibited.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
from decimal import Decimal
from enum import Enum


class CurrencyType(Enum):
    """Supported currency types."""    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"


class PaymentMethod(Enum):
    """Supported payment methods."""    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"


class LicenseType(Enum):
    """Content licensing types."""    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    ROYALTY_FREE = "royalty_free"
    CREATIVE_COMMONS = "creative_commons"
    CUSTOM = "custom"


class RevenueSource(Enum):
    """Revenue source types."""    STREAMING = "streaming"
    LICENSING = "licensing"
    COLLABORATION = "collaboration"
    ADVERTISING = "advertising"
    MERCHANDISE = "merchandise"
    DONATIONS = "donations"


class RevenueTrackerInterface(ABC):
    """Interface for revenue tracking and management."""    
    @abstractmethod
    async def track_content_revenue(
        self,
        content_id: str,
        platform: str,
        revenue_amount: Decimal,
        currency: CurrencyType,
        period_start: datetime,
        period_end: datetime
    ) -> str:
        """        Track revenue for specific content.
        
        Args:
            content_id: Content identifier
            platform: Platform generating revenue
            revenue_amount: Revenue amount
            currency: Currency type
            period_start: Revenue period start
            period_end: Revenue period end
            
        Returns:
            Revenue tracking record ID
        """        pass
    
    @abstractmethod
    async def calculate_total_revenue(
        self,
        user_id: str,
        timeframe: str,
        currency: CurrencyType = CurrencyType.EUR
    ) -> Dict[str, Decimal]:
        """Calculate total revenue for user across all sources."""        pass
    
    @abstractmethod
    async def get_revenue_breakdown(
        self,
        user_id: str,
        timeframe: str
    ) -> Dict[str, Any]:
        """Get detailed revenue breakdown by source and platform."""        pass
    
    @abstractmethod
    async def predict_future_revenue(
        self,
        user_id: str,
        prediction_months: int
    ) -> Dict[str, Decimal]:
        """Predict future revenue based on historical data."""        pass
    
    @abstractmethod
    async def track_revenue_growth(
        self,
        user_id: str,
        comparison_period: str
    ) -> Dict[str, float]:
        """Track revenue growth metrics and trends."""        pass


class PaymentProcessorInterface(ABC):
    """Interface for payment processing operations."""    
    @abstractmethod
    async def setup_payment_account(
        self,
        user_id: str,
        payment_method: PaymentMethod,
        account_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Setup payment account for user.
        
        Args:
            user_id: User identifier
            payment_method: Chosen payment method
            account_details: Payment account configuration
            
        Returns:
            Payment account setup status and information
        """        pass
    
    @abstractmethod
    async def process_payment(
        self,
        payment_id: str,
        amount: Decimal,
        currency: CurrencyType,
        recipient_id: str,
        payment_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process payment to recipient."""        pass
    
    @abstractmethod
    async def schedule_recurring_payment(
        self,
        payer_id: str,
        recipient_id: str,
        amount: Decimal,
        currency: CurrencyType,
        frequency: str,
        start_date: datetime
    ) -> str:
        """Schedule recurring payment setup."""        pass
    
    @abstractmethod
    async def validate_payment_details(
        self,
        payment_method: PaymentMethod,
        payment_details: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Validate payment method details."""        pass
    
    @abstractmethod
    async def handle_payment_dispute(
        self,
        payment_id: str,
        dispute_reason: str,
        evidence: Dict[str, Any]
    ) -> str:
        """Handle payment dispute resolution."""        pass
    
    @abstractmethod
    async def calculate_payment_fees(
        self,
        amount: Decimal,
        currency: CurrencyType,
        payment_method: PaymentMethod
    ) -> Dict[str, Decimal]:
        """Calculate payment processing fees."""        pass


class LicensingInterface(ABC):
    """Interface for content licensing management."""    
    @abstractmethod
    async def create_license_agreement(
        self,
        content_id: str,
        licensor_id: str,
        license_terms: Dict[str, Any]
    ) -> str:
        """        Create content license agreement.
        
        Args:
            content_id: Content being licensed
            licensor_id: Content owner/licensor
            license_terms: License terms and conditions
            
        Returns:
            License agreement ID
        """        pass
    
    @abstractmethod
    async def purchase_content_license(
        self,
        license_id: str,
        buyer_id: str,
        payment_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Purchase license for content usage."""        pass
    
    @abstractmethod
    async def validate_license_usage(
        self,
        license_id: str,
        usage_details: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Validate if usage complies with license terms."""        pass
    
    @abstractmethod
    async def generate_license_certificate(
        self,
        license_id: str
    ) -> str:
        """Generate digital license certificate."""        pass
    
    @abstractmethod
    async def track_license_usage(
        self,
        license_id: str,
        usage_data: Dict[str, Any]
    ) -> bool:
        """Track and log license usage for compliance."""        pass
    
    @abstractmethod
    async def handle_license_violation(
        self,
        license_id: str,
        violation_details: Dict[str, Any]
    ) -> str:
        """Handle license violation and enforcement."""        pass


class RevenueSharingInterface(ABC):
    """Interface for revenue sharing in collaborations."""    
    @abstractmethod
    async def setup_revenue_sharing(
        self,
        collaboration_id: str,
        participants: List[str],
        sharing_terms: Dict[str, Any]
    ) -> str:
        """        Setup revenue sharing for collaboration.
        
        Args:
            collaboration_id: Collaboration identifier
            participants: List of participant user IDs
            sharing_terms: Revenue sharing terms and percentages
            
        Returns:
            Revenue sharing agreement ID
        """        pass
    
    @abstractmethod
    async def calculate_revenue_distribution(
        self,
        sharing_agreement_id: str,
        total_revenue: Decimal,
        currency: CurrencyType
    ) -> Dict[str, Decimal]:
        """Calculate revenue distribution among participants."""        pass
    
    @abstractmethod
    async def process_revenue_distribution(
        self,
        sharing_agreement_id: str,
        revenue_period: Dict[str, datetime]
    ) -> Dict[str, Any]:
        """Process and distribute revenue to participants."""        pass
    
    @abstractmethod
    async def update_sharing_terms(
        self,
        sharing_agreement_id: str,
        new_terms: Dict[str, Any],
        approval_required: bool = True
    ) -> bool:
        """Update revenue sharing terms with participant approval."""        pass
    
    @abstractmethod
    async def audit_revenue_sharing(
        self,
        sharing_agreement_id: str,
        audit_period: str
    ) -> Dict[str, Any]:
        """Audit revenue sharing calculations and distributions."""        pass


class FinancialReportingInterface(ABC):
    """Interface for financial reporting and analytics."""    
    @abstractmethod
    async def generate_income_statement(
        self,
        user_id: str,
        period_start: datetime,
        period_end: datetime,
        currency: CurrencyType = CurrencyType.EUR
    ) -> Dict[str, Any]:
        """        Generate income statement for user.
        
        Args:
            user_id: User identifier
            period_start: Report period start
            period_end: Report period end
            currency: Report currency
            
        Returns:
            Income statement with revenue, expenses, and profit
        """        pass
    
    @abstractmethod
    async def generate_tax_report(
        self,
        user_id: str,
        tax_year: int,
        tax_jurisdiction: str
    ) -> Dict[str, Any]:
        """Generate tax report for specific jurisdiction."""        pass
    
    @abstractmethod
    async def calculate_profit_margins(
        self,
        user_id: str,
        timeframe: str
    ) -> Dict[str, float]:
        """Calculate profit margins by content and platform."""        pass
    
    @abstractmethod
    async def generate_roi_analysis(
        self,
        user_id: str,
        investment_categories: List[str],
        timeframe: str
    ) -> Dict[str, Any]:
        """Generate return on investment analysis."""        pass
    
    @abstractmethod
    async def create_financial_dashboard(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Create comprehensive financial dashboard data."""        pass
    
    @abstractmethod
    async def export_financial_data(
        self,
        user_id: str,
        export_format: str,
        date_range: Dict[str, datetime]
    ) -> str:
        """Export financial data in specified format (CSV, PDF, Excel)."""        pass
