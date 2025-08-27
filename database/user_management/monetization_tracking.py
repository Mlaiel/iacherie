"""
Monetization Tracking Database Models and Operations

Gestion complète du suivi de monétisation avec revenus automatisés,
analytics financières et optimisation IA.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer & Monetization Specialist

AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle de Fahed Mlaiel.
Toute utilisation, reproduction ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de 
poursuites judiciaires selon la loi allemande.
Email: mlaiel@live.de pour autorisation d'utilisation.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum, ForeignKey, Decimal, Index
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum as PyEnum
import logging
import uuid
import json
from decimal import Decimal as PyDecimal

logger = logging.getLogger(__name__)

Base = declarative_base()


class RevenueSource(PyEnum):
    """Sources de revenus supportées."""
    STREAMING_ROYALTIES = "streaming_royalties"
    DOWNLOAD_SALES = "download_sales"
    LICENSING_FEES = "licensing_fees"
    SYNC_RIGHTS = "sync_rights"
    MERCHANDISE = "merchandise"
    LIVE_PERFORMANCES = "live_performances"
    SPONSORSHIPS = "sponsorships"
    BRAND_PARTNERSHIPS = "brand_partnerships"
    SUBSCRIPTION_FEES = "subscription_fees"
    AD_REVENUE = "ad_revenue"
    TIPS_DONATIONS = "tips_donations"
    CONTENT_PROTECTION = "content_protection"


class PaymentStatus(PyEnum):
    """Statuts de paiement."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class RevenueType(PyEnum):
    """Types de revenus."""
    GROSS = "gross"
    NET = "net"
    COMMISSION = "commission"
    ROYALTY = "royalty"
    BONUS = "bonus"
    PENALTY = "penalty"


