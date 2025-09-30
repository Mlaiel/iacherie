"""🚀 Tenant Billing Manager - IA Influencer Agent Platform Enterprise
=====================================================================
Module: backend/platform_core/tenant_management/tenant_billing_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 FACTURATION ISOLÉE MULTI-TENANT
Système ultra-avancé de facturation et billing par tenant
- Facturation isolée par tenant avec multiple billing models
- Usage-based billing en temps réel avec metering précis
- Multi-currency support avec conversion automatique
- Subscription management avec prorations et upgrades
"""

import asyncio
import logging
import uuid
import json
import decimal
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import stripe
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)


class BillingModel(Enum):
    """Modèles de facturation"""
    SUBSCRIPTION = "subscription"
    USAGE_BASED = "usage_based"
    HYBRID = "hybrid"
    ONE_TIME = "one_time"
    FREEMIUM = "freemium"
    TIERED = "tiered"


class BillingCycle(Enum):
    """Cycles de facturation"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    WEEKLY = "weekly"
    DAILY = "daily"


class InvoiceStatus(Enum):
    """États des factures"""
    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(Enum):
    """États des paiements"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Currency(Enum):
    """Devises supportées"""
    USD = "usd"
    EUR = "eur"
    GBP = "gbp"
    CAD = "cad"
    JPY = "jpy"
    AUD = "aud"


@dataclass
class TenantBillingProfile:
    """Profil de facturation d'un tenant"""
    tenant_id: str
    billing_model: BillingModel
    billing_cycle: BillingCycle
    currency: Currency
    tax_rate: decimal.Decimal = decimal.Decimal('0.0')
    billing_address: Dict[str, str] = field(default_factory=dict)
    payment_methods: List[str] = field(default_factory=list)
    billing_contact: Dict[str, str] = field(default_factory=dict)
    credit_limit: decimal.Decimal = decimal.Decimal('0.0')
    auto_charge: bool = True
    invoice_delivery: str = "email"  # email, api, postal
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class UsageMetric:
    """Métrique d'usage facturable"""
    metric_id: str
    tenant_id: str
    metric_name: str
    metric_type: str  # api_calls, storage_gb, compute_hours, etc.
    quantity: decimal.Decimal
    unit_price: decimal.Decimal
    timestamp: datetime
    billing_period: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantInvoice:
    """Facture d'un tenant"""
    invoice_id: str
    tenant_id: str
    invoice_number: str
    billing_period_start: datetime
    billing_period_end: datetime
    currency: Currency
    subtotal: decimal.Decimal
    tax_amount: decimal.Decimal
    total_amount: decimal.Decimal
    status: InvoiceStatus
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    issued_at: datetime = field(default_factory=datetime.utcnow)
    due_date: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    paid_at: Optional[datetime] = None
    payment_intent_id: Optional[str] = None


@dataclass
class BillingPlan:
    """Plan de facturation"""
    plan_id: str
    plan_name: str
    billing_model: BillingModel
    currency: Currency
    base_price: decimal.Decimal
    billing_cycle: BillingCycle
    features: List[str] = field(default_factory=list)
    usage_limits: Dict[str, Any] = field(default_factory=dict)
    overage_pricing: Dict[str, decimal.Decimal] = field(default_factory=dict)
    trial_period_days: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PaymentTransaction:
    """Transaction de paiement"""
    transaction_id: str
    tenant_id: str
    invoice_id: str
    amount: decimal.Decimal
    currency: Currency
    payment_method: str
    status: PaymentStatus
    gateway_transaction_id: Optional[str] = None
    gateway_response: Dict[str, Any] = field(default_factory=dict)
    processed_at: datetime = field(default_factory=datetime.utcnow)
    failure_reason: Optional[str] = None


