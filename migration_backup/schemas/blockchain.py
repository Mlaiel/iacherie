"""Blockchain & NFT Schemas for IA Influencer Agent Platform
Comprehensive blockchain integration, NFT management, and crypto monetization schemas

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import Field, HttpUrl, validator

from .base import BaseSchema, TimestampSchema, UUIDSchema, AuditSchema


class BlockchainNetwork(UUIDSchema, TimestampSchema):
    """
Blockchain network configuration schema."""
    
    network_name: str = Field(description="Blockchain network name")
    network_type: str = Field(description="Type of blockchain network")
    blockchain_protocol: str = Field(description="Blockchain protocol used")
    
    # Network specifications
    chain_id: int = Field(description="Blockchain chain ID")
    network_url: HttpUrl = Field(description="RPC endpoint URL")
    explorer_url: HttpUrl = Field(description="Block explorer URL")
    native_currency: Dict[str, str] = Field(description="Native currency details")
    
    # Network characteristics
    consensus_mechanism: str = Field(description="Consensus mechanism")
    block_time: float = Field(gt=0.0, description="Average block time in seconds")
    transaction_finality: str = Field(description="Transaction finality type")
    scalability_metrics: Dict[str, float] = Field(default_factory=dict)
    
    # Gas and fees
    gas_price_gwei: Optional[float] = Field(None, ge=0.0)
    estimated_gas_costs: Dict[str, int] = Field(default_factory=dict)
    fee_structure: Dict[str, str] = Field(default_factory=dict)
    dynamic_fee_support: bool = Field(default=False)
    
    # Security and reliability
    network_security_level: str = Field(description="Network security assessment")
    uptime_percentage: float = Field(default=99.9, ge=0.0, le=100.0)
    decentralization_score: float = Field(ge=0.0, le=1.0)
    audit_reports: List[HttpUrl] = Field(default_factory=list)
    
    # Integration capabilities
    supported_standards: List[str] = Field(default_factory=list)
    smart_contract_support: bool = Field(default=True)
    layer2_solutions: List[str] = Field(default_factory=list)
    cross_chain_compatibility: List[str] = Field(default_factory=list)
    
    # Development tools
    development_frameworks: List[str] = Field(default_factory=list)
    testing_networks: List[str] = Field(default_factory=list)
    developer_documentation: Optional[HttpUrl] = None
    api_endpoints: List[HttpUrl] = Field(default_factory=list)
    
    # Status and monitoring
    is_active: bool = Field(default=True)
    network_status: str = Field(default="operational")
    last_health_check: Optional[datetime] = None
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    
    @validator('network_type')
    def validate_network_type(cls, v):
        """Validate network type."""
        allowed_types = {
            "mainnet", "testnet", "private", "consortium", "sidechain",
            "layer2", "rollup", "state_channel", "plasma"
        }
        if v not in allowed_types:
            raise ValueError(f'Network type must be one of: {", ".join(allowed_types)}')
        return v


class SmartContract(UUIDSchema, TimestampSchema, AuditSchema):
    """Smart contract configuration and management schema."""
    
    contract_name: str = Field(description="Smart contract name")
    contract_type: str = Field(description="Type of smart contract")
    blockchain_network_id: UUID = Field(description="Associated blockchain network")
    
    # Contract details
    contract_address: str = Field(description="Contract address on blockchain")
    contract_abi: List[Dict[str, Any]] = Field(description="Contract ABI")
    bytecode: Optional[str] = Field(None, description="Contract bytecode")
    source_code: Optional[str] = Field(None, description="Contract source code")
    
    # Contract metadata
    compiler_version: str = Field(description="Solidity compiler version")
    optimization_enabled: bool = Field(default=True)
    license: str = Field(description="Contract license")
    verification_status: str = Field(default="unverified")
    
    # Deployment information
    deployment_transaction: str = Field(description="Deployment transaction hash")
    deployer_address: str = Field(description="Deployer wallet address")
    deployment_gas_used: int = Field(ge=0)
    deployment_cost: Decimal = Field(ge=0, description="Deployment cost in native currency")
    
    # Contract functionality
    supported_functions: List[Dict[str, Any]] = Field(default_factory=list)
    events_emitted: List[Dict[str, Any]] = Field(default_factory=list)
    state_variables: List[Dict[str, Any]] = Field(default_factory=list)
    modifiers: List[str] = Field(default_factory=list)
    
    # Security and auditing
    security_audit_status: str = Field(default="not_audited")
    audit_reports: List[HttpUrl] = Field(default_factory=list)
    known_vulnerabilities: List[str] = Field(default_factory=list)
    security_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    
    # Upgradability
    is_upgradeable: bool = Field(default=False)
    proxy_pattern: Optional[str] = None
    upgrade_mechanism: Optional[str] = None
    admin_controls: List[str] = Field(default_factory=list)
    
    # Usage statistics
    total_transactions: int = Field(default=0, ge=0)
    active_users: int = Field(default=0, ge=0)
    total_value_locked: Decimal = Field(default=Decimal('0.00'), ge=0)
    gas_usage_statistics: Dict[str, float] = Field(default_factory=dict)
    
    # Monitoring and maintenance
    monitoring_enabled: bool = Field(default=True)
    alert_configurations: List[Dict[str, Any]] = Field(default_factory=list)
    maintenance_schedule: Optional[str] = None
    
    @validator('contract_type')
    def validate_contract_type(cls, v):
        """Validate contract type."""
        allowed_types = {
            "nft_contract", "token_contract", "marketplace", "royalty_splitter",
            "auction", "staking", "governance", "oracle", "bridge", "vault"
        }
        if v not in allowed_types:
            raise ValueError(f'Contract type must be one of: {", ".join(allowed_types)}')
        return v


class NFTCollection(UUIDSchema, TimestampSchema, AuditSchema):
    """NFT collection management schema."""
    
    creator_id: UUID = Field(description="Creator of the NFT collection")
    collection_name: str = Field(description="NFT collection name")
    collection_symbol: str = Field(description="Collection symbol/ticker")
    collection_description: str = Field(description="Collection description")
    
    # Collection metadata
    total_supply: int = Field(ge=1, description="Total number of NFTs in collection")
    max_supply: Optional[int] = Field(None, description="Maximum possible supply")
    current_supply: int = Field(default=0, ge=0, description="Currently minted NFTs")
    collection_image: HttpUrl = Field(description="Collection cover image")
    
    # Blockchain details
    smart_contract_id: UUID = Field(description="Associated smart contract")
    contract_address: str = Field(description="Contract address")
    blockchain_network: str = Field(description="Blockchain network name")
    token_standard: str = Field(description="Token standard (ERC-721, ERC-1155)")
    
    # Pricing and economics
    mint_price: Decimal = Field(ge=0, description="Mint price per NFT")
    royalty_percentage: float = Field(ge=0.0, le=100.0, description="Creator royalty percentage")
    secondary_sales_royalty: float = Field(ge=0.0, le=100.0)
    pricing_strategy: str = Field(description="Pricing strategy")
    
    # Minting configuration
    minting_enabled: bool = Field(default=False)
    public_mint_start: Optional[datetime] = None
    public_mint_end: Optional[datetime] = None
    whitelist_mint_start: Optional[datetime] = None
    max_mint_per_wallet: int = Field(default=1, ge=1)
    
    # Utility and features
    utility_features: List[str] = Field(default_factory=list)
    membership_benefits: List[str] = Field(default_factory=list)
    staking_rewards: Optional[Dict[str, Any]] = None
    governance_rights: bool = Field(default=False)
    
    # Metadata and assets
    base_token_uri: HttpUrl = Field(description="Base URI for token metadata")
    metadata_frozen: bool = Field(default=False)
    reveal_strategy: str = Field(default="immediate")
    placeholder_image: Optional[HttpUrl] = None
    
    # Marketing and community
    discord_server: Optional[HttpUrl] = None
    twitter_handle: Optional[str] = None
    website_url: Optional[HttpUrl] = None
    community_size: int = Field(default=0, ge=0)
    
    # Performance metrics
    total_volume_traded: Decimal = Field(default=Decimal('0.00'), ge=0)
    floor_price: Optional[Decimal] = Field(None, ge=0)
    average_sale_price: Optional[Decimal] = Field(None, ge=0)
    holder_count: int = Field(default=0, ge=0)
    
    # Rarity and traits
    trait_definitions: List[Dict[str, Any]] = Field(default_factory=list)
    rarity_distribution: Dict[str, float] = Field(default_factory=dict)
    rarity_calculation_method: str = Field(default="trait_count")
    
    @validator('token_standard')
    def validate_token_standard(cls, v):
        """Validate token standard."""
        allowed_standards = {"ERC-721", "ERC-1155", "BEP-721", "SPL", "TRC-721"}
        if v not in allowed_standards:
            raise ValueError(f'Token standard must be one of: {", ".join(allowed_standards)}')
        return v


class NFTToken(UUIDSchema, TimestampSchema):
    """Individual NFT token schema."""
    
    collection_id: UUID = Field(description="Parent collection")
    token_id: str = Field(description="Unique token ID within collection")
    token_name: str = Field(description="Individual token name")
    
    # Token metadata
    token_description: Optional[str] = None
    image_url: HttpUrl = Field(description="Token image URL")
    animation_url: Optional[HttpUrl] = None
    external_url: Optional[HttpUrl] = None
    attributes: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Ownership and provenance
    current_owner: str = Field(description="Current owner wallet address")
    original_creator: str = Field(description="Original creator wallet address")
    ownership_history: List[Dict[str, Any]] = Field(default_factory=list)
    transfer_count: int = Field(default=0, ge=0)
    
    # Minting details
    minted_at: datetime = Field(description="Minting timestamp")
    mint_transaction: str = Field(description="Minting transaction hash")
    mint_price: Decimal = Field(ge=0, description="Original mint price")
    gas_fee_paid: Decimal = Field(ge=0, description="Gas fees for minting")
    
    # Content protection
    content_hash: str = Field(description="Content hash for authenticity")
    copyright_protection: bool = Field(default=True)
    usage_rights: Dict[str, bool] = Field(default_factory=dict)
    licensing_terms: Optional[str] = None
    
    # Market data
    last_sale_price: Optional[Decimal] = Field(None, ge=0)
    last_sale_date: Optional[datetime] = None
    current_listing_price: Optional[Decimal] = Field(None, ge=0)
    price_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Rarity and ranking
    rarity_rank: Optional[int] = Field(None, ge=1)
    rarity_score: Optional[float] = Field(None, ge=0.0)
    trait_rarity_scores: Dict[str, float] = Field(default_factory=dict)
    
    # Utility and access
    utility_status: Dict[str, bool] = Field(default_factory=dict)
    access_permissions: List[str] = Field(default_factory=list)
    staking_status: Optional[str] = None
    reward_claims: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Technical details
    metadata_uri: HttpUrl = Field(description="Token metadata URI")
    metadata_frozen: bool = Field(default=False)
    token_standard: str = Field(description="Token standard")
    blockchain_network: str = Field(description="Blockchain network")
    
    # Social and community
    like_count: int = Field(default=0, ge=0)
    view_count: int = Field(default=0, ge=0)
    comment_count: int = Field(default=0, ge=0)
    social_mentions: Dict[str, int] = Field(default_factory=dict)


class CryptoWallet(UUIDSchema, TimestampSchema, AuditSchema):
    """Cryptocurrency wallet management schema."""
    
    owner_id: UUID = Field(description="Wallet owner")
    wallet_name: str = Field(description="Wallet display name")
    wallet_type: str = Field(description="Type of wallet")
    
    # Wallet addresses
    primary_address: str = Field(description="Primary wallet address")
    supported_networks: List[str] = Field(description="Supported blockchain networks")
    network_addresses: Dict[str, str] = Field(default_factory=dict)
    
    # Security settings
    is_multi_signature: bool = Field(default=False)
    required_signatures: Optional[int] = Field(None, ge=1)
    authorized_signers: List[str] = Field(default_factory=list)
    security_level: str = Field(description="Wallet security level")
    
    # Wallet balances
    native_balances: Dict[str, Decimal] = Field(default_factory=dict)
    token_balances: List[Dict[str, Any]] = Field(default_factory=list)
    nft_holdings: List[Dict[str, Any]] = Field(default_factory=list)
    total_portfolio_value: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Transaction history
    transaction_count: int = Field(default=0, ge=0)
    last_transaction_date: Optional[datetime] = None
    total_sent: Dict[str, Decimal] = Field(default_factory=dict)
    total_received: Dict[str, Decimal] = Field(default_factory=dict)
    
    # DeFi positions
    defi_protocols_used: List[str] = Field(default_factory=list)
    liquidity_positions: List[Dict[str, Any]] = Field(default_factory=list)
    staking_positions: List[Dict[str, Any]] = Field(default_factory=list)
    lending_positions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Wallet features
    supports_smart_contracts: bool = Field(default=True)
    supports_nfts: bool = Field(default=True)
    supports_defi: bool = Field(default=True)
    hardware_wallet_support: bool = Field(default=False)
    
    # Integration settings
    connected_platforms: List[str] = Field(default_factory=list)
    api_access_enabled: bool = Field(default=False)
    webhook_endpoints: List[HttpUrl] = Field(default_factory=list)
    
    # Privacy and compliance
    privacy_level: str = Field(description="Privacy level setting")
    kyc_verified: bool = Field(default=False)
    aml_compliance: bool = Field(default=True)
    tax_reporting_enabled: bool = Field(default=False)
    
    @validator('wallet_type')
    def validate_wallet_type(cls, v):
        """Validate wallet type."""
        allowed_types = {
            "hot_wallet", "cold_wallet", "hardware_wallet", "multisig_wallet",
            "smart_contract_wallet", "custodial_wallet", "non_custodial_wallet"
        }
        if v not in allowed_types:
            raise ValueError(f'Wallet type must be one of: {", ".join(allowed_types)}')
        return v


class BlockchainTransaction(UUIDSchema, TimestampSchema):
    """Blockchain transaction tracking schema."""
    
    transaction_hash: str = Field(description="Transaction hash")
    blockchain_network: str = Field(description="Blockchain network")
    transaction_type: str = Field(description="Type of transaction")
    
    # Transaction details
    from_address: str = Field(description="Sender address")
    to_address: str = Field(description="Recipient address")
    value: Decimal = Field(ge=0, description="Transaction value")
    currency: str = Field(description="Currency/token")
    
    # Gas and fees
    gas_limit: int = Field(ge=0)
    gas_used: int = Field(ge=0)
    gas_price: Decimal = Field(ge=0)
    transaction_fee: Decimal = Field(ge=0)
    
    # Transaction status
    status: str = Field(description="Transaction status")
    block_number: Optional[int] = Field(None, ge=0)
    block_hash: Optional[str] = None
    transaction_index: Optional[int] = Field(None, ge=0)
    confirmations: int = Field(default=0, ge=0)
    
    # Timing
    submitted_at: datetime = Field(description="Transaction submission time")
    confirmed_at: Optional[datetime] = None
    finalized_at: Optional[datetime] = None
    
    # Smart contract interaction
    contract_address: Optional[str] = None
    function_called: Optional[str] = None
    input_data: Optional[str] = None
    logs: List[Dict[str, Any]] = Field(default_factory=list)
    
    # NFT specific
    token_id: Optional[str] = None
    token_standard: Optional[str] = None
    nft_metadata: Optional[Dict[str, Any]] = None
    
    # Business context
    related_content_id: Optional[UUID] = None
    business_purpose: Optional[str] = None
    internal_reference: Optional[str] = None
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = Field(default=0, ge=0)
    replaced_by: Optional[str] = None
    
    @validator('transaction_type')
    def validate_transaction_type(cls, v):
        """Validate transaction type."""
        allowed_types = {
            "transfer", "nft_mint", "nft_transfer", "contract_deployment",
            "contract_interaction", "token_approval", "staking", "unstaking",
            "swap", "liquidity_provision", "governance_vote", "royalty_payment"
        }
        if v not in allowed_types:
            raise ValueError(f'Transaction type must be one of: {", ".join(allowed_types)}')
        return v


class CryptoPayment(UUIDSchema, TimestampSchema):
    """Cryptocurrency payment processing schema."""
    
    payment_id: str = Field(description="Unique payment identifier")
    payer_id: UUID = Field(description="Payer user ID")
    recipient_id: UUID = Field(description="Recipient user ID")
    payment_purpose: str = Field(description="Purpose of payment")
    
    # Payment details
    amount: Decimal = Field(gt=0, description="Payment amount")
    currency: str = Field(description="Cryptocurrency used")
    exchange_rate: Optional[Decimal] = Field(None, description="Exchange rate to USD")
    usd_equivalent: Optional[Decimal] = Field(None, description="USD equivalent amount")
    
    # Addresses and networks
    payer_address: str = Field(description="Payer wallet address")
    recipient_address: str = Field(description="Recipient wallet address")
    blockchain_network: str = Field(description="Blockchain network used")
    
    # Transaction tracking
    transaction_hash: Optional[str] = None
    payment_status: str = Field(default="pending")
    confirmation_status: str = Field(default="unconfirmed")
    required_confirmations: int = Field(default=6, ge=1)
    
    # Timing
    payment_initiated_at: datetime
    payment_confirmed_at: Optional[datetime] = None
    payment_completed_at: Optional[datetime] = None
    timeout_at: Optional[datetime] = None
    
    # Fees and costs
    network_fee: Decimal = Field(default=Decimal('0.00'), ge=0)
    platform_fee: Decimal = Field(default=Decimal('0.00'), ge=0)
    processing_fee: Decimal = Field(default=Decimal('0.00'), ge=0)
    total_fees: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Payment verification
    payment_proof: Optional[str] = None
    verification_method: str = Field(description="Payment verification method")
    fraud_check_passed: bool = Field(default=True)
    aml_check_passed: bool = Field(default=True)
    
    # Business context
    invoice_id: Optional[str] = None
    order_id: Optional[str] = None
    subscription_id: Optional[UUID] = None
    related_content_id: Optional[UUID] = None
    
    # Refund information
    is_refundable: bool = Field(default=True)
    refund_deadline: Optional[datetime] = None
    refund_status: Optional[str] = None
    refund_transaction_hash: Optional[str] = None
    
    @validator('payment_status')
    def validate_payment_status(cls, v):
        """Validate payment status."""
        allowed_statuses = {
            "pending", "processing", "confirmed", "completed", "failed",
            "cancelled", "expired", "refunded", "partially_refunded"
        }
        if v not in allowed_statuses:
            raise ValueError(f'Payment status must be one of: {", ".join(allowed_statuses)}')
        return v


class DeFiIntegration(UUIDSchema, TimestampSchema):
    """DeFi protocol integration schema."""
    
    protocol_name: str = Field(description="DeFi protocol name")
    protocol_type: str = Field(description="Type of DeFi protocol")
    integration_type: str = Field(description="Integration approach")
    
    # Protocol details
    protocol_contracts: List[str] = Field(description="Protocol contract addresses")
    supported_networks: List[str] = Field(description="Supported blockchain networks")
    protocol_version: str = Field(description="Protocol version")
    
    # Integration configuration
    api_endpoints: List[HttpUrl] = Field(default_factory=list)
    sdk_version: Optional[str] = None
    integration_status: str = Field(default="active")
    
    # Yield farming
    supported_pools: List[Dict[str, Any]] = Field(default_factory=list)
    yield_strategies: List[Dict[str, Any]] = Field(default_factory=list)
    auto_compound_enabled: bool = Field(default=False)
    
    # Staking configuration
    staking_rewards: Dict[str, Any] = Field(default_factory=dict)
    lock_periods: List[int] = Field(default_factory=list)
    reward_tokens: List[str] = Field(default_factory=list)
    
    # Risk management
    risk_assessment: Dict[str, str] = Field(default_factory=dict)
    audit_reports: List[HttpUrl] = Field(default_factory=list)
    insurance_coverage: Optional[Dict[str, Any]] = None
    
    # Performance metrics
    total_value_locked: Decimal = Field(default=Decimal('0.00'), ge=0)
    annual_percentage_yield: Optional[float] = Field(None, ge=0.0)
    historical_performance: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator('protocol_type')
    def validate_protocol_type(cls, v):
        """Validate protocol type."""
        allowed_types = {
            "dex", "lending", "staking", "yield_farming", "liquidity_mining",
            "governance", "insurance", "derivatives", "synthetic_assets", "bridge"
        }
        if v not in allowed_types:
            raise ValueError(f'Protocol type must be one of: {", ".join(allowed_types)}')
        return v
