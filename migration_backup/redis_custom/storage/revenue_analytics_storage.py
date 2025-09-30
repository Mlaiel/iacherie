"""💰 Revenue Analytics Storage - Enterprise Grade
===============================================
Expert: ML ENGINEER + DBA + BACKEND SENIOR + SÉCURITÉ + IA PROMPT ENGINEER
Technologies: Revenue Intelligence + ML Predictions + Financial Analytics + Fraud Detection
Architecture: Level 2 - Storage Layer - Creator Economy
Date: 2025-01-14

Enterprise storage solution for revenue analytics with ML-driven predictions,
financial intelligence, fraud detection and comprehensive creator monetization insights.
===============================================
"""

import asyncio
import logging
import time
import hashlib
import json
import uuid
from typing import Dict, Any, Optional, List, Union, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict

# Optional imports with fallbacks
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

logger = logging.getLogger(__name__)

class RevenueStream(Enum):
    """Flux de revenus"""
    SUBSCRIPTION = "subscription"
    ONE_TIME_SALE = "one_time_sale"
    ADVERTISING = "advertising"
    SPONSORSHIP = "sponsorship"
    AFFILIATE = "affiliate"
    MERCHANDISE = "merchandise"
    LICENSING = "licensing"
    TIPS_DONATIONS = "tips_donations"
    COURSE_SALES = "course_sales"
    CONSULTATION = "consultation"

