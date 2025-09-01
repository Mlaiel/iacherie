"""Revenue Records Database Models

Gestion des enregistrements de revenus avec tracking complet
des transactions financières pour la plateforme IA Influencer Agent.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer & Financial Systems Architect
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import logging
from dataclasses import dataclass
from sqlalchemy import Column, String, Numeric, DateTime, Integer, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from ..models.base import BaseModel, TimestampMixin
from ...core.database import DatabaseManager
from ...core.security import EncryptionService
from ...utils.financial import CurrencyConverter, TaxCalculator

logger = logging.getLogger(__name__)

Base = declarative_base()


class TransactionStatus(Enum):
    """Status des transactions de revenus"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSED = "processed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class TransactionType(Enum):
    """Types de transactions financières"""
    PLATFORM_REVENUE = "platform_revenue"
    COMMISSION = "commission"
    ROYALTY = "royalty"
    LICENSING_FEE = "licensing_fee"
    SUBSCRIPTION = "subscription"
    ADVERTISEMENT = "advertisement"
    MERCHANDISE = "merchandise"
    DONATION = "donation"
    COLLABORATION_FEE = "collaboration_fee"


class RevenueSource(Enum):
    """Sources de revenus par plateforme"""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    TWITCH = "twitch"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    CUSTOM_PLATFORM = "custom_platform"


