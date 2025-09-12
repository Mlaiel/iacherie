"""
BERT Content Analyzer for Ainflue Platform
==========================================

Advanced BERT-based content analysis for semantic SEO optimization.
Leverages transformer models for deep content understanding and optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import asyncpg
from datetime import datetime
import torch
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    BertTokenizer, BertModel, pipeline
)
from sentence_transformers import SentenceTransformer
import spacy
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import re

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Content types for BERT analysis."""
    ARTICLE = "article"
    PRODUCT_DESCRIPTION = "product_description"
    VIDEO_DESCRIPTION = "video_description"
    SOCIAL_POST = "social_post"
    EMAIL = "email"
    LANDING_PAGE = "landing_page"
    BLOG_POST = "blog_post"

class AnalysisType(Enum):
    """Types of BERT analysis."""
    SEMANTIC_SIMILARITY = "semantic_similarity"
    CONTENT_CLASSIFICATION = "content_classification"
    ENTITY_EXTRACTION = "entity_extraction"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    TOPIC_MODELING = "topic_modeling"
    READABILITY_ANALYSIS = "readability_analysis"
    INTENT_DETECTION = "intent_detection"

@dataclass
class BERTAnalysisResult:
    """BERT content analysis result."""
    analysis_id: str
    content_id: str
    content_type: ContentType
    analysis_type: AnalysisType
    semantic_embeddings: List[float]
    topics: List[Dict[str, Any]]
    entities: List[Dict[str, Any]]
    sentiment_scores: Dict[str, float]
    readability_metrics: Dict[str, float]
    intent_classification: Dict[str, float]
    similarity_scores: Dict[str, float]
    optimization_suggestions: List[str]
    confidence_score: float
    processing_time_ms: int
    created_at: datetime

@dataclass
class SemanticCluster:
    """Semantic content cluster."""
    cluster_id: str
    cluster_name: str
    content_ids: List[str]
    representative_keywords: List[str]
    semantic_center: List[float]
    coherence_score: float
    size: int
    created_at: datetime

@dataclass
class ContentSimilarity:
    """Content similarity analysis."""
    similarity_id: str
    content_id_1: str
    content_id_2: str
    semantic_similarity: float
    topic_similarity: float
    entity_similarity: float
    overall_similarity: float
    similar_aspects: List[str]
    different_aspects: List[str]
    created_at: datetime

