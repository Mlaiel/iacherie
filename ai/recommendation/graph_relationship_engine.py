"""Graph Database Engine for Complex Creator Relationships
=========================================================

Advanced graph database integration for modeling complex creator relationships,
influence networks, collaboration patterns, and recommendation optimization.

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
⚠️  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Development Team Specialties:
- Lead Dev + AI Architect Developer
- Senior Backend Developer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Developer
- DevOps Engineer
- AI Prompt Engineer
Email: mlaiel@live.de
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import uuid
from collections import defaultdict, deque
import math

# Graph database imports
try:
    import networkx as nx
    import numpy as np
    from scipy.sparse import csr_matrix
    from sklearn.cluster import SpectralClustering
    from sklearn.metrics.pairwise import cosine_similarity
    GRAPH_AVAILABLE = True
except ImportError:
    GRAPH_AVAILABLE = False
    # Mock classes for environments without graph libraries
    class MockGraph:
        def __init__(self): 
            self.nodes = {}
            self.edges = {}
        def add_node(self, *args, **kwargs): pass
        def add_edge(self, *args, **kwargs): pass
        def has_node(self, node): return node in self.nodes
        def neighbors(self, node): return []
        def __len__(self): return len(self.nodes)
    
    nx = type('MockNetworkX', (), {
        'DiGraph': MockGraph,
        'Graph': MockGraph,
        'pagerank': lambda g: {},
        'betweenness_centrality': lambda g: {},
        'clustering': lambda g: {},
        'shortest_path_length': lambda g, s, t: 1
    })()

logger = logging.getLogger(__name__)


class RelationshipType(Enum):
    """Types of relationships between creators"""
    COLLABORATION = "collaboration"
    INFLUENCE = "influence"
    MUTUAL_FOLLOW = "mutual_follow"
    FEATURE = "feature"
    REMIX = "remix"
    MENTOR_MENTEE = "mentor_mentee"
    SAME_GENRE = "same_genre"
    AUDIENCE_OVERLAP = "audience_overlap"
    BRAND_PARTNERSHIP = "brand_partnership"
    LABEL_MATE = "label_mate"
    GEOGRAPHIC = "geographic"
    PLATFORM_CROSSOVER = "platform_crossover"


class NodeType(Enum):
    """Types of nodes in the creator graph"""
    CREATOR = "creator"
    GENRE = "genre"
    PLATFORM = "platform"
    LABEL = "label"
    LOCATION = "location"
    SKILL = "skill"
    AUDIENCE_SEGMENT = "audience_segment"
    BRAND = "brand"


@dataclass
class GraphNode:
    """Enhanced graph node representation"""
    id: str
    node_type: NodeType
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.node_type.value,
            'properties': self.properties,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class GraphEdge:
    """Enhanced graph edge representation"""
    source: str
    target: str
    relationship_type: RelationshipType
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source': self.source,
            'target': self.target,
            'type': self.relationship_type.value,
            'weight': self.weight,
            'properties': self.properties,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


@dataclass
class InfluenceScore:
    """Creator influence scoring in the network"""
    creator_id: str
    global_influence: float
    genre_influence: Dict[str, float] = field(default_factory=dict)
    platform_influence: Dict[str, float] = field(default_factory=dict)
    collaboration_reach: float = 0.0
    network_centrality: float = 0.0
    trend_leadership: float = 0.0
    
    def overall_score(self) -> float:
        """Calculate overall influence score"""
        return (
            self.global_influence * 0.3 +
            sum(self.genre_influence.values()) / max(len(self.genre_influence), 1) * 0.25 +
            sum(self.platform_influence.values()) / max(len(self.platform_influence), 1) * 0.2 +
            self.collaboration_reach * 0.15 +
            self.network_centrality * 0.1
        )


@dataclass
class CommunityCluster:
    """Creator community cluster analysis"""
    cluster_id: str
    members: List[str] = field(default_factory=list)
    dominant_genres: List[str] = field(default_factory=list)
    avg_influence: float = 0.0
    internal_connections: int = 0
    external_connections: int = 0
    cohesion_score: float = 0.0
    description: str = ""


@dataclass
class PathAnalysis:
    """Analysis of connection paths between creators"""
    source: str
    target: str
    shortest_path: List[str] = field(default_factory=list)
    path_length: int = 0
    path_strength: float = 0.0
    intermediary_influencers: List[str] = field(default_factory=list)
    connection_types: List[RelationshipType] = field(default_factory=list)
    trust_score: float = 0.0


class GraphRelationshipEngine:
    """
    Advanced Graph Database Engine for Creator Relationships
    
    Provides sophisticated graph-based analysis for:
    - Complex relationship modeling
    - Influence network analysis
    - Community detection
    - Path finding and recommendation
    - Network evolution tracking
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the graph relationship engine"""
        self.config = config or {}
        self.is_initialized = False
        
        # Graph structures
        self.creator_graph = nx.DiGraph() if GRAPH_AVAILABLE else MockGraph()
        self.genre_graph = nx.Graph() if GRAPH_AVAILABLE else MockGraph()
        self.platform_graph = nx.Graph() if GRAPH_AVAILABLE else MockGraph()
        self.collaboration_graph = nx.Graph() if GRAPH_AVAILABLE else MockGraph()
        
        # Node and edge storage
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, GraphEdge] = {}
        
        # Analysis caches
        self.influence_cache: Dict[str, InfluenceScore] = {}
        self.community_cache: Dict[str, List[CommunityCluster]] = {}
        self.path_cache: Dict[Tuple[str, str], PathAnalysis] = {}
        
        # Analytics
        self.analytics = {
            'total_nodes': 0,
            'total_edges': 0,
            'avg_degree': 0.0,
            'clustering_coefficient': 0.0,
            'network_density': 0.0,
            'largest_component_size': 0,
            'communities_detected': 0
        }
        
        # Update tracking
        self.last_analysis_update = datetime.now()
        self.update_frequency = timedelta(hours=1)
        
        logger.info("GraphRelationshipEngine initialized")
    
    async def initialize(self) -> bool:
        """Initialize the graph relationship engine"""
        try:
            logger.info("Initializing Graph Relationship Engine...")
            
            # Initialize graph structures
            await self._initialize_graphs()
            
            # Load existing data
            await self._load_graph_data()
            
            # Perform initial analysis
            await self._perform_initial_analysis()
            
            self.is_initialized = True
            logger.info("Graph Relationship Engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Graph Relationship Engine: {e}")
            raise Exception(f"Initialization failed: {e}")
    
    async def _initialize_graphs(self) -> None:
        """Initialize graph data structures"""
        try:
            if not GRAPH_AVAILABLE:
                logger.warning("Graph libraries not available, using mock graphs")
                return
            
            # Configure graph properties
            self.creator_graph = nx.DiGraph()
            self.genre_graph = nx.Graph()
            self.platform_graph = nx.Graph()
            self.collaboration_graph = nx.Graph()
            
            logger.debug("Graph structures initialized")
            
        except Exception as e:
            logger.error(f"Error initializing graphs: {e}")
            raise
    
    async def _load_graph_data(self) -> None:
        """Load existing graph data"""
        try:
            # In a real implementation, this would load from persistent storage
            # For now, we'll start with empty graphs
            logger.debug("Graph data loaded")
            
        except Exception as e:
            logger.error(f"Error loading graph data: {e}")
            raise
    
    async def _perform_initial_analysis(self) -> None:
        """Perform initial graph analysis"""
        try:
            await self._update_analytics()
            logger.debug("Initial graph analysis completed")
            
        except Exception as e:
            logger.error(f"Error in initial analysis: {e}")
            raise
    
    async def add_creator_node(
        self,
        creator_id: str,
        creator_data: Dict[str, Any]
    ) -> bool:
        """Add creator node to the graph"""
        try:
            # Create node
            node = GraphNode(
                id=creator_id,
                node_type=NodeType.CREATOR,
                properties=creator_data
            )
            
            self.nodes[creator_id] = node
            
            # Add to main graph
            if hasattr(self.creator_graph, 'add_node'):
                self.creator_graph.add_node(creator_id, **creator_data)
            
            # Add related nodes (genres, platforms, etc.)
            await self._add_related_nodes(creator_id, creator_data)
            
            # Update analytics
            await self._update_analytics()
            
            logger.debug(f"Creator node {creator_id} added to graph")
            return True
            
        except Exception as e:
            logger.error(f"Error adding creator node {creator_id}: {e}")
            return False
    
    async def _add_related_nodes(
        self,
        creator_id: str,
        creator_data: Dict[str, Any]
    ) -> None:
        """Add related nodes (genres, platforms, etc.) for a creator"""
        try:
            # Add genre nodes and connections
            genres = creator_data.get('genres', [])
            for genre in genres:
                genre_id = f"genre_{genre}"
                if genre_id not in self.nodes:
                    genre_node = GraphNode(
                        id=genre_id,
                        node_type=NodeType.GENRE,
                        properties={'name': genre}
                    )
                    self.nodes[genre_id] = genre_node
                
                # Connect creator to genre
                await self.add_relationship(
                    creator_id,
                    genre_id,
                    RelationshipType.SAME_GENRE,
                    weight=1.0
                )
            
            # Add platform nodes and connections
            platforms = creator_data.get('platforms', [])
            for platform in platforms:
                platform_id = f"platform_{platform}"
                if platform_id not in self.nodes:
                    platform_node = GraphNode(
                        id=platform_id,
                        node_type=NodeType.PLATFORM,
                        properties={'name': platform}
                    )
                    self.nodes[platform_id] = platform_node
                
                # Connect creator to platform
                await self.add_relationship(
                    creator_id,
                    platform_id,
                    RelationshipType.PLATFORM_CROSSOVER,
                    weight=1.0
                )
            
            # Add location node if available
            location = creator_data.get('location')
            if location:
                location_id = f"location_{location}"
                if location_id not in self.nodes:
                    location_node = GraphNode(
                        id=location_id,
                        node_type=NodeType.LOCATION,
                        properties={'name': location}
                    )
                    self.nodes[location_id] = location_node
                
                # Connect creator to location
                await self.add_relationship(
                    creator_id,
                    location_id,
                    RelationshipType.GEOGRAPHIC,
                    weight=1.0
                )
            
        except Exception as e:
            logger.error(f"Error adding related nodes for {creator_id}: {e}")
    
    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        weight: float = 1.0,
        properties: Optional[Dict] = None,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """Add relationship edge between nodes"""
        try:
            # Create edge
            edge_id = f"{source_id}_{target_id}_{relationship_type.value}"
            edge = GraphEdge(
                source=source_id,
                target=target_id,
                relationship_type=relationship_type,
                weight=weight,
                properties=properties or {},
                expires_at=expires_at
            )
            
            self.edges[edge_id] = edge
            
            # Add to appropriate graphs
            if hasattr(self.creator_graph, 'add_edge'):
                self.creator_graph.add_edge(
                    source_id, 
                    target_id, 
                    type=relationship_type.value,
                    weight=weight,
                    **edge.properties
                )
            
            # Add to specialized graphs based on relationship type
            if relationship_type == RelationshipType.COLLABORATION:
                if hasattr(self.collaboration_graph, 'add_edge'):
                    self.collaboration_graph.add_edge(source_id, target_id, weight=weight)
            
            # Clear relevant caches
            self._clear_analysis_caches(source_id, target_id)
            
            logger.debug(f"Relationship {relationship_type.value} added between {source_id} and {target_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding relationship: {e}")
            return False
    
    async def calculate_influence_score(
        self,
        creator_id: str,
        force_recalculate: bool = False
    ) -> InfluenceScore:
        """Calculate comprehensive influence score for a creator"""
        try:
            # Check cache
            if not force_recalculate and creator_id in self.influence_cache:
                return self.influence_cache[creator_id]
            
            if not hasattr(self.creator_graph, 'has_node') or not self.creator_graph.has_node(creator_id):
                return InfluenceScore(creator_id=creator_id, global_influence=0.0)
            
            # Calculate different influence metrics
            global_influence = await self._calculate_global_influence(creator_id)
            genre_influence = await self._calculate_genre_influence(creator_id)
            platform_influence = await self._calculate_platform_influence(creator_id)
            collaboration_reach = await self._calculate_collaboration_reach(creator_id)
            network_centrality = await self._calculate_network_centrality(creator_id)
            trend_leadership = await self._calculate_trend_leadership(creator_id)
            
            influence_score = InfluenceScore(
                creator_id=creator_id,
                global_influence=global_influence,
                genre_influence=genre_influence,
                platform_influence=platform_influence,
                collaboration_reach=collaboration_reach,
                network_centrality=network_centrality,
                trend_leadership=trend_leadership
            )
            
            # Cache the result
            self.influence_cache[creator_id] = influence_score
            
            return influence_score
            
        except Exception as e:
            logger.error(f"Error calculating influence score for {creator_id}: {e}")
            return InfluenceScore(creator_id=creator_id, global_influence=0.0)
    
    async def _calculate_global_influence(self, creator_id: str) -> float:
        """Calculate global influence using PageRank algorithm"""
        try:
            if not GRAPH_AVAILABLE:
                return 0.5
            
            pagerank_scores = nx.pagerank(self.creator_graph, weight='weight')
            return pagerank_scores.get(creator_id, 0.0)
            
        except Exception as e:
            logger.error(f"Error calculating global influence: {e}")
            return 0.0
    
    async def _calculate_genre_influence(self, creator_id: str) -> Dict[str, float]:
        """Calculate influence within specific genres"""
        try:
            genre_influence = {}
            
            # Get creator's genres
            creator_node = self.nodes.get(creator_id)
            if not creator_node:
                return {}
            
            genres = creator_node.properties.get('genres', [])
            
            for genre in genres:
                # Find other creators in the same genre
                genre_creators = []
                for node_id, node in self.nodes.items():
                    if (node.node_type == NodeType.CREATOR and 
                        genre in node.properties.get('genres', [])):
                        genre_creators.append(node_id)
                
                if len(genre_creators) > 1:
                    # Create subgraph for this genre
                    if GRAPH_AVAILABLE and hasattr(self.creator_graph, 'subgraph'):
                        genre_subgraph = self.creator_graph.subgraph(genre_creators)
                        pagerank_scores = nx.pagerank(genre_subgraph, weight='weight')
                        genre_influence[genre] = pagerank_scores.get(creator_id, 0.0)
                    else:
                        genre_influence[genre] = 1.0 / len(genre_creators)
            
            return genre_influence
            
        except Exception as e:
            logger.error(f"Error calculating genre influence: {e}")
            return {}
    
    async def _calculate_platform_influence(self, creator_id: str) -> Dict[str, float]:
        """Calculate influence within specific platforms"""
        try:
            platform_influence = {}
            
            # Get creator's platforms
            creator_node = self.nodes.get(creator_id)
            if not creator_node:
                return {}
            
            platforms = creator_node.properties.get('platforms', [])
            
            for platform in platforms:
                # Calculate influence based on follower count and engagement
                follower_count = creator_node.properties.get(f'{platform}_followers', 0)
                engagement_rate = creator_node.properties.get(f'{platform}_engagement', 0.0)
                
                # Normalize influence score
                platform_influence[platform] = min(
                    (follower_count / 100000) * 0.7 + engagement_rate * 0.3,
                    1.0
                )
            
            return platform_influence
            
        except Exception as e:
            logger.error(f"Error calculating platform influence: {e}")
            return {}
    
    async def _calculate_collaboration_reach(self, creator_id: str) -> float:
        """Calculate reach through collaborations"""
        try:
            if not hasattr(self.collaboration_graph, 'has_node'):
                return 0.0
            
            if not self.collaboration_graph.has_node(creator_id):
                return 0.0
            
            # Calculate reach as the sum of collaborator influences
            collaborators = list(self.collaboration_graph.neighbors(creator_id))
            total_reach = 0.0
            
            for collaborator in collaborators:
                collaborator_node = self.nodes.get(collaborator)
                if collaborator_node:
                    follower_count = collaborator_node.properties.get('follower_count', 0)
                    total_reach += follower_count
            
            # Normalize reach score
            return min(total_reach / 1000000, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating collaboration reach: {e}")
            return 0.0
    
    async def _calculate_network_centrality(self, creator_id: str) -> float:
        """Calculate network centrality metrics"""
        try:
            if not GRAPH_AVAILABLE or not hasattr(self.creator_graph, 'has_node'):
                return 0.0
            
            if not self.creator_graph.has_node(creator_id):
                return 0.0
            
            # Calculate betweenness centrality
            centrality_scores = nx.betweenness_centrality(self.creator_graph, weight='weight')
            return centrality_scores.get(creator_id, 0.0)
            
        except Exception as e:
            logger.error(f"Error calculating network centrality: {e}")
            return 0.0
    
    async def _calculate_trend_leadership(self, creator_id: str) -> float:
        """Calculate trend leadership score"""
        try:
            # This would analyze trend adoption patterns
            # For now, return a mock score based on recent activity
            creator_node = self.nodes.get(creator_id)
            if not creator_node:
                return 0.0
            
            # Mock calculation based on recent collaborations
            recent_collabs = [
                edge for edge in self.edges.values()
                if ((edge.source == creator_id or edge.target == creator_id) and
                    edge.relationship_type == RelationshipType.COLLABORATION and
                    edge.created_at > datetime.now() - timedelta(days=90))
            ]
            
            return min(len(recent_collabs) / 10, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating trend leadership: {e}")
            return 0.0
    
    async def detect_communities(
        self,
        algorithm: str = "spectral",
        min_size: int = 3
    ) -> List[CommunityCluster]:
        """Detect creator communities in the network"""
        try:
            cache_key = f"{algorithm}_{min_size}"
            if cache_key in self.community_cache:
                return self.community_cache[cache_key]
            
            communities = []
            
            if not GRAPH_AVAILABLE or not hasattr(self.creator_graph, 'nodes'):
                return communities
            
            # Get creator nodes only
            creator_nodes = [
                node_id for node_id, node in self.nodes.items()
                if node.node_type == NodeType.CREATOR
            ]
            
            if len(creator_nodes) < min_size:
                return communities
            
            # Create adjacency matrix for clustering
            node_to_idx = {node: idx for idx, node in enumerate(creator_nodes)}
            n_nodes = len(creator_nodes)
            
            # Build adjacency matrix
            adjacency_matrix = np.zeros((n_nodes, n_nodes))
            
            for edge in self.edges.values():
                if (edge.source in node_to_idx and edge.target in node_to_idx and
                    edge.relationship_type in [RelationshipType.COLLABORATION, RelationshipType.MUTUAL_FOLLOW]):
                    src_idx = node_to_idx[edge.source]
                    tgt_idx = node_to_idx[edge.target]
                    adjacency_matrix[src_idx, tgt_idx] = edge.weight
                    adjacency_matrix[tgt_idx, src_idx] = edge.weight
            
            # Perform spectral clustering
            try:
                from sklearn.cluster import SpectralClustering
                n_clusters = min(max(2, len(creator_nodes) // 5), 10)
                clustering = SpectralClustering(
                    n_clusters=n_clusters,
                    affinity='precomputed',
                    random_state=42
                )
                cluster_labels = clustering.fit_predict(adjacency_matrix)
                
                # Group nodes by cluster
                clusters = defaultdict(list)
                for idx, label in enumerate(cluster_labels):
                    clusters[label].append(creator_nodes[idx])
                
                # Create community cluster objects
                for cluster_id, members in clusters.items():
                    if len(members) >= min_size:
                        community = await self._analyze_community(
                            f"cluster_{cluster_id}", members
                        )
                        communities.append(community)
                
            except ImportError:
                # Fallback to simple connected components
                if hasattr(self.creator_graph, 'connected_components'):
                    components = nx.connected_components(
                        self.creator_graph.to_undirected()
                    )
                    for idx, component in enumerate(components):
                        members = [node for node in component if node in creator_nodes]
                        if len(members) >= min_size:
                            community = await self._analyze_community(
                                f"component_{idx}", members
                            )
                            communities.append(community)
            
            # Cache results
            self.community_cache[cache_key] = communities
            
            # Update analytics
            self.analytics['communities_detected'] = len(communities)
            
            return communities
            
        except Exception as e:
            logger.error(f"Error detecting communities: {e}")
            return []
    
    async def _analyze_community(
        self,
        cluster_id: str,
        members: List[str]
    ) -> CommunityCluster:
        """Analyze a community cluster"""
        try:
            # Analyze dominant genres
            genre_counts = defaultdict(int)
            total_influence = 0.0
            
            for member in members:
                member_node = self.nodes.get(member)
                if member_node:
                    # Count genres
                    genres = member_node.properties.get('genres', [])
                    for genre in genres:
                        genre_counts[genre] += 1
                    
                    # Sum influence
                    influence = await self.calculate_influence_score(member)
                    total_influence += influence.overall_score()
            
            # Get dominant genres (top 3)
            dominant_genres = [
                genre for genre, count in 
                sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            ]
            
            # Calculate internal/external connections
            internal_connections = 0
            external_connections = 0
            
            for edge in self.edges.values():
                if edge.source in members:
                    if edge.target in members:
                        internal_connections += 1
                    else:
                        external_connections += 1
            
            # Calculate cohesion score
            total_possible_internal = len(members) * (len(members) - 1)
            cohesion_score = internal_connections / max(total_possible_internal, 1)
            
            # Generate description
            description = f"Community of {len(members)} creators"
            if dominant_genres:
                description += f" focused on {', '.join(dominant_genres[:2])}"
            
            return CommunityCluster(
                cluster_id=cluster_id,
                members=members,
                dominant_genres=dominant_genres,
                avg_influence=total_influence / len(members),
                internal_connections=internal_connections,
                external_connections=external_connections,
                cohesion_score=cohesion_score,
                description=description
            )
            
        except Exception as e:
            logger.error(f"Error analyzing community {cluster_id}: {e}")
            return CommunityCluster(cluster_id=cluster_id, members=members)
    
    async def find_connection_path(
        self,
        source_id: str,
        target_id: str,
        max_hops: int = 4
    ) -> PathAnalysis:
        """Find connection path between two creators"""
        try:
            cache_key = (source_id, target_id)
            if cache_key in self.path_cache:
                return self.path_cache[cache_key]
            
            path_analysis = PathAnalysis(source=source_id, target=target_id)
            
            if not (hasattr(self.creator_graph, 'has_node') and
                    self.creator_graph.has_node(source_id) and
                    self.creator_graph.has_node(target_id)):
                return path_analysis
            
            try:
                if GRAPH_AVAILABLE:
                    # Find shortest path
                    shortest_path = nx.shortest_path(
                        self.creator_graph.to_undirected(),
                        source_id,
                        target_id
                    )
                    
                    path_analysis.shortest_path = shortest_path
                    path_analysis.path_length = len(shortest_path) - 1
                    
                    # Calculate path strength
                    path_strength = await self._calculate_path_strength(shortest_path)
                    path_analysis.path_strength = path_strength
                    
                    # Identify intermediary influencers
                    intermediaries = shortest_path[1:-1]  # Exclude source and target
                    influencer_intermediaries = []
                    
                    for intermediary in intermediaries:
                        influence = await self.calculate_influence_score(intermediary)
                        if influence.overall_score() > 0.5:
                            influencer_intermediaries.append(intermediary)
                    
                    path_analysis.intermediary_influencers = influencer_intermediaries
                    
                    # Analyze connection types
                    connection_types = []
                    for i in range(len(shortest_path) - 1):
                        edge_id = f"{shortest_path[i]}_{shortest_path[i+1]}"
                        edge = self.edges.get(edge_id)
                        if edge:
                            connection_types.append(edge.relationship_type)
                    
                    path_analysis.connection_types = connection_types
                    
                    # Calculate trust score
                    trust_score = await self._calculate_path_trust(shortest_path)
                    path_analysis.trust_score = trust_score
                
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                # No path exists
                path_analysis.path_length = -1
            
            # Cache result
            self.path_cache[cache_key] = path_analysis
            
            return path_analysis
            
        except Exception as e:
            logger.error(f"Error finding connection path: {e}")
            return PathAnalysis(source=source_id, target=target_id, path_length=-1)
    
    async def _calculate_path_strength(self, path: List[str]) -> float:
        """Calculate strength of a connection path"""
        try:
            if len(path) < 2:
                return 0.0
            
            total_strength = 0.0
            edge_count = 0
            
            for i in range(len(path) - 1):
                # Find edge between consecutive nodes
                for edge in self.edges.values():
                    if ((edge.source == path[i] and edge.target == path[i+1]) or
                        (edge.source == path[i+1] and edge.target == path[i])):
                        total_strength += edge.weight
                        edge_count += 1
                        break
            
            return total_strength / max(edge_count, 1)
            
        except Exception as e:
            logger.error(f"Error calculating path strength: {e}")
            return 0.0
    
    async def _calculate_path_trust(self, path: List[str]) -> float:
        """Calculate trust score for a connection path"""
        try:
            if len(path) < 2:
                return 0.0
            
            # Trust degrades with path length
            length_penalty = 1.0 / len(path)
            
            # Trust increases with intermediary influence
            intermediary_trust = 0.0
            if len(path) > 2:
                for intermediary in path[1:-1]:
                    influence = await self.calculate_influence_score(intermediary)
                    intermediary_trust += influence.overall_score()
                intermediary_trust /= (len(path) - 2)
            else:
                intermediary_trust = 1.0  # Direct connection
            
            return length_penalty * 0.4 + intermediary_trust * 0.6
            
        except Exception as e:
            logger.error(f"Error calculating path trust: {e}")
            return 0.0
    
    async def get_recommendation_candidates(
        self,
        creator_id: str,
        algorithm: str = "hybrid",
        limit: int = 20
    ) -> List[Tuple[str, float]]:
        """Get recommendation candidates using graph analysis"""
        try:
            candidates = []
            
            if algorithm == "network_proximity":
                candidates = await self._get_network_proximity_candidates(creator_id)
            elif algorithm == "community_based":
                candidates = await self._get_community_based_candidates(creator_id)
            elif algorithm == "influence_propagation":
                candidates = await self._get_influence_propagation_candidates(creator_id)
            elif algorithm == "hybrid":
                # Combine multiple algorithms
                proximity_candidates = await self._get_network_proximity_candidates(creator_id)
                community_candidates = await self._get_community_based_candidates(creator_id)
                influence_candidates = await self._get_influence_propagation_candidates(creator_id)
                
                # Merge and weight candidates
                candidate_scores = defaultdict(float)
                
                for candidate, score in proximity_candidates:
                    candidate_scores[candidate] += score * 0.4
                
                for candidate, score in community_candidates:
                    candidate_scores[candidate] += score * 0.3
                
                for candidate, score in influence_candidates:
                    candidate_scores[candidate] += score * 0.3
                
                candidates = list(candidate_scores.items())
            
            # Sort by score and limit results
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recommendation candidates: {e}")
            return []
    
    async def _get_network_proximity_candidates(self, creator_id: str) -> List[Tuple[str, float]]:
        """Get candidates based on network proximity"""
        try:
            candidates = []
            
            if not hasattr(self.creator_graph, 'neighbors'):
                return candidates
            
            # Get direct neighbors (2-hop connections)
            visited = {creator_id}
            queue = deque([(creator_id, 0, 1.0)])  # (node, distance, score)
            
            while queue:
                current_node, distance, current_score = queue.popleft()
                
                if distance >= 2:  # Limit to 2 hops
                    continue
                
                try:
                    neighbors = list(self.creator_graph.neighbors(current_node))
                except:
                    neighbors = []
                
                for neighbor in neighbors:
                    if neighbor not in visited and neighbor != creator_id:
                        visited.add(neighbor)
                        
                        # Calculate score based on distance and edge weight
                        edge_weight = 1.0
                        for edge in self.edges.values():
                            if ((edge.source == current_node and edge.target == neighbor) or
                                (edge.source == neighbor and edge.target == current_node)):
                                edge_weight = edge.weight
                                break
                        
                        score = current_score * edge_weight * (1.0 / (distance + 1))
                        
                        # Only include creator nodes
                        neighbor_node = self.nodes.get(neighbor)
                        if neighbor_node and neighbor_node.node_type == NodeType.CREATOR:
                            candidates.append((neighbor, score))
                        
                        if distance < 1:  # Continue search from this neighbor
                            queue.append((neighbor, distance + 1, score))
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error getting network proximity candidates: {e}")
            return []
    
    async def _get_community_based_candidates(self, creator_id: str) -> List[Tuple[str, float]]:
        """Get candidates from the same communities"""
        try:
            candidates = []
            
            # Find communities containing the creator
            communities = await self.detect_communities()
            creator_communities = [
                community for community in communities
                if creator_id in community.members
            ]
            
            for community in creator_communities:
                for member in community.members:
                    if member != creator_id:
                        # Score based on community cohesion and member influence
                        influence = await self.calculate_influence_score(member)
                        score = community.cohesion_score * 0.6 + influence.overall_score() * 0.4
                        candidates.append((member, score))
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error getting community-based candidates: {e}")
            return []
    
    async def _get_influence_propagation_candidates(self, creator_id: str) -> List[Tuple[str, float]]:
        """Get candidates based on influence propagation"""
        try:
            candidates = []
            
            # Get creator's influence score
            creator_influence = await self.calculate_influence_score(creator_id)
            
            # Find creators with complementary influence profiles
            for node_id, node in self.nodes.items():
                if (node.node_type == NodeType.CREATOR and 
                    node_id != creator_id):
                    
                    candidate_influence = await self.calculate_influence_score(node_id)
                    
                    # Calculate influence compatibility
                    score = await self._calculate_influence_compatibility(
                        creator_influence, candidate_influence
                    )
                    
                    if score > 0.3:  # Minimum threshold
                        candidates.append((node_id, score))
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error getting influence propagation candidates: {e}")
            return []
    
    async def _calculate_influence_compatibility(
        self,
        influence1: InfluenceScore,
        influence2: InfluenceScore
    ) -> float:
        """Calculate compatibility between two influence profiles"""
        try:
            # Genre influence overlap
            genres1 = set(influence1.genre_influence.keys())
            genres2 = set(influence2.genre_influence.keys())
            genre_overlap = len(genres1 & genres2) / len(genres1 | genres2) if genres1 | genres2 else 0
            
            # Platform influence overlap
            platforms1 = set(influence1.platform_influence.keys())
            platforms2 = set(influence2.platform_influence.keys())
            platform_overlap = len(platforms1 & platforms2) / len(platforms1 | platforms2) if platforms1 | platforms2 else 0
            
            # Influence balance (not too different levels)
            influence_diff = abs(influence1.overall_score() - influence2.overall_score())
            influence_balance = 1.0 - influence_diff
            
            # Combine factors
            compatibility = (
                genre_overlap * 0.4 +
                platform_overlap * 0.3 +
                influence_balance * 0.3
            )
            
            return compatibility
            
        except Exception as e:
            logger.error(f"Error calculating influence compatibility: {e}")
            return 0.0
    
    def _clear_analysis_caches(self, *node_ids: str) -> None:
        """Clear analysis caches for affected nodes"""
        try:
            # Clear influence cache for affected nodes
            for node_id in node_ids:
                if node_id in self.influence_cache:
                    del self.influence_cache[node_id]
            
            # Clear community cache
            self.community_cache.clear()
            
            # Clear path cache for affected nodes
            paths_to_remove = []
            for (source, target) in self.path_cache.keys():
                if source in node_ids or target in node_ids:
                    paths_to_remove.append((source, target))
            
            for path_key in paths_to_remove:
                del self.path_cache[path_key]
            
        except Exception as e:
            logger.error(f"Error clearing analysis caches: {e}")
    
    async def _update_analytics(self) -> None:
        """Update graph analytics"""
        try:
            # Count nodes and edges
            self.analytics['total_nodes'] = len(self.nodes)
            self.analytics['total_edges'] = len(self.edges)
            
            if GRAPH_AVAILABLE and hasattr(self.creator_graph, 'nodes'):
                # Calculate network metrics
                creator_nodes = [
                    node_id for node_id, node in self.nodes.items()
                    if node.node_type == NodeType.CREATOR
                ]
                
                if creator_nodes:
                    creator_subgraph = self.creator_graph.subgraph(creator_nodes)
                    
                    # Average degree
                    degrees = [d for n, d in creator_subgraph.degree()]
                    self.analytics['avg_degree'] = sum(degrees) / len(degrees) if degrees else 0
                    
                    # Network density
                    self.analytics['network_density'] = nx.density(creator_subgraph)
                    
                    # Clustering coefficient
                    self.analytics['clustering_coefficient'] = nx.average_clustering(creator_subgraph)
                    
                    # Largest component size
                    components = list(nx.connected_components(creator_subgraph.to_undirected()))
                    self.analytics['largest_component_size'] = len(max(components, key=len)) if components else 0
            
            self.last_analysis_update = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
    
    async def get_graph_analytics(self) -> Dict[str, Any]:
        """Get comprehensive graph analytics"""
        try:
            # Update analytics if needed
            if datetime.now() - self.last_analysis_update > self.update_frequency:
                await self._update_analytics()
            
            return {
                **self.analytics,
                'cache_sizes': {
                    'influence_cache': len(self.influence_cache),
                    'community_cache': len(self.community_cache),
                    'path_cache': len(self.path_cache)
                },
                'last_update': self.last_analysis_update.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting graph analytics: {e}")
            return self.analytics
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the graph engine"""
        health = {
            'status': 'healthy' if self.is_initialized else 'not_initialized',
            'graph_available': GRAPH_AVAILABLE,
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'creator_nodes': len([n for n in self.nodes.values() if n.node_type == NodeType.CREATOR]),
            'has_graph_structure': hasattr(self.creator_graph, 'nodes'),
            'cache_active': len(self.influence_cache) > 0
        }
        
        return health


# Export main classes
__all__ = [
    'GraphRelationshipEngine',
    'RelationshipType',
    'NodeType',
    'GraphNode',
    'GraphEdge',
    'InfluenceScore',
    'CommunityCluster',
    'PathAnalysis'
]