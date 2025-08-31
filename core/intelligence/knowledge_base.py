"""Knowledge Base - Intelligent Information Storage and Retrieval

Comprehensive knowledge management system for content intelligence.
Implements advanced knowledge representation, storage, retrieval,
and reasoning capabilities for intelligent content processing.

Features:
- Graph-based knowledge representation
- Semantic search and retrieval
- Ontology management
- Knowledge reasoning and inference
- Dynamic knowledge updating
- Multi-modal knowledge integration

Author: Fahed Mlaiel <mlaiel@live.de>
"""
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from collections import defaultdict, deque
import pickle

# Graph and Knowledge Management
import networkx as nx
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher
import rdflib
from rdflib import Graph as RDFGraph, Namespace, URIRef, Literal

# Vector Storage and Similarity
import faiss
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Natural Language Processing
import spacy
from transformers import AutoTokenizer, AutoModel
import torch

# Database Storage
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Core Dependencies
from ..storage.knowledge_storage import KnowledgeStorage
from ..processors.knowledge_processor import KnowledgeProcessor
from ..engines.reasoning_engine import ReasoningEngine
from ..adapters.ontology_adapter import OntologyAdapter


class KnowledgeType(Enum):
    """Knowledge representation types"""    FACTUAL = "factual"
    PROCEDURAL = "procedural"
    CONCEPTUAL = "conceptual"
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    DECLARATIVE = "declarative"
    CONTEXTUAL = "contextual"
    TEMPORAL = "temporal"


class RelationType(Enum):
    """Relationship types in knowledge graph"""    IS_A = "is_a"
    HAS_PROPERTY = "has_property"
    RELATED_TO = "related_to"
    CAUSES = "causes"
    ENABLES = "enables"
    REQUIRES = "requires"
    CONTAINS = "contains"
    SIMILAR_TO = "similar_to"
    TEMPORAL_BEFORE = "temporal_before"
    TEMPORAL_AFTER = "temporal_after"


@dataclass
class KnowledgeEntity:
    """Knowledge entity representation"""    entity_id: str
    entity_type: str
    name: str
    properties: Dict[str, Any]
    embeddings: Optional[np.ndarray] = None
    confidence: float = 1.0
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class KnowledgeRelation:
    """Knowledge relationship representation"""    relation_id: str
    source_entity: str
    target_entity: str
    relation_type: RelationType
    properties: Dict[str, Any]
    confidence: float = 1.0
    evidence: List[str] = None


@dataclass
class QueryResult:
    """Knowledge query result"""    entities: List[KnowledgeEntity]
    relations: List[KnowledgeRelation]
    query_time: float
    confidence_score: float
    reasoning_path: List[str]


class SemanticMemory:
    """Semantic memory for concept storage and retrieval"""    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.concept_store = {}
        self.concept_embeddings = None
        self.concept_index = None
        self.dimension = 384  # Default for MiniLM
        
    def add_concept(self, concept_id: str, concept_data: Dict[str, Any]) -> bool:
        """Add concept to semantic memory"""        try:
            # Create concept representation
            concept_text = self._concept_to_text(concept_data)
            embedding = self.embedding_model.encode(concept_text)
            
            # Store concept
            self.concept_store[concept_id] = {
                'data': concept_data,
                'text': concept_text,
                'embedding': embedding,
                'created_at': datetime.now()
            }
            
            # Update index
            self._update_index()
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to add concept {concept_id}: {e}")
            return False
    
    def _concept_to_text(self, concept_data: Dict[str, Any]) -> str:
        """Convert concept data to searchable text"""        text_parts = []
        
        # Add name and description
        if 'name' in concept_data:
            text_parts.append(concept_data['name'])
        if 'description' in concept_data:
            text_parts.append(concept_data['description'])
        
        # Add properties
        for key, value in concept_data.get('properties', {}).items():
            text_parts.append(f"{key}: {value}")
        
        # Add tags or keywords
        if 'tags' in concept_data:
            text_parts.extend(concept_data['tags'])
        
        return " ".join(text_parts)
    
    def _update_index(self) -> None:
        """Update FAISS index with current concepts"""        if not self.concept_store:
            return
        
        # Collect all embeddings
        embeddings = []
        for concept in self.concept_store.values():
            embeddings.append(concept['embedding'])
        
        embeddings = np.array(embeddings).astype('float32')
        
        # Create or update FAISS index
        if self.concept_index is None:
            self.concept_index = faiss.IndexFlatIP(self.dimension)
        else:
            self.concept_index.reset()
        
        self.concept_index.add(embeddings)
        self.concept_embeddings = embeddings
    
    def search_concepts(
        self,
        query: str,
        top_k: int = 10,
        threshold: float = 0.5
    ) -> List[Tuple[str, float]]:
        """Search for similar concepts"""        try:
            if not self.concept_store or self.concept_index is None:
                return []
            
            # Encode query
            query_embedding = self.embedding_model.encode(query).astype('float32')
            query_embedding = query_embedding.reshape(1, -1)
            
            # Search
            scores, indices = self.concept_index.search(query_embedding, top_k)
            
            # Filter by threshold and return results
            results = []
            concept_ids = list(self.concept_store.keys())
            
            for score, idx in zip(scores[0], indices[0]):
                if score >= threshold and idx < len(concept_ids):
                    concept_id = concept_ids[idx]
                    results.append((concept_id, float(score)))
            
            return results
            
        except Exception as e:
            logging.error(f"Concept search failed: {e}")
            return []


