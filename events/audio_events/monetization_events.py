"""Audio Monetization Events - Industrial Grade Monetization Event Management
============================================================================

This module handles all events related to audio monetization, licensing,
revenue generation, and royalty distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from ..core.base_event import BaseEvent


class LicenseType(Enum):
    """LicenseType class implementation"""
    COMMERCIAL = "commercial"
    NON_COMMERCIAL = "non_commercial"
    SYNC = "sync"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"


class RevenueSource(Enum):
    """RevenueSource class implementation"""
    STREAMING = "streaming"
    DOWNLOAD = "download"
    LICENSING = "licensing"
    SYNC = "sync"
    PERFORMANCE = "performance"


class PaymentStatus(Enum):
    """PaymentStatus class implementation"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class AudioMonetizationStartedEvent(BaseEvent):
    """AudioMonetizationStartedEvent class implementation"""
    user_id: UUID
    file_id: UUID
    monetization_id: UUID
    monetization_type: str
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.monetization.started",
            data={
                "file_id": str(self.file_id),
                "monetization_id": str(self.monetization_id),
                "monetization_type": self.monetization_type
            }
        )


@dataclass
class AudioLicenseCreatedEvent(BaseEvent):
    """AudioLicenseCreatedEvent class implementation"""
    user_id: UUID
    file_id: UUID
    license_id: UUID
    license_type: str
    price: float
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.monetization.license_created",
            data={
                "file_id": str(self.file_id),
                "license_id": str(self.license_id),
                "license_type": self.license_type,
                "price": self.price
            }
        )


@dataclass
class AudioRevenueGeneratedEvent(BaseEvent):
    """AudioRevenueGeneratedEvent class implementation"""
    user_id: UUID
    file_id: UUID
    revenue_id: UUID
    amount: float
    currency: str
    revenue_source: str
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.monetization.revenue_generated",
            data={
                "file_id": str(self.file_id),
                "revenue_id": str(self.revenue_id),
                "amount": self.amount,
                "currency": self.currency,
                "revenue_source": self.revenue_source
            }
        )


@dataclass
class AudioRoyaltyDistributedEvent(BaseEvent):
    """AudioRoyaltyDistributedEvent class implementation"""
    user_id: UUID
    file_id: UUID
    distribution_id: UUID
    total_amount: float
    currency: str
    recipients: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.monetization.royalty_distributed",
            data={
                "file_id": str(self.file_id),
                "distribution_id": str(self.distribution_id),
                "total_amount": self.total_amount,
                "currency": self.currency,
                "recipients_count": len(self.recipients)
            }
        )


@dataclass
class AudioSaleCompletedEvent(BaseEvent):
    """AudioSaleCompletedEvent class implementation"""
    user_id: UUID
    file_id: UUID
    sale_id: UUID
    buyer_id: UUID
    amount: float
    currency: str
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.monetization.sale_completed",
            data={
                "file_id": str(self.file_id),
                "sale_id": str(self.sale_id),
                "buyer_id": str(self.buyer_id),
                "amount": self.amount,
                "currency": self.currency
            }
        )


@dataclass
class AudioStreamingRevenueEvent(BaseEvent):
    """AudioStreamingRevenueEvent class implementation"""
    user_id: UUID
    file_id: UUID
    platform: str
    streams_count: int
    revenue: float
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.monetization.streaming_revenue",
            data={
                "file_id": str(self.file_id),
                "platform": self.platform,
                "streams_count": self.streams_count,
                "revenue": self.revenue
            }
        )


@dataclass
class AudioSyncLicenseRequestEvent(BaseEvent):
    """AudioSyncLicenseRequestEvent class implementation"""
    user_id: UUID
    file_id: UUID
    request_id: UUID
    project_type: str
    requested_usage: str
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.monetization.sync_license_request",
            data={
                "file_id": str(self.file_id),
                "request_id": str(self.request_id),
                "project_type": self.project_type,
                "requested_usage": self.requested_usage
            }
        )


@dataclass
class AudioPerformanceRoyaltyEvent(BaseEvent):
    """AudioPerformanceRoyaltyEvent class implementation"""
    user_id: UUID
    file_id: UUID
    performance_id: UUID
    venue: str
    performance_date: datetime
    royalty_amount: float
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.monetization.performance_royalty",
            data={
                "file_id": str(self.file_id),
                "performance_id": str(self.performance_id),
                "venue": self.venue,
                "royalty_amount": self.royalty_amount
            }
        )


@dataclass
class AudioMonetizationAnalyticsEvent(BaseEvent):
    """AudioMonetizationAnalyticsEvent class implementation"""
    user_id: UUID
    file_id: UUID
    analytics_id: UUID
    total_revenue: float
    revenue_breakdown: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.monetization.analytics",
            data={
                "file_id": str(self.file_id),
                "analytics_id": str(self.analytics_id),
                "total_revenue": self.total_revenue,
                "revenue_sources": list(self.revenue_breakdown.keys())
            }
        )


@dataclass
class AudioNFTMintingEvent(BaseEvent):
    """AudioNFTMintingEvent class implementation"""
    user_id: UUID
    file_id: UUID
    nft_id: UUID
    blockchain: str
    mint_price: float
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.monetization.nft_minting",
            data={
                "file_id": str(self.file_id),
                "nft_id": str(self.nft_id),
                "blockchain": self.blockchain,
                "mint_price": self.mint_price
            }
        )