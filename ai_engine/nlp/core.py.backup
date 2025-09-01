"""Core NLP Engine for IA Influencer Agent Platform

Advanced Natural Language Processing core functionality with enterprise-grade features
for content creators, influencers, and multi-format content processing.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
import spacy
import transformers
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class NLPTask:
    """Represents an NLP processing task"""
    task_id: str
    content: str
    content_type: str  # 'text', 'audio_transcript', 'video_caption', 'image_description'
    language: str
    priority: int = 1
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class NLPResult:
    """Represents NLP processing results"""
    task_id: str
    results: Dict[str, Any]
    confidence_scores: Dict[str, float]
    processing_time: float
    model_versions: Dict[str, str]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class AdvancedNLPEngine:
    """
    Enterprise-grade NLP Engine for IA Influencer Agent Platform
    
    Capabilities:
    - Multi-language content processing
    - Semantic similarity analysis
    - Content quality assessment
    - Brand voice analysis
    - Collaboration matching
    - SEO optimization
    - Content fingerprinting
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        self.nlp_processors = {}
        self.vectorizers = {}
        self.is_initialized = False
        
    async def initialize(self) -> bool:
        """Initialize all NLP models and processors"""
        try:
            logger.info("Initializing Advanced NLP Engine...")
            
            # Load SpaCy models for different languages
            await self._load_spacy_models()
            
            # Load Transformers models
            await self._load_transformer_models()
            
            # Initialize specialized pipelines
            await self._initialize_pipelines()
            
            # Initialize vectorizers
            await self._initialize_vectorizers()
            
            self.is_initialized = True
            logger.info("NLP Engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize NLP Engine: {str(e)}")
            return False
    
    async def _load_spacy_models(self):
        """Load SpaCy models for multiple languages"""
        models_to_load = {
            'en': 'en_core_web_lg',
            'de': 'de_core_news_lg',
            'fr': 'fr_core_news_lg',
            'es': 'es_core_news_lg',
            'it': 'it_core_news_lg'
        }
        
        for lang, model_name in models_to_load.items():
            try:
                self.nlp_processors[lang] = spacy.load(model_name)
                logger.info(f"Loaded SpaCy model for {lang}: {model_name}")
            except IOError:
                logger.warning(f"SpaCy model {model_name} not found, using smaller model")
                try:
                    backup_models = {
                        'en': 'en_core_web_sm',
                        'de': 'de_core_news_sm',
                        'fr': 'fr_core_news_sm',
                        'es': 'es_core_news_sm',
                        'it': 'it_core_news_sm'
                    }
                    self.nlp_processors[lang] = spacy.load(backup_models[lang])
                except IOError:
                    logger.error(f"No SpaCy model available for {lang}")
    
    async def _load_transformer_models(self):
        """Load transformer models for advanced processing"""
        models_config = {
            'sentiment': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
            'embeddings': 'sentence-transformers/all-MiniLM-L6-v2',
            'classification': 'microsoft/DialoGPT-medium',
            'generation': 'gpt2-medium',
            'summarization': 'facebook/bart-large-cnn',
            'question_answering': 'distilbert-base-cased-distilled-squad'
        }
        
        for task, model_name in models_config.items():
            try:
                self.tokenizers[task] = AutoTokenizer.from_pretrained(model_name)
                self.models[task] = AutoModel.from_pretrained(model_name)
                logger.info(f"Loaded transformer model for {task}: {model_name}")
            except Exception as e:
                logger.warning(f"Could not load {task} model: {str(e)}")
    
    async def _initialize_pipelines(self):
        """Initialize HuggingFace pipelines"""
        pipeline_configs = {
            'sentiment': ('sentiment-analysis', 'cardiffnlp/twitter-roberta-base-sentiment-latest'),
            'summarization': ('summarization', 'facebook/bart-large-cnn'),
            'text_generation': ('text-generation', 'gpt2'),
            'question_answering': ('question-answering', 'distilbert-base-cased-distilled-squad'),
            'feature_extraction': ('feature-extraction', 'sentence-transformers/all-MiniLM-L6-v2'),
            'text_classification': ('text-classification', 'microsoft/DialoGPT-medium')
        }
        
        for name, (task, model) in pipeline_configs.items():
            try:
                self.pipelines[name] = pipeline(task, model=model)
                logger.info(f"Initialized pipeline: {name}")
            except Exception as e:
                logger.warning(f"Could not initialize {name} pipeline: {str(e)}")
    
    async def _initialize_vectorizers(self):
        """Initialize TF-IDF and other vectorizers"""
        self.vectorizers['tfidf'] = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 3),
            stop_words='english'
        )
        
        self.vectorizers['tfidf_multilang'] = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            analyzer='word'
        )
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'max_content_length': 10000,
            'supported_languages': ['en', 'de', 'fr', 'es', 'it'],
            'batch_size': 32,
            'device': 'cuda' if torch.cuda.is_available() else 'cpu',
            'cache_size': 1000,
            'timeout_seconds': 30
        }
    
    async def process_content(self, task: NLPTask) -> NLPResult:
        """
        Process content with comprehensive NLP analysis
        
        Args:
            task: NLPTask object containing content and metadata
            
        Returns:
            NLPResult with comprehensive analysis results
        """
        if not self.is_initialized:
            await self.initialize()
        
        start_time = datetime.utcnow()
        results = {}
        confidence_scores = {}
        
        try:
            # Language detection
            detected_lang = await self._detect_language(task.content)
            results['detected_language'] = detected_lang
            confidence_scores['language_detection'] = 0.95
            
            # Content preprocessing
            cleaned_content = await self._preprocess_content(task.content)
            results['cleaned_content'] = cleaned_content
            
            # Linguistic analysis
            linguistic_analysis = await self._linguistic_analysis(cleaned_content, detected_lang)
            results['linguistic_analysis'] = linguistic_analysis
            confidence_scores['linguistic_analysis'] = 0.90
            
            # Semantic analysis
            semantic_analysis = await self._semantic_analysis(cleaned_content)
            results['semantic_analysis'] = semantic_analysis
            confidence_scores['semantic_analysis'] = 0.88
            
            # Content quality assessment
            quality_metrics = await self._assess_content_quality(cleaned_content, detected_lang)
            results['quality_metrics'] = quality_metrics
            confidence_scores['quality_assessment'] = 0.85
            
            # Brand voice analysis
            brand_voice = await self._analyze_brand_voice(cleaned_content)
            results['brand_voice'] = brand_voice
            confidence_scores['brand_voice'] = 0.82
            
            # Collaboration potential
            collaboration_metrics = await self._analyze_collaboration_potential(cleaned_content)
            results['collaboration_potential'] = collaboration_metrics
            confidence_scores['collaboration_analysis'] = 0.80
            
            # Content fingerprinting
            fingerprint = await self._generate_content_fingerprint(cleaned_content)
            results['content_fingerprint'] = fingerprint
            confidence_scores['fingerprinting'] = 0.95
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return NLPResult(
                task_id=task.task_id,
                results=results,
                confidence_scores=confidence_scores,
                processing_time=processing_time,
                model_versions=self._get_model_versions()
            )
            
        except Exception as e:
            logger.error(f"Error processing content for task {task.task_id}: {str(e)}")
            raise
    
    async def _detect_language(self, content: str) -> str:
        """Detect content language"""
        # Simple language detection - can be enhanced with dedicated models
        if any(word in content.lower() for word in ['the', 'and', 'is', 'are', 'was', 'were']):
            return 'en'
        elif any(word in content.lower() for word in ['der', 'die', 'das', 'und', 'ist', 'sind']):
            return 'de'
        elif any(word in content.lower() for word in ['le', 'la', 'les', 'et', 'est', 'sont']):
            return 'fr'
        else:
            return 'en'  # Default to English
    
    async def _preprocess_content(self, content: str) -> str:
        """Clean and preprocess content"""
        # Remove extra whitespace
        content = ' '.join(content.split())
        
        # Remove special characters but keep punctuation
        import re
        content = re.sub(r'[^\w\s\.\!\?\,\;\:]', '', content)
        
        return content.strip()
    
    async def _linguistic_analysis(self, content: str, language: str) -> Dict[str, Any]:
        """Perform linguistic analysis using SpaCy"""
        if language not in self.nlp_processors:
            language = 'en'  # Default to English
        
        nlp = self.nlp_processors[language]
        doc = nlp(content)
        
        return {
            'tokens': len(doc),
            'sentences': len(list(doc.sents)),
            'words': len([token for token in doc if token.is_alpha]),
            'entities': [(ent.text, ent.label_) for ent in doc.ents],
            'pos_tags': [(token.text, token.pos_) for token in doc if token.is_alpha],
            'dependencies': [(token.text, token.dep_, token.head.text) for token in doc if token.is_alpha],
            'readability_score': self._calculate_readability(doc)
        }
    
    async def _semantic_analysis(self, content: str) -> Dict[str, Any]:
        """Perform semantic analysis"""
        try:
            # Generate embeddings
            embeddings = self.pipelines['feature_extraction'](content)
            embedding_vector = np.mean(embeddings[0], axis=0)
            
            # Topic extraction (simplified)
            topics = await self._extract_topics(content)
            
            # Semantic similarity with common influencer topics
            influencer_topics = [
                "lifestyle fashion beauty",
                "music entertainment performance",
                "technology innovation digital",
                "fitness health wellness",
                "travel adventure exploration",
                "food cooking culinary",
                "business entrepreneurship success"
            ]
            
            topic_similarities = []
            for topic in influencer_topics:
                topic_embedding = self.pipelines['feature_extraction'](topic)
                topic_vector = np.mean(topic_embedding[0], axis=0)
                similarity = cosine_similarity([embedding_vector], [topic_vector])[0][0]
                topic_similarities.append((topic, float(similarity)))
            
            return {
                'embedding_dimension': len(embedding_vector),
                'topics': topics,
                'topic_similarities': topic_similarities,
                'semantic_richness': float(np.std(embedding_vector))
            }
            
        except Exception as e:
            logger.warning(f"Semantic analysis failed: {str(e)}")
            return {'error': str(e)}
    
    async def _assess_content_quality(self, content: str, language: str) -> Dict[str, Any]:
        """Assess content quality metrics"""
        words = content.split()
        sentences = content.split('.')
        
        # Basic quality metrics
        avg_sentence_length = len(words) / max(len(sentences), 1)
        word_variety = len(set(words)) / max(len(words), 1)
        
        # Content engagement potential
        engagement_keywords = [
            'amazing', 'incredible', 'stunning', 'beautiful', 'awesome',
            'love', 'perfect', 'best', 'great', 'wonderful', 'fantastic'
        ]
        engagement_score = sum(1 for word in words if word.lower() in engagement_keywords) / max(len(words), 1)
        
        # Professional tone assessment
        professional_indicators = [
            'professional', 'expertise', 'experience', 'quality', 'service',
            'innovative', 'excellence', 'certified', 'proven', 'reliable'
        ]
        professionalism_score = sum(1 for word in words if word.lower() in professional_indicators) / max(len(words), 1)
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_sentence_length': avg_sentence_length,
            'word_variety': word_variety,
            'engagement_score': engagement_score,
            'professionalism_score': professionalism_score,
            'content_density': len(words) / max(len(content), 1),
            'quality_grade': self._calculate_quality_grade(avg_sentence_length, word_variety, engagement_score)
        }
    
    async def _analyze_brand_voice(self, content: str) -> Dict[str, Any]:
        """Analyze brand voice characteristics"""
        try:
            # Sentiment analysis
            sentiment_result = self.pipelines['sentiment'](content)
            
            # Tone analysis (simplified)
            tone_indicators = {
                'professional': ['professional', 'business', 'corporate', 'formal'],
                'casual': ['hey', 'awesome', 'cool', 'fun', 'casual'],
                'inspirational': ['inspire', 'motivate', 'achieve', 'dream', 'success'],
                'educational': ['learn', 'understand', 'explain', 'knowledge', 'teach'],
                'entertaining': ['funny', 'humor', 'laugh', 'entertaining', 'amusing']
            }
            
            words = content.lower().split()
            tone_scores = {}
            
            for tone, indicators in tone_indicators.items():
                score = sum(1 for word in words if word in indicators) / max(len(words), 1)
                tone_scores[tone] = score
            
            dominant_tone = max(tone_scores, key=tone_scores.get)
            
            return {
                'sentiment': sentiment_result[0] if sentiment_result else None,
                'tone_scores': tone_scores,
                'dominant_tone': dominant_tone,
                'voice_consistency': max(tone_scores.values()),
                'authenticity_score': self._calculate_authenticity_score(content)
            }
            
        except Exception as e:
            logger.warning(f"Brand voice analysis failed: {str(e)}")
            return {'error': str(e)}
    
    async def _analyze_collaboration_potential(self, content: str) -> Dict[str, Any]:
        """Analyze content for collaboration potential"""
        collaboration_indicators = {
            'partnership': ['partner', 'collaboration', 'together', 'team', 'joint'],
            'brand_mention': ['brand', 'sponsor', 'featured', 'review', 'recommend'],
            'community': ['community', 'followers', 'audience', 'fans', 'subscribers'],
            'networking': ['connect', 'network', 'meet', 'contact', 'reach'],
            'creative': ['creative', 'art', 'design', 'innovative', 'original']
        }
        
        words = content.lower().split()
        collab_scores = {}
        
        for category, indicators in collaboration_indicators.items():
            score = sum(1 for word in words if word in indicators) / max(len(words), 1)
            collab_scores[category] = score
        
        overall_potential = sum(collab_scores.values()) / len(collab_scores)
        
        return {
            'category_scores': collab_scores,
            'overall_potential': overall_potential,
            'collaboration_readiness': overall_potential > 0.05,
            'recommended_partnerships': self._suggest_partnerships(collab_scores)
        }
    
    async def _generate_content_fingerprint(self, content: str) -> Dict[str, Any]:
        """Generate unique content fingerprint for protection"""
        import hashlib
        
        # Create multiple hash types for robust fingerprinting
        content_bytes = content.encode('utf-8')
        
        fingerprints = {
            'md5': hashlib.md5(content_bytes).hexdigest(),
            'sha256': hashlib.sha256(content_bytes).hexdigest(),
            'content_length': len(content),
            'word_count': len(content.split()),
            'char_frequency': self._calculate_char_frequency(content),
            'structural_hash': self._calculate_structural_hash(content)
        }
        
        return fingerprints
    
    async def _extract_topics(self, content: str) -> List[str]:
        """Extract main topics from content"""
        # Simplified topic extraction - can be enhanced with LDA or other methods
        words = content.lower().split()
        
        # Remove stop words (simplified)
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Simple frequency-based topic extraction
        from collections import Counter
        word_freq = Counter(meaningful_words)
        topics = [word for word, freq in word_freq.most_common(10) if freq > 1]
        
        return topics
    
    def _calculate_readability(self, doc) -> float:
        """Calculate readability score (simplified Flesch Reading Ease)"""
        sentences = len(list(doc.sents))
        words = len([token for token in doc if token.is_alpha])
        syllables = sum(self._count_syllables(token.text) for token in doc if token.is_alpha)
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Simplified Flesch Reading Ease formula
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        return max(0.0, min(100.0, score))
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""
        vowels = 'aeiouy'
        count = 0
        prev_was_vowel = False
        
        for char in word.lower():
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                count += 1
            prev_was_vowel = is_vowel
        
        return max(1, count)
    
    def _calculate_quality_grade(self, avg_sentence_length: float, word_variety: float, engagement_score: float) -> str:
        """Calculate overall content quality grade"""
        # Scoring system
        sentence_score = min(10, max(0, 10 - abs(avg_sentence_length - 15) / 2))
        variety_score = word_variety * 10
        engagement_score_scaled = engagement_score * 100
        
        total_score = (sentence_score + variety_score + engagement_score_scaled) / 3
        
        if total_score >= 8:
            return "A"
        elif total_score >= 6:
            return "B"
        elif total_score >= 4:
            return "C"
        else:
            return "D"
    
    def _calculate_authenticity_score(self, content: str) -> float:
        """Calculate content authenticity score"""
        # Simple authenticity indicators
        personal_pronouns = ['i', 'me', 'my', 'myself', 'we', 'us', 'our']
        authentic_phrases = ['in my experience', 'i believe', 'personally', 'from my perspective']
        
        words = content.lower().split()
        personal_score = sum(1 for word in words if word in personal_pronouns) / max(len(words), 1)
        phrase_score = sum(1 for phrase in authentic_phrases if phrase in content.lower()) / 10
        
        return min(1.0, personal_score + phrase_score)
    
    def _suggest_partnerships(self, collab_scores: Dict[str, float]) -> List[str]:
        """Suggest partnership types based on collaboration scores"""
        suggestions = []
        
        if collab_scores.get('brand_mention', 0) > 0.03:
            suggestions.append('Brand partnerships')
        if collab_scores.get('creative', 0) > 0.02:
            suggestions.append('Creative collaborations')
        if collab_scores.get('community', 0) > 0.04:
            suggestions.append('Community partnerships')
        if collab_scores.get('networking', 0) > 0.02:
            suggestions.append('Professional networking')
        
        return suggestions if suggestions else ['General content collaboration']
    
    def _calculate_char_frequency(self, content: str) -> Dict[str, float]:
        """Calculate character frequency distribution"""
        from collections import Counter
        char_count = Counter(content.lower())
        total_chars = sum(char_count.values())
        
        return {char: count/total_chars for char, count in char_count.most_common(10)}
    
    def _calculate_structural_hash(self, content: str) -> str:
        """Calculate structural hash based on content pattern"""
        import hashlib
        
        # Create structural signature
        structure = []
        for char in content:
            if char.isalpha():
                structure.append('L')
            elif char.isdigit():
                structure.append('D')
            elif char.isspace():
                structure.append('S')
            else:
                structure.append('P')
        
        structure_str = ''.join(structure[:100])  # Limit to first 100 chars
        return hashlib.md5(structure_str.encode()).hexdigest()
    
    def _get_model_versions(self) -> Dict[str, str]:
        """Get versions of loaded models"""
        return {
            'spacy_version': spacy.__version__,
            'transformers_version': transformers.__version__,
            'torch_version': torch.__version__,
            'sklearn_version': '1.0.0',  # Placeholder
            'engine_version': '1.0.0'
        }
    
    async def batch_process(self, tasks: List[NLPTask]) -> List[NLPResult]:
        """Process multiple tasks in batch"""
        results = []
        
        # Process in batches to manage memory
        batch_size = self.config.get('batch_size', 32)
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.process_content(task) for task in batch],
                return_exceptions=True
            )
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error: {str(result)}")
                else:
                    results.append(result)
        
        return results
    
    async def cleanup(self):
        """Cleanup resources"""
        self.models.clear()
        self.tokenizers.clear()
        self.pipelines.clear()
        self.nlp_processors.clear()
        self.vectorizers.clear()
        self.is_initialized = False
        logger.info("NLP Engine cleaned up")

# Global engine instance
_nlp_engine = None

async def get_nlp_engine() -> AdvancedNLPEngine:
    """Get global NLP engine instance"""
    global _nlp_engine
    if _nlp_engine is None:
        _nlp_engine = AdvancedNLPEngine()
        await _nlp_engine.initialize()
    return _nlp_engine

async def process_content_quick(content: str, content_type: str = 'text', language: str = 'auto') -> Dict[str, Any]:
    """Quick content processing function"""
    engine = await get_nlp_engine()
    task = NLPTask(
        task_id=f"quick_{datetime.utcnow().timestamp()}",
        content=content,
        content_type=content_type,
        language=language
    )
    result = await engine.process_content(task)
    return result.results
