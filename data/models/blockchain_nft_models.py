"""Blockchain NFT Models
=====================

Advanced blockchain and NFT models for IA Influencer Agent platform.
Multi-blockchain asset management with NFT creation, smart contracts,
and decentralized ownership verification.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

🚀 ENTERPRISE FEATURES:
• Multi-blockchain NFT creation & management
• Smart contract deployment & execution
• Cryptocurrency payment integration
• Automated royalty distribution
• Cross-chain asset management
• Immutable ownership verification
• Decentralized licensing & rights management
• Blockchain analytics & reporting
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum, Index, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from decimal import Decimal
from datetime import datetime, date
from enum import Enum
import uuid
from typing import Optional, Dict, Any, List

# Import base from enterprise content models
from .enterprise_content_models import Base

# ============================================================================
# ENUMS - Blockchain System
# ============================================================================

class BlockchainNetwork(Enum):
    """Supported blockchain networks"""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    SOLANA = "solana"
    BINANCE_SMART_CHAIN = "binance_smart_chain"
    AVALANCHE = "avalanche"
    CARDANO = "cardano"
    FLOW = "flow"
    TEZOS = "tezos"
    NEAR = "near"
    COSMOS = "cosmos"
    POLKADOT = "polkadot"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    FANTOM = "fantom"
    CRONOS = "cronos"


class NFTStandard(Enum):
    """NFT token standards"""
    ERC721 = "erc721"      # Ethereum non-fungible tokens
    ERC1155 = "erc1155"    # Ethereum multi-token standard
    SPL_TOKEN = "spl_token"  # Solana Program Library tokens
    BEP721 = "bep721"      # Binance Smart Chain NFTs
    BEP1155 = "bep1155"    # Binance Smart Chain multi-tokens
    FA2 = "fa2"            # Tezos NFT standard
    CIS2 = "cis2"          # Concordium token standard
    FLOW_NFT = "flow_nft"  # Flow blockchain NFTs


class SmartContractType(Enum):
    """Types of smart contracts"""
    NFT_MINTING = "nft_minting"
    LICENSING = "licensing"
    ROYALTY_DISTRIBUTION = "royalty_distribution"
    OWNERSHIP_TRANSFER = "ownership_transfer"
    GOVERNANCE = "governance"
    MARKETPLACE = "marketplace"
    AUCTION = "auction"
    STAKING = "staking"
    ESCROW = "escrow"
    REVENUE_SHARING = "revenue_sharing"
    COPYRIGHT_PROTECTION = "copyright_protection"
    COLLABORATION_AGREEMENT = "collaboration_agreement"


class TransactionStatus(Enum):
    """Blockchain transaction status"""
    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DROPPED = "dropped"
    REPLACED = "replaced"
    REVERTED = "reverted"


class AssetType(Enum):
    """Types of blockchain assets"""
    MUSIC_NFT = "music_nft"
    VIDEO_NFT = "video_nft"
    IMAGE_NFT = "image_nft"
    AUDIO_NFT = "audio_nft"
    COLLECTION = "collection"
    UTILITY_TOKEN = "utility_token"
    GOVERNANCE_TOKEN = "governance_token"
    REVENUE_TOKEN = "revenue_token"
    FRACTIONAL_NFT = "fractional_nft"
    COMPOSITE_NFT = "composite_nft"
    DYNAMIC_NFT = "dynamic_nft"
    PROGRAMMABLE_NFT = "programmable_nft"


class RoyaltyStructure(Enum):
    """Royalty distribution structures"""
    FIXED = "fixed"           # Fixed percentage
    PERCENTAGE = "percentage" # Variable percentage
    TIERED = "tiered"        # Tiered based on sales volume
    DYNAMIC = "dynamic"      # AI-determined dynamic rates
    WATERFALL = "waterfall"  # Hierarchical distribution
    EQUAL_SPLIT = "equal_split"  # Equal among collaborators
    WEIGHTED = "weighted"    # Weighted by contribution
    PERFORMANCE_BASED = "performance_based"  # Based on performance


# ============================================================================
# BLOCKCHAIN ASSET MODELS
# ============================================================================

class BlockchainAssetModel(Base):
    """
    Enterprise blockchain asset model for comprehensive asset management.
    Multi-blockchain support with advanced asset tracking and analytics.
    """
    __tablename__ = 'blockchain_assets'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey('content.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Blockchain configuration
    blockchain_network = Column(SQLEnum(BlockchainNetwork), nullable=False, index=True)
    asset_type = Column(SQLEnum(AssetType), nullable=False, index=True)
    token_standard = Column(SQLEnum(NFTStandard), nullable=False)
    
    # Asset identification
    token_id = Column(String(200), index=True)
    contract_address = Column(String(200), nullable=False, index=True)
    token_uri = Column(String(1000))  # Metadata URI
    collection_id = Column(String(200), index=True)
    creator_address = Column(String(200), nullable=False)
    current_owner_address = Column(String(200), nullable=False, index=True)
    
    # Asset metadata
    asset_name = Column(String(500), nullable=False)
    asset_description = Column(Text)
    asset_image_url = Column(String(1000))
    asset_animation_url = Column(String(1000))
    external_url = Column(String(1000))
    background_color = Column(String(7))  # Hex color
    
    # Technical specifications
    metadata_json = Column(JSONB, default=dict)  # Complete NFT metadata
    attributes = Column(JSONB, default=list)  # NFT attributes/traits
    rarity_score = Column(Float, default=0.0)  # Rarity ranking
    rarity_rank = Column(Integer)
    total_supply = Column(Integer, default=1)  # For ERC1155
    circulating_supply = Column(Integer, default=1)
    
    # Minting information
    minting_transaction_hash = Column(String(200), unique=True, index=True)
    minting_block_number = Column(Integer)
    minting_timestamp = Column(DateTime(timezone=True))
    minting_gas_used = Column(Integer)
    minting_gas_price = Column(Numeric(30, 0))  # Wei
    minting_cost = Column(Numeric(20, 8))  # Cost in native token
    
    # Pricing & Valuation
    mint_price = Column(Numeric(20, 8))  # Original mint price
    current_price = Column(Numeric(20, 8))  # Current market price
    last_sale_price = Column(Numeric(20, 8))  # Last sale price
    floor_price = Column(Numeric(20, 8))  # Collection floor price
    estimated_value = Column(Numeric(20, 8))  # AI-estimated value
    price_currency = Column(String(10), default="ETH")
    
    # Trading history
    total_sales = Column(Integer, default=0)
    total_volume = Column(Numeric(25, 8), default=0)  # Total trading volume
    last_sale_timestamp = Column(DateTime(timezone=True))
    highest_sale_price = Column(Numeric(20, 8))
    average_sale_price = Column(Numeric(20, 8))
    
    # Marketplace presence
    listed_on_marketplaces = Column(JSONB, default=list)  # ["opensea", "rarible"]
    marketplace_urls = Column(JSONB, default=dict)
    is_listed_for_sale = Column(Boolean, default=False)
    listing_price = Column(Numeric(20, 8))
    listing_expiry = Column(DateTime(timezone=True))
    
    # Royalty configuration
    royalty_percentage = Column(Float, default=0.0)  # 0-100%
    royalty_structure = Column(SQLEnum(RoyaltyStructure), default=RoyaltyStructure.FIXED)
    royalty_recipients = Column(JSONB, default=dict)  # {"address": percentage}
    total_royalties_earned = Column(Numeric(20, 8), default=0)
    royalty_contract_address = Column(String(200))
    
    # Ownership history
    ownership_history = Column(JSONB, default=list)  # Transfer history
    transfer_count = Column(Integer, default=0)
    first_owner = Column(String(200))
    ownership_duration = Column(Integer, default=0)  # Days with current owner
    
    # Utility & Functionality
    utility_features = Column(JSONB, default=list)  # NFT utilities
    unlockable_content = Column(Boolean, default=False)
    access_permissions = Column(JSONB, default=dict)
    staking_enabled = Column(Boolean, default=False)
    staking_rewards = Column(Numeric(20, 8), default=0)
    
    # Copyright & Legal
    copyright_status = Column(String(100), default="creator_owned")
    licensing_terms = Column(Text)
    commercial_use_allowed = Column(Boolean, default=False)
    derivative_works_allowed = Column(Boolean, default=False)
    legal_disclaimers = Column(Text)
    
    # Analytics & Performance
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    social_mentions = Column(Integer, default=0)
    engagement_score = Column(Float, default=0.0)
    
    # Cross-chain features
    is_bridged = Column(Boolean, default=False)
    bridge_contracts = Column(JSONB, default=list)
    cross_chain_addresses = Column(JSONB, default=dict)
    bridge_history = Column(JSONB, default=list)
    
    # Fractionalization
    is_fractionalized = Column(Boolean, default=False)
    fraction_token_contract = Column(String(200))
    total_fractions = Column(Integer)
    fraction_price = Column(Numeric(20, 8))
    fraction_holders = Column(Integer, default=0)
    
    # AI & Enhancement
    ai_generated = Column(Boolean, default=False)
    ai_enhancement_applied = Column(Boolean, default=False)
    ai_valuation_model = Column(String(100))
    ai_predicted_value = Column(Numeric(20, 8))
    ai_market_insights = Column(JSONB, default=dict)
    
    # Environmental impact
    carbon_footprint = Column(Float, default=0.0)  # CO2 equivalent
    energy_efficient_network = Column(Boolean, default=False)
    carbon_offset_applied = Column(Boolean, default=False)
    sustainability_score = Column(Float, default=0.0)
    
    # Insurance & Protection
    insured_value = Column(Numeric(20, 8))
    insurance_provider = Column(String(200))
    insurance_policy_id = Column(String(200))
    theft_protection = Column(Boolean, default=False)
    fraud_protection = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_price_update = Column(DateTime(timezone=True))
    last_metadata_sync = Column(DateTime(timezone=True))
    
    # System flags
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)
    is_flagged = Column(Boolean, default=False)
    is_burned = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    content = relationship("ContentModel", backref="blockchain_assets")
    user = relationship("UserModel", backref="blockchain_assets")
    smart_contracts = relationship("SmartContractModel", back_populates="blockchain_asset", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_asset_network_type', 'blockchain_network', 'asset_type'),
        Index('idx_asset_contract_token', 'contract_address', 'token_id'),
        Index('idx_asset_owner_price', 'current_owner_address', 'current_price'),
        Index('idx_asset_collection_rarity', 'collection_id', 'rarity_rank'),
    )
    
    def __repr__(self):
        return f"<BlockchainAssetModel(id={self.id}, network={self.blockchain_network.value}, type={self.asset_type.value})>"


# ============================================================================
# NFT MODELS
# ============================================================================

class NFTModel(Base):
    """
    Specialized NFT model for non-fungible token management.
    Extended NFT features with marketplace integration and analytics.
    """
    __tablename__ = 'nfts'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    blockchain_asset_id = Column(UUID(as_uuid=True), ForeignKey('blockchain_assets.id'), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey('content.id'), nullable=False, index=True)
    creator_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # NFT specific details
    nft_name = Column(String(500), nullable=False)
    nft_description = Column(Text)
    edition_number = Column(Integer)  # For limited editions
    edition_size = Column(Integer)   # Total editions
    series_name = Column(String(300))
    
    # Visual & Media
    image_url = Column(String(1000))
    animation_url = Column(String(1000))
    video_url = Column(String(1000))
    audio_url = Column(String(1000))
    model_3d_url = Column(String(1000))
    thumbnail_url = Column(String(1000))
    
    # Metadata & Attributes
    traits = Column(JSONB, default=list)  # NFT traits/properties
    properties = Column(JSONB, default=dict)  # Additional properties
    levels = Column(JSONB, default=dict)  # Level-based attributes
    stats = Column(JSONB, default=dict)  # Stat-based attributes
    boosts = Column(JSONB, default=dict)  # Boost-based attributes
    
    # Rarity & Classification
    rarity_tier = Column(String(50))  # "common", "rare", "epic", "legendary"
    rarity_percentage = Column(Float)  # % rarity in collection
    classification = Column(String(100))  # Art category/genre
    style = Column(String(100))
    medium = Column(String(100))
    
    # Provenance & Authentication
    provenance_verified = Column(Boolean, default=False)
    authenticity_certificate = Column(String(1000))  # Certificate URL/hash
    creation_process = Column(Text)  # How it was created
    inspiration = Column(Text)  # Inspiration/story behind NFT
    historical_significance = Column(Text)
    
    # Rights & Licensing
    copyright_holder = Column(String(300))
    licensing_terms = Column(Text)
    commercial_rights = Column(Boolean, default=False)
    derivative_rights = Column(Boolean, default=False)
    display_rights = Column(Boolean, default=True)
    resale_rights = Column(Boolean, default=True)
    
    # Physical & Digital
    has_physical_counterpart = Column(Boolean, default=False)
    physical_description = Column(Text)
    physical_location = Column(String(300))
    shipping_information = Column(JSONB, default=dict)
    digital_only = Column(Boolean, default=True)
    
    # Interactive Features
    interactive_elements = Column(JSONB, default=list)
    unlockable_content_type = Column(String(100))
    unlockable_content_url = Column(String(1000))
    access_token_required = Column(Boolean, default=False)
    membership_benefits = Column(JSONB, default=list)
    
    # Gaming & Utility
    game_assets = Column(JSONB, default=list)
    utility_functions = Column(JSONB, default=list)
    staking_rewards_apr = Column(Float, default=0.0)
    governance_voting_power = Column(Integer, default=0)
    access_passes = Column(JSONB, default=list)
    
    # Social Features
    creator_social_links = Column(JSONB, default=dict)
    community_features = Column(JSONB, default=list)
    collaboration_credits = Column(JSONB, default=list)
    fan_engagement_tools = Column(JSONB, default=dict)
    
    # Marketplace Performance
    marketplace_performance = Column(JSONB, default=dict)  # Per marketplace stats
    trending_score = Column(Float, default=0.0)
    popularity_rank = Column(Integer)
    search_rankings = Column(JSONB, default=dict)
    recommendation_score = Column(Float, default=0.0)
    
    # Investment & Financial
    investment_potential = Column(Float, default=0.0)  # AI-assessed potential
    price_volatility = Column(Float, default=0.0)
    liquidity_score = Column(Float, default=0.0)
    market_sentiment = Column(String(20), default="neutral")
    financial_metrics = Column(JSONB, default=dict)
    
    # Environmental & Sustainability
    eco_friendly_minting = Column(Boolean, default=False)
    carbon_neutral = Column(Boolean, default=False)
    environmental_impact = Column(JSONB, default=dict)
    sustainability_certifications = Column(JSONB, default=list)
    
    # Technical Specifications
    file_format = Column(String(50))
    file_size = Column(Integer)  # bytes
    resolution = Column(String(50))
    duration = Column(Float)  # For audio/video
    quality_settings = Column(JSONB, default=dict)
    compression_applied = Column(Boolean, default=False)
    
    # Version Control
    version_number = Column(String(20), default="1.0")
    version_history = Column(JSONB, default=list)
    update_mechanism = Column(String(100))
    immutable_features = Column(JSONB, default=list)
    mutable_features = Column(JSONB, default=list)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    minted_at = Column(DateTime(timezone=True))
    last_transfer_at = Column(DateTime(timezone=True))
    
    # System flags
    is_verified_creator = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    is_adult_content = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    blockchain_asset = relationship("BlockchainAssetModel", backref="nft_details")
    content = relationship("ContentModel", backref="nfts")
    creator = relationship("UserModel", backref="created_nfts")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_nft_creator_rarity', 'creator_id', 'rarity_tier'),
        Index('idx_nft_series_edition', 'series_name', 'edition_number'),
        Index('idx_nft_trending_featured', 'trending_score', 'is_featured'),
    )
    
    def __repr__(self):
        return f"<NFTModel(id={self.id}, name='{self.nft_name[:50]}', rarity={self.rarity_tier})>"


# ============================================================================
# SMART CONTRACT MODELS
# ============================================================================

class SmartContractModel(Base):
    """
    Smart contract model for blockchain contract management.
    Comprehensive contract tracking with execution monitoring.
    """
    __tablename__ = 'smart_contracts'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    blockchain_asset_id = Column(UUID(as_uuid=True), ForeignKey('blockchain_assets.id'), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Contract details
    contract_type = Column(SQLEnum(SmartContractType), nullable=False, index=True)
    contract_address = Column(String(200), nullable=False, unique=True, index=True)
    blockchain_network = Column(SQLEnum(BlockchainNetwork), nullable=False, index=True)
    contract_name = Column(String(300), nullable=False)
    contract_symbol = Column(String(20))
    
    # Deployment information
    deployment_transaction_hash = Column(String(200), unique=True, index=True)
    deployment_block_number = Column(Integer)
    deployment_timestamp = Column(DateTime(timezone=True))
    deployer_address = Column(String(200), nullable=False)
    deployment_gas_used = Column(Integer)
    deployment_gas_price = Column(Numeric(30, 0))  # Wei
    deployment_cost = Column(Numeric(20, 8))
    
    # Contract code & ABI
    contract_source_code = Column(Text)
    contract_abi = Column(JSONB)  # Application Binary Interface
    bytecode = Column(Text)
    constructor_parameters = Column(JSONB, default=dict)
    contract_version = Column(String(20), default="1.0")
    
    # Functionality
    contract_functions = Column(JSONB, default=list)  # Available functions
    contract_events = Column(JSONB, default=list)    # Events emitted
    permission_model = Column(JSONB, default=dict)   # Access controls
    upgrade_mechanism = Column(String(100))
    is_upgradeable = Column(Boolean, default=False)
    
    # Execution tracking
    total_transactions = Column(Integer, default=0)
    successful_transactions = Column(Integer, default=0)
    failed_transactions = Column(Integer, default=0)
    total_gas_used = Column(Numeric(30, 0), default=0)
    average_gas_per_transaction = Column(Integer)
    
    # Financial tracking
    total_value_processed = Column(Numeric(25, 8), default=0)  # Total ETH/tokens
    fees_collected = Column(Numeric(20, 8), default=0)
    royalties_distributed = Column(Numeric(20, 8), default=0)
    revenue_generated = Column(Numeric(20, 8), default=0)
    
    # Royalty configuration (for royalty contracts)
    royalty_percentage = Column(Float)
    royalty_recipients = Column(JSONB, default=dict)
    royalty_distribution_logic = Column(Text)
    automatic_distribution = Column(Boolean, default=True)
    
    # Governance features
    governance_enabled = Column(Boolean, default=False)
    voting_mechanism = Column(String(100))
    proposal_threshold = Column(Numeric(20, 8))
    quorum_required = Column(Float)  # Percentage
    voting_period_days = Column(Integer)
    
    # Security features
    security_audited = Column(Boolean, default=False)
    audit_report_url = Column(String(1000))
    security_score = Column(Float, default=0.0)  # 0-100
    vulnerability_count = Column(Integer, default=0)
    last_security_check = Column(DateTime(timezone=True))
    
    # Performance metrics
    response_time_ms = Column(Float, default=0.0)
    uptime_percentage = Column(Float, default=100.0)
    error_rate = Column(Float, default=0.0)
    optimization_score = Column(Float, default=0.0)
    
    # Monitoring & Alerts
    monitoring_enabled = Column(Boolean, default=True)
    alert_thresholds = Column(JSONB, default=dict)
    webhook_urls = Column(JSONB, default=list)
    notification_settings = Column(JSONB, default=dict)
    
    # Legal & Compliance
    legal_framework = Column(String(200))
    compliance_status = Column(String(100), default="compliant")
    regulatory_approvals = Column(JSONB, default=list)
    terms_of_service_url = Column(String(1000))
    privacy_policy_url = Column(String(1000))
    
    # Integration features
    api_endpoints = Column(JSONB, default=list)
    webhook_endpoints = Column(JSONB, default=list)
    external_integrations = Column(JSONB, default=list)
    oracle_connections = Column(JSONB, default=list)
    
    # Version control
    contract_versions = Column(JSONB, default=list)
    upgrade_history = Column(JSONB, default=list)
    pending_upgrades = Column(JSONB, default=list)
    rollback_capability = Column(Boolean, default=False)
    
    # Analytics
    usage_analytics = Column(JSONB, default=dict)
    performance_analytics = Column(JSONB, default=dict)
    user_analytics = Column(JSONB, default=dict)
    financial_analytics = Column(JSONB, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_interaction = Column(DateTime(timezone=True))
    next_maintenance = Column(DateTime(timezone=True))
    
    # System flags
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    is_paused = Column(Boolean, default=False)
    is_deprecated = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    blockchain_asset = relationship("BlockchainAssetModel", back_populates="smart_contracts")
    user = relationship("UserModel", backref="smart_contracts")
    cryptocurrency_transactions = relationship("CryptocurrencyModel", back_populates="smart_contract", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_contract_type_network', 'contract_type', 'blockchain_network'),
        Index('idx_contract_user_active', 'user_id', 'is_active'),
        Index('idx_contract_deployment_timestamp', 'deployment_timestamp'),
    )
    
    def __repr__(self):
        return f"<SmartContractModel(id={self.id}, type={self.contract_type.value}, address={self.contract_address[:10]}...)>"


# ============================================================================
# CRYPTOCURRENCY MODELS
# ============================================================================

class CryptocurrencyModel(Base):
    """
    Cryptocurrency transaction and wallet model.
    Comprehensive crypto payment and transaction tracking.
    """
    __tablename__ = 'cryptocurrency'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    smart_contract_id = Column(UUID(as_uuid=True), ForeignKey('smart_contracts.id'), nullable=True, index=True)
    
    # Transaction details
    transaction_hash = Column(String(200), unique=True, nullable=False, index=True)
    blockchain_network = Column(SQLEnum(BlockchainNetwork), nullable=False, index=True)
    transaction_type = Column(String(100), nullable=False)  # "transfer", "mint", "sale", "royalty"
    status = Column(SQLEnum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING, index=True)
    
    # Financial details
    amount = Column(Numeric(25, 8), nullable=False)  # Crypto amount
    currency = Column(String(20), nullable=False)  # "ETH", "BTC", "MATIC", etc.
    usd_value = Column(Numeric(15, 4))  # USD value at transaction time
    gas_fee = Column(Numeric(20, 8))  # Gas fee paid
    network_fee = Column(Numeric(20, 8))  # Additional network fees
    platform_fee = Column(Numeric(20, 8))  # Platform fees
    
    # Addresses
    from_address = Column(String(200), nullable=False, index=True)
    to_address = Column(String(200), nullable=False, index=True)
    contract_address = Column(String(200), index=True)  # Token contract
    
    # Blockchain data
    block_number = Column(Integer, index=True)
    block_timestamp = Column(DateTime(timezone=True))
    gas_used = Column(Integer)
    gas_price = Column(Numeric(30, 0))  # Wei
    nonce = Column(Integer)
    confirmation_count = Column(Integer, default=0)
    
    # Transaction metadata
    transaction_data = Column(Text)  # Raw transaction data
    logs = Column(JSONB, default=list)  # Transaction logs
    events = Column(JSONB, default=list)  # Contract events
    method_signature = Column(String(100))  # Called method
    input_parameters = Column(JSONB, default=dict)
    
    # Context information
    transaction_purpose = Column(String(200))  # Purpose description
    related_nft_id = Column(String(200))  # Related NFT token ID
    marketplace = Column(String(100))  # Marketplace if applicable
    auction_id = Column(String(200))  # Auction ID if applicable
    
    # Tax & Accounting
    tax_category = Column(String(100))  # Tax classification
    taxable_event = Column(Boolean, default=True)
    cost_basis = Column(Numeric(15, 4))  # Cost basis in USD
    capital_gains = Column(Numeric(15, 4))  # Capital gains/loss
    tax_year = Column(Integer)
    
    # Exchange rate data
    exchange_rate = Column(Numeric(15, 8))  # Crypto to USD rate
    exchange_rate_source = Column(String(100))  # Rate source
    exchange_rate_timestamp = Column(DateTime(timezone=True))
    
    # Risk & Compliance
    risk_score = Column(Float, default=0.0)  # 0-1 risk assessment
    aml_check_status = Column(String(50), default="passed")  # Anti-money laundering
    sanctions_check = Column(Boolean, default=False)
    compliance_notes = Column(Text)
    flagged_by_system = Column(Boolean, default=False)
    
    # Performance tracking
    confirmation_time = Column(Float)  # Seconds to confirm
    processing_time = Column(Float)  # Total processing time
    retry_count = Column(Integer, default=0)
    error_message = Column(Text)
    success_probability = Column(Float, default=1.0)
    
    # Analytics
    transaction_analytics = Column(JSONB, default=dict)
    user_analytics = Column(JSONB, default=dict)
    market_analytics = Column(JSONB, default=dict)
    performance_metrics = Column(JSONB, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    submitted_at = Column(DateTime(timezone=True))
    confirmed_at = Column(DateTime(timezone=True))
    
    # System flags
    is_internal = Column(Boolean, default=False)  # Internal platform transaction
    is_test_transaction = Column(Boolean, default=False)
    is_refunded = Column(Boolean, default=False)
    is_disputed = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    user = relationship("UserModel", backref="crypto_transactions")
    smart_contract = relationship("SmartContractModel", back_populates="cryptocurrency_transactions")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_crypto_user_currency', 'user_id', 'currency'),
        Index('idx_crypto_network_status', 'blockchain_network', 'status'),
        Index('idx_crypto_from_to_addresses', 'from_address', 'to_address'),
        Index('idx_crypto_timestamp_amount', 'block_timestamp', 'amount'),
    )
    
    def __repr__(self):
        return f"<CryptocurrencyModel(id={self.id}, hash={self.transaction_hash[:10]}..., amount={self.amount} {self.currency})>"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_blockchain_asset_example(content_id: str, user_id: str,
                                   network: BlockchainNetwork = BlockchainNetwork.ETHEREUM) -> BlockchainAssetModel:
    """Create example blockchain asset for testing and development"""
    return BlockchainAssetModel(
        content_id=content_id,
        user_id=user_id,
        blockchain_network=network,
        asset_type=AssetType.MUSIC_NFT,
        token_standard=NFTStandard.ERC721,
        asset_name="Sample Music NFT",
        asset_description="This is a sample music NFT for testing purposes",
        contract_address="0x" + "0" * 40,  # Placeholder address
        creator_address="0x" + "1" * 40,
        current_owner_address="0x" + "1" * 40,
        mint_price=Decimal("0.1"),
        price_currency="ETH"
    )


def create_nft_example(blockchain_asset_id: str, content_id: str, creator_id: str) -> NFTModel:
    """Create example NFT for testing and development"""
    return NFTModel(
        blockchain_asset_id=blockchain_asset_id,
        content_id=content_id,
        creator_id=creator_id,
        nft_name="Sample Art NFT",
        nft_description="This is a sample art NFT for testing purposes",
        edition_number=1,
        edition_size=100,
        rarity_tier="rare",
        traits=[{"trait_type": "Color", "value": "Blue"}, {"trait_type": "Style", "value": "Abstract"}]
    )


def calculate_royalty_distribution(total_amount: Decimal, royalty_recipients: Dict[str, float]) -> Dict[str, Decimal]:
    """Calculate royalty distribution based on recipient percentages"""
    distribution = {}
    total_percentage = sum(royalty_recipients.values())
    
    if total_percentage <= 0:
        return distribution
    
    for recipient, percentage in royalty_recipients.items():
        amount = total_amount * Decimal(str(percentage / 100.0))
        distribution[recipient] = amount.quantize(Decimal('0.00000001'))  # 8 decimal places
    
    return distribution


def estimate_gas_cost(network: BlockchainNetwork, operation: str = "mint") -> Dict[str, Any]:
    """Estimate gas cost for blockchain operations"""
    # Simplified gas estimation (in production, use real gas estimation APIs)
    gas_estimates = {
        BlockchainNetwork.ETHEREUM: {"mint": 200000, "transfer": 21000, "approve": 45000},
        BlockchainNetwork.POLYGON: {"mint": 200000, "transfer": 21000, "approve": 45000},
        BlockchainNetwork.SOLANA: {"mint": 1000, "transfer": 1000, "approve": 1000},  # Solana uses different units
    }
    
    gas_prices = {
        BlockchainNetwork.ETHEREUM: 30,  # Gwei
        BlockchainNetwork.POLYGON: 30,   # Gwei
        BlockchainNetwork.SOLANA: 0.000005,  # SOL
    }
    
    gas_limit = gas_estimates.get(network, {}).get(operation, 100000)
    gas_price = gas_prices.get(network, 30)
    
    if network == BlockchainNetwork.SOLANA:
        estimated_cost = gas_price  # Solana has fixed transaction fees
        currency = "SOL"
    else:
        estimated_cost = (gas_limit * gas_price) / 1e9  # Convert Gwei to ETH/MATIC
        currency = "ETH" if network == BlockchainNetwork.ETHEREUM else "MATIC"
    
    return {
        "gas_limit": gas_limit,
        "gas_price": gas_price,
        "estimated_cost": estimated_cost,
        "currency": currency,
        "network": network.value
    }


# ============================================================================
# EXPORT SECTION
# ============================================================================

__all__ = [
    # Models
    'BlockchainAssetModel', 'NFTModel', 'SmartContractModel', 'CryptocurrencyModel',
    
    # Blockchain Enums
    'BlockchainNetwork', 'NFTStandard', 'SmartContractType', 'TransactionStatus',
    'AssetType', 'RoyaltyStructure',
    
    # Utility Functions
    'create_blockchain_asset_example', 'create_nft_example',
    'calculate_royalty_distribution', 'estimate_gas_cost'
]