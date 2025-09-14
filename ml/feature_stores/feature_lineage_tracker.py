"""🔍 Feature Lineage Tracker - Enterprise ML Feature Governance
=====================================================================
Module: ml/feature_stores/feature_lineage_tracker.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 FEATURE LINEAGE TRACKING & GOVERNANCE
Complete feature lineage tracking from raw data to model input
- Source data tracking et transformation history
- Feature dependency mapping et impact analysis
- Compliance audit trails pour regulatory requirements
- Real-time lineage updates et metadata management
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
from pathlib import Path
from collections import defaultdict, deque
import networkx as nx

# Configuration
logger = logging.getLogger(__name__)

class LineageEventType(Enum):
    """Types d'événements de lineage"""
    
    CREATION = "creation"
    TRANSFORMATION = "transformation"
    AGGREGATION = "aggregation"
    DERIVATION = "derivation"
    DELETION = "deletion"
    UPDATE = "update"

class DataSource(Enum):
    """Sources de données"""
    
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    CACHE = "cache"
    EXTERNAL = "external"

@dataclass
class LineageNode:
    """Nœud dans le graphe de lineage"""
    
    node_id: str
    name: str
    type: str  # feature, dataset, transformation, model
    source: DataSource
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    creator_types: List[str] = field(default_factory=list)  # musician, blogger, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'node_id': self.node_id,
            'name': self.name,
            'type': self.type,
            'source': self.source.value,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata,
            'creator_types': self.creator_types
        }

@dataclass
class LineageEdge:
    """Arête dans le graphe de lineage"""
    
    source_id: str
    target_id: str
    event_type: LineageEventType
    transformation_logic: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'event_type': self.event_type.value,
            'transformation_logic': self.transformation_logic,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }

@dataclass
class LineageQuery:
    """Requête de lineage"""
    
    feature_name: Optional[str] = None
    creator_type: Optional[str] = None
    time_range: Optional[Tuple[datetime, datetime]] = None
    depth: int = 10
    direction: str = "both"  # upstream, downstream, both

