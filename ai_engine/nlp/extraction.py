"""Advanced Extraction Module for IA Influencer Agent Platform

Intelligent information extraction system for parsing and structuring
content from various sources and formats.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re
import json
from abc import ABC, abstractmethod
import numpy as np
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

@dataclass
class ExtractedEntity:
    """
Extracted entity structure"""
    text: str
    entity_type: str
    confidence: float
    start_position: int
    end_position: int
    context: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContactInfo:
    """Contact information structure"""
    emails: List[str] = field(default_factory=list)
    phone_numbers: List[str] = field(default_factory=list)
    social_handles: Dict[str, List[str]] = field(default_factory=dict)
    websites: List[str] = field(default_factory=list)
    addresses: List[str] = field(default_factory=list)

@dataclass
class ContentMetrics:
    """
Content metrics structure"""
    engagement_indicators: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    trend_indicators: List[str] = field(default_factory=list)
    viral_signals: List[str] = field(default_factory=list)
    brand_mentions: List[str] = field(default_factory=list)

@dataclass
class KeywordExtraction:
    """
Keyword extraction results"""
    primary_keywords: List[str]
    secondary_keywords: List[str]
    hashtags: List[str]
    mentions: List[str]
    trending_terms: List[str]
    keyword_density: Dict[str, float]
    semantic_keywords: List[str]

@dataclass
class StructuredData:
    """
Structured data extraction"""
    titles: List[str]
    headings: List[str]
    bullet_points: List[str]
    numbered_lists: List[str]
    quotes: List[str]
    code_blocks: List[str]
    links: List[Dict[str, str]]
    images: List[Dict[str, str]]

@dataclass
class ExtractionResult:
    """
Complete extraction result"""
    request_id: str
    original_text: str
    entities: List[ExtractedEntity]
    contact_info: ContactInfo
    content_metrics: ContentMetrics
    keywords: KeywordExtraction
    structured_data: StructuredData
    topics: List[str]
    sentiments: Dict[str, float]
    key_phrases: List[str]
    summary: str
    metadata: Dict[str, Any]
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

class AdvancedContentExtractor:
    """
    Advanced content extraction system
    
    Features:
    - Named Entity Recognition (NER)
    - Contact information extraction
    - Content metrics extraction
    - Keyword and hashtag extraction
    - Structured data parsing
    - Topic extraction
    - Sentiment extraction
    - Key phrase identification
    - Content summarization
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.entity_patterns = self._load_entity_patterns()
        self.keyword_extractors = self._initialize_keyword_extractors()
        self.topic_extractors = self._initialize_topic_extractors()
        self.summarizers = self._initialize_summarizers()
        self.contact_patterns = self._load_contact_patterns()
        self.metrics_patterns = self._load_metrics_patterns()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """
Get default configuration"""
        return {
            'enable_entity_extraction': True,
            'enable_contact_extraction': True,
            'enable_keyword_extraction': True,
            'enable_topic_extraction': True,
            'enable_sentiment_extraction': True,
            'enable_summarization': True,
            'confidence_threshold': 0.7,
            'max_keywords': 20,
            'max_entities': 50,
            'detailed_analysis': True,
            'preserve_context': True
        }
    
    def _load_entity_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
Load entity recognition patterns"""
        return {
            'person': {
                'patterns': [
                    r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last
                    r'\b@[A-Za-z0-9_]+',  # Social media mentions
                    r'\bCEO\s+[A-Z][a-z]+ [A-Z][a-z]+',
                    r'\bfounder\s+[A-Z][a-z]+ [A-Z][a-z]+'
                ],
                'context_keywords': ['said', 'founder', 'CEO', 'creator', 'influencer', 'by']
            },
            'organization': {
                'patterns': [
                    r'\b[A-Z][a-zA-Z0-9&\s]+ (Inc|LLC|Corp|Company|Ltd)\b',
                    r'\b[A-Z][a-zA-Z0-9&\s]+ (Corporation|Limited|Group)\b',
                    r'\b(Apple|Google|Microsoft|Amazon|Meta|Tesla|Netflix)\b'
                ],
                'context_keywords': ['company', 'corporation', 'brand', 'business', 'startup']
            },
            'location': {
                'patterns': [
                    r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b',  # City, State
                    r'\b(New York|Los Angeles|Chicago|Houston|Phoenix|Philadelphia|San Antonio|San Diego|Dallas|San Jose)\b',
                    r'\b(USA|United States|UK|United Kingdom|Canada|Australia|Germany|France|Japan)\b'
                ],
                'context_keywords': ['in', 'at', 'from', 'located', 'based']
            },
            'product': {
                'patterns': [
                    r'\biPhone\s+\d+\b',
                    r'\bMacBook\s+(Pro|Air)\b',
                    r'\bApple\s+Watch\b',
                    r'\bAirPods\s+(Pro|Max)?\b'
                ],
                'context_keywords': ['product', 'device', 'gadget', 'technology', 'review']
            },
            'brand': {
                'patterns': [
                    r'\b#[A-Za-z0-9_]+Brand\b',
                    r'\b@[A-Za-z0-9_]+(Official|Brand)\b',
                    r'\b(Nike|Adidas|Coca-Cola|McDonald\'s|Disney|Samsung|Sony)\b'
                ],
                'context_keywords': ['brand', 'sponsored', 'partnership', 'collaboration', 'ad']
            },
            'event': {
                'patterns': [
                    r'\b[A-Z][a-zA-Z\s]+ (Conference|Summit|Event|Festival|Awards)\b',
                    r'\b(CES|WWDC|Comic-Con|Coachella|Grammy|Oscar|Emmy)\b',
                    r'\bwebinar\s+[A-Z][a-zA-Z\s]+\b'
                ],
                'context_keywords': ['event', 'conference', 'summit', 'attending', 'speaking']
            },
            'money': {
                'patterns': [
                    r'\$[\d,]+(?:\.\d{2})?\b',
                    r'\b\d+(?:,\d{3})*\s+dollars?\b',
                    r'\b\d+k\b',  # 100k
                    r'\bmillion\s+dollars?\b'
                ],
                'context_keywords': ['cost', 'price', 'revenue', 'profit', 'investment', 'funding']
            },
            'date': {
                'patterns': [
                    r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
                    r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY
                    r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
                    r'\b(today|tomorrow|yesterday|next week|last week)\b'
                ],
                'context_keywords': ['on', 'date', 'when', 'schedule', 'launch', 'release']
            }
        }
    
    def _initialize_keyword_extractors(self) -> Dict[str, Any]:
        """
