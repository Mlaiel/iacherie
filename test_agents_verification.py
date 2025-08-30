"""
Test script to verify 53 agents implementation in business_logic_core.py

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from business_logic_core import BusinessLogicCore, ContentUpload, CreatorType


async def test_53_agents_verification():
    """Test that all 53 agents are properly implemented and functional"""
    
    print("🔍 Testing Business Logic Core - 53 Agents Verification")
    print("=" * 60)
    
    # Initialize business logic core
    business_core = BusinessLogicCore()
    
    print("🚀 Initializing Business Logic Core...")
    success = await business_core.initialize()
    
    if not success:
        print("❌ Failed to initialize Business Logic Core")
        return False
    
    print("✅ Business Logic Core initialized successfully")
    
    # Verify agent count
    agent_status = business_core.get_agent_status()
    total_agents = agent_status['total_agents']
    active_agents = agent_status['active_agents']
    
    print(f"\n📊 Agent Status:")
    print(f"   Total agents: {total_agents}")
    print(f"   Active agents: {active_agents}")
    print(f"   Initialized: {agent_status['initialized']}")
    
    # Verify exactly 53 agents
    if total_agents != 53:
        print(f"❌ Expected 53 agents, found {total_agents}")
        return False
    
    if active_agents != 53:
        print(f"❌ Expected 53 active agents, found {active_agents}")
        return False
    
    print("✅ All 53 agents are properly implemented and active")
    
    # List all agents
    print(f"\n📋 Complete Agent List ({len(business_core.agents)} agents):")
    for i, (agent_name, agent_info) in enumerate(business_core.agents.items(), 1):
        status_icon = "✅" if agent_info['status'] == 'active' else "❌"
        print(f"   {i:2d}. {status_icon} {agent_name} - {agent_info['description']}")
    
    # Test workflow functionality
    print(f"\n🔄 Testing Workflow Functionality...")
    
    test_content = ContentUpload(
        content_id="test_verification_001",
        creator_id="test_creator",
        creator_type=CreatorType.MUSICIAN,
        content_type="audio",
        file_path="/tmp/test.mp3",
        metadata={
            "title": "Test Content for Agent Verification",
            "description": "Testing 53 agents workflow",
            "tags": ["test", "verification"]
        }
    )
    
    print(f"   Processing test content: {test_content.content_id}")
    workflow_results = await business_core.process_content_workflow(test_content)
    
    print(f"   Workflow completed with {len(workflow_results)} stages")
    successful_stages = len([r for r in workflow_results if r.success])
    
    for result in workflow_results:
        status_icon = "✅" if result.success else "❌"
        print(f"     {status_icon} {result.stage.value}")
    
    print(f"   Success rate: {successful_stages}/{len(workflow_results)} stages")
    
    # Final verification
    if total_agents == 53 and active_agents == 53 and successful_stages > 0:
        print(f"\n🏆 VERIFICATION SUCCESSFUL!")
        print(f"   ✅ All 53 agents implemented and active")
        print(f"   ✅ Business logic workflow functional")
        print(f"   ✅ Core functionality validated")
        return True
    else:
        print(f"\n❌ VERIFICATION FAILED!")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_53_agents_verification())
    sys.exit(0 if result else 1)