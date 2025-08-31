"""
Rights Tracking Data Models - Enterprise Database Schema
Modèles de données avancés pour la gestion des droits d'auteur
Système professionnel avec validation, sécurité et performance optimisées
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from decimal import Decimal
import hashlib
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, JSON, 
    DECIMAL, ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

Base = declarative_base()


class ContentType(Enum):
    """Types de contenu supportés"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    SOFTWARE = "software"
    MULTIMEDIA = "multimedia"
    LIVESTREAM = "livestream"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    EBOOK = "ebook"


class RightScope(Enum):
    """Portée des droits"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SOLE = "sole"
    CO_EXCLUSIVE = "co_exclusive"


class LicenseScope(Enum):
    """Portée des licences"""
    COMMERCIAL = "commercial"
    NON_COMMERCIAL = "non_commercial"
    EDUCATIONAL = "educational"
    RESEARCH = "research"
    PERSONAL = "personal"
    BROADCAST = "broadcast"


class RevenueSplitType(Enum):
    """Types de partage de revenus"""
    EQUAL = "equal"
    PROPORTIONAL = "proportional"
    CUSTOM = "custom"
    PERFORMANCE_BASED = "performance_based"
    TIERED = "tiered"


# =============================================================================
# TABLES PRINCIPALES
# =============================================================================

class ContentMetadata(Base):
    """Métadonnées complètes du contenu"""
    __tablename__ = 'content_metadata'
    
    # Clé primaire
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Informations de base
    title = Column(String(500), nullable=False)
    content_type = Column(String(50), nullable=False)
    original_filename = Column(String(500))
    file_size = Column(Integer)  # En bytes
    duration = Column(Integer)  # En secondes
    
    # Hashes et fingerprints
    md5_hash = Column(String(32), index=True)
    sha256_hash = Column(String(64), index=True)
    content_fingerprint = Column(Text)  # JSON des empreintes
    
    # Métadonnées créatives
    genre = Column(String(100))
    language = Column(String(10))
    tags = Column(JSON)  # Liste de tags
    description = Column(Text)
    
    # Métadonnées techniques
    quality_metadata = Column(JSON)  # Résolution, bitrate, etc.
    encoding_info = Column(JSON)
    technical_specs = Column(JSON)
    
    # Géolocalisation et contexte
    creation_location = Column(String(200))
    recording_details = Column(JSON)
    equipment_used = Column(JSON)
    
    # Versioning
    version_number = Column(String(20), default="1.0")
    parent_content_id = Column(String(100), index=True)  # Pour les dérivés
    is_derivative = Column(Boolean, default=False)
    derivative_type = Column(String(50))  # remix, cover, sample, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    rights_records = relationship("RightsRecord", back_populates="content_metadata")
    usage_events = relationship("UsageEvent", back_populates="content_metadata")
    
    # Index composés pour performance
    __table_args__ = (
        Index('idx_content_type_created', 'content_type', 'created_at'),
        Index('idx_title_search', 'title'),
        Index('idx_hash_lookup', 'md5_hash', 'sha256_hash'),
    )


class RightsHolder(Base):
    """Détenteurs de droits avec informations complètes"""
    __tablename__ = 'rights_holders'
    
    # Clé primaire
    id = Column(Integer, primary_key=True, autoincrement=True)
    holder_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Informations personnelles/entreprise
    holder_type = Column(String(20), nullable=False)  # individual, company, organization
    legal_name = Column(String(200), nullable=False)
    display_name = Column(String(200))
    artist_name = Column(String(200))  # Pour les artistes
    
    # Contact
    email = Column(String(200), nullable=False, index=True)
    phone = Column(String(50))
    website = Column(String(300))
    social_media = Column(JSON)  # Liens réseaux sociaux
    
    # Adresse
    address_line1 = Column(String(300))
    address_line2 = Column(String(300))
    city = Column(String(100))
    state_province = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(3))  # Code ISO
    
    # Informations légales
    tax_id = Column(String(50))
    vat_number = Column(String(50))
    business_registration = Column(String(100))
    legal_representative = Column(String(200))
    
    # Organisations de droits
    performing_rights_org = Column(String(100))  # SACEM, ASCAP, etc.
    mechanical_rights_org = Column(String(100))
    pro_membership_number = Column(String(50))
    
    # Informations bancaires (chiffrées)
    bank_details = Column(JSON)  # Détails bancaires sécurisés
    payment_preferences = Column(JSON)
    preferred_currency = Column(String(3), default='EUR')
    
    # Vérification et compliance
    identity_verified = Column(Boolean, default=False)
    kyc_status = Column(String(20), default='pending')  # pending, verified, rejected
    kyc_documents = Column(JSON)
    last_verification_date = Column(DateTime)
    
    # Profil créatif
    biography = Column(Text)
    genres = Column(JSON)  # Liste des genres musicaux
    instruments = Column(JSON)  # Instruments joués
    roles = Column(JSON)  # Compositeur, interprète, producteur, etc.
    
    # Statistiques
    total_content_count = Column(Integer, default=0)
    total_earnings = Column(DECIMAL(15, 2), default=0)
    join_date = Column(DateTime, default=datetime.utcnow)
    
    # Statut
    account_status = Column(String(20), default='active')  # active, suspended, closed
    subscription_tier = Column(String(20), default='basic')
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relations
    rights_records = relationship("RightsRecord", back_populates="primary_holder_rel")
    license_agreements = relationship("LicenseAgreement", back_populates="licensor_rel")
    
    # Contraintes
    __table_args__ = (
        Index('idx_holder_email', 'email'),
        Index('idx_holder_country', 'country'),
        Index('idx_holder_status', 'account_status'),
        CheckConstraint('holder_type IN ("individual", "company", "organization")'),
    )


class RightsRecord(Base):
    """Enregistrement complet des droits d'auteur"""
    __tablename__ = 'rights_records'
    
    # Clé primaire
    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(String(100), unique=True, nullable=False, index=True)
    content_id = Column(String(100), ForeignKey('content_metadata.content_id'), nullable=False)
    
    # Détenteur principal
    primary_holder_id = Column(String(100), ForeignKey('rights_holders.holder_id'), nullable=False)
    
    # Informations de base
    title = Column(String(500), nullable=False)
    content_type = Column(String(50), nullable=False)
    creation_date = Column(DateTime, nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    
    # Droits et portée
    rights_granted = Column(JSON, nullable=False)  # Liste des droits
    rights_scope = Column(String(20), default='non_exclusive')
    territories = Column(JSON, default=['worldwide'])
    
    # Durée et validité
    effective_date = Column(DateTime, default=datetime.utcnow)
    expiration_date = Column(DateTime)
    renewable = Column(Boolean, default=True)
    auto_renewal = Column(Boolean, default=False)
    
    # Enregistrement officiel
    copyright_office = Column(String(100))
    registration_number = Column(String(100), index=True)
    certificate_number = Column(String(100))
    deposit_reference = Column(String(100))
    
    # Statut et vérification
    status = Column(String(20), default='active')
    verification_status = Column(String(20), default='pending')
    verification_evidence = Column(JSON)
    dispute_status = Column(String(20))  # none, pending, resolved
    
    # Informations créatives détaillées
    creators = Column(JSON)  # Liste détaillée des créateurs
    contributors = Column(JSON)  # Contributeurs (musiciens, etc.)
    producers = Column(JSON)  # Producteurs
    publishers = Column(JSON)  # Éditeurs
    
    # Métadonnées de création
    creation_process = Column(JSON)  # Processus de création
    source_materials = Column(JSON)  # Matériaux sources utilisés
    derivative_works = Column(JSON)  # Œuvres dérivées autorisées
    
    # Restrictions et conditions
    usage_restrictions = Column(JSON)
    platform_restrictions = Column(JSON)
    geographic_restrictions = Column(JSON)
    time_restrictions = Column(JSON)
    
    # Historique et audit
    ownership_history = Column(JSON)  # Historique des changements
    audit_trail = Column(JSON)  # Trail d'audit complet
    version_history = Column(JSON)  # Versions du record
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    content_metadata = relationship("ContentMetadata", back_populates="rights_records")
    primary_holder_rel = relationship("RightsHolder", back_populates="rights_records")
    co_holders = relationship("CoHolderAssociation", back_populates="rights_record")
    license_agreements = relationship("LicenseAgreement", back_populates="rights_record")
    
    # Index pour performance
    __table_args__ = (
        Index('idx_rights_content', 'content_id'),
        Index('idx_rights_holder', 'primary_holder_id'),
        Index('idx_rights_status', 'status'),
        Index('idx_rights_registration', 'registration_number'),
        Index('idx_rights_created', 'created_at'),
    )


class CoHolderAssociation(Base):
    """Association des co-détenteurs avec parts"""
    __tablename__ = 'co_holder_associations'
    
    # Clé primaire composée
    id = Column(Integer, primary_key=True, autoincrement=True)
    rights_record_id = Column(String(100), ForeignKey('rights_records.record_id'), nullable=False)
    holder_id = Column(String(100), ForeignKey('rights_holders.holder_id'), nullable=False)
    
    # Part et rôle
    ownership_percentage = Column(DECIMAL(5, 4), nullable=False)  # 0.0000 à 1.0000
    role = Column(String(50))  # composer, performer, producer, etc.
    contribution_type = Column(String(50))  # lyrics, music, performance, etc.
    
    # Conditions spéciales
    special_conditions = Column(JSON)
    revenue_split_override = Column(DECIMAL(5, 4))  # Peut différer de ownership
    
    # Validité
    effective_date = Column(DateTime, default=datetime.utcnow)
    termination_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    rights_record = relationship("RightsRecord", back_populates="co_holders")
    holder = relationship("RightsHolder")
    
    # Contraintes
    __table_args__ = (
        UniqueConstraint('rights_record_id', 'holder_id'),
        Index('idx_coholder_record', 'rights_record_id'),
        Index('idx_coholder_holder', 'holder_id'),
        CheckConstraint('ownership_percentage >= 0 AND ownership_percentage <= 1'),
    )


class LicenseAgreement(Base):
    """Accords de licence complets"""
    __tablename__ = 'license_agreements'
    
    # Clé primaire
    id = Column(Integer, primary_key=True, autoincrement=True)
    license_id = Column(String(100), unique=True, nullable=False, index=True)
    rights_record_id = Column(String(100), ForeignKey('rights_records.record_id'), nullable=False)
    
    # Parties
    licensor_id = Column(String(100), ForeignKey('rights_holders.holder_id'), nullable=False)
    licensee_id = Column(String(100), nullable=False)  # Peut être externe
    
    # Type et portée de licence
    license_type = Column(String(20), nullable=False)  # exclusive, non_exclusive, sole
    license_scope = Column(String(20), nullable=False)  # commercial, non_commercial, etc.
    licensed_rights = Column(JSON, nullable=False)
    territories = Column(JSON, nullable=False)
    
    # Durée et renouvellement
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    is_perpetual = Column(Boolean, default=False)
    auto_renewal = Column(Boolean, default=False)
    renewal_period_months = Column(Integer)
    notice_period_days = Column(Integer, default=30)
    
    # Conditions d'utilisation
    usage_limitations = Column(JSON)
    platform_restrictions = Column(JSON)
    volume_limitations = Column(JSON)
    quality_restrictions = Column(JSON)
    
    # Conditions financières
    royalty_structure = Column(JSON, nullable=False)
    minimum_guarantee = Column(DECIMAL(15, 2), default=0)
    advance_payment = Column(DECIMAL(15, 2), default=0)
    payment_schedule = Column(String(20), default='quarterly')
    currency = Column(String(3), default='EUR')
    
    # Reporting et audit
    reporting_frequency = Column(String(20), default='quarterly')
    reporting_requirements = Column(JSON)
    audit_rights = Column(Boolean, default=True)
    access_to_analytics = Column(Boolean, default=True)
    
    # Clauses spéciales
    attribution_requirements = Column(JSON)
    modification_rights = Column(JSON)
    sublicensing_allowed = Column(Boolean, default=False)
    termination_conditions = Column(JSON)
    
    # Statut et gestion
    status = Column(String(20), default='active')
    approval_status = Column(String(20), default='pending')
    signature_status = Column(JSON)  # Statut des signatures
    
    # Documents
    contract_document_url = Column(String(500))
    amendments = Column(JSON)  # Liste des amendements
    exhibits = Column(JSON)  # Pièces jointes
    
    # Tracking et performance
    performance_metrics = Column(JSON)
    compliance_status = Column(String(20), default='compliant')
    violation_count = Column(Integer, default=0)
    last_violation_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    signed_at = Column(DateTime)
    activated_at = Column(DateTime)
    terminated_at = Column(DateTime)
    
    # Relations
    rights_record = relationship("RightsRecord", back_populates="license_agreements")
    licensor_rel = relationship("RightsHolder", back_populates="license_agreements")
    usage_reports = relationship("UsageReport", back_populates="license_agreement")
    
    # Index pour performance
    __table_args__ = (
        Index('idx_license_record', 'rights_record_id'),
        Index('idx_license_licensor', 'licensor_id'),
        Index('idx_license_licensee', 'licensee_id'),
        Index('idx_license_status', 'status'),
        Index('idx_license_dates', 'start_date', 'end_date'),
    )


class UsageEvent(Base):
    """Événements d'utilisation détaillés"""
    __tablename__ = 'usage_events'
    
    # Clé primaire
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(100), unique=True, nullable=False, index=True)
    content_id = Column(String(100), ForeignKey('content_metadata.content_id'), nullable=False)
    
    # Plateforme et détection
    platform_id = Column(String(100), nullable=False, index=True)
    platform_name = Column(String(200))
    detected_url = Column(String(1000), nullable=False)
    detection_method = Column(String(50), nullable=False)
    confidence_score = Column(DECIMAL(3, 2), nullable=False)
    
    # Type d'utilisation
    usage_type = Column(String(50), nullable=False)
    usage_category = Column(String(50))  # stream, download, view, etc.
    commercial_use = Column(Boolean, default=False)
    
    # Métadonnées d'utilisation
    user_identifier = Column(String(200))
    user_type = Column(String(50))  # individual, business, broadcaster
    geographic_location = Column(String(100), index=True)
    device_info = Column(JSON)
    
    # Métriques
    view_count = Column(Integer, default=0)
    play_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    engagement_score = Column(DECIMAL(5, 2), default=0)
    
    # Données financières
    revenue_generated = Column(DECIMAL(15, 2), default=0)
    currency = Column(String(3), default='EUR')
    cpm_rate = Column(DECIMAL(10, 4))  # Cost per mille
    conversion_rate = Column(DECIMAL(5, 4))
    
    # Timing
    usage_started_at = Column(DateTime)
    usage_ended_at = Column(DateTime)
    peak_concurrent_users = Column(Integer)
    total_watch_time_seconds = Column(Integer)
    
    # Contexte et qualité
    content_quality = Column(String(20))  # SD, HD, 4K, etc.
    audio_quality = Column(String(20))  # MP3, FLAC, etc.
    context_tags = Column(JSON)  # Contexte d'utilisation
    
    # License et légal
    license_status = Column(String(20), default='unknown')
    license_agreement_id = Column(String(100), ForeignKey('license_agreements.license_id'))
    rights_cleared = Column(Boolean, default=False)
    violation_severity = Column(String(20))  # low, medium, high, critical
    
    # Processing et actions
    processing_status = Column(String(20), default='detected')
    action_taken = Column(String(50))
    takedown_requested = Column(Boolean, default=False)
    monetization_claimed = Column(Boolean, default=False)
    
    # Métadonnées techniques
    fingerprint_match_score = Column(DECIMAL(3, 2))
    detection_algorithm = Column(String(100))
    false_positive_probability = Column(DECIMAL(3, 2))
    manual_verification_required = Column(Boolean, default=False)
    
    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processed_at = Column(DateTime)
    verified_at = Column(DateTime)
    
    # Relations
    content_metadata = relationship("ContentMetadata", back_populates="usage_events")
    license_agreement = relationship("LicenseAgreement")
    
    # Index pour performance et recherche
    __table_args__ = (
        Index('idx_usage_content', 'content_id'),
        Index('idx_usage_platform', 'platform_id'),
        Index('idx_usage_detected', 'detected_at'),
        Index('idx_usage_location', 'geographic_location'),
        Index('idx_usage_status', 'processing_status'),
        Index('idx_usage_license_status', 'license_status'),
    )


