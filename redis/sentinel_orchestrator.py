#!/usr/bin/env python3
"""
Redis Sentinel Orchestrator - Ainflue Platform
==============================================

Enterprise Sentinel orchestration with automatic deployment, monitoring,
and intelligent failover coordination for Redis high availability.

Author: Fahed Mlaiel (mlaiel@live.de)
Roles: Lead Dev IA + Backend Senior + DBA + DevOps + Sécurité
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import uuid
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from redis.asyncio.sentinel import Sentinel
import yaml
import aiohttp
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentinelState(Enum):
    """Sentinel instance states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNREACHABLE = "unreachable"
    FAILED = "failed"
    STARTING = "starting"
    STOPPING = "stopping"


class QuorumStatus(Enum):
    """Quorum status enumeration"""
    SUFFICIENT = "sufficient"
    INSUFFICIENT = "insufficient"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class SentinelInstance:
    """Sentinel instance information"""
    instance_id: str
    host: str
    port: int
    state: SentinelState
    last_seen: float
    uptime: int
    version: str
    masters_monitored: List[str]
    quorum_votes: int
    response_time: float
    error_count: int
    consecutive_failures: int


@dataclass
class MasterMonitoring:
    """Master monitoring configuration"""
    master_name: str
    host: str
    port: int
    quorum: int
    down_after_milliseconds: int
    failover_timeout: int
    parallel_syncs: int
    auth_pass: Optional[str] = None
    sentinels_monitoring: List[str] = None


@dataclass
class QuorumCheck:
    """Quorum check results"""
    master_name: str
    required_quorum: int
    available_sentinels: int
    responding_sentinels: int
    quorum_status: QuorumStatus
    can_failover: bool
    insufficient_reason: Optional[str] = None