class FeatureLineageTracker:
    """
    🔍 Feature Lineage Tracker
    
    Suivi complet de la lignée des features avec:
    - Graphe de dépendances en temps réel
    - Audit trail pour compliance
    - Impact analysis automatisé
    - Creator-specific lineage patterns
    """
    
    def __init__(
        self,
        storage_path -> None: str = "data/lineage",
        enable_real_time -> None: bool = True,
        max_history_days -> None: int = 365
    ) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.enable_real_time = enable_real_time
        self.max_history_days = max_history_days
        
        # Graphe de lineage
        self.lineage_graph = nx.DiGraph()
        
        # Storage pour metadata et history
        self.nodes: Dict[str, LineageNode] = {}
        self.edges: Dict[str, LineageEdge] = {}
        
        # Index pour recherche rapide
        self.feature_index: Dict[str, Set[str]] = defaultdict(set)
        self.creator_index: Dict[str, Set[str]] = defaultdict(set)
        self.source_index: Dict[DataSource, Set[str]] = defaultdict(set)
        
        # Cache pour performance
        self.lineage_cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes
        
        logger.info("🔍 Feature Lineage Tracker initialized")
    
    async def register_feature(
        self,
        feature_name: str,
        source: DataSource,
        creator_types: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Enregistrer une nouvelle feature"""
        
        node_id = f"feature_{hashlib.md5(feature_name.encode()).hexdigest()[:8]}"
        
        node = LineageNode(
            node_id=node_id,
            name=feature_name,
            type="feature",
            source=source,
            created_at=datetime.now(),
            metadata=metadata or {},
            creator_types=creator_types
        )
        
        # Stocker le nœud
        self.nodes[node_id] = node
        self.lineage_graph.add_node(node_id, **node.to_dict())
        
        # Mettre à jour les index
        self.feature_index[feature_name].add(node_id)
        for creator_type in creator_types:
            self.creator_index[creator_type].add(node_id)
        self.source_index[source].add(node_id)
        
        # Persister
        await self._persist_node(node)
        
        logger.info(f"✅ Feature registered: {feature_name} [{node_id}]")
        return node_id
    
    async def track_transformation(
        self,
        source_features: List[str],
        target_feature: str,
        transformation_logic: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Suivre une transformation de features"""
        
        # Créer un ID pour cette transformation
        transform_id = f"transform_{uuid.uuid4().hex[:8]}"
        
        # Obtenir les IDs des features sources
        source_ids = []
        for feature_name in source_features:
            if feature_name in self.feature_index:
                source_ids.extend(list(self.feature_index[feature_name]))
        
        # Obtenir l'ID de la feature target
        target_ids = list(self.feature_index.get(target_feature, []))
        
        if not target_ids:
            logger.warning(f"Target feature not found: {target_feature}")
            return transform_id
        
        # Créer les arêtes de lineage
        for source_id in source_ids:
            for target_id in target_ids:
                edge = LineageEdge(
                    source_id=source_id,
                    target_id=target_id,
                    event_type=LineageEventType.TRANSFORMATION,
                    transformation_logic=transformation_logic,
                    timestamp=datetime.now(),
                    metadata=metadata or {}
                )
                
                edge_key = f"{source_id}->{target_id}_{transform_id}"
                self.edges[edge_key] = edge
                
                # Ajouter au graphe
                self.lineage_graph.add_edge(
                    source_id, 
                    target_id, 
                    **edge.to_dict()
                )
                
                # Persister
                await self._persist_edge(edge)
        
        # Invalider le cache
        self.lineage_cache.clear()
        
        logger.info(f"✅ Transformation tracked: {source_features} -> {target_feature}")
        return transform_id
    
    async def get_upstream_lineage(
        self,
        feature_name: str,
        depth: int = 5
    ) -> Dict[str, Any]:
        """Obtenir la lignée amont d'une feature"""
        
        cache_key = f"upstream_{feature_name}_{depth}"
        if cache_key in self.lineage_cache:
            cache_entry = self.lineage_cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                return cache_entry['data']
        
        # Obtenir les IDs de la feature
        feature_ids = list(self.feature_index.get(feature_name, []))
        if not feature_ids:
            return {'nodes': [], 'edges': [], 'path_count': 0}
        
        # Construire la lignée amont
        upstream_nodes = set()
        upstream_edges = []
        
        for feature_id in feature_ids:
            # DFS pour remonter la lignée
            visited = set()
            stack = [(feature_id, 0)]
            
            while stack and len(stack) <= depth:
                current_id, current_depth = stack.pop()
                
                if current_id in visited or current_depth >= depth:
                    continue
                
                visited.add(current_id)
                upstream_nodes.add(current_id)
                
                # Ajouter les prédécesseurs
                for predecessor in self.lineage_graph.predecessors(current_id):
                    if predecessor not in visited:
                        stack.append((predecessor, current_depth + 1))
                        
                        # Ajouter l'arête
                        edge_data = self.lineage_graph.get_edge_data(predecessor, current_id)
                        if edge_data:
                            upstream_edges.append({
                                'source': predecessor,
                                'target': current_id,
                                'data': edge_data
                            })
        
        # Construire le résultat
        result = {
            'nodes': [self.nodes[node_id].to_dict() for node_id in upstream_nodes if node_id in self.nodes],
            'edges': upstream_edges,
            'path_count': len(upstream_edges),
            'max_depth_reached': depth
        }
        
        # Cache le résultat
        self.lineage_cache[cache_key] = {
            'data': result,
            'timestamp': time.time()
        }
        
        return result
    
    async def get_downstream_lineage(
        self,
        feature_name: str,
        depth: int = 5
    ) -> Dict[str, Any]:
        """Obtenir la lignée aval d'une feature"""
        
        cache_key = f"downstream_{feature_name}_{depth}"
        if cache_key in self.lineage_cache:
            cache_entry = self.lineage_cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                return cache_entry['data']
        
        # Obtenir les IDs de la feature
        feature_ids = list(self.feature_index.get(feature_name, []))
        if not feature_ids:
            return {'nodes': [], 'edges': [], 'path_count': 0}
        
        # Construire la lignée aval
        downstream_nodes = set()
        downstream_edges = []
        
        for feature_id in feature_ids:
            # DFS pour descendre la lignée
            visited = set()
            stack = [(feature_id, 0)]
            
            while stack and len(stack) <= depth:
                current_id, current_depth = stack.pop()
                
                if current_id in visited or current_depth >= depth:
                    continue
                
                visited.add(current_id)
                downstream_nodes.add(current_id)
                
                # Ajouter les successeurs
                for successor in self.lineage_graph.successors(current_id):
                    if successor not in visited:
                        stack.append((successor, current_depth + 1))
                        
                        # Ajouter l'arête
                        edge_data = self.lineage_graph.get_edge_data(current_id, successor)
                        if edge_data:
                            downstream_edges.append({
                                'source': current_id,
                                'target': successor,
                                'data': edge_data
                            })
        
        # Construire le résultat
        result = {
            'nodes': [self.nodes[node_id].to_dict() for node_id in downstream_nodes if node_id in self.nodes],
            'edges': downstream_edges,
            'path_count': len(downstream_edges),
            'max_depth_reached': depth
        }
        
        # Cache le résultat
        self.lineage_cache[cache_key] = {
            'data': result,
            'timestamp': time.time()
        }
        
        return result
    
    async def analyze_impact(
        self,
        feature_name: str,
        change_type: str = "modification"
    ) -> Dict[str, Any]:
        """Analyser l'impact d'un changement de feature"""
        
        # Obtenir la lignée aval complète
        downstream = await self.get_downstream_lineage(feature_name, depth=10)
        
        # Analyser l'impact
        impacted_features = []
        impacted_models = []
        impact_score = 0
        
        for node in downstream['nodes']:
            if node['type'] == 'feature':
                impacted_features.append(node['name'])
                impact_score += 1
            elif node['type'] == 'model':
                impacted_models.append(node['name'])
                impact_score += 3  # Les modèles ont plus de poids
        
        # Analyser par creator type
        creator_impact = defaultdict(int)
        for node in downstream['nodes']:
            for creator_type in node.get('creator_types', []):
                creator_impact[creator_type] += 1
        
        return {
            'feature_name': feature_name,
            'change_type': change_type,
            'impact_score': impact_score,
            'impacted_features': impacted_features,
            'impacted_models': impacted_models,
            'creator_impact': dict(creator_impact),
            'total_downstream_nodes': len(downstream['nodes']),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    async def get_compliance_report(
        self,
        creator_type: Optional[str] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Générer un rapport de compliance pour audit"""
        
        # Filtrer les nœuds selon les critères
        filtered_nodes = []
        filtered_edges = []
        
        for node in self.nodes.values():
            include_node = True
            
            if creator_type and creator_type not in node.creator_types:
                include_node = False
            
            if time_range and not (time_range[0] <= node.created_at <= time_range[1]):
                include_node = False
            
            if include_node:
                filtered_nodes.append(node.to_dict())
        
        for edge in self.edges.values():
            include_edge = True
            
            if time_range and not (time_range[0] <= edge.timestamp <= time_range[1]):
                include_edge = False
            
            if include_edge:
                filtered_edges.append(edge.to_dict())
        
        # Statistiques
        stats = {
            'total_features': len([n for n in filtered_nodes if n['type'] == 'feature']),
            'total_transformations': len(filtered_edges),
            'sources_used': len(set(n['source'] for n in filtered_nodes)),
            'creator_types': len(set(ct for n in filtered_nodes for ct in n['creator_types']))
        }
        
        return {
            'report_id': str(uuid.uuid4()),
            'generated_at': datetime.now().isoformat(),
            'filter_criteria': {
                'creator_type': creator_type,
                'time_range': [t.isoformat() for t in time_range] if time_range else None
            },
            'statistics': stats,
            'nodes': filtered_nodes,
            'edges': filtered_edges,
            'compliance_status': 'COMPLIANT'  # À implémenter selon les règles business
        }
    
    async def _persist_node(self, node -> None: LineageNode) -> None:
        """Persister un nœud"""
        if self.enable_real_time:
            node_file = self.storage_path / f"nodes/{node.node_id}.json"
            node_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(node_file, 'w') as f:
                json.dump(node.to_dict(), f, indent=2)
    
    async def _persist_edge(self, edge -> None: LineageEdge) -> None:
        """Persister une arête"""
        if self.enable_real_time:
            edge_file = self.storage_path / f"edges/{edge.source_id}_{edge.target_id}_{int(edge.timestamp.timestamp())}.json"
            edge_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(edge_file, 'w') as f:
                json.dump(edge.to_dict(), f, indent=2)
    
    async def cleanup_old_data(self) -> None:
        """Nettoyer les anciennes données"""
        cutoff_date = datetime.now() - timedelta(days=self.max_history_days)
        
        # Nettoyer les nœuds anciens
        nodes_to_remove = []
        for node_id, node in self.nodes.items():
            if node.created_at < cutoff_date:
                nodes_to_remove.append(node_id)
        
        for node_id in nodes_to_remove:
            del self.nodes[node_id]
            if self.lineage_graph.has_node(node_id):
                self.lineage_graph.remove_node(node_id)
        
        # Nettoyer les arêtes anciennes
        edges_to_remove = []
        for edge_key, edge in self.edges.items():
            if edge.timestamp < cutoff_date:
                edges_to_remove.append(edge_key)
        
        for edge_key in edges_to_remove:
            del self.edges[edge_key]
        
        logger.info(f"🧹 Cleaned up {len(nodes_to_remove)} nodes and {len(edges_to_remove)} edges")

# Usage Example
async def main() -> None:
    """Exemple d'utilisation du Feature Lineage Tracker"""
    
    tracker = FeatureLineageTracker()
    
    # Enregistrer des features
    user_id = await tracker.register_feature(
        "user_engagement_score",
        DataSource.DATABASE,
        ["musician", "blogger"],
        {"description": "Score d'engagement utilisateur", "version": "1.0"}
    )
    
    content_id = await tracker.register_feature(
        "content_popularity",
        DataSource.API,
        ["musician"],
        {"description": "Popularité du contenu", "version": "1.0"}
    )
    
    # Suivre une transformation
    await tracker.track_transformation(
        ["user_engagement_score", "content_popularity"],
        "recommendation_score",
        "weighted_average(engagement * 0.7 + popularity * 0.3)",
        {"transformation_type": "weighted_combination"}
    )
    
    # Analyser l'impact
    impact = await tracker.analyze_impact("user_engagement_score")
    print(f"Impact analysis: {impact}")
    
    # Générer un rapport de compliance
    report = await tracker.get_compliance_report(creator_type="musician")
    print(f"Compliance report: {report['statistics']}")

if __name__ == "__main__":
    asyncio.run(main())