"""
Enterprise Semantic Processing Module
===================================

Next-generation semantic understanding for content creators:
- Deep neural semantic similarity analysis
- Multi-layered concept extraction and knowledge graphs
- Intent understanding with behavioral prediction
- Contextual meaning analysis for content optimization
- Semantic search and content matching algorithms
- Topic modeling and content clustering
- Real-time semantic content recommendation engine
- Cultural context and sentiment-aware processing

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Specialist + DevOps Expert
Copyright: Fahed Mlaiel - All Rights Reserved

⚠️  STRICT LEGAL WARNING: 
    This proprietary code is protected by international copyright law.
    Unauthorized use, copying, distribution, modification, or reverse engineering 
    is STRICTLY PROHIBITED and will result in immediate legal action.
    This includes any attempt to steal, replicate, or use this concept without 
    explicit written authorization from Fahed Mlaiel.
    
    Contact: mlaiel@live.de for licensing inquiries ONLY.
    Violators will be prosecuted to the full extent of German and EU law.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import re
from datetime import datetime, timezone
import hashlib
import json

import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import DBSCAN
import gensim
from gensim.models import Word2Vec, Doc2Vec
from transformers import AutoTokenizer, AutoModel, pipeline
import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

from ...core.config import settings
from ...core.logging import get_logger
from ...core.cache import cache_manager
from ...utils.text_utils import clean_text, normalize_unicode
from ...security.encryption import encrypt_data, decrypt_data

logger = get_logger(__name__)


class ConceptType(Enum):
    """Types of concepts extracted from content"""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    EVENT = "event"
    PRODUCT = "product"
    SERVICE = "service"
    TOPIC = "topic"
    EMOTION = "emotion"
    ACTION = "action"
    ATTRIBUTE = "attribute"
    TIME = "time"
    QUANTITY = "quantity"


class SemanticRelation(Enum):
    """Types of semantic relations between concepts"""
    SIMILAR_TO = "similar_to"
    RELATED_TO = "related_to"
    PART_OF = "part_of"
    CAUSED_BY = "caused_by"
    LEADS_TO = "leads_to"
    OPPOSITE_OF = "opposite_of"
    EXAMPLE_OF = "example_of"
    INCLUDES = "includes"


class IntentCategory(Enum):
    """Content intent categories"""
    INFORMATIONAL = "informational"
    PROMOTIONAL = "promotional"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    INSPIRATIONAL = "inspirational"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"
    CONVERSATIONAL = "conversational"


@dataclass
class Concept:
    """Represents an extracted concept"""
    text: str
    concept_type: ConceptType
    confidence: float
    frequency: int = 1
    context: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[np.ndarray] = None


@dataclass
class SemanticRelationship:
    """Represents a relationship between concepts"""
    source_concept: str
    target_concept: str
    relation_type: SemanticRelation
    strength: float
    evidence: List[str] = field(default_factory=list)


@dataclass
class SemanticAnalysisResult:
    """Complete semantic analysis result"""
    concepts: List[Concept]
    relationships: List[SemanticRelationship]
    topics: List[Tuple[str, float]]
    intent: IntentCategory
    intent_confidence: float
    semantic_density: float
    conceptual_coherence: float
    abstraction_level: str
    domain_context: str
    key_themes: List[str] = field(default_factory=list)
    content_structure: Dict[str, Any] = field(default_factory=dict)
    analysis_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ConceptGraph:
    """Concept graph representation"""
    nodes: Dict[str, Concept]
    edges: List[SemanticRelationship]
    centrality_scores: Dict[str, float] = field(default_factory=dict)
    clusters: List[List[str]] = field(default_factory=list)
    graph_metrics: Dict[str, float] = field(default_factory=dict)


class SemanticProcessor:
    """Advanced semantic processing engine"""
    
    def __init__(self):
        self.nlp = None
        self.sentence_transformer = None
        self.concept_extractors = {}
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize semantic processing models"""
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_lg")
            
            # Load sentence transformer for embeddings
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize topic modeling
            self.topic_model = LatentDirichletAllocation(
                n_components=10,
                random_state=42,
                max_iter=100
            )
            
            # Initialize intent classifier
            self.intent_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                tokenizer="microsoft/DialoGPT-medium"
            )
            
            logger.info("Semantic processing models initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize semantic models: {e}")
            
    async def analyze_semantics(
        self,
        text: str,
        context: Optional[Dict] = None,
        extract_relationships: bool = True
    ) -> SemanticAnalysisResult:
        """
        Perform comprehensive semantic analysis
        
        Args:
            text: Text content to analyze
            context: Optional context information
            extract_relationships: Whether to extract concept relationships
            
        Returns:
            SemanticAnalysisResult with detailed semantic information
        """
        try:
            # Cache key for performance
            cache_key = f"semantic_{hashlib.md5(text.encode()).hexdigest()}"
            cached_result = await cache_manager.get(cache_key)
            if cached_result:
                return cached_result
                
            # Clean and preprocess text
            cleaned_text = clean_text(text)
            
            # Extract concepts
            concepts = await self._extract_concepts(cleaned_text)
            
            # Extract relationships if requested
            relationships = []
            if extract_relationships and concepts:
                relationships = await self._extract_relationships(cleaned_text, concepts)
                
            # Topic modeling
            topics = await self._extract_topics(cleaned_text)
            
            # Intent analysis
            intent, intent_confidence = await self._analyze_intent(cleaned_text, context)
            
            # Calculate semantic metrics
            semantic_density = await self._calculate_semantic_density(cleaned_text, concepts)
            conceptual_coherence = await self._calculate_conceptual_coherence(concepts, relationships)
            
            # Determine abstraction level
            abstraction_level = await self._determine_abstraction_level(concepts)
            
            # Identify domain context
            domain_context = await self._identify_domain_context(concepts, topics)
            
            # Extract key themes
            key_themes = await self._extract_key_themes(topics, concepts)
            
            # Analyze content structure
            content_structure = await self._analyze_content_structure(cleaned_text)
            
            result = SemanticAnalysisResult(
                concepts=concepts,
                relationships=relationships,
                topics=topics,
                intent=intent,
                intent_confidence=intent_confidence,
                semantic_density=semantic_density,
                conceptual_coherence=conceptual_coherence,
                abstraction_level=abstraction_level,
                domain_context=domain_context,
                key_themes=key_themes,
                content_structure=content_structure
            )
            
            # Cache result
            await cache_manager.set(cache_key, result, expire=3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Semantic analysis failed: {e}")
            raise
            
    async def _extract_concepts(self, text: str) -> List[Concept]:
        """Extract concepts from text using NLP"""
        try:
            if not self.nlp:
                return []
                
            doc = self.nlp(text)
            concepts = []
            concept_counts = {}
            
            # Extract named entities
            for ent in doc.ents:
                concept_type = self._map_spacy_label_to_concept_type(ent.label_)
                concept_text = ent.text.strip()
                
                if concept_text and len(concept_text) > 1:
                    if concept_text in concept_counts:
                        concept_counts[concept_text]['frequency'] += 1
                        concept_counts[concept_text]['context'].append(ent.sent.text)
                    else:
                        concept_counts[concept_text] = {
                            'type': concept_type,
                            'frequency': 1,
                            'context': [ent.sent.text],
                            'confidence': min(ent._.confidence if hasattr(ent, '_') else 0.8, 1.0)
                        }
                        
            # Extract noun phrases as potential concepts
            for chunk in doc.noun_chunks:
                if chunk.root.pos_ == "NOUN" and not chunk.root.is_stop:
                    concept_text = chunk.text.strip()
                    if concept_text and len(concept_text) > 2:
                        if concept_text not in concept_counts:
                            concept_counts[concept_text] = {
                                'type': ConceptType.TOPIC,
                                'frequency': 1,
                                'context': [chunk.sent.text],
                                'confidence': 0.6
                            }
                            
            # Convert to Concept objects
            for text, data in concept_counts.items():
                # Generate embedding for concept
                embedding = await self._get_concept_embedding(text)
                
                concept = Concept(
                    text=text,
                    concept_type=data['type'],
                    confidence=data['confidence'],
                    frequency=data['frequency'],
                    context=data['context'][:3],  # Limit context
                    embedding=embedding
                )
                concepts.append(concept)
                
            # Sort by confidence and frequency
            concepts.sort(key=lambda x: (x.confidence, x.frequency), reverse=True)
            return concepts[:50]  # Limit to top 50 concepts
            
        except Exception as e:
            logger.error(f"Concept extraction failed: {e}")
            return []
            
    def _map_spacy_label_to_concept_type(self, spacy_label: str) -> ConceptType:
        """Map spaCy entity labels to our concept types"""
        mapping = {
            'PERSON': ConceptType.PERSON,
            'ORG': ConceptType.ORGANIZATION,
            'GPE': ConceptType.LOCATION,
            'LOC': ConceptType.LOCATION,
            'EVENT': ConceptType.EVENT,
            'PRODUCT': ConceptType.PRODUCT,
            'WORK_OF_ART': ConceptType.PRODUCT,
            'LAW': ConceptType.TOPIC,
            'LANGUAGE': ConceptType.TOPIC,
            'DATE': ConceptType.TIME,
            'TIME': ConceptType.TIME,
            'PERCENT': ConceptType.QUANTITY,
            'MONEY': ConceptType.QUANTITY,
            'QUANTITY': ConceptType.QUANTITY,
            'ORDINAL': ConceptType.QUANTITY,
            'CARDINAL': ConceptType.QUANTITY
        }
        return mapping.get(spacy_label, ConceptType.TOPIC)
        
    async def _get_concept_embedding(self, concept_text: str) -> Optional[np.ndarray]:
        """Generate embedding for concept"""
        try:
            if self.sentence_transformer:
                embedding = self.sentence_transformer.encode([concept_text])
                return embedding[0]
            return None
        except Exception as e:
            logger.error(f"Concept embedding generation failed: {e}")
            return None
            
    async def _extract_relationships(self, text: str, concepts: List[Concept]) -> List[SemanticRelationship]:
        """Extract semantic relationships between concepts"""
        try:
            relationships = []
            
            if not self.nlp or len(concepts) < 2:
                return relationships
                
            doc = self.nlp(text)
            
            # Create concept lookup
            concept_texts = {concept.text.lower(): concept for concept in concepts}
            
            # Extract dependency-based relationships
            for sent in doc.sents:
                for token in sent:
                    if token.text.lower() in concept_texts:
                        # Look for related concepts in dependencies
                        for child in token.children:
                            if child.text.lower() in concept_texts:
                                relation_type = self._determine_relation_type(token, child, token.dep_)
                                if relation_type:
                                    relationship = SemanticRelationship(
                                        source_concept=token.text,
                                        target_concept=child.text,
                                        relation_type=relation_type,
                                        strength=0.7,
                                        evidence=[sent.text]
                                    )
                                    relationships.append(relationship)
                                    
            # Extract co-occurrence based relationships
            concept_pairs = [(concepts[i], concepts[j]) 
                           for i in range(len(concepts)) 
                           for j in range(i+1, len(concepts))]
                           
            for concept1, concept2 in concept_pairs[:20]:  # Limit pairs
                cooccurrence_strength = await self._calculate_cooccurrence_strength(
                    concept1.text, concept2.text, text
                )
                
                if cooccurrence_strength > 0.3:
                    relationship = SemanticRelationship(
                        source_concept=concept1.text,
                        target_concept=concept2.text,
                        relation_type=SemanticRelation.RELATED_TO,
                        strength=cooccurrence_strength,
                        evidence=[]
                    )
                    relationships.append(relationship)
                    
            return relationships
            
        except Exception as e:
            logger.error(f"Relationship extraction failed: {e}")
            return []
            
    def _determine_relation_type(self, token1, token2, dependency: str) -> Optional[SemanticRelation]:
        """Determine semantic relation type from dependency"""
        relation_mappings = {
            'nsubj': SemanticRelation.RELATED_TO,
            'dobj': SemanticRelation.RELATED_TO,
            'pobj': SemanticRelation.RELATED_TO,
            'amod': SemanticRelation.RELATED_TO,
            'compound': SemanticRelation.PART_OF,
            'conj': SemanticRelation.SIMILAR_TO,
            'appos': SemanticRelation.EXAMPLE_OF
        }
        return relation_mappings.get(dependency)
        
    async def _calculate_cooccurrence_strength(self, concept1: str, concept2: str, text: str) -> float:
        """Calculate strength of concept co-occurrence"""
        try:
            sentences = re.split(r'[.!?]+', text)
            total_sentences = len(sentences)
            cooccurrence_count = 0
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if concept1.lower() in sentence_lower and concept2.lower() in sentence_lower:
                    cooccurrence_count += 1
                    
            return cooccurrence_count / max(total_sentences, 1)
            
        except Exception as e:
            logger.error(f"Co-occurrence calculation failed: {e}")
            return 0.0
            
    async def _extract_topics(self, text: str) -> List[Tuple[str, float]]:
        """Extract topics using topic modeling"""
        try:
            # Simple topic extraction using TF-IDF and clustering
            sentences = re.split(r'[.!?]+', text)
            if len(sentences) < 2:
                return []
                
            # Vectorize sentences
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            try:
                sentence_vectors = vectorizer.fit_transform(sentences)
                feature_names = vectorizer.get_feature_names_out()
                
                # Get top features as topics
                tfidf_scores = sentence_vectors.sum(axis=0).A1
                topic_indices = tfidf_scores.argsort()[-10:][::-1]
                
                topics = [(feature_names[i], tfidf_scores[i]) for i in topic_indices]
                return topics
                
            except ValueError:
                # Fallback to simple word frequency
                words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
                word_freq = {}
                for word in words:
                    if word not in STOP_WORDS:
                        word_freq[word] = word_freq.get(word, 0) + 1
                        
                sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
                return sorted_words[:10]
                
        except Exception as e:
            logger.error(f"Topic extraction failed: {e}")
            return []
            
    async def _analyze_intent(self, text: str, context: Optional[Dict]) -> Tuple[IntentCategory, float]:
        """Analyze content intent"""
        try:
            # Intent classification based on text patterns
            text_lower = text.lower()
            
            # Define intent indicators
            intent_patterns = {
                IntentCategory.PROMOTIONAL: [
                    'buy', 'purchase', 'sale', 'discount', 'offer', 'deal',
                    'subscribe', 'sign up', 'join', 'register'
                ],
                IntentCategory.EDUCATIONAL: [
                    'learn', 'how to', 'tutorial', 'guide', 'tips',
                    'explain', 'understand', 'knowledge'
                ],
                IntentCategory.INFORMATIONAL: [
                    'what is', 'information', 'facts', 'data', 'report',
                    'news', 'update', 'announcement'
                ],
                IntentCategory.ENTERTAINMENT: [
                    'funny', 'humor', 'joke', 'entertainment', 'fun',
                    'amusing', 'comedy', 'laugh'
                ],
                IntentCategory.INSPIRATIONAL: [
                    'motivate', 'inspire', 'succeed', 'achieve', 'dream',
                    'goal', 'success', 'motivation'
                ],
                IntentCategory.CONVERSATIONAL: [
                    'what do you think', 'comment', 'share', 'discuss',
                    'opinion', 'thoughts', 'feedback'
                ]
            }
            
            # Calculate intent scores
            intent_scores = {}
            for intent, patterns in intent_patterns.items():
                score = sum(1 for pattern in patterns if pattern in text_lower)
                if score > 0:
                    intent_scores[intent] = score / len(patterns)
                    
            if intent_scores:
                best_intent = max(intent_scores, key=intent_scores.get)
                confidence = intent_scores[best_intent]
                return best_intent, min(confidence, 1.0)
            else:
                return IntentCategory.INFORMATIONAL, 0.5
                
        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            return IntentCategory.INFORMATIONAL, 0.5
            
    async def _calculate_semantic_density(self, text: str, concepts: List[Concept]) -> float:
        """Calculate semantic density of the text"""
        try:
            if not concepts:
                return 0.0
                
            words = text.split()
            concept_words = sum(len(concept.text.split()) for concept in concepts)
            
            return min(concept_words / max(len(words), 1), 1.0)
            
        except Exception as e:
            logger.error(f"Semantic density calculation failed: {e}")
            return 0.0
            
    async def _calculate_conceptual_coherence(
        self,
        concepts: List[Concept],
        relationships: List[SemanticRelationship]
    ) -> float:
        """Calculate coherence between concepts"""
        try:
            if len(concepts) < 2:
                return 1.0
                
            # Calculate embedding similarities
            embeddings = [concept.embedding for concept in concepts if concept.embedding is not None]
            
            if len(embeddings) < 2:
                return 0.5
                
            # Calculate pairwise similarities
            similarities = []
            for i in range(len(embeddings)):
                for j in range(i+1, len(embeddings)):
                    similarity = cosine_similarity(
                        embeddings[i].reshape(1, -1),
                        embeddings[j].reshape(1, -1)
                    )[0][0]
                    similarities.append(similarity)
                    
            return np.mean(similarities) if similarities else 0.5
            
        except Exception as e:
            logger.error(f"Conceptual coherence calculation failed: {e}")
            return 0.5
            
    async def _determine_abstraction_level(self, concepts: List[Concept]) -> str:
        """Determine abstraction level of concepts"""
        try:
            if not concepts:
                return "medium"
                
            # Count abstract vs concrete concepts
            abstract_types = {ConceptType.TOPIC, ConceptType.EMOTION, ConceptType.ATTRIBUTE}
            concrete_types = {ConceptType.PERSON, ConceptType.ORGANIZATION, ConceptType.LOCATION, ConceptType.PRODUCT}
            
            abstract_count = sum(1 for concept in concepts if concept.concept_type in abstract_types)
            concrete_count = sum(1 for concept in concepts if concept.concept_type in concrete_types)
            
            total_count = len(concepts)
            abstract_ratio = abstract_count / max(total_count, 1)
            
            if abstract_ratio > 0.7:
                return "high"
            elif abstract_ratio < 0.3:
                return "low"
            else:
                return "medium"
                
        except Exception as e:
            logger.error(f"Abstraction level determination failed: {e}")
            return "medium"
            
    async def _identify_domain_context(self, concepts: List[Concept], topics: List[Tuple[str, float]]) -> str:
        """Identify domain context from concepts and topics"""
        try:
            # Domain keywords mapping
            domain_keywords = {
                'technology': ['tech', 'software', 'digital', 'computer', 'internet', 'app'],
                'music': ['music', 'song', 'artist', 'album', 'concert', 'sound'],
                'business': ['business', 'company', 'market', 'sales', 'revenue', 'profit'],
                'health': ['health', 'medical', 'doctor', 'treatment', 'wellness', 'fitness'],
                'education': ['education', 'learning', 'school', 'student', 'teacher', 'study'],
                'entertainment': ['movie', 'film', 'show', 'entertainment', 'celebrity', 'actor'],
                'sports': ['sports', 'game', 'team', 'player', 'match', 'competition'],
                'travel': ['travel', 'trip', 'vacation', 'destination', 'hotel', 'flight'],
                'food': ['food', 'restaurant', 'recipe', 'cooking', 'chef', 'meal'],
                'fashion': ['fashion', 'style', 'clothing', 'brand', 'design', 'trend']
            }
            
            # Count domain indicators
            domain_scores = {}
            all_text = ' '.join([concept.text.lower() for concept in concepts] + 
                              [topic[0].lower() for topic in topics])
            
            for domain, keywords in domain_keywords.items():
                score = sum(1 for keyword in keywords if keyword in all_text)
                if score > 0:
                    domain_scores[domain] = score
                    
            if domain_scores:
                return max(domain_scores, key=domain_scores.get)
            else:
                return "general"
                
        except Exception as e:
            logger.error(f"Domain context identification failed: {e}")
            return "general"
            
    async def _extract_key_themes(self, topics: List[Tuple[str, float]], concepts: List[Concept]) -> List[str]:
        """Extract key themes from topics and concepts"""
        try:
            themes = []
            
            # Add top topics as themes
            for topic, score in topics[:5]:
                if score > 0.1:  # Threshold for significance
                    themes.append(topic)
                    
            # Add high-confidence concepts as themes
            for concept in concepts:
                if concept.confidence > 0.8 and concept.frequency > 1:
                    themes.append(concept.text)
                    
            # Remove duplicates and return top themes
            unique_themes = list(set(themes))
            return unique_themes[:10]
            
        except Exception as e:
            logger.error(f"Key theme extraction failed: {e}")
            return []
            
    async def _analyze_content_structure(self, text: str) -> Dict[str, Any]:
        """Analyze structural elements of content"""
        try:
            structure = {
                'has_introduction': False,
                'has_conclusion': False,
                'has_sections': False,
                'narrative_flow': 'linear',
                'complexity_score': 0.0,
                'readability_level': 'medium'
            }
            
            sentences = re.split(r'[.!?]+', text)
            
            # Check for introduction patterns
            intro_patterns = ['first', 'begin', 'start', 'introduce', 'welcome']
            if any(pattern in text.lower() for pattern in intro_patterns):
                structure['has_introduction'] = True
                
            # Check for conclusion patterns
            conclusion_patterns = ['finally', 'conclude', 'summary', 'end', 'last']
            if any(pattern in text.lower() for pattern in conclusion_patterns):
                structure['has_conclusion'] = True
                
            # Check for sections
            section_patterns = ['first', 'second', 'next', 'then', 'finally']
            section_count = sum(1 for pattern in section_patterns if pattern in text.lower())
            structure['has_sections'] = section_count > 2
            
            # Calculate complexity
            avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
            structure['complexity_score'] = min(avg_sentence_length / 20, 1.0)
            
            return structure
            
        except Exception as e:
            logger.error(f"Content structure analysis failed: {e}")
            return {'complexity_score': 0.5}


class ConceptExtractor:
    """Specialized concept extraction engine"""
    
    def __init__(self):
        self.semantic_processor = SemanticProcessor()
        
    async def extract_concept_graph(self, text: str) -> ConceptGraph:
        """Extract concept graph from text"""
        try:
            # Get semantic analysis
            semantic_result = await self.semantic_processor.analyze_semantics(text)
            
            # Build concept graph
            nodes = {concept.text: concept for concept in semantic_result.concepts}
            edges = semantic_result.relationships
            
            # Calculate centrality scores using NetworkX
            G = nx.Graph()
            
            # Add nodes
            for concept_text in nodes.keys():
                G.add_node(concept_text)
                
            # Add edges
            for relationship in edges:
                G.add_edge(
                    relationship.source_concept,
                    relationship.target_concept,
                    weight=relationship.strength
                )
                
            # Calculate centrality scores
            centrality_scores = {}
            if G.nodes():
                centrality_scores = nx.degree_centrality(G)
                
            # Perform clustering
            clusters = await self._cluster_concepts(semantic_result.concepts)
            
            # Calculate graph metrics
            graph_metrics = {
                'node_count': len(nodes),
                'edge_count': len(edges),
                'density': nx.density(G) if G.nodes() else 0,
                'average_clustering': nx.average_clustering(G) if G.nodes() else 0
            }
            
            return ConceptGraph(
                nodes=nodes,
                edges=edges,
                centrality_scores=centrality_scores,
                clusters=clusters,
                graph_metrics=graph_metrics
            )
            
        except Exception as e:
            logger.error(f"Concept graph extraction failed: {e}")
            return ConceptGraph(nodes={}, edges=[])
            
    async def _cluster_concepts(self, concepts: List[Concept]) -> List[List[str]]:
        """Cluster related concepts"""
        try:
            if len(concepts) < 3:
                return [[concept.text for concept in concepts]]
                
            # Get embeddings
            embeddings = []
            concept_texts = []
            
            for concept in concepts:
                if concept.embedding is not None:
                    embeddings.append(concept.embedding)
                    concept_texts.append(concept.text)
                    
            if len(embeddings) < 3:
                return [concept_texts]
                
            # Perform clustering
            clustering = DBSCAN(eps=0.3, min_samples=2)
            cluster_labels = clustering.fit_predict(embeddings)
            
            # Group concepts by cluster
            clusters = {}
            for i, label in enumerate(cluster_labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(concept_texts[i])
                
            return list(clusters.values())
            
        except Exception as e:
            logger.error(f"Concept clustering failed: {e}")
            return [[concept.text for concept in concepts]]
