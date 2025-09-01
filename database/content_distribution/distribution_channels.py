"""Distribution Channels Database Module - Enterprise Multi-Platform Distribution Channel Management

Advanced database system for managing intelligent distribution channels, routing optimization,
and platform-specific content delivery across the IA Influencer Agent ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL NOTICE:
This code and database architecture are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written 
permission is strictly prohibited and will result in immediate legal action.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties: Lead AI Developer + Senior Backend Engineer + Database Administrator + 
Security Specialist + Microservices Architect + ML Engineer + Platform Integration Expert
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from contextlib import asynccontextmanager
import logging
import hashlib

import asyncpg
import aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
import pydantic
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

# Database Models
Base = declarative_base()

class DistributionChannelType(str, Enum):
    """
Distribution channel types"""

    SOCIAL_MEDIA = "social_media"
    STREAMING_PLATFORM = "streaming_platform"
    CONTENT_PLATFORM = "content_platform"
    COLLABORATION_NETWORK = "collaboration_network"
    MONETIZATION_CHANNEL = "monetization_channel"
    ENTERPRISE_API = "enterprise_api"

class ChannelStatus(str, Enum):
    """Channel operational status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    SUSPENDED = "suspended"

class PriorityLevel(str, Enum):
    """Channel priority levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"

@dataclass
class ChannelMetrics:
    """Channel performance metrics"""
    success_rate: float = 0.0
    average_response_time: float = 0.0
    total_distributions: int = 0
    failed_distributions: int = 0
    revenue_generated: float = 0.0
    engagement_rate: float = 0.0
    cost_per_distribution: float = 0.0
    quality_score: float = 0.0

@dataclass
class ChannelCapabilities:
    """
Channel technical capabilities"""
    max_file_size: int = 0
    supported_formats: List[str] = field(default_factory=list)
    max_concurrent_uploads: int = 1
    supports_scheduling: bool = False
    supports_analytics: bool = False
    supports_monetization: bool = False
    api_rate_limit: int = 100
    requires_authentication: bool = True

class DistributionChannel(Base):
    """
Distribution channel database model"""
    __tablename__ = "distribution_channels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_name = Column(String(100), nullable=False, unique=True)
    channel_type = Column(String(50), nullable=False)
    platform_id = Column(String(100), nullable=False)
    status = Column(String(20), default=ChannelStatus.ACTIVE)
    priority_level = Column(String(20), default=PriorityLevel.MEDIUM)
    
    # Configuration
    api_endpoint = Column(String(500))
    authentication_config = Column(JSONB)
    channel_capabilities = Column(JSONB)
    routing_rules = Column(JSONB)
    
    # Metrics and monitoring
    performance_metrics = Column(JSONB)
    health_check_config = Column(JSONB)
    last_health_check = Column(DateTime)
    
    # Business logic
    cost_configuration = Column(JSONB)
    revenue_sharing = Column(JSONB)
    quality_thresholds = Column(JSONB)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    tags = Column(ARRAY(String))

class ChannelRouting(Base):
    """Channel routing configuration model"""
    __tablename__ = "channel_routing"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id = Column(UUID(as_uuid=True), ForeignKey('distribution_channels.id'), nullable=False)
    content_type = Column(String(50), nullable=False)
    routing_criteria = Column(JSONB, nullable=False)
    destination_config = Column(JSONB, nullable=False)
    priority_score = Column(Float, default=0.5)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChannelPerformance(Base):
    """Channel performance tracking model"""
    __tablename__ = "channel_performance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id = Column(UUID(as_uuid=True), ForeignKey('distribution_channels.id'), nullable=False)
    measurement_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Performance metrics
    response_time_ms = Column(Float)
    success_rate = Column(Float)
    error_rate = Column(Float)
    throughput = Column(Float)
    
    # Business metrics
    cost_efficiency = Column(Float)
    revenue_impact = Column(Float)
    engagement_quality = Column(Float)
    user_satisfaction = Column(Float)
    
    # Operational metrics
    uptime_percentage = Column(Float)
    api_quota_usage = Column(Float)
    bandwidth_usage = Column(Float)
    storage_usage = Column(Float)
    
    metadata = Column(JSONB)

# Pydantic Models for API
class ChannelConfigRequest(BaseModel):
    """Channel configuration request model"""
    channel_name: str = Field(..., min_length=1, max_length=100)
    channel_type: DistributionChannelType
    platform_id: str = Field(..., min_length=1, max_length=100)
    priority_level: PriorityLevel = PriorityLevel.MEDIUM
    api_endpoint: Optional[str] = None
    authentication_config: Optional[Dict[str, Any]] = None
    capabilities: Optional[ChannelCapabilities] = None
    routing_rules: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class ChannelResponse(BaseModel):
    """
