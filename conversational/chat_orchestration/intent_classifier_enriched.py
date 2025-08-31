"""Intent Classifier - Enterprise intent recognition for creator conversations
==========================================================================

Advanced ML-powered intent classification system for multi-format content creators
with specialized recognition patterns for music, photography, blogging, influencer
marketing, and comedy content creation workflows.

Features:
- Multi-layered intent classification with hierarchical categories
- Creator-specific intent patterns and vocabularies
- Real-time learning and adaptation from conversation patterns
- Contextual intent understanding with conversation memory
- Confidence scoring and uncertainty handling
- Performance monitoring and analytics integration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are proprietary intellectual property of Fahed Mlaiel.
Unauthorized copying, modification, distribution, or use without explicit written
permission is strictly prohibited and will result in legal action.
"""
import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime
import re
from collections import defaultdict, Counter
import numpy as np

from backend.ai.models import ConversationalAI
from backend.monitoring.analytics import AnalyticsTracker
from backend.core.config import settings
from backend.ml.models import IntentClassificationModel
from backend.utils.text_processor import TextProcessor


class PrimaryIntentCategory(Enum):
    """Primary intent categories for creator conversations"""    CONTENT_CREATION = "content_creation"
    MONETIZATION = "monetization"
    PROTECTION = "protection"
    COLLABORATION = "collaboration"
    TECHNICAL_SUPPORT = "technical_support"
    LEARNING = "learning"
    ANALYTICS = "analytics"
    STRATEGY = "strategy"
    COMMUNITY = "community"
    LEGAL = "legal"
    MARKETING = "marketing"
    DISTRIBUTION = "distribution"


class CreatorSpecificIntent(Enum):
    """Creator-specific intent subcategories"""    # Music-specific
    MUSIC_PRODUCTION = "music_production"
    SONG_COLLABORATION = "song_collaboration"
    ROYALTY_MANAGEMENT = "royalty_management"
    MUSIC_DISTRIBUTION = "music_distribution"
    PERFORMANCE_BOOKING = "performance_booking"
    
    # Photography-specific
    PHOTO_EDITING = "photo_editing"
    PORTFOLIO_REVIEW = "portfolio_review"
    CLIENT_MANAGEMENT = "client_management"
    LICENSING_INQUIRY = "licensing_inquiry"
    EQUIPMENT_ADVICE = "equipment_advice"
    
    # Blogging-specific
    CONTENT_PLANNING = "content_planning"
    SEO_OPTIMIZATION = "seo_optimization"
    AUDIENCE_GROWTH = "audience_growth"
    BLOG_MONETIZATION = "blog_monetization"
    WRITING_IMPROVEMENT = "writing_improvement"
    
    # Influencer-specific
    BRAND_PARTNERSHIPS = "brand_partnerships"
    SOCIAL_MEDIA_STRATEGY = "social_media_strategy"
    ENGAGEMENT_OPTIMIZATION = "engagement_optimization"
    CONTENT_SCHEDULING = "content_scheduling"
    AUDIENCE_ANALYSIS = "audience_analysis"
    
    # Comedy-specific
    MATERIAL_DEVELOPMENT = "material_development"
    VENUE_BOOKING = "venue_booking"
    AUDIENCE_FEEDBACK = "audience_feedback"
    JOKE_PROTECTION = "joke_protection"
    COMEDY_NETWORKING = "comedy_networking"


class IntentUrgency(Enum):
    """Intent urgency levels"""    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class IntentComplexity(Enum):
    """Intent complexity levels"""    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    MULTI_STEP = "multi_step"
    EXPERT_REQUIRED = "expert_required"


@dataclass
class IntentContext:
    """Contextual information for intent classification"""    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    creator_specializations: List[str] = field(default_factory=list)
    current_projects: List[str] = field(default_factory=list)
    recent_activities: List[str] = field(default_factory=list)
    platform_context: Dict[str, Any] = field(default_factory=dict)
    temporal_context: Dict[str, Any] = field(default_factory=dict)
    emotional_context: Dict[str, str] = field(default_factory=dict)


