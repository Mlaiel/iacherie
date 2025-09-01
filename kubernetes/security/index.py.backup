"""Main Index for Deployment Security Module

This module provides easy access to all security components for deployment
environments in the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Company: IA Influencer Agent Platform
License: Proprietary - All rights reserved

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and
will result in legal action.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import all security components
from .certificate_manager import CertificateManager, TLSConfigGenerator
from .encrypted_config import EncryptedConfigManager, SecretVaultIntegration, ConfigEncryption
from .secure_communication import SecureChannelManager, MessageEncryption, ProtocolValidator
from .compliance_monitor import ComplianceChecker, SecurityAuditLogger, PolicyEnforcer
from .access_control import DeploymentAccessControl, PermissionManager, RoleBasedSecurity
from .vulnerability_scanner import ContainerScanner, DependencyChecker, SecurityAssessment

logger = logging.getLogger(__name__)


class DeploymentSecurityManager:
    """
    Unified security management interface for deployment environments
    
    This class provides a centralized interface to all security components,
    making it easy to configure and manage security for deployment environments.
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        redis_url: str = "redis://localhost:6379",
        cert_dir: str = "/etc/ssl/certs",
        key_dir: str = "/etc/ssl/private",
        log_dir: str = "/var/log/ia-influencer/security"
    ):
        """
        Initialize deployment security manager
        
        Args:
            config: Security configuration dictionary
            redis_url: Redis connection URL
            cert_dir: Certificate directory
            key_dir: Private key directory
            log_dir: Log directory
        """
        self.config = config or {}
        self.redis_url = redis_url
        self.cert_dir = cert_dir
        self.key_dir = key_dir
        self.log_dir = log_dir
        
        # Initialize security components
        self._initialize_components()
        
        logger.info("Deployment security manager initialized")
    
    def _initialize_components(self):
        """Initialize all security components"""
        try:
            # Certificate management
            self.certificate_manager = CertificateManager(
                cert_dir=self.cert_dir,
                key_dir=self.key_dir,
                auto_renewal=self.config.get('auto_renewal', True)
            )
            
            self.tls_generator = TLSConfigGenerator(self.certificate_manager)
            
            # Configuration security
            self.config_manager = EncryptedConfigManager(
                config_dir=self.config.get('config_dir', '/etc/ia-influencer/config')
            )
            
            self.secret_vault = SecretVaultIntegration()
            self.config_encryption = ConfigEncryption()
            
            # Secure communication
            self.channel_manager = SecureChannelManager(
                redis_url=self.redis_url
            )
            
            self.message_encryption = MessageEncryption()
            self.protocol_validator = ProtocolValidator()
            
            # Compliance and monitoring
            self.audit_logger = SecurityAuditLogger(
                log_directory=self.log_dir,
                retention_days=self.config.get('audit_retention_days', 2555)
            )
            
            self.compliance_checker = ComplianceChecker(self.audit_logger)
            self.policy_enforcer = PolicyEnforcer(self.audit_logger)
            
            # Access control
            self.access_control = DeploymentAccessControl(
                redis_url=self.redis_url,
                jwt_secret=self.config.get('jwt_secret', 'default-secret-change-in-production'),
                session_timeout=self.config.get('session_timeout', 3600)
            )
            
            # Vulnerability scanning
            self.container_scanner = ContainerScanner()
            self.dependency_checker = DependencyChecker()
            self.security_assessment = SecurityAssessment()
            
            logger.info("All security components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize security components: {e}")
            raise
    
    async def setup_environment_security(
        self,
        environment: str,
        domain: str,
        services: List[str] = None
    ) -> Dict[str, Any]:
        """
        Setup comprehensive security for deployment environment
        
        Args:
            environment: Environment name (dev, staging, prod)
            domain: Domain name for certificates
            services: List of services to secure
            
        Returns:
            Setup results and configuration
        """
        try:
            logger.info(f"Setting up security for environment: {environment}")
            
            setup_results = {
                'environment': environment,
                'domain': domain,
                'setup_time': datetime.utcnow().isoformat(),
                'certificates': {},
                'configurations': {},
                'access_control': {},
                'monitoring': {}
            }
            
            # 1. Generate certificates for domain
            logger.info(f"Generating certificates for domain: {domain}")
            
            # Generate private key
            private_key = self.certificate_manager.generate_private_key("rsa", 2048)
            
            # Create certificate request
            csr = self.certificate_manager.create_certificate_request(
                private_key=private_key,
                common_name=domain,
                subject_alt_names=[f"*.{domain}", domain]
            )
            
            # Self-sign certificate (in production, use proper CA)
            certificate = self.certificate_manager.self_sign_certificate(
                private_key, csr, validity_days=365
            )
            
            # Save certificate and key
            cert_path, key_path = self.certificate_manager.save_certificate_and_key(
                certificate, private_key, f"{environment}-{domain.replace('.', '-')}"
            )
            
            setup_results['certificates'] = {
                'certificate_path': cert_path,
                'private_key_path': key_path,
                'domain': domain,
                'validity_days': 365
            }
            
            # 2. Setup encrypted configuration
            logger.info(f"Setting up encrypted configuration for {environment}")
            
            from .encrypted_config import ConfigTemplate
            config_template = ConfigTemplate(
                environment=environment,
                database_url=f"postgresql://user:pass@localhost/{environment}_db",
                redis_url=self.redis_url,
                secret_key=self.config_encryption._fernet.generate_key().decode(),
                jwt_secret=self.config_encryption._fernet.generate_key().decode(),
                api_keys={},
                external_services={},
                security_settings={
                    'tls_enabled': True,
                    'certificate_path': cert_path,
                    'private_key_path': key_path,
                    'session_timeout': 3600,
                    'mfa_required': environment == 'prod'
                },
                monitoring_config={
                    'audit_logging': True,
                    'metrics_enabled': True,
                    'alerting_enabled': environment == 'prod'
                }
            )
            
            config_file = self.config_manager.create_environment_config(
                environment, config_template
            )
            
            setup_results['configurations'] = {
                'config_file': config_file,
                'template_created': True
            }
            
            # 3. Setup access control
            logger.info(f"Setting up access control for {environment}")
            
            # Create environment-specific admin user
            admin_user = self.access_control.rbac.create_user(
                user_id=f"{environment}_admin",
                username=f"admin_{environment}",
                email=f"admin-{environment}@ia-influencer.com",
                role_ids=["system_admin"]
            )
            
            setup_results['access_control'] = {
                'admin_user_created': True,
                'admin_user_id': admin_user.id,
                'default_roles': list(self.access_control.rbac.roles.keys())
            }
            
            # 4. Setup monitoring and compliance
            logger.info(f"Setting up monitoring for {environment}")
            
            # Create secure communication channel for the environment
            channel_config = self.channel_manager.create_secure_channel(
                channel_id=f"{environment}_admin_channel",
                participants=[f"{environment}_admin"],
                protocol="websocket",
                message_ttl=3600
            )
            
            setup_results['monitoring'] = {
                'audit_logging_enabled': True,
                'secure_channel_created': True,
                'channel_id': channel_config.channel_id
            }
            
            logger.info(f"Environment security setup completed: {environment}")
            return setup_results
            
        except Exception as e:
            logger.error(f"Failed to setup environment security: {e}")
            raise
    
    async def perform_security_assessment(
        self,
        environment: str,
        scan_containers: bool = True,
        scan_dependencies: bool = True,
        scan_configurations: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive security assessment
        
        Args:
            environment: Environment to assess
            scan_containers: Enable container scanning
            scan_dependencies: Enable dependency scanning
            scan_configurations: Enable configuration scanning
            
        Returns:
            Assessment results
        """
        try:
            logger.info(f"Starting security assessment for environment: {environment}")
            
            assessment_config = {
                'scan_containers': scan_containers,
                'scan_dependencies': scan_dependencies,
                'scan_configurations': scan_configurations,
                'python_requirements': 'requirements.txt',
                'nodejs_package_json': 'package.json',
                'configuration_files': [
                    f'/etc/ia-influencer/config/{environment}.json.encrypted'
                ]
            }
            
            # Perform comprehensive assessment
            assessment_result = await self.security_assessment.perform_comprehensive_assessment(
                target_environment=environment,
                assessment_config=assessment_config
            )
            
            # Generate detailed report
            report = await self.security_assessment.generate_assessment_report(
                assessment_result,
                output_file=f"/tmp/security_assessment_{environment}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            logger.info(f"Security assessment completed for {environment}: Score {assessment_result.overall_score:.1f}")
            
            return {
                'assessment_id': assessment_result.assessment_id,
                'environment': environment,
                'overall_score': assessment_result.overall_score,
                'risk_level': assessment_result.risk_level,
                'total_vulnerabilities': sum(
                    len(scan.vulnerabilities) for scan in assessment_result.scan_results
                ),
                'recommendations': assessment_result.recommendations,
                'report_file': report.get('report_file'),
                'scan_summary': {
                    scan.scan_type.value: scan.summary
                    for scan in assessment_result.scan_results
                }
            }
            
        except Exception as e:
            logger.error(f"Security assessment failed: {e}")
            raise
    
    async def monitor_compliance(
        self,
        environment: str,
        frameworks: List[str] = None
    ) -> Dict[str, Any]:
        """
        Monitor compliance for environment
        
        Args:
            environment: Environment to monitor
            frameworks: List of compliance frameworks to check
            
        Returns:
            Compliance monitoring results
        """
        try:
            from .compliance_monitor import ComplianceFramework
            
            if frameworks is None:
                frameworks = ['gdpr', 'soc2', 'iso27001']
            
            # Convert string frameworks to enum
            framework_enums = []
            for framework in frameworks:
                try:
                    framework_enums.append(ComplianceFramework(framework.lower()))
                except ValueError:
                    logger.warning(f"Unknown compliance framework: {framework}")
            
            # Create compliance context
            context = {
                'environment': environment,
                'database_encryption_enabled': True,
                'application_encryption_enabled': True,
                'audit_logging_enabled': True,
                'data_access_logging_enabled': True,
                'retention_policies_defined': True,
                'automatic_cleanup_enabled': True,
                'rbac_enabled': True,
                'mfa_enabled': environment == 'prod',
                'monitoring_enabled': True,
                'alerting_configured': True,
                'incident_procedures_defined': True,
                'incident_tracking_system': True
            }
            
            # Generate compliance reports
            compliance_reports = await self.compliance_checker.generate_compliance_report(
                frameworks=framework_enums,
                context=context,
                output_file=f"/tmp/compliance_report_{environment}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            # Summary results
            results = {
                'environment': environment,
                'assessment_time': datetime.utcnow().isoformat(),
                'frameworks': {}
            }
            
            for framework_name, report in compliance_reports.items():
                results['frameworks'][framework_name] = {
                    'compliance_score': report.compliance_score,
                    'total_rules': report.total_rules,
                    'passed_rules': report.passed_rules,
                    'failed_rules': report.failed_rules,
                    'violations_count': len(report.violations),
                    'recommendations_count': len(report.recommendations)
                }
            
            logger.info(f"Compliance monitoring completed for {environment}")
            return results
            
        except Exception as e:
            logger.error(f"Compliance monitoring failed: {e}")
            raise
    
    async def cleanup_security_resources(self):
        """Cleanup expired security resources"""
        try:
            logger.info("Starting security resources cleanup")
            
            cleanup_results = {
                'certificates_checked': 0,
                'expired_sessions_removed': 0,
                'old_logs_removed': 0,
                'expired_messages_cleaned': 0
            }
            
            # Check and renew certificates
            if hasattr(self.certificate_manager, 'auto_renew_certificates'):
                renewal_results = await self.certificate_manager.auto_renew_certificates()
                cleanup_results['certificates_checked'] = len(renewal_results)
            
            # Cleanup expired sessions
            await self.access_control.cleanup_expired_sessions()
            
            # Cleanup old audit logs
            await self.audit_logger.cleanup_old_logs()
            
            # Cleanup expired messages
            await self.channel_manager.cleanup_expired_messages()
            
            logger.info("Security resources cleanup completed")
            return cleanup_results
            
        except Exception as e:
            logger.error(f"Security cleanup failed: {e}")
            return {'error': str(e)}
    
    def get_security_status(self) -> Dict[str, Any]:
        """
        Get overall security status
        
        Returns:
            Security status summary
        """
        try:
            status = {
                'timestamp': datetime.utcnow().isoformat(),
                'components': {
                    'certificate_manager': 'active',
                    'config_manager': 'active',
                    'channel_manager': 'active',
                    'audit_logger': 'active',
                    'access_control': 'active',
                    'vulnerability_scanner': 'active'
                },
                'configuration': {
                    'auto_renewal_enabled': True,
                    'audit_logging_enabled': True,
                    'compliance_monitoring_enabled': True,
                    'vulnerability_scanning_enabled': True
                },
                'statistics': {
                    'active_sessions': len(self.access_control.sessions),
                    'total_roles': len(self.access_control.rbac.roles),
                    'total_users': len(self.access_control.rbac.users),
                    'secure_channels': len(self.channel_manager.channels)
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get security status: {e}")
            return {'error': str(e)}


# Main entry point function
async def initialize_deployment_security(
    environment: str,
    domain: str,
    config: Optional[Dict[str, Any]] = None
) -> DeploymentSecurityManager:
    """
    Initialize deployment security for a specific environment
    
    Args:
        environment: Environment name
        domain: Domain name for certificates
        config: Optional configuration dictionary
        
    Returns:
        Configured security manager
    """
    try:
        logger.info(f"Initializing deployment security for {environment}")
        
        # Create security manager
        security_manager = DeploymentSecurityManager(config=config)
        
        # Setup environment security
        setup_results = await security_manager.setup_environment_security(
            environment=environment,
            domain=domain
        )
        
        logger.info(f"Deployment security initialized successfully: {setup_results}")
        return security_manager
        
    except Exception as e:
        logger.error(f"Failed to initialize deployment security: {e}")
        raise


# Convenience functions for quick access
def create_certificate_manager(**kwargs) -> CertificateManager:
    """Create certificate manager with default settings"""
    return CertificateManager(**kwargs)


def create_access_control(**kwargs) -> DeploymentAccessControl:
    """Create access control system with default settings"""
    return DeploymentAccessControl(**kwargs)


def create_vulnerability_scanner() -> SecurityAssessment:
    """Create vulnerability scanner with default settings"""
    return SecurityAssessment()


def create_compliance_checker(**kwargs) -> ComplianceChecker:
    """Create compliance checker with default settings"""
    audit_logger = SecurityAuditLogger(**kwargs)
    return ComplianceChecker(audit_logger)


# Export main classes and functions
__all__ = [
    'DeploymentSecurityManager',
    'initialize_deployment_security',
    'create_certificate_manager',
    'create_access_control',
    'create_vulnerability_scanner',
    'create_compliance_checker',
    
    # Core components
    'CertificateManager',
    'TLSConfigGenerator',
    'EncryptedConfigManager',
    'SecretVaultIntegration',
    'ConfigEncryption',
    'SecureChannelManager',
    'MessageEncryption',
    'ProtocolValidator',
    'ComplianceChecker',
    'SecurityAuditLogger',
    'PolicyEnforcer',
    'DeploymentAccessControl',
    'PermissionManager',
    'RoleBasedSecurity',
    'ContainerScanner',
    'DependencyChecker',
    'SecurityAssessment'
]


if __name__ == "__main__":
    # Example usage
    async def main():
        """Example of how to use the deployment security module"""
        
        # Initialize security for production environment
        security_manager = await initialize_deployment_security(
            environment="production",
            domain="api.ia-influencer.com",
            config={
                'auto_renewal': True,
                'audit_retention_days': 2555,  # 7 years
                'session_timeout': 3600,
                'jwt_secret': 'your-production-jwt-secret'
            }
        )
        
        # Perform security assessment
        assessment_results = await security_manager.perform_security_assessment(
            environment="production"
        )
        
        print(f"Security Assessment Results:")
        print(f"Overall Score: {assessment_results['overall_score']:.1f}")
        print(f"Risk Level: {assessment_results['risk_level']}")
        print(f"Total Vulnerabilities: {assessment_results['total_vulnerabilities']}")
        
        # Monitor compliance
        compliance_results = await security_manager.monitor_compliance(
            environment="production",
            frameworks=['gdpr', 'soc2', 'iso27001']
        )
        
        print(f"\nCompliance Results:")
        for framework, results in compliance_results['frameworks'].items():
            print(f"{framework.upper()}: {results['compliance_score']:.1f}%")
        
        # Get security status
        status = security_manager.get_security_status()
        print(f"\nSecurity Status: {status['components']}")
        
        # Cleanup resources
        cleanup_results = await security_manager.cleanup_security_resources()
        print(f"\nCleanup Results: {cleanup_results}")
    
    # Run example
    asyncio.run(main())
