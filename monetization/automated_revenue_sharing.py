"""Automated Revenue Sharing System
Industrial-grade automated revenue distribution and sharing engine for creators and collaborators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import json
import uuid

logger = logging.getLogger(__name__)


class SharingType(Enum):
    """Revenue sharing types"""
    COLLABORATION = "collaboration"
    PLATFORM_FEE = "platform_fee" 
    CREATOR_ROYALTY = "creator_royalty"
    INFLUENCER_CUT = "influencer_cut"
    BRAND_PARTNERSHIP = "brand_partnership"
    LICENSING_FEE = "licensing_fee"
    PERFORMANCE_BONUS = "performance_bonus"
    REFERRAL_COMMISSION = "referral_commission"


class SharingStatus(Enum):
    """Revenue sharing status"""
    PENDING = "pending"
    CALCULATING = "calculating"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"


@dataclass
class RevenueShare:
    """Revenue share configuration"""
    share_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int = 0
    content_id: int = 0
    sharing_type: SharingType = SharingType.CREATOR_ROYALTY
    percentage: Decimal = Decimal('0.00')
    fixed_amount: Decimal = Decimal('0.00')
    minimum_threshold: Decimal = Decimal('1.00')
    maximum_cap: Optional[Decimal] = None
    currency: str = "EUR"
    created_at: datetime = field(default_factory=datetime.utcnow)
    valid_from: datetime = field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RevenueDistribution:
    """Revenue distribution record"""
    distribution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: int = 0
    total_revenue: Decimal = Decimal('0.00')
    platform_fee: Decimal = Decimal('0.00')
    net_revenue: Decimal = Decimal('0.00')
    shares: List[Dict[str, Any]] = field(default_factory=list)
    status: SharingStatus = SharingStatus.PENDING
    currency: str = "EUR"
    period_start: datetime = field(default_factory=datetime.utcnow)
    period_end: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AutomatedRevenueSharingEngine:
    """Industrial-grade automated revenue sharing engine"""

    def __init__(self):
        self.sharing_rules: Dict[int, List[RevenueShare]] = {}
        self.distributions: Dict[str, RevenueDistribution] = {}
        self.processing_queue: List[str] = []
        
        # Platform configuration
        self.platform_fee_percentage = Decimal('0.05')  # 5% platform fee
        self.minimum_payout_threshold = Decimal('10.00')  # €10 minimum
        self.processing_frequency = timedelta(hours=1)  # Process hourly
        
        # Performance metrics
        self.metrics = {
            "total_distributions": 0,
            "total_revenue_shared": Decimal('0.00'),
            "successful_payouts": 0,
            "failed_payouts": 0,
            "average_processing_time": 0.0
        }

    async def register_revenue_share(
        self, 
        content_id: int, 
        user_id: int,
        sharing_config: Dict[str, Any]
    ) -> RevenueShare:
        """Register new revenue sharing configuration"""
        try:
            share = RevenueShare(
                user_id=user_id,
                content_id=content_id,
                sharing_type=SharingType(sharing_config.get('type', 'creator_royalty')),
                percentage=Decimal(str(sharing_config.get('percentage', 0))),
                fixed_amount=Decimal(str(sharing_config.get('fixed_amount', 0))),
                minimum_threshold=Decimal(str(sharing_config.get('minimum_threshold', 1))),
                maximum_cap=Decimal(str(sharing_config['maximum_cap'])) if sharing_config.get('maximum_cap') else None,
                currency=sharing_config.get('currency', 'EUR'),
                valid_from=datetime.fromisoformat(sharing_config['valid_from']) if sharing_config.get('valid_from') else datetime.utcnow(),
                valid_until=datetime.fromisoformat(sharing_config['valid_until']) if sharing_config.get('valid_until') else None,
                metadata=sharing_config.get('metadata', {})
            )
            
            if content_id not in self.sharing_rules:
                self.sharing_rules[content_id] = []
            
            self.sharing_rules[content_id].append(share)
            
            logger.info(f"Registered revenue share {share.share_id} for content {content_id}")
            return share
            
        except Exception as e:
            logger.error(f"Failed to register revenue share: {str(e)}")
            raise

    async def calculate_revenue_distribution(
        self,
        content_id: int,
        total_revenue: Decimal,
        period_start: datetime,
        period_end: datetime,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RevenueDistribution:
        """Calculate automated revenue distribution"""
        try:
            # Calculate platform fee
            platform_fee = total_revenue * self.platform_fee_percentage
            net_revenue = total_revenue - platform_fee
            
            # Get active revenue shares for content
            shares = self.sharing_rules.get(content_id, [])
            active_shares = [
                share for share in shares
                if share.is_active and 
                share.valid_from <= datetime.utcnow() and
                (share.valid_until is None or share.valid_until >= datetime.utcnow())
            ]
            
            # Calculate individual shares
            calculated_shares = []
            remaining_revenue = net_revenue
            
            for share in active_shares:
                share_amount = Decimal('0.00')
                
                # Calculate percentage-based share
                if share.percentage > 0:
                    share_amount = net_revenue * (share.percentage / Decimal('100'))
                
                # Add fixed amount
                if share.fixed_amount > 0:
                    share_amount += share.fixed_amount
                
                # Apply minimum threshold
                if share_amount < share.minimum_threshold:
                    share_amount = Decimal('0.00')
                
                # Apply maximum cap
                if share.maximum_cap and share_amount > share.maximum_cap:
                    share_amount = share.maximum_cap
                
                # Ensure we don't exceed remaining revenue
                if share_amount > remaining_revenue:
                    share_amount = remaining_revenue
                
                if share_amount > 0:
                    calculated_shares.append({
                        'share_id': share.share_id,
                        'user_id': share.user_id,
                        'sharing_type': share.sharing_type.value,
                        'amount': float(share_amount),
                        'currency': share.currency,
                        'percentage_applied': float(share.percentage),
                        'fixed_amount_applied': float(share.fixed_amount),
                        'metadata': share.metadata
                    })
                    remaining_revenue -= share_amount
            
            # Create distribution record
            distribution = RevenueDistribution(
                content_id=content_id,
                total_revenue=total_revenue,
                platform_fee=platform_fee,
                net_revenue=net_revenue,
                shares=calculated_shares,
                status=SharingStatus.CALCULATING,
                period_start=period_start,
                period_end=period_end,
                metadata=metadata or {}
            )
            
            self.distributions[distribution.distribution_id] = distribution
            
            logger.info(f"Calculated revenue distribution {distribution.distribution_id} for content {content_id}")
            return distribution
            
        except Exception as e:
            logger.error(f"Failed to calculate revenue distribution: {str(e)}")
            raise

    async def process_revenue_distribution(self, distribution_id: str) -> bool:
        """Process and execute revenue distribution"""
        try:
            distribution = self.distributions.get(distribution_id)
            if not distribution:
                raise ValueError(f"Distribution {distribution_id} not found")
            
            distribution.status = SharingStatus.PROCESSING
            processing_start = datetime.utcnow()
            
            # Process each share
            successful_shares = 0
            failed_shares = []
            
            for share in distribution.shares:
                try:
                    # Simulate payment processing
                    await self._process_individual_share(share, distribution)
                    successful_shares += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process share {share['share_id']}: {str(e)}")
                    failed_shares.append({
                        'share_id': share['share_id'],
                        'error': str(e)
                    })
            
            # Update distribution status
            if failed_shares:
                distribution.status = SharingStatus.FAILED
                distribution.metadata['failed_shares'] = failed_shares
            else:
                distribution.status = SharingStatus.COMPLETED
                distribution.processed_at = datetime.utcnow()
                
                # Update metrics
                self.metrics['total_distributions'] += 1
                self.metrics['total_revenue_shared'] += distribution.net_revenue
                self.metrics['successful_payouts'] += successful_shares
                
                processing_time = (datetime.utcnow() - processing_start).total_seconds()
                self.metrics['average_processing_time'] = (
                    (self.metrics['average_processing_time'] * (self.metrics['total_distributions'] - 1) + processing_time) /
                    self.metrics['total_distributions']
                )
            
            logger.info(f"Processed revenue distribution {distribution_id} with status {distribution.status.value}")
            return distribution.status == SharingStatus.COMPLETED
            
        except Exception as e:
            logger.error(f"Failed to process revenue distribution: {str(e)}")
            if distribution_id in self.distributions:
                self.distributions[distribution_id].status = SharingStatus.FAILED
            return False

    async def _process_individual_share(self, share: Dict[str, Any], distribution: RevenueDistribution):
        """Process individual revenue share payment"""
        # Simulate payment processing logic
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # In real implementation, this would:
        # 1. Validate user payment details
        # 2. Create payment transaction
        # 3. Execute payment via payment processor
        # 4. Update user account balance
        # 5. Send notification to user
        # 6. Record transaction in audit log
        
        logger.debug(f"Processed share {share['share_id']} amount {share['amount']} {share['currency']}")

    async def get_revenue_analytics(
        self,
        content_id: Optional[int] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive revenue sharing analytics"""
        try:
            # Filter distributions based on criteria
            filtered_distributions = []
            for dist in self.distributions.values():
                if content_id and dist.content_id != content_id:
                    continue
                if start_date and dist.period_start < start_date:
                    continue
                if end_date and dist.period_end > end_date:
                    continue
                if user_id:
                    # Check if user is involved in any shares
                    user_involved = any(share.get('user_id') == user_id for share in dist.shares)
                    if not user_involved:
                        continue
                
                filtered_distributions.append(dist)
            
            # Calculate analytics
            total_revenue = sum(dist.total_revenue for dist in filtered_distributions)
            total_platform_fees = sum(dist.platform_fee for dist in filtered_distributions)
            total_shared = sum(dist.net_revenue for dist in filtered_distributions)
            
            # Status breakdown
            status_breakdown = {}
            for status in SharingStatus:
                count = len([d for d in filtered_distributions if d.status == status])
                status_breakdown[status.value] = count
            
            # Sharing type breakdown
            sharing_type_breakdown = {}
            for dist in filtered_distributions:
                for share in dist.shares:
                    share_type = share['sharing_type']
                    if share_type not in sharing_type_breakdown:
                        sharing_type_breakdown[share_type] = {
                            'count': 0,
                            'total_amount': 0.0
                        }
                    sharing_type_breakdown[share_type]['count'] += 1
                    sharing_type_breakdown[share_type]['total_amount'] += share['amount']
            
            analytics = {
                'overview': {
                    'total_distributions': len(filtered_distributions),
                    'total_revenue': float(total_revenue),
                    'total_platform_fees': float(total_platform_fees),
                    'total_shared_revenue': float(total_shared),
                    'average_distribution_amount': float(total_shared / len(filtered_distributions)) if filtered_distributions else 0
                },
                'status_breakdown': status_breakdown,
                'sharing_type_breakdown': sharing_type_breakdown,
                'performance_metrics': dict(self.metrics),
                'period': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get revenue analytics: {str(e)}")
            raise

    async def schedule_automated_processing(self):
        """Schedule automated revenue distribution processing"""
        try:
            # Find pending distributions
            pending_distributions = [
                dist_id for dist_id, dist in self.distributions.items()
                if dist.status == SharingStatus.PENDING and
                dist.period_end <= datetime.utcnow()
            ]
            
            # Process each pending distribution
            for dist_id in pending_distributions:
                try:
                    await self.process_revenue_distribution(dist_id)
                except Exception as e:
                    logger.error(f"Failed to process distribution {dist_id}: {str(e)}")
            
            logger.info(f"Processed {len(pending_distributions)} revenue distributions")
            
        except Exception as e:
            logger.error(f"Failed scheduled processing: {str(e)}")

    async def get_user_revenue_summary(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive revenue summary for a user"""
        try:
            user_shares = []
            total_earned = Decimal('0.00')
            
            for dist in self.distributions.values():
                if start_date and dist.period_start < start_date:
                    continue
                if end_date and dist.period_end > end_date:
                    continue
                
                for share in dist.shares:
                    if share.get('user_id') == user_id:
                        user_shares.append({
                            'distribution_id': dist.distribution_id,
                            'content_id': dist.content_id,
                            'share_amount': share['amount'],
                            'sharing_type': share['sharing_type'],
                            'period_start': dist.period_start.isoformat(),
                            'period_end': dist.period_end.isoformat(),
                            'status': dist.status.value,
                            'processed_at': dist.processed_at.isoformat() if dist.processed_at else None
                        })
                        if dist.status == SharingStatus.COMPLETED:
                            total_earned += Decimal(str(share['amount']))
            
            # Group by sharing type
            earnings_by_type = {}
            for share in user_shares:
                share_type = share['sharing_type']
                if share_type not in earnings_by_type:
                    earnings_by_type[share_type] = {
                        'count': 0,
                        'total_amount': 0.0
                    }
                earnings_by_type[share_type]['count'] += 1
                earnings_by_type[share_type]['total_amount'] += share['share_amount']
            
            summary = {
                'user_id': user_id,
                'total_earned': float(total_earned),
                'total_shares': len(user_shares),
                'earnings_by_type': earnings_by_type,
                'recent_shares': sorted(user_shares, key=lambda x: x['period_end'], reverse=True)[:10],
                'period': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get user revenue summary: {str(e)}")
            raise


# Global revenue sharing engine instance
_revenue_sharing_engine = None

def get_revenue_sharing_engine() -> AutomatedRevenueSharingEngine:
    """Get global revenue sharing engine instance"""
    global _revenue_sharing_engine
    if _revenue_sharing_engine is None:
        _revenue_sharing_engine = AutomatedRevenueSharingEngine()
    return _revenue_sharing_engine


async def register_content_revenue_sharing(
    content_id: int,
    sharing_rules: List[Dict[str, Any]]
) -> List[RevenueShare]:
    """Register revenue sharing rules for content"""
    engine = get_revenue_sharing_engine()
    shares = []
    
    for rule in sharing_rules:
        share = await engine.register_revenue_share(
            content_id=content_id,
            user_id=rule['user_id'],
            sharing_config=rule
        )
        shares.append(share)
    
    return shares


async def distribute_content_revenue(
    content_id: int,
    revenue_amount: Decimal,
    period_start: datetime,
    period_end: datetime
) -> RevenueDistribution:
    """Distribute revenue for content automatically"""
    engine = get_revenue_sharing_engine()
    
    # Calculate distribution
    distribution = await engine.calculate_revenue_distribution(
        content_id=content_id,
        total_revenue=revenue_amount,
        period_start=period_start,
        period_end=period_end
    )
    
    # Process distribution
    await engine.process_revenue_distribution(distribution.distribution_id)
    
    return distribution