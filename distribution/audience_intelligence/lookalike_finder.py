"""
Lookalike Finder - Advanced Audience Expansion Engine
====================================================

AI-powered lookalike audience discovery for targeted expansion.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimilarityMethod(Enum):
    """Similarity calculation methods"""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    JACCARD = "jaccard"
    PEARSON = "pearson"
    HYBRID = "hybrid"


class ExpansionStrategy(Enum):
    """Audience expansion strategies"""
    CONSERVATIVE = "conservative"  # High similarity, smaller reach
    BALANCED = "balanced"         # Moderate similarity, balanced reach
    AGGRESSIVE = "aggressive"     # Lower similarity, maximum reach
    CUSTOM = "custom"            # Custom thresholds


@dataclass
class LookalikeAudience:
    """Lookalike audience structure"""
    audience_id: str
    similarity_score: float
    estimated_size: int
    overlap_percentage: float
    demographic_match: Dict[str, float]
    behavioral_match: Dict[str, float]
    interest_match: Dict[str, float]
    quality_score: float
    expansion_potential: int
    recommended_budget: float


@dataclass
class LookalikeConfig:
    """Configuration for lookalike finding"""
    similarity_threshold: float = 0.75
    max_audiences: int = 10
    min_audience_size: int = 1000
    max_audience_size: int = 1000000
    similarity_method: SimilarityMethod = SimilarityMethod.HYBRID
    expansion_strategy: ExpansionStrategy = ExpansionStrategy.BALANCED
    include_demographics: bool = True
    include_behaviors: bool = True
    include_interests: bool = True
    include_psychographics: bool = True


class LookalikeFinder:
    """
    Advanced Lookalike Audience Finder
    =================================
    
    Uses sophisticated ML algorithms to identify similar audiences
    for targeted expansion and improved campaign performance.
    """
    
    def __init__(self) -> None:
        """Initialize the Lookalike Finder"""
        self.similarity_models = self._load_similarity_models()
        self.audience_database = self._initialize_audience_database()
        self.feature_extractors = self._load_feature_extractors()
        
        logger.info("LookalikeFinder initialized successfully")
    
    async def find_lookalike_audiences(
        self,
        source_audience_id: str,
        config: Optional[LookalikeConfig] = None
    ) -> List[LookalikeAudience]:
        """
        Find lookalike audiences based on source audience
        
        Args:
            source_audience_id: ID of the source audience to match
            config: Configuration for lookalike finding
            
        Returns:
            List of lookalike audiences ranked by similarity
        """
        try:
            if config is None:
                config = LookalikeConfig()
            
            logger.info(f"Finding lookalike audiences for: {source_audience_id}")
            
            # Extract source audience features
            source_features = await self._extract_audience_features(
                source_audience_id, config
            )
            
            # Get candidate audiences
            candidate_audiences = await self._get_candidate_audiences(
                source_audience_id, config
            )
            
            # Calculate similarities
            lookalike_candidates = []
            for candidate_id in candidate_audiences:
                candidate_features = await self._extract_audience_features(
                    candidate_id, config
                )
                
                similarity_score = await self._calculate_similarity(
                    source_features, candidate_features, config.similarity_method
                )
                
                if similarity_score >= config.similarity_threshold:
                    lookalike = await self._create_lookalike_audience(
                        candidate_id, similarity_score, source_features, 
                        candidate_features, config
                    )
                    lookalike_candidates.append(lookalike)
            
            # Rank and filter results
            ranked_lookalikes = await self._rank_lookalike_audiences(
                lookalike_candidates, config
            )
            
            # Apply size and quality filters
            filtered_lookalikes = await self._filter_audiences(
                ranked_lookalikes, config
            )
            
            logger.info(f"Found {len(filtered_lookalikes)} lookalike audiences")
            return filtered_lookalikes[:config.max_audiences]
            
        except Exception as e:
            logger.error(f"Error finding lookalike audiences: {str(e)}")
            raise
    
    async def find_custom_lookalikes(
        self,
        custom_profile: Dict[str, Any],
        config: Optional[LookalikeConfig] = None
    ) -> List[LookalikeAudience]:
        """
        Find lookalike audiences based on custom profile
        
        Args:
            custom_profile: Custom audience profile to match
            config: Configuration for lookalike finding
            
        Returns:
            List of lookalike audiences
        """
        try:
            if config is None:
                config = LookalikeConfig()
            
            logger.info("Finding lookalike audiences for custom profile")
            
            # Convert custom profile to feature vector
            source_features = await self._profile_to_features(custom_profile, config)
            
            # Get all candidate audiences
            candidate_audiences = await self._get_all_candidate_audiences(config)
            
            # Find similar audiences
            lookalike_candidates = []
            for candidate_id in candidate_audiences:
                candidate_features = await self._extract_audience_features(
                    candidate_id, config
                )
                
                similarity_score = await self._calculate_similarity(
                    source_features, candidate_features, config.similarity_method
                )
                
                if similarity_score >= config.similarity_threshold:
                    lookalike = await self._create_lookalike_audience(
                        candidate_id, similarity_score, source_features,
                        candidate_features, config
                    )
                    lookalike_candidates.append(lookalike)
            
            # Rank and return results
            ranked_lookalikes = await self._rank_lookalike_audiences(
                lookalike_candidates, config
            )
            
            return ranked_lookalikes[:config.max_audiences]
            
        except Exception as e:
            logger.error(f"Error finding custom lookalike audiences: {str(e)}")
            raise
    
    async def expand_audience_incrementally(
        self,
        source_audience_id: str,
        expansion_percentage: float = 50.0,
        quality_threshold: float = 0.8
    ) -> List[LookalikeAudience]:
        """
        Incrementally expand audience while maintaining quality
        
        Args:
            source_audience_id: Source audience to expand
            expansion_percentage: Target expansion percentage
            quality_threshold: Minimum quality score to maintain
            
        Returns:
            List of incremental expansion audiences
        """
        try:
            logger.info(f"Incremental expansion for audience: {source_audience_id}")
            
            # Start with high similarity threshold
            current_threshold = 0.95
            min_threshold = 0.70
            step_size = 0.05
            
            all_lookalikes = []
            current_expansion = 0.0
            
            while current_threshold >= min_threshold and current_expansion < expansion_percentage:
                config = LookalikeConfig(
                    similarity_threshold=current_threshold,
                    max_audiences=20
                )
                
                lookalikes = await self.find_lookalike_audiences(
                    source_audience_id, config
                )
                
                # Filter by quality threshold
                quality_lookalikes = [
                    la for la in lookalikes 
                    if la.quality_score >= quality_threshold
                ]
                
                if quality_lookalikes:
                    all_lookalikes.extend(quality_lookalikes)
                    
                    # Calculate current expansion
                    total_expansion_size = sum(la.estimated_size for la in quality_lookalikes)
                    current_expansion += total_expansion_size * 0.01  # Convert to percentage
                
                current_threshold -= step_size
            
            # Remove duplicates and rank by quality
            unique_lookalikes = await self._remove_duplicate_audiences(all_lookalikes)
            return sorted(unique_lookalikes, key=lambda x: x.quality_score, reverse=True)
            
        except Exception as e:
            logger.error(f"Error in incremental expansion: {str(e)}")
            raise
    
    async def _extract_audience_features(
        self, 
        audience_id: str, 
        config: LookalikeConfig
    ) -> Dict[str, Any]:
        """Extract comprehensive features from audience"""
        await asyncio.sleep(0.01)  # Simulate feature extraction
        
        features = {}
        
        if config.include_demographics:
            features['demographics'] = await self._extract_demographic_features(audience_id)
        
        if config.include_behaviors:
            features['behaviors'] = await self._extract_behavioral_features(audience_id)
        
        if config.include_interests:
            features['interests'] = await self._extract_interest_features(audience_id)
        
        if config.include_psychographics:
            features['psychographics'] = await self._extract_psychographic_features(audience_id)
        
        return features
    
    async def _extract_demographic_features(self, audience_id: str) -> Dict[str, float]:
        """Extract demographic feature vector"""
        await asyncio.sleep(0.01)
        
        # Simulate demographic feature extraction
        return {
            'age_18_24': 0.25,
            'age_25_34': 0.35,
            'age_35_44': 0.25,
            'age_45_plus': 0.15,
            'gender_male': 0.45,
            'gender_female': 0.55,
            'income_low': 0.20,
            'income_medium': 0.50,
            'income_high': 0.30,
            'education_high_school': 0.25,
            'education_college': 0.45,
            'education_graduate': 0.30,
            'urban': 0.60,
            'suburban': 0.30,
            'rural': 0.10
        }
    
    async def _extract_behavioral_features(self, audience_id: str) -> Dict[str, float]:
        """Extract behavioral feature vector"""
        await asyncio.sleep(0.01)
        
        return {
            'platform_instagram': 0.75,
            'platform_tiktok': 0.60,
            'platform_youtube': 0.55,
            'platform_facebook': 0.40,
            'platform_twitter': 0.35,
            'engagement_high': 0.30,
            'engagement_medium': 0.50,
            'engagement_low': 0.20,
            'content_creator': 0.15,
            'content_consumer': 0.85,
            'shopping_frequency_high': 0.25,
            'shopping_frequency_medium': 0.45,
            'shopping_frequency_low': 0.30
        }
    
    async def _extract_interest_features(self, audience_id: str) -> Dict[str, float]:
        """Extract interest-based feature vector"""
        await asyncio.sleep(0.01)
        
        return {
            'fitness': 0.45,
            'technology': 0.60,
            'fashion': 0.40,
            'travel': 0.55,
            'food': 0.50,
            'music': 0.65,
            'gaming': 0.35,
            'sports': 0.40,
            'art': 0.30,
            'business': 0.35,
            'education': 0.40,
            'health': 0.45
        }
    
    async def _extract_psychographic_features(self, audience_id: str) -> Dict[str, float]:
        """Extract psychographic feature vector"""
        await asyncio.sleep(0.01)
        
        return {
            'openness': 0.65,
            'conscientiousness': 0.55,
            'extraversion': 0.60,
            'agreeableness': 0.70,
            'neuroticism': 0.30,
            'innovators': 0.20,
            'achievers': 0.30,
            'experiencers': 0.25,
            'believers': 0.15,
            'strivers': 0.10
        }
    
    async def _calculate_similarity(
        self,
        source_features: Dict[str, Any],
        candidate_features: Dict[str, Any],
        method: SimilarityMethod
    ) -> float:
        """Calculate similarity between feature vectors"""
        await asyncio.sleep(0.01)
        
        if method == SimilarityMethod.HYBRID:
            # Weighted combination of different similarity methods
            cosine_sim = await self._cosine_similarity(source_features, candidate_features)
            jaccard_sim = await self._jaccard_similarity(source_features, candidate_features)
            euclidean_sim = await self._euclidean_similarity(source_features, candidate_features)
            
            # Weighted average
            return (cosine_sim * 0.5 + jaccard_sim * 0.3 + euclidean_sim * 0.2)
        
        elif method == SimilarityMethod.COSINE:
            return await self._cosine_similarity(source_features, candidate_features)
        
        elif method == SimilarityMethod.JACCARD:
            return await self._jaccard_similarity(source_features, candidate_features)
        
        elif method == SimilarityMethod.EUCLIDEAN:
            return await self._euclidean_similarity(source_features, candidate_features)
        
        else:
            return await self._cosine_similarity(source_features, candidate_features)
    
    async def _cosine_similarity(
        self, 
        features1: Dict[str, Any], 
        features2: Dict[str, Any]
    ) -> float:
        """Calculate cosine similarity between feature vectors"""
        await asyncio.sleep(0.01)
        
        # Flatten feature dictionaries
        vec1 = self._flatten_features(features1)
        vec2 = self._flatten_features(features2)
        
        # Calculate cosine similarity
        dot_product = sum(vec1[i] * vec2[i] for i in range(len(vec1)))
        norm1 = math.sqrt(sum(x * x for x in vec1))
        norm2 = math.sqrt(sum(x * x for x in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def _jaccard_similarity(
        self, 
        features1: Dict[str, Any], 
        features2: Dict[str, Any]
    ) -> float:
        """Calculate Jaccard similarity for categorical features"""
        await asyncio.sleep(0.01)
        
        # Convert to binary features for Jaccard calculation
        binary1 = self._to_binary_features(features1)
        binary2 = self._to_binary_features(features2)
        
        intersection = sum(1 for i in range(len(binary1)) if binary1[i] and binary2[i])
        union = sum(1 for i in range(len(binary1)) if binary1[i] or binary2[i])
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    async def _euclidean_similarity(
        self, 
        features1: Dict[str, Any], 
        features2: Dict[str, Any]
    ) -> float:
        """Calculate Euclidean similarity (converted from distance)"""
        await asyncio.sleep(0.01)
        
        vec1 = self._flatten_features(features1)
        vec2 = self._flatten_features(features2)
        
        # Calculate Euclidean distance
        distance = math.sqrt(sum((vec1[i] - vec2[i]) ** 2 for i in range(len(vec1))))
        
        # Convert distance to similarity (0-1 range)
        max_distance = math.sqrt(len(vec1))  # Maximum possible distance
        similarity = 1 - (distance / max_distance)
        
        return max(similarity, 0.0)
    
    def _flatten_features(self, features: Dict[str, Any]) -> List[float]:
        """Flatten nested feature dictionary to vector"""
        flattened = []
        
        for key, value in features.items():
            if isinstance(value, dict):
                flattened.extend(value.values())
            elif isinstance(value, (int, float)):
                flattened.append(float(value))
            elif isinstance(value, list):
                flattened.extend([float(x) for x in value if isinstance(x, (int, float))])
        
        return flattened
    
    def _to_binary_features(self, features: Dict[str, Any], threshold: float = 0.5) -> List[bool]:
        """Convert features to binary representation"""
        flattened = self._flatten_features(features)
        return [x > threshold for x in flattened]
    
    async def _create_lookalike_audience(
        self,
        candidate_id: str,
        similarity_score: float,
        source_features: Dict[str, Any],
        candidate_features: Dict[str, Any],
        config: LookalikeConfig
    ) -> LookalikeAudience:
        """Create LookalikeAudience object with detailed metrics"""
        await asyncio.sleep(0.01)
        
        # Calculate specific match scores
        demographic_match = await self._calculate_feature_match(
            source_features.get('demographics', {}),
            candidate_features.get('demographics', {})
        )
        
        behavioral_match = await self._calculate_feature_match(
            source_features.get('behaviors', {}),
            candidate_features.get('behaviors', {})
        )
        
        interest_match = await self._calculate_feature_match(
            source_features.get('interests', {}),
            candidate_features.get('interests', {})
        )
        
        # Estimate audience size and overlap
        estimated_size = await self._estimate_audience_size(candidate_id)
        overlap_percentage = await self._calculate_overlap_percentage(
            candidate_id, source_features
        )
        
        # Calculate quality score
        quality_score = await self._calculate_quality_score(
            similarity_score, demographic_match, behavioral_match, 
            interest_match, estimated_size
        )
        
        # Calculate expansion potential
        expansion_potential = await self._calculate_expansion_potential(
            estimated_size, overlap_percentage, quality_score
        )
        
        # Recommend budget
        recommended_budget = await self._calculate_recommended_budget(
            estimated_size, quality_score, config.expansion_strategy
        )
        
        return LookalikeAudience(
            audience_id=candidate_id,
            similarity_score=similarity_score,
            estimated_size=estimated_size,
            overlap_percentage=overlap_percentage,
            demographic_match=demographic_match,
            behavioral_match=behavioral_match,
            interest_match=interest_match,
            quality_score=quality_score,
            expansion_potential=expansion_potential,
            recommended_budget=recommended_budget
        )
    
    async def _calculate_feature_match(
        self, 
        source_features: Dict[str, float], 
        candidate_features: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate detailed feature-level matches"""
        await asyncio.sleep(0.01)
        
        matches = {}
        
        for key in source_features:
            if key in candidate_features:
                # Calculate similarity for this specific feature
                diff = abs(source_features[key] - candidate_features[key])
                similarity = 1 - diff  # Assuming values are normalized 0-1
                matches[key] = max(similarity, 0.0)
        
        return matches
    
    async def _estimate_audience_size(self, audience_id: str) -> int:
        """Estimate audience size"""
        await asyncio.sleep(0.01)
        
        # Simulate audience size estimation
        base_size = hash(audience_id) % 900000 + 100000  # Random size between 100K-1M
        return base_size
    
    async def _calculate_overlap_percentage(
        self, 
        candidate_id: str, 
        source_features: Dict[str, Any]
    ) -> float:
        """Calculate overlap percentage with source audience"""
        await asyncio.sleep(0.01)
        
        # Simulate overlap calculation
        return min(hash(candidate_id) % 20 + 5, 25.0)  # 5-25% overlap
    
    async def _calculate_quality_score(
        self,
        similarity_score: float,
        demographic_match: Dict[str, float],
        behavioral_match: Dict[str, float],
        interest_match: Dict[str, float],
        estimated_size: int
    ) -> float:
        """Calculate overall quality score"""
        await asyncio.sleep(0.01)
        
        # Weighted quality calculation
        demo_avg = sum(demographic_match.values()) / len(demographic_match) if demographic_match else 0.5
        behavior_avg = sum(behavioral_match.values()) / len(behavioral_match) if behavioral_match else 0.5
        interest_avg = sum(interest_match.values()) / len(interest_match) if interest_match else 0.5
        
        # Size factor (prefer medium-sized audiences)
        if 50000 <= estimated_size <= 500000:
            size_factor = 1.0
        elif 10000 <= estimated_size < 50000:
            size_factor = 0.9
        elif estimated_size < 10000:
            size_factor = 0.7
        else:
            size_factor = 0.8
        
        quality = (
            similarity_score * 0.4 +
            demo_avg * 0.2 +
            behavior_avg * 0.25 +
            interest_avg * 0.15
        ) * size_factor
        
        return min(quality, 1.0)
    
    async def _calculate_expansion_potential(
        self, 
        estimated_size: int, 
        overlap_percentage: float, 
        quality_score: float
    ) -> int:
        """Calculate expansion potential"""
        await asyncio.sleep(0.01)
        
        # Calculate unique audience size
        unique_size = estimated_size * (1 - overlap_percentage / 100)
        
        # Adjust by quality score
        expansion_potential = int(unique_size * quality_score)
        
        return expansion_potential
    
    async def _calculate_recommended_budget(
        self, 
        estimated_size: int, 
        quality_score: float, 
        strategy: ExpansionStrategy
    ) -> float:
        """Calculate recommended budget for this audience"""
        await asyncio.sleep(0.01)
        
        # Base cost per thousand impressions (CPM)
        base_cpm = 5.0
        
        # Adjust CPM by quality (higher quality = higher cost but better performance)
        adjusted_cpm = base_cpm * (1 + quality_score * 0.5)
        
        # Strategy multipliers
        strategy_multipliers = {
            ExpansionStrategy.CONSERVATIVE: 0.8,
            ExpansionStrategy.BALANCED: 1.0,
            ExpansionStrategy.AGGRESSIVE: 1.3,
            ExpansionStrategy.CUSTOM: 1.0
        }
        
        multiplier = strategy_multipliers.get(strategy, 1.0)
        final_cpm = adjusted_cpm * multiplier
        
        # Calculate budget for 3 impressions per user
        impressions = min(estimated_size * 3, 1000000)  # Cap at 1M impressions
        budget = (impressions / 1000) * final_cpm
        
        return round(budget, 2)
    
    async def _rank_lookalike_audiences(
        self, 
        lookalikes: List[LookalikeAudience], 
        config: LookalikeConfig
    ) -> List[LookalikeAudience]:
        """Rank lookalike audiences by multiple criteria"""
        await asyncio.sleep(0.01)
        
        # Multi-criteria ranking
        def ranking_score(lookalike: LookalikeAudience) -> float:
            return (
                lookalike.similarity_score * 0.4 +
                lookalike.quality_score * 0.3 +
                (lookalike.expansion_potential / 100000) * 0.2 +  # Normalize expansion potential
                (1 - lookalike.overlap_percentage / 100) * 0.1  # Prefer lower overlap
            )
        
        return sorted(lookalikes, key=ranking_score, reverse=True)
    
    async def _filter_audiences(
        self, 
        lookalikes: List[LookalikeAudience], 
        config: LookalikeConfig
    ) -> List[LookalikeAudience]:
        """Apply size and quality filters"""
        await asyncio.sleep(0.01)
        
        filtered = []
        
        for lookalike in lookalikes:
            # Size filters
            if not (config.min_audience_size <= lookalike.estimated_size <= config.max_audience_size):
                continue
            
            # Quality filter (require minimum quality based on strategy)
            min_quality = {
                ExpansionStrategy.CONSERVATIVE: 0.8,
                ExpansionStrategy.BALANCED: 0.7,
                ExpansionStrategy.AGGRESSIVE: 0.6,
                ExpansionStrategy.CUSTOM: 0.7
            }.get(config.expansion_strategy, 0.7)
            
            if lookalike.quality_score < min_quality:
                continue
            
            filtered.append(lookalike)
        
        return filtered
    
    async def _remove_duplicate_audiences(
        self, 
        lookalikes: List[LookalikeAudience]
    ) -> List[LookalikeAudience]:
        """Remove duplicate audiences, keeping the highest quality one"""
        await asyncio.sleep(0.01)
        
        seen_ids = set()
        unique_lookalikes = []
        
        # Sort by quality first
        sorted_lookalikes = sorted(lookalikes, key=lambda x: x.quality_score, reverse=True)
        
        for lookalike in sorted_lookalikes:
            if lookalike.audience_id not in seen_ids:
                unique_lookalikes.append(lookalike)
                seen_ids.add(lookalike.audience_id)
        
        return unique_lookalikes
    
    async def _get_candidate_audiences(
        self, 
        source_audience_id: str, 
        config: LookalikeConfig
    ) -> List[str]:
        """Get candidate audiences for comparison"""
        await asyncio.sleep(0.01)
        
        # Simulate database query for candidate audiences
        # In real implementation, this would query actual audience database
        candidates = [f"audience_{i}" for i in range(100, 150)]
        return [aid for aid in candidates if aid != source_audience_id]
    
    async def _get_all_candidate_audiences(self, config: LookalikeConfig) -> List[str]:
        """Get all available candidate audiences"""
        await asyncio.sleep(0.01)
        
        # Simulate getting all available audiences
        return [f"audience_{i}" for i in range(100, 200)]
    
    async def _profile_to_features(
        self, 
        profile: Dict[str, Any], 
        config: LookalikeConfig
    ) -> Dict[str, Any]:
        """Convert custom profile to feature vector format"""
        await asyncio.sleep(0.01)
        
        features = {}
        
        if config.include_demographics and 'demographics' in profile:
            features['demographics'] = profile['demographics']
        
        if config.include_behaviors and 'behaviors' in profile:
            features['behaviors'] = profile['behaviors']
        
        if config.include_interests and 'interests' in profile:
            features['interests'] = profile['interests']
        
        if config.include_psychographics and 'psychographics' in profile:
            features['psychographics'] = profile['psychographics']
        
        return features
    
    def _load_similarity_models(self) -> Dict[str, Any]:
        """Load pre-trained similarity models"""
        # In real implementation, load actual ML models
        return {
            'cosine_model': 'mock_cosine_model',
            'neural_similarity': 'mock_neural_model'
        }
    
    def _initialize_audience_database(self) -> Dict[str, Any]:
        """Initialize audience database connection"""
        # In real implementation, connect to actual database
        return {
            'connection': 'mock_db_connection',
            'cache': {}
        }
    
    def _load_feature_extractors(self) -> Dict[str, Any]:
        """Load feature extraction models"""
        # In real implementation, load actual feature extractors
        return {
            'demographic_extractor': 'mock_demo_extractor',
            'behavioral_extractor': 'mock_behavior_extractor',
            'interest_extractor': 'mock_interest_extractor'
        }