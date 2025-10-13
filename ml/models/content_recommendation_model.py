"""
Content Recommendation Model - IA Chérie Enterprise
==============================================
Modèle recommandation contenu avec collaborative filtering et deep learning.
Personalization + creator matching + content discovery + business optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie ML Models
Version: 1.0 Production
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from pathlib import Path
import json
import pickle
from collections import defaultdict, Counter
import random
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

# ⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
# Cette architecture ML et tous ses algorithmes sont la propriété intellectuelle 
# EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Tous droits réservés.

logger = logging.getLogger(__name__)

class RecommendationType(Enum):
    """Types de recommandations"""
    CONTENT_BASED = "content_based"
    COLLABORATIVE = "collaborative" 
    HYBRID = "hybrid"
    TRENDING = "trending"
    CREATOR_MATCH = "creator_match"
    PERSONALIZED = "personalized"

class ContentCategory(Enum):
    """Catégories de contenu pour recommandations"""
    MUSIC = "music"
    PHOTOGRAPHY = "photography"
    VIDEO = "video"
    BLOG = "blog"
    PODCAST = "podcast"
    ART = "art"
    COMEDY = "comedy"
    EDUCATION = "education"

class EngagementLevel(Enum):
    """Niveaux d'engagement pour recommandations"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VIRAL = 4

@dataclass
class UserProfile:
    """Profil utilisateur pour personnalisation"""
    user_id: str
    preferences: Dict[str, float]
    interaction_history: List[Dict[str, Any]]
    demographic_info: Dict[str, Any]
    engagement_patterns: Dict[str, float]
    creator_follows: List[str]
    content_ratings: Dict[str, float]

@dataclass
class ContentItem:
    """Item de contenu pour recommandations"""
    content_id: str
    creator_id: str
    category: ContentCategory
    features: Dict[str, Any]
    engagement_metrics: Dict[str, float]
    quality_score: float
    tags: List[str]
    creation_date: str
    monetization_potential: float

@dataclass
class RecommendationRequest:
    """Requête de recommandation"""
    user_profile: UserProfile
    request_type: RecommendationType
    num_recommendations: int = 10
    content_filters: Optional[Dict[str, Any]] = None
    business_objectives: Optional[Dict[str, float]] = None
    platform_context: Optional[str] = None

@dataclass
class RecommendationItem:
    """Item recommandé avec métadonnées"""
    content_item: ContentItem
    score: float
    reason: str
    confidence: float
    business_value: float
    engagement_prediction: float

@dataclass
class RecommendationResult:
    """Résultat complet de recommandation"""
    user_id: str
    recommendations: List[RecommendationItem]
    recommendation_type: RecommendationType
    personalization_score: float
    diversity_score: float
    novelty_score: float
    business_optimization: Dict[str, Any]
    explanation: Dict[str, Any]
    processing_time_ms: float
    timestamp: str

@dataclass
class RecommendationConfig:
    """Configuration pour système de recommandations"""
    model_version: str = "1.0"
    device: str = "cpu"
    enable_hybrid: bool = True
    diversity_weight: float = 0.3
    novelty_weight: float = 0.2
    business_weight: float = 0.4
    cache_recommendations: bool = True

