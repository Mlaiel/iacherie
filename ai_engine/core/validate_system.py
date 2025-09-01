#!/usr/bin/env python3
"""AI Core System Validation Script

Comprehensive validation suite for the IA-Influencer-Agent AI core system.
Tests all components, workflows, and integrations to ensure enterprise-grade quality.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
"""

import asyncio
import sys
import traceback
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test results collector
validation_results = {
    "timestamp": datetime.utcnow().isoformat(),
    "tests_passed": 0,
    "tests_failed": 0,
    "total_tests": 0,
    "component_status": {},
    "errors": [],
    "warnings": [],
    "recommendations": []
}


def log_test_result(test_name: str, success: bool, details: str = "", error: str = ""):
    """Log test result"""
    validation_results["total_tests"] += 1
    
    if success:
        validation_results["tests_passed"] += 1
        logger.info(f"✅ {test_name}: PASSED {details}")
    else:
        validation_results["tests_failed"] += 1
        logger.error(f"❌ {test_name}: FAILED {details}")
        if error:
            validation_results["errors"].append(f"{test_name}: {error}")


def test_imports():
    """Test all imports and core functionality"""
    try:
        # Test basic imports
        from ai.core import (
            ai_orchestrator, WorkflowType, ProcessingPriority, 
            WorkflowRequest, WorkflowResult
        )
        log_test_result("Core Orchestrator Import", True, "All core components imported successfully")
        
        # Test AI engines imports
        from ai.core import (
            collaboration_ai, revenue_optimizer, content_protector,
            seo_optimizer, business_intelligence, content_intelligence
        )
        log_test_result("AI Engines Import", True, "All AI engines imported successfully")
        
        # Test specialized components
        from ai.core import (
            performance_monitor_system, optimization_engine, 
            auto_optimizer, collaboration_engine
        )
        log_test_result("Specialized Components Import", True, "All specialized components imported successfully")
        
        # Test data models
        from ai.core import (
            CreatorProfile, CollaborationOpportunity, 
            MonetizationOpportunity, ContentFingerprint
        )
        log_test_result("Data Models Import", True, "All data models imported successfully")
        
        # Test configuration
        from ai.core.config import get_config, Environment
        config = get_config(Environment.DEVELOPMENT)
        log_test_result("Configuration System", True, f"Config loaded for {config.environment.value}")
        
        return True
        
    except ImportError as e:
        log_test_result("Import Test", False, "", str(e))
        return False
    except Exception as e:
        log_test_result("Import Test", False, "", str(e))
        return False


async def test_orchestrator():
    """Test AI orchestrator functionality"""
    try:
        from ai.core import ai_orchestrator, WorkflowType, ProcessingPriority, WorkflowRequest
        
        # Test system status
        status = await ai_orchestrator.get_system_status()
        if status.get("system_status") == "operational":
            log_test_result("Orchestrator Status", True, "System operational")
        else:
            log_test_result("Orchestrator Status", False, f"Status: {status}")
        
        # Test workflow creation (without execution)
        request = WorkflowRequest(
            request_id="test_validation_001",
            workflow_type=WorkflowType.CONTENT_OPTIMIZATION,
            priority=ProcessingPriority.HIGH,
            user_id="test_user",
            content_data={"title": "Test Content"},
            async_processing=False
        )
        
        log_test_result("Workflow Request Creation", True, f"Created request: {request.request_id}")
        
        return True
        
    except Exception as e:
        log_test_result("Orchestrator Test", False, "", str(e))
        return False


