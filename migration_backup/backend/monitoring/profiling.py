"""⚡ Unified Profiling Module - IA Influencer Agent Platform
========================================================

Consolidated performance profiling and capacity planning system combining:
- Performance profiling (CPU, memory, execution time)
- Capacity planning and resource forecasting
- Bottleneck detection and optimization recommendations
- System resource monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import cProfile
import pstats
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import threading
from contextlib import contextmanager
from collections import defaultdict, deque
import statistics

# Optional system monitoring dependency
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    # Create dummy psutil for when not available
    class DummyPsutil:
        @staticmethod
        def cpu_percent(interval=1):
            return 45.0
        
        @staticmethod
        def virtual_memory():
            class Memory:
                percent = 67.0
                available = 8 * 1024**3  # 8GB
                total = 16 * 1024**3     # 16GB
                used = 8 * 1024**3       # 8GB
                cached = 1 * 1024**3     # 1GB
                buffers = 0.5 * 1024**3  # 0.5GB
            return Memory()
        
        @staticmethod
        def disk_usage(path):
            class Disk:
                total = 500 * 1024**3    # 500GB
                used = 250 * 1024**3     # 250GB  
                free = 250 * 1024**3     # 250GB
            return Disk()
        
        @staticmethod
        def net_io_counters():
            class Network:
                bytes_sent = 1024**6     # 1MB
                bytes_recv = 2 * 1024**6 # 2MB
                packets_sent = 1000
                packets_recv = 2000
                errin = 0
                errout = 0
            return Network()
        
        @staticmethod
        def disk_io_counters():
            class DiskIO:
                read_bytes = 1024**7     # 10MB
                write_bytes = 1024**6    # 1MB
                read_time = 100
                write_time = 50
            return DiskIO()
            
        @staticmethod
        def cpu_count():
            return 4
            
        @staticmethod
        def cpu_freq():
            class CPUFreq:
                current = 2800
                min = 1200
                max = 3600
                def _asdict(self):
                    return {"current": self.current, "min": self.min, "max": self.max}
            return CPUFreq()
            
        @staticmethod
        def getloadavg():
            return (1.2, 1.1, 1.0)
    
    psutil = DummyPsutil()

import logging
logger = logging.getLogger(__name__)


class ProfileType(Enum):
    """Types of profiling"""
    CPU = "cpu"
    MEMORY = "memory"
    IO = "io"
    NETWORK = "network"
    CUSTOM = "custom"


class ResourceType(Enum):
    """Types of system resources"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"


@dataclass
class PerformanceProfile:
    """Performance profile result"""
    id: str
    name: str
    profile_type: ProfileType
    duration_seconds: float
    started_at: datetime
    completed_at: datetime
    stats: Dict[str, Any] = field(default_factory=dict)
    bottlenecks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    function_stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceUsage:
    """Resource usage snapshot"""
    timestamp: datetime
    resource_type: ResourceType
    current_usage: float
    max_capacity: float
    utilization_percent: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CapacityForecast:
    """Capacity planning forecast"""
    resource_type: ResourceType
    current_usage: float
    forecasted_usage: float
    forecast_period_days: int
    capacity_exhaustion_date: Optional[datetime] = None
    recommendations: List[str] = field(default_factory=list)
    confidence_score: float = 0.0


