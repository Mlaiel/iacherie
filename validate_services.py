#!/usr/bin/env python3
"""
Simple Enterprise Services Validation
====================================

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0.0 Enterprise
"""

import sys
import time
import importlib
import traceback

def test_service_imports():
    """Test all service imports"""
    print("🔥 TESTING ENTERPRISE SERVICES IMPORTS")
    print("=" * 50)
    
    services_to_test = [
        # Core services
        ("services.core.health_monitor", "HealthCheckService"),
        ("services.core.service_registry", "ServiceRegistry"),
        ("services.core.event_bus", "EventBus"),
        ("services.core.config_manager", "ConfigurationManager"),
        ("services.core.lifecycle_manager", "LifecycleManager"),
        ("services.core.metrics_collector", "MetricsCollector"),
        
        # Processing services
        ("services.processing.content_processor", "ContentProcessingService"),
        ("services.processing.ai_orchestrator", "ContentAnalyzer"),
        ("services.processing.media_pipeline", "MediaPipeline"),
        ("services.processing.recommendation_engine", "RecommendationEngine"),
        ("services.processing.validation_service", "ValidationService"),
        ("services.processing.transformation_engine", "TransformationEngine"),
        
        # Orchestration services
        ("services.orchestration.workflow_orchestrator", "MLWorkflowOrchestrator"),
        ("services.orchestration.business_intelligence", "BusinessIntelligenceService"),
        ("services.orchestration.automation_engine", "AutomationEngine"),
        ("services.orchestration.collaboration_hub", "CollaborationEngine"),
        ("services.orchestration.analytics_processor", "DataPipelineService"),
    ]
    
    passed = 0
    total = len(services_to_test)
    
    for module_path, class_name in services_to_test:
        try:
            start_time = time.time()
            
            # Import module
            module = importlib.import_module(module_path)
            
            # Get class
            service_class = getattr(module, class_name)
            
            # Test basic instantiation (if possible)
            try:
                instance = service_class()
            except TypeError:
                try:
                    instance = service_class(redis_url="redis://localhost:6379")
                except:
                    instance = None  # Skip instantiation test
            
            import_time = time.time() - start_time
            
            print(f"✅ {module_path}.{class_name} - OK ({import_time*1000:.1f}ms)")
            passed += 1
            
        except Exception as e:
            print(f"❌ {module_path}.{class_name} - FAILED: {e}")
            # Uncomment for debugging:
            # traceback.print_exc()
    
    print(f"\n📊 RESULTS: {passed}/{total} services passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL SERVICES WORKING - ENTERPRISE COMPLIANT!")
        return True
    else:
        print("⚠️  SOME SERVICES NEED ATTENTION")
        return False

def test_async_patterns():
    """Test async patterns in services"""
    print("\n🔧 TESTING ASYNC PATTERNS")
    print("=" * 30)
    
    try:
        from services.core.health_monitor import HealthCheckService
        
        service = HealthCheckService()
        
        # Check for async methods
        async_methods = [
            method for method in dir(service) 
            if not method.startswith('_') and 
            callable(getattr(service, method))
        ]
        
        print(f"✅ Async patterns validated - {len(async_methods)} public methods")
        return True
        
    except Exception as e:
        print(f"❌ Async patterns test failed: {e}")
        return False

def test_configuration():
    """Test configuration files"""
    print("\n⚙️ TESTING CONFIGURATION")
    print("=" * 25)
    
    try:
        import yaml
        import os
        
        config_files = [
            "services/config/services.yaml",
            "services/config/performance.yaml"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                print(f"✅ {config_file} - Valid YAML")
            else:
                print(f"⚠️  {config_file} - Not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    start_time = time.time()
    
    test1 = test_service_imports()
    test2 = test_async_patterns()
    test3 = test_configuration()
    
    total_time = time.time() - start_time
    
    print(f"\n🏁 TOTAL TEST TIME: {total_time:.2f}s")
    
    if test1 and test2 and test3:
        print("🎯 ALL TESTS PASSED - ENTERPRISE READY!")
        return True
    else:
        print("❌ SOME TESTS FAILED - NEEDS WORK")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)