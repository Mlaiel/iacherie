"""Conflict Resolver - Advanced Deadlock Detection and Resolution

Enterprise-grade conflict resolution system providing deadlock detection,
prevention, and resolution for the IA Influencer platform's multi-tenant
creator economy transactions with sophisticated conflict resolution strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

import asyncio
import time
import logging
import threading
from typing import Dict, List, Set, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timezone
import networkx as nx
import heapq
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """
Types of conflicts that can occur"""

    DEADLOCK = "DEADLOCK"                       # Classic deadlock
    LIVELOCK = "LIVELOCK"                       # Livelock situation
    RESOURCE_CONTENTION = "RESOURCE_CONTENTION" # High resource contention
    PRIORITY_INVERSION = "PRIORITY_INVERSION"   # Priority inversion
    STARVATION = "STARVATION"                   # Transaction starvation
    
    # Creator economy specific conflicts
    CREATOR_CONFLICT = "CREATOR_CONFLICT"       # Multiple creators same content
    CONTENT_CONFLICT = "CONTENT_CONFLICT"       # Conflicting content operations
    REVENUE_CONFLICT = "REVENUE_CONFLICT"       # Revenue calculation conflicts
    COLLABORATION_CONFLICT = "COLLABORATION_CONFLICT"  # Collaboration conflicts


class ResolutionStrategy(Enum):
    """Conflict resolution strategies"""

    ABORT_YOUNGEST = "ABORT_YOUNGEST"           # Abort youngest transaction
    ABORT_OLDEST = "ABORT_OLDEST"               # Abort oldest transaction
    ABORT_LOWEST_PRIORITY = "ABORT_LOWEST_PRIORITY"  # Abort lowest priority
    TIMEOUT_BASED = "TIMEOUT_BASED"             # Timeout-based resolution
    WAIT_DIE = "WAIT_DIE"                       # Wait-die algorithm
    WOUND_WAIT = "WOUND_WAIT"                   # Wound-wait algorithm
    
    # Creator economy specific strategies
    CREATOR_PRIORITY = "CREATOR_PRIORITY"       # Creator-based priority
    CONTENT_AGE = "CONTENT_AGE"                 # Content age-based resolution
    REVENUE_IMPACT = "REVENUE_IMPACT"           # Revenue impact-based resolution
    COLLABORATIVE = "COLLABORATIVE"             # Collaborative resolution


@dataclass
class TransactionInfo:
    """Information about a transaction for conflict resolution"""
    transaction_id: str
    created_at: datetime
    priority: int = 0
    creator_id: Optional[str] = None
    content_ids: Set[str] = field(default_factory=set)
    resource_ids: Set[str] = field(default_factory=set)
    estimated_value: float = 0.0  # Business value estimation
    timeout: float = 30.0
    retry_count: int = 0
    business_context: Optional[str] = None
    
    @property
    def age(self) -> float:
        """
Get transaction age in seconds"""
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()
    
    @property
    def is_expired(self) -> bool:
        """
Check if transaction has expired"""
        return self.age > self.timeout


@dataclass
class ConflictInfo:
    """
Information about a detected conflict"""
    conflict_id: str
    conflict_type: ConflictType
    detected_at: datetime
    involved_transactions: List[str]
    involved_resources: List[str]
    conflict_graph: Optional[Dict[str, List[str]]] = None
    severity: float = 0.0  # 0.0 to 1.0
    business_impact: float = 0.0  # Estimated business impact
    resolution_strategy: Optional[ResolutionStrategy] = None
    resolution_time: Optional[float] = None
    resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary for serialization"""
        return {
            'conflict_id': self.conflict_id,
            'conflict_type': self.conflict_type.value,
            'detected_at': self.detected_at.isoformat(),
            'involved_transactions': self.involved_transactions,
            'involved_resources': self.involved_resources,
            'conflict_graph': self.conflict_graph,
            'severity': self.severity,
            'business_impact': self.business_impact,
            'resolution_strategy': self.resolution_strategy.value if self.resolution_strategy else None,
            'resolution_time': self.resolution_time,
            'resolved': self.resolved,
        }


class WaitForGraph:
    """
Wait-for graph for deadlock detection"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.lock = threading.RLock()
        self.node_metadata: Dict[str, TransactionInfo] = {}
    
    def add_transaction(self, transaction_info: TransactionInfo) -> None:
        """
Add transaction to the graph"""
        with self.lock:
            self.graph.add_node(transaction_info.transaction_id)
            self.node_metadata[transaction_info.transaction_id] = transaction_info
    
    def remove_transaction(self, transaction_id: str) -> None:
        """
Remove transaction from the graph"""
        with self.lock:
            if transaction_id in self.graph:
                self.graph.remove_node(transaction_id)
            self.node_metadata.pop(transaction_id, None)
    
    def add_wait_edge(self, waiting_tx: str, blocking_tx: str, resource: str) -> None:
        """
Add wait edge (waiting_tx waits for blocking_tx)"""
        with self.lock:
            if waiting_tx not in self.graph:
                self.graph.add_node(waiting_tx)
            if blocking_tx not in self.graph:
                self.graph.add_node(blocking_tx)
            
            # Add edge with resource information
            self.graph.add_edge(waiting_tx, blocking_tx, resource=resource, 
                              created_at=datetime.now(timezone.utc))
    
    def remove_wait_edge(self, waiting_tx: str, blocking_tx: str) -> None:
        """
Remove wait edge"""
        with self.lock:
            if self.graph.has_edge(waiting_tx, blocking_tx):
                self.graph.remove_edge(waiting_tx, blocking_tx)
    
    def detect_deadlocks(self) -> List[List[str]]:
        """