Initialize keyword extraction components"""
        return {
            'tfidf': 'tfidf_vectorizer',  # Would use actual TF-IDF
            'keybert': 'keybert_model',  # Would use KeyBERT
            'rake': 'rake_algorithm',  # Would use RAKE
            'yake': 'yake_algorithm',  # Would use YAKE
            'textrank': 'textrank_algorithm',  # Would use TextRank
            'lda_topics': 'lda_topic_model'  # Would use LDA
        }
    
    def _initialize_topic_extractors(self) -> Dict[str, Any]:
        """
Initialize topic extraction components"""
        return {
            'lda_model': 'latent_dirichlet_allocation',
            'bert_topic': 'bert_topic_model',
            'nmf_model': 'non_negative_matrix_factorization',
            'topic_keywords': self._build_topic_database()
        }
    
    def _build_topic_database(self) -> Dict[str, List[str]]:
        """
Build comprehensive topic database"""
        return {
            'technology': ['tech', 'software', 'ai', 'machine learning', 'coding', 'programming', 'developer'],
            'lifestyle': ['fashion', 'beauty', 'fitness', 'health', 'wellness', 'self-care', 'routine'],
            'business': ['entrepreneur', 'startup', 'marketing', 'sales', 'growth', 'strategy', 'leadership'],
            'entertainment': ['movie', 'music', 'gaming', 'celebrity', 'tv show', 'streaming', 'entertainment'],
            'education': ['learning', 'tutorial', 'course', 'skill', 'knowledge', 'study', 'education'],
            'travel': ['travel', 'vacation', 'destination', 'hotel', 'flight', 'adventure', 'explore'],
            'food': ['recipe', 'cooking', 'restaurant', 'food', 'cuisine', 'chef', 'meal'],
            'sports': ['sports', 'fitness', 'workout', 'exercise', 'athlete', 'competition', 'training'],
            'finance': ['money', 'investment', 'cryptocurrency', 'trading', 'finance', 'economics', 'market'],
            'science': ['research', 'study', 'discovery', 'experiment', 'innovation', 'science', 'technology']
        }
    
    def _initialize_summarizers(self) -> Dict[str, Any]:
        """
Initialize summarization components"""
        return {
            'extractive': 'extractive_summarizer',  # Would use actual extractive summarizer
            'abstractive': 'abstractive_summarizer',  # Would use T5/BART
            'keyword_based': 'keyword_summarizer',
            'sentence_ranking': 'sentence_ranker'
        }
    
    def _load_contact_patterns(self) -> Dict[str, List[str]]:
        """
