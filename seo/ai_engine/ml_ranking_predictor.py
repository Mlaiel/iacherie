"""
ML Ranking Predictor for Ainflue Platform
Machine Learning-based ranking prediction and optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Tuple, Union, Any
import json
import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import numpy as np


@dataclass
class RankingFeature:
    """Ranking feature representation"""
    name: str
    value: float
    weight: float
    category: str  # 'technical', 'content', 'authority', 'user_signals'
    importance: float = 0.0


@dataclass
class RankingPrediction:
    """Ranking prediction result"""
    url: str
    keyword: str
    predicted_rank: int
    confidence: float
    current_rank: Optional[int] = None
    features: List[RankingFeature] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    potential_improvement: int = 0


@dataclass
class ModelPerformance:
    """Model performance metrics"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mean_absolute_error: float


class MLRankingPredictor:
    """
    Machine Learning-based ranking prediction engine
    Predicts search engine rankings based on multiple SEO factors
    """
    
    def __init__(self) -> None:
        self.feature_weights = self._initialize_feature_weights()
        self.model_coefficients = self._initialize_model_coefficients()
        self.ranking_factors = self._define_ranking_factors()
        self.performance_metrics = None
        
    def _initialize_feature_weights(self) -> Dict[str, float]:
        """Initialize feature weights based on SEO research"""
        return {
            # Content Quality Features (40%)
            'content_length': 0.08,
            'keyword_density': 0.06,
            'readability_score': 0.05,
            'content_freshness': 0.04,
            'semantic_richness': 0.07,
            'title_optimization': 0.06,
            'meta_description_quality': 0.04,
            
            # Technical SEO Features (25%)
            'page_speed': 0.06,
            'mobile_friendliness': 0.05,
            'core_web_vitals': 0.06,
            'schema_markup': 0.03,
            'ssl_certificate': 0.02,
            'url_structure': 0.03,
            
            # Authority Features (20%)
            'domain_authority': 0.08,
            'page_authority': 0.05,
            'backlink_quality': 0.04,
            'internal_link_strength': 0.03,
            
            # User Signals Features (15%)
            'click_through_rate': 0.06,
            'bounce_rate': 0.04,
            'dwell_time': 0.03,
            'user_engagement': 0.02
        }
        
    def _initialize_model_coefficients(self) -> Dict[str, float]:
        """Initialize machine learning model coefficients"""
        # Simplified linear regression coefficients
        # In practice, these would be learned from training data
        return {
            'intercept': 50.0,  # Base ranking position
            'content_quality_multiplier': -0.8,
            'technical_seo_multiplier': -0.6,
            'authority_multiplier': -1.2,
            'user_signals_multiplier': -0.9,
            'competition_factor': 0.3
        }
        
    def _define_ranking_factors(self) -> Dict[str, Dict]:
        """Define comprehensive ranking factors with thresholds"""
        return {
            'content_length': {
                'optimal_range': (1000, 3000),
                'scoring_function': 'sigmoid',
                'platform_specific': {
                    'blog': (800, 2500),
                    'tutorial': (1500, 4000),
                    'portfolio': (300, 1000)
                }
            },
            'keyword_density': {
                'optimal_range': (1.0, 3.0),
                'scoring_function': 'inverted_u',
                'penalty_threshold': 5.0
            },
            'page_speed': {
                'optimal_threshold': 3.0,  # seconds
                'scoring_function': 'exponential_decay',
                'mobile_weight': 1.5
            },
            'core_web_vitals': {
                'lcp_threshold': 2.5,  # Largest Contentful Paint
                'fid_threshold': 100,  # First Input Delay (ms)
                'cls_threshold': 0.1   # Cumulative Layout Shift
            }
        }
        
    def extract_features(self, page_data: Dict, keyword: str, content_type: str = None) -> List[RankingFeature]:
        """Extract ranking features from page data"""
        
        features = []
        
        # Content Quality Features
        features.extend(self._extract_content_features(page_data, keyword))
        
        # Technical SEO Features
        features.extend(self._extract_technical_features(page_data))
        
        # Authority Features
        features.extend(self._extract_authority_features(page_data))
        
        # User Signal Features
        features.extend(self._extract_user_signal_features(page_data))
        
        # Competition Features
        features.extend(self._extract_competition_features(keyword, page_data))
        
        # Platform-specific adjustments
        if content_type:
            features = self._apply_content_type_adjustments(features, content_type)
            
        return features
        
    def _extract_content_features(self, page_data: Dict, keyword: str) -> List[RankingFeature]:
        """Extract content-related ranking features"""
        
        features = []
        content = page_data.get('content', '')
        title = page_data.get('title', '')
        meta_description = page_data.get('meta_description', '')
        
        # Content Length
        content_length = len(content.split())
        length_score = self._score_content_length(content_length)
        features.append(RankingFeature(
            name='content_length',
            value=length_score,
            weight=self.feature_weights['content_length'],
            category='content'
        ))
        
        # Keyword Density
        keyword_density = self._calculate_keyword_density(content, keyword)
        density_score = self._score_keyword_density(keyword_density)
        features.append(RankingFeature(
            name='keyword_density',
            value=density_score,
            weight=self.feature_weights['keyword_density'],
            category='content'
        ))
        
        # Readability
        readability = self._calculate_readability(content)
        features.append(RankingFeature(
            name='readability_score',
            value=readability,
            weight=self.feature_weights['readability_score'],
            category='content'
        ))
        
        # Content Freshness
        publish_date = page_data.get('publish_date')
        freshness_score = self._calculate_freshness_score(publish_date)
        features.append(RankingFeature(
            name='content_freshness',
            value=freshness_score,
            weight=self.feature_weights['content_freshness'],
            category='content'
        ))
        
        # Semantic Richness
        semantic_score = self._calculate_semantic_richness(content, keyword)
        features.append(RankingFeature(
            name='semantic_richness',
            value=semantic_score,
            weight=self.feature_weights['semantic_richness'],
            category='content'
        ))
        
        # Title Optimization
        title_score = self._score_title_optimization(title, keyword)
        features.append(RankingFeature(
            name='title_optimization',
            value=title_score,
            weight=self.feature_weights['title_optimization'],
            category='content'
        ))
        
        # Meta Description Quality
        meta_score = self._score_meta_description(meta_description, keyword)
        features.append(RankingFeature(
            name='meta_description_quality',
            value=meta_score,
            weight=self.feature_weights['meta_description_quality'],
            category='content'
        ))
        
        return features
        
    def _extract_technical_features(self, page_data: Dict) -> List[RankingFeature]:
        """Extract technical SEO features"""
        
        features = []
        
        # Page Speed
        page_speed = page_data.get('page_speed', 5.0)  # seconds
        speed_score = max(0, min(100, 100 - (page_speed - 1) * 20))
        features.append(RankingFeature(
            name='page_speed',
            value=speed_score,
            weight=self.feature_weights['page_speed'],
            category='technical'
        ))
        
        # Mobile Friendliness
        mobile_friendly = page_data.get('mobile_friendly', True)
        mobile_score = 100 if mobile_friendly else 0
        features.append(RankingFeature(
            name='mobile_friendliness',
            value=mobile_score,
            weight=self.feature_weights['mobile_friendliness'],
            category='technical'
        ))
        
        # Core Web Vitals
        cwv_score = self._calculate_core_web_vitals_score(page_data)
        features.append(RankingFeature(
            name='core_web_vitals',
            value=cwv_score,
            weight=self.feature_weights['core_web_vitals'],
            category='technical'
        ))
        
        # Schema Markup
        has_schema = page_data.get('schema_markup', False)
        schema_score = 100 if has_schema else 0
        features.append(RankingFeature(
            name='schema_markup',
            value=schema_score,
            weight=self.feature_weights['schema_markup'],
            category='technical'
        ))
        
        # SSL Certificate
        has_ssl = page_data.get('ssl_certificate', True)
        ssl_score = 100 if has_ssl else 0
        features.append(RankingFeature(
            name='ssl_certificate',
            value=ssl_score,
            weight=self.feature_weights['ssl_certificate'],
            category='technical'
        ))
        
        # URL Structure
        url = page_data.get('url', '')
        url_score = self._score_url_structure(url)
        features.append(RankingFeature(
            name='url_structure',
            value=url_score,
            weight=self.feature_weights['url_structure'],
            category='technical'
        ))
        
        return features
        
    def _extract_authority_features(self, page_data: Dict) -> List[RankingFeature]:
        """Extract authority-related features"""
        
        features = []
        
        # Domain Authority
        domain_authority = page_data.get('domain_authority', 50)
        features.append(RankingFeature(
            name='domain_authority',
            value=domain_authority,
            weight=self.feature_weights['domain_authority'],
            category='authority'
        ))
        
        # Page Authority
        page_authority = page_data.get('page_authority', 30)
        features.append(RankingFeature(
            name='page_authority',
            value=page_authority,
            weight=self.feature_weights['page_authority'],
            category='authority'
        ))
        
        # Backlink Quality
        backlink_score = self._calculate_backlink_quality_score(page_data)
        features.append(RankingFeature(
            name='backlink_quality',
            value=backlink_score,
            weight=self.feature_weights['backlink_quality'],
            category='authority'
        ))
        
        # Internal Link Strength
        internal_links = page_data.get('internal_links_count', 0)
        internal_score = min(100, internal_links * 10)
        features.append(RankingFeature(
            name='internal_link_strength',
            value=internal_score,
            weight=self.feature_weights['internal_link_strength'],
            category='authority'
        ))
        
        return features
        
    def _extract_user_signal_features(self, page_data: Dict) -> List[RankingFeature]:
        """Extract user signal features"""
        
        features = []
        
        # Click Through Rate
        ctr = page_data.get('click_through_rate', 0.02)  # 2% default
        ctr_score = min(100, ctr * 1000)  # Scale to 0-100
        features.append(RankingFeature(
            name='click_through_rate',
            value=ctr_score,
            weight=self.feature_weights['click_through_rate'],
            category='user_signals'
        ))
        
        # Bounce Rate
        bounce_rate = page_data.get('bounce_rate', 0.6)  # 60% default
        bounce_score = max(0, 100 - bounce_rate * 100)
        features.append(RankingFeature(
            name='bounce_rate',
            value=bounce_score,
            weight=self.feature_weights['bounce_rate'],
            category='user_signals'
        ))
        
        # Dwell Time
        dwell_time = page_data.get('dwell_time', 120)  # seconds
        dwell_score = min(100, dwell_time / 3)  # 5 minutes = 100 score
        features.append(RankingFeature(
            name='dwell_time',
            value=dwell_score,
            weight=self.feature_weights['dwell_time'],
            category='user_signals'
        ))
        
        # User Engagement
        engagement_score = self._calculate_engagement_score(page_data)
        features.append(RankingFeature(
            name='user_engagement',
            value=engagement_score,
            weight=self.feature_weights['user_engagement'],
            category='user_signals'
        ))
        
        return features
        
    def _extract_competition_features(self, keyword: str, page_data: Dict) -> List[RankingFeature]:
        """Extract competition-related features"""
        
        # This would typically analyze competitor pages for the keyword
        # For now, we'll use simplified competition analysis
        
        keyword_difficulty = self._estimate_keyword_difficulty(keyword)
        
        return [RankingFeature(
            name='keyword_competition',
            value=100 - keyword_difficulty,  # Invert difficulty to get competitiveness score
            weight=0.05,
            category='competition'
        )]
        
    def predict_ranking(self, page_data: Dict, keyword: str, 
                       content_type: str = None) -> RankingPrediction:
        """Predict ranking position for a page and keyword"""
        
        # Extract features
        features = self.extract_features(page_data, keyword, content_type)
        
        # Calculate weighted scores by category
        category_scores = defaultdict(float)
        for feature in features:
            category_scores[feature.category] += feature.value * feature.weight
            
        # Apply ML model
        predicted_rank = self._apply_ranking_model(category_scores)
        
        # Calculate confidence
        confidence = self._calculate_prediction_confidence(features, category_scores)
        
        # Generate recommendations
        recommendations = self._generate_ranking_recommendations(features, predicted_rank)
        
        # Calculate potential improvement
        potential_improvement = self._calculate_potential_improvement(features, predicted_rank)
        
        return RankingPrediction(
            url=page_data.get('url', ''),
            keyword=keyword,
            predicted_rank=int(predicted_rank),
            confidence=confidence,
            features=features,
            recommendations=recommendations,
            potential_improvement=potential_improvement
        )
        
    def _apply_ranking_model(self, category_scores: Dict[str, float]) -> float:
        """Apply ML model to predict ranking"""
        
        coefficients = self.model_coefficients
        
        # Calculate base score
        base_score = coefficients['intercept']
        
        # Apply category multipliers
        content_score = category_scores.get('content', 0)
        technical_score = category_scores.get('technical', 0)
        authority_score = category_scores.get('authority', 0)
        user_signals_score = category_scores.get('user_signals', 0)
        competition_score = category_scores.get('competition', 0)
        
        # Linear combination (simplified ML model)
        predicted_rank = (
            base_score +
            content_score * coefficients['content_quality_multiplier'] +
            technical_score * coefficients['technical_seo_multiplier'] +
            authority_score * coefficients['authority_multiplier'] +
            user_signals_score * coefficients['user_signals_multiplier'] +
            competition_score * coefficients['competition_factor']
        )
        
        # Ensure ranking is positive and reasonable
        predicted_rank = max(1, min(100, predicted_rank))
        
        return predicted_rank
        
    def _calculate_prediction_confidence(self, features: List[RankingFeature], 
                                       category_scores: Dict[str, float]) -> float:
        """Calculate confidence in the ranking prediction"""
        
        # Base confidence
        confidence = 0.7
        
        # Adjust based on feature completeness
        total_features = len(self.feature_weights)
        available_features = len(features)
        completeness = available_features / total_features
        confidence *= completeness
        
        # Adjust based on score distribution
        score_variance = np.var(list(category_scores.values())) if category_scores else 0
        if score_variance > 100:  # High variance = lower confidence
            confidence *= 0.9
        elif score_variance < 50:  # Low variance = higher confidence
            confidence *= 1.1
            
        return min(1.0, max(0.1, confidence))
        
    def _generate_ranking_recommendations(self, features: List[RankingFeature], 
                                        predicted_rank: float) -> List[str]:
        """Generate recommendations to improve ranking"""
        
        recommendations = []
        
        # Find weakest features
        weak_features = [f for f in features if f.value < 50]
        weak_features.sort(key=lambda x: x.weight * (50 - x.value), reverse=True)
        
        for feature in weak_features[:5]:  # Top 5 improvement opportunities
            if feature.name == 'content_length':
                recommendations.append("Increase content length to 1000+ words for better rankings")
            elif feature.name == 'keyword_density':
                recommendations.append("Optimize keyword density to 1-3% for target keywords")
            elif feature.name == 'page_speed':
                recommendations.append("Improve page loading speed to under 3 seconds")
            elif feature.name == 'mobile_friendliness':
                recommendations.append("Ensure website is fully mobile-responsive")
            elif feature.name == 'readability_score':
                recommendations.append("Improve content readability with shorter sentences and simpler words")
            elif feature.name == 'title_optimization':
                recommendations.append("Optimize page title to include target keyword near the beginning")
            elif feature.name == 'backlink_quality':
                recommendations.append("Build high-quality backlinks from authoritative websites")
            elif feature.name == 'user_engagement':
                recommendations.append("Improve user engagement with interactive content and clear CTAs")
                
        # General recommendations based on predicted rank
        if predicted_rank > 20:
            recommendations.append("Focus on fundamental SEO improvements for significant ranking gains")
        elif predicted_rank > 10:
            recommendations.append("Target long-tail keywords and improve content depth")
        else:
            recommendations.append("Fine-tune technical SEO and build topical authority")
            
        return recommendations
        
    def _calculate_potential_improvement(self, features: List[RankingFeature], 
                                       current_predicted_rank: float) -> int:
        """Calculate potential ranking improvement if issues are fixed"""
        
        # Simulate improvements to weak features
        improved_features = []
        
        for feature in features:
            if feature.value < 70:  # Room for improvement
                # Simulate 80% of optimal value
                improved_value = min(100, feature.value + (100 - feature.value) * 0.8)
            else:
                improved_value = feature.value
                
            improved_features.append(RankingFeature(
                name=feature.name,
                value=improved_value,
                weight=feature.weight,
                category=feature.category
            ))
            
        # Recalculate with improved features
        improved_category_scores = defaultdict(float)
        for feature in improved_features:
            improved_category_scores[feature.category] += feature.value * feature.weight
            
        improved_rank = self._apply_ranking_model(improved_category_scores)
        
        potential_improvement = max(0, int(current_predicted_rank - improved_rank))
        
        return potential_improvement
        
    # Utility scoring methods
    def _score_content_length(self, word_count: int) -> float:
        """Score content length on 0-100 scale"""
        if word_count < 300:
            return word_count / 300 * 30
        elif word_count < 1000:
            return 30 + (word_count - 300) / 700 * 40
        elif word_count < 3000:
            return 70 + (word_count - 1000) / 2000 * 30
        else:
            return max(70, 100 - (word_count - 3000) / 1000 * 10)
            
    def _calculate_keyword_density(self, content: str, keyword: str) -> float:
        """Calculate keyword density"""
        words = content.lower().split()
        keyword_count = words.count(keyword.lower())
        return (keyword_count / len(words)) * 100 if words else 0
        
    def _score_keyword_density(self, density: float) -> float:
        """Score keyword density (optimal 1-3%)"""
        if density < 1:
            return density * 50
        elif density <= 3:
            return 50 + (density - 1) * 25
        else:
            return max(0, 100 - (density - 3) * 20)
            
    def _calculate_readability(self, content: str) -> float:
        """Calculate readability score (simplified)"""
        if not content:
            return 0
            
        sentences = len(re.split(r'[.!?]+', content))
        words = len(content.split())
        
        if sentences == 0:
            return 0
            
        avg_sentence_length = words / sentences
        
        # Simple readability scoring
        if avg_sentence_length < 15:
            return 90
        elif avg_sentence_length < 20:
            return 70
        elif avg_sentence_length < 25:
            return 50
        else:
            return 30
            
    def _calculate_freshness_score(self, publish_date: Optional[str]) -> float:
        """Calculate content freshness score"""
        if not publish_date:
            return 50  # Neutral score if date unknown
            
        try:
            pub_date = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
            days_old = (datetime.now() - pub_date).days
            
            if days_old < 30:
                return 100
            elif days_old < 90:
                return 80
            elif days_old < 365:
                return 60
            else:
                return max(20, 60 - (days_old - 365) / 365 * 20)
        except:
            return 50
            
    def _calculate_semantic_richness(self, content: str, keyword: str) -> float:
        """Calculate semantic richness score"""
        # Simplified semantic analysis
        words = set(content.lower().split())
        
        # Related terms (simplified - would use NLP in practice)
        related_terms = {
            'music': ['song', 'audio', 'melody', 'rhythm', 'harmony'],
            'photo': ['image', 'picture', 'visual', 'camera', 'lens'],
            'video': ['film', 'movie', 'cinema', 'footage', 'recording'],
            'blog': ['article', 'post', 'content', 'story', 'writing']
        }
        
        keyword_base = keyword.split()[0].lower()
        if keyword_base in related_terms:
            related_count = sum(1 for term in related_terms[keyword_base] if term in words)
            return min(100, related_count * 20)
            
        return 50  # Neutral score
        
    def _score_title_optimization(self, title: str, keyword: str) -> float:
        """Score title optimization"""
        if not title:
            return 0
            
        score = 0
        
        # Keyword in title
        if keyword.lower() in title.lower():
            score += 50
            
        # Keyword near beginning
        words = title.lower().split()
        if len(words) > 0 and keyword.lower() in ' '.join(words[:3]):
            score += 30
            
        # Length optimization
        if 30 <= len(title) <= 60:
            score += 20
        elif 20 <= len(title) <= 70:
            score += 10
            
        return min(100, score)
        
    def _score_meta_description(self, meta_description: str, keyword: str) -> float:
        """Score meta description optimization"""
        if not meta_description:
            return 0
            
        score = 0
        
        # Has meta description
        score += 30
        
        # Keyword in description
        if keyword.lower() in meta_description.lower():
            score += 40
            
        # Length optimization
        if 120 <= len(meta_description) <= 160:
            score += 30
        elif 100 <= len(meta_description) <= 180:
            score += 20
            
        return min(100, score)
        
    def _calculate_core_web_vitals_score(self, page_data: Dict) -> float:
        """Calculate Core Web Vitals score"""
        lcp = page_data.get('largest_contentful_paint', 3.0)
        fid = page_data.get('first_input_delay', 150)
        cls = page_data.get('cumulative_layout_shift', 0.15)
        
        # Score each metric
        lcp_score = 100 if lcp <= 2.5 else max(0, 100 - (lcp - 2.5) * 40)
        fid_score = 100 if fid <= 100 else max(0, 100 - (fid - 100) * 0.5)
        cls_score = 100 if cls <= 0.1 else max(0, 100 - (cls - 0.1) * 500)
        
        # Weighted average
        return (lcp_score * 0.5 + fid_score * 0.25 + cls_score * 0.25)
        
    def _score_url_structure(self, url: str) -> float:
        """Score URL structure quality"""
        if not url:
            return 0
            
        score = 50  # Base score
        
        # HTTPS
        if url.startswith('https'):
            score += 10
            
        # No special characters
        if re.match(r'^[a-zA-Z0-9\-/:.]+$', url):
            score += 10
            
        # Descriptive path
        path = url.split('/')[-1] if '/' in url else ''
        if len(path) > 3 and '-' in path:
            score += 15
            
        # Not too long
        if len(url) < 100:
            score += 15
            
        return min(100, score)
        
    def _calculate_backlink_quality_score(self, page_data: Dict) -> float:
        """Calculate backlink quality score"""
        backlink_count = page_data.get('backlink_count', 0)
        referring_domains = page_data.get('referring_domains', 0)
        avg_domain_authority = page_data.get('avg_referring_domain_authority', 30)
        
        # Score based on quantity and quality
        quantity_score = min(50, backlink_count * 2)
        diversity_score = min(25, referring_domains * 5)
        quality_score = min(25, avg_domain_authority / 4)
        
        return quantity_score + diversity_score + quality_score
        
    def _calculate_engagement_score(self, page_data: Dict) -> float:
        """Calculate user engagement score"""
        pages_per_session = page_data.get('pages_per_session', 1.5)
        time_on_page = page_data.get('time_on_page', 120)
        return_visitors = page_data.get('return_visitor_rate', 0.3)
        
        # Combine engagement metrics
        page_score = min(40, pages_per_session * 20)
        time_score = min(40, time_on_page / 5)
        return_score = min(20, return_visitors * 66.7)
        
        return page_score + time_score + return_score
        
    def _estimate_keyword_difficulty(self, keyword: str) -> float:
        """Estimate keyword difficulty (simplified)"""
        # In practice, this would analyze SERP competition
        
        # Basic heuristics
        word_count = len(keyword.split())
        
        if word_count == 1:
            return 80  # Single words are typically hard
        elif word_count == 2:
            return 60
        elif word_count >= 3:
            return 40  # Long-tail keywords are easier
            
        return 50
        
    def _apply_content_type_adjustments(self, features: List[RankingFeature], 
                                      content_type: str) -> List[RankingFeature]:
        """Apply content type specific adjustments"""
        
        adjustments = {
            'blog': {'content_length': 1.2, 'readability_score': 1.1},
            'tutorial': {'content_length': 1.3, 'semantic_richness': 1.2},
            'portfolio': {'user_engagement': 1.3, 'page_speed': 1.2},
            'video': {'user_engagement': 1.4, 'dwell_time': 1.3},
            'music': {'user_engagement': 1.5, 'semantic_richness': 1.1}
        }
        
        if content_type in adjustments:
            for feature in features:
                if feature.name in adjustments[content_type]:
                    feature.weight *= adjustments[content_type][feature.name]
                    
        return features


