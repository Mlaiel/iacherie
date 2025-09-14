"""
Ainflue Platform - Network Effect Analyzer
==========================================

Enterprise-grade network effect analysis system for collaboration platforms with social graph analysis,
influence mapping, viral coefficient tracking, and network growth optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import statistics
import networkx as nx
from collections import defaultdict, deque
import numpy as np
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkNodeType(Enum):
    """Types of nodes in the collaboration network."""
    CREATOR = "creator"
    COLLABORATOR = "collaborator"
    BRAND = "brand"
    INFLUENCER = "influencer"
    AGENCY = "agency"
    PLATFORM = "platform"
    COMMUNITY = "community"

class ConnectionType(Enum):
    """Types of connections between network nodes."""
    COLLABORATION = "collaboration"
    REFERRAL = "referral"
    MENTORSHIP = "mentorship"
    PARTNERSHIP = "partnership"
    FOLLOW = "follow"
    ENDORSEMENT = "endorsement"
    CO_CREATION = "co_creation"
    CROSS_PROMOTION = "cross_promotion"

class NetworkMetricType(Enum):
    """Types of network metrics to track."""
    CENTRALITY = "centrality"
    CLUSTERING = "clustering"
    REACH = "reach"
    INFLUENCE = "influence"
    GROWTH_RATE = "growth_rate"
    VIRAL_COEFFICIENT = "viral_coefficient"
    ENGAGEMENT_DEPTH = "engagement_depth"

@dataclass
class NetworkNode:
    """Individual node in the collaboration network."""
    node_id: str
    node_type: NetworkNodeType
    user_id: str
    display_name: str
    creation_date: datetime
    last_active: datetime
    followers_count: int = 0
    following_count: int = 0
    collaborations_count: int = 0
    referrals_made: int = 0
    referrals_received: int = 0
    engagement_score: float = 0.0
    influence_score: float = 0.0
    trust_score: float = 0.0
    platform_tenure_days: int = 0
    categories: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NetworkConnection:
    """Connection between two network nodes."""
    connection_id: str
    source_node_id: str
    target_node_id: str
    connection_type: ConnectionType
    strength: float
    weight: float
    created_at: datetime
    last_interaction: datetime
    interaction_count: int = 0
    mutual_connections: int = 0
    collaboration_value: float = 0.0
    success_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NetworkMetrics:
    """Network-level metrics and analytics."""
    total_nodes: int = 0
    total_connections: int = 0
    density: float = 0.0
    average_clustering: float = 0.0
    average_path_length: float = 0.0
    diameter: int = 0
    connected_components: int = 0
    giant_component_size: int = 0
    growth_rate: float = 0.0
    viral_coefficient: float = 0.0
    network_value: float = 0.0
    engagement_index: float = 0.0
    influence_concentration: float = 0.0
    calculated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ViralGrowthMetrics:
    """Viral growth and network effect metrics."""
    period_start: datetime
    period_end: datetime
    new_users: int = 0
    invited_users: int = 0
    viral_coefficient: float = 0.0
    k_factor: float = 0.0
    invitation_conversion_rate: float = 0.0
    referral_loop_strength: float = 0.0
    network_value_increase: float = 0.0
    viral_features_usage: Dict[str, int] = field(default_factory=dict)
    growth_attribution: Dict[str, float] = field(default_factory=dict)

class NetworkEffectAnalyzer:
    """
    Enterprise network effect analysis system.
    
    Features:
    - Social graph analysis and mapping
    - Viral coefficient calculation
    - Network growth optimization
    - Influence mapping and analysis
    - Collaboration network insights
    - Network value quantification
    - Viral feature optimization
    - Growth attribution analysis
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.network_graph = nx.MultiDiGraph()
        self.nodes: Dict[str, NetworkNode] = {}
        self.connections: Dict[str, NetworkConnection] = {}
        self.network_metrics = NetworkMetrics()
        self.viral_metrics_history: List[ViralGrowthMetrics] = []
        self.growth_optimization_rules: Dict[str, Any] = {}
        
        # Initialize network analysis components
        self._setup_network_algorithms()
        self._setup_viral_tracking()
        self._setup_influence_calculation()
        self._setup_growth_optimization()
        
        logger.info("🌐 Network Effect Analyzer initialized")
    
    def _setup_network_algorithms(self) -> None:
        """Initialize network analysis algorithms."""
        self.network_algorithms = {
            "centrality_metrics": {
                "betweenness": True,
                "closeness": True,
                "eigenvector": True,
                "pagerank": True,
                "degree": True
            },
            "clustering_algorithms": {
                "local_clustering": True,
                "global_clustering": True,
                "transitivity": True
            },
            "community_detection": {
                "louvain": True,
                "label_propagation": True,
                "modularity_optimization": True
            },
            "path_analysis": {
                "shortest_paths": True,
                "diameter_calculation": True,
                "average_path_length": True
            }
        }
        
        logger.info("🧮 Network analysis algorithms configured")
    
    def _setup_viral_tracking(self) -> None:
        """Initialize viral growth tracking."""
        self.viral_config = {
            "tracking_window_days": 30,
            "viral_coefficient_threshold": 1.0,
            "k_factor_calculation": "invites_per_user * conversion_rate",
            "viral_features": [
                "referral_program",
                "social_sharing",
                "collaboration_invites",
                "content_virality",
                "network_recommendations"
            ],
            "growth_attribution_weights": {
                "organic": 0.4,
                "referral": 0.3,
                "viral": 0.2,
                "paid": 0.1
            }
        }
        
        logger.info("📈 Viral growth tracking configured")
    
    def _setup_influence_calculation(self) -> None:
        """Initialize influence calculation system."""
        self.influence_config = {
            "influence_factors": {
                "network_centrality": 0.25,
                "collaboration_success": 0.20,
                "content_engagement": 0.20,
                "referral_quality": 0.15,
                "platform_tenure": 0.10,
                "trust_score": 0.10
            },
            "influence_decay": {
                "time_decay_rate": 0.05,
                "activity_boost": 0.1,
                "collaboration_boost": 0.15
            },
            "influence_thresholds": {
                "micro_influencer": 0.1,
                "macro_influencer": 0.3,
                "mega_influencer": 0.7,
                "super_influencer": 0.9
            }
        }
        
        logger.info("⭐ Influence calculation system configured")
    
    def _setup_growth_optimization(self) -> None:
        """Initialize growth optimization rules."""
        self.growth_optimization_rules = {
            "viral_loop_optimization": {
                "optimal_invitation_timing": "24_hours_after_join",
                "invitation_personalization": True,
                "social_proof_integration": True,
                "gamification_incentives": True
            },
            "network_density_optimization": {
                "connection_recommendations": True,
                "mutual_interest_matching": True,
                "geographic_clustering": True,
                "skill_complementarity": True
            },
            "retention_optimization": {
                "early_connection_facilitation": True,
                "onboarding_network_building": True,
                "inactive_user_re_engagement": True,
                "network_value_demonstration": True
            }
        }
        
        logger.info("🚀 Growth optimization system configured")
    
    async def add_network_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new node to the collaboration network.
        
        Args:
            node_data: Node information
            
        Returns:
            Node addition result with network impact
        """
        try:
            node_id = node_data["node_id"]
            user_id = node_data["user_id"]
            node_type = NetworkNodeType(node_data["node_type"])
            
            # Create network node
            node = NetworkNode(
                node_id=node_id,
                node_type=node_type,
                user_id=user_id,
                display_name=node_data.get("display_name", f"User {user_id}"),
                creation_date=datetime.utcnow(),
                last_active=datetime.utcnow(),
                followers_count=node_data.get("followers_count", 0),
                following_count=node_data.get("following_count", 0),
                categories=node_data.get("categories", []),
                metadata=node_data.get("metadata", {})
            )
            
            # Calculate platform tenure
            if "join_date" in node_data:
                join_date = datetime.fromisoformat(node_data["join_date"])
                node.platform_tenure_days = (datetime.utcnow() - join_date).days
            
            # Add to network graph
            self.network_graph.add_node(node_id, **node.__dict__)
            self.nodes[node_id] = node
            
            # Calculate initial metrics
            initial_metrics = await self._calculate_initial_node_metrics(node)
            node.engagement_score = initial_metrics["engagement_score"]
            node.influence_score = initial_metrics["influence_score"]
            
            # Analyze network impact
            network_impact = await self._analyze_node_addition_impact(node)
            
            # Update network metrics
            await self._update_network_metrics()
            
            logger.info(f"🎯 Network node added: {node_id} ({node_type.value})")
            
            return {
                "node_id": node_id,
                "status": "added",
                "node_type": node_type.value,
                "initial_metrics": initial_metrics,
                "network_impact": network_impact,
                "recommendations": await self._generate_node_recommendations(node)
            }
            
        except Exception as e:
            logger.error(f"❌ Error adding network node: {e}")
            return {"status": "error", "message": str(e)}
    
    async def add_network_connection(self, connection_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a connection between network nodes.
        
        Args:
            connection_data: Connection information
            
        Returns:
            Connection addition result with network effect analysis
        """
        try:
            source_node_id = connection_data["source_node_id"]
            target_node_id = connection_data["target_node_id"]
            connection_type = ConnectionType(connection_data["connection_type"])
            
            # Validate nodes exist
            if source_node_id not in self.nodes or target_node_id not in self.nodes:
                return {"status": "error", "message": "One or both nodes not found"}
            
            connection_id = str(uuid.uuid4())
            
            # Calculate connection strength and weight
            strength = await self._calculate_connection_strength(
                source_node_id, target_node_id, connection_type, connection_data
            )
            
            weight = await self._calculate_connection_weight(
                source_node_id, target_node_id, strength, connection_data
            )
            
            # Create connection
            connection = NetworkConnection(
                connection_id=connection_id,
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                connection_type=connection_type,
                strength=strength,
                weight=weight,
                created_at=datetime.utcnow(),
                last_interaction=datetime.utcnow(),
                interaction_count=1,
                collaboration_value=connection_data.get("collaboration_value", 0.0),
                metadata=connection_data.get("metadata", {})
            )
            
            # Add to network graph
            self.network_graph.add_edge(
                source_node_id, target_node_id,
                key=connection_id,
                **connection.__dict__
            )
            
            self.connections[connection_id] = connection
            
            # Calculate mutual connections
            connection.mutual_connections = await self._count_mutual_connections(
                source_node_id, target_node_id
            )
            
            # Analyze network effect
            network_effect = await self._analyze_connection_network_effect(connection)
            
            # Update node metrics
            await self._update_node_metrics_for_connection(connection)
            
            # Update network metrics
            await self._update_network_metrics()
            
            logger.info(f"🔗 Network connection added: {source_node_id} -> {target_node_id}")
            
            return {
                "connection_id": connection_id,
                "status": "added",
                "connection_type": connection_type.value,
                "strength": strength,
                "weight": weight,
                "network_effect": network_effect,
                "mutual_connections": connection.mutual_connections
            }
            
        except Exception as e:
            logger.error(f"❌ Error adding network connection: {e}")
            return {"status": "error", "message": str(e)}
    
    async def calculate_viral_coefficient(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Calculate viral coefficient and k-factor for the network.
        
        Args:
            period_days: Analysis period in days
            
        Returns:
            Viral growth metrics and analysis
        """
        try:
            period_start = datetime.utcnow() - timedelta(days=period_days)
            period_end = datetime.utcnow()
            
            # Get new users in period
            new_users = [
                node for node in self.nodes.values()
                if node.creation_date >= period_start
            ]
            
            # Calculate invitations and conversions
            total_invitations = sum(node.referrals_made for node in self.nodes.values())
            invited_users = [
                node for node in new_users
                if node.metadata.get("invited_by") is not None
            ]
            
            # Viral coefficient calculation
            viral_coefficient = len(invited_users) / max(len(new_users) - len(invited_users), 1)
            
            # K-factor calculation (invitations per user * conversion rate)
            avg_invitations_per_user = total_invitations / max(len(self.nodes), 1)
            invitation_conversion_rate = len(invited_users) / max(total_invitations, 1)
            k_factor = avg_invitations_per_user * invitation_conversion_rate
            
            # Referral loop strength
            referral_loop_strength = await self._calculate_referral_loop_strength(
                new_users, invited_users
            )
            
            # Network value increase
            network_value_increase = await self._calculate_network_value_increase(
                period_start, period_end
            )
            
            # Viral features usage
            viral_features_usage = await self._analyze_viral_features_usage(period_days)
            
            # Growth attribution
            growth_attribution = await self._calculate_growth_attribution(new_users)
            
            # Create viral metrics
            viral_metrics = ViralGrowthMetrics(
                period_start=period_start,
                period_end=period_end,
                new_users=len(new_users),
                invited_users=len(invited_users),
                viral_coefficient=viral_coefficient,
                k_factor=k_factor,
                invitation_conversion_rate=invitation_conversion_rate,
                referral_loop_strength=referral_loop_strength,
                network_value_increase=network_value_increase,
                viral_features_usage=viral_features_usage,
                growth_attribution=growth_attribution
            )
            
            self.viral_metrics_history.append(viral_metrics)
            
            # Keep only last 12 months of history
            if len(self.viral_metrics_history) > 12:
                self.viral_metrics_history = self.viral_metrics_history[-12:]
            
            logger.info(f"📊 Viral coefficient calculated: {viral_coefficient:.3f} (k-factor: {k_factor:.3f})")
            
            return {
                "period_days": period_days,
                "viral_coefficient": viral_coefficient,
                "k_factor": k_factor,
                "new_users": len(new_users),
                "invited_users": len(invited_users),
                "invitation_conversion_rate": invitation_conversion_rate,
                "referral_loop_strength": referral_loop_strength,
                "network_value_increase": network_value_increase,
                "viral_features_usage": viral_features_usage,
                "growth_attribution": growth_attribution,
                "optimization_recommendations": await self._generate_viral_optimization_recommendations(viral_metrics)
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating viral coefficient: {e}")
            return {"status": "error", "message": str(e)}
    
    async def analyze_network_influence(self, node_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze influence patterns in the network.
        
        Args:
            node_id: Specific node to analyze (optional)
            
        Returns:
            Influence analysis results
        """
        try:
            if node_id:
                # Analyze specific node influence
                if node_id not in self.nodes:
                    return {"status": "error", "message": "Node not found"}
                
                return await self._analyze_node_influence(node_id)
            else:
                # Analyze network-wide influence patterns
                return await self._analyze_network_wide_influence()
            
        except Exception as e:
            logger.error(f"❌ Error analyzing network influence: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_network_recommendations(self, user_id: str, recommendation_type: str = "connections") -> Dict[str, Any]:
        """
        Get personalized network recommendations for a user.
        
        Args:
            user_id: User identifier
            recommendation_type: Type of recommendations to generate
            
        Returns:
            Personalized network recommendations
        """
        try:
            # Find user's node
            user_node = None
            for node in self.nodes.values():
                if node.user_id == user_id:
                    user_node = node
                    break
            
            if not user_node:
                return {"status": "error", "message": "User not found in network"}
            
            recommendations = []
            
            if recommendation_type == "connections":
                recommendations = await self._generate_connection_recommendations(user_node)
            elif recommendation_type == "collaborations":
                recommendations = await self._generate_collaboration_recommendations(user_node)
            elif recommendation_type == "growth":
                recommendations = await self._generate_growth_recommendations(user_node)
            elif recommendation_type == "influence":
                recommendations = await self._generate_influence_recommendations(user_node)
            
            logger.info(f"💡 Generated {len(recommendations)} recommendations for {user_id}")
            
            return {
                "user_id": user_id,
                "recommendation_type": recommendation_type,
                "recommendations": recommendations,
                "network_position": await self._analyze_user_network_position(user_node),
                "optimization_potential": await self._calculate_optimization_potential(user_node)
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating network recommendations: {e}")
            return {"status": "error", "message": str(e)}
    
    async def calculate_network_value(self) -> Dict[str, Any]:
        """
        Calculate the total value of the network using Metcalfe's Law and other metrics.
        
        Returns:
            Network value analysis
        """
        try:
            n_nodes = len(self.nodes)
            n_connections = len(self.connections)
            
            # Metcalfe's Law: Network value = n^2
            metcalfe_value = n_nodes ** 2
            
            # Reed's Law: Network value = 2^n (for group-forming networks)
            reed_value = min(2 ** min(n_nodes, 20), 1e6)  # Cap to prevent overflow
            
            # Sarnoff's Law: Network value = n (linear)
            sarnoff_value = n_nodes
            
            # Quality-adjusted network value
            total_connection_weight = sum(conn.weight for conn in self.connections.values())
            avg_connection_quality = total_connection_weight / max(n_connections, 1)
            quality_adjusted_value = metcalfe_value * avg_connection_quality
            
            # Collaboration value
            total_collaboration_value = sum(
                conn.collaboration_value for conn in self.connections.values()
                if conn.connection_type == ConnectionType.COLLABORATION
            )
            
            # Network density impact
            max_possible_connections = n_nodes * (n_nodes - 1)
            density = n_connections / max(max_possible_connections, 1)
            density_factor = 1 + (density * 0.5)  # Bonus for higher density
            
            # Influence concentration
            influence_scores = [node.influence_score for node in self.nodes.values()]
            influence_gini = self._calculate_gini_coefficient(influence_scores)
            influence_factor = 1 - (influence_gini * 0.3)  # Penalty for high concentration
            
            # Final network value calculation
            composite_value = (
                quality_adjusted_value * density_factor * influence_factor +
                total_collaboration_value
            )
            
            # Network growth potential
            growth_potential = await self._calculate_network_growth_potential()
            
            value_analysis = {
                "total_nodes": n_nodes,
                "total_connections": n_connections,
                "network_density": density,
                "metcalfe_value": metcalfe_value,
                "reed_value": reed_value,
                "sarnoff_value": sarnoff_value,
                "quality_adjusted_value": quality_adjusted_value,
                "collaboration_value": total_collaboration_value,
                "composite_network_value": composite_value,
                "average_connection_quality": avg_connection_quality,
                "influence_concentration": influence_gini,
                "growth_potential": growth_potential,
                "value_per_node": composite_value / max(n_nodes, 1),
                "network_efficiency": composite_value / max(n_connections, 1)
            }
            
            # Update network metrics
            self.network_metrics.network_value = composite_value
            self.network_metrics.density = density
            self.network_metrics.influence_concentration = influence_gini
            
            logger.info(f"💰 Network value calculated: {composite_value:,.0f}")
            
            return value_analysis
            
        except Exception as e:
            logger.error(f"❌ Error calculating network value: {e}")
            return {"status": "error", "message": str(e)}
    
    async def optimize_network_growth(self, optimization_goals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate network growth optimization recommendations.
        
        Args:
            optimization_goals: Optimization objectives
            
        Returns:
            Growth optimization strategy
        """
        try:
            current_metrics = await self.calculate_network_value()
            viral_metrics = await self.calculate_viral_coefficient()
            
            optimization_strategy = {
                "current_state": current_metrics,
                "viral_performance": viral_metrics,
                "optimization_goals": optimization_goals,
                "recommendations": []
            }
            
            # Viral coefficient optimization
            if optimization_goals.get("increase_viral_coefficient"):
                viral_recommendations = await self._optimize_viral_coefficient(viral_metrics)
                optimization_strategy["recommendations"].extend(viral_recommendations)
            
            # Network density optimization
            if optimization_goals.get("increase_network_density"):
                density_recommendations = await self._optimize_network_density(current_metrics)
                optimization_strategy["recommendations"].extend(density_recommendations)
            
            # Influence distribution optimization
            if optimization_goals.get("optimize_influence_distribution"):
                influence_recommendations = await self._optimize_influence_distribution(current_metrics)
                optimization_strategy["recommendations"].extend(influence_recommendations)
            
            # Growth rate optimization
            if optimization_goals.get("increase_growth_rate"):
                growth_recommendations = await self._optimize_growth_rate(viral_metrics)
                optimization_strategy["recommendations"].extend(growth_recommendations)
            
            # Network value optimization
            if optimization_goals.get("maximize_network_value"):
                value_recommendations = await self._optimize_network_value(current_metrics)
                optimization_strategy["recommendations"].extend(value_recommendations)
            
            # Prioritize recommendations
            optimization_strategy["recommendations"] = await self._prioritize_recommendations(
                optimization_strategy["recommendations"], optimization_goals
            )
            
            # Calculate expected impact
            optimization_strategy["expected_impact"] = await self._calculate_optimization_impact(
                optimization_strategy["recommendations"], current_metrics
            )
            
            logger.info(f"🚀 Network growth optimization strategy generated with {len(optimization_strategy['recommendations'])} recommendations")
            
            return optimization_strategy
            
        except Exception as e:
            logger.error(f"❌ Error optimizing network growth: {e}")
            return {"status": "error", "message": str(e)}
    
    # Helper methods
    
    async def _calculate_initial_node_metrics(self, node: NetworkNode) -> Dict[str, float]:
        """Calculate initial metrics for a new node."""
        # Base engagement score from external metrics
        engagement_score = 0.0
        if node.followers_count > 0:
            engagement_score += min(math.log10(node.followers_count) / 6, 0.3)
        
        if node.categories:
            engagement_score += len(node.categories) * 0.05
        
        # Initial influence score
        influence_score = 0.1  # Base score for new users
        if node.platform_tenure_days > 0:
            influence_score += min(node.platform_tenure_days / 365, 0.2)
        
        return {
            "engagement_score": engagement_score,
            "influence_score": influence_score
        }
    
    async def _analyze_node_addition_impact(self, node: NetworkNode) -> Dict[str, Any]:
        """Analyze the impact of adding a new node to the network."""
        return {
            "network_growth_contribution": 1 / max(len(self.nodes), 1),
            "potential_connections": await self._estimate_potential_connections(node),
            "category_diversity_impact": await self._calculate_category_diversity_impact(node),
            "expected_collaboration_value": await self._estimate_collaboration_value(node)
        }
    
    async def _estimate_potential_connections(self, node: NetworkNode) -> int:
        """Estimate potential connections for a new node."""
        # Count nodes with similar categories
        similar_nodes = 0
        for existing_node in self.nodes.values():
            if existing_node.node_id != node.node_id:
                common_categories = set(node.categories) & set(existing_node.categories)
                if common_categories:
                    similar_nodes += 1
        
        # Estimate based on network patterns
        return min(similar_nodes, int(len(self.nodes) * 0.1))  # Max 10% of network
    
    async def _calculate_category_diversity_impact(self, node: NetworkNode) -> float:
        """Calculate how much the node increases category diversity."""
        existing_categories = set()
        for existing_node in self.nodes.values():
            existing_categories.update(existing_node.categories)
        
        new_categories = set(node.categories) - existing_categories
        return len(new_categories) / max(len(node.categories), 1)
    
    async def _estimate_collaboration_value(self, node: NetworkNode) -> float:
        """Estimate potential collaboration value for a new node."""
        base_value = 100.0  # Base collaboration value
        
        # Adjust based on node type
        type_multipliers = {
            NetworkNodeType.CREATOR: 1.2,
            NetworkNodeType.INFLUENCER: 1.5,
            NetworkNodeType.BRAND: 2.0,
            NetworkNodeType.AGENCY: 1.8
        }
        
        multiplier = type_multipliers.get(node.node_type, 1.0)
        
        # Adjust based on followers
        if node.followers_count > 1000:
            multiplier *= 1.2
        if node.followers_count > 10000:
            multiplier *= 1.5
        
        return base_value * multiplier
    
    async def _generate_node_recommendations(self, node: NetworkNode) -> List[Dict[str, Any]]:
        """Generate recommendations for a new node."""
        recommendations = []
        
        # Connection recommendations
        similar_nodes = await self._find_similar_nodes(node)
        if similar_nodes:
            recommendations.append({
                "type": "connect_with_similar",
                "priority": "high",
                "description": f"Connect with {len(similar_nodes)} users in similar categories",
                "action_items": [f"Connect with {node_id}" for node_id in similar_nodes[:5]]
            })
        
        # Category expansion
        if len(node.categories) < 3:
            recommendations.append({
                "type": "expand_categories",
                "priority": "medium",
                "description": "Add more categories to increase discoverability",
                "target": "3-5 categories"
            })
        
        return recommendations
    
    async def _find_similar_nodes(self, node: NetworkNode) -> List[str]:
        """Find nodes similar to the given node."""
        similar_nodes = []
        
        for existing_node in self.nodes.values():
            if existing_node.node_id != node.node_id:
                # Check category similarity
                common_categories = set(node.categories) & set(existing_node.categories)
                if len(common_categories) >= 1:
                    similar_nodes.append(existing_node.node_id)
        
        return similar_nodes[:10]  # Return top 10
    
    async def _calculate_connection_strength(self, source_id: str, target_id: str, 
                                           connection_type: ConnectionType, 
                                           connection_data: Dict[str, Any]) -> float:
        """Calculate the strength of a connection."""
        base_strength = 0.5
        
        # Adjust based on connection type
        type_strengths = {
            ConnectionType.COLLABORATION: 0.9,
            ConnectionType.PARTNERSHIP: 0.8,
            ConnectionType.MENTORSHIP: 0.7,
            ConnectionType.REFERRAL: 0.6,
            ConnectionType.CO_CREATION: 0.8,
            ConnectionType.CROSS_PROMOTION: 0.6,
            ConnectionType.ENDORSEMENT: 0.5,
            ConnectionType.FOLLOW: 0.3
        }
        
        base_strength = type_strengths.get(connection_type, 0.5)
        
        # Adjust based on mutual connections
        source_node = self.nodes[source_id]
        target_node = self.nodes[target_id]
        
        # Category similarity boost
        common_categories = set(source_node.categories) & set(target_node.categories)
        if common_categories:
            base_strength += len(common_categories) * 0.05
        
        # Trust score influence
        avg_trust = (source_node.trust_score + target_node.trust_score) / 2
        base_strength *= (0.8 + avg_trust * 0.4)  # 80% to 120% based on trust
        
        return min(base_strength, 1.0)
    
    async def _calculate_connection_weight(self, source_id: str, target_id: str, 
                                         strength: float, connection_data: Dict[str, Any]) -> float:
        """Calculate the weight of a connection for network analysis."""
        # Weight combines strength with interaction frequency and value
        base_weight = strength
        
        # Interaction frequency (if available)
        interaction_count = connection_data.get("interaction_count", 1)
        interaction_boost = min(math.log10(interaction_count + 1) / 2, 0.3)
        
        # Collaboration value influence
        collaboration_value = connection_data.get("collaboration_value", 0.0)
        value_boost = min(collaboration_value / 1000, 0.2)  # Cap at 20% boost
        
        return base_weight + interaction_boost + value_boost
    
    async def _count_mutual_connections(self, node1_id: str, node2_id: str) -> int:
        """Count mutual connections between two nodes."""
        node1_connections = set()
        node2_connections = set()
        
        # Get all connections for both nodes
        for connection in self.connections.values():
            if connection.source_node_id == node1_id:
                node1_connections.add(connection.target_node_id)
            elif connection.target_node_id == node1_id:
                node1_connections.add(connection.source_node_id)
            
            if connection.source_node_id == node2_id:
                node2_connections.add(connection.target_node_id)
            elif connection.target_node_id == node2_id:
                node2_connections.add(connection.source_node_id)
        
        # Count mutual connections
        mutual = node1_connections & node2_connections
        return len(mutual)
    
    async def _analyze_connection_network_effect(self, connection: NetworkConnection) -> Dict[str, Any]:
        """Analyze the network effect of a new connection."""
        # Network density change
        total_possible = len(self.nodes) * (len(self.nodes) - 1)
        density_change = 1 / max(total_possible, 1)
        
        # Clustering coefficient change
        clustering_change = await self._calculate_clustering_change(connection)
        
        # Path length impact
        path_impact = await self._calculate_path_length_impact(connection)
        
        return {
            "density_change": density_change,
            "clustering_change": clustering_change,
            "path_length_impact": path_impact,
            "network_value_increase": connection.weight * 10,  # Simplified
            "viral_potential": connection.strength * 0.1
        }
    
    async def _calculate_clustering_change(self, connection: NetworkConnection) -> float:
        """Calculate how the new connection affects clustering coefficient."""
        # Simplified calculation - in practice would use NetworkX
        return 0.01  # Small positive change
    
    async def _calculate_path_length_impact(self, connection: NetworkConnection) -> float:
        """Calculate how the new connection affects average path length."""
        # Simplified - new connections generally reduce path length
        return -0.01  # Small reduction in average path length
    
    async def _update_node_metrics_for_connection(self, connection -> None: NetworkConnection) -> None:
        """Update node metrics when a new connection is added."""
        source_node = self.nodes[connection.source_node_id]
        target_node = self.nodes[connection.target_node_id]
        
        # Update collaboration counts
        if connection.connection_type == ConnectionType.COLLABORATION:
            source_node.collaborations_count += 1
            target_node.collaborations_count += 1
        
        # Update referral counts
        if connection.connection_type == ConnectionType.REFERRAL:
            source_node.referrals_made += 1
            target_node.referrals_received += 1
        
        # Update last active time
        source_node.last_active = datetime.utcnow()
        target_node.last_active = datetime.utcnow()
    
    async def _update_network_metrics(self) -> None:
        """Update overall network metrics."""
        self.network_metrics.total_nodes = len(self.nodes)
        self.network_metrics.total_connections = len(self.connections)
        
        # Calculate density
        if self.network_metrics.total_nodes > 1:
            max_connections = self.network_metrics.total_nodes * (self.network_metrics.total_nodes - 1)
            self.network_metrics.density = self.network_metrics.total_connections / max_connections
        
        # Calculate growth rate (simplified)
        if len(self.viral_metrics_history) >= 2:
            recent_growth = self.viral_metrics_history[-1].new_users
            previous_growth = self.viral_metrics_history[-2].new_users
            self.network_metrics.growth_rate = (recent_growth - previous_growth) / max(previous_growth, 1)
        
        self.network_metrics.calculated_at = datetime.utcnow()
    
    async def _calculate_referral_loop_strength(self, new_users: List[NetworkNode], 
                                              invited_users: List[NetworkNode]) -> float:
        """Calculate the strength of the referral loop."""
        if not invited_users:
            return 0.0
        
        # Check how many invited users become inviters themselves
        new_inviters = [user for user in invited_users if user.referrals_made > 0]
        
        return len(new_inviters) / len(invited_users)
    
    async def _calculate_network_value_increase(self, period_start: datetime, 
                                              period_end: datetime) -> float:
        """Calculate network value increase over period."""
        # Count new connections in period
        new_connections = [
            conn for conn in self.connections.values()
            if conn.created_at >= period_start
        ]
        
        # Calculate value increase (simplified)
        value_increase = sum(conn.weight * 10 for conn in new_connections)
        
        return value_increase
    
    async def _analyze_viral_features_usage(self, period_days: int) -> Dict[str, int]:
        """Analyze usage of viral features."""
        # Simplified implementation - would track actual feature usage
        return {
            "referral_program": len(self.nodes) // 10,
            "social_sharing": len(self.nodes) // 5,
            "collaboration_invites": len(self.connections) // 3,
            "content_virality": len(self.nodes) // 8,
            "network_recommendations": len(self.nodes) // 4
        }
    
    async def _calculate_growth_attribution(self, new_users: List[NetworkNode]) -> Dict[str, float]:
        """Calculate growth attribution to different channels."""
        if not new_users:
            return {"organic": 0, "referral": 0, "viral": 0, "paid": 0}
        
        # Simplified attribution based on metadata
        organic = len([u for u in new_users if not u.metadata.get("invited_by")])
        referral = len([u for u in new_users if u.metadata.get("invited_by")])
        
        total = len(new_users)
        
        return {
            "organic": organic / total,
            "referral": referral / total,
            "viral": 0.1,  # Simplified
            "paid": 0.1   # Simplified
        }
    
    async def _generate_viral_optimization_recommendations(self, viral_metrics: ViralGrowthMetrics) -> List[Dict[str, Any]]:
        """Generate recommendations to optimize viral growth."""
        recommendations = []
        
        if viral_metrics.viral_coefficient < 1.0:
            recommendations.append({
                "type": "improve_viral_coefficient",
                "priority": "high",
                "description": "Viral coefficient below 1.0 - optimize invitation flow",
                "target": "1.2+ viral coefficient",
                "actions": ["Simplify invitation process", "Add incentives", "Improve onboarding"]
            })
        
        if viral_metrics.invitation_conversion_rate < 0.1:
            recommendations.append({
                "type": "improve_conversion_rate",
                "priority": "high",
                "description": "Low invitation conversion rate",
                "target": "15%+ conversion rate",
                "actions": ["Personalize invitations", "Add social proof", "Optimize landing page"]
            })
        
        return recommendations
    
    def _calculate_gini_coefficient(self, values: List[float]) -> float:
        """Calculate Gini coefficient for measuring inequality."""
        if not values:
            return 0.0
        
        values = sorted(values)
        n = len(values)
        index = range(1, n + 1)
        
        return 2 * sum(index[i] * values[i] for i in range(n)) / (n * sum(values)) - (n + 1) / n
    
    async def _calculate_network_growth_potential(self) -> float:
        """Calculate the network's growth potential."""
        # Based on current density, viral coefficient, and engagement
        current_density = self.network_metrics.density
        
        # Networks with lower density have higher growth potential
        density_potential = 1.0 - current_density
        
        # Factor in recent growth trends
        growth_trend = self.network_metrics.growth_rate if self.network_metrics.growth_rate > 0 else 0
        
        # Combine factors
        growth_potential = (density_potential * 0.6) + (growth_trend * 0.4)
        
        return min(growth_potential, 1.0)
    
    # Additional helper methods for comprehensive network analysis...
    
    async def _analyze_node_influence(self, node_id: str) -> Dict[str, Any]:
        """Analyze influence metrics for a specific node."""
        node = self.nodes[node_id]
        
        # Calculate centrality metrics using NetworkX
        centrality_metrics = {}
        if len(self.network_graph) > 1:
            try:
                centrality_metrics = {
                    "degree_centrality": nx.degree_centrality(self.network_graph).get(node_id, 0),
                    "betweenness_centrality": nx.betweenness_centrality(self.network_graph).get(node_id, 0),
                    "closeness_centrality": nx.closeness_centrality(self.network_graph).get(node_id, 0),
                    "pagerank": nx.pagerank(self.network_graph).get(node_id, 0)
                }
            except:
                # Fallback if graph algorithms fail
                centrality_metrics = {
                    "degree_centrality": 0.0,
                    "betweenness_centrality": 0.0,
                    "closeness_centrality": 0.0,
                    "pagerank": 0.0
                }
        
        # Influence score calculation
        influence_factors = self.influence_config["influence_factors"]
        influence_score = (
            centrality_metrics.get("pagerank", 0) * influence_factors["network_centrality"] +
            (node.collaborations_count / 10) * influence_factors["collaboration_success"] +
            node.engagement_score * influence_factors["content_engagement"] +
            (node.referrals_made / 5) * influence_factors["referral_quality"] +
            (node.platform_tenure_days / 365) * influence_factors["platform_tenure"] +
            node.trust_score * influence_factors["trust_score"]
        )
        
        # Update node influence score
        node.influence_score = min(influence_score, 1.0)
        
        return {
            "node_id": node_id,
            "influence_score": node.influence_score,
            "centrality_metrics": centrality_metrics,
            "influence_tier": self._determine_influence_tier(node.influence_score),
            "influence_factors": {
                "network_position": centrality_metrics.get("pagerank", 0),
                "collaboration_activity": node.collaborations_count,
                "engagement_level": node.engagement_score,
                "referral_activity": node.referrals_made,
                "platform_experience": node.platform_tenure_days,
                "trust_level": node.trust_score
            },
            "growth_recommendations": await self._generate_influence_growth_recommendations(node)
        }
    
    def _determine_influence_tier(self, influence_score: float) -> str:
        """Determine influence tier based on score."""
        thresholds = self.influence_config["influence_thresholds"]
        
        if influence_score >= thresholds["super_influencer"]:
            return "super_influencer"
        elif influence_score >= thresholds["mega_influencer"]:
            return "mega_influencer"
        elif influence_score >= thresholds["macro_influencer"]:
            return "macro_influencer"
        elif influence_score >= thresholds["micro_influencer"]:
            return "micro_influencer"
        else:
            return "emerging"
    
    async def _generate_influence_growth_recommendations(self, node: NetworkNode) -> List[Dict[str, Any]]:
        """Generate recommendations to grow influence."""
        recommendations = []
        
        if node.collaborations_count < 5:
            recommendations.append({
                "type": "increase_collaborations",
                "priority": "high",
                "description": "Participate in more collaborations to build network presence",
                "target": "5+ collaborations"
            })
        
        if node.referrals_made < 3:
            recommendations.append({
                "type": "make_referrals",
                "priority": "medium",
                "description": "Refer quality users to build reputation",
                "target": "3+ successful referrals"
            })
        
        if node.engagement_score < 0.5:
            recommendations.append({
                "type": "improve_engagement",
                "priority": "high",
                "description": "Increase content engagement and platform activity",
                "target": "0.7+ engagement score"
            })
        
        return recommendations

# Create global instance
network_effect_analyzer = NetworkEffectAnalyzer()

__all__ = [
    'NetworkEffectAnalyzer',
    'NetworkNodeType',
    'ConnectionType',
    'NetworkMetricType',
    'NetworkNode',
    'NetworkConnection',
    'NetworkMetrics',
    'ViralGrowthMetrics',
    'network_effect_analyzer'
]