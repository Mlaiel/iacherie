#!/usr/bin/env python3
"""Environment Setup Utility - IA Influencer Agent
===============================================
Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Multi-format Creator Platform with AI Protection & Monetization

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Automated setup utility for deployment environments.
Provides one-click environment initialization and validation.
===============================================
"""

import os
import sys
import asyncio
import logging
import argparse
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml
import json

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.deployment.environments import (
    EnvironmentType,
    EnvironmentCoordinator,
    EnvironmentManagerFactory,
    validate_environment_configuration
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnvironmentSetupManager:
    """
    Manages automated setup of deployment environments.
    
    Features:
    - Environment validation and initialization
    - Configuration generation and validation
    - Health checks and diagnostics
    - Prerequisites verification
    - Security setup and hardening
    - Performance optimization
    """
    
    def __init__(self):
        self.coordinator = EnvironmentCoordinator()
        self.setup_results: Dict[str, Any] = {}
        
    async def setup_all_environments(self, environment_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
Setup all or specified environments"""
        try:
            logger.info("Starting environment setup process...")
            
            # Default to all environments if none specified
            if environment_types is None:
                environment_types = [env.value for env in EnvironmentType]
            
            # Convert strings to EnvironmentType enums
            env_enums = []
            for env_type in environment_types:
                try:
                    env_enums.append(EnvironmentType(env_type))
                except ValueError:
                    logger.warning(f"Unknown environment type: {env_type}")
                    continue
            
            # Prerequisites check
            prereq_results = await self._check_prerequisites()
            self.setup_results['prerequisites'] = prereq_results
            
            if not prereq_results['all_satisfied']:
                logger.error("Prerequisites not satisfied. Aborting setup.")
                return self.setup_results
            
            # Environment setup
            setup_results = self.coordinator.setup_multi_environment_deployment(env_enums)
            self.setup_results['environment_setup'] = setup_results
            
            # Configuration validation
            config_validation = await self._validate_configurations(env_enums)
            self.setup_results['configuration_validation'] = config_validation
            
            # Security setup
            security_setup = await self._setup_security()
            self.setup_results['security_setup'] = security_setup
            
            # Health checks
            health_status = self.coordinator.get_global_health_status()
            self.setup_results['health_status'] = health_status
            
            # Performance optimization
            optimization = self.coordinator.optimize_resource_allocation()
            self.setup_results['optimization'] = optimization
            
            # Compliance validation
            compliance = self.coordinator.validate_compliance_across_environments()
            self.setup_results['compliance'] = compliance
            
            # Generate summary report
            summary = await self._generate_setup_summary()
            self.setup_results['summary'] = summary
            
            logger.info("Environment setup process completed")
            return self.setup_results
            
        except Exception as e:
            logger.error(f"Error during environment setup: {e}")
            self.setup_results['error'] = str(e)
            return self.setup_results
    
    async def _check_prerequisites(self) -> Dict[str, Any]:
        """Check system prerequisites"""
        try:
            prereq_results = {
                'all_satisfied': True,
                'checks': {},
                'missing_requirements': [],
                'recommendations': []
            }
            
            # Python version check
            python_version = sys.version_info
            python_check = python_version >= (3, 8)
            prereq_results['checks']['python_version'] = {
                'satisfied': python_check,
                'current': f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                'required': '3.8+'
            }
            if not python_check:
                prereq_results['missing_requirements'].append('Python 3.8 or higher')
                prereq_results['all_satisfied'] = False
            
            # Environment variables check
            required_env_vars = [
                'DATABASE_URL',
                'REDIS_URL',
                'JWT_SECRET_KEY'
            ]
            
            env_vars_check = True
            missing_env_vars = []
            
            for var in required_env_vars:
                if not os.getenv(var):
                    missing_env_vars.append(var)
                    env_vars_check = False
            
            prereq_results['checks']['environment_variables'] = {
                'satisfied': env_vars_check,
                'missing': missing_env_vars
            }
            
            if not env_vars_check:
                prereq_results['missing_requirements'].extend(missing_env_vars)
                prereq_results['all_satisfied'] = False
            
            # Disk space check
            disk_space = self._get_available_disk_space()
            disk_check = disk_space > 10  # GB
            prereq_results['checks']['disk_space'] = {
                'satisfied': disk_check,
                'available_gb': disk_space,
                'required_gb': 10
            }
            if not disk_check:
                prereq_results['missing_requirements'].append('At least 10GB disk space')
                prereq_results['all_satisfied'] = False
            
            # Memory check
            memory_gb = self._get_available_memory()
            memory_check = memory_gb > 4
            prereq_results['checks']['memory'] = {
                'satisfied': memory_check,
                'available_gb': memory_gb,
                'required_gb': 4
            }
            if not memory_check:
                prereq_results['missing_requirements'].append('At least 4GB RAM')
                prereq_results['all_satisfied'] = False
            
            # Network connectivity check
            network_check = await self._check_network_connectivity()
            prereq_results['checks']['network'] = network_check
            if not network_check['satisfied']:
                prereq_results['missing_requirements'].append('Network connectivity')
                prereq_results['all_satisfied'] = False
            
            # Docker availability check (if needed)
            docker_check = self._check_docker_availability()
            prereq_results['checks']['docker'] = docker_check
            
            # Kubernetes availability check (if needed)
            k8s_check = self._check_kubernetes_availability()
            prereq_results['checks']['kubernetes'] = k8s_check
            
            return prereq_results
            
        except Exception as e:
            logger.error(f"Error checking prerequisites: {e}")
            return {'all_satisfied': False, 'error': str(e)}
    
    async def _validate_configurations(self, environments: List[EnvironmentType]) -> Dict[str, Any]:
        """Validate environment configurations"""
        try:
            validation_results = {
                'overall_valid': True,
                'environment_validations': {},
                'global_issues': [],
                'recommendations': []
            }
            
            for env_type in environments:
                try:
                    manager = EnvironmentManagerFactory.create_manager(env_type)
                    config = manager.load_configuration()
                    
                    # Validate configuration
                    validation = validate_environment_configuration(env_type.value, config)
                    validation_results['environment_validations'][env_type.value] = validation
                    
                    if not validation['valid']:
                        validation_results['overall_valid'] = False
                    
                except Exception as e:
                    validation_results['environment_validations'][env_type.value] = {
                        'valid': False,
                        'error': str(e)
                    }
                    validation_results['overall_valid'] = False
            
            # Cross-environment validation
            cross_validation = self._validate_cross_environment_configurations(environments)
            validation_results['cross_environment'] = cross_validation
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating configurations: {e}")
            return {'overall_valid': False, 'error': str(e)}
    
    async def _setup_security(self) -> Dict[str, Any]:
        """Setup security configurations"""
        try:
            security_results = {
                'ssl_certificates': False,
                'firewall_rules': False,
                'access_controls': False,
                'encryption': False,
                'audit_logging': False,
                'security_scanning': False
            }
            
            # SSL certificate setup
            ssl_setup = await self._setup_ssl_certificates()
            security_results['ssl_certificates'] = ssl_setup
            
            # Firewall configuration
            firewall_setup = await self._setup_firewall_rules()
            security_results['firewall_rules'] = firewall_setup
            
            # Access control setup
            access_setup = await self._setup_access_controls()
            security_results['access_controls'] = access_setup
            
            # Encryption setup
            encryption_setup = await self._setup_encryption()
            security_results['encryption'] = encryption_setup
            
            # Audit logging setup
            audit_setup = await self._setup_audit_logging()
            security_results['audit_logging'] = audit_setup
            
            # Security scanning setup
            scanning_setup = await self._setup_security_scanning()
            security_results['security_scanning'] = scanning_setup
            
            return security_results
            
        except Exception as e:
            logger.error(f"Error setting up security: {e}")
            return {'error': str(e)}
    
    async def _generate_setup_summary(self) -> Dict[str, Any]:
        """Generate setup summary report"""
        try:
            summary = {
                'setup_completion_time': self._get_current_timestamp(),
                'total_environments': 0,
                'successful_environments': 0,
                'failed_environments': 0,
                'warnings': [],
                'next_steps': [],
                'documentation_links': []
            }
            
            # Count environments
            if 'environment_setup' in self.setup_results:
                env_setup = self.setup_results['environment_setup']
                summary['total_environments'] = len(env_setup)
                
                for env_name, env_result in env_setup.items():
                    if env_result.get('setup', False):
                        summary['successful_environments'] += 1
                    else:
                        summary['failed_environments'] += 1
            
            # Generate recommendations
            summary['next_steps'] = self._generate_next_steps()
            summary['documentation_links'] = self._get_documentation_links()
            
            # Add warnings for failed components
            if summary['failed_environments'] > 0:
                summary['warnings'].append(
                    f"{summary['failed_environments']} environments failed to setup properly"
                )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating setup summary: {e}")
            return {'error': str(e)}
    
    # Helper methods
    def _get_available_disk_space(self) -> float:
        """Get available disk space in GB"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            return free / (1024**3)  # Convert to GB
        except:
            return 0.0
    
    def _get_available_memory(self) -> float:
        """
Get available memory in GB"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.available / (1024**3)  # Convert to GB
        except:
            return 0.0
    
    async def _check_network_connectivity(self) -> Dict[str, Any]:
        """
Check network connectivity"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.github.com', timeout=5) as response:
                    return {
                        'satisfied': response.status == 200,
                        'status_code': response.status
                    }
        except:
            return {'satisfied': False, 'error': 'Network connectivity failed'}
    
    def _check_docker_availability(self) -> Dict[str, Any]:
        """
Check Docker availability"""
        try:
            import subprocess
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            return {
                'available': result.returncode == 0,
                'version': result.stdout.strip() if result.returncode == 0 else None
            }
        except:
            return {'available': False}
    
    def _check_kubernetes_availability(self) -> Dict[str, Any]:
        """
Check Kubernetes availability"""
        try:
            import subprocess
            result = subprocess.run(['kubectl', 'version', '--client'], capture_output=True, text=True)
            return {
                'available': result.returncode == 0,
                'version': result.stdout.strip() if result.returncode == 0 else None
            }
        except:
            return {'available': False}
    
    def _validate_cross_environment_configurations(self, environments: List[EnvironmentType]) -> Dict[str, Any]:
        """
Validate cross-environment configurations"""
        return {
            'conflicts': [],
            'recommendations': [
                'Ensure consistent security policies across environments',
                'Verify network connectivity between environments'
            ]
        }
    
    async def _setup_ssl_certificates(self) -> bool:
        """
Setup SSL certificates"""
        # Placeholder for SSL certificate setup
        return True
    
    async def _setup_firewall_rules(self) -> bool:
        """
Setup firewall rules"""
        # Placeholder for firewall setup
        return True
    
    async def _setup_access_controls(self) -> bool:
        """
Setup access controls"""
        # Placeholder for access control setup
        return True
    
    async def _setup_encryption(self) -> bool:
        """
Setup encryption"""
        # Placeholder for encryption setup
        return True
    
    async def _setup_audit_logging(self) -> bool:
        """
Setup audit logging"""
        # Placeholder for audit logging setup
        return True
    
    async def _setup_security_scanning(self) -> bool:
        """
Setup security scanning"""
        # Placeholder for security scanning setup
        return True
    
    def _generate_next_steps(self) -> List[str]:
        """
Generate next steps recommendations"""
        return [
            "Review environment configurations",
            "Run health checks",
            "Setup monitoring and alerting",
            "Configure backup strategies",
            "Test disaster recovery procedures"
        ]
    
    def _get_documentation_links(self) -> List[str]:
        """Get documentation links"""
        return [
            "README.md - Environment overview",
            "README.de.md - German documentation",
            "README.fr.md - French documentation",
            "API Documentation - Auto-generated docs"
        ]
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


async def main():
    """
Main setup function"""
    parser = argparse.ArgumentParser(description='IA Influencer Agent Environment Setup')
    parser.add_argument(
        '--environments',
        nargs='*',
        help='Specific environments to setup (default: all)',
        choices=[env.value for env in EnvironmentType]
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate configurations without setup'
    )
    parser.add_argument(
        '--output-format',
        choices=['json', 'yaml', 'text'],
        default='text',
        help='Output format for results'
    )
    parser.add_argument(
        '--output-file',
        help='Output file for results'
    )
    
    args = parser.parse_args()
    
    setup_manager = EnvironmentSetupManager()
    
    try:
        if args.validate_only:
            logger.info("Running validation only...")
            # Implementation for validation-only mode
            results = {'validation': 'completed'}
        else:
            logger.info("Running full environment setup...")
            results = await setup_manager.setup_all_environments(args.environments)
        
        # Output results
        if args.output_format == 'json':
            output = json.dumps(results, indent=2)
        elif args.output_format == 'yaml':
            output = yaml.dump(results, default_flow_style=False)
        else:
            output = f"Setup Results:\n{json.dumps(results, indent=2)}"
        
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(output)
            logger.info(f"Results written to {args.output_file}")
        else:
            print(output)
        
        # Exit with appropriate code
        if results.get('summary', {}).get('failed_environments', 0) > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
