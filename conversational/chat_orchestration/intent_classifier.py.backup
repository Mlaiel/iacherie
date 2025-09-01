"""Intent Classifier - Advanced user intent classification for multi-format creators
================================================================================

Classifies user intents with high accuracy using ML models and pattern matching
optimized for different creator types and their specific needs.

Author: Fahed Mlaiel <mlaiel@live.de>
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import re
from datetime import datetime

from backend.ai.models import ConversationalAI


class PrimaryIntent(Enum):
    """Primary user intent categories"""
    CONTENT_UPLOAD = "content_upload"
    CONTENT_ANALYSIS = "content_analysis"
    MONETIZATION_QUESTION = "monetization_question"
    PROTECTION_CONCERN = "protection_concern"
    COLLABORATION_REQUEST = "collaboration_request"
    SEO_HELP = "seo_help"
    TECHNICAL_ISSUE = "technical_issue"
    BUSINESS_ADVICE = "business_advice"
    CREATIVE_HELP = "creative_help"
    ANALYTICS_QUESTION = "analytics_question"
    PLATFORM_OPTIMIZATION = "platform_optimization"
    GENERAL_CHAT = "general_chat"
    ACCOUNT_MANAGEMENT = "account_management"
    FEATURE_REQUEST = "feature_request"
    FEEDBACK = "feedback"


class IntentConfidence(Enum):
    """Intent classification confidence levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


@dataclass
class IntentClassificationResult:
    """Complete intent classification results"""
    primary_intent: PrimaryIntent
    secondary_intents: List[PrimaryIntent]
    confidence: float
    confidence_level: IntentConfidence
    intent_indicators: List[str]
    context_factors: Dict[str, Any]
    creator_specific_intents: Dict[str, Any]
    actionable_items: List[str]
    suggested_responses: List[str]
    classification_reasoning: str


