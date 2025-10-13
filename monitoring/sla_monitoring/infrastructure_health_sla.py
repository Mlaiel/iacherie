"""Infrastructure Health SLA Monitoring System
Advanced SLA tracking for system uptime, database performance, storage, and network infrastructure.

⚠️ PROPRIETARY CODE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use, distribution, or modification is strictly prohibited.
"""

import asyncio
import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from collections import deque, defaultdict
import json
import time
from enum import Enum

class InfrastructureComponent(Enum):
    """Infrastructure components for SLA tracking"""
    WEB_SERVER = "web_server"
    API_SERVER = "api_server"
    DATABASE = "database"
    CACHE = "cache"
    STORAGE = "storage"
    CDN = "cdn"
    LOAD_BALANCER = "load_balancer"
    MESSAGE_QUEUE = "message_queue"
    SEARCH_ENGINE = "search_engine"
    MONITORING = "monitoring"
    BACKUP_SYSTEM = "backup_system"
    SECURITY_GATEWAY = "security_gateway"

class DatabaseType(Enum):
    """Database types for performance tracking"""
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    INFLUXDB = "influxdb"
    MYSQL = "mysql"
    CASSANDRA = "cassandra"

class StorageType(Enum):
    """Storage types for monitoring"""
    LOCAL_SSD = "local_ssd"
    NETWORK_STORAGE = "network_storage"
    OBJECT_STORAGE = "object_storage"
    BLOCK_STORAGE = "block_storage"
    FILE_SYSTEM = "file_system"
    BACKUP_STORAGE = "backup_storage"

@dataclass
class InfrastructureMetric:
    """Infrastructure health metric with SLA targets"""
    metric_name: str
    target_value: float
    current_value: float = 0.0
    unit: str = ""
    component: InfrastructureComponent = InfrastructureComponent.WEB_SERVER
    database_type: Optional[DatabaseType] = None
    storage_type: Optional[StorageType] = None
    measurement_window: int = 300  # 5 minutes default
    last_measurement: datetime = field(default_factory=datetime.now)
    violation_count: int = 0
    health_score: float = 100.0

@dataclass
class InfrastructureHealthSLATargets:
    """Comprehensive Infrastructure Health SLA targets"""
    # System Uptime SLA
    system_uptime_percentage: float = 99.99  # 99.99% system uptime
    planned_downtime_hours_monthly: float = 4.0  # <4h planned downtime/month
    unplanned_downtime_minutes_monthly: float = 43.2  # <43.2min unplanned downtime/month
    mttr_minutes: float = 15.0  # <15min Mean Time To Recovery
    
    # Database Performance SLA
    database_query_response_ms: float = 100.0  # <100ms database query response
    database_connection_pool_utilization: float = 80.0  # <80% connection pool utilization
    database_availability_percentage: float = 99.999  # 99.999% database availability
    database_backup_success_rate: float = 100.0  # 100% backup success rate
    
    # Cache Performance SLA
    cache_hit_ratio_percentage: float = 95.0  # >95% cache hit ratio
    cache_response_time_ms: float = 5.0  # <5ms cache response time
    cache_memory_utilization: float = 85.0  # <85% cache memory utilization
    cache_eviction_rate: float = 1.0  # <1% eviction rate per hour
    
    # Storage Performance SLA
    storage_availability_percentage: float = 99.999  # 99.999% storage availability
    storage_io_latency_ms: float = 10.0  # <10ms storage I/O latency
    storage_throughput_mbps: float = 1000.0  # >1000 MB/s storage throughput
    storage_utilization_percentage: float = 80.0  # <80% storage utilization
    
    # Network Performance SLA
    network_latency_ms: float = 50.0  # <50ms network latency
    network_packet_loss_percentage: float = 0.01  # <0.01% packet loss
    network_bandwidth_utilization: float = 70.0  # <70% bandwidth utilization
    dns_resolution_ms: float = 20.0  # <20ms DNS resolution
    
    # Load Balancer SLA
    load_balancer_response_time_ms: float = 5.0  # <5ms load balancer response
    load_balancer_availability: float = 99.99  # 99.99% load balancer availability
    load_balancer_health_check_success: float = 99.9  # 99.9% health check success
    
    # CDN Performance SLA
    cdn_cache_hit_ratio: float = 90.0  # >90% CDN cache hit ratio
    cdn_edge_response_time_ms: float = 100.0  # <100ms CDN edge response
    cdn_global_availability: float = 99.95  # 99.95% global CDN availability
    
    # Monitoring System SLA
    monitoring_data_freshness_seconds: float = 30.0  # <30s monitoring data freshness
    monitoring_alert_delivery_seconds: float = 10.0  # <10s alert delivery time
    monitoring_system_availability: float = 99.9  # 99.9% monitoring availability

