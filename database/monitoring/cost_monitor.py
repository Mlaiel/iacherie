"""
Database Cost Monitor - Intelligent Cost Optimization and Resource Management

Advanced database cost monitoring system with AI-powered optimization recommendations,
resource usage tracking, and automated cost control for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

  AVERTISSEMENT STRICT - PROPRIÉTÉ INTELLECTUELLE 
Toute utilisation, modification ou distribution non autorisée de ce code est strictement interdite.
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute violation sera poursuivie selon les lois en vigueur.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import statistics
from collections import defaultdict, deque

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import asyncpg

from ..core.database import get_database_session
from ...core.config import Settings
from ...utils.cache import RedisCache
from ...ai.cost_optimization import CostOptimizationAI
from ...monitoring.notifications import CostNotificationManager
from ...cloud.aws import AWSCostExplorer
from ...cloud.azure import AzureCostManagement
from ...cloud.gcp import GCPBilling


class CostCategory(Enum):
    """Database cost categories"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    BACKUP = "backup"
    MONITORING = "monitoring"
    SECURITY = "security"
    MAINTENANCE = "maintenance"
    LICENSING = "licensing"


class ResourceType(Enum):
    """Database resource types"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    CONNECTIONS = "connections"
    IOPS = "iops"
    BANDWIDTH = "bandwidth"


class OptimizationStrategy(Enum):
    """Cost optimization strategies"""
    RIGHTSIZING = "rightsizing"
    RESERVED_INSTANCES = "reserved_instances"
    SPOT_INSTANCES = "spot_instances"
    AUTO_SCALING = "auto_scaling"
    STORAGE_OPTIMIZATION = "storage_optimization"
    QUERY_OPTIMIZATION = "query_optimization"
    INDEX_OPTIMIZATION = "index_optimization"
    ARCHIVAL = "archival"


@dataclass
class CostMetric:
    """Cost tracking metric"""
    metric_id: str
    timestamp: datetime
    category: CostCategory
    resource_type: ResourceType
    current_cost: float
    projected_cost: float
    currency: str = "EUR"
    usage_units: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            'metric_id': self.metric_id,
            'timestamp': self.timestamp.isoformat(),
            'category': self.category.value,
            'resource_type': self.resource_type.value,
            'current_cost': self.current_cost,
            'projected_cost': self.projected_cost,
            'currency': self.currency,
            'usage_units': self.usage_units,
            'metadata': self.metadata
        }


@dataclass
class OptimizationRecommendation:
    """Cost optimization recommendation"""
    recommendation_id: str
    timestamp: datetime
    strategy: OptimizationStrategy
    current_cost: float
    optimized_cost: float
    savings_potential: float
    confidence: float
    implementation_effort: str  # LOW, MEDIUM, HIGH
    risk_level: str  # LOW, MEDIUM, HIGH
    description: str
    action_items: List[str] = field(default_factory=list)
    estimated_timeline: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            'recommendation_id': self.recommendation_id,
            'timestamp': self.timestamp.isoformat(),
            'strategy': self.strategy.value,
            'current_cost': self.current_cost,
            'optimized_cost': self.optimized_cost,
            'savings_potential': self.savings_potential,
            'confidence': self.confidence,
            'implementation_effort': self.implementation_effort,
            'risk_level': self.risk_level,
            'description': self.description,
            'action_items': self.action_items,
            'estimated_timeline': self.estimated_timeline,
            'metadata': self.metadata
        }


@dataclass
class ResourceUsage:
    """Resource usage tracking"""
    resource_id: str
    timestamp: datetime
    resource_type: ResourceType
    allocated: float
    utilized: float
    peak_usage: float
    average_usage: float
    utilization_rate: float
    cost_per_unit: float
    total_cost: float
    efficiency_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            'resource_id': self.resource_id,
            'timestamp': self.timestamp.isoformat(),
            'resource_type': self.resource_type.value,
            'allocated': self.allocated,
            'utilized': self.utilized,
            'peak_usage': self.peak_usage,
            'average_usage': self.average_usage,
            'utilization_rate': self.utilization_rate,
            'cost_per_unit': self.cost_per_unit,
            'total_cost': self.total_cost,
            'efficiency_score': self.efficiency_score
        }


class DatabaseCostMonitor:
    """Advanced database cost monitoring and optimization system"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.cache = RedisCache()
        self.cost_ai = CostOptimizationAI()
        self.notification_manager = CostNotificationManager()
        
        # Cloud cost management clients
        self.aws_cost_explorer = AWSCostExplorer()
        self.azure_cost_mgmt = AzureCostManagement()
        self.gcp_billing = GCPBilling()
        
        # Cost monitoring state
        self.cost_metrics: deque = deque(maxlen=10000)
        self.optimization_recommendations: Dict[str, OptimizationRecommendation] = {}
        self.resource_usage: Dict[str, ResourceUsage] = {}
        self.cost_budgets: Dict[str, Dict] = {}
        self.cost_alerts: List[Dict] = []
        
        # Monitoring flags
        self._monitoring_active = False
        self._monitoring_task = None
        
        # Load cost budgets
        asyncio.create_task(self._load_cost_budgets())
        
    async def _load_cost_budgets(self):
        """Load cost budgets and thresholds"""



        try:
            # Default budgets for different cost categories
            self.cost_budgets = {
                'monthly_total': {
                    'limit': 5000.0,  # EUR
                    'warning_threshold': 0.8,
                    'critical_threshold': 0.95
                },
                'compute': {
                    'limit': 2000.0,
                    'warning_threshold': 0.8,
                    'critical_threshold': 0.9
                },
                'storage': {
                    'limit': 1500.0,
                    'warning_threshold': 0.8,
                    'critical_threshold': 0.9
                },
                'network': {
                    'limit': 800.0,
                    'warning_threshold': 0.8,
                    'critical_threshold': 0.9
                },
                'backup': {
                    'limit': 500.0,
                    'warning_threshold': 0.8,
                    'critical_threshold': 0.9
                }
            }
            
            self.logger.info("Loaded cost budgets and thresholds")
            
        except Exception as e:
            self.logger.error(f"Failed to load cost budgets: {e}")
            
    async def start_monitoring(self, interval: int = 300):  # 5 minutes
        """Start cost monitoring"""
        if self._monitoring_active:
            self.logger.warning("Cost monitoring already active")
            return
            
        self._monitoring_active = True
        self._monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval)
        )
        self.logger.info("Database cost monitoring started")
        
    async def stop_monitoring(self):
        """Stop cost monitoring"""
        self._monitoring_active = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Database cost monitoring stopped")
        
    async def _monitoring_loop(self, interval: int):
        """Main cost monitoring loop"""
        while self._monitoring_active:
            try:
                await self._collect_cost_metrics()
                await self._collect_resource_usage()
                await self._analyze_cost_trends()
                await self._generate_optimization_recommendations()
                await self._check_budget_alerts()
                await self._cleanup_old_data()
                await asyncio.sleep(interval)
            except Exception as e:
                self.logger.error(f"Cost monitoring error: {e}")
                await asyncio.sleep(interval)
                
    async def _collect_cost_metrics(self):
        """Collect current cost metrics"""



        try:
            # Collect database-specific costs
            db_costs = await self._get_database_costs()
            
            # Collect cloud infrastructure costs
            cloud_costs = await self._get_cloud_costs()
            
            # Combine and process costs
            all_costs = {**db_costs, **cloud_costs}
            
            for category, cost_data in all_costs.items():
                metric = CostMetric(
                    metric_id=f"cost_{category}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.utcnow(),
                    category=CostCategory(category),
                    resource_type=ResourceType(cost_data.get('resource_type', 'cpu')),
                    current_cost=cost_data['current'],
                    projected_cost=cost_data['projected'],
                    currency="EUR",
                    usage_units=cost_data.get('units', ''),
                    metadata=cost_data.get('metadata', {})
                )
                
                await self._store_cost_metric(metric)
                
        except Exception as e:
            self.logger.error(f"Failed to collect cost metrics: {e}")
            
    async def _get_database_costs(self) -> Dict[str, Dict]:
        """Get database-specific cost metrics"""



        try:
            async with get_database_session() as session:
                # Get database size and storage costs
                storage_query = text("""
                    SELECT 
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                        pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                    FROM pg_tables
                    WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                """)
                
                result = await session.execute(storage_query)
                tables = result.fetchall()
                
                total_storage_bytes = sum(table.size_bytes for table in tables)
                storage_gb = total_storage_bytes / (1024**3)
                
                # Calculate storage costs (example pricing)
                storage_cost_per_gb = 0.10  # EUR per GB per month
                monthly_storage_cost = storage_gb * storage_cost_per_gb
                
                # Get connection costs
                connection_query = text("""
                    SELECT count(*) as active_connections,
                           max(extract(epoch from now() - backend_start)) as longest_connection
                    FROM pg_stat_activity
                    WHERE state = 'active'
                """)
                
                result = await session.execute(connection_query)
                connection_data = result.fetchone()
                
                # Calculate compute costs based on connections and usage
                connection_cost = connection_data.active_connections * 0.05  # EUR per connection per hour
                
                return {
                    'storage': {
                        'current': monthly_storage_cost,
                        'projected': monthly_storage_cost * 1.1,  # 10% growth projection
                        'resource_type': 'disk',
                        'units': 'GB',
                        'metadata': {
                            'storage_gb': storage_gb,
                            'table_count': len(tables),
                            'largest_table': tables[0].tablename if tables else None
                        }
                    },
                    'compute': {
                        'current': connection_cost * 24 * 30,  # Monthly cost
                        'projected': connection_cost * 24 * 30 * 1.2,  # 20% growth
                        'resource_type': 'cpu',
                        'units': 'connections',
                        'metadata': {
                            'active_connections': connection_data.active_connections,
                            'longest_connection_hours': connection_data.longest_connection / 3600 if connection_data.longest_connection else 0
                        }
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get database costs: {e}")
            return {}
            
    async def _get_cloud_costs(self) -> Dict[str, Dict]:
        """Get cloud infrastructure costs"""



        try:
            cloud_costs = {}
            
            # AWS costs
            if hasattr(self.settings, 'aws_enabled') and self.settings.aws_enabled:
                aws_costs = await self.aws_cost_explorer.get_database_costs()
                cloud_costs.update(aws_costs)
                
            # Azure costs
            if hasattr(self.settings, 'azure_enabled') and self.settings.azure_enabled:
                azure_costs = await self.azure_cost_mgmt.get_database_costs()
                cloud_costs.update(azure_costs)
                
            # GCP costs
            if hasattr(self.settings, 'gcp_enabled') and self.settings.gcp_enabled:
                gcp_costs = await self.gcp_billing.get_database_costs()
                cloud_costs.update(gcp_costs)
                
            return cloud_costs
            
        except Exception as e:
            self.logger.error(f"Failed to get cloud costs: {e}")
            return {}
            
    async def _store_cost_metric(self, metric: CostMetric):
        """Store cost metric"""



        try:
            # Store in Redis
            await self.cache.set(
                f"cost_metric:{metric.metric_id}",
                json.dumps(metric.to_dict()),
                expire=2592000  # 30 days
            )
            
            # Add to timeline
            await self.cache.zadd(
                "cost_metrics_timeline",
                {metric.metric_id: metric.timestamp.timestamp()}
            )
            
            # Index by category
            await self.cache.zadd(
                f"cost_by_category:{metric.category.value}",
                {metric.metric_id: metric.current_cost}
            )
            
            self.logger.debug(f"Stored cost metric: {metric.metric_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to store cost metric: {e}")
            
    async def _collect_resource_usage(self):
        """Collect resource usage metrics"""



        try:
            # CPU usage
            cpu_usage = await self._get_cpu_usage()
            await self._store_resource_usage(cpu_usage)
            
            # Memory usage
            memory_usage = await self._get_memory_usage()
            await self._store_resource_usage(memory_usage)
            
            # Disk usage
            disk_usage = await self._get_disk_usage()
            await self._store_resource_usage(disk_usage)
            
            # Connection usage
            connection_usage = await self._get_connection_usage()
            await self._store_resource_usage(connection_usage)
            
        except Exception as e:
            self.logger.error(f"Failed to collect resource usage: {e}")
            
    async def _get_cpu_usage(self) -> ResourceUsage:
        """Get CPU usage metrics"""



        try:
            async with get_database_session() as session:
                # Get CPU-related statistics
                cpu_query = text("""
                    SELECT 
                        (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_queries,
                        (SELECT setting FROM pg_settings WHERE name = 'max_connections') as max_connections,
                        extract(epoch from now() - pg_postmaster_start_time()) as uptime_seconds
                """)
                
                result = await session.execute(cpu_query)
                data = result.fetchone()
                
                # Calculate CPU utilization (simplified)
                cpu_utilization = (data.active_queries / int(data.max_connections)) * 100
                
                return ResourceUsage(
                    resource_id=f"cpu_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.utcnow(),
                    resource_type=ResourceType.CPU,
                    allocated=100.0,  # 100% CPU available
                    utilized=cpu_utilization,
                    peak_usage=cpu_utilization,  # Would track over time
                    average_usage=cpu_utilization,
                    utilization_rate=cpu_utilization / 100,
                    cost_per_unit=0.02,  # EUR per CPU hour
                    total_cost=(cpu_utilization / 100) * 0.02 * 24 * 30,  # Monthly cost
                    efficiency_score=min(cpu_utilization / 80, 1.0)  # Optimal at 80% usage
                )
                
        except Exception as e:
            self.logger.error(f"Failed to get CPU usage: {e}")
            return None
            
    async def _get_memory_usage(self) -> ResourceUsage:
        """Get memory usage metrics"""



        try:
            async with get_database_session() as session:
                # Get memory statistics
                memory_query = text("""
                    SELECT 
                        setting as shared_buffers
                    FROM pg_settings 
                    WHERE name = 'shared_buffers'
                """)
                
                result = await session.execute(memory_query)
                data = result.fetchone()
                
                # Parse shared_buffers setting (e.g., "128MB")
                shared_buffers_str = data.shared_buffers
                if shared_buffers_str.endswith('MB'):
                    shared_buffers_mb = int(shared_buffers_str[:-2])
                elif shared_buffers_str.endswith('GB'):
                    shared_buffers_mb = int(shared_buffers_str[:-2]) * 1024
                else:
                    shared_buffers_mb = 128  # Default
                    
                # Estimate memory usage (simplified)
                total_memory_mb = shared_buffers_mb * 4  # Estimate total allocated
                used_memory_mb = shared_buffers_mb * 0.7  # Estimate usage
                
                return ResourceUsage(
                    resource_id=f"memory_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.utcnow(),
                    resource_type=ResourceType.MEMORY,
                    allocated=total_memory_mb,
                    utilized=used_memory_mb,
                    peak_usage=used_memory_mb,
                    average_usage=used_memory_mb,
                    utilization_rate=used_memory_mb / total_memory_mb,
                    cost_per_unit=0.01,  # EUR per MB per month
                    total_cost=total_memory_mb * 0.01,
                    efficiency_score=min((used_memory_mb / total_memory_mb) / 0.8, 1.0)
                )
                
        except Exception as e:
            self.logger.error(f"Failed to get memory usage: {e}")
            return None
            
    async def _get_disk_usage(self) -> ResourceUsage:
        """Get disk usage metrics"""



        try:
            async with get_database_session() as session:
                # Get disk usage statistics
                disk_query = text("""
                    SELECT 
                        sum(pg_total_relation_size(oid)) as total_size
                    FROM pg_class
                    WHERE relkind IN ('r', 'i')
                """)
                
                result = await session.execute(disk_query)
                data = result.fetchone()
                
                total_size_bytes = data.total_size or 0
                total_size_gb = total_size_bytes / (1024**3)
                
                # Estimate allocated vs used storage
                allocated_gb = total_size_gb * 1.5  # Assume 50% overhead
                
                return ResourceUsage(
                    resource_id=f"disk_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.utcnow(),
                    resource_type=ResourceType.DISK,
                    allocated=allocated_gb,
                    utilized=total_size_gb,
                    peak_usage=total_size_gb,
                    average_usage=total_size_gb,
                    utilization_rate=total_size_gb / allocated_gb if allocated_gb > 0 else 0,
                    cost_per_unit=0.10,  # EUR per GB per month
                    total_cost=allocated_gb * 0.10,
                    efficiency_score=min((total_size_gb / allocated_gb) / 0.8, 1.0) if allocated_gb > 0 else 0
                )
                
        except Exception as e:
            self.logger.error(f"Failed to get disk usage: {e}")
            return None
            
    async def _get_connection_usage(self) -> ResourceUsage:
        """Get connection usage metrics"""



        try:
            async with get_database_session() as session:
                # Get connection statistics
                conn_query = text("""
                    SELECT 
                        count(*) as current_connections,
                        (SELECT setting FROM pg_settings WHERE name = 'max_connections') as max_connections,
                        count(*) FILTER (WHERE state = 'active') as active_connections,
                        count(*) FILTER (WHERE state = 'idle') as idle_connections
                    FROM pg_stat_activity
                """)
                
                result = await session.execute(conn_query)
                data = result.fetchone()
                
                max_connections = int(data.max_connections)
                current_connections = data.current_connections
                
                return ResourceUsage(
                    resource_id=f"connections_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.utcnow(),
                    resource_type=ResourceType.CONNECTIONS,
                    allocated=max_connections,
                    utilized=current_connections,
                    peak_usage=current_connections,
                    average_usage=current_connections,
                    utilization_rate=current_connections / max_connections,
                    cost_per_unit=0.05,  # EUR per connection per day
                    total_cost=max_connections * 0.05 * 30,  # Monthly cost
                    efficiency_score=min((current_connections / max_connections) / 0.8, 1.0)
                )
                
        except Exception as e:
            self.logger.error(f"Failed to get connection usage: {e}")
            return None
            
    async def _store_resource_usage(self, usage: ResourceUsage):
        """Store resource usage data"""
        if not usage:
            return
            
        try:
            # Store in Redis
            await self.cache.set(
                f"resource_usage:{usage.resource_id}",
                json.dumps(usage.to_dict()),
                expire=2592000  # 30 days
            )
            
            # Add to timeline
            await self.cache.zadd(
                f"resource_timeline:{usage.resource_type.value}",
                {usage.resource_id: usage.timestamp.timestamp()}
            )
            
            # Track current values
            self.resource_usage[usage.resource_type.value] = usage
            
            self.logger.debug(f"Stored resource usage: {usage.resource_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to store resource usage: {e}")
            
    async def _analyze_cost_trends(self):
        """Analyze cost trends and patterns"""



        try:
            # Get recent cost metrics
            recent_metrics = await self._get_recent_cost_metrics(hours=24)
            
            if len(recent_metrics) < 2:
                return
                
            # Calculate trends by category
            cost_trends = {}
            for category in CostCategory:
                category_metrics = [m for m in recent_metrics if m['category'] == category.value]
                if len(category_metrics) >= 2:
                    trend = self._calculate_cost_trend(category_metrics)
                    cost_trends[category.value] = trend
                    
            # Store trends
            await self.cache.set(
                "cost_trends",
                json.dumps(cost_trends),
                expire=3600  # 1 hour
            )
            
            # Check for significant trend changes
            await self._check_cost_trend_alerts(cost_trends)
            
        except Exception as e:
            self.logger.error(f"Failed to analyze cost trends: {e}")
            
    def _calculate_cost_trend(self, metrics: List[Dict]) -> Dict[str, float]:
        """Calculate cost trend for metrics"""
        if len(metrics) < 2:
            return {'trend': 0.0, 'confidence': 0.0}
            
        # Sort by timestamp
        metrics.sort(key=lambda x: x['timestamp'])
        
        costs = [m['current_cost'] for m in metrics]
        
        # Calculate simple linear trend
        n = len(costs)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(costs)
        
        numerator = sum((i - x_mean) * (costs[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        trend = numerator / denominator if denominator != 0 else 0.0
        
        # Calculate confidence based on R-squared
        predicted = [y_mean + trend * (i - x_mean) for i in range(n)]
        ss_res = sum((costs[i] - predicted[i]) ** 2 for i in range(n))
        ss_tot = sum((costs[i] - y_mean) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
        
        return {
            'trend': trend,
            'confidence': max(r_squared, 0.0),
            'current_cost': costs[-1],
            'projected_daily': trend * 24,  # Daily trend
            'projected_monthly': trend * 24 * 30  # Monthly trend
        }
        
    async def _get_recent_cost_metrics(self, hours: int = 24) -> List[Dict]:
        """Get recent cost metrics"""



        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            cutoff_timestamp = cutoff_time.timestamp()
            
            metric_ids = await self.cache.zrangebyscore(
                "cost_metrics_timeline",
                cutoff_timestamp,
                "+inf"
            )
            
            metrics = []
            for metric_id in metric_ids:
                metric_data = await self.cache.get(f"cost_metric:{metric_id}")
                if metric_data:
                    metrics.append(json.loads(metric_data))
                    
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get recent cost metrics: {e}")
            return []
            
    async def _check_cost_trend_alerts(self, trends: Dict[str, Dict]):
        """Check for cost trend alerts"""



        try:
            for category, trend_data in trends.items():
                monthly_projection = trend_data.get('projected_monthly', 0.0)
                
                # Check if projected cost exceeds budget
                budget = self.cost_budgets.get(category, {}).get('limit', 0.0)
                
                if budget > 0 and monthly_projection > budget:
                    await self._send_cost_trend_alert(category, trend_data, budget)
                    
        except Exception as e:
            self.logger.error(f"Failed to check cost trend alerts: {e}")
            
    async def _send_cost_trend_alert(self, category: str, trend_data: Dict, budget: float):
        """Send cost trend alert"""



        try:
            await self.notification_manager.send_cost_alert(
                severity='HIGH',
                title=f'Cost Trend Alert: {category.title()}',
                message=f"Projected monthly cost ({trend_data['projected_monthly']:.2f} EUR) exceeds budget ({budget:.2f} EUR)",
                details={
                    'category': category,
                    'current_trend': trend_data,
                    'budget_limit': budget,
                    'overage_amount': trend_data['projected_monthly'] - budget
                }
            )
        except Exception as e:
            self.logger.error(f"Failed to send cost trend alert: {e}")
            
    async def _generate_optimization_recommendations(self):
        """Generate AI-powered optimization recommendations"""



        try:
            # Get current resource usage
            current_usage = list(self.resource_usage.values())
            
            if not current_usage:
                return
                
            # Generate recommendations using AI
            recommendations = await self.cost_ai.generate_recommendations(
                current_usage, self.cost_metrics
            )
            
            for rec in recommendations:
                self.optimization_recommendations[rec.recommendation_id] = rec
                await self._store_optimization_recommendation(rec)
                
                # Send high-impact recommendations
                if rec.savings_potential > 1000.0:  # > 1000 EUR savings
                    await self._send_optimization_alert(rec)
                    
        except Exception as e:
            self.logger.error(f"Failed to generate optimization recommendations: {e}")
            
    async def _store_optimization_recommendation(self, recommendation: OptimizationRecommendation):
        """Store optimization recommendation"""



        try:
            await self.cache.set(
                f"optimization_rec:{recommendation.recommendation_id}",
                json.dumps(recommendation.to_dict()),
                expire=2592000  # 30 days
            )
            
            # Index by strategy
            await self.cache.sadd(
                f"recommendations_by_strategy:{recommendation.strategy.value}",
                recommendation.recommendation_id
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store optimization recommendation: {e}")
            
    async def _send_optimization_alert(self, recommendation: OptimizationRecommendation):
        """Send optimization recommendation alert"""



        try:
            await self.notification_manager.send_optimization_alert(
                title='Cost Optimization Opportunity',
                message=f"Potential savings: {recommendation.savings_potential:.2f} EUR",
                details=recommendation.to_dict()
            )
        except Exception as e:
            self.logger.error(f"Failed to send optimization alert: {e}")
            
    async def _check_budget_alerts(self):
        """Check budget thresholds and send alerts"""



        try:
            current_costs = await self._calculate_current_monthly_costs()
            
            for budget_category, budget_config in self.cost_budgets.items():
                current_cost = current_costs.get(budget_category, 0.0)
                budget_limit = budget_config['limit']
                warning_threshold = budget_config['warning_threshold']
                critical_threshold = budget_config['critical_threshold']
                
                usage_percentage = current_cost / budget_limit if budget_limit > 0 else 0
                
                # Check thresholds
                if usage_percentage >= critical_threshold:
                    await self._send_budget_alert(budget_category, current_cost, budget_limit, 'CRITICAL')
                elif usage_percentage >= warning_threshold:
                    await self._send_budget_alert(budget_category, current_cost, budget_limit, 'WARNING')
                    
        except Exception as e:
            self.logger.error(f"Failed to check budget alerts: {e}")
            
    async def _calculate_current_monthly_costs(self) -> Dict[str, float]:
        """Calculate current monthly costs by category"""



        try:
            # Get costs for current month
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            costs_by_category = defaultdict(float)
            
            for category in CostCategory:
                category_costs = await self.cache.zrangebyscore(
                    f"cost_by_category:{category.value}",
                    month_start.timestamp(),
                    "+inf",
                    withscores=True
                )
                
                total_cost = sum(score for _, score in category_costs)
                costs_by_category[category.value] = total_cost
                
            # Calculate total
            costs_by_category['monthly_total'] = sum(costs_by_category.values())
            
            return dict(costs_by_category)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate current monthly costs: {e}")
            return {}
            
    async def _send_budget_alert(self, category: str, current_cost: float, budget_limit: float, severity: str):
        """Send budget alert"""



        try:
            usage_percentage = (current_cost / budget_limit) * 100
            
            await self.notification_manager.send_budget_alert(
                severity=severity,
                title=f'Budget Alert: {category.title()}',
                message=f"Current spending: {current_cost:.2f} EUR ({usage_percentage:.1f}% of budget)",
                details={
                    'category': category,
                    'current_cost': current_cost,
                    'budget_limit': budget_limit,
                    'usage_percentage': usage_percentage,
                    'remaining_budget': budget_limit - current_cost
                }
            )
        except Exception as e:
            self.logger.error(f"Failed to send budget alert: {e}")
            
    async def _cleanup_old_data(self):
        """Cleanup old cost monitoring data"""



        try:
            # Remove data older than 90 days
            cutoff_time = datetime.utcnow() - timedelta(days=90)
            cutoff_timestamp = cutoff_time.timestamp()
            
            # Cleanup cost metrics
            await self.cache.zremrangebyscore(
                "cost_metrics_timeline",
                "-inf",
                cutoff_timestamp
            )
            
            # Cleanup resource usage data
            for resource_type in ResourceType:
                await self.cache.zremrangebyscore(
                    f"resource_timeline:{resource_type.value}",
                    "-inf",
                    cutoff_timestamp
                )
                
            self.logger.debug("Cleaned up old cost monitoring data")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
            
    async def get_cost_summary(self, period: str = "monthly") -> Dict[str, Any]:
        """Get comprehensive cost summary"""



        try:
            if period == "daily":
                hours = 24
            elif period == "weekly":
                hours = 24 * 7
            else:  # monthly
                hours = 24 * 30
                
            # Get cost metrics
            cost_metrics = await self._get_recent_cost_metrics(hours)
            
            # Calculate summary statistics
            total_current_cost = sum(m['current_cost'] for m in cost_metrics)
            total_projected_cost = sum(m['projected_cost'] for m in cost_metrics)
            
            costs_by_category = defaultdict(float)
            for metric in cost_metrics:
                costs_by_category[metric['category']] += metric['current_cost']
                
            # Get optimization recommendations
            active_recommendations = len(self.optimization_recommendations)
            total_savings_potential = sum(
                rec.savings_potential for rec in self.optimization_recommendations.values()
            )
            
            # Get resource efficiency
            resource_efficiency = {}
            for resource_type, usage in self.resource_usage.items():
                resource_efficiency[resource_type] = usage.efficiency_score
                
            return {
                'period': period,
                'total_current_cost': total_current_cost,
                'total_projected_cost': total_projected_cost,
                'cost_by_category': dict(costs_by_category),
                'optimization_recommendations': active_recommendations,
                'total_savings_potential': total_savings_potential,
                'resource_efficiency': resource_efficiency,
                'budget_status': await self._get_budget_status(),
                'monitoring_active': self._monitoring_active,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get cost summary: {e}")
            return {}
            
    async def _get_budget_status(self) -> Dict[str, Dict]:
        """Get current budget status"""



        try:
            current_costs = await self._calculate_current_monthly_costs()
            budget_status = {}
            
            for category, budget_config in self.cost_budgets.items():
                current_cost = current_costs.get(category, 0.0)
                budget_limit = budget_config['limit']
                
                usage_percentage = (current_cost / budget_limit) * 100 if budget_limit > 0 else 0
                
                budget_status[category] = {
                    'current_cost': current_cost,
                    'budget_limit': budget_limit,
                    'usage_percentage': usage_percentage,
                    'remaining_budget': budget_limit - current_cost,
                    'status': 'OK' if usage_percentage < 80 else 'WARNING' if usage_percentage < 95 else 'CRITICAL'
                }
                
            return budget_status
            
        except Exception as e:
            self.logger.error(f"Failed to get budget status: {e}")
            return {}


class ResourceOptimizer:
    """Advanced resource optimization engine"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
    async def optimize_resources(self, usage_data: List[ResourceUsage]) -> List[OptimizationRecommendation]:
        """Generate resource optimization recommendations"""
        # Implementation for resource optimization
        pass
        
    async def right_size_instances(self, current_usage: Dict[str, ResourceUsage]) -> List[Dict]:
        """Recommend instance right-sizing"""
        # Implementation for instance right-sizing
        pass


class CostAnalyzer:
    """Advanced cost analysis and forecasting"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
    async def forecast_costs(self, historical_data: List[CostMetric], periods: int = 12) -> List[Dict]:
        """Forecast future costs"""
        # Implementation for cost forecasting
        pass
        
    async def analyze_cost_drivers(self, cost_data: List[CostMetric]) -> Dict[str, Any]:
        """Analyze main cost drivers"""
        # Implementation for cost driver analysis
        pass