class KnowledgeGraph:
    """Graph-based knowledge representation"""    
    def __init__(self, graph_db_url: Optional[str] = None):
        self.graph_db_url = graph_db_url
        
        if graph_db_url:
            try:
                self.graph = Graph(graph_db_url)
                self.use_neo4j = True
            except:
                self.graph = nx.DiGraph()
                self.use_neo4j = False
        else:
            self.graph = nx.DiGraph()
            self.use_neo4j = False
        
        self.entity_cache = {}
        self.relation_cache = {}
        
    def add_entity(self, entity: KnowledgeEntity) -> bool:
        """Add entity to knowledge graph"""        try:
            if self.use_neo4j:
                # Neo4j implementation
                node = Node(
                    entity.entity_type,
                    entity_id=entity.entity_id,
                    name=entity.name,
                    properties=json.dumps(entity.properties),
                    confidence=entity.confidence,
                    created_at=entity.created_at.isoformat() if entity.created_at else None
                )
                self.graph.create(node)
            else:
                # NetworkX implementation
                self.graph.add_node(
                    entity.entity_id,
                    entity_type=entity.entity_type,
                    name=entity.name,
                    properties=entity.properties,
                    confidence=entity.confidence,
                    created_at=entity.created_at,
                    embeddings=entity.embeddings
                )
            
            # Cache entity
            self.entity_cache[entity.entity_id] = entity
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to add entity {entity.entity_id}: {e}")
            return False
    
    def add_relation(self, relation: KnowledgeRelation) -> bool:
        """Add relationship to knowledge graph"""        try:
            if self.use_neo4j:
                # Neo4j implementation
                source_node = self.graph.nodes.match(entity_id=relation.source_entity).first()
                target_node = self.graph.nodes.match(entity_id=relation.target_entity).first()
                
                if source_node and target_node:
                    rel = Relationship(
                        source_node,
                        relation.relation_type.value,
                        target_node,
                        relation_id=relation.relation_id,
                        properties=json.dumps(relation.properties),
                        confidence=relation.confidence,
                        evidence=json.dumps(relation.evidence or [])
                    )
                    self.graph.create(rel)
            else:
                # NetworkX implementation
                self.graph.add_edge(
                    relation.source_entity,
                    relation.target_entity,
                    relation_id=relation.relation_id,
                    relation_type=relation.relation_type.value,
                    properties=relation.properties,
                    confidence=relation.confidence,
                    evidence=relation.evidence
                )
            
            # Cache relation
            self.relation_cache[relation.relation_id] = relation
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to add relation {relation.relation_id}: {e}")
            return False
    
    def get_entity(self, entity_id: str) -> Optional[KnowledgeEntity]:
        """Get entity by ID"""        if entity_id in self.entity_cache:
            return self.entity_cache[entity_id]
        
        try:
            if self.use_neo4j:
                node = self.graph.nodes.match(entity_id=entity_id).first()
                if node:
                    return self._node_to_entity(node)
            else:
                if entity_id in self.graph.nodes:
                    node_data = self.graph.nodes[entity_id]
                    return KnowledgeEntity(
                        entity_id=entity_id,
                        entity_type=node_data.get('entity_type', 'unknown'),
                        name=node_data.get('name', ''),
                        properties=node_data.get('properties', {}),
                        embeddings=node_data.get('embeddings'),
                        confidence=node_data.get('confidence', 1.0),
                        created_at=node_data.get('created_at')
                    )
            
            return None
            
        except Exception as e:
            logging.error(f"Failed to get entity {entity_id}: {e}")
            return None
    
    def get_related_entities(
        self,
        entity_id: str,
        relation_types: Optional[List[RelationType]] = None,
        max_depth: int = 2
    ) -> List[KnowledgeEntity]:
        """Get entities related to given entity"""        try:
            related_entities = []
            
            if self.use_neo4j:
                # Neo4j query for related entities
                query = f"""                MATCH (source {{entity_id: $entity_id}})
                MATCH (source)-[r*1..{max_depth}]-(target)
                RETURN DISTINCT target
                """                results = self.graph.run(query, entity_id=entity_id)
                
                for record in results:
                    entity = self._node_to_entity(record['target'])
                    if entity:
                        related_entities.append(entity)
            else:
                # NetworkX traversal
                visited = set()
                queue = deque([(entity_id, 0)])
                
                while queue:
                    current_id, depth = queue.popleft()
                    
                    if depth >= max_depth or current_id in visited:
                        continue
                    
                    visited.add(current_id)
                    
                    # Get neighbors
                    for neighbor in self.graph.neighbors(current_id):
                        if neighbor not in visited:
                            entity = self.get_entity(neighbor)
                            if entity:
                                related_entities.append(entity)
                            queue.append((neighbor, depth + 1))
            
            return related_entities
            
        except Exception as e:
            logging.error(f"Failed to get related entities for {entity_id}: {e}")
            return []
    
    def _node_to_entity(self, node) -> Optional[KnowledgeEntity]:
        """Convert Neo4j node to KnowledgeEntity"""        try:
            return KnowledgeEntity(
                entity_id=node.get('entity_id', ''),
                entity_type=list(node.labels)[0] if node.labels else 'unknown',
                name=node.get('name', ''),
                properties=json.loads(node.get('properties', '{}')),
                confidence=node.get('confidence', 1.0),
                created_at=datetime.fromisoformat(node.get('created_at')) if node.get('created_at') else None
            )
        except Exception:
            return None
    
    def find_shortest_path(
        self,
        source_id: str,
        target_id: str
    ) -> List[str]:
        """Find shortest path between entities"""        try:
            if self.use_neo4j:
                query = """                MATCH (source {entity_id: $source_id}), (target {entity_id: $target_id})
                MATCH path = shortestPath((source)-[*]-(target))
                RETURN path
                """                result = self.graph.run(query, source_id=source_id, target_id=target_id).data()
                
                if result:
                    path = result[0]['path']
                    return [node['entity_id'] for node in path.nodes]
            else:
                try:
                    path = nx.shortest_path(self.graph, source_id, target_id)
                    return path
                except nx.NetworkXNoPath:
                    return []
            
            return []
            
        except Exception as e:
            logging.error(f"Failed to find path from {source_id} to {target_id}: {e}")
            return []