class FunctionProfiler:
    """Function-level performance profiler"""
    
    def __init__(self):
        self.profiles: Dict[str, cProfile.Profile] = {}
        self.active_profiles: Dict[str, datetime] = {}
        self.completed_profiles: List[PerformanceProfile] = []
    
    @contextmanager
    def profile_function(self, name: str):
        """Context manager for profiling functions"""
        profile_id = f"{name}_{int(time.time())}"
        profiler = cProfile.Profile()
        
        start_time = datetime.now()
        self.active_profiles[profile_id] = start_time
        
        try:
            profiler.enable()
            yield profile_id
        finally:
            profiler.disable()
            end_time = datetime.now()
            
            # Process profile results
            self._process_profile_results(profile_id, name, profiler, start_time, end_time)
            
            if profile_id in self.active_profiles:
                del self.active_profiles[profile_id]
    
    def _process_profile_results(
        self,
        profile_id: str,
        name: str,
        profiler: cProfile.Profile,
        start_time: datetime,
        end_time: datetime
    ):
        """Process profile results and extract insights"""
        
        # Create stats object
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        
        # Extract function statistics
        function_stats = {}
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            filename, line, func_name = func
            function_stats[f"{filename}:{func_name}"] = {
                "call_count": cc,
                "total_time": tt,
                "cumulative_time": ct,
                "per_call_time": tt / cc if cc > 0 else 0
            }
        
        # Identify bottlenecks (functions taking > 10% of total time)
        total_time = sum(stat["total_time"] for stat in function_stats.values())
        bottlenecks = [
            func for func, stat in function_stats.items()
            if stat["total_time"] > total_time * 0.1
        ]
        
        # Generate recommendations
        recommendations = []
        if bottlenecks:
            recommendations.append(f"Optimize {len(bottlenecks)} performance bottleneck(s)")
        if total_time > 1.0:
            recommendations.append("Consider async/await for long-running operations")
        
        # Create performance profile
        profile = PerformanceProfile(
            id=profile_id,
            name=name,
            profile_type=ProfileType.CPU,
            duration_seconds=(end_time - start_time).total_seconds(),
            started_at=start_time,
            completed_at=end_time,
            stats={
                "total_time": total_time,
                "total_calls": sum(stat["call_count"] for stat in function_stats.values()),
                "avg_call_time": total_time / len(function_stats) if function_stats else 0
            },
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            function_stats=function_stats
        )
        
        self.completed_profiles.append(profile)
        logger.info(f"Completed profiling for {name}: {len(bottlenecks)} bottlenecks found")
    
    def get_profile_results(self, profile_id: Optional[str] = None) -> List[PerformanceProfile]:
        """Get profile results"""
        if profile_id:
            return [p for p in self.completed_profiles if p.id == profile_id]
        return self.completed_profiles.copy()