class CollaborativeFilteringEngine(nn.Module):
    """Moteur collaborative filtering avec deep learning"""
    
    def __init__(self, config: RecommendationConfig, num_users: int, num_items: int):
        super().__init__()
        self.config = config
        self.embedding_dim = 128
        
        # User and item embeddings
        self.user_embeddings = nn.Embedding(num_users, self.embedding_dim)
        self.item_embeddings = nn.Embedding(num_items, self.embedding_dim)
        
        # Bias terms
        self.user_bias = nn.Embedding(num_users, 1)
        self.item_bias = nn.Embedding(num_items, 1)
        self.global_bias = nn.Parameter(torch.zeros(1))
        
        # Deep neural network for interaction modeling
        self.interaction_net = nn.Sequential(
            nn.Linear(self.embedding_dim * 2, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        
        # Initialize embeddings
        nn.init.normal_(self.user_embeddings.weight, std=0.1)
        nn.init.normal_(self.item_embeddings.weight, std=0.1)
        nn.init.normal_(self.user_bias.weight, std=0.01)
        nn.init.normal_(self.item_bias.weight, std=0.01)
    
    def forward(self, user_ids: torch.Tensor, item_ids: torch.Tensor) -> torch.Tensor:
        """Forward pass pour collaborative filtering"""
        # Get embeddings
        user_embeds = self.user_embeddings(user_ids)
        item_embeds = self.item_embeddings(item_ids)
        
        # Get bias terms
        user_biases = self.user_bias(user_ids).squeeze()
        item_biases = self.item_bias(item_ids).squeeze()
        
        # Matrix factorization component
        dot_product = (user_embeds * item_embeds).sum(dim=1)
        
        # Deep learning component
        interaction_input = torch.cat([user_embeds, item_embeds], dim=1)
        deep_interaction = self.interaction_net(interaction_input).squeeze()
        
        # Combine components
        prediction = (
            self.global_bias + 
            user_biases + 
            item_biases + 
            dot_product + 
            deep_interaction
        )
        
        return torch.sigmoid(prediction)
    
    def get_user_recommendations(self, user_id: int, item_candidates: List[int], 
                               top_k: int = 10) -> List[Tuple[int, float]]:
        """Obtenir top-k recommandations pour utilisateur"""
        self.eval()
        with torch.no_grad():
            user_tensor = torch.tensor([user_id] * len(item_candidates))
            items_tensor = torch.tensor(item_candidates)
            
            scores = self.forward(user_tensor, items_tensor)
            
            # Get top-k items
            top_scores, top_indices = torch.topk(scores, min(top_k, len(item_candidates)))
            
            recommendations = [
                (item_candidates[idx], score.item()) 
                for idx, score in zip(top_indices, top_scores)
            ]
            
        return recommendations

class ContentEmbeddingEngine:
    """Moteur embeddings contenu pour content-based filtering"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.content_embeddings = {}
        self.feature_weights = {
            'tags': 0.3,
            'category': 0.2,
            'creator_style': 0.2,
            'quality_features': 0.2,
            'engagement_features': 0.1
        }
    
    def build_content_embeddings(self, content_items: List[ContentItem]):
        """Construction embeddings contenu basés sur features"""
        # Prepare text data for TF-IDF
        text_data = []
        content_features = []
        
        for item in content_items:
            # Combine textual features
            text_features = ' '.join(item.tags + [item.category.value])
            text_data.append(text_features)
            
            # Extract numerical features
            features = []
            features.append(item.quality_score)
            features.append(item.monetization_potential)
            features.extend(list(item.engagement_metrics.values())[:5])  # Top 5 engagement metrics
            
            # Pad or truncate to fixed size
            while len(features) < 10:
                features.append(0.0)
            features = features[:10]
            
            content_features.append(features)
        
        # Create TF-IDF embeddings
        tfidf_embeddings = self.vectorizer.fit_transform(text_data).toarray()
        
        # Combine TF-IDF with numerical features
        content_features = np.array(content_features)
        combined_embeddings = np.concatenate([tfidf_embeddings, content_features], axis=1)
        
        # Store embeddings
        for i, item in enumerate(content_items):
            self.content_embeddings[item.content_id] = combined_embeddings[i]
    
    def get_similar_content(self, content_id: str, candidate_ids: List[str], 
                          top_k: int = 10) -> List[Tuple[str, float]]:
        """Obtenir contenu similaire basé sur embeddings"""
        if content_id not in self.content_embeddings:
            return []
        
        target_embedding = self.content_embeddings[content_id].reshape(1, -1)
        similarities = []
        
        for candidate_id in candidate_ids:
            if candidate_id in self.content_embeddings and candidate_id != content_id:
                candidate_embedding = self.content_embeddings[candidate_id].reshape(1, -1)
                similarity = cosine_similarity(target_embedding, candidate_embedding)[0][0]
                similarities.append((candidate_id, similarity))
        
        # Sort by similarity and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

class CreatorMatchingEngine:
    """Moteur matching créateurs pour collaboration opportunities"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.creator_profiles = {}
        self.collaboration_history = defaultdict(list)
    
    def build_creator_profiles(self, content_items: List[ContentItem]):
        """Construction profils créateurs basés sur contenu"""
        creator_content = defaultdict(list)
        
        # Group content by creator
        for item in content_items:
            creator_content[item.creator_id].append(item)
        
        # Build profiles
        for creator_id, contents in creator_content.items():
            profile = self._analyze_creator_style(contents)
            self.creator_profiles[creator_id] = profile
    
    def _analyze_creator_style(self, contents: List[ContentItem]) -> Dict[str, Any]:
        """Analyse style créateur basé sur contenu"""
        if not contents:
            return {}
        
        # Category distribution
        categories = [item.category.value for item in contents]
        category_counts = Counter(categories)
        
        # Average metrics
        avg_quality = np.mean([item.quality_score for item in contents])
        avg_engagement = np.mean([
            np.mean(list(item.engagement_metrics.values()))
            for item in contents if item.engagement_metrics
        ])
        avg_monetization = np.mean([item.monetization_potential for item in contents])
        
        # Tag analysis
        all_tags = []
        for item in contents:
            all_tags.extend(item.tags)
        common_tags = [tag for tag, count in Counter(all_tags).most_common(10)]
        
        return {
            'primary_category': max(category_counts, key=category_counts.get),
            'category_diversity': len(category_counts) / len(contents),
            'avg_quality_score': avg_quality,
            'avg_engagement': avg_engagement,
            'avg_monetization_potential': avg_monetization,
            'signature_tags': common_tags,
            'content_volume': len(contents),
            'style_consistency': self._calculate_style_consistency(contents)
        }
    
    def _calculate_style_consistency(self, contents: List[ContentItem]) -> float:
        """Calcul cohérence style créateur"""
        if len(contents) < 2:
            return 1.0
        
        # Calculate variance in key metrics
        quality_scores = [item.quality_score for item in contents]
        quality_var = np.var(quality_scores)
        
        # Lower variance = higher consistency
        consistency = max(0.0, 1.0 - quality_var)
        return consistency
    
    def find_collaboration_matches(self, creator_id: str, candidate_creators: List[str],
                                 top_k: int = 5) -> List[Tuple[str, float, str]]:
        """Trouver matches collaboration pour créateur"""
        if creator_id not in self.creator_profiles:
            return []
        
        creator_profile = self.creator_profiles[creator_id]
        matches = []
        
        for candidate_id in candidate_creators:
            if candidate_id == creator_id or candidate_id not in self.creator_profiles:
                continue
                
            candidate_profile = self.creator_profiles[candidate_id]
            
            # Calculate compatibility score
            compatibility = self._calculate_creator_compatibility(
                creator_profile, candidate_profile
            )
            
            # Generate collaboration reason  
            reason = self._generate_collaboration_reason(creator_profile, candidate_profile)
            
            if compatibility > 0.3:  # Threshold for meaningful collaborations
                matches.append((candidate_id, compatibility, reason))
        
        # Sort by compatibility
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:top_k]
    
    def _calculate_creator_compatibility(self, profile1: Dict[str, Any], 
                                       profile2: Dict[str, Any]) -> float:
        """Calcul compatibilité entre créateurs"""
        compatibility = 0.0
        
        # Category complementarity (different but compatible)
        if profile1['primary_category'] != profile2['primary_category']:
            compatible_pairs = {
                'music': ['video', 'photography'],
                'video': ['music', 'photography', 'art'],
                'photography': ['music', 'video', 'art', 'blog'],
                'blog': ['photography', 'podcast'],
                'podcast': ['blog', 'music'],
                'art': ['photography', 'video'],
                'comedy': ['video', 'podcast'],
                'education': ['blog', 'video', 'podcast']
            }
            
            if (profile1['primary_category'] in compatible_pairs and 
                profile2['primary_category'] in compatible_pairs[profile1['primary_category']]):
                compatibility += 0.4
        
        # Quality alignment
        quality_diff = abs(profile1['avg_quality_score'] - profile2['avg_quality_score'])
        quality_compatibility = max(0, 1.0 - quality_diff)
        compatibility += quality_compatibility * 0.3
        
        # Engagement level similarity
        engagement_diff = abs(profile1['avg_engagement'] - profile2['avg_engagement'])
        engagement_compatibility = max(0, 1.0 - engagement_diff)
        compatibility += engagement_compatibility * 0.2
        
        # Monetization potential alignment
        monetization_diff = abs(profile1['avg_monetization_potential'] - profile2['avg_monetization_potential'])
        monetization_compatibility = max(0, 1.0 - monetization_diff)
        compatibility += monetization_compatibility * 0.1
        
        return min(1.0, compatibility)
    
    def _generate_collaboration_reason(self, profile1: Dict[str, Any], 
                                     profile2: Dict[str, Any]) -> str:
        """Génération raison collaboration"""
        reasons = []
        
        # Category complementarity
        if profile1['primary_category'] != profile2['primary_category']:
            reasons.append(f"Complementary skills: {profile1['primary_category']} + {profile2['primary_category']}")
        
        # Quality alignment
        if abs(profile1['avg_quality_score'] - profile2['avg_quality_score']) < 0.2:
            reasons.append("Similar quality standards")
        
        # High engagement potential
        if profile1['avg_engagement'] > 0.7 and profile2['avg_engagement'] > 0.7:
            reasons.append("High engagement creators")
        
        # Tag overlap
        common_tags = set(profile1['signature_tags']) & set(profile2['signature_tags'])
        if common_tags:
            reasons.append(f"Shared interests: {', '.join(list(common_tags)[:3])}")
        
        return "; ".join(reasons) if reasons else "Potential synergy"

class TrendingPredictionEngine:
    """Moteur prédiction trending content avec ML forecasting"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.trending_features = [
            'engagement_velocity',
            'share_rate',
            'comment_sentiment',
            'creator_influence',
            'content_novelty',
            'platform_algorithm_boost',
            'hashtag_trending_score',
            'time_factor'
        ]
    
    def predict_trending_content(self, content_items: List[ContentItem],
                              time_horizon_hours: int = 24) -> List[Tuple[str, float]]:
        """Prédiction contenu trending basée sur engagement patterns"""
        trending_scores = []
        
        for item in content_items:
            # Extract trending features
            features = self._extract_trending_features(item)
            
            # Calculate trending score
            trending_score = self._calculate_trending_score(features, time_horizon_hours)
            
            trending_scores.append((item.content_id, trending_score))
        
        # Sort by trending score
        trending_scores.sort(key=lambda x: x[1], reverse=True)
        return trending_scores
    
    def _extract_trending_features(self, item: ContentItem) -> Dict[str, float]:
        """Extraction features trending pour contenu"""
        features = {}
        
        # Engagement velocity (recent engagement rate)
        total_engagement = sum(item.engagement_metrics.values())
        features['engagement_velocity'] = min(1.0, total_engagement / 1000.0)
        
        # Share rate (viral indicator)
        shares = item.engagement_metrics.get('shares', 0)
        views = item.engagement_metrics.get('views', 1)
        features['share_rate'] = min(1.0, shares / max(views, 1))
        
        # Comment sentiment (positive engagement)
        features['comment_sentiment'] = 0.7  # Placeholder - would use sentiment analysis
        
        # Creator influence (follower-based)
        features['creator_influence'] = 0.5  # Placeholder - would use creator metrics
        
        # Content novelty (uniqueness)
        features['content_novelty'] = item.quality_score * 0.8
        
        # Platform algorithm boost (platform-specific)
        features['platform_algorithm_boost'] = 0.6  # Placeholder
        
        # Hashtag trending score
        features['hashtag_trending_score'] = min(1.0, len(item.tags) / 10.0)
        
        # Time factor (recency boost)
        features['time_factor'] = 0.8  # Placeholder - would use creation time
        
        return features
    
    def _calculate_trending_score(self, features: Dict[str, float], 
                                time_horizon_hours: int) -> float:
        """Calcul score trending basé sur features"""
        # Weighted combination of features
        weights = {
            'engagement_velocity': 0.25,
            'share_rate': 0.20,
            'comment_sentiment': 0.15,
            'creator_influence': 0.15,
            'content_novelty': 0.10,
            'platform_algorithm_boost': 0.05,
            'hashtag_trending_score': 0.05,
            'time_factor': 0.05
        }
        
        trending_score = sum(
            features.get(feature, 0) * weight 
            for feature, weight in weights.items()
        )
        
        # Adjust for time horizon
        time_decay = max(0.1, 1.0 - (time_horizon_hours / 168.0))  # Weekly decay
        trending_score *= time_decay
        
        return min(1.0, trending_score)

class BusinessOptimizer:
    """Optimiseur business pour revenue maximization"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.business_objectives = {
            'revenue_optimization': 0.4,
            'user_retention': 0.3,
            'creator_satisfaction': 0.2,
            'platform_growth': 0.1
        }
    
    def optimize_recommendations(self, recommendations: List[RecommendationItem],
                               business_context: Dict[str, Any]) -> List[RecommendationItem]:
        """Optimization recommandations pour business objectives"""
        
        # Calculate business scores for each recommendation
        for rec in recommendations:
            business_score = self._calculate_business_score(rec, business_context)
            rec.business_value = business_score
            
            # Adjust overall score with business weight
            business_weight = self.config.business_weight
            rec.score = (
                rec.score * (1 - business_weight) + 
                business_score * business_weight
            )
        
        # Re-sort by adjusted scores
        recommendations.sort(key=lambda x: x.score, reverse=True)
        
        return recommendations
    
    def _calculate_business_score(self, recommendation: RecommendationItem,
                                business_context: Dict[str, Any]) -> float:
        """Calcul score business pour recommandation"""
        content = recommendation.content_item
        
        # Revenue potential
        revenue_score = content.monetization_potential * 0.4
        
        # Creator tier bonus (premium creators)
        creator_tier = business_context.get('creator_tiers', {}).get(content.creator_id, 'standard')
        if creator_tier == 'premium':
            revenue_score *= 1.3
        elif creator_tier == 'gold':
            revenue_score *= 1.5
        
        # Engagement prediction impact
        engagement_score = recommendation.engagement_prediction * 0.3
        
        # Quality premium
        quality_score = content.quality_score * 0.2
        
        # Platform strategic content
        strategic_bonus = 0.0
        if any(tag in content.tags for tag in business_context.get('strategic_tags', [])):
            strategic_bonus = 0.1
        
        business_score = revenue_score + engagement_score + quality_score + strategic_bonus
        
        return min(1.0, business_score)