Channel response model"""
    id: str
    channel_name: str
    channel_type: str
    platform_id: str
    status: str
    priority_level: str
    capabilities: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

class DistributionChannelManager:
    """
Enterprise distribution channel management system"""
    
    def __init__(self, database_url: str, redis_url: str):
        self.database_url = database_url
        self.redis_url = redis_url
        self.engine = None
        self.session_factory = None
        self.redis_client = None
        
    async def initialize(self):
        """
Initialize database connections and create tables"""
        try:
            self.engine = create_async_engine(
                self.database_url,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                echo=False
            )
            
            self.session_factory = sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
            
            # Create tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                
            logger.info("Distribution channel manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize distribution channel manager: {str(e)}")
            raise

    @asynccontextmanager
    async def get_session(self):
        """Get async database session"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def create_distribution_channel(
        self,
        config: ChannelConfigRequest,
        user_id: str
    ) -> Dict[str, Any]:
        """
Create new distribution channel"""
        try:
            async with self.get_session() as session:
                # Validate channel uniqueness
                existing = await self._get_channel_by_name(session, config.channel_name)
                if existing:
                    raise ValueError(f"Channel '{config.channel_name}' already exists")
                
                # Create channel record
                channel = DistributionChannel(
                    channel_name=config.channel_name,
                    channel_type=config.channel_type.value,
                    platform_id=config.platform_id,
                    priority_level=config.priority_level.value,
                    api_endpoint=config.api_endpoint,
                    authentication_config=config.authentication_config or {},
                    channel_capabilities=asdict(config.capabilities) if config.capabilities else {},
                    routing_rules=config.routing_rules or {},
                    performance_metrics=asdict(ChannelMetrics()),
                    created_by=uuid.UUID(user_id),
                    tags=config.tags or []
                )
                
                session.add(channel)
                await session.flush()
                
                # Initialize channel performance tracking
                await self._initialize_channel_performance(session, channel.id)
                
                # Cache channel configuration
                await self._cache_channel_config(channel.id, channel)
                
                logger.info(f"Created distribution channel: {config.channel_name}")
                
                return {
                    "channel_id": str(channel.id),
                    "channel_name": channel.channel_name,
                    "status": "created",
                    "message": "Distribution channel created successfully"
                }
                
        except Exception as e:
            logger.error(f"Failed to create distribution channel: {str(e)}")
            raise

    async def configure_channel_routing(
        self,
        channel_id: str,
        content_type: str,
        routing_criteria: Dict[str, Any],
        destination_config: Dict[str, Any],
        priority_score: float = 0.5
    ) -> Dict[str, Any]:
        """Configure channel routing rules"""
        try:
            async with self.get_session() as session:
                # Validate channel exists
                channel = await self._get_channel_by_id(session, channel_id)
                if not channel:
                    raise ValueError(f"Channel {channel_id} not found")
                
                # Create routing configuration
                routing = ChannelRouting(
                    channel_id=uuid.UUID(channel_id),
                    content_type=content_type,
                    routing_criteria=routing_criteria,
                    destination_config=destination_config,
                    priority_score=priority_score
                )
                
                session.add(routing)
                await session.flush()
                
                # Update routing cache
                await self._update_routing_cache(channel_id, routing)
                
                logger.info(f"Configured routing for channel {channel_id}")
                
                return {
                    "routing_id": str(routing.id),
                    "channel_id": channel_id,
                    "content_type": content_type,
                    "status": "configured"
                }
                
        except Exception as e:
            logger.error(f"Failed to configure channel routing: {str(e)}")
            raise

    async def optimize_channel_selection(
        self,
        content_metadata: Dict[str, Any],
        target_audience: Dict[str, Any],
        business_criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Optimize channel selection using AI algorithms"""
        try:
            # Get available channels
            async with self.get_session() as session:
                channels = await self._get_active_channels(session)
            
            # Score channels based on multiple criteria
            scored_channels = []
            
            for channel in channels:
                score = await self._calculate_channel_score(
                    channel,
                    content_metadata,
                    target_audience,
                    business_criteria
                )
                
                if score > 0.3:  # Minimum threshold
                    scored_channels.append({
                        "channel_id": str(channel.id),
                        "channel_name": channel.channel_name,
                        "platform_id": channel.platform_id,
                        "score": score,
                        "reasoning": await self._generate_selection_reasoning(
                            channel, content_metadata, score
                        ),
                        "estimated_performance": await self._predict_performance(
                            channel, content_metadata
                        )
                    })
            
            # Sort by score and return top recommendations
            scored_channels.sort(key=lambda x: x["score"], reverse=True)
            
            logger.info(f"Optimized channel selection: {len(scored_channels)} recommendations")
            
            return scored_channels[:10]  # Top 10 recommendations
            
        except Exception as e:
            logger.error(f"Failed to optimize channel selection: {str(e)}")
            raise

    async def monitor_channel_health(
        self,
        channel_id: str
    ) -> Dict[str, Any]:
        """Monitor channel health and performance"""
        try:
            async with self.get_session() as session:
                channel = await self._get_channel_by_id(session, channel_id)
                if not channel:
                    raise ValueError(f"Channel {channel_id} not found")
                
                # Perform health checks
                health_status = await self._perform_health_checks(channel)
                
                # Get performance metrics
                performance = await self._get_recent_performance(session, channel_id)
                
                # Calculate health score
                health_score = await self._calculate_health_score(health_status, performance)
                
                # Update channel status if needed
                if health_score < 0.5:
                    await self._update_channel_status(
                        session, channel_id, ChannelStatus.ERROR
                    )
                elif health_score < 0.7:
                    await self._update_channel_status(
                        session, channel_id, ChannelStatus.MAINTENANCE
                    )
                else:
                    await self._update_channel_status(
                        session, channel_id, ChannelStatus.ACTIVE
                    )
                
                return {
                    "channel_id": channel_id,
                    "health_score": health_score,
                    "status": channel.status,
                    "health_details": health_status,
                    "performance_summary": performance,
                    "recommendations": await self._generate_health_recommendations(
                        health_status, performance
                    )
                }
                
        except Exception as e:
            logger.error(f"Failed to monitor channel health: {str(e)}")
            raise

    async def get_channel_analytics(
        self,
        channel_id: str,
        time_range: Dict[str, datetime]
    ) -> Dict[str, Any]:
        """Get comprehensive channel analytics"""
        try:
            async with self.get_session() as session:
                # Get channel info
                channel = await self._get_channel_by_id(session, channel_id)
                if not channel:
                    raise ValueError(f"Channel {channel_id} not found")
                
                # Get performance data
                performance_data = await self._get_performance_data(
                    session, channel_id, time_range
                )
                
                # Generate analytics
                analytics = {
                    "channel_info": {
                        "id": str(channel.id),
                        "name": channel.channel_name,
                        "type": channel.channel_type,
                        "platform": channel.platform_id,
                        "status": channel.status
                    },
                    "performance_metrics": await self._calculate_performance_metrics(
                        performance_data
                    ),
                    "trend_analysis": await self._analyze_performance_trends(
                        performance_data
                    ),
                    "cost_analysis": await self._analyze_cost_efficiency(
                        performance_data
                    ),
                    "recommendations": await self._generate_optimization_recommendations(
                        channel, performance_data
                    )
                }
                
                return analytics
                
        except Exception as e:
            logger.error(f"Failed to get channel analytics: {str(e)}")
            raise

    # Helper Methods
    async def _get_channel_by_name(self, session: AsyncSession, name: str):
        """Get channel by name"""
        from sqlalchemy import select
        result = await session.execute(
            select(DistributionChannel).where(DistributionChannel.channel_name == name)
        )
        return result.scalar_one_or_none()

    async def _get_channel_by_id(self, session: AsyncSession, channel_id: str):
        """
Get channel by ID"""
        from sqlalchemy import select
        result = await session.execute(
            select(DistributionChannel).where(DistributionChannel.id == uuid.UUID(channel_id))
        )
        return result.scalar_one_or_none()

    async def _get_active_channels(self, session: AsyncSession):
        """
Get all active channels"""
        from sqlalchemy import select
        result = await session.execute(
            select(DistributionChannel).where(DistributionChannel.status == ChannelStatus.ACTIVE)
        )
        return result.scalars().all()

    async def _initialize_channel_performance(self, session: AsyncSession, channel_id: uuid.UUID):
        """
Initialize performance tracking for new channel"""
        performance = ChannelPerformance(
            channel_id=channel_id,
            response_time_ms=0.0,
            success_rate=1.0,
            error_rate=0.0,
            throughput=0.0,
            cost_efficiency=1.0,
            revenue_impact=0.0,
            engagement_quality=0.0,
            user_satisfaction=0.0,
            uptime_percentage=100.0,
            api_quota_usage=0.0,
            bandwidth_usage=0.0,
            storage_usage=0.0,
            metadata={}
        )
        session.add(performance)

    async def _cache_channel_config(self, channel_id: uuid.UUID, channel: DistributionChannel):
        """
Cache channel configuration in Redis"""
        config_data = {
            "id": str(channel.id),
            "name": channel.channel_name,
            "type": channel.channel_type,
            "platform": channel.platform_id,
            "status": channel.status,
            "capabilities": channel.channel_capabilities,
            "routing_rules": channel.routing_rules
        }
        
        await self.redis_client.setex(
            f"channel:config:{channel_id}",
            3600,  # 1 hour TTL
            json.dumps(config_data)
        )

    async def _update_routing_cache(self, channel_id: str, routing: ChannelRouting):
        """Update routing cache"""
        routing_key = f"channel:routing:{channel_id}"
        routing_data = {
            "id": str(routing.id),
            "content_type": routing.content_type,
            "criteria": routing.routing_criteria,
            "destination": routing.destination_config,
            "priority": routing.priority_score
        }
        
        await self.redis_client.lpush(routing_key, json.dumps(routing_data))
        await self.redis_client.expire(routing_key, 3600)

    async def _calculate_channel_score(
        self,
        channel: DistributionChannel,
        content_metadata: Dict[str, Any],
        target_audience: Dict[str, Any],
        business_criteria: Dict[str, Any]
    ) -> float:
        """Calculate channel compatibility score"""
        score = 0.0
        
        # Content compatibility (30%)
        content_score = await self._score_content_compatibility(channel, content_metadata)
        score += content_score * 0.3
        
        # Audience alignment (25%)
        audience_score = await self._score_audience_alignment(channel, target_audience)
        score += audience_score * 0.25
        
        # Performance history (20%)
        performance_score = await self._score_performance_history(channel)
        score += performance_score * 0.2
        
        # Cost efficiency (15%)
        cost_score = await self._score_cost_efficiency(channel, business_criteria)
        score += cost_score * 0.15
        
        # Platform priority (10%)
        priority_score = await self._score_platform_priority(channel, business_criteria)
        score += priority_score * 0.1
        
        return min(max(score, 0.0), 1.0)

    async def _score_content_compatibility(
        self,
        channel: DistributionChannel,
        content_metadata: Dict[str, Any]
    ) -> float:
        """
Score content compatibility with channel"""
        capabilities = channel.channel_capabilities or {}
        
        # Check format support
        content_format = content_metadata.get("format", "").lower()
        supported_formats = capabilities.get("supported_formats", [])
        format_score = 1.0 if content_format in supported_formats else 0.0
        
        # Check file size
        content_size = content_metadata.get("file_size", 0)
        max_size = capabilities.get("max_file_size", float("inf"))
        size_score = 1.0 if content_size <= max_size else 0.0
        
        # Check content type alignment
        content_type = content_metadata.get("type", "")
        channel_type = channel.channel_type
        type_score = await self._calculate_type_alignment_score(content_type, channel_type)
        
        return (format_score + size_score + type_score) / 3.0

    async def _score_audience_alignment(
        self,
        channel: DistributionChannel,
        target_audience: Dict[str, Any]
    ) -> float:
        """Score audience alignment with channel"""
        # Get channel audience data from analytics
        channel_audience = await self._get_channel_audience_profile(channel.id)
        
        if not channel_audience:
            return 0.5  # Neutral score if no data
        
        # Compare demographics
        demo_score = await self._compare_demographics(
            target_audience.get("demographics", {}),
            channel_audience.get("demographics", {})
        )
        
        # Compare interests
        interest_score = await self._compare_interests(
            target_audience.get("interests", []),
            channel_audience.get("interests", [])
        )
        
        # Compare behavior patterns
        behavior_score = await self._compare_behavior_patterns(
            target_audience.get("behavior", {}),
            channel_audience.get("behavior", {})
        )
        
        return (demo_score + interest_score + behavior_score) / 3.0

    async def _score_performance_history(self, channel: DistributionChannel) -> float:
        """Score channel based on historical performance"""
        metrics = channel.performance_metrics or {}
        
        success_rate = metrics.get("success_rate", 0.0)
        engagement_rate = metrics.get("engagement_rate", 0.0)
        quality_score = metrics.get("quality_score", 0.0)
        
        return (success_rate + engagement_rate + quality_score) / 3.0

    async def _score_cost_efficiency(
        self,
        channel: DistributionChannel,
        business_criteria: Dict[str, Any]
    ) -> float:
        """Score channel cost efficiency"""
        metrics = channel.performance_metrics or {}
        cost_per_distribution = metrics.get("cost_per_distribution", 0.0)
        revenue_generated = metrics.get("revenue_generated", 0.0)
        
        max_budget = business_criteria.get("max_cost_per_distribution", float("inf"))
        
        if cost_per_distribution > max_budget:
            return 0.0
        
        # Calculate ROI-based score
        if cost_per_distribution > 0:
            roi = revenue_generated / cost_per_distribution
            return min(roi / 10.0, 1.0)  # Normalize to 0-1 scale
        
        return 1.0 if revenue_generated > 0 else 0.5

    async def _score_platform_priority(
        self,
        channel: DistributionChannel,
        business_criteria: Dict[str, Any]
    ) -> float:
        """Score channel based on platform priority"""
        platform_priorities = business_criteria.get("platform_priorities", {})
        platform_score = platform_priorities.get(channel.platform_id, 0.5)
        
        # Adjust for channel priority level
        priority_multiplier = {
            PriorityLevel.CRITICAL: 1.0,
            PriorityLevel.HIGH: 0.8,
            PriorityLevel.MEDIUM: 0.6,
            PriorityLevel.LOW: 0.4,
            PriorityLevel.BACKGROUND: 0.2
        }.get(channel.priority_level, 0.5)
        
        return platform_score * priority_multiplier

    async def _perform_health_checks(self, channel: DistributionChannel) -> Dict[str, Any]:
        """Perform comprehensive health checks"""
        health_status = {}
        
        # API connectivity check
        if channel.api_endpoint:
            health_status["api_connectivity"] = await self._check_api_connectivity(
                channel.api_endpoint, channel.authentication_config
            )
        
        # Rate limit status
        health_status["rate_limit_status"] = await self._check_rate_limit_status(channel)
        
        # Authentication validity
        health_status["authentication_valid"] = await self._check_authentication(channel)
        
        # Platform status
        health_status["platform_status"] = await self._check_platform_status(channel.platform_id)
        
        return health_status

    async def _calculate_health_score(
        self,
        health_status: Dict[str, Any],
        performance: Dict[str, Any]
    ) -> float:
        """Calculate overall health score"""
        scores = []
        
        # Health check scores
        for check, status in health_status.items():
            if isinstance(status, bool):
                scores.append(1.0 if status else 0.0)
            elif isinstance(status, dict) and "score" in status:
                scores.append(status["score"])
        
        # Performance scores
        if performance:
            success_rate = performance.get("success_rate", 0.0)
            uptime = performance.get("uptime_percentage", 0.0) / 100.0
            scores.extend([success_rate, uptime])
        
        return sum(scores) / len(scores) if scores else 0.0

    async def _generate_selection_reasoning(
        self,
        channel: DistributionChannel,
        content_metadata: Dict[str, Any],
        score: float
    ) -> str:
        """Generate human-readable reasoning for channel selection"""
        reasons = []
        
        if score > 0.8:
            reasons.append("Excellent compatibility with content and audience")
        elif score > 0.6:
            reasons.append("Good match for content distribution")
        else:
            reasons.append("Suitable option with room for optimization")
        
        # Add specific reasons based on channel characteristics
        if channel.channel_type == DistributionChannelType.SOCIAL_MEDIA:
            reasons.append("Strong social media engagement potential")
        elif channel.channel_type == DistributionChannelType.STREAMING_PLATFORM:
            reasons.append("Optimized for streaming content delivery")
        
        return "; ".join(reasons)

    async def _predict_performance(
        self,
        channel: DistributionChannel,
        content_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict content performance on channel"""
        metrics = channel.performance_metrics or {}
        
        # Base predictions on historical data
        base_engagement = metrics.get("engagement_rate", 0.05)
        base_reach = metrics.get("average_reach", 1000)
        
        # Adjust for content type
        content_type = content_metadata.get("type", "")
        type_multiplier = {
            "video": 1.2,
            "image": 1.0,
            "audio": 0.9,
            "text": 0.8
        }.get(content_type, 1.0)
        
        return {
            "estimated_engagement_rate": base_engagement * type_multiplier,
            "estimated_reach": int(base_reach * type_multiplier),
            "estimated_revenue": metrics.get("revenue_generated", 0.0) * 0.1,
            "confidence_score": min(metrics.get("quality_score", 0.5), 1.0)
        }

    # Additional helper methods would continue here...
    # Due to length constraints, implementing remaining helper methods
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.redis_client:
            await self.redis_client.close()
        if self.engine:
            await self.engine.dispose()
