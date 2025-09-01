"""Intent Recognizer - Advanced Intent Detection System
===================================================

Advanced AI-powered intent recognition system for understanding user intentions,
goals, and purposes in text content with high accuracy.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import json

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers library not available. Intent recognition will use fallback methods.")

from .config import NLPAgentConfig, default_config

# Setup logging
logger = logging.getLogger(__name__)

class IntentCategory(Enum):
    """Main intent categories"""
    INFORMATIONAL = "informational"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"
    COMMERCIAL = "commercial"
    SOCIAL = "social"
    ENTERTAINMENT = "entertainment"
    SUPPORT = "support"
    PERSONAL = "personal"

class IntentType(Enum):
    """Specific intent types"""
    QUESTION = "question"
    REQUEST = "request"
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"
    SUGGESTION = "suggestion"
    ANNOUNCEMENT = "announcement"
    INSTRUCTION = "instruction"
    INVITATION = "invitation"
    OFFER = "offer"
    PURCHASE = "purchase"
    BOOKING = "booking"
    SEARCH = "search"
    COMPARISON = "comparison"
    REVIEW = "review"
    SHARING = "sharing"

@dataclass
class IntentScore:
    """Individual intent detection score"""
    intent: str
    category: str
    confidence: float
    keywords: List[str] = field(default_factory=list)
    context_clues: List[str] = field(default_factory=list)

@dataclass
class IntentResult:
    """Complete intent recognition result"""
    text: str
    primary_intent: str
    primary_category: str
    confidence: float
    intent_scores: List[IntentScore] = field(default_factory=list)
    urgency_level: str = "medium"  # low, medium, high
    emotion_context: Optional[str] = None
    target_audience: Optional[str] = None
    action_required: bool = False
    response_expected: bool = False
    temporal_context: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class IntentRecognizer:
    """
    Advanced AI-powered intent recognition system for understanding user intentions,
    goals, and purposes in text content.
    """
    
    def __init__(self, config: Optional[NLPAgentConfig] = None):
        """Initialize Intent Recognizer"""
        self.config = config or default_config
        self.models = {}
        self.pipelines = {}
        self.intent_patterns = self._load_intent_patterns()
        self.context_analyzers = self._load_context_analyzers()
        
        self._initialize_models()
    
    def _load_intent_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Load patterns for intent recognition"""
        return {
            "question": {
                "patterns": [
                    r'\b(what|how|why|where|when|who|which|whose)\b',
                    r'\?$',
                    r'\b(can you|could you|would you|do you know)\b',
                    r'\b(is it|are there|does it|will it)\b'
                ],
                "keywords": ["question", "ask", "wonder", "curious", "explain", "tell me"]
            },
            "request": {
                "patterns": [
                    r'\b(please|could you|would you|can you)\b',
                    r'\b(help|assist|support|show me)\b',
                    r'\b(need|want|require|wish)\b',
                    r'\b(send|give|provide|share)\b'
                ],
                "keywords": ["request", "need", "want", "please", "help", "assist"]
            },
            "complaint": {
                "patterns": [
                    r'\b(problem|issue|trouble|error|bug|wrong)\b',
                    r'\b(not working|broken|failed|disappointed)\b',
                    r'\b(terrible|awful|horrible|worst|bad)\b',
                    r'\b(frustrated|angry|upset|annoyed)\b'
                ],
                "keywords": ["complaint", "problem", "issue", "disappointed", "frustrated"]
            },
            "compliment": {
                "patterns": [
                    r'\b(great|excellent|amazing|wonderful|fantastic)\b',
                    r'\b(love|like|enjoy|appreciate|impressed)\b',
                    r'\b(good job|well done|congratulations|awesome)\b',
                    r'\b(thank you|thanks|grateful|pleased)\b'
                ],
                "keywords": ["compliment", "praise", "thanks", "appreciate", "love"]
            },
            "purchase": {
                "patterns": [
                    r'\b(buy|purchase|order|pay|payment)\b',
                    r'\b(price|cost|how much|expensive|cheap)\b',
                    r'\b(shop|store|cart|checkout|billing)\b',
                    r'\b(discount|sale|offer|deal|promotion)\b'
                ],
                "keywords": ["buy", "purchase", "order", "price", "cost", "shop"]
            },
            "booking": {
                "patterns": [
                    r'\b(book|reserve|schedule|appointment)\b',
                    r'\b(available|availability|free|slot)\b',
                    r'\b(date|time|when|calendar|meeting)\b',
                    r'\b(confirm|cancel|reschedule|change)\b'
                ],
                "keywords": ["book", "reserve", "schedule", "appointment", "availability"]
            },
            "search": {
                "patterns": [
                    r'\b(find|search|look for|locate)\b',
                    r'\b(where is|where can|how to find)\b',
                    r'\b(directory|list|catalog|database)\b',
                    r'\b(browse|explore|discover|navigate)\b'
                ],
                "keywords": ["find", "search", "look for", "locate", "browse"]
            },
            "comparison": {
                "patterns": [
                    r'\b(compare|versus|vs|difference|better)\b',
                    r'\b(which is|what is the difference|pros and cons)\b',
                    r'\b(similar|different|same|alternative)\b',
                    r'\b(recommend|suggest|advise|choose)\b'
                ],
                "keywords": ["compare", "difference", "better", "recommend", "choose"]
            },
            "sharing": {
                "patterns": [
                    r'\b(share|post|publish|upload|submit)\b',
                    r'\b(tell everyone|announce|broadcast|spread)\b',
                    r'\b(social media|facebook|twitter|instagram)\b',
                    r'\b(experience|story|news|update)\b'
                ],
                "keywords": ["share", "post", "announce", "social", "experience"]
            },
            "instruction": {
                "patterns": [
                    r'\b(how to|step by step|tutorial|guide)\b',
                    r'\b(first|second|next|then|finally)\b',
                    r'\b(follow|do this|click|select|enter)\b',
                    r'\b(instruction|manual|procedure|process)\b'
                ],
                "keywords": ["how to", "tutorial", "guide", "instruction", "step"]
            }
        }
    
    def _load_context_analyzers(self) -> Dict[str, List[str]]:
        """Load context analyzers for intent refinement"""
        return {
            "urgency": {
                "high": ["urgent", "asap", "immediately", "emergency", "critical", "now"],
                "medium": ["soon", "today", "this week", "please", "important"],
                "low": ["sometime", "eventually", "when possible", "no rush", "later"]
            },
            "emotion": {
                "positive": ["happy", "excited", "pleased", "satisfied", "great", "love"],
                "negative": ["frustrated", "angry", "disappointed", "upset", "terrible"],
                "neutral": ["okay", "fine", "normal", "standard", "regular"]
            },
            "audience": {
                "professional": ["colleagues", "team", "business", "corporate", "formal"],
                "personal": ["friends", "family", "personal", "private", "individual"],
                "public": ["everyone", "public", "community", "audience", "followers"]
            },
            "temporal": {
                "immediate": ["now", "right now", "immediately", "asap", "currently"],
                "near_future": ["today", "tomorrow", "this week", "soon", "shortly"],
                "future": ["next week", "next month", "later", "someday", "eventually"]
            }
        }
    
    def _initialize_models(self):
        """Initialize intent recognition models"""
        try:
            if TRANSFORMERS_AVAILABLE:
                # Intent classification model
                self.pipelines["intent"] = pipeline(
                    "text-classification",
                    model="microsoft/DialoGPT-medium",  # General conversational model
                    device=self._get_device(),
                    return_all_scores=True
                )
                
                # Question-answering for intent refinement
                try:
                    self.pipelines["qa"] = pipeline(
                        "question-answering",
                        model="deepset/roberta-base-squad2",
                        device=self._get_device()
                    )
                except:
                    logger.warning("Question-answering model not available")
                
                logger.info("Intent recognition models initialized")
            else:
                self._setup_fallback_methods()
                
        except Exception as e:
            logger.error(f"Failed to initialize intent models: {e}")
            self._setup_fallback_methods()
    
    def _setup_fallback_methods(self):
        """Setup fallback methods for intent recognition"""
        logger.info("Setting up intent recognition fallback methods")
        self.fallback_mode = True
        
        # Compile regex patterns for better performance
        self.compiled_patterns = {}
        for intent, data in self.intent_patterns.items():
            self.compiled_patterns[intent] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in data["patterns"]
            ]
    
    def _get_device(self) -> int:
        """Get optimal device for model execution"""
        if self.config.performance.enable_gpu and TRANSFORMERS_AVAILABLE:
            try:
                if torch.cuda.is_available():
                    return 0  # Use first GPU
            except:
                pass
        return -1  # Use CPU
    
    async def recognize_intent(
        self,
        text: Union[str, List[str]],
        include_context: bool = True,
        analyze_urgency: bool = True,
        detect_emotion: bool = True
    ) -> Union[IntentResult, List[IntentResult]]:
        """
        Recognize intent in text
        
        Args:
            text: Text or list of texts to analyze
            include_context: Whether to include contextual analysis
            analyze_urgency: Whether to analyze urgency level
            detect_emotion: Whether to detect emotional context
        
        Returns:
            IntentResult or list of results
        """
        start_time = asyncio.get_event_loop().time()
        
        # Handle batch processing
        is_batch = isinstance(text, list)
        texts = text if is_batch else [text]
        
        results = []
        
        try:
            for single_text in texts:
                result = await self._recognize_single_text(
                    single_text,
                    include_context,
                    analyze_urgency,
                    detect_emotion
                )
                results.append(result)
            
            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            for result in results:
                result.processing_time = processing_time / len(results)
            
            return results if is_batch else results[0]
            
        except Exception as e:
            logger.error(f"Intent recognition failed: {e}")
            raise
    
    async def _recognize_single_text(
        self,
        text: str,
        include_context: bool,
        analyze_urgency: bool,
        detect_emotion: bool
    ) -> IntentResult:
        """Recognize intent for a single text"""
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")
        
        result = IntentResult(
            text=text,
            primary_intent="unknown",
            primary_category="personal",
            confidence=0.0
        )
        
        try:
            # Primary intent recognition
            if hasattr(self, 'fallback_mode') and self.fallback_mode:
                await self._recognize_with_patterns(text, result)
            else:
                await self._recognize_with_transformer(text, result)
            
            # Context analysis
            if include_context:
                await self._analyze_context(text, result)
            
            # Urgency analysis
            if analyze_urgency:
                result.urgency_level = await self._analyze_urgency(text)
            
            # Emotion context
            if detect_emotion:
                result.emotion_context = await self._detect_emotion_context(text)
            
            # Additional analysis
            result.target_audience = await self._detect_target_audience(text)
            result.action_required = await self._requires_action(text)
            result.response_expected = await self._expects_response(text)
            result.temporal_context = await self._analyze_temporal_context(text)
            
            # Add metadata
            result.metadata = {
                "text_length": len(text),
                "word_count": len(text.split()),
                "question_marks": text.count("?"),
                "exclamation_marks": text.count("!"),
                "recognition_method": "transformer" if not hasattr(self, 'fallback_mode') else "pattern_based"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Single text intent recognition failed: {e}")
            result.metadata["error"] = str(e)
            return result
    
    async def _recognize_with_transformer(self, text: str, result: IntentResult):
        """Recognize intent using transformer model"""
        try:
            # Use zero-shot classification for intent recognition
            intent_pipeline = self.pipelines.get("intent")
            if intent_pipeline:
                # Define candidate intents
                candidate_intents = [intent.value for intent in IntentType]
                
                predictions = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: intent_pipeline(text, candidate_intents)
                )
                
                if predictions:
                    # Process results
                    intent_scores = []
                    for pred in predictions:
                        intent = pred["label"]
                        confidence = pred["score"]
                        
                        intent_scores.append(IntentScore(
                            intent=intent,
                            category=self._map_intent_to_category(intent),
                            confidence=confidence,
                            keywords=self._extract_intent_keywords(text, intent)
                        ))
                    
                    result.intent_scores = intent_scores
                    if intent_scores:
                        result.primary_intent = intent_scores[0].intent
                        result.primary_category = intent_scores[0].category
                        result.confidence = intent_scores[0].confidence
            
        except Exception as e:
            logger.error(f"Transformer intent recognition failed: {e}")
            # Fall back to pattern-based recognition
            await self._recognize_with_patterns(text, result)
    
    async def _recognize_with_patterns(self, text: str, result: IntentResult):
        """Recognize intent using pattern-based approach"""
        text_lower = text.lower()
        intent_scores = {}
        
        # Check each intent pattern
        for intent, patterns in self.compiled_patterns.items():
            score = 0.0
            matched_keywords = []
            
            # Pattern matching
            for pattern in patterns:
                matches = pattern.findall(text)
                score += len(matches) * 0.3
                matched_keywords.extend(matches)
            
            # Keyword matching
            keywords = self.intent_patterns[intent]["keywords"]
            for keyword in keywords:
                if keyword in text_lower:
                    score += 0.4
                    matched_keywords.append(keyword)
            
            # Normalize score
            if score > 0:
                intent_scores[intent] = {
                    "score": min(score, 1.0),
                    "keywords": list(set(matched_keywords))
                }
        
        # Create intent scores
        sorted_scores = sorted(
            intent_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        result.intent_scores = [
            IntentScore(
                intent=intent,
                category=self._map_intent_to_category(intent),
                confidence=data["score"],
                keywords=data["keywords"]
            )
            for intent, data in sorted_scores[:5]  # Top 5
        ]
        
        if sorted_scores:
            result.primary_intent = sorted_scores[0][0]
            result.primary_category = self._map_intent_to_category(sorted_scores[0][0])
            result.confidence = sorted_scores[0][1]["score"]
        else:
            result.primary_intent = "sharing"  # Default intent
            result.primary_category = "social"
            result.confidence = 0.1
    
    def _map_intent_to_category(self, intent: str) -> str:
        """Map specific intent to general category"""
        intent_to_category = {
            "question": "informational",
            "request": "support",
            "complaint": "support",
            "compliment": "social",
            "suggestion": "social",
            "announcement": "informational",
            "instruction": "informational",
            "invitation": "social",
            "offer": "commercial",
            "purchase": "transactional",
            "booking": "transactional",
            "search": "navigational",
            "comparison": "commercial",
            "review": "social",
            "sharing": "social"
        }
        
        return intent_to_category.get(intent, "personal")
    
    def _extract_intent_keywords(self, text: str, intent: str) -> List[str]:
        """Extract keywords that match a specific intent"""
        if intent not in self.intent_patterns:
            return []
        
        text_lower = text.lower()
        keywords = self.intent_patterns[intent]["keywords"]
        
        return [keyword for keyword in keywords if keyword in text_lower]
    
    async def _analyze_context(self, text: str, result: IntentResult):
        """Analyze contextual information"""
        # This method can be expanded with more sophisticated context analysis
        context_info = {}
        
        # Check for context clues
        if "?" in text:
            context_info["has_question"] = True
        
        if "!" in text:
            context_info["has_exclamation"] = True
        
        if any(word in text.lower() for word in ["please", "thanks", "thank you"]):
            context_info["polite"] = True
        
        result.metadata.update(context_info)
    
    async def _analyze_urgency(self, text: str) -> str:
        """Analyze urgency level of the text"""
        text_lower = text.lower()
        urgency_indicators = self.context_analyzers["urgency"]
        
        # Check for urgency indicators
        for level, indicators in urgency_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return level
        
        # Default to medium urgency
        return "medium"
    
    async def _detect_emotion_context(self, text: str) -> Optional[str]:
        """Detect emotional context of the text"""
        text_lower = text.lower()
        emotion_indicators = self.context_analyzers["emotion"]
        
        emotion_scores = {}
        for emotion, indicators in emotion_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            return max(emotion_scores, key=emotion_scores.get)
        
        return None
    
    async def _detect_target_audience(self, text: str) -> Optional[str]:
        """Detect target audience of the text"""
        text_lower = text.lower()
        audience_indicators = self.context_analyzers["audience"]
        
        for audience, indicators in audience_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return audience
        
        return "general"
    
    async def _requires_action(self, text: str) -> bool:
        """Determine if text requires action"""
        action_indicators = [
            "please", "help", "fix", "solve", "do", "make", "create",
            "send", "give", "provide", "show", "tell", "explain"
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in action_indicators)
    
    async def _expects_response(self, text: str) -> bool:
        """Determine if text expects a response"""
        response_indicators = [
            "?", "what", "how", "why", "when", "where", "who",
            "please respond", "let me know", "get back to me",
            "reply", "answer", "feedback"
        ]
        
        return any(indicator in text.lower() for indicator in response_indicators)
    
    async def _analyze_temporal_context(self, text: str) -> Optional[str]:
        """Analyze temporal context of the text"""
        text_lower = text.lower()
        temporal_indicators = self.context_analyzers["temporal"]
        
        for timeframe, indicators in temporal_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return timeframe
        
        return None
    
    async def analyze_intent_confidence(self, text: str) -> Dict[str, float]:
        """Get confidence scores for all possible intents"""
        result = await self.recognize_intent(text)
        
        confidence_scores = {}
        for score in result.intent_scores:
            confidence_scores[score.intent] = score.confidence
        
        return confidence_scores
    
    async def compare_intents(
        self,
        text1: str,
        text2: str
    ) -> Dict[str, Any]:
        """Compare intents between two texts"""
        results = await self.recognize_intent([text1, text2])
        result1, result2 = results
        
        comparison = {
            "text1_intent": result1.primary_intent,
            "text2_intent": result2.primary_intent,
            "same_intent": result1.primary_intent == result2.primary_intent,
            "same_category": result1.primary_category == result2.primary_category,
            "confidence_difference": abs(result1.confidence - result2.confidence),
            "urgency_comparison": {
                "text1": result1.urgency_level,
                "text2": result2.urgency_level
            },
            "emotion_comparison": {
                "text1": result1.emotion_context,
                "text2": result2.emotion_context
            }
        }
        
        return comparison
    
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intent types"""
        return list(self.intent_patterns.keys())
    
    def get_intent_patterns(self, intent: str) -> Dict[str, Any]:
        """Get patterns for a specific intent"""
        return self.intent_patterns.get(intent, {})
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        status = {
            "status": "healthy",
            "models_loaded": len(self.pipelines),
            "patterns_loaded": len(self.intent_patterns),
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "fallback_mode": hasattr(self, 'fallback_mode') and self.fallback_mode
        }
        
        # Test basic functionality
        try:
            test_result = asyncio.run(self.recognize_intent("This is a test message."))
            status["test_result"] = "passed"
            status["test_intent"] = test_result.primary_intent
        except Exception as e:
            status["status"] = "degraded"
            status["error"] = str(e)
        
        return status
    
    def shutdown(self):
        """Shutdown the intent recognizer"""
        logger.info("Shutting down Intent Recognizer")
        
        # Clear models
        self.models.clear()
        self.pipelines.clear()
        if hasattr(self, 'compiled_patterns'):
            self.compiled_patterns.clear()
        
        # Clear GPU memory if using CUDA
        if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()

# Utility functions
def calculate_intent_similarity(result1: IntentResult, result2: IntentResult) -> float:
    """Calculate similarity between two intent results"""
    # Same intent
    if result1.primary_intent == result2.primary_intent:
        intent_sim = 1.0
    elif result1.primary_category == result2.primary_category:
        intent_sim = 0.7  # Same category but different intent
    else:
        intent_sim = 0.0
    
    # Confidence similarity
    confidence_sim = 1.0 - abs(result1.confidence - result2.confidence)
    
    # Context similarity
    context_sim = 0.5  # Default
    if result1.urgency_level == result2.urgency_level:
        context_sim += 0.2
    if result1.emotion_context == result2.emotion_context:
        context_sim += 0.3
    
    return (intent_sim + confidence_sim + context_sim) / 3.0

def extract_intent_features(result: IntentResult) -> Dict[str, Any]:
    """Extract key features from intent result"""
    return {
        "primary_intent": result.primary_intent,
        "primary_category": result.primary_category,
        "confidence": result.confidence,
        "urgency_level": result.urgency_level,
        "emotion_context": result.emotion_context,
        "action_required": result.action_required,
        "response_expected": result.response_expected,
        "temporal_context": result.temporal_context,
        "num_intent_scores": len(result.intent_scores)
    }
