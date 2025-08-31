"""
Entity Extractor - Core Module

Advanced entity extraction engine for multi-format content with intelligent
recognition of creative industry entities, business relationships, and 
content-specific metadata. Optimized for musicians, influencers, photographers,
bloggers, and content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""

import asyncio
import re
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

import spacy
import numpy as np
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import torch

from ...core.base_service import BaseService
from ...core.cache import cache_manager
from ...core.monitoring import MetricsCollector
from ...models.content import ContentType, ContentMetadata
from ...models.entities import EntityType, Entity, EntityRelation
from ...utils.text_processors import TextPreprocessor
from ...utils.validation import validate_input


class EntityCategory(Enum):
    """Entity categories specific to creative industry"""
    PERSON = "person"
    ORGANIZATION = "organization"
    CREATIVE_WORK = "creative_work"
    PLATFORM = "platform"
    GENRE = "genre"
    INSTRUMENT = "instrument"
    BRAND = "brand"
    LOCATION = "location"
    EVENT = "event"
    TECHNOLOGY = "technology"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"


class EntityConfidence(Enum):
    """Confidence levels for entity extraction"""
    HIGH = 0.9
    MEDIUM = 0.7
    LOW = 0.5


@dataclass
class ExtractedEntity:
    """Data class for extracted entity with metadata"""
    text: str
    entity_type: EntityCategory
    confidence: float
    start_pos: int
    end_pos: int
    context: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    relationships: List['EntityRelation'] = field(default_factory=list)
    canonical_form: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization validation and normalization"""
        if self.confidence > 1.0:
            self.confidence = 1.0
        elif self.confidence < 0.0:
            self.confidence = 0.0
            
        if not self.canonical_form:
            self.canonical_form = self.text.strip().lower()


@dataclass
class ExtractionResult:
    """Comprehensive extraction result with analytics"""
    entities: List[ExtractedEntity]
    processing_time: float
    confidence_score: float
    entity_count_by_type: Dict[EntityCategory, int]
    relationships: List[EntityRelation]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_high_confidence_entities(self) -> List[ExtractedEntity]:
        """Get entities with high confidence scores"""



        return [e for e in self.entities if e.confidence >= EntityConfidence.HIGH.value]
    
    def get_entities_by_type(self, entity_type: EntityCategory) -> List[ExtractedEntity]:
        """Get entities filtered by type"""



        return [e for e in self.entities if e.entity_type == entity_type]


