"""
Commission Calculator System
Advanced commission structure management and calculation engine

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field


class CommissionType(Enum):
    """Types of commission structures"""
    PERCENTAGE = "percentage"
    FLAT_RATE = "flat_rate"
    TIERED = "tiered"
    PERFORMANCE_BASED = "performance_based"
    HYBRID = "hybrid"


class TierCriteria(Enum):
    """Criteria for tiered commissions"""
    REVENUE_AMOUNT = "revenue_amount"
    TRANSACTION_COUNT = "transaction_count"
    USER_LEVEL = "user_level"
    PLATFORM_PERFORMANCE = "platform_performance"
    CONTENT_QUALITY = "content_quality"


@dataclass
class CommissionTier:
    """Individual commission tier definition"""
    tier_name: str
    min_threshold: Decimal
    max_threshold: Optional[Decimal]
    commission_rate: Decimal
    flat_fee: Optional[Decimal] = None
    bonus_rate: Optional[Decimal] = None
    
    def applies_to_amount(self, amount: Decimal) -> bool:
        """Check if tier applies to given amount"""
        if amount < self.min_threshold:
            return False
        if self.max_threshold and amount > self.max_threshold:
            return False
        return True


@dataclass 
class CommissionStructure:
    """Complete commission structure definition"""
    structure_id: str
    name: str
    description: str
    commission_type: CommissionType
    base_percentage: Decimal = Decimal("15.0")
    flat_rate: Optional[Decimal] = None
    tiers: List[CommissionTier] = field(default_factory=list)
    performance_multipliers: Dict[str, Decimal] = field(default_factory=dict)
    minimum_commission: Decimal = Decimal("0.50")
    maximum_commission: Optional[Decimal] = None
    effective_date: datetime = field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = None
    
    def is_active(self) -> bool:
        """Check if commission structure is currently active"""
        now = datetime.now()
        if now < self.effective_date:
            return False
        if self.expiry_date and now > self.expiry_date:
            return False
        return True


class CommissionCalculationRequest(BaseModel):
    """Request for commission calculation"""
    user_id: int
    revenue_amount: Decimal = Field(..., gt=0)
    platform: str
    content_type: str
    transaction_count: int = 1
    user_tier: Optional[str] = None
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    custom_parameters: Dict[str, Any] = Field(default_factory=dict)


class CommissionResult(BaseModel):
    """Commission calculation result"""
    gross_revenue: Decimal
    commission_amount: Decimal
    commission_rate: Decimal
    net_revenue: Decimal
    tier_applied: Optional[str] = None
    calculation_breakdown: Dict[str, Any]
    bonuses_applied: List[Dict[str, Any]] = Field(default_factory=list)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get calculation summary"""



        return {
            "gross_revenue": float(self.gross_revenue),
            "commission_amount": float(self.commission_amount),
            "commission_rate": float(self.commission_rate),
            "net_revenue": float(self.net_revenue),
            "tier_applied": self.tier_applied,
            "bonuses_count": len(self.bonuses_applied)
        }