class IntentClassifier:
    """
    Advanced intent classification system that accurately identifies user
    intentions with creator-type specific optimizations and contextual
    understanding for optimal conversation routing.
    """
    
    def __init__(self, ai_engine: ConversationalAI):
        self.ai_engine = ai_engine
        self.logger = logging.getLogger(__name__)
        
        # Initialize classification models and patterns
        self._setup_intent_patterns()
        self._setup_creator_specific_patterns()
        self._setup_confidence_thresholds()
        self._setup_ml_features()
        
        # Classification performance tracking
        self.classification_metrics = {
            "total_classifications": 0,
            "high_confidence_count": 0,
            "accuracy_estimates": {},
            "creator_type_performance": {}
        }
    
    async def classify_intent(
        self,
        processed_message: Any,
        context_analysis: Dict[str, Any],
        creator_type: Any
    ) -> IntentClassificationResult:
        """
        Classify user intent with high accuracy and contextual understanding
        
        Args:
            processed_message: Processed user message
            context_analysis: Context analysis results
            creator_type: Type of content creator
            
        Returns:
            IntentClassificationResult: Complete intent classification
        """
        try:
            message_content = processed_message.processed_content
            has_attachments = len(processed_message.attachments) > 0
            creator_value = creator_type.value if hasattr(creator_type, 'value') else str(creator_type)
            
            # Step 1: Extract linguistic features
            linguistic_features = await self._extract_linguistic_features(message_content)
            
            # Step 2: Pattern-based classification
            pattern_scores = await self._classify_by_patterns(
                message_content,
                has_attachments,
                linguistic_features
            )
            
            # Step 3: Creator-specific classification
            creator_scores = await self._classify_creator_specific(
                message_content,
                creator_value,
                context_analysis
            )
            
            # Step 4: Context-enhanced classification
            context_scores = await self._classify_with_context(
                message_content,
                context_analysis,
                has_attachments
            )
            
            # Step 5: ML-based classification (if available)
            ml_scores = await self._classify_with_ml(
                message_content,
                linguistic_features,
                creator_value
            )
            
            # Step 6: Combine scores from all methods
            combined_scores = await self._combine_classification_scores(
                pattern_scores,
                creator_scores,
                context_scores,
                ml_scores
            )
            
            # Step 7: Determine primary and secondary intents
            primary_intent, secondary_intents = await self._determine_intents(combined_scores)
            
            # Step 8: Calculate confidence metrics
            confidence, confidence_level = await self._calculate_confidence(
                combined_scores,
                primary_intent,
                linguistic_features
            )
            
            # Step 9: Extract intent indicators and reasoning
            intent_indicators = await self._extract_intent_indicators(
                message_content,
                primary_intent,
                creator_value
            )
            
            classification_reasoning = await self._generate_classification_reasoning(
                primary_intent,
                combined_scores,
                intent_indicators,
                confidence
            )
            
            # Step 10: Generate actionable items and suggestions
            actionable_items = await self._generate_actionable_items(
                primary_intent,
                secondary_intents,
                creator_value,
                context_analysis
            )
            
            suggested_responses = await self._generate_response_suggestions(
                primary_intent,
                creator_value,
                context_analysis
            )
            
            # Step 11: Extract creator-specific intents
            creator_specific_intents = await self._extract_creator_specific_intents(
                message_content,
                primary_intent,
                creator_value
            )
            
            # Create final classification result
            classification_result = IntentClassificationResult(
                primary_intent=primary_intent,
                secondary_intents=secondary_intents,
                confidence=confidence,
                confidence_level=confidence_level,
                intent_indicators=intent_indicators,
                context_factors=context_analysis,
                creator_specific_intents=creator_specific_intents,
                actionable_items=actionable_items,
                suggested_responses=suggested_responses,
                classification_reasoning=classification_reasoning
            )
            
            # Update metrics
            await self._update_classification_metrics(
                classification_result,
                creator_value
            )
            
            self.logger.info(
                f"Classified intent: {primary_intent.value} "
                f"(confidence: {confidence:.3f}) for {creator_value}"
            )
            
            return classification_result
            
        except Exception as e:
            self.logger.error(f"Intent classification failed: {str(e)}")
            return self._create_fallback_classification(processed_message)
    
    async def _extract_linguistic_features(self, message: str) -> Dict[str, Any]:
        """Extract linguistic features for classification"""
        try:
            features = {
                "message_length": len(message),
                "word_count": len(message.split()),
                "sentence_count": len(re.findall(r'[.!?]+', message)),
                "question_marks": message.count('?'),
                "exclamation_marks": message.count('!'),
                "capital_ratio": sum(1 for c in message if c.isupper()) / max(1, len(message)),
                "has_urls": bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)),
                "has_mentions": '@' in message,
                "has_hashtags": '#' in message,
                "starts_with_question": message.strip().lower().startswith(('what', 'how', 'why', 'when', 'where', 'who', 'can', 'could', 'would', 'should')),
                "imperative_indicators": any(word in message.lower() for word in ['help', 'show', 'tell', 'explain', 'teach', 'give'])
            }
            
            # Extract key phrases
            features["key_phrases"] = await self._extract_key_phrases(message)
            
            # Analyze grammatical structure
            features["grammar_indicators"] = await self._analyze_grammar_indicators(message)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract linguistic features: {str(e)}")
            return {}
    
    async def _classify_by_patterns(
        self,
        message: str,
        has_attachments: bool,
        linguistic_features: Dict[str, Any]
    ) -> Dict[PrimaryIntent, float]:
        """Classify intent using pattern matching"""
        try:
            scores = {intent: 0.0 for intent in PrimaryIntent}
            message_lower = message.lower()
            
            # Direct pattern matching
            for intent, patterns in self.intent_patterns.items():
                pattern_matches = sum(1 for pattern in patterns if pattern in message_lower)
                if pattern_matches > 0:
                    # Weight by pattern quality and frequency
                    base_score = min(1.0, pattern_matches / len(patterns) * 2)
                    scores[intent] += base_score
            
            # Attachment-based classification
            if has_attachments:
                scores[PrimaryIntent.CONTENT_UPLOAD] += 0.7
                scores[PrimaryIntent.CONTENT_ANALYSIS] += 0.5
                scores[PrimaryIntent.PROTECTION_CONCERN] += 0.3
            
            # Question-based classification
            if linguistic_features.get("question_marks", 0) > 0:
                question_intents = [
                    PrimaryIntent.GENERAL_CHAT,
                    PrimaryIntent.TECHNICAL_ISSUE,
                    PrimaryIntent.BUSINESS_ADVICE,
                    PrimaryIntent.ANALYTICS_QUESTION
                ]
                for intent in question_intents:
                    scores[intent] += 0.2
            
            # Imperative-based classification
            if linguistic_features.get("imperative_indicators", False):
                action_intents = [
                    PrimaryIntent.CONTENT_ANALYSIS,
                    PrimaryIntent.TECHNICAL_ISSUE,
                    PrimaryIntent.CREATIVE_HELP
                ]
                for intent in action_intents:
                    scores[intent] += 0.3
            
            return scores
            
        except Exception as e:
            self.logger.error(f"Pattern-based classification failed: {str(e)}")
            return {intent: 0.1 for intent in PrimaryIntent}
    
    async def _classify_creator_specific(
        self,
        message: str,
        creator_type: str,
        context_analysis: Dict[str, Any]
    ) -> Dict[PrimaryIntent, float]:
        """Classify with creator-type specific patterns"""
        try:
            scores = {intent: 0.0 for intent in PrimaryIntent}
            message_lower = message.lower()
            
            creator_patterns = self.creator_specific_patterns.get(creator_type, {})
            
            for intent_str, patterns in creator_patterns.items():
                try:
                    intent = PrimaryIntent(intent_str)
                    pattern_matches = sum(1 for pattern in patterns if pattern in message_lower)
                    if pattern_matches > 0:
                        scores[intent] += min(1.0, pattern_matches / len(patterns) * 1.5)
                except ValueError:
                    continue
            
            # Creator-specific boosting
            if creator_type == "musician":
                music_keywords = ["music", "song", "track", "audio", "spotify", "streaming"]
                if any(keyword in message_lower for keyword in music_keywords):
                    scores[PrimaryIntent.PLATFORM_OPTIMIZATION] += 0.4
                    scores[PrimaryIntent.MONETIZATION_QUESTION] += 0.3
            
            elif creator_type == "blogger":
                blog_keywords = ["blog", "article", "seo", "content", "writing", "traffic"]
                if any(keyword in message_lower for keyword in blog_keywords):
                    scores[PrimaryIntent.SEO_HELP] += 0.5
                    scores[PrimaryIntent.CONTENT_ANALYSIS] += 0.3
            
            elif creator_type == "photographer":
                photo_keywords = ["photo", "image", "portfolio", "camera", "shoot", "editing"]
                if any(keyword in message_lower for keyword in photo_keywords):
                    scores[PrimaryIntent.CONTENT_ANALYSIS] += 0.4
                    scores[PrimaryIntent.PROTECTION_CONCERN] += 0.4
            
            elif creator_type == "influencer":
                influencer_keywords = ["followers", "engagement", "brand", "sponsor", "social media"]
                if any(keyword in message_lower for keyword in influencer_keywords):
                    scores[PrimaryIntent.ANALYTICS_QUESTION] += 0.5
                    scores[PrimaryIntent.COLLABORATION_REQUEST] += 0.3
            
            elif creator_type == "comedian":
                comedy_keywords = ["comedy", "funny", "joke", "perform", "audience", "video"]
                if any(keyword in message_lower for keyword in comedy_keywords):
                    scores[PrimaryIntent.CREATIVE_HELP] += 0.4
                    scores[PrimaryIntent.PLATFORM_OPTIMIZATION] += 0.3
            
            return scores
            
        except Exception as e:
            self.logger.error(f"Creator-specific classification failed: {str(e)}")
            return {intent: 0.0 for intent in PrimaryIntent}
    
    async def _classify_with_context(
        self,
        message: str,
        context_analysis: Dict[str, Any],
        has_attachments: bool
    ) -> Dict[PrimaryIntent, float]:
        """Enhance classification with context analysis"""
        try:
            scores = {intent: 0.0 for intent in PrimaryIntent}
            
            # Business intent context
            business_intent = context_analysis.get("business_intent", {})
            if "monetization" in business_intent:
                scores[PrimaryIntent.MONETIZATION_QUESTION] += 0.6
            if "growth" in business_intent:
                scores[PrimaryIntent.ANALYTICS_QUESTION] += 0.4
                scores[PrimaryIntent.PLATFORM_OPTIMIZATION] += 0.4
            if "collaboration" in business_intent:
                scores[PrimaryIntent.COLLABORATION_REQUEST] += 0.7
            
            # Creative direction context
            creative_direction = context_analysis.get("creative_direction", {})
            if "inspiration" in creative_direction:
                scores[PrimaryIntent.CREATIVE_HELP] += 0.5
            if "quality_improvement" in creative_direction:
                scores[PrimaryIntent.CONTENT_ANALYSIS] += 0.4
            
            # Temporal context
            temporal_context = context_analysis.get("temporal_context", {})
            if "immediate" in temporal_context:
                scores[PrimaryIntent.TECHNICAL_ISSUE] += 0.3
                scores[PrimaryIntent.GENERAL_CHAT] += 0.2
            
            # Emotional state context
            emotional_state = context_analysis.get("emotional_state", {})
            if emotional_state.get("frustration", 0) > 0.5:
                scores[PrimaryIntent.TECHNICAL_ISSUE] += 0.5
            if emotional_state.get("excitement", 0) > 0.5:
                scores[PrimaryIntent.CREATIVE_HELP] += 0.3
                scores[PrimaryIntent.GENERAL_CHAT] += 0.2
            
            # Conversation stage context
            conversation_stage = context_analysis.get("conversation_stage", "")
            if conversation_stage == "deep_dive":
                scores[PrimaryIntent.TECHNICAL_ISSUE] += 0.3
                scores[PrimaryIntent.BUSINESS_ADVICE] += 0.3
            elif conversation_stage == "initial":
                scores[PrimaryIntent.GENERAL_CHAT] += 0.4
            
            return scores
            
        except Exception as e:
            self.logger.error(f"Context-based classification failed: {str(e)}")
            return {intent: 0.0 for intent in PrimaryIntent}
    
    async def _classify_with_ml(
        self,
        message: str,
        linguistic_features: Dict[str, Any],
        creator_type: str
    ) -> Dict[PrimaryIntent, float]:
        """ML-based intent classification (placeholder for future ML model)"""
        try:
            # This would integrate with actual ML models in production
            # For now, return uniform low scores
            scores = {intent: 0.1 for intent in PrimaryIntent}
            
            # Future ML integration points:
            # - Text embedding models (BERT, RoBERTa)
            # - Creator-specific fine-tuned models
            # - Multi-modal classification for attachments
            # - Contextual sequence models (LSTM, Transformer)
            
            return scores
            
        except Exception as e:
            self.logger.error(f"ML-based classification failed: {str(e)}")
            return {intent: 0.1 for intent in PrimaryIntent}
    
    async def _combine_classification_scores(
        self,
        pattern_scores: Dict[PrimaryIntent, float],
        creator_scores: Dict[PrimaryIntent, float],
        context_scores: Dict[PrimaryIntent, float],
        ml_scores: Dict[PrimaryIntent, float]
    ) -> Dict[PrimaryIntent, float]:
        """Combine scores from different classification methods"""
        try:
            combined_scores = {}
            
            # Weights for different classification methods
            weights = {
                "pattern": 0.4,
                "creator": 0.3,
                "context": 0.2,
                "ml": 0.1
            }
            
            for intent in PrimaryIntent:
                combined_score = (
                    pattern_scores.get(intent, 0.0) * weights["pattern"] +
                    creator_scores.get(intent, 0.0) * weights["creator"] +
                    context_scores.get(intent, 0.0) * weights["context"] +
                    ml_scores.get(intent, 0.0) * weights["ml"]
                )
                combined_scores[intent] = combined_score
            
            # Normalize scores
            max_score = max(combined_scores.values()) if combined_scores.values() else 1.0
            if max_score > 0:
                combined_scores = {k: v / max_score for k, v in combined_scores.items()}
            
            return combined_scores
            
        except Exception as e:
            self.logger.error(f"Score combination failed: {str(e)}")
            return {intent: 0.1 for intent in PrimaryIntent}
    
    async def _determine_intents(
        self,
        combined_scores: Dict[PrimaryIntent, float]
    ) -> Tuple[PrimaryIntent, List[PrimaryIntent]]:
        """Determine primary and secondary intents"""
        try:
            # Sort intents by score
            sorted_intents = sorted(
                combined_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Primary intent is highest scoring
            primary_intent = sorted_intents[0][0]
            
            # Secondary intents are those with scores > 0.3 and within 0.4 of primary
            primary_score = sorted_intents[0][1]
            secondary_intents = []
            
            for intent, score in sorted_intents[1:]:
                if score > 0.3 and (primary_score - score) < 0.4:
                    secondary_intents.append(intent)
                if len(secondary_intents) >= 3:  # Limit to top 3 secondary intents
                    break
            
            return primary_intent, secondary_intents
            
        except Exception as e:
            self.logger.error(f"Intent determination failed: {str(e)}")
            return PrimaryIntent.GENERAL_CHAT, []
    
    async def _calculate_confidence(
        self,
        combined_scores: Dict[PrimaryIntent, float],
        primary_intent: PrimaryIntent,
        linguistic_features: Dict[str, Any]
    ) -> Tuple[float, IntentConfidence]:
        """Calculate classification confidence"""
        try:
            primary_score = combined_scores.get(primary_intent, 0.0)
            
            # Base confidence from primary score
            confidence = primary_score
            
            # Boost confidence for clear linguistic indicators
            if linguistic_features.get("starts_with_question", False):
                confidence += 0.1
            
            if linguistic_features.get("imperative_indicators", False):
                confidence += 0.1
            
            # Penalize confidence for ambiguous cases
            sorted_scores = sorted(combined_scores.values(), reverse=True)
            if len(sorted_scores) > 1:
                score_gap = sorted_scores[0] - sorted_scores[1]
                if score_gap < 0.2:
                    confidence -= 0.2
            
            # Ensure confidence is in [0, 1] range
            confidence = max(0.0, min(1.0, confidence))
            
            # Determine confidence level
            if confidence >= 0.8:
                confidence_level = IntentConfidence.HIGH
            elif confidence >= 0.6:
                confidence_level = IntentConfidence.MEDIUM
            elif confidence >= 0.4:
                confidence_level = IntentConfidence.LOW
            else:
                confidence_level = IntentConfidence.UNCERTAIN
            
            return confidence, confidence_level
            
        except Exception as e:
            self.logger.error(f"Confidence calculation failed: {str(e)}")
            return 0.5, IntentConfidence.UNCERTAIN
    
    async def _extract_intent_indicators(
        self,
        message: str,
        primary_intent: PrimaryIntent,
        creator_type: str
    ) -> List[str]:
        """Extract specific indicators that led to intent classification"""
        try:
            indicators = []
            message_lower = message.lower()
            
            # Get patterns for the primary intent
            intent_patterns = self.intent_patterns.get(primary_intent, [])
            
            # Find matching patterns
            for pattern in intent_patterns:
                if pattern in message_lower:
                    indicators.append(f"Pattern: '{pattern}'")
            
            # Creator-specific indicators
            creator_patterns = self.creator_specific_patterns.get(creator_type, {})
            if primary_intent.value in creator_patterns:
                for pattern in creator_patterns[primary_intent.value]:
                    if pattern in message_lower:
                        indicators.append(f"Creator-specific: '{pattern}'")
            
            # Linguistic indicators
            if message.endswith('?'):
                indicators.append("Question format")
            
            if any(word in message_lower for word in ['help', 'assist', 'support']):
                indicators.append("Help request")
            
            return indicators[:5]  # Limit to top 5 indicators
            
        except Exception as e:
            self.logger.error(f"Failed to extract intent indicators: {str(e)}")
            return []
    
    async def _generate_classification_reasoning(
        self,
        primary_intent: PrimaryIntent,
        combined_scores: Dict[PrimaryIntent, float],
        intent_indicators: List[str],
        confidence: float
    ) -> str:
        """Generate human-readable classification reasoning"""
        try:
            primary_score = combined_scores.get(primary_intent, 0.0)
            
            reasoning = f"Classified as '{primary_intent.value}' with {confidence:.1%} confidence. "
            reasoning += f"Primary score: {primary_score:.3f}. "
            
            if intent_indicators:
                reasoning += f"Key indicators: {', '.join(intent_indicators[:3])}. "
            
            # Add confidence explanation
            if confidence >= 0.8:
                reasoning += "High confidence due to clear intent signals."
            elif confidence >= 0.6:
                reasoning += "Medium confidence with good pattern matches."
            elif confidence >= 0.4:
                reasoning += "Low confidence due to ambiguous signals."
            else:
                reasoning += "Uncertain classification, using fallback routing."
            
            return reasoning
            
        except Exception as e:
            self.logger.error(f"Failed to generate reasoning: {str(e)}")
            return f"Classified as {primary_intent.value} with moderate confidence."
    
    def _create_fallback_classification(self, processed_message: Any) -> IntentClassificationResult:
        """Create fallback classification when main classification fails"""
        return IntentClassificationResult(
            primary_intent=PrimaryIntent.GENERAL_CHAT,
            secondary_intents=[],
            confidence=0.5,
            confidence_level=IntentConfidence.UNCERTAIN,
            intent_indicators=["Fallback classification"],
            context_factors={},
            creator_specific_intents={},
            actionable_items=["Provide more specific information"],
            suggested_responses=["I'd be happy to help! Could you provide more details?"],
            classification_reasoning="Fallback classification due to processing error"
        )
    
    def _setup_intent_patterns(self):
        """Setup pattern matching for intent classification"""
        self.intent_patterns = {
            PrimaryIntent.CONTENT_UPLOAD: [
                "upload", "share", "post", "submit", "attach", "file", "send"
            ],
            PrimaryIntent.CONTENT_ANALYSIS: [
                "analyze", "review", "check", "evaluate", "assess", "examine", "feedback"
            ],
            PrimaryIntent.MONETIZATION_QUESTION: [
                "money", "revenue", "income", "profit", "earn", "monetize", "pricing", "payment"
            ],
            PrimaryIntent.PROTECTION_CONCERN: [
                "protect", "copyright", "theft", "stolen", "piracy", "unauthorized", "secure"
            ],
            PrimaryIntent.COLLABORATION_REQUEST: [
                "collaborate", "partner", "work together", "team", "joint", "cooperation"
            ],
            PrimaryIntent.SEO_HELP: [
                "seo", "search", "ranking", "optimization", "traffic", "visibility", "keywords"
            ],
            PrimaryIntent.TECHNICAL_ISSUE: [
                "problem", "issue", "error", "bug", "not working", "broken", "fix", "trouble"
            ],
            PrimaryIntent.BUSINESS_ADVICE: [
                "business", "strategy", "advice", "guidance", "consultation", "planning"
            ],
            PrimaryIntent.CREATIVE_HELP: [
                "creative", "inspiration", "ideas", "artistic", "design", "style", "improve"
            ],
            PrimaryIntent.ANALYTICS_QUESTION: [
                "analytics", "metrics", "performance", "stats", "data", "insights", "reports"
            ],
            PrimaryIntent.PLATFORM_OPTIMIZATION: [
                "optimize", "platform", "improve", "enhance", "boost", "increase", "growth"
            ],
            PrimaryIntent.GENERAL_CHAT: [
                "hello", "hi", "thanks", "thank you", "how are you", "what can you do"
            ],
            PrimaryIntent.ACCOUNT_MANAGEMENT: [
                "account", "profile", "settings", "preferences", "subscription", "billing"
            ],
            PrimaryIntent.FEATURE_REQUEST: [
                "feature", "request", "suggestion", "add", "new", "implement", "would like"
            ],
            PrimaryIntent.FEEDBACK: [
                "feedback", "review", "opinion", "experience", "suggestion", "improvement"
            ]
        }
    
    def _setup_creator_specific_patterns(self):
        """Setup creator-type specific patterns"""
        self.creator_specific_patterns = {
            "musician": {
                "content_analysis": ["song", "track", "music", "audio", "melody", "lyrics"],
                "monetization_question": ["streaming", "royalties", "spotify", "revenue", "sales"],
                "platform_optimization": ["playlist", "discovery", "algorithm", "promotion"],
                "collaboration_request": ["featuring", "remix", "duet", "band", "producer"],
                "protection_concern": ["sampling", "cover", "original", "copyright", "dmca"]
            },
            "blogger": {
                "content_analysis": ["article", "post", "blog", "writing", "content"],
                "seo_help": ["seo", "ranking", "traffic", "keywords", "optimization"],
                "monetization_question": ["ads", "affiliate", "sponsor", "income", "monetize"],
                "analytics_question": ["traffic", "views", "engagement", "bounce rate"],
                "creative_help": ["topics", "writing", "style", "voice", "audience"]
            },
            "photographer": {
                "content_analysis": ["photo", "image", "picture", "shot", "portfolio"],
                "protection_concern": ["watermark", "copyright", "licensing", "usage rights"],
                "monetization_question": ["stock", "prints", "licensing", "client work"],
                "creative_help": ["composition", "lighting", "editing", "style"],
                "business_advice": ["pricing", "client", "contract", "portfolio"]
            },
            "influencer": {
                "analytics_question": ["followers", "engagement", "reach", "impressions"],
                "collaboration_request": ["brand", "sponsor", "partnership", "campaign"],
                "monetization_question": ["brand deals", "affiliate", "sponsored", "income"],
                "platform_optimization": ["algorithm", "growth", "visibility", "trending"],
                "content_analysis": ["post", "content", "stories", "reels", "videos"]
            },
            "comedian": {
                "creative_help": ["material", "jokes", "timing", "delivery", "performance"],
                "content_analysis": ["video", "comedy", "skit", "routine", "performance"],
                "platform_optimization": ["viral", "engagement", "algorithm", "discovery"],
                "monetization_question": ["gigs", "shows", "monetize", "comedy clubs"],
                "collaboration_request": ["other comedians", "collab", "guest", "feature"]
            }
        }
    
    def _setup_confidence_thresholds(self):
        """Setup confidence level thresholds"""
        self.confidence_thresholds = {
            IntentConfidence.HIGH: 0.8,
            IntentConfidence.MEDIUM: 0.6,
            IntentConfidence.LOW: 0.4,
            IntentConfidence.UNCERTAIN: 0.0
        }
    
    def _setup_ml_features(self):
        """Setup ML feature extraction (placeholder)"""
        self.ml_features = {
            "text_embeddings": False,  # Future: BERT/RoBERTa embeddings
            "sequence_modeling": False,  # Future: LSTM/Transformer models
            "multimodal": False,  # Future: Text + attachment analysis
            "creator_personalization": False  # Future: User-specific models
        }
    
    # Helper methods for additional functionality
    async def _extract_key_phrases(self, message: str) -> List[str]:
        """Extract key phrases from message"""
        # Simplified key phrase extraction
        words = message.lower().split()
        key_phrases = [word for word in words if len(word) > 4]
        return key_phrases[:10]
    
    async def _analyze_grammar_indicators(self, message: str) -> Dict[str, bool]:
        """Analyze grammatical indicators"""
        return {
            "has_questions": '?' in message,
            "has_imperatives": any(word in message.lower() for word in ['help', 'show', 'tell']),
            "has_conditionals": any(word in message.lower() for word in ['if', 'would', 'could']),
            "has_negations": any(word in message.lower() for word in ['not', 'no', 'never', "don't"])
        }
    
    async def _generate_actionable_items(
        self,
        primary_intent: PrimaryIntent,
        secondary_intents: List[PrimaryIntent],
        creator_type: str,
        context_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable items based on classified intent"""
        actionable_items = []
        
        # Primary intent actions
        intent_actions = {
            PrimaryIntent.CONTENT_UPLOAD: ["Process uploaded files", "Generate content analysis"],
            PrimaryIntent.MONETIZATION_QUESTION: ["Calculate revenue potential", "Suggest monetization strategies"],
            PrimaryIntent.PROTECTION_CONCERN: ["Enable content protection", "Generate fingerprints"],
            PrimaryIntent.SEO_HELP: ["Analyze SEO opportunities", "Suggest keyword optimizations"],
            PrimaryIntent.TECHNICAL_ISSUE: ["Diagnose technical problem", "Provide solution steps"]
        }
        
        actionable_items.extend(intent_actions.get(primary_intent, ["Provide relevant assistance"]))
        
        # Add creator-specific actions
        if creator_type == "musician" and primary_intent == PrimaryIntent.PLATFORM_OPTIMIZATION:
            actionable_items.append("Optimize Spotify artist profile")
        
        return actionable_items[:5]
    
    async def _generate_response_suggestions(
        self,
        primary_intent: PrimaryIntent,
        creator_type: str,
        context_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate suggested response approaches"""
        suggestions = []
        
        # Intent-based suggestions
        if primary_intent == PrimaryIntent.CONTENT_ANALYSIS:
            suggestions.append("Provide detailed content analysis with optimization recommendations")
        elif primary_intent == PrimaryIntent.MONETIZATION_QUESTION:
            suggestions.append("Share monetization strategies specific to creator type")
        elif primary_intent == PrimaryIntent.TECHNICAL_ISSUE:
            suggestions.append("Offer step-by-step troubleshooting guidance")
        
        # Creator-specific suggestions
        creator_suggestions = {
            "musician": "Include music industry insights and Spotify optimization tips",
            "blogger": "Provide SEO guidance and content strategy recommendations",
            "photographer": "Offer portfolio optimization and licensing advice",
            "influencer": "Share social media growth and engagement strategies",
            "comedian": "Provide performance tips and content creation guidance"
        }
        
        if creator_type in creator_suggestions:
            suggestions.append(creator_suggestions[creator_type])
        
        return suggestions[:3]
    
    async def _extract_creator_specific_intents(
        self,
        message: str,
        primary_intent: PrimaryIntent,
        creator_type: str
    ) -> Dict[str, Any]:
        """Extract intents specific to creator type"""
        creator_intents = {}
        message_lower = message.lower()
        
        if creator_type == "musician":
            if "spotify" in message_lower:
                creator_intents["spotify_optimization"] = True
            if any(word in message_lower for word in ["playlist", "discover"]):
                creator_intents["playlist_strategy"] = True
            if "collaborate" in message_lower:
                creator_intents["music_collaboration"] = True
        
        elif creator_type == "blogger":
            if "seo" in message_lower:
                creator_intents["seo_focus"] = True
            if any(word in message_lower for word in ["traffic", "ranking"]):
                creator_intents["traffic_growth"] = True
            if "monetize" in message_lower:
                creator_intents["blog_monetization"] = True
        
        return creator_intents
    
    async def _update_classification_metrics(
        self,
        classification_result: IntentClassificationResult,
        creator_type: str
    ):
        """Update classification performance metrics"""
        self.classification_metrics["total_classifications"] += 1
        
        if classification_result.confidence_level == IntentConfidence.HIGH:
            self.classification_metrics["high_confidence_count"] += 1
        
        # Track creator-specific performance
        if creator_type not in self.classification_metrics["creator_type_performance"]:
            self.classification_metrics["creator_type_performance"][creator_type] = {
                "total": 0,
                "high_confidence": 0
            }
        
        self.classification_metrics["creator_type_performance"][creator_type]["total"] += 1
        
        if classification_result.confidence_level == IntentConfidence.HIGH:
            self.classification_metrics["creator_type_performance"][creator_type]["high_confidence"] += 1
