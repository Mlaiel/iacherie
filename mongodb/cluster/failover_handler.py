"""MongoDB Failover Handler
========================

Intelligent automatic failover and disaster recovery system for MongoDB clusters
in the Ainflue platform enterprise infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

try:
    import pymongo
    from pymongo import MongoClient
    from pymongo.errors import ServerSelectionTimeoutError, NetworkTimeout
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

from . import ClusterState, ClusterStatus

logger = logging.getLogger(__name__)

class FailoverTrigger(Enum):
    """Failover trigger types."""
    PRIMARY_DOWN = "primary_down"
    NETWORK_PARTITION = "network_partition"
    HIGH_LATENCY = "high_latency"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    MANUAL = "manual"

@dataclass
class FailoverEvent:
    """Failover event information."""
    event_id: str
    trigger: FailoverTrigger
    timestamp: datetime
    old_primary: Optional[str]
    new_primary: Optional[str]
    duration_seconds: float
    affected_connections: int
    recovery_time_seconds: float

class FailoverHandler:
    """Enterprise-grade automatic failover and recovery system."""
    
    def __init__(self, connection_string: str, replica_set_name: str):
        """Initialize failover handler."""
        if not MONGODB_AVAILABLE:
            raise ImportError("PyMongo is required for failover handling")
            
        self.connection_string = connection_string
        self.replica_set_name = replica_set_name
        self.client = None
        self.monitoring_active = False
        self.failover_callbacks: List[Callable] = []
        
        # Configuration
        self.health_check_interval = 10  # seconds
        self.failover_timeout = 120  # seconds
        self.max_latency_threshold = 1000  # milliseconds
        self.retry_attempts = 3
        self.retry_delay = 5  # seconds
        
        # State tracking
        self.last_known_primary = None
        self.failover_in_progress = False
        self.failover_history: List[FailoverEvent] = []
    
    async def start_monitoring(self):
        """Start continuous cluster health monitoring."""
        self.monitoring_active = True
        logger.info("Starting cluster health monitoring")
        
        while self.monitoring_active:
            try:
                await self._check_cluster_health()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    def stop_monitoring(self):
        """Stop cluster health monitoring."""
        self.monitoring_active = False
        logger.info("Stopped cluster health monitoring")
    
    def add_failover_callback(self, callback: Callable[[FailoverEvent], None]):
        """Add callback function to be executed on failover events."""
        self.failover_callbacks.append(callback)
    
    async def _check_cluster_health(self):
        """Perform comprehensive cluster health check."""
        try:
            if not self.client:
                self.client = MongoClient(
                    self.connection_string,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000
                )
            
            # Get replica set status
            status = self.client.admin.command("replSetGetStatus")
            current_primary = self._find_primary(status)
            
            # Check for primary changes
            if current_primary != self.last_known_primary:
                if self.last_known_primary is not None:
                    await self._handle_primary_change(self.last_known_primary, current_primary)
                self.last_known_primary = current_primary
            
            # Check for cluster health issues
            await self._check_for_issues(status)
            
        except ServerSelectionTimeoutError:
            logger.warning("Server selection timeout - checking for network partition")
            await self._handle_network_issues()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            await self._handle_connection_failure()
    
    async def _handle_primary_change(self, old_primary: Optional[str], new_primary: Optional[str]):
        """Handle primary node changes."""
        if not new_primary:
            logger.critical("No primary node available - cluster in critical state")
            await self._trigger_failover(FailoverTrigger.PRIMARY_DOWN, old_primary, None)
            return
        
        if old_primary and new_primary != old_primary:
            logger.warning(f"Primary changed from {old_primary} to {new_primary}")
            
            # Determine if this was planned or unplanned
            trigger = await self._determine_failover_cause(old_primary, new_primary)
            await self._trigger_failover(trigger, old_primary, new_primary)
    
    async def _check_for_issues(self, status: Dict[str, Any]):
        """Check for various cluster issues that might require intervention."""
        # Check replication lag
        max_lag = self._calculate_max_replication_lag(status)
        if max_lag > self.max_latency_threshold:
            logger.warning(f"High replication lag detected: {max_lag}ms")
            
            # Consider triggering failover if lag is excessive
            if max_lag > self.max_latency_threshold * 5:
                primary = self._find_primary(status)
                await self._trigger_failover(FailoverTrigger.HIGH_LATENCY, primary, None)
        
        # Check member health
        unhealthy_members = self._find_unhealthy_members(status)
        if unhealthy_members:
            logger.warning(f"Unhealthy members detected: {unhealthy_members}")
        
        # Check for network partitions
        if self._detect_network_partition(status):
            logger.critical("Network partition detected")
            primary = self._find_primary(status)
            await self._trigger_failover(FailoverTrigger.NETWORK_PARTITION, primary, None)
    
    async def _trigger_failover(self, 
                               trigger: FailoverTrigger, 
                               old_primary: Optional[str], 
                               new_primary: Optional[str]):
        """Trigger failover process."""
        if self.failover_in_progress:
            logger.info("Failover already in progress, skipping")
            return
        
        self.failover_in_progress = True
        start_time = datetime.now()
        
        try:
            logger.critical(f"Triggering failover - Cause: {trigger.value}")
            
            # Create failover event
            event = FailoverEvent(
                event_id=f"fo_{int(start_time.timestamp())}",
                trigger=trigger,
                timestamp=start_time,
                old_primary=old_primary,
                new_primary=new_primary,
                duration_seconds=0,
                affected_connections=0,
                recovery_time_seconds=0
            )
            
            # Execute failover steps
            recovery_start = datetime.now()
            
            if trigger == FailoverTrigger.PRIMARY_DOWN:
                await self._handle_primary_failure()
            elif trigger == FailoverTrigger.NETWORK_PARTITION:
                await self._handle_network_partition()
            elif trigger == FailoverTrigger.HIGH_LATENCY:
                await self._handle_performance_issue()
            
            # Wait for new primary election
            new_primary = await self._wait_for_new_primary()
            
            recovery_end = datetime.now()
            
            # Update event with results
            event.new_primary = new_primary
            event.duration_seconds = (datetime.now() - start_time).total_seconds()
            event.recovery_time_seconds = (recovery_end - recovery_start).total_seconds()
            
            # Record event
            self.failover_history.append(event)
            
            # Notify callbacks
            for callback in self.failover_callbacks:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Failover callback failed: {e}")
            
            logger.info(f"Failover completed - New primary: {new_primary}")
            
        except Exception as e:
            logger.error(f"Failover process failed: {e}")
        finally:
            self.failover_in_progress = False
    
    async def _handle_primary_failure(self):
        """Handle primary node failure."""
        logger.info("Handling primary node failure")
        
        # Force step down if primary is still responsive
        try:
            if self.client:
                self.client.admin.command("replSetStepDown", 60, force=True)
        except:
            pass  # Primary might already be down
        
        # Trigger priority-based election
        await self._trigger_election()
    
    async def _handle_network_partition(self):
        """Handle network partition scenarios."""
        logger.info("Handling network partition")
        
        # Implement partition detection and recovery logic
        # This might involve checking multiple connection paths
        await self._attempt_reconnection()
    
    async def _handle_performance_issue(self):
        """Handle performance-related failover."""
        logger.info("Handling performance issue")
        
        # Force primary step down to allow a healthier secondary to take over
        try:
            if self.client:
                self.client.admin.command("replSetStepDown", 30)
        except Exception as e:
            logger.error(f"Failed to step down primary: {e}")
    
    async def _wait_for_new_primary(self, timeout: int = None) -> Optional[str]:
        """Wait for a new primary to be elected."""
        if timeout is None:
            timeout = self.failover_timeout
            
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            try:
                if self.client:
                    status = self.client.admin.command("replSetGetStatus")
                    primary = self._find_primary(status)
                    if primary:
                        return primary
            except:
                pass
            
            await asyncio.sleep(2)
        
        logger.error("Timeout waiting for new primary election")
        return None
    
    async def _trigger_election(self):
        """Trigger a new primary election."""
        try:
            # This would implement custom election logic if needed
            # For now, rely on MongoDB's automatic election process
            logger.info("Waiting for automatic primary election")
        except Exception as e:
            logger.error(f"Failed to trigger election: {e}")
    
    async def _attempt_reconnection(self):
        """Attempt to reconnect to the cluster."""
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Reconnection attempt {attempt + 1}/{self.retry_attempts}")
                
                if self.client:
                    self.client.close()
                
                self.client = MongoClient(
                    self.connection_string,
                    serverSelectionTimeoutMS=10000
                )
                
                # Test connection
                self.client.admin.command("isMaster")
                logger.info("Reconnection successful")
                return True
                
            except Exception as e:
                logger.warning(f"Reconnection attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay)
        
        logger.error("All reconnection attempts failed")
        return False
    
    async def _handle_network_issues(self):
        """Handle network connectivity issues."""
        logger.warning("Handling network issues")
        await self._attempt_reconnection()
    
    async def _handle_connection_failure(self):
        """Handle general connection failures."""
        logger.warning("Handling connection failure")
        await self._attempt_reconnection()
    
    async def _determine_failover_cause(self, old_primary: str, new_primary: str) -> FailoverTrigger:
        """Determine the cause of a failover event."""
        # Implement logic to determine if failover was planned or due to failure
        # This could check logs, timing, or other indicators
        return FailoverTrigger.PRIMARY_DOWN
    
    def _find_primary(self, status: Dict[str, Any]) -> Optional[str]:
        """Find the current primary node."""
        for member in status.get("members", []):
            if member.get("stateStr") == "PRIMARY":
                return member.get("name")
        return None
    
    def _calculate_max_replication_lag(self, status: Dict[str, Any]) -> int:
        """Calculate maximum replication lag in milliseconds."""
        primary_optime = None
        max_lag = 0
        
        # Find primary optime
        for member in status.get("members", []):
            if member.get("stateStr") == "PRIMARY":
                primary_optime = member.get("optimeDate")
                break
        
        if not primary_optime:
            return 0
        
        # Calculate lag for each secondary
        for member in status.get("members", []):
            if member.get("stateStr") == "SECONDARY":
                member_optime = member.get("optimeDate")
                if member_optime:
                    lag_ms = int((primary_optime - member_optime).total_seconds() * 1000)
                    max_lag = max(max_lag, lag_ms)
        
        return max_lag
    
    def _find_unhealthy_members(self, status: Dict[str, Any]) -> List[str]:
        """Find members that are in an unhealthy state."""
        unhealthy = []
        healthy_states = ["PRIMARY", "SECONDARY", "ARBITER"]
        
        for member in status.get("members", []):
            if (member.get("stateStr") not in healthy_states or 
                member.get("health", 0) != 1):
                unhealthy.append(member.get("name", "unknown"))
        
        return unhealthy
    
    def _detect_network_partition(self, status: Dict[str, Any]) -> bool:
        """Detect if there's a network partition."""
        total_members = len(status.get("members", []))
        visible_members = len([m for m in status.get("members", []) 
                              if m.get("health", 0) == 1])
        
        # Simple partition detection: if less than majority is visible
        return visible_members < (total_members // 2) + 1
    
    def get_failover_history(self, limit: int = 10) -> List[FailoverEvent]:
        """Get recent failover history."""
        return self.failover_history[-limit:]
    
    def get_failover_statistics(self) -> Dict[str, Any]:
        """Get failover statistics."""
        if not self.failover_history:
            return {}
        
        total_events = len(self.failover_history)
        avg_duration = sum(e.duration_seconds for e in self.failover_history) / total_events
        avg_recovery = sum(e.recovery_time_seconds for e in self.failover_history) / total_events
        
        trigger_counts = {}
        for event in self.failover_history:
            trigger = event.trigger.value
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        return {
            "total_failovers": total_events,
            "average_duration_seconds": avg_duration,
            "average_recovery_seconds": avg_recovery,
            "triggers": trigger_counts,
            "last_failover": self.failover_history[-1].timestamp if self.failover_history else None
        }
    
    def close(self):
        """Close database connections and stop monitoring."""
        self.stop_monitoring()
        if self.client:
            self.client.close()

# Export the main class
__all__ = ['FailoverHandler', 'FailoverEvent', 'FailoverTrigger']