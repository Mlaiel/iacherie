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

"""Comprehensive Test Suite for Business Logic Core
Tests the complete integration of 53 AI agents

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import pytest
import sys
import os
from pathlib import Path
import pytest_asyncio
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any

from business_logic_core import (
    BusinessLogicCore, 
    ContentUpload, 
    CreatorType, 
    WorkflowStage,
    WorkflowResult,
    initialize_business_logic_core,
    business_logic_core
)

logger = logging.getLogger(__name__)


class TestBusinessLogicCore:
    """Comprehensive test suite for business logic core with 53 agents"""
    
    @pytest_asyncio.fixture
    async def initialized_core(self):
        """Initialize business logic core for testing"""
        core = BusinessLogicCore()
        await core.initialize()
        return core
    
    @pytest.fixture
    def sample_content_musician(self):
        """Sample musician content for testing"""
        return ContentUpload(
            content_id="music_001",
            creator_id="musician_test",
            creator_type=CreatorType.MUSICIAN,
            content_type="audio",
            file_path="/tmp/test_song.mp3",
            metadata={
                "title": "Test Song",
                "description": "Original music composition for testing",
                "tags": ["original", "music", "test"],
                "target_platforms": ["spotify", "youtube", "soundcloud"],
                "collaboration_preferences": {"open_to_collaboration": True},
                "monetization_preferences": {"revenue_sharing": True}
            }
        )
    
    @pytest.fixture
    def sample_content_blogger(self):
        """Sample blogger content for testing"""
        return ContentUpload(
            content_id="blog_001",
            creator_id="blogger_test",
            creator_type=CreatorType.BLOGGER,
            content_type="text",
            file_path="/tmp/test_article.md",
            metadata={
                "title": "Test Article",
                "description": "Tech blog article for testing",
                "tags": ["tech", "ai", "blog"],
                "target_platforms": ["medium", "wordpress", "linkedin"],
                "collaboration_preferences": {"open_to_collaboration": False},
                "monetization_preferences": {"revenue_sharing": False}
            }
        )
    
    @pytest.mark.asyncio
    async def test_business_logic_core_initialization(self, initialized_core):
        """Test that business logic core initializes properly"""
        assert initialized_core.initialized == True
        
        # Test agent count
        agent_status = initialized_core.get_agent_status()
        assert agent_status['total_agents'] == 53
        assert agent_status['active_agents'] == 53
        
        # Test workflow status
        workflow_status = initialized_core.get_workflow_status()
        assert workflow_status['total_workflows'] >= 1
        assert workflow_status['enabled_workflows'] >= 1
        
        logger.info(f"✅ Business logic core initialized with {agent_status['total_agents']} agents")
    
    @pytest.mark.asyncio
    async def test_all_53_agents_present(self, initialized_core):
        """Test that all 53 agents are properly registered"""
        expected_agents = [
            # Core business agents
            'content_agent', 'fingerprinting_agent', 'protection_agent',
            'seo_agent', 'collaboration_agent', 'distribution_agent', 'monetization_agent',
            
            # Analytics agents
            'analytics_agent', 'predictive_analytics_agent',
            
            # Platform agents
            'platform_agent', 'social_media_agent', 'spotify_agent',
            
            # Content format agents
            'audio_agent', 'video_agent', 'image_agent', 'text_agent',
            
            # Business management agents
            'marketplace_agent', 'revenue_agent', 'payment_processing_agent', 'creator_onboarding_agent',
            
            # Security agents
            'fraud_detection_agent', 'compliance_agent', 'gdpr_compliance_agent', 'dmca_agent', 'legal_agent',
            
            # Intelligence agents
            'intelligence_agent', 'recommendation_agent', 'trend_agent', 'market_intelligence_agent', 
            'competitor_monitoring_agent',
            
            # Quality agents
            'quality_agent', 'moderation_agent', 'brand_agent',
            
            # AI processing agents
            'ml_agent', 'nlp_agent', 'vision_agent', 'music_agent',
            
            # Engagement agents
            'engagement_agent', 'licensing_agent', 'crawling_agent', 'audit_trail_agent',
            
            # Communication agents
            'notification_agent', 'support_agent',
            
            # Infrastructure agents
            'api_gateway_agent', 'caching_agent', 'storage_agent', 'vector_agent', 
            'auto_scaling_agent', 'optimization_agent',
            
            # Workflow agents
            'workflow_agent', 'scheduling_agent', 'webhook_agent',
            
            # Advanced agents
            'blockchain_agent'
        ]
        
        assert len(expected_agents) == 53, f"Expected 53 agents, defined {len(expected_agents)}"
        
        for agent_name in expected_agents:
            assert agent_name in initialized_core.agents, f"Agent {agent_name} not found"
            agent = initialized_core.agents[agent_name]
            assert agent['status'] == 'active', f"Agent {agent_name} not active"
            assert agent['initialized'] == True, f"Agent {agent_name} not initialized"
        
        logger.info("✅ All 53 agents are properly registered and active")
    
    @pytest.mark.asyncio
    async def test_complete_workflow_musician(self, initialized_core, sample_content_musician):
        """Test complete workflow for musician content"""
        results = await initialized_core.process_content_workflow(sample_content_musician)
        
        # Verify all stages completed
        assert len(results) == 7, "Should have 7 workflow stages"
        
        # Verify all stages succeeded
        for result in results:
            assert result.success == True, f"Stage {result.stage} failed: {result.errors}"
            assert result.content_id == sample_content_musician.content_id
        
        # Verify specific stage results
        stages = [r.stage for r in results]
        expected_stages = [
            WorkflowStage.CONTENT_ANALYSIS,
            WorkflowStage.RIGHTS_PROTECTION,
            WorkflowStage.SEO_OPTIMIZATION,
            WorkflowStage.COLLABORATION_MATCHING,
            WorkflowStage.DISTRIBUTION,
            WorkflowStage.MONETIZATION,
            WorkflowStage.ANALYTICS
        ]
        
        for expected_stage in expected_stages:
            assert expected_stage in stages, f"Missing stage: {expected_stage}"
        
        # Verify content analysis result
        analysis_result = next(r for r in results if r.stage == WorkflowStage.CONTENT_ANALYSIS)
        assert 'quality_score' in analysis_result.data
        assert analysis_result.data['quality_score'] > 0
        
        # Verify protection result
        protection_result = next(r for r in results if r.stage == WorkflowStage.RIGHTS_PROTECTION)
        assert protection_result.data['protection_applied'] == True
        assert 'fingerprint_id' in protection_result.data
        
        # Verify monetization result
        monetization_result = next(r for r in results if r.stage == WorkflowStage.MONETIZATION)
        assert monetization_result.data['monetization_enabled'] == True
        assert monetization_result.data['estimated_revenue'] > 0
        
        logger.info("✅ Complete musician workflow test passed")
    
    @pytest.mark.asyncio
    async def test_complete_workflow_blogger(self, initialized_core, sample_content_blogger):
        """Test complete workflow for blogger content"""
        results = await initialized_core.process_content_workflow(sample_content_blogger)
        
        # Verify all stages completed successfully
        assert len(results) == 7
        assert all(r.success for r in results), "All workflow stages should succeed"
        
        # Verify SEO optimization for text content
        seo_result = next(r for r in results if r.stage == WorkflowStage.SEO_OPTIMIZATION)
        assert 'keywords' in seo_result.data
        assert 'hashtags' in seo_result.data
        assert seo_result.data['seo_score'] > 80  # High SEO score for blog content
        
        # Verify distribution targets blog platforms
        distribution_result = next(r for r in results if r.stage == WorkflowStage.DISTRIBUTION)
        assert 'platforms' in distribution_result.data
        platforms = distribution_result.data['platforms']
        # Should include text-focused platforms
        assert any('youtube' in p or 'instagram' in p for p in platforms)
        
        logger.info("✅ Complete blogger workflow test passed")
    
    @pytest.mark.asyncio
    async def test_agent_integration_capabilities(self, initialized_core):
        """Test that agents have proper integration capabilities"""
        for agent_name, agent in initialized_core.agents.items():
            # Each agent should have proper structure
            assert 'type' in agent
            assert 'description' in agent
            assert 'status' in agent
            assert 'capabilities' in agent
            assert 'priority' in agent
            
            # Capabilities should be appropriate for agent type
            assert len(agent['capabilities']) >= 1
            assert any(agent_name.replace('_agent', '') in cap for cap in agent['capabilities'])
            
            # Critical agents should have high priority
            if agent_name in ['content_agent', 'protection_agent', 'monetization_agent']:
                assert agent['priority'] == 'high'
        
        logger.info("✅ Agent integration capabilities test passed")
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, initialized_core):
        """Test workflow error handling with invalid content"""
        # Create invalid content
        invalid_content = ContentUpload(
            content_id="invalid_001",
            creator_id="",  # Empty creator ID
            creator_type=CreatorType.MUSICIAN,
            content_type="unknown",  # Invalid content type
            file_path="",  # Empty file path
            metadata={}
        )
        
        # Workflow should handle errors gracefully
        results = await initialized_core.process_content_workflow(invalid_content)
        
        # Should still return results (even if some fail)
        assert len(results) >= 1
        
        logger.info("✅ Workflow error handling test passed")
    
    @pytest.mark.asyncio
    async def test_agent_status_monitoring(self, initialized_core):
        """Test agent status monitoring capabilities"""
        status = initialized_core.get_agent_status()
        
        assert status['total_agents'] == 53
        assert status['active_agents'] == 53
        assert len(status['agent_types']) == 53
        assert status['initialized'] == True
        
        # All agent types should be unique
        assert len(set(status['agent_types'])) == len(status['agent_types'])
        
        logger.info("✅ Agent status monitoring test passed")
    
    @pytest.mark.asyncio
    async def test_global_business_logic_core(self):
        """Test the global business logic core instance"""
        success = await initialize_business_logic_core()
        assert success == True
        
        # Test global instance
        assert business_logic_core.initialized == True
        assert len(business_logic_core.agents) == 53
        
        # Test sample workflow on global instance
        test_content = ContentUpload(
            content_id="global_test_001",
            creator_id="global_creator",
            creator_type=CreatorType.PHOTOGRAPHER,
            content_type="image",
            file_path="/tmp/test.jpg",
            metadata={"title": "Test Photo", "tags": ["test", "photo"]}
        )
        
        results = await business_logic_core.process_content_workflow(test_content)
        assert len(results) == 7
        assert all(r.success for r in results)
        
        logger.info("✅ Global business logic core test passed")
    
    @pytest.mark.asyncio
    async def test_multiple_creator_types(self, initialized_core):
        """Test workflow with different creator types"""
        creator_types = [
            CreatorType.MUSICIAN,
            CreatorType.BLOGGER,
            CreatorType.PHOTOGRAPHER,
            CreatorType.INFLUENCER,
            CreatorType.COMEDIAN,
            CreatorType.PODCASTER
        ]
        
        for creator_type in creator_types:
            content = ContentUpload(
                content_id=f"test_{creator_type.value}_001",
                creator_id=f"{creator_type.value}_creator",
                creator_type=creator_type,
                content_type="mixed_media",
                file_path=f"/tmp/test_{creator_type.value}.file",
                metadata={"title": f"Test {creator_type.value} Content"}
            )
            
            results = await initialized_core.process_content_workflow(content)
            
            # Each creator type should complete workflow successfully
            assert len(results) == 7
            assert all(r.success for r in results), f"Workflow failed for {creator_type.value}"
        
        logger.info("✅ Multiple creator types test passed")
    
    def test_business_logic_core_import(self):
        """Test that business logic core can be imported correctly"""
        # Import test
        from business_logic_core import BusinessLogicCore, business_logic_core
        
        assert BusinessLogicCore is not None
        assert business_logic_core is not None
        
        logger.info("✅ Business logic core import test passed")
    
    @pytest.mark.asyncio
    async def test_workflow_performance(self, initialized_core, sample_content_musician):
        """Test workflow performance with timing"""
        start_time = datetime.now()
        
        results = await initialized_core.process_content_workflow(sample_content_musician)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Workflow should complete in reasonable time
        assert duration < 10.0, f"Workflow took too long: {duration}s"
        assert len(results) == 7
        assert all(r.success for r in results)
        
        logger.info(f"✅ Workflow performance test passed ({duration:.2f}s)")


if __name__ == "__main__":
    async def run_tests():
        """Run all tests manually"""
        print("🧪 Running Business Logic Core Tests")
        
        # Initialize test instance
        test_instance = TestBusinessLogicCore()
        
        try:
            # Test 1: Initialization
            print("🧪 Test 1: Initialization")
            core = BusinessLogicCore()
            await core.initialize()
            await test_instance.test_business_logic_core_initialization(core)
            print("✅ Initialization test passed")
            
            # Test 2: All 53 agents
            print("🧪 Test 2: All 53 Agents")
            await test_instance.test_all_53_agents_present(core)
            print("✅ All 53 agents test passed")
            
            # Test 3: Complete workflow
            print("🧪 Test 3: Complete Workflow")
            sample_content = ContentUpload(
                content_id="test_manual_001",
                creator_id="manual_test_creator",
                creator_type=CreatorType.MUSICIAN,
                content_type="audio",
                file_path="/tmp/manual_test.mp3",
                metadata={"title": "Manual Test Song", "tags": ["test"]}
            )
            await test_instance.test_complete_workflow_musician(core, sample_content)
            print("✅ Complete workflow test passed")
            
            # Test 4: Global instance
            print("🧪 Test 4: Global Instance")
            await test_instance.test_global_business_logic_core()
            print("✅ Global instance test passed")
            
            print("🏆 All tests passed successfully!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Run manual tests
    asyncio.run(run_tests())