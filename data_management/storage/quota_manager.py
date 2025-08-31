"""💾 Quota Manager - IA Influencer Agent Platform Enterprise
=========================================================
Module: backend/data_management/storage/quota_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
=========================================================

Enterprise quota management system with usage tracking,
billing integration, and resource allocation optimization.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

ÉQUIPE PROJET - SPÉCIALITÉS:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel  
- FinOps: Fahed Mlaiel
- DevOps: Fahed Mlaiel
"""from typing import Dict, List, Optional, Any, Union, Tuple, Callable
import logging
import asyncio
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import aiofiles
import aiofiles.os
from decimal import Decimal, ROUND_HALF_UP
import statistics

logger = logging.getLogger(__name__)

class QuotaType(Enum):
    """Types of quotas"""    STORAGE_SIZE = "storage_size"
    FILE_COUNT = "file_count"
    BANDWIDTH = "bandwidth"
    API_REQUESTS = "api_requests"
    CONCURRENT_UPLOADS = "concurrent_uploads"
    CONCURRENT_DOWNLOADS = "concurrent_downloads"
    BACKUP_COUNT = "backup_count"
    ARCHIVE_SIZE = "archive_size"
    TEMP_SIZE = "temp_size"

class UsageMetric(Enum):
    """Usage metrics for tracking"""    BYTES_STORED = "bytes_stored"
    FILES_STORED = "files_stored"
    BYTES_TRANSFERRED = "bytes_transferred"
    REQUESTS_MADE = "requests_made"
    ACTIVE_CONNECTIONS = "active_connections"
    BACKUP_OPERATIONS = "backup_operations"
    ARCHIVE_OPERATIONS = "archive_operations"

class BillingModel(Enum):
    """Billing models"""    FIXED = "fixed"
    USAGE_BASED = "usage_based"
    TIERED = "tiered"
    HYBRID = "hybrid"

class QuotaPeriod(Enum):
    """Quota reset periods"""    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    NEVER = "never"

class AlertLevel(Enum):
    """Alert levels for quota warnings"""    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class OptimizationStrategy(Enum):
    """Resource optimization strategies"""    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"

@dataclass
class QuotaLimit:
    """Represents a quota limit"""    quota_id: str
    quota_type: QuotaType
    limit_value: int
    
    # Identification
    name: str
    description: str = ""
    
    # Scope
    user_id: Optional[str] = None
    group_id: Optional[str] = None
    plan_id: Optional[str] = None
    resource_pattern: str = "*"
    
    # Period and reset
    period: QuotaPeriod = QuotaPeriod.MONTHLY
    reset_day: int = 1  # For monthly quotas
    reset_hour: int = 0  # For daily/hourly quotas
    
    # Enforcement
    is_hard_limit: bool = True  # Hard vs soft limit
    grace_period_hours: int = 0
    auto_upgrade: bool = False
    
    # Cost and billing
    cost_per_unit: Decimal = Decimal('0.00')
    overage_cost_per_unit: Decimal = Decimal('0.00')
    billing_model: BillingModel = BillingModel.FIXED
    
    # Alerts
    warning_threshold: float = 0.8  # 80%
    critical_threshold: float = 0.95  # 95%
    
    # Metadata
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class UsageRecord:
    """Represents usage tracking record"""    record_id: str
    user_id: str
    quota_type: QuotaType
    metric: UsageMetric
    
    # Usage data
    value: int
    timestamp: datetime
    
    # Context
    resource_path: str = ""
    operation: str = ""
    session_id: str = ""
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QuotaUsage:
    """Current quota usage state"""    quota_id: str
    user_id: str
    quota_type: QuotaType
    
    # Current usage
    current_usage: int = 0
    limit_value: int = 0
    
    # Period tracking
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Usage statistics
    peak_usage: int = 0
    average_usage: float = 0.0
    usage_trend: float = 0.0  # Positive = increasing
    
    # Billing
    current_cost: Decimal = Decimal('0.00')
    projected_cost: Decimal = Decimal('0.00')
    overage_cost: Decimal = Decimal('0.00')
    
    # Last update
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class QuotaAlert:
    """Quota alert notification"""    alert_id: str
    quota_id: str
    user_id: str
    
    # Alert details
    level: AlertLevel
    message: str
    threshold: float
    current_usage_percent: float
    
    # Timing
    triggered_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    
    # Status
    is_active: bool = True
    acknowledged: bool = False
    
    # Actions
    recommended_actions: List[str] = field(default_factory=list)
    auto_actions_taken: List[str] = field(default_factory=list)

@dataclass
class ResourceRecommendation:
    """Resource optimization recommendation"""    recommendation_id: str
    user_id: str
    
    # Recommendation details
    type: str
    title: str
    description: str
    
    # Impact
    potential_savings: Decimal = Decimal('0.00')
    potential_space_saved: int = 0
    implementation_effort: str = "low"  # low, medium, high
    
    # Priority
    priority: int = 50  # 1-100
    confidence: float = 0.8  # 0.0-1.0
    
    # Implementation
    auto_implementable: bool = False
    implementation_steps: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Status
    status: str = "active"  # active, implemented, dismissed, expired