class BERTContentAnalyzer:
    """
    Advanced BERT Content Analyzer
    
    Features:
    - Semantic content understanding
    - Topic modeling and clustering
    - Entity recognition and linking
    - Content similarity analysis
    - Intent detection and classification
    - Sentiment and emotion analysis
    - Readability optimization
    - Content gap identification
    """
    
    def __init__(self, db_pool: asyncpg.Pool, model_cache_dir: str = "/tmp/bert_models"):
        self.db_pool = db_pool
        self.model_cache_dir = model_cache_dir
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize models
        self.models = {}
        self.tokenizers = {}
        self.nlp = None
        
        # Initialize models asynchronously
        asyncio.create_task(self._initialize_models())
    
    async def _initialize_models(self):
        """Initialize BERT and related models."""
        try:
            logger.info("Initializing BERT models...")
            
            # BERT base model for general embeddings
            self.tokenizers['bert-base'] = BertTokenizer.from_pretrained('bert-base-uncased')
            self.models['bert-base'] = BertModel.from_pretrained('bert-base-uncased').to(self.device)
            
            # Sentence-BERT for semantic similarity
            self.models['sentence-bert'] = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Classification models
            self.models['sentiment'] = pipeline(
                'sentiment-analysis',
                model='cardiffnlp/twitter-roberta-base-sentiment-latest',
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Topic classification
            self.models['topic-classifier'] = pipeline(
                'zero-shot-classification',
                model='facebook/bart-large-mnli',
                device=0 if torch.cuda.is_available() else -1
            )
            
            # NER model
            self.models['ner'] = pipeline(
                'ner',
                model='dbmdz/bert-large-cased-finetuned-conll03-english',
                aggregation_strategy='simple',
                device=0 if torch.cuda.is_available() else -1
            )
            
            # spaCy for additional NLP
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not available")
            
            logger.info("BERT models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing BERT models: {e}")
    
    async def analyze_content(
        self,
        content_id: str,
        content_text: str,
        content_type: ContentType,
        analysis_types: List[AnalysisType],
        target_keywords: Optional[List[str]] = None
    ) -> BERTAnalysisResult:
        """
        Perform comprehensive BERT analysis on content.
        
        Args:
            content_id: Unique content identifier
            content_text: Content text to analyze
            content_type: Type of content
            analysis_types: Types of analysis to perform
            target_keywords: Target keywords for optimization
            
        Returns:
            BERTAnalysisResult object
        """
        try:
            start_time = datetime.utcnow()
            
            analysis_id = f"bert_analysis_{content_id}_{int(start_time.timestamp())}"
            
            # Initialize result containers
            semantic_embeddings = []
            topics = []
            entities = []
            sentiment_scores = {}
            readability_metrics = {}
            intent_classification = {}
            similarity_scores = {}
            optimization_suggestions = []
            
            # Perform requested analyses
            for analysis_type in analysis_types:
                try:
                    if analysis_type == AnalysisType.SEMANTIC_SIMILARITY:
                        semantic_embeddings = await self._generate_semantic_embeddings(content_text)
                        
                    elif analysis_type == AnalysisType.CONTENT_CLASSIFICATION:
                        topics = await self._classify_content_topics(content_text)
                        
                    elif analysis_type == AnalysisType.ENTITY_EXTRACTION:
                        entities = await self._extract_entities_bert(content_text)
                        
                    elif analysis_type == AnalysisType.SENTIMENT_ANALYSIS:
                        sentiment_scores = await self._analyze_sentiment_bert(content_text)
                        
                    elif analysis_type == AnalysisType.READABILITY_ANALYSIS:
                        readability_metrics = await self._analyze_readability_bert(content_text)
                        
                    elif analysis_type == AnalysisType.INTENT_DETECTION:
                        intent_classification = await self._detect_content_intent(content_text)
                        
                except Exception as e:
                    logger.error(f"Error in {analysis_type.value} analysis: {e}")
            
            # Calculate similarity scores if target keywords provided
            if target_keywords:
                similarity_scores = await self._calculate_keyword_similarity(
                    content_text, target_keywords, semantic_embeddings
                )
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_bert_optimization_suggestions(
                content_text, topics, entities, sentiment_scores, 
                readability_metrics, target_keywords
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_analysis_confidence(
                semantic_embeddings, topics, entities, sentiment_scores
            )
            
            # Calculate processing time
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            result = BERTAnalysisResult(
                analysis_id=analysis_id,
                content_id=content_id,
                content_type=content_type,
                analysis_type=analysis_types[0] if analysis_types else AnalysisType.SEMANTIC_SIMILARITY,
                semantic_embeddings=semantic_embeddings,
                topics=topics,
                entities=entities,
                sentiment_scores=sentiment_scores,
                readability_metrics=readability_metrics,
                intent_classification=intent_classification,
                similarity_scores=similarity_scores,
                optimization_suggestions=optimization_suggestions,
                confidence_score=confidence_score,
                processing_time_ms=processing_time_ms,
                created_at=datetime.utcnow()
            )
            
            # Store analysis result
            await self._store_bert_analysis(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing content with BERT: {e}")
            raise
    
    async def _generate_semantic_embeddings(self, content_text: str) -> List[float]:
        """Generate semantic embeddings using BERT."""
        try:
            if 'sentence-bert' not in self.models:
                logger.warning("Sentence-BERT model not available")
                return []
            
            # Clean and prepare text
            cleaned_text = self._preprocess_text(content_text)
            
            # Generate embeddings
            embeddings = self.models['sentence-bert'].encode([cleaned_text])
            
            return embeddings[0].tolist()
            
        except Exception as e:
            logger.error(f"Error generating semantic embeddings: {e}")
            return []
    
    async def _classify_content_topics(self, content_text: str) -> List[Dict[str, Any]]:
        """Classify content into topics using BERT."""
        try:
            if 'topic-classifier' not in self.models:
                logger.warning("Topic classifier not available")
                return []
            
            # Define candidate topics for creator content
            candidate_topics = [
                "entertainment", "education", "tutorial", "review", "news",
                "lifestyle", "technology", "music", "art", "photography",
                "gaming", "fitness", "food", "travel", "fashion",
                "business", "finance", "marketing", "social media"
            ]
            
            # Classify content
            result = self.models['topic-classifier'](content_text, candidate_topics)
            
            # Format results
            topics = []
            for label, score in zip(result['labels'], result['scores']):
                if score > 0.1:  # Only include confident predictions
                    topics.append({
                        'topic': label,
                        'confidence': float(score),
                        'relevance': 'high' if score > 0.7 else 'medium' if score > 0.3 else 'low'
                    })
            
            return topics
            
        except Exception as e:
            logger.error(f"Error classifying content topics: {e}")
            return []
    
    async def _extract_entities_bert(self, content_text: str) -> List[Dict[str, Any]]:
        """Extract entities using BERT NER."""
        try:
            if 'ner' not in self.models:
                logger.warning("NER model not available")
                return []
            
            # Extract entities
            ner_results = self.models['ner'](content_text)
            
            # Format entities
            entities = []
            for entity in ner_results:
                entities.append({
                    'text': entity['word'],
                    'label': entity['entity_group'],
                    'confidence': float(entity['score']),
                    'start': entity['start'],
                    'end': entity['end']
                })
            
            # Add spaCy entities if available
            if self.nlp:
                doc = self.nlp(content_text)
                for ent in doc.ents:
                    entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'confidence': 0.8,  # Default confidence for spaCy
                        'start': ent.start_char,
                        'end': ent.end_char,
                        'description': spacy.explain(ent.label_)
                    })
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    async def _analyze_sentiment_bert(self, content_text: str) -> Dict[str, float]:
        """Analyze sentiment using BERT."""
        try:
            if 'sentiment' not in self.models:
                logger.warning("Sentiment model not available")
                return {}
            
            # Analyze sentiment
            sentiment_result = self.models['sentiment'](content_text)
            
            # Process results
            sentiment_scores = {}
            for result in sentiment_result:
                sentiment_scores[result['label'].lower()] = float(result['score'])
            
            # Calculate overall sentiment
            if 'positive' in sentiment_scores and 'negative' in sentiment_scores:
                sentiment_scores['overall'] = sentiment_scores.get('positive', 0) - sentiment_scores.get('negative', 0)
            
            return sentiment_scores
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {}
    
    async def _analyze_readability_bert(self, content_text: str) -> Dict[str, float]:
        """Analyze readability using BERT-based metrics."""
        try:
            # Basic readability metrics
            sentences = content_text.split('.')
            words = content_text.split()
            
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            
            # Calculate complexity using BERT embeddings
            complexity_score = await self._calculate_semantic_complexity(content_text)
            
            return {
                'average_sentence_length': avg_sentence_length,
                'average_word_length': avg_word_length,
                'semantic_complexity': complexity_score,
                'readability_score': max(0, 100 - (avg_sentence_length * 2) - (complexity_score * 10))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing readability: {e}")
            return {}
    
    async def _detect_content_intent(self, content_text: str) -> Dict[str, float]:
        """Detect content intent using BERT classification."""
        try:
            if 'topic-classifier' not in self.models:
                logger.warning("Topic classifier not available for intent detection")
                return {}
            
            # Define intent categories
            intent_categories = [
                "inform", "entertain", "persuade", "educate", "sell",
                "review", "compare", "guide", "news", "opinion"
            ]
            
            # Classify intent
            result = self.models['topic-classifier'](content_text, intent_categories)
            
            # Format results
            intent_scores = {}
            for label, score in zip(result['labels'], result['scores']):
                intent_scores[label] = float(score)
            
            return intent_scores
            
        except Exception as e:
            logger.error(f"Error detecting content intent: {e}")
            return {}
    
    async def _calculate_keyword_similarity(
        self,
        content_text: str,
        keywords: List[str],
        content_embeddings: List[float]
    ) -> Dict[str, float]:
        """Calculate semantic similarity between content and keywords."""
        try:
            if not content_embeddings or 'sentence-bert' not in self.models:
                return {}
            
            # Generate keyword embeddings
            keyword_embeddings = self.models['sentence-bert'].encode(keywords)
            
            # Calculate similarities
            similarities = {}
            content_emb = np.array(content_embeddings).reshape(1, -1)
            
            for i, keyword in enumerate(keywords):
                keyword_emb = keyword_embeddings[i].reshape(1, -1)
                similarity = cosine_similarity(content_emb, keyword_emb)[0][0]
                similarities[keyword] = float(similarity)
            
            return similarities
            
        except Exception as e:
            logger.error(f"Error calculating keyword similarity: {e}")
            return {}
    
    async def _calculate_semantic_complexity(self, content_text: str) -> float:
        """Calculate semantic complexity using BERT."""
        try:
            if 'bert-base' not in self.models:
                return 0.5  # Default medium complexity
            
            # Tokenize text
            tokenizer = self.tokenizers['bert-base']
            model = self.models['bert-base']
            
            # Get attention weights (complexity indicator)
            inputs = tokenizer(content_text, return_tensors="pt", truncate=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = model(**inputs, output_attentions=True)
                attentions = outputs.attentions
            
            # Calculate attention complexity (variance in attention patterns)
            attention_variance = torch.var(attentions[-1]).item()
            
            # Normalize to 0-1 scale
            complexity = min(attention_variance * 10, 1.0)
            
            return complexity
            
        except Exception as e:
            logger.error(f"Error calculating semantic complexity: {e}")
            return 0.5
    
    async def _generate_bert_optimization_suggestions(
        self,
        content_text: str,
        topics: List[Dict[str, Any]],
        entities: List[Dict[str, Any]],
        sentiment_scores: Dict[str, float],
        readability_metrics: Dict[str, float],
        target_keywords: Optional[List[str]]
    ) -> List[str]:
        """Generate BERT-based optimization suggestions."""
        suggestions = []
        
        # Topic optimization
        if topics:
            top_topic = max(topics, key=lambda x: x['confidence'])
            if top_topic['confidence'] < 0.5:
                suggestions.append("Content topic focus is unclear - consider strengthening the main theme")
            
            # Check topic diversity
            if len([t for t in topics if t['confidence'] > 0.3]) > 3:
                suggestions.append("Content covers too many topics - focus on 2-3 main themes")
        
        # Entity optimization
        if entities:
            entity_types = set(e['label'] for e in entities)
            if 'PERSON' not in entity_types and 'ORG' not in entity_types:
                suggestions.append("Consider adding authoritative sources or expert mentions")
        
        # Sentiment optimization
        if sentiment_scores:
            overall_sentiment = sentiment_scores.get('overall', 0)
            if overall_sentiment < -0.3:
                suggestions.append("Content tone is quite negative - consider balancing with positive aspects")
            elif overall_sentiment > 0.8:
                suggestions.append("Content is very positive - ensure credibility with balanced perspective")
        
        # Readability optimization
        if readability_metrics:
            if readability_metrics.get('average_sentence_length', 0) > 25:
                suggestions.append("Sentences are too long - break them down for better readability")
            
            if readability_metrics.get('semantic_complexity', 0) > 0.8:
                suggestions.append("Content is semantically complex - simplify language for broader audience")
        
        # Keyword optimization
        if target_keywords:
            suggestions.append("Optimize content structure to better align with target keywords semantically")
        
        # General BERT-based suggestions
        suggestions.extend([
            "Use more specific and descriptive language for better semantic understanding",
            "Add structured data to help search engines understand content context",
            "Consider adding FAQ section to cover related semantic queries"
        ])
        
        return suggestions
    
    def _calculate_analysis_confidence(
        self,
        embeddings: List[float],
        topics: List[Dict[str, Any]],
        entities: List[Dict[str, Any]],
        sentiment_scores: Dict[str, float]
    ) -> float:
        """Calculate overall confidence score for the analysis."""
        confidence = 0.0
        factors = 0
        
        # Embeddings confidence
        if embeddings:
            confidence += 0.8
            factors += 1
        
        # Topics confidence
        if topics:
            avg_topic_confidence = sum(t['confidence'] for t in topics) / len(topics)
            confidence += avg_topic_confidence
            factors += 1
        
        # Entities confidence
        if entities:
            avg_entity_confidence = sum(e['confidence'] for e in entities) / len(entities)
            confidence += avg_entity_confidence
            factors += 1
        
        # Sentiment confidence
        if sentiment_scores:
            max_sentiment_score = max(sentiment_scores.values())
            confidence += max_sentiment_score
            factors += 1
        
        return confidence / factors if factors > 0 else 0.5
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for BERT analysis."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)]', '', text)
        
        # Limit length for BERT
        words = text.split()
        if len(words) > 400:  # Approximate token limit
            text = ' '.join(words[:400])
        
        return text.strip()
    
    async def cluster_content_semantically(
        self,
        content_items: List[Tuple[str, str]],
        num_clusters: int = 5
    ) -> List[SemanticCluster]:
        """
        Cluster content based on semantic similarity.
        
        Args:
            content_items: List of (content_id, content_text) tuples
            num_clusters: Number of clusters to create
            
        Returns:
            List of SemanticCluster objects
        """
        try:
            if 'sentence-bert' not in self.models:
                logger.warning("Sentence-BERT model not available for clustering")
                return []
            
            # Generate embeddings for all content
            content_texts = [item[1] for item in content_items]
            embeddings = self.models['sentence-bert'].encode(content_texts)
            
            # Perform clustering
            kmeans = KMeans(n_clusters=min(num_clusters, len(content_items)), random_state=42)
            cluster_labels = kmeans.fit_predict(embeddings)
            
            # Create cluster objects
            clusters = []
            for cluster_id in range(kmeans.n_clusters):
                cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
                cluster_content_ids = [content_items[i][0] for i in cluster_indices]
                
                # Calculate representative keywords
                cluster_texts = [content_items[i][1] for i in cluster_indices]
                representative_keywords = await self._extract_cluster_keywords(cluster_texts)
                
                # Calculate coherence score
                cluster_embeddings = embeddings[cluster_indices]
                coherence_score = self._calculate_cluster_coherence(cluster_embeddings)
                
                cluster = SemanticCluster(
                    cluster_id=f"cluster_{cluster_id}_{int(datetime.utcnow().timestamp())}",
                    cluster_name=f"Cluster {cluster_id + 1}",
                    content_ids=cluster_content_ids,
                    representative_keywords=representative_keywords,
                    semantic_center=kmeans.cluster_centers_[cluster_id].tolist(),
                    coherence_score=coherence_score,
                    size=len(cluster_content_ids),
                    created_at=datetime.utcnow()
                )
                
                clusters.append(cluster)
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error clustering content semantically: {e}")
            return []
    
    async def find_content_gaps(
        self,
        existing_content: List[str],
        competitor_content: List[str],
        target_topics: List[str]
    ) -> Dict[str, Any]:
        """
        Identify content gaps using BERT semantic analysis.
        
        Args:
            existing_content: List of existing content texts
            competitor_content: List of competitor content texts  
            target_topics: Target topics to analyze
            
        Returns:
            Content gap analysis results
        """
        try:
            if 'sentence-bert' not in self.models:
                logger.warning("Sentence-BERT model not available for gap analysis")
                return {}
            
            # Generate embeddings
            existing_embeddings = self.models['sentence-bert'].encode(existing_content)
            competitor_embeddings = self.models['sentence-bert'].encode(competitor_content)
            topic_embeddings = self.models['sentence-bert'].encode(target_topics)
            
            # Find gaps
            gaps = []
            opportunities = []
            
            for i, topic in enumerate(target_topics):
                topic_emb = topic_embeddings[i].reshape(1, -1)
                
                # Calculate similarity to existing content
                existing_similarities = cosine_similarity(topic_emb, existing_embeddings)
                max_existing_sim = np.max(existing_similarities) if len(existing_similarities) > 0 else 0
                
                # Calculate similarity to competitor content
                competitor_similarities = cosine_similarity(topic_emb, competitor_embeddings)
                max_competitor_sim = np.max(competitor_similarities) if len(competitor_similarities) > 0 else 0
                
                # Identify gaps and opportunities
                if max_existing_sim < 0.3:  # Low coverage in existing content
                    if max_competitor_sim > 0.6:  # High coverage by competitors
                        gaps.append({
                            'topic': topic,
                            'gap_type': 'competitive_gap',
                            'priority': 'high',
                            'existing_coverage': float(max_existing_sim),
                            'competitor_coverage': float(max_competitor_sim)
                        })
                    else:
                        opportunities.append({
                            'topic': topic,
                            'opportunity_type': 'market_opportunity',
                            'priority': 'medium',
                            'existing_coverage': float(max_existing_sim),
                            'competitor_coverage': float(max_competitor_sim)
                        })
            
            return {
                'content_gaps': gaps,
                'opportunities': opportunities,
                'analysis_date': datetime.utcnow().isoformat(),
                'recommendations': self._generate_gap_recommendations(gaps, opportunities)
            }
            
        except Exception as e:
            logger.error(f"Error finding content gaps: {e}")
            return {}
    
    async def _store_bert_analysis(self, result: BERTAnalysisResult):
        """Store BERT analysis result in database."""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO bert_content_analysis 
                    (analysis_id, content_id, content_type, analysis_type, semantic_embeddings,
                     topics, entities, sentiment_scores, readability_metrics, intent_classification,
                     similarity_scores, optimization_suggestions, confidence_score, 
                     processing_time_ms, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                """, 
                    result.analysis_id, result.content_id, result.content_type.value,
                    result.analysis_type.value, json.dumps(result.semantic_embeddings),
                    json.dumps(result.topics), json.dumps(result.entities),
                    json.dumps(result.sentiment_scores), json.dumps(result.readability_metrics),
                    json.dumps(result.intent_classification), json.dumps(result.similarity_scores),
                    json.dumps(result.optimization_suggestions), result.confidence_score,
                    result.processing_time_ms, result.created_at
                )
        except Exception as e:
            logger.error(f"Error storing BERT analysis: {e}")

# Export classes
__all__ = [
    'BERTContentAnalyzer',
    'BERTAnalysisResult',
    'SemanticCluster',
    'ContentSimilarity',
    'ContentType',
    'AnalysisType'
]