@dataclass
class RevenueRecord(BaseModel, TimestampMixin):
    """
    Modèle principal pour les enregistrements de revenus
    """
    __tablename__ = "revenue_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey("content.id"), nullable=True, index=True)
    
    # Détails de la transaction
    transaction_id = Column(String(255), unique=True, nullable=False, index=True)
    external_transaction_id = Column(String(500), nullable=True, index=True)
    
    # Informations financières
    amount_gross = Column(Numeric(15, 4), nullable=False)
    amount_net = Column(Numeric(15, 4), nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")
    
    # Métadonnées de la transaction
    transaction_type = Column(String(50), nullable=False)
    revenue_source = Column(String(50), nullable=False)
    transaction_status = Column(String(20), nullable=False, default="pending")
    
    # Détails de la plateforme
    platform_name = Column(String(100), nullable=False)
    platform_transaction_id = Column(String(500), nullable=True)
    platform_fee_percentage = Column(Numeric(5, 4), nullable=True)
    platform_fee_amount = Column(Numeric(15, 4), nullable=True)
    
    # Calculs de commission
    commission_percentage = Column(Numeric(5, 4), nullable=False, default=Decimal("0.15"))
    commission_amount = Column(Numeric(15, 4), nullable=False)
    creator_payout = Column(Numeric(15, 4), nullable=False)
    
    # Métadonnées additionnelles
    metadata = Column(JSONB, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Tracking temporel
    transaction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    processed_date = Column(DateTime, nullable=True)
    settlement_date = Column(DateTime, nullable=True)
    
    # Relations
    user = relationship("User", back_populates="revenue_records")
    content = relationship("Content", back_populates="revenue_records")
    tax_records = relationship("TaxRecord", back_populates="revenue_record")
    audit_logs = relationship("RevenueAuditLog", back_populates="revenue_record")

    def __init__(self, **kwargs):
        """Initialisation avec calculs automatiques"""
        super().__init__(**kwargs)
        self.transaction_id = self.transaction_id or self._generate_transaction_id()
        self._calculate_commission_and_payout()

    def _generate_transaction_id(self) -> str:
        """Génère un ID unique pour la transaction"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"REV_{timestamp}_{unique_id}"

    def _calculate_commission_and_payout(self):
        """Calcule automatiquement les commissions et le payout créateur"""
        if self.amount_net and self.commission_percentage:
            self.commission_amount = self.amount_net * (self.commission_percentage / 100)
            self.creator_payout = self.amount_net - self.commission_amount


class RevenueRecordManager:
    """
    Manager pour la gestion des enregistrements de revenus
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.encryption = EncryptionService()
        self.currency_converter = CurrencyConverter()
        self.tax_calculator = TaxCalculator()
        self.logger = logging.getLogger(__name__)

    async def create_revenue_record(
        self,
        user_id: uuid.UUID,
        amount_gross: Decimal,
        currency: str,
        transaction_type: TransactionType,
        revenue_source: RevenueSource,
        platform_name: str,
        content_id: Optional[uuid.UUID] = None,
        external_transaction_id: Optional[str] = None,
        platform_fee_percentage: Optional[Decimal] = None,
        commission_percentage: Optional[Decimal] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RevenueRecord:
        """
        Crée un nouvel enregistrement de revenus
        
        Args:
            user_id: ID utilisateur
            amount_gross: Montant brut
            currency: Devise
            transaction_type: Type de transaction
            revenue_source: Source de revenus
            platform_name: Nom de la plateforme
            content_id: ID du contenu (optionnel)
            external_transaction_id: ID transaction externe
            platform_fee_percentage: Pourcentage de frais plateforme
            commission_percentage: Pourcentage de commission personnalisé
            metadata: Métadonnées additionnelles
            
        Returns:
            RevenueRecord: Enregistrement créé
        """
        try:
            # Calcul du montant net après frais plateforme
            platform_fee = Decimal("0")
            if platform_fee_percentage:
                platform_fee = amount_gross * (platform_fee_percentage / 100)
            
            amount_net = amount_gross - platform_fee
            
            # Commission par défaut si non spécifiée
            if not commission_percentage:
                commission_percentage = await self._get_default_commission_rate(
                    user_id, revenue_source
                )
            
            # Création de l'enregistrement
            record = RevenueRecord(
                user_id=user_id,
                content_id=content_id,
                external_transaction_id=external_transaction_id,
                amount_gross=amount_gross,
                amount_net=amount_net,
                currency=currency,
                transaction_type=transaction_type.value,
                revenue_source=revenue_source.value,
                platform_name=platform_name,
                platform_fee_percentage=platform_fee_percentage,
                platform_fee_amount=platform_fee,
                commission_percentage=commission_percentage,
                metadata=metadata or {}
            )
            
            # Sauvegarde en base
            async with self.db.get_session() as session:
                session.add(record)
                await session.commit()
                await session.refresh(record)
            
            # Log de création
            await self._log_revenue_action(
                record.id, "created", f"Revenue record created for user {user_id}"
            )
            
            self.logger.info(
                f"Revenue record created: {record.transaction_id} "
                f"for user {user_id}, amount: {amount_gross} {currency}"
            )
            
            return record
            
        except Exception as e:
            self.logger.error(f"Error creating revenue record: {str(e)}")
            raise

    async def update_transaction_status(
        self,
        transaction_id: str,
        new_status: TransactionStatus,
        notes: Optional[str] = None
    ) -> RevenueRecord:
        """
        Met à jour le statut d'une transaction
        
        Args:
            transaction_id: ID de la transaction
            new_status: Nouveau statut
            notes: Notes additionnelles
            
        Returns:
            RevenueRecord: Enregistrement mis à jour
        """
        try:
            async with self.db.get_session() as session:
                record = await session.query(RevenueRecord).filter(
                    RevenueRecord.transaction_id == transaction_id
                ).first()
                
                if not record:
                    raise ValueError(f"Transaction not found: {transaction_id}")
                
                old_status = record.transaction_status
                record.transaction_status = new_status.value
                
                if notes:
                    record.notes = notes
                
                # Mise à jour des dates selon le statut
                if new_status == TransactionStatus.PROCESSED:
                    record.processed_date = datetime.utcnow()
                elif new_status == TransactionStatus.CONFIRMED:
                    record.settlement_date = datetime.utcnow()
                
                await session.commit()
                await session.refresh(record)
            
            # Log de changement de statut
            await self._log_revenue_action(
                record.id,
                "status_updated",
                f"Status changed from {old_status} to {new_status.value}"
            )
            
            return record
            
        except Exception as e:
            self.logger.error(f"Error updating transaction status: {str(e)}")
            raise

    async def get_user_revenue_summary(
        self,
        user_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        currency: str = "EUR"
    ) -> Dict[str, Any]:
        """
        Récupère un résumé des revenus pour un utilisateur
        
        Args:
            user_id: ID utilisateur
            start_date: Date de début
            end_date: Date de fin
            currency: Devise pour la conversion
            
        Returns:
            Dict: Résumé des revenus
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            async with self.db.get_session() as session:
                # Requête des revenus dans la période
                query = session.query(RevenueRecord).filter(
                    RevenueRecord.user_id == user_id,
                    RevenueRecord.transaction_date >= start_date,
                    RevenueRecord.transaction_date <= end_date,
                    RevenueRecord.transaction_status.in_([
                        TransactionStatus.CONFIRMED.value,
                        TransactionStatus.PROCESSED.value
                    ])
                )
                
                records = await query.all()
            
            # Calculs du résumé
            total_gross = Decimal("0")
            total_net = Decimal("0")
            total_commission = Decimal("0")
            total_payout = Decimal("0")
            
            platform_breakdown = {}
            transaction_count = len(records)
            
            for record in records:
                # Conversion de devise si nécessaire
                if record.currency != currency:
                    rate = await self.currency_converter.get_rate(
                        record.currency, currency
                    )
                    gross = record.amount_gross * rate
                    net = record.amount_net * rate
                    commission = record.commission_amount * rate
                    payout = record.creator_payout * rate
                else:
                    gross = record.amount_gross
                    net = record.amount_net
                    commission = record.commission_amount
                    payout = record.creator_payout
                
                total_gross += gross
                total_net += net
                total_commission += commission
                total_payout += payout
                
                # Breakdown par plateforme
                platform = record.platform_name
                if platform not in platform_breakdown:
                    platform_breakdown[platform] = {
                        "count": 0,
                        "total_gross": Decimal("0"),
                        "total_payout": Decimal("0")
                    }
                
                platform_breakdown[platform]["count"] += 1
                platform_breakdown[platform]["total_gross"] += gross
                platform_breakdown[platform]["total_payout"] += payout
            
            return {
                "user_id": str(user_id),
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "currency": currency,
                "summary": {
                    "transaction_count": transaction_count,
                    "total_gross": float(total_gross),
                    "total_net": float(total_net),
                    "total_commission": float(total_commission),
                    "total_payout": float(total_payout),
                    "average_transaction": float(total_gross / transaction_count) if transaction_count > 0 else 0
                },
                "platform_breakdown": {
                    platform: {
                        "count": data["count"],
                        "total_gross": float(data["total_gross"]),
                        "total_payout": float(data["total_payout"]),
                        "percentage": float((data["total_gross"] / total_gross) * 100) if total_gross > 0 else 0
                    }
                    for platform, data in platform_breakdown.items()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user revenue summary: {str(e)}")
            raise

    async def process_bulk_transactions(
        self,
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Traite plusieurs transactions en lot
        
        Args:
            transactions: Liste des transactions à traiter
            
        Returns:
            Dict: Résultats du traitement en lot
        """
        try:
            results = {
                "success_count": 0,
                "error_count": 0,
                "errors": [],
                "processed_transactions": []
            }
            
            async with self.db.get_session() as session:
                for i, transaction_data in enumerate(transactions):
                    try:
                        # Validation des données
                        required_fields = [
                            "user_id", "amount_gross", "currency",
                            "transaction_type", "revenue_source", "platform_name"
                        ]
                        
                        for field in required_fields:
                            if field not in transaction_data:
                                raise ValueError(f"Missing required field: {field}")
                        
                        # Création de l'enregistrement
                        record = await self.create_revenue_record(**transaction_data)
                        
                        results["success_count"] += 1
                        results["processed_transactions"].append({
                            "index": i,
                            "transaction_id": record.transaction_id,
                            "status": "success"
                        })
                        
                    except Exception as e:
                        results["error_count"] += 1
                        results["errors"].append({
                            "index": i,
                            "error": str(e),
                            "transaction_data": transaction_data
                        })
                        self.logger.error(f"Error processing transaction {i}: {str(e)}")
            
            self.logger.info(
                f"Bulk transaction processing completed: "
                f"{results['success_count']} success, {results['error_count']} errors"
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in bulk transaction processing: {str(e)}")
            raise

    async def _get_default_commission_rate(
        self,
        user_id: uuid.UUID,
        revenue_source: RevenueSource
    ) -> Decimal:
        """Récupère le taux de commission par défaut pour un utilisateur"""
        # Cette logique pourrait être configurée par utilisateur/plan
        default_rates = {
            RevenueSource.SPOTIFY: Decimal("15.0"),
            RevenueSource.YOUTUBE: Decimal("20.0"),
            RevenueSource.TIKTOK: Decimal("18.0"),
            RevenueSource.INSTAGRAM: Decimal("17.0"),
            RevenueSource.SOUNDCLOUD: Decimal("16.0")
        }
        
        return default_rates.get(revenue_source, Decimal("15.0"))

    async def _log_revenue_action(
        self,
        revenue_record_id: uuid.UUID,
        action: str,
        description: str
    ):
        """Log les actions sur les enregistrements de revenus"""
        # Cette méthode sera implémentée avec le système d'audit
        pass


# Export des classes principales
__all__ = [
    "RevenueRecord",
    "RevenueRecordManager", 
    "TransactionStatus",
    "TransactionType",
    "RevenueSource"
]
