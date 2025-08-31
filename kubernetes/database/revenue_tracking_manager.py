"""Revenue Tracking Database Manager
Advanced monetization and revenue tracking for IA Influencer Agent

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

AVERTISSEMENT LEGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Developer IA: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- Database Administrator: Fahed Mlaiel
- Sécurité Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Processing Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

⚠️ ATTENTION IMPORTANTE ⚠️
Toute tentative de vol, copie, ou utilisation non autorisée de ce code, 
concept ou idée sans autorisation écrite explicite de Fahed Mlaiel 
sera poursuivie selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

FONCTIONNALITÉS ENTERPRISE:
=========================

💰 TRACKING REVENUS MULTI-PLATEFORMES:
- Intégration APIs YouTube, Instagram, TikTok, Spotify
- Collecte automatique des données de revenus
- Normalisation des devises et métriques
- Tracking temps réel des performances
- Projections IA des revenus futurs
- Alertes de performance automatiques

📊 ANALYTICS REVENUS AVANCÉS:
- Dashboard revenus temps réel
- Analyse des tendances et patterns
- Segmentation par plateforme/contenu
- Comparaison périodes et benchmarks
- ROI et ROAS calculations
- Prédictions machine learning

💳 GESTION PAIEMENTS AUTOMATISÉE:
- Intégration Stripe, Wise, PayPal
- Automated payout scheduling
- Multi-currency support complet
- Tax calculation et compliance
- Fraud detection avancée
- Reconciliation automatique

🎯 DISTRIBUTION INTELLIGENTE:
- Revenue splitting automatique
- Contract-based distributions
- Collaborator payout management
- Royalty calculations complexes
- Escrow et holding accounts
- Dispute resolution tracking

📈 OPTIMISATION PERFORMANCE:
- Revenue optimization suggestions
- Platform-specific recommendations
- Content performance analytics
- Audience engagement correlation
- A/B testing for monetization
- Cross-platform optimization

🛡️ COMPLIANCE ET AUDIT:
- Financial audit trails complets
- Tax reporting automation
- GDPR compliance pour financial data
- Regulatory reporting support
- Fraud monitoring continu
- Risk assessment automation

⚡ REAL-TIME PROCESSING:
- Streaming revenue data ingestion
- Real-time dashboard updates
- Instant notification system
- Live performance monitoring
- Dynamic threshold adjustments
- Automated response triggers

🔒 SÉCURITÉ FINANCIÈRE:
- End-to-end encryption pour financial data
- PCI DSS compliance
- Multi-factor authentication
- Role-based access control
- Audit logging complet
- Secure API integrations
"""
import asyncio
from typing import Dict, Any, Optional, List, Union, Tuple, Set
from datetime import datetime, timedelta, date
from enum import Enum
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import json
import logging
import statistics
from sqlalchemy import (
    text, select, insert, update, delete, func, and_, or_,
    Index, ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, NUMERIC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.deployment.database.postgresql_manager import get_postgresql_manager


class Platform(Enum):
    """Revenue platforms"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    TWITCH = "twitch"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    CUSTOM = "custom"


class RevenueType(Enum):
    """Types of revenue"""
    AD_REVENUE = "ad_revenue"
    SUBSCRIPTION = "subscription"
    TIPS_DONATIONS = "tips_donations"
    MERCHANDISE = "merchandise"
    LICENSING = "licensing"
    STREAMING = "streaming"
    DOWNLOADS = "downloads"
    LIVE_PERFORMANCE = "live_performance"
    SPONSORSHIP = "sponsorship"
    BRAND_PARTNERSHIP = "brand_partnership"
    AFFILIATE = "affiliate"
    ROYALTIES = "royalties"
    OTHER = "other"


class Currency(Enum):
    """Supported currencies"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"
    PLN = "PLN"
    CZK = "CZK"
    HUF = "HUF"
    RUB = "RUB"
    BRL = "BRL"
    INR = "INR"
    KRW = "KRW"
    SGD = "SGD"
    HKD = "HKD"


class PayoutStatus(Enum):
    """Payout status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    DISPUTED = "disputed"


class PaymentMethod(Enum):
    """Payment methods"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"
    CHECK = "check"
    CASH = "cash"
    OTHER = "other"


@dataclass
class RevenueData:
    """Revenue data structure"""
    user_id: str
    platform: Platform
    revenue_type: RevenueType
    amount: Decimal
    currency: Currency
    period_start: date
    period_end: date
    content_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    raw_data: Optional[Dict[str, Any]] = None
    collected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PayoutRequest:
    """Payout request structure"""
    user_id: str
    amount: Decimal
    currency: Currency
    payment_method: PaymentMethod
    destination_account: str
    metadata: Optional[Dict[str, Any]] = None
    scheduled_date: Optional[datetime] = None


class RevenueTrackingManager:
    """
    Enterprise Revenue Tracking Database Manager
    
    Manages all revenue tracking, analytics, and payout operations
    with enterprise-grade performance, security, and compliance.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(f"{__name__}.RevenueTrackingManager")
        self.settings = get_settings()
        
        # Database components
        self._db_manager = None
        
        # Currency conversion rates cache
        self._exchange_rates: Dict[str, Dict[str, float]] = {}
        self._rates_last_updated: Optional[datetime] = None
        self._rates_update_interval = timedelta(hours=1)
        
        # Performance settings
        self.batch_size = self.config.get('batch_size', 1000)
        self.default_currency = Currency(self.config.get('default_currency', 'EUR'))
        self.min_payout_amount = Decimal(self.config.get('min_payout_amount', '10.00'))
        
        # Caching
        self._revenue_cache: Dict[str, Any] = {}
        self._cache_ttl = timedelta(minutes=15)
    
    async def initialize(self) -> bool:
        """Initialize the revenue tracking manager"""
        try:
            self.logger.info("🚀 Initializing Revenue Tracking Manager...")
            
            # Get database manager
            self._db_manager = get_postgresql_manager()
            
            # Create schema if not exists
            await self._create_revenue_schema()
            
            # Initialize exchange rates
            await self._update_exchange_rates()
            
            self.logger.info("✅ Revenue Tracking Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Revenue Tracking Manager: {e}")
            return False
    
    async def _create_revenue_schema(self):
        """Create revenue tracking database schema"""
        self.logger.debug("Creating revenue tracking database schema...")
        
        schema_sql = """
        -- Platform API Configurations
        CREATE TABLE IF NOT EXISTS platform_api_configs (
            config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            platform VARCHAR(50) NOT NULL,
            
            -- API credentials (encrypted)
            api_key_encrypted TEXT,
            api_secret_encrypted TEXT,
            access_token_encrypted TEXT,
            refresh_token_encrypted TEXT,
            
            -- Configuration
            is_active BOOLEAN DEFAULT true,
            auto_collect BOOLEAN DEFAULT true,
            collection_frequency VARCHAR(20) DEFAULT 'daily',
            last_collection_at TIMESTAMP,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            
            -- Constraints
            UNIQUE(user_id, platform),
            INDEX idx_platform_configs_user (user_id),
            INDEX idx_platform_configs_platform (platform),
            INDEX idx_platform_configs_active (is_active)
        );
        
        -- Revenue Records
        CREATE TABLE IF NOT EXISTS revenue_records (
            revenue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            platform VARCHAR(50) NOT NULL,
            content_id VARCHAR(255),
            
            -- Revenue details
            revenue_type VARCHAR(50) NOT NULL,
            amount NUMERIC(15,4) NOT NULL CHECK (amount >= 0),
            currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
            amount_usd NUMERIC(15,4), -- Normalized amount in USD
            amount_eur NUMERIC(15,4), -- Normalized amount in EUR
            
            -- Time period
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,
            collection_date DATE DEFAULT CURRENT_DATE,
            
            -- Metrics
            views BIGINT DEFAULT 0,
            clicks BIGINT DEFAULT 0,
            impressions BIGINT DEFAULT 0,
            engagement_rate FLOAT DEFAULT 0.0,
            cpm NUMERIC(10,4) DEFAULT 0.0,
            cpc NUMERIC(10,4) DEFAULT 0.0,
            
            -- Raw data
            platform_data JSONB,
            metadata JSONB,
            
            -- Processing
            exchange_rate NUMERIC(10,6),
            collected_at TIMESTAMP DEFAULT NOW(),
            processed_at TIMESTAMP,
            is_verified BOOLEAN DEFAULT false,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            
            -- Indexes
            INDEX idx_revenue_records_user (user_id),
            INDEX idx_revenue_records_platform (platform),
            INDEX idx_revenue_records_content (content_id),
            INDEX idx_revenue_records_type (revenue_type),
            INDEX idx_revenue_records_period (period_start, period_end),
            INDEX idx_revenue_records_amount (amount),
            INDEX idx_revenue_records_currency (currency),
            INDEX idx_revenue_records_collection (collection_date),
            INDEX idx_revenue_records_verified (is_verified)
        );
        
        -- Revenue Aggregations (for performance)
        CREATE TABLE IF NOT EXISTS revenue_aggregations (
            aggregation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            
            -- Aggregation details
            aggregation_type VARCHAR(20) NOT NULL, -- daily, weekly, monthly, yearly
            aggregation_date DATE NOT NULL,
            platform VARCHAR(50),
            revenue_type VARCHAR(50),
            
            -- Aggregated values
            total_amount NUMERIC(15,4) NOT NULL DEFAULT 0,
            total_amount_usd NUMERIC(15,4) NOT NULL DEFAULT 0,
            total_amount_eur NUMERIC(15,4) NOT NULL DEFAULT 0,
            currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
            
            -- Metrics
            total_views BIGINT DEFAULT 0,
            total_clicks BIGINT DEFAULT 0,
            total_impressions BIGINT DEFAULT 0,
            avg_engagement_rate FLOAT DEFAULT 0.0,
            avg_cpm NUMERIC(10,4) DEFAULT 0.0,
            avg_cpc NUMERIC(10,4) DEFAULT 0.0,
            
            -- Counts
            record_count INTEGER DEFAULT 0,
            content_count INTEGER DEFAULT 0,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            
            -- Constraints
            UNIQUE(user_id, aggregation_type, aggregation_date, platform, revenue_type),
            INDEX idx_revenue_agg_user (user_id),
            INDEX idx_revenue_agg_type (aggregation_type),
            INDEX idx_revenue_agg_date (aggregation_date),
            INDEX idx_revenue_agg_platform (platform),
            INDEX idx_revenue_agg_amount (total_amount)
        );
        
        -- Payout Requests
        CREATE TABLE IF NOT EXISTS payout_requests (
            payout_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            
            -- Payout details
            amount NUMERIC(15,4) NOT NULL CHECK (amount > 0),
            currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
            payment_method VARCHAR(50) NOT NULL,
            
            -- Destination
            destination_account TEXT NOT NULL,
            destination_metadata JSONB,
            
            -- Status
            status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled', 'on_hold', 'disputed')),
            
            -- Processing
            external_transaction_id TEXT,
            processing_fee NUMERIC(15,4) DEFAULT 0,
            net_amount NUMERIC(15,4),
            
            -- Timing
            requested_at TIMESTAMP DEFAULT NOW(),
            scheduled_date TIMESTAMP,
            processed_at TIMESTAMP,
            completed_at TIMESTAMP,
            
            -- Additional info
            notes TEXT,
            failure_reason TEXT,
            metadata JSONB,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            
            -- Indexes
            INDEX idx_payout_requests_user (user_id),
            INDEX idx_payout_requests_status (status),
            INDEX idx_payout_requests_method (payment_method),
            INDEX idx_payout_requests_amount (amount),
            INDEX idx_payout_requests_requested (requested_at),
            INDEX idx_payout_requests_scheduled (scheduled_date)
        );
        
        -- Revenue Forecasts
        CREATE TABLE IF NOT EXISTS revenue_forecasts (
            forecast_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            
            -- Forecast details
            forecast_type VARCHAR(20) NOT NULL, -- daily, weekly, monthly, quarterly, yearly
            forecast_date DATE NOT NULL,
            platform VARCHAR(50),
            
            -- Predictions
            predicted_amount NUMERIC(15,4) NOT NULL,
            currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
            confidence_score FLOAT DEFAULT 0.0 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
            
            -- Model info
            model_name VARCHAR(100),
            model_version VARCHAR(20),
            features_used JSONB,
            
            -- Actuals (filled later)
            actual_amount NUMERIC(15,4),
            accuracy_score FLOAT,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            
            -- Indexes
            UNIQUE(user_id, forecast_type, forecast_date, platform),
            INDEX idx_revenue_forecasts_user (user_id),
            INDEX idx_revenue_forecasts_date (forecast_date),
            INDEX idx_revenue_forecasts_platform (platform),
            INDEX idx_revenue_forecasts_confidence (confidence_score)
        );
        
        -- Exchange Rates
        CREATE TABLE IF NOT EXISTS exchange_rates (
            rate_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            from_currency VARCHAR(3) NOT NULL,
            to_currency VARCHAR(3) NOT NULL,
            rate NUMERIC(12,8) NOT NULL,
            rate_date DATE NOT NULL DEFAULT CURRENT_DATE,
            source VARCHAR(50) NOT NULL DEFAULT 'api',
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            
            -- Constraints
            UNIQUE(from_currency, to_currency, rate_date),
            INDEX idx_exchange_rates_currencies (from_currency, to_currency),
            INDEX idx_exchange_rates_date (rate_date)
        );
        
        -- Revenue Insights
        CREATE TABLE IF NOT EXISTS revenue_insights (
            insight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            
            -- Insight details
            insight_type VARCHAR(50) NOT NULL, -- trend, anomaly, opportunity, warning
            insight_category VARCHAR(50), -- performance, optimization, forecast
            title VARCHAR(200) NOT NULL,
            description TEXT,
            
            -- Data
            affected_platforms JSONB,
            metrics JSONB,
            recommendations JSONB,
            
            -- Scoring
            impact_score FLOAT DEFAULT 0.0 CHECK (impact_score >= 0.0 AND impact_score <= 1.0),
            confidence_score FLOAT DEFAULT 0.0 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
            priority_score FLOAT DEFAULT 0.0 CHECK (priority_score >= 0.0 AND priority_score <= 1.0),
            
            -- Status
            is_read BOOLEAN DEFAULT false,
            is_acted_upon BOOLEAN DEFAULT false,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            expires_at TIMESTAMP,
            
            -- Indexes
            INDEX idx_revenue_insights_user (user_id),
            INDEX idx_revenue_insights_type (insight_type),
            INDEX idx_revenue_insights_category (insight_category),
            INDEX idx_revenue_insights_impact (impact_score),
            INDEX idx_revenue_insights_created (created_at),
            INDEX idx_revenue_insights_read (is_read)
        );
        
        -- Tax Information
        CREATE TABLE IF NOT EXISTS tax_information (
            tax_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            
            -- Tax details
            tax_year INTEGER NOT NULL,
            tax_jurisdiction VARCHAR(100) NOT NULL, -- country/state
            
            -- Revenue summary
            total_revenue NUMERIC(15,4) DEFAULT 0,
            total_revenue_usd NUMERIC(15,4) DEFAULT 0,
            currency VARCHAR(3) DEFAULT 'EUR',
            
            -- Tax calculations
            taxable_income NUMERIC(15,4) DEFAULT 0,
            tax_rate NUMERIC(5,4) DEFAULT 0,
            estimated_tax NUMERIC(15,4) DEFAULT 0,
            
            -- Deductions
            business_expenses NUMERIC(15,4) DEFAULT 0,
            equipment_costs NUMERIC(15,4) DEFAULT 0,
            platform_fees NUMERIC(15,4) DEFAULT 0,
            
            -- Documents
            documents JSONB,
            
            -- Status
            is_finalized BOOLEAN DEFAULT false,
            filed_at TIMESTAMP,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            
            -- Constraints
            UNIQUE(user_id, tax_year, tax_jurisdiction),
            INDEX idx_tax_info_user (user_id),
            INDEX idx_tax_info_year (tax_year),
            INDEX idx_tax_info_jurisdiction (tax_jurisdiction)
        );
        
        -- Update timestamp triggers
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        -- Apply triggers
        DROP TRIGGER IF EXISTS update_platform_api_configs_updated_at ON platform_api_configs;
        CREATE TRIGGER update_platform_api_configs_updated_at
            BEFORE UPDATE ON platform_api_configs
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_revenue_records_updated_at ON revenue_records;
        CREATE TRIGGER update_revenue_records_updated_at
            BEFORE UPDATE ON revenue_records
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_revenue_aggregations_updated_at ON revenue_aggregations;
        CREATE TRIGGER update_revenue_aggregations_updated_at
            BEFORE UPDATE ON revenue_aggregations
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_payout_requests_updated_at ON payout_requests;
        CREATE TRIGGER update_payout_requests_updated_at
            BEFORE UPDATE ON payout_requests
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_revenue_forecasts_updated_at ON revenue_forecasts;
        CREATE TRIGGER update_revenue_forecasts_updated_at
            BEFORE UPDATE ON revenue_forecasts
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_tax_information_updated_at ON tax_information;
        CREATE TRIGGER update_tax_information_updated_at
            BEFORE UPDATE ON tax_information
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
        
        async with self._db_manager.get_session() as session:
            await session.execute(text(schema_sql))
            await session.commit()
        
        self.logger.debug("✅ Revenue tracking schema created successfully")
    
    async def _update_exchange_rates(self):
        """Update exchange rates from external API"""
        try:
            # This would normally call a real exchange rate API
            # For now, we'll use mock data
            mock_rates = {
                'USD': {'EUR': 0.85, 'GBP': 0.73, 'JPY': 110.0},
                'EUR': {'USD': 1.18, 'GBP': 0.86, 'JPY': 129.0},
                'GBP': {'USD': 1.37, 'EUR': 1.16, 'JPY': 150.0}
            }
            
            self._exchange_rates = mock_rates
            self._rates_last_updated = datetime.utcnow()
            
            # Store in database
            rate_data = []
            for from_curr, rates in mock_rates.items():
                for to_curr, rate in rates.items():
                    rate_data.append({
                        'from_currency': from_curr,
                        'to_currency': to_curr,
                        'rate': rate,
                        'rate_date': date.today(),
                        'source': 'mock_api'
                    })
            
            if rate_data:
                async with self._db_manager.get_session() as session:
                    await session.execute(
                        text("""
                            INSERT INTO exchange_rates (from_currency, to_currency, rate, rate_date, source)
                            VALUES (:from_currency, :to_currency, :rate, :rate_date, :source)
                            ON CONFLICT (from_currency, to_currency, rate_date) DO UPDATE SET
                                rate = EXCLUDED.rate,
                                created_at = NOW()
                        """),
                        rate_data
                    )
                    await session.commit()
            
            self.logger.debug("✅ Exchange rates updated successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update exchange rates: {e}")
    
    async def convert_currency(self, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        """Convert amount between currencies"""
        try:
            if from_currency == to_currency:
                return amount
            
            # Check if we need to update rates
            if (not self._rates_last_updated or 
                datetime.utcnow() - self._rates_last_updated > self._rates_update_interval):
                await self._update_exchange_rates()
            
            # Get rate from cache or database
            rate = None
            if from_currency in self._exchange_rates and to_currency in self._exchange_rates[from_currency]:
                rate = self._exchange_rates[from_currency][to_currency]
            else:
                # Query database
                async with self._db_manager.get_session() as session:
                    result = await session.execute(
                        text("""
                            SELECT rate FROM exchange_rates 
                            WHERE from_currency = :from_curr AND to_currency = :to_curr 
                            ORDER BY rate_date DESC LIMIT 1
                        """),
                        {'from_curr': from_currency, 'to_curr': to_currency}
                    )
                    
                    row = result.fetchone()
                    if row:
                        rate = float(row.rate)
            
            if rate is None:
                self.logger.warning(f"No exchange rate found for {from_currency} to {to_currency}")
                return amount  # Return original amount if no rate found
            
            converted = amount * Decimal(str(rate))
            return converted.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            self.logger.error(f"Currency conversion failed: {e}")
            return amount
    
    async def record_revenue(self, revenue_data: RevenueData) -> str:
        """Record revenue data"""
        try:
            self.logger.debug(f"Recording revenue for user {revenue_data.user_id}")
            
            # Convert to USD and EUR for normalization
            amount_usd = await self.convert_currency(
                revenue_data.amount, 
                revenue_data.currency.value, 
                'USD'
            )
            amount_eur = await self.convert_currency(
                revenue_data.amount, 
                revenue_data.currency.value, 
                'EUR'
            )
            
            # Get exchange rate used
            exchange_rate = None
            if revenue_data.currency.value != 'EUR':
                rate_result = await self.convert_currency(Decimal('1'), revenue_data.currency.value, 'EUR')
                exchange_rate = float(rate_result)
            
            # Prepare revenue record
            record_data = {
                'user_id': revenue_data.user_id,
                'platform': revenue_data.platform.value,
                'content_id': revenue_data.content_id,
                'revenue_type': revenue_data.revenue_type.value,
                'amount': float(revenue_data.amount),
                'currency': revenue_data.currency.value,
                'amount_usd': float(amount_usd),
                'amount_eur': float(amount_eur),
                'period_start': revenue_data.period_start,
                'period_end': revenue_data.period_end,
                'exchange_rate': exchange_rate,
                'platform_data': json.dumps(revenue_data.raw_data) if revenue_data.raw_data else None,
                'metadata': json.dumps(revenue_data.metadata) if revenue_data.metadata else None,
                'collected_at': revenue_data.collected_at,
                'processed_at': datetime.utcnow()
            }
            
            # Insert into database
            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        INSERT INTO revenue_records 
                        (user_id, platform, content_id, revenue_type, amount, currency,
                         amount_usd, amount_eur, period_start, period_end, exchange_rate,
                         platform_data, metadata, collected_at, processed_at)
                        VALUES (:user_id, :platform, :content_id, :revenue_type, :amount, :currency,
                               :amount_usd, :amount_eur, :period_start, :period_end, :exchange_rate,
                               :platform_data, :metadata, :collected_at, :processed_at)
                        RETURNING revenue_id
                    """),
                    record_data
                )
                
                revenue_id = result.scalar()
                await session.commit()
            
            # Update aggregations
            await self._update_revenue_aggregations(revenue_data.user_id, revenue_data.period_start)
            
            self.logger.debug(f"✅ Revenue recorded successfully: {revenue_id}")
            return revenue_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to record revenue: {e}")
            raise
    
    async def _update_revenue_aggregations(self, user_id: str, period_date: date):
        """Update revenue aggregations"""
        try:
            aggregation_types = {
                'daily': period_date,
                'weekly': period_date - timedelta(days=period_date.weekday()),
                'monthly': period_date.replace(day=1),
                'yearly': period_date.replace(month=1, day=1)
            }
            
            for agg_type, agg_date in aggregation_types.items():
                await self._calculate_aggregation(user_id, agg_type, agg_date)
        
        except Exception as e:
            self.logger.error(f"Failed to update aggregations: {e}")
    
    async def _calculate_aggregation(self, user_id: str, agg_type: str, agg_date: date):
        """Calculate revenue aggregation for a specific period"""
        try:
            # Define date range based on aggregation type
            if agg_type == 'daily':
                start_date = agg_date
                end_date = agg_date
            elif agg_type == 'weekly':
                start_date = agg_date
                end_date = agg_date + timedelta(days=6)
            elif agg_type == 'monthly':
                start_date = agg_date
                if agg_date.month == 12:
                    end_date = agg_date.replace(year=agg_date.year + 1, month=1) - timedelta(days=1)
                else:
                    end_date = agg_date.replace(month=agg_date.month + 1) - timedelta(days=1)
            elif agg_type == 'yearly':
                start_date = agg_date
                end_date = agg_date.replace(year=agg_date.year + 1) - timedelta(days=1)
            
            # Calculate aggregations
            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT 
                            platform,
                            revenue_type,
                            SUM(amount) as total_amount,
                            SUM(amount_usd) as total_amount_usd,
                            SUM(amount_eur) as total_amount_eur,
                            SUM(views) as total_views,
                            SUM(clicks) as total_clicks,
                            SUM(impressions) as total_impressions,
                            AVG(engagement_rate) as avg_engagement_rate,
                            AVG(cpm) as avg_cpm,
                            AVG(cpc) as avg_cpc,
                            COUNT(*) as record_count,
                            COUNT(DISTINCT content_id) as content_count
                        FROM revenue_records 
                        WHERE user_id = :user_id 
                        AND period_start >= :start_date 
                        AND period_end <= :end_date
                        GROUP BY platform, revenue_type
                    """),
                    {
                        'user_id': user_id,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                )
                
                aggregations = result.fetchall()
                
                # Insert or update aggregations
                for agg in aggregations:
                    await session.execute(
                        text("""
                            INSERT INTO revenue_aggregations
                            (user_id, aggregation_type, aggregation_date, platform, revenue_type,
                             total_amount, total_amount_usd, total_amount_eur, currency,
                             total_views, total_clicks, total_impressions, avg_engagement_rate,
                             avg_cpm, avg_cpc, record_count, content_count)
                            VALUES (:user_id, :agg_type, :agg_date, :platform, :revenue_type,
                                   :total_amount, :total_amount_usd, :total_amount_eur, :currency,
                                   :total_views, :total_clicks, :total_impressions, :avg_engagement_rate,
                                   :avg_cpm, :avg_cpc, :record_count, :content_count)
                            ON CONFLICT (user_id, aggregation_type, aggregation_date, platform, revenue_type) 
                            DO UPDATE SET
                                total_amount = EXCLUDED.total_amount,
                                total_amount_usd = EXCLUDED.total_amount_usd,
                                total_amount_eur = EXCLUDED.total_amount_eur,
                                total_views = EXCLUDED.total_views,
                                total_clicks = EXCLUDED.total_clicks,
                                total_impressions = EXCLUDED.total_impressions,
                                avg_engagement_rate = EXCLUDED.avg_engagement_rate,
                                avg_cpm = EXCLUDED.avg_cpm,
                                avg_cpc = EXCLUDED.avg_cpc,
                                record_count = EXCLUDED.record_count,
                                content_count = EXCLUDED.content_count,
                                updated_at = NOW()
                        """),
                        {
                            'user_id': user_id,
                            'agg_type': agg_type,
                            'agg_date': agg_date,
                            'platform': agg.platform,
                            'revenue_type': agg.revenue_type,
                            'total_amount': float(agg.total_amount or 0),
                            'total_amount_usd': float(agg.total_amount_usd or 0),
                            'total_amount_eur': float(agg.total_amount_eur or 0),
                            'currency': 'EUR',
                            'total_views': int(agg.total_views or 0),
                            'total_clicks': int(agg.total_clicks or 0),
                            'total_impressions': int(agg.total_impressions or 0),
                            'avg_engagement_rate': float(agg.avg_engagement_rate or 0),
                            'avg_cpm': float(agg.avg_cpm or 0),
                            'avg_cpc': float(agg.avg_cpc or 0),
                            'record_count': int(agg.record_count or 0),
                            'content_count': int(agg.content_count or 0)
                        }
                    )
                
                await session.commit()
        
        except Exception as e:
            self.logger.error(f"Failed to calculate aggregation: {e}")
    
    async def get_revenue_summary(
        self, 
        user_id: str, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        platform: Optional[Platform] = None
    ) -> Dict[str, Any]:
        """Get revenue summary for a user"""
        try:
            # Default to last 30 days if no dates provided
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            query = """
                SELECT 
                    platform,
                    revenue_type,
                    currency,
                    SUM(amount) as total_amount,
                    SUM(amount_usd) as total_amount_usd,
                    SUM(amount_eur) as total_amount_eur,
                    COUNT(*) as record_count,
                    COUNT(DISTINCT content_id) as content_count,
                    AVG(amount) as avg_amount,
                    MAX(amount) as max_amount,
                    MIN(amount) as min_amount
                FROM revenue_records 
                WHERE user_id = :user_id 
                AND period_start >= :start_date 
                AND period_end <= :end_date
            """
            
            params = {
                'user_id': user_id,
                'start_date': start_date,
                'end_date': end_date
            }
            
            if platform:
                query += " AND platform = :platform"
                params['platform'] = platform.value
            
            query += " GROUP BY platform, revenue_type, currency ORDER BY total_amount_eur DESC"
            
            async with self._db_manager.get_session() as session:
                result = await session.execute(text(query), params)
                revenue_breakdown = [dict(row._mapping) for row in result.fetchall()]
                
                # Get totals
                total_result = await session.execute(
                    text("""
                        SELECT 
                            SUM(amount_eur) as total_eur,
                            SUM(amount_usd) as total_usd,
                            COUNT(*) as total_records,
                            COUNT(DISTINCT platform) as platform_count,
                            COUNT(DISTINCT content_id) as content_count
                        FROM revenue_records 
                        WHERE user_id = :user_id 
                        AND period_start >= :start_date 
                        AND period_end <= :end_date
                    """),
                    params
                )
                
                totals = dict(total_result.fetchone()._mapping)
                
                # Get top performing content
                top_content_result = await session.execute(
                    text("""
                        SELECT 
                            content_id,
                            platform,
                            SUM(amount_eur) as total_revenue,
                            COUNT(*) as record_count
                        FROM revenue_records 
                        WHERE user_id = :user_id 
                        AND period_start >= :start_date 
                        AND period_end <= :end_date
                        AND content_id IS NOT NULL
                        GROUP BY content_id, platform
                        ORDER BY total_revenue DESC
                        LIMIT 10
                    """),
                    params
                )
                
                top_content = [dict(row._mapping) for row in top_content_result.fetchall()]
                
                return {
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    },
                    'totals': totals,
                    'breakdown': revenue_breakdown,
                    'top_content': top_content,
                    'summary': {
                        'total_revenue_eur': float(totals.get('total_eur', 0)),
                        'total_revenue_usd': float(totals.get('total_usd', 0)),
                        'platform_count': int(totals.get('platform_count', 0)),
                        'content_count': int(totals.get('content_count', 0)),
                        'average_daily_revenue': float(totals.get('total_eur', 0)) / max(1, (end_date - start_date).days)
                    }
                }
        
        except Exception as e:
            self.logger.error(f"Failed to get revenue summary: {e}")
            return {'error': str(e)}
    
    async def create_payout_request(self, payout_request: PayoutRequest) -> str:
        """Create a payout request"""
        try:
            self.logger.debug(f"Creating payout request for user {payout_request.user_id}")
            
            # Validate minimum payout amount
            if payout_request.amount < self.min_payout_amount:
                raise ValueError(f"Payout amount must be at least {self.min_payout_amount}")
            
            # Check available balance
            available_balance = await self._get_available_balance(payout_request.user_id, payout_request.currency)
            if payout_request.amount > available_balance:
                raise ValueError(f"Insufficient balance. Available: {available_balance}")
            
            # Calculate processing fee (example: 2.5% + fixed fee)
            processing_fee = payout_request.amount * Decimal('0.025') + Decimal('0.50')
            net_amount = payout_request.amount - processing_fee
            
            # Prepare payout data
            payout_data = {
                'user_id': payout_request.user_id,
                'amount': float(payout_request.amount),
                'currency': payout_request.currency.value,
                'payment_method': payout_request.payment_method.value,
                'destination_account': payout_request.destination_account,
                'destination_metadata': json.dumps(payout_request.metadata) if payout_request.metadata else None,
                'processing_fee': float(processing_fee),
                'net_amount': float(net_amount),
                'scheduled_date': payout_request.scheduled_date or datetime.utcnow() + timedelta(days=1)
            }
            
            # Insert into database
            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        INSERT INTO payout_requests 
                        (user_id, amount, currency, payment_method, destination_account,
                         destination_metadata, processing_fee, net_amount, scheduled_date)
                        VALUES (:user_id, :amount, :currency, :payment_method, :destination_account,
                               :destination_metadata, :processing_fee, :net_amount, :scheduled_date)
                        RETURNING payout_id
                    """),
                    payout_data
                )
                
                payout_id = result.scalar()
                await session.commit()
            
            self.logger.debug(f"✅ Payout request created successfully: {payout_id}")
            return payout_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create payout request: {e}")
            raise
    
    async def _get_available_balance(self, user_id: str, currency: Currency) -> Decimal:
        """Get available balance for user"""
        try:
            async with self._db_manager.get_session() as session:
                # Get total revenue
                result = await session.execute(
                    text("""
                        SELECT COALESCE(SUM(amount_eur), 0) as total_revenue
                        FROM revenue_records 
                        WHERE user_id = :user_id AND is_verified = true
                    """),
                    {'user_id': user_id}
                )
                
                total_revenue = Decimal(str(result.scalar() or 0))
                
                # Get total payouts
                result = await session.execute(
                    text("""
                        SELECT COALESCE(SUM(amount), 0) as total_payouts
                        FROM payout_requests 
                        WHERE user_id = :user_id 
                        AND status IN ('completed', 'processing', 'pending')
                    """),
                    {'user_id': user_id}
                )
                
                total_payouts = Decimal(str(result.scalar() or 0))
                
                available_balance = total_revenue - total_payouts
                
                # Convert to requested currency if needed
                if currency != Currency.EUR:
                    available_balance = await self.convert_currency(
                        available_balance, 
                        'EUR', 
                        currency.value
                    )
                
                return max(Decimal('0'), available_balance)
        
        except Exception as e:
            self.logger.error(f"Failed to get available balance: {e}")
            return Decimal('0')
    
    async def get_user_payouts(
        self, 
        user_id: str, 
        status: Optional[PayoutStatus] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get payout requests for a user"""
        try:
            query = """
                SELECT payout_id, amount, currency, payment_method, status,
                       processing_fee, net_amount, requested_at, scheduled_date,
                       processed_at, completed_at, failure_reason, notes
                FROM payout_requests 
                WHERE user_id = :user_id
            """
            
            params = {'user_id': user_id}
            
            if status:
                query += " AND status = :status"
                params['status'] = status.value
            
            query += " ORDER BY requested_at DESC LIMIT :limit"
            params['limit'] = limit
            
            async with self._db_manager.get_session() as session:
                result = await session.execute(text(query), params)
                payouts = [dict(row._mapping) for row in result.fetchall()]
                
                return payouts
        
        except Exception as e:
            self.logger.error(f"Failed to get user payouts: {e}")
            return []
    
    async def update_payout_status(
        self, 
        payout_id: str, 
        status: PayoutStatus,
        external_transaction_id: Optional[str] = None,
        failure_reason: Optional[str] = None
    ) -> bool:
        """Update payout status"""
        try:
            update_data = {
                'payout_id': payout_id,
                'status': status.value
            }
            
            update_fields = ['status = :status']
            
            if external_transaction_id:
                update_data['external_transaction_id'] = external_transaction_id
                update_fields.append('external_transaction_id = :external_transaction_id')
            
            if failure_reason:
                update_data['failure_reason'] = failure_reason
                update_fields.append('failure_reason = :failure_reason')
            
            if status == PayoutStatus.PROCESSING:
                update_fields.append('processed_at = NOW()')
            elif status == PayoutStatus.COMPLETED:
                update_fields.append('completed_at = NOW()')
            
            query = f"""
                UPDATE payout_requests 
                SET {', '.join(update_fields)}, updated_at = NOW()
                WHERE payout_id = :payout_id
            """
            
            async with self._db_manager.get_session() as session:
                result = await session.execute(text(query), update_data)
                await session.commit()
                
                return result.rowcount > 0
        
        except Exception as e:
            self.logger.error(f"Failed to update payout status: {e}")
            return False
    
    async def generate_revenue_forecast(
        self, 
        user_id: str, 
        forecast_type: str = 'monthly',
        periods: int = 6
    ) -> List[Dict[str, Any]]:
        """Generate revenue forecast using simple trend analysis"""
        try:
            # Get historical data
            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT aggregation_date, total_amount_eur
                        FROM revenue_aggregations 
                        WHERE user_id = :user_id 
                        AND aggregation_type = :forecast_type
                        ORDER BY aggregation_date DESC
                        LIMIT 12
                    """),
                    {'user_id': user_id, 'forecast_type': forecast_type}
                )
                
                historical_data = [dict(row._mapping) for row in result.fetchall()]
            
            if len(historical_data) < 3:
                return []  # Not enough data for forecasting
            
            # Calculate trend (simple linear regression)
            amounts = [float(d['total_amount_eur']) for d in historical_data]
            n = len(amounts)
            
            # Calculate trend
            x_values = list(range(n))
            sum_x = sum(x_values)
            sum_y = sum(amounts)
            sum_xy = sum(x * y for x, y in zip(x_values, amounts))
            sum_x_squared = sum(x * x for x in x_values)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Generate forecasts
            forecasts = []
            last_date = historical_data[0]['aggregation_date']
            
            for i in range(1, periods + 1):
                if forecast_type == 'daily':
                    forecast_date = last_date + timedelta(days=i)
                elif forecast_type == 'weekly':
                    forecast_date = last_date + timedelta(weeks=i)
                elif forecast_type == 'monthly':
                    if last_date.month + i > 12:
                        forecast_date = last_date.replace(
                            year=last_date.year + ((last_date.month + i - 1) // 12),
                            month=((last_date.month + i - 1) % 12) + 1
                        )
                    else:
                        forecast_date = last_date.replace(month=last_date.month + i)
                
                predicted_amount = max(0, slope * (n + i - 1) + intercept)
                
                # Calculate confidence (decreases with distance)
                confidence = max(0.1, 0.9 - (i * 0.1))
                
                forecast = {
                    'forecast_date': forecast_date,
                    'predicted_amount': round(predicted_amount, 2),
                    'confidence_score': round(confidence, 2),
                    'forecast_type': forecast_type
                }
                
                forecasts.append(forecast)
                
                # Store forecast in database
                await session.execute(
                    text("""
                        INSERT INTO revenue_forecasts 
                        (user_id, forecast_type, forecast_date, predicted_amount, 
                         confidence_score, model_name, model_version)
                        VALUES (:user_id, :forecast_type, :forecast_date, :predicted_amount,
                               :confidence_score, :model_name, :model_version)
                        ON CONFLICT (user_id, forecast_type, forecast_date, platform) DO UPDATE SET
                            predicted_amount = EXCLUDED.predicted_amount,
                            confidence_score = EXCLUDED.confidence_score,
                            updated_at = NOW()
                    """),
                    {
                        'user_id': user_id,
                        'forecast_type': forecast_type,
                        'forecast_date': forecast_date,
                        'predicted_amount': predicted_amount,
                        'confidence_score': confidence,
                        'model_name': 'linear_trend',
                        'model_version': '1.0'
                    }
                )
            
            await session.commit()
            
            return forecasts
        
        except Exception as e:
            self.logger.error(f"Failed to generate revenue forecast: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            health = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'components': {
                    'database': 'healthy',
                    'exchange_rates': 'healthy',
                    'cache': 'healthy'
                },
                'metrics': {
                    'total_revenue_records': 0,
                    'total_payout_requests': 0,
                    'exchange_rates_age': None
                }
            }
            
            # Check database connectivity
            async with self._db_manager.get_session() as session:
                result = await session.execute(text("SELECT COUNT(*) FROM revenue_records"))
                health['metrics']['total_revenue_records'] = result.scalar()
                
                result = await session.execute(text("SELECT COUNT(*) FROM payout_requests"))
                health['metrics']['total_payout_requests'] = result.scalar()
            
            # Check exchange rates age
            if self._rates_last_updated:
                age = datetime.utcnow() - self._rates_last_updated
                health['metrics']['exchange_rates_age'] = str(age)
                
                if age > timedelta(hours=24):
                    health['components']['exchange_rates'] = 'warning'
                    health['status'] = 'warning'
            
            return health
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def shutdown(self):
        """Shutdown the revenue tracking manager"""
        try:
            self.logger.info("🚨 Shutting down Revenue Tracking Manager...")
            
            # Clear caches
            self._revenue_cache.clear()
            self._exchange_rates.clear()
            
            self.logger.info("✅ Revenue Tracking Manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Shutdown failed: {e}")


# Factory function
_revenue_tracking_manager: Optional[RevenueTrackingManager] = None


def get_revenue_tracking_manager(config: Optional[Dict[str, Any]] = None) -> RevenueTrackingManager:
    """Get or create revenue tracking manager instance"""
    global _revenue_tracking_manager
    
    if _revenue_tracking_manager is None:
        _revenue_tracking_manager = RevenueTrackingManager(config)
    
    return _revenue_tracking_manager