Load contact information patterns"""
        return {
            'email': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            'phone': [
                r'\b\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
                r'\b\d{3}-\d{3}-\d{4}\b',
                r'\b\(\d{3}\)\s?\d{3}-\d{4}\b'
            ],
            'social_instagram': [
                r'@[A-Za-z0-9_\.]+',
                r'instagram\.com/[A-Za-z0-9_\.]+',
                r'ig:\s*@?[A-Za-z0-9_\.]+'
            ],
            'social_twitter': [
                r'twitter\.com/[A-Za-z0-9_]+',
                r'@[A-Za-z0-9_]+',
                r'tweet\s+@[A-Za-z0-9_]+'
            ],
            'social_tiktok': [
                r'tiktok\.com/@[A-Za-z0-9_\.]+',
                r'tiktok:\s*@?[A-Za-z0-9_\.]+'
            ],
            'social_youtube': [
                r'youtube\.com/[A-Za-z0-9_]+',
                r'youtu\.be/[A-Za-z0-9_]+'
            ],
            'website': [
                r'https?://(?:[-\w.])+(?:\.[a-zA-Z]{2,5})+(?:/[^\s]*)?',
                r'www\.[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',
                r'\b[A-Za-z0-9.-]+\.(com|org|net|edu|gov|io|co)\b'
            ]
        }
    
    def _load_metrics_patterns(self) -> Dict[str, List[str]]:
        """