class UsageReport(Base):
    """Rapports d'utilisation détaillés"""
    __tablename__ = 'usage_reports'
    
    # Clé primaire
    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String(100), unique=True, nullable=False, index=True)
    license_agreement_id = Column(String(100), ForeignKey('license_agreements.license_id'), nullable=False)
    
    # Période de reporting
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    report_type = Column(String(20), default='regular')  # regular, special, audit
    
    # Données d'utilisation agrégées
    total_usage_events = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_plays = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    
    # Données financières
    gross_revenue = Column(DECIMAL(15, 2), default=0)
    net_revenue = Column(DECIMAL(15, 2), default=0)
    royalties_due = Column(DECIMAL(15, 2), default=0)
    deductions = Column(DECIMAL(15, 2), default=0)
    currency = Column(String(3), default='EUR')
    
    # Breakdowns détaillés
    geographic_breakdown = Column(JSON)
    platform_breakdown = Column(JSON)
    device_breakdown = Column(JSON)
    time_breakdown = Column(JSON)
    
    # Métriques de performance
    engagement_metrics = Column(JSON)
    quality_metrics = Column(JSON)
    trend_analysis = Column(JSON)
    
    # Validation et statut
    submitted_by = Column(String(100))
    verification_status = Column(String(20), default='pending')
    verified_by = Column(String(100))
    dispute_status = Column(String(20))
    
    # Paiement
    payment_due_date = Column(DateTime)
    payment_status = Column(String(20), default='pending')
    payment_reference = Column(String(100))
    paid_at = Column(DateTime)
    
    # Documents
    supporting_documents = Column(JSON)
    audit_trail = Column(JSON)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    submitted_at = Column(DateTime)
    verified_at = Column(DateTime)
    
    # Relations
    license_agreement = relationship("LicenseAgreement", back_populates="usage_reports")
    
    # Index
    __table_args__ = (
        Index('idx_report_license', 'license_agreement_id'),
        Index('idx_report_period', 'period_start', 'period_end'),
        Index('idx_report_status', 'verification_status'),
        Index('idx_report_payment', 'payment_status'),
    )


