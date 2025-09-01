"""Intent Classification Engine

Core intent classification system with advanced ML models for creative industry
professionals. Provides multi-modal intent recognition with confidence scoring
and contextual understanding.

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
import pickle
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

import numpy as np
import torch
import torch.nn.functional as F
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    pipeline, BertTokenizer, BertForSequenceClassification
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import spacy

from ...core.base_service import BaseService
from ...core.cache import cache_manager
from ...core.monitoring import MetricsCollector
from ...models.conversation import ConversationMessage
from ...utils.text_processors import TextPreprocessor
from ...utils.validation import validate_input
from .config import IntentRecognitionConfig
from .exceptions import ClassificationError, ModelLoadError


class IntentCategory(Enum):
    """Primary intent categories for creative industry professionals"""
    
    # Content Creation & Management
    CONTENT_UPLOAD = "content_upload"
    CONTENT_EDIT = "content_edit"
    CONTENT_ENHANCE = "content_enhance"
    CONTENT_GENERATE = "content_generate"
    CONTENT_DELETE = "content_delete"
    CONTENT_ORGANIZE = "content_organize"
    
    # Protection & Security
    PROTECTION_FINGERPRINT = "protection_fingerprint"
    PROTECTION_MONITOR = "protection_monitor"
    PROTECTION_REPORT = "protection_report"
    PROTECTION_TAKEDOWN = "protection_takedown"
    PROTECTION_CONFIGURE = "protection_configure"
    
    # Monetization & Revenue
    MONETIZATION_TRACK = "monetization_track"
    MONETIZATION_LICENSE = "monetization_license"
    MONETIZATION_PAYOUT = "monetization_payout"
    MONETIZATION_ANALYZE = "monetization_analyze"
    MONETIZATION_OPTIMIZE = "monetization_optimize"
    
    # Collaboration & Team
    COLLABORATION_INVITE = "collaboration_invite"
    COLLABORATION_SHARE = "collaboration_share"
    COLLABORATION_PERMISSION = "collaboration_permission"
    COLLABORATION_WORKFLOW = "collaboration_workflow"
    COLLABORATION_COMMUNICATE = "collaboration_communicate"
    
    # Analytics & Insights
    ANALYTICS_PERFORMANCE = "analytics_performance"
    ANALYTICS_AUDIENCE = "analytics_audience"
    ANALYTICS_TRENDS = "analytics_trends"
    ANALYTICS_COMPARE = "analytics_compare"
    ANALYTICS_FORECAST = "analytics_forecast"
    
    # Platform Operations
    PLATFORM_DISTRIBUTE = "platform_distribute"
    PLATFORM_SCHEDULE = "platform_schedule"
    PLATFORM_OPTIMIZE = "platform_optimize"
    PLATFORM_SYNC = "platform_sync"
    PLATFORM_CONFIGURE = "platform_configure"
    
    # General Assistance
    HELP_SUPPORT = "help_support"
    HELP_TUTORIAL = "help_tutorial"
    HELP_TROUBLESHOOT = "help_troubleshoot"
    
    # Undefined/Unknown
    UNKNOWN = "unknown"


@dataclass
class IntentConfidence:
    """Intent classification confidence metrics"""
    primary_score: float
    secondary_score: Optional[float] = None
    uncertainty: float = 0.0
    calibrated_confidence: float = 0.0
    entropy: float = 0.0
    model_agreement: float = 1.0


@dataclass
class ClassificationResult:
    """Complete intent classification result"""
    primary_intent: IntentCategory
    secondary_intent: Optional[IntentCategory] = None
    confidence: IntentConfidence = field(default_factory=IntentConfidence)
    intent_parameters: Dict[str, Any] = field(default_factory=dict)
    context_factors: Dict[str, float] = field(default_factory=dict)
    processing_time: float = 0.0
    model_version: str = "1.0.0"
    timestamp: datetime = field(default_factory=datetime.now)


class IntentClassifier(BaseService):
    """
    Advanced intent classification engine for creative industry workflows
    
    Features:
    - Multi-model ensemble classification
    - Contextual intent understanding
    - Confidence calibration and uncertainty quantification
    - Real-time performance optimization
    - Adaptive learning capabilities
    """
    
    def __init__(self, config: IntentRecognitionConfig):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("intent_classifier")
        
        # Model components
        self.transformer_model = None
        self.transformer_tokenizer = None
        self.ensemble_models = {}
        self.tfidf_vectorizer = None
        self.nlp_processor = None
        
        # Performance tracking
        self.classification_cache = {}
        self.model_performance = {}
        self.calibration_data = []
        
        # Initialize components
        self._initialize_models()
        
    async def _initialize_models(self) -> None:
        """Initialize all classification models and components"""
        try:
            self.logger.info("Initializing intent classification models...")
            
            # Load transformer model for primary classification
            await self._load_transformer_model()
            
            # Initialize ensemble models
            await self._load_ensemble_models()
            
            # Load text processing components
            await self._load_text_processors()
            
            # Load calibration data
            await self._load_calibration_data()
            
            self.logger.info("Intent classification models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize models: {str(e)}")
            raise ModelLoadError(f"Model initialization failed: {str(e)}")
    
    async def _load_transformer_model(self) -> None:
        """Load fine-tuned transformer model for intent classification"""
        try:
            model_name = self.config.transformer_model_name
            
            self.transformer_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.transformer_model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                num_labels=len(IntentCategory),
                output_attentions=True,
                output_hidden_states=True
            )
            
            # Set to evaluation mode
            self.transformer_model.eval()
            
            # Load custom fine-tuned weights if available
            if self.config.custom_model_path:
                checkpoint = torch.load(self.config.custom_model_path, map_location='cpu')
                self.transformer_model.load_state_dict(checkpoint['model_state_dict'])
                
            self.logger.info(f"Transformer model loaded: {model_name}")
            
        except Exception as e:
            raise ModelLoadError(f"Failed to load transformer model: {str(e)}")
    
    async def _load_ensemble_models(self) -> None:
        """Load ensemble models for improved accuracy"""
        try:
            # TF-IDF + Random Forest for fallback classification
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=self.config.tfidf_max_features,
                ngram_range=(1, 3),
                stop_words='english'
            )
            
            self.ensemble_models['random_forest'] = RandomForestClassifier(
                n_estimators=self.config.rf_n_estimators,
                max_depth=self.config.rf_max_depth,
                random_state=42
            )
            
            # Load pre-trained ensemble models if available
            if self.config.ensemble_models_path:
                with open(self.config.ensemble_models_path, 'rb') as f:
                    ensemble_data = pickle.load(f)
                    self.ensemble_models.update(ensemble_data.get('models', {}))
                    self.tfidf_vectorizer = ensemble_data.get('vectorizer', self.tfidf_vectorizer)
            
            self.logger.info("Ensemble models loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to load ensemble models: {str(e)}")
    
    async def _load_text_processors(self) -> None:
        """Load NLP processing components"""
        try:
            # Load spaCy model for text preprocessing
            self.nlp_processor = spacy.load(self.config.spacy_model)
            
            # Add custom components for creative industry entities
            if 'creative_entity_ruler' not in self.nlp_processor.pipe_names:
                ruler = self.nlp_processor.add_pipe('entity_ruler', name='creative_entity_ruler')
                creative_patterns = self._get_creative_entity_patterns()
                ruler.add_patterns(creative_patterns)
            
            self.logger.info("Text processors loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to load text processors: {str(e)}")
    
    async def _load_calibration_data(self) -> None:
        """Load confidence calibration data"""
        try:
            if self.config.calibration_data_path:
                with open(self.config.calibration_data_path, 'rb') as f:
                    self.calibration_data = pickle.load(f)
                    
                self.logger.info("Calibration data loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to load calibration data: {str(e)}")
    
    def _get_creative_entity_patterns(self) -> List[Dict[str, Any]]:
        """Get entity patterns specific to creative industry"""
        return [
            # Music-related patterns
            {"label": "MUSIC_GENRE", "pattern": [{"LOWER": {"IN": ["pop", "rock", "jazz", "classical", "electronic", "hip-hop", "country"]}}]},
            {"label": "INSTRUMENT", "pattern": [{"LOWER": {"IN": ["guitar", "piano", "drums", "violin", "saxophone", "bass"]}}]},
            
            # Platform patterns
            {"label": "PLATFORM", "pattern": [{"LOWER": {"IN": ["spotify", "youtube", "instagram", "tiktok", "soundcloud", "bandcamp"]}}]},
            
            # Content type patterns
            {"label": "CONTENT_TYPE", "pattern": [{"LOWER": {"IN": ["song", "track", "album", "playlist", "video", "photo", "post", "story"]}}]},
            
            # Action patterns
            {"label": "ACTION", "pattern": [{"LOWER": {"IN": ["upload", "share", "protect", "monetize", "collaborate", "analyze"]}}]}
        ]
    
    @cache_manager.cached(ttl=300)
    async def classify_intent(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> ClassificationResult:
        """
        Classify user intent from text input
        
        Args:
            text: Input text to classify
            context: Optional conversation context
            user_id: User identifier for personalization
            session_id: Session identifier for context tracking
            
        Returns:
            ClassificationResult with intent and confidence scores
        """
        start_time = datetime.now()
        
        try:
            # Validate input
            if not text or not text.strip():
                raise ClassificationError("Empty input text provided")
            
            # Preprocess text
            processed_text = await self._preprocess_text(text)
            
            # Extract features
            features = await self._extract_features(processed_text, context)
            
            # Primary classification using transformer
            primary_result = await self._classify_with_transformer(processed_text, features)
            
            # Secondary classification using ensemble
            secondary_result = await self._classify_with_ensemble(processed_text, features)
            
            # Combine results and calculate confidence
            combined_result = await self._combine_classifications(
                primary_result, secondary_result, features
            )
            
            # Add context factors
            combined_result.context_factors = await self._analyze_context_factors(
                text, context, user_id, session_id
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            combined_result.processing_time = processing_time
            
            # Update metrics
            await self._update_metrics(combined_result, processing_time)
            
            return combined_result
            
        except Exception as e:
            self.logger.error(f"Intent classification failed: {str(e)}")
            raise ClassificationError(f"Classification failed: {str(e)}")
    
    async def _preprocess_text(self, text: str) -> str:
        """Preprocess input text for classification"""
        try:
            # Basic cleaning
            text = text.strip().lower()
            
            # Remove excessive whitespace
            text = ' '.join(text.split())
            
            # Process with spaCy if available
            if self.nlp_processor:
                doc = self.nlp_processor(text)
                # Extract meaningful tokens (excluding stop words, punctuation)
                tokens = [token.lemma_ for token in doc 
                         if not token.is_stop and not token.is_punct and token.is_alpha]
                text = ' '.join(tokens)
            
            return text
            
        except Exception as e:
            self.logger.warning(f"Text preprocessing failed: {str(e)}")
            return text.strip().lower()
    
    async def _extract_features(
        self, 
        text: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract classification features from text and context"""
        features = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'has_question': '?' in text,
            'has_exclamation': '!' in text,
            'context_features': {}
        }
        
        # Extract context features if available
        if context:
            features['context_features'] = {
                'previous_intent': context.get('previous_intent'),
                'conversation_stage': context.get('conversation_stage'),
                'user_type': context.get('user_type'),
                'platform_context': context.get('platform_context')
            }
        
        # Extract entity features
        if self.nlp_processor:
            doc = self.nlp_processor(text)
            features['entities'] = {
                'music_genre_mentioned': any(ent.label_ == 'MUSIC_GENRE' for ent in doc.ents),
                'platform_mentioned': any(ent.label_ == 'PLATFORM' for ent in doc.ents),
                'content_type_mentioned': any(ent.label_ == 'CONTENT_TYPE' for ent in doc.ents),
                'action_mentioned': any(ent.label_ == 'ACTION' for ent in doc.ents)
            }
        
        return features
    
    async def _classify_with_transformer(
        self, 
        text: str, 
        features: Dict[str, Any]
    ) -> Tuple[IntentCategory, float]:
        """Classify intent using transformer model"""
        try:
            if not self.transformer_model or not self.transformer_tokenizer:
                raise ModelLoadError("Transformer model not loaded")
            
            # Tokenize input
            inputs = self.transformer_tokenizer(
                text,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=self.config.max_sequence_length
            )
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.transformer_model(**inputs)
                logits = outputs.logits
                probabilities = F.softmax(logits, dim=-1)
            
            # Get top prediction
            top_prob, top_idx = torch.max(probabilities, dim=-1)
            predicted_intent = list(IntentCategory)[top_idx.item()]
            confidence = top_prob.item()
            
            return predicted_intent, confidence
            
        except Exception as e:
            self.logger.error(f"Transformer classification failed: {str(e)}")
            return IntentCategory.UNKNOWN, 0.5
    
    async def _classify_with_ensemble(
        self, 
        text: str, 
        features: Dict[str, Any]
    ) -> Tuple[Optional[IntentCategory], float]:
        """Classify intent using ensemble models"""
        try:
            if not self.ensemble_models or not self.tfidf_vectorizer:
                return None, 0.0
            
            # Vectorize text
            text_vector = self.tfidf_vectorizer.transform([text])
            
            # Get predictions from ensemble models
            predictions = []
            confidences = []
            
            for model_name, model in self.ensemble_models.items():
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(text_vector)
                    pred_idx = np.argmax(proba)
                    confidence = proba[0][pred_idx]
                    
                    if pred_idx < len(IntentCategory):
                        predicted_intent = list(IntentCategory)[pred_idx]
                        predictions.append(predicted_intent)
                        confidences.append(confidence)
            
            if predictions:
                # Return most confident prediction
                best_idx = np.argmax(confidences)
                return predictions[best_idx], confidences[best_idx]
            
            return None, 0.0
            
        except Exception as e:
            self.logger.error(f"Ensemble classification failed: {str(e)}")
            return None, 0.0
    
    async def _combine_classifications(
        self,
        primary_result: Tuple[IntentCategory, float],
        secondary_result: Tuple[Optional[IntentCategory], float],
        features: Dict[str, Any]
    ) -> ClassificationResult:
        """Combine primary and secondary classification results"""
        
        primary_intent, primary_confidence = primary_result
        secondary_intent, secondary_confidence = secondary_result
        
        # Calculate combined confidence
        if secondary_intent and secondary_confidence > 0:
            # Weight primary model higher
            combined_confidence = (0.7 * primary_confidence + 0.3 * secondary_confidence)
            model_agreement = 1.0 if primary_intent == secondary_intent else 0.5
        else:
            combined_confidence = primary_confidence
            model_agreement = 1.0
        
        # Calculate uncertainty metrics
        entropy = -primary_confidence * np.log(primary_confidence + 1e-10)
        uncertainty = 1.0 - combined_confidence
        
        # Calibrate confidence if calibration data available
        calibrated_confidence = self._calibrate_confidence(
            combined_confidence, primary_intent
        )
        
        # Create confidence object
        confidence = IntentConfidence(
            primary_score=primary_confidence,
            secondary_score=secondary_confidence if secondary_intent else None,
            uncertainty=uncertainty,
            calibrated_confidence=calibrated_confidence,
            entropy=entropy,
            model_agreement=model_agreement
        )
        
        # Create result
        result = ClassificationResult(
            primary_intent=primary_intent,
            secondary_intent=secondary_intent,
            confidence=confidence,
            intent_parameters=self._extract_intent_parameters(features),
            model_version=self.config.model_version
        )
        
        return result
    
    def _calibrate_confidence(self, confidence: float, intent: IntentCategory) -> float:
        """Calibrate confidence score using historical data"""
        try:
            if not self.calibration_data:
                return confidence
            
            # Simple isotonic regression calibration
            # In production, this would use more sophisticated calibration
            intent_name = intent.value
            if intent_name in self.calibration_data:
                calibration_curve = self.calibration_data[intent_name]
                # Linear interpolation for calibration
                for threshold, calibrated in calibration_curve:
                    if confidence <= threshold:
                        return calibrated
            
            return confidence
            
        except Exception as e:
            self.logger.warning(f"Confidence calibration failed: {str(e)}")
            return confidence
    
    def _extract_intent_parameters(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Extract parameters specific to the identified intent"""
        parameters = {}
        
        # Extract relevant entities and context
        if 'entities' in features:
            parameters.update(features['entities'])
        
        if 'context_features' in features:
            parameters['context'] = features['context_features']
        
        # Add text-based parameters
        parameters['text_metrics'] = {
            'length': features.get('text_length', 0),
            'word_count': features.get('word_count', 0),
            'has_question': features.get('has_question', False),
            'has_exclamation': features.get('has_exclamation', False)
        }
        
        return parameters
    
    async def _analyze_context_factors(
        self,
        text: str,
        context: Optional[Dict[str, Any]],
        user_id: Optional[str],
        session_id: Optional[str]
    ) -> Dict[str, float]:
        """Analyze contextual factors that influence intent classification"""
        
        factors = {
            'text_clarity': self._calculate_text_clarity(text),
            'context_relevance': 0.5,  # Default when no context
            'user_consistency': 0.5,   # Default when no user history
            'session_coherence': 0.5   # Default when no session history
        }
        
        # Analyze context relevance
        if context:
            factors['context_relevance'] = self._calculate_context_relevance(context)
        
        # Analyze user consistency (would require user history lookup)
        if user_id:
            factors['user_consistency'] = await self._calculate_user_consistency(user_id, text)
        
        # Analyze session coherence (would require session history lookup)  
        if session_id:
            factors['session_coherence'] = await self._calculate_session_coherence(session_id, text)
        
        return factors
    
    def _calculate_text_clarity(self, text: str) -> float:
        """Calculate clarity score for input text"""
        try:
            # Simple heuristics for text clarity
            words = text.split()
            
            if len(words) == 0:
                return 0.0
            
            # Factors that increase clarity
            clarity_score = 0.5  # Base score
            
            # Length factor (too short or too long reduces clarity)
            if 3 <= len(words) <= 20:
                clarity_score += 0.2
            
            # Question marks indicate clear intent
            if '?' in text:
                clarity_score += 0.1
            
            # Common action words increase clarity
            action_words = ['upload', 'download', 'create', 'delete', 'share', 'protect', 'analyze']
            if any(word in text.lower() for word in action_words):
                clarity_score += 0.2
            
            return min(1.0, clarity_score)
            
        except Exception:
            return 0.5
    
    def _calculate_context_relevance(self, context: Dict[str, Any]) -> float:
        """Calculate relevance of provided context"""
        relevance = 0.5  # Base score
        
        # Check for relevant context fields
        relevant_fields = ['previous_intent', 'conversation_stage', 'user_type', 'platform_context']
        provided_fields = sum(1 for field in relevant_fields if context.get(field))
        
        relevance += (provided_fields / len(relevant_fields)) * 0.5
        
        return min(1.0, relevance)
    
    async def _calculate_user_consistency(self, user_id: str, text: str) -> float:
        """Calculate user intent consistency (placeholder for user history analysis)"""
        # In production, this would analyze user's historical intent patterns
        return 0.7  # Placeholder value
    
    async def _calculate_session_coherence(self, session_id: str, text: str) -> float:
        """Calculate session coherence score (placeholder for session analysis)"""
        # In production, this would analyze session conversation flow
        return 0.6  # Placeholder value
    
    async def _update_metrics(self, result: ClassificationResult, processing_time: float) -> None:
        """Update performance metrics"""
        try:
            # Record classification metrics
            self.metrics.record_counter('classifications_total')
            self.metrics.record_histogram('classification_time', processing_time)
            self.metrics.record_gauge('confidence_score', result.confidence.primary_score)
            self.metrics.record_counter(f'intent_{result.primary_intent.value}')
            
            # Update model performance tracking
            intent_name = result.primary_intent.value
            if intent_name not in self.model_performance:
                self.model_performance[intent_name] = {
                    'count': 0,
                    'avg_confidence': 0.0,
                    'avg_processing_time': 0.0
                }
            
            perf = self.model_performance[intent_name]
            perf['count'] += 1
            perf['avg_confidence'] = (
                (perf['avg_confidence'] * (perf['count'] - 1) + result.confidence.primary_score) 
                / perf['count']
            )
            perf['avg_processing_time'] = (
                (perf['avg_processing_time'] * (perf['count'] - 1) + processing_time)
                / perf['count']
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to update metrics: {str(e)}")
    
    async def batch_classify(
        self,
        texts: List[str],
        contexts: Optional[List[Dict[str, Any]]] = None,
        user_ids: Optional[List[str]] = None
    ) -> List[ClassificationResult]:
        """
        Classify multiple intents in batch for improved performance
        
        Args:
            texts: List of input texts
            contexts: Optional list of contexts
            user_ids: Optional list of user identifiers
            
        Returns:
            List of classification results
        """
        try:
            # Prepare inputs
            if contexts is None:
                contexts = [None] * len(texts)
            if user_ids is None:
                user_ids = [None] * len(texts)
            
            # Create classification tasks
            tasks = [
                self.classify_intent(text, context, user_id)
                for text, context, user_id in zip(texts, contexts, user_ids)
            ]
            
            # Execute batch classification
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"Batch classification error: {str(result)}")
                    # Create error result
                    error_result = ClassificationResult(
                        primary_intent=IntentCategory.UNKNOWN,
                        confidence=IntentConfidence(primary_score=0.0)
                    )
                    processed_results.append(error_result)
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Batch classification failed: {str(e)}")
            raise ClassificationError(f"Batch classification failed: {str(e)}")
    
    async def get_classification_confidence_distribution(
        self,
        intent: IntentCategory,
        time_window_hours: int = 24
    ) -> Dict[str, float]:
        """Get confidence score distribution for specific intent"""
        try:
            # In production, this would query historical data
            # Placeholder implementation
            return {
                'mean_confidence': 0.85,
                'std_confidence': 0.12,
                'min_confidence': 0.45,
                'max_confidence': 0.98,
                'sample_count': 150
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get confidence distribution: {str(e)}")
            return {}
    
    async def update_model_performance(
        self,
        feedback_data: List[Dict[str, Any]]
    ) -> None:
        """Update model performance based on user feedback"""
        try:
            # Process feedback for model improvement
            for feedback in feedback_data:
                text = feedback.get('text')
                predicted_intent = feedback.get('predicted_intent')
                actual_intent = feedback.get('actual_intent')
                user_rating = feedback.get('rating')
                
                if all([text, predicted_intent, actual_intent]):
                    # Store feedback for model retraining
                    feedback_entry = {
                        'text': text,
                        'predicted': predicted_intent,
                        'actual': actual_intent,
                        'rating': user_rating,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # In production, this would be stored in a feedback database
                    self.logger.info(f"Feedback recorded: {feedback_entry}")
            
        except Exception as e:
            self.logger.error(f"Failed to update model performance: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models and performance"""
        return {
            'transformer_model': self.config.transformer_model_name,
            'model_version': self.config.model_version,
            'ensemble_models': list(self.ensemble_models.keys()),
            'supported_intents': [intent.value for intent in IntentCategory],
            'performance_metrics': self.model_performance,
            'cache_size': len(self.classification_cache),
            'initialized': self.transformer_model is not None
        }