class CommissionCalculator:
    """Advanced commission calculation engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.commission_structures: Dict[str, CommissionStructure] = {}
        self._initialize_default_structures()
        
    def _initialize_default_structures(self) -> None:
        """Initialize default commission structures"""
        
        # Standard percentage structure
        standard = CommissionStructure(
            structure_id="standard",
            name="Standard Commission",
            description="Standard 15% commission on all revenue",
            commission_type=CommissionType.PERCENTAGE,
            base_percentage=Decimal("15.0")
        )
        
        # Tiered structure for high-volume creators
        tiered = CommissionStructure(
            structure_id="tiered",
            name="Tiered Commission",
            description="Tiered commission based on revenue volume",
            commission_type=CommissionType.TIERED,
            base_percentage=Decimal("15.0"),
            tiers=[
                CommissionTier(
                    tier_name="Bronze",
                    min_threshold=Decimal("0"),
                    max_threshold=Decimal("1000"),
                    commission_rate=Decimal("15.0")
                ),
                CommissionTier(
                    tier_name="Silver", 
                    min_threshold=Decimal("1000"),
                    max_threshold=Decimal("5000"),
                    commission_rate=Decimal("12.0")
                ),
                CommissionTier(
                    tier_name="Gold",
                    min_threshold=Decimal("5000"),
                    max_threshold=Decimal("20000"),
                    commission_rate=Decimal("10.0")
                ),
                CommissionTier(
                    tier_name="Platinum",
                    min_threshold=Decimal("20000"),
                    max_threshold=None,
                    commission_rate=Decimal("8.0")
                )
            ]
        )
        
        # Performance-based structure
        performance = CommissionStructure(
            structure_id="performance",
            name="Performance-Based Commission",
            description="Commission adjusted based on performance metrics",
            commission_type=CommissionType.PERFORMANCE_BASED,
            base_percentage=Decimal("15.0"),
            performance_multipliers={
                "high_engagement": Decimal("0.8"),  # 20% reduction for high engagement
                "exclusive_content": Decimal("0.7"), # 30% reduction for exclusive content
                "consistent_creator": Decimal("0.9")  # 10% reduction for consistency
            }
        )
        
        self.commission_structures["standard"] = standard
        self.commission_structures["tiered"] = tiered
        self.commission_structures["performance"] = performance
    
    async def calculate_commission(
        self,
        request: CommissionCalculationRequest,
        structure_id: str = "standard",
        session: Optional[AsyncSession] = None
    ) -> CommissionResult:
        """Calculate commission based on structure and request parameters"""



        try:
            # Get commission structure
            structure = self.commission_structures.get(structure_id)
            if not structure or not structure.is_active():
                structure = self.commission_structures["standard"]  # Fallback
            
            # Calculate base commission
            if structure.commission_type == CommissionType.PERCENTAGE:
                commission_amount = await self._calculate_percentage_commission(
                    request, structure
                )
                commission_rate = structure.base_percentage
                tier_applied = None
                
            elif structure.commission_type == CommissionType.TIERED:
                commission_amount, commission_rate, tier_applied = await self._calculate_tiered_commission(
                    request, structure
                )
                
            elif structure.commission_type == CommissionType.PERFORMANCE_BASED:
                commission_amount, commission_rate = await self._calculate_performance_commission(
                    request, structure
                )
                tier_applied = None
                
            elif structure.commission_type == CommissionType.FLAT_RATE:
                commission_amount = structure.flat_rate or Decimal("10.0")
                commission_rate = (commission_amount / request.revenue_amount) * 100
                tier_applied = None
                
            else:
                # Hybrid or other types - fallback to percentage
                commission_amount = await self._calculate_percentage_commission(
                    request, structure
                )
                commission_rate = structure.base_percentage
                tier_applied = None
            
            # Apply minimum/maximum limits
            if commission_amount < structure.minimum_commission:
                commission_amount = structure.minimum_commission
            
            if structure.maximum_commission and commission_amount > structure.maximum_commission:
                commission_amount = structure.maximum_commission
            
            # Calculate bonuses
            bonuses = await self._calculate_bonuses(request, structure)
            total_bonus = sum(bonus["amount"] for bonus in bonuses)
            
            # Final commission amount (reduced by bonuses)
            final_commission = commission_amount - total_bonus
            final_commission = max(final_commission, structure.minimum_commission)
            
            # Calculate net revenue
            net_revenue = request.revenue_amount - final_commission
            
            # Create detailed breakdown
            breakdown = {
                "base_commission": float(commission_amount),
                "bonuses_applied": float(total_bonus),
                "final_commission": float(final_commission),
                "structure_used": structure.name,
                "calculation_method": structure.commission_type.value,
                "performance_adjustments": self._get_performance_adjustments(request, structure)
            }
            
            return CommissionResult(
                gross_revenue=request.revenue_amount,
                commission_amount=final_commission.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                commission_rate=commission_rate,
                net_revenue=net_revenue.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                tier_applied=tier_applied,
                calculation_breakdown=breakdown,
                bonuses_applied=bonuses
            )
            
        except Exception as e:
            self.logger.error(f"Commission calculation failed: {str(e)}")
            raise
    
    async def _calculate_percentage_commission(
        self,
        request: CommissionCalculationRequest,
        structure: CommissionStructure
    ) -> Decimal:
        """Calculate simple percentage-based commission"""



        return request.revenue_amount * (structure.base_percentage / 100)
    
    async def _calculate_tiered_commission(
        self,
        request: CommissionCalculationRequest,
        structure: CommissionStructure
    ) -> tuple[Decimal, Decimal, str]:
        """Calculate tiered commission based on revenue amount"""
        total_commission = Decimal("0")
        remaining_amount = request.revenue_amount
        applied_tier = None
        weighted_rate = Decimal("0")
        
        for tier in sorted(structure.tiers, key=lambda t: t.min_threshold):
            if remaining_amount <= 0:
                break
                
            # Calculate amount for this tier
            tier_min = tier.min_threshold
            tier_max = tier.max_threshold or request.revenue_amount
            
            # Amount that falls within this tier
            tier_amount = min(remaining_amount, tier_max - tier_min)
            
            if tier_amount > 0:
                tier_commission = tier_amount * (tier.commission_rate / 100)
                total_commission += tier_commission
                
                # Track the highest tier applied
                if not applied_tier or tier.min_threshold > structure.tiers[0].min_threshold:
                    applied_tier = tier.tier_name
                
                # Calculate weighted average rate
                weighted_rate += (tier.commission_rate * tier_amount) / request.revenue_amount
                
                remaining_amount -= tier_amount
        
        return total_commission, weighted_rate, applied_tier
    
    async def _calculate_performance_commission(
        self,
        request: CommissionCalculationRequest,
        structure: CommissionStructure
    ) -> tuple[Decimal, Decimal]:
        """Calculate performance-based commission with multipliers"""
        base_commission = request.revenue_amount * (structure.base_percentage / 100)
        performance_factor = Decimal("1.0")
        
        # Apply performance multipliers
        for metric, value in request.performance_metrics.items():
            multiplier = structure.performance_multipliers.get(metric)
            if multiplier:
                # Convert performance value to multiplier factor
                if value > 0.8:  # High performance threshold
                    performance_factor *= multiplier
        
        # Platform-specific adjustments
        platform_adjustments = {
            "spotify": Decimal("0.95"),  # 5% reduction for Spotify
            "youtube": Decimal("0.90"),  # 10% reduction for YouTube
            "instagram": Decimal("0.85"), # 15% reduction for Instagram
            "tiktok": Decimal("0.80")    # 20% reduction for TikTok
        }
        
        platform_factor = platform_adjustments.get(request.platform.lower(), Decimal("1.0"))
        
        # Content type adjustments
        content_adjustments = {
            "music": Decimal("0.90"),    # 10% reduction for music
            "podcast": Decimal("0.95"),  # 5% reduction for podcasts
            "video": Decimal("1.0"),     # No adjustment for video
            "image": Decimal("1.05")     # 5% increase for images
        }
        
        content_factor = content_adjustments.get(request.content_type.lower(), Decimal("1.0"))
        
        # Calculate final commission
        final_commission = base_commission * performance_factor * platform_factor * content_factor
        
        # Calculate effective rate
        effective_rate = (final_commission / request.revenue_amount) * 100
        
        return final_commission, effective_rate
    
    async def _calculate_bonuses(
        self,
        request: CommissionCalculationRequest,
        structure: CommissionStructure
    ) -> List[Dict[str, Any]]:
        """Calculate bonus reductions to commission"""
        bonuses = []
        
        # Volume bonus (for high transaction counts)
        if request.transaction_count > 100:
            volume_bonus = request.revenue_amount * Decimal("0.01")  # 1% bonus
            bonuses.append({
                "type": "volume_bonus",
                "description": f"High volume bonus ({request.transaction_count} transactions)",
                "amount": float(volume_bonus),
                "percentage": 1.0
            })
        
        # Loyalty bonus (would require user history data)
        if request.user_tier == "premium":
            loyalty_bonus = request.revenue_amount * Decimal("0.005")  # 0.5% bonus
            bonuses.append({
                "type": "loyalty_bonus",
                "description": "Premium user loyalty bonus",
                "amount": float(loyalty_bonus),
                "percentage": 0.5
            })
        
        # Engagement bonus
        engagement_rate = request.performance_metrics.get("engagement_rate", 0)
        if engagement_rate > 0.1:  # 10% engagement rate
            engagement_bonus = request.revenue_amount * Decimal("0.0075")  # 0.75% bonus
            bonuses.append({
                "type": "engagement_bonus",
                "description": f"High engagement bonus ({engagement_rate:.1%})",
                "amount": float(engagement_bonus),
                "percentage": 0.75
            })
        
        return bonuses
    
    def _get_performance_adjustments(
        self,
        request: CommissionCalculationRequest,
        structure: CommissionStructure
    ) -> Dict[str, Any]:
        """Get detailed performance adjustments applied"""
        adjustments = {}
        
        for metric, value in request.performance_metrics.items():
            if metric in structure.performance_multipliers:
                adjustments[metric] = {
                    "value": value,
                    "multiplier": float(structure.performance_multipliers[metric]),
                    "applied": value > 0.8
                }
        
        return adjustments
    
    async def calculate_monthly_commission_summary(
        self,
        user_id: int,
        month: datetime,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Calculate comprehensive monthly commission summary"""



        try:
            from ...database.models import RevenueRecord
            from sqlalchemy import select, func
            
            # Get month boundaries
            start_date = month.replace(day=1)
            if month.month == 12:
                end_date = month.replace(year=month.year + 1, month=1, day=1)
            else:
                end_date = month.replace(month=month.month + 1, day=1)
            
            # Get revenue records for the month
            result = await session.execute(
                select(
                    RevenueRecord.platform,
                    RevenueRecord.source,
                    func.sum(RevenueRecord.amount).label('total_amount'),
                    func.count(RevenueRecord.id).label('transaction_count'),
                    func.avg(RevenueRecord.amount).label('avg_amount')
                ).where(
                    RevenueRecord.user_id == user_id,
                    RevenueRecord.date >= start_date,
                    RevenueRecord.date < end_date,
                    RevenueRecord.status == "confirmed"
                ).group_by(RevenueRecord.platform, RevenueRecord.source)
            )
            
            platform_summaries = []
            total_gross_revenue = Decimal("0")
            total_commission = Decimal("0")
            
            for row in result:
                # Create calculation request for this platform/source combination
                calculation_request = CommissionCalculationRequest(
                    user_id=user_id,
                    revenue_amount=Decimal(str(row.total_amount)),
                    platform=row.platform,
                    content_type=row.source,
                    transaction_count=row.transaction_count,
                    performance_metrics={}  # Would get from analytics
                )
                
                # Calculate commission
                commission_result = await self.calculate_commission(
                    calculation_request, "tiered", session
                )
                
                platform_summaries.append({
                    "platform": row.platform,
                    "source": row.source,
                    "gross_revenue": float(row.total_amount),
                    "commission_amount": float(commission_result.commission_amount),
                    "commission_rate": float(commission_result.commission_rate),
                    "net_revenue": float(commission_result.net_revenue),
                    "transaction_count": row.transaction_count,
                    "average_transaction": float(row.avg_amount),
                    "tier_applied": commission_result.tier_applied
                })
                
                total_gross_revenue += Decimal(str(row.total_amount))
                total_commission += commission_result.commission_amount
            
            return {
                "user_id": user_id,
                "month": month.strftime("%Y-%m"),
                "summary": {
                    "total_gross_revenue": float(total_gross_revenue),
                    "total_commission": float(total_commission),
                    "total_net_revenue": float(total_gross_revenue - total_commission),
                    "effective_commission_rate": float((total_commission / total_gross_revenue) * 100) if total_gross_revenue > 0 else 0,
                    "platform_count": len(set(p["platform"] for p in platform_summaries))
                },
                "platform_breakdown": platform_summaries
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate monthly commission summary: {str(e)}")
            return {}
    
    def add_commission_structure(self, structure: CommissionStructure) -> None:
        """Add new commission structure"""
        self.commission_structures[structure.structure_id] = structure
        self.logger.info(f"Added commission structure: {structure.name}")
    
    def get_available_structures(self) -> List[Dict[str, Any]]:
        """Get list of available commission structures"""



        return [
            {
                "structure_id": structure.structure_id,
                "name": structure.name,
                "description": structure.description,
                "type": structure.commission_type.value,
                "base_rate": float(structure.base_percentage),
                "is_active": structure.is_active(),
                "tier_count": len(structure.tiers)
            }
            for structure in self.commission_structures.values()
        ]
    
    async def simulate_commission_scenarios(
        self,
        revenue_amounts: List[Decimal],
        structure_ids: List[str]
    ) -> Dict[str, Any]:
        """Simulate commission calculations for different scenarios"""
        scenarios = {}
        
        for structure_id in structure_ids:
            structure_scenarios = []
            
            for amount in revenue_amounts:
                # Create mock request
                request = CommissionCalculationRequest(
                    user_id=1,  # Mock user ID
                    revenue_amount=amount,
                    platform="spotify",
                    content_type="music"
                )
                
                # Calculate commission
                result = await self.calculate_commission(request, structure_id)
                
                structure_scenarios.append({
                    "revenue_amount": float(amount),
                    "commission_amount": float(result.commission_amount),
                    "commission_rate": float(result.commission_rate),
                    "net_revenue": float(result.net_revenue),
                    "tier_applied": result.tier_applied
                })
            
            scenarios[structure_id] = {
                "structure_name": self.commission_structures[structure_id].name,
                "scenarios": structure_scenarios
            }
        
        return scenarios
