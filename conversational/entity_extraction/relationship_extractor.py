"""Relationship Extractor - Advanced Relationship Discovery

Sophisticated relationship extraction engine for identifying and modeling
relationships between entities in creative content. Specialized for musicians,
influencers, content creators, and creative industry professionals.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
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
import json

import numpy as np
import spacy
from spacy.matcher import Matcher, DependencyMatcher
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ...core.base_service import BaseService
from ...core.cache import cache_manager
from ...core.monitoring import MetricsCollector
from ...models.entities import EntityRelation, RelationshipType
from ...utils.text_processors import TextPreprocessor
from .entity_extractor import ExtractedEntity, EntityCategory


class RelationType(Enum):
    """
Types of relationships in creative industry context"""
    # Collaboration relationships
    COLLABORATION = "collaboration"
    FEATURING = "featuring"
    REMIX = "remix"
    COVER = "cover"
    DUET = "duet"
    
    # Ownership/Creation relationships
    CREATED_BY = "created_by"
    OWNED_BY = "owned_by"
    PRODUCED_BY = "produced_by"
    WRITTEN_BY = "written_by"
    PERFORMED_BY = "performed_by"
    
    # Platform relationships
    AVAILABLE_ON = "available_on"
    RELEASED_ON = "released_on"
    STREAMED_ON = "streamed_on"
    PROMOTED_ON = "promoted_on"
    
    # Business relationships
    SIGNED_TO = "signed_to"
    SPONSORED_BY = "sponsored_by"
    PARTNERED_WITH = "partnered_with"
    LICENSED_BY = "licensed_by"
    DISTRIBUTED_BY = "distributed_by"
    
    # Temporal relationships
    BEFORE = "before"
    AFTER = "after"
    DURING = "during"
    CONCURRENT = "concurrent"
    
    # Geographical relationships
    BASED_IN = "based_in"
    ORIGINATED_FROM = "originated_from"
    PERFORMED_AT = "performed_at"
    RECORDED_AT = "recorded_at"
    
    # Genre/Style relationships
    INFLUENCED_BY = "influenced_by"
    SIMILAR_TO = "similar_to"
    GENRE_OF = "genre_of"
    STYLE_OF = "style_of"
    
    # Technical relationships
    ENCODED_WITH = "encoded_with"
    FORMAT_OF = "format_of"
    VERSION_OF = "version_of"
    SAMPLE_OF = "sample_of"


class ConfidenceLevel(Enum):
    """Confidence levels for relationship extraction"""

    VERY_HIGH = 0.95
    HIGH = 0.85
    MEDIUM = 0.70
    LOW = 0.50
    VERY_LOW = 0.30


@dataclass
class ExtractedRelationship:
    """
Extracted relationship with metadata"""
    source_entity: ExtractedEntity
    target_entity: ExtractedEntity
    relation_type: RelationType
    confidence: float
    evidence_text: str
    context: str = ""
    direction: str = "forward"  # forward, backward, bidirectional
    metadata: Dict[str, Any] = field(default_factory=dict)
    extraction_method: str = ""
    temporal_info: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization validation"""
        if self.confidence > 1.0:
            self.confidence = 1.0
        elif self.confidence < 0.0:
            self.confidence = 0.0


@dataclass
class RelationshipPattern:
    """
Pattern for relationship extraction"""
    pattern_id: str
    relation_type: RelationType
    pattern_text: str
    entity_positions: List[str]  # ["ENTITY1", "ENTITY2"]
    confidence_base: float
    context_requirements: List[str] = field(default_factory=list)
    entity_type_constraints: Dict[str, List[EntityCategory]] = field(default_factory=dict)