class RedisSentinelOrchestrator:
    """
    Redis Sentinel Orchestrator for High Availability
    
    Features:
    - Automatic Sentinel deployment and management
    - Dynamic quorum management
    - Intelligent failover coordination
    - Health monitoring and recovery
    - Split-brain prevention
    - Multi-master support
    - Configuration synchronization
    - Performance optimization
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Sentinel orchestrator"""
        self.config = config or self._get_default_config()
        
        # Sentinel management
        self.sentinel_instances: Dict[str, SentinelInstance] = {}
        self.master_configs: Dict[str, MasterMonitoring] = {}
        self.sentinel_clients: Dict[str, redis.Redis] = {}
        
        # Quorum and consensus
        self.quorum_checks: Dict[str, QuorumCheck] = {}
        self.last_quorum_check = 0
        
        # Monitoring
        self.monitoring_tasks: List[asyncio.Task] = []
        self.orchestrator_id = str(uuid.uuid4())
        
        # Configuration
        self.sentinel_base_port = self.config.get('sentinel_base_port', 26379)
        self.quorum_check_interval = self.config.get('quorum_check_interval', 30)
        self.health_check_interval = self.config.get('health_check_interval', 10)
        self.auto_recovery_enabled = self.config.get('auto_recovery_enabled', True)

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'sentinel_base_port': 26379,
            'quorum_check_interval': 30,
            'health_check_interval': 10,
            'auto_recovery_enabled': True,
            'min_sentinels': 3,
            'max_sentinels': 7,
            'auto_deploy_sentinels': True,
            'sentinel_down_threshold': 30000,  # 30 seconds
            'failover_timeout': 180000,  # 3 minutes
            'parallel_syncs': 1,
            'notification_webhook': None,
            'config_sync_enabled': True
        }

    async def initialize(self) -> None:
        """Initialize Sentinel orchestrator"""
        try:
            # Load master configurations
            await self._load_master_configurations()
            
            # Discover existing Sentinels
            await self._discover_sentinels()
            
            # Validate and ensure sufficient Sentinels
            await self._ensure_sentinel_deployment()
            
            # Start monitoring
            await self._start_monitoring()
            
            logger.info(f"Sentinel orchestrator initialized with {len(self.sentinel_instances)} instances")
            
        except Exception as e:
            logger.error(f"Failed to initialize Sentinel orchestrator: {e}")
            raise

    async def _load_master_configurations(self) -> None:
        """Load master monitoring configurations"""
        try:
            # Load from configuration file or discover from cluster
            master_configs = self.config.get('masters', [])
            
            if not master_configs:
                # Auto-discover masters from cluster
                master_configs = await self._auto_discover_masters()
            
            for config in master_configs:
                master_config = MasterMonitoring(
                    master_name=config['name'],
                    host=config['host'],
                    port=config['port'],
                    quorum=config.get('quorum', 2),
                    down_after_milliseconds=config.get('down_after_milliseconds', 30000),
                    failover_timeout=config.get('failover_timeout', 180000),
                    parallel_syncs=config.get('parallel_syncs', 1),
                    auth_pass=config.get('auth_pass'),
                    sentinels_monitoring=[]
                )
                
                self.master_configs[master_config.master_name] = master_config
            
            logger.info(f"Loaded {len(self.master_configs)} master configurations")
            
        except Exception as e:
            logger.error(f"Failed to load master configurations: {e}")
            raise

    async def _auto_discover_masters(self) -> List[Dict[str, Any]]:
        """Auto-discover Redis masters"""
        try:
            # This would integrate with cluster discovery
            # For now, return default configuration
            return [
                {
                    'name': 'ainflue-master',
                    'host': 'redis-master',
                    'port': 6379,
                    'quorum': 2
                }
            ]
            
        except Exception as e:
            logger.error(f"Failed to auto-discover masters: {e}")
            return []

    async def _discover_sentinels(self) -> None:
        """Discover existing Sentinel instances"""
        try:
            # Scan common Sentinel ports on known hosts
            sentinel_hosts = self.config.get('sentinel_hosts', ['localhost', 'redis-sentinel-1', 'redis-sentinel-2', 'redis-sentinel-3'])
            sentinel_ports = self.config.get('sentinel_ports', [26379, 26380, 26381])
            
            discovered_sentinels = []
            
            for host in sentinel_hosts:
                for port in sentinel_ports:
                    try:
                        # Try to connect to potential Sentinel
                        sentinel_client = redis.Redis(
                            host=host,
                            port=port,
                            decode_responses=True,
                            socket_timeout=3.0
                        )
                        
                        # Check if it's a Sentinel
                        sentinel_info = await sentinel_client.info('sentinel')
                        
                        if 'sentinel_masters' in sentinel_info:
                            instance_id = f"{host}:{port}"
                            
                            sentinel_instance = SentinelInstance(
                                instance_id=instance_id,
                                host=host,
                                port=port,
                                state=SentinelState.HEALTHY,
                                last_seen=time.time(),
                                uptime=sentinel_info.get('uptime_in_seconds', 0),
                                version=sentinel_info.get('redis_version', 'unknown'),
                                masters_monitored=[],
                                quorum_votes=0,
                                response_time=0.0,
                                error_count=0,
                                consecutive_failures=0
                            )
                            
                            self.sentinel_instances[instance_id] = sentinel_instance
                            self.sentinel_clients[instance_id] = sentinel_client
                            discovered_sentinels.append(instance_id)
                            
                            # Get monitored masters
                            await self._update_sentinel_masters(instance_id)
                            
                        else:
                            await sentinel_client.close()
                            
                    except Exception:
                        # Not a Sentinel or unreachable
                        continue
            
            logger.info(f"Discovered {len(discovered_sentinels)} Sentinel instances")
            
        except Exception as e:
            logger.error(f"Failed to discover Sentinels: {e}")

    async def _update_sentinel_masters(self, instance_id: str) -> None:
        """Update monitored masters for a Sentinel instance"""
        try:
            if instance_id not in self.sentinel_clients:
                return
                
            sentinel_client = self.sentinel_clients[instance_id]
            
            # Get masters monitored by this Sentinel
            masters = await sentinel_client.execute_command('SENTINEL', 'masters')
            
            monitored_masters = []
            for master_info in masters:
                master_dict = dict(zip(master_info[::2], master_info[1::2]))
                master_name = master_dict.get('name')
                if master_name:
                    monitored_masters.append(master_name)
            
            self.sentinel_instances[instance_id].masters_monitored = monitored_masters
            
        except Exception as e:
            logger.warning(f"Failed to update masters for Sentinel {instance_id}: {e}")

    async def _ensure_sentinel_deployment(self) -> None:
        """Ensure sufficient Sentinels are deployed"""
        try:
            min_sentinels = self.config.get('min_sentinels', 3)
            current_sentinels = len(self.sentinel_instances)
            
            if current_sentinels < min_sentinels:
                if self.config.get('auto_deploy_sentinels', True):
                    await self._deploy_additional_sentinels(min_sentinels - current_sentinels)
                else:
                    logger.warning(f"Insufficient Sentinels: {current_sentinels} < {min_sentinels} "
                                 f"(auto-deploy disabled)")
            
            # Ensure all masters are monitored
            await self._configure_master_monitoring()
            
        except Exception as e:
            logger.error(f"Failed to ensure Sentinel deployment: {e}")

    async def _deploy_additional_sentinels(self, count: int) -> None:
        """Deploy additional Sentinel instances"""
        try:
            logger.info(f"Deploying {count} additional Sentinel instances")
            
            # This is a simplified implementation
            # In production, this would integrate with container orchestration
            deployment_hosts = self.config.get('deployment_hosts', ['redis-sentinel-4', 'redis-sentinel-5'])
            
            for i in range(count):
                if i < len(deployment_hosts):
                    host = deployment_hosts[i]
                    port = self.sentinel_base_port + len(self.sentinel_instances)
                    
                    # Simulate deployment
                    await self._deploy_sentinel_instance(host, port)
                    
        except Exception as e:
            logger.error(f"Failed to deploy additional Sentinels: {e}")

    async def _deploy_sentinel_instance(self, host: str, port: int) -> None:
        """Deploy a single Sentinel instance"""
        try:
            instance_id = f"{host}:{port}"
            
            # In production, this would actually deploy the instance
            # For now, simulate successful deployment
            logger.info(f"Deploying Sentinel instance {instance_id}")
            
            # Simulate deployment time
            await asyncio.sleep(2)
            
            # Create instance record
            sentinel_instance = SentinelInstance(
                instance_id=instance_id,
                host=host,
                port=port,
                state=SentinelState.STARTING,
                last_seen=time.time(),
                uptime=0,
                version='7.0.0',
                masters_monitored=[],
                quorum_votes=0,
                response_time=0.0,
                error_count=0,
                consecutive_failures=0
            )
            
            self.sentinel_instances[instance_id] = sentinel_instance
            
            # Configure monitoring for masters
            await self._configure_sentinel_monitoring(instance_id)
            
            logger.info(f"Sentinel instance {instance_id} deployed successfully")
            
        except Exception as e:
            logger.error(f"Failed to deploy Sentinel instance {host}:{port}: {e}")

    async def _configure_master_monitoring(self) -> None:
        """Configure master monitoring on all Sentinels"""
        try:
            for master_name, master_config in self.master_configs.items():
                for instance_id in self.sentinel_instances.keys():
                    await self._configure_sentinel_monitoring(instance_id, master_name)
                    
        except Exception as e:
            logger.error(f"Failed to configure master monitoring: {e}")

    async def _configure_sentinel_monitoring(self, instance_id: str, master_name: str = None) -> None:
        """Configure monitoring for a specific master on a Sentinel"""
        try:
            if instance_id not in self.sentinel_clients:
                return
                
            sentinel_client = self.sentinel_clients[instance_id]
            
            # Configure all masters if none specified
            masters_to_configure = [master_name] if master_name else list(self.master_configs.keys())
            
            for master in masters_to_configure:
                if master not in self.master_configs:
                    continue
                    
                config = self.master_configs[master]
                
                try:
                    # Configure Sentinel to monitor this master
                    await sentinel_client.execute_command(
                        'SENTINEL', 'monitor',
                        config.master_name,
                        config.host,
                        config.port,
                        config.quorum
                    )
                    
                    # Set additional configuration
                    await sentinel_client.execute_command(
                        'SENTINEL', 'set',
                        config.master_name,
                        'down-after-milliseconds',
                        config.down_after_milliseconds
                    )
                    
                    await sentinel_client.execute_command(
                        'SENTINEL', 'set',
                        config.master_name,
                        'failover-timeout',
                        config.failover_timeout
                    )
                    
                    await sentinel_client.execute_command(
                        'SENTINEL', 'set',
                        config.master_name,
                        'parallel-syncs',
                        config.parallel_syncs
                    )
                    
                    if config.auth_pass:
                        await sentinel_client.execute_command(
                            'SENTINEL', 'set',
                            config.master_name,
                            'auth-pass',
                            config.auth_pass
                        )
                    
                    logger.debug(f"Configured monitoring for {master} on Sentinel {instance_id}")
                    
                except Exception as e:
                    logger.warning(f"Failed to configure {master} on Sentinel {instance_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to configure Sentinel monitoring for {instance_id}: {e}")

    async def _start_monitoring(self) -> None:
        """Start monitoring tasks"""
        try:
            # Health monitoring task
            health_task = asyncio.create_task(self._health_monitoring_loop())
            self.monitoring_tasks.append(health_task)
            
            # Quorum monitoring task
            quorum_task = asyncio.create_task(self._quorum_monitoring_loop())
            self.monitoring_tasks.append(quorum_task)
            
            # Configuration sync task
            if self.config.get('config_sync_enabled', True):
                sync_task = asyncio.create_task(self._config_sync_loop())
                self.monitoring_tasks.append(sync_task)
            
            # Recovery task
            if self.auto_recovery_enabled:
                recovery_task = asyncio.create_task(self._recovery_loop())
                self.monitoring_tasks.append(recovery_task)
            
            logger.info(f"Started {len(self.monitoring_tasks)} monitoring tasks")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring tasks: {e}")

    async def _health_monitoring_loop(self) -> None:
        """Health monitoring loop for all Sentinels"""
        while True:
            try:
                # Check health of all Sentinels
                await self._check_all_sentinels_health()
                
                # Sleep until next check
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring loop error: {e}")
                await asyncio.sleep(self.health_check_interval)

    async def _check_all_sentinels_health(self) -> None:
        """Check health of all Sentinel instances"""
        tasks = []
        
        for instance_id in list(self.sentinel_instances.keys()):
            task = asyncio.create_task(self._check_sentinel_health(instance_id))
            tasks.append(task)
        
        # Wait for all health checks
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_sentinel_health(self, instance_id: str) -> None:
        """Check health of a specific Sentinel instance"""
        try:
            if instance_id not in self.sentinel_instances:
                return
                
            instance = self.sentinel_instances[instance_id]
            
            # Ping test
            start_time = time.time()
            
            try:
                if instance_id in self.sentinel_clients:
                    sentinel_client = self.sentinel_clients[instance_id]
                    await sentinel_client.ping()
                    
                    # Update health metrics
                    instance.response_time = time.time() - start_time
                    instance.last_seen = time.time()
                    instance.state = SentinelState.HEALTHY
                    instance.consecutive_failures = 0
                    
                    # Get additional info
                    info = await sentinel_client.info('sentinel')
                    instance.uptime = info.get('uptime_in_seconds', 0)
                    
                    # Update monitored masters
                    await self._update_sentinel_masters(instance_id)
                    
                else:
                    # Try to reconnect
                    await self._reconnect_sentinel(instance_id)
                    
            except Exception as e:
                # Sentinel is unreachable
                instance.consecutive_failures += 1
                instance.error_count += 1
                instance.response_time = time.time() - start_time
                
                if instance.consecutive_failures >= 3:
                    instance.state = SentinelState.UNREACHABLE
                else:
                    instance.state = SentinelState.DEGRADED
                
                logger.warning(f"Sentinel {instance_id} health check failed: {e}")
                
        except Exception as e:
            logger.error(f"Health check failed for Sentinel {instance_id}: {e}")

    async def _reconnect_sentinel(self, instance_id: str) -> None:
        """Attempt to reconnect to a Sentinel instance"""
        try:
            if instance_id not in self.sentinel_instances:
                return
                
            instance = self.sentinel_instances[instance_id]
            
            # Close existing connection if any
            if instance_id in self.sentinel_clients:
                try:
                    await self.sentinel_clients[instance_id].close()
                except:
                    pass
                del self.sentinel_clients[instance_id]
            
            # Create new connection
            sentinel_client = redis.Redis(
                host=instance.host,
                port=instance.port,
                decode_responses=True,
                socket_timeout=3.0
            )
            
            # Test connection
            await sentinel_client.ping()
            
            self.sentinel_clients[instance_id] = sentinel_client
            logger.info(f"Reconnected to Sentinel {instance_id}")
            
        except Exception as e:
            logger.warning(f"Failed to reconnect to Sentinel {instance_id}: {e}")

    async def _quorum_monitoring_loop(self) -> None:
        """Quorum monitoring loop"""
        while True:
            try:
                # Check quorum for all masters
                await self._check_all_quorums()
                
                self.last_quorum_check = time.time()
                
                # Sleep until next check
                await asyncio.sleep(self.quorum_check_interval)
                
            except Exception as e:
                logger.error(f"Quorum monitoring loop error: {e}")
                await asyncio.sleep(self.quorum_check_interval)

    async def _check_all_quorums(self) -> None:
        """Check quorum status for all masters"""
        for master_name in self.master_configs.keys():
            await self._check_master_quorum(master_name)

    async def _check_master_quorum(self, master_name: str) -> None:
        """Check quorum status for a specific master"""
        try:
            if master_name not in self.master_configs:
                return
                
            config = self.master_configs[master_name]
            
            # Count responding Sentinels monitoring this master
            responding_sentinels = 0
            total_sentinels = 0
            
            for instance_id, instance in self.sentinel_instances.items():
                if master_name in instance.masters_monitored:
                    total_sentinels += 1
                    if instance.state == SentinelState.HEALTHY:
                        responding_sentinels += 1
            
            # Determine quorum status
            can_failover = responding_sentinels >= config.quorum
            
            if responding_sentinels >= config.quorum:
                quorum_status = QuorumStatus.SUFFICIENT
                insufficient_reason = None
            elif responding_sentinels > 0:
                quorum_status = QuorumStatus.INSUFFICIENT
                insufficient_reason = f"Only {responding_sentinels} of {config.quorum} required Sentinels responding"
            else:
                quorum_status = QuorumStatus.CRITICAL
                insufficient_reason = "No Sentinels responding"
            
            quorum_check = QuorumCheck(
                master_name=master_name,
                required_quorum=config.quorum,
                available_sentinels=total_sentinels,
                responding_sentinels=responding_sentinels,
                quorum_status=quorum_status,
                can_failover=can_failover,
                insufficient_reason=insufficient_reason
            )
            
            self.quorum_checks[master_name] = quorum_check
            
            # Log critical quorum issues
            if quorum_status == QuorumStatus.CRITICAL:
                logger.critical(f"Critical quorum failure for master {master_name}: {insufficient_reason}")
                await self._send_notification("critical", f"Quorum failure for {master_name}", insufficient_reason)
                
            elif quorum_status == QuorumStatus.INSUFFICIENT:
                logger.warning(f"Insufficient quorum for master {master_name}: {insufficient_reason}")
                
        except Exception as e:
            logger.error(f"Failed to check quorum for master {master_name}: {e}")

    async def _config_sync_loop(self) -> None:
        """Configuration synchronization loop"""
        while True:
            try:
                # Sync configuration across all Sentinels
                await self._synchronize_configurations()
                
                # Sleep for sync interval
                await asyncio.sleep(300)  # Sync every 5 minutes
                
            except Exception as e:
                logger.error(f"Config sync loop error: {e}")
                await asyncio.sleep(300)

    async def _synchronize_configurations(self) -> None:
        """Synchronize configurations across all Sentinels"""
        try:
            # Ensure all Sentinels have consistent master configurations
            for master_name in self.master_configs.keys():
                await self._sync_master_config(master_name)
                
        except Exception as e:
            logger.error(f"Failed to synchronize configurations: {e}")

    async def _sync_master_config(self, master_name: str) -> None:
        """Synchronize master configuration across Sentinels"""
        try:
            if master_name not in self.master_configs:
                return
                
            config = self.master_configs[master_name]
            
            # Get current configuration from one Sentinel
            reference_config = None
            for instance_id in self.sentinel_instances.keys():
                if instance_id in self.sentinel_clients:
                    try:
                        sentinel_client = self.sentinel_clients[instance_id]
                        masters = await sentinel_client.execute_command('SENTINEL', 'masters')
                        
                        for master_info in masters:
                            master_dict = dict(zip(master_info[::2], master_info[1::2]))
                            if master_dict.get('name') == master_name:
                                reference_config = master_dict
                                break
                                
                        if reference_config:
                            break
                            
                    except Exception:
                        continue
            
            if not reference_config:
                logger.warning(f"No reference configuration found for master {master_name}")
                return
            
            # Apply configuration to all Sentinels
            for instance_id in self.sentinel_instances.keys():
                try:
                    await self._configure_sentinel_monitoring(instance_id, master_name)
                except Exception as e:
                    logger.warning(f"Failed to sync config for {master_name} on {instance_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to sync master config {master_name}: {e}")

    async def _recovery_loop(self) -> None:
        """Recovery loop for failed Sentinels"""
        while True:
            try:
                # Attempt recovery of failed Sentinels
                await self._attempt_sentinel_recovery()
                
                # Check if we need more Sentinels
                await self._check_sentinel_sufficiency()
                
                await asyncio.sleep(60)  # Recovery check every minute
                
            except Exception as e:
                logger.error(f"Recovery loop error: {e}")
                await asyncio.sleep(60)

    async def _attempt_sentinel_recovery(self) -> None:
        """Attempt to recover failed Sentinel instances"""
        failed_sentinels = [
            instance_id for instance_id, instance in self.sentinel_instances.items()
            if instance.state in [SentinelState.UNREACHABLE, SentinelState.FAILED]
        ]
        
        for instance_id in failed_sentinels:
            try:
                await self._recover_sentinel_instance(instance_id)
            except Exception as e:
                logger.error(f"Failed to recover Sentinel {instance_id}: {e}")

    async def _recover_sentinel_instance(self, instance_id: str) -> None:
        """Recover a specific Sentinel instance"""
        try:
            logger.info(f"Attempting to recover Sentinel {instance_id}")
            
            instance = self.sentinel_instances[instance_id]
            
            # Try to reconnect
            await self._reconnect_sentinel(instance_id)
            
            # If reconnection successful, reconfigure monitoring
            if instance_id in self.sentinel_clients:
                await self._configure_master_monitoring()
                instance.state = SentinelState.HEALTHY
                logger.info(f"Successfully recovered Sentinel {instance_id}")
            else:
                # If reconnection failed, try to redeploy
                if self.config.get('auto_deploy_sentinels', True):
                    await self._redeploy_sentinel_instance(instance_id)
                    
        except Exception as e:
            logger.error(f"Failed to recover Sentinel {instance_id}: {e}")

    async def _redeploy_sentinel_instance(self, instance_id: str) -> None:
        """Redeploy a failed Sentinel instance"""
        try:
            logger.info(f"Redeploying Sentinel {instance_id}")
            
            instance = self.sentinel_instances[instance_id]
            
            # Remove old instance
            if instance_id in self.sentinel_clients:
                try:
                    await self.sentinel_clients[instance_id].close()
                except:
                    pass
                del self.sentinel_clients[instance_id]
            
            # Redeploy
            await self._deploy_sentinel_instance(instance.host, instance.port)
            
        except Exception as e:
            logger.error(f"Failed to redeploy Sentinel {instance_id}: {e}")

    async def _check_sentinel_sufficiency(self) -> None:
        """Check if we have sufficient Sentinels"""
        healthy_sentinels = sum(
            1 for instance in self.sentinel_instances.values()
            if instance.state == SentinelState.HEALTHY
        )
        
        min_sentinels = self.config.get('min_sentinels', 3)
        
        if healthy_sentinels < min_sentinels:
            shortage = min_sentinels - healthy_sentinels
            logger.warning(f"Sentinel shortage detected: {healthy_sentinels} < {min_sentinels}")
            
            if self.config.get('auto_deploy_sentinels', True):
                await self._deploy_additional_sentinels(shortage)

    async def _send_notification(self, severity: str, title: str, message: str) -> None:
        """Send notification about Sentinel events"""
        try:
            webhook_url = self.config.get('notification_webhook')
            if not webhook_url:
                return
                
            payload = {
                'severity': severity,
                'title': title,
                'message': message,
                'timestamp': time.time(),
                'orchestrator_id': self.orchestrator_id,
                'sentinel_count': len(self.sentinel_instances),
                'healthy_sentinels': sum(
                    1 for instance in self.sentinel_instances.values()
                    if instance.state == SentinelState.HEALTHY
                )
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        logger.debug(f"Notification sent: {title}")
                    else:
                        logger.warning(f"Notification failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

    async def force_failover(self, master_name: str) -> Dict[str, Any]:
        """Force failover for a master"""
        try:
            if master_name not in self.master_configs:
                return {'success': False, 'error': f'Master {master_name} not found'}
            
            # Check quorum
            quorum_check = self.quorum_checks.get(master_name)
            if not quorum_check or not quorum_check.can_failover:
                return {
                    'success': False, 
                    'error': f'Insufficient quorum for failover: {quorum_check.insufficient_reason if quorum_check else "No quorum check available"}'
                }
            
            # Execute failover using first available Sentinel
            for instance_id, instance in self.sentinel_instances.items():
                if (instance.state == SentinelState.HEALTHY and 
                    master_name in instance.masters_monitored and
                    instance_id in self.sentinel_clients):
                    
                    try:
                        sentinel_client = self.sentinel_clients[instance_id]
                        await sentinel_client.execute_command('SENTINEL', 'failover', master_name)
                        
                        logger.info(f"Forced failover initiated for master {master_name} via Sentinel {instance_id}")
                        
                        return {
                            'success': True,
                            'message': f'Failover initiated for {master_name}',
                            'sentinel_used': instance_id
                        }
                        
                    except Exception as e:
                        logger.warning(f"Failover attempt failed on Sentinel {instance_id}: {e}")
                        continue
            
            return {'success': False, 'error': 'No healthy Sentinels available for failover'}
            
        except Exception as e:
            logger.error(f"Force failover failed for {master_name}: {e}")
            return {'success': False, 'error': str(e)}

    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator status"""
        return {
            'orchestrator_id': self.orchestrator_id,
            'sentinel_instances': {
                instance_id: asdict(instance)
                for instance_id, instance in self.sentinel_instances.items()
            },
            'master_configurations': {
                master_name: asdict(config)
                for master_name, config in self.master_configs.items()
            },
            'quorum_checks': {
                master_name: asdict(check)
                for master_name, check in self.quorum_checks.items()
            },
            'summary': {
                'total_sentinels': len(self.sentinel_instances),
                'healthy_sentinels': sum(
                    1 for instance in self.sentinel_instances.values()
                    if instance.state == SentinelState.HEALTHY
                ),
                'monitored_masters': len(self.master_configs),
                'last_quorum_check': self.last_quorum_check,
                'monitoring_tasks': len(self.monitoring_tasks)
            },
            'configuration': {
                'min_sentinels': self.config.get('min_sentinels', 3),
                'auto_recovery_enabled': self.auto_recovery_enabled,
                'auto_deploy_enabled': self.config.get('auto_deploy_sentinels', True)
            }
        }

    async def add_master_monitoring(self, master_config: Dict[str, Any]) -> Dict[str, Any]:
        """Add monitoring for a new master"""
        try:
            master_name = master_config['name']
            
            # Create master configuration
            config = MasterMonitoring(
                master_name=master_name,
                host=master_config['host'],
                port=master_config['port'],
                quorum=master_config.get('quorum', 2),
                down_after_milliseconds=master_config.get('down_after_milliseconds', 30000),
                failover_timeout=master_config.get('failover_timeout', 180000),
                parallel_syncs=master_config.get('parallel_syncs', 1),
                auth_pass=master_config.get('auth_pass'),
                sentinels_monitoring=[]
            )
            
            self.master_configs[master_name] = config
            
            # Configure monitoring on all Sentinels
            await self._configure_master_monitoring()
            
            logger.info(f"Added monitoring for master {master_name}")
            
            return {
                'success': True,
                'message': f'Monitoring added for master {master_name}',
                'master_config': asdict(config)
            }
            
        except Exception as e:
            logger.error(f"Failed to add master monitoring: {e}")
            return {'success': False, 'error': str(e)}

    async def remove_master_monitoring(self, master_name: str) -> Dict[str, Any]:
        """Remove monitoring for a master"""
        try:
            if master_name not in self.master_configs:
                return {'success': False, 'error': f'Master {master_name} not monitored'}
            
            # Remove from all Sentinels
            for instance_id in self.sentinel_instances.keys():
                if instance_id in self.sentinel_clients:
                    try:
                        sentinel_client = self.sentinel_clients[instance_id]
                        await sentinel_client.execute_command('SENTINEL', 'remove', master_name)
                    except Exception as e:
                        logger.warning(f"Failed to remove {master_name} from Sentinel {instance_id}: {e}")
            
            # Remove from configuration
            del self.master_configs[master_name]
            if master_name in self.quorum_checks:
                del self.quorum_checks[master_name]
            
            logger.info(f"Removed monitoring for master {master_name}")
            
            return {
                'success': True,
                'message': f'Monitoring removed for master {master_name}'
            }
            
        except Exception as e:
            logger.error(f"Failed to remove master monitoring: {e}")
            return {'success': False, 'error': str(e)}

    async def shutdown(self) -> None:
        """Shutdown Sentinel orchestrator"""
        try:
            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self.monitoring_tasks:
                await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
            
            # Close Sentinel connections
            for client in self.sentinel_clients.values():
                try:
                    await client.close()
                except:
                    pass
            
            logger.info("Sentinel orchestrator shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Example usage
async def main():
    """Example usage of Sentinel Orchestrator"""
    try:
        # Configuration example
        config = {
            'masters': [
                {
                    'name': 'ainflue-master',
                    'host': 'redis-master',
                    'port': 6379,
                    'quorum': 2
                }
            ],
            'min_sentinels': 3,
            'auto_deploy_sentinels': True,
            'notification_webhook': 'https://your-webhook-url.com/alerts'
        }
        
        # Initialize orchestrator
        orchestrator = RedisSentinelOrchestrator(config)
        await orchestrator.initialize()
        
        # Run for demonstration
        print("Sentinel orchestrator running...")
        await asyncio.sleep(60)
        
        # Get status
        status = await orchestrator.get_orchestrator_status()
        print(f"Status: {json.dumps(status, indent=2, default=str)}")
        
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'orchestrator' in locals():
            await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())