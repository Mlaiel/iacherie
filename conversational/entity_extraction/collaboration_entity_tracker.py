"""Collaboration Entity Tracker - Specialized Module

Advanced collaboration opportunity detection and tracking for content creators.
Identifies potential collaborators, partnership opportunities, brand mentions,
and cross-platform collaboration patterns for strategic networking optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de

Team Specializations:
- Lead AI Developer: Advanced ML/NLP architectures
- Backend Senior: Enterprise-grade scalable systems  
- ML Engineer: Production ML pipelines & optimization
- Database Administrator: High-performance data architecture
- Security Expert: Advanced cybersecurity & protection
- Microservices Architect: Distributed systems design
- Audio Engineer: Professional audio processing
- DevOps Engineer: CI/CD & infrastructure automation
- IA Prompt Engineer: Advanced AI prompt optimization
"""
import asyncio
import re
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging

import spacy
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
import networkx as nx
import torch

from ...core.base_service import BaseService
from ...core.cache import cache_manager
from ...core.monitoring import MetricsCollector
from ...models.content import ContentType, ContentMetadata
from ...models.entities import EntityType, Entity
from ...utils.text_processors import TextPreprocessor
from ...utils.validation import validate_input


class CollaborationType(Enum):
    """Types of collaboration opportunities"""
    MUSIC_COLLABORATION = "music_collaboration"
    CONTENT_COLLABORATION = "content_collaboration"
    BRAND_PARTNERSHIP = "brand_partnership"
    CROSS_PROMOTION = "cross_promotion"
    FEATURE_REQUEST = "feature_request"
    REMIX_OPPORTUNITY = "remix_opportunity"
    COVER_COLLABORATION = "cover_collaboration"
    DUET_OPPORTUNITY = "duet_opportunity"
    JOINT_VENTURE = "joint_venture"
    SPONSORSHIP = "sponsorship"
    AFFILIATE_PARTNERSHIP = "affiliate_partnership"
    GUEST_APPEARANCE = "guest_appearance"
    MENTORSHIP = "mentorship"
    SKILL_EXCHANGE = "skill_exchange"
    NETWORK_BUILDING = "network_building"


class CollaborationStatus(Enum):
    """Status of collaboration opportunities"""
    DETECTED = "detected"
    ANALYZED = "analyzed"
    CONTACTED = "contacted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DECLINED = "declined"
    EXPIRED = "expired"


