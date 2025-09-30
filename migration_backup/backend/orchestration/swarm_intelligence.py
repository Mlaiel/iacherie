"""
Swarm Intelligence Module - Distributed AI Decision Making

Advanced swarm intelligence orchestration with collective decision-making,
emergent behavior, and distributed consensus algorithms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import numpy as np
import random
import math
from typing import Dict, List, Any, Optional, Union, Tuple, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import json
import threading
from collections import defaultdict, deque
import uuid
import weakref

logger = logging.getLogger(__name__)


class SwarmBehavior(Enum):
    """Swarm behavior patterns"""
    FLOCKING = "flocking"
    FORAGING = "foraging"
    CONSENSUS = "consensus"
    EXPLORATION = "exploration"
    CLUSTERING = "clustering"
    OPTIMIZATION = "optimization"
    EMERGENCE = "emergence"


class AgentRole(Enum):
    """Agent roles in swarm"""
    WORKER = "worker"
    SCOUT = "scout"
    LEADER = "leader"
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"
    FOLLOWER = "follower"


class DecisionStrategy(Enum):
    """Decision making strategies"""
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_CONSENSUS = "weighted_consensus"
    EXPERT_OPINION = "expert_opinion"
    EMERGENT_CONSENSUS = "emergent_consensus"
    HIERARCHICAL = "hierarchical"
    DISTRIBUTED = "distributed"


@dataclass
class SwarmConfig:
    """Configuration for swarm intelligence"""
    swarm_size: int = 100
    behavior_type: SwarmBehavior = SwarmBehavior.CONSENSUS
    decision_strategy: DecisionStrategy = DecisionStrategy.MAJORITY_VOTE
    communication_range: float = 10.0
    interaction_strength: float = 1.0
    exploration_rate: float = 0.1
    convergence_threshold: float = 0.01
    max_iterations: int = 1000
    enable_adaptation: bool = True
    enable_learning: bool = True
    noise_level: float = 0.01
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "swarm_size": self.swarm_size,
            "behavior_type": self.behavior_type.value,
            "decision_strategy": self.decision_strategy.value,
            "communication_range": self.communication_range,
            "interaction_strength": self.interaction_strength,
            "exploration_rate": self.exploration_rate,
            "convergence_threshold": self.convergence_threshold,
            "max_iterations": self.max_iterations,
            "enable_adaptation": self.enable_adaptation,
            "enable_learning": self.enable_learning,
            "noise_level": self.noise_level
        }


@dataclass
class AgentState:
    """State of a swarm agent"""
    agent_id: str
    position: np.ndarray
    velocity: np.ndarray
    role: AgentRole
    fitness: float = 0.0
    energy: float = 1.0
    knowledge: Dict[str, Any] = field(default_factory=dict)
    connections: Set[str] = field(default_factory=set)
    last_update: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "agent_id": self.agent_id,
            "position": self.position.tolist(),
            "velocity": self.velocity.tolist(),
            "role": self.role.value,
            "fitness": self.fitness,
            "energy": self.energy,
            "knowledge": self.knowledge,
            "connections": list(self.connections),
            "last_update": self.last_update.isoformat()
        }


class SwarmAgent:
    """Individual agent in the swarm"""
    
    def __init__(self, agent_id: str, initial_position: np.ndarray, 
                 role: AgentRole = AgentRole.WORKER):
        self.agent_id = agent_id
        self.state = AgentState(
            agent_id=agent_id,
            position=initial_position.copy(),
            velocity=np.zeros_like(initial_position),
            role=role
        )
        self.memory: deque = deque(maxlen=1000)
        self.local_best_position = initial_position.copy()
        self.local_best_fitness = float('-inf')
        self.communication_history: deque = deque(maxlen=100)
        
        logger.debug(f"Created swarm agent {agent_id} with role {role.value}")
    
    async def update_position(self, dt: float, forces: np.ndarray):
        """Update agent position based on forces"""
        # Update velocity with forces
        self.state.velocity += forces * dt
        
        # Apply velocity limits
        max_velocity = 10.0
        velocity_magnitude = np.linalg.norm(self.state.velocity)
        if velocity_magnitude > max_velocity:
            self.state.velocity = self.state.velocity / velocity_magnitude * max_velocity
        
        # Update position
        self.state.position += self.state.velocity * dt
        
        # Update timestamp
        self.state.last_update = datetime.utcnow()
        
        # Store in memory
        self.memory.append({
            'timestamp': self.state.last_update,
            'position': self.state.position.copy(),
            'velocity': self.state.velocity.copy(),
            'forces': forces.copy()
        })
    
    async def communicate_with_agent(self, other_agent: 'SwarmAgent', 
                                   message: Dict[str, Any]) -> Dict[str, Any]:
        """Communicate with another agent"""
        # Record communication
        communication_record = {
            'timestamp': datetime.utcnow(),
            'with_agent': other_agent.agent_id,
            'message_sent': message,
            'response_received': None
        }
        
        # Process message based on role
        response = await self._process_message(message, other_agent)
        communication_record['response_received'] = response
        
        self.communication_history.append(communication_record)
        
        return response
    
    async def _process_message(self, message: Dict[str, Any], 
                             sender: 'SwarmAgent') -> Dict[str, Any]:
        """Process incoming message"""
        message_type = message.get('type', 'general')
        
        if message_type == 'position_update':
            # Share own position
            return {
                'type': 'position_response',
                'position': self.state.position.tolist(),
                'velocity': self.state.velocity.tolist(),
                'fitness': self.state.fitness
            }
        
        elif message_type == 'knowledge_share':
            # Share knowledge
            return {
                'type': 'knowledge_response',
                'knowledge': self.state.knowledge.copy(),
                'experience': len(self.memory)
            }
        
        elif message_type == 'coordination_request':
            # Respond to coordination request
            return {
                'type': 'coordination_response',
                'agent_id': self.agent_id,
                'role': self.state.role.value,
                'availability': self.state.energy > 0.5
            }
        
        else:
            # Generic response
            return {
                'type': 'generic_response',
                'agent_id': self.agent_id,
                'status': 'received'
            }
    
    def update_fitness(self, fitness_function: Callable[[np.ndarray], float]):
        """Update agent fitness"""
        self.state.fitness = fitness_function(self.state.position)
        
        # Update local best if improved
        if self.state.fitness > self.local_best_fitness:
            self.local_best_fitness = self.state.fitness
            self.local_best_position = self.state.position.copy()
    
    def add_connection(self, other_agent_id: str):
        """Add connection to another agent"""
        self.state.connections.add(other_agent_id)
    
    def remove_connection(self, other_agent_id: str):
        """Remove connection to another agent"""
        self.state.connections.discard(other_agent_id)
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get comprehensive agent information"""
        return {
            'state': self.state.to_dict(),
            'local_best_position': self.local_best_position.tolist(),
            'local_best_fitness': self.local_best_fitness,
            'memory_size': len(self.memory),
            'communication_count': len(self.communication_history),
            'connection_count': len(self.state.connections)
        }


