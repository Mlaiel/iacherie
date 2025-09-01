"""Standalone test for specialized challenges functionality

This test validates the specialized challenges implementation without 
requiring full module dependencies.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal

# Add current directory to path to test the specific module
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, '..'))

# Direct import of the specialized challenges module
from core.challenges.specialized_challenges import (
    SpecializedChallengeManager,
    MonthlyCreativeChallenge,
    TechnicalChallenge,
    GlobalCompetition,
    ChallengeRewardType,
    SpecializedReward
)


async def test_monthly_creative_challenge():
    """
Test monthly creative challenge creation"""
    print("Testing Monthly Creative Challenge...")
    
    manager = SpecializedChallengeManager()
    
    challenge = await manager.create_monthly_creative_challenge(
        title="January 2025 Creative Innovation",
        theme="AI-Powered Creativity", 
        description="Create innovative content using AI tools and techniques"
    )
    
    # Validate basic properties
    assert challenge.title == "January 2025 Creative Innovation"
    assert challenge.theme == "AI-Powered Creativity"
    assert challenge.challenge_id in manager.monthly_challenges
    
    # Validate rewards
    assert challenge.grand_prize.reward_type == ChallengeRewardType.CASH_PRIZE
    assert challenge.grand_prize.value == Decimal('500')
    assert len(challenge.runner_up_prizes) == 2
    assert len(challenge.participation_rewards) == 2
    
    # Validate timing (30-day duration)
    duration = challenge.end_date - challenge.start_date
    assert duration.days == 30
    
    print("✅ Monthly Creative Challenge test passed")
    return True


async def test_seo_challenge():
    """Test SEO technical challenge creation"""
    print("Testing SEO Technical Challenge...")
    
    manager = SpecializedChallengeManager()
    
    challenge = await manager.create_seo_challenge(
        title="SEO Mastery Challenge 2025",
        description="Improve your content's search ranking and organic visibility",
        target_improvement=25.0
    )
    
    # Validate basic properties
    assert challenge.title == "SEO Mastery Challenge 2025"
    assert challenge.technical_focus == "seo"
    assert challenge.seo_targets["ranking_improvement"] == 25.0
    
    # Validate automatic calculation
    assert challenge.seo_targets["organic_traffic_increase"] == 37.5  # 25 * 1.5
    assert challenge.seo_targets["keyword_optimization_count"] == 10
    
    # Validate rewards
    assert len(challenge.achievement_rewards) == 3
    reward_types = [r.reward_type for r in challenge.achievement_rewards]
    assert ChallengeRewardType.POINTS in reward_types
    assert ChallengeRewardType.BADGE in reward_types
    assert ChallengeRewardType.FEATURE_UNLOCK in reward_types
    
    print("✅ SEO Technical Challenge test passed")
    return True


async def test_revenue_optimization_challenge():
    """Test revenue optimization challenge creation"""
    print("Testing Revenue Optimization Challenge...")
    
    manager = SpecializedChallengeManager()
    
    challenge = await manager.create_revenue_challenge(
        title="Revenue Boost Challenge 2025",
        description="Optimize monetization to increase revenue by 50%",
        target_increase=50.0
    )
    
    # Validate basic properties
    assert challenge.title == "Revenue Boost Challenge 2025"
    assert challenge.technical_focus == "revenue_optimization"
    assert challenge.revenue_targets["revenue_increase_percentage"] == 50.0
    assert challenge.revenue_targets["new_revenue_streams"] == 2
    
    # Validate rewards include cash prize
    cash_rewards = [r for r in challenge.achievement_rewards 
                   if r.reward_type == ChallengeRewardType.CASH_PRIZE]
    assert len(cash_rewards) > 0
    assert cash_rewards[0].value == Decimal('300')
    
    print("✅ Revenue Optimization Challenge test passed")
    return True


async def test_global_competition():
    """Test global competition creation"""
    print("Testing Global Competition...")
    
    manager = SpecializedChallengeManager()
    
    competition = await manager.create_global_competition(
        title="Global Creative Championship 2025",
        event_type="seasonal",
        description="The ultimate global creative competition",
        prize_pool=25000
    )
    
    # Validate basic properties
    assert competition.title == "Global Creative Championship 2025"
    assert competition.event_type == "seasonal"
    assert competition.total_prize_pool == Decimal('25000')
    
    # Validate global reach
    assert len(competition.participating_regions) == 7
    assert len(competition.language_support) == 10
    assert "North America" in competition.participating_regions
    assert "Europe" in competition.participating_regions
    assert "en" in competition.language_support
    assert "es" in competition.language_support
    
    # Validate prize distribution
    assert "first_place" in competition.prize_distribution
    first_prize = competition.prize_distribution["first_place"]
    expected_first_prize = Decimal('25000') * Decimal('0.3')  # 30% of pool
    assert first_prize.value == expected_first_prize
    
    print("✅ Global Competition test passed")
    return True


async def test_specialized_rewards():
    """Test specialized reward system"""
    print("Testing Specialized Reward System...")
    
    # Test cash prize reward
    cash_reward = SpecializedReward(
        reward_type=ChallengeRewardType.CASH_PRIZE,
        value=Decimal('500'),
        currency="USD",
        description="Monthly challenge grand prize"
    )
    
    assert cash_reward.reward_type == ChallengeRewardType.CASH_PRIZE
    assert cash_reward.value == Decimal('500')
    assert cash_reward.currency == "USD"
    
    # Test feature unlock reward
    feature_reward = SpecializedReward(
        reward_type=ChallengeRewardType.FEATURE_UNLOCK,
        value="advanced_seo_analytics",
        description="Unlock advanced SEO analytics tools"
    )
    
    assert feature_reward.reward_type == ChallengeRewardType.FEATURE_UNLOCK
    assert feature_reward.value == "advanced_seo_analytics"
    
    # Test badge reward
    badge_reward = SpecializedReward(
        reward_type=ChallengeRewardType.BADGE,
        value="seo_master_2025",
        description="SEO Master Badge 2025"
    )
    
    assert badge_reward.reward_type == ChallengeRewardType.BADGE
    assert badge_reward.value == "seo_master_2025"
    
    print("✅ Specialized Reward System test passed")
    return True


async def test_active_challenges_filtering():
    """Test filtering active challenges"""
    print("Testing Active Challenges Filtering...")
    
    manager = SpecializedChallengeManager()
    now = datetime.now(timezone.utc)
    
    # Create active challenge
    active_challenge = await manager.create_monthly_creative_challenge(
        title="Active Challenge",
        theme="Active Theme",
        start_date=now - timedelta(days=5),
        end_date=now + timedelta(days=25)
    )
    
    # Create expired challenge
    expired_challenge = await manager.create_monthly_creative_challenge(
        title="Expired Challenge",
        theme="Expired Theme",
        start_date=now - timedelta(days=35),
        end_date=now - timedelta(days=5)
    )
    
    # Get active challenges
    active_challenges = await manager.get_active_monthly_challenges()
    
    # Should only return the active challenge
    assert len(active_challenges) == 1
    assert active_challenges[0].title == "Active Challenge"
    
    print("✅ Active Challenges Filtering test passed")
    return True


async def test_challenge_analytics():
    """Test challenge analytics functionality"""
    print("Testing Challenge Analytics...")
    
    manager = SpecializedChallengeManager()
    
    # Create test challenges
    await manager.create_monthly_creative_challenge(
        title="Analytics Test Monthly",
        theme="Test"
    )
    
    await manager.create_seo_challenge(
        title="Analytics Test SEO",
        target_improvement=20.0
    )
    
    await manager.create_revenue_challenge(
        title="Analytics Test Revenue",
        target_increase=30.0
    )
    
    await manager.create_global_competition(
        title="Analytics Test Global",
        event_type="milestone",
        prize_pool=5000
    )
    
    # Get analytics
    analytics = await manager.get_challenge_analytics()
    
    # Validate analytics structure and data
    assert "monthly_challenges" in analytics
    assert "technical_challenges" in analytics
    assert "global_competitions" in analytics
    
    assert analytics["monthly_challenges"]["total"] == 1
    assert analytics["technical_challenges"]["total"] == 2
    assert analytics["technical_challenges"]["seo_challenges"] == 1
    assert analytics["technical_challenges"]["revenue_challenges"] == 1
    assert analytics["global_competitions"]["total"] == 1
    assert analytics["global_competitions"]["total_prize_pool"] == Decimal('5000')
    
    print("✅ Challenge Analytics test passed")
    return True


async def main():
    """Run all tests"""
    print("🎯 Starting Specialized Challenges & Competitions Tests")
    print("=" * 60)
    
    tests = [
        test_monthly_creative_challenge,
        test_seo_challenge,
        test_revenue_optimization_challenge,
        test_global_competition,
        test_specialized_rewards,
        test_active_challenges_filtering,
        test_challenge_analytics
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"🎯 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All specialized challenges and competitions tests passed!")
        print("\n📋 Implemented Features:")
        print("✅ Monthly Creative Challenges with rewards")
        print("✅ Technical SEO Challenges")
        print("✅ Revenue Optimization Challenges")
        print("✅ Global Competitions for special events")
        print("✅ Comprehensive reward system")
        print("✅ Challenge analytics and management")
        return True
    else:
        print(f"⚠️  {failed} tests failed. Please review implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)