Load content metrics patterns"""
        return {
            'engagement': [
                r'\b\d+(\.\d+)?[kKmM]?\s*(likes?|comments?|shares?|views?)\b',
                r'\b(viral|trending|popular|hit|success)\b',
                r'\b\d+(\.\d+)?%\s*(engagement|reach|impression)\b'
            ],
            'performance': [
                r'\b\d+(\.\d+)?[kKmM]?\s*(followers?|subscribers?|fans?)\b',
                r'\b(growth|increase|boost|surge)\b',
                r'\bROI\s*:?\s*\d+(\.\d+)?%?\b'
            ],
            'trends': [
                r'#trending\w*',
                r'\b(trending|viral|hot|popular|buzzing)\b',
                r'\b(tiktok|instagram|youtube)\s+(trend|challenge)\b'
            ],
            'brand_mentions': [
                r'\b(sponsored|ad|partnership|collab|collaboration)\b',
                r'#(ad|sponsored|partnership|promo)\b',
                r'\b(brand\s+ambassador|influencer\s+marketing)\b'
            ]
        }
    
    async def extract_content(self, text: str, source_type: str = "text", 
                            extraction_options: Dict[str, bool] = None) -> ExtractionResult:
        """Comprehensive content extraction"""
        start_time = datetime.utcnow()
        request_id = self._generate_request_id(text)
        
        # Default extraction options
        if extraction_options is None:
            extraction_options = {
                'entities': True,
                'contact_info': True,
                'keywords': True,
                'topics': True,
                'sentiments': True,
                'structured_data': True,
                'summarization': True
            }
        
        try:
            # Extract entities
            entities = []
            if extraction_options.get('entities', True):
                entities = await self._extract_entities(text)
            
            # Extract contact information
            contact_info = ContactInfo()
            if extraction_options.get('contact_info', True):
                contact_info = await self._extract_contact_info(text)
            
            # Extract content metrics
            content_metrics = await self._extract_content_metrics(text)
            
            # Extract keywords
            keywords = KeywordExtraction([], [], [], [], [], {}, [])
            if extraction_options.get('keywords', True):
                keywords = await self._extract_keywords(text)
            
            # Extract structured data
            structured_data = StructuredData([], [], [], [], [], [], [], [])
            if extraction_options.get('structured_data', True):
                structured_data = await self._extract_structured_data(text, source_type)
            
            # Extract topics
            topics = []
            if extraction_options.get('topics', True):
                topics = await self._extract_topics(text)
            
            # Extract sentiments (simplified)
            sentiments = {}
            if extraction_options.get('sentiments', True):
                sentiments = await self._extract_sentiments(text)
            
            # Extract key phrases
            key_phrases = await self._extract_key_phrases(text)
            
            # Generate summary
            summary = ""
            if extraction_options.get('summarization', True):
                summary = await self._generate_summary(text)
            
            # Extract metadata
            metadata = await self._extract_metadata(text, source_type)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = ExtractionResult(
                request_id=request_id,
                original_text=text,
                entities=entities,
                contact_info=contact_info,
                content_metrics=content_metrics,
                keywords=keywords,
                structured_data=structured_data,
                topics=topics,
                sentiments=sentiments,
                key_phrases=key_phrases,
                summary=summary,
                metadata=metadata,
                processing_time=processing_time
            )
            
            logger.info(f"Content extraction completed: {request_id}")
            return result
            
        except Exception as e:
            logger.error(f"Content extraction failed for {request_id}: {str(e)}")
            raise
    
    async def batch_extract_content(self, texts: List[str], source_type: str = "text") -> List[ExtractionResult]:
        """Batch content extraction"""
        tasks = [self.extract_content(text, source_type) for text in texts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch extraction error: {str(result)}")
                # Create minimal error result
                error_result = ExtractionResult(
                    request_id="error",
                    original_text="",
                    entities=[],
                    contact_info=ContactInfo(),
                    content_metrics=ContentMetrics(),
                    keywords=KeywordExtraction([], [], [], [], [], {}, []),
                    structured_data=StructuredData([], [], [], [], [], [], [], []),
                    topics=[],
                    sentiments={},
                    key_phrases=[],
                    summary="",
                    metadata={},
                    processing_time=0.0
                )
                valid_results.append(error_result)
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def _extract_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract named entities from text"""
        entities = []
        
        for entity_type, entity_info in self.entity_patterns.items():
            patterns = entity_info.get('patterns', [])
            context_keywords = entity_info.get('context_keywords', [])
            
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    entity_text = match.group()
                    start_pos = match.start()
                    end_pos = match.end()
                    
                    # Extract context (surrounding words)
                    context_start = max(0, start_pos - 50)
                    context_end = min(len(text), end_pos + 50)
                    context = text[context_start:context_end]
                    
                    # Calculate confidence based on context
                    confidence = await self._calculate_entity_confidence(
                        entity_text, entity_type, context, context_keywords
                    )
                    
                    if confidence >= self.config['confidence_threshold']:
                        entity = ExtractedEntity(
                            text=entity_text,
                            entity_type=entity_type,
                            confidence=confidence,
                            start_position=start_pos,
                            end_position=end_pos,
                            context=context,
                            attributes=await self._extract_entity_attributes(entity_text, entity_type)
                        )
                        entities.append(entity)
        
        # Remove duplicates and sort by confidence
        unique_entities = self._remove_duplicate_entities(entities)
        unique_entities.sort(key=lambda x: x.confidence, reverse=True)
        
        return unique_entities[:self.config['max_entities']]
    
    async def _calculate_entity_confidence(self, entity_text: str, entity_type: str, 
                                         context: str, context_keywords: List[str]) -> float:
        """
Calculate confidence score for extracted entity"""
        base_confidence = 0.5
        
        # Boost confidence if context keywords are found
        context_lower = context.lower()
        keyword_matches = sum(1 for keyword in context_keywords if keyword in context_lower)
        context_boost = min(0.3, keyword_matches * 0.1)
        
        # Boost confidence based on entity format
        format_boost = 0.0
        if entity_type == 'person' and re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', entity_text):
            format_boost = 0.2
        elif entity_type == 'email' and '@' in entity_text and '.' in entity_text:
            format_boost = 0.3
        elif entity_type == 'money' and ('$' in entity_text or 'dollar' in entity_text.lower()):
            format_boost = 0.2
        
        # Penalty for very short entities (likely noise)
        length_penalty = 0.0
        if len(entity_text) < 3:
            length_penalty = 0.2
        
        final_confidence = base_confidence + context_boost + format_boost - length_penalty
        return min(1.0, max(0.0, final_confidence))
    
    async def _extract_entity_attributes(self, entity_text: str, entity_type: str) -> Dict[str, Any]:
        """
Extract additional attributes for entities"""
        attributes = {}
        
        if entity_type == 'person':
            # Extract name components
            name_parts = entity_text.split()
            if len(name_parts) >= 2:
                attributes['first_name'] = name_parts[0]
                attributes['last_name'] = name_parts[-1]
                if len(name_parts) > 2:
                    attributes['middle_names'] = name_parts[1:-1]
        
        elif entity_type == 'money':
            # Extract amount and currency
            amount_match = re.search(r'[\d,]+(?:\.\d{2})?', entity_text)
            if amount_match:
                attributes['amount'] = amount_match.group()
                attributes['currency'] = 'USD'  # Default currency
        
        elif entity_type == 'date':
            # Normalize date format
            attributes['original_format'] = entity_text
            attributes['normalized_date'] = self._normalize_date(entity_text)
        
        elif entity_type == 'location':
            # Extract location components
            if ',' in entity_text:
                parts = entity_text.split(',')
                attributes['city'] = parts[0].strip()
                if len(parts) > 1:
                    attributes['state_or_country'] = parts[1].strip()
        
        return attributes
    
    def _normalize_date(self, date_text: str) -> str:
        """
Normalize date to standard format"""
        # Simplified date normalization
        date_lower = date_text.lower()
        
        if date_lower in ['today', 'yesterday', 'tomorrow']:
            return date_lower
        elif 'next week' in date_lower:
            return 'next_week'
        elif 'last week' in date_lower:
            return 'last_week'
        else:
            return date_text  # Return original for now
    
    def _remove_duplicate_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """
Remove duplicate entities"""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            # Create a key based on text and type
            key = (entity.text.lower(), entity.entity_type)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    async def _extract_contact_info(self, text: str) -> ContactInfo:
        """
Extract contact information"""
        contact_info = ContactInfo()
        
        # Extract emails
        email_patterns = self.contact_patterns['email']
        for pattern in email_patterns:
            emails = re.findall(pattern, text)
            contact_info.emails.extend(emails)
        
        # Extract phone numbers
        phone_patterns = self.contact_patterns['phone']
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            contact_info.phone_numbers.extend(phones)
        
        # Extract social media handles
        social_platforms = ['instagram', 'twitter', 'tiktok', 'youtube']
        for platform in social_platforms:
            platform_key = f'social_{platform}'
            if platform_key in self.contact_patterns:
                patterns = self.contact_patterns[platform_key]
                handles = []
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    handles.extend(matches)
                
                if handles:
                    contact_info.social_handles[platform] = list(set(handles))
        
        # Extract websites
        website_patterns = self.contact_patterns['website']
        for pattern in website_patterns:
            websites = re.findall(pattern, text, re.IGNORECASE)
            contact_info.websites.extend(websites)
        
        # Remove duplicates
        contact_info.emails = list(set(contact_info.emails))
        contact_info.phone_numbers = list(set(contact_info.phone_numbers))
        contact_info.websites = list(set(contact_info.websites))
        
        return contact_info
    
    async def _extract_content_metrics(self, text: str) -> ContentMetrics:
        """
Extract content performance metrics"""
        metrics = ContentMetrics()
        
        # Extract engagement indicators
        engagement_patterns = self.metrics_patterns['engagement']
        for pattern in engagement_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metrics.engagement_indicators.extend(matches)
        
        # Extract performance metrics
        performance_patterns = self.metrics_patterns['performance']
        for pattern in performance_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            
        # Extract trend indicators
        trend_patterns = self.metrics_patterns['trends']
        for pattern in trend_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metrics.trend_indicators.extend(matches)
        
        # Extract brand mentions
        brand_patterns = self.metrics_patterns['brand_mentions']
        for pattern in brand_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metrics.brand_mentions.extend(matches)
        
        # Parse numerical metrics
        metrics.performance_metrics = await self._parse_numerical_metrics(text)
        
        # Identify viral signals
        metrics.viral_signals = await self._identify_viral_signals(text)
        
        return metrics
    
    async def _parse_numerical_metrics(self, text: str) -> Dict[str, float]:
        """
Parse numerical performance metrics"""
        metrics = {}
        
        # Parse follower counts
        follower_pattern = r'(\d+(?:\.\d+)?[kKmM]?)\s*(?:followers?|subscribers?)'
        follower_matches = re.findall(follower_pattern, text, re.IGNORECASE)
        if follower_matches:
            metrics['followers'] = self._convert_metric_to_number(follower_matches[0])
        
        # Parse engagement rates
        engagement_pattern = r'(\d+(?:\.\d+)?)%\s*engagement'
        engagement_matches = re.findall(engagement_pattern, text, re.IGNORECASE)
        if engagement_matches:
            metrics['engagement_rate'] = float(engagement_matches[0])
        
        # Parse view counts
        view_pattern = r'(\d+(?:\.\d+)?[kKmM]?)\s*(?:views?|impressions?)'
        view_matches = re.findall(view_pattern, text, re.IGNORECASE)
        if view_matches:
            metrics['views'] = self._convert_metric_to_number(view_matches[0])
        
        return metrics
    
    def _convert_metric_to_number(self, metric_str: str) -> float:
        """
Convert metric string (e.g., '1.2M') to number"""
        metric_str = metric_str.upper()
        
        if metric_str.endswith('K'):
            return float(metric_str[:-1]) * 1000
        elif metric_str.endswith('M'):
            return float(metric_str[:-1]) * 1000000
        else:
            return float(metric_str)
    
    async def _identify_viral_signals(self, text: str) -> List[str]:
        """
Identify signals that indicate viral content"""
        viral_signals = []
        text_lower = text.lower()
        
        viral_keywords = [
            'viral', 'trending', 'exploded', 'blew up', 'went viral',
            'millions of views', 'overnight success', 'took off',
            'massive response', 'incredible reach', 'broke the internet'
        ]
        
        for keyword in viral_keywords:
            if keyword in text_lower:
                viral_signals.append(keyword)
        
        # Check for high engagement indicators
        if re.search(r'\d+[mM]\s*(?:views?|likes?)', text):
            viral_signals.append('high_engagement_numbers')
        
        # Check for trending hashtags
        if re.search(r'#trending|#viral|#fyp', text, re.IGNORECASE):
            viral_signals.append('trending_hashtags')
        
        return viral_signals
    
    async def _extract_keywords(self, text: str) -> KeywordExtraction:
        """
Extract keywords using multiple methods"""
        
        # Extract primary keywords using TF-IDF approach (simplified)
        primary_keywords = await self._extract_tfidf_keywords(text)
        
        # Extract secondary keywords
        secondary_keywords = await self._extract_secondary_keywords(text)
        
        # Extract hashtags
        hashtags = re.findall(r'#\w+', text)
        hashtags = [tag[1:] for tag in hashtags]  # Remove # symbol
        
        # Extract mentions
        mentions = re.findall(r'@\w+', text)
        mentions = [mention[1:] for mention in mentions]  # Remove @ symbol
        
        # Extract trending terms
        trending_terms = await self._extract_trending_terms(text)
        
        # Calculate keyword density
        keyword_density = await self._calculate_keyword_density(text, primary_keywords + secondary_keywords)
        
        # Extract semantic keywords
        semantic_keywords = await self._extract_semantic_keywords(text)
        
        return KeywordExtraction(
            primary_keywords=primary_keywords,
            secondary_keywords=secondary_keywords,
            hashtags=hashtags,
            mentions=mentions,
            trending_terms=trending_terms,
            keyword_density=keyword_density,
            semantic_keywords=semantic_keywords
        )
    
    async def _extract_tfidf_keywords(self, text: str) -> List[str]:
        """
Extract keywords using TF-IDF approach (simplified)"""
        words = text.lower().split()
        
        # Remove stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Filter words
        filtered_words = [
            word for word in words 
            if len(word) > 2 and word not in stop_words and word.isalpha()
        ]
        
        # Count word frequency
        word_counts = Counter(filtered_words)
        
        # Get most frequent words as keywords
        keywords = [word for word, count in word_counts.most_common(10)]
        
        return keywords
    
    async def _extract_secondary_keywords(self, text: str) -> List[str]:
        """
Extract secondary keywords using phrase extraction"""
        # Extract 2-word phrases
        words = text.lower().split()
        phrases = []
        
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            if len(phrase) > 5:  # Minimum phrase length
                phrases.append(phrase)
        
        # Count phrase frequency
        phrase_counts = Counter(phrases)
        
        # Get most frequent phrases
        secondary_keywords = [phrase for phrase, count in phrase_counts.most_common(5)]
        
        return secondary_keywords
    
    async def _extract_trending_terms(self, text: str) -> List[str]:
        """Extract trending terms and buzzwords"""
        trending_indicators = [
            'trending', 'viral', 'hot', 'popular', 'buzzing', 'talked about',
            'everyone is', 'latest', 'new', 'breakthrough', 'revolutionary'
        ]
        
        trending_terms = []
        text_lower = text.lower()
        
        for indicator in trending_indicators:
            if indicator in text_lower:
                trending_terms.append(indicator)
        
        # Extract terms that appear with trending indicators
        for indicator in trending_indicators:
            pattern = rf'{indicator}\s+(\w+(?:\s+\w+)?)'
            matches = re.findall(pattern, text_lower)
            trending_terms.extend(matches)
        
        return list(set(trending_terms))
    
    async def _calculate_keyword_density(self, text: str, keywords: List[str]) -> Dict[str, float]:
        """
Calculate keyword density"""
        text_lower = text.lower()
        total_words = len(text.split())
        
        keyword_density = {}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = text_lower.count(keyword_lower)
            density = (count / total_words) * 100 if total_words > 0 else 0
            keyword_density[keyword] = round(density, 2)
        
        return keyword_density
    
    async def _extract_semantic_keywords(self, text: str) -> List[str]:
        """
Extract semantically related keywords"""
        # This would use actual semantic analysis in production
        # For now, we'll use topic-based keyword extraction
        
        semantic_keywords = []
        text_lower = text.lower()
        
        topic_keywords = self.topic_extractors['topic_keywords']
        
        for topic, keywords in topic_keywords.items():
            topic_matches = 0
            for keyword in keywords:
                if keyword in text_lower:
                    topic_matches += 1
            
            # If topic is relevant, add related keywords
            if topic_matches >= 2:
                semantic_keywords.extend(keywords[:3])  # Top 3 keywords per topic
        
        return list(set(semantic_keywords))
    
    async def _extract_structured_data(self, text: str, source_type: str) -> StructuredData:
        """
Extract structured data elements"""
        structured_data = StructuredData([], [], [], [], [], [], [], [])
        
        if source_type in ['markdown', 'html', 'document']:
            # Extract titles and headings
            structured_data.titles = self._extract_titles(text)
            structured_data.headings = self._extract_headings(text)
            
            # Extract lists
            structured_data.bullet_points = self._extract_bullet_points(text)
            structured_data.numbered_lists = self._extract_numbered_lists(text)
            
            # Extract quotes
            structured_data.quotes = self._extract_quotes(text)
            
            # Extract code blocks
            structured_data.code_blocks = self._extract_code_blocks(text)
        
        # Extract links (for all source types)
        structured_data.links = self._extract_links(text)
        
        # Extract image references
        structured_data.images = self._extract_image_references(text)
        
        return structured_data
    
    def _extract_titles(self, text: str) -> List[str]:
        """
Extract titles from text"""
        # Markdown-style titles
        titles = re.findall(r'^#\s+(.+)$', text, re.MULTILINE)
        
        # HTML-style titles
        html_titles = re.findall(r'<h[1-6]>(.+?)</h[1-6]>', text, re.IGNORECASE)
        titles.extend(html_titles)
        
        return titles
    
    def _extract_headings(self, text: str) -> List[str]:
        """
Extract headings from text"""
        # Markdown-style headings
        headings = re.findall(r'^#{2,6}\s+(.+)$', text, re.MULTILINE)
        
        # HTML-style headings
        html_headings = re.findall(r'<h[2-6]>(.+?)</h[2-6]>', text, re.IGNORECASE)
        headings.extend(html_headings)
        
        return headings
    
    def _extract_bullet_points(self, text: str) -> List[str]:
        """
Extract bullet points from text"""
        # Markdown-style bullet points
        bullet_points = re.findall(r'^\s*[-*+]\s+(.+)$', text, re.MULTILINE)
        
        # HTML-style list items
        html_bullets = re.findall(r'<li>(.+?)</li>', text, re.IGNORECASE)
        bullet_points.extend(html_bullets)
        
        return bullet_points
    
    def _extract_numbered_lists(self, text: str) -> List[str]:
        """
Extract numbered lists from text"""
        # Numbered lists
        numbered_items = re.findall(r'^\s*\d+\.\s+(.+)$', text, re.MULTILINE)
        
        return numbered_items
    
    def _extract_quotes(self, text: str) -> List[str]:
        """
Extract quotes from text"""
        # Markdown-style quotes
        quotes = re.findall(r'^>\s+(.+)$', text, re.MULTILINE)
        
        # Traditional quotes
        quoted_text = re.findall(r'"([^"]+)"', text)
        quotes.extend(quoted_text)
        
        single_quotes = re.findall(r"'([^']+)'", text)
        quotes.extend(single_quotes)
        
        return quotes
    
    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from text"""
        # Markdown-style code blocks
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', text, re.DOTALL)
        
        # Inline code
        inline_code = re.findall(r'`([^`]+)`', text)
        code_blocks.extend(inline_code)
        
        return code_blocks
    
    def _extract_links(self, text: str) -> List[Dict[str, str]]:
        """
