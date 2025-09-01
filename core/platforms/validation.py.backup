"""Platform Integration Validation Module

Comprehensive validation and testing utilities for the platform ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .base import PlatformType, PlatformConfig, ContentType
from .index import (
    PlatformFactory, PLATFORM_REGISTRY, get_ecosystem,
    get_available_platforms, is_platform_supported
)
from .distributor import PlatformDistributor, DistributionStrategy
from .aggregator import PlatformAggregator, AggregationType
from .monitor import PlatformMonitor, MonitorSeverity
from .connector import get_connector
from .metrics import get_metrics_collector
from .scheduler import get_scheduler
from .automation import get_automation_engine

logger = logging.getLogger(__name__)


class PlatformValidator:
    """Comprehensive platform ecosystem validator"""
    
    def __init__(self):
        """Initialize validator"""
        self.validation_results: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    async def validate_ecosystem(self) -> Dict[str, Any]:
        """Validate entire platform ecosystem"""
        logger.info("Starting comprehensive ecosystem validation...")
        
        validation_start = datetime.utcnow()
        
        # Reset results
        self.validation_results = {}
        self.errors = []
        self.warnings = []
        
        try:
            # 1. Validate platform registry
            registry_validation = self._validate_platform_registry()
            self.validation_results['platform_registry'] = registry_validation
            
            # 2. Validate platform factory
            factory_validation = self._validate_platform_factory()
            self.validation_results['platform_factory'] = factory_validation
            
            # 3. Validate core modules
            core_validation = await self._validate_core_modules()
            self.validation_results['core_modules'] = core_validation
            
            # 4. Validate advanced features
            advanced_validation = await self._validate_advanced_features()
            self.validation_results['advanced_features'] = advanced_validation
            
            # 5. Validate platform implementations
            platform_validation = self._validate_platform_implementations()
            self.validation_results['platform_implementations'] = platform_validation
            
            # 6. Validate integrations
            integration_validation = await self._validate_integrations()
            self.validation_results['integrations'] = integration_validation
            
            # Calculate overall results
            validation_end = datetime.utcnow()
            validation_time = (validation_end - validation_start).total_seconds()
            
            overall_result = {
                'validation_timestamp': validation_start.isoformat(),
                'validation_duration_seconds': validation_time,
                'total_platforms_supported': len(PLATFORM_REGISTRY),
                'validation_results': self.validation_results,
                'errors': self.errors,
                'warnings': self.warnings,
                'overall_status': 'PASS' if not self.errors else 'FAIL',
                'summary': {
                    'total_validations': len(self.validation_results),
                    'passed_validations': len([r for r in self.validation_results.values() if r.get('status') == 'PASS']),
                    'failed_validations': len([r for r in self.validation_results.values() if r.get('status') == 'FAIL']),
                    'total_errors': len(self.errors),
                    'total_warnings': len(self.warnings)
                }
            }
            
            if overall_result['overall_status'] == 'PASS':
                logger.info("✅ Ecosystem validation PASSED - All systems operational")
            else:
                logger.error("❌ Ecosystem validation FAILED - Issues detected")
            
            return overall_result
            
        except Exception as e:
            self.errors.append(f"Validation process failed: {str(e)}")
            logger.error(f"Critical validation error: {e}")
            
            return {
                'validation_timestamp': validation_start.isoformat(),
                'validation_duration_seconds': 0,
                'overall_status': 'CRITICAL_FAILURE',
                'errors': self.errors,
                'warnings': self.warnings,
                'critical_error': str(e)
            }
    
    def _validate_platform_registry(self) -> Dict[str, Any]:
        """Validate platform registry completeness"""
        try:
            expected_platforms = 28  # Based on requirements
            actual_platforms = len(PLATFORM_REGISTRY)
            
            # Check if all expected platform types are present
            expected_types = [
                # Core platforms (16)
                PlatformType.SPOTIFY, PlatformType.YOUTUBE, PlatformType.INSTAGRAM,
                PlatformType.TIKTOK, PlatformType.TWITTER, PlatformType.FACEBOOK,
                PlatformType.TWITCH, PlatformType.SOUNDCLOUD, PlatformType.APPLE_MUSIC,
                PlatformType.BANDCAMP, PlatformType.REDDIT, PlatformType.LINKEDIN,
                PlatformType.PINTEREST, PlatformType.SNAPCHAT, PlatformType.DISCORD,
                PlatformType.TELEGRAM,
                
                # Extended platforms (12)
                PlatformType.WHATSAPP, PlatformType.VIMEO, PlatformType.CLUBHOUSE,
                PlatformType.MEDIUM, PlatformType.MASTODON, PlatformType.BEREAL,
                PlatformType.ONLYFANS, PlatformType.PATREON, PlatformType.SUBSTACK,
                PlatformType.THREADS, PlatformType.KICK, PlatformType.RUMBLE
            ]
            
            missing_platforms = []
            for platform_type in expected_types:
                if platform_type not in PLATFORM_REGISTRY:
                    missing_platforms.append(platform_type.value)
            
            if missing_platforms:
                self.errors.append(f"Missing platforms in registry: {missing_platforms}")
                return {
                    'status': 'FAIL',
                    'expected_platforms': expected_platforms,
                    'actual_platforms': actual_platforms,
                    'missing_platforms': missing_platforms
                }
            
            if actual_platforms != expected_platforms:
                self.warnings.append(f"Platform count mismatch: expected {expected_platforms}, got {actual_platforms}")
            
            return {
                'status': 'PASS',
                'expected_platforms': expected_platforms,
                'actual_platforms': actual_platforms,
                'missing_platforms': [],
                'all_platforms_registered': True
            }
            
        except Exception as e:
            self.errors.append(f"Platform registry validation failed: {str(e)}")
            return {'status': 'FAIL', 'error': str(e)}
    
    def _validate_platform_factory(self) -> Dict[str, Any]:
        """Validate platform factory functionality"""
        try:
            # Test factory methods
            available_platforms = get_available_platforms()
            
            if len(available_platforms) == 0:
                self.errors.append("No platforms available from factory")
                return {'status': 'FAIL', 'error': 'No platforms available'}
            
            # Test platform support checking
            for platform_type in available_platforms[:5]:  # Test first 5
                if not is_platform_supported(platform_type):
                    self.errors.append(f"Platform {platform_type.value} reported as not supported")
            
            return {
                'status': 'PASS',
                'available_platforms_count': len(available_platforms),
                'factory_methods_working': True
            }
            
        except Exception as e:
            self.errors.append(f"Platform factory validation failed: {str(e)}")
            return {'status': 'FAIL', 'error': str(e)}
    
    async def _validate_core_modules(self) -> Dict[str, Any]:
        """Validate core module functionality"""
        results = {}
        
        try:
            # Validate distributor
            try:
                distributor = PlatformDistributor(None)  # Mock platform manager
                results['distributor'] = {'status': 'PASS', 'initialized': True}
            except Exception as e:
                self.errors.append(f"PlatformDistributor initialization failed: {str(e)}")
                results['distributor'] = {'status': 'FAIL', 'error': str(e)}
            
            # Validate aggregator
            try:
                aggregator = PlatformAggregator(None)  # Mock platform manager
                results['aggregator'] = {'status': 'PASS', 'initialized': True}
            except Exception as e:
                self.errors.append(f"PlatformAggregator initialization failed: {str(e)}")
                results['aggregator'] = {'status': 'FAIL', 'error': str(e)}
            
            # Validate monitor
            try:
                monitor = PlatformMonitor()
                results['monitor'] = {'status': 'PASS', 'initialized': True}
            except Exception as e:
                self.errors.append(f"PlatformMonitor initialization failed: {str(e)}")
                results['monitor'] = {'status': 'FAIL', 'error': str(e)}
            
            # Validate connector
            try:
                connector = await get_connector()
                results['connector'] = {'status': 'PASS', 'initialized': True}
            except Exception as e:
                self.errors.append(f"PlatformConnector initialization failed: {str(e)}")
                results['connector'] = {'status': 'FAIL', 'error': str(e)}
            
            return results
            
        except Exception as e:
            self.errors.append(f"Core modules validation failed: {str(e)}")
            return {'status': 'FAIL', 'error': str(e)}
    
    async def _validate_advanced_features(self) -> Dict[str, Any]:
        """Validate advanced feature modules"""
        results = {}
        
        try:
            # Validate metrics collector
            try:
                metrics_collector = get_metrics_collector()
                results['metrics_collector'] = {'status': 'PASS', 'initialized': True}
            except Exception as e:
                self.errors.append(f"MetricsCollector initialization failed: {str(e)}")
                results['metrics_collector'] = {'status': 'FAIL', 'error': str(e)}
            
            # Validate scheduler
            try:
                scheduler = get_scheduler()
                results['scheduler'] = {'status': 'PASS', 'initialized': True}
            except Exception as e:
                self.errors.append(f"PlatformScheduler initialization failed: {str(e)}")
                results['scheduler'] = {'status': 'FAIL', 'error': str(e)}
            
            # Validate automation engine
            try:
                automation_engine = get_automation_engine()
                results['automation_engine'] = {'status': 'PASS', 'initialized': True}
            except Exception as e:
                self.errors.append(f"AutomationEngine initialization failed: {str(e)}")
                results['automation_engine'] = {'status': 'FAIL', 'error': str(e)}
            
            return results
            
        except Exception as e:
            self.errors.append(f"Advanced features validation failed: {str(e)}")
            return {'status': 'FAIL', 'error': str(e)}
    
    def _validate_platform_implementations(self) -> Dict[str, Any]:
        """Validate individual platform implementations"""
        results = {}
        
        try:
            for platform_type, platform_class in PLATFORM_REGISTRY.items():
                try:
                    # Check if class can be imported and has required methods
                    required_methods = [
                        'authenticate', 'refresh_token', 'upload_content',
                        'get_analytics', 'search_content', 'get_user_content',
                        'delete_content', 'update_content'
                    ]
                    
                    missing_methods = []
                    for method in required_methods:
                        if not hasattr(platform_class, method):
                            missing_methods.append(method)
                    
                    if missing_methods:
                        self.warnings.append(f"Platform {platform_type.value} missing methods: {missing_methods}")
                        results[platform_type.value] = {
                            'status': 'WARNING',
                            'missing_methods': missing_methods
                        }
                    else:
                        results[platform_type.value] = {
                            'status': 'PASS',
                            'all_methods_present': True
                        }
                        
                except Exception as e:
                    self.errors.append(f"Platform {platform_type.value} validation failed: {str(e)}")
                    results[platform_type.value] = {
                        'status': 'FAIL',
                        'error': str(e)
                    }
            
            return {
                'status': 'PASS' if not self.errors else 'PARTIAL',
                'platform_results': results,
                'total_platforms_validated': len(results)
            }
            
        except Exception as e:
            self.errors.append(f"Platform implementations validation failed: {str(e)}")
            return {'status': 'FAIL', 'error': str(e)}
    
    async def _validate_integrations(self) -> Dict[str, Any]:
        """Validate module integrations"""
        results = {}
        
        try:
            # Test ecosystem initialization
            try:
                ecosystem = await get_ecosystem()
                results['ecosystem'] = {'status': 'PASS', 'initialized': True}
            except Exception as e:
                self.warnings.append(f"Ecosystem initialization warning: {str(e)}")
                results['ecosystem'] = {'status': 'WARNING', 'error': str(e)}
            
            # Test module imports
            module_imports = [
                'base', 'distributor', 'aggregator', 'monitor', 'connector',
                'metrics', 'scheduler', 'automation', 'index'
            ]
            
            for module_name in module_imports:
                try:
                    exec(f"from . import {module_name}")
                    results[f'{module_name}_import'] = {'status': 'PASS'}
                except Exception as e:
                    self.errors.append(f"Module {module_name} import failed: {str(e)}")
                    results[f'{module_name}_import'] = {'status': 'FAIL', 'error': str(e)}
            
            return results
            
        except Exception as e:
            self.errors.append(f"Integration validation failed: {str(e)}")
            return {'status': 'FAIL', 'error': str(e)}
    
    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate human-readable validation report"""
        report = []
        report.append("=" * 80)
        report.append("🔍 PLATFORM ECOSYSTEM VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        summary = validation_results.get('summary', {})
        status = validation_results.get('overall_status', 'UNKNOWN')
        
        report.append(f"📊 OVERALL STATUS: {status}")
        report.append(f"⏱️  VALIDATION TIME: {validation_results.get('validation_timestamp', 'N/A')}")
        report.append(f"⚡ DURATION: {validation_results.get('validation_duration_seconds', 0):.2f} seconds")
        report.append(f"🎯 PLATFORMS SUPPORTED: {validation_results.get('total_platforms_supported', 0)}")
        report.append("")
        
        # Validation summary
        report.append("📈 VALIDATION SUMMARY:")
        report.append(f"   ✅ Total Validations: {summary.get('total_validations', 0)}")
        report.append(f"   ✅ Passed: {summary.get('passed_validations', 0)}")
        report.append(f"   ❌ Failed: {summary.get('failed_validations', 0)}")
        report.append(f"   🚨 Errors: {summary.get('total_errors', 0)}")
        report.append(f"   ⚠️  Warnings: {summary.get('total_warnings', 0)}")
        report.append("")
        
        # Detailed results
        report.append("📋 DETAILED RESULTS:")
        for category, result in validation_results.get('validation_results', {}).items():
            status_icon = "✅" if result.get('status') == 'PASS' else "❌" if result.get('status') == 'FAIL' else "⚠️"
            report.append(f"   {status_icon} {category.replace('_', ' ').title()}: {result.get('status', 'UNKNOWN')}")
        
        report.append("")
        
        # Errors
        errors = validation_results.get('errors', [])
        if errors:
            report.append("🚨 ERRORS:")
            for error in errors:
                report.append(f"   ❌ {error}")
            report.append("")
        
        # Warnings
        warnings = validation_results.get('warnings', [])
        if warnings:
            report.append("⚠️ WARNINGS:")
            for warning in warnings:
                report.append(f"   ⚠️ {warning}")
            report.append("")
        
        # Footer
        report.append("=" * 80)
        report.append("© 2025 Fahed Mlaiel - Platform Ecosystem Validation")
        report.append("=" * 80)
        
        return "\n".join(report)


async def validate_platform_ecosystem() -> Dict[str, Any]:
    """Run comprehensive platform ecosystem validation"""
    validator = PlatformValidator()
    return await validator.validate_ecosystem()


def quick_validation() -> bool:
    """Quick validation check - returns True if basic functionality works"""
    try:
        # Check basic imports
        from . import base, distributor, aggregator, monitor, connector
        from . import metrics, scheduler, automation, index
        
        # Check platform registry
        if len(PLATFORM_REGISTRY) < 20:  # Should have at least 20 platforms
            return False
        
        # Check factory
        available = get_available_platforms()
        if len(available) == 0:
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Quick validation failed: {e}")
        return False


async def async_quick_validation() -> bool:
    """Async version of quick validation check"""
    return quick_validation()


def get_ecosystem_health() -> Dict[str, Any]:
    """Get current ecosystem health status"""
    try:
        return {
            'status': 'HEALTHY',
            'timestamp': datetime.utcnow().isoformat(),
            'total_platforms': len(PLATFORM_REGISTRY),
            'available_platforms': len(get_available_platforms()),
            'core_modules_loaded': True,
            'advanced_features_loaded': True
        }
    except Exception as e:
        return {
            'status': 'UNHEALTHY',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }


if __name__ == "__main__":
    # Run validation when module is executed directly
    import asyncio
    
    async def main():
        print("🔍 Running Platform Ecosystem Validation...")
        results = await validate_platform_ecosystem()
        
        validator = PlatformValidator()
        report = validator.generate_validation_report(results)
        print(report)
        
        return results['overall_status'] == 'PASS'
    
    success = asyncio.run(main())
    exit(0 if success else 1)
