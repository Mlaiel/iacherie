"""Entity Extractor - Advanced Named Entity Recognition System
==========================================================

Advanced AI-powered named entity recognition and extraction system for identifying
and classifying entities in text with high precision and comprehensive coverage.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import json
from collections import defaultdict

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers library not available. Entity extraction will use fallback methods.")

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available. Using alternative NER methods.")

from .config import NLPAgentConfig, default_config

# Setup logging
logger = logging.getLogger(__name__)

class EntityType(Enum):
    """Standard entity types"""    PERSON = "PERSON"
    ORGANIZATION = "ORG"
    LOCATION = "LOC"
    MISC = "MISC"
    DATE = "DATE"
    TIME = "TIME"
    MONEY = "MONEY"
    PERCENT = "PERCENT"
    PRODUCT = "PRODUCT"
    EVENT = "EVENT"
    LANGUAGE = "LANGUAGE"
    NATIONALITY = "NORP"
    FACILITY = "FAC"
    GPE = "GPE"  # Geopolitical entity
    LAW = "LAW"
    WORK_OF_ART = "WORK_OF_ART"

class EntityCategory(Enum):
    """High-level entity categories"""    PEOPLE = "people"
    ORGANIZATIONS = "organizations"
    PLACES = "places"
    TEMPORAL = "temporal"
    NUMERICAL = "numerical"
    CREATIVE = "creative"
    OTHER = "other"

@dataclass
class Entity:
    """Individual entity with detailed information"""    text: str
    label: str
    start: int
    end: int
    confidence: float
    category: str = ""
    description: str = ""
    aliases: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    context: str = ""
    canonical_form: str = ""
    linked_entities: List[str] = field(default_factory=list)

@dataclass
class EntityCluster:
    """Cluster of related entities"""    entities: List[Entity]
    cluster_type: str
    representative: Entity
    confidence: float
    relationships: List[str] = field(default_factory=list)

@dataclass
class ExtractionResult:
    """Complete entity extraction result"""    text: str
    entities: List[Entity] = field(default_factory=list)
    entity_clusters: List[EntityCluster] = field(default_factory=list)
    entity_counts: Dict[str, int] = field(default_factory=dict)
    entity_coverage: float = 0.0  # Percentage of text covered by entities
    unique_entities: int = 0
    total_entities: int = 0
    dominant_category: str = ""
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class EntityExtractor:
    """    Advanced AI-powered named entity recognition and extraction system for identifying
    and classifying entities in text content with comprehensive analysis.
    """    
    def __init__(self, config: Optional[NLPAgentConfig] = None):
        """Initialize Entity Extractor"""        self.config = config or default_config
        self.models = {}
        self.pipelines = {}
        self.nlp = None
        self.entity_patterns = self._load_entity_patterns()
        self.entity_mappings = self._load_entity_mappings()
        
        self._initialize_models()
    
    def _load_entity_patterns(self) -> Dict[str, List[str]]:
        """Load regex patterns for entity recognition"""        return {
            "email": [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            "phone": [
                r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
                r'\b\d{3}-\d{3}-\d{4}\b',
                r'\b\(\d{3}\)\s*\d{3}-\d{4}\b'
            ],
            "url": [
                r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
                r'www\.(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
            ],
            "hashtag": [
                r'#\w+'
            ],
            "mention": [
                r'@\w+'
            ],
            "currency": [
                r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
                r'€\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
                r'£\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
            ],
            "percentage": [
                r'\d+(?:\.\d+)?%'
            ],
            "date": [
                r'\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b',
                r'\b\d{4}[/\-]\d{1,2}[/\-]\d{1,2}\b',
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b'
            ],
            "time": [
                r'\b\d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:AM|PM|am|pm))?\b'
            ],
            "ip_address": [
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            ],
            "credit_card": [
                r'\b(?:\d{4}[\s-]?){3}\d{4}\b'
            ]
        }
    
    def _load_entity_mappings(self) -> Dict[str, str]:
        """Load entity type to category mappings"""        return {
            "PERSON": "people",
            "PER": "people",
            "ORG": "organizations",
            "ORGANIZATION": "organizations",
            "LOC": "places",
            "LOCATION": "places",
            "GPE": "places",
            "FACILITY": "places",
            "FAC": "places",
            "DATE": "temporal",
            "TIME": "temporal",
            "MONEY": "numerical",
            "PERCENT": "numerical",
            "QUANTITY": "numerical",
            "ORDINAL": "numerical",
            "CARDINAL": "numerical",
            "PRODUCT": "creative",
            "WORK_OF_ART": "creative",
            "EVENT": "other",
            "LAW": "other",
            "LANGUAGE": "other",
            "NORP": "other",
            "MISC": "other"
        }
    
    def _initialize_models(self):
        """Initialize entity extraction models"""        try:
            # Initialize spaCy if available
            if SPACY_AVAILABLE:
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                    logger.info("spaCy model loaded successfully")
                except OSError:
                    logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
                    self.nlp = None
            
            # Initialize transformer models if available
            if TRANSFORMERS_AVAILABLE:
                try:
                    # NER pipeline
                    self.pipelines["ner"] = pipeline(
                        "token-classification",
                        model="dbmdz/bert-large-cased-finetuned-conll03-english",
                        aggregation_strategy="simple",
                        device=self._get_device()
                    )
                    
                    # Alternative NER model for better coverage
                    try:
                        self.pipelines["ner_roberta"] = pipeline(
                            "token-classification",
                            model="Jean-Baptiste/roberta-large-ner-english",
                            aggregation_strategy="simple",
                            device=self._get_device()
                        )
                    except:
                        logger.warning("Alternative NER model not available")
                    
                    logger.info("Transformer NER models initialized")
                    
                except Exception as e:
                    logger.warning(f"Failed to load transformer models: {e}")
            
            # Compile regex patterns
            self._compile_patterns()
            
        except Exception as e:
            logger.error(f"Failed to initialize entity extraction models: {e}")
            self._setup_fallback_methods()
    
    def _setup_fallback_methods(self):
        """Setup fallback methods for entity extraction"""        logger.info("Setting up entity extraction fallback methods")
        self.fallback_mode = True
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for better performance"""        self.compiled_patterns = {}
        for entity_type, patterns in self.entity_patterns.items():
            self.compiled_patterns[entity_type] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in patterns
            ]
    
    def _get_device(self) -> int:
        """Get optimal device for model execution"""        if self.config.performance.enable_gpu and TRANSFORMERS_AVAILABLE:
            try:
                if torch.cuda.is_available():
                    return 0  # Use first GPU
            except:
                pass
        return -1  # Use CPU
    
    async def extract_entities(
        self,
        text: Union[str, List[str]],
        entity_types: Optional[List[str]] = None,
        include_patterns: bool = True,
        merge_overlapping: bool = True,
        cluster_entities: bool = True
    ) -> Union[ExtractionResult, List[ExtractionResult]]:
        """        Extract entities from text
        
        Args:
            text: Text or list of texts to analyze
            entity_types: Specific entity types to extract (None for all)
            include_patterns: Whether to include pattern-based extraction
            merge_overlapping: Whether to merge overlapping entities
            cluster_entities: Whether to cluster related entities
        
        Returns:
            ExtractionResult or list of results
        """        start_time = asyncio.get_event_loop().time()
        
        # Handle batch processing
        is_batch = isinstance(text, list)
        texts = text if is_batch else [text]
        
        results = []
        
        try:
            for single_text in texts:
                result = await self._extract_single_text(
                    single_text,
                    entity_types,
                    include_patterns,
                    merge_overlapping,
                    cluster_entities
                )
                results.append(result)
            
            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            for result in results:
                result.processing_time = processing_time / len(results)
            
            return results if is_batch else results[0]
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            raise
    
    async def _extract_single_text(
        self,
        text: str,
        entity_types: Optional[List[str]],
        include_patterns: bool,
        merge_overlapping: bool,
        cluster_entities: bool
    ) -> ExtractionResult:
        """Extract entities from a single text"""        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")
        
        result = ExtractionResult(text=text)
        all_entities = []
        
        try:
            # Extract using different methods
            if self.nlp and SPACY_AVAILABLE:
                spacy_entities = await self._extract_with_spacy(text, entity_types)
                all_entities.extend(spacy_entities)
            
            if TRANSFORMERS_AVAILABLE and "ner" in self.pipelines:
                transformer_entities = await self._extract_with_transformer(text, entity_types)
                all_entities.extend(transformer_entities)
            
            if include_patterns:
                pattern_entities = await self._extract_with_patterns(text, entity_types)
                all_entities.extend(pattern_entities)
            
            # Merge overlapping entities if requested
            if merge_overlapping:
                all_entities = self._merge_overlapping_entities(all_entities)
            
            # Sort entities by position
            all_entities.sort(key=lambda e: (e.start, e.end))
            result.entities = all_entities
            
            # Calculate statistics
            await self._calculate_statistics(result)
            
            # Cluster entities if requested
            if cluster_entities and all_entities:
                result.entity_clusters = await self._cluster_entities(all_entities)
            
            # Find relationships
            result.relationships = await self._find_relationships(all_entities, text)
            
            # Add metadata
            result.metadata = {
                "text_length": len(text),
                "extraction_methods": self._get_extraction_methods(),
                "entity_types_found": list(set(e.label for e in all_entities)),
                "spacy_available": SPACY_AVAILABLE and self.nlp is not None,
                "transformers_available": TRANSFORMERS_AVAILABLE
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Single text entity extraction failed: {e}")
            result.metadata["error"] = str(e)
            return result
    
    async def _extract_with_spacy(
        self,
        text: str,
        entity_types: Optional[List[str]]
    ) -> List[Entity]:
        """Extract entities using spaCy"""        entities = []
        
        try:
            doc = self.nlp(text)
            
            for ent in doc.ents:
                # Filter by entity types if specified
                if entity_types and ent.label_ not in entity_types:
                    continue
                
                entity = Entity(
                    text=ent.text,
                    label=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=0.8,  # spaCy doesn't provide confidence scores
                    category=self.entity_mappings.get(ent.label_, "other"),
                    description=spacy.explain(ent.label_) or "",
                    canonical_form=ent.text.lower(),
                    context=text[max(0, ent.start_char-50):min(len(text), ent.end_char+50)]
                )
                
                entities.append(entity)
            
        except Exception as e:
            logger.error(f"spaCy entity extraction failed: {e}")
        
        return entities
    
    async def _extract_with_transformer(
        self,
        text: str,
        entity_types: Optional[List[str]]
    ) -> List[Entity]:
        """Extract entities using transformer models"""        entities = []
        
        try:
            # Use primary NER pipeline
            ner_pipeline = self.pipelines.get("ner")
            if ner_pipeline:
                predictions = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ner_pipeline(text)
                )
                
                for pred in predictions:
                    # Filter by entity types if specified
                    if entity_types and pred["entity_group"] not in entity_types:
                        continue
                    
                    entity = Entity(
                        text=pred["word"],
                        label=pred["entity_group"],
                        start=pred["start"],
                        end=pred["end"],
                        confidence=pred["score"],
                        category=self.entity_mappings.get(pred["entity_group"], "other"),
                        canonical_form=pred["word"].lower(),
                        context=text[max(0, pred["start"]-50):min(len(text), pred["end"]+50)]
                    )
                    
                    entities.append(entity)
            
            # Use alternative model if available
            alt_pipeline = self.pipelines.get("ner_roberta")
            if alt_pipeline and len(entities) < 3:  # Use alternative if primary found few entities
                try:
                    alt_predictions = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: alt_pipeline(text)
                    )
                    
                    # Add entities not already found
                    existing_positions = {(e.start, e.end) for e in entities}
                    
                    for pred in alt_predictions:
                        pos = (pred["start"], pred["end"])
                        if pos not in existing_positions:
                            if not entity_types or pred["entity_group"] in entity_types:
                                entity = Entity(
                                    text=pred["word"],
                                    label=pred["entity_group"],
                                    start=pred["start"],
                                    end=pred["end"],
                                    confidence=pred["score"],
                                    category=self.entity_mappings.get(pred["entity_group"], "other"),
                                    canonical_form=pred["word"].lower(),
                                    context=text[max(0, pred["start"]-50):min(len(text), pred["end"]+50)]
                                )
                                
                                entities.append(entity)
                
                except Exception as e:
                    logger.warning(f"Alternative NER model failed: {e}")
            
        except Exception as e:
            logger.error(f"Transformer entity extraction failed: {e}")
        
        return entities
    
    async def _extract_with_patterns(
        self,
        text: str,
        entity_types: Optional[List[str]]
    ) -> List[Entity]:
        """Extract entities using regex patterns"""        entities = []
        
        try:
            for entity_type, patterns in self.compiled_patterns.items():
                # Filter by entity types if specified
                if entity_types and entity_type.upper() not in entity_types:
                    continue
                
                for pattern in patterns:
                    matches = pattern.finditer(text)
                    
                    for match in matches:
                        entity = Entity(
                            text=match.group(),
                            label=entity_type.upper(),
                            start=match.start(),
                            end=match.end(),
                            confidence=0.9,  # High confidence for pattern matches
                            category=self.entity_mappings.get(entity_type.upper(), "other"),
                            canonical_form=match.group().lower(),
                            context=text[max(0, match.start()-50):min(len(text), match.end()+50)]
                        )
                        
                        entities.append(entity)
        
        except Exception as e:
            logger.error(f"Pattern-based entity extraction failed: {e}")
        
        return entities
    
    def _merge_overlapping_entities(self, entities: List[Entity]) -> List[Entity]:
        """Merge overlapping entities, keeping the one with higher confidence"""        if not entities:
            return entities
        
        # Sort by start position
        sorted_entities = sorted(entities, key=lambda e: (e.start, -e.confidence))
        merged = []
        
        for entity in sorted_entities:
            # Check for overlap with existing entities
            overlapping = False
            for i, existing in enumerate(merged):
                if (entity.start < existing.end and entity.end > existing.start):
                    # Overlap detected
                    if entity.confidence > existing.confidence:
                        merged[i] = entity  # Replace with higher confidence entity
                    overlapping = True
                    break
            
            if not overlapping:
                merged.append(entity)
        
        return merged
    
    async def _calculate_statistics(self, result: ExtractionResult):
        """Calculate entity statistics"""        entities = result.entities
        
        if not entities:
            return
        
        # Count entities by type
        result.entity_counts = defaultdict(int)
        for entity in entities:
            result.entity_counts[entity.label] += 1
        
        # Calculate coverage
        total_entity_chars = sum(len(entity.text) for entity in entities)
        result.entity_coverage = total_entity_chars / len(result.text) if result.text else 0
        
        # Count unique and total entities
        result.unique_entities = len(set(entity.canonical_form for entity in entities))
        result.total_entities = len(entities)
        
        # Find dominant category
        category_counts = defaultdict(int)
        for entity in entities:
            category_counts[entity.category] += 1
        
        if category_counts:
            result.dominant_category = max(category_counts, key=category_counts.get)
    
    async def _cluster_entities(self, entities: List[Entity]) -> List[EntityCluster]:
        """Cluster related entities"""        clusters = []
        
        try:
            # Group entities by category
            category_groups = defaultdict(list)
            for entity in entities:
                category_groups[entity.category].append(entity)
            
            # Create clusters for each category
            for category, category_entities in category_groups.items():
                if len(category_entities) > 1:
                    # Find representative entity (highest confidence)
                    representative = max(category_entities, key=lambda e: e.confidence)
                    
                    # Calculate cluster confidence
                    cluster_confidence = sum(e.confidence for e in category_entities) / len(category_entities)
                    
                    cluster = EntityCluster(
                        entities=category_entities,
                        cluster_type=category,
                        representative=representative,
                        confidence=cluster_confidence
                    )
                    
                    clusters.append(cluster)
        
        except Exception as e:
            logger.error(f"Entity clustering failed: {e}")
        
        return clusters
    
    async def _find_relationships(
        self,
        entities: List[Entity],
        text: str
    ) -> List[Dict[str, Any]]:
        """Find relationships between entities"""        relationships = []
        
        try:
            # Simple co-occurrence based relationships
            for i, entity1 in enumerate(entities):
                for entity2 in entities[i+1:]:
                    # Check if entities are close to each other
                    distance = abs(entity1.start - entity2.start)
                    
                    if distance < 100:  # Within 100 characters
                        relationship = {
                            "entity1": entity1.text,
                            "entity2": entity2.text,
                            "type": "co_occurrence",
                            "distance": distance,
                            "confidence": min(entity1.confidence, entity2.confidence)
                        }
                        
                        relationships.append(relationship)
        
        except Exception as e:
            logger.error(f"Relationship finding failed: {e}")
        
        return relationships
    
    def _get_extraction_methods(self) -> List[str]:
        """Get list of available extraction methods"""        methods = []
        
        if SPACY_AVAILABLE and self.nlp:
            methods.append("spacy")
        
        if TRANSFORMERS_AVAILABLE and self.pipelines:
            methods.append("transformers")
        
        methods.append("patterns")
        
        return methods
    
    async def get_entity_details(
        self,
        entity_text: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """Get detailed information about a specific entity"""        # This could be expanded to query external knowledge bases
        details = {
            "text": entity_text,
            "canonical_form": entity_text.lower(),
            "context": context,
            "possible_types": [],
            "attributes": {}
        }
        
        # Try to classify the entity
        for entity_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(entity_text):
                    details["possible_types"].append(entity_type)
        
        return details
    
    async def extract_entities_by_type(
        self,
        text: str,
        entity_type: str
    ) -> List[Entity]:
        """Extract entities of a specific type"""        result = await self.extract_entities(text, entity_types=[entity_type])
        return [e for e in result.entities if e.label == entity_type]
    
    async def find_entity_mentions(
        self,
        text: str,
        entity_text: str,
        fuzzy_match: bool = True
    ) -> List[Entity]:
        """Find all mentions of a specific entity in text"""        mentions = []
        
        # Extract all entities first
        result = await self.extract_entities(text)
        
        # Find matches
        for entity in result.entities:
            if fuzzy_match:
                if entity.canonical_form == entity_text.lower():
                    mentions.append(entity)
            else:
                if entity.text == entity_text:
                    mentions.append(entity)
        
        return mentions
    
    def get_supported_entity_types(self) -> List[str]:
        """Get list of supported entity types"""        types = list(EntityType.__members__.keys())
        types.extend(self.entity_patterns.keys())
        return sorted(set(types))
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""        status = {
            "status": "healthy",
            "spacy_available": SPACY_AVAILABLE and self.nlp is not None,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "models_loaded": len(self.pipelines),
            "patterns_loaded": len(self.compiled_patterns),
            "extraction_methods": self._get_extraction_methods()
        }
        
        # Test basic functionality
        try:
            test_result = asyncio.run(
                self.extract_entities("John Doe works at Google in New York.")
            )
            status["test_result"] = "passed"
            status["test_entities_found"] = len(test_result.entities)
        except Exception as e:
            status["status"] = "degraded"
            status["error"] = str(e)
        
        return status
    
    def shutdown(self):
        """Shutdown the entity extractor"""        logger.info("Shutting down Entity Extractor")
        
        # Clear models
        self.models.clear()
        self.pipelines.clear()
        if hasattr(self, 'compiled_patterns'):
            self.compiled_patterns.clear()
        
        # Clear spaCy model
        if self.nlp:
            self.nlp = None
        
        # Clear GPU memory if using CUDA
        if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()

# Utility functions
def calculate_entity_overlap(entity1: Entity, entity2: Entity) -> float:
    """Calculate overlap between two entities"""    if entity1.end <= entity2.start or entity2.end <= entity1.start:
        return 0.0  # No overlap
    
    overlap_start = max(entity1.start, entity2.start)
    overlap_end = min(entity1.end, entity2.end)
    overlap_length = overlap_end - overlap_start
    
    total_length = max(entity1.end, entity2.end) - min(entity1.start, entity2.start)
    
    return overlap_length / total_length if total_length > 0 else 0.0

def merge_entity_results(results: List[ExtractionResult]) -> ExtractionResult:
    """Merge multiple extraction results"""    if not results:
        return ExtractionResult(text="")
    
    merged_text = " ".join(result.text for result in results)
    merged_entities = []
    text_offset = 0
    
    for result in results:
        # Adjust entity positions
        for entity in result.entities:
            adjusted_entity = Entity(
                text=entity.text,
                label=entity.label,
                start=entity.start + text_offset,
                end=entity.end + text_offset,
                confidence=entity.confidence,
                category=entity.category,
                description=entity.description,
                canonical_form=entity.canonical_form
            )
            merged_entities.append(adjusted_entity)
        
        text_offset += len(result.text) + 1  # +1 for space
    
    merged_result = ExtractionResult(
        text=merged_text,
        entities=merged_entities
    )
    
    return merged_result