Extract links from text"""
        links = []
        
        # Markdown-style links
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)
        for link_text, url in markdown_links:
            links.append({'text': link_text, 'url': url, 'type': 'markdown'})
        
        # HTML-style links
        html_links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>', text, re.IGNORECASE)
        for url, link_text in html_links:
            links.append({'text': link_text, 'url': url, 'type': 'html'})
        
        # Plain URLs
        plain_urls = re.findall(r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        for url in plain_urls:
            links.append({'text': url, 'url': url, 'type': 'plain'})
        
        return links
    
    def _extract_image_references(self, text: str) -> List[Dict[str, str]]:
        """Extract image references from text"""
        images = []
        
        # Markdown-style images
        markdown_images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', text)
        for alt_text, url in markdown_images:
            images.append({'alt_text': alt_text, 'url': url, 'type': 'markdown'})
        
        # HTML-style images
        html_images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*(?:alt=["\']([^"\']*)["\'])?[^>]*>', text, re.IGNORECASE)
        for url, alt_text in html_images:
            images.append({'alt_text': alt_text or '', 'url': url, 'type': 'html'})
        
        return images
    
    async def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text"""
        topics = []
        text_lower = text.lower()
        
        topic_keywords = self.topic_extractors['topic_keywords']
        topic_scores = {}
        
        # Score each topic based on keyword presence
        for topic, keywords in topic_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            
            if score > 0:
                # Normalize score by topic keyword count
                normalized_score = score / len(keywords)
                topic_scores[topic] = normalized_score
        
        # Sort topics by relevance
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top topics
        topics = [topic for topic, score in sorted_topics if score > 0.1]
        
        return topics[:5]  # Top 5 topics
    
    async def _extract_sentiments(self, text: str) -> Dict[str, float]:
        """
Extract sentiment information (simplified)"""
        # This would integrate with the sentiment module in production
        
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'awesome']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'horrible', 'disappointing', 'worst']
        neutral_words = ['okay', 'fine', 'normal', 'average', 'standard']
        
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        neutral_count = sum(1 for word in words if word in neutral_words)
        
        total_sentiment_words = positive_count + negative_count + neutral_count
        
        if total_sentiment_words == 0:
            return {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
        
        return {
            'positive': positive_count / total_sentiment_words,
            'negative': negative_count / total_sentiment_words,
            'neutral': neutral_count / total_sentiment_words
        }
    
    async def _extract_key_phrases(self, text: str) -> List[str]:
        """
Extract key phrases from text"""
        # Extract noun phrases and important phrases
        sentences = text.split('.')
        key_phrases = []
        
        for sentence in sentences:
            # Extract capitalized phrases (likely important)
            capitalized_phrases = re.findall(r'\b[A-Z][a-zA-Z\s]{2,20}\b', sentence)
            key_phrases.extend(capitalized_phrases)
            
            # Extract quoted phrases
            quoted_phrases = re.findall(r'"([^"]+)"', sentence)
            key_phrases.extend(quoted_phrases)
        
        # Remove duplicates and filter
        unique_phrases = []
        seen = set()
        
        for phrase in key_phrases:
            phrase_clean = phrase.strip()
            if len(phrase_clean) > 3 and phrase_clean.lower() not in seen:
                seen.add(phrase_clean.lower())
                unique_phrases.append(phrase_clean)
        
        return unique_phrases[:10]  # Top 10 key phrases
    
    async def _generate_summary(self, text: str) -> str:
        """Generate text summary"""
        # Simplified extractive summarization
        sentences = text.split('.')
        
        if len(sentences) <= 3:
            return text.strip()
        
        # Score sentences based on keyword frequency
        word_freq = Counter(text.lower().split())
        
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) > 10:  # Skip very short sentences
                words = sentence.lower().split()
                score = sum(word_freq[word] for word in words if word in word_freq)
                sentence_scores[i] = score / len(words) if words else 0
        
        # Select top sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Take top 2-3 sentences for summary
        summary_count = min(3, len(top_sentences))
        selected_indices = sorted([idx for idx, score in top_sentences[:summary_count]])
        
        summary_sentences = [sentences[i].strip() for i in selected_indices if sentences[i].strip()]
        
        return '. '.join(summary_sentences) + '.' if summary_sentences else text[:200] + '...'
    
    async def _extract_metadata(self, text: str, source_type: str) -> Dict[str, Any]:
        """
Extract metadata from content"""
        metadata = {
            'source_type': source_type,
            'word_count': len(text.split()),
            'character_count': len(text),
            'sentence_count': len(text.split('.')),
            'paragraph_count': len(text.split('\n\n')),
            'language': await self._detect_language(text),
            'readability_score': await self._calculate_readability(text),
            'complexity_level': await self._assess_complexity(text),
            'extraction_timestamp': datetime.utcnow().isoformat()
        }
        
        return metadata
    
    async def _detect_language(self, text: str) -> str:
        """
Detect text language (simplified)"""
        # This would use actual language detection in production
        english_indicators = ['the', 'and', 'is', 'are', 'was', 'were', 'have', 'has']
        spanish_indicators = ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es']
        french_indicators = ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et']
        
        text_lower = text.lower()
        
        english_count = sum(1 for word in english_indicators if word in text_lower)
        spanish_count = sum(1 for word in spanish_indicators if word in text_lower)
        french_count = sum(1 for word in french_indicators if word in text_lower)
        
        if english_count >= spanish_count and english_count >= french_count:
            return 'en'
        elif spanish_count >= french_count:
            return 'es'
        elif french_count > 0:
            return 'fr'
        else:
            return 'unknown'
    
    async def _calculate_readability(self, text: str) -> float:
        """
Calculate readability score (simplified Flesch Reading Ease)"""
        sentences = text.split('.')
        words = text.split()
        syllables = sum(self._count_syllables(word) for word in words)
        
        if len(sentences) == 0 or len(words) == 0:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        
        # Simplified Flesch Reading Ease formula
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        return max(0.0, min(100.0, score))
    
    def _count_syllables(self, word: str) -> int:
        """
Count syllables in a word (simplified)"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    async def _assess_complexity(self, text: str) -> str:
        """
