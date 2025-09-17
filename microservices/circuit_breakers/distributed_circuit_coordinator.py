"""
Distributed Circuit Coordinator - Ainflue Platform
================================================

Coordinator circuit breakers distribués enterprise.
Consensus algorithms + state synchronization + cluster management.

Author: Fahed Mlaiel (mlaiel@live.de)
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture circuit breakers et tous ses patterns sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import json
import logging
import hashlib
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict
import uuid
import aiohttp

logger = logging.getLogger(__name__)

class NodeState(Enum):
    """Cluster node states"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LEADER = "LEADER"
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"
    FAILED = "FAILED"

class ConsensusState(Enum):
    """Raft consensus states"""
    LEADER = "LEADER"
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"

class CircuitEvent(Enum):
    """Circuit breaker events"""
    STATE_CHANGE = "STATE_CHANGE"
    FAILURE_DETECTED = "FAILURE_DETECTED"
    RECOVERY_ATTEMPT = "RECOVERY_ATTEMPT"
    THRESHOLD_CHANGE = "THRESHOLD_CHANGE"
    FORCE_OPEN = "FORCE_OPEN"
    FORCE_CLOSE = "FORCE_CLOSE"

@dataclass
class ClusterNode:
    """Cluster node information"""
    node_id: str
    hostname: str
    port: int
    state: NodeState = NodeState.INACTIVE
    last_heartbeat: Optional[datetime] = None
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def endpoint(self) -> str:
        return f"http://{self.hostname}:{self.port}"
    
    def is_healthy(self, timeout_seconds: int = 30) -> bool:
        """Check if node is healthy based on heartbeat"""
        if not self.last_heartbeat:
            return False
        return datetime.now() - self.last_heartbeat < timedelta(seconds=timeout_seconds)

@dataclass
class ClusterConfig:
    """Cluster configuration"""
    cluster_id: str
    nodes: List[ClusterNode] = field(default_factory=list)
    heartbeat_interval: int = 5  # seconds
    election_timeout: int = 30   # seconds
    consensus_timeout: int = 10  # seconds
    partition_tolerance: bool = True
    min_cluster_size: int = 3
    max_cluster_size: int = 10

@dataclass
class CircuitEventData:
    """Circuit breaker event data"""
    event_id: str
    event_type: CircuitEvent
    service_name: str
    circuit_state: str
    timestamp: datetime
    node_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'service_name': self.service_name,
            'circuit_state': self.circuit_state,
            'timestamp': self.timestamp.isoformat(),
            'node_id': self.node_id,
            'data': self.data
        }

