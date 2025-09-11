"""MongoDB Write Concern Optimizer
================================

Intelligent write concern configuration for optimal performance and data durability.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
from pymongo.write_concern import WriteConcern

logger = logging.getLogger(__name__)

class DurabilityLevel(Enum):
    """Write durability level enumeration."""
    NONE = "none"          # w=0, no acknowledgment
    ACKNOWLEDGED = "ack"   # w=1, acknowledged by primary
    MAJORITY = "majority"  # w="majority", acknowledged by majority
    ALL = "all"           # w="all", acknowledged by all members
    CUSTOM = "custom"     # Custom w value

class JournalRequirement(Enum):
    """Journal requirement enumeration."""
    NOT_REQUIRED = False
    REQUIRED = True
    ADAPTIVE = "adaptive"

@dataclass
class WriteConfiguration:
    """Write concern configuration."""
    durability_level: DurabilityLevel
    journal_required: Union[bool, str] = False
    write_timeout_ms: Optional[int] = None
    fsync_required: bool = False
    custom_w_value: Optional[Union[int, str]] = None

@dataclass
class WriteMetrics:
    """Write operation metrics."""
    total_writes: int = 0
    successful_writes: int = 0
    failed_writes: int = 0
    timeout_writes: int = 0
    avg_write_latency_ms: float = 0.0
    avg_replication_lag_ms: float = 0.0
    durability_failures: int = 0

class WriteConcernOptimizer:
    """Advanced write concern optimizer with adaptive strategies."""
    
    def __init__(self):
        """Initialize write concern optimizer."""
        self._metrics = WriteMetrics()
        self._latency_samples: List[float] = []
        self._replication_lag_samples: List[float] = []
        
        # Adaptive configuration
        self._adaptive_config = {
            'latency_threshold_ms': 100,
            'timeout_threshold_ms': 5000,
            'failure_rate_threshold': 0.05,
            'sample_size': 100,
            'replication_lag_threshold_ms': 1000
        }
        
        # Current configuration
        self._current_config = WriteConfiguration(
            durability_level=DurabilityLevel.ACKNOWLEDGED,
            journal_required=False
        )
        
        # Replica set information
        self._replica_set_size = 3  # Default assumption
        self._known_secondaries = 0
    
    def optimize_write_concern(self, operation_type: str,
                             criticality: str = "normal",
                             performance_priority: bool = False) -> WriteConcern:
        """Optimize write concern for specific operation.
        
        Args:
            operation_type: Type of write operation (insert, update, delete, etc.)
            criticality: Data criticality level (low, normal, high, critical)
            performance_priority: Whether to prioritize performance over durability
            
        Returns:
            Optimized write concern
        """
        # Determine optimal configuration based on criticality
        if criticality == "critical":
            config = WriteConfiguration(
                durability_level=DurabilityLevel.MAJORITY,
                journal_required=True,
                write_timeout_ms=10000,
                fsync_required=True
            )
        elif criticality == "high":
            config = WriteConfiguration(
                durability_level=DurabilityLevel.MAJORITY,
                journal_required=True,
                write_timeout_ms=5000
            )
        elif criticality == "low" or performance_priority:
            config = WriteConfiguration(
                durability_level=DurabilityLevel.ACKNOWLEDGED,
                journal_required=False,
                write_timeout_ms=1000
            )
        else:  # normal
            config = self._get_adaptive_configuration(operation_type)
        
        write_concern = self._create_write_concern(config)
        
        logger.debug(f"Optimized write concern for {operation_type} ({criticality}): "
                    f"w={write_concern.acknowledged}, j={write_concern.journal}")
        
        return write_concern
    
    def configure_for_workload(self, workload_profile: Dict[str, Any]) -> WriteConfiguration:
        """Configure write concern for specific workload profile.
        
        Args:
            workload_profile: Workload characteristics
            
        Returns:
            Optimized write configuration
        """
        write_heavy = workload_profile.get('write_percentage', 50) > 70
        batch_operations = workload_profile.get('batch_operations', False)
        real_time_required = workload_profile.get('real_time_required', False)
        data_criticality = workload_profile.get('data_criticality', 'normal')
        network_latency_ms = workload_profile.get('network_latency_ms', 10)
        
        # Determine optimal configuration
        if data_criticality == "critical":
            durability = DurabilityLevel.MAJORITY
            journal = True
            timeout = 10000
        elif real_time_required and not write_heavy:
            durability = DurabilityLevel.ACKNOWLEDGED
            journal = False
            timeout = 1000
        elif write_heavy or batch_operations:
            durability = DurabilityLevel.ACKNOWLEDGED
            journal = False
            timeout = 5000
        else:
            durability = DurabilityLevel.MAJORITY
            journal = True
            timeout = max(5000, network_latency_ms * 10)
        
        config = WriteConfiguration(
            durability_level=durability,
            journal_required=journal,
            write_timeout_ms=timeout
        )
        
        self._current_config = config
        logger.info(f"Configured write concern for workload: {durability.value}")
        
        return config
    
    def create_bulk_operation_concern(self, batch_size: int,
                                    operation_type: str = "mixed") -> WriteConcern:
        """Create optimized write concern for bulk operations.
        
        Args:
            batch_size: Size of the bulk operation
            operation_type: Type of bulk operation
            
        Returns:
            Optimized write concern for bulk operations
        """
        # For large batches, prioritize performance
        if batch_size > 1000:
            config = WriteConfiguration(
                durability_level=DurabilityLevel.ACKNOWLEDGED,
                journal_required=False,
                write_timeout_ms=30000  # Longer timeout for large batches
            )
        elif batch_size > 100:
            config = WriteConfiguration(
                durability_level=DurabilityLevel.ACKNOWLEDGED,
                journal_required=True,
                write_timeout_ms=10000
            )
        else:
            config = WriteConfiguration(
                durability_level=DurabilityLevel.MAJORITY,
                journal_required=True,
                write_timeout_ms=5000
            )
        
        return self._create_write_concern(config)
    
    def record_write_operation(self, operation_type: str, latency_ms: float,
                             success: bool, timeout_occurred: bool = False,
                             replication_lag_ms: float = 0,
                             durability_achieved: bool = True) -> None:
        """Record write operation metrics.
        
        Args:
            operation_type: Type of write operation
            latency_ms: Operation latency in milliseconds
            success: Whether operation was successful
            timeout_occurred: Whether operation timed out
            replication_lag_ms: Replication lag in milliseconds
            durability_achieved: Whether desired durability was achieved
        """
        self._metrics.total_writes += 1
        
        if success:
            self._metrics.successful_writes += 1
        else:
            self._metrics.failed_writes += 1
        
        if timeout_occurred:
            self._metrics.timeout_writes += 1
        
        if not durability_achieved:
            self._metrics.durability_failures += 1
        
        # Update latency tracking
        self._latency_samples.append(latency_ms)
        if len(self._latency_samples) > self._adaptive_config['sample_size']:
            self._latency_samples = self._latency_samples[-self._adaptive_config['sample_size']:]
        
        self._metrics.avg_write_latency_ms = sum(self._latency_samples) / len(self._latency_samples)
        
        # Update replication lag tracking
        if replication_lag_ms > 0:
            self._replication_lag_samples.append(replication_lag_ms)
            if len(self._replication_lag_samples) > self._adaptive_config['sample_size']:
                self._replication_lag_samples = self._replication_lag_samples[-self._adaptive_config['sample_size']:]
            
            self._metrics.avg_replication_lag_ms = (
                sum(self._replication_lag_samples) / len(self._replication_lag_samples)
            )
        
        logger.debug(f"Recorded write operation: {operation_type}, "
                    f"latency: {latency_ms:.1f}ms, success: {success}")
    
    def update_replica_set_info(self, primary_count: int, secondary_count: int) -> None:
        """Update replica set topology information.
        
        Args:
            primary_count: Number of primary nodes (should be 1)
            secondary_count: Number of secondary nodes
        """
        self._replica_set_size = primary_count + secondary_count
        self._known_secondaries = secondary_count
        
        logger.info(f"Updated replica set info: {self._replica_set_size} total members, "
                   f"{secondary_count} secondaries")
    
    def get_performance_recommendations(self) -> List[str]:
        """Get performance optimization recommendations.
        
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        # Failure rate analysis
        if self._metrics.total_writes > 0:
            failure_rate = self._metrics.failed_writes / self._metrics.total_writes
            if failure_rate > self._adaptive_config['failure_rate_threshold']:
                recommendations.append(
                    f"High write failure rate ({failure_rate:.2%}). "
                    "Consider reducing write concern or increasing timeout."
                )
        
        # Timeout analysis
        if self._metrics.total_writes > 0:
            timeout_rate = self._metrics.timeout_writes / self._metrics.total_writes
            if timeout_rate > 0.05:  # 5% threshold
                recommendations.append(
                    f"High timeout rate ({timeout_rate:.2%}). "
                    "Consider increasing wtimeout or using w=1 for non-critical operations."
                )
        
        # Latency analysis
        if self._metrics.avg_write_latency_ms > self._adaptive_config['latency_threshold_ms']:
            recommendations.append(
                f"High average write latency ({self._metrics.avg_write_latency_ms:.1f}ms). "
                "Consider using w=1 for performance-critical operations or "
                "optimizing network infrastructure."
            )
        
        # Replication lag analysis
        if (self._metrics.avg_replication_lag_ms > 
            self._adaptive_config['replication_lag_threshold_ms']):
            recommendations.append(
                f"High replication lag ({self._metrics.avg_replication_lag_ms:.1f}ms). "
                "Consider optimizing secondary nodes or network connectivity."
            )
        
        # Durability analysis
        if self._metrics.total_writes > 0:
            durability_failure_rate = self._metrics.durability_failures / self._metrics.total_writes
            if durability_failure_rate > 0.01:  # 1% threshold
                recommendations.append(
                    f"Durability failures detected ({durability_failure_rate:.2%}). "
                    "Consider increasing write concern or investigating replica set health."
                )
        
        return recommendations
    
    def create_geographic_configuration(self, data_centers: List[str],
                                      primary_dc: str) -> WriteConfiguration:
        """Create geographically optimized write configuration.
        
        Args:
            data_centers: List of data center names
            primary_dc: Primary data center
            
        Returns:
            Geographic write configuration
        """
        # For geographic distribution, use custom write concern
        # to ensure writes reach multiple data centers
        if len(data_centers) >= 3:
            # Majority across data centers
            config = WriteConfiguration(
                durability_level=DurabilityLevel.MAJORITY,
                journal_required=True,
                write_timeout_ms=10000
            )
        elif len(data_centers) == 2:
            # At least one replica in each DC
            config = WriteConfiguration(
                durability_level=DurabilityLevel.CUSTOM,
                custom_w_value=2,  # Primary + one secondary
                journal_required=True,
                write_timeout_ms=15000  # Longer timeout for geo-distribution
            )
        else:
            # Single DC, use majority
            config = WriteConfiguration(
                durability_level=DurabilityLevel.MAJORITY,
                journal_required=True,
                write_timeout_ms=5000
            )
        
        logger.info(f"Created geographic write configuration for DCs: {data_centers}")
        return config
    
    def get_metrics(self) -> WriteMetrics:
        """Get current write metrics.
        
        Returns:
            Current write operation metrics
        """
        return self._metrics
    
    def reset_metrics(self) -> None:
        """Reset all metrics counters."""
        self._metrics = WriteMetrics()
        self._latency_samples.clear()
        self._replication_lag_samples.clear()
        logger.info("Write concern metrics reset")
    
    def _get_adaptive_configuration(self, operation_type: str) -> WriteConfiguration:
        """Get adaptive write concern configuration based on current metrics."""
        # Default to acknowledged writes
        durability = DurabilityLevel.ACKNOWLEDGED
        journal = False
        timeout = 5000
        
        # Adapt based on performance metrics
        if len(self._latency_samples) >= 10:
            recent_latency = sum(self._latency_samples[-10:]) / 10
            
            if recent_latency > self._adaptive_config['latency_threshold_ms']:
                # High latency, reduce durability requirements
                durability = DurabilityLevel.ACKNOWLEDGED
                journal = False
                timeout = 1000
            elif recent_latency < 50:  # Very low latency
                # Low latency, can afford stronger durability
                durability = DurabilityLevel.MAJORITY
                journal = True
                timeout = 5000
        
        # Adapt based on failure rates
        if self._metrics.total_writes > 0:
            failure_rate = self._metrics.failed_writes / self._metrics.total_writes
            if failure_rate > self._adaptive_config['failure_rate_threshold']:
                # High failures, reduce requirements
                durability = DurabilityLevel.ACKNOWLEDGED
                journal = False
                timeout = max(timeout, 10000)
        
        # Consider operation type
        if operation_type in ['analytics_insert', 'bulk_insert', 'temporary_data']:
            # Non-critical operations
            durability = DurabilityLevel.ACKNOWLEDGED
            journal = False
        elif operation_type in ['user_data', 'financial', 'audit_log']:
            # Critical operations
            durability = DurabilityLevel.MAJORITY
            journal = True
        
        return WriteConfiguration(
            durability_level=durability,
            journal_required=journal,
            write_timeout_ms=timeout
        )
    
    def _create_write_concern(self, config: WriteConfiguration) -> WriteConcern:
        """Create PyMongo write concern object."""
        kwargs = {}
        
        # Set w (write concern)
        if config.durability_level == DurabilityLevel.NONE:
            kwargs['w'] = 0
        elif config.durability_level == DurabilityLevel.ACKNOWLEDGED:
            kwargs['w'] = 1
        elif config.durability_level == DurabilityLevel.MAJORITY:
            kwargs['w'] = "majority"
        elif config.durability_level == DurabilityLevel.ALL:
            kwargs['w'] = "all"
        elif config.durability_level == DurabilityLevel.CUSTOM:
            kwargs['w'] = config.custom_w_value or 1
        else:
            kwargs['w'] = 1  # Default
        
        # Set journal requirement
        if isinstance(config.journal_required, bool):
            kwargs['j'] = config.journal_required
        # For adaptive journal, we'll decide based on current metrics
        elif config.journal_required == "adaptive":
            # Use journal if latency is acceptable
            if self._metrics.avg_write_latency_ms < self._adaptive_config['latency_threshold_ms']:
                kwargs['j'] = True
            else:
                kwargs['j'] = False
        
        # Set timeout
        if config.write_timeout_ms:
            kwargs['wtimeout'] = config.write_timeout_ms
        
        # Set fsync requirement
        if config.fsync_required:
            kwargs['fsync'] = True
        
        return WriteConcern(**kwargs)

# Global optimizer instance
_default_optimizer: Optional[WriteConcernOptimizer] = None

def get_write_concern_optimizer() -> WriteConcernOptimizer:
    """Get or create default write concern optimizer."""
    global _default_optimizer
    if _default_optimizer is None:
        _default_optimizer = WriteConcernOptimizer()
    return _default_optimizer

__all__ = [
    'WriteConcernOptimizer', 'WriteConfiguration', 'WriteMetrics',
    'DurabilityLevel', 'JournalRequirement', 'get_write_concern_optimizer'
]