@dataclass
class QuotaConfig:
    """Configuration for quota manager"""    storage_root_path: str
    quotas_directory: str
    usage_directory: str
    billing_directory: str
    
    # Tracking settings
    usage_tracking_enabled: bool = True
    real_time_tracking: bool = True
    detailed_usage_logging: bool = True
    usage_aggregation_interval_minutes: int = 5
    
    # Enforcement settings
    enforce_quotas: bool = True
    quota_check_interval_seconds: int = 60
    grace_period_enforcement: bool = True
    auto_cleanup_enabled: bool = True
    
    # Billing settings
    billing_enabled: bool = True
    billing_currency: str = "USD"
    billing_precision: int = 4
    invoice_generation_enabled: bool = True
    
    # Optimization settings
    optimization_enabled: bool = True
    auto_optimization: bool = False
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    recommendation_frequency_hours: int = 24
    
    # Alert settings
    alerts_enabled: bool = True
    email_alerts: bool = True
    webhook_alerts: bool = True
    slack_alerts: bool = False
    
    # Performance settings
    cache_usage_data: bool = True
    cache_timeout_minutes: int = 5
    batch_size: int = 1000
    max_concurrent_operations: int = 100
    
    # Retention settings
    usage_retention_days: int = 365
    billing_retention_years: int = 7
    alert_retention_days: int = 90

