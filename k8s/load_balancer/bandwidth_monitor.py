"""Bandwidth Monitor for Load Balancer - IA Influencer Agent Platform

Advanced bandwidth monitoring and traffic shaping for optimal performance
of content protection, fingerprinting, and monetization services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""

import asyncio
import logging
import time
import psutil
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import statistics
from collections import deque, defaultdict
import threading
import subprocess
import re

logger = logging.getLogger(__name__)


class TrafficType(Enum):
    """
Traffic type classification"""

    UPLOAD = "upload"
    DOWNLOAD = "download"
    API_REQUESTS = "api_requests"
    WEBSOCKET = "websocket"
    FINGERPRINTING = "fingerprinting"
    PROTECTION = "protection"
    MONETIZATION = "monetization"
    AI_AGENT = "ai_agent"
    CRAWLERS = "crawlers"


@dataclass
class BandwidthLimit:
    """Bandwidth limit configuration"""
    service_name: str
    traffic_type: TrafficType
    max_bandwidth_mbps: float
    burst_bandwidth_mbps: float
    priority: int = 5  # 1 = highest, 10 = lowest
    enabled: bool = True


@dataclass
class TrafficSample:
    """
Traffic measurement sample"""
    timestamp: datetime
    bytes_in: int
    bytes_out: int
    packets_in: int
    packets_out: int
    connections: int
    latency_ms: float = 0.0
    errors: int = 0


@dataclass
class ServiceTrafficStats:
    """
