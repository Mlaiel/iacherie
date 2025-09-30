"""
Voice Search Optimizer for Ainflue Platform
===========================================

Advanced voice search optimization for content discovery and creator visibility.
Optimizes content for voice queries, featured snippets, and conversational search.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import asyncpg
from datetime import datetime
import spacy
from collections import defaultdict, Counter
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from textstat import flesch_reading_ease

logger = logging.getLogger(__name__)

class VoiceQueryType(Enum):
    """Types of voice search queries."""
    QUESTION = "question"
    COMMAND = "command"
    LOCAL = "local"
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    CONVERSATIONAL = "conversational"

class VoiceIntent(Enum):
    """Voice search intents."""
    WHO = "who"
    WHAT = "what"
    WHERE = "where"
    WHEN = "when"
    WHY = "why"
    HOW = "how"
    FIND = "find"
    PLAY = "play"
    SHOW = "show"
    BOOK = "book"
    BUY = "buy"
    CALL = "call"

@dataclass
class VoiceQuery:
    """Voice search query analysis."""
    query_id: str
    original_query: str
    normalized_query: str
    query_type: VoiceQueryType
    intent: VoiceIntent
    entities: List[str]
    keywords: List[str]
    location: Optional[str]
    confidence_score: float
    length: int
    complexity: str
    created_at: datetime

@dataclass
class VoiceOptimizedContent:
    """Voice-optimized content structure."""
    content_id: str
    title: str
    featured_snippet: str
    qa_pairs: List[Dict[str, str]]
    conversational_keywords: List[str]
    voice_search_score: float
    readability_score: float
    structure_score: float
    recommendations: List[str]
    created_at: datetime

@dataclass
class FeaturedSnippetData:
    """Featured snippet optimization data."""
    snippet_id: str
    content_id: str
    snippet_type: str  # paragraph, list, table, video
    query: str
    content: str
    word_count: int
    position: int
    optimization_score: float
    recommendations: List[str]
    created_at: datetime

class VoiceSearchOptimizer:
    """
    Advanced Voice Search Optimizer
    
    Features:
    - Voice query analysis and intent detection
    - Featured snippet optimization
    - Conversational keyword research
    - Q&A content generation
    - Local voice search optimization
    - Voice-friendly content structuring
    - Answer box optimization
    """
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        self.nlp = None
        self.voice_patterns = self._load_voice_patterns()
        self._initialize_nlp()
        
    def _initialize_nlp(self):
        """Initialize NLP tools."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('maxent_ne_chunker', quiet=True)
            nltk.download('words', quiet=True)
        except Exception as e:
            logger.warning(f"NLP initialization warning: {e}")
    
    def _load_voice_patterns(self) -> Dict[str, List[str]]:
        """Load voice search query patterns."""
        return {
            'question_starters': [
                'what is', 'what are', 'who is', 'who are', 'where is', 'where are',
                'when is', 'when does', 'why is', 'why does', 'how to', 'how do',
                'how can', 'how much', 'how many', 'which is', 'which are'
            ],
            'command_starters': [
                'find me', 'show me', 'play', 'call', 'book', 'buy', 'get',
                'search for', 'look up', 'tell me about'
            ],
            'local_indicators': [
                'near me', 'nearby', 'close to', 'in my area', 'around here',
                'local', 'closest', 'directions to'
            ],
            'conversational_phrases': [
                'i want to', 'i need to', 'i\'m looking for', 'can you help me',
                'i would like', 'please help', 'show me how'
            ]
        }
    
    async def analyze_voice_query(
        self,
        query: str,
        user_location: Optional[str] = None
    ) -> VoiceQuery:
        """
        Analyze a voice search query for optimization insights.
        
        Args:
            query: Voice search query text
            user_location: User's location context
            
        Returns:
            VoiceQuery analysis object
        """
        try:
            query_id = f"vq_{hash(query)}_{int(datetime.utcnow().timestamp())}"
            
            # Normalize query
            normalized_query = self._normalize_voice_query(query)
            
            # Detect query type
            query_type = self._detect_query_type(normalized_query)
            
            # Extract intent
            intent = self._extract_intent(normalized_query)
            
            # Extract entities
            entities = self._extract_entities(normalized_query)
            
            # Extract keywords
            keywords = self._extract_keywords(normalized_query)
            
            # Detect location mentions
            location = self._extract_location(normalized_query, user_location)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                normalized_query, query_type, intent, entities
            )
            
            # Analyze complexity
            complexity = self._analyze_query_complexity(normalized_query)
            
            voice_query = VoiceQuery(
                query_id=query_id,
                original_query=query,
                normalized_query=normalized_query,
                query_type=query_type,
                intent=intent,
                entities=entities,
                keywords=keywords,
                location=location,
                confidence_score=confidence_score,
                length=len(query.split()),
                complexity=complexity,
                created_at=datetime.utcnow()
            )
            
            # Store analysis
            await self._store_voice_query_analysis(voice_query)
            
            return voice_query
            
        except Exception as e:
            logger.error(f"Error analyzing voice query: {e}")
            raise
    
    async def optimize_content_for_voice(
        self,
        content_id: str,
        content: str,
        target_queries: List[str],
        content_type: str = "article"
    ) -> VoiceOptimizedContent:
        """
        Optimize content for voice search discovery.
        
        Args:
            content_id: Content identifier
            content: Content text to optimize
            target_queries: Target voice queries
            content_type: Type of content being optimized
            
        Returns:
            VoiceOptimizedContent object with optimizations
        """
        try:
            # Generate optimized title
            optimized_title = await self._optimize_title_for_voice(content, target_queries)
            
            # Create featured snippet
            featured_snippet = await self._create_featured_snippet(content, target_queries)
            
            # Generate Q&A pairs
            qa_pairs = await self._generate_qa_pairs(content, target_queries)
            
            # Extract conversational keywords
            conversational_keywords = self._extract_conversational_keywords(
                content, target_queries
            )
            
            # Calculate voice search score
            voice_search_score = self._calculate_voice_search_score(
                content, target_queries, qa_pairs
            )
            
            # Calculate readability score
            readability_score = flesch_reading_ease(content)
            
            # Calculate structure score
            structure_score = self._calculate_structure_score(content)
            
            # Generate recommendations
            recommendations = self._generate_voice_optimization_recommendations(
                content, voice_search_score, readability_score, structure_score
            )
            
            optimized_content = VoiceOptimizedContent(
                content_id=content_id,
                title=optimized_title,
                featured_snippet=featured_snippet,
                qa_pairs=qa_pairs,
                conversational_keywords=conversational_keywords,
                voice_search_score=voice_search_score,
                readability_score=readability_score,
                structure_score=structure_score,
                recommendations=recommendations,
                created_at=datetime.utcnow()
            )
            
            # Store optimization
            await self._store_voice_optimization(optimized_content)
            
            return optimized_content
            
        except Exception as e:
            logger.error(f"Error optimizing content for voice: {e}")
            raise
    
    async def optimize_featured_snippets(
        self,
        content_id: str,
        content: str,
        target_queries: List[str]
    ) -> List[FeaturedSnippetData]:
        """
        Optimize content for featured snippets across multiple queries.
        
        Args:
            content_id: Content identifier
            content: Content text
            target_queries: Target queries for snippets
            
        Returns:
            List of FeaturedSnippetData objects
        """
        try:
            snippets = []
            
            for query in target_queries:
                # Analyze query for snippet type
                snippet_type = self._determine_snippet_type(query, content)
                
                # Generate snippet content
                snippet_content = await self._generate_snippet_content(
                    content, query, snippet_type
                )
                
                if snippet_content:
                    snippet_id = f"fs_{hash(query + content_id)}_{int(datetime.utcnow().timestamp())}"
                    
                    # Calculate optimization score
                    optimization_score = self._calculate_snippet_score(
                        snippet_content, query, snippet_type
                    )
                    
                    # Generate recommendations
                    recommendations = self._generate_snippet_recommendations(
                        snippet_content, query, snippet_type, optimization_score
                    )
                    
                    snippet_data = FeaturedSnippetData(
                        snippet_id=snippet_id,
                        content_id=content_id,
                        snippet_type=snippet_type,
                        query=query,
                        content=snippet_content,
                        word_count=len(snippet_content.split()),
                        position=0,  # Would be determined by actual search results
                        optimization_score=optimization_score,
                        recommendations=recommendations,
                        created_at=datetime.utcnow()
                    )
                    
                    snippets.append(snippet_data)
                    
                    # Store snippet data
                    await self._store_featured_snippet(snippet_data)
            
            return snippets
            
        except Exception as e:
            logger.error(f"Error optimizing featured snippets: {e}")
            return []
    
    async def research_voice_keywords(
        self,
        seed_keywords: List[str],
        industry: str,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Research voice search keywords and phrases.
        
        Args:
            seed_keywords: Base keywords to expand
            industry: Industry/niche context
            location: Location context for local voice search
            
        Returns:
            Voice keyword research results
        """
        try:
            # Expand keywords with voice modifiers
            voice_keywords = self._expand_with_voice_modifiers(seed_keywords)
            
            # Add question-based keywords
            question_keywords = self._generate_question_keywords(seed_keywords)
            
            # Add conversational keywords
            conversational_keywords = self._generate_conversational_keywords(seed_keywords)
            
            # Add local voice keywords if location provided
            local_keywords = []
            if location:
                local_keywords = self._generate_local_voice_keywords(seed_keywords, location)
            
            # Combine all keywords
            all_keywords = (
                voice_keywords + question_keywords + 
                conversational_keywords + local_keywords
            )
            
            # Analyze keyword metrics
            keyword_analysis = await self._analyze_voice_keywords(all_keywords, industry)
            
            # Identify trending voice queries
            trending_queries = await self._identify_trending_voice_queries(
                seed_keywords, industry
            )
            
            return {
                'seed_keywords': seed_keywords,
                'voice_keywords': voice_keywords,
                'question_keywords': question_keywords,
                'conversational_keywords': conversational_keywords,
                'local_keywords': local_keywords,
                'keyword_analysis': keyword_analysis,
                'trending_queries': trending_queries,
                'total_keywords': len(all_keywords),
                'research_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error researching voice keywords: {e}")
            return {}
    
    def _normalize_voice_query(self, query: str) -> str:
        """Normalize voice query for analysis."""
        # Convert to lowercase
        normalized = query.lower().strip()
        
        # Remove filler words common in voice queries
        filler_words = ['um', 'uh', 'like', 'you know', 'actually', 'basically']
        for filler in filler_words:
            normalized = normalized.replace(filler, '')
        
        # Normalize contractions
        contractions = {
            "what's": "what is",
            "where's": "where is",
            "who's": "who is",
            "how's": "how is",
            "there's": "there is",
            "i'm": "i am",
            "you're": "you are",
            "can't": "cannot",
            "won't": "will not",
            "don't": "do not"
        }
        
        for contraction, expansion in contractions.items():
            normalized = normalized.replace(contraction, expansion)
        
        # Clean up extra spaces
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _detect_query_type(self, query: str) -> VoiceQueryType:
        """Detect the type of voice query."""
        query_lower = query.lower()
        
        # Check for question patterns
        question_patterns = self.voice_patterns['question_starters']
        if any(pattern in query_lower for pattern in question_patterns):
            return VoiceQueryType.QUESTION
        
        # Check for command patterns
        command_patterns = self.voice_patterns['command_starters']
        if any(pattern in query_lower for pattern in command_patterns):
            return VoiceQueryType.COMMAND
        
        # Check for local indicators
        local_patterns = self.voice_patterns['local_indicators']
        if any(pattern in query_lower for pattern in local_patterns):
            return VoiceQueryType.LOCAL
        
        # Check for conversational patterns
        conversational_patterns = self.voice_patterns['conversational_phrases']
        if any(pattern in query_lower for pattern in conversational_patterns):
            return VoiceQueryType.CONVERSATIONAL
        
        # Default classification based on query structure
        if query.endswith('?'):
            return VoiceQueryType.QUESTION
        elif any(word in query_lower for word in ['buy', 'purchase', 'order', 'book']):
            return VoiceQueryType.TRANSACTIONAL
        elif any(word in query_lower for word in ['go to', 'navigate', 'directions']):
            return VoiceQueryType.NAVIGATIONAL
        
        return VoiceQueryType.INFORMATIONAL
    
    def _extract_intent(self, query: str) -> VoiceIntent:
        """Extract the primary intent from voice query."""
        query_lower = query.lower()
        
        # Intent mapping based on query starters
        intent_patterns = {
            VoiceIntent.WHO: ['who is', 'who are', 'who was', 'who were'],
            VoiceIntent.WHAT: ['what is', 'what are', 'what was', 'what were', 'what does'],
            VoiceIntent.WHERE: ['where is', 'where are', 'where can', 'where do'],
            VoiceIntent.WHEN: ['when is', 'when are', 'when does', 'when did'],
            VoiceIntent.WHY: ['why is', 'why are', 'why does', 'why did'],
            VoiceIntent.HOW: ['how to', 'how do', 'how can', 'how much', 'how many'],
            VoiceIntent.FIND: ['find', 'search for', 'look for', 'locate'],
            VoiceIntent.PLAY: ['play', 'start playing', 'put on'],
            VoiceIntent.SHOW: ['show me', 'display', 'demonstrate'],
            VoiceIntent.BOOK: ['book', 'reserve', 'schedule'],
            VoiceIntent.BUY: ['buy', 'purchase', 'order', 'get'],
            VoiceIntent.CALL: ['call', 'phone', 'contact']
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                return intent
        
        # Default to WHAT for informational queries
        return VoiceIntent.WHAT
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract named entities from voice query."""
        entities = []
        
        if self.nlp:
            doc = self.nlp(query)
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'description': spacy.explain(ent.label_)
                })
        else:
            # Fallback using NLTK
            try:
                tokens = word_tokenize(query)
                pos_tags = pos_tag(tokens)
                tree = ne_chunk(pos_tags)
                
                for subtree in tree:
                    if hasattr(subtree, 'label'):
                        entity_name = ' '.join([token for token, pos in subtree.leaves()])
                        entities.append({
                            'text': entity_name,
                            'label': subtree.label(),
                            'description': subtree.label()
                        })
            except Exception as e:
                logger.warning(f"Entity extraction failed: {e}")
        
        return entities
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from voice query."""
        # Remove stop words common in voice queries
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'can', 'could', 'should', 'would',
            'me', 'my', 'i', 'you', 'your'
        }
        
        words = query.lower().split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def _extract_location(self, query: str, user_location: Optional[str]) -> Optional[str]:
        """Extract location information from query."""
        # Look for explicit location mentions
        location_patterns = [
            r'in ([A-Z][a-z]+ ?[A-Z]?[a-z]*)',
            r'near ([A-Z][a-z]+ ?[A-Z]?[a-z]*)',
            r'at ([A-Z][a-z]+ ?[A-Z]?[a-z]*)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1)
        
        # Check for "near me" or similar and use user location
        if any(phrase in query.lower() for phrase in ['near me', 'nearby', 'close to me']):
            return user_location
        
        return None
    
    def _calculate_confidence_score(
        self,
        query: str,
        query_type: VoiceQueryType,
        intent: VoiceIntent,
        entities: List[str]
    ) -> float:
        """Calculate confidence score for voice query analysis."""
        score = 0.0
        
        # Base score for query length (voice queries tend to be longer)
        word_count = len(query.split())
        if 3 <= word_count <= 10:
            score += 30
        elif word_count > 10:
            score += 20
        
        # Score for clear intent patterns
        if any(pattern in query.lower() for pattern in self.voice_patterns['question_starters']):
            score += 25
        
        # Score for entities found
        if entities:
            score += min(len(entities) * 10, 25)
        
        # Score for natural language patterns
        conversational_indicators = ['i', 'me', 'my', 'please', 'can you', 'help me']
        if any(indicator in query.lower() for indicator in conversational_indicators):
            score += 20
        
        return min(score, 100.0)
    
    def _analyze_query_complexity(self, query: str) -> str:
        """Analyze the complexity of the voice query."""
        word_count = len(query.split())
        
        if word_count <= 3:
            return "simple"
        elif word_count <= 7:
            return "medium"
        else:
            return "complex"
    
    async def _optimize_title_for_voice(
        self,
        content: str,
        target_queries: List[str]
    ) -> str:
        """Optimize title for voice search visibility."""
        # Extract question-based titles from target queries
        question_queries = [q for q in target_queries if '?' in q or any(
            starter in q.lower() for starter in self.voice_patterns['question_starters']
        )]
        
        if question_queries:
            # Use the most natural question as title
            primary_question = max(question_queries, key=len)
            return primary_question.title()
        
        # Fallback: create question-based title from content
        sentences = sent_tokenize(content)
        if sentences:
            first_sentence = sentences[0]
            # Convert statement to question if possible
            if not first_sentence.endswith('?'):
                return f"What You Need to Know: {first_sentence}"
            return first_sentence
        
        return "Voice Search Optimized Content"
    
    async def _create_featured_snippet(
        self,
        content: str,
        target_queries: List[str]
    ) -> str:
        """Create optimized featured snippet from content."""
        sentences = sent_tokenize(content)
        
        # Find the most relevant sentences for the queries
        relevant_sentences = []
        
        for query in target_queries:
            query_keywords = self._extract_keywords(query)
            
            for sentence in sentences:
                # Score sentence relevance
                sentence_lower = sentence.lower()
                keyword_matches = sum(1 for keyword in query_keywords if keyword in sentence_lower)
                
                if keyword_matches > 0:
                    relevant_sentences.append((sentence, keyword_matches))
        
        if not relevant_sentences:
            # Fallback to first few sentences
            return ' '.join(sentences[:2])
        
        # Sort by relevance and take top sentences
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [s[0] for s in relevant_sentences[:2]]
        
        snippet = ' '.join(top_sentences)
        
        # Ensure snippet is within optimal length (40-60 words)
        words = snippet.split()
        if len(words) > 60:
            snippet = ' '.join(words[:60]) + '...'
        
        return snippet
    
    async def _generate_qa_pairs(
        self,
        content: str,
        target_queries: List[str]
    ) -> List[Dict[str, str]]:
        """Generate Q&A pairs for voice search optimization."""
        qa_pairs = []
        
        # Use target queries as questions
        for query in target_queries:
            if '?' in query or any(starter in query.lower() for starter in self.voice_patterns['question_starters']):
                # Extract relevant answer from content
                answer = await self._extract_answer_for_question(content, query)
                if answer:
                    qa_pairs.append({
                        'question': query,
                        'answer': answer
                    })
        
        # Generate additional Q&A pairs from content
        additional_qa = self._generate_implicit_qa_pairs(content)
        qa_pairs.extend(additional_qa)
        
        return qa_pairs
    
    async def _extract_answer_for_question(self, content: str, question: str) -> str:
        """Extract relevant answer from content for a specific question."""
        sentences = sent_tokenize(content)
        question_keywords = self._extract_keywords(question)
        
        # Find most relevant sentence
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            score = sum(1 for keyword in question_keywords if keyword in sentence_lower)
            
            if score > best_score:
                best_score = score
                best_sentence = sentence
        
        # If found a good match, potentially expand with context
        if best_sentence and best_score > 0:
            sentence_index = sentences.index(best_sentence)
            
            # Add following sentence for context if it's short
            if (sentence_index + 1 < len(sentences) and 
                len(best_sentence.split()) < 30):
                best_sentence += " " + sentences[sentence_index + 1]
        
        return best_sentence
    
    def _generate_implicit_qa_pairs(self, content: str) -> List[Dict[str, str]]:
        """Generate implicit Q&A pairs from content structure."""
        qa_pairs = []
        sentences = sent_tokenize(content)
        
        # Look for definition patterns
        for i, sentence in enumerate(sentences):
            if any(pattern in sentence.lower() for pattern in [' is ', ' are ', ' means ', ' refers to ']):
                # Try to form a "what is" question
                words = sentence.split()
                subject_end = next((i for i, word in enumerate(words) if word.lower() in ['is', 'are', 'means']), -1)
                
                if subject_end > 0:
                    subject = ' '.join(words[:subject_end])
                    if len(subject.split()) <= 4:  # Reasonable subject length
                        question = f"What is {subject}?"
                        qa_pairs.append({
                            'question': question,
                            'answer': sentence
                        })
        
        return qa_pairs[:5]  # Limit to 5 additional pairs
    
    def _extract_conversational_keywords(
        self,
        content: str,
        target_queries: List[str]
    ) -> List[str]:
        """Extract keywords optimized for conversational search."""
        conversational_keywords = []
        
        # Extract keywords from target queries
        for query in target_queries:
            keywords = self._extract_keywords(query)
            conversational_keywords.extend(keywords)
        
        # Add natural language variations
        content_keywords = self._extract_keywords(content)
        
        # Combine and deduplicate
        all_keywords = list(set(conversational_keywords + content_keywords))
        
        return all_keywords
    
    def _calculate_voice_search_score(
        self,
        content: str,
        target_queries: List[str],
        qa_pairs: List[Dict[str, str]]
    ) -> float:
        """Calculate overall voice search optimization score."""
        score = 0.0
        
        # Question coverage score (30 points)
        question_queries = [q for q in target_queries if '?' in q]
        if question_queries:
            answered_questions = len(qa_pairs)
            coverage_ratio = min(answered_questions / len(question_queries), 1.0)
            score += coverage_ratio * 30
        
        # Conversational tone score (25 points)
        conversational_indicators = ['you', 'your', 'we', 'our', 'can', 'will', 'should']
        content_lower = content.lower()
        indicator_count = sum(1 for indicator in conversational_indicators if indicator in content_lower)
        score += min(indicator_count * 3, 25)
        
        # Readability score (25 points)
        readability = flesch_reading_ease(content)
        if readability >= 60:  # Easy to read
            score += 25
        elif readability >= 30:  # Moderately easy
            score += 15
        
        # Structure score (20 points)
        if qa_pairs:
            score += 10
        sentences = sent_tokenize(content)
        if len(sentences) > 0:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg_sentence_length <= 20:  # Voice-friendly sentence length
                score += 10
        
        return min(score, 100.0)
    
    def _calculate_structure_score(self, content: str) -> float:
        """Calculate content structure score for voice search."""
        score = 0.0
        sentences = sent_tokenize(content)
        
        if not sentences:
            return 0.0
        
        # Sentence length score (40 points)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_sentence_length <= 15:
            score += 40
        elif avg_sentence_length <= 25:
            score += 25
        
        # Paragraph structure score (30 points)
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            score += 15
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs if p.strip()) / max(len(paragraphs), 1)
        if avg_paragraph_length <= 100:
            score += 15
        
        # List and formatting score (30 points)
        if any(indicator in content for indicator in ['\n-', '\n*', '\n1.', '\n2.']):
            score += 15
        if any(indicator in content for indicator in ['?', ':']):
            score += 15
        
        return min(score, 100.0)
    
    async def _store_voice_query_analysis(self, voice_query: VoiceQuery):
        """Store voice query analysis in database."""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO voice_query_analysis 
                    (query_id, original_query, normalized_query, query_type, intent,
                     entities, keywords, location, confidence_score, length, complexity, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """, 
                    voice_query.query_id,
                    voice_query.original_query,
                    voice_query.normalized_query,
                    voice_query.query_type.value,
                    voice_query.intent.value,
                    json.dumps(voice_query.entities),
                    json.dumps(voice_query.keywords),
                    voice_query.location,
                    voice_query.confidence_score,
                    voice_query.length,
                    voice_query.complexity,
                    voice_query.created_at
                )
        except Exception as e:
            logger.error(f"Error storing voice query analysis: {e}")
    
    def _expand_with_voice_modifiers(self, keywords: List[str]) -> List[str]:
        """Expand keywords with voice search modifiers."""
        modifiers = [
            "how to", "what is", "where is", "who is", "when is", "why is",
            "best", "top", "find", "near me", "help me", "show me"
        ]
        
        expanded = []
        for keyword in keywords:
            expanded.append(keyword)  # Original keyword
            for modifier in modifiers:
                if modifier.endswith(" is"):
                    expanded.append(f"{modifier} {keyword}")
                elif modifier in ["best", "top"]:
                    expanded.append(f"{modifier} {keyword}")
                elif modifier == "how to":
                    expanded.append(f"{modifier} {keyword}")
                    expanded.append(f"{modifier} use {keyword}")
                else:
                    expanded.append(f"{modifier} {keyword}")
        
        return list(set(expanded))
    
    def _generate_question_keywords(self, keywords: List[str]) -> List[str]:
        """Generate question-based keywords."""
        questions = []
        
        question_templates = [
            "what is {keyword}",
            "how does {keyword} work",
            "where can I find {keyword}",
            "who uses {keyword}",
            "when to use {keyword}",
            "why is {keyword} important",
            "how to choose {keyword}",
            "what are the benefits of {keyword}"
        ]
        
        for keyword in keywords:
            for template in question_templates:
                questions.append(template.format(keyword=keyword))
        
        return questions
    
    def _generate_conversational_keywords(self, keywords: List[str]) -> List[str]:
        """Generate conversational style keywords."""
        conversational = []
        
        conversational_templates = [
            "I need help with {keyword}",
            "can you help me with {keyword}",
            "I'm looking for {keyword}",
            "tell me about {keyword}",
            "I want to know about {keyword}",
            "show me how to {keyword}",
            "help me understand {keyword}"
        ]
        
        for keyword in keywords:
            for template in conversational_templates:
                conversational.append(template.format(keyword=keyword))
        
        return conversational

# Export classes
__all__ = [
    'VoiceSearchOptimizer',
    'VoiceQuery',
    'VoiceOptimizedContent',
    'FeaturedSnippetData',
    'VoiceQueryType',
    'VoiceIntent'
]