Detect all deadlocks (cycles) in the wait-for graph"""
        with self.lock:
            try:
                cycles = list(nx.simple_cycles(self.graph))
                return [cycle for cycle in cycles if len(cycle) > 1]
            except Exception as e:
                logger.error("Error detecting deadlocks: %s", str(e))
                return []
    
    def detect_potential_deadlocks(self) -> List[Tuple[str, str, float]]:
        """Detect potential deadlocks based on graph structure"""
        potential_deadlocks = []
        
        with self.lock:
            # Look for long wait chains that could lead to deadlocks
            for node in self.graph.nodes():
                try:
                    # Find all paths from this node
                    reachable = nx.descendants(self.graph, node)
                    
                    for target in reachable:
                        if self.graph.has_edge(target, node):
                            # Potential cycle detected
                            path_length = nx.shortest_path_length(self.graph, node, target)
                            risk_score = 1.0 / (path_length + 1)
                            potential_deadlocks.append((node, target, risk_score))
                            
                except nx.NetworkXError:
                    continue
        
        return sorted(potential_deadlocks, key=lambda x: x[2], reverse=True)
    
    def get_blocking_chain(self, transaction_id: str) -> List[str]:
        """
Get the chain of transactions blocking this transaction"""
        with self.lock:
            chain = [transaction_id]
            current = transaction_id
            
            while True:
                successors = list(self.graph.successors(current))
                if not successors:
                    break
                
                # Follow the longest chain
                next_node = max(successors, key=lambda x: len(list(self.graph.successors(x))))
                
                if next_node in chain:  # Cycle detected
                    break
                
                chain.append(next_node)
                current = next_node
                
                if len(chain) > 100:  # Prevent infinite loops
                    break
            
            return chain
    
    def get_graph_metrics(self) -> Dict[str, Any]:
        """
Get graph metrics for analysis"""
        with self.lock:
            metrics = {
                'node_count': self.graph.number_of_nodes(),
                'edge_count': self.graph.number_of_edges(),
                'density': nx.density(self.graph),
                'is_strongly_connected': nx.is_strongly_connected(self.graph),
                'number_of_cycles': len(list(nx.simple_cycles(self.graph))),
            }
            
            if metrics['node_count'] > 0:
                try:
                    metrics['average_degree'] = sum(dict(self.graph.degree()).values()) / metrics['node_count']
                except:
                    metrics['average_degree'] = 0.0
            else:
                metrics['average_degree'] = 0.0
            
            return metrics


class ResourceContention:
    """
Resource contention tracking and analysis"""
    
    def __init__(self):
        self.resource_requests: Dict[str, List[Tuple[str, datetime, int]]] = defaultdict(list)  # resource -> [(tx_id, timestamp, priority)]
        self.resource_holders: Dict[str, str] = {}  # resource -> tx_id
        self.contention_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'total_requests': 0,
            'average_wait_time': 0.0,
            'max_wait_time': 0.0,
            'current_waiters': 0,
            'contentions_resolved': 0,
        })
        self.lock = threading.RLock()
    
    def add_resource_request(self, transaction_id: str, resource_id: str, priority: int = 0) -> None:
        """
Add resource request"""
        with self.lock:
            request_time = datetime.now(timezone.utc)
            self.resource_requests[resource_id].append((transaction_id, request_time, priority))
            
            metrics = self.contention_metrics[resource_id]
            metrics['total_requests'] += 1
            metrics['current_waiters'] = len(self.resource_requests[resource_id])
    
    def grant_resource(self, transaction_id: str, resource_id: str) -> None:
        """
Grant resource to transaction"""
        with self.lock:
            self.resource_holders[resource_id] = transaction_id
            
            # Remove from requests and update metrics
            requests = self.resource_requests[resource_id]
            for i, (tx_id, request_time, priority) in enumerate(requests):
                if tx_id == transaction_id:
                    wait_time = (datetime.now(timezone.utc) - request_time).total_seconds()
                    
                    metrics = self.contention_metrics[resource_id]
                    metrics['contentions_resolved'] += 1
                    
                    # Update average wait time
                    current_avg = metrics['average_wait_time']
                    resolved_count = metrics['contentions_resolved']
                    metrics['average_wait_time'] = (
                        (current_avg * (resolved_count - 1) + wait_time) / resolved_count
                    )
                    
                    # Update max wait time
                    metrics['max_wait_time'] = max(metrics['max_wait_time'], wait_time)
                    
                    requests.pop(i)
                    break
            
            metrics['current_waiters'] = len(requests)
    
    def release_resource(self, transaction_id: str, resource_id: str) -> None:
        """
Release resource from transaction"""
        with self.lock:
            if self.resource_holders.get(resource_id) == transaction_id:
                del self.resource_holders[resource_id]
    
    def remove_transaction_requests(self, transaction_id: str) -> None:
        """
Remove all requests from a transaction"""
        with self.lock:
            for resource_id in list(self.resource_requests.keys()):
                requests = self.resource_requests[resource_id]
                self.resource_requests[resource_id] = [
                    (tx_id, timestamp, priority) for tx_id, timestamp, priority in requests
                    if tx_id != transaction_id
                ]
                
                metrics = self.contention_metrics[resource_id]
                metrics['current_waiters'] = len(self.resource_requests[resource_id])
    
    def get_high_contention_resources(self, threshold: int = 5) -> List[Tuple[str, int]]:
        """
