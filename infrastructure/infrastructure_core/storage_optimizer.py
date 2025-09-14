"""
Storage Optimizer - Enterprise Storage Performance Optimization and Management
© 2025 Fahed Mlaiel. All rights reserved.

Advanced storage optimization for Ainflue creator platform with intelligent
storage allocation, tiering, and performance monitoring for creator content.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid

logger = logging.getLogger(__name__)


class StorageType(Enum):
    """Storage types"""
    SSD_HIGH_PERFORMANCE = "ssd_high_performance"
    SSD_STANDARD = "ssd_standard"
    HDD_CAPACITY = "hdd_capacity"
    ARCHIVE_COLD = "archive_cold"
    GLACIER_DEEP = "glacier_deep"
    MEMORY_CACHE = "memory_cache"


class StorageTier(Enum):
    """Storage tiers"""
    HOT = "hot"          # Frequently accessed
    WARM = "warm"        # Occasionally accessed
    COOL = "cool"        # Rarely accessed
    COLD = "cold"        # Archive
    FROZEN = "frozen"    # Deep archive


class StorageOptimizationStrategy(Enum):
    """Storage optimization strategies"""
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    CAPACITY_OPTIMIZED = "capacity_optimized"
    COST_OPTIMIZED = "cost_optimized"
    AVAILABILITY_OPTIMIZED = "availability_optimized"
    BALANCED = "balanced"


@dataclass
class StorageMetrics:
    """Storage performance metrics"""
    timestamp: datetime
    total_capacity_tb: float
    used_capacity_tb: float
    free_capacity_tb: float
    iops_read: float
    iops_write: float
    throughput_mbps_read: float
    throughput_mbps_write: float
    latency_ms_read: float
    latency_ms_write: float
    queue_depth: float
    utilization_percent: float


class StorageOptimizer:
    """
    Enterprise storage optimization system for Ainflue platform.
    
    Provides:
    - Intelligent storage tiering and lifecycle management
    - Creator content specific storage optimization
    - Performance and cost optimization
    - Automated data migration and archiving
    - Storage capacity planning and forecasting
    - Multi-cloud storage orchestration
    """
    
    def __init__(self):
        self.storage_allocations = {}
        self.storage_tiers = {}
        self.storage_metrics_history = []
        self.lifecycle_policies = {}
        
        # Ainflue-specific storage configuration
        self.ainflue_storage_config = self._initialize_ainflue_storage_config()
        
        # Storage optimization settings
        self.optimization_config = {
            'target_utilization_percent': 80.0,
            'max_utilization_percent': 90.0,
            'target_iops_utilization': 75.0,
            'auto_tiering_enabled': True,
            'compression_enabled': True,
            'deduplication_enabled': True
        }
        
        logger.info("Storage optimizer initialized for Ainflue platform")
    
    def _initialize_ainflue_storage_config(self) -> Dict[str, Any]:
        """Initialize Ainflue-specific storage configuration"""
        
        config = {
            'total_storage_capacity_tb': 10000.0,  # 10 PB total
            'storage_types': {
                'ssd_high_performance': {
                    'capacity_tb': 500.0,
                    'cost_per_gb_month': 0.15,
                    'iops_per_gb': 50,
                    'latency_ms': 1.0
                },
                'ssd_standard': {
                    'capacity_tb': 1500.0,
                    'cost_per_gb_month': 0.08,
                    'iops_per_gb': 10,
                    'latency_ms': 5.0
                },
                'hdd_capacity': {
                    'capacity_tb': 5000.0,
                    'cost_per_gb_month': 0.03,
                    'iops_per_gb': 1,
                    'latency_ms': 20.0
                },
                'archive_cold': {
                    'capacity_tb': 2000.0,
                    'cost_per_gb_month': 0.01,
                    'iops_per_gb': 0.1,
                    'latency_ms': 1000.0
                },
                'glacier_deep': {
                    'capacity_tb': 1000.0,
                    'cost_per_gb_month': 0.002,
                    'iops_per_gb': 0.01,
                    'latency_ms': 43200000.0  # 12 hours
                }
            },
            'content_allocation': {
                'creator_uploads_active': {
                    'storage_type': 'ssd_high_performance',
                    'tier': 'hot',
                    'retention_days': 30
                },
                'creator_uploads_recent': {
                    'storage_type': 'ssd_standard',
                    'tier': 'warm',
                    'retention_days': 90
                },
                'creator_uploads_archive': {
                    'storage_type': 'hdd_capacity',
                    'tier': 'cool',
                    'retention_days': 365
                },
                'ai_models_active': {
                    'storage_type': 'ssd_high_performance',
                    'tier': 'hot',
                    'retention_days': 90
                },
                'ai_models_archive': {
                    'storage_type': 'ssd_standard',
                    'tier': 'warm',
                    'retention_days': 730
                },
                'revenue_data_active': {
                    'storage_type': 'ssd_high_performance',
                    'tier': 'hot',
                    'retention_days': 2555  # 7 years
                },
                'analytics_data': {
                    'storage_type': 'hdd_capacity',
                    'tier': 'cool',
                    'retention_days': 1095  # 3 years
                },
                'backup_data': {
                    'storage_type': 'archive_cold',
                    'tier': 'cold',
                    'retention_days': 2555
                },
                'compliance_archive': {
                    'storage_type': 'glacier_deep',
                    'tier': 'frozen',
                    'retention_days': 3650  # 10 years
                }
            },
            'replication_config': {
                'creator_content': {'replicas': 3, 'cross_region': True},
                'ai_models': {'replicas': 2, 'cross_region': True},
                'revenue_data': {'replicas': 4, 'cross_region': True},
                'analytics': {'replicas': 2, 'cross_region': False}
            }
        }
        
        return config
    
    async def optimize_storage_allocation(
        self,
        storage_metrics: Dict[str, Any],
        optimization_strategy: StorageOptimizationStrategy = StorageOptimizationStrategy.BALANCED
    ) -> Dict[str, Any]:
        """Optimize storage allocation based on usage metrics"""
        
        logger.info(f"Optimizing storage allocation with strategy: {optimization_strategy.value}")
        
        # Analyze current storage usage patterns
        usage_analysis = await self._analyze_storage_usage_patterns(storage_metrics)
        
        # Generate optimization recommendations
        recommendations = await self._generate_storage_optimization_recommendations(
            usage_analysis, optimization_strategy
        )
        
        # Apply optimizations
        optimization_results = await self._apply_storage_optimizations(recommendations)
        
        return {
            'strategy': optimization_strategy.value,
            'analysis': usage_analysis,
            'recommendations': recommendations,
            'results': optimization_results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _analyze_storage_usage_patterns(
        self,
        storage_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze storage usage patterns across different content types"""
        
        logger.info("Analyzing storage usage patterns")
        
        analysis = {
            'overall_utilization': 0.0,
            'storage_breakdown': {},
            'performance_metrics': {},
            'cost_analysis': {},
            'tiering_opportunities': [],
            'capacity_forecast': {}
        }
        
        total_storage_used = 0.0
        total_storage_capacity = 0.0
        
        # Analyze storage by content type
        for content_type, metrics in storage_metrics.items():
            storage_used = metrics.get('storage_used_tb', 0.0)
            storage_capacity = metrics.get('storage_capacity_tb', 0.0)
            iops_read = metrics.get('iops_read', 0.0)
            iops_write = metrics.get('iops_write', 0.0)
            
            total_storage_used += storage_used
            total_storage_capacity += storage_capacity
            
            analysis['storage_breakdown'][content_type] = {
                'storage_used_tb': storage_used,
                'storage_capacity_tb': storage_capacity,
                'utilization_percent': (storage_used / storage_capacity * 100.0) if storage_capacity > 0 else 0.0,
                'iops_read': iops_read,
                'iops_write': iops_write,
                'access_pattern': self._analyze_access_pattern(metrics),
                'cost_per_month': self._calculate_storage_cost(content_type, storage_used)
            }
            
            # Analyze performance metrics
            analysis['performance_metrics'][content_type] = {
                'latency_ms_read': metrics.get('latency_ms_read', 0.0),
                'latency_ms_write': metrics.get('latency_ms_write', 0.0),
                'throughput_mbps_read': metrics.get('throughput_mbps_read', 0.0),
                'throughput_mbps_write': metrics.get('throughput_mbps_write', 0.0),
                'performance_score': self._calculate_storage_performance_score(metrics)
            }
            
            # Identify tiering opportunities
            access_frequency = metrics.get('access_frequency_per_day', 0.0)
            current_tier = self._get_current_storage_tier(content_type)
            optimal_tier = self._determine_optimal_tier(access_frequency, metrics)
            
            if current_tier != optimal_tier:
                analysis['tiering_opportunities'].append({
                    'content_type': content_type,
                    'current_tier': current_tier,
                    'recommended_tier': optimal_tier,
                    'storage_amount_tb': storage_used,
                    'potential_savings': self._calculate_tiering_savings(
                        content_type, storage_used, current_tier, optimal_tier
                    )
                })
        
        analysis['overall_utilization'] = (total_storage_used / total_storage_capacity * 100.0) if total_storage_capacity > 0 else 0.0
        
        # Calculate cost analysis
        total_cost = sum(
            breakdown['cost_per_month']
            for breakdown in analysis['storage_breakdown'].values()
        )
        
        analysis['cost_analysis'] = {
            'total_monthly_cost': total_cost,
            'cost_per_tb': total_cost / total_storage_used if total_storage_used > 0 else 0.0,
            'cost_breakdown_by_type': {
                content_type: breakdown['cost_per_month']
                for content_type, breakdown in analysis['storage_breakdown'].items()
            }
        }
        
        # Capacity forecasting
        analysis['capacity_forecast'] = await self._forecast_storage_capacity(storage_metrics)
        
        return analysis
    
    def _analyze_access_pattern(self, metrics: Dict[str, Any]) -> str:
        """Analyze storage access pattern"""
        
        access_frequency = metrics.get('access_frequency_per_day', 0.0)
        read_write_ratio = metrics.get('read_write_ratio', 1.0)
        
        if access_frequency > 100:
            return 'high_frequency'
        elif access_frequency > 10:
            return 'medium_frequency'
        elif access_frequency > 1:
            return 'low_frequency'
        else:
            return 'archive'
    
    def _get_current_storage_tier(self, content_type: str) -> str:
        """Get current storage tier for content type"""
        return self.ainflue_storage_config['content_allocation'].get(
            content_type, {}
        ).get('tier', 'warm')
    
    def _determine_optimal_tier(self, access_frequency: float, metrics: Dict[str, Any]) -> str:
        """Determine optimal storage tier based on access patterns"""
        
        if access_frequency > 50:  # Daily access
            return 'hot'
        elif access_frequency > 5:  # Weekly access
            return 'warm'
        elif access_frequency > 0.5:  # Monthly access
            return 'cool'
        elif access_frequency > 0.1:  # Quarterly access
            return 'cold'
        else:  # Rarely accessed
            return 'frozen'
    
    def _calculate_storage_cost(self, content_type: str, storage_tb: float) -> float:
        """Calculate monthly storage cost"""
        
        storage_config = self.ainflue_storage_config['content_allocation'].get(content_type, {})
        storage_type = storage_config.get('storage_type', 'ssd_standard')
        
        cost_per_gb = self.ainflue_storage_config['storage_types'][storage_type]['cost_per_gb_month']
        return storage_tb * 1024 * cost_per_gb  # TB to GB conversion
    
    def _calculate_tiering_savings(
        self,
        content_type: str,
        storage_tb: float,
        current_tier: str,
        recommended_tier: str
    ) -> float:
        """Calculate potential savings from storage tiering"""
        
        # Simplified calculation - would be more complex in real implementation
        tier_cost_multipliers = {
            'hot': 1.0,
            'warm': 0.7,
            'cool': 0.4,
            'cold': 0.2,
            'frozen': 0.1
        }
        
        current_cost = self._calculate_storage_cost(content_type, storage_tb)
        current_multiplier = tier_cost_multipliers.get(current_tier, 1.0)
        recommended_multiplier = tier_cost_multipliers.get(recommended_tier, 1.0)
        
        savings_ratio = (current_multiplier - recommended_multiplier) / current_multiplier
        return current_cost * savings_ratio
    
    def _calculate_storage_performance_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate storage performance score"""
        
        latency_read = metrics.get('latency_ms_read', 100.0)
        latency_write = metrics.get('latency_ms_write', 100.0)
        throughput_read = metrics.get('throughput_mbps_read', 0.0)
        throughput_write = metrics.get('throughput_mbps_write', 0.0)
        iops_read = metrics.get('iops_read', 0.0)
        iops_write = metrics.get('iops_write', 0.0)
        
        # Score based on performance characteristics
        latency_score = max(0.0, 100.0 - (latency_read + latency_write) / 20.0)
        throughput_score = min(100.0, (throughput_read + throughput_write) / 100.0)
        iops_score = min(100.0, (iops_read + iops_write) / 1000.0)
        
        return (latency_score * 0.4 + throughput_score * 0.3 + iops_score * 0.3)
    
    async def _forecast_storage_capacity(
        self,
        storage_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Forecast future storage capacity needs"""
        
        logger.info("Forecasting storage capacity needs")
        
        forecast = {
            'forecast_horizon_months': 12,
            'growth_projections': {},
            'capacity_requirements': {},
            'cost_projections': {}
        }
        
        for content_type, metrics in storage_metrics.items():
            current_storage = metrics.get('storage_used_tb', 0.0)
            growth_rate = metrics.get('growth_rate_percent_monthly', 5.0) / 100.0
            
            # Project growth over 12 months
            projected_storage = current_storage
            monthly_projections = []
            
            for month in range(1, 13):
                projected_storage *= (1 + growth_rate)
                monthly_projections.append(projected_storage)
            
            forecast['growth_projections'][content_type] = {
                'current_storage_tb': current_storage,
                'projected_storage_12m_tb': projected_storage,
                'growth_rate_monthly_percent': growth_rate * 100.0,
                'monthly_projections': monthly_projections
            }
            
            # Calculate capacity requirements
            forecast['capacity_requirements'][content_type] = {
                'additional_capacity_needed_tb': max(0.0, projected_storage - current_storage),
                'capacity_buffer_tb': projected_storage * 0.2,  # 20% buffer
                'total_capacity_needed_tb': projected_storage * 1.2
            }
            
            # Project costs
            current_cost = self._calculate_storage_cost(content_type, current_storage)
            projected_cost = self._calculate_storage_cost(content_type, projected_storage)
            
            forecast['cost_projections'][content_type] = {
                'current_monthly_cost': current_cost,
                'projected_monthly_cost': projected_cost,
                'cost_increase': projected_cost - current_cost,
                'cost_increase_percent': ((projected_cost - current_cost) / current_cost * 100.0) if current_cost > 0 else 0.0
            }
        
        return forecast
    
    async def _generate_storage_optimization_recommendations(
        self,
        analysis: Dict[str, Any],
        strategy: StorageOptimizationStrategy
    ) -> List[Dict[str, Any]]:
        """Generate storage optimization recommendations"""
        
        logger.info("Generating storage optimization recommendations")
        
        recommendations = []
        
        # Storage tiering recommendations
        for opportunity in analysis['tiering_opportunities']:
            recommendations.append({
                'type': 'storage_tiering',
                'content_type': opportunity['content_type'],
                'action': 'migrate_to_optimal_tier',
                'parameter': 'storage_tier',
                'current_value': opportunity['current_tier'],
                'recommended_value': opportunity['recommended_tier'],
                'priority': 'medium',
                'estimated_improvement': f"${opportunity['potential_savings']:.2f}/month savings"
            })
        
        # Capacity planning recommendations
        for content_type, forecast in analysis['capacity_forecast']['capacity_requirements'].items():
            if forecast['additional_capacity_needed_tb'] > 0:
                recommendations.append({
                    'type': 'capacity_planning',
                    'content_type': content_type,
                    'action': 'expand_storage_capacity',
                    'parameter': 'storage_capacity_tb',
                    'recommended_value': forecast['total_capacity_needed_tb'],
                    'priority': 'high',
                    'estimated_improvement': 'Prevent capacity shortages'
                })
        
        # Performance optimization recommendations
        for content_type, perf_metrics in analysis['performance_metrics'].items():
            if perf_metrics['performance_score'] < 70.0:
                recommendations.append({
                    'type': 'performance_optimization',
                    'content_type': content_type,
                    'action': 'upgrade_storage_type',
                    'parameter': 'storage_type',
                    'priority': 'medium',
                    'estimated_improvement': '50% performance improvement'
                })
        
        # Strategy-specific recommendations
        if strategy == StorageOptimizationStrategy.COST_OPTIMIZED:
            recommendations.extend(await self._generate_cost_optimization_recommendations(analysis))
        elif strategy == StorageOptimizationStrategy.PERFORMANCE_OPTIMIZED:
            recommendations.extend(await self._generate_performance_optimization_recommendations(analysis))
        elif strategy == StorageOptimizationStrategy.AVAILABILITY_OPTIMIZED:
            recommendations.extend(await self._generate_availability_optimization_recommendations(analysis))
        
        return recommendations
    
    async def _apply_storage_optimizations(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply storage optimization recommendations"""
        
        logger.info(f"Applying {len(recommendations)} storage optimizations")
        
        results = {
            'applied_optimizations': 0,
            'failed_optimizations': 0,
            'storage_improvements': {},
            'cost_savings': 0.0
        }
        
        for recommendation in recommendations:
            try:
                success = await self._apply_single_storage_optimization(recommendation)
                
                if success:
                    results['applied_optimizations'] += 1
                    
                    content_type = recommendation.get('content_type', 'unknown')
                    improvement = recommendation.get('estimated_improvement', 'Unknown')
                    results['storage_improvements'][content_type] = improvement
                    
                    # Extract cost savings if mentioned
                    if 'savings' in improvement:
                        try:
                            savings = float(improvement.split('$')[1].split('/')[0])
                            results['cost_savings'] += savings
                        except:
                            pass
                else:
                    results['failed_optimizations'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to apply storage optimization: {e}")
                results['failed_optimizations'] += 1
        
        return results
    
    async def _apply_single_storage_optimization(
        self,
        recommendation: Dict[str, Any]
    ) -> bool:
        """Apply a single storage optimization"""
        
        action = recommendation['action']
        content_type = recommendation.get('content_type', 'unknown')
        
        logger.info(f"Applying storage optimization: {action} for {content_type}")
        
        try:
            if action == 'migrate_to_optimal_tier':
                await self._migrate_storage_tier(
                    content_type,
                    recommendation['recommended_value']
                )
            elif action == 'expand_storage_capacity':
                await self._expand_storage_capacity(
                    content_type,
                    recommendation['recommended_value']
                )
            elif action == 'upgrade_storage_type':
                await self._upgrade_storage_type(content_type)
            elif action == 'enable_compression':
                await self._enable_compression(content_type)
            elif action == 'configure_replication':
                await self._configure_replication(content_type)
            
            await asyncio.sleep(1)  # Simulate optimization time
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply storage optimization: {e}")
            return False
    
    # Implementation methods (simulate actual storage operations)
    async def _migrate_storage_tier(self, content_type: str, new_tier: str):
        logger.info(f"Migrating {content_type} to {new_tier} tier")
        await asyncio.sleep(2.0)  # Migration takes longer
    
    async def _expand_storage_capacity(self, content_type: str, new_capacity: float):
        logger.info(f"Expanding storage capacity for {content_type} to {new_capacity} TB")
        await asyncio.sleep(1.0)
    
    async def _upgrade_storage_type(self, content_type: str):
        logger.info(f"Upgrading storage type for {content_type}")
        await asyncio.sleep(1.5)
    
    async def _enable_compression(self, content_type: str):
        logger.info(f"Enabling compression for {content_type}")
        await asyncio.sleep(0.5)
    
    async def _configure_replication(self, content_type: str):
        logger.info(f"Configuring replication for {content_type}")
        await asyncio.sleep(1.0)
    
    async def _generate_cost_optimization_recommendations(
        self,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate cost-focused optimization recommendations"""
        
        recommendations = []
        
        # Recommend compression for large storage consumers
        for content_type, breakdown in analysis['storage_breakdown'].items():
            if breakdown['storage_used_tb'] > 100.0:  # Large storage usage
                recommendations.append({
                    'type': 'cost_optimization',
                    'content_type': content_type,
                    'action': 'enable_compression',
                    'parameter': 'compression_ratio',
                    'priority': 'medium',
                    'estimated_improvement': '30% storage cost reduction'
                })
        
        return recommendations
    
    async def _generate_performance_optimization_recommendations(
        self,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate performance-focused optimization recommendations"""
        
        recommendations = []
        
        # Recommend SSD upgrades for high-access content
        for content_type, perf_metrics in analysis['performance_metrics'].items():
            if perf_metrics['latency_ms_read'] > 50.0:  # High latency
                recommendations.append({
                    'type': 'performance_optimization',
                    'content_type': content_type,
                    'action': 'upgrade_to_ssd',
                    'parameter': 'storage_type',
                    'priority': 'high',
                    'estimated_improvement': '80% latency reduction'
                })
        
        return recommendations
    
    async def _generate_availability_optimization_recommendations(
        self,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate availability-focused optimization recommendations"""
        
        recommendations = []
        
        # Recommend additional replication for critical content
        critical_content = ['creator_uploads_active', 'revenue_data_active']
        
        for content_type in critical_content:
            if content_type in analysis['storage_breakdown']:
                recommendations.append({
                    'type': 'availability_optimization',
                    'content_type': content_type,
                    'action': 'increase_replication',
                    'parameter': 'replica_count',
                    'priority': 'high',
                    'estimated_improvement': '99.9% availability guarantee'
                })
        
        return recommendations
    
    async def monitor_storage_performance(
        self,
        duration_seconds: int = 300
    ) -> Dict[str, Any]:
        """Monitor storage performance for specified duration"""
        
        logger.info(f"Starting storage performance monitoring for {duration_seconds} seconds")
        
        monitoring_data = {
            'start_time': datetime.utcnow(),
            'duration_seconds': duration_seconds,
            'samples': [],
            'summary': {}
        }
        
        sample_interval = 20  # Sample every 20 seconds
        samples_count = duration_seconds // sample_interval
        
        for i in range(samples_count):
            sample = await self._collect_storage_metrics_sample()
            monitoring_data['samples'].append(sample)
            await asyncio.sleep(sample_interval)
        
        monitoring_data['summary'] = self._calculate_storage_monitoring_summary(
            monitoring_data['samples']
        )
        
        monitoring_data['end_time'] = datetime.utcnow()
        
        logger.info("Storage performance monitoring completed")
        return monitoring_data
    
    async def _collect_storage_metrics_sample(self) -> Dict[str, Any]:
        """Collect a single storage metrics sample"""
        
        import random
        
        total_capacity = self.ainflue_storage_config['total_storage_capacity_tb']
        
        sample = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_capacity_tb': total_capacity,
            'used_capacity_tb': random.uniform(total_capacity * 0.4, total_capacity * 0.85),
            'iops_read_total': random.uniform(10000.0, 100000.0),
            'iops_write_total': random.uniform(5000.0, 50000.0),
            'throughput_mbps_read': random.uniform(1000.0, 8000.0),
            'throughput_mbps_write': random.uniform(500.0, 4000.0),
            'latency_ms_read_avg': random.uniform(1.0, 50.0),
            'latency_ms_write_avg': random.uniform(2.0, 100.0),
            'queue_depth_avg': random.uniform(1.0, 32.0)
        }
        
        sample['free_capacity_tb'] = total_capacity - sample['used_capacity_tb']
        sample['utilization_percent'] = (sample['used_capacity_tb'] / total_capacity) * 100.0
        
        return sample
    
    def _calculate_storage_monitoring_summary(
        self,
        samples: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate summary statistics from storage monitoring samples"""
        
        if not samples:
            return {}
        
        metrics = [
            'utilization_percent',
            'iops_read_total',
            'iops_write_total',
            'throughput_mbps_read',
            'throughput_mbps_write',
            'latency_ms_read_avg',
            'latency_ms_write_avg',
            'queue_depth_avg'
        ]
        
        summary = {}
        
        for metric in metrics:
            values = [sample.get(metric, 0.0) for sample in samples]
            
            if values:
                summary[metric] = {
                    'average': sum(values) / len(values),
                    'minimum': min(values),
                    'maximum': max(values),
                    'p95': sorted(values)[int(len(values) * 0.95)] if len(values) > 20 else max(values)
                }
        
        # Calculate efficiency score
        avg_utilization = summary.get('utilization_percent', {}).get('average', 0.0)
        avg_read_latency = summary.get('latency_ms_read_avg', {}).get('average', 50.0)
        avg_write_latency = summary.get('latency_ms_write_avg', {}).get('average', 100.0)
        avg_iops_read = summary.get('iops_read_total', {}).get('average', 0.0)
        avg_iops_write = summary.get('iops_write_total', {}).get('average', 0.0)
        
        # Optimal utilization around 80%, low latency, high IOPS
        utilization_score = 100.0 - abs(avg_utilization - 80.0)
        latency_score = max(0.0, 100.0 - (avg_read_latency + avg_write_latency) / 2.0)
        iops_score = min(100.0, (avg_iops_read + avg_iops_write) / 1000.0)
        
        summary['efficiency_score'] = (utilization_score * 0.4 + latency_score * 0.4 + iops_score * 0.2)
        
        return summary