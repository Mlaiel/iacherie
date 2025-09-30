"""
🔍 Data Lineage Tracker - Traçabilité des Données Enterprise
© Fahed Mlaiel 2024-2025 - Ainflue Microservices Enterprise

Service de traçabilité complète des données avec graphe de lignage intelligent.
Suivi automatique des transformations et analyse d'impact pour gouvernance enterprise.
"""

import asyncio
from typing import Dict, List, Optional, Union, Any, Set
from datetime import datetime, timedelta
import logging
import json
from dataclasses import dataclass, field
from enum import Enum
import uuid

import networkx as nx
import pandas as pd
from sqlparse import parse as sql_parse
import graphviz

logger = logging.getLogger(__name__)


class LineageType(Enum):
    """Types de relations de lignage"""
    DERIVES_FROM = "derives_from"
    TRANSFORMS_TO = "transforms_to"
    JOINS_WITH = "joins_with"
    AGGREGATES = "aggregates"
    FILTERS = "filters"
    COPIES = "copies"
    REFERENCES = "references"


class NodeType(Enum):
    """Types de nœuds dans le graphe de lignage"""
    TABLE = "table"
    VIEW = "view"
    FILE = "file"
    COLUMN = "column"
    TRANSFORMATION = "transformation"
    REPORT = "report"
    MODEL = "model"
    API = "api"


@dataclass
class LineageNode:
    """Nœud dans le graphe de lignage"""
    node_id: str
    name: str
    node_type: NodeType
    source_system: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    owner: Optional[str] = None
    description: Optional[str] = None


@dataclass
class LineageEdge:
    """Arête dans le graphe de lignage"""
    edge_id: str
    source_node: str
    target_node: str
    lineage_type: LineageType
    transformation_logic: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    confidence_score: float = 1.0


@dataclass
class LineageQuery:
    """Requête de lignage"""
    node_id: str
    direction: str = "both"  # upstream, downstream, both
    depth: int = 5
    include_node_types: List[NodeType] = field(default_factory=list)
    exclude_node_types: List[NodeType] = field(default_factory=list)
    include_lineage_types: List[LineageType] = field(default_factory=list)
    time_range: Optional[Dict[str, datetime]] = None


@dataclass
class ImpactAnalysis:
    """Analyse d'impact"""
    target_node: str
    affected_nodes: List[str]
    impact_paths: List[List[str]]
    severity: str  # low, medium, high, critical
    estimated_effort: str
    recommendations: List[str]