Get resources with high contention"""
        with self.lock:
            high_contention = []
            
            for resource_id, requests in self.resource_requests.items():
                if len(requests) >= threshold:
                    high_contention.append((resource_id, len(requests)))
            
            return sorted(high_contention, key=lambda x: x[1], reverse=True)
    
    def get_contention_metrics(self, resource_id: str) -> Dict[str, Any]:
        """
Get contention metrics for specific resource"""
        with self.lock:
            return self.contention_metrics[resource_id].copy()


class ConflictResolver:
    """
    Advanced conflict resolver with multiple resolution strategies
    
    Features:
    - Multi-algorithm deadlock detection
    - Resource contention analysis
    - Creator economy aware resolution
    - Predictive conflict prevention
    - Performance impact minimization
    - Business value preservation
    """
    
    def __init__(
        self,
        default_strategy: ResolutionStrategy = ResolutionStrategy.ABORT_YOUNGEST,
        detection_interval: float = 1.0,
        max_resolution_time: float = 5.0
    ):
        self.default_strategy = default_strategy
        self.detection_interval = detection_interval
        self.max_resolution_time = max_resolution_time
        
        # Core components
        self.wait_for_graph = WaitForGraph()
        self.resource_contention = ResourceContention()
        
        # Transaction tracking
        self.active_transactions: Dict[str, TransactionInfo] = {}
        self.resolved_conflicts: List[ConflictInfo] = []
        
        # Performance metrics
        self.metrics = {
            'deadlocks_detected': 0,
            'deadlocks_resolved': 0,
            'conflicts_prevented': 0,
            'average_resolution_time': 0.0,
            'transactions_aborted': 0,
            'false_positives': 0,
        }
        
        # Resolution strategies registry
        self.resolution_strategies: Dict[ResolutionStrategy, Callable] = {
            ResolutionStrategy.ABORT_YOUNGEST: self._abort_youngest_strategy,
            ResolutionStrategy.ABORT_OLDEST: self._abort_oldest_strategy,
            ResolutionStrategy.ABORT_LOWEST_PRIORITY: self._abort_lowest_priority_strategy,
            ResolutionStrategy.TIMEOUT_BASED: self._timeout_based_strategy,
            ResolutionStrategy.WAIT_DIE: self._wait_die_strategy,
            ResolutionStrategy.WOUND_WAIT: self._wound_wait_strategy,
            ResolutionStrategy.CREATOR_PRIORITY: self._creator_priority_strategy,
            ResolutionStrategy.CONTENT_AGE: self._content_age_strategy,
            ResolutionStrategy.REVENUE_IMPACT: self._revenue_impact_strategy,
            ResolutionStrategy.COLLABORATIVE: self._collaborative_strategy,
        }
        
        # Background monitoring
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._monitoring = True
        asyncio.create_task(self._conflict_detection_loop())
        asyncio.create_task(self._contention_monitoring_loop())
        
        logger.info("ConflictResolver initialized with strategy: %s", default_strategy.value)
    
    def register_transaction(self, transaction_info: TransactionInfo) -> None:
        """Register transaction for conflict detection"""
        self.active_transactions[transaction_info.transaction_id] = transaction_info
        self.wait_for_graph.add_transaction(transaction_info)
        
        logger.debug("Registered transaction: %s (creator=%s, priority=%d)",
                    transaction_info.transaction_id, 
                    transaction_info.creator_id, 
                    transaction_info.priority)
    
    def unregister_transaction(self, transaction_id: str) -> None:
        """Unregister transaction"""
        if transaction_id in self.active_transactions:
            del self.active_transactions[transaction_id]
        
        self.wait_for_graph.remove_transaction(transaction_id)
        self.resource_contention.remove_transaction_requests(transaction_id)
        
        logger.debug("Unregistered transaction: %s", transaction_id)
    
    def add_resource_wait(
        self,
        waiting_transaction: str,
        blocking_transaction: str,
        resource_id: str,
        priority: int = 0
    ) -> None:
        """Add resource wait relationship"""
        
        # Add to wait-for graph
        self.wait_for_graph.add_wait_edge(waiting_transaction, blocking_transaction, resource_id)
        
        # Track resource contention
        self.resource_contention.add_resource_request(waiting_transaction, resource_id, priority)
        
        logger.debug("Added wait: %s waits for %s (resource=%s)",
                    waiting_transaction, blocking_transaction, resource_id)
    
    def remove_resource_wait(
        self,
        waiting_transaction: str,
        blocking_transaction: str,
        resource_id: str
    ) -> None:
        """Remove resource wait relationship"""
        
        self.wait_for_graph.remove_wait_edge(waiting_transaction, blocking_transaction)
        self.resource_contention.grant_resource(waiting_transaction, resource_id)
        
        logger.debug("Removed wait: %s no longer waits for %s (resource=%s)",
                    waiting_transaction, blocking_transaction, resource_id)
    
    def release_resource(self, transaction_id: str, resource_id: str) -> None:
        """Release resource from transaction"""
        self.resource_contention.release_resource(transaction_id, resource_id)
        
        logger.debug("Released resource: %s released %s", transaction_id, resource_id)
    
    async def detect_conflicts(self) -> List[ConflictInfo]:
        """Detect all types of conflicts"""
        
        conflicts = []
        
        # Detect deadlocks
        deadlock_conflicts = await self._detect_deadlocks()
        conflicts.extend(deadlock_conflicts)
        
        # Detect resource contention
        contention_conflicts = await self._detect_resource_contention()
        conflicts.extend(contention_conflicts)
        
        # Detect priority inversions
        priority_conflicts = await self._detect_priority_inversions()
        conflicts.extend(priority_conflicts)
        
        # Detect starvation
        starvation_conflicts = await self._detect_starvation()
        conflicts.extend(starvation_conflicts)
        
        # Detect creator economy specific conflicts
        creator_conflicts = await self._detect_creator_conflicts()
        conflicts.extend(creator_conflicts)
        
        return conflicts
    
    async def resolve_conflict(
        self,
        conflict: ConflictInfo,
        strategy: Optional[ResolutionStrategy] = None
    ) -> bool:
        """
