"""
Financial Instruments - Advanced Financial Modeling and Investment Tracking

Ultra-advanced financial instruments system for content creators including
investment tracking, portfolio management, tax optimization, and financial analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 CRITICAL LEGAL WARNING:
This code and all associated intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, modification, distribution, or commercialization 
is STRICTLY PROHIBITED and will result in immediate legal action.

Contact: mlaiel@live.de for licensing inquiries and authorization.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Solution Architect
- Senior Backend Engineer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer & Automation Specialist
"""

from sqlalchemy import (
    Column, String, Text, DateTime, Float, Integer, Boolean, JSON, 
    ForeignKey, Index, Enum as SQLEnum, Numeric, UniqueConstraint,
    CheckConstraint, event
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional, Union

Base = declarative_base()


class InvestmentType(Enum):
    """Types of financial investments available to creators"""
    # Traditional investments
    STOCKS = "stocks"
    BONDS = "bonds"
    MUTUAL_FUNDS = "mutual_funds"
    ETF = "etf"
    INDEX_FUNDS = "index_funds"
    
    # Alternative investments
    REAL_ESTATE = "real_estate"
    REIT = "reit"
    COMMODITIES = "commodities"
    PRECIOUS_METALS = "precious_metals"
    
    # Creator-specific investments
    MUSIC_ROYALTIES = "music_royalties"
    CONTENT_LICENSING = "content_licensing"
    BRAND_EQUITY = "brand_equity"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    
    # Cryptocurrency and DeFi
    CRYPTOCURRENCY = "cryptocurrency"
    DEFI_STAKING = "defi_staking"
    NFT_INVESTMENTS = "nft_investments"
    YIELD_FARMING = "yield_farming"
    
    # Business investments
    STARTUP_EQUITY = "startup_equity"
    VENTURE_CAPITAL = "venture_capital"
    ANGEL_INVESTING = "angel_investing"
    BUSINESS_ACQUISITION = "business_acquisition"


class RiskLevel(Enum):
    """Investment risk levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    SPECULATIVE = "speculative"


class TaxCategory(Enum):
    """Tax categories for different income types"""
    ORDINARY_INCOME = "ordinary_income"
    CAPITAL_GAINS_SHORT = "capital_gains_short"
    CAPITAL_GAINS_LONG = "capital_gains_long"
    DIVIDEND_INCOME = "dividend_income"
    ROYALTY_INCOME = "royalty_income"
    BUSINESS_INCOME = "business_income"
    PASSIVE_INCOME = "passive_income"
    TAX_EXEMPT = "tax_exempt"


class FinancialAccount(Base):
    """User financial accounts for investment and tax management"""
    __tablename__ = "financial_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Account identification
    account_type = Column(String(50), nullable=False)  # brokerage, bank, crypto_wallet
    account_name = Column(String(255), nullable=False)
    account_number = Column(String(255))
    institution_name = Column(String(255))
    institution_code = Column(String(50))
    
    # Account details
    currency = Column(String(3), default="EUR")
    balance = Column(Numeric(15, 2), default=0)
    available_balance = Column(Numeric(15, 2), default=0)
    pending_balance = Column(Numeric(15, 2), default=0)
    
    # Investment settings
    risk_tolerance = Column(SQLEnum(RiskLevel), default=RiskLevel.MODERATE)
    investment_goals = Column(JSONB)
    auto_invest_enabled = Column(Boolean, default=False)
    auto_invest_amount = Column(Numeric(10, 2))
    auto_invest_frequency = Column(String(20))  # monthly, weekly, daily
    
    # Tax optimization
    tax_jurisdiction = Column(String(50))
    tax_optimization_enabled = Column(Boolean, default=True)
    tax_loss_harvesting = Column(Boolean, default=False)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_level = Column(String(50))
    
    # Security and access
    api_connected = Column(Boolean, default=False)
    last_sync = Column(DateTime(timezone=True))
    sync_frequency = Column(String(20), default="daily")
    
    # Metadata
    account_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    investments = relationship("Investment", back_populates="account")
    transactions = relationship("FinancialTransaction", back_populates="account")
    
    # Indexes
    __table_args__ = (
        Index("idx_financial_accounts_user", "user_id"),
        Index("idx_financial_accounts_type", "account_type"),
        Index("idx_financial_accounts_status", "is_active"),
    )


class Investment(Base):
    """Individual investment holdings and tracking"""
    __tablename__ = "investments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("financial_accounts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Investment identification
    symbol = Column(String(20))  # Stock symbol, crypto symbol, etc.
    name = Column(String(255), nullable=False)
    investment_type = Column(SQLEnum(InvestmentType), nullable=False)
    asset_class = Column(String(50))
    sector = Column(String(100))
    industry = Column(String(100))
    
    # Position details
    quantity = Column(Numeric(20, 8), nullable=False)
    average_cost_basis = Column(Numeric(15, 4))
    current_price = Column(Numeric(15, 4))
    market_value = Column(Numeric(15, 2))
    unrealized_gain_loss = Column(Numeric(15, 2))
    unrealized_gain_loss_percent = Column(Numeric(8, 4))
    
    # Purchase information
    purchase_date = Column(DateTime(timezone=True))
    purchase_price = Column(Numeric(15, 4))
    total_investment = Column(Numeric(15, 2))
    
    # Risk and performance
    risk_level = Column(SQLEnum(RiskLevel))
    beta = Column(Numeric(6, 4))
    volatility = Column(Numeric(8, 4))
    sharpe_ratio = Column(Numeric(6, 4))
    
    # Tax implications
    tax_category = Column(SQLEnum(TaxCategory))
    tax_lot_method = Column(String(20))  # FIFO, LIFO, specific_id
    holding_period = Column(Integer)  # days
    qualified_for_long_term = Column(Boolean, default=False)
    
    # Income generation
    dividend_yield = Column(Numeric(6, 4))
    dividend_frequency = Column(String(20))
    last_dividend_date = Column(DateTime(timezone=True))
    next_dividend_date = Column(DateTime(timezone=True))
    annual_income = Column(Numeric(12, 2))
    
    # Metadata and tracking
    acquisition_method = Column(String(50))  # purchase, gift, inheritance, etc.
    investment_goal = Column(String(100))
    notes = Column(Text)
    external_id = Column(String(255))  # For API synchronization
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("FinancialAccount", back_populates="investments")
    transactions = relationship("FinancialTransaction", back_populates="investment")
    performance_history = relationship("InvestmentPerformance", back_populates="investment")
    
    # Indexes
    __table_args__ = (
        Index("idx_investments_user", "user_id"),
        Index("idx_investments_account", "account_id"),
        Index("idx_investments_symbol", "symbol"),
        Index("idx_investments_type", "investment_type"),
        Index("idx_investments_status", "is_active"),
    )


class FinancialTransaction(Base):
    """Financial transactions including buys, sells, dividends, etc."""
    __tablename__ = "financial_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("financial_accounts.id"), nullable=False)
    investment_id = Column(UUID(as_uuid=True), ForeignKey("investments.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Transaction identification
    transaction_type = Column(String(50), nullable=False)  # buy, sell, dividend, split, etc.
    transaction_id = Column(String(255), unique=True)
    external_transaction_id = Column(String(255))
    
    # Transaction details
    quantity = Column(Numeric(20, 8))
    price = Column(Numeric(15, 4))
    gross_amount = Column(Numeric(15, 2), nullable=False)
    fees = Column(Numeric(10, 2), default=0)
    taxes = Column(Numeric(10, 2), default=0)
    net_amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    
    # Tax implications
    tax_category = Column(SQLEnum(TaxCategory))
    realized_gain_loss = Column(Numeric(15, 2))
    cost_basis_adjustment = Column(Numeric(15, 2))
    wash_sale_adjustment = Column(Numeric(15, 2))
    
    # Settlement and execution
    trade_date = Column(DateTime(timezone=True), nullable=False)
    settlement_date = Column(DateTime(timezone=True))
    execution_price = Column(Numeric(15, 4))
    execution_time = Column(DateTime(timezone=True))
    
    # Order information
    order_type = Column(String(20))  # market, limit, stop_loss, etc.
    order_id = Column(String(255))
    fill_status = Column(String(20))  # filled, partial, cancelled
    
    # Market data
    market_price_at_trade = Column(Numeric(15, 4))
    exchange = Column(String(50))
    market_hours = Column(Boolean, default=True)
    
    # Description and notes
    description = Column(Text)
    notes = Column(Text)
    
    # Metadata
    transaction_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("FinancialAccount", back_populates="transactions")
    investment = relationship("Investment", back_populates="transactions")
    
    # Indexes
    __table_args__ = (
        Index("idx_financial_transactions_user", "user_id"),
        Index("idx_financial_transactions_account", "account_id"),
        Index("idx_financial_transactions_investment", "investment_id"),
        Index("idx_financial_transactions_date", "trade_date"),
        Index("idx_financial_transactions_type", "transaction_type"),
    )


class InvestmentPerformance(Base):
    """Historical performance tracking for investments"""
    __tablename__ = "investment_performance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investment_id = Column(UUID(as_uuid=True), ForeignKey("investments.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Performance date and period
    performance_date = Column(DateTime(timezone=True), nullable=False)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly, quarterly, yearly
    
    # Price and value metrics
    opening_price = Column(Numeric(15, 4))
    closing_price = Column(Numeric(15, 4))
    high_price = Column(Numeric(15, 4))
    low_price = Column(Numeric(15, 4))
    volume = Column(Integer)
    market_value = Column(Numeric(15, 2))
    
    # Return calculations
    absolute_return = Column(Numeric(15, 2))
    percentage_return = Column(Numeric(8, 4))
    annualized_return = Column(Numeric(8, 4))
    risk_adjusted_return = Column(Numeric(8, 4))
    
    # Risk metrics
    volatility = Column(Numeric(8, 4))
    beta = Column(Numeric(6, 4))
    alpha = Column(Numeric(6, 4))
    sharpe_ratio = Column(Numeric(6, 4))
    max_drawdown = Column(Numeric(8, 4))
    
    # Income metrics
    dividend_income = Column(Numeric(12, 2))
    interest_income = Column(Numeric(12, 2))
    capital_gains = Column(Numeric(15, 2))
    total_income = Column(Numeric(15, 2))
    
    # Benchmark comparison
    benchmark_return = Column(Numeric(8, 4))
    relative_performance = Column(Numeric(8, 4))
    tracking_error = Column(Numeric(6, 4))
    
    # Metadata
    data_source = Column(String(100))
    calculation_method = Column(String(100))
    performance_metadata = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    investment = relationship("Investment", back_populates="performance_history")
    
    # Indexes
    __table_args__ = (
        Index("idx_investment_performance_investment", "investment_id"),
        Index("idx_investment_performance_date", "performance_date"),
        Index("idx_investment_performance_period", "period_type"),
        UniqueConstraint("investment_id", "performance_date", "period_type", 
                        name="uq_investment_performance_date_period"),
    )


class TaxOptimizationStrategy(Base):
    """Tax optimization strategies and recommendations"""
    __tablename__ = "tax_optimization_strategies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Strategy identification
    strategy_name = Column(String(255), nullable=False)
    strategy_type = Column(String(100), nullable=False)
    tax_year = Column(Integer, nullable=False)
    
    # Strategy details
    description = Column(Text)
    implementation_steps = Column(JSONB)
    required_actions = Column(JSONB)
    deadlines = Column(JSONB)
    
    # Impact analysis
    estimated_tax_savings = Column(Numeric(12, 2))
    confidence_level = Column(Numeric(4, 2))  # 0-100%
    risk_assessment = Column(String(50))
    
    # Implementation status
    status = Column(String(50), default="recommended")  # recommended, in_progress, completed, declined
    implementation_date = Column(DateTime(timezone=True))
    completion_date = Column(DateTime(timezone=True))
    
    # Related investments and transactions
    affected_investments = Column(ARRAY(String))
    recommended_transactions = Column(JSONB)
    
    # Professional advice
    advisor_notes = Column(Text)
    requires_professional_review = Column(Boolean, default=False)
    
    # Metadata
    strategy_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_tax_strategies_user", "user_id"),
        Index("idx_tax_strategies_year", "tax_year"),
        Index("idx_tax_strategies_status", "status"),
        Index("idx_tax_strategies_type", "strategy_type"),
    )


class PortfolioAllocation(Base):
    """Portfolio allocation tracking and rebalancing"""
    __tablename__ = "portfolio_allocations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("financial_accounts.id"))
    
    # Allocation identification
    allocation_name = Column(String(255), nullable=False)
    allocation_type = Column(String(50), nullable=False)  # target, actual, model
    effective_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Asset class allocations (percentages)
    stocks_allocation = Column(Numeric(5, 2), default=0)
    bonds_allocation = Column(Numeric(5, 2), default=0)
    real_estate_allocation = Column(Numeric(5, 2), default=0)
    commodities_allocation = Column(Numeric(5, 2), default=0)
    crypto_allocation = Column(Numeric(5, 2), default=0)
    cash_allocation = Column(Numeric(5, 2), default=0)
    alternative_allocation = Column(Numeric(5, 2), default=0)
    
    # Geographic allocations
    domestic_allocation = Column(Numeric(5, 2), default=0)
    international_developed_allocation = Column(Numeric(5, 2), default=0)
    emerging_markets_allocation = Column(Numeric(5, 2), default=0)
    
    # Sector allocations
    technology_allocation = Column(Numeric(5, 2), default=0)
    healthcare_allocation = Column(Numeric(5, 2), default=0)
    financials_allocation = Column(Numeric(5, 2), default=0)
    energy_allocation = Column(Numeric(5, 2), default=0)
    consumer_allocation = Column(Numeric(5, 2), default=0)
    industrials_allocation = Column(Numeric(5, 2), default=0)
    other_sectors_allocation = Column(Numeric(5, 2), default=0)
    
    # Rebalancing settings
    rebalancing_frequency = Column(String(20))  # monthly, quarterly, annually
    drift_threshold = Column(Numeric(4, 2), default=5)  # 5% default
    auto_rebalance_enabled = Column(Boolean, default=False)
    last_rebalance_date = Column(DateTime(timezone=True))
    next_rebalance_date = Column(DateTime(timezone=True))
    
    # Performance metrics
    total_value = Column(Numeric(15, 2))
    allocation_drift = Column(Numeric(6, 2))
    rebalancing_needed = Column(Boolean, default=False)
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    allocation_metadata = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_portfolio_allocations_user", "user_id"),
        Index("idx_portfolio_allocations_account", "account_id"),
        Index("idx_portfolio_allocations_type", "allocation_type"),
        Index("idx_portfolio_allocations_date", "effective_date"),
        CheckConstraint(
            "(stocks_allocation + bonds_allocation + real_estate_allocation + "
            "commodities_allocation + crypto_allocation + cash_allocation + "
            "alternative_allocation) <= 100",
            name="chk_total_allocation_valid"
        ),
    )


class CreatorRevenueDiversification(Base):
    """Revenue diversification tracking for content creators"""
    __tablename__ = "creator_revenue_diversification"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Analysis period
    analysis_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Revenue stream breakdown (percentages)
    streaming_revenue_percent = Column(Numeric(5, 2), default=0)
    licensing_revenue_percent = Column(Numeric(5, 2), default=0)
    brand_partnerships_percent = Column(Numeric(5, 2), default=0)
    merchandise_revenue_percent = Column(Numeric(5, 2), default=0)
    live_events_revenue_percent = Column(Numeric(5, 2), default=0)
    digital_sales_percent = Column(Numeric(5, 2), default=0)
    subscription_revenue_percent = Column(Numeric(5, 2), default=0)
    investment_income_percent = Column(Numeric(5, 2), default=0)
    other_revenue_percent = Column(Numeric(5, 2), default=0)
    
    # Platform diversification
    spotify_revenue_percent = Column(Numeric(5, 2), default=0)
    youtube_revenue_percent = Column(Numeric(5, 2), default=0)
    instagram_revenue_percent = Column(Numeric(5, 2), default=0)
    tiktok_revenue_percent = Column(Numeric(5, 2), default=0)
    other_platforms_percent = Column(Numeric(5, 2), default=0)
    
    # Diversification metrics
    revenue_concentration_index = Column(Numeric(6, 4))  # Herfindahl index
    platform_concentration_index = Column(Numeric(6, 4))
    diversification_score = Column(Numeric(4, 2))  # 0-100 scale
    risk_level = Column(SQLEnum(RiskLevel))
    
    # Recommendations
    diversification_recommendations = Column(JSONB)
    risk_mitigation_strategies = Column(JSONB)
    growth_opportunities = Column(JSONB)
    
    # Total revenue tracking
    total_revenue = Column(Numeric(15, 2))
    total_investment_income = Column(Numeric(15, 2))
    passive_income_ratio = Column(Numeric(5, 2))
    
    # Metadata
    analysis_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_creator_diversification_user", "user_id"),
        Index("idx_creator_diversification_date", "analysis_date"),
        Index("idx_creator_diversification_period", "period_start", "period_end"),
    )


# SQLAlchemy event listeners
@event.listens_for(Investment, 'before_update')
def investment_before_update(mapper, connection, target):
    """Calculate performance metrics before updating investment"""
    if target.quantity and target.current_price and target.average_cost_basis:
        target.market_value = target.quantity * target.current_price
        target.unrealized_gain_loss = target.market_value - (target.quantity * target.average_cost_basis)
        if target.total_investment and target.total_investment > 0:
            target.unrealized_gain_loss_percent = (target.unrealized_gain_loss / target.total_investment) * 100


@event.listens_for(PortfolioAllocation, 'before_insert')
@event.listens_for(PortfolioAllocation, 'before_update')
def portfolio_allocation_validation(mapper, connection, target):
    """Validate portfolio allocation percentages"""
    total_allocation = (
        (target.stocks_allocation or 0) +
        (target.bonds_allocation or 0) +
        (target.real_estate_allocation or 0) +
        (target.commodities_allocation or 0) +
        (target.crypto_allocation or 0) +
        (target.cash_allocation or 0) +
        (target.alternative_allocation or 0)
    )
    
    # Allow for small rounding differences
    if total_allocation > 100.01:
        raise ValueError("Total allocation cannot exceed 100%")


# Export all models
__all__ = [
    'InvestmentType', 'RiskLevel', 'TaxCategory',
    'FinancialAccount', 'Investment', 'FinancialTransaction',
    'InvestmentPerformance', 'TaxOptimizationStrategy',
    'PortfolioAllocation', 'CreatorRevenueDiversification'
]