class DataLineageTracker:
    """Service de traçabilité des données enterprise"""
    
    def __init__(self):
        self.lineage_graph = nx.DiGraph()
        self.nodes: Dict[str, LineageNode] = {}
        self.edges: Dict[str, LineageEdge] = {}
        
        # Configuration des analyseurs
        self.sql_parser = self._initialize_sql_parser()
        self.auto_discovery_enabled = True
        
        # Métriques et cache
        self.lineage_cache = {}
        self.cache_ttl = 600  # 10 minutes
        self.metrics = {
            'nodes_count': 0,
            'edges_count': 0,
            'last_update': datetime.utcnow()
        }
    
    async def register_node(self, node: LineageNode) -> Dict[str, Any]:
        """Enregistre un nœud dans le graphe de lignage"""
        
        try:
            # Ajouter au graphe NetworkX
            self.lineage_graph.add_node(
                node.node_id,
                **node.__dict__
            )
            
            # Stocker dans le dictionnaire local
            self.nodes[node.node_id] = node
            
            # Mettre à jour les métriques
            self.metrics['nodes_count'] = len(self.nodes)
            self.metrics['last_update'] = datetime.utcnow()
            
            logger.info(f"Lineage node {node.node_id} registered")
            
            return {
                'success': True,
                'node_id': node.node_id,
                'message': 'Node registered successfully'
            }
            
        except Exception as e:
            logger.error(f"Error registering lineage node {node.node_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def register_edge(self, edge: LineageEdge) -> Dict[str, Any]:
        """Enregistre une arête dans le graphe de lignage"""
        
        try:
            # Vérifier que les nœuds source et target existent
            if edge.source_node not in self.nodes:
                return {
                    'success': False,
                    'error': f'Source node {edge.source_node} not found'
                }
            
            if edge.target_node not in self.nodes:
                return {
                    'success': False,
                    'error': f'Target node {edge.target_node} not found'
                }
            
            # Ajouter au graphe NetworkX
            self.lineage_graph.add_edge(
                edge.source_node,
                edge.target_node,
                edge_id=edge.edge_id,
                lineage_type=edge.lineage_type.value,
                transformation_logic=edge.transformation_logic,
                metadata=edge.metadata,
                created_at=edge.created_at,
                created_by=edge.created_by,
                confidence_score=edge.confidence_score
            )
            
            # Stocker dans le dictionnaire local
            self.edges[edge.edge_id] = edge
            
            # Mettre à jour les métriques
            self.metrics['edges_count'] = len(self.edges)
            self.metrics['last_update'] = datetime.utcnow()
            
            # Invalider le cache
            self._invalidate_cache()
            
            logger.info(f"Lineage edge {edge.edge_id} registered")
            
            return {
                'success': True,
                'edge_id': edge.edge_id,
                'message': 'Edge registered successfully'
            }
            
        except Exception as e:
            logger.error(f"Error registering lineage edge {edge.edge_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def trace_lineage(self, query: LineageQuery) -> Dict[str, Any]:
        """Trace le lignage pour un nœud donné"""
        
        try:
            # Vérifier le cache
            cache_key = self._generate_lineage_cache_key(query)
            if cache_key in self.lineage_cache:
                cached_result = self.lineage_cache[cache_key]
                if self._is_cache_valid(cached_result):
                    return cached_result['result']
            
            # Vérifier que le nœud existe
            if query.node_id not in self.nodes:
                return {
                    'success': False,
                    'error': f'Node {query.node_id} not found'
                }
            
            # Tracer le lignage
            lineage_result = await self._perform_lineage_trace(query)
            
            # Enrichir avec des métadonnées
            enriched_result = await self._enrich_lineage_result(lineage_result, query)
            
            # Mettre en cache
            self._cache_lineage_result(cache_key, enriched_result)
            
            return enriched_result
            
        except Exception as e:
            logger.error(f"Error tracing lineage for {query.node_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _perform_lineage_trace(self, query: LineageQuery) -> Dict[str, Any]:
        """Effectue le traçage de lignage"""
        
        upstream_nodes = set()
        downstream_nodes = set()
        upstream_edges = []
        downstream_edges = []
        
        # Traçage upstream (sources)
        if query.direction in ['upstream', 'both']:
            upstream_nodes, upstream_edges = await self._trace_upstream(
                query.node_id, query.depth, query
            )
        
        # Traçage downstream (destinations)
        if query.direction in ['downstream', 'both']:
            downstream_nodes, downstream_edges = await self._trace_downstream(
                query.node_id, query.depth, query
            )
        
        # Combiner les résultats
        all_nodes = upstream_nodes | downstream_nodes | {query.node_id}
        all_edges = upstream_edges + downstream_edges
        
        # Filtrer selon les critères
        filtered_nodes = self._filter_nodes(all_nodes, query)
        filtered_edges = self._filter_edges(all_edges, query)
        
        return {
            'success': True,
            'root_node': query.node_id,
            'nodes': list(filtered_nodes),
            'edges': filtered_edges,
            'upstream_count': len(upstream_nodes),
            'downstream_count': len(downstream_nodes),
            'total_depth': max(len(upstream_nodes), len(downstream_nodes)),
            'traced_at': datetime.utcnow().isoformat()
        }
    
    async def _trace_upstream(
        self,
        node_id: str,
        max_depth: int,
        query: LineageQuery,
        current_depth: int = 0,
        visited: Optional[Set[str]] = None
    ) -> tuple[Set[str], List[Dict[str, Any]]]:
        """Trace les nœuds upstream (sources)"""
        
        if visited is None:
            visited = set()
        
        if current_depth >= max_depth or node_id in visited:
            return set(), []
        
        visited.add(node_id)
        nodes = set()
        edges = []
        
        # Obtenir les prédécesseurs directs
        predecessors = list(self.lineage_graph.predecessors(node_id))
        
        for pred in predecessors:
            # Ajouter le nœud prédécesseur
            nodes.add(pred)
            
            # Ajouter l'arête
            edge_data = self.lineage_graph.get_edge_data(pred, node_id)
            if edge_data:
                edges.append({
                    'source': pred,
                    'target': node_id,
                    'lineage_type': edge_data.get('lineage_type'),
                    'transformation_logic': edge_data.get('transformation_logic'),
                    'confidence_score': edge_data.get('confidence_score', 1.0)
                })
            
            # Récursion pour tracer plus profondément
            upstream_nodes, upstream_edges = await self._trace_upstream(
                pred, max_depth, query, current_depth + 1, visited.copy()
            )
            
            nodes.update(upstream_nodes)
            edges.extend(upstream_edges)
        
        return nodes, edges
    
    async def _trace_downstream(
        self,
        node_id: str,
        max_depth: int,
        query: LineageQuery,
        current_depth: int = 0,
        visited: Optional[Set[str]] = None
    ) -> tuple[Set[str], List[Dict[str, Any]]]:
        """Trace les nœuds downstream (destinations)"""
        
        if visited is None:
            visited = set()
        
        if current_depth >= max_depth or node_id in visited:
            return set(), []
        
        visited.add(node_id)
        nodes = set()
        edges = []
        
        # Obtenir les successeurs directs
        successors = list(self.lineage_graph.successors(node_id))
        
        for succ in successors:
            # Ajouter le nœud successeur
            nodes.add(succ)
            
            # Ajouter l'arête
            edge_data = self.lineage_graph.get_edge_data(node_id, succ)
            if edge_data:
                edges.append({
                    'source': node_id,
                    'target': succ,
                    'lineage_type': edge_data.get('lineage_type'),
                    'transformation_logic': edge_data.get('transformation_logic'),
                    'confidence_score': edge_data.get('confidence_score', 1.0)
                })
            
            # Récursion pour tracer plus profondément
            downstream_nodes, downstream_edges = await self._trace_downstream(
                succ, max_depth, query, current_depth + 1, visited.copy()
            )
            
            nodes.update(downstream_nodes)
            edges.extend(downstream_edges)
        
        return nodes, edges
    
    def _filter_nodes(self, nodes: Set[str], query: LineageQuery) -> Set[str]:
        """Filtre les nœuds selon les critères"""
        
        filtered_nodes = set()
        
        for node_id in nodes:
            if node_id not in self.nodes:
                continue
            
            node = self.nodes[node_id]
            
            # Filtrer par type de nœud
            if query.include_node_types and node.node_type not in query.include_node_types:
                continue
            
            if query.exclude_node_types and node.node_type in query.exclude_node_types:
                continue
            
            # Filtrer par date
            if query.time_range:
                if 'start' in query.time_range and node.created_at < query.time_range['start']:
                    continue
                if 'end' in query.time_range and node.created_at > query.time_range['end']:
                    continue
            
            filtered_nodes.add(node_id)
        
        return filtered_nodes
    
    def _filter_edges(self, edges: List[Dict[str, Any]], query: LineageQuery) -> List[Dict[str, Any]]:
        """Filtre les arêtes selon les critères"""
        
        if not query.include_lineage_types:
            return edges
        
        filtered_edges = []
        
        for edge in edges:
            lineage_type_str = edge.get('lineage_type')
            if lineage_type_str:
                try:
                    lineage_type = LineageType(lineage_type_str)
                    if lineage_type in query.include_lineage_types:
                        filtered_edges.append(edge)
                except ValueError:
                    # Type inconnu, inclure par défaut
                    filtered_edges.append(edge)
            else:
                filtered_edges.append(edge)
        
        return filtered_edges
    
    async def _enrich_lineage_result(
        self,
        lineage_result: Dict[str, Any],
        query: LineageQuery
    ) -> Dict[str, Any]:
        """Enrichit le résultat de lignage avec des métadonnées"""
        
        # Enrichir les nœuds avec leurs métadonnées complètes
        enriched_nodes = []
        for node_id in lineage_result['nodes']:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                enriched_nodes.append({
                    'node_id': node_id,
                    'name': node.name,
                    'node_type': node.node_type.value,
                    'source_system': node.source_system,
                    'owner': node.owner,
                    'description': node.description,
                    'created_at': node.created_at.isoformat(),
                    'tags': node.tags,
                    'metadata': node.metadata
                })
        
        # Calculer des statistiques
        statistics = await self._calculate_lineage_statistics(lineage_result)
        
        # Détecter des patterns
        patterns = await self._detect_lineage_patterns(lineage_result)
        
        return {
            **lineage_result,
            'nodes': enriched_nodes,
            'statistics': statistics,
            'patterns': patterns,
            'query': {
                'node_id': query.node_id,
                'direction': query.direction,
                'depth': query.depth
            }
        }
    
    async def _calculate_lineage_statistics(self, lineage_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule des statistiques sur le lignage"""
        
        nodes = lineage_result['nodes']
        edges = lineage_result['edges']
        
        # Statistiques par type de nœud
        node_type_counts = {}
        for node_id in nodes:
            if node_id in self.nodes:
                node_type = self.nodes[node_id].node_type.value
                node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1
        
        # Statistiques par type de lignage
        lineage_type_counts = {}
        for edge in edges:
            lineage_type = edge.get('lineage_type', 'unknown')
            lineage_type_counts[lineage_type] = lineage_type_counts.get(lineage_type, 0) + 1
        
        # Calculs de complexité
        complexity_score = len(nodes) * 0.5 + len(edges) * 0.3
        
        return {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'node_type_distribution': node_type_counts,
            'lineage_type_distribution': lineage_type_counts,
            'complexity_score': complexity_score,
            'avg_confidence': np.mean([e.get('confidence_score', 1.0) for e in edges]) if edges else 1.0
        }
    
    async def _detect_lineage_patterns(self, lineage_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Détecte des patterns dans le lignage"""
        
        patterns = []
        nodes = lineage_result['nodes']
        edges = lineage_result['edges']
        
        # Pattern: Chaîne linéaire
        if len(edges) == len(nodes) - 1:
            patterns.append({
                'type': 'linear_chain',
                'description': 'Linear data transformation chain detected',
                'complexity': 'low'
            })
        
        # Pattern: Hub central
        node_degrees = {}
        for edge in edges:
            source = edge['source']
            target = edge['target']
            node_degrees[source] = node_degrees.get(source, 0) + 1
            node_degrees[target] = node_degrees.get(target, 0) + 1
        
        if node_degrees:
            max_degree = max(node_degrees.values())
            if max_degree > len(nodes) * 0.5:
                hub_node = max(node_degrees, key=node_degrees.get)
                patterns.append({
                    'type': 'hub_pattern',
                    'description': f'Central hub node detected: {hub_node}',
                    'hub_node': hub_node,
                    'complexity': 'medium'
                })
        
        # Pattern: Transformation multiple
        transformation_edges = [e for e in edges if 'transform' in e.get('lineage_type', '').lower()]
        if len(transformation_edges) > 3:
            patterns.append({
                'type': 'complex_transformation',
                'description': 'Multiple transformation steps detected',
                'transformation_count': len(transformation_edges),
                'complexity': 'high'
            })
        
        return patterns
    
    async def analyze_impact(self, node_id: str, change_type: str = "schema_change") -> ImpactAnalysis:
        """Analyse l'impact d'un changement sur un nœud"""
        
        try:
            # Tracer tous les nœuds downstream
            query = LineageQuery(
                node_id=node_id,
                direction="downstream",
                depth=10
            )
            
            lineage_result = await self._perform_lineage_trace(query)
            
            if not lineage_result['success']:
                raise Exception("Failed to trace lineage for impact analysis")
            
            affected_nodes = lineage_result['nodes']
            
            # Calculer les chemins d'impact
            impact_paths = await self._calculate_impact_paths(node_id, affected_nodes)
            
            # Évaluer la sévérité
            severity = self._assess_impact_severity(affected_nodes, change_type)
            
            # Estimer l'effort
            estimated_effort = self._estimate_change_effort(affected_nodes, change_type)
            
            # Générer des recommandations
            recommendations = await self._generate_impact_recommendations(
                node_id, affected_nodes, change_type
            )
            
            return ImpactAnalysis(
                target_node=node_id,
                affected_nodes=affected_nodes,
                impact_paths=impact_paths,
                severity=severity,
                estimated_effort=estimated_effort,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error analyzing impact for {node_id}: {e}")
            raise
    
    async def _calculate_impact_paths(
        self,
        source_node: str,
        affected_nodes: List[str]
    ) -> List[List[str]]:
        """Calcule les chemins d'impact"""
        
        impact_paths = []
        
        for target_node in affected_nodes:
            try:
                # Utiliser NetworkX pour trouver le chemin le plus court
                if nx.has_path(self.lineage_graph, source_node, target_node):
                    path = nx.shortest_path(self.lineage_graph, source_node, target_node)
                    impact_paths.append(path)
            except nx.NetworkXNoPath:
                continue
        
        return impact_paths
    
    def _assess_impact_severity(self, affected_nodes: List[str], change_type: str) -> str:
        """Évalue la sévérité de l'impact"""
        
        # Facteurs de sévérité
        node_count = len(affected_nodes)
        
        # Compter les types de nœuds critiques
        critical_nodes = 0
        for node_id in affected_nodes:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                if node.node_type in [NodeType.REPORT, NodeType.MODEL]:
                    critical_nodes += 1
        
        # Logique de sévérité
        if critical_nodes > 5 or node_count > 20:
            return "critical"
        elif critical_nodes > 2 or node_count > 10:
            return "high"
        elif critical_nodes > 0 or node_count > 5:
            return "medium"
        else:
            return "low"
    
    def _estimate_change_effort(self, affected_nodes: List[str], change_type: str) -> str:
        """Estime l'effort nécessaire pour le changement"""
        
        base_effort = {
            "schema_change": 2,
            "data_type_change": 3,
            "column_removal": 4,
            "table_rename": 1,
            "logic_change": 3
        }.get(change_type, 2)
        
        total_effort = base_effort * len(affected_nodes)
        
        if total_effort < 5:
            return "low (1-2 days)"
        elif total_effort < 15:
            return "medium (3-7 days)"
        elif total_effort < 30:
            return "high (1-2 weeks)"
        else:
            return "very high (2+ weeks)"
    
    async def _generate_impact_recommendations(
        self,
        node_id: str,
        affected_nodes: List[str],
        change_type: str
    ) -> List[str]:
        """Génère des recommandations pour gérer l'impact"""
        
        recommendations = []
        
        # Recommandations générales
        recommendations.append("Review and test all affected downstream processes")
        recommendations.append("Coordinate with owners of affected systems")
        
        # Recommandations spécifiques au type de changement
        if change_type == "schema_change":
            recommendations.append("Update data contracts and API documentation")
            recommendations.append("Consider backward compatibility options")
        elif change_type == "column_removal":
            recommendations.append("Verify that removed columns are not used in critical reports")
            recommendations.append("Plan phased removal with deprecation period")
        
        # Recommandations basées sur les nœuds affectés
        critical_nodes = [
            node_id for node_id in affected_nodes
            if node_id in self.nodes and 
            self.nodes[node_id].node_type in [NodeType.REPORT, NodeType.MODEL]
        ]
        
        if critical_nodes:
            recommendations.append(f"Priority attention needed for {len(critical_nodes)} critical downstream systems")
        
        return recommendations
    
    async def auto_discover_lineage(
        self,
        source_system: str,
        discovery_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Découvre automatiquement le lignage à partir d'un système source"""
        
        try:
            discovered_nodes = []
            discovered_edges = []
            
            # Découverte basée sur le type de système
            if source_system.lower() in ['sql', 'database']:
                nodes, edges = await self._discover_sql_lineage(discovery_config)
                discovered_nodes.extend(nodes)
                discovered_edges.extend(edges)
            
            elif source_system.lower() in ['etl', 'pipeline']:
                nodes, edges = await self._discover_etl_lineage(discovery_config)
                discovered_nodes.extend(nodes)
                discovered_edges.extend(edges)
            
            # Enregistrer les découvertes
            registration_results = []
            
            for node in discovered_nodes:
                result = await self.register_node(node)
                registration_results.append(result)
            
            for edge in discovered_edges:
                result = await self.register_edge(edge)
                registration_results.append(result)
            
            successful_registrations = sum(1 for r in registration_results if r['success'])
            
            return {
                'success': True,
                'discovered_nodes': len(discovered_nodes),
                'discovered_edges': len(discovered_edges),
                'successful_registrations': successful_registrations,
                'discovery_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in auto discovery for {source_system}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _discover_sql_lineage(
        self,
        config: Dict[str, Any]
    ) -> tuple[List[LineageNode], List[LineageEdge]]:
        """Découvre le lignage à partir de requêtes SQL"""
        
        nodes = []
        edges = []
        
        # Placeholder pour analyse SQL
        # En production, analyser les requêtes SQL pour extraire les dépendances
        sql_queries = config.get('sql_queries', [])
        
        for query in sql_queries:
            try:
                # Parser la requête SQL
                parsed = sql_parse(query)
                
                # Extraire les tables sources et cibles
                # Cette implémentation est simplifiée
                source_tables = self._extract_source_tables(parsed)
                target_tables = self._extract_target_tables(parsed)
                
                # Créer des nœuds pour les tables
                for table in source_tables + target_tables:
                    node = LineageNode(
                        node_id=f"table_{table}",
                        name=table,
                        node_type=NodeType.TABLE,
                        source_system="sql",
                        metadata={'discovered': True}
                    )
                    nodes.append(node)
                
                # Créer des arêtes entre sources et cibles
                for source in source_tables:
                    for target in target_tables:
                        edge = LineageEdge(
                            edge_id=str(uuid.uuid4()),
                            source_node=f"table_{source}",
                            target_node=f"table_{target}",
                            lineage_type=LineageType.TRANSFORMS_TO,
                            transformation_logic=query,
                            confidence_score=0.8
                        )
                        edges.append(edge)
                        
            except Exception as e:
                logger.warning(f"Error parsing SQL query: {e}")
        
        return nodes, edges
    
    def _extract_source_tables(self, parsed_sql) -> List[str]:
        """Extrait les tables sources d'une requête SQL parsée"""
        # Implémentation simplifiée
        return ["source_table_1", "source_table_2"]
    
    def _extract_target_tables(self, parsed_sql) -> List[str]:
        """Extrait les tables cibles d'une requête SQL parsée"""
        # Implémentation simplifiée
        return ["target_table_1"]
    
    async def _discover_etl_lineage(
        self,
        config: Dict[str, Any]
    ) -> tuple[List[LineageNode], List[LineageEdge]]:
        """Découvre le lignage à partir de pipelines ETL"""
        
        nodes = []
        edges = []
        
        # Placeholder pour découverte ETL
        # En production, analyser les configurations ETL
        
        return nodes, edges
    
    def _initialize_sql_parser(self) -> Dict[str, Any]:
        """Initialise le parser SQL"""
        return {
            'enabled': True,
            'confidence_threshold': 0.7
        }
    
    def _generate_lineage_cache_key(self, query: LineageQuery) -> str:
        """Génère une clé de cache pour une requête de lignage"""
        
        import hashlib
        
        key_components = [
            query.node_id,
            query.direction,
            str(query.depth),
            ','.join([nt.value for nt in query.include_node_types]),
            ','.join([nt.value for nt in query.exclude_node_types]),
            ','.join([lt.value for lt in query.include_lineage_types])
        ]
        
        key_string = '|'.join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _is_cache_valid(self, cached_result: Dict[str, Any]) -> bool:
        """Vérifie si le résultat en cache est encore valide"""
        
        cached_time = cached_result['timestamp']
        return (datetime.utcnow() - cached_time).seconds < self.cache_ttl
    
    def _cache_lineage_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Met en cache un résultat de lignage"""
        
        self.lineage_cache[cache_key] = {
            'result': result,
            'timestamp': datetime.utcnow()
        }
        
        # Limiter la taille du cache
        if len(self.lineage_cache) > 50:
            oldest_key = min(self.lineage_cache.keys(),
                           key=lambda k: self.lineage_cache[k]['timestamp'])
            del self.lineage_cache[oldest_key]
    
    def _invalidate_cache(self) -> None:
        """Invalide tout le cache de lignage"""
        self.lineage_cache.clear()
    
    async def export_lineage_graph(
        self,
        format_type: str = "graphviz",
        include_metadata: bool = True
    ) -> str:
        """Exporte le graphe de lignage dans différents formats"""
        
        try:
            if format_type == "graphviz":
                return await self._export_to_graphviz(include_metadata)
            elif format_type == "json":
                return await self._export_to_json(include_metadata)
            elif format_type == "cytoscape":
                return await self._export_to_cytoscape(include_metadata)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
                
        except Exception as e:
            logger.error(f"Error exporting lineage graph: {e}")
            raise
    
    async def _export_to_graphviz(self, include_metadata: bool) -> str:
        """Exporte vers format Graphviz DOT"""
        
        dot = graphviz.Digraph(comment='Data Lineage Graph')
        dot.attr(rankdir='LR')
        
        # Ajouter les nœuds
        for node_id, node in self.nodes.items():
            label = f"{node.name}\\n({node.node_type.value})"
            if include_metadata and node.owner:
                label += f"\\nOwner: {node.owner}"
            
            dot.node(node_id, label)
        
        # Ajouter les arêtes
        for edge in self.edges.values():
            label = edge.lineage_type.value
            if include_metadata and edge.transformation_logic:
                label += f"\\n{edge.transformation_logic[:50]}..."
            
            dot.edge(edge.source_node, edge.target_node, label=label)
        
        return dot.source
    
    async def _export_to_json(self, include_metadata: bool) -> str:
        """Exporte vers format JSON"""
        
        export_data = {
            'nodes': [],
            'edges': []
        }
        
        # Exporter les nœuds
        for node in self.nodes.values():
            node_data = {
                'id': node.node_id,
                'name': node.name,
                'type': node.node_type.value,
                'source_system': node.source_system
            }
            
            if include_metadata:
                node_data.update({
                    'owner': node.owner,
                    'description': node.description,
                    'tags': node.tags,
                    'metadata': node.metadata,
                    'created_at': node.created_at.isoformat()
                })
            
            export_data['nodes'].append(node_data)
        
        # Exporter les arêtes
        for edge in self.edges.values():
            edge_data = {
                'source': edge.source_node,
                'target': edge.target_node,
                'type': edge.lineage_type.value
            }
            
            if include_metadata:
                edge_data.update({
                    'transformation_logic': edge.transformation_logic,
                    'confidence_score': edge.confidence_score,
                    'created_at': edge.created_at.isoformat()
                })
            
            export_data['edges'].append(edge_data)
        
        return json.dumps(export_data, indent=2)
    
    async def _export_to_cytoscape(self, include_metadata: bool) -> str:
        """Exporte vers format Cytoscape.js"""
        
        cytoscape_data = {
            'elements': {
                'nodes': [],
                'edges': []
            }
        }
        
        # Nœuds pour Cytoscape
        for node in self.nodes.values():
            node_element = {
                'data': {
                    'id': node.node_id,
                    'label': node.name,
                    'type': node.node_type.value
                }
            }
            
            if include_metadata:
                node_element['data'].update({
                    'owner': node.owner,
                    'description': node.description
                })
            
            cytoscape_data['elements']['nodes'].append(node_element)
        
        # Arêtes pour Cytoscape
        for edge in self.edges.values():
            edge_element = {
                'data': {
                    'id': edge.edge_id,
                    'source': edge.source_node,
                    'target': edge.target_node,
                    'label': edge.lineage_type.value
                }
            }
            
            if include_metadata:
                edge_element['data']['confidence'] = edge.confidence_score
            
            cytoscape_data['elements']['edges'].append(edge_element)
        
        return json.dumps(cytoscape_data, indent=2)


# Instance globale du service
data_lineage_tracker = DataLineageTracker()