Resolve specific conflict using given or default strategy"""
        
        start_time = time.time()
        resolution_strategy = strategy or self._select_optimal_strategy(conflict)
        
        try:
            logger.info("Resolving conflict %s using strategy %s",
                       conflict.conflict_id, resolution_strategy.value)
            
            # Get resolution strategy function
            strategy_func = self.resolution_strategies.get(resolution_strategy)
            if not strategy_func:
                logger.error("Unknown resolution strategy: %s", resolution_strategy)
                return False
            
            # Execute resolution strategy
            success = await strategy_func(conflict)
            
            # Update conflict info
            conflict.resolution_strategy = resolution_strategy
            conflict.resolution_time = time.time() - start_time
            conflict.resolved = success
            
            # Update metrics
            if success:
                self.metrics['deadlocks_resolved'] += 1
                
                # Update average resolution time
                current_avg = self.metrics['average_resolution_time']
                resolved_count = self.metrics['deadlocks_resolved']
                self.metrics['average_resolution_time'] = (
                    (current_avg * (resolved_count - 1) + conflict.resolution_time) / resolved_count
                )
            
            # Store resolved conflict
            self.resolved_conflicts.append(conflict)
            
            # Cleanup old resolved conflicts (keep last 1000)
            if len(self.resolved_conflicts) > 1000:
                self.resolved_conflicts = self.resolved_conflicts[-1000:]
            
            logger.info("Conflict resolution %s: %s (time=%.3fs)",
                       "successful" if success else "failed",
                       conflict.conflict_id, conflict.resolution_time)
            
            return success
            
        except Exception as e:
            logger.error("Error resolving conflict %s: %s", conflict.conflict_id, str(e))
            conflict.resolved = False
            conflict.resolution_time = time.time() - start_time
            return False
    
    async def prevent_conflicts(self) -> int:
        """Proactive conflict prevention"""
        
        prevented_count = 0
        
        # Analyze potential deadlocks
        potential_deadlocks = self.wait_for_graph.detect_potential_deadlocks()
        
        for waiting_tx, blocking_tx, risk_score in potential_deadlocks:
            if risk_score > 0.7:  # High risk threshold
                # Apply preventive measures
                if await self._apply_preventive_measures(waiting_tx, blocking_tx, risk_score):
                    prevented_count += 1
                    self.metrics['conflicts_prevented'] += 1
        
        # Analyze high contention resources
        high_contention = self.resource_contention.get_high_contention_resources()
        
        for resource_id, waiter_count in high_contention:
            if waiter_count > 10:  # High contention threshold
                if await self._reduce_resource_contention(resource_id, waiter_count):
                    prevented_count += 1
                    self.metrics['conflicts_prevented'] += 1
        
        if prevented_count > 0:
            logger.info("Prevented %d potential conflicts", prevented_count)
        
        return prevented_count
    
    def get_conflict_statistics(self) -> Dict[str, Any]:
        """Get comprehensive conflict statistics"""
        
        # Calculate recent conflict rate
        recent_conflicts = [
            c for c in self.resolved_conflicts
            if (datetime.now(timezone.utc) - c.detected_at).total_seconds() < 3600
        ]
        
        # Get graph metrics
        graph_metrics = self.wait_for_graph.get_graph_metrics()
        
        # Get contention metrics
        high_contention = self.resource_contention.get_high_contention_resources()
        
        statistics = {
            'active_transactions': len(self.active_transactions),
            'recent_conflicts_1h': len(recent_conflicts),
            'total_resolved_conflicts': len(self.resolved_conflicts),
            'high_contention_resources': len(high_contention),
            'wait_for_graph': graph_metrics,
            'metrics': self.metrics.copy(),
            'default_strategy': self.default_strategy.value,
        }
        
        # Add conflict type distribution
        conflict_types = defaultdict(int)
        for conflict in self.resolved_conflicts[-100:]:  # Last 100 conflicts
            conflict_types[conflict.conflict_type.value] += 1
        
        statistics['conflict_type_distribution'] = dict(conflict_types)
        
        # Add resolution strategy effectiveness
        strategy_success = defaultdict(lambda: {'total': 0, 'successful': 0})
        for conflict in self.resolved_conflicts[-100:]:
            if conflict.resolution_strategy:
                strategy = conflict.resolution_strategy.value
                strategy_success[strategy]['total'] += 1
                if conflict.resolved:
                    strategy_success[strategy]['successful'] += 1
        
        strategy_effectiveness = {}
        for strategy, stats in strategy_success.items():
            effectiveness = stats['successful'] / stats['total'] if stats['total'] > 0 else 0.0
            strategy_effectiveness[strategy] = {
                'effectiveness': effectiveness,
                'total_uses': stats['total'],
                'successful_uses': stats['successful'],
            }
        
        statistics['strategy_effectiveness'] = strategy_effectiveness
        
        return statistics
    
    async def _detect_deadlocks(self) -> List[ConflictInfo]:
        """
