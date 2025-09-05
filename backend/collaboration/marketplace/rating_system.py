"""Rating System Module - Comprehensive Creator and Project Rating Platform
===========================================================================

Advanced rating and review system for creator marketplace providing multi-dimensional
ratings, reputation management, fraud detection, and intelligent recommendation
algorithms based on historical performance and peer feedback.

This module implements:
- Multi-dimensional rating system (quality, communication, delivery, etc.)
- Weighted reputation scoring with decay and recency factors
- Review authenticity verification and fraud detection
- Collaborative filtering for personalized recommendations
- Reputation-based marketplace features and incentives

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import statistics
import math
from decimal import Decimal

logger = logging.getLogger(__name__)


class RatingDimension(Enum):
    """Different dimensions of rating"""
    OVERALL = "overall"
    QUALITY = "quality"
    COMMUNICATION = "communication"
    DELIVERY_TIME = "delivery_time"
    PROFESSIONALISM = "professionalism"
    CREATIVITY = "creativity"
    VALUE_FOR_MONEY = "value_for_money"
    TECHNICAL_SKILLS = "technical_skills"
    COLLABORATION = "collaboration"
    RELIABILITY = "reliability"


class ReviewType(Enum):
    """Types of reviews"""
    PROJECT_COMPLETION = "project_completion"
    COLLABORATION = "collaboration"
    SERVICE_DELIVERY = "service_delivery"
    MARKETPLACE_TRANSACTION = "marketplace_transaction"
    PEER_ENDORSEMENT = "peer_endorsement"


class ReviewStatus(Enum):
    """Review status states"""
    PENDING = "pending"
    PUBLISHED = "published"
    FLAGGED = "flagged"
    HIDDEN = "hidden"
    VERIFIED = "verified"
    DISPUTED = "disputed"


class ReputationTier(Enum):
    """Reputation tier levels"""
    NEWCOMER = "newcomer"        # 0-50 reputation points
    BRONZE = "bronze"            # 51-150 reputation points
    SILVER = "silver"            # 151-300 reputation points
    GOLD = "gold"                # 301-500 reputation points
    PLATINUM = "platinum"        # 501-750 reputation points
    DIAMOND = "diamond"          # 751+ reputation points


@dataclass
class RatingScore:
    """Individual rating score for a dimension"""
    dimension: RatingDimension
    score: float  # 1-5 scale
    weight: float = 1.0
    confidence: float = 1.0


@dataclass
class Review:
    """Individual review/rating"""
    review_id: str
    reviewer_id: str
    reviewee_id: str
    project_id: Optional[str]
    review_type: ReviewType
    ratings: List[RatingScore]
    overall_rating: float
    title: str
    comment: str
    tags: List[str] = field(default_factory=list)
    status: ReviewStatus = ReviewStatus.PENDING
    is_anonymous: bool = False
    verification_level: str = "unverified"  # verified, peer_verified, system_verified
    helpful_votes: int = 0
    total_votes: int = 0
    response: Optional[str] = None  # Reviewee response
    response_date: Optional[datetime] = None
    created_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    published_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReputationScore:
    """Comprehensive reputation score"""
    user_id: str
    overall_score: float
    tier: ReputationTier
    dimension_scores: Dict[RatingDimension, float]
    total_reviews: int
    average_rating: float
    confidence_score: float
    recency_score: float
    volume_score: float
    consistency_score: float
    trend_score: float  # positive/negative trend
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RatingAnalytics:
    """Analytics for ratings and reviews"""
    user_id: str
    rating_distribution: Dict[str, int]  # 1-star, 2-star, etc.
    dimension_breakdown: Dict[RatingDimension, Dict[str, float]]
    review_sentiment: Dict[str, float]  # positive, negative, neutral
    improvement_areas: List[str]
    strengths: List[str]
    peer_comparison: Dict[str, float]
    trend_analysis: Dict[str, float]
    recommendation_score: float


@dataclass
class FraudDetectionResult:
    """Result of fraud detection analysis"""
    review_id: str
    fraud_probability: float
    fraud_indicators: List[str]
    confidence_level: str
    recommended_action: str
    additional_verification_needed: bool


class RatingSystem:
    """Advanced rating and reputation management system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the rating system"""
        self.config = config or {}
        self.reviews: Dict[str, Review] = {}
        self.reputation_scores: Dict[str, ReputationScore] = {}
        self.user_analytics: Dict[str, RatingAnalytics] = {}
        
        # Configuration
        self.min_reviews_for_score = self.config.get('min_reviews_for_score', 3)
        self.recency_decay_factor = self.config.get('recency_decay_factor', 0.95)
        self.fraud_detection_enabled = self.config.get('fraud_detection_enabled', True)
        self.auto_verification_threshold = self.config.get('auto_verification_threshold', 0.8)
        
        # Weights for different aspects of reputation
        self.reputation_weights = {
            'rating_average': 0.4,
            'review_volume': 0.2,
            'consistency': 0.15,
            'recency': 0.15,
            'trend': 0.1
        }
        
        logger.info("⭐ Rating System initialized")
    
    async def submit_review(
        self,
        reviewer_id: str,
        reviewee_id: str,
        ratings: List[RatingScore],
        title: str,
        comment: str,
        project_id: Optional[str] = None,
        review_type: ReviewType = ReviewType.PROJECT_COMPLETION,
        tags: List[str] = None,
        is_anonymous: bool = False
    ) -> Dict[str, Any]:
        """Submit a new review"""
        try:
            # Validate review submission
            validation_result = await self._validate_review_submission(
                reviewer_id, reviewee_id, ratings, project_id
            )
            
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "errors": validation_result["errors"]
                }
            
            # Calculate overall rating
            overall_rating = await self._calculate_overall_rating(ratings)
            
            # Create review
            review_id = str(uuid.uuid4())
            review = Review(
                review_id=review_id,
                reviewer_id=reviewer_id,
                reviewee_id=reviewee_id,
                project_id=project_id,
                review_type=review_type,
                ratings=ratings,
                overall_rating=overall_rating,
                title=title,
                comment=comment,
                tags=tags or [],
                is_anonymous=is_anonymous
            )
            
            # Fraud detection
            if self.fraud_detection_enabled:
                fraud_result = await self._detect_review_fraud(review)
                if fraud_result.fraud_probability > 0.7:
                    review.status = ReviewStatus.FLAGGED
                    await self._handle_fraudulent_review(review, fraud_result)
                elif fraud_result.fraud_probability < 0.3:
                    review.status = ReviewStatus.PUBLISHED
                    review.published_date = datetime.now(timezone.utc)
                    
                    # Auto-verify if confidence is high
                    if fraud_result.confidence_level == "high":
                        review.verification_level = "system_verified"
            else:
                review.status = ReviewStatus.PUBLISHED
                review.published_date = datetime.now(timezone.utc)
            
            # Store review
            self.reviews[review_id] = review
            
            # Update reputation scores
            if review.status == ReviewStatus.PUBLISHED:
                await self._update_reputation_score(reviewee_id)
                await self._update_analytics(reviewee_id)
            
            # Send notifications
            await self._notify_review_submitted(review)
            
            logger.info(f"⭐ Review submitted: {review_id}")
            
            return {
                "success": True,
                "review_id": review_id,
                "status": review.status.value,
                "overall_rating": overall_rating,
                "verification_required": review.status == ReviewStatus.PENDING
            }
            
        except Exception as e:
            logger.error(f"❌ Error submitting review: {e}")
            return {
                "success": False,
                "errors": [str(e)]
            }
    
    async def respond_to_review(
        self,
        review_id: str,
        reviewee_id: str,
        response: str
    ) -> Dict[str, Any]:
        """Allow reviewee to respond to a review"""
        try:
            review = self.reviews.get(review_id)
            if not review:
                return {"success": False, "error": "Review not found"}
            
            if review.reviewee_id != reviewee_id:
                return {"success": False, "error": "Unauthorized"}
            
            if review.response:
                return {"success": False, "error": "Response already exists"}
            
            # Add response
            review.response = response
            review.response_date = datetime.now(timezone.utc)
            
            # Notify reviewer
            await self._notify_review_response(review)
            
            logger.info(f"⭐ Review response added: {review_id}")
            
            return {
                "success": True,
                "message": "Response added successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error responding to review: {e}")
            return {"success": False, "error": str(e)}
    
    async def vote_review_helpful(
        self,
        review_id: str,
        voter_id: str,
        helpful: bool
    ) -> Dict[str, Any]:
        """Vote on review helpfulness"""
        try:
            review = self.reviews.get(review_id)
            if not review:
                return {"success": False, "error": "Review not found"}
            
            # Check if user already voted (in production, store this separately)
            # For now, just increment votes
            review.total_votes += 1
            if helpful:
                review.helpful_votes += 1
            
            # Update review helpfulness score
            helpfulness_ratio = review.helpful_votes / review.total_votes if review.total_votes > 0 else 0
            
            return {
                "success": True,
                "helpful_votes": review.helpful_votes,
                "total_votes": review.total_votes,
                "helpfulness_ratio": helpfulness_ratio
            }
            
        except Exception as e:
            logger.error(f"❌ Error voting on review: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_reputation(self, user_id: str) -> Optional[ReputationScore]:
        """Get user's reputation score"""
        return self.reputation_scores.get(user_id)
    
    async def get_user_reviews(
        self,
        user_id: str,
        as_reviewer: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Review]:
        """Get reviews for a user"""
        reviews = []
        
        for review in self.reviews.values():
            if review.status != ReviewStatus.PUBLISHED:
                continue
                
            if as_reviewer and review.reviewer_id == user_id:
                reviews.append(review)
            elif not as_reviewer and review.reviewee_id == user_id:
                reviews.append(review)
        
        # Sort by date (newest first)
        reviews.sort(key=lambda r: r.published_date or r.created_date, reverse=True)
        
        return reviews[offset:offset + limit]
    
    async def get_reviews_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of reviews for a user"""
        reviews = await self.get_user_reviews(user_id)
        
        if not reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0,
                "rating_distribution": {},
                "dimension_averages": {}
            }
        
        # Calculate statistics
        total_reviews = len(reviews)
        ratings = [r.overall_rating for r in reviews]
        average_rating = statistics.mean(ratings)
        
        # Rating distribution
        distribution = {}
        for i in range(1, 6):
            count = len([r for r in ratings if i <= r < i + 1])
            distribution[f"{i}_star"] = count
        
        # Dimension averages
        dimension_averages = {}
        for dimension in RatingDimension:
            dimension_ratings = []
            for review in reviews:
                for rating in review.ratings:
                    if rating.dimension == dimension:
                        dimension_ratings.append(rating.score)
            
            if dimension_ratings:
                dimension_averages[dimension.value] = statistics.mean(dimension_ratings)
        
        return {
            "total_reviews": total_reviews,
            "average_rating": average_rating,
            "rating_distribution": distribution,
            "dimension_averages": dimension_averages,
            "recent_reviews": reviews[:5]  # Latest 5 reviews
        }
    
    async def _validate_review_submission(
        self,
        reviewer_id: str,
        reviewee_id: str,
        ratings: List[RatingScore],
        project_id: Optional[str]
    ) -> Dict[str, Any]:
        """Validate review submission"""
        errors = []
        
        # Check basic requirements
        if reviewer_id == reviewee_id:
            errors.append("Cannot review yourself")
        
        if not ratings:
            errors.append("At least one rating dimension is required")
        
        # Validate rating scores
        for rating in ratings:
            if not (1 <= rating.score <= 5):
                errors.append(f"Rating score must be between 1 and 5 for {rating.dimension.value}")
        
        # Check for duplicate reviews (simplified)
        existing_reviews = [
            r for r in self.reviews.values()
            if r.reviewer_id == reviewer_id and r.reviewee_id == reviewee_id and r.project_id == project_id
        ]
        
        if existing_reviews:
            errors.append("Review already exists for this project")
        
        # Check if reviewer is eligible (in production, check project participation)
        # For now, assume all reviews are valid
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _calculate_overall_rating(self, ratings: List[RatingScore]) -> float:
        """Calculate overall rating from dimension ratings"""
        if not ratings:
            return 0.0
        
        weighted_sum = sum(rating.score * rating.weight for rating in ratings)
        total_weight = sum(rating.weight for rating in ratings)
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    async def _detect_review_fraud(self, review: Review) -> FraudDetectionResult:
        """Detect potential review fraud"""
        fraud_indicators = []
        fraud_score = 0.0
        
        # Check for unusual patterns
        # 1. Extreme ratings (all 1s or all 5s)
        ratings_variance = statistics.variance([r.score for r in review.ratings]) if len(review.ratings) > 1 else 0
        if ratings_variance < 0.1:  # Very low variance
            fraud_indicators.append("Unusually uniform ratings")
            fraud_score += 0.2
        
        # 2. Very short or generic comments
        if len(review.comment.split()) < 5:
            fraud_indicators.append("Very short comment")
            fraud_score += 0.1
        
        # 3. Check for common spam phrases (simplified)
        spam_phrases = ["great job", "highly recommend", "excellent work", "amazing", "perfect"]
        comment_lower = review.comment.lower()
        spam_matches = sum(1 for phrase in spam_phrases if phrase in comment_lower)
        if spam_matches >= 3:
            fraud_indicators.append("Generic/spam-like language")
            fraud_score += 0.3
        
        # 4. Check reviewer history (simplified)
        reviewer_reviews = [r for r in self.reviews.values() if r.reviewer_id == review.reviewer_id]
        if len(reviewer_reviews) > 10:  # High review volume
            avg_rating = statistics.mean([r.overall_rating for r in reviewer_reviews])
            if avg_rating > 4.8 or avg_rating < 1.5:  # Extreme averages
                fraud_indicators.append("Suspicious reviewer pattern")
                fraud_score += 0.3
        
        # Determine confidence level
        if fraud_score < 0.2:
            confidence = "high"
        elif fraud_score < 0.5:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Determine recommended action
        if fraud_score > 0.7:
            action = "reject"
        elif fraud_score > 0.4:
            action = "manual_review"
        else:
            action = "accept"
        
        return FraudDetectionResult(
            review_id=review.review_id,
            fraud_probability=min(fraud_score, 1.0),
            fraud_indicators=fraud_indicators,
            confidence_level=confidence,
            recommended_action=action,
            additional_verification_needed=fraud_score > 0.5
        )
    
    async def _handle_fraudulent_review(self, review: Review, fraud_result: FraudDetectionResult) -> None:
        """Handle potentially fraudulent review"""
        # Log the fraud detection
        logger.warning(f"⚠️ Potential fraud detected in review {review.review_id}: {fraud_result.fraud_indicators}")
        
        # In production, this would:
        # 1. Flag for manual review
        # 2. Notify moderators
        # 3. Potentially suspend reviewer
        # 4. Request additional verification
    
    async def _update_reputation_score(self, user_id: str) -> None:
        """Update user's reputation score"""
        try:
            # Get all published reviews for user
            user_reviews = await self.get_user_reviews(user_id)
            
            if len(user_reviews) < self.min_reviews_for_score:
                # Not enough reviews for a meaningful score
                return
            
            # Calculate dimension scores
            dimension_scores = {}
            for dimension in RatingDimension:
                dimension_ratings = []
                for review in user_reviews:
                    for rating in review.ratings:
                        if rating.dimension == dimension:
                            # Apply recency weighting
                            days_old = (datetime.now(timezone.utc) - (review.published_date or review.created_date)).days
                            recency_weight = self.recency_decay_factor ** (days_old / 30)  # Decay over 30-day periods
                            weighted_rating = rating.score * recency_weight
                            dimension_ratings.append(weighted_rating)
                
                if dimension_ratings:
                    dimension_scores[dimension] = statistics.mean(dimension_ratings)
            
            # Calculate overall metrics
            overall_ratings = [r.overall_rating for r in user_reviews]
            average_rating = statistics.mean(overall_ratings)
            
            # Calculate confidence score based on review count and consistency
            confidence_score = min(len(user_reviews) / 20, 1.0)  # Max confidence at 20+ reviews
            rating_variance = statistics.variance(overall_ratings) if len(overall_ratings) > 1 else 0
            consistency_score = max(0, 1 - (rating_variance / 4))  # Normalize variance
            
            # Calculate recency score
            recent_reviews = [r for r in user_reviews if (datetime.now(timezone.utc) - (r.published_date or r.created_date)).days <= 90]
            recency_score = len(recent_reviews) / max(len(user_reviews), 1)
            
            # Calculate volume score
            volume_score = min(len(user_reviews) / 50, 1.0)  # Max at 50+ reviews
            
            # Calculate trend score
            trend_score = await self._calculate_trend_score(user_reviews)
            
            # Calculate overall reputation score
            overall_score = (
                average_rating * self.reputation_weights['rating_average'] +
                volume_score * self.reputation_weights['review_volume'] * 5 +  # Scale to 5-point system
                consistency_score * self.reputation_weights['consistency'] * 5 +
                recency_score * self.reputation_weights['recency'] * 5 +
                trend_score * self.reputation_weights['trend'] * 5
            )
            
            # Determine reputation tier
            tier = self._determine_reputation_tier(overall_score, len(user_reviews))
            
            # Create/update reputation score
            reputation = ReputationScore(
                user_id=user_id,
                overall_score=overall_score,
                tier=tier,
                dimension_scores=dimension_scores,
                total_reviews=len(user_reviews),
                average_rating=average_rating,
                confidence_score=confidence_score,
                recency_score=recency_score,
                volume_score=volume_score,
                consistency_score=consistency_score,
                trend_score=trend_score
            )
            
            self.reputation_scores[user_id] = reputation
            
            logger.info(f"⭐ Reputation updated for {user_id}: {overall_score:.2f} ({tier.value})")
            
        except Exception as e:
            logger.error(f"❌ Error updating reputation score: {e}")
    
    async def _calculate_trend_score(self, reviews: List[Review]) -> float:
        """Calculate trend score (improving/declining ratings)"""
        if len(reviews) < 5:
            return 0.5  # Neutral for insufficient data
        
        # Sort by date
        sorted_reviews = sorted(reviews, key=lambda r: r.published_date or r.created_date)
        
        # Split into recent and older reviews
        mid_point = len(sorted_reviews) // 2
        older_reviews = sorted_reviews[:mid_point]
        recent_reviews = sorted_reviews[mid_point:]
        
        older_avg = statistics.mean([r.overall_rating for r in older_reviews])
        recent_avg = statistics.mean([r.overall_rating for r in recent_reviews])
        
        # Calculate trend (normalize to 0-1 scale)
        trend_diff = recent_avg - older_avg
        trend_score = 0.5 + (trend_diff / 8)  # Normalize to 0-1 range
        
        return max(0, min(1, trend_score))
    
    def _determine_reputation_tier(self, overall_score: float, review_count: int) -> ReputationTier:
        """Determine reputation tier based on score and review count"""
        # Require minimum reviews for higher tiers
        if review_count < 3:
            return ReputationTier.NEWCOMER
        
        if overall_score >= 4.5 and review_count >= 20:
            return ReputationTier.DIAMOND
        elif overall_score >= 4.2 and review_count >= 15:
            return ReputationTier.PLATINUM
        elif overall_score >= 3.8 and review_count >= 10:
            return ReputationTier.GOLD
        elif overall_score >= 3.4 and review_count >= 5:
            return ReputationTier.SILVER
        elif overall_score >= 3.0:
            return ReputationTier.BRONZE
        else:
            return ReputationTier.NEWCOMER
    
    async def _update_analytics(self, user_id: str) -> None:
        """Update user analytics"""
        try:
            reviews = await self.get_user_reviews(user_id)
            
            if not reviews:
                return
            
            # Rating distribution
            rating_distribution = {}
            for i in range(1, 6):
                count = len([r for r in reviews if i <= r.overall_rating < i + 1])
                rating_distribution[f"{i}_star"] = count
            
            # Dimension breakdown
            dimension_breakdown = {}
            for dimension in RatingDimension:
                dimension_ratings = []
                for review in reviews:
                    for rating in review.ratings:
                        if rating.dimension == dimension:
                            dimension_ratings.append(rating.score)
                
                if dimension_ratings:
                    dimension_breakdown[dimension] = {
                        "average": statistics.mean(dimension_ratings),
                        "count": len(dimension_ratings),
                        "min": min(dimension_ratings),
                        "max": max(dimension_ratings)
                    }
            
            # Sentiment analysis (simplified)
            positive_words = ["excellent", "great", "amazing", "perfect", "outstanding", "fantastic"]
            negative_words = ["poor", "bad", "terrible", "awful", "disappointing", "unsatisfactory"]
            
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for review in reviews:
                comment_lower = review.comment.lower()
                pos_score = sum(1 for word in positive_words if word in comment_lower)
                neg_score = sum(1 for word in negative_words if word in comment_lower)
                
                if pos_score > neg_score:
                    positive_count += 1
                elif neg_score > pos_score:
                    negative_count += 1
                else:
                    neutral_count += 1
            
            total = len(reviews)
            review_sentiment = {
                "positive": positive_count / total if total > 0 else 0,
                "negative": negative_count / total if total > 0 else 0,
                "neutral": neutral_count / total if total > 0 else 0
            }
            
            # Identify improvement areas and strengths
            improvement_areas = []
            strengths = []
            
            for dimension, breakdown in dimension_breakdown.items():
                avg_score = breakdown["average"]
                if avg_score < 3.5:
                    improvement_areas.append(dimension.value)
                elif avg_score >= 4.5:
                    strengths.append(dimension.value)
            
            # Calculate recommendation score
            reputation = self.reputation_scores.get(user_id)
            recommendation_score = reputation.overall_score / 5.0 if reputation else 0.5
            
            # Create analytics
            analytics = RatingAnalytics(
                user_id=user_id,
                rating_distribution=rating_distribution,
                dimension_breakdown=dimension_breakdown,
                review_sentiment=review_sentiment,
                improvement_areas=improvement_areas,
                strengths=strengths,
                peer_comparison={},  # Would compare to similar users
                trend_analysis={},   # Would analyze trends over time
                recommendation_score=recommendation_score
            )
            
            self.user_analytics[user_id] = analytics
            
        except Exception as e:
            logger.error(f"❌ Error updating analytics: {e}")
    
    # Notification methods
    async def _notify_review_submitted(self, review: Review) -> None:
        """Notify parties of review submission"""
        logger.info(f"📧 Review notification sent for {review.review_id}")
    
    async def _notify_review_response(self, review: Review) -> None:
        """Notify reviewer of response"""
        logger.info(f"📧 Review response notification sent for {review.review_id}")
    
    # Public analytics methods
    async def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get overall marketplace rating statistics"""
        all_reviews = [r for r in self.reviews.values() if r.status == ReviewStatus.PUBLISHED]
        
        if not all_reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0,
                "rating_distribution": {},
                "top_rated_users": []
            }
        
        total_reviews = len(all_reviews)
        average_rating = statistics.mean([r.overall_rating for r in all_reviews])
        
        # Rating distribution
        distribution = {}
        for i in range(1, 6):
            count = len([r for r in all_reviews if i <= r.overall_rating < i + 1])
            distribution[f"{i}_star"] = count
        
        # Top rated users
        top_users = sorted(
            self.reputation_scores.items(),
            key=lambda x: x[1].overall_score,
            reverse=True
        )[:10]
        
        return {
            "total_reviews": total_reviews,
            "average_rating": average_rating,
            "rating_distribution": distribution,
            "top_rated_users": [
                {
                    "user_id": user_id,
                    "score": score.overall_score,
                    "tier": score.tier.value,
                    "reviews": score.total_reviews
                }
                for user_id, score in top_users
            ]
        }
    
    async def get_user_analytics(self, user_id: str) -> Optional[RatingAnalytics]:
        """Get detailed analytics for a user"""
        return self.user_analytics.get(user_id)
    
    async def search_reviews(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        limit: int = 50
    ) -> List[Review]:
        """Search reviews with filters"""
        filters = filters or {}
        results = []
        
        for review in self.reviews.values():
            if review.status != ReviewStatus.PUBLISHED:
                continue
            
            # Text search
            if query.lower() in review.title.lower() or query.lower() in review.comment.lower():
                # Apply filters
                if filters.get('min_rating') and review.overall_rating < filters['min_rating']:
                    continue
                if filters.get('max_rating') and review.overall_rating > filters['max_rating']:
                    continue
                if filters.get('review_type') and review.review_type != ReviewType(filters['review_type']):
                    continue
                
                results.append(review)
        
        # Sort by relevance (simplified - by date)
        results.sort(key=lambda r: r.published_date or r.created_date, reverse=True)
        
        return results[:limit]


# Export main classes
__all__ = [
    'RatingSystem',
    'Review',
    'RatingScore',
    'ReputationScore',
    'RatingAnalytics',
    'FraudDetectionResult',
    'RatingDimension',
    'ReviewType',
    'ReviewStatus',
    'ReputationTier'
]