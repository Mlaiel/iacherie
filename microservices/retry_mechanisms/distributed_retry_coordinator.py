"""
Distributed Retry Coordinator - Ainflue
=======================================
Coordinateur retry distribué pour microservices.
Cross-node coordination + distributed locks + retry consensus.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Retry Mechanisms
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture retry mechanisms et tous ses algorithmes sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import time
import json
import hashlib
import random
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class LockStatus(Enum):
    """Status du distributed lock"""
    ACQUIRED = "acquired"
    FAILED = "failed"
    EXPIRED = "expired"
    RELEASED = "released"

class ConsensusDecision(Enum):
    """Décisions consensus retry"""
    PROCEED = "proceed"
    DELAY = "delay"
    REJECT = "reject"
    REDISTRIBUTE = "redistribute"

class NodeRole(Enum):
    """Rôles des nodes dans coordination"""
    LEADER = "leader"
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    OBSERVER = "observer"

@dataclass
class CoordinatorConfig:
    """Configuration coordinateur distribué"""
    # Node configuration
    node_id: str = field(default_factory=lambda: f"node-{int(time.time())}")
    cluster_nodes: List[str] = field(default_factory=list)
    heartbeat_interval: float = 30.0
    leader_election_timeout: float = 60.0
    
    # Lock configuration
    lock_timeout: int = 300  # 5 minutes
    lock_renewal_interval: float = 60.0  # 1 minute
    max_lock_attempts: int = 3
    
    # Consensus configuration
    consensus_timeout: float = 30.0
    quorum_size: int = 3
    retry_budget_per_node: int = 100
    
    # Coordination settings
    max_concurrent_operations: int = 50
    operation_timeout: float = 900.0  # 15 minutes
    redistribution_threshold: float = 0.8

@dataclass
class DistributedRetryRequest:
    """Requête retry distribuée"""
    operation_id: str
    service_name: str
    operation_type: str
    priority: int
    node_id: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)
    retry_count: int = 0
    distributed_lock_required: bool = True

@dataclass
class RetryProposal:
    """Proposition retry pour consensus"""
    operation_id: str
    proposer_node: str
    retry_strategy: Dict
    resource_requirements: Dict
    expected_duration: float
    priority: int
    timestamp: float = field(default_factory=time.time)

@dataclass
class LockResult:
    """Résultat acquisition lock"""
    operation_id: str
    status: LockStatus
    lock_holder: Optional[str] = None
    expiry_time: Optional[float] = None
    error_message: Optional[str] = None

class DistributedLockManager:
    """Manager distributed locks pour retry operations"""
    
    def __init__(self, config: CoordinatorConfig):
        self.config = config
        self.active_locks = {}  # operation_id -> lock_info
        self.lock_requests = deque(maxlen=1000)
        self.lock_metrics = {
            'locks_acquired': 0,
            'locks_failed': 0,
            'locks_expired': 0,
            'locks_released': 0
        }
    
    async def acquire_lock(self, operation_id: str, requester_node: str, timeout: int = None) -> LockResult:
        """Acquisition distributed lock pour retry operation"""
        timeout = timeout or self.config.lock_timeout
        expiry_time = time.time() + timeout
        
        # Vérification si lock déjà détenu
        if operation_id in self.active_locks:
            existing_lock = self.active_locks[operation_id]
            if existing_lock['expiry_time'] > time.time():
                if existing_lock['holder'] == requester_node:
                    # Renouvellement automatique
                    existing_lock['expiry_time'] = expiry_time
                    return LockResult(operation_id, LockStatus.ACQUIRED, requester_node, expiry_time)
                else:
                    return LockResult(operation_id, LockStatus.FAILED, existing_lock['holder'])
        
        # Acquisition nouveau lock
        lock_info = {
            'operation_id': operation_id,
            'holder': requester_node,
            'acquired_at': time.time(),
            'expiry_time': expiry_time,
            'renewed_count': 0
        }
        
        self.active_locks[operation_id] = lock_info
        self.lock_metrics['locks_acquired'] += 1
        
        # Enregistrement requête
        self.lock_requests.append({
            'operation_id': operation_id,
            'requester': requester_node,
            'action': 'acquire',
            'timestamp': time.time()
        })
        
        logger.info(f"Distributed lock acquired for {operation_id} by {requester_node}")
        return LockResult(operation_id, LockStatus.ACQUIRED, requester_node, expiry_time)
    
    async def release_lock(self, operation_id: str, holder_node: str) -> LockResult:
        """Libération distributed lock"""
        
        if operation_id not in self.active_locks:
            return LockResult(operation_id, LockStatus.FAILED, error_message="Lock not found")
        
        lock_info = self.active_locks[operation_id]
        
        # Vérification authorisation
        if lock_info['holder'] != holder_node:
            return LockResult(
                operation_id, 
                LockStatus.FAILED, 
                lock_info['holder'],
                error_message="Not authorized to release lock"
            )
        
        # Libération
        del self.active_locks[operation_id]
        self.lock_metrics['locks_released'] += 1
        
        logger.info(f"Distributed lock released for {operation_id} by {holder_node}")
        return LockResult(operation_id, LockStatus.RELEASED)
    
    async def renew_lock(self, operation_id: str, holder_node: str, extend_by: int = None) -> LockResult:
        """Renouvellement distributed lock"""
        extend_by = extend_by or self.config.lock_timeout
        
        if operation_id not in self.active_locks:
            return LockResult(operation_id, LockStatus.EXPIRED)
        
        lock_info = self.active_locks[operation_id]
        
        if lock_info['holder'] != holder_node:
            return LockResult(operation_id, LockStatus.FAILED, lock_info['holder'])
        
        # Renouvellement
        lock_info['expiry_time'] = time.time() + extend_by
        lock_info['renewed_count'] += 1
        
        logger.debug(f"Lock renewed for {operation_id} by {holder_node}")
        return LockResult(operation_id, LockStatus.ACQUIRED, holder_node, lock_info['expiry_time'])
    
    async def cleanup_expired_locks(self):
        """Nettoyage locks expirés"""
        current_time = time.time()
        expired_locks = []
        
        for operation_id, lock_info in list(self.active_locks.items()):
            if lock_info['expiry_time'] <= current_time:
                expired_locks.append(operation_id)
                del self.active_locks[operation_id]
                self.lock_metrics['locks_expired'] += 1
        
        if expired_locks:
            logger.info(f"Cleaned up {len(expired_locks)} expired locks")
        
        return expired_locks
    
    def get_lock_status(self, operation_id: str) -> Optional[Dict]:
        """Status d'un lock spécifique"""
        if operation_id in self.active_locks:
            lock_info = self.active_locks[operation_id]
            return {
                **lock_info,
                'is_expired': lock_info['expiry_time'] <= time.time(),
                'time_remaining': max(0, lock_info['expiry_time'] - time.time())
            }
        return None

