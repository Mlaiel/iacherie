"""SQLAlchemy model for Campaigns (Pétitions & Fundraising)"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean,
    DateTime, ARRAY, JSON, Index, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
import enum

from models.base import Base


class CampaignType(str, enum.Enum):
    """Types de campagnes"""
    PETITION = "petition"  # Pétition
    FUNDRAISING = "fundraising"  # Collecte de fonds


class CampaignStatus(str, enum.Enum):
    """Statut de la campagne"""
    DRAFT = "draft"  # Brouillon
    ACTIVE = "active"  # Active
    SUCCESSFUL = "successful"  # Objectif atteint
    CLOSED = "closed"  # Terminée
    CANCELLED = "cancelled"  # Annulée


class Campaign(Base):
    """Campaign (Pétition ou Fundraising) model"""
    
    __tablename__ = 'ia2good_campaigns'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Type et statut
    type = Column(SQLEnum(CampaignType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    status = Column(SQLEnum(CampaignStatus, values_callable=lambda x: [e.value for e in x]), default=CampaignStatus.DRAFT)
    
    # Contenu
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    story = Column(Text)  # Histoire détaillée, contexte
    objectives = Column(Text)  # Objectifs à atteindre
    tags = Column(ARRAY(String(50)), default=[])
    
    # Créateur
    creator_id = Column(UUID(as_uuid=True), nullable=False)  # Foreign key to users
    creator_type = Column(String(50))  # 'individual', 'organization', 'volunteer'
    organization_name = Column(String(200))  # Si créé par une org
    
    # Objectif
    # Pour PETITION: nombre de signatures
    # Pour FUNDRAISING: montant en euros
    goal = Column(Float, nullable=False)
    current_amount = Column(Float, default=0)  # Signatures ou euros actuels
    
    # Dates
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)  # Date limite (optionnelle)
    
    # Médias
    cover_image = Column(String(500))
    images = Column(ARRAY(String(500)), default=[])
    videos = Column(ARRAY(String(500)), default=[])
    
    # Pour FUNDRAISING uniquement
    beneficiary_name = Column(String(200))  # Bénéficiaire
    beneficiary_details = Column(Text)
    funds_usage_plan = Column(Text)  # Plan d'utilisation des fonds
    transparency_reports = Column(JSON, default=[])  # Rapports de transparence
    
    # Pour PETITION uniquement
    target_authority = Column(String(200))  # Autorité visée (ministre, maire, etc.)
    target_email = Column(String(255))  # Email pour envoyer la pétition
    petition_text = Column(Text)  # Texte officiel de la pétition
    
    # Engagement
    supporters_count = Column(Integer, default=0)  # Total supporters (signateurs ou donateurs)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    
    # Métadonnées
    extra_metadata = Column(JSON, default={})
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)  # Vérifié par modérateur
    
    # Résultats
    success_story = Column(Text)  # Histoire de succès après atteinte de l'objectif
    impact_achieved = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('idx_ia2good_campaigns_type', 'type'),
        Index('idx_ia2good_campaigns_status', 'status'),
        Index('idx_ia2good_campaigns_creator_id', 'creator_id'),
        Index('idx_ia2good_campaigns_tags', 'tags', postgresql_using='gin'),
    )
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, type='{self.type}', title='{self.title}')>"


class Signature(Base):
    """Signatures de pétitions"""
    
    __tablename__ = 'ia2good_signatures'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True))  # Peut être null si signature anonyme
    
    # Informations du signataire
    full_name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False)
    city = Column(String(100))
    country = Column(String(50))
    
    # Message optionnel
    message = Column(Text)  # Message de soutien
    
    # Visibilité
    is_public = Column(Boolean, default=True)  # Signature visible publiquement
    is_anonymous = Column(Boolean, default=False)  # Nom caché
    
    # Validation
    is_verified = Column(Boolean, default=False)  # Email vérifié
    verification_token = Column(String(100))
    verified_at = Column(DateTime)
    
    # IP pour détecter fraude
    ip_address = Column(String(45))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_ia2good_signatures_campaign_id', 'campaign_id'),
        Index('idx_ia2good_signatures_user_id', 'user_id'),
        Index('idx_ia2good_signatures_email', 'email'),
    )
    
    def __repr__(self):
        return f"<Signature(id={self.id}, campaign_id={self.campaign_id})>"


class Donation(Base):
    """Donations pour fundraising"""
    
    __tablename__ = 'ia2good_donations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True))  # Peut être null si don anonyme
    
    # Montant
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default='EUR')
    
    # Informations du donateur
    donor_name = Column(String(200))
    donor_email = Column(String(255))
    
    # Message
    message = Column(Text)  # Message de soutien
    
    # Visibilité
    is_public = Column(Boolean, default=True)
    is_anonymous = Column(Boolean, default=False)
    
    # Paiement (placeholder - à implémenter plus tard)
    payment_method = Column(String(50))  # 'stripe', 'paypal', 'bank_transfer'
    payment_status = Column(String(20), default='pending')  # pending, completed, failed, refunded
    payment_id = Column(String(200))  # ID transaction externe
    payment_metadata = Column(JSON, default={})
    
    # Reçu fiscal
    tax_receipt_requested = Column(Boolean, default=False)
    tax_receipt_sent = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    __table_args__ = (
        Index('idx_ia2good_donations_campaign_id', 'campaign_id'),
        Index('idx_ia2good_donations_user_id', 'user_id'),
        Index('idx_ia2good_donations_payment_status', 'payment_status'),
    )
    
    def __repr__(self):
        return f"<Donation(id={self.id}, campaign_id={self.campaign_id}, amount={self.amount})>"


class CampaignUpdate(Base):
    """Mises à jour de campagnes"""
    
    __tablename__ = 'ia2good_campaign_updates'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id = Column(UUID(as_uuid=True), nullable=False)
    author_id = Column(UUID(as_uuid=True), nullable=False)
    
    title = Column(String(200))
    content = Column(Text, nullable=False)
    media_urls = Column(ARRAY(String(500)), default=[])
    
    # Type d'update
    update_type = Column(String(50), default='general')  # general, milestone, transparency, thank_you
    
    # Pour les rapports de transparence (fundraising)
    funds_used = Column(Float)  # Montant utilisé
    funds_usage_details = Column(Text)
    receipts = Column(ARRAY(String(500)), default=[])  # Reçus/preuves
    
    # Notifications
    notify_supporters = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_ia2good_campaign_updates_campaign_id', 'campaign_id'),
    )
    
    def __repr__(self):
        return f"<CampaignUpdate(id={self.id}, campaign_id={self.campaign_id})>"