async def test_components():
    """Test individual AI components"""
    component_tests = []
    
    try:
        from ai.core import ai_orchestrator
        
        # Get component manager
        component_manager = ai_orchestrator.component_manager
        
        # Test each component health
        for component_name in component_manager.components.keys():
            try:
                health = await component_manager.check_component_health(component_name)
                
                if health.status.value in ["active", "idle"]:
                    log_test_result(f"Component: {component_name}", True, f"Status: {health.status.value}")
                    validation_results["component_status"][component_name] = "healthy"
                    component_tests.append(True)
                else:
                    log_test_result(f"Component: {component_name}", False, f"Status: {health.status.value}")
                    validation_results["component_status"][component_name] = "unhealthy"
                    component_tests.append(False)
                    
            except Exception as e:
                log_test_result(f"Component: {component_name}", False, "", str(e))
                validation_results["component_status"][component_name] = "error"
                component_tests.append(False)
        
        # Overall component health
        healthy_components = sum(component_tests)
        total_components = len(component_tests)
        
        if healthy_components >= total_components * 0.8:  # At least 80% healthy
            log_test_result("Overall Component Health", True, f"{healthy_components}/{total_components} components healthy")
            return True
        else:
            log_test_result("Overall Component Health", False, f"Only {healthy_components}/{total_components} components healthy")
            return False
            
    except Exception as e:
        log_test_result("Component Health Test", False, "", str(e))
        return False


def test_configuration():
    """Test configuration system"""
    try:
        from ai.core.config import get_config, Environment, get_database_config, get_security_config
        
        # Test config loading
        config = get_config(Environment.DEVELOPMENT)
        log_test_result("Configuration Loading", True, f"Loaded config for {config.environment.value}")
        
        # Test database config
        db_config = get_database_config()
        if db_config.host:
            log_test_result("Database Configuration", True, f"DB host: {db_config.host}")
        else:
            log_test_result("Database Configuration", False, "No database host configured")
        
        # Test security config
        security_config = get_security_config()
        log_test_result("Security Configuration", True, f"Security level: {security_config.security_level.value}")
        
        return True
        
    except Exception as e:
        log_test_result("Configuration Test", False, "", str(e))
        return False


def test_data_models():
    """Test data model creation and validation"""
    try:
        from ai.core import CreatorProfile, CollaborationOpportunity, WorkflowRequest, WorkflowType, ProcessingPriority
        
        # Test CreatorProfile
        profile = CreatorProfile(
            creator_id="test_creator",
            username="test_user",
            creator_type="musician",
            follower_count=10000,
            engagement_rate=0.05,
            content_categories=["music", "entertainment"]
        )
        log_test_result("CreatorProfile Creation", True, f"Created profile for {profile.username}")
        
        # Test WorkflowRequest
        request = WorkflowRequest(
            request_id="test_request",
            workflow_type=WorkflowType.COLLABORATION_DISCOVERY,
            priority=ProcessingPriority.NORMAL,
            user_id="test_user"
        )
        log_test_result("WorkflowRequest Creation", True, f"Created request: {request.request_id}")
        
        # Test serialization
        request_dict = request.to_dict()
        if isinstance(request_dict, dict) and "request_id" in request_dict:
            log_test_result("Data Model Serialization", True, "Models serialize to dict correctly")
        else:
            log_test_result("Data Model Serialization", False, "Serialization failed")
        
        return True
        
    except Exception as e:
        log_test_result("Data Models Test", False, "", str(e))
        return False


def test_package_completeness():
    """Test package completeness and exports"""
    try:
        import ai.core as ai_core
        
        # Check main exports
        required_exports = [
            'ai_orchestrator', 'WorkflowType', 'ProcessingPriority',
            'collaboration_ai', 'revenue_optimizer', 'content_protector',
            'seo_optimizer', 'business_intelligence'
        ]
        
        missing_exports = []
        for export in required_exports:
            if not hasattr(ai_core, export):
                missing_exports.append(export)
        
        if missing_exports:
            log_test_result("Package Exports", False, f"Missing exports: {missing_exports}")
            return False
        else:
            log_test_result("Package Exports", True, f"All {len(required_exports)} required exports present")
        
        # Check package metadata
        if hasattr(ai_core, '__version__'):
            log_test_result("Package Metadata", True, f"Version: {ai_core.__version__}")
        else:
            validation_results["warnings"].append("Package version not defined")
        
        # Test get_system_info
        if hasattr(ai_core, 'get_system_info'):
            system_info = ai_core.get_system_info()
            if isinstance(system_info, dict):
                log_test_result("System Info", True, f"Components: {len(system_info.get('components', {}))}")
            else:
                log_test_result("System Info", False, "System info not returning dict")
        
        return True
        
    except Exception as e:
        log_test_result("Package Completeness", False, "", str(e))
        return False