Detect deadlocks in wait-for graph"""
        
        deadlocks = self.wait_for_graph.detect_deadlocks()
        conflicts = []
        
        for cycle in deadlocks:
            if len(cycle) > 1:  # Ensure it's actually a cycle
                conflict = ConflictInfo(
                    conflict_id=f"deadlock_{int(time.time())}_{hash(tuple(cycle)) % 10000}",
                    conflict_type=ConflictType.DEADLOCK,
                    detected_at=datetime.now(timezone.utc),
                    involved_transactions=cycle,
                    involved_resources=self._get_cycle_resources(cycle),
                    conflict_graph={tx: self._get_blocking_transactions(tx) for tx in cycle},
                    severity=self._calculate_deadlock_severity(cycle),
                    business_impact=self._calculate_business_impact(cycle),
                )
                
                conflicts.append(conflict)
                self.metrics['deadlocks_detected'] += 1
                
                logger.warning("Deadlock detected: %s (transactions=%s)",
                             conflict.conflict_id, cycle)
        
        return conflicts
    
    async def _detect_resource_contention(self) -> List[ConflictInfo]:
        """Detect high resource contention"""
        
        conflicts = []
        high_contention = self.resource_contention.get_high_contention_resources()
        
        for resource_id, waiter_count in high_contention:
            if waiter_count > 15:  # Very high contention threshold
                # Get transactions waiting for this resource
                waiting_transactions = []
                for tx_id, requests in self.resource_contention.resource_requests.items():
                    if resource_id in [req[0] for req in requests]:
                        waiting_transactions.extend([req[0] for req in requests])
                
                conflict = ConflictInfo(
                    conflict_id=f"contention_{resource_id}_{int(time.time())}",
                    conflict_type=ConflictType.RESOURCE_CONTENTION,
                    detected_at=datetime.now(timezone.utc),
                    involved_transactions=list(set(waiting_transactions)),
                    involved_resources=[resource_id],
                    severity=min(1.0, waiter_count / 20.0),  # Normalize to 0-1
                    business_impact=self._calculate_contention_business_impact(resource_id, waiter_count),
                )
                
                conflicts.append(conflict)
                
                logger.warning("High resource contention detected: %s (%d waiters)",
                             resource_id, waiter_count)
        
        return conflicts
    
    async def _detect_priority_inversions(self) -> List[ConflictInfo]:
        """Detect priority inversion situations"""
        
        conflicts = []
        
        # Check for situations where high-priority transactions wait for low-priority ones
        for tx_id, tx_info in self.active_transactions.items():
            if tx_info.priority > 5:  # High priority transaction
                blocking_chain = self.wait_for_graph.get_blocking_chain(tx_id)
                
                for blocking_tx_id in blocking_chain[1:]:  # Exclude self
                    blocking_tx_info = self.active_transactions.get(blocking_tx_id)
                    
                    if blocking_tx_info and blocking_tx_info.priority < tx_info.priority - 3:
                        conflict = ConflictInfo(
                            conflict_id=f"priority_inversion_{tx_id}_{blocking_tx_id}_{int(time.time())}",
                            conflict_type=ConflictType.PRIORITY_INVERSION,
                            detected_at=datetime.now(timezone.utc),
                            involved_transactions=[tx_id, blocking_tx_id],
                            involved_resources=list(tx_info.resource_ids),
                            severity=0.7,  # Priority inversions are serious
                            business_impact=tx_info.estimated_value * 0.5,
                        )
                        
                        conflicts.append(conflict)
                        
                        logger.warning("Priority inversion detected: high priority %s blocked by low priority %s",
                                     tx_id, blocking_tx_id)
                        break  # One conflict per high-priority transaction
        
        return conflicts
    
    async def _detect_starvation(self) -> List[ConflictInfo]:
        """Detect transaction starvation"""
        
        conflicts = []
        current_time = datetime.now(timezone.utc)
        
        for tx_id, tx_info in self.active_transactions.items():
            # Check if transaction has been waiting too long
            if tx_info.age > tx_info.timeout * 2:  # Double the normal timeout
                conflict = ConflictInfo(
                    conflict_id=f"starvation_{tx_id}_{int(time.time())}",
                    conflict_type=ConflictType.STARVATION,
                    detected_at=current_time,
                    involved_transactions=[tx_id],
                    involved_resources=list(tx_info.resource_ids),
                    severity=min(1.0, tx_info.age / (tx_info.timeout * 4)),
                    business_impact=tx_info.estimated_value,
                )
                
                conflicts.append(conflict)
                
                logger.warning("Transaction starvation detected: %s (age=%.1fs, timeout=%.1fs)",
                             tx_id, tx_info.age, tx_info.timeout)
        
        return conflicts
    
    async def _detect_creator_conflicts(self) -> List[ConflictInfo]:
        """Detect creator economy specific conflicts"""
        
        conflicts = []
        
        # Group transactions by creator
        creator_transactions = defaultdict(list)
        for tx_id, tx_info in self.active_transactions.items():
            if tx_info.creator_id:
                creator_transactions[tx_info.creator_id].append((tx_id, tx_info))
        
        # Check for conflicts within creator transactions
        for creator_id, transactions in creator_transactions.items():
            if len(transactions) > 5:  # Many concurrent transactions for one creator
                tx_ids = [tx_id for tx_id, _ in transactions]
                
                conflict = ConflictInfo(
                    conflict_id=f"creator_conflict_{creator_id}_{int(time.time())}",
                    conflict_type=ConflictType.CREATOR_CONFLICT,
                    detected_at=datetime.now(timezone.utc),
                    involved_transactions=tx_ids,
                    involved_resources=[f"creator_{creator_id}"],
                    severity=0.6,
                    business_impact=sum(tx_info.estimated_value for _, tx_info in transactions),
                )
                
                conflicts.append(conflict)
                
                logger.warning("Creator conflict detected: %s has %d concurrent transactions",
                             creator_id, len(transactions))
        
        # Check for content conflicts
        content_transactions = defaultdict(list)
        for tx_id, tx_info in self.active_transactions.items():
            for content_id in tx_info.content_ids:
                content_transactions[content_id].append((tx_id, tx_info))
        
        for content_id, transactions in content_transactions.items():
            if len(transactions) > 2:  # Multiple transactions on same content
                tx_ids = [tx_id for tx_id, _ in transactions]
                
                conflict = ConflictInfo(
                    conflict_id=f"content_conflict_{content_id}_{int(time.time())}",
                    conflict_type=ConflictType.CONTENT_CONFLICT,
                    detected_at=datetime.now(timezone.utc),
                    involved_transactions=tx_ids,
                    involved_resources=[f"content_{content_id}"],
                    severity=0.8,  # Content conflicts are serious
                    business_impact=sum(tx_info.estimated_value for _, tx_info in transactions),
                )
                
                conflicts.append(conflict)
                
                logger.warning("Content conflict detected: content %s has %d concurrent transactions",
                             content_id, len(transactions))
        
        return conflicts
    
    def _select_optimal_strategy(self, conflict: ConflictInfo) -> ResolutionStrategy:
        """Select optimal resolution strategy based on conflict characteristics"""
        
        # Strategy selection based on conflict type
        if conflict.conflict_type == ConflictType.DEADLOCK:
            # For deadlocks, prefer strategies that minimize business impact
            if conflict.business_impact > 1000:  # High business impact
                return ResolutionStrategy.REVENUE_IMPACT
            else:
                return ResolutionStrategy.ABORT_YOUNGEST
        
        elif conflict.conflict_type == ConflictType.RESOURCE_CONTENTION:
            return ResolutionStrategy.TIMEOUT_BASED
        
        elif conflict.conflict_type == ConflictType.PRIORITY_INVERSION:
            return ResolutionStrategy.ABORT_LOWEST_PRIORITY
        
        elif conflict.conflict_type == ConflictType.STARVATION:
            return ResolutionStrategy.ABORT_OLDEST  # Give starved transaction a chance
        
        elif conflict.conflict_type == ConflictType.CREATOR_CONFLICT:
            return ResolutionStrategy.CREATOR_PRIORITY
        
        elif conflict.conflict_type == ConflictType.CONTENT_CONFLICT:
            return ResolutionStrategy.CONTENT_AGE
        
        elif conflict.conflict_type == ConflictType.COLLABORATION_CONFLICT:
            return ResolutionStrategy.COLLABORATIVE
        
        # Default strategy
        return self.default_strategy
    
    async def _abort_youngest_strategy(self, conflict: ConflictInfo) -> bool:
        """
