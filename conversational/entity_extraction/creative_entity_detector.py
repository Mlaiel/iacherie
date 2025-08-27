"""
Creative Entity Detector - Specialized Creative Industry Detection

Advanced entity detection specifically designed for the creative industry,
with specialized recognition for musical terms, artistic concepts, cultural
references, and creative professional roles and relationships.

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
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ...core.base_service import BaseService
from ...core.cache import cache_manager
from ...core.monitoring import MetricsCollector
from ...utils.text_processors import TextPreprocessor
from .entity_extractor import ExtractedEntity, EntityCategory


class CreativeEntityType(Enum):
    """Types of creative industry entities"""
    MUSICAL_GENRE = "musical_genre"
    MUSICAL_INSTRUMENT = "musical_instrument"
    ARTISTIC_TECHNIQUE = "artistic_technique"
    CREATIVE_ROLE = "creative_role"
    CULTURAL_MOVEMENT = "cultural_movement"
    ARTISTIC_STYLE = "artistic_style"
    CREATIVE_MEDIUM = "creative_medium"
    PERFORMANCE_VENUE = "performance_venue"
    ARTISTIC_CONCEPT = "artistic_concept"
    CREATIVE_PROCESS = "creative_process"
    AESTHETIC_QUALITY = "aesthetic_quality"
    CREATIVE_COLLABORATION = "creative_collaboration"
    ARTISTIC_INFLUENCE = "artistic_influence"
    CREATIVE_EXPRESSION = "creative_expression"
    INDUSTRY_TERM = "industry_term"


class CreativeSpecialty(Enum):
    """Creative specialties for focused detection"""
    MUSIC_PRODUCTION = "music_production"
    VISUAL_ARTS = "visual_arts"
    PERFORMING_ARTS = "performing_arts"
    DIGITAL_ARTS = "digital_arts"
    LITERARY_ARTS = "literary_arts"
    FASHION_DESIGN = "fashion_design"
    FILM_VIDEO = "film_video"
    CONTENT_CREATION = "content_creation"


@dataclass
class CreativeEntityData:
    """Creative entity with specialized metadata"""
    entity: ExtractedEntity
    creative_type: CreativeEntityType
    specialty: CreativeSpecialty
    cultural_context: Dict[str, Any] = field(default_factory=dict)
    artistic_metadata: Dict[str, Any] = field(default_factory=dict)
    influence_network: List[str] = field(default_factory=list)
    trend_analysis: Dict[str, float] = field(default_factory=dict)
    creative_value: float = 0.0
    innovation_score: float = 0.0


@dataclass
class CreativeDetectionResult:
    """Result of creative entity detection"""
    creative_entities: List[CreativeEntityData]
    genre_classification: Dict[str, float]
    style_analysis: Dict[str, Any]
    influence_map: Dict[str, List[str]]
    trend_indicators: Dict[str, float]
    creative_summary: Dict[str, Any]
    processing_time: float
    confidence_score: float


class CreativeEntityDetector(BaseService):
    """
    Specialized Creative Entity Detector for creative industry content.
    
    Features:
    - Musical genre and style detection
    - Artistic technique and medium identification
    - Creative role and collaboration analysis
    - Cultural movement and influence tracking
    - Trend analysis and innovation scoring
    - Cross-cultural creative concept mapping
    - Creative process and workflow recognition
    - Aesthetic quality assessment
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("creative_entity_detector")
        self.text_processor = TextPreprocessor()
        
        # NLP models for creative analysis
        self.creative_classifier = None
        self.style_analyzer = None
        self.influence_mapper = None
        
        # Creative knowledge bases
        self.creative_vocabularies = {}
        self.genre_taxonomies = {}
        self.artistic_concepts = {}
        self.cultural_mappings = {}
        
        # Trend analysis models
        self.trend_analyzers = {}
        self.innovation_detectors = {}
        
        # Processing cache
        self.detection_cache = {}
        
        # Statistics
        self.detection_stats = {
            'total_detections': 0,
            'successful_detections': 0,
            'creative_type_distribution': {},
            'specialty_distribution': {},
            'avg_processing_time': 0.0,
            'innovation_discoveries': 0
        }
    
    async def initialize(self):
        """Initialize creative entity detection resources"""
        try:
            self.logger.info("Initializing CreativeEntityDetector...")
            
            # Load creative analysis models
            await self._load_creative_models()
            
            # Initialize creative vocabularies
            await self._load_creative_vocabularies()
            
            # Load genre and style taxonomies
            await self._load_genre_taxonomies()
            
            # Initialize cultural mappings
            await self._load_cultural_mappings()
            
            # Load trend analysis models
            await self._load_trend_analyzers()
            
            self.logger.info("CreativeEntityDetector initialization completed")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize CreativeEntityDetector: {str(e)}")
            raise
    
    async def _load_creative_models(self):
        """Load machine learning models for creative analysis"""
        try:
            # Creative content classifier
            self.creative_classifier = pipeline(
                "text-classification",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            # Style analysis model
            self.style_analyzer = pipeline(
                "feature-extraction",
                model="sentence-transformers/all-MiniLM-L6-v2",
                return_tensors="pt"
            )
            
            self.logger.info("Loaded creative analysis models")
            
        except Exception as e:
            self.logger.warning(f"Failed to load some creative models: {str(e)}")
    
    async def _load_creative_vocabularies(self):
        """Load comprehensive creative industry vocabularies"""
        self.creative_vocabularies = {
            'musical_genres': {
                'electronic': {
                    'subgenres': ['house', 'techno', 'dubstep', 'trance', 'ambient', 'breakbeat', 'drum_and_bass', 'garage'],
                    'characteristics': ['synthesized', 'programmed', 'digital', 'sampled'],
                    'instruments': ['synthesizer', 'drum_machine', 'sampler', 'sequencer'],
                    'pioneers': ['kraftwerk', 'aphex_twin', 'daft_punk', 'deadmau5']
                },
                'hip_hop': {
                    'subgenres': ['old_school', 'new_school', 'trap', 'conscious', 'gangsta', 'alternative'],
                    'characteristics': ['rap', 'beatboxing', 'sampling', 'turntabling'],
                    'elements': ['mcing', 'djing', 'graffiti', 'breakdancing'],
                    'pioneers': ['grandmaster_flash', 'run_dmc', 'public_enemy', 'nas']
                },
                'rock': {
                    'subgenres': ['classic', 'punk', 'alternative', 'progressive', 'metal', 'indie'],
                    'characteristics': ['guitar_driven', 'band_based', 'live_performance'],
                    'instruments': ['electric_guitar', 'bass_guitar', 'drums', 'vocals'],
                    'pioneers': ['beatles', 'led_zeppelin', 'nirvana', 'radiohead']
                },
                'pop': {
                    'subgenres': ['dance_pop', 'teen_pop', 'electropop', 'indie_pop', 'k_pop'],
                    'characteristics': ['catchy', 'commercial', 'mainstream', 'accessible'],
                    'production': ['polished', 'hook_based', 'radio_friendly'],
                    'pioneers': ['michael_jackson', 'madonna', 'prince', 'taylor_swift']
                },
                'jazz': {
                    'subgenres': ['bebop', 'cool_jazz', 'fusion', 'smooth_jazz', 'free_jazz'],
                    'characteristics': ['improvisation', 'complex_harmony', 'swing', 'blues_influence'],
                    'instruments': ['saxophone', 'trumpet', 'piano', 'double_bass'],
                    'pioneers': ['louis_armstrong', 'miles_davis', 'john_coltrane', 'duke_ellington']
                }
            },
            'artistic_techniques': {
                'visual_arts': {
                    'painting': ['oil', 'acrylic', 'watercolor', 'tempera', 'fresco'],
                    'drawing': ['pencil', 'charcoal', 'ink', 'pastel', 'digital'],
                    'printmaking': ['etching', 'lithography', 'screen_printing', 'woodcut'],
                    'sculpture': ['carving', 'modeling', 'casting', 'assemblage', 'installation']
                },
                'digital_arts': {
                    'digital_painting': ['photoshop', 'procreate', 'corel_painter', 'clip_studio'],
                    '3d_modeling': ['blender', 'maya', 'zbrush', 'cinema_4d'],
                    'motion_graphics': ['after_effects', 'premiere', 'davinci_resolve'],
                    'web_design': ['figma', 'sketch', 'adobe_xd', 'webflow']
                },
                'music_production': {
                    'recording': ['multitrack', 'overdubbing', 'punch_in', 'comping'],
                    'mixing': ['eq', 'compression', 'reverb', 'delay', 'automation'],
                    'mastering': ['limiting', 'stereo_enhancement', 'loudness', 'sequencing'],
                    'composition': ['songwriting', 'arrangement', 'orchestration', 'harmony']
                }
            },
            'creative_roles': {
                'music_industry': {
                    'performers': ['vocalist', 'instrumentalist', 'dj', 'rapper', 'singer_songwriter'],
                    'production': ['producer', 'engineer', 'mixer', 'mastering_engineer', 'sound_designer'],
                    'business': ['a&r', 'manager', 'booking_agent', 'publicist', 'label_executive'],
                    'creative': ['songwriter', 'composer', 'arranger', 'music_director', 'session_musician']
                },
                'visual_arts': {
                    'fine_arts': ['painter', 'sculptor', 'printmaker', 'installation_artist', 'conceptual_artist'],
                    'design': ['graphic_designer', 'web_designer', 'ux_designer', 'product_designer'],
                    'digital': ['3d_artist', 'animator', 'vfx_artist', 'motion_designer', 'digital_painter'],
                    'commercial': ['illustrator', 'photographer', 'art_director', 'creative_director']
                },
                'content_creation': {
                    'video': ['content_creator', 'youtuber', 'streamer', 'videographer', 'editor'],
                    'social_media': ['influencer', 'tiktoker', 'instagrammer', 'community_manager'],
                    'writing': ['blogger', 'copywriter', 'journalist', 'author', 'screenwriter'],
                    'audio': ['podcaster', 'voice_actor', 'audio_engineer', 'sound_designer']
                }
            },
            'creative_processes': {
                'ideation': ['brainstorming', 'mind_mapping', 'free_writing', 'sketching', 'improvisation'],
                'development': ['iteration', 'refinement', 'collaboration', 'feedback', 'experimentation'],
                'production': ['execution', 'craftsmanship', 'technique', 'workflow', 'quality_control'],
                'distribution': ['publishing', 'exhibition', 'performance', 'marketing', 'audience_engagement']
            },
            'aesthetic_qualities': {
                'visual': ['minimalist', 'maximalist', 'abstract', 'realistic', 'surreal', 'impressionistic'],
                'auditory': ['melodic', 'rhythmic', 'harmonic', 'atonal', 'ambient', 'aggressive'],
                'emotional': ['melancholic', 'uplifting', 'energetic', 'peaceful', 'dramatic', 'nostalgic'],
                'conceptual': ['innovative', 'traditional', 'experimental', 'commercial', 'avant_garde']
            }
        }
    
    async def _load_genre_taxonomies(self):
        """Load genre classification taxonomies"""
        self.genre_taxonomies = {
            'music_genre_tree': {
                'electronic': {
                    'house': ['deep_house', 'tech_house', 'progressive_house', 'electro_house'],
                    'techno': ['detroit_techno', 'minimal_techno', 'acid_techno', 'industrial_techno'],
                    'dubstep': ['brostep', 'chillstep', 'riddim', 'future_garage'],
                    'trance': ['uplifting_trance', 'progressive_trance', 'psytrance', 'vocal_trance']
                },
                'hip_hop': {
                    'east_coast': ['boom_bap', 'hardcore_hip_hop', 'conscious_rap'],
                    'west_coast': ['g_funk', 'gangsta_rap', 'hyphy'],
                    'south': ['dirty_south', 'crunk', 'trap', 'bounce'],
                    'midwest': ['chicago_rap', 'detroit_rap', 'chopped_and_screwed']
                },
                'rock': {
                    'classic_rock': ['blues_rock', 'hard_rock', 'arena_rock', 'southern_rock'],
                    'alternative': ['grunge', 'britpop', 'indie_rock', 'post_rock'],
                    'metal': ['heavy_metal', 'thrash_metal', 'death_metal', 'black_metal'],
                    'punk': ['hardcore_punk', 'pop_punk', 'post_punk', 'ska_punk']
                }
            },
            'visual_art_movements': {
                'modern': ['impressionism', 'expressionism', 'cubism', 'surrealism', 'abstract_expressionism'],
                'contemporary': ['pop_art', 'minimalism', 'conceptual_art', 'performance_art', 'installation_art'],
                'digital': ['new_media_art', 'digital_art', 'interactive_art', 'virtual_reality_art']
            },
            'content_categories': {
                'entertainment': ['comedy', 'drama', 'action', 'horror', 'documentary', 'reality'],
                'educational': ['tutorial', 'explainer', 'review', 'analysis', 'demonstration'],
                'lifestyle': ['fashion', 'beauty', 'fitness', 'food', 'travel', 'home'],
                'technology': ['tech_review', 'programming', 'gaming', 'science', 'innovation']
            }
        }
    
    async def _load_cultural_mappings(self):
        """Load cultural context mappings"""
        self.cultural_mappings = {
            'regional_music_styles': {
                'latin_america': {
                    'genres': ['reggaeton', 'salsa', 'bachata', 'cumbia', 'samba', 'tango'],
                    'instruments': ['conga', 'bongo', 'timbales', 'maracas', 'guitarra', 'accordion'],
                    'characteristics': ['rhythmic', 'dance_oriented', 'percussion_heavy']
                },
                'africa': {
                    'genres': ['afrobeat', 'highlife', 'soukous', 'mbalax', 'kwaito', 'amapiano'],
                    'instruments': ['djembe', 'kalimba', 'kora', 'talking_drum', 'mbira'],
                    'characteristics': ['polyrhythmic', 'call_and_response', 'communal']
                },
                'asia': {
                    'genres': ['j_pop', 'k_pop', 'bollywood', 'qawwali', 'gamelan', 'enka'],
                    'instruments': ['sitar', 'tabla', 'shamisen', 'erhu', 'gamelan_orchestra'],
                    'characteristics': ['melodic', 'ornamental', 'pentatonic_scales']
                },
                'europe': {
                    'genres': ['folk', 'classical', 'opera', 'flamenco', 'celtic', 'chanson'],
                    'instruments': ['violin', 'piano', 'accordion', 'bagpipes', 'mandolin'],
                    'characteristics': ['harmonic', 'structured', 'lyrical']
                }
            },
            'generational_trends': {
                'gen_z': {
                    'platforms': ['tiktok', 'instagram', 'youtube_shorts', 'discord'],
                    'content_types': ['memes', 'challenges', 'micro_content', 'authentic_content'],
                    'aesthetics': ['retro', 'minimalist', 'colorful', 'authentic'],
                    'values': ['diversity', 'authenticity', 'social_justice', 'sustainability']
                },
                'millennial': {
                    'platforms': ['instagram', 'youtube', 'facebook', 'twitter'],
                    'content_types': ['vlogs', 'tutorials', 'lifestyle_content', 'nostalgia'],
                    'aesthetics': ['polished', 'aspirational', 'curated', 'professional'],
                    'values': ['work_life_balance', 'experiences', 'personal_brand', 'achievement']
                }
            },
            'cultural_movements': {
                'underground': {
                    'characteristics': ['experimental', 'anti_mainstream', 'community_driven', 'diy'],
                    'distribution': ['independent_labels', 'small_venues', 'word_of_mouth', 'niche_platforms'],
                    'aesthetics': ['raw', 'authentic', 'unconventional', 'artistic']
                },
                'mainstream': {
                    'characteristics': ['accessible', 'commercial', 'mass_appeal', 'polished'],
                    'distribution': ['major_labels', 'radio', 'television', 'streaming_platforms'],
                    'aesthetics': ['professional', 'trendy', 'marketable', 'familiar']
                }
            }
        }
    
    async def _load_trend_analyzers(self):
        """Load trend analysis models and data"""
        self.trend_analyzers = {
            'genre_popularity': {
                'rising_genres': ['hyperpop', 'phonk', 'pluggnb', 'jersey_club', 'afrobeats'],
                'declining_genres': ['dubstep', 'big_room_house', 'brostep'],
                'stable_genres': ['pop', 'rock', 'hip_hop', 'electronic', 'r&b']
            },
            'platform_trends': {
                'tiktok': {
                    'trending_sounds': ['viral_audio', 'remixes', 'mashups', 'sound_effects'],
                    'content_formats': ['dance_videos', 'lip_sync', 'comedy_skits', 'tutorials'],
                    'trend_lifecycle': 'fast_viral_decay'
                },
                'instagram': {
                    'trending_formats': ['reels', 'stories', 'igtv', 'live_streams'],
                    'aesthetic_trends': ['vintage_filters', 'minimalist', 'colorful', 'authentic'],
                    'trend_lifecycle': 'medium_sustained_engagement'
                },
                'youtube': {
                    'trending_formats': ['shorts', 'long_form', 'live_streams', 'premieres'],
                    'content_trends': ['educational', 'entertainment', 'music_videos', 'vlogs'],
                    'trend_lifecycle': 'slow_long_term_growth'
                }
            },
            'innovation_indicators': {
                'technology_adoption': ['ai_music_generation', 'virtual_instruments', 'live_streaming', 'nft_art'],
                'creative_techniques': ['genre_fusion', 'cross_cultural_collaboration', 'user_generated_content'],
                'business_models': ['direct_fan_support', 'subscription_content', 'virtual_concerts', 'nft_releases']
            }
        }
    
    @cache_manager.cached(ttl=1800)
    async def detect_creative_entities(
        self,
        text: str,
        specialty_focus: Optional[CreativeSpecialty] = None,
        cultural_context: Optional[str] = None
    ) -> CreativeDetectionResult:
        """
        Detect and analyze creative entities in text.
        
        Args:
            text: Input text to analyze
            specialty_focus: Focus on specific creative specialty
            cultural_context: Cultural context for analysis
            
        Returns:
            CreativeDetectionResult with detected entities and analysis
        """
        start_time = datetime.now()
        
        try:
            self.logger.debug(f"Detecting creative entities in text of length {len(text)}")
            self.metrics.increment('detection_requests')
            
            # Preprocess text
            processed_text = self.text_processor.clean_text(text)
            
            # Detect creative entities
            creative_entities = await self._detect_creative_entities(
                processed_text, specialty_focus, cultural_context
            )
            
            # Classify genres and styles
            genre_classification = await self._classify_genres(processed_text, creative_entities)
            
            # Analyze artistic styles
            style_analysis = await self._analyze_artistic_styles(processed_text, creative_entities)
            
            # Map influences and connections
            influence_map = await self._map_influences(creative_entities)
            
            # Analyze trends
            trend_indicators = await self._analyze_trends(creative_entities, processed_text)
            
            # Generate creative summary
            creative_summary = await self._generate_creative_summary(
                creative_entities, genre_classification, style_analysis
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate confidence score
            confidence_score = self._calculate_detection_confidence(
                creative_entities, genre_classification, style_analysis
            )
            
            result = CreativeDetectionResult(
                creative_entities=creative_entities,
                genre_classification=genre_classification,
                style_analysis=style_analysis,
                influence_map=influence_map,
                trend_indicators=trend_indicators,
                creative_summary=creative_summary,
                processing_time=processing_time,
                confidence_score=confidence_score
            )
            
            # Update statistics
            self._update_detection_stats(result)
            
            self.logger.info(f"Creative detection completed: {len(creative_entities)} entities "
                           f"in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Creative entity detection failed: {str(e)}")
            self.metrics.increment('detection_errors')
            raise
    
    async def _detect_creative_entities(
        self,
        text: str,
        specialty_focus: Optional[CreativeSpecialty],
        cultural_context: Optional[str]
    ) -> List[CreativeEntityData]:
        """Detect creative entities using multiple approaches"""
        entities = []
        
        # Pattern-based detection
        pattern_entities = await self._pattern_based_detection(text, specialty_focus)
        entities.extend(pattern_entities)
        
        # Vocabulary-based detection
        vocab_entities = await self._vocabulary_based_detection(text, specialty_focus)
        entities.extend(vocab_entities)
        
        # ML-based detection
        ml_entities = await self._ml_based_detection(text, specialty_focus)
        entities.extend(ml_entities)
        
        # Cultural context enhancement
        if cultural_context:
            entities = await self._enhance_with_cultural_context(entities, cultural_context)
        
        # Remove duplicates and merge similar entities
        entities = self._deduplicate_entities(entities)
        
        return entities
    
    async def _pattern_based_detection(
        self,
        text: str,
        specialty_focus: Optional[CreativeSpecialty]
    ) -> List[CreativeEntityData]:
        """Detect entities using pattern matching"""
        entities = []
        text_lower = text.lower()
        
        # Musical genre patterns
        genre_patterns = {
            'electronic_subgenres': r'\b(?:deep house|tech house|minimal techno|acid house|future garage)\b',
            'hip_hop_styles': r'\b(?:boom bap|trap music|conscious rap|old school|drill music)\b',
            'rock_variants': r'\b(?:indie rock|post punk|shoegaze|math rock|progressive rock)\b',
            'world_music': r'\b(?:afrobeat|reggaeton|k-pop|j-pop|bollywood|flamenco)\b'
        }
        
        for pattern_type, pattern in genre_patterns.items():
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                entity_text = match.group()
                
                # Create base entity
                base_entity = ExtractedEntity(
                    text=entity_text,
                    label="CREATIVE_GENRE",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.8,
                    category=EntityCategory.CREATIVE
                )
                
                # Enhance with creative metadata
                creative_entity = CreativeEntityData(
                    entity=base_entity,
                    creative_type=CreativeEntityType.MUSICAL_GENRE,
                    specialty=CreativeSpecialty.MUSIC_PRODUCTION,
                    cultural_context=self._get_genre_cultural_context(entity_text),
                    artistic_metadata={'pattern_type': pattern_type},
                    creative_value=0.7,
                    innovation_score=self._calculate_innovation_score(entity_text)
                )
                
                entities.append(creative_entity)
        
        # Artistic technique patterns
        technique_patterns = {
            'music_production': r'\b(?:multitrack|overdub|compression|eq|reverb|mastering|mixing)\b',
            'visual_arts': r'\b(?:oil painting|watercolor|digital art|3d modeling|sculpture)\b',
            'performance': r'\b(?:improvisation|choreography|method acting|voice training)\b'
        }
        
        for technique_type, pattern in technique_patterns.items():
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                entity_text = match.group()
                
                base_entity = ExtractedEntity(
                    text=entity_text,
                    label="ARTISTIC_TECHNIQUE",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.75,
                    category=EntityCategory.CREATIVE
                )
                
                creative_entity = CreativeEntityData(
                    entity=base_entity,
                    creative_type=CreativeEntityType.ARTISTIC_TECHNIQUE,
                    specialty=self._map_technique_to_specialty(technique_type),
                    artistic_metadata={'technique_category': technique_type},
                    creative_value=0.6,
                    innovation_score=0.5
                )
                
                entities.append(creative_entity)
        
        # Creative role patterns
        role_patterns = {
            'music_roles': r'\b(?:producer|songwriter|sound engineer|a&r|session musician)\b',
            'visual_roles': r'\b(?:graphic designer|illustrator|art director|animator|photographer)\b',
            'content_roles': r'\b(?:content creator|influencer|youtuber|streamer|tiktoker)\b'
        }
        
        for role_type, pattern in role_patterns.items():
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                entity_text = match.group()
                
                base_entity = ExtractedEntity(
                    text=entity_text,
                    label="CREATIVE_ROLE",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.85,
                    category=EntityCategory.CREATIVE
                )
                
                creative_entity = CreativeEntityData(
                    entity=base_entity,
                    creative_type=CreativeEntityType.CREATIVE_ROLE,
                    specialty=self._map_role_to_specialty(role_type),
                    artistic_metadata={'role_category': role_type},
                    creative_value=0.8,
                    innovation_score=0.4
                )
                
                entities.append(creative_entity)
        
        return entities
    
    async def _vocabulary_based_detection(
        self,
        text: str,
        specialty_focus: Optional[CreativeSpecialty]
    ) -> List[CreativeEntityData]:
        """Detect entities using creative vocabularies"""
        entities = []
        text_lower = text.lower()
        
        # Search through creative vocabularies
        for vocab_category, vocab_data in self.creative_vocabularies.items():
            if specialty_focus and not self._is_relevant_to_specialty(vocab_category, specialty_focus):
                continue
            
            for subcategory, items in vocab_data.items():
                if isinstance(items, dict):
                    # Handle nested structures
                    for sub_items in items.values():
                        if isinstance(sub_items, list):
                            entities.extend(self._match_vocabulary_items(
                                text_lower, sub_items, vocab_category, subcategory
                            ))
                elif isinstance(items, list):
                    # Handle direct lists
                    entities.extend(self._match_vocabulary_items(
                        text_lower, items, vocab_category, subcategory
                    ))
        
        return entities
    
    def _match_vocabulary_items(
        self,
        text: str,
        items: List[str],
        vocab_category: str,
        subcategory: str
    ) -> List[CreativeEntityData]:
        """Match vocabulary items in text"""
        entities = []
        
        for item in items:
            # Create search patterns for different formats
            patterns = [
                item.replace('_', ' '),  # Replace underscores with spaces
                item.replace('_', '-'),  # Replace underscores with hyphens
                item  # Original format
            ]
            
            for pattern in patterns:
                if pattern.lower() in text:
                    # Find exact position
                    start_pos = text.find(pattern.lower())
                    if start_pos != -1:
                        base_entity = ExtractedEntity(
                            text=pattern,
                            label=f"CREATIVE_{vocab_category.upper()}",
                            start=start_pos,
                            end=start_pos + len(pattern),
                            confidence=0.7,
                            category=EntityCategory.CREATIVE
                        )
                        
                        creative_entity = CreativeEntityData(
                            entity=base_entity,
                            creative_type=self._map_vocab_to_creative_type(vocab_category),
                            specialty=self._map_vocab_to_specialty(vocab_category),
                            artistic_metadata={
                                'vocabulary_category': vocab_category,
                                'subcategory': subcategory,
                                'original_item': item
                            },
                            creative_value=0.6,
                            innovation_score=self._calculate_vocabulary_innovation(item, vocab_category)
                        )
                        
                        entities.append(creative_entity)
                        break  # Only match once per item
        
        return entities
    
    async def _ml_based_detection(
        self,
        text: str,
        specialty_focus: Optional[CreativeSpecialty]
    ) -> List[CreativeEntityData]:
        """Detect entities using machine learning models"""
        entities = []
        
        if not self.creative_classifier:
            return entities
        
        try:
            # Analyze text with creative classifier
            classification_results = self.creative_classifier(text)
            
            # Extract creative concepts from classification
            for result in classification_results:
                if result['score'] > 0.6:  # Confidence threshold
                    # Map classification to creative entity
                    creative_type = self._map_classification_to_creative_type(result['label'])
                    
                    if creative_type:
                        base_entity = ExtractedEntity(
                            text=result['label'],
                            label="ML_CREATIVE_CONCEPT",
                            start=0,  # ML doesn't provide exact positions
                            end=len(result['label']),
                            confidence=result['score'],
                            category=EntityCategory.CREATIVE
                        )
                        
                        creative_entity = CreativeEntityData(
                            entity=base_entity,
                            creative_type=creative_type,
                            specialty=specialty_focus or CreativeSpecialty.CONTENT_CREATION,
                            artistic_metadata={
                                'ml_classification': result['label'],
                                'ml_score': result['score']
                            },
                            creative_value=result['score'],
                            innovation_score=0.5
                        )
                        
                        entities.append(creative_entity)
            
            # Style analysis if available
            if self.style_analyzer:
                style_features = self.style_analyzer(text)
                # Process style features to extract style-related entities
                style_entities = self._extract_style_entities(style_features, text)
                entities.extend(style_entities)
                
        except Exception as e:
            self.logger.warning(f"ML-based detection failed: {str(e)}")
        
        return entities
    
    async def _enhance_with_cultural_context(
        self,
        entities: List[CreativeEntityData],
        cultural_context: str
    ) -> List[CreativeEntityData]:
        """Enhance entities with cultural context"""
        enhanced_entities = []
        
        for entity in entities:
            # Add cultural context based on keywords
            cultural_data = self._extract_cultural_data(cultural_context, entity)
            
            if cultural_data:
                entity.cultural_context.update(cultural_data)
                entity.creative_value *= 1.1  # Boost for cultural relevance
            
            enhanced_entities.append(entity)
        
        return enhanced_entities
    
    async def _classify_genres(
        self,
        text: str,
        entities: List[CreativeEntityData]
    ) -> Dict[str, float]:
        """Classify genres and styles from entities"""
        genre_scores = {}
        
        # Extract genre entities
        genre_entities = [e for e in entities if e.creative_type == CreativeEntityType.MUSICAL_GENRE]
        
        for entity in genre_entities:
            genre_name = entity.entity.text.lower()
            
            # Get genre hierarchy
            main_genre = self._get_main_genre(genre_name)
            if main_genre:
                genre_scores[main_genre] = genre_scores.get(main_genre, 0) + entity.creative_value
            
            # Add specific subgenre
            genre_scores[genre_name] = genre_scores.get(genre_name, 0) + entity.creative_value
        
        # Normalize scores
        if genre_scores:
            max_score = max(genre_scores.values())
            genre_scores = {k: v / max_score for k, v in genre_scores.items()}
        
        return genre_scores
    
    async def _analyze_artistic_styles(
        self,
        text: str,
        entities: List[CreativeEntityData]
    ) -> Dict[str, Any]:
        """Analyze artistic styles and aesthetics"""
        style_analysis = {
            'dominant_styles': [],
            'aesthetic_qualities': [],
            'creative_approaches': [],
            'innovation_level': 0.0,
            'complexity_score': 0.0
        }
        
        # Analyze aesthetic quality entities
        aesthetic_entities = [e for e in entities 
                            if e.creative_type in [CreativeEntityType.AESTHETIC_QUALITY,
                                                 CreativeEntityType.ARTISTIC_STYLE]]
        
        if aesthetic_entities:
            style_analysis['aesthetic_qualities'] = [e.entity.text for e in aesthetic_entities]
            style_analysis['innovation_level'] = np.mean([e.innovation_score for e in aesthetic_entities])
        
        # Analyze technique entities for complexity
        technique_entities = [e for e in entities if e.creative_type == CreativeEntityType.ARTISTIC_TECHNIQUE]
        
        if technique_entities:
            style_analysis['creative_approaches'] = [e.entity.text for e in technique_entities]
            style_analysis['complexity_score'] = len(technique_entities) / 10.0  # Normalize
        
        # Determine dominant styles
        style_counts = {}
        for entity in entities:
            specialty = entity.specialty.value
            style_counts[specialty] = style_counts.get(specialty, 0) + 1
        
        style_analysis['dominant_styles'] = sorted(style_counts.items(), key=lambda x: x[1], reverse=True)
        
        return style_analysis
    
    async def _map_influences(self, entities: List[CreativeEntityData]) -> Dict[str, List[str]]:
        """Map influences and connections between entities"""
        influence_map = {}
        
        # Group entities by type
        entity_groups = {}
        for entity in entities:
            entity_type = entity.creative_type.value
            if entity_type not in entity_groups:
                entity_groups[entity_type] = []
            entity_groups[entity_type].append(entity.entity.text)
        
        # Create influence connections
        for entity_type, entity_list in entity_groups.items():
            if len(entity_list) > 1:
                # Entities of same type influence each other
                for entity_text in entity_list:
                    influences = [e for e in entity_list if e != entity_text]
                    if influences:
                        influence_map[entity_text] = influences[:3]  # Limit to top 3
        
        # Add cross-type influences based on creative knowledge
        genre_entities = entity_groups.get('musical_genre', [])
        technique_entities = entity_groups.get('artistic_technique', [])
        
        for genre in genre_entities:
            related_techniques = self._get_related_techniques(genre)
            if related_techniques:
                influence_map[genre] = influence_map.get(genre, []) + related_techniques
        
        return influence_map
    
    async def _analyze_trends(
        self,
        entities: List[CreativeEntityData],
        text: str
    ) -> Dict[str, float]:
        """Analyze trend indicators"""
        trend_indicators = {
            'innovation_trend': 0.0,
            'mainstream_appeal': 0.0,
            'underground_factor': 0.0,
            'cross_cultural_fusion': 0.0,
            'technology_integration': 0.0,
            'generational_relevance': 0.0
        }
        
        if not entities:
            return trend_indicators
        
        # Calculate innovation trend
        innovation_scores = [e.innovation_score for e in entities]
        trend_indicators['innovation_trend'] = np.mean(innovation_scores)
        
        # Analyze mainstream vs underground
        mainstream_keywords = ['commercial', 'radio', 'mainstream', 'popular', 'chart']
        underground_keywords = ['indie', 'underground', 'experimental', 'avant-garde', 'diy']
        
        text_lower = text.lower()
        mainstream_count = sum(1 for keyword in mainstream_keywords if keyword in text_lower)
        underground_count = sum(1 for keyword in underground_keywords if keyword in text_lower)
        
        total_keywords = mainstream_count + underground_count
        if total_keywords > 0:
            trend_indicators['mainstream_appeal'] = mainstream_count / total_keywords
            trend_indicators['underground_factor'] = underground_count / total_keywords
        
        # Analyze cross-cultural fusion
        cultural_entities = [e for e in entities if 'cultural' in str(e.cultural_context)]
        trend_indicators['cross_cultural_fusion'] = len(cultural_entities) / max(len(entities), 1)
        
        # Technology integration
        tech_keywords = ['digital', 'ai', 'algorithm', 'streaming', 'social media', 'virtual']
        tech_count = sum(1 for keyword in tech_keywords if keyword in text_lower)
        trend_indicators['technology_integration'] = min(1.0, tech_count / 5.0)
        
        # Generational relevance (simplified)
        gen_z_keywords = ['tiktok', 'viral', 'meme', 'authentic', 'diverse']
        gen_z_count = sum(1 for keyword in gen_z_keywords if keyword in text_lower)
        trend_indicators['generational_relevance'] = min(1.0, gen_z_count / 3.0)
        
        return trend_indicators
    
    async def _generate_creative_summary(
        self,
        entities: List[CreativeEntityData],
        genre_classification: Dict[str, float],
        style_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive creative summary"""
        summary = {
            'total_entities': len(entities),
            'creative_diversity': 0.0,
            'innovation_potential': 0.0,
            'commercial_viability': 0.0,
            'artistic_complexity': 0.0,
            'key_themes': [],
            'recommended_focus': [],
            'creative_opportunities': []
        }
        
        if not entities:
            return summary
        
        # Calculate creative diversity
        entity_types = set(e.creative_type for e in entities)
        summary['creative_diversity'] = len(entity_types) / len(CreativeEntityType)
        
        # Innovation potential
        innovation_scores = [e.innovation_score for e in entities]
        summary['innovation_potential'] = np.mean(innovation_scores)
        
        # Commercial viability (inverse of underground factor)
        creative_values = [e.creative_value for e in entities]
        summary['commercial_viability'] = np.mean(creative_values)
        
        # Artistic complexity
        summary['artistic_complexity'] = style_analysis.get('complexity_score', 0.0)
        
        # Key themes from most common entity types
        type_counts = {}
        for entity in entities:
            entity_type = entity.creative_type.value
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        
        summary['key_themes'] = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Recommended focus based on strengths
        if genre_classification:
            top_genre = max(genre_classification.items(), key=lambda x: x[1])
            summary['recommended_focus'].append(f"Focus on {top_genre[0]} genre")
        
        if summary['innovation_potential'] > 0.7:
            summary['recommended_focus'].append("Emphasize innovative aspects")
        
        if summary['commercial_viability'] > 0.6:
            summary['recommended_focus'].append("Consider mainstream appeal")
        
        # Creative opportunities
        if summary['creative_diversity'] > 0.5:
            summary['creative_opportunities'].append("Cross-genre collaboration potential")
        
        if summary['innovation_potential'] > 0.6:
            summary['creative_opportunities'].append("Pioneer new creative trends")
        
        if summary['artistic_complexity'] > 0.5:
            summary['creative_opportunities'].append("Showcase technical expertise")
        
        return summary
    
    # Helper methods
    def _is_relevant_to_specialty(self, vocab_category: str, specialty: CreativeSpecialty) -> bool:
        """Check if vocabulary category is relevant to specialty"""
        relevance_map = {
            CreativeSpecialty.MUSIC_PRODUCTION: ['musical_genres', 'creative_processes', 'creative_roles'],
            CreativeSpecialty.VISUAL_ARTS: ['artistic_techniques', 'aesthetic_qualities', 'creative_roles'],
            CreativeSpecialty.CONTENT_CREATION: ['creative_processes', 'creative_roles', 'aesthetic_qualities']
        }
        
        relevant_categories = relevance_map.get(specialty, [])
        return any(cat in vocab_category for cat in relevant_categories)
    
    def _map_vocab_to_creative_type(self, vocab_category: str) -> CreativeEntityType:
        """Map vocabulary category to creative entity type"""
        mapping = {
            'musical_genres': CreativeEntityType.MUSICAL_GENRE,
            'artistic_techniques': CreativeEntityType.ARTISTIC_TECHNIQUE,
            'creative_roles': CreativeEntityType.CREATIVE_ROLE,
            'creative_processes': CreativeEntityType.CREATIVE_PROCESS,
            'aesthetic_qualities': CreativeEntityType.AESTHETIC_QUALITY
        }
        
        for key, value in mapping.items():
            if key in vocab_category:
                return value
        
        return CreativeEntityType.ARTISTIC_CONCEPT
    
    def _map_vocab_to_specialty(self, vocab_category: str) -> CreativeSpecialty:
        """Map vocabulary category to creative specialty"""
        if 'music' in vocab_category:
            return CreativeSpecialty.MUSIC_PRODUCTION
        elif 'visual' in vocab_category or 'artistic' in vocab_category:
            return CreativeSpecialty.VISUAL_ARTS
        elif 'digital' in vocab_category:
            return CreativeSpecialty.DIGITAL_ARTS
        else:
            return CreativeSpecialty.CONTENT_CREATION
    
    def _map_technique_to_specialty(self, technique_type: str) -> CreativeSpecialty:
        """Map technique type to specialty"""
        mapping = {
            'music_production': CreativeSpecialty.MUSIC_PRODUCTION,
            'visual_arts': CreativeSpecialty.VISUAL_ARTS,
            'performance': CreativeSpecialty.PERFORMING_ARTS
        }
        return mapping.get(technique_type, CreativeSpecialty.CONTENT_CREATION)
    
    def _map_role_to_specialty(self, role_type: str) -> CreativeSpecialty:
        """Map role type to specialty"""
        mapping = {
            'music_roles': CreativeSpecialty.MUSIC_PRODUCTION,
            'visual_roles': CreativeSpecialty.VISUAL_ARTS,
            'content_roles': CreativeSpecialty.CONTENT_CREATION
        }
        return mapping.get(role_type, CreativeSpecialty.CONTENT_CREATION)
    
    def _map_classification_to_creative_type(self, label: str) -> Optional[CreativeEntityType]:
        """Map ML classification label to creative entity type"""
        # This would depend on the specific model being used
        label_lower = label.lower()
        
        if 'genre' in label_lower or 'music' in label_lower:
            return CreativeEntityType.MUSICAL_GENRE
        elif 'technique' in label_lower or 'method' in label_lower:
            return CreativeEntityType.ARTISTIC_TECHNIQUE
        elif 'style' in label_lower or 'aesthetic' in label_lower:
            return CreativeEntityType.ARTISTIC_STYLE
        
        return None
    
    def _extract_style_entities(self, style_features, text: str) -> List[CreativeEntityData]:
        """Extract style entities from ML features"""
        entities = []
        
        # This would process the style features to identify style-related entities
        # For now, return empty list as this would require specific model analysis
        
        return entities
    
    def _extract_cultural_data(self, cultural_context: str, entity: CreativeEntityData) -> Dict[str, Any]:
        """Extract cultural context data"""
        cultural_data = {}
        context_lower = cultural_context.lower()
        
        # Check for regional indicators
        for region, data in self.cultural_mappings.get('regional_music_styles', {}).items():
            if any(keyword in context_lower for keyword in data.get('characteristics', [])):
                cultural_data['region'] = region
                cultural_data['regional_characteristics'] = data.get('characteristics', [])
                break
        
        # Check for generational indicators
        for generation, data in self.cultural_mappings.get('generational_trends', {}).items():
            if any(platform in context_lower for platform in data.get('platforms', [])):
                cultural_data['generation'] = generation
                cultural_data['target_platforms'] = data.get('platforms', [])
                break
        
        return cultural_data
    
    def _get_main_genre(self, genre_name: str) -> Optional[str]:
        """Get main genre from subgenre"""
        for main_genre, subgenres in self.genre_taxonomies.get('music_genre_tree', {}).items():
            for subgenre_category, subgenre_list in subgenres.items():
                if genre_name in subgenre_list or genre_name == subgenre_category:
                    return main_genre
        
        return None
    
    def _get_related_techniques(self, genre: str) -> List[str]:
        """Get techniques related to a genre"""
        # Simplified mapping of genres to techniques
        genre_techniques = {
            'electronic': ['synthesis', 'sampling', 'sequencing', 'mixing'],
            'hip_hop': ['sampling', 'beatmaking', 'turntabling', 'rap'],
            'rock': ['guitar_playing', 'band_arrangement', 'live_recording'],
            'jazz': ['improvisation', 'complex_harmony', 'ensemble_playing']
        }
        
        for key, techniques in genre_techniques.items():
            if key in genre.lower():
                return techniques
        
        return []
    
    def _get_genre_cultural_context(self, genre: str) -> Dict[str, Any]:
        """Get cultural context for a genre"""
        # Search cultural mappings for genre context
        for region, data in self.cultural_mappings.get('regional_music_styles', {}).items():
            if genre in data.get('genres', []):
                return {
                    'origin_region': region,
                    'cultural_characteristics': data.get('characteristics', []),
                    'traditional_instruments': data.get('instruments', [])
                }
        
        return {}
    
    def _calculate_innovation_score(self, entity_text: str) -> float:
        """Calculate innovation score for entity"""
        # Check against trending/innovative terms
        innovative_keywords = ['fusion', 'experimental', 'hybrid', 'new', 'emerging', 'cutting-edge']
        traditional_keywords = ['classic', 'traditional', 'standard', 'conventional']
        
        entity_lower = entity_text.lower()
        
        innovation_score = 0.5  # Base score
        
        # Boost for innovative keywords
        for keyword in innovative_keywords:
            if keyword in entity_lower:
                innovation_score += 0.1
        
        # Reduce for traditional keywords
        for keyword in traditional_keywords:
            if keyword in entity_lower:
                innovation_score -= 0.1
        
        # Check against rising trends
        rising_genres = self.trend_analyzers.get('genre_popularity', {}).get('rising_genres', [])
        if any(genre in entity_lower for genre in rising_genres):
            innovation_score += 0.2
        
        # Check against declining trends
        declining_genres = self.trend_analyzers.get('genre_popularity', {}).get('declining_genres', [])
        if any(genre in entity_lower for genre in declining_genres):
            innovation_score -= 0.2
        
        return max(0.0, min(1.0, innovation_score))
    
    def _calculate_vocabulary_innovation(self, item: str, vocab_category: str) -> float:
        """Calculate innovation score for vocabulary item"""
        base_score = 0.4
        
        # Boost for technology-related terms
        if 'digital' in vocab_category or 'technology' in item:
            base_score += 0.2
        
        # Boost for emerging concepts
        emerging_indicators = ['ai', 'virtual', 'nft', 'blockchain', 'algorithm']
        if any(indicator in item.lower() for indicator in emerging_indicators):
            base_score += 0.3
        
        return min(1.0, base_score)
    
    def _deduplicate_entities(self, entities: List[CreativeEntityData]) -> List[CreativeEntityData]:
        """Remove duplicate entities and merge similar ones"""
        unique_entities = []
        seen_texts = set()
        
        for entity in entities:
            entity_text_lower = entity.entity.text.lower()
            
            # Check for exact duplicates
            if entity_text_lower not in seen_texts:
                seen_texts.add(entity_text_lower)
                unique_entities.append(entity)
            else:
                # Merge with existing entity (enhance metadata)
                for existing_entity in unique_entities:
                    if existing_entity.entity.text.lower() == entity_text_lower:
                        # Merge artistic metadata
                        existing_entity.artistic_metadata.update(entity.artistic_metadata)
                        # Take higher confidence
                        if entity.entity.confidence > existing_entity.entity.confidence:
                            existing_entity.entity.confidence = entity.entity.confidence
                        break
        
        return unique_entities
    
    def _calculate_detection_confidence(
        self,
        entities: List[CreativeEntityData],
        genre_classification: Dict[str, float],
        style_analysis: Dict[str, Any]
    ) -> float:
        """Calculate overall detection confidence"""
        factors = []
        
        # Entity detection confidence
        if entities:
            entity_confidences = [e.entity.confidence for e in entities]
            factors.append(np.mean(entity_confidences))
        
        # Genre classification confidence
        if genre_classification:
            genre_scores = list(genre_classification.values())
            factors.append(np.mean(genre_scores))
        
        # Style analysis completeness
        style_completeness = len(style_analysis.get('aesthetic_qualities', [])) / 5.0
        factors.append(min(1.0, style_completeness))
        
        # Number of entities factor
        entity_count_factor = min(1.0, len(entities) / 10.0)
        factors.append(entity_count_factor)
        
        return np.mean(factors) if factors else 0.5
    
    def _update_detection_stats(self, result: CreativeDetectionResult):
        """Update detection statistics"""
        self.detection_stats['total_detections'] += 1
        self.detection_stats['successful_detections'] += 1
        
        # Update creative type distribution
        for entity in result.creative_entities:
            creative_type = entity.creative_type.value
            self.detection_stats['creative_type_distribution'][creative_type] = \
                self.detection_stats['creative_type_distribution'].get(creative_type, 0) + 1
        
        # Update specialty distribution
        for entity in result.creative_entities:
            specialty = entity.specialty.value
            self.detection_stats['specialty_distribution'][specialty] = \
                self.detection_stats['specialty_distribution'].get(specialty, 0) + 1
        
        # Update innovation discoveries
        high_innovation_entities = [e for e in result.creative_entities if e.innovation_score > 0.7]
        self.detection_stats['innovation_discoveries'] += len(high_innovation_entities)
        
        # Update average processing time
        current_avg = self.detection_stats['avg_processing_time']
        total_detections = self.detection_stats['total_detections']
        new_avg = ((current_avg * (total_detections - 1)) + result.processing_time) / total_detections
        self.detection_stats['avg_processing_time'] = new_avg
    
    async def get_detection_statistics(self) -> Dict[str, Any]:
        """Get creative detection statistics"""
        return {
            **self.detection_stats,
            'supported_creative_types': [ct.value for ct in CreativeEntityType],
            'supported_specialties': [cs.value for cs in CreativeSpecialty],
            'vocabulary_categories': list(self.creative_vocabularies.keys()),
            'cultural_regions': list(self.cultural_mappings.get('regional_music_styles', {}).keys()),
            'trend_indicators': list(self.trend_analyzers.get('genre_popularity', {}).keys())
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for creative entity detector"""
        return {
            'status': 'healthy',
            'creative_classifier_available': self.creative_classifier is not None,
            'style_analyzer_available': self.style_analyzer is not None,
            'vocabularies_loaded': len(self.creative_vocabularies),
            'total_detections': self.detection_stats['total_detections'],
            'success_rate': (
                self.detection_stats['successful_detections'] / 
                max(self.detection_stats['total_detections'], 1)
            ) * 100,
            'avg_processing_time': self.detection_stats['avg_processing_time'],
            'innovation_discoveries': self.detection_stats['innovation_discoveries']
        }