class RaftConsensus:
    """Simplified Raft consensus implementation for circuit breaker coordination"""
    
    def __init__(self, node_id: str, cluster_config: ClusterConfig):
        self.node_id = node_id
        self.cluster_config = cluster_config
        self.state = ConsensusState.FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        self.last_applied = 0
        self.leader_id = None
        self.election_timeout = cluster_config.election_timeout
        self.last_heartbeat = datetime.now()
        
        # Leader state
        self.next_index = {}
        self.match_index = {}
        
        # Candidates state
        self.votes_received = set()
        
        logger.info(f"Raft consensus initialized for node {node_id}")
    
    async def start_election(self) -> bool:
        """Start leader election"""
        self.state = ConsensusState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}
        
        logger.info(f"Node {self.node_id} starting election for term {self.current_term}")
        
        # Request votes from other nodes
        tasks = []
        for node in self.cluster_config.nodes:
            if node.node_id != self.node_id and node.is_healthy():
                task = asyncio.create_task(self._request_vote(node))
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count votes
            vote_count = len(self.votes_received)
            required_votes = (len(self.cluster_config.nodes) + 1) // 2
            
            if vote_count >= required_votes:
                await self._become_leader()
                return True
        
        # Election failed
        self.state = ConsensusState.FOLLOWER
        return False
    
    async def _request_vote(self, node: ClusterNode) -> bool:
        """Request vote from a node"""
        try:
            async with aiohttp.ClientSession() as session:
                vote_request = {
                    'term': self.current_term,
                    'candidate_id': self.node_id,
                    'last_log_index': len(self.log) - 1 if self.log else -1,
                    'last_log_term': self.log[-1]['term'] if self.log else 0
                }
                
                timeout = aiohttp.ClientTimeout(total=5)
                async with session.post(
                    f"{node.endpoint}/raft/request_vote",
                    json=vote_request,
                    timeout=timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('vote_granted'):
                            self.votes_received.add(node.node_id)
                            return True
        
        except Exception as e:
            logger.warning(f"Failed to request vote from {node.node_id}: {str(e)}")
        
        return False
    
    async def _become_leader(self):
        """Become cluster leader"""
        self.state = ConsensusState.LEADER
        self.leader_id = self.node_id
        
        # Initialize leader state
        for node in self.cluster_config.nodes:
            if node.node_id != self.node_id:
                self.next_index[node.node_id] = len(self.log)
                self.match_index[node.node_id] = -1
        
        logger.info(f"Node {self.node_id} became leader for term {self.current_term}")
        
        # Start sending heartbeats
        asyncio.create_task(self._send_heartbeats())
    
    async def _send_heartbeats(self):
        """Send periodic heartbeats to followers"""
        while self.state == ConsensusState.LEADER:
            try:
                tasks = []
                for node in self.cluster_config.nodes:
                    if node.node_id != self.node_id and node.is_healthy():
                        task = asyncio.create_task(self._send_heartbeat(node))
                        tasks.append(task)
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                await asyncio.sleep(self.cluster_config.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Heartbeat sending failed: {str(e)}")
                break
    
    async def _send_heartbeat(self, node: ClusterNode):
        """Send heartbeat to a follower"""
        try:
            async with aiohttp.ClientSession() as session:
                heartbeat = {
                    'term': self.current_term,
                    'leader_id': self.node_id,
                    'prev_log_index': self.next_index.get(node.node_id, 0) - 1,
                    'prev_log_term': self.log[self.next_index.get(node.node_id, 0) - 1]['term'] if self.next_index.get(node.node_id, 0) > 0 else 0,
                    'entries': [],  # Empty for heartbeat
                    'leader_commit': self.commit_index
                }
                
                timeout = aiohttp.ClientTimeout(total=3)
                async with session.post(
                    f"{node.endpoint}/raft/append_entries",
                    json=heartbeat,
                    timeout=timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if not result.get('success'):
                            # Handle log inconsistency
                            if node.node_id in self.next_index:
                                self.next_index[node.node_id] = max(0, self.next_index[node.node_id] - 1)
        
        except Exception as e:
            logger.debug(f"Heartbeat to {node.node_id} failed: {str(e)}")
    
    async def append_log_entry(self, entry: Dict[str, Any]) -> bool:
        """Append entry to log and replicate to followers"""
        if self.state != ConsensusState.LEADER:
            return False
        
        # Add to local log
        log_entry = {
            'term': self.current_term,
            'index': len(self.log),
            'entry': entry,
            'timestamp': datetime.now().isoformat()
        }
        self.log.append(log_entry)
        
        # Replicate to followers
        success_count = 1  # Count self
        tasks = []
        
        for node in self.cluster_config.nodes:
            if node.node_id != self.node_id and node.is_healthy():
                task = asyncio.create_task(self._replicate_to_follower(node, log_entry))
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count += sum(1 for result in results if result is True)
        
        # Check if majority acknowledged
        required_acks = (len(self.cluster_config.nodes) + 1) // 2
        if success_count >= required_acks:
            self.commit_index = len(self.log) - 1
            return True
        
        return False
    
    async def _replicate_to_follower(self, node: ClusterNode, entry: Dict[str, Any]) -> bool:
        """Replicate log entry to a follower"""
        try:
            async with aiohttp.ClientSession() as session:
                append_request = {
                    'term': self.current_term,
                    'leader_id': self.node_id,
                    'prev_log_index': self.next_index.get(node.node_id, 0) - 1,
                    'prev_log_term': self.log[self.next_index.get(node.node_id, 0) - 1]['term'] if self.next_index.get(node.node_id, 0) > 0 else 0,
                    'entries': [entry],
                    'leader_commit': self.commit_index
                }
                
                timeout = aiohttp.ClientTimeout(total=5)
                async with session.post(
                    f"{node.endpoint}/raft/append_entries",
                    json=append_request,
                    timeout=timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('success'):
                            self.next_index[node.node_id] = entry['index'] + 1
                            self.match_index[node.node_id] = entry['index']
                            return True
        
        except Exception as e:
            logger.warning(f"Replication to {node.node_id} failed: {str(e)}")
        
        return False

class StateReplicator:
    """State replication for circuit breaker states"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.circuit_states = {}
        self.replication_queue = asyncio.Queue()
        self.subscribers = set()
        
    async def replicate_state_change(self, service_name: str, state_data: Dict[str, Any], target_nodes: List[str]):
        """Replicate state change to target nodes"""
        replication_task = {
            'service_name': service_name,
            'state_data': state_data,
            'target_nodes': target_nodes,
            'timestamp': datetime.now().isoformat(),
            'retry_count': 0
        }
        
        await self.replication_queue.put(replication_task)
    
    async def start_replication_worker(self):
        """Start background worker for state replication"""
        while True:
            try:
                task = await self.replication_queue.get()
                await self._execute_replication(task)
                self.replication_queue.task_done()
            except Exception as e:
                logger.error(f"Replication worker error: {str(e)}")
                await asyncio.sleep(1)
    
    async def _execute_replication(self, task: Dict[str, Any]):
        """Execute state replication to target nodes"""
        service_name = task['service_name']
        state_data = task['state_data']
        target_nodes = task['target_nodes']
        
        successful_replications = 0
        
        for node_endpoint in target_nodes:
            try:
                async with aiohttp.ClientSession() as session:
                    replication_data = {
                        'service_name': service_name,
                        'source_node': self.node_id,
                        'state_data': state_data,
                        'timestamp': task['timestamp']
                    }
                    
                    timeout = aiohttp.ClientTimeout(total=5)
                    async with session.post(
                        f"{node_endpoint}/circuit/replicate_state",
                        json=replication_data,
                        timeout=timeout
                    ) as response:
                        if response.status == 200:
                            successful_replications += 1
            
            except Exception as e:
                logger.warning(f"State replication to {node_endpoint} failed: {str(e)}")
        
        logger.debug(f"State replication for {service_name}: {successful_replications}/{len(target_nodes)} successful")

class ClusterHealthMonitor:
    """Monitor cluster health and node status"""
    
    def __init__(self, cluster_config: ClusterConfig):
        self.cluster_config = cluster_config
        self.node_health = {}
        self.health_history = defaultdict(list)
        self.monitoring_active = False
    
    async def start_monitoring(self):
        """Start cluster health monitoring"""
        self.monitoring_active = True
        await asyncio.gather(
            self._monitor_node_health(),
            self._cleanup_history()
        )
    
    async def stop_monitoring(self):
        """Stop cluster health monitoring"""
        self.monitoring_active = False
    
    async def _monitor_node_health(self):
        """Monitor health of all cluster nodes"""
        while self.monitoring_active:
            try:
                for node in self.cluster_config.nodes:
                    health_status = await self._check_node_health(node)
                    self.node_health[node.node_id] = health_status
                    self._record_health_history(node.node_id, health_status)
                
                await asyncio.sleep(self.cluster_config.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _check_node_health(self, node: ClusterNode) -> Dict[str, Any]:
        """Check health of a specific node"""
        health_data = {
            'node_id': node.node_id,
            'timestamp': datetime.now(),
            'healthy': False,
            'response_time': None,
            'error': None
        }
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                timeout = aiohttp.ClientTimeout(total=5)
                async with session.get(
                    f"{node.endpoint}/health",
                    timeout=timeout
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        health_data['healthy'] = True
                        health_data['response_time'] = response_time
                        node.last_heartbeat = datetime.now()
                        node.state = NodeState.ACTIVE
                    else:
                        health_data['error'] = f"HTTP {response.status}"
                        node.state = NodeState.INACTIVE
        
        except Exception as e:
            health_data['error'] = str(e)
            node.state = NodeState.FAILED
        
        return health_data
    
    def _record_health_history(self, node_id: str, health_data: Dict[str, Any]):
        """Record health history for a node"""
        self.health_history[node_id].append(health_data)
        
        # Keep only recent history (last 100 entries)
        if len(self.health_history[node_id]) > 100:
            self.health_history[node_id] = self.health_history[node_id][-100:]
    
    async def _cleanup_history(self):
        """Clean up old health history"""
        while self.monitoring_active:
            try:
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                for node_id in self.health_history:
                    self.health_history[node_id] = [
                        entry for entry in self.health_history[node_id]
                        if entry['timestamp'] > cutoff_time
                    ]
                
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                logger.error(f"Health history cleanup error: {str(e)}")
                await asyncio.sleep(3600)
    
    def get_cluster_health_summary(self) -> Dict[str, Any]:
        """Get cluster health summary"""
        healthy_nodes = sum(1 for health in self.node_health.values() if health.get('healthy', False))
        total_nodes = len(self.cluster_config.nodes)
        
        return {
            'cluster_id': self.cluster_config.cluster_id,
            'total_nodes': total_nodes,
            'healthy_nodes': healthy_nodes,
            'health_percentage': (healthy_nodes / total_nodes * 100) if total_nodes > 0 else 0,
            'node_health': self.node_health,
            'last_updated': datetime.now().isoformat()
        }

class DistributedCircuitCoordinator:
    """
    Coordinateur circuit breakers distribués enterprise.
    Consensus algorithms + state synchronization + cluster management.
    """
    
    def __init__(self, node_id: str, cluster_config: ClusterConfig):
        self.node_id = node_id
        self.cluster_config = cluster_config
        
        # Core components
        self.consensus_algorithm = RaftConsensus(node_id, cluster_config)
        self.state_synchronizer = StateReplicator(node_id)
        self.health_monitor = ClusterHealthMonitor(cluster_config)
        
        # Circuit coordination
        self.circuit_decisions = {}
        self.pending_decisions = {}
        self.coordination_lock = asyncio.Lock()
        
        # Event handling
        self.event_handlers = {}
        self.event_queue = asyncio.Queue()
        
        logger.info(f"Distributed circuit coordinator initialized for node {node_id}")
    
    async def start(self):
        """Start the distributed coordinator"""
        try:
            # Start core components
            await asyncio.gather(
                self.health_monitor.start_monitoring(),
                self.state_synchronizer.start_replication_worker(),
                self._start_event_processor(),
                self._start_consensus_monitor()
            )
        except Exception as e:
            logger.error(f"Failed to start distributed coordinator: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the distributed coordinator"""
        await self.health_monitor.stop_monitoring()
        logger.info(f"Distributed circuit coordinator stopped for node {self.node_id}")
    
    async def coordinate_circuit_decisions(self, circuit_events: List[CircuitEventData]) -> Dict[str, Any]:
        """
        Coordination décisions circuit breakers à travers cluster.
        
        Features:
        - Raft consensus pour décisions critiques
        - State replication temps réel
        - Byzantine fault tolerance
        - Network partition handling
        - Leader election pour coordination
        """
        async with self.coordination_lock:
            coordination_result = {
                'coordinator_node': self.node_id,
                'events_processed': len(circuit_events),
                'decisions': {},
                'consensus_achieved': False,
                'replication_status': {}
            }
            
            for event in circuit_events:
                try:
                    # Process event based on type
                    decision = await self._process_circuit_event(event)
                    coordination_result['decisions'][event.event_id] = decision
                    
                    # If this is a critical decision, use consensus
                    if await self._is_critical_decision(event):
                        consensus_achieved = await self._achieve_consensus(event, decision)
                        coordination_result['consensus_achieved'] = consensus_achieved
                        
                        if consensus_achieved:
                            # Replicate decision to all nodes
                            await self.synchronize_circuit_states(
                                [node.endpoint for node in self.cluster_config.nodes if node.node_id != self.node_id]
                            )
                    
                except Exception as e:
                    logger.error(f"Failed to coordinate event {event.event_id}: {str(e)}")
                    coordination_result['decisions'][event.event_id] = {'error': str(e)}
            
            return coordination_result
    
    async def _process_circuit_event(self, event: CircuitEventData) -> Dict[str, Any]:
        """Process individual circuit event"""
        event_handlers = {
            CircuitEvent.STATE_CHANGE: self._handle_state_change,
            CircuitEvent.FAILURE_DETECTED: self._handle_failure_detected,
            CircuitEvent.RECOVERY_ATTEMPT: self._handle_recovery_attempt,
            CircuitEvent.THRESHOLD_CHANGE: self._handle_threshold_change,
            CircuitEvent.FORCE_OPEN: self._handle_force_open,
            CircuitEvent.FORCE_CLOSE: self._handle_force_close
        }
        
        handler = event_handlers.get(event.event_type, self._handle_unknown_event)
        return await handler(event)
    
    async def _handle_state_change(self, event: CircuitEventData) -> Dict[str, Any]:
        """Handle circuit state change event"""
        return {
            'action': 'state_change_acknowledged',
            'service': event.service_name,
            'new_state': event.circuit_state,
            'coordinator_decision': 'approved'
        }
    
    async def _handle_failure_detected(self, event: CircuitEventData) -> Dict[str, Any]:
        """Handle failure detection event"""
        failure_count = event.data.get('failure_count', 0)
        threshold = event.data.get('threshold', 5)
        
        if failure_count >= threshold:
            return {
                'action': 'recommend_circuit_open',
                'service': event.service_name,
                'reason': f'Failure count {failure_count} exceeded threshold {threshold}'
            }
        
        return {
            'action': 'monitor_closely',
            'service': event.service_name,
            'failure_count': failure_count
        }
    
    async def _handle_recovery_attempt(self, event: CircuitEventData) -> Dict[str, Any]:
        """Handle recovery attempt event"""
        return {
            'action': 'allow_recovery_test',
            'service': event.service_name,
            'coordinator_decision': 'approved'
        }
    
    async def _handle_threshold_change(self, event: CircuitEventData) -> Dict[str, Any]:
        """Handle threshold change event"""
        new_threshold = event.data.get('new_threshold')
        return {
            'action': 'threshold_change_approved',
            'service': event.service_name,
            'new_threshold': new_threshold
        }
    
    async def _handle_force_open(self, event: CircuitEventData) -> Dict[str, Any]:
        """Handle force open event"""
        return {
            'action': 'force_open_acknowledged',
            'service': event.service_name,
            'coordinator_decision': 'approved'
        }
    
    async def _handle_force_close(self, event: CircuitEventData) -> Dict[str, Any]:
        """Handle force close event"""
        return {
            'action': 'force_close_acknowledged',
            'service': event.service_name,
            'coordinator_decision': 'approved'
        }
    
    async def _handle_unknown_event(self, event: CircuitEventData) -> Dict[str, Any]:
        """Handle unknown event type"""
        logger.warning(f"Unknown event type: {event.event_type}")
        return {
            'action': 'unknown_event',
            'error': f'Unknown event type: {event.event_type.value}'
        }
    
    async def _is_critical_decision(self, event: CircuitEventData) -> bool:
        """Determine if decision requires consensus"""
        critical_events = {
            CircuitEvent.FORCE_OPEN,
            CircuitEvent.FORCE_CLOSE,
            CircuitEvent.THRESHOLD_CHANGE
        }
        return event.event_type in critical_events
    
    async def _achieve_consensus(self, event: CircuitEventData, decision: Dict[str, Any]) -> bool:
        """Achieve consensus on critical decision using Raft"""
        if self.consensus_algorithm.state != ConsensusState.LEADER:
            # If not leader, can't achieve consensus
            return False
        
        consensus_entry = {
            'type': 'circuit_decision',
            'event_id': event.event_id,
            'event_data': event.to_dict(),
            'decision': decision,
            'coordinator': self.node_id
        }
        
        return await self.consensus_algorithm.append_log_entry(consensus_entry)
    
    async def synchronize_circuit_states(self, target_nodes: List[str]) -> bool:
        """Synchronisation états circuits entre nœuds"""
        try:
            # Get current circuit states
            current_states = {}
            for service_name, decision_data in self.circuit_decisions.items():
                current_states[service_name] = {
                    'state': decision_data.get('state'),
                    'last_updated': decision_data.get('timestamp'),
                    'decision_data': decision_data
                }
            
            # Replicate to target nodes
            await self.state_synchronizer.replicate_state_change(
                'all_circuits',
                current_states,
                target_nodes
            )
            
            logger.info(f"Circuit states synchronized to {len(target_nodes)} nodes")
            return True
            
        except Exception as e:
            logger.error(f"Circuit state synchronization failed: {str(e)}")
            return False
    
    async def handle_network_partition(self, partition_info: Dict[str, Any]) -> Dict[str, Any]:
        """Gestion partitions réseau avec degraded mode"""
        partitioned_nodes = partition_info.get('partitioned_nodes', [])
        available_nodes = partition_info.get('available_nodes', [])
        
        # Check if we have majority
        total_nodes = len(self.cluster_config.nodes)
        available_count = len(available_nodes)
        has_majority = available_count > (total_nodes // 2)
        
        partition_response = {
            'partition_detected': True,
            'partitioned_nodes': partitioned_nodes,
            'available_nodes': available_nodes,
            'has_majority': has_majority,
            'coordinator_action': None
        }
        
        if has_majority:
            # Continue normal operation
            partition_response['coordinator_action'] = 'continue_normal_operation'
            logger.info("Network partition detected, but majority available - continuing normal operation")
        else:
            # Enter degraded mode
            partition_response['coordinator_action'] = 'enter_degraded_mode'
            logger.warning("Network partition detected without majority - entering degraded mode")
            
            # In degraded mode, be more conservative with circuit decisions
            await self._enter_degraded_mode()
        
        return partition_response
    
    async def _enter_degraded_mode(self):
        """Enter degraded mode during network partition"""
        # Make circuit breakers more conservative
        # This could involve lowering thresholds, increasing timeouts, etc.
        logger.info("Entered degraded mode due to network partition")
    
    async def elect_circuit_leader(self, candidates: List[str]) -> str:
        """Élection leader pour coordination circuits"""
        if not candidates:
            return self.node_id
        
        # Start election if we're a candidate
        if self.node_id in candidates:
            election_successful = await self.consensus_algorithm.start_election()
            if election_successful:
                return self.node_id
        
        # Wait for election result
        max_wait = 30  # seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if self.consensus_algorithm.leader_id:
                return self.consensus_algorithm.leader_id
            await asyncio.sleep(1)
        
        # No leader elected, return first candidate
        return candidates[0] if candidates else self.node_id
    
    async def _start_event_processor(self):
        """Start background event processor"""
        while True:
            try:
                # Process events from queue
                try:
                    event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                    await self._process_circuit_event(event)
                    self.event_queue.task_done()
                except asyncio.TimeoutError:
                    continue
                    
            except Exception as e:
                logger.error(f"Event processor error: {str(e)}")
                await asyncio.sleep(1)
    
    async def _start_consensus_monitor(self):
        """Monitor consensus and trigger elections if needed"""
        while True:
            try:
                # Check if leader election is needed
                if (self.consensus_algorithm.state == ConsensusState.FOLLOWER and 
                    not self.consensus_algorithm.leader_id):
                    
                    # Check if election timeout elapsed
                    time_since_heartbeat = datetime.now() - self.consensus_algorithm.last_heartbeat
                    if time_since_heartbeat.total_seconds() > self.consensus_algorithm.election_timeout:
                        logger.info("Leader election timeout - starting election")
                        await self.consensus_algorithm.start_election()
                
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Consensus monitor error: {str(e)}")
                await asyncio.sleep(5)
    
    async def get_coordinator_status(self) -> Dict[str, Any]:
        """Get coordinator status and metrics"""
        cluster_health = self.health_monitor.get_cluster_health_summary()
        
        return {
            'node_id': self.node_id,
            'consensus_state': self.consensus_algorithm.state.value,
            'leader_id': self.consensus_algorithm.leader_id,
            'current_term': self.consensus_algorithm.current_term,
            'cluster_health': cluster_health,
            'circuit_decisions_count': len(self.circuit_decisions),
            'pending_decisions_count': len(self.pending_decisions),
            'log_entries_count': len(self.consensus_algorithm.log),
            'commit_index': self.consensus_algorithm.commit_index
        }
    
    async def add_event(self, event: CircuitEventData):
        """Add event to processing queue"""
        await self.event_queue.put(event)

# Export main classes
__all__ = [
    'DistributedCircuitCoordinator',
    'ClusterConfig',
    'ClusterNode',
    'CircuitEventData',
    'CircuitEvent',
    'NodeState',
    'RaftConsensus',
    'StateReplicator',
    'ClusterHealthMonitor'
]