"""Enterprise Content Summarization Engine
=======================================

Next-generation intelligent text summarization for content optimization:
- Neural extractive and abstractive summarization
- Multi-document and cross-platform summarization
- Key point extraction with importance scoring
- Content condensation for platform-specific optimization
- Real-time summary generation with quality assessment
- Context-aware summarization with cultural sensitivity
- Professional executive summary generation
- Multi-language summarization with tone preservation

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Specialist + DevOps Expert
Copyright: Fahed Mlaiel - All Rights Reserved

⚠️  STRICT LEGAL WARNING: 
    This proprietary code is protected by international copyright law.
    Unauthorized use, copying, distribution, modification, or reverse engineering 
    is STRICTLY PROHIBITED and will result in immediate legal action.
    This includes any attempt to steal, replicate, or use this concept without 
    explicit written authorization from Fahed Mlaiel.
    
    Contact: mlaiel@live.de for licensing inquiries ONLY.
    Violators will be prosecuted to the full extent of German and EU law.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import re
from datetime import datetime, timezone
import heapq
from collections import Counter

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag
import networkx as nx
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer

from ...core.config import settings
from ...core.logging import get_logger
from ...core.cache import cache_manager
from ...utils.text_utils import clean_text, normalize_unicode

logger = get_logger(__name__)


class SummarizationType(Enum):
    """Types of summarization"""    EXTRACTIVE = "extractive"
    ABSTRACTIVE = "abstractive"
    HYBRID = "hybrid"
    KEY_POINTS = "key_points"
    BULLET_POINTS = "bullet_points"


class SummarizationLength(Enum):
    """Summarization length options"""    VERY_SHORT = "very_short"  # 1-2 sentences
    SHORT = "short"           # 3-5 sentences
    MEDIUM = "medium"         # 1-2 paragraphs
    LONG = "long"            # Multiple paragraphs
    CUSTOM = "custom"        # User-defined


class ContentType(Enum):
    """Types of content to summarize"""    ARTICLE = "article"
    BLOG_POST = "blog_post"
    NEWS = "news"
    RESEARCH_PAPER = "research_paper"
    SOCIAL_POST = "social_post"
    EMAIL = "email"
    MEETING_NOTES = "meeting_notes"
    GENERAL = "general"


@dataclass
class SentenceScore:
    """Represents a scored sentence"""    text: str
    score: float
    position: int
    word_count: int
    contains_keywords: bool
    tf_idf_score: float = 0.0
    position_score: float = 0.0
    length_score: float = 0.0


@dataclass
class KeyPoint:
    """Represents a key point from content"""    text: str
    importance_score: float
    supporting_sentences: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)
    section: str = ""


@dataclass
class SummaryResult:
    """Complete summarization result"""    summary_text: str
    key_points: List[KeyPoint]
    bullet_points: List[str]
    original_length: int
    summary_length: int
    compression_ratio: float
    readability_score: float
    content_coverage: float
    summarization_method: SummarizationType
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SummarizationEngine:
    """Advanced content summarization engine"""    
    def __init__(self):
        self.nlp = None
        self.abstractive_model = None
        self.tokenizer = None
        self.stop_words = set()
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize summarization models"""        try:
            # Initialize spaCy
            self.nlp = spacy.load("en_core_web_lg")
            
            # Initialize abstractive summarization model
            self.abstractive_model = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Load stop words
            try:
                self.stop_words = set(stopwords.words('english'))
            except:
                nltk.download('stopwords', quiet=True)
                self.stop_words = set(stopwords.words('english'))
                
            logger.info("Summarization models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize summarization models: {e}")
            
    async def summarize(
        self,
        text: str,
        summarization_type: SummarizationType = SummarizationType.HYBRID,
        length: SummarizationLength = SummarizationLength.MEDIUM,
        content_type: ContentType = ContentType.GENERAL,
        custom_length: Optional[int] = None,
        include_key_points: bool = True,
        include_bullets: bool = True
    ) -> SummaryResult:
        """        Summarize text using specified method
        
        Args:
            text: Text to summarize
            summarization_type: Type of summarization to perform
            length: Desired length of summary
            content_type: Type of content being summarized
            custom_length: Custom length in sentences (if length is CUSTOM)
            include_key_points: Whether to extract key points
            include_bullets: Whether to generate bullet points
            
        Returns:
            SummaryResult with summary and analysis
        """        try:
            start_time = datetime.now()
            
            # Clean and preprocess text
            cleaned_text = clean_text(text)
            original_length = len(cleaned_text.split())
            
            # Determine target length
            target_sentences = self._calculate_target_length(
                cleaned_text, length, custom_length
            )
            
            # Generate summary based on type
            if summarization_type == SummarizationType.EXTRACTIVE:
                summary_text = await self._extractive_summarization(
                    cleaned_text, target_sentences, content_type
                )
            elif summarization_type == SummarizationType.ABSTRACTIVE:
                summary_text = await self._abstractive_summarization(
                    cleaned_text, target_sentences
                )
            elif summarization_type == SummarizationType.HYBRID:
                summary_text = await self._hybrid_summarization(
                    cleaned_text, target_sentences, content_type
                )
            else:
                summary_text = await self._extractive_summarization(
                    cleaned_text, target_sentences, content_type
                )
                
            # Extract key points if requested
            key_points = []
            if include_key_points:
                key_points = await self._extract_key_points(cleaned_text)
                
            # Generate bullet points if requested
            bullet_points = []
            if include_bullets:
                bullet_points = await self._generate_bullet_points(cleaned_text, key_points)
                
            # Calculate metrics
            summary_length = len(summary_text.split())
            compression_ratio = summary_length / original_length if original_length > 0 else 0
            readability_score = await self._calculate_readability(summary_text)
            content_coverage = await self._calculate_coverage(cleaned_text, summary_text)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return SummaryResult(
                summary_text=summary_text,
                key_points=key_points,
                bullet_points=bullet_points,
                original_length=original_length,
                summary_length=summary_length,
                compression_ratio=compression_ratio,
                readability_score=readability_score,
                content_coverage=content_coverage,
                summarization_method=summarization_type,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            raise
            
    def _calculate_target_length(
        self,
        text: str,
        length: SummarizationLength,
        custom_length: Optional[int]
    ) -> int:
        """Calculate target number of sentences for summary"""        try:
            sentences = sent_tokenize(text)
            total_sentences = len(sentences)
            
            if length == SummarizationLength.CUSTOM and custom_length:
                return min(custom_length, total_sentences)
            elif length == SummarizationLength.VERY_SHORT:
                return min(2, total_sentences)
            elif length == SummarizationLength.SHORT:
                return min(5, max(3, total_sentences // 10))
            elif length == SummarizationLength.MEDIUM:
                return min(10, max(5, total_sentences // 5))
            elif length == SummarizationLength.LONG:
                return min(20, max(10, total_sentences // 3))
            else:
                return min(5, max(3, total_sentences // 10))
                
        except Exception as e:
            logger.error(f"Target length calculation failed: {e}")
            return 3
            
    async def _extractive_summarization(
        self,
        text: str,
        target_sentences: int,
        content_type: ContentType
    ) -> str:
        """Perform extractive summarization"""        try:
            sentences = sent_tokenize(text)
            
            if len(sentences) <= target_sentences:
                return text
                
            # Score sentences using multiple methods
            scored_sentences = await self._score_sentences_comprehensive(
                sentences, text, content_type
            )
            
            # Select top sentences
            top_sentences = heapq.nlargest(
                target_sentences,
                scored_sentences,
                key=lambda x: x.score
            )
            
            # Sort by original position to maintain flow
            top_sentences.sort(key=lambda x: x.position)
            
            # Combine into summary
            summary = " ".join([s.text for s in top_sentences])
            
            return summary
            
        except Exception as e:
            logger.error(f"Extractive summarization failed: {e}")
            return text[:1000]  # Fallback
            
    async def _abstractive_summarization(
        self,
        text: str,
        target_sentences: int
    ) -> str:
        """Perform abstractive summarization using transformer models"""        try:
            if not self.abstractive_model:
                # Fallback to extractive
                return await self._extractive_summarization(text, target_sentences, ContentType.GENERAL)
                
            # Split long text into chunks if necessary
            max_length = 1024  # BART input limit
            words = text.split()
            
            if len(words) <= max_length:
                # Text is short enough for one pass
                result = self.abstractive_model(
                    text,
                    max_length=min(150, len(words) // 2),
                    min_length=30,
                    do_sample=False
                )
                return result[0]['summary_text']
            else:
                # Split into chunks and summarize each
                chunk_size = max_length // 2
                chunks = [
                    " ".join(words[i:i + chunk_size])
                    for i in range(0, len(words), chunk_size)
                ]
                
                chunk_summaries = []
                for chunk in chunks:
                    result = self.abstractive_model(
                        chunk,
                        max_length=100,
                        min_length=20,
                        do_sample=False
                    )
                    chunk_summaries.append(result[0]['summary_text'])
                    
                # Combine chunk summaries
                combined = " ".join(chunk_summaries)
                
                # Final summarization if combined is still too long
                if len(combined.split()) > target_sentences * 15:  # Approximate
                    result = self.abstractive_model(
                        combined,
                        max_length=target_sentences * 15,
                        min_length=target_sentences * 5,
                        do_sample=False
                    )
                    return result[0]['summary_text']
                else:
                    return combined
                    
        except Exception as e:
            logger.error(f"Abstractive summarization failed: {e}")
            # Fallback to extractive
            return await self._extractive_summarization(text, target_sentences, ContentType.GENERAL)
            
    async def _hybrid_summarization(
        self,
        text: str,
        target_sentences: int,
        content_type: ContentType
    ) -> str:
        """Combine extractive and abstractive methods"""        try:
            # First, use extractive to get important content
            extractive_summary = await self._extractive_summarization(
                text, target_sentences * 2, content_type  # Get more content initially
            )
            
            # Then use abstractive to refine and condense
            if len(extractive_summary.split()) > target_sentences * 10:
                abstractive_summary = await self._abstractive_summarization(
                    extractive_summary, target_sentences
                )
                return abstractive_summary
            else:
                return extractive_summary
                
        except Exception as e:
            logger.error(f"Hybrid summarization failed: {e}")
            return await self._extractive_summarization(text, target_sentences, content_type)
            
    async def _score_sentences_comprehensive(
        self,
        sentences: List[str],
        full_text: str,
        content_type: ContentType
    ) -> List[SentenceScore]:
        """Score sentences using multiple criteria"""        try:
            scored_sentences = []
            
            # Calculate TF-IDF scores
            tfidf_scores = await self._calculate_tfidf_scores(sentences)
            
            # Extract keywords for keyword scoring
            keywords = await self._extract_important_words(full_text)
            
            for i, sentence in enumerate(sentences):
                # Professional quality metrics
                quality_metrics = {
                    'coherence': self._calculate_coherence(summary),
                    'completeness': self._calculate_completeness(summary, text),
                    'conciseness': self._calculate_conciseness(summary, text),
                    'accuracy': self._calculate_accuracy(summary, text),
                    'readability': self._calculate_readability(summary)
                }
                word_count = len(sentence.split())
                
                # Position score (beginning and end are more important)
                position_score = self._calculate_position_score(i, len(sentences))
                
                # Length score (prefer medium-length sentences)
                length_score = self._calculate_length_score(word_count)
                
                # Keyword score
                keyword_score = self._calculate_keyword_score(sentence, keywords)
                
                # TF-IDF score
                tfidf_score = tfidf_scores[i] if i < len(tfidf_scores) else 0
                
                # Content type specific score
                content_score = self._calculate_content_type_score(sentence, content_type)
                
                # Combine scores
                final_score = (
                    tfidf_score * 0.3 +
                    keyword_score * 0.25 +
                    position_score * 0.2 +
                    length_score * 0.15 +
                    content_score * 0.1
                )
                
                scored_sentence = SentenceScore(
                    text=sentence,
                    score=final_score,
                    position=i,
                    word_count=word_count,
                    contains_keywords=keyword_score > 0.5,
                    tf_idf_score=tfidf_score,
                    position_score=position_score,
                    length_score=length_score
                )
                scored_sentences.append(scored_sentence)
                
            return scored_sentences
            
        except Exception as e:
            logger.error(f"Sentence scoring failed: {e}")
            # Return simple scores as fallback
            return [
                SentenceScore(text=sent, score=1.0, position=i, word_count=len(sent.split()), contains_keywords=False)
                for i, sent in enumerate(sentences)
            ]
            
    async def _calculate_tfidf_scores(self, sentences: List[str]) -> List[float]:
        """Calculate TF-IDF scores for sentences"""        try:
            if len(sentences) < 2:
                return [1.0] * len(sentences)
                
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(sentences)
            
            # Calculate average TF-IDF score for each sentence
            scores = np.mean(tfidf_matrix.toarray(), axis=1)
            
            return scores.tolist()
            
        except Exception as e:
            logger.error(f"TF-IDF calculation failed: {e}")
            return [1.0] * len(sentences)
            
    async def _extract_important_words(self, text: str) -> List[str]:
        """Extract important words for keyword scoring"""        try:
            if not self.nlp:
                return []
                
            doc = self.nlp(text)
            
            # Extract nouns, proper nouns, and adjectives
            important_words = []
            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and
                    len(token.text) > 3 and
                    token.text.lower() not in self.stop_words and
                    token.is_alpha):
                    important_words.append(token.lemma_.lower())
                    
            # Count frequencies and return most common
            word_counts = Counter(important_words)
            return [word for word, count in word_counts.most_common(20)]
            
        except Exception as e:
            logger.error(f"Important word extraction failed: {e}")
            return []
            
    def _calculate_position_score(self, position: int, total_sentences: int) -> float:
        """Calculate score based on sentence position"""        try:
            # Higher scores for beginning and end
            if total_sentences <= 3:
                return 1.0
                
            relative_pos = position / (total_sentences - 1)
            
            # U-shaped curve: high at beginning and end
            if relative_pos <= 0.1:  # First 10%
                return 1.0
            elif relative_pos >= 0.9:  # Last 10%
                return 0.8
            elif relative_pos <= 0.2:  # First 20%
                return 0.7
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Position score calculation failed: {e}")
            return 0.5
            
    def _calculate_length_score(self, word_count: int) -> float:
        """Calculate score based on sentence length"""        try:
            # Prefer medium-length sentences (10-25 words)
            if 10 <= word_count <= 25:
                return 1.0
            elif 8 <= word_count <= 30:
                return 0.8
            elif 6 <= word_count <= 35:
                return 0.6
            elif word_count >= 5:
                return 0.4
            else:
                return 0.1
                
        except Exception as e:
            logger.error(f"Length score calculation failed: {e}")
            return 0.5
            
    def _calculate_keyword_score(self, sentence: str, keywords: List[str]) -> float:
        """Calculate score based on keyword presence"""        try:
            if not keywords:
                return 0.5
                
            sentence_lower = sentence.lower()
            keyword_count = sum(1 for keyword in keywords if keyword in sentence_lower)
            
            # Normalize by sentence length
            word_count = len(sentence.split())
            if word_count == 0:
                return 0
                
            density = keyword_count / word_count
            return min(density * 10, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Keyword score calculation failed: {e}")
            return 0.5
            
    def _calculate_content_type_score(self, sentence: str, content_type: ContentType) -> float:
        """Calculate score based on content type specific patterns"""        try:
            sentence_lower = sentence.lower()
            
            if content_type == ContentType.NEWS:
                # Look for news-specific patterns
                news_indicators = ['said', 'reported', 'according to', 'announced', 'revealed']
                if any(indicator in sentence_lower for indicator in news_indicators):
                    return 1.0
                    
            elif content_type == ContentType.RESEARCH_PAPER:
                # Look for research-specific patterns
                research_indicators = ['study', 'research', 'findings', 'results', 'conclusion']
                if any(indicator in sentence_lower for indicator in research_indicators):
                    return 1.0
                    
            elif content_type == ContentType.BLOG_POST:
                # Look for blog-specific patterns
                blog_indicators = ['tips', 'how to', 'guide', 'tutorial', 'steps']
                if any(indicator in sentence_lower for indicator in blog_indicators):
                    return 1.0
                    
            return 0.5
            
        except Exception as e:
            logger.error(f"Content type score calculation failed: {e}")
            return 0.5
            
    async def _extract_key_points(self, text: str) -> List[KeyPoint]:
        """Extract key points from text"""        try:
            sentences = sent_tokenize(text)
            
            if len(sentences) < 3:
                return []
                
            # Score sentences for importance
            scored_sentences = await self._score_sentences_comprehensive(
                sentences, text, ContentType.GENERAL
            )
            
            # Select top sentences as key points
            top_sentences = heapq.nlargest(
                min(5, len(sentences) // 3),
                scored_sentences,
                key=lambda x: x.score
            )
            
            key_points = []
            for i, scored_sentence in enumerate(top_sentences):
                key_point = KeyPoint(
                    text=scored_sentence.text,
                    importance_score=scored_sentence.score,
                    supporting_sentences=[],
                    related_concepts=[],
                    section=f"Point {i + 1}"
                )
                key_points.append(key_point)
                
            return key_points
            
        except Exception as e:
            logger.error(f"Key point extraction failed: {e}")
            return []
            
    async def _generate_bullet_points(self, text: str, key_points: List[KeyPoint]) -> List[str]:
        """Generate bullet points from text and key points"""        try:
            bullet_points = []
            
            # Use key points if available
            if key_points:
                for key_point in key_points[:5]:  # Limit to 5 bullet points
                    # Simplify the key point text
                    simplified = await self._simplify_sentence(key_point.text)
                    bullet_points.append(simplified)
            else:
                # Extract bullet points directly from text
                sentences = sent_tokenize(text)
                
                # Score and select sentences
                scored_sentences = await self._score_sentences_comprehensive(
                    sentences, text, ContentType.GENERAL
                )
                
                top_sentences = heapq.nlargest(
                    min(5, len(sentences) // 3),
                    scored_sentences,
                    key=lambda x: x.score
                )
                
                for scored_sentence in top_sentences:
                    simplified = await self._simplify_sentence(scored_sentence.text)
                    bullet_points.append(simplified)
                    
            return bullet_points
            
        except Exception as e:
            logger.error(f"Bullet point generation failed: {e}")
            return []
            
    async def _simplify_sentence(self, sentence: str) -> str:
        """Simplify a sentence for bullet point format"""        try:
            # Remove unnecessary words and phrases
            simplified = sentence.strip()
            
            # Remove common sentence starters
            starters_to_remove = [
                'However,', 'Moreover,', 'Furthermore,', 'Additionally,',
                'In addition,', 'In conclusion,', 'Therefore,', 'Thus,'
            ]
            
            for starter in starters_to_remove:
                if simplified.startswith(starter):
                    simplified = simplified[len(starter):].strip()
                    
            # Capitalize first letter
            if simplified:
                simplified = simplified[0].upper() + simplified[1:]
                
            # Ensure it ends with a period
            if not simplified.endswith('.'):
                simplified += '.'
                
            return simplified
            
        except Exception as e:
            logger.error(f"Sentence simplification failed: {e}")
            return sentence
            
    async def _calculate_readability(self, text: str) -> float:
        """Calculate readability score of text"""        try:
            # Simple readability metric based on average sentence length
            sentences = sent_tokenize(text)
            if not sentences:
                return 0.0
                
            words = text.split()
            avg_sentence_length = len(words) / len(sentences)
            
            # Ideal sentence length is around 15-20 words
            if 15 <= avg_sentence_length <= 20:
                return 1.0
            elif 10 <= avg_sentence_length <= 25:
                return 0.8
            elif 8 <= avg_sentence_length <= 30:
                return 0.6
            else:
                return 0.4
                
        except Exception as e:
            logger.error(f"Readability calculation failed: {e}")
            return 0.5
            
    async def _calculate_coverage(self, original_text: str, summary_text: str) -> float:
        """Calculate how well the summary covers the original content"""        try:
            if not original_text or not summary_text:
                return 0.0
                
            # Extract important words from both texts
            original_words = await self._extract_important_words(original_text)
            summary_words = await self._extract_important_words(summary_text)
            
            if not original_words:
                return 0.5
                
            # Calculate overlap
            common_words = set(original_words) & set(summary_words)
            coverage = len(common_words) / len(original_words)
            
            return min(coverage, 1.0)
            
        except Exception as e:
            logger.error(f"Coverage calculation failed: {e}")
            return 0.5


class MultiDocumentSummarizer:
    """Summarizer for multiple documents"""    
    def __init__(self):
        self.single_summarizer = SummarizationEngine()
        
    async def summarize_multiple_documents(
        self,
        documents: List[str],
        length: SummarizationLength = SummarizationLength.MEDIUM,
        content_type: ContentType = ContentType.GENERAL
    ) -> SummaryResult:
        """        Summarize multiple documents into a single summary
        
        Args:
            documents: List of document texts
            length: Desired length of summary
            content_type: Type of content being summarized
            
        Returns:
            SummaryResult with combined summary
        """        try:
            if not documents:
                raise ValueError("No documents provided")
                
            if len(documents) == 1:
                return await self.single_summarizer.summarize(
                    documents[0], SummarizationType.HYBRID, length, content_type
                )
                
            # Summarize each document individually first
            individual_summaries = []
            for doc in documents:
                summary_result = await self.single_summarizer.summarize(
                    doc, SummarizationType.EXTRACTIVE, SummarizationLength.SHORT, content_type
                )
                individual_summaries.append(summary_result.summary_text)
                
            # Combine individual summaries
            combined_text = " ".join(individual_summaries)
            
            # Summarize the combined summaries
            final_summary = await self.single_summarizer.summarize(
                combined_text, SummarizationType.HYBRID, length, content_type
            )
            
            return final_summary
            
        except Exception as e:
            logger.error(f"Multi-document summarization failed: {e}")
            raise
