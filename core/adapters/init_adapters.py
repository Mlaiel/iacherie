#!/usr/bin/env python3
"""Adapter System Initialization Script

This script initializes the complete adapter system with automatic discovery,
configuration loading, and health monitoring setup.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution
of this code is strictly prohibited without explicit written permission.

Usage:
    python init_adapters.py [--environment ENV] [--config-dir DIR] [--auto-register]
"""

import asyncio
import logging
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.core.adapters import (
    initialize_adapter_index,
    get_adapter_index_manager,
    get_configuration_manager,
    get_adapter_registry,
    Environment
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def initialize_adapter_system(environment: Environment, config_dir: Path = None, auto_register: bool = True):
    """
Initialize the complete adapter system."""
    
    logger.info(f"Initializing Adapter System for environment: {environment.value}")
    start_time = datetime.utcnow()
    
    try:
        # Step 1: Initialize configuration manager
        logger.info("Step 1: Loading configuration...")
        config_manager = get_configuration_manager(environment)
        logger.info(f"Configuration loaded for {len(config_manager.configurations)} adapters")
        
        # Step 2: Initialize adapter index and discovery
        logger.info("Step 2: Discovering and loading adapter modules...")
        discovery_result = await initialize_adapter_index(auto_register=auto_register)
        
        logger.info(f"Discovery Results:")
        logger.info(f"  - Total modules found: {discovery_result.total_modules}")
        logger.info(f"  - Successfully loaded: {discovery_result.loaded_modules}")
        logger.info(f"  - Failed to load: {discovery_result.failed_modules}")
        logger.info(f"  - Discovery time: {discovery_result.discovery_time:.2f}s")
        logger.info(f"  - Discovered adapters: {', '.join(discovery_result.discovered_adapters)}")
        
        if discovery_result.errors:
            logger.warning("Errors during discovery:")
            for error in discovery_result.errors:
                logger.warning(f"  - {error}")
        
        # Step 3: Get system status
        logger.info("Step 3: Checking system status...")
        index_manager = get_adapter_index_manager()
        system_status = await index_manager.get_system_status()
        
        logger.info("System Status:")
        logger.info(f"  - System initialized: {system_status['system_initialized']}")
        logger.info(f"  - Total adapter classes: {system_status['total_adapter_classes']}")
        logger.info(f"  - Available platforms: {', '.join(system_status['available_platforms'])}")
        
        # Step 4: Validate configurations
        logger.info("Step 4: Validating adapter configurations...")
        validation_results = {}
        for adapter_name in config_manager.list_adapters():
            validation = config_manager.validate_configuration(adapter_name)
            validation_results[adapter_name] = validation
            
            status = "✓ VALID" if validation['valid'] else "✗ INVALID"
            logger.info(f"  - {adapter_name}: {status}")
            
            if validation['errors']:
                for error in validation['errors']:
                    logger.error(f"    Error: {error}")
            
            if validation['warnings']:
                for warning in validation['warnings']:
                    logger.warning(f"    Warning: {warning}")
        
        # Step 5: Auto-register adapters if requested
        if auto_register:
            logger.info("Step 5: Auto-registering valid adapters...")
            registry = get_adapter_registry()
            registered_count = 0
            
            for adapter_name, validation in validation_results.items():
                if validation['valid']:
                    try:
                        # Get adapter configuration
                        adapter_config = config_manager.get_adapter_config(adapter_name)
                        
                        # Create adapter instance based on platform type
                        adapter_class = index_manager.get_adapter_class(
                            adapter_config.platform_type.title() + "Adapter"
                        )
                        
                        if adapter_class:
                            adapter_instance = adapter_class(adapter_config.__dict__)
                            registration_id = await registry.register_adapter(
                                adapter_instance, 
                                adapter_config.__dict__
                            )
                            logger.info(f"    Registered {adapter_name} with ID: {registration_id}")
                            registered_count += 1
                        else:
                            logger.warning(f"    No adapter class found for {adapter_name}")
                    
                    except Exception as e:
                        logger.error(f"    Failed to register {adapter_name}: {str(e)}")
            
            logger.info(f"Successfully registered {registered_count} adapters")
        
        # Step 6: Final health check
        logger.info("Step 6: Running initial health check...")
        final_status = await index_manager.get_system_status()
        health_status = final_status.get('health', {})
        
        logger.info("Health Check Results:")
        logger.info(f"  - Total adapters: {health_status.get('total_adapters', 0)}")
        logger.info(f"  - Healthy adapters: {health_status.get('healthy_adapters', 0)}")
        logger.info(f"  - Overall health: {health_status.get('overall_health', 'unknown')}")
        
        # Calculate total initialization time
        total_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"✓ Adapter system initialization completed in {total_time:.2f}s")
        
        return {
            'success': True,
            'discovery_result': discovery_result,
            'system_status': system_status,
            'validation_results': validation_results,
            'initialization_time': total_time
        }
    
    except Exception as e:
        logger.error(f"Failed to initialize adapter system: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'initialization_time': (datetime.utcnow() - start_time).total_seconds()
        }