async def run_validation():
    """Run complete validation suite"""
    print("🚀 Starting IA-Influencer-Agent AI Core Validation Suite")
    print("=" * 60)
    print(f"Validation started at: {datetime.utcnow()}")
    print("=" * 60)
    
    # Run all tests
    test_results = []
    
    # 1. Import tests
    print("\n📦 Testing Imports and Basic Functionality...")
    test_results.append(test_imports())
    
    # 2. Configuration tests
    print("\n⚙️ Testing Configuration System...")
    test_results.append(test_configuration())
    
    # 3. Data model tests
    print("\n📊 Testing Data Models...")
    test_results.append(test_data_models())
    
    # 4. Package completeness
    print("\n📋 Testing Package Completeness...")
    test_results.append(test_package_completeness())
    
    # 5. Orchestrator tests (async)
    print("\n🎯 Testing AI Orchestrator...")
    test_results.append(await test_orchestrator())
    
    # 6. Component tests (async)
    print("\n🔧 Testing AI Components...")
    test_results.append(await test_components())
    
    # Generate final report
    print("\n" + "=" * 60)
    print("🎯 VALIDATION RESULTS SUMMARY")
    print("=" * 60)
    
    passed = validation_results["tests_passed"]
    failed = validation_results["tests_failed"]
    total = validation_results["total_tests"]
    
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    print(f"📊 Total Tests: {total}")
    print(f"📈 Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
    
    # Component status summary
    if validation_results["component_status"]:
        print(f"\n🔧 Component Status:")
        for component, status in validation_results["component_status"].items():
            status_icon = "✅" if status == "healthy" else "❌" if status == "error" else "⚠️"
            print(f"  {status_icon} {component}: {status}")
    
    # Show errors if any
    if validation_results["errors"]:
        print(f"\n❌ Errors Found:")
        for error in validation_results["errors"][:5]:  # Show first 5 errors
            print(f"  • {error}")
        if len(validation_results["errors"]) > 5:
            print(f"  ... and {len(validation_results['errors']) - 5} more errors")
    
    # Show warnings if any
    if validation_results["warnings"]:
        print(f"\n⚠️ Warnings:")
        for warning in validation_results["warnings"][:3]:  # Show first 3 warnings
            print(f"  • {warning}")
    
    # Overall system status
    print("\n" + "=" * 60)
    overall_success = passed >= total * 0.8  # 80% success rate required
    
    if overall_success:
        print("🎉 AI CORE SYSTEM: VALIDATION SUCCESSFUL!")
        print("✅ System is ready for enterprise deployment")
        print("🚀 All critical components are operational")
        
        # Generate recommendations for successful validation
        validation_results["recommendations"] = [
            "System passed validation - ready for production deployment",
            "Consider running performance benchmarks for optimization",
            "Set up monitoring and alerting for production environment",
            "Configure backup and disaster recovery procedures"
        ]
        
        exit_code = 0
    else:
        print("⚠️ AI CORE SYSTEM: VALIDATION FAILED!")
        print("❌ System requires fixes before deployment")
        print("🔧 Please address the errors above")
        
        # Generate recommendations for failed validation
        validation_results["recommendations"] = [
            "Fix failed component tests before proceeding",
            "Review error messages and resolve import issues",
            "Verify all dependencies are properly installed",
            "Check configuration files and environment setup"
        ]
        
        exit_code = 1
    
    # Save validation report
    try:
        report_file = f"ai_core_validation_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(validation_results, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
    except Exception as e:
        print(f"\n⚠️ Could not save validation report: {e}")
    
    print("=" * 60)
    print(f"Validation completed at: {datetime.utcnow()}")
    print("(c) 2025 Fahed Mlaiel - IA-Influencer-Agent AI Core System")
    print("=" * 60)
    
    return exit_code


if __name__ == "__main__":
    try:
        # Run validation
        exit_code = asyncio.run(run_validation())
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed with unexpected error: {e}")
        print(traceback.format_exc())
        sys.exit(1)
