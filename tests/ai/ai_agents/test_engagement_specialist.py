# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
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
Comprehensive Tests for EngagementSpecialistAgent

Industrial-grade testing for engagement optimization, community management,
interaction strategies, and audience retention capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from ai.ai_agents import (
    EngagementSpecialistAgent,
    AgentConfiguration,
    AgentCapability
)

logger = logging.getLogger(__name__)


class TestEngagementSpecialistAgent:
    """
Comprehensive test suite for EngagementSpecialistAgent"""
    
    @pytest.fixture
    def engagement_config(self) -> AgentConfiguration:
        """
Engagement specialist agent configuration"""
        return AgentConfiguration(
            agent_id="engagement_specialist_test",
            agent_name="Test Engagement Specialist Agent",
            capabilities={
                AgentCapability.engagement_optimization,
                AgentCapability.community_management,
                AgentCapability.audience_interaction,
                AgentCapability.content_strategy,
                AgentCapability.social_listening,
                AgentCapability.influencer_outreach,
                AgentCapability.trend_monitoring,
                AgentCapability.relationship_building
            },
            max_concurrent_tasks=15,
            default_timeout=45,
            custom_settings={
                "real_time_monitoring": True,
                "sentiment_analysis": True,
                "automated_responses": True,
                "engagement_scoring": True,
                "community_insights": True,
                "crisis_management": True,
                "influencer_collaboration": True,
                "audience_segmentation": True,
                "personalization": True
            }
        )
    
    @pytest.fixture
    async def engagement_agent(self, engagement_config) -> EngagementSpecialistAgent:
        """Initialized engagement specialist agent"""
        agent = EngagementSpecialistAgent(engagement_config)
        await agent.initialize()
        
        yield agent
        
        await agent.shutdown()
    
    async def test_agent_initialization(self, engagement_config):
        """
Test engagement specialist agent initialization"""
        agent = EngagementSpecialistAgent(engagement_config)
        
        # Before initialization
        assert not agent.initialized
        assert agent.status.name == "CREATED"
        
        # Initialize
        result = await agent.initialize()
        
        # After initialization
        assert result is True
        assert agent.initialized
        assert agent.status.name == "READY"
        
        # Verify capabilities
        assert agent.has_capability(AgentCapability.engagement_optimization)
        assert agent.has_capability(AgentCapability.community_management)
        assert agent.has_capability(AgentCapability.audience_interaction)
        assert agent.has_capability(AgentCapability.social_listening)
        
        # Verify settings
        assert agent.get_setting("real_time_monitoring") is True
        assert agent.get_setting("sentiment_analysis") is True
        assert agent.get_setting("automated_responses") is True
        
        await agent.shutdown()
    
    async def test_engagement_optimization(self, engagement_agent, test_engagement_data):
        """Test engagement optimization strategies"""
        optimization_request = {
            "task_type": "engagement_optimization",
            "content_data": {
                "post_id": "test_post_123",
                "content_type": "video",
                "platform": "tiktok",
                "current_metrics": {
                    "views": 10000,
                    "likes": 500,
                    "comments": 50,
                    "shares": 25,
                    "engagement_rate": 0.055
                }
            },
            "optimization_goals": {
                "increase_engagement_rate": 0.08,
                "boost_comments": True,
                "improve_shares": True,
                "extend_reach": True
            },
            "target_audience": {
                "age_range": "18-25",
                "interests": ["technology", "ai", "content_creation"],
                "behavior_patterns": ["night_active", "mobile_first"]
            },
            "timeframe": "24_hours"
        }
        
        result = await engagement_agent.process_task(optimization_request)
        
        # Verify successful optimization
        assert result["success"] is True
        assert "optimization_strategy" in result
        
        strategy = result["optimization_strategy"]
        assert "immediate_actions" in strategy
        assert "content_adjustments" in strategy
        assert "posting_optimization" in strategy
        assert "audience_targeting" in strategy
        assert "performance_predictions" in strategy
        
        # Verify immediate actions
        actions = strategy["immediate_actions"]
        assert isinstance(actions, list)
        assert len(actions) > 0
        for action in actions:
            assert "action_type" in action
            assert "description" in action
            assert "expected_impact" in action
            assert "priority" in action
        
        # Verify content adjustments
        adjustments = strategy["content_adjustments"]
        assert "hashtag_optimization" in adjustments
        assert "caption_enhancement" in adjustments
        assert "visual_improvements" in adjustments
        assert "call_to_action" in adjustments
        
        # Verify posting optimization
        posting = strategy["posting_optimization"]
        assert "optimal_timing" in posting
        assert "frequency_recommendation" in posting
        assert "cross_platform_strategy" in posting
        
        # Verify performance predictions
        predictions = strategy["performance_predictions"]
        assert "expected_engagement_rate" in predictions
        assert "projected_reach" in predictions
        assert "confidence_level" in predictions
        assert predictions["expected_engagement_rate"] > 0.055
    
    async def test_community_management(self, engagement_agent):
        """Test community management capabilities"""
        community_request = {
            "task_type": "community_management",
            "platform": "instagram",
            "management_scope": {
                "comments_moderation": True,
                "dm_responses": True,
                "community_engagement": True,
                "crisis_monitoring": True
            },
            "community_data": {
                "total_followers": 50000,
                "active_members": 15000,
                "engagement_rate": 0.045,
                "sentiment_score": 0.75
            },
            "moderation_rules": {
                "auto_hide_spam": True,
                "filter_inappropriate": True,
                "sentiment_threshold": 0.3,
                "response_time_target": 30  # minutes
            },
            "engagement_strategy": {
                "proactive_engagement": True,
                "community_challenges": True,
                "user_generated_content": True,
                "influencer_collaboration": True
            }
        }
        
        result = await engagement_agent.process_task(community_request)
        
        # Verify successful community management
        assert result["success"] is True
        assert "management_plan" in result
        
        plan = result["management_plan"]
        assert "moderation_strategy" in plan
        assert "engagement_initiatives" in plan
        assert "response_templates" in plan
        assert "monitoring_setup" in plan
        assert "performance_metrics" in plan
        
        # Verify moderation strategy
        moderation = plan["moderation_strategy"]
        assert "automated_filters" in moderation
        assert "escalation_procedures" in moderation
        assert "review_process" in moderation
        
        # Verify engagement initiatives
        initiatives = plan["engagement_initiatives"]
        assert isinstance(initiatives, list)
        for initiative in initiatives:
            assert "name" in initiative
            assert "description" in initiative
            assert "target_metrics" in initiative
            assert "timeline" in initiative
        
        # Verify response templates
        templates = plan["response_templates"]
        assert "welcome_messages" in templates
        assert "thank_you_responses" in templates
        assert "question_responses" in templates
        assert "complaint_handling" in templates
        
        # Verify monitoring setup
        monitoring = plan["monitoring_setup"]
        assert "keywords_tracking" in monitoring
        assert "sentiment_monitoring" in monitoring
        assert "engagement_alerts" in monitoring
    
    async def test_audience_interaction_analysis(self, engagement_agent):
        """Test audience interaction analysis"""
        interaction_request = {
            "task_type": "interaction_analysis",
            "analysis_period": "last_30_days",
            "platforms": ["instagram", "tiktok", "youtube"],
            "interaction_types": [
                "comments", "likes", "shares", "saves", "dm_conversations"
            ],
            "analysis_depth": "comprehensive",
            "include_sentiment": True,
            "segment_analysis": True
        }
        
        result = await engagement_agent.process_task(interaction_request)
        
        # Verify successful interaction analysis
        assert result["success"] is True
        assert "interaction_insights" in result
        
        insights = result["interaction_insights"]
        assert "overall_metrics" in insights
        assert "platform_breakdown" in insights
        assert "audience_segments" in insights
        assert "interaction_patterns" in insights
        assert "sentiment_analysis" in insights
        
        # Verify overall metrics
        overall = insights["overall_metrics"]
        assert "total_interactions" in overall
        assert "engagement_rate" in overall
        assert "response_rate" in overall
        assert "conversation_quality" in overall
        
        # Verify platform breakdown
        platforms = insights["platform_breakdown"]
        assert len(platforms) == 3
        for platform_name, platform_data in platforms.items():
            assert "interaction_volume" in platform_data
            assert "engagement_quality" in platform_data
            assert "top_content_types" in platform_data
        
        # Verify audience segments
        segments = insights["audience_segments"]
        assert isinstance(segments, list)
        for segment in segments:
            assert "segment_name" in segment
            assert "size" in segment
            assert "characteristics" in segment
            assert "interaction_preferences" in segment
        
        # Verify interaction patterns
        patterns = insights["interaction_patterns"]
        assert "peak_activity_times" in patterns
        assert "common_conversation_topics" in patterns
        assert "user_journey_analysis" in patterns
        
        # Verify sentiment analysis
        sentiment = insights["sentiment_analysis"]
        assert "overall_sentiment" in sentiment
        assert "sentiment_distribution" in sentiment
        assert "trending_sentiments" in sentiment
    
    async def test_content_engagement_strategy(self, engagement_agent):
        """Test content engagement strategy development"""
        strategy_request = {
            "task_type": "content_engagement_strategy",
            "content_categories": [
                "educational", "entertainment", "behind_scenes", "user_generated"
            ],
            "target_objectives": {
                "increase_comments": 50,  # percent
                "boost_shares": 75,
                "improve_saves": 100,
                "enhance_story_engagement": 25
            },
            "audience_data": {
                "primary_demographics": {
                    "age": "22-35",
                    "gender": "mixed",
                    "location": "global"
                },
                "interests": ["technology", "creativity", "lifestyle"],
                "behavior_patterns": ["evening_active", "weekend_engaged"]
            },
            "competitive_analysis": True,
            "trend_integration": True
        }
        
        result = await engagement_agent.process_task(strategy_request)
        
        # Verify successful strategy development
        assert result["success"] is True
        assert "engagement_strategy" in result
        
        strategy = result["engagement_strategy"]
        assert "content_calendar" in strategy
        assert "engagement_tactics" in strategy
        assert "audience_interaction_plan" in strategy
        assert "performance_benchmarks" in strategy
        assert "competitive_insights" in strategy
        
        # Verify content calendar
        calendar = strategy["content_calendar"]
        assert "weekly_themes" in calendar
        assert "posting_schedule" in calendar
        assert "content_mix" in calendar
        
        # Verify engagement tactics
        tactics = strategy["engagement_tactics"]
        assert isinstance(tactics, list)
        for tactic in tactics:
            assert "tactic_name" in tactic
            assert "implementation" in tactic
            assert "expected_results" in tactic
            assert "measurement_criteria" in tactic
        
        # Verify audience interaction plan
        interaction_plan = strategy["audience_interaction_plan"]
        assert "response_strategy" in interaction_plan
        assert "proactive_engagement" in interaction_plan
        assert "community_building" in interaction_plan
        
        # Verify competitive insights
        competitive = strategy["competitive_insights"]
        assert "competitor_analysis" in competitive
        assert "opportunity_gaps" in competitive
        assert "differentiation_strategies" in competitive
    
    async def test_social_listening(self, engagement_agent):
        """Test social listening and monitoring"""
        listening_request = {
            "task_type": "social_listening",
            "monitoring_keywords": [
                "AI influencer", "content creation", "social media AI"
            ],
            "platforms": ["twitter", "instagram", "tiktok", "youtube", "linkedin"],
            "monitoring_scope": {
                "brand_mentions": True,
                "competitor_mentions": True,
                "industry_discussions": True,
                "trend_detection": True
            },
            "sentiment_tracking": True,
            "influencer_identification": True,
            "alert_thresholds": {
                "mention_volume": 100,  # per hour
                "sentiment_drop": 0.2,  # 20% negative change
                "viral_potential": 1000  # engagement threshold
            }
        }
        
        result = await engagement_agent.process_task(listening_request)
        
        # Verify successful social listening
        assert result["success"] is True
        assert "listening_insights" in result
        
        insights = result["listening_insights"]
        assert "mention_analysis" in insights
        assert "sentiment_trends" in insights
        assert "conversation_themes" in insights
        assert "influencer_activity" in insights
        assert "alert_summary" in insights
        
        # Verify mention analysis
        mentions = insights["mention_analysis"]
        assert "total_mentions" in mentions
        assert "platform_distribution" in mentions
        assert "mention_growth" in mentions
        assert "reach_analysis" in mentions
        
        # Verify sentiment trends
        sentiment = insights["sentiment_trends"]
        assert "current_sentiment" in sentiment
        assert "sentiment_change" in sentiment
        assert "sentiment_drivers" in sentiment
        
        # Verify conversation themes
        themes = insights["conversation_themes"]
        assert "trending_topics" in themes
        assert "emerging_conversations" in themes
        assert "topic_sentiment" in themes
        
        # Verify influencer activity
        influencers = insights["influencer_activity"]
        assert "key_influencers" in influencers
        assert "influencer_sentiment" in influencers
        assert "collaboration_opportunities" in influencers
        
        # Verify alert summary
        alerts = insights["alert_summary"]
        assert "active_alerts" in alerts
        assert "alert_history" in alerts
        assert "recommended_actions" in alerts
    
    async def test_influencer_outreach(self, engagement_agent):
        """Test influencer outreach and collaboration"""
        outreach_request = {
            "task_type": "influencer_outreach",
            "campaign_objective": "brand_awareness",
            "target_criteria": {
                "follower_range": "10k-100k",
                "engagement_rate_min": 0.03,
                "content_categories": ["technology", "lifestyle"],
                "audience_overlap": 0.7,
                "location": "global"
            },
            "collaboration_types": [
                "sponsored_posts", "product_reviews", "takeovers", "challenges"
            ],
            "budget_range": {
                "min": 1000,
                "max": 10000,
                "currency": "USD"
            },
            "campaign_duration": "3_months"
        }
        
        result = await engagement_agent.process_task(outreach_request)
        
        # Verify successful influencer outreach
        assert result["success"] is True
        assert "outreach_strategy" in result
        
        strategy = result["outreach_strategy"]
        assert "influencer_prospects" in strategy
        assert "outreach_templates" in strategy
        assert "collaboration_proposals" in strategy
        assert "performance_tracking" in strategy
        assert "relationship_management" in strategy
        
        # Verify influencer prospects
        prospects = strategy["influencer_prospects"]
        assert isinstance(prospects, list)
        assert len(prospects) > 0
        for prospect in prospects:
            assert "influencer_id" in prospect
            assert "metrics" in prospect
            assert "fit_score" in prospect
            assert "collaboration_potential" in prospect
        
        # Verify outreach templates
        templates = strategy["outreach_templates"]
        assert "initial_contact" in templates
        assert "follow_up" in templates
        assert "proposal_template" in templates
        assert "contract_template" in templates
        
        # Verify collaboration proposals
        proposals = strategy["collaboration_proposals"]
        assert isinstance(proposals, list)
        for proposal in proposals:
            assert "collaboration_type" in proposal
            assert "deliverables" in proposal
            assert "compensation" in proposal
            assert "timeline" in proposal
    
    async def test_crisis_management(self, engagement_agent):
        """Test crisis management and reputation protection"""
        crisis_request = {
            "task_type": "crisis_management",
            "crisis_type": "negative_sentiment_spike",
            "severity_level": "medium",
            "affected_platforms": ["twitter", "instagram"],
            "crisis_details": {
                "trigger_event": "content_controversy",
                "sentiment_drop": 0.4,
                "mention_spike": 300,  # percent increase
                "key_concerns": ["authenticity", "brand_values"]
            },
            "stakeholders": ["community", "partners", "media"],
            "response_urgency": "immediate"
        }
        
        result = await engagement_agent.process_task(crisis_request)
        
        # Verify successful crisis management
        assert result["success"] is True
        assert "crisis_response_plan" in result
        
        plan = result["crisis_response_plan"]
        assert "immediate_actions" in plan
        assert "communication_strategy" in plan
        assert "monitoring_protocol" in plan
        assert "recovery_plan" in plan
        assert "prevention_measures" in plan
        
        # Verify immediate actions
        actions = plan["immediate_actions"]
        assert isinstance(actions, list)
        for action in actions:
            assert "action" in action
            assert "priority" in action
            assert "timeline" in action
            assert "responsible_party" in action
        
        # Verify communication strategy
        communication = plan["communication_strategy"]
        assert "key_messages" in communication
        assert "stakeholder_communications" in communication
        assert "response_templates" in communication
        
        # Verify monitoring protocol
        monitoring = plan["monitoring_protocol"]
        assert "tracking_metrics" in monitoring
        assert "alert_thresholds" in monitoring
        assert "reporting_frequency" in monitoring
        
        # Verify recovery plan
        recovery = plan["recovery_plan"]
        assert "reputation_rebuild" in recovery
        assert "trust_restoration" in recovery
        assert "long_term_strategy" in recovery
    
    async def test_engagement_scoring(self, engagement_agent):
        """Test engagement scoring and quality assessment"""
        scoring_request = {
            "task_type": "engagement_scoring",
            "content_items": [
                {
                    "content_id": "post_1",
                    "metrics": {
                        "views": 50000,
                        "likes": 2500,
                        "comments": 150,
                        "shares": 75,
                        "saves": 200
                    },
                    "content_type": "video",
                    "platform": "tiktok"
                },
                {
                    "content_id": "post_2",
                    "metrics": {
                        "views": 30000,
                        "likes": 1800,
                        "comments": 200,
                        "shares": 50,
                        "saves": 150
                    },
                    "content_type": "image",
                    "platform": "instagram"
                }
            ],
            "scoring_criteria": {
                "engagement_rate": 0.3,
                "comment_quality": 0.2,
                "share_rate": 0.2,
                "save_rate": 0.15,
                "reach_efficiency": 0.15
            },
            "benchmark_data": True
        }
        
        result = await engagement_agent.process_task(scoring_request)
        
        # Verify successful engagement scoring
        assert result["success"] is True
        assert "scoring_results" in result
        
        results = result["scoring_results"]
        assert "individual_scores" in results
        assert "comparative_analysis" in results
        assert "improvement_recommendations" in results
        assert "benchmark_comparison" in results
        
        # Verify individual scores
        scores = results["individual_scores"]
        assert len(scores) == 2
        for score in scores:
            assert "content_id" in score
            assert "overall_score" in score
            assert "category_scores" in score
            assert "performance_grade" in score
        
        # Verify comparative analysis
        comparative = results["comparative_analysis"]
        assert "best_performing" in comparative
        assert "performance_gaps" in comparative
        assert "success_factors" in comparative
        
        # Verify improvement recommendations
        recommendations = results["improvement_recommendations"]
        assert isinstance(recommendations, list)
        for rec in recommendations:
            assert "content_id" in rec
            assert "recommendations" in rec
            assert "expected_impact" in rec
    
    async def test_audience_retention_analysis(self, engagement_agent):
        """Test audience retention and loyalty analysis"""
        retention_request = {
            "task_type": "audience_retention_analysis",
            "analysis_period": "last_6_months",
            "platforms": ["instagram", "youtube"],
            "retention_metrics": [
                "follower_retention", "engagement_consistency",
                "content_consumption", "community_participation"
            ],
            "segmentation": {
                "by_acquisition_date": True,
                "by_engagement_level": True,
                "by_demographics": True
            },
            "predictive_analysis": True
        }
        
        result = await engagement_agent.process_task(retention_request)
        
        # Verify successful retention analysis
        assert result["success"] is True
        assert "retention_insights" in result
        
        insights = result["retention_insights"]
        assert "overall_retention" in insights
        assert "segment_analysis" in insights
        assert "churn_analysis" in insights
        assert "loyalty_indicators" in insights
        assert "retention_predictions" in insights
        
        # Verify overall retention
        overall = insights["overall_retention"]
        assert "retention_rate" in overall
        assert "average_lifespan" in overall
        assert "engagement_decay" in overall
        
        # Verify segment analysis
        segments = insights["segment_analysis"]
        assert isinstance(segments, list)
        for segment in segments:
            assert "segment_name" in segment
            assert "retention_rate" in segment
            assert "characteristics" in segment
        
        # Verify churn analysis
        churn = insights["churn_analysis"]
        assert "churn_rate" in churn
        assert "churn_reasons" in churn
        assert "at_risk_segments" in churn
        
        # Verify loyalty indicators
        loyalty = insights["loyalty_indicators"]
        assert "high_loyalty_factors" in loyalty
        assert "loyalty_score_distribution" in loyalty
        assert "advocacy_potential" in loyalty
    
    async def test_concurrent_engagement_tasks(self, engagement_agent):
        """Test concurrent engagement processing"""
        tasks = [
            {
                "task_type": "engagement_optimization",
                "content_data": {"post_id": "test_1"},
                "optimization_goals": {"increase_engagement_rate": 0.08}
            },
            {
                "task_type": "social_listening",
                "monitoring_keywords": ["AI"],
                "platforms": ["twitter"]
            },
            {
                "task_type": "interaction_analysis",
                "analysis_period": "last_7_days",
                "platforms": ["instagram"]
            }
        ]
        
        # Execute tasks concurrently
        results = await asyncio.gather(*[
            engagement_agent.process_task(task) for task in tasks
        ])
        
        # Verify all tasks completed successfully
        assert len(results) == 3
        for result in results:
            assert result["success"] is True
    
    @pytest.mark.performance
    async def test_engagement_performance(self, engagement_agent, assert_performance):
        """Test engagement processing performance"""
        # Test optimization speed
        optimization_task = {
            "task_type": "engagement_optimization",
            "content_data": {"post_id": "perf_test"},
            "optimization_goals": {"increase_engagement_rate": 0.08}
        }
        
        result = await engagement_agent.process_task(optimization_task)
        assert_performance("engagement_optimization", max_time=20.0)
        assert result["success"] is True
        
        # Test social listening speed
        listening_task = {
            "task_type": "social_listening",
            "monitoring_keywords": ["test"],
            "platforms": ["twitter", "instagram"]
        }
        
        result = await engagement_agent.process_task(listening_task)
        assert_performance("social_listening", max_time=25.0)
        assert result["success"] is True
    
    async def test_error_handling(self, engagement_agent):
        """Test error handling in engagement processing"""
        # Test invalid platform
        invalid_platform_task = {
            "task_type": "engagement_optimization",
            "content_data": {"platform": "invalid_platform"}
        }
        
        result = await engagement_agent.process_task(invalid_platform_task)
        assert result["success"] is False
        assert "error" in result
        
        # Test missing required data
        incomplete_task = {
            "task_type": "social_listening"
            # Missing required parameters
        }
        
        result = await engagement_agent.process_task(incomplete_task)
        assert result["success"] is False
        assert "error" in result
        
        # Agent should remain functional
        valid_task = {
            "task_type": "interaction_analysis",
            "analysis_period": "last_7_days",
            "platforms": ["instagram"]
        }
        
        result = await engagement_agent.process_task(valid_task)
        assert result["success"] is True
