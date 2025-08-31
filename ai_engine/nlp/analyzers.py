"""Content Analyzers Module for IA Influencer Agent Platform

Advanced content analysis capabilities for sentiment analysis, topic detection,
engagement prediction, and content performance optimization for creators.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from collections import Counter, defaultdict
import re

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Result of content analysis"""    content_id: str
    analysis_type: str
    results: Dict[str, Any]
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

class ContentAnalyzer(ABC):
    """Abstract base class for content analyzers"""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        self.model_cache = {}
        self.analysis_history = []
    
    @abstractmethod
    async def analyze(self, content: str, metadata: Dict[str, Any] = None) -> AnalysisResult:
        """Analyze content and return results"""        pass
    
    def _generate_content_id(self, content: str) -> str:
        """Generate unique content ID"""        import hashlib
        return hashlib.md5(content.encode()).hexdigest()[:12]

class SentimentAnalyzer(ContentAnalyzer):
    """    Advanced sentiment analysis with emotion detection
    
    Capabilities:
    - Multi-dimensional sentiment analysis
    - Emotion detection (joy, anger, fear, sadness, surprise, disgust)
    - Sentiment intensity scoring
    - Context-aware sentiment shifts
    """    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.sentiment_lexicon = self._load_sentiment_lexicon()
        self.emotion_patterns = self._load_emotion_patterns()
    
    async def analyze(self, content: str, metadata: Dict[str, Any] = None) -> AnalysisResult:
        content_id = self._generate_content_id(content)
        
        try:
            # Basic sentiment analysis
            sentiment_scores = await self._analyze_basic_sentiment(content)
            
            # Emotion detection
            emotions = await self._detect_emotions(content)
            
            # Sentiment intensity
            intensity = await self._calculate_sentiment_intensity(content)
            
            # Context analysis
            context_sentiment = await self._analyze_contextual_sentiment(content)
            
            # Sentiment shifts detection
            sentiment_shifts = await self._detect_sentiment_shifts(content)
            
            results = {
                'overall_sentiment': sentiment_scores,
                'emotions': emotions,
                'intensity': intensity,
                'contextual_sentiment': context_sentiment,
                'sentiment_shifts': sentiment_shifts,
                'engagement_prediction': self._predict_engagement_from_sentiment(sentiment_scores, emotions),
                'brand_alignment': self._assess_brand_sentiment_alignment(sentiment_scores)
            }
            
            confidence = self._calculate_sentiment_confidence(results)
            
            return AnalysisResult(
                content_id=content_id,
                analysis_type='sentiment',
                results=results,
                confidence_score=confidence,
                metadata={'content_length': len(content), 'word_count': len(content.split())}
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return AnalysisResult(
                content_id=content_id,
                analysis_type='sentiment',
                results={'error': str(e)},
                confidence_score=0.0
            )
    
    async def _analyze_basic_sentiment(self, content: str) -> Dict[str, float]:
        """Perform basic sentiment analysis"""        words = content.lower().split()
        
        positive_score = 0
        negative_score = 0
        neutral_count = 0
        
        for word in words:
            if word in self.sentiment_lexicon:
                score = self.sentiment_lexicon[word]
                if score > 0:
                    positive_score += score
                elif score < 0:
                    negative_score += abs(score)
                else:
                    neutral_count += 1
            else:
                neutral_count += 1
        
        total_words = len(words)
        if total_words == 0:
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
        
        positive_norm = positive_score / total_words
        negative_norm = negative_score / total_words
        neutral_norm = neutral_count / total_words
        
        # Normalize to sum to 1
        total = positive_norm + negative_norm + neutral_norm
        if total > 0:
            return {
                'positive': positive_norm / total,
                'negative': negative_norm / total,
                'neutral': neutral_norm / total
            }
        
        return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
    
    async def _detect_emotions(self, content: str) -> Dict[str, float]:
        """Detect emotions in content"""        emotions = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                score += matches
            
            # Normalize by content length
            emotions[emotion] = score / max(len(content.split()), 1)
        
        return emotions
    
    async def _calculate_sentiment_intensity(self, content: str) -> Dict[str, float]:
        """Calculate sentiment intensity"""        # Intensity indicators
        intensifiers = ['very', 'extremely', 'incredibly', 'absolutely', 'completely', 'totally']
        diminishers = ['slightly', 'somewhat', 'fairly', 'rather', 'quite']
        
        words = content.lower().split()
        
        intensifier_count = sum(1 for word in words if word in intensifiers)
        diminisher_count = sum(1 for word in words if word in diminishers)
        
        # Punctuation intensity
        exclamation_count = content.count('!')
        caps_count = sum(1 for char in content if char.isupper())
        
        base_intensity = 0.5  # Neutral baseline
        
        # Adjust based on intensifiers and diminishers
        intensity_boost = (intensifier_count - diminisher_count) * 0.1
        punctuation_boost = min(0.3, exclamation_count * 0.05)
        caps_boost = min(0.2, caps_count / max(len(content), 1))
        
        final_intensity = max(0.0, min(1.0, base_intensity + intensity_boost + punctuation_boost + caps_boost))
        
        return {
            'overall_intensity': final_intensity,
            'intensifiers': intensifier_count,
            'diminishers': diminisher_count,
            'punctuation_emphasis': exclamation_count,
            'caps_usage': caps_count
        }
    
    async def _analyze_contextual_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment in different contexts"""        sentences = content.split('.')
        sentence_sentiments = []
        
        for sentence in sentences:
            if sentence.strip():
                sent_sentiment = await self._analyze_basic_sentiment(sentence)
                sentence_sentiments.append(sent_sentiment)
        
        if not sentence_sentiments:
            return {'error': 'No sentences to analyze'}
        
        # Calculate sentiment progression
        sentiment_progression = []
        for sent in sentence_sentiments:
            # Convert to single sentiment score (-1 to 1)
            score = sent['positive'] - sent['negative']
            sentiment_progression.append(score)
        
        return {
            'sentence_count': len(sentence_sentiments),
            'sentiment_progression': sentiment_progression,
            'sentiment_variance': float(np.var(sentiment_progression)) if sentiment_progression else 0.0,
            'sentiment_trend': self._calculate_sentiment_trend(sentiment_progression)
        }
    
    async def _detect_sentiment_shifts(self, content: str) -> List[Dict[str, Any]]:
        """Detect sentiment shifts in content"""        sentences = content.split('.')
        shifts = []
        
        if len(sentences) < 2:
            return shifts
        
        prev_sentiment = None
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                current_sentiment = await self._analyze_basic_sentiment(sentence)
                
                if prev_sentiment is not None:
                    # Calculate sentiment change
                    prev_score = prev_sentiment['positive'] - prev_sentiment['negative']
                    current_score = current_sentiment['positive'] - current_sentiment['negative']
                    
                    change = current_score - prev_score
                    
                    # Detect significant shifts
                    if abs(change) > 0.3:  # Threshold for significant shift
                        shifts.append({
                            'position': i,
                            'direction': 'positive' if change > 0 else 'negative',
                            'magnitude': abs(change),
                            'context': sentence.strip()[:100]  # First 100 chars
                        })
                
                prev_sentiment = current_sentiment
        
        return shifts
    
    def _load_sentiment_lexicon(self) -> Dict[str, float]:
        """Load sentiment lexicon (simplified version)"""        # In production, load from comprehensive sentiment lexicon
        return {
            # Positive words
            'love': 1.0, 'amazing': 0.9, 'great': 0.8, 'good': 0.6, 'nice': 0.5,
            'excellent': 1.0, 'fantastic': 0.9, 'wonderful': 0.8, 'beautiful': 0.7,
            'perfect': 1.0, 'awesome': 0.9, 'brilliant': 0.8, 'outstanding': 0.9,
            
            # Negative words
            'hate': -1.0, 'terrible': -0.9, 'bad': -0.6, 'awful': -0.8, 'horrible': -0.9,
            'disgusting': -0.9, 'annoying': -0.5, 'frustrating': -0.6, 'disappointing': -0.7,
            'worst': -1.0, 'useless': -0.8, 'stupid': -0.7, 'ridiculous': -0.6,
            
            # Neutral words
            'okay': 0.1, 'fine': 0.2, 'average': 0.0, 'normal': 0.0
        }
    
    def _load_emotion_patterns(self) -> Dict[str, List[str]]:
        """Load emotion detection patterns"""        return {
            'joy': [r'\b(happy|joy|excited|thrilled|delighted|cheerful)\b', r':\)|😊|😄|😃'],
            'anger': [r'\b(angry|mad|furious|irritated|annoyed)\b', r'😠|😡|🤬'],
            'fear': [r'\b(scared|afraid|worried|anxious|nervous)\b', r'😰|😱|😨'],
            'sadness': [r'\b(sad|depressed|upset|disappointed|heartbroken)\b', r'😢|😭|😞'],
            'surprise': [r'\b(surprised|shocked|amazed|astonished)\b', r'😲|😮|😯'],
            'disgust': [r'\b(disgusted|revolted|sick|gross)\b', r'🤮|😷|🤢']
        }
    
    def _predict_engagement_from_sentiment(self, sentiment: Dict[str, float], emotions: Dict[str, float]) -> Dict[str, float]:
        """Predict engagement based on sentiment and emotions"""        # High engagement emotions
        engagement_emotions = ['joy', 'anger', 'surprise']
        
        engagement_score = 0.0
        
        # Strong positive or negative sentiment tends to drive engagement
        sentiment_score = sentiment['positive'] - sentiment['negative']
        engagement_score += abs(sentiment_score) * 0.5
        
        # Specific emotions that drive engagement
        for emotion in engagement_emotions:
            if emotion in emotions:
                engagement_score += emotions[emotion] * 0.3
        
        return {
            'predicted_engagement': min(1.0, engagement_score),
            'engagement_factors': self._identify_engagement_factors(sentiment, emotions)
        }
    
    def _assess_brand_sentiment_alignment(self, sentiment: Dict[str, float]) -> Dict[str, Any]:
        """Assess sentiment alignment with brand safety"""        positive_ratio = sentiment['positive']
        negative_ratio = sentiment['negative']
        
        # Brand-safe content typically has neutral to positive sentiment
        if positive_ratio > 0.6:
            alignment = 'positive_brand_safe'
            score = 0.9
        elif negative_ratio > 0.6:
            alignment = 'negative_risk'
            score = 0.3
        else:
            alignment = 'neutral_safe'
            score = 0.7
        
        return {
            'alignment_category': alignment,
            'brand_safety_score': score,
            'recommendation': self._get_brand_recommendation(alignment)
        }
    
    def _calculate_sentiment_confidence(self, results: Dict[str, Any]) -> float:
        """Calculate confidence in sentiment analysis"""        # Factors that affect confidence
        confidence_factors = []
        
        # Strong sentiment signals increase confidence
        sentiment = results['overall_sentiment']
        max_sentiment = max(sentiment['positive'], sentiment['negative'], sentiment['neutral'])
        confidence_factors.append(max_sentiment)
        
        # Consistent emotions increase confidence
        emotions = results['emotions']
        if emotions:
            emotion_consistency = 1.0 - np.std(list(emotions.values()))
            confidence_factors.append(max(0.0, emotion_consistency))
        
        # Low sentiment variance increases confidence
        if 'contextual_sentiment' in results and 'sentiment_variance' in results['contextual_sentiment']:
            variance = results['contextual_sentiment']['sentiment_variance']
            variance_confidence = max(0.0, 1.0 - variance)
            confidence_factors.append(variance_confidence)
        
        return np.mean(confidence_factors) if confidence_factors else 0.5
    
    def _calculate_sentiment_trend(self, progression: List[float]) -> str:
        """Calculate overall sentiment trend"""        if len(progression) < 2:
            return 'stable'
        
        # Calculate linear trend
        x = np.arange(len(progression))
        slope = np.polyfit(x, progression, 1)[0]
        
        if slope > 0.1:
            return 'improving'
        elif slope < -0.1:
            return 'declining'
        else:
            return 'stable'
    
    def _identify_engagement_factors(self, sentiment: Dict[str, float], emotions: Dict[str, float]) -> List[str]:
        """Identify factors that drive engagement"""        factors = []
        
        if sentiment['positive'] > 0.7:
            factors.append('strong_positive_sentiment')
        if sentiment['negative'] > 0.7:
            factors.append('strong_negative_sentiment')
        
        for emotion, score in emotions.items():
            if score > 0.3:
                factors.append(f'high_{emotion}')
        
        return factors
    
    def _get_brand_recommendation(self, alignment: str) -> str:
        """Get brand safety recommendation"""        recommendations = {
            'positive_brand_safe': 'Excellent for brand campaigns and partnerships',
            'negative_risk': 'Review content for brand safety concerns',
            'neutral_safe': 'Safe for most brand partnerships with minor optimization'
        }
        return recommendations.get(alignment, 'Requires detailed review')

class TopicAnalyzer(ContentAnalyzer):
    """    Advanced topic modeling and content categorization
    
    Capabilities:
    - Latent Dirichlet Allocation (LDA) topic modeling
    - Keyword extraction and importance scoring
    - Content categorization for influencer niches
    - Topic trend analysis
    """    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.vectorizer = None
        self.topic_model = None
        self.influencer_categories = self._load_influencer_categories()
        self.trending_topics = {}
    
    async def analyze(self, content: str, metadata: Dict[str, Any] = None) -> AnalysisResult:
        content_id = self._generate_content_id(content)
        
        try:
            # Extract keywords
            keywords = await self._extract_keywords(content)
            
            # Topic modeling
            topics = await self._extract_topics(content)
            
            # Content categorization
            categories = await self._categorize_content(content)
            
            # Trend analysis
            trend_analysis = await self._analyze_trends(content, keywords)
            
            # Content-topic fit analysis
            topic_fit = await self._analyze_topic_fit(content, topics)
            
            results = {
                'keywords': keywords,
                'topics': topics,
                'categories': categories,
                'trend_analysis': trend_analysis,
                'topic_fit': topic_fit,
                'content_niche': self._determine_content_niche(categories, keywords),
                'collaboration_opportunities': self._identify_collaboration_opportunities(categories, topics)
            }
            
            confidence = self._calculate_topic_confidence(results)
            
            return AnalysisResult(
                content_id=content_id,
                analysis_type='topic',
                results=results,
                confidence_score=confidence,
                metadata={'content_length': len(content), 'word_count': len(content.split())}
            )
            
        except Exception as e:
            logger.error(f"Topic analysis failed: {str(e)}")
            return AnalysisResult(
                content_id=content_id,
                analysis_type='topic',
                results={'error': str(e)},
                confidence_score=0.0
            )
    
    async def _extract_keywords(self, content: str) -> Dict[str, Any]:
        """Extract and score keywords"""        # Initialize vectorizer if not exists
        if self.vectorizer is None:
            self.vectorizer = TfidfVectorizer(
                max_features=100,
                ngram_range=(1, 3),
                stop_words='english',
                lowercase=True
            )
        
        # Handle single document
        try:
            tfidf_matrix = self.vectorizer.fit_transform([content])
            feature_names = self.vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords with scores
            keyword_scores = list(zip(feature_names, tfidf_scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Filter out zero scores
            top_keywords = [(kw, float(score)) for kw, score in keyword_scores if score > 0][:20]
            
            return {
                'top_keywords': top_keywords,
                'keyword_count': len(top_keywords),
                'keyword_density': self._calculate_keyword_density(content, [kw[0] for kw in top_keywords])
            }
            
        except Exception as e:
            logger.warning(f"Keyword extraction failed: {str(e)}")
            # Fallback to simple word frequency
            return self._simple_keyword_extraction(content)
    
    async def _extract_topics(self, content: str) -> Dict[str, Any]:
        """Extract topics using LDA"""        try:
            # Prepare text
            documents = content.split('.')  # Split into sentences for better topic modeling
            documents = [doc.strip() for doc in documents if doc.strip()]
            
            if len(documents) < 2:
                return {'topics': [], 'message': 'Insufficient content for topic modeling'}
            
            # Vectorize
            vectorizer = TfidfVectorizer(
                max_features=50,
                ngram_range=(1, 2),
                stop_words='english'
            )
            
            doc_term_matrix = vectorizer.fit_transform(documents)
            
            # LDA topic modeling
            n_topics = min(3, len(documents))  # Adaptive number of topics
            lda = LatentDirichletAllocation(
                n_components=n_topics,
                random_state=42,
                max_iter=100
            )
            
            lda.fit(doc_term_matrix)
            
            # Extract topics
            feature_names = vectorizer.get_feature_names_out()
            topics = []
            
            for topic_idx, topic in enumerate(lda.components_):
                top_words_idx = topic.argsort()[-10:][::-1]
                top_words = [feature_names[i] for i in top_words_idx]
                topic_weights = [float(topic[i]) for i in top_words_idx]
                
                topics.append({
                    'topic_id': topic_idx,
                    'words': top_words,
                    'weights': topic_weights,
                    'coherence_score': self._calculate_topic_coherence(top_words, content)
                })
            
            return {
                'topics': topics,
                'num_topics': n_topics,
                'topic_distribution': self._get_document_topic_distribution(lda, doc_term_matrix)
            }
            
        except Exception as e:
            logger.warning(f"Topic modeling failed: {str(e)}")
            return {'topics': [], 'error': str(e)}
    
    async def _categorize_content(self, content: str) -> Dict[str, Any]:
        """Categorize content into influencer niches"""        content_lower = content.lower()
        category_scores = {}
        
        for category, keywords in self.influencer_categories.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in content_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            # Normalize by content length
            normalized_score = score / max(len(content.split()), 1)
            
            if normalized_score > 0:
                category_scores[category] = {
                    'score': float(normalized_score),
                    'matched_keywords': matched_keywords,
                    'keyword_count': len(matched_keywords)
                }
        
        # Determine primary category
        primary_category = max(category_scores.keys(), key=lambda x: category_scores[x]['score']) if category_scores else 'general'
        
        return {
            'category_scores': category_scores,
            'primary_category': primary_category,
            'confidence': category_scores.get(primary_category, {}).get('score', 0.0) if category_scores else 0.0,
            'multi_category': len(category_scores) > 1
        }
    
    async def _analyze_trends(self, content: str, keywords: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trending topics and keywords"""        # Simple trend analysis based on current trending topics
        trending_keywords = []
        seasonal_relevance = {}
        
        # Check if keywords match current trends
        for keyword, score in keywords.get('top_keywords', []):
            if keyword in self.trending_topics:
                trending_keywords.append({
                    'keyword': keyword,
                    'trend_score': self.trending_topics[keyword],
                    'content_score': score
                })
        
        # Seasonal relevance (simplified)
        current_month = datetime.now().month
        seasonal_keywords = self._get_seasonal_keywords(current_month)
        
        for seasonal_kw in seasonal_keywords:
            if seasonal_kw in content.lower():
                seasonal_relevance[seasonal_kw] = 'high'
        
        return {
            'trending_keywords': trending_keywords,
            'seasonal_relevance': seasonal_relevance,
            'trend_alignment_score': self._calculate_trend_alignment(trending_keywords),
            'virality_potential': self._assess_virality_potential(content, trending_keywords)
        }
    
    async def _analyze_topic_fit(self, content: str, topics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how well content fits identified topics"""        if not topics.get('topics'):
            return {'fit_score': 0.0, 'analysis': 'No topics identified'}
        
        content_words = set(content.lower().split())
        topic_fits = []
        
        for topic in topics['topics']:
            topic_words = set(topic['words'])
            
            # Calculate overlap
            overlap = len(content_words.intersection(topic_words))
            coverage = overlap / len(topic_words) if topic_words else 0
            
            topic_fits.append({
                'topic_id': topic['topic_id'],
                'fit_score': float(coverage),
                'word_overlap': overlap,
                'coherence': topic.get('coherence_score', 0.0)
            })
        
        # Overall fit score
        avg_fit = np.mean([tf['fit_score'] for tf in topic_fits]) if topic_fits else 0.0
        
        return {
            'overall_fit_score': float(avg_fit),
            'topic_fits': topic_fits,
            'best_fitting_topic': max(topic_fits, key=lambda x: x['fit_score']) if topic_fits else None,
            'content_coherence': self._assess_content_coherence(topic_fits)
        }
    
    def _load_influencer_categories(self) -> Dict[str, List[str]]:
        """Load influencer category keywords"""        return {
            'lifestyle': ['lifestyle', 'daily', 'routine', 'life', 'living', 'home', 'family', 'personal'],
            'fashion': ['fashion', 'style', 'outfit', 'clothing', 'designer', 'brand', 'trendy', 'wardrobe'],
            'beauty': ['beauty', 'makeup', 'skincare', 'cosmetics', 'hair', 'nails', 'spa', 'treatment'],
            'fitness': ['fitness', 'workout', 'exercise', 'gym', 'health', 'training', 'muscle', 'cardio'],
            'food': ['food', 'recipe', 'cooking', 'chef', 'restaurant', 'meal', 'nutrition', 'diet'],
            'travel': ['travel', 'trip', 'vacation', 'destination', 'adventure', 'explore', 'journey'],
            'technology': ['tech', 'technology', 'gadget', 'software', 'app', 'digital', 'innovation'],
            'gaming': ['gaming', 'game', 'player', 'stream', 'esports', 'console', 'pc', 'mobile'],
            'music': ['music', 'song', 'artist', 'album', 'concert', 'performance', 'instrument'],
            'business': ['business', 'entrepreneur', 'startup', 'marketing', 'success', 'money', 'finance'],
            'education': ['education', 'learning', 'teaching', 'student', 'course', 'knowledge', 'skill'],
            'parenting': ['parenting', 'kids', 'children', 'family', 'baby', 'mom', 'dad', 'parent']
        }
    
    def _simple_keyword_extraction(self, content: str) -> Dict[str, Any]:
        """Fallback simple keyword extraction"""        words = content.lower().split()
        
        # Remove stop words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count frequency
        word_freq = Counter(meaningful_words)
        top_keywords = [(word, freq) for word, freq in word_freq.most_common(20)]
        
        return {
            'top_keywords': top_keywords,
            'keyword_count': len(top_keywords),
            'keyword_density': len(meaningful_words) / len(words) if words else 0
        }
    
    def _calculate_keyword_density(self, content: str, keywords: List[str]) -> Dict[str, float]:
        """Calculate keyword density metrics"""        words = content.lower().split()
        densities = {}
        
        for keyword in keywords:
            keyword_count = content.lower().count(keyword.lower())
            densities[keyword] = keyword_count / len(words) if words else 0
        
        return densities
    
    def _calculate_topic_coherence(self, topic_words: List[str], content: str) -> float:
        """Calculate topic coherence score"""        content_words = set(content.lower().split())
        topic_word_set = set(topic_words)
        
        # Simple coherence based on word co-occurrence
        overlap = len(topic_word_set.intersection(content_words))
        coherence = overlap / len(topic_word_set) if topic_word_set else 0
        
        return float(coherence)
    
    def _get_document_topic_distribution(self, lda_model, doc_term_matrix) -> List[Dict[str, float]]:
        """Get topic distribution for documents"""        doc_topic_dist = lda_model.transform(doc_term_matrix)
        
        distributions = []
        for doc_dist in doc_topic_dist:
            doc_topics = {}
            for topic_idx, prob in enumerate(doc_dist):
                doc_topics[f'topic_{topic_idx}'] = float(prob)
            distributions.append(doc_topics)
        
        return distributions
    
    def _determine_content_niche(self, categories: Dict[str, Any], keywords: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the specific niche of the content"""        primary_category = categories.get('primary_category', 'general')
        confidence = categories.get('confidence', 0.0)
        
        # Sub-niche detection based on keywords
        sub_niches = self._detect_sub_niches(primary_category, keywords.get('top_keywords', []))
        
        return {
            'primary_niche': primary_category,
            'confidence': confidence,
            'sub_niches': sub_niches,
            'niche_specificity': self._calculate_niche_specificity(categories, keywords)
        }
    
    def _identify_collaboration_opportunities(self, categories: Dict[str, Any], topics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential collaboration opportunities"""        opportunities = []
        primary_category = categories.get('primary_category', 'general')
        
        # Define collaboration mappings
        collaboration_mapping = {
            'fashion': ['beauty', 'lifestyle', 'photography'],
            'beauty': ['fashion', 'lifestyle', 'health'],
            'fitness': ['health', 'nutrition', 'lifestyle'],
            'food': ['lifestyle', 'health', 'travel'],
            'travel': ['photography', 'lifestyle', 'culture'],
            'technology': ['gaming', 'education', 'business'],
            'music': ['entertainment', 'lifestyle', 'events']
        }
        
        related_niches = collaboration_mapping.get(primary_category, [])
        
        for niche in related_niches:
            opportunities.append({
                'collaboration_type': f'{primary_category}-{niche}',
                'potential_score': self._calculate_collaboration_potential(categories, niche),
                'suggested_content': self._suggest_collaboration_content(primary_category, niche)
            })
        
        return opportunities
    
    def _get_seasonal_keywords(self, month: int) -> List[str]:
        """Get seasonal keywords for the given month"""        seasonal_mapping = {
            12: ['christmas', 'holiday', 'winter', 'new year', 'gift'],
            1: ['new year', 'resolution', 'fresh start', 'winter'],
            2: ['valentine', 'love', 'romance', 'winter'],
            3: ['spring', 'fresh', 'renewal', 'march'],
            4: ['spring', 'easter', 'bloom', 'april'],
            5: ['spring', 'mother day', 'flower', 'may'],
            6: ['summer', 'vacation', 'father day', 'june'],
            7: ['summer', 'vacation', 'beach', 'july'],
            8: ['summer', 'vacation', 'back to school', 'august'],
            9: ['fall', 'autumn', 'school', 'september'],
            10: ['fall', 'autumn', 'halloween', 'october'],
            11: ['thanksgiving', 'gratitude', 'fall', 'november']
        }
        
        return seasonal_mapping.get(month, [])
    
    def _calculate_trend_alignment(self, trending_keywords: List[Dict[str, Any]]) -> float:
        """Calculate alignment with current trends"""        if not trending_keywords:
            return 0.0
        
        total_alignment = sum(kw['trend_score'] * kw['content_score'] for kw in trending_keywords)
        return min(1.0, total_alignment / len(trending_keywords))
    
    def _assess_virality_potential(self, content: str, trending_keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess potential for viral content"""        viral_indicators = {
            'trending_alignment': len(trending_keywords) > 0,
            'emotional_triggers': self._has_emotional_triggers(content),
            'shareability': self._assess_shareability(content),
            'controversy_potential': self._assess_controversy_potential(content)
        }
        
        # Calculate overall virality score
        score_weights = {
            'trending_alignment': 0.3,
            'emotional_triggers': 0.3,
            'shareability': 0.25,
            'controversy_potential': 0.15
        }
        
        virality_score = sum(
            score_weights[factor] * (1.0 if indicator else 0.0)
            for factor, indicator in viral_indicators.items()
        )
        
        return {
            'virality_score': virality_score,
            'viral_indicators': viral_indicators,
            'recommendation': self._get_virality_recommendation(virality_score)
        }
    
    def _assess_content_coherence(self, topic_fits: List[Dict[str, Any]]) -> str:
        """Assess overall content coherence"""        if not topic_fits:
            return 'unclear'
        
        avg_coherence = np.mean([tf['coherence'] for tf in topic_fits])
        
        if avg_coherence > 0.7:
            return 'high'
        elif avg_coherence > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _detect_sub_niches(self, primary_category: str, keywords: List[Tuple[str, float]]) -> List[str]:
        """Detect sub-niches within primary category"""        sub_niche_mapping = {
            'fashion': ['streetwear', 'luxury', 'sustainable', 'vintage'],
            'beauty': ['skincare', 'makeup', 'haircare', 'natural'],
            'fitness': ['bodybuilding', 'yoga', 'running', 'crossfit'],
            'food': ['vegan', 'baking', 'healthy', 'international']
        }
        
        sub_niches = []
        category_sub_niches = sub_niche_mapping.get(primary_category, [])
        
        keyword_text = ' '.join([kw[0] for kw in keywords])
        
        for sub_niche in category_sub_niches:
            if sub_niche in keyword_text:
                sub_niches.append(sub_niche)
        
        return sub_niches
    
    def _calculate_niche_specificity(self, categories: Dict[str, Any], keywords: Dict[str, Any]) -> float:
        """Calculate how specific the content is to its niche"""        category_scores = categories.get('category_scores', {})
        
        if not category_scores:
            return 0.0
        
        # High specificity = high score in one category, low in others
        scores = [cat['score'] for cat in category_scores.values()]
        max_score = max(scores)
        score_variance = np.var(scores)
        
        # Higher variance and higher max score = more specific
        specificity = (max_score * score_variance) if len(scores) > 1 else max_score
        
        return min(1.0, specificity)
    
    def _calculate_collaboration_potential(self, categories: Dict[str, Any], target_niche: str) -> float:
        """Calculate potential for collaboration with target niche"""        # Simple scoring based on category overlap and complementarity
        category_scores = categories.get('category_scores', {})
        
        if target_niche in category_scores:
            return category_scores[target_niche]['score']
        
        # Complementarity scoring for non-overlapping niches
        complementarity_scores = {
            'fashion-beauty': 0.8,
            'fitness-health': 0.9,
            'food-lifestyle': 0.7,
            'travel-photography': 0.8
        }
        
        primary = categories.get('primary_category', '')
        collab_key = f"{primary}-{target_niche}"
        reverse_key = f"{target_niche}-{primary}"
        
        return complementarity_scores.get(collab_key, complementarity_scores.get(reverse_key, 0.5))
    
    def _suggest_collaboration_content(self, primary_niche: str, target_niche: str) -> List[str]:
        """Suggest collaboration content ideas"""        collaboration_ideas = {
            'fashion-beauty': ['makeup tutorials with outfit coordination', 'seasonal style and beauty trends'],
            'fitness-health': ['workout nutrition guides', 'healthy lifestyle challenges'],
            'food-lifestyle': ['home cooking lifestyle content', 'healthy meal prep routines'],
            'travel-photography': ['destination photography guides', 'travel photo challenges']
        }
        
        collab_key = f"{primary_niche}-{target_niche}"
        reverse_key = f"{target_niche}-{primary_niche}"
        
        return collaboration_ideas.get(collab_key, collaboration_ideas.get(reverse_key, ['cross-niche content collaboration']))
    
    def _has_emotional_triggers(self, content: str) -> bool:
        """Check if content has emotional triggers"""        emotional_triggers = [
            'amazing', 'incredible', 'shocking', 'unbelievable',
            'secret', 'revealed', 'exposed', 'truth',
            'love', 'hate', 'fear', 'joy'
        ]
        
        content_lower = content.lower()
        return any(trigger in content_lower for trigger in emotional_triggers)
    
    def _assess_shareability(self, content: str) -> bool:
        """Assess content shareability"""        shareable_indicators = [
            'tip', 'hack', 'guide', 'how to', 'tutorial',
            'share', 'tag', 'comment', 'thoughts',
            'opinion', 'experience', 'story'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in shareable_indicators)
    
    def _assess_controversy_potential(self, content: str) -> bool:
        """Assess potential for controversial content"""        controversial_indicators = [
            'controversial', 'debate', 'argue', 'disagree',
            'wrong', 'right', 'opinion', 'unpopular'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in controversial_indicators)
    
    def _get_virality_recommendation(self, score: float) -> str:
        """Get recommendation based on virality score"""        if score > 0.7:
            return "High viral potential - optimize for maximum reach"
        elif score > 0.4:
            return "Moderate viral potential - consider trending hashtags"
        else:
            return "Low viral potential - focus on niche audience engagement"
    
    def _calculate_topic_confidence(self, results: Dict[str, Any]) -> float:
        """Calculate confidence in topic analysis"""        confidence_factors = []
        
        # Keyword extraction confidence
        keywords = results.get('keywords', {})
        if keywords.get('keyword_count', 0) > 5:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.4)
        
        # Topic modeling confidence
        topics = results.get('topics', {})
        if topics.get('topics') and len(topics['topics']) > 0:
            avg_coherence = np.mean([t.get('coherence_score', 0) for t in topics['topics']])
            confidence_factors.append(avg_coherence)
        
        # Categorization confidence
        categories = results.get('categories', {})
        if categories.get('confidence', 0) > 0.3:
            confidence_factors.append(categories['confidence'])
        else:
            confidence_factors.append(0.3)
        
        return np.mean(confidence_factors) if confidence_factors else 0.5

# Utility functions for quick analysis
async def quick_sentiment_analysis(content: str) -> Dict[str, Any]:
    """Quick sentiment analysis"""    analyzer = SentimentAnalyzer()
    result = await analyzer.analyze(content)
    return result.results

async def quick_topic_analysis(content: str) -> Dict[str, Any]:
    """Quick topic analysis"""    analyzer = TopicAnalyzer()
    result = await analyzer.analyze(content)
    return result.results

# Analysis pipeline
class ContentAnalysisPipeline:
    """Pipeline for comprehensive content analysis"""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.analyzers = {
            'sentiment': SentimentAnalyzer(config),
            'topic': TopicAnalyzer(config)
        }
    
    async def analyze_comprehensive(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, AnalysisResult]:
        """Perform comprehensive analysis"""        results = {}
        
        tasks = [
            (name, analyzer.analyze(content, metadata))
            for name, analyzer in self.analyzers.items()
        ]
        
        # Run analyses in parallel
        analysis_results = await asyncio.gather(
            *[task[1] for task in tasks],
            return_exceptions=True
        )
        
        # Compile results
        for i, (name, _) in enumerate(tasks):
            result = analysis_results[i]
            if isinstance(result, Exception):
                logger.error(f"Analysis {name} failed: {str(result)}")
                # Create error result
                results[name] = AnalysisResult(
                    content_id=self.analyzers[name]._generate_content_id(content),
                    analysis_type=name,
                    results={'error': str(result)},
                    confidence_score=0.0
                )
            else:
                results[name] = result
        
        return results