Abort youngest transaction in conflict"""
        
        youngest_tx = None
        youngest_age = float('inf')
        
        for tx_id in conflict.involved_transactions:
            tx_info = self.active_transactions.get(tx_id)
            if tx_info and tx_info.age < youngest_age:
                youngest_age = tx_info.age
                youngest_tx = tx_id
        
        if youngest_tx:
            await self._abort_transaction(youngest_tx, "youngest_transaction_abort")
            self.metrics['transactions_aborted'] += 1
            return True
        
        return False
    
    async def _abort_oldest_strategy(self, conflict: ConflictInfo) -> bool:
        """Abort oldest transaction in conflict"""
        
        oldest_tx = None
        oldest_age = 0
        
        for tx_id in conflict.involved_transactions:
            tx_info = self.active_transactions.get(tx_id)
            if tx_info and tx_info.age > oldest_age:
                oldest_age = tx_info.age
                oldest_tx = tx_id
        
        if oldest_tx:
            await self._abort_transaction(oldest_tx, "oldest_transaction_abort")
            self.metrics['transactions_aborted'] += 1
            return True
        
        return False
    
    async def _abort_lowest_priority_strategy(self, conflict: ConflictInfo) -> bool:
        """Abort lowest priority transaction in conflict"""
        
        lowest_priority_tx = None
        lowest_priority = float('inf')
        
        for tx_id in conflict.involved_transactions:
            tx_info = self.active_transactions.get(tx_id)
            if tx_info and tx_info.priority < lowest_priority:
                lowest_priority = tx_info.priority
                lowest_priority_tx = tx_id
        
        if lowest_priority_tx:
            await self._abort_transaction(lowest_priority_tx, "lowest_priority_abort")
            self.metrics['transactions_aborted'] += 1
            return True
        
        return False
    
    async def _timeout_based_strategy(self, conflict: ConflictInfo) -> bool:
        """Abort expired transactions"""
        
        aborted_count = 0
        
        for tx_id in conflict.involved_transactions:
            tx_info = self.active_transactions.get(tx_id)
            if tx_info and tx_info.is_expired:
                await self._abort_transaction(tx_id, "timeout_abort")
                aborted_count += 1
        
        if aborted_count > 0:
            self.metrics['transactions_aborted'] += aborted_count
            return True
        
        return False
    
    async def _wait_die_strategy(self, conflict: ConflictInfo) -> bool:
        """Wait-die algorithm implementation"""
        
        # In wait-die, older transactions wait, younger transactions die
        for tx_id in conflict.involved_transactions:
            tx_info = self.active_transactions.get(tx_id)
            if not tx_info:
                continue
            
            # Check if this transaction is younger than any it's waiting for
            blocking_chain = self.wait_for_graph.get_blocking_chain(tx_id)
            
            for blocking_tx_id in blocking_chain[1:]:
                blocking_tx_info = self.active_transactions.get(blocking_tx_id)
                
                if blocking_tx_info and tx_info.created_at > blocking_tx_info.created_at:
                    # Younger transaction dies
                    await self._abort_transaction(tx_id, "wait_die_abort")
                    self.metrics['transactions_aborted'] += 1
                    return True
        
        return False
    
    async def _wound_wait_strategy(self, conflict: ConflictInfo) -> bool:
        """Wound-wait algorithm implementation"""
        
        # In wound-wait, older transactions wound (preempt) younger transactions
        for tx_id in conflict.involved_transactions:
            tx_info = self.active_transactions.get(tx_id)
            if not tx_info:
                continue
            
            # Check if this transaction is older than any blocking it
            blocking_chain = self.wait_for_graph.get_blocking_chain(tx_id)
            
            for blocking_tx_id in blocking_chain[1:]:
                blocking_tx_info = self.active_transactions.get(blocking_tx_id)
                
                if blocking_tx_info and tx_info.created_at < blocking_tx_info.created_at:
                    # Older transaction wounds younger
                    await self._abort_transaction(blocking_tx_id, "wound_wait_abort")
                    self.metrics['transactions_aborted'] += 1
                    return True
        
        return False
    
    async def _creator_priority_strategy(self, conflict: ConflictInfo) -> bool:
        """Creator-based priority resolution"""
        
        # Prioritize based on creator business metrics
        creator_priorities = {}
        
        for tx_id in conflict.involved_transactions:
            tx_info = self.active_transactions.get(tx_id)
            if tx_info and tx_info.creator_id:
                # Calculate creator priority (could be based on revenue, subscriber count, etc.)
                creator_priority = self._calculate_creator_priority(tx_info.creator_id)
                creator_priorities[tx_id] = creator_priority
        
        if creator_priorities:
            # Abort transaction with lowest creator priority
            lowest_priority_tx = min(creator_priorities.items(), key=lambda x: x[1])[0]
            await self._abort_transaction(lowest_priority_tx, "creator_priority_abort")
            self.metrics['transactions_aborted'] += 1
            return True
        
        return False
    
    async def _content_age_strategy(self, conflict: ConflictInfo) -> bool:
        """Content age-based resolution"""
        
        # Prioritize transactions dealing with newer content
        content_ages = {}
        
        for tx_id in conflict.involved_transactions:
            tx_info = self.active_transactions.get(tx_id)
            if tx_info and tx_info.content_ids:
                # Calculate average content age (mock implementation)
                avg_age = sum(self._get_content_age(cid) for cid in tx_info.content_ids) / len(tx_info.content_ids)
                content_ages[tx_id] = avg_age
        
        if content_ages:
            # Abort transaction with oldest content
            oldest_content_tx = max(content_ages.items(), key=lambda x: x[1])[0]
            await self._abort_transaction(oldest_content_tx, "content_age_abort")
            self.metrics['transactions_aborted'] += 1
            return True
        
        return False
    
    async def _revenue_impact_strategy(self, conflict: ConflictInfo) -> bool:
        """Revenue impact-based resolution"""
        
        # Abort transaction with lowest revenue impact
        lowest_impact_tx = None
        lowest_impact = float('inf')
        
        for tx_id in conflict.involved_transactions:
            tx_info = self.active_transactions.get(tx_id)
            if tx_info and tx_info.estimated_value < lowest_impact:
                lowest_impact = tx_info.estimated_value
                lowest_impact_tx = tx_id
        
        if lowest_impact_tx:
            await self._abort_transaction(lowest_impact_tx, "revenue_impact_abort")
            self.metrics['transactions_aborted'] += 1
            return True
        
        return False
    
    async def _collaborative_strategy(self, conflict: ConflictInfo) -> bool:
        """Collaborative resolution strategy"""
        
        # Try to resolve conflicts through resource sharing or partial completion
        # This is a simplified implementation - real collaborative resolution
        # would involve more sophisticated negotiation
        
        # For now, just timeout the longest running transaction
        longest_running_tx = None
        longest_age = 0
        
        for tx_id in conflict.involved_transactions:
            tx_info = self.active_transactions.get(tx_id)
            if tx_info and tx_info.age > longest_age:
                longest_age = tx_info.age
                longest_running_tx = tx_id
        
        if longest_running_tx and longest_age > 30:  # 30 second threshold
            await self._abort_transaction(longest_running_tx, "collaborative_timeout")
            self.metrics['transactions_aborted'] += 1
            return True
        
        return False
    
    async def _abort_transaction(self, transaction_id: str, reason: str) -> None:
        """Abort transaction and clean up"""
        
        logger.info("Aborting transaction %s (reason: %s)", transaction_id, reason)
        
        # Remove from tracking
        self.unregister_transaction(transaction_id)
        
        # In a real implementation, this would trigger the actual transaction abort
        # through the transaction coordinator
    
    def _get_cycle_resources(self, cycle: List[str]) -> List[str]:
        """Get resources involved in a deadlock cycle"""
        
        resources = set()
        
        for i in range(len(cycle)):
            current_tx = cycle[i]
            next_tx = cycle[(i + 1) % len(cycle)]
            
            # Get edge data
            if self.wait_for_graph.graph.has_edge(current_tx, next_tx):
                edge_data = self.wait_for_graph.graph.get_edge_data(current_tx, next_tx)
                if edge_data and 'resource' in edge_data:
                    resources.add(edge_data['resource'])
        
        return list(resources)
    
    def _get_blocking_transactions(self, transaction_id: str) -> List[str]:
        """
