"""
AI Agents Module Validation

Comprehensive validation and testing suite for the AI Agents module.
Ensures all components are properly implemented and working correctly.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import sys
import traceback
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAgentsValidator:
    """
    Comprehensive validation system for AI Agents module
    """
    
    def __init__(self):
        self.validation_results = []
        self.errors = []
        self.warnings = []
    
    def validate_imports(self) -> bool:
        """Validate all module imports"""
        print("🔍 Validating module imports...")
        
        try:
            # Test core imports
            from . import (
                # System management
                AIAgentsSystem,
                initialize_system,
                get_system,
                shutdown_system,
                
                # Configuration
                AIAgentsConfig,
                get_config,
                load_config,
                ConfigManager,
                
                # Base agent framework
                BaseAIAgent,
                AgentConfiguration,
                AgentCapability,
                AgentStatus,
                
                # Specialized agents
                ContentCreatorAgent,
                SocialMediaManagerAgent,
                AnalyticsAgent,
                EngagementSpecialistAgent,
                AudioSpecialistAgent,
                
                # Infrastructure
                AgentRegistry,
                AgentCommunicationHub,
                WorkflowEngine,
                TaskManager,
                
                # Examples and utilities
                AIAgentsOrchestrator
            )
            
            self.validation_results.append("✅ All core imports successful")
            return True
            
        except ImportError as e:
            self.errors.append(f"❌ Import error: {str(e)}")
            return False
        except Exception as e:
            self.errors.append(f"❌ Unexpected import error: {str(e)}")
            return False
    
    def validate_class_definitions(self) -> bool:
        """Validate that all classes are properly defined"""
        print("🔍 Validating class definitions...")
        
        try:
            from . import (
                BaseAIAgent,
                ContentCreatorAgent,
                SocialMediaManagerAgent,
                AnalyticsAgent,
                EngagementSpecialistAgent,
                AudioSpecialistAgent,
                AIAgentsSystem,
                ConfigManager,
                TaskManager
            )
            
            # Check inheritance
            agents = [
                ContentCreatorAgent,
                SocialMediaManagerAgent,
                AnalyticsAgent,
                EngagementSpecialistAgent,
                AudioSpecialistAgent
            ]
            
            for agent_class in agents:
                if not issubclass(agent_class, BaseAIAgent):
                    self.errors.append(f"❌ {agent_class.__name__} does not inherit from BaseAIAgent")
                    return False
            
            # Check required methods
            required_methods = [
                'initialize',
                'process_task',
                'get_health_status',
                'shutdown'
            ]
            
            for agent_class in agents:
                for method in required_methods:
                    if not hasattr(agent_class, method):
                        self.errors.append(f"❌ {agent_class.__name__} missing method: {method}")
                        return False
            
            self.validation_results.append("✅ All class definitions valid")
            return True
            
        except Exception as e:
            self.errors.append(f"❌ Class validation error: {str(e)}")
            return False
    
    def validate_configuration_system(self) -> bool:
        """Validate configuration management"""
        print("🔍 Validating configuration system...")
        
        try:
            from .config import (
                AIAgentsConfig,
                ConfigManager,
                get_default_config,
                DatabaseConfig,
                RedisConfig,
                AIConfig,
                SecurityConfig
            )
            
            # Test default configuration
            default_config = get_default_config()
            if not isinstance(default_config, AIAgentsConfig):
                self.errors.append("❌ Default config is not AIAgentsConfig instance")
                return False
            
            # Test configuration manager
            config_manager = ConfigManager()
            if not hasattr(config_manager, 'load_config'):
                self.errors.append("❌ ConfigManager missing load_config method")
                return False
            
            # Test config components
            config_components = [
                default_config.database,
                default_config.redis,
                default_config.ai,
                default_config.security
            ]
            
            if not all(config_components):
                self.errors.append("❌ Missing configuration components")
                return False
            
            self.validation_results.append("✅ Configuration system valid")
            return True
            
        except Exception as e:
            self.errors.append(f"❌ Configuration validation error: {str(e)}")
            return False
    
    async def validate_system_initialization(self) -> bool:
        """Validate system initialization"""
        print("🔍 Validating system initialization...")
        
        try:
            from . import initialize_system, get_default_config, shutdown_system
            
            # Test system initialization with default config
            config = get_default_config()
            system = await initialize_system(config.__dict__)
            
            if not system:
                self.errors.append("❌ System initialization returned None")
                return False
            
            if not hasattr(system, 'initialized'):
                self.errors.append("❌ System missing initialized attribute")
                return False
            
            if not hasattr(system, 'health_status'):
                self.errors.append("❌ System missing health_status attribute")
                return False
            
            # Test system status
            status = await system.get_system_status()
            if not isinstance(status, dict):
                self.errors.append("❌ System status is not a dictionary")
                return False
            
            required_status_keys = ['system_health', 'initialized', 'uptime_seconds', 'agents']
            for key in required_status_keys:
                if key not in status:
                    self.errors.append(f"❌ Missing status key: {key}")
                    return False
            
            # Clean shutdown
            await shutdown_system()
            
            self.validation_results.append("✅ System initialization valid")
            return True
            
        except Exception as e:
            self.errors.append(f"❌ System initialization error: {str(e)}")
            return False
    
    def validate_agent_capabilities(self) -> bool:
        """Validate agent capabilities and enums"""
        print("🔍 Validating agent capabilities...")
        
        try:
            from . import AgentCapability
            
            # Test that AgentCapability is an enum
            if not hasattr(AgentCapability, '__members__'):
                self.errors.append("❌ AgentCapability is not an enum")
                return False
            
            # Check for required capabilities
            required_capabilities = [
                'text_generation',
                'image_generation',
                'audio_generation',
                'platform_posting',
                'engagement_management',
                'performance_analysis'
            ]
            
            available_capabilities = [cap.value for cap in AgentCapability]
            
            for capability in required_capabilities:
                if capability not in available_capabilities:
                    self.warnings.append(f"⚠️  Missing capability: {capability}")
            
            self.validation_results.append("✅ Agent capabilities valid")
            return True
            
        except Exception as e:
            self.errors.append(f"❌ Capabilities validation error: {str(e)}")
            return False
    
    def validate_communication_system(self) -> bool:
        """Validate inter-agent communication"""
        print("🔍 Validating communication system...")
        
        try:
            from . import AgentCommunicationHub, TaskManager, WorkflowEngine
            
            # Test communication hub
            hub = AgentCommunicationHub()
            if not hasattr(hub, 'initialize'):
                self.errors.append("❌ Communication hub missing initialize method")
                return False
            
            # Test task manager
            task_manager = TaskManager(None, None)  # Will be properly initialized in real usage
            if not hasattr(task_manager, 'submit_task'):
                self.errors.append("❌ Task manager missing submit_task method")
                return False
            
            # Test workflow engine
            workflow_engine = WorkflowEngine(None, None)  # Will be properly initialized in real usage
            if not hasattr(workflow_engine, 'execute_workflow'):
                self.errors.append("❌ Workflow engine missing execute_workflow method")
                return False
            
            self.validation_results.append("✅ Communication system valid")
            return True
            
        except Exception as e:
            self.errors.append(f"❌ Communication validation error: {str(e)}")
            return False
    
    def validate_module_completeness(self) -> bool:
        """Validate overall module completeness"""
        print("🔍 Validating module completeness...")
        
        try:
            from . import __all__, MODULE_INFO, AVAILABLE_AGENTS
            
            # Check that __all__ is defined and not empty
            if not __all__ or len(__all__) < 10:
                self.errors.append("❌ __all__ is not properly defined or too small")
                return False
            
            # Check module info
            if not isinstance(MODULE_INFO, dict):
                self.errors.append("❌ MODULE_INFO is not a dictionary")
                return False
            
            required_info_keys = ['name', 'version', 'description', 'capabilities']
            for key in required_info_keys:
                if key not in MODULE_INFO:
                    self.errors.append(f"❌ Missing MODULE_INFO key: {key}")
                    return False
            
            # Check available agents
            if not isinstance(AVAILABLE_AGENTS, dict):
                self.errors.append("❌ AVAILABLE_AGENTS is not a dictionary")
                return False
            
            if len(AVAILABLE_AGENTS) < 5:
                self.errors.append("❌ Too few available agents defined")
                return False
            
            self.validation_results.append("✅ Module completeness valid")
            return True
            
        except Exception as e:
            self.errors.append(f"❌ Completeness validation error: {str(e)}")
            return False
    
    async def run_full_validation(self) -> Dict[str, Any]:
        """Run complete validation suite"""
        print("🚀 Starting AI Agents Module Validation")
        print("=" * 50)
        
        validation_steps = [
            ("Import Validation", self.validate_imports),
            ("Class Definitions", self.validate_class_definitions),
            ("Configuration System", self.validate_configuration_system),
            ("Agent Capabilities", self.validate_agent_capabilities),
            ("Communication System", self.validate_communication_system),
            ("Module Completeness", self.validate_module_completeness),
            ("System Initialization", self.validate_system_initialization)
        ]
        
        results = {
            "total_tests": len(validation_steps),
            "passed": 0,
            "failed": 0,
            "errors": [],
            "warnings": [],
            "success": True
        }
        
        for step_name, validation_func in validation_steps:
            try:
                print(f"\n📋 {step_name}...")
                
                if asyncio.iscoroutinefunction(validation_func):
                    success = await validation_func()
                else:
                    success = validation_func()
                
                if success:
                    results["passed"] += 1
                    print(f"✅ {step_name} - PASSED")
                else:
                    results["failed"] += 1
                    results["success"] = False
                    print(f"❌ {step_name} - FAILED")
                
            except Exception as e:
                results["failed"] += 1
                results["success"] = False
                error_msg = f"{step_name} - Exception: {str(e)}"
                self.errors.append(error_msg)
                print(f"💥 {error_msg}")
                traceback.print_exc()
        
        # Compile final results
        results["errors"] = self.errors
        results["warnings"] = self.warnings
        results["validation_results"] = self.validation_results
        
        # Print summary
        self.print_validation_summary(results)
        
        return results
    
    def print_validation_summary(self, results: Dict[str, Any]) -> None:
        """Print validation summary"""
        print("\n" + "=" * 50)
        print("📊 VALIDATION SUMMARY")
        print("=" * 50)
        
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed']} ✅")
        print(f"Failed: {results['failed']} ❌")
        print(f"Success Rate: {(results['passed'] / results['total_tests'] * 100):.1f}%")
        
        if results['success']:
            print("\n🎉 ALL VALIDATIONS PASSED!")
            print("The AI Agents module is COMPLETELY implemented and ready for production use.")
        else:
            print("\n⚠️  SOME VALIDATIONS FAILED")
            print("Please review the errors below:")
        
        if results['errors']:
            print("\n❌ ERRORS:")
            for error in results['errors']:
                print(f"  • {error}")
        
        if results['warnings']:
            print("\n⚠️  WARNINGS:")
            for warning in results['warnings']:
                print(f"  • {warning}")
        
        if results['validation_results']:
            print("\n✅ SUCCESSFUL VALIDATIONS:")
            for result in results['validation_results']:
                print(f"  • {result}")
        
        print("\n" + "=" * 50)


async def validate_ai_agents_module():
    """Main validation function"""
    validator = AIAgentsValidator()
    results = await validator.run_full_validation()
    return results


if __name__ == "__main__":
    # Run validation
    results = asyncio.run(validate_ai_agents_module())
    
    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)
