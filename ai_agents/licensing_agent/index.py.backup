"""Licensing Agent Index - Module Entry Point & Quick Access

Industrial-grade entry point for the Licensing Agent module providing
quick access to all core functionality and streamlined initialization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from contextlib import asynccontextmanager

# Import all core components
from .licensing_agent import (
    LicensingAgent, 
    LicensingAgentManager,
    LicenseType,
    LicenseStatus,
    LicenseTerms,
    LicenseRequest
)

from .rights_manager import (
    RightsManager,
    CopyrightProtector,
    RightsType,
    OwnershipType,
    RightsStatus,
    RightsOwner
)

from .license_generator import (
    LicenseGenerator,
    ContractAutomator,
    ContractType,
    ContractTemplate,
    DocumentFormat
)

from .royalty_calculator import (
    RoyaltyCalculator,
    RevenueDistributor,
    RoyaltyModel,
    PaymentMethod,
    UsageMetrics
)

from .compliance_checker import (
    ComplianceChecker,
    LegalValidator,
    ComplianceArea,
    ComplianceStatus,
    RiskLevel
)

logger = logging.getLogger(__name__)

class LicensingAgentFactory:
    """
    Factory class for creating and managing licensing agent instances
    with proper initialization and configuration management.
    """
    
    _instances = {}
    _initialized = False
    
    @classmethod
    async def initialize(cls, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the licensing agent factory with configuration"""
        if cls._initialized:
            logger.warning("LicensingAgentFactory already initialized")
            return
            
        logger.info("Initializing Licensing Agent Factory")
        
        # Set default configuration
        default_config = {
            "blockchain_enabled": True,
            "payment_processing": True,
            "legal_compliance": True,
            "ai_analysis": True,
            "multi_currency": True,
            "audit_logging": True
        }
        
        cls._config = {**default_config, **(config or {})}
        cls._initialized = True
        
        logger.info("Licensing Agent Factory initialized successfully")
    
    @classmethod
    async def create_licensing_agent(
        cls, 
        agent_id: Optional[str] = None,
        specialized_config: Optional[Dict[str, Any]] = None
    ) -> LicensingAgent:
        """Create a new licensing agent instance"""
        if not cls._initialized:
            await cls.initialize()
            
        if not agent_id:
            agent_id = f"licensing_agent_{len(cls._instances) + 1}"
            
        if agent_id in cls._instances:
            logger.warning(f"Licensing agent {agent_id} already exists, returning existing instance")
            return cls._instances[agent_id]
        
        # Create agent with specialized configuration
        agent_config = {**cls._config, **(specialized_config or {})}
        agent = LicensingAgent(config=agent_config)
        
        # Initialize agent
        await agent.initialize()
        
        cls._instances[agent_id] = agent
        logger.info(f"Created licensing agent: {agent_id}")
        
        return agent
    
    @classmethod
    async def create_rights_manager(
        cls,
        manager_id: Optional[str] = None
    ) -> RightsManager:
        """Create a new rights manager instance"""
        if not cls._initialized:
            await cls.initialize()
            
        rights_manager = RightsManager(config=cls._config)
        await rights_manager.initialize()
        
        return rights_manager
    
    @classmethod
    async def create_complete_licensing_suite(
        cls,
        suite_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a complete licensing suite with all components"""
        if not cls._initialized:
            await cls.initialize()
            
        if not suite_id:
            suite_id = f"licensing_suite_{len(cls._instances) + 1}"
        
        # Create all components
        licensing_agent = await cls.create_licensing_agent(f"{suite_id}_agent")
        rights_manager = await cls.create_rights_manager(f"{suite_id}_rights")
        license_generator = LicenseGenerator(config=cls._config)
        royalty_calculator = RoyaltyCalculator(config=cls._config)
        compliance_checker = ComplianceChecker(config=cls._config)
        
        # Initialize components
        await license_generator.initialize()
        await royalty_calculator.initialize()
        await compliance_checker.initialize()
        
        suite = {
            "suite_id": suite_id,
            "licensing_agent": licensing_agent,
            "rights_manager": rights_manager,
            "license_generator": license_generator,
            "royalty_calculator": royalty_calculator,
            "compliance_checker": compliance_checker,
            "suite_manager": LicensingAgentManager()
        }
        
        cls._instances[suite_id] = suite
        logger.info(f"Created complete licensing suite: {suite_id}")
        
        return suite
    
    @classmethod
    def get_instance(cls, instance_id: str) -> Optional[Any]:
        """Get an existing instance by ID"""
        return cls._instances.get(instance_id)
    
    @classmethod
    def list_instances(cls) -> List[str]:
        """List all created instances"""
        return list(cls._instances.keys())
    
    @classmethod
    async def cleanup_instance(cls, instance_id: str) -> bool:
        """Cleanup and remove an instance"""
        if instance_id in cls._instances:
            instance = cls._instances[instance_id]
            
            # Cleanup based on instance type
            if hasattr(instance, 'cleanup'):
                await instance.cleanup()
            elif isinstance(instance, dict) and 'licensing_agent' in instance:
                # Cleanup suite components
                for component in instance.values():
                    if hasattr(component, 'cleanup'):
                        await component.cleanup()
            
            del cls._instances[instance_id]
            logger.info(f"Cleaned up instance: {instance_id}")
            return True
            
        return False
    
    @classmethod
    async def cleanup_all(cls) -> None:
        """Cleanup all instances"""
        for instance_id in list(cls._instances.keys()):
            await cls.cleanup_instance(instance_id)
            
        cls._initialized = False
        logger.info("All licensing agent instances cleaned up")

@asynccontextmanager
async def licensing_context(config: Optional[Dict[str, Any]] = None):
    """
    Context manager for licensing operations with automatic cleanup
    
    Usage:
        async with licensing_context() as suite:
            result = await suite['licensing_agent'].process_license_request(request)
    """
    await LicensingAgentFactory.initialize(config)
    suite = await LicensingAgentFactory.create_complete_licensing_suite()
    
    try:
        yield suite
    finally:
        await LicensingAgentFactory.cleanup_all()

# Quick access functions for common operations
async def quick_license_generation(
    content_id: str,
    licensee_id: str,
    license_type: Union[str, LicenseType],
    terms: Dict[str, Any]
) -> Dict[str, Any]:
    """Quick function for simple license generation"""
    async with licensing_context() as suite:
        agent = suite['licensing_agent']
        
        request = LicenseRequest(
            content_id=content_id,
            licensee_id=licensee_id,
            license_type=LicenseType(license_type) if isinstance(license_type, str) else license_type,
            **terms
        )
        
        return await agent.process_license_request(request)

async def quick_rights_verification(
    content_id: str,
    owner_id: str
) -> Dict[str, Any]:
    """Quick function for rights verification"""
    async with licensing_context() as suite:
        rights_manager = suite['rights_manager']
        return await rights_manager.verify_ownership(content_id, owner_id)

async def quick_compliance_check(
    contract_data: Dict[str, Any],
    jurisdiction: str
) -> Dict[str, Any]:
    """Quick function for compliance checking"""
    async with licensing_context() as suite:
        compliance_checker = suite['compliance_checker']
        return await compliance_checker.check_contract_compliance(contract_data, jurisdiction)

# Export all important classes and functions
__all__ = [
    # Factory and context management
    'LicensingAgentFactory',
    'licensing_context',
    
    # Quick access functions
    'quick_license_generation',
    'quick_rights_verification', 
    'quick_compliance_check',
    
    # Core agent classes
    'LicensingAgent',
    'LicensingAgentManager',
    'RightsManager',
    'CopyrightProtector',
    'LicenseGenerator',
    'ContractAutomator',
    'RoyaltyCalculator',
    'RevenueDistributor',
    'ComplianceChecker',
    'LegalValidator',
    
    # Enums and data classes
    'LicenseType',
    'LicenseStatus',
    'RightsType',
    'OwnershipType',
    'RightsStatus',
    'ContractType',
    'DocumentFormat',
    'RoyaltyModel',
    'PaymentMethod',
    'ComplianceArea',
    'ComplianceStatus',
    'RiskLevel',
    
    # Data classes
    'LicenseTerms',
    'LicenseRequest',
    'RightsOwner',
    'UsageMetrics'
]
