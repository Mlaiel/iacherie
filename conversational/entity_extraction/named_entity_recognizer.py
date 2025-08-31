"""Named Entity Recognizer - Advanced NER Engine

Specialized named entity recognition for creative industry content with
multi-model ensemble, domain adaptation, and real-time processing capabilities.
Optimized for musicians, influencers, content creators, and creative professionals.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""import asyncio
import pickle
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
import json

import numpy as np
import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer, AutoModelForTokenClassification, 
    BertTokenizer, BertForTokenClassification,
    pipeline, Trainer, TrainingArguments
)
from sklearn.metrics import classification_report, confusion_matrix
import spacy
from spacy.training import Example
from spacy.tokens import DocBin

from ...core.base_service import BaseService
from ...core.cache import cache_manager
from ...core.monitoring import MetricsCollector
from ...models.entities import EntityType, NERResult, TrainingExample
from ...utils.text_processors import TextPreprocessor
from ...utils.model_utils import ModelManager
from .entity_extractor import EntityCategory, ExtractedEntity


class NERModelType(Enum):
    """Types of NER models available"""    BERT_BASE = "bert_base"
    BERT_CREATIVE = "bert_creative"
    SPACY_CUSTOM = "spacy_custom"
    TRANSFORMER_ENSEMBLE = "transformer_ensemble"
    HYBRID_MODEL = "hybrid_model"


class LanguageSupport(Enum):
    """Supported languages for NER"""    ENGLISH = "en"
    GERMAN = "de"
    FRENCH = "fr"
    SPANISH = "es"
    MULTILINGUAL = "multi"


@dataclass
class NERPrediction:
    """Single NER prediction with confidence and metadata"""    token: str
    label: str
    confidence: float
    start_pos: int
    end_pos: int
    model_source: str
    language: str = "en"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NERModelMetrics:
    """Performance metrics for NER model"""    precision: float
    recall: float
    f1_score: float
    accuracy: float
    training_time: float
    inference_time: float
    model_size: int
    entity_type_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)


class NamedEntityRecognizer(BaseService):
    """    Advanced Named Entity Recognition engine with creative industry specialization.
    
    Features:
    - Multi-model ensemble for maximum accuracy
    - Domain-specific fine-tuning for creative content
    - Real-time inference with GPU acceleration
    - Multi-language support
    - Custom entity type training
    - Active learning for continuous improvement
    - Model performance monitoring and A/B testing
    """    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("named_entity_recognizer")
        self.text_processor = TextPreprocessor()
        self.model_manager = ModelManager()
        
        # Model configurations
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        self.model_configs = {}
        
        # Performance tracking
        self.model_metrics = {}
        self.prediction_cache = {}
        
        # Training configurations
        self.training_config = {
            'batch_size': 16,
            'learning_rate': 2e-5,
            'num_epochs': 3,
            'max_length': 512,
            'warmup_steps': 100
        }
        
        # Creative industry entity labels
        self.creative_labels = self._initialize_creative_labels()
        
        # Language-specific models
        self.language_models = {}
        
    async def initialize(self):
        """Initialize all NER models and resources"""        try:
            self.logger.info("Initializing NamedEntityRecognizer...")
            
            # Load pre-trained models
            await self._load_pretrained_models()
            
            # Load custom creative industry models
            await self._load_custom_models()
            
    async def _initialize_ensemble(self):
        """Initialize ensemble of NER models for maximum accuracy"""        try:
            self.ensemble_models = {}
            self.model_weights = {}
            
            # Load primary BERT model for creative content
            await self._load_bert_creative_model()
            
            # Load spaCy custom model
            await self._load_spacy_custom_model()
            
            # Load transformer ensemble
            await self._load_transformer_ensemble()
            
            # Load hybrid model combining multiple approaches
            await self._load_hybrid_model()
            
            # Initialize ensemble weights based on validation performance
            self.model_weights = {
                NERModelType.BERT_CREATIVE: 0.35,
                NERModelType.SPACY_CUSTOM: 0.25,
                NERModelType.TRANSFORMER_ENSEMBLE: 0.30,
                NERModelType.HYBRID_MODEL: 0.10
            }
            
            self.logger.info("NER ensemble models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ensemble: {str(e)}")
            raise
    
    async def _load_bert_creative_model(self):
        """Load fine-tuned BERT model for creative industry entities"""        try:
            model_name = "bert-base-multilingual-cased"
            
            # Load pre-trained tokenizer and model
            self.creative_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.creative_model = AutoModelForTokenClassification.from_pretrained(
                model_name,
                num_labels=len(self._get_all_labels()),
                problem_type="token_classification"
            )
            
            # Load fine-tuned weights if available
            creative_model_path = self.config.get('creative_model_path')
            if creative_model_path:
                try:
                    state_dict = torch.load(creative_model_path, map_location=self.device)
                    self.creative_model.load_state_dict(state_dict)
                    self.logger.info("Loaded fine-tuned creative industry model")
                except Exception as e:
                    self.logger.warning(f"Could not load fine-tuned model: {e}")
            
            # Move to appropriate device
            self.creative_model.to(self.device)
            self.creative_model.eval()
            
            # Create pipeline for easy inference
            self.creative_pipeline = pipeline(
                "token-classification",
                model=self.creative_model,
                tokenizer=self.creative_tokenizer,
                aggregation_strategy="first",
                device=0 if self.device.type == 'cuda' else -1
            )
            
            self.ensemble_models[NERModelType.BERT_CREATIVE] = {
                'model': self.creative_model,
                'tokenizer': self.creative_tokenizer,
                'pipeline': self.creative_pipeline
            }
            
        except Exception as e:
            self.logger.error(f"Failed to load BERT creative model: {str(e)}")
            raise
    
    async def _load_spacy_custom_model(self):
        """Load custom spaCy model trained on creative content"""        try:
            # Load base spaCy model
            try:
                self.spacy_model = spacy.load("en_core_web_trf")
            except OSError:
                # Fallback to smaller model if transformer not available
                self.spacy_model = spacy.load("en_core_web_sm")
                self.logger.warning("Using smaller spaCy model as fallback")
            
            # Add custom NER component for creative entities
            if "creative_ner" not in self.spacy_model.pipe_names:
                creative_ner = self.spacy_model.add_pipe(
                    "ner", 
                    name="creative_ner",
                    after="ner"
                )
                
                # Add creative industry labels
                for category_labels in self.creative_labels.values():
                    for label in category_labels:
                        if label.startswith('B-') or label.startswith('I-'):
                            creative_ner.add_label(label[2:])  # Remove BIO prefix
            
            # Load custom training data if available
            custom_model_path = self.config.get('spacy_custom_model_path')
            if custom_model_path:
                try:
                    self.spacy_model = spacy.load(custom_model_path)
                    self.logger.info("Loaded custom spaCy model")
                except Exception as e:
                    self.logger.warning(f"Could not load custom spaCy model: {e}")
            
            self.ensemble_models[NERModelType.SPACY_CUSTOM] = {
                'model': self.spacy_model
            }
            
        except Exception as e:
            self.logger.error(f"Failed to load spaCy custom model: {str(e)}")
            raise
    
    async def _load_transformer_ensemble(self):
        """Load ensemble of transformer models for enhanced accuracy"""        try:
            self.transformer_models = []
            
            # Load multiple transformer models for ensemble
            model_configs = [
                ("distilbert-base-multilingual-cased", "distilbert"),
                ("microsoft/DialoGPT-medium", "dialogpt"),
                ("facebook/bart-base", "bart")
            ]
            
            for model_name, model_type in model_configs:
                try:
                    tokenizer = AutoTokenizer.from_pretrained(model_name)
                    model = AutoModelForTokenClassification.from_pretrained(
                        model_name,
                        num_labels=len(self._get_all_labels()),
                        ignore_mismatched_sizes=True
                    )
                    
                    model.to(self.device)
                    model.eval()
                    
                    pipeline_model = pipeline(
                        "token-classification",
                        model=model,
                        tokenizer=tokenizer,
                        aggregation_strategy="first",
                        device=0 if self.device.type == 'cuda' else -1
                    )
                    
                    self.transformer_models.append({
                        'name': model_type,
                        'model': model,
                        'tokenizer': tokenizer,
                        'pipeline': pipeline_model
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Could not load {model_name}: {e}")
                    continue
            
            self.ensemble_models[NERModelType.TRANSFORMER_ENSEMBLE] = {
                'models': self.transformer_models
            }
            
            self.logger.info(f"Loaded {len(self.transformer_models)} transformer models")
            
        except Exception as e:
            self.logger.error(f"Failed to load transformer ensemble: {str(e)}")
            raise
    
    async def _load_hybrid_model(self):
        """Load hybrid model combining rule-based and ML approaches"""        try:
            # Initialize rule-based patterns for creative entities
            self.creative_patterns = self._create_creative_patterns()
            
            # Initialize regex patterns for handles, hashtags, etc.
            self.regex_patterns = self._create_regex_patterns()
            
            # Initialize gazetteer for known entities
            self.gazetteers = await self._load_gazetteers()
            
            # Initialize custom neural architecture for hybrid processing
            self.hybrid_neural_net = self._create_hybrid_neural_network()
            
            self.ensemble_models[NERModelType.HYBRID_MODEL] = {
                'patterns': self.creative_patterns,
                'regex': self.regex_patterns,
                'gazetteers': self.gazetteers,
                'neural_net': self.hybrid_neural_net
            }
            
        except Exception as e:
            self.logger.error(f"Failed to load hybrid model: {str(e)}")
            raise
    
    def _create_creative_patterns(self) -> Dict[str, List[Dict]]:
        """Create rule-based patterns for creative entity recognition"""        return {
            'music_patterns': [
                {'pattern': [{'LOWER': 'ft'}, {'LOWER': '.'}, {'ENT_TYPE': 'PERSON'}], 'label': 'ARTIST'},
                {'pattern': [{'LOWER': 'featuring'}, {'ENT_TYPE': 'PERSON'}], 'label': 'ARTIST'},
                {'pattern': [{'LOWER': 'remix'}, {'LOWER': 'by'}, {'ENT_TYPE': 'PERSON'}], 'label': 'ARTIST'},
                {'pattern': [{'LOWER': 'produced'}, {'LOWER': 'by'}, {'ENT_TYPE': 'PERSON'}], 'label': 'PRODUCER'},
                {'pattern': [{'SHAPE': 'Xxxx'}, {'LOWER': 'records'}], 'label': 'LABEL'},
                {'pattern': [{'SHAPE': 'Xxxx'}, {'LOWER': 'music'}], 'label': 'LABEL'}
            ],
            'platform_patterns': [
                {'pattern': [{'LOWER': '@'}, {'IS_ALPHA': True}], 'label': 'HANDLE'},
                {'pattern': [{'LOWER': '#'}, {'IS_ALPHA': True}], 'label': 'HASHTAG'},
                {'pattern': [{'LOWER': 'youtube'}, {'LOWER': 'channel'}], 'label': 'PLATFORM'},
                {'pattern': [{'LOWER': 'instagram'}, {'LOWER': 'page'}], 'label': 'PLATFORM'},
                {'pattern': [{'LOWER': 'tiktok'}, {'LOWER': 'account'}], 'label': 'PLATFORM'},
                {'pattern': [{'LOWER': 'spotify'}, {'LOWER': 'playlist'}], 'label': 'PLATFORM'}
            ],
            'business_patterns': [
                {'pattern': [{'LIKE_NUM': True}, {'LOWER': 'streams'}], 'label': 'METRIC'},
                {'pattern': [{'LIKE_NUM': True}, {'LOWER': 'views'}], 'label': 'METRIC'},
                {'pattern': [{'LIKE_NUM': True}, {'LOWER': 'followers'}], 'label': 'METRIC'},
                {'pattern': [{'LOWER': '$'}, {'LIKE_NUM': True}], 'label': 'REVENUE'},
                {'pattern': [{'LIKE_NUM': True}, {'LOWER': 'million'}, {'LOWER': 'streams'}], 'label': 'METRIC'}
            ]
        }
    
    def _create_regex_patterns(self) -> Dict[str, str]:
        """Create regex patterns for entity extraction"""        import re
        return {
            'social_handle': r'@[a-zA-Z0-9_]{1,50}',
            'hashtag': r'#[a-zA-Z0-9_]{1,100}',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'url': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            'phone': r'(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            'revenue': r'\$[\d,]+(\.\d{2})?[KMB]?',
            'percentage': r'\d+(\.\d+)?%',
            'year': r'\b(19|20)\d{2}\b',
            'time_duration': r'\d{1,2}:\d{2}(:\d{2})?',
            'file_extension': r'\.[a-zA-Z0-9]{2,4}$'
        }
    
    async def _load_gazetteers(self) -> Dict[str, Set[str]]:
        """Load gazetteer lists for known entities"""        gazetteers = {
            'music_genres': set([
                'rock', 'pop', 'hip-hop', 'jazz', 'classical', 'electronic', 'country',
                'r&b', 'soul', 'funk', 'reggae', 'blues', 'folk', 'indie', 'alternative',
                'metal', 'punk', 'disco', 'house', 'techno', 'trance', 'dubstep', 'trap',
                'ambient', 'experimental', 'lo-fi', 'drill', 'phonk', 'afrobeat', 'reggaeton'
            ]),
            'instruments': set([
                'guitar', 'piano', 'drums', 'bass', 'violin', 'saxophone', 'trumpet',
                'flute', 'clarinet', 'cello', 'viola', 'harp', 'banjo', 'mandolin',
                'synthesizer', 'keyboard', 'microphone', 'turntables', 'sampler'
            ]),
            'platforms': set([
                'youtube', 'instagram', 'tiktok', 'spotify', 'soundcloud', 'bandcamp',
                'apple music', 'deezer', 'tidal', 'amazon music', 'facebook', 'twitter',
                'linkedin', 'snapchat', 'twitch', 'discord', 'telegram', 'whatsapp'
            ]),
            'music_labels': set([
                'universal music group', 'sony music', 'warner music group',
                'atlantic records', 'columbia records', 'capitol records', 'def jam',
                'interscope', 'republic records', 'rca records', 'epic records'
            ]),
            'social_media_metrics': set([
                'views', 'likes', 'comments', 'shares', 'followers', 'subscribers',
                'impressions', 'reach', 'engagement', 'clicks', 'saves', 'downloads'
            ])
        }
        
        # Load additional gazetteers from external sources if configured
        gazetteer_sources = self.config.get('gazetteer_sources', {})
        for category, source_path in gazetteer_sources.items():
            try:
                with open(source_path, 'r', encoding='utf-8') as f:
                    additional_terms = set(line.strip().lower() for line in f)
                    gazetteers[category].update(additional_terms)
            except Exception as e:
                self.logger.warning(f"Could not load gazetteer {category}: {e}")
        
        return gazetteers
    
    def _create_hybrid_neural_network(self) -> nn.Module:
        """Create custom neural network for hybrid NER processing"""        class HybridNERNetwork(nn.Module):
            def __init__(self, vocab_size, embedding_dim, hidden_dim, num_labels):
                super(HybridNERNetwork, self).__init__()
                self.embedding = nn.Embedding(vocab_size, embedding_dim)
                self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True, bidirectional=True)
                self.dropout = nn.Dropout(0.3)
                self.classifier = nn.Linear(hidden_dim * 2, num_labels)
                
            def forward(self, input_ids, attention_mask=None):
                embeddings = self.embedding(input_ids)
                lstm_out, _ = self.lstm(embeddings)
                lstm_out = self.dropout(lstm_out)
                logits = self.classifier(lstm_out)
                return logits
        
        # Initialize network parameters
        vocab_size = self.config.get('hybrid_vocab_size', 50000)
        embedding_dim = self.config.get('hybrid_embedding_dim', 256)
        hidden_dim = self.config.get('hybrid_hidden_dim', 512)
        num_labels = len(self._get_all_labels())
        
        network = HybridNERNetwork(vocab_size, embedding_dim, hidden_dim, num_labels)
        network.to(self.device)
        
        # Load pre-trained weights if available
        hybrid_weights_path = self.config.get('hybrid_weights_path')
        if hybrid_weights_path:
            try:
                network.load_state_dict(torch.load(hybrid_weights_path, map_location=self.device))
                self.logger.info("Loaded pre-trained hybrid neural network weights")
            except Exception as e:
                self.logger.warning(f"Could not load hybrid weights: {e}")
        
        return network
    
    def _initialize_creative_labels(self) -> Dict[str, List[str]]:
        """Initialize entity labels specific to creative industries"""        return {
            'music': [
                'B-ARTIST', 'I-ARTIST',          # Musical artists
                'B-SONG', 'I-SONG',              # Song titles
                'B-ALBUM', 'I-ALBUM',            # Album titles
                'B-GENRE', 'I-GENRE',            # Music genres
                'B-INSTRUMENT', 'I-INSTRUMENT',  # Musical instruments
                'B-LABEL', 'I-LABEL',            # Record labels
                'B-VENUE', 'I-VENUE',            # Performance venues
                'B-FESTIVAL', 'I-FESTIVAL'       # Music festivals
            ],
            'content': [
                'B-PLATFORM', 'I-PLATFORM',      # Social media platforms
                'B-HASHTAG', 'I-HASHTAG',        # Hashtags
                'B-HANDLE', 'I-HANDLE',          # Social media handles
                'B-BRAND', 'I-BRAND',            # Brand names
                'B-PRODUCT', 'I-PRODUCT',        # Products
                'B-CAMPAIGN', 'I-CAMPAIGN'       # Marketing campaigns
            ],
            'business': [
                'B-REVENUE', 'I-REVENUE',        # Revenue figures
                'B-CONTRACT', 'I-CONTRACT',      # Contract types
                'B-LICENSING', 'I-LICENSING',    # Licensing terms
                'B-ROYALTY', 'I-ROYALTY',        # Royalty information
                'B-PARTNERSHIP', 'I-PARTNERSHIP' # Business partnerships
            ],
            'technical': [
                'B-SOFTWARE', 'I-SOFTWARE',      # Software tools
                'B-FORMAT', 'I-FORMAT',          # File formats
                'B-CODEC', 'I-CODEC',            # Audio/video codecs
                'B-METADATA', 'I-METADATA'       # Technical metadata
            ]
        }
    
    async def _load_pretrained_models(self):
        """Load pre-trained NER models"""        model_configs = {
            'bert_base_ner': {
                'model_name': 'dbmdz/bert-large-cased-finetuned-conll03-english',
                'type': NERModelType.BERT_BASE,
                'language': LanguageSupport.ENGLISH
            },
            'bert_creative_ner': {
                'model_name': 'microsoft/DialoGPT-medium',
                'type': NERModelType.BERT_CREATIVE,
                'language': LanguageSupport.ENGLISH
            },
            'multilingual_ner': {
                'model_name': 'xlm-roberta-large-finetuned-conll03-english',
                'type': NERModelType.TRANSFORMER_ENSEMBLE,
                'language': LanguageSupport.MULTILINGUAL
            }
        }
        
        for model_id, config in model_configs.items():
            try:
                self.logger.info(f"Loading model: {model_id}")
                
                # Load tokenizer
                tokenizer = AutoTokenizer.from_pretrained(config['model_name'])
                self.tokenizers[model_id] = tokenizer
                
                # Load model
                model = AutoModelForTokenClassification.from_pretrained(config['model_name'])
                self.models[model_id] = model
                
                # Create pipeline
                pipeline_obj = pipeline(
                    "ner",
                    model=model,
                    tokenizer=tokenizer,
                    aggregation_strategy="simple",
                    device=0 if torch.cuda.is_available() else -1
                )
                self.pipelines[model_id] = pipeline_obj
                
                # Store configuration
                self.model_configs[model_id] = config
                
                self.logger.info(f"Successfully loaded model: {model_id}")
                
            except Exception as e:
                self.logger.warning(f"Failed to load model {model_id}: {str(e)}")
    
    async def _load_custom_models(self):
        """Load custom fine-tuned models for creative industry"""        custom_model_paths = {
            'music_specialist': '/models/ner/music_specialist',
            'influencer_specialist': '/models/ner/influencer_specialist',
            'business_specialist': '/models/ner/business_specialist'
        }
        
        for model_id, model_path in custom_model_paths.items():
            try:
                if await self.model_manager.model_exists(model_path):
                    model_data = await self.model_manager.load_model(model_path)
                    self.models[model_id] = model_data['model']
                    self.tokenizers[model_id] = model_data['tokenizer']
                    self.model_configs[model_id] = model_data['config']
                    
                    # Create pipeline for custom model
                    pipeline_obj = pipeline(
                        "ner",
                        model=self.models[model_id],
                        tokenizer=self.tokenizers[model_id],
                        aggregation_strategy="simple"
                    )
                    self.pipelines[model_id] = pipeline_obj
                    
                    self.logger.info(f"Loaded custom model: {model_id}")
                else:
                    self.logger.info(f"Custom model not found: {model_path}")
                    
            except Exception as e:
                self.logger.warning(f"Failed to load custom model {model_id}: {str(e)}")
    
    async def _initialize_ensemble(self):
        """Initialize ensemble model combining multiple NER models"""        try:
            # Create ensemble pipeline that combines predictions from multiple models
            ensemble_models = [
                model_id for model_id in self.pipelines.keys()
                if model_id in ['bert_base_ner', 'bert_creative_ner']
            ]
            
            if len(ensemble_models) >= 2:
                self.pipelines['ensemble'] = {
                    'models': ensemble_models,
                    'voting_strategy': 'weighted_confidence',
                    'weights': {
                        'bert_base_ner': 0.4,
                        'bert_creative_ner': 0.6
                    }
                }
                
                self.model_configs['ensemble'] = {
                    'type': NERModelType.TRANSFORMER_ENSEMBLE,
                    'base_models': ensemble_models,
                    'language': LanguageSupport.ENGLISH
                }
                
                self.logger.info("Ensemble model initialized successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize ensemble model: {str(e)}")
    
    async def _load_language_models(self):
        """Load language-specific models"""        language_configs = {
            'de': 'dbmdz/bert-base-german-cased',
            'fr': 'camembert-base',
            'es': 'dccuchile/bert-base-spanish-wwm-cased'
        }
        
        for lang_code, model_name in language_configs.items():
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForTokenClassification.from_pretrained(model_name)
                pipeline_obj = pipeline("ner", model=model, tokenizer=tokenizer)
                
                self.language_models[lang_code] = {
                    'tokenizer': tokenizer,
                    'model': model,
                    'pipeline': pipeline_obj
                }
                
                self.logger.info(f"Loaded language model for {lang_code}")
                
            except Exception as e:
                self.logger.warning(f"Failed to load language model for {lang_code}: {str(e)}")
    
    async def _load_prediction_cache(self):
        """Load cached predictions for faster inference"""        try:
            cache_path = '/cache/ner_predictions.pkl'
            if await self.model_manager.model_exists(cache_path):
                with open(cache_path, 'rb') as f:
                    self.prediction_cache = pickle.load(f)
                self.logger.info(f"Loaded {len(self.prediction_cache)} cached predictions")
            
        except Exception as e:
            self.logger.warning(f"Failed to load prediction cache: {str(e)}")
            self.prediction_cache = {}
    
    @cache_manager.cached(ttl=1800)
    async def recognize_entities(
        self,
        text: str,
        model_type: Optional[NERModelType] = None,
        language: Optional[LanguageSupport] = None,
        confidence_threshold: float = 0.5
    ) -> List[NERPrediction]:
        """        Recognize named entities in text using specified or ensemble models.
        
        Args:
            text: Input text for entity recognition
            model_type: Specific model type to use (None for ensemble)
            language: Language of the text
            confidence_threshold: Minimum confidence for predictions
            
        Returns:
            List of NER predictions with confidence scores
        """        start_time = datetime.now()
        
        try:
            self.logger.debug(f"Starting NER for text length: {len(text)}")
            self.metrics.increment('ner_requests')
            
            # Check cache first
            cache_key = hash(f"{text}_{model_type}_{language}_{confidence_threshold}")
            if cache_key in self.prediction_cache:
                self.metrics.increment('cache_hits')
                return self.prediction_cache[cache_key]
            
            # Preprocess text
            processed_text = self.text_processor.clean_text(text)
            
            # Determine language if not specified
            if not language:
                language = await self._detect_language(processed_text)
            
            # Select appropriate models
            if model_type:
                predictions = await self._run_single_model(
                    processed_text, model_type, language, confidence_threshold
                )
            else:
                predictions = await self._run_ensemble_models(
                    processed_text, language, confidence_threshold
                )
            
            # Post-process predictions
            predictions = await self._post_process_predictions(predictions, text)
            
            # Cache results
            self.prediction_cache[cache_key] = predictions
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"NER completed: {len(predictions)} entities in {processing_time:.3f}s")
            
            # Update metrics
            self.metrics.histogram('processing_time', processing_time)
            self.metrics.histogram('entity_count', len(predictions))
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"NER failed: {str(e)}")
            self.metrics.increment('ner_errors')
            raise
    
    async def _detect_language(self, text: str) -> LanguageSupport:
        """Detect language of input text"""        try:
            # Simple language detection based on character patterns
            # In production, use a proper language detection library
            if any(char in text for char in 'äöüß'):
                return LanguageSupport.GERMAN
            elif any(char in text for char in 'àâäéèêëïîôöùûüÿç'):
                return LanguageSupport.FRENCH
            elif any(char in text for char in 'ñáéíóúü'):
                return LanguageSupport.SPANISH
            else:
                return LanguageSupport.ENGLISH
                
        except Exception:
            return LanguageSupport.ENGLISH
    
    async def _run_single_model(
        self,
        text: str,
        model_type: NERModelType,
        language: LanguageSupport,
        confidence_threshold: float
    ) -> List[NERPrediction]:
        """Run NER with a single model"""        predictions = []
        
        # Find appropriate model
        model_id = self._select_model_for_type_and_language(model_type, language)
        if not model_id or model_id not in self.pipelines:
            self.logger.warning(f"Model not available: {model_type}, {language}")
            return predictions
        
        try:
            # Run inference
            results = self.pipelines[model_id](text)
            
            # Convert to our format
            for result in results:
                if result['score'] >= confidence_threshold:
                    prediction = NERPrediction(
                        token=result['word'],
                        label=result['entity_group'],
                        confidence=result['score'],
                        start_pos=result['start'],
                        end_pos=result['end'],
                        model_source=model_id,
                        language=language.value,
                        metadata={
                            'model_type': model_type.value,
                            'original_label': result.get('entity', result['entity_group'])
                        }
                    )
                    predictions.append(prediction)
                    
        except Exception as e:
            self.logger.error(f"Single model inference failed: {str(e)}")
            
        return predictions
    
    async def _run_ensemble_models(
        self,
        text: str,
        language: LanguageSupport,
        confidence_threshold: float
    ) -> List[NERPrediction]:
        """Run ensemble of models and combine predictions"""        all_predictions = []
        
        # Run each available model
        for model_id, pipeline_obj in self.pipelines.items():
            if model_id == 'ensemble':  # Skip ensemble configuration
                continue
                
            try:
                # Check if model supports the language
                model_config = self.model_configs.get(model_id, {})
                model_language = model_config.get('language', LanguageSupport.ENGLISH)
                
                if model_language not in [language, LanguageSupport.MULTILINGUAL]:
                    continue
                
                # Run model
                results = pipeline_obj(text)
                
                # Convert results
                for result in results:
                    if result['score'] >= confidence_threshold:
                        prediction = NERPrediction(
                            token=result['word'],
                            label=result['entity_group'],
                            confidence=result['score'],
                            start_pos=result['start'],
                            end_pos=result['end'],
                            model_source=model_id,
                            language=language.value,
                            metadata={
                                'ensemble_member': True,
                                'original_label': result.get('entity', result['entity_group'])
                            }
                        )
                        all_predictions.append(prediction)
                        
            except Exception as e:
                self.logger.warning(f"Model {model_id} failed in ensemble: {str(e)}")
        
        # Combine predictions from ensemble
        combined_predictions = await self._combine_ensemble_predictions(all_predictions)
        
        return combined_predictions
    
    async def _combine_ensemble_predictions(self, predictions: List[NERPrediction]) -> List[NERPrediction]:
        """Combine predictions from multiple models using voting"""        if not predictions:
            return []
        
        # Group overlapping predictions
        grouped_predictions = self._group_overlapping_predictions(predictions)
        
        # Combine each group
        combined = []
        for group in grouped_predictions:
            if len(group) == 1:
                combined.append(group[0])
            else:
                # Weighted voting based on model confidence and type
                best_prediction = self._vote_on_predictions(group)
                combined.append(best_prediction)
        
        return combined
    
    def _group_overlapping_predictions(self, predictions: List[NERPrediction]) -> List[List[NERPrediction]]:
        """Group predictions that overlap in position"""        if not predictions:
            return []
        
        # Sort by start position
        sorted_predictions = sorted(predictions, key=lambda x: x.start_pos)
        
        groups = []
        current_group = [sorted_predictions[0]]
        
        for pred in sorted_predictions[1:]:
            # Check if overlaps with current group
            if any(pred.start_pos < p.end_pos and pred.end_pos > p.start_pos for p in current_group):
                current_group.append(pred)
            else:
                groups.append(current_group)
                current_group = [pred]
        
        groups.append(current_group)
        return groups
    
    def _vote_on_predictions(self, predictions: List[NERPrediction]) -> NERPrediction:
        """Vote on overlapping predictions to select best one"""        if len(predictions) == 1:
            return predictions[0]
        
        # Weight predictions based on model type and confidence
        weighted_scores = {}
        
        for pred in predictions:
            # Model weights
            model_weight = self._get_model_weight(pred.model_source)
            
            # Label consistency weight
            label_key = pred.label
            if label_key not in weighted_scores:
                weighted_scores[label_key] = {
                    'total_weight': 0.0,
                    'predictions': []
                }
            
            weight = pred.confidence * model_weight
            weighted_scores[label_key]['total_weight'] += weight
            weighted_scores[label_key]['predictions'].append(pred)
        
        # Select label with highest weighted score
        best_label = max(weighted_scores.keys(), key=lambda k: weighted_scores[k]['total_weight'])
        best_predictions = weighted_scores[best_label]['predictions']
        
        # Select best prediction from winning label
        best_pred = max(best_predictions, key=lambda p: p.confidence)
        
        # Update confidence with ensemble information
        ensemble_confidence = weighted_scores[best_label]['total_weight'] / len(predictions)
        best_pred.confidence = min(ensemble_confidence, 1.0)
        best_pred.metadata['ensemble_vote'] = {
            'num_votes': len(best_predictions),
            'total_models': len(predictions),
            'vote_weight': weighted_scores[best_label]['total_weight']
        }
        
        return best_pred
    
    def _get_model_weight(self, model_source: str) -> float:
        """Get weight for model in ensemble voting"""        weights = {
            'bert_base_ner': 0.3,
            'bert_creative_ner': 0.4,
            'multilingual_ner': 0.2,
            'music_specialist': 0.5,
            'influencer_specialist': 0.5,
            'business_specialist': 0.4
        }
        return weights.get(model_source, 0.1)
    
    def _select_model_for_type_and_language(
        self,
        model_type: NERModelType,
        language: LanguageSupport
    ) -> Optional[str]:
        """Select appropriate model based on type and language"""        for model_id, config in self.model_configs.items():
            if config.get('type') == model_type:
                model_language = config.get('language', LanguageSupport.ENGLISH)
                if model_language in [language, LanguageSupport.MULTILINGUAL]:
                    return model_id
        return None
    
    async def _post_process_predictions(
        self,
        predictions: List[NERPrediction],
        original_text: str
    ) -> List[NERPrediction]:
        """Post-process predictions for consistency and accuracy"""        if not predictions:
            return predictions
        
        # Sort by position
        predictions.sort(key=lambda x: x.start_pos)
        
        # Merge adjacent tokens of same entity type
        merged_predictions = []
        i = 0
        
        while i < len(predictions):
            current = predictions[i]
            
            # Look for adjacent tokens of same type
            while (i + 1 < len(predictions) and 
                   predictions[i + 1].start_pos <= current.end_pos + 2 and
                   predictions[i + 1].label == current.label):
                next_pred = predictions[i + 1]
                
                # Merge tokens
                merged_token = original_text[current.start_pos:next_pred.end_pos]
                current.token = merged_token
                current.end_pos = next_pred.end_pos
                current.confidence = max(current.confidence, next_pred.confidence)
                
                i += 1
            
            merged_predictions.append(current)
            i += 1
        
        # Apply creative industry specific corrections
        corrected_predictions = await self._apply_creative_corrections(merged_predictions)
        
        return corrected_predictions
    
    async def _apply_creative_corrections(self, predictions: List[NERPrediction]) -> List[NERPrediction]:
        """Apply creative industry specific corrections to predictions"""        corrected = []
        
        for pred in predictions:
            # Correct common misclassifications in creative content
            corrected_pred = self._correct_creative_entity(pred)
            corrected.append(corrected_pred)
        
        return corrected
    
    def _correct_creative_entity(self, prediction: NERPrediction) -> NERPrediction:
        """Correct entity based on creative industry knowledge"""        token_lower = prediction.token.lower()
        
        # Music platform corrections
        music_platforms = {'spotify', 'apple music', 'youtube music', 'soundcloud', 'bandcamp'}
        if token_lower in music_platforms and prediction.label != 'PLATFORM':
            prediction.label = 'PLATFORM'
            prediction.confidence = min(prediction.confidence + 0.1, 1.0)
        
        # Social media platform corrections
        social_platforms = {'instagram', 'tiktok', 'twitter', 'facebook', 'youtube'}
        if token_lower in social_platforms and prediction.label != 'PLATFORM':
            prediction.label = 'PLATFORM'
            prediction.confidence = min(prediction.confidence + 0.1, 1.0)
        
        # Music genre corrections
        music_genres = {'pop', 'rock', 'hip-hop', 'jazz', 'classical', 'electronic'}
        if token_lower in music_genres and prediction.label != 'GENRE':
            prediction.label = 'GENRE'
            prediction.confidence = min(prediction.confidence + 0.15, 1.0)
        
        return prediction
    
    async def train_custom_model(
        self,
        training_data: List[TrainingExample],
        model_name: str,
        base_model: str = "bert-base-uncased"
    ) -> NERModelMetrics:
        """        Train a custom NER model for specific entity types.
        
        Args:
            training_data: List of training examples with labels
            model_name: Name for the custom model
            base_model: Base model to fine-tune
            
        Returns:
            Training metrics and performance
        """        try:
            self.logger.info(f"Starting training of custom model: {model_name}")
            start_time = datetime.now()
            
            # Prepare training data
            train_dataset, eval_dataset = self._prepare_training_data(training_data)
            
            # Load base model
            tokenizer = AutoTokenizer.from_pretrained(base_model)
            model = AutoModelForTokenClassification.from_pretrained(
                base_model,
                num_labels=len(self._get_all_labels())
            )
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir=f'/models/ner/{model_name}',
                learning_rate=self.training_config['learning_rate'],
                per_device_train_batch_size=self.training_config['batch_size'],
                num_train_epochs=self.training_config['num_epochs'],
                warmup_steps=self.training_config['warmup_steps'],
                logging_dir=f'/logs/ner/{model_name}',
                evaluation_strategy="epoch",
                save_strategy="epoch",
                load_best_model_at_end=True,
                metric_for_best_model="f1",
            )
            
            # Create trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                tokenizer=tokenizer,
                compute_metrics=self._compute_metrics
            )
            
            # Train model
            trainer.train()
            
            # Evaluate model
            eval_results = trainer.evaluate()
            
            # Save model
            model_path = f'/models/ner/{model_name}'
            trainer.save_model(model_path)
            tokenizer.save_pretrained(model_path)
            
            # Calculate metrics
            training_time = (datetime.now() - start_time).total_seconds()
            metrics = NERModelMetrics(
                precision=eval_results['eval_precision'],
                recall=eval_results['eval_recall'],
                f1_score=eval_results['eval_f1'],
                accuracy=eval_results['eval_accuracy'],
                training_time=training_time,
                inference_time=0.0,  # Will be measured during inference
                model_size=self._get_model_size(model_path)
            )
            
            # Store model in registry
            self.models[model_name] = model
            self.tokenizers[model_name] = tokenizer
            self.model_metrics[model_name] = metrics
            
            self.logger.info(f"Model training completed: {model_name}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Model training failed: {str(e)}")
            raise
    
    def _prepare_training_data(self, training_data: List[TrainingExample]) -> Tuple[Any, Any]:
        """Prepare training data for model training"""        # Convert training examples to format expected by transformers
        # This would involve tokenization and label alignment
        # Implementation depends on specific training data format
        pass
    
    def _get_all_labels(self) -> List[str]:
        """Get all possible entity labels"""        all_labels = ['O']  # Outside label
        for category_labels in self.creative_labels.values():
            all_labels.extend(category_labels)
        return list(set(all_labels))
    
    def _compute_metrics(self, eval_pred):
        """Compute evaluation metrics during training"""        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=2)
        
        # Remove padding
        true_predictions = [
            [p for p, l in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        true_labels = [
            [l for l in label if l != -100]
            for label in labels
        ]
        
        # Calculate metrics
        results = classification_report(
            [label for sublist in true_labels for label in sublist],
            [pred for sublist in true_predictions for pred in sublist],
            output_dict=True
        )
        
        return {
            'precision': results['macro avg']['precision'],
            'recall': results['macro avg']['recall'],
            'f1': results['macro avg']['f1-score'],
            'accuracy': results['accuracy']
        }
    
    def _get_model_size(self, model_path: str) -> int:
        """Get model size in bytes"""        import os
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(model_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size
    
    async def get_model_performance(self, model_name: str) -> Optional[NERModelMetrics]:
        """Get performance metrics for a specific model"""        return self.model_metrics.get(model_name)
    
    async def list_available_models(self) -> Dict[str, Dict[str, Any]]:
        """List all available NER models with their configurations"""        models_info = {}
        
        for model_id, config in self.model_configs.items():
            models_info[model_id] = {
                'config': config,
                'loaded': model_id in self.models,
                'metrics': self.model_metrics.get(model_id)
            }
        
        return models_info
    
    async def save_prediction_cache(self):
        """Save prediction cache to disk"""        try:
            cache_path = '/cache/ner_predictions.pkl'
            with open(cache_path, 'wb') as f:
                pickle.dump(self.prediction_cache, f)
            self.logger.info(f"Saved {len(self.prediction_cache)} cached predictions")
            
        except Exception as e:
            self.logger.error(f"Failed to save prediction cache: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for NER service"""        return {
            'status': 'healthy',
            'loaded_models': len(self.models),
            'available_pipelines': len(self.pipelines),
            'cached_predictions': len(self.prediction_cache),
            'supported_languages': [lang.value for lang in LanguageSupport],
            'gpu_available': torch.cuda.is_available(),
            'model_metrics': {
                model_name: {
                    'f1_score': metrics.f1_score,
                    'accuracy': metrics.accuracy
                }
                for model_name, metrics in self.model_metrics.items()
            }
        }