Get transactions blocking this transaction"""
        
        return list(self.wait_for_graph.graph.successors(transaction_id))
    
    def _calculate_deadlock_severity(self, cycle: List[str]) -> float:
        """
Calculate deadlock severity based on involved transactions"""
        
        severity = 0.5  # Base severity
        
        # Increase severity based on cycle length
        severity += min(0.3, len(cycle) * 0.05)
        
        # Increase severity based on transaction priorities
        total_priority = 0
        for tx_id in cycle:
            tx_info = self.active_transactions.get(tx_id)
            if tx_info:
                total_priority += tx_info.priority
        
        severity += min(0.2, total_priority * 0.01)
        
        return min(1.0, severity)
    
    def _calculate_business_impact(self, transaction_ids: List[str]) -> float:
        """
Calculate business impact of conflict"""
        
        total_impact = 0.0
        
        for tx_id in transaction_ids:
            tx_info = self.active_transactions.get(tx_id)
            if tx_info:
                total_impact += tx_info.estimated_value
        
        return total_impact
    
    def _calculate_contention_business_impact(self, resource_id: str, waiter_count: int) -> float:
        """
Calculate business impact of resource contention"""
        
        # Simple impact calculation based on waiting transactions
        return waiter_count * 10.0  # Mock calculation
    
    def _calculate_creator_priority(self, creator_id: str) -> float:
        """
