"""Entity Linker - Advanced Entity Linking and Resolution

Sophisticated entity linking system for creative content with knowledge graph
integration, disambiguation, and canonical entity resolution. Specialized for
musicians, influencers, content creators, and creative industry professionals.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""
import asyncio
import json
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
import hashlib

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import requests
import networkx as nx
from fuzzywuzzy import fuzz, process
import spacy

from ...core.base_service import BaseService
from ...core.cache import cache_manager
from ...core.monitoring import MetricsCollector
from ...models.entities import KnowledgeGraphEntity, EntityLink, LinkingCandidate
from ...utils.text_processors import TextPreprocessor
from ...utils.vector_operations import VectorManager
from .entity_extractor import ExtractedEntity, EntityCategory


class LinkingStrategy(Enum):
    """Entity linking strategies"""    EXACT_MATCH = "exact_match"
    FUZZY_MATCH = "fuzzy_match"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    HYBRID_ENSEMBLE = "hybrid_ensemble"


class ConfidenceLevel(Enum):
    """Confidence levels for entity linking"""    VERY_HIGH = 0.95
    HIGH = 0.85
    MEDIUM = 0.70
    LOW = 0.50
    VERY_LOW = 0.30


@dataclass
class EntityCandidate:
    """Candidate entity for linking"""    entity_id: str
    canonical_name: str
    entity_type: EntityCategory
    confidence_score: float
    source_database: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)
    description: str = ""
    external_ids: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation"""        if self.confidence_score > 1.0:
            self.confidence_score = 1.0
        elif self.confidence_score < 0.0:
            self.confidence_score = 0.0


@dataclass
class LinkingResult:
    """Result of entity linking process"""    original_entity: ExtractedEntity
    linked_entity: Optional[EntityCandidate]
    confidence: float
    linking_strategy: LinkingStrategy
    alternative_candidates: List[EntityCandidate] = field(default_factory=list)
    disambiguation_context: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    
    @property
    def is_linked(self) -> bool:
        """Check if entity was successfully linked"""        return self.linked_entity is not None and self.confidence > ConfidenceLevel.LOW.value