class RoyaltyCalculation(Base):
    """Calculs de redevances détaillés"""
    __tablename__ = 'royalty_calculations'
    
    # Clé primaire
    id = Column(Integer, primary_key=True, autoincrement=True)
    calculation_id = Column(String(100), unique=True, nullable=False, index=True)
    usage_report_id = Column(String(100), ForeignKey('usage_reports.report_id'))
    
    # Données de base
    content_id = Column(String(100), nullable=False)
    license_agreement_id = Column(String(100))
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Inputs du calcul
    gross_revenue = Column(DECIMAL(15, 2), nullable=False)
    usage_count = Column(Integer, default=0)
    usage_data = Column(JSON)
    
    # Règles appliquées
    royalty_rules_applied = Column(JSON)
    calculation_method = Column(String(50), default='standard')
    base_rate = Column(DECIMAL(5, 4), nullable=False)
    
    # Calculs intermédiaires
    base_royalty = Column(DECIMAL(15, 2), default=0)
    performance_adjustments = Column(JSON)
    volume_bonuses = Column(DECIMAL(15, 2), default=0)
    tier_adjustments = Column(DECIMAL(15, 2), default=0)
    
    # Déductions
    platform_fees = Column(DECIMAL(15, 2), default=0)
    processing_fees = Column(DECIMAL(15, 2), default=0)
    tax_withholding = Column(DECIMAL(15, 2), default=0)
    other_deductions = Column(JSON)
    
    # Résultats finaux
    gross_royalty = Column(DECIMAL(15, 2), default=0)
    total_deductions = Column(DECIMAL(15, 2), default=0)
    net_royalty = Column(DECIMAL(15, 2), default=0)
    
    # Devises
    original_currency = Column(String(3), default='EUR')
    payout_currency = Column(String(3), default='EUR')
    exchange_rate = Column(DECIMAL(10, 6))
    
    # Répartition
    holder_distributions = Column(JSON)  # Répartition par détenteur
    
    # Validation et audit
    calculation_confidence = Column(DECIMAL(3, 2), default=1.0)
    verification_status = Column(String(20), default='pending')
    audit_trail = Column(JSON)
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    verified_at = Column(DateTime)
    
    # Relations
    usage_report = relationship("UsageReport")
    
    # Index
    __table_args__ = (
        Index('idx_royalty_content', 'content_id'),
        Index('idx_royalty_license', 'license_agreement_id'),
        Index('idx_royalty_period', 'period_start', 'period_end'),
        Index('idx_royalty_calculated', 'calculated_at'),
    )


