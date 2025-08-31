#!/usr/bin/env python3
"""
Validation Test for Protection Agent Module
Tests imports and basic functionality to ensure everything works

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: Proprietary - All rights reserved
WARNING: Unauthorized use, copying, or distribution prohibited
"""

import sys
import traceback

def test_imports():
    """Test all imports from the protection agent module"""
    print(" Testing Protection Agent imports...")
    
    try:
        # Test main module import
        from . import __version__, __author__, __email__
        print(f" Module metadata: v{__version__} by {__author__}")
        
        # Test main classes import
        from . import (
            ProtectionAgent,
            ProtectionAgentIndex,
            AdvancedContentAnalyzer,
            AdvancedCopyrightManager,
            AdvancedRightsManager,
            AdvancedWatermarkingEngine,
            ProtectionManager
        )
        print(" Core classes imported successfully")
        
        # Test utility functions
        from . import (
            get_protection_index,
            protect_content,
            get_status,
            get_metrics
        )
        print(" Utility functions imported successfully")
        
        # Test data structures
        from . import (
            ContentFingerprint,
            CopyrightClaim,
            DMCANotice,
            RightsBundle,
            License,
            MonetizationRule,
            WatermarkConfig,
            DigitalSignature,
            ProtectionRequest,
            MonitoringAlert
        )
        print(" Data structures imported successfully")
        
        # Test enums
        from . import (
            ProtectionLevel,
            ViolationType,
            RightType,
            LicenseType,
            UsageType,
            BatchOperationType
        )
        print(" Enums imported successfully")
        
        return True
        
    except Exception as e:
        print(f" Import test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("\n Testing basic functionality...")
    
    try:
        from . import ProtectionAgentIndex, get_protection_index
        
        # Test singleton pattern
        index1 = get_protection_index()
        index2 = get_protection_index()
        
        if index1 is index2:
            print(" Singleton pattern working correctly")
        else:
            print(" Singleton pattern failed")
            return False
        
        # Test configuration
        config = {
            'protection_level': 'enterprise',
            'monitoring': {'real_time': True}
        }
        
        index = ProtectionAgentIndex(config)
        if index.config == config:
            print(" Configuration initialization working")
        else:
            print(" Configuration initialization failed")
            return False
        
        # Test metrics
        metrics = index.get_performance_metrics()
        required_keys = ['timestamp', 'metrics', 'service_health', 'uptime_info']
        
        if all(key in metrics for key in required_keys):
            print(" Performance metrics working correctly")
        else:
            print(" Performance metrics missing keys")
            return False
        
        return True
        
    except Exception as e:
        print(f" Functionality test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_class_instantiation():
    """Test that main classes can be instantiated"""
    print("\n Testing class instantiation...")
    
    try:
        from . import (
            AdvancedContentAnalyzer,
            AdvancedCopyrightManager,
            AdvancedRightsManager,
            AdvancedWatermarkingEngine,
            ProtectionManager,
            ProtectionAgent
        )
        
        # Test basic instantiation (without external dependencies)
        config = {}
        
        analyzer = AdvancedContentAnalyzer()
        print(" AdvancedContentAnalyzer instantiated")
        
        copyright_mgr = AdvancedCopyrightManager(config)
        print(" AdvancedCopyrightManager instantiated")
        
        rights_mgr = AdvancedRightsManager(config)
        print(" AdvancedRightsManager instantiated")
        
        watermark_engine = AdvancedWatermarkingEngine(config)
        print(" AdvancedWatermarkingEngine instantiated")
        
        protection_mgr = ProtectionManager(config)
        print(" ProtectionManager instantiated")
        
        protection_agent = ProtectionAgent(config)
        print(" ProtectionAgent instantiated")
        
        return True
        
    except Exception as e:
        print(f" Class instantiation test failed: {str(e)}")
        traceback.print_exc()
        return False

def validate_module():
    """Run complete module validation"""
    print(" Starting Protection Agent Module Validation")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Basic Functionality Test", test_basic_functionality),
        ("Class Instantiation Test", test_class_instantiation)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n Running {test_name}...")
        results[test_name] = test_func()
    
    print("\n" + "=" * 60)
    print(" VALIDATION RESULTS")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = " PASSED" if passed else " FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n ALL TESTS PASSED - Module is ready for production!")
        print(" Protection Agent is fully operational")
    else:
        print("\n SOME TESTS FAILED - Please check the issues above")
        return False
    
    return True

if __name__ == "__main__":
    success = validate_module()
    sys.exit(0 if success else 1)
