"""NLP Configuration for IA-Influencer Agent Platform
==================================================

Professional Natural Language Processing configuration and models.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

STRICT COPYRIGHT NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or reverse engineering
without explicit written permission is STRICTLY PROHIBITED and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""
from typing import Dict, List, Optional, Union, Any, Tuple
from pydantic import BaseSettings, validator
from enum import Enum
from dataclasses import dataclass
import os


class NLPTask(str, Enum):
    """Supported NLP tasks for content processing."""
    
    TEXT_CLASSIFICATION = "text_classification"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    NAMED_ENTITY_RECOGNITION = "ner"
    TEXT_SIMILARITY = "text_similarity"
    TEXT_EMBEDDING = "text_embedding"
    LANGUAGE_DETECTION = "language_detection"
    CONTENT_MODERATION = "content_moderation"
    KEYWORD_EXTRACTION = "keyword_extraction"
    TEXT_SUMMARIZATION = "text_summarization"
    CONTENT_GENERATION = "content_generation"
    HASHTAG_GENERATION = "hashtag_generation"
    SEO_OPTIMIZATION = "seo_optimization"
    TRANSLATION = "translation"
    QUESTION_ANSWERING = "question_answering"
    TEXT_CLUSTERING = "text_clustering"


class NLPLanguage(str, Enum):
    """Supported languages for NLP processing."""
    
    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"
    MULTILINGUAL = "multilingual"
    AUTO_DETECT = "auto"


@dataclass
class NLPModelSpec:
    """Specification for NLP model configuration."""
    
    task: NLPTask
    model_name: str
    model_path: str
    languages: List[NLPLanguage]
    max_sequence_length: int = 512
    batch_size: int = 32
    requires_gpu: bool = False
    memory_requirement_mb: int = 512
    inference_time_ms: int = 100
    accuracy_score: float = 0.85
    supports_streaming: bool = False
    custom_params: Optional[Dict[str, Any]] = None


class NLPConfig(BaseSettings):
    """
    Professional NLP Configuration for IA-Influencer Agent Platform.
    
    Manages all Natural Language Processing models and configurations for
    content analysis, generation, protection, and optimization.
    """
    
    # Core NLP Configuration
    DEFAULT_LANGUAGE: NLPLanguage = NLPLanguage.ENGLISH
    AUTO_LANGUAGE_DETECTION: bool = True
    MULTILINGUAL_SUPPORT: bool = True
    MAX_TEXT_LENGTH: int = 5000
    MIN_TEXT_LENGTH: int = 10
    
    # Model Configuration
    NLP_MODEL_CACHE_DIR: str = "/tmp/nlp_models"
    MODEL_PARALLEL_PROCESSING: bool = True
    BATCH_PROCESSING_ENABLED: bool = True
    GPU_ACCELERATION: bool = False
    
    # Text Classification Models
    CONTENT_CLASSIFIER_MODEL: str = "facebook/bart-large-mnli"
    SENTIMENT_ANALYSIS_MODEL: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    TOXICITY_CLASSIFIER: str = "martin-ha/toxic-comment-model"
    SPAM_CLASSIFIER: str = "microsoft/DialoGPT-medium"
    
    # Text Embedding Models
    SENTENCE_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    MULTILINGUAL_EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    SEMANTIC_SEARCH_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    
    # Language Processing Models
    LANGUAGE_DETECTION_MODEL: str = "papluca/xlm-roberta-base-language-detection"
    NER_MODEL: str = "dbmdz/bert-large-cased-finetuned-conll03-english"
    POS_TAGGING_MODEL: str = "vblagoje/bert-english-uncased-finetuned-pos"
    
    # Content Generation Models
    TEXT_GENERATION_MODEL: str = "microsoft/DialoGPT-large"
    HASHTAG_GENERATION_MODEL: str = "cardiffnlp/twitter-roberta-base-hashtag"
    SEO_OPTIMIZATION_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CONTENT_SUMMARIZATION_MODEL: str = "facebook/bart-large-cnn"
    
    # Translation Models
    TRANSLATION_MODEL: str = "Helsinki-NLP/opus-mt"
    MULTILINGUAL_TRANSLATION: str = "facebook/m2m100_418M"
    
    # Specialized Models
    KEYWORD_EXTRACTION_MODEL: str = "yake"  # YAKE algorithm
    TOPIC_MODELING_MODEL: str = "bertopic"
    TEXT_CLUSTERING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Performance Configuration
    NLP_BATCH_SIZE: int = 32
    MAX_CONCURRENT_REQUESTS: int = 10
    MODEL_WARMUP_ENABLED: bool = True
    RESPONSE_CACHE_TTL: int = 3600  # seconds
    
    # Content Quality Thresholds
    SENTIMENT_CONFIDENCE_THRESHOLD: float = 0.8
    TOXICITY_THRESHOLD: float = 0.7
    SPAM_THRESHOLD: float = 0.8
    SIMILARITY_THRESHOLD: float = 0.85
    
    # SEO and Marketing Configuration
    SEO_KEYWORD_DENSITY_TARGET: float = 0.02  # 2%
    HASHTAG_MAX_COUNT: int = 30
    HASHTAG_MIN_POPULARITY: int = 1000
    META_DESCRIPTION_LENGTH: int = 160
    TITLE_OPTIMAL_LENGTH: int = 60
    
    # Multilingual Support
    SUPPORTED_LANGUAGES: List[str] = [
        "en", "fr", "de", "es", "it", "pt", "ru", "zh", "ja", "ko", "ar", "hi"
    ]
    TRANSLATION_QUALITY_THRESHOLD: float = 0.85
    
    class Config:
        env_prefix = "NLP_"
        case_sensitive = False
        env_file = ".env"
    
    @validator("NLP_MODEL_CACHE_DIR")
    def create_cache_dir(cls, v):
        """Ensure NLP model cache directory exists."""
        os.makedirs(v, exist_ok=True)
        return v
    
    def get_nlp_model_spec(self, task: NLPTask) -> NLPModelSpec:
        """Get NLP model specification by task."""
        specs = {
            NLPTask.TEXT_CLASSIFICATION: NLPModelSpec(
                task=NLPTask.TEXT_CLASSIFICATION,
                model_name="content_classifier",
                model_path=self.CONTENT_CLASSIFIER_MODEL,
                languages=[NLPLanguage.ENGLISH, NLPLanguage.MULTILINGUAL],
                max_sequence_length=1024,
                batch_size=16,
                requires_gpu=False,
                memory_requirement_mb=768,
                inference_time_ms=150,
                accuracy_score=0.91,
                custom_params={
                    "num_labels": 10,
                    "hypothesis_template": "This text is about {}."
                }
            ),
            
            NLPTask.SENTIMENT_ANALYSIS: NLPModelSpec(
                task=NLPTask.SENTIMENT_ANALYSIS,
                model_name="sentiment_analyzer",
                model_path=self.SENTIMENT_ANALYSIS_MODEL,
                languages=[NLPLanguage.ENGLISH],
                max_sequence_length=512,
                batch_size=32,
                requires_gpu=False,
                memory_requirement_mb=512,
                inference_time_ms=80,
                accuracy_score=0.88,
                supports_streaming=True,
                custom_params={
                    "labels": ["negative", "neutral", "positive"],
                    "confidence_threshold": self.SENTIMENT_CONFIDENCE_THRESHOLD
                }
            ),
            
            NLPTask.TEXT_EMBEDDING: NLPModelSpec(
                task=NLPTask.TEXT_EMBEDDING,
                model_name="text_embedder",
                model_path=self.SENTENCE_EMBEDDING_MODEL,
                languages=[NLPLanguage.ENGLISH],
                max_sequence_length=512,
                batch_size=64,
                requires_gpu=False,
                memory_requirement_mb=384,
                inference_time_ms=50,
                accuracy_score=0.86,
                supports_streaming=True,
                custom_params={
                    "normalize_embeddings": True,
                    "output_dimension": 384
                }
            ),
            
            NLPTask.LANGUAGE_DETECTION: NLPModelSpec(
                task=NLPTask.LANGUAGE_DETECTION,
                model_name="language_detector",
                model_path=self.LANGUAGE_DETECTION_MODEL,
                languages=[NLPLanguage.MULTILINGUAL],
                max_sequence_length=256,
                batch_size=128,
                requires_gpu=False,
                memory_requirement_mb=256,
                inference_time_ms=30,
                accuracy_score=0.95,
                supports_streaming=True,
                custom_params={
                    "supported_languages": self.SUPPORTED_LANGUAGES,
                    "min_confidence": 0.9
                }
            ),
            
            NLPTask.CONTENT_MODERATION: NLPModelSpec(
                task=NLPTask.CONTENT_MODERATION,
                model_name="toxicity_classifier",
                model_path=self.TOXICITY_CLASSIFIER,
                languages=[NLPLanguage.ENGLISH],
                max_sequence_length=512,
                batch_size=16,
                requires_gpu=False,
                memory_requirement_mb=512,
                inference_time_ms=100,
                accuracy_score=0.89,
                custom_params={
                    "toxicity_threshold": self.TOXICITY_THRESHOLD,
                    "categories": ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
                }
            ),
            
            NLPTask.HASHTAG_GENERATION: NLPModelSpec(
                task=NLPTask.HASHTAG_GENERATION,
                model_name="hashtag_generator",
                model_path=self.HASHTAG_GENERATION_MODEL,
                languages=[NLPLanguage.ENGLISH],
                max_sequence_length=280,
                batch_size=8,
                requires_gpu=False,
                memory_requirement_mb=1024,
                inference_time_ms=200,
                accuracy_score=0.82,
                custom_params={
                    "max_hashtags": self.HASHTAG_MAX_COUNT,
                    "min_popularity": self.HASHTAG_MIN_POPULARITY,
                    "trending_boost": True
                }
            ),
            
            NLPTask.TEXT_SUMMARIZATION: NLPModelSpec(
                task=NLPTask.TEXT_SUMMARIZATION,
                model_name="content_summarizer",
                model_path=self.CONTENT_SUMMARIZATION_MODEL,
                languages=[NLPLanguage.ENGLISH],
                max_sequence_length=1024,
                batch_size=4,
                requires_gpu=True,
                memory_requirement_mb=2048,
                inference_time_ms=500,
                accuracy_score=0.85,
                custom_params={
                    "max_summary_length": 150,
                    "min_summary_length": 30,
                    "no_repeat_ngram_size": 3
                }
            ),
            
            NLPTask.SEO_OPTIMIZATION: NLPModelSpec(
                task=NLPTask.SEO_OPTIMIZATION,
                model_name="seo_optimizer",
                model_path=self.SEO_OPTIMIZATION_MODEL,
                languages=[NLPLanguage.ENGLISH, NLPLanguage.MULTILINGUAL],
                max_sequence_length=512,
                batch_size=16,
                requires_gpu=False,
                memory_requirement_mb=512,
                inference_time_ms=120,
                accuracy_score=0.83,
                custom_params={
                    "keyword_density_target": self.SEO_KEYWORD_DENSITY_TARGET,
                    "meta_description_length": self.META_DESCRIPTION_LENGTH,
                    "title_optimal_length": self.TITLE_OPTIMAL_LENGTH
                }
            ),
            
            NLPTask.TRANSLATION: NLPModelSpec(
                task=NLPTask.TRANSLATION,
                model_name="translator",
                model_path=self.MULTILINGUAL_TRANSLATION,
                languages=[NLPLanguage.MULTILINGUAL],
                max_sequence_length=512,
                batch_size=8,
                requires_gpu=True,
                memory_requirement_mb=1536,
                inference_time_ms=300,
                accuracy_score=0.87,
                custom_params={
                    "quality_threshold": self.TRANSLATION_QUALITY_THRESHOLD,
                    "supported_pairs": 100  # language pairs
                }
            ),
        }
        
        return specs.get(task, self._get_default_nlp_spec(task))
    
    def _get_default_nlp_spec(self, task: NLPTask) -> NLPModelSpec:
        """Get default NLP model specification."""
        return NLPModelSpec(
            task=task,
            model_name="default_nlp",
            model_path=self.SENTENCE_EMBEDDING_MODEL,
            languages=[self.DEFAULT_LANGUAGE],
            max_sequence_length=self.MAX_TEXT_LENGTH,
            batch_size=self.NLP_BATCH_SIZE,
        )
    
    def get_models_by_language(self, language: NLPLanguage) -> List[NLPModelSpec]:
        """Get all NLP models that support a specific language."""
        all_tasks = [task for task in NLPTask]
        models = []
        
        for task in all_tasks:
            spec = self.get_nlp_model_spec(task)
            if language in spec.languages or NLPLanguage.MULTILINGUAL in spec.languages:
                models.append(spec)
        
        return models
    
    def get_content_analysis_pipeline(self) -> List[NLPTask]:
        """Get recommended NLP pipeline for content analysis."""
        return [
            NLPTask.LANGUAGE_DETECTION,
            NLPTask.CONTENT_MODERATION,
            NLPTask.SENTIMENT_ANALYSIS,
            NLPTask.TEXT_CLASSIFICATION,
            NLPTask.NAMED_ENTITY_RECOGNITION,
            NLPTask.TEXT_EMBEDDING,
            NLPTask.KEYWORD_EXTRACTION,
        ]
    
    def get_content_optimization_pipeline(self) -> List[NLPTask]:
        """Get recommended NLP pipeline for content optimization."""
        return [
            NLPTask.SEO_OPTIMIZATION,
            NLPTask.HASHTAG_GENERATION,
            NLPTask.TEXT_SUMMARIZATION,
            NLPTask.SENTIMENT_ANALYSIS,
        ]
    
    def get_multilingual_config(self) -> Dict[str, Any]:
        """Get multilingual processing configuration."""
        return {
            "default_language": self.DEFAULT_LANGUAGE,
            "auto_detection": self.AUTO_LANGUAGE_DETECTION,
            "supported_languages": self.SUPPORTED_LANGUAGES,
            "translation_enabled": True,
            "translation_model": self.MULTILINGUAL_TRANSLATION,
            "quality_threshold": self.TRANSLATION_QUALITY_THRESHOLD,
            "models": {
                "detection": self.LANGUAGE_DETECTION_MODEL,
                "embedding": self.MULTILINGUAL_EMBEDDING_MODEL,
                "translation": self.MULTILINGUAL_TRANSLATION,
            }
        }
    
    def get_content_quality_config(self) -> Dict[str, float]:
        """Get content quality thresholds and metrics."""
        return {
            "sentiment_confidence": self.SENTIMENT_CONFIDENCE_THRESHOLD,
            "toxicity_threshold": self.TOXICITY_THRESHOLD,
            "spam_threshold": self.SPAM_THRESHOLD,
            "similarity_threshold": self.SIMILARITY_THRESHOLD,
            "translation_quality": self.TRANSLATION_QUALITY_THRESHOLD,
            "keyword_density": self.SEO_KEYWORD_DENSITY_TARGET,
        }
    
    def get_seo_config(self) -> Dict[str, Any]:
        """Get SEO optimization configuration."""
        return {
            "keyword_density_target": self.SEO_KEYWORD_DENSITY_TARGET,
            "meta_description_length": self.META_DESCRIPTION_LENGTH,
            "title_optimal_length": self.TITLE_OPTIMAL_LENGTH,
            "hashtag_config": {
                "max_count": self.HASHTAG_MAX_COUNT,
                "min_popularity": self.HASHTAG_MIN_POPULARITY,
            },
            "models": {
                "seo_optimizer": self.SEO_OPTIMIZATION_MODEL,
                "hashtag_generator": self.HASHTAG_GENERATION_MODEL,
                "summarizer": self.CONTENT_SUMMARIZATION_MODEL,
            }
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get NLP performance configuration."""
        return {
            "batch_size": self.NLP_BATCH_SIZE,
            "max_concurrent": self.MAX_CONCURRENT_REQUESTS,
            "warmup_enabled": self.MODEL_WARMUP_ENABLED,
            "cache_ttl": self.RESPONSE_CACHE_TTL,
            "gpu_acceleration": self.GPU_ACCELERATION,
            "parallel_processing": self.MODEL_PARALLEL_PROCESSING,
            "streaming_support": True,
            "limits": {
                "max_text_length": self.MAX_TEXT_LENGTH,
                "min_text_length": self.MIN_TEXT_LENGTH,
            }
        }


# Global NLP configuration instance
nlp_config = NLPConfig()
