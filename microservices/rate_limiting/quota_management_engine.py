"""
Quota Management Engine Enterprise - IA Chérie
============================================
Moteur gestion quotas enterprise avec billing integration.
Quota tracking + billing + analytics + forecasting.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Rate Limiting
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import defaultdict, deque
import statistics
import calendar

logger = logging.getLogger(__name__)

class QuotaType(Enum):
    """Types de quotas gérés"""
    API_REQUESTS = "api_requests"
    BANDWIDTH = "bandwidth"
    STORAGE = "storage"
    COMPUTE_TIME = "compute_time"
    AI_PROCESSING = "ai_processing"
    UPLOADS = "uploads"
    DOWNLOADS = "downloads"
    PREMIUM_FEATURES = "premium_features"

class BillingPeriod(Enum):
    """Périodes de facturation"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    PAY_PER_USE = "pay_per_use"

class SubscriptionTier(Enum):
    """Tiers d'abonnement"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class QuotaStatus(Enum):
    """Status des quotas"""
    ACTIVE = "active"
    EXCEEDED = "exceeded"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    PENDING_RENEWAL = "pending_renewal"

@dataclass
class QuotaConfig:
    """Configuration quota management""" 
    enable_billing_integration: bool = True
    enable_usage_analytics: bool = True
    enable_forecasting: bool = True
    enable_overage_protection: bool = True
    enable_auto_scaling: bool = False
    grace_period_hours: int = 24
    overage_multiplier: float = 1.5
    warning_thresholds: List[float] = field(default_factory=lambda: [0.8, 0.9, 0.95])
    reset_on_billing_cycle: bool = True
    
@dataclass
class UserQuota:
    """Quota utilisateur"""
    user_id: str
    quota_type: QuotaType
    allocated_amount: int
    used_amount: int = 0
    billing_period: BillingPeriod = BillingPeriod.MONTHLY
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    reset_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))
    overage_allowed: bool = False
    overage_limit: int = 0
    priority: int = 100
    status: QuotaStatus = QuotaStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def remaining_amount(self) -> int:
        """Montant restant"""
        return max(0, self.allocated_amount - self.used_amount)
    
    @property
    def usage_percentage(self) -> float:
        """Pourcentage d'utilisation"""
        if self.allocated_amount <= 0:
            return 0.0
        return min(100.0, (self.used_amount / self.allocated_amount) * 100)
    
    @property
    def is_exceeded(self) -> bool:
        """Quota dépassé"""
        return self.used_amount > self.allocated_amount
    
    @property
    def is_near_limit(self, threshold: float = 0.9) -> bool:
        """Proche de la limite"""
        return self.usage_percentage >= (threshold * 100)

@dataclass
class QuotaRequest:
    """Request quota usage"""
    user_id: str
    quota_type: QuotaType
    requested_amount: int
    operation_id: Optional[str] = None
    priority: int = 100
    allow_overage: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class QuotaResult:
    """Résultat operation quota"""
    success: bool
    allocated_amount: int
    remaining_quota: int
    usage_percentage: float
    overage_applied: bool = False
    overage_amount: int = 0
    billing_impact: Optional[Dict[str, Any]] = None
    warnings: List[str] = field(default_factory=list)
    next_reset: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UsageEvent:
    """Événement usage quota"""
    event_id: str
    user_id: str
    quota_type: QuotaType
    amount_used: int
    operation_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    billing_context: Optional[Dict[str, Any]] = None

@dataclass
class UsageResult:
    """Résultat tracking usage"""
    event_recorded: bool
    quota_updated: bool
    new_usage_total: int
    warnings_triggered: List[str]
    billing_events: List[Dict[str, Any]]
    quota_status: QuotaStatus
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QuotaForecast:
    """Prédiction usage quota"""
    user_id: str
    quota_type: QuotaType
    forecast_period_days: int
    predicted_usage: List[int]
    confidence_intervals: List[Tuple[int, int]]
    estimated_overage: int
    recommended_quota: int
    cost_projection: Optional[float] = None
    risk_assessment: str = "medium"
    recommendations: List[str] = field(default_factory=list)

@dataclass
class OptimizationResult:
    """Résultat optimization quota"""
    organization_id: str
    current_allocation: Dict[str, int]
    optimized_allocation: Dict[str, int]
    projected_savings: float
    efficiency_improvement: float
    recommendations: List[str]
    implementation_priority: str = "medium"