# Example usage and testing
if __name__ == "__main__":
    predictor = MLRankingPredictor()
    
    # Sample page data
    page_data = {
        'url': 'https://ainflue.com/blog/ai-music-creation',
        'title': 'How to Create Amazing Music with AI Tools',
        'content': '''Creating music with artificial intelligence has become increasingly popular...''' * 50,
        'meta_description': 'Learn how to create amazing music using AI tools and techniques. Complete guide for beginners.',
        'publish_date': '2024-01-15T10:00:00Z',
        'page_speed': 2.8,
        'mobile_friendly': True,
        'domain_authority': 65,
        'page_authority': 45,
        'backlink_count': 25,
        'click_through_rate': 0.035,
        'bounce_rate': 0.45,
        'dwell_time': 180
    }
    
    # Predict ranking
    prediction = predictor.predict_ranking(page_data, "AI music creation", "blog")
    
    print(f"Ranking Prediction for '{prediction.keyword}':")
    print(f"Predicted Rank: {prediction.predicted_rank}")
    print(f"Confidence: {prediction.confidence:.2f}")
    print(f"Potential Improvement: {prediction.potential_improvement} positions")
    print("\nTop Recommendations:")
    for i, rec in enumerate(prediction.recommendations[:5], 1):
        print(f"{i}. {rec}")
        
    print("\nFeature Analysis:")
    sorted_features = sorted(prediction.features, key=lambda x: x.weight * x.value, reverse=True)
    for feature in sorted_features[:10]:
        print(f"{feature.name}: {feature.value:.1f} (weight: {feature.weight:.3f}, category: {feature.category})")