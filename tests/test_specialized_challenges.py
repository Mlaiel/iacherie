"""Test specialized challenges and competitions functionality

Tests for:
- Monthly Creative Challenges with rewards
- Technical Challenges (SEO and revenue optimization) 
- Global Competitions for special events
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from core.challenges.specialized_challenges import (
    SpecializedChallengeManager,
    MonthlyCreativeChallenge,
    TechnicalChallenge, 
    GlobalCompetition,
    SpecializedChallengeType,
    ChallengeRewardType,
    SpecializedReward,
    create_default_specialized_challenges
)


class TestSpecializedChallenges:
    """
Test specialized challenge functionality"""
    
    @pytest.fixture
    async def challenge_manager(self):
        """
Create a challenge manager for testing"""
        manager = SpecializedChallengeManager()
        return manager
    
    @pytest.mark.asyncio
    async def test_monthly_creative_challenge_creation(self, challenge_manager):
        """
Test creating monthly creative challenges"""
        challenge = await challenge_manager.create_monthly_creative_challenge(
            title="Test Monthly Creative Challenge",
            theme="Innovation Test",
            description="Test description for monthly challenge"
        )
        
        assert challenge.title == "Test Monthly Creative Challenge"
        assert challenge.theme == "Innovation Test"
        assert challenge.challenge_id in challenge_manager.monthly_challenges
        
        # Test default rewards are set
        assert challenge.grand_prize.reward_type == ChallengeRewardType.CASH_PRIZE
        assert challenge.grand_prize.value == Decimal('500')
        assert len(challenge.runner_up_prizes) == 2
        assert len(challenge.participation_rewards) == 2
        
        # Test timing defaults
        assert challenge.end_date > challenge.start_date
        assert (challenge.end_date - challenge.start_date).days == 30
    
    @pytest.mark.asyncio
    async def test_seo_challenge_creation(self, challenge_manager):
        """Test creating SEO optimization challenges"""
        challenge = await challenge_manager.create_seo_challenge(
            title="Test SEO Challenge",
            description="Test SEO optimization challenge",
            target_improvement=25.0
        )
        
        assert challenge.title == "Test SEO Challenge"
        assert challenge.technical_focus == "seo"
        assert challenge.seo_targets["ranking_improvement"] == 25.0
        assert challenge.seo_targets["organic_traffic_increase"] == 37.5  # 25 * 1.5
        
        # Test rewards
        assert len(challenge.achievement_rewards) == 3
        reward_types = [r.reward_type for r in challenge.achievement_rewards]
        assert ChallengeRewardType.POINTS in reward_types
        assert ChallengeRewardType.BADGE in reward_types
        assert ChallengeRewardType.FEATURE_UNLOCK in reward_types
    
    @pytest.mark.asyncio
    async def test_revenue_challenge_creation(self, challenge_manager):
        """Test creating revenue optimization challenges"""
        challenge = await challenge_manager.create_revenue_challenge(
            title="Test Revenue Challenge",
            description="Test revenue optimization challenge",
            target_increase=60.0
        )
        
        assert challenge.title == "Test Revenue Challenge"
        assert challenge.technical_focus == "revenue_optimization"
        assert challenge.revenue_targets["revenue_increase_percentage"] == 60.0
        assert challenge.revenue_targets["new_revenue_streams"] == 2
        
        # Test rewards include cash prize
        cash_rewards = [r for r in challenge.achievement_rewards 
                       if r.reward_type == ChallengeRewardType.CASH_PRIZE]
        assert len(cash_rewards) > 0
        assert cash_rewards[0].value == Decimal('300')
    
    @pytest.mark.asyncio
    async def test_global_competition_creation(self, challenge_manager):
        """Test creating global competitions"""
        competition = await challenge_manager.create_global_competition(
            title="Test Global Competition",
            event_type="seasonal",
            description="Test global competition",
            prize_pool=15000
        )
        
        assert competition.title == "Test Global Competition"
        assert competition.event_type == "seasonal"
        assert competition.total_prize_pool == Decimal('15000')
        
        # Test global features
        assert len(competition.participating_regions) == 7
        assert len(competition.language_support) == 10
        assert "North America" in competition.participating_regions
        assert "en" in competition.language_support
        
        # Test prize distribution
        assert "first_place" in competition.prize_distribution
        first_prize = competition.prize_distribution["first_place"]
        assert first_prize.value == Decimal('15000') * Decimal('0.3')  # 30% of pool
    
    @pytest.mark.asyncio
    async def test_active_challenges_retrieval(self, challenge_manager):
        """Test retrieving active challenges"""
        # Create challenges with different timing
        now = datetime.now(timezone.utc)
        
        # Active monthly challenge
        await challenge_manager.create_monthly_creative_challenge(
            title="Active Monthly Challenge",
            theme="Test Theme",
            start_date=now - timedelta(days=5),
            end_date=now + timedelta(days=25)
        )
        
        # Expired challenge
        await challenge_manager.create_monthly_creative_challenge(
            title="Expired Monthly Challenge", 
            theme="Past Theme",
            start_date=now - timedelta(days=35),
            end_date=now - timedelta(days=5)
        )
        
        # Future challenge
        await challenge_manager.create_monthly_creative_challenge(
            title="Future Monthly Challenge",
            theme="Future Theme", 
            start_date=now + timedelta(days=5),
            end_date=now + timedelta(days=35)
        )
        
        active_challenges = await challenge_manager.get_active_monthly_challenges()
        assert len(active_challenges) == 1
        assert active_challenges[0].title == "Active Monthly Challenge"
    
    @pytest.mark.asyncio
    async def test_challenge_analytics(self, challenge_manager):
        """Test challenge analytics functionality"""
        # Create some test challenges
        await challenge_manager.create_monthly_creative_challenge(
            title="Analytics Test Monthly",
            theme="Test"
        )
        
        await challenge_manager.create_seo_challenge(
            title="Analytics Test SEO",
            target_improvement=20.0
        )
        
        await challenge_manager.create_revenue_challenge(
            title="Analytics Test Revenue",
            target_increase=30.0
        )
        
        await challenge_manager.create_global_competition(
            title="Analytics Test Global",
            event_type="milestone",
            prize_pool=5000
        )
        
        analytics = await challenge_manager.get_challenge_analytics()
        
        assert analytics["monthly_challenges"]["total"] == 1
        assert analytics["technical_challenges"]["total"] == 2
        assert analytics["technical_challenges"]["seo_challenges"] == 1
        assert analytics["technical_challenges"]["revenue_challenges"] == 1
        assert analytics["global_competitions"]["total"] == 1
        assert analytics["global_competitions"]["total_prize_pool"] == Decimal('5000')
    
    @pytest.mark.asyncio
    async def test_specialized_reward_creation(self):
        """Test specialized reward creation and configuration"""
        # Test cash prize reward
        cash_reward = SpecializedReward(
            reward_type=ChallengeRewardType.CASH_PRIZE,
            value=Decimal('250'),
            currency="USD",
            description="Monthly challenge winner prize"
        )
        
        assert cash_reward.reward_type == ChallengeRewardType.CASH_PRIZE
        assert cash_reward.value == Decimal('250')
        assert cash_reward.currency == "USD"
        
        # Test feature unlock reward
        feature_reward = SpecializedReward(
            reward_type=ChallengeRewardType.FEATURE_UNLOCK,
            value="premium_analytics",
            description="Unlock premium analytics tools"
        )
        
        assert feature_reward.reward_type == ChallengeRewardType.FEATURE_UNLOCK
        assert feature_reward.value == "premium_analytics"
        
        # Test badge reward
        badge_reward = SpecializedReward(
            reward_type=ChallengeRewardType.BADGE,
            value="seo_master_2025",
            description="SEO Master Badge 2025"
        )
        
        assert badge_reward.reward_type == ChallengeRewardType.BADGE
        assert badge_reward.value == "seo_master_2025"


class TestDefaultChallengeCreation:
    """Test default challenge creation functionality"""
    
    @pytest.mark.asyncio
    async def test_create_default_specialized_challenges(self):
        """
