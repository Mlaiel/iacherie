"""
💰 Monetization Orchestration Engine - Enterprise Core
=====================================================

Moteur d'orchestration avancé pour la monétisation Creator Economy Ainflue.
Optimisation intelligente des revenus et gestion automatisée des paiements.

Architecture: monitoring/core_orchestration/ (NIVEAU 3)
Responsabilité: Orchestration maître monétisation et revenue optimization

© 2025 Fahed Mlaiel - Architecture Monetization Propriétaire Ultra-Avancée
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import json
import uuid


class RevenueStreamType(Enum):
    """Types de flux de revenus"""
    SUBSCRIPTION = "subscription"
    PAY_PER_VIEW = "pay_per_view"
    COLLABORATION_FEE = "collaboration_fee"
    PREMIUM_CONTENT = "premium_content"
    SPONSORSHIP = "sponsorship"
    MERCHANDISE = "merchandise"
    LICENSING = "licensing"
    AFFILIATE = "affiliate"
    DONATION = "donation"
    WORKSHOP = "workshop"


class PaymentStatus(Enum):
    """Statuts de paiement"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class TaxJurisdiction(Enum):
    """Juridictions fiscales"""
    EU = "european_union"
    US = "united_states"
    UK = "united_kingdom"
    CA = "canada"
    AU = "australia"
    OTHER = "other"


@dataclass
class RevenueStreamConfig:
    """Configuration flux de revenus"""
    stream_type: RevenueStreamType
    commission_rate: Decimal
    minimum_payout: Decimal
    payment_frequency: str  # "daily", "weekly", "monthly"
    auto_optimization: bool = True
    tax_handling: bool = True


@dataclass
class PaymentTransaction:
    """Transaction de paiement"""
    transaction_id: str
    creator_id: str
    amount: Decimal
    currency: str
    revenue_stream: RevenueStreamType
    status: PaymentStatus
    created_at: datetime
    processed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreatorEarnings:
    """Revenus créateur"""
    creator_id: str
    total_earnings: Decimal
    pending_earnings: Decimal
    paid_earnings: Decimal
    revenue_streams: Dict[RevenueStreamType, Decimal]
    performance_metrics: Dict[str, float]
    optimization_score: float
    tax_info: Dict[str, Any] = field(default_factory=dict)