class ResourceMonitor:
    """System resource monitoring"""
    
    def __init__(self):
        self.usage_history: Dict[ResourceType, deque] = {
            resource_type: deque(maxlen=1000) for resource_type in ResourceType
        }
        self.monitoring_active = False
        self.monitor_interval = 30  # seconds
    
    async def start_monitoring(self, interval: int = 30):
        """Start resource monitoring"""
        self.monitoring_active = True
        self.monitor_interval = interval
        logger.info(f"Starting resource monitoring with {interval}s interval")
        
        while self.monitoring_active:
            try:
                await self.collect_resource_usage()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                await asyncio.sleep(interval)
    
    async def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring_active = False
        logger.info("Stopped resource monitoring")
    
    async def collect_resource_usage(self):
        """Collect current resource usage"""
        timestamp = datetime.now()
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_usage = ResourceUsage(
            timestamp=timestamp,
            resource_type=ResourceType.CPU,
            current_usage=cpu_percent,
            max_capacity=100.0,
            utilization_percent=cpu_percent,
            details={
                "cpu_count": psutil.cpu_count(),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
                "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
        )
        self.usage_history[ResourceType.CPU].append(cpu_usage)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage = ResourceUsage(
            timestamp=timestamp,
            resource_type=ResourceType.MEMORY,
            current_usage=memory.used,
            max_capacity=memory.total,
            utilization_percent=memory.percent,
            details={
                "available": memory.available,
                "cached": memory.cached if hasattr(memory, 'cached') else 0,
                "buffers": memory.buffers if hasattr(memory, 'buffers') else 0
            }
        )
        self.usage_history[ResourceType.MEMORY].append(memory_usage)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        disk_usage = ResourceUsage(
            timestamp=timestamp,
            resource_type=ResourceType.DISK,
            current_usage=disk.used,
            max_capacity=disk.total,
            utilization_percent=(disk.used / disk.total) * 100,
            details={
                "free": disk.free,
                "read_bytes": disk_io.read_bytes if disk_io else 0,
                "write_bytes": disk_io.write_bytes if disk_io else 0,
                "read_time": disk_io.read_time if disk_io else 0,
                "write_time": disk_io.write_time if disk_io else 0
            }
        )
        self.usage_history[ResourceType.DISK].append(disk_usage)
        
        # Network usage
        network = psutil.net_io_counters()
        network_usage = ResourceUsage(
            timestamp=timestamp,
            resource_type=ResourceType.NETWORK,
            current_usage=network.bytes_sent + network.bytes_recv if network else 0,
            max_capacity=float('inf'),  # No fixed capacity for network
            utilization_percent=0.0,  # Cannot calculate without knowing capacity
            details={
                "bytes_sent": network.bytes_sent if network else 0,
                "bytes_recv": network.bytes_recv if network else 0,
                "packets_sent": network.packets_sent if network else 0,
                "packets_recv": network.packets_recv if network else 0,
                "errin": network.errin if network else 0,
                "errout": network.errout if network else 0
            }
        )
        self.usage_history[ResourceType.NETWORK].append(network_usage)
    
    def get_current_usage(self, resource_type: ResourceType) -> Optional[ResourceUsage]:
        """Get current resource usage"""
        history = self.usage_history.get(resource_type, deque())
        return history[-1] if history else None
    
    def get_usage_history(self, resource_type: ResourceType, hours: int = 24) -> List[ResourceUsage]:
        """Get resource usage history"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        history = self.usage_history.get(resource_type, deque())
        
        return [
            usage for usage in history
            if usage.timestamp >= cutoff_time
        ]
    
    def get_usage_statistics(self, resource_type: ResourceType, hours: int = 24) -> Dict[str, Any]:
        """Get usage statistics for a resource"""
        history = self.get_usage_history(resource_type, hours)
        
        if not history:
            return {"error": "No data available"}
        
        utilizations = [usage.utilization_percent for usage in history]
        
        return {
            "resource_type": resource_type.value,
            "period_hours": hours,
            "data_points": len(history),
            "current_utilization": utilizations[-1] if utilizations else 0,
            "avg_utilization": statistics.mean(utilizations),
            "max_utilization": max(utilizations),
            "min_utilization": min(utilizations),
            "std_deviation": statistics.stdev(utilizations) if len(utilizations) > 1 else 0,
            "trend": self._calculate_trend(utilizations)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        change_percent = ((second_avg - first_avg) / first_avg) * 100 if first_avg > 0 else 0
        
        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"


class CapacityPlanner:
    """Capacity planning and forecasting"""
    
    def __init__(self, resource_monitor: ResourceMonitor):
        self.resource_monitor = resource_monitor
        self.forecasts: Dict[ResourceType, CapacityForecast] = {}
    
    def generate_capacity_forecast(
        self,
        resource_type: ResourceType,
        forecast_days: int = 30
    ) -> CapacityForecast:
        """Generate capacity forecast for a resource"""
        
        # Get historical usage data
        history = self.resource_monitor.get_usage_history(resource_type, hours=24*7)  # 7 days
        
        if len(history) < 10:
            return CapacityForecast(
                resource_type=resource_type,
                current_usage=0,
                forecasted_usage=0,
                forecast_period_days=forecast_days,
                recommendations=["Insufficient data for forecasting"],
                confidence_score=0.0
            )
        
        # Calculate trend
        utilizations = [usage.utilization_percent for usage in history]
        current_usage = utilizations[-1]
        
        # Simple linear regression for trend
        growth_rate = self._calculate_growth_rate(utilizations)
        forecasted_usage = current_usage + (growth_rate * forecast_days)
        
        # Calculate when capacity might be exhausted
        capacity_exhaustion_date = None
        if growth_rate > 0 and current_usage < 100:
            days_to_exhaustion = (100 - current_usage) / growth_rate
            if days_to_exhaustion > 0:
                capacity_exhaustion_date = datetime.now() + timedelta(days=days_to_exhaustion)
        
        # Generate recommendations
        recommendations = self._generate_capacity_recommendations(
            resource_type, current_usage, forecasted_usage, growth_rate
        )
        
        # Calculate confidence score
        confidence_score = min(len(history) / 100, 1.0)  # More data = higher confidence
        
        forecast = CapacityForecast(
            resource_type=resource_type,
            current_usage=current_usage,
            forecasted_usage=forecasted_usage,
            forecast_period_days=forecast_days,
            capacity_exhaustion_date=capacity_exhaustion_date,
            recommendations=recommendations,
            confidence_score=confidence_score
        )
        
        self.forecasts[resource_type] = forecast
        return forecast
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate daily growth rate"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend
        first_value = statistics.mean(values[:len(values)//3])
        last_value = statistics.mean(values[-len(values)//3:])
        
        # Growth rate per day (assuming values are collected daily)
        growth_rate = (last_value - first_value) / (len(values) / 24)  # Assuming hourly data
        
        return growth_rate
    
    def _generate_capacity_recommendations(
        self,
        resource_type: ResourceType,
        current_usage: float,
        forecasted_usage: float,
        growth_rate: float
    ) -> List[str]:
        """Generate capacity planning recommendations"""
        recommendations = []
        
        if current_usage > 80:
            recommendations.append(f"{resource_type.value.upper()} usage is high ({current_usage:.1f}%)")
        
        if forecasted_usage > 90:
            recommendations.append(f"Predicted {resource_type.value} exhaustion in forecast period")
        
        if growth_rate > 2:  # Growing more than 2% per day
            recommendations.append(f"{resource_type.value.upper()} usage growing rapidly ({growth_rate:.1f}%/day)")
        
        # Resource-specific recommendations
        if resource_type == ResourceType.CPU:
            if current_usage > 70:
                recommendations.append("Consider CPU scaling or optimization")
            if growth_rate > 1:
                recommendations.append("Monitor for CPU-intensive processes")
        
        elif resource_type == ResourceType.MEMORY:
            if current_usage > 75:
                recommendations.append("Consider memory scaling or optimization")
            if growth_rate > 1:
                recommendations.append("Check for memory leaks")
        
        elif resource_type == ResourceType.DISK:
            if current_usage > 80:
                recommendations.append("Consider disk cleanup or expansion")
            if growth_rate > 1:
                recommendations.append("Implement log rotation and data archiving")
        
        if not recommendations:
            recommendations.append(f"{resource_type.value.upper()} capacity is adequate")
        
        return recommendations
    
    def get_all_forecasts(self, forecast_days: int = 30) -> Dict[ResourceType, CapacityForecast]:
        """Get forecasts for all resource types"""
        forecasts = {}
        for resource_type in [ResourceType.CPU, ResourceType.MEMORY, ResourceType.DISK]:
            forecasts[resource_type] = self.generate_capacity_forecast(resource_type, forecast_days)
        return forecasts


class UnifiedProfilingManager:
    """
    Unified profiling system that consolidates all performance monitoring functionality
    """
    
    def __init__(self):
        self.function_profiler = FunctionProfiler()
        self.resource_monitor = ResourceMonitor()
        self.capacity_planner = CapacityPlanner(self.resource_monitor)
        
        # State tracking
        self.active_monitoring = False
        self.profiling_enabled = True
    
    async def start_monitoring(self, interval: int = 30):
        """Start all monitoring components"""
        self.active_monitoring = True
        logger.info("Starting unified profiling and monitoring")
        
        # Start resource monitoring
        await self.resource_monitor.start_monitoring(interval)
    
    async def stop_monitoring(self):
        """Stop all monitoring components"""
        self.active_monitoring = False
        await self.resource_monitor.stop_monitoring()
        logger.info("Stopped unified profiling and monitoring")
    
    def profile_function(self, name: str):
        """Profile a function"""
        if not self.profiling_enabled:
            return self.function_profiler.profile_function(f"disabled_{name}")
        
        return self.function_profiler.profile_function(name)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        
        # Get resource statistics
        resource_stats = {}
        for resource_type in ResourceType:
            if resource_type in [ResourceType.DATABASE, ResourceType.CACHE]:
                continue  # Skip non-system resources
            
            stats = self.resource_monitor.get_usage_statistics(resource_type)
            resource_stats[resource_type.value] = stats
        
        # Get profiling statistics
        profiles = self.function_profiler.get_profile_results()
        profiling_stats = {
            "total_profiles": len(profiles),
            "total_bottlenecks": sum(len(p.bottlenecks) for p in profiles),
            "avg_execution_time": statistics.mean([p.duration_seconds for p in profiles]) if profiles else 0,
            "recent_profiles": [
                {
                    "name": p.name,
                    "duration": p.duration_seconds,
                    "bottlenecks": len(p.bottlenecks)
                }
                for p in profiles[-5:]  # Last 5 profiles
            ]
        }
        
        # Get capacity forecasts
        forecasts = self.capacity_planner.get_all_forecasts()
        capacity_summary = {
            resource_type.value: {
                "current_usage": forecast.current_usage,
                "forecasted_usage": forecast.forecasted_usage,
                "exhaustion_date": forecast.capacity_exhaustion_date.isoformat() 
                    if forecast.capacity_exhaustion_date else None,
                "recommendation_count": len(forecast.recommendations)
            }
            for resource_type, forecast in forecasts.items()
        }
        
        return {
            "monitoring_active": self.active_monitoring,
            "profiling_enabled": self.profiling_enabled,
            "resource_statistics": resource_stats,
            "profiling_statistics": profiling_stats,
            "capacity_forecasts": capacity_summary,
            "summary_generated_at": datetime.now().isoformat()
        }
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get system optimization recommendations"""
        recommendations = []
        
        # From resource monitoring
        for resource_type in [ResourceType.CPU, ResourceType.MEMORY, ResourceType.DISK]:
            stats = self.resource_monitor.get_usage_statistics(resource_type)
            if stats.get("avg_utilization", 0) > 80:
                recommendations.append(f"High {resource_type.value} usage detected - consider optimization")
        
        # From capacity planning
        forecasts = self.capacity_planner.get_all_forecasts()
        for forecast in forecasts.values():
            recommendations.extend(forecast.recommendations)
        
        # From profiling
        profiles = self.function_profiler.get_profile_results()
        for profile in profiles[-5:]:  # Recent profiles
            recommendations.extend(profile.recommendations)
        
        # Remove duplicates
        return list(set(recommendations))


# Global profiling manager instance
profiling_manager = UnifiedProfilingManager()


# Convenience functions for external use
async def start_performance_monitoring(interval: int = 30):
    """Start performance monitoring"""
    await profiling_manager.start_monitoring(interval)


async def stop_performance_monitoring():
    """Stop performance monitoring"""
    await profiling_manager.stop_monitoring()


def profile_function(name: str):
    """Profile a function"""
    return profiling_manager.profile_function(name)


def get_performance_summary() -> Dict[str, Any]:
    """Get performance summary"""
    return profiling_manager.get_performance_summary()


def get_optimization_recommendations() -> List[str]:
    """Get optimization recommendations"""
    return profiling_manager.get_optimization_recommendations()


def get_capacity_forecast(resource_type: ResourceType, days: int = 30) -> CapacityForecast:
    """Get capacity forecast"""
    return profiling_manager.capacity_planner.generate_capacity_forecast(resource_type, days)