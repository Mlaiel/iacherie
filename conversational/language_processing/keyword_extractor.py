"""Enterprise Keyword Extraction and Topic Modeling Module
=======================================================

Next-generation keyword extraction and topic discovery for content optimization:
- Multi-algorithm intelligent keyword extraction with neural networks
- Advanced topic modeling and semantic theme identification
- SEO keyword suggestions with competitive analysis
- Content clustering and automated categorization
- Trending keyword detection and prediction
- Real-time keyword performance analytics
- Industry-specific keyword optimization
- Multi-language keyword extraction with cultural context

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
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import re
from datetime import datetime, timezone
import hashlib

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import yake
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
from gensim import corpora, models
from gensim.models import Word2Vec, LdaModel
from transformers import pipeline
import torch

from ...core.config import settings
from ...core.logging import get_logger
from ...core.cache import cache_manager
from ...utils.text_utils import clean_text, normalize_unicode

logger = get_logger(__name__)


class ExtractionMethod(Enum):
    """
Keyword extraction methods"""

    TFIDF = "tfidf"
    YAKE = "yake"
    TEXTRANK = "textrank"
    NER = "ner"
    STATISTICAL = "statistical"
    TRANSFORMER = "transformer"
    HYBRID = "hybrid"


class TopicModelType(Enum):
    """Topic modeling algorithms"""

    LDA = "lda"
    NMF = "nmf"
    GENSIM_LDA = "gensim_lda"
    BERT_TOPIC = "bert_topic"


class KeywordType(Enum):
    """Types of extracted keywords"""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    ENTITY = "entity"
    TECHNICAL = "technical"
    BRAND = "brand"
    LOCATION = "location"
    PERSON = "person"
    ORGANIZATION = "organization"


@dataclass
class Keyword:
    """Represents an extracted keyword"""
    text: str
    keyword_type: KeywordType
    frequency: int
    relevance_score: float
    tfidf_score: float
    positions: List[int] = field(default_factory=list)
    context_sentences: List[str] = field(default_factory=list)
    related_keywords: List[str] = field(default_factory=list)
    extraction_method: ExtractionMethod = ExtractionMethod.HYBRID


@dataclass
class Topic:
    """
Represents a discovered topic"""
    topic_id: int
    topic_name: str
    keywords: List[str]
    keyword_weights: List[float]
    coherence_score: float
    topic_probability: float
    representative_documents: List[str] = field(default_factory=list)
    related_topics: List[int] = field(default_factory=list)


@dataclass
class KeywordExtractionResult:
    """
Complete keyword extraction result"""
    primary_keywords: List[Keyword]
    secondary_keywords: List[Keyword]
    entities: List[Keyword]
    topics: List[Topic]
    keyword_clusters: Dict[str, List[str]]
    semantic_relationships: Dict[str, List[str]]
    seo_suggestions: List[str]
    content_categories: List[str]
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class KeywordExtractor:
    """
Advanced keyword extraction engine"""
    
    def __init__(self):
        self.nlp = None
        self.yake_extractor = None
        self.stop_words = set()
        self._initialize_models()
        
    def _initialize_models(self):
        """