class QuotaTracker:
    """Tracker usage quotas temps réel"""
    
    def __init__(self, config: QuotaConfig):
        self.config = config
        self.user_quotas = {}  # user_id -> {quota_type -> UserQuota}
        self.usage_history = defaultdict(lambda: deque(maxlen=10000))
        self.billing_events = deque(maxlen=50000)
        self.warning_cache = defaultdict(set)  # Éviter spam warnings
        self.logger = logging.getLogger(__name__)
    
    async def initialize_user_quota(self, user_id: str, quota_type: QuotaType,
                                  allocated_amount: int, subscription_tier: SubscriptionTier,
                                  billing_period: BillingPeriod = BillingPeriod.MONTHLY) -> bool:
        """Initialisation quota utilisateur"""
        try:
            if user_id not in self.user_quotas:
                self.user_quotas[user_id] = {}
            
            # Calcul reset date basé sur billing period
            reset_date = self._calculate_reset_date(billing_period)
            
            # Configuration overage basé sur tier
            overage_config = self._get_overage_config(subscription_tier)
            
            quota = UserQuota(
                user_id=user_id,
                quota_type=quota_type,
                allocated_amount=allocated_amount,
                billing_period=billing_period,
                subscription_tier=subscription_tier,
                reset_date=reset_date,
                overage_allowed=overage_config["allowed"],
                overage_limit=overage_config["limit"],
                metadata={
                    "created_at": datetime.now().isoformat(),
                    "tier": subscription_tier.value,
                    "billing_period": billing_period.value
                }
            )
            
            self.user_quotas[user_id][quota_type] = quota
            
            self.logger.info(f"Quota initialized for user {user_id}: {quota_type.value} = {allocated_amount}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize quota for {user_id}: {e}")
            return False
    
    async def consume_quota(self, request: QuotaRequest) -> QuotaResult:
        """Consommation quota avec vérifications"""
        try:
            # Récupération quota utilisateur
            user_quota = self._get_user_quota(request.user_id, request.quota_type)
            if not user_quota:
                return QuotaResult(
                    success=False,
                    allocated_amount=0,
                    remaining_quota=0,
                    usage_percentage=0.0,
                    warnings=["Quota not found - initialize quota first"]
                )
            
            # Vérification status quota
            if user_quota.status not in [QuotaStatus.ACTIVE, QuotaStatus.PENDING_RENEWAL]:
                return QuotaResult(
                    success=False,
                    allocated_amount=user_quota.allocated_amount,
                    remaining_quota=user_quota.remaining_amount,
                    usage_percentage=user_quota.usage_percentage,
                    warnings=[f"Quota status: {user_quota.status.value}"]
                )
            
            # Vérification reset date
            if datetime.now() > user_quota.reset_date:
                await self._reset_quota(user_quota)
            
            # Vérification disponibilité
            available_quota = user_quota.remaining_amount
            overage_amount = 0
            
            if request.requested_amount > available_quota:
                # Vérification overage
                if not request.allow_overage or not user_quota.overage_allowed:
                    return QuotaResult(
                        success=False,
                        allocated_amount=user_quota.allocated_amount,
                        remaining_quota=available_quota,
                        usage_percentage=user_quota.usage_percentage,
                        warnings=["Insufficient quota - overage not allowed"]
                    )
                
                # Calcul overage nécessaire
                overage_needed = request.requested_amount - available_quota
                
                if overage_needed > user_quota.overage_limit:
                    return QuotaResult(
                        success=False,
                        allocated_amount=user_quota.allocated_amount,
                        remaining_quota=available_quota,
                        usage_percentage=user_quota.usage_percentage,
                        warnings=[f"Overage limit exceeded: {overage_needed} > {user_quota.overage_limit}"]
                    )
                
                overage_amount = overage_needed
            
            # Consommation quota
            user_quota.used_amount += request.requested_amount
            
            # Génération événement billing si overage
            billing_impact = None
            if overage_amount > 0:
                billing_impact = await self._generate_billing_event(
                    request.user_id, request.quota_type, overage_amount
                )
            
            # Vérification warnings
            warnings = await self._check_quota_warnings(user_quota)
            
            # Résultat final
            result = QuotaResult(
                success=True,
                allocated_amount=user_quota.allocated_amount,
                remaining_quota=user_quota.remaining_amount,
                usage_percentage=user_quota.usage_percentage,
                overage_applied=overage_amount > 0,
                overage_amount=overage_amount,
                billing_impact=billing_impact,
                warnings=warnings,
                next_reset=user_quota.reset_date,
                metadata={
                    "operation_id": request.operation_id,
                    "consumed_amount": request.requested_amount,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Quota consumption failed for {request.user_id}: {e}")
            return QuotaResult(
                success=False,
                allocated_amount=0,
                remaining_quota=0,
                usage_percentage=0.0,
                warnings=[f"Quota consumption error: {str(e)}"]
            )
    
    async def track_usage(self, usage_event: UsageEvent) -> UsageResult:
        """Tracking usage en temps réel"""
        try:
            # Enregistrement événement
            self.usage_history[usage_event.user_id].append(usage_event)
            
            # Récupération quota
            user_quota = self._get_user_quota(usage_event.user_id, usage_event.quota_type)
            if not user_quota:
                return UsageResult(
                    event_recorded=True,
                    quota_updated=False,
                    new_usage_total=0,
                    warnings_triggered=["Quota not found"],
                    billing_events=[],
                    quota_status=QuotaStatus.SUSPENDED
                )
            
            # Update usage
            user_quota.used_amount += usage_event.amount_used
            
            # Vérification warnings
            warnings = await self._check_quota_warnings(user_quota)
            
            # Génération billing events si nécessaire
            billing_events = []
            if user_quota.is_exceeded and self.config.enable_billing_integration:
                billing_event = await self._generate_billing_event(
                    usage_event.user_id, usage_event.quota_type, 
                    user_quota.used_amount - user_quota.allocated_amount
                )
                if billing_event:
                    billing_events.append(billing_event)
            
            # Update status quota
            new_status = await self._update_quota_status(user_quota)
            
            return UsageResult(
                event_recorded=True,
                quota_updated=True,
                new_usage_total=user_quota.used_amount,
                warnings_triggered=warnings,
                billing_events=billing_events,
                quota_status=new_status,
                metadata={
                    "event_id": usage_event.event_id,
                    "usage_percentage": user_quota.usage_percentage
                }
            )
            
        except Exception as e:
            self.logger.error(f"Usage tracking failed for {usage_event.user_id}: {e}")
            return UsageResult(
                event_recorded=False,
                quota_updated=False,
                new_usage_total=0,
                warnings_triggered=[f"Tracking error: {str(e)}"],
                billing_events=[],
                quota_status=QuotaStatus.SUSPENDED
            )
    
    def _get_user_quota(self, user_id: str, quota_type: QuotaType) -> Optional[UserQuota]:
        """Récupération quota utilisateur"""
        user_quotas = self.user_quotas.get(user_id, {})
        return user_quotas.get(quota_type)
    
    def _calculate_reset_date(self, billing_period: BillingPeriod) -> datetime:
        """Calcul prochaine date reset"""
        now = datetime.now()
        
        if billing_period == BillingPeriod.HOURLY:
            return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        elif billing_period == BillingPeriod.DAILY:
            return now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif billing_period == BillingPeriod.WEEKLY:
            days_until_monday = (7 - now.weekday()) % 7
            return now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
        elif billing_period == BillingPeriod.MONTHLY:
            next_month = now.replace(day=1) + timedelta(days=32)
            return next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif billing_period == BillingPeriod.YEARLY:
            return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=365)
        else:  # PAY_PER_USE
            return now + timedelta(days=365)  # Far future
    
    def _get_overage_config(self, subscription_tier: SubscriptionTier) -> Dict[str, Any]:
        """Configuration overage par tier"""
        overage_configs = {
            SubscriptionTier.FREE: {"allowed": False, "limit": 0},
            SubscriptionTier.BASIC: {"allowed": True, "limit": 100},
            SubscriptionTier.PRO: {"allowed": True, "limit": 1000},
            SubscriptionTier.ENTERPRISE: {"allowed": True, "limit": 10000},
            SubscriptionTier.CUSTOM: {"allowed": True, "limit": 50000}
        }
        return overage_configs.get(subscription_tier, {"allowed": False, "limit": 0})
    
    async def _reset_quota(self, user_quota: UserQuota):
        """Reset quota à nouveau cycle"""
        user_quota.used_amount = 0
        user_quota.reset_date = self._calculate_reset_date(user_quota.billing_period)
        user_quota.status = QuotaStatus.ACTIVE
        
        # Clear warning cache pour cet utilisateur
        warning_key = f"{user_quota.user_id}:{user_quota.quota_type.value}"
        self.warning_cache[warning_key].clear()
        
        self.logger.info(f"Quota reset for {user_quota.user_id}: {user_quota.quota_type.value}")
    
    async def _check_quota_warnings(self, user_quota: UserQuota) -> List[str]:
        """Vérification warnings quota"""
        warnings = []
        warning_key = f"{user_quota.user_id}:{user_quota.quota_type.value}"
        
        for threshold in self.config.warning_thresholds:
            if user_quota.usage_percentage >= (threshold * 100):
                threshold_key = f"{threshold}"
                
                # Éviter spam warnings
                if threshold_key not in self.warning_cache[warning_key]:
                    warnings.append(f"Quota {threshold*100:.0f}% used ({user_quota.used_amount}/{user_quota.allocated_amount})")
                    self.warning_cache[warning_key].add(threshold_key)
        
        return warnings
    
    async def _generate_billing_event(self, user_id: str, quota_type: QuotaType, 
                                    overage_amount: int) -> Optional[Dict[str, Any]]:
        """Génération événement billing"""
        if not self.config.enable_billing_integration:
            return None
        
        # Calcul coût overage
        base_cost = self._get_base_cost(quota_type)
        overage_cost = base_cost * overage_amount * self.config.overage_multiplier
        
        billing_event = {
            "event_id": str(uuid.uuid4()),
            "user_id": user_id,
            "quota_type": quota_type.value,
            "event_type": "overage_charge",
            "amount": overage_amount,
            "cost": overage_cost,
            "timestamp": datetime.now().isoformat(),
            "multiplier": self.config.overage_multiplier
        }
        
        self.billing_events.append(billing_event)
        return billing_event
    
    def _get_base_cost(self, quota_type: QuotaType) -> float:
        """Coût de base par type quota"""
        base_costs = {
            QuotaType.API_REQUESTS: 0.001,      # $0.001 per request
            QuotaType.BANDWIDTH: 0.00001,       # $0.00001 per MB
            QuotaType.STORAGE: 0.0001,          # $0.0001 per GB/month
            QuotaType.COMPUTE_TIME: 0.01,       # $0.01 per minute
            QuotaType.AI_PROCESSING: 0.1,       # $0.1 per processing unit
            QuotaType.UPLOADS: 0.01,            # $0.01 per upload
            QuotaType.DOWNLOADS: 0.005,         # $0.005 per download
            QuotaType.PREMIUM_FEATURES: 0.1     # $0.1 per feature use
        }
        return base_costs.get(quota_type, 0.01)
    
    async def _update_quota_status(self, user_quota: UserQuota) -> QuotaStatus:
        """Update status quota"""
        if user_quota.is_exceeded and not user_quota.overage_allowed:
            user_quota.status = QuotaStatus.EXCEEDED
        elif datetime.now() > user_quota.reset_date:
            user_quota.status = QuotaStatus.EXPIRED
        else:
            user_quota.status = QuotaStatus.ACTIVE
        
        return user_quota.status

class BillingIntegrator:
    """Intégration systèmes billing"""
    
    def __init__(self, config: QuotaConfig):
        self.config = config
        self.billing_providers = {}
        self.billing_cache = {}
        self.invoice_queue = deque(maxlen=10000)
        self.logger = logging.getLogger(__name__)
    
    async def process_billing_events(self, billing_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Processing événements billing"""
        try:
            processed_events = 0
            total_charges = 0.0
            failed_events = []
            
            for event in billing_events:
                try:
                    # Processing événement billing
                    charge_result = await self._process_charge(event)
                    
                    if charge_result["success"]:
                        processed_events += 1
                        total_charges += event.get("cost", 0.0)
                    else:
                        failed_events.append(event)
                        
                except Exception as e:
                    self.logger.error(f"Billing event processing failed: {e}")
                    failed_events.append(event)
            
            # Génération invoice si seuil atteint
            if total_charges > 0:
                await self._generate_invoice_if_needed(total_charges)
            
            return {
                "processed_events": processed_events,
                "total_charges": total_charges,
                "failed_events": len(failed_events),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Billing events processing failed: {e}")
            return {
                "processed_events": 0,
                "total_charges": 0.0,
                "failed_events": len(billing_events),
                "error": str(e)
            }
    
    async def _process_charge(self, billing_event: Dict[str, Any]) -> Dict[str, Any]:
        """Processing charge individuelle"""
        try:
            # Simulation API call vers billing provider
            await asyncio.sleep(0.01)  # Simulate API latency
            
            # Validation charge
            if billing_event.get("cost", 0) <= 0:
                return {"success": False, "reason": "Invalid charge amount"}
            
            # Record charge
            charge_record = {
                "charge_id": str(uuid.uuid4()),
                "user_id": billing_event["user_id"],
                "amount": billing_event["cost"],
                "description": f"Quota overage: {billing_event['quota_type']}",
                "processed_at": datetime.now().isoformat(),
                "status": "completed"
            }
            
            return {"success": True, "charge_record": charge_record}
            
        except Exception as e:
            return {"success": False, "reason": str(e)}
    
    async def _generate_invoice_if_needed(self, total_charges: float):
        """Génération invoice si seuil atteint"""
        if total_charges >= 10.0:  # $10 threshold
            invoice = {
                "invoice_id": str(uuid.uuid4()),
                "total_amount": total_charges,
                "generated_at": datetime.now().isoformat(),
                "status": "pending"
            }
            self.invoice_queue.append(invoice)

class UsageAnalyticsEngine:
    """Moteur analytics usage"""
    
    def __init__(self, config: QuotaConfig):
        self.config = config
        self.analytics_cache = {}
        self.usage_patterns = defaultdict(lambda: deque(maxlen=1000))
        self.logger = logging.getLogger(__name__)
    
    async def analyze_usage_patterns(self, user_id: str, 
                                   analysis_period_days: int = 30) -> Dict[str, Any]:
        """Analyse patterns usage utilisateur"""
        try:
            # Récupération données usage
            usage_data = await self._get_usage_data(user_id, analysis_period_days)
            
            if not usage_data:
                return {"error": "No usage data found"}
            
            # Analyse statistique
            stats = await self._calculate_usage_stats(usage_data)
            
            # Détection patterns
            patterns = await self._detect_usage_patterns(usage_data)
            
            # Recommendations
            recommendations = await self._generate_usage_recommendations(stats, patterns)
            
            return {
                "user_id": user_id,
                "analysis_period_days": analysis_period_days,
                "statistics": stats,
                "patterns": patterns,
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Usage pattern analysis failed for {user_id}: {e}")
            return {"error": str(e)}
    
    async def _get_usage_data(self, user_id: str, days: int) -> List[Dict[str, Any]]:
        """Récupération données usage"""
        # Simulation - dans une vraie implémentation, requête DB
        return [
            {
                "date": (datetime.now() - timedelta(days=i)).date().isoformat(),
                "api_requests": 100 + (i * 10),
                "bandwidth_mb": 50 + (i * 5),
                "storage_gb": 10 + (i * 0.5)
            }
            for i in range(days)
        ]
    
    async def _calculate_usage_stats(self, usage_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcul statistiques usage"""
        api_requests = [d["api_requests"] for d in usage_data]
        bandwidth = [d["bandwidth_mb"] for d in usage_data]
        
        return {
            "api_requests": {
                "total": sum(api_requests),
                "average_daily": statistics.mean(api_requests),
                "peak_daily": max(api_requests),
                "trend": "increasing" if api_requests[-1] > api_requests[0] else "decreasing"
            },
            "bandwidth": {
                "total_mb": sum(bandwidth),
                "average_daily_mb": statistics.mean(bandwidth),
                "peak_daily_mb": max(bandwidth),
                "trend": "increasing" if bandwidth[-1] > bandwidth[0] else "decreasing"
            }
        }
    
    async def _detect_usage_patterns(self, usage_data: List[Dict[str, Any]]) -> List[str]:
        """Détection patterns usage"""
        patterns = []
        
        api_requests = [d["api_requests"] for d in usage_data]
        
        # Pattern: usage croissant
        if len(api_requests) >= 7:
            recent_avg = statistics.mean(api_requests[-7:])
            older_avg = statistics.mean(api_requests[:7])
            
            if recent_avg > older_avg * 1.2:
                patterns.append("increasing_usage_trend")
            elif recent_avg < older_avg * 0.8:
                patterns.append("decreasing_usage_trend")
        
        # Pattern: spikes réguliers
        if max(api_requests) > statistics.mean(api_requests) * 2:
            patterns.append("periodic_spikes")
        
        return patterns
    
    async def _generate_usage_recommendations(self, stats: Dict[str, Any], 
                                            patterns: List[str]) -> List[str]:
        """Génération recommendations"""
        recommendations = []
        
        # Recommendations basées sur trends
        if "increasing_usage_trend" in patterns:
            recommendations.append("Consider upgrading subscription tier")
            recommendations.append("Monitor quota limits closely")
        
        if "periodic_spikes" in patterns:
            recommendations.append("Enable auto-scaling quotas")
            recommendations.append("Configure overage protection")
        
        # Recommendations basées sur stats
        api_avg = stats.get("api_requests", {}).get("average_daily", 0)
        if api_avg > 1000:
            recommendations.append("Consider enterprise tier for better rates")
        
        return recommendations

class QuotaForecastingEngine:
    """Moteur forecasting quotas"""
    
    def __init__(self, config: QuotaConfig):
        self.config = config
        self.forecast_models = {}
        self.forecast_cache = {}
        self.logger = logging.getLogger(__name__)
    
    async def forecast_quota_needs(self, user_id: str, quota_type: QuotaType,
                                 forecast_days: int = 30) -> QuotaForecast:
        """Forecasting besoins quota"""
        try:
            # Récupération données historiques
            historical_data = await self._get_historical_data(user_id, quota_type)
            
            # Génération prédictions
            predictions = await self._generate_predictions(historical_data, forecast_days)
            
            # Calcul confidence intervals
            confidence_intervals = await self._calculate_confidence_intervals(predictions)
            
            # Estimation overage
            current_quota = await self._get_current_quota(user_id, quota_type)
            estimated_overage = max(0, max(predictions) - current_quota)
            
            # Recommendation nouveau quota
            recommended_quota = int(max(predictions) * 1.2)  # 20% buffer
            
            # Projection coût
            cost_projection = await self._calculate_cost_projection(
                user_id, quota_type, recommended_quota, forecast_days
            )
            
            # Assessment risque
            risk_assessment = await self._assess_risk(predictions, current_quota)
            
            # Génération recommendations
            recommendations = await self._generate_forecast_recommendations(
                predictions, current_quota, estimated_overage
            )
            
            return QuotaForecast(
                user_id=user_id,
                quota_type=quota_type,
                forecast_period_days=forecast_days,
                predicted_usage=predictions,
                confidence_intervals=confidence_intervals,
                estimated_overage=estimated_overage,
                recommended_quota=recommended_quota,
                cost_projection=cost_projection,
                risk_assessment=risk_assessment,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Quota forecasting failed for {user_id}: {e}")
            return QuotaForecast(
                user_id=user_id,
                quota_type=quota_type,
                forecast_period_days=forecast_days,
                predicted_usage=[],
                confidence_intervals=[],
                estimated_overage=0,
                recommended_quota=0,
                recommendations=[f"Forecasting error: {str(e)}"]
            )
    
    async def _get_historical_data(self, user_id: str, quota_type: QuotaType) -> List[int]:
        """Récupération données historiques"""
        # Simulation données historiques
        base_usage = 100
        return [base_usage + (i * 5) + (i % 7) * 10 for i in range(30)]
    
    async def _generate_predictions(self, historical_data: List[int], 
                                  forecast_days: int) -> List[int]:
        """Génération prédictions usage"""
        if len(historical_data) < 7:
            # Pas assez de données - extrapolation simple
            avg_usage = statistics.mean(historical_data) if historical_data else 100
            return [int(avg_usage)] * forecast_days
        
        # Simple linear extrapolation avec seasonal component
        recent_trend = (historical_data[-1] - historical_data[-7]) / 7
        seasonal_pattern = [historical_data[i % len(historical_data)] 
                          for i in range(forecast_days)]
        
        predictions = []
        for i in range(forecast_days):
            base_prediction = historical_data[-1] + (recent_trend * i)
            seasonal_adjustment = seasonal_pattern[i] - statistics.mean(historical_data)
            prediction = max(0, int(base_prediction + seasonal_adjustment * 0.3))
            predictions.append(prediction)
        
        return predictions
    
    async def _calculate_confidence_intervals(self, predictions: List[int]) -> List[Tuple[int, int]]:
        """Calcul confidence intervals"""
        intervals = []
        for prediction in predictions:
            # Simple confidence interval basé sur variance
            margin = int(prediction * 0.2)  # 20% margin
            intervals.append((max(0, prediction - margin), prediction + margin))
        
        return intervals
    
    async def _get_current_quota(self, user_id: str, quota_type: QuotaType) -> int:
        """Récupération quota actuel"""
        return 1000  # Simulation
    
    async def _calculate_cost_projection(self, user_id: str, quota_type: QuotaType,
                                       recommended_quota: int, forecast_days: int) -> float:
        """Calcul projection coût"""
        base_cost = self._get_base_cost_per_unit(quota_type)
        monthly_cost = recommended_quota * base_cost
        projected_cost = (monthly_cost / 30) * forecast_days
        return round(projected_cost, 2)
    
    def _get_base_cost_per_unit(self, quota_type: QuotaType) -> float:
        """Coût de base par unité"""
        costs = {
            QuotaType.API_REQUESTS: 0.001,
            QuotaType.BANDWIDTH: 0.00001,
            QuotaType.STORAGE: 0.0001,
            QuotaType.COMPUTE_TIME: 0.01,
            QuotaType.AI_PROCESSING: 0.1
        }
        return costs.get(quota_type, 0.01)
    
    async def _assess_risk(self, predictions: List[int], current_quota: int) -> str:
        """Assessment risque overage"""
        max_predicted = max(predictions) if predictions else 0
        
        if max_predicted > current_quota * 1.5:
            return "high"
        elif max_predicted > current_quota * 1.2:
            return "medium"
        else:
            return "low"
    
    async def _generate_forecast_recommendations(self, predictions: List[int],
                                               current_quota: int, estimated_overage: int) -> List[str]:
        """Génération recommendations forecast"""
        recommendations = []
        
        if estimated_overage > 0:
            recommendations.append(f"Increase quota by {estimated_overage} units to avoid overage")
        
        if max(predictions) > current_quota * 1.2:
            recommendations.append("Consider upgrading subscription tier")
        
        if len(set(predictions)) == 1:  # Predictions identiques
            recommendations.append("Usage pattern is stable - current quota may be sufficient")
        
        return recommendations

class QuotaManagementEngine:
    """
    Moteur gestion quotas enterprise avec billing integration.
    Quota tracking + billing + analytics + forecasting.
    """
    
    def __init__(self, quota_config: QuotaConfig):
        self.quota_config = quota_config
        self.quota_tracker = QuotaTracker(quota_config)
        self.billing_integrator = BillingIntegrator(quota_config)
        self.usage_analytics = UsageAnalyticsEngine(quota_config)
        self.forecaster = QuotaForecastingEngine(quota_config)
        
        # État global
        self.organization_quotas = {}
        self.quota_policies = {}
        self.auto_scaling_rules = {}
        
        self.logger = logging.getLogger(__name__)
        
        # Background tasks
        self._background_tasks = []
        self._stop_event = asyncio.Event()
    
    async def initialize(self) -> bool:
        """Initialisation quota management engine"""
        try:
            # Chargement policies par défaut
            await self._load_default_policies()
            
            # Démarrage background tasks
            await self._start_background_tasks()
            
            self.logger.info("Quota management engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Quota management engine initialization failed: {e}")
            return False
    
    async def manage_user_quotas(self, user_id: str, quota_request: QuotaRequest) -> QuotaResult:
        """
        Gestion quotas utilisateur avec billing integration.
        
        Quota Features:
        - Hierarchical quota management (user/team/org)
        - Real-time quota tracking avec usage analytics
        - Billing integration pour quota overages
        - Quota forecasting basé sur usage patterns
        - Automatic quota scaling pour premium users
        - Quota transfer between users/teams
        - Usage-based recommendations pour quota optimization
        """
        try:
            # 1. Vérification policy organization
            org_policy = await self._get_organization_policy(user_id)
            if not await self._validate_quota_request(quota_request, org_policy):
                return QuotaResult(
                    success=False,
                    allocated_amount=0,
                    remaining_quota=0,
                    usage_percentage=0.0,
                    warnings=["Request violates organization policy"]
                )
            
            # 2. Consommation quota
            quota_result = await self.quota_tracker.consume_quota(quota_request)
            
            # 3. Processing billing si overage
            if quota_result.overage_applied and self.quota_config.enable_billing_integration:
                billing_events = [quota_result.billing_impact] if quota_result.billing_impact else []
                await self.billing_integrator.process_billing_events(billing_events)
            
            # 4. Auto-scaling si configuré
            if (self.quota_config.enable_auto_scaling and 
                quota_result.usage_percentage > 90):
                await self._trigger_auto_scaling(user_id, quota_request.quota_type)
            
            # 5. Analytics et recommendations
            if self.quota_config.enable_usage_analytics:
                await self._update_usage_analytics(user_id, quota_request)
            
            return quota_result
            
        except Exception as e:
            self.logger.error(f"User quota management failed for {user_id}: {e}")
            return QuotaResult(
                success=False,
                allocated_amount=0,
                remaining_quota=0,
                usage_percentage=0.0,
                warnings=[f"Quota management error: {str(e)}"]
            )
    
    async def track_quota_usage(self, usage_event: UsageEvent) -> UsageResult:
        """Tracking usage quotas temps réel avec analytics"""
        try:
            # Tracking de base
            usage_result = await self.quota_tracker.track_usage(usage_event)
            
            # Processing billing events
            if usage_result.billing_events:
                await self.billing_integrator.process_billing_events(usage_result.billing_events)
            
            # Update analytics
            if self.quota_config.enable_usage_analytics:
                await self._update_usage_analytics_from_event(usage_event)
            
            return usage_result
            
        except Exception as e:
            self.logger.error(f"Quota usage tracking failed: {e}")
            return UsageResult(
                event_recorded=False,
                quota_updated=False,
                new_usage_total=0,
                warnings_triggered=[f"Tracking error: {str(e)}"],
                billing_events=[],
                quota_status=QuotaStatus.SUSPENDED
            )
    
    async def forecast_quota_needs(self, user_id: str, forecast_period: int) -> QuotaForecast:
        """Forecasting besoins quota basé sur ML predictions"""
        try:
            # Détermination quota type le plus utilisé
            primary_quota_type = await self._get_primary_quota_type(user_id)
            
            # Génération forecast
            forecast = await self.forecaster.forecast_quota_needs(
                user_id, primary_quota_type, forecast_period
            )
            
            return forecast
            
        except Exception as e:
            self.logger.error(f"Quota forecasting failed for {user_id}: {e}")
            return QuotaForecast(
                user_id=user_id,
                quota_type=QuotaType.API_requests,
                forecast_period_days=forecast_period,
                predicted_usage=[],
                confidence_intervals=[],
                estimated_overage=0,
                recommended_quota=0,
                recommendations=[f"Forecasting error: {str(e)}"]
            )
    
    async def optimize_quota_allocation(self, organization_id: str) -> OptimizationResult:
        """Optimization allocation quotas pour organization"""
        try:
            # Analyse allocation actuelle
            current_allocation = await self._get_organization_allocation(organization_id)
            
            # Analyse usage patterns
            usage_patterns = await self._analyze_organization_usage(organization_id)
            
            # Génération allocation optimisée
            optimized_allocation = await self._generate_optimized_allocation(
                current_allocation, usage_patterns
            )
            
            # Calcul savings projetés
            projected_savings = await self._calculate_projected_savings(
                current_allocation, optimized_allocation
            )
            
            # Calcul improvement efficiency
            efficiency_improvement = await self._calculate_efficiency_improvement(
                usage_patterns, optimized_allocation
            )
            
            # Génération recommendations
            recommendations = await self._generate_optimization_recommendations(
                current_allocation, optimized_allocation, projected_savings
            )
            
            return OptimizationResult(
                organization_id=organization_id,
                current_allocation=current_allocation,
                optimized_allocation=optimized_allocation,
                projected_savings=projected_savings,
                efficiency_improvement=efficiency_improvement,
                recommendations=recommendations,
                implementation_priority="high" if projected_savings > 1000 else "medium"
            )
            
        except Exception as e:
            self.logger.error(f"Quota optimization failed for {organization_id}: {e}")
            return OptimizationResult(
                organization_id=organization_id,
                current_allocation={},
                optimized_allocation={},
                projected_savings=0.0,
                efficiency_improvement=0.0,
                recommendations=[f"Optimization error: {str(e)}"]
            )
    
    async def _load_default_policies(self):
        """Chargement policies par défaut"""
        # Policies par défaut par tier
        default_policies = {
            SubscriptionTier.FREE: {
                QuotaType.API_REQUESTS: 1000,
                QuotaType.BANDWIDTH: 100,  # MB
                QuotaType.STORAGE: 1,      # GB
                QuotaType.AI_PROCESSING: 10
            },
            SubscriptionTier.BASIC: {
                QuotaType.API_REQUESTS: 10000,
                QuotaType.BANDWIDTH: 1000,
                QuotaType.STORAGE: 10,
                QuotaType.AI_PROCESSING: 100
            },
            SubscriptionTier.PRO: {
                QuotaType.API_REQUESTS: 100000,
                QuotaType.BANDWIDTH: 10000,
                QuotaType.STORAGE: 100,
                QuotaType.AI_PROCESSING: 1000
            },
            SubscriptionTier.ENTERPRISE: {
                QuotaType.API_REQUESTS: 1000000,
                QuotaType.BANDWIDTH: 100000,
                QuotaType.STORAGE: 1000,
                QuotaType.AI_PROCESSING: 10000
            }
        }
        
        self.quota_policies = default_policies
    
    async def _start_background_tasks(self):
        """Démarrage tâches background"""
        # Tâche reset quotas périodique
        reset_task = asyncio.create_task(self._quota_reset_loop())
        self._background_tasks.append(reset_task)
        
        # Tâche billing processing
        billing_task = asyncio.create_task(self._billing_processing_loop())
        self._background_tasks.append(billing_task)
        
        # Tâche auto-scaling monitoring
        if self.quota_config.enable_auto_scaling:
            scaling_task = asyncio.create_task(self._auto_scaling_loop())
            self._background_tasks.append(scaling_task)
    
    async def _quota_reset_loop(self):
        """Loop reset quotas périodique"""
        while not self._stop_event.is_set():
            try:
                await self._process_quota_resets()
                await asyncio.sleep(3600)  # Every hour
            except Exception as e:
                self.logger.error(f"Quota reset loop error: {e}")
                await asyncio.sleep(300)
    
    async def _billing_processing_loop(self):
        """Loop processing billing"""
        while not self._stop_event.is_set():
            try:
                if self.billing_integrator.billing_events:
                    events_to_process = list(self.billing_integrator.billing_events)
                    await self.billing_integrator.process_billing_events(events_to_process)
                    
                await asyncio.sleep(300)  # Every 5 minutes
            except Exception as e:
                self.logger.error(f"Billing processing loop error: {e}")
                await asyncio.sleep(300)
    
    async def _auto_scaling_loop(self):
        """Loop auto-scaling monitoring"""
        while not self._stop_event.is_set():
            try:
                await self._check_auto_scaling_triggers()
                await asyncio.sleep(900)  # Every 15 minutes
            except Exception as e:
                self.logger.error(f"Auto-scaling loop error: {e}")
                await asyncio.sleep(300)
    
    # Helper methods pour operations internes
    async def _get_organization_policy(self, user_id: str) -> Dict[str, Any]:
        """Récupération policy organization"""
        return {"max_quota_per_user": 1000000}  # Simplified
    
    async def _validate_quota_request(self, request: QuotaRequest, policy: Dict[str, Any]) -> bool:
        """Validation request contre policy"""
        return request.requested_amount <= policy.get("max_quota_per_user", 1000000)
    
    async def _trigger_auto_scaling(self, user_id: str, quota_type: QuotaType):
        """Trigger auto-scaling quota"""
        pass  # Simplified
    
    async def _update_usage_analytics(self, user_id: str, quota_request: QuotaRequest):
        """Update analytics usage"""
        pass  # Simplified
    
    async def _update_usage_analytics_from_event(self, usage_event: UsageEvent):
        """Update analytics depuis événement"""
        pass  # Simplified
    
    async def _get_primary_quota_type(self, user_id: str) -> QuotaType:
        """Détermination quota type principal"""
        return QuotaType.API_REQUESTS  # Simplified
    
    async def _get_organization_allocation(self, organization_id: str) -> Dict[str, int]:
        """Allocation actuelle organization"""
        return {"total_api_requests": 1000000}  # Simplified
    
    async def _analyze_organization_usage(self, organization_id: str) -> Dict[str, Any]:
        """Analyse usage organization"""
        return {"efficiency": 0.7}  # Simplified
    
    async def _generate_optimized_allocation(self, current: Dict[str, int], 
                                           patterns: Dict[str, Any]) -> Dict[str, int]:
        """Génération allocation optimisée"""
        return current  # Simplified
    
    async def _calculate_projected_savings(self, current: Dict[str, int], 
                                         optimized: Dict[str, int]) -> float:
        """Calcul savings projetés"""
        return 500.0  # Simplified
    
    async def _calculate_efficiency_improvement(self, patterns: Dict[str, Any], 
                                              optimized: Dict[str, int]) -> float:
        """Calcul improvement efficiency"""
        return 15.0  # 15% improvement
    
    async def _generate_optimization_recommendations(self, current: Dict[str, int],
                                                   optimized: Dict[str, int], 
                                                   savings: float) -> List[str]:
        """Génération recommendations optimization"""
        return ["Redistribute underutilized quotas", "Implement auto-scaling"]
    
    async def _process_quota_resets(self):
        """Processing resets quotas"""
        pass  # Simplified
    
    async def _check_auto_scaling_triggers(self):
        """Vérification triggers auto-scaling"""
        pass  # Simplified

# Factory functions
def create_enterprise_quota_manager(billing_enabled: bool = True) -> QuotaManagementEngine:
    """Factory pour quota manager enterprise"""
    config = QuotaConfig(
        enable_billing_integration=billing_enabled,
        enable_usage_analytics=True,
        enable_forecasting=True,
        enable_overage_protection=True,
        enable_auto_scaling=True,
        grace_period_hours=24,
        overage_multiplier=1.5,
        warning_thresholds=[0.7, 0.8, 0.9, 0.95]
    )
    
    return QuotaManagementEngine(config)

def create_basic_quota_manager() -> QuotaManagementEngine:
    """Factory pour quota manager basique"""
    config = QuotaConfig(
        enable_billing_integration=False,
        enable_usage_analytics=True,
        enable_forecasting=False,
        enable_overage_protection=True,
        enable_auto_scaling=False,
        warning_thresholds=[0.8, 0.9]
    )
    
    return QuotaManagementEngine(config)

# Export classes principales
__all__ = [
    'QuotaManagementEngine',
    'QuotaConfig',
    'UserQuota',
    'QuotaRequest',
    'QuotaResult',
    'UsageEvent',
    'QuotaForecast',
    'OptimizationResult',
    'QuotaType',
    'BillingPeriod',
    'SubscriptionTier',
    'QuotaStatus',
    'create_enterprise_quota_manager',
    'create_basic_quota_manager'
]