"""Content Classifier - Advanced Content Categorization System
===========================================================

Advanced AI-powered content classification system for categorizing text content
across multiple domains with high accuracy and contextual understanding.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import re

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers library not available. Content classification will use fallback methods.")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline as SklearnPipeline
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from .config import NLPAgentConfig, default_config

# Setup logging
logger = logging.getLogger(__name__)

class ContentCategory(Enum):
    """Main content categories"""

    MUSIC = "music"
    ENTERTAINMENT = "entertainment"
    TECHNOLOGY = "technology"
    SPORTS = "sports"
    NEWS = "news"
    EDUCATION = "education"
    BUSINESS = "business"
    LIFESTYLE = "lifestyle"
    TRAVEL = "travel"
    FOOD = "food"
    FASHION = "fashion"
    HEALTH = "health"
    SCIENCE = "science"
    POLITICS = "politics"
    ARTS = "arts"
    GAMING = "gaming"
    SOCIAL = "social"
    PERSONAL = "personal"
    PROMOTIONAL = "promotional"
    REVIEW = "review"

class ContentTone(Enum):
    """Content tone classification"""

    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FORMAL = "formal"
    HUMOROUS = "humorous"
    SERIOUS = "serious"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    CONVERSATIONAL = "conversational"

class ContentIntent(Enum):
    """Content intent classification"""

    INFORM = "inform"
    ENTERTAIN = "entertain"
    PERSUADE = "persuade"
    SELL = "sell"
    EDUCATE = "educate"
    ENGAGE = "engage"
    ANNOUNCE = "announce"
    QUESTION = "question"
    SHARE = "share"
    REVIEW = "review"

@dataclass
class CategoryScore:
    """Individual category score"""
    category: str
    confidence: float
    subcategory: Optional[str] = None
    keywords: List[str] = field(default_factory=list)

@dataclass
class ClassificationResult:
    """
Complete content classification result"""
    text: str
    primary_category: str
    confidence: float
    category_scores: List[CategoryScore] = field(default_factory=list)
    tone: Optional[str] = None
    intent: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    content_quality_score: float = 0.0
    audience_target: Optional[str] = None
    content_safety: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class ContentClassifier:
    """
    Advanced AI-powered content classification system for categorizing text content
    across multiple domains with high accuracy and contextual understanding.
    """
    
    def __init__(self, config: Optional[NLPAgentConfig] = None):
        """
Initialize Content Classifier"""
        self.config = config or default_config
        self.models = {}
        self.pipelines = {}
        self.category_keywords = self._load_category_keywords()
        self.fallback_classifiers = {}
        
        self._initialize_models()
    
    def _load_category_keywords(self) -> Dict[str, Set[str]]:
        """