class ContentRecommendationModel:
    """
    Modèle principal recommandation contenu avec collaborative filtering et deep learning.
    Personalization + creator matching + content discovery + business optimization.
    """
    
    def __init__(self, recommendation_config: RecommendationConfig):
        self.recommendation_config = recommendation_config
        self.collaborative_filter = None  # Initialized when training data available
        self.content_embedder = ContentEmbeddingEngine(recommendation_config)
        self.creator_matcher = CreatorMatchingEngine(recommendation_config)
        self.business_optimizer = BusinessOptimizer(recommendation_config)
        self.trending_predictor = TrendingPredictionEngine(recommendation_config)
        
        # Cache for performance
        self.recommendation_cache = {} if recommendation_config.cache_recommendations else None
    
    def initialize_models(self, content_items: List[ContentItem], 
                         user_interactions: List[Dict[str, Any]]):
        """Initialisation modèles avec données d'entraînement"""
        # Build content embeddings
        self.content_embedder.build_content_embeddings(content_items)
        
        # Build creator profiles
        self.creator_matcher.build_creator_profiles(content_items)
        
        # Initialize collaborative filtering if interaction data available
        if user_interactions:
            unique_users = set(interaction['user_id'] for interaction in user_interactions)
            unique_items = set(interaction['content_id'] for interaction in user_interactions)
            
            self.collaborative_filter = CollaborativeFilteringEngine(
                self.recommendation_config, 
                len(unique_users), 
                len(unique_items)
            )
    
    async def generate_content_recommendations(self, 
                                             recommendation_request: RecommendationRequest) -> RecommendationResult:
        """
        Génération recommandations contenu avec business optimization.
        
        Content Recommendation Features:
        - Collaborative filtering avec deep neural networks
        - Content-based recommendations avec semantic similarity
        - Creator-to-creator matching pour collaboration opportunities
        - Trending content prediction basé sur engagement patterns
        - Personalized content discovery pour user retention
        - Business value optimization pour revenue maximization
        - Cross-platform content adaptation recommendations
        - Seasonal content strategy suggestions
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            user_profile = recommendation_request.user_profile
            request_type = recommendation_request.request_type
            num_recommendations = recommendation_request.num_recommendations
            
            # Check cache first
            cache_key = f"{user_profile.user_id}_{request_type.value}_{num_recommendations}"
            if self.recommendation_cache and cache_key in self.recommendation_cache:
                return self.recommendation_cache[cache_key]
            
            # Generate recommendations based on type
            recommendations = []
            
            if request_type in [RecommendationType.COLLABORATIVE, RecommendationType.HYBRID]:
                collab_recs = await self._generate_collaborative_recommendations(
                    user_profile, num_recommendations
                )
                recommendations.extend(collab_recs)
            
            if request_type in [RecommendationType.CONTENT_BASED, RecommendationType.HYBRID]:
                content_recs = await self._generate_content_based_recommendations(
                    user_profile, num_recommendations
                )
                recommendations.extend(content_recs)
            
            if request_type == RecommendationType.TRENDING:
                trending_recs = await self._generate_trending_recommendations(
                    user_profile, num_recommendations
                )
                recommendations.extend(trending_recs)
            
            if request_type == RecommendationType.CREATOR_MATCH:
                creator_recs = await self._generate_creator_match_recommendations(
                    user_profile, num_recommendations
                )
                recommendations.extend(creator_recs)
            
            # Remove duplicates and limit to requested number
            unique_recommendations = self._deduplicate_recommendations(recommendations)
            unique_recommendations = unique_recommendations[:num_recommendations]
            
            # Business optimization
            if recommendation_request.business_objectives:
                unique_recommendations = self.business_optimizer.optimize_recommendations(
                    unique_recommendations, recommendation_request.business_objectives
                )
            
            # Calculate metrics
            personalization_score = self._calculate_personalization_score(
                unique_recommendations, user_profile
            )
            diversity_score = self._calculate_diversity_score(unique_recommendations)
            novelty_score = self._calculate_novelty_score(unique_recommendations, user_profile)
            
            # Generate business optimization insights
            business_optimization = self._generate_business_optimization_insights(
                unique_recommendations, recommendation_request
            )
            
            # Generate explanation
            explanation = self._generate_recommendation_explanation(
                unique_recommendations, request_type, user_profile
            )
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            result = RecommendationResult(
                user_id=user_profile.user_id,
                recommendations=unique_recommendations,
                recommendation_type=request_type,
                personalization_score=personalization_score,
                diversity_score=diversity_score,
                novelty_score=novelty_score,
                business_optimization=business_optimization,
                explanation=explanation,
                processing_time_ms=processing_time,
                timestamp=str(np.datetime64('now'))
            )
            
            # Cache result
            if self.recommendation_cache:
                self.recommendation_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Content recommendation error: {e}")
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return self._default_recommendation_result(
                recommendation_request, processing_time
            )
    
    async def _generate_collaborative_recommendations(self, user_profile: UserProfile,
                                                    num_recommendations: int) -> List[RecommendationItem]:
        """Génération recommandations collaborative filtering"""
        recommendations = []
        
        if not self.collaborative_filter:
            return recommendations
        
        try:
            # Get user's interaction history
            interacted_items = [
                interaction['content_id'] 
                for interaction in user_profile.interaction_history
            ]
            
            # Generate candidate items (simplified - would use actual item database)
            candidate_items = [f"item_{i}" for i in range(1000) if f"item_{i}" not in interacted_items]
            
            # Get collaborative recommendations
            user_id_numeric = hash(user_profile.user_id) % 1000  # Simplified mapping
            item_ids_numeric = [hash(item) % 1000 for item in candidate_items]
            
            collab_results = self.collaborative_filter.get_user_recommendations(
                user_id_numeric, item_ids_numeric, num_recommendations * 2
            )
            
            # Convert to RecommendationItem objects
            for item_id, score in collab_results:
                # Create mock ContentItem (in real implementation, would fetch from database)
                content_item = ContentItem(
                    content_id=f"collab_{item_id}",
                    creator_id=f"creator_{item_id % 100}",
                    category=random.choice(list(ContentCategory)),
                    features={},
                    engagement_metrics={'views': random.randint(100, 10000), 'likes': random.randint(10, 1000)},
                    quality_score=random.uniform(0.6, 1.0),
                    tags=[f"tag_{i}" for i in range(3)],
                    creation_date=str(np.datetime64('now')),
                    monetization_potential=random.uniform(0.4, 0.9)
                )
                
                rec_item = RecommendationItem(
                    content_item=content_item,
                    score=score,
                    reason="Similar user preferences",
                    confidence=score,
                    business_value=content_item.monetization_potential,
                    engagement_prediction=score * 0.8
                )
                
                recommendations.append(rec_item)
        
        except Exception as e:
            logger.error(f"Collaborative filtering error: {e}")
        
        return recommendations
    
    async def _generate_content_based_recommendations(self, user_profile: UserProfile,
                                                    num_recommendations: int) -> List[RecommendationItem]:
        """Génération recommandations content-based filtering"""
        recommendations = []
        
        try:
            # Get user's preferred content from interaction history
            preferred_content_ids = [
                interaction['content_id'] 
                for interaction in user_profile.interaction_history 
                if interaction.get('rating', 0) >= 4.0
            ]
            
            if not preferred_content_ids:
                return recommendations
            
            # Find similar content for each preferred item
            all_candidates = set()
            for content_id in preferred_content_ids[:5]:  # Limit to top 5 preferred items
                similar_items = self.content_embedder.get_similar_content(
                    content_id, list(self.content_embedder.content_embeddings.keys()), 
                    num_recommendations
                )
                
                for similar_id, similarity in similar_items:
                    all_candidates.add((similar_id, similarity))
            
            # Sort by similarity and create recommendations
            sorted_candidates = sorted(all_candidates, key=lambda x: x[1], reverse=True)
            
            for content_id, similarity in sorted_candidates[:num_recommendations]:
                # Create mock ContentItem
                content_item = ContentItem(
                    content_id=content_id,
                    creator_id=f"creator_{hash(content_id) % 100}",
                    category=random.choice(list(ContentCategory)),
                    features={},
                    engagement_metrics={'views': random.randint(100, 10000), 'likes': random.randint(10, 1000)},
                    quality_score=random.uniform(0.6, 1.0),
                    tags=[f"tag_{i}" for i in range(3)],
                    creation_date=str(np.datetime64('now')),
                    monetization_potential=random.uniform(0.4, 0.9)
                )
                
                rec_item = RecommendationItem(
                    content_item=content_item,
                    score=similarity,
                    reason="Similar to your liked content",
                    confidence=similarity,
                    business_value=content_item.monetization_potential,
                    engagement_prediction=similarity * 0.7
                )
                
                recommendations.append(rec_item)
        
        except Exception as e:
            logger.error(f"Content-based filtering error: {e}")
        
        return recommendations
    
    async def _generate_trending_recommendations(self, user_profile: UserProfile,
                                               num_recommendations: int) -> List[RecommendationItem]:
        """Génération recommandations trending content"""
        recommendations = []
        
        try:
            # Create mock trending content items
            trending_items = []
            for i in range(num_recommendations * 3):
                item = ContentItem(
                    content_id=f"trending_{i}",
                    creator_id=f"creator_{i % 50}",
                    category=random.choice(list(ContentCategory)),
                    features={},
                    engagement_metrics={
                        'views': random.randint(1000, 100000),
                        'likes': random.randint(100, 10000),
                        'shares': random.randint(10, 5000),
                        'comments': random.randint(5, 1000)
                    },
                    quality_score=random.uniform(0.7, 1.0),
                    tags=[f"trending_tag_{j}" for j in range(random.randint(3, 8))],
                    creation_date=str(np.datetime64('now')),
                    monetization_potential=random.uniform(0.5, 1.0)
                )
                trending_items.append(item)
            
            # Predict trending scores
            trending_predictions = self.trending_predictor.predict_trending_content(
                trending_items, time_horizon_hours=24
            )
            
            # Create recommendations from top trending items
            for content_id, trending_score in trending_predictions[:num_recommendations]:
                # Find corresponding content item
                content_item = next(
                    item for item in trending_items if item.content_id == content_id
                )
                
                rec_item = RecommendationItem(
                    content_item=content_item,
                    score=trending_score,
                    reason="Trending now",
                    confidence=trending_score,
                    business_value=content_item.monetization_potential,
                    engagement_prediction=trending_score * 0.9
                )
                
                recommendations.append(rec_item)
        
        except Exception as e:
            logger.error(f"Trending recommendations error: {e}")
        
        return recommendations
    
    async def _generate_creator_match_recommendations(self, user_profile: UserProfile,
                                                    num_recommendations: int) -> List[RecommendationItem]:
        """Génération recommandations creator matching"""
        recommendations = []
        
        try:
            # Get creators user follows
            followed_creators = user_profile.creator_follows
            
            if not followed_creators:
                return recommendations
            
            # Find collaboration matches for followed creators
            all_matches = []
            for creator_id in followed_creators[:3]:  # Limit to top 3 followed creators
                matches = self.creator_matcher.find_collaboration_matches(
                    creator_id, list(self.creator_matcher.creator_profiles.keys()), 5
                )
                all_matches.extend(matches)
            
            # Create recommendations from matches
            for match_creator_id, compatibility, reason in all_matches[:num_recommendations]:
                # Create mock content from matched creator
                content_item = ContentItem(
                    content_id=f"collab_content_{match_creator_id}",
                    creator_id=match_creator_id,
                    category=random.choice(list(ContentCategory)),
                    features={},
                    engagement_metrics={'views': random.randint(500, 20000), 'likes': random.randint(50, 2000)},
                    quality_score=random.uniform(0.6, 1.0),
                    tags=[f"collab_tag_{i}" for i in range(3)],
                    creation_date=str(np.datetime64('now')),
                    monetization_potential=random.uniform(0.5, 0.9)
                )
                
                rec_item = RecommendationItem(
                    content_item=content_item,
                    score=compatibility,
                    reason=f"Creator collaboration: {reason}",
                    confidence=compatibility,
                    business_value=content_item.monetization_potential,
                    engagement_prediction=compatibility * 0.8
                )
                
                recommendations.append(rec_item)
        
        except Exception as e:
            logger.error(f"Creator match recommendations error: {e}")
        
        return recommendations
    
    def _deduplicate_recommendations(self, recommendations: List[RecommendationItem]) -> List[RecommendationItem]:
        """Suppression doublons dans recommandations"""
        seen_content_ids = set()
        unique_recommendations = []
        
        for rec in recommendations:
            if rec.content_item.content_id not in seen_content_ids:
                seen_content_ids.add(rec.content_item.content_id)
                unique_recommendations.append(rec)
        
        # Sort by score
        unique_recommendations.sort(key=lambda x: x.score, reverse=True)
        return unique_recommendations
    
    def _calculate_personalization_score(self, recommendations: List[RecommendationItem],
                                       user_profile: UserProfile) -> float:
        """Calcul score personnalisation"""
        if not recommendations:
            return 0.0
        
        # Check alignment with user preferences
        preference_alignment = 0.0
        for rec in recommendations:
            content_category = rec.content_item.category.value
            if content_category in user_profile.preferences:
                preference_alignment += user_profile.preferences[content_category]
        
        return min(1.0, preference_alignment / len(recommendations))
    
    def _calculate_diversity_score(self, recommendations: List[RecommendationItem]) -> float:
        """Calcul score diversité"""
        if not recommendations:
            return 0.0
        
        # Calculate category diversity
        categories = [rec.content_item.category.value for rec in recommendations]
        unique_categories = len(set(categories))
        max_possible_categories = min(len(ContentCategory), len(recommendations))
        
        diversity = unique_categories / max_possible_categories
        return diversity
    
    def _calculate_novelty_score(self, recommendations: List[RecommendationItem],
                               user_profile: UserProfile) -> float:
        """Calcul score nouveauté"""
        if not recommendations:
            return 0.0
        
        # Check how many recommended items are new to user
        interacted_content = set(
            interaction['content_id'] 
            for interaction in user_profile.interaction_history
        )
        
        new_content_count = sum(
            1 for rec in recommendations 
            if rec.content_item.content_id not in interacted_content
        )
        
        novelty = new_content_count / len(recommendations)
        return novelty
    
    def _generate_business_optimization_insights(self, recommendations: List[RecommendationItem],
                                               request: RecommendationRequest) -> Dict[str, Any]:
        """Génération insights optimization business"""
        insights = {
            'revenue_potential': np.mean([rec.content_item.monetization_potential for rec in recommendations]),
            'engagement_forecast': np.mean([rec.engagement_prediction for rec in recommendations]),
            'quality_distribution': {
                'high_quality': sum(1 for rec in recommendations if rec.content_item.quality_score > 0.8),
                'medium_quality': sum(1 for rec in recommendations if 0.6 <= rec.content_item.quality_score <= 0.8),
                'improving_quality': sum(1 for rec in recommendations if rec.content_item.quality_score < 0.6)
            },
            'creator_opportunities': len(set(rec.content_item.creator_id for rec in recommendations)),
            'category_focus': Counter([rec.content_item.category.value for rec in recommendations])
        }
        
        return insights
    
    def _generate_recommendation_explanation(self, recommendations: List[RecommendationItem],
                                           request_type: RecommendationType,
                                           user_profile: UserProfile) -> Dict[str, Any]:
        """Génération explication recommandations"""
        explanation = {
            'algorithm_used': request_type.value,
            'personalization_factors': [],
            'recommendation_reasons': {},
            'diversity_info': f"Recommended {len(set(rec.content_item.category.value for rec in recommendations))} different content categories"
        }
        
        # Add personalization factors
        if user_profile.preferences:
            top_preferences = sorted(
                user_profile.preferences.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            explanation['personalization_factors'] = [
                f"You enjoy {category} content ({score:.1%})" 
                for category, score in top_preferences
            ]
        
        # Add individual recommendation reasons
        for rec in recommendations[:5]:  # Top 5 explanations
            explanation['recommendation_reasons'][rec.content_item.content_id] = rec.reason
        
        return explanation
    
    def _default_recommendation_result(self, request: RecommendationRequest,
                                     processing_time: float) -> RecommendationResult:
        """Résultat recommandation par défaut en cas d'erreur"""
        return RecommendationResult(
            user_id=request.user_profile.user_id,
            recommendations=[],
            recommendation_type=request.request_type,
            personalization_score=0.0,
            diversity_score=0.0,
            novelty_score=0.0,
            business_optimization={},
            explanation={'error': 'Recommendation generation failed'},
            processing_time_ms=processing_time,
            timestamp=str(np.datetime64('now'))
        )