class Currency(PyEnum):
    """Devises supportées."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"


class RevenueTransaction(Base):
    """
    Transaction de revenus avec tracking complet et attribution.
    """
    __tablename__ = "revenue_transactions"

    # Identifiants principaux
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_uuid = Column(String, unique=True, nullable=False)
    creator_id = Column(String, ForeignKey("creator_accounts.id"), nullable=False)
    
    # Source et attribution
    revenue_source = Column(Enum(RevenueSource), nullable=False)
    platform_id = Column(String, ForeignKey("platform_integrations.id"))
    content_id = Column(String)  # ID du contenu générant le revenu
    collaboration_id = Column(String, ForeignKey("collaborations.id"))  # Si applicable
    
    # Détails financiers
    gross_amount = Column(Decimal(12, 4), nullable=False)
    net_amount = Column(Decimal(12, 4), nullable=False)
    currency = Column(Enum(Currency), default=Currency.EUR)
    exchange_rate = Column(Decimal(10, 6), default=1.0)
    amount_usd = Column(Decimal(12, 4))  # Montant converti en USD
    
    # Commissions et frais
    platform_commission = Column(Decimal(12, 4), default=0.0)
    platform_commission_rate = Column(Decimal(5, 4), default=0.0)
    service_fee = Column(Decimal(12, 4), default=0.0)
    processing_fee = Column(Decimal(12, 4), default=0.0)
    tax_amount = Column(Decimal(12, 4), default=0.0)
    
    # Informations de paiement
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(String(100))
    payment_reference = Column(String(200))
    payment_processor = Column(String(100))
    
    # Période et attribution temporelle
    revenue_period_start = Column(DateTime)
    revenue_period_end = Column(DateTime)
    earned_date = Column(DateTime, nullable=False)
    payment_date = Column(DateTime)
    reporting_date = Column(DateTime, default=datetime.utcnow)
    
    # Métadonnées détaillées
    transaction_details = Column(JSON)  # Détails spécifiques à la source
    geographic_data = Column(JSON)  # Données géographiques des revenus
    demographic_data = Column(JSON)  # Données démographiques
    attribution_data = Column(JSON)  # Attribution marketing/promotion
    
    # Validation et conformité
    is_validated = Column(Boolean, default=False)
    validation_date = Column(DateTime)
    tax_jurisdiction = Column(String(10))
    requires_tax_reporting = Column(Boolean, default=False)
    
    # Métadonnées système
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    imported_at = Column(DateTime, default=datetime.utcnow)
    external_transaction_id = Column(String(200))

    def __init__(self, **kwargs):
        super().__init__()
        self.transaction_uuid = str(uuid.uuid4())
        for key, value in kwargs.items():
            setattr(self, key, value)


class RevenueProjection(Base):
    """
    Projections de revenus basées sur l'IA et l'analyse prédictive.
    """
    __tablename__ = "revenue_projections"

    # Identifiants principaux
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    projection_uuid = Column(String, unique=True, nullable=False)
    creator_id = Column(String, ForeignKey("creator_accounts.id"), nullable=False)
    
    # Période de projection
    projection_period = Column(String(20), nullable=False)  # "monthly", "quarterly", "yearly"
    projection_start_date = Column(DateTime, nullable=False)
    projection_end_date = Column(DateTime, nullable=False)
    
    # Projections par source
    streaming_projection = Column(Decimal(12, 2), default=0.0)
    licensing_projection = Column(Decimal(12, 2), default=0.0)
    merchandise_projection = Column(Decimal(12, 2), default=0.0)
    performance_projection = Column(Decimal(12, 2), default=0.0)
    sponsorship_projection = Column(Decimal(12, 2), default=0.0)
    total_projection = Column(Decimal(12, 2), default=0.0)
    
    # Méthodologie et confiance
    projection_method = Column(String(100))  # "ml_model", "trend_analysis", "manual"
    confidence_score = Column(Decimal(3, 2), default=0.0)  # 0-1
    model_version = Column(String(50))
    input_factors = Column(JSON)  # Facteurs utilisés pour la projection
    
    # Scénarios
    conservative_estimate = Column(Decimal(12, 2), default=0.0)
    realistic_estimate = Column(Decimal(12, 2), default=0.0)
    optimistic_estimate = Column(Decimal(12, 2), default=0.0)
    
    # Données historiques utilisées
    historical_period_months = Column(Integer, default=12)
    trend_factors = Column(JSON)  # Facteurs de tendance identifiés
    seasonality_adjustments = Column(JSON)  # Ajustements saisonniers
    
    # Validation et performance
    actual_revenue = Column(Decimal(12, 2))  # Revenu réel (une fois la période écoulée)
    accuracy_score = Column(Decimal(3, 2))  # Précision de la projection
    variance_percentage = Column(Decimal(5, 2))  # Écart par rapport au réel
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    generated_by = Column(String(100), default="ai_model")

    def __init__(self, **kwargs):
        super().__init__()
        self.projection_uuid = str(uuid.uuid4())
        for key, value in kwargs.items():
            setattr(self, key, value)


class RevenueAnalytics(Base):
    """
    Analytics détaillées des revenus avec insights IA.
    """
    __tablename__ = "revenue_analytics"

    # Identifiants principaux
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    analytics_uuid = Column(String, unique=True, nullable=False)
    creator_id = Column(String, ForeignKey("creator_accounts.id"), nullable=False)
    
    # Période d'analyse
    analysis_period = Column(String(20), nullable=False)  # "daily", "weekly", "monthly"
    period_start_date = Column(DateTime, nullable=False)
    period_end_date = Column(DateTime, nullable=False)
    
    # Métriques principales
    total_revenue = Column(Decimal(12, 2), default=0.0)
    total_transactions = Column(Integer, default=0)
    average_transaction_value = Column(Decimal(10, 2), default=0.0)
    revenue_growth_rate = Column(Decimal(5, 2), default=0.0)
    
    # Répartition par source
    revenue_by_source = Column(JSON)  # {"streaming": 1000, "licensing": 500, ...}
    source_percentages = Column(JSON)  # Pourcentages par source
    top_revenue_sources = Column(JSON)  # Top 5 sources
    
    # Répartition géographique
    revenue_by_country = Column(JSON)  # Revenus par pays
    top_markets = Column(JSON)  # Top 5 marchés
    market_penetration = Column(JSON)  # Pénétration par marché
    
    # Analyses temporelles
    daily_revenue_trend = Column(JSON)  # Tendance quotidienne
    weekly_patterns = Column(JSON)  # Patterns hebdomadaires
    seasonal_trends = Column(JSON)  # Tendances saisonnières
    peak_periods = Column(JSON)  # Périodes de pic
    
    # Performance relative
    industry_benchmark = Column(Decimal(5, 2))  # Benchmark industrie
    peer_comparison = Column(JSON)  # Comparaison avec pairs
    market_position = Column(String(50))  # "top_10_percent", "average", etc.
    
    # Insights IA
    ai_insights = Column(JSON)  # Insights générés par IA
    optimization_recommendations = Column(JSON)  # Recommandations
    risk_factors = Column(JSON)  # Facteurs de risque identifiés
    opportunities = Column(JSON)  # Opportunités identifiées
    
    # Métriques de performance
    revenue_per_content = Column(Decimal(10, 2), default=0.0)
    monetization_efficiency = Column(Decimal(5, 2), default=0.0)
    audience_value = Column(Decimal(10, 2), default=0.0)  # Valeur par fan/follower
    
    # Prévisions courtes
    next_period_forecast = Column(Decimal(12, 2), default=0.0)
    forecast_confidence = Column(Decimal(3, 2), default=0.0)
    
    # Métadonnées
    calculated_at = Column(DateTime, default=datetime.utcnow)
    data_completeness = Column(Decimal(3, 2), default=1.0)  # Complétude des données
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__()
        self.analytics_uuid = str(uuid.uuid4())
        for key, value in kwargs.items():
            setattr(self, key, value)


class PayoutRequest(Base):
    """
    Demandes de paiement avec gestion automatisée.
    """
    __tablename__ = "payout_requests"

    # Identifiants principaux
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    payout_uuid = Column(String, unique=True, nullable=False)
    creator_id = Column(String, ForeignKey("creator_accounts.id"), nullable=False)
    
    # Détails du paiement
    requested_amount = Column(Decimal(12, 2), nullable=False)
    available_balance = Column(Decimal(12, 2), nullable=False)
    currency = Column(Enum(Currency), default=Currency.EUR)
    
    # Configuration de paiement
    payout_method = Column(String(100), nullable=False)  # "bank_transfer", "paypal", "stripe"
    payment_details = Column(JSON)  # Détails de paiement chiffrés
    processing_fee = Column(Decimal(10, 2), default=0.0)
    net_payout_amount = Column(Decimal(12, 2))
    
    # Statut et traitement
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Validation et conformité
    requires_verification = Column(Boolean, default=False)
    verification_documents = Column(JSON)  # Documents requis
    tax_withholding = Column(Decimal(10, 2), default=0.0)
    compliance_status = Column(String(50), default="pending")
    
    # Références externes
    payment_processor_reference = Column(String(200))
    bank_reference = Column(String(200))
    transaction_hash = Column(String(200))  # Pour crypto
    
    # Métadonnées
    processor_response = Column(JSON)  # Réponse du processeur
    error_details = Column(JSON)  # Détails d'erreur
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__()
        self.payout_uuid = str(uuid.uuid4())
        for key, value in kwargs.items():
            setattr(self, key, value)


# Index pour optimiser les performances
Index('idx_revenue_creator_date', RevenueTransaction.creator_id, RevenueTransaction.earned_date)
Index('idx_revenue_source_status', RevenueTransaction.revenue_source, RevenueTransaction.payment_status)
Index('idx_analytics_creator_period', RevenueAnalytics.creator_id, RevenueAnalytics.period_start_date)


class MonetizationRepository:
    """
    Repository pour la gestion de la monétisation et des revenus.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def record_transaction(self, transaction_data: Dict[str, Any]) -> RevenueTransaction:
        """Enregistrer une nouvelle transaction de revenu."""
        try:
            transaction = RevenueTransaction(**transaction_data)
            
            # Calculer le montant USD si nécessaire
            if transaction.currency != Currency.USD and transaction.exchange_rate:
                transaction.amount_usd = transaction.net_amount * transaction.exchange_rate
            else:
                transaction.amount_usd = transaction.net_amount
            
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            
            logger.info(f"Transaction enregistrée: {transaction.transaction_uuid}")
            return transaction
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur enregistrement transaction: {str(e)}")
            raise

    def get_revenue_summary(self, creator_id: str, days: int = 30) -> Dict[str, Any]:
        """Obtenir un résumé des revenus pour une période."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            transactions = self.db.query(RevenueTransaction).filter(
                RevenueTransaction.creator_id == creator_id,
                RevenueTransaction.earned_date >= start_date,
                RevenueTransaction.payment_status.in_([PaymentStatus.COMPLETED, PaymentStatus.PENDING])
            ).all()
            
            total_revenue = sum(t.net_amount for t in transactions)
            total_transactions = len(transactions)
            
            # Répartition par source
            revenue_by_source = {}
            for transaction in transactions:
                source = transaction.revenue_source.value
                revenue_by_source[source] = revenue_by_source.get(source, 0) + float(transaction.net_amount)
            
            # Revenus par statut
            pending_revenue = sum(
                t.net_amount for t in transactions 
                if t.payment_status == PaymentStatus.PENDING
            )
            
            completed_revenue = sum(
                t.net_amount for t in transactions 
                if t.payment_status == PaymentStatus.COMPLETED
            )
            
            # Croissance (comparaison période précédente)
            previous_start = start_date - timedelta(days=days)
            previous_transactions = self.db.query(RevenueTransaction).filter(
                RevenueTransaction.creator_id == creator_id,
                RevenueTransaction.earned_date >= previous_start,
                RevenueTransaction.earned_date < start_date,
                RevenueTransaction.payment_status.in_([PaymentStatus.COMPLETED, PaymentStatus.PENDING])
            ).all()
            
            previous_revenue = sum(t.net_amount for t in previous_transactions)
            growth_rate = 0
            if previous_revenue > 0:
                growth_rate = ((float(total_revenue) - float(previous_revenue)) / float(previous_revenue)) * 100
            
            return {
                "period_days": days,
                "total_revenue": float(total_revenue),
                "total_transactions": total_transactions,
                "average_transaction": float(total_revenue / total_transactions) if total_transactions > 0 else 0,
                "pending_revenue": float(pending_revenue),
                "completed_revenue": float(completed_revenue),
                "revenue_by_source": revenue_by_source,
                "growth_rate": round(growth_rate, 2),
                "currency": "EUR"  # Par défaut
            }
            
        except Exception as e:
            logger.error(f"Erreur résumé revenus: {str(e)}")
            return {}

    def create_revenue_projection(self, creator_id: str, projection_data: Dict[str, Any]) -> RevenueProjection:
        """Créer une projection de revenus."""
        try:
            # Analyser les données historiques pour la projection
            historical_data = self._get_historical_revenue_data(creator_id, 
                                                              projection_data.get('historical_period_months', 12))
            
            # Calculer les projections basées sur les tendances
            projection_amounts = self._calculate_projections(historical_data, projection_data)
            
            projection_data.update(projection_amounts)
            
            projection = RevenueProjection(
                creator_id=creator_id,
                **projection_data
            )
            
            self.db.add(projection)
            self.db.commit()
            self.db.refresh(projection)
            
            logger.info(f"Projection créée: {projection.projection_uuid}")
            return projection
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur création projection: {str(e)}")
            raise

    def generate_revenue_analytics(self, creator_id: str, period: str = "monthly") -> RevenueAnalytics:
        """Générer des analytics de revenus avec insights IA."""
        try:
            # Déterminer la période d'analyse
            end_date = datetime.utcnow()
            if period == "daily":
                start_date = end_date - timedelta(days=1)
            elif period == "weekly":
                start_date = end_date - timedelta(weeks=1)
            elif period == "monthly":
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Récupérer les transactions de la période
            transactions = self.db.query(RevenueTransaction).filter(
                RevenueTransaction.creator_id == creator_id,
                RevenueTransaction.earned_date >= start_date,
                RevenueTransaction.earned_date <= end_date
            ).all()
            
            # Calculer les métriques de base
            total_revenue = sum(t.net_amount for t in transactions)
            total_transactions = len(transactions)
            avg_transaction = total_revenue / total_transactions if total_transactions > 0 else 0
            
            # Analyser la répartition par source
            revenue_by_source = {}
            for transaction in transactions:
                source = transaction.revenue_source.value
                revenue_by_source[source] = revenue_by_source.get(source, 0) + float(transaction.net_amount)
            
            # Générer des insights IA
            ai_insights = self._generate_ai_insights(transactions, revenue_by_source)
            
            analytics_data = {
                "creator_id": creator_id,
                "analysis_period": period,
                "period_start_date": start_date,
                "period_end_date": end_date,
                "total_revenue": total_revenue,
                "total_transactions": total_transactions,
                "average_transaction_value": avg_transaction,
                "revenue_by_source": revenue_by_source,
                "ai_insights": ai_insights
            }
            
            analytics = RevenueAnalytics(**analytics_data)
            self.db.add(analytics)
            self.db.commit()
            self.db.refresh(analytics)
            
            logger.info(f"Analytics générées: {analytics.analytics_uuid}")
            return analytics
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur génération analytics: {str(e)}")
            raise

    def request_payout(self, creator_id: str, payout_data: Dict[str, Any]) -> PayoutRequest:
        """Créer une demande de paiement."""
        try:
            # Vérifier le solde disponible
            available_balance = self._calculate_available_balance(creator_id)
            
            if payout_data['requested_amount'] > available_balance:
                raise ValueError("Montant demandé supérieur au solde disponible")
            
            payout_data['available_balance'] = available_balance
            payout_data['creator_id'] = creator_id
            
            # Calculer les frais et le montant net
            processing_fee = self._calculate_processing_fee(
                payout_data['requested_amount'], 
                payout_data['payout_method']
            )
            payout_data['processing_fee'] = processing_fee
            payout_data['net_payout_amount'] = payout_data['requested_amount'] - processing_fee
            
            payout = PayoutRequest(**payout_data)
            self.db.add(payout)
            self.db.commit()
            self.db.refresh(payout)
            
            logger.info(f"Demande de paiement créée: {payout.payout_uuid}")
            return payout
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur demande paiement: {str(e)}")
            raise

    def get_monetization_opportunities(self, creator_id: str) -> Dict[str, Any]:
        """Identifier des opportunités de monétisation via IA."""
        try:
            # Analyser l'historique de revenus
            revenue_data = self._get_historical_revenue_data(creator_id, 6)
            
            # Analyser les sources de revenus actuelles
            current_sources = set()
            for month_data in revenue_data:
                current_sources.update(month_data.get('sources', []))
            
            # Identifier les sources manquantes
            all_sources = set([source.value for source in RevenueSource])
            missing_sources = all_sources - current_sources
            
            # Générer des recommandations spécifiques
            recommendations = []
            for source in missing_sources:
                recommendation = self._generate_source_recommendation(source, revenue_data)
                if recommendation:
                    recommendations.append(recommendation)
            
            # Analyser les tendances de performance
            performance_trends = self._analyze_performance_trends(revenue_data)
            
            return {
                "current_sources": list(current_sources),
                "missing_opportunities": list(missing_sources),
                "recommendations": recommendations,
                "performance_trends": performance_trends,
                "optimization_score": self._calculate_optimization_score(current_sources, revenue_data)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse opportunités: {str(e)}")
            return {}

    def _get_historical_revenue_data(self, creator_id: str, months: int) -> List[Dict[str, Any]]:
        """Récupérer les données historiques de revenus."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=months * 30)
            
            transactions = self.db.query(RevenueTransaction).filter(
                RevenueTransaction.creator_id == creator_id,
                RevenueTransaction.earned_date >= start_date
            ).all()
            
            # Grouper par mois
            monthly_data = {}
            for transaction in transactions:
                month_key = transaction.earned_date.strftime("%Y-%m")
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        "total": 0,
                        "sources": set(),
                        "transactions": 0
                    }
                
                monthly_data[month_key]["total"] += float(transaction.net_amount)
                monthly_data[month_key]["sources"].add(transaction.revenue_source.value)
                monthly_data[month_key]["transactions"] += 1
            
            # Convertir en liste triée
            historical_data = []
            for month, data in sorted(monthly_data.items()):
                data["sources"] = list(data["sources"])
                data["month"] = month
                historical_data.append(data)
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Erreur données historiques: {str(e)}")
            return []

    def _calculate_projections(self, historical_data: List[Dict[str, Any]], 
                             projection_params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculer les projections basées sur les données historiques."""
        if not historical_data:
            return {"total_projection": 0, "confidence_score": 0}
        
        # Calcul de tendance simple
        revenues = [month["total"] for month in historical_data]
        if len(revenues) >= 2:
            trend = (revenues[-1] - revenues[0]) / len(revenues)
            projection = revenues[-1] + trend
        else:
            projection = revenues[-1] if revenues else 0
        
        return {
            "total_projection": max(0, projection),
            "confidence_score": min(0.8, len(revenues) / 12)  # Plus de données = plus de confiance
        }

    def _generate_ai_insights(self, transactions: List[RevenueTransaction], 
                            revenue_by_source: Dict[str, float]) -> List[str]:
        """Générer des insights IA basés sur les données."""
        insights = []
        
        if not transactions:
            return ["Aucune transaction dans la période analysée."]
        
        # Analyser la diversification
        source_count = len(revenue_by_source)
        if source_count == 1:
            insights.append("Revenus concentrés sur une seule source - considérez la diversification.")
        elif source_count >= 5:
            insights.append("Excellente diversification des sources de revenus.")
        
        # Analyser la source principale
        if revenue_by_source:
            top_source = max(revenue_by_source, key=revenue_by_source.get)
            top_percentage = (revenue_by_source[top_source] / sum(revenue_by_source.values())) * 100
            
            if top_percentage > 70:
                insights.append(f"Dépendance élevée ({top_percentage:.1f}%) sur {top_source}.")
            
            insights.append(f"Source principale: {top_source} ({top_percentage:.1f}% des revenus).")
        
        return insights

    def _calculate_available_balance(self, creator_id: str) -> PyDecimal:
        """Calculer le solde disponible pour paiement."""
        try:
            # Revenus complétés non encore payés
            completed_revenue = self.db.query(RevenueTransaction).filter(
                RevenueTransaction.creator_id == creator_id,
                RevenueTransaction.payment_status == PaymentStatus.COMPLETED
            ).all()
            
            total_earned = sum(t.net_amount for t in completed_revenue)
            
            # Paiements déjà effectués
            paid_out = self.db.query(PayoutRequest).filter(
                PayoutRequest.creator_id == creator_id,
                PayoutRequest.status == PaymentStatus.COMPLETED
            ).all()
            
            total_paid = sum(p.net_payout_amount for p in paid_out)
            
            return total_earned - total_paid
            
        except Exception as e:
            logger.error(f"Erreur calcul solde: {str(e)}")
            return PyDecimal('0')

    def _calculate_processing_fee(self, amount: PyDecimal, method: str) -> PyDecimal:
        """Calculer les frais de traitement."""
        fee_rates = {
            "bank_transfer": PyDecimal('0.02'),  # 2%
            "paypal": PyDecimal('0.035'),  # 3.5%
            "stripe": PyDecimal('0.029'),  # 2.9%
            "crypto": PyDecimal('0.01')  # 1%
        }
        
        rate = fee_rates.get(method, PyDecimal('0.03'))
        return amount * rate

    def _generate_source_recommendation(self, source: str, revenue_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Générer une recommandation pour une source de revenus."""
        recommendations = {
            "licensing_fees": {
                "title": "Monétisez via les licences",
                "description": "Proposez vos contenus pour des licences commerciales.",
                "potential_revenue": "Moyen-Élevé",
                "difficulty": "Moyen"
            },
            "merchandise": {
                "title": "Lancez des produits dérivés",
                "description": "Créez et vendez des produits à votre image.",
                "potential_revenue": "Moyen",
                "difficulty": "Moyen"
            },
            "brand_partnerships": {
                "title": "Partenariats de marque",
                "description": "Collaborez avec des marques alignées à vos valeurs.",
                "potential_revenue": "Élevé",
                "difficulty": "Élevé"
            }
        }
        
        return recommendations.get(source)

    def _analyze_performance_trends(self, revenue_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyser les tendances de performance."""
        if len(revenue_data) < 2:
            return {"trend": "insufficient_data"}
        
        revenues = [month["total"] for month in revenue_data]
        
        # Calcul de tendance simple
        recent_avg = sum(revenues[-3:]) / min(3, len(revenues))
        older_avg = sum(revenues[:-3]) / max(1, len(revenues) - 3)
        
        if recent_avg > older_avg * 1.1:
            trend = "growing"
        elif recent_avg < older_avg * 0.9:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "recent_average": recent_avg,
            "growth_rate": ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        }

    def _calculate_optimization_score(self, current_sources: set, revenue_data: List[Dict[str, Any]]) -> float:
        """Calculer un score d'optimisation de la monétisation."""
        # Score basé sur la diversification et la croissance
        diversification_score = min(len(current_sources) / 8, 1.0) * 0.6  # Max 8 sources principales
        
        growth_score = 0
        if len(revenue_data) >= 2:
            revenues = [month["total"] for month in revenue_data]
            if revenues[-1] > revenues[0]:
                growth_score = 0.4
        
        return (diversification_score + growth_score) * 100
