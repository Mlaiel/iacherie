"""
Voice Search Optimizer for IA Chérie Platform
==========================================

Advanced voice search optimization system leveraging NLP and conversational AI
for creator economy content optimization across voice assistants and smart devices.

Features:
- Conversational keyword analysis and optimization
- Featured snippet optimization for voice results
- Local voice search optimization
- Question-based content optimization
- Voice intent classification and matching
- Multi-language voice search support

Author: Fahed Mlaiel (mlaiel@live.de)
Lead Dev IA + Audio Engineer + ML Engineer expertise applied
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import re
import openai
# from transformers import AutoTokenizer, AutoModel, pipeline
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import speech_recognition as sr
from gtts import gTTS
import io

logger = logging.getLogger(__name__)

class VoiceSearchDevice(Enum):
    """Voice search device types."""
    GOOGLE_ASSISTANT = "google_assistant"
    AMAZON_ALEXA = "amazon_alexa"
    APPLE_SIRI = "apple_siri"
    MICROSOFT_CORTANA = "microsoft_cortana"
    SMART_SPEAKERS = "smart_speakers"
    MOBILE_VOICE = "mobile_voice"

class VoiceQueryType(Enum):
    """Types of voice queries."""
    QUESTION = "question"
    COMMAND = "command"
    LOCAL_SEARCH = "local_search"
    INFORMATION_REQUEST = "information_request"
    NAVIGATION = "navigation"
    TRANSACTION = "transaction"

class ConversationContext(Enum):
    """Conversational context types."""
    CASUAL = "casual"
    FORMAL = "formal"
    TECHNICAL = "technical"
    COLLOQUIAL = "colloquial"
    EDUCATIONAL = "educational"

class SnippetType(Enum):
    """Featured snippet types."""
    PARAGRAPH = "paragraph"
    LIST = "list"
    TABLE = "table"
    DEFINITION = "definition"
    HOWTO = "howto"
    FAQ = "faq"

@dataclass
class VoiceQuery:
    """Voice query representation."""
    query_text: str
    query_type: VoiceQueryType
    device_type: VoiceSearchDevice
    conversation_context: ConversationContext
    confidence: float
    intent: str
    entities: List[str]
    location_context: Optional[str]

@dataclass
class ConversationalKeywords:
    """Conversational keyword analysis result."""
    original_keywords: List[str]
    conversational_variants: List[str]
    question_variants: List[str]
    natural_language_phrases: List[str]
    voice_search_difficulty: float
    optimization_opportunities: List[str]

@dataclass
class VoiceOptimization:
    """Voice search optimization result."""
    original_content: str
    optimized_content: str
    voice_readiness_score: float
    conversational_keywords: ConversationalKeywords
    featured_snippet_candidates: List[str]
    voice_search_improvements: List[str]
    natural_language_score: float
    question_answering_score: float

@dataclass
class SnippetCandidate:
    """Featured snippet candidate."""
    snippet_type: SnippetType
    content: str
    question: str
    answer: str
    confidence_score: float
    optimization_suggestions: List[str]
    markup_requirements: List[str]

@dataclass
class SnippetOptimization:
    """Featured snippet optimization result."""
    target_queries: List[str]
    snippet_candidates: List[SnippetCandidate]
    optimization_priority: int
    implementation_difficulty: str
    expected_voice_traffic: int
    structured_data_requirements: List[str]

@dataclass
class LocationData:
    """Location data for local voice search."""
    city: str
    state: str
    country: str
    latitude: float
    longitude: float
    radius: float
    local_keywords: List[str]

@dataclass
class LocalVoiceOptimization:
    """Local voice search optimization."""
    location: LocationData
    local_intent_keywords: List[str]
    near_me_variations: List[str]
    local_business_opportunities: List[str]
    gmb_optimization_suggestions: List[str]
    local_content_recommendations: List[str]
    voice_search_local_score: float

@dataclass
class QuestionPattern:
    """Question pattern for optimization."""
    question_type: str
    pattern: str
    example_questions: List[str]
    answer_structure: str
    optimization_priority: int

@dataclass
class QuestionOptimization:
    """Question-based content optimization."""
    identified_questions: List[str]
    question_patterns: List[QuestionPattern]
    answer_optimization: Dict[str, str]
    faq_structure_suggestions: List[str]
    conversational_flow_improvements: List[str]
    voice_answer_readiness: float

class VoiceSearchOptimizer:
    """Advanced voice search optimization engine."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize voice search optimizer.
        
        Args:
            config: Configuration dictionary with model settings and API keys
        """
        self.config = config or {}
        self.model_name = self.config.get('model_name', 'sentence-transformers/all-MiniLM-L6-v2')
        self.spacy_model = self.config.get('spacy_model', 'en_core_web_sm')
        self.openai_api_key = self.config.get('openai_api_key')
        
        # Voice search optimization settings
        self.max_snippet_length = self.config.get('max_snippet_length', 300)
        self.question_confidence_threshold = self.config.get('question_threshold', 0.7)
        self.local_search_radius = self.config.get('local_radius', 50)  # km
        
        # Initialize models
        self.tokenizer = None
        self.model = None
        self.nlp = None
        self.openai_client = None
        self.speech_recognizer = None
        
        # Voice search patterns
        self.question_patterns = [
            r'^(what|where|when|why|how|who|which|whose)\s',
            r'\b(is|are|was|were|can|could|should|would|will|do|does|did)\b',
            r'\?$'
        ]
        
        self.conversational_indicators = [
            'tell me', 'show me', 'find me', 'help me', 'i need', 'looking for',
            'search for', 'where can i', 'how do i', 'what is the best'
        ]
        
        # Caching for performance
        self._voice_optimization_cache: Dict[str, VoiceOptimization] = {}
        self._conversational_cache: Dict[str, ConversationalKeywords] = {}
        self._snippet_cache: Dict[str, List[SnippetCandidate]] = {}
        
        logger.info("VoiceSearchOptimizer initialized")

    async def initialize_models(self) -> None:
        """Initialize NLP and voice processing models."""
        try:
            # Initialize transformer model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            
            # Initialize spaCy
            self.nlp = spacy.load(self.spacy_model)
            
            # Initialize OpenAI
            if self.openai_api_key:
                openai.api_key = self.openai_api_key
                self.openai_client = openai
            
            # Initialize speech recognition
            self.speech_recognizer = sr.Recognizer()
            
            # Download NLTK data if needed
            try:
                nltk.data.find('tokenizers/punkt')
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
            
            logger.info("Voice search models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize voice search models: {e}")
            raise

    async def voice_query_optimization(self, content: str, 
                                     target_queries: Optional[List[str]] = None) -> VoiceOptimization:
        """Optimize content for voice search queries.
        
        Args:
            content: Content to optimize for voice search
            target_queries: Optional list of target voice queries
            
        Returns:
            VoiceOptimization with optimized content and analysis
        """
        if not self.model:
            await self.initialize_models()
            
        cache_key = f"{hash(content)}_{hash(str(target_queries))}"
        if cache_key in self._voice_optimization_cache:
            return self._voice_optimization_cache[cache_key]
            
        try:
            # Analyze current voice readiness
            voice_readiness_score = await self._assess_voice_readiness(content)
            
            # Extract and optimize conversational keywords
            conversational_keywords = await self._analyze_conversational_keywords(content, target_queries)
            
            # Identify featured snippet opportunities
            snippet_candidates = await self._identify_snippet_opportunities(content)
            
            # Optimize content structure for voice search
            optimized_content = await self._optimize_content_for_voice(content, conversational_keywords)
            
            # Calculate natural language score
            natural_language_score = await self._calculate_natural_language_score(optimized_content)
            
            # Calculate question-answering score
            qa_score = await self._calculate_qa_score(optimized_content)
            
            # Generate voice search improvements
            improvements = await self._generate_voice_improvements(
                content, optimized_content, conversational_keywords, snippet_candidates
            )
            
            result = VoiceOptimization(
                original_content=content,
                optimized_content=optimized_content,
                voice_readiness_score=voice_readiness_score,
                conversational_keywords=conversational_keywords,
                featured_snippet_candidates=[candidate.content for candidate in snippet_candidates],
                voice_search_improvements=improvements,
                natural_language_score=natural_language_score,
                question_answering_score=qa_score
            )
            
            # Cache result
            self._voice_optimization_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Voice query optimization failed: {e}")
            raise

    async def conversational_keyword_analysis(self, queries: List[str]) -> ConversationalKeywords:
        """Analyze and generate conversational keyword variations.
        
        Args:
            queries: List of search queries to analyze
            
        Returns:
            ConversationalKeywords with conversational variations
        """
        cache_key = hash(str(queries))
        if cache_key in self._conversational_cache:
            return self._conversational_cache[cache_key]
            
        try:
            # Extract base keywords from queries
            original_keywords = await self._extract_keywords_from_queries(queries)
            
            # Generate conversational variants
            conversational_variants = await self._generate_conversational_variants(original_keywords)
            
            # Generate question variants
            question_variants = await self._generate_question_variants(original_keywords)
            
            # Generate natural language phrases
            natural_phrases = await self._generate_natural_language_phrases(original_keywords)
            
            # Calculate voice search difficulty
            difficulty = await self._calculate_voice_search_difficulty(original_keywords)
            
            # Identify optimization opportunities
            opportunities = await self._identify_conversational_opportunities(
                original_keywords, conversational_variants, question_variants
            )
            
            result = ConversationalKeywords(
                original_keywords=original_keywords,
                conversational_variants=conversational_variants,
                question_variants=question_variants,
                natural_language_phrases=natural_phrases,
                voice_search_difficulty=difficulty,
                optimization_opportunities=opportunities
            )
            
            # Cache result
            self._conversational_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Conversational keyword analysis failed: {e}")
            raise

    async def featured_snippet_optimization(self, content: str, 
                                          target_questions: Optional[List[str]] = None) -> SnippetOptimization:
        """Optimize content for featured snippets in voice search.
        
        Args:
            content: Content to optimize for snippets
            target_questions: Optional target questions for snippets
            
        Returns:
            SnippetOptimization with optimization strategy
        """
        cache_key = f"{hash(content)}_{hash(str(target_questions))}"
        if cache_key in self._snippet_cache:
            cached_candidates = self._snippet_cache[cache_key]
        else:
            cached_candidates = await self._identify_snippet_opportunities(content)
            self._snippet_cache[cache_key] = cached_candidates
            
        try:
            # Identify or use provided target questions
            if not target_questions:
                target_questions = await self._extract_implicit_questions(content)
            
            # Analyze snippet candidates
            snippet_candidates = cached_candidates
            
            # Calculate optimization priority
            priority = await self._calculate_snippet_priority(snippet_candidates, target_questions)
            
            # Assess implementation difficulty
            difficulty = await self._assess_snippet_difficulty(snippet_candidates)
            
            # Estimate voice traffic potential
            voice_traffic = await self._estimate_voice_traffic(target_questions)
            
            # Identify structured data requirements
            structured_data = await self._identify_structured_data_needs(snippet_candidates)
            
            return SnippetOptimization(
                target_queries=target_questions,
                snippet_candidates=snippet_candidates,
                optimization_priority=priority,
                implementation_difficulty=difficulty,
                expected_voice_traffic=voice_traffic,
                structured_data_requirements=structured_data
            )
            
        except Exception as e:
            logger.error(f"Featured snippet optimization failed: {e}")
            raise

    async def local_voice_search_optimization(self, location_data: LocationData, 
                                            business_type: Optional[str] = None) -> LocalVoiceOptimization:
        """Optimize for local voice search queries.
        
        Args:
            location_data: Location information for optimization
            business_type: Optional business type for targeted optimization
            
        Returns:
            LocalVoiceOptimization with local search strategy
        """
        try:
            # Generate local intent keywords
            local_keywords = await self._generate_local_intent_keywords(location_data, business_type)
            
            # Generate "near me" variations
            near_me_variations = await self._generate_near_me_variations(location_data, business_type)
            
            # Identify local business opportunities
            business_opportunities = await self._identify_local_business_opportunities(
                location_data, business_type
            )
            
            # Generate GMB optimization suggestions
            gmb_suggestions = await self._generate_gmb_optimization_suggestions(location_data)
            
            # Generate local content recommendations
            content_recommendations = await self._generate_local_content_recommendations(
                location_data, business_type
            )
            
            # Calculate local voice search score
            local_score = await self._calculate_local_voice_score(
                location_data, local_keywords, near_me_variations
            )
            
            return LocalVoiceOptimization(
                location=location_data,
                local_intent_keywords=local_keywords,
                near_me_variations=near_me_variations,
                local_business_opportunities=business_opportunities,
                gmb_optimization_suggestions=gmb_suggestions,
                local_content_recommendations=content_recommendations,
                voice_search_local_score=local_score
            )
            
        except Exception as e:
            logger.error(f"Local voice search optimization failed: {e}")
            raise

    async def question_based_content_optimization(self, content: str) -> QuestionOptimization:
        """Optimize content for question-based voice searches.
        
        Args:
            content: Content to optimize for questions
            
        Returns:
            QuestionOptimization with question-focused improvements
        """
        try:
            # Identify questions in and about the content
            identified_questions = await self._identify_content_questions(content)
            
            # Analyze question patterns
            question_patterns = await self._analyze_question_patterns(identified_questions)
            
            # Optimize answers for voice delivery
            answer_optimization = await self._optimize_answers_for_voice(content, identified_questions)
            
            # Generate FAQ structure suggestions
            faq_suggestions = await self._generate_faq_structure(identified_questions, answer_optimization)
            
            # Improve conversational flow
            flow_improvements = await self._improve_conversational_flow(content, identified_questions)
            
            # Calculate voice answer readiness
            voice_readiness = await self._calculate_voice_answer_readiness(
                identified_questions, answer_optimization
            )
            
            return QuestionOptimization(
                identified_questions=identified_questions,
                question_patterns=question_patterns,
                answer_optimization=answer_optimization,
                faq_structure_suggestions=faq_suggestions,
                conversational_flow_improvements=flow_improvements,
                voice_answer_readiness=voice_readiness
            )
            
        except Exception as e:
            logger.error(f"Question-based optimization failed: {e}")
            raise

    # Private helper methods

    async def _assess_voice_readiness(self, content: str) -> float:
        """Assess content readiness for voice search."""
        try:
            score_factors = []
            
            # Conversational language score
            conversational_score = await self._calculate_conversational_language_score(content)
            score_factors.append(conversational_score * 0.3)
            
            # Question-answer structure score
            qa_structure_score = await self._calculate_qa_structure_score(content)
            score_factors.append(qa_structure_score * 0.25)
            
            # Natural language flow score
            natural_flow_score = await self._calculate_natural_flow_score(content)
            score_factors.append(natural_flow_score * 0.2)
            
            # Featured snippet readiness
            snippet_readiness = await self._calculate_snippet_readiness(content)
            score_factors.append(snippet_readiness * 0.15)
            
            # Local optimization score (if applicable)
            local_score = await self._calculate_local_optimization_score(content)
            score_factors.append(local_score * 0.1)
            
            return sum(score_factors)
            
        except Exception as e:
            logger.error(f"Voice readiness assessment failed: {e}")
            return 0.5

    async def _calculate_conversational_language_score(self, content: str) -> float:
        """Calculate how conversational the language is."""
        try:
            # Count conversational indicators
            conversational_count = 0
            for indicator in self.conversational_indicators:
                conversational_count += content.lower().count(indicator)
            
            # Normalize by content length
            word_count = len(content.split())
            conversational_ratio = conversational_count / max(word_count / 100, 1)
            
            # Check for personal pronouns
            personal_pronouns = ['you', 'your', 'we', 'our', 'i', 'my']
            pronoun_count = sum(content.lower().count(pronoun) for pronoun in personal_pronouns)
            pronoun_ratio = pronoun_count / max(word_count / 50, 1)
            
            # Check for contractions
            contractions = ["don't", "won't", "can't", "isn't", "aren't", "doesn't", "didn't"]
            contraction_count = sum(content.lower().count(contraction) for contraction in contractions)
            contraction_ratio = contraction_count / max(word_count / 100, 1)
            
            # Combine scores
            score = min((conversational_ratio + pronoun_ratio + contraction_ratio) / 3, 1.0)
            
            return score
            
        except Exception:
            return 0.5

    async def _calculate_qa_structure_score(self, content: str) -> float:
        """Calculate question-answer structure score."""
        try:
            # Count questions in content
            question_count = 0
            for pattern in self.question_patterns:
                question_count += len(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
            
            # Check for answer structures
            answer_indicators = ['answer:', 'solution:', 'here\'s how', 'steps:', 'method:']
            answer_count = sum(content.lower().count(indicator) for indicator in answer_indicators)
            
            # Check for list structures
            list_indicators = [r'\d+\.', r'•', r'-\s', r'\*\s']
            list_count = sum(len(re.findall(pattern, content)) for pattern in list_indicators)
            
            # Normalize scores
            word_count = len(content.split())
            qa_score = min((question_count + answer_count + list_count / 5) / max(word_count / 200, 1), 1.0)
            
            return qa_score
            
        except Exception:
            return 0.5

    async def _calculate_natural_flow_score(self, content: str) -> float:
        """Calculate natural language flow score."""
        try:
            if not self.nlp:
                await self.initialize_models()
            
            # Analyze sentence structure
            sentences = sent_tokenize(content)
            if not sentences:
                return 0.0
            
            # Calculate average sentence length
            avg_sentence_length = np.mean([len(sentence.split()) for sentence in sentences])
            
            # Optimal sentence length for voice (8-20 words)
            length_score = 1.0 if 8 <= avg_sentence_length <= 20 else max(0, 1 - abs(avg_sentence_length - 14) / 14)
            
            # Calculate readability (simplified)
            complex_words = 0
            total_words = 0
            
            for sentence in sentences[:10]:  # Limit for performance
                words = word_tokenize(sentence)
                total_words += len(words)
                complex_words += len([word for word in words if len(word) > 6])
            
            complexity_ratio = complex_words / max(total_words, 1)
            readability_score = max(0, 1 - complexity_ratio)
            
            return (length_score + readability_score) / 2
            
        except Exception:
            return 0.5

    async def _calculate_snippet_readiness(self, content: str) -> float:
        """Calculate featured snippet readiness."""
        try:
            # Check for definition structures
            definition_indicators = ['is a', 'is an', 'refers to', 'means', 'defined as']
            definition_score = min(sum(content.lower().count(indicator) for indicator in definition_indicators) / 3, 1.0)
            
            # Check for how-to structures
            howto_indicators = ['step 1', 'first,', 'then,', 'next,', 'finally,']
            howto_score = min(sum(content.lower().count(indicator) for indicator in howto_indicators) / 3, 1.0)
            
            # Check for list structures
            list_patterns = [r'\d+\.', r'•', r'-\s']
            list_score = min(sum(len(re.findall(pattern, content)) for pattern in list_patterns) / 10, 1.0)
            
            return (definition_score + howto_score + list_score) / 3
            
        except Exception:
            return 0.5

    async def _calculate_local_optimization_score(self, content: str) -> float:
        """Calculate local optimization score."""
        local_indicators = ['near', 'local', 'nearby', 'location', 'address', 'city', 'area']
        local_count = sum(content.lower().count(indicator) for indicator in local_indicators)
        
        word_count = len(content.split())
        local_ratio = local_count / max(word_count / 100, 1)
        
        return min(local_ratio, 1.0)

    async def _analyze_conversational_keywords(self, content: str, 
                                             target_queries: Optional[List[str]]) -> ConversationalKeywords:
        """Analyze conversational keywords in content."""
        try:
            # Extract keywords from content
            content_keywords = await self._extract_keywords_from_content_text(content)
            
            # Include target queries if provided
            if target_queries:
                query_keywords = await self._extract_keywords_from_queries(target_queries)
                original_keywords = list(set(content_keywords + query_keywords))
            else:
                original_keywords = content_keywords
            
            # Generate conversational variants
            conversational_variants = await self._generate_conversational_variants(original_keywords)
            
            # Generate question variants
            question_variants = await self._generate_question_variants(original_keywords)
            
            # Generate natural language phrases
            natural_phrases = await self._generate_natural_language_phrases(original_keywords)
            
            # Calculate difficulty
            difficulty = await self._calculate_voice_search_difficulty(original_keywords)
            
            # Identify opportunities
            opportunities = await self._identify_conversational_opportunities(
                original_keywords, conversational_variants, question_variants
            )
            
            return ConversationalKeywords(
                original_keywords=original_keywords,
                conversational_variants=conversational_variants,
                question_variants=question_variants,
                natural_language_phrases=natural_phrases,
                voice_search_difficulty=difficulty,
                optimization_opportunities=opportunities
            )
            
        except Exception as e:
            logger.error(f"Conversational keyword analysis failed: {e}")
            return ConversationalKeywords([], [], [], [], 0.5, [])

    async def _extract_keywords_from_content_text(self, content: str) -> List[str]:
        """Extract keywords from content text."""
        try:
            # Use TF-IDF for keyword extraction
            vectorizer = TfidfVectorizer(
                max_features=30,
                stop_words='english',
                ngram_range=(1, 3),
                min_df=1
            )
            
            tfidf_matrix = vectorizer.fit_transform([content])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return [keyword for keyword, score in keyword_scores[:20] if score > 0.1]
            
        except Exception:
            # Fallback to simple extraction
            if self.nlp:
                doc = self.nlp(content[:2000])  # Limit for performance
                return [token.text for token in doc if token.pos_ in ['NOUN', 'ADJ'] and not token.is_stop][:20]
            
            return []

    async def _extract_keywords_from_queries(self, queries: List[str]) -> List[str]:
        """Extract keywords from search queries."""
        all_keywords = []
        
        for query in queries:
            # Remove question words
            cleaned_query = re.sub(r'\b(what|where|when|why|how|who|which|whose|is|are|was|were|can|could|should|would|will|do|does|did)\b', '', query, flags=re.IGNORECASE)
            
            # Extract meaningful words
            words = word_tokenize(cleaned_query.lower())
            stop_words = set(stopwords.words('english'))
            keywords = [word for word in words if word.isalpha() and word not in stop_words and len(word) > 2]
            
            all_keywords.extend(keywords)
        
        return list(set(all_keywords))

    async def _generate_conversational_variants(self, keywords: List[str]) -> List[str]:
        """Generate conversational variants of keywords."""
        variants = []
        
        for keyword in keywords:
            # Add conversational prefixes
            conversational_prefixes = [
                f"tell me about {keyword}",
                f"what is {keyword}",
                f"how does {keyword} work",
                f"find me {keyword}",
                f"show me {keyword}",
                f"I need help with {keyword}",
                f"looking for {keyword}",
                f"where can I find {keyword}"
            ]
            
            variants.extend(conversational_prefixes)
        
        return variants[:50]  # Limit variants

    async def _generate_question_variants(self, keywords: List[str]) -> List[str]:
        """Generate question variants of keywords."""
        questions = []
        
        question_templates = [
            "What is {}?",
            "How does {} work?",
            "Why is {} important?",
            "When should I use {}?",
            "Where can I find {}?",
            "Who uses {}?",
            "Which {} is best?",
            "How to {}?",
            "What are the benefits of {}?",
            "How much does {} cost?"
        ]
        
        for keyword in keywords:
            for template in question_templates:
                questions.append(template.format(keyword))
        
        return questions[:40]  # Limit questions

    async def _generate_natural_language_phrases(self, keywords: List[str]) -> List[str]:
        """Generate natural language phrases."""
        phrases = []
        
        for keyword in keywords:
            natural_phrases = [
                f"everything about {keyword}",
                f"guide to {keyword}",
                f"tips for {keyword}",
                f"how to use {keyword}",
                f"benefits of {keyword}",
                f"problems with {keyword}",
                f"alternatives to {keyword}",
                f"best practices for {keyword}"
            ]
            
            phrases.extend(natural_phrases)
        
        return phrases[:30]  # Limit phrases

    async def _calculate_voice_search_difficulty(self, keywords: List[str]) -> float:
        """Calculate voice search difficulty for keywords."""
        try:
            difficulty_factors = []
            
            for keyword in keywords:
                # Word count factor (longer = easier for voice)
                word_count = len(keyword.split())
                length_factor = min(word_count / 4, 1.0)
                
                # Pronunciation complexity (simplified)
                complexity_factor = max(0, 1 - len(keyword) / 20)
                
                # Common word factor
                common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
                common_factor = sum(1 for word in keyword.split() if word.lower() in common_words) / max(len(keyword.split()), 1)
                
                keyword_difficulty = (length_factor + complexity_factor + common_factor) / 3
                difficulty_factors.append(1 - keyword_difficulty)  # Invert so higher = more difficult
            
            return np.mean(difficulty_factors) if difficulty_factors else 0.5
            
        except Exception:
            return 0.5

    async def _identify_conversational_opportunities(self, original: List[str], 
                                                   conversational: List[str], 
                                                   questions: List[str]) -> List[str]:
        """Identify conversational optimization opportunities."""
        opportunities = []
        
        if len(original) > len(conversational) / 3:
            opportunities.append("Expand conversational keyword variants")
        
        if len(questions) < len(original) * 2:
            opportunities.append("Create more question-based content")
        
        # Check for missing voice search patterns
        voice_patterns = ['how to', 'what is', 'where can', 'tell me']
        missing_patterns = []
        for pattern in voice_patterns:
            if not any(pattern in q.lower() for q in questions):
                missing_patterns.append(pattern)
        
        if missing_patterns:
            opportunities.append(f"Add content for patterns: {', '.join(missing_patterns)}")
        
        return opportunities

    async def _identify_snippet_opportunities(self, content: str) -> List[SnippetCandidate]:
        """Identify featured snippet opportunities in content."""
        candidates = []
        
        try:
            # Look for definition opportunities
            definition_candidates = await self._find_definition_candidates(content)
            candidates.extend(definition_candidates)
            
            # Look for list opportunities
            list_candidates = await self._find_list_candidates(content)
            candidates.extend(list_candidates)
            
            # Look for how-to opportunities
            howto_candidates = await self._find_howto_candidates(content)
            candidates.extend(howto_candidates)
            
            # Look for FAQ opportunities
            faq_candidates = await self._find_faq_candidates(content)
            candidates.extend(faq_candidates)
            
            return candidates[:10]  # Limit candidates
            
        except Exception as e:
            logger.error(f"Snippet opportunity identification failed: {e}")
            return []

    async def _find_definition_candidates(self, content: str) -> List[SnippetCandidate]:
        """Find definition snippet candidates."""
        candidates = []
        
        # Look for definition patterns
        definition_patterns = [
            r'(\w+(?:\s+\w+)*)\s+is\s+(?:a|an)\s+([^.]+\.)',
            r'(\w+(?:\s+\w+)*)\s+refers\s+to\s+([^.]+\.)',
            r'(\w+(?:\s+\w+)*)\s+means\s+([^.]+\.)'
        ]
        
        for pattern in definition_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                term = match.group(1).strip()
                definition = match.group(2).strip()
                
                if len(definition) <= self.max_snippet_length:
                    candidate = SnippetCandidate(
                        snippet_type=SnippetType.DEFINITION,
                        content=f"{term} {definition}",
                        question=f"What is {term}?",
                        answer=definition,
                        confidence_score=0.8,
                        optimization_suggestions=[
                            "Ensure definition is within 50 words",
                            "Add structured data markup"
                        ],
                        markup_requirements=["FAQ schema", "Definition schema"]
                    )
                    candidates.append(candidate)
        
        return candidates[:3]

    async def _find_list_candidates(self, content: str) -> List[SnippetCandidate]:
        """Find list snippet candidates."""
        candidates = []
        
        # Look for numbered lists
        numbered_list_pattern = r'(\d+\.\s+[^\n]+(?:\n|$))+'
        matches = re.finditer(numbered_list_pattern, content, re.MULTILINE)
        
        for match in matches:
            list_content = match.group(0).strip()
            if len(list_content) <= self.max_snippet_length:
                candidate = SnippetCandidate(
                    snippet_type=SnippetType.LIST,
                    content=list_content,
                    question="What are the steps?",
                    answer=list_content,
                    confidence_score=0.7,
                    optimization_suggestions=[
                        "Keep list items concise",
                        "Use proper HTML list markup"
                    ],
                    markup_requirements=["Ordered list schema"]
                )
                candidates.append(candidate)
        
        return candidates[:2]

    async def _find_howto_candidates(self, content: str) -> List[SnippetCandidate]:
        """Find how-to snippet candidates."""
        candidates = []
        
        # Look for how-to patterns
        howto_patterns = [
            r'(?:how to|steps to)\s+([^:]+):\s*\n((?:\d+\.\s+[^\n]+\n?)+)',
            r'(step\s+\d+[^\n]+\n?)+'
        ]
        
        for pattern in howto_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                howto_content = match.group(0).strip()
                if len(howto_content) <= self.max_snippet_length:
                    candidate = SnippetCandidate(
                        snippet_type=SnippetType.HOWTO,
                        content=howto_content,
                        question="How to do this?",
                        answer=howto_content,
                        confidence_score=0.75,
                        optimization_suggestions=[
                            "Use clear step numbering",
                            "Add HowTo schema markup"
                        ],
                        markup_requirements=["HowTo schema"]
                    )
                    candidates.append(candidate)
        
        return candidates[:2]

    async def _find_faq_candidates(self, content: str) -> List[SnippetCandidate]:
        """Find FAQ snippet candidates."""
        candidates = []
        
        # Look for Q&A patterns
        qa_patterns = [
            r'Q:\s*([^?]+\?)\s*A:\s*([^Q]+)',
            r'Question:\s*([^?]+\?)\s*Answer:\s*([^Q]+)',
            r'([^?]+\?)\s*\n\s*([^?]+(?:\.|$))'
        ]
        
        for pattern in qa_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                question = match.group(1).strip()
                answer = match.group(2).strip()
                
                if len(answer) <= self.max_snippet_length:
                    candidate = SnippetCandidate(
                        snippet_type=SnippetType.FAQ,
                        content=f"Q: {question}\nA: {answer}",
                        question=question,
                        answer=answer,
                        confidence_score=0.8,
                        optimization_suggestions=[
                            "Keep answers concise",
                            "Use FAQ schema markup"
                        ],
                        markup_requirements=["FAQ schema"]
                    )
                    candidates.append(candidate)
        
        return candidates[:3]

    async def _optimize_content_for_voice(self, content: str, 
                                        conversational_keywords: ConversationalKeywords) -> str:
        """Optimize content structure for voice search."""
        try:
            optimized_content = content
            
            # Add conversational introductions
            if not any(indicator in content.lower() for indicator in self.conversational_indicators):
                intro_phrases = [
                    "Here's what you need to know about",
                    "Let me explain",
                    "Here's how you can"
                ]
                # Add intro if content doesn't start conversationally
                first_sentence = content.split('.')[0] if '.' in content else content[:100]
                if not any(phrase in first_sentence.lower() for phrase in intro_phrases):
                    optimized_content = f"Here's what you need to know: {optimized_content}"
            
            # Optimize sentence structure for voice
            sentences = sent_tokenize(optimized_content)
            optimized_sentences = []
            
            for sentence in sentences:
                # Break down long sentences
                if len(sentence.split()) > 25:
                    # Simple sentence splitting (in production, use more sophisticated NLP)
                    parts = sentence.split(',')
                    if len(parts) > 1:
                        optimized_sentences.extend([part.strip() + '.' for part in parts])
                    else:
                        optimized_sentences.append(sentence)
                else:
                    optimized_sentences.append(sentence)
            
            optimized_content = ' '.join(optimized_sentences)
            
            # Add question-answer structure
            if conversational_keywords.question_variants:
                # Add a few key questions at the beginning
                key_questions = conversational_keywords.question_variants[:3]
                qa_section = "\n\nFrequently Asked Questions:\n"
                for i, question in enumerate(key_questions, 1):
                    qa_section += f"\nQ{i}: {question}\nA{i}: [Answer based on content]\n"
                
                optimized_content += qa_section
            
            return optimized_content
            
        except Exception as e:
            logger.error(f"Content optimization for voice failed: {e}")
            return content

    async def _calculate_natural_language_score(self, content: str) -> float:
        """Calculate natural language score."""
        return await self._calculate_conversational_language_score(content)

    async def _calculate_qa_score(self, content: str) -> float:
        """Calculate question-answering score."""
        return await self._calculate_qa_structure_score(content)

    async def _generate_voice_improvements(self, original: str, optimized: str, 
                                         keywords: ConversationalKeywords, 
                                         snippets: List[SnippetCandidate]) -> List[str]:
        """Generate voice search improvement suggestions."""
        improvements = []
        
        # Based on conversational analysis
        improvements.extend(keywords.optimization_opportunities)
        
        # Based on snippet opportunities
        if snippets:
            improvements.append(f"Optimize {len(snippets)} featured snippet opportunities")
        
        # General voice improvements
        improvements.extend([
            "Use more conversational language",
            "Add FAQ section with common questions",
            "Optimize for local voice search if applicable",
            "Include natural language phrases",
            "Structure content for voice delivery"
        ])
        
        return list(set(improvements))  # Remove duplicates

    # Local voice search methods
    async def _generate_local_intent_keywords(self, location: LocationData, 
                                            business_type: Optional[str]) -> List[str]:
        """Generate local intent keywords."""
        keywords = []
        
        # Location-based keywords
        location_keywords = [
            f"{location.city}",
            f"{location.city} {location.state}",
            f"in {location.city}",
            f"{location.city} area",
            f"near {location.city}"
        ]
        keywords.extend(location_keywords)
        
        # Business type + location
        if business_type:
            business_location_keywords = [
                f"{business_type} in {location.city}",
                f"{business_type} near me",
                f"best {business_type} {location.city}",
                f"local {business_type}",
                f"{business_type} {location.city} {location.state}"
            ]
            keywords.extend(business_location_keywords)
        
        return keywords

    async def _generate_near_me_variations(self, location: LocationData, 
                                         business_type: Optional[str]) -> List[str]:
        """Generate 'near me' variations."""
        variations = [
            "near me",
            "nearby",
            "close by",
            "in my area",
            "around here",
            "local",
            f"in {location.city}",
            f"near {location.city}"
        ]
        
        if business_type:
            business_variations = [
                f"{business_type} near me",
                f"nearby {business_type}",
                f"local {business_type}",
                f"{business_type} close by",
                f"{business_type} in my area"
            ]
            variations.extend(business_variations)
        
        return variations

    async def _identify_local_business_opportunities(self, location: LocationData, 
                                                   business_type: Optional[str]) -> List[str]:
        """Identify local business opportunities."""
        opportunities = [
            "Optimize Google My Business listing",
            "Create location-specific landing pages",
            "Add local business schema markup",
            "Include customer reviews and testimonials",
            "Create content about local events and community"
        ]
        
        if business_type:
            opportunities.extend([
                f"Target '{business_type} near me' keywords",
                f"Create {business_type}-specific local content",
                f"Optimize for voice searches about {business_type} services"
            ])
        
        return opportunities

    async def _generate_gmb_optimization_suggestions(self, location: LocationData) -> List[str]:
        """Generate Google My Business optimization suggestions."""
        return [
            "Complete all GMB profile sections",
            "Add high-quality photos and videos",
            "Encourage and respond to customer reviews",
            "Post regular updates and offers",
            "Use relevant categories and attributes",
            "Add Q&A section for voice search",
            "Include accurate business hours",
            "Add services and product listings"
        ]

    async def _generate_local_content_recommendations(self, location: LocationData, 
                                                    business_type: Optional[str]) -> List[str]:
        """Generate local content recommendations."""
        recommendations = [
            f"Create content about {location.city} local events",
            f"Write guides specific to {location.city} area",
            "Include local landmarks and references",
            "Create location-specific FAQ pages",
            "Add testimonials from local customers"
        ]
        
        if business_type:
            recommendations.extend([
                f"Create {business_type} guides for {location.city}",
                f"Write about {business_type} trends in {location.state}",
                f"Compare {business_type} options in {location.city}"
            ])
        
        return recommendations

    async def _calculate_local_voice_score(self, location: LocationData, 
                                         local_keywords: List[str], 
                                         near_me_variations: List[str]) -> float:
        """Calculate local voice search optimization score."""
        score_factors = []
        
        # Keyword coverage score
        keyword_score = min(len(local_keywords) / 20, 1.0)
        score_factors.append(keyword_score * 0.4)
        
        # Near me variation score
        variation_score = min(len(near_me_variations) / 10, 1.0)
        score_factors.append(variation_score * 0.3)
        
        # Location specificity score
        specificity_score = 0.8 if location.city and location.state else 0.4
        score_factors.append(specificity_score * 0.3)
        
        return sum(score_factors)

    # Question optimization methods
    async def _identify_content_questions(self, content: str) -> List[str]:
        """Identify questions in and about content."""
        questions = []
        
        # Find explicit questions in content
        for pattern in self.question_patterns:
            matches = re.findall(pattern + r'[^?]*\?', content, re.IGNORECASE | re.MULTILINE)
            questions.extend(matches)
        
        # Generate implicit questions about content topics
        if self.nlp:
            doc = self.nlp(content[:1000])  # Limit for performance
            topics = [token.text for token in doc if token.pos_ in ['NOUN'] and not token.is_stop]
            
            for topic in topics[:10]:
                implicit_questions = [
                    f"What is {topic}?",
                    f"How does {topic} work?",
                    f"Why is {topic} important?"
                ]
                questions.extend(implicit_questions)
        
        return list(set(questions))[:20]  # Limit and deduplicate

    async def _analyze_question_patterns(self, questions: List[str]) -> List[QuestionPattern]:
        """Analyze patterns in questions."""
        patterns = []
        
        # Group questions by type
        question_types = {
            'what': [q for q in questions if q.lower().startswith('what')],
            'how': [q for q in questions if q.lower().startswith('how')],
            'why': [q for q in questions if q.lower().startswith('why')],
            'when': [q for q in questions if q.lower().startswith('when')],
            'where': [q for q in questions if q.lower().startswith('where')],
            'who': [q for q in questions if q.lower().startswith('who')]
        }
        
        for question_type, type_questions in question_types.items():
            if type_questions:
                pattern = QuestionPattern(
                    question_type=question_type,
                    pattern=f"{question_type.capitalize()} + [topic/subject]",
                    example_questions=type_questions[:3],
                    answer_structure=self._get_answer_structure_for_type(question_type),
                    optimization_priority=len(type_questions)
                )
                patterns.append(pattern)
        
        return patterns

    def _get_answer_structure_for_type(self, question_type: str) -> str:
        """Get optimal answer structure for question type."""
        structures = {
            'what': 'Definition + explanation + examples',
            'how': 'Step-by-step process + tips',
            'why': 'Reasons + benefits + evidence',
            'when': 'Time/conditions + context',
            'where': 'Location + directions + alternatives',
            'who': 'Person/entity + background + relevance'
        }
        return structures.get(question_type, 'Clear answer + supporting details')

    async def _optimize_answers_for_voice(self, content: str, questions: List[str]) -> Dict[str, str]:
        """Optimize answers for voice delivery."""
        optimized_answers = {}
        
        for question in questions:
            # Extract or generate answer from content
            answer = await self._extract_answer_for_question(content, question)
            
            # Optimize answer for voice
            voice_optimized_answer = await self._optimize_answer_for_voice_delivery(answer)
            
            optimized_answers[question] = voice_optimized_answer
        
        return optimized_answers

    async def _extract_answer_for_question(self, content: str, question: str) -> str:
        """Extract answer for a specific question from content."""
        # Simplified answer extraction
        # In production, use more sophisticated NLP/QA models
        
        sentences = sent_tokenize(content)
        
        # Look for sentences that might answer the question
        question_keywords = [word.lower() for word in word_tokenize(question) 
                           if word.isalpha() and word.lower() not in stopwords.words('english')]
        
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            sentence_words = [word.lower() for word in word_tokenize(sentence) if word.isalpha()]
            score = len(set(question_keywords) & set(sentence_words))
            
            if score > best_score:
                best_score = score
                best_sentence = sentence
        
        return best_sentence if best_sentence else "Answer not found in content."

    async def _optimize_answer_for_voice_delivery(self, answer: str) -> str:
        """Optimize answer for voice delivery."""
        if not answer or answer == "Answer not found in content.":
            return answer
        
        # Make answer more conversational
        if not answer.strip().endswith(('.', '!', '?')):
            answer += '.'
        
        # Add conversational starter if needed
        conversational_starters = ['Here\'s the answer:', 'Simply put,', 'In short,']
        if not any(starter.lower() in answer.lower() for starter in conversational_starters):
            answer = f"Simply put, {answer.lower()}"
        
        return answer

    async def _generate_faq_structure(self, questions: List[str], 
                                    answers: Dict[str, str]) -> List[str]:
        """Generate FAQ structure suggestions."""
        suggestions = [
            "Create dedicated FAQ section",
            "Use schema markup for FAQ content",
            "Organize questions by topic/category",
            "Include 'People also ask' style questions",
            "Add voice-friendly answer format"
        ]
        
        if len(questions) > 10:
            suggestions.append("Consider breaking FAQ into multiple sections")
        
        if len(questions) < 5:
            suggestions.append("Add more common questions based on user queries")
        
        return suggestions

    async def _improve_conversational_flow(self, content: str, questions: List[str]) -> List[str]:
        """Improve conversational flow of content."""
        improvements = [
            "Use transitional phrases between sections",
            "Add conversational connectors (however, moreover, in addition)",
            "Include direct address to reader (you, your)",
            "Use active voice instead of passive",
            "Add call-to-action phrases"
        ]
        
        # Analyze current flow
        if not re.search(r'\b(you|your)\b', content, re.IGNORECASE):
            improvements.append("Add more direct reader address")
        
        if not re.search(r'\b(however|moreover|furthermore|additionally)\b', content, re.IGNORECASE):
            improvements.append("Add transitional phrases for better flow")
        
        return improvements

    async def _calculate_voice_answer_readiness(self, questions: List[str], 
                                              answers: Dict[str, str]) -> float:
        """Calculate voice answer readiness score."""
        if not questions:
            return 0.0
        
        score_factors = []
        
        # Answer completeness
        answered_questions = len([q for q in questions if answers.get(q) and answers[q] != "Answer not found in content."])
        completeness_score = answered_questions / len(questions)
        score_factors.append(completeness_score * 0.4)
        
        # Answer length appropriateness for voice
        appropriate_length_count = 0
        for answer in answers.values():
            if answer and answer != "Answer not found in content.":
                word_count = len(answer.split())
                if 10 <= word_count <= 50:  # Good for voice
                    appropriate_length_count += 1
        
        length_score = appropriate_length_count / max(len(answers), 1)
        score_factors.append(length_score * 0.3)
        
        # Conversational language in answers
        conversational_count = 0
        for answer in answers.values():
            if answer and any(indicator in answer.lower() for indicator in ['simply put', 'here\'s', 'you can', 'in short']):
                conversational_count += 1
        
        conversational_score = conversational_count / max(len(answers), 1)
        score_factors.append(conversational_score * 0.3)
        
        return sum(score_factors)

    # Additional utility methods
    async def _extract_implicit_questions(self, content: str) -> List[str]:
        """Extract implicit questions that content could answer."""
        implicit_questions = []
        
        # Based on content structure and topics
        if self.nlp:
            doc = self.nlp(content[:1000])
            entities = [ent.text for ent in doc.ents if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT']]
            
            for entity in entities[:5]:
                implicit_questions.extend([
                    f"What is {entity}?",
                    f"Where is {entity}?",
                    f"How does {entity} work?"
                ])
        
        return implicit_questions[:10]

    async def _calculate_snippet_priority(self, candidates: List[SnippetCandidate], 
                                        questions: List[str]) -> int:
        """Calculate optimization priority for snippets."""
        if not candidates:
            return 1
        
        # High confidence candidates get higher priority
        avg_confidence = np.mean([c.confidence_score for c in candidates])
        
        # More candidates = higher priority
        candidate_factor = min(len(candidates) / 5, 1.0)
        
        # Question coverage factor
        question_factor = min(len(questions) / 10, 1.0)
        
        priority = int((avg_confidence + candidate_factor + question_factor) / 3 * 10)
        
        return max(min(priority, 10), 1)

    async def _assess_snippet_difficulty(self, candidates: List[SnippetCandidate]) -> str:
        """Assess implementation difficulty for snippets."""
        if not candidates:
            return "low"
        
        avg_confidence = np.mean([c.confidence_score for c in candidates])
        
        if avg_confidence >= 0.8:
            return "low"
        elif avg_confidence >= 0.6:
            return "medium"
        else:
            return "high"

    async def _estimate_voice_traffic(self, questions: List[str]) -> int:
        """Estimate potential voice search traffic."""
        # Simplified estimation based on question count and types
        base_traffic = len(questions) * 50  # Base estimate per question
        
        # Boost for common question types
        common_starters = ['what is', 'how to', 'where can', 'how much']
        boost_factor = sum(1 for q in questions if any(starter in q.lower() for starter in common_starters))
        
        estimated_traffic = base_traffic + (boost_factor * 25)
        
        return min(estimated_traffic, 5000)  # Cap at reasonable maximum

    async def _identify_structured_data_needs(self, candidates: List[SnippetCandidate]) -> List[str]:
        """Identify structured data requirements."""
        structured_data_needs = set()
        
        for candidate in candidates:
            structured_data_needs.update(candidate.markup_requirements)
        
        # Add general recommendations
        structured_data_needs.update([
            "Organization schema",
            "WebPage schema",
            "BreadcrumbList schema"
        ])
        
        return list(structured_data_needs)