Test creating default specialized challenges"""
        manager = await create_default_specialized_challenges()
        
        # Verify monthly challenges
        monthly_challenges = list(manager.monthly_challenges.values())
        assert len(monthly_challenges) >= 1
        
        # Find the January 2025 challenge
        january_challenge = None
        for challenge in monthly_challenges:
            if "January 2025" in challenge.title:
                january_challenge = challenge
                break
        
        assert january_challenge is not None
        assert january_challenge.theme == "New Year Innovation"
        assert "AI tools" in january_challenge.creative_constraints[0]
        
        # Verify technical challenges
        technical_challenges = list(manager.technical_challenges.values())
        assert len(technical_challenges) >= 2
        
        # Check for SEO and Revenue challenges
        seo_challenges = [c for c in technical_challenges if c.technical_focus == "seo"]
        revenue_challenges = [c for c in technical_challenges if c.technical_focus == "revenue_optimization"]
        
        assert len(seo_challenges) >= 1
        assert len(revenue_challenges) >= 1
        
        # Verify global competitions
        global_competitions = list(manager.global_competitions.values())
        assert len(global_competitions) >= 1
        
        winter_competition = global_competitions[0]
        assert "Global Winter" in winter_competition.title
        assert winter_competition.total_prize_pool == Decimal('25000')


class TestChallengeIntegration:
    """Test integration between different challenge types"""
    
    @pytest.mark.asyncio
    async def test_challenge_type_integration(self):
        """
