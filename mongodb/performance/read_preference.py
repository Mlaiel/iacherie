"""MongoDB Read Preference Optimizer
=================================

Intelligent read preference configuration for optimal performance and data consistency.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from pymongo.read_preferences import ReadPreference, Primary, Secondary, Nearest, PrimaryPreferred, SecondaryPreferred
from pymongo.read_concern import ReadConcern

logger = logging.getLogger(__name__)

class ReadPreferenceStrategy(Enum):
    """Read preference strategy enumeration."""
    PRIMARY = "primary"
    SECONDARY = "secondary" 
    NEAREST = "nearest"
    PRIMARY_PREFERRED = "primaryPreferred"
    SECONDARY_PREFERRED = "secondaryPreferred"
    ADAPTIVE = "adaptive"

class ReadConsistencyLevel(Enum):
    """Read consistency level enumeration."""
    LOCAL = "local"
    AVAILABLE = "available"
    MAJORITY = "majority"
    LINEARIZABLE = "linearizable"

@dataclass
class ReadConfiguration:
    """Read preference configuration."""
    preference: ReadPreferenceStrategy
    max_staleness_seconds: Optional[int] = None
    tag_sets: Optional[List[Dict[str, str]]] = None
    consistency_level: ReadConsistencyLevel = ReadConsistencyLevel.LOCAL
    hedge_enabled: bool = False

@dataclass 
class ReadMetrics:
    """Read operation metrics."""
    total_reads: int = 0
    primary_reads: int = 0
    secondary_reads: int = 0
    avg_read_latency_ms: float = 0.0
    read_errors: int = 0
    stale_reads: int = 0

class ReadPreferenceOptimizer:
    """Advanced read preference optimizer with adaptive strategies."""
    
    def __init__(self) -> None:
        """Initialize read preference optimizer."""
        self._metrics = ReadMetrics()
        self._latency_samples: List[float] = []
        
        # Adaptive configuration
        self._adaptive_config = {
            'primary_latency_threshold_ms': 100,
            'secondary_latency_threshold_ms': 50,
            'staleness_tolerance_seconds': 5,
            'error_rate_threshold': 0.05,
            'sample_size': 100
        }
        
        # Current configuration
        self._current_config = ReadConfiguration(
            preference=ReadPreferenceStrategy.PRIMARY_PREFERRED
        )
    
    def optimize_read_preference(self, operation_type: str, 
                                consistency_required: bool = False,
                                max_staleness_acceptable: int = None) -> ReadPreference:
        """Optimize read preference for specific operation.
        
        Args:
            operation_type: Type of read operation (query, aggregate, count, etc.)
            consistency_required: Whether strong consistency is required
            max_staleness_acceptable: Maximum acceptable staleness in seconds
            
        Returns:
            Optimized read preference
        """
        # Determine optimal strategy
        if consistency_required:
            strategy = ReadPreferenceStrategy.PRIMARY
        elif operation_type in ['analytics', 'reporting', 'search']:
            # Analytics can tolerate some staleness
            strategy = ReadPreferenceStrategy.SECONDARY_PREFERRED
        elif self._should_use_adaptive():
            strategy = self._get_adaptive_strategy()
        else:
            strategy = ReadPreferenceStrategy.PRIMARY_PREFERRED
        
        # Configure read preference
        read_pref = self._create_read_preference(
            strategy, 
            max_staleness_acceptable
        )
        
        logger.debug(f"Optimized read preference for {operation_type}: {strategy.value}")
        return read_pref
    
    def get_read_concern(self, consistency_level: ReadConsistencyLevel = None) -> ReadConcern:
        """Get optimized read concern.
        
        Args:
            consistency_level: Required consistency level
            
        Returns:
            Read concern configuration
        """
        if consistency_level is None:
            consistency_level = self._current_config.consistency_level
        
        read_concern_map = {
            ReadConsistencyLevel.LOCAL: ReadConcern("local"),
            ReadConsistencyLevel.AVAILABLE: ReadConcern("available"),
            ReadConsistencyLevel.MAJORITY: ReadConcern("majority"),
            ReadConsistencyLevel.LINEARIZABLE: ReadConcern("linearizable")
        }
        
        return read_concern_map.get(consistency_level, ReadConcern("local"))
    
    def configure_for_workload(self, workload_profile: Dict[str, Any]) -> ReadConfiguration:
        """Configure read preferences for specific workload profile.
        
        Args:
            workload_profile: Workload characteristics
            
        Returns:
            Optimized read configuration
        """
        read_heavy = workload_profile.get('read_percentage', 50) > 70
        analytics_heavy = workload_profile.get('analytics_percentage', 0) > 30
        real_time_required = workload_profile.get('real_time_required', False)
        geographic_distribution = workload_profile.get('geographic_distribution', False)
        
        # Determine optimal configuration
        if real_time_required:
            preference = ReadPreferenceStrategy.PRIMARY
            consistency = ReadConsistencyLevel.MAJORITY
        elif analytics_heavy:
            preference = ReadPreferenceStrategy.SECONDARY_PREFERRED
            consistency = ReadConsistencyLevel.LOCAL
        elif read_heavy and geographic_distribution:
            preference = ReadPreferenceStrategy.NEAREST
            consistency = ReadConsistencyLevel.LOCAL
        elif read_heavy:
            preference = ReadPreferenceStrategy.SECONDARY_PREFERRED
            consistency = ReadConsistencyLevel.LOCAL
        else:
            preference = ReadPreferenceStrategy.PRIMARY_PREFERRED
            consistency = ReadConsistencyLevel.LOCAL
        
        config = ReadConfiguration(
            preference=preference,
            consistency_level=consistency,
            max_staleness_seconds=workload_profile.get('max_staleness_seconds'),
            hedge_enabled=workload_profile.get('hedge_enabled', False)
        )
        
        self._current_config = config
        logger.info(f"Configured read preferences for workload: {preference.value}")
        
        return config
    
    def record_read_operation(self, operation_type: str, latency_ms: float,
                            read_from_primary: bool, error_occurred: bool = False,
                            data_staleness_seconds: float = 0) -> None:
        """Record read operation metrics.
        
        Args:
            operation_type: Type of read operation
            latency_ms: Operation latency in milliseconds
            read_from_primary: Whether read was from primary
            error_occurred: Whether operation resulted in error
            data_staleness_seconds: Data staleness in seconds
        """
        self._metrics.total_reads += 1
        
        if read_from_primary:
            self._metrics.primary_reads += 1
        else:
            self._metrics.secondary_reads += 1
        
        if error_occurred:
            self._metrics.read_errors += 1
        
        if data_staleness_seconds > self._adaptive_config['staleness_tolerance_seconds']:
            self._metrics.stale_reads += 1
        
        # Update latency tracking
        self._latency_samples.append(latency_ms)
        if len(self._latency_samples) > self._adaptive_config['sample_size']:
            self._latency_samples = self._latency_samples[-self._adaptive_config['sample_size']:]
        
        self._metrics.avg_read_latency_ms = sum(self._latency_samples) / len(self._latency_samples)
        
        logger.debug(f"Recorded read operation: {operation_type}, "
                    f"latency: {latency_ms:.1f}ms, primary: {read_from_primary}")
    
    def get_performance_recommendations(self) -> List[str]:
        """Get performance optimization recommendations.
        
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        # Error rate analysis
        if self._metrics.total_reads > 0:
            error_rate = self._metrics.read_errors / self._metrics.total_reads
            if error_rate > self._adaptive_config['error_rate_threshold']:
                recommendations.append(
                    f"High error rate ({error_rate:.2%}). Consider using PRIMARY read preference "
                    "for better reliability."
                )
        
        # Latency analysis
        if self._metrics.avg_read_latency_ms > self._adaptive_config['primary_latency_threshold_ms']:
            recommendations.append(
                f"High average latency ({self._metrics.avg_read_latency_ms:.1f}ms). "
                "Consider using NEAREST read preference or adding more secondaries."
            )
        
        # Staleness analysis
        if self._metrics.total_reads > 0:
            staleness_rate = self._metrics.stale_reads / self._metrics.total_reads
            if staleness_rate > 0.1:  # 10% threshold
                recommendations.append(
                    f"High staleness rate ({staleness_rate:.2%}). "
                    "Consider reducing maxStalenessSeconds or using PRIMARY_PREFERRED."
                )
        
        # Load distribution analysis
        if self._metrics.total_reads > 0:
            primary_ratio = self._metrics.primary_reads / self._metrics.total_reads
            if primary_ratio > 0.8:  # 80% threshold
                recommendations.append(
                    "Most reads are hitting primary. Consider using SECONDARY_PREFERRED "
                    "for read-heavy workloads to distribute load."
                )
            elif primary_ratio < 0.2:  # 20% threshold
                recommendations.append(
                    "Most reads are hitting secondaries. Ensure this aligns with "
                    "your consistency requirements."
                )
        
        return recommendations
    
    def create_geographic_configuration(self, regions: List[str],
                                      preferred_region: str = None) -> ReadConfiguration:
        """Create geographically optimized read configuration.
        
        Args:
            regions: List of available regions
            preferred_region: Preferred region for reads
            
        Returns:
            Geographic read configuration
        """
        tag_sets = []
        
        # Prefer specified region
        if preferred_region and preferred_region in regions:
            tag_sets.append({"region": preferred_region})
        
        # Add other regions as fallbacks
        for region in regions:
            if region != preferred_region:
                tag_sets.append({"region": region})
        
        # Add empty tag set as final fallback
        tag_sets.append({})
        
        config = ReadConfiguration(
            preference=ReadPreferenceStrategy.NEAREST,
            tag_sets=tag_sets,
            consistency_level=ReadConsistencyLevel.LOCAL,
            max_staleness_seconds=30  # Allow some staleness for geo-distribution
        )
        
        logger.info(f"Created geographic configuration for regions: {regions}")
        return config
    
    def get_metrics(self) -> ReadMetrics:
        """Get current read metrics.
        
        Returns:
            Current read operation metrics
        """
        return self._metrics
    
    def reset_metrics(self) -> None:
        """Reset all metrics counters."""
        self._metrics = ReadMetrics()
        self._latency_samples.clear()
        logger.info("Read preference metrics reset")
    
    def _should_use_adaptive(self) -> bool:
        """Determine if adaptive strategy should be used."""
        # Use adaptive strategy if we have enough samples
        return len(self._latency_samples) >= 10
    
    def _get_adaptive_strategy(self) -> ReadPreferenceStrategy:
        """Get adaptive read preference strategy based on current metrics."""
        primary_threshold = self._adaptive_config['primary_latency_threshold_ms']
        secondary_threshold = self._adaptive_config['secondary_latency_threshold_ms']
        
        # Calculate recent latency trend
        recent_samples = self._latency_samples[-10:] if len(self._latency_samples) >= 10 else self._latency_samples
        avg_recent_latency = sum(recent_samples) / len(recent_samples) if recent_samples else 0
        
        # Determine strategy based on latency and error rate
        error_rate = self._metrics.read_errors / max(self._metrics.total_reads, 1)
        
        if error_rate > self._adaptive_config['error_rate_threshold']:
            # High error rate, prefer primary
            return ReadPreferenceStrategy.PRIMARY
        elif avg_recent_latency > primary_threshold:
            # High latency, try secondaries
            return ReadPreferenceStrategy.SECONDARY_PREFERRED
        elif avg_recent_latency < secondary_threshold:
            # Low latency, can use nearest
            return ReadPreferenceStrategy.NEAREST
        else:
            # Moderate latency, prefer primary but allow secondaries
            return ReadPreferenceStrategy.PRIMARY_PREFERRED
    
    def _create_read_preference(self, strategy: ReadPreferenceStrategy,
                              max_staleness: Optional[int] = None) -> ReadPreference:
        """Create PyMongo read preference object."""
        kwargs = {}
        
        if max_staleness:
            kwargs['max_staleness_seconds'] = max_staleness
        
        if self._current_config.tag_sets:
            kwargs['tag_sets'] = self._current_config.tag_sets
        
        if self._current_config.hedge_enabled:
            kwargs['hedge'] = {"enabled": True}
        
        strategy_map = {
            ReadPreferenceStrategy.PRIMARY: Primary(**kwargs),
            ReadPreferenceStrategy.SECONDARY: Secondary(**kwargs),
            ReadPreferenceStrategy.NEAREST: Nearest(**kwargs),
            ReadPreferenceStrategy.PRIMARY_PREFERRED: PrimaryPreferred(**kwargs),
            ReadPreferenceStrategy.SECONDARY_PREFERRED: SecondaryPreferred(**kwargs)
        }
        
        return strategy_map.get(strategy, PrimaryPreferred(**kwargs))

# Global optimizer instance
_default_optimizer: Optional[ReadPreferenceOptimizer] = None

def get_read_preference_optimizer() -> ReadPreferenceOptimizer:
    """Get or create default read preference optimizer."""
    global _default_optimizer
    if _default_optimizer is None:
        _default_optimizer = ReadPreferenceOptimizer()
    return _default_optimizer

__all__ = [
    'ReadPreferenceOptimizer', 'ReadConfiguration', 'ReadMetrics',
    'ReadPreferenceStrategy', 'ReadConsistencyLevel', 'get_read_preference_optimizer'
]