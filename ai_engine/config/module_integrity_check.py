#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ultra-Advanced Configuration Module Integrity Checker
=====================================================

PROPRIETARY SOFTWARE - ALL RIGHTS RESERVED
Copyright © 2025 Fahed Mlaiel (mlaiel@live.de)

⚠️  STRICT COPYRIGHT WARNING ⚠️
This software and its source code are the exclusive property of Fahed Mlaiel.
Any unauthorized copying, distribution, modification, or use of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited
and will result in legal action.

Contact: mlaiel@live.de for licensing and permissions.
"""
import os
import sys
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ConfigurationModuleChecker:
    """Ultra-advanced configuration module integrity checker"""    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.dirname(__file__)
        self.results = {}
        self.errors = []
        
    def check_all_modules(self) -> Dict[str, Any]:
        """Check all configuration modules"""        logger.info("🔍 Starting comprehensive configuration module check...")
        
        # Define expected modules
        expected_modules = [
            'ai_models_config',
            'audio_config', 
            'business_logic_config',
            'integration_config',
            'monetization_config',
            'performance_config',
            'protection_config',
            'security_config',
            'seo_config',
            'index'
        ]
        
        # Check each module
        for module_name in expected_modules:
            logger.info(f"Checking module: {module_name}")
            self.results[module_name] = self._check_module(module_name)
        
        # Check main __init__.py
        self.results['__init__'] = self._check_init_module()
        
        # Check README files
        self.results['documentation'] = self._check_documentation()
        
        return self._generate_report()
    
    def _check_module(self, module_name: str) -> Dict[str, Any]:
        """Check individual module"""        result = {
            'status': 'unknown',
            'imports': False,
            'classes': [],
            'functions': [],
            'enums': [],
            'errors': []
        }
        
        try:
            # Try to import the module
            module_path = f"backend.ai.config.{module_name}"
            module = importlib.import_module(module_path)
            result['imports'] = True
            result['status'] = 'success'
            
            # Check for key classes and functions
            for attr_name in dir(module):
                if not attr_name.startswith('_'):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type):
                        if hasattr(attr, '__bases__') and any(base.__name__ == 'Enum' for base in attr.__bases__):
                            result['enums'].append(attr_name)
                        else:
                            result['classes'].append(attr_name)
                    elif callable(attr):
                        result['functions'].append(attr_name)
            
            logger.info(f"✅ Module {module_name}: {len(result['classes'])} classes, {len(result['enums'])} enums")
            
        except ImportError as e:
            result['status'] = 'import_error'
            result['errors'].append(f"Import error: {str(e)}")
            logger.error(f"❌ Module {module_name}: Import failed - {e}")
            self.errors.append(f"{module_name}: {e}")
            
        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(f"General error: {str(e)}")
            logger.error(f"❌ Module {module_name}: Error - {e}")
            self.errors.append(f"{module_name}: {e}")
        
        return result
    
    def _check_init_module(self) -> Dict[str, Any]:
        """Check main __init__.py module"""        result = {
            'status': 'unknown',
            'master_config_manager': False,
            'configuration_registry': False,
            'all_imports': False,
            'exports': [],
            'errors': []
        }
        
        try:
            from . import MasterConfigManager, ConfigurationRegistry
            result['master_config_manager'] = True
            result['configuration_registry'] = True
            
            # Check if all expected classes are available
            from . import (
                AIModelsConfig, AudioConfig, BusinessLogicConfig,
                IntegrationConfig, MonetizationConfig, PerformanceConfig,
                ProtectionConfig, SecurityConfig, SEOConfig
            )
            result['all_imports'] = True
            result['status'] = 'success'
            
            logger.info("✅ Main __init__.py: All core components available")
            
        except ImportError as e:
            result['status'] = 'import_error'
            result['errors'].append(f"Import error: {str(e)}")
            logger.error(f"❌ Main __init__.py: Import failed - {e}")
            self.errors.append(f"__init__: {e}")
            
        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(f"General error: {str(e)}")
            logger.error(f"❌ Main __init__.py: Error - {e}")
            self.errors.append(f"__init__: {e}")
        
        return result
    
    def _check_documentation(self) -> Dict[str, Any]:
        """Check documentation files"""        result = {
            'status': 'success',
            'files': {},
            'errors': []
        }
        
        expected_files = [
            'README.md',
            'README.fr.md', 
            'README.de.md',
            'DEVELOPER_DOCS.md',
            'DEVELOPER_DOCS_ULTRA.md'
        ]
        
        for filename in expected_files:
            filepath = os.path.join(self.config_path, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        result['files'][filename] = {
                            'exists': True,
                            'size': len(content),
                            'lines': len(content.splitlines()),
                            'has_copyright': 'Fahed Mlaiel' in content
                        }
                        logger.info(f"✅ Documentation {filename}: {result['files'][filename]['lines']} lines")
                except Exception as e:
                    result['files'][filename] = {
                        'exists': True,
                        'error': str(e)
                    }
                    logger.error(f"❌ Documentation {filename}: Error reading - {e}")
            else:
                result['files'][filename] = {'exists': False}
                logger.warning(f"⚠️ Documentation {filename}: File not found")
        
        return result
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive report"""        total_modules = len([k for k in self.results.keys() if k not in ['documentation']])
        successful_modules = len([k for k, v in self.results.items() 
                                if k != 'documentation' and v.get('status') == 'success'])
        
        report = {
            'summary': {
                'total_modules': total_modules,
                'successful_modules': successful_modules,
                'success_rate': (successful_modules / total_modules * 100) if total_modules > 0 else 0,
                'has_errors': len(self.errors) > 0
            },
            'modules': self.results,
            'errors': self.errors,
            'recommendations': self._get_recommendations()
        }
        
        return report
    
    def _get_recommendations(self) -> List[str]:
        """Get recommendations based on check results"""        recommendations = []
        
        if self.errors:
            recommendations.append("Fix import errors before deployment")
        
        # Check if all documentation exists
        doc_result = self.results.get('documentation', {})
        missing_docs = [filename for filename, info in doc_result.get('files', {}).items() 
                       if not info.get('exists', False)]
        
        if missing_docs:
            recommendations.append(f"Add missing documentation files: {', '.join(missing_docs)}")
        
        if self.results.get('__init__', {}).get('status') != 'success':
            recommendations.append("Fix main __init__.py module")
        
        return recommendations
    
    def print_summary(self):
        """Print summary of check results"""        report = self._generate_report()
        summary = report['summary']
        
        print("\n" + "="*80)
        print("🔍 CONFIGURATION MODULE INTEGRITY CHECK SUMMARY")
        print("="*80)
        print(f"📊 Total Modules: {summary['total_modules']}")
        print(f"✅ Successful: {summary['successful_modules']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"❌ Errors: {len(self.errors)}")
        
        if summary['success_rate'] >= 90:
            print("🎉 STATUS: EXCELLENT - Module is ready for production!")
        elif summary['success_rate'] >= 75:
            print("✅ STATUS: GOOD - Minor issues to address")
        elif summary['success_rate'] >= 50:
            print("⚠️ STATUS: NEEDS IMPROVEMENT - Several issues found")
        else:
            print("❌ STATUS: CRITICAL - Major issues require immediate attention")
        
        if self.errors:
            print("\n🚨 ERRORS FOUND:")
            for error in self.errors:
                print(f"   • {error}")
        
        if report.get('recommendations'):
            print("\n💡 RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
        print("="*80)


def main():
    """Main function to run configuration check"""    checker = ConfigurationModuleChecker()
    
    try:
        print("🚀 Starting IA Influencer Agent Configuration Module Check...")
        results = checker.check_all_modules()
        checker.print_summary()
        
        # Exit with appropriate code
        if results['summary']['has_errors']:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"💥 Fatal error during module check: {e}")
        print(f"💥 FATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