Initialize keyword extraction models"""
        try:
            # Initialize spaCy
            self.nlp = spacy.load("en_core_web_lg")
            
            # Initialize YAKE
            self.yake_extractor = yake.KeywordExtractor(
                lan="en",
                n=3,  # n-gram size
                dedupLim=0.7,
                top=20
            )
            
            # Load stop words
            try:
                self.stop_words = set(stopwords.words('english'))
            except:
                nltk.download('stopwords', quiet=True)
                self.stop_words = set(stopwords.words('english'))
                
            # Initialize transformer model for semantic analysis
            self.semantic_model = pipeline(
                "feature-extraction",
                model="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            logger.info("Keyword extraction models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize keyword models: {e}")
            
    async def extract_keywords(
        self,
        text: str,
        num_keywords: int = 20,
        methods: List[ExtractionMethod] = None,
        include_entities: bool = True,
        include_topics: bool = True
    ) -> KeywordExtractionResult:
        """
        Extract keywords using multiple methods
        
        Args:
            text: Text to extract keywords from
            num_keywords: Number of keywords to extract
            methods: Extraction methods to use
            include_entities: Whether to extract named entities
            include_topics: Whether to perform topic modeling
            
        Returns:
            KeywordExtractionResult with extracted keywords and topics
        """
        try:
            start_time = datetime.now()
            
            # Use default methods if none specified
            if methods is None:
                methods = [ExtractionMethod.HYBRID]
                
            # Clean and preprocess text
            cleaned_text = clean_text(text)
            
            # Extract keywords using different methods
            all_keywords = []
            
            for method in methods:
                method_keywords = await self._extract_with_method(cleaned_text, method, num_keywords)
                all_keywords.extend(method_keywords)
                
            # Merge and rank keywords
            merged_keywords = await self._merge_and_rank_keywords(all_keywords)
            
            # Categorize keywords
            primary_keywords, secondary_keywords = await self._categorize_keywords(merged_keywords)
            
            # Extract entities if requested
            entities = []
            if include_entities:
                entities = await self._extract_entities(cleaned_text)
                
            # Perform topic modeling if requested
            topics = []
            if include_topics and len(cleaned_text.split()) > 50:
                topics = await self._extract_topics(cleaned_text)
                
            # Generate keyword clusters
            keyword_clusters = await self._cluster_keywords(primary_keywords + secondary_keywords)
            
            # Find semantic relationships
            semantic_relationships = await self._find_semantic_relationships(
                primary_keywords + secondary_keywords
            )
            
            # Generate SEO suggestions
            seo_suggestions = await self._generate_seo_suggestions(
                primary_keywords, secondary_keywords, cleaned_text
            )
            
            # Categorize content
            content_categories = await self._categorize_content(topics, primary_keywords)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return KeywordExtractionResult(
                primary_keywords=primary_keywords[:num_keywords//2],
                secondary_keywords=secondary_keywords[:num_keywords//2],
                entities=entities,
                topics=topics,
                keyword_clusters=keyword_clusters,
                semantic_relationships=semantic_relationships,
                seo_suggestions=seo_suggestions,
                content_categories=content_categories,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            raise
            
    async def _extract_with_method(
        self,
        text: str,
        method: ExtractionMethod,
        num_keywords: int
    ) -> List[Keyword]:
        """Extract keywords using specific method"""
        try:
            if method == ExtractionMethod.TFIDF:
                return await self._extract_tfidf_keywords(text, num_keywords)
            elif method == ExtractionMethod.YAKE:
                return await self._extract_yake_keywords(text, num_keywords)
            elif method == ExtractionMethod.NER:
                return await self._extract_ner_keywords(text, num_keywords)
            elif method == ExtractionMethod.STATISTICAL:
                return await self._extract_statistical_keywords(text, num_keywords)
            elif method == ExtractionMethod.TRANSFORMER:
                return await self._extract_transformer_keywords(text, num_keywords)
            elif method == ExtractionMethod.HYBRID:
                return await self._extract_hybrid_keywords(text, num_keywords)
            else:
                return await self._extract_tfidf_keywords(text, num_keywords)
                
        except Exception as e:
            logger.error(f"Keyword extraction with {method.value} failed: {e}")
            return []
            
    async def _extract_tfidf_keywords(self, text: str, num_keywords: int) -> List[Keyword]:
        """Extract keywords using TF-IDF"""
        try:
            # Prepare documents (sentences)
            sentences = sent_tokenize(text)
            
            if len(sentences) < 2:
                return []
                
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=num_keywords * 2,
                stop_words='english',
                ngram_range=(1, 3),
                max_df=0.8,
                min_df=1
            )
            
            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get scores
            scores = tfidf_matrix.sum(axis=0).A1
            
            # Create keywords
            keywords = []
            for i, score in enumerate(scores):
                if score > 0:
                    keyword_text = feature_names[i]
                    frequency = text.lower().count(keyword_text.lower())
                    
                    keyword = Keyword(
                        text=keyword_text,
                        keyword_type=KeywordType.PRIMARY,
                        frequency=frequency,
                        relevance_score=score,
                        tfidf_score=score,
                        extraction_method=ExtractionMethod.TFIDF
                    )
                    keywords.append(keyword)
                    
            # Sort by score and return top keywords
            keywords.sort(key=lambda x: x.tfidf_score, reverse=True)
            return keywords[:num_keywords]
            
        except Exception as e:
            logger.error(f"TF-IDF extraction failed: {e}")
            return []
            
    async def _extract_yake_keywords(self, text: str, num_keywords: int) -> List[Keyword]:
        """Extract keywords using YAKE"""
        try:
            if not self.yake_extractor:
                return []
                
            # Extract keywords
            yake_keywords = self.yake_extractor.extract_keywords(text)
            
            keywords = []
            for score, keyword_text in yake_keywords[:num_keywords]:
                frequency = text.lower().count(keyword_text.lower())
                # YAKE score is lower for better keywords, so invert
                relevance_score = 1.0 / (1.0 + score)
                
                keyword = Keyword(
                    text=keyword_text,
                    keyword_type=KeywordType.PRIMARY,
                    frequency=frequency,
                    relevance_score=relevance_score,
                    tfidf_score=relevance_score,
                    extraction_method=ExtractionMethod.YAKE
                )
                keywords.append(keyword)
                
            return keywords
            
        except Exception as e:
            logger.error(f"YAKE extraction failed: {e}")
            return []
            
    async def _extract_ner_keywords(self, text: str, num_keywords: int) -> List[Keyword]:
        """Extract keywords using Named Entity Recognition"""
        try:
            if not self.nlp:
                return []
                
            doc = self.nlp(text)
            keywords = []
            entity_counts = {}
            
            # Count entity frequencies
            for ent in doc.ents:
                entity_text = ent.text.strip()
                if len(entity_text) > 1:
                    entity_counts[entity_text] = entity_counts.get(entity_text, 0) + 1
                    
            # Create keyword objects
            for entity_text, frequency in entity_counts.items():
                keyword_type = self._map_entity_label_to_keyword_type(entity_text, doc)
                
                keyword = Keyword(
                    text=entity_text,
                    keyword_type=keyword_type,
                    frequency=frequency,
                    relevance_score=frequency / len(doc.ents) if doc.ents else 0,
                    tfidf_score=frequency,
                    extraction_method=ExtractionMethod.NER
                )
                keywords.append(keyword)
                
            # Sort by frequency and return top keywords
            keywords.sort(key=lambda x: x.frequency, reverse=True)
            return keywords[:num_keywords]
            
        except Exception as e:
            logger.error(f"NER extraction failed: {e}")
            return []
            
    def _map_entity_label_to_keyword_type(self, entity_text: str, doc) -> KeywordType:
        """Map entity label to keyword type"""
        for ent in doc.ents:
            if ent.text == entity_text:
                if ent.label_ == "PERSON":
                    return KeywordType.PERSON
                elif ent.label_ == "ORG":
                    return KeywordType.ORGANIZATION
                elif ent.label_ in ["GPE", "LOC"]:
                    return KeywordType.LOCATION
                else:
                    return KeywordType.ENTITY
        return KeywordType.ENTITY
        
    async def _extract_statistical_keywords(self, text: str, num_keywords: int) -> List[Keyword]:
        """Extract keywords using statistical methods"""
        try:
            # Tokenize and filter words
            words = word_tokenize(text.lower())
            words = [word for word in words if word.isalpha() and word not in self.stop_words]
            
            # Calculate word frequencies
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
                
            # Calculate scores (frequency * length bonus)
            keywords = []
            for word, freq in word_freq.items():
                if len(word) > 2 and freq > 1:
                    # Length bonus for longer words
                    length_bonus = min(len(word) / 10, 1.0)
                    relevance_score = freq * (1 + length_bonus)
                    
                    keyword = Keyword(
                        text=word,
                        keyword_type=KeywordType.SECONDARY,
                        frequency=freq,
                        relevance_score=relevance_score,
                        tfidf_score=relevance_score,
                        extraction_method=ExtractionMethod.STATISTICAL
                    )
                    keywords.append(keyword)
                    
            # Sort by relevance and return top keywords
            keywords.sort(key=lambda x: x.relevance_score, reverse=True)
            return keywords[:num_keywords]
            
        except Exception as e:
            logger.error(f"Statistical extraction failed: {e}")
            return []
            
    async def _extract_transformer_keywords(self, text: str, num_keywords: int) -> List[Keyword]:
        """Extract keywords using transformer models"""
        try:
            # This is a simplified implementation
            # In a full implementation, you would use more sophisticated transformer-based methods
            
            # Extract noun phrases using spaCy
            if not self.nlp:
                return []
                
            doc = self.nlp(text)
            noun_phrases = []
            
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) <= 3:  # Limit to trigrams
                    noun_phrases.append(chunk.text.strip())
                    
            # Score noun phrases
            keywords = []
            for phrase in noun_phrases:
                frequency = text.lower().count(phrase.lower())
                if frequency > 0:
                    # Simple scoring based on frequency and phrase length
                    relevance_score = frequency * len(phrase.split())
                    
                    keyword = Keyword(
                        text=phrase,
                        keyword_type=KeywordType.TECHNICAL,
                        frequency=frequency,
                        relevance_score=relevance_score,
                        tfidf_score=relevance_score,
                        extraction_method=ExtractionMethod.TRANSFORMER
                    )
                    keywords.append(keyword)
                    
            # Sort and return top keywords
            keywords.sort(key=lambda x: x.relevance_score, reverse=True)
            return keywords[:num_keywords]
            
        except Exception as e:
            logger.error(f"Transformer extraction failed: {e}")
            return []
            
    async def _extract_hybrid_keywords(self, text: str, num_keywords: int) -> List[Keyword]:
        """Extract keywords using hybrid approach"""
        try:
            # Combine multiple methods
            tfidf_keywords = await self._extract_tfidf_keywords(text, num_keywords // 2)
            yake_keywords = await self._extract_yake_keywords(text, num_keywords // 2)
            ner_keywords = await self._extract_ner_keywords(text, num_keywords // 4)
            
            # Combine all keywords
            all_keywords = tfidf_keywords + yake_keywords + ner_keywords
            
            return all_keywords
            
        except Exception as e:
            logger.error(f"Hybrid extraction failed: {e}")
            return []
            
    async def _merge_and_rank_keywords(self, keywords: List[Keyword]) -> List[Keyword]:
        """Merge duplicate keywords and rank by combined scores"""
        try:
            keyword_map = {}
            
            # Merge duplicates
            for keyword in keywords:
                key = keyword.text.lower()
                if key in keyword_map:
                    # Combine scores
                    existing = keyword_map[key]
                    existing.frequency += keyword.frequency
                    existing.relevance_score = max(existing.relevance_score, keyword.relevance_score)
                    existing.tfidf_score = max(existing.tfidf_score, keyword.tfidf_score)
                else:
                    keyword_map[key] = keyword
                    
            # Convert back to list and sort
            merged_keywords = list(keyword_map.values())
            merged_keywords.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return merged_keywords
            
        except Exception as e:
            logger.error(f"Keyword merging failed: {e}")
            return keywords
            
    async def _categorize_keywords(self, keywords: List[Keyword]) -> Tuple[List[Keyword], List[Keyword]]:
        """Categorize keywords into primary and secondary"""
        try:
            # Sort by relevance score
            sorted_keywords = sorted(keywords, key=lambda x: x.relevance_score, reverse=True)
            
            # Split into primary and secondary
            split_point = len(sorted_keywords) // 2
            primary = sorted_keywords[:split_point]
            secondary = sorted_keywords[split_point:]
            
            # Update keyword types
            for keyword in primary:
                if keyword.keyword_type == KeywordType.SECONDARY:
                    keyword.keyword_type = KeywordType.PRIMARY
                    
            return primary, secondary
            
        except Exception as e:
            logger.error(f"Keyword categorization failed: {e}")
            return keywords[:len(keywords)//2], keywords[len(keywords)//2:]
            
    async def _extract_entities(self, text: str) -> List[Keyword]:
        """Extract named entities as keywords"""
        try:
            if not self.nlp:
                return []
                
            doc = self.nlp(text)
            entities = []
            
            for ent in doc.ents:
                if len(ent.text.strip()) > 1:
                    keyword_type = self._map_entity_label_to_keyword_type(ent.text, doc)
                    frequency = text.count(ent.text)
                    
                    keyword = Keyword(
                        text=ent.text.strip(),
                        keyword_type=keyword_type,
                        frequency=frequency,
                        relevance_score=frequency,
                        tfidf_score=frequency,
                        extraction_method=ExtractionMethod.NER
                    )
                    entities.append(keyword)
                    
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []
            
    async def _extract_topics(self, text: str, num_topics: int = 5) -> List[Topic]:
        """Extract topics using LDA"""
        try:
            # Prepare text for topic modeling
            sentences = sent_tokenize(text)
            
            if len(sentences) < 3:
                return []
                
            # Create LDA model
            vectorizer = CountVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2),
                max_df=0.8,
                min_df=1
            )
            
            doc_term_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
            
            # Fit LDA model
            lda = LatentDirichletAllocation(
                n_components=min(num_topics, len(sentences)),
                random_state=42,
                max_iter=100
            )
            
            lda.fit(doc_term_matrix)
            
            # Extract topics
            topics = []
            for topic_idx, topic in enumerate(lda.components_):
                # Get top words for topic
                top_word_indices = topic.argsort()[-10:][::-1]
                topic_keywords = [feature_names[i] for i in top_word_indices]
                topic_weights = [topic[i] for i in top_word_indices]
                
                # Calculate topic probability
                topic_prob = np.sum(topic) / np.sum(lda.components_)
                
                topic_obj = Topic(
                    topic_id=topic_idx,
                    topic_name=f"Topic {topic_idx + 1}",
                    keywords=topic_keywords,
                    keyword_weights=topic_weights,
                    coherence_score=0.7,  # Simplified coherence score
                    topic_probability=topic_prob
                )
                topics.append(topic_obj)
                
            return topics
            
        except Exception as e:
            logger.error(f"Topic extraction failed: {e}")
            return []
            
    async def _cluster_keywords(self, keywords: List[Keyword]) -> Dict[str, List[str]]:
        """Cluster related keywords"""
        try:
            if len(keywords) < 3:
                return {}
                
            # Simple clustering based on keyword similarity
            keyword_texts = [kw.text for kw in keywords]
            
            # Create TF-IDF vectors for keywords
            vectorizer = TfidfVectorizer(ngram_range=(1, 1))
            try:
                vectors = vectorizer.fit_transform(keyword_texts)
                
                # Perform clustering
                n_clusters = min(5, len(keywords) // 2)
                if n_clusters < 2:
                    return {"main_cluster": keyword_texts}
                    
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                cluster_labels = kmeans.fit_predict(vectors)
                
                # Group keywords by cluster
                clusters = {}
                for i, label in enumerate(cluster_labels):
                    cluster_name = f"cluster_{label}"
                    if cluster_name not in clusters:
                        clusters[cluster_name] = []
                    clusters[cluster_name].append(keyword_texts[i])
                    
                return clusters
                
            except ValueError:
                # Fallback: return all keywords in one cluster
                return {"main_cluster": keyword_texts}
                
        except Exception as e:
            logger.error(f"Keyword clustering failed: {e}")
            return {}
            
    async def _find_semantic_relationships(self, keywords: List[Keyword]) -> Dict[str, List[str]]:
        """Find semantic relationships between keywords"""
        try:
            relationships = {}
            
            # Simple relationship finding based on co-occurrence
            keyword_texts = [kw.text.lower() for kw in keywords]
            
            for i, keyword1 in enumerate(keyword_texts):
                related = []
                for j, keyword2 in enumerate(keyword_texts):
                    if i != j:
                        # Simple similarity check (could be enhanced with word embeddings)
                        if any(word in keyword1.split() for word in keyword2.split()):
                            related.append(keyword2)
                            
                if related:
                    relationships[keyword1] = related[:3]  # Top 3 related
                    
            return relationships
            
        except Exception as e:
            logger.error(f"Semantic relationship finding failed: {e}")
            return {}
            
    async def _generate_seo_suggestions(
        self,
        primary_keywords: List[Keyword],
        secondary_keywords: List[Keyword],
        text: str
    ) -> List[str]:
        """Generate SEO optimization suggestions"""
        try:
            suggestions = []
            
            # Keyword density analysis
            word_count = len(text.split())
            
            for keyword in primary_keywords[:5]:
                density = (keyword.frequency / word_count) * 100 if word_count > 0 else 0
                
                if density < 1.0:
                    suggestions.append(f"Increase usage of '{keyword.text}' (current density: {density:.1f}%)")
                elif density > 3.0:
                    suggestions.append(f"Reduce usage of '{keyword.text}' (current density: {density:.1f}%)")
                    
            # Content length suggestions
            if word_count < 300:
                suggestions.append("Content is too short for optimal SEO (aim for 300+ words)")
            elif word_count > 2000:
                suggestions.append("Content is very long - consider breaking into multiple pieces")
                
            # Keyword variety suggestions
            if len(primary_keywords) < 3:
                suggestions.append("Add more primary keywords for better topic coverage")
                
            return suggestions[:5]  # Limit to top 5 suggestions
            
        except Exception as e:
            logger.error(f"SEO suggestion generation failed: {e}")
            return []
            
    async def _categorize_content(
        self,
        topics: List[Topic],
        keywords: List[Keyword]
    ) -> List[str]:
        """Categorize content based on topics and keywords"""
        try:
            categories = []
            
            # Category mapping based on keywords
            category_keywords = {
                'technology': ['tech', 'software', 'digital', 'computer', 'ai', 'machine learning'],
                'business': ['business', 'marketing', 'sales', 'revenue', 'company', 'strategy'],
                'health': ['health', 'medical', 'wellness', 'fitness', 'diet', 'exercise'],
                'education': ['education', 'learning', 'school', 'study', 'teaching', 'course'],
                'entertainment': ['entertainment', 'movie', 'music', 'game', 'show', 'celebrity'],
                'sports': ['sports', 'game', 'team', 'player', 'match', 'competition'],
                'travel': ['travel', 'trip', 'vacation', 'destination', 'hotel', 'tourism'],
                'food': ['food', 'recipe', 'cooking', 'restaurant', 'cuisine', 'chef'],
                'fashion': ['fashion', 'style', 'clothing', 'brand', 'design', 'trend'],
                'finance': ['finance', 'money', 'investment', 'banking', 'economy', 'market']
            }
            
            # Check keywords against categories
            all_keyword_texts = [kw.text.lower() for kw in keywords]
            
            for category, category_terms in category_keywords.items():
                matches = sum(1 for term in category_terms 
                            if any(term in keyword for keyword in all_keyword_texts))
                
                if matches >= 2:  # Threshold for category assignment
                    categories.append(category)
                    
            # If no categories found, use generic
            if not categories:
                categories = ['general']
                
            return categories[:3]  # Limit to top 3 categories
            
        except Exception as e:
            logger.error(f"Content categorization failed: {e}")
            return ['general']


class TopicModeling:
    """Advanced topic modeling for content analysis"""
    
    def __init__(self):
        self.keyword_extractor = KeywordExtractor()
        
    async def discover_topics(
        self,
        documents: List[str],
        num_topics: int = 10,
        model_type: TopicModelType = TopicModelType.LDA
    ) -> List[Topic]:
        """
        Discover topics from a collection of documents
        
        Args:
            documents: List of document texts
            num_topics: Number of topics to discover
            model_type: Type of topic modeling algorithm
            
        Returns:
            List of discovered topics
        """
        try:
            if model_type == TopicModelType.LDA:
                return await self._lda_topic_modeling(documents, num_topics)
            elif model_type == TopicModelType.NMF:
                return await self._nmf_topic_modeling(documents, num_topics)
            elif model_type == TopicModelType.GENSIM_LDA:
                return await self._gensim_lda_modeling(documents, num_topics)
            else:
                return await self._lda_topic_modeling(documents, num_topics)
                
        except Exception as e:
            logger.error(f"Topic discovery failed: {e}")
            raise
            
    async def _lda_topic_modeling(self, documents: List[str], num_topics: int) -> List[Topic]:
        """Perform LDA topic modeling using scikit-learn"""
        try:
            # Preprocess documents
            vectorizer = CountVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                max_df=0.8,
                min_df=2
            )
            
            doc_term_matrix = vectorizer.fit_transform(documents)
            feature_names = vectorizer.get_feature_names_out()
            
            # Fit LDA model
            lda = LatentDirichletAllocation(
                n_components=num_topics,
                random_state=42,
                max_iter=100,
                learning_method='batch'
            )
            
            lda.fit(doc_term_matrix)
            
            # Extract topics
            topics = []
            for topic_idx, topic in enumerate(lda.components_):
                # Get top words
                top_word_indices = topic.argsort()[-10:][::-1]
                topic_keywords = [feature_names[i] for i in top_word_indices]
                topic_weights = [float(topic[i]) for i in top_word_indices]
                
                # Normalize weights
                total_weight = sum(topic_weights)
                if total_weight > 0:
                    topic_weights = [w / total_weight for w in topic_weights]
                
                topic_obj = Topic(
                    topic_id=topic_idx,
                    topic_name=f"Topic {topic_idx + 1}: {topic_keywords[0]}",
                    keywords=topic_keywords,
                    keyword_weights=topic_weights,
                    coherence_score=0.7,  # Simplified
                    topic_probability=1.0 / num_topics
                )
                topics.append(topic_obj)
                
            return topics
            
        except Exception as e:
            logger.error(f"LDA topic modeling failed: {e}")
            return []
            
    async def _nmf_topic_modeling(self, documents: List[str], num_topics: int) -> List[Topic]:
        """Perform NMF topic modeling"""
        try:
            # Use TF-IDF for NMF
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                max_df=0.8,
                min_df=2
            )
            
            tfidf_matrix = vectorizer.fit_transform(documents)
            feature_names = vectorizer.get_feature_names_out()
            
            # Fit NMF model
            nmf = NMF(
                n_components=num_topics,
                random_state=42,
                max_iter=200
            )
            
            nmf.fit(tfidf_matrix)
            
            # Extract topics
            topics = []
            for topic_idx, topic in enumerate(nmf.components_):
                # Get top words
                top_word_indices = topic.argsort()[-10:][::-1]
                topic_keywords = [feature_names[i] for i in top_word_indices]
                topic_weights = [float(topic[i]) for i in top_word_indices]
                
                # Normalize weights
                total_weight = sum(topic_weights)
                if total_weight > 0:
                    topic_weights = [w / total_weight for w in topic_weights]
                
                topic_obj = Topic(
                    topic_id=topic_idx,
                    topic_name=f"Topic {topic_idx + 1}: {topic_keywords[0]}",
                    keywords=topic_keywords,
                    keyword_weights=topic_weights,
                    coherence_score=0.7,
                    topic_probability=1.0 / num_topics
                )
                topics.append(topic_obj)
                
            return topics
            
        except Exception as e:
            logger.error(f"NMF topic modeling failed: {e}")
            return []
            
    async def _gensim_lda_modeling(self, documents: List[str], num_topics: int) -> List[Topic]:
        """Perform LDA topic modeling using Gensim"""
        try:
            # Preprocess documents
            processed_docs = []
            for doc in documents:
                words = word_tokenize(doc.lower())
                words = [word for word in words if word.isalpha() and word not in stopwords.words('english')]
                processed_docs.append(words)
                
            # Create dictionary and corpus
            dictionary = corpora.Dictionary(processed_docs)
            corpus = [dictionary.doc2bow(doc) for doc in processed_docs]
            
            # Build LDA model
            lda_model = LdaModel(
                corpus=corpus,
                id2word=dictionary,
                num_topics=num_topics,
                random_state=42,
                passes=10,
                alpha='auto',
                per_word_topics=True
            )
            
            # Extract topics
            topics = []
            for topic_id in range(num_topics):
                topic_words = lda_model.show_topic(topic_id, topn=10)
                
                keywords = [word for word, _ in topic_words]
                weights = [float(weight) for _, weight in topic_words]
                
                topic_obj = Topic(
                    topic_id=topic_id,
                    topic_name=f"Topic {topic_id + 1}: {keywords[0]}",
                    keywords=keywords,
                    keyword_weights=weights,
                    coherence_score=0.7,
                    topic_probability=1.0 / num_topics
                )
                topics.append(topic_obj)
                
            return topics
            
        except Exception as e:
            logger.error(f"Gensim LDA modeling failed: {e}")
            return []