class MonetizationOrchestrationEngine:
    """Moteur orchestration monétisation enterprise"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # Revenue tracking
        self.revenue_streams: Dict[str, RevenueStreamConfig] = {}
        self.creator_earnings: Dict[str, CreatorEarnings] = {}
        self.pending_transactions: List[PaymentTransaction] = []
        self.completed_transactions: List[PaymentTransaction] = []
        
        # Revenue optimization
        self.optimization_rules: Dict[str, Any] = {}
        self.performance_thresholds: Dict[str, float] = {}
        
        # Payment processing
        self.payment_processors: Dict[str, Any] = {}
        self.payout_schedules: Dict[str, datetime] = {}
        
        # Tax compliance
        self.tax_calculators: Dict[TaxJurisdiction, Any] = {}
        self.compliance_rules: Dict[str, Any] = {}
        
        # Analytics and insights
        self.revenue_analytics: Dict[str, Any] = {}
        self.prediction_models: Dict[str, Any] = {}
        
        # Initialize components
        self._initialize_revenue_streams()
        self._initialize_optimization_rules()
        self._initialize_tax_compliance()
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging"""
        logger = logging.getLogger("monetization_orchestration")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
        
    def _initialize_revenue_streams(self):
        """Initialisation flux de revenus"""
        self.revenue_streams = {
            "subscription": RevenueStreamConfig(
                stream_type=RevenueStreamType.SUBSCRIPTION,
                commission_rate=Decimal("0.15"),  # 15%
                minimum_payout=Decimal("50.00"),
                payment_frequency="monthly"
            ),
            "collaboration": RevenueStreamConfig(
                stream_type=RevenueStreamType.COLLABORATION_FEE,
                commission_rate=Decimal("0.10"),  # 10%
                minimum_payout=Decimal("100.00"),
                payment_frequency="weekly"
            ),
            "premium_content": RevenueStreamConfig(
                stream_type=RevenueStreamType.PREMIUM_CONTENT,
                commission_rate=Decimal("0.12"),  # 12%
                minimum_payout=Decimal("25.00"),
                payment_frequency="weekly"
            ),
            "sponsorship": RevenueStreamConfig(
                stream_type=RevenueStreamType.SPONSORSHIP,
                commission_rate=Decimal("0.08"),  # 8%
                minimum_payout=Decimal("200.00"),
                payment_frequency="monthly"
            )
        }
        
        self.logger.info(f"Initialized {len(self.revenue_streams)} revenue streams")
        
    def _initialize_optimization_rules(self):
        """Initialisation règles optimisation"""
        self.optimization_rules = {
            "tier_based_commission": {
                "starter": Decimal("0.20"),
                "rising": Decimal("0.15"),
                "established": Decimal("0.12"),
                "premium": Decimal("0.10"),
                "vip": Decimal("0.08"),
                "legendary": Decimal("0.05")
            },
            "performance_bonuses": {
                "high_engagement": Decimal("0.02"),  # 2% bonus
                "viral_content": Decimal("0.05"),   # 5% bonus
                "collaboration_success": Decimal("0.03")  # 3% bonus
            },
            "volume_discounts": {
                1000: Decimal("0.01"),   # 1% reduction at €1000+
                5000: Decimal("0.02"),   # 2% reduction at €5000+
                10000: Decimal("0.03")   # 3% reduction at €10000+
            }
        }
        
        self.performance_thresholds = {
            "min_engagement_rate": 0.05,
            "min_content_quality": 0.70,
            "max_refund_rate": 0.02,
            "min_creator_satisfaction": 0.85
        }
        
    def _initialize_tax_compliance(self):
        """Initialisation conformité fiscale"""
        self.compliance_rules = {
            "eu_vat": {
                "applicable": True,
                "rate": Decimal("0.20"),
                "threshold": Decimal("10000.00")
            },
            "us_tax": {
                "applicable": True,
                "w9_required": True,
                "threshold": Decimal("600.00")
            },
            "reporting": {
                "frequency": "quarterly",
                "auto_generation": True,
                "formats": ["pdf", "xml", "csv"]
            }
        }
        
    async def initialize_monetization_orchestrator(self):
        """Initialisation orchestrateur monétisation"""
        self.logger.info("🚀 Initializing Monetization Orchestration Engine...")
        
        # Initialize payment processors (mock implementation)
        await self._initialize_payment_processors()
        
        # Initialize analytics models
        await self._initialize_analytics_models()
        
        # Initialize prediction models
        await self._initialize_prediction_models()
        
        # Start background tasks
        await self._start_background_tasks()
        
        self.logger.info("✅ Monetization Orchestration Engine initialized successfully!")
        
    async def _initialize_payment_processors(self):
        """Initialisation processeurs de paiement"""
        self.payment_processors = {
            "stripe": {
                "enabled": True,
                "commission": Decimal("0.029"),  # 2.9%
                "currencies": ["EUR", "USD", "GBP"],
                "features": ["instant_payouts", "dispute_handling"]
            },
            "paypal": {
                "enabled": True,
                "commission": Decimal("0.034"),  # 3.4%
                "currencies": ["EUR", "USD", "GBP", "CAD"],
                "features": ["buyer_protection", "seller_protection"]
            },
            "crypto": {
                "enabled": True,
                "commission": Decimal("0.015"),  # 1.5%
                "currencies": ["BTC", "ETH", "USDC"],
                "features": ["low_fees", "instant_settlement"]
            }
        }
        
        self.logger.info("Payment processors initialized")
        
    async def _initialize_analytics_models(self):
        """Initialisation modèles analytiques"""
        self.revenue_analytics = {
            "daily_revenue_tracking": {},
            "creator_performance_metrics": {},
            "revenue_stream_analysis": {},
            "seasonal_patterns": {},
            "market_trends": {}
        }
        
    async def _initialize_prediction_models(self):
        """Initialisation modèles prédictifs"""
        self.prediction_models = {
            "revenue_forecasting": {
                "accuracy": 0.87,
                "horizon": "90_days",
                "confidence_interval": 0.95
            },
            "creator_lifetime_value": {
                "accuracy": 0.84,
                "factors": ["engagement", "content_quality", "collaboration_rate"]
            },
            "churn_prediction": {
                "accuracy": 0.91,
                "early_warning_days": 14
            }
        }
        
    async def _start_background_tasks(self):
        """Démarrage tâches arrière-plan"""
        # Schedule revenue optimization
        asyncio.create_task(self._revenue_optimization_task())
        
        # Schedule payout processing
        asyncio.create_task(self._payout_processing_task())
        
        # Schedule analytics updates
        asyncio.create_task(self._analytics_update_task())
        
    async def process_revenue_event(self, creator_id: str, amount: Decimal, 
                                  stream_type: RevenueStreamType, metadata: Dict[str, Any] = None):
        """Traitement événement revenus"""
        try:
            # Create transaction
            transaction = PaymentTransaction(
                transaction_id=str(uuid.uuid4()),
                creator_id=creator_id,
                amount=amount,
                currency="EUR",  # Default currency
                revenue_stream=stream_type,
                status=PaymentStatus.PENDING,
                created_at=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            # Apply optimization rules
            optimized_amount = await self._apply_optimization_rules(
                creator_id, amount, stream_type
            )
            transaction.amount = optimized_amount
            
            # Process transaction
            await self._process_transaction(transaction)
            
            # Update creator earnings
            await self._update_creator_earnings(creator_id, transaction)
            
            # Update analytics
            await self._update_revenue_analytics(transaction)
            
            self.logger.info(f"Revenue event processed: {creator_id} - €{amount} ({stream_type.value})")
            
            return transaction
            
        except Exception as e:
            self.logger.error(f"Error processing revenue event: {e}")
            raise
            
    async def _apply_optimization_rules(self, creator_id: str, amount: Decimal, 
                                      stream_type: RevenueStreamType) -> Decimal:
        """Application règles optimisation"""
        optimized_amount = amount
        
        # Get creator tier (mock implementation)
        creator_tier = await self._get_creator_tier(creator_id)
        
        # Apply tier-based commission reduction
        if creator_tier in self.optimization_rules["tier_based_commission"]:
            commission_rate = self.optimization_rules["tier_based_commission"][creator_tier]
            base_commission = self.revenue_streams.get(stream_type.value, {}).commission_rate or Decimal("0.15")
            
            if commission_rate < base_commission:
                savings = (base_commission - commission_rate) * amount
                optimized_amount += savings
                
        # Apply performance bonuses
        creator_performance = await self._get_creator_performance(creator_id)
        for bonus_type, bonus_rate in self.optimization_rules["performance_bonuses"].items():
            if creator_performance.get(bonus_type, False):
                bonus = amount * bonus_rate
                optimized_amount += bonus
                
        # Apply volume discounts
        monthly_volume = await self._get_creator_monthly_volume(creator_id)
        for threshold, discount_rate in self.optimization_rules["volume_discounts"].items():
            if monthly_volume >= threshold:
                discount = amount * discount_rate
                optimized_amount += discount
                break
                
        return optimized_amount
        
    async def _process_transaction(self, transaction: PaymentTransaction):
        """Traitement transaction"""
        # Simulate payment processing
        transaction.status = PaymentStatus.PROCESSING
        
        # Add to pending transactions
        self.pending_transactions.append(transaction)
        
        # Simulate processing delay (would be actual payment processor integration)
        await asyncio.sleep(0.1)
        
        # Mark as completed
        transaction.status = PaymentStatus.COMPLETED
        transaction.processed_at = datetime.utcnow()
        
        # Move to completed transactions
        self.pending_transactions.remove(transaction)
        self.completed_transactions.append(transaction)
        
    async def _update_creator_earnings(self, creator_id: str, transaction: PaymentTransaction):
        """Mise à jour revenus créateur"""
        if creator_id not in self.creator_earnings:
            self.creator_earnings[creator_id] = CreatorEarnings(
                creator_id=creator_id,
                total_earnings=Decimal("0"),
                pending_earnings=Decimal("0"),
                paid_earnings=Decimal("0"),
                revenue_streams={},
                performance_metrics={},
                optimization_score=0.0
            )
            
        earnings = self.creator_earnings[creator_id]
        
        # Update total earnings
        earnings.total_earnings += transaction.amount
        
        # Update revenue stream breakdown
        if transaction.revenue_stream not in earnings.revenue_streams:
            earnings.revenue_streams[transaction.revenue_stream] = Decimal("0")
        earnings.revenue_streams[transaction.revenue_stream] += transaction.amount
        
        # Update status-based earnings
        if transaction.status == PaymentStatus.COMPLETED:
            earnings.paid_earnings += transaction.amount
        else:
            earnings.pending_earnings += transaction.amount
            
        # Update optimization score
        earnings.optimization_score = await self._calculate_optimization_score(creator_id)
        
    async def _update_revenue_analytics(self, transaction: PaymentTransaction):
        """Mise à jour analytiques revenus"""
        today = datetime.utcnow().date()
        
        # Daily revenue tracking
        if today not in self.revenue_analytics["daily_revenue_tracking"]:
            self.revenue_analytics["daily_revenue_tracking"][today] = {
                "total_revenue": Decimal("0"),
                "transaction_count": 0,
                "unique_creators": set()
            }
            
        daily_data = self.revenue_analytics["daily_revenue_tracking"][today]
        daily_data["total_revenue"] += transaction.amount
        daily_data["transaction_count"] += 1
        daily_data["unique_creators"].add(transaction.creator_id)
        
        # Creator performance metrics
        creator_id = transaction.creator_id
        if creator_id not in self.revenue_analytics["creator_performance_metrics"]:
            self.revenue_analytics["creator_performance_metrics"][creator_id] = {
                "total_revenue": Decimal("0"),
                "avg_transaction": Decimal("0"),
                "revenue_streams": {},
                "growth_rate": 0.0
            }
            
        creator_metrics = self.revenue_analytics["creator_performance_metrics"][creator_id]
        creator_metrics["total_revenue"] += transaction.amount
        
        # Revenue stream analysis
        stream_name = transaction.revenue_stream.value
        if stream_name not in self.revenue_analytics["revenue_stream_analysis"]:
            self.revenue_analytics["revenue_stream_analysis"][stream_name] = {
                "total_revenue": Decimal("0"),
                "transaction_count": 0,
                "avg_amount": Decimal("0")
            }
            
        stream_data = self.revenue_analytics["revenue_stream_analysis"][stream_name]
        stream_data["total_revenue"] += transaction.amount
        stream_data["transaction_count"] += 1
        stream_data["avg_amount"] = stream_data["total_revenue"] / stream_data["transaction_count"]
        
    async def get_creator_revenue_insights(self, creator_id: str) -> Dict[str, Any]:
        """Insights revenus créateur"""
        if creator_id not in self.creator_earnings:
            return {"error": "Creator not found"}
            
        earnings = self.creator_earnings[creator_id]
        
        # Get recent transactions
        recent_transactions = [
            t for t in self.completed_transactions 
            if t.creator_id == creator_id and 
            t.processed_at and t.processed_at > datetime.utcnow() - timedelta(days=30)
        ]
        
        # Calculate growth metrics
        growth_metrics = await self._calculate_creator_growth(creator_id)
        
        # Get optimization recommendations
        optimization_recommendations = await self._get_optimization_recommendations(creator_id)
        
        # Get tax information
        tax_info = await self._calculate_tax_obligations(creator_id)
        
        return {
            "creator_id": creator_id,
            "total_earnings": float(earnings.total_earnings),
            "pending_earnings": float(earnings.pending_earnings),
            "paid_earnings": float(earnings.paid_earnings),
            "revenue_streams": {
                stream.value: float(amount) 
                for stream, amount in earnings.revenue_streams.items()
            },
            "optimization_score": earnings.optimization_score,
            "recent_transactions_count": len(recent_transactions),
            "monthly_average": float(earnings.total_earnings / 12) if earnings.total_earnings > 0 else 0.0,
            "growth_metrics": growth_metrics,
            "optimization_recommendations": optimization_recommendations,
            "tax_obligations": tax_info,
            "next_payout_date": await self._get_next_payout_date(creator_id),
            "performance_tier": await self._get_creator_tier(creator_id)
        }
        
    async def get_monetization_dashboard(self) -> Dict[str, Any]:
        """Dashboard monétisation"""
        total_revenue = sum(
            float(earnings.total_earnings) 
            for earnings in self.creator_earnings.values()
        )
        
        total_pending = sum(
            float(earnings.pending_earnings) 
            for earnings in self.creator_earnings.values()
        )
        
        # Calculate today's metrics
        today = datetime.utcnow().date()
        today_data = self.revenue_analytics["daily_revenue_tracking"].get(today, {
            "total_revenue": Decimal("0"),
            "transaction_count": 0,
            "unique_creators": set()
        })
        
        # Top performing creators
        top_creators = sorted(
            self.creator_earnings.items(),
            key=lambda x: x[1].total_earnings,
            reverse=True
        )[:10]
        
        # Revenue stream breakdown
        stream_breakdown = {}
        for stream_name, data in self.revenue_analytics["revenue_stream_analysis"].items():
            stream_breakdown[stream_name] = {
                "total_revenue": float(data["total_revenue"]),
                "transaction_count": data["transaction_count"],
                "average_amount": float(data["avg_amount"])
            }
            
        return {
            "total_platform_revenue": total_revenue,
            "total_pending_payouts": total_pending,
            "active_creators": len(self.creator_earnings),
            "total_transactions": len(self.completed_transactions),
            "today_revenue": float(today_data["total_revenue"]),
            "today_transactions": today_data["transaction_count"],
            "today_active_creators": len(today_data["unique_creators"]),
            "revenue_streams": stream_breakdown,
            "top_creators": [
                {
                    "creator_id": creator_id,
                    "total_earnings": float(earnings.total_earnings),
                    "optimization_score": earnings.optimization_score
                }
                for creator_id, earnings in top_creators
            ],
            "platform_metrics": {
                "average_creator_revenue": total_revenue / len(self.creator_earnings) if self.creator_earnings else 0,
                "revenue_growth_rate": await self._calculate_platform_growth_rate(),
                "creator_satisfaction_score": await self._calculate_creator_satisfaction(),
                "payout_efficiency": await self._calculate_payout_efficiency()
            }
        }
        
    async def _revenue_optimization_task(self):
        """Tâche optimisation revenus"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Analyze creator performance
                for creator_id in self.creator_earnings.keys():
                    await self._optimize_creator_revenue(creator_id)
                    
                # Update optimization rules based on performance
                await self._update_optimization_rules()
                
                self.logger.info("Revenue optimization cycle completed")
                
            except Exception as e:
                self.logger.error(f"Error in revenue optimization task: {e}")
                
    async def _payout_processing_task(self):
        """Tâche traitement payouts"""
        while True:
            try:
                await asyncio.sleep(86400)  # Run daily
                
                # Process scheduled payouts
                await self._process_scheduled_payouts()
                
                # Update payout schedules
                await self._update_payout_schedules()
                
                self.logger.info("Payout processing cycle completed")
                
            except Exception as e:
                self.logger.error(f"Error in payout processing task: {e}")
                
    async def _analytics_update_task(self):
        """Tâche mise à jour analytiques"""
        while True:
            try:
                await asyncio.sleep(1800)  # Run every 30 minutes
                
                # Update analytics models
                await self._update_analytics_models()
                
                # Generate insights
                await self._generate_business_insights()
                
                self.logger.info("Analytics update cycle completed")
                
            except Exception as e:
                self.logger.error(f"Error in analytics update task: {e}")
                
    # Helper methods (mock implementations for now)
    async def _get_creator_tier(self, creator_id: str) -> str:
        """Get creator tier"""
        return "established"  # Mock implementation
        
    async def _get_creator_performance(self, creator_id: str) -> Dict[str, bool]:
        """Get creator performance indicators"""
        return {
            "high_engagement": True,
            "viral_content": False,
            "collaboration_success": True
        }
        
    async def _get_creator_monthly_volume(self, creator_id: str) -> Decimal:
        """Get creator monthly volume"""
        return Decimal("2500.00")  # Mock implementation
        
    async def _calculate_optimization_score(self, creator_id: str) -> float:
        """Calculate optimization score"""
        return 0.85  # Mock implementation
        
    async def _calculate_creator_growth(self, creator_id: str) -> Dict[str, Any]:
        """Calculate creator growth metrics"""
        return {
            "monthly_growth_rate": 0.15,
            "quarterly_growth_rate": 0.45,
            "year_over_year": 2.3
        }
        
    async def _get_optimization_recommendations(self, creator_id: str) -> List[Dict[str, Any]]:
        """Get optimization recommendations"""
        return [
            {
                "recommendation": "increase_premium_content_ratio",
                "impact": "revenue_increase_12_percent",
                "effort": "medium",
                "timeline": "2_weeks"
            },
            {
                "recommendation": "optimize_collaboration_frequency",
                "impact": "revenue_increase_8_percent",
                "effort": "low",
                "timeline": "1_week"
            }
        ]
        
    async def _calculate_tax_obligations(self, creator_id: str) -> Dict[str, Any]:
        """Calculate tax obligations"""
        return {
            "jurisdiction": "EU",
            "vat_applicable": True,
            "estimated_quarterly_tax": 450.00,
            "documents_required": ["invoice_template", "vat_registration"]
        }
        
    async def _get_next_payout_date(self, creator_id: str) -> str:
        """Get next payout date"""
        next_week = datetime.utcnow() + timedelta(days=7)
        return next_week.isoformat()
        
    async def _calculate_platform_growth_rate(self) -> float:
        """Calculate platform growth rate"""
        return 0.25  # 25% growth rate
        
    async def _calculate_creator_satisfaction(self) -> float:
        """Calculate creator satisfaction score"""
        return 0.89  # 89% satisfaction
        
    async def _calculate_payout_efficiency(self) -> float:
        """Calculate payout efficiency"""
        return 0.96  # 96% efficiency
        
    async def _optimize_creator_revenue(self, creator_id: str):
        """Optimize individual creator revenue"""
        # Mock implementation
        pass
        
    async def _update_optimization_rules(self):
        """Update optimization rules"""
        # Mock implementation
        pass
        
    async def _process_scheduled_payouts(self):
        """Process scheduled payouts"""
        # Mock implementation
        pass
        
    async def _update_payout_schedules(self):
        """Update payout schedules"""
        # Mock implementation
        pass
        
    async def _update_analytics_models(self):
        """Update analytics models"""
        # Mock implementation
        pass
        
    async def _generate_business_insights(self):
        """Generate business insights"""
        # Mock implementation
        pass
        
    async def shutdown(self):
        """Arrêt propre du moteur"""
        self.logger.info("⏹️ Shutting down Monetization Orchestration Engine...")
        
        # Process remaining transactions
        for transaction in self.pending_transactions:
            await self._process_transaction(transaction)
            
        # Save analytics data
        await self._save_analytics_data()
        
        # Clear memory
        self.creator_earnings.clear()
        self.pending_transactions.clear()
        self.completed_transactions.clear()
        
        self.logger.info("✅ Monetization Orchestration Engine shutdown completed")
        
    async def _save_analytics_data(self):
        """Save analytics data"""
        # Mock implementation - would save to database
        self.logger.info("Analytics data saved")


# Point d'entrée principal pour tests
if __name__ == "__main__":
    async def test_monetization():
        engine = MonetizationOrchestrationEngine()
        await engine.initialize_monetization_orchestrator()
        
        # Test revenue processing
        await engine.process_revenue_event(
            creator_id="creator_123",
            amount=Decimal("150.00"),
            stream_type=RevenueStreamType.SUBSCRIPTION,
            metadata={"platform": "web", "tier": "premium"}
        )
        
        # Get insights
        insights = await engine.get_creator_revenue_insights("creator_123")
        print("Creator insights:", json.dumps(insights, indent=2, default=str))
        
        # Get dashboard
        dashboard = await engine.get_monetization_dashboard()
        print("Dashboard:", json.dumps(dashboard, indent=2, default=str))
        
        await engine.shutdown()
        
    asyncio.run(test_monetization())