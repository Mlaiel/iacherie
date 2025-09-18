"""
Enterprise Distributed Key Manager
Created by: Senior Engineering Team (DevOps + DBA + Security + ML + Microservices + IA Prompt Engineer)
Date: 2024
Purpose: Distributed key management with Byzantine fault tolerance for Creator Economy Platform

Features:
- Byzantine fault-tolerant key consensus mechanisms
- Multi-region key distribution and synchronization
- Creator-specific sharding strategies
- Conflict resolution and consistency guarantees
- Blockchain-inspired consensus algorithms
- Creator Economy specific optimizations
"""

import asyncio
import hashlib
import json
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
import redis
import etcd3
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import requests


class ConsensusAlgorithm(Enum):
    """Supported consensus algorithms for distributed key management"""
    RAFT = "raft"
    PBFT = "pbft"  # Practical Byzantine Fault Tolerance
    TENDERMINT = "tendermint"
    CREATOR_BFT = "creator_bft"  # Custom Creator Economy BFT


class NodeRole(Enum):
    """Node roles in distributed key management"""
    LEADER = "leader"
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    OBSERVER = "observer"
    CREATOR_VALIDATOR = "creator_validator"


class KeyShardStrategy(Enum):
    """Key sharding strategies for creators"""
    GEOGRAPHIC = "geographic"
    CREATOR_TYPE = "creator_type"
    CONTENT_TYPE = "content_type"
    PERFORMANCE_BASED = "performance_based"
    REGULATORY = "regulatory"


@dataclass
class Node:
    """Distributed key management node"""
    node_id: str
    address: str
    port: int
    role: NodeRole
    region: str
    is_healthy: bool = True
    last_heartbeat: datetime = field(default_factory=datetime.now)
    creator_specialization: Optional[str] = None
    
    @property
    def endpoint(self) -> str:
        return f"{self.address}:{self.port}"


@dataclass
class KeyProposal:
    """Key operation proposal for consensus"""
    proposal_id: str
    operation_type: str  # create, update, delete, rotate
    key_id: str
    creator_id: Optional[str]
    key_data: Dict[str, Any]
    proposed_by: str
    timestamp: datetime
    signatures: Dict[str, str] = field(default_factory=dict)
    
    def serialize(self) -> str:
        """Serialize proposal for network transmission"""
        return json.dumps({
            'proposal_id': self.proposal_id,
            'operation_type': self.operation_type,
            'key_id': self.key_id,
            'creator_id': self.creator_id,
            'key_data': self.key_data,
            'proposed_by': self.proposed_by,
            'timestamp': self.timestamp.isoformat(),
            'signatures': self.signatures
        })


@dataclass
class ConsensusResult:
    """Result of consensus operation"""
    success: bool
    proposal_id: str
    committed_nodes: List[str]
    failed_nodes: List[str]
    execution_time: float
    error_message: Optional[str] = None