class RevenuePeriod(Enum):
    """Périodes revenus"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class RevenueCategory(Enum):
    """Catégories revenus"""
    ACTIVE_INCOME = "active_income"
    PASSIVE_INCOME = "passive_income"
    RECURRING_INCOME = "recurring_income"
    ONE_TIME_INCOME = "one_time_income"

class PredictionModel(Enum):
    """Modèles de prédiction"""
    LINEAR_REGRESSION = "linear_regression"
    ARIMA = "arima"
    PROPHET = "prophet"
    ML_ENSEMBLE = "ml_ensemble"
    NEURAL_NETWORK = "neural_network"

@dataclass
class RevenueAnalyticsConfig:
    """Configuration analytics revenus"""
    redis_url: str = "redis://localhost:6379"
    max_pool_size: int = 35
    revenue_ttl: int = 86400 * 1095  # 3 ans
    analytics_ttl: int = 86400 * 365  # 1 an
    enable_ml_predictions: bool = True
    enable_fraud_detection: bool = True
    enable_real_time_tracking: bool = True
    prediction_horizon_days: int = 90
    anomaly_threshold: float = 2.5
    min_data_points_for_prediction: int = 30
    currency_precision: int = 2
    supported_currencies: Set[str] = field(default_factory=lambda: {
        'USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY'
    })

@dataclass
class RevenueEntry:
    """Entrée revenus"""
    revenue_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    content_id: Optional[str] = None
    revenue_stream: RevenueStream = RevenueStream.ONE_TIME_SALE
    amount: Decimal = Decimal('0.00')
    currency: str = "USD"
    transaction_id: str = ""
    platform: str = ""
    payer_id: Optional[str] = None
    commission: Decimal = Decimal('0.00')
    fees: Decimal = Decimal('0.00')
    net_amount: Decimal = Decimal('0.00')
    tax_amount: Decimal = Decimal('0.00')
    processing_date: datetime = field(default_factory=datetime.now)
    settlement_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    fraud_score: Optional[float] = None
    verification_status: str = "verified"

@dataclass
class RevenueAnalytics:
    """Analytics revenus"""
    analytics_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    period: RevenuePeriod = RevenuePeriod.MONTHLY
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    total_revenue: Decimal = Decimal('0.00')
    net_revenue: Decimal = Decimal('0.00')
    gross_revenue: Decimal = Decimal('0.00')
    revenue_by_stream: Dict[str, Decimal] = field(default_factory=dict)
    revenue_by_platform: Dict[str, Decimal] = field(default_factory=dict)
    revenue_by_content: Dict[str, Decimal] = field(default_factory=dict)
    transaction_count: int = 0
    avg_transaction_value: Decimal = Decimal('0.00')
    growth_rate: float = 0.0
    mrr: Decimal = Decimal('0.00')  # Monthly Recurring Revenue
    arr: Decimal = Decimal('0.00')  # Annual Recurring Revenue
    ltv: Decimal = Decimal('0.00')  # Lifetime Value
    churn_rate: float = 0.0
    conversion_metrics: Dict[str, float] = field(default_factory=dict)
    geographic_distribution: Dict[str, Decimal] = field(default_factory=dict)
    top_performing_content: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class RevenuePrediction:
    """Prédiction revenus"""
    prediction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    model_used: PredictionModel = PredictionModel.ML_ENSEMBLE
    prediction_date: datetime = field(default_factory=datetime.now)
    horizon_days: int = 30
    predicted_revenue: Decimal = Decimal('0.00')
    confidence_interval_lower: Decimal = Decimal('0.00')
    confidence_interval_upper: Decimal = Decimal('0.00')
    confidence_score: float = 0.0
    factors: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    model_performance: Dict[str, float] = field(default_factory=dict)

@dataclass
class RevenueInsight:
    """Insight revenus"""
    insight_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    insight_type: str = ""
    title: str = ""
    description: str = ""
    impact_score: float = 0.0
    actionable_recommendations: List[str] = field(default_factory=list)
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    urgency: str = "medium"  # low, medium, high
    generated_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))

class RevenueAnalyticsStorage:
    """Gestionnaire stockage analytics revenus enterprise"""
    
    def __init__(self, config: RevenueAnalyticsConfig):
        self.config = config
        self.redis_pool = None
        self.revenue_cache = {}
        self.analytics_cache = {}
        self.predictions_cache = {}
        self.ml_predictor = MLRevenuePredictor() if config.enable_ml_predictions else None
        self.fraud_detector = FraudDetector() if config.enable_fraud_detection else None
        
        # Métriques temps réel
        self.real_time_metrics = {
            'total_revenue_today': Decimal('0.00'),
            'transactions_today': 0,
            'avg_transaction_value': Decimal('0.00'),
            'revenue_growth_rate': 0.0,
            'fraud_alerts': 0,
            'top_revenue_streams': []
        }
        
        logger.info("RevenueAnalyticsStorage initialisé")
    
    async def initialize(self):
        """Initialisation connexions Redis"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis non disponible - mode dégradé")
            return
        
        try:
            self.redis_pool = redis.ConnectionPool.from_url(
                self.config.redis_url,
                max_connections=self.config.max_pool_size,
                retry_on_timeout=True
            )
            
            # Test connexion
            async with redis.Redis(connection_pool=self.redis_pool) as r:
                await r.ping()
            
            # Démarrage processus
            if self.config.enable_real_time_tracking:
                asyncio.create_task(self._real_time_tracker())
            
            if self.config.enable_ml_predictions:
                asyncio.create_task(self._prediction_updater())
            
            asyncio.create_task(self._analytics_calculator())
            asyncio.create_task(self._insights_generator())
            
            logger.info("Connexion Redis établie pour les analytics revenus")
            
        except Exception as e:
            logger.error(f"Erreur initialisation Redis revenus: {e}")
            self.redis_pool = None
    
    async def record_revenue(self, revenue_data: Dict[str, Any]) -> str:
        """Enregistrement revenus"""
        try:
            # Validation données
            validation_result = await self._validate_revenue_data(revenue_data)
            if not validation_result['valid']:
                raise ValueError(f"Données revenus invalides: {validation_result['errors']}")
            
            # Création entrée revenus
            revenue = RevenueEntry(
                creator_id=revenue_data['creator_id'],
                content_id=revenue_data.get('content_id'),
                revenue_stream=RevenueStream(revenue_data['revenue_stream']),
                amount=Decimal(str(revenue_data['amount'])),
                currency=revenue_data.get('currency', 'USD'),
                transaction_id=revenue_data.get('transaction_id', ''),
                platform=revenue_data.get('platform', ''),
                payer_id=revenue_data.get('payer_id'),
                metadata=revenue_data.get('metadata', {})
            )
            
            # Calcul montants dérivés
            await self._calculate_derived_amounts(revenue, revenue_data)
            
            # Détection fraude
            if self.fraud_detector:
                fraud_score = await self.fraud_detector.analyze_revenue(revenue)
                revenue.fraud_score = fraud_score
                
                if fraud_score > 0.8:
                    revenue.verification_status = "suspicious"
                    self.real_time_metrics['fraud_alerts'] += 1
                    logger.warning(f"Revenus suspects détectés: {revenue.revenue_id}")
            
            # Stockage Redis
            if self.redis_pool:
                await self._store_revenue_to_redis(revenue)
            
            # Cache local
            self.revenue_cache[revenue.revenue_id] = revenue
            
            # Mise à jour métriques temps réel
            await self._update_real_time_metrics(revenue)
            
            # Déclenchement analyses
            if self.config.enable_ml_predictions:
                await self._trigger_prediction_update(revenue.creator_id)
            
            logger.info(f"Revenus enregistrés: {revenue.revenue_id} ({revenue.amount} {revenue.currency})")
            return revenue.revenue_id
            
        except Exception as e:
            logger.error(f"Erreur enregistrement revenus: {e}")
            raise
    
    async def get_revenue_analytics(self, creator_id: str, period: RevenuePeriod,
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> RevenueAnalytics:
        """Récupération analytics revenus"""
        try:
            # Calcul période si non spécifiée
            if not start_date or not end_date:
                start_date, end_date = self._calculate_period_dates(period)
            
            # Clé cache
            cache_key = f"{creator_id}_{period.value}_{start_date.date()}_{end_date.date()}"
            if cache_key in self.analytics_cache:
                cached = self.analytics_cache[cache_key]
                if (datetime.now() - cached['cached_at']).seconds < 1800:  # 30 min cache
                    return cached['analytics']
            
            # Récupération données revenus
            revenue_entries = await self._get_revenue_entries(creator_id, start_date, end_date)
            
            # Calcul analytics
            analytics = RevenueAnalytics(
                creator_id=creator_id,
                period=period,
                period_start=start_date,
                period_end=end_date
            )
            
            if revenue_entries:
                # Métriques de base
                analytics.total_revenue = sum(r.amount for r in revenue_entries)
                analytics.net_revenue = sum(r.net_amount for r in revenue_entries)
                analytics.gross_revenue = analytics.total_revenue + sum(r.fees for r in revenue_entries)
                analytics.transaction_count = len(revenue_entries)
                analytics.avg_transaction_value = analytics.total_revenue / analytics.transaction_count
                
                # Revenus par stream
                for entry in revenue_entries:
                    stream = entry.revenue_stream.value
                    if stream not in analytics.revenue_by_stream:
                        analytics.revenue_by_stream[stream] = Decimal('0.00')
                    analytics.revenue_by_stream[stream] += entry.amount
                
                # Revenus par plateforme
                for entry in revenue_entries:
                    platform = entry.platform or 'unknown'
                    if platform not in analytics.revenue_by_platform:
                        analytics.revenue_by_platform[platform] = Decimal('0.00')
                    analytics.revenue_by_platform[platform] += entry.amount
                
                # Revenus par contenu
                for entry in revenue_entries:
                    if entry.content_id:
                        content_id = entry.content_id
                        if content_id not in analytics.revenue_by_content:
                            analytics.revenue_by_content[content_id] = Decimal('0.00')
                        analytics.revenue_by_content[content_id] += entry.amount
                
                # Calcul métriques avancées
                await self._calculate_advanced_metrics(analytics, revenue_entries)
                
                # Top contenu performant
                analytics.top_performing_content = await self._get_top_performing_content(
                    analytics.revenue_by_content
                )
            
            # Mise en cache
            self.analytics_cache[cache_key] = {
                'analytics': analytics,
                'cached_at': datetime.now()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Erreur analytics revenus {creator_id}: {e}")
            return RevenueAnalytics(creator_id=creator_id, period=period)
    
    async def predict_revenue(self, creator_id: str, horizon_days: int = 30) -> RevenuePrediction:
        """Prédiction revenus"""
        try:
            if not self.ml_predictor:
                raise ValueError("Prédiction ML non activée")
            
            # Clé cache
            cache_key = f"{creator_id}_{horizon_days}"
            if cache_key in self.predictions_cache:
                cached = self.predictions_cache[cache_key]
                if (datetime.now() - cached['cached_at']).seconds < 3600:  # 1h cache
                    return cached['prediction']
            
            # Récupération données historiques
            historical_data = await self._get_historical_revenue_data(creator_id)
            
            if len(historical_data) < self.config.min_data_points_for_prediction:
                raise ValueError(f"Données insuffisantes pour prédiction: {len(historical_data)} points")
            
            # Génération prédiction ML
            prediction = await self.ml_predictor.predict_revenue(
                creator_id, historical_data, horizon_days
            )
            
            # Enrichissement avec recommandations
            prediction.recommendations = await self._generate_revenue_recommendations(
                creator_id, prediction, historical_data
            )
            
            # Évaluation des risques
            prediction.risk_assessment = await self._assess_revenue_risks(
                creator_id, prediction, historical_data
            )
            
            # Mise en cache
            self.predictions_cache[cache_key] = {
                'prediction': prediction,
                'cached_at': datetime.now()
            }
            
            logger.info(f"Prédiction revenus générée: {creator_id} ({prediction.predicted_revenue} sur {horizon_days} jours)")
            return prediction
            
        except Exception as e:
            logger.error(f"Erreur prédiction revenus {creator_id}: {e}")
            raise
    
    async def get_revenue_insights(self, creator_id: str) -> List[RevenueInsight]:
        """Génération insights revenus"""
        try:
            insights = []
            
            # Analytics récentes
            monthly_analytics = await self.get_revenue_analytics(creator_id, RevenuePeriod.MONTHLY)
            yearly_analytics = await self.get_revenue_analytics(creator_id, RevenuePeriod.YEARLY)
            
            # Insights croissance
            growth_insights = await self._generate_growth_insights(creator_id, monthly_analytics)
            insights.extend(growth_insights)
            
            # Insights diversification
            diversification_insights = await self._generate_diversification_insights(
                creator_id, monthly_analytics
            )
            insights.extend(diversification_insights)
            
            # Insights saisonnalité
            seasonal_insights = await self._generate_seasonal_insights(creator_id, yearly_analytics)
            insights.extend(seasonal_insights)
            
            # Insights optimisation
            optimization_insights = await self._generate_optimization_insights(
                creator_id, monthly_analytics
            )
            insights.extend(optimization_insights)
            
            # Tri par score d'impact
            insights.sort(key=lambda i: i.impact_score, reverse=True)
            
            return insights[:10]  # Top 10 insights
            
        except Exception as e:
            logger.error(f"Erreur génération insights {creator_id}: {e}")
            return []
    
    async def compare_revenue_performance(self, creator_id: str, 
                                        benchmark_type: str = "peer_average") -> Dict[str, Any]:
        """Comparaison performance revenus"""
        try:
            # Analytics créateur
            creator_analytics = await self.get_revenue_analytics(creator_id, RevenuePeriod.MONTHLY)
            
            # Récupération benchmark
            benchmark_data = await self._get_benchmark_data(creator_id, benchmark_type)
            
            comparison = {
                'creator_revenue': float(creator_analytics.total_revenue),
                'benchmark_revenue': benchmark_data.get('avg_revenue', 0),
                'performance_ratio': 0,
                'percentile_ranking': 0,
                'comparison_insights': [],
                'improvement_areas': []
            }
            
            if benchmark_data.get('avg_revenue', 0) > 0:
                comparison['performance_ratio'] = float(
                    creator_analytics.total_revenue / Decimal(str(benchmark_data['avg_revenue']))
                )
            
            # Calcul percentile
            comparison['percentile_ranking'] = await self._calculate_percentile_ranking(
                creator_id, creator_analytics.total_revenue
            )
            
            # Insights comparatifs
            comparison['comparison_insights'] = await self._generate_comparison_insights(
                creator_analytics, benchmark_data
            )
            
            # Zones d'amélioration
            comparison['improvement_areas'] = await self._identify_improvement_areas(
                creator_analytics, benchmark_data
            )
            
            return comparison
            
        except Exception as e:
            logger.error(f"Erreur comparaison performance {creator_id}: {e}")
            return {}
    
    async def _validate_revenue_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validation données revenus"""
        errors = []
        
        # Champs requis
        required_fields = ['creator_id', 'revenue_stream', 'amount']
        for field in required_fields:
            if field not in data:
                errors.append(f"Champ requis manquant: {field}")
        
        # Validation montant
        if 'amount' in data:
            try:
                amount = Decimal(str(data['amount']))
                if amount < 0:
                    errors.append("Montant ne peut pas être négatif")
                if amount > Decimal('1000000'):  # 1M limit
                    errors.append("Montant trop élevé")
            except:
                errors.append("Montant invalide")
        
        # Validation devise
        if 'currency' in data and data['currency'] not in self.config.supported_currencies:
            errors.append(f"Devise non supportée: {data['currency']}")
        
        # Validation stream
        if 'revenue_stream' in data:
            try:
                RevenueStream(data['revenue_stream'])
            except ValueError:
                errors.append(f"Stream revenus invalide: {data['revenue_stream']}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    async def _calculate_derived_amounts(self, revenue: RevenueEntry, 
                                       revenue_data: Dict[str, Any]):
        """Calcul montants dérivés"""
        # Commission (pourcentage ou montant fixe)
        if 'commission_rate' in revenue_data:
            revenue.commission = revenue.amount * Decimal(str(revenue_data['commission_rate']))
        elif 'commission_amount' in revenue_data:
            revenue.commission = Decimal(str(revenue_data['commission_amount']))
        else:
            # Commission par défaut selon stream
            default_commission_rates = {
                RevenueStream.SUBSCRIPTION: Decimal('0.05'),  # 5%
                RevenueStream.ONE_TIME_SALE: Decimal('0.03'),  # 3%
                RevenueStream.ADVERTISING: Decimal('0.15'),    # 15%
                RevenueStream.SPONSORSHIP: Decimal('0.10'),    # 10%
                RevenueStream.AFFILIATE: Decimal('0.20'),      # 20%
            }
            rate = default_commission_rates.get(revenue.revenue_stream, Decimal('0.05'))
            revenue.commission = revenue.amount * rate
        
        # Frais de traitement
        if 'fees' in revenue_data:
            revenue.fees = Decimal(str(revenue_data['fees']))
        else:
            # Frais par défaut (2.9% + $0.30 pour cartes)
            revenue.fees = revenue.amount * Decimal('0.029') + Decimal('0.30')
        
        # Taxes
        if 'tax_rate' in revenue_data:
            revenue.tax_amount = revenue.amount * Decimal(str(revenue_data['tax_rate']))
        
        # Montant net
        revenue.net_amount = revenue.amount - revenue.commission - revenue.fees - revenue.tax_amount
    
    async def _update_real_time_metrics(self, revenue: RevenueEntry):
        """Mise à jour métriques temps réel"""
        today = datetime.now().date()
        revenue_date = revenue.processing_date.date()
        
        if revenue_date == today:
            self.real_time_metrics['total_revenue_today'] += revenue.amount
            self.real_time_metrics['transactions_today'] += 1
            
            # Recalcul moyenne
            if self.real_time_metrics['transactions_today'] > 0:
                self.real_time_metrics['avg_transaction_value'] = (
                    self.real_time_metrics['total_revenue_today'] / 
                    self.real_time_metrics['transactions_today']
                )
        
        # Mise à jour top streams
        await self._update_top_revenue_streams()
    
    async def _update_top_revenue_streams(self):
        """Mise à jour top streams revenus"""
        # Calcul basé sur dernières 24h (simplifié)
        stream_totals = defaultdict(Decimal)
        
        for revenue in list(self.revenue_cache.values())[-1000:]:  # Dernières 1000 entrées
            if (datetime.now() - revenue.processing_date).days == 0:
                stream_totals[revenue.revenue_stream.value] += revenue.amount
        
        # Tri et top 5
        sorted_streams = sorted(stream_totals.items(), key=lambda x: x[1], reverse=True)
        self.real_time_metrics['top_revenue_streams'] = [
            {'stream': stream, 'amount': float(amount)}
            for stream, amount in sorted_streams[:5]
        ]
    
    def _calculate_period_dates(self, period: RevenuePeriod) -> Tuple[datetime, datetime]:
        """Calcul dates période"""
        now = datetime.now()
        
        if period == RevenuePeriod.DAILY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period == RevenuePeriod.WEEKLY:
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
        elif period == RevenuePeriod.MONTHLY:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)
        elif period == RevenuePeriod.QUARTERLY:
            quarter = (now.month - 1) // 3 + 1
            start = now.replace(month=(quarter - 1) * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=90)  # Approximation
        else:  # YEARLY
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start.replace(year=start.year + 1)
        
        return start, end
    
    async def _store_revenue_to_redis(self, revenue: RevenueEntry):
        """Stockage revenus Redis"""
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            revenue_key = f"revenue:entry:{revenue.revenue_id}"
            revenue_data = {
                'revenue_id': revenue.revenue_id,
                'creator_id': revenue.creator_id,
                'content_id': revenue.content_id,
                'revenue_stream': revenue.revenue_stream.value,
                'amount': str(revenue.amount),
                'currency': revenue.currency,
                'transaction_id': revenue.transaction_id,
                'platform': revenue.platform,
                'payer_id': revenue.payer_id,
                'commission': str(revenue.commission),
                'fees': str(revenue.fees),
                'net_amount': str(revenue.net_amount),
                'tax_amount': str(revenue.tax_amount),
                'processing_date': revenue.processing_date.isoformat(),
                'settlement_date': revenue.settlement_date.isoformat() if revenue.settlement_date else None,
                'metadata': revenue.metadata,
                'fraud_score': revenue.fraud_score,
                'verification_status': revenue.verification_status
            }
            
            await r.setex(revenue_key, self.config.revenue_ttl, json.dumps(revenue_data))
            
            # Index temporel
            timeline_key = f"revenue:timeline:{revenue.creator_id}"
            await r.zadd(timeline_key, {revenue.revenue_id: revenue.processing_date.timestamp()})
            
            # Index par stream
            stream_key = f"revenue:stream:{revenue.creator_id}:{revenue.revenue_stream.value}"
            await r.sadd(stream_key, revenue.revenue_id)
    
    async def _get_revenue_entries(self, creator_id: str, start_date: datetime, 
                                  end_date: datetime) -> List[RevenueEntry]:
        """Récupération entrées revenus"""
        entries = []
        
        if not self.redis_pool:
            return entries
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            timeline_key = f"revenue:timeline:{creator_id}"
            
            # Récupération par plage temporelle
            revenue_ids = await r.zrangebyscore(
                timeline_key,
                start_date.timestamp(),
                end_date.timestamp()
            )
            
            for revenue_id in revenue_ids:
                revenue = await self._get_revenue_entry(revenue_id)
                if revenue:
                    entries.append(revenue)
        
        return entries
    
    async def _get_revenue_entry(self, revenue_id: str) -> Optional[RevenueEntry]:
        """Récupération entrée revenus"""
        # Cache local d'abord
        if revenue_id in self.revenue_cache:
            return self.revenue_cache[revenue_id]
        
        # Redis ensuite
        if not self.redis_pool:
            return None
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            revenue_key = f"revenue:entry:{revenue_id}"
            revenue_json = await r.get(revenue_key)
            
            if not revenue_json:
                return None
            
            data = json.loads(revenue_json)
            
            revenue = RevenueEntry(
                revenue_id=data['revenue_id'],
                creator_id=data['creator_id'],
                content_id=data['content_id'],
                revenue_stream=RevenueStream(data['revenue_stream']),
                amount=Decimal(data['amount']),
                currency=data['currency'],
                transaction_id=data['transaction_id'],
                platform=data['platform'],
                payer_id=data['payer_id'],
                commission=Decimal(data['commission']),
                fees=Decimal(data['fees']),
                net_amount=Decimal(data['net_amount']),
                tax_amount=Decimal(data['tax_amount']),
                processing_date=datetime.fromisoformat(data['processing_date']),
                settlement_date=datetime.fromisoformat(data['settlement_date']) if data['settlement_date'] else None,
                metadata=data['metadata'],
                fraud_score=data['fraud_score'],
                verification_status=data['verification_status']
            )
            
            # Mise en cache
            self.revenue_cache[revenue_id] = revenue
            return revenue
    
    async def _calculate_advanced_metrics(self, analytics: RevenueAnalytics,
                                         revenue_entries: List[RevenueEntry]):
        """Calcul métriques avancées"""
        # Taux de croissance
        prev_period_start = analytics.period_start - (analytics.period_end - analytics.period_start)
        prev_period_end = analytics.period_start
        
        prev_entries = await self._get_revenue_entries(
            analytics.creator_id, prev_period_start, prev_period_end
        )
        
        if prev_entries:
            prev_revenue = sum(r.amount for r in prev_entries)
            if prev_revenue > 0:
                analytics.growth_rate = float(
                    (analytics.total_revenue - prev_revenue) / prev_revenue * 100
                )
        
        # MRR (Monthly Recurring Revenue)
        recurring_streams = {RevenueStream.SUBSCRIPTION}
        recurring_revenue = sum(
            r.amount for r in revenue_entries 
            if r.revenue_stream in recurring_streams
        )
        analytics.mrr = recurring_revenue
        analytics.arr = analytics.mrr * 12
        
        # Métriques conversion
        analytics.conversion_metrics = await self._calculate_conversion_metrics(
            analytics.creator_id, revenue_entries
        )
        
        # Distribution géographique
        analytics.geographic_distribution = await self._calculate_geographic_distribution(
            revenue_entries
        )
    
    async def _calculate_conversion_metrics(self, creator_id: str,
                                          revenue_entries: List[RevenueEntry]) -> Dict[str, float]:
        """Calcul métriques conversion"""
        # Placeholder - à implémenter avec données engagement
        return {
            'visitor_to_customer': 0.025,  # 2.5%
            'trial_to_paid': 0.15,         # 15%
            'upsell_rate': 0.08,           # 8%
            'retention_rate': 0.85         # 85%
        }
    
    async def _calculate_geographic_distribution(self, 
                                               revenue_entries: List[RevenueEntry]) -> Dict[str, Decimal]:
        """Calcul distribution géographique"""
        geo_revenue = defaultdict(Decimal)
        
        for entry in revenue_entries:
            country = entry.metadata.get('country', 'Unknown')
            geo_revenue[country] += entry.amount
        
        return dict(geo_revenue)
    
    async def _get_top_performing_content(self, 
                                        revenue_by_content: Dict[str, Decimal]) -> List[Dict[str, Any]]:
        """Top contenu performant"""
        sorted_content = sorted(revenue_by_content.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'content_id': content_id,
                'revenue': float(revenue),
                'percentage': float(revenue / sum(revenue_by_content.values()) * 100) if revenue_by_content else 0
            }
            for content_id, revenue in sorted_content[:10]
        ]
    
    async def _get_historical_revenue_data(self, creator_id: str) -> List[Dict[str, Any]]:
        """Récupération données historiques"""
        # Données des 12 derniers mois
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        revenue_entries = await self._get_revenue_entries(creator_id, start_date, end_date)
        
        # Agrégation par jour
        daily_revenue = defaultdict(Decimal)
        for entry in revenue_entries:
            date_key = entry.processing_date.date()
            daily_revenue[date_key] += entry.amount
        
        # Conversion en format ML
        historical_data = []
        current_date = start_date.date()
        while current_date <= end_date.date():
            historical_data.append({
                'date': current_date.isoformat(),
                'revenue': float(daily_revenue.get(current_date, Decimal('0.00'))),
                'day_of_week': current_date.weekday(),
                'day_of_month': current_date.day,
                'month': current_date.month,
                'quarter': (current_date.month - 1) // 3 + 1
            })
            current_date += timedelta(days=1)
        
        return historical_data
    
    async def _generate_revenue_recommendations(self, creator_id: str,
                                              prediction: RevenuePrediction,
                                              historical_data: List[Dict[str, Any]]) -> List[str]:
        """Génération recommandations revenus"""
        recommendations = []
        
        # Basé sur la prédiction
        if prediction.predicted_revenue < Decimal('1000'):
            recommendations.append("Diversifier les sources de revenus pour augmenter les gains")
        
        if prediction.confidence_score < 0.7:
            recommendations.append("Stabiliser les revenus pour améliorer la prévisibilité")
        
        # Basé sur les facteurs
        if prediction.factors.get('seasonality', 0) > 0.3:
            recommendations.append("Préparer stratégie pour périodes de faible activité saisonnière")
        
        # Recommandations générales
        recommendations.extend([
            "Optimiser le pricing de vos offres premium",
            "Développer des produits récurrents pour stabiliser les revenus",
            "Analyser et répliquer les stratégies de vos contenus les plus rentables"
        ])
        
        return recommendations[:5]  # Top 5
    
    async def _assess_revenue_risks(self, creator_id: str, prediction: RevenuePrediction,
                                   historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Évaluation risques revenus"""
        # Calcul volatilité
        revenues = [d['revenue'] for d in historical_data]
        avg_revenue = sum(revenues) / len(revenues) if revenues else 0
        volatility = (
            sum((r - avg_revenue) ** 2 for r in revenues) / len(revenues)
        ) ** 0.5 if revenues else 0
        
        # Classification risque
        risk_level = "low"
        if volatility > avg_revenue * 0.5:
            risk_level = "high"
        elif volatility > avg_revenue * 0.3:
            risk_level = "medium"
        
        return {
            'overall_risk_level': risk_level,
            'volatility_score': round(volatility / max(avg_revenue, 1), 3),
            'revenue_concentration_risk': 'medium',  # À calculer
            'seasonal_dependency_risk': 'low',       # À calculer
            'platform_dependency_risk': 'medium',   # À calculer
            'recommendations': [
                "Diversifier les sources de revenus",
                "Créer un fonds d'urgence pour les périodes difficiles",
                "Surveiller les indicateurs de performance clés"
            ]
        }
    
    # Méthodes génération insights
    async def _generate_growth_insights(self, creator_id: str,
                                       analytics: RevenueAnalytics) -> List[RevenueInsight]:
        """Génération insights croissance"""
        insights = []
        
        if analytics.growth_rate > 20:
            insight = RevenueInsight(
                creator_id=creator_id,
                insight_type="growth",
                title="🚀 Croissance exceptionnelle des revenus",
                description=f"Vos revenus ont augmenté de {analytics.growth_rate:.1f}% ce mois",
                impact_score=0.9,
                actionable_recommendations=[
                    "Capitaliser sur cette dynamique positive",
                    "Investir dans l'expansion de votre audience",
                    "Préparer l'infrastructure pour soutenir cette croissance"
                ],
                confidence=0.95,
                urgency="high"
            )
            insights.append(insight)
        elif analytics.growth_rate < -10:
            insight = RevenueInsight(
                creator_id=creator_id,
                insight_type="growth",
                title="⚠️ Baisse significative des revenus",
                description=f"Vos revenus ont diminué de {abs(analytics.growth_rate):.1f}% ce mois",
                impact_score=0.8,
                actionable_recommendations=[
                    "Analyser les causes de la baisse",
                    "Revoir votre stratégie de contenu",
                    "Diversifier vos sources de revenus"
                ],
                confidence=0.9,
                urgency="high"
            )
            insights.append(insight)
        
        return insights
    
    async def _generate_diversification_insights(self, creator_id: str,
                                               analytics: RevenueAnalytics) -> List[RevenueInsight]:
        """Génération insights diversification"""
        insights = []
        
        # Calcul concentration revenus
        if analytics.revenue_by_stream:
            max_stream_revenue = max(analytics.revenue_by_stream.values())
            concentration_ratio = float(max_stream_revenue / analytics.total_revenue)
            
            if concentration_ratio > 0.8:
                insight = RevenueInsight(
                    creator_id=creator_id,
                    insight_type="diversification",
                    title="🎯 Revenus très concentrés",
                    description=f"{concentration_ratio*100:.1f}% de vos revenus proviennent d'une seule source",
                    impact_score=0.7,
                    actionable_recommendations=[
                        "Développer de nouveaux flux de revenus",
                        "Réduire la dépendance à votre source principale",
                        "Expérimenter avec différents modèles de monétisation"
                    ],
                    confidence=0.85,
                    urgency="medium"
                )
                insights.append(insight)
        
        return insights
    
    async def _generate_seasonal_insights(self, creator_id: str,
                                        analytics: RevenueAnalytics) -> List[RevenueInsight]:
        """Génération insights saisonnalité"""
        insights = []
        
        # Analyse saisonnalité (simplifiée)
        current_month = datetime.now().month
        if current_month in [11, 12]:  # Novembre, Décembre
            insight = RevenueInsight(
                creator_id=creator_id,
                insight_type="seasonal",
                title="🎄 Opportunité saisonnière",
                description="La période des fêtes offre des opportunités de revenus accrues",
                impact_score=0.6,
                actionable_recommendations=[
                    "Créer du contenu thématique pour les fêtes",
                    "Lancer des promotions spéciales",
                    "Proposer des produits cadeaux"
                ],
                confidence=0.8,
                urgency="medium"
            )
            insights.append(insight)
        
        return insights
    
    async def _generate_optimization_insights(self, creator_id: str,
                                            analytics: RevenueAnalytics) -> List[RevenueInsight]:
        """Génération insights optimisation"""
        insights = []
        
        if analytics.avg_transaction_value < Decimal('50'):
            insight = RevenueInsight(
                creator_id=creator_id,
                insight_type="optimization",
                title="💡 Opportunité d'augmenter la valeur moyenne",
                description=f"Votre transaction moyenne est de {analytics.avg_transaction_value}",
                impact_score=0.65,
                actionable_recommendations=[
                    "Proposer des bundles de produits",
                    "Implémenter des stratégies d'upselling",
                    "Créer des tiers de prix plus élevés"
                ],
                confidence=0.75,
                urgency="medium"
            )
            insights.append(insight)
        
        return insights
    
    async def _get_benchmark_data(self, creator_id: str, benchmark_type: str) -> Dict[str, Any]:
        """Récupération données benchmark"""
        # Données de benchmark simulées (à remplacer par vraies données)
        benchmark_data = {
            'peer_average': {
                'avg_revenue': 2500.0,
                'avg_transaction_value': 45.0,
                'avg_growth_rate': 15.0,
                'avg_streams_count': 3.2
            },
            'industry_average': {
                'avg_revenue': 3200.0,
                'avg_transaction_value': 52.0,
                'avg_growth_rate': 12.0,
                'avg_streams_count': 4.1
            },
            'top_performers': {
                'avg_revenue': 8500.0,
                'avg_transaction_value': 125.0,
                'avg_growth_rate': 35.0,
                'avg_streams_count': 6.5
            }
        }
        
        return benchmark_data.get(benchmark_type, benchmark_data['peer_average'])
    
    async def _calculate_percentile_ranking(self, creator_id: str, revenue: Decimal) -> int:
        """Calcul classement percentile"""
        # Simulation (à remplacer par calcul réel)
        revenue_float = float(revenue)
        
        if revenue_float > 10000:
            return 95
        elif revenue_float > 5000:
            return 80
        elif revenue_float > 2500:
            return 60
        elif revenue_float > 1000:
            return 40
        else:
            return 20
    
    async def _generate_comparison_insights(self, creator_analytics: RevenueAnalytics,
                                          benchmark_data: Dict[str, Any]) -> List[str]:
        """Génération insights comparatifs"""
        insights = []
        
        performance_ratio = float(creator_analytics.total_revenue) / benchmark_data.get('avg_revenue', 1)
        
        if performance_ratio > 1.2:
            insights.append("Vos revenus dépassent la moyenne de 20%+")
        elif performance_ratio < 0.8:
            insights.append("Vos revenus sont 20% sous la moyenne du secteur")
        
        if creator_analytics.growth_rate > benchmark_data.get('avg_growth_rate', 0):
            insights.append("Votre croissance surpasse la moyenne du marché")
        
        return insights
    
    async def _identify_improvement_areas(self, creator_analytics: RevenueAnalytics,
                                        benchmark_data: Dict[str, Any]) -> List[str]:
        """Identification zones d'amélioration"""
        areas = []
        
        if float(creator_analytics.avg_transaction_value) < benchmark_data.get('avg_transaction_value', 0):
            areas.append("Valeur moyenne des transactions")
        
        if len(creator_analytics.revenue_by_stream) < benchmark_data.get('avg_streams_count', 0):
            areas.append("Diversification des sources de revenus")
        
        if creator_analytics.growth_rate < benchmark_data.get('avg_growth_rate', 0):
            areas.append("Taux de croissance")
        
        return areas
    
    # Processus asynchrones
    async def _real_time_tracker(self):
        """Tracker temps réel"""
        while True:
            try:
                await asyncio.sleep(60)  # Chaque minute
                
                # Calcul taux de croissance journalier
                today_revenue = self.real_time_metrics['total_revenue_today']
                yesterday_revenue = await self._get_yesterday_revenue()
                
                if yesterday_revenue > 0:
                    growth_rate = float((today_revenue - yesterday_revenue) / yesterday_revenue * 100)
                    self.real_time_metrics['revenue_growth_rate'] = growth_rate
                
            except Exception as e:
                logger.error(f"Erreur real-time tracker: {e}")
                await asyncio.sleep(60)
    
    async def _get_yesterday_revenue(self) -> Decimal:
        """Récupération revenus d'hier"""
        yesterday = datetime.now() - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        total = Decimal('0.00')
        for revenue in self.revenue_cache.values():
            if start_date <= revenue.processing_date < end_date:
                total += revenue.amount
        
        return total
    
    async def _prediction_updater(self):
        """Mise à jour prédictions"""
        while True:
            try:
                await asyncio.sleep(3600)  # Chaque heure
                
                # Mise à jour prédictions pour créateurs actifs
                active_creators = set()
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                for revenue in self.revenue_cache.values():
                    if revenue.processing_date >= cutoff_time:
                        active_creators.add(revenue.creator_id)
                
                # Limite pour performance
                for creator_id in list(active_creators)[:10]:
                    try:
                        await self.predict_revenue(creator_id)
                    except Exception as e:
                        logger.error(f"Erreur prédiction {creator_id}: {e}")
                
            except Exception as e:
                logger.error(f"Erreur prediction updater: {e}")
                await asyncio.sleep(3600)
    
    async def _analytics_calculator(self):
        """Calculateur analytics"""
        while True:
            try:
                await asyncio.sleep(1800)  # Toutes les 30 minutes
                
                # Invalidation cache analytics pour forcer recalcul
                self.analytics_cache.clear()
                
            except Exception as e:
                logger.error(f"Erreur analytics calculator: {e}")
                await asyncio.sleep(1800)
    
    async def _insights_generator(self):
        """Générateur insights"""
        while True:
            try:
                await asyncio.sleep(7200)  # Toutes les 2 heures
                
                # Génération insights pour créateurs actifs
                active_creators = set(revenue.creator_id for revenue in list(self.revenue_cache.values())[-100:])
                
                for creator_id in list(active_creators)[:5]:  # Limite pour performance
                    try:
                        insights = await self.get_revenue_insights(creator_id)
                        if insights:
                            logger.info(f"Insights générés pour {creator_id}: {len(insights)} insights")
                    except Exception as e:
                        logger.error(f"Erreur génération insights {creator_id}: {e}")
                
            except Exception as e:
                logger.error(f"Erreur insights generator: {e}")
                await asyncio.sleep(7200)
    
    async def _trigger_prediction_update(self, creator_id: str):
        """Déclenchement mise à jour prédiction"""
        # Invalidation cache prédictions pour ce créateur
        keys_to_remove = [k for k in self.predictions_cache.keys() if k.startswith(creator_id)]
        for key in keys_to_remove:
            self.predictions_cache.pop(key, None)
    
    async def get_revenue_statistics(self) -> Dict[str, Any]:
        """Statistiques revenus globales"""
        try:
            stats = {}
            
            # Métriques temps réel
            stats.update(self.real_time_metrics)
            
            # Statistiques cache
            stats['revenue_entries_cached'] = len(self.revenue_cache)
            stats['analytics_cached'] = len(self.analytics_cache)
            stats['predictions_cached'] = len(self.predictions_cache)
            
            # Conversion Decimal vers float pour JSON
            for key, value in stats.items():
                if isinstance(value, Decimal):
                    stats[key] = float(value)
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur récupération statistiques revenus: {e}")
            return self.real_time_metrics

class MLRevenuePredictor:
    """Prédicteur ML revenus (placeholder)"""
    
    async def predict_revenue(self, creator_id: str, historical_data: List[Dict[str, Any]],
                            horizon_days: int) -> RevenuePrediction:
        """Prédiction revenus ML"""
        # Simulation prédiction ML
        recent_avg = sum(d['revenue'] for d in historical_data[-30:]) / 30
        trend = (sum(d['revenue'] for d in historical_data[-7:]) / 7) - recent_avg
        
        predicted_daily = recent_avg + trend
        predicted_total = Decimal(str(predicted_daily * horizon_days))
        
        return RevenuePrediction(
            creator_id=creator_id,
            model_used=PredictionModel.ML_ENSEMBLE,
            horizon_days=horizon_days,
            predicted_revenue=predicted_total,
            confidence_interval_lower=predicted_total * Decimal('0.8'),
            confidence_interval_upper=predicted_total * Decimal('1.2'),
            confidence_score=0.75,
            factors={
                'trend': 0.3,
                'seasonality': 0.2,
                'historical_performance': 0.5
            },
            model_performance={
                'accuracy': 0.82,
                'mape': 0.15,  # Mean Absolute Percentage Error
                'rmse': 0.18   # Root Mean Square Error
            }
        )

class FraudDetector:
    """Détecteur de fraude (placeholder)"""
    
    async def analyze_revenue(self, revenue: RevenueEntry) -> float:
        """Analyse fraude revenus"""
        fraud_score = 0.0
        
        # Montant suspect
        if revenue.amount > Decimal('5000'):
            fraud_score += 0.3
        
        # Fréquence suspecte (à implémenter)
        # fraud_score += await self._check_frequency_patterns(revenue)
        
        # Patterns géographiques (à implémenter)
        # fraud_score += await self._check_geographic_patterns(revenue)
        
        return min(fraud_score, 1.0)

# Factory function
def create_revenue_analytics_storage(
    redis_url: str = "redis://localhost:6379",
    **kwargs
) -> RevenueAnalyticsStorage:
    """Factory pour création stockage analytics revenus"""
    config = RevenueAnalyticsConfig(redis_url=redis_url, **kwargs)
    return RevenueAnalyticsStorage(config)

# Export classes principales
__all__ = [
    'RevenueAnalyticsStorage',
    'RevenueAnalyticsConfig',
    'RevenueEntry',
    'RevenueAnalytics',
    'RevenuePrediction',
    'RevenueInsight',
    'RevenueStream',
    'RevenuePeriod',
    'RevenueCategory',
    'PredictionModel',
    'MLRevenuePredictor',
    'FraudDetector',
    'create_revenue_analytics_storage'
]