@dataclass
class IntentClassificationResult:
    """Comprehensive intent classification result"""    classification_id: str
    primary_intent: PrimaryIntentCategory
    secondary_intents: List[PrimaryIntentCategory] = field(default_factory=list)
    creator_specific_intent: Optional[CreatorSpecificIntent] = None
    confidence_score: float = 0.0
    urgency: IntentUrgency = IntentUrgency.NORMAL
    complexity: IntentComplexity = IntentComplexity.SIMPLE
    entities: Dict[str, List[str]] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    context_factors: Dict[str, Any] = field(default_factory=dict)
    suggested_actions: List[str] = field(default_factory=list)
    routing_recommendations: List[str] = field(default_factory=list)
    alternative_interpretations: List[Dict[str, Any]] = field(default_factory=list)
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class EnterpriseIntentClassifier:
    """    Enterprise-grade intent classification system for creator conversations
    with advanced ML models, contextual understanding, and creator-specific
    optimizations.
    
    This classifier provides:
    - Multi-layered intent recognition with hierarchical categories
    - Creator-specific pattern recognition and vocabulary adaptation
    - Contextual intent understanding with conversation memory
    - Real-time learning and model improvement
    - Confidence scoring and uncertainty handling
    - Performance analytics and monitoring
    """    
    def __init__(
        self,
        ai_engine: ConversationalAI,
        analytics_tracker: AnalyticsTracker,
        intent_model: Optional[IntentClassificationModel] = None
    ):
        self.ai_engine = ai_engine
        self.analytics = analytics_tracker
        self.intent_model = intent_model
        self.text_processor = TextProcessor()
        
        # Intent patterns and vocabularies
        self.intent_patterns = self._load_intent_patterns()
        self.creator_vocabularies = self._load_creator_vocabularies()
        self.entity_extractors = self._initialize_entity_extractors()
        
        # Classification metrics
        self.classification_metrics = {
            "total_classifications": 0,
            "accuracy_score": 0.0,
            "avg_confidence": 0.0,
            "creator_type_distribution": defaultdict(int),
            "intent_distribution": defaultdict(int),
            "error_rate": 0.0
        }
        
        # Configuration
        self.min_confidence_threshold = settings.get("intent.min_confidence", 0.7)
        self.enable_learning = settings.get("intent.enable_learning", True)
        self.max_alternative_intents = settings.get("intent.max_alternatives", 3)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
    
    async def classify_intent(
        self,
        processed_message: Any,  # ProcessedMessage object
        context_analysis: Dict[str, Any],
        creator_profile: Any,  # CreatorProfile object
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> IntentClassificationResult:
        """        Classify user intent with comprehensive analysis and creator-specific optimization
        
        Args:
            processed_message: Processed message object with content and metadata
            context_analysis: Context analysis from conversation analyzer
            creator_profile: Creator profile with specializations and preferences
            conversation_history: Recent conversation history for context
            
        Returns:
            IntentClassificationResult with comprehensive classification details
        """        classification_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # Extract message content and metadata
            message_content = processed_message.processed_content
            message_type = processed_message.message_type
            attachments = processed_message.attachments
            
            # Build intent context
            intent_context = await self._build_intent_context(
                creator_profile,
                context_analysis,
                conversation_history or []
            )
            
            # Preprocess message for classification
            preprocessed_content = await self._preprocess_for_classification(
                message_content,
                message_type,
                creator_profile
            )
            
            # Extract entities and keywords
            entities = await self._extract_entities(
                preprocessed_content,
                creator_profile,
                intent_context
            )
            
            keywords = await self._extract_keywords(
                preprocessed_content,
                creator_profile,
                intent_context
            )
            
            # Perform multi-layered intent classification
            primary_classification = await self._classify_primary_intent(
                preprocessed_content,
                entities,
                keywords,
                intent_context,
                creator_profile
            )
            
            # Classify secondary intents
            secondary_intents = await self._classify_secondary_intents(
                preprocessed_content,
                primary_classification,
                intent_context,
                creator_profile
            )
            
            # Classify creator-specific intent
            creator_specific_intent = await self._classify_creator_specific_intent(
                preprocessed_content,
                primary_classification,
                creator_profile,
                intent_context
            )
            
            # Determine intent urgency
            urgency = await self._determine_intent_urgency(
                primary_classification,
                entities,
                intent_context,
                processed_message
            )
            
            # Assess intent complexity
            complexity = await self._assess_intent_complexity(
                primary_classification,
                secondary_intents,
                entities,
                intent_context
            )
            
            # Calculate overall confidence score
            confidence_score = await self._calculate_confidence_score(
                primary_classification,
                secondary_intents,
                creator_specific_intent,
                entities
            )
            
            # Generate suggested actions
            suggested_actions = await self._generate_suggested_actions(
                primary_classification,
                creator_specific_intent,
                creator_profile,
                intent_context
            )
            
            # Generate routing recommendations
            routing_recommendations = await self._generate_routing_recommendations(
                primary_classification,
                urgency,
                complexity,
                creator_profile
            )
            
            # Generate alternative interpretations if confidence is low
            alternative_interpretations = []
            if confidence_score < self.min_confidence_threshold:
                alternative_interpretations = await self._generate_alternative_interpretations(
                    preprocessed_content,
                    entities,
                    intent_context,
                    creator_profile
                )
            
            # Extract context factors
            context_factors = await self._extract_context_factors(
                intent_context,
                context_analysis,
                processed_message
            )
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Create classification result
            result = IntentClassificationResult(
                classification_id=classification_id,
                primary_intent=primary_classification,
                secondary_intents=secondary_intents,
                creator_specific_intent=creator_specific_intent,
                confidence_score=confidence_score,
                urgency=urgency,
                complexity=complexity,
                entities=entities,
                keywords=keywords,
                context_factors=context_factors,
                suggested_actions=suggested_actions,
                routing_recommendations=routing_recommendations,
                alternative_interpretations=alternative_interpretations,
                processing_metadata={
                    "processing_time_ms": processing_time,
                    "model_version": self.ai_engine.get_model_version(),
                    "creator_type": creator_profile.creator_type.value,
                    "message_type": message_type.value if hasattr(message_type, 'value') else str(message_type),
                    "confidence_threshold": self.min_confidence_threshold,
                    "classification_method": "enterprise_ml"
                },
                timestamp=datetime.utcnow()
            )
            
            # Track classification analytics
            await self._track_classification_analytics(result, creator_profile)
            
            # Update metrics
            self._update_classification_metrics(result, processing_time)
            
            # Adaptive learning if enabled
            if self.enable_learning:
                await self._update_learning_models(result, preprocessed_content, intent_context)
            
            self.logger.info(
                f"Classified intent {classification_id}: {primary_classification.value} "
                f"(confidence: {confidence_score:.2f})"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to classify intent {classification_id}: {str(e)}")
            
            # Track error
            await self.analytics.track_error(
                "intent_classification_error",
                str(e),
                {"classification_id": classification_id}
            )
            
            # Return fallback classification
            return self._create_fallback_classification(
                classification_id,
                processed_message,
                creator_profile,
                str(e)
            )
    
    async def _build_intent_context(
        self,
        creator_profile: Any,
        context_analysis: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> IntentContext:
        """Build comprehensive intent context for classification"""        
        return IntentContext(
            conversation_history=conversation_history,
            creator_specializations=creator_profile.specializations,
            current_projects=creator_profile.collaboration_interests,
            recent_activities=context_analysis.get("recent_activities", []),
            platform_context=context_analysis.get("platform_context", {}),
            temporal_context={
                "time_of_day": datetime.utcnow().hour,
                "day_of_week": datetime.utcnow().weekday(),
                "conversation_length": len(conversation_history)
            },
            emotional_context=context_analysis.get("emotional_context", {})
        )
    
    async def _preprocess_for_classification(
        self,
        content: str,
        message_type: Any,
        creator_profile: Any
    ) -> str:
        """Preprocess message content for intent classification"""        
        # Basic text cleaning
        preprocessed = self.text_processor.clean_text(content)
        
        # Creator-specific preprocessing
        creator_type = creator_profile.creator_type.value
        
        if creator_type == "musician":
            # Expand music-related abbreviations and terminology
            preprocessed = self._expand_music_terminology(preprocessed)
        elif creator_type == "photographer":
            # Expand photography terminology
            preprocessed = self._expand_photography_terminology(preprocessed)
        elif creator_type == "blogger":
            # Expand blogging and SEO terminology
            preprocessed = self._expand_blogging_terminology(preprocessed)
        
        # Normalize common intent phrases
        preprocessed = self._normalize_intent_phrases(preprocessed)
        
        return preprocessed
    
    async def _extract_entities(
        self,
        content: str,
        creator_profile: Any,
        context: IntentContext
    ) -> Dict[str, List[str]]:
        """Extract entities relevant to creator workflows"""        
        entities = defaultdict(list)
        
        # Use AI engine for general entity extraction
        ai_entities = await self.ai_engine.extract_entities(content)
        entities.update(ai_entities)
        
        # Creator-specific entity extraction
        creator_type = creator_profile.creator_type.value
        
        if creator_type == "musician":
            entities.update(await self._extract_music_entities(content))
        elif creator_type == "photographer":
            entities.update(await self._extract_photography_entities(content))
        elif creator_type == "blogger":
            entities.update(await self._extract_blogging_entities(content))
        elif creator_type == "influencer":
            entities.update(await self._extract_influencer_entities(content))
        elif creator_type == "comedian":
            entities.update(await self._extract_comedy_entities(content))
        
        return dict(entities)
    
    async def _extract_keywords(
        self,
        content: str,
        creator_profile: Any,
        context: IntentContext
    ) -> List[str]:
        """Extract intent-relevant keywords"""        
        # Use text processor for general keyword extraction
        general_keywords = self.text_processor.extract_keywords(content)
        
        # Add creator-specific keywords
        creator_keywords = self._get_creator_specific_keywords(
            content,
            creator_profile.creator_type.value
        )
        
        # Combine and deduplicate
        all_keywords = list(set(general_keywords + creator_keywords))
        
        # Sort by relevance (implementation would use scoring)
        return all_keywords[:20]  # Top 20 keywords
    
    async def _classify_primary_intent(
        self,
        content: str,
        entities: Dict[str, List[str]],
        keywords: List[str],
        context: IntentContext,
        creator_profile: Any
    ) -> PrimaryIntentCategory:
        """Classify primary intent using ML models and pattern matching"""        
        # Use ML model if available
        if self.intent_model:
            ml_prediction = await self.intent_model.predict_intent(
                content, entities, keywords, context
            )
            if ml_prediction["confidence"] > self.min_confidence_threshold:
                return PrimaryIntentCategory(ml_prediction["intent"])
        
        # Fallback to pattern-based classification
        return await self._pattern_based_classification(
            content, entities, keywords, context, creator_profile
        )
    
    async def _pattern_based_classification(
        self,
        content: str,
        entities: Dict[str, List[str]],
        keywords: List[str],
        context: IntentContext,
        creator_profile: Any
    ) -> PrimaryIntentCategory:
        """Pattern-based intent classification as fallback"""        
        content_lower = content.lower()
        
        # Monetization intent patterns
        monetization_patterns = [
            r"\\b(money|revenue|income|earn|profit|monetize|sell|price|cost)\\b",
            r"\\b(sponsor|brand deal|partnership|collaboration fee)\\b",
            r"\\b(subscription|patreon|donations|tips)\\b"
        ]
        
        if any(re.search(pattern, content_lower) for pattern in monetization_patterns):
            return PrimaryIntentCategory.MONETIZATION
        
        # Protection intent patterns
        protection_patterns = [
            r"\\b(copyright|protect|steal|stolen|piracy|dmca|takedown)\\b",
            r"\\b(license|licensing|permission|unauthorized)\\b",
            r"\\b(intellectual property|ip|trademark)\\b"
        ]
        
        if any(re.search(pattern, content_lower) for pattern in protection_patterns):
            return PrimaryIntentCategory.PROTECTION
        
        # Collaboration intent patterns
        collaboration_patterns = [
            r"\\b(collaborate|collab|partner|work together|team up)\\b",
            r"\\b(feature|featuring|guest|duet|remix)\\b",
            r"\\b(network|connect|introduce|referral)\\b"
        ]
        
        if any(re.search(pattern, content_lower) for pattern in collaboration_patterns):
            return PrimaryIntentCategory.COLLABORATION
        
        # Content creation patterns
        creation_patterns = [
            r"\\b(create|make|produce|develop|design|write|compose)\\b",
            r"\\b(content|video|photo|song|blog|post|article)\\b",
            r"\\b(idea|concept|theme|style|format)\\b"
        ]
        
        if any(re.search(pattern, content_lower) for pattern in creation_patterns):
            return PrimaryIntentCategory.CONTENT_CREATION
        
        # Learning intent patterns
        learning_patterns = [
            r"\\b(learn|teach|tutorial|guide|how to|explain)\\b",
            r"\\b(course|training|workshop|education|skill)\\b",
            r"\\b(improve|better|enhance|develop|master)\\b"
        ]
        
        if any(re.search(pattern, content_lower) for pattern in learning_patterns):
            return PrimaryIntentCategory.LEARNING
        
        # Technical support patterns
        technical_patterns = [
            r"\\b(problem|issue|bug|error|broken|not working)\\b",
            r"\\b(help|support|fix|solve|troubleshoot)\\b",
            r"\\b(technical|tech|software|platform|tool)\\b"
        ]
        
        if any(re.search(pattern, content_lower) for pattern in technical_patterns):
            return PrimaryIntentCategory.TECHNICAL_SUPPORT
        
        # Analytics patterns
        analytics_patterns = [
            r"\\b(analytics|metrics|data|statistics|performance)\\b",
            r"\\b(views|likes|shares|engagement|reach|impressions)\\b",
            r"\\b(track|measure|analyze|report|dashboard)\\b"
        ]
        
        if any(re.search(pattern, content_lower) for pattern in analytics_patterns):
            return PrimaryIntentCategory.ANALYTICS
        
        # Default to strategy for complex queries
        return PrimaryIntentCategory.STRATEGY
    
    async def _classify_secondary_intents(
        self,
        content: str,
        primary_intent: PrimaryIntentCategory,
        context: IntentContext,
        creator_profile: Any
    ) -> List[PrimaryIntentCategory]:
        """Classify secondary intents that might be present"""        
        secondary_intents = []
        
        # Implementation would identify additional intents in the message
        # For now, return empty list
        
        return secondary_intents
    
    async def _classify_creator_specific_intent(
        self,
        content: str,
        primary_intent: PrimaryIntentCategory,
        creator_profile: Any,
        context: IntentContext
    ) -> Optional[CreatorSpecificIntent]:
        """Classify creator-specific intent subcategories"""        
        creator_type = creator_profile.creator_type.value
        content_lower = content.lower()
        
        if creator_type == "musician":
            # Music-specific intent classification
            if "production" in content_lower or "recording" in content_lower:
                return CreatorSpecificIntent.MUSIC_PRODUCTION
            elif "collaboration" in content_lower or "feature" in content_lower:
                return CreatorSpecificIntent.SONG_COLLABORATION
            elif "royalty" in content_lower or "streaming" in content_lower:
                return CreatorSpecificIntent.ROYALTY_MANAGEMENT
            elif "distribution" in content_lower or "release" in content_lower:
                return CreatorSpecificIntent.MUSIC_DISTRIBUTION
            elif "performance" in content_lower or "gig" in content_lower:
                return CreatorSpecificIntent.PERFORMANCE_BOOKING
        
        elif creator_type == "photographer":
            # Photography-specific intent classification
            if "editing" in content_lower or "photoshop" in content_lower:
                return CreatorSpecificIntent.PHOTO_EDITING
            elif "portfolio" in content_lower or "gallery" in content_lower:
                return CreatorSpecificIntent.PORTFOLIO_REVIEW
            elif "client" in content_lower or "customer" in content_lower:
                return CreatorSpecificIntent.CLIENT_MANAGEMENT
            elif "license" in content_lower or "usage rights" in content_lower:
                return CreatorSpecificIntent.LICENSING_INQUIRY
            elif "camera" in content_lower or "equipment" in content_lower:
                return CreatorSpecificIntent.EQUIPMENT_ADVICE
        
        elif creator_type == "blogger":
            # Blogging-specific intent classification
            if "content plan" in content_lower or "editorial" in content_lower:
                return CreatorSpecificIntent.CONTENT_PLANNING
            elif "seo" in content_lower or "search" in content_lower:
                return CreatorSpecificIntent.SEO_OPTIMIZATION
            elif "audience" in content_lower or "readers" in content_lower:
                return CreatorSpecificIntent.AUDIENCE_GROWTH
            elif "monetize" in content_lower or "income" in content_lower:
                return CreatorSpecificIntent.BLOG_MONETIZATION
            elif "writing" in content_lower or "style" in content_lower:
                return CreatorSpecificIntent.WRITING_IMPROVEMENT
        
        elif creator_type == "influencer":
            # Influencer-specific intent classification
            if "brand" in content_lower or "sponsor" in content_lower:
                return CreatorSpecificIntent.BRAND_PARTNERSHIPS
            elif "social media" in content_lower or "strategy" in content_lower:
                return CreatorSpecificIntent.SOCIAL_MEDIA_STRATEGY
            elif "engagement" in content_lower or "interaction" in content_lower:
                return CreatorSpecificIntent.ENGAGEMENT_OPTIMIZATION
            elif "schedule" in content_lower or "posting" in content_lower:
                return CreatorSpecificIntent.CONTENT_SCHEDULING
            elif "analytics" in content_lower or "insights" in content_lower:
                return CreatorSpecificIntent.AUDIENCE_ANALYSIS
        
        elif creator_type == "comedian":
            # Comedy-specific intent classification
            if "material" in content_lower or "jokes" in content_lower:
                return CreatorSpecificIntent.MATERIAL_DEVELOPMENT
            elif "venue" in content_lower or "booking" in content_lower:
                return CreatorSpecificIntent.VENUE_BOOKING
            elif "audience feedback" in content_lower or "response" in content_lower:
                return CreatorSpecificIntent.AUDIENCE_FEEDBACK
            elif "protect" in content_lower or "steal" in content_lower:
                return CreatorSpecificIntent.JOKE_PROTECTION
            elif "network" in content_lower or "comedian" in content_lower:
                return CreatorSpecificIntent.COMEDY_NETWORKING
        
        return None
    
    async def _determine_intent_urgency(
        self,
        primary_intent: PrimaryIntentCategory,
        entities: Dict[str, List[str]],
        context: IntentContext,
        processed_message: Any
    ) -> IntentUrgency:
        """Determine the urgency level of the intent"""        
        # Check for urgent keywords
        urgent_keywords = ["urgent", "asap", "immediately", "emergency", "critical", "deadline"]
        content = processed_message.processed_content.lower()
        
        if any(keyword in content for keyword in urgent_keywords):
            return IntentUrgency.URGENT
        
        # Protection issues are typically high priority
        if primary_intent == PrimaryIntentCategory.PROTECTION:
            return IntentUrgency.HIGH
        
        # Technical issues might be urgent
        if primary_intent == PrimaryIntentCategory.TECHNICAL_SUPPORT:
            if any(word in content for word in ["broken", "not working", "error", "bug"]):
                return IntentUrgency.HIGH
        
        # Time-sensitive terms
        time_sensitive = ["today", "tonight", "tomorrow", "this week"]
        if any(term in content for term in time_sensitive):
            return IntentUrgency.HIGH
        
        return IntentUrgency.NORMAL
    
    async def _assess_intent_complexity(
        self,
        primary_intent: PrimaryIntentCategory,
        secondary_intents: List[PrimaryIntentCategory],
        entities: Dict[str, List[str]],
        context: IntentContext
    ) -> IntentComplexity:
        """Assess the complexity level of the intent"""        
        # Multiple intents increase complexity
        if len(secondary_intents) > 1:
            return IntentComplexity.COMPLEX
        
        # Large number of entities suggests complexity
        total_entities = sum(len(entity_list) for entity_list in entities.values())
        if total_entities > 10:
            return IntentComplexity.COMPLEX
        
        # Certain intent types are inherently complex
        complex_intents = [
            PrimaryIntentCategory.STRATEGY,
            PrimaryIntentCategory.LEGAL,
            PrimaryIntentCategory.ANALYTICS
        ]
        
        if primary_intent in complex_intents:
            return IntentComplexity.MODERATE
        
        return IntentComplexity.SIMPLE
    
    async def _calculate_confidence_score(
        self,
        primary_intent: PrimaryIntentCategory,
        secondary_intents: List[PrimaryIntentCategory],
        creator_specific_intent: Optional[CreatorSpecificIntent],
        entities: Dict[str, List[str]]
    ) -> float:
        """Calculate overall confidence score for the classification"""        
        base_confidence = 0.8  # Base confidence for pattern matching
        
        # Boost confidence if creator-specific intent was found
        if creator_specific_intent:
            base_confidence += 0.1
        
        # Reduce confidence if many secondary intents (ambiguous)
        if len(secondary_intents) > 2:
            base_confidence -= 0.2
        
        # Boost confidence based on relevant entities
        relevant_entity_types = ["person", "organization", "product", "service"]
        relevant_entities = sum(
            1 for entity_type in relevant_entity_types 
            if entity_type in entities and entities[entity_type]
        )
        
        base_confidence += min(0.1, relevant_entities * 0.025)
        
        return min(1.0, max(0.0, base_confidence))
    
    # Helper methods for entity extraction
    async def _extract_music_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract music-specific entities"""        entities = defaultdict(list)
        
        # Music genres
        genres = re.findall(r'\\b(rock|pop|jazz|classical|hip.hop|rap|country|blues|electronic|folk)\\b', content.lower())
        if genres:
            entities["music_genres"].extend(genres)
        
        # Instruments
        instruments = re.findall(r'\\b(guitar|piano|drums|bass|violin|saxophone|synthesizer)\\b', content.lower())
        if instruments:
            entities["instruments"].extend(instruments)
        
        return dict(entities)
    
    async def _extract_photography_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract photography-specific entities"""        entities = defaultdict(list)
        
        # Camera brands
        camera_brands = re.findall(r'\\b(canon|nikon|sony|fujifilm|olympus|pentax|leica)\\b', content.lower())
        if camera_brands:
            entities["camera_brands"].extend(camera_brands)
        
        # Photography styles
        styles = re.findall(r'\\b(portrait|landscape|street|macro|wildlife|wedding|fashion)\\b', content.lower())
        if styles:
            entities["photography_styles"].extend(styles)
        
        return dict(entities)
    
    async def _extract_blogging_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract blogging-specific entities"""        entities = defaultdict(list)
        
        # Content management systems
        cms = re.findall(r'\\b(wordpress|blogger|medium|ghost|squarespace|wix)\\b', content.lower())
        if cms:
            entities["cms_platforms"].extend(cms)
        
        # SEO terms
        seo_terms = re.findall(r'\\b(keyword|backlink|ranking|organic|search engine)\\b', content.lower())
        if seo_terms:
            entities["seo_terms"].extend(seo_terms)
        
        return dict(entities)
    
    async def _extract_influencer_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract influencer-specific entities"""        entities = defaultdict(list)
        
        # Social platforms
        platforms = re.findall(r'\\b(instagram|tiktok|youtube|twitter|facebook|linkedin|pinterest)\\b', content.lower())
        if platforms:
            entities["social_platforms"].extend(platforms)
        
        # Brand types
        brand_types = re.findall(r'\\b(fashion|beauty|tech|fitness|food|travel|lifestyle)\\b', content.lower())
        if brand_types:
            entities["brand_categories"].extend(brand_types)
        
        return dict(entities)
    
    async def _extract_comedy_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract comedy-specific entities"""        entities = defaultdict(list)
        
        # Comedy styles
        styles = re.findall(r'\\b(standup|improv|sketch|satire|observational|dark.comedy)\\b', content.lower())
        if styles:
            entities["comedy_styles"].extend(styles)
        
        # Venue types
        venues = re.findall(r'\\b(comedy.club|theater|bar|festival|open.mic)\\b', content.lower())
        if venues:
            entities["venue_types"].extend(venues)
        
        return dict(entities)
    
    # Additional helper methods
    def _expand_music_terminology(self, content: str) -> str:
        """Expand music-related abbreviations and terminology"""        expansions = {
            "daw": "digital audio workstation",
            "bpm": "beats per minute",
            "eq": "equalizer",
            "vst": "virtual studio technology"
        }
        
        for abbrev, expansion in expansions.items():
            content = re.sub(f"\\b{abbrev}\\b", expansion, content, flags=re.IGNORECASE)
        
        return content
    
    def _expand_photography_terminology(self, content: str) -> str:
        """Expand photography-related terminology"""        expansions = {
            "iso": "international standards organization",
            "dslr": "digital single lens reflex",
            "hdr": "high dynamic range",
            "bokeh": "background blur"
        }
        
        for abbrev, expansion in expansions.items():
            content = re.sub(f"\\b{abbrev}\\b", expansion, content, flags=re.IGNORECASE)
        
        return content
    
    def _expand_blogging_terminology(self, content: str) -> str:
        """Expand blogging and SEO terminology"""        expansions = {
            "seo": "search engine optimization",
            "cms": "content management system",
            "cta": "call to action",
            "ctr": "click through rate"
        }
        
        for abbrev, expansion in expansions.items():
            content = re.sub(f"\\b{abbrev}\\b", expansion, content, flags=re.IGNORECASE)
        
        return content
    
    def _normalize_intent_phrases(self, content: str) -> str:
        """Normalize common intent phrases for better matching"""        normalizations = {
            r"how do i": "how to",
            r"what should i": "how to",
            r"can you help me": "help with",
            r"i need to": "need to",
            r"i want to": "want to"
        }
        
        for pattern, replacement in normalizations.items():
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        return content
    
    def _get_creator_specific_keywords(self, content: str, creator_type: str) -> List[str]:
        """Get creator-specific keywords from content"""        
        creator_keywords = {
            "musician": ["music", "song", "album", "band", "artist", "melody", "rhythm", "harmony"],
            "photographer": ["photo", "image", "camera", "lens", "shoot", "portfolio", "client"],
            "blogger": ["blog", "post", "article", "content", "writing", "audience", "traffic"],
            "influencer": ["brand", "sponsor", "engagement", "followers", "social", "platform"],
            "comedian": ["comedy", "joke", "laugh", "audience", "performance", "material", "funny"]
        }
        
        keywords = creator_keywords.get(creator_type, [])
        found_keywords = [kw for kw in keywords if kw in content.lower()]
        
        return found_keywords
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent patterns from configuration"""        # Implementation would load from configuration files
        return {}
    
    def _load_creator_vocabularies(self) -> Dict[str, Dict[str, List[str]]]:
        """Load creator-specific vocabularies"""        # Implementation would load from configuration files
        return {}
    
    def _initialize_entity_extractors(self) -> Dict[str, Any]:
        """Initialize entity extraction models"""        # Implementation would initialize NER models
        return {}
    
    async def _generate_suggested_actions(
        self,
        primary_intent: PrimaryIntentCategory,
        creator_specific_intent: Optional[CreatorSpecificIntent],
        creator_profile: Any,
        context: IntentContext
    ) -> List[str]:
        """Generate suggested actions based on classified intent"""        
        actions = []
        
        if primary_intent == PrimaryIntentCategory.MONETIZATION:
            actions.extend([
                "Review current revenue streams",
                "Explore new monetization opportunities",
                "Analyze audience demographics for targeted offers"
            ])
        
        elif primary_intent == PrimaryIntentCategory.PROTECTION:
            actions.extend([
                "Enable content protection monitoring",
                "Review copyright settings",
                "Consider watermarking original content"
            ])
        
        elif primary_intent == PrimaryIntentCategory.COLLABORATION:
            actions.extend([
                "Search for potential collaborators",
                "Update collaboration preferences",
                "Review partnership agreements"
            ])
        
        return actions
    
    async def _generate_routing_recommendations(
        self,
        primary_intent: PrimaryIntentCategory,
        urgency: IntentUrgency,
        complexity: IntentComplexity,
        creator_profile: Any
    ) -> List[str]:
        """Generate routing recommendations for conversation handling"""        
        recommendations = []
        
        if urgency in [IntentUrgency.URGENT, IntentUrgency.CRITICAL]:
            recommendations.append("priority_queue")
        
        if complexity == IntentComplexity.EXPERT_REQUIRED:
            recommendations.append("expert_consultation")
        
        if primary_intent == PrimaryIntentCategory.LEGAL:
            recommendations.append("legal_specialist")
        
        return recommendations
    
    async def _generate_alternative_interpretations(
        self,
        content: str,
        entities: Dict[str, List[str]],
        context: IntentContext,
        creator_profile: Any
    ) -> List[Dict[str, Any]]:
        """Generate alternative intent interpretations for low-confidence classifications"""        
        alternatives = []
        
        # Implementation would generate alternative interpretations
        # For now, return empty list
        
        return alternatives
    
    async def _extract_context_factors(
        self,
        intent_context: IntentContext,
        context_analysis: Dict[str, Any],
        processed_message: Any
    ) -> Dict[str, Any]:
        """Extract context factors that influenced classification"""        
        return {
            "conversation_length": len(intent_context.conversation_history),
            "creator_specializations": intent_context.creator_specializations,
            "temporal_context": intent_context.temporal_context,
            "emotional_context": intent_context.emotional_context,
            "message_type": str(processed_message.message_type),
            "has_attachments": len(processed_message.attachments) > 0
        }
    
    async def _track_classification_analytics(
        self,
        result: IntentClassificationResult,
        creator_profile: Any
    ) -> None:
        """Track intent classification analytics"""        
        await self.analytics.track_event(
            "intent_classified",
            {
                "classification_id": result.classification_id,
                "primary_intent": result.primary_intent.value,
                "creator_type": creator_profile.creator_type.value,
                "confidence_score": result.confidence_score,
                "urgency": result.urgency.value,
                "complexity": result.complexity.value,
                "processing_time_ms": result.processing_metadata.get("processing_time_ms", 0)
            }
        )
    
    def _update_classification_metrics(
        self,
        result: IntentClassificationResult,
        processing_time: float
    ) -> None:
        """Update internal classification metrics"""        
        self.classification_metrics["total_classifications"] += 1
        
        # Update averages
        total = self.classification_metrics["total_classifications"]
        current_avg_confidence = self.classification_metrics["avg_confidence"]
        self.classification_metrics["avg_confidence"] = (
            (current_avg_confidence * (total - 1) + result.confidence_score) / total
        )
        
        # Update distributions
        creator_type = result.processing_metadata.get("creator_type", "unknown")
        self.classification_metrics["creator_type_distribution"][creator_type] += 1
        self.classification_metrics["intent_distribution"][result.primary_intent.value] += 1
    
    async def _update_learning_models(
        self,
        result: IntentClassificationResult,
        content: str,
        context: IntentContext
    ) -> None:
        """Update learning models with classification result"""        
        if self.intent_model:
            await self.intent_model.update_with_feedback(
                content=content,
                predicted_intent=result.primary_intent.value,
                confidence=result.confidence_score,
                context=context
            )
    
    def _create_fallback_classification(
        self,
        classification_id: str,
        processed_message: Any,
        creator_profile: Any,
        error: str
    ) -> IntentClassificationResult:
        """Create fallback classification result for errors"""        
        return IntentClassificationResult(
            classification_id=classification_id,
            primary_intent=PrimaryIntentCategory.TECHNICAL_SUPPORT,
            confidence_score=0.1,
            urgency=IntentUrgency.NORMAL,
            complexity=IntentComplexity.SIMPLE,
            entities={},
            keywords=[],
            context_factors={},
            suggested_actions=["Request clarification", "Try rephrasing the question"],
            routing_recommendations=["fallback_handler"],
            processing_metadata={
                "error": error,
                "fallback_classification": True,
                "creator_type": creator_profile.creator_type.value
            },
            timestamp=datetime.utcnow()
        )
    
    def get_classification_metrics(self) -> Dict[str, Any]:
        """Get current classification metrics"""        return self.classification_metrics.copy()


# Maintain backward compatibility
IntentClassifier = EnterpriseIntentClassifier
