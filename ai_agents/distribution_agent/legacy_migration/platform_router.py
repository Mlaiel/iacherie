"""Platform Router for intelligent content distribution.
Routes content to optimal platforms based on content analysis and business logic.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent. All rights reserved.
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import asyncio

from .models.distribution_models import ContentMetadata, ContentType, PlatformType
from .platform_registry import get_platform_registry

logger = logging.getLogger(__name__)

class PlatformRouter:
    """    Intelligent router that determines the best platforms for content distribution
    based on content analysis, audience targeting, and business objectives.
    """    
    def __init__(self):
        self.platform_registry = get_platform_registry()
        
        # Platform scoring weights
        self.scoring_weights = {
            "content_match": 0.3,      # How well content fits platform
            "audience_match": 0.25,    # Target audience alignment
            "engagement_potential": 0.2, # Expected engagement
            "monetization_potential": 0.15, # Revenue potential
            "platform_growth": 0.1     # Platform growth trends
        }
        
        logger.info("Platform Router initialized with intelligent routing algorithms")
    
    async def route_content(
        self,
        content_metadata: ContentMetadata,
        business_objectives: Dict[str, Any] = None,
        budget_constraints: Dict[str, float] = None,
        target_audience: Dict[str, Any] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """        Route content to optimal platforms with confidence scores and reasoning.
        Returns list of (platform_name, confidence_score, routing_details)
        """        try:
            if not business_objectives:
                business_objectives = {"primary": "engagement", "secondary": "reach"}
            
            if not budget_constraints:
                budget_constraints = {"total": 1000.0, "per_platform": 200.0}
            
            if not target_audience:
                target_audience = content_metadata.target_audience or {}
            
            # Get all available platforms
            available_platforms = self.platform_registry.list_platforms()
            
            # Score each platform
            platform_scores = []
            
            for platform_name in available_platforms:
                try:
                    score, details = await self._score_platform(
                        platform_name,
                        content_metadata,
                        business_objectives,
                        budget_constraints,
                        target_audience
                    )
                    
                    platform_scores.append((platform_name, score, details))
                    
                except Exception as e:
                    logger.error(f"Failed to score platform {platform_name}: {e}")
                    continue
            
            # Sort by score (highest first)
            platform_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Filter by minimum confidence threshold
            min_confidence = 0.3
            qualified_platforms = [
                (platform, score, details) 
                for platform, score, details in platform_scores 
                if score >= min_confidence
            ]
            
            logger.info(f"Routed content to {len(qualified_platforms)} qualified platforms")
            return qualified_platforms
            
        except Exception as e:
            logger.error(f"Content routing failed: {e}")
            return []
    
    async def _score_platform(
        self,
        platform_name: str,
        content_metadata: ContentMetadata,
        business_objectives: Dict[str, Any],
        budget_constraints: Dict[str, float],
        target_audience: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """Score a platform for content suitability."""        try:
            platform_config = self.platform_registry.get_platform_config(platform_name)
            if not platform_config:
                return 0.0, {"error": "Platform configuration not found"}
            
            scores = {}
            details = {
                "platform_name": platform_name,
                "scoring_breakdown": {},
                "recommendations": [],
                "considerations": []
            }
            
            # Content match score
            content_score = await self._calculate_content_match_score(
                content_metadata, platform_config
            )
            scores["content_match"] = content_score
            details["scoring_breakdown"]["content_match"] = content_score
            
            # Audience match score
            audience_score = await self._calculate_audience_match_score(
                target_audience, platform_config
            )
            scores["audience_match"] = audience_score
            details["scoring_breakdown"]["audience_match"] = audience_score
            
            # Engagement potential score
            engagement_score = await self._calculate_engagement_potential_score(
                content_metadata, platform_config
            )
            scores["engagement_potential"] = engagement_score
            details["scoring_breakdown"]["engagement_potential"] = engagement_score
            
            # Monetization potential score
            monetization_score = await self._calculate_monetization_potential_score(
                content_metadata, platform_config, business_objectives
            )
            scores["monetization_potential"] = monetization_score
            details["scoring_breakdown"]["monetization_potential"] = monetization_score
            
            # Platform growth score
            growth_score = await self._calculate_platform_growth_score(
                platform_config
            )
            scores["platform_growth"] = growth_score
            details["scoring_breakdown"]["platform_growth"] = growth_score
            
            # Calculate weighted final score
            final_score = sum(
                scores[category] * self.scoring_weights[category]
                for category in scores
            )
            
            # Add recommendations based on scores
            details["recommendations"] = await self._generate_recommendations(
                platform_name, scores, content_metadata
            )
            
            # Add considerations
            details["considerations"] = await self._generate_considerations(
                platform_name, platform_config, content_metadata
            )
            
            return min(final_score, 1.0), details
            
        except Exception as e:
            logger.error(f"Platform scoring failed for {platform_name}: {e}")
            return 0.0, {"error": str(e)}
    
    async def _calculate_content_match_score(
        self,
        content_metadata: ContentMetadata,
        platform_config: Dict[str, Any]
    ) -> float:
        """Calculate how well content matches platform capabilities."""        try:
            score = 0.0
            
            # Content type compatibility (40% of content match)
            content_type = content_metadata.content_type
            supported_types = platform_config.get("supported_content_types", [])
            
            if content_type.value in [t.lower() if hasattr(t, 'lower') else str(t).lower() for t in supported_types]:
                score += 0.4
            
            # Format compatibility (20% of content match)
            if content_metadata.format and platform_config.get("supported_formats"):
                supported_formats = platform_config["supported_formats"]
                if content_metadata.format.lower() in [f.lower() for f in supported_formats]:
                    score += 0.2
            else:
                score += 0.1  # Neutral if no format specified
            
            # Size limitations (20% of content match)
            if content_metadata.size and platform_config.get("max_file_size"):
                max_size = platform_config["max_file_size"]
                if content_metadata.size <= max_size:
                    score += 0.2
                elif content_metadata.size <= max_size * 1.5:  # Within 150% of limit
                    score += 0.1
            else:
                score += 0.15  # Neutral if no size constraints
            
            # Duration limitations (20% of content match)
            if content_metadata.duration and platform_config.get("max_duration"):
                max_duration = platform_config["max_duration"]
                if content_metadata.duration <= max_duration:
                    score += 0.2
                elif content_metadata.duration <= max_duration * 1.2:  # Within 120% of limit
                    score += 0.1
            else:
                score += 0.15  # Neutral if no duration constraints
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Content match scoring failed: {e}")
            return 0.3  # Default moderate score
    
    async def _calculate_audience_match_score(
        self,
        target_audience: Dict[str, Any],
        platform_config: Dict[str, Any]
    ) -> float:
        """Calculate audience alignment score."""        try:
            if not target_audience:
                return 0.5  # Neutral score for unspecified audience
            
            score = 0.0
            
            # Age demographics (40% of audience match)
            target_age_range = target_audience.get("age_range", [18, 65])
            platform_demographics = platform_config.get("demographics", {})
            platform_age_range = platform_demographics.get("primary_age_range", [18, 65])
            
            # Calculate age range overlap
            overlap_start = max(target_age_range[0], platform_age_range[0])
            overlap_end = min(target_age_range[1], platform_age_range[1])
            
            if overlap_end > overlap_start:
                overlap_ratio = (overlap_end - overlap_start) / (target_age_range[1] - target_age_range[0])
                score += 0.4 * overlap_ratio
            
            # Interest alignment (30% of audience match)
            target_interests = target_audience.get("interests", [])
            platform_interests = platform_config.get("popular_content_categories", [])
            
            if target_interests and platform_interests:
                interest_overlap = len(set(target_interests) & set(platform_interests))
                max_possible_overlap = min(len(target_interests), len(platform_interests))
                if max_possible_overlap > 0:
                    score += 0.3 * (interest_overlap / max_possible_overlap)
            else:
                score += 0.15  # Neutral if no interest data
            
            # Geographic alignment (20% of audience match)
            target_locations = target_audience.get("locations", [])
            platform_regions = platform_config.get("strong_regions", [])
            
            if target_locations and platform_regions:
                location_overlap = len(set(target_locations) & set(platform_regions))
                if location_overlap > 0:
                    score += 0.2
                else:
                    score += 0.1
            else:
                score += 0.15  # Neutral if no location data
            
            # Engagement behavior (10% of audience match)
            target_behavior = target_audience.get("engagement_style", "mixed")
            platform_behavior = platform_config.get("typical_engagement_style", "mixed")
            
            if target_behavior == platform_behavior:
                score += 0.1
            else:
                score += 0.05
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Audience match scoring failed: {e}")
            return 0.5  # Default neutral score
    
    async def _calculate_engagement_potential_score(
        self,
        content_metadata: ContentMetadata,
        platform_config: Dict[str, Any]
    ) -> float:
        """Calculate expected engagement potential."""        try:
            score = 0.0
            
            # Content type engagement multiplier (30% of engagement potential)
            content_type = content_metadata.content_type
            engagement_multipliers = {
                ContentType.VIDEO: 0.9,      # High engagement
                ContentType.IMAGE: 0.7,      # Good engagement
                ContentType.AUDIO: 0.6,      # Medium engagement
                ContentType.TEXT: 0.4,       # Lower engagement
                ContentType.LIVE_STREAM: 0.95, # Very high engagement
                ContentType.STORY: 0.8,      # High engagement
                ContentType.REEL: 0.9        # High engagement
            }
            
            content_multiplier = engagement_multipliers.get(content_type, 0.5)
            score += 0.3 * content_multiplier
            
            # Platform algorithm favorability (25% of engagement potential)
            algorithm_boost = platform_config.get("algorithm_boost_factors", {})
            content_category = content_metadata.category or "general"
            
            if content_category.lower() in algorithm_boost:
                boost_factor = algorithm_boost[content_category.lower()]
                score += 0.25 * boost_factor
            else:
                score += 0.125  # Neutral boost
            
            # Hashtag and SEO potential (20% of engagement potential)
            if content_metadata.hashtags:
                hashtag_count = len(content_metadata.hashtags)
                max_hashtags = platform_config.get("max_hashtags", 30)
                
                # Optimal hashtag usage (not too few, not too many)
                if 3 <= hashtag_count <= max_hashtags * 0.8:
                    score += 0.2
                elif hashtag_count > 0:
                    score += 0.1
            
            # Timing and freshness (15% of engagement potential)
            content_age_hours = (datetime.now() - content_metadata.created_at).total_seconds() / 3600
            
            if content_age_hours < 1:  # Very fresh content
                score += 0.15
            elif content_age_hours < 24:  # Fresh content
                score += 0.12
            elif content_age_hours < 168:  # Week-old content
                score += 0.08
            else:
                score += 0.05  # Older content
            
            # Quality indicators (10% of engagement potential)
            quality_score = 0
            if content_metadata.resolution and "1080" in str(content_metadata.resolution):
                quality_score += 0.5
            if content_metadata.thumbnail_path:
                quality_score += 0.3
            if len(content_metadata.description) > 50:
                quality_score += 0.2
            
            score += 0.1 * min(quality_score, 1.0)
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Engagement potential scoring failed: {e}")
            return 0.5  # Default moderate score
    
    async def _calculate_monetization_potential_score(
        self,
        content_metadata: ContentMetadata,
        platform_config: Dict[str, Any],
        business_objectives: Dict[str, Any]
    ) -> float:
        """Calculate monetization potential score."""        try:
            if not content_metadata.monetization_enabled:
                return 0.0
            
            score = 0.0
            
            # Platform monetization support (40% of monetization potential)
            if platform_config.get("monetization_available", False):
                monetization_features = platform_config.get("monetization_features", [])
                feature_count = len(monetization_features)
                score += 0.4 * min(feature_count / 5, 1.0)  # Up to 5 features considered optimal
            
            # Revenue sharing model (30% of monetization potential)
            creator_share = platform_config.get("creator_revenue_share", 50)
            if creator_share >= 70:
                score += 0.3
            elif creator_share >= 50:
                score += 0.2
            elif creator_share >= 30:
                score += 0.1
            
            # Content type monetization fit (20% of monetization potential)
            content_type = content_metadata.content_type
            high_monetization_types = [
                ContentType.VIDEO, ContentType.LIVE_STREAM, 
                ContentType.AUDIO, ContentType.ARTICLE
            ]
            
            if content_type in high_monetization_types:
                score += 0.2
            else:
                score += 0.1
            
            # Business objective alignment (10% of monetization potential)
            primary_objective = business_objectives.get("primary", "engagement")
            if primary_objective in ["revenue", "monetization", "sales"]:
                score += 0.1
            else:
                score += 0.05
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Monetization potential scoring failed: {e}")
            return 0.3  # Default moderate score
    
    async def _calculate_platform_growth_score(
        self,
        platform_config: Dict[str, Any]
    ) -> float:
        """Calculate platform growth and trend score."""        try:
            # This would ideally use real market data
            # For now, using predefined growth scores based on 2024 trends
            platform_growth_scores = {
                "tiktok": 0.95,      # Very high growth
                "youtube": 0.85,     # Strong growth
                "instagram": 0.8,    # Good growth
                "twitch": 0.75,      # Gaming growth
                "discord": 0.7,      # Community growth
                "linkedin": 0.65,    # Professional growth
                "spotify": 0.6,      # Steady music growth
                "twitter": 0.5,      # Moderate growth
                "facebook": 0.45,    # Slower growth
                "pinterest": 0.4     # Niche growth
            }
            
            platform_name = platform_config.get("platform_name", "").lower()
            growth_score = platform_growth_scores.get(platform_name, 0.5)
            
            # Adjust based on platform maturity and saturation
            user_base_size = platform_config.get("estimated_active_users", 1000000)
            if user_base_size > 2000000000:  # Very large platforms (2B+ users)
                growth_score *= 0.9  # Slight penalty for saturation
            elif user_base_size < 100000000:  # Smaller platforms (100M- users)
                growth_score *= 1.1  # Bonus for growth potential
            
            return min(growth_score, 1.0)
            
        except Exception as e:
            logger.error(f"Platform growth scoring failed: {e}")
            return 0.5  # Default moderate score
    
    async def _generate_recommendations(
        self,
        platform_name: str,
        scores: Dict[str, float],
        content_metadata: ContentMetadata
    ) -> List[str]:
        """Generate actionable recommendations for platform optimization."""        recommendations = []
        
        try:
            # Content optimization recommendations
            if scores.get("content_match", 0) < 0.7:
                recommendations.append(
                    f"Consider optimizing content format/size for {platform_name} requirements"
                )
            
            # Engagement optimization recommendations
            if scores.get("engagement_potential", 0) < 0.6:
                if not content_metadata.hashtags:
                    recommendations.append("Add relevant hashtags to improve discoverability")
                
                if not content_metadata.thumbnail_path and content_metadata.content_type == ContentType.VIDEO:
                    recommendations.append("Add an attractive thumbnail for better click-through rates")
            
            # Monetization recommendations
            if scores.get("monetization_potential", 0) > 0.7:
                recommendations.append(
                    f"High monetization potential on {platform_name} - consider premium content strategy"
                )
            
            # Audience targeting recommendations
            if scores.get("audience_match", 0) < 0.5:
                recommendations.append(
                    f"Refine targeting strategy to better align with {platform_name} audience"
                )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Consider platform-specific optimization"]
    
    async def _generate_considerations(
        self,
        platform_name: str,
        platform_config: Dict[str, Any],
        content_metadata: ContentMetadata
    ) -> List[str]:
        """Generate important considerations for the platform."""        considerations = []
        
        try:
            # Content policy considerations
            if platform_config.get("requires_review", False):
                considerations.append(
                    f"{platform_name} requires content review - expect longer processing times"
                )
            
            # Rate limiting considerations
            rate_limit = platform_config.get("rate_limit_per_hour", 0)
            if rate_limit < 10:
                considerations.append(
                    f"Limited to {rate_limit} uploads per hour on {platform_name}"
                )
            
            # Monetization requirements
            if platform_config.get("monetization_available") and content_metadata.monetization_enabled:
                min_requirements = platform_config.get("monetization_requirements", {})
                if min_requirements:
                    considerations.append(
                        f"Ensure you meet {platform_name} monetization requirements: {min_requirements}"
                    )
            
            # Content format considerations
            max_size = platform_config.get("max_file_size", 0)
            if max_size > 0 and content_metadata.size and content_metadata.size > max_size * 0.8:
                considerations.append(
                    f"File size is near {platform_name} limits - consider compression"
                )
            
            return considerations
            
        except Exception as e:
            logger.error(f"Considerations generation failed: {e}")
            return [f"Review {platform_name} specific requirements"]
    
    async def get_routing_analytics(
        self,
        routing_results: List[Tuple[str, float, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Generate analytics and insights from routing results."""        try:
            analytics = {
                "total_platforms_evaluated": len(routing_results),
                "qualified_platforms": len([r for r in routing_results if r[1] >= 0.3]),
                "top_platform": routing_results[0] if routing_results else None,
                "average_confidence": sum(r[1] for r in routing_results) / len(routing_results) if routing_results else 0,
                "platform_rankings": [(r[0], r[1]) for r in routing_results],
                "category_insights": {},
                "recommendations_summary": []
            }
            
            # Analyze scoring categories
            if routing_results:
                category_scores = {}
                for platform, score, details in routing_results:
                    scoring_breakdown = details.get("scoring_breakdown", {})
                    for category, category_score in scoring_breakdown.items():
                        if category not in category_scores:
                            category_scores[category] = []
                        category_scores[category].append(category_score)
                
                # Calculate average scores per category
                for category, scores in category_scores.items():
                    analytics["category_insights"][category] = {
                        "average_score": sum(scores) / len(scores),
                        "best_platform": max(routing_results, 
                                           key=lambda x: x[2].get("scoring_breakdown", {}).get(category, 0))[0],
                        "recommendation": await self._get_category_recommendation(category, scores)
                    }
                
                # Collect all recommendations
                all_recommendations = []
                for platform, score, details in routing_results:
                    all_recommendations.extend(details.get("recommendations", []))
                
                # Deduplicate and prioritize recommendations
                unique_recommendations = list(set(all_recommendations))
                analytics["recommendations_summary"] = unique_recommendations[:5]  # Top 5
            
            return analytics
            
        except Exception as e:
            logger.error(f"Routing analytics generation failed: {e}")
            return {"error": str(e)}
    
    async def _get_category_recommendation(
        self,
        category: str,
        scores: List[float]
    ) -> str:
        """Get recommendation for a scoring category."""        avg_score = sum(scores) / len(scores)
        
        recommendations = {
            "content_match": {
                "high": "Content is well-suited for most platforms",
                "medium": "Consider format optimization for better platform compatibility",
                "low": "Content may need significant optimization for platform requirements"
            },
            "audience_match": {
                "high": "Target audience aligns well with platform demographics",
                "medium": "Audience targeting could be refined for better alignment",
                "low": "Consider adjusting content strategy for better audience fit"
            },
            "engagement_potential": {
                "high": "Content has strong viral potential across platforms",
                "medium": "Add engagement elements like hashtags and compelling thumbnails",
                "low": "Consider content format changes to boost engagement potential"
            },
            "monetization_potential": {
                "high": "Strong revenue opportunities across selected platforms",
                "medium": "Focus on platforms with better monetization features",
                "low": "Consider value-add content strategies for better monetization"
            },
            "platform_growth": {
                "high": "Leveraging trending platforms for maximum reach",
                "medium": "Good mix of established and growing platforms",
                "low": "Consider including more growth-oriented platforms"
            }
        }
        
        category_recs = recommendations.get(category, {})
        
        if avg_score >= 0.7:
            return category_recs.get("high", "Strong performance in this category")
        elif avg_score >= 0.4:
            return category_recs.get("medium", "Moderate performance in this category")
        else:
            return category_recs.get("low", "Needs improvement in this category")

# Export singleton instance
platform_router = PlatformRouter()
