"""Recommendation engine for content optimization and collaboration matching."""

import logging
from typing import Dict, List, Tuple
from collections import defaultdict
import math

logger = logging.getLogger(__name__)

# Try to import numpy, fallback to math if not available
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False
    logger.warning("NumPy not available, using fallback math implementation")


class RecommendationEngine:
    def __init__(self):
        self.content_features = {}
        self.user_preferences = defaultdict(dict)
        if NUMPY_AVAILABLE:
            logger.info("RecommendationEngine initialized with NumPy support")
        else:
            logger.info("RecommendationEngine initialized with fallback math support")

    def analyze_content_similarity(self, content_features: Dict) -> Dict:
        """Analyze content similarity for recommendations."""
        # Extract key features for similarity computation
        feature_vector = self._extract_feature_vector(content_features)
        
        # Mock similarity computation with stored content
        similarities = []
        for stored_id, stored_features in self.content_features.items():
            similarity = self._compute_similarity(feature_vector, stored_features)
            similarities.append({
                "content_id": stored_id,
                "similarity_score": similarity,
                "match_reasons": self._get_match_reasons(content_features, stored_features)
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return {
            "similar_content": similarities[:5],
            "diversity_score": self._calculate_diversity(similarities),
            "recommendation_confidence": 0.85
        }

    def recommend_hashtags(self, content_features: Dict) -> List[str]:
        """Recommend hashtags based on content analysis."""
        base_tags = []
        
        # Based on media type
        media_type = content_features.get("media_type", "general")
        type_tags = {
            "audio": ["#music", "#audio", "#sound", "#podcast"],
            "video": ["#video", "#content", "#visual", "#entertainment"],
            "image": ["#photo", "#image", "#visual", "#art"],
            "text": ["#blog", "#writing", "#content", "#thoughts"]
        }.get(media_type, ["#content"])
        
        base_tags.extend(type_tags)
        
        # Based on sentiment/topic if available
        if "sentiment" in content_features:
            sentiment = content_features["sentiment"]
            if sentiment == "positive":
                base_tags.extend(["#positive", "#inspiration", "#motivation"])
            elif sentiment == "negative":
                base_tags.extend(["#real", "#honest", "#authentic"])
        
        # Based on detected keywords/topics
        if "keywords" in content_features:
            for keyword in content_features["keywords"][:3]:
                base_tags.append(f"#{keyword}")
        
        # Add trending/popular tags (mock data)
        trending = ["#viral", "#trending", "#creator", "#original"]
        base_tags.extend(trending[:2])
        
        return list(set(base_tags))[:10]  # Return unique tags, max 10

    def suggest_posting_times(self, user_profile: Dict) -> List[Dict]:
        """Suggest optimal posting times based on audience analysis."""
        # Mock audience analysis - in reality would use real data
        default_times = [
            {"time": "09:00", "timezone": "UTC", "engagement_score": 0.85, "reason": "morning_peak"},
            {"time": "13:00", "timezone": "UTC", "engagement_score": 0.75, "reason": "lunch_break"},
            {"time": "19:00", "timezone": "UTC", "engagement_score": 0.90, "reason": "evening_peak"},
            {"time": "21:00", "timezone": "UTC", "engagement_score": 0.80, "reason": "prime_time"}
        ]
        
        # Adjust based on content type if available
        content_type = user_profile.get("primary_content_type", "general")
        if content_type == "music":
            # Music content often performs better in evening
            for time_slot in default_times:
                if int(time_slot["time"].split(":")[0]) >= 17:
                    time_slot["engagement_score"] += 0.05
        
        return sorted(default_times, key=lambda x: x["engagement_score"], reverse=True)

    def recommend_collaborators(self, user_profile: Dict, content_features: Dict) -> List[Dict]:
        """Recommend potential collaborators based on content and profile."""
        # Mock collaborator database
        potential_collaborators = [
            {
                "name": "MusicProducer_Pro",
                "type": "music_producer",
                "compatibility_score": 0.92,
                "shared_interests": ["electronic", "ambient", "production"],
                "follower_count": 15000,
                "engagement_rate": 0.08
            },
            {
                "name": "VisualArtist_Creative",
                "type": "visual_artist", 
                "compatibility_score": 0.88,
                "shared_interests": ["art", "visual", "creative"],
                "follower_count": 8500,
                "engagement_rate": 0.12
            },
            {
                "name": "ContentCreator_Daily",
                "type": "content_creator",
                "compatibility_score": 0.75,
                "shared_interests": ["content", "daily", "lifestyle"],
                "follower_count": 25000,
                "engagement_rate": 0.06
            }
        ]
        
        # Filter and rank based on content features
        media_type = content_features.get("media_type", "general")
        
        # Boost scores for compatible types
        for collab in potential_collaborators:
            if media_type == "audio" and collab["type"] == "music_producer":
                collab["compatibility_score"] += 0.05
            elif media_type == "image" and collab["type"] == "visual_artist":
                collab["compatibility_score"] += 0.05
        
        return sorted(potential_collaborators, key=lambda x: x["compatibility_score"], reverse=True)

    def _extract_feature_vector(self, content_features: Dict) -> List[float]:
        """Extract numerical feature vector from content features."""
        # Simple feature extraction - in reality would be much more sophisticated
        features = []
        
        # Media type encoding
        media_types = ["audio", "video", "image", "text"]
        media_type = content_features.get("media_type", "text")
        media_encoding = [1.0 if mt == media_type else 0.0 for mt in media_types]
        features.extend(media_encoding)
        
        # Numerical features
        features.append(content_features.get("duration", 0.0))
        features.append(content_features.get("brightness", 0.0))
        features.append(content_features.get("contrast", 0.0))
        features.append(len(content_features.get("keywords", [])))
        
        if NUMPY_AVAILABLE:
            return np.array(features)
        else:
            return features

    def _compute_similarity(self, vec1, vec2) -> float:
        """Compute cosine similarity between two feature vectors."""
        if NUMPY_AVAILABLE and hasattr(vec1, 'shape') and hasattr(vec2, 'shape'):
            # Use numpy implementation
            if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
                return 0.0
            return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
        else:
            # Fallback implementation using basic math
            if not vec1 or not vec2 or len(vec1) != len(vec2):
                return 0.0
            
            # Compute dot product
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            
            # Compute norms
            norm1 = math.sqrt(sum(a * a for a in vec1))
            norm2 = math.sqrt(sum(b * b for b in vec2))
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)

    def _get_match_reasons(self, features1: Dict, features2: Dict) -> List[str]:
        """Get reasons why two pieces of content are similar."""
        reasons = []
        
        if features1.get("media_type") == features2.get("media_type"):
            reasons.append("same_media_type")
        
        # Check for keyword overlap
        keywords1 = set(features1.get("keywords", []))
        keywords2 = set(features2.get("keywords", []))
        if keywords1 & keywords2:
            reasons.append("shared_keywords")
        
        # Check for similar metrics
        brightness_diff = abs(features1.get("brightness", 0) - features2.get("brightness", 0))
        if brightness_diff < 20:
            reasons.append("similar_visual_style")
        
        return reasons[:3]  # Return top 3 reasons

    def _calculate_diversity(self, similarities: List[Dict]) -> float:
        """Calculate diversity score of recommended content."""
        if not similarities:
            return 0.0
        
        # Simple diversity based on score spread
        scores = [s["similarity_score"] for s in similarities[:5]]
        if len(scores) <= 1:
            return 0.0
        
        if NUMPY_AVAILABLE:
            score_std = np.std(scores)
        else:
            # Fallback calculation of standard deviation
            mean_score = sum(scores) / len(scores)
            variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
            score_std = math.sqrt(variance)
        
        return min(1.0, score_std * 2)  # Normalize to 0-1 range
