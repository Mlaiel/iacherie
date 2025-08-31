"""
IA Influencer Agent - Replication Monitor
Real-time data replication monitoring and integrity validation

This module provides comprehensive monitoring of data replication across:
- Multi-cloud storage replication
- Database replication streams
- Content fingerprint synchronization
- Real-time data consistency validation
- Replication lag monitoring and alerting

Author: Fahed Mlaiel <mlaiel@live.de>
License: Proprietary - All rights reserved
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import time
from collections import defaultdict, deque

from backend.core.database import DatabaseManager
from backend.core.config import Config
from backend.utils.metrics import MetricsCollector
from backend.storage.multi_cloud import MultiCloudManager
from backend.security.encryption import EncryptionManager


class ReplicationType(Enum):
    """Types of replication monitoring"""
    DATABASE_MASTER_SLAVE = "database_master_slave"
    DATABASE_MASTER_MASTER = "database_master_master"
    STORAGE_CROSS_REGION = "storage_cross_region"
    STORAGE_CROSS_CLOUD = "storage_cross_cloud"
    CONTENT_FINGERPRINT = "content_fingerprint"
    CONFIGURATION_SYNC = "configuration_sync"
    LOG_STREAMING = "log_streaming"


class ReplicationStatus(Enum):
    """Replication health status"""
    HEALTHY = "healthy"
    LAGGING = "lagging"
    INCONSISTENT = "inconsistent"
    FAILED = "failed"
    RECOVERING = "recovering"
    SUSPENDED = "suspended"


class ConsistencyLevel(Enum):
    """Data consistency levels"""
    EVENTUALLY_CONSISTENT = "eventually_consistent"
    STRONG_CONSISTENCY = "strong_consistency"
    CAUSAL_CONSISTENCY = "causal_consistency"
    MONOTONIC_CONSISTENCY = "monotonic_consistency"


@dataclass
class ReplicationEndpoint:
    """Replication endpoint configuration"""
    endpoint_id: str
    endpoint_type: str  # "master", "slave", "peer"
    location: str
    connection_string: str
    health_check_url: str
    priority: int = 5
    weight: float = 1.0
    encryption_enabled: bool = True
    compression_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplicationStream:
    """Replication stream configuration and state"""
    stream_id: str
    replication_type: ReplicationType
    source_endpoint: ReplicationEndpoint
    target_endpoints: List[ReplicationEndpoint]
    consistency_level: ConsistencyLevel
    max_lag_seconds: int
    check_interval: int
    batch_size: int
    retry_policy: Dict[str, Any]
    status: ReplicationStatus = ReplicationStatus.HEALTHY
    last_sync_time: Optional[datetime] = None
    lag_seconds: float = 0.0
    throughput_mbps: float = 0.0
    error_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsistencyCheck:
    """Data consistency validation record"""
    check_id: str
    stream_id: str
    check_type: str
    source_checksum: str
    target_checksums: Dict[str, str]
    timestamp: datetime
    consistent: bool
    inconsistencies: List[Dict[str, Any]] = field(default_factory=list)
    repair_actions: List[str] = field(default_factory=list)


class ReplicationMonitor:
    """
    Comprehensive replication monitoring and consistency validation system
    
    Features:
    - Real-time replication lag monitoring
    - Multi-endpoint consistency validation
    - Automated data repair and reconciliation
    - Performance metrics and alerting
    - Cross-cloud replication oversight
    - Content fingerprint synchronization tracking
    """

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.db_manager = DatabaseManager(config)
        self.metrics = MetricsCollector()
        self.multi_cloud = MultiCloudManager(config)
        self.encryption_manager = EncryptionManager(config)
        
        # Replication monitoring state
        self.replication_streams: Dict[str, ReplicationStream] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.consistency_history: deque = deque(maxlen=10000)
        
        # Alert thresholds
        self.alert_thresholds = {
            'max_lag_warning': 60,      # seconds
            'max_lag_critical': 300,    # seconds
            'error_rate_warning': 0.01, # 1%
            'error_rate_critical': 0.05, # 5%
            'consistency_warning': 0.95, # 95%
            'consistency_critical': 0.90 # 90%
        }
        
        # Performance tracking
        self.replication_metrics = {
            'total_streams': 0,
            'healthy_streams': 0,
            'average_lag': 0.0,
            'total_throughput': 0.0,
            'consistency_score': 100.0,
            'repair_operations': 0,
            'failed_repairs': 0
        }
        
        # Repair automation
        self.auto_repair_enabled = config.get('replication.auto_repair', True)
        self.repair_strategies = self._initialize_repair_strategies()

    def _initialize_repair_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize automated repair strategies for different inconsistency types"""



        return {
            'missing_record': {
                'strategy': 'copy_from_source',
                'max_attempts': 3,
                'backoff_seconds': 30,
                'validation_required': True
            },
            'checksum_mismatch': {
                'strategy': 'compare_and_merge',
                'max_attempts': 2,
                'backoff_seconds': 60,
                'validation_required': True
            },
            'timestamp_drift': {
                'strategy': 'sync_timestamps',
                'max_attempts': 1,
                'backoff_seconds': 10,
                'validation_required': False
            },
            'schema_mismatch': {
                'strategy': 'manual_intervention',
                'max_attempts': 0,
                'alert_priority': 'critical',
                'validation_required': True
            },
            'encoding_mismatch': {
                'strategy': 're_encode_data',
                'max_attempts': 2,
                'backoff_seconds': 30,
                'validation_required': True
            }
        }

    async def register_replication_stream(self, stream_config: Dict[str, Any]) -> str:
        """
        Register a new replication stream for monitoring
        
        Args:
            stream_config: Replication stream configuration
            
        Returns:
            str: Stream ID
        """



        try:
            # Create source endpoint
            source_config = stream_config['source_endpoint']
            source_endpoint = ReplicationEndpoint(
                endpoint_id=source_config['endpoint_id'],
                endpoint_type=source_config['endpoint_type'],
                location=source_config['location'],
                connection_string=source_config['connection_string'],
                health_check_url=source_config['health_check_url'],
                priority=source_config.get('priority', 5),
                weight=source_config.get('weight', 1.0),
                encryption_enabled=source_config.get('encryption_enabled', True),
                compression_enabled=source_config.get('compression_enabled', True)
            )
            
            # Create target endpoints
            target_endpoints = []
            for target_config in stream_config['target_endpoints']:
                target_endpoint = ReplicationEndpoint(
                    endpoint_id=target_config['endpoint_id'],
                    endpoint_type=target_config['endpoint_type'],
                    location=target_config['location'],
                    connection_string=target_config['connection_string'],
                    health_check_url=target_config['health_check_url'],
                    priority=target_config.get('priority', 5),
                    weight=target_config.get('weight', 1.0),
                    encryption_enabled=target_config.get('encryption_enabled', True),
                    compression_enabled=target_config.get('compression_enabled', True)
                )
                target_endpoints.append(target_endpoint)
            
            # Create replication stream
            stream_id = stream_config.get('stream_id', self._generate_stream_id())
            replication_stream = ReplicationStream(
                stream_id=stream_id,
                replication_type=ReplicationType(stream_config['replication_type']),
                source_endpoint=source_endpoint,
                target_endpoints=target_endpoints,
                consistency_level=ConsistencyLevel(stream_config.get('consistency_level', 'eventually_consistent')),
                max_lag_seconds=stream_config.get('max_lag_seconds', 300),
                check_interval=stream_config.get('check_interval', 30),
                batch_size=stream_config.get('batch_size', 1000),
                retry_policy=stream_config.get('retry_policy', {'max_retries': 3, 'backoff': 'exponential'})
            )
            
            # Register stream
            self.replication_streams[stream_id] = replication_stream
            
            # Start monitoring task
            monitoring_task = asyncio.create_task(
                self._monitor_replication_stream(replication_stream)
            )
            self.monitoring_tasks[stream_id] = monitoring_task
            
            self.logger.info(f"Replication stream {stream_id} registered and monitoring started")
            return stream_id
            
        except Exception as e:
            self.logger.error(f"Failed to register replication stream: {e}")
            raise

    async def _monitor_replication_stream(self, stream: ReplicationStream):
        """Continuously monitor replication stream health and consistency"""
        stream_id = stream.stream_id
        
        while stream_id in self.replication_streams:
            try:
                # Check replication lag
                lag_check = await self._check_replication_lag(stream)
                stream.lag_seconds = lag_check['lag_seconds']
                stream.throughput_mbps = lag_check['throughput_mbps']
                
                # Validate data consistency
                consistency_check = await self._validate_data_consistency(stream)
                
                # Update stream status based on checks
                await self._update_stream_status(stream, lag_check, consistency_check)
                
                # Trigger alerts if thresholds exceeded
                await self._evaluate_alert_conditions(stream, lag_check, consistency_check)
                
                # Attempt automatic repair if enabled and issues detected
                if self.auto_repair_enabled and not consistency_check['consistent']:
                    await self._attempt_automatic_repair(stream, consistency_check)
                
                # Update metrics
                self._update_replication_metrics(stream, lag_check, consistency_check)
                
                # Store consistency check in history
                self.consistency_history.append(consistency_check)
                
                await asyncio.sleep(stream.check_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring error for stream {stream_id}: {e}")
                stream.status = ReplicationStatus.FAILED
                await asyncio.sleep(stream.check_interval)

    async def _check_replication_lag(self, stream: ReplicationStream) -> Dict[str, Any]:
        """Check replication lag for all target endpoints"""
        lag_results = {}
        max_lag = 0.0
        total_throughput = 0.0
        
        try:
            # Get latest timestamp from source
            source_timestamp = await self._get_latest_timestamp(stream.source_endpoint)
            
            for target in stream.target_endpoints:
                target_timestamp = await self._get_latest_timestamp(target)
                
                if source_timestamp and target_timestamp:
                    lag_seconds = (source_timestamp - target_timestamp).total_seconds()
                    lag_results[target.endpoint_id] = {
                        'lag_seconds': max(0, lag_seconds),
                        'source_timestamp': source_timestamp.isoformat(),
                        'target_timestamp': target_timestamp.isoformat()
                    }
                    max_lag = max(max_lag, lag_seconds)
                
                # Calculate throughput
                throughput = await self._calculate_throughput(target, stream.check_interval)
                lag_results[target.endpoint_id]['throughput_mbps'] = throughput
                total_throughput += throughput
            
            return {
                'lag_seconds': max_lag,
                'throughput_mbps': total_throughput,
                'target_results': lag_results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Lag check failed for stream {stream.stream_id}: {e}")
            return {
                'lag_seconds': float('inf'),
                'throughput_mbps': 0.0,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def _validate_data_consistency(self, stream: ReplicationStream) -> Dict[str, Any]:
        """Validate data consistency across all replication endpoints"""
        check_id = f"consistency_{stream.stream_id}_{int(time.time())}"
        
        try:
            # Select sample data for consistency check
            sample_data = await self._select_consistency_sample(stream)
            
            # Calculate checksum for source data
            source_checksum = await self._calculate_data_checksum(
                stream.source_endpoint, 
                sample_data
            )
            
            # Calculate checksums for target endpoints
            target_checksums = {}
            inconsistencies = []
            
            for target in stream.target_endpoints:
                try:
                    target_checksum = await self._calculate_data_checksum(target, sample_data)
                    target_checksums[target.endpoint_id] = target_checksum
                    
                    # Compare with source
                    if target_checksum != source_checksum:
                        inconsistency = await self._analyze_inconsistency(
                            stream.source_endpoint,
                            target,
                            sample_data
                        )
                        inconsistencies.append(inconsistency)
                        
                except Exception as e:
                    self.logger.error(f"Checksum calculation failed for {target.endpoint_id}: {e}")
                    target_checksums[target.endpoint_id] = "ERROR"
                    inconsistencies.append({
                        'target_endpoint': target.endpoint_id,
                        'error': str(e),
                        'type': 'calculation_error'
                    })
            
            # Determine overall consistency
            consistent_targets = sum(1 for checksum in target_checksums.values() 
                                   if checksum == source_checksum and checksum != "ERROR")
            total_targets = len(target_checksums)
            consistency_percentage = (consistent_targets / total_targets * 100) if total_targets > 0 else 0
            
            # Create consistency check record
            consistency_check = ConsistencyCheck(
                check_id=check_id,
                stream_id=stream.stream_id,
                check_type="sample_checksum",
                source_checksum=source_checksum,
                target_checksums=target_checksums,
                timestamp=datetime.utcnow(),
                consistent=len(inconsistencies) == 0,
                inconsistencies=inconsistencies
            )
            
            return {
                'check_id': check_id,
                'consistent': consistency_check.consistent,
                'consistency_percentage': consistency_percentage,
                'inconsistencies': inconsistencies,
                'sample_size': len(sample_data),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Consistency validation failed for stream {stream.stream_id}: {e}")
            return {
                'check_id': check_id,
                'consistent': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def _attempt_automatic_repair(self, stream: ReplicationStream, consistency_check: Dict[str, Any]):
        """Attempt to automatically repair data inconsistencies"""
        if not consistency_check.get('inconsistencies'):
            return
        
        repair_results = []
        
        for inconsistency in consistency_check['inconsistencies']:
            inconsistency_type = inconsistency.get('type', 'unknown')
            
            if inconsistency_type in self.repair_strategies:
                strategy = self.repair_strategies[inconsistency_type]
                
                if strategy['strategy'] == 'manual_intervention':
                    # Alert for manual intervention
                    await self._send_manual_intervention_alert(stream, inconsistency)
                    continue
                
                try:
                    repair_result = await self._execute_repair_strategy(
                        stream, 
                        inconsistency, 
                        strategy
                    )
                    repair_results.append(repair_result)
                    
                    if repair_result['success']:
                        self.replication_metrics['repair_operations'] += 1
                    else:
                        self.replication_metrics['failed_repairs'] += 1
                        
                except Exception as e:
                    self.logger.error(f"Repair failed for inconsistency {inconsistency_type}: {e}")
                    repair_results.append({
                        'inconsistency_type': inconsistency_type,
                        'success': False,
                        'error': str(e)
                    })
                    self.replication_metrics['failed_repairs'] += 1
        
        return repair_results

    async def _execute_repair_strategy(self, stream: ReplicationStream, 
                                     inconsistency: Dict[str, Any], 
                                     strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific repair strategy for an inconsistency"""
        strategy_name = strategy['strategy']
        max_attempts = strategy['max_attempts']
        backoff_seconds = strategy['backoff_seconds']
        
        for attempt in range(max_attempts):
            try:
                if strategy_name == 'copy_from_source':
                    result = await self._repair_copy_from_source(stream, inconsistency)
                elif strategy_name == 'compare_and_merge':
                    result = await self._repair_compare_and_merge(stream, inconsistency)
                elif strategy_name == 'sync_timestamps':
                    result = await self._repair_sync_timestamps(stream, inconsistency)
                elif strategy_name == 're_encode_data':
                    result = await self._repair_re_encode_data(stream, inconsistency)
                else:
                    raise ValueError(f"Unknown repair strategy: {strategy_name}")
                
                if result['success']:
                    # Validate repair if required
                    if strategy.get('validation_required', True):
                        validation_result = await self._validate_repair(stream, inconsistency, result)
                        if validation_result['valid']:
                            return {
                                'strategy': strategy_name,
                                'attempt': attempt + 1,
                                'success': True,
                                'validated': True,
                                'details': result
                            }
                        else:
                            # Repair validation failed, try again
                            await asyncio.sleep(backoff_seconds)
                            continue
                    else:
                        return {
                            'strategy': strategy_name,
                            'attempt': attempt + 1,
                            'success': True,
                            'validated': False,
                            'details': result
                        }
                else:
                    await asyncio.sleep(backoff_seconds)
                    
            except Exception as e:
                self.logger.warning(f"Repair attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(backoff_seconds)
        
        return {
            'strategy': strategy_name,
            'attempts': max_attempts,
            'success': False,
            'error': 'All repair attempts failed'
        }

    async def get_replication_status(self, stream_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive replication status"""
        if stream_id:
            # Get status for specific stream
            if stream_id not in self.replication_streams:
                return {'error': 'Stream not found'}
            
            stream = self.replication_streams[stream_id]
            recent_checks = [
                check for check in self.consistency_history
                if check.get('stream_id') == stream_id
            ][-10:]  # Last 10 checks
            
            return {
                'stream_id': stream_id,
                'status': stream.status.value,
                'replication_type': stream.replication_type.value,
                'lag_seconds': stream.lag_seconds,
                'throughput_mbps': stream.throughput_mbps,
                'error_rate': stream.error_rate,
                'last_sync_time': stream.last_sync_time.isoformat() if stream.last_sync_time else None,
                'source_endpoint': stream.source_endpoint.endpoint_id,
                'target_endpoints': [ep.endpoint_id for ep in stream.target_endpoints],
                'recent_consistency_checks': recent_checks
            }
        else:
            # Get status for all streams
            return {
                'total_streams': len(self.replication_streams),
                'streams': {
                    sid: {
                        'status': stream.status.value,
                        'lag_seconds': stream.lag_seconds,
                        'throughput_mbps': stream.throughput_mbps
                    }
                    for sid, stream in self.replication_streams.items()
                },
                'metrics': self.replication_metrics.copy()
            }

    async def force_consistency_check(self, stream_id: str) -> Dict[str, Any]:
        """Force immediate consistency check for a stream"""
        if stream_id not in self.replication_streams:
            return {'error': 'Stream not found'}
        
        stream = self.replication_streams[stream_id]
        consistency_result = await self._validate_data_consistency(stream)
        
        # Store in history
        self.consistency_history.append(consistency_result)
        
        return consistency_result

    async def suspend_replication(self, stream_id: str) -> bool:
        """Suspend replication monitoring for a stream"""



        try:
            if stream_id in self.replication_streams:
                self.replication_streams[stream_id].status = ReplicationStatus.SUSPENDED
                
                # Cancel monitoring task
                if stream_id in self.monitoring_tasks:
                    self.monitoring_tasks[stream_id].cancel()
                    del self.monitoring_tasks[stream_id]
                
                self.logger.info(f"Replication monitoring suspended for stream {stream_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to suspend replication {stream_id}: {e}")
            return False

    async def resume_replication(self, stream_id: str) -> bool:
        """Resume replication monitoring for a stream"""



        try:
            if stream_id in self.replication_streams:
                stream = self.replication_streams[stream_id]
                stream.status = ReplicationStatus.HEALTHY
                
                # Restart monitoring task
                monitoring_task = asyncio.create_task(
                    self._monitor_replication_stream(stream)
                )
                self.monitoring_tasks[stream_id] = monitoring_task
                
                self.logger.info(f"Replication monitoring resumed for stream {stream_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to resume replication {stream_id}: {e}")
            return False

    def _generate_stream_id(self) -> str:
        """Generate unique stream identifier"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"repl_{timestamp}_{len(self.replication_streams) + 1}"

    def _update_replication_metrics(self, stream: ReplicationStream, 
                                  lag_check: Dict[str, Any], 
                                  consistency_check: Dict[str, Any]):
        """Update aggregated replication metrics"""
        # Update stream counts
        self.replication_metrics['total_streams'] = len(self.replication_streams)
        self.replication_metrics['healthy_streams'] = len([
            s for s in self.replication_streams.values() 
            if s.status == ReplicationStatus.HEALTHY
        ])
        
        # Update average lag
        total_lag = sum(s.lag_seconds for s in self.replication_streams.values())
        stream_count = len(self.replication_streams)
        self.replication_metrics['average_lag'] = total_lag / stream_count if stream_count > 0 else 0
        
        # Update total throughput
        self.replication_metrics['total_throughput'] = sum(
            s.throughput_mbps for s in self.replication_streams.values()
        )
        
        # Update consistency score
        recent_checks = list(self.consistency_history)[-100:]  # Last 100 checks
        if recent_checks:
            consistent_checks = sum(1 for check in recent_checks if check.get('consistent', False))
            self.replication_metrics['consistency_score'] = (consistent_checks / len(recent_checks)) * 100