class EntityExtractor(BaseService):
    """
    Advanced entity extraction engine with specialized models for creative content.
    
    Features:
    - Multi-model ensemble for improved accuracy
    - Creative industry domain adaptation
    - Real-time processing with caching
    - Relationship extraction between entities
    - Context-aware entity disambiguation
    - Multi-language support
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("entity_extraction")
        self.text_processor = TextPreprocessor()
        
        # Model configurations
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        
        # Entity patterns for creative industry
        self.creative_patterns = self._load_creative_patterns()
        
        # Cache configurations
        self.cache_ttl = 3600  # 1 hour
        
        # Performance tracking
        self.extraction_stats = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'avg_processing_time': 0.0,
            'entity_type_distribution': {}
        }
        
    async def initialize(self):
        """Initialize models and resources"""



        try:
            self.logger.info("Initializing EntityExtractor models...")
            
            # Load pre-trained NER models
            await self._load_ner_models()
            
            # Load spaCy models
            await self._load_spacy_models()
            
            # Initialize custom transformers
            await self._load_transformer_models()
            
            # Load creative industry vocabularies
            await self._load_creative_vocabularies()
            
            self.logger.info("EntityExtractor initialization completed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize EntityExtractor: {str(e)}")
            raise
    
    async def _load_ner_models(self):
        """Load named entity recognition models"""
        models_config = {
            'general_ner': 'dbmdz/bert-large-cased-finetuned-conll03-english',
            'creative_ner': 'microsoft/DialoGPT-medium',  # Adapted for creative content
            'business_ner': 'ProsusAI/finbert'  # For business/financial entities
        }
        
        for model_name, model_path in models_config.items():
            try:
                self.tokenizers[model_name] = AutoTokenizer.from_pretrained(model_path)
                self.models[model_name] = AutoModelForTokenClassification.from_pretrained(model_path)
                self.pipelines[model_name] = pipeline(
                    "ner", 
                    model=self.models[model_name],
                    tokenizer=self.tokenizers[model_name],
                    aggregation_strategy="simple"
                )
                self.logger.info(f"Loaded NER model: {model_name}")
                
            except Exception as e:
                self.logger.warning(f"Failed to load model {model_name}: {str(e)}")
    
    async def _load_spacy_models(self):
        """Load spaCy models for additional entity recognition"""



        try:
            # Try to load English model
            self.nlp_en = spacy.load("en_core_web_sm")
            self.logger.info("Loaded spaCy English model")
            
            # Try to load additional language models if available
            language_models = ['de_core_news_sm', 'fr_core_news_sm']
            self.nlp_multilang = {}
            
            for lang_model in language_models:
                try:
                    self.nlp_multilang[lang_model.split('_')[0]] = spacy.load(lang_model)
                    self.logger.info(f"Loaded spaCy model: {lang_model}")
                except OSError:
                    self.logger.warning(f"spaCy model {lang_model} not available")
                    
        except OSError:
            self.logger.warning("spaCy English model not available, using basic extraction")
            self.nlp_en = None
    
    async def _load_transformer_models(self):
        """Load transformer models for advanced entity recognition"""



        try:
            # Load BERT for creative content understanding
            self.creative_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                return_all_scores=True
            )
            
            # Load model for music/audio specific entities
            self.audio_entity_detector = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english"
            )
            
            self.logger.info("Loaded transformer models successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to load some transformer models: {str(e)}")
    
    async def _load_creative_vocabularies(self):
        """Load specialized vocabularies for creative industries"""
        self.creative_vocabularies = {
            'music_genres': {
                'pop', 'rock', 'jazz', 'classical', 'electronic', 'hip-hop', 'r&b',
                'country', 'blues', 'reggae', 'folk', 'punk', 'metal', 'indie',
                'ambient', 'techno', 'house', 'trance', 'dubstep', 'drum and bass'
            },
            'instruments': {
                'guitar', 'piano', 'drums', 'bass', 'violin', 'trumpet', 'saxophone',
                'synthesizer', 'keyboard', 'flute', 'clarinet', 'cello', 'harp',
                'microphone', 'amplifier', 'mixer', 'daw', 'audio interface'
            },
            'platforms': {
                'spotify', 'youtube', 'instagram', 'tiktok', 'soundcloud', 'bandcamp',
                'apple music', 'amazon music', 'facebook', 'twitter', 'twitch',
                'discord', 'telegram', 'whatsapp', 'linkedin', 'pinterest'
            },
            'content_types': {
                'song', 'album', 'single', 'ep', 'mixtape', 'podcast', 'video',
                'photo', 'story', 'reel', 'short', 'live stream', 'concert',
                'performance', 'interview', 'collaboration', 'remix', 'cover'
            },
            'business_terms': {
                'royalty', 'licensing', 'copyright', 'trademark', 'revenue',
                'monetization', 'subscription', 'streaming', 'download', 'sale',
                'contract', 'agreement', 'partnership', 'sponsorship', 'brand deal'
            }
        }
    
    def _load_creative_patterns(self) -> Dict[str, List[str]]:
        """Load regex patterns for creative industry entities"""



        return {
            'social_handles': [
                r'@[\w\d_]+',
                r'#[\w\d_]+',
                r'(?:instagram\.com/|twitter\.com/|tiktok\.com/@)[\w\d_]+'
            ],
            'urls': [
                r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
                r'www\.[\w\d\-\.]+\.[a-z]{2,}'
            ],
            'email': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            'phone': [
                r'\+?[\d\s\-\(\)]{10,}'
            ],
            'music_metadata': [
                r'BPM:\s*\d+',
                r'Key:\s*[A-G][#b]?\s*(?:major|minor|maj|min)?',
                r'Duration:\s*\d+:\d+',
                r'Track\s*\d+',
                r'Album:\s*[\w\s]+',
                r'Artist:\s*[\w\s]+'
            ],
            'timestamps': [
                r'\d{1,2}:\d{2}(?::\d{2})?',
                r'\b\d{4}-\d{2}-\d{2}\b',
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b'
            ]
        }
    
    @validate_input
    @cache_manager.cached(ttl=3600)
    async def extract_entities(
        self,
        text: str,
        content_type: Optional[ContentType] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ExtractionResult:
        """
        Extract entities from text with creative industry specialization.
        
        Args:
            text: Input text for entity extraction
            content_type: Type of content being analyzed
            context: Additional context for better extraction
            
        Returns:
            ExtractionResult with extracted entities and metadata
        """
        start_time = datetime.now()
        
        try:
            self.logger.debug(f"Starting entity extraction for text length: {len(text)}")
            self.metrics.increment('extraction_requests')
            
            # Preprocess text
            processed_text = self.text_processor.clean_text(text)
            
            # Initialize extraction result
            entities = []
            relationships = []
            
            # Multi-model entity extraction
            spacy_entities = await self._extract_spacy_entities(processed_text)
            transformer_entities = await self._extract_transformer_entities(processed_text)
            pattern_entities = await self._extract_pattern_entities(processed_text)
            creative_entities = await self._extract_creative_entities(processed_text, content_type)
            
            # Combine and deduplicate entities
            all_entities = spacy_entities + transformer_entities + pattern_entities + creative_entities
            entities = await self._deduplicate_entities(all_entities)
            
            # Extract relationships between entities
            relationships = await self._extract_relationships(entities, processed_text)
            
            # Calculate confidence scores
            confidence_score = self._calculate_overall_confidence(entities)
            
            # Generate statistics
            entity_count_by_type = self._count_entities_by_type(entities)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = ExtractionResult(
                entities=entities,
                processing_time=processing_time,
                confidence_score=confidence_score,
                entity_count_by_type=entity_count_by_type,
                relationships=relationships,
                metadata={
                    'content_type': content_type.value if content_type else None,
                    'text_length': len(text),
                    'processed_text_length': len(processed_text),
                    'extraction_timestamp': datetime.now().isoformat(),
                    'context': context
                }
            )
            
            # Update statistics
            self._update_extraction_stats(result)
            
            self.logger.info(f"Entity extraction completed: {len(entities)} entities found in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Entity extraction failed: {str(e)}")
            self.metrics.increment('extraction_errors')
            raise
    
    async def _extract_spacy_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract entities using spaCy models"""
        entities = []
        
        if not self.nlp_en:
            return entities
            
        try:
            doc = self.nlp_en(text)
            
            for ent in doc.ents:
                entity_type = self._map_spacy_label_to_category(ent.label_)
                if entity_type:
                    entity = ExtractedEntity(
                        text=ent.text,
                        entity_type=entity_type,
                        confidence=0.8,  # spaCy confidence approximation
                        start_pos=ent.start_char,
                        end_pos=ent.end_char,
                        context=self._extract_context(text, ent.start_char, ent.end_char),
                        metadata={'spacy_label': ent.label_, 'source': 'spacy'}
                    )
                    entities.append(entity)
                    
        except Exception as e:
            self.logger.warning(f"spaCy entity extraction failed: {str(e)}")
            
        return entities
    
    async def _extract_transformer_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract entities using transformer models"""
        entities = []
        
        for model_name, pipeline_obj in self.pipelines.items():
            try:
                # Skip if text is too long for transformer
                if len(text) > 512:
                    chunks = [text[i:i+512] for i in range(0, len(text), 512)]
                else:
                    chunks = [text]
                
                for chunk_idx, chunk in enumerate(chunks):
                    ner_results = pipeline_obj(chunk)
                    
                    for result in ner_results:
                        entity_type = self._map_transformer_label_to_category(result['entity_group'])
                        if entity_type:
                            # Adjust positions for chunked text
                            start_pos = result['start'] + (chunk_idx * 512)
                            end_pos = result['end'] + (chunk_idx * 512)
                            
                            entity = ExtractedEntity(
                                text=result['word'],
                                entity_type=entity_type,
                                confidence=result['score'],
                                start_pos=start_pos,
                                end_pos=end_pos,
                                context=self._extract_context(text, start_pos, end_pos),
                                metadata={
                                    'transformer_label': result['entity_group'],
                                    'source': f'transformer_{model_name}'
                                }
                            )
                            entities.append(entity)
                            
            except Exception as e:
                self.logger.warning(f"Transformer entity extraction failed for {model_name}: {str(e)}")
                
        return entities
    
    async def _extract_pattern_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract entities using regex patterns"""
        entities = []
        
        for pattern_type, patterns in self.creative_patterns.items():
            entity_type = self._map_pattern_type_to_category(pattern_type)
            if not entity_type:
                continue
                
            for pattern in patterns:
                try:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    
                    for match in matches:
                        entity = ExtractedEntity(
                            text=match.group(),
                            entity_type=entity_type,
                            confidence=0.9,  # High confidence for pattern matches
                            start_pos=match.start(),
                            end_pos=match.end(),
                            context=self._extract_context(text, match.start(), match.end()),
                            metadata={
                                'pattern_type': pattern_type,
                                'pattern': pattern,
                                'source': 'regex_pattern'
                            }
                        )
                        entities.append(entity)
                        
                except Exception as e:
                    self.logger.warning(f"Pattern matching failed for {pattern}: {str(e)}")
                    
        return entities
    
    async def _extract_creative_entities(self, text: str, content_type: Optional[ContentType]) -> List[ExtractedEntity]:
        """Extract creative industry specific entities"""
        entities = []
        text_lower = text.lower()
        
        # Extract entities from creative vocabularies
        for vocab_type, vocabulary in self.creative_vocabularies.items():
            entity_type = self._map_vocabulary_type_to_category(vocab_type)
            if not entity_type:
                continue
                
            for term in vocabulary:
                # Find all occurrences of the term
                pattern = r'\b' + re.escape(term) + r'\b'
                matches = re.finditer(pattern, text_lower)
                
                for match in matches:
                    # Get original case from text
                    original_text = text[match.start():match.end()]
                    
                    entity = ExtractedEntity(
                        text=original_text,
                        entity_type=entity_type,
                        confidence=0.85,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        context=self._extract_context(text, match.start(), match.end()),
                        metadata={
                            'vocabulary_type': vocab_type,
                            'source': 'creative_vocabulary'
                        }
                    )
                    entities.append(entity)
        
        # Content-type specific extraction
        if content_type:
            content_entities = await self._extract_content_specific_entities(text, content_type)
            entities.extend(content_entities)
            
        return entities
    
    async def _extract_content_specific_entities(self, text: str, content_type: ContentType) -> List[ExtractedEntity]:
        """Extract entities specific to content type"""
        entities = []
        
        if content_type == ContentType.AUDIO:
            # Audio-specific entities
            audio_patterns = {
                'audio_format': r'\b(?:mp3|wav|flac|aac|ogg|m4a)\b',
                'sample_rate': r'\b\d+\s*(?:kHz|khz|Hz|hz)\b',
                'bit_rate': r'\b\d+\s*(?:kbps|Kbps|KBPS)\b',
                'audio_software': r'\b(?:Pro Tools|Logic|Ableton|FL Studio|Cubase|Reaper)\b'
            }
            
            for pattern_name, pattern in audio_patterns.items():
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity = ExtractedEntity(
                        text=match.group(),
                        entity_type=EntityCategory.TECHNOLOGY,
                        confidence=0.9,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        context=self._extract_context(text, match.start(), match.end()),
                        metadata={
                            'content_specific': True,
                            'content_type': content_type.value,
                            'pattern_name': pattern_name,
                            'source': 'content_specific'
                        }
                    )
                    entities.append(entity)
                    
        elif content_type == ContentType.VIDEO:
            # Video-specific entities
            video_patterns = {
                'video_format': r'\b(?:mp4|avi|mov|mkv|webm|flv)\b',
                'resolution': r'\b(?:\d{3,4}x\d{3,4}|\d+p|\d+K)\b',
                'frame_rate': r'\b\d+\s*fps\b',
                'video_software': r'\b(?:Premiere|Final Cut|DaVinci|After Effects)\b'
            }
            
            for pattern_name, pattern in video_patterns.items():
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity = ExtractedEntity(
                        text=match.group(),
                        entity_type=EntityCategory.TECHNOLOGY,
                        confidence=0.9,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        context=self._extract_context(text, match.start(), match.end()),
                        metadata={
                            'content_specific': True,
                            'content_type': content_type.value,
                            'pattern_name': pattern_name,
                            'source': 'content_specific'
                        }
                    )
                    entities.append(entity)
                    
        return entities
    
    async def _deduplicate_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """Remove duplicate entities and merge similar ones"""
        if not entities:
            return []
            
        # Sort by position
        entities.sort(key=lambda x: x.start_pos)
        
        deduplicated = []
        i = 0
        
        while i < len(entities):
            current = entities[i]
            overlapping = [current]
            
            # Find overlapping entities
            j = i + 1
            while j < len(entities) and entities[j].start_pos < current.end_pos:
                overlapping.append(entities[j])
                j += 1
            
            # Select best entity from overlapping group
            best_entity = self._select_best_entity(overlapping)
            deduplicated.append(best_entity)
            
            i = j
            
        return deduplicated
    
    def _select_best_entity(self, entities: List[ExtractedEntity]) -> ExtractedEntity:
        """Select the best entity from overlapping entities"""
        if len(entities) == 1:
            return entities[0]
            
        # Priority: highest confidence, then longest text, then most specific type
        best = max(entities, key=lambda e: (
            e.confidence,
            len(e.text),
            self._get_entity_type_specificity(e.entity_type)
        ))
        
        # Merge metadata from all overlapping entities
        all_metadata = {}
        for entity in entities:
            all_metadata.update(entity.metadata)
        best.metadata.update(all_metadata)
        
        return best
    
    def _get_entity_type_specificity(self, entity_type: EntityCategory) -> int:
        """Get specificity score for entity type (higher = more specific)"""
        specificity_map = {
            EntityCategory.CREATIVE_WORK: 10,
            EntityCategory.INSTRUMENT: 9,
            EntityCategory.GENRE: 8,
            EntityCategory.PLATFORM: 7,
            EntityCategory.TECHNOLOGY: 6,
            EntityCategory.BRAND: 5,
            EntityCategory.EVENT: 4,
            EntityCategory.ORGANIZATION: 3,
            EntityCategory.PERSON: 2,
            EntityCategory.LOCATION: 1
        }
        return specificity_map.get(entity_type, 0)
    
    async def _extract_relationships(self, entities: List[ExtractedEntity], text: str) -> List[EntityRelation]:
        """Extract relationships between entities"""
        relationships = []
        
        # Simple relationship extraction based on proximity and patterns
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities[i+1:], i+1):
                # Skip if entities are too far apart
                if entity2.start_pos - entity1.end_pos > 100:
                    continue
                    
                relationship = self._identify_relationship(entity1, entity2, text)
                if relationship:
                    relationships.append(relationship)
                    
        return relationships
    
    def _identify_relationship(self, entity1: ExtractedEntity, entity2: ExtractedEntity, text: str) -> Optional[EntityRelation]:
        """Identify relationship between two entities"""
        # Extract text between entities
        between_text = text[entity1.end_pos:entity2.start_pos].lower().strip()
        
        # Define relationship patterns
        relationship_patterns = {
            'collaboration': ['featuring', 'ft.', 'with', 'and', 'collaborated with'],
            'ownership': ['by', 'from', 'of', 'belongs to'],
            'platform_presence': ['on', 'at', 'available on'],
            'creation': ['created', 'produced', 'made', 'composed'],
            'performance': ['performed', 'played', 'sang', 'recorded']
        }
        
        for relationship_type, patterns in relationship_patterns.items():
            if any(pattern in between_text for pattern in patterns):
                return EntityRelation(
                    source_entity=entity1,
                    target_entity=entity2,
                    relationship_type=relationship_type,
                    confidence=0.7
                )
                
        return None
    
    def _extract_context(self, text: str, start_pos: int, end_pos: int, context_size: int = 50) -> str:
        """Extract context around entity"""
        context_start = max(0, start_pos - context_size)
        context_end = min(len(text), end_pos + context_size)
        return text[context_start:context_end].strip()
    
    def _map_spacy_label_to_category(self, label: str) -> Optional[EntityCategory]:
        """Map spaCy entity labels to our categories"""
        mapping = {
            'PERSON': EntityCategory.PERSON,
            'ORG': EntityCategory.ORGANIZATION,
            'GPE': EntityCategory.LOCATION,
            'EVENT': EntityCategory.EVENT,
            'WORK_OF_ART': EntityCategory.CREATIVE_WORK,
            'PRODUCT': EntityCategory.BRAND,
            'DATE': EntityCategory.EVENT,
            'TIME': EntityCategory.EVENT
        }
        return mapping.get(label)
    
    def _map_transformer_label_to_category(self, label: str) -> Optional[EntityCategory]:
        """Map transformer entity labels to our categories"""
        mapping = {
            'PER': EntityCategory.PERSON,
            'ORG': EntityCategory.ORGANIZATION,
            'LOC': EntityCategory.LOCATION,
            'MISC': EntityCategory.CREATIVE_WORK
        }
        return mapping.get(label)
    
    def _map_pattern_type_to_category(self, pattern_type: str) -> Optional[EntityCategory]:
        """Map pattern types to entity categories"""
        mapping = {
            'social_handles': EntityCategory.PLATFORM,
            'urls': EntityCategory.PLATFORM,
            'email': EntityCategory.PERSON,
            'phone': EntityCategory.PERSON,
            'music_metadata': EntityCategory.CREATIVE_WORK,
            'timestamps': EntityCategory.EVENT
        }
        return mapping.get(pattern_type)
    
    def _map_vocabulary_type_to_category(self, vocab_type: str) -> Optional[EntityCategory]:
        """Map vocabulary types to entity categories"""
        mapping = {
            'music_genres': EntityCategory.GENRE,
            'instruments': EntityCategory.INSTRUMENT,
            'platforms': EntityCategory.PLATFORM,
            'content_types': EntityCategory.CREATIVE_WORK,
            'business_terms': EntityCategory.MONETIZATION
        }
        return mapping.get(vocab_type)
    
    def _calculate_overall_confidence(self, entities: List[ExtractedEntity]) -> float:
        """Calculate overall confidence score for extraction"""
        if not entities:
            return 0.0
            
        total_confidence = sum(entity.confidence for entity in entities)
        return total_confidence / len(entities)
    
    def _count_entities_by_type(self, entities: List[ExtractedEntity]) -> Dict[EntityCategory, int]:
        """Count entities by type"""
        counts = {}
        for entity in entities:
            counts[entity.entity_type] = counts.get(entity.entity_type, 0) + 1
        return counts
    
    def _update_extraction_stats(self, result: ExtractionResult):
        """Update extraction statistics"""
        self.extraction_stats['total_extractions'] += 1
        self.extraction_stats['successful_extractions'] += 1
        
        # Update average processing time
        current_avg = self.extraction_stats['avg_processing_time']
        total_extractions = self.extraction_stats['total_extractions']
        new_avg = ((current_avg * (total_extractions - 1)) + result.processing_time) / total_extractions
        self.extraction_stats['avg_processing_time'] = new_avg
        
        # Update entity type distribution
        for entity_type, count in result.entity_count_by_type.items():
            current_count = self.extraction_stats['entity_type_distribution'].get(entity_type.value, 0)
            self.extraction_stats['entity_type_distribution'][entity_type.value] = current_count + count
    
    async def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get extraction statistics"""



        return {
            **self.extraction_stats,
            'cache_stats': cache_manager.get_stats(),
            'model_info': {
                'loaded_models': list(self.models.keys()),
                'spacy_available': self.nlp_en is not None,
                'multilang_models': list(self.nlp_multilang.keys()) if hasattr(self, 'nlp_multilang') else []
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for entity extraction service"""



        return {
            'status': 'healthy',
            'models_loaded': len(self.models),
            'spacy_available': self.nlp_en is not None,
            'cache_size': cache_manager.get_cache_size(),
            'total_extractions': self.extraction_stats['total_extractions'],
            'avg_processing_time': self.extraction_stats['avg_processing_time']
        }