class CollectiveIntelligence:
    """Collective intelligence algorithms for swarm"""
    
    def __init__(self, config: SwarmConfig):
        self.config = config
        self.collective_memory: Dict[str, Any] = {}
        self.consensus_history: List[Dict[str, Any]] = []
        self.knowledge_base: Dict[str, Any] = {}
        
    async def reach_consensus(self, agents: List[SwarmAgent], 
                            decision_topic: str, options: List[Any]) -> Dict[str, Any]:
        """Reach collective consensus on a decision"""
        if self.config.decision_strategy == DecisionStrategy.MAJORITY_VOTE:
            return await self._majority_vote_consensus(agents, decision_topic, options)
        elif self.config.decision_strategy == DecisionStrategy.WEIGHTED_CONSENSUS:
            return await self._weighted_consensus(agents, decision_topic, options)
        elif self.config.decision_strategy == DecisionStrategy.EMERGENT_CONSENSUS:
            return await self._emergent_consensus(agents, decision_topic, options)
        else:
            return await self._majority_vote_consensus(agents, decision_topic, options)
    
    async def _majority_vote_consensus(self, agents: List[SwarmAgent], 
                                     decision_topic: str, options: List[Any]) -> Dict[str, Any]:
        """Simple majority vote consensus"""
        votes = {}
        for option in options:
            votes[str(option)] = 0
        
        # Collect votes from agents
        for agent in agents:
            # Simulate agent decision making
            choice = await self._agent_make_choice(agent, options)
            votes[str(choice)] += 1
        
        # Find majority decision
        winning_option = max(votes.items(), key=lambda x: x[1])
        total_votes = sum(votes.values())
        
        consensus_result = {
            'decision_topic': decision_topic,
            'winning_option': winning_option[0],
            'vote_count': winning_option[1],
            'vote_percentage': winning_option[1] / max(total_votes, 1),
            'all_votes': votes,
            'total_participants': len(agents),
            'consensus_strength': winning_option[1] / max(total_votes, 1),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.consensus_history.append(consensus_result)
        return consensus_result
    
    async def _weighted_consensus(self, agents: List[SwarmAgent], 
                                decision_topic: str, options: List[Any]) -> Dict[str, Any]:
        """Weighted consensus based on agent fitness/expertise"""
        weighted_votes = {}
        total_weight = 0
        
        for option in options:
            weighted_votes[str(option)] = 0
        
        # Collect weighted votes
        for agent in agents:
            choice = await self._agent_make_choice(agent, options)
            weight = max(agent.state.fitness, 0.1)  # Minimum weight of 0.1
            
            weighted_votes[str(choice)] += weight
            total_weight += weight
        
        # Find weighted winner
        winning_option = max(weighted_votes.items(), key=lambda x: x[1])
        
        consensus_result = {
            'decision_topic': decision_topic,
            'winning_option': winning_option[0],
            'weighted_score': winning_option[1],
            'score_percentage': winning_option[1] / max(total_weight, 1),
            'all_weighted_votes': weighted_votes,
            'total_participants': len(agents),
            'total_weight': total_weight,
            'consensus_strength': winning_option[1] / max(total_weight, 1),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.consensus_history.append(consensus_result)
        return consensus_result
    
    async def _emergent_consensus(self, agents: List[SwarmAgent], 
                                decision_topic: str, options: List[Any]) -> Dict[str, Any]:
        """Emergent consensus through iterative convergence"""
        max_rounds = 10
        convergence_threshold = 0.9
        
        agent_preferences = {}
        for agent in agents:
            agent_preferences[agent.agent_id] = await self._agent_make_choice(agent, options)
        
        for round_num in range(max_rounds):
            # Share preferences and influence each other
            new_preferences = {}
            
            for agent in agents:
                # Get connected agents' preferences
                connected_prefs = []
                for connected_id in agent.state.connections:
                    if connected_id in agent_preferences:
                        connected_prefs.append(agent_preferences[connected_id])
                
                # Influence from neighbors
                if connected_prefs:
                    # Find most common preference among connections
                    pref_counts = {}
                    for pref in connected_prefs:
                        pref_counts[str(pref)] = pref_counts.get(str(pref), 0) + 1
                    
                    most_common_pref = max(pref_counts.items(), key=lambda x: x[1])[0]
                    
                    # Agent may change preference based on social influence
                    if random.random() < 0.3:  # 30% chance to be influenced
                        new_preferences[agent.agent_id] = eval(most_common_pref)
                    else:
                        new_preferences[agent.agent_id] = agent_preferences[agent.agent_id]
                else:
                    new_preferences[agent.agent_id] = agent_preferences[agent.agent_id]
            
            agent_preferences = new_preferences
            
            # Check for convergence
            vote_counts = {}
            for pref in agent_preferences.values():
                vote_counts[str(pref)] = vote_counts.get(str(pref), 0) + 1
            
            max_votes = max(vote_counts.values()) if vote_counts else 0
            convergence = max_votes / len(agents)
            
            if convergence >= convergence_threshold:
                break
        
        # Final result
        final_votes = {}
        for pref in agent_preferences.values():
            final_votes[str(pref)] = final_votes.get(str(pref), 0) + 1
        
        winning_option = max(final_votes.items(), key=lambda x: x[1])
        
        consensus_result = {
            'decision_topic': decision_topic,
            'winning_option': winning_option[0],
            'vote_count': winning_option[1],
            'convergence_rounds': round_num + 1,
            'final_convergence': winning_option[1] / len(agents),
            'all_votes': final_votes,
            'total_participants': len(agents),
            'consensus_strength': winning_option[1] / len(agents),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.consensus_history.append(consensus_result)
        return consensus_result
    
    async def _agent_make_choice(self, agent: SwarmAgent, options: List[Any]) -> Any:
        """Simulate agent decision making"""
        # Simple decision based on agent position and role
        if agent.state.role == AgentRole.LEADER:
            # Leaders tend to choose first option (bias toward action)
            weights = [0.4] + [0.6 / (len(options) - 1)] * (len(options) - 1)
        elif agent.state.role == AgentRole.SCOUT:
            # Scouts prefer exploration (random choice)
            weights = [1.0 / len(options)] * len(options)
        else:
            # Workers use position-based decision
            position_sum = np.sum(agent.state.position)
            choice_index = int(abs(position_sum)) % len(options)
            weights = [0.1] * len(options)
            weights[choice_index] = 0.8
        
        # Add randomness
        weights = np.array(weights)
        weights += np.random.normal(0, 0.1, len(weights))
        weights = np.abs(weights)
        weights /= np.sum(weights)
        
        # Choose based on weights
        choice_index = np.random.choice(len(options), p=weights)
        return options[choice_index]
    
    async def share_knowledge(self, agents: List[SwarmAgent]) -> Dict[str, Any]:
        """Facilitate knowledge sharing among agents"""
        shared_knowledge = {}
        knowledge_contributions = {}
        
        for agent in agents:
            agent_knowledge = agent.state.knowledge
            knowledge_contributions[agent.agent_id] = len(agent_knowledge)
            
            # Merge knowledge
            for key, value in agent_knowledge.items():
                if key not in shared_knowledge:
                    shared_knowledge[key] = []
                shared_knowledge[key].append(value)
        
        # Aggregate knowledge
        aggregated_knowledge = {}
        for key, values in shared_knowledge.items():
            if all(isinstance(v, (int, float)) for v in values):
                # Numerical values - take average
                aggregated_knowledge[key] = np.mean(values)
            else:
                # Non-numerical - take most common
                unique_values = list(set(str(v) for v in values))
                aggregated_knowledge[key] = unique_values[0] if unique_values else None
        
        # Update collective memory
        self.collective_memory.update(aggregated_knowledge)
        
        knowledge_sharing_result = {
            'shared_knowledge_items': len(aggregated_knowledge),
            'contributing_agents': len(knowledge_contributions),
            'knowledge_contributions': knowledge_contributions,
            'aggregated_knowledge': aggregated_knowledge,
            'collective_memory_size': len(self.collective_memory),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return knowledge_sharing_result
    
    def get_collective_stats(self) -> Dict[str, Any]:
        """Get collective intelligence statistics"""
        return {
            'collective_memory_size': len(self.collective_memory),
            'consensus_decisions_made': len(self.consensus_history),
            'knowledge_base_size': len(self.knowledge_base),
            'last_consensus': self.consensus_history[-1] if self.consensus_history else None,
            'average_consensus_strength': np.mean([
                c['consensus_strength'] for c in self.consensus_history
            ]) if self.consensus_history else 0.0
        }


class EmergentBehavior:
    """Emergent behavior patterns in swarm"""
    
    def __init__(self, config: SwarmConfig):
        self.config = config
        self.behavior_patterns: Dict[str, Any] = {}
        self.emergence_history: List[Dict[str, Any]] = []
        
    async def detect_emergence(self, agents: List[SwarmAgent]) -> Dict[str, Any]:
        """Detect emergent behavior patterns"""
        patterns = {}
        
        # Flocking behavior detection
        flocking_score = await self._detect_flocking(agents)
        patterns['flocking'] = flocking_score
        
        # Clustering behavior detection
        clustering_score = await self._detect_clustering(agents)
        patterns['clustering'] = clustering_score
        
        # Leadership emergence detection
        leadership_score = await self._detect_leadership(agents)
        patterns['leadership'] = leadership_score
        
        # Communication network analysis
        network_score = await self._analyze_communication_network(agents)
        patterns['communication_network'] = network_score
        
        # Overall emergence score
        emergence_score = np.mean(list(patterns.values()))
        
        emergence_result = {
            'emergence_score': emergence_score,
            'behavior_patterns': patterns,
            'agent_count': len(agents),
            'timestamp': datetime.utcnow().isoformat(),
            'config': self.config.to_dict()
        }
        
        self.emergence_history.append(emergence_result)
        
        return emergence_result
    
    async def _detect_flocking(self, agents: List[SwarmAgent]) -> float:
        """Detect flocking behavior (alignment, cohesion, separation)"""
        if len(agents) < 3:
            return 0.0
        
        positions = np.array([agent.state.position for agent in agents])
        velocities = np.array([agent.state.velocity for agent in agents])
        
        # Alignment: similar velocity directions
        velocity_magnitudes = np.linalg.norm(velocities, axis=1)
        nonzero_velocities = velocities[velocity_magnitudes > 0.01]
        
        if len(nonzero_velocities) < 2:
            alignment = 0.0
        else:
            normalized_velocities = nonzero_velocities / np.linalg.norm(nonzero_velocities, axis=1, keepdims=True)
            pairwise_dots = np.dot(normalized_velocities, normalized_velocities.T)
            alignment = np.mean(pairwise_dots)
        
        # Cohesion: agents stay close together
        center_of_mass = np.mean(positions, axis=0)
        distances_to_center = np.linalg.norm(positions - center_of_mass, axis=1)
        max_distance = np.max(distances_to_center) if len(distances_to_center) > 0 else 1.0
        cohesion = 1.0 - (np.mean(distances_to_center) / max_distance)
        
        # Separation: agents maintain minimum distance
        pairwise_distances = []
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                dist = np.linalg.norm(positions[i] - positions[j])
                pairwise_distances.append(dist)
        
        if pairwise_distances:
            min_desired_distance = 1.0
            separation = np.mean([min(dist / min_desired_distance, 1.0) for dist in pairwise_distances])
        else:
            separation = 0.0
        
        # Combine scores
        flocking_score = (alignment + cohesion + separation) / 3.0
        return max(0.0, min(1.0, flocking_score))
    
    async def _detect_clustering(self, agents: List[SwarmAgent]) -> float:
        """Detect clustering behavior"""
        if len(agents) < 4:
            return 0.0
        
        positions = np.array([agent.state.position for agent in agents])
        
        # Simple clustering detection using k-means-like approach
        # Estimate number of clusters
        max_clusters = min(5, len(agents) // 2)
        best_clustering_score = 0.0
        
        for k in range(2, max_clusters + 1):
            # Random cluster centers
            cluster_centers = positions[np.random.choice(len(positions), k, replace=False)]
            
            # Assign agents to clusters
            cluster_assignments = []
            for pos in positions:
                distances = [np.linalg.norm(pos - center) for center in cluster_centers]
                cluster_assignments.append(np.argmin(distances))
            
            # Calculate within-cluster variance
            within_cluster_variance = 0.0
            for cluster_id in range(k):
                cluster_positions = positions[np.array(cluster_assignments) == cluster_id]
                if len(cluster_positions) > 0:
                    cluster_center = np.mean(cluster_positions, axis=0)
                    variance = np.mean([np.linalg.norm(pos - cluster_center) ** 2 for pos in cluster_positions])
                    within_cluster_variance += variance
            
            # Lower variance = better clustering
            clustering_score = 1.0 / (1.0 + within_cluster_variance)
            best_clustering_score = max(best_clustering_score, clustering_score)
        
        return best_clustering_score
    
    async def _detect_leadership(self, agents: List[SwarmAgent]) -> float:
        """Detect leadership emergence"""
        if len(agents) < 3:
            return 0.0
        
        leadership_scores = {}
        
        for agent in agents:
            score = 0.0
            
            # Factor 1: Fitness
            if agent.state.fitness > 0:
                score += agent.state.fitness / 10.0
            
            # Factor 2: Connection count (influence)
            score += len(agent.state.connections) / len(agents)
            
            # Factor 3: Role
            if agent.state.role == AgentRole.LEADER:
                score += 0.5
            elif agent.state.role == AgentRole.COORDINATOR:
                score += 0.3
            
            # Factor 4: Communication activity
            score += len(agent.communication_history) / 100.0
            
            leadership_scores[agent.agent_id] = score
        
        # Measure leadership inequality (higher inequality = clearer leadership)
        scores = list(leadership_scores.values())
        if len(scores) > 1:
            leadership_emergence = np.std(scores) / np.mean(scores) if np.mean(scores) > 0 else 0.0
        else:
            leadership_emergence = 0.0
        
        return min(1.0, leadership_emergence)
    
    async def _analyze_communication_network(self, agents: List[SwarmAgent]) -> float:
        """Analyze communication network structure"""
        if len(agents) < 3:
            return 0.0
        
        # Build adjacency matrix
        agent_ids = [agent.agent_id for agent in agents]
        n = len(agent_ids)
        adjacency_matrix = np.zeros((n, n))
        
        id_to_index = {agent_id: i for i, agent_id in enumerate(agent_ids)}
        
        for agent in agents:
            agent_index = id_to_index[agent.agent_id]
            for connected_id in agent.state.connections:
                if connected_id in id_to_index:
                    connected_index = id_to_index[connected_id]
                    adjacency_matrix[agent_index][connected_index] = 1
        
        # Calculate network metrics
        total_connections = np.sum(adjacency_matrix)
        possible_connections = n * (n - 1)
        
        if possible_connections > 0:
            connectivity = total_connections / possible_connections
        else:
            connectivity = 0.0
        
        # Small-world network detection (simplified)
        # Higher local clustering + short path lengths
        local_clustering = 0.0
        for i in range(n):
            neighbors = np.where(adjacency_matrix[i] == 1)[0]
            if len(neighbors) > 1:
                neighbor_connections = 0
                for j in neighbors:
                    for k in neighbors:
                        if j != k and adjacency_matrix[j][k] == 1:
                            neighbor_connections += 1
                possible_neighbor_connections = len(neighbors) * (len(neighbors) - 1)
                if possible_neighbor_connections > 0:
                    local_clustering += neighbor_connections / possible_neighbor_connections
        
        local_clustering /= n
        
        # Combine metrics
        network_score = (connectivity + local_clustering) / 2.0
        return min(1.0, network_score)


class DistributedDecisionEngine:
    """Distributed decision making engine"""
    
    def __init__(self, config: SwarmConfig):
        self.config = config
        self.pending_decisions: Dict[str, Dict[str, Any]] = {}
        self.completed_decisions: List[Dict[str, Any]] = []
        self.decision_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    async def initiate_decision(self, decision_id: str, decision_topic: str,
                              options: List[Any], agents: List[SwarmAgent],
                              deadline: Optional[datetime] = None) -> str:
        """Initiate a distributed decision process"""
        decision_record = {
            'decision_id': decision_id,
            'decision_topic': decision_topic,
            'options': options,
            'participating_agents': [agent.agent_id for agent in agents],
            'deadline': deadline or (datetime.utcnow() + timedelta(minutes=10)),
            'status': 'initiated',
            'votes': {},
            'created_at': datetime.utcnow(),
            'result': None
        }
        
        self.pending_decisions[decision_id] = decision_record
        
        logger.info(f"Initiated distributed decision {decision_id}: {decision_topic}")
        return decision_id
    
    async def collect_votes(self, decision_id: str, agents: List[SwarmAgent]) -> Dict[str, Any]:
        """Collect votes from agents for a decision"""
        if decision_id not in self.pending_decisions:
            raise ValueError(f"Decision {decision_id} not found")
        
        decision_record = self.pending_decisions[decision_id]
        options = decision_record['options']
        
        # Collect votes in parallel
        vote_tasks = []
        for agent in agents:
            if agent.agent_id in decision_record['participating_agents']:
                task = asyncio.create_task(self._collect_agent_vote(agent, decision_id, options))
                vote_tasks.append((agent.agent_id, task))
        
        votes = {}
        for agent_id, task in vote_tasks:
            try:
                vote = await task
                votes[agent_id] = vote
            except Exception as e:
                logger.error(f"Failed to collect vote from agent {agent_id}: {e}")
                votes[agent_id] = None
        
        decision_record['votes'] = votes
        decision_record['status'] = 'votes_collected'
        
        return votes
    
    async def _collect_agent_vote(self, agent: SwarmAgent, decision_id: str, 
                                options: List[Any]) -> Dict[str, Any]:
        """Collect vote from individual agent"""
        # Simulate agent deliberation time
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Agent makes choice based on their characteristics
        choice_weights = []
        
        for option in options:
            weight = 1.0
            
            # Role-based preferences
            if agent.state.role == AgentRole.LEADER:
                # Leaders prefer decisive options
                weight *= 1.2
            elif agent.state.role == AgentRole.SCOUT:
                # Scouts prefer exploratory options
                weight *= random.uniform(0.8, 1.5)
            
            # Fitness-based confidence
            weight *= (0.5 + agent.state.fitness)
            
            # Add some randomness
            weight *= random.uniform(0.8, 1.2)
            
            choice_weights.append(weight)
        
        # Normalize weights and choose
        total_weight = sum(choice_weights)
        if total_weight > 0:
            probabilities = [w / total_weight for w in choice_weights]
        else:
            probabilities = [1.0 / len(options)] * len(options)
        
        chosen_option_index = np.random.choice(len(options), p=probabilities)
        chosen_option = options[chosen_option_index]
        
        # Calculate confidence
        confidence = choice_weights[chosen_option_index] / max(choice_weights)
        
        vote = {
            'option': chosen_option,
            'confidence': confidence,
            'reasoning': f"Agent {agent.agent_id} chose based on role {agent.state.role.value}",
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return vote
    
    async def finalize_decision(self, decision_id: str, 
                              collective_intelligence: CollectiveIntelligence) -> Dict[str, Any]:
        """Finalize decision using collective intelligence"""
        if decision_id not in self.pending_decisions:
            raise ValueError(f"Decision {decision_id} not found")
        
        decision_record = self.pending_decisions[decision_id]
        votes = decision_record['votes']
        
        # Extract valid votes
        valid_votes = {k: v for k, v in votes.items() if v is not None}
        
        if not valid_votes:
            result = {
                'decision_id': decision_id,
                'outcome': 'no_decision',
                'reason': 'no_valid_votes',
                'finalized_at': datetime.utcnow().isoformat()
            }
        else:
            # Apply decision strategy
            if self.config.decision_strategy == DecisionStrategy.MAJORITY_VOTE:
                result = await self._majority_vote_decision(decision_record, valid_votes)
            elif self.config.decision_strategy == DecisionStrategy.WEIGHTED_CONSENSUS:
                result = await self._weighted_consensus_decision(decision_record, valid_votes)
            else:
                result = await self._majority_vote_decision(decision_record, valid_votes)
        
        # Update decision record
        decision_record['result'] = result
        decision_record['status'] = 'finalized'
        decision_record['finalized_at'] = datetime.utcnow()
        
        # Move to completed decisions
        self.completed_decisions.append(decision_record)
        self.decision_history[decision_record['decision_topic']].append(result)
        del self.pending_decisions[decision_id]
        
        logger.info(f"Finalized decision {decision_id}: {result['outcome']}")
        
        return result
    
    async def _majority_vote_decision(self, decision_record: Dict[str, Any], 
                                    valid_votes: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Make decision based on majority vote"""
        option_counts = {}
        for vote in valid_votes.values():
            option = str(vote['option'])
            option_counts[option] = option_counts.get(option, 0) + 1
        
        if not option_counts:
            return {
                'decision_id': decision_record['decision_id'],
                'outcome': 'no_decision',
                'reason': 'no_valid_options'
            }
        
        winning_option = max(option_counts.items(), key=lambda x: x[1])
        total_votes = sum(option_counts.values())
        
        return {
            'decision_id': decision_record['decision_id'],
            'outcome': 'decision_made',
            'chosen_option': winning_option[0],
            'vote_count': winning_option[1],
            'total_votes': total_votes,
            'vote_percentage': winning_option[1] / total_votes,
            'margin_of_victory': winning_option[1] - max([count for option, count in option_counts.items() if option != winning_option[0]], default=0),
            'all_vote_counts': option_counts,
            'decision_strength': winning_option[1] / total_votes,
            'finalized_at': datetime.utcnow().isoformat()
        }
    
    async def _weighted_consensus_decision(self, decision_record: Dict[str, Any], 
                                         valid_votes: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Make decision based on weighted consensus"""
        option_weights = {}
        total_weight = 0
        
        for vote in valid_votes.values():
            option = str(vote['option'])
            confidence = vote.get('confidence', 1.0)
            
            option_weights[option] = option_weights.get(option, 0) + confidence
            total_weight += confidence
        
        if not option_weights:
            return {
                'decision_id': decision_record['decision_id'],
                'outcome': 'no_decision',
                'reason': 'no_weighted_options'
            }
        
        winning_option = max(option_weights.items(), key=lambda x: x[1])
        
        return {
            'decision_id': decision_record['decision_id'],
            'outcome': 'decision_made',
            'chosen_option': winning_option[0],
            'weighted_score': winning_option[1],
            'total_weight': total_weight,
            'weight_percentage': winning_option[1] / total_weight,
            'all_weighted_scores': option_weights,
            'decision_strength': winning_option[1] / total_weight,
            'finalized_at': datetime.utcnow().isoformat()
        }
    
    def get_decision_stats(self) -> Dict[str, Any]:
        """Get decision engine statistics"""
        return {
            'pending_decisions': len(self.pending_decisions),
            'completed_decisions': len(self.completed_decisions),
            'decision_topics': len(self.decision_history),
            'average_decision_strength': np.mean([
                d['result']['decision_strength'] for d in self.completed_decisions 
                if d['result'] and 'decision_strength' in d['result']
            ]) if self.completed_decisions else 0.0,
            'success_rate': len([d for d in self.completed_decisions 
                               if d['result']['outcome'] == 'decision_made']) / max(len(self.completed_decisions), 1)
        }


class SwarmOrchestrator:
    """Main orchestrator for swarm intelligence"""
    
    def __init__(self, config: SwarmConfig):
        self.config = config
        self.agents: Dict[str, SwarmAgent] = {}
        self.collective_intelligence = CollectiveIntelligence(config)
        self.emergent_behavior = EmergentBehavior(config)
        self.decision_engine = DistributedDecisionEngine(config)
        self.is_running = False
        self.simulation_step = 0
        self._executor = ThreadPoolExecutor(max_workers=8)
        
        logger.info(f"SwarmOrchestrator initialized with {config.swarm_size} agents")
    
    async def initialize_swarm(self, space_dimensions: int = 2, 
                             space_bounds: Tuple[float, float] = (-100.0, 100.0)) -> List[str]:
        """Initialize swarm with agents"""
        agent_ids = []
        
        for i in range(self.config.swarm_size):
            agent_id = f"agent_{i:04d}"
            
            # Random initial position
            initial_position = np.random.uniform(
                space_bounds[0], space_bounds[1], 
                size=space_dimensions
            )
            
            # Assign role based on distribution
            if i < self.config.swarm_size * 0.05:  # 5% leaders
                role = AgentRole.LEADER
            elif i < self.config.swarm_size * 0.15:  # 10% scouts
                role = AgentRole.SCOUT
            elif i < self.config.swarm_size * 0.25:  # 10% coordinators
                role = AgentRole.COORDINATOR
            else:  # Rest are workers
                role = AgentRole.WORKER
            
            agent = SwarmAgent(agent_id, initial_position, role)
            self.agents[agent_id] = agent
            agent_ids.append(agent_id)
        
        # Establish initial connections
        await self._establish_initial_connections()
        
        logger.info(f"Initialized swarm with {len(agent_ids)} agents")
        return agent_ids
    
    async def _establish_initial_connections(self):
        """Establish initial connections between agents"""
        agent_list = list(self.agents.values())
        
        for agent in agent_list:
            # Connect to nearby agents
            for other_agent in agent_list:
                if agent.agent_id != other_agent.agent_id:
                    distance = np.linalg.norm(agent.state.position - other_agent.state.position)
                    
                    if distance <= self.config.communication_range:
                        agent.add_connection(other_agent.agent_id)
                        other_agent.add_connection(agent.agent_id)
    
    async def run_swarm_simulation(self, steps: int = 1000, dt: float = 0.1) -> Dict[str, Any]:
        """Run complete swarm simulation"""
        self.is_running = True
        simulation_results = {
            'steps_completed': 0,
            'emergence_events': [],
            'decisions_made': [],
            'knowledge_sharing_events': [],
            'final_stats': {}
        }
        
        logger.info(f"Starting swarm simulation for {steps} steps")
        
        try:
            for step in range(steps):
                self.simulation_step = step
                
                # Update agent positions and behaviors
                await self._update_swarm_step(dt)
                
                # Check for emergent behavior every 10 steps
                if step % 10 == 0:
                    emergence = await self.emergent_behavior.detect_emergence(list(self.agents.values()))
                    simulation_results['emergence_events'].append(emergence)
                
                # Facilitate knowledge sharing every 50 steps
                if step % 50 == 0:
                    knowledge_event = await self.collective_intelligence.share_knowledge(list(self.agents.values()))
                    simulation_results['knowledge_sharing_events'].append(knowledge_event)
                
                # Periodic decisions every 100 steps
                if step % 100 == 0 and step > 0:
                    decision_result = await self._make_swarm_decision(f"decision_{step}")
                    simulation_results['decisions_made'].append(decision_result)
                
                if not self.is_running:
                    break
                
                # Log progress every 100 steps
                if step % 100 == 0:
                    logger.debug(f"Simulation step {step}/{steps}")
        
        except Exception as e:
            logger.error(f"Simulation error at step {self.simulation_step}: {e}")
        
        finally:
            self.is_running = False
            simulation_results['steps_completed'] = self.simulation_step
            simulation_results['final_stats'] = await self.get_orchestrator_stats()
        
        logger.info(f"Swarm simulation completed after {simulation_results['steps_completed']} steps")
        return simulation_results
    
    async def _update_swarm_step(self, dt: float):
        """Update one simulation step for all agents"""
        agent_list = list(self.agents.values())
        
        # Calculate forces for each agent
        update_tasks = []
        for agent in agent_list:
            task = asyncio.create_task(self._calculate_agent_forces(agent, agent_list))
            update_tasks.append((agent, task))
        
        # Apply forces and update positions
        for agent, task in update_tasks:
            try:
                forces = await task
                await agent.update_position(dt, forces)
            except Exception as e:
                logger.error(f"Error updating agent {agent.agent_id}: {e}")
    
    async def _calculate_agent_forces(self, agent: SwarmAgent, all_agents: List[SwarmAgent]) -> np.ndarray:
        """Calculate forces acting on an agent"""
        total_force = np.zeros_like(agent.state.position)
        
        if self.config.behavior_type == SwarmBehavior.FLOCKING:
            total_force += await self._calculate_flocking_forces(agent, all_agents)
        elif self.config.behavior_type == SwarmBehavior.FORAGING:
            total_force += await self._calculate_foraging_forces(agent, all_agents)
        elif self.config.behavior_type == SwarmBehavior.EXPLORATION:
            total_force += await self._calculate_exploration_forces(agent, all_agents)
        else:
            # Default random walk
            total_force += np.random.normal(0, 0.1, agent.state.position.shape)
        
        # Add noise
        noise = np.random.normal(0, self.config.noise_level, agent.state.position.shape)
        total_force += noise
        
        return total_force
    
    async def _calculate_flocking_forces(self, agent: SwarmAgent, all_agents: List[SwarmAgent]) -> np.ndarray:
        """Calculate flocking forces (Reynolds model)"""
        separation_force = np.zeros_like(agent.state.position)
        alignment_force = np.zeros_like(agent.state.position)
        cohesion_force = np.zeros_like(agent.state.position)
        
        neighbors = []
        for other_agent in all_agents:
            if other_agent.agent_id != agent.agent_id:
                distance = np.linalg.norm(agent.state.position - other_agent.state.position)
                if distance <= self.config.communication_range:
                    neighbors.append(other_agent)
        
        if neighbors:
            # Separation: avoid crowding
            for neighbor in neighbors:
                diff = agent.state.position - neighbor.state.position
                distance = np.linalg.norm(diff)
                if distance > 0 and distance < 2.0:  # Separation distance
                    separation_force += diff / (distance ** 2)
            
            # Alignment: steer towards average heading
            neighbor_velocities = [n.state.velocity for n in neighbors]
            if neighbor_velocities:
                avg_velocity = np.mean(neighbor_velocities, axis=0)
                alignment_force = avg_velocity - agent.state.velocity
            
            # Cohesion: steer towards average position
            neighbor_positions = [n.state.position for n in neighbors]
            avg_position = np.mean(neighbor_positions, axis=0)
            cohesion_force = (avg_position - agent.state.position) * 0.01
        
        total_force = separation_force * 2.0 + alignment_force * 1.0 + cohesion_force * 1.0
        return total_force * self.config.interaction_strength
    
    async def _calculate_foraging_forces(self, agent: SwarmAgent, all_agents: List[SwarmAgent]) -> np.ndarray:
        """Calculate foraging forces"""
        # Simulate food sources at specific locations
        food_sources = [
            np.array([50.0, 50.0]),
            np.array([-30.0, 20.0]),
            np.array([10.0, -40.0])
        ]
        
        foraging_force = np.zeros_like(agent.state.position)
        
        # Attraction to nearest food source
        min_distance = float('inf')
        nearest_food = None
        
        for food_pos in food_sources:
            distance = np.linalg.norm(agent.state.position - food_pos)
            if distance < min_distance:
                min_distance = distance
                nearest_food = food_pos
        
        if nearest_food is not None and min_distance > 1.0:
            direction = nearest_food - agent.state.position
            foraging_force = direction / np.linalg.norm(direction) * 0.5
        
        # Add some flocking behavior
        flocking_force = await self._calculate_flocking_forces(agent, all_agents)
        
        return foraging_force + flocking_force * 0.3
    
    async def _calculate_exploration_forces(self, agent: SwarmAgent, all_agents: List[SwarmAgent]) -> np.ndarray:
        """Calculate exploration forces"""
        # Random exploration with some coordination
        exploration_force = np.random.normal(0, 1.0, agent.state.position.shape)
        
        # Scouts explore more randomly
        if agent.state.role == AgentRole.SCOUT:
            exploration_force *= 2.0
        
        # Leaders coordinate exploration
        if agent.state.role == AgentRole.LEADER:
            # Bias towards unexplored areas (simplified)
            exploration_force += np.array([self.simulation_step % 100 - 50, 
                                         (self.simulation_step // 10) % 100 - 50]) * 0.01
        
        return exploration_force * self.config.exploration_rate
    
    async def _make_swarm_decision(self, decision_id: str) -> Dict[str, Any]:
        """Make a collective swarm decision"""
        options = ["option_A", "option_B", "option_C"]
        decision_topic = f"swarm_decision_{self.simulation_step}"
        
        # Initiate decision
        await self.decision_engine.initiate_decision(
            decision_id, decision_topic, options, list(self.agents.values())
        )
        
        # Collect votes
        await self.decision_engine.collect_votes(decision_id, list(self.agents.values()))
        
        # Finalize decision
        result = await self.decision_engine.finalize_decision(decision_id, self.collective_intelligence)
        
        return result
    
    def stop_simulation(self):
        """Stop running simulation"""
        self.is_running = False
    
    async def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator statistics"""
        agent_stats = {}
        total_connections = 0
        role_distribution = defaultdict(int)
        
        for agent in self.agents.values():
            agent_info = agent.get_agent_info()
            agent_stats[agent.agent_id] = agent_info
            total_connections += len(agent.state.connections)
            role_distribution[agent.state.role.value] += 1
        
        collective_stats = self.collective_intelligence.get_collective_stats()
        decision_stats = self.decision_engine.get_decision_stats()
        
        return {
            'config': self.config.to_dict(),
            'total_agents': len(self.agents),
            'simulation_step': self.simulation_step,
            'is_running': self.is_running,
            'total_connections': total_connections // 2,  # Undirected connections
            'average_connections_per_agent': total_connections / max(len(self.agents) * 2, 1),
            'role_distribution': dict(role_distribution),
            'collective_intelligence_stats': collective_stats,
            'decision_engine_stats': decision_stats,
            'emergence_events_detected': len(self.emergent_behavior.emergence_history),
            'last_emergence_score': (
                self.emergent_behavior.emergence_history[-1]['emergence_score'] 
                if self.emergent_behavior.emergence_history else 0.0
            )
        }