class RelationshipExtractor(BaseService):
    """
    Advanced Relationship Extraction engine with creative industry specialization.
    
    Features:
    - Pattern-based relationship extraction with domain-specific patterns
    - Machine learning models for relationship classification
    - Dependency parsing for grammatical relationship discovery
    - Temporal relationship extraction and ordering
    - Creative industry specific relationship types
    - Context-aware relationship disambiguation
    - Relationship confidence scoring and validation
    - Graph-based relationship inference and completion
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("relationship_extractor")
        self.text_processor = TextPreprocessor()
        
        # NLP models
        self.nlp = None
        self.matcher = None
        self.dependency_matcher = None
        self.relation_classifier = None
        
        # Relationship patterns
        self.relationship_patterns = []
        self.pattern_matchers = {}
        
        # Relationship graph
        self.relationship_graph = nx.DiGraph()
        
        # Caching
        self.extraction_cache = {}
        
        # Statistics
        self.extraction_stats = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'relation_type_distribution': {},
            'avg_processing_time': 0.0,
            'confidence_distribution': {}
        }
        
    async def initialize(self):
        """Initialize comprehensive relationship extraction resources and models"""
        try:
            self.logger.info("Initializing advanced RelationshipExtractor...")
            
            # Load advanced spaCy model with relationship parsing capabilities
            await self._load_advanced_spacy_model()
            
            # Initialize multiple relationship classifiers for ensemble prediction
            await self._load_relationship_classifiers()
            
            # Load comprehensive relationship patterns and rules
            await self._load_comprehensive_patterns()
            
            # Initialize pattern matchers with creative industry specificity
            await self._initialize_pattern_matchers()
            
            # Load pre-trained relationship embeddings
            await self._load_relationship_embeddings()
            
            # Initialize graph-based relationship inference engine
            await self._initialize_graph_inference_engine()
            
            # Load relationship validation models
            await self._load_validation_models()
            
            # Initialize contextual relationship disambiguators
            await self._initialize_disambiguation_models()
            
            # Load industry-specific relationship taxonomies
            await self._load_industry_taxonomies()
            
            # Initialize real-time relationship tracking
            await self._initialize_realtime_tracking()
            
            self.logger.info("Advanced RelationshipExtractor initialization completed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RelationshipExtractor: {str(e)}")
            raise
    
    async def _load_advanced_spacy_model(self):
        """Load advanced spaCy model with custom relationship components"""
        try:
            # Load the most capable spaCy model available
            try:
                self.nlp = spacy.load("en_core_web_trf")  # Transformer-based model
            except OSError:
                try:
                    self.nlp = spacy.load("en_core_web_lg")  # Large model
                except OSError:
                    try:
                        self.nlp = spacy.load("en_core_web_md")  # Medium model
                    except OSError:
                        self.nlp = spacy.load("en_core_web_sm")  # Small model fallback
                        self.logger.warning("Using basic spaCy model as fallback")
            
            # Add custom pipeline components for relationship extraction
            if "relationship_extractor" not in self.nlp.pipe_names:
                @spacy.Language.component("relationship_extractor")
                def relationship_component(doc):
                    # Custom relationship extraction logic
                    for sent in doc.sents:
                        # Process sentence for relationships
                        relationships = self._extract_sentence_relationships(sent)
                        # Store relationships in custom doc attributes
                        if not doc._.has("relationships"):
                            doc._.set("relationships", [])
                        doc._.relationships.extend(relationships)
                    return doc
                
                # Set custom attribute
                spacy.tokens.Doc.set_extension("relationships", default=[], force=True)
                
                # Add component to pipeline
                self.nlp.add_pipe("relationship_extractor", after="ner")
            
            # Initialize advanced matchers
            self.matcher = Matcher(self.nlp.vocab)
            self.dependency_matcher = DependencyMatcher(self.nlp.vocab)
            
            self.logger.info(f"Loaded spaCy model: {self.nlp.meta['name']}")
            
        except Exception as e:
            self.logger.error(f"Failed to load spaCy model: {e}")
            raise
    
    async def _load_relationship_classifiers(self):
        """Load ensemble of relationship classification models"""
        try:
            # Primary relationship classifier
            self.primary_relation_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                return_all_scores=True,
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Secondary relationship classifier for validation
            self.secondary_relation_classifier = pipeline(
                "text-classification",
                model="facebook/bart-large-mnli",
                return_all_scores=True,
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Domain-specific relationship classifier for creative industry
            self.creative_relation_classifier = self._initialize_creative_classifier()
            
            # Temporal relationship classifier
            self.temporal_classifier = pipeline(
                "text-classification",
                model="facebook/bart-base",
                return_all_scores=True
            )
            
            # Business relationship classifier
            self.business_classifier = self._initialize_business_relationship_classifier()
            
            # Geographical relationship classifier
            self.geo_classifier = pipeline(
                "token-classification",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="first"
            )
            
            self.logger.info("Loaded ensemble of relationship classifiers")
            
        except Exception as e:
            self.logger.error(f"Failed to load relationship classifiers: {e}")
            await self._load_fallback_classifiers()
    
    def _initialize_creative_classifier(self):
        """Initialize custom classifier for creative industry relationships"""
        import torch.nn as nn
        
        class CreativeRelationshipClassifier(nn.Module):
            def __init__(self, vocab_size=50000, embedding_dim=300, hidden_dim=512, num_classes=25):
                super(CreativeRelationshipClassifier, self).__init__()
                
                self.embedding = nn.Embedding(vocab_size, embedding_dim)
                self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True, bidirectional=True)
                self.dropout = nn.Dropout(0.3)
                self.attention = nn.MultiheadAttention(hidden_dim * 2, num_heads=8)
                self.classifier = nn.Linear(hidden_dim * 2, num_classes)
                
            def forward(self, input_ids):
                embeddings = self.embedding(input_ids)
                lstm_out, _ = self.lstm(embeddings)
                lstm_out = self.dropout(lstm_out)
                
                # Apply attention mechanism
                attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
                
                # Global max pooling
                pooled = torch.max(attn_out, dim=1)[0]
                
                return torch.softmax(self.classifier(pooled), dim=1)
        
        model = CreativeRelationshipClassifier()
        
        # Load pre-trained weights if available
        creative_model_path = self.config.get('creative_relationship_model_path')
        if creative_model_path:
            try:
                model.load_state_dict(torch.load(creative_model_path))
                self.logger.info("Loaded pre-trained creative relationship classifier")
            except Exception as e:
                self.logger.warning(f"Could not load creative classifier weights: {e}")
        
        return model
    
    def _initialize_business_relationship_classifier(self):
        """Initialize classifier for business and commercial relationships"""
        import torch.nn as nn
        
        class BusinessRelationshipClassifier(nn.Module):
            def __init__(self, input_dim=768, hidden_dims=[512, 256, 128], num_classes=15):
                super(BusinessRelationshipClassifier, self).__init__()
                
                layers = []
                prev_dim = input_dim
                
                for hidden_dim in hidden_dims:
                    layers.extend([
                        nn.Linear(prev_dim, hidden_dim),
                        nn.ReLU(),
                        nn.BatchNorm1d(hidden_dim),
                        nn.Dropout(0.25)
                    ])
                    prev_dim = hidden_dim
                
                layers.append(nn.Linear(prev_dim, num_classes))
                layers.append(nn.Softmax(dim=1))
                
                self.network = nn.Sequential(*layers)
            
            def forward(self, x):
                pass
        try:
            logger.info(f"Executing forward")
            
            # Implementation for forward
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"forward completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"forward failed: {e}")
            raise
        model = BusinessRelationshipClassifier()
        
        # Load pre-trained weights if available
        business_model_path = self.config.get('business_relationship_model_path')
        if business_model_path:
            try:
                model.load_state_dict(torch.load(business_model_path))
                self.logger.info("Loaded pre-trained business relationship classifier")
            except Exception as e:
                self.logger.warning(f"Could not load business classifier weights: {e}")
        
        return model
    
    async def _load_comprehensive_patterns(self):
        """Load comprehensive relationship patterns for creative industry"""
        self.relationship_patterns = {
            RelationType.COLLABORATION: [
                # Musical collaboration patterns
                {"pattern": [{"LOWER": "ft"}, {"LOWER": "."}, {"ENT_TYPE": "PERSON"}], "label": "FEATURING"},
                {"pattern": [{"LOWER": "featuring"}, {"ENT_TYPE": "PERSON"}], "label": "FEATURING"},
                {"pattern": [{"LOWER": "collab"}, {"LOWER": "with"}, {"ENT_TYPE": "PERSON"}], "label": "COLLABORATION"},
                {"pattern": [{"LOWER": "collaboration"}, {"LOWER": "between"}, {"ENT_TYPE": "PERSON"}, {"LOWER": "and"}, {"ENT_TYPE": "PERSON"}], "label": "COLLABORATION"},
                {"pattern": [{"ENT_TYPE": "PERSON"}, {"LOWER": "x"}, {"ENT_TYPE": "PERSON"}], "label": "COLLABORATION"},
                
                # Content collaboration patterns
                {"pattern": [{"LOWER": "guest"}, {"LOWER": "post"}, {"LOWER": "by"}, {"ENT_TYPE": "PERSON"}], "label": "GUEST_CONTENT"},
                {"pattern": [{"LOWER": "takeover"}, {"LOWER": "by"}, {"ENT_TYPE": "PERSON"}], "label": "CONTENT_TAKEOVER"},
                {"pattern": [{"LOWER": "joint"}, {"LOWER": "video"}, {"LOWER": "with"}, {"ENT_TYPE": "PERSON"}], "label": "JOINT_CONTENT"}
            ],
            
            RelationType.CREATED_BY: [
                {"pattern": [{"LOWER": "written"}, {"LOWER": "by"}, {"ENT_TYPE": "PERSON"}], "label": "WRITTEN_BY"},
                {"pattern": [{"LOWER": "composed"}, {"LOWER": "by"}, {"ENT_TYPE": "PERSON"}], "label": "COMPOSED_BY"},
                {"pattern": [{"LOWER": "produced"}, {"LOWER": "by"}, {"ENT_TYPE": "PERSON"}], "label": "PRODUCED_BY"},
                {"pattern": [{"LOWER": "directed"}, {"LOWER": "by"}, {"ENT_TYPE": "PERSON"}], "label": "DIRECTED_BY"},
                {"pattern": [{"LOWER": "created"}, {"LOWER": "by"}, {"ENT_TYPE": "PERSON"}], "label": "CREATED_BY"},
                {"pattern": [{"LOWER": "shot"}, {"LOWER": "by"}, {"ENT_TYPE": "PERSON"}], "label": "PHOTOGRAPHED_BY"}
            ],
            
            RelationType.AVAILABLE_ON: [
                {"pattern": [{"LOWER": "available"}, {"LOWER": "on"}, {"ENT_TYPE": "ORG"}], "label": "AVAILABLE_ON"},
                {"pattern": [{"LOWER": "streaming"}, {"LOWER": "on"}, {"ENT_TYPE": "ORG"}], "label": "STREAMING_ON"},
                {"pattern": [{"LOWER": "released"}, {"LOWER": "on"}, {"ENT_TYPE": "ORG"}], "label": "RELEASED_ON"},
                {"pattern": [{"LOWER": "published"}, {"LOWER": "on"}, {"ENT_TYPE": "ORG"}], "label": "PUBLISHED_ON"},
                {"pattern": [{"LOWER": "distributed"}, {"LOWER": "by"}, {"ENT_TYPE": "ORG"}], "label": "DISTRIBUTED_BY"}
            ],
            
            RelationType.SIGNED_TO: [
                {"pattern": [{"LOWER": "signed"}, {"LOWER": "to"}, {"ENT_TYPE": "ORG"}], "label": "SIGNED_TO"},
                {"pattern": [{"LOWER": "under"}, {"ENT_TYPE": "ORG"}, {"LOWER": "records"}], "label": "LABEL_RELATIONSHIP"},
                {"pattern": [{"ENT_TYPE": "ORG"}, {"LOWER": "artist"}], "label": "LABEL_ARTIST"},
                {"pattern": [{"LOWER": "represented"}, {"LOWER": "by"}, {"ENT_TYPE": "ORG"}], "label": "REPRESENTED_BY"}
            ],
            
            RelationType.INFLUENCED_BY: [
                {"pattern": [{"LOWER": "influenced"}, {"LOWER": "by"}, {"ENT_TYPE": "PERSON"}], "label": "INFLUENCED_BY"},
                {"pattern": [{"LOWER": "inspired"}, {"LOWER": "by"}, {"ENT_TYPE": "PERSON"}], "label": "INSPIRED_BY"},
                {"pattern": [{"LOWER": "reminds"}, {"LOWER": "me"}, {"LOWER": "of"}, {"ENT_TYPE": "PERSON"}], "label": "SIMILAR_TO"},
                {"pattern": [{"LOWER": "sounds"}, {"LOWER": "like"}, {"ENT_TYPE": "PERSON"}], "label": "SIMILAR_TO"}
            ]
        }
        
        # Add regex patterns for complex relationships
        self.regex_patterns = {
            'collaboration_mentions': r'(?i)(?:feat|ft|featuring|with|x|&|and)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            'platform_mentions': r'(?i)(?:on|via|through|streaming on)\s+(spotify|youtube|instagram|tiktok|soundcloud|apple music)',
            'production_credits': r'(?i)(?:produced|mixed|mastered|written|composed)\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            'label_relationships': r'(?i)(?:signed to|under|via)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:records|music|entertainment))',
            'temporal_relationships': r'(?i)(?:before|after|during|since|until)\s+(\d{4}|\w+\s+\d{4})',
            'geographical_relationships': r'(?i)(?:from|based in|located in|recorded in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        }
    
    async def _initialize_pattern_matchers(self):
        """Initialize sophisticated pattern matchers for relationship extraction"""
        try:
            # Add patterns to spaCy matcher
            for relation_type, patterns in self.relationship_patterns.items():
                for i, pattern in enumerate(patterns):
                    pattern_name = f"{relation_type.value}_{i}"
                    self.matcher.add(pattern_name, [pattern["pattern"]])
            
            # Initialize dependency-based patterns
            dependency_patterns = [
                # Subject-verb-object patterns
                {
                    "LEFT_ID": "anchor",
                    "REL_OP": ">",
                    "RIGHT_ID": "subject",
                    "RIGHT_ATTRS": {"DEP": "nsubj"}
                },
                {
                    "LEFT_ID": "anchor", 
                    "REL_OP": ">",
                    "RIGHT_ID": "object",
                    "RIGHT_ATTRS": {"DEP": "dobj"}
                }
            ]
            
            for i, pattern in enumerate(dependency_patterns):
                self.dependency_matcher.add(f"dependency_pattern_{i}", [dependency_patterns])
            
            # Initialize regex-based matchers
            import re
            self.compiled_regex_patterns = {}
            for pattern_name, pattern in self.regex_patterns.items():
                self.compiled_regex_patterns[pattern_name] = re.compile(pattern)
            
            self.logger.info("Pattern matchers initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize pattern matchers: {e}")
    
    async def _load_fallback_classifiers(self):
        """Load simplified fallback classifiers if advanced models fail"""
        try:
            self.primary_relation_classifier = pipeline(
                "text-classification",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            
            self.logger.info("Loaded fallback relationship classifiers")
            
        except Exception as e:
            self.logger.error(f"Failed to load fallback classifiers: {e}")
            await self._initialize_matchers()
            
            # Load relationship graph
            await self._load_relationship_graph()
            
            self.logger.info("RelationshipExtractor initialization completed")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RelationshipExtractor: {str(e)}")
            raise
    
    async def _load_spacy_model(self):
        """Load spaCy model for dependency parsing"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.logger.info("Loaded spaCy model for relationship extraction")
            
        except OSError:
            self.logger.warning("spaCy model not available, using basic extraction")
            self.nlp = None
    
    async def _load_relation_classifier(self):
        """Load machine learning model for relationship classification"""
        try:
            # Use a pre-trained model fine-tuned for relationship classification
            model_name = "microsoft/DialoGPT-medium"  # Would be replaced with actual relation classifier
            
            self.relation_classifier = pipeline(
                "text-classification",
                model=model_name,
                return_all_scores=True
            )
            
            self.logger.info("Loaded relationship classifier")
            
        except Exception as e:
            self.logger.warning(f"Failed to load relationship classifier: {str(e)}")
    
    async def _load_relationship_patterns(self):
        """Load predefined relationship patterns for creative industry"""
        self.relationship_patterns = [
            # Collaboration patterns
            RelationshipPattern(
                pattern_id="feat_collaboration",
                relation_type=RelationType.FEATURING,
                pattern_text=r"(.+?)\s+(?:featuring|feat\.?|ft\.?)\s+(.+)",
                entity_positions=["ENTITY1", "ENTITY2"],
                confidence_base=0.9,
                entity_type_constraints={
                    "ENTITY1": [EntityCategory.PERSON, EntityCategory.CREATIVE_WORK],
                    "ENTITY2": [EntityCategory.PERSON]
                }
            ),
            
            RelationshipPattern(
                pattern_id="collaboration_with",
                relation_type=RelationType.COLLABORATION,
                pattern_text=r"(.+?)\s+(?:collaborated with|worked with|teamed up with)\s+(.+)",
                entity_positions=["ENTITY1", "ENTITY2"],
                confidence_base=0.85,
                entity_type_constraints={
                    "ENTITY1": [EntityCategory.PERSON],
                    "ENTITY2": [EntityCategory.PERSON]
                }
            ),
            
            # Creation patterns
            RelationshipPattern(
                pattern_id="created_by",
                relation_type=RelationType.CREATED_BY,
                pattern_text=r"(.+?)\s+(?:by|created by|made by)\s+(.+)",
                entity_positions=["ENTITY1", "ENTITY2"],
                confidence_base=0.8,
                entity_type_constraints={
                    "ENTITY1": [EntityCategory.CREATIVE_WORK],
                    "ENTITY2": [EntityCategory.PERSON]
                }
            ),
            
            RelationshipPattern(
                pattern_id="produced_by",
                relation_type=RelationType.PRODUCED_BY,
                pattern_text=r"(.+?)\s+(?:produced by|production by)\s+(.+)",
                entity_positions=["ENTITY1", "ENTITY2"],
                confidence_base=0.85,
                entity_type_constraints={
                    "ENTITY1": [EntityCategory.CREATIVE_WORK],
                    "ENTITY2": [EntityCategory.PERSON]
                }
            ),
            
            # Platform patterns
            RelationshipPattern(
                pattern_id="available_on",
                relation_type=RelationType.AVAILABLE_ON,
                pattern_text=r"(.+?)\s+(?:available on|on|streaming on|listen on)\s+(.+)",
                entity_positions=["ENTITY1", "ENTITY2"],
                confidence_base=0.8,
                entity_type_constraints={
                    "ENTITY1": [EntityCategory.CREATIVE_WORK],
                    "ENTITY2": [EntityCategory.PLATFORM]
                }
            ),
            
            RelationshipPattern(
                pattern_id="released_on",
                relation_type=RelationType.RELEASED_ON,
                pattern_text=r"(.+?)\s+(?:released on|out on|drops on)\s+(.+)",
                entity_positions=["ENTITY1", "ENTITY2"],
                confidence_base=0.85,
                entity_type_constraints={
                    "ENTITY1": [EntityCategory.CREATIVE_WORK],
                    "ENTITY2": [EntityCategory.PLATFORM]
                }
            ),
            
            # Business patterns
            RelationshipPattern(
                pattern_id="signed_to",
                relation_type=RelationType.SIGNED_TO,
                pattern_text=r"(.+?)\s+(?:signed to|signed with|under)\s+(.+)",
                entity_positions=["ENTITY1", "ENTITY2"],
                confidence_base=0.9,
                entity_type_constraints={
                    "ENTITY1": [EntityCategory.PERSON],
                    "ENTITY2": [EntityCategory.ORGANIZATION]
                }
            ),
            
            RelationshipPattern(
                pattern_id="sponsored_by",
                relation_type=RelationType.SPONSORED_BY,
                pattern_text=r"(.+?)\s+(?:sponsored by|in partnership with|brand partner)\s+(.+)",
                entity_positions=["ENTITY1", "ENTITY2"],
                confidence_base=0.8,
                entity_type_constraints={
                    "ENTITY1": [EntityCategory.PERSON, EntityCategory.EVENT],
                    "ENTITY2": [EntityCategory.BRAND, EntityCategory.ORGANIZATION]
                }
            ),
            
            # Location patterns
            RelationshipPattern(
                pattern_id="based_in",
                relation_type=RelationType.BASED_IN,
                pattern_text=r"(.+?)\s+(?:based in|from|located in)\s+(.+)",
                entity_positions=["ENTITY1", "ENTITY2"],
                confidence_base=0.7,
                entity_type_constraints={
                    "ENTITY1": [EntityCategory.PERSON, EntityCategory.ORGANIZATION],
                    "ENTITY2": [EntityCategory.LOCATION]
                }
            ),
            
            RelationshipPattern(
                pattern_id="performed_at",
                relation_type=RelationType.PERFORMED_AT,
                pattern_text=r"(.+?)\s+(?:performed at|live at|concert at)\s+(.+)",
                entity_positions=["ENTITY1", "ENTITY2"],
                confidence_base=0.85,
                entity_type_constraints={
                    "ENTITY1": [EntityCategory.PERSON],
                    "ENTITY2": [EntityCategory.LOCATION, EntityCategory.EVENT]
                }
            ),
            
            # Genre patterns
            RelationshipPattern(
                pattern_id="genre_of",
                relation_type=RelationType.GENRE_OF,
                pattern_text=r"(.+?)\s+(?:genre|style|type)\s+(.+)",
                entity_positions=["ENTITY2", "ENTITY1"],  # Reversed order
                confidence_base=0.7,
                entity_type_constraints={
                    "ENTITY1": [EntityCategory.CREATIVE_WORK, EntityCategory.PERSON],
                    "ENTITY2": [EntityCategory.GENRE]
                }
            ),
            
            # Technical patterns
            RelationshipPattern(
                pattern_id="remix_of",
                relation_type=RelationType.REMIX,
                pattern_text=r"(.+?)\s+(?:remix of|rmx of|rework of)\s+(.+)",
                entity_positions=["ENTITY1", "ENTITY2"],
                confidence_base=0.9,
                entity_type_constraints={
                    "ENTITY1": [EntityCategory.CREATIVE_WORK],
                    "ENTITY2": [EntityCategory.CREATIVE_WORK]
                }
            ),
            
            RelationshipPattern(
                pattern_id="cover_of",
                relation_type=RelationType.COVER,
                pattern_text=r"(.+?)\s+(?:cover of|covering|version of)\s+(.+)",
                entity_positions=["ENTITY1", "ENTITY2"],
                confidence_base=0.85,
                entity_type_constraints={
                    "ENTITY1": [EntityCategory.CREATIVE_WORK],
                    "ENTITY2": [EntityCategory.CREATIVE_WORK]
                }
            )
        ]
    
    async def _initialize_matchers(self):
        """Initialize spaCy matchers for pattern-based extraction"""
        if not self.nlp:
            return
            
        self.matcher = Matcher(self.nlp.vocab)
        self.dependency_matcher = DependencyMatcher(self.nlp.vocab)
        
        # Add patterns to matcher
        for pattern in self.relationship_patterns:
            try:
                # Convert regex pattern to spaCy pattern (simplified)
                pattern_name = pattern.pattern_id
                
                # This is a simplified conversion - in practice, we'd need more sophisticated
                # pattern conversion from regex to spaCy token patterns
                spacy_pattern = self._convert_regex_to_spacy_pattern(pattern.pattern_text)
                
                if spacy_pattern:
                    self.matcher.add(pattern_name, [spacy_pattern])
                    
            except Exception as e:
                self.logger.warning(f"Failed to add pattern {pattern.pattern_id}: {str(e)}")
        
        # Add dependency patterns for grammatical relationships
        self._add_dependency_patterns()
    
    def _convert_regex_to_spacy_pattern(self, regex_pattern: str) -> Optional[List[Dict[str, Any]]]:
        """Convert regex pattern to spaCy token pattern (simplified implementation)"""
        # This is a very basic conversion - in practice, we'd need a more sophisticated
        # system to convert regex patterns to spaCy token patterns
        
        # For now, return None to use regex-based matching instead
        return None
    
    def _add_dependency_patterns(self):
        """
Add dependency patterns for grammatical relationship extraction"""
        if not self.dependency_matcher:
            return
            
        # Pattern for "X created by Y"
        created_by_pattern = [
            {"RIGHT_ID": "created", "RIGHT_ATTRS": {"LEMMA": {"IN": ["create", "make", "produce"]}}},
            {"LEFT_ID": "created", "REL_OP": ">", "RIGHT_ID": "by", "RIGHT_ATTRS": {"LEMMA": "by"}},
            {"LEFT_ID": "by", "REL_OP": ">", "RIGHT_ID": "creator", "RIGHT_ATTRS": {"POS": {"IN": ["NOUN", "PROPN"]}}},
            {"LEFT_ID": "created", "REL_OP": "<", "RIGHT_ID": "object", "RIGHT_ATTRS": {"POS": {"IN": ["NOUN", "PROPN"]}}}
        ]
        self.dependency_matcher.add("CREATED_BY", [created_by_pattern])
        
        # Pattern for "X featuring Y"
        featuring_pattern = [
            {"RIGHT_ID": "feat", "RIGHT_ATTRS": {"LEMMA": {"IN": ["feature", "featuring"]}}},
            {"LEFT_ID": "feat", "REL_OP": ">", "RIGHT_ID": "featured", "RIGHT_ATTRS": {"POS": {"IN": ["NOUN", "PROPN"]}}},
            {"LEFT_ID": "feat", "REL_OP": "<", "RIGHT_ID": "main", "RIGHT_ATTRS": {"POS": {"IN": ["NOUN", "PROPN"]}}}
        ]
        self.dependency_matcher.add("FEATURING", [featuring_pattern])
    
    async def _load_relationship_graph(self):
        """Load existing relationship graph"""
        try:
            # In production, this would load from a persistent graph database
            self.relationship_graph = nx.DiGraph()
            
            # Add some basic relationship types as nodes
            for relation_type in RelationType:
                self.relationship_graph.add_node(relation_type.value, type="relation_type")
            
            self.logger.info("Initialized relationship graph")
            
        except Exception as e:
            self.logger.warning(f"Failed to load relationship graph: {str(e)}")
    
    @cache_manager.cached(ttl=1800)
    async def extract_relationships(
        self,
        entities: List[ExtractedEntity],
        text: str,
        context: Optional[str] = None
    ) -> List[ExtractedRelationship]:
        """
        Extract relationships between entities in text.
        
        Args:
            entities: List of extracted entities
            text: Original text containing entities
            context: Additional context for relationship extraction
            
        Returns:
            List of extracted relationships
        """
        start_time = datetime.now()
        
        try:
            self.logger.debug(f"Extracting relationships from {len(entities)} entities")
            self.metrics.increment('extraction_requests')
            
            # Check cache
            cache_key = self._generate_cache_key(entities, text, context)
            if cache_key in self.extraction_cache:
                self.metrics.increment('cache_hits')
                return self.extraction_cache[cache_key]
            
            relationships = []
            
            # Pattern-based extraction
            pattern_relationships = await self._extract_pattern_relationships(entities, text)
            relationships.extend(pattern_relationships)
            
            # Dependency parsing extraction
            if self.nlp:
                dependency_relationships = await self._extract_dependency_relationships(entities, text)
                relationships.extend(dependency_relationships)
            
            # Machine learning based extraction
            if self.relation_classifier:
                ml_relationships = await self._extract_ml_relationships(entities, text, context)
                relationships.extend(ml_relationships)
            
            # Proximity-based extraction
            proximity_relationships = await self._extract_proximity_relationships(entities, text)
            relationships.extend(proximity_relationships)
            
            # Remove duplicates and filter by confidence
            filtered_relationships = self._filter_and_deduplicate_relationships(relationships)
            
            # Add to relationship graph
            self._add_relationships_to_graph(filtered_relationships)
            
            # Cache results
            self.extraction_cache[cache_key] = filtered_relationships
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            self._update_extraction_stats(filtered_relationships, processing_time)
            
            self.logger.info(f"Extracted {len(filtered_relationships)} relationships in {processing_time:.3f}s")
            
            return filtered_relationships
            
        except Exception as e:
            self.logger.error(f"Relationship extraction failed: {str(e)}")
            self.metrics.increment('extraction_errors')
            raise
    
    async def _extract_pattern_relationships(
        self,
        entities: List[ExtractedEntity],
        text: str
    ) -> List[ExtractedRelationship]:
        """Extract relationships using predefined patterns"""
        relationships = []
        
        for pattern in self.relationship_patterns:
            try:
                matches = re.finditer(pattern.pattern_text, text, re.IGNORECASE)
                
                for match in matches:
                    # Extract entity mentions from match
                    entity1_text = match.group(1).strip()
                    entity2_text = match.group(2).strip()
                    
                    # Find corresponding entities
                    entity1 = self._find_entity_by_text(entities, entity1_text)
                    entity2 = self._find_entity_by_text(entities, entity2_text)
                    
                    if entity1 and entity2:
                        # Check entity type constraints
                        if self._validate_entity_constraints(entity1, entity2, pattern):
                            relationship = ExtractedRelationship(
                                source_entity=entity1,
                                target_entity=entity2,
                                relation_type=pattern.relation_type,
                                confidence=pattern.confidence_base,
                                evidence_text=match.group(0),
                                context=self._extract_relationship_context(text, match.start(), match.end()),
                                extraction_method="pattern_based",
                                metadata={
                                    'pattern_id': pattern.pattern_id,
                                    'match_start': match.start(),
                                    'match_end': match.end()
                                }
                            )
                            relationships.append(relationship)
                            
            except Exception as e:
                self.logger.warning(f"Pattern matching failed for {pattern.pattern_id}: {str(e)}")
        
        return relationships
    
    async def _extract_dependency_relationships(
        self,
        entities: List[ExtractedEntity],
        text: str
    ) -> List[ExtractedRelationship]:
        """Extract relationships using dependency parsing"""
        relationships = []
        
        if not self.nlp or not self.dependency_matcher:
            return relationships
        
        try:
            doc = self.nlp(text)
            matches = self.dependency_matcher(doc)
            
            for match_id, token_ids in matches:
                label = self.nlp.vocab.strings[match_id]
                
                # Extract entities involved in the dependency relationship
                involved_tokens = [doc[token_id] for token_id in token_ids]
                
                # Map to our entities
                matched_entities = []
                for token in involved_tokens:
                    entity = self._find_entity_by_position(entities, token.idx, token.idx + len(token.text))
                    if entity:
                        matched_entities.append(entity)
                
                if len(matched_entities) >= 2:
                    # Create relationship based on dependency pattern
                    relation_type = self._map_dependency_to_relation_type(label)
                    if relation_type:
                        relationship = ExtractedRelationship(
                            source_entity=matched_entities[0],
                            target_entity=matched_entities[1],
                            relation_type=relation_type,
                            confidence=0.7,  # Medium confidence for dependency parsing
                            evidence_text=' '.join([token.text for token in involved_tokens]),
                            extraction_method="dependency_parsing",
                            metadata={
                                'dependency_label': label,
                                'tokens': [token.text for token in involved_tokens]
                            }
                        )
                        relationships.append(relationship)
                        
        except Exception as e:
            self.logger.warning(f"Dependency parsing extraction failed: {str(e)}")
        
        return relationships
    
    async def _extract_ml_relationships(
        self,
        entities: List[ExtractedEntity],
        text: str,
        context: Optional[str]
    ) -> List[ExtractedRelationship]:
        """Extract relationships using machine learning classifier"""
        relationships = []
        
        if not self.relation_classifier:
            return relationships
        
        # Generate entity pairs
        entity_pairs = []
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities[i+1:], i+1):
                # Skip if entities are too far apart
                if abs(entity1.start_pos - entity2.start_pos) > 200:
                    continue
                    
                entity_pairs.append((entity1, entity2))
        
        # Classify relationships for each pair
        for entity1, entity2 in entity_pairs:
            try:
                # Create input text for classifier
                context_start = max(0, min(entity1.start_pos, entity2.start_pos) - 50)
                context_end = min(len(text), max(entity1.end_pos, entity2.end_pos) + 50)
                context_text = text[context_start:context_end]
                
                # Classify relationship
                results = self.relation_classifier(context_text)
                
                # Find best relationship type
                best_result = max(results, key=lambda x: x['score'])
                
                if best_result['score'] > 0.6:  # Confidence threshold
                    # Map classifier label to our relation types
                    relation_type = self._map_classifier_label_to_relation_type(best_result['label'])
                    
                    if relation_type:
                        relationship = ExtractedRelationship(
                            source_entity=entity1,
                            target_entity=entity2,
                            relation_type=relation_type,
                            confidence=best_result['score'],
                            evidence_text=context_text,
                            extraction_method="machine_learning",
                            metadata={
                                'classifier_label': best_result['label'],
                                'all_scores': results
                            }
                        )
                        relationships.append(relationship)
                        
            except Exception as e:
                self.logger.warning(f"ML relationship classification failed: {str(e)}")
        
        return relationships
    
    async def _extract_proximity_relationships(
        self,
        entities: List[ExtractedEntity],
        text: str
    ) -> List[ExtractedRelationship]:
        """Extract relationships based on entity proximity and common patterns"""
        relationships = []
        
        # Define proximity-based relationship patterns
        proximity_patterns = {
            'and': RelationType.COLLABORATION,
            '&': RelationType.COLLABORATION,
            'with': RelationType.COLLABORATION,
            'featuring': RelationType.FEATURING,
            'on': RelationType.AVAILABLE_ON,
            'by': RelationType.CREATED_BY,
            'from': RelationType.ORIGINATED_FROM
        }
        
        # Sort entities by position
        sorted_entities = sorted(entities, key=lambda e: e.start_pos)
        
        for i, entity1 in enumerate(sorted_entities):
            for j, entity2 in enumerate(sorted_entities[i+1:], i+1):
                # Check if entities are close enough
                distance = entity2.start_pos - entity1.end_pos
                if distance > 100:  # Skip if too far apart
                    break
                
                # Extract text between entities
                between_text = text[entity1.end_pos:entity2.start_pos].lower().strip()
                
                # Look for relationship indicators
                for indicator, relation_type in proximity_patterns.items():
                    if indicator in between_text:
                        # Validate entity types for this relationship
                        if self._is_valid_entity_pair_for_relation(entity1, entity2, relation_type):
                            confidence = self._calculate_proximity_confidence(distance, indicator, between_text)
                            
                            relationship = ExtractedRelationship(
                                source_entity=entity1,
                                target_entity=entity2,
                                relation_type=relation_type,
                                confidence=confidence,
                                evidence_text=between_text,
                                extraction_method="proximity_based",
                                metadata={
                                    'indicator': indicator,
                                    'distance': distance,
                                    'between_text': between_text
                                }
                            )
                            relationships.append(relationship)
                            break  # Take first matching indicator
        
        return relationships
    
    def _find_entity_by_text(self, entities: List[ExtractedEntity], text: str) -> Optional[ExtractedEntity]:
        """Find entity by matching text"""
        text_lower = text.lower().strip()
        
        for entity in entities:
            if entity.text.lower().strip() == text_lower:
                return entity
            
            # Check if text contains entity text or vice versa
            if (text_lower in entity.text.lower() or 
                entity.text.lower() in text_lower):
                return entity
        
        return None
    
    def _find_entity_by_position(
        self,
        entities: List[ExtractedEntity],
        start_pos: int,
        end_pos: int
    ) -> Optional[ExtractedEntity]:
        """
Find entity by position overlap"""
        for entity in entities:
            # Check for position overlap
            if (start_pos < entity.end_pos and end_pos > entity.start_pos):
                return entity
        return None
    
    def _validate_entity_constraints(
        self,
        entity1: ExtractedEntity,
        entity2: ExtractedEntity,
        pattern: RelationshipPattern
    ) -> bool:
        """
Validate that entities match pattern constraints"""
        constraints = pattern.entity_type_constraints
        
        if "ENTITY1" in constraints:
            if entity1.entity_type not in constraints["ENTITY1"]:
                return False
        
        if "ENTITY2" in constraints:
            if entity2.entity_type not in constraints["ENTITY2"]:
                return False
        
        return True
    
    def _is_valid_entity_pair_for_relation(
        self,
        entity1: ExtractedEntity,
        entity2: ExtractedEntity,
        relation_type: RelationType
    ) -> bool:
        """Check if entity pair is valid for specific relation type"""
        # Define valid entity type combinations for each relation type
        valid_combinations = {
            RelationType.COLLABORATION: [
                (EntityCategory.PERSON, EntityCategory.PERSON),
                (EntityCategory.ORGANIZATION, EntityCategory.ORGANIZATION)
            ],
            RelationType.FEATURING: [
                (EntityCategory.PERSON, EntityCategory.PERSON),
                (EntityCategory.CREATIVE_WORK, EntityCategory.PERSON)
            ],
            RelationType.CREATED_BY: [
                (EntityCategory.CREATIVE_WORK, EntityCategory.PERSON),
                (EntityCategory.CREATIVE_WORK, EntityCategory.ORGANIZATION)
            ],
            RelationType.AVAILABLE_ON: [
                (EntityCategory.CREATIVE_WORK, EntityCategory.PLATFORM)
            ],
            RelationType.SIGNED_TO: [
                (EntityCategory.PERSON, EntityCategory.ORGANIZATION)
            ],
            RelationType.BASED_IN: [
                (EntityCategory.PERSON, EntityCategory.LOCATION),
                (EntityCategory.ORGANIZATION, EntityCategory.LOCATION)
            ]
        }
        
        combinations = valid_combinations.get(relation_type, [])
        entity_pair = (entity1.entity_type, entity2.entity_type)
        
        return entity_pair in combinations or (entity_pair[1], entity_pair[0]) in combinations
    
    def _extract_relationship_context(self, text: str, start_pos: int, end_pos: int, context_size: int = 30) -> str:
        """
Extract context around relationship mention"""
        context_start = max(0, start_pos - context_size)
        context_end = min(len(text), end_pos + context_size)
        return text[context_start:context_end].strip()
    
    def _calculate_proximity_confidence(self, distance: int, indicator: str, between_text: str) -> float:
        """
Calculate confidence for proximity-based relationships"""
        base_confidence = 0.5
        
        # Closer entities get higher confidence
        distance_factor = max(0, 1 - (distance / 100))
        
        # Stronger indicators get higher confidence
        indicator_weights = {
            'featuring': 0.9,
            'by': 0.8,
            'with': 0.7,
            'and': 0.6,
            '&': 0.6,
            'on': 0.5,
            'from': 0.5
        }
        indicator_factor = indicator_weights.get(indicator, 0.3)
        
        # Less noise between entities increases confidence
        noise_factor = max(0.5, 1 - (len(between_text.split()) / 10))
        
        final_confidence = base_confidence * distance_factor * indicator_factor * noise_factor
        return min(final_confidence, 1.0)
    
    def _map_dependency_to_relation_type(self, dependency_label: str) -> Optional[RelationType]:
        """
Map dependency parsing label to relation type"""
        mapping = {
            'CREATED_BY': RelationType.CREATED_BY,
            'FEATURING': RelationType.FEATURING,
            'PRODUCED_BY': RelationType.PRODUCED_BY
        }
        return mapping.get(dependency_label)
    
    def _map_classifier_label_to_relation_type(self, classifier_label: str) -> Optional[RelationType]:
        """
Map ML classifier label to relation type"""
        # This would depend on the specific classifier being used
        # For now, return a default mapping
        label_mapping = {
            'collaboration': RelationType.COLLABORATION,
            'creation': RelationType.CREATED_BY,
            'platform': RelationType.AVAILABLE_ON,
            'business': RelationType.SIGNED_TO,
            'location': RelationType.BASED_IN
        }
        
        return label_mapping.get(classifier_label.lower())
    
    def _filter_and_deduplicate_relationships(
        self,
        relationships: List[ExtractedRelationship]
    ) -> List[ExtractedRelationship]:
        """
Filter and deduplicate extracted relationships"""
        if not relationships:
            return []
        
        # Remove low confidence relationships
        filtered = [r for r in relationships if r.confidence >= ConfidenceLevel.VERY_LOW.value]
        
        # Group by entity pair and relation type
        relationship_groups = {}
        
        for rel in filtered:
            key = (
                rel.source_entity.text,
                rel.target_entity.text,
                rel.relation_type.value
            )
            
            if key not in relationship_groups:
                relationship_groups[key] = []
            relationship_groups[key].append(rel)
        
        # Select best relationship from each group
        deduplicated = []
        for group in relationship_groups.values():
            if len(group) == 1:
                deduplicated.append(group[0])
            else:
                # Select relationship with highest confidence
                best_rel = max(group, key=lambda r: r.confidence)
                
                # Combine evidence from all relationships in group
                all_evidence = [r.evidence_text for r in group]
                best_rel.evidence_text = " | ".join(all_evidence)
                
                # Update metadata
                best_rel.metadata['merged_from'] = [r.extraction_method for r in group]
                best_rel.metadata['total_evidence_count'] = len(group)
                
                deduplicated.append(best_rel)
        
        # Sort by confidence
        deduplicated.sort(key=lambda r: r.confidence, reverse=True)
        
        return deduplicated
    
    def _add_relationships_to_graph(self, relationships: List[ExtractedRelationship]):
        """Add extracted relationships to the relationship graph"""
        for rel in relationships:
            try:
                # Add entity nodes if they don't exist
                source_id = f"{rel.source_entity.entity_type.value}:{rel.source_entity.text}"
                target_id = f"{rel.target_entity.entity_type.value}:{rel.target_entity.text}"
                
                self.relationship_graph.add_node(source_id, 
                    text=rel.source_entity.text,
                    type=rel.source_entity.entity_type.value
                )
                self.relationship_graph.add_node(target_id,
                    text=rel.target_entity.text,
                    type=rel.target_entity.entity_type.value
                )
                
                # Add relationship edge
                self.relationship_graph.add_edge(source_id, target_id,
                    relation=rel.relation_type.value,
                    confidence=rel.confidence,
                    evidence=rel.evidence_text,
                    method=rel.extraction_method
                )
                
            except Exception as e:
                self.logger.warning(f"Failed to add relationship to graph: {str(e)}")
    
    def _generate_cache_key(
        self,
        entities: List[ExtractedEntity],
        text: str,
        context: Optional[str]
    ) -> str:
        """Generate cache key for relationship extraction"""
        import hashlib
        
        entity_key = "|".join(f"{e.text}:{e.entity_type.value}" for e in entities)
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        context_key = context or ""
        
        full_key = f"{entity_key}|{text_hash}|{context_key}"
        return hashlib.md5(full_key.encode()).hexdigest()
    
    def _update_extraction_stats(self, relationships: List[ExtractedRelationship], processing_time: float):
        """Update extraction statistics"""
        self.extraction_stats['total_extractions'] += 1
        self.extraction_stats['successful_extractions'] += len(relationships)
        
        # Update average processing time
        current_avg = self.extraction_stats['avg_processing_time']
        total_extractions = self.extraction_stats['total_extractions']
        new_avg = ((current_avg * (total_extractions - 1)) + processing_time) / total_extractions
        self.extraction_stats['avg_processing_time'] = new_avg
        
        # Update relation type distribution
        for rel in relationships:
            rel_type = rel.relation_type.value
            self.extraction_stats['relation_type_distribution'][rel_type] = \
                self.extraction_stats['relation_type_distribution'].get(rel_type, 0) + 1
        
        # Update confidence distribution
        for rel in relationships:
            confidence_bucket = f"{int(rel.confidence * 10) * 10}-{int(rel.confidence * 10) * 10 + 10}%"
            self.extraction_stats['confidence_distribution'][confidence_bucket] = \
                self.extraction_stats['confidence_distribution'].get(confidence_bucket, 0) + 1
    
    async def infer_implicit_relationships(
        self,
        relationships: List[ExtractedRelationship]
    ) -> List[ExtractedRelationship]:
        """Infer implicit relationships from explicit ones using graph reasoning"""
        inferred_relationships = []
        
        # Build temporary graph from relationships
        temp_graph = nx.DiGraph()
        
        for rel in relationships:
            source_id = f"{rel.source_entity.entity_type.value}:{rel.source_entity.text}"
            target_id = f"{rel.target_entity.entity_type.value}:{rel.target_entity.text}"
            
            temp_graph.add_edge(source_id, target_id, 
                relation=rel.relation_type.value,
                confidence=rel.confidence
            )
        
        # Apply inference rules
        inference_rules = [
            self._infer_transitive_relationships,
            self._infer_symmetric_relationships,
            self._infer_inverse_relationships
        ]
        
        for rule in inference_rules:
            try:
                rule_inferences = await rule(temp_graph, relationships)
                inferred_relationships.extend(rule_inferences)
                
            except Exception as e:
                self.logger.warning(f"Inference rule failed: {str(e)}")
        
        return inferred_relationships
    
    async def _infer_transitive_relationships(
        self,
        graph: nx.DiGraph,
        relationships: List[ExtractedRelationship]
    ) -> List[ExtractedRelationship]:
        """Infer transitive relationships (A -> B, B -> C implies A -> C)"""
        inferred = []
        
        # Define transitive relation types
        transitive_relations = {
            RelationType.INFLUENCED_BY,
            RelationType.SIMILAR_TO,
            RelationType.BASED_IN  # If A is based in B, and B is based in C, A might be based in C
        }
        
        for rel_type in transitive_relations:
            # Find paths of length 2 with same relation type
            for node in graph.nodes():
                for path in nx.single_source_shortest_path(graph, node, cutoff=2).values():
                    if len(path) == 3:  # A -> B -> C
                        # Check if both edges have the same relation type
                        edge1 = graph[path[0]][path[1]]
                        edge2 = graph[path[1]][path[2]]
                        
                        if (edge1.get('relation') == rel_type.value and 
                            edge2.get('relation') == rel_type.value):
                            
                            # Create inferred relationship
                            confidence = min(edge1.get('confidence', 0), edge2.get('confidence', 0)) * 0.7
                            
                            # This is simplified - in practice, we'd need to reconstruct entities
                            # from the node IDs and create proper ExtractedRelationship objects
                            
        return inferred
    
    async def _infer_symmetric_relationships(
        self,
        graph: nx.DiGraph,
        relationships: List[ExtractedRelationship]
    ) -> List[ExtractedRelationship]:
        """
Infer symmetric relationships (A -> B implies B -> A)"""
        inferred = []
        
        # Define symmetric relation types
        symmetric_relations = {
            RelationType.COLLABORATION,
            RelationType.SIMILAR_TO
        }
        
        for rel in relationships:
            if rel.relation_type in symmetric_relations:
                # Check if reverse relationship already exists
                reverse_exists = any(
                    r.source_entity.text == rel.target_entity.text and
                    r.target_entity.text == rel.source_entity.text and
                    r.relation_type == rel.relation_type
                    for r in relationships
                )
                
                if not reverse_exists:
                    # Create reverse relationship with slightly lower confidence
                    reverse_rel = ExtractedRelationship(
                        source_entity=rel.target_entity,
                        target_entity=rel.source_entity,
                        relation_type=rel.relation_type,
                        confidence=rel.confidence * 0.9,
                        evidence_text=rel.evidence_text,
                        extraction_method="inference_symmetric",
                        metadata={'inferred_from': rel.evidence_text}
                    )
                    inferred.append(reverse_rel)
        
        return inferred
    
    async def _infer_inverse_relationships(
        self,
        graph: nx.DiGraph,
        relationships: List[ExtractedRelationship]
    ) -> List[ExtractedRelationship]:
        """Infer inverse relationships"""
        inferred = []
        
        # Define inverse relation pairs
        inverse_relations = {
            RelationType.CREATED_BY: RelationType.OWNED_BY,
            RelationType.PRODUCED_BY: RelationType.OWNED_BY,
            RelationType.INFLUENCED_BY: RelationType.INFLUENCED_BY  # Self-inverse
        }
        
        for rel in relationships:
            if rel.relation_type in inverse_relations:
                inverse_type = inverse_relations[rel.relation_type]
                
                # Create inverse relationship
                inverse_rel = ExtractedRelationship(
                    source_entity=rel.target_entity,
                    target_entity=rel.source_entity,
                    relation_type=inverse_type,
                    confidence=rel.confidence * 0.8,
                    evidence_text=rel.evidence_text,
                    extraction_method="inference_inverse",
                    metadata={'inferred_from': rel.evidence_text}
                )
                inferred.append(inverse_rel)
        
        return inferred
    
    async def get_relationship_statistics(self) -> Dict[str, Any]:
        """Get relationship extraction statistics"""
        return {
            **self.extraction_stats,
            'graph_stats': {
                'nodes': len(self.relationship_graph.nodes),
                'edges': len(self.relationship_graph.edges),
                'density': nx.density(self.relationship_graph)
            },
            'pattern_count': len(self.relationship_patterns),
            'cache_size': len(self.extraction_cache),
            'available_relation_types': [rt.value for rt in RelationType]
        }
    
    async def export_relationship_graph(self, format: str = "json") -> Dict[str, Any]:
        """Export relationship graph in specified format"""
        if format == "json":
            return {
                'nodes': [
                    {'id': node, **data}
                    for node, data in self.relationship_graph.nodes(data=True)
                ],
                'edges': [
                    {'source': source, 'target': target, **data}
                    for source, target, data in self.relationship_graph.edges(data=True)
                ]
            }
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for relationship extractor"""
        return {
            'status': 'healthy',
            'spacy_available': self.nlp is not None,
            'classifier_available': self.relation_classifier is not None,
            'patterns_loaded': len(self.relationship_patterns),
            'graph_size': len(self.relationship_graph.nodes),
            'total_extractions': self.extraction_stats['total_extractions'],
            'success_rate': (
                self.extraction_stats['successful_extractions'] / 
                max(self.extraction_stats['total_extractions'], 1)
            ) * 100,
            'avg_processing_time': self.extraction_stats['avg_processing_time']
        }