class CollaborationPriority(Enum):
    """Priority levels for collaboration opportunities"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CollaborationEntity:
    """Collaboration opportunity entity with comprehensive metadata"""
    text: str
    collaboration_type: CollaborationType
    priority: CollaborationPriority
    status: CollaborationStatus
    confidence: float
    start_pos: int
    end_pos: int
    collaborator_info: Dict[str, Any] = field(default_factory=dict)
    opportunity_score: float = 0.0
    matching_criteria: List[str] = field(default_factory=list)
    contact_information: Dict[str, str] = field(default_factory=dict)
    social_metrics: Dict[str, int] = field(default_factory=dict)
    compatibility_score: float = 0.0
    mutual_connections: List[str] = field(default_factory=list)
    collaboration_history: List[Dict[str, Any]] = field(default_factory=list)
    estimated_reach: int = 0
    genres_overlap: List[str] = field(default_factory=list)
    platforms_shared: List[str] = field(default_factory=list)
    location_info: Dict[str, str] = field(default_factory=dict)
    availability_window: Optional[Tuple[datetime, datetime]] = None
    budget_range: Optional[Tuple[int, int]] = None
    requirements: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    extracted_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class CollaborationNetwork:
    """Network analysis of collaboration opportunities"""
    nodes: List[str]
    edges: List[Tuple[str, str, float]]
    clusters: List[List[str]]
    central_nodes: List[str]
    collaboration_paths: Dict[str, List[str]]
    network_metrics: Dict[str, float]
    influence_scores: Dict[str, float]


@dataclass
class CollaborationAnalysisResult:
    """Complete collaboration analysis results"""
    entities: List[CollaborationEntity]
    total_opportunities: int
    high_priority_count: int
    collaboration_network: CollaborationNetwork
    recommendations: List[Dict[str, Any]]
    analysis_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class CollaborationEntityTracker(BaseService):
    """
    Advanced collaboration entity tracker for content creators.
    
    Specializes in:
    - Collaboration opportunity detection
    - Influencer/creator matching
    - Brand partnership identification
    - Cross-platform collaboration analysis
    - Network effect optimization
    - Partnership compatibility scoring
    - Strategic recommendation generation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("collaboration_entity_tracker")
        
        # Load NLP models
        self._load_models()
        
        # Initialize collaboration patterns
        self._collaboration_patterns = self._initialize_collaboration_patterns()
        
        # Initialize vectorizer for similarity analysis
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        
        # Cache configuration
        self.cache_ttl = config.get("cache_ttl", 1800) if config else 1800
        
        # Collaboration tracking history
        self.collaboration_history = {}
        
    def _load_models(self):
        """Load comprehensive ML models for advanced collaboration analysis"""
        try:
            # Primary collaboration classifier with domain-specific fine-tuning
            self.collaboration_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                device=0 if torch.cuda.is_available() else -1,
                return_all_scores=True
            )
            
            # Advanced sentiment analyzer for collaboration tone analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1,
                return_all_scores=True
            )
            
            # Entity relationship extraction model for partnership mapping
            self.relationship_extractor = pipeline(
                "token-classification",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                device=0 if torch.cuda.is_available() else -1,
                aggregation_strategy="first"
            )
            
            # Influencer compatibility scorer
            self.compatibility_scorer = pipeline(
                "text-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Brand-creator matching model
            self.brand_matcher = pipeline(
                "feature-extraction",
                model="sentence-transformers/all-MiniLM-L6-v2",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Collaboration success predictor
            self.success_predictor = self._initialize_success_prediction_model()
            
            # Load spaCy model for advanced NLP processing
            try:
                self.nlp = spacy.load("en_core_web_lg")
            except OSError:
                try:
                    self.nlp = spacy.load("en_core_web_md")
                except OSError:
                    self.nlp = spacy.load("en_core_web_sm")
                    self.logger.warning("Using basic spaCy model as fallback")
            
            # Initialize network analysis tools
            self.collaboration_graph = nx.Graph()
            
            # Load industry-specific vocabularies
            self._load_industry_vocabularies()
            
            # Initialize real-time tracking components
            self._initialize_real_time_tracking()
            
            self.models_loaded = True
            self.logger.info("All collaboration analysis models loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load collaboration models: {e}")
            self.models_loaded = False
            # Load fallback models
            await self._load_fallback_models()
    
    def _initialize_success_prediction_model(self):
        """Initialize ML model for predicting collaboration success"""
        import torch.nn as nn
        
        class CollaborationSuccessPredictor(nn.Module):
            def __init__(self, input_dim=150, hidden_dims=[256, 128, 64]):
                super(CollaborationSuccessPredictor, self).__init__()
                
                layers = []
                prev_dim = input_dim
                
                for hidden_dim in hidden_dims:
                    layers.extend([
                        nn.Linear(prev_dim, hidden_dim),
                        nn.ReLU(),
                        nn.BatchNorm1d(hidden_dim),
                        nn.Dropout(0.3)
                    ])
                    prev_dim = hidden_dim
                
                # Output layer for success probability
                layers.append(nn.Linear(prev_dim, 1))
                layers.append(nn.Sigmoid())
                
                self.network = nn.Sequential(*layers)
            
            def forward(self, x):
                return self.network(x)
        
        model = CollaborationSuccessPredictor()
        
        # Load pre-trained weights if available
        success_model_path = self.config.get('collaboration_success_model_path')
        if success_model_path:
            try:
                model.load_state_dict(torch.load(success_model_path))
                self.logger.info("Loaded pre-trained collaboration success model")
            except Exception as e:
                self.logger.warning(f"Could not load success prediction weights: {e}")
        
        return model
    
    def _load_industry_vocabularies(self):
        """Load comprehensive industry-specific vocabularies for collaboration detection"""
        self.industry_vocab = {
            'music_industry': {
                'roles': [
                    'producer', 'songwriter', 'vocalist', 'rapper', 'singer', 'composer',
                    'musician', 'drummer', 'guitarist', 'pianist', 'bassist', 'dj',
                    'sound_engineer', 'mixing_engineer', 'mastering_engineer', 'beatmaker'
                ],
                'collaboration_terms': [
                    'featuring', 'collab', 'remix', 'cover', 'duet', 'feature',
                    'studio_session', 'jam_session', 'recording_session', 'co_write'
                ],
                'opportunities': [
                    'looking_for_producer', 'need_vocalist', 'seeking_collaboration',
                    'open_to_features', 'accepting_remixes', 'studio_available'
                ]
            },
            'content_creation': {
                'roles': [
                    'influencer', 'creator', 'blogger', 'vlogger', 'photographer',
                    'videographer', 'editor', 'animator', 'designer', 'content_strategist'
                ],
                'collaboration_terms': [
                    'guest_post', 'takeover', 'cross_promotion', 'joint_content',
                    'collaboration_video', 'podcast_guest', 'interview'
                ],
                'platforms': [
                    'youtube', 'instagram', 'tiktok', 'twitch', 'linkedin',
                    'twitter', 'facebook', 'snapchat', 'pinterest', 'discord'
                ]
            },
            'brand_partnerships': {
                'types': [
                    'sponsored_content', 'brand_ambassador', 'affiliate_marketing',
                    'product_placement', 'brand_collaboration', 'endorsement'
                ],
                'industries': [
                    'fashion', 'beauty', 'technology', 'gaming', 'fitness',
                    'food', 'travel', 'automotive', 'finance', 'education'
                ],
                'terms': [
                    'partnership_opportunity', 'brand_deal', 'sponsorship',
                    'marketing_campaign', 'product_launch', 'brand_activation'
                ]
            },
            'business_opportunities': {
                'types': [
                    'joint_venture', 'merger', 'acquisition', 'licensing_deal',
                    'distribution_agreement', 'publishing_deal', 'sync_opportunity'
                ],
                'financial_terms': [
                    'revenue_share', 'profit_split', 'royalty_agreement',
                    'advance_payment', 'milestone_payment', 'performance_bonus'
                ],
                'legal_terms': [
                    'exclusive_agreement', 'non_exclusive', 'territory_rights',
                    'term_length', 'renewal_option', 'termination_clause'
                ]
            }
        }
    
    def _initialize_real_time_tracking(self):
        """Initialize real-time collaboration opportunity tracking"""
        self.tracking_components = {
            'social_media_monitors': {
                'twitter_api': self._initialize_twitter_monitor(),
                'instagram_api': self._initialize_instagram_monitor(),
                'youtube_api': self._initialize_youtube_monitor(),
                'tiktok_api': self._initialize_tiktok_monitor()
            },
            'collaboration_keywords': [
                'collab', 'collaboration', 'partnership', 'feature',
                'looking for', 'seeking', 'open to', 'available for',
                'interested in', 'wanting to work with', 'reach out'
            ],
            'engagement_thresholds': {
                'minimum_followers': 1000,
                'minimum_engagement_rate': 0.02,
                'minimum_content_quality_score': 0.7
            },
            'notification_settings': {
                'high_priority_threshold': 0.8,
                'real_time_alerts': True,
                'batch_processing_interval': 300  # 5 minutes
            }
        }
    
    def _initialize_twitter_monitor(self):
        """Initialize Twitter API monitoring for collaboration opportunities"""
        # This would initialize Twitter API v2 streaming
        # For now, return configuration structure
        return {
            'api_version': 'v2',
            'search_terms': ['#collab', '#collaboration', '#musiccollab', '#contentcreator'],
            'user_fields': ['public_metrics', 'verified', 'description'],
            'tweet_fields': ['public_metrics', 'context_annotations', 'entities'],
            'max_results': 100,
            'polling_interval': 60
        }
    
    def _initialize_instagram_monitor(self):
        """Initialize Instagram API monitoring"""
        return {
            'api_version': 'basic_display',
            'hashtags': ['#collab', '#collaboration', '#brandpartnership'],
            'user_fields': ['followers_count', 'media_count'],
            'media_fields': ['like_count', 'comments_count', 'caption'],
            'polling_interval': 300
        }
    
    def _initialize_youtube_monitor(self):
        """Initialize YouTube API monitoring"""
        return {
            'api_version': 'v3',
            'search_terms': ['collaboration', 'featuring', 'guest appearance'],
            'channel_fields': ['statistics', 'snippet'],
            'video_fields': ['statistics', 'snippet'],
            'max_results': 50,
            'polling_interval': 600
        }
    
    def _initialize_tiktok_monitor(self):
        """Initialize TikTok API monitoring"""
        return {
            'api_version': 'research',
            'hashtags': ['#collab', '#duet', '#collaboration'],
            'user_fields': ['follower_count', 'video_count'],
            'video_fields': ['like_count', 'comment_count', 'share_count'],
            'polling_interval': 180
        }
    
    async def _load_fallback_models(self):
        """Load simplified fallback models if advanced models fail"""
        try:
            self.collaboration_classifier = pipeline(
                "text-classification",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Basic spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            
            self.models_loaded = True
            self.logger.info("Loaded fallback collaboration models")
            
        except Exception as e:
            self.logger.error(f"Failed to load fallback models: {e}")
            self.models_loaded = False
    
    def _initialize_collaboration_patterns(self) -> Dict[CollaborationType, List[re.Pattern]]:
        """Initialize regex patterns for collaboration detection"""
        patterns = {
            CollaborationType.MUSIC_COLLABORATION: [
                re.compile(r"collab(?:oration)?.*music", re.IGNORECASE),
                re.compile(r"looking for.*(?:producer|musician|artist)", re.IGNORECASE),
                re.compile(r"feat(?:uring)?.*with", re.IGNORECASE),
                re.compile(r"remix.*collaboration", re.IGNORECASE),
                re.compile(r"studio.*session.*together", re.IGNORECASE)
            ],
            CollaborationType.CONTENT_COLLABORATION: [
                re.compile(r"content.*collaboration", re.IGNORECASE),
                re.compile(r"looking for.*(?:creator|influencer)", re.IGNORECASE),
                re.compile(r"joint.*content", re.IGNORECASE),
                re.compile(r"cross.*promotion", re.IGNORECASE),
                re.compile(r"guest.*(?:post|appearance)", re.IGNORECASE)
            ],
            CollaborationType.BRAND_PARTNERSHIP: [
                re.compile(r"brand.*partnership", re.IGNORECASE),
                re.compile(r"sponsored.*content", re.IGNORECASE),
                re.compile(r"ambassador.*program", re.IGNORECASE),
                re.compile(r"product.*placement", re.IGNORECASE),
                re.compile(r"affiliate.*program", re.IGNORECASE)
            ],
            CollaborationType.CROSS_PROMOTION: [
                re.compile(r"cross.*promot", re.IGNORECASE),
                re.compile(r"mutual.*promotion", re.IGNORECASE),
                re.compile(r"share.*(?:audience|followers)", re.IGNORECASE),
                re.compile(r"exchange.*shoutout", re.IGNORECASE)
            ],
            CollaborationType.DUET_OPPORTUNITY: [
                re.compile(r"duet.*(?:with|collaboration)", re.IGNORECASE),
                re.compile(r"harmonies.*together", re.IGNORECASE),
                re.compile(r"vocal.*collaboration", re.IGNORECASE),
                re.compile(r"singing.*together", re.IGNORECASE)
            ],
            CollaborationType.REMIX_OPPORTUNITY: [
                re.compile(r"remix.*(?:my|this|track)", re.IGNORECASE),
                re.compile(r"looking for.*remix", re.IGNORECASE),
                re.compile(r"beat.*remix", re.IGNORECASE),
                re.compile(r"version.*of.*song", re.IGNORECASE)
            ],
            CollaborationType.SPONSORSHIP: [
                re.compile(r"sponsor(?:ship)?.*opportunit", re.IGNORECASE),
                re.compile(r"looking for.*sponsor", re.IGNORECASE),
                re.compile(r"funding.*(?:project|album)", re.IGNORECASE),
                re.compile(r"invest.*in.*music", re.IGNORECASE)
            ],
            CollaborationType.MENTORSHIP: [
                re.compile(r"mentor(?:ship)?.*program", re.IGNORECASE),
                re.compile(r"looking for.*mentor", re.IGNORECASE),
                re.compile(r"guidance.*from.*expert", re.IGNORECASE),
                re.compile(r"learning.*from.*professional", re.IGNORECASE)
            ]
        }
        
        return patterns
    
    @cache_manager.cached(ttl=1800)
    async def track_collaboration_entities(
        self,
        text: str,
        content_metadata: Optional[ContentMetadata] = None,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> CollaborationAnalysisResult:
        """
        Track and analyze collaboration opportunities in text
        
        Args:
            text: Input text to analyze
            content_metadata: Optional content metadata for context
            user_profile: Optional user profile for personalization
            
        Returns:
            Complete collaboration analysis results
        """
        start_time = datetime.now()
        
        try:
            # Validate input
            if not validate_input(text, str):
                raise ValueError("Invalid text input")
            
            # Preprocess text
            processed_text = TextPreprocessor.clean_text(text)
            
            # Extract collaboration entities
            entities = await self._extract_collaboration_entities(
                processed_text, content_metadata, user_profile
            )
            
            # Analyze collaboration network
            network = await self._analyze_collaboration_network(entities, text)
            
            # Generate recommendations
            recommendations = await self._generate_collaboration_recommendations(
                entities, user_profile, network
            )
            
            # Calculate metrics
            total_opportunities = len(entities)
            high_priority_count = sum(
                1 for entity in entities 
                if entity.priority in [CollaborationPriority.CRITICAL, CollaborationPriority.HIGH]
            )
            
            analysis_time = (datetime.now() - start_time).total_seconds()
            
            # Update metrics
            await self.metrics.increment("collaboration_opportunities_found", total_opportunities)
            await self.metrics.increment("high_priority_opportunities", high_priority_count)
            await self.metrics.record("analysis_time", analysis_time)
            
            result = CollaborationAnalysisResult(
                entities=entities,
                total_opportunities=total_opportunities,
                high_priority_count=high_priority_count,
                collaboration_network=network,
                recommendations=recommendations,
                analysis_time=analysis_time,
                metadata={
                    "text_length": len(text),
                    "processed_length": len(processed_text),
                    "content_type": content_metadata.content_type.value if content_metadata else None,
                    "user_id": user_profile.get("user_id") if user_profile else None
                }
            )
            
            self.logger.info(
                f"Found {total_opportunities} collaboration opportunities, "
                f"{high_priority_count} high priority"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Collaboration tracking failed: {e}")
            await self.metrics.increment("tracking_errors")
            raise
    
    async def _extract_collaboration_entities(
        self,
        text: str,
        content_metadata: Optional[ContentMetadata],
        user_profile: Optional[Dict[str, Any]]
    ) -> List[CollaborationEntity]:
        """Extract collaboration entities from text"""
        entities = []
        
        try:
            # Pattern-based extraction
            for collab_type, patterns in self._collaboration_patterns.items():
                for pattern in patterns:
                    matches = pattern.finditer(text)
                    
                    for match in matches:
                        entity = await self._create_collaboration_entity(
                            match, collab_type, text, content_metadata, user_profile
                        )
                        if entity:
                            entities.append(entity)
            
            # ML-based extraction for implicit collaborations
            ml_entities = await self._extract_implicit_collaborations(
                text, content_metadata, user_profile
            )
            entities.extend(ml_entities)
            
            # Deduplicate and refine
            entities = await self._deduplicate_collaboration_entities(entities)
            
            # Score and prioritize
            for entity in entities:
                entity.opportunity_score = await self._calculate_opportunity_score(
                    entity, user_profile
                )
                entity.priority = await self._determine_priority(entity)
            
        except Exception as e:
            self.logger.error(f"Collaboration entity extraction failed: {e}")
        
        return entities
    
    async def _create_collaboration_entity(
        self,
        match: re.Match,
        collab_type: CollaborationType,
        full_text: str,
        content_metadata: Optional[ContentMetadata],
        user_profile: Optional[Dict[str, Any]]
    ) -> Optional[CollaborationEntity]:
        """Create collaboration entity from pattern match"""
        try:
            # Extract context around match
            context_start = max(0, match.start() - 100)
            context_end = min(len(full_text), match.end() + 100)
            context = full_text[context_start:context_end]
            
            # Analyze sentiment and tone
            sentiment = await self._analyze_collaboration_sentiment(context)
            
            # Extract collaborator information
            collaborator_info = await self._extract_collaborator_info(context)
            
            # Calculate confidence
            confidence = await self._calculate_collaboration_confidence(
                match, collab_type, context, sentiment
            )
            
            # Determine initial status
            status = CollaborationStatus.DETECTED
            
            entity = CollaborationEntity(
                text=match.group(0),
                collaboration_type=collab_type,
                priority=CollaborationPriority.MEDIUM,  # Will be refined later
                status=status,
                confidence=confidence,
                start_pos=match.start(),
                end_pos=match.end(),
                collaborator_info=collaborator_info
            )
            
            # Enrich with additional metadata
            await self._enrich_collaboration_entity(entity, context, user_profile)
            
            return entity
            
        except Exception as e:
            self.logger.error(f"Failed to create collaboration entity: {e}")
            return None
    
    async def _extract_implicit_collaborations(
        self,
        text: str,
        content_metadata: Optional[ContentMetadata],
        user_profile: Optional[Dict[str, Any]]
    ) -> List[CollaborationEntity]:
        """Extract implicit collaboration opportunities using ML"""
        entities = []
        
        try:
            # Use NLP to identify entities and relationships
            doc = self.nlp(text)
            
            # Look for person entities that might be collaborators
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "ORG"]:
                    # Analyze context for collaboration indicators
                    context = text[max(0, ent.start_char - 50):ent.end_char + 50]
                    
                    # Use transformer model to classify collaboration likelihood
                    classification = await self._classify_collaboration_context(context)
                    
                    if classification["score"] > 0.6:  # Threshold for implicit collaboration
                        entity = CollaborationEntity(
                            text=ent.text,
                            collaboration_type=self._map_classification_to_type(
                                classification["label"]
                            ),
                            priority=CollaborationPriority.MEDIUM,
                            status=CollaborationStatus.DETECTED,
                            confidence=classification["score"],
                            start_pos=ent.start_char,
                            end_pos=ent.end_char,
                            collaborator_info={"name": ent.text, "type": ent.label_}
                        )
                        
                        entities.append(entity)
            
            # Analyze sentence structure for collaboration patterns
            for sent in doc.sents:
                # Look for specific grammatical patterns indicating collaboration
                patterns = await self._analyze_grammatical_collaboration_patterns(sent)
                entities.extend(patterns)
            
        except Exception as e:
            self.logger.error(f"Implicit collaboration extraction failed: {e}")
        
        return entities
    
    async def _analyze_collaboration_sentiment(self, context: str) -> Dict[str, Any]:
        """Analyze sentiment of collaboration context"""
        try:
            result = self.sentiment_analyzer(context)
            return {
                "label": result[0]["label"],
                "score": result[0]["score"],
                "is_positive": result[0]["label"] in ["POSITIVE", "LABEL_2"]
            }
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            return {"label": "NEUTRAL", "score": 0.5, "is_positive": True}
    
    async def _extract_collaborator_info(self, context: str) -> Dict[str, Any]:
        """Extract information about potential collaborators"""
        info = {}
        
        try:
            doc = self.nlp(context)
            
            # Extract person names
            persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
            if persons:
                info["potential_collaborators"] = persons
            
            # Extract organizations
            orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
            if orgs:
                info["organizations"] = orgs
            
            # Extract skills/genres mentioned
            skills = await self._extract_skills_and_genres(context)
            if skills:
                info["required_skills"] = skills
            
            # Extract contact information
            contact = await self._extract_contact_information(context)
            if contact:
                info["contact"] = contact
            
            # Extract location information
            locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
            if locations:
                info["locations"] = locations
            
        except Exception as e:
            self.logger.error(f"Collaborator info extraction failed: {e}")
        
        return info
    
    async def _extract_skills_and_genres(self, context: str) -> List[str]:
        """Extract skills and genres from context"""
        skills = []
        
        # Music genres
        music_genres = [
            "pop", "rock", "hip hop", "rap", "r&b", "jazz", "classical", "electronic",
            "dance", "house", "techno", "dubstep", "reggae", "country", "folk",
            "indie", "alternative", "metal", "punk", "blues", "soul", "funk"
        ]
        
        # Skills and instruments
        skills_keywords = [
            "guitar", "piano", "drums", "vocals", "singing", "producer", "mixing",
            "mastering", "songwriter", "composer", "beatmaker", "dj", "rapper",
            "photography", "videography", "editing", "animation", "design"
        ]
        
        context_lower = context.lower()
        
        for genre in music_genres:
            if genre in context_lower:
                skills.append(genre)
        
        for skill in skills_keywords:
            if skill in context_lower:
                skills.append(skill)
        
        return skills
    
    async def _extract_contact_information(self, context: str) -> Dict[str, str]:
        """Extract contact information from context"""
        contact = {}
        
        # Email pattern
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        emails = email_pattern.findall(context)
        if emails:
            contact["email"] = emails[0]
        
        # Phone pattern
        phone_pattern = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
        phones = phone_pattern.findall(context)
        if phones:
            contact["phone"] = phones[0]
        
        # Social media handles
        handle_pattern = re.compile(r'@[a-zA-Z0-9_.]+')
        handles = handle_pattern.findall(context)
        if handles:
            contact["social_handles"] = handles
        
        return contact
    
    async def _calculate_collaboration_confidence(
        self,
        match: re.Match,
        collab_type: CollaborationType,
        context: str,
        sentiment: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for collaboration entity"""
        base_confidence = 0.6
        
        # Type-specific confidence adjustments
        type_weights = {
            CollaborationType.MUSIC_COLLABORATION: 0.8,
            CollaborationType.BRAND_PARTNERSHIP: 0.9,
            CollaborationType.CONTENT_COLLABORATION: 0.7,
            CollaborationType.SPONSORSHIP: 0.85
        }
        
        confidence = type_weights.get(collab_type, base_confidence)
        
        # Sentiment adjustment
        if sentiment["is_positive"]:
            confidence += 0.1 * sentiment["score"]
        else:
            confidence -= 0.05 * sentiment["score"]
        
        # Context quality adjustment
        if len(context) > 50:
            confidence += 0.05
        
        # Specific keywords boost
        high_confidence_keywords = [
            "collaboration", "partnership", "looking for", "seeking", "need",
            "hiring", "opportunity", "project", "work together"
        ]
        
        keyword_count = sum(1 for keyword in high_confidence_keywords if keyword in context.lower())
        confidence += min(0.15, keyword_count * 0.03)
        
        return min(0.95, max(0.1, confidence))
    
    async def _enrich_collaboration_entity(
        self,
        entity: CollaborationEntity,
        context: str,
        user_profile: Optional[Dict[str, Any]]
    ):
        """Enrich collaboration entity with additional metadata"""
        try:
            # Calculate compatibility score
            if user_profile:
                entity.compatibility_score = await self._calculate_compatibility_score(
                    entity, user_profile
                )
            
            # Extract requirements and benefits
            entity.requirements = await self._extract_requirements(context)
            entity.benefits = await self._extract_benefits(context)
            entity.risks = await self._extract_risks(context)
            
            # Estimate reach and impact
            entity.estimated_reach = await self._estimate_collaboration_reach(entity)
            
            # Set expiration if time-sensitive
            entity.expires_at = await self._calculate_expiration_date(entity, context)
            
            # Extract location information
            entity.location_info = await self._extract_location_context(context)
            
        except Exception as e:
            self.logger.error(f"Entity enrichment failed: {e}")
    
    async def _calculate_compatibility_score(
        self,
        entity: CollaborationEntity,
        user_profile: Dict[str, Any]
    ) -> float:
        """Calculate compatibility score between user and collaboration opportunity"""
        score = 0.5  # Base score
        
        try:
            user_genres = user_profile.get("genres", [])
            user_skills = user_profile.get("skills", [])
            user_location = user_profile.get("location", "")
            
            # Genre overlap
            entity_skills = entity.collaborator_info.get("required_skills", [])
            if user_genres and entity_skills:
                overlap = len(set(user_genres) & set(entity_skills))
                score += min(0.3, overlap * 0.1)
            
            # Skill match
            if user_skills and entity_skills:
                skill_overlap = len(set(user_skills) & set(entity_skills))
                score += min(0.2, skill_overlap * 0.05)
            
            # Location proximity
            entity_locations = entity.collaborator_info.get("locations", [])
            if user_location and entity_locations:
                # Simple string matching (could be enhanced with geolocation)
                if any(user_location.lower() in loc.lower() for loc in entity_locations):
                    score += 0.15
            
            # Collaboration type preference
            user_preferences = user_profile.get("collaboration_preferences", [])
            if entity.collaboration_type.value in user_preferences:
                score += 0.2
            
        except Exception as e:
            self.logger.error(f"Compatibility calculation failed: {e}")
        
        return min(1.0, max(0.0, score))
    
    async def _extract_requirements(self, context: str) -> List[str]:
        """Extract requirements from collaboration context"""
        requirements = []
        
        # Common requirement patterns
        requirement_patterns = [
            r"must have (.+?)(?:\.|,|;|$)",
            r"require(?:s|d) (.+?)(?:\.|,|;|$)",
            r"need(?:s|ed) (.+?)(?:\.|,|;|$)",
            r"looking for (.+?)(?:\.|,|;|$)"
        ]
        
        for pattern in requirement_patterns:
            matches = re.finditer(pattern, context, re.IGNORECASE)
            for match in matches:
                requirement = match.group(1).strip()
                if len(requirement) > 3 and len(requirement) < 100:
                    requirements.append(requirement)
        
        return requirements
    
    async def _extract_benefits(self, context: str) -> List[str]:
        """Extract benefits from collaboration context"""
        benefits = []
        
        # Common benefit patterns
        benefit_patterns = [
            r"benefit(?:s)? (.+?)(?:\.|,|;|$)",
            r"gain (.+?)(?:\.|,|;|$)",
            r"get (.+?)(?:\.|,|;|$)",
            r"receive (.+?)(?:\.|,|;|$)",
            r"opportunity to (.+?)(?:\.|,|;|$)"
        ]
        
        for pattern in benefit_patterns:
            matches = re.finditer(pattern, context, re.IGNORECASE)
            for match in matches:
                benefit = match.group(1).strip()
                if len(benefit) > 3 and len(benefit) < 100:
                    benefits.append(benefit)
        
        return benefits
    
    async def _extract_risks(self, context: str) -> List[str]:
        """Extract potential risks from collaboration context"""
        risks = []
        
        # Risk indicators
        risk_keywords = [
            "unpaid", "no payment", "free", "spec work", "test project",
            "might not", "unclear", "vague", "no contract", "no guarantee"
        ]
        
        context_lower = context.lower()
        for keyword in risk_keywords:
            if keyword in context_lower:
                risks.append(f"Potential risk: {keyword}")
        
        # Check for missing information
        if "contact" not in context_lower and "@" not in context:
            risks.append("No clear contact information provided")
        
        if len(context) < 50:
            risks.append("Limited information provided")
        
        return risks
    
    async def _analyze_collaboration_network(
        self,
        entities: List[CollaborationEntity],
        text: str
    ) -> CollaborationNetwork:
        """Analyze collaboration network and relationships"""
        try:
            # Create network graph
            G = nx.Graph()
            
            # Add nodes (collaborators)
            nodes = set()
            for entity in entities:
                collaborators = entity.collaborator_info.get("potential_collaborators", [])
                nodes.update(collaborators)
                
                # Add current user as a node
                nodes.add("current_user")
            
            G.add_nodes_from(nodes)
            
            # Add edges (collaboration relationships)
            edges = []
            for entity in entities:
                collaborators = entity.collaborator_info.get("potential_collaborators", [])
                for collaborator in collaborators:
                    edge_weight = entity.opportunity_score
                    edges.append(("current_user", collaborator, edge_weight))
                    G.add_edge("current_user", collaborator, weight=edge_weight)
            
            # Perform network analysis
            clusters = list(nx.connected_components(G))
            
            # Calculate centrality measures
            try:
                centrality = nx.degree_centrality(G)
                central_nodes = sorted(centrality.keys(), key=lambda x: centrality[x], reverse=True)[:5]
            except:
                central_nodes = list(nodes)[:5]
            
            # Calculate shortest paths
            collaboration_paths = {}
            try:
                for node in nodes:
                    if node != "current_user" and G.has_node(node):
                        try:
                            path = nx.shortest_path(G, "current_user", node)
                            collaboration_paths[node] = path
                        except nx.NetworkXNoPath:
                            collaboration_paths[node] = []
            except:
                pass
            
            # Calculate network metrics
            network_metrics = {}
            try:
                network_metrics["density"] = nx.density(G)
                network_metrics["connected_components"] = nx.number_connected_components(G)
                network_metrics["average_clustering"] = nx.average_clustering(G)
            except:
                network_metrics = {"density": 0, "connected_components": 0, "average_clustering": 0}
            
            # Calculate influence scores
            influence_scores = {}
            for node in nodes:
                # Simple influence score based on connections and collaboration types
                score = 0
                for entity in entities:
                    if node in entity.collaborator_info.get("potential_collaborators", []):
                        score += entity.opportunity_score
                influence_scores[node] = score
            
            return CollaborationNetwork(
                nodes=list(nodes),
                edges=edges,
                clusters=[list(cluster) for cluster in clusters],
                central_nodes=central_nodes,
                collaboration_paths=collaboration_paths,
                network_metrics=network_metrics,
                influence_scores=influence_scores
            )
            
        except Exception as e:
            self.logger.error(f"Network analysis failed: {e}")
            return CollaborationNetwork(
                nodes=[],
                edges=[],
                clusters=[],
                central_nodes=[],
                collaboration_paths={},
                network_metrics={},
                influence_scores={}
            )
    
    async def _generate_collaboration_recommendations(
        self,
        entities: List[CollaborationEntity],
        user_profile: Optional[Dict[str, Any]],
        network: CollaborationNetwork
    ) -> List[Dict[str, Any]]:
        """Generate strategic collaboration recommendations"""
        recommendations = []
        
        try:
            # High-priority opportunities
            high_priority_entities = [
                e for e in entities 
                if e.priority in [CollaborationPriority.CRITICAL, CollaborationPriority.HIGH]
            ]
            
            if high_priority_entities:
                recommendations.append({
                    "type": "immediate_action",
                    "title": "High-Priority Opportunities",
                    "description": f"Act on {len(high_priority_entities)} high-priority collaborations",
                    "entities": [e.text for e in high_priority_entities[:3]],
                    "urgency": "high"
                })
            
            # Network expansion recommendations
            if network.central_nodes:
                recommendations.append({
                    "type": "network_expansion",
                    "title": "Key Network Connections",
                    "description": f"Focus on connecting with {network.central_nodes[0]}",
                    "entities": network.central_nodes[:3],
                    "urgency": "medium"
                })
            
            # Genre-specific recommendations
            if user_profile:
                user_genres = user_profile.get("genres", [])
                matching_entities = [
                    e for e in entities
                    if any(genre in e.collaborator_info.get("required_skills", []) for genre in user_genres)
                ]
                
                if matching_entities:
                    recommendations.append({
                        "type": "genre_match",
                        "title": "Genre-Matched Collaborations",
                        "description": f"Perfect genre matches for your {', '.join(user_genres[:2])} style",
                        "entities": [e.text for e in matching_entities[:3]],
                        "urgency": "medium"
                    })
            
            # Time-sensitive opportunities
            time_sensitive = [
                e for e in entities 
                if e.expires_at and e.expires_at < datetime.now() + timedelta(days=7)
            ]
            
            if time_sensitive:
                recommendations.append({
                    "type": "time_sensitive",
                    "title": "Expiring Opportunities",
                    "description": f"{len(time_sensitive)} opportunities expiring soon",
                    "entities": [e.text for e in time_sensitive],
                    "urgency": "critical"
                })
            
            # Brand partnership opportunities
            brand_entities = [
                e for e in entities 
                if e.collaboration_type == CollaborationType.BRAND_PARTNERSHIP
            ]
            
            if brand_entities:
                recommendations.append({
                    "type": "monetization",
                    "title": "Brand Partnership Opportunities",
                    "description": f"Monetize with {len(brand_entities)} brand partnerships",
                    "entities": [e.text for e in brand_entities[:3]],
                    "urgency": "medium"
                })
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
        
        return recommendations
    
    async def _deduplicate_collaboration_entities(
        self, 
        entities: List[CollaborationEntity]
    ) -> List[CollaborationEntity]:
        """Remove duplicate collaboration entities"""
        if not entities:
            return []
        
        # Group by text similarity
        entity_groups = {}
        for entity in entities:
            key = entity.text.lower().strip()
            if key not in entity_groups:
                entity_groups[key] = []
            entity_groups[key].append(entity)
        
        unique_entities = []
        
        for group in entity_groups.values():
            if len(group) == 1:
                unique_entities.append(group[0])
            else:
                # Merge similar entities
                best_entity = max(group, key=lambda e: e.confidence)
                
                # Merge collaborator info
                for other in group:
                    if other != best_entity:
                        for key, value in other.collaborator_info.items():
                            if key not in best_entity.collaborator_info:
                                best_entity.collaborator_info[key] = value
                            elif isinstance(value, list):
                                best_entity.collaborator_info[key].extend(value)
                
                unique_entities.append(best_entity)
        
        return unique_entities
    
    async def _calculate_opportunity_score(
        self,
        entity: CollaborationEntity,
        user_profile: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate overall opportunity score"""
        score = entity.confidence * 0.4  # Base confidence weight
        
        # Add compatibility score
        score += entity.compatibility_score * 0.3
        
        # Collaboration type impact
        type_weights = {
            CollaborationType.BRAND_PARTNERSHIP: 0.9,
            CollaborationType.SPONSORSHIP: 0.85,
            CollaborationType.MUSIC_COLLABORATION: 0.8,
            CollaborationType.CONTENT_COLLABORATION: 0.75
        }
        
        type_weight = type_weights.get(entity.collaboration_type, 0.6)
        score += type_weight * 0.2
        
        # Risk adjustment
        risk_penalty = len(entity.risks) * 0.05
        score -= risk_penalty
        
        # Benefit bonus
        benefit_bonus = min(0.1, len(entity.benefits) * 0.02)
        score += benefit_bonus
        
        return min(1.0, max(0.0, score))
    
    async def _determine_priority(self, entity: CollaborationEntity) -> CollaborationPriority:
        """Determine priority level for collaboration entity"""
        score = entity.opportunity_score
        
        # Time-sensitive boost
        if entity.expires_at and entity.expires_at < datetime.now() + timedelta(days=3):
            score += 0.2
        
        # Brand partnership boost
        if entity.collaboration_type in [CollaborationType.BRAND_PARTNERSHIP, CollaborationType.SPONSORSHIP]:
            score += 0.15
        
        # High compatibility boost
        if entity.compatibility_score > 0.8:
            score += 0.1
        
        if score >= 0.85:
            return CollaborationPriority.CRITICAL
        elif score >= 0.7:
            return CollaborationPriority.HIGH
        elif score >= 0.5:
            return CollaborationPriority.MEDIUM
        else:
            return CollaborationPriority.LOW
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health status"""
        return {
            "status": "healthy" if self.models_loaded else "degraded",
            "models_loaded": self.models_loaded,
            "collaboration_types_supported": len(self._collaboration_patterns),
            "cache_enabled": bool(self.cache_ttl),
            "timestamp": datetime.now().isoformat()
        }