Assess text complexity level"""
        words = text.split()
        
        if not words:
            return 'unknown'
        
        # Calculate average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Count complex words (more than 6 characters)
        complex_words = sum(1 for word in words if len(word) > 6)
        complexity_ratio = complex_words / len(words)
        
        # Determine complexity level
        if avg_word_length > 6 and complexity_ratio > 0.3:
            return 'advanced'
        elif avg_word_length > 5 and complexity_ratio > 0.2:
            return 'intermediate'
        else:
            return 'beginner'
    
    def _generate_request_id(self, text: str) -> str:
        """
Generate unique request ID"""
        import hashlib
        id_string = f"{text[:100]}{datetime.utcnow().isoformat()}"
        return hashlib.md5(id_string.encode()).hexdigest()[:12]

# Utility functions for quick extraction
async def quick_extract_keywords(text: str) -> List[str]:
    """Quick keyword extraction"""
    extractor = AdvancedContentExtractor()
    result = await extractor.extract_content(text, extraction_options={'keywords': True})
    return result.keywords.primary_keywords + result.keywords.secondary_keywords

async def quick_extract_entities(text: str) -> List[Dict[str, Any]]:
    """
Quick entity extraction"""
    extractor = AdvancedContentExtractor()
    result = await extractor.extract_content(text, extraction_options={'entities': True})
    
    return [
        {
            'text': entity.text,
            'type': entity.entity_type,
            'confidence': entity.confidence
        }
        for entity in result.entities
    ]

async def extract_contact_info(text: str) -> Dict[str, Any]:
    """
Extract contact information from text"""
    extractor = AdvancedContentExtractor()
    result = await extractor.extract_content(text, extraction_options={'contact_info': True})
    
    return {
        'emails': result.contact_info.emails,
        'phones': result.contact_info.phone_numbers,
        'social_media': result.contact_info.social_handles,
        'websites': result.contact_info.websites
    }