class TenantBillingManager:
    """
    🚀 Gestionnaire de facturation multi-tenant ultra-avancé
    
    Fonctionnalités Enterprise:
    - Facturation isolée par tenant avec billing models flexibles
    - Usage-based billing en temps réel avec metering précis
    - Subscription management avec upgrades/downgrades automatiques
    - Multi-currency support avec taux de change temps réel
    - Tax calculation automatique par région
    - Payment processing avec multiples gateways
    - Dunning management pour recouvrement automatique
    - Revenue recognition et reporting financier
    - Prorations intelligentes pour changements de plan
    """
    
    def __init__(
        self,
        database_url: str,
        redis_url: str,
        stripe_api_key: Optional[str] = None,
        default_currency: Currency = Currency.USD,
        enable_tax_calculation: bool = True
    ):
        self.database_url = database_url
        self.redis_url = redis_url
        self.stripe_api_key = stripe_api_key
        self.default_currency = default_currency
        self.enable_tax_calculation = enable_tax_calculation
        
        # Clients
        self.engine = None
        self.redis_client = None
        
        # Configuration Stripe
        if stripe_api_key:
            stripe.api_key = stripe_api_key
        
        # Caches
        self.billing_profiles: Dict[str, TenantBillingProfile] = {}
        self.billing_plans: Dict[str, BillingPlan] = {}
        self.pending_invoices: Dict[str, List[TenantInvoice]] = {}
        self.usage_buffer: Dict[str, List[UsageMetric]] = {}
        
        # Configuration
        self.billing_config = self._initialize_billing_config()
        self.tax_rates = self._initialize_tax_rates()
        self.currency_rates = {}  # À charger depuis un service externe
        
        # Statistiques
        self.billing_stats = {
            "total_tenants_billed": 0,
            "total_invoices_generated": 0,
            "total_revenue": decimal.Decimal('0.0'),
            "payment_success_rate": 0.0,
            "average_monthly_revenue": decimal.Decimal('0.0'),
            "churn_rate": 0.0
        }
        
        logger.info("TenantBillingManager initialisé")
    
    async def initialize(self) -> None:
        """Initialise le gestionnaire de facturation"""
        try:
            # Connexion base de données
            self.engine = create_async_engine(
                self.database_url,
                pool_size=15,
                max_overflow=25,
                pool_pre_ping=True
            )
            
            # Connexion Redis
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Initialisation des tables billing
            await self._initialize_billing_tables()
            
            # Chargement des configurations
            await self._load_billing_configurations()
            
            # Chargement des taux de change
            await self._load_currency_rates()
            
            # Démarrage des tâches de facturation
            asyncio.create_task(self._usage_metering_scheduler())
            asyncio.create_task(self._invoice_generation_scheduler())
            asyncio.create_task(self._payment_processing_scheduler())
            asyncio.create_task(self._dunning_management_scheduler())
            
            logger.info("TenantBillingManager initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation TenantBillingManager: {e}")
            raise
    
    async def setup_tenant_billing(
        self,
        tenant_id: str,
        billing_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        💳 Configure la facturation pour un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            billing_config: Configuration de facturation
            
        Returns:
            Configuration de facturation créée
        """
        try:
            setup_id = str(uuid.uuid4())
            
            # Validation de la configuration
            required_fields = ["billing_model", "currency"]
            for field in required_fields:
                if field not in billing_config:
                    raise ValueError(f"Champ requis manquant: {field}")
            
            # Création du profil de facturation
            billing_profile = TenantBillingProfile(
                tenant_id=tenant_id,
                billing_model=BillingModel(billing_config["billing_model"]),
                billing_cycle=BillingCycle(billing_config.get("billing_cycle", "monthly")),
                currency=Currency(billing_config["currency"]),
                tax_rate=decimal.Decimal(str(billing_config.get("tax_rate", 0.0))),
                billing_address=billing_config.get("billing_address", {}),
                billing_contact=billing_config.get("billing_contact", {}),
                credit_limit=decimal.Decimal(str(billing_config.get("credit_limit", 0.0))),
                auto_charge=billing_config.get("auto_charge", True),
                invoice_delivery=billing_config.get("invoice_delivery", "email")
            )
            
            # Configuration du customer Stripe si applicable
            stripe_customer_id = None
            if self.stripe_api_key:
                stripe_customer = await self._create_stripe_customer(tenant_id, billing_profile)
                stripe_customer_id = stripe_customer.id
                billing_profile.payment_methods.append(f"stripe:{stripe_customer_id}")
            
            # Sauvegarde du profil
            await self._save_billing_profile(billing_profile)
            
            # Mise en cache
            self.billing_profiles[tenant_id] = billing_profile
            
            # Configuration des méthodes de paiement par défaut
            payment_methods_setup = await self._setup_default_payment_methods(
                tenant_id,
                billing_config.get("payment_methods", [])
            )
            
            # Configuration des alertes de facturation
            billing_alerts = await self._setup_billing_alerts(tenant_id, billing_profile)
            
            # Mise à jour des statistiques
            self.billing_stats["total_tenants_billed"] += 1
            
            result = {
                "setup_id": setup_id,
                "tenant_id": tenant_id,
                "billing_profile": {
                    "billing_model": billing_profile.billing_model.value,
                    "billing_cycle": billing_profile.billing_cycle.value,
                    "currency": billing_profile.currency.value,
                    "tax_rate": float(billing_profile.tax_rate),
                    "auto_charge": billing_profile.auto_charge,
                    "invoice_delivery": billing_profile.invoice_delivery
                },
                "stripe_customer_id": stripe_customer_id,
                "payment_methods": payment_methods_setup,
                "billing_alerts": billing_alerts,
                "next_billing_date": self._calculate_next_billing_date(billing_profile).isoformat(),
                "setup_completed_at": datetime.utcnow().isoformat()
            }
            
            # Audit trail
            await self._log_billing_activity(
                tenant_id,
                "billing_setup",
                {
                    "setup_id": setup_id,
                    "billing_model": billing_profile.billing_model.value,
                    "currency": billing_profile.currency.value
                }
            )
            
            logger.info(f"Facturation configurée pour {tenant_id}: {billing_profile.billing_model.value}")
            return result
            
        except Exception as e:
            logger.error(f"Erreur configuration facturation {tenant_id}: {e}")
            raise
    
    async def record_usage_metric(
        self,
        tenant_id: str,
        metric_name: str,
        quantity: Union[int, float, decimal.Decimal],
        unit_price: Optional[Union[float, decimal.Decimal]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        📊 Enregistre une métrique d'usage facturable
        
        Args:
            tenant_id: Identifiant du tenant
            metric_name: Nom de la métrique
            quantity: Quantité utilisée
            unit_price: Prix unitaire (optionnel)
            metadata: Métadonnées additionnelles
            
        Returns:
            Confirmation d'enregistrement de la métrique
        """
        try:
            metric_id = str(uuid.uuid4())
            
            # Récupération du profil de facturation
            billing_profile = self.billing_profiles.get(tenant_id)
            if not billing_profile:
                raise ValueError(f"Profil de facturation non trouvé pour {tenant_id}")
            
            # Détermination du prix unitaire si non fourni
            if unit_price is None:
                unit_price = await self._get_metric_unit_price(
                    tenant_id,
                    metric_name,
                    billing_profile
                )
            
            # Création de la métrique d'usage
            usage_metric = UsageMetric(
                metric_id=metric_id,
                tenant_id=tenant_id,
                metric_name=metric_name,
                metric_type=self._classify_metric_type(metric_name),
                quantity=decimal.Decimal(str(quantity)),
                unit_price=decimal.Decimal(str(unit_price)),
                timestamp=datetime.utcnow(),
                billing_period=self._get_current_billing_period(billing_profile),
                metadata=metadata or {}
            )
            
            # Ajout au buffer d'usage
            if tenant_id not in self.usage_buffer:
                self.usage_buffer[tenant_id] = []
            self.usage_buffer[tenant_id].append(usage_metric)
            
            # Sauvegarde immédiate en Redis pour traçabilité
            await self.redis_client.setex(
                f"usage_metric:{tenant_id}:{metric_id}",
                86400,  # 24 heures
                json.dumps({
                    "metric_id": metric_id,
                    "metric_name": metric_name,
                    "quantity": str(usage_metric.quantity),
                    "unit_price": str(usage_metric.unit_price),
                    "timestamp": usage_metric.timestamp.isoformat()
                })
            )
            
            # Mise à jour des totaux en temps réel
            await self._update_real_time_usage_totals(tenant_id, usage_metric)
            
            # Vérification des seuils d'alerte
            await self._check_usage_thresholds(tenant_id, usage_metric)
            
            # Calcul du coût cumulé
            current_cost = usage_metric.quantity * usage_metric.unit_price
            
            result = {
                "metric_id": metric_id,
                "tenant_id": tenant_id,
                "metric_name": metric_name,
                "quantity": float(usage_metric.quantity),
                "unit_price": float(usage_metric.unit_price),
                "total_cost": float(current_cost),
                "currency": billing_profile.currency.value,
                "billing_period": usage_metric.billing_period,
                "recorded_at": usage_metric.timestamp.isoformat()
            }
            
            logger.debug(
                f"Métrique d'usage enregistrée: {tenant_id}/{metric_name} "
                f"({usage_metric.quantity} x {usage_metric.unit_price})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur enregistrement métrique usage {tenant_id}: {e}")
            raise
    
    async def generate_tenant_invoice(
        self,
        tenant_id: str,
        billing_period_start: Optional[datetime] = None,
        billing_period_end: Optional[datetime] = None,
        force_generation: bool = False
    ) -> Dict[str, Any]:
        """
        🧾 Génère une facture pour un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            billing_period_start: Début de la période (optionnel)
            billing_period_end: Fin de la période (optionnel)
            force_generation: Forcer la génération même si existe
            
        Returns:
            Facture générée avec détails
        """
        try:
            generation_id = str(uuid.uuid4())
            
            # Récupération du profil de facturation
            billing_profile = self.billing_profiles.get(tenant_id)
            if not billing_profile:
                raise ValueError(f"Profil de facturation non trouvé pour {tenant_id}")
            
            # Détermination de la période de facturation
            if not billing_period_start or not billing_period_end:
                period = self._calculate_billing_period(billing_profile)
                billing_period_start = period["start"]
                billing_period_end = period["end"]
            
            # Vérification d'existence d'une facture pour cette période
            existing_invoice = await self._check_existing_invoice(
                tenant_id,
                billing_period_start,
                billing_period_end
            )
            
            if existing_invoice and not force_generation:
                return {
                    "generation_id": generation_id,
                    "tenant_id": tenant_id,
                    "status": "already_exists",
                    "existing_invoice_id": existing_invoice["invoice_id"],
                    "message": "Facture déjà existante pour cette période"
                }
            
            # Collecte des métriques d'usage pour la période
            usage_metrics = await self._collect_usage_metrics(
                tenant_id,
                billing_period_start,
                billing_period_end
            )
            
            # Calcul des line items de la facture
            line_items = await self._calculate_invoice_line_items(
                tenant_id,
                billing_profile,
                usage_metrics,
                billing_period_start,
                billing_period_end
            )
            
            # Calcul des totaux
            subtotal = sum(item["total"] for item in line_items)
            
            # Calcul des taxes si activé
            tax_amount = decimal.Decimal('0.0')
            if self.enable_tax_calculation:
                tax_amount = await self._calculate_tax_amount(
                    tenant_id,
                    subtotal,
                    billing_profile
                )
            
            total_amount = subtotal + tax_amount
            
            # Génération du numéro de facture
            invoice_number = await self._generate_invoice_number(tenant_id)
            
            # Création de la facture
            invoice = TenantInvoice(
                invoice_id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                invoice_number=invoice_number,
                billing_period_start=billing_period_start,
                billing_period_end=billing_period_end,
                currency=billing_profile.currency,
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total_amount,
                status=InvoiceStatus.DRAFT,
                line_items=line_items,
                due_date=datetime.utcnow() + timedelta(
                    days=self.billing_config.get("default_payment_terms_days", 30)
                )
            )
            
            # Sauvegarde de la facture
            await self._save_invoice(invoice)
            
            # Mise en cache
            if tenant_id not in self.pending_invoices:
                self.pending_invoices[tenant_id] = []
            self.pending_invoices[tenant_id].append(invoice)
            
            # Création du payment intent si auto-charge activé
            payment_intent_id = None
            if billing_profile.auto_charge and self.stripe_api_key:
                payment_intent = await self._create_payment_intent(invoice)
                payment_intent_id = payment_intent.id
                invoice.payment_intent_id = payment_intent_id
                await self._update_invoice(invoice)
            
            # Mise à jour du statut de la facture
            invoice.status = InvoiceStatus.PENDING
            await self._update_invoice(invoice)
            
            # Mise à jour des statistiques
            self.billing_stats["total_invoices_generated"] += 1
            self.billing_stats["total_revenue"] += total_amount
            
            result = {
                "generation_id": generation_id,
                "invoice_id": invoice.invoice_id,
                "tenant_id": tenant_id,
                "invoice_number": invoice_number,
                "billing_period": {
                    "start": billing_period_start.isoformat(),
                    "end": billing_period_end.isoformat()
                },
                "amounts": {
                    "subtotal": float(subtotal),
                    "tax_amount": float(tax_amount),
                    "total_amount": float(total_amount),
                    "currency": billing_profile.currency.value
                },
                "line_items": line_items,
                "due_date": invoice.due_date.isoformat(),
                "status": invoice.status.value,
                "payment_intent_id": payment_intent_id,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Audit trail
            await self._log_billing_activity(
                tenant_id,
                "invoice_generated",
                {
                    "invoice_id": invoice.invoice_id,
                    "total_amount": float(total_amount),
                    "currency": billing_profile.currency.value
                }
            )
            
            logger.info(
                f"Facture générée pour {tenant_id}: {invoice_number} "
                f"({total_amount} {billing_profile.currency.value})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur génération facture {tenant_id}: {e}")
            raise
    
    async def process_tenant_payment(
        self,
        tenant_id: str,
        invoice_id: str,
        payment_method: str,
        amount: Optional[Union[float, decimal.Decimal]] = None
    ) -> Dict[str, Any]:
        """
        💰 Traite un paiement pour un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            invoice_id: Identifiant de la facture
            payment_method: Méthode de paiement
            amount: Montant à payer (optionnel, facture complète par défaut)
            
        Returns:
            Résultat du traitement du paiement
        """
        try:
            payment_id = str(uuid.uuid4())
            
            # Récupération de la facture
            invoice = await self._get_invoice(invoice_id)
            if not invoice or invoice.tenant_id != tenant_id:
                raise ValueError("Facture non trouvée ou accès non autorisé")
            
            # Détermination du montant à payer
            if amount is None:
                amount = invoice.total_amount
            else:
                amount = decimal.Decimal(str(amount))
            
            # Validation du montant
            if amount <= 0 or amount > invoice.total_amount:
                raise ValueError("Montant de paiement invalide")
            
            # Création de la transaction de paiement
            transaction = PaymentTransaction(
                transaction_id=payment_id,
                tenant_id=tenant_id,
                invoice_id=invoice_id,
                amount=amount,
                currency=invoice.currency,
                payment_method=payment_method,
                status=PaymentStatus.PENDING
            )
            
            # Traitement du paiement selon la méthode
            if payment_method.startswith("stripe:") and self.stripe_api_key:
                payment_result = await self._process_stripe_payment(
                    invoice,
                    transaction,
                    payment_method
                )
            else:
                # Autres méthodes de paiement
                payment_result = await self._process_alternative_payment(
                    invoice,
                    transaction,
                    payment_method
                )
            
            # Mise à jour de la transaction
            transaction.status = PaymentStatus(payment_result["status"])
            transaction.gateway_transaction_id = payment_result.get("gateway_transaction_id")
            transaction.gateway_response = payment_result.get("gateway_response", {})
            transaction.failure_reason = payment_result.get("failure_reason")
            
            # Sauvegarde de la transaction
            await self._save_payment_transaction(transaction)
            
            # Mise à jour de la facture si paiement réussi
            if transaction.status == PaymentStatus.SUCCEEDED:
                if amount >= invoice.total_amount:
                    invoice.status = InvoiceStatus.PAID
                    invoice.paid_at = datetime.utcnow()
                    await self._update_invoice(invoice)
                    
                    # Mise à jour des statistiques de succès
                    await self._update_payment_success_stats(tenant_id, amount)
                
                # Traitement post-paiement
                await self._handle_successful_payment(tenant_id, invoice, transaction)
            
            elif transaction.status == PaymentStatus.FAILED:
                # Gestion des échecs de paiement
                await self._handle_failed_payment(tenant_id, invoice, transaction)
            
            result = {
                "payment_id": payment_id,
                "tenant_id": tenant_id,
                "invoice_id": invoice_id,
                "transaction_details": {
                    "amount": float(amount),
                    "currency": invoice.currency.value,
                    "payment_method": payment_method,
                    "status": transaction.status.value,
                    "gateway_transaction_id": transaction.gateway_transaction_id
                },
                "invoice_status": invoice.status.value,
                "processed_at": transaction.processed_at.isoformat(),
                "failure_reason": transaction.failure_reason
            }
            
            # Audit trail
            await self._log_billing_activity(
                tenant_id,
                "payment_processed",
                {
                    "payment_id": payment_id,
                    "invoice_id": invoice_id,
                    "amount": float(amount),
                    "status": transaction.status.value
                }
            )
            
            logger.info(
                f"Paiement traité pour {tenant_id}: {amount} {invoice.currency.value} "
                f"({transaction.status.value})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur traitement paiement {tenant_id}: {e}")
            raise
    
    async def get_tenant_billing_summary(
        self,
        tenant_id: str,
        period_months: int = 12
    ) -> Dict[str, Any]:
        """
        📈 Récupère un résumé de facturation pour un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            period_months: Période d'analyse en mois
            
        Returns:
            Résumé détaillé de facturation
        """
        try:
            summary_id = str(uuid.uuid4())
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_months * 30)
            
            # Récupération du profil de facturation
            billing_profile = self.billing_profiles.get(tenant_id)
            if not billing_profile:
                raise ValueError(f"Profil de facturation non trouvé pour {tenant_id}")
            
            # Collecte des factures de la période
            invoices = await self._get_tenant_invoices(tenant_id, start_date, end_date)
            
            # Calcul des métriques financières
            financial_metrics = await self._calculate_financial_metrics(invoices)
            
            # Analyse des patterns d'usage
            usage_patterns = await self._analyze_usage_patterns(tenant_id, start_date, end_date)
            
            # Historique des paiements
            payment_history = await self._get_payment_history(tenant_id, start_date, end_date)
            
            # Prédictions de revenus
            revenue_forecast = await self._forecast_revenue(tenant_id, billing_profile, usage_patterns)
            
            # Analyse de la santé financière
            financial_health = await self._assess_financial_health(
                tenant_id,
                financial_metrics,
                payment_history
            )
            
            # Recommandations d'optimisation
            optimization_recommendations = await self._generate_billing_recommendations(
                tenant_id,
                billing_profile,
                financial_metrics,
                usage_patterns
            )
            
            summary = {
                "summary_id": summary_id,
                "tenant_id": tenant_id,
                "analysis_period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "duration_months": period_months
                },
                "billing_profile": {
                    "billing_model": billing_profile.billing_model.value,
                    "billing_cycle": billing_profile.billing_cycle.value,
                    "currency": billing_profile.currency.value,
                    "auto_charge": billing_profile.auto_charge
                },
                "financial_metrics": financial_metrics,
                "usage_patterns": usage_patterns,
                "payment_history": payment_history,
                "revenue_forecast": revenue_forecast,
                "financial_health": financial_health,
                "optimization_recommendations": optimization_recommendations,
                "current_status": {
                    "outstanding_amount": await self._get_outstanding_amount(tenant_id),
                    "next_billing_date": self._calculate_next_billing_date(billing_profile).isoformat(),
                    "payment_status": financial_health.get("payment_status", "unknown")
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Résumé de facturation généré pour {tenant_id}: {period_months} mois")
            return summary
            
        except Exception as e:
            logger.error(f"Erreur génération résumé facturation {tenant_id}: {e}")
            raise
    
    # Méthodes privées utilitaires
    
    def _initialize_billing_config(self) -> Dict[str, Any]:
        """Initialise la configuration de facturation"""
        return {
            "default_payment_terms_days": 30,
            "late_fee_percentage": 5.0,
            "currency_conversion_margin": 0.02,
            "invoice_number_prefix": "INV",
            "dunning_grace_period_days": 7,
            "auto_suspend_after_days": 30
        }
    
    def _initialize_tax_rates(self) -> Dict[str, decimal.Decimal]:
        """Initialise les taux de taxes par région"""
        return {
            "US": decimal.Decimal('0.08'),  # 8% moyenne US
            "EU": decimal.Decimal('0.20'),  # 20% TVA EU
            "CA": decimal.Decimal('0.13'),  # 13% HST Canada
            "GB": decimal.Decimal('0.20'),  # 20% VAT UK
            "default": decimal.Decimal('0.0')
        }
    
    async def _initialize_billing_tables(self) -> None:
        """Initialise les tables de facturation"""
        async with self.engine.begin() as conn:
            # Table des profils de facturation
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS tenant_billing_profiles (
                    tenant_id VARCHAR(255) PRIMARY KEY,
                    billing_model VARCHAR(50),
                    billing_cycle VARCHAR(50),
                    currency VARCHAR(10),
                    tax_rate DECIMAL(5,4),
                    billing_address JSONB,
                    payment_methods TEXT[],
                    billing_contact JSONB,
                    credit_limit DECIMAL(15,2),
                    auto_charge BOOLEAN DEFAULT TRUE,
                    invoice_delivery VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """))
            
            # Table des métriques d'usage
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS usage_metrics (
                    metric_id VARCHAR(255) PRIMARY KEY,
                    tenant_id VARCHAR(255),
                    metric_name VARCHAR(255),
                    metric_type VARCHAR(100),
                    quantity DECIMAL(15,4),
                    unit_price DECIMAL(10,4),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    billing_period VARCHAR(50),
                    metadata JSONB
                )
            """))
            
            # Table des factures
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS tenant_invoices (
                    invoice_id VARCHAR(255) PRIMARY KEY,
                    tenant_id VARCHAR(255),
                    invoice_number VARCHAR(100),
                    billing_period_start TIMESTAMP,
                    billing_period_end TIMESTAMP,
                    currency VARCHAR(10),
                    subtotal DECIMAL(15,2),
                    tax_amount DECIMAL(15,2),
                    total_amount DECIMAL(15,2),
                    status VARCHAR(20),
                    line_items JSONB,
                    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    due_date TIMESTAMP,
                    paid_at TIMESTAMP,
                    payment_intent_id VARCHAR(255)
                )
            """))
            
            # Table des transactions de paiement
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS payment_transactions (
                    transaction_id VARCHAR(255) PRIMARY KEY,
                    tenant_id VARCHAR(255),
                    invoice_id VARCHAR(255),
                    amount DECIMAL(15,2),
                    currency VARCHAR(10),
                    payment_method VARCHAR(100),
                    status VARCHAR(20),
                    gateway_transaction_id VARCHAR(255),
                    gateway_response JSONB,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    failure_reason TEXT
                )
            """))
    
    async def _load_billing_configurations(self) -> None:
        """Charge les configurations de facturation"""
        # Chargement des profils de facturation existants
        async with self.engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT * FROM tenant_billing_profiles WHERE is_active = TRUE
            """))
            
            for row in result:
                profile = TenantBillingProfile(
                    tenant_id=row.tenant_id,
                    billing_model=BillingModel(row.billing_model),
                    billing_cycle=BillingCycle(row.billing_cycle),
                    currency=Currency(row.currency),
                    tax_rate=row.tax_rate,
                    billing_address=row.billing_address or {},
                    payment_methods=row.payment_methods or [],
                    billing_contact=row.billing_contact or {},
                    credit_limit=row.credit_limit,
                    auto_charge=row.auto_charge,
                    invoice_delivery=row.invoice_delivery,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                    is_active=row.is_active
                )
                self.billing_profiles[row.tenant_id] = profile
    
    async def _load_currency_rates(self) -> None:
        """Charge les taux de change actuels"""
        # En production, charger depuis un service de taux de change
        self.currency_rates = {
            "USD": 1.0,
            "EUR": 0.85,
            "GBP": 0.73,
            "CAD": 1.25,
            "JPY": 110.0,
            "AUD": 1.35
        }
    
    async def _create_stripe_customer(
        self,
        tenant_id: str,
        billing_profile: TenantBillingProfile
    ) -> Any:
        """Crée un customer Stripe"""
        if not self.stripe_api_key:
            raise ValueError("Stripe API key non configurée")
        
        customer_data = {
            "metadata": {"tenant_id": tenant_id},
            "preferred_locales": ["en"]
        }
        
        if billing_profile.billing_contact:
            customer_data.update({
                "name": billing_profile.billing_contact.get("name"),
                "email": billing_profile.billing_contact.get("email"),
                "phone": billing_profile.billing_contact.get("phone")
            })
        
        if billing_profile.billing_address:
            customer_data["address"] = billing_profile.billing_address
        
        return stripe.Customer.create(**customer_data)
    
    def _calculate_next_billing_date(self, billing_profile: TenantBillingProfile) -> datetime:
        """Calcule la prochaine date de facturation"""
        now = datetime.utcnow()
        
        if billing_profile.billing_cycle == BillingCycle.MONTHLY:
            return now.replace(day=1) + timedelta(days=32)
        elif billing_profile.billing_cycle == BillingCycle.YEARLY:
            return now.replace(month=1, day=1) + timedelta(days=366)
        elif billing_profile.billing_cycle == BillingCycle.WEEKLY:
            return now + timedelta(weeks=1)
        else:
            return now + timedelta(days=30)  # Default monthly
    
    async def _usage_metering_scheduler(self) -> None:
        """Planificateur de mesure d'usage"""
        while True:
            try:
                # Flush périodique des métriques d'usage
                for tenant_id in list(self.usage_buffer.keys()):
                    await self._flush_usage_metrics(tenant_id)
                
                await asyncio.sleep(300)  # Toutes les 5 minutes
            except Exception as e:
                logger.error(f"Erreur usage metering scheduler: {e}")
                await asyncio.sleep(300)
    
    async def _invoice_generation_scheduler(self) -> None:
        """Planificateur de génération de factures"""
        while True:
            try:
                # Génération automatique des factures selon les cycles
                await asyncio.sleep(3600)  # Toutes les heures
            except Exception as e:
                logger.error(f"Erreur invoice generation scheduler: {e}")
                await asyncio.sleep(3600)
    
    async def _payment_processing_scheduler(self) -> None:
        """Planificateur de traitement des paiements"""
        while True:
            try:
                # Traitement des paiements en attente
                await asyncio.sleep(600)  # Toutes les 10 minutes
            except Exception as e:
                logger.error(f"Erreur payment processing scheduler: {e}")
                await asyncio.sleep(600)
    
    async def _dunning_management_scheduler(self) -> None:
        """Planificateur de gestion des impayés"""
        while True:
            try:
                # Gestion des factures en retard
                await asyncio.sleep(86400)  # Tous les jours
            except Exception as e:
                logger.error(f"Erreur dunning management scheduler: {e}")
                await asyncio.sleep(86400)
    
    async def _log_billing_activity(
        self,
        tenant_id: str,
        activity_type: str,
        details: Dict[str, Any]
    ) -> None:
        """Enregistre une activité de facturation"""
        activity_data = {
            "tenant_id": tenant_id,
            "activity_type": activity_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.redis_client.setex(
            f"billing_activity:{tenant_id}:{int(datetime.utcnow().timestamp())}",
            timedelta(days=365).total_seconds(),  # Conservation 1 an
            json.dumps(activity_data)
        )
    
    async def cleanup(self) -> None:
        """Nettoyage des ressources"""
        # Flush final des métriques d'usage
        for tenant_id in list(self.usage_buffer.keys()):
            await self._flush_usage_metrics(tenant_id)
        
        if self.engine:
            await self.engine.dispose()
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("TenantBillingManager nettoyé")


# Instance principale
tenant_billing_manager = None


async def get_tenant_billing_manager() -> TenantBillingManager:
    """Factory pour l'instance TenantBillingManager"""
    global tenant_billing_manager
    if not tenant_billing_manager:
        database_url = "postgresql+asyncpg://localhost/ainflue_billing"
        redis_url = "redis://localhost:6379/8"
        stripe_key = "sk_test_..."  # Clé de test Stripe
        
        tenant_billing_manager = TenantBillingManager(
            database_url=database_url,
            redis_url=redis_url,
            stripe_api_key=stripe_key,
            default_currency=Currency.USD
        )
        await tenant_billing_manager.initialize()
    
    return tenant_billing_manager


# Tests de démonstration
async def main():
    """Fonction principale pour tests et démonstration"""
    manager = await get_tenant_billing_manager()
    
    test_tenant_id = "tenant_billing_demo"
    
    try:
        # Test configuration facturation
        billing_config = {
            "billing_model": "usage_based",
            "billing_cycle": "monthly",
            "currency": "usd",
            "tax_rate": 0.08,
            "auto_charge": True,
            "billing_contact": {
                "name": "Test Company",
                "email": "billing@test.com"
            }
        }
        
        setup_result = await manager.setup_tenant_billing(test_tenant_id, billing_config)
        print(f"✅ Facturation configurée: {setup_result['billing_profile']['billing_model']}")
        
        # Test enregistrement métriques d'usage
        usage_result = await manager.record_usage_metric(
            test_tenant_id,
            "api_calls",
            1000,
            0.001  # $0.001 par appel API
        )
        print(f"✅ Métrique d'usage: {usage_result['total_cost']}$ pour {usage_result['quantity']} appels")
        
        # Test génération facture
        invoice_result = await manager.generate_tenant_invoice(test_tenant_id)
        print(f"✅ Facture générée: {invoice_result['invoice_number']}")
        print(f"   Montant: {invoice_result['amounts']['total_amount']} {invoice_result['amounts']['currency']}")
        
        # Test résumé de facturation
        summary = await manager.get_tenant_billing_summary(test_tenant_id, 6)
        print(f"✅ Résumé généré: {summary['analysis_period']['duration_months']} mois")
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    finally:
        await manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())