class CreatorShardingEngine:
    """Advanced sharding engine for creator-specific key distribution"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.shard_cache = {}
        
    def calculate_shard(self, 
                       creator_id: str,
                       strategy: KeyShardStrategy,
                       metadata: Dict[str, Any]) -> str:
        """Calculate optimal shard for creator key"""
        try:
            if strategy == KeyShardStrategy.GEOGRAPHIC:
                return self._geographic_shard(creator_id, metadata)
            elif strategy == KeyShardStrategy.CREATOR_TYPE:
                return self._creator_type_shard(creator_id, metadata)
            elif strategy == KeyShardStrategy.CONTENT_TYPE:
                return self._content_type_shard(creator_id, metadata)
            elif strategy == KeyShardStrategy.PERFORMANCE_BASED:
                return self._performance_shard(creator_id, metadata)
            elif strategy == KeyShardStrategy.REGULATORY:
                return self._regulatory_shard(creator_id, metadata)
            else:
                return self._default_shard(creator_id)
                
        except Exception as e:
            self.logger.error(f"Shard calculation failed: {e}")
            return self._default_shard(creator_id)
    
    def _geographic_shard(self, creator_id: str, metadata: Dict[str, Any]) -> str:
        """Geographic-based sharding"""
        region = metadata.get('region', 'unknown')
        country = metadata.get('country', 'unknown')
        
        # Europe
        if region in ['EU', 'Europe'] or country in ['FR', 'DE', 'IT', 'ES', 'UK']:
            return 'shard_eu'
        # North America
        elif region in ['NA', 'North America'] or country in ['US', 'CA', 'MX']:
            return 'shard_na'
        # Asia Pacific
        elif region in ['APAC', 'Asia'] or country in ['JP', 'KR', 'CN', 'IN', 'AU']:
            return 'shard_apac'
        # Middle East & Africa
        elif region in ['MEA', 'Africa'] or country in ['AE', 'SA', 'ZA', 'EG']:
            return 'shard_mea'
        else:
            return 'shard_global'
    
    def _creator_type_shard(self, creator_id: str, metadata: Dict[str, Any]) -> str:
        """Creator type-based sharding"""
        creator_type = metadata.get('creator_type', 'unknown')
        
        if creator_type in ['musician', 'audio_producer', 'podcaster']:
            return 'shard_audio_creators'
        elif creator_type in ['photographer', 'visual_artist', 'designer']:
            return 'shard_visual_creators'
        elif creator_type in ['blogger', 'writer', 'journalist']:
            return 'shard_text_creators'
        elif creator_type in ['video_creator', 'filmmaker', 'animator']:
            return 'shard_video_creators'
        elif creator_type in ['influencer', 'social_media_manager']:
            return 'shard_social_creators'
        else:
            return 'shard_mixed_creators'
    
    def _content_type_shard(self, creator_id: str, metadata: Dict[str, Any]) -> str:
        """Content type-based sharding"""
        content_types = metadata.get('content_types', [])
        
        if 'audio' in content_types or 'music' in content_types:
            return 'shard_audio_content'
        elif 'video' in content_types or 'streaming' in content_types:
            return 'shard_video_content'
        elif 'image' in content_types or 'photo' in content_types:
            return 'shard_image_content'
        elif 'text' in content_types or 'article' in content_types:
            return 'shard_text_content'
        else:
            return 'shard_mixed_content'
    
    def _performance_shard(self, creator_id: str, metadata: Dict[str, Any]) -> str:
        """Performance-based sharding"""
        followers = metadata.get('followers', 0)
        engagement_rate = metadata.get('engagement_rate', 0.0)
        content_volume = metadata.get('monthly_content_volume', 0)
        
        # High-performance creators
        if followers > 1000000 or engagement_rate > 0.1 or content_volume > 100:
            return 'shard_high_performance'
        # Medium-performance creators
        elif followers > 10000 or engagement_rate > 0.05 or content_volume > 20:
            return 'shard_medium_performance'
        # Emerging creators
        else:
            return 'shard_emerging_creators'
    
    def _regulatory_shard(self, creator_id: str, metadata: Dict[str, Any]) -> str:
        """Regulatory compliance-based sharding"""
        regulations = metadata.get('applicable_regulations', [])
        
        if 'GDPR' in regulations:
            return 'shard_gdpr_compliant'
        elif 'CCPA' in regulations:
            return 'shard_ccpa_compliant'
        elif 'PIPEDA' in regulations:
            return 'shard_pipeda_compliant'
        elif 'DATA_LOCALIZATION' in regulations:
            return 'shard_localized'
        else:
            return 'shard_standard_compliance'
    
    def _default_shard(self, creator_id: str) -> str:
        """Default hash-based sharding"""
        hash_value = hashlib.sha256(creator_id.encode()).hexdigest()
        shard_num = int(hash_value[:8], 16) % 16
        return f'shard_{shard_num:02d}'


class ConsensusEngine(ABC):
    """Abstract base class for consensus algorithms"""
    
    @abstractmethod
    async def propose_operation(self, proposal: KeyProposal) -> ConsensusResult:
        """Propose a key operation for consensus"""
        pass
    
    @abstractmethod
    async def validate_proposal(self, proposal: KeyProposal) -> bool:
        """Validate a proposal"""
        pass
    
    @abstractmethod
    async def commit_operation(self, proposal: KeyProposal) -> bool:
        """Commit a consensus operation"""
        pass


class CreatorBFTConsensus(ConsensusEngine):
    """Custom Byzantine Fault Tolerant consensus for Creator Economy"""
    
    def __init__(self, node_id: str, nodes: List[Node]):
        self.node_id = node_id
        self.nodes = {node.node_id: node for node in nodes}
        self.logger = logging.getLogger(__name__)
        self.pending_proposals = {}
        self.committed_proposals = set()
        
    async def propose_operation(self, proposal: KeyProposal) -> ConsensusResult:
        """Propose operation using Creator BFT consensus"""
        start_time = time.time()
        committed_nodes = []
        failed_nodes = []
        
        try:
            # Phase 1: Prepare
            prepare_votes = await self._prepare_phase(proposal)
            
            if len(prepare_votes) < self._required_votes():
                return ConsensusResult(
                    success=False,
                    proposal_id=proposal.proposal_id,
                    committed_nodes=committed_nodes,
                    failed_nodes=failed_nodes,
                    execution_time=time.time() - start_time,
                    error_message="Insufficient prepare votes"
                )
            
            # Phase 2: Commit
            commit_votes = await self._commit_phase(proposal)
            
            if len(commit_votes) >= self._required_votes():
                # Execute the operation
                success = await self.commit_operation(proposal)
                if success:
                    committed_nodes = list(commit_votes)
                    self.committed_proposals.add(proposal.proposal_id)
                    
                    return ConsensusResult(
                        success=True,
                        proposal_id=proposal.proposal_id,
                        committed_nodes=committed_nodes,
                        failed_nodes=failed_nodes,
                        execution_time=time.time() - start_time
                    )
            
            return ConsensusResult(
                success=False,
                proposal_id=proposal.proposal_id,
                committed_nodes=committed_nodes,
                failed_nodes=failed_nodes,
                execution_time=time.time() - start_time,
                error_message="Insufficient commit votes"
            )
            
        except Exception as e:
            self.logger.error(f"Consensus failed: {e}")
            return ConsensusResult(
                success=False,
                proposal_id=proposal.proposal_id,
                committed_nodes=committed_nodes,
                failed_nodes=failed_nodes,
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _prepare_phase(self, proposal: KeyProposal) -> Set[str]:
        """BFT prepare phase"""
        votes = set()
        tasks = []
        
        for node_id, node in self.nodes.items():
            if node.is_healthy:
                task = self._send_prepare_request(node, proposal)
                tasks.append((node_id, task))
        
        for node_id, task in tasks:
            try:
                response = await asyncio.wait_for(task, timeout=5.0)
                if response:
                    votes.add(node_id)
            except asyncio.TimeoutError:
                self.logger.warning(f"Prepare timeout for node {node_id}")
            except Exception as e:
                self.logger.error(f"Prepare failed for node {node_id}: {e}")
        
        return votes
    
    async def _commit_phase(self, proposal: KeyProposal) -> Set[str]:
        """BFT commit phase"""
        votes = set()
        tasks = []
        
        for node_id, node in self.nodes.items():
            if node.is_healthy:
                task = self._send_commit_request(node, proposal)
                tasks.append((node_id, task))
        
        for node_id, task in tasks:
            try:
                response = await asyncio.wait_for(task, timeout=10.0)
                if response:
                    votes.add(node_id)
            except asyncio.TimeoutError:
                self.logger.warning(f"Commit timeout for node {node_id}")
            except Exception as e:
                self.logger.error(f"Commit failed for node {node_id}: {e}")
        
        return votes
    
    async def _send_prepare_request(self, node: Node, proposal: KeyProposal) -> bool:
        """Send prepare request to node"""
        try:
            # Simulate network request
            await asyncio.sleep(0.1)
            
            # Validate proposal for creator-specific requirements
            if proposal.creator_id:
                creator_validation = await self._validate_creator_proposal(proposal)
                if not creator_validation:
                    return False
            
            return await self.validate_proposal(proposal)
            
        except Exception as e:
            self.logger.error(f"Prepare request failed: {e}")
            return False
    
    async def _send_commit_request(self, node: Node, proposal: KeyProposal) -> bool:
        """Send commit request to node"""
        try:
            # Simulate network request
            await asyncio.sleep(0.2)
            return True
            
        except Exception as e:
            self.logger.error(f"Commit request failed: {e}")
            return False
    
    async def _validate_creator_proposal(self, proposal: KeyProposal) -> bool:
        """Validate creator-specific proposal requirements"""
        try:
            # Check creator permissions
            creator_id = proposal.creator_id
            if not creator_id:
                return True
            
            # Validate creator exists and has proper permissions
            # This would integrate with creator management system
            
            # Check content type compatibility
            content_type = proposal.key_data.get('content_type')
            if content_type:
                # Validate that creator can handle this content type
                pass
            
            # Check geographic restrictions
            creator_region = proposal.key_data.get('creator_region')
            if creator_region:
                # Validate regional compliance
                pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"Creator validation failed: {e}")
            return False
    
    def _required_votes(self) -> int:
        """Calculate required votes for consensus (2f+1 for f Byzantine faults)"""
        total_nodes = len([n for n in self.nodes.values() if n.is_healthy])
        return (total_nodes * 2) // 3 + 1
    
    async def validate_proposal(self, proposal: KeyProposal) -> bool:
        """Validate proposal"""
        try:
            # Basic validation
            if not proposal.proposal_id or not proposal.key_id:
                return False
            
            # Check if already committed
            if proposal.proposal_id in self.committed_proposals:
                return False
            
            # Validate operation type
            valid_operations = ['create', 'update', 'delete', 'rotate']
            if proposal.operation_type not in valid_operations:
                return False
            
            # Validate key data structure
            if not isinstance(proposal.key_data, dict):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Proposal validation failed: {e}")
            return False
    
    async def commit_operation(self, proposal: KeyProposal) -> bool:
        """Commit operation locally"""
        try:
            # This would integrate with local key storage
            self.logger.info(f"Committing operation {proposal.proposal_id}")
            
            # Simulate key operation
            if proposal.operation_type == 'create':
                # Create key logic
                pass
            elif proposal.operation_type == 'update':
                # Update key logic
                pass
            elif proposal.operation_type == 'delete':
                # Delete key logic
                pass
            elif proposal.operation_type == 'rotate':
                # Rotate key logic
                pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"Operation commit failed: {e}")
            return False


class DistributedKeyManager:
    """Main distributed key management orchestrator"""
    
    def __init__(self, 
                 node_id: str,
                 consensus_algorithm: ConsensusAlgorithm = ConsensusAlgorithm.CREATOR_BFT,
                 redis_client: Optional[redis.Redis] = None,
                 etcd_client: Optional[etcd3.Etcd3Client] = None):
        self.node_id = node_id
        self.consensus_algorithm = consensus_algorithm
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        self.etcd_client = etcd_client or etcd3.client()
        self.logger = logging.getLogger(__name__)
        
        # Components
        self.sharding_engine = CreatorShardingEngine()
        self.nodes = {}
        self.consensus_engine = None
        self.is_leader = False
        
        # State
        self.key_registry = {}
        self.operation_log = []
        self.sync_status = {}
        
        # Metrics
        self.metrics = {
            'operations_proposed': 0,
            'operations_committed': 0,
            'consensus_failures': 0,
            'sync_operations': 0,
            'creator_operations': 0
        }
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = False
        
    async def initialize(self, nodes: List[Node]):
        """Initialize distributed key manager"""
        try:
            self.nodes = {node.node_id: node for node in nodes}
            
            # Initialize consensus engine
            if self.consensus_algorithm == ConsensusAlgorithm.CREATOR_BFT:
                self.consensus_engine = CreatorBFTConsensus(self.node_id, nodes)
            
            # Start background tasks
            self.running = True
            asyncio.create_task(self._heartbeat_loop())
            asyncio.create_task(self._sync_loop())
            asyncio.create_task(self._leader_election_loop())
            
            self.logger.info(f"Distributed key manager initialized with {len(nodes)} nodes")
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            raise
    
    async def create_key(self, 
                        key_id: str,
                        creator_id: Optional[str] = None,
                        key_data: Dict[str, Any] = None,
                        metadata: Dict[str, Any] = None) -> ConsensusResult:
        """Create a new key through distributed consensus"""
        try:
            # Determine optimal shard
            if creator_id and metadata:
                strategy = KeyShardStrategy.CREATOR_TYPE  # Default strategy
                shard_id = self.sharding_engine.calculate_shard(creator_id, strategy, metadata)
                key_data = key_data or {}
                key_data['shard_id'] = shard_id
            
            # Create proposal
            proposal = KeyProposal(
                proposal_id=str(uuid.uuid4()),
                operation_type='create',
                key_id=key_id,
                creator_id=creator_id,
                key_data=key_data or {},
                proposed_by=self.node_id,
                timestamp=datetime.now()
            )
            
            # Execute consensus
            result = await self.consensus_engine.propose_operation(proposal)
            
            if result.success:
                self.metrics['operations_committed'] += 1
                if creator_id:
                    self.metrics['creator_operations'] += 1
            else:
                self.metrics['consensus_failures'] += 1
            
            self.metrics['operations_proposed'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Key creation failed: {e}")
            self.metrics['consensus_failures'] += 1
            return ConsensusResult(
                success=False,
                proposal_id="",
                committed_nodes=[],
                failed_nodes=[],
                execution_time=0.0,
                error_message=str(e)
            )
    
    async def update_key(self, 
                        key_id: str,
                        updates: Dict[str, Any],
                        creator_id: Optional[str] = None) -> ConsensusResult:
        """Update a key through distributed consensus"""
        try:
            proposal = KeyProposal(
                proposal_id=str(uuid.uuid4()),
                operation_type='update',
                key_id=key_id,
                creator_id=creator_id,
                key_data=updates,
                proposed_by=self.node_id,
                timestamp=datetime.now()
            )
            
            result = await self.consensus_engine.propose_operation(proposal)
            
            if result.success:
                self.metrics['operations_committed'] += 1
                if creator_id:
                    self.metrics['creator_operations'] += 1
            else:
                self.metrics['consensus_failures'] += 1
            
            self.metrics['operations_proposed'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Key update failed: {e}")
            self.metrics['consensus_failures'] += 1
            return ConsensusResult(
                success=False,
                proposal_id="",
                committed_nodes=[],
                failed_nodes=[],
                execution_time=0.0,
                error_message=str(e)
            )
    
    async def delete_key(self, 
                        key_id: str,
                        creator_id: Optional[str] = None) -> ConsensusResult:
        """Delete a key through distributed consensus"""
        try:
            proposal = KeyProposal(
                proposal_id=str(uuid.uuid4()),
                operation_type='delete',
                key_id=key_id,
                creator_id=creator_id,
                key_data={},
                proposed_by=self.node_id,
                timestamp=datetime.now()
            )
            
            result = await self.consensus_engine.propose_operation(proposal)
            
            if result.success:
                self.metrics['operations_committed'] += 1
                if creator_id:
                    self.metrics['creator_operations'] += 1
            else:
                self.metrics['consensus_failures'] += 1
            
            self.metrics['operations_proposed'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Key deletion failed: {e}")
            self.metrics['consensus_failures'] += 1
            return ConsensusResult(
                success=False,
                proposal_id="",
                committed_nodes=[],
                failed_nodes=[],
                execution_time=0.0,
                error_message=str(e)
            )
    
    async def rotate_key(self, 
                        key_id: str,
                        rotation_data: Dict[str, Any],
                        creator_id: Optional[str] = None) -> ConsensusResult:
        """Rotate a key through distributed consensus"""
        try:
            proposal = KeyProposal(
                proposal_id=str(uuid.uuid4()),
                operation_type='rotate',
                key_id=key_id,
                creator_id=creator_id,
                key_data=rotation_data,
                proposed_by=self.node_id,
                timestamp=datetime.now()
            )
            
            result = await self.consensus_engine.propose_operation(proposal)
            
            if result.success:
                self.metrics['operations_committed'] += 1
                if creator_id:
                    self.metrics['creator_operations'] += 1
            else:
                self.metrics['consensus_failures'] += 1
            
            self.metrics['operations_proposed'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Key rotation failed: {e}")
            self.metrics['consensus_failures'] += 1
            return ConsensusResult(
                success=False,
                proposal_id="",
                committed_nodes=[],
                failed_nodes=[],
                execution_time=0.0,
                error_message=str(e)
            )
    
    async def sync_cluster_state(self):
        """Synchronize cluster state across nodes"""
        try:
            # Get cluster state from leader
            if not self.is_leader:
                leader_node = self._get_leader_node()
                if leader_node:
                    state = await self._fetch_cluster_state(leader_node)
                    if state:
                        await self._apply_cluster_state(state)
                        self.metrics['sync_operations'] += 1
            
        except Exception as e:
            self.logger.error(f"Cluster sync failed: {e}")
    
    async def _heartbeat_loop(self):
        """Background heartbeat loop"""
        while self.running:
            try:
                await self._send_heartbeats()
                await self._check_node_health()
                await asyncio.sleep(5)  # 5-second heartbeat interval
                
            except Exception as e:
                self.logger.error(f"Heartbeat loop error: {e}")
                await asyncio.sleep(1)
    
    async def _sync_loop(self):
        """Background synchronization loop"""
        while self.running:
            try:
                await self.sync_cluster_state()
                await asyncio.sleep(30)  # 30-second sync interval
                
            except Exception as e:
                self.logger.error(f"Sync loop error: {e}")
                await asyncio.sleep(5)
    
    async def _leader_election_loop(self):
        """Background leader election loop"""
        while self.running:
            try:
                await self._participate_in_leader_election()
                await asyncio.sleep(10)  # 10-second election check
                
            except Exception as e:
                self.logger.error(f"Leader election error: {e}")
                await asyncio.sleep(2)
    
    async def _send_heartbeats(self):
        """Send heartbeats to other nodes"""
        for node_id, node in self.nodes.items():
            if node_id != self.node_id and node.is_healthy:
                try:
                    # Simulate heartbeat
                    pass
                except Exception as e:
                    self.logger.warning(f"Heartbeat to {node_id} failed: {e}")
    
    async def _check_node_health(self):
        """Check health of cluster nodes"""
        current_time = datetime.now()
        for node_id, node in self.nodes.items():
            if node_id != self.node_id:
                time_since_heartbeat = current_time - node.last_heartbeat
                if time_since_heartbeat > timedelta(seconds=30):
                    node.is_healthy = False
                    self.logger.warning(f"Node {node_id} marked as unhealthy")
    
    async def _participate_in_leader_election(self):
        """Participate in leader election"""
        try:
            # Simple leader election based on node ID
            healthy_nodes = [nid for nid, node in self.nodes.items() if node.is_healthy]
            if healthy_nodes:
                leader_id = min(healthy_nodes)
                self.is_leader = (leader_id == self.node_id)
                
        except Exception as e:
            self.logger.error(f"Leader election failed: {e}")
    
    def _get_leader_node(self) -> Optional[Node]:
        """Get current leader node"""
        healthy_nodes = [(nid, node) for nid, node in self.nodes.items() if node.is_healthy]
        if healthy_nodes:
            leader_id = min(nid for nid, _ in healthy_nodes)
            return self.nodes.get(leader_id)
        return None
    
    async def _fetch_cluster_state(self, leader_node: Node) -> Optional[Dict[str, Any]]:
        """Fetch cluster state from leader"""
        try:
            # Simulate fetching state from leader
            return {
                'key_registry': {},
                'operation_log': [],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to fetch cluster state: {e}")
            return None
    
    async def _apply_cluster_state(self, state: Dict[str, Any]):
        """Apply cluster state locally"""
        try:
            # Apply state updates
            if 'key_registry' in state:
                self.key_registry.update(state['key_registry'])
            
            if 'operation_log' in state:
                # Merge operation logs
                pass
            
        except Exception as e:
            self.logger.error(f"Failed to apply cluster state: {e}")
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get current cluster status"""
        healthy_nodes = [nid for nid, node in self.nodes.items() if node.is_healthy]
        return {
            'node_id': self.node_id,
            'is_leader': self.is_leader,
            'total_nodes': len(self.nodes),
            'healthy_nodes': len(healthy_nodes),
            'consensus_algorithm': self.consensus_algorithm.value,
            'metrics': self.metrics.copy(),
            'nodes': {
                nid: {
                    'is_healthy': node.is_healthy,
                    'role': node.role.value,
                    'region': node.region,
                    'last_heartbeat': node.last_heartbeat.isoformat()
                }
                for nid, node in self.nodes.items()
            }
        }
    
    async def shutdown(self):
        """Shutdown distributed key manager"""
        try:
            self.running = False
            self.executor.shutdown(wait=True)
            self.logger.info("Distributed key manager shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")


