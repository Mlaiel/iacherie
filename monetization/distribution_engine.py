"""
Distribution Engine
Automated revenue distribution and multi-creator payment system.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid
import logging

logger = logging.getLogger(__name__)


class DistributionType(Enum):
    """Distribution types"""
    EQUAL_SPLIT = "equal_split"
    PERCENTAGE_BASED = "percentage_based"
    CONTRIBUTION_BASED = "contribution_based"
    ROLE_BASED = "role_based"
    HYBRID = "hybrid"


class PayoutSchedule(Enum):
    """Payout schedule options"""
    IMMEDIATE = "immediate"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


@dataclass
class Contributor:
    """Content contributor structure"""
    user_id: str
    role: str
    contribution_percentage: float
    revenue_share: float
    minimum_payout: float = 5.0
    preferred_currency: str = "EUR"
    tax_country: str = "DE"
    payment_details: Optional[Dict] = None


@dataclass
class DistributionRule:
    """Revenue distribution rules"""
    content_id: str
    distribution_type: DistributionType
    contributors: List[Contributor]
    platform_fee: float = 0.10  # 10% platform fee
    reserve_percentage: float = 0.05  # 5% reserve for disputes
    payout_schedule: PayoutSchedule = PayoutSchedule.MONTHLY
    minimum_threshold: float = 10.0
    created_at: Optional[datetime] = None


@dataclass
class DistributionEvent:
    """Distribution event record"""
    id: str
    content_id: str
    total_revenue: float
    platform_revenue: float
    reserved_amount: float
    distributed_amount: float
    contributor_payouts: List[Dict]
    period_start: datetime
    period_end: datetime
    processed_at: Optional[datetime] = None
    status: str = "pending"


class DistributionEngine:
    """Automated revenue distribution engine"""
    
    # Default role-based revenue shares
    DEFAULT_ROLE_SHARES = {
        "primary_artist": 0.40,
        "featured_artist": 0.25,
        "producer": 0.20,
        "songwriter": 0.10,
        "mixer": 0.03,
        "mastering": 0.02
    }
    
    # Country-specific tax handling
    TAX_WITHHOLDING = {
        "US": 0.30,   # 30% withholding for non-residents
        "DE": 0.26,   # 26.375% withholding
        "FR": 0.30,   # 30% withholding
        "GB": 0.20,   # 20% withholding
        "CA": 0.25    # 25% withholding
    }
    
    def __init__(self):
        self.distribution_rules = {}
        self.distribution_history = {}
        self.pending_payouts = {}
        
    async def create_distribution_rule(
        self,
        content_id: str,
        contributors: List[Contributor],
        distribution_type: DistributionType = DistributionType.PERCENTAGE_BASED,
        platform_fee: float = 0.10,
        payout_schedule: PayoutSchedule = PayoutSchedule.MONTHLY
    ) -> DistributionRule:
        """Create revenue distribution rule for content"""



        try:
            # Validate contribution percentages
            total_contribution = sum(c.contribution_percentage for c in contributors)
            if abs(total_contribution - 1.0) > 0.01:  # Allow 1% tolerance
                raise ValueError(f"Contribution percentages must sum to 100%, got {total_contribution * 100}%")
            
            # Calculate revenue shares based on distribution type
            if distribution_type == DistributionType.EQUAL_SPLIT:
                share_per_contributor = 1.0 / len(contributors)
                for contributor in contributors:
                    contributor.revenue_share = share_per_contributor
                    
            elif distribution_type == DistributionType.PERCENTAGE_BASED:
                for contributor in contributors:
                    contributor.revenue_share = contributor.contribution_percentage
                    
            elif distribution_type == DistributionType.ROLE_BASED:
                for contributor in contributors:
                    contributor.revenue_share = self.DEFAULT_ROLE_SHARES.get(
                        contributor.role, 
                        1.0 / len(contributors)
                    )
                    
            elif distribution_type == DistributionType.CONTRIBUTION_BASED:
                # Use contribution percentage as revenue share
                for contributor in contributors:
                    contributor.revenue_share = contributor.contribution_percentage
                    
            # Normalize revenue shares to sum to 1.0
            total_shares = sum(c.revenue_share for c in contributors)
            if total_shares > 0:
                for contributor in contributors:
                    contributor.revenue_share = contributor.revenue_share / total_shares
            
            rule = DistributionRule(
                content_id=content_id,
                distribution_type=distribution_type,
                contributors=contributors,
                platform_fee=platform_fee,
                payout_schedule=payout_schedule,
                created_at=datetime.now()
            )
            
            self.distribution_rules[content_id] = rule
            
            logger.info(f"Distribution rule created for content {content_id} with {len(contributors)} contributors")
            return rule
            
        except Exception as e:
            logger.error(f"Error creating distribution rule: {str(e)}")
            raise
    
    async def calculate_distribution(
        self,
        content_id: str,
        revenue_data: Dict[str, float],
        period_start: datetime,
        period_end: datetime
    ) -> DistributionEvent:
        """Calculate revenue distribution for a period"""



        try:
            rule = self.distribution_rules.get(content_id)
            if not rule:
                raise ValueError(f"No distribution rule found for content {content_id}")
            
            total_revenue = sum(revenue_data.values())
            
            # Calculate platform fee
            platform_revenue = total_revenue * rule.platform_fee
            
            # Calculate reserve amount
            reserved_amount = total_revenue * rule.reserve_percentage
            
            # Distributable amount
            distributable = total_revenue - platform_revenue - reserved_amount
            
            # Calculate individual payouts
            contributor_payouts = []
            total_distributed = 0.0
            
            for contributor in rule.contributors:
                gross_payout = distributable * contributor.revenue_share
                
                # Apply tax withholding if applicable
                tax_withholding = 0.0
                if contributor.tax_country in self.TAX_WITHHOLDING:
                    tax_withholding = gross_payout * self.TAX_WITHHOLDING[contributor.tax_country]
                
                net_payout = gross_payout - tax_withholding
                
                # Check minimum payout threshold
                if net_payout >= contributor.minimum_payout:
                    payout_data = {
                        "user_id": contributor.user_id,
                        "role": contributor.role,
                        "revenue_share": contributor.revenue_share,
                        "gross_amount": gross_payout,
                        "tax_withholding": tax_withholding,
                        "net_amount": net_payout,
                        "currency": contributor.preferred_currency,
                        "status": "pending"
                    }
                    contributor_payouts.append(payout_data)
                    total_distributed += net_payout
                else:
                    # Add to next period if below threshold
                    logger.info(f"Payout for {contributor.user_id} below threshold: {net_payout}")
            
            distribution_event = DistributionEvent(
                id=str(uuid.uuid4()),
                content_id=content_id,
                total_revenue=total_revenue,
                platform_revenue=platform_revenue,
                reserved_amount=reserved_amount,
                distributed_amount=total_distributed,
                contributor_payouts=contributor_payouts,
                period_start=period_start,
                period_end=period_end,
                status="calculated"
            )
            
            logger.info(f"Distribution calculated for content {content_id}: €{total_distributed:.2f} to {len(contributor_payouts)} contributors")
            return distribution_event
            
        except Exception as e:
            logger.error(f"Error calculating distribution: {str(e)}")
            raise
    
    async def process_automatic_distribution(
        self,
        content_id: str,
        revenue_data: Dict[str, float]
    ) -> Optional[DistributionEvent]:
        """Process automatic distribution based on schedule"""



        try:
            rule = self.distribution_rules.get(content_id)
            if not rule:
                logger.warning(f"No distribution rule for content {content_id}")
                return None
            
            # Determine period based on payout schedule
            now = datetime.now()
            
            if rule.payout_schedule == PayoutSchedule.DAILY:
                period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                period_end = period_start + timedelta(days=1)
            elif rule.payout_schedule == PayoutSchedule.WEEKLY:
                days_since_monday = now.weekday()
                period_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
                period_end = period_start + timedelta(days=7)
            elif rule.payout_schedule == PayoutSchedule.MONTHLY:
                period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if now.month == 12:
                    period_end = period_start.replace(year=now.year + 1, month=1)
                else:
                    period_end = period_start.replace(month=now.month + 1)
            else:
                # Default to monthly
                period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                period_end = period_start + timedelta(days=30)
            
            # Calculate distribution
            distribution = await self.calculate_distribution(
                content_id, revenue_data, period_start, period_end
            )
            
            # Check if total meets minimum threshold
            if distribution.distributed_amount >= rule.minimum_threshold:
                # Process the distribution
                distribution.processed_at = datetime.now()
                distribution.status = "processing"
                
                # Store distribution event
                self.distribution_history[distribution.id] = distribution
                
                # Queue payouts
                await self._queue_payouts(distribution)
                
                return distribution
            else:
                logger.info(f"Distribution amount below threshold: {distribution.distributed_amount}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing automatic distribution: {str(e)}")
            return None
    
    async def handle_multi_creator_collaboration(
        self,
        project_id: str,
        creators: List[Dict[str, Any]],
        revenue_split_agreement: Dict[str, float]
    ) -> DistributionRule:
        """Handle complex multi-creator collaborations"""



        try:
            contributors = []
            
            for creator_data in creators:
                contributor = Contributor(
                    user_id=creator_data["user_id"],
                    role=creator_data.get("role", "collaborator"),
                    contribution_percentage=creator_data.get("contribution", 0.0),
                    revenue_share=revenue_split_agreement.get(creator_data["user_id"], 0.0),
                    minimum_payout=creator_data.get("minimum_payout", 5.0),
                    preferred_currency=creator_data.get("currency", "EUR"),
                    tax_country=creator_data.get("country", "DE")
                )
                contributors.append(contributor)
            
            # Validate that revenue splits sum to 1.0
            total_split = sum(revenue_split_agreement.values())
            if abs(total_split - 1.0) > 0.01:
                raise ValueError(f"Revenue splits must sum to 100%, got {total_split * 100}%")
            
            rule = await self.create_distribution_rule(
                content_id=project_id,
                contributors=contributors,
                distribution_type=DistributionType.PERCENTAGE_BASED,
                payout_schedule=PayoutSchedule.MONTHLY
            )
            
            logger.info(f"Multi-creator collaboration rule created for project {project_id}")
            return rule
            
        except Exception as e:
            logger.error(f"Error handling multi-creator collaboration: {str(e)}")
            raise
    
    async def calculate_tax_implications(
        self,
        user_id: str,
        annual_earnings: float,
        tax_country: str
    ) -> Dict[str, Any]:
        """Calculate tax implications for user earnings"""



        try:
            # Get user's distributions for the year
            user_distributions = []
            for event in self.distribution_history.values():
                for payout in event.contributor_payouts:
                    if payout["user_id"] == user_id:
                        user_distributions.append({
                            "amount": payout["net_amount"],
                            "tax_withholding": payout["tax_withholding"],
                            "date": event.processed_at
                        })
            
            total_withholding = sum(d["tax_withholding"] for d in user_distributions)
            total_net_earnings = sum(d["amount"] for d in user_distributions)
            
            # Country-specific tax calculations
            tax_brackets = self._get_tax_brackets(tax_country)
            estimated_tax = self._calculate_progressive_tax(annual_earnings, tax_brackets)
            
            tax_summary = {
                "user_id": user_id,
                "tax_country": tax_country,
                "annual_earnings": annual_earnings,
                "total_withholding": total_withholding,
                "estimated_tax_owed": estimated_tax,
                "tax_refund_due": max(0, total_withholding - estimated_tax),
                "additional_tax_due": max(0, estimated_tax - total_withholding),
                "effective_tax_rate": estimated_tax / annual_earnings if annual_earnings > 0 else 0,
                "distributions_count": len(user_distributions)
            }
            
            return tax_summary
            
        except Exception as e:
            logger.error(f"Error calculating tax implications: {str(e)}")
            return {}
    
    async def generate_royalty_statements(
        self,
        content_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Generate detailed royalty statements"""



        try:
            rule = self.distribution_rules.get(content_id)
            if not rule:
                return {"error": "No distribution rule found"}
            
            # Get distributions for the period
            period_distributions = []
            for event in self.distribution_history.values():
                if (event.content_id == content_id and
                    event.period_start >= period_start and
                    event.period_end <= period_end):
                    period_distributions.append(event)
            
            # Aggregate data by contributor
            contributor_statements = {}
            
            for event in period_distributions:
                for payout in event.contributor_payouts:
                    user_id = payout["user_id"]
                    
                    if user_id not in contributor_statements:
                        contributor_statements[user_id] = {
                            "user_id": user_id,
                            "role": payout["role"],
                            "total_gross": 0.0,
                            "total_net": 0.0,
                            "total_tax_withholding": 0.0,
                            "payment_count": 0,
                            "payments": []
                        }
                    
                    stmt = contributor_statements[user_id]
                    stmt["total_gross"] += payout["gross_amount"]
                    stmt["total_net"] += payout["net_amount"]
                    stmt["total_tax_withholding"] += payout["tax_withholding"]
                    stmt["payment_count"] += 1
                    stmt["payments"].append({
                        "date": event.processed_at.isoformat() if event.processed_at else None,
                        "gross_amount": payout["gross_amount"],
                        "net_amount": payout["net_amount"],
                        "tax_withholding": payout["tax_withholding"]
                    })
            
            total_revenue = sum(event.total_revenue for event in period_distributions)
            total_distributed = sum(event.distributed_amount for event in period_distributions)
            
            royalty_statement = {
                "content_id": content_id,
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "total_revenue": total_revenue,
                "total_distributed": total_distributed,
                "contributor_statements": list(contributor_statements.values()),
                "distribution_events": len(period_distributions),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Royalty statement generated for content {content_id}")
            return royalty_statement
            
        except Exception as e:
            logger.error(f"Error generating royalty statements: {str(e)}")
            return {"error": str(e)}
    
    async def _queue_payouts(self, distribution: DistributionEvent):
        """Queue payouts for processing"""



        try:
            for payout in distribution.contributor_payouts:
                payout_id = str(uuid.uuid4())
                
                payout_data = {
                    "id": payout_id,
                    "distribution_id": distribution.id,
                    "user_id": payout["user_id"],
                    "amount": payout["net_amount"],
                    "currency": payout["currency"],
                    "status": "queued",
                    "queued_at": datetime.now(),
                    "scheduled_for": datetime.now() + timedelta(hours=24)  # Process next day
                }
                
                self.pending_payouts[payout_id] = payout_data
            
            logger.info(f"Queued {len(distribution.contributor_payouts)} payouts for distribution {distribution.id}")
            
        except Exception as e:
            logger.error(f"Error queueing payouts: {str(e)}")
    
    def _get_tax_brackets(self, country: str) -> List[Tuple[float, float]]:
        """Get tax brackets for country"""
        # Simplified tax brackets
        brackets = {
            "DE": [(9744, 0.14), (57051, 0.25), (270500, 0.42), (float('inf'), 0.45)],
            "US": [(12950, 0.10), (52525, 0.22), (210725, 0.32), (523600, 0.37)],
            "FR": [(10225, 0.11), (26070, 0.30), (74545, 0.41), (160336, 0.45)],
            "GB": [(12570, 0.20), (50270, 0.40), (float('inf'), 0.45)]
        }
        
        return brackets.get(country, [(10000, 0.20), (50000, 0.30), (float('inf'), 0.40)])
    
    def _calculate_progressive_tax(self, income: float, tax_brackets: List[Tuple[float, float]]) -> float:
        """Calculate progressive tax"""
        total_tax = 0.0
        remaining_income = income
        previous_threshold = 0.0
        
        for threshold, rate in tax_brackets:
            if remaining_income <= 0:
                break
                
            taxable_in_bracket = min(remaining_income, threshold - previous_threshold)
            total_tax += taxable_in_bracket * rate
            remaining_income -= taxable_in_bracket
            previous_threshold = threshold
        
        return total_tax
    
    async def get_distribution_analytics(
        self,
        content_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get distribution analytics"""



        try:
            filtered_events = []
            
            for event in self.distribution_history.values():
                if content_id and event.content_id != content_id:
                    continue
                if start_date and event.processed_at and event.processed_at < start_date:
                    continue
                if end_date and event.processed_at and event.processed_at > end_date:
                    continue
                if user_id:
                    has_user = any(p["user_id"] == user_id for p in event.contributor_payouts)
                    if not has_user:
                        continue
                        
                filtered_events.append(event)
            
            if not filtered_events:
                return {"message": "No distribution events found"}
            
            # Calculate analytics
            total_revenue = sum(e.total_revenue for e in filtered_events)
            total_distributed = sum(e.distributed_amount for e in filtered_events)
            total_platform_fees = sum(e.platform_revenue for e in filtered_events)
            
            # Calculate averages
            avg_distribution = total_distributed / len(filtered_events)
            avg_platform_fee_rate = total_platform_fees / total_revenue if total_revenue > 0 else 0
            
            # Top contributors
            contributor_totals = {}
            for event in filtered_events:
                for payout in event.contributor_payouts:
                    user_id = payout["user_id"]
                    if user_id not in contributor_totals:
                        contributor_totals[user_id] = 0.0
                    contributor_totals[user_id] += payout["net_amount"]
            
            top_contributors = sorted(contributor_totals.items(), key=lambda x: x[1], reverse=True)[:10]
            
            analytics = {
                "total_events": len(filtered_events),
                "total_revenue": total_revenue,
                "total_distributed": total_distributed,
                "total_platform_fees": total_platform_fees,
                "avg_distribution_amount": avg_distribution,
                "avg_platform_fee_rate": avg_platform_fee_rate,
                "distribution_efficiency": total_distributed / total_revenue if total_revenue > 0 else 0,
                "top_contributors": [{"user_id": uid, "total_earnings": amount} for uid, amount in top_contributors],
                "period_start": start_date.isoformat() if start_date else None,
                "period_end": end_date.isoformat() if end_date else None,
                "generated_at": datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting distribution analytics: {str(e)}")
            return {"error": str(e)}