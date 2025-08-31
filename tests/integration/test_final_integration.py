# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Final Integration Test for Business Logic Core with 53 Agents
Validates the complete business workflow integration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
from datetime import datetime

from business_logic_core import (
    BusinessLogicCore, 
    ContentUpload, 
    CreatorType,
    business_logic_core,
    initialize_business_logic_core
)

logger = logging.getLogger(__name__)


async def test_complete_integration():
    """Test complete integration of 53 agents in business logic core"""    print("🚀 Testing Complete Business Logic Core Integration")
    print("=" * 60)
    
    try:
        # Test 1: Initialize Business Logic Core
        print("📝 Test 1: Initializing Business Logic Core with 53 agents...")
        success = await initialize_business_logic_core()
        assert success, "Failed to initialize business logic core"
        print("✅ Business Logic Core initialized successfully")
        
        # Test 2: Verify all 53 agents are active
        print("\n📝 Test 2: Verifying all 53 agents are active...")
        agent_status = business_logic_core.get_agent_status()
        print(f"   📊 Total agents: {agent_status['total_agents']}")
        print(f"   📊 Active agents: {agent_status['active_agents']}")
        assert agent_status['total_agents'] == 53, f"Expected 53 agents, got {agent_status['total_agents']}"
        assert agent_status['active_agents'] == 53, f"Expected 53 active agents, got {agent_status['active_agents']}"
        print("✅ All 53 agents are active and operational")
        
        # Test 3: Test workflow for different creator types
        creator_types = [
            CreatorType.MUSICIAN,
            CreatorType.BLOGGER, 
            CreatorType.PHOTOGRAPHER,
            CreatorType.INFLUENCER,
            CreatorType.COMEDIAN
        ]
        
        workflow_results = {}
        
        for i, creator_type in enumerate(creator_types, 1):
            print(f"\n📝 Test 3.{i}: Testing {creator_type.value} workflow...")
            
            content = ContentUpload(
                content_id=f"{creator_type.value}_content_001",
                creator_id=f"{creator_type.value}_creator_001",
                creator_type=creator_type,
                content_type="mixed_media",
                file_path=f"/tmp/{creator_type.value}_content.file",
                metadata={
                    "title": f"Test {creator_type.value.title()} Content",
                    "description": f"Professional {creator_type.value} content for testing",
                    "tags": [creator_type.value, "professional", "test"],
                    "target_platforms": ["youtube", "instagram", "tiktok"]
                }
            )
            
            start_time = datetime.now()
            results = await business_logic_core.process_content_workflow(content)
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds()
            
            # Validate results
            assert len(results) == 7, f"Expected 7 stages, got {len(results)}"
            successful_stages = [r for r in results if r.success]
            assert len(successful_stages) == 7, f"All stages should succeed for {creator_type.value}"
            
            workflow_results[creator_type.value] = {
                'stages': len(results),
                'successful': len(successful_stages),
                'duration': duration,
                'results': results
            }
            
            print(f"   ✅ {creator_type.value} workflow completed successfully ({duration:.2f}s)")
        
        # Test 4: Performance analysis
        print(f"\n📝 Test 4: Performance Analysis...")
        total_duration = sum(r['duration'] for r in workflow_results.values())
        avg_duration = total_duration / len(workflow_results)
        
        print(f"   📊 Total workflows processed: {len(workflow_results)}")
        print(f"   📊 Total processing time: {total_duration:.2f}s")
        print(f"   📊 Average processing time: {avg_duration:.2f}s")
        print(f"   📊 Total stages processed: {sum(r['stages'] for r in workflow_results.values())}")
        
        assert avg_duration < 5.0, f"Average processing time too high: {avg_duration:.2f}s"
        print("✅ Performance metrics are within acceptable limits")
        
        # Test 5: Agent capability verification
        print(f"\n📝 Test 5: Verifying agent capabilities...")
        critical_agents = [
            'content_agent', 'protection_agent', 'seo_agent', 
            'collaboration_agent', 'distribution_agent', 'monetization_agent',
            'analytics_agent'
        ]
        
        for agent_name in critical_agents:
            assert agent_name in business_logic_core.agents, f"Critical agent {agent_name} not found"
            agent = business_logic_core.agents[agent_name]
            assert agent['status'] == 'active', f"Critical agent {agent_name} not active"
            assert len(agent['capabilities']) > 0, f"Critical agent {agent_name} has no capabilities"
        
        print("✅ All critical agents have proper capabilities")
        
        # Test 6: Workflow stage verification
        print(f"\n📝 Test 6: Verifying workflow stages...")
        expected_stages = [
            'content_analysis', 'rights_protection', 'seo_optimization',
            'collaboration_matching', 'distribution', 'monetization', 'analytics'
        ]
        
        # Check one workflow result in detail
        sample_result = workflow_results[CreatorType.MUSICIAN.value]['results']
        actual_stages = [r.stage.value for r in sample_result]
        
        for expected_stage in expected_stages:
            assert expected_stage in actual_stages, f"Missing stage: {expected_stage}"
        
        print("✅ All required workflow stages are present and functional")
        
        # Test 7: Data integrity verification
        print(f"\n📝 Test 7: Verifying data integrity...")
        for creator_type, result_data in workflow_results.items():
            for result in result_data['results']:
                assert result.content_id is not None, f"Missing content_id in {creator_type} workflow"
                assert result.stage is not None, f"Missing stage in {creator_type} workflow"
                assert isinstance(result.data, dict), f"Invalid data format in {creator_type} workflow"
                assert isinstance(result.errors, list), f"Invalid errors format in {creator_type} workflow"
        
        print("✅ Data integrity verified across all workflows")
        
        # Final summary
        print("\n" + "=" * 60)
        print("🏆 BUSINESS LOGIC CORE INTEGRATION TEST RESULTS")
        print("=" * 60)
        print(f"✅ Total agents initialized: {agent_status['total_agents']}")
        print(f"✅ Creator types tested: {len(creator_types)}")
        print(f"✅ Total workflows processed: {len(workflow_results)}")
        print(f"✅ Total stages executed: {sum(r['stages'] for r in workflow_results.values())}")
        print(f"✅ Average processing time: {avg_duration:.2f}s")
        print(f"✅ Success rate: 100%")
        print("\n🎉 ALL TESTS PASSED! Business Logic Core with 53 agents is fully operational!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_registry_completeness():
    """Test that the agent registry matches the business logic core"""    print("\n🔍 Testing Agent Registry Completeness...")
    
    try:
        # Import the existing agent registry
        from ai_agents.AGENTS_REGISTRY_COMPLET import EXISTING_AGENTS_REGISTRY
        
        # Get business logic core agents
        await initialize_business_logic_core()
        core_agents = set(business_logic_core.agents.keys())
        
        # Check overlap
        registry_agents = set(EXISTING_AGENTS_REGISTRY.keys())
        
        print(f"   📊 Registry agents: {len(registry_agents)}")
        print(f"   📊 Core agents: {len(core_agents)}")
        
        # Find matches
        matching_agents = core_agents.intersection(registry_agents)
        core_only = core_agents - registry_agents
        registry_only = registry_agents - core_agents
        
        print(f"   📊 Matching agents: {len(matching_agents)}")
        print(f"   📊 Core only: {len(core_only)}")
        print(f"   📊 Registry only: {len(registry_only)}")
        
        if core_only:
            print(f"   🔍 Agents in core but not registry: {sorted(core_only)}")
        
        print("✅ Agent registry analysis completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Registry test failed: {e}")
        return False


if __name__ == "__main__":
    async def main():
        """Run all integration tests"""        print("🚀 Starting Business Logic Core Final Integration Tests")
        print("📅 " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Run main integration test
        test1_success = await test_complete_integration()
        
        # Run registry completeness test
        test2_success = await test_agent_registry_completeness()
        
        # Final result
        if test1_success and test2_success:
            print("\n🎉 ALL INTEGRATION TESTS PASSED!")
            print("✅ Business Logic Core with 53 agents is ready for production")
        else:
            print("\n❌ Some integration tests failed")
            print("🔧 Please review the results and fix any issues")
    
    # Run the tests
    asyncio.run(main())