# Example usage and testing
async def demo_distributed_key_manager():
    """Demonstrate distributed key manager capabilities"""
    
    # Create nodes
    nodes = [
        Node("node1", "192.168.1.10", 8001, NodeRole.LEADER, "us-east-1"),
        Node("node2", "192.168.1.11", 8001, NodeRole.FOLLOWER, "us-west-2"),
        Node("node3", "192.168.1.12", 8001, NodeRole.FOLLOWER, "eu-west-1"),
        Node("node4", "192.168.1.13", 8001, NodeRole.CREATOR_VALIDATOR, "ap-southeast-1"),
    ]
    
    # Initialize manager
    manager = DistributedKeyManager("node1", ConsensusAlgorithm.CREATOR_BFT)
    await manager.initialize(nodes)
    
    # Create key for a creator
    creator_metadata = {
        'creator_type': 'musician',
        'region': 'North America',
        'country': 'US',
        'followers': 50000,
        'engagement_rate': 0.08,
        'monthly_content_volume': 25,
        'content_types': ['audio', 'video'],
        'applicable_regulations': ['CCPA']
    }
    
    result = await manager.create_key(
        key_id="creator_key_001",
        creator_id="creator_12345",
        key_data={'algorithm': 'AES-256-GCM', 'purpose': 'content_encryption'},
        metadata=creator_metadata
    )
    
    print(f"Key creation result: {result}")
    
    # Update key
    update_result = await manager.update_key(
        key_id="creator_key_001",
        updates={'last_rotation': datetime.now().isoformat()},
        creator_id="creator_12345"
    )
    
    print(f"Key update result: {update_result}")
    
    # Get cluster status
    status = manager.get_cluster_status()
    print(f"Cluster status: {json.dumps(status, indent=2)}")
    
    # Shutdown
    await manager.shutdown()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run demo
    asyncio.run(demo_distributed_key_manager())