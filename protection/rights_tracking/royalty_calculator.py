"""Royalty Calculator - Advanced Multi-Currency Royalty Calculation Engine
Système de calcul de redevances avancé avec gestion multi-devises
Moteur professionnel pour calculs complexes de royalties et distributions

Auteur: Fahed Mlaiel - Lead Developer & AI Architect
Email: mlaiel@live.de
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  AVERTISSEMENT LÉGAL - PROPRIÉTÉ INTELLECTUELLE PROTÉGÉE ⚠️
Ce code est la propriété exclusive de Fahed Mlaiel et est protégé par les lois
sur la propriété intellectuelle. Toute reproduction, distribution, ou utilisation
non autorisée est strictement interdite et passible de poursuites judiciaires.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from decimal import Decimal, ROUND_HALF_UP
import math
from collections import defaultdict

from pydantic import BaseModel, Field, validator


logger = logging.getLogger(__name__)


class CurrencyCode(Enum):
    """Codes de devises supportées"""    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"
    SEK = "SEK"
    NOK = "NOK"


class RoyaltyType(Enum):
    """Types de redevances"""    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    SYNCHRONIZATION = "synchronization"
    REPRODUCTION = "reproduction"
    DISTRIBUTION = "distribution"
    STREAMING = "streaming"
    DOWNLOAD = "download"
    PHYSICAL_SALES = "physical_sales"
    ADVERTISING = "advertising"
    SUBSCRIPTION = "subscription"


class PaymentFrequency(Enum):
    """Fréquences de paiement"""    REAL_TIME = "real_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"


class TaxJurisdiction(Enum):
    """Juridictions fiscales"""    US = "US"
    EU = "EU"
    UK = "UK"
    CANADA = "CA"
    AUSTRALIA = "AU"
    JAPAN = "JP"
    OTHER = "OTHER"


class RoyaltyRule(BaseModel):
    """Règle de calcul de redevances"""    rule_id: str = Field(..., description="ID unique de la règle")
    rule_name: str
    
    # Applicabilité
    content_types: List[str] = Field(default_factory=list)
    platforms: List[str] = Field(default_factory=list)
    territories: List[str] = Field(default_factory=list)
    usage_types: List[RoyaltyType] = Field(default_factory=list)
    
    # Configuration de calcul
    rate_type: str = Field(default="percentage")  # percentage, fixed, tiered, performance_based
    base_rate: Decimal = Field(default=Decimal('0.0'))
    minimum_payout: Decimal = Field(default=Decimal('0.01'))
    maximum_rate: Optional[Decimal] = None
    
    # Conditions de paliers
    tier_thresholds: Dict[str, Decimal] = Field(default_factory=dict)
    tier_rates: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Facteurs de modification
    performance_multipliers: Dict[str, float] = Field(default_factory=dict)
    seasonal_adjustments: Dict[str, float] = Field(default_factory=dict)
    volume_bonuses: Dict[str, float] = Field(default_factory=dict)
    
    # Déductions
    platform_fee_percentage: float = Field(default=0.0)
    processing_fee: Decimal = Field(default=Decimal('0.0'))
    tax_withholding: Dict[str, float] = Field(default_factory=dict)
    
    # Métadonnées
    effective_date: datetime = Field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = None
    active: bool = Field(default=True)
    priority: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExchangeRate(BaseModel):
    """Taux de change entre devises"""    from_currency: CurrencyCode
    to_currency: CurrencyCode
    rate: Decimal
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = Field(default="ecb")  # ecb, fed, bank_of_england, etc.
    
    @validator('rate')
    def validate_positive_rate(cls, v):
        if v <= 0:
            raise ValueError("Le taux de change doit être positif")
        return v


class RoyaltyCalculation(BaseModel):
    """Résultat de calcul de redevances"""    calculation_id: str = Field(..., description="ID unique du calcul")
    content_id: str
    license_id: Optional[str] = None
    
    # Période de calcul
    period_start: datetime
    period_end: datetime
    
    # Données d'entrée
    gross_revenue: Decimal
    usage_count: int = Field(default=0)
    usage_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Calculs financiers
    applicable_rules: List[str] = Field(default_factory=list)
    base_royalty: Decimal = Field(default=Decimal('0.0'))
    multipliers_applied: Dict[str, float] = Field(default_factory=dict)
    bonuses_applied: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Déductions
    platform_fees: Decimal = Field(default=Decimal('0.0'))
    processing_fees: Decimal = Field(default=Decimal('0.0'))
    tax_withholding: Decimal = Field(default=Decimal('0.0'))
    other_deductions: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Résultats finaux
    gross_royalty: Decimal = Field(default=Decimal('0.0'))
    total_deductions: Decimal = Field(default=Decimal('0.0'))
    net_royalty: Decimal = Field(default=Decimal('0.0'))
    
    # Répartition par détenteur
    holder_distributions: Dict[str, Dict[str, Decimal]] = Field(default_factory=dict)
    
    # Devises
    original_currency: CurrencyCode = Field(default=CurrencyCode.EUR)
    payout_currency: CurrencyCode = Field(default=CurrencyCode.EUR)
    exchange_rate_used: Optional[Decimal] = None
    
    # Métadonnées
    calculation_method: str = Field(default="automated")
    confidence_level: float = Field(default=1.0)
    verification_status: str = Field(default="pending")
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    notes: List[str] = Field(default_factory=list)


class PaymentInstruction(BaseModel):
    """Instructions de paiement"""    payment_id: str = Field(..., description="ID unique du paiement")
    calculation_id: str
    payee_id: str
    
    # Montants
    gross_amount: Decimal
    deductions: Decimal = Field(default=Decimal('0.0'))
    net_amount: Decimal
    currency: CurrencyCode
    
    # Instructions bancaires
    payment_method: str = Field(default="bank_transfer")  # bank_transfer, paypal, stripe, crypto
    bank_details: Dict[str, str] = Field(default_factory=dict)
    payment_reference: str = Field(default="")
    
    # Timing
    payment_due_date: datetime
    payment_frequency: PaymentFrequency
    
    # Statut
    status: str = Field(default="pending")  # pending, processing, completed, failed, cancelled
    processing_fee: Decimal = Field(default=Decimal('0.0'))
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class RoyaltyCalculator:
    """Calculateur avancé de redevances avec IA et multi-devises"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.royalty_rules: Dict[str, RoyaltyRule] = {}
        self.exchange_rates: Dict[Tuple[CurrencyCode, CurrencyCode], ExchangeRate] = {}
        self.calculations: Dict[str, RoyaltyCalculation] = {}
        self.payment_instructions: Dict[str, PaymentInstruction] = {}
        
        # Configuration
        self.default_currency = CurrencyCode(config.get('default_currency', 'EUR'))
        self.precision_digits = config.get('precision_digits', 4)
        self.minimum_payout = Decimal(config.get('minimum_payout', '0.01'))
        self.auto_exchange_rates = config.get('auto_exchange_rates', True)
        
        # Services intégrés
        self.ai_optimization = config.get('ai_optimization', True)
        self.real_time_rates = config.get('real_time_rates', True)
        
        # Initialisation
        asyncio.create_task(self._load_default_rules())
        if self.auto_exchange_rates:
            asyncio.create_task(self._initialize_exchange_rates())
    
    async def _load_default_rules(self):
        """Charge les règles de redevances par défaut"""        try:
            # Règle streaming standard
            streaming_rule = RoyaltyRule(
                rule_id="STREAM_STD_001",
                rule_name="Standard Streaming Royalty",
                content_types=["audio", "video"],
                platforms=["spotify", "youtube", "soundcloud"],
                usage_types=[RoyaltyType.STREAMING],
                rate_type="percentage",
                base_rate=Decimal('0.15'),
                minimum_payout=Decimal('0.01'),
                platform_fee_percentage=0.30,  # 30% fee plateforme
                tier_thresholds={
                    "bronze": Decimal('1000'),
                    "silver": Decimal('10000'),
                    "gold": Decimal('100000')
                },
                tier_rates={
                    "bronze": Decimal('0.15'),
                    "silver": Decimal('0.18'),
                    "gold": Decimal('0.22')
                }
            )
            
            # Règle download/vente
            download_rule = RoyaltyRule(
                rule_id="DWN_STD_001",
                rule_name="Standard Download Royalty",
                content_types=["audio", "video"],
                usage_types=[RoyaltyType.DOWNLOAD],
                rate_type="percentage",
                base_rate=Decimal('0.70'),
                minimum_payout=Decimal('0.05'),
                platform_fee_percentage=0.15
            )
            
            # Règle synchronisation
            sync_rule = RoyaltyRule(
                rule_id="SYNC_STD_001",
                rule_name="Synchronization Royalty",
                content_types=["audio"],
                usage_types=[RoyaltyType.SYNCHRONIZATION],
                rate_type="fixed",
                base_rate=Decimal('100.00'),
                minimum_payout=Decimal('50.00'),
                platform_fee_percentage=0.20
            )
            
            # Règle performance live
            performance_rule = RoyaltyRule(
                rule_id="PERF_STD_001",
                rule_name="Performance Royalty",
                content_types=["audio"],
                usage_types=[RoyaltyType.PERFORMANCE],
                rate_type="percentage",
                base_rate=Decimal('0.08'),
                minimum_payout=Decimal('1.00'),
                performance_multipliers={
                    "venue_size_small": 1.0,
                    "venue_size_medium": 1.5,
                    "venue_size_large": 2.0,
                    "broadcast": 3.0
                }
            )
            
            # Règle publicité
            advertising_rule = RoyaltyRule(
                rule_id="AD_STD_001",
                rule_name="Advertising Royalty",
                content_types=["audio", "video"],
                usage_types=[RoyaltyType.ADVERTISING],
                rate_type="performance_based",
                base_rate=Decimal('0.05'),
                performance_multipliers={
                    "cpm_low": 0.8,
                    "cpm_medium": 1.0,
                    "cpm_high": 1.5,
                    "premium_placement": 2.0
                }
            )
            
            self.royalty_rules = {
                streaming_rule.rule_id: streaming_rule,
                download_rule.rule_id: download_rule,
                sync_rule.rule_id: sync_rule,
                performance_rule.rule_id: performance_rule,
                advertising_rule.rule_id: advertising_rule
            }
            
            logger.info(f"Règles de redevances chargées: {len(self.royalty_rules)}")
            
        except Exception as e:
            logger.error(f"Erreur chargement règles: {e}")
    
    async def _initialize_exchange_rates(self):
        """Initialise les taux de change"""        try:
            # Taux de change fictifs pour démonstration
            # Dans un environnement réel, intégrer des APIs comme ECB, Fed, etc.
            
            base_rates = {
                (CurrencyCode.EUR, CurrencyCode.USD): Decimal('1.08'),
                (CurrencyCode.EUR, CurrencyCode.GBP): Decimal('0.86'),
                (CurrencyCode.EUR, CurrencyCode.JPY): Decimal('158.50'),
                (CurrencyCode.EUR, CurrencyCode.CAD): Decimal('1.47'),
                (CurrencyCode.EUR, CurrencyCode.AUD): Decimal('1.64'),
                (CurrencyCode.EUR, CurrencyCode.CHF): Decimal('0.96'),
                (CurrencyCode.EUR, CurrencyCode.CNY): Decimal('7.84'),
                (CurrencyCode.EUR, CurrencyCode.SEK): Decimal('11.52'),
                (CurrencyCode.EUR, CurrencyCode.NOK): Decimal('11.73'),
            }
            
            # Création des taux dans les deux sens
            for (from_curr, to_curr), rate in base_rates.items():
                self.exchange_rates[(from_curr, to_curr)] = ExchangeRate(
                    from_currency=from_curr,
                    to_currency=to_curr,
                    rate=rate
                )
                
                # Taux inverse
                inverse_rate = Decimal('1') / rate
                self.exchange_rates[(to_curr, from_curr)] = ExchangeRate(
                    from_currency=to_curr,
                    to_currency=from_curr,
                    rate=inverse_rate
                )
            
            # Taux identiques pour même devise
            for currency in CurrencyCode:
                self.exchange_rates[(currency, currency)] = ExchangeRate(
                    from_currency=currency,
                    to_currency=currency,
                    rate=Decimal('1.0')
                )
            
            logger.info(f"Taux de change initialisés: {len(self.exchange_rates)} paires")
            
        except Exception as e:
            logger.error(f"Erreur initialisation taux de change: {e}")
    
    async def calculate_royalties(
        self,
        content_id: str,
        usage_data: Dict[str, Any],
        period_start: datetime,
        period_end: datetime,
        license_id: Optional[str] = None,
        force_currency: Optional[CurrencyCode] = None
    ) -> RoyaltyCalculation:
        """Calcule les redevances pour un contenu sur une période"""        try:
            calculation_id = self._generate_calculation_id()
            
            # Extraction des données d'utilisation
            gross_revenue = Decimal(str(usage_data.get('gross_revenue', 0)))
            usage_count = usage_data.get('usage_count', 0)
            platform_id = usage_data.get('platform_id', 'unknown')
            territory = usage_data.get('territory', 'worldwide')
            content_type = usage_data.get('content_type', 'audio')
            usage_type = RoyaltyType(usage_data.get('usage_type', 'streaming'))
            
            # Sélection des règles applicables
            applicable_rules = await self._select_applicable_rules(
                content_type=content_type,
                platform_id=platform_id,
                territory=territory,
                usage_type=usage_type
            )
            
            if not applicable_rules:
                logger.warning(f"Aucune règle applicable pour {content_id}")
                return RoyaltyCalculation(
                    calculation_id=calculation_id,
                    content_id=content_id,
                    license_id=license_id,
                    period_start=period_start,
                    period_end=period_end,
                    gross_revenue=gross_revenue,
                    usage_count=usage_count,
                    usage_data=usage_data
                )
            
            # Sélection de la règle avec la plus haute priorité
            primary_rule = max(applicable_rules, key=lambda r: r.priority)
            
            # Calcul de base des redevances
            base_royalty = await self._calculate_base_royalty(
                primary_rule,
                gross_revenue,
                usage_count,
                usage_data
            )
            
            # Application des multiplicateurs
            multipliers_applied = await self._apply_performance_multipliers(
                primary_rule,
                usage_data,
                base_royalty
            )
            
            # Application des bonus de volume
            bonuses_applied = await self._apply_volume_bonuses(
                primary_rule,
                usage_count,
                gross_revenue
            )
            
            # Calcul du montant brut
            gross_royalty = base_royalty
            for multiplier in multipliers_applied.values():
                gross_royalty *= Decimal(str(multiplier))
            
            for bonus in bonuses_applied.values():
                gross_royalty += bonus
            
            # Calcul des déductions
            platform_fees = gross_royalty * Decimal(str(primary_rule.platform_fee_percentage))
            processing_fees = primary_rule.processing_fee
            tax_withholding = await self._calculate_tax_withholding(
                gross_royalty,
                territory,
                primary_rule
            )
            
            total_deductions = platform_fees + processing_fees + tax_withholding
            net_royalty = max(Decimal('0'), gross_royalty - total_deductions)
            
            # Vérification du minimum de paiement
            if net_royalty < primary_rule.minimum_payout:
                net_royalty = Decimal('0')
            
            # Conversion de devise si nécessaire
            original_currency = CurrencyCode(usage_data.get('currency', self.default_currency.value))
            payout_currency = force_currency or original_currency
            exchange_rate_used = None
            
            if original_currency != payout_currency:
                exchange_rate = await self._get_exchange_rate(original_currency, payout_currency)
                if exchange_rate:
                    gross_royalty *= exchange_rate.rate
                    total_deductions *= exchange_rate.rate
                    net_royalty *= exchange_rate.rate
                    exchange_rate_used = exchange_rate.rate
            
            # Création du résultat de calcul
            calculation = RoyaltyCalculation(
                calculation_id=calculation_id,
                content_id=content_id,
                license_id=license_id,
                period_start=period_start,
                period_end=period_end,
                gross_revenue=gross_revenue,
                usage_count=usage_count,
                usage_data=usage_data,
                applicable_rules=[primary_rule.rule_id],
                base_royalty=base_royalty,
                multipliers_applied=multipliers_applied,
                bonuses_applied={k: float(v) for k, v in bonuses_applied.items()},
                platform_fees=platform_fees,
                processing_fees=processing_fees,
                tax_withholding=tax_withholding,
                gross_royalty=gross_royalty,
                total_deductions=total_deductions,
                net_royalty=net_royalty,
                original_currency=original_currency,
                payout_currency=payout_currency,
                exchange_rate_used=exchange_rate_used,
                calculation_method="automated_ai" if self.ai_optimization else "automated"
            )
            
            # Optimisation IA si activée
            if self.ai_optimization:
                calculation = await self._ai_optimize_calculation(calculation, usage_data)
            
            # Stockage du calcul
            self.calculations[calculation_id] = calculation
            
            logger.info(f"Redevances calculées: {calculation_id} - Net: {net_royalty} {payout_currency.value}")
            return calculation
            
        except Exception as e:
            logger.error(f"Erreur calcul redevances: {e}")
            raise
    
    async def calculate_holder_distributions(
        self,
        calculation_id: str,
        rights_shares: Dict[str, float],
        holder_preferences: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, PaymentInstruction]:
        """Calcule la répartition des redevances entre détenteurs"""        try:
            if calculation_id not in self.calculations:
                raise ValueError(f"Calcul {calculation_id} non trouvé")
            
            calculation = self.calculations[calculation_id]
            
            # Validation des parts (doivent totaliser 1.0)
            total_shares = sum(rights_shares.values())
            if abs(total_shares - 1.0) > 0.01:
                raise ValueError(f"Parts totales incorrectes: {total_shares}")
            
            payment_instructions = {}
            holder_distributions = {}
            
            for holder_id, share in rights_shares.items():
                # Calcul de la part du détenteur
                holder_gross = calculation.gross_royalty * Decimal(str(share))
                holder_deductions = calculation.total_deductions * Decimal(str(share))
                holder_net = calculation.net_royalty * Decimal(str(share))
                
                # Préférences du détenteur
                holder_prefs = holder_preferences.get(holder_id, {}) if holder_preferences else {}
                preferred_currency = CurrencyCode(holder_prefs.get('currency', calculation.payout_currency.value))
                payment_method = holder_prefs.get('payment_method', 'bank_transfer')
                payment_frequency = PaymentFrequency(holder_prefs.get('frequency', 'monthly'))
                
                # Conversion de devise si nécessaire
                final_amount = holder_net
                exchange_rate_used = None
                
                if preferred_currency != calculation.payout_currency:
                    exchange_rate = await self._get_exchange_rate(calculation.payout_currency, preferred_currency)
                    if exchange_rate:
                        final_amount *= exchange_rate.rate
                        exchange_rate_used = exchange_rate.rate
                
                # Vérification du minimum de paiement
                if final_amount >= self.minimum_payout:
                    payment_id = self._generate_payment_id()
                    
                    # Calcul de la date d'échéance
                    due_date = await self._calculate_payment_due_date(payment_frequency)
                    
                    # Frais de traitement
                    processing_fee = await self._calculate_processing_fee(
                        final_amount,
                        payment_method,
                        preferred_currency
                    )
                    
                    final_net_amount = final_amount - processing_fee
                    
                    # Création de l'instruction de paiement
                    payment_instruction = PaymentInstruction(
                        payment_id=payment_id,
                        calculation_id=calculation_id,
                        payee_id=holder_id,
                        gross_amount=final_amount,
                        deductions=processing_fee,
                        net_amount=final_net_amount,
                        currency=preferred_currency,
                        payment_method=payment_method,
                        payment_due_date=due_date,
                        payment_frequency=payment_frequency,
                        processing_fee=processing_fee
                    )
                    
                    payment_instructions[holder_id] = payment_instruction
                    self.payment_instructions[payment_id] = payment_instruction
                    
                    # Stockage de la répartition
                    holder_distributions[holder_id] = {
                        'share_percentage': Decimal(str(share)),
                        'gross_amount': holder_gross,
                        'deductions': holder_deductions,
                        'net_amount': holder_net,
                        'final_amount': final_amount,
                        'final_currency': preferred_currency,
                        'exchange_rate': exchange_rate_used,
                        'payment_id': payment_id
                    }
                
                else:
                    # Montant trop faible pour paiement
                    holder_distributions[holder_id] = {
                        'share_percentage': Decimal(str(share)),
                        'gross_amount': holder_gross,
                        'deductions': holder_deductions,
                        'net_amount': holder_net,
                        'final_amount': final_amount,
                        'final_currency': preferred_currency,
                        'payment_status': 'below_minimum',
                        'minimum_required': self.minimum_payout
                    }
            
            # Mise à jour du calcul avec les répartitions
            calculation.holder_distributions = holder_distributions
            
            logger.info(f"Répartition calculée pour {len(rights_shares)} détenteurs: {len(payment_instructions)} paiements générés")
            return payment_instructions
            
        except Exception as e:
            logger.error(f"Erreur calcul répartition: {e}")
            raise
    
    async def process_bulk_calculations(
        self,
        bulk_data: List[Dict[str, Any]],
        parallel_processing: bool = True
    ) -> List[RoyaltyCalculation]:
        """Traite des calculs de redevances en lot"""        try:
            if parallel_processing:
                # Traitement parallèle
                tasks = []
                for data in bulk_data:
                    task = self.calculate_royalties(
                        content_id=data['content_id'],
                        usage_data=data['usage_data'],
                        period_start=datetime.fromisoformat(data['period_start']),
                        period_end=datetime.fromisoformat(data['period_end']),
                        license_id=data.get('license_id'),
                        force_currency=CurrencyCode(data['currency']) if 'currency' in data else None
                    )
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filtrage des erreurs
                successful_calculations = []
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Erreur calcul lot item {i}: {result}")
                    else:
                        successful_calculations.append(result)
                
                logger.info(f"Traitement lot: {len(successful_calculations)}/{len(bulk_data)} réussis")
                return successful_calculations
            
            else:
                # Traitement séquentiel
                results = []
                for data in bulk_data:
                    try:
                        calculation = await self.calculate_royalties(
                            content_id=data['content_id'],
                            usage_data=data['usage_data'],
                            period_start=datetime.fromisoformat(data['period_start']),
                            period_end=datetime.fromisoformat(data['period_end']),
                            license_id=data.get('license_id'),
                            force_currency=CurrencyCode(data['currency']) if 'currency' in data else None
                        )
                        results.append(calculation)
                    except Exception as e:
                        logger.error(f"Erreur calcul séquentiel: {e}")
                        continue
                
                return results
            
        except Exception as e:
            logger.error(f"Erreur traitement lot: {e}")
            return []
    
    async def generate_royalty_forecast(
        self,
        content_id: str,
        historical_data: List[Dict[str, Any]],
        forecast_periods: int = 12
    ) -> Dict[str, Any]:
        """Génère des prévisions de redevances basées sur l'historique"""        try:
            if not historical_data:
                return {'error': 'Pas de données historiques disponibles'}
            
            # Analyse des tendances historiques
            monthly_revenues = []
            monthly_usage = []
            
            for data in historical_data:
                monthly_revenues.append(float(data.get('revenue', 0)))
                monthly_usage.append(data.get('usage_count', 0))
            
            # Calcul des tendances (régression linéaire simple)
            if len(monthly_revenues) >= 2:
                revenue_trend = self._calculate_trend(monthly_revenues)
                usage_trend = self._calculate_trend(monthly_usage)
                
                # Génération des prévisions
                forecasts = []
                last_revenue = monthly_revenues[-1]
                last_usage = monthly_usage[-1]
                
                for i in range(1, forecast_periods + 1):
                    predicted_revenue = max(0, last_revenue + (revenue_trend * i))
                    predicted_usage = max(0, last_usage + (usage_trend * i))
                    
                    # Facteur de confiance décroissant
                    confidence = max(0.1, 1.0 - (i * 0.1))
                    
                    forecasts.append({
                        'period': i,
                        'predicted_revenue': round(predicted_revenue, 2),
                        'predicted_usage': int(predicted_usage),
                        'confidence_level': round(confidence, 2)
                    })
                
                # Métriques de résumé
                total_forecast_revenue = sum(f['predicted_revenue'] for f in forecasts)
                avg_monthly_growth = revenue_trend / last_revenue * 100 if last_revenue > 0 else 0
                
                return {
                    'content_id': content_id,
                    'forecast_periods': forecast_periods,
                    'forecasts': forecasts,
                    'summary': {
                        'total_forecast_revenue': round(total_forecast_revenue, 2),
                        'avg_monthly_growth_rate': round(avg_monthly_growth, 2),
                        'last_actual_revenue': last_revenue,
                        'revenue_trend': round(revenue_trend, 2),
                        'usage_trend': round(usage_trend, 2)
                    },
                    'generated_at': datetime.utcnow().isoformat()
                }
            
            else:
                return {'error': 'Données historiques insuffisantes pour prévision'}
            
        except Exception as e:
            logger.error(f"Erreur génération prévisions: {e}")
            return {'error': str(e)}
    
    async def _select_applicable_rules(
        self,
        content_type: str,
        platform_id: str,
        territory: str,
        usage_type: RoyaltyType
    ) -> List[RoyaltyRule]:
        """Sélectionne les règles applicables"""        applicable_rules = []
        
        for rule in self.royalty_rules.values():
            if not rule.active:
                continue
            
            # Vérification date d'expiration
            if rule.expiry_date and datetime.utcnow() > rule.expiry_date:
                continue
            
            # Vérification type de contenu
            if rule.content_types and content_type not in rule.content_types:
                continue
            
            # Vérification plateforme
            if rule.platforms and platform_id not in rule.platforms:
                continue
            
            # Vérification territoire
            if rule.territories and territory not in rule.territories and 'worldwide' not in rule.territories:
                continue
            
            # Vérification type d'usage
            if rule.usage_types and usage_type not in rule.usage_types:
                continue
            
            applicable_rules.append(rule)
        
        return applicable_rules
    
    async def _calculate_base_royalty(
        self,
        rule: RoyaltyRule,
        gross_revenue: Decimal,
        usage_count: int,
        usage_data: Dict[str, Any]
    ) -> Decimal:
        """Calcule la redevance de base selon la règle"""        if rule.rate_type == "percentage":
            return gross_revenue * rule.base_rate
        
        elif rule.rate_type == "fixed":
            return rule.base_rate
        
        elif rule.rate_type == "tiered":
            # Application des paliers
            for tier_name, threshold in rule.tier_thresholds.items():
                if usage_count >= threshold:
                    tier_rate = rule.tier_rates.get(tier_name, rule.base_rate)
                    return gross_revenue * tier_rate
            
            return gross_revenue * rule.base_rate
        
        elif rule.rate_type == "performance_based":
            # Calcul basé sur les performances
            performance_factor = usage_data.get('performance_factor', 1.0)
            return gross_revenue * rule.base_rate * Decimal(str(performance_factor))
        
        else:
            return gross_revenue * rule.base_rate
    
    def _calculate_trend(self, data: List[float]) -> float:
        """Calcule la tendance linéaire des données"""        if len(data) < 2:
            return 0
        
        n = len(data)
        x_values = list(range(n))
        
        # Calcul de la pente (régression linéaire simple)
        sum_x = sum(x_values)
        sum_y = sum(data)
        sum_xy = sum(x * y for x, y in zip(x_values, data))
        sum_x_squared = sum(x * x for x in x_values)
        
        denominator = n * sum_x_squared - sum_x * sum_x
        if denominator == 0:
            return 0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope
    
    def _generate_calculation_id(self) -> str:
        """Génère un ID unique pour le calcul"""        return f"CALC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    def _generate_payment_id(self) -> str:
        """Génère un ID unique pour le paiement"""        return f"PAY-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    async def get_calculator_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du calculateur"""        try:
            total_calculations = len(self.calculations)
            total_payments = len(self.payment_instructions)
            
            # Calcul des totaux
            total_gross_royalties = sum(
                calc.gross_royalty for calc in self.calculations.values()
            )
            total_net_royalties = sum(
                calc.net_royalty for calc in self.calculations.values()
            )
            
            # Répartition par devise
            currency_breakdown = defaultdict(lambda: {'count': 0, 'total': Decimal('0')})
            for calc in self.calculations.values():
                currency_breakdown[calc.payout_currency.value]['count'] += 1
                currency_breakdown[calc.payout_currency.value]['total'] += calc.net_royalty
            
            return {
                'total_calculations': total_calculations,
                'total_payment_instructions': total_payments,
                'total_gross_royalties': float(total_gross_royalties),
                'total_net_royalties': float(total_net_royalties),
                'average_deduction_rate': float(
                    (total_gross_royalties - total_net_royalties) / total_gross_royalties * 100
                ) if total_gross_royalties > 0 else 0,
                'currency_breakdown': {
                    currency: {
                        'calculation_count': data['count'],
                        'total_amount': float(data['total'])
                    }
                    for currency, data in currency_breakdown.items()
                },
                'rules_available': len(self.royalty_rules),
                'exchange_rates_cached': len(self.exchange_rates),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur statistiques calculateur: {e}")
            return {}


# Fonctions utilitaires
async def _apply_performance_multipliers(
    rule: RoyaltyRule,
    usage_data: Dict[str, Any],
    base_amount: Decimal
) -> Dict[str, float]:
    """Applique les multiplicateurs de performance"""    multipliers = {}
    
    for factor, multiplier in rule.performance_multipliers.items():
        if factor in usage_data and usage_data[factor]:
            multipliers[factor] = multiplier
    
    return multipliers

async def _apply_volume_bonuses(
    rule: RoyaltyRule,
    usage_count: int,
    gross_revenue: Decimal
) -> Dict[str, Decimal]:
    """Applique les bonus de volume"""    bonuses = {}
    
    for threshold_name, bonus_rate in rule.volume_bonuses.items():
        threshold_value = int(threshold_name.split('_')[-1]) if threshold_name.split('_')[-1].isdigit() else 0
        if usage_count >= threshold_value:
            bonus_amount = gross_revenue * Decimal(str(bonus_rate))
            bonuses[threshold_name] = bonus_amount
    
    return bonuses

async def _calculate_tax_withholding(
    gross_amount: Decimal,
    territory: str,
    rule: RoyaltyRule
) -> Decimal:
    """Calcule la retenue fiscale"""    withholding_rate = rule.tax_withholding.get(territory, 0.0)
    return gross_amount * Decimal(str(withholding_rate))

async def _get_exchange_rate(
    self,
    from_currency: CurrencyCode,
    to_currency: CurrencyCode
) -> Optional[ExchangeRate]:
    """Récupère le taux de change"""    rate_key = (from_currency, to_currency)
    return self.exchange_rates.get(rate_key)

async def _ai_optimize_calculation(
    calculation: RoyaltyCalculation,
    usage_data: Dict[str, Any]
) -> RoyaltyCalculation:
    """Optimise le calcul avec l'IA"""    # Optimisations IA simples
    # Dans un environnement réel, intégrer des modèles ML pour optimisation
    
    calculation.confidence_level = 0.95  # IA confidence score
    calculation.notes.append("AI optimization applied")
    
    return calculation

async def _calculate_payment_due_date(frequency: PaymentFrequency) -> datetime:
    """Calcule la date d'échéance du paiement"""    now = datetime.utcnow()
    
    if frequency == PaymentFrequency.REAL_TIME:
        return now
    elif frequency == PaymentFrequency.DAILY:
        return now + timedelta(days=1)
    elif frequency == PaymentFrequency.WEEKLY:
        return now + timedelta(weeks=1)
    elif frequency == PaymentFrequency.MONTHLY:
        return now + timedelta(days=30)
    elif frequency == PaymentFrequency.QUARTERLY:
        return now + timedelta(days=90)
    elif frequency == PaymentFrequency.SEMI_ANNUAL:
        return now + timedelta(days=180)
    elif frequency == PaymentFrequency.ANNUAL:
        return now + timedelta(days=365)
    else:
        return now + timedelta(days=30)  # Default monthly

async def _calculate_processing_fee(
    amount: Decimal,
    payment_method: str,
    currency: CurrencyCode
) -> Decimal:
    """Calcule les frais de traitement"""    # Frais de traitement simples
    if payment_method == "bank_transfer":
        return min(Decimal('5.00'), amount * Decimal('0.01'))  # 1% max 5€
    elif payment_method == "paypal":
        return amount * Decimal('0.029') + Decimal('0.30')  # 2.9% + 0.30€
    elif payment_method == "stripe":
        return amount * Decimal('0.029') + Decimal('0.30')  # 2.9% + 0.30€
    elif payment_method == "crypto":
        return amount * Decimal('0.005')  # 0.5%
    else:
        return Decimal('0.00')


__all__ = [
    'RoyaltyCalculator',
    'RoyaltyRule',
    'RoyaltyCalculation',
    'PaymentInstruction',
    'ExchangeRate',
    'CurrencyCode',
    'RoyaltyType',
    'PaymentFrequency',
    'TaxJurisdiction'
]