class InfrastructureHealthSLA:
    """
    Advanced Infrastructure Health SLA monitoring system
    Tracks system uptime, database performance, storage, network, and infrastructure components
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.targets = InfrastructureHealthSLATargets()
        self.metrics: Dict[str, InfrastructureMetric] = {}
        self.measurements: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: List[Dict[str, Any]] = []
        
        # Infrastructure tracking
        self.component_health: Dict[str, Dict[str, Any]] = {}
        self.database_performance: Dict[str, Dict[str, Any]] = {}
        self.storage_metrics: Dict[str, Dict[str, Any]] = {}
        self.network_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Performance monitoring
        self.uptime_tracking: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.error_rates: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.resource_utilization: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        self._setup_default_metrics()
        
    def _setup_default_metrics(self):
        """Initialize default infrastructure health metrics"""
        default_metrics = [
            ("system_uptime", self.targets.system_uptime_percentage, "percentage", InfrastructureComponent.WEB_SERVER),
            ("database_performance", self.targets.database_query_response_ms, "milliseconds", InfrastructureComponent.DATABASE),
            ("cache_performance", self.targets.cache_hit_ratio_percentage, "percentage", InfrastructureComponent.CACHE),
            ("storage_availability", self.targets.storage_availability_percentage, "percentage", InfrastructureComponent.STORAGE),
            ("network_latency", self.targets.network_latency_ms, "milliseconds", InfrastructureComponent.LOAD_BALANCER),
            ("monitoring_freshness", self.targets.monitoring_data_freshness_seconds, "seconds", InfrastructureComponent.MONITORING),
        ]
        
        for metric_name, target, unit, component in default_metrics:
            self.metrics[metric_name] = InfrastructureMetric(
                metric_name=metric_name,
                target_value=target,
                unit=unit,
                component=component
            )
    
    async def track_system_uptime(self, uptime_id: str, component: InfrastructureComponent,
                                service_name: str, measurement_start: datetime,
                                measurement_end: datetime, uptime_percentage: float,
                                downtime_minutes: float, planned_downtime: bool,
                                incident_count: int) -> Dict[str, Any]:
        """Track system uptime SLA compliance"""
        try:
            measurement_duration = (measurement_end - measurement_start).total_seconds() / 3600  # Convert to hours
            
            # Update metric
            metric = self.metrics["system_uptime"]
            metric.current_value = uptime_percentage
            metric.last_measurement = measurement_end
            metric.component = component
            metric.health_score = uptime_percentage
            
            # Check SLA compliance
            uptime_compliant = uptime_percentage >= self.targets.system_uptime_percentage
            
            if planned_downtime:
                downtime_compliant = downtime_minutes <= (self.targets.planned_downtime_hours_monthly * 60)
            else:
                downtime_compliant = downtime_minutes <= self.targets.unplanned_downtime_minutes_monthly
            
            if not uptime_compliant:
                metric.violation_count += 1
                await self._generate_alert(
                    "System Uptime SLA Violation",
                    f"Service {service_name} uptime: {uptime_percentage:.3f}% (target: {self.targets.system_uptime_percentage}%)",
                    "critical",
                    {
                        "uptime_id": uptime_id,
                        "component": component.value,
                        "service_name": service_name,
                        "uptime_percentage": uptime_percentage,
                        "downtime_minutes": downtime_minutes,
                        "planned_downtime": planned_downtime,
                        "incident_count": incident_count
                    }
                )
            
            if not downtime_compliant:
                severity = "medium" if planned_downtime else "high"
                await self._generate_alert(
                    "Downtime SLA Violation",
                    f"Service {service_name} downtime: {downtime_minutes:.2f}min exceeded monthly limit",
                    severity,
                    {
                        "uptime_id": uptime_id,
                        "service_name": service_name,
                        "downtime_minutes": downtime_minutes,
                        "planned_downtime": planned_downtime,
                        "monthly_limit": self.targets.planned_downtime_hours_monthly * 60 if planned_downtime else self.targets.unplanned_downtime_minutes_monthly
                    }
                )
            
            # Store measurements
            self.measurements["system_uptime"].append({
                "timestamp": measurement_end,
                "value": uptime_percentage,
                "uptime_id": uptime_id,
                "component": component.value,
                "service_name": service_name,
                "downtime_minutes": downtime_minutes,
                "planned_downtime": planned_downtime,
                "incident_count": incident_count,
                "measurement_duration": measurement_duration,
                "uptime_compliant": uptime_compliant,
                "downtime_compliant": downtime_compliant
            })
            
            # Update component health tracking
            component_key = f"{component.value}:{service_name}"
            self.component_health[component_key] = {
                "uptime_percentage": uptime_percentage,
                "downtime_minutes": downtime_minutes,
                "planned_downtime": planned_downtime,
                "incident_count": incident_count,
                "last_measurement": measurement_end,
                "health_score": uptime_percentage
            }
            
            # Update uptime tracking
            self.uptime_tracking[component.value].append(uptime_percentage)
            
            self.logger.info(f"System uptime tracked - Component: {component.value}, Service: {service_name}, Uptime: {uptime_percentage:.3f}%")
            
            return {
                "uptime_id": uptime_id,
                "component": component.value,
                "service_name": service_name,
                "uptime_percentage": uptime_percentage,
                "downtime_minutes": downtime_minutes,
                "planned_downtime": planned_downtime,
                "incident_count": incident_count,
                "uptime_compliant": uptime_compliant,
                "downtime_compliant": downtime_compliant
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking system uptime: {e}")
            raise
    
    async def track_database_performance(self, db_metric_id: str, database_type: DatabaseType,
                                       database_name: str, measurement_time: datetime,
                                       query_response_time_ms: float, connection_pool_utilization: float,
                                       active_connections: int, max_connections: int,
                                       query_throughput_qps: float, cache_hit_ratio: float) -> Dict[str, Any]:
        """Track database performance SLA compliance"""
        try:
            # Update metric
            metric = self.metrics["database_performance"]
            metric.current_value = query_response_time_ms
            metric.last_measurement = measurement_time
            metric.component = InfrastructureComponent.DATABASE
            metric.database_type = database_type
            
            # Calculate health score based on multiple factors
            response_score = max(0, 100 - (query_response_time_ms / self.targets.database_query_response_ms) * 100)
            utilization_score = max(0, 100 - (connection_pool_utilization / self.targets.database_connection_pool_utilization) * 100)
            cache_score = (cache_hit_ratio / 95.0) * 100  # 95% is optimal cache hit ratio
            health_score = (response_score + utilization_score + cache_score) / 3
            
            metric.health_score = health_score
            
            # Check SLA compliance
            response_compliant = query_response_time_ms <= self.targets.database_query_response_ms
            utilization_compliant = connection_pool_utilization <= self.targets.database_connection_pool_utilization
            cache_compliant = cache_hit_ratio >= 80.0  # Minimum acceptable cache hit ratio
            
            if not response_compliant:
                metric.violation_count += 1
                await self._generate_alert(
                    "Database Response Time SLA Violation",
                    f"Database {database_name} response time: {query_response_time_ms:.2f}ms (target: {self.targets.database_query_response_ms}ms)",
                    "high",
                    {
                        "db_metric_id": db_metric_id,
                        "database_type": database_type.value,
                        "database_name": database_name,
                        "query_response_time_ms": query_response_time_ms,
                        "connection_pool_utilization": connection_pool_utilization,
                        "active_connections": active_connections,
                        "max_connections": max_connections
                    }
                )
            
            if not utilization_compliant:
                await self._generate_alert(
                    "Database Connection Pool SLA Violation",
                    f"Database {database_name} connection pool utilization: {connection_pool_utilization:.2f}% (target: <{self.targets.database_connection_pool_utilization}%)",
                    "medium",
                    {
                        "db_metric_id": db_metric_id,
                        "database_name": database_name,
                        "connection_pool_utilization": connection_pool_utilization,
                        "active_connections": active_connections,
                        "max_connections": max_connections
                    }
                )
            
            if not cache_compliant:
                await self._generate_alert(
                    "Database Cache Performance Warning",
                    f"Database {database_name} cache hit ratio: {cache_hit_ratio:.2f}% (recommended: >80%)",
                    "medium",
                    {
                        "db_metric_id": db_metric_id,
                        "database_name": database_name,
                        "cache_hit_ratio": cache_hit_ratio
                    }
                )
            
            # Store measurements
            self.measurements["database_performance"].append({
                "timestamp": measurement_time,
                "value": query_response_time_ms,
                "db_metric_id": db_metric_id,
                "database_type": database_type.value,
                "database_name": database_name,
                "query_response_time_ms": query_response_time_ms,
                "connection_pool_utilization": connection_pool_utilization,
                "active_connections": active_connections,
                "max_connections": max_connections,
                "query_throughput_qps": query_throughput_qps,
                "cache_hit_ratio": cache_hit_ratio,
                "health_score": health_score,
                "response_compliant": response_compliant,
                "utilization_compliant": utilization_compliant,
                "cache_compliant": cache_compliant
            })
            
            # Update database performance tracking
            db_key = f"{database_type.value}:{database_name}"
            self.database_performance[db_key] = {
                "query_response_time_ms": query_response_time_ms,
                "connection_pool_utilization": connection_pool_utilization,
                "active_connections": active_connections,
                "max_connections": max_connections,
                "query_throughput_qps": query_throughput_qps,
                "cache_hit_ratio": cache_hit_ratio,
                "health_score": health_score,
                "last_measurement": measurement_time
            }
            
            # Update response time tracking
            self.response_times[db_key].append(query_response_time_ms)
            
            self.logger.info(f"Database performance tracked - DB: {database_name}, Response: {query_response_time_ms:.2f}ms, Health: {health_score:.2f}")
            
            return {
                "db_metric_id": db_metric_id,
                "database_type": database_type.value,
                "database_name": database_name,
                "query_response_time_ms": query_response_time_ms,
                "connection_pool_utilization": connection_pool_utilization,
                "query_throughput_qps": query_throughput_qps,
                "cache_hit_ratio": cache_hit_ratio,
                "health_score": health_score,
                "response_compliant": response_compliant,
                "utilization_compliant": utilization_compliant,
                "cache_compliant": cache_compliant
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking database performance: {e}")
            raise
    
    async def track_storage_performance(self, storage_metric_id: str, storage_type: StorageType,
                                      storage_name: str, measurement_time: datetime,
                                      io_latency_ms: float, throughput_mbps: float,
                                      utilization_percentage: float, iops: int,
                                      availability_percentage: float) -> Dict[str, Any]:
        """Track storage performance SLA compliance"""
        try:
            # Update metric
            metric = self.metrics["storage_availability"]
            metric.current_value = availability_percentage
            metric.last_measurement = measurement_time
            metric.component = InfrastructureComponent.STORAGE
            metric.storage_type = storage_type
            
            # Calculate health score
            latency_score = max(0, 100 - (io_latency_ms / self.targets.storage_io_latency_ms) * 100)
            throughput_score = min(100, (throughput_mbps / self.targets.storage_throughput_mbps) * 100)
            utilization_score = max(0, 100 - (utilization_percentage / self.targets.storage_utilization_percentage) * 100)
            availability_score = availability_percentage
            health_score = (latency_score + throughput_score + utilization_score + availability_score) / 4
            
            metric.health_score = health_score
            
            # Check SLA compliance
            latency_compliant = io_latency_ms <= self.targets.storage_io_latency_ms
            throughput_compliant = throughput_mbps >= self.targets.storage_throughput_mbps
            utilization_compliant = utilization_percentage <= self.targets.storage_utilization_percentage
            availability_compliant = availability_percentage >= self.targets.storage_availability_percentage
            
            if not latency_compliant:
                metric.violation_count += 1
                await self._generate_alert(
                    "Storage I/O Latency SLA Violation",
                    f"Storage {storage_name} I/O latency: {io_latency_ms:.2f}ms (target: {self.targets.storage_io_latency_ms}ms)",
                    "high",
                    {
                        "storage_metric_id": storage_metric_id,
                        "storage_type": storage_type.value,
                        "storage_name": storage_name,
                        "io_latency_ms": io_latency_ms,
                        "throughput_mbps": throughput_mbps,
                        "utilization_percentage": utilization_percentage
                    }
                )
            
            if not throughput_compliant:
                await self._generate_alert(
                    "Storage Throughput SLA Violation",
                    f"Storage {storage_name} throughput: {throughput_mbps:.2f} MB/s (target: {self.targets.storage_throughput_mbps} MB/s)",
                    "medium",
                    {
                        "storage_metric_id": storage_metric_id,
                        "storage_name": storage_name,
                        "throughput_mbps": throughput_mbps,
                        "storage_type": storage_type.value
                    }
                )
            
            if not utilization_compliant:
                await self._generate_alert(
                    "Storage Utilization Warning",
                    f"Storage {storage_name} utilization: {utilization_percentage:.2f}% (warning threshold: {self.targets.storage_utilization_percentage}%)",
                    "medium",
                    {
                        "storage_metric_id": storage_metric_id,
                        "storage_name": storage_name,
                        "utilization_percentage": utilization_percentage
                    }
                )
            
            if not availability_compliant:
                await self._generate_alert(
                    "Storage Availability SLA Violation",
                    f"Storage {storage_name} availability: {availability_percentage:.3f}% (target: {self.targets.storage_availability_percentage}%)",
                    "critical",
                    {
                        "storage_metric_id": storage_metric_id,
                        "storage_name": storage_name,
                        "availability_percentage": availability_percentage,
                        "storage_type": storage_type.value
                    }
                )
            
            # Store measurements
            self.measurements["storage_availability"].append({
                "timestamp": measurement_time,
                "value": availability_percentage,
                "storage_metric_id": storage_metric_id,
                "storage_type": storage_type.value,
                "storage_name": storage_name,
                "io_latency_ms": io_latency_ms,
                "throughput_mbps": throughput_mbps,
                "utilization_percentage": utilization_percentage,
                "iops": iops,
                "availability_percentage": availability_percentage,
                "health_score": health_score,
                "latency_compliant": latency_compliant,
                "throughput_compliant": throughput_compliant,
                "utilization_compliant": utilization_compliant,
                "availability_compliant": availability_compliant
            })
            
            # Update storage metrics tracking
            storage_key = f"{storage_type.value}:{storage_name}"
            self.storage_metrics[storage_key] = {
                "io_latency_ms": io_latency_ms,
                "throughput_mbps": throughput_mbps,
                "utilization_percentage": utilization_percentage,
                "iops": iops,
                "availability_percentage": availability_percentage,
                "health_score": health_score,
                "last_measurement": measurement_time
            }
            
            # Update performance tracking
            self.response_times[storage_key].append(io_latency_ms)
            self.resource_utilization[storage_key].append(utilization_percentage)
            
            self.logger.info(f"Storage performance tracked - Storage: {storage_name}, Latency: {io_latency_ms:.2f}ms, Health: {health_score:.2f}")
            
            return {
                "storage_metric_id": storage_metric_id,
                "storage_type": storage_type.value,
                "storage_name": storage_name,
                "io_latency_ms": io_latency_ms,
                "throughput_mbps": throughput_mbps,
                "utilization_percentage": utilization_percentage,
                "iops": iops,
                "availability_percentage": availability_percentage,
                "health_score": health_score,
                "latency_compliant": latency_compliant,
                "throughput_compliant": throughput_compliant,
                "utilization_compliant": utilization_compliant,
                "availability_compliant": availability_compliant
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking storage performance: {e}")
            raise
    
    async def track_network_performance(self, network_metric_id: str, measurement_time: datetime,
                                      network_latency_ms: float, packet_loss_percentage: float,
                                      bandwidth_utilization_percentage: float, dns_resolution_ms: float,
                                      connection_success_rate: float) -> Dict[str, Any]:
        """Track network performance SLA compliance"""
        try:
            # Update metric
            metric = self.metrics["network_latency"]
            metric.current_value = network_latency_ms
            metric.last_measurement = measurement_time
            metric.component = InfrastructureComponent.LOAD_BALANCER
            
            # Calculate health score
            latency_score = max(0, 100 - (network_latency_ms / self.targets.network_latency_ms) * 100)
            packet_loss_score = max(0, 100 - (packet_loss_percentage / self.targets.network_packet_loss_percentage) * 100)
            bandwidth_score = max(0, 100 - (bandwidth_utilization_percentage / self.targets.network_bandwidth_utilization) * 100)
            dns_score = max(0, 100 - (dns_resolution_ms / self.targets.dns_resolution_ms) * 100)
            connection_score = connection_success_rate
            health_score = (latency_score + packet_loss_score + bandwidth_score + dns_score + connection_score) / 5
            
            metric.health_score = health_score
            
            # Check SLA compliance
            latency_compliant = network_latency_ms <= self.targets.network_latency_ms
            packet_loss_compliant = packet_loss_percentage <= self.targets.network_packet_loss_percentage
            bandwidth_compliant = bandwidth_utilization_percentage <= self.targets.network_bandwidth_utilization
            dns_compliant = dns_resolution_ms <= self.targets.dns_resolution_ms
            connection_compliant = connection_success_rate >= 99.0  # 99% connection success rate
            
            if not latency_compliant:
                metric.violation_count += 1
                await self._generate_alert(
                    "Network Latency SLA Violation",
                    f"Network latency: {network_latency_ms:.2f}ms (target: {self.targets.network_latency_ms}ms)",
                    "medium",
                    {
                        "network_metric_id": network_metric_id,
                        "network_latency_ms": network_latency_ms,
                        "packet_loss_percentage": packet_loss_percentage,
                        "bandwidth_utilization_percentage": bandwidth_utilization_percentage
                    }
                )
            
            if not packet_loss_compliant:
                await self._generate_alert(
                    "Network Packet Loss SLA Violation",
                    f"Packet loss: {packet_loss_percentage:.4f}% (target: {self.targets.network_packet_loss_percentage}%)",
                    "high",
                    {
                        "network_metric_id": network_metric_id,
                        "packet_loss_percentage": packet_loss_percentage,
                        "network_latency_ms": network_latency_ms
                    }
                )
            
            if not dns_compliant:
                await self._generate_alert(
                    "DNS Resolution SLA Violation",
                    f"DNS resolution time: {dns_resolution_ms:.2f}ms (target: {self.targets.dns_resolution_ms}ms)",
                    "medium",
                    {
                        "network_metric_id": network_metric_id,
                        "dns_resolution_ms": dns_resolution_ms
                    }
                )
            
            # Store measurements
            self.measurements["network_latency"].append({
                "timestamp": measurement_time,
                "value": network_latency_ms,
                "network_metric_id": network_metric_id,
                "network_latency_ms": network_latency_ms,
                "packet_loss_percentage": packet_loss_percentage,
                "bandwidth_utilization_percentage": bandwidth_utilization_percentage,
                "dns_resolution_ms": dns_resolution_ms,
                "connection_success_rate": connection_success_rate,
                "health_score": health_score,
                "latency_compliant": latency_compliant,
                "packet_loss_compliant": packet_loss_compliant,
                "bandwidth_compliant": bandwidth_compliant,
                "dns_compliant": dns_compliant,
                "connection_compliant": connection_compliant
            })
            
            # Update network metrics tracking
            self.network_metrics["global"] = {
                "network_latency_ms": network_latency_ms,
                "packet_loss_percentage": packet_loss_percentage,
                "bandwidth_utilization_percentage": bandwidth_utilization_percentage,
                "dns_resolution_ms": dns_resolution_ms,
                "connection_success_rate": connection_success_rate,
                "health_score": health_score,
                "last_measurement": measurement_time
            }
            
            # Update performance tracking
            self.response_times["network"].append(network_latency_ms)
            
            self.logger.info(f"Network performance tracked - Latency: {network_latency_ms:.2f}ms, Packet Loss: {packet_loss_percentage:.4f}%, Health: {health_score:.2f}")
            
            return {
                "network_metric_id": network_metric_id,
                "network_latency_ms": network_latency_ms,
                "packet_loss_percentage": packet_loss_percentage,
                "bandwidth_utilization_percentage": bandwidth_utilization_percentage,
                "dns_resolution_ms": dns_resolution_ms,
                "connection_success_rate": connection_success_rate,
                "health_score": health_score,
                "latency_compliant": latency_compliant,
                "packet_loss_compliant": packet_loss_compliant,
                "bandwidth_compliant": bandwidth_compliant,
                "dns_compliant": dns_compliant,
                "connection_compliant": connection_compliant
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking network performance: {e}")
            raise
    
    async def get_infrastructure_sla_summary(self, time_window_hours: int = 24,
                                           component: Optional[InfrastructureComponent] = None) -> Dict[str, Any]:
        """Get comprehensive infrastructure health SLA summary"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
            summary = {
                "time_window_hours": time_window_hours,
                "cutoff_time": cutoff_time.isoformat(),
                "overall_compliance": {},
                "metric_summaries": {},
                "component_health": {},
                "database_analytics": {},
                "storage_analytics": {},
                "network_analytics": {},
                "uptime_analytics": {},
                "recommendations": []
            }
            
            # Calculate overall compliance for each metric
            for metric_name, metric in self.metrics.items():
                measurements = [
                    m for m in self.measurements[metric_name]
                    if m["timestamp"] >= cutoff_time
                ]
                
                # Apply component filter
                if component:
                    measurements = [m for m in measurements if m.get("component") == component.value]
                
                if measurements:
                    # Calculate compliance based on metric type
                    if "compliant" in measurements[0]:
                        compliant_fields = [k for k in measurements[0].keys() if k.endswith("_compliant")]
                        if compliant_fields:
                            compliance_rates = []
                            for field in compliant_fields:
                                field_compliance = (sum(1 for m in measurements if m.get(field, True)) / len(measurements)) * 100
                                compliance_rates.append(field_compliance)
                            compliance_rate = min(compliance_rates)
                        else:
                            compliance_rate = 100.0
                    else:
                        # For percentage-based metrics
                        if metric_name in ["system_uptime", "storage_availability"]:
                            compliance_rate = statistics.mean([m["value"] for m in measurements])
                        else:
                            # For response time metrics, check if values are within target
                            target = metric.target_value
                            compliant_count = sum(1 for m in measurements if m["value"] <= target)
                            compliance_rate = (compliant_count / len(measurements)) * 100
                    
                    avg_value = statistics.mean([m["value"] for m in measurements])
                    p95_value = statistics.quantiles([m["value"] for m in measurements], n=20)[18] if len(measurements) >= 20 else max([m["value"] for m in measurements])
                    avg_health = statistics.mean([m.get("health_score", 100) for m in measurements])
                    
                    summary["metric_summaries"][metric_name] = {
                        "compliance_rate": compliance_rate,
                        "measurement_count": len(measurements),
                        "avg_value": avg_value,
                        "p95_value": p95_value,
                        "avg_health_score": avg_health,
                        "target_value": metric.target_value,
                        "unit": metric.unit,
                        "violation_count": metric.violation_count
                    }
                    
                    summary["overall_compliance"][metric_name] = compliance_rate >= 95.0
            
            # Component health analysis
            for component_key, health in self.component_health.items():
                summary["component_health"][component_key] = {
                    "health_score": health["health_score"],
                    "uptime_percentage": health.get("uptime_percentage", 100.0),
                    "last_measurement": health["last_measurement"].isoformat(),
                    "incident_count": health.get("incident_count", 0)
                }
            
            # Database analytics
            if self.database_performance:
                db_health_scores = [db["health_score"] for db in self.database_performance.values()]
                db_response_times = [db["query_response_time_ms"] for db in self.database_performance.values()]
                db_utilization = [db["connection_pool_utilization"] for db in self.database_performance.values()]
                
                summary["database_analytics"] = {
                    "total_databases": len(self.database_performance),
                    "avg_health_score": statistics.mean(db_health_scores),
                    "avg_response_time": statistics.mean(db_response_times),
                    "avg_connection_utilization": statistics.mean(db_utilization),
                    "healthy_databases": len([db for db in self.database_performance.values() if db["health_score"] >= 90.0])
                }
            
            # Storage analytics
            if self.storage_metrics:
                storage_health_scores = [storage["health_score"] for storage in self.storage_metrics.values()]
                storage_latencies = [storage["io_latency_ms"] for storage in self.storage_metrics.values()]
                storage_utilization = [storage["utilization_percentage"] for storage in self.storage_metrics.values()]
                
                summary["storage_analytics"] = {
                    "total_storage_systems": len(self.storage_metrics),
                    "avg_health_score": statistics.mean(storage_health_scores),
                    "avg_io_latency": statistics.mean(storage_latencies),
                    "avg_utilization": statistics.mean(storage_utilization),
                    "healthy_storage_systems": len([storage for storage in self.storage_metrics.values() if storage["health_score"] >= 90.0])
                }
            
            # Network analytics
            if self.network_metrics:
                network_data = self.network_metrics.get("global", {})
                if network_data:
                    summary["network_analytics"] = {
                        "avg_latency": network_data.get("network_latency_ms", 0),
                        "packet_loss": network_data.get("packet_loss_percentage", 0),
                        "bandwidth_utilization": network_data.get("bandwidth_utilization_percentage", 0),
                        "dns_resolution_time": network_data.get("dns_resolution_ms", 0),
                        "connection_success_rate": network_data.get("connection_success_rate", 100),
                        "health_score": network_data.get("health_score", 100)
                    }
            
            # Uptime analytics
            all_uptime = []
            for uptime_data in self.uptime_tracking.values():
                all_uptime.extend(list(uptime_data))
            
            if all_uptime:
                summary["uptime_analytics"] = {
                    "avg_uptime": statistics.mean(all_uptime),
                    "min_uptime": min(all_uptime),
                    "components_monitored": len(self.uptime_tracking),
                    "components_meeting_sla": len([
                        component for component in self.uptime_tracking.values()
                        if statistics.mean(list(component)) >= self.targets.system_uptime_percentage
                    ])
                }
            
            # Generate recommendations
            for metric_name, compliance in summary["overall_compliance"].items():
                if not compliance:
                    if metric_name == "system_uptime":
                        summary["recommendations"].append("Implement redundancy and failover mechanisms to improve system uptime")
                    elif metric_name == "database_performance":
                        summary["recommendations"].append("Optimize database queries, connection pooling, and implement read replicas")
                    elif metric_name == "storage_availability":
                        summary["recommendations"].append("Implement storage redundancy, monitoring, and predictive maintenance")
                    elif metric_name == "network_latency":
                        summary["recommendations"].append("Optimize network routing, implement CDN, and upgrade network infrastructure")
                    elif metric_name == "cache_performance":
                        summary["recommendations"].append("Optimize cache policies, increase cache capacity, and implement cache warming")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating infrastructure SLA summary: {e}")
            raise
    
    async def _generate_alert(self, title: str, message: str, severity: str, metadata: Dict[str, Any]):
        """Generate SLA violation alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "message": message,
            "severity": severity,
            "component": "infrastructure_health_sla",
            "metadata": metadata
        }
        
        self.alerts.append(alert)
        self.logger.warning(f"Infrastructure SLA Alert - {title}: {message}")
        
        # Keep only last 1000 alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
    
    async def get_real_time_infrastructure_metrics(self) -> Dict[str, Any]:
        """Get real-time infrastructure metrics for monitoring dashboards"""
        try:
            current_time = datetime.now()
            
            metrics_data = {}
            for metric_name, metric in self.metrics.items():
                # Get recent measurements (last 5 minutes)
                recent_measurements = [
                    m for m in self.measurements[metric_name]
                    if (current_time - m["timestamp"]).total_seconds() <= 300
                ]
                
                if recent_measurements:
                    current_avg = statistics.mean([m["value"] for m in recent_measurements])
                    avg_health = statistics.mean([m.get("health_score", 100) for m in recent_measurements])
                    
                    if "compliant" in recent_measurements[0]:
                        compliant_fields = [k for k in recent_measurements[0].keys() if k.endswith("_compliant")]
                        if compliant_fields:
                            compliance_rates = []
                            for field in compliant_fields:
                                field_compliance = (sum(1 for m in recent_measurements if m.get(field, True)) / len(recent_measurements)) * 100
                                compliance_rates.append(field_compliance)
                            compliance_rate = min(compliance_rates)
                        else:
                            compliance_rate = 100.0
                    else:
                        if metric_name in ["system_uptime", "storage_availability"]:
                            compliance_rate = current_avg
                        else:
                            target = metric.target_value
                            compliant_count = sum(1 for m in recent_measurements if m["value"] <= target)
                            compliance_rate = (compliant_count / len(recent_measurements)) * 100
                else:
                    current_avg = metric.current_value
                    avg_health = metric.health_score
                    compliance_rate = 100.0 if metric.current_value >= metric.target_value else 0.0
                
                metrics_data[metric_name] = {
                    "current_value": current_avg,
                    "target_value": metric.target_value,
                    "compliance_rate": compliance_rate,
                    "health_score": avg_health,
                    "unit": metric.unit,
                    "status": "compliant" if compliance_rate >= 95.0 else "violation",
                    "last_updated": metric.last_measurement.isoformat(),
                    "recent_measurements_count": len(recent_measurements)
                }
            
            # Calculate infrastructure health indicators
            infrastructure_health = {
                "total_components": len(self.component_health),
                "healthy_components": len([
                    comp for comp in self.component_health.values()
                    if comp["health_score"] >= 95.0
                ]),
                "total_databases": len(self.database_performance),
                "healthy_databases": len([
                    db for db in self.database_performance.values()
                    if db["health_score"] >= 90.0
                ]),
                "total_storage_systems": len(self.storage_metrics),
                "healthy_storage_systems": len([
                    storage for storage in self.storage_metrics.values()
                    if storage["health_score"] >= 90.0
                ]),
                "network_health": self.network_metrics.get("global", {}).get("health_score", 100.0)
            }
            
            return {
                "timestamp": current_time.isoformat(),
                "metrics": metrics_data,
                "infrastructure_health": infrastructure_health,
                "overall_status": "healthy" if all(m["compliance_rate"] >= 95.0 for m in metrics_data.values()) else "degraded",
                "active_alerts_count": len([a for a in self.alerts if (current_time - datetime.fromisoformat(a["timestamp"])).total_seconds() <= 3600])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting real-time infrastructure metrics: {e}")
            raise

# Global instance for easy access
infrastructure_health_sla = InfrastructureHealthSLA()