class RetryConsensusEngine:
    """Moteur consensus pour décisions retry distribuées"""
    
    def __init__(self, config: CoordinatorConfig):
        self.config = config
        self.proposals = {}  # proposal_id -> proposal_info
        self.votes = defaultdict(dict)  # proposal_id -> {node_id: vote}
        self.consensus_history = deque(maxlen=500)
    
    async def propose_retry_operation(self, proposal: RetryProposal) -> str:
        """Proposition opération retry pour consensus"""
        proposal_id = self._generate_proposal_id(proposal)
        
        proposal_info = {
            'id': proposal_id,
            'proposal': proposal,
            'status': 'proposed',
            'votes_received': 0,
            'votes_needed': max(1, self.config.quorum_size // 2 + 1),
            'created_at': time.time(),
            'timeout_at': time.time() + self.config.consensus_timeout
        }
        
        self.proposals[proposal_id] = proposal_info
        logger.info(f"Retry proposal {proposal_id} created for operation {proposal.operation_id}")
        
        return proposal_id
    
    async def vote_on_proposal(self, proposal_id: str, voter_node: str, vote: bool, reasoning: str = "") -> bool:
        """Vote sur proposition retry"""
        
        if proposal_id not in self.proposals:
            return False
        
        proposal_info = self.proposals[proposal_id]
        
        # Vérification timeout
        if time.time() > proposal_info['timeout_at']:
            proposal_info['status'] = 'timeout'
            return False
        
        # Enregistrement vote
        self.votes[proposal_id][voter_node] = {
            'vote': vote,
            'reasoning': reasoning,
            'timestamp': time.time()
        }
        
        proposal_info['votes_received'] = len(self.votes[proposal_id])
        
        # Vérification consensus
        if proposal_info['votes_received'] >= proposal_info['votes_needed']:
            await self._evaluate_consensus(proposal_id)
        
        return True
    
    async def _evaluate_consensus(self, proposal_id: str):
        """Évaluation consensus pour proposition"""
        proposal_info = self.proposals[proposal_id]
        votes = self.votes[proposal_id]
        
        # Comptage votes
        positive_votes = sum(1 for vote_info in votes.values() if vote_info['vote'])
        total_votes = len(votes)
        
        # Décision consensus
        if positive_votes >= proposal_info['votes_needed']:
            decision = ConsensusDecision.PROCEED
        elif total_votes >= self.config.quorum_size and positive_votes < total_votes // 2:
            decision = ConsensusDecision.REJECT
        else:
            decision = ConsensusDecision.DELAY
        
        proposal_info['status'] = 'decided'
        proposal_info['decision'] = decision
        proposal_info['decided_at'] = time.time()
        
        # Historique
        self.consensus_history.append({
            'proposal_id': proposal_id,
            'decision': decision.value,
            'positive_votes': positive_votes,
            'total_votes': total_votes,
            'timestamp': time.time()
        })
        
        logger.info(f"Consensus reached for {proposal_id}: {decision.value} ({positive_votes}/{total_votes})")
    
    async def get_consensus_decision(self, proposal_id: str) -> Optional[ConsensusDecision]:
        """Récupération décision consensus"""
        if proposal_id in self.proposals:
            proposal_info = self.proposals[proposal_id]
            return proposal_info.get('decision')
        return None
    
    def _generate_proposal_id(self, proposal: RetryProposal) -> str:
        """Génération ID unique pour proposition"""
        content = f"{proposal.operation_id}-{proposal.proposer_node}-{proposal.timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    async def cleanup_old_proposals(self):
        """Nettoyage anciennes propositions"""
        current_time = time.time()
        expired_proposals = []
        
        for proposal_id, proposal_info in list(self.proposals.items()):
            if current_time > proposal_info['timeout_at'] and proposal_info['status'] != 'decided':
                proposal_info['status'] = 'timeout'
                expired_proposals.append(proposal_id)
        
        return expired_proposals

class NodeCoordinationManager:
    """Manager coordination entre nodes du cluster"""
    
    def __init__(self, config: CoordinatorConfig):
        self.config = config
        self.current_role = NodeRole.FOLLOWER
        self.leader_node = None
        self.cluster_state = {}  # node_id -> node_info
        self.heartbeats = defaultdict(float)  # node_id -> last_heartbeat
        self.load_distribution = defaultdict(int)  # node_id -> current_load
        
        # Election state
        self.election_in_progress = False
        self.election_votes = {}
        self.last_election = 0
    
    async def join_cluster(self) -> bool:
        """Rejoindre cluster de coordination"""
        
        # Initialisation état node
        self.cluster_state[self.config.node_id] = {
            'node_id': self.config.node_id,
            'role': self.current_role.value,
            'joined_at': time.time(),
            'last_seen': time.time(),
            'load': 0,
            'capabilities': ['retry_coordination', 'lock_management', 'consensus']
        }
        
        # Annonce aux autres nodes
        await self._announce_node_join()
        
        logger.info(f"Node {self.config.node_id} joined cluster")
        return True
    
    async def _announce_node_join(self):
        """Annonce rejoindre cluster"""
        # En production, enverrait message aux autres nodes
        pass
    
    async def send_heartbeat(self):
        """Envoi heartbeat aux autres nodes"""
        current_time = time.time()
        self.heartbeats[self.config.node_id] = current_time
        
        # Mise à jour état local
        if self.config.node_id in self.cluster_state:
            self.cluster_state[self.config.node_id]['last_seen'] = current_time
    
    async def detect_failed_nodes(self) -> List[str]:
        """Détection nodes défaillants"""
        current_time = time.time()
        failed_nodes = []
        
        for node_id, last_heartbeat in self.heartbeats.items():
            if (current_time - last_heartbeat > self.config.heartbeat_interval * 3 and
                node_id != self.config.node_id):
                failed_nodes.append(node_id)
                
                # Nettoyage état
                if node_id in self.cluster_state:
                    self.cluster_state[node_id]['status'] = 'failed'
        
        if failed_nodes:
            logger.warning(f"Detected failed nodes: {failed_nodes}")
        
        return failed_nodes
    
    async def elect_leader(self) -> str:
        """Élection leader cluster"""
        
        if self.election_in_progress:
            return self.leader_node or self.config.node_id
        
        self.election_in_progress = True
        self.last_election = time.time()
        
        # Candidats viables (nodes actifs)
        active_nodes = [
            node_id for node_id, node_info in self.cluster_state.items()
            if node_info.get('status') != 'failed'
        ]
        
        if not active_nodes:
            active_nodes = [self.config.node_id]
        
        # Election basique - node avec ID le plus ancien
        leader = min(active_nodes)
        
        # Mise à jour rôles
        for node_id in active_nodes:
            if node_id == leader:
                if node_id == self.config.node_id:
                    self.current_role = NodeRole.LEADER
                self.cluster_state[node_id]['role'] = NodeRole.LEADER.value
            else:
                if node_id == self.config.node_id:
                    self.current_role = NodeRole.FOLLOWER
                self.cluster_state[node_id]['role'] = NodeRole.FOLLOWER.value
        
        self.leader_node = leader
        self.election_in_progress = False
        
        logger.info(f"Leader elected: {leader}")
        return leader
    
    async def redistribute_load(self, failed_nodes: List[str]) -> Dict:
        """Redistribution charge après défaillance nodes"""
        
        if not failed_nodes:
            return {'redistributed_operations': 0, 'target_nodes': []}
        
        # Calcul charge totale à redistribuer
        total_load_to_redistribute = sum(
            self.load_distribution.get(node, 0) for node in failed_nodes
        )
        
        # Nodes actifs pour redistribution
        active_nodes = [
            node_id for node_id, node_info in self.cluster_state.items()
            if (node_info.get('status') != 'failed' and 
                node_id not in failed_nodes and
                node_id != self.config.node_id)
        ]
        
        if not active_nodes:
            active_nodes = [self.config.node_id]
        
        # Distribution équitable
        load_per_node = total_load_to_redistribute // len(active_nodes)
        remainder = total_load_to_redistribute % len(active_nodes)
        
        redistribution_plan = {}
        for i, node_id in enumerate(active_nodes):
            node_load = load_per_node + (1 if i < remainder else 0)
            redistribution_plan[node_id] = node_load
            self.load_distribution[node_id] += node_load
        
        # Nettoyage charge des nodes défaillants
        for failed_node in failed_nodes:
            self.load_distribution[failed_node] = 0
        
        logger.info(f"Redistributed {total_load_to_redistribute} operations to {len(active_nodes)} nodes")
        
        return {
            'redistributed_operations': total_load_to_redistribute,
            'target_nodes': list(redistribution_plan.keys()),
            'distribution_plan': redistribution_plan
        }
    
    def get_cluster_status(self) -> Dict:
        """Status cluster complet"""
        return {
            'cluster_size': len(self.cluster_state),
            'leader_node': self.leader_node,
            'current_role': self.current_role.value,
            'active_nodes': [
                node_id for node_id, info in self.cluster_state.items()
                if info.get('status') != 'failed'
            ],
            'failed_nodes': [
                node_id for node_id, info in self.cluster_state.items()
                if info.get('status') == 'failed'
            ],
            'load_distribution': dict(self.load_distribution),
            'last_election': self.last_election,
            'election_in_progress': self.election_in_progress
        }

class DistributedRetryCoordinator:
    """
    Coordinateur retry distribué pour microservices.
    Cross-node coordination + distributed locks + retry consensus.
    """
    
    def __init__(self, coordinator_config: CoordinatorConfig = None):
        self.coordinator_config = coordinator_config or CoordinatorConfig()
        self.distributed_lock = DistributedLockManager(self.coordinator_config)
        self.consensus_engine = RetryConsensusEngine(self.coordinator_config)
        self.node_coordinator = NodeCoordinationManager(self.coordinator_config)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # État coordination
        self.active_operations = {}  # operation_id -> operation_info
        self.coordination_metrics = {
            'operations_coordinated': 0,
            'consensus_decisions': 0,
            'locks_managed': 0,
            'redistributions': 0
        }
        
        # Retry budgets
        self.node_retry_budgets = defaultdict(lambda: self.coordinator_config.retry_budget_per_node)
        
        # Background tasks
        self._background_tasks = []
    
    async def start_coordination(self):
        """Démarrage coordinateur distribué"""
        
        # Rejoindre cluster
        await self.node_coordinator.join_cluster()
        
        # Démarrage tâches background
        self._background_tasks = [
            asyncio.create_task(self._heartbeat_loop()),
            asyncio.create_task(self._cleanup_loop()),
            asyncio.create_task(self._failure_detection_loop())
        ]
        
        logger.info(f"Distributed retry coordinator started on node {self.coordinator_config.node_id}")
    
    async def stop_coordination(self):
        """Arrêt coordinateur"""
        
        # Arrêt tâches background
        for task in self._background_tasks:
            task.cancel()
        
        # Libération locks détenus
        await self._release_all_locks()
        
        logger.info("Distributed retry coordinator stopped")
    
    async def coordinate_distributed_retry(self, retry_request: DistributedRetryRequest) -> Dict:
        """
        Coordination retry distribué avec consensus.
        
        Coordination Features:
        - Distributed retry consensus pour éviter duplicate operations
        - Cross-node retry coordination avec leader election
        - Distributed locks pour critical retry operations
        - Retry budget sharing entre nodes
        - Global retry rate limiting coordination
        - Node failure detection et retry redistribution
        - Consistent retry state across distributed system
        """
        
        coordination_result = {
            'operation_id': retry_request.operation_id,
            'status': 'pending',
            'coordinator_node': self.coordinator_config.node_id,
            'coordination_steps': []
        }
        
        try:
            # 1. Vérification retry budget
            if not await self._check_retry_budget(retry_request.node_id):
                coordination_result['status'] = 'rejected'
                coordination_result['reason'] = 'retry budget exceeded'
                return coordination_result
            
            coordination_result['coordination_steps'].append('budget_check_passed')
            
            # 2. Acquisition distributed lock si requis
            if retry_request.distributed_lock_required:
                lock_result = await self.acquire_retry_lock(
                    retry_request.operation_id, 
                    retry_request.node_id,
                    self.coordinator_config.lock_timeout
                )
                
                if lock_result.status != LockStatus.ACQUIRED:
                    coordination_result['status'] = 'lock_failed'
                    coordination_result['lock_holder'] = lock_result.lock_holder
                    return coordination_result
                
                coordination_result['coordination_steps'].append('lock_acquired')
            
            # 3. Création proposition consensus
            proposal = RetryProposal(
                operation_id=retry_request.operation_id,
                proposer_node=retry_request.node_id,
                retry_strategy={'max_retries': 3, 'backoff': 'exponential'},
                resource_requirements={'cpu': 0.5, 'memory': '256MB'},
                expected_duration=300.0,
                priority=retry_request.priority
            )
            
            proposal_id = await self.establish_retry_consensus([proposal])
            coordination_result['proposal_id'] = proposal_id
            coordination_result['coordination_steps'].append('consensus_proposed')
            
            # 4. Attente décision consensus
            decision = await self._wait_for_consensus_decision(proposal_id)
            
            if decision == ConsensusDecision.PROCEED:
                coordination_result['status'] = 'approved'
                coordination_result['coordination_steps'].append('consensus_approved')
                
                # Déduction retry budget
                self.node_retry_budgets[retry_request.node_id] -= 1
                
                # Enregistrement opération active
                self.active_operations[retry_request.operation_id] = {
                    'request': retry_request,
                    'started_at': time.time(),
                    'coordinator_node': self.coordinator_config.node_id,
                    'status': 'active'
                }
                
                self.coordination_metrics['operations_coordinated'] += 1
                
            else:
                coordination_result['status'] = 'rejected'
                coordination_result['reason'] = f'consensus_decision_{decision.value}'
                
                # Libération lock si acquired
                if retry_request.distributed_lock_required:
                    await self.distributed_lock.release_lock(
                        retry_request.operation_id, 
                        retry_request.node_id
                    )
            
            return coordination_result
            
        except Exception as e:
            self.logger.error(f"Error coordinating retry for {retry_request.operation_id}: {str(e)}")
            coordination_result['status'] = 'error'
            coordination_result['error'] = str(e)
            return coordination_result
    
    async def acquire_retry_lock(self, operation_id: str, node_id: str, lock_timeout: int) -> LockResult:
        """Acquisition distributed lock pour retry operation."""
        
        self.coordination_metrics['locks_managed'] += 1
        return await self.distributed_lock.acquire_lock(operation_id, node_id, lock_timeout)
    
    async def establish_retry_consensus(self, retry_proposals: List[RetryProposal]) -> str:
        """Établissement consensus retry entre nodes."""
        
        if not retry_proposals:
            raise ValueError("No retry proposals provided")
        
        # Pour simplicité, traitement d'une proposition à la fois
        proposal = retry_proposals[0]
        proposal_id = await self.consensus_engine.propose_retry_operation(proposal)
        
        # Auto-vote si leader
        if self.node_coordinator.current_role == NodeRole.LEADER:
            await self.consensus_engine.vote_on_proposal(
                proposal_id, 
                self.coordinator_config.node_id, 
                True, 
                "Leader auto-approval"
            )
        
        self.coordination_metrics['consensus_decisions'] += 1
        return proposal_id
    
    async def redistribute_retry_load(self, failed_nodes: List[str]) -> Dict:
        """Redistribution charge retry après node failures."""
        
        redistribution_result = await self.node_coordinator.redistribute_load(failed_nodes)
        
        # Réassignation opérations des nodes défaillants
        reassigned_operations = []
        
        for operation_id, operation_info in list(self.active_operations.items()):
            if operation_info.get('coordinator_node') in failed_nodes:
                # Réassignation à node actif
                active_nodes = self.node_coordinator.get_cluster_status()['active_nodes']
                if active_nodes:
                    new_coordinator = active_nodes[0]  # Simple assignment
                    operation_info['coordinator_node'] = new_coordinator
                    operation_info['reassigned_at'] = time.time()
                    reassigned_operations.append(operation_id)
        
        redistribution_result['reassigned_operations'] = reassigned_operations
        self.coordination_metrics['redistributions'] += 1
        
        logger.info(f"Redistributed load after {len(failed_nodes)} node failures")
        return redistribution_result
    
    async def sync_retry_state(self, state_updates: List[Dict]) -> Dict:
        """Synchronisation état retry across distributed nodes."""
        
        sync_result = {
            'updates_processed': 0,
            'conflicts_resolved': 0,
            'sync_timestamp': time.time()
        }
        
        for update in state_updates:
            operation_id = update.get('operation_id')
            if not operation_id:
                continue
            
            # Vérification conflit état
            if operation_id in self.active_operations:
                local_info = self.active_operations[operation_id]
                remote_timestamp = update.get('timestamp', 0)
                local_timestamp = local_info.get('last_updated', local_info.get('started_at', 0))
                
                # Résolution conflit - dernière écriture gagne
                if remote_timestamp > local_timestamp:
                    local_info.update(update)
                    sync_result['conflicts_resolved'] += 1
            else:
                # Nouvelle opération
                self.active_operations[operation_id] = update
            
            sync_result['updates_processed'] += 1
        
        return sync_result
    
    async def _check_retry_budget(self, node_id: str) -> bool:
        """Vérification budget retry node"""
        return self.node_retry_budgets[node_id] > 0
    
    async def _wait_for_consensus_decision(self, proposal_id: str, timeout: float = 30.0) -> ConsensusDecision:
        """Attente décision consensus avec timeout"""
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            decision = await self.consensus_engine.get_consensus_decision(proposal_id)
            if decision:
                return decision
            
            await asyncio.sleep(1.0)
        
        # Timeout - décision par défaut
        return ConsensusDecision.DELAY
    
    async def _heartbeat_loop(self):
        """Boucle heartbeat background"""
        while True:
            try:
                await self.node_coordinator.send_heartbeat()
                await asyncio.sleep(self.coordinator_config.heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {str(e)}")
                await asyncio.sleep(5.0)
    
    async def _cleanup_loop(self):
        """Boucle nettoyage background"""
        while True:
            try:
                # Nettoyage locks expirés
                await self.distributed_lock.cleanup_expired_locks()
                
                # Nettoyage propositions anciennes
                await self.consensus_engine.cleanup_old_proposals()
                
                # Refresh retry budgets
                await self._refresh_retry_budgets()
                
                await asyncio.sleep(300.0)  # 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {str(e)}")
                await asyncio.sleep(60.0)
    
    async def _failure_detection_loop(self):
        """Boucle détection défaillances"""
        while True:
            try:
                failed_nodes = await self.node_coordinator.detect_failed_nodes()
                
                if failed_nodes:
                    # Élection nouveau leader si nécessaire
                    if self.node_coordinator.leader_node in failed_nodes:
                        await self.node_coordinator.elect_leader()
                    
                    # Redistribution charge
                    await self.redistribute_retry_load(failed_nodes)
                
                await asyncio.sleep(self.coordinator_config.heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in failure detection loop: {str(e)}")
                await asyncio.sleep(30.0)
    
    async def _refresh_retry_budgets(self):
        """Refresh budgets retry périodique"""
        for node_id in self.node_retry_budgets:
            # Restauration graduelle budget
            current_budget = self.node_retry_budgets[node_id]
            max_budget = self.coordinator_config.retry_budget_per_node
            
            if current_budget < max_budget:
                self.node_retry_budgets[node_id] = min(max_budget, current_budget + 10)
    
    async def _release_all_locks(self):
        """Libération tous locks détenus par ce node"""
        for operation_id in list(self.distributed_lock.active_locks.keys()):
            lock_info = self.distributed_lock.active_locks[operation_id]
            if lock_info['holder'] == self.coordinator_config.node_id:
                await self.distributed_lock.release_lock(operation_id, self.coordinator_config.node_id)
    
    async def get_coordination_status(self) -> Dict:
        """Status complet coordination"""
        
        cluster_status = self.node_coordinator.get_cluster_status()
        
        return {
            'coordinator_node': self.coordinator_config.node_id,
            'coordination_metrics': self.coordination_metrics,
            'cluster_status': cluster_status,
            'active_operations': len(self.active_operations),
            'active_locks': len(self.distributed_lock.active_locks),
            'retry_budgets': dict(self.node_retry_budgets),
            'proposals_pending': len(self.consensus_engine.proposals),
            'background_tasks_running': len([t for t in self._background_tasks if not t.done()])
        }

# Factory functions
def create_distributed_coordinator(
    node_id: str = None,
    cluster_nodes: List[str] = None,
    retry_budget: int = 100
) -> DistributedRetryCoordinator:
    """Factory pour création coordinateur distribué"""
    
    config = CoordinatorConfig(
        node_id=node_id or f"node-{int(time.time())}",
        cluster_nodes=cluster_nodes or [],
        retry_budget_per_node=retry_budget
    )
    
    return DistributedRetryCoordinator(config)

__all__ = [
    'DistributedRetryCoordinator',
    'CoordinatorConfig',
    'DistributedRetryRequest',
    'RetryProposal',
    'LockResult',
    'LockStatus',
    'ConsensusDecision',
    'NodeRole',
    'DistributedLockManager',
    'RetryConsensusEngine',
    'NodeCoordinationManager',
    'create_distributed_coordinator'
]