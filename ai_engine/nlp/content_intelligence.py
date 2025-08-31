"""Content Intelligence Engine for IA Influencer Agent Platform

Intelligent content analysis, understanding, and optimization for multi-format creator content.
Handles textual analysis for music, video, blog, photography, and influencer content.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import re
import numpy as np
import spacy
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from collections import defaultdict, Counter
import hashlib
import json

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content type enumeration for specialized processing."""
    MUSIC_LYRICS = "music_lyrics"
    VIDEO_SCRIPT = "video_script"
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    PHOTOGRAPHY_CAPTION = "photography_caption"
    PODCAST_TRANSCRIPT = "podcast_transcript"
    COMEDY_SCRIPT = "comedy_script"
    INFLUENCER_POST = "influencer_post"


class ContentCategory(Enum):
    """Content category classification."""
    ENTERTAINMENT = "entertainment"
    EDUCATIONAL = "educational"
    PROMOTIONAL = "promotional"
    PERSONAL = "personal"
    COMMERCIAL = "commercial"
    ARTISTIC = "artistic"
    TECHNICAL = "technical"


@dataclass
class ContentMetrics:
    """Content quality and engagement metrics."""
    readability_score: float
    engagement_potential: float
    viral_probability: float
    monetization_score: float
    seo_strength: float
    brand_alignment: float
    authenticity_score: float
    creativity_index: float
    technical_quality: float
    market_relevance: float