class OntologyManager:
    """Ontology management for structured knowledge"""    
    def __init__(self):
        self.ontology = RDFGraph()
        self.namespaces = {}
        self.classes = set()
        self.properties = set()
        
        # Define common namespaces
        self.content_ns = Namespace("http://content.ai/ontology#")
        self.ontology.bind("content", self.content_ns)
        
    def add_class(self, class_name: str, parent_class: Optional[str] = None) -> bool:
        """Add class to ontology"""        try:
            class_uri = self.content_ns[class_name]
            
            # Add class declaration
            self.ontology.add((class_uri, rdflib.RDF.type, rdflib.RDFS.Class))
            
            # Add parent relationship if specified
            if parent_class:
                parent_uri = self.content_ns[parent_class]
                self.ontology.add((class_uri, rdflib.RDFS.subClassOf, parent_uri))
            
            self.classes.add(class_name)
            return True
            
        except Exception as e:
            logging.error(f"Failed to add class {class_name}: {e}")
            return False
    
    def add_property(
        self,
        property_name: str,
        domain: Optional[str] = None,
        range_type: Optional[str] = None
    ) -> bool:
        """Add property to ontology"""        try:
            property_uri = self.content_ns[property_name]
            
            # Add property declaration
            self.ontology.add((property_uri, rdflib.RDF.type, rdflib.RDF.Property))
            
            # Add domain if specified
            if domain:
                domain_uri = self.content_ns[domain]
                self.ontology.add((property_uri, rdflib.RDFS.domain, domain_uri))
            
            # Add range if specified
            if range_type:
                if range_type in ['string', 'integer', 'float', 'boolean']:
                    range_uri = getattr(rdflib.XSD, range_type)
                else:
                    range_uri = self.content_ns[range_type]
                self.ontology.add((property_uri, rdflib.RDFS.range, range_uri))
            
            self.properties.add(property_name)
            return True
            
        except Exception as e:
            logging.error(f"Failed to add property {property_name}: {e}")
            return False
    
    def validate_instance(self, instance_data: Dict[str, Any], class_name: str) -> bool:
        """Validate instance against ontology"""        try:
            # Check if class exists
            if class_name not in self.classes:
                return False
            
            # Get class properties
            class_uri = self.content_ns[class_name]
            class_properties = set()
            
            for prop_uri in self.ontology.subjects(rdflib.RDFS.domain, class_uri):
                prop_name = str(prop_uri).split('#')[-1]
                class_properties.add(prop_name)
            
            # Validate instance properties
            for prop_name, prop_value in instance_data.items():
                if prop_name not in class_properties:
                    logging.warning(f"Property {prop_name} not defined for class {class_name}")
                    return False
            
            return True
            
        except Exception as e:
            logging.error(f"Instance validation failed: {e}")
            return False
    
    def query_ontology(self, sparql_query: str) -> List[Dict[str, Any]]:
        """Execute SPARQL query on ontology"""        try:
            results = self.ontology.query(sparql_query)
            return [dict(row.asdict()) for row in results]
        except Exception as e:
            logging.error(f"SPARQL query failed: {e}")
            return []