Traffic statistics for a service"""
    service_name: str
    current_bandwidth_in_mbps: float = 0.0
    current_bandwidth_out_mbps: float = 0.0
    avg_bandwidth_in_mbps: float = 0.0
    avg_bandwidth_out_mbps: float = 0.0
    peak_bandwidth_in_mbps: float = 0.0
    peak_bandwidth_out_mbps: float = 0.0
    total_bytes_in: int = 0
    total_bytes_out: int = 0
    active_connections: int = 0
    avg_latency_ms: float = 0.0
    error_rate: float = 0.0
    samples: deque = field(default_factory=lambda: deque(maxlen=1440))  # 24 hours @ 1min intervals


class BandwidthMonitor:
    """
    Enterprise Bandwidth Monitor for Load Balancer
    
    Provides comprehensive traffic monitoring, bandwidth limiting,
    and Quality of Service (QoS) management for the IA Influencer
    Agent platform's microservices.
    """
    
    def __init__(self, collection_interval: int = 10):
        self.collection_interval = collection_interval
        
        # Traffic monitoring
        self.service_stats: Dict[str, ServiceTrafficStats] = {}
        self.bandwidth_limits: Dict[str, BandwidthLimit] = {}
        self.traffic_history: deque = deque(maxlen=8640)  # 24 hours @ 10s intervals
        
        # Network interfaces
        self.network_interfaces: List[str] = []
        self.main_interface: Optional[str] = None
        
        # Runtime state
        self.is_monitoring = False
        self.monitor_task = None
        self.shaping_task = None
        self.last_network_stats = {}
        
        # Alerts and thresholds
        self.bandwidth_threshold = 0.8  # Alert at 80% usage
        self.latency_threshold_ms = 1000
        self.error_rate_threshold = 0.05  # 5%
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        logger.info("Bandwidth Monitor initialized")
    
    async def initialize(self) -> None:
        """Initialize bandwidth monitoring"""
        try:
            logger.info("Initializing Bandwidth Monitor...")
            
            # Discover network interfaces
            await self._discover_network_interfaces()
            
            # Configure service limits
            await self._configure_service_limits()
            
            # Initialize service statistics
            await self._initialize_service_stats()
            
            # Setup traffic shaping
            await self._setup_traffic_shaping()
            
            logger.info("Bandwidth Monitor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Bandwidth Monitor: {e}")
            raise
    
    async def _discover_network_interfaces(self) -> None:
        """Discover available network interfaces"""
        try:
            interfaces = psutil.net_if_stats()
            self.network_interfaces = [
                name for name, stats in interfaces.items()
                if stats.isup and name != 'lo'  # Exclude loopback
            ]
            
            # Select main interface (usually the one with default route)
            if self.network_interfaces:
                self.main_interface = self.network_interfaces[0]
                
                # Try to find the interface with most traffic
                net_io = psutil.net_io_counters(pernic=True)
                max_traffic = 0
                for interface in self.network_interfaces:
                    if interface in net_io:
                        traffic = net_io[interface].bytes_sent + net_io[interface].bytes_recv
                        if traffic > max_traffic:
                            max_traffic = traffic
                            self.main_interface = interface
            
            logger.info(f"Discovered network interfaces: {self.network_interfaces}")
            logger.info(f"Main interface: {self.main_interface}")
            
        except Exception as e:
            logger.error(f"Failed to discover network interfaces: {e}")
            raise
    
    async def _configure_service_limits(self) -> None:
        """Configure bandwidth limits for platform services"""
        # Fingerprinting service - high bandwidth for media uploads
        self.bandwidth_limits["fingerprinting_upload"] = BandwidthLimit(
            service_name="fingerprinting",
            traffic_type=TrafficType.UPLOAD,
            max_bandwidth_mbps=500.0,  # 500 Mbps for media uploads
            burst_bandwidth_mbps=800.0,
            priority=2
        )
        
        self.bandwidth_limits["fingerprinting_processing"] = BandwidthLimit(
            service_name="fingerprinting",
            traffic_type=TrafficType.FINGERPRINTING,
            max_bandwidth_mbps=200.0,
            burst_bandwidth_mbps=300.0,
            priority=3
        )
        
        # Protection service - moderate bandwidth
        self.bandwidth_limits["protection_api"] = BandwidthLimit(
            service_name="protection",
            traffic_type=TrafficType.API_REQUESTS,
            max_bandwidth_mbps=100.0,
            burst_bandwidth_mbps=150.0,
            priority=4
        )
        
        # Monetization service - critical for revenue
        self.bandwidth_limits["monetization_api"] = BandwidthLimit(
            service_name="monetization",
            traffic_type=TrafficType.API_REQUESTS,
            max_bandwidth_mbps=150.0,
            burst_bandwidth_mbps=200.0,
            priority=1  # Highest priority
        )
        
        # AI Agent service - moderate priority
        self.bandwidth_limits["ai_agent_api"] = BandwidthLimit(
            service_name="ai_agent",
            traffic_type=TrafficType.AI_AGENT,
            max_bandwidth_mbps=100.0,
            burst_bandwidth_mbps=150.0,
            priority=3
        )
        
        # Crawler service - lowest priority
        self.bandwidth_limits["crawlers_download"] = BandwidthLimit(
            service_name="crawlers",
            traffic_type=TrafficType.DOWNLOAD,
            max_bandwidth_mbps=50.0,
            burst_bandwidth_mbps=100.0,
            priority=8
        )
        
        logger.info(f"Configured {len(self.bandwidth_limits)} bandwidth limits")
    
    async def _initialize_service_stats(self) -> None:
        """Initialize statistics tracking for services"""
        services = ["fingerprinting", "protection", "monetization", "ai_agent", "crawlers"]
        
        for service in services:
            self.service_stats[service] = ServiceTrafficStats(service_name=service)
        
        logger.info(f"Initialized statistics for {len(services)} services")
    
    async def _setup_traffic_shaping(self) -> None:
        """Setup traffic shaping using tc (Traffic Control)"""
        try:
            if not self.main_interface:
                logger.warning("No main interface found, skipping traffic shaping")
                return
            
            # Remove existing qdisc
            try:
                subprocess.run([
                    "tc", "qdisc", "del", "dev", self.main_interface, "root"
                ], capture_output=True)
            except subprocess.CalledProcessError:
                pass  # Ignore if no existing qdisc
            
            # Create HTB (Hierarchical Token Bucket) root qdisc
            subprocess.run([
                "tc", "qdisc", "add", "dev", self.main_interface, "root", "handle", "1:",
                "htb", "default", "999"
            ], check=True, capture_output=True)
            
            # Create root class with total bandwidth
            subprocess.run([
                "tc", "class", "add", "dev", self.main_interface, "parent", "1:",
                "classid", "1:1", "htb", "rate", "1000mbit", "ceil", "1000mbit"
            ], check=True, capture_output=True)
            
            # Create service-specific classes
            class_id = 10
            for limit_name, limit in self.bandwidth_limits.items():
                if limit.enabled:
                    class_id += 1
                    
                    # Create class for the service
                    subprocess.run([
                        "tc", "class", "add", "dev", self.main_interface,
                        "parent", "1:1", "classid", f"1:{class_id}",
                        "htb", "rate", f"{limit.max_bandwidth_mbps}mbit",
                        "ceil", f"{limit.burst_bandwidth_mbps}mbit",
                        "prio", str(limit.priority)
                    ], check=True, capture_output=True)
                    
                    # Add SFQ qdisc for fair queuing
                    subprocess.run([
                        "tc", "qdisc", "add", "dev", self.main_interface,
                        "parent", f"1:{class_id}", "handle", f"{class_id}:",
                        "sfq", "perturb", "10"
                    ], check=True, capture_output=True)
            
            logger.info("Traffic shaping configured successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to setup traffic shaping: {e}")
        except Exception as e:
            logger.error(f"Error in traffic shaping setup: {e}")
    
    async def start_monitoring(self) -> None:
        """Start bandwidth monitoring"""
        if self.is_monitoring:
            logger.warning("Bandwidth monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        self.shaping_task = asyncio.create_task(self._traffic_shaping_loop())
        
        logger.info("Bandwidth monitoring started")
    
    async def stop_monitoring(self) -> None:
        try:
                    # Collect metrics
                    metrics = {
                        "timestamp": datetime.utcnow(),
                        "metric_name": "stop_monitoring",
                        "value": data if data else 0,
                        "tags": self._get_metric_tags()
                    }
            
                    # Store metrics
                    await self._store_metric(metrics)
            
                    # Send to monitoring system
                    if hasattr(self, 'metrics_client'):
                        await self.metrics_client.send(metrics)
            
                    logger.info(f"Metric stop_monitoring collected")
                    return metrics
            
                except Exception as e:
                    logger.error(f"Metric collection stop_monitoring failed: {e}")
                    return None
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect network statistics
                await self._collect_network_stats()
                
                # Update service statistics
                await self._update_service_stats()
                
                # Check for alerts
                await self._check_bandwidth_alerts()
                
                # Sleep for collection interval
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_network_stats(self) -> None:
        """Collect network interface statistics"""
        try:
            current_time = datetime.now()
            
            # Get network I/O counters
            net_io = psutil.net_io_counters(pernic=True)
            
            if self.main_interface in net_io:
                stats = net_io[self.main_interface]
                
                # Calculate rates if we have previous stats
                if self.main_interface in self.last_network_stats:
                    prev_stats, prev_time = self.last_network_stats[self.main_interface]
                    time_diff = (current_time - prev_time).total_seconds()
                    
                    if time_diff > 0:
                        bytes_in_rate = (stats.bytes_recv - prev_stats.bytes_recv) / time_diff
                        bytes_out_rate = (stats.bytes_sent - prev_stats.bytes_sent) / time_diff
                        packets_in_rate = (stats.packets_recv - prev_stats.packets_recv) / time_diff
                        packets_out_rate = (stats.packets_sent - prev_stats.packets_sent) / time_diff
                        
                        # Convert to Mbps
                        bandwidth_in_mbps = (bytes_in_rate * 8) / (1024 * 1024)
                        bandwidth_out_mbps = (bytes_out_rate * 8) / (1024 * 1024)
                        
                        # Create traffic sample
                        sample = TrafficSample(
                            timestamp=current_time,
                            bytes_in=int(bytes_in_rate),
                            bytes_out=int(bytes_out_rate),
                            packets_in=int(packets_in_rate),
                            packets_out=int(packets_out_rate),
                            connections=0,  # Will be updated by service-specific monitoring
                            errors=stats.errin + stats.errout
                        )
                        
                        self.traffic_history.append(sample)
                
                # Store current stats for next calculation
                self.last_network_stats[self.main_interface] = (stats, current_time)
                
        except Exception as e:
            logger.error(f"Failed to collect network stats: {e}")
    
    async def _update_service_stats(self) -> None:
        """Update statistics for each service"""
        try:
            current_time = datetime.now()
            
            for service_name, stats in self.service_stats.items():
                # Get service-specific metrics (this would integrate with service monitoring)
                # For now, we'll use placeholder logic
                
                # Calculate averages from recent samples
                if len(stats.samples) > 0:
                    recent_samples = list(stats.samples)[-60:]  # Last hour
                    
                    if recent_samples:
                        stats.avg_bandwidth_in_mbps = statistics.mean(
                            [(s.bytes_in * 8) / (1024 * 1024) for s in recent_samples]
                        )
                        stats.avg_bandwidth_out_mbps = statistics.mean(
                            [(s.bytes_out * 8) / (1024 * 1024) for s in recent_samples]
                        )
                        stats.avg_latency_ms = statistics.mean(
                            [s.latency_ms for s in recent_samples if s.latency_ms > 0]
                        ) if any(s.latency_ms > 0 for s in recent_samples) else 0.0
                
                # Update peak values
                if self.traffic_history:
                    latest_sample = self.traffic_history[-1]
                    current_in_mbps = (latest_sample.bytes_in * 8) / (1024 * 1024)
                    current_out_mbps = (latest_sample.bytes_out * 8) / (1024 * 1024)
                    
                    stats.current_bandwidth_in_mbps = current_in_mbps
                    stats.current_bandwidth_out_mbps = current_out_mbps
                    
                    if current_in_mbps > stats.peak_bandwidth_in_mbps:
                        stats.peak_bandwidth_in_mbps = current_in_mbps
                    
                    if current_out_mbps > stats.peak_bandwidth_out_mbps:
                        stats.peak_bandwidth_out_mbps = current_out_mbps
                
        except Exception as e:
            logger.error(f"Failed to update service stats: {e}")
    
    async def _check_bandwidth_alerts(self) -> None:
        """Check for bandwidth usage alerts"""
        try:
            for limit_name, limit in self.bandwidth_limits.items():
                if not limit.enabled:
                    continue
                
                service_stats = self.service_stats.get(limit.service_name)
                if not service_stats:
                    continue
                
                # Check bandwidth usage
                current_usage = service_stats.current_bandwidth_out_mbps
                if limit.traffic_type == TrafficType.UPLOAD:
                    current_usage = service_stats.current_bandwidth_in_mbps
                
                usage_percentage = (current_usage / limit.max_bandwidth_mbps) * 100
                
                if usage_percentage > self.bandwidth_threshold * 100:
                    logger.warning(
                        f"High bandwidth usage for {limit.service_name}: "
                        f"{usage_percentage:.1f}% ({current_usage:.1f} Mbps)"
                    )
                
                # Check latency
                if service_stats.avg_latency_ms > self.latency_threshold_ms:
                    logger.warning(
                        f"High latency for {limit.service_name}: "
                        f"{service_stats.avg_latency_ms:.1f}ms"
                    )
                
        except Exception as e:
            logger.error(f"Failed to check bandwidth alerts: {e}")
    
    async def _traffic_shaping_loop(self) -> None:
        """Traffic shaping adjustment loop"""
        while self.is_monitoring:
            try:
                # Adjust traffic shaping based on current usage
                await self._adjust_traffic_shaping()
                
                # Sleep for 60 seconds (less frequent than monitoring)
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in traffic shaping loop: {e}")
                await asyncio.sleep(60)
    
    async def _adjust_traffic_shaping(self) -> None:
        """Adjust traffic shaping rules based on current usage"""
        try:
            # This would implement dynamic adjustment of tc rules
            # based on current traffic patterns and service priorities
            
            # For now, we'll log the current status
            total_bandwidth_used = sum(
                stats.current_bandwidth_in_mbps + stats.current_bandwidth_out_mbps
                for stats in self.service_stats.values()
            )
            
            logger.debug(f"Total bandwidth usage: {total_bandwidth_used:.2f} Mbps")
            
        except Exception as e:
            logger.error(f"Failed to adjust traffic shaping: {e}")
    
    async def get_bandwidth_statistics(self) -> Dict[str, Any]:
        """Get comprehensive bandwidth statistics"""
        try:
            with self._lock:
                # Calculate total usage
                total_in_mbps = sum(stats.current_bandwidth_in_mbps for stats in self.service_stats.values())
                total_out_mbps = sum(stats.current_bandwidth_out_mbps for stats in self.service_stats.values())
                
                # Service breakdown
                service_breakdown = {}
                for service_name, stats in self.service_stats.items():
                    service_breakdown[service_name] = {
                        "current_in_mbps": stats.current_bandwidth_in_mbps,
                        "current_out_mbps": stats.current_bandwidth_out_mbps,
                        "avg_in_mbps": stats.avg_bandwidth_in_mbps,
                        "avg_out_mbps": stats.avg_bandwidth_out_mbps,
                        "peak_in_mbps": stats.peak_bandwidth_in_mbps,
                        "peak_out_mbps": stats.peak_bandwidth_out_mbps,
                        "total_bytes_in": stats.total_bytes_in,
                        "total_bytes_out": stats.total_bytes_out,
                        "active_connections": stats.active_connections,
                        "avg_latency_ms": stats.avg_latency_ms,
                        "error_rate": stats.error_rate
                    }
                
                # Recent traffic history
                recent_history = []
                if len(self.traffic_history) >= 60:  # Last 10 minutes
                    for sample in list(self.traffic_history)[-60:]:
                        recent_history.append({
                            "timestamp": sample.timestamp.isoformat(),
                            "bandwidth_in_mbps": (sample.bytes_in * 8) / (1024 * 1024),
                            "bandwidth_out_mbps": (sample.bytes_out * 8) / (1024 * 1024),
                            "packets_in": sample.packets_in,
                            "packets_out": sample.packets_out,
                            "latency_ms": sample.latency_ms,
                            "errors": sample.errors
                        })
                
                return {
                    "total_bandwidth_in_mbps": total_in_mbps,
                    "total_bandwidth_out_mbps": total_out_mbps,
                    "is_monitoring": self.is_monitoring,
                    "main_interface": self.main_interface,
                    "network_interfaces": self.network_interfaces,
                    "service_breakdown": service_breakdown,
                    "bandwidth_limits": {
                        name: {
                            "service_name": limit.service_name,
                            "traffic_type": limit.traffic_type.value,
                            "max_bandwidth_mbps": limit.max_bandwidth_mbps,
                            "burst_bandwidth_mbps": limit.burst_bandwidth_mbps,
                            "priority": limit.priority,
                            "enabled": limit.enabled
                        } for name, limit in self.bandwidth_limits.items()
                    },
                    "recent_history": recent_history,
                    "collection_interval": self.collection_interval,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get bandwidth statistics: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def set_bandwidth_limit(self, service_name: str, traffic_type: TrafficType,
                                max_bandwidth_mbps: float, burst_bandwidth_mbps: float,
                                priority: int = 5) -> bool:
        """Set or update bandwidth limit for a service"""
        try:
            limit_name = f"{service_name}_{traffic_type.value}"
            
            self.bandwidth_limits[limit_name] = BandwidthLimit(
                service_name=service_name,
                traffic_type=traffic_type,
                max_bandwidth_mbps=max_bandwidth_mbps,
                burst_bandwidth_mbps=burst_bandwidth_mbps,
                priority=priority,
                enabled=True
            )
            
            # Update traffic shaping rules
            await self._setup_traffic_shaping()
            
            logger.info(f"Bandwidth limit updated for {service_name}: {max_bandwidth_mbps} Mbps")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set bandwidth limit: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown bandwidth monitor"""
        try:
            logger.info("Shutting down Bandwidth Monitor...")
            
            await self.stop_monitoring()
            
            # Clean up traffic shaping rules
            if self.main_interface:
                try:
                    subprocess.run([
                        "tc", "qdisc", "del", "dev", self.main_interface, "root"
                    ], capture_output=True)
                    logger.info("Traffic shaping rules cleaned up")
                except subprocess.CalledProcessError:
                    pass  # Ignore if no qdisc exists
            
            logger.info("Bandwidth Monitor shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during Bandwidth Monitor shutdown: {e}")
