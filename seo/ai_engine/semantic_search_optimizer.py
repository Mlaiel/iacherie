"""
Semantic Search Optimizer for Ainflue Platform
==============================================

Advanced semantic search optimization leveraging transformer models and knowledge graphs.
Optimizes content for semantic understanding by modern search engines and AI systems.

Features:
- Semantic similarity analysis with BERT/RoBERTa
- Entity relationship mapping and knowledge graphs
- Contextual relevance scoring
- Intent-based optimization
- Vector embeddings for content understanding

Author: Fahed Mlaiel (mlaiel@live.de)
Lead Dev IA + ML Engineer + Backend Senior expertise applied
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import re
import torch
from transformers import AutoTokenizer, AutoModel, pipeline
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import networkx as nx

logger = logging.getLogger(__name__)

class SemanticOptimizationLevel(Enum):
    """Semantic optimization complexity levels."""
    BASIC = "basic"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"
    AI_POWERED = "ai_powered"

class SearchIntent(Enum):
    """Search intent categories for optimization."""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"
    LOCAL = "local"

@dataclass
class Entity:
    """Semantic entity representation."""
    text: str
    label: str
    confidence: float
    start_pos: int
    end_pos: int
    semantic_type: str
    relations: List[str]

@dataclass
class SemanticVector:
    """Semantic vector representation of content."""
    content_id: str
    embeddings: np.ndarray
    entity_vectors: Dict[str, np.ndarray]
    similarity_scores: Dict[str, float]
    semantic_clusters: List[int]

@dataclass
class KnowledgeGraph:
    """Knowledge graph structure for entities."""
    nodes: Dict[str, Dict[str, Any]]
    edges: List[Tuple[str, str, str]]
    centrality_scores: Dict[str, float]
    semantic_paths: List[List[str]]
    authority_score: float

@dataclass
class SemanticOptimization:
    """Result of semantic search optimization."""
    original_content: str
    optimized_content: str
    semantic_score: float
    entity_graph: KnowledgeGraph
    semantic_keywords: List[str]
    context_suggestions: List[str]
    intent_alignment: Dict[SearchIntent, float]
    similarity_matrix: np.ndarray
    optimization_metadata: Dict[str, Any]

@dataclass
class RelevanceScore:
    """Contextual relevance scoring."""
    content_relevance: float
    entity_relevance: float
    semantic_coherence: float
    intent_alignment: float
    overall_score: float
    improvement_suggestions: List[str]

class SemanticSearchOptimizer:
    """Advanced semantic search optimization engine."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize semantic search optimizer.
        
        Args:
            config: Configuration dictionary with model settings
        """
        self.config = config or {}
        self.model_name = self.config.get('model_name', 'sentence-transformers/all-MiniLM-L6-v2')
        self.spacy_model = self.config.get('spacy_model', 'en_core_web_sm')
        self.optimization_level = SemanticOptimizationLevel(
            self.config.get('optimization_level', 'advanced')
        )
        
        # Initialize models
        self.tokenizer = None
        self.model = None
        self.nlp = None
        self.similarity_threshold = self.config.get('similarity_threshold', 0.7)
        self.max_entities = self.config.get('max_entities', 50)
        
        # Caching for performance
        self._embedding_cache: Dict[str, np.ndarray] = {}
        self._entity_cache: Dict[str, List[Entity]] = {}
        
        logger.info(f"SemanticSearchOptimizer initialized with {self.optimization_level}")

    async def initialize_models(self) -> None:
        """Initialize transformer and NLP models asynchronously."""
        try:
            # Load transformer model for embeddings
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            
            # Load spaCy for entity extraction
            self.nlp = spacy.load(self.spacy_model)
            
            logger.info("Semantic models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize semantic models: {e}")
            raise

    async def optimize_for_semantic_search(self, content: str, target_keywords: Optional[List[str]] = None) -> SemanticOptimization:
        """Optimize content for semantic search understanding.
        
        Args:
            content: Content to optimize
            target_keywords: Optional target keywords for optimization
            
        Returns:
            SemanticOptimization with optimized content and analysis
        """
        if not self.model:
            await self.initialize_models()
            
        try:
            # Extract entities and create knowledge graph
            entities = await self.extract_semantic_entities(content)
            knowledge_graph = await self.generate_entity_graph(entities)
            
            # Generate semantic embeddings
            embeddings = await self._generate_embeddings(content)
            
            # Analyze semantic similarity with target keywords
            similarity_matrix = await self._compute_similarity_matrix(content, target_keywords or [])
            
            # Determine search intent alignment
            intent_alignment = await self._analyze_search_intent(content)
            
            # Generate semantic keywords
            semantic_keywords = await self._extract_semantic_keywords(content, entities)
            
            # Optimize content structure
            optimized_content = await self._optimize_semantic_structure(
                content, entities, semantic_keywords, intent_alignment
            )
            
            # Calculate semantic score
            semantic_score = await self._calculate_semantic_score(
                content, optimized_content, entities, intent_alignment
            )
            
            # Generate context suggestions
            context_suggestions = await self._generate_context_suggestions(
                content, entities, semantic_keywords
            )
            
            return SemanticOptimization(
                original_content=content,
                optimized_content=optimized_content,
                semantic_score=semantic_score,
                entity_graph=knowledge_graph,
                semantic_keywords=semantic_keywords,
                context_suggestions=context_suggestions,
                intent_alignment=intent_alignment,
                similarity_matrix=similarity_matrix,
                optimization_metadata={
                    'optimization_level': self.optimization_level.value,
                    'entities_count': len(entities),
                    'processing_time': datetime.now().isoformat(),
                    'model_version': self.model_name
                }
            )
            
        except Exception as e:
            logger.error(f"Semantic optimization failed: {e}")
            raise

    async def generate_entity_graph(self, entities: List[Entity]) -> KnowledgeGraph:
        """Generate knowledge graph from extracted entities.
        
        Args:
            entities: List of extracted entities
            
        Returns:
            KnowledgeGraph with entity relationships
        """
        try:
            # Create graph structure
            graph = nx.DiGraph()
            nodes = {}
            edges = []
            
            # Add entity nodes
            for entity in entities:
                node_id = f"{entity.text}_{entity.label}"
                nodes[node_id] = {
                    'text': entity.text,
                    'label': entity.label,
                    'confidence': entity.confidence,
                    'semantic_type': entity.semantic_type
                }
                graph.add_node(node_id, **nodes[node_id])
            
            # Generate entity relationships
            for i, entity1 in enumerate(entities):
                for j, entity2 in enumerate(entities[i+1:], i+1):
                    # Calculate semantic relationship
                    relationship_strength = await self._calculate_entity_relationship(entity1, entity2)
                    
                    if relationship_strength > self.similarity_threshold:
                        node1_id = f"{entity1.text}_{entity1.label}"
                        node2_id = f"{entity2.text}_{entity2.label}"
                        relation_type = self._determine_relation_type(entity1, entity2)
                        
                        edges.append((node1_id, node2_id, relation_type))
                        graph.add_edge(node1_id, node2_id, 
                                     weight=relationship_strength, 
                                     relation=relation_type)
            
            # Calculate centrality scores
            try:
                centrality_scores = nx.pagerank(graph)
                authority_score = sum(centrality_scores.values()) / len(centrality_scores) if centrality_scores else 0.0
            except:
                centrality_scores = {node: 0.5 for node in nodes.keys()}
                authority_score = 0.5
            
            # Find semantic paths
            semantic_paths = []
            try:
                for source in list(graph.nodes())[:5]:  # Limit for performance
                    for target in list(graph.nodes())[:5]:
                        if source != target and graph.has_node(source) and graph.has_node(target):
                            try:
                                path = nx.shortest_path(graph, source, target)
                                if len(path) <= 4:  # Only short meaningful paths
                                    semantic_paths.append(path)
                            except nx.NetworkXNoPath:
                                continue
            except Exception as e:
                logger.warning(f"Error finding semantic paths: {e}")
            
            return KnowledgeGraph(
                nodes=nodes,
                edges=edges,
                centrality_scores=centrality_scores,
                semantic_paths=semantic_paths,
                authority_score=authority_score
            )
            
        except Exception as e:
            logger.error(f"Knowledge graph generation failed: {e}")
            # Return empty graph on failure
            return KnowledgeGraph(
                nodes={}, edges=[], centrality_scores={}, 
                semantic_paths=[], authority_score=0.0
            )

    async def extract_semantic_entities(self, content: str) -> List[Entity]:
        """Extract semantic entities from content.
        
        Args:
            content: Content to analyze
            
        Returns:
            List of extracted entities
        """
        if content in self._entity_cache:
            return self._entity_cache[content]
            
        try:
            if not self.nlp:
                await self.initialize_models()
                
            doc = self.nlp(content)
            entities = []
            
            for ent in doc.ents[:self.max_entities]:  # Limit entities for performance
                entity = Entity(
                    text=ent.text,
                    label=ent.label_,
                    confidence=1.0,  # spaCy doesn't provide confidence scores directly
                    start_pos=ent.start_char,
                    end_pos=ent.end_char,
                    semantic_type=self._get_semantic_type(ent.label_),
                    relations=[]
                )
                entities.append(entity)
            
            # Cache entities
            self._entity_cache[content] = entities
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []

    async def optimize_knowledge_graph(self, entities: List[Entity]) -> KnowledgeGraph:
        """Optimize knowledge graph for better semantic understanding.
        
        Args:
            entities: List of entities to optimize
            
        Returns:
            Optimized KnowledgeGraph
        """
        try:
            # Generate base knowledge graph
            base_graph = await self.generate_entity_graph(entities)
            
            # Optimize graph structure
            optimized_nodes = await self._optimize_graph_nodes(base_graph.nodes)
            optimized_edges = await self._optimize_graph_edges(base_graph.edges, base_graph.centrality_scores)
            
            # Recalculate metrics
            graph = nx.DiGraph()
            for node_id, node_data in optimized_nodes.items():
                graph.add_node(node_id, **node_data)
                
            for edge in optimized_edges:
                graph.add_edge(edge[0], edge[1], relation=edge[2])
            
            try:
                centrality_scores = nx.pagerank(graph)
                authority_score = sum(centrality_scores.values()) / len(centrality_scores) if centrality_scores else 0.0
            except:
                centrality_scores = {node: 0.5 for node in optimized_nodes.keys()}
                authority_score = 0.5
            
            return KnowledgeGraph(
                nodes=optimized_nodes,
                edges=optimized_edges,
                centrality_scores=centrality_scores,
                semantic_paths=base_graph.semantic_paths,
                authority_score=authority_score
            )
            
        except Exception as e:
            logger.error(f"Knowledge graph optimization failed: {e}")
            return await self.generate_entity_graph(entities)

    async def semantic_similarity_analysis(self, content: str, queries: List[str]) -> np.ndarray:
        """Analyze semantic similarity between content and search queries.
        
        Args:
            content: Content to analyze
            queries: List of search queries
            
        Returns:
            Similarity matrix as numpy array
        """
        try:
            # Generate embeddings for content and queries
            content_embedding = await self._generate_embeddings(content)
            query_embeddings = []
            
            for query in queries:
                query_embedding = await self._generate_embeddings(query)
                query_embeddings.append(query_embedding)
            
            if not query_embeddings:
                return np.array([[0.0]])
            
            # Calculate similarity matrix
            similarities = []
            for query_embedding in query_embeddings:
                similarity = cosine_similarity(
                    content_embedding.reshape(1, -1),
                    query_embedding.reshape(1, -1)
                )[0][0]
                similarities.append(similarity)
            
            return np.array(similarities).reshape(-1, 1)
            
        except Exception as e:
            logger.error(f"Semantic similarity analysis failed: {e}")
            return np.array([[0.0]])

    async def contextual_relevance_scoring(self, content: str, context: Optional[Dict[str, Any]] = None) -> RelevanceScore:
        """Score contextual relevance of content.
        
        Args:
            content: Content to score
            context: Optional context information
            
        Returns:
            RelevanceScore with detailed metrics
        """
        try:
            context = context or {}
            
            # Extract entities for relevance analysis
            entities = await self.extract_semantic_entities(content)
            
            # Calculate content relevance
            content_relevance = await self._calculate_content_relevance(content, entities)
            
            # Calculate entity relevance
            entity_relevance = await self._calculate_entity_relevance(entities, context)
            
            # Calculate semantic coherence
            semantic_coherence = await self._calculate_semantic_coherence(content, entities)
            
            # Calculate intent alignment
            intent_scores = await self._analyze_search_intent(content)
            intent_alignment = max(intent_scores.values()) if intent_scores else 0.0
            
            # Calculate overall score
            weights = {
                'content': 0.3,
                'entity': 0.25,
                'coherence': 0.25,
                'intent': 0.2
            }
            
            overall_score = (
                content_relevance * weights['content'] +
                entity_relevance * weights['entity'] +
                semantic_coherence * weights['coherence'] +
                intent_alignment * weights['intent']
            )
            
            # Generate improvement suggestions
            suggestions = await self._generate_relevance_suggestions(
                content_relevance, entity_relevance, semantic_coherence, intent_alignment
            )
            
            return RelevanceScore(
                content_relevance=content_relevance,
                entity_relevance=entity_relevance,
                semantic_coherence=semantic_coherence,
                intent_alignment=intent_alignment,
                overall_score=overall_score,
                improvement_suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Contextual relevance scoring failed: {e}")
            return RelevanceScore(0.0, 0.0, 0.0, 0.0, 0.0, [])

    # Private helper methods

    async def _generate_embeddings(self, text: str) -> np.ndarray:
        """Generate semantic embeddings for text."""
        if text in self._embedding_cache:
            return self._embedding_cache[text]
            
        try:
            if not self.model or not self.tokenizer:
                await self.initialize_models()
                
            # Tokenize and encode
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True, 
                                  padding=True, max_length=512)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            
            # Cache embeddings
            self._embedding_cache[text] = embeddings
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return np.zeros(384)  # Default embedding size

    async def _compute_similarity_matrix(self, content: str, keywords: List[str]) -> np.ndarray:
        """Compute similarity matrix between content and keywords."""
        try:
            if not keywords:
                return np.array([[1.0]])
                
            content_embedding = await self._generate_embeddings(content)
            similarities = []
            
            for keyword in keywords:
                keyword_embedding = await self._generate_embeddings(keyword)
                similarity = cosine_similarity(
                    content_embedding.reshape(1, -1),
                    keyword_embedding.reshape(1, -1)
                )[0][0]
                similarities.append(similarity)
            
            return np.array(similarities).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Similarity matrix computation failed: {e}")
            return np.array([[0.0]])

    async def _analyze_search_intent(self, content: str) -> Dict[SearchIntent, float]:
        """Analyze search intent alignment of content."""
        try:
            intent_keywords = {
                SearchIntent.INFORMATIONAL: ['what', 'how', 'why', 'guide', 'tutorial', 'learn'],
                SearchIntent.NAVIGATIONAL: ['login', 'contact', 'about', 'home', 'website'],
                SearchIntent.TRANSACTIONAL: ['buy', 'purchase', 'order', 'download', 'get'],
                SearchIntent.COMMERCIAL: ['best', 'review', 'compare', 'vs', 'top', 'price'],
                SearchIntent.LOCAL: ['near', 'location', 'address', 'local', 'nearby']
            }
            
            content_lower = content.lower()
            intent_scores = {}
            
            for intent, keywords in intent_keywords.items():
                score = sum(1 for keyword in keywords if keyword in content_lower)
                intent_scores[intent] = min(score / len(keywords), 1.0)
            
            return intent_scores
            
        except Exception as e:
            logger.error(f"Search intent analysis failed: {e}")
            return {intent: 0.0 for intent in SearchIntent}

    async def _extract_semantic_keywords(self, content: str, entities: List[Entity]) -> List[str]:
        """Extract semantic keywords from content and entities."""
        try:
            keywords = set()
            
            # Add entity texts as keywords
            for entity in entities:
                if len(entity.text.split()) <= 3:  # Only short phrases
                    keywords.add(entity.text.lower())
            
            # Extract important terms using TF-IDF
            try:
                vectorizer = TfidfVectorizer(max_features=20, stop_words='english', 
                                           ngram_range=(1, 2))
                tfidf_matrix = vectorizer.fit_transform([content])
                feature_names = vectorizer.get_feature_names_out()
                scores = tfidf_matrix.toarray()[0]
                
                # Get top terms
                for i, score in enumerate(scores):
                    if score > 0.1:  # Threshold for relevance
                        keywords.add(feature_names[i])
                        
            except Exception as e:
                logger.warning(f"TF-IDF extraction failed: {e}")
            
            return list(keywords)[:30]  # Limit keywords
            
        except Exception as e:
            logger.error(f"Semantic keyword extraction failed: {e}")
            return []

    async def _optimize_semantic_structure(self, content: str, entities: List[Entity], 
                                         keywords: List[str], intent_alignment: Dict[SearchIntent, float]) -> str:
        """Optimize content structure for semantic understanding."""
        try:
            optimized_content = content
            
            # Add semantic structure improvements
            if intent_alignment.get(SearchIntent.INFORMATIONAL, 0) > 0.5:
                # Add informational structure
                if not any(word in content.lower() for word in ['introduction', 'overview', 'summary']):
                    optimized_content = f"## Overview\n\n{optimized_content}"
            
            # Enhance entity mentions
            for entity in entities[:10]:  # Limit processing
                if entity.confidence > 0.8 and entity.text not in optimized_content:
                    # Add context for important entities
                    optimized_content = optimized_content.replace(
                        entity.text,
                        f"**{entity.text}**",
                        1  # Only first occurrence
                    )
            
            return optimized_content
            
        except Exception as e:
            logger.error(f"Semantic structure optimization failed: {e}")
            return content

    async def _calculate_semantic_score(self, original: str, optimized: str, 
                                      entities: List[Entity], intent_alignment: Dict[SearchIntent, float]) -> float:
        """Calculate overall semantic optimization score."""
        try:
            # Entity density score
            entity_score = min(len(entities) / 20, 1.0)  # Normalize to 0-1
            
            # Intent alignment score
            intent_score = max(intent_alignment.values()) if intent_alignment else 0.0
            
            # Content enhancement score
            enhancement_score = len(optimized) / max(len(original), 1)
            enhancement_score = min(max(enhancement_score - 1, 0) * 2, 1.0)  # Normalize improvement
            
            # Weighted final score
            final_score = (entity_score * 0.4 + intent_score * 0.4 + enhancement_score * 0.2)
            
            return min(final_score, 1.0)
            
        except Exception as e:
            logger.error(f"Semantic score calculation failed: {e}")
            return 0.0

    async def _generate_context_suggestions(self, content: str, entities: List[Entity], 
                                          keywords: List[str]) -> List[str]:
        """Generate context-aware optimization suggestions."""
        try:
            suggestions = []
            
            # Entity-based suggestions
            if len(entities) < 5:
                suggestions.append("Add more relevant entities and named mentions to improve semantic understanding")
            
            # Keyword suggestions
            if len(keywords) < 10:
                suggestions.append("Include more semantic keywords and related terms")
            
            # Structure suggestions
            if not re.search(r'#{1,3}\s', content):
                suggestions.append("Add semantic headings (H1-H3) to improve content structure")
            
            # Length suggestions
            if len(content.split()) < 300:
                suggestions.append("Expand content length for better semantic coverage")
            
            return suggestions[:5]  # Limit suggestions
            
        except Exception as e:
            logger.error(f"Context suggestions generation failed: {e}")
            return []

    def _get_semantic_type(self, entity_label: str) -> str:
        """Get semantic type for entity label."""
        type_mapping = {
            'PERSON': 'person',
            'ORG': 'organization',
            'GPE': 'location',
            'DATE': 'temporal',
            'MONEY': 'financial',
            'PRODUCT': 'product',
            'EVENT': 'event'
        }
        return type_mapping.get(entity_label, 'general')

    async def _calculate_entity_relationship(self, entity1: Entity, entity2: Entity) -> float:
        """Calculate semantic relationship strength between entities."""
        try:
            # Same type entities have higher relationship
            if entity1.semantic_type == entity2.semantic_type:
                base_score = 0.6
            else:
                base_score = 0.3
            
            # Proximity bonus
            distance = abs(entity1.start_pos - entity2.start_pos)
            proximity_score = max(0, 1 - distance / 1000)  # Normalize distance
            
            return min(base_score + proximity_score * 0.4, 1.0)
            
        except Exception:
            return 0.3  # Default relationship strength

    def _determine_relation_type(self, entity1: Entity, entity2: Entity) -> str:
        """Determine relationship type between entities."""
        if entity1.semantic_type == entity2.semantic_type:
            return 'similar_type'
        elif entity1.semantic_type == 'person' and entity2.semantic_type == 'organization':
            return 'person_org'
        elif entity1.semantic_type == 'organization' and entity2.semantic_type == 'location':
            return 'org_location'
        else:
            return 'related'

    async def _optimize_graph_nodes(self, nodes: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Optimize knowledge graph nodes."""
        # For now, return nodes as-is. Can be enhanced with node filtering/merging
        return nodes

    async def _optimize_graph_edges(self, edges: List[Tuple[str, str, str]], 
                                  centrality_scores: Dict[str, float]) -> List[Tuple[str, str, str]]:
        """Optimize knowledge graph edges."""
        # Filter edges based on centrality scores
        optimized_edges = []
        for edge in edges:
            source_score = centrality_scores.get(edge[0], 0.0)
            target_score = centrality_scores.get(edge[1], 0.0)
            if source_score > 0.1 or target_score > 0.1:  # Keep important connections
                optimized_edges.append(edge)
        return optimized_edges

    async def _calculate_content_relevance(self, content: str, entities: List[Entity]) -> float:
        """Calculate content relevance score."""
        try:
            # Based on content length, structure, and entity density
            word_count = len(content.split())
            entity_density = len(entities) / max(word_count, 1) * 100
            
            # Optimal entity density is around 2-5%
            if 2 <= entity_density <= 5:
                density_score = 1.0
            else:
                density_score = max(0, 1 - abs(entity_density - 3.5) / 3.5)
            
            # Content structure score
            structure_score = 0.5
            if re.search(r'#{1,3}\s', content):
                structure_score += 0.3
            if word_count >= 300:
                structure_score += 0.2
            
            return min((density_score + structure_score) / 2, 1.0)
            
        except Exception:
            return 0.5

    async def _calculate_entity_relevance(self, entities: List[Entity], context: Dict[str, Any]) -> float:
        """Calculate entity relevance score."""
        try:
            if not entities:
                return 0.0
            
            # Score based on entity types and confidence
            type_scores = {
                'person': 0.8,
                'organization': 0.9,
                'location': 0.7,
                'product': 0.9,
                'event': 0.6
            }
            
            total_score = 0
            for entity in entities:
                type_score = type_scores.get(entity.semantic_type, 0.5)
                total_score += type_score * entity.confidence
            
            return min(total_score / len(entities), 1.0)
            
        except Exception:
            return 0.5

    async def _calculate_semantic_coherence(self, content: str, entities: List[Entity]) -> float:
        """Calculate semantic coherence score."""
        try:
            # Check for semantic consistency in entity usage
            entity_types = [entity.semantic_type for entity in entities]
            type_diversity = len(set(entity_types)) / max(len(entity_types), 1)
            
            # Optimal diversity is moderate (not too scattered, not too narrow)
            if 0.3 <= type_diversity <= 0.7:
                diversity_score = 1.0
            else:
                diversity_score = max(0, 1 - abs(type_diversity - 0.5) / 0.5)
            
            return diversity_score
            
        except Exception:
            return 0.5

    async def _generate_relevance_suggestions(self, content_rel: float, entity_rel: float, 
                                            coherence: float, intent_align: float) -> List[str]:
        """Generate suggestions based on relevance scores."""
        suggestions = []
        
        if content_rel < 0.6:
            suggestions.append("Improve content structure with clear headings and sections")
        
        if entity_rel < 0.6:
            suggestions.append("Add more relevant entities and proper nouns")
        
        if coherence < 0.6:
            suggestions.append("Ensure semantic consistency across entity types")
        
        if intent_align < 0.6:
            suggestions.append("Align content better with target search intent")
        
        return suggestions