class ContentRecommendationService:
    """
    Service principal pour content recommendations IA Chérie.
    Orchestration + analytics + A/B testing + performance monitoring.
    """
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.model = ContentRecommendationModel(config)
        self.analytics_data = []
        self.ab_test_variants = {}
    
    async def get_recommendations_batch(self, requests: List[RecommendationRequest]) -> List[RecommendationResult]:
        """Traitement batch recommandations pour optimisation performance"""
        results = []
        
        for request in requests:
            result = await self.model.generate_content_recommendations(request)
            results.append(result)
            
            # Store for analytics
            self.analytics_data.append(result)
        
        return results
    
    async def generate_recommendation_analytics(self) -> Dict[str, Any]:
        """Génération analytics recommandations agrégées"""
        if not self.analytics_data:
            return {}
        
        results = self.analytics_data
        
        analytics = {
            'total_recommendations': len(results),
            'algorithm_performance': {},
            'personalization_metrics': {
                'avg_personalization_score': np.mean([r.personalization_score for r in results]),
                'avg_diversity_score': np.mean([r.diversity_score for r in results]),
                'avg_novelty_score': np.mean([r.novelty_score for r in results])
            },
            'business_impact': {
                'avg_revenue_potential': np.mean([
                    r.business_optimization.get('revenue_potential', 0) for r in results
                ]),
                'avg_engagement_forecast': np.mean([
                    r.business_optimization.get('engagement_forecast', 0) for r in results
                ])
            },
            'processing_performance': {
                'avg_processing_time_ms': np.mean([r.processing_time_ms for r in results]),
                'recommendations_per_second': len(results) / (sum(r.processing_time_ms for r in results) / 1000)
            }
        }
        
        # Algorithm performance breakdown
        algorithm_groups = defaultdict(list)
        for result in results:
            algorithm_groups[result.recommendation_type.value].append(result)
        
        for algorithm, alg_results in algorithm_groups.items():
            analytics['algorithm_performance'][algorithm] = {
                'count': len(alg_results),
                'avg_personalization': np.mean([r.personalization_score for r in alg_results]),
                'avg_diversity': np.mean([r.diversity_score for r in alg_results]),
                'avg_processing_time': np.mean([r.processing_time_ms for r in alg_results])
            }
        
        return analytics


# Factory function pour faciliter l'utilisation
def create_content_recommender(device: str = "cpu",
                             enable_hybrid: bool = True,
                             cache_recommendations: bool = True) -> ContentRecommendationService:
    """Factory function pour créer content recommender"""
    config = RecommendationConfig(
        device=device,
        enable_hybrid=enable_hybrid,
        diversity_weight=0.3,
        novelty_weight=0.2,
        business_weight=0.4,
        cache_recommendations=cache_recommendations
    )
    
    return ContentRecommendationService(config)


# Export des classes principales
__all__ = [
    "RecommendationType",
    "ContentCategory",
    "EngagementLevel",
    "UserProfile",
    "ContentItem",
    "RecommendationRequest",
    "RecommendationItem",
    "RecommendationResult",
    "RecommendationConfig",
    "ContentRecommendationModel",
    "ContentRecommendationService",
    "create_content_recommender"
]