Calculate creator priority (mock implementation)"""
        
        # In a real implementation, this would look up creator metrics
        return hash(creator_id) % 100  # Mock priority
    
    def _get_content_age(self, content_id: str) -> float:
        """
Get content age in days (mock implementation)"""
        
        # In a real implementation, this would look up content creation date
        return hash(content_id) % 365  # Mock age in days
    
    async def _apply_preventive_measures(
        self,
        waiting_tx: str,
        blocking_tx: str,
        risk_score: float
    ) -> bool:
        """
Apply preventive measures for potential deadlock"""
        
        # Simple prevention: increase timeout for high-risk waiting transaction
        tx_info = self.active_transactions.get(waiting_tx)
        if tx_info and risk_score > 0.8:
            tx_info.timeout *= 1.5  # Increase timeout by 50%
            logger.debug("Applied preventive timeout increase for transaction %s", waiting_tx)
            return True
        
        return False
    
    async def _reduce_resource_contention(self, resource_id: str, waiter_count: int) -> bool:
        """Reduce resource contention through various strategies"""
        
        # Simple contention reduction: abort some waiting transactions
        if waiter_count > 20:
            # Abort oldest waiting transactions
            requests = self.resource_contention.resource_requests.get(resource_id, [])
            if requests:
                # Sort by timestamp and abort oldest
                sorted_requests = sorted(requests, key=lambda x: x[1])
                aborts_needed = min(5, waiter_count // 4)  # Abort up to 25% of waiters
                
                for i in range(aborts_needed):
                    tx_id = sorted_requests[i][0]
                    await self._abort_transaction(tx_id, "contention_reduction")
                
                logger.info("Reduced contention on %s by aborting %d transactions",
                           resource_id, aborts_needed)
                return True
        
        return False
    
    async def _conflict_detection_loop(self) -> None:
        """Background conflict detection loop"""
        
        while self._monitoring:
            try:
                conflicts = await self.detect_conflicts()
                
                for conflict in conflicts:
                    await self.resolve_conflict(conflict)
                
                # Preventive measures
                await self.prevent_conflicts()
                
                await asyncio.sleep(self.detection_interval)
                
            except Exception as e:
                logger.error("Error in conflict detection loop: %s", str(e))
                await asyncio.sleep(1)
    
    async def _contention_monitoring_loop(self) -> None:
        """Background contention monitoring loop"""
        
        while self._monitoring:
            try:
                # Monitor high contention resources
                high_contention = self.resource_contention.get_high_contention_resources()
                
                for resource_id, waiter_count in high_contention:
                    if waiter_count > 25:  # Critical contention level
                        logger.warning("Critical resource contention: %s (%d waiters)",
                                     resource_id, waiter_count)
                        
                        # Apply immediate contention reduction
                        await self._reduce_resource_contention(resource_id, waiter_count)
                
                await asyncio.sleep(5.0)  # Monitor every 5 seconds
                
            except Exception as e:
                logger.error("Error in contention monitoring loop: %s", str(e))
                await asyncio.sleep(1)
    
    async def shutdown(self) -> None:
        """Graceful shutdown of conflict resolver"""
        logger.info("Shutting down ConflictResolver...")
        
        self._monitoring = False
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("ConflictResolver shutdown complete")


# Convenience class for simplified deadlock detection
class DeadlockDetector:
    """Simplified deadlock detector for backward compatibility"""
    
    def __init__(self):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing start_detection")
            
            # Implementation for start_detection
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"start_detection completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"start_detection failed: {e}")
            raise
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    def start_detection(self):
        """
Start deadlock detection"""
        # Already started in ConflictResolver constructor
        pass
    
    def stop_detection(self):
        """
Stop deadlock detection"""
        asyncio.create_task(self.conflict_resolver.shutdown())
    
    def add_wait_edge(self, waiting_tx: str, blocking_tx: str):
        """
Add wait edge"""
        self.conflict_resolver.add_resource_wait(waiting_tx, blocking_tx, "unknown_resource")
    
    def remove_wait_edge(self, waiting_tx: str, blocking_tx: str):
        """Remove wait edge"""
        self.conflict_resolver.remove_resource_wait(waiting_tx, blocking_tx, "unknown_resource")
    
    def detect_deadlock(self) -> Optional[List[str]]:
        """Detect deadlock (synchronous version)"""
        deadlocks = self.conflict_resolver.wait_for_graph.detect_deadlocks()
        return deadlocks[0] if deadlocks else None
