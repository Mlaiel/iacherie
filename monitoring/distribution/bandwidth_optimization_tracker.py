"""
Bandwidth Optimization Tracker - Distribution Module
==================================================

Advanced bandwidth optimization tracking system for monitoring and optimizing
network bandwidth usage across content distribution platforms.

Features:
- Real-time bandwidth usage monitoring
- Intelligent traffic shaping and prioritization
- Bandwidth cost optimization
- Quality adaptation based on network conditions
- Peak traffic management
- Compression and encoding optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class TrafficType(Enum):
    """Types of network traffic"""
    VIDEO_STREAMING = "video_streaming"
    AUDIO_STREAMING = "audio_streaming"
    IMAGE_DELIVERY = "image_delivery"
    METADATA_SYNC = "metadata_sync"
    API_REQUESTS = "api_requests"
    LIVE_STREAMING = "live_streaming"
    FILE_UPLOAD = "file_upload"
    ANALYTICS_DATA = "analytics_data"

class QualityLevel(Enum):
    """Content quality levels for adaptive streaming"""
    LOW = "low"          # 480p, 64kbps audio
    MEDIUM = "medium"    # 720p, 128kbps audio
    HIGH = "high"        # 1080p, 256kbps audio
    ULTRA = "ultra"      # 4K, 320kbps audio

class OptimizationStrategy(Enum):
    """Bandwidth optimization strategies"""
    COMPRESSION = "compression"
    QUALITY_ADAPTATION = "quality_adaptation"
    TRAFFIC_SHAPING = "traffic_shaping"
    CACHING = "caching"
    CDN_ROUTING = "cdn_routing"
    PEER_TO_PEER = "peer_to_peer"

@dataclass
class BandwidthUsage:
    """Real-time bandwidth usage measurement"""
    measurement_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    traffic_type: TrafficType = TrafficType.VIDEO_STREAMING
    platform: str = "youtube"
    region: str = "us_east"
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Bandwidth metrics
    upload_mbps: float = 0.0
    download_mbps: float = 0.0
    total_mbps: float = 0.0
    
    # Quality metrics
    quality_level: QualityLevel = QualityLevel.MEDIUM
    compression_ratio: float = 0.0
    latency_ms: float = 0.0
    packet_loss_rate: float = 0.0
    
    # Cost metrics
    cost_per_gb: float = 0.0
    estimated_monthly_cost: float = 0.0
    
    # User metrics
    concurrent_users: int = 0
    quality_switches: int = 0

@dataclass
class OptimizationRule:
    """Bandwidth optimization rule"""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    strategy: OptimizationStrategy = OptimizationStrategy.COMPRESSION
    traffic_type: TrafficType = TrafficType.VIDEO_STREAMING
    
    # Trigger conditions
    bandwidth_threshold_mbps: float = 100.0
    latency_threshold_ms: float = 200.0
    cost_threshold_per_gb: float = 0.10
    
    # Actions
    target_quality: QualityLevel = QualityLevel.MEDIUM
    compression_level: float = 0.7
    cache_duration_hours: int = 24
    
    # Metadata
    enabled: bool = True
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class TrafficPattern:
    """Detected traffic pattern"""
    pattern_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pattern_type: str = ""  # "peak_hours", "seasonal", "event_driven"
    description: str = ""
    
    # Pattern characteristics
    peak_hours: List[int] = field(default_factory=list)
    peak_days: List[str] = field(default_factory=list)
    average_bandwidth_mbps: float = 0.0
    peak_bandwidth_mbps: float = 0.0
    
    # Prediction metrics
    confidence_score: float = 0.0
    next_peak_prediction: Optional[datetime] = None
    suggested_optimizations: List[str] = field(default_factory=list)

@dataclass
class QualityAdaptation:
    """Quality adaptation event"""
    adaptation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_session_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Adaptation details
    old_quality: QualityLevel = QualityLevel.MEDIUM
    new_quality: QualityLevel = QualityLevel.LOW
    reason: str = "bandwidth_limitation"
    
    # Network conditions
    available_bandwidth_mbps: float = 0.0
    latency_ms: float = 0.0
    packet_loss_rate: float = 0.0
    
    # Impact
    bandwidth_saved_mbps: float = 0.0
    user_satisfaction_impact: float = 0.0  # -1 to 1 scale

class BandwidthOptimizationTracker:
    """Main bandwidth optimization tracking system"""
    
    def __init__(self):
        self.bandwidth_usage: List[BandwidthUsage] = []
        self.optimization_rules: List[OptimizationRule] = []
        self.traffic_patterns: List[TrafficPattern] = []
        self.quality_adaptations: List[QualityAdaptation] = []
        
        # Configuration
        self.monitoring_active = False
        self.optimization_active = True
        self.quality_profiles = self._initialize_quality_profiles()
        self.cost_thresholds = self._initialize_cost_thresholds()
        
        # Real-time tracking
        self.current_bandwidth_limit = 1000.0  # Mbps
        self.peak_usage_threshold = 0.8  # 80% of limit
        
    def _initialize_quality_profiles(self) -> Dict[QualityLevel, Dict[str, Any]]:
        """Initialize quality profiles for different content types"""
        return {
            QualityLevel.LOW: {
                "video_bitrate_kbps": 500,
                "audio_bitrate_kbps": 64,
                "resolution": "480p",
                "fps": 30,
                "bandwidth_requirement_mbps": 0.8
            },
            QualityLevel.MEDIUM: {
                "video_bitrate_kbps": 2500,
                "audio_bitrate_kbps": 128,
                "resolution": "720p",
                "fps": 30,
                "bandwidth_requirement_mbps": 3.5
            },
            QualityLevel.HIGH: {
                "video_bitrate_kbps": 5000,
                "audio_bitrate_kbps": 256,
                "resolution": "1080p",
                "fps": 60,
                "bandwidth_requirement_mbps": 7.0
            },
            QualityLevel.ULTRA: {
                "video_bitrate_kbps": 15000,
                "audio_bitrate_kbps": 320,
                "resolution": "4K",
                "fps": 60,
                "bandwidth_requirement_mbps": 20.0
            }
        }
        
    def _initialize_cost_thresholds(self) -> Dict[str, float]:
        """Initialize cost thresholds for different optimization triggers"""
        return {
            "low_cost_per_gb": 0.05,
            "medium_cost_per_gb": 0.08,
            "high_cost_per_gb": 0.12,
            "critical_cost_per_gb": 0.15,
            "monthly_budget_usd": 5000.0
        }
        
    async def start_monitoring(self):
        """Start bandwidth optimization monitoring"""
        self.monitoring_active = True
        
        # Start monitoring tasks
        monitoring_tasks = [
            self._monitor_bandwidth_usage(),
            self._detect_traffic_patterns(),
            self._apply_optimization_rules(),
            self._adaptive_quality_management(),
            self._cost_optimization()
        ]
        
        await asyncio.gather(*monitoring_tasks)
        
    async def stop_monitoring(self):
        """Stop bandwidth optimization monitoring"""
        self.monitoring_active = False
        logger.info("Bandwidth optimization monitoring stopped")
        
    async def _monitor_bandwidth_usage(self):
        """Monitor real-time bandwidth usage"""
        while self.monitoring_active:
            try:
                # Monitor different traffic types
                for traffic_type in TrafficType:
                    usage = await self._measure_bandwidth_usage(traffic_type)
                    self.bandwidth_usage.append(usage)
                    
                    # Check for immediate optimization needs
                    if usage.total_mbps > self.current_bandwidth_limit * self.peak_usage_threshold:
                        await self._handle_bandwidth_congestion(usage)
                        
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring bandwidth usage: {e}")
                await asyncio.sleep(30)
                
    async def _measure_bandwidth_usage(self, traffic_type: TrafficType) -> BandwidthUsage:
        """Measure current bandwidth usage for traffic type (simulated)"""
        import random
        
        # Simulate realistic bandwidth patterns
        base_usage = {
            TrafficType.VIDEO_STREAMING: 50.0,
            TrafficType.AUDIO_STREAMING: 5.0,
            TrafficType.IMAGE_DELIVERY: 2.0,
            TrafficType.METADATA_SYNC: 0.5,
            TrafficType.API_REQUESTS: 0.2,
            TrafficType.LIVE_STREAMING: 100.0,
            TrafficType.FILE_UPLOAD: 20.0,
            TrafficType.ANALYTICS_DATA: 1.0
        }
        
        base_mbps = base_usage.get(traffic_type, 10.0)
        
        # Add time-based variations
        current_hour = datetime.now().hour
        peak_multiplier = 1.5 if 18 <= current_hour <= 23 else 1.0
        
        # Add randomness
        variance = random.uniform(0.7, 1.3)
        
        total_mbps = base_mbps * peak_multiplier * variance
        upload_mbps = total_mbps * 0.2  # Upload is typically 20% of total
        download_mbps = total_mbps * 0.8
        
        # Calculate derived metrics
        compression_ratio = random.uniform(0.3, 0.8)
        latency_ms = random.uniform(20, 150)
        packet_loss_rate = random.uniform(0.001, 0.05)
        concurrent_users = int(total_mbps / 5)  # Rough estimate
        
        return BandwidthUsage(
            traffic_type=traffic_type,
            platform="youtube",  # Default platform
            region="us_east",
            upload_mbps=upload_mbps,
            download_mbps=download_mbps,
            total_mbps=total_mbps,
            quality_level=QualityLevel.MEDIUM,
            compression_ratio=compression_ratio,
            latency_ms=latency_ms,
            packet_loss_rate=packet_loss_rate,
            cost_per_gb=0.08,
            estimated_monthly_cost=total_mbps * 24 * 30 * 3.6 * 0.08,  # GB/month * cost
            concurrent_users=concurrent_users,
            quality_switches=random.randint(0, 5)
        )
        
    async def _handle_bandwidth_congestion(self, usage: BandwidthUsage):
        """Handle bandwidth congestion situations"""
        logger.warning(f"Bandwidth congestion detected: {usage.total_mbps:.1f} Mbps")
        
        # Apply immediate optimizations
        optimizations_applied = []
        
        # 1. Reduce quality for high-bandwidth traffic
        if usage.traffic_type in [TrafficType.VIDEO_STREAMING, TrafficType.LIVE_STREAMING]:
            await self._apply_quality_reduction(usage)
            optimizations_applied.append("quality_reduction")
            
        # 2. Increase compression
        if usage.compression_ratio < 0.6:
            await self._increase_compression(usage)
            optimizations_applied.append("increased_compression")
            
        # 3. Activate traffic shaping
        await self._apply_traffic_shaping(usage)
        optimizations_applied.append("traffic_shaping")
        
        logger.info(f"Applied optimizations: {optimizations_applied}")
        
    async def _apply_quality_reduction(self, usage: BandwidthUsage):
        """Apply quality reduction to reduce bandwidth usage"""
        current_quality = usage.quality_level
        
        # Determine target quality based on current bandwidth pressure
        bandwidth_pressure = usage.total_mbps / self.current_bandwidth_limit
        
        if bandwidth_pressure > 0.9:
            target_quality = QualityLevel.LOW
        elif bandwidth_pressure > 0.8:
            target_quality = QualityLevel.MEDIUM
        else:
            target_quality = current_quality
            
        if target_quality != current_quality:
            adaptation = QualityAdaptation(
                user_session_id=f"session_{usage.measurement_id}",
                old_quality=current_quality,
                new_quality=target_quality,
                reason="bandwidth_congestion",
                available_bandwidth_mbps=usage.total_mbps,
                latency_ms=usage.latency_ms,
                packet_loss_rate=usage.packet_loss_rate,
                bandwidth_saved_mbps=self._calculate_bandwidth_savings(current_quality, target_quality),
                user_satisfaction_impact=-0.3  # Negative impact from quality reduction
            )
            
            self.quality_adaptations.append(adaptation)
            logger.info(f"Quality reduced from {current_quality.value} to {target_quality.value}")
            
    def _calculate_bandwidth_savings(self, old_quality: QualityLevel, new_quality: QualityLevel) -> float:
        """Calculate bandwidth savings from quality change"""
        old_profile = self.quality_profiles[old_quality]
        new_profile = self.quality_profiles[new_quality]
        
        old_bandwidth = old_profile["bandwidth_requirement_mbps"]
        new_bandwidth = new_profile["bandwidth_requirement_mbps"]
        
        return max(0, old_bandwidth - new_bandwidth)
        
    async def _increase_compression(self, usage: BandwidthUsage):
        """Increase compression to reduce bandwidth usage"""
        current_compression = usage.compression_ratio
        target_compression = min(0.9, current_compression + 0.2)
        
        logger.info(f"Increasing compression from {current_compression:.1%} to {target_compression:.1%}")
        
    async def _apply_traffic_shaping(self, usage: BandwidthUsage):
        """Apply traffic shaping rules"""
        # Prioritize different traffic types
        priority_order = [
            TrafficType.LIVE_STREAMING,    # Highest priority
            TrafficType.VIDEO_STREAMING,
            TrafficType.AUDIO_STREAMING,
            TrafficType.API_REQUESTS,
            TrafficType.IMAGE_DELIVERY,
            TrafficType.METADATA_SYNC,
            TrafficType.ANALYTICS_DATA,
            TrafficType.FILE_UPLOAD        # Lowest priority
        ]
        
        traffic_priority = priority_order.index(usage.traffic_type) if usage.traffic_type in priority_order else len(priority_order)
        
        logger.info(f"Applied traffic shaping priority {traffic_priority} for {usage.traffic_type.value}")
        
    async def _detect_traffic_patterns(self):
        """Detect and analyze traffic patterns"""
        while self.monitoring_active:
            try:
                if len(self.bandwidth_usage) >= 100:  # Need minimum data
                    await self._analyze_peak_hour_patterns()
                    await self._analyze_seasonal_patterns()
                    await self._predict_future_usage()
                    
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
            except Exception as e:
                logger.error(f"Error detecting traffic patterns: {e}")
                await asyncio.sleep(300)
                
    async def _analyze_peak_hour_patterns(self):
        """Analyze peak hour traffic patterns"""
        # Group usage by hour of day
        hourly_usage = defaultdict(list)
        
        for usage in self.bandwidth_usage[-1000:]:  # Last 1000 measurements
            hour = usage.timestamp.hour
            hourly_usage[hour].append(usage.total_mbps)
            
        # Find peak hours
        hourly_averages = {}
        for hour, usage_list in hourly_usage.items():
            if len(usage_list) >= 5:  # Minimum samples
                hourly_averages[hour] = statistics.mean(usage_list)
                
        if hourly_averages:
            overall_average = statistics.mean(hourly_averages.values())
            peak_hours = [hour for hour, avg in hourly_averages.items() 
                         if avg > overall_average * 1.5]
            
            if peak_hours:
                pattern = TrafficPattern(
                    pattern_type="peak_hours",
                    description=f"Peak traffic hours: {peak_hours}",
                    peak_hours=peak_hours,
                    average_bandwidth_mbps=overall_average,
                    peak_bandwidth_mbps=max(hourly_averages.values()),
                    confidence_score=0.8,
                    suggested_optimizations=[
                        "pre_cache_content_before_peak",
                        "scale_bandwidth_capacity",
                        "implement_quality_adaptation"
                    ]
                )
                
                # Check if pattern already exists
                existing = any(p.pattern_type == "peak_hours" for p in self.traffic_patterns)
                if not existing:
                    self.traffic_patterns.append(pattern)
                    logger.info(f"Peak hour pattern detected: {peak_hours}")
                    
    async def _analyze_seasonal_patterns(self):
        """Analyze seasonal traffic patterns"""
        # Group usage by day of week
        daily_usage = defaultdict(list)
        
        for usage in self.bandwidth_usage[-5000:]:  # Last 5000 measurements
            day = usage.timestamp.strftime("%A")
            daily_usage[day].append(usage.total_mbps)
            
        # Find peak days
        daily_averages = {}
        for day, usage_list in daily_usage.items():
            if len(usage_list) >= 10:
                daily_averages[day] = statistics.mean(usage_list)
                
        if daily_averages:
            overall_average = statistics.mean(daily_averages.values())
            peak_days = [day for day, avg in daily_averages.items() 
                        if avg > overall_average * 1.3]
            
            if peak_days:
                pattern = TrafficPattern(
                    pattern_type="seasonal",
                    description=f"Peak traffic days: {peak_days}",
                    peak_days=peak_days,
                    average_bandwidth_mbps=overall_average,
                    peak_bandwidth_mbps=max(daily_averages.values()),
                    confidence_score=0.7,
                    suggested_optimizations=[
                        "weekend_capacity_scaling",
                        "predictive_caching",
                        "load_balancing_optimization"
                    ]
                )
                
                existing = any(p.pattern_type == "seasonal" for p in self.traffic_patterns)
                if not existing:
                    self.traffic_patterns.append(pattern)
                    
    async def _predict_future_usage(self):
        """Predict future bandwidth usage"""
        if len(self.bandwidth_usage) < 50:
            return
            
        # Simple trend analysis
        recent_usage = [u.total_mbps for u in self.bandwidth_usage[-50:]]
        
        if len(recent_usage) >= 10:
            # Calculate trend
            x = list(range(len(recent_usage)))
            
            # Simple linear regression
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(recent_usage)
            sum_xy = sum(xi * yi for xi, yi in zip(x, recent_usage))
            sum_x2 = sum(xi * xi for xi in x)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # Predict next peak (assuming 24-hour cycle)
            hours_ahead = 24
            predicted_usage = recent_usage[-1] + slope * hours_ahead
            
            if predicted_usage > self.current_bandwidth_limit * 0.9:
                next_peak = datetime.now() + timedelta(hours=hours_ahead)
                
                pattern = TrafficPattern(
                    pattern_type="predicted_peak",
                    description=f"Predicted peak usage: {predicted_usage:.1f} Mbps",
                    average_bandwidth_mbps=statistics.mean(recent_usage),
                    peak_bandwidth_mbps=predicted_usage,
                    confidence_score=0.6,
                    next_peak_prediction=next_peak,
                    suggested_optimizations=[
                        "proactive_capacity_scaling",
                        "content_pre_positioning",
                        "quality_pre_optimization"
                    ]
                )
                
                self.traffic_patterns.append(pattern)
                logger.warning(f"Predicted bandwidth peak: {predicted_usage:.1f} Mbps at {next_peak}")
                
    async def _apply_optimization_rules(self):
        """Apply bandwidth optimization rules"""
        while self.monitoring_active:
            try:
                if not self.optimization_active:
                    await asyncio.sleep(60)
                    continue
                    
                # Check each optimization rule
                for rule in self.optimization_rules:
                    if rule.enabled:
                        await self._evaluate_optimization_rule(rule)
                        
                await asyncio.sleep(30)  # Check rules every 30 seconds
                
            except Exception as e:
                logger.error(f"Error applying optimization rules: {e}")
                await asyncio.sleep(60)
                
    async def _evaluate_optimization_rule(self, rule: OptimizationRule):
        """Evaluate and apply optimization rule if conditions are met"""
        # Get recent usage for rule's traffic type
        relevant_usage = [
            u for u in self.bandwidth_usage[-10:]
            if u.traffic_type == rule.traffic_type
        ]
        
        if not relevant_usage:
            return
            
        latest_usage = relevant_usage[-1]
        
        # Check trigger conditions
        should_trigger = False
        
        if latest_usage.total_mbps > rule.bandwidth_threshold_mbps:
            should_trigger = True
        if latest_usage.latency_ms > rule.latency_threshold_ms:
            should_trigger = True
        if latest_usage.cost_per_gb > rule.cost_threshold_per_gb:
            should_trigger = True
            
        if should_trigger:
            await self._execute_optimization_action(rule, latest_usage)
            
    async def _execute_optimization_action(self, rule: OptimizationRule, usage: BandwidthUsage):
        """Execute optimization action based on rule"""
        logger.info(f"Executing optimization rule: {rule.name}")
        
        if rule.strategy == OptimizationStrategy.COMPRESSION:
            await self._apply_compression_optimization(rule, usage)
        elif rule.strategy == OptimizationStrategy.QUALITY_ADAPTATION:
            await self._apply_quality_optimization(rule, usage)
        elif rule.strategy == OptimizationStrategy.TRAFFIC_SHAPING:
            await self._apply_traffic_optimization(rule, usage)
        elif rule.strategy == OptimizationStrategy.CACHING:
            await self._apply_caching_optimization(rule, usage)
            
    async def _apply_compression_optimization(self, rule: OptimizationRule, usage: BandwidthUsage):
        """Apply compression optimization"""
        target_compression = rule.compression_level
        current_compression = usage.compression_ratio
        
        if target_compression > current_compression:
            logger.info(f"Increasing compression to {target_compression:.1%}")
            
    async def _apply_quality_optimization(self, rule: OptimizationRule, usage: BandwidthUsage):
        """Apply quality optimization"""
        target_quality = rule.target_quality
        current_quality = usage.quality_level
        
        if target_quality != current_quality:
            adaptation = QualityAdaptation(
                user_session_id=f"rule_{rule.rule_id}",
                old_quality=current_quality,
                new_quality=target_quality,
                reason=f"optimization_rule_{rule.name}",
                available_bandwidth_mbps=usage.total_mbps,
                latency_ms=usage.latency_ms,
                bandwidth_saved_mbps=self._calculate_bandwidth_savings(current_quality, target_quality)
            )
            
            self.quality_adaptations.append(adaptation)
            
    async def _apply_traffic_optimization(self, rule: OptimizationRule, usage: BandwidthUsage):
        """Apply traffic shaping optimization"""
        logger.info(f"Applying traffic shaping for {usage.traffic_type.value}")
        
    async def _apply_caching_optimization(self, rule: OptimizationRule, usage: BandwidthUsage):
        """Apply caching optimization"""
        cache_duration = rule.cache_duration_hours
        logger.info(f"Optimizing cache duration to {cache_duration} hours")
        
    async def _adaptive_quality_management(self):
        """Manage adaptive quality streaming"""
        while self.monitoring_active:
            try:
                await self._monitor_user_quality_experience()
                await self._optimize_quality_ladder()
                await self._balance_quality_vs_bandwidth()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in adaptive quality management: {e}")
                await asyncio.sleep(120)
                
    async def _monitor_user_quality_experience(self):
        """Monitor user quality experience metrics"""
        if not self.quality_adaptations:
            return
            
        # Analyze recent quality adaptations
        recent_adaptations = [
            a for a in self.quality_adaptations
            if a.timestamp > datetime.now() - timedelta(hours=1)
        ]
        
        if recent_adaptations:
            avg_satisfaction_impact = statistics.mean(
                a.user_satisfaction_impact for a in recent_adaptations
            )
            
            if avg_satisfaction_impact < -0.5:  # Poor user experience
                logger.warning(f"Poor user quality experience detected: {avg_satisfaction_impact:.2f}")
                
    async def _optimize_quality_ladder(self):
        """Optimize quality ladder based on usage patterns"""
        # Analyze quality distribution
        quality_usage = defaultdict(int)
        
        for usage in self.bandwidth_usage[-100:]:
            quality_usage[usage.quality_level] += 1
            
        most_used_quality = max(quality_usage.items(), key=lambda x: x[1])[0] if quality_usage else QualityLevel.MEDIUM
        
        logger.debug(f"Most used quality level: {most_used_quality.value}")
        
    async def _balance_quality_vs_bandwidth(self):
        """Balance quality vs bandwidth usage"""
        if not self.bandwidth_usage:
            return
            
        recent_usage = self.bandwidth_usage[-10:]
        avg_bandwidth = statistics.mean(u.total_mbps for u in recent_usage)
        
        # If consistently high bandwidth usage, suggest quality adjustments
        if avg_bandwidth > self.current_bandwidth_limit * 0.85:
            logger.info("High bandwidth usage detected, recommending quality optimization")
            
    async def _cost_optimization(self):
        """Optimize bandwidth costs"""
        while self.monitoring_active:
            try:
                await self._monitor_cost_efficiency()
                await self._optimize_peak_hour_costs()
                await self._suggest_infrastructure_changes()
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in cost optimization: {e}")
                await asyncio.sleep(300)
                
    async def _monitor_cost_efficiency(self):
        """Monitor cost efficiency metrics"""
        if not self.bandwidth_usage:
            return
            
        recent_usage = [
            u for u in self.bandwidth_usage
            if u.timestamp > datetime.now() - timedelta(hours=24)
        ]
        
        if recent_usage:
            total_cost = sum(u.estimated_monthly_cost for u in recent_usage) / len(recent_usage)
            avg_cost_per_gb = statistics.mean(u.cost_per_gb for u in recent_usage)
            
            if avg_cost_per_gb > self.cost_thresholds["high_cost_per_gb"]:
                logger.warning(f"High bandwidth costs detected: ${avg_cost_per_gb:.3f}/GB")
                
    async def _optimize_peak_hour_costs(self):
        """Optimize costs during peak hours"""
        # Find current peak hour patterns
        peak_patterns = [p for p in self.traffic_patterns if p.pattern_type == "peak_hours"]
        
        if peak_patterns:
            current_hour = datetime.now().hour
            peak_hours = peak_patterns[0].peak_hours
            
            if current_hour in peak_hours:
                logger.info("Peak hour detected, applying cost optimization strategies")
                
    async def _suggest_infrastructure_changes(self):
        """Suggest infrastructure changes for cost optimization"""
        if len(self.bandwidth_usage) < 100:
            return
            
        # Analyze usage patterns
        avg_usage = statistics.mean(u.total_mbps for u in self.bandwidth_usage[-100:])
        peak_usage = max(u.total_mbps for u in self.bandwidth_usage[-100:])
        
        utilization_ratio = avg_usage / self.current_bandwidth_limit
        
        suggestions = []
        
        if utilization_ratio < 0.3:
            suggestions.append("Consider reducing bandwidth capacity to save costs")
        elif utilization_ratio > 0.8:
            suggestions.append("Consider increasing bandwidth capacity for better performance")
            
        if peak_usage > self.current_bandwidth_limit:
            suggestions.append("Implement burst capacity for peak handling")
            
        if suggestions:
            logger.info(f"Infrastructure suggestions: {suggestions}")
            
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get comprehensive bandwidth optimization summary"""
        if not self.bandwidth_usage:
            return {"message": "No bandwidth data available"}
            
        # Calculate summary metrics
        recent_usage = self.bandwidth_usage[-100:]
        
        total_bandwidth = sum(u.total_mbps for u in recent_usage)
        avg_bandwidth = total_bandwidth / len(recent_usage)
        peak_bandwidth = max(u.total_mbps for u in recent_usage)
        
        # Cost metrics
        total_cost = sum(u.estimated_monthly_cost for u in recent_usage)
        avg_cost_per_gb = statistics.mean(u.cost_per_gb for u in recent_usage)
        
        # Quality metrics
        quality_distribution = defaultdict(int)
        for usage in recent_usage:
            quality_distribution[usage.quality_level.value] += 1
            
        # Optimization effectiveness
        bandwidth_savings = sum(
            a.bandwidth_saved_mbps for a in self.quality_adaptations
            if a.timestamp > datetime.now() - timedelta(hours=24)
        )
        
        return {
            "bandwidth_metrics": {
                "average_usage_mbps": avg_bandwidth,
                "peak_usage_mbps": peak_bandwidth,
                "utilization_percentage": (avg_bandwidth / self.current_bandwidth_limit) * 100,
                "capacity_limit_mbps": self.current_bandwidth_limit
            },
            "cost_metrics": {
                "estimated_monthly_cost": total_cost / len(recent_usage),
                "average_cost_per_gb": avg_cost_per_gb,
                "cost_efficiency_score": 1.0 - (avg_cost_per_gb / self.cost_thresholds["high_cost_per_gb"])
            },
            "quality_distribution": dict(quality_distribution),
            "optimization_effectiveness": {
                "total_adaptations_24h": len([a for a in self.quality_adaptations 
                                            if a.timestamp > datetime.now() - timedelta(hours=24)]),
                "bandwidth_saved_mbps": bandwidth_savings,
                "active_optimization_rules": len([r for r in self.optimization_rules if r.enabled])
            },
            "traffic_patterns": len(self.traffic_patterns),
            "recommendations": self._generate_optimization_recommendations()
        }
        
    def _generate_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on current state"""
        recommendations = []
        
        if not self.bandwidth_usage:
            return recommendations
            
        recent_usage = self.bandwidth_usage[-50:]
        avg_bandwidth = statistics.mean(u.total_mbps for u in recent_usage)
        
        # Bandwidth utilization recommendations
        utilization = avg_bandwidth / self.current_bandwidth_limit
        if utilization > 0.9:
            recommendations.append("Consider scaling bandwidth capacity")
        elif utilization < 0.3:
            recommendations.append("Consider reducing bandwidth allocation to save costs")
            
        # Quality optimization recommendations
        high_quality_usage = len([u for u in recent_usage if u.quality_level == QualityLevel.ULTRA])
        if high_quality_usage / len(recent_usage) > 0.5:
            recommendations.append("Consider implementing adaptive quality streaming")
            
        # Cost optimization recommendations
        avg_cost = statistics.mean(u.cost_per_gb for u in recent_usage)
        if avg_cost > self.cost_thresholds["medium_cost_per_gb"]:
            recommendations.append("Implement compression optimization to reduce costs")
            
        return recommendations

# Export main classes
__all__ = [
    'BandwidthOptimizationTracker',
    'BandwidthUsage',
    'OptimizationRule',
    'TrafficPattern',
    'QualityAdaptation',
    'TrafficType',
    'QualityLevel',
    'OptimizationStrategy'
]