Load keyword sets for each category"""
        return {
            "music": {
                "song", "album", "artist", "band", "concert", "tour", "music", "melody",
                "lyrics", "beat", "rhythm", "sound", "acoustic", "genre", "playlist",
                "spotify", "streaming", "recording", "studio", "performance", "live",
                "guitar", "piano", "drums", "vocals", "harmony", "composition"
            },
            "entertainment": {
                "movie", "film", "tv", "show", "series", "episode", "actor", "actress",
                "celebrity", "entertainment", "cinema", "theater", "comedy", "drama",
                "netflix", "streaming", "premiere", "trailer", "review", "rating",
                "hollywood", "director", "producer", "script", "scene", "character"
            },
            "technology": {
                "tech", "technology", "software", "hardware", "app", "application",
                "computer", "mobile", "smartphone", "ai", "artificial intelligence",
                "machine learning", "programming", "code", "developer", "startup",
                "innovation", "digital", "internet", "web", "cybersecurity", "data"
            },
            "sports": {
                "sport", "sports", "game", "match", "team", "player", "athlete",
                "championship", "tournament", "league", "soccer", "football", "basketball",
                "tennis", "baseball", "hockey", "olympics", "fitness", "training",
                "coach", "score", "victory", "defeat", "competition", "stadium"
            },
            "business": {
                "business", "company", "corporate", "finance", "economy", "market",
                "stock", "investment", "profit", "revenue", "sales", "marketing",
                "entrepreneur", "startup", "brand", "product", "service", "customer",
                "strategy", "growth", "management", "leadership", "industry", "sector"
            },
            "lifestyle": {
                "lifestyle", "life", "living", "home", "family", "relationship",
                "personal", "daily", "routine", "habit", "wellness", "balance",
                "happiness", "motivation", "inspiration", "self-improvement",
                "mindfulness", "meditation", "productivity", "organization", "tips"
            },
            "health": {
                "health", "medical", "doctor", "medicine", "treatment", "symptoms",
                "disease", "illness", "wellness", "fitness", "exercise", "nutrition",
                "diet", "mental health", "therapy", "healthcare", "hospital",
                "patient", "diagnosis", "cure", "prevention", "healthy", "recovery"
            },
            "education": {
                "education", "school", "university", "college", "student", "teacher",
                "learning", "study", "course", "lesson", "class", "academic",
                "knowledge", "skill", "training", "tutorial", "research", "science",
                "mathematics", "history", "literature", "language", "exam", "degree"
            }
        }
    
    def _initialize_models(self):
        """Initialize classification models"""
        try:
            if TRANSFORMERS_AVAILABLE:
                self._initialize_transformer_models()
            
            if SKLEARN_AVAILABLE:
                self._initialize_sklearn_models()
            
            # Rule-based fallback is always available
            self._initialize_rule_based_classifier()
            
        except Exception as e:
            logger.error(f"Failed to initialize classification models: {e}")
            self._initialize_rule_based_classifier()
    
    def _initialize_transformer_models(self):
        """Initialize transformer-based models"""
        try:
            # General content classification
            self.pipelines["content"] = pipeline(
                "text-classification",
                model="facebook/bart-large-mnli",  # Zero-shot classification
                device=self._get_device()
            )
            
            # Specialized models for different aspects
            classification_models = {
                "sentiment": "cardiffnlp/twitter-roberta-base-sentiment-latest",
                "emotion": "j-hartmann/emotion-english-distilroberta-base",
                "topics": "microsoft/DialoGPT-medium"
            }
            
            for name, model_name in classification_models.items():
                try:
                    self.pipelines[name] = pipeline(
                        "text-classification",
                        model=model_name,
                        device=self._get_device(),
                        return_all_scores=True
                    )
                    logger.info(f"Loaded {name} classification model")
                except Exception as e:
                    logger.warning(f"Failed to load {name} model: {e}")
            
            logger.info("Transformer models initialized for content classification")
            
        except Exception as e:
            logger.error(f"Failed to initialize transformer models: {e}")
    
    def _initialize_sklearn_models(self):
        """Initialize scikit-learn based models"""
        try:
            # Create TF-IDF + Naive Bayes classifier
            self.fallback_classifiers["tfidf_nb"] = SklearnPipeline([
                ('tfidf', TfidfVectorizer(max_features=5000, stop_words='english')),
                ('classifier', MultinomialNB())
            ])
            
            # Create TF-IDF + Logistic Regression classifier
            self.fallback_classifiers["tfidf_lr"] = SklearnPipeline([
                ('tfidf', TfidfVectorizer(max_features=5000, stop_words='english')),
                ('classifier', LogisticRegression(max_iter=1000))
            ])
            
            logger.info("Scikit-learn models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize scikit-learn models: {e}")
    
    def _initialize_rule_based_classifier(self):
        """Initialize rule-based classification system"""
        self.rule_patterns = {
            "music": [
                r'\b(song|album|artist|band|music|lyrics|melody|beat)\b',
                r'\b(spotify|soundcloud|apple music|youtube music)\b',
                r'\b(concert|tour|live performance|gig)\b'
            ],
            "entertainment": [
                r'\b(movie|film|tv|show|series|netflix|cinema)\b',
                r'\b(actor|actress|celebrity|director|producer)\b',
                r'\b(comedy|drama|thriller|action|horror)\b'
            ],
            "technology": [
                r'\b(tech|software|app|ai|programming|code)\b',
                r'\b(smartphone|computer|internet|web|digital)\b',
                r'\b(startup|innovation|cybersecurity|data)\b'
            ],
            "sports": [
                r'\b(sport|game|match|team|player|athlete)\b',
                r'\b(championship|tournament|league|olympics)\b',
                r'\b(soccer|football|basketball|tennis|baseball)\b'
            ],
            "business": [
                r'\b(business|company|corporate|finance|market)\b',
                r'\b(investment|profit|revenue|sales|marketing)\b',
                r'\b(entrepreneur|startup|brand|strategy)\b'
            ]
        }
        
        # Compile patterns for performance
        self.compiled_patterns = {
            category: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for category, patterns in self.rule_patterns.items()
        }
        
        logger.info("Rule-based classifier initialized")
    
    def _get_device(self) -> int:
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle__get_device_request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler _get_device failed: {e}")
                    return {"status": "error", "message": str(e)}
    async def classify(
        self,
        text: Union[str, List[str]],
        categories: Optional[List[str]] = None,
        include_subcategories: bool = True,
        include_tone: bool = True,
        include_intent: bool = True
    ) -> Union[ClassificationResult, List[ClassificationResult]]:
        """
        Classify content into categories
        
        Args:
            text: Text or list of texts to classify
            categories: Optional list of target categories
            include_subcategories: Whether to detect subcategories
            include_tone: Whether to analyze tone
            include_intent: Whether to detect intent
        
        Returns:
            ClassificationResult or list of results
        """
        start_time = asyncio.get_event_loop().time()
        
        # Handle batch processing
        is_batch = isinstance(text, list)
        texts = text if is_batch else [text]
        
        # Use default categories if none provided
        if categories is None:
            categories = [cat.value for cat in ContentCategory]
        
        results = []
        
        try:
            for single_text in texts:
                result = await self._classify_single_text(
                    single_text,
                    categories,
                    include_subcategories,
                    include_tone,
                    include_intent
                )
                results.append(result)
            
            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            for result in results:
                result.processing_time = processing_time / len(results)
            
            return results if is_batch else results[0]
            
        except Exception as e:
            logger.error(f"Content classification failed: {e}")
            raise
    
    async def _classify_single_text(
        self,
        text: str,
        categories: List[str],
        include_subcategories: bool,
        include_tone: bool,
        include_intent: bool
    ) -> ClassificationResult:
        """Classify a single text"""
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")
        
        result = ClassificationResult(
            text=text,
            primary_category="unknown",
            confidence=0.0
        )
        
        try:
            # Primary classification
            if "content" in self.pipelines:
                await self._classify_with_transformer(text, categories, result)
            else:
                await self._classify_with_rules(text, categories, result)
            
            # Extract keywords and topics
            result.keywords = await self._extract_keywords(text)
            result.topics = await self._extract_topics(text)
            
            # Tone analysis
            if include_tone:
                result.tone = await self._analyze_tone(text)
            
            # Intent detection
            if include_intent:
                result.intent = await self._detect_intent(text)
            
            # Content quality assessment
            result.content_quality_score = await self._assess_content_quality(text)
            
            # Audience target detection
            result.audience_target = await self._detect_audience_target(text)
            
            # Content safety analysis
            result.content_safety = await self._analyze_content_safety(text)
            
            # Add metadata
            result.metadata = {
                "text_length": len(text),
                "word_count": len(text.split()),
                "categories_considered": len(categories),
                "classification_method": "transformer" if "content" in self.pipelines else "rule_based"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Single text classification failed: {e}")
            result.metadata["error"] = str(e)
            return result
    
    async def _classify_with_transformer(
        self,
        text: str,
        categories: List[str],
        result: ClassificationResult
    ):
        """Classify using transformer model (zero-shot)"""
        try:
            classifier = self.pipelines["content"]
            
            # Zero-shot classification
            candidate_labels = categories
            
            predictions = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: classifier(text, candidate_labels)
            )
            
            if predictions:
                # Extract results
                labels = predictions["labels"]
                scores = predictions["scores"]
                
                # Create category scores
                category_scores = []
                for label, score in zip(labels, scores):
                    category_scores.append(CategoryScore(
                        category=label,
                        confidence=score,
                        keywords=self._get_category_keywords(text, label)
                    ))
                
                result.category_scores = category_scores
                result.primary_category = labels[0]
                result.confidence = scores[0]
                
        except Exception as e:
            logger.error(f"Transformer classification failed: {e}")
            # Fall back to rule-based
            await self._classify_with_rules(text, categories, result)
    
    async def _classify_with_rules(
        self,
        text: str,
        categories: List[str],
        result: ClassificationResult
    ):
        """Classify using rule-based approach"""
        text_lower = text.lower()
        category_scores = {}
        
        # Score based on keyword matches
        for category in categories:
            score = 0.0
            matched_keywords = []
            
            # Check compiled patterns
            if category in self.compiled_patterns:
                for pattern in self.compiled_patterns[category]:
                    matches = pattern.findall(text)
                    score += len(matches) * 0.1
                    matched_keywords.extend(matches)
            
            # Check category keywords
            if category in self.category_keywords:
                for keyword in self.category_keywords[category]:
                    if keyword in text_lower:
                        score += 0.2
                        matched_keywords.append(keyword)
            
            # Normalize score
            text_words = len(text.split())
            if text_words > 0:
                score = min(score / (text_words * 0.1), 1.0)
            
            if score > 0:
                category_scores[category] = {
                    "score": score,
                    "keywords": matched_keywords
                }
        
        # Sort by score
        sorted_scores = sorted(
            category_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        # Create results
        result.category_scores = [
            CategoryScore(
                category=category,
                confidence=data["score"],
                keywords=list(set(data["keywords"]))
            )
            for category, data in sorted_scores[:5]  # Top 5
        ]
        
        if sorted_scores:
            result.primary_category = sorted_scores[0][0]
            result.confidence = sorted_scores[0][1]["score"]
        else:
            result.primary_category = "general"
            result.confidence = 0.1
    
    def _get_category_keywords(self, text: str, category: str) -> List[str]:
        """Get keywords that match a specific category from text"""
        if category not in self.category_keywords:
            return []
        
        text_lower = text.lower()
        matched_keywords = []
        
        for keyword in self.category_keywords[category]:
            if keyword in text_lower:
                matched_keywords.append(keyword)
        
        return matched_keywords
    
    async def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
Extract key terms from text"""
        try:
            # Simple keyword extraction based on frequency and importance
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            
            # Remove common stop words
            stop_words = {
                'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
                'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
                'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
            }
            
            filtered_words = [word for word in words if word not in stop_words]
            
            # Count frequency
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top keywords
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in top_words[:max_keywords]]
            
        except Exception:
            return []
    
    async def _extract_topics(self, text: str) -> List[str]:
        """
Extract main topics from text"""
        # Simple topic extraction based on categories and keywords
        topics = []
        
        # Check for category-specific topics
        for category, keywords in self.category_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text.lower())
            if matches > 2:  # Threshold for topic relevance
                topics.append(category)
        
        return topics[:5]  # Limit to top 5 topics
    
    async def _analyze_tone(self, text: str) -> Optional[str]:
        """
Analyze the tone of the content"""
        # Rule-based tone detection
        text_lower = text.lower()
        
        tone_indicators = {
            "professional": ["please", "thank you", "sincerely", "regards", "formal"],
            "casual": ["hey", "hi", "cool", "awesome", "yeah", "ok"],
            "humorous": ["lol", "funny", "joke", "hilarious", "haha", "😂"],
            "serious": ["important", "urgent", "critical", "significant", "serious"],
            "friendly": ["welcome", "glad", "happy", "excited", "wonderful"]
        }
        
        tone_scores = {}
        for tone, indicators in tone_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            if score > 0:
                tone_scores[tone] = score
        
        if tone_scores:
            return max(tone_scores.items(), key=lambda x: x[1])[0]
        
        return "neutral"
    
    async def _detect_intent(self, text: str) -> Optional[str]:
        """Detect the intent of the content"""
        # Rule-based intent detection
        text_lower = text.lower()
        
        intent_patterns = {
            "question": [r'\?', r'\bwhat\b', r'\bhow\b', r'\bwhy\b', r'\bwhere\b', r'\bwhen\b'],
            "inform": [r'\bis\b', r'\bare\b', r'\bfact\b', r'\bknow\b', r'\binformation\b'],
            "sell": [r'\bbuy\b', r'\bpurchase\b', r'\bsale\b', r'\boffer\b', r'\bdeal\b'],
            "entertain": [r'\bfunny\b', r'\bjoke\b', r'\bstory\b', r'\bwatch\b'],
            "persuade": [r'\bshould\b', r'\bmust\b', r'\bneed to\b', r'\bconvince\b']
        }
        
        intent_scores = {}
        for intent, patterns in intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        
        return "share"  # Default intent
    
    async def _assess_content_quality(self, text: str) -> float:
        """Assess the quality of content"""
        quality_score = 0.5  # Base score
        
        # Length factor
        word_count = len(text.split())
        if 20 <= word_count <= 500:
            quality_score += 0.2
        elif word_count > 10:
            quality_score += 0.1
        
        # Spelling and grammar (simple heuristics)
        sentences = text.split('.')
        if len(sentences) > 1:  # Multiple sentences
            quality_score += 0.1
        
        # Punctuation usage
        if any(p in text for p in ['.', '!', '?', ',']):
            quality_score += 0.1
        
        # Capital letters (proper formatting)
        if text[0].isupper() if text else False:
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    async def _detect_audience_target(self, text: str) -> Optional[str]:
        """
Detect the target audience"""
        text_lower = text.lower()
        
        audience_indicators = {
            "general": ["everyone", "all", "people"],
            "professionals": ["business", "industry", "corporate", "professional"],
            "young_adults": ["college", "student", "young", "millennial", "gen z"],
            "parents": ["family", "kids", "children", "parent"],
            "tech_savvy": ["tech", "developer", "programmer", "geek"]
        }
        
        for audience, indicators in audience_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return audience
        
        return "general"
    
    async def _analyze_content_safety(self, text: str) -> Dict[str, Any]:
        """Analyze content safety factors"""
        safety_analysis = {
            "is_safe": True,
            "concerns": [],
            "confidence": 0.9
        }
        
        # Simple safety checks
        unsafe_indicators = [
            "hate", "violence", "dangerous", "illegal", "inappropriate"
        ]
        
        text_lower = text.lower()
        for indicator in unsafe_indicators:
            if indicator in text_lower:
                safety_analysis["is_safe"] = False
                safety_analysis["concerns"].append(indicator)
                safety_analysis["confidence"] = 0.3
        
        return safety_analysis
    
    async def classify_batch(
        self,
        texts: List[str],
        categories: Optional[List[str]] = None,
        **kwargs
    ) -> List[ClassificationResult]:
        """Classify multiple texts efficiently"""
        return await self.classify(texts, categories, **kwargs)
    
    def get_available_categories(self) -> List[str]:
        """
Get list of available categories"""
        return [cat.value for cat in ContentCategory]
    
    def get_category_keywords(self, category: str) -> List[str]:
        try:
            logger.info(f"Executing health_check")
            
            # Implementation for health_check
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"health_check completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"health_check failed: {e}")
            raise
        except Exception as e:
            status["status"] = "degraded"
            status["error"] = str(e)
        
        return status
    
    def shutdown(self):
        """Shutdown the content classifier"""
        logger.info("Shutting down Content Classifier")
        
        # Clear models
        self.models.clear()
        self.pipelines.clear()
        self.fallback_classifiers.clear()
        
        # Clear GPU memory if using CUDA
        if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()

# Utility functions
def merge_classification_results(results: List[ClassificationResult]) -> Dict[str, Any]:
    """Merge multiple classification results for analysis"""
    if not results:
        return {}
    
    # Category distribution
    category_counts = {}
    for result in results:
        category = result.primary_category
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Average confidence
    avg_confidence = sum(r.confidence for r in results) / len(results)
    
    # Common keywords
    all_keywords = []
    for result in results:
        all_keywords.extend(result.keywords)
    
    keyword_freq = {}
    for keyword in all_keywords:
        keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
    
    top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "total_texts": len(results),
        "category_distribution": category_counts,
        "average_confidence": avg_confidence,
        "top_keywords": [kw for kw, freq in top_keywords],
        "quality_scores": [r.content_quality_score for r in results]
    }