async def test_adapter_operations():
    """Test basic adapter operations after initialization."""
    logger.info("Testing adapter operations...")
    
    try:
        registry = get_adapter_registry()
        adapters = registry.list_adapters()
        
        logger.info(f"Found {len(adapters)} registered adapters:")
        for adapter_id in adapters:
            adapter = registry.get_adapter(adapter_id)
            logger.info(f"  - {adapter.name} ({adapter.platform_type}) - Status: {adapter.status.value}")
        
        # Test health checks
        if adapters:
            index_manager = get_adapter_index_manager()
            health_status = await index_manager.health_monitor.check_all_adapters_health()
            
            logger.info("Health check completed:")
            for adapter_id, health in health_status['adapters'].items():
                status = health['status']
                response_time = health['response_time']
                logger.info(f"  - {adapter_id}: {status} (response: {response_time:.3f}s)")
        
        return True
    
    except Exception as e:
        logger.error(f"Adapter operation test failed: {str(e)}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Initialize the IA Influencer Agent Adapter System"
    )
    
    parser.add_argument(
        '--environment', '-e',
        type=str,
        choices=['development', 'staging', 'production', 'testing'],
        default='development',
        help='Deployment environment (default: development)'
    )
    
    parser.add_argument(
        '--config-dir', '-c',
        type=Path,
        help='Custom configuration directory path'
    )
    
    parser.add_argument(
        '--auto-register', '-r',
        action='store_true',
        default=True,
        help='Automatically register valid adapters (default: True)'
    )
    
    parser.add_argument(
        '--test-operations', '-t',
        action='store_true',
        help='Run adapter operation tests after initialization'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Convert environment string to enum
    environment = Environment(args.environment)
    
    async def run_initialization():
        """Run the initialization process."""
        print("=" * 80)
        print("IA INFLUENCER AGENT - ADAPTER SYSTEM INITIALIZATION")
        print("=" * 80)
        print(f"Environment: {environment.value}")
        print(f"Auto-register: {args.auto_register}")
        if args.config_dir:
            print(f"Config directory: {args.config_dir}")
        print("=" * 80)
        
        # Initialize the adapter system
        result = await initialize_adapter_system(
            environment=environment,
            config_dir=args.config_dir,
            auto_register=args.auto_register
        )
        
        if result['success']:
            print("\n✓ Adapter system initialization SUCCESSFUL!")
            
            if args.test_operations:
                print("\nRunning adapter operation tests...")
                test_result = await test_adapter_operations()
                if test_result:
                    print("✓ Adapter operation tests PASSED!")
                else:
                    print("✗ Adapter operation tests FAILED!")
                    return 1
        else:
            print(f"\n✗ Adapter system initialization FAILED: {result['error']}")
            return 1
        
        print("\nAdapter system is ready for use!")
        return 0
    
    # Run the initialization
    try:
        exit_code = asyncio.run(run_initialization())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nInitialization interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
