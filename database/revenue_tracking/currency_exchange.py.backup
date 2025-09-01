"""Currency Exchange & Multi-Currency Management

Système avancé de gestion multi-devises avec conversion temps réel,
hedging automatisé et optimisation des taux de change pour la plateforme IA Influencer Agent.

Architecture: Real-time currency conversion with automated hedging and rate optimization
Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe Projet: Lead AI Developer + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  AVERTISSEMENT DE PROPRIÉTÉ INTELLECTUELLE ⚠️
Ce code et concept sont la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Violation = Poursuites judiciaires selon le droit allemand et international.
"""
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import uuid
import logging
import asyncio
import aiohttp
from dataclasses import dataclass, field
from sqlalchemy import Column, String, Numeric, DateTime, Integer, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base

from ..models.base import BaseModel, TimestampMixin
from ...core.database import DatabaseManager
from ...core.security import EncryptionService
from ...utils.validation import ValidationService
from ...core.cache import CacheManager
from ...core.events import EventEmitter

logger = logging.getLogger(__name__)

Base = declarative_base()


class CurrencyCode(Enum):
    """Codes des devises supportées"""
    EUR = "EUR"  # Euro
    USD = "USD"  # Dollar américain
    GBP = "GBP"  # Livre sterling
    CAD = "CAD"  # Dollar canadien
    AUD = "AUD"  # Dollar australien
    JPY = "JPY"  # Yen japonais
    CHF = "CHF"  # Franc suisse
    SEK = "SEK"  # Couronne suédoise
    NOK = "NOK"  # Couronne norvégienne
    DKK = "DKK"  # Couronne danoise
    PLN = "PLN"  # Zloty polonais
    CZK = "CZK"  # Couronne tchèque
    HUF = "HUF"  # Forint hongrois
    BRL = "BRL"  # Real brésilien
    MXN = "MXN"  # Peso mexicain
    CNY = "CNY"  # Yuan chinois
    KRW = "KRW"  # Won sud-coréen
    INR = "INR"  # Roupie indienne
    SGD = "SGD"  # Dollar de Singapour
    HKD = "HKD"  # Dollar de Hong Kong
    NZD = "NZD"  # Dollar néo-zélandais
    RUB = "RUB"  # Rouble russe
    TRY = "TRY"  # Livre turque
    ZAR = "ZAR"  # Rand sud-africain


class ConversionType(Enum):
    """Types de conversion de devises"""
    SPOT = "spot"
    FORWARD = "forward"
    HEDGED = "hedged"
    OPTIMIZED = "optimized"


class HedgingStrategy(Enum):
    """Stratégies de couverture"""
    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"
    AI_OPTIMIZED = "ai_optimized"


