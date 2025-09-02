#!/usr/bin/env python3
"""Comprehensive Integration Test - Phase 1 Validation
Tests the complete integration of all major systems implemented in Phase 1:
- 53 AI Agents Orchestrator
- Enhanced Business Logic Core  
- Enterprise Monetization Engine

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from datetime import datetime
from decimal import Decimal

# Import our major implementations
from ai_agents_orchestrator import get_orchestrator
from enhanced_business_logic_core import get_enhanced_business_core, ContentUpload, ContentType
from enterprise_monetization_engine import get_monetization_engine, PaymentRequest, PaymentProvider, RevenueStream

logger = logging.getLogger(__name__)

class PhaseOneIntegrationTest:
    """Comprehensive integration test for Phase 1 implementations"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
    
    async def run_comprehensive_test(self):
        """Run complete integration test suite"""
        logger.info("🚀 Starting Phase 1 Comprehensive Integration Test")
        logger.info("=" * 80)
        
        try:
            # Test 1: AI Agents Orchestrator
            await self._test_ai_agents_orchestrator()
            
            # Test 2: Enhanced Business Logic Core
            await self._test_enhanced_business_logic()
            
            # Test 3: Enterprise Monetization Engine
            await self._test_monetization_engine()
            
            # Test 4: End-to-End Integration
            await self._test_end_to_end_integration()
            
            # Generate final report
            await self._generate_test_report()
            
        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")
            raise
    
    async def _test_ai_agents_orchestrator(self):
        """Test the 53 AI Agents Orchestrator"""
        logger.info("🤖 Testing 53 AI Agents Orchestrator...")
        
        try:
            # Initialize orchestrator
            orchestrator = await get_orchestrator()
            
            # Test agent registration
            status = orchestrator.get_all_agents_status()
            assert status["total_agents"] == 53, f"Expected 53 agents, got {status['total_agents']}"
            assert status["initialized"] == True, "Orchestrator not initialized"
            
            # Test category distribution
            assert status["agents_by_category"]["core_business"] == 20, "Wrong core business agent count"
            assert status["agents_by_category"]["specialized_content"] == 15, "Wrong content agent count"
            assert status["agents_by_category"]["technical_support"] == 18, "Wrong technical agent count"
            
            # Test workflows
            workflows = ["content_creation_workflow", "collaboration_workflow", "monetization_workflow", "protection_workflow"]
            for workflow in workflows:
                result = await orchestrator.execute_workflow(workflow, {"test": True})
                assert result is not None, f"Workflow {workflow} failed"
            
            self.test_results["ai_agents_orchestrator"] = {
                "status": "✅ PASSED",
                "agents_count": status["total_agents"],
                "workflows_tested": len(workflows),
                "details": "All 53 agents operational, workflows functional"
            }
            
            logger.info("✅ AI Agents Orchestrator test PASSED")
            
        except Exception as e:
            self.test_results["ai_agents_orchestrator"] = {
                "status": "❌ FAILED", 
                "error": str(e)
            }
            logger.error(f"❌ AI Agents Orchestrator test failed: {e}")
            raise
    
    async def _test_enhanced_business_logic(self):
        """Test the Enhanced Business Logic Core"""
        logger.info("🏢 Testing Enhanced Business Logic Core...")
        
        try:
            # Initialize business core
            core = await get_enhanced_business_core()
            
            # Test initialization
            assert core.initialized == True, "Business core not initialized"
            assert core.orchestrator is not None, "AI orchestrator not connected"
            
            # Test workflow configuration
            assert len(core.workflows) >= 3, "Insufficient workflows configured"
            assert "complete_content_workflow" in core.workflows, "Missing complete workflow"
            
            # Test business rules
            assert core.business_rules["monetization"]["enabled"] == True, "Monetization not enabled"
            assert core.business_rules["protection"]["enabled"] == True, "Protection not enabled"
            
            # Test content workflow processing
            test_content = ContentUpload(
                content_id="test_content_001",
                creator_id="test_creator_001",
                content_type=ContentType.MUSIC,
                file_path="/test/music.mp3",
                metadata={"title": "Test Track", "genre": "electronic"},
                target_platforms=["youtube", "spotify"],
                monetization_goals=["streaming_revenue"]
            )
            
            workflow_results = await core.process_content_workflow(test_content, "fast_track_workflow")
            assert len(workflow_results) > 0, "No workflow results"
            assert all(result.success for result in workflow_results), "Some workflow stages failed"
            
            # Test business metrics
            metrics = await core.get_business_metrics()
            assert "system_health" in metrics, "Missing system health metrics"
            assert metrics["system_health"]["business_logic_core"] == "healthy", "Business core not healthy"
            
            self.test_results["enhanced_business_logic"] = {
                "status": "✅ PASSED",
                "workflows_configured": len(core.workflows),
                "test_stages_processed": len(workflow_results),
                "details": "Business logic core fully operational with AI integration"
            }
            
            logger.info("✅ Enhanced Business Logic Core test PASSED")
            
        except Exception as e:
            self.test_results["enhanced_business_logic"] = {
                "status": "❌ FAILED",
                "error": str(e)
            }
            logger.error(f"❌ Enhanced Business Logic Core test failed: {e}")
            raise
    
    async def _test_monetization_engine(self):
        """Test the Enterprise Monetization Engine"""
        logger.info("💰 Testing Enterprise Monetization Engine...")
        
        try:
            # Initialize monetization engine
            engine = await get_monetization_engine()
            
            # Test initialization
            assert engine.initialized == True, "Monetization engine not initialized"
            assert len(engine.providers) >= 5, "Insufficient payment providers"
            
            # Test payment providers
            expected_providers = [PaymentProvider.STRIPE, PaymentProvider.PAYPAL, PaymentProvider.WISE]
            for provider in expected_providers:
                assert provider in engine.providers, f"Missing provider: {provider}"
                assert engine.providers[provider]["enabled"] == True, f"Provider {provider} not enabled"
            
            # Test payment processing
            payment_request = PaymentRequest(
                payment_id="test_payment_001",
                creator_id="test_creator_001", 
                amount=Decimal("100.00"),
                currency="USD",
                provider=PaymentProvider.STRIPE,
                revenue_stream=RevenueStream.STREAMING,
                metadata={"test": True}
            )
            
            payment_result = await engine.process_payment(payment_request)
            assert payment_result.status.value == "completed", f"Payment failed: {payment_result.status}"
            assert payment_result.amount_processed == Decimal("100.00"), "Wrong amount processed"
            assert payment_result.net_amount > 0, "No net amount calculated"
            
            # Test revenue optimization
            revenue_data = {
                "current_revenue": 1000,
                "revenue_streams": ["streaming", "downloads"],
                "platforms": ["youtube", "spotify"]
            }
            
            optimization = await engine.optimize_revenue("test_creator_001", revenue_data)
            assert "optimized_strategies" in optimization, "Missing optimization strategies"
            assert "revenue_forecast" in optimization, "Missing revenue forecast"
            
            # Test system metrics
            metrics = await engine.get_system_metrics()
            assert "system_health" in metrics, "Missing system health"
            assert metrics["system_health"]["success_rate"] >= 0, "Invalid success rate"
            
            self.test_results["monetization_engine"] = {
                "status": "✅ PASSED",
                "payment_providers": len(engine.providers),
                "payment_processed": float(payment_result.amount_processed),
                "net_amount": float(payment_result.net_amount),
                "details": "Multi-provider payment processing and revenue optimization functional"
            }
            
            logger.info("✅ Enterprise Monetization Engine test PASSED")
            
        except Exception as e:
            self.test_results["monetization_engine"] = {
                "status": "❌ FAILED",
                "error": str(e)
            }
            logger.error(f"❌ Enterprise Monetization Engine test failed: {e}")
            raise
    
    async def _test_end_to_end_integration(self):
        """Test complete end-to-end integration of all systems"""
        logger.info("🔄 Testing End-to-End Integration...")
        
        try:
            # Initialize all systems
            orchestrator = await get_orchestrator()
            business_core = await get_enhanced_business_core()
            monetization_engine = await get_monetization_engine()
            
            # Test complete content lifecycle
            content = ContentUpload(
                content_id="e2e_test_content",
                creator_id="e2e_test_creator",
                content_type=ContentType.VIDEO,
                file_path="/test/video.mp4",
                metadata={"title": "E2E Test Video", "description": "End-to-end test content"},
                target_platforms=["youtube", "tiktok", "instagram"],
                monetization_goals=["brand_partnerships", "streaming_revenue"],
                collaboration_preferences={"type": "cross_promotion", "requirements": {"min_followers": 1000}}
            )
            
            # Process complete workflow
            workflow_results = await business_core.process_content_workflow(content, "complete_content_workflow")
            
            # Verify all stages completed
            expected_stages = ["content_upload", "content_analysis", "ai_enhancement", "rights_protection", 
                             "seo_optimization", "collaboration_matching", "distribution", "monetization", 
                             "analytics", "optimization"]
            
            completed_stages = [result.stage.value for result in workflow_results if result.success]
            assert len(completed_stages) == len(expected_stages), f"Missing stages: {set(expected_stages) - set(completed_stages)}"
            
            # Test monetization integration
            payment_request = PaymentRequest(
                payment_id="e2e_payment",
                creator_id="e2e_test_creator",
                amount=Decimal("500.00"),
                currency="USD", 
                provider=PaymentProvider.STRIPE,
                revenue_stream=RevenueStream.BRAND_PARTNERSHIPS,
                metadata={"content_id": content.content_id}
            )
            
            payment_result = await monetization_engine.process_payment(payment_request)
            assert payment_result.status.value == "completed", "E2E payment failed"
            
            # Test AI agents utilization
            ai_workflow_result = await orchestrator.execute_workflow("content_creation_workflow", {
                "content_type": content.content_type.value,
                "target_audience": "general",
                "goals": content.monetization_goals
            })
            assert ai_workflow_result is not None, "AI workflow integration failed"
            
            self.test_results["end_to_end_integration"] = {
                "status": "✅ PASSED", 
                "workflow_stages_completed": len(completed_stages),
                "payment_amount": float(payment_result.amount_processed),
                "ai_workflows_executed": 1,
                "details": "Complete system integration functional - upload to monetization"
            }
            
            logger.info("✅ End-to-End Integration test PASSED")
            
        except Exception as e:
            self.test_results["end_to_end_integration"] = {
                "status": "❌ FAILED",
                "error": str(e)
            }
            logger.error(f"❌ End-to-End Integration test failed: {e}")
            raise
    
    async def _generate_test_report(self):
        """Generate comprehensive test report"""
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds()
        
        # Count passed/failed tests
        passed_tests = len([r for r in self.test_results.values() if "✅ PASSED" in r["status"]])
        total_tests = len(self.test_results)
        
        report = {
            "test_execution": {
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_duration_seconds": total_time,
                "tests_passed": passed_tests,
                "tests_total": total_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0
            },
            "system_validation": {
                "ai_agents_system": self.test_results.get("ai_agents_orchestrator", {}).get("status", "❌ NOT TESTED"),
                "business_logic_core": self.test_results.get("enhanced_business_logic", {}).get("status", "❌ NOT TESTED"),
                "monetization_engine": self.test_results.get("monetization_engine", {}).get("status", "❌ NOT TESTED"),
                "end_to_end_integration": self.test_results.get("end_to_end_integration", {}).get("status", "❌ NOT TESTED")
            },
            "detailed_results": self.test_results,
            "overall_status": "✅ ALL SYSTEMS OPERATIONAL" if passed_tests == total_tests else f"⚠️ {total_tests - passed_tests} TESTS FAILED"
        }
        
        logger.info("=" * 80)
        logger.info("📊 PHASE 1 INTEGRATION TEST REPORT")
        logger.info("=" * 80)
        logger.info(f"🕐 Test Duration: {total_time:.2f} seconds")
        logger.info(f"📈 Success Rate: {passed_tests}/{total_tests} ({report['test_execution']['success_rate']:.1%})")
        logger.info(f"🎯 Overall Status: {report['overall_status']}")
        logger.info("")
        
        for test_name, result in self.test_results.items():
            logger.info(f"  {result['status']} {test_name.replace('_', ' ').title()}")
            if "details" in result:
                logger.info(f"    └─ {result['details']}")
        
        logger.info("=" * 80)
        
        # Save detailed report
        with open("PHASE1_INTEGRATION_TEST_REPORT.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info("📄 Detailed report saved to: PHASE1_INTEGRATION_TEST_REPORT.json")
        
        self.final_report = report
        return report

async def main():
    """Run the comprehensive Phase 1 integration test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    test_suite = PhaseOneIntegrationTest()
    await test_suite.run_comprehensive_test()
    report = test_suite.final_report
    
    # Final validation
    if report["test_execution"]["success_rate"] == 1.0:
        logger.info("🎉 PHASE 1 IMPLEMENTATION FULLY VALIDATED!")
        logger.info("🚀 All systems operational and ready for production")
        return 0
    else:
        logger.error("❌ PHASE 1 VALIDATION INCOMPLETE")
        logger.error("⚠️ Some systems require attention before production")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())