@dataclass
class ContentInsight:
    """Deep content analysis insights."""
    content_id: str
    content_type: ContentType
    category: ContentCategory
    metrics: ContentMetrics
    keywords: List[str]
    hashtags: List[str]
    entities: List[Dict[str, Any]]
    topics: List[str]
    sentiment_profile: Dict[str, float]
    language_patterns: Dict[str, Any]
    optimization_suggestions: List[str]
    collaboration_matches: List[str]
    monetization_opportunities: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class ContentIntelligenceEngine:
    """
    Advanced content intelligence engine for creator content analysis.
    
    Provides comprehensive analysis of textual content across multiple formats,
    extracting insights for optimization, monetization, and collaboration.
    """
    
    def __init__(self):
        """Initialize the content intelligence engine."""
        self.nlp = None
        self.sentiment_analyzer = None
        self.tokenizer = None
        self.model = None
        self._load_models()
        
        # Content patterns for different creator types
        self.creator_patterns = {
            ContentType.MUSIC_LYRICS: {
                'patterns': [r'\b(verse|chorus|bridge|hook)\b', r'\b(rhyme|beat|melody)\b'],
                'keywords': ['rhythm', 'melody', 'harmony', 'beat', 'tune', 'song']
            },
            ContentType.VIDEO_SCRIPT: {
                'patterns': [r'\b(scene|cut|fade|action)\b', r'\b(camera|shot|frame)\b'],
                'keywords': ['visual', 'scene', 'dialogue', 'script', 'video', 'film']
            },
            ContentType.BLOG_POST: {
                'patterns': [r'\b(introduction|conclusion|paragraph)\b', r'\b(SEO|keywords|meta)\b'],
                'keywords': ['article', 'blog', 'content', 'writing', 'post', 'author']
            },
            ContentType.SOCIAL_MEDIA: {
                'patterns': [r'#\w+', r'@\w+', r'\b(trending|viral|share)\b'],
                'keywords': ['hashtag', 'viral', 'engagement', 'followers', 'likes', 'share']
            },
            ContentType.PHOTOGRAPHY_CAPTION: {
                'patterns': [r'\b(shot|photo|capture|lens)\b', r'\b(lighting|composition)\b'],
                'keywords': ['photography', 'photo', 'image', 'visual', 'artistic', 'creative']
            }
        }
    
    def _load_models(self):
        """Load NLP models and tools."""
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            
            # Load sentiment analysis pipeline
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            
            # Load transformer model for embeddings
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            
            logger.info("Content intelligence models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load NLP models: {e}")
            raise
    
    async def analyze_content(
        self, 
        content: str, 
        content_type: ContentType,
        creator_profile: Optional[Dict[str, Any]] = None
    ) -> ContentInsight:
        """
        Perform comprehensive content analysis.
        
        Args:
            content: Text content to analyze
            content_type: Type of content being analyzed
            creator_profile: Optional creator profile for personalization
            
        Returns:
            ContentInsight: Comprehensive analysis results
        """
        try:
            # Generate content ID
            content_id = hashlib.md5(content.encode()).hexdigest()[:12]
            
            # Parallel analysis tasks
            tasks = [
                self._analyze_metrics(content, content_type),
                self._extract_keywords(content, content_type),
                self._extract_entities(content),
                self._analyze_sentiment(content),
                self._detect_topics(content),
                self._analyze_language_patterns(content),
                self._generate_optimization_suggestions(content, content_type),
                self._find_collaboration_matches(content, creator_profile),
                self._identify_monetization_opportunities(content, content_type)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Extract hashtags
            hashtags = self._extract_hashtags(content)
            
            # Determine category
            category = self._classify_category(content, content_type)
            
            return ContentInsight(
                content_id=content_id,
                content_type=content_type,
                category=category,
                metrics=results[0],
                keywords=results[1],
                hashtags=hashtags,
                entities=results[2],
                topics=results[4],
                sentiment_profile=results[3],
                language_patterns=results[5],
                optimization_suggestions=results[6],
                collaboration_matches=results[7],
                monetization_opportunities=results[8]
            )
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            raise
    
    async def _analyze_metrics(self, content: str, content_type: ContentType) -> ContentMetrics:
        """Analyze content quality and engagement metrics."""
        try:
            # Readability analysis
            readability = self._calculate_readability(content)
            
            # Engagement potential based on content patterns
            engagement = self._calculate_engagement_potential(content, content_type)
            
            # Viral probability analysis
            viral_prob = self._calculate_viral_probability(content, content_type)
            
            # Monetization score
            monetization = self._calculate_monetization_score(content, content_type)
            
            # SEO strength
            seo_strength = self._calculate_seo_strength(content)
            
            # Brand alignment (requires brand profile)
            brand_alignment = 0.75  # Placeholder - would use brand profile
            
            # Authenticity score
            authenticity = self._calculate_authenticity_score(content)
            
            # Creativity index
            creativity = self._calculate_creativity_index(content, content_type)
            
            # Technical quality
            technical_quality = self._assess_technical_quality(content)
            
            # Market relevance
            market_relevance = self._assess_market_relevance(content, content_type)
            
            return ContentMetrics(
                readability_score=readability,
                engagement_potential=engagement,
                viral_probability=viral_prob,
                monetization_score=monetization,
                seo_strength=seo_strength,
                brand_alignment=brand_alignment,
                authenticity_score=authenticity,
                creativity_index=creativity,
                technical_quality=technical_quality,
                market_relevance=market_relevance
            )
            
        except Exception as e:
            logger.error(f"Metrics analysis failed: {e}")
            raise
    
    def _calculate_readability(self, content: str) -> float:
        """Calculate content readability score."""
        try:
            # Simplified readability calculation
            sentences = len(re.findall(r'[.!?]+', content))
            words = len(content.split())
            
            if sentences == 0:
                return 0.0
            
            avg_sentence_length = words / sentences
            
            # Flesch Reading Ease approximation
            score = 206.835 - (1.015 * avg_sentence_length)
            return min(max(score / 100, 0.0), 1.0)
            
        except Exception:
            return 0.5
    
    def _calculate_engagement_potential(self, content: str, content_type: ContentType) -> float:
        """Calculate potential for audience engagement."""
        try:
            engagement_indicators = [
                r'\b(amazing|incredible|wow|awesome)\b',
                r'\b(question|what|how|why)\b',
                r'[!]{1,3}',
                r'\b(you|your|yours)\b',
                r'\b(share|comment|like|follow)\b'
            ]
            
            score = 0.0
            content_lower = content.lower()
            
            for pattern in engagement_indicators:
                matches = len(re.findall(pattern, content_lower))
                score += min(matches * 0.1, 0.2)
            
            # Content type specific bonuses
            type_bonus = {
                ContentType.SOCIAL_MEDIA: 0.2,
                ContentType.INFLUENCER_POST: 0.15,
                ContentType.VIDEO_SCRIPT: 0.1,
                ContentType.BLOG_POST: 0.05
            }.get(content_type, 0.0)
            
            return min(score + type_bonus, 1.0)
            
        except Exception:
            return 0.5
    
    def _calculate_viral_probability(self, content: str, content_type: ContentType) -> float:
        """Calculate probability of content going viral."""
        try:
            viral_indicators = [
                r'\b(trending|viral|breaking|exclusive)\b',
                r'\b(shocking|unbelievable|must-see)\b',
                r'\b(first|never|only|unique)\b',
                r'[!]{2,}',
                r'#\w+',
                r'\b(challenge|reaction|versus)\b'
            ]
            
            score = 0.0
            content_lower = content.lower()
            
            for pattern in viral_indicators:
                matches = len(re.findall(pattern, content_lower))
                score += min(matches * 0.15, 0.25)
            
            # Length penalty for very long content
            if len(content) > 2000:
                score *= 0.8
            elif len(content) < 50:
                score *= 0.6
            
            return min(score, 1.0)
            
        except Exception:
            return 0.3
    
    def _calculate_monetization_score(self, content: str, content_type: ContentType) -> float:
        """Calculate monetization potential."""
        try:
            monetization_indicators = [
                r'\b(buy|purchase|sale|discount|offer)\b',
                r'\b(product|service|brand|sponsor)\b',
                r'\b(link|website|shop|store)\b',
                r'\b(premium|exclusive|limited)\b',
                r'\b(collaboration|partnership|deal)\b'
            ]
            
            score = 0.0
            content_lower = content.lower()
            
            for pattern in monetization_indicators:
                matches = len(re.findall(pattern, content_lower))
                score += min(matches * 0.1, 0.2)
            
            # Content type bonuses
            type_multiplier = {
                ContentType.INFLUENCER_POST: 1.3,
                ContentType.BLOG_POST: 1.2,
                ContentType.VIDEO_SCRIPT: 1.1,
                ContentType.SOCIAL_MEDIA: 1.0
            }.get(content_type, 0.8)
            
            return min(score * type_multiplier, 1.0)
            
        except Exception:
            return 0.4
    
    def _calculate_seo_strength(self, content: str) -> float:
        """Calculate SEO optimization strength."""
        try:
            seo_factors = {
                'title_keywords': len(re.findall(r'\b[A-Z][a-z]+\b', content[:100])) * 0.1,
                'keyword_density': min(len(set(content.lower().split())) / len(content.split()) * 2, 0.3),
                'content_length': min(len(content) / 2000, 0.2),
                'headers': len(re.findall(r'#{1,6}\s', content)) * 0.1,
                'links': len(re.findall(r'http[s]?://|www\.', content)) * 0.05
            }
            
            return min(sum(seo_factors.values()), 1.0)
            
        except Exception:
            return 0.5
    
    def _calculate_authenticity_score(self, content: str) -> float:
        """Calculate content authenticity and originality."""
        try:
            authenticity_indicators = [
                r'\b(I|my|me|personal|experience)\b',
                r'\b(honest|genuine|real|truth)\b',
                r'\b(story|journey|behind)\b',
                r'\b(learned|discovered|realized)\b'
            ]
            
            score = 0.0
            content_lower = content.lower()
            
            for pattern in authenticity_indicators:
                matches = len(re.findall(pattern, content_lower))
                score += min(matches * 0.1, 0.2)
            
            # Penalize overly promotional content
            promotional_terms = len(re.findall(r'\b(buy|purchase|sale|discount)\b', content_lower))
            if promotional_terms > 3:
                score *= 0.7
            
            return min(max(score, 0.3), 1.0)
            
        except Exception:
            return 0.6
    
    def _calculate_creativity_index(self, content: str, content_type: ContentType) -> float:
        """Calculate creativity and uniqueness index."""
        try:
            creativity_indicators = [
                r'\b(creative|unique|original|innovative)\b',
                r'\b(imagine|visualize|picture|dream)\b',
                r'\b(artistic|beautiful|stunning|masterpiece)\b',
                r'[!?]{2,}',
                r'\b(metaphor|like|as if|reminds me)\b'
            ]
            
            score = 0.0
            content_lower = content.lower()
            
            for pattern in creativity_indicators:
                matches = len(re.findall(pattern, content_lower))
                score += min(matches * 0.12, 0.2)
            
            # Vocabulary diversity
            unique_words = len(set(content.lower().split()))
            total_words = len(content.split())
            if total_words > 0:
                diversity = unique_words / total_words
                score += diversity * 0.3
            
            return min(score, 1.0)
            
        except Exception:
            return 0.5
    
    def _assess_technical_quality(self, content: str) -> float:
        """Assess technical quality of content."""
        try:
            # Grammar and spelling approximation
            sentences = re.split(r'[.!?]+', content)
            well_formed_sentences = sum(1 for s in sentences if len(s.strip()) > 10 and s.strip()[0].isupper())
            
            if len(sentences) == 0:
                return 0.5
            
            grammar_score = well_formed_sentences / len(sentences)
            
            # Punctuation consistency
            punctuation_score = min(len(re.findall(r'[.!?]', content)) / max(len(sentences), 1), 1.0)
            
            # Capitalization
            cap_score = min(len(re.findall(r'\b[A-Z][a-z]+', content)) / max(len(content.split()), 1) * 5, 1.0)
            
            return (grammar_score + punctuation_score + cap_score) / 3
            
        except Exception:
            return 0.7
    
    def _assess_market_relevance(self, content: str, content_type: ContentType) -> float:
        """Assess market relevance and timeliness."""
        try:
            trending_terms = [
                r'\b(2025|latest|new|current|today)\b',
                r'\b(trending|popular|viral|hot)\b',
                r'\b(AI|technology|digital|online)\b',
                r'\b(sustainable|eco|green|climate)\b',
                r'\b(community|social|connection)\b'
            ]
            
            score = 0.0
            content_lower = content.lower()
            
            for pattern in trending_terms:
                matches = len(re.findall(pattern, content_lower))
                score += min(matches * 0.15, 0.25)
            
            return min(score, 1.0)
            
        except Exception:
            return 0.6
    
    async def _extract_keywords(self, content: str, content_type: ContentType) -> List[str]:
        """Extract relevant keywords from content."""
        try:
            # Process with spaCy
            doc = self.nlp(content)
            
            # Extract noun phrases and important terms
            keywords = []
            
            # Named entities
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "ORG", "PRODUCT", "EVENT", "WORK_OF_ART"]:
                    keywords.append(ent.text.lower())
            
            # Noun phrases
            for chunk in doc.noun_chunks:
                if len(chunk.text) > 3 and len(chunk.text.split()) <= 3:
                    keywords.append(chunk.text.lower())
            
            # Content-specific patterns
            if content_type in self.creator_patterns:
                for keyword in self.creator_patterns[content_type]['keywords']:
                    if keyword.lower() in content.lower():
                        keywords.append(keyword.lower())
            
            # Remove duplicates and return top keywords
            return list(set(keywords))[:20]
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content."""
        try:
            hashtag_pattern = r'#(\w+)'
            hashtags = re.findall(hashtag_pattern, content)
            return list(set(hashtags))
            
        except Exception:
            return []
    
    async def _extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract named entities from content."""
        try:
            doc = self.nlp(content)
            entities = []
            
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': 1.0  # spaCy doesn't provide confidence scores
                })
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []
    
    async def _analyze_sentiment(self, content: str) -> Dict[str, float]:
        """Analyze sentiment profile of content."""
        try:
            # Use transformer-based sentiment analysis
            results = self.sentiment_analyzer(content)
            
            sentiment_profile = {
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 0.0
            }
            
            for result in results if isinstance(results, list) else [results]:
                label = result['label'].lower()
                score = result['score']
                
                if 'pos' in label:
                    sentiment_profile['positive'] = score
                elif 'neg' in label:
                    sentiment_profile['negative'] = score
                else:
                    sentiment_profile['neutral'] = score
            
            # Normalize scores
            total = sum(sentiment_profile.values())
            if total > 0:
                sentiment_profile = {k: v/total for k, v in sentiment_profile.items()}
            
            return sentiment_profile
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
    
    async def _detect_topics(self, content: str) -> List[str]:
        """Detect main topics in content."""
        try:
            doc = self.nlp(content)
            
            # Extract topics based on noun phrases and entities
            topics = set()
            
            # From entities
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "ORG", "EVENT", "WORK_OF_ART", "PRODUCT"]:
                    topics.add(ent.label_.lower())
            
            # From noun phrases (simplified topic extraction)
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) <= 2:
                    topics.add(chunk.root.text.lower())
            
            return list(topics)[:10]
            
        except Exception as e:
            logger.error(f"Topic detection failed: {e}")
            return []
    
    async def _analyze_language_patterns(self, content: str) -> Dict[str, Any]:
        """Analyze language patterns and style."""
        try:
            doc = self.nlp(content)
            
            patterns = {
                'sentence_count': len(list(doc.sents)),
                'avg_sentence_length': np.mean([len(sent.text.split()) for sent in doc.sents]),
                'question_count': len(re.findall(r'\?', content)),
                'exclamation_count': len(re.findall(r'!', content)),
                'uppercase_ratio': len(re.findall(r'[A-Z]', content)) / len(content) if content else 0,
                'punctuation_density': len(re.findall(r'[.,!?;:]', content)) / len(content) if content else 0,
                'word_count': len(content.split()),
                'unique_word_ratio': len(set(content.lower().split())) / len(content.split()) if content.split() else 0,
                'readability_level': self._get_readability_level(content)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Language pattern analysis failed: {e}")
            return {}
    
    def _get_readability_level(self, content: str) -> str:
        """Determine readability level."""
        try:
            readability = self._calculate_readability(content)
            
            if readability >= 0.8:
                return "very_easy"
            elif readability >= 0.7:
                return "easy"
            elif readability >= 0.6:
                return "fairly_easy"
            elif readability >= 0.5:
                return "standard"
            elif readability >= 0.3:
                return "fairly_difficult"
            else:
                return "difficult"
                
        except Exception:
            return "standard"
    
    async def _generate_optimization_suggestions(
        self, 
        content: str, 
        content_type: ContentType
    ) -> List[str]:
        """Generate content optimization suggestions."""
        try:
            suggestions = []
            content_lower = content.lower()
            
            # Length optimization
            word_count = len(content.split())
            if word_count < 50:
                suggestions.append("Consider expanding content for better engagement")
            elif word_count > 2000:
                suggestions.append("Consider breaking into smaller, digestible sections")
            
            # Engagement optimization
            if not re.search(r'[?!]', content):
                suggestions.append("Add questions or exclamations to increase engagement")
            
            if len(re.findall(r'\b(you|your)\b', content_lower)) < 3:
                suggestions.append("Use more direct address (you, your) to connect with audience")
            
            # SEO optimization
            if not re.search(r'#\w+', content):
                suggestions.append("Add relevant hashtags for discoverability")
            
            # Content-specific suggestions
            if content_type == ContentType.SOCIAL_MEDIA:
                if len(content) > 280:
                    suggestions.append("Consider shorter format for social media")
                if not re.search(r'@\w+', content):
                    suggestions.append("Consider mentioning relevant accounts")
            
            elif content_type == ContentType.BLOG_POST:
                if not re.search(r'#{1,6}\s', content):
                    suggestions.append("Add headers to improve structure and SEO")
            
            elif content_type == ContentType.MUSIC_LYRICS:
                if not any(pattern in content_lower for pattern in ['verse', 'chorus', 'bridge']):
                    suggestions.append("Consider adding song structure markers")
            
            return suggestions[:10]
            
        except Exception as e:
            logger.error(f"Optimization suggestion generation failed: {e}")
            return []
    
    async def _find_collaboration_matches(
        self, 
        content: str, 
        creator_profile: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Find potential collaboration matches."""
        try:
            matches = []
            content_lower = content.lower()
            
            # Genre/niche detection for matching
            niches = {
                'music': ['music', 'song', 'beat', 'melody', 'artist', 'band'],
                'fitness': ['workout', 'fitness', 'gym', 'health', 'exercise'],
                'cooking': ['recipe', 'food', 'cooking', 'chef', 'kitchen'],
                'tech': ['technology', 'software', 'coding', 'digital', 'AI'],
                'fashion': ['fashion', 'style', 'outfit', 'clothing', 'trend'],
                'travel': ['travel', 'destination', 'trip', 'adventure', 'explore'],
                'gaming': ['game', 'gaming', 'player', 'stream', 'esports']
            }
            
            detected_niches = []
            for niche, keywords in niches.items():
                if any(keyword in content_lower for keyword in keywords):
                    detected_niches.append(niche)
            
            # Generate collaboration suggestions
            for niche in detected_niches:
                matches.extend([
                    f"{niche}_creators",
                    f"{niche}_influencers",
                    f"{niche}_brands"
                ])
            
            return matches[:5]
            
        except Exception as e:
            logger.error(f"Collaboration matching failed: {e}")
            return []
    
    async def _identify_monetization_opportunities(
        self, 
        content: str, 
        content_type: ContentType
    ) -> List[str]:
        """Identify monetization opportunities."""
        try:
            opportunities = []
            content_lower = content.lower()
            
            # Product placement opportunities
            if any(term in content_lower for term in ['product', 'brand', 'service', 'tool']):
                opportunities.append("affiliate_marketing")
                opportunities.append("sponsored_content")
            
            # Educational content
            if any(term in content_lower for term in ['learn', 'tutorial', 'guide', 'how to']):
                opportunities.append("course_creation")
                opportunities.append("consulting_services")
            
            # Entertainment content
            if any(term in content_lower for term in ['funny', 'entertainment', 'show', 'performance']):
                opportunities.append("live_streaming")
                opportunities.append("merchandise")
            
            # Content-specific opportunities
            if content_type == ContentType.MUSIC_LYRICS:
                opportunities.extend(["music_licensing", "streaming_royalties", "live_performances"])
            elif content_type == ContentType.BLOG_POST:
                opportunities.extend(["ad_revenue", "premium_subscriptions", "email_marketing"])
            elif content_type == ContentType.VIDEO_SCRIPT:
                opportunities.extend(["youtube_monetization", "brand_partnerships", "product_placements"])
            
            return opportunities[:8]
            
        except Exception as e:
            logger.error(f"Monetization opportunity identification failed: {e}")
            return []
    
    def _classify_category(self, content: str, content_type: ContentType) -> ContentCategory:
        """Classify content into categories."""
        try:
            content_lower = content.lower()
            
            # Educational indicators
            if any(term in content_lower for term in ['learn', 'tutorial', 'guide', 'how', 'explain', 'teach']):
                return ContentCategory.EDUCATIONAL
            
            # Commercial indicators
            if any(term in content_lower for term in ['buy', 'sale', 'discount', 'offer', 'product', 'service']):
                return ContentCategory.COMMERCIAL
            
            # Promotional indicators
            if any(term in content_lower for term in ['brand', 'sponsor', 'partnership', 'collaboration']):
                return ContentCategory.PROMOTIONAL
            
            # Personal indicators
            if any(term in content_lower for term in ['my', 'personal', 'story', 'experience', 'journey']):
                return ContentCategory.PERSONAL
            
            # Artistic indicators
            if any(term in content_lower for term in ['creative', 'art', 'beautiful', 'artistic', 'masterpiece']):
                return ContentCategory.ARTISTIC
            
            # Default to entertainment
            return ContentCategory.ENTERTAINMENT
            
        except Exception:
            return ContentCategory.ENTERTAINMENT


class ContentBatchProcessor:
    """Batch processor for multiple content pieces."""
    
    def __init__(self, engine: ContentIntelligenceEngine):
        """Initialize batch processor."""
        self.engine = engine
        self.batch_size = 10
    
    async def process_batch(
        self, 
        content_batch: List[Dict[str, Any]]
    ) -> List[ContentInsight]:
        """Process multiple content pieces in batches."""
        try:
            results = []
            
            for i in range(0, len(content_batch), self.batch_size):
                batch = content_batch[i:i + self.batch_size]
                
                # Process batch in parallel
                tasks = [
                    self.engine.analyze_content(
                        item['content'],
                        ContentType(item['content_type']),
                        item.get('creator_profile')
                    )
                    for item in batch
                ]
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filter out exceptions and add successful results
                for result in batch_results:
                    if isinstance(result, ContentInsight):
                        results.append(result)
                    else:
                        logger.error(f"Batch processing error: {result}")
            
            return results
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise


# Export classes
__all__ = [
    'ContentType',
    'ContentCategory', 
    'ContentMetrics',
    'ContentInsight',
    'ContentIntelligenceEngine',
    'ContentBatchProcessor'
]
