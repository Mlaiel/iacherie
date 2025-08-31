"""Recommendation Engine
AI-powered content and collaboration recommendations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ContentRecommendation:
    """Content recommendation structure"""    content_id: str
    title: str
    creator: str
    similarity_score: float
    recommendation_reason: str
    content_type: str
    estimated_engagement: float


@dataclass
class CollaborationRecommendation:
    """Collaboration recommendation structure"""    target_user_id: str
    username: str
    compatibility_score: float
    shared_interests: List[str]
    recommendation_reason: str
    collaboration_potential: str


@dataclass
class TrendRecommendation:
    """Trend recommendation structure"""    trend_id: str
    trend_name: str
    category: str
    growth_rate: float
    opportunity_score: float
    suggested_actions: List[str]
    time_sensitive: bool


class RecommendationEngine:
    """AI-powered recommendation system for content and collaborations"""    
    def __init__(self):
        self.user_profiles = {}
        self.content_database = {}
        self.interaction_history = {}
        self.trending_data = {}
        
    async def update_user_profile(
        self,
        user_id: str,
        interaction_data: Dict[str, Any]
    ):
        """Update user profile based on interactions"""        try:
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = {
                    "preferences": {},
                    "engagement_patterns": {},
                    "content_types": [],
                    "collaboration_history": [],
                    "genre_preferences": [],
                    "activity_times": [],
                    "platform_usage": {}
                }
            
            profile = self.user_profiles[user_id]
            
            # Update preferences based on interactions
            if "liked_content" in interaction_data:
                for content_id in interaction_data["liked_content"]:
                    # Analyze content to update preferences
                    await self._analyze_content_preferences(user_id, content_id, "like")
            
            if "shared_content" in interaction_data:
                for content_id in interaction_data["shared_content"]:
                    await self._analyze_content_preferences(user_id, content_id, "share")
            
            if "viewed_content" in interaction_data:
                for content_id in interaction_data["viewed_content"]:
                    await self._analyze_content_preferences(user_id, content_id, "view")
            
            # Update activity patterns
            if "activity_time" in interaction_data:
                profile["activity_times"].append(interaction_data["activity_time"])
                # Keep only last 30 entries
                profile["activity_times"] = profile["activity_times"][-30:]
            
            logger.info(f"User profile updated for {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
    
    async def get_content_recommendations(
        self,
        user_id: str,
        limit: int = 10,
        content_type: Optional[str] = None
    ) -> List[ContentRecommendation]:
        """Get personalized content recommendations"""        try:
            user_profile = self.user_profiles.get(user_id, {})
            recommendations = []
            
            # Get user preferences
            genre_preferences = user_profile.get("genre_preferences", [])
            preferred_types = user_profile.get("content_types", [])
            
            # Simulate content database query
            available_content = await self._get_available_content(content_type)
            
            for content in available_content:
                similarity_score = await self._calculate_content_similarity(
                    user_profile, content
                )
                
                if similarity_score >= 0.3:  # Minimum threshold
                    recommendation = ContentRecommendation(
                        content_id=content["id"],
                        title=content["title"],
                        creator=content["creator"],
                        similarity_score=similarity_score,
                        recommendation_reason=self._generate_recommendation_reason(
                            user_profile, content, similarity_score
                        ),
                        content_type=content["type"],
                        estimated_engagement=similarity_score * 0.8  # Simplified estimate
                    )
                    recommendations.append(recommendation)
            
            # Sort by similarity score
            recommendations.sort(key=lambda x: x.similarity_score, reverse=True)
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting content recommendations: {str(e)}")
            return []
    
    async def get_collaboration_recommendations(
        self,
        user_id: str,
        collaboration_type: str = "any",
        limit: int = 5
    ) -> List[CollaborationRecommendation]:
        """Get collaboration partner recommendations"""        try:
            user_profile = self.user_profiles.get(user_id, {})
            recommendations = []
            
            # Get potential collaborators
            for other_user_id, other_profile in self.user_profiles.items():
                if other_user_id == user_id:
                    continue
                
                compatibility_score = await self._calculate_collaboration_compatibility(
                    user_profile, other_profile
                )
                
                if compatibility_score >= 0.5:  # Minimum compatibility
                    shared_interests = self._find_shared_interests(user_profile, other_profile)
                    
                    recommendation = CollaborationRecommendation(
                        target_user_id=other_user_id,
                        username=f"user_{other_user_id}",  # Simplified
                        compatibility_score=compatibility_score,
                        shared_interests=shared_interests,
                        recommendation_reason=self._generate_collaboration_reason(
                            compatibility_score, shared_interests
                        ),
                        collaboration_potential=self._assess_collaboration_potential(
                            compatibility_score
                        )
                    )
                    recommendations.append(recommendation)
            
            # Sort by compatibility score
            recommendations.sort(key=lambda x: x.compatibility_score, reverse=True)
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting collaboration recommendations: {str(e)}")
            return []
    
    async def get_trending_recommendations(
        self,
        user_id: str,
        category: Optional[str] = None
    ) -> List[TrendRecommendation]:
        """Get trending topic and opportunity recommendations"""        try:
            user_profile = self.user_profiles.get(user_id, {})
            recommendations = []
            
            # Simulate trending data
            trending_topics = await self._get_trending_topics(category)
            
            for trend in trending_topics:
                # Calculate opportunity score based on user profile
                opportunity_score = await self._calculate_trend_opportunity(
                    user_profile, trend
                )
                
                if opportunity_score >= 0.4:  # Minimum opportunity threshold
                    recommendation = TrendRecommendation(
                        trend_id=trend["id"],
                        trend_name=trend["name"],
                        category=trend["category"],
                        growth_rate=trend["growth_rate"],
                        opportunity_score=opportunity_score,
                        suggested_actions=self._generate_trend_actions(trend, user_profile),
                        time_sensitive=trend["growth_rate"] > 0.5
                    )
                    recommendations.append(recommendation)
            
            # Sort by opportunity score
            recommendations.sort(key=lambda x: x.opportunity_score, reverse=True)
            
            return recommendations[:10]
            
        except Exception as e:
            logger.error(f"Error getting trending recommendations: {str(e)}")
            return []
    
    async def get_platform_optimization_recommendations(
        self,
        user_id: str
    ) -> Dict[str, List[str]]:
        """Get platform-specific optimization recommendations"""        try:
            user_profile = self.user_profiles.get(user_id, {})
            platform_usage = user_profile.get("platform_usage", {})
            
            recommendations = {}
            
            for platform, usage_data in platform_usage.items():
                platform_recommendations = []
                
                # Analyze platform performance
                engagement_rate = usage_data.get("engagement_rate", 0.0)
                posting_frequency = usage_data.get("posting_frequency", 0)
                peak_times = usage_data.get("peak_times", [])
                
                if engagement_rate < 0.05:  # Low engagement
                    platform_recommendations.extend([
                        "Improve content quality and visual appeal",
                        "Use trending hashtags relevant to your niche",
                        "Engage more with your audience through comments and messages",
                        "Post during peak audience activity times"
                    ])
                
                if posting_frequency < 3:  # Low posting frequency
                    platform_recommendations.extend([
                        "Increase posting frequency to maintain audience engagement",
                        "Create a content calendar for consistent posting",
                        "Consider batch content creation sessions"
                    ])
                
                if not peak_times:
                    platform_recommendations.append(
                        "Analyze your audience insights to identify optimal posting times"
                    )
                
                if platform == "youtube":
                    platform_recommendations.extend([
                        "Optimize video thumbnails for higher click-through rates",
                        "Create compelling video titles with SEO keywords",
                        "Add end screens and cards to promote other videos"
                    ])
                elif platform == "instagram":
                    platform_recommendations.extend([
                        "Use Instagram Stories and Reels for higher visibility",
                        "Collaborate with other creators through Stories",
                        "Utilize Instagram Shopping features if applicable"
                    ])
                elif platform == "tiktok":
                    platform_recommendations.extend([
                        "Jump on trending sounds and challenges quickly",
                        "Keep videos short and engaging from the first second",
                        "Use effects and filters to make content more visually appealing"
                    ])
                
                recommendations[platform] = platform_recommendations[:5]  # Top 5 per platform
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting platform optimization recommendations: {str(e)}")
            return {}
    
    async def generate_content_ideas(
        self,
        user_id: str,
        content_type: str = "music",
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate personalized content ideas"""        try:
            user_profile = self.user_profiles.get(user_id, {})
            genre_preferences = user_profile.get("genre_preferences", [])
            trending_topics = await self._get_trending_topics()
            
            content_ideas = []
            
            # Generate ideas based on user preferences and trends
            for i in range(count):
                if genre_preferences:
                    base_genre = genre_preferences[i % len(genre_preferences)]
                else:
                    base_genre = "electronic"  # Default
                
                if trending_topics:
                    trend = trending_topics[i % len(trending_topics)]
                    trend_element = trend["name"]
                else:
                    trend_element = "remix"
                
                idea = {
                    "id": f"idea_{user_id}_{i}",
                    "title": f"{base_genre.title()} {trend_element}",
                    "description": f"Create a {base_genre} track incorporating {trend_element} elements",
                    "genre": base_genre,
                    "trend_factor": trend_element,
                    "estimated_difficulty": "medium",
                    "estimated_engagement": 0.7,
                    "suggested_platforms": self._suggest_platforms_for_content(content_type, base_genre),
                    "inspiration_keywords": [base_genre, trend_element, "original", "creative"]
                }
                content_ideas.append(idea)
            
            return content_ideas
            
        except Exception as e:
            logger.error(f"Error generating content ideas: {str(e)}")
            return []
    
    async def _analyze_content_preferences(
        self,
        user_id: str,
        content_id: str,
        interaction_type: str
    ):
        """Analyze content to update user preferences"""        try:
            # Simulate content analysis
            content_data = {
                "genre": "electronic",
                "mood": "upbeat",
                "tempo": "fast",
                "instruments": ["synthesizer", "drums"],
                "style": "dance"
            }
            
            profile = self.user_profiles[user_id]
            
            # Weight interactions differently
            weight = {"view": 1, "like": 3, "share": 5}.get(interaction_type, 1)
            
            # Update genre preferences
            genre = content_data["genre"]
            if genre not in profile["genre_preferences"]:
                profile["genre_preferences"].append(genre)
            
            # Update other preferences based on weight
            for key, value in content_data.items():
                if key not in profile["preferences"]:
                    profile["preferences"][key] = {}
                if value not in profile["preferences"][key]:
                    profile["preferences"][key][value] = 0
                profile["preferences"][key][value] += weight
            
        except Exception as e:
            logger.error(f"Error analyzing content preferences: {str(e)}")
    
    async def _get_available_content(self, content_type: Optional[str]) -> List[Dict]:
        """Get available content for recommendations"""        try:
            # Simulate content database
            sample_content = [
                {
                    "id": "content_1",
                    "title": "Electronic Dreams",
                    "creator": "DJ_Producer_1",
                    "type": "music",
                    "genre": "electronic",
                    "tags": ["synthesizer", "ambient", "chill"],
                    "engagement_rate": 0.08
                },
                {
                    "id": "content_2", 
                    "title": "Acoustic Vibes",
                    "creator": "Acoustic_Artist",
                    "type": "music",
                    "genre": "acoustic",
                    "tags": ["guitar", "folk", "relaxing"],
                    "engagement_rate": 0.06
                },
                {
                    "id": "content_3",
                    "title": "Hip Hop Beats",
                    "creator": "Beat_Maker",
                    "type": "music", 
                    "genre": "hip-hop",
                    "tags": ["beats", "rap", "urban"],
                    "engagement_rate": 0.09
                }
            ]
            
            if content_type:
                return [c for c in sample_content if c["type"] == content_type]
            
            return sample_content
            
        except Exception as e:
            logger.error(f"Error getting available content: {str(e)}")
            return []
    
    async def _calculate_content_similarity(
        self,
        user_profile: Dict,
        content: Dict
    ) -> float:
        """Calculate similarity between user preferences and content"""        try:
            similarity_score = 0.0
            
            # Genre similarity
            user_genres = user_profile.get("genre_preferences", [])
            if content["genre"] in user_genres:
                similarity_score += 0.4
            
            # Tag similarity
            user_preferences = user_profile.get("preferences", {})
            content_tags = content.get("tags", [])
            
            tag_matches = 0
            for tag in content_tags:
                if any(tag in user_preferences.get(pref_type, {}) for pref_type in user_preferences):
                    tag_matches += 1
            
            if content_tags:
                tag_similarity = tag_matches / len(content_tags)
                similarity_score += tag_similarity * 0.3
            
            # Engagement compatibility
            content_engagement = content.get("engagement_rate", 0.0)
            if content_engagement > 0.05:  # Good engagement
                similarity_score += 0.3
            
            return min(1.0, similarity_score)
            
        except Exception as e:
            logger.error(f"Error calculating content similarity: {str(e)}")
            return 0.0
    
    async def _calculate_collaboration_compatibility(
        self,
        profile1: Dict,
        profile2: Dict
    ) -> float:
        """Calculate collaboration compatibility between two users"""        try:
            compatibility = 0.0
            
            # Genre overlap
            genres1 = set(profile1.get("genre_preferences", []))
            genres2 = set(profile2.get("genre_preferences", []))
            
            if genres1 and genres2:
                genre_overlap = len(genres1 & genres2) / len(genres1 | genres2)
                compatibility += genre_overlap * 0.4
            
            # Complementary skills (different content types)
            types1 = set(profile1.get("content_types", []))
            types2 = set(profile2.get("content_types", []))
            
            if types1 and types2:
                complementary = len(types1 - types2) / max(len(types1), 1)
                compatibility += min(complementary, 0.5) * 0.3
            
            # Activity time overlap
            times1 = profile1.get("activity_times", [])
            times2 = profile2.get("activity_times", [])
            
            if times1 and times2:
                # Simplified time overlap calculation
                compatibility += 0.3  # Assume some overlap
            
            return min(1.0, compatibility)
            
        except Exception as e:
            logger.error(f"Error calculating collaboration compatibility: {str(e)}")
            return 0.0
    
    def _find_shared_interests(self, profile1: Dict, profile2: Dict) -> List[str]:
        """Find shared interests between two user profiles"""        try:
            shared = []
            
            # Shared genres
            genres1 = set(profile1.get("genre_preferences", []))
            genres2 = set(profile2.get("genre_preferences", []))
            shared.extend(list(genres1 & genres2))
            
            # Shared content types
            types1 = set(profile1.get("content_types", []))
            types2 = set(profile2.get("content_types", []))
            shared.extend(list(types1 & types2))
            
            return shared[:5]  # Top 5 shared interests
            
        except Exception as e:
            logger.error(f"Error finding shared interests: {str(e)}")
            return []
    
    async def _get_trending_topics(self, category: Optional[str] = None) -> List[Dict]:
        """Get current trending topics"""        try:
            # Simulate trending topics
            trending = [
                {
                    "id": "trend_1",
                    "name": "Lo-fi Hip Hop",
                    "category": "music",
                    "growth_rate": 0.8,
                    "keywords": ["lo-fi", "chill", "study", "beats"]
                },
                {
                    "id": "trend_2",
                    "name": "Synthwave Revival",
                    "category": "music", 
                    "growth_rate": 0.6,
                    "keywords": ["synthwave", "80s", "neon", "retro"]
                },
                {
                    "id": "trend_3",
                    "name": "Collaborative Remixes",
                    "category": "collaboration",
                    "growth_rate": 0.7,
                    "keywords": ["remix", "collaboration", "featured"]
                }
            ]
            
            if category:
                return [t for t in trending if t["category"] == category]
            
            return trending
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {str(e)}")
            return []
    
    async def _calculate_trend_opportunity(
        self,
        user_profile: Dict,
        trend: Dict
    ) -> float:
        """Calculate opportunity score for user to participate in trend"""        try:
            opportunity = 0.0
            
            # Genre alignment
            user_genres = user_profile.get("genre_preferences", [])
            trend_keywords = trend.get("keywords", [])
            
            genre_match = any(genre in trend_keywords for genre in user_genres)
            if genre_match:
                opportunity += 0.4
            
            # Growth rate factor
            opportunity += trend["growth_rate"] * 0.3
            
            # User experience factor
            collab_history = len(user_profile.get("collaboration_history", []))
            experience_factor = min(collab_history / 5, 1.0)  # Normalize to 0-1
            opportunity += experience_factor * 0.3
            
            return min(1.0, opportunity)
            
        except Exception as e:
            logger.error(f"Error calculating trend opportunity: {str(e)}")
            return 0.0
    
    def _generate_recommendation_reason(
        self,
        user_profile: Dict,
        content: Dict,
        similarity_score: float
    ) -> str:
        """Generate human-readable recommendation reason"""        try:
            reasons = []
            
            user_genres = user_profile.get("genre_preferences", [])
            if content["genre"] in user_genres:
                reasons.append(f"matches your interest in {content['genre']} music")
            
            if similarity_score > 0.8:
                reasons.append("highly similar to your previous likes")
            elif similarity_score > 0.6:
                reasons.append("similar to content you've engaged with")
            
            if content.get("engagement_rate", 0) > 0.07:
                reasons.append("popular with other users")
            
            if reasons:
                return "Recommended because it " + " and ".join(reasons)
            else:
                return "Recommended based on your profile"
                
        except Exception as e:
            logger.error(f"Error generating recommendation reason: {str(e)}")
            return "Recommended for you"
    
    def _generate_collaboration_reason(
        self,
        compatibility_score: float,
        shared_interests: List[str]
    ) -> str:
        """Generate collaboration recommendation reason"""        try:
            if compatibility_score > 0.8:
                level = "highly compatible"
            elif compatibility_score > 0.6:
                level = "compatible"
            else:
                level = "potentially compatible"
            
            if shared_interests:
                interests_str = ", ".join(shared_interests[:2])
                return f"{level} collaborator with shared interests in {interests_str}"
            else:
                return f"{level} collaborator with complementary skills"
                
        except Exception as e:
            logger.error(f"Error generating collaboration reason: {str(e)}")
            return "Potential collaboration partner"
    
    def _assess_collaboration_potential(self, compatibility_score: float) -> str:
        """Assess collaboration potential level"""        if compatibility_score > 0.8:
            return "Very High"
        elif compatibility_score > 0.6:
            return "High"
        elif compatibility_score > 0.4:
            return "Medium"
        else:
            return "Low"
    
    def _generate_trend_actions(
        self,
        trend: Dict,
        user_profile: Dict
    ) -> List[str]:
        """Generate suggested actions for trending opportunity"""        try:
            actions = []
            
            trend_name = trend["name"]
            
            if "lo-fi" in trend_name.lower():
                actions.extend([
                    "Create a lo-fi version of your existing tracks",
                    "Collaborate with other lo-fi producers",
                    "Use lo-fi elements in your next release"
                ])
            elif "synthwave" in trend_name.lower():
                actions.extend([
                    "Experiment with 80s-inspired synth sounds",
                    "Create retro-aesthetic visuals for your content",
                    "Remix classic 80s tracks with modern production"
                ])
            elif "collaboration" in trend_name.lower():
                actions.extend([
                    "Reach out to potential collaboration partners",
                    "Offer remix services to other creators",
                    "Join collaborative challenges and projects"
                ])
            else:
                actions.extend([
                    f"Create content inspired by {trend_name}",
                    f"Use #{trend_name.replace(' ', '').lower()} hashtags",
                    "Engage with the trending community"
                ])
            
            return actions[:3]  # Top 3 actions
            
        except Exception as e:
            logger.error(f"Error generating trend actions: {str(e)}")
            return ["Explore this trending opportunity"]
    
    def _suggest_platforms_for_content(self, content_type: str, genre: str) -> List[str]:
        """Suggest optimal platforms for content type and genre"""        try:
            platforms = []
            
            if content_type == "music":
                platforms.extend(["spotify", "soundcloud", "youtube"])
                
                if genre in ["electronic", "dance"]:
                    platforms.append("tiktok")
                elif genre in ["acoustic", "folk"]:
                    platforms.append("instagram")
                elif genre in ["hip-hop", "rap"]:
                    platforms.extend(["tiktok", "twitter"])
            
            return platforms[:3]  # Top 3 platforms
            
        except Exception as e:
            logger.error(f"Error suggesting platforms: {str(e)}")
            return ["youtube", "instagram", "tiktok"]