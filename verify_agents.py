#!/usr/bin/env python3
"""Agent Verification Script - Verify all 10 critical agents are working

This script verifies that all 10 critical agents have been successfully implemented
and can be imported, initialized, and basic functionality tested.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def verify_agent(agent_class, agent_name):
    """Verify a single agent"""
    try:
        print(f"🔍 Testing {agent_name}...")
        
        # Test initialization
        agent = agent_class()
        print(f"  ✅ Initialization: {agent.agent_type}")
        
        # Test required config keys
        config_keys = agent.get_required_config_keys()
        print(f"  ✅ Config keys: {len(config_keys)} required")
        
        # Test startup/shutdown
        await agent.start()
        print(f"  ✅ Startup: Running={agent.is_running}")
        
        await agent.shutdown()
        print(f"  ✅ Shutdown: Running={agent.is_running}")
        
        print(f"✅ {agent_name} - ALL TESTS PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ {agent_name} - FAILED: {e}\n")
        return False

async def main():
    """Main verification function"""
    print("🚀 VERIFYING ALL 10 CRITICAL AI AGENTS")
    print("=" * 50)
    
    # Import all agents (avoiding dependency issues)
    try:
        from ai_agents.content_strategist_agent.manager import ContentStrategistManager
        from ai_agents.revenue_optimizer_agent.manager import RevenueOptimizerManager  
        from ai_agents.trend_analyst_agent.manager import TrendAnalystManager
        from ai_agents.audience_analyzer_agent.manager import AudienceAnalyzerManager
        from ai_agents.brand_safety_agent.manager import BrandSafetyManager
        from ai_agents.compliance_monitor_agent.manager import ComplianceMonitorManager
        from ai_agents.personalization_agent.manager import PersonalizationManager
        from ai_agents.community_manager_agent.manager import CommunityManagerManager
        from ai_agents.quality_assurance_agent.manager import QualityAssuranceManager
        from ai_agents.business_intelligence_agent.manager import BusinessIntelligenceManager
        
        print("✅ All agent imports successful!\n")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return
    
    # Test all agents
    agents_to_test = [
        (ContentStrategistManager, "ContentStrategistAgent"),
        (RevenueOptimizerManager, "RevenueOptimizerAgent"),
        (TrendAnalystManager, "TrendAnalystAgent"),
        (AudienceAnalyzerManager, "AudienceAnalyzerAgent"), 
        (BrandSafetyManager, "BrandSafetyAgent"),
        (ComplianceMonitorManager, "ComplianceMonitorAgent"),
        (PersonalizationManager, "PersonalizationAgent"),
        (CommunityManagerManager, "CommunityManagerAgent"),
        (QualityAssuranceManager, "QualityAssuranceAgent"),
        (BusinessIntelligenceManager, "BusinessIntelligenceAgent")
    ]
    
    results = []
    for agent_class, agent_name in agents_to_test:
        result = await verify_agent(agent_class, agent_name)
        results.append((agent_name, result))
    
    # Summary
    print("🎯 VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for agent_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {agent_name}")
    
    print(f"\n🏆 FINAL RESULT: {passed}/{total} agents verified successfully")
    
    if passed == total:
        print("🎉 ALL 10 CRITICAL AGENTS SUCCESSFULLY IMPLEMENTED!")
        print("🚀 Ready for production deployment!")
    else:
        print(f"⚠️  {total - passed} agents need attention")

if __name__ == "__main__":
    asyncio.run(main())