Test that different challenge types work together"""
        manager = SpecializedChallengeManager()
        
        # Create one of each type
        monthly = await manager.create_monthly_creative_challenge(
            title="Integration Test Monthly",
            theme="Integration"
        )
        
        seo = await manager.create_seo_challenge(
            title="Integration Test SEO", 
            target_improvement=15.0
        )
        
        revenue = await manager.create_revenue_challenge(
            title="Integration Test Revenue",
            target_increase=25.0
        )
        
        global_comp = await manager.create_global_competition(
            title="Integration Test Global",
            event_type="integration",
            prize_pool=1000
        )
        
        # Verify all are stored correctly
        assert len(manager.monthly_challenges) == 1
        assert len(manager.technical_challenges) == 2
        assert len(manager.global_competitions) == 1
        
        # Verify they have unique IDs
        all_ids = [
            monthly.challenge_id,
            seo.challenge_id, 
            revenue.challenge_id,
            global_comp.competition_id
        ]
        
        assert len(set(all_ids)) == 4  # All unique
    
    @pytest.mark.asyncio
    async def test_reward_system_integration(self):
        """Test reward system works across challenge types"""
        manager = SpecializedChallengeManager()
        
        # Create challenges with different reward structures
        monthly = await manager.create_monthly_creative_challenge(
            title="Reward Test Monthly",
            theme="Rewards"
        )
        
        seo = await manager.create_seo_challenge(
            title="Reward Test SEO",
            target_improvement=20.0
        )
        
        # Check rewards are properly configured
        assert monthly.grand_prize.value > Decimal('0')
        assert len(monthly.runner_up_prizes) > 0
        assert len(seo.achievement_rewards) > 0
        
        # Verify different reward types
        monthly_reward_types = [monthly.grand_prize.reward_type] + [r.reward_type for r in monthly.runner_up_prizes]
        seo_reward_types = [r.reward_type for r in seo.achievement_rewards]
        
        assert ChallengeRewardType.CASH_PRIZE in monthly_reward_types
        assert ChallengeRewardType.POINTS in seo_reward_types


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])