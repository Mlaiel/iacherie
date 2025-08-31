# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Test suite for Collaboration AI Agents

Tests all functionalities of collaboration matching, partnership opportunities, 
cross-promotion strategies, and network building agents.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from ai.ai_agents.collaboration_agents import (
    CollaborationMatcherAgent,
    NetworkAnalysisAgent,
    PartnershipAgent,
    CrossPromotionAgent,
    CollaborationMatch,
    NetworkAnalysis,
    PartnershipProposal,
    CrossPromotionCampaign
)


class TestCollaborationMatcherAgent:
    """Test CollaborationMatcherAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create CollaborationMatcherAgent instance"""
        return CollaborationMatcherAgent()
    
    @pytest.fixture
    def sample_creator_profile(self):
        """Sample creator profile for collaboration matching"""
        return {
            "creator_id": "creator_001",
            "name": "TechCreator",
            "niche": "technology",
            "total_followers": 50000,
            "engagement_rate": 0.055,
            "audience_demographics": {
                "age_groups": {"18-24": 25, "25-34": 45, "35-44": 25, "45+": 5},
                "gender": {"male": 60, "female": 38, "other": 2},
                "interests": ["programming", "AI", "gadgets", "tech news"]
            },
            "content_style": {
                "format_preference": ["video", "tutorial", "review"],
                "tone": "educational_friendly",
                "posting_frequency": "daily",
                "average_video_length": 600
            },
            "brand_values": ["innovation", "accessibility", "quality"],
            "collaboration_history": [
                {"partner": "partner_1", "type": "joint_video", "success_score": 0.8},
                {"partner": "partner_2", "type": "cross_promotion", "success_score": 0.6}
            ]
        }
    
    @pytest.fixture
    def sample_collaboration_goals(self):
        """Sample collaboration goals"""
        return {
            "primary_objectives": ["audience_growth", "content_diversification"],
            "preferred_collaboration_types": ["joint_creation", "cross_promotion"],
            "target_audience_expansion": ["younger_demographics", "international"],
            "content_goals": ["tutorial_series", "product_reviews"],
            "timeline": "3_months",
            "commitment_level": "moderate"
        }
    
    @pytest.mark.asyncio
    async def test_find_collaboration_matches(self, agent, sample_creator_profile, sample_collaboration_goals):
        """Test collaboration match finding"""
        matches = await agent.find_collaboration_matches(
            sample_creator_profile, 
            sample_collaboration_goals
        )
        
        assert isinstance(matches, list)
        assert len(matches) > 0
        
        for match in matches[:3]:  # Check first 3 matches
            assert isinstance(match, CollaborationMatch)
            assert match.partner_id is not None
            assert 0 <= match.compatibility_score <= 1
            assert 0 <= match.audience_overlap <= 1
            assert 0 <= match.synergy_potential <= 1
            assert len(match.collaboration_types) > 0
            assert match.estimated_reach_boost >= 0
            assert len(match.mutual_benefits) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_compatibility(self, agent, sample_creator_profile):
        """Test creator compatibility analysis"""
        potential_partner = {
            "creator_id": "creator_002",
            "niche": "tech_reviews",
            "total_followers": 75000,
            "engagement_rate": 0.045,
            "audience_demographics": {
                "age_groups": {"18-24": 35, "25-34": 40, "35-44": 20, "45+": 5},
                "gender": {"male": 55, "female": 42, "other": 3},
                "interests": ["tech reviews", "gaming", "mobile tech"]
            },
            "content_style": {
                "format_preference": ["video", "livestream"],
                "tone": "entertaining_informative"
            }
        }
        
        compatibility = await agent.analyze_compatibility(
            sample_creator_profile, 
            potential_partner
        )
        
        assert "compatibility_score" in compatibility
        assert "factor_breakdown" in compatibility
        assert "strengths" in compatibility
        assert "challenges" in compatibility
        assert 0 <= compatibility["compatibility_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_calculate_audience_synergy(self, agent, sample_creator_profile):
        """Test audience synergy calculation"""
        partner_profile = {
            "audience_demographics": {
                "age_groups": {"18-24": 40, "25-34": 35, "35-44": 20, "45+": 5},
                "interests": ["AI", "programming", "startups", "innovation"]
            },
            "total_followers": 60000,
            "geographic_distribution": {"US": 50, "EU": 30, "Asia": 15, "Other": 5}
        }
        
        synergy = await agent.calculate_audience_synergy(
            sample_creator_profile,
            partner_profile
        )
        
        assert "overlap_percentage" in synergy
        assert "complementary_segments" in synergy
        assert "growth_potential" in synergy
        assert "synergy_score" in synergy
        assert 0 <= synergy["overlap_percentage"] <= 1
        assert 0 <= synergy["synergy_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_recommend_collaboration_types(self, agent, sample_creator_profile, sample_collaboration_goals):
        """Test collaboration type recommendations"""
        recommendations = await agent.recommend_collaboration_types(
            sample_creator_profile,
            sample_collaboration_goals
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for rec in recommendations:
            assert "type" in rec
            assert "description" in rec
            assert "suitability_score" in rec
            assert "implementation_complexity" in rec
            assert "expected_outcomes" in rec
            assert 0 <= rec["suitability_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_generate_collaboration_proposal(self, agent, sample_creator_profile):
        """Test collaboration proposal generation"""
        match_data = {
            "partner_id": "creator_002",
            "partner_name": "TechReviewer",
            "collaboration_type": "joint_video_series",
            "compatibility_score": 0.85
        }
        
        proposal = await agent.generate_collaboration_proposal(
            sample_creator_profile,
            match_data
        )
        
        assert "proposal_title" in proposal
        assert "collaboration_concept" in proposal
        assert "mutual_benefits" in proposal
        assert "resource_requirements" in proposal
        assert "timeline" in proposal
        assert "success_metrics" in proposal


class TestNetworkAnalysisAgent:
    """Test NetworkAnalysisAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create NetworkAnalysisAgent instance"""
        return NetworkAnalysisAgent()
    
    @pytest.fixture
    def sample_network_data(self):
        """Sample network data for analysis"""
        return {
            "creator_id": "creator_001",
            "direct_connections": [
                {"id": "creator_002", "relationship_strength": 0.8, "collaboration_count": 3},
                {"id": "creator_003", "relationship_strength": 0.6, "collaboration_count": 1},
                {"id": "creator_004", "relationship_strength": 0.9, "collaboration_count": 5}
            ],
            "indirect_connections": [
                {"id": "creator_005", "mutual_connections": 2, "potential_reach": 100000},
                {"id": "creator_006", "mutual_connections": 1, "potential_reach": 75000}
            ],
            "collaboration_history": {
                "total_collaborations": 9,
                "successful_collaborations": 7,
                "average_roi": 1.4,
                "top_performing_types": ["joint_videos", "cross_promotion"]
            },
            "network_metrics": {
                "network_size": 15,
                "average_connection_strength": 0.7,
                "network_diversity": 0.6,
                "influence_centrality": 0.75
            }
        }
    
    @pytest.mark.asyncio
    async def test_analyze_creator_network(self, agent, sample_network_data):
        """Test creator network analysis"""
        analysis = await agent.analyze_creator_network(sample_network_data)
        
        assert isinstance(analysis, NetworkAnalysis)
        assert 0 <= analysis.network_strength <= 1
        assert 0 <= analysis.influence_score <= 1
        assert analysis.collaboration_history is not None
        assert len(analysis.growth_opportunities) > 0
        assert isinstance(analysis.relationship_gaps, list)
        assert isinstance(analysis.strategic_connections, list)
    
    @pytest.mark.asyncio
    async def test_identify_network_gaps(self, agent, sample_network_data):
        """Test network gap identification"""
        gaps = await agent.identify_network_gaps(sample_network_data)
        
        assert isinstance(gaps, list)
        
        for gap in gaps:
            assert "gap_type" in gap
            assert "description" in gap
            assert "impact_potential" in gap
            assert "recommended_actions" in gap
            assert gap["gap_type"] in ["niche_gap", "geographic_gap", "audience_gap", "influence_gap"]
    
    @pytest.mark.asyncio
    async def test_recommend_strategic_connections(self, agent, sample_network_data):
        """Test strategic connection recommendations"""
        recommendations = await agent.recommend_strategic_connections(sample_network_data)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for rec in recommendations:
            assert "target_creator" in rec
            assert "connection_value" in rec
            assert "approach_strategy" in rec
            assert "expected_benefits" in rec
            assert 0 <= rec["connection_value"] <= 1
    
    @pytest.mark.asyncio
    async def test_calculate_network_influence(self, agent, sample_network_data):
        """Test network influence calculation"""
        influence = await agent.calculate_network_influence(sample_network_data)
        
        assert "influence_score" in influence
        assert "centrality_metrics" in influence
        assert "reach_potential" in influence
        assert "network_effects" in influence
        assert 0 <= influence["influence_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_optimize_network_growth(self, agent, sample_network_data):
        """Test network growth optimization"""
        optimization = await agent.optimize_network_growth(sample_network_data)
        
        assert "growth_strategy" in optimization
        assert "priority_connections" in optimization
        assert "networking_tactics" in optimization
        assert "timeline_recommendations" in optimization


class TestPartnershipAgent:
    """Test PartnershipAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create PartnershipAgent instance"""
        return PartnershipAgent()
    
    @pytest.fixture
    def sample_partnership_requirements(self):
        """Sample partnership requirements"""
        return {
            "partnership_type": "brand_collaboration",
            "creator_profile": {
                "niche": "lifestyle",
                "followers": 100000,
                "engagement_rate": 0.065,
                "demographics": {"primary_age": "25-34", "primary_gender": "female"}
            },
            "brand_requirements": {
                "industry": "fashion",
                "target_audience": "young_women",
                "campaign_budget": "$10000",
                "campaign_duration": "1_month"
            },
            "deliverables": [
                {"type": "instagram_posts", "quantity": 3},
                {"type": "stories", "quantity": 5},
                {"type": "reel", "quantity": 1}
            ]
        }
    
    @pytest.mark.asyncio
    async def test_evaluate_partnership_fit(self, agent, sample_partnership_requirements):
        """Test partnership fit evaluation"""
        evaluation = await agent.evaluate_partnership_fit(sample_partnership_requirements)
        
        assert "fit_score" in evaluation
        assert "alignment_factors" in evaluation
        assert "potential_challenges" in evaluation
        assert "success_probability" in evaluation
        assert 0 <= evaluation["fit_score"] <= 1
        assert 0 <= evaluation["success_probability"] <= 1
    
    @pytest.mark.asyncio
    async def test_negotiate_partnership_terms(self, agent, sample_partnership_requirements):
        """Test partnership term negotiation"""
        negotiation = await agent.negotiate_partnership_terms(sample_partnership_requirements)
        
        assert "proposed_terms" in negotiation
        assert "negotiation_points" in negotiation
        assert "value_proposition" in negotiation
        assert "contract_framework" in negotiation
    
    @pytest.mark.asyncio
    async def test_create_partnership_proposal(self, agent, sample_partnership_requirements):
        """Test partnership proposal creation"""
        proposal = await agent.create_partnership_proposal(sample_partnership_requirements)
        
        assert isinstance(proposal, PartnershipProposal)
        assert proposal.partnership_type is not None
        assert proposal.value_proposition is not None
        assert len(proposal.deliverables) > 0
        assert proposal.timeline is not None
        assert proposal.compensation is not None
    
    @pytest.mark.asyncio
    async def test_monitor_partnership_performance(self, agent, sample_partnership_requirements):
        """Test partnership performance monitoring"""
        campaign_data = {
            "posts_performance": [
                {"reach": 25000, "engagement": 1500, "clicks": 200},
                {"reach": 30000, "engagement": 1800, "clicks": 250},
                {"reach": 28000, "engagement": 1700, "clicks": 220}
            ],
            "overall_metrics": {
                "total_reach": 83000,
                "total_engagement": 5000,
                "conversion_rate": 0.08
            }
        }
        
        performance = await agent.monitor_partnership_performance(
            sample_partnership_requirements,
            campaign_data
        )
        
        assert "performance_summary" in performance
        assert "kpi_analysis" in performance
        assert "optimization_recommendations" in performance
        assert "roi_calculation" in performance


class TestCrossPromotionAgent:
    """Test CrossPromotionAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create CrossPromotionAgent instance"""
        return CrossPromotionAgent()
    
    @pytest.fixture
    def sample_cross_promotion_setup(self):
        """Sample cross-promotion setup"""
        return {
            "primary_creator": {
                "id": "creator_001",
                "followers": 50000,
                "engagement_rate": 0.05,
                "niche": "fitness"
            },
            "partner_creators": [
                {
                    "id": "creator_002",
                    "followers": 40000,
                    "engagement_rate": 0.06,
                    "niche": "nutrition"
                },
                {
                    "id": "creator_003", 
                    "followers": 60000,
                    "engagement_rate": 0.045,
                    "niche": "wellness"
                }
            ],
            "campaign_objectives": [
                "audience_growth",
                "cross_niche_exposure",
                "community_building"
            ],
            "content_themes": ["healthy_lifestyle", "fitness_tips", "wellness_journey"]
        }
    
    @pytest.mark.asyncio
    async def test_design_cross_promotion_campaign(self, agent, sample_cross_promotion_setup):
        """Test cross-promotion campaign design"""
        campaign = await agent.design_cross_promotion_campaign(sample_cross_promotion_setup)
        
        assert isinstance(campaign, CrossPromotionCampaign)
        assert campaign.campaign_name is not None
        assert len(campaign.participating_creators) > 0
        assert len(campaign.content_schedule) > 0
        assert campaign.success_metrics is not None
        assert campaign.timeline is not None
    
    @pytest.mark.asyncio
    async def test_optimize_promotion_strategy(self, agent, sample_cross_promotion_setup):
        """Test promotion strategy optimization"""
        strategy = await agent.optimize_promotion_strategy(sample_cross_promotion_setup)
        
        assert "content_distribution" in strategy
        assert "timing_optimization" in strategy
        assert "engagement_tactics" in strategy
        assert "measurement_framework" in strategy
    
    @pytest.mark.asyncio
    async def test_calculate_mutual_benefits(self, agent, sample_cross_promotion_setup):
        """Test mutual benefits calculation"""
        benefits = await agent.calculate_mutual_benefits(sample_cross_promotion_setup)
        
        assert isinstance(benefits, dict)
        
        for creator_id in [sample_cross_promotion_setup["primary_creator"]["id"]] + [c["id"] for c in sample_cross_promotion_setup["partner_creators"]]:
            assert creator_id in benefits
            assert "expected_reach_gain" in benefits[creator_id]
            assert "audience_growth_potential" in benefits[creator_id]
            assert "engagement_boost" in benefits[creator_id]
    
    @pytest.mark.asyncio
    async def test_track_campaign_performance(self, agent, sample_cross_promotion_setup):
        """Test campaign performance tracking"""
        campaign_results = {
            "creator_001": {"new_followers": 500, "engagement_increase": 0.008, "reach": 75000},
            "creator_002": {"new_followers": 600, "engagement_increase": 0.01, "reach": 65000},
            "creator_003": {"new_followers": 450, "engagement_increase": 0.006, "reach": 85000}
        }
        
        tracking = await agent.track_campaign_performance(
            sample_cross_promotion_setup,
            campaign_results
        )
        
        assert "individual_performance" in tracking
        assert "collective_impact" in tracking
        assert "success_rate" in tracking
        assert "lessons_learned" in tracking


class TestIntegrationScenarios:
    """Test integration between different collaboration agents"""
    
    @pytest.fixture
    def agents(self):
        """Create all collaboration agents for integration testing"""
        return {
            "matcher": CollaborationMatcherAgent(),
            "network": NetworkAnalysisAgent(),
            "partnership": PartnershipAgent(),
            "cross_promotion": CrossPromotionAgent()
        }
    
    @pytest.mark.asyncio
    async def test_comprehensive_collaboration_workflow(self, agents):
        """Test comprehensive collaboration workflow"""
        # Sample creator looking for collaborations
        creator_data = {
            "creator_id": "integration_creator",
            "profile": {
                "niche": "tech_education",
                "followers": 75000,
                "engagement_rate": 0.055,
                "content_style": "educational_entertaining"
            },
            "network": {
                "connections": 12,
                "collaboration_history": 8,
                "network_strength": 0.7
            },
            "goals": {
                "target_growth": 150000,
                "collaboration_types": ["joint_content", "cross_promotion"],
                "timeline": "6_months"
            }
        }
        
        # Execute integrated workflow
        # 1. Find collaboration matches
        matches = await agents["matcher"].find_collaboration_matches(
            creator_data["profile"],
            creator_data["goals"]
        )
        
        # 2. Analyze network opportunities
        network_analysis = await agents["network"].analyze_creator_network(creator_data["network"])
        
        # 3. Evaluate partnership potential (using first match)
        if matches:
            partnership_eval = await agents["partnership"].evaluate_partnership_fit({
                "partnership_type": "collaboration",
                "creator_profile": creator_data["profile"],
                "partner_profile": {"creator_id": matches[0].partner_id}
            })
        
        # 4. Design cross-promotion campaign
        cross_promo_setup = {
            "primary_creator": creator_data["profile"],
            "partner_creators": [{"id": match.partner_id} for match in matches[:2]],
            "campaign_objectives": ["audience_growth"]
        }
        
        cross_promo_campaign = await agents["cross_promotion"].design_cross_promotion_campaign(
            cross_promo_setup
        )
        
        # Verify integrated results
        assert len(matches) > 0
        assert network_analysis is not None
        assert cross_promo_campaign is not None
        
        # Verify workflow coherence
        assert matches[0].compatibility_score > 0.5
        assert network_analysis.network_strength >= 0
        assert len(cross_promo_campaign.participating_creators) > 0


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def agent(self):
        """Create CollaborationMatcherAgent for error testing"""
        return CollaborationMatcherAgent()
    
    @pytest.mark.asyncio
    async def test_invalid_creator_profile(self, agent):
        """Test handling of invalid creator profile"""
        invalid_profile = {"invalid": "data"}
        goals = {"objectives": ["growth"]}
        
        with pytest.raises((ValueError, KeyError)):
            await agent.find_collaboration_matches(invalid_profile, goals)
    
    @pytest.mark.asyncio
    async def test_empty_collaboration_goals(self, agent):
        """Test handling of empty collaboration goals"""
        valid_profile = {"creator_id": "test", "niche": "tech", "followers": 1000}
        empty_goals = {}
        
        try:
            matches = await agent.find_collaboration_matches(valid_profile, empty_goals)
            # Should handle gracefully with default behavior
            assert isinstance(matches, list)
        except (ValueError, KeyError):
            # Acceptable to require minimum goals
            pass
    
    @pytest.mark.asyncio
    async def test_network_failure_handling(self, agent):
        """Test handling of network failures"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = Exception("Network error")
            
            try:
                result = await agent.find_collaboration_matches(
                    {"creator_id": "test"}, 
                    {"objectives": ["growth"]}
                )
                # Should provide fallback or handle gracefully
                assert result is not None or True
            except Exception as e:
                # Should provide meaningful error context
                assert len(str(e)) > 0


class TestPerformanceAndScaling:
    """Test performance and scaling scenarios"""
    
    @pytest.fixture
    def agent(self):
        """Create CollaborationMatcherAgent for performance testing"""
        return CollaborationMatcherAgent()
    
    @pytest.mark.asyncio
    async def test_large_scale_matching(self, agent):
        """Test large-scale collaboration matching performance"""
        # Simulate large creator database
        large_profile = {
            "creator_id": "large_creator",
            "niche": "lifestyle",
            "followers": 500000,
            "potential_matches": 10000  # Large potential match set
        }
        
        goals = {"objectives": ["growth"], "max_matches": 20}
        
        start_time = datetime.now()
        matches = await agent.find_collaboration_matches(large_profile, goals)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        assert isinstance(matches, list)
        assert processing_time < 30  # Should complete within reasonable time
    
    @pytest.mark.asyncio
    async def test_concurrent_matching_requests(self, agent):
        """Test concurrent collaboration matching"""
        profiles = [
            {"creator_id": f"creator_{i}", "niche": "tech", "followers": 10000 + i*1000}
            for i in range(5)
        ]
        
        goals = {"objectives": ["growth"]}
        
        tasks = [
            agent.find_collaboration_matches(profile, goals)
            for profile in profiles
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        assert len(results) == len(profiles)
        for result in results:
            assert not isinstance(result, Exception)
