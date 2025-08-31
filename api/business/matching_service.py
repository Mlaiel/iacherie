"""Matching business service for IA Influencer Agent platform.

This service handles intelligent matching between content creators for 
collaborations, partnerships, and content discovery using AI algorithms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from ..core.config import get_settings
from ..core.database import get_db
from ..models.user import User
from ..models.content import Content
from ..models.collaboration import Collaboration
from ..utils.ml_models import ContentEmbeddingModel, UserProfileModel
from ..services.analytics import AnalyticsService

logger = logging.getLogger(__name__)
settings = get_settings()

class MatchingService:
    """    AI-powered matching service for content creator collaborations.
    
    Features:
    - Content-based matching using ML embeddings
    - User profile similarity analysis
    - Collaboration history optimization
    - Genre and style compatibility
    - Audience overlap analysis
    - Success prediction modeling
    """    
    def __init__(self):
        self.content_embedding = ContentEmbeddingModel()
        self.user_profile_model = UserProfileModel()
        self.analytics = AnalyticsService()
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    
    async def find_collaboration_matches(
        self, 
        user_id: uuid.UUID,
        match_criteria: Dict[str, Any],
        limit: int = 50,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """        Find optimal collaboration matches for a user based on AI analysis.
        
        Args:
            user_id: ID of user seeking collaboration
            match_criteria: Criteria for matching (genre, role, audience, etc.)
            limit: Maximum number of matches to return
            db: Database session
            
        Returns:
            Sorted list of collaboration matches with compatibility scores
        """        try:
            if not db:
                db = next(get_db())
            
            # Get requesting user profile
            requesting_user = await self._get_user_profile(user_id, db)
            if not requesting_user:
                raise ValueError(f"User {user_id} not found")
            
            # Get potential collaboration partners
            potential_partners = await self._get_potential_partners(
                requesting_user, match_criteria, db
            )
            
            if not potential_partners:
                return []
            
            # Calculate compatibility scores
            matches = []
            for partner in potential_partners:
                compatibility_score = await self._calculate_compatibility_score(
                    requesting_user, partner, db
                )
                
                if compatibility_score >= settings.MIN_COMPATIBILITY_THRESHOLD:
                    match_data = {
                        "user_id": partner.id,
                        "username": partner.username,
                        "full_name": partner.full_name,
                        "role": partner.role,
                        "compatibility_score": compatibility_score,
                        "match_reasons": await self._get_match_reasons(
                            requesting_user, partner, compatibility_score
                        ),
                        "collaboration_potential": await self._predict_collaboration_success(
                            requesting_user, partner, db
                        ),
                        "audience_overlap": await self._calculate_audience_overlap(
                            requesting_user, partner, db
                        ),
                        "content_synergy": await self._analyze_content_synergy(
                            requesting_user, partner, db
                        ),
                        "profile_image": partner.profile_image_url,
                        "verified": partner.is_verified,
                        "last_active": partner.last_activity_at
                    }
                    matches.append(match_data)
            
            # Sort by compatibility score and success prediction
            matches.sort(
                key=lambda x: (x["compatibility_score"], x["collaboration_potential"]), 
                reverse=True
            )
            
            logger.info(f"Found {len(matches)} collaboration matches for user {user_id}")
            return matches[:limit]
            
        except Exception as e:
            logger.error(f"Error finding collaboration matches: {str(e)}")
            raise
    
    async def find_content_matches(
        self,
        content_id: uuid.UUID,
        match_type: str,
        limit: int = 20,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """        Find similar content or complementary content for cross-promotion.
        
        Args:
            content_id: ID of content to match against
            match_type: Type of matching ('similar', 'complementary', 'remix')
            limit: Maximum number of matches to return
            db: Database session
            
        Returns:
            List of matching content with similarity scores
        """        try:
            if not db:
                db = next(get_db())
            
            # Get source content
            source_content = db.query(Content).filter(Content.id == content_id).first()
            if not source_content:
                raise ValueError(f"Content {content_id} not found")
            
            # Get content embeddings
            source_embedding = await self.content_embedding.get_embedding(source_content)
            
            # Find candidate contents
            candidate_contents = await self._get_candidate_contents(
                source_content, match_type, db
            )
            
            matches = []
            for candidate in candidate_contents:
                candidate_embedding = await self.content_embedding.get_embedding(candidate)
                
                if match_type == "similar":
                    similarity_score = await self._calculate_content_similarity(
                        source_embedding, candidate_embedding
                    )
                elif match_type == "complementary":
                    similarity_score = await self._calculate_content_complementarity(
                        source_content, candidate, db
                    )
                elif match_type == "remix":
                    similarity_score = await self._calculate_remix_potential(
                        source_content, candidate, db
                    )
                
                if similarity_score >= settings.MIN_CONTENT_MATCH_THRESHOLD:
                    match_data = {
                        "content_id": candidate.id,
                        "title": candidate.title,
                        "description": candidate.description,
                        "file_type": candidate.file_type,
                        "category": candidate.category,
                        "owner_id": candidate.owner_id,
                        "owner_username": candidate.owner.username,
                        "similarity_score": similarity_score,
                        "match_type": match_type,
                        "thumbnail_url": candidate.thumbnail_url,
                        "duration": getattr(candidate.metadata, 'duration', None),
                        "view_count": candidate.view_count,
                        "like_count": candidate.like_count,
                        "created_at": candidate.created_at
                    }
                    matches.append(match_data)
            
            # Sort by similarity score
            matches.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            logger.info(f"Found {len(matches)} {match_type} content matches for {content_id}")
            return matches[:limit]
            
        except Exception as e:
            logger.error(f"Error finding content matches: {str(e)}")
            raise
    
    async def create_collaboration_request(
        self,
        requester_id: uuid.UUID,
        partner_id: uuid.UUID,
        collaboration_type: str,
        proposal_data: Dict[str, Any],
        db: Session = None
    ) -> Dict[str, Any]:
        """        Create a collaboration request between users.
        
        Args:
            requester_id: ID of user making the request
            partner_id: ID of user receiving the request
            collaboration_type: Type of collaboration
            proposal_data: Collaboration proposal details
            db: Database session
            
        Returns:
            Created collaboration request data
        """        try:
            if not db:
                db = next(get_db())
            
            # Validate users exist and are eligible for collaboration
            await self._validate_collaboration_eligibility(
                requester_id, partner_id, db
            )
            
            # Create collaboration record
            collaboration = Collaboration(
                id=uuid.uuid4(),
                requester_id=requester_id,
                partner_id=partner_id,
                collaboration_type=collaboration_type,
                status="pending",
                proposal_data=proposal_data,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            
            # Calculate initial match score
            requester = db.query(User).filter(User.id == requester_id).first()
            partner = db.query(User).filter(User.id == partner_id).first()
            
            collaboration.compatibility_score = await self._calculate_compatibility_score(
                requester, partner, db
            )
            
            db.add(collaboration)
            db.commit()
            db.refresh(collaboration)
            
            logger.info(f"Collaboration request created: {requester_id} -> {partner_id}")
            
            return {
                "collaboration_id": collaboration.id,
                "status": collaboration.status,
                "compatibility_score": collaboration.compatibility_score,
                "expires_at": collaboration.expires_at,
                "created_at": collaboration.created_at
            }
            
        except Exception as e:
            logger.error(f"Error creating collaboration request: {str(e)}")
            if db:
                db.rollback()
            raise
    
    async def get_match_recommendations(
        self,
        user_id: uuid.UUID,
        recommendation_type: str,
        db: Session = None
    ) -> Dict[str, Any]:
        """        Get personalized match recommendations for a user.
        
        Args:
            user_id: User ID for recommendations
            recommendation_type: Type of recommendations ('daily', 'trending', 'personal')
            db: Database session
            
        Returns:
            Comprehensive recommendation data
        """        try:
            if not db:
                db = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            recommendations = {
                "user_id": user_id,
                "recommendation_type": recommendation_type,
                "generated_at": datetime.utcnow(),
                "collaborations": [],
                "content_matches": [],
                "trending_creators": [],
                "personalized_suggestions": []
            }
            
            if recommendation_type in ["daily", "personal"]:
                # Get personalized collaboration recommendations
                recommendations["collaborations"] = await self.find_collaboration_matches(
                    user_id, {"personalized": True}, limit=10, db=db
                )
                
                # Get personalized content recommendations
                user_contents = db.query(Content).filter(
                    Content.owner_id == user_id
                ).order_by(desc(Content.created_at)).limit(5).all()
                
                for content in user_contents:
                    content_matches = await self.find_content_matches(
                        content.id, "similar", limit=5, db=db
                    )
                    recommendations["content_matches"].extend(content_matches)
            
            if recommendation_type in ["daily", "trending"]:
                # Get trending creators in user's categories
                recommendations["trending_creators"] = await self._get_trending_creators(
                    user, db
                )
            
            # Add success prediction and insights
            recommendations["insights"] = await self._generate_match_insights(user, db)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating match recommendations: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _get_user_profile(self, user_id: uuid.UUID, db: Session) -> Optional[User]:
        """Get comprehensive user profile for matching."""        return db.query(User).filter(
            and_(User.id == user_id, User.is_active == True)
        ).first()
    
    async def _get_potential_partners(
        self, 
        user: User, 
        criteria: Dict[str, Any], 
        db: Session
    ) -> List[User]:
        """Find potential collaboration partners based on criteria."""        query = db.query(User).filter(
            and_(
                User.id != user.id,
                User.is_active == True,
                User.enable_collaboration == True
            )
        )
        
        # Apply criteria filters
        if "role" in criteria:
            query = query.filter(User.role.in_(criteria["role"]))
        
        if "content_formats" in criteria:
            formats = criteria["content_formats"]
            query = query.filter(
                func.array_overlap(User.supported_content_formats, formats)
            )
        
        if "minimum_followers" in criteria:
            query = query.filter(User.follower_count >= criteria["minimum_followers"])
        
        if "verified_only" in criteria and criteria["verified_only"]:
            query = query.filter(User.is_verified == True)
        
        return query.limit(200).all()
    
    async def _calculate_compatibility_score(
        self, 
        user1: User, 
        user2: User, 
        db: Session
    ) -> float:
        """Calculate compatibility score between two users using ML."""        try:
            # Content format compatibility (30%)
            format_score = self._calculate_format_compatibility(user1, user2)
            
            # Genre/category compatibility (25%)
            genre_score = await self._calculate_genre_compatibility(user1, user2, db)
            
            # Audience compatibility (20%)
            audience_score = await self._calculate_audience_compatibility(user1, user2, db)
            
            # Collaboration history (15%)
            history_score = await self._calculate_collaboration_history_score(user1, user2, db)
            
            # Profile completeness and activity (10%)
            activity_score = self._calculate_activity_compatibility(user1, user2)
            
            # Weighted final score
            compatibility_score = (
                format_score * 0.30 +
                genre_score * 0.25 +
                audience_score * 0.20 +
                history_score * 0.15 +
                activity_score * 0.10
            )
            
            return round(compatibility_score, 3)
            
        except Exception as e:
            logger.error(f"Error calculating compatibility score: {str(e)}")
            return 0.0
    
    def _calculate_format_compatibility(self, user1: User, user2: User) -> float:
        """Calculate content format compatibility score."""        if not user1.supported_content_formats or not user2.supported_content_formats:
            return 0.0
        
        formats1 = set(user1.supported_content_formats)
        formats2 = set(user2.supported_content_formats)
        
        intersection = len(formats1.intersection(formats2))
        union = len(formats1.union(formats2))
        
        return intersection / union if union > 0 else 0.0
    
    async def _calculate_genre_compatibility(
        self, 
        user1: User, 
        user2: User, 
        db: Session
    ) -> float:
        """Calculate genre/category compatibility score."""        try:
            # Get recent content for both users
            user1_contents = db.query(Content).filter(
                Content.owner_id == user1.id
            ).order_by(desc(Content.created_at)).limit(10).all()
            
            user2_contents = db.query(Content).filter(
                Content.owner_id == user2.id
            ).order_by(desc(Content.created_at)).limit(10).all()
            
            if not user1_contents or not user2_contents:
                return 0.5  # Neutral score if no content
            
            # Extract categories and tags
            user1_features = []
            user2_features = []
            
            for content in user1_contents:
                features = [content.category] + (content.tags or [])
                user1_features.extend(features)
            
            for content in user2_contents:
                features = [content.category] + (content.tags or [])
                user2_features.extend(features)
            
            # Use TF-IDF for similarity
            if user1_features and user2_features:
                user1_text = " ".join(user1_features)
                user2_text = " ".join(user2_features)
                
                vectors = self.tfidf_vectorizer.fit_transform([user1_text, user2_text])
                similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
                
                return max(0.0, min(1.0, similarity))
            
            return 0.5
            
        except Exception as e:
            logger.error(f"Error calculating genre compatibility: {str(e)}")
            return 0.5
    
    async def _calculate_audience_compatibility(
        self, 
        user1: User, 
        user2: User, 
        db: Session
    ) -> float:
        """Calculate audience overlap and compatibility."""        try:
            # Get audience analytics for both users
            user1_analytics = await self.analytics.get_user_audience_data(user1.id, db)
            user2_analytics = await self.analytics.get_user_audience_data(user2.id, db)
            
            if not user1_analytics or not user2_analytics:
                return 0.5
            
            # Calculate audience overlap metrics
            demographic_score = self._compare_demographics(
                user1_analytics.get("demographics", {}),
                user2_analytics.get("demographics", {})
            )
            
            geographic_score = self._compare_geographic_data(
                user1_analytics.get("geographic", {}),
                user2_analytics.get("geographic", {})
            )
            
            interest_score = self._compare_interests(
                user1_analytics.get("interests", []),
                user2_analytics.get("interests", [])
            )
            
            # Weighted audience compatibility
            audience_score = (
                demographic_score * 0.4 +
                geographic_score * 0.3 +
                interest_score * 0.3
            )
            
            return audience_score
            
        except Exception as e:
            logger.error(f"Error calculating audience compatibility: {str(e)}")
            return 0.5
    
    def _compare_demographics(self, demo1: Dict, demo2: Dict) -> float:
        """Compare demographic data between audiences."""        if not demo1 or not demo2:
            return 0.5
        
        age_similarity = self._compare_age_ranges(
            demo1.get("age_ranges", {}), 
            demo2.get("age_ranges", {})
        )
        
        gender_similarity = self._compare_gender_distribution(
            demo1.get("gender", {}),
            demo2.get("gender", {})
        )
        
        return (age_similarity + gender_similarity) / 2
    
    def _compare_age_ranges(self, ages1: Dict, ages2: Dict) -> float:
        """Compare age range distributions."""        if not ages1 or not ages2:
            return 0.5
        
        # Calculate overlap in age distributions
        overlap_score = 0.0
        total_weight = 0.0
        
        for age_range in ages1:
            if age_range in ages2:
                weight1 = ages1[age_range]
                weight2 = ages2[age_range]
                overlap_score += min(weight1, weight2)
                total_weight += max(weight1, weight2)
        
        return overlap_score / total_weight if total_weight > 0 else 0.5
    
    def _compare_gender_distribution(self, gender1: Dict, gender2: Dict) -> float:
        """Compare gender distributions."""        if not gender1 or not gender2:
            return 0.5
        
        # Simple similarity based on distribution overlap
        male_diff = abs(gender1.get("male", 0) - gender2.get("male", 0))
        female_diff = abs(gender1.get("female", 0) - gender2.get("female", 0))
        
        total_diff = male_diff + female_diff
        return max(0.0, 1.0 - total_diff / 200.0)  # Normalize to 0-1
    
    def _compare_geographic_data(self, geo1: Dict, geo2: Dict) -> float:
        """Compare geographic audience data."""        if not geo1 or not geo2:
            return 0.5
        
        # Compare top countries/regions
        countries1 = set(geo1.get("top_countries", []))
        countries2 = set(geo2.get("top_countries", []))
        
        if not countries1 or not countries2:
            return 0.5
        
        intersection = len(countries1.intersection(countries2))
        union = len(countries1.union(countries2))
        
        return intersection / union if union > 0 else 0.0
    
    def _compare_interests(self, interests1: List, interests2: List) -> float:
        """Compare audience interests."""        if not interests1 or not interests2:
            return 0.5
        
        set1 = set(interests1)
        set2 = set(interests2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    async def _calculate_collaboration_history_score(
        self, 
        user1: User, 
        user2: User, 
        db: Session
    ) -> float:
        """Calculate score based on collaboration history and success."""        try:
            # Check if users have collaborated before
            previous_collaborations = db.query(Collaboration).filter(
                or_(
                    and_(
                        Collaboration.requester_id == user1.id,
                        Collaboration.partner_id == user2.id
                    ),
                    and_(
                        Collaboration.requester_id == user2.id,
                        Collaboration.partner_id == user1.id
                    )
                )
            ).all()
            
            if previous_collaborations:
                # Calculate success rate of previous collaborations
                successful_collaborations = [
                    c for c in previous_collaborations 
                    if c.status == "completed" and c.success_rating >= 4.0
                ]
                
                success_rate = len(successful_collaborations) / len(previous_collaborations)
                return success_rate
            
            # No previous collaborations - calculate based on general success rates
            user1_success_rate = await self._calculate_user_collaboration_success_rate(
                user1.id, db
            )
            user2_success_rate = await self._calculate_user_collaboration_success_rate(
                user2.id, db
            )
            
            # Average success rates
            combined_success_rate = (user1_success_rate + user2_success_rate) / 2
            return combined_success_rate
            
        except Exception as e:
            logger.error(f"Error calculating collaboration history score: {str(e)}")
            return 0.5
    
    async def _calculate_user_collaboration_success_rate(
        self, 
        user_id: uuid.UUID, 
        db: Session
    ) -> float:
        """Calculate user's overall collaboration success rate."""        try:
            user_collaborations = db.query(Collaboration).filter(
                or_(
                    Collaboration.requester_id == user_id,
                    Collaboration.partner_id == user_id
                )
            ).all()
            
            if not user_collaborations:
                return 0.7  # Default neutral score
            
            completed_collaborations = [
                c for c in user_collaborations if c.status == "completed"
            ]
            
            if not completed_collaborations:
                return 0.5  # No completed collaborations
            
            successful_collaborations = [
                c for c in completed_collaborations if c.success_rating >= 4.0
            ]
            
            return len(successful_collaborations) / len(completed_collaborations)
            
        except Exception as e:
            logger.error(f"Error calculating user collaboration success rate: {str(e)}")
            return 0.5
    
    def _calculate_activity_compatibility(self, user1: User, user2: User) -> float:
        """Calculate activity level and profile completeness compatibility."""        try:
            # Profile completeness scores
            user1_completeness = self._calculate_profile_completeness(user1)
            user2_completeness = self._calculate_profile_completeness(user2)
            
            # Activity level scores (based on last activity)
            user1_activity = self._calculate_activity_score(user1)
            user2_activity = self._calculate_activity_score(user2)
            
            # Compatibility is higher when both users have similar levels
            completeness_compatibility = 1.0 - abs(user1_completeness - user2_completeness)
            activity_compatibility = 1.0 - abs(user1_activity - user2_activity) / 2
            
            return (completeness_compatibility + activity_compatibility) / 2
            
        except Exception as e:
            logger.error(f"Error calculating activity compatibility: {str(e)}")
            return 0.5
    
    def _calculate_profile_completeness(self, user: User) -> float:
        """Calculate profile completeness score."""        score = 0.0
        total_fields = 10
        
        if user.full_name: score += 1
        if user.bio: score += 1
        if user.profile_image_url: score += 1
        if user.website_url: score += 1
        if user.social_media_links: score += 1
        if user.supported_content_formats: score += 1
        if user.skills: score += 1
        if user.location: score += 1
        if user.timezone: score += 1
        if user.professional_info: score += 1
        
        return score / total_fields
    
    def _calculate_activity_score(self, user: User) -> float:
        """Calculate user activity score based on recent activity."""        if not user.last_activity_at:
            return 0.0
        
        days_since_activity = (datetime.utcnow() - user.last_activity_at).days
        
        if days_since_activity <= 1:
            return 1.0
        elif days_since_activity <= 7:
            return 0.8
        elif days_since_activity <= 30:
            return 0.6
        elif days_since_activity <= 90:
            return 0.4
        else:
            return 0.2
    
    async def _get_match_reasons(
        self, 
        user1: User, 
        user2: User, 
        compatibility_score: float
    ) -> List[str]:
        """Generate human-readable match reasons."""        reasons = []
        
        # Format compatibility
        format_overlap = self._calculate_format_compatibility(user1, user2)
        if format_overlap > 0.7:
            common_formats = set(user1.supported_content_formats or []).intersection(
                set(user2.supported_content_formats or [])
            )
            reasons.append(f"Both work with {', '.join(common_formats)}")
        
        # Role compatibility
        if user1.role != user2.role:
            reasons.append(f"Complementary roles: {user1.role} & {user2.role}")
        
        # Activity level
        if self._calculate_activity_score(user1) > 0.8 and self._calculate_activity_score(user2) > 0.8:
            reasons.append("Both are highly active creators")
        
        # Verification status
        if user1.is_verified and user2.is_verified:
            reasons.append("Both are verified creators")
        
        # High compatibility
        if compatibility_score > 0.8:
            reasons.append("Exceptional compatibility match")
        elif compatibility_score > 0.6:
            reasons.append("Strong collaboration potential")
        
        return reasons
    
    async def _predict_collaboration_success(
        self, 
        user1: User, 
        user2: User, 
        db: Session
    ) -> float:
        """Predict the success probability of a collaboration."""        try:
            # Feature extraction for ML model
            features = await self._extract_collaboration_features(user1, user2, db)
            
            # Use ML model to predict success (simplified version)
            # In production, this would use a trained ML model
            success_probability = (
                features["compatibility_score"] * 0.3 +
                features["combined_success_rate"] * 0.25 +
                features["audience_overlap"] * 0.2 +
                features["activity_score"] * 0.15 +
                features["profile_completeness"] * 0.1
            )
            
            return min(1.0, max(0.0, success_probability))
            
        except Exception as e:
            logger.error(f"Error predicting collaboration success: {str(e)}")
            return 0.5
    
    async def _extract_collaboration_features(
        self, 
        user1: User, 
        user2: User, 
        db: Session
    ) -> Dict[str, float]:
        """Extract features for collaboration success prediction."""        features = {}
        
        features["compatibility_score"] = await self._calculate_compatibility_score(
            user1, user2, db
        )
        
        features["combined_success_rate"] = (
            await self._calculate_user_collaboration_success_rate(user1.id, db) +
            await self._calculate_user_collaboration_success_rate(user2.id, db)
        ) / 2
        
        features["audience_overlap"] = await self._calculate_audience_overlap(
            user1, user2, db
        )
        
        features["activity_score"] = (
            self._calculate_activity_score(user1) + 
            self._calculate_activity_score(user2)
        ) / 2
        
        features["profile_completeness"] = (
            self._calculate_profile_completeness(user1) + 
            self._calculate_profile_completeness(user2)
        ) / 2
        
        return features
    
    async def _calculate_audience_overlap(
        self, 
        user1: User, 
        user2: User, 
        db: Session
    ) -> float:
        """Calculate audience overlap percentage."""        try:
            # This is a simplified version - in production would use detailed analytics
            user1_followers = user1.follower_count or 0
            user2_followers = user2.follower_count or 0
            
            if user1_followers == 0 or user2_followers == 0:
                return 0.0
            
            # Estimate overlap based on content similarity and user profiles
            content_similarity = await self._calculate_genre_compatibility(user1, user2, db)
            
            # Simplified overlap calculation
            overlap_estimate = content_similarity * 0.3  # Max 30% overlap
            
            return min(0.3, overlap_estimate)
            
        except Exception as e:
            logger.error(f"Error calculating audience overlap: {str(e)}")
            return 0.0
    
    async def _analyze_content_synergy(
        self, 
        user1: User, 
        user2: User, 
        db: Session
    ) -> Dict[str, Any]:
        """Analyze content synergy potential."""        try:
            synergy_analysis = {
                "format_synergy": self._calculate_format_compatibility(user1, user2),
                "genre_synergy": await self._calculate_genre_compatibility(user1, user2, db),
                "complementary_skills": await self._analyze_complementary_skills(user1, user2),
                "cross_promotion_potential": await self._calculate_cross_promotion_potential(
                    user1, user2, db
                ),
                "remix_opportunities": await self._identify_remix_opportunities(user1, user2, db)
            }
            
            # Overall synergy score
            synergy_analysis["overall_synergy"] = sum(synergy_analysis.values()) / len(synergy_analysis)
            
            return synergy_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content synergy: {str(e)}")
            return {"overall_synergy": 0.5}
    
    async def _analyze_complementary_skills(self, user1: User, user2: User) -> float:
        """Analyze how well users' skills complement each other."""        if not user1.skills or not user2.skills:
            return 0.5
        
        skills1 = set(user1.skills)
        skills2 = set(user2.skills)
        
        # Complementary skills are better than overlapping skills for some collaborations
        unique_skills = skills1.symmetric_difference(skills2)
        total_skills = skills1.union(skills2)
        
        if not total_skills:
            return 0.5
        
        complementary_ratio = len(unique_skills) / len(total_skills)
        
        # Optimal complementary ratio is around 0.6-0.8
        if 0.6 <= complementary_ratio <= 0.8:
            return 1.0
        elif 0.4 <= complementary_ratio < 0.6:
            return 0.8
        elif 0.8 < complementary_ratio <= 1.0:
            return 0.7
        else:
            return 0.5
    
    async def _calculate_cross_promotion_potential(
        self, 
        user1: User, 
        user2: User, 
        db: Session
    ) -> float:
        """Calculate cross-promotion potential."""        try:
            # Factors: audience size difference, audience overlap, content complementarity
            follower1 = user1.follower_count or 0
            follower2 = user2.follower_count or 0
            
            # Benefit is higher when there's some size difference but not too extreme
            if follower1 == 0 or follower2 == 0:
                return 0.3
            
            ratio = min(follower1, follower2) / max(follower1, follower2)
            
            # Optimal ratio for cross-promotion is 0.3-0.8
            if 0.3 <= ratio <= 0.8:
                size_benefit = 1.0
            elif 0.1 <= ratio < 0.3:
                size_benefit = 0.7
            elif 0.8 < ratio <= 1.0:
                size_benefit = 0.8
            else:
                size_benefit = 0.4
            
            # Content complementarity
            content_complement = 1.0 - await self._calculate_genre_compatibility(user1, user2, db)
            
            return (size_benefit + content_complement) / 2
            
        except Exception as e:
            logger.error(f"Error calculating cross-promotion potential: {str(e)}")
            return 0.5
    
    async def _identify_remix_opportunities(
        self, 
        user1: User, 
        user2: User, 
        db: Session
    ) -> float:
        """Identify remix and mashup opportunities."""        try:
            # Get recent audio/video content from both users
            user1_content = db.query(Content).filter(
                and_(
                    Content.owner_id == user1.id,
                    Content.file_type.in_(["audio", "video"])
                )
            ).order_by(desc(Content.created_at)).limit(5).all()
            
            user2_content = db.query(Content).filter(
                and_(
                    Content.owner_id == user2.id,
                    Content.file_type.in_(["audio", "video"])
                )
            ).order_by(desc(Content.created_at)).limit(5).all()
            
            if not user1_content or not user2_content:
                return 0.3
            
            # Analyze remix potential based on content characteristics
            remix_scores = []
            
            for content1 in user1_content:
                for content2 in user2_content:
                    score = await self._calculate_remix_potential(content1, content2, db)
                    remix_scores.append(score)
            
            if remix_scores:
                return sum(remix_scores) / len(remix_scores)
            
            return 0.3
            
        except Exception as e:
            logger.error(f"Error identifying remix opportunities: {str(e)}")
            return 0.3
    
    async def _get_candidate_contents(
        self,
        source_content: Content,
        match_type: str,
        db: Session
    ) -> List[Content]:
        """Get candidate contents for matching."""        query = db.query(Content).filter(
            and_(
                Content.id != source_content.id,
                Content.is_active == True,
                Content.privacy_level.in_(["public", "collaboration"])
            )
        )
        
        # Filter by content type for certain match types
        if match_type == "remix" and source_content.file_type == "audio":
            query = query.filter(Content.file_type.in_(["audio", "video"]))
        elif match_type == "similar":
            query = query.filter(Content.file_type == source_content.file_type)
        
        # Filter by category similarity for better matching
        if source_content.category:
            query = query.filter(Content.category == source_content.category)
        
        return query.limit(100).all()
    
    async def _calculate_content_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """Calculate similarity between content embeddings."""        try:
            if embedding1 is None or embedding2 is None:
                return 0.0
            
            # Cosine similarity
            similarity = cosine_similarity(
                embedding1.reshape(1, -1), 
                embedding2.reshape(1, -1)
            )[0][0]
            
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Error calculating content similarity: {str(e)}")
            return 0.0
    
    async def _calculate_content_complementarity(
        self,
        content1: Content,
        content2: Content,
        db: Session
    ) -> float:
        """Calculate how well contents complement each other."""        try:
            # Complementarity factors
            format_complement = 0.0
            if content1.file_type != content2.file_type:
                format_complement = 0.8  # Different formats complement well
            
            # Category relationship
            category_complement = 0.5
            if content1.category and content2.category:
                if content1.category != content2.category:
                    category_complement = 0.7  # Different categories can complement
                else:
                    category_complement = 0.3  # Same category less complementary
            
            # Duration/length compatibility (for time-based content)
            duration_complement = 0.5
            if hasattr(content1.metadata, 'duration') and hasattr(content2.metadata, 'duration'):
                duration1 = content1.metadata.duration
                duration2 = content2.metadata.duration
                
                if duration1 and duration2:
                    ratio = min(duration1, duration2) / max(duration1, duration2)
                    duration_complement = ratio  # Similar durations work better together
            
            # Overall complementarity score
            complement_score = (
                format_complement * 0.4 +
                category_complement * 0.3 +
                duration_complement * 0.3
            )
            
            return complement_score
            
        except Exception as e:
            logger.error(f"Error calculating content complementarity: {str(e)}")
            return 0.5
    
    async def _calculate_remix_potential(
        self,
        content1: Content,
        content2: Content,
        db: Session
    ) -> float:
        """Calculate remix potential between two pieces of content."""        try:
            # Only audio and video content can be remixed effectively
            if content1.file_type not in ["audio", "video"] or content2.file_type not in ["audio", "video"]:
                return 0.0
            
            # Audio metadata analysis
            remix_score = 0.5  # Base score
            
            if content1.metadata and content2.metadata:
                # Tempo compatibility (for audio)
                if hasattr(content1.metadata, 'tempo') and hasattr(content2.metadata, 'tempo'):
                    tempo1 = content1.metadata.tempo
                    tempo2 = content2.metadata.tempo
                    
                    if tempo1 and tempo2:
                        tempo_ratio = min(tempo1, tempo2) / max(tempo1, tempo2)
                        remix_score += (tempo_ratio * 0.3)
                
                # Key compatibility (for audio)
                if hasattr(content1.metadata, 'key') and hasattr(content2.metadata, 'key'):
                    key1 = content1.metadata.key
                    key2 = content2.metadata.key
                    
                    if key1 and key2:
                        # Simplified key compatibility check
                        if self._are_keys_compatible(key1, key2):
                            remix_score += 0.2
                
                # Duration similarity
                if hasattr(content1.metadata, 'duration') and hasattr(content2.metadata, 'duration'):
                    duration1 = content1.metadata.duration
                    duration2 = content2.metadata.duration
                    
                    if duration1 and duration2:
                        duration_ratio = min(duration1, duration2) / max(duration1, duration2)
                        remix_score += (duration_ratio * 0.2)
            
            return min(1.0, remix_score)
            
        except Exception as e:
            logger.error(f"Error calculating remix potential: {str(e)}")
            return 0.0
    
    def _are_keys_compatible(self, key1: str, key2: str) -> bool:
        """Check if musical keys are compatible for remixing."""        # Simplified key compatibility - in production would use music theory
        compatible_keys = {
            "C": ["C", "Am", "F", "G"],
            "G": ["G", "Em", "C", "D"],
            "D": ["D", "Bm", "G", "A"],
            "A": ["A", "F#m", "D", "E"],
            "E": ["E", "C#m", "A", "B"],
            "B": ["B", "G#m", "E", "F#"],
            "F#": ["F#", "D#m", "B", "C#"],
            "F": ["F", "Dm", "Bb", "C"],
            "Bb": ["Bb", "Gm", "Eb", "F"],
            "Eb": ["Eb", "Cm", "Ab", "Bb"],
            "Ab": ["Ab", "Fm", "Db", "Eb"],
            "Db": ["Db", "Bbm", "Gb", "Ab"]
        }
        
        return key2 in compatible_keys.get(key1, [])
    
    async def _validate_collaboration_eligibility(
        self,
        requester_id: uuid.UUID,
        partner_id: uuid.UUID,
        db: Session
    ):
        """Validate that both users are eligible for collaboration."""        # Check if users exist and are active
        requester = db.query(User).filter(User.id == requester_id).first()
        partner = db.query(User).filter(User.id == partner_id).first()
        
        if not requester or not partner:
            raise ValueError("One or both users not found")
        
        if not requester.is_active or not partner.is_active:
            raise ValueError("One or both users are inactive")
        
        if not partner.enable_collaboration:
            raise ValueError("Partner has disabled collaborations")
        
        # Check for existing pending requests
        existing_request = db.query(Collaboration).filter(
            and_(
                Collaboration.requester_id == requester_id,
                Collaboration.partner_id == partner_id,
                Collaboration.status == "pending",
                Collaboration.expires_at > datetime.utcnow()
            )
        ).first()
        
        if existing_request:
            raise ValueError("Collaboration request already exists")
    
    async def _get_trending_creators(self, user: User, db: Session) -> List[Dict[str, Any]]:
        """Get trending creators in user's categories."""        try:
            # Get users with similar content formats and high recent activity
            trending_query = db.query(User).filter(
                and_(
                    User.id != user.id,
                    User.is_active == True,
                    User.enable_collaboration == True,
                    func.array_overlap(
                        User.supported_content_formats, 
                        user.supported_content_formats or []
                    )
                )
            ).order_by(
                desc(User.follower_count),
                desc(User.last_activity_at)
            ).limit(20)
            
            trending_users = trending_query.all()
            
            trending_data = []
            for trending_user in trending_users:
                # Calculate trending score based on recent activity and growth
                trending_score = await self._calculate_trending_score(trending_user, db)
                
                if trending_score >= 0.6:
                    trending_data.append({
                        "user_id": trending_user.id,
                        "username": trending_user.username,
                        "full_name": trending_user.full_name,
                        "role": trending_user.role,
                        "follower_count": trending_user.follower_count,
                        "trending_score": trending_score,
                        "profile_image": trending_user.profile_image_url,
                        "verified": trending_user.is_verified,
                        "supported_formats": trending_user.supported_content_formats
                    })
            
            # Sort by trending score
            trending_data.sort(key=lambda x: x["trending_score"], reverse=True)
            
            return trending_data[:10]
            
        except Exception as e:
            logger.error(f"Error getting trending creators: {str(e)}")
            return []
    
    async def _calculate_trending_score(self, user: User, db: Session) -> float:
        """Calculate trending score for a user."""        try:
            score = 0.0
            
            # Recent activity score (40%)
            activity_score = self._calculate_activity_score(user)
            score += activity_score * 0.4
            
            # Content upload frequency (30%)
            recent_content_count = db.query(func.count(Content.id)).filter(
                and_(
                    Content.owner_id == user.id,
                    Content.created_at >= datetime.utcnow() - timedelta(days=30)
                )
            ).scalar()
            
            content_frequency_score = min(1.0, recent_content_count / 10.0)
            score += content_frequency_score * 0.3
            
            # Engagement growth (20%)
            engagement_score = min(1.0, (user.follower_count or 0) / 10000.0)
            score += engagement_score * 0.2
            
            # Profile quality (10%)
            profile_score = self._calculate_profile_completeness(user)
            score += profile_score * 0.1
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating trending score: {str(e)}")
            return 0.0
    
    async def _generate_match_insights(self, user: User, db: Session) -> Dict[str, Any]:
        """Generate personalized matching insights for user."""        try:
            insights = {
                "profile_optimization": [],
                "collaboration_tips": [],
                "trending_opportunities": [],
                "skill_recommendations": []
            }
            
            # Profile optimization suggestions
            profile_completeness = self._calculate_profile_completeness(user)
            if profile_completeness < 0.8:
                missing_fields = []
                if not user.bio:
                    missing_fields.append("bio")
                if not user.profile_image_url:
                    missing_fields.append("profile image")
                if not user.skills:
                    missing_fields.append("skills")
                
                insights["profile_optimization"] = [
                    f"Complete your {', '.join(missing_fields)} to increase match quality"
                ]
            
            # Collaboration tips based on user's collaboration history
            user_success_rate = await self._calculate_user_collaboration_success_rate(user.id, db)
            if user_success_rate < 0.6:
                insights["collaboration_tips"] = [
                    "Consider smaller projects to build collaboration reputation",
                    "Be clear about expectations and timelines",
                    "Respond promptly to collaboration requests"
                ]
            
            # Trending opportunities
            user_formats = set(user.supported_content_formats or [])
            trending_formats = {"video", "audio", "mixed_media"}  # Would come from analytics
            
            missing_trending = trending_formats - user_formats
            if missing_trending:
                insights["trending_opportunities"] = [
                    f"Consider expanding to {', '.join(missing_trending)} content for more opportunities"
                ]
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating match insights: {str(e)}")
            return {}
