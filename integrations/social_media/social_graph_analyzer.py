"""Social Graph Analyzer - Social Media Network Analysis and Insights
===================================================================

Comprehensive social graph analysis system for understanding social media
connections, influence patterns, and content virality across platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import statistics
import networkx as nx
import numpy as np
from decimal import Decimal

import aioredis
import aiofiles

logger = logging.getLogger(__name__)


class SocialPlatform(Enum):
    """Social media platforms."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"
    DISCORD = "discord"
    REDDIT = "reddit"


class ConnectionType(Enum):
    """Types of social connections."""
    FOLLOWER = "follower"
    FOLLOWING = "following"
    MUTUAL = "mutual"
    SUBSCRIBER = "subscriber"
    FRIEND = "friend"
    COLLABORATOR = "collaborator"
    MENTION = "mention"
    SHARE = "share"
    COMMENT = "comment"
    LIKE = "like"
    REPOST = "repost"


class InfluenceLevel(Enum):
    """Influence levels."""
    NANO = "nano"          # 1K-10K followers
    MICRO = "micro"        # 10K-100K followers
    MACRO = "macro"        # 100K-1M followers
    MEGA = "mega"          # 1M+ followers
    CELEBRITY = "celebrity" # 10M+ followers


class ContentCategory(Enum):
    """Content categories."""
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    MUSIC = "music"
    GAMING = "gaming"
    LIFESTYLE = "lifestyle"
    TECHNOLOGY = "technology"
    FOOD = "food"
    TRAVEL = "travel"
    FITNESS = "fitness"
    FASHION = "fashion"
    BUSINESS = "business"
    NEWS = "news"
    COMEDY = "comedy"
    ART = "art"
    BEAUTY = "beauty"


@dataclass
class SocialNode:
    """Social media node (user/creator)."""
    node_id: str
    platform: SocialPlatform
    username: str
    display_name: str
    follower_count: int
    following_count: int
    content_count: int
    engagement_rate: float
    influence_level: InfluenceLevel
    content_categories: List[ContentCategory]
    verified: bool = False
    created_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SocialEdge:
    """Social media connection/edge."""
    source_id: str
    target_id: str
    connection_type: ConnectionType
    platform: SocialPlatform
    weight: float
    created_at: datetime
    last_interaction: Optional[datetime] = None
    interaction_count: int = 0
    strength_score: float = 0.0
    mutual: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentItem:
    """Social media content item."""
    content_id: str
    creator_id: str
    platform: SocialPlatform
    content_type: str
    title: Optional[str]
    description: Optional[str]
    url: str
    created_at: datetime
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    engagement_rate: float
    reach: int
    impressions: int
    categories: List[ContentCategory]
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    virality_score: float = 0.0
    sentiment_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InfluenceMetrics:
    """Influence metrics for a node."""
    centrality_betweenness: float
    centrality_closeness: float
    centrality_eigenvector: float
    centrality_degree: float
    pagerank_score: float
    authority_score: float
    hub_score: float
    clustering_coefficient: float
    local_influence: float
    global_influence: float
    reach_potential: int
    engagement_quality: float


@dataclass
class CommunityCluster:
    """Social community cluster."""
    cluster_id: str
    platform: SocialPlatform
    size: int
    density: float
    modularity: float
    primary_category: ContentCategory
    influence_level: InfluenceLevel
    members: List[str]
    key_influencers: List[str]
    content_themes: List[str]
    avg_engagement_rate: float
    total_reach: int
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ViralityPrediction:
    """Virality prediction for content."""
    content_id: str
    predicted_views: int
    predicted_engagement: float
    predicted_shares: int
    virality_probability: float
    peak_time_estimate: datetime
    factors: Dict[str, float]
    confidence_score: float
    recommendation: str


