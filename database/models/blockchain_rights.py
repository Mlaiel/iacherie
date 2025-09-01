"""Blockchain Rights Management Database Model

Enterprise-grade SQLAlchemy model for blockchain-based rights management,
NFT integration, and immutable copyright verification.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class BlockchainNetwork(Enum):
    """
Supported blockchain networks"""

    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BINANCE_SMART_CHAIN = "binance_smart_chain"
    AVALANCHE = "avalanche"
    SOLANA = "solana"
    CARDANO = "cardano"
    TEZOS = "tezos"
    FLOW = "flow"


class RightsType(Enum):
    """Digital rights types"""

    COPYRIGHT = "copyright"
    PERFORMANCE_RIGHTS = "performance_rights"
    MECHANICAL_RIGHTS = "mechanical_rights"
    SYNC_RIGHTS = "sync_rights"
    MASTER_RECORDING = "master_recording"
    PUBLISHING_RIGHTS = "publishing_rights"
    MERCHANDISING_RIGHTS = "merchandising_rights"
    STREAMING_RIGHTS = "streaming_rights"
    DISTRIBUTION_RIGHTS = "distribution_rights"
    REMIX_RIGHTS = "remix_rights"


class SmartContractStatus(Enum):
    """Smart contract status"""

    PENDING_DEPLOYMENT = "pending_deployment"
    DEPLOYED = "deployed"
    ACTIVE = "active"
    PAUSED = "paused"
    TERMINATED = "terminated"
    UPGRADED = "upgraded"
    FAILED = "failed"


class BlockchainRights(Base):
    """
    Blockchain Rights Management Model
    
    Manages immutable rights registration, NFT minting, and smart contract automation
    for content creators' intellectual property protection.
    """
    __tablename__ = "blockchain_rights"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_fingerprint_id = Column(UUID(as_uuid=True), ForeignKey('content_fingerprints.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Blockchain registration
    blockchain_network = Column(SQLEnum(BlockchainNetwork), nullable=False, index=True)
    smart_contract_address = Column(String(255), nullable=True, index=True)
    transaction_hash = Column(String(255), nullable=True, unique=True, index=True)
    block_number = Column(Integer, nullable=True)
    gas_used = Column(Integer, nullable=True)
    
    # Rights definition
    rights_type = Column(SQLEnum(RightsType), nullable=False, index=True)
    rights_percentage = Column(Float, default=100.0)  # Ownership percentage
    rights_duration_years = Column(Integer, default=50)  # Copyright duration
    territorial_scope = Column(ARRAY(String), nullable=True)  # Countries/regions
    
    # NFT Integration
    nft_token_id = Column(String(255), nullable=True, unique=True, index=True)
    nft_metadata_uri = Column(Text, nullable=True)
    nft_royalty_percentage = Column(Float, default=10.0)
    is_nft_minted = Column(Boolean, default=False)
    
    # Smart contract management
    contract_status = Column(SQLEnum(SmartContractStatus), default=SmartContractStatus.PENDING_DEPLOYMENT)
    contract_abi = Column(JSON, nullable=True)
    deployment_cost = Column(Numeric(18, 8), nullable=True)
    
    # Rights verification
    ownership_proof_hash = Column(String(255), nullable=False)
    timestamp_proof = Column(DateTime(timezone=True), nullable=False)
    verification_signatures = Column(JSON, nullable=True)
    witness_addresses = Column(ARRAY(String), nullable=True)
    
    # Revenue sharing
    revenue_split_rules = Column(JSON, nullable=True)
    automated_distribution = Column(Boolean, default=True)
    minimum_payout_threshold = Column(Numeric(18, 8), default=Decimal('10.0'))
    
    # Legal framework
    legal_jurisdiction = Column(String(100), default="International")
    applicable_law = Column(String(255), nullable=True)
    dispute_resolution_method = Column(String(100), default="blockchain_arbitration")
    
    # Licensing automation
    license_terms = Column(JSON, nullable=True)
    automatic_licensing_enabled = Column(Boolean, default=False)
    license_price_usd = Column(Numeric(18, 8), nullable=True)
    bulk_license_discounts = Column(JSON, nullable=True)
    
    # Violation tracking
    violation_count = Column(Integer, default=0)
    last_violation_detected = Column(DateTime(timezone=True), nullable=True)
    enforcement_actions = Column(JSON, nullable=True)
    damages_recovered = Column(Numeric(18, 8), default=Decimal('0.0'))
    
    # Network statistics
    network_fees_paid = Column(Numeric(18, 8), default=Decimal('0.0'))
    total_transactions = Column(Integer, default=0)
    last_chain_sync = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata and documentation
    rights_documentation = Column(JSON, nullable=True)
    creator_statement = Column(Text, nullable=True)
    third_party_verifications = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deployed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    is_transferable = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    content_fingerprint = relationship("ContentFingerprint", back_populates="blockchain_rights")
    license_agreements = relationship("LicensingAgreement", back_populates="blockchain_rights", cascade="all, delete-orphan")
    violation_reports = relationship("ViolationReport", back_populates="blockchain_rights", cascade="all, delete-orphan")
    
    # Advanced indexes for performance
    __table_args__ = (
        Index('idx_blockchain_rights_user_network', 'user_id', 'blockchain_network'),
        Index('idx_blockchain_rights_contract_status', 'smart_contract_address', 'contract_status'),
        Index('idx_blockchain_rights_nft', 'nft_token_id', 'is_nft_minted'),
        Index('idx_blockchain_rights_rights_type', 'rights_type', 'rights_percentage'),
        Index('idx_blockchain_rights_verification', 'ownership_proof_hash', 'is_verified'),
        Index('idx_blockchain_rights_licensing', 'automatic_licensing_enabled', 'license_price_usd'),
        Index('idx_blockchain_rights_violations', 'violation_count', 'last_violation_detected'),
    )
    
    def __repr__(self):
        return f"<BlockchainRights(id={self.id}, network={self.blockchain_network.value}, rights_type={self.rights_type.value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        return {
            "id": str(self.id),
            "content_fingerprint_id": str(self.content_fingerprint_id),
            "user_id": str(self.user_id),
            "blockchain_network": self.blockchain_network.value,
            "smart_contract_address": self.smart_contract_address,
            "transaction_hash": self.transaction_hash,
            "block_number": self.block_number,
            "gas_used": self.gas_used,
            "rights_type": self.rights_type.value,
            "rights_percentage": self.rights_percentage,
            "rights_duration_years": self.rights_duration_years,
            "territorial_scope": self.territorial_scope,
            "nft_token_id": self.nft_token_id,
            "nft_metadata_uri": self.nft_metadata_uri,
            "nft_royalty_percentage": self.nft_royalty_percentage,
            "is_nft_minted": self.is_nft_minted,
            "contract_status": self.contract_status.value,
            "deployment_cost": float(self.deployment_cost) if self.deployment_cost else None,
            "ownership_proof_hash": self.ownership_proof_hash,
            "timestamp_proof": self.timestamp_proof.isoformat() if self.timestamp_proof else None,
            "verification_signatures": self.verification_signatures,
            "witness_addresses": self.witness_addresses,
            "revenue_split_rules": self.revenue_split_rules,
            "automated_distribution": self.automated_distribution,
            "minimum_payout_threshold": float(self.minimum_payout_threshold) if self.minimum_payout_threshold else None,
            "legal_jurisdiction": self.legal_jurisdiction,
            "applicable_law": self.applicable_law,
            "dispute_resolution_method": self.dispute_resolution_method,
            "license_terms": self.license_terms,
            "automatic_licensing_enabled": self.automatic_licensing_enabled,
            "license_price_usd": float(self.license_price_usd) if self.license_price_usd else None,
            "bulk_license_discounts": self.bulk_license_discounts,
            "violation_count": self.violation_count,
            "last_violation_detected": self.last_violation_detected.isoformat() if self.last_violation_detected else None,
            "enforcement_actions": self.enforcement_actions,
            "damages_recovered": float(self.damages_recovered) if self.damages_recovered else None,
            "network_fees_paid": float(self.network_fees_paid) if self.network_fees_paid else None,
            "total_transactions": self.total_transactions,
            "last_chain_sync": self.last_chain_sync.isoformat() if self.last_chain_sync else None,
            "rights_documentation": self.rights_documentation,
            "creator_statement": self.creator_statement,
            "third_party_verifications": self.third_party_verifications,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deployed_at": self.deployed_at.isoformat() if self.deployed_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "is_transferable": self.is_transferable,
            "is_verified": self.is_verified
        }


class ViolationReport(Base):
    """
    Blockchain Violation Report Model
    
    Tracks and documents intellectual property violations with immutable evidence.
    """
    __tablename__ = "violation_reports"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    blockchain_rights_id = Column(UUID(as_uuid=True), ForeignKey('blockchain_rights.id'), nullable=False, index=True)
    
    # Violation details
    violation_type = Column(String(100), nullable=False)
    detected_platform = Column(String(100), nullable=False)
    infringing_url = Column(Text, nullable=False)
    similarity_score = Column(Float, nullable=False)
    
    # Evidence collection
    evidence_hash = Column(String(255), nullable=False)
    screenshot_hash = Column(String(255), nullable=True)
    metadata_captured = Column(JSON, nullable=True)
    blockchain_timestamp = Column(DateTime(timezone=True), nullable=False)
    
    # Response tracking
    takedown_request_sent = Column(Boolean, default=False)
    takedown_response_received = Column(Boolean, default=False)
    legal_action_initiated = Column(Boolean, default=False)
    resolution_status = Column(String(50), default="pending")
    
    # Financial impact
    estimated_damages = Column(Numeric(18, 8), nullable=True)
    recovery_amount = Column(Numeric(18, 8), default=Decimal('0.0'))
    legal_costs = Column(Numeric(18, 8), default=Decimal('0.0'))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    blockchain_rights = relationship("BlockchainRights", back_populates="violation_reports")
    
    def __repr__(self):
        return f"<ViolationReport(id={self.id}, platform={self.detected_platform}, score={self.similarity_score})>"


class LicenseAutomation(Base):
    """
    License Automation Model
    
    Manages automated licensing requests, negotiations, and smart contract execution.
    """
    __tablename__ = "license_automation"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    blockchain_rights_id = Column(UUID(as_uuid=True), ForeignKey('blockchain_rights.id'), nullable=False, index=True)
    
    # License request details
    licensee_wallet_address = Column(String(255), nullable=False, index=True)
    requested_usage_type = Column(String(100), nullable=False)
    proposed_price = Column(Numeric(18, 8), nullable=False)
    license_duration_days = Column(Integer, nullable=False)
    territory_requested = Column(ARRAY(String), nullable=True)
    
    # Automation rules
    auto_approval_threshold = Column(Numeric(18, 8), nullable=True)
    negotiation_allowed = Column(Boolean, default=True)
    maximum_discount_percentage = Column(Float, default=0.0)
    
    # Smart contract execution
    contract_address = Column(String(255), nullable=True)
    escrow_amount = Column(Numeric(18, 8), nullable=True)
    execution_status = Column(String(50), default="pending")
    
    # Timestamps
    requested_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<LicenseAutomation(id={self.id}, price={self.proposed_price}, status={self.execution_status})>"
