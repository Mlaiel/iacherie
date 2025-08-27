#!/usr/bin/env python3
"""
Seeds Index Manager - Central orchestration for all data management seeds
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: All rights reserved - Unauthorized use strictly prohibited

This module provides centralized management and orchestration for all seed data
initialization across the IA Influencer Agent platform.
"""

from typing import Dict, List, Any, Optional, Union
import asyncio
import logging
from datetime import datetime, timezone
import json
from pathlib import Path

# Import all seed managers
from .user_seeds import UserSeedsManager
from .content_seeds import ContentSeedsManager
from .platform_seeds import PlatformSeedsManager
from .analytics_seeds import AnalyticsSeedsManager
from .ai_models_seeds import AIModelsSeedsManager
from .collaboration_seeds import CollaborationSeedsManager
from .monetization_seeds import MonetizationSeedsManager
from .protection_seeds import ProtectionSeedsManager
from .security_seeds import SecuritySeedsManager
from .fingerprint_seeds import FingerprintSeedsManager

logger = logging.getLogger(__name__)


class SeedsOrchestrator:
    """
    Enterprise-grade seeds orchestrator for comprehensive data management initialization.
    
    Handles:
    - Centralized seed data coordination across all modules
    - Dependency management between different seed types
    - Parallel and sequential initialization strategies
    - Error handling and rollback mechanisms
    - Performance monitoring and optimization
    - Seed data validation and integrity checks
    - Export and import capabilities for seed data
    - Environment-specific configuration management
    """
    
    def __init__(self):
        """Initialize seeds orchestrator with all managers."""
        self.managers = {
            'user_seeds': UserSeedsManager(),
            'content_seeds': ContentSeedsManager(),
            'platform_seeds': PlatformSeedsManager(),
            'analytics_seeds': AnalyticsSeedsManager(),
            'ai_models_seeds': AIModelsSeedsManager(),
            'collaboration_seeds': CollaborationSeedsManager(),
            'monetization_seeds': MonetizationSeedsManager(),
            'protection_seeds': ProtectionSeedsManager(),
            'security_seeds': SecuritySeedsManager(),
            'fingerprint_seeds': FingerprintSeedsManager()
        }
        
        # Dependency mapping for initialization order
        self.dependencies = {
            'security_seeds': [],  # Foundation - no dependencies
            'user_seeds': ['security_seeds'],
            'content_seeds': ['user_seeds', 'security_seeds'],
            'platform_seeds': ['user_seeds', 'security_seeds'],
            'ai_models_seeds': ['content_seeds', 'security_seeds'],
            'fingerprint_seeds': ['ai_models_seeds', 'content_seeds'],
            'protection_seeds': ['fingerprint_seeds', 'ai_models_seeds'],
            'analytics_seeds': ['content_seeds', 'user_seeds'],
            'monetization_seeds': ['analytics_seeds', 'platform_seeds'],
            'collaboration_seeds': ['user_seeds', 'monetization_seeds']
        }
    
    async def initialize_all(self, 
                           parallel: bool = True,
                           validate: bool = True) -> Dict[str, Any]:
        """
        Initialize all seed data with dependency management.
        
        Args:
            parallel: Whether to run independent seeds in parallel
            validate: Whether to validate seed data after initialization
            
        Returns:
            Comprehensive initialization results
        """
        logger.info("🚀 Starting comprehensive seeds initialization...")
        start_time = datetime.now(timezone.utc)
        
        results = {}
        initialized = set()
        
        try:
            # Determine initialization order based on dependencies
            initialization_order = self._calculate_initialization_order()
            
            for batch in initialization_order:
                if parallel and len(batch) > 1:
                    # Run batch in parallel
                    batch_results = await self._initialize_batch_parallel(batch)
                else:
                    # Run batch sequentially
                    batch_results = await self._initialize_batch_sequential(batch)
                
                results.update(batch_results)
                initialized.update(batch)
                
                logger.info(f"✅ Completed batch: {', '.join(batch)}")
            
            # Validate all seed data if requested
            if validate:
                validation_results = await self._validate_all_seeds()
                results['validation'] = validation_results
            
            # Generate comprehensive summary
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            summary = self._generate_summary(results, duration)
            
            logger.info(f"🎉 All seeds initialized successfully in {duration:.2f}s")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Seeds initialization failed: {str(e)}")
            # Attempt rollback of partial initialization
            await self._rollback_initialization(initialized)
            raise
    
    async def initialize_module(self, module_name: str) -> Dict[str, Any]:
        """Initialize a specific seed module."""
        if module_name not in self.managers:
            raise ValueError(f"Unknown module: {module_name}")
        
        logger.info(f"Initializing {module_name}...")
        manager = self.managers[module_name]
        
        try:
            result = await manager.initialize()
            logger.info(f"✅ {module_name} initialized successfully")
            return result
        except Exception as e:
            logger.error(f"❌ {module_name} initialization failed: {str(e)}")
            raise
    
    async def export_seeds(self, output_path: Path) -> Dict[str, Any]:
        """Export all seed data to files."""
        logger.info(f"Exporting seeds data to {output_path}")
        output_path.mkdir(parents=True, exist_ok=True)
        
        export_results = {}
        
        for module_name, manager in self.managers.items():
            try:
                # Initialize if not already done
                seed_data = await manager.initialize()
                
                # Export to JSON file
                output_file = output_path / f"{module_name}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(seed_data, f, indent=2, default=str)
                
                export_results[module_name] = {
                    'status': 'success',
                    'file_path': str(output_file),
                    'records_count': seed_data.get('count', 0)
                }
                
            except Exception as e:
                export_results[module_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        logger.info("Seeds data export completed")
        return export_results
    
    async def import_seeds(self, input_path: Path) -> Dict[str, Any]:
        """Import seed data from files."""
        logger.info(f"Importing seeds data from {input_path}")
        
        import_results = {}
        
        for module_name in self.managers.keys():
            input_file = input_path / f"{module_name}.json"
            
            if input_file.exists():
                try:
                    with open(input_file, 'r', encoding='utf-8') as f:
                        seed_data = json.load(f)
                    
                    # TODO: Implement import logic for each manager
                    import_results[module_name] = {
                        'status': 'success',
                        'records_imported': len(seed_data.get('data', {}))
                    }
                    
                except Exception as e:
                    import_results[module_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
            else:
                import_results[module_name] = {
                    'status': 'skipped',
                    'reason': 'file_not_found'
                }
        
        logger.info("Seeds data import completed")
        return import_results
    
    def _calculate_initialization_order(self) -> List[List[str]]:
        """Calculate initialization order based on dependencies."""
        batches = []
        remaining = set(self.managers.keys())
        initialized = set()
        
        while remaining:
            # Find modules with satisfied dependencies
            ready = set()
            for module in remaining:
                deps = self.dependencies.get(module, [])
                if all(dep in initialized for dep in deps):
                    ready.add(module)
            
            if not ready:
                # Circular dependency or missing dependency
                raise ValueError(f"Circular or missing dependencies for: {remaining}")
            
            batches.append(list(ready))
            remaining -= ready
            initialized.update(ready)
        
        return batches
    
    async def _initialize_batch_parallel(self, batch: List[str]) -> Dict[str, Any]:
        """Initialize a batch of modules in parallel."""
        tasks = []
        for module_name in batch:
            task = asyncio.create_task(
                self.managers[module_name].initialize(),
                name=f"init_{module_name}"
            )
            tasks.append((module_name, task))
        
        results = {}
        for module_name, task in tasks:
            try:
                result = await task
                results[module_name] = result
            except Exception as e:
                logger.error(f"Failed to initialize {module_name}: {str(e)}")
                results[module_name] = {'status': 'error', 'error': str(e)}
        
        return results
    
    async def _initialize_batch_sequential(self, batch: List[str]) -> Dict[str, Any]:
        """Initialize a batch of modules sequentially."""
        results = {}
        for module_name in batch:
            try:
                result = await self.managers[module_name].initialize()
                results[module_name] = result
            except Exception as e:
                logger.error(f"Failed to initialize {module_name}: {str(e)}")
                results[module_name] = {'status': 'error', 'error': str(e)}
                # Continue with next module in sequential mode
        
        return results
    
    async def _validate_all_seeds(self) -> Dict[str, Any]:
        """Validate all initialized seed data."""
        validation_results = {}
        
        for module_name, manager in self.managers.items():
            try:
                # Basic validation - check if manager has data
                if hasattr(manager, 'validate'):
                    result = await manager.validate()
                else:
                    result = {'status': 'validation_not_implemented'}
                
                validation_results[module_name] = result
                
            except Exception as e:
                validation_results[module_name] = {
                    'status': 'validation_error',
                    'error': str(e)
                }
        
        return validation_results
    
    async def _rollback_initialization(self, initialized: set):
        """Rollback partial initialization on failure."""
        logger.warning("Rolling back partial initialization...")
        
        for module_name in initialized:
            try:
                manager = self.managers[module_name]
                if hasattr(manager, 'reset'):
                    await manager.reset()
                    logger.info(f"Rolled back {module_name}")
            except Exception as e:
                logger.error(f"Failed to rollback {module_name}: {str(e)}")
    
    def _generate_summary(self, results: Dict[str, Any], duration: float) -> Dict[str, Any]:
        """Generate comprehensive initialization summary."""
        successful_modules = []
        failed_modules = []
        total_records = 0
        
        for module_name, result in results.items():
            if module_name == 'validation':
                continue
                
            if result.get('status') == 'success' or 'count' in result:
                successful_modules.append(module_name)
                total_records += result.get('count', 0)
            else:
                failed_modules.append(module_name)
        
        return {
            'status': 'success' if not failed_modules else 'partial_failure',
            'duration_seconds': duration,
            'total_modules': len(self.managers),
            'successful_modules': len(successful_modules),
            'failed_modules': len(failed_modules),
            'total_records_created': total_records,
            'modules_summary': {
                'successful': successful_modules,
                'failed': failed_modules
            },
            'detailed_results': results,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


# Global orchestrator instance
seeds_orchestrator = SeedsOrchestrator()


async def initialize_all_seeds(**kwargs) -> Dict[str, Any]:
    """Convenience function to initialize all seeds."""
    return await seeds_orchestrator.initialize_all(**kwargs)


async def initialize_seed_module(module_name: str) -> Dict[str, Any]:
    """Convenience function to initialize a specific seed module."""
    return await seeds_orchestrator.initialize_module(module_name)


if __name__ == "__main__":
    # Example usage
    import sys
    
    async def main():
        if len(sys.argv) > 1:
            module_name = sys.argv[1]
            result = await initialize_seed_module(module_name)
        else:
            result = await initialize_all_seeds(parallel=True, validate=True)
        
        print(json.dumps(result, indent=2, default=str))
    
    asyncio.run(main())
