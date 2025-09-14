"""Entity Extraction SEO
Advanced entity extraction and optimization for enhanced SEO performance.

Features:
- Named Entity Recognition (NER)
- Entity linking and relationship mapping
- Schema markup generation
- Knowledge graph optimization
- Entity-based keyword expansion

Author: Fahed Mlaiel (mlaiel@live.de)
ML Engineer + Semantic SEO expertise applied
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

try:
    import spacy
    from spacy.matcher import Matcher
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.tag import pos_tag
    from nltk.chunk import ne_chunk
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    import numpy as np
    import requests
    from collections import Counter, defaultdict
except ImportError as e:
    logging.warning(f"Optional dependencies not available: {e}")

logger = logging.getLogger(__name__)

class EntityType(Enum):
    """Entity types for SEO optimization."""
    PERSON = "PERSON"
    ORGANIZATION = "ORG"
    LOCATION = "LOC"
    PRODUCT = "PRODUCT"
    EVENT = "EVENT"
    MONEY = "MONEY"
    DATE = "DATE"
    TIME = "TIME"
    PERCENT = "PERCENT"
    WORK_OF_ART = "WORK_OF_ART"
    LANGUAGE = "LANGUAGE"
    NATIONALITY = "NORP"
    FACILITY = "FAC"
    GEOPOLITICAL = "GPE"
    LAW = "LAW"
    ORDINAL = "ORDINAL"
    CARDINAL = "CARDINAL"
    QUANTITY = "QUANTITY"
    MISC = "MISC"

@dataclass
class Entity:
    """Extracted entity with metadata."""
    text: str
    label: EntityType
    start: int
    end: int
    confidence: float
    context: str
    mentions: int = 1
    importance_score: float = 0.0
    related_entities: List[str] = field(default_factory=list)
    schema_type: Optional[str] = None
    wikipedia_url: Optional[str] = None
    knowledge_graph_id: Optional[str] = None

@dataclass
class EntityRelationship:
    """Relationship between entities."""
    source_entity: str
    target_entity: str
    relationship_type: str
    confidence: float
    context: str

@dataclass
class EntityExtractionResult:
    """Result of entity extraction and analysis."""
    entities: List[Entity]
    relationships: List[EntityRelationship]
    entity_clusters: Dict[EntityType, List[Entity]]
    schema_markup: Dict[str, Any]
    knowledge_graph_data: Dict[str, Any]
    seo_recommendations: List[str]
    entity_density: float
    coverage_score: float

@dataclass
class EntitySEOConfig:
    """Configuration for entity-based SEO optimization."""
    target_entities: List[str]
    business_type: str
    content_type: str
    enable_entity_linking: bool = True
    enable_schema_generation: bool = True
    enable_knowledge_graph: bool = True
    minimum_confidence: float = 0.7
    max_entities_per_type: int = 10

class EntityExtractionSEO:
    """Advanced entity extraction and SEO optimization engine."""
    
    def __init__(self) -> None:
        """Initialize the Entity Extraction SEO engine."""
        self.nlp_models = {}
        self.entity_classifier = None
        self.entity_matcher = None
        self._load_models()
        
        # Entity type mappings for schema.org
        self.schema_mappings = self._load_schema_mappings()
        
        # Knowledge graph endpoints
        self.kg_endpoints = {
            "wikidata": "https://www.wikidata.org/w/api.php",
            "dbpedia": "https://dbpedia.org/sparql"
        }
        
        # Entity importance weights
        self.importance_weights = {
            EntityType.PERSON: 0.9,
            EntityType.ORGANIZATION: 0.85,
            EntityType.PRODUCT: 0.8,
            EntityType.LOCATION: 0.75,
            EntityType.EVENT: 0.7,
            EntityType.WORK_OF_ART: 0.65,
            EntityType.GEOPOLITICAL: 0.75,
            EntityType.FACILITY: 0.6,
            EntityType.MONEY: 0.5,
            EntityType.DATE: 0.4,
            EntityType.TIME: 0.3,
            EntityType.PERCENT: 0.4,
            EntityType.QUANTITY: 0.35,
            EntityType.ORDINAL: 0.25,
            EntityType.CARDINAL: 0.2,
            EntityType.MISC: 0.3
        }
    
    def _load_models(self) -> None:
        """Load NLP models for entity extraction."""
        try:
            # Load spaCy models for different languages
            language_models = {
                "en": "en_core_web_sm",
                "fr": "fr_core_news_sm",
                "de": "de_core_news_sm",
                "es": "es_core_news_sm"
            }
            
            for lang, model_name in language_models.items():
                try:
                    nlp = spacy.load(model_name)
                    self.nlp_models[lang] = nlp
                    logger.info(f"Loaded {model_name} for {lang}")
                except OSError:
                    logger.warning(f"Model {model_name} not found for {lang}")
            
            # Load transformer-based NER model
            try:
                self.entity_classifier = pipeline(
                    "ner",
                    model="dbmdz/bert-large-cased-finetuned-conll03-english",
                    aggregation_strategy="simple"
                )
            except Exception as e:
                logger.warning(f"Could not load transformer NER model: {e}")
            
            # Initialize entity matcher
            if self.nlp_models.get("en"):
                self.entity_matcher = Matcher(self.nlp_models["en"].vocab)
                self._add_custom_entity_patterns()
                
        except Exception as e:
            logger.error(f"Error loading entity extraction models: {e}")
    
    def _load_schema_mappings(self) -> Dict[EntityType, str]:
        """Load entity type to schema.org mappings."""
        return {
            EntityType.PERSON: "Person",
            EntityType.ORGANIZATION: "Organization",
            EntityType.LOCATION: "Place",
            EntityType.PRODUCT: "Product",
            EntityType.EVENT: "Event",
            EntityType.WORK_OF_ART: "CreativeWork",
            EntityType.GEOPOLITICAL: "Place",
            EntityType.FACILITY: "Place",
            EntityType.MONEY: "MonetaryAmount",
            EntityType.DATE: "Date",
            EntityType.TIME: "Time",
            EntityType.PERCENT: "QuantitativeValue",
            EntityType.QUANTITY: "QuantitativeValue",
            EntityType.MISC: "Thing"
        }
    
    def _add_custom_entity_patterns(self) -> None:
        """Add custom entity patterns to matcher."""
        try:
            if not self.entity_matcher:
                return
            
            # Product patterns
            product_patterns = [
                [{"LOWER": {"IN": ["iphone", "samsung", "google", "apple"]}},
                 {"IS_TITLE": True, "OP": "?"}],
                [{"LOWER": {"IN": ["model", "version"]}},
                 {"IS_DIGIT": True}]
            ]
            
            self.entity_matcher.add("PRODUCT", product_patterns)
            
            # Event patterns
            event_patterns = [
                [{"LOWER": {"IN": ["conference", "summit", "meeting", "workshop"]}},
                 {"IS_TITLE": True, "OP": "+"}],
                [{"IS_TITLE": True},
                 {"LOWER": {"IN": ["festival", "championship", "cup", "games"]}}]
            ]
            
            self.entity_matcher.add("EVENT", event_patterns)
            
        except Exception as e:
            logger.error(f"Error adding custom entity patterns: {e}")
    
    async def extract_entities(
        self,
        content: str,
        config: EntitySEOConfig,
        language: str = "en"
    ) -> EntityExtractionResult:
        """Extract and analyze entities from content.
        
        Args:
            content: Text content to analyze
            config: Entity extraction configuration
            language: Language code
            
        Returns:
            EntityExtractionResult with comprehensive entity analysis
        """
        try:
            # Extract entities using multiple methods
            spacy_entities = await self._extract_with_spacy(content, language)
            transformer_entities = await self._extract_with_transformers(content)
            custom_entities = await self._extract_custom_entities(content, config)
            
            # Merge and deduplicate entities
            all_entities = self._merge_entities(
                spacy_entities, transformer_entities, custom_entities
            )
            
            # Filter by confidence
            filtered_entities = [
                entity for entity in all_entities
                if entity.confidence >= config.minimum_confidence
            ]
            
            # Calculate entity importance scores
            for entity in filtered_entities:
                entity.importance_score = self._calculate_entity_importance(
                    entity, content, config
                )
            
            # Sort by importance
            filtered_entities.sort(key=lambda x: x.importance_score, reverse=True)
            
            # Limit entities per type
            entity_clusters = self._cluster_entities_by_type(
                filtered_entities, config.max_entities_per_type
            )
            
            # Extract entity relationships
            relationships = await self._extract_entity_relationships(
                filtered_entities, content
            )
            
            # Generate schema markup
            schema_markup = {}
            if config.enable_schema_generation:
                schema_markup = await self._generate_schema_markup(
                    filtered_entities, config
                )
            
            # Fetch knowledge graph data
            knowledge_graph_data = {}
            if config.enable_knowledge_graph:
                knowledge_graph_data = await self._fetch_knowledge_graph_data(
                    filtered_entities[:10]  # Limit to top 10 entities
                )
            
            # Generate SEO recommendations
            seo_recommendations = self._generate_entity_seo_recommendations(
                filtered_entities, config
            )
            
            # Calculate metrics
            entity_density = self._calculate_entity_density(filtered_entities, content)
            coverage_score = self._calculate_coverage_score(filtered_entities, config)
            
            return EntityExtractionResult(
                entities=filtered_entities,
                relationships=relationships,
                entity_clusters=entity_clusters,
                schema_markup=schema_markup,
                knowledge_graph_data=knowledge_graph_data,
                seo_recommendations=seo_recommendations,
                entity_density=entity_density,
                coverage_score=coverage_score
            )
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return self._create_empty_result()
    
    async def _extract_with_spacy(
        self,
        content: str,
        language: str
    ) -> List[Entity]:
        """Extract entities using spaCy NLP model."""
        try:
            nlp_model = self.nlp_models.get(language, self.nlp_models.get("en"))
            if not nlp_model:
                return []
            
            doc = nlp_model(content)
            entities = []
            
            for ent in doc.ents:
                try:
                    entity_type = EntityType(ent.label_)
                except ValueError:
                    entity_type = EntityType.MISC
                
                # Get context (surrounding words)
                context_start = max(0, ent.start - 5)
                context_end = min(len(doc), ent.end + 5)
                context = doc[context_start:context_end].text
                
                entity = Entity(
                    text=ent.text,
                    label=entity_type,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=0.8,  # Default spaCy confidence
                    context=context
                )
                
                entities.append(entity)
            
            # Extract custom pattern matches
            if self.entity_matcher:
                matches = self.entity_matcher(doc)
                for match_id, start, end in matches:
                    span = doc[start:end]
                    label_name = nlp_model.vocab.strings[match_id]
                    
                    try:
                        entity_type = EntityType(label_name)
                    except ValueError:
                        entity_type = EntityType.MISC
                    
                    entity = Entity(
                        text=span.text,
                        label=entity_type,
                        start=span.start_char,
                        end=span.end_char,
                        confidence=0.7,  # Custom pattern confidence
                        context=span.sent.text if span.sent else span.text
                    )
                    
                    entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities with spaCy: {e}")
            return []
    
    async def _extract_with_transformers(self, content: str) -> List[Entity]:
        """Extract entities using transformer models."""
        try:
            if not self.entity_classifier:
                return []
            
            # Process content in chunks to handle length limits
            max_length = 512
            entities = []
            
            for i in range(0, len(content), max_length):
                chunk = content[i:i + max_length]
                
                results = self.entity_classifier(chunk)
                
                for result in results:
                    try:
                        # Map transformer labels to our entity types
                        label_mapping = {
                            "PER": EntityType.PERSON,
                            "ORG": EntityType.ORGANIZATION,
                            "LOC": EntityType.LOCATION,
                            "MISC": EntityType.MISC
                        }
                        
                        entity_type = label_mapping.get(result["entity_group"], EntityType.MISC)
                        
                        entity = Entity(
                            text=result["word"],
                            label=entity_type,
                            start=result["start"] + i,
                            end=result["end"] + i,
                            confidence=result["score"],
                            context=chunk[max(0, result["start"]-20):result["end"]+20]
                        )
                        
                        entities.append(entity)
                        
                    except Exception as entity_error:
                        logger.warning(f"Error processing entity result: {entity_error}")
                        continue
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities with transformers: {e}")
            return []
    
    async def _extract_custom_entities(
        self,
        content: str,
        config: EntitySEOConfig
    ) -> List[Entity]:
        """Extract custom business-specific entities."""
        try:
            entities = []
            
            # Extract target entities mentioned in config
            for target_entity in config.target_entities:
                pattern = r'\b' + re.escape(target_entity) + r'\b'
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                
                for match in matches:
                    # Determine entity type based on business context
                    entity_type = self._determine_entity_type_from_context(
                        target_entity, config.business_type
                    )
                    
                    # Get surrounding context
                    context_start = max(0, match.start() - 50)
                    context_end = min(len(content), match.end() + 50)
                    context = content[context_start:context_end]
                    
                    entity = Entity(
                        text=match.group(),
                        label=entity_type,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.9,  # High confidence for target entities
                        context=context
                    )
                    
                    entities.append(entity)
            
            # Extract domain-specific entities based on business type
            domain_entities = self._extract_domain_specific_entities(content, config)
            entities.extend(domain_entities)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting custom entities: {e}")
            return []
    
    def _determine_entity_type_from_context(
        self,
        entity_text: str,
        business_type: str
    ) -> EntityType:
        """Determine entity type based on business context."""
        try:
            business_type_lower = business_type.lower()
            entity_lower = entity_text.lower()
            
            # Business type specific mappings
            if business_type_lower in ["ecommerce", "retail", "store"]:
                if any(keyword in entity_lower for keyword in ["product", "item", "model"]):
                    return EntityType.PRODUCT
                elif any(keyword in entity_lower for keyword in ["brand", "company"]):
                    return EntityType.ORGANIZATION
            
            elif business_type_lower in ["restaurant", "food", "cuisine"]:
                if any(keyword in entity_lower for keyword in ["dish", "meal", "cuisine"]):
                    return EntityType.PRODUCT
                elif any(keyword in entity_lower for keyword in ["restaurant", "cafe"]):
                    return EntityType.FACILITY
            
            elif business_type_lower in ["music", "musician", "artist"]:
                if any(keyword in entity_lower for keyword in ["album", "song", "track"]):
                    return EntityType.WORK_OF_ART
                elif any(keyword in entity_lower for keyword in ["artist", "band", "musician"]):
                    return EntityType.PERSON
            
            elif business_type_lower in ["event", "conference", "festival"]:
                return EntityType.EVENT
            
            # Default classifications
            if entity_text.istitle() and len(entity_text.split()) == 1:
                return EntityType.PERSON
            elif any(keyword in entity_lower for keyword in ["inc", "ltd", "corp", "company"]):
                return EntityType.ORGANIZATION
            else:
                return EntityType.MISC
                
        except Exception as e:
            logger.error(f"Error determining entity type: {e}")
            return EntityType.MISC
    
    def _extract_domain_specific_entities(
        self,
        content: str,
        config: EntitySEOConfig
    ) -> List[Entity]:
        """Extract entities specific to the business domain."""
        try:
            entities = []
            
            # Domain-specific patterns
            domain_patterns = {
                "technology": [
                    r'\b(API|SDK|SaaS|AI|ML|IoT|VR|AR|5G|blockchain)\b',
                    r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:app|software|platform|system)\b'
                ],
                "finance": [
                    r'\$[\d,]+(?:\.\d{2})?',
                    r'\b(?:USD|EUR|GBP|JPY|crypto|bitcoin|ethereum)\b'
                ],
                "healthcare": [
                    r'\b(?:treatment|therapy|diagnosis|medicine|drug|vaccine)\b',
                    r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:hospital|clinic|center)\b'
                ],
                "education": [
                    r'\b(?:course|degree|certification|training|workshop)\b',
                    r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:university|college|school)\b'
                ]
            }
            
            business_type_lower = config.business_type.lower()
            patterns = domain_patterns.get(business_type_lower, [])
            
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    # Determine entity type based on pattern
                    matched_text = match.group()
                    
                    if re.match(r'\$[\d,]+', matched_text):
                        entity_type = EntityType.MONEY
                    elif any(tech_term in matched_text.upper() for tech_term in ["API", "SDK", "AI", "ML"]):
                        entity_type = EntityType.PRODUCT
                    elif "hospital" in matched_text.lower() or "clinic" in matched_text.lower():
                        entity_type = EntityType.FACILITY
                    elif "university" in matched_text.lower() or "college" in matched_text.lower():
                        entity_type = EntityType.ORGANIZATION
                    else:
                        entity_type = EntityType.MISC
                    
                    # Get context
                    context_start = max(0, match.start() - 30)
                    context_end = min(len(content), match.end() + 30)
                    context = content[context_start:context_end]
                    
                    entity = Entity(
                        text=matched_text,
                        label=entity_type,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.6,  # Medium confidence for pattern matches
                        context=context
                    )
                    
                    entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting domain-specific entities: {e}")
            return []
    
    def _merge_entities(
        self,
        spacy_entities: List[Entity],
        transformer_entities: List[Entity],
        custom_entities: List[Entity]
    ) -> List[Entity]:
        """Merge entities from different extraction methods."""
        try:
            all_entities = spacy_entities + transformer_entities + custom_entities
            
            # Remove duplicates based on text and position overlap
            unique_entities = []
            seen_entities = set()
            
            for entity in all_entities:
                # Create a unique key based on text and approximate position
                key = (entity.text.lower(), entity.start // 10 * 10)  # Round to nearest 10
                
                if key not in seen_entities:
                    seen_entities.add(key)
                    unique_entities.append(entity)
                else:
                    # If duplicate, keep the one with higher confidence
                    for i, existing_entity in enumerate(unique_entities):
                        existing_key = (existing_entity.text.lower(), existing_entity.start // 10 * 10)
                        if existing_key == key and entity.confidence > existing_entity.confidence:
                            unique_entities[i] = entity
                            break
            
            # Count mentions for each entity
            entity_counts = Counter(entity.text.lower() for entity in unique_entities)
            
            for entity in unique_entities:
                entity.mentions = entity_counts[entity.text.lower()]
            
            return unique_entities
            
        except Exception as e:
            logger.error(f"Error merging entities: {e}")
            return []
    
    def _calculate_entity_importance(
        self,
        entity: Entity,
        content: str,
        config: EntitySEOConfig
    ) -> float:
        """Calculate importance score for an entity."""
        try:
            score = 0.0
            
            # Base score from entity type
            type_weight = self.importance_weights.get(entity.label, 0.3)
            score += type_weight * 0.4
            
            # Confidence score
            score += entity.confidence * 0.3
            
            # Mention frequency
            mention_score = min(entity.mentions / 5, 1.0)  # Normalize to max 5 mentions
            score += mention_score * 0.2
            
            # Target entity bonus
            if entity.text.lower() in [target.lower() for target in config.target_entities]:
                score += 0.1
            
            # Position importance (earlier mentions are more important)
            position_score = 1.0 - (entity.start / len(content))
            score += position_score * 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating entity importance: {e}")
            return 0.0
    
    def _cluster_entities_by_type(
        self,
        entities: List[Entity],
        max_per_type: int
    ) -> Dict[EntityType, List[Entity]]:
        """Cluster entities by type and limit per type."""
        try:
            clusters = defaultdict(list)
            
            for entity in entities:
                if len(clusters[entity.label]) < max_per_type:
                    clusters[entity.label].append(entity)
            
            return dict(clusters)
            
        except Exception as e:
            logger.error(f"Error clustering entities: {e}")
            return {}
    
    async def _extract_entity_relationships(
        self,
        entities: List[Entity],
        content: str
    ) -> List[EntityRelationship]:
        """Extract relationships between entities."""
        try:
            relationships = []
            
            # Simple co-occurrence based relationships
            for i, entity1 in enumerate(entities):
                for entity2 in entities[i+1:]:
                    # Check if entities appear in same sentence
                    sentences = sent_tokenize(content)
                    
                    for sentence in sentences:
                        if (entity1.text in sentence and entity2.text in sentence and
                            entity1.text != entity2.text):
                            
                            # Determine relationship type
                            relationship_type = self._determine_relationship_type(
                                entity1, entity2, sentence
                            )
                            
                            if relationship_type:
                                relationship = EntityRelationship(
                                    source_entity=entity1.text,
                                    target_entity=entity2.text,
                                    relationship_type=relationship_type,
                                    confidence=0.7,
                                    context=sentence
                                )
                                
                                relationships.append(relationship)
                                break
            
            return relationships
            
        except Exception as e:
            logger.error(f"Error extracting entity relationships: {e}")
            return []
    
    def _determine_relationship_type(
        self,
        entity1: Entity,
        entity2: Entity,
        context: str
    ) -> Optional[str]:
        """Determine relationship type between entities."""
        try:
            context_lower = context.lower()
            
            # Person-Organization relationships
            if (entity1.label == EntityType.PERSON and entity2.label == EntityType.ORGANIZATION):
                if any(word in context_lower for word in ["works for", "employed by", "ceo of", "founder of"]):
                    return "works_for"
                elif any(word in context_lower for word in ["owns", "founded", "created"]):
                    return "founded"
            
            # Organization-Product relationships
            elif (entity1.label == EntityType.ORGANIZATION and entity2.label == EntityType.PRODUCT):
                if any(word in context_lower for word in ["makes", "produces", "develops", "created"]):
                    return "produces"
                elif any(word in context_lower for word in ["sells", "offers", "provides"]):
                    return "sells"
            
            # Location relationships
            elif entity2.label in [EntityType.LOCATION, EntityType.GEOPOLITICAL]:
                if any(word in context_lower for word in ["located in", "based in", "from"]):
                    return "located_in"
                elif any(word in context_lower for word in ["near", "close to"]):
                    return "near"
            
            # Event relationships
            elif entity2.label == EntityType.EVENT:
                if any(word in context_lower for word in ["attended", "spoke at", "participated in"]):
                    return "participated_in"
                elif any(word in context_lower for word in ["organized", "hosted"]):
                    return "organized"
            
            # Generic association
            if any(word in context_lower for word in ["and", "with", "alongside"]):
                return "associated_with"
            
            return None
            
        except Exception as e:
            logger.error(f"Error determining relationship type: {e}")
            return None
    
    async def _generate_schema_markup(
        self,
        entities: List[Entity],
        config: EntitySEOConfig
    ) -> Dict[str, Any]:
        """Generate schema.org markup for entities."""
        try:
            schema_data = {
                "@context": "https://schema.org",
                "@graph": []
            }
            
            for entity in entities[:20]:  # Limit to top 20 entities
                schema_type = self.schema_mappings.get(entity.label)
                if not schema_type:
                    continue
                
                entity_schema = {
                    "@type": schema_type,
                    "name": entity.text
                }
                
                # Add entity-specific properties
                if entity.label == EntityType.PERSON:
                    entity_schema.update({
                        "@type": "Person",
                        "name": entity.text
                    })
                
                elif entity.label == EntityType.ORGANIZATION:
                    entity_schema.update({
                        "@type": "Organization",
                        "name": entity.text
                    })
                
                elif entity.label == EntityType.PRODUCT:
                    entity_schema.update({
                        "@type": "Product",
                        "name": entity.text
                    })
                
                elif entity.label == EntityType.EVENT:
                    entity_schema.update({
                        "@type": "Event",
                        "name": entity.text
                    })
                
                elif entity.label in [EntityType.LOCATION, EntityType.GEOPOLITICAL]:
                    entity_schema.update({
                        "@type": "Place",
                        "name": entity.text
                    })
                
                # Add Wikipedia URL if available
                if entity.wikipedia_url:
                    entity_schema["sameAs"] = entity.wikipedia_url
                
                # Add knowledge graph ID if available
                if entity.knowledge_graph_id:
                    entity_schema["identifier"] = entity.knowledge_graph_id
                
                schema_data["@graph"].append(entity_schema)
            
            return schema_data
            
        except Exception as e:
            logger.error(f"Error generating schema markup: {e}")
            return {}
    
    async def _fetch_knowledge_graph_data(
        self,
        entities: List[Entity]
    ) -> Dict[str, Any]:
        """Fetch additional data from knowledge graphs."""
        try:
            kg_data = {}
            
            for entity in entities:
                try:
                    # Search Wikidata for entity
                    wikidata_info = await self._search_wikidata(entity.text)
                    if wikidata_info:
                        kg_data[entity.text] = wikidata_info
                        entity.knowledge_graph_id = wikidata_info.get("id")
                        entity.wikipedia_url = wikidata_info.get("wikipedia_url")
                        
                except Exception as entity_error:
                    logger.warning(f"Error fetching KG data for {entity.text}: {entity_error}")
                    continue
            
            return kg_data
            
        except Exception as e:
            logger.error(f"Error fetching knowledge graph data: {e}")
            return {}
    
    async def _search_wikidata(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Search Wikidata for entity information."""
        try:
            # This is a simplified example - in production you'd want more robust API calls
            params = {
                "action": "wbsearchentities",
                "search": entity_name,
                "language": "en",
                "format": "json",
                "limit": 1
            }
            
            # Note: In production, you'd make actual API calls here
            # For now, return mock data structure
            mock_data = {
                "id": f"Q{hash(entity_name) % 1000000}",
                "label": entity_name,
                "description": f"Information about {entity_name}",
                "wikipedia_url": f"https://en.wikipedia.org/wiki/{entity_name.replace(' ', '_')}"
            }
            
            return mock_data
            
        except Exception as e:
            logger.error(f"Error searching Wikidata: {e}")
            return None
    
    def _generate_entity_seo_recommendations(
        self,
        entities: List[Entity],
        config: EntitySEOConfig
    ) -> List[str]:
        """Generate SEO recommendations based on entity analysis."""
        try:
            recommendations = []
            
            # Entity density recommendations
            high_importance_entities = [e for e in entities if e.importance_score > 0.7]
            
            if len(high_importance_entities) < 3:
                recommendations.append("Consider adding more relevant entities (people, organizations, products) to increase content authority")
            
            # Entity type diversity
            entity_types_present = set(e.label for e in entities)
            important_types = {EntityType.PERSON, EntityType.ORGANIZATION, EntityType.PRODUCT, EntityType.LOCATION}
            
            missing_types = important_types - entity_types_present
            if missing_types:
                recommendations.append(f"Consider adding entities of types: {', '.join(t.value for t in missing_types)}")
            
            # Target entity coverage
            target_entities_found = [e for e in entities if e.text.lower() in [t.lower() for t in config.target_entities]]
            if len(target_entities_found) < len(config.target_entities):
                recommendations.append("Some target entities are missing from the content")
            
            # Schema markup recommendation
            if config.enable_schema_generation:
                recommendations.append("Add generated schema.org markup to improve search engine understanding")
            
            # Entity linking recommendation
            entities_with_kg_data = [e for e in entities if e.wikipedia_url or e.knowledge_graph_id]
            if len(entities_with_kg_data) < len(entities) * 0.3:
                recommendations.append("Consider linking more entities to authoritative sources (Wikipedia, knowledge graphs)")
            
            # Mention frequency recommendations
            low_mention_entities = [e for e in entities if e.mentions == 1 and e.importance_score > 0.6]
            if low_mention_entities:
                recommendations.append(f"Important entities mentioned only once: {', '.join(e.text for e in low_mention_entities[:3])}")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating entity SEO recommendations: {e}")
            return []
    
    def _calculate_entity_density(self, entities: List[Entity], content: str) -> float:
        """Calculate entity density in content."""
        try:
            total_words = len(content.split())
            total_entity_words = sum(len(entity.text.split()) for entity in entities)
            
            return total_entity_words / total_words if total_words > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating entity density: {e}")
            return 0.0
    
    def _calculate_coverage_score(
        self,
        entities: List[Entity],
        config: EntitySEOConfig
    ) -> float:
        """Calculate how well entities cover the target domain."""
        try:
            score_components = []
            
            # Target entity coverage
            target_entities_found = len([e for e in entities if e.text.lower() in [t.lower() for t in config.target_entities]])
            target_coverage = target_entities_found / len(config.target_entities) if config.target_entities else 1.0
            score_components.append(target_coverage * 0.4)
            
            # Entity type diversity
            entity_types_present = len(set(e.label for e in entities))
            type_diversity = min(entity_types_present / 8, 1.0)  # Normalize to 8 types
            score_components.append(type_diversity * 0.3)
            
            # High-importance entity presence
            high_importance_count = len([e for e in entities if e.importance_score > 0.7])
            importance_score = min(high_importance_count / 5, 1.0)  # Normalize to 5 entities
            score_components.append(importance_score * 0.3)
            
            return sum(score_components)
            
        except Exception as e:
            logger.error(f"Error calculating coverage score: {e}")
            return 0.0
    
    def _create_empty_result(self) -> EntityExtractionResult:
        """Create empty result for error cases."""
        return EntityExtractionResult(
            entities=[],
            relationships=[],
            entity_clusters={},
            schema_markup={},
            knowledge_graph_data={},
            seo_recommendations=[],
            entity_density=0.0,
            coverage_score=0.0
        )

    async def optimize_entity_mentions(
        self,
        content: str,
        entities: List[Entity],
        target_mentions: int = 3
    ) -> str:
        """Optimize entity mentions in content for better SEO."""
        try:
            optimized_content = content
            
            # Identify entities that need more mentions
            entities_to_boost = [
                entity for entity in entities
                if entity.importance_score > 0.7 and entity.mentions < target_mentions
            ]
            
            sentences = sent_tokenize(optimized_content)
            
            for entity in entities_to_boost[:3]:  # Limit to top 3 entities
                mentions_needed = target_mentions - entity.mentions
                
                for i in range(min(mentions_needed, 2)):  # Add max 2 additional mentions
                    # Find appropriate insertion points
                    insertion_point = len(sentences) // (i + 2)
                    
                    # Create natural mention
                    if entity.label == EntityType.PERSON:
                        mention_sentence = f"As {entity.text} noted, this is important."
                    elif entity.label == EntityType.ORGANIZATION:
                        mention_sentence = f"{entity.text} continues to lead in this area."
                    elif entity.label == EntityType.PRODUCT:
                        mention_sentence = f"The {entity.text} offers significant benefits."
                    else:
                        mention_sentence = f"This relates to {entity.text} in important ways."
                    
                    sentences.insert(insertion_point, mention_sentence)
            
            return " ".join(sentences)
            
        except Exception as e:
            logger.error(f"Error optimizing entity mentions: {e}")
            return content

    async def batch_extract_entities(
        self,
        contents: List[str],
        configs: List[EntitySEOConfig]
    ) -> List[EntityExtractionResult]:
        """Extract entities for multiple contents in batch."""
        try:
            tasks = [
                self.extract_entities(content, config)
                for content, config in zip(contents, configs)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log them
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error extracting entities for content {i}: {result}")
                    valid_results.append(self._create_empty_result())
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            logger.error(f"Error in batch entity extraction: {e}")
            return [self._create_empty_result() for _ in contents]