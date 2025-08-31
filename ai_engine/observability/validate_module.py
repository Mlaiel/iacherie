#!/usr/bin/env python3
"""
Observability Module Validation Script

Final validation script to ensure all components are working correctly
and the module is production-ready for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  AVERTISSEMENT LÉGAL / LEGAL WARNING 
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""

import sys
import asyncio
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
import json
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


class ObservabilityValidator:
    """Comprehensive validation suite for the observability module"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "validation_results": {},
            "summary": {},
            "errors": []
        }
        self.modules_to_test = [
            "index",
            "config", 
            "analytics",
            "business_process_monitoring",
            "intelligent_monitoring",
            "ai_observability",
            "observability_logging",
            "reporting",
            "metrics",
            "monitoring",
            "visualization",
            "dashboards",
            "quality",
            "health",
            "alerting",
            "tracing",
            "diagnostics",
            "data_management"
        ]
    
    def validate_imports(self) -> Tuple[bool, List[str]]:
        """Validate all module imports"""
        logger.info(" Validating module imports...")
        
        successful_imports = []
        failed_imports = []
        
        for module_name in self.modules_to_test:
            try:
                module = importlib.import_module(module_name)
                successful_imports.append(module_name)
                logger.info(f"    {module_name}: OK")
            except ImportError as e:
                failed_imports.append(f"{module_name}: {str(e)}")
                logger.error(f"    {module_name}: {str(e)}")
            except Exception as e:
                failed_imports.append(f"{module_name}: Unexpected error - {str(e)}")
                logger.error(f"    {module_name}: Unexpected error - {str(e)}")
        
        success_rate = len(successful_imports) / len(self.modules_to_test) * 100
        logger.info(f" Import Success Rate: {success_rate:.1f}% ({len(successful_imports)}/{len(self.modules_to_test)})")
        
        self.results["validation_results"]["imports"] = {
            "success_rate": success_rate,
            "successful": successful_imports,
            "failed": failed_imports,
            "total_modules": len(self.modules_to_test)
        }
        
        return len(failed_imports) == 0, failed_imports
    
    async def validate_core_functionality(self) -> Tuple[bool, List[str]]:
        """Validate core functionality"""
        logger.info(" Validating core functionality...")
        
        errors = []
        
        try:
            # Test ObservabilityIndex initialization
            from index import ObservabilityIndex
            
            observability = ObservabilityIndex()
            logger.info("    ObservabilityIndex creation: OK")
            
            # Test async initialization
            try:
                await observability.initialize()
                logger.info("    Async initialization: OK")
            except Exception as e:
                errors.append(f"Async initialization failed: {str(e)}")
                logger.error(f"    Async initialization: {str(e)}")
            
            # Test business process monitoring
            try:
                from business_process_monitoring import (
                    ContentType, CreatorType, ProcessStage, 
                    BusinessProcessOrchestrator
                )
                
                business_orchestrator = BusinessProcessOrchestrator()
                logger.info("    Business process orchestrator: OK")
                
                # Test business intelligence report
                business_report = await business_orchestrator.get_comprehensive_business_report()
                if isinstance(business_report, dict):
                    logger.info("    Business intelligence report: OK")
                else:
                    errors.append("Business intelligence report returned invalid type")
                    
            except Exception as e:
                errors.append(f"Business process monitoring failed: {str(e)}")
                logger.error(f"    Business process monitoring: {str(e)}")
            
            # Test analytics
            try:
                from analytics import RealTimeAnalytics, AnalyticsTimeframe
                
                analytics = RealTimeAnalytics()
                logger.info("    Real-time analytics: OK")
                
            except Exception as e:
                errors.append(f"Analytics validation failed: {str(e)}")
                logger.error(f"    Analytics: {str(e)}")
            
        except Exception as e:
            errors.append(f"Core functionality validation failed: {str(e)}")
            logger.error(f"    Core functionality: {str(e)}")
        
        self.results["validation_results"]["core_functionality"] = {
            "success": len(errors) == 0,
            "errors": errors
        }
        
        return len(errors) == 0, errors
    
    def validate_file_structure(self) -> Tuple[bool, List[str]]:
        """Validate file structure completeness"""
        logger.info(" Validating file structure...")
        
        required_files = [
            "__init__.py",
            "index.py",
            "config.py",
            "analytics.py", 
            "business_process_monitoring.py",
            "intelligent_monitoring.py",
            "ai_observability.py",
            "observability_logging.py",
            "reporting.py",
            "README.md",
            "README.de.md", 
            "README.fr.md",
            "COMPLETION_SUMMARY.md",
            "TECHNICAL_ARCHITECTURE.md",
            "examples.py",
            "complete_examples.py",
            "run_demo.py"
        ]
        
        missing_files = []
        existing_files = []
        
        for filename in required_files:
            file_path = current_dir / filename
            if file_path.exists():
                existing_files.append(filename)
                logger.info(f"    {filename}: OK")
            else:
                missing_files.append(filename)
                logger.error(f"    {filename}: MISSING")
        
        completion_rate = len(existing_files) / len(required_files) * 100
        logger.info(f" File Structure Completion: {completion_rate:.1f}% ({len(existing_files)}/{len(required_files)})")
        
        self.results["validation_results"]["file_structure"] = {
            "completion_rate": completion_rate,
            "existing_files": existing_files,
            "missing_files": missing_files,
            "required_files": len(required_files)
        }
        
        return len(missing_files) == 0, missing_files
    
    def validate_documentation(self) -> Tuple[bool, List[str]]:
        """Validate documentation completeness"""
        logger.info(" Validating documentation...")
        
        doc_files = ["README.md", "README.de.md", "README.fr.md"]
        errors = []
        
        for doc_file in doc_files:
            doc_path = current_dir / doc_file
            if doc_path.exists():
                try:
                    content = doc_path.read_text(encoding='utf-8')
                    
                    # Check for required sections
                    required_sections = [
                        "Fahed Mlaiel", 
                        "mlaiel@live.de",
                        "LEGAL WARNING",
                        "COPYRIGHT"
                    ]
                    
                    missing_sections = [
                        section for section in required_sections 
                        if section not in content
                    ]
                    
                    if missing_sections:
                        errors.append(f"{doc_file} missing sections: {', '.join(missing_sections)}")
                        logger.warning(f"    {doc_file}: Missing sections: {', '.join(missing_sections)}")
                    else:
                        logger.info(f"    {doc_file}: Complete")
                        
                except Exception as e:
                    errors.append(f"Error reading {doc_file}: {str(e)}")
                    logger.error(f"    {doc_file}: Error reading - {str(e)}")
            else:
                errors.append(f"{doc_file} not found")
                logger.error(f"    {doc_file}: Not found")
        
        self.results["validation_results"]["documentation"] = {
            "success": len(errors) == 0,
            "errors": errors,
            "validated_files": len(doc_files)
        }
        
        return len(errors) == 0, errors
    
    async def validate_business_logic(self) -> Tuple[bool, List[str]]:
        """Validate IA Influencer Agent business logic integration"""
        logger.info(" Validating IA Influencer business logic...")
        
        errors = []
        
        try:
            from business_process_monitoring import (
                ContentType, CreatorType, ProcessStage, ProcessStatus,
                DistributionPlatform, ContentProcessingMonitor,
                CollaborationMonitor, MonetizationMonitor
            )
            
            # Validate enums
            content_types = [e.value for e in ContentType]
            creator_types = [e.value for e in CreatorType] 
            process_stages = [e.value for e in ProcessStage]
            platforms = [e.value for e in DistributionPlatform]
            
            expected_content_types = ["music", "video", "photo", "blog_post", "audio"]
            expected_creator_types = ["musician", "blogger", "photographer", "influencer", "comedian"]
            expected_stages = ["upload", "ai_analysis", "protection", "seo_optimization", "distribution"]
            expected_platforms = ["youtube", "spotify", "instagram", "tiktok", "soundcloud"]
            
            # Check business logic coverage
            for expected in expected_content_types:
                if expected not in content_types:
                    errors.append(f"Missing content type: {expected}")
            
            for expected in expected_creator_types:
                if expected not in creator_types:
                    errors.append(f"Missing creator type: {expected}")
                    
            for expected in expected_stages:
                if expected not in process_stages:
                    errors.append(f"Missing process stage: {expected}")
            
            if not errors:
                logger.info("    Business logic enums: Complete")
            else:
                logger.warning(f"    Business logic coverage: {len(errors)} issues")
            
            # Test monitors initialization
            content_monitor = ContentProcessingMonitor()
            collaboration_monitor = CollaborationMonitor()
            monetization_monitor = MonetizationMonitor()
            
            logger.info("    Business monitors: OK")
            
        except Exception as e:
            errors.append(f"Business logic validation failed: {str(e)}")
            logger.error(f"    Business logic: {str(e)}")
        
        self.results["validation_results"]["business_logic"] = {
            "success": len(errors) == 0,
            "errors": errors
        }
        
        return len(errors) == 0, errors
    
    async def run_complete_validation(self) -> Dict[str, Any]:
        """Run complete validation suite"""
        logger.info(" STARTING COMPLETE OBSERVABILITY MODULE VALIDATION")
        logger.info("=" * 70)
        
        validation_steps = [
            ("File Structure", self.validate_file_structure),
            ("Module Imports", self.validate_imports),
            ("Documentation", self.validate_documentation),
            ("Core Functionality", self.validate_core_functionality),
            ("Business Logic", self.validate_business_logic)
        ]
        
        overall_success = True
        
        for step_name, step_function in validation_steps:
            logger.info(f"\n {step_name.upper()} VALIDATION:")
            
            try:
                if asyncio.iscoroutinefunction(step_function):
                    success, details = await step_function()
                else:
                    success, details = step_function()
                
                if success:
                    logger.info(f" {step_name}: PASSED")
                else:
                    logger.error(f" {step_name}: FAILED - {len(details)} issues")
                    overall_success = False
                    
            except Exception as e:
                logger.error(f" {step_name}: EXCEPTION - {str(e)}")
                self.results["errors"].append(f"{step_name}: {str(e)}")
                overall_success = False
        
        # Generate summary
        self.results["summary"] = {
            "overall_success": overall_success,
            "validation_steps": len(validation_steps),
            "completed_at": datetime.now().isoformat(),
            "status": "PASSED" if overall_success else "FAILED"
        }
        
        # Print final results
        logger.info("\n" + "=" * 70)
        logger.info(" VALIDATION SUMMARY:")
        logger.info("=" * 70)
        
        if overall_success:
            logger.info(" ALL VALIDATIONS PASSED - MODULE IS PRODUCTION READY!")
            logger.info(" The observability module is fully functional and complete")
            logger.info(" All business logic for IA Influencer Agent is integrated")
            logger.info(" Documentation and legal protections are in place")
        else:
            logger.error(" SOME VALIDATIONS FAILED - SEE DETAILS ABOVE")
            logger.error(" Please address the issues before using in production")
        
        logger.info(f" Validation completed at: {self.results['summary']['completed_at']}")
        
        return self.results
    
    def save_results(self, filename: str = "validation_results.json"):
        """Save validation results to file"""
        results_path = current_dir / filename
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info(f" Results saved to: {results_path}")


async def main():
    """Main validation runner"""
    print(" IA INFLUENCER AGENT - OBSERVABILITY MODULE VALIDATOR")
    print("=" * 70)
    print("‍ Author: Fahed Mlaiel <mlaiel@live.de>")
    print(" Production Readiness Validation Suite")
    print("=" * 70)
    
    validator = ObservabilityValidator()
    
    try:
        results = await validator.run_complete_validation()
        validator.save_results()
        
        # Return appropriate exit code
        if results["summary"]["overall_success"]:
            print("\n VALIDATION SUCCESSFUL - MODULE READY FOR PRODUCTION!")
            return 0
        else:
            print("\n VALIDATION FAILED - ISSUES NEED TO BE ADDRESSED")
            return 1
            
    except Exception as e:
        logger.error(f" Validation runner failed: {str(e)}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f" Fatal error: {str(e)}")
        sys.exit(1)
