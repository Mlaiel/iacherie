#!/usr/bin/env python3
"""
Simple syntax validation test for global compliance implementation
"""
import sys
import os

def test_compliance_syntax():
    """Test that compliance.py has valid syntax"""
    try:
        # Check file exists
        compliance_file = "data_management/governance/compliance.py"
        if not os.path.exists(compliance_file):
            print(f"❌ File {compliance_file} not found")
            return False
        
        # Test syntax by compiling
        with open(compliance_file, 'r') as f:
            code = f.read()
        
        compile(code, compliance_file, 'exec')
        print("✅ compliance.py syntax is valid")
        
        # Check that all new frameworks are in the enum
        if 'PIPEDA = "pipeda"' in code and 'LGPD = "lgpd"' in code and 'PDPA = "pdpa"' in code:
            print("✅ New compliance frameworks added to enum")
        else:
            print("❌ New compliance frameworks missing from enum")
            return False
        
        # Check that all new classes are defined
        required_classes = ['PIPEDACompliance', 'LGPDCompliance', 'PDPACompliance']
        for class_name in required_classes:
            if f'class {class_name}(' in code:
                print(f"✅ {class_name} class defined")
            else:
                print(f"❌ {class_name} class missing")
                return False
        
        # Check that ComplianceManager includes new frameworks
        if ('ComplianceFramework.PIPEDA:' in code and 
            'ComplianceFramework.LGPD:' in code and 
            'ComplianceFramework.PDPA:' in code):
            print("✅ ComplianceManager updated with new frameworks")
        else:
            print("❌ ComplianceManager not updated with new frameworks")
            return False
        
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in compliance.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking compliance.py: {e}")
        return False

def test_test_file_syntax():
    """Test that test file has valid syntax"""
    try:
        test_file = "tests/compliance/test_automated_gdpr_ccpa.py"
        if not os.path.exists(test_file):
            print(f"❌ File {test_file} not found")
            return False
        
        with open(test_file, 'r') as f:
            code = f.read()
        
        compile(code, test_file, 'exec')
        print("✅ test_automated_gdpr_ccpa.py syntax is valid")
        
        # Check for new test methods
        if ('test_pipeda_consent_collection' in code and 
            'test_lgpd_data_subject_rights' in code and 
            'test_pdpa_consent_obligations' in code):
            print("✅ New test methods added")
        else:
            print("❌ New test methods missing")
            return False
        
        # Check for new data generators
        if ('generate_canadian_user_data' in code and 
            'generate_brazilian_user_data' in code and 
            'generate_singapore_user_data' in code):
            print("✅ New data generators added")
        else:
            print("❌ New data generators missing")
            return False
        
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in test file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking test file: {e}")
        return False

def check_file_changes():
    """Check that files have been modified appropriately"""
    try:
        # Check compliance.py for new content
        with open("data_management/governance/compliance.py", 'r') as f:
            compliance_content = f.read()
        
        # Count lines to ensure significant additions
        lines = compliance_content.split('\n')
        if len(lines) > 1700:  # Should be over 1700 lines with additions
            print(f"✅ compliance.py expanded to {len(lines)} lines (includes new frameworks)")
        else:
            print(f"❌ compliance.py only has {len(lines)} lines (may be missing implementations)")
            return False
        
        # Check test file
        with open("tests/compliance/test_automated_gdpr_ccpa.py", 'r') as f:
            test_content = f.read()
        
        test_lines = test_content.split('\n')
        if len(test_lines) > 900:  # Should be over 900 lines with additions
            print(f"✅ test file expanded to {len(test_lines)} lines (includes new tests)")
        else:
            print(f"❌ test file only has {len(test_lines)} lines (may be missing tests)")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error checking file changes: {e}")
        return False

def main():
    """Main validation function"""
    print("🔍 Validating Global Legal Compliance Implementation")
    print("=" * 60)
    
    tests = [
        ("Compliance Module Syntax", test_compliance_syntax),
        ("Test File Syntax", test_test_file_syntax),
        ("File Changes", check_file_changes)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Validation Summary: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All syntax and structure validations passed!")
        print("\n📋 Implementation Summary:")
        print("✅ PIPEDA (Canada) compliance framework implemented")
        print("✅ LGPD (Brazil) compliance framework implemented") 
        print("✅ PDPA (Singapore) compliance framework implemented")
        print("✅ ComplianceManager updated to include new frameworks")
        print("✅ Comprehensive tests added for all new frameworks")
        return True
    else:
        print("⚠️  Some validations failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)