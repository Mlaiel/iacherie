"""Social Proof Workflow

AI-powered social proof and community validation workflow for gamification.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from ..core.exceptions import WorkflowError
from ..utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class ProofType(Enum):
    """Types of social proof"""
    TESTIMONIAL = "testimonial"
    ACHIEVEMENT_SHOWCASE = "achievement_showcase"
    USER_MILESTONE = "user_milestone"
    COMMUNITY_HIGHLIGHT = "community_highlight"
    SUCCESS_STORY = "success_story"
    PEER_RECOGNITION = "peer_recognition"


@dataclass
class SocialProof:
    """Social proof item"""
    proof_id: str
    user_id: str
    proof_type: ProofType
    title: str
    content: str
    achievement_data: Dict[str, Any]
    engagement_score: float = 0.0
    visibility: str = "public"  # public, community, private
    created_at: datetime = field(default_factory=datetime.utcnow)
    verified: bool = False


@dataclass
class ProofEngagement:
    """Engagement metrics for social proof"""
    proof_id: str
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    inspiration_clicks: int = 0  # "This inspired me" clicks
    last_updated: datetime = field(default_factory=datetime.utcnow)


class SocialProofWorkflow:
    """AI-powered social proof workflow"""
    
    def __init__(self) -> None:
        self.metrics_collector = MetricsCollector()
        self.social_proofs: Dict[str, SocialProof] = {}
        self.proof_engagement: Dict[str, ProofEngagement] = {}
        
    async def create_social_proof(
        self,
        user_id: str,
        proof_type: ProofType,
        title: str,
        content: str,
        achievement_data: Dict[str, Any],
        auto_verify: bool = False
    ) -> SocialProof:
        """
        Create a social proof item
        
        Args:
            user_id: User identifier
            proof_type: Type of social proof
            title: Proof title
            content: Proof content/description
            achievement_data: Related achievement data
            auto_verify: Whether to auto-verify the proof
            
        Returns:
            SocialProof object
        """
        try:
            proof_id = f"proof_{int(datetime.utcnow().timestamp())}_{user_id}"
            
            # Calculate engagement score based on achievement significance
            engagement_score = await self._calculate_engagement_potential(achievement_data, proof_type)
            
            social_proof = SocialProof(
                proof_id=proof_id,
                user_id=user_id,
                proof_type=proof_type,
                title=title,
                content=content,
                achievement_data=achievement_data,
                engagement_score=engagement_score,
                verified=auto_verify
            )
            
            # Store social proof
            self.social_proofs[proof_id] = social_proof
            
            # Initialize engagement tracking
            self.proof_engagement[proof_id] = ProofEngagement(proof_id=proof_id)
            
            # Record metrics
            await self.metrics_collector.record_metric("social_proofs_created", 1)
            await self.metrics_collector.record_metric(f"social_proof_{proof_type.value}", 1)
            
            logger.info(f"Created social proof {proof_id} for user {user_id}")
            return social_proof
            
        except Exception as e:
            logger.error(f"Social proof creation failed: {e}")
            raise WorkflowError(f"Social proof creation failed: {e}")
    
    async def generate_achievement_showcase(
        self,
        user_id: str,
        achievement: Dict[str, Any],
        user_stats: Dict[str, Any]
    ) -> SocialProof:
        """Generate social proof for achievement automatically"""
        
        # Create compelling title and content
        achievement_name = achievement.get("name", "Achievement")
        achievement_description = achievement.get("description", "")
        
        title = f"🎉 Just earned: {achievement_name}!"
        content = await self._generate_achievement_content(achievement, user_stats)
        
        return await self.create_social_proof(
            user_id=user_id,
            proof_type=ProofType.ACHIEVEMENT_SHOWCASE,
            title=title,
            content=content,
            achievement_data=achievement,
            auto_verify=True
        )
    
    async def generate_milestone_announcement(
        self,
        user_id: str,
        milestone: str,
        milestone_data: Dict[str, Any],
        user_stats: Dict[str, Any]
    ) -> SocialProof:
        """Generate social proof for milestone achievement"""
        
        title, content = await self._generate_milestone_content(milestone, milestone_data, user_stats)
        
        return await self.create_social_proof(
            user_id=user_id,
            proof_type=ProofType.USER_MILESTONE,
            title=title,
            content=content,
            achievement_data=milestone_data,
            auto_verify=True
        )
    
    async def track_proof_engagement(
        self,
        proof_id: str,
        engagement_type: str,
        value: int = 1
    ) -> ProofEngagement:
        """
        Track engagement on social proof
        
        Args:
            proof_id: Social proof identifier
            engagement_type: Type of engagement (view, like, share, comment, inspiration)
            value: Value to add (default 1)
            
        Returns:
            Updated ProofEngagement object
        """
        try:
            if proof_id not in self.proof_engagement:
                self.proof_engagement[proof_id] = ProofEngagement(proof_id=proof_id)
            
            engagement = self.proof_engagement[proof_id]
            
            # Update engagement metrics
            if engagement_type == "view":
                engagement.views += value
            elif engagement_type == "like":
                engagement.likes += value
            elif engagement_type == "share":
                engagement.shares += value
            elif engagement_type == "comment":
                engagement.comments += value
            elif engagement_type == "inspiration":
                engagement.inspiration_clicks += value
            
            engagement.last_updated = datetime.utcnow()
            
            # Update social proof engagement score
            if proof_id in self.social_proofs:
                self.social_proofs[proof_id].engagement_score = await self._calculate_current_engagement_score(engagement)
            
            return engagement
            
        except Exception as e:
            logger.error(f"Engagement tracking failed: {e}")
            raise WorkflowError(f"Engagement tracking failed: {e}")
    
    async def get_trending_proofs(self, limit: int = 10, time_window_hours: int = 24) -> List[SocialProof]:
        """Get trending social proofs based on recent engagement"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        # Calculate trending scores for recent proofs
        trending_proofs = []
        
        for proof in self.social_proofs.values():
            if proof.created_at >= cutoff_time and proof.verified:
                engagement = self.proof_engagement.get(proof.proof_id)
                if engagement:
                    trending_score = await self._calculate_trending_score(proof, engagement)
                    trending_proofs.append((proof, trending_score))
        
        # Sort by trending score
        trending_proofs.sort(key=lambda x: x[1], reverse=True)
        
        return [proof for proof, score in trending_proofs[:limit]]
    
    async def get_user_social_proofs(self, user_id: str, include_private: bool = False) -> List[SocialProof]:
        """Get all social proofs for a user"""
        
        user_proofs = []
        for proof in self.social_proofs.values():
            if proof.user_id == user_id:
                if include_private or proof.visibility == "public":
                    user_proofs.append(proof)
        
        # Sort by creation date (newest first)
        user_proofs.sort(key=lambda x: x.created_at, reverse=True)
        
        return user_proofs
    
    async def get_community_highlights(self, limit: int = 20) -> List[SocialProof]:
        """Get community highlights for featuring"""
        
        # Get high-engagement proofs from the last week
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        
        eligible_proofs = []
        for proof in self.social_proofs.values():
            if (proof.created_at >= one_week_ago and 
                proof.verified and 
                proof.visibility == "public" and
                proof.engagement_score > 0.7):
                eligible_proofs.append(proof)
        
        # Sort by engagement score
        eligible_proofs.sort(key=lambda x: x.engagement_score, reverse=True)
        
        return eligible_proofs[:limit]
    
    async def verify_social_proof(self, proof_id: str, verified: bool = True) -> bool:
        """Verify or unverify a social proof"""
        
        if proof_id not in self.social_proofs:
            return False
        
        self.social_proofs[proof_id].verified = verified
        
        if verified:
            logger.info(f"Social proof {proof_id} verified")
        else:
            logger.info(f"Social proof {proof_id} unverified")
        
        return True
    
    async def generate_peer_recognition(
        self,
        recognizer_user_id: str,
        recognized_user_id: str,
        recognition_type: str,
        message: str
    ) -> SocialProof:
        """Generate peer recognition social proof"""
        
        title = f"👏 Peer Recognition: {recognition_type}"
        content = f"Recognized by a fellow creator: {message}"
        
        achievement_data = {
            "recognition_type": recognition_type,
            "recognizer_id": recognizer_user_id,
            "message": message
        }
        
        return await self.create_social_proof(
            user_id=recognized_user_id,
            proof_type=ProofType.PEER_RECOGNITION,
            title=title,
            content=content,
            achievement_data=achievement_data,
            auto_verify=True
        )
    
    async def _calculate_engagement_potential(self, achievement_data: Dict[str, Any], proof_type: ProofType) -> float:
        """Calculate potential engagement score for social proof"""
        
        base_score = 0.5
        
        # Achievement significance
        achievement_rarity = achievement_data.get("rarity", "common")
        rarity_bonus = {
            "common": 0.1,
            "rare": 0.2, 
            "epic": 0.3,
            "legendary": 0.4
        }.get(achievement_rarity, 0.1)
        
        # Proof type impact
        type_multiplier = {
            ProofType.ACHIEVEMENT_SHOWCASE: 1.0,
            ProofType.USER_MILESTONE: 1.2,
            ProofType.SUCCESS_STORY: 1.3,
            ProofType.PEER_RECOGNITION: 1.1,
            ProofType.COMMUNITY_HIGHLIGHT: 1.4
        }.get(proof_type, 1.0)
        
        return min((base_score + rarity_bonus) * type_multiplier, 1.0)
    
    async def _calculate_current_engagement_score(self, engagement: ProofEngagement) -> float:
        """Calculate current engagement score based on actual metrics"""
        
        # Weighted engagement score
        score = (
            engagement.views * 0.1 +
            engagement.likes * 0.3 +
            engagement.shares * 0.4 +
            engagement.comments * 0.5 +
            engagement.inspiration_clicks * 0.6
        ) / 100  # Normalize
        
        return min(score, 1.0)
    
    async def _calculate_trending_score(self, proof: SocialProof, engagement: ProofEngagement) -> float:
        """Calculate trending score for ranking"""
        
        # Time decay factor (recent content gets higher score)
        hours_since_creation = (datetime.utcnow() - proof.created_at).total_seconds() / 3600
        time_decay = max(0.1, 1.0 - (hours_since_creation / 24))  # Linear decay over 24 hours
        
        # Engagement velocity
        engagement_rate = (engagement.likes + engagement.shares + engagement.comments) / max(engagement.views, 1)
        
        # Combined trending score
        trending_score = proof.engagement_score * time_decay * (1 + engagement_rate)
        
        return trending_score
    
    async def _generate_achievement_content(self, achievement: Dict[str, Any], user_stats: Dict[str, Any]) -> str:
        """Generate engaging content for achievement showcase"""
        
        achievement_name = achievement.get("name", "Achievement")
        achievement_desc = achievement.get("description", "")
        
        # Add personal context
        content_parts = [
            f"I'm excited to share that I just earned the '{achievement_name}' achievement!",
            achievement_desc
        ]
        
        # Add relevant stats if available
        if "followers_count" in user_stats:
            content_parts.append(f"Current followers: {user_stats['followers_count']:,}")
        
        if "posts_count" in user_stats:
            content_parts.append(f"Posts created: {user_stats['posts_count']:,}")
        
        content_parts.append("Thanks to everyone who's been part of this journey! 🙏")
        
        return " ".join(content_parts)
    
    async def _generate_milestone_content(
        self, 
        milestone: str, 
        milestone_data: Dict[str, Any], 
        user_stats: Dict[str, Any]
    ) -> tuple:
        """Generate title and content for milestone announcement"""
        
        milestone_templates = {
            "first_1000_followers": {
                "title": "🎉 Just hit 1,000 followers!",
                "content": "What an incredible milestone! Thank you to all 1,000 of you for following my journey. This is just the beginning!"
            },
            "100_posts_created": {
                "title": "📝 100 posts milestone reached!",
                "content": "I've just published my 100th post! It's been an amazing creative journey, and I'm excited for the next 100!"
            },
            "viral_content": {
                "title": "🚀 Content went viral!",
                "content": "Wow! My recent post just went viral with over 10,000 views! So grateful for the amazing response from the community!"
            }
        }
        
        template = milestone_templates.get(milestone, {
            "title": f"🎯 {milestone.replace('_', ' ').title()} milestone achieved!",
            "content": f"Just reached an important milestone: {milestone.replace('_', ' ')}. Feeling grateful for this journey!"
        })
        
        return template["title"], template["content"]