"""Semantic Intent Analysis for Creative Industry

Advanced semantic analysis for understanding deep intent meaning and context
in creative professional communications and workflow management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from transformers import pipeline, AutoTokenizer, AutoModel
import torch

from .config import IntentRecognitionConfig
from .exceptions import SemanticAnalysisError

logger = logging.getLogger(__name__)


class SemanticDimension(Enum):
    """Semantic analysis dimensions"""
    EMOTIONAL_TONE = "emotional_tone"
    TECHNICAL_COMPLEXITY = "technical_complexity"
    URGENCY_LEVEL = "urgency_level"
    CREATIVITY_ASPECT = "creativity_aspect"
    BUSINESS_CONTEXT = "business_context"
    COLLABORATION_INTENT = "collaboration_intent"
    LEARNING_INTENT = "learning_intent"
    PROBLEM_SOLVING = "problem_solving"


class IntentCluster(Enum):
    """High-level intent clusters"""
    CONTENT_CREATION = "content_creation"
    BUSINESS_OPERATIONS = "business_operations"
    TECHNICAL_SUPPORT = "technical_support"
    CREATIVE_COLLABORATION = "creative_collaboration"
    LEARNING_DEVELOPMENT = "learning_development"
    PLATFORM_MANAGEMENT = "platform_management"
    MONETIZATION_STRATEGY = "monetization_strategy"
    PROTECTION_SECURITY = "protection_security"


@dataclass
class SemanticFeatures:
    """Extracted semantic features from text"""
    
    # Embedding vectors
    sentence_embedding: np.ndarray = field(default_factory=lambda: np.array([]))
    token_embeddings: List[np.ndarray] = field(default_factory=list)
    
    # Semantic dimensions
    emotional_valence: float = 0.0  # -1 to 1
    technical_complexity: float = 0.0  # 0 to 1
    urgency_score: float = 0.0  # 0 to 1
    creativity_level: float = 0.0  # 0 to 1
    
    # Entity information
    named_entities: List[Dict[str, Any]] = field(default_factory=list)
    key_phrases: List[str] = field(default_factory=list)
    domain_terms: List[str] = field(default_factory=list)
    
    # Linguistic features
    sentence_complexity: float = 0.0
    formality_level: float = 0.0
    question_type: Optional[str] = None
    
    # Context indicators
    temporal_references: List[str] = field(default_factory=list)
    platform_mentions: List[str] = field(default_factory=list)
    action_words: List[str] = field(default_factory=list)


@dataclass
class SemanticIntentResult:
    """Result of semantic intent analysis"""
    
    # Primary intent cluster
    intent_cluster: IntentCluster
    cluster_confidence: float
    
    # Semantic similarity scores
    similarity_scores: Dict[str, float] = field(default_factory=dict)
    
    # Detailed analysis
    semantic_features: SemanticFeatures = field(default_factory=SemanticFeatures)
    intent_nuances: List[str] = field(default_factory=list)
    
    # Context understanding
    implied_context: Dict[str, Any] = field(default_factory=dict)
    missing_information: List[str] = field(default_factory=list)
    
    # Recommendations
    clarification_questions: List[str] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)
    
    # Metadata
    analysis_confidence: float = 0.0
    processing_time_ms: float = 0.0


class SemanticIntentAnalyzer:
    """
    Advanced semantic analysis system for intent understanding
    
    Provides deep semantic analysis including:
    - Sentence embedding generation
    - Semantic similarity matching
    - Intent clustering and classification
    - Context and nuance extraction
    - Multi-dimensional semantic analysis
    """
    
    def __init__(self, config: IntentRecognitionConfig):
        self.config = config
        self.sentence_transformer = None
        self.nlp_pipeline = None
        self.sentiment_analyzer = None
        self.intent_embeddings = {}
        self.domain_vocabulary = {}
        
        self._initialize_models()
        self._load_domain_knowledge()
    
    def _initialize_models(self):
        """Initialize semantic analysis models"""
        try:
            # Load sentence transformer for embeddings
            model_name = self.config.model.transformer_model_name
            self.sentence_transformer = SentenceTransformer(model_name)
            
            # Load spaCy for NLP
            spacy_model = self.config.model.spacy_model
            self.nlp_pipeline = spacy.load(spacy_model)
            
            # Load sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            logger.info("Semantic models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize semantic models: {e}")
            raise SemanticAnalysisError(f"Model initialization failed: {e}")
    
    def _load_domain_knowledge(self):
        """Load domain-specific knowledge and vocabularies"""
        try:
            # Creative industry domain vocabulary
            self.domain_vocabulary = {
                "music_production": [
                    "mixing", "mastering", "recording", "composition", "arrangement",
                    "melody", "harmony", "rhythm", "tempo", "key", "chord", "scale"
                ],
                "content_creation": [
                    "filming", "editing", "post-production", "storytelling", "narrative",
                    "visual", "aesthetic", "composition", "lighting", "color grading"
                ],
                "social_media": [
                    "engagement", "followers", "reach", "impressions", "algorithm",
                    "hashtags", "viral", "trending", "organic", "sponsored"
                ],
                "business_terms": [
                    "monetization", "revenue", "roi", "conversion", "analytics",
                    "metrics", "kpi", "growth", "scaling", "optimization"
                ],
                "technical_terms": [
                    "api", "integration", "automation", "workflow", "pipeline",
                    "backend", "frontend", "database", "cloud", "deployment"
                ]
            }
            
            # Pre-compute intent cluster embeddings
            intent_descriptions = {
                IntentCluster.CONTENT_CREATION: "Creating, editing, and producing content including music, videos, photos, and written material",
                IntentCluster.BUSINESS_OPERATIONS: "Managing business aspects including revenue, partnerships, contracts, and operations",
                IntentCluster.TECHNICAL_SUPPORT: "Getting help with technical issues, software problems, and platform integration",
                IntentCluster.CREATIVE_COLLABORATION: "Working with others on creative projects, finding collaborators, and managing partnerships",
                IntentCluster.LEARNING_DEVELOPMENT: "Learning new skills, improving techniques, and professional development",
                IntentCluster.PLATFORM_MANAGEMENT: "Managing presence on social media and content platforms",
                IntentCluster.MONETIZATION_STRATEGY: "Developing and implementing revenue generation strategies",
                IntentCluster.PROTECTION_SECURITY: "Protecting content, managing rights, and ensuring security"
            }
            
            for cluster, description in intent_descriptions.items():
                embedding = self.sentence_transformer.encode(description)
                self.intent_embeddings[cluster] = embedding
            
            logger.info("Domain knowledge loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load domain knowledge: {e}")
    
    def analyze_semantic_intent(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> SemanticIntentResult:
        """
        Perform comprehensive semantic intent analysis
        
        Args:
            text: Input text to analyze
            context: Additional context information
            user_profile: User profile for personalization
            
        Returns:
            SemanticIntentResult: Comprehensive semantic analysis
        """
        import time
        start_time = time.time()
        
        try:
            # Extract semantic features
            semantic_features = self._extract_semantic_features(text)
            
            # Determine intent cluster
            intent_cluster, cluster_confidence = self._classify_intent_cluster(
                text, semantic_features
            )
            
            # Calculate similarity scores
            similarity_scores = self._calculate_similarity_scores(
                semantic_features.sentence_embedding
            )
            
            # Extract intent nuances
            intent_nuances = self._extract_intent_nuances(text, semantic_features)
            
            # Analyze implied context
            implied_context = self._analyze_implied_context(
                text, semantic_features, context, user_profile
            )
            
            # Identify missing information
            missing_information = self._identify_missing_information(
                text, intent_cluster, semantic_features
            )
            
            # Generate clarification questions
            clarification_questions = self._generate_clarification_questions(
                intent_cluster, missing_information
            )
            
            # Suggest actions
            suggested_actions = self._suggest_actions(
                intent_cluster, semantic_features, context
            )
            
            # Calculate overall confidence
            analysis_confidence = self._calculate_analysis_confidence(
                cluster_confidence, semantic_features
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            return SemanticIntentResult(
                intent_cluster=intent_cluster,
                cluster_confidence=cluster_confidence,
                similarity_scores=similarity_scores,
                semantic_features=semantic_features,
                intent_nuances=intent_nuances,
                implied_context=implied_context,
                missing_information=missing_information,
                clarification_questions=clarification_questions,
                suggested_actions=suggested_actions,
                analysis_confidence=analysis_confidence,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Semantic intent analysis failed: {e}")
            raise SemanticAnalysisError(f"Analysis failed: {e}")
    
    def _extract_semantic_features(self, text: str) -> SemanticFeatures:
        """Extract comprehensive semantic features from text"""
        
        # Generate sentence embedding
        sentence_embedding = self.sentence_transformer.encode(text)
        
        # Process with spaCy
        doc = self.nlp_pipeline(text)
        
        # Extract named entities
        named_entities = [
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            }
            for ent in doc.ents
        ]
        
        # Extract key phrases (noun phrases)
        key_phrases = [chunk.text for chunk in doc.noun_chunks]
        
        # Identify domain terms
        domain_terms = self._identify_domain_terms(text.lower())
        
        # Calculate emotional valence
        emotional_valence = self._calculate_emotional_valence(text)
        
        # Calculate technical complexity
        technical_complexity = self._calculate_technical_complexity(text, domain_terms)
        
        # Calculate urgency score
        urgency_score = self._calculate_urgency_score(text)
        
        # Calculate creativity level
        creativity_level = self._calculate_creativity_level(text, domain_terms)
        
        # Calculate linguistic features
        sentence_complexity = self._calculate_sentence_complexity(doc)
        formality_level = self._calculate_formality_level(text)
        
        # Identify question type
        question_type = self._identify_question_type(text)
        
        # Extract temporal references
        temporal_references = self._extract_temporal_references(doc)
        
        # Extract platform mentions
        platform_mentions = self._extract_platform_mentions(text)
        
        # Extract action words
        action_words = self._extract_action_words(doc)
        
        return SemanticFeatures(
            sentence_embedding=sentence_embedding,
            emotional_valence=emotional_valence,
            technical_complexity=technical_complexity,
            urgency_score=urgency_score,
            creativity_level=creativity_level,
            named_entities=named_entities,
            key_phrases=key_phrases,
            domain_terms=domain_terms,
            sentence_complexity=sentence_complexity,
            formality_level=formality_level,
            question_type=question_type,
            temporal_references=temporal_references,
            platform_mentions=platform_mentions,
            action_words=action_words
        )
    
    def _identify_domain_terms(self, text: str) -> List[str]:
        """Identify domain-specific terms in text"""
        identified_terms = []
        
        for domain, terms in self.domain_vocabulary.items():
            for term in terms:
                if term in text:
                    identified_terms.append(term)
        
        return identified_terms
    
    def _calculate_emotional_valence(self, text: str) -> float:
        """Calculate emotional valence (-1 to 1)"""
        try:
            sentiment_results = self.sentiment_analyzer(text)
            
            # Convert to valence score
            positive_score = 0
            negative_score = 0
            
            for result in sentiment_results[0]:
                if result['label'] == 'LABEL_2':  # Positive
                    positive_score = result['score']
                elif result['label'] == 'LABEL_0':  # Negative
                    negative_score = result['score']
            
            return positive_score - negative_score
            
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return 0.0
    
    def _calculate_technical_complexity(self, text: str, domain_terms: List[str]) -> float:
        """Calculate technical complexity (0 to 1)"""
        
        # Technical indicators
        technical_indicators = [
            "api", "integration", "configuration", "setup", "technical",
            "code", "programming", "development", "implementation"
        ]
        
        technical_count = sum(1 for term in technical_indicators if term in text.lower())
        domain_technical_count = len([term for term in domain_terms if term in technical_indicators])
        
        # Calculate complexity based on technical terms and sentence length
        words = text.split()
        complexity_score = (technical_count + domain_technical_count) / max(len(words), 1)
        
        return min(1.0, complexity_score * 10)  # Scale and cap at 1.0
    
    def _calculate_urgency_score(self, text: str) -> float:
        """Calculate urgency score (0 to 1)"""
        
        urgency_indicators = [
            "urgent", "asap", "immediately", "quickly", "rush", "emergency",
            "deadline", "critical", "priority", "now", "soon"
        ]
        
        text_lower = text.lower()
        urgency_count = sum(1 for indicator in urgency_indicators if indicator in text_lower)
        
        # Check for punctuation indicators
        exclamation_count = text.count('!')
        question_count = text.count('?')
        
        urgency_score = (urgency_count * 0.3 + exclamation_count * 0.1 + question_count * 0.05)
        
        return min(1.0, urgency_score)
    
    def _calculate_creativity_level(self, text: str, domain_terms: List[str]) -> float:
        """Calculate creativity level (0 to 1)"""
        
        creative_indicators = [
            "creative", "artistic", "design", "aesthetic", "beautiful",
            "inspiring", "original", "unique", "innovative", "experimental"
        ]
        
        creative_domains = ["music_production", "content_creation"]
        creative_domain_terms = []
        
        for domain in creative_domains:
            creative_domain_terms.extend(self.domain_vocabulary.get(domain, []))
        
        text_lower = text.lower()
        creative_count = sum(1 for indicator in creative_indicators if indicator in text_lower)
        creative_domain_count = len([term for term in domain_terms if term in creative_domain_terms])
        
        creativity_score = (creative_count * 0.2 + creative_domain_count * 0.1)
        
        return min(1.0, creativity_score)
    
    def _calculate_sentence_complexity(self, doc) -> float:
        """Calculate sentence complexity"""
        
        total_tokens = len(doc)
        sentences = list(doc.sents)
        
        if not sentences:
            return 0.0
        
        avg_sentence_length = total_tokens / len(sentences)
        
        # Calculate dependency depth
        max_depth = 0
        for token in doc:
            depth = self._get_dependency_depth(token)
            max_depth = max(max_depth, depth)
        
        # Normalize complexity
        complexity = (avg_sentence_length / 20) + (max_depth / 10)
        
        return min(1.0, complexity)
    
    def _get_dependency_depth(self, token) -> int:
        """Calculate dependency tree depth for a token"""
        depth = 0
        current = token
        
        while current.head != current:
            depth += 1
            current = current.head
            if depth > 20:  # Prevent infinite loops
                break
        
        return depth
    
    def _calculate_formality_level(self, text: str) -> float:
        """Calculate formality level (0 to 1)"""
        
        formal_indicators = [
            "please", "thank you", "would", "could", "may", "might",
            "therefore", "furthermore", "however", "consequently"
        ]
        
        informal_indicators = [
            "hey", "hi", "yeah", "yep", "nope", "gonna", "wanna",
            "kinda", "sorta", "awesome", "cool", "lol"
        ]
        
        text_lower = text.lower()
        formal_count = sum(1 for indicator in formal_indicators if indicator in text_lower)
        informal_count = sum(1 for indicator in informal_indicators if indicator in text_lower)
        
        if formal_count + informal_count == 0:
            return 0.5  # Neutral
        
        formality_score = formal_count / (formal_count + informal_count)
        
        return formality_score
    
    def _identify_question_type(self, text: str) -> Optional[str]:
        """Identify type of question if text is a question"""
        
        if not text.strip().endswith('?'):
            return None
        
        text_lower = text.lower()
        
        question_types = {
            "how": "procedural",
            "what": "informational",
            "when": "temporal",
            "where": "locational",
            "why": "explanatory",
            "who": "identification",
            "which": "selection",
            "can": "capability",
            "should": "recommendation",
            "will": "prediction"
        }
        
        for keyword, q_type in question_types.items():
            if text_lower.startswith(keyword):
                return q_type
        
        return "general"
    
    def _extract_temporal_references(self, doc) -> List[str]:
        """Extract temporal references from text"""
        
        temporal_entities = []
        
        for ent in doc.ents:
            if ent.label_ in ["DATE", "TIME", "EVENT"]:
                temporal_entities.append(ent.text)
        
        # Additional temporal keywords
        temporal_keywords = [
            "today", "tomorrow", "yesterday", "now", "soon", "later",
            "morning", "afternoon", "evening", "night", "weekend"
        ]
        
        text_lower = doc.text.lower()
        for keyword in temporal_keywords:
            if keyword in text_lower:
                temporal_entities.append(keyword)
        
        return list(set(temporal_entities))
    
    def _extract_platform_mentions(self, text: str) -> List[str]:
        """Extract platform mentions from text"""
        
        platforms = [
            "spotify", "instagram", "youtube", "tiktok", "twitter",
            "facebook", "soundcloud", "bandcamp", "twitch", "patreon"
        ]
        
        text_lower = text.lower()
        mentioned_platforms = []
        
        for platform in platforms:
            if platform in text_lower:
                mentioned_platforms.append(platform)
        
        return mentioned_platforms
    
    def _extract_action_words(self, doc) -> List[str]:
        """Extract action words (verbs) from text"""
        
        action_words = []
        
        for token in doc:
            if token.pos_ == "VERB" and not token.is_stop:
                action_words.append(token.lemma_)
        
        return action_words
    
    def _classify_intent_cluster(
        self, 
        text: str, 
        features: SemanticFeatures
    ) -> Tuple[IntentCluster, float]:
        """Classify intent into high-level clusters"""
        
        # Calculate similarity with each intent cluster
        similarities = {}
        
        for cluster, cluster_embedding in self.intent_embeddings.items():
            similarity = cosine_similarity(
                features.sentence_embedding.reshape(1, -1),
                cluster_embedding.reshape(1, -1)
            )[0][0]
            similarities[cluster] = similarity
        
        # Find best matching cluster
        best_cluster = max(similarities, key=similarities.get)
        confidence = similarities[best_cluster]
        
        # Apply feature-based adjustments
        if features.technical_complexity > 0.7:
            if best_cluster != IntentCluster.TECHNICAL_SUPPORT:
                confidence *= 0.9  # Reduce confidence if high technical complexity
        
        if features.creativity_level > 0.7:
            if best_cluster == IntentCluster.CONTENT_CREATION:
                confidence *= 1.1  # Boost confidence for creative content
        
        if len(features.platform_mentions) > 0:
            if best_cluster == IntentCluster.PLATFORM_MANAGEMENT:
                confidence *= 1.1  # Boost confidence for platform management
        
        return best_cluster, min(1.0, confidence)
    
    def _calculate_similarity_scores(self, embedding: np.ndarray) -> Dict[str, float]:
        """Calculate similarity scores with various intent categories"""
        
        similarity_scores = {}
        
        for cluster, cluster_embedding in self.intent_embeddings.items():
            similarity = cosine_similarity(
                embedding.reshape(1, -1),
                cluster_embedding.reshape(1, -1)
            )[0][0]
            similarity_scores[cluster.value] = float(similarity)
        
        return similarity_scores
    
    def _extract_intent_nuances(self, text: str, features: SemanticFeatures) -> List[str]:
        """Extract nuanced aspects of the intent"""
        
        nuances = []
        
        # Emotional nuances
        if features.emotional_valence > 0.5:
            nuances.append("positive_sentiment")
        elif features.emotional_valence < -0.5:
            nuances.append("negative_sentiment")
        
        # Complexity nuances
        if features.technical_complexity > 0.7:
            nuances.append("high_technical_complexity")
        elif features.technical_complexity < 0.3:
            nuances.append("low_technical_complexity")
        
        # Urgency nuances
        if features.urgency_score > 0.7:
            nuances.append("high_urgency")
        elif features.urgency_score < 0.3:
            nuances.append("low_urgency")
        
        # Creativity nuances
        if features.creativity_level > 0.7:
            nuances.append("high_creativity")
        
        # Question nuances
        if features.question_type:
            nuances.append(f"question_type_{features.question_type}")
        
        # Formality nuances
        if features.formality_level > 0.7:
            nuances.append("formal_tone")
        elif features.formality_level < 0.3:
            nuances.append("informal_tone")
        
        return nuances
    
    def _analyze_implied_context(
        self,
        text: str,
        features: SemanticFeatures,
        context: Optional[Dict[str, Any]],
        user_profile: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze implied context from the text and features"""
        
        implied_context = {}
        
        # Implied timeline
        if features.urgency_score > 0.7:
            implied_context["timeline"] = "immediate"
        elif features.urgency_score > 0.4:
            implied_context["timeline"] = "soon"
        else:
            implied_context["timeline"] = "flexible"
        
        # Implied skill level
        if features.technical_complexity > 0.7:
            implied_context["skill_level"] = "advanced"
        elif features.technical_complexity < 0.3:
            implied_context["skill_level"] = "beginner"
        else:
            implied_context["skill_level"] = "intermediate"
        
        # Implied collaboration need
        collaboration_indicators = ["we", "us", "team", "together", "collaborate"]
        if any(indicator in text.lower() for indicator in collaboration_indicators):
            implied_context["collaboration_needed"] = True
        
        # Implied platform focus
        if features.platform_mentions:
            implied_context["target_platforms"] = features.platform_mentions
        
        return implied_context
    
    def _identify_missing_information(
        self,
        text: str,
        intent_cluster: IntentCluster,
        features: SemanticFeatures
    ) -> List[str]:
        """Identify what information might be missing for complete understanding"""
        
        missing_info = []
        
        # Cluster-specific missing information
        if intent_cluster == IntentCluster.CONTENT_CREATION:
            if not features.platform_mentions:
                missing_info.append("target_platform")
            if "upload" in text.lower() and len(features.named_entities) == 0:
                missing_info.append("content_type")
        
        elif intent_cluster == IntentCluster.MONETIZATION_STRATEGY:
            if "revenue" in text.lower() and not features.temporal_references:
                missing_info.append("timeline")
            if not any(term in text.lower() for term in ["followers", "audience", "subscribers"]):
                missing_info.append("audience_size")
        
        elif intent_cluster == IntentCluster.TECHNICAL_SUPPORT:
            if "error" in text.lower() and len(features.named_entities) == 0:
                missing_info.append("error_details")
            if "not working" in text.lower() and not features.platform_mentions:
                missing_info.append("affected_platform")
        
        # General missing information
        if features.urgency_score > 0.7 and not features.temporal_references:
            missing_info.append("specific_deadline")
        
        if features.question_type and "how" in text.lower() and features.technical_complexity < 0.3:
            missing_info.append("current_experience_level")
        
        return missing_info
    
    def _generate_clarification_questions(
        self,
        intent_cluster: IntentCluster,
        missing_information: List[str]
    ) -> List[str]:
        """Generate clarification questions based on missing information"""
        
        questions = []
        
        # Map missing information to questions
        question_map = {
            "target_platform": "Which platform would you like to focus on?",
            "content_type": "What type of content are you working with?",
            "timeline": "What's your target timeline for this?",
            "audience_size": "How large is your current audience?",
            "error_details": "Can you provide more details about the error?",
            "affected_platform": "Which platform is experiencing the issue?",
            "specific_deadline": "Do you have a specific deadline?",
            "current_experience_level": "What's your current experience level with this?"
        }
        
        for missing_item in missing_information:
            if missing_item in question_map:
                questions.append(question_map[missing_item])
        
        # Cluster-specific questions
        if intent_cluster == IntentCluster.CONTENT_CREATION and not questions:
            questions.append("What type of content would you like to create?")
        elif intent_cluster == IntentCluster.BUSINESS_OPERATIONS and not questions:
            questions.append("What specific business aspect would you like help with?")
        
        return questions
    
    def _suggest_actions(
        self,
        intent_cluster: IntentCluster,
        features: SemanticFeatures,
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Suggest relevant actions based on intent analysis"""
        
        actions = []
        
        # Cluster-specific actions
        cluster_actions = {
            IntentCluster.CONTENT_CREATION: [
                "Set up content creation workflow",
                "Choose appropriate platform",
                "Plan content calendar"
            ],
            IntentCluster.MONETIZATION_STRATEGY: [
                "Analyze current revenue streams",
                "Explore monetization options",
                "Set revenue targets"
            ],
            IntentCluster.PLATFORM_MANAGEMENT: [
                "Review platform analytics",
                "Optimize posting schedule",
                "Improve content strategy"
            ],
            IntentCluster.TECHNICAL_SUPPORT: [
                "Check system requirements",
                "Review error logs",
                "Contact technical support"
            ]
        }
        
        actions.extend(cluster_actions.get(intent_cluster, []))
        
        # Feature-based actions
        if features.urgency_score > 0.7:
            actions.insert(0, "Prioritize immediate action")
        
        if features.creativity_level > 0.7:
            actions.append("Explore creative tools and resources")
        
        if len(features.platform_mentions) > 1:
            actions.append("Consider cross-platform strategy")
        
        return actions[:5]  # Limit to top 5 actions
    
    def _calculate_analysis_confidence(
        self,
        cluster_confidence: float,
        features: SemanticFeatures
    ) -> float:
        """Calculate overall confidence in the analysis"""
        
        # Base confidence from cluster classification
        confidence = cluster_confidence
        
        # Adjust based on text quality indicators
        if len(features.key_phrases) > 3:
            confidence += 0.1  # More key phrases = better understanding
        
        if len(features.domain_terms) > 2:
            confidence += 0.1  # Domain expertise evident
        
        if features.sentence_complexity > 0.8:
            confidence -= 0.1  # Very complex sentences may be harder to parse
        
        if len(features.named_entities) > 0:
            confidence += 0.05  # Named entities provide context
        
        return min(1.0, max(0.0, confidence))
    
    def get_intent_embedding(self, text: str) -> np.ndarray:
        """Get embedding vector for given text"""
        return self.sentence_transformer.encode(text)
    
    def compare_intents(self, text1: str, text2: str) -> float:
        """Compare semantic similarity between two texts"""
        embedding1 = self.get_intent_embedding(text1)
        embedding2 = self.get_intent_embedding(text2)
        
        similarity = cosine_similarity(
            embedding1.reshape(1, -1),
            embedding2.reshape(1, -1)
        )[0][0]
        
        return float(similarity)
