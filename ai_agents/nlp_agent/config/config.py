"""NLP Agent Configuration Module
=============================

Configuration settings for the NLP Agent system including model configurations,
processing parameters, and system settings.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import os
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import yaml
import json

class ModelType(Enum):
    """Supported NLP model types"""
    BERT = "bert"
    ROBERTA = "roberta"
    DISTILBERT = "distilbert"
    ALBERT = "albert"
    DEBERTA = "deberta"
    ELECTRA = "electra"
    GPT = "gpt"
    T5 = "t5"
    BART = "bart"

class LanguageCode(Enum):
    """Supported language codes"""
    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    RUSSIAN = "ru"
    ARABIC = "ar"
    HINDI = "hi"
    MULTILINGUAL = "multilingual"

class ProcessingMode(Enum):
    """Text processing modes"""
    FAST = "fast"
    BALANCED = "balanced"
    ACCURATE = "accurate"
    CUSTOM = "custom"

@dataclass
class ModelConfig:
    """Configuration for individual models"""
    model_name: str
    model_type: ModelType
    tokenizer_name: Optional[str] = None
    max_sequence_length: int = 512
    batch_size: int = 32
    device: str = "auto"
    precision: str = "fp32"
    use_cache: bool = True
    cache_dir: Optional[str] = None
    trust_remote_code: bool = False

@dataclass
class SentimentConfig:
    """Sentiment analysis configuration"""
    model_config: ModelConfig = field(default_factory=lambda: ModelConfig(
        model_name="cardiffnlp/twitter-roberta-base-sentiment-latest",
        model_type=ModelType.ROBERTA
    ))
    confidence_threshold: float = 0.7
    return_all_scores: bool = True
    enable_emotion_detection: bool = True
    emotion_model: str = "j-hartmann/emotion-english-distilroberta-base"

@dataclass
class LanguageDetectionConfig:
    """Language detection configuration"""
    model_name: str = "papluca/xlm-roberta-base-language-detection"
    confidence_threshold: float = 0.8
    max_languages: int = 3
    fallback_to_nltk: bool = True

@dataclass
class EntityExtractionConfig:
    """Named Entity Recognition configuration"""
    model_name: str = "dbmdz/bert-large-cased-finetuned-conll03-english"
    aggregation_strategy: str = "simple"
    return_confidence: bool = True
    group_entities: bool = True
    custom_entities: List[str] = field(default_factory=list)

@dataclass
class TopicModelingConfig:
    """Topic modeling configuration"""
    algorithm: str = "lda"  # lda, nmf, bertopic
    num_topics: int = 10
    max_features: int = 5000
    min_df: int = 2
    max_df: float = 0.95
    ngram_range: tuple = (1, 2)
    random_state: int = 42

@dataclass
class EmbeddingsConfig:
    """Text embeddings configuration"""
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    normalize_embeddings: bool = True
    convert_to_numpy: bool = True
    batch_size: int = 32
    show_progress_bar: bool = False
    device: Optional[str] = None

@dataclass
class TextFingerprintingConfig:
    """Text fingerprinting configuration"""
    similarity_threshold: float = 0.85
    embedding_model: str = "sentence-transformers/all-mpnet-base-v2"
    chunking_strategy: str = "sentence"
    chunk_size: int = 200
    overlap_size: int = 50
    use_semantic_search: bool = True
    index_type: str = "faiss"

@dataclass
class CacheConfig:
    """Caching configuration"""
    enabled: bool = True
    cache_type: str = "redis"  # redis, memory, disk
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    ttl_seconds: int = 3600
    max_cache_size: int = 1000

@dataclass
class ProcessingConfig:
    """General processing configuration"""
    mode: ProcessingMode = ProcessingMode.BALANCED
    max_text_length: int = 10000
    min_text_length: int = 10
    enable_preprocessing: bool = True
    remove_html: bool = True
    remove_urls: bool = False
    normalize_whitespace: bool = True
    lowercase: bool = False
    remove_punctuation: bool = False
    remove_stopwords: bool = False
    custom_preprocessing_steps: List[str] = field(default_factory=list)

@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    max_workers: int = 4
    use_multiprocessing: bool = True
    enable_gpu: bool = True
    memory_efficient: bool = True
    optimize_for_latency: bool = False
    max_memory_usage: str = "4GB"
    enable_onnx: bool = False

@dataclass
class NLPAgentConfig:
    """Main NLP Agent configuration"""
    # Model configurations
    sentiment: SentimentConfig = field(default_factory=SentimentConfig)
    language_detection: LanguageDetectionConfig = field(default_factory=LanguageDetectionConfig)
    entity_extraction: EntityExtractionConfig = field(default_factory=EntityExtractionConfig)
    topic_modeling: TopicModelingConfig = field(default_factory=TopicModelingConfig)
    embeddings: EmbeddingsConfig = field(default_factory=EmbeddingsConfig)
    text_fingerprinting: TextFingerprintingConfig = field(default_factory=TextFingerprintingConfig)
    
    # System configurations
    cache: CacheConfig = field(default_factory=CacheConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Feature flags
    enable_sentiment_analysis: bool = True
    enable_language_detection: bool = True
    enable_entity_extraction: bool = True
    enable_topic_modeling: bool = True
    enable_text_fingerprinting: bool = True
    enable_embeddings: bool = True
    enable_intent_recognition: bool = True
    
    # Logging and monitoring
    log_level: str = "INFO"
    enable_metrics: bool = True
    metrics_port: int = 8080
    enable_tracing: bool = False
    
    # Security
    api_key: Optional[str] = None
    rate_limit_per_minute: int = 1000
    enable_content_filtering: bool = True
    
    @classmethod
    def from_file(cls, config_path: str) -> "NLPAgentConfig":
        """Load configuration from file"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                config_data = yaml.safe_load(f)
            elif config_path.endswith('.json'):
                config_data = json.load(f)
            else:
                raise ValueError("Configuration file must be YAML or JSON")
        
        return cls(**config_data)
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to file"""
        config_dict = self.__dict__.copy()
        
        # Convert enums to strings
        for key, value in config_dict.items():
            if hasattr(value, '__dict__'):
                for sub_key, sub_value in value.__dict__.items():
                    if isinstance(sub_value, Enum):
                        setattr(value, sub_key, sub_value.value)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            elif config_path.endswith('.json'):
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError("Configuration file must be YAML or JSON")
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        try:
            # Validate model configurations
            if not self.sentiment.model_config.model_name:
                raise ValueError("Sentiment model name cannot be empty")
            
            # Validate thresholds
            if not 0.0 <= self.sentiment.confidence_threshold <= 1.0:
                raise ValueError("Sentiment confidence threshold must be between 0 and 1")
            
            if not 0.0 <= self.language_detection.confidence_threshold <= 1.0:
                raise ValueError("Language detection confidence threshold must be between 0 and 1")
            
            if not 0.0 <= self.text_fingerprinting.similarity_threshold <= 1.0:
                raise ValueError("Text fingerprinting similarity threshold must be between 0 and 1")
            
            # Validate performance settings
            if self.performance.max_workers < 1:
                raise ValueError("Max workers must be at least 1")
            
            # Validate processing settings
            if self.processing.max_text_length < self.processing.min_text_length:
                raise ValueError("Max text length must be greater than min text length")
            
            return True
        except Exception as e:
            print(f"Configuration validation error: {e}")
            return False

# Default configuration instance
default_config = NLPAgentConfig()

# Model registry for easy model selection
MODEL_REGISTRY = {
    "sentiment": {
        "roberta_twitter": "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "bert_multilingual": "nlptown/bert-base-multilingual-uncased-sentiment",
        "distilbert": "distilbert-base-uncased-finetuned-sst-2-english"
    },
    "emotion": {
        "distilroberta": "j-hartmann/emotion-english-distilroberta-base",
        "bert_emotion": "nateraw/bert-base-uncased-emotion"
    },
    "language_detection": {
        "xlm_roberta": "papluca/xlm-roberta-base-language-detection",
        "fasttext": "lid.176.bin"
    },
    "ner": {
        "bert_conll": "dbmdz/bert-large-cased-finetuned-conll03-english",
        "roberta_ontonotes": "Jean-Baptiste/roberta-large-ner-english",
        "spacy_en": "en_core_web_sm"
    },
    "embeddings": {
        "sentence_transformers": {
            "all_miniLM_L6": "sentence-transformers/all-MiniLM-L6-v2",
            "all_mpnet": "sentence-transformers/all-mpnet-base-v2",
            "multilingual": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        }
    }
}

def get_config_from_env() -> NLPAgentConfig:
    """Create configuration from environment variables"""
    config = NLPAgentConfig()
    
    # Override with environment variables if present
    if os.getenv("NLP_SENTIMENT_MODEL"):
        config.sentiment.model_config.model_name = os.getenv("NLP_SENTIMENT_MODEL")
    
    if os.getenv("NLP_CACHE_ENABLED"):
        config.cache.enabled = os.getenv("NLP_CACHE_ENABLED").lower() == "true"
    
    if os.getenv("NLP_REDIS_HOST"):
        config.cache.redis_host = os.getenv("NLP_REDIS_HOST")
    
    if os.getenv("NLP_REDIS_PORT"):
        config.cache.redis_port = int(os.getenv("NLP_REDIS_PORT"))
    
    if os.getenv("NLP_MAX_WORKERS"):
        config.performance.max_workers = int(os.getenv("NLP_MAX_WORKERS"))
    
    if os.getenv("NLP_ENABLE_GPU"):
        config.performance.enable_gpu = os.getenv("NLP_ENABLE_GPU").lower() == "true"
    
    return config
