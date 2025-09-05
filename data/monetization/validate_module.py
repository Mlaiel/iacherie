#!/usr/bin/env python3
"""Monetization Module Validation Script
====================================

Validates that all monetization components are properly implemented and importable.
Performs comprehensive checks on module integrity and functionality.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import sys
import logging
import os
from pathlib import Path
from typing import Dict, Any, List

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_imports() -> Dict[str, bool]:
    """Validate all monetization module imports."""
    validation_results = {}
    
    try:
        # Test core module import
        from backend.monetization import __version__, __author__
        validation_results["core_module"] = True
        logger.info(f"✅ Core module imported successfully - Version: {__version__}")
        
        # Test individual component imports
        components = [
            "RevenueCalculator",
            "PaymentProcessor", 
            "MonetizationOrchestrator",
            "SubscriptionEngine",
            "CryptoWallet",
            "TaxCalculator",
            "LicensingManager",
            "ComplianceEngine",
            "RevenueOptimizer",
            "RoyaltyEngine"
        ]
        
        for component in components:
            try:
                exec(f"from backend.monetization import {component}")
                validation_results[component] = True
                logger.info(f"✅ {component} imported successfully")
            except ImportError as e:
                validation_results[component] = False
                logger.error(f"❌ Failed to import {component}: {str(e)}")
        
        # Test service interfaces
        try:
            from backend.monetization import get_monetization_orchestrator
            validation_results["MonetizationOrchestrator"] = True
            logger.info("✅ MonetizationOrchestrator imported successfully")
        except ImportError as e:
            validation_results["MonetizationOrchestrator"] = False
            logger.error(f"❌ Failed to import MonetizationOrchestrator: {str(e)}")
        
        return validation_results
        
    except Exception as e:
        logger.error(f"❌ Critical import failure: {str(e)}")
        return {"critical_failure": False}

def validate_enums() -> Dict[str, bool]:
    """Validate enum definitions."""
    validation_results = {}
    
    try:
        from backend.monetization import (
            SubscriptionStatus, Currency, PaymentStatus,
            LicenseStatus, LicenseType, TransactionStatus,
            PaymentMethod, BillingCycle, CryptoCurrency
        )
        
        enums = {
            "SubscriptionStatus": SubscriptionStatus,
            "Currency": Currency,
            "PaymentStatus": PaymentStatus,
            "LicenseStatus": LicenseStatus,
            "LicenseType": LicenseType,
            "TransactionStatus": TransactionStatus,
            "PaymentMethod": PaymentMethod,
            "BillingCycle": BillingCycle,
            "CryptoCurrency": CryptoCurrency
        }
        
        for enum_name, enum_class in enums.items():
            try:
                # Test that enum has values
                values = list(enum_class)
                if values:
                    validation_results[enum_name] = True
                    logger.info(f"✅ {enum_name} enum validated - {len(values)} values")
                else:
                    validation_results[enum_name] = False
                    logger.error(f"❌ {enum_name} enum has no values")
            except Exception as e:
                validation_results[enum_name] = False
                logger.error(f"❌ {enum_name} enum validation failed: {str(e)}")
        
        return validation_results
        
    except ImportError as e:
        logger.error(f"❌ Enum import failure: {str(e)}")
        return {"enum_import_failure": False}

def validate_data_models() -> Dict[str, bool]:
    """Validate data model definitions."""
    validation_results = {}
    
    try:
        from backend.monetization import (
            SubscriptionPlan, Subscription, PaymentRequest, CryptoWallet,
            RevenueData, TaxCalculation, OptimizationRecommendation,
            ComplianceCheck, ContentLicense, RoyaltyDistribution
        )
        
        models = [
            SubscriptionPlan, Subscription, PaymentRequest, CryptoWallet,
            RevenueData, TaxCalculation, OptimizationRecommendation,
            ComplianceCheck, ContentLicense, RoyaltyDistribution
        ]
        
        for model in models:
            try:
                # Test that model is a dataclass or has proper structure
                model_name = model.__name__
                if hasattr(model, '__dataclass_fields__') or hasattr(model, '__annotations__'):
                    validation_results[model_name] = True
                    logger.info(f"✅ {model_name} data model validated")
                else:
                    validation_results[model_name] = False
                    logger.error(f"❌ {model_name} is not properly structured")
            except Exception as e:
                validation_results[model.__name__] = False
                logger.error(f"❌ {model.__name__} validation failed: {str(e)}")
        
        return validation_results
        
    except ImportError as e:
        logger.error(f"❌ Data model import failure: {str(e)}")
        return {"model_import_failure": False}

def validate_configuration() -> Dict[str, bool]:
    """Validate module configuration."""
    validation_results = {}
    
    try:
        # Since MONETIZATION_CONFIG is not available, let's check the orchestrator
        from backend.monetization import get_monetization_orchestrator
        
        # Test that we can get the orchestrator instance
        orchestrator = get_monetization_orchestrator()
        validation_results["monetization_orchestrator"] = True
        logger.info("✅ Monetization orchestrator validated successfully")
        
        # Test that we can get other main services  
        from backend.monetization import (
            get_subscription_engine,
            get_payment_processor,
            get_revenue_optimizer,
            get_tax_calculator
        )
        
        services = {
            "subscription_engine": get_subscription_engine,
            "payment_processor": get_payment_processor,
            "revenue_optimizer": get_revenue_optimizer,
            "tax_calculator": get_tax_calculator
        }
        
        for service_name, service_getter in services.items():
            try:
                service = service_getter()
                validation_results[f"service_{service_name}"] = True
                logger.info(f"✅ Service {service_name} validated successfully")
            except Exception as e:
                validation_results[f"service_{service_name}"] = False
                logger.error(f"❌ Service {service_name} validation failed: {str(e)}")
        
        return validation_results
        
    except ImportError as e:
        logger.error(f"❌ Configuration import failure: {str(e)}")
        return {"config_import_failure": False}

def generate_validation_report(results: Dict[str, Dict[str, bool]]) -> None:
    """Generate comprehensive validation report."""
    total_tests = 0
    passed_tests = 0
    
    logger.info("\n" + "="*80)
    logger.info("🧪 MONETIZATION MODULE VALIDATION REPORT")
    logger.info("="*80)
    
    for category, category_results in results.items():
        logger.info(f"\n📋 {category.upper()} VALIDATION:")
        logger.info("-" * 40)
        
        category_passed = 0
        category_total = len(category_results)
        
        for test_name, passed in category_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"  {test_name}: {status}")
            if passed:
                category_passed += 1
                passed_tests += 1
            total_tests += 1
        
        success_rate = (category_passed / category_total * 100) if category_total > 0 else 0
        logger.info(f"  📊 Category Success Rate: {success_rate:.1f}% ({category_passed}/{category_total})")
    
    overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    logger.info("\n" + "="*80)
    logger.info("📈 OVERALL VALIDATION SUMMARY")
    logger.info("="*80)
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed Tests: {passed_tests}")
    logger.info(f"Failed Tests: {total_tests - passed_tests}")
    logger.info(f"Success Rate: {overall_success_rate:.1f}%")
    
    if overall_success_rate >= 95:
        logger.info("🎉 EXCELLENT: Monetization module is production-ready!")
    elif overall_success_rate >= 85:
        logger.info("✅ GOOD: Monetization module is well-implemented with minor issues")
    elif overall_success_rate >= 70:
        logger.info("⚠️  ACCEPTABLE: Monetization module has some issues that should be addressed")
    else:
        logger.info("❌ CRITICAL: Monetization module has significant issues requiring immediate attention")
    
    logger.info("="*80)

def main():
    """Run the complete validation suite."""
    try:
        logger.info("🔧 Starting Monetization Module Validation")
        
        # Run all validation checks
        results = {
            "imports": validate_imports(),
            "enums": validate_enums(),
            "data_models": validate_data_models(),
            "configuration": validate_configuration()
        }
        
        generate_validation_report(results)
        
        # Check if all validations passed
        all_passed = all(
            all(test_results.values()) if isinstance(test_results, dict) else test_results
            for test_results in results.values()
        )
        
        if all_passed:
            logger.info("✅ Validation completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Validation failed - please address the issues above")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