class SocialGraphAnalyzer:
    """Social graph analysis and insights system."""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self.redis_url = redis_url
        
        # Network graphs by platform
        self.graphs: Dict[SocialPlatform, nx.DiGraph] = {}
        self.nodes: Dict[str, SocialNode] = {}
        self.edges: Dict[str, SocialEdge] = {}
        self.content: Dict[str, ContentItem] = {}
        
        # Analysis cache
        self.influence_cache: Dict[str, InfluenceMetrics] = {}
        self.community_cache: Dict[str, List[CommunityCluster]] = {}
        self.virality_cache: Dict[str, ViralityPrediction] = {}
        
        # Analysis parameters
        self.cache_ttl = 3600  # 1 hour
        self.min_connection_weight = 0.1
        self.influence_decay_factor = 0.9
        
        # Initialize platform graphs
        for platform in SocialPlatform:
            self.graphs[platform] = nx.DiGraph()
    
    async def initialize(self) -> bool:
        """Initialize social graph analyzer."""
        try:
            if self.redis_url:
                self.redis_client = aioredis.from_url(self.redis_url)
                await self.redis_client.ping()
            
            logger.info("Social graph analyzer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize social graph analyzer: {str(e)}")
            return False
    
    async def add_node(self, node: SocialNode) -> bool:
        """Add a social media node to the graph."""
        try:
            # Store node
            self.nodes[node.node_id] = node
            
            # Add to platform graph
            graph = self.graphs[node.platform]
            graph.add_node(node.node_id, **asdict(node))
            
            # Cache in Redis
            if self.redis_client:
                await self.redis_client.setex(
                    f"social_node:{node.node_id}",
                    self.cache_ttl,
                    json.dumps(asdict(node), default=str)
                )
            
            logger.debug(f"Added social node: {node.username} on {node.platform.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add social node: {str(e)}")
            return False
    
    async def add_edge(self, edge: SocialEdge) -> bool:
        """Add a social media connection to the graph."""
        try:
            edge_key = f"{edge.source_id}_{edge.target_id}_{edge.platform.value}"
            self.edges[edge_key] = edge
            
            # Add to platform graph
            graph = self.graphs[edge.platform]
            graph.add_edge(
                edge.source_id,
                edge.target_id,
                weight=edge.weight,
                connection_type=edge.connection_type.value,
                **asdict(edge)
            )
            
            # Cache in Redis
            if self.redis_client:
                await self.redis_client.setex(
                    f"social_edge:{edge_key}",
                    self.cache_ttl,
                    json.dumps(asdict(edge), default=str)
                )
            
            logger.debug(f"Added social edge: {edge.source_id} -> {edge.target_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add social edge: {str(e)}")
            return False
    
    async def add_content(self, content: ContentItem) -> bool:
        """Add content item for analysis."""
        try:
            self.content[content.content_id] = content
            
            # Cache in Redis
            if self.redis_client:
                await self.redis_client.setex(
                    f"social_content:{content.content_id}",
                    self.cache_ttl,
                    json.dumps(asdict(content), default=str)
                )
            
            logger.debug(f"Added content item: {content.content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add content item: {str(e)}")
            return False
    
    async def calculate_influence_metrics(self, node_id: str, platform: SocialPlatform) -> InfluenceMetrics:
        """Calculate comprehensive influence metrics for a node."""
        try:
            cache_key = f"{node_id}_{platform.value}"
            
            # Check cache
            if cache_key in self.influence_cache:
                return self.influence_cache[cache_key]
            
            graph = self.graphs[platform]
            
            if node_id not in graph:
                raise ValueError(f"Node {node_id} not found in {platform.value} graph")
            
            # Calculate centrality measures
            centrality_betweenness = nx.betweenness_centrality(graph).get(node_id, 0.0)
            centrality_closeness = nx.closeness_centrality(graph).get(node_id, 0.0)
            
            try:
                centrality_eigenvector = nx.eigenvector_centrality(graph, max_iter=1000).get(node_id, 0.0)
            except:
                centrality_eigenvector = 0.0
            
            centrality_degree = nx.degree_centrality(graph).get(node_id, 0.0)
            
            # Calculate PageRank
            pagerank_scores = nx.pagerank(graph, alpha=0.85)
            pagerank_score = pagerank_scores.get(node_id, 0.0)
            
            # Calculate HITS scores
            try:
                hubs, authorities = nx.hits(graph, max_iter=1000)
                authority_score = authorities.get(node_id, 0.0)
                hub_score = hubs.get(node_id, 0.0)
            except:
                authority_score = 0.0
                hub_score = 0.0
            
            # Calculate clustering coefficient
            clustering_coefficient = nx.clustering(graph.to_undirected()).get(node_id, 0.0)
            
            # Calculate local and global influence
            local_influence = self._calculate_local_influence(node_id, graph)
            global_influence = self._calculate_global_influence(node_id, graph)
            
            # Calculate reach potential
            reach_potential = self._calculate_reach_potential(node_id, graph)
            
            # Calculate engagement quality
            engagement_quality = self._calculate_engagement_quality(node_id)
            
            metrics = InfluenceMetrics(
                centrality_betweenness=centrality_betweenness,
                centrality_closeness=centrality_closeness,
                centrality_eigenvector=centrality_eigenvector,
                centrality_degree=centrality_degree,
                pagerank_score=pagerank_score,
                authority_score=authority_score,
                hub_score=hub_score,
                clustering_coefficient=clustering_coefficient,
                local_influence=local_influence,
                global_influence=global_influence,
                reach_potential=reach_potential,
                engagement_quality=engagement_quality
            )
            
            # Cache metrics
            self.influence_cache[cache_key] = metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate influence metrics: {str(e)}")
            raise
    
    def _calculate_local_influence(self, node_id: str, graph: nx.DiGraph) -> float:
        """Calculate local influence based on immediate neighbors."""
        try:
            neighbors = list(graph.neighbors(node_id))
            if not neighbors:
                return 0.0
            
            # Weight by neighbor influence (follower counts)
            total_influence = 0.0
            for neighbor in neighbors:
                if neighbor in self.nodes:
                    neighbor_node = self.nodes[neighbor]
                    total_influence += neighbor_node.follower_count * neighbor_node.engagement_rate
            
            return min(total_influence / 1000000, 1.0)  # Normalize to 0-1
            
        except Exception:
            return 0.0
    
    def _calculate_global_influence(self, node_id: str, graph: nx.DiGraph) -> float:
        """Calculate global influence based on network position."""
        try:
            # Use combination of centrality measures
            betweenness = nx.betweenness_centrality(graph).get(node_id, 0.0)
            closeness = nx.closeness_centrality(graph).get(node_id, 0.0)
            
            # Weighted combination
            global_influence = (betweenness * 0.6) + (closeness * 0.4)
            
            return global_influence
            
        except Exception:
            return 0.0
    
    def _calculate_reach_potential(self, node_id: str, graph: nx.DiGraph) -> int:
        """Calculate potential reach through network."""
        try:
            # BFS to calculate 2-hop reach
            visited = set()
            queue = deque([(node_id, 0)])
            reach = 0
            
            while queue:
                current_node, depth = queue.popleft()
                
                if current_node in visited or depth > 2:
                    continue
                
                visited.add(current_node)
                
                if current_node in self.nodes:
                    reach += self.nodes[current_node].follower_count
                
                if depth < 2:
                    for neighbor in graph.neighbors(current_node):
                        if neighbor not in visited:
                            queue.append((neighbor, depth + 1))
            
            return reach
            
        except Exception:
            return 0
    
    def _calculate_engagement_quality(self, node_id: str) -> float:
        """Calculate engagement quality based on content performance."""
        try:
            if node_id not in self.nodes:
                return 0.0
            
            node = self.nodes[node_id]
            
            # Get creator's content
            creator_content = [c for c in self.content.values() if c.creator_id == node_id]
            
            if not creator_content:
                return node.engagement_rate
            
            # Calculate average engagement quality
            engagement_scores = []
            for content in creator_content:
                # Engagement quality based on multiple factors
                engagement_score = (
                    content.engagement_rate * 0.4 +
                    min(content.sentiment_score, 1.0) * 0.3 +
                    min(content.virality_score, 1.0) * 0.3
                )
                engagement_scores.append(engagement_score)
            
            return statistics.mean(engagement_scores)
            
        except Exception:
            return 0.0
    
    async def detect_communities(self, platform: SocialPlatform, 
                               min_size: int = 5) -> List[CommunityCluster]:
        """Detect communities in the social graph."""
        try:
            cache_key = f"communities_{platform.value}"
            
            # Check cache
            if cache_key in self.community_cache:
                return self.community_cache[cache_key]
            
            graph = self.graphs[platform]
            
            if len(graph) < min_size:
                return []
            
            # Convert to undirected for community detection
            undirected_graph = graph.to_undirected()
            
            # Use Louvain algorithm for community detection
            try:
                import community as community_louvain
                partition = community_louvain.best_partition(undirected_graph)
            except ImportError:
                # Fallback to simple connected components
                partition = {}
                for i, component in enumerate(nx.connected_components(undirected_graph)):
                    for node in component:
                        partition[node] = i
            
            # Group nodes by community
            communities = defaultdict(list)
            for node, community_id in partition.items():
                communities[community_id].append(node)
            
            # Create community clusters
            clusters = []
            for community_id, members in communities.items():
                if len(members) < min_size:
                    continue
                
                cluster = await self._create_community_cluster(
                    community_id, platform, members, undirected_graph
                )
                clusters.append(cluster)
            
            # Cache communities
            self.community_cache[cache_key] = clusters
            
            return clusters
            
        except Exception as e:
            logger.error(f"Failed to detect communities: {str(e)}")
            return []
    
    async def _create_community_cluster(self, community_id: int, platform: SocialPlatform,
                                      members: List[str], graph: nx.Graph) -> CommunityCluster:
        """Create community cluster from members."""
        try:
            # Calculate community metrics
            subgraph = graph.subgraph(members)
            density = nx.density(subgraph)
            
            # Determine primary category
            categories = []
            engagement_rates = []
            total_reach = 0
            key_influencers = []
            
            for member in members:
                if member in self.nodes:
                    node = self.nodes[member]
                    categories.extend(node.content_categories)
                    engagement_rates.append(node.engagement_rate)
                    total_reach += node.follower_count
                    
                    # Identify key influencers (top 20% by follower count)
                    if node.follower_count > 10000:  # Threshold for key influencer
                        key_influencers.append(member)
            
            # Find most common category
            if categories:
                category_counts = defaultdict(int)
                for cat in categories:
                    category_counts[cat] += 1
                primary_category = max(category_counts.items(), key=lambda x: x[1])[0]
            else:
                primary_category = ContentCategory.ENTERTAINMENT
            
            # Determine influence level
            avg_followers = total_reach / len(members) if members else 0
            if avg_followers >= 1000000:
                influence_level = InfluenceLevel.MEGA
            elif avg_followers >= 100000:
                influence_level = InfluenceLevel.MACRO
            elif avg_followers >= 10000:
                influence_level = InfluenceLevel.MICRO
            else:
                influence_level = InfluenceLevel.NANO
            
            cluster = CommunityCluster(
                cluster_id=f"{platform.value}_community_{community_id}",
                platform=platform,
                size=len(members),
                density=density,
                modularity=0.0,  # Would need full graph for true modularity
                primary_category=primary_category,
                influence_level=influence_level,
                members=members,
                key_influencers=key_influencers[:10],  # Top 10 key influencers
                content_themes=[],  # Would extract from content analysis
                avg_engagement_rate=statistics.mean(engagement_rates) if engagement_rates else 0.0,
                total_reach=total_reach
            )
            
            return cluster
            
        except Exception as e:
            logger.error(f"Failed to create community cluster: {str(e)}")
            raise
    
    async def predict_virality(self, content: ContentItem) -> ViralityPrediction:
        """Predict virality potential for content."""
        try:
            cache_key = f"virality_{content.content_id}"
            
            # Check cache
            if cache_key in self.virality_cache:
                return self.virality_cache[cache_key]
            
            # Get creator influence
            creator_metrics = await self.calculate_influence_metrics(
                content.creator_id, content.platform
            )
            
            # Calculate virality factors
            factors = {}
            
            # Creator influence factor (0-1)
            factors['creator_influence'] = min(creator_metrics.global_influence * 2, 1.0)
            
            # Engagement factor (0-1)
            factors['engagement_factor'] = min(content.engagement_rate * 2, 1.0)
            
            # Content freshness factor (0-1)
            hours_old = (datetime.utcnow() - content.created_at).total_seconds() / 3600
            factors['freshness_factor'] = max(0, 1 - (hours_old / 24))  # Decays over 24 hours
            
            # Platform-specific factor
            platform_multipliers = {
                SocialPlatform.TIKTOK: 1.5,
                SocialPlatform.YOUTUBE: 1.2,
                SocialPlatform.INSTAGRAM: 1.1,
                SocialPlatform.TWITTER: 1.0,
                SocialPlatform.FACEBOOK: 0.8
            }
            factors['platform_factor'] = platform_multipliers.get(content.platform, 1.0)
            
            # Hashtag popularity factor
            factors['hashtag_factor'] = min(len(content.hashtags) / 10, 1.0)
            
            # Time of posting factor (simplified)
            post_hour = content.created_at.hour
            if 18 <= post_hour <= 22:  # Peak engagement hours
                factors['timing_factor'] = 1.0
            elif 12 <= post_hour <= 17:
                factors['timing_factor'] = 0.8
            else:
                factors['timing_factor'] = 0.6
            
            # Calculate overall virality probability
            virality_probability = (
                factors['creator_influence'] * 0.25 +
                factors['engagement_factor'] * 0.20 +
                factors['freshness_factor'] * 0.15 +
                factors['platform_factor'] * 0.15 +
                factors['hashtag_factor'] * 0.10 +
                factors['timing_factor'] * 0.15
            )
            
            # Predict specific metrics
            base_reach = creator_metrics.reach_potential
            predicted_views = int(base_reach * virality_probability * factors['platform_factor'])
            predicted_engagement = content.engagement_rate * (1 + virality_probability)
            predicted_shares = int(predicted_views * predicted_engagement * 0.1)
            
            # Estimate peak time
            peak_time_estimate = content.created_at + timedelta(
                hours=6 if virality_probability > 0.7 else 12
            )
            
            # Generate recommendation
            if virality_probability > 0.8:
                recommendation = "High virality potential - boost promotion"
            elif virality_probability > 0.6:
                recommendation = "Good potential - consider targeted promotion"
            elif virality_probability > 0.4:
                recommendation = "Moderate potential - optimize for engagement"
            else:
                recommendation = "Low potential - focus on community building"
            
            prediction = ViralityPrediction(
                content_id=content.content_id,
                predicted_views=predicted_views,
                predicted_engagement=predicted_engagement,
                predicted_shares=predicted_shares,
                virality_probability=virality_probability,
                peak_time_estimate=peak_time_estimate,
                factors=factors,
                confidence_score=min(creator_metrics.authority_score + 0.5, 1.0),
                recommendation=recommendation
            )
            
            # Cache prediction
            self.virality_cache[cache_key] = prediction
            
            return prediction
            
        except Exception as e:
            logger.error(f"Failed to predict virality: {str(e)}")
            raise
    
    async def find_collaboration_opportunities(self, creator_id: str, 
                                             platform: SocialPlatform,
                                             max_recommendations: int = 10) -> List[Dict[str, Any]]:
        """Find collaboration opportunities for a creator."""
        try:
            if creator_id not in self.nodes:
                raise ValueError(f"Creator {creator_id} not found")
            
            creator = self.nodes[creator_id]
            creator_metrics = await self.calculate_influence_metrics(creator_id, platform)
            
            # Find potential collaborators
            recommendations = []
            
            # Analyze other creators in the same categories
            for node_id, node in self.nodes.items():
                if (node_id != creator_id and 
                    node.platform == platform and
                    any(cat in creator.content_categories for cat in node.content_categories)):
                    
                    # Calculate collaboration score
                    other_metrics = await self.calculate_influence_metrics(node_id, platform)
                    
                    # Score factors
                    category_overlap = len(set(creator.content_categories) & set(node.content_categories))
                    engagement_compatibility = 1 - abs(creator.engagement_rate - node.engagement_rate)
                    influence_balance = 1 - abs(creator_metrics.global_influence - other_metrics.global_influence)
                    
                    collaboration_score = (
                        category_overlap * 0.4 +
                        engagement_compatibility * 0.3 +
                        influence_balance * 0.3
                    )
                    
                    recommendations.append({
                        'creator_id': node_id,
                        'username': node.username,
                        'display_name': node.display_name,
                        'follower_count': node.follower_count,
                        'engagement_rate': node.engagement_rate,
                        'shared_categories': list(set(creator.content_categories) & set(node.content_categories)),
                        'collaboration_score': collaboration_score,
                        'potential_reach': creator.follower_count + node.follower_count,
                        'synergy_type': self._determine_synergy_type(creator, node)
                    })
            
            # Sort by collaboration score
            recommendations.sort(key=lambda x: x['collaboration_score'], reverse=True)
            
            return recommendations[:max_recommendations]
            
        except Exception as e:
            logger.error(f"Failed to find collaboration opportunities: {str(e)}")
            return []
    
    def _determine_synergy_type(self, creator1: SocialNode, creator2: SocialNode) -> str:
        """Determine the type of synergy between two creators."""
        # Similar audience size
        if abs(creator1.follower_count - creator2.follower_count) / max(creator1.follower_count, creator2.follower_count) < 0.3:
            return "peer_collaboration"
        # One significantly larger
        elif creator1.follower_count > creator2.follower_count * 2:
            return "mentorship_opportunity"
        elif creator2.follower_count > creator1.follower_count * 2:
            return "growth_opportunity"
        else:
            return "complementary_skills"
    
    async def analyze_trending_content(self, platform: SocialPlatform,
                                     time_window_hours: int = 24,
                                     min_engagement_threshold: float = 0.05) -> List[Dict[str, Any]]:
        """Analyze trending content on a platform."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            # Filter recent high-engagement content
            trending_content = []
            for content in self.content.values():
                if (content.platform == platform and 
                    content.created_at > cutoff_time and
                    content.engagement_rate > min_engagement_threshold):
                    
                    # Calculate trend score
                    hours_old = (datetime.utcnow() - content.created_at).total_seconds() / 3600
                    recency_factor = max(0, 1 - (hours_old / time_window_hours))
                    
                    trend_score = (
                        content.engagement_rate * 0.4 +
                        content.virality_score * 0.3 +
                        recency_factor * 0.3
                    )
                    
                    trending_content.append({
                        'content_id': content.content_id,
                        'creator_id': content.creator_id,
                        'title': content.title,
                        'engagement_rate': content.engagement_rate,
                        'view_count': content.view_count,
                        'trend_score': trend_score,
                        'categories': [cat.value for cat in content.categories],
                        'hashtags': content.hashtags,
                        'created_at': content.created_at.isoformat()
                    })
            
            # Sort by trend score
            trending_content.sort(key=lambda x: x['trend_score'], reverse=True)
            
            return trending_content
            
        except Exception as e:
            logger.error(f"Failed to analyze trending content: {str(e)}")
            return []
    
    async def get_network_statistics(self, platform: SocialPlatform) -> Dict[str, Any]:
        """Get comprehensive network statistics."""
        try:
            graph = self.graphs[platform]
            
            if len(graph) == 0:
                return {}
            
            # Basic statistics
            stats = {
                'node_count': graph.number_of_nodes(),
                'edge_count': graph.number_of_edges(),
                'density': nx.density(graph),
                'is_connected': nx.is_weakly_connected(graph),
                'average_clustering': nx.average_clustering(graph.to_undirected()),
                'platform': platform.value
            }
            
            # Degree statistics
            degrees = [d for n, d in graph.degree()]
            if degrees:
                stats['average_degree'] = statistics.mean(degrees)
                stats['max_degree'] = max(degrees)
                stats['min_degree'] = min(degrees)
            
            # Path statistics (for connected components)
            if nx.is_weakly_connected(graph):
                stats['average_shortest_path_length'] = nx.average_shortest_path_length(graph)
                stats['diameter'] = nx.diameter(graph.to_undirected())
            
            # Component analysis
            weak_components = list(nx.weakly_connected_components(graph))
            stats['weak_components'] = len(weak_components)
            stats['largest_component_size'] = max(len(comp) for comp in weak_components) if weak_components else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get network statistics: {str(e)}")
            return {}
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            # Clear caches
            self.influence_cache.clear()
            self.community_cache.clear()
            self.virality_cache.clear()
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Social graph analyzer cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Failed to cleanup social graph analyzer: {str(e)}")


# Example usage
async def main():
    """Example usage of social graph analyzer."""
    analyzer = SocialGraphAnalyzer()
    
    # Initialize
    if await analyzer.initialize():
        print("✅ Social graph analyzer initialized")
        
        # Add some sample nodes
        creator1 = SocialNode(
            node_id="creator_1",
            platform=SocialPlatform.YOUTUBE,
            username="techreviewguru",
            display_name="Tech Review Guru",
            follower_count=500000,
            following_count=1000,
            content_count=300,
            engagement_rate=0.08,
            influence_level=InfluenceLevel.MACRO,
            content_categories=[ContentCategory.TECHNOLOGY, ContentCategory.EDUCATION],
            verified=True
        )
        
        creator2 = SocialNode(
            node_id="creator_2",
            platform=SocialPlatform.YOUTUBE,
            username="musicproducer",
            display_name="Music Producer",
            follower_count=200000,
            following_count=500,
            content_count=150,
            engagement_rate=0.12,
            influence_level=InfluenceLevel.MACRO,
            content_categories=[ContentCategory.MUSIC, ContentCategory.ENTERTAINMENT],
            verified=False
        )
        
        await analyzer.add_node(creator1)
        await analyzer.add_node(creator2)
        
        # Add connection
        connection = SocialEdge(
            source_id="creator_1",
            target_id="creator_2",
            connection_type=ConnectionType.FOLLOWING,
            platform=SocialPlatform.YOUTUBE,
            weight=0.8,
            created_at=datetime.utcnow(),
            interaction_count=5,
            strength_score=0.7
        )
        
        await analyzer.add_edge(connection)
        
        # Calculate influence metrics
        metrics = await analyzer.calculate_influence_metrics("creator_1", SocialPlatform.YOUTUBE)
        print(f"📊 Influence metrics for creator_1:")
        print(f"   PageRank: {metrics.pagerank_score:.4f}")
        print(f"   Authority: {metrics.authority_score:.4f}")
        print(f"   Engagement Quality: {metrics.engagement_quality:.4f}")
        
        # Get network statistics
        stats = await analyzer.get_network_statistics(SocialPlatform.YOUTUBE)
        print(f"🌐 Network statistics:")
        print(f"   Nodes: {stats.get('node_count', 0)}")
        print(f"   Edges: {stats.get('edge_count', 0)}")
        print(f"   Density: {stats.get('density', 0):.4f}")


if __name__ == "__main__":
    asyncio.run(main())