@dataclass
class ExchangeRateModel(BaseModel, TimestampMixin):
    """
    Modèle des taux de change
    """
    __tablename__ = "exchange_rates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rate_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Paire de devises
    base_currency = Column(String(3), nullable=False, index=True)
    target_currency = Column(String(3), nullable=False, index=True)
    
    # Taux et métriques
    exchange_rate = Column(Numeric(12, 6), nullable=False)
    bid_rate = Column(Numeric(12, 6), nullable=True)
    ask_rate = Column(Numeric(12, 6), nullable=True)
    spread = Column(Numeric(8, 6), nullable=True)
    
    # Source et validité
    rate_source = Column(String(100), nullable=False)
    effective_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    expiration_date = Column(DateTime, nullable=True)
    
    # Volatilité et tendances
    volatility_score = Column(Numeric(5, 4), nullable=True)
    trend_indicator = Column(String(20), nullable=True)  # rising, falling, stable
    confidence_score = Column(Numeric(3, 2), nullable=False, default=1.0)
    
    # Métadonnées
    market_data = Column(JSONB, nullable=True)
    historical_context = Column(JSONB, nullable=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    is_real_time = Column(Boolean, nullable=False, default=True)


@dataclass
class CurrencyConversionModel(BaseModel, TimestampMixin):
    """
    Modèle des conversions de devises
    """
    __tablename__ = "currency_conversions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversion_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Identifiants liés
    revenue_record_id = Column(UUID(as_uuid=True), ForeignKey("revenue_records.id"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Détails de la conversion
    original_amount = Column(Numeric(15, 4), nullable=False)
    original_currency = Column(String(3), nullable=False)
    target_currency = Column(String(3), nullable=False)
    converted_amount = Column(Numeric(15, 4), nullable=False)
    
    # Taux appliqués
    exchange_rate_used = Column(Numeric(12, 6), nullable=False)
    conversion_fee = Column(Numeric(15, 4), nullable=False, default=0)
    hedging_cost = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Type et stratégie
    conversion_type = Column(String(20), nullable=False, default="spot")
    hedging_strategy = Column(String(20), nullable=False, default="none")
    
    # Timing
    conversion_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    settlement_date = Column(DateTime, nullable=True)
    
    # Optimisation
    optimization_applied = Column(Boolean, nullable=False, default=False)
    savings_achieved = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Métadonnées
    market_conditions = Column(JSONB, nullable=True)
    conversion_metadata = Column(JSONB, nullable=True)


@dataclass
class CurrencyHedgeModel(BaseModel, TimestampMixin):
    """
    Modèle des opérations de couverture
    """
    __tablename__ = "currency_hedges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hedge_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Configuration de la couverture
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    base_currency = Column(String(3), nullable=False)
    target_currency = Column(String(3), nullable=False)
    
    # Montants et ratios
    notional_amount = Column(Numeric(15, 4), nullable=False)
    hedge_ratio = Column(Numeric(3, 2), nullable=False, default=1.0)
    current_exposure = Column(Numeric(15, 4), nullable=False)
    
    # Instruments de couverture
    hedge_instrument = Column(String(50), nullable=False)  # forward, option, swap
    strike_rate = Column(Numeric(12, 6), nullable=True)
    premium_paid = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Dates
    hedge_start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    hedge_expiry_date = Column(DateTime, nullable=False)
    settlement_date = Column(DateTime, nullable=True)
    
    # Performance
    unrealized_pnl = Column(Numeric(15, 4), nullable=False, default=0)
    realized_pnl = Column(Numeric(15, 4), nullable=False, default=0)
    hedge_effectiveness = Column(Numeric(3, 2), nullable=True)
    
    # Status
    hedge_status = Column(String(20), nullable=False, default="active")
    auto_renewal = Column(Boolean, nullable=False, default=False)
    
    # Métadonnées
    hedge_parameters = Column(JSONB, nullable=True)
    performance_metrics = Column(JSONB, nullable=True)


@dataclass
class CurrencyPortfolioModel(BaseModel, TimestampMixin):
    """
    Modèle du portefeuille multi-devises
    """
    __tablename__ = "currency_portfolios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Propriétaire
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Configuration du portefeuille
    base_currency = Column(String(3), nullable=False, default="EUR")
    target_currencies = Column(ARRAY(String), nullable=False)
    
    # Expositions par devise
    currency_exposures = Column(JSONB, nullable=False)
    hedge_ratios = Column(JSONB, nullable=False)
    
    # Métriques de risque
    total_exposure = Column(Numeric(15, 4), nullable=False, default=0)
    var_95 = Column(Numeric(15, 4), nullable=True)  # Value at Risk 95%
    volatility = Column(Numeric(5, 4), nullable=True)
    correlation_matrix = Column(JSONB, nullable=True)
    
    # Stratégie de gestion
    risk_tolerance = Column(String(20), nullable=False, default="medium")
    auto_hedging_enabled = Column(Boolean, nullable=False, default=False)
    rebalancing_frequency = Column(String(20), nullable=False, default="monthly")
    
    # Performance
    total_return = Column(Numeric(15, 4), nullable=False, default=0)
    currency_return = Column(Numeric(15, 4), nullable=False, default=0)
    hedging_cost = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Dernière mise à jour
    last_rebalance_date = Column(DateTime, nullable=True)
    next_rebalance_date = Column(DateTime, nullable=True)


class ExchangeRateProvider:
    """
    Fournisseur de taux de change en temps réel
    """
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.api_keys = {
            'fixer': 'your_fixer_api_key',
            'exchangerate_api': 'your_exchangerate_api_key',
            'openexchangerates': 'your_openexchangerates_api_key'
        }
        self.fallback_providers = ['fixer', 'exchangerate_api', 'openexchangerates']
    
    async def get_exchange_rate(
        self,
        base_currency: str,
        target_currency: str,
        real_time: bool = True
    ) -> Optional[Decimal]:
        """
        Récupère le taux de change pour une paire de devises
        """
        cache_key = f"exchange_rate:{base_currency}:{target_currency}"
        
        # Vérification du cache
        if not real_time:
            cached_rate = await self.cache_manager.get(cache_key)
            if cached_rate:
                return Decimal(str(cached_rate))
        
        # Récupération en temps réel
        for provider in self.fallback_providers:
            try:
                rate = await self._fetch_rate_from_provider(
                    provider, base_currency, target_currency
                )
                if rate:
                    # Mise en cache (5 minutes)
                    await self.cache_manager.set(cache_key, str(rate), ttl=300)
                    return rate
                    
            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}")
                continue
        
        logger.error(f"All providers failed for {base_currency}/{target_currency}")
        return None
    
    async def _fetch_rate_from_provider(
        self,
        provider: str,
        base_currency: str,
        target_currency: str
    ) -> Optional[Decimal]:
        """
        Récupère le taux depuis un fournisseur spécifique
        """
        if provider == 'fixer':
            return await self._fetch_from_fixer(base_currency, target_currency)
        elif provider == 'exchangerate_api':
            return await self._fetch_from_exchangerate_api(base_currency, target_currency)
        elif provider == 'openexchangerates':
            return await self._fetch_from_openexchangerates(base_currency, target_currency)
        
        return None
    
    async def _fetch_from_fixer(
        self,
        base_currency: str,
        target_currency: str
    ) -> Optional[Decimal]:
        """
        Récupère le taux depuis Fixer.io
        """
        url = f"http://data.fixer.io/api/latest"
        params = {
            'access_key': self.api_keys['fixer'],
            'base': base_currency,
            'symbols': target_currency
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and target_currency in data.get('rates', {}):
                        return Decimal(str(data['rates'][target_currency]))
        
        return None
    
    async def get_multiple_rates(
        self,
        base_currency: str,
        target_currencies: List[str]
    ) -> Dict[str, Decimal]:
        """
        Récupère plusieurs taux simultanément
        """
        tasks = [
            self.get_exchange_rate(base_currency, target_currency)
            for target_currency in target_currencies
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        rates = {}
        for target_currency, result in zip(target_currencies, results):
            if isinstance(result, Decimal):
                rates[target_currency] = result
            else:
                logger.error(f"Failed to get rate for {base_currency}/{target_currency}")
        
        return rates


class CurrencyConversionEngine:
    """
    Moteur de conversion de devises avec optimisation
    """
    
    def __init__(self, db_session: Session, cache_manager: CacheManager):
        self.db_session = db_session
        self.cache_manager = cache_manager
        self.rate_provider = ExchangeRateProvider(cache_manager)
        self.event_emitter = EventEmitter()
    
    async def convert_currency(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        user_id: uuid.UUID,
        conversion_type: ConversionType = ConversionType.SPOT,
        optimize: bool = True
    ) -> CurrencyConversionModel:
        """
        Convertit un montant d'une devise à une autre
        """
        try:
            # Récupération du taux de change
            exchange_rate = await self._get_optimal_exchange_rate(
                from_currency, to_currency, conversion_type, optimize
            )
            
            if not exchange_rate:
                raise ValueError(f"Exchange rate not available for {from_currency}/{to_currency}")
            
            # Calcul de la conversion
            converted_amount = amount * exchange_rate
            
            # Calcul des frais
            conversion_fee = await self._calculate_conversion_fee(
                amount, from_currency, to_currency, user_id
            )
            
            # Application de l'optimisation
            savings = Decimal('0')
            if optimize:
                optimized_rate, savings = await self._apply_rate_optimization(
                    exchange_rate, amount, from_currency, to_currency
                )
                if optimized_rate:
                    exchange_rate = optimized_rate
                    converted_amount = amount * exchange_rate
            
            # Création de l'enregistrement
            conversion = CurrencyConversionModel(
                conversion_id=f"CONV_{datetime.utcnow().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}",
                user_id=user_id,
                original_amount=amount,
                original_currency=from_currency,
                target_currency=to_currency,
                converted_amount=converted_amount - conversion_fee,
                exchange_rate_used=exchange_rate,
                conversion_fee=conversion_fee,
                conversion_type=conversion_type.value,
                optimization_applied=optimize,
                savings_achieved=savings,
                market_conditions=await self._get_market_conditions(from_currency, to_currency)
            )
            
            # Sauvegarde
            self.db_session.add(conversion)
            await self.db_session.commit()
            
            # Émission d'événement
            await self.event_emitter.emit("currency_converted", {
                "conversion_id": conversion.conversion_id,
                "user_id": str(user_id),
                "amount": float(amount),
                "from_currency": from_currency,
                "to_currency": to_currency,
                "converted_amount": float(converted_amount)
            })
            
            logger.info(f"Currency conversion completed: {conversion.conversion_id}")
            return conversion
            
        except Exception as e:
            logger.error(f"Currency conversion failed: {e}")
            await self.db_session.rollback()
            raise
    
    async def _get_optimal_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
        conversion_type: ConversionType,
        optimize: bool
    ) -> Optional[Decimal]:
        """
        Récupère le taux de change optimal
        """
        if conversion_type == ConversionType.SPOT:
            rate = await self.rate_provider.get_exchange_rate(from_currency, to_currency)
            
            if optimize:
                # Application d'optimisations intelligentes
                optimized_rate = await self._optimize_spot_rate(rate, from_currency, to_currency)
                return optimized_rate or rate
            
            return rate
        
        elif conversion_type == ConversionType.FORWARD:
            return await self._get_forward_rate(from_currency, to_currency)
        
        elif conversion_type == ConversionType.HEDGED:
            return await self._get_hedged_rate(from_currency, to_currency)
        
        return None
    
    async def _optimize_spot_rate(
        self,
        base_rate: Decimal,
        from_currency: str,
        to_currency: str
    ) -> Optional[Decimal]:
        """
        Optimise le taux spot en utilisant différentes stratégies
        """
        # 1. Agrégation de plusieurs sources
        rates = await self._get_rates_from_multiple_sources(from_currency, to_currency)
        
        if len(rates) > 1:
            # Utilisation du meilleur taux disponible
            best_rate = max(rates)
            if best_rate > base_rate:
                return best_rate
        
        # 2. Timing optimal basé sur les patterns historiques
        optimal_timing_rate = await self._get_optimal_timing_rate(
            base_rate, from_currency, to_currency
        )
        
        if optimal_timing_rate and optimal_timing_rate > base_rate:
            return optimal_timing_rate
        
        return None
    
    async def _calculate_conversion_fee(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        user_id: uuid.UUID
    ) -> Decimal:
        """
        Calcule les frais de conversion
        """
        # Récupération du profil utilisateur pour les tarifs
        user_tier = await self._get_user_tier(user_id)
        
        # Barème des frais par niveau
        fee_rates = {
            'basic': Decimal('0.015'),      # 1.5%
            'premium': Decimal('0.010'),    # 1.0%
            'professional': Decimal('0.005'), # 0.5%
            'enterprise': Decimal('0.002')  # 0.2%
        }
        
        fee_rate = fee_rates.get(user_tier, fee_rates['basic'])
        
        # Frais minimum et maximum
        fee = amount * fee_rate
        min_fee = Decimal('0.50')  # 0.50 EUR minimum
        max_fee = Decimal('100.00')  # 100 EUR maximum
        
        return max(min_fee, min(fee, max_fee))


class CurrencyHedgingEngine:
    """
    Moteur de couverture de change automatisé
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.event_emitter = EventEmitter()
    
    async def create_hedge(
        self,
        user_id: uuid.UUID,
        base_currency: str,
        target_currency: str,
        notional_amount: Decimal,
        hedging_strategy: HedgingStrategy,
        hedge_ratio: Decimal = Decimal('1.0')
    ) -> CurrencyHedgeModel:
        """
        Crée une opération de couverture
        """
        try:
            # Détermination de l'instrument de couverture
            hedge_instrument = await self._select_hedge_instrument(
                hedging_strategy, base_currency, target_currency, notional_amount
            )
            
            # Calcul des paramètres de couverture
            hedge_parameters = await self._calculate_hedge_parameters(
                hedge_instrument, base_currency, target_currency, notional_amount
            )
            
            # Création de la couverture
            hedge = CurrencyHedgeModel(
                hedge_id=f"HEDGE_{datetime.utcnow().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}",
                user_id=user_id,
                base_currency=base_currency,
                target_currency=target_currency,
                notional_amount=notional_amount,
                hedge_ratio=hedge_ratio,
                current_exposure=notional_amount * hedge_ratio,
                hedge_instrument=hedge_instrument,
                strike_rate=hedge_parameters.get('strike_rate'),
                premium_paid=hedge_parameters.get('premium', Decimal('0')),
                hedge_expiry_date=hedge_parameters['expiry_date'],
                hedge_parameters=hedge_parameters
            )
            
            # Sauvegarde
            self.db_session.add(hedge)
            await self.db_session.commit()
            
            logger.info(f"Currency hedge created: {hedge.hedge_id}")
            return hedge
            
        except Exception as e:
            logger.error(f"Hedge creation failed: {e}")
            await self.db_session.rollback()
            raise
    
    async def monitor_hedge_performance(
        self,
        hedge: CurrencyHedgeModel
    ) -> Dict[str, Any]:
        """
        Surveille la performance d'une couverture
        """
        # Récupération du taux de change actuel
        current_rate = await self.rate_provider.get_exchange_rate(
            hedge.base_currency, hedge.target_currency
        )
        
        if not current_rate:
            return {'error': 'Unable to get current exchange rate'}
        
        # Calcul du P&L non réalisé
        if hedge.hedge_instrument == 'forward':
            unrealized_pnl = await self._calculate_forward_pnl(hedge, current_rate)
        elif hedge.hedge_instrument == 'option':
            unrealized_pnl = await self._calculate_option_pnl(hedge, current_rate)
        else:
            unrealized_pnl = Decimal('0')
        
        # Mise à jour de la couverture
        hedge.unrealized_pnl = unrealized_pnl
        
        # Calcul de l'efficacité de la couverture
        hedge_effectiveness = await self._calculate_hedge_effectiveness(hedge)
        hedge.hedge_effectiveness = hedge_effectiveness
        
        await self.db_session.commit()
        
        return {
            'hedge_id': hedge.hedge_id,
            'current_rate': float(current_rate),
            'unrealized_pnl': float(unrealized_pnl),
            'hedge_effectiveness': float(hedge_effectiveness) if hedge_effectiveness else None,
            'recommendation': await self._generate_hedge_recommendation(hedge)
        }
    
    async def auto_hedge_portfolio(
        self,
        user_id: uuid.UUID,
        target_hedge_ratio: Decimal = Decimal('0.8')
    ) -> List[CurrencyHedgeModel]:
        """
        Couverture automatique du portefeuille
        """
        # Récupération du portefeuille
        portfolio = await self._get_currency_portfolio(user_id)
        
        if not portfolio:
            return []
        
        created_hedges = []
        
        # Analyse des expositions non couvertes
        for currency, exposure in portfolio.currency_exposures.items():
            current_hedge_ratio = portfolio.hedge_ratios.get(currency, 0)
            
            if current_hedge_ratio < target_hedge_ratio:
                # Création d'une couverture supplémentaire
                additional_hedge_amount = (
                    Decimal(str(exposure)) * 
                    (target_hedge_ratio - Decimal(str(current_hedge_ratio)))
                )
                
                if additional_hedge_amount > Decimal('100'):  # Seuil minimum
                    hedge = await self.create_hedge(
                        user_id=user_id,
                        base_currency=portfolio.base_currency,
                        target_currency=currency,
                        notional_amount=additional_hedge_amount,
                        hedging_strategy=HedgingStrategy.AI_OPTIMIZED
                    )
                    created_hedges.append(hedge)
        
        return created_hedges


class CurrencyManager:
    """
    Gestionnaire principal multi-devises
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.cache_manager = CacheManager()
        self.converter = CurrencyConversionEngine(
            db_manager.get_session(), 
            self.cache_manager
        )
        self.hedger = CurrencyHedgingEngine(db_manager.get_session())
    
    async def process_multi_currency_revenue(
        self,
        revenue_record_id: uuid.UUID,
        user_id: uuid.UUID,
        target_currency: str = "EUR"
    ) -> Dict[str, Any]:
        """
        Traite automatiquement les revenus multi-devises
        """
        # Récupération de l'enregistrement de revenus
        revenue_record = await self._get_revenue_record(revenue_record_id)
        
        results = {
            'original_amount': float(revenue_record.amount_net),
            'original_currency': revenue_record.currency,
            'target_currency': target_currency,
            'conversions': [],
            'hedges': [],
            'total_converted': 0.0
        }
        
        # Conversion si nécessaire
        if revenue_record.currency != target_currency:
            conversion = await self.converter.convert_currency(
                amount=revenue_record.amount_net,
                from_currency=revenue_record.currency,
                to_currency=target_currency,
                user_id=user_id,
                optimize=True
            )
            results['conversions'].append({
                'conversion_id': conversion.conversion_id,
                'converted_amount': float(conversion.converted_amount),
                'exchange_rate': float(conversion.exchange_rate_used),
                'fee': float(conversion.conversion_fee),
                'savings': float(conversion.savings_achieved)
            })
            results['total_converted'] = float(conversion.converted_amount)
        else:
            results['total_converted'] = float(revenue_record.amount_net)
        
        # Évaluation du besoin de couverture
        hedge_recommendation = await self._evaluate_hedge_need(
            user_id, revenue_record.currency, revenue_record.amount_net
        )
        
        if hedge_recommendation['recommended']:
            hedge = await self.hedger.create_hedge(
                user_id=user_id,
                base_currency=target_currency,
                target_currency=revenue_record.currency,
                notional_amount=revenue_record.amount_net,
                hedging_strategy=HedgingStrategy.AI_OPTIMIZED
            )
            results['hedges'].append({
                'hedge_id': hedge.hedge_id,
                'notional_amount': float(hedge.notional_amount),
                'hedge_ratio': float(hedge.hedge_ratio)
            })
        
        return results
    
    async def setup_user_currency_profile(
        self,
        user_id: uuid.UUID,
        base_currency: str,
        target_currencies: List[str],
        risk_tolerance: str = "medium",
        auto_hedging: bool = False
    ) -> CurrencyPortfolioModel:
        """
        Configure le profil multi-devises d'un utilisateur
        """
        portfolio = CurrencyPortfolioModel(
            portfolio_id=f"PORTFOLIO_{user_id.hex[:8]}",
            user_id=user_id,
            base_currency=base_currency,
            target_currencies=target_currencies,
            currency_exposures={currency: 0.0 for currency in target_currencies},
            hedge_ratios={currency: 0.0 for currency in target_currencies},
            risk_tolerance=risk_tolerance,
            auto_hedging_enabled=auto_hedging,
            rebalancing_frequency="monthly" if auto_hedging else "manual"
        )
        
        async with self.db_manager.get_session() as session:
            session.add(portfolio)
            await session.commit()
        
        return portfolio
    
    async def generate_currency_report(
        self,
        user_id: uuid.UUID,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Génère un rapport complet des devises
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Récupération des données
        conversions = await self._get_user_conversions(user_id, start_date, end_date)
        hedges = await self._get_user_hedges(user_id)
        portfolio = await self._get_currency_portfolio(user_id)
        
        # Calcul des métriques
        total_converted = sum(c.converted_amount for c in conversions)
        total_fees = sum(c.conversion_fee for c in conversions)
        total_savings = sum(c.savings_achieved for c in conversions)
        
        return {
            'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'summary': {
                'total_conversions': len(conversions),
                'total_converted_amount': float(total_converted),
                'total_fees_paid': float(total_fees),
                'total_savings_achieved': float(total_savings),
                'active_hedges': len([h for h in hedges if h.hedge_status == 'active'])
            },
            'portfolio': {
                'base_currency': portfolio.base_currency if portfolio else None,
                'total_exposure': float(portfolio.total_exposure) if portfolio else 0,
                'hedge_ratio': portfolio.hedge_ratios if portfolio else {},
                'var_95': float(portfolio.var_95) if portfolio and portfolio.var_95 else None
            },
            'recommendations': await self._generate_currency_recommendations(user_id)
        }