class KnowledgeBase:
    """    Comprehensive knowledge base for content intelligence
    """    
    def __init__(self, config: Dict[str, Any]):
        """        Initialize knowledge base
        
        Args:
            config: Configuration dictionary
        """        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self._initialize_storage()
        self._initialize_graph()
        self._initialize_semantic_memory()
        self._initialize_ontology()
        
        # Initialize processors
        self._initialize_processors()
        
        # Knowledge tracking
        self.knowledge_metrics = {
            "total_entities": 0,
            "total_relations": 0,
            "total_concepts": 0,
            "query_count": 0,
            "average_query_time": 0.0,
            "knowledge_completeness": 0.0
        }
        
        # Cache for frequent queries
        self.query_cache = {}
        self.cache_size = config.get("cache_size", 1000)
    
    def _initialize_storage(self) -> None:
        """Initialize knowledge storage"""        try:
            self.knowledge_storage = KnowledgeStorage(self.config)
            self.logger.info("Knowledge storage initialized")
        except Exception as e:
            self.logger.warning(f"Knowledge storage initialization failed: {e}")
    
    def _initialize_graph(self) -> None:
        """Initialize knowledge graph"""        graph_db_url = self.config.get("graph_db_url")
        self.knowledge_graph = KnowledgeGraph(graph_db_url)
        self.logger.info("Knowledge graph initialized")
    
    def _initialize_semantic_memory(self) -> None:
        """Initialize semantic memory"""        embedding_model = self.config.get("embedding_model", "all-MiniLM-L6-v2")
        self.semantic_memory = SemanticMemory(embedding_model)
        self.logger.info("Semantic memory initialized")
    
    def _initialize_ontology(self) -> None:
        """Initialize ontology manager"""        self.ontology_manager = OntologyManager()
        self._setup_content_ontology()
        self.logger.info("Ontology manager initialized")
    
    def _initialize_processors(self) -> None:
        """Initialize knowledge processors"""        try:
            self.knowledge_processor = KnowledgeProcessor(self.config)
            self.reasoning_engine = ReasoningEngine(self.config)
            self.ontology_adapter = OntologyAdapter(self.config)
        except Exception as e:
            self.logger.warning(f"Some processors could not be initialized: {e}")
    
    def _setup_content_ontology(self) -> None:
        """Setup basic content ontology"""        # Add content classes
        self.ontology_manager.add_class("Content")
        self.ontology_manager.add_class("AudioContent", "Content")
        self.ontology_manager.add_class("VideoContent", "Content")
        self.ontology_manager.add_class("ImageContent", "Content")
        self.ontology_manager.add_class("TextContent", "Content")
        
        # Add creator classes
        self.ontology_manager.add_class("Creator")
        self.ontology_manager.add_class("Musician", "Creator")
        self.ontology_manager.add_class("Blogger", "Creator")
        self.ontology_manager.add_class("Photographer", "Creator")
        self.ontology_manager.add_class("Influencer", "Creator")
        
        # Add properties
        self.ontology_manager.add_property("hasTitle", "Content", "string")
        self.ontology_manager.add_property("hasDescription", "Content", "string")
        self.ontology_manager.add_property("hasDuration", "Content", "float")
        self.ontology_manager.add_property("hasQuality", "Content", "float")
        self.ontology_manager.add_property("createdBy", "Content", "Creator")
        self.ontology_manager.add_property("hasGenre", "Content", "string")
        self.ontology_manager.add_property("hasTag", "Content", "string")
    
    async def add_knowledge(
        self,
        knowledge_type: KnowledgeType,
        data: Dict[str, Any],
        source: str = "user_input"
    ) -> bool:
        """        Add knowledge to the knowledge base
        
        Args:
            knowledge_type: Type of knowledge to add
            data: Knowledge data
            source: Source of the knowledge
            
        Returns:
            Success status
        """        try:
            if knowledge_type == KnowledgeType.FACTUAL:
                return await self._add_factual_knowledge(data, source)
            elif knowledge_type == KnowledgeType.CONCEPTUAL:
                return await self._add_conceptual_knowledge(data, source)
            elif knowledge_type == KnowledgeType.SEMANTIC:
                return await self._add_semantic_knowledge(data, source)
            elif knowledge_type == KnowledgeType.PROCEDURAL:
                return await self._add_procedural_knowledge(data, source)
            else:
                return await self._add_general_knowledge(data, source, knowledge_type)
                
        except Exception as e:
            self.logger.error(f"Failed to add knowledge: {e}")
            return False
    
    async def _add_factual_knowledge(self, data: Dict[str, Any], source: str) -> bool:
        """Add factual knowledge as entities and relations"""        try:
            # Extract entities from data
            entities = data.get('entities', [])
            relations = data.get('relations', [])
            
            # Add entities to graph
            for entity_data in entities:
                entity = KnowledgeEntity(
                    entity_id=entity_data.get('id', f"entity_{len(self.knowledge_graph.entity_cache)}"),
                    entity_type=entity_data.get('type', 'unknown'),
                    name=entity_data.get('name', ''),
                    properties=entity_data.get('properties', {}),
                    confidence=entity_data.get('confidence', 1.0),
                    created_at=datetime.now()
                )
                
                # Validate against ontology
                if entity.entity_type in self.ontology_manager.classes:
                    if not self.ontology_manager.validate_instance(entity.properties, entity.entity_type):
                        self.logger.warning(f"Entity {entity.entity_id} failed ontology validation")
                
                self.knowledge_graph.add_entity(entity)
            
            # Add relations to graph
            for relation_data in relations:
                relation = KnowledgeRelation(
                    relation_id=relation_data.get('id', f"rel_{len(self.knowledge_graph.relation_cache)}"),
                    source_entity=relation_data.get('source'),
                    target_entity=relation_data.get('target'),
                    relation_type=RelationType(relation_data.get('type', 'related_to')),
                    properties=relation_data.get('properties', {}),
                    confidence=relation_data.get('confidence', 1.0),
                    evidence=[source]
                )
                
                self.knowledge_graph.add_relation(relation)
            
            # Update metrics
            self.knowledge_metrics["total_entities"] += len(entities)
            self.knowledge_metrics["total_relations"] += len(relations)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add factual knowledge: {e}")
            return False
    
    async def _add_conceptual_knowledge(self, data: Dict[str, Any], source: str) -> bool:
        """Add conceptual knowledge to semantic memory"""        try:
            concepts = data.get('concepts', [])
            
            for concept_data in concepts:
                concept_id = concept_data.get('id', f"concept_{len(self.semantic_memory.concept_store)}")
                
                # Add to semantic memory
                success = self.semantic_memory.add_concept(concept_id, concept_data)
                
                if success:
                    self.knowledge_metrics["total_concepts"] += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add conceptual knowledge: {e}")
            return False
    
    async def _add_semantic_knowledge(self, data: Dict[str, Any], source: str) -> bool:
        """Add semantic knowledge"""        # For semantic knowledge, we can add both to graph and semantic memory
        success1 = await self._add_factual_knowledge(data, source)
        success2 = await self._add_conceptual_knowledge(data, source)
        
        return success1 or success2
    
    async def _add_procedural_knowledge(self, data: Dict[str, Any], source: str) -> bool:
        """Add procedural knowledge (processes and workflows)"""        try:
            # Procedural knowledge as a sequence of steps
            process_id = data.get('process_id', f"process_{int(datetime.now().timestamp())}")
            steps = data.get('steps', [])
            
            # Create entities for each step
            for i, step in enumerate(steps):
                step_entity = KnowledgeEntity(
                    entity_id=f"{process_id}_step_{i}",
                    entity_type="ProcessStep",
                    name=step.get('name', f"Step {i+1}"),
                    properties={
                        'description': step.get('description', ''),
                        'order': i,
                        'process_id': process_id
                    },
                    confidence=step.get('confidence', 1.0),
                    created_at=datetime.now()
                )
                
                self.knowledge_graph.add_entity(step_entity)
                
                # Add sequential relations
                if i > 0:
                    relation = KnowledgeRelation(
                        relation_id=f"{process_id}_seq_{i-1}_{i}",
                        source_entity=f"{process_id}_step_{i-1}",
                        target_entity=f"{process_id}_step_{i}",
                        relation_type=RelationType.TEMPORAL_BEFORE,
                        properties={'process_id': process_id},
                        confidence=1.0,
                        evidence=[source]
                    )
                    
                    self.knowledge_graph.add_relation(relation)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add procedural knowledge: {e}")
            return False
    
    async def _add_general_knowledge(
        self,
        data: Dict[str, Any],
        source: str,
        knowledge_type: KnowledgeType
    ) -> bool:
        """Add general knowledge"""        # Default implementation: treat as factual knowledge
        return await self._add_factual_knowledge(data, source)
    
    async def query_knowledge(
        self,
        query: str,
        query_type: str = "semantic",
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> QueryResult:
        """        Query the knowledge base
        
        Args:
            query: Query string
            query_type: Type of query (semantic, graph, ontology)
            filters: Optional filters
            limit: Maximum number of results
            
        Returns:
            QueryResult: Query results and metadata
        """        start_time = datetime.now()
        
        try:
            # Check cache first
            cache_key = f"{query}_{query_type}_{hash(str(filters))}_{limit}"
            if cache_key in self.query_cache:
                cached_result = self.query_cache[cache_key]
                self.knowledge_metrics["query_count"] += 1
                return cached_result
            
            entities = []
            relations = []
            reasoning_path = []
            
            if query_type == "semantic":
                # Semantic search in concept store
                concept_results = self.semantic_memory.search_concepts(query, limit)
                
                for concept_id, similarity in concept_results:
                    if concept_id in self.semantic_memory.concept_store:
                        concept_data = self.semantic_memory.concept_store[concept_id]['data']
                        
                        entity = KnowledgeEntity(
                            entity_id=concept_id,
                            entity_type="Concept",
                            name=concept_data.get('name', concept_id),
                            properties=concept_data,
                            confidence=similarity
                        )
                        entities.append(entity)
                        reasoning_path.append(f"Semantic similarity: {similarity:.3f}")
            
            elif query_type == "graph":
                # Graph-based search
                entities = await self._graph_search(query, filters, limit)
                reasoning_path.append("Graph traversal search")
            
            elif query_type == "ontology":
                # Ontology-based query
                sparql_query = self._natural_to_sparql(query)
                ontology_results = self.ontology_manager.query_ontology(sparql_query)
                
                for result in ontology_results[:limit]:
                    # Convert SPARQL result to entity
                    entity = self._sparql_result_to_entity(result)
                    if entity:
                        entities.append(entity)
                
                reasoning_path.append(f"SPARQL query: {sparql_query}")
            
            # Get relations between found entities
            if len(entities) > 1:
                relations = await self._find_entity_relations(entities)
            
            # Calculate query time
            query_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate confidence score
            confidence_score = np.mean([e.confidence for e in entities]) if entities else 0.0
            
            # Create result
            result = QueryResult(
                entities=entities,
                relations=relations,
                query_time=query_time,
                confidence_score=confidence_score,
                reasoning_path=reasoning_path
            )
            
            # Cache result
            if len(self.query_cache) < self.cache_size:
                self.query_cache[cache_key] = result
            
            # Update metrics
            self.knowledge_metrics["query_count"] += 1
            current_avg = self.knowledge_metrics["average_query_time"]
            total_queries = self.knowledge_metrics["query_count"]
            self.knowledge_metrics["average_query_time"] = (
                (current_avg * (total_queries - 1) + query_time) / total_queries
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Knowledge query failed: {e}")
            return QueryResult([], [], 0.0, 0.0, [f"Error: {e}"])
    
    async def _graph_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        limit: int
    ) -> List[KnowledgeEntity]:
        """Search entities in knowledge graph"""        entities = []
        
        try:
            # Simple name-based search for now
            for entity_id, entity in self.knowledge_graph.entity_cache.items():
                if query.lower() in entity.name.lower():
                    # Apply filters if provided
                    if filters:
                        if not self._apply_filters(entity, filters):
                            continue
                    
                    entities.append(entity)
                    
                    if len(entities) >= limit:
                        break
            
            return entities
            
        except Exception as e:
            self.logger.error(f"Graph search failed: {e}")
            return []
    
    def _apply_filters(self, entity: KnowledgeEntity, filters: Dict[str, Any]) -> bool:
        """Apply filters to entity"""        try:
            for filter_key, filter_value in filters.items():
                if filter_key == "entity_type":
                    if entity.entity_type != filter_value:
                        return False
                elif filter_key == "confidence_min":
                    if entity.confidence < filter_value:
                        return False
                elif filter_key in entity.properties:
                    if entity.properties[filter_key] != filter_value:
                        return False
            
            return True
            
        except Exception:
            return False
    
    async def _find_entity_relations(self, entities: List[KnowledgeEntity]) -> List[KnowledgeRelation]:
        """Find relations between entities"""        relations = []
        
        try:
            entity_ids = {e.entity_id for e in entities}
            
            # Check all cached relations
            for relation in self.knowledge_graph.relation_cache.values():
                if (relation.source_entity in entity_ids and 
                    relation.target_entity in entity_ids):
                    relations.append(relation)
            
            return relations
            
        except Exception as e:
            self.logger.error(f"Finding entity relations failed: {e}")
            return []
    
    def _natural_to_sparql(self, query: str) -> str:
        """Convert natural language query to SPARQL (simplified)"""        # This is a very basic implementation
        # A real system would use more sophisticated NLP
        
        query_lower = query.lower()
        
        if "content" in query_lower and "type" in query_lower:
            return """            SELECT ?content ?type WHERE {
                ?content rdf:type content:Content .
                ?content rdf:type ?type .
            }
            """        elif "creator" in query_lower:
            return """            SELECT ?creator ?name WHERE {
                ?creator rdf:type content:Creator .
                ?creator content:hasName ?name .
            }
            """        else:
            return """            SELECT ?s ?p ?o WHERE {
                ?s ?p ?o .
            } LIMIT 10
            """    
    def _sparql_result_to_entity(self, result: Dict[str, Any]) -> Optional[KnowledgeEntity]:
        """Convert SPARQL result to KnowledgeEntity"""        try:
            # Extract entity information from SPARQL result
            entity_id = str(result.get('s', result.get('content', 'unknown')))
            entity_type = str(result.get('type', 'unknown')).split('#')[-1]
            name = str(result.get('name', entity_id))
            
            return KnowledgeEntity(
                entity_id=entity_id,
                entity_type=entity_type,
                name=name,
                properties=result,
                confidence=1.0,
                created_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"SPARQL result conversion failed: {e}")
            return None
    
    async def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get summary of knowledge base contents"""        try:
            summary = {
                "metrics": self.knowledge_metrics.copy(),
                "entity_types": defaultdict(int),
                "relation_types": defaultdict(int),
                "concept_categories": defaultdict(int),
                "top_entities": [],
                "knowledge_coverage": {}
            }
            
            # Analyze entities
            for entity in self.knowledge_graph.entity_cache.values():
                summary["entity_types"][entity.entity_type] += 1
            
            # Analyze relations
            for relation in self.knowledge_graph.relation_cache.values():
                summary["relation_types"][relation.relation_type.value] += 1
            
            # Analyze concepts
            for concept_id, concept in self.semantic_memory.concept_store.items():
                category = concept['data'].get('category', 'uncategorized')
                summary["concept_categories"][category] += 1
            
            # Get top entities by confidence
            top_entities = sorted(
                self.knowledge_graph.entity_cache.values(),
                key=lambda x: x.confidence,
                reverse=True
            )[:10]
            
            summary["top_entities"] = [
                {
                    "id": e.entity_id,
                    "name": e.name,
                    "type": e.entity_type,
                    "confidence": e.confidence
                }
                for e in top_entities
            ]
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Knowledge summary generation failed: {e}")
            return {"error": str(e)}
    
    async def validate_knowledge_consistency(self) -> Dict[str, Any]:
        """Validate knowledge base consistency"""        try:
            validation_results = {
                "is_consistent": True,
                "issues": [],
                "warnings": [],
                "recommendations": []
            }
            
            # Check for orphaned entities
            entity_ids = set(self.knowledge_graph.entity_cache.keys())
            referenced_entities = set()
            
            for relation in self.knowledge_graph.relation_cache.values():
                referenced_entities.add(relation.source_entity)
                referenced_entities.add(relation.target_entity)
            
            orphaned = entity_ids - referenced_entities
            if orphaned:
                validation_results["warnings"].append(f"Found {len(orphaned)} orphaned entities")
            
            # Check for broken relations
            broken_relations = []
            for relation in self.knowledge_graph.relation_cache.values():
                if (relation.source_entity not in entity_ids or 
                    relation.target_entity not in entity_ids):
                    broken_relations.append(relation.relation_id)
            
            if broken_relations:
                validation_results["is_consistent"] = False
                validation_results["issues"].append(f"Found {len(broken_relations)} broken relations")
            
            # Check ontology compliance
            ontology_violations = 0
            for entity in self.knowledge_graph.entity_cache.values():
                if entity.entity_type in self.ontology_manager.classes:
                    if not self.ontology_manager.validate_instance(entity.properties, entity.entity_type):
                        ontology_violations += 1
            
            if ontology_violations > 0:
                validation_results["warnings"].append(f"Found {ontology_violations} ontology violations")
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Knowledge validation failed: {e}")
            return {"is_consistent": False, "error": str(e)}
    
    def clear_cache(self) -> None:
        """Clear query cache"""        self.query_cache.clear()
        self.logger.info("Knowledge base cache cleared")
    
    async def backup_knowledge(self, backup_path: str) -> bool:
        """Backup knowledge base to file"""        try:
            backup_data = {
                "entities": {k: {
                    "entity_id": v.entity_id,
                    "entity_type": v.entity_type,
                    "name": v.name,
                    "properties": v.properties,
                    "confidence": v.confidence,
                    "created_at": v.created_at.isoformat() if v.created_at else None
                } for k, v in self.knowledge_graph.entity_cache.items()},
                
                "relations": {k: {
                    "relation_id": v.relation_id,
                    "source_entity": v.source_entity,
                    "target_entity": v.target_entity,
                    "relation_type": v.relation_type.value,
                    "properties": v.properties,
                    "confidence": v.confidence,
                    "evidence": v.evidence
                } for k, v in self.knowledge_graph.relation_cache.items()},
                
                "concepts": {k: v['data'] for k, v in self.semantic_memory.concept_store.items()},
                
                "metadata": {
                    "backup_time": datetime.now().isoformat(),
                    "metrics": self.knowledge_metrics
                }
            }
            
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            self.logger.info(f"Knowledge base backed up to {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Knowledge backup failed: {e}")
            return False
