#!/usr/bin/env python3
"""
Simple test script to validate global compliance implementation
"""
import asyncio
import sys
from datetime import datetime
from typing import Dict, Any

# Add current directory to path to import local modules
sys.path.append('.')

def test_compliance_imports():
    """Test that all compliance modules can be imported"""
    try:
        from data_management.governance.compliance import (
            ComplianceFramework, 
            ComplianceManager,
            PIPEDACompliance,
            LGPDCompliance, 
            PDPACompliance
        )
        print("✅ All compliance modules imported successfully")
        
        # Test framework enum
        frameworks = [f.value for f in ComplianceFramework]
        expected_frameworks = ['gdpr', 'ccpa', 'dmca', 'pipeda', 'lgpd', 'pdpa']
        
        for framework in expected_frameworks:
            if framework in frameworks:
                print(f"✅ {framework.upper()} framework available")
            else:
                print(f"❌ {framework.upper()} framework missing")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

async def test_compliance_manager():
    """Test compliance manager initialization"""
    try:
        from data_management.governance.compliance import ComplianceManager, ComplianceFramework
        
        manager = ComplianceManager()
        print("✅ ComplianceManager initialized successfully")
        
        # Check that all expected checkers are available
        expected_checkers = [
            ComplianceFramework.GDPR,
            ComplianceFramework.CCPA, 
            ComplianceFramework.DMCA,
            ComplianceFramework.PIPEDA,
            ComplianceFramework.LGPD,
            ComplianceFramework.PDPA
        ]
        
        for framework in expected_checkers:
            if framework in manager.checkers:
                print(f"✅ {framework.value.upper()} checker available")
            else:
                print(f"❌ {framework.value.upper()} checker missing")
        
        return True
    except Exception as e:
        print(f"❌ ComplianceManager error: {e}")
        return False

async def test_individual_compliance_checkers():
    """Test individual compliance checker instantiation"""
    try:
        from data_management.governance.compliance import (
            PIPEDACompliance,
            LGPDCompliance,
            PDPACompliance
        )
        
        # Test PIPEDA compliance
        pipeda = PIPEDACompliance()
        framework_info = pipeda.get_framework_info()
        print(f"✅ PIPEDA compliance checker: {framework_info['name']} ({framework_info['jurisdiction']})")
        
        # Test LGPD compliance
        lgpd = LGPDCompliance()
        framework_info = lgpd.get_framework_info()
        print(f"✅ LGPD compliance checker: {framework_info['name']} ({framework_info['jurisdiction']})")
        
        # Test PDPA compliance
        pdpa = PDPACompliance()
        framework_info = pdpa.get_framework_info()
        print(f"✅ PDPA compliance checker: {framework_info['name']} ({framework_info['jurisdiction']})")
        
        return True
    except Exception as e:
        print(f"❌ Individual compliance checker error: {e}")
        return False

async def test_compliance_assessment():
    """Test basic compliance assessment"""
    try:
        from data_management.governance.compliance import PIPEDACompliance, LGPDCompliance, PDPACompliance
        
        # Test data
        test_metadata = {
            "consent": {
                "explicit_consent": True,
                "purpose_specified": True,
                "consent_obtained": True,
                "specific_consent": True,
                "withdrawal_mechanism": True
            },
            "collection": {
                "necessary_for_purpose": True
            },
            "individual_access": {
                "access_mechanism_available": True
            },
            "retention": {
                "retention_policy_defined": True
            },
            "data_subject_rights": {
                "access_implemented": True,
                "rectification_implemented": True,
                "deletion_implemented": True,
                "portability_implemented": True,
                "objection_implemented": True
            },
            "legal_basis": {
                "basis_identified": True
            },
            "dpo": {
                "dpo_designated": True
            },
            "notification": {
                "purpose_notified": True
            },
            "access": {
                "access_mechanism": True
            },
            "protection": {
                "reasonable_security": True
            }
        }
        
        # Test PIPEDA assessment
        pipeda = PIPEDACompliance()
        pipeda_report = await pipeda.assess_compliance("test_content_1", "user_data", test_metadata)
        print(f"✅ PIPEDA assessment: Score {pipeda_report.score:.1f}, Status {pipeda_report.status.value}")
        
        # Test LGPD assessment
        lgpd = LGPDCompliance()
        lgpd_report = await lgpd.assess_compliance("test_content_2", "user_data", test_metadata)
        print(f"✅ LGPD assessment: Score {lgpd_report.score:.1f}, Status {lgpd_report.status.value}")
        
        # Test PDPA assessment
        pdpa = PDPACompliance()
        pdpa_report = await pdpa.assess_compliance("test_content_3", "user_data", test_metadata)
        print(f"✅ PDPA assessment: Score {pdpa_report.score:.1f}, Status {pdpa_report.status.value}")
        
        return True
    except Exception as e:
        print(f"❌ Compliance assessment error: {e}")
        return False

async def main():
    """Main test function"""
    print("🔍 Testing Global Legal Compliance Implementation")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_compliance_imports),
        ("Compliance Manager Test", test_compliance_manager),
        ("Individual Checkers Test", test_individual_compliance_checkers),
        ("Assessment Test", test_compliance_assessment)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All global compliance tests passed!")
        return True
    else:
        print("⚠️  Some compliance tests failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)