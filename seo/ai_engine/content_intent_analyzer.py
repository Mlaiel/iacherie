"""Content Intent Analyzer
Advanced AI-powered content intent analysis for SEO optimization.

Features:
- Search intent classification (informational, transactional, navigational, commercial)
- User journey mapping
- Content gap analysis
- Intent-based keyword optimization
- SERP intent analysis

Author: Fahed Mlaiel (mlaiel@live.de)
ML Engineer + IA Prompt Engineer expertise applied
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    from sklearn.metrics.pairwise import cosine_similarity
    import spacy
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from textblob import TextBlob
except ImportError as e:
    logging.warning(f"Optional dependencies not available: {e}")

logger = logging.getLogger(__name__)

class SearchIntent(Enum):
    """Search intent categories."""
    INFORMATIONAL = "informational"
    TRANSACTIONAL = "transactional" 
    NAVIGATIONAL = "navigational"
    COMMERCIAL = "commercial"
    LOCAL = "local"
    UNKNOWN = "unknown"

@dataclass
class IntentSignals:
    """Signals that indicate specific search intent."""
    informational: List[str] = field(default_factory=lambda: [
        "what", "how", "why", "when", "where", "who", "guide", "tutorial", 
        "learn", "understand", "explain", "definition", "meaning", "tips",
        "help", "information", "facts", "research", "study", "analysis"
    ])
    
    transactional: List[str] = field(default_factory=lambda: [
        "buy", "purchase", "order", "shop", "price", "cost", "sale", 
        "discount", "deal", "offer", "checkout", "cart", "payment",
        "shipping", "delivery", "return", "warranty", "guarantee"
    ])
    
    navigational: List[str] = field(default_factory=lambda: [
        "homepage", "website", "site", "login", "contact", "about",
        "services", "products", "menu", "navigation", "home page",
        "official", "main", "portal", "dashboard", "account"
    ])
    
    commercial: List[str] = field(default_factory=lambda: [
        "best", "top", "review", "compare", "comparison", "vs", "versus",
        "rating", "recommendation", "alternative", "option", "choice",
        "evaluation", "assessment", "opinion", "testimonial", "feedback"
    ])
    
    local: List[str] = field(default_factory=lambda: [
        "near me", "nearby", "local", "location", "address", "directions",
        "hours", "open", "closed", "phone", "contact", "store", "branch",
        "office", "clinic", "restaurant", "service area", "delivery area"
    ])

@dataclass
class IntentAnalysisResult:
    """Result of intent analysis."""
    primary_intent: SearchIntent
    confidence_score: float
    secondary_intent: Optional[SearchIntent]
    intent_distribution: Dict[SearchIntent, float]
    keyword_signals: Dict[SearchIntent, List[str]]
    user_journey_stage: str
    content_gaps: List[str]
    optimization_recommendations: List[str]
    serp_intent_alignment: float

@dataclass
class ContentIntentConfig:
    """Configuration for content intent analysis."""
    target_keywords: List[str]
    content_type: str
    target_audience: str
    business_type: str = "general"
    include_serp_analysis: bool = True
    confidence_threshold: float = 0.7
    language: str = "en"

class ContentIntentAnalyzer:
    """Advanced content intent analysis engine."""
    
    def __init__(self):
        """Initialize the Content Intent Analyzer."""
        self.intent_signals = IntentSignals()
        self.intent_classifier = None
        self.nlp_model = None
        self.semantic_model = None
        self._load_models()
        
        # Pre-trained intent patterns
        self.intent_patterns = self._load_intent_patterns()
        
        # User journey stages
        self.journey_stages = {
            "awareness": ["problem", "issue", "challenge", "need", "want"],
            "consideration": ["solution", "option", "alternative", "compare", "evaluate"],
            "decision": ["buy", "purchase", "choose", "select", "decide"],
            "retention": ["support", "help", "maintenance", "upgrade", "renew"]
        }
    
    def _load_models(self):
        """Load AI models for intent analysis."""
        try:
            # Load zero-shot classification model
            self.intent_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            
            # Load spaCy model
            try:
                self.nlp_model = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy English model not found")
            
            # Load semantic similarity model
            self.semantic_model = pipeline(
                "feature-extraction",
                model="sentence-transformers/all-MiniLM-L6-v2"
            )
            
        except Exception as e:
            logger.error(f"Error loading intent analysis models: {e}")
    
    def _load_intent_patterns(self) -> Dict[SearchIntent, List[str]]:
        """Load pre-defined intent patterns."""
        return {
            SearchIntent.INFORMATIONAL: [
                r"\b(what|how|why|when|where|who)\s+is\b",
                r"\b(guide|tutorial|tips|advice)\b",
                r"\b(learn|understand|explain|definition)\b",
                r"\b(information|facts|research|study)\b"
            ],
            SearchIntent.TRANSACTIONAL: [
                r"\b(buy|purchase|order|shop)\b",
                r"\b(price|cost|sale|discount|deal)\b",
                r"\b(checkout|cart|payment|shipping)\b",
                r"\b(warranty|guarantee|return)\b"
            ],
            SearchIntent.NAVIGATIONAL: [
                r"\b(homepage|website|site|login)\b",
                r"\b(contact|about|services|products)\b",
                r"\b(official|main|portal)\b",
                r"\b[a-zA-Z]+\.(com|org|net|gov)\b"
            ],
            SearchIntent.COMMERCIAL: [
                r"\b(best|top|review|compare)\b",
                r"\b(rating|recommendation|alternative)\b",
                r"\b(vs|versus|comparison)\b",
                r"\b(opinion|testimonial|feedback)\b"
            ],
            SearchIntent.LOCAL: [
                r"\bnear\s+me\b",
                r"\b(nearby|local|location)\b",
                r"\b(address|directions|hours)\b",
                r"\b(phone|contact|store|branch)\b"
            ]
        }
    
    async def analyze_content_intent(
        self,
        content: str,
        config: ContentIntentConfig
    ) -> IntentAnalysisResult:
        """Analyze content intent comprehensively.
        
        Args:
            content: Content to analyze
            config: Analysis configuration
            
        Returns:
            IntentAnalysisResult with detailed intent analysis
        """
        try:
            # 1. Pattern-based intent detection
            pattern_scores = self._analyze_intent_patterns(content)
            
            # 2. Keyword-based intent analysis
            keyword_scores = self._analyze_keyword_intent(content, config.target_keywords)
            
            # 3. AI-based intent classification
            ai_scores = await self._classify_intent_with_ai(content)
            
            # 4. Context-based intent analysis
            context_scores = self._analyze_contextual_intent(content, config)
            
            # 5. Combine all scores
            combined_scores = self._combine_intent_scores(
                pattern_scores, keyword_scores, ai_scores, context_scores
            )
            
            # 6. Determine primary and secondary intent
            primary_intent, confidence = self._determine_primary_intent(combined_scores)
            secondary_intent = self._determine_secondary_intent(combined_scores, primary_intent)
            
            # 7. Analyze user journey stage
            journey_stage = self._analyze_user_journey_stage(content)
            
            # 8. Identify content gaps
            content_gaps = await self._identify_content_gaps(content, primary_intent, config)
            
            # 9. Generate optimization recommendations
            recommendations = self._generate_intent_recommendations(
                content, primary_intent, config
            )
            
            # 10. Analyze SERP intent alignment (if enabled)
            serp_alignment = 0.8  # Placeholder - would integrate with SERP analysis
            if config.include_serp_analysis:
                serp_alignment = await self._analyze_serp_intent_alignment(
                    config.target_keywords, primary_intent
                )
            
            # 11. Extract keyword signals for each intent
            keyword_signals = self._extract_keyword_signals(content)
            
            return IntentAnalysisResult(
                primary_intent=primary_intent,
                confidence_score=confidence,
                secondary_intent=secondary_intent,
                intent_distribution=combined_scores,
                keyword_signals=keyword_signals,
                user_journey_stage=journey_stage,
                content_gaps=content_gaps,
                optimization_recommendations=recommendations,
                serp_intent_alignment=serp_alignment
            )
            
        except Exception as e:
            logger.error(f"Error analyzing content intent: {e}")
            return self._create_default_result()
    
    def _analyze_intent_patterns(self, content: str) -> Dict[SearchIntent, float]:
        """Analyze intent using regex patterns."""
        try:
            scores = {intent: 0.0 for intent in SearchIntent}
            content_lower = content.lower()
            
            for intent, patterns in self.intent_patterns.items():
                for pattern in patterns:
                    matches = len(re.findall(pattern, content_lower))
                    scores[intent] += matches * 0.1  # Weight each match
            
            # Normalize scores
            total_score = sum(scores.values())
            if total_score > 0:
                scores = {intent: score / total_score for intent, score in scores.items()}
            
            return scores
            
        except Exception as e:
            logger.error(f"Error analyzing intent patterns: {e}")
            return {intent: 0.0 for intent in SearchIntent}
    
    def _analyze_keyword_intent(
        self,
        content: str,
        target_keywords: List[str]
    ) -> Dict[SearchIntent, float]:
        """Analyze intent based on keyword signals."""
        try:
            scores = {intent: 0.0 for intent in SearchIntent}
            content_lower = content.lower()
            
            # Check for intent signals in content
            for intent_type in [SearchIntent.INFORMATIONAL, SearchIntent.TRANSACTIONAL, 
                               SearchIntent.NAVIGATIONAL, SearchIntent.COMMERCIAL, SearchIntent.LOCAL]:
                signals = getattr(self.intent_signals, intent_type.value)
                
                for signal in signals:
                    if signal in content_lower:
                        scores[intent_type] += 1
            
            # Analyze target keywords for intent signals
            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                
                # Check which intent signals the keyword contains
                for intent_type in [SearchIntent.INFORMATIONAL, SearchIntent.TRANSACTIONAL,
                                   SearchIntent.NAVIGATIONAL, SearchIntent.COMMERCIAL, SearchIntent.LOCAL]:
                    signals = getattr(self.intent_signals, intent_type.value)
                    
                    for signal in signals:
                        if signal in keyword_lower:
                            scores[intent_type] += 0.5
            
            # Normalize scores
            total_score = sum(scores.values())
            if total_score > 0:
                scores = {intent: score / total_score for intent, score in scores.items()}
            
            return scores
            
        except Exception as e:
            logger.error(f"Error analyzing keyword intent: {e}")
            return {intent: 0.0 for intent in SearchIntent}
    
    async def _classify_intent_with_ai(self, content: str) -> Dict[SearchIntent, float]:
        """Classify intent using AI models."""
        try:
            if not self.intent_classifier:
                return {intent: 0.0 for intent in SearchIntent}
            
            # Prepare intent labels
            intent_labels = [intent.value for intent in SearchIntent if intent != SearchIntent.UNKNOWN]
            
            # Classify with AI model
            result = self.intent_classifier(content[:512], intent_labels)
            
            # Convert to our format
            scores = {intent: 0.0 for intent in SearchIntent}
            
            for label, score in zip(result['labels'], result['scores']):
                intent = SearchIntent(label)
                scores[intent] = score
            
            return scores
            
        except Exception as e:
            logger.error(f"Error classifying intent with AI: {e}")
            return {intent: 0.0 for intent in SearchIntent}
    
    def _analyze_contextual_intent(
        self,
        content: str,
        config: ContentIntentConfig
    ) -> Dict[SearchIntent, float]:
        """Analyze intent based on context clues."""
        try:
            scores = {intent: 0.0 for intent in SearchIntent}
            
            # Content type context
            content_type_intent_map = {
                "blog": SearchIntent.INFORMATIONAL,
                "product": SearchIntent.TRANSACTIONAL,
                "landing": SearchIntent.TRANSACTIONAL,
                "about": SearchIntent.NAVIGATIONAL,
                "contact": SearchIntent.NAVIGATIONAL,
                "review": SearchIntent.COMMERCIAL,
                "comparison": SearchIntent.COMMERCIAL
            }
            
            if config.content_type.lower() in content_type_intent_map:
                intent = content_type_intent_map[config.content_type.lower()]
                scores[intent] += 0.3
            
            # Business type context
            business_type_intent_map = {
                "ecommerce": SearchIntent.TRANSACTIONAL,
                "saas": SearchIntent.COMMERCIAL,
                "blog": SearchIntent.INFORMATIONAL,
                "local": SearchIntent.LOCAL,
                "service": SearchIntent.COMMERCIAL
            }
            
            if config.business_type.lower() in business_type_intent_map:
                intent = business_type_intent_map[config.business_type.lower()]
                scores[intent] += 0.2
            
            # Content structure analysis
            if any(word in content.lower() for word in ["price", "$", "buy", "order"]):
                scores[SearchIntent.TRANSACTIONAL] += 0.2
            
            if any(word in content.lower() for word in ["how to", "guide", "tutorial"]):
                scores[SearchIntent.INFORMATIONAL] += 0.2
            
            if any(word in content.lower() for word in ["vs", "compare", "best"]):
                scores[SearchIntent.COMMERCIAL] += 0.2
            
            return scores
            
        except Exception as e:
            logger.error(f"Error analyzing contextual intent: {e}")
            return {intent: 0.0 for intent in SearchIntent}
    
    def _combine_intent_scores(
        self,
        pattern_scores: Dict[SearchIntent, float],
        keyword_scores: Dict[SearchIntent, float],
        ai_scores: Dict[SearchIntent, float],
        context_scores: Dict[SearchIntent, float]
    ) -> Dict[SearchIntent, float]:
        """Combine multiple intent scoring methods."""
        try:
            combined_scores = {intent: 0.0 for intent in SearchIntent}
            
            # Weighted combination
            weights = {
                'pattern': 0.25,
                'keyword': 0.25,
                'ai': 0.35,
                'context': 0.15
            }
            
            for intent in SearchIntent:
                combined_scores[intent] = (
                    pattern_scores.get(intent, 0) * weights['pattern'] +
                    keyword_scores.get(intent, 0) * weights['keyword'] +
                    ai_scores.get(intent, 0) * weights['ai'] +
                    context_scores.get(intent, 0) * weights['context']
                )
            
            return combined_scores
            
        except Exception as e:
            logger.error(f"Error combining intent scores: {e}")
            return {intent: 0.0 for intent in SearchIntent}
    
    def _determine_primary_intent(
        self,
        scores: Dict[SearchIntent, float]
    ) -> Tuple[SearchIntent, float]:
        """Determine primary intent and confidence."""
        try:
            # Find highest scoring intent
            primary_intent = max(scores, key=scores.get)
            confidence = scores[primary_intent]
            
            # If confidence is too low, mark as unknown
            if confidence < 0.3:
                return SearchIntent.UNKNOWN, confidence
            
            return primary_intent, confidence
            
        except Exception as e:
            logger.error(f"Error determining primary intent: {e}")
            return SearchIntent.UNKNOWN, 0.0
    
    def _determine_secondary_intent(
        self,
        scores: Dict[SearchIntent, float],
        primary_intent: SearchIntent
    ) -> Optional[SearchIntent]:
        """Determine secondary intent if applicable."""
        try:
            # Remove primary intent from consideration
            remaining_scores = {k: v for k, v in scores.items() if k != primary_intent}
            
            if not remaining_scores:
                return None
            
            secondary_intent = max(remaining_scores, key=remaining_scores.get)
            secondary_score = remaining_scores[secondary_intent]
            
            # Only return if secondary intent has reasonable score
            if secondary_score >= 0.2:
                return secondary_intent
            
            return None
            
        except Exception as e:
            logger.error(f"Error determining secondary intent: {e}")
            return None
    
    def _analyze_user_journey_stage(self, content: str) -> str:
        """Analyze which stage of user journey the content targets."""
        try:
            content_lower = content.lower()
            stage_scores = {}
            
            for stage, keywords in self.journey_stages.items():
                score = sum(1 for keyword in keywords if keyword in content_lower)
                stage_scores[stage] = score
            
            if not stage_scores or max(stage_scores.values()) == 0:
                return "consideration"  # Default
            
            return max(stage_scores, key=stage_scores.get)
            
        except Exception as e:
            logger.error(f"Error analyzing user journey stage: {e}")
            return "consideration"
    
    async def _identify_content_gaps(
        self,
        content: str,
        primary_intent: SearchIntent,
        config: ContentIntentConfig
    ) -> List[str]:
        """Identify content gaps based on intent analysis."""
        try:
            gaps = []
            content_lower = content.lower()
            
            # Intent-specific gap analysis
            if primary_intent == SearchIntent.INFORMATIONAL:
                if "how" not in content_lower and "what" not in content_lower:
                    gaps.append("Missing explanatory content (how/what)")
                
                if "example" not in content_lower and "case" not in content_lower:
                    gaps.append("Missing examples or case studies")
            
            elif primary_intent == SearchIntent.TRANSACTIONAL:
                if "price" not in content_lower and "cost" not in content_lower:
                    gaps.append("Missing pricing information")
                
                if "buy" not in content_lower and "purchase" not in content_lower:
                    gaps.append("Missing clear call-to-action")
            
            elif primary_intent == SearchIntent.COMMERCIAL:
                if "compare" not in content_lower and "vs" not in content_lower:
                    gaps.append("Missing comparison information")
                
                if "review" not in content_lower and "rating" not in content_lower:
                    gaps.append("Missing review or rating information")
            
            elif primary_intent == SearchIntent.NAVIGATIONAL:
                if "contact" not in content_lower:
                    gaps.append("Missing contact information")
                
                if "about" not in content_lower:
                    gaps.append("Missing about information")
            
            elif primary_intent == SearchIntent.LOCAL:
                if "address" not in content_lower and "location" not in content_lower:
                    gaps.append("Missing location information")
                
                if "phone" not in content_lower and "contact" not in content_lower:
                    gaps.append("Missing contact details")
            
            return gaps
            
        except Exception as e:
            logger.error(f"Error identifying content gaps: {e}")
            return []
    
    def _generate_intent_recommendations(
        self,
        content: str,
        primary_intent: SearchIntent,
        config: ContentIntentConfig
    ) -> List[str]:
        """Generate optimization recommendations based on intent."""
        try:
            recommendations = []
            
            # Intent-specific recommendations
            if primary_intent == SearchIntent.INFORMATIONAL:
                recommendations.extend([
                    "Add clear headings and subheadings for better structure",
                    "Include step-by-step instructions or explanations",
                    "Add relevant examples and use cases",
                    "Consider adding FAQ section",
                    "Use bullet points for better readability"
                ])
            
            elif primary_intent == SearchIntent.TRANSACTIONAL:
                recommendations.extend([
                    "Add clear and prominent call-to-action buttons",
                    "Include pricing information and product details",
                    "Add trust signals (reviews, testimonials, certifications)",
                    "Optimize for conversion with urgency elements",
                    "Include shipping and return policy information"
                ])
            
            elif primary_intent == SearchIntent.COMMERCIAL:
                recommendations.extend([
                    "Add comparison tables or charts",
                    "Include pros and cons for different options",
                    "Add customer reviews and ratings",
                    "Include detailed product specifications",
                    "Add recommendation sections"
                ])
            
            elif primary_intent == SearchIntent.NAVIGATIONAL:
                recommendations.extend([
                    "Ensure clear navigation and site structure",
                    "Add breadcrumb navigation",
                    "Include search functionality",
                    "Add clear contact information",
                    "Optimize for brand-related searches"
                ])
            
            elif primary_intent == SearchIntent.LOCAL:
                recommendations.extend([
                    "Add Google My Business optimization",
                    "Include local schema markup",
                    "Add location-specific content",
                    "Include customer reviews and local testimonials",
                    "Optimize for 'near me' searches"
                ])
            
            # General recommendations
            recommendations.extend([
                f"Optimize for primary intent: {primary_intent.value}",
                "Ensure content matches user search intent",
                "Add relevant internal and external links"
            ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating intent recommendations: {e}")
            return []
    
    async def _analyze_serp_intent_alignment(
        self,
        keywords: List[str],
        primary_intent: SearchIntent
    ) -> float:
        """Analyze how well content aligns with SERP intent."""
        try:
            # This would integrate with actual SERP analysis
            # For now, return a placeholder score
            
            # Intent alignment scoring logic would go here
            # - Analyze top 10 SERP results for target keywords
            # - Determine dominant intent in SERP
            # - Compare with content's primary intent
            # - Return alignment score
            
            alignment_score = 0.8  # Placeholder
            return alignment_score
            
        except Exception as e:
            logger.error(f"Error analyzing SERP intent alignment: {e}")
            return 0.5
    
    def _extract_keyword_signals(self, content: str) -> Dict[SearchIntent, List[str]]:
        """Extract keyword signals for each intent type."""
        try:
            signals = {intent: [] for intent in SearchIntent}
            content_lower = content.lower()
            
            for intent_type in [SearchIntent.INFORMATIONAL, SearchIntent.TRANSACTIONAL,
                               SearchIntent.NAVIGATIONAL, SearchIntent.COMMERCIAL, SearchIntent.LOCAL]:
                intent_signals = getattr(self.intent_signals, intent_type.value)
                
                for signal in intent_signals:
                    if signal in content_lower:
                        signals[intent_type].append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error extracting keyword signals: {e}")
            return {intent: [] for intent in SearchIntent}
    
    def _create_default_result(self) -> IntentAnalysisResult:
        """Create default result for error cases."""
        return IntentAnalysisResult(
            primary_intent=SearchIntent.UNKNOWN,
            confidence_score=0.0,
            secondary_intent=None,
            intent_distribution={intent: 0.0 for intent in SearchIntent},
            keyword_signals={intent: [] for intent in SearchIntent},
            user_journey_stage="consideration",
            content_gaps=[],
            optimization_recommendations=[],
            serp_intent_alignment=0.5
        )

    async def batch_analyze_intent(
        self,
        contents: List[str],
        configs: List[ContentIntentConfig]
    ) -> List[IntentAnalysisResult]:
        """Analyze intent for multiple contents in batch."""
        try:
            tasks = [
                self.analyze_content_intent(content, config)
                for content, config in zip(contents, configs)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log them
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error analyzing intent for content {i}: {result}")
                    valid_results.append(self._create_default_result())
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            logger.error(f"Error in batch intent analysis: {e}")
            return [self._create_default_result() for _ in contents]

    def get_intent_keywords(self, intent: SearchIntent) -> List[str]:
        """Get keywords associated with a specific intent."""
        try:
            if intent == SearchIntent.UNKNOWN:
                return []
            
            return getattr(self.intent_signals, intent.value, [])
            
        except Exception as e:
            logger.error(f"Error getting intent keywords: {e}")
            return []