class QuotaManager:
    """    Enterprise quota management system for storage resources.
    
    Features:
    - Multi-dimensional quota management
    - Real-time usage tracking
    - Cost optimization
    - Predictive analytics
    - Automated billing
    - Resource recommendations
    - Alert system
    """    
    def __init__(self, config: QuotaConfig):
        """Initialize quota manager"""        self.config = config
        self.quota_limits: Dict[str, QuotaLimit] = {}
        self.quota_usage: Dict[str, QuotaUsage] = {}
        self.usage_records: List[UsageRecord] = []
        self.active_alerts: Dict[str, QuotaAlert] = {}
        self.recommendations: Dict[str, ResourceRecommendation] = {}
        
        # Managers
        self.usage_tracker = UsageTracker(self)
        self.billing_manager = BillingManager(self)
        self.optimization_manager = OptimizationManager(self)
        self.alert_manager = AlertManager(self)
        
        # Cache
        self.usage_cache: Dict[str, Dict[str, Any]] = {}
        self.cost_cache: Dict[str, Decimal] = {}
        
        # Performance tracking
        self.metrics = {
            'total_quotas': 0,
            'active_quotas': 0,
            'total_users': 0,
            'quota_violations': 0,
            'total_cost': Decimal('0.00'),
            'optimizations_applied': 0,
            'space_saved': 0,
            'cost_saved': Decimal('0.00'),
            'average_usage_check_time': 0.0,
            'alerts_sent': 0
        }
        
        # Initialize directories and load data
        self._initialize_quota_directories()
        asyncio.create_task(self._load_initial_data())
        
        # Start background tasks
        asyncio.create_task(self._start_background_tasks())
        
        logger.info("QuotaManager initialized successfully")
    
    def _initialize_quota_directories(self) -> None:
        """Initialize quota management directories"""        try:
            directories = [
                self.config.storage_root_path,
                self.config.quotas_directory,
                self.config.usage_directory,
                self.config.billing_directory
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            usage_dir = Path(self.config.usage_directory)
            (usage_dir / "daily").mkdir(exist_ok=True)
            (usage_dir / "monthly").mkdir(exist_ok=True)
            (usage_dir / "realtime").mkdir(exist_ok=True)
            
            billing_dir = Path(self.config.billing_directory)
            (billing_dir / "invoices").mkdir(exist_ok=True)
            (billing_dir / "reports").mkdir(exist_ok=True)
            (billing_dir / "cost_analysis").mkdir(exist_ok=True)
            
            quotas_dir = Path(self.config.quotas_directory)
            (quotas_dir / "active").mkdir(exist_ok=True)
            (quotas_dir / "templates").mkdir(exist_ok=True)
            (quotas_dir / "archived").mkdir(exist_ok=True)
            
            logger.info("Quota management directories initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize quota directories: {str(e)}")
            raise
    
    async def create_quota(self, quota_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new quota limit"""        try:
            # Validate required fields
            required_fields = ['quota_type', 'limit_value', 'name']
            for field in required_fields:
                if field not in quota_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Generate quota ID
            quota_id = f"quota_{int(time.time())}_{hash(quota_data['name']) & 0xFFFF:04x}"
            
            # Create quota limit
            quota = QuotaLimit(
                quota_id=quota_id,
                quota_type=QuotaType(quota_data['quota_type']),
                limit_value=int(quota_data['limit_value']),
                name=quota_data['name'],
                description=quota_data.get('description', ''),
                user_id=quota_data.get('user_id'),
                group_id=quota_data.get('group_id'),
                plan_id=quota_data.get('plan_id'),
                resource_pattern=quota_data.get('resource_pattern', '*'),
                period=QuotaPeriod(quota_data.get('period', 'monthly')),
                reset_day=quota_data.get('reset_day', 1),
                reset_hour=quota_data.get('reset_hour', 0),
                is_hard_limit=quota_data.get('is_hard_limit', True),
                grace_period_hours=quota_data.get('grace_period_hours', 0),
                auto_upgrade=quota_data.get('auto_upgrade', False),
                cost_per_unit=Decimal(str(quota_data.get('cost_per_unit', '0.00'))),
                overage_cost_per_unit=Decimal(str(quota_data.get('overage_cost_per_unit', '0.00'))),
                billing_model=BillingModel(quota_data.get('billing_model', 'fixed')),
                warning_threshold=quota_data.get('warning_threshold', 0.8),
                critical_threshold=quota_data.get('critical_threshold', 0.95),
                is_active=quota_data.get('is_active', True),
                tags=quota_data.get('tags', [])
            )
            
            # Store quota
            self.quota_limits[quota_id] = quota
            
            # Create initial usage record
            usage_key = f"{quota.user_id or 'global'}:{quota_id}"
            period_start, period_end = self._calculate_period_bounds(quota.period)
            
            self.quota_usage[usage_key] = QuotaUsage(
                quota_id=quota_id,
                user_id=quota.user_id or 'global',
                quota_type=quota.quota_type,
                limit_value=quota.limit_value,
                period_start=period_start,
                period_end=period_end
            )
            
            # Save quota to disk
            await self._save_quota(quota)
            
            # Update metrics
            self.metrics['total_quotas'] += 1
            if quota.is_active:
                self.metrics['active_quotas'] += 1
            
            logger.info(f"Quota created: {quota_id} - {quota.name}")
            
            return {
                'success': True,
                'quota_id': quota_id,
                'quota_config': {
                    'name': quota.name,
                    'type': quota.quota_type.value,
                    'limit': quota.limit_value,
                    'period': quota.period.value,
                    'cost_per_unit': float(quota.cost_per_unit),
                    'is_active': quota.is_active
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create quota: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def track_usage(
        self,
        user_id: str,
        quota_type: QuotaType,
        metric: UsageMetric,
        value: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Track resource usage"""        try:
            if not self.config.usage_tracking_enabled:
                return {'success': True, 'message': 'Usage tracking disabled'}
            
            context = context or {}
            
            # Create usage record
            record = UsageRecord(
                record_id=f"usage_{int(time.time())}_{hash(user_id) & 0xFFFF:04x}",
                user_id=user_id,
                quota_type=quota_type,
                metric=metric,
                value=value,
                timestamp=datetime.now(),
                resource_path=context.get('resource_path', ''),
                operation=context.get('operation', ''),
                session_id=context.get('session_id', ''),
                metadata=context
            )
            
            # Store usage record
            self.usage_records.append(record)
            
            # Keep only recent records in memory
            if len(self.usage_records) > 10000:
                self.usage_records = self.usage_records[-5000:]
            
            # Update quota usage
            await self._update_quota_usage(user_id, quota_type, value)
            
            # Check quota limits
            violations = await self._check_quota_violations(user_id, quota_type)
            
            # Save usage record if detailed logging is enabled
            if self.config.detailed_usage_logging:
                await self._save_usage_record(record)
            
            return {
                'success': True,
                'record_id': record.record_id,
                'violations': violations,
                'current_usage': await self.get_current_usage(user_id, quota_type)
            }
            
        except Exception as e:
            logger.error(f"Usage tracking failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def check_quota_available(
        self,
        user_id: str,
        quota_type: QuotaType,
        requested_amount: int
    ) -> Dict[str, Any]:
        """Check if quota is available for requested amount"""        try:
            start_time = time.time()
            
            # Get applicable quotas
            applicable_quotas = self._get_applicable_quotas(user_id, quota_type)
            
            if not applicable_quotas:
                return {
                    'success': True,
                    'available': True,
                    'message': 'No quota limits apply'
                }
            
            # Check each applicable quota
            quota_status = []
            overall_available = True
            
            for quota in applicable_quotas:
                usage_key = f"{user_id}:{quota.quota_id}"
                current_usage = self.quota_usage.get(usage_key, QuotaUsage(
                    quota_id=quota.quota_id,
                    user_id=user_id,
                    quota_type=quota_type,
                    limit_value=quota.limit_value
                ))
                
                available_amount = quota.limit_value - current_usage.current_usage
                would_exceed = (current_usage.current_usage + requested_amount) > quota.limit_value
                
                # Check for grace period
                grace_allowed = False
                if would_exceed and not quota.is_hard_limit and quota.grace_period_hours > 0:
                    grace_allowed = True
                
                quota_available = not would_exceed or grace_allowed
                overall_available = overall_available and quota_available
                
                quota_status.append({
                    'quota_id': quota.quota_id,
                    'quota_name': quota.name,
                    'limit': quota.limit_value,
                    'current_usage': current_usage.current_usage,
                    'available': available_amount,
                    'requested': requested_amount,
                    'would_exceed': would_exceed,
                    'quota_available': quota_available,
                    'grace_allowed': grace_allowed,
                    'usage_percent': (current_usage.current_usage / quota.limit_value) * 100
                })
            
            check_time = (time.time() - start_time) * 1000
            
            # Update average check time
            old_avg = self.metrics['average_usage_check_time']
            self.metrics['average_usage_check_time'] = (old_avg * 0.9) + (check_time * 0.1)
            
            return {
                'success': True,
                'available': overall_available,
                'quota_status': quota_status,
                'check_time_ms': check_time
            }
            
        except Exception as e:
            logger.error(f"Quota availability check failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'available': False
            }
    
    async def get_current_usage(self, user_id: str, quota_type: Optional[QuotaType] = None) -> Dict[str, Any]:
        """Get current usage for user"""        try:
            if quota_type:
                # Get usage for specific quota type
                applicable_quotas = self._get_applicable_quotas(user_id, quota_type)
                usage_data = []
                
                for quota in applicable_quotas:
                    usage_key = f"{user_id}:{quota.quota_id}"
                    usage = self.quota_usage.get(usage_key)
                    
                    if usage:
                        usage_data.append({
                            'quota_id': quota.quota_id,
                            'quota_name': quota.name,
                            'quota_type': quota.quota_type.value,
                            'current_usage': usage.current_usage,
                            'limit': usage.limit_value,
                            'usage_percent': (usage.current_usage / usage.limit_value) * 100 if usage.limit_value > 0 else 0,
                            'period_start': usage.period_start.isoformat(),
                            'period_end': usage.period_end.isoformat(),
                            'current_cost': float(usage.current_cost),
                            'projected_cost': float(usage.projected_cost)
                        })
                
                return {
                    'success': True,
                    'user_id': user_id,
                    'quota_type': quota_type.value,
                    'usage_data': usage_data
                }
            else:
                # Get all usage for user
                all_usage = []
                
                for usage_key, usage in self.quota_usage.items():
                    if usage.user_id == user_id:
                        quota = self.quota_limits.get(usage.quota_id)
                        
                        if quota:
                            all_usage.append({
                                'quota_id': quota.quota_id,
                                'quota_name': quota.name,
                                'quota_type': quota.quota_type.value,
                                'current_usage': usage.current_usage,
                                'limit': usage.limit_value,
                                'usage_percent': (usage.current_usage / usage.limit_value) * 100 if usage.limit_value > 0 else 0,
                                'period_start': usage.period_start.isoformat(),
                                'period_end': usage.period_end.isoformat(),
                                'current_cost': float(usage.current_cost),
                                'projected_cost': float(usage.projected_cost)
                            })
                
                return {
                    'success': True,
                    'user_id': user_id,
                    'usage_data': all_usage
                }
            
        except Exception as e:
            logger.error(f"Failed to get current usage: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_cost_report(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive cost report"""        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            return await self.billing_manager.generate_cost_report(user_id, start_date, end_date)
            
        except Exception as e:
            logger.error(f"Cost report generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_optimization_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get resource optimization recommendations"""        try:
            return await self.optimization_manager.generate_recommendations(user_id)
            
        except Exception as e:
            logger.error(f"Failed to get optimization recommendations: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def apply_optimization(self, recommendation_id: str) -> Dict[str, Any]:
        """Apply optimization recommendation"""        try:
            if recommendation_id not in self.recommendations:
                return {
                    'success': False,
                    'error': f'Recommendation not found: {recommendation_id}'
                }
            
            recommendation = self.recommendations[recommendation_id]
            
            if not recommendation.auto_implementable:
                return {
                    'success': False,
                    'error': 'Recommendation requires manual implementation'
                }
            
            # Apply optimization
            result = await self.optimization_manager.apply_recommendation(recommendation)
            
            if result['success']:
                # Update recommendation status
                recommendation.status = 'implemented'
                
                # Update metrics
                self.metrics['optimizations_applied'] += 1
                self.metrics['space_saved'] += recommendation.potential_space_saved
                self.metrics['cost_saved'] += recommendation.potential_savings
            
            return result
            
        except Exception as e:
            logger.error(f"Optimization application failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_quota_statistics(self) -> Dict[str, Any]:
        """Get comprehensive quota statistics"""        try:
            # Basic quota statistics
            total_quotas = len(self.quota_limits)
            active_quotas = len([q for q in self.quota_limits.values() if q.is_active])
            
            # Usage statistics
            total_users = len(set(usage.user_id for usage in self.quota_usage.values()))
            
            # Quota type distribution
            quota_type_distribution = {}
            for quota_type in QuotaType:
                count = len([q for q in self.quota_limits.values() if q.quota_type == quota_type])
                quota_type_distribution[quota_type.value] = count
            
            # Cost statistics
            total_cost = sum(usage.current_cost for usage in self.quota_usage.values())
            projected_cost = sum(usage.projected_cost for usage in self.quota_usage.values())
            
            # Alert statistics
            active_alerts = len([a for a in self.active_alerts.values() if a.is_active])
            critical_alerts = len([
                a for a in self.active_alerts.values() 
                if a.is_active and a.level == AlertLevel.CRITICAL
            ])
            
            # Usage trends
            usage_trends = self._calculate_usage_trends()
            
            return {
                'quotas': {
                    'total_quotas': total_quotas,
                    'active_quotas': active_quotas,
                    'quota_type_distribution': quota_type_distribution
                },
                'usage': {
                    'total_users': total_users,
                    'usage_trends': usage_trends
                },
                'costs': {
                    'total_cost': float(total_cost),
                    'projected_cost': float(projected_cost),
                    'currency': self.config.billing_currency
                },
                'alerts': {
                    'active_alerts': active_alerts,
                    'critical_alerts': critical_alerts
                },
                'performance': self.metrics,
                'optimization': {
                    'recommendations_available': len([
                        r for r in self.recommendations.values() 
                        if r.status == 'active'
                    ]),
                    'potential_savings': float(sum(
                        r.potential_savings for r in self.recommendations.values() 
                        if r.status == 'active'
                    ))
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get quota statistics: {str(e)}")
            return {'error': str(e)}
    
    # Private implementation methods
    
    def _get_applicable_quotas(self, user_id: str, quota_type: QuotaType) -> List[QuotaLimit]:
        """Get quotas applicable to user and quota type"""        applicable_quotas = []
        
        for quota in self.quota_limits.values():
            if not quota.is_active:
                continue
            
            if quota.quota_type != quota_type:
                continue
            
            # Check if quota applies to user
            if quota.user_id and quota.user_id != user_id:
                continue
            
            # Add group and plan checks
            if quota.group_id:
                # Check if user belongs to the specified group
                user_groups = await self._get_user_groups(user_id)
                if quota.group_id not in user_groups:
                    continue
            
            if quota.plan_id:
                # Check if user has the specified plan
                user_plan = await self._get_user_plan(user_id)
                if quota.plan_id != user_plan:
                    continue
            
            
            applicable_quotas.append(quota)
        
        return applicable_quotas
    
    def _calculate_period_bounds(self, period: QuotaPeriod) -> Tuple[datetime, datetime]:
        """Calculate period start and end dates"""        now = datetime.now()
        
        if period == QuotaPeriod.HOURLY:
            start = now.replace(minute=0, second=0, microsecond=0)
            end = start + timedelta(hours=1)
        elif period == QuotaPeriod.DAILY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period == QuotaPeriod.WEEKLY:
            days_since_monday = now.weekday()
            start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(weeks=1)
        elif period == QuotaPeriod.MONTHLY:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)
        elif period == QuotaPeriod.YEARLY:
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start.replace(year=start.year + 1)
        else:  # NEVER
            start = datetime.min
            end = datetime.max
        
        return start, end
    
    async def _update_quota_usage(self, user_id: str, quota_type: QuotaType, value: int) -> None:
        """Update quota usage with new value"""        try:
            applicable_quotas = self._get_applicable_quotas(user_id, quota_type)
            
            for quota in applicable_quotas:
                usage_key = f"{user_id}:{quota.quota_id}"
                
                if usage_key not in self.quota_usage:
                    # Create new usage record
                    period_start, period_end = self._calculate_period_bounds(quota.period)
                    self.quota_usage[usage_key] = QuotaUsage(
                        quota_id=quota.quota_id,
                        user_id=user_id,
                        quota_type=quota_type,
                        limit_value=quota.limit_value,
                        period_start=period_start,
                        period_end=period_end
                    )
                
                usage = self.quota_usage[usage_key]
                
                # Check if we need to reset for new period
                now = datetime.now()
                if now >= usage.period_end:
                    # Reset usage for new period
                    period_start, period_end = self._calculate_period_bounds(quota.period)
                    usage.current_usage = 0
                    usage.period_start = period_start
                    usage.period_end = period_end
                
                # Update usage
                usage.current_usage += value
                usage.peak_usage = max(usage.peak_usage, usage.current_usage)
                usage.last_updated = now
                
                # Calculate cost
                await self._update_usage_cost(usage, quota)
                
                # Save usage to cache
                if self.config.cache_usage_data:
                    self.usage_cache[usage_key] = {
                        'current_usage': usage.current_usage,
                        'limit_value': usage.limit_value,
                        'last_updated': now,
                        'expires_at': now + timedelta(minutes=self.config.cache_timeout_minutes)
                    }
        
        except Exception as e:
            logger.error(f"Failed to update quota usage: {str(e)}")
    
    async def _update_usage_cost(self, usage: QuotaUsage, quota: QuotaLimit) -> None:
        """Update usage cost calculations"""        try:
            if quota.billing_model == BillingModel.FIXED:
                # Fixed cost regardless of usage
                usage.current_cost = quota.cost_per_unit
            
            elif quota.billing_model == BillingModel.USAGE_BASED:
                # Cost based on actual usage
                usage.current_cost = Decimal(usage.current_usage) * quota.cost_per_unit
                
                # Add overage costs if applicable
                if usage.current_usage > quota.limit_value:
                    overage = usage.current_usage - quota.limit_value
                    usage.overage_cost = Decimal(overage) * quota.overage_cost_per_unit
                    usage.current_cost += usage.overage_cost
            
            elif quota.billing_model == BillingModel.TIERED:
                # Tiered pricing (simplified implementation)
                usage.current_cost = self._calculate_tiered_cost(usage.current_usage, quota)
            
            # Calculate projected cost for end of period
            if usage.current_usage > 0 and usage.period_start < datetime.now() < usage.period_end:
                time_elapsed = (datetime.now() - usage.period_start).total_seconds()
                period_duration = (usage.period_end - usage.period_start).total_seconds()
                
                if time_elapsed > 0:
                    usage_rate = usage.current_usage / time_elapsed
                    projected_usage = usage_rate * period_duration
                    
                    # Calculate projected cost
                    if quota.billing_model == BillingModel.USAGE_BASED:
                        usage.projected_cost = Decimal(projected_usage) * quota.cost_per_unit
                    else:
                        usage.projected_cost = usage.current_cost
        
        except Exception as e:
            logger.error(f"Failed to update usage cost: {str(e)}")
    
    def _calculate_tiered_cost(self, usage: int, quota: QuotaLimit) -> Decimal:
        """Calculate tiered pricing cost (simplified)"""        # This is a simplified implementation
        # In a real system, you would have configurable tiers
        base_cost = quota.cost_per_unit
        
        if usage <= quota.limit_value:
            return Decimal(usage) * base_cost
        else:
            # Higher rate for overage
            base_cost_total = Decimal(quota.limit_value) * base_cost
            overage = usage - quota.limit_value
            overage_cost = Decimal(overage) * quota.overage_cost_per_unit
            return base_cost_total + overage_cost
    
    async def _check_quota_violations(self, user_id: str, quota_type: QuotaType) -> List[Dict[str, Any]]:
        """Check for quota violations and trigger alerts"""        violations = []
        
        try:
            applicable_quotas = self._get_applicable_quotas(user_id, quota_type)
            
            for quota in applicable_quotas:
                usage_key = f"{user_id}:{quota.quota_id}"
                usage = self.quota_usage.get(usage_key)
                
                if not usage:
                    continue
                
                usage_percent = (usage.current_usage / quota.limit_value) * 100 if quota.limit_value > 0 else 0
                
                # Check for violations
                if usage.current_usage > quota.limit_value:
                    if quota.is_hard_limit:
                        violations.append({
                            'quota_id': quota.quota_id,
                            'quota_name': quota.name,
                            'type': 'hard_limit_exceeded',
                            'current_usage': usage.current_usage,
                            'limit': quota.limit_value,
                            'overage': usage.current_usage - quota.limit_value,
                            'usage_percent': usage_percent
                        })
                        
                        self.metrics['quota_violations'] += 1
                
                # Check for warning thresholds
                if usage_percent >= quota.critical_threshold * 100:
                    await self.alert_manager.trigger_alert(
                        quota, usage, AlertLevel.CRITICAL
                    )
                elif usage_percent >= quota.warning_threshold * 100:
                    await self.alert_manager.trigger_alert(
                        quota, usage, AlertLevel.WARNING
                    )
            
            return violations
            
        except Exception as e:
            logger.error(f"Quota violation check failed: {str(e)}")
            return []
    
    def _calculate_usage_trends(self) -> Dict[str, Any]:
        """Calculate usage trends across time periods"""        try:
            # This is a simplified implementation
            # In a real system, you would analyze historical data
            
            trends = {}
            
            for quota_type in QuotaType:
                recent_usage = [
                    record.value for record in self.usage_records[-1000:]
                    if record.quota_type == quota_type
                ]
                
                if len(recent_usage) > 1:
                    # Calculate simple trend
                    mid_point = len(recent_usage) // 2
                    first_half_avg = statistics.mean(recent_usage[:mid_point]) if mid_point > 0 else 0
                    second_half_avg = statistics.mean(recent_usage[mid_point:]) if mid_point < len(recent_usage) else 0
                    
                    trend = second_half_avg - first_half_avg if first_half_avg > 0 else 0
                    
                    trends[quota_type.value] = {
                        'trend': trend,
                        'direction': 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable',
                        'recent_average': second_half_avg,
                        'sample_size': len(recent_usage)
                    }
            
            return trends
            
        except Exception as e:
            logger.error(f"Usage trend calculation failed: {str(e)}")
            return {}
    
    async def _load_initial_data(self) -> None:
        """Load initial data from disk"""        try:
            # Load quotas
            quotas_dir = Path(self.config.quotas_directory) / "active"
            if quotas_dir.exists():
                for quota_file in quotas_dir.glob("*.json"):
                    try:
                        async with aiofiles.open(quota_file, 'r') as f:
                            quota_data = json.loads(await f.read())
                        
                        # Reconstruct quota object
                        quota = QuotaLimit(
                            quota_id=quota_data['quota_id'],
                            quota_type=QuotaType(quota_data['quota_type']),
                            limit_value=quota_data['limit_value'],
                            name=quota_data['name'],
                            description=quota_data.get('description', ''),
                            user_id=quota_data.get('user_id'),
                            group_id=quota_data.get('group_id'),
                            plan_id=quota_data.get('plan_id'),
                            resource_pattern=quota_data.get('resource_pattern', '*'),
                            period=QuotaPeriod(quota_data.get('period', 'monthly')),
                            reset_day=quota_data.get('reset_day', 1),
                            reset_hour=quota_data.get('reset_hour', 0),
                            is_hard_limit=quota_data.get('is_hard_limit', True),
                            grace_period_hours=quota_data.get('grace_period_hours', 0),
                            auto_upgrade=quota_data.get('auto_upgrade', False),
                            cost_per_unit=Decimal(str(quota_data.get('cost_per_unit', '0.00'))),
                            overage_cost_per_unit=Decimal(str(quota_data.get('overage_cost_per_unit', '0.00'))),
                            billing_model=BillingModel(quota_data.get('billing_model', 'fixed')),
                            warning_threshold=quota_data.get('warning_threshold', 0.8),
                            critical_threshold=quota_data.get('critical_threshold', 0.95),
                            is_active=quota_data.get('is_active', True),
                            created_at=datetime.fromisoformat(quota_data.get('created_at', datetime.now().isoformat())),
                            updated_at=datetime.fromisoformat(quota_data['updated_at']) if quota_data.get('updated_at') else None,
                            tags=quota_data.get('tags', [])
                        )
                        
                        self.quota_limits[quota.quota_id] = quota
                        
                    except Exception as e:
                        logger.error(f"Failed to load quota from {quota_file}: {str(e)}")
            
            logger.info(f"Loaded {len(self.quota_limits)} quota limits")
            
        except Exception as e:
            logger.error(f"Failed to load initial data: {str(e)}")
    
    async def _get_user_groups(self, user_id: str) -> List[str]:
        """Get list of groups that user belongs to"""        try:
            # In a production system, this would query the user management system
            # For now, simulate group membership
            user_groups_map = {
                'user1': ['basic_users', 'content_creators'],
                'user2': ['premium_users', 'content_creators'],
                'user3': ['admin_users', 'content_creators'],
                'default': ['basic_users']
            }
            
            return user_groups_map.get(user_id, user_groups_map['default'])
            
        except Exception as e:
            logger.error(f"Failed to get user groups for {user_id}: {str(e)}")
            return []
    
    async def _get_user_plan(self, user_id: str) -> Optional[str]:
        """Get user's current subscription plan"""        try:
            # In a production system, this would query the subscription management system
            # For now, simulate plan assignments
            user_plans_map = {
                'user1': 'basic_plan',
                'user2': 'premium_plan',
                'user3': 'enterprise_plan'
            }
            
            return user_plans_map.get(user_id, 'basic_plan')
            
        except Exception as e:
            logger.error(f"Failed to get user plan for {user_id}: {str(e)}")
            return None
    
    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks"""        try:
            # Start quota monitoring
            if self.config.enforce_quotas:
                asyncio.create_task(self._quota_monitoring_task())
            
            # Start usage aggregation
            if self.config.usage_tracking_enabled:
                asyncio.create_task(self._usage_aggregation_task())
            
            # Start optimization recommendations
            if self.config.optimization_enabled:
                asyncio.create_task(self._optimization_task())
            
            # Start billing calculations
            if self.config.billing_enabled:
                asyncio.create_task(self._billing_task())
            
        except Exception as e:
            logger.error(f"Failed to start background tasks: {str(e)}")
    
    async def _quota_monitoring_task(self) -> None:
        """Monitor quota usage and enforce limits"""        while True:
            try:
                await asyncio.sleep(self.config.quota_check_interval_seconds)
                
                # Check all active quotas
                for quota in self.quota_limits.values():
                    if not quota.is_active:
                        continue
                    
                    # Check users with this quota
                    for usage_key, usage in self.quota_usage.items():
                        if usage.quota_id == quota.quota_id:
                            await self._check_quota_violations(usage.user_id, quota.quota_type)
                
            except Exception as e:
                logger.error(f"Quota monitoring error: {str(e)}")
    
    async def _usage_aggregation_task(self) -> None:
        """Aggregate usage data for reporting"""        while True:
            try:
                await asyncio.sleep(self.config.usage_aggregation_interval_minutes * 60)
                
                # Aggregate recent usage records
                # This would implement actual aggregation logic
                logger.debug("Usage aggregation task executed")
                
            except Exception as e:
                logger.error(f"Usage aggregation error: {str(e)}")
    
    async def _optimization_task(self) -> None:
        """Generate optimization recommendations"""        while True:
            try:
                await asyncio.sleep(self.config.recommendation_frequency_hours * 3600)
                
                # Generate recommendations for all users
                unique_users = set(usage.user_id for usage in self.quota_usage.values())
                
                for user_id in unique_users:
                    try:
                        await self.optimization_manager.generate_recommendations(user_id)
                    except Exception as e:
                        logger.error(f"Optimization generation failed for user {user_id}: {str(e)}")
                
            except Exception as e:
                logger.error(f"Optimization task error: {str(e)}")
    
    async def _billing_task(self) -> None:
        """Process billing calculations"""        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Update billing calculations
                await self.billing_manager.process_billing_updates()
                
            except Exception as e:
                logger.error(f"Billing task error: {str(e)}")
    
    async def _save_quota(self, quota: QuotaLimit) -> None:
        """Save quota to disk"""        try:
            quota_path = Path(self.config.quotas_directory) / "active" / f"{quota.quota_id}.json"
            
            quota_data = {
                'quota_id': quota.quota_id,
                'quota_type': quota.quota_type.value,
                'limit_value': quota.limit_value,
                'name': quota.name,
                'description': quota.description,
                'user_id': quota.user_id,
                'group_id': quota.group_id,
                'plan_id': quota.plan_id,
                'resource_pattern': quota.resource_pattern,
                'period': quota.period.value,
                'reset_day': quota.reset_day,
                'reset_hour': quota.reset_hour,
                'is_hard_limit': quota.is_hard_limit,
                'grace_period_hours': quota.grace_period_hours,
                'auto_upgrade': quota.auto_upgrade,
                'cost_per_unit': str(quota.cost_per_unit),
                'overage_cost_per_unit': str(quota.overage_cost_per_unit),
                'billing_model': quota.billing_model.value,
                'warning_threshold': quota.warning_threshold,
                'critical_threshold': quota.critical_threshold,
                'is_active': quota.is_active,
                'created_at': quota.created_at.isoformat(),
                'updated_at': datetime.now().isoformat(),
                'tags': quota.tags
            }
            
            async with aiofiles.open(quota_path, 'w') as f:
                await f.write(json.dumps(quota_data, indent=2))
            
        except Exception as e:
            logger.error(f"Failed to save quota: {str(e)}")
    
    async def _save_usage_record(self, record: UsageRecord) -> None:
        """Save usage record to disk"""        try:
            # Create date-based directory structure
            date_str = record.timestamp.strftime("%Y/%m/%d")
            usage_dir = Path(self.config.usage_directory) / "realtime" / date_str
            usage_dir.mkdir(parents=True, exist_ok=True)
            
            # Save record
            record_file = usage_dir / f"{record.record_id}.json"
            
            record_data = {
                'record_id': record.record_id,
                'user_id': record.user_id,
                'quota_type': record.quota_type.value,
                'metric': record.metric.value,
                'value': record.value,
                'timestamp': record.timestamp.isoformat(),
                'resource_path': record.resource_path,
                'operation': record.operation,
                'session_id': record.session_id,
                'metadata': record.metadata
            }
            
            async with aiofiles.open(record_file, 'w') as f:
                await f.write(json.dumps(record_data, indent=2))
            
        except Exception as e:
            logger.error(f"Failed to save usage record: {str(e)}")


class UsageTracker:
    """Tracks resource usage"""    
    def __init__(self, quota_manager: QuotaManager):
        """Initialize usage tracker"""        self.quota_manager = quota_manager


class BillingManager:
    """Manages billing and cost calculations"""    
    def __init__(self, quota_manager: QuotaManager):
        """Initialize billing manager"""        self.quota_manager = quota_manager
    
    async def generate_cost_report(
        self,
        user_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate comprehensive cost report"""        try:
            # This would implement actual cost report generation
            # For now, return a placeholder
            
            return {
                'success': True,
                'report': {
                    'user_id': user_id,
                    'period': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'total_cost': 0.0,
                    'currency': self.quota_manager.config.billing_currency,
                    'breakdown': {}
                }
            }
            
        except Exception as e:
            logger.error(f"Cost report generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def process_billing_updates(self) -> None:
        """Process billing updates"""        try:
            # Update all usage costs
            for usage in self.quota_manager.quota_usage.values():
                quota = self.quota_manager.quota_limits.get(usage.quota_id)
                if quota:
                    await self.quota_manager._update_usage_cost(usage, quota)
            
        except Exception as e:
            logger.error(f"Billing update processing failed: {str(e)}")


class OptimizationManager:
    """Manages resource optimization"""    
    def __init__(self, quota_manager: QuotaManager):
        """Initialize optimization manager"""        self.quota_manager = quota_manager
    
    async def generate_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Generate optimization recommendations for user"""        try:
            recommendations = []
            
            # Analyze user's usage patterns
            user_usage = [
                usage for usage in self.quota_manager.quota_usage.values()
                if usage.user_id == user_id
            ]
            
            # Generate recommendations based on usage patterns
            for usage in user_usage:
                quota = self.quota_manager.quota_limits.get(usage.quota_id)
                if not quota:
                    continue
                
                usage_percent = (usage.current_usage / usage.limit_value) * 100 if usage.limit_value > 0 else 0
                
                # Low usage recommendation
                if usage_percent < 20:
                    rec_id = f"rec_{int(time.time())}_{hash(user_id) & 0xFFFF:04x}"
                    recommendation = ResourceRecommendation(
                        recommendation_id=rec_id,
                        user_id=user_id,
                        type="quota_reduction",
                        title=f"Consider reducing {quota.name} quota",
                        description=f"Your usage is only {usage_percent:.1f}% of allocated quota",
                        potential_savings=usage.current_cost * Decimal('0.5'),
                        implementation_effort="low",
                        priority=30,
                        confidence=0.8,
                        auto_implementable=False,
                        implementation_steps=[
                            f"Review usage patterns for {quota.name}",
                            "Consider reducing quota limit",
                            "Monitor for any impact"
                        ]
                    )
                    
                    self.quota_manager.recommendations[rec_id] = recommendation
                    recommendations.append(recommendation)
            
            return {
                'success': True,
                'user_id': user_id,
                'recommendations': [
                    {
                        'recommendation_id': rec.recommendation_id,
                        'type': rec.type,
                        'title': rec.title,
                        'description': rec.description,
                        'potential_savings': float(rec.potential_savings),
                        'priority': rec.priority,
                        'confidence': rec.confidence,
                        'auto_implementable': rec.auto_implementable
                    }
                    for rec in recommendations
                ]
            }
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def apply_recommendation(self, recommendation: ResourceRecommendation) -> Dict[str, Any]:
        """Apply optimization recommendation"""        try:
            # This would implement actual recommendation application
            # For now, return a placeholder
            
            return {
                'success': True,
                'recommendation_id': recommendation.recommendation_id,
                'message': 'Recommendation applied successfully'
            }
            
        except Exception as e:
            logger.error(f"Recommendation application failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class AlertManager:
    """Manages quota alerts"""    
    def __init__(self, quota_manager: QuotaManager):
        """Initialize alert manager"""        self.quota_manager = quota_manager
    
    async def trigger_alert(self, quota: QuotaLimit, usage: QuotaUsage, level: AlertLevel) -> None:
        """Trigger quota alert"""        try:
            if not self.quota_manager.config.alerts_enabled:
                return
            
            alert_id = f"alert_{int(time.time())}_{hash(usage.user_id) & 0xFFFF:04x}"
            
            usage_percent = (usage.current_usage / usage.limit_value) * 100 if usage.limit_value > 0 else 0
            
            # Create alert
            alert = QuotaAlert(
                alert_id=alert_id,
                quota_id=quota.quota_id,
                user_id=usage.user_id,
                level=level,
                message=f"{quota.name} usage is at {usage_percent:.1f}%",
                threshold=quota.warning_threshold if level == AlertLevel.WARNING else quota.critical_threshold,
                current_usage_percent=usage_percent / 100
            )
            
            # Add recommended actions
            if level == AlertLevel.WARNING:
                alert.recommended_actions = [
                    "Monitor usage closely",
                    "Consider optimizing resource usage",
                    "Review upcoming usage plans"
                ]
            elif level == AlertLevel.CRITICAL:
                alert.recommended_actions = [
                    "Reduce usage immediately",
                    "Upgrade quota if necessary",
                    "Contact support if needed"
                ]
            
            # Store alert
            self.quota_manager.active_alerts[alert_id] = alert
            
            # Update metrics
            self.quota_manager.metrics['alerts_sent'] += 1
            
            logger.warning(f"Quota alert triggered: {alert.message} for user {usage.user_id}")
            
        except Exception as e:
            logger.error(f"Alert triggering failed: {str(e)}")


# Export classes and functions
__all__ = [
    'QuotaManager',
    'UsageTracker',
    'BillingManager',
    'OptimizationManager',
    'AlertManager',
    'QuotaLimit',
    'UsageRecord',
    'QuotaUsage',
    'QuotaAlert',
    'ResourceRecommendation',
    'QuotaConfig',
    'QuotaType',
    'UsageMetric',
    'BillingModel',
    'QuotaPeriod',
    'AlertLevel',
    'OptimizationStrategy'
]