class PaymentInstruction(Base):
    """Instructions de paiement"""
    __tablename__ = 'payment_instructions'
    
    # Clé primaire
    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(String(100), unique=True, nullable=False, index=True)
    royalty_calculation_id = Column(String(100), ForeignKey('royalty_calculations.calculation_id'))
    
    # Bénéficiaire
    payee_id = Column(String(100), nullable=False)
    payee_name = Column(String(200), nullable=False)
    payee_type = Column(String(20), default='individual')
    
    # Montants
    gross_amount = Column(DECIMAL(15, 2), nullable=False)
    deductions = Column(DECIMAL(15, 2), default=0)
    net_amount = Column(DECIMAL(15, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    
    # Méthode de paiement
    payment_method = Column(String(50), nullable=False)
    bank_details = Column(JSON)  # Détails bancaires sécurisés
    digital_wallet = Column(JSON)  # PayPal, Stripe, etc.
    cryptocurrency_address = Column(String(200))
    
    # Timing
    payment_due_date = Column(DateTime, nullable=False)
    payment_frequency = Column(String(20), default='monthly')
    
    # Statut et traitement
    status = Column(String(20), default='pending')
    processing_reference = Column(String(100))
    transaction_id = Column(String(100))
    failure_reason = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Frais
    processing_fee = Column(DECIMAL(10, 2), default=0)
    exchange_fee = Column(DECIMAL(10, 2), default=0)
    total_fees = Column(DECIMAL(10, 2), default=0)
    
    # Compliance
    tax_reporting_required = Column(Boolean, default=False)
    aml_check_status = Column(String(20), default='pending')
    compliance_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime)
    completed_at = Column(DateTime)
    failed_at = Column(DateTime)
    
    # Relations
    royalty_calculation = relationship("RoyaltyCalculation")
    
    # Index
    __table_args__ = (
        Index('idx_payment_payee', 'payee_id'),
        Index('idx_payment_status', 'status'),
        Index('idx_payment_due', 'payment_due_date'),
        Index('idx_payment_method', 'payment_method'),
    )


class TerritorialRights(Base):
    """Droits territoriaux détaillés"""
    __tablename__ = 'territorial_rights'
    
    # Clé primaire
    id = Column(Integer, primary_key=True, autoincrement=True)
    territorial_rights_id = Column(String(100), unique=True, nullable=False, index=True)
    rights_record_id = Column(String(100), ForeignKey('rights_records.record_id'), nullable=False)
    
    # Territoire
    territory_id = Column(String(10), nullable=False)
    territory_name = Column(String(200), nullable=False)
    territory_type = Column(String(20), nullable=False)  # country, region, worldwide
    
    # Droits accordés
    granted_rights = Column(JSON, nullable=False)
    excluded_rights = Column(JSON)
    conditional_rights = Column(JSON)
    
    # Validité
    effective_date = Column(DateTime, default=datetime.utcnow)
    expiration_date = Column(DateTime)
    renewable = Column(Boolean, default=True)
    
    # Restrictions
    usage_restrictions = Column(JSON)
    platform_exclusions = Column(JSON)
    audience_restrictions = Column(JSON)
    time_restrictions = Column(JSON)
    
    # Conditions financières
    territory_royalty_rates = Column(JSON)
    minimum_guarantees = Column(JSON)
    local_tax_obligations = Column(JSON)
    
    # Compliance locale
    local_registration_required = Column(Boolean, default=False)
    local_registration_status = Column(String(20))
    collecting_society_affiliation = Column(JSON)
    
    # Statut
    status = Column(String(20), default='active')
    approval_status = Column(String(20), default='pending')
    compliance_verified = Column(Boolean, default=False)
    
    # Timestamps
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_verified_at = Column(DateTime)
    
    # Relations
    rights_record = relationship("RightsRecord")
    
    # Index
    __table_args__ = (
        Index('idx_territorial_record', 'rights_record_id'),
        Index('idx_territorial_territory', 'territory_id'),
        Index('idx_territorial_status', 'status'),
    )


# =============================================================================
# PYDANTIC MODELS POUR L'API
# =============================================================================

class ContentMetadataSchema(BaseModel):
    """Schema Pydantic pour ContentMetadata"""
    content_id: str
    title: str
    content_type: ContentType
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[int] = None
    
    # Hashes
    md5_hash: Optional[str] = None
    sha256_hash: Optional[str] = None
    content_fingerprint: Optional[Dict[str, Any]] = None
    
    # Métadonnées créatives
    genre: Optional[str] = None
    language: Optional[str] = None
    tags: List[str] = []
    description: Optional[str] = None
    
    # Métadonnées techniques
    quality_metadata: Dict[str, Any] = {}
    encoding_info: Dict[str, Any] = {}
    technical_specs: Dict[str, Any] = {}
    
    # Géolocalisation
    creation_location: Optional[str] = None
    recording_details: Dict[str, Any] = {}
    equipment_used: Dict[str, Any] = {}
    
    # Versioning
    version_number: str = "1.0"
    parent_content_id: Optional[str] = None
    is_derivative: bool = False
    derivative_type: Optional[str] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True


class RightsHolderSchema(BaseModel):
    """Schema Pydantic pour RightsHolder"""
    holder_id: str
    holder_type: str
    legal_name: str
    display_name: Optional[str] = None
    artist_name: Optional[str] = None
    
    # Contact
    email: str
    phone: Optional[str] = None
    website: Optional[str] = None
    social_media: Dict[str, str] = {}
    
    # Adresse
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    
    # Informations légales
    tax_id: Optional[str] = None
    vat_number: Optional[str] = None
    business_registration: Optional[str] = None
    legal_representative: Optional[str] = None
    
    # Organisations de droits
    performing_rights_org: Optional[str] = None
    mechanical_rights_org: Optional[str] = None
    pro_membership_number: Optional[str] = None
    
    # Préférences
    preferred_currency: str = 'EUR'
    payment_preferences: Dict[str, Any] = {}
    
    # Vérification
    identity_verified: bool = False
    kyc_status: str = 'pending'
    
    # Profil créatif
    biography: Optional[str] = None
    genres: List[str] = []
    instruments: List[str] = []
    roles: List[str] = []
    
    # Statut
    account_status: str = 'active'
    subscription_tier: str = 'basic'
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v
    
    @validator('country')
    def validate_country(cls, v):
        if v and len(v) != 2:
            raise ValueError('Country code must be 2 characters (ISO 3166-1 alpha-2)')
        return v
    
    class Config:
        from_attributes = True


class RightsRecordSchema(BaseModel):
    """Schema Pydantic pour RightsRecord"""
    record_id: str
    content_id: str
    primary_holder_id: str
    
    # Informations de base
    title: str
    content_type: ContentType
    creation_date: datetime
    registration_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Droits
    rights_granted: List[str]
    rights_scope: RightScope = RightScope.NON_EXCLUSIVE
    territories: List[str] = ['worldwide']
    
    # Validité
    effective_date: datetime = Field(default_factory=datetime.utcnow)
    expiration_date: Optional[datetime] = None
    renewable: bool = True
    auto_renewal: bool = False
    
    # Enregistrement officiel
    copyright_office: Optional[str] = None
    registration_number: Optional[str] = None
    certificate_number: Optional[str] = None
    deposit_reference: Optional[str] = None
    
    # Statut
    status: str = 'active'
    verification_status: str = 'pending'
    verification_evidence: Dict[str, Any] = {}
    dispute_status: Optional[str] = None
    
    # Détails créatifs
    creators: List[Dict[str, Any]] = []
    contributors: List[Dict[str, Any]] = []
    producers: List[Dict[str, Any]] = []
    publishers: List[Dict[str, Any]] = []
    
    # Restrictions
    usage_restrictions: Dict[str, Any] = {}
    platform_restrictions: List[str] = []
    geographic_restrictions: Dict[str, Any] = {}
    time_restrictions: Dict[str, Any] = {}
    
    @validator('rights_granted')
    def validate_rights_granted(cls, v):
        if not v:
            raise ValueError('At least one right must be granted')
        return v
    
    @validator('territories')
    def validate_territories(cls, v):
        if not v:
            raise ValueError('At least one territory must be specified')
        return v
    
    class Config:
        from_attributes = True
        use_enum_values = True


class LicenseAgreementSchema(BaseModel):
    """Schema Pydantic pour LicenseAgreement"""
    license_id: str
    rights_record_id: str
    licensor_id: str
    licensee_id: str
    
    # Type et portée
    license_type: str
    license_scope: LicenseScope
    licensed_rights: List[str]
    territories: List[str]
    
    # Durée
    start_date: datetime
    end_date: Optional[datetime] = None
    is_perpetual: bool = False
    auto_renewal: bool = False
    renewal_period_months: Optional[int] = None
    notice_period_days: int = 30
    
    # Conditions d'utilisation
    usage_limitations: Dict[str, Any] = {}
    platform_restrictions: List[str] = []
    volume_limitations: Dict[str, Any] = {}
    quality_restrictions: Dict[str, Any] = {}
    
    # Conditions financières
    royalty_structure: Dict[str, Any]
    minimum_guarantee: Decimal = Decimal('0')
    advance_payment: Decimal = Decimal('0')
    payment_schedule: str = 'quarterly'
    currency: str = 'EUR'
    
    # Reporting
    reporting_frequency: str = 'quarterly'
    reporting_requirements: Dict[str, Any] = {}
    audit_rights: bool = True
    access_to_analytics: bool = True
    
    # Clauses spéciales
    attribution_requirements: Dict[str, Any] = {}
    modification_rights: Dict[str, Any] = {}
    sublicensing_allowed: bool = False
    termination_conditions: Dict[str, Any] = {}
    
    # Statut
    status: str = 'active'
    approval_status: str = 'pending'
    signature_status: Dict[str, Any] = {}
    
    @validator('licensed_rights')
    def validate_licensed_rights(cls, v):
        if not v:
            raise ValueError('At least one right must be licensed')
        return v
    
    @validator('territories')
    def validate_territories(cls, v):
        if not v:
            raise ValueError('At least one territory must be specified')
        return v
    
    @validator('royalty_structure')
    def validate_royalty_structure(cls, v):
        if not v:
            raise ValueError('Royalty structure must be defined')
        return v
    
    class Config:
        from_attributes = True
        use_enum_values = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def generate_content_id() -> str:
    """Génère un ID unique pour le contenu"""



    return f"CNT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"

def generate_holder_id() -> str:
    """Génère un ID unique pour le détenteur"""



    return f"HLD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"

def generate_rights_record_id() -> str:
    """Génère un ID unique pour l'enregistrement de droits"""



    return f"RR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"

def generate_license_id() -> str:
    """Génère un ID unique pour la licence"""



    return f"LIC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"

def generate_usage_event_id() -> str:
    """Génère un ID unique pour l'événement d'utilisation"""



    return f"USE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"

def calculate_content_hash(content_data: bytes) -> Tuple[str, str]:
    """Calcule les hashes MD5 et SHA256 du contenu"""
    md5_hash = hashlib.md5(content_data).hexdigest()
    sha256_hash = hashlib.sha256(content_data).hexdigest()
    return md5_hash, sha256_hash

def validate_percentage(value: float) -> bool:
    """Valide qu'un pourcentage est entre 0 et 1"""



    return 0.0 <= value <= 1.0

def validate_currency_code(currency: str) -> bool:
    """Valide un code de devise ISO 4217"""
    iso_currencies = {
        'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 
        'SEK', 'NOK', 'DKK', 'PLN', 'CZK', 'HUF', 'BRL', 'MXN',
        'KRW', 'SGD', 'HKD', 'NZD', 'THB', 'MYR', 'PHP', 'IDR'
    }
    return currency.upper() in iso_currencies

def validate_country_code(country: str) -> bool:
    """Valide un code pays ISO 3166-1 alpha-2"""
    # Validation basique - en production, utiliser une liste complète
    return len(country) == 2 and country.isalpha()

def validate_email_format(email: str) -> bool:
    """Validation basique du format email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


__all__ = [
    # Tables SQLAlchemy
    'Base',
    'ContentMetadata',
    'RightsHolder', 
    'RightsRecord',
    'CoHolderAssociation',
    'LicenseAgreement',
    'UsageEvent',
    'UsageReport',
    'RoyaltyCalculation',
    'PaymentInstruction',
    'TerritorialRights',
    
    # Schemas Pydantic
    'ContentMetadataSchema',
    'RightsHolderSchema',
    'RightsRecordSchema', 
    'LicenseAgreementSchema',
    
    # Enums
    'ContentType',
    'RightScope',
    'LicenseScope',
    'RevenueSplitType',
    
    # Fonctions utilitaires
    'generate_content_id',
    'generate_holder_id',
    'generate_rights_record_id',
    'generate_license_id',
    'generate_usage_event_id',
    'calculate_content_hash',
    'validate_percentage',
    'validate_currency_code',
    'validate_country_code',
    'validate_email_format'
]