class EntityLinker(BaseService):
    """    Advanced Entity Linking system with creative industry specialization.
    
    Features:
    - Multi-strategy entity linking (exact, fuzzy, semantic, knowledge graph)
    - Creative industry knowledge bases integration
    - Real-time disambiguation with context analysis
    - Vector similarity search with FAISS indexing
    - External API integration (MusicBrainz, Discogs, Spotify, etc.)
    - Dynamic knowledge graph construction
    - Confidence scoring with uncertainty quantification
    - Performance monitoring and optimization
    """    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("entity_linker")
        self.text_processor = TextPreprocessor()
        self.vector_manager = VectorManager()
        
        # Knowledge bases and indexes
        self.knowledge_bases = {}
        self.vector_indexes = {}
        self.entity_embeddings = {}
        
        # External API configurations
        self.api_configs = {}
        self.api_rate_limits = {}
        
        # Caching configurations
        self.linking_cache = {}
        self.candidate_cache = {}
        
        # Sentence transformer for semantic similarity
        self.sentence_transformer = None
        
        # Knowledge graph
        self.knowledge_graph = nx.DiGraph()
        
        # Linking statistics
        self.linking_stats = {
            'total_linkings': 0,
            'successful_linkings': 0,
            'failed_linkings': 0,
            'avg_processing_time': 0.0,
            'strategy_usage': {},
            'confidence_distribution': {}
        }
        
    async def initialize(self):
        """Initialize comprehensive entity linking system with advanced capabilities"""        try:
            self.logger.info("Initializing advanced EntityLinker system...")
            
            # Load advanced sentence transformers for semantic similarity
            await self._load_advanced_transformers()
            
            # Initialize comprehensive knowledge bases for creative industry
            await self._initialize_comprehensive_knowledge_bases()
            
            # Load high-performance vector indexes with FAISS
            await self._load_optimized_vector_indexes()
            
            # Initialize external API clients for real-time data
            await self._initialize_external_api_clients()
            
            # Load and construct knowledge graph with relationships
            await self._construct_knowledge_graph()
            
            # Initialize fuzzy matching and string similarity engines
            await self._initialize_similarity_engines()
            
            # Load pre-computed entity embeddings
            await self._load_entity_embeddings()
            
            # Initialize disambiguation models
            await self._initialize_disambiguation_models()
            
            # Set up real-time knowledge base updates
            await self._setup_realtime_updates()
            
            # Load cached linking results for performance
            await self._load_linking_cache()
            
            # Initialize quality assessment and validation
            await self._initialize_quality_assessment()
            
            self.logger.info("Advanced EntityLinker initialization completed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize EntityLinker: {str(e)}")
            raise
    
    async def _load_advanced_transformers(self):
        """Load multiple sentence transformer models for different use cases"""        try:
            # Primary model for general semantic similarity
            self.primary_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Specialized model for music and creative content
            self.music_transformer = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
            
            # Multilingual model for international content
            self.multilingual_transformer = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            
            # Domain-specific model for business and legal entities
            self.business_transformer = SentenceTransformer('sentence-transformers/all-distilroberta-v1')
            
            # Load custom-trained transformer for creative industry if available
            custom_model_path = self.config.get('custom_transformer_path')
            if custom_model_path:
                try:
                    self.custom_transformer = SentenceTransformer(custom_model_path)
                    self.logger.info("Loaded custom creative industry transformer")
                except Exception as e:
                    self.logger.warning(f"Could not load custom transformer: {e}")
            
            self.logger.info("Loaded advanced sentence transformer ensemble")
            
        except Exception as e:
            self.logger.error(f"Failed to load transformers: {e}")
            # Fallback to basic transformer
            self.primary_transformer = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def _initialize_comprehensive_knowledge_bases(self):
        """Initialize comprehensive knowledge bases for creative industry"""        self.knowledge_bases = {
            'music_artists': {
                'path': '/data/knowledge_bases/music_artists.json',
                'entity_type': EntityCategory.PERSON,
                'priority': 1,
                'size': 0,
                'last_updated': None,
                'entities': {},
                'name_index': {},
                'alias_index': {}
            },
            'music_albums': {
                'path': '/data/knowledge_bases/music_albums.json',
                'entity_type': EntityCategory.CREATIVE_WORK,
                'priority': 1,
                'size': 0,
                'last_updated': None,
                'entities': {},
                'name_index': {},
                'alias_index': {}
            },
            'music_tracks': {
                'path': '/data/knowledge_bases/music_tracks.json',
                'entity_type': EntityCategory.CREATIVE_WORK,
                'priority': 1,
                'size': 0,
                'last_updated': None,
                'entities': {},
                'name_index': {},
                'alias_index': {}
            },
            'record_labels': {
                'path': '/data/knowledge_bases/record_labels.json',
                'entity_type': EntityCategory.ORGANIZATION,
                'priority': 1,
                'size': 0,
                'last_updated': None,
                'entities': {},
                'name_index': {},
                'alias_index': {}
            },
            'streaming_platforms': {
                'path': '/data/knowledge_bases/streaming_platforms.json',
                'entity_type': EntityCategory.PLATFORM,
                'priority': 1,
                'size': 0,
                'last_updated': None,
                'entities': {},
                'name_index': {},
                'alias_index': {}
            },
            'social_media_influencers': {
                'path': '/data/knowledge_bases/influencers.json',
                'entity_type': EntityCategory.PERSON,
                'priority': 2,
                'size': 0,
                'last_updated': None,
                'entities': {},
                'name_index': {},
                'alias_index': {}
            },
            'content_creators': {
                'path': '/data/knowledge_bases/content_creators.json',
                'entity_type': EntityCategory.PERSON,
                'priority': 2,
                'size': 0,
                'last_updated': None,
                'entities': {},
                'name_index': {},
                'alias_index': {}
            },
            'brands_sponsors': {
                'path': '/data/knowledge_bases/brands.json',
                'entity_type': EntityCategory.ORGANIZATION,
                'priority': 2,
                'size': 0,
                'last_updated': None,
                'entities': {},
                'name_index': {},
                'alias_index': {}
            },
            'venues_festivals': {
                'path': '/data/knowledge_bases/venues.json',
                'entity_type': EntityCategory.ORGANIZATION,
                'priority': 2,
                'size': 0,
                'last_updated': None,
                'entities': {},
                'name_index': {},
                'alias_index': {}
            },
            'music_genres': {
                'path': '/data/knowledge_bases/genres.json',
                'entity_type': EntityCategory.GENRE,
                'priority': 3,
                'size': 0,
                'last_updated': None,
                'entities': {},
                'name_index': {},
                'alias_index': {}
            },
            'instruments': {
                'path': '/data/knowledge_bases/instruments.json',
                'entity_type': EntityCategory.INSTRUMENT,
                'priority': 3,
                'size': 0,
                'last_updated': None,
                'entities': {},
                'name_index': {},
                'alias_index': {}
            }
        }
        
        # Load each knowledge base
        for kb_name, kb_config in self.knowledge_bases.items():
            await self._load_knowledge_base(kb_name, kb_config)
        
        # Create unified search indexes
        await self._create_unified_indexes()
        
        self.logger.info(f"Initialized {len(self.knowledge_bases)} knowledge bases")
    
    async def _load_knowledge_base(self, kb_name: str, kb_config: Dict[str, Any]):
        """Load individual knowledge base from file or API"""        try:
            # Try to load from local file first
            if os.path.exists(kb_config['path']):
                with open(kb_config['path'], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    kb_config['entities'] = data.get('entities', {})
                    kb_config['size'] = len(kb_config['entities'])
                    kb_config['last_updated'] = data.get('last_updated')
                    
                    # Build search indexes
                    self._build_kb_indexes(kb_name, kb_config)
                    
                    self.logger.info(f"Loaded {kb_config['size']} entities from {kb_name}")
            else:
                # Load from external API if configured
                api_config = self.config.get(f'{kb_name}_api')
                if api_config:
                    await self._load_kb_from_api(kb_name, kb_config, api_config)
                else:
                    # Create empty knowledge base
                    kb_config['entities'] = {}
                    kb_config['size'] = 0
                    self.logger.warning(f"Knowledge base {kb_name} not found, created empty")
                    
        except Exception as e:
            self.logger.error(f"Failed to load knowledge base {kb_name}: {e}")
            kb_config['entities'] = {}
            kb_config['size'] = 0
    
    def _build_kb_indexes(self, kb_name: str, kb_config: Dict[str, Any]):
        """Build search indexes for knowledge base"""        name_index = {}
        alias_index = {}
        
        for entity_id, entity_data in kb_config['entities'].items():
            # Index canonical name
            canonical_name = entity_data.get('canonical_name', '').lower()
            if canonical_name:
                if canonical_name not in name_index:
                    name_index[canonical_name] = []
                name_index[canonical_name].append(entity_id)
            
            # Index aliases
            aliases = entity_data.get('aliases', [])
            for alias in aliases:
                alias_lower = alias.lower()
                if alias_lower not in alias_index:
                    alias_index[alias_lower] = []
                alias_index[alias_lower].append(entity_id)
        
        kb_config['name_index'] = name_index
        kb_config['alias_index'] = alias_index
    
    async def _load_optimized_vector_indexes(self):
        """Load high-performance FAISS vector indexes for entity embeddings"""        try:
            self.vector_indexes = {}
            
            for kb_name, kb_config in self.knowledge_bases.items():
                if kb_config['size'] > 0:
                    # Create or load FAISS index for this knowledge base
                    index_path = f"/data/vector_indexes/{kb_name}.faiss"
                    embeddings_path = f"/data/vector_indexes/{kb_name}_embeddings.npy"
                    
                    if os.path.exists(index_path) and os.path.exists(embeddings_path):
                        # Load existing index
                        index = faiss.read_index(index_path)
                        embeddings = np.load(embeddings_path)
                        
                        self.vector_indexes[kb_name] = {
                            'index': index,
                            'embeddings': embeddings,
                            'entity_ids': list(kb_config['entities'].keys())
                        }
                        
                        self.logger.info(f"Loaded FAISS index for {kb_name} with {index.ntotal} vectors")
                    else:
                        # Create new index
                        await self._create_vector_index(kb_name, kb_config)
            
        except Exception as e:
            self.logger.error(f"Failed to load vector indexes: {e}")
    
    async def _create_vector_index(self, kb_name: str, kb_config: Dict[str, Any]):
        """Create FAISS vector index for knowledge base"""        try:
            entities = kb_config['entities']
            if not entities:
                return
            
            # Generate embeddings for all entities
            entity_texts = []
            entity_ids = []
            
            for entity_id, entity_data in entities.items():
                # Combine name, aliases, and description for embedding
                text_parts = [entity_data.get('canonical_name', '')]
                text_parts.extend(entity_data.get('aliases', []))
                if entity_data.get('description'):
                    text_parts.append(entity_data['description'])
                
                combined_text = ' '.join(text_parts)
                entity_texts.append(combined_text)
                entity_ids.append(entity_id)
            
            # Generate embeddings
            embeddings = self.primary_transformer.encode(entity_texts)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            index.add(embeddings)
            
            # Store index
            self.vector_indexes[kb_name] = {
                'index': index,
                'embeddings': embeddings,
                'entity_ids': entity_ids
            }
            
            # Save to disk
            os.makedirs("/data/vector_indexes", exist_ok=True)
            faiss.write_index(index, f"/data/vector_indexes/{kb_name}.faiss")
            np.save(f"/data/vector_indexes/{kb_name}_embeddings.npy", embeddings)
            
            self.logger.info(f"Created FAISS index for {kb_name} with {len(entity_ids)} entities")
            
        except Exception as e:
            self.logger.error(f"Failed to create vector index for {kb_name}: {e}")
    
    async def _initialize_external_api_clients(self):
        """Initialize clients for external knowledge bases and APIs"""        self.external_apis = {
            'spotify': {
                'client_id': self.config.get('spotify_client_id'),
                'client_secret': self.config.get('spotify_client_secret'),
                'base_url': 'https://api.spotify.com/v1',
                'enabled': bool(self.config.get('spotify_client_id'))
            },
            'musicbrainz': {
                'base_url': 'https://musicbrainz.org/ws/2',
                'enabled': True
            },
            'discogs': {
                'api_key': self.config.get('discogs_api_key'),
                'base_url': 'https://api.discogs.com',
                'enabled': bool(self.config.get('discogs_api_key'))
            },
            'youtube': {
                'api_key': self.config.get('youtube_api_key'),
                'base_url': 'https://www.googleapis.com/youtube/v3',
                'enabled': bool(self.config.get('youtube_api_key'))
            },
            'instagram': {
                'access_token': self.config.get('instagram_access_token'),
                'base_url': 'https://graph.instagram.com',
                'enabled': bool(self.config.get('instagram_access_token'))
            },
            'wikidata': {
                'base_url': 'https://www.wikidata.org/w/api.php',
                'enabled': True
            },
            'dbpedia': {
                'base_url': 'https://dbpedia.org/sparql',
                'enabled': True
            }
        }
        
        # Initialize API authentication
        await self._setup_api_authentication()
        
        self.logger.info(f"Initialized {sum(1 for api in self.external_apis.values() if api['enabled'])} external API clients")
    
    async def _setup_api_authentication(self):
        """Setup authentication for external APIs"""        try:
            # Spotify authentication
            if self.external_apis['spotify']['enabled']:
                await self._authenticate_spotify()
            
            # Add other API authentication as needed
            
        except Exception as e:
            self.logger.warning(f"Some API authentications failed: {e}")
    
    async def _authenticate_spotify(self):
        """Authenticate with Spotify API"""        try:
            import base64
            
            client_id = self.external_apis['spotify']['client_id']
            client_secret = self.external_apis['spotify']['client_secret']
            
            # Get access token
            auth_str = f"{client_id}:{client_secret}"
            auth_bytes = auth_str.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {'grant_type': 'client_credentials'}
            
            response = requests.post(
                'https://accounts.spotify.com/api/token',
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.external_apis['spotify']['access_token'] = token_data['access_token']
                self.logger.info("Successfully authenticated with Spotify API")
            else:
                self.logger.error(f"Spotify authentication failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Spotify authentication error: {e}")
                'entity_type': EntityCategory.CREATIVE_WORK,
                'priority': 1
            },
            'platforms': {
                'path': '/data/knowledge_bases/platforms.json',
                'entity_type': EntityCategory.PLATFORM,
                'priority': 2
            },
            'brands': {
                'path': '/data/knowledge_bases/brands.json',
                'entity_type': EntityCategory.BRAND,
                'priority': 2
            },
            'venues': {
                'path': '/data/knowledge_bases/venues.json',
                'entity_type': EntityCategory.LOCATION,
                'priority': 3
            }
        }
        
        for kb_name, config in knowledge_base_configs.items():
            try:
                await self._load_knowledge_base(kb_name, config)
                self.logger.info(f"Loaded knowledge base: {kb_name}")
                
            except Exception as e:
                self.logger.warning(f"Failed to load knowledge base {kb_name}: {str(e)}")
                # Create empty knowledge base
                self.knowledge_bases[kb_name] = {
                    'entities': {},
                    'config': config,
                    'last_updated': datetime.now()
                }
    
    async def _load_knowledge_base(self, name: str, config: Dict[str, Any]):
        """Load a specific knowledge base"""        try:
            # Try to load from file
            import os
            if os.path.exists(config['path']):
                with open(config['path'], 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                # Initialize with basic data for creative industry
                data = await self._initialize_basic_knowledge_base(name, config)
            
            # Process and index entities
            processed_entities = {}
            for entity_id, entity_data in data.get('entities', {}).items():
                processed_entity = self._process_knowledge_base_entity(entity_id, entity_data, config)
                processed_entities[entity_id] = processed_entity
            
            self.knowledge_bases[name] = {
                'entities': processed_entities,
                'config': config,
                'last_updated': datetime.now(),
                'total_entities': len(processed_entities)
            }
            
        except Exception as e:
            self.logger.error(f"Error loading knowledge base {name}: {str(e)}")
            raise
    
    async def _initialize_basic_knowledge_base(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize basic knowledge base with essential creative industry entities"""        basic_data = {'entities': {}}
        
        if name == 'music_artists':
            # Add some well-known artists as examples
            basic_artists = {
                'artist_1': {
                    'name': 'Independent Artist',
                    'aliases': ['indie artist', 'unsigned artist'],
                    'type': 'musician',
                    'genres': ['independent'],
                    'platforms': ['spotify', 'soundcloud', 'bandcamp']
                }
            }
            basic_data['entities'] = basic_artists
            
        elif name == 'platforms':
            # Add major platforms
            basic_platforms = {
                'spotify': {
                    'name': 'Spotify',
                    'aliases': ['spotify music'],
                    'type': 'music_streaming',
                    'category': 'audio'
                },
                'youtube': {
                    'name': 'YouTube',
                    'aliases': ['youtube music', 'yt'],
                    'type': 'video_platform',
                    'category': 'video'
                },
                'instagram': {
                    'name': 'Instagram',
                    'aliases': ['ig', 'insta'],
                    'type': 'social_media',
                    'category': 'visual'
                },
                'tiktok': {
                    'name': 'TikTok',
                    'aliases': ['tik tok'],
                    'type': 'social_media',
                    'category': 'short_video'
                }
            }
            basic_data['entities'] = basic_platforms
            
        return basic_data
    
    def _process_knowledge_base_entity(self, entity_id: str, entity_data: Dict[str, Any], config: Dict[str, Any]) -> EntityCandidate:
        """Process and normalize knowledge base entity"""        return EntityCandidate(
            entity_id=entity_id,
            canonical_name=entity_data.get('name', entity_id),
            entity_type=config['entity_type'],
            confidence_score=1.0,  # KB entities have full confidence
            source_database=f"kb_{config.get('name', 'unknown')}",
            aliases=entity_data.get('aliases', []),
            description=entity_data.get('description', ''),
            metadata=entity_data.get('metadata', {}),
            external_ids=entity_data.get('external_ids', {})
        )
    
    async def _load_vector_indexes(self):
        """Load FAISS vector indexes for fast similarity search"""        try:
            # Initialize vector indexes for each knowledge base
            for kb_name, kb_data in self.knowledge_bases.items():
                await self._build_vector_index(kb_name, kb_data)
                
        except Exception as e:
            self.logger.warning(f"Failed to load vector indexes: {str(e)}")
    
    async def _build_vector_index(self, kb_name: str, kb_data: Dict[str, Any]):
        """Build FAISS vector index for a knowledge base"""        try:
            if not self.sentence_transformer:
                return
                
            entities = kb_data['entities']
            if not entities:
                return
            
            # Generate embeddings for all entities
            entity_texts = []
            entity_ids = []
            
            for entity_id, entity in entities.items():
                # Combine name and aliases for embedding
                text_parts = [entity.canonical_name] + entity.aliases
                combined_text = ' '.join(text_parts)
                entity_texts.append(combined_text)
                entity_ids.append(entity_id)
            
            # Generate embeddings
            embeddings = self.sentence_transformer.encode(entity_texts, convert_to_numpy=True)
            
            # Build FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            index.add(embeddings.astype('float32'))
            
            # Store index and metadata
            self.vector_indexes[kb_name] = {
                'index': index,
                'entity_ids': entity_ids,
                'embeddings': embeddings,
                'dimension': dimension
            }
            
            self.logger.info(f"Built vector index for {kb_name}: {len(entity_ids)} entities")
            
        except Exception as e:
            self.logger.error(f"Failed to build vector index for {kb_name}: {str(e)}")
    
    async def _initialize_external_apis(self):
        """Initialize external API clients for entity linking"""        self.api_configs = {
            'musicbrainz': {
                'base_url': 'https://musicbrainz.org/ws/2',
                'rate_limit': 1.0,  # 1 request per second
                'headers': {'User-Agent': 'IA-Influencer-Agent/2.0'},
                'timeout': 5.0
            },
            'discogs': {
                'base_url': 'https://api.discogs.com',
                'rate_limit': 0.4,  # 25 requests per minute
                'headers': {'User-Agent': 'IA-Influencer-Agent/2.0'},
                'timeout': 5.0
            },
            'spotify': {
                'base_url': 'https://api.spotify.com/v1',
                'rate_limit': 10.0,  # High rate limit with proper auth
                'headers': {},
                'timeout': 3.0
            }
        }
        
        # Initialize rate limiters
        for api_name in self.api_configs.keys():
            self.api_rate_limits[api_name] = {
                'last_request': 0.0,
                'request_count': 0
            }
    
    async def _load_knowledge_graph(self):
        """Load knowledge graph for relationship-based linking"""        try:
            # Build knowledge graph from all knowledge bases
            for kb_name, kb_data in self.knowledge_bases.items():
                for entity_id, entity in kb_data['entities'].items():
                    # Add entity node
                    self.knowledge_graph.add_node(
                        entity_id,
                        name=entity.canonical_name,
                        type=entity.entity_type.value,
                        source=kb_name
                    )
                    
                    # Add relationships based on metadata
                    if 'related_entities' in entity.metadata:
                        for related_id in entity.metadata['related_entities']:
                            self.knowledge_graph.add_edge(entity_id, related_id, relation='related')
            
            self.logger.info(f"Loaded knowledge graph: {len(self.knowledge_graph.nodes)} nodes, {len(self.knowledge_graph.edges)} edges")
            
        except Exception as e:
            self.logger.warning(f"Failed to load knowledge graph: {str(e)}")
    
    async def _load_linking_cache(self):
        """Load cached linking results"""        try:
            cache_path = '/cache/entity_linking.json'
            import os
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    self.linking_cache = json.load(f)
                self.logger.info(f"Loaded {len(self.linking_cache)} cached linking results")
            
        except Exception as e:
            self.logger.warning(f"Failed to load linking cache: {str(e)}")
            self.linking_cache = {}
    
    @cache_manager.cached(ttl=3600)
    async def link_entity(
        self,
        entity: ExtractedEntity,
        context: Optional[str] = None,
        strategy: Optional[LinkingStrategy] = None,
        confidence_threshold: float = 0.5
    ) -> LinkingResult:
        """        Link an extracted entity to a canonical knowledge base entity.
        
        Args:
            entity: Extracted entity to link
            context: Additional context for disambiguation
            strategy: Specific linking strategy to use
            confidence_threshold: Minimum confidence for successful linking
            
        Returns:
            LinkingResult with linked entity and metadata
        """        start_time = datetime.now()
        
        try:
            self.logger.debug(f"Linking entity: {entity.text} ({entity.entity_type.value})")
            self.metrics.increment('linking_requests')
            
            # Check cache first
            cache_key = self._generate_cache_key(entity, context, strategy)
            if cache_key in self.linking_cache:
                self.metrics.increment('cache_hits')
                cached_result = self.linking_cache[cache_key]
                return self._deserialize_linking_result(cached_result)
            
            # Get linking candidates
            candidates = await self._get_linking_candidates(entity, context)
            
            # Apply linking strategy
            if strategy:
                best_candidate = await self._apply_single_strategy(entity, candidates, strategy, context)
            else:
                best_candidate = await self._apply_hybrid_strategy(entity, candidates, context)
            
            # Calculate final confidence
            final_confidence = self._calculate_linking_confidence(entity, best_candidate, context)
            
            # Create linking result
            result = LinkingResult(
                original_entity=entity,
                linked_entity=best_candidate if final_confidence >= confidence_threshold else None,
                confidence=final_confidence,
                linking_strategy=strategy or LinkingStrategy.HYBRID_ENSEMBLE,
                alternative_candidates=candidates[:5],  # Top 5 alternatives
                disambiguation_context={'context': context},
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            
            # Cache result
            self.linking_cache[cache_key] = self._serialize_linking_result(result)
            
            # Update statistics
            self._update_linking_stats(result)
            
            self.logger.info(f"Entity linking completed: {entity.text} -> {best_candidate.canonical_name if best_candidate else 'None'} (confidence: {final_confidence:.3f})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Entity linking failed: {str(e)}")
            self.metrics.increment('linking_errors')
            raise
    
    async def _get_linking_candidates(self, entity: ExtractedEntity, context: Optional[str]) -> List[EntityCandidate]:
        """Get all possible linking candidates for an entity"""        all_candidates = []
        
        # Get candidates from knowledge bases
        kb_candidates = await self._get_knowledge_base_candidates(entity)
        all_candidates.extend(kb_candidates)
        
        # Get candidates from external APIs
        api_candidates = await self._get_api_candidates(entity)
        all_candidates.extend(api_candidates)
        
        # Get candidates from vector similarity
        if self.sentence_transformer:
            vector_candidates = await self._get_vector_similarity_candidates(entity)
            all_candidates.extend(vector_candidates)
        
        # Remove duplicates and sort by confidence
        unique_candidates = self._deduplicate_candidates(all_candidates)
        sorted_candidates = sorted(unique_candidates, key=lambda c: c.confidence_score, reverse=True)
        
        return sorted_candidates[:20]  # Return top 20 candidates
    
    async def _get_knowledge_base_candidates(self, entity: ExtractedEntity) -> List[EntityCandidate]:
        """Get candidates from local knowledge bases"""        candidates = []
        
        for kb_name, kb_data in self.knowledge_bases.items():
            # Filter by entity type if possible
            kb_config = kb_data['config']
            if kb_config['entity_type'] != entity.entity_type:
                continue
            
            # Search in knowledge base
            for entity_id, kb_entity in kb_data['entities'].items():
                # Exact match
                if entity.text.lower() == kb_entity.canonical_name.lower():
                    kb_entity.confidence_score = 0.95
                    candidates.append(kb_entity)
                    continue
                
                # Alias match
                for alias in kb_entity.aliases:
                    if entity.text.lower() == alias.lower():
                        kb_entity.confidence_score = 0.90
                        candidates.append(kb_entity)
                        break
                
                # Fuzzy match
                fuzzy_score = fuzz.ratio(entity.text.lower(), kb_entity.canonical_name.lower()) / 100.0
                if fuzzy_score >= 0.8:
                    kb_entity.confidence_score = fuzzy_score * 0.8  # Discount for fuzzy match
                    candidates.append(kb_entity)
        
        return candidates
    
    async def _get_api_candidates(self, entity: ExtractedEntity) -> List[EntityCandidate]:
        """Get candidates from external APIs"""        candidates = []
        
        # Select appropriate APIs based on entity type
        relevant_apis = self._select_relevant_apis(entity.entity_type)
        
        for api_name in relevant_apis:
            try:
                api_candidates = await self._query_external_api(api_name, entity)
                candidates.extend(api_candidates)
                
            except Exception as e:
                self.logger.warning(f"Failed to query {api_name}: {str(e)}")
        
        return candidates
    
    def _select_relevant_apis(self, entity_type: EntityCategory) -> List[str]:
        """Select relevant APIs based on entity type"""        api_mapping = {
            EntityCategory.PERSON: ['musicbrainz', 'discogs'],
            EntityCategory.CREATIVE_WORK: ['musicbrainz', 'discogs', 'spotify'],
            EntityCategory.PLATFORM: [],  # Usually handled by KB
            EntityCategory.BRAND: ['discogs'],
            EntityCategory.ORGANIZATION: ['musicbrainz'],
            EntityCategory.LOCATION: ['musicbrainz']
        }
        return api_mapping.get(entity_type, [])
    
    async def _query_external_api(self, api_name: str, entity: ExtractedEntity) -> List[EntityCandidate]:
        """Query external API for entity candidates"""        candidates = []
        
        try:
            # Rate limiting
            await self._apply_rate_limit(api_name)
            
            if api_name == 'musicbrainz':
                candidates = await self._query_musicbrainz(entity)
            elif api_name == 'discogs':
                candidates = await self._query_discogs(entity)
            elif api_name == 'spotify':
                candidates = await self._query_spotify(entity)
            
        except Exception as e:
            self.logger.warning(f"API query failed for {api_name}: {str(e)}")
        
        return candidates
    
    async def _apply_rate_limit(self, api_name: str):
        """Apply rate limiting for API requests"""        config = self.api_configs.get(api_name, {})
        rate_limit = config.get('rate_limit', 1.0)
        
        current_time = datetime.now().timestamp()
        last_request = self.api_rate_limits[api_name]['last_request']
        
        time_since_last = current_time - last_request
        min_interval = 1.0 / rate_limit
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.api_rate_limits[api_name]['last_request'] = datetime.now().timestamp()
        self.api_rate_limits[api_name]['request_count'] += 1
    
    async def _query_musicbrainz(self, entity: ExtractedEntity) -> List[EntityCandidate]:
        """Query MusicBrainz API for music-related entities"""        candidates = []
        
        try:
            config = self.api_configs['musicbrainz']
            
            # Determine MusicBrainz entity type
            mb_entity_type = self._map_to_musicbrainz_type(entity.entity_type)
            if not mb_entity_type:
                return candidates
            
            # Build query
            query = f'"{entity.text}"'
            url = f"{config['base_url']}/{mb_entity_type}/?query={query}&fmt=json&limit=5"
            
            # Make request
            response = requests.get(url, headers=config['headers'], timeout=config['timeout'])
            response.raise_for_status()
            
            data = response.json()
            
            # Process results
            for result in data.get(mb_entity_type, []):
                candidate = EntityCandidate(
                    entity_id=result['id'],
                    canonical_name=result['name'],
                    entity_type=entity.entity_type,
                    confidence_score=self._calculate_api_confidence(entity.text, result['name']),
                    source_database='musicbrainz',
                    metadata={
                        'score': result.get('score', 0),
                        'type': result.get('type'),
                        'disambiguation': result.get('disambiguation', '')
                    },
                    external_ids={'musicbrainz': result['id']}
                )
                candidates.append(candidate)
                
        except Exception as e:
            self.logger.warning(f"MusicBrainz query failed: {str(e)}")
        
        return candidates
    
    async def _query_discogs(self, entity: ExtractedEntity) -> List[EntityCandidate]:
        """Query Discogs API for music industry entities"""        candidates = []
        
        try:
            config = self.api_configs['discogs']
            
            # Build search query
            search_type = 'release' if entity.entity_type == EntityCategory.CREATIVE_WORK else 'artist'
            url = f"{config['base_url']}/database/search"
            params = {
                'q': entity.text,
                'type': search_type,
                'per_page': 5
            }
            
            response = requests.get(url, headers=config['headers'], params=params, timeout=config['timeout'])
            response.raise_for_status()
            
            data = response.json()
            
            # Process results
            for result in data.get('results', []):
                candidate = EntityCandidate(
                    entity_id=str(result['id']),
                    canonical_name=result['title'],
                    entity_type=entity.entity_type,
                    confidence_score=self._calculate_api_confidence(entity.text, result['title']),
                    source_database='discogs',
                    metadata={
                        'type': result.get('type'),
                        'year': result.get('year'),
                        'format': result.get('format', []),
                        'label': result.get('label', [])
                    },
                    external_ids={'discogs': str(result['id'])}
                )
                candidates.append(candidate)
                
        except Exception as e:
            self.logger.warning(f"Discogs query failed: {str(e)}")
        
        return candidates
    
    async def _query_spotify(self, entity: ExtractedEntity) -> List[EntityCandidate]:
        """Query Spotify API for music entities"""        candidates = []
        
        try:
            # Note: This would require Spotify API authentication
            # For now, return empty list
            # In production, implement proper Spotify Web API integration
            pass
            
        except Exception as e:
            self.logger.warning(f"Spotify query failed: {str(e)}")
        
        return candidates
    
    async def _get_vector_similarity_candidates(self, entity: ExtractedEntity) -> List[EntityCandidate]:
        """Get candidates using vector similarity search"""        candidates = []
        
        if not self.sentence_transformer:
            return candidates
        
        try:
            # Generate embedding for entity
            entity_embedding = self.sentence_transformer.encode([entity.text], convert_to_numpy=True)
            faiss.normalize_L2(entity_embedding)
            
            # Search in each vector index
            for kb_name, index_data in self.vector_indexes.items():
                index = index_data['index']
                entity_ids = index_data['entity_ids']
                
                # Search for similar entities
                similarities, indices = index.search(entity_embedding.astype('float32'), k=5)
                
                for similarity, idx in zip(similarities[0], indices[0]):
                    if idx < len(entity_ids) and similarity > 0.7:  # Threshold for similarity
                        entity_id = entity_ids[idx]
                        kb_entity = self.knowledge_bases[kb_name]['entities'][entity_id]
                        
                        # Create candidate with similarity score
                        candidate = EntityCandidate(
                            entity_id=entity_id,
                            canonical_name=kb_entity.canonical_name,
                            entity_type=kb_entity.entity_type,
                            confidence_score=float(similarity),
                            source_database=f"vector_{kb_name}",
                            metadata={'similarity_score': float(similarity)},
                            aliases=kb_entity.aliases
                        )
                        candidates.append(candidate)
                        
        except Exception as e:
            self.logger.warning(f"Vector similarity search failed: {str(e)}")
        
        return candidates
    
    def _deduplicate_candidates(self, candidates: List[EntityCandidate]) -> List[EntityCandidate]:
        """Remove duplicate candidates based on canonical name and source"""        seen = set()
        unique_candidates = []
        
        for candidate in candidates:
            key = (candidate.canonical_name.lower(), candidate.source_database)
            if key not in seen:
                seen.add(key)
                unique_candidates.append(candidate)
        
        return unique_candidates
    
    async def _apply_single_strategy(
        self,
        entity: ExtractedEntity,
        candidates: List[EntityCandidate],
        strategy: LinkingStrategy,
        context: Optional[str]
    ) -> Optional[EntityCandidate]:
        """Apply a single linking strategy"""        if not candidates:
            return None
        
        if strategy == LinkingStrategy.EXACT_MATCH:
            return self._find_exact_match(entity, candidates)
        elif strategy == LinkingStrategy.FUZZY_MATCH:
            return self._find_fuzzy_match(entity, candidates)
        elif strategy == LinkingStrategy.SEMANTIC_SIMILARITY:
            return await self._find_semantic_match(entity, candidates, context)
        elif strategy == LinkingStrategy.KNOWLEDGE_GRAPH:
            return self._find_knowledge_graph_match(entity, candidates, context)
        else:
            # Default to highest confidence
            return max(candidates, key=lambda c: c.confidence_score)
    
    async def _apply_hybrid_strategy(
        self,
        entity: ExtractedEntity,
        candidates: List[EntityCandidate],
        context: Optional[str]
    ) -> Optional[EntityCandidate]:
        """Apply hybrid ensemble strategy combining multiple approaches"""        if not candidates:
            return None
        
        # Score candidates using multiple strategies
        scored_candidates = []
        
        for candidate in candidates:
            scores = {
                'exact': self._score_exact_match(entity.text, candidate.canonical_name),
                'fuzzy': self._score_fuzzy_match(entity.text, candidate.canonical_name),
                'semantic': await self._score_semantic_match(entity.text, candidate.canonical_name),
                'source': self._score_source_reliability(candidate.source_database),
                'context': self._score_context_match(entity, candidate, context)
            }
            
            # Weighted combination
            weights = {
                'exact': 0.3,
                'fuzzy': 0.2,
                'semantic': 0.25,
                'source': 0.15,
                'context': 0.1
            }
            
            combined_score = sum(scores[key] * weights[key] for key in scores.keys())
            
            scored_candidates.append((candidate, combined_score))
        
        # Return candidate with highest combined score
        best_candidate, best_score = max(scored_candidates, key=lambda x: x[1])
        best_candidate.confidence_score = best_score
        
        return best_candidate
    
    def _find_exact_match(self, entity: ExtractedEntity, candidates: List[EntityCandidate]) -> Optional[EntityCandidate]:
        """Find exact match candidate"""        entity_text_lower = entity.text.lower()
        
        for candidate in candidates:
            if candidate.canonical_name.lower() == entity_text_lower:
                return candidate
            
            # Check aliases
            for alias in candidate.aliases:
                if alias.lower() == entity_text_lower:
                    return candidate
        
        return None
    
    def _find_fuzzy_match(self, entity: ExtractedEntity, candidates: List[EntityCandidate]) -> Optional[EntityCandidate]:
        """Find best fuzzy match candidate"""        best_candidate = None
        best_score = 0
        
        for candidate in candidates:
            # Score against canonical name
            score = fuzz.ratio(entity.text.lower(), candidate.canonical_name.lower()) / 100.0
            
            # Score against aliases
            for alias in candidate.aliases:
                alias_score = fuzz.ratio(entity.text.lower(), alias.lower()) / 100.0
                score = max(score, alias_score)
            
            if score > best_score:
                best_score = score
                best_candidate = candidate
        
        if best_candidate:
            best_candidate.confidence_score = best_score
        
        return best_candidate
    
    async def _find_semantic_match(
        self,
        entity: ExtractedEntity,
        candidates: List[EntityCandidate],
        context: Optional[str]
    ) -> Optional[EntityCandidate]:
        """Find best semantic similarity match"""        if not self.sentence_transformer:
            return None
        
        # Create context-aware entity representation
        entity_text = entity.text
        if context:
            entity_text = f"{context} {entity_text}"
        
        entity_embedding = self.sentence_transformer.encode([entity_text])
        
        best_candidate = None
        best_similarity = 0
        
        for candidate in candidates:
            # Create candidate representation
            candidate_text = f"{candidate.canonical_name} {' '.join(candidate.aliases)}"
            candidate_embedding = self.sentence_transformer.encode([candidate_text])
            
            # Calculate cosine similarity
            similarity = np.dot(entity_embedding[0], candidate_embedding[0]) / (
                np.linalg.norm(entity_embedding[0]) * np.linalg.norm(candidate_embedding[0])
            )
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_candidate = candidate
        
        if best_candidate:
            best_candidate.confidence_score = best_similarity
        
        return best_candidate
    
    def _find_knowledge_graph_match(
        self,
        entity: ExtractedEntity,
        candidates: List[EntityCandidate],
        context: Optional[str]
    ) -> Optional[EntityCandidate]:
        """Find match using knowledge graph relationships"""        # Simple implementation - could be enhanced with graph algorithms
        # For now, boost confidence of candidates that have connections in the graph
        
        for candidate in candidates:
            if candidate.entity_id in self.knowledge_graph.nodes:
                # Boost confidence for entities in knowledge graph
                candidate.confidence_score = min(candidate.confidence_score * 1.1, 1.0)
        
        # Return highest confidence candidate
        return max(candidates, key=lambda c: c.confidence_score) if candidates else None
    
    def _score_exact_match(self, text1: str, text2: str) -> float:
        """Score exact match between two texts"""        return 1.0 if text1.lower() == text2.lower() else 0.0
    
    def _score_fuzzy_match(self, text1: str, text2: str) -> float:
        """Score fuzzy match between two texts"""        return fuzz.ratio(text1.lower(), text2.lower()) / 100.0
    
    async def _score_semantic_match(self, text1: str, text2: str) -> float:
        """Score semantic similarity between two texts"""        if not self.sentence_transformer:
            return 0.0
        
        try:
            embeddings = self.sentence_transformer.encode([text1, text2])
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            return max(0.0, float(similarity))
            
        except Exception:
            return 0.0
    
    def _score_source_reliability(self, source: str) -> float:
        """Score reliability of the data source"""        source_scores = {
            'musicbrainz': 0.9,
            'discogs': 0.8,
            'spotify': 0.85,
            'kb_music_artists': 0.95,
            'kb_platforms': 0.9,
            'vector_': 0.7  # Prefix for vector sources
        }
        
        for source_key, score in source_scores.items():
            if source.startswith(source_key):
                return score
        
        return 0.5  # Default score for unknown sources
    
    def _score_context_match(
        self,
        entity: ExtractedEntity,
        candidate: EntityCandidate,
        context: Optional[str]
    ) -> float:
        """Score how well candidate matches the context"""        if not context:
            return 0.5  # Neutral score if no context
        
        context_lower = context.lower()
        
        # Check if candidate metadata matches context
        metadata_match = 0.0
        for key, value in candidate.metadata.items():
            if isinstance(value, str) and value.lower() in context_lower:
                metadata_match += 0.2
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and item.lower() in context_lower:
                        metadata_match += 0.1
        
        return min(metadata_match, 1.0)
    
    def _calculate_api_confidence(self, query_text: str, result_name: str) -> float:
        """Calculate confidence score for API results"""        # Simple confidence based on string similarity
        similarity = fuzz.ratio(query_text.lower(), result_name.lower()) / 100.0
        return similarity * 0.8  # Discount for API uncertainty
    
    def _calculate_linking_confidence(
        self,
        entity: ExtractedEntity,
        candidate: Optional[EntityCandidate],
        context: Optional[str]
    ) -> float:
        """Calculate final confidence for entity linking"""        if not candidate:
            return 0.0
        
        base_confidence = candidate.confidence_score
        
        # Adjust based on entity extraction confidence
        extraction_confidence = entity.confidence
        combined_confidence = (base_confidence + extraction_confidence) / 2
        
        # Adjust based on source reliability
        source_boost = self._score_source_reliability(candidate.source_database) * 0.1
        
        final_confidence = min(combined_confidence + source_boost, 1.0)
        return final_confidence
    
    def _map_to_musicbrainz_type(self, entity_type: EntityCategory) -> Optional[str]:
        """Map entity category to MusicBrainz entity type"""        mapping = {
            EntityCategory.PERSON: 'artist',
            EntityCategory.CREATIVE_WORK: 'recording',
            EntityCategory.ORGANIZATION: 'label',
            EntityCategory.LOCATION: 'place',
            EntityCategory.EVENT: 'event'
        }
        return mapping.get(entity_type)
    
    def _generate_cache_key(
        self,
        entity: ExtractedEntity,
        context: Optional[str],
        strategy: Optional[LinkingStrategy]
    ) -> str:
        """Generate cache key for linking result"""        key_parts = [
            entity.text,
            entity.entity_type.value,
            str(entity.confidence),
            context or "",
            strategy.value if strategy else "hybrid"
        ]
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _serialize_linking_result(self, result: LinkingResult) -> Dict[str, Any]:
        """Serialize linking result for caching"""        return {
            'linked_entity': result.linked_entity.__dict__ if result.linked_entity else None,
            'confidence': result.confidence,
            'linking_strategy': result.linking_strategy.value,
            'processing_time': result.processing_time
        }
    
    def _deserialize_linking_result(self, data: Dict[str, Any]) -> LinkingResult:
        """Deserialize linking result from cache"""        # This is a simplified version - full implementation would reconstruct all objects
        return LinkingResult(
            original_entity=None,  # Would need to be reconstructed
            linked_entity=EntityCandidate(**data['linked_entity']) if data['linked_entity'] else None,
            confidence=data['confidence'],
            linking_strategy=LinkingStrategy(data['linking_strategy']),
            processing_time=data['processing_time']
        )
    
    def _update_linking_stats(self, result: LinkingResult):
        """Update linking statistics"""        self.linking_stats['total_linkings'] += 1
        
        if result.is_linked:
            self.linking_stats['successful_linkings'] += 1
        else:
            self.linking_stats['failed_linkings'] += 1
        
        # Update average processing time
        current_avg = self.linking_stats['avg_processing_time']
        total_linkings = self.linking_stats['total_linkings']
        new_avg = ((current_avg * (total_linkings - 1)) + result.processing_time) / total_linkings
        self.linking_stats['avg_processing_time'] = new_avg
        
        # Update strategy usage
        strategy_key = result.linking_strategy.value
        self.linking_stats['strategy_usage'][strategy_key] = self.linking_stats['strategy_usage'].get(strategy_key, 0) + 1
        
        # Update confidence distribution
        confidence_bucket = f"{int(result.confidence * 10) * 10}-{int(result.confidence * 10) * 10 + 10}%"
        self.linking_stats['confidence_distribution'][confidence_bucket] = self.linking_stats['confidence_distribution'].get(confidence_bucket, 0) + 1
    
    async def batch_link_entities(
        self,
        entities: List[ExtractedEntity],
        context: Optional[str] = None,
        confidence_threshold: float = 0.5
    ) -> List[LinkingResult]:
        """Link multiple entities in batch for efficiency"""        tasks = []
        
        for entity in entities:
            task = self.link_entity(entity, context, None, confidence_threshold)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, LinkingResult)]
        
        return valid_results
    
    async def save_linking_cache(self):
        """Save linking cache to disk"""        try:
            cache_path = '/cache/entity_linking.json'
            with open(cache_path, 'w') as f:
                json.dump(self.linking_cache, f, indent=2)
            self.logger.info(f"Saved {len(self.linking_cache)} linking results to cache")
            
        except Exception as e:
            self.logger.error(f"Failed to save linking cache: {str(e)}")
    
    async def get_linking_statistics(self) -> Dict[str, Any]:
        """Get entity linking statistics"""        return {
            **self.linking_stats,
            'knowledge_bases': {
                kb_name: kb_data['total_entities']
                for kb_name, kb_data in self.knowledge_bases.items()
            },
            'vector_indexes': {
                idx_name: len(idx_data['entity_ids'])
                for idx_name, idx_data in self.vector_indexes.items()
            },
            'cache_size': len(self.linking_cache),
            'api_requests': {
                api_name: rate_data['request_count']
                for api_name, rate_data in self.api_rate_limits.items()
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for entity linking service"""        return {
            'status': 'healthy',
            'knowledge_bases_loaded': len(self.knowledge_bases),
            'vector_indexes_available': len(self.vector_indexes),
            'sentence_transformer_loaded': self.sentence_transformer is not None,
            'knowledge_graph_nodes': len(self.knowledge_graph.nodes),
            'knowledge_graph_edges': len(self.knowledge_graph.edges),
            'total_linkings': self.linking_stats['total_linkings'],
            'success_rate': (
                self.linking_stats['successful_linkings'] / max(self.linking_stats['total_linkings'], 1)
            ) * 100,
            'avg_processing_time': self.linking_stats['avg_processing_time']
        }
