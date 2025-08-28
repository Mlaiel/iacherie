"""
Semantic Processor - Advanced Semantic Understanding Engine
==========================================================

Advanced semantic processing system for deep text understanding,
meaning extraction, and contextual analysis using state-of-the-art NLP models.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import re
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    import torch.nn.functional as F
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers/SentenceTransformers not available. Semantic processing will use fallback methods.")

try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
    import scipy.spatial.distance as distance
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from .config import NLPAgentConfig, default_config

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class SemanticEntity:
    """Semantic entity with meaning and relationships"""
    text: str
    semantic_type: str
    confidence: float
    context: str
    relationships: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SemanticRelation:
    """Semantic relationship between entities"""
    subject: str
    predicate: str
    object: str
    confidence: float
    context: str

@dataclass
class ConceptualTheme:
    """High-level conceptual theme"""
    theme: str
    relevance_score: float
    supporting_evidence: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)

@dataclass
class SemanticResult:
    """Complete semantic processing result"""
    text: str
    main_concepts: List[str] = field(default_factory=list)
    semantic_entities: List[SemanticEntity] = field(default_factory=list)
    semantic_relations: List[SemanticRelation] = field(default_factory=list)
    conceptual_themes: List[ConceptualTheme] = field(default_factory=list)
    semantic_similarity_score: float = 0.0
    abstract_meaning: str = ""
    contextual_understanding: Dict[str, Any] = field(default_factory=dict)
    discourse_markers: List[str] = field(default_factory=list)
    logical_structure: Dict[str, Any] = field(default_factory=dict)
    semantic_density: float = 0.0
    coherence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class SemanticProcessor:
    """
    Advanced semantic processing system for deep text understanding,
    meaning extraction, and contextual analysis.
    """
    
    def __init__(self, config: Optional[NLPAgentConfig] = None):
        """Initialize Semantic Processor"""
        self.config = config or default_config
        self.models = {}
        self.embeddings_model = None
        self.semantic_patterns = self._load_semantic_patterns()
        self.concept_ontology = self._load_concept_ontology()
        
        self._initialize_models()
    
    def _load_semantic_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for semantic analysis"""
        return {
            "causal": [
                r"\bbecause\b", r"\bsince\b", r"\bas\b", r"\bdue to\b",
                r"\btherefore\b", r"\bthus\b", r"\bhence\b", r"\bso\b"
            ],
            "temporal": [
                r"\bbefore\b", r"\bafter\b", r"\bduring\b", r"\bwhile\b",
                r"\bwhen\b", r"\bthen\b", r"\bnext\b", r"\bfinally\b"
            ],
            "comparative": [
                r"\bbetter\b", r"\bworse\b", r"\bmore\b", r"\bless\b",
                r"\bsimilar\b", r"\bdifferent\b", r"\blike\b", r"\bunlike\b"
            ],
            "conditional": [
                r"\bif\b", r"\bunless\b", r"\bprovided\b", r"\bassuming\b",
                r"\bsuppose\b", r"\bwould\b", r"\bcould\b", r"\bmight\b"
            ],
            "emphasis": [
                r"\bespecially\b", r"\bparticularly\b", r"\bnotably\b",
                r"\bimportantly\b", r"\bsignificantly\b", r"\bclearly\b"
            ]
        }
    
    def _load_concept_ontology(self) -> Dict[str, Dict[str, Any]]:
        """Load conceptual ontology for semantic understanding"""
        return {
            "emotions": {
                "subconcepts": ["joy", "sadness", "anger", "fear", "surprise", "disgust"],
                "related": ["feelings", "mood", "sentiment", "psychology"],
                "attributes": ["intensity", "duration", "trigger"]
            },
            "actions": {
                "subconcepts": ["movement", "creation", "destruction", "communication"],
                "related": ["behavior", "activity", "performance", "execution"],
                "attributes": ["agent", "object", "method", "purpose"]
            },
            "objects": {
                "subconcepts": ["physical", "abstract", "digital", "conceptual"],
                "related": ["entities", "items", "things", "artifacts"],
                "attributes": ["properties", "function", "location", "state"]
            },
            "relationships": {
                "subconcepts": ["social", "professional", "familial", "romantic"],
                "related": ["connections", "bonds", "associations", "networks"],
                "attributes": ["strength", "type", "duration", "reciprocity"]
            },
            "time": {
                "subconcepts": ["past", "present", "future", "duration"],
                "related": ["temporal", "chronology", "sequence", "timing"],
                "attributes": ["moment", "period", "frequency", "order"]
            },
            "space": {
                "subconcepts": ["location", "direction", "distance", "dimension"],
                "related": ["geography", "position", "orientation", "scale"],
                "attributes": ["coordinates", "boundaries", "proximity", "size"]
            }
        }
    
    def _initialize_models(self):
        """Initialize semantic processing models"""
        try:
            if TRANSFORMERS_AVAILABLE:
                # Sentence transformer for embeddings
                embedding_model = self.config.embeddings.model_name
                logger.info(f"Loading sentence transformer: {embedding_model}")
                self.embeddings_model = SentenceTransformer(embedding_model)
                
                # Specialized models
                self.models["similarity"] = self.embeddings_model
                
                # Question answering for semantic understanding
                try:
                    self.models["qa"] = pipeline(
                        "question-answering",
                        model="deepset/roberta-base-squad2",
                        device=self._get_device()
                    )
                except:
                    logger.warning("Question-answering model not available")
                
                # Text generation for semantic completion
                try:
                    self.models["generation"] = pipeline(
                        "text-generation",
                        model="gpt2",
                        device=self._get_device(),
                        max_length=100
                    )
                except:
                    logger.warning("Text generation model not available")
                
                logger.info("Semantic processing models initialized")
            else:
                self._setup_fallback_methods()
                
        except Exception as e:
            logger.error(f"Failed to initialize semantic models: {e}")
            self._setup_fallback_methods()
    
    def _setup_fallback_methods(self):
        """Setup fallback methods for semantic processing"""
        logger.info("Setting up semantic processing fallback methods")
        self.fallback_mode = True
    
    def _get_device(self) -> int:
        """Get optimal device for model execution"""
        if self.config.performance.enable_gpu and TRANSFORMERS_AVAILABLE:
            try:
                if torch.cuda.is_available():
                    return 0  # Use first GPU
            except:
                pass
        return -1  # Use CPU
    
    async def process(
        self,
        text: Union[str, List[str]],
        include_entities: bool = True,
        include_relations: bool = True,
        include_themes: bool = True,
        analyze_coherence: bool = True
    ) -> Union[SemanticResult, List[SemanticResult]]:
        """
        Process text for semantic understanding
        
        Args:
            text: Text or list of texts to process
            include_entities: Whether to extract semantic entities
            include_relations: Whether to identify semantic relations
            include_themes: Whether to detect conceptual themes
            analyze_coherence: Whether to analyze text coherence
        
        Returns:
            SemanticResult or list of results
        """
        start_time = asyncio.get_event_loop().time()
        
        # Handle batch processing
        is_batch = isinstance(text, list)
        texts = text if is_batch else [text]
        
        results = []
        
        try:
            for single_text in texts:
                result = await self._process_single_text(
                    single_text,
                    include_entities,
                    include_relations,
                    include_themes,
                    analyze_coherence
                )
                results.append(result)
            
            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            for result in results:
                result.processing_time = processing_time / len(results)
            
            return results if is_batch else results[0]
            
        except Exception as e:
            logger.error(f"Semantic processing failed: {e}")
            raise
    
    async def _process_single_text(
        self,
        text: str,
        include_entities: bool,
        include_relations: bool,
        include_themes: bool,
        analyze_coherence: bool
    ) -> SemanticResult:
        """Process semantic understanding for a single text"""
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")
        
        result = SemanticResult(text=text)
        
        try:
            # Extract main concepts
            result.main_concepts = await self._extract_main_concepts(text)
            
            # Extract semantic entities
            if include_entities:
                result.semantic_entities = await self._extract_semantic_entities(text)
            
            # Identify semantic relations
            if include_relations:
                result.semantic_relations = await self._identify_semantic_relations(text)
            
            # Detect conceptual themes
            if include_themes:
                result.conceptual_themes = await self._detect_conceptual_themes(text)
            
            # Generate abstract meaning
            result.abstract_meaning = await self._generate_abstract_meaning(text, result)
            
            # Analyze contextual understanding
            result.contextual_understanding = await self._analyze_contextual_understanding(text)
            
            # Extract discourse markers
            result.discourse_markers = await self._extract_discourse_markers(text)
            
            # Analyze logical structure
            result.logical_structure = await self._analyze_logical_structure(text)
            
            # Calculate semantic density
            result.semantic_density = await self._calculate_semantic_density(text, result)
            
            # Analyze coherence
            if analyze_coherence:
                result.coherence_score = await self._analyze_coherence(text)
            
            # Add metadata
            result.metadata = {
                "word_count": len(text.split()),
                "sentence_count": len([s for s in text.split('.') if s.strip()]),
                "concept_count": len(result.main_concepts),
                "entity_count": len(result.semantic_entities),
                "relation_count": len(result.semantic_relations),
                "processing_mode": "transformer" if not hasattr(self, 'fallback_mode') else "fallback"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Single text semantic processing failed: {e}")
            result.metadata["error"] = str(e)
            return result
    
    async def _extract_main_concepts(self, text: str) -> List[str]:
        """Extract main conceptual themes from text"""
        concepts = []
        
        # Use embeddings-based approach if available
        if self.embeddings_model and not hasattr(self, 'fallback_mode'):
            try:
                # Split into sentences for better concept extraction
                sentences = [s.strip() for s in text.split('.') if s.strip()]
                
                # Generate embeddings for each sentence
                sentence_embeddings = self.embeddings_model.encode(sentences)
                
                # Cluster sentences to find main themes
                if len(sentences) > 2 and SKLEARN_AVAILABLE:
                    n_clusters = min(3, len(sentences))
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                    clusters = kmeans.fit_predict(sentence_embeddings)
                    
                    # Extract representative concepts from each cluster
                    for cluster_id in range(n_clusters):
                        cluster_sentences = [sentences[i] for i, c in enumerate(clusters) if c == cluster_id]
                        concept = await self._extract_concept_from_sentences(cluster_sentences)
                        if concept:
                            concepts.append(concept)
                
            except Exception as e:
                logger.warning(f"Embeddings-based concept extraction failed: {e}")
        
        # Fallback to rule-based concept extraction
        if not concepts:
            concepts = await self._extract_concepts_rule_based(text)
        
        return concepts[:5]  # Limit to top 5 concepts
    
    async def _extract_concept_from_sentences(self, sentences: List[str]) -> Optional[str]:
        """Extract a concept from a group of sentences"""
        if not sentences:
            return None
        
        # Simple approach: find most common important words
        words = []
        for sentence in sentences:
            words.extend([
                word.lower() for word in sentence.split()
                if len(word) > 3 and word.isalpha()
            ])
        
        if not words:
            return None
        
        # Count word frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return most frequent word as concept
        if word_freq:
            return max(word_freq, key=word_freq.get)
        
        return None
    
    async def _extract_concepts_rule_based(self, text: str) -> List[str]:
        """Extract concepts using rule-based approach"""
        concepts = []
        
        # Check against concept ontology
        text_lower = text.lower()
        for concept, details in self.concept_ontology.items():
            # Check if concept keywords appear in text
            concept_score = 0
            if concept in text_lower:
                concept_score += 2
            
            # Check subconcepts
            for subconcept in details.get("subconcepts", []):
                if subconcept in text_lower:
                    concept_score += 1
            
            # Check related terms
            for related in details.get("related", []):
                if related in text_lower:
                    concept_score += 0.5
            
            if concept_score > 1:
                concepts.append((concept, concept_score))
        
        # Sort by score and return top concepts
        concepts.sort(key=lambda x: x[1], reverse=True)
        return [concept for concept, score in concepts[:5]]
    
    async def _extract_semantic_entities(self, text: str) -> List[SemanticEntity]:
        """Extract semantic entities with meaning and context"""
        entities = []
        
        # Rule-based entity extraction with semantic types
        entity_patterns = {
            "agent": r'\b(I|we|they|he|she|it|[A-Z][a-z]+ [A-Z][a-z]+)\b',
            "action": r'\b(doing|making|creating|building|writing|speaking|thinking)\b',
            "object": r'\b(thing|item|product|service|content|material)\b',
            "quality": r'\b(good|bad|excellent|poor|amazing|terrible|beautiful|ugly)\b',
            "quantity": r'\b(\d+|many|few|several|some|all|none|most)\b'
        }
        
        for entity_type, pattern in entity_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity_text = match.group()
                
                entity = SemanticEntity(
                    text=entity_text,
                    semantic_type=entity_type,
                    confidence=0.7,  # Rule-based confidence
                    context=text[max(0, match.start()-20):match.end()+20]
                )
                
                entities.append(entity)
        
        return entities
    
    async def _identify_semantic_relations(self, text: str) -> List[SemanticRelation]:
        """Identify semantic relationships between entities"""
        relations = []
        
        # Simple pattern-based relation extraction
        relation_patterns = {
            "causation": [r'(\w+)\s+(causes?|leads? to|results? in)\s+(\w+)'],
            "association": [r'(\w+)\s+(is|are)\s+(\w+)', r'(\w+)\s+(has|have)\s+(\w+)'],
            "temporal": [r'(\w+)\s+(before|after)\s+(\w+)'],
            "spatial": [r'(\w+)\s+(in|on|at|near)\s+(\w+)']
        }
        
        for relation_type, patterns in relation_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) >= 3:
                        subject = match.group(1)
                        predicate = match.group(2)
                        obj = match.group(3)
                        
                        relation = SemanticRelation(
                            subject=subject,
                            predicate=predicate,
                            object=obj,
                            confidence=0.6,
                            context=match.group()
                        )
                        
                        relations.append(relation)
        
        return relations
    
    async def _detect_conceptual_themes(self, text: str) -> List[ConceptualTheme]:
        """Detect high-level conceptual themes"""
        themes = []
        
        # Analyze text for thematic content
        theme_indicators = {
            "technology": ["tech", "digital", "computer", "software", "ai", "internet"],
            "emotions": ["feel", "emotion", "happy", "sad", "angry", "love", "hate"],
            "business": ["money", "profit", "company", "market", "business", "economy"],
            "relationships": ["friend", "family", "partner", "relationship", "social"],
            "creativity": ["create", "art", "design", "music", "write", "imagine"],
            "learning": ["learn", "study", "knowledge", "education", "skill", "teach"]
        }
        
        text_lower = text.lower()
        for theme, indicators in theme_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            if score > 0:
                relevance = score / len(text.split()) * 10  # Normalize by text length
                
                theme_obj = ConceptualTheme(
                    theme=theme,
                    relevance_score=min(relevance, 1.0),
                    supporting_evidence=[ind for ind in indicators if ind in text_lower],
                    related_concepts=[]
                )
                
                themes.append(theme_obj)
        
        # Sort by relevance
        themes.sort(key=lambda x: x.relevance_score, reverse=True)
        return themes[:3]  # Top 3 themes
    
    async def _generate_abstract_meaning(self, text: str, result: SemanticResult) -> str:
        """Generate abstract meaning summary"""
        # Create abstract meaning based on extracted information
        concepts = result.main_concepts[:3]
        themes = [t.theme for t in result.conceptual_themes[:2]]
        
        if concepts or themes:
            meaning_parts = []
            
            if concepts:
                meaning_parts.append(f"The text primarily discusses {', '.join(concepts)}")
            
            if themes:
                meaning_parts.append(f"with thematic focus on {', '.join(themes)}")
            
            return ". ".join(meaning_parts) + "."
        
        return "The text contains general content without specific dominant themes."
    
    async def _analyze_contextual_understanding(self, text: str) -> Dict[str, Any]:
        """Analyze contextual understanding of the text"""
        return {
            "formality_level": await self._assess_formality(text),
            "subjectivity": await self._assess_subjectivity(text),
            "complexity": await self._assess_complexity(text),
            "temporal_focus": await self._assess_temporal_focus(text),
            "perspective": await self._assess_perspective(text)
        }
    
    async def _assess_formality(self, text: str) -> str:
        """Assess formality level of text"""
        formal_indicators = ["therefore", "furthermore", "consequently", "nevertheless"]
        informal_indicators = ["anyway", "basically", "kinda", "sorta", "gonna"]
        
        text_lower = text.lower()
        formal_count = sum(1 for ind in formal_indicators if ind in text_lower)
        informal_count = sum(1 for ind in informal_indicators if ind in text_lower)
        
        if formal_count > informal_count:
            return "formal"
        elif informal_count > formal_count:
            return "informal"
        else:
            return "neutral"
    
    async def _assess_subjectivity(self, text: str) -> float:
        """Assess subjectivity level (0=objective, 1=subjective)"""
        subjective_indicators = ["I think", "I believe", "in my opinion", "personally", "feel"]
        objective_indicators = ["data shows", "research indicates", "studies reveal", "according to"]
        
        text_lower = text.lower()
        subjective_count = sum(1 for ind in subjective_indicators if ind in text_lower)
        objective_count = sum(1 for ind in objective_indicators if ind in text_lower)
        
        total = subjective_count + objective_count
        if total == 0:
            return 0.5  # Neutral
        
        return subjective_count / total
    
    async def _assess_complexity(self, text: str) -> str:
        """Assess complexity level of text"""
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        sentences = [s for s in text.split('.') if s.strip()]
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        if avg_word_length > 6 and avg_sentence_length > 20:
            return "high"
        elif avg_word_length < 4 and avg_sentence_length < 10:
            return "low"
        else:
            return "medium"
    
    async def _assess_temporal_focus(self, text: str) -> str:
        """Assess temporal focus of text"""
        past_indicators = ["was", "were", "had", "did", "yesterday", "ago"]
        present_indicators = ["is", "are", "am", "do", "does", "now", "today"]
        future_indicators = ["will", "shall", "going to", "tomorrow", "next"]
        
        text_lower = text.lower()
        past_count = sum(1 for ind in past_indicators if ind in text_lower)
        present_count = sum(1 for ind in present_indicators if ind in text_lower)
        future_count = sum(1 for ind in future_indicators if ind in text_lower)
        
        max_count = max(past_count, present_count, future_count)
        if max_count == past_count:
            return "past"
        elif max_count == future_count:
            return "future"
        else:
            return "present"
    
    async def _assess_perspective(self, text: str) -> str:
        """Assess narrative perspective"""
        first_person = len(re.findall(r'\b(I|we|my|our|me|us)\b', text, re.IGNORECASE))
        second_person = len(re.findall(r'\b(you|your)\b', text, re.IGNORECASE))
        third_person = len(re.findall(r'\b(he|she|it|they|his|her|their)\b', text, re.IGNORECASE))
        
        max_count = max(first_person, second_person, third_person)
        if max_count == first_person:
            return "first_person"
        elif max_count == second_person:
            return "second_person"
        elif max_count == third_person:
            return "third_person"
        else:
            return "neutral"
    
    async def _extract_discourse_markers(self, text: str) -> List[str]:
        """Extract discourse markers that indicate text structure"""
        discourse_markers = []
        
        marker_patterns = {
            "addition": ["also", "furthermore", "moreover", "additionally"],
            "contrast": ["however", "nevertheless", "but", "although"],
            "sequence": ["first", "second", "next", "finally"],
            "emphasis": ["indeed", "certainly", "definitely", "clearly"],
            "conclusion": ["therefore", "thus", "in conclusion", "overall"]
        }
        
        text_lower = text.lower()
        for category, markers in marker_patterns.items():
            for marker in markers:
                if marker in text_lower:
                    discourse_markers.append(f"{category}:{marker}")
        
        return discourse_markers
    
    async def _analyze_logical_structure(self, text: str) -> Dict[str, Any]:
        """Analyze logical structure of text"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        structure = {
            "total_sentences": len(sentences),
            "has_introduction": False,
            "has_conclusion": False,
            "argument_flow": "unclear",
            "coherence_markers": []
        }
        
        if sentences:
            # Check for introduction patterns
            first_sentence = sentences[0].lower()
            intro_patterns = ["in this", "this text", "i will discuss", "let me explain"]
            structure["has_introduction"] = any(pattern in first_sentence for pattern in intro_patterns)
            
            # Check for conclusion patterns
            last_sentence = sentences[-1].lower()
            conclusion_patterns = ["in conclusion", "to summarize", "overall", "finally"]
            structure["has_conclusion"] = any(pattern in last_sentence for pattern in conclusion_patterns)
            
            # Analyze argument flow
            if len(sentences) >= 3:
                structure["argument_flow"] = "developed"
            elif len(sentences) >= 2:
                structure["argument_flow"] = "basic"
            else:
                structure["argument_flow"] = "simple"
        
        return structure
    
    async def _calculate_semantic_density(self, text: str, result: SemanticResult) -> float:
        """Calculate semantic density of text"""
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        
        # Count semantic elements
        semantic_elements = (
            len(result.main_concepts) +
            len(result.semantic_entities) +
            len(result.semantic_relations) +
            len(result.conceptual_themes)
        )
        
        # Normalize by text length
        density = semantic_elements / (word_count / 100)  # Per 100 words
        return min(density, 1.0)  # Cap at 1.0
    
    async def _analyze_coherence(self, text: str) -> float:
        """Analyze text coherence using embeddings similarity"""
        if hasattr(self, 'fallback_mode') or not self.embeddings_model:
            # Fallback coherence analysis
            return await self._analyze_coherence_fallback(text)
        
        try:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            if len(sentences) < 2:
                return 1.0  # Single sentence is coherent by definition
            
            # Generate embeddings for sentences
            embeddings = self.embeddings_model.encode(sentences)
            
            # Calculate pairwise similarities
            similarities = []
            for i in range(len(embeddings) - 1):
                similarity = cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
                similarities.append(similarity)
            
            # Average similarity as coherence score
            coherence = np.mean(similarities) if similarities else 0.5
            return float(coherence)
            
        except Exception as e:
            logger.warning(f"Coherence analysis failed: {e}")
            return await self._analyze_coherence_fallback(text)
    
    async def _analyze_coherence_fallback(self, text: str) -> float:
        """Fallback coherence analysis using word overlap"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if len(sentences) < 2:
            return 1.0
        
        # Calculate word overlap between consecutive sentences
        overlaps = []
        for i in range(len(sentences) - 1):
            words1 = set(sentences[i].lower().split())
            words2 = set(sentences[i + 1].lower().split())
            
            if len(words1) == 0 or len(words2) == 0:
                overlap = 0.0
            else:
                overlap = len(words1.intersection(words2)) / min(len(words1), len(words2))
            
            overlaps.append(overlap)
        
        return np.mean(overlaps) if overlaps else 0.5
    
    async def compare_semantic_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compare semantic similarity between two texts"""
        if hasattr(self, 'fallback_mode') or not self.embeddings_model:
            # Fallback: simple word overlap
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if len(words1) == 0 or len(words2) == 0:
                return 0.0
            
            overlap = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return overlap / union if union > 0 else 0.0
        
        try:
            # Use sentence transformer embeddings
            embeddings = self.embeddings_model.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity calculation failed: {e}")
            return 0.0
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        status = {
            "status": "healthy",
            "embeddings_model_loaded": self.embeddings_model is not None,
            "models_loaded": len(self.models),
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "sklearn_available": SKLEARN_AVAILABLE,
            "concept_ontology_size": len(self.concept_ontology)
        }
        
        # Test basic functionality
        try:
            if self.embeddings_model:
                # Quick embedding test
                test_embedding = self.embeddings_model.encode(["This is a test."])
                status["test_result"] = "passed"
                status["embedding_dimension"] = len(test_embedding[0])
            else:
                status["test_result"] = "fallback_mode"
        except Exception as e:
            status["status"] = "degraded"
            status["error"] = str(e)
        
        return status
    
    def shutdown(self):
        """Shutdown the semantic processor"""
        logger.info("Shutting down Semantic Processor")
        
        # Clear models
        self.models.clear()
        if self.embeddings_model:
            del self.embeddings_model
            self.embeddings_model = None
        
        # Clear GPU memory if using CUDA
        if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()

# Utility functions
def calculate_semantic_overlap(result1: SemanticResult, result2: SemanticResult) -> float:
    """Calculate semantic overlap between two results"""
    # Compare main concepts
    concepts1 = set(result1.main_concepts)
    concepts2 = set(result2.main_concepts)
    concept_overlap = len(concepts1.intersection(concepts2)) / max(len(concepts1.union(concepts2)), 1)
    
    # Compare themes
    themes1 = set(t.theme for t in result1.conceptual_themes)
    themes2 = set(t.theme for t in result2.conceptual_themes)
    theme_overlap = len(themes1.intersection(themes2)) / max(len(themes1.union(themes2)), 1)
    
    # Average overlap
    return (concept_overlap + theme_overlap) / 2

def extract_semantic_keywords(result: SemanticResult) -> List[str]:
    """Extract semantic keywords from processing result"""
    keywords = []
    
    # Add main concepts
    keywords.extend(result.main_concepts)
    
    # Add entity texts
    keywords.extend([entity.text for entity in result.semantic_entities])
    
    # Add theme names
    keywords.extend([theme.theme for theme in result.conceptual_themes])
    
    # Remove duplicates and return
    return list(set(keywords))
