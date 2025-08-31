"""
Orchestration Module Validation Script

Simple validation script to verify that all orchestration modules can be imported
correctly and that the basic structure is functional.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL WARNING:
This code is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import sys
import traceback
from typing import List, Dict, Any


def validate_orchestration_imports() -> Dict[str, Any]:
    """Validate that all orchestration modules can be imported."""
    results = {
        "success": [],
        "failed": [],
        "summary": {}
    }
    
    # List of modules to validate
    modules_to_test = [
        "backend.core.orchestration.workflow_engine",
        "backend.core.orchestration.pipeline_coordinator", 
        "backend.core.orchestration.task_scheduler",
        "backend.core.orchestration.resource_manager",
        "backend.core.orchestration.execution_engine",
        "backend.core.orchestration.state_manager",
        "backend.core.orchestration.dependency_resolver",
        "backend.core.orchestration.event_coordinator",
        "backend.core.orchestration.performance_optimizer",
        "backend.core.orchestration.error_handler",
        "backend.core.orchestration.metrics_collector",
        "backend.core.orchestration.configuration_manager",
        "backend.core.orchestration.workflow_factory",
        "backend.core.orchestration.pipeline_builder",
        "backend.core.orchestration.orchestration_controller",
        "backend.core.orchestration.index"
    ]
    
    print(" Validating Orchestration Module Imports...")
    print("=" * 60)
    
    for module_name in modules_to_test:
        try:
            print(f"Testing import: {module_name}")
            __import__(module_name)
            results["success"].append(module_name)
            print(f" SUCCESS: {module_name}")
            
        except Exception as e:
            error_info = {
                "module": module_name,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            results["failed"].append(error_info)
            print(f" FAILED: {module_name} - {str(e)}")
    
    # Test main module import
    try:
        print(f"\nTesting main module import...")
        import backend.core.orchestration
        results["success"].append("backend.core.orchestration")
        print(f" SUCCESS: backend.core.orchestration")
        
        # Test __all__ exports
        if hasattr(backend.core.orchestration, '__all__'):
            print(f" Available exports: {len(backend.core.orchestration.__all__)} items")
            for export in backend.core.orchestration.__all__:
                if hasattr(backend.core.orchestration, export):
                    print(f"   {export}")
                else:
                    print(f"   {export} (missing)")
        
    except Exception as e:
        error_info = {
            "module": "backend.core.orchestration",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        results["failed"].append(error_info)
        print(f" FAILED: backend.core.orchestration - {str(e)}")
    
    # Generate summary
    total_modules = len(modules_to_test) + 1  # +1 for main module
    success_count = len(results["success"])
    failed_count = len(results["failed"])
    
    results["summary"] = {
        "total_modules": total_modules,
        "successful_imports": success_count,
        "failed_imports": failed_count,
        "success_rate": (success_count / total_modules) * 100
    }
    
    print("\n" + "=" * 60)
    print(" VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total modules tested: {total_modules}")
    print(f"Successful imports: {success_count}")
    print(f"Failed imports: {failed_count}")
    print(f"Success rate: {results['summary']['success_rate']:.1f}%")
    
    if failed_count == 0:
        print("\n ALL MODULES IMPORTED SUCCESSFULLY!")
        print(" Orchestration module structure is valid and functional")
    else:
        print(f"\n  {failed_count} MODULES FAILED TO IMPORT")
        print(" Please check the failed modules and fix import issues")
        
        print("\n FAILED MODULES DETAILS:")
        for failure in results["failed"]:
            print(f"\n Module: {failure['module']}")
            print(f"   Error: {failure['error']}")
    
    return results


def validate_orchestration_structure():
    """Validate the overall orchestration module structure."""
    print("\n  VALIDATING ORCHESTRATION STRUCTURE...")
    print("=" * 60)
    
    try:
        from backend.core.orchestration import (
            OrchestrationSystem,
            OrchestrationSystemConfig,
            initialize_orchestration_system,
            get_orchestration_system,
            shutdown_orchestration_system
        )
        
        print(" Main orchestration classes imported successfully")
        
        # Test configuration creation
        config = OrchestrationSystemConfig()
        print(" OrchestrationSystemConfig creation successful")
        
        print(" Orchestration structure validation passed")
        return True
        
    except Exception as e:
        print(f" Orchestration structure validation failed: {str(e)}")
        print(f"   Full error: {traceback.format_exc()}")
        return False


def validate_pipeline_templates():
    """Validate pipeline template functionality."""
    print("\n VALIDATING PIPELINE TEMPLATES...")
    print("=" * 60)
    
    try:
        from backend.core.orchestration.pipeline_builder import PipelineBuilder
        
        builder = PipelineBuilder()
        
        # Check default templates
        templates = builder.list_templates()
        print(f" Available pipeline templates: {len(templates)}")
        for template in templates:
            print(f"   {template}")
        
        if len(templates) >= 3:  # Expecting at least 3 default templates
            print(" Pipeline templates validation passed")
            return True
        else:
            print("  Expected at least 3 default templates")
            return False
            
    except Exception as e:
        print(f" Pipeline templates validation failed: {str(e)}")
        return False


def main():
    """Run all validation tests."""
    print(" IA INFLUENCER AGENT - ORCHESTRATION MODULE VALIDATION")
    print("=" * 80)
    print("Author: Fahed Mlaiel <mlaiel@live.de>")
    print("Copyright (c) 2025 Fahed Mlaiel. All rights reserved.")
    print("=" * 80)
    
    # Run validation tests
    import_results = validate_orchestration_imports()
    structure_valid = validate_orchestration_structure()
    templates_valid = validate_pipeline_templates()
    
    # Final summary
    print("\n" + "=" * 80)
    print(" FINAL VALIDATION RESULTS")
    print("=" * 80)
    
    all_passed = (
        import_results["summary"]["failed_imports"] == 0 and
        structure_valid and
        templates_valid
    )
    
    if all_passed:
        print(" ALL VALIDATIONS PASSED!")
        print(" Orchestration module is fully functional and ready for use")
        print(" All imports successful")
        print(" Structure validation passed")
        print(" Pipeline templates functional")
        return 0
    else:
        print("  SOME VALIDATIONS FAILED")
        print(" Please review and fix the issues above")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
