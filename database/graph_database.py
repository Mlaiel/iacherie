"""Graph Database for Complex Relationships

Advanced graph-based relationship mapping and analysis for the IA matching service.
Implements NetworkX-based graph database with sophisticated relationship modeling.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT INTELLECTUAL PROPERTY WARNING ⚠️
This software and all associated code are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
UNAUTHORIZED ACCESS, COPYING, MODIFICATION, DISTRIBUTION, REVERSE ENGINEERING, 
OR COMMERCIALIZATION without explicit written permission is STRICTLY PROHIBITED
and will result in immediate legal action under German and International copyright laws.

For legitimate licensing inquiries: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import networkx as nx
from collections import defaultdict, Counter
import pickle
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class RelationshipType(Enum):
    """Types of relationships in the creator network"""
    COLLABORATION = "collaboration"
    INFLUENCE = "influence"
    GENRE_SIMILARITY = "genre_similarity"
    SKILL_COMPLEMENT = "skill_complement"
    PLATFORM_OVERLAP = "platform_overlap"
    AUDIENCE_OVERLAP = "audience_overlap"
    MENTOR_MENTEE = "mentor_mentee"
    LABEL_ARTIST = "label_artist"
    PRODUCER_ARTIST = "producer_artist"
    CREATIVE_SYNERGY = "creative_synergy"


class EdgeWeight(Enum):
    """Edge weight categories"""
    WEAK = 0.1
    MODERATE = 0.4
    STRONG = 0.7
    VERY_STRONG = 0.9


@dataclass
class RelationshipEdge:
    """Represents a relationship edge in the graph"""
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    weight: float
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Temporal properties
    strength_over_time: List[Tuple[datetime, float]] = field(default_factory=list)
    interaction_frequency: float = 0.0
    collaboration_success_rate: float = 0.0


@dataclass
class NetworkNode:
    """Represents a creator node in the graph"""
    node_id: str
    node_type: str = "creator"
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # Centrality metrics
    degree_centrality: float = 0.0
    betweenness_centrality: float = 0.0
    closeness_centrality: float = 0.0
    eigenvector_centrality: float = 0.0
    pagerank: float = 0.0
    
    # Community metrics
    community_id: Optional[int] = None
    cluster_coefficient: float = 0.0
    
    # Influence metrics
    influence_score: float = 0.0
    reach_potential: int = 0
    network_value: float = 0.0
    
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class NetworkCommunity:
    """Represents a community within the network"""
    community_id: int
    members: List[str]
    community_type: str
    
    # Community characteristics
    genre_focus: List[str] = field(default_factory=list)
    skill_specialization: List[str] = field(default_factory=list)
    geographic_concentration: Optional[str] = None
    average_experience_level: float = 0.0
    
    # Community metrics
    modularity: float = 0.0
    internal_density: float = 0.0
    external_connectivity: float = 0.0
    influence_concentration: float = 0.0
    
    # Temporal evolution
    formation_date: datetime = field(default_factory=datetime.now)
    stability_index: float = 0.0
    growth_rate: float = 0.0


class CreatorGraphDatabase:
    """
    Advanced graph database for creator relationships and network analysis
    
    Features:
    - Multi-layered relationship modeling
    - Dynamic community detection
    - Influence propagation analysis
    - Temporal network evolution tracking
    - Path optimization for collaboration discovery
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the graph database"""
        self.db_path = db_path or "creator_network.db"
        
        # Core graph structures
        self.main_graph = nx.MultiDiGraph()  # Directed multigraph for complex relationships
        self.collaboration_graph = nx.Graph()  # Undirected for collaboration analysis
        self.influence_graph = nx.DiGraph()  # Directed for influence flow
        self.genre_graph = nx.Graph()  # Genre similarity network
        
        # Data storage
        self.nodes: Dict[str, NetworkNode] = {}
        self.edges: Dict[str, RelationshipEdge] = {}
        self.communities: Dict[int, NetworkCommunity] = {}
        
        # Analysis caches
        self.centrality_cache: Dict[str, Dict] = {}
        self.path_cache: Dict[str, List] = {}
        self.community_cache: Dict[str, Any] = {}
        
        # Temporal tracking
        self.evolution_snapshots: List[Tuple[datetime, Dict]] = []
        
        # Initialize database
        self._initialize_database()
        
        logger.info("Creator Graph Database initialized")
    
    def _initialize_database(self):
        """Initialize the SQLite database for persistence"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables for persistent storage
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nodes (
                    node_id TEXT PRIMARY KEY,
                    node_type TEXT,
                    properties TEXT,
                    centrality_metrics TEXT,
                    created_at TEXT,
                    last_updated TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS edges (
                    edge_id TEXT PRIMARY KEY,
                    source_id TEXT,
                    target_id TEXT,
                    relationship_type TEXT,
                    weight REAL,
                    confidence REAL,
                    metadata TEXT,
                    created_at TEXT,
                    last_updated TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS communities (
                    community_id INTEGER PRIMARY KEY,
                    members TEXT,
                    community_type TEXT,
                    characteristics TEXT,
                    metrics TEXT,
                    formation_date TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
    
    async def add_creator_node(
        self,
        creator_id: str,
        creator_data: Dict[str, Any]
    ) -> NetworkNode:
        """Add a creator node to the graph"""
        try:
            # Create network node
            node = NetworkNode(
                node_id=creator_id,
                node_type="creator",
                properties=creator_data
            )
            
            # Add to main graph
            self.main_graph.add_node(
                creator_id,
                **creator_data,
                node_object=node
            )
            
            # Add to specialized graphs
            self.collaboration_graph.add_node(creator_id, **creator_data)
            self.influence_graph.add_node(creator_id, **creator_data)
            
            # Store node
            self.nodes[creator_id] = node
            
            # Persist to database
            await self._persist_node(node)
            
            logger.info(f"Added creator node: {creator_id}")
            return node
            
        except Exception as e:
            logger.error(f"Error adding creator node: {str(e)}")
            raise
    
    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        weight: float,
        confidence: float,
        metadata: Optional[Dict] = None
    ) -> RelationshipEdge:
        """Add a relationship edge between creators"""
        try:
            if metadata is None:
                metadata = {}
            
            # Create relationship edge
            edge_id = f"{source_id}_{target_id}_{relationship_type.value}"
            edge = RelationshipEdge(
                source_id=source_id,
                target_id=target_id,
                relationship_type=relationship_type,
                weight=weight,
                confidence=confidence,
                metadata=metadata
            )
            
            # Add to main graph
            self.main_graph.add_edge(
                source_id,
                target_id,
                key=relationship_type.value,
                relationship_type=relationship_type.value,
                weight=weight,
                confidence=confidence,
                edge_object=edge,
                **metadata
            )
            
            # Add to specialized graphs based on relationship type
            if relationship_type == RelationshipType.COLLABORATION:
                self.collaboration_graph.add_edge(source_id, target_id, weight=weight)
            
            if relationship_type == RelationshipType.INFLUENCE:
                self.influence_graph.add_edge(source_id, target_id, weight=weight)
            
            if relationship_type == RelationshipType.GENRE_SIMILARITY:
                self.genre_graph.add_edge(source_id, target_id, weight=weight)
            
            # Store edge
            self.edges[edge_id] = edge
            
            # Persist to database
            await self._persist_edge(edge)
            
            # Invalidate caches
            self._invalidate_caches()
            
            logger.info(f"Added relationship: {source_id} -> {target_id} ({relationship_type.value})")
            return edge
            
        except Exception as e:
            logger.error(f"Error adding relationship: {str(e)}")
            raise
    
    async def calculate_network_metrics(self, node_id: str) -> Dict[str, float]:
        """Calculate comprehensive network metrics for a node"""
        try:
            if node_id not in self.main_graph:
                raise ValueError(f"Node {node_id} not found in graph")
            
            # Check cache first
            cache_key = f"metrics_{node_id}"
            if cache_key in self.centrality_cache:
                cached_time, metrics = self.centrality_cache[cache_key]
                if (datetime.now() - cached_time).seconds < 1800:  # 30 min cache
                    return metrics
            
            metrics = {}
            
            # Basic centrality metrics
            if len(self.main_graph) > 1:
                degree_centrality = nx.degree_centrality(self.main_graph.to_undirected())
                betweenness_centrality = nx.betweenness_centrality(self.main_graph.to_undirected())
                closeness_centrality = nx.closeness_centrality(self.main_graph.to_undirected())
                
                metrics.update({
                    "degree_centrality": degree_centrality.get(node_id, 0.0),
                    "betweenness_centrality": betweenness_centrality.get(node_id, 0.0),
                    "closeness_centrality": closeness_centrality.get(node_id, 0.0),
                })
                
                # PageRank for influence
                pagerank = nx.pagerank(self.main_graph)
                metrics["pagerank"] = pagerank.get(node_id, 0.0)
                
                # Clustering coefficient
                clustering = nx.clustering(self.main_graph.to_undirected())
                metrics["clustering_coefficient"] = clustering.get(node_id, 0.0)
            
            # Specialized metrics for different graph types
            if node_id in self.collaboration_graph and len(self.collaboration_graph) > 1:
                collab_degree = self.collaboration_graph.degree(node_id)
                metrics["collaboration_connections"] = collab_degree
                
                # Collaboration strength (sum of edge weights)
                collab_strength = sum(
                    data.get('weight', 1.0) 
                    for _, _, data in self.collaboration_graph.edges(node_id, data=True)
                )
                metrics["collaboration_strength"] = collab_strength
            
            if node_id in self.influence_graph and len(self.influence_graph) > 1:
                in_degree = self.influence_graph.in_degree(node_id)
                out_degree = self.influence_graph.out_degree(node_id)
                
                metrics.update({
                    "influence_received": in_degree,
                    "influence_given": out_degree,
                    "influence_ratio": out_degree / max(in_degree, 1)
                })
            
            # Neighborhood metrics
            neighbors = list(self.main_graph.neighbors(node_id))
            metrics["neighborhood_size"] = len(neighbors)
            
            if neighbors:
                # Average neighbor connectivity
                neighbor_connections = [
                    self.main_graph.degree(neighbor) 
                    for neighbor in neighbors
                ]
                metrics["avg_neighbor_connectivity"] = np.mean(neighbor_connections)
                
                # Neighborhood diversity (number of different relationship types)
                relationship_types = set()
                for neighbor in neighbors:
                    edges = self.main_graph.edges(node_id, neighbor, data=True)
                    for _, _, data in edges:
                        relationship_types.add(data.get('relationship_type', 'unknown'))
                metrics["relationship_diversity"] = len(relationship_types)
            
            # Cache the results
            self.centrality_cache[cache_key] = (datetime.now(), metrics)
            
            # Update node object
            if node_id in self.nodes:
                node = self.nodes[node_id]
                node.degree_centrality = metrics.get("degree_centrality", 0.0)
                node.betweenness_centrality = metrics.get("betweenness_centrality", 0.0)
                node.closeness_centrality = metrics.get("closeness_centrality", 0.0)
                node.pagerank = metrics.get("pagerank", 0.0)
                node.cluster_coefficient = metrics.get("clustering_coefficient", 0.0)
                node.last_updated = datetime.now()
            
            logger.info(f"Calculated network metrics for {node_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating network metrics: {str(e)}")
            return {}
    
    async def detect_communities(self, algorithm: str = "louvain") -> Dict[int, NetworkCommunity]:
        """Detect communities in the creator network"""
        try:
            # Check cache
            cache_key = f"communities_{algorithm}"
            if cache_key in self.community_cache:
                cached_time, communities = self.community_cache[cache_key]
                if (datetime.now() - cached_time).seconds < 3600:  # 1 hour cache
                    return communities
            
            communities = {}
            
            if len(self.main_graph) < 3:
                logger.warning("Not enough nodes for community detection")
                return communities
            
            # Convert to undirected graph for community detection
            undirected_graph = self.main_graph.to_undirected()
            
            # Apply community detection algorithm
            if algorithm == "louvain":
                import networkx.algorithms.community as nx_comm
                community_sets = nx_comm.louvain_communities(undirected_graph)
            elif algorithm == "greedy_modularity":
                community_sets = nx.community.greedy_modularity_communities(undirected_graph)
            else:
                logger.warning(f"Unknown algorithm {algorithm}, using louvain")
                community_sets = nx_comm.louvain_communities(undirected_graph)
            
            # Create NetworkCommunity objects
            for i, community_set in enumerate(community_sets):
                members = list(community_set)
                
                # Analyze community characteristics
                genre_focus = await self._analyze_community_genres(members)
                skill_specialization = await self._analyze_community_skills(members)
                
                # Calculate community metrics
                subgraph = undirected_graph.subgraph(members)
                internal_edges = subgraph.number_of_edges()
                possible_internal_edges = len(members) * (len(members) - 1) / 2
                internal_density = internal_edges / max(possible_internal_edges, 1)
                
                community = NetworkCommunity(
                    community_id=i,
                    members=members,
                    community_type="genre_based" if genre_focus else "skill_based",
                    genre_focus=genre_focus,
                    skill_specialization=skill_specialization,
                    internal_density=internal_density
                )
                
                communities[i] = community
                
                # Update node community assignments
                for member_id in members:
                    if member_id in self.nodes:
                        self.nodes[member_id].community_id = i
            
            # Cache results
            self.community_cache[cache_key] = (datetime.now(), communities)
            
            # Store communities
            self.communities = communities
            
            # Persist communities
            for community in communities.values():
                await self._persist_community(community)
            
            logger.info(f"Detected {len(communities)} communities using {algorithm}")
            return communities
            
        except Exception as e:
            logger.error(f"Error detecting communities: {str(e)}")
            return {}
    
    async def find_shortest_collaboration_path(
        self,
        source_id: str,
        target_id: str,
        max_path_length: int = 4
    ) -> List[Tuple[str, str, float]]:
        """Find shortest path for potential collaboration"""
        try:
            if source_id not in self.collaboration_graph or target_id not in self.collaboration_graph:
                return []
            
            # Check cache
            cache_key = f"path_{source_id}_{target_id}"
            if cache_key in self.path_cache:
                return self.path_cache[cache_key]
            
            try:
                # Find shortest weighted path
                path = nx.shortest_path(
                    self.collaboration_graph,
                    source_id,
                    target_id,
                    weight='weight'
                )
                
                if len(path) > max_path_length:
                    return []
                
                # Build path with relationship details
                collaboration_path = []
                for i in range(len(path) - 1):
                    current_node = path[i]
                    next_node = path[i + 1]
                    
                    # Get edge weight
                    edge_data = self.collaboration_graph.get_edge_data(current_node, next_node)
                    weight = edge_data.get('weight', 0.5) if edge_data else 0.5
                    
                    collaboration_path.append((current_node, next_node, weight))
                
                # Cache result
                self.path_cache[cache_key] = collaboration_path
                
                logger.info(f"Found collaboration path: {source_id} -> {target_id} (length: {len(path)})")
                return collaboration_path
                
            except nx.NetworkXNoPath:
                logger.info(f"No collaboration path found between {source_id} and {target_id}")
                return []
            
        except Exception as e:
            logger.error(f"Error finding collaboration path: {str(e)}")
            return []
    
    async def analyze_influence_propagation(
        self,
        source_id: str,
        steps: int = 3
    ) -> Dict[str, float]:
        """Analyze how influence propagates from a source node"""
        try:
            if source_id not in self.influence_graph:
                return {}
            
            influence_scores = {source_id: 1.0}
            current_nodes = {source_id: 1.0}
            
            for step in range(steps):
                next_nodes = {}
                
                for node_id, current_influence in current_nodes.items():
                    # Get outgoing influence edges
                    for target in self.influence_graph.successors(node_id):
                        edge_data = self.influence_graph.get_edge_data(node_id, target)
                        edge_weight = edge_data.get('weight', 0.5) if edge_data else 0.5
                        
                        # Calculate propagated influence (diminishes with distance)
                        propagated_influence = current_influence * edge_weight * (0.7 ** step)
                        
                        if target not in influence_scores:
                            influence_scores[target] = 0.0
                        
                        influence_scores[target] += propagated_influence
                        
                        if target not in next_nodes:
                            next_nodes[target] = 0.0
                        next_nodes[target] += propagated_influence
                
                current_nodes = {
                    node_id: influence 
                    for node_id, influence in next_nodes.items() 
                    if influence > 0.01  # Threshold to prevent infinite propagation
                }
                
                if not current_nodes:
                    break
            
            # Remove source node and sort by influence
            influence_scores.pop(source_id, None)
            sorted_influences = dict(sorted(
                influence_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            ))
            
            logger.info(f"Analyzed influence propagation from {source_id} to {len(sorted_influences)} nodes")
            return sorted_influences
            
        except Exception as e:
            logger.error(f"Error analyzing influence propagation: {str(e)}")
            return {}
    
    async def recommend_collaboration_bridges(
        self,
        creator_id: str,
        target_community: int,
        limit: int = 5
    ) -> List[Tuple[str, float, str]]:
        """Recommend creators who can bridge to a target community"""
        try:
            if creator_id not in self.nodes:
                return []
            
            creator_community = self.nodes[creator_id].community_id
            if creator_community == target_community:
                return []  # Already in target community
            
            if target_community not in self.communities:
                return []
            
            bridge_candidates = []
            target_members = self.communities[target_community].members
            
            # Find creators connected to both communities
            for member_id in target_members:
                if member_id == creator_id:
                    continue
                
                # Check if there's a path to this member
                path = await self.find_shortest_collaboration_path(creator_id, member_id)
                
                if path and len(path) <= 2:  # Direct or one-hop connection
                    # Calculate bridge strength
                    bridge_strength = 1.0 / len(path)  # Shorter path = stronger bridge
                    
                    # Get member's network metrics
                    member_metrics = await self.calculate_network_metrics(member_id)
                    bridge_strength *= member_metrics.get("betweenness_centrality", 0.5)
                    
                    # Generate bridge reason
                    member_node = self.nodes.get(member_id)
                    if member_node:
                        member_genres = member_node.properties.get("primary_genres", [])
                        creator_genres = self.nodes[creator_id].properties.get("primary_genres", [])
                        
                        shared_genres = set(member_genres) & set(creator_genres)
                        if shared_genres:
                            reason = f"Shared genres: {', '.join(list(shared_genres)[:2])}"
                        else:
                            reason = f"Community bridge via {member_node.properties.get('username', member_id)}"
                    else:
                        reason = "Community connection opportunity"
                    
                    bridge_candidates.append((member_id, bridge_strength, reason))
            
            # Sort by bridge strength
            bridge_candidates.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Found {len(bridge_candidates)} bridge candidates for {creator_id} -> community {target_community}")
            return bridge_candidates[:limit]
            
        except Exception as e:
            logger.error(f"Error recommending collaboration bridges: {str(e)}")
            return []
    
    async def get_network_evolution_summary(self, days_back: int = 30) -> Dict[str, Any]:
        """Get summary of network evolution over time"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Count new nodes and edges
            new_nodes = len([
                node for node in self.nodes.values()
                if node.created_at >= cutoff_date
            ])
            
            new_edges = len([
                edge for edge in self.edges.values()
                if edge.created_at >= cutoff_date
            ])
            
            # Current network stats
            total_nodes = len(self.nodes)
            total_edges = len(self.edges)
            total_communities = len(self.communities)
            
            # Calculate network density
            max_possible_edges = total_nodes * (total_nodes - 1) / 2
            network_density = total_edges / max(max_possible_edges, 1)
            
            # Average path length (for connected components)
            try:
                if nx.is_connected(self.collaboration_graph.to_undirected()):
                    avg_path_length = nx.average_shortest_path_length(
                        self.collaboration_graph.to_undirected()
                    )
                else:
                    # Get largest connected component
                    largest_cc = max(
                        nx.connected_components(self.collaboration_graph.to_undirected()),
                        key=len
                    )
                    subgraph = self.collaboration_graph.subgraph(largest_cc)
                    avg_path_length = nx.average_shortest_path_length(subgraph)
            except:
                avg_path_length = 0.0
            
            # Most influential creators
            influence_scores = []
            for node_id, node in self.nodes.items():
                influence_score = (
                    node.degree_centrality * 0.3 +
                    node.betweenness_centrality * 0.3 +
                    node.pagerank * 0.4
                )
                influence_scores.append((node_id, influence_score))
            
            influence_scores.sort(key=lambda x: x[1], reverse=True)
            top_influencers = influence_scores[:5]
            
            summary = {
                "period_days": days_back,
                "network_growth": {
                    "new_nodes": new_nodes,
                    "new_edges": new_edges,
                    "total_nodes": total_nodes,
                    "total_edges": total_edges
                },
                "network_structure": {
                    "density": network_density,
                    "communities": total_communities,
                    "avg_path_length": avg_path_length,
                    "clustering_coefficient": nx.average_clustering(
                        self.collaboration_graph.to_undirected()
                    ) if total_nodes > 0 else 0.0
                },
                "top_influencers": [
                    {
                        "creator_id": creator_id,
                        "username": self.nodes.get(creator_id, {}).properties.get("username", creator_id),
                        "influence_score": score
                    }
                    for creator_id, score in top_influencers
                ],
                "relationship_distribution": self._get_relationship_distribution(),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Generated network evolution summary for {days_back} days")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating network evolution summary: {str(e)}")
            return {}
    
    # --- Internal Helper Methods ---
    
    def _invalidate_caches(self):
        """Invalidate analysis caches when graph changes"""
        self.centrality_cache.clear()
        self.path_cache.clear()
        self.community_cache.clear()
    
    async def _analyze_community_genres(self, members: List[str]) -> List[str]:
        """Analyze common genres in a community"""
        try:
            genre_counter = Counter()
            
            for member_id in members:
                if member_id in self.nodes:
                    member_genres = self.nodes[member_id].properties.get("primary_genres", [])
                    genre_counter.update(member_genres)
            
            # Return genres that appear in at least 30% of members
            threshold = max(1, len(members) * 0.3)
            common_genres = [
                genre for genre, count in genre_counter.items()
                if count >= threshold
            ]
            
            return common_genres[:5]  # Top 5 common genres
            
        except Exception as e:
            logger.error(f"Error analyzing community genres: {str(e)}")
            return []
    
    async def _analyze_community_skills(self, members: List[str]) -> List[str]:
        """Analyze common skills in a community"""
        try:
            skill_counter = Counter()
            
            for member_id in members:
                if member_id in self.nodes:
                    member_skills = self.nodes[member_id].properties.get("skills", [])
                    skill_counter.update(member_skills)
            
            # Return skills that appear in at least 25% of members
            threshold = max(1, len(members) * 0.25)
            common_skills = [
                skill for skill, count in skill_counter.items()
                if count >= threshold
            ]
            
            return common_skills[:5]  # Top 5 common skills
            
        except Exception as e:
            logger.error(f"Error analyzing community skills: {str(e)}")
            return []
    
    def _get_relationship_distribution(self) -> Dict[str, int]:
        """Get distribution of relationship types"""
        distribution = Counter()
        
        for edge in self.edges.values():
            distribution[edge.relationship_type.value] += 1
        
        return dict(distribution)
    
    async def _persist_node(self, node: NetworkNode):
        """Persist node to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO nodes 
                (node_id, node_type, properties, centrality_metrics, created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                node.node_id,
                node.node_type,
                json.dumps(node.properties),
                json.dumps({
                    "degree_centrality": node.degree_centrality,
                    "betweenness_centrality": node.betweenness_centrality,
                    "closeness_centrality": node.closeness_centrality,
                    "pagerank": node.pagerank
                }),
                node.created_at.isoformat(),
                node.last_updated.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error persisting node: {str(e)}")
    
    async def _persist_edge(self, edge: RelationshipEdge):
        """Persist edge to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            edge_id = f"{edge.source_id}_{edge.target_id}_{edge.relationship_type.value}"
            
            cursor.execute('''
                INSERT OR REPLACE INTO edges 
                (edge_id, source_id, target_id, relationship_type, weight, confidence, metadata, created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                edge_id,
                edge.source_id,
                edge.target_id,
                edge.relationship_type.value,
                edge.weight,
                edge.confidence,
                json.dumps(edge.metadata),
                edge.created_at.isoformat(),
                edge.last_updated.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error persisting edge: {str(e)}")
    
    async def _persist_community(self, community: NetworkCommunity):
        """Persist community to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO communities 
                (community_id, members, community_type, characteristics, metrics, formation_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                community.community_id,
                json.dumps(community.members),
                community.community_type,
                json.dumps({
                    "genre_focus": community.genre_focus,
                    "skill_specialization": community.skill_specialization
                }),
                json.dumps({
                    "internal_density": community.internal_density,
                    "external_connectivity": community.external_connectivity
                }),
                community.formation_date.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error persisting community: {str(e)}")
    
    async def load_from_database(self):
        """Load graph data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load nodes
            cursor.execute("SELECT * FROM nodes")
            for row in cursor.fetchall():
                node_id, node_type, properties_json, centrality_json, created_at, last_updated = row
                
                properties = json.loads(properties_json)
                centrality = json.loads(centrality_json)
                
                node = NetworkNode(
                    node_id=node_id,
                    node_type=node_type,
                    properties=properties,
                    degree_centrality=centrality.get("degree_centrality", 0.0),
                    betweenness_centrality=centrality.get("betweenness_centrality", 0.0),
                    closeness_centrality=centrality.get("closeness_centrality", 0.0),
                    pagerank=centrality.get("pagerank", 0.0),
                    created_at=datetime.fromisoformat(created_at),
                    last_updated=datetime.fromisoformat(last_updated)
                )
                
                self.nodes[node_id] = node
                self.main_graph.add_node(node_id, **properties, node_object=node)
            
            # Load edges
            cursor.execute("SELECT * FROM edges")
            for row in cursor.fetchall():
                edge_id, source_id, target_id, rel_type, weight, confidence, metadata_json, created_at, last_updated = row
                
                metadata = json.loads(metadata_json)
                relationship_type = RelationshipType(rel_type)
                
                edge = RelationshipEdge(
                    source_id=source_id,
                    target_id=target_id,
                    relationship_type=relationship_type,
                    weight=weight,
                    confidence=confidence,
                    metadata=metadata,
                    created_at=datetime.fromisoformat(created_at),
                    last_updated=datetime.fromisoformat(last_updated)
                )
                
                self.edges[edge_id] = edge
                
                # Add to appropriate graphs
                await self.add_relationship(
                    source_id, target_id, relationship_type, weight, confidence, metadata
                )
            
            conn.close()
            logger.info("Loaded graph data from database")
            
        except Exception as e:
            logger.error(f"Error loading from database: {str(e)}")


# Module exports
__all__ = [
    'CreatorGraphDatabase',
    'RelationshipType',
    'EdgeWeight',
    'RelationshipEdge',
    'NetworkNode',
    'NetworkCommunity'
]