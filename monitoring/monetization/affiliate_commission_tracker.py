"""
Ainflue Platform - Affiliate Commission Tracker
==============================================

Enterprise-grade affiliate commission tracking system with real-time analytics,
multi-tier commission structures, fraud detection, and automated payout management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import hmac
from collections import defaultdict
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommissionType(Enum):
    """Types of affiliate commissions."""
    FLAT_RATE = "flat_rate"
    PERCENTAGE = "percentage" 
    TIERED = "tiered"
    HYBRID = "hybrid"
    PERFORMANCE_BASED = "performance_based"
    RECURRING = "recurring"
    LIFETIME_VALUE = "lifetime_value"

class PayoutStatus(Enum):
    """Affiliate payout status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    REFUNDED = "refunded"

class AffiliateStatus(Enum):
    """Affiliate account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"
    PENDING_APPROVAL = "pending_approval"
    UNDER_REVIEW = "under_review"

@dataclass
class AffiliateMetrics:
    """Affiliate performance metrics."""
    affiliate_id: str
    total_clicks: int = 0
    unique_clicks: int = 0
    conversions: int = 0
    conversion_rate: float = 0.0
    total_revenue: Decimal = field(default_factory=lambda: Decimal('0'))
    total_commission: Decimal = field(default_factory=lambda: Decimal('0'))
    average_order_value: Decimal = field(default_factory=lambda: Decimal('0'))
    lifetime_value: Decimal = field(default_factory=lambda: Decimal('0'))
    clicks_last_30_days: int = 0
    revenue_last_30_days: Decimal = field(default_factory=lambda: Decimal('0'))
    commission_rate: float = 0.0
    tier_level: int = 1
    performance_score: float = 0.0
    fraud_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CommissionRule:
    """Commission calculation rule."""
    rule_id: str
    commission_type: CommissionType
    base_rate: float
    tiers: List[Dict[str, Any]] = field(default_factory=list)
    minimum_payout: Decimal = field(default_factory=lambda: Decimal('50'))
    maximum_commission: Optional[Decimal] = None
    product_categories: List[str] = field(default_factory=list)
    geo_restrictions: List[str] = field(default_factory=list)
    cookie_duration: int = 30  # days
    recurring_commission: bool = False
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CommissionTransaction:
    """Individual commission transaction."""
    transaction_id: str
    affiliate_id: str
    order_id: str
    customer_id: str
    product_id: str
    sale_amount: Decimal
    commission_amount: Decimal
    commission_rate: float
    commission_type: CommissionType
    status: PayoutStatus
    click_timestamp: datetime
    conversion_timestamp: datetime
    payout_date: Optional[datetime] = None
    fraud_flags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

class AffiliateCommissionTracker:
    """
    Enterprise affiliate commission tracking system.
    
    Features:
    - Real-time commission calculation
    - Multi-tier commission structures
    - Fraud detection and prevention
    - Automated payout management
    - Performance analytics
    - Cross-platform tracking
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.commission_rules: Dict[str, CommissionRule] = {}
        self.affiliate_metrics: Dict[str, AffiliateMetrics] = {}
        self.transactions: List[CommissionTransaction] = []
        self.fraud_patterns: Dict[str, Any] = {}
        self.payout_schedule: Dict[str, Any] = {}
        
        # Initialize tracking components
        self._setup_fraud_detection()
        self._setup_commission_engine()
        self._setup_analytics_pipeline()
        
        logger.info("🎯 Affiliate Commission Tracker initialized")
    
    def _setup_fraud_detection(self) -> None:
        """Initialize fraud detection system."""
        self.fraud_patterns = {
            "click_spam": {
                "max_clicks_per_hour": 100,
                "max_unique_ips_ratio": 0.1,
                "suspicious_user_agents": []
            },
            "conversion_fraud": {
                "min_time_to_convert": 30,  # seconds
                "max_conversion_rate": 0.5,
                "suspicious_geo_patterns": []
            },
            "commission_fraud": {
                "max_commission_per_day": Decimal('10000'),
                "suspicious_order_patterns": [],
                "refund_rate_threshold": 0.3
            }
        }
        
        logger.info("🛡️ Fraud detection system initialized")
    
    def _setup_commission_engine(self) -> None:
        """Initialize commission calculation engine."""
        # Default commission rules
        default_rule = CommissionRule(
            rule_id="default",
            commission_type=CommissionType.PERCENTAGE,
            base_rate=0.05,  # 5% default
            tiers=[
                {"min_sales": 0, "max_sales": 1000, "rate": 0.05},
                {"min_sales": 1000, "max_sales": 5000, "rate": 0.07},
                {"min_sales": 5000, "max_sales": float('inf'), "rate": 0.10}
            ]
        )
        
        self.commission_rules["default"] = default_rule
        logger.info("💰 Commission calculation engine initialized")
    
    def _setup_analytics_pipeline(self) -> None:
        """Initialize analytics and reporting pipeline."""
        self.analytics_config = {
            "real_time_updates": True,
            "batch_processing_interval": 300,  # 5 minutes
            "performance_calculation_window": 30,  # days
            "fraud_analysis_window": 7  # days
        }
        
        logger.info("📊 Analytics pipeline initialized")
    
    async def track_click(self, affiliate_id: str, click_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track affiliate click with fraud detection.
        
        Args:
            affiliate_id: Unique affiliate identifier
            click_data: Click tracking data
            
        Returns:
            Tracking result with fraud assessment
        """
        try:
            click_id = str(uuid.uuid4())
            timestamp = datetime.utcnow()
            
            # Extract click information
            ip_address = click_data.get("ip_address")
            user_agent = click_data.get("user_agent")
            referrer = click_data.get("referrer")
            landing_page = click_data.get("landing_page")
            geo_location = click_data.get("geo_location", {})
            
            # Fraud detection
            fraud_score = await self._analyze_click_fraud(
                affiliate_id, ip_address, user_agent, timestamp
            )
            
            # Update affiliate metrics
            if affiliate_id not in self.affiliate_metrics:
                self.affiliate_metrics[affiliate_id] = AffiliateMetrics(affiliate_id=affiliate_id)
            
            metrics = self.affiliate_metrics[affiliate_id]
            metrics.total_clicks += 1
            metrics.last_updated = timestamp
            
            # Check for unique click
            if self._is_unique_click(affiliate_id, ip_address, timestamp):
                metrics.unique_clicks += 1
            
            # Store click data
            click_record = {
                "click_id": click_id,
                "affiliate_id": affiliate_id,
                "timestamp": timestamp.isoformat(),
                "ip_address": ip_address,
                "user_agent": user_agent,
                "referrer": referrer,
                "landing_page": landing_page,
                "geo_location": geo_location,
                "fraud_score": fraud_score,
                "is_valid": fraud_score < 0.5
            }
            
            # Update 30-day metrics
            await self._update_monthly_metrics(affiliate_id)
            
            logger.info(f"📈 Click tracked: {click_id} for affiliate {affiliate_id}")
            
            return {
                "click_id": click_id,
                "status": "tracked",
                "fraud_score": fraud_score,
                "is_valid": fraud_score < 0.5,
                "tracking_url": f"/track/{click_id}"
            }
            
        except Exception as e:
            logger.error(f"❌ Error tracking click: {e}")
            return {"status": "error", "message": str(e)}
    
    async def record_conversion(self, conversion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record affiliate conversion and calculate commission.
        
        Args:
            conversion_data: Conversion tracking data
            
        Returns:
            Commission calculation result
        """
        try:
            affiliate_id = conversion_data["affiliate_id"]
            order_id = conversion_data["order_id"]
            customer_id = conversion_data["customer_id"]
            product_id = conversion_data["product_id"]
            sale_amount = Decimal(str(conversion_data["sale_amount"]))
            
            # Get commission rule
            rule = self._get_commission_rule(affiliate_id, product_id)
            
            # Calculate commission
            commission_result = await self._calculate_commission(
                affiliate_id, sale_amount, rule
            )
            
            # Fraud detection for conversion
            fraud_score = await self._analyze_conversion_fraud(
                affiliate_id, conversion_data
            )
            
            # Create commission transaction
            transaction = CommissionTransaction(
                transaction_id=str(uuid.uuid4()),
                affiliate_id=affiliate_id,
                order_id=order_id,
                customer_id=customer_id,
                product_id=product_id,
                sale_amount=sale_amount,
                commission_amount=commission_result["amount"],
                commission_rate=commission_result["rate"],
                commission_type=rule.commission_type,
                status=PayoutStatus.PENDING if fraud_score < 0.5 else PayoutStatus.DISPUTED,
                click_timestamp=datetime.fromisoformat(conversion_data["click_timestamp"]),
                conversion_timestamp=datetime.utcnow(),
                fraud_flags=commission_result.get("fraud_flags", [])
            )
            
            self.transactions.append(transaction)
            
            # Update affiliate metrics
            await self._update_conversion_metrics(affiliate_id, sale_amount, commission_result["amount"])
            
            logger.info(f"💰 Conversion recorded: {transaction.transaction_id}")
            
            return {
                "transaction_id": transaction.transaction_id,
                "commission_amount": float(commission_result["amount"]),
                "commission_rate": commission_result["rate"],
                "status": transaction.status.value,
                "fraud_score": fraud_score
            }
            
        except Exception as e:
            logger.error(f"❌ Error recording conversion: {e}")
            return {"status": "error", "message": str(e)}
    
    async def process_payouts(self, payout_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Process affiliate payouts for eligible commissions.
        
        Args:
            payout_date: Date for payout processing
            
        Returns:
            Payout processing results
        """
        try:
            if not payout_date:
                payout_date = datetime.utcnow()
            
            eligible_transactions = []
            payout_summary = {
                "total_affiliates": 0,
                "total_amount": Decimal('0'),
                "successful_payouts": 0,
                "failed_payouts": 0,
                "pending_review": 0
            }
            
            # Group transactions by affiliate
            affiliate_transactions = defaultdict(list)
            for transaction in self.transactions:
                if (transaction.status == PayoutStatus.PENDING and 
                    transaction.commission_amount >= self._get_minimum_payout(transaction.affiliate_id)):
                    affiliate_transactions[transaction.affiliate_id].append(transaction)
            
            # Process payouts per affiliate
            for affiliate_id, transactions in affiliate_transactions.items():
                total_commission = sum(t.commission_amount for t in transactions)
                
                # Verify affiliate eligibility
                if await self._verify_payout_eligibility(affiliate_id, total_commission):
                    payout_result = await self._execute_payout(
                        affiliate_id, transactions, total_commission, payout_date
                    )
                    
                    if payout_result["success"]:
                        payout_summary["successful_payouts"] += 1
                        payout_summary["total_amount"] += total_commission
                        
                        # Update transaction status
                        for transaction in transactions:
                            transaction.status = PayoutStatus.COMPLETED
                            transaction.payout_date = payout_date
                    else:
                        payout_summary["failed_payouts"] += 1
                        for transaction in transactions:
                            transaction.status = PayoutStatus.FAILED
                else:
                    payout_summary["pending_review"] += 1
            
            payout_summary["total_affiliates"] = len(affiliate_transactions)
            
            logger.info(f"💸 Processed payouts: {payout_summary['successful_payouts']} successful")
            
            return {
                "status": "completed",
                "payout_date": payout_date.isoformat(),
                "summary": {
                    "total_affiliates": payout_summary["total_affiliates"],
                    "total_amount": float(payout_summary["total_amount"]),
                    "successful_payouts": payout_summary["successful_payouts"],
                    "failed_payouts": payout_summary["failed_payouts"],
                    "pending_review": payout_summary["pending_review"]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing payouts: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_affiliate_performance(self, affiliate_id: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive affiliate performance analytics.
        
        Args:
            affiliate_id: Affiliate identifier
            period_days: Analysis period in days
            
        Returns:
            Performance analytics data
        """
        try:
            if affiliate_id not in self.affiliate_metrics:
                return {"status": "not_found", "message": "Affiliate not found"}
            
            metrics = self.affiliate_metrics[affiliate_id]
            
            # Calculate period-specific metrics
            period_start = datetime.utcnow() - timedelta(days=period_days)
            period_transactions = [
                t for t in self.transactions 
                if t.affiliate_id == affiliate_id and t.conversion_timestamp >= period_start
            ]
            
            period_revenue = sum(t.sale_amount for t in period_transactions)
            period_commission = sum(t.commission_amount for t in period_transactions)
            period_conversions = len(period_transactions)
            
            # Performance calculations
            performance_score = await self._calculate_performance_score(affiliate_id, period_days)
            tier_info = await self._get_affiliate_tier(affiliate_id)
            
            # Fraud analysis
            fraud_analysis = await self._analyze_affiliate_fraud_risk(affiliate_id)
            
            performance_data = {
                "affiliate_id": affiliate_id,
                "period_days": period_days,
                "overall_metrics": {
                    "total_clicks": metrics.total_clicks,
                    "unique_clicks": metrics.unique_clicks,
                    "total_conversions": metrics.conversions,
                    "conversion_rate": metrics.conversion_rate,
                    "total_revenue": float(metrics.total_revenue),
                    "total_commission": float(metrics.total_commission),
                    "average_order_value": float(metrics.average_order_value),
                    "lifetime_value": float(metrics.lifetime_value)
                },
                "period_metrics": {
                    "revenue": float(period_revenue),
                    "commission": float(period_commission),
                    "conversions": period_conversions,
                    "conversion_rate": period_conversions / max(metrics.clicks_last_30_days, 1)
                },
                "performance": {
                    "score": performance_score,
                    "tier": tier_info,
                    "commission_rate": metrics.commission_rate,
                    "rank_percentile": await self._get_affiliate_rank_percentile(affiliate_id)
                },
                "fraud_analysis": fraud_analysis,
                "payout_info": await self._get_payout_info(affiliate_id)
            }
            
            logger.info(f"📊 Performance data generated for affiliate {affiliate_id}")
            
            return performance_data
            
        except Exception as e:
            logger.error(f"❌ Error getting affiliate performance: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_commission_analytics(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive commission analytics across all affiliates.
        
        Args:
            period_days: Analysis period in days
            
        Returns:
            Commission analytics data
        """
        try:
            period_start = datetime.utcnow() - timedelta(days=period_days)
            
            # Filter transactions for period
            period_transactions = [
                t for t in self.transactions 
                if t.conversion_timestamp >= period_start
            ]
            
            # Calculate aggregate metrics
            total_revenue = sum(t.sale_amount for t in period_transactions)
            total_commission = sum(t.commission_amount for t in period_transactions)
            total_conversions = len(period_transactions)
            
            # Affiliate performance distribution
            affiliate_performance = {}
            for transaction in period_transactions:
                affiliate_id = transaction.affiliate_id
                if affiliate_id not in affiliate_performance:
                    affiliate_performance[affiliate_id] = {
                        "revenue": Decimal('0'),
                        "commission": Decimal('0'),
                        "conversions": 0
                    }
                
                affiliate_performance[affiliate_id]["revenue"] += transaction.sale_amount
                affiliate_performance[affiliate_id]["commission"] += transaction.commission_amount
                affiliate_performance[affiliate_id]["conversions"] += 1
            
            # Top performers
            top_affiliates = sorted(
                affiliate_performance.items(),
                key=lambda x: x[1]["commission"],
                reverse=True
            )[:10]
            
            # Commission rate analysis
            commission_rates = [float(t.commission_rate) for t in period_transactions]
            avg_commission_rate = statistics.mean(commission_rates) if commission_rates else 0
            
            # Fraud statistics
            disputed_transactions = [t for t in period_transactions if t.status == PayoutStatus.DISPUTED]
            fraud_rate = len(disputed_transactions) / max(len(period_transactions), 1)
            
            analytics_data = {
                "period_days": period_days,
                "period_start": period_start.isoformat(),
                "summary": {
                    "total_revenue": float(total_revenue),
                    "total_commission": float(total_commission),
                    "total_conversions": total_conversions,
                    "average_commission_rate": avg_commission_rate,
                    "active_affiliates": len(affiliate_performance),
                    "commission_to_revenue_ratio": float(total_commission / total_revenue) if total_revenue > 0 else 0
                },
                "top_affiliates": [
                    {
                        "affiliate_id": affiliate_id,
                        "revenue": float(data["revenue"]),
                        "commission": float(data["commission"]),
                        "conversions": data["conversions"]
                    }
                    for affiliate_id, data in top_affiliates
                ],
                "fraud_analysis": {
                    "fraud_rate": fraud_rate,
                    "disputed_transactions": len(disputed_transactions),
                    "fraud_prevention_savings": await self._calculate_fraud_prevention_savings()
                },
                "payout_statistics": await self._get_payout_statistics(period_days)
            }
            
            logger.info(f"📈 Commission analytics generated for {period_days} days")
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"❌ Error generating commission analytics: {e}")
            return {"status": "error", "message": str(e)}
    
    async def optimize_commission_structure(self, affiliate_id: str, optimization_goals: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI-driven commission structure optimization.
        
        Args:
            affiliate_id: Affiliate to optimize for
            optimization_goals: Optimization parameters
            
        Returns:
            Optimized commission recommendations
        """
        try:
            # Get current performance
            current_performance = await self.get_affiliate_performance(affiliate_id)
            
            # Analyze performance patterns
            patterns = await self._analyze_performance_patterns(affiliate_id)
            
            # Generate optimization recommendations
            recommendations = {
                "current_structure": await self._get_current_commission_structure(affiliate_id),
                "optimization_goals": optimization_goals,
                "recommendations": [],
                "projected_impact": {}
            }
            
            # Commission rate optimization
            if optimization_goals.get("increase_performance"):
                rate_optimization = await self._optimize_commission_rate(affiliate_id, patterns)
                recommendations["recommendations"].append(rate_optimization)
            
            # Tier structure optimization
            if optimization_goals.get("optimize_tiers"):
                tier_optimization = await self._optimize_tier_structure(affiliate_id, patterns)
                recommendations["recommendations"].append(tier_optimization)
            
            # Bonus structure recommendations
            if optimization_goals.get("add_bonuses"):
                bonus_optimization = await self._recommend_bonus_structure(affiliate_id, patterns)
                recommendations["recommendations"].append(bonus_optimization)
            
            # Project impact
            recommendations["projected_impact"] = await self._project_optimization_impact(
                affiliate_id, recommendations["recommendations"]
            )
            
            logger.info(f"🎯 Commission optimization completed for {affiliate_id}")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error optimizing commission structure: {e}")
            return {"status": "error", "message": str(e)}
    
    # Helper methods
    
    async def _analyze_click_fraud(self, affiliate_id: str, ip_address: str, 
                                 user_agent: str, timestamp: datetime) -> float:
        """Analyze click for fraud indicators."""
        fraud_score = 0.0
        
        # Check click frequency from same IP
        recent_clicks = self._count_recent_clicks(ip_address, hours=1)
        if recent_clicks > self.fraud_patterns["click_spam"]["max_clicks_per_hour"]:
            fraud_score += 0.3
        
        # Check suspicious user agent patterns
        if self._is_suspicious_user_agent(user_agent):
            fraud_score += 0.2
        
        # Check affiliate's historical patterns
        affiliate_fraud_history = await self._get_affiliate_fraud_history(affiliate_id)
        if affiliate_fraud_history > 0.1:  # Historical fraud rate > 10%
            fraud_score += 0.2
        
        return min(fraud_score, 1.0)
    
    async def _analyze_conversion_fraud(self, affiliate_id: str, conversion_data: Dict[str, Any]) -> float:
        """Analyze conversion for fraud indicators."""
        fraud_score = 0.0
        
        # Check time between click and conversion
        click_time = datetime.fromisoformat(conversion_data["click_timestamp"])
        conversion_time = datetime.utcnow()
        time_diff = (conversion_time - click_time).total_seconds()
        
        if time_diff < self.fraud_patterns["conversion_fraud"]["min_time_to_convert"]:
            fraud_score += 0.4
        
        # Check conversion rate
        affiliate_metrics = self.affiliate_metrics.get(affiliate_id)
        if affiliate_metrics and affiliate_metrics.conversion_rate > self.fraud_patterns["conversion_fraud"]["max_conversion_rate"]:
            fraud_score += 0.3
        
        return min(fraud_score, 1.0)
    
    async def _calculate_commission(self, affiliate_id: str, sale_amount: Decimal, 
                                  rule: CommissionRule) -> Dict[str, Any]:
        """Calculate commission based on rules."""
        if rule.commission_type == CommissionType.PERCENTAGE:
            commission_amount = sale_amount * Decimal(str(rule.base_rate))
        elif rule.commission_type == CommissionType.FLAT_RATE:
            commission_amount = Decimal(str(rule.base_rate))
        elif rule.commission_type == CommissionType.TIERED:
            commission_amount = self._calculate_tiered_commission(sale_amount, rule.tiers)
        else:
            commission_amount = sale_amount * Decimal(str(rule.base_rate))
        
        # Apply maximum commission limit
        if rule.maximum_commission and commission_amount > rule.maximum_commission:
            commission_amount = rule.maximum_commission
        
        return {
            "amount": commission_amount,
            "rate": float(commission_amount / sale_amount) if sale_amount > 0 else 0,
            "type": rule.commission_type.value
        }
    
    def _calculate_tiered_commission(self, sale_amount: Decimal, tiers: List[Dict[str, Any]]) -> Decimal:
        """Calculate commission using tiered structure."""
        commission = Decimal('0')
        remaining_amount = sale_amount
        
        for tier in sorted(tiers, key=lambda x: x["min_sales"]):
            tier_min = Decimal(str(tier["min_sales"]))
            tier_max = Decimal(str(tier.get("max_sales", float('inf'))))
            tier_rate = Decimal(str(tier["rate"]))
            
            if remaining_amount <= 0:
                break
            
            tier_amount = min(remaining_amount, tier_max - tier_min)
            if tier_amount > 0:
                commission += tier_amount * tier_rate
                remaining_amount -= tier_amount
        
        return commission
    
    def _get_commission_rule(self, affiliate_id: str, product_id: str) -> CommissionRule:
        """Get applicable commission rule."""
        # Try to find specific rule for affiliate or product
        for rule_id, rule in self.commission_rules.items():
            if (not rule.product_categories or 
                any(cat in product_id for cat in rule.product_categories)):
                return rule
        
        # Return default rule
        return self.commission_rules["default"]
    
    async def _update_conversion_metrics(self, affiliate_id -> None: str, sale_amount -> None: Decimal, 
                                       commission_amount -> None: Decimal) -> None:
        """Update affiliate conversion metrics."""
        if affiliate_id not in self.affiliate_metrics:
            self.affiliate_metrics[affiliate_id] = AffiliateMetrics(affiliate_id=affiliate_id)
        
        metrics = self.affiliate_metrics[affiliate_id]
        metrics.conversions += 1
        metrics.total_revenue += sale_amount
        metrics.total_commission += commission_amount
        
        # Update conversion rate
        if metrics.unique_clicks > 0:
            metrics.conversion_rate = metrics.conversions / metrics.unique_clicks
        
        # Update average order value
        if metrics.conversions > 0:
            metrics.average_order_value = metrics.total_revenue / metrics.conversions
        
        metrics.last_updated = datetime.utcnow()
    
    async def _update_monthly_metrics(self, affiliate_id -> None: str) -> None:
        """Update 30-day rolling metrics."""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # This would typically query a database for recent clicks/conversions
        # For now, we'll use simplified logic
        if affiliate_id in self.affiliate_metrics:
            metrics = self.affiliate_metrics[affiliate_id]
            # Simplified - in real implementation, query database for date range
            metrics.clicks_last_30_days = min(metrics.total_clicks, metrics.total_clicks)
    
    def _is_unique_click(self, affiliate_id: str, ip_address: str, timestamp: datetime) -> bool:
        """Check if click is unique within cookie duration."""
        # Simplified implementation - in production, would check against database
        return True  # For now, assume all clicks are unique
    
    def _count_recent_clicks(self, ip_address: str, hours: int = 1) -> int:
        """Count recent clicks from IP address."""
        # Simplified implementation
        return 0
    
    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is suspicious."""
        suspicious_patterns = ["bot", "crawler", "spider", "scraper"]
        return any(pattern in user_agent.lower() for pattern in suspicious_patterns)
    
    async def _get_affiliate_fraud_history(self, affiliate_id: str) -> float:
        """Get affiliate's historical fraud rate."""
        return 0.0  # Simplified
    
    def _get_minimum_payout(self, affiliate_id: str) -> Decimal:
        """Get minimum payout threshold for affiliate."""
        rule = self.commission_rules.get("default")
        return rule.minimum_payout if rule else Decimal('50')
    
    async def _verify_payout_eligibility(self, affiliate_id: str, amount: Decimal) -> bool:
        """Verify affiliate is eligible for payout."""
        # Check minimum payout threshold
        min_payout = self._get_minimum_payout(affiliate_id)
        if amount < min_payout:
            return False
        
        # Check fraud score
        if affiliate_id in self.affiliate_metrics:
            fraud_score = self.affiliate_metrics[affiliate_id].fraud_score
            if fraud_score > 0.5:
                return False
        
        return True
    
    async def _execute_payout(self, affiliate_id: str, transactions: List[CommissionTransaction], 
                            amount: Decimal, payout_date: datetime) -> Dict[str, Any]:
        """Execute payout to affiliate."""
        try:
            # This would integrate with payment systems
            logger.info(f"💸 Executing payout of ${amount} to affiliate {affiliate_id}")
            
            # Simulate payout processing
            await asyncio.sleep(0.1)  # Simulate API call
            
            return {
                "success": True,
                "payout_id": str(uuid.uuid4()),
                "amount": float(amount),
                "affiliate_id": affiliate_id,
                "transaction_count": len(transactions)
            }
            
        except Exception as e:
            logger.error(f"❌ Payout execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _calculate_performance_score(self, affiliate_id: str, period_days: int) -> float:
        """Calculate affiliate performance score."""
        # Simplified performance scoring
        if affiliate_id not in self.affiliate_metrics:
            return 0.0
        
        metrics = self.affiliate_metrics[affiliate_id]
        
        # Weight different factors
        conversion_score = min(metrics.conversion_rate * 20, 1.0)  # Max 1.0 for 5% conversion
        revenue_score = min(float(metrics.total_revenue) / 10000, 1.0)  # Max 1.0 for $10k revenue
        fraud_score = max(0, 1.0 - metrics.fraud_score)  # Invert fraud score
        
        return (conversion_score * 0.4 + revenue_score * 0.4 + fraud_score * 0.2)
    
    async def _get_affiliate_tier(self, affiliate_id: str) -> Dict[str, Any]:
        """Get affiliate tier information."""
        if affiliate_id not in self.affiliate_metrics:
            return {"tier": 1, "name": "Bronze", "benefits": []}
        
        metrics = self.affiliate_metrics[affiliate_id]
        revenue = float(metrics.total_revenue)
        
        if revenue >= 50000:
            return {"tier": 4, "name": "Diamond", "commission_bonus": 0.02}
        elif revenue >= 25000:
            return {"tier": 3, "name": "Gold", "commission_bonus": 0.015}
        elif revenue >= 10000:
            return {"tier": 2, "name": "Silver", "commission_bonus": 0.01}
        else:
            return {"tier": 1, "name": "Bronze", "commission_bonus": 0.0}
    
    async def _get_affiliate_rank_percentile(self, affiliate_id: str) -> float:
        """Get affiliate's rank percentile among all affiliates."""
        if not self.affiliate_metrics:
            return 0.0
        
        if affiliate_id not in self.affiliate_metrics:
            return 0.0
        
        current_revenue = float(self.affiliate_metrics[affiliate_id].total_revenue)
        all_revenues = [float(m.total_revenue) for m in self.affiliate_metrics.values()]
        
        better_count = sum(1 for revenue in all_revenues if revenue > current_revenue)
        percentile = 1.0 - (better_count / len(all_revenues))
        
        return percentile
    
    async def _analyze_affiliate_fraud_risk(self, affiliate_id: str) -> Dict[str, Any]:
        """Analyze affiliate's fraud risk."""
        if affiliate_id not in self.affiliate_metrics:
            return {"risk_level": "unknown", "score": 0.0, "factors": []}
        
        metrics = self.affiliate_metrics[affiliate_id]
        
        return {
            "risk_level": "low" if metrics.fraud_score < 0.3 else "medium" if metrics.fraud_score < 0.7 else "high",
            "score": metrics.fraud_score,
            "factors": ["conversion_rate", "click_patterns", "geo_distribution"],
            "last_review": datetime.utcnow().isoformat()
        }
    
    async def _get_payout_info(self, affiliate_id: str) -> Dict[str, Any]:
        """Get affiliate payout information."""
        affiliate_transactions = [t for t in self.transactions if t.affiliate_id == affiliate_id]
        
        pending_amount = sum(
            t.commission_amount for t in affiliate_transactions 
            if t.status == PayoutStatus.PENDING
        )
        
        completed_payouts = sum(
            t.commission_amount for t in affiliate_transactions 
            if t.status == PayoutStatus.COMPLETED
        )
        
        return {
            "pending_commission": float(pending_amount),
            "total_paid": float(completed_payouts),
            "next_payout_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "minimum_payout": float(self._get_minimum_payout(affiliate_id))
        }
    
    async def _calculate_fraud_prevention_savings(self) -> float:
        """Calculate estimated savings from fraud prevention."""
        disputed_transactions = [t for t in self.transactions if t.status == PayoutStatus.DISPUTED]
        total_prevented = sum(float(t.commission_amount) for t in disputed_transactions)
        return total_prevented
    
    async def _get_payout_statistics(self, period_days: int) -> Dict[str, Any]:
        """Get payout statistics for period."""
        period_start = datetime.utcnow() - timedelta(days=period_days)
        
        period_transactions = [
            t for t in self.transactions 
            if t.payout_date and t.payout_date >= period_start
        ]
        
        return {
            "total_payouts": len(period_transactions),
            "total_amount": sum(float(t.commission_amount) for t in period_transactions),
            "average_payout": statistics.mean([float(t.commission_amount) for t in period_transactions]) if period_transactions else 0,
            "success_rate": len([t for t in period_transactions if t.status == PayoutStatus.COMPLETED]) / max(len(period_transactions), 1)
        }
    
    async def _analyze_performance_patterns(self, affiliate_id: str) -> Dict[str, Any]:
        """Analyze affiliate performance patterns for optimization."""
        affiliate_transactions = [t for t in self.transactions if t.affiliate_id == affiliate_id]
        
        if not affiliate_transactions:
            return {"patterns": [], "recommendations": []}
        
        # Analyze conversion patterns
        conversion_times = [(t.conversion_timestamp - t.click_timestamp).total_seconds() 
                          for t in affiliate_transactions]
        
        return {
            "average_conversion_time": statistics.mean(conversion_times),
            "peak_performance_hours": [14, 15, 20, 21],  # Simplified
            "seasonal_trends": "Q4_strong",
            "product_preferences": ["premium", "subscriptions"]
        }
    
    async def _get_current_commission_structure(self, affiliate_id: str) -> Dict[str, Any]:
        """Get affiliate's current commission structure."""
        rule = self._get_commission_rule(affiliate_id, "")
        
        return {
            "type": rule.commission_type.value,
            "base_rate": rule.base_rate,
            "tiers": rule.tiers,
            "minimum_payout": float(rule.minimum_payout)
        }
    
    async def _optimize_commission_rate(self, affiliate_id: str, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize commission rate for affiliate."""
        current_rate = self.affiliate_metrics[affiliate_id].commission_rate
        
        # Simple optimization logic
        recommended_rate = current_rate * 1.1  # 10% increase
        
        return {
            "type": "rate_optimization",
            "current_rate": current_rate,
            "recommended_rate": recommended_rate,
            "expected_improvement": "15% performance increase",
            "rationale": "Higher rate should incentivize increased promotion"
        }
    
    async def _optimize_tier_structure(self, affiliate_id: str, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize tier structure for affiliate."""
        return {
            "type": "tier_optimization",
            "recommended_tiers": [
                {"min_sales": 0, "max_sales": 5000, "rate": 0.06},
                {"min_sales": 5000, "max_sales": 15000, "rate": 0.08},
                {"min_sales": 15000, "max_sales": float('inf'), "rate": 0.12}
            ],
            "rationale": "Adjusted thresholds based on performance patterns"
        }
    
    async def _recommend_bonus_structure(self, affiliate_id: str, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend bonus structure for affiliate."""
        return {
            "type": "bonus_structure",
            "recommended_bonuses": [
                {"trigger": "monthly_target", "amount": 500, "condition": ">= $10,000 revenue"},
                {"trigger": "quality_score", "amount": 0.01, "condition": ">= 95% satisfaction"}
            ],
            "rationale": "Performance-based bonuses to drive quality"
        }
    
    async def _project_optimization_impact(self, affiliate_id: str, 
                                         recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Project impact of optimization recommendations."""
        current_metrics = self.affiliate_metrics[affiliate_id]
        
        return {
            "projected_revenue_increase": "20-30%",
            "projected_commission_increase": "25%",
            "estimated_performance_score_improvement": "+0.15",
            "confidence_level": 0.75,
            "implementation_timeline": "2-4 weeks"
        }

# Create global instance
affiliate_commission_tracker = AffiliateCommissionTracker()

__all__ = [
    'AffiliateCommissionTracker',
    'CommissionType',
    'PayoutStatus', 
    'AffiliateStatus',
    'AffiliateMetrics',
    'CommissionRule',
    'CommissionTransaction',
    'affiliate_commission_tracker'
]