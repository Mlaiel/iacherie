"""Royalty Configuration Module
===========================

Professional royalty management and distribution system for content creators.
Advanced royalty calculation, split management, and automated distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + Music Industry Expert

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from decimal import Decimal
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class RoyaltyType(str, Enum):
    """Types of royalties in the music and content industry."""
    # Music Royalties
    MECHANICAL = "mechanical"  # Physical/digital reproduction
    PERFORMANCE = "performance"  # Radio, streaming, live performance
    SYNCHRONIZATION = "synchronization"  # TV, film, advertising
    PRINT = "print"  # Sheet music
    MASTER = "master"  # Sound recording rights
    PUBLISHING = "publishing"  # Composition rights
    NEIGHBORING_RIGHTS = "neighboring_rights"  # Related rights
    
    # Digital Content Royalties
    STREAMING = "streaming"  # Digital streaming platforms
    DOWNLOAD = "download"  # Digital downloads
    SUBSCRIPTION = "subscription"  # Subscription-based access
    ADVERTISING = "advertising"  # Ad-supported content
    
    # Content Protection Royalties
    CLAIMED_CONTENT = "claimed_content"  # Content protection claims
    LICENSING_FEES = "licensing_fees"  # Licensing agreements
    SETTLEMENT_FUNDS = "settlement_funds"  # Legal settlements
    
    # Platform-Specific
    YOUTUBE_CONTENT_ID = "youtube_content_id"
    SPOTIFY_STREAMS = "spotify_streams"
    APPLE_MUSIC_STREAMS = "apple_music_streams"
    INSTAGRAM_REELS = "instagram_reels"
    TIKTOK_VIEWS = "tiktok_views"
    
    # Other Revenue Streams
    MERCHANDISE = "merchandise"
    LIVE_PERFORMANCE = "live_performance"
    BRAND_PARTNERSHIPS = "brand_partnerships"
    NFT_SALES = "nft_sales"
    CUSTOM = "custom"


class RoyaltyCalculationMethod(str, Enum):
    """Methods for calculating royalty distributions."""
    PERCENTAGE = "percentage"  # Fixed percentage split
    FIXED_AMOUNT = "fixed_amount"  # Fixed amount per unit
    TIERED = "tiered"  # Different rates based on volume
    WATERFALL = "waterfall"  # Sequential distribution
    PRO_RATA = "pro_rata"  # Proportional distribution
    HYBRID = "hybrid"  # Combination of methods
    CUSTOM_FORMULA = "custom_formula"  # Custom calculation


class RoyaltyRecipientType(str, Enum):
    """Types of royalty recipients."""
    ARTIST = "artist"  # Primary artist/creator
    SONGWRITER = "songwriter"  # Song composer
    PRODUCER = "producer"  # Music producer
    PUBLISHER = "publisher"  # Publishing company
    LABEL = "label"  # Record label
    DISTRIBUTOR = "distributor"  # Distribution company
    MANAGER = "manager"  # Artist manager
    AGENT = "agent"  # Booking agent
    COLLABORATOR = "collaborator"  # Collaborating artist
    SESSION_MUSICIAN = "session_musician"  # Session player
    ENGINEER = "engineer"  # Recording engineer
    PLATFORM = "platform"  # Platform commission
    COLLECTION_SOCIETY = "collection_society"  # PRO/CMO
    CUSTOM = "custom"


class RoyaltyStatus(str, Enum):
    """Status of royalty payments."""
    PENDING = "pending"
    CALCULATED = "calculated"
    APPROVED = "approved"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    DISPUTED = "disputed"
    WITHHELD = "withheld"
    RECOUPED = "recouped"  # Recoupment against advances
    CANCELLED = "cancelled"


class RoyaltyPeriod(str, Enum):
    """Reporting and distribution periods."""
    REAL_TIME = "real_time"  # Instant distribution
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"


@dataclass
class RoyaltyRate:
    """Royalty rate configuration for different scenarios."""
    rate_percentage: Decimal
    minimum_amount: Decimal = Decimal("0.00")
    maximum_amount: Optional[Decimal] = None
    currency: str = "EUR"
    
    # Tier-based rates
    volume_tiers: Dict[int, Decimal] = field(default_factory=dict)  # volume -> rate
    
    # Time-based rates
    effective_from: Optional[datetime] = None
    effective_until: Optional[datetime] = None
    
    # Geographic rates
    territory_specific: Dict[str, Decimal] = field(default_factory=dict)  # country -> rate


@dataclass
class RoyaltySplit:
    """Defines how royalties are split among recipients."""
    recipient_id: str
    recipient_type: RoyaltyRecipientType
    recipient_name: str
    split_percentage: Decimal
    calculation_method: RoyaltyCalculationMethod
    
    # Advanced split configuration
    minimum_threshold: Decimal = Decimal("0.00")
    recoupment_priority: int = 0  # Lower = higher priority
    withholding_tax_rate: Decimal = Decimal("0.00")
    
    # Payment details
    payment_method: Optional[str] = None
    payment_details: Dict[str, Any] = field(default_factory=dict)
    
    # Legal and contractual
    contract_reference: Optional[str] = None
    effective_from: Optional[datetime] = None
    effective_until: Optional[datetime] = None


@dataclass
class RoyaltySource:
    """Configuration for royalty sources/platforms."""
    source_id: str
    source_name: str
    source_type: str  # platform, collection_society, direct
    
    # Revenue configuration
    supported_royalty_types: List[RoyaltyType]
    base_rates: Dict[RoyaltyType, RoyaltyRate]
    
    # Platform-specific settings
    api_integration: bool = False
    api_endpoint: Optional[str] = None
    reporting_frequency: RoyaltyPeriod = RoyaltyPeriod.MONTHLY
    payment_delay_days: int = 30
    
    # Currency and fees
    default_currency: str = "EUR"
    platform_fee_percentage: Decimal = Decimal("0.00")
    transaction_fee: Decimal = Decimal("0.00")
    
    # Minimum thresholds
    minimum_payout_amount: Decimal = Decimal("1.00")
    aggregation_threshold: Decimal = Decimal("0.01")


@dataclass
class RecoupmentSchedule:
    """Advanced recoupment configuration for advances and costs."""
    advance_amount: Decimal
    recoupment_rate: Decimal  # Percentage of royalties to recoup
    recoupable_costs: List[str] = field(default_factory=list)
    non_recoupable_costs: List[str] = field(default_factory=list)
    
    # Recoupment priorities
    cross_collateralization: bool = False  # Recoup from all revenue streams
    recoupment_cap: Optional[Decimal] = None
    interest_rate: Decimal = Decimal("0.00")
    
    # Contractual terms
    recoupment_start_date: Optional[datetime] = None
    recoupment_end_date: Optional[datetime] = None


@dataclass
class RoyaltyConfig:
    """Professional royalty management configuration."""
    
    # Global Royalty Settings
    ENABLE_ROYALTY_SYSTEM: bool = True
    DEFAULT_CURRENCY: str = "EUR"
    DEFAULT_CALCULATION_METHOD: RoyaltyCalculationMethod = RoyaltyCalculationMethod.PERCENTAGE
    DEFAULT_DISTRIBUTION_PERIOD: RoyaltyPeriod = RoyaltyPeriod.MONTHLY
    
    # Minimum Thresholds
    GLOBAL_MINIMUM_PAYOUT: Decimal = Decimal("10.00")
    MICRO_PAYMENT_THRESHOLD: Decimal = Decimal("0.01")  # Below this, accumulate
    
    # Platform Commission
    PLATFORM_COMMISSION_PERCENTAGE: Decimal = Decimal("15.0")  # Platform takes 15%
    
    # Standard Royalty Rates by Type
    STANDARD_ROYALTY_RATES: Dict[RoyaltyType, RoyaltyRate] = field(
        default_factory=lambda: {
            RoyaltyType.STREAMING: RoyaltyRate(
                rate_percentage=Decimal("70.0"),  # 70% to rights holders
                minimum_amount=Decimal("0.001"),
                currency="EUR"
            ),
            RoyaltyType.DOWNLOAD: RoyaltyRate(
                rate_percentage=Decimal("70.0"),
                minimum_amount=Decimal("0.10"),
                currency="EUR"
            ),
            RoyaltyType.MECHANICAL: RoyaltyRate(
                rate_percentage=Decimal("9.1"),  # Standard mechanical rate
                minimum_amount=Decimal("0.091"),
                currency="USD"
            ),
            RoyaltyType.PERFORMANCE: RoyaltyRate(
                rate_percentage=Decimal("50.0"),  # 50/50 split typical
                minimum_amount=Decimal("0.01"),
                currency="EUR"
            ),
            RoyaltyType.SYNCHRONIZATION: RoyaltyRate(
                rate_percentage=Decimal("50.0"),  # Negotiable rate
                minimum_amount=Decimal("1.00"),
                currency="EUR"
            ),
            RoyaltyType.YOUTUBE_CONTENT_ID: RoyaltyRate(
                rate_percentage=Decimal("55.0"),  # YouTube's rate to creators
                minimum_amount=Decimal("0.01"),
                currency="USD"
            ),
            RoyaltyType.CLAIMED_CONTENT: RoyaltyRate(
                rate_percentage=Decimal("90.0"),  # Most goes to rights holder
                minimum_amount=Decimal("0.01"),
                currency="EUR"
            )
        }
    )
    
    # Default Split Templates for Common Scenarios
    SPLIT_TEMPLATES: Dict[str, List[RoyaltySplit]] = field(
        default_factory=lambda: {
            "solo_artist": [
                RoyaltySplit(
                    recipient_id="artist_primary",
                    recipient_type=RoyaltyRecipientType.ARTIST,
                    recipient_name="Primary Artist",
                    split_percentage=Decimal("85.0"),
                    calculation_method=RoyaltyCalculationMethod.PERCENTAGE
                ),
                RoyaltySplit(
                    recipient_id="platform_commission",
                    recipient_type=RoyaltyRecipientType.PLATFORM,
                    recipient_name="Platform Commission",
                    split_percentage=Decimal("15.0"),
                    calculation_method=RoyaltyCalculationMethod.PERCENTAGE
                )
            ],
            "artist_producer_split": [
                RoyaltySplit(
                    recipient_id="artist_primary",
                    recipient_type=RoyaltyRecipientType.ARTIST,
                    recipient_name="Primary Artist",
                    split_percentage=Decimal("70.0"),
                    calculation_method=RoyaltyCalculationMethod.PERCENTAGE
                ),
                RoyaltySplit(
                    recipient_id="producer",
                    recipient_type=RoyaltyRecipientType.PRODUCER,
                    recipient_name="Producer",
                    split_percentage=Decimal("15.0"),
                    calculation_method=RoyaltyCalculationMethod.PERCENTAGE
                ),
                RoyaltySplit(
                    recipient_id="platform_commission",
                    recipient_type=RoyaltyRecipientType.PLATFORM,
                    recipient_name="Platform Commission",
                    split_percentage=Decimal("15.0"),
                    calculation_method=RoyaltyCalculationMethod.PERCENTAGE
                )
            ],
            "collaboration_equal": [
                RoyaltySplit(
                    recipient_id="artist_1",
                    recipient_type=RoyaltyRecipientType.ARTIST,
                    recipient_name="Artist 1",
                    split_percentage=Decimal("42.5"),
                    calculation_method=RoyaltyCalculationMethod.PERCENTAGE
                ),
                RoyaltySplit(
                    recipient_id="artist_2",
                    recipient_type=RoyaltyRecipientType.COLLABORATOR,
                    recipient_name="Artist 2",
                    split_percentage=Decimal("42.5"),
                    calculation_method=RoyaltyCalculationMethod.PERCENTAGE
                ),
                RoyaltySplit(
                    recipient_id="platform_commission",
                    recipient_type=RoyaltyRecipientType.PLATFORM,
                    recipient_name="Platform Commission",
                    split_percentage=Decimal("15.0"),
                    calculation_method=RoyaltyCalculationMethod.PERCENTAGE
                )
            ],
            "label_deal_major": [
                RoyaltySplit(
                    recipient_id="artist_primary",
                    recipient_type=RoyaltyRecipientType.ARTIST,
                    recipient_name="Artist",
                    split_percentage=Decimal("15.0"),  # Artist royalty rate
                    calculation_method=RoyaltyCalculationMethod.PERCENTAGE,
                    recoupment_priority=1
                ),
                RoyaltySplit(
                    recipient_id="record_label",
                    recipient_type=RoyaltyRecipientType.LABEL,
                    recipient_name="Record Label",
                    split_percentage=Decimal("70.0"),
                    calculation_method=RoyaltyCalculationMethod.PERCENTAGE
                ),
                RoyaltySplit(
                    recipient_id="platform_commission",
                    recipient_type=RoyaltyRecipientType.PLATFORM,
                    recipient_name="Platform Commission",
                    split_percentage=Decimal("15.0"),
                    calculation_method=RoyaltyCalculationMethod.PERCENTAGE
                )
            ]
        }
    )
    
    # Royalty Sources Configuration
    ROYALTY_SOURCES: Dict[str, RoyaltySource] = field(
        default_factory=lambda: {
            "spotify": RoyaltySource(
                source_id="spotify",
                source_name="Spotify",
                source_type="platform",
                supported_royalty_types=[RoyaltyType.STREAMING, RoyaltyType.SPOTIFY_STREAMS],
                base_rates={
                    RoyaltyType.STREAMING: RoyaltyRate(
                        rate_percentage=Decimal("70.0"),
                        minimum_amount=Decimal("0.003"),
                        currency="USD"
                    )
                },
                api_integration=True,
                api_endpoint="https://api.spotify.com/v1",
                reporting_frequency=RoyaltyPeriod.MONTHLY,
                payment_delay_days=60,
                minimum_payout_amount=Decimal("10.00")
            ),
            "youtube": RoyaltySource(
                source_id="youtube",
                source_name="YouTube",
                source_type="platform",
                supported_royalty_types=[
                    RoyaltyType.STREAMING, 
                    RoyaltyType.ADVERTISING,
                    RoyaltyType.YOUTUBE_CONTENT_ID
                ],
                base_rates={
                    RoyaltyType.ADVERTISING: RoyaltyRate(
                        rate_percentage=Decimal("55.0"),
                        minimum_amount=Decimal("0.01"),
                        currency="USD"
                    )
                },
                api_integration=True,
                api_endpoint="https://www.googleapis.com/youtube/v3",
                reporting_frequency=RoyaltyPeriod.MONTHLY,
                payment_delay_days=30,
                minimum_payout_amount=Decimal("100.00")  # YouTube's threshold
            ),
            "apple_music": RoyaltySource(
                source_id="apple_music",
                source_name="Apple Music",
                source_type="platform",
                supported_royalty_types=[RoyaltyType.STREAMING, RoyaltyType.APPLE_MUSIC_STREAMS],
                base_rates={
                    RoyaltyType.STREAMING: RoyaltyRate(
                        rate_percentage=Decimal("70.0"),
                        minimum_amount=Decimal("0.006"),
                        currency="USD"
                    )
                },
                reporting_frequency=RoyaltyPeriod.MONTHLY,
                payment_delay_days=45,
                minimum_payout_amount=Decimal("25.00")
            ),
            "content_protection": RoyaltySource(
                source_id="content_protection",
                source_name="Content Protection Claims",
                source_type="direct",
                supported_royalty_types=[
                    RoyaltyType.CLAIMED_CONTENT, 
                    RoyaltyType.LICENSING_FEES,
                    RoyaltyType.SETTLEMENT_FUNDS
                ],
                base_rates={
                    RoyaltyType.CLAIMED_CONTENT: RoyaltyRate(
                        rate_percentage=Decimal("90.0"),
                        minimum_amount=Decimal("0.01"),
                        currency="EUR"
                    )
                },
                reporting_frequency=RoyaltyPeriod.REAL_TIME,
                payment_delay_days=1,
                minimum_payout_amount=Decimal("1.00")
            )
        }
    )
    
    # Advanced Features Configuration
    ADVANCED_FEATURES: Dict[str, Any] = field(default_factory=lambda: {
        # Recoupment and Advances
        "recoupment_enabled": True,
        "cross_collateralization": False,
        "advance_interest_rate": Decimal("0.0"),
        
        # Tax and Legal
        "withholding_tax_enabled": True,
        "international_tax_treaties": True,
        "tax_reporting_enabled": True,
        
        # Currency and Exchange
        "multi_currency_support": True,
        "auto_currency_conversion": True,
        "exchange_rate_provider": "fixer.io",
        "exchange_markup": Decimal("1.0"),
        
        # Performance and Scalability
        "real_time_calculation": False,
        "batch_processing": True,
        "batch_size": 10000,
        "calculation_queue_enabled": True,
        
        # Audit and Compliance
        "audit_trail_enabled": True,
        "transaction_logging": True,
        "compliance_reporting": True,
        "fraud_detection": True,
        
        # Notifications and Reporting
        "payment_notifications": True,
        "statement_generation": True,
        "statement_frequency": RoyaltyPeriod.QUARTERLY,
        "performance_analytics": True
    })
    
    # Collection Society Integration
    COLLECTION_SOCIETIES: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "GEMA": {  # Germany
            "name": "GEMA",
            "country": "DE",
            "royalty_types": [RoyaltyType.PERFORMANCE, RoyaltyType.MECHANICAL],
            "collection_rate": Decimal("10.0"),
            "payment_frequency": RoyaltyPeriod.QUARTERLY,
            "api_integration": False
        },
        "ASCAP": {  # USA
            "name": "ASCAP",
            "country": "US",
            "royalty_types": [RoyaltyType.PERFORMANCE],
            "collection_rate": Decimal("11.5"),
            "payment_frequency": RoyaltyPeriod.QUARTERLY,
            "api_integration": True
        },
        "PRS": {  # UK
            "name": "PRS for Music",
            "country": "GB",
            "royalty_types": [RoyaltyType.PERFORMANCE, RoyaltyType.MECHANICAL],
            "collection_rate": Decimal("12.0"),
            "payment_frequency": RoyaltyPeriod.QUARTERLY,
            "api_integration": True
        },
        "SACEM": {  # France
            "name": "SACEM",
            "country": "FR",
            "royalty_types": [RoyaltyType.PERFORMANCE],
            "collection_rate": Decimal("10.5"),
            "payment_frequency": RoyaltyPeriod.QUARTERLY,
            "api_integration": False
        }
    })
    
    # Business Rules and Validation
    BUSINESS_RULES: Dict[str, Any] = field(default_factory=lambda: {
        "split_percentage_tolerance": Decimal("0.01"),  # Allow 0.01% rounding
        "minimum_split_percentage": Decimal("0.01"),
        "maximum_recipients_per_work": 20,
        "require_split_validation": True,
        "allow_zero_splits": False,
        "require_payment_details": True,
        "automatic_escalation_threshold": Decimal("10000.00"),
        "dispute_resolution_enabled": True,
        "contract_integration": True,
        "metadata_validation": True
    })
    
    def get_royalty_rate(self, royalty_type: RoyaltyType, 
                        source_id: Optional[str] = None) -> RoyaltyRate:
        """Get royalty rate for specific type and source."""
        if source_id and source_id in self.ROYALTY_SOURCES:
            source = self.ROYALTY_SOURCES[source_id]
            if royalty_type in source.base_rates:
                return source.base_rates[royalty_type]
        
        return self.STANDARD_ROYALTY_RATES.get(
            royalty_type, 
            RoyaltyRate(rate_percentage=Decimal("0.0"))
        )
    
    def get_split_template(self, template_name: str) -> List[RoyaltySplit]:
        """Get predefined split template."""
        return self.SPLIT_TEMPLATES.get(template_name, [])
    
    def validate_splits(self, splits: List[RoyaltySplit]) -> Dict[str, Any]:
        """Validate royalty splits for consistency."""
        total_percentage = sum(split.split_percentage for split in splits)
        tolerance = self.BUSINESS_RULES["split_percentage_tolerance"]
        
        validation_result = {
            "valid": True,
            "total_percentage": total_percentage,
            "errors": [],
            "warnings": []
        }
        
        # Check total percentage
        if abs(total_percentage - Decimal("100.0")) > tolerance:
            validation_result["valid"] = False
            validation_result["errors"].append(
                f"Split percentages total {total_percentage}%, must equal 100%"
            )
        
        # Check minimum splits
        min_split = self.BUSINESS_RULES["minimum_split_percentage"]
        for split in splits:
            if split.split_percentage < min_split and split.split_percentage > 0:
                validation_result["warnings"].append(
                    f"Split for {split.recipient_name} is below minimum {min_split}%"
                )
        
        # Check recipient limits
        max_recipients = self.BUSINESS_RULES["maximum_recipients_per_work"]
        if len(splits) > max_recipients:
            validation_result["valid"] = False
            validation_result["errors"].append(
                f"Too many recipients ({len(splits)}), maximum is {max_recipients}"
            )
        
        return validation_result
    
    def calculate_royalty_distribution(self, total_revenue: Decimal, 
                                     splits: List[RoyaltySplit],
                                     royalty_type: RoyaltyType = RoyaltyType.STREAMING) -> Dict[str, Decimal]:
        """Calculate royalty distribution based on splits."""
        distribution = {}
        
        # Apply platform commission first
        net_revenue = total_revenue * (Decimal("100.0") - self.PLATFORM_COMMISSION_PERCENTAGE) / Decimal("100.0")
        
        for split in splits:
            if split.recipient_type == RoyaltyRecipientType.PLATFORM:
                # Platform commission
                amount = total_revenue * self.PLATFORM_COMMISSION_PERCENTAGE / Decimal("100.0")
            else:
                # Calculate recipient share from net revenue
                amount = net_revenue * split.split_percentage / Decimal("100.0")
            
            # Apply minimum thresholds
            if amount < split.minimum_threshold:
                amount = Decimal("0.00")
            
            distribution[split.recipient_id] = amount
        
        return distribution
    
    def get_collection_society_info(self, country_code: str) -> Optional[Dict[str, Any]]:
        """Get collection society information for a country."""
        for society_name, info in self.COLLECTION_SOCIETIES.items():
            if info["country"] == country_code.upper():
                return info
        return None


# Global configuration instance
royalty_config = RoyaltyConfig()

import os
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class RoyaltyType(str, Enum):
    """Types of royalties."""
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    SYNCHRONIZATION = "synchronization"
    MASTER = "master"
    PUBLISHING = "publishing"
    NEIGHBORING = "neighboring"
    DIGITAL = "digital"
    STREAMING = "streaming"
    DOWNLOAD = "download"
    RADIO = "radio"
    TV = "tv"
    LIVE_PERFORMANCE = "live_performance"
    COVER_VERSION = "cover_version"
    REMIX = "remix"
    SAMPLE = "sample"


class RoyaltyCalculationMethod(str, Enum):
    """Methods for calculating royalties."""
    PERCENTAGE = "percentage"
    PER_STREAM = "per_stream"
    PER_DOWNLOAD = "per_download"
    FLAT_RATE = "flat_rate"
    TIERED = "tiered"
    HYBRID = "hybrid"


class DistributionFrequency(str, Enum):
    """Frequency of royalty distributions."""
    REAL_TIME = "real_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"


class RoyaltyStatus(str, Enum):
    """Status of royalty payments."""
    PENDING = "pending"
    CALCULATED = "calculated"
    APPROVED = "approved"
    DISTRIBUTED = "distributed"
    DISPUTED = "disputed"
    WITHHELD = "withheld"
    CANCELLED = "cancelled"


class RightType(str, Enum):
    """Types of rights for royalty collection."""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SHARED = "shared"
    ADMINISTERED = "administered"
    SUB_PUBLISHED = "sub_published"


@dataclass
class RoyaltyRate:
    """Royalty rate configuration."""
    rate_type: RoyaltyType
    calculation_method: RoyaltyCalculationMethod
    rate_value: Decimal
    minimum_amount: Decimal
    maximum_amount: Optional[Decimal]
    currency: str
    effective_date: str
    expiration_date: Optional[str]
    territory: str = "WORLDWIDE"
    platform_specific: bool = False


@dataclass
class PlatformRoyaltyConfig:
    """Platform-specific royalty configuration."""
    platform_name: str
    platform_id: str
    royalty_rates: Dict[RoyaltyType, RoyaltyRate]
    minimum_payout: Decimal
    payout_frequency: DistributionFrequency
    commission_rate: Decimal  # Platform's commission
    currency: str
    supported_territories: List[str]
    reporting_delay_days: int
    payment_delay_days: int


@dataclass
class CollaboratorSplit:
    """Collaborator royalty split configuration."""
    collaborator_id: str
    name: str
    role: str  # composer, lyricist, producer, performer, etc.
    split_percentage: Decimal
    royalty_types: List[RoyaltyType]
    is_featured: bool = False
    advance_recoupable: bool = False
    minimum_guarantee: Decimal = Decimal("0.00")


@dataclass
class TerritoryRoyaltyConfig:
    """Territory-specific royalty configuration."""
    territory_code: str
    territory_name: str
    collection_societies: Dict[RoyaltyType, str]
    royalty_rates: Dict[RoyaltyType, Decimal]
    tax_withholding_rate: Decimal
    currency: str
    minimum_distribution: Decimal
    reporting_requirements: List[str]


@dataclass
class RoyaltyConfig:
    """Main royalty configuration class."""
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "ROYALTY_DB_URL", 
        "postgresql://user:pass@localhost:5432/royalty_db"
    )
    
    # Default Settings
    DEFAULT_CURRENCY: str = "EUR"
    DEFAULT_TERRITORY: str = "WORLDWIDE"
    DEFAULT_DISTRIBUTION_FREQUENCY: DistributionFrequency = DistributionFrequency.MONTHLY
    
    # Global Royalty Rates
    GLOBAL_ROYALTY_RATES: Dict[RoyaltyType, RoyaltyRate] = field(
        default_factory=lambda: {
            RoyaltyType.STREAMING: RoyaltyRate(
                rate_type=RoyaltyType.STREAMING,
                calculation_method=RoyaltyCalculationMethod.PER_STREAM,
                rate_value=Decimal("0.003"),  # €0.003 per stream
                minimum_amount=Decimal("0.001"),
                maximum_amount=None,
                currency="EUR",
                effective_date="2025-01-01",
                expiration_date=None,
                territory="WORLDWIDE"
            ),
            RoyaltyType.DOWNLOAD: RoyaltyRate(
                rate_type=RoyaltyType.DOWNLOAD,
                calculation_method=RoyaltyCalculationMethod.PERCENTAGE,
                rate_value=Decimal("70.0"),  # 70% to artist
                minimum_amount=Decimal("0.10"),
                maximum_amount=None,
                currency="EUR",
                effective_date="2025-01-01",
                expiration_date=None,
                territory="WORLDWIDE"
            ),
            RoyaltyType.MECHANICAL: RoyaltyRate(
                rate_type=RoyaltyType.MECHANICAL,
                calculation_method=RoyaltyCalculationMethod.PER_DOWNLOAD,
                rate_value=Decimal("0.091"),  # US statutory rate
                minimum_amount=Decimal("0.01"),
                maximum_amount=Decimal("0.20"),
                currency="USD",
                effective_date="2025-01-01",
                expiration_date=None,
                territory="US"
            ),
            RoyaltyType.PERFORMANCE: RoyaltyRate(
                rate_type=RoyaltyType.PERFORMANCE,
                calculation_method=RoyaltyCalculationMethod.PERCENTAGE,
                rate_value=Decimal("50.0"),  # 50% to writer/publisher
                minimum_amount=Decimal("0.01"),
                maximum_amount=None,
                currency="EUR",
                effective_date="2025-01-01",
                expiration_date=None,
                territory="WORLDWIDE"
            ),
            RoyaltyType.SYNCHRONIZATION: RoyaltyRate(
                rate_type=RoyaltyType.SYNCHRONIZATION,
                calculation_method=RoyaltyCalculationMethod.FLAT_RATE,
                rate_value=Decimal("500.00"),  # Base sync fee
                minimum_amount=Decimal("100.00"),
                maximum_amount=Decimal("50000.00"),
                currency="EUR",
                effective_date="2025-01-01",
                expiration_date=None,
                territory="WORLDWIDE"
            ),
            RoyaltyType.MASTER: RoyaltyRate(
                rate_type=RoyaltyType.MASTER,
                calculation_method=RoyaltyCalculationMethod.PERCENTAGE,
                rate_value=Decimal("50.0"),  # 50% to master owner
                minimum_amount=Decimal("0.01"),
                maximum_amount=None,
                currency="EUR",
                effective_date="2025-01-01",
                expiration_date=None,
                territory="WORLDWIDE"
            )
        }
    )
    
    # Platform-Specific Royalty Configurations
    PLATFORM_CONFIGS: Dict[str, PlatformRoyaltyConfig] = field(
        default_factory=lambda: {
            "spotify": PlatformRoyaltyConfig(
                platform_name="Spotify",
                platform_id="spotify",
                royalty_rates={
                    RoyaltyType.STREAMING: RoyaltyRate(
                        rate_type=RoyaltyType.STREAMING,
                        calculation_method=RoyaltyCalculationMethod.PER_STREAM,
                        rate_value=Decimal("0.003"),
                        minimum_amount=Decimal("0.001"),
                        maximum_amount=None,
                        currency="EUR",
                        effective_date="2025-01-01",
                        expiration_date=None
                    )
                },
                minimum_payout=Decimal("10.00"),
                payout_frequency=DistributionFrequency.MONTHLY,
                commission_rate=Decimal("15.0"),
                currency="EUR",
                supported_territories=["WORLDWIDE"],
                reporting_delay_days=45,
                payment_delay_days=60
            ),
            "apple_music": PlatformRoyaltyConfig(
                platform_name="Apple Music",
                platform_id="apple_music",
                royalty_rates={
                    RoyaltyType.STREAMING: RoyaltyRate(
                        rate_type=RoyaltyType.STREAMING,
                        calculation_method=RoyaltyCalculationMethod.PER_STREAM,
                        rate_value=Decimal("0.007"),
                        minimum_amount=Decimal("0.001"),
                        maximum_amount=None,
                        currency="USD",
                        effective_date="2025-01-01",
                        expiration_date=None
                    )
                },
                minimum_payout=Decimal("25.00"),
                payout_frequency=DistributionFrequency.MONTHLY,
                commission_rate=Decimal("15.0"),
                currency="USD",
                supported_territories=["WORLDWIDE"],
                reporting_delay_days=60,
                payment_delay_days=90
            ),
            "youtube": PlatformRoyaltyConfig(
                platform_name="YouTube",
                platform_id="youtube",
                royalty_rates={
                    RoyaltyType.STREAMING: RoyaltyRate(
                        rate_type=RoyaltyType.STREAMING,
                        calculation_method=RoyaltyCalculationMethod.PER_STREAM,
                        rate_value=Decimal("0.0015"),
                        minimum_amount=Decimal("0.001"),
                        maximum_amount=None,
                        currency="USD",
                        effective_date="2025-01-01",
                        expiration_date=None
                    )
                },
                minimum_payout=Decimal("100.00"),
                payout_frequency=DistributionFrequency.MONTHLY,
                commission_rate=Decimal("45.0"),  # YouTube's cut is high
                currency="USD",
                supported_territories=["WORLDWIDE"],
                reporting_delay_days=30,
                payment_delay_days=45
            )
        }
    )
    
    # Territory-Specific Configurations
    TERRITORY_CONFIGS: Dict[str, TerritoryRoyaltyConfig] = field(
        default_factory=lambda: {
            "DE": TerritoryRoyaltyConfig(
                territory_code="DE",
                territory_name="Germany",
                collection_societies={
                    RoyaltyType.PERFORMANCE: "GEMA",
                    RoyaltyType.MECHANICAL: "GEMA",
                    RoyaltyType.NEIGHBORING: "GVL"
                },
                royalty_rates={
                    RoyaltyType.PERFORMANCE: Decimal("8.0"),  # 8% of revenue
                    RoyaltyType.MECHANICAL: Decimal("6.25"),  # 6.25% of revenue
                    RoyaltyType.NEIGHBORING: Decimal("20.0")  # 20% of performance royalties
                },
                tax_withholding_rate=Decimal("19.0"),  # German VAT
                currency="EUR",
                minimum_distribution=Decimal("25.00"),
                reporting_requirements=["Monthly reports", "Annual statements"]
            ),
            "US": TerritoryRoyaltyConfig(
                territory_code="US",
                territory_name="United States",
                collection_societies={
                    RoyaltyType.PERFORMANCE: "ASCAP/BMI/SESAC",
                    RoyaltyType.MECHANICAL: "Harry Fox Agency",
                    RoyaltyType.DIGITAL: "SoundExchange"
                },
                royalty_rates={
                    RoyaltyType.PERFORMANCE: Decimal("10.5"),  # 10.5% of revenue
                    RoyaltyType.MECHANICAL: Decimal("9.1"),   # $0.091 per track
                    RoyaltyType.DIGITAL: Decimal("45.0")      # 45% of net revenue
                },
                tax_withholding_rate=Decimal("30.0"),  # Non-resident withholding
                currency="USD",
                minimum_distribution=Decimal("50.00"),
                reporting_requirements=["Quarterly reports", "Annual 1099"]
            ),
            "GB": TerritoryRoyaltyConfig(
                territory_code="GB",
                territory_name="United Kingdom",
                collection_societies={
                    RoyaltyType.PERFORMANCE: "PRS for Music",
                    RoyaltyType.MECHANICAL: "MCPS",
                    RoyaltyType.NEIGHBORING: "PPL"
                },
                royalty_rates={
                    RoyaltyType.PERFORMANCE: Decimal("8.5"),  # 8.5% of revenue
                    RoyaltyType.MECHANICAL: Decimal("6.5"),   # 6.5% of revenue
                    RoyaltyType.NEIGHBORING: Decimal("20.0")  # 20% of performance
                },
                tax_withholding_rate=Decimal("20.0"),  # UK VAT
                currency="GBP",
                minimum_distribution=Decimal("20.00"),
                reporting_requirements=["Monthly reports", "Annual returns"]
            )
        }
    )
    
    # Distribution Configuration
    DISTRIBUTION_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "default_frequency": DistributionFrequency.MONTHLY,
        "minimum_distribution_amount": Decimal("25.00"),
        "hold_period_days": 45,  # Hold before first distribution
        "recoupment_enabled": True,
        "advance_recoupment_rate": Decimal("100.0"),  # 100% recoupment
        "cross_collateralization": False,
        "reserve_percentage": Decimal("15.0"),  # 15% reserve for returns
        "reserve_hold_months": 12,
        "currency_conversion_enabled": True,
        "fx_rate_date": "settlement_date"  # or "accrual_date"
    })
    
    # Reporting Configuration
    REPORTING_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "generate_statements": True,
        "statement_frequency": DistributionFrequency.MONTHLY,
        "detailed_usage_reports": True,
        "territory_breakdowns": True,
        "platform_breakdowns": True,
        "collaborator_statements": True,
        "tax_documents": True,
        "audit_trail_enabled": True,
        "data_retention_years": 7,
        "export_formats": ["PDF", "CSV", "JSON", "XML"]
    })
    
    # Audit and Compliance Configuration
    AUDIT_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "audit_rights_enabled": True,
        "audit_period_years": 3,
        "audit_notice_days": 90,
        "audit_cost_threshold": Decimal("10000.00"),
        "discrepancy_threshold": Decimal("500.00"),
        "compliance_monitoring": True,
        "regulatory_reporting": True,
        "anti_fraud_measures": True,
        "transaction_verification": True
    })
    
    # Advanced Features Configuration
    ADVANCED_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "predictive_earnings": True,
        "trend_analysis": True,
        "comparative_analytics": True,
        "market_intelligence": True,
        "benchmarking": True,
        "forecasting_models": True,
        "ai_powered_insights": True,
        "custom_reporting": True,
        "white_label_statements": True,
        "multi_currency_support": True
    })
    
    def get_platform_config(self, platform_id: str) -> Optional[PlatformRoyaltyConfig]:
        """Get platform-specific royalty configuration."""
        return self.PLATFORM_CONFIGS.get(platform_id.lower())
    
    def get_territory_config(self, territory_code: str) -> Optional[TerritoryRoyaltyConfig]:
        """Get territory-specific royalty configuration."""
        return self.TERRITORY_CONFIGS.get(territory_code.upper())
    
    def get_royalty_rate(
        self, 
        royalty_type: RoyaltyType, 
        platform: Optional[str] = None
    ) -> Optional[RoyaltyRate]:
        """Get royalty rate for a specific type and platform."""
        if platform:
            platform_config = self.get_platform_config(platform)
            if platform_config and royalty_type in platform_config.royalty_rates:
                return platform_config.royalty_rates[royalty_type]
        
        return self.GLOBAL_ROYALTY_RATES.get(royalty_type)
    
    def calculate_royalty_amount(
        self,
        royalty_type: RoyaltyType,
        usage_quantity: Union[int, Decimal],
        gross_revenue: Decimal,
        platform: Optional[str] = None
    ) -> Decimal:
        """Calculate royalty amount based on usage and revenue."""
        rate_config = self.get_royalty_rate(royalty_type, platform)
        if not rate_config:
            return Decimal("0.00")
        
        if rate_config.calculation_method == RoyaltyCalculationMethod.PERCENTAGE:
            amount = gross_revenue * (rate_config.rate_value / Decimal("100"))
        elif rate_config.calculation_method == RoyaltyCalculationMethod.PER_STREAM:
            amount = Decimal(str(usage_quantity)) * rate_config.rate_value
        elif rate_config.calculation_method == RoyaltyCalculationMethod.FLAT_RATE:
            amount = rate_config.rate_value
        else:
            amount = Decimal("0.00")
        
        # Apply minimum and maximum constraints
        if amount < rate_config.minimum_amount:
            amount = rate_config.minimum_amount
        
        if rate_config.maximum_amount and amount > rate_config.maximum_amount:
            amount = rate_config.maximum_amount
        
        return amount.quantize(Decimal("0.01"))
    
    def split_royalty_amount(
        self, 
        total_amount: Decimal, 
        collaborators: List[CollaboratorSplit]
    ) -> Dict[str, Decimal]:
        """Split royalty amount among collaborators."""
        splits = {}
        remaining_amount = total_amount
        
        # Calculate splits
        for collaborator in collaborators:
            split_amount = total_amount * (collaborator.split_percentage / Decimal("100"))
            splits[collaborator.collaborator_id] = split_amount.quantize(Decimal("0.01"))
            remaining_amount -= splits[collaborator.collaborator_id]
        
        # Handle rounding differences by adding to largest split
        if remaining_amount != Decimal("0.00"):
            largest_split_id = max(splits.keys(), key=lambda k: splits[k])
            splits[largest_split_id] += remaining_amount
        
        return splits
    
    def get_tax_withholding_rate(self, territory_code: str) -> Decimal:
        """Get tax withholding rate for a territory."""
        territory_config = self.get_territory_config(territory_code)
        if territory_config:
            return territory_config.tax_withholding_rate
        
        return Decimal("0.00")  # No withholding by default


# Global configuration instance
royalty_config = RoyaltyConfig()
