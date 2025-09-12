"""
Master Election Controller for Redis Enterprise
Backend Senior + Microservices Implementation - High Availability Master Election

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import socket
import uuid
import redis.asyncio as redis
from config.core.redis import RedisSettings

logger = logging.getLogger(__name__)

class NodeState(Enum):
    """Redis node states in cluster"""
    MASTER = "master"
    REPLICA = "replica"
    CANDIDATE = "candidate"
    FOLLOWER = "follower"
    FAILED = "failed"
    RECOVERING = "recovering"

class ElectionPhase(Enum):
    """Election phases"""
    IDLE = "idle"
    CANDIDATE = "candidate"
    VOTING = "voting"
    LEADER_ELECTED = "leader_elected"
    SPLIT_BRAIN_DETECTION = "split_brain_detection"

@dataclass
class NodeInfo:
    """Information about a Redis node"""
    node_id: str
    host: str
    port: int
    state: NodeState
    last_seen: datetime
    health_score: float = 100.0
    replication_lag: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    connections: int = 0
    uptime: int = 0
    is_available: bool = True
    priority: int = 50  # Election priority (0-100)
    
@dataclass
class Election:
    """Election information"""
    election_id: str
    term: int
    phase: ElectionPhase
    started_at: datetime
    candidates: Set[str] = field(default_factory=set)
    votes: Dict[str, str] = field(default_factory=dict)  # voter_id -> candidate_id
    winner: Optional[str] = None
    completed_at: Optional[datetime] = None

@dataclass
class MasterInfo:
    """Current master information"""
    node_id: str
    host: str
    port: int
    elected_at: datetime
    term: int
    last_heartbeat: datetime
    failover_count: int = 0

class MasterElectionController:
    """
    Enterprise master election controller for Redis high availability
    Backend Senior + Microservices implementation with Raft-like consensus
    """
    
    def __init__(self, redis_settings: RedisSettings, node_id: Optional[str] = None):
        self.redis_settings = redis_settings
        self.node_id = node_id or self._generate_node_id()
        self.redis_client: Optional[redis.Redis] = None
        
        # Cluster state
        self.nodes: Dict[str, NodeInfo] = {}
        self.current_master: Optional[MasterInfo] = None
        self.current_election: Optional[Election] = None
        self.my_state = NodeState.FOLLOWER
        self.current_term = 0
        self.voted_for: Optional[str] = None
        
        # Election configuration
        self.election_timeout = 5.0  # seconds
        self.heartbeat_interval = 1.0  # seconds
        self.vote_timeout = 3.0  # seconds
        self.min_nodes_for_election = 3
        self.master_failure_threshold = 3  # missed heartbeats
        
        # Redis keys for coordination
        self.cluster_key = "ainflue:cluster:nodes"
        self.master_key = "ainflue:cluster:master"
        self.election_key = "ainflue:cluster:election"
        self.heartbeat_key = "ainflue:cluster:heartbeat"
        self.term_key = "ainflue:cluster:term"
        
        # Event callbacks
        self.on_master_elected: Optional[Callable[[MasterInfo], None]] = None
        self.on_master_failed: Optional[Callable[[str], None]] = None
        self.on_election_started: Optional[Callable[[Election], None]] = None
        
        # Background tasks
        self._running = False
        self._tasks: List[asyncio.Task] = []
        
        # Node information
        self.my_node_info = NodeInfo(
            node_id=self.node_id,
            host=self.redis_settings.redis_host,
            port=self.redis_settings.redis_port,
            state=NodeState.FOLLOWER,
            last_seen=datetime.utcnow(),
            priority=50  # Default priority
        )
    
    def _generate_node_id(self) -> str:
        """Generate unique node ID"""
        hostname = socket.gethostname()
        timestamp = int(time.time())
        random_id = uuid.uuid4().hex[:8]
        return f"{hostname}-{timestamp}-{random_id}"
    
    async def initialize(self):
        """Initialize the master election controller"""
        try:
            # Connect to Redis
            self.redis_client = redis.from_url(
                self.redis_settings.redis_dsn,
                encoding='utf-8',
                decode_responses=True,
                max_connections=self.redis_settings.redis_max_connections
            )
            
            # Test connection
            await self.redis_client.ping()
            
            # Load current cluster state
            await self._load_cluster_state()
            
            # Register this node
            await self._register_node()
            
            # Start background tasks
            self._running = True
            self._tasks = [
                asyncio.create_task(self._heartbeat_loop()),
                asyncio.create_task(self._monitor_cluster()),
                asyncio.create_task(self._election_manager()),
                asyncio.create_task(self._health_monitor())
            ]
            
            logger.info(f"Master Election Controller initialized for node {self.node_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Master Election Controller: {e}")
            raise
    
    async def _load_cluster_state(self):
        """Load current cluster state from Redis"""
        try:
            # Load nodes
            nodes_data = await self.redis_client.hgetall(self.cluster_key)
            for node_id, node_json in nodes_data.items():
                try:
                    node_data = json.loads(node_json)
                    node_info = NodeInfo(**node_data)
                    self.nodes[node_id] = node_info
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse node data for {node_id}: {e}")
            
            # Load current master
            master_data = await self.redis_client.get(self.master_key)
            if master_data:
                try:
                    master_info_data = json.loads(master_data)
                    self.current_master = MasterInfo(**master_info_data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse master data: {e}")
            
            # Load current term
            term_data = await self.redis_client.get(self.term_key)
            if term_data:
                self.current_term = int(term_data)
            
            # Load current election
            election_data = await self.redis_client.get(self.election_key)
            if election_data:
                try:
                    election_info_data = json.loads(election_data)
                    self.current_election = Election(**election_info_data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse election data: {e}")
                    
        except Exception as e:
            logger.error(f"Error loading cluster state: {e}")
    
    async def _register_node(self):
        """Register this node in the cluster"""
        try:
            # Update node information
            self.my_node_info.last_seen = datetime.utcnow()
            
            # Store in Redis
            node_json = json.dumps({
                'node_id': self.my_node_info.node_id,
                'host': self.my_node_info.host,
                'port': self.my_node_info.port,
                'state': self.my_node_info.state.value,
                'last_seen': self.my_node_info.last_seen.isoformat(),
                'health_score': self.my_node_info.health_score,
                'priority': self.my_node_info.priority,
                'is_available': self.my_node_info.is_available
            })
            
            await self.redis_client.hset(self.cluster_key, self.node_id, node_json)
            self.nodes[self.node_id] = self.my_node_info
            
            logger.info(f"Node {self.node_id} registered in cluster")
            
        except Exception as e:
            logger.error(f"Error registering node: {e}")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats"""
        while self._running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                if self.my_state == NodeState.MASTER:
                    await self._send_master_heartbeat()
                else:
                    await self._send_node_heartbeat()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(1)
    
    async def _send_master_heartbeat(self):
        """Send master heartbeat to all nodes"""
        try:
            if not self.current_master or self.current_master.node_id != self.node_id:
                return
            
            heartbeat_data = {
                'master_id': self.node_id,
                'term': self.current_term,
                'timestamp': datetime.utcnow().isoformat(),
                'health_score': self.my_node_info.health_score
            }
            
            await self.redis_client.set(
                f"{self.heartbeat_key}:master",
                json.dumps(heartbeat_data),
                ex=int(self.heartbeat_interval * 3)  # TTL
            )
            
            # Update master info
            self.current_master.last_heartbeat = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error sending master heartbeat: {e}")
    
    async def _send_node_heartbeat(self):
        """Send node heartbeat"""
        try:
            # Update node information
            await self._update_node_metrics()
            await self._register_node()
            
        except Exception as e:
            logger.error(f"Error sending node heartbeat: {e}")
    
    async def _update_node_metrics(self):
        """Update node health metrics"""
        try:
            # Get Redis info for metrics
            info = await self.redis_client.info()
            
            self.my_node_info.memory_usage = info.get('used_memory_percentage', 0)
            self.my_node_info.connections = info.get('connected_clients', 0)
            self.my_node_info.uptime = info.get('uptime_in_seconds', 0)
            
            # Calculate health score based on metrics
            health_score = 100.0
            
            # Penalize high memory usage
            if self.my_node_info.memory_usage > 80:
                health_score -= (self.my_node_info.memory_usage - 80) * 2
            
            # Penalize high connection count
            max_connections = self.redis_settings.redis_max_connections
            if self.my_node_info.connections > max_connections * 0.8:
                health_score -= 10
            
            # Bonus for longer uptime (stability)
            if self.my_node_info.uptime > 3600:  # 1 hour
                health_score += min(5, self.my_node_info.uptime / 3600)
            
            self.my_node_info.health_score = max(0, min(100, health_score))
            self.my_node_info.last_seen = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error updating node metrics: {e}")
    
    async def _monitor_cluster(self):
        """Monitor cluster health and detect master failures"""
        while self._running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                # Check master health
                if self.current_master and self.my_state != NodeState.MASTER:
                    await self._check_master_health()
                
                # Clean up stale nodes
                await self._cleanup_stale_nodes()
                
                # Update cluster view
                await self._update_cluster_view()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cluster monitor: {e}")
                await asyncio.sleep(1)
    
    async def _check_master_health(self):
        """Check if current master is healthy"""
        try:
            if not self.current_master:
                return
            
            # Check master heartbeat
            heartbeat_data = await self.redis_client.get(f"{self.heartbeat_key}:master")
            
            if not heartbeat_data:
                logger.warning("No master heartbeat found")
                await self._handle_master_failure()
                return
            
            try:
                heartbeat_info = json.loads(heartbeat_data)
                last_heartbeat = datetime.fromisoformat(heartbeat_info['timestamp'])
                
                # Check if heartbeat is recent
                time_since_heartbeat = (datetime.utcnow() - last_heartbeat).total_seconds()
                
                if time_since_heartbeat > self.heartbeat_interval * self.master_failure_threshold:
                    logger.warning(f"Master heartbeat timeout: {time_since_heartbeat}s")
                    await self._handle_master_failure()
                    
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Invalid master heartbeat data: {e}")
                await self._handle_master_failure()
                
        except Exception as e:
            logger.error(f"Error checking master health: {e}")
    
    async def _handle_master_failure(self):
        """Handle master failure detection"""
        try:
            if self.current_master:
                logger.warning(f"Master failure detected: {self.current_master.node_id}")
                
                # Notify callbacks
                if self.on_master_failed:
                    try:
                        await self.on_master_failed(self.current_master.node_id)
                    except Exception as e:
                        logger.error(f"Error in master failure callback: {e}")
                
                # Clear master
                self.current_master = None
                await self.redis_client.delete(self.master_key)
                
                # Trigger election if not already in progress
                if not self.current_election or self.current_election.phase == ElectionPhase.IDLE:
                    await self._start_election()
                    
        except Exception as e:
            logger.error(f"Error handling master failure: {e}")
    
    async def _cleanup_stale_nodes(self):
        """Remove stale nodes from cluster view"""
        try:
            now = datetime.utcnow()
            stale_timeout = timedelta(seconds=self.heartbeat_interval * 5)
            
            stale_nodes = []
            for node_id, node_info in self.nodes.items():
                if node_id != self.node_id:  # Don't remove ourselves
                    time_since_seen = now - node_info.last_seen
                    if time_since_seen > stale_timeout:
                        stale_nodes.append(node_id)
            
            # Remove stale nodes
            for node_id in stale_nodes:
                del self.nodes[node_id]
                await self.redis_client.hdel(self.cluster_key, node_id)
                logger.info(f"Removed stale node: {node_id}")
                
        except Exception as e:
            logger.error(f"Error cleaning up stale nodes: {e}")
    
    async def _update_cluster_view(self):
        """Update cluster view from Redis"""
        try:
            nodes_data = await self.redis_client.hgetall(self.cluster_key)
            
            for node_id, node_json in nodes_data.items():
                if node_id != self.node_id:  # Don't overwrite our own info
                    try:
                        node_data = json.loads(node_json)
                        # Convert datetime fields
                        if 'last_seen' in node_data:
                            node_data['last_seen'] = datetime.fromisoformat(node_data['last_seen'])
                        if 'state' in node_data:
                            node_data['state'] = NodeState(node_data['state'])
                        
                        node_info = NodeInfo(**node_data)
                        self.nodes[node_id] = node_info
                        
                    except (json.JSONDecodeError, ValueError) as e:
                        logger.warning(f"Failed to parse node data for {node_id}: {e}")
                        
        except Exception as e:
            logger.error(f"Error updating cluster view: {e}")
    
    async def _election_manager(self):
        """Manage election process"""
        while self._running:
            try:
                await asyncio.sleep(0.5)  # Check elections frequently
                
                # Check if we need to start an election
                if (not self.current_master and 
                    (not self.current_election or self.current_election.phase == ElectionPhase.IDLE) and
                    len(self.nodes) >= self.min_nodes_for_election):
                    
                    await self._start_election()
                
                # Process ongoing election
                if self.current_election and self.current_election.phase != ElectionPhase.IDLE:
                    await self._process_election()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in election manager: {e}")
                await asyncio.sleep(1)
    
    async def _start_election(self):
        """Start a new election"""
        try:
            # Only start election if we're eligible
            if not self._is_eligible_for_election():
                return
            
            # Increment term
            self.current_term += 1
            await self.redis_client.set(self.term_key, self.current_term)
            
            # Create new election
            election_id = f"election-{self.current_term}-{int(time.time())}"
            self.current_election = Election(
                election_id=election_id,
                term=self.current_term,
                phase=ElectionPhase.CANDIDATE,
                started_at=datetime.utcnow()
            )
            
            # Become candidate
            self.my_state = NodeState.CANDIDATE
            self.my_node_info.state = NodeState.CANDIDATE
            self.voted_for = self.node_id  # Vote for ourselves
            
            # Add ourselves as candidate
            self.current_election.candidates.add(self.node_id)
            self.current_election.votes[self.node_id] = self.node_id
            
            # Store election info
            await self._store_election_info()
            
            # Update our node state
            await self._register_node()
            
            logger.info(f"Started election {election_id} for term {self.current_term}")
            
            # Notify callbacks
            if self.on_election_started:
                try:
                    await self.on_election_started(self.current_election)
                except Exception as e:
                    logger.error(f"Error in election started callback: {e}")
            
            # Request votes from other nodes
            await self._request_votes()
            
        except Exception as e:
            logger.error(f"Error starting election: {e}")
    
    def _is_eligible_for_election(self) -> bool:
        """Check if this node is eligible to start an election"""
        try:
            # Check if we're healthy
            if self.my_node_info.health_score < 50:
                return False
            
            # Check if we're available
            if not self.my_node_info.is_available:
                return False
            
            # Check if enough nodes in cluster
            if len(self.nodes) < self.min_nodes_for_election:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking election eligibility: {e}")
            return False
    
    async def _request_votes(self):
        """Request votes from other nodes"""
        try:
            if not self.current_election:
                return
            
            vote_request = {
                'election_id': self.current_election.election_id,
                'term': self.current_term,
                'candidate_id': self.node_id,
                'candidate_health': self.my_node_info.health_score,
                'candidate_priority': self.my_node_info.priority,
                'request_time': datetime.utcnow().isoformat()
            }
            
            # Store vote request
            vote_key = f"{self.election_key}:vote_request:{self.node_id}"
            await self.redis_client.set(
                vote_key,
                json.dumps(vote_request),
                ex=int(self.vote_timeout)
            )
            
            logger.info(f"Requested votes for election {self.current_election.election_id}")
            
        except Exception as e:
            logger.error(f"Error requesting votes: {e}")
    
    async def _process_election(self):
        """Process ongoing election"""
        try:
            if not self.current_election:
                return
            
            # Load current election state
            await self._load_election_state()
            
            # Check for vote requests if we haven't voted
            if not self.voted_for or self.voted_for == self.node_id:
                await self._process_vote_requests()
            
            # Count votes if we're a candidate
            if self.my_state == NodeState.CANDIDATE:
                await self._count_votes()
            
            # Check for election timeout
            election_age = (datetime.utcnow() - self.current_election.started_at).total_seconds()
            if election_age > self.election_timeout:
                await self._handle_election_timeout()
                
        except Exception as e:
            logger.error(f"Error processing election: {e}")
    
    async def _process_vote_requests(self):
        """Process vote requests from candidates"""
        try:
            # Get all vote requests
            pattern = f"{self.election_key}:vote_request:*"
            vote_request_keys = await self.redis_client.keys(pattern)
            
            best_candidate = None
            best_score = -1
            
            for key in vote_request_keys:
                try:
                    request_data = await self.redis_client.get(key)
                    if not request_data:
                        continue
                    
                    vote_request = json.loads(request_data)
                    candidate_id = vote_request['candidate_id']
                    
                    # Skip if already voted for someone else
                    if self.voted_for and self.voted_for != candidate_id and self.voted_for != self.node_id:
                        continue
                    
                    # Skip if term is old
                    if vote_request['term'] < self.current_term:
                        continue
                    
                    # Calculate candidate score
                    score = self._calculate_candidate_score(vote_request)
                    
                    if score > best_score:
                        best_candidate = candidate_id
                        best_score = score
                        
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Invalid vote request: {e}")
            
            # Vote for best candidate
            if best_candidate and (not self.voted_for or self.voted_for == self.node_id):
                await self._cast_vote(best_candidate)
                
        except Exception as e:
            logger.error(f"Error processing vote requests: {e}")
    
    def _calculate_candidate_score(self, vote_request: Dict[str, Any]) -> float:
        """Calculate candidate score for voting decision"""
        try:
            score = 0.0
            
            # Health score (0-100)
            health = vote_request.get('candidate_health', 0)
            score += health
            
            # Priority (0-100)
            priority = vote_request.get('candidate_priority', 50)
            score += priority * 0.5
            
            # Prefer ourselves if we're also a candidate
            if vote_request['candidate_id'] == self.node_id:
                score += 10
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating candidate score: {e}")
            return 0.0
    
    async def _cast_vote(self, candidate_id: str):
        """Cast vote for candidate"""
        try:
            if not self.current_election:
                return
            
            self.voted_for = candidate_id
            
            # Store vote
            vote_data = {
                'election_id': self.current_election.election_id,
                'voter_id': self.node_id,
                'candidate_id': candidate_id,
                'term': self.current_term,
                'vote_time': datetime.utcnow().isoformat()
            }
            
            vote_key = f"{self.election_key}:vote:{self.node_id}"
            await self.redis_client.set(
                vote_key,
                json.dumps(vote_data),
                ex=int(self.election_timeout * 2)
            )
            
            logger.info(f"Voted for candidate {candidate_id} in election {self.current_election.election_id}")
            
        except Exception as e:
            logger.error(f"Error casting vote: {e}")
    
    async def _count_votes(self):
        """Count votes for current election"""
        try:
            if not self.current_election or self.my_state != NodeState.CANDIDATE:
                return
            
            # Get all votes
            pattern = f"{self.election_key}:vote:*"
            vote_keys = await self.redis_client.keys(pattern)
            
            votes_for_me = 0
            total_votes = 0
            
            for key in vote_keys:
                try:
                    vote_data = await self.redis_client.get(key)
                    if not vote_data:
                        continue
                    
                    vote = json.loads(vote_data)
                    
                    # Check if vote is for current election
                    if vote.get('election_id') != self.current_election.election_id:
                        continue
                    
                    # Check if vote is for current term
                    if vote.get('term') != self.current_term:
                        continue
                    
                    total_votes += 1
                    if vote.get('candidate_id') == self.node_id:
                        votes_for_me += 1
                        
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Invalid vote data: {e}")
            
            # Check if we have majority
            active_nodes = len([n for n in self.nodes.values() if n.is_available])
            majority_threshold = (active_nodes // 2) + 1
            
            if votes_for_me >= majority_threshold:
                await self._become_master()
            
            logger.debug(f"Vote count: {votes_for_me}/{total_votes}, need {majority_threshold} for majority")
            
        except Exception as e:
            logger.error(f"Error counting votes: {e}")
    
    async def _become_master(self):
        """Become the master node"""
        try:
            # Create master info
            self.current_master = MasterInfo(
                node_id=self.node_id,
                host=self.my_node_info.host,
                port=self.my_node_info.port,
                elected_at=datetime.utcnow(),
                term=self.current_term,
                last_heartbeat=datetime.utcnow()
            )
            
            # Update our state
            self.my_state = NodeState.MASTER
            self.my_node_info.state = NodeState.MASTER
            
            # Store master info
            master_json = json.dumps({
                'node_id': self.current_master.node_id,
                'host': self.current_master.host,
                'port': self.current_master.port,
                'elected_at': self.current_master.elected_at.isoformat(),
                'term': self.current_master.term,
                'last_heartbeat': self.current_master.last_heartbeat.isoformat(),
                'failover_count': self.current_master.failover_count
            })
            
            await self.redis_client.set(self.master_key, master_json)
            
            # Complete election
            if self.current_election:
                self.current_election.phase = ElectionPhase.LEADER_ELECTED
                self.current_election.winner = self.node_id
                self.current_election.completed_at = datetime.utcnow()
                await self._store_election_info()
            
            # Update our node info
            await self._register_node()
            
            # Clean up election data
            await self._cleanup_election()
            
            logger.info(f"Became master for term {self.current_term}")
            
            # Notify callbacks
            if self.on_master_elected:
                try:
                    await self.on_master_elected(self.current_master)
                except Exception as e:
                    logger.error(f"Error in master elected callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error becoming master: {e}")
    
    async def _handle_election_timeout(self):
        """Handle election timeout"""
        try:
            logger.warning(f"Election {self.current_election.election_id} timed out")
            
            # Reset election state
            self.current_election = None
            self.voted_for = None
            
            if self.my_state == NodeState.CANDIDATE:
                self.my_state = NodeState.FOLLOWER
                self.my_node_info.state = NodeState.FOLLOWER
                await self._register_node()
            
            # Clean up election data
            await self._cleanup_election()
            
        except Exception as e:
            logger.error(f"Error handling election timeout: {e}")
    
    async def _store_election_info(self):
        """Store election information in Redis"""
        try:
            if not self.current_election:
                return
            
            election_data = {
                'election_id': self.current_election.election_id,
                'term': self.current_election.term,
                'phase': self.current_election.phase.value,
                'started_at': self.current_election.started_at.isoformat(),
                'candidates': list(self.current_election.candidates),
                'votes': self.current_election.votes,
                'winner': self.current_election.winner,
                'completed_at': self.current_election.completed_at.isoformat() if self.current_election.completed_at else None
            }
            
            await self.redis_client.set(
                self.election_key,
                json.dumps(election_data),
                ex=int(self.election_timeout * 2)
            )
            
        except Exception as e:
            logger.error(f"Error storing election info: {e}")
    
    async def _load_election_state(self):
        """Load current election state from Redis"""
        try:
            election_data = await self.redis_client.get(self.election_key)
            if not election_data:
                return
            
            election_info = json.loads(election_data)
            
            # Update current election if it's the same
            if (self.current_election and 
                self.current_election.election_id == election_info.get('election_id')):
                
                self.current_election.candidates = set(election_info.get('candidates', []))
                self.current_election.votes = election_info.get('votes', {})
                if election_info.get('phase'):
                    self.current_election.phase = ElectionPhase(election_info['phase'])
                if election_info.get('winner'):
                    self.current_election.winner = election_info['winner']
                if election_info.get('completed_at'):
                    self.current_election.completed_at = datetime.fromisoformat(election_info['completed_at'])
                    
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to load election state: {e}")
        except Exception as e:
            logger.error(f"Error loading election state: {e}")
    
    async def _cleanup_election(self):
        """Clean up election data"""
        try:
            # Remove election data
            await self.redis_client.delete(self.election_key)
            
            # Remove vote requests
            pattern = f"{self.election_key}:vote_request:*"
            vote_request_keys = await self.redis_client.keys(pattern)
            if vote_request_keys:
                await self.redis_client.delete(*vote_request_keys)
            
            # Remove votes
            pattern = f"{self.election_key}:vote:*"
            vote_keys = await self.redis_client.keys(pattern)
            if vote_keys:
                await self.redis_client.delete(*vote_keys)
                
        except Exception as e:
            logger.error(f"Error cleaning up election: {e}")
    
    async def _health_monitor(self):
        """Monitor overall cluster health"""
        while self._running:
            try:
                await asyncio.sleep(5)  # Health check every 5 seconds
                
                # Update our health metrics
                await self._update_node_metrics()
                
                # Check for split brain scenario
                await self._check_split_brain()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(1)
    
    async def _check_split_brain(self):
        """Check for split brain scenario (multiple masters)"""
        try:
            # Look for multiple master heartbeats
            pattern = f"{self.heartbeat_key}:master:*"
            master_keys = await self.redis_client.keys(pattern)
            
            if len(master_keys) > 1:
                logger.critical("Split brain detected - multiple masters!")
                
                # If we're a master, check if we should step down
                if self.my_state == NodeState.MASTER:
                    await self._resolve_split_brain()
                    
        except Exception as e:
            logger.error(f"Error checking split brain: {e}")
    
    async def _resolve_split_brain(self):
        """Resolve split brain scenario"""
        try:
            # Simple resolution: master with highest term wins
            # More sophisticated algorithms could be implemented
            
            current_term = self.current_term
            should_step_down = False
            
            # Check other masters' terms
            pattern = f"{self.heartbeat_key}:master:*"
            master_keys = await self.redis_client.keys(pattern)
            
            for key in master_keys:
                try:
                    heartbeat_data = await self.redis_client.get(key)
                    if heartbeat_data:
                        heartbeat = json.loads(heartbeat_data)
                        other_term = heartbeat.get('term', 0)
                        
                        if other_term > current_term:
                            should_step_down = True
                            break
                            
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Invalid master heartbeat: {e}")
            
            if should_step_down:
                logger.warning("Stepping down due to split brain resolution")
                await self._step_down()
                
        except Exception as e:
            logger.error(f"Error resolving split brain: {e}")
    
    async def _step_down(self):
        """Step down from master role"""
        try:
            # Clear master state
            self.current_master = None
            self.my_state = NodeState.FOLLOWER
            self.my_node_info.state = NodeState.FOLLOWER
            
            # Clear master key
            await self.redis_client.delete(self.master_key)
            
            # Update node state
            await self._register_node()
            
            logger.info("Stepped down from master role")
            
        except Exception as e:
            logger.error(f"Error stepping down: {e}")
    
    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get current cluster status"""
        try:
            return {
                'node_id': self.node_id,
                'state': self.my_state.value,
                'current_term': self.current_term,
                'master': {
                    'node_id': self.current_master.node_id if self.current_master else None,
                    'elected_at': self.current_master.elected_at.isoformat() if self.current_master else None,
                    'term': self.current_master.term if self.current_master else None
                },
                'nodes': {
                    node_id: {
                        'state': node.state.value,
                        'health_score': node.health_score,
                        'last_seen': node.last_seen.isoformat()
                    } for node_id, node in self.nodes.items()
                },
                'election': {
                    'active': self.current_election is not None,
                    'phase': self.current_election.phase.value if self.current_election else None,
                    'candidates': list(self.current_election.candidates) if self.current_election else []
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting cluster status: {e}")
            return {'error': str(e)}
    
    async def shutdown(self):
        """Shutdown the master election controller"""
        try:
            self._running = False
            
            # Cancel background tasks
            for task in self._tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self._tasks:
                await asyncio.gather(*self._tasks, return_exceptions=True)
            
            # Step down if we're master
            if self.my_state == NodeState.MASTER:
                await self._step_down()
            
            # Remove ourselves from cluster
            await self.redis_client.hdel(self.cluster_key, self.node_id)
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Master Election Controller shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Factory function for easy initialization
async def create_master_election_controller(redis_settings: Optional[RedisSettings] = None, 
                                          node_id: Optional[str] = None) -> MasterElectionController:
    """Factory function to create and initialize MasterElectionController"""
    if redis_settings is None:
        redis_settings = RedisSettings()
    
    controller = MasterElectionController(redis_settings, node_id)
    await controller.initialize()
    return controller