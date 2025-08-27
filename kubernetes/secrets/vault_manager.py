"""
IA Influencer Agent - Enterprise Vault Manager
Secure HashiCorp Vault integration for secrets management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import os
import logging
import hvac
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pathlib import Path
import json
import base64
from cryptography.fernet import Fernet
from kubernetes import client, config
import ssl
import certifi

from .config import SecretsConfig
from .utils import SecurityUtils, ValidationUtils

logger = logging.getLogger(__name__)


class VaultManager:
    """
    Enterprise-grade HashiCorp Vault manager for secure secrets operations.
    
    Provides comprehensive vault operations including:
    - Multi-environment secret management
    - Dynamic secret generation
    - Policy management
    - Audit logging
    - High availability support
    """
    
    def __init__(
        self,
        vault_url: str = None,
        vault_token: str = None,
        auth_method: str = "token",
        namespace: str = None,
        verify_ssl: bool = True,
        ca_cert: str = None,
        client_cert: str = None,
        client_key: str = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize Vault manager with enterprise configuration.
        
        Args:
            vault_url: Vault server URL
            vault_token: Vault authentication token
            auth_method: Authentication method (token, kubernetes, aws, ldap)
            namespace: Vault namespace for enterprise installations
            verify_ssl: Enable SSL certificate verification
            ca_cert: Custom CA certificate path
            client_cert: Client certificate for mutual TLS
            client_key: Client private key for mutual TLS
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
        """
        self.config = SecretsConfig()
        self.vault_url = vault_url or self.config.vault_url
        self.namespace = namespace or self.config.vault_namespace
        self.auth_method = auth_method or self.config.vault_auth_method
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Initialize Vault client
        self.client = self._initialize_client(
            vault_token, ca_cert, client_cert, client_key
        )
        
        # Authenticate with Vault
        self._authenticate()
        
        # Initialize security utilities
        self.security = SecurityUtils()
        self.validator = ValidationUtils()
        
        logger.info(f"VaultManager initialized for {self.vault_url}")
    
    def _initialize_client(
        self,
        vault_token: str,
        ca_cert: str,
        client_cert: str,
        client_key: str
    ) -> hvac.Client:
        """Initialize HashiCorp Vault client with security configuration."""
        try:
            # Configure SSL/TLS
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            if ca_cert:
                ssl_context.load_verify_locations(ca_cert)
            if client_cert and client_key:
                ssl_context.load_cert_chain(client_cert, client_key)
            
            # Create Vault client
            client = hvac.Client(
                url=self.vault_url,
                token=vault_token or self.config.vault_token,
                verify=ssl_context if self.verify_ssl else False,
                namespace=self.namespace,
                timeout=self.timeout
            )
            
            return client
            
        except Exception as e:
            logger.error(f"Failed to initialize Vault client: {e}")
            raise
    
    def _authenticate(self) -> bool:
        """Authenticate with Vault using configured method."""
        try:
            if self.auth_method == "kubernetes":
                return self._authenticate_kubernetes()
            elif self.auth_method == "aws":
                return self._authenticate_aws()
            elif self.auth_method == "ldap":
                return self._authenticate_ldap()
            elif self.auth_method == "token":
                return self._authenticate_token()
            else:
                raise ValueError(f"Unsupported auth method: {self.auth_method}")
                
        except Exception as e:
            logger.error(f"Vault authentication failed: {e}")
            raise
    
    def _authenticate_kubernetes(self) -> bool:
        """Authenticate using Kubernetes service account."""
        try:
            # Load Kubernetes configuration
            if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount'):
                config.load_incluster_config()
            else:
                config.load_kube_config()
            
            # Read service account token
            token_path = '/var/run/secrets/kubernetes.io/serviceaccount/token'
            if os.path.exists(token_path):
                with open(token_path, 'r') as f:
                    jwt_token = f.read().strip()
            else:
                jwt_token = self.config.kubernetes_token
            
            # Authenticate with Vault
            result = self.client.auth.kubernetes.login(
                role=self.config.vault_role,
                jwt=jwt_token
            )
            
            self.client.token = result['auth']['client_token']
            logger.info("Kubernetes authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Kubernetes authentication failed: {e}")
            return False
    
    def _authenticate_aws(self) -> bool:
        """Authenticate using AWS IAM."""
        try:
            import boto3
            
            # Get AWS credentials
            session = boto3.Session()
            credentials = session.get_credentials()
            
            # Authenticate with Vault
            result = self.client.auth.aws.iam_login(
                access_key=credentials.access_key,
                secret_key=credentials.secret_key,
                session_token=credentials.token,
                role=self.config.vault_role
            )
            
            self.client.token = result['auth']['client_token']
            logger.info("AWS IAM authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"AWS authentication failed: {e}")
            return False
    
    def _authenticate_ldap(self) -> bool:
        """Authenticate using LDAP credentials."""
        try:
            result = self.client.auth.ldap.login(
                username=self.config.ldap_username,
                password=self.config.ldap_password
            )
            
            self.client.token = result['auth']['client_token']
            logger.info("LDAP authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"LDAP authentication failed: {e}")
            return False
    
    def _authenticate_token(self) -> bool:
        """Authenticate using token method."""
        try:
            if self.client.is_authenticated():
                logger.info("Token authentication successful")
                return True
            else:
                logger.error("Token authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Token authentication failed: {e}")
            return False
    
    def store_secret(
        self,
        path: str,
        secret_data: Dict[str, Any],
        metadata: Dict[str, Any] = None,
        version: int = None
    ) -> bool:
        """
        Store secret in Vault with metadata and versioning.
        
        Args:
            path: Secret path in Vault
            secret_data: Secret data to store
            metadata: Optional metadata for the secret
            version: Specific version to update (KV v2 only)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate inputs
            if not self.validator.validate_secret_path(path):
                raise ValueError(f"Invalid secret path: {path}")
            
            if not self.validator.validate_secret_data(secret_data):
                raise ValueError("Invalid secret data format")
            
            # Encrypt sensitive data
            encrypted_data = self.security.encrypt_secret_data(secret_data)
            
            # Prepare secret with metadata
            secret_payload = {
                'data': encrypted_data,
                'metadata': {
                    'created_by': self.config.service_account,
                    'created_at': datetime.utcnow().isoformat(),
                    'encrypted': True,
                    'version_info': metadata or {}
                }
            }
            
            # Store in Vault
            if self.config.vault_kv_version == 2:
                response = self.client.secrets.kv.v2.create_or_update_secret(
                    path=path,
                    secret=secret_payload,
                    cas=version
                )
            else:
                response = self.client.secrets.kv.v1.create_or_update_secret(
                    path=path,
                    secret=secret_payload
                )
            
            # Log audit trail
            self._log_audit_event('secret_stored', path, success=True)
            
            logger.info(f"Secret stored successfully at path: {path}")
            return True
            
        except Exception as e:
            self._log_audit_event('secret_stored', path, success=False, error=str(e))
            logger.error(f"Failed to store secret at {path}: {e}")
            return False
    
    def get_secret(
        self,
        path: str,
        version: int = None,
        decrypt: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve secret from Vault with automatic decryption.
        
        Args:
            path: Secret path in Vault
            version: Specific version to retrieve (KV v2 only)
            decrypt: Whether to decrypt the secret data
            
        Returns:
            dict: Secret data or None if not found
        """
        try:
            # Validate path
            if not self.validator.validate_secret_path(path):
                raise ValueError(f"Invalid secret path: {path}")
            
            # Retrieve from Vault
            if self.config.vault_kv_version == 2:
                response = self.client.secrets.kv.v2.read_secret_version(
                    path=path,
                    version=version
                )
                secret_data = response['data']['data']
            else:
                response = self.client.secrets.kv.v1.read_secret(path=path)
                secret_data = response['data']
            
            # Decrypt if needed
            if decrypt and secret_data.get('metadata', {}).get('encrypted'):
                decrypted_data = self.security.decrypt_secret_data(
                    secret_data['data']
                )
                secret_data['data'] = decrypted_data
            
            # Log audit trail
            self._log_audit_event('secret_retrieved', path, success=True)
            
            logger.debug(f"Secret retrieved successfully from path: {path}")
            return secret_data
            
        except hvac.exceptions.InvalidPath:
            logger.warning(f"Secret not found at path: {path}")
            return None
        except Exception as e:
            self._log_audit_event('secret_retrieved', path, success=False, error=str(e))
            logger.error(f"Failed to retrieve secret from {path}: {e}")
            return None
    
    def delete_secret(
        self,
        path: str,
        versions: List[int] = None,
        permanent: bool = False
    ) -> bool:
        """
        Delete secret from Vault with optional version control.
        
        Args:
            path: Secret path in Vault
            versions: Specific versions to delete (KV v2 only)
            permanent: Whether to permanently destroy the secret
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate path
            if not self.validator.validate_secret_path(path):
                raise ValueError(f"Invalid secret path: {path}")
            
            # Delete from Vault
            if self.config.vault_kv_version == 2:
                if permanent:
                    response = self.client.secrets.kv.v2.destroy_secret_versions(
                        path=path,
                        versions=versions or [1]
                    )
                else:
                    response = self.client.secrets.kv.v2.delete_secret_versions(
                        path=path,
                        versions=versions or [1]
                    )
            else:
                response = self.client.secrets.kv.v1.delete_secret(path=path)
            
            # Log audit trail
            action = 'secret_destroyed' if permanent else 'secret_deleted'
            self._log_audit_event(action, path, success=True)
            
            logger.info(f"Secret {'destroyed' if permanent else 'deleted'} at path: {path}")
            return True
            
        except Exception as e:
            action = 'secret_destroyed' if permanent else 'secret_deleted'
            self._log_audit_event(action, path, success=False, error=str(e))
            logger.error(f"Failed to delete secret at {path}: {e}")
            return False
    
    def list_secrets(
        self,
        path: str = "",
        recursive: bool = True
    ) -> List[str]:
        """
        List secrets at specified path.
        
        Args:
            path: Base path to list secrets from
            recursive: Whether to list recursively
            
        Returns:
            list: List of secret paths
        """
        try:
            # List secrets
            if self.config.vault_kv_version == 2:
                response = self.client.secrets.kv.v2.list_secrets(path=path)
            else:
                response = self.client.secrets.kv.v1.list_secrets(path=path)
            
            secret_paths = response['data']['keys']
            
            # Handle recursive listing
            if recursive:
                all_paths = []
                for secret_path in secret_paths:
                    if secret_path.endswith('/'):
                        # Directory, recurse into it
                        subdirectory_path = f"{path}/{secret_path}".strip('/')
                        sub_paths = self.list_secrets(subdirectory_path, recursive=True)
                        all_paths.extend(sub_paths)
                    else:
                        # File
                        full_path = f"{path}/{secret_path}".strip('/')
                        all_paths.append(full_path)
                secret_paths = all_paths
            
            # Log audit trail
            self._log_audit_event('secrets_listed', path, success=True)
            
            logger.debug(f"Listed {len(secret_paths)} secrets at path: {path}")
            return secret_paths
            
        except Exception as e:
            self._log_audit_event('secrets_listed', path, success=False, error=str(e))
            logger.error(f"Failed to list secrets at {path}: {e}")
            return []
    
    def create_policy(
        self,
        policy_name: str,
        policy_rules: str,
        description: str = None
    ) -> bool:
        """
        Create or update Vault policy.
        
        Args:
            policy_name: Name of the policy
            policy_rules: HCL policy rules
            description: Optional policy description
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate policy
            if not self.validator.validate_policy_name(policy_name):
                raise ValueError(f"Invalid policy name: {policy_name}")
            
            # Create policy
            self.client.sys.create_or_update_policy(
                name=policy_name,
                policy=policy_rules
            )
            
            # Log audit trail
            self._log_audit_event('policy_created', policy_name, success=True)
            
            logger.info(f"Policy created: {policy_name}")
            return True
            
        except Exception as e:
            self._log_audit_event('policy_created', policy_name, success=False, error=str(e))
            logger.error(f"Failed to create policy {policy_name}: {e}")
            return False
    
    def generate_database_credentials(
        self,
        db_role: str,
        ttl: str = "1h"
    ) -> Optional[Dict[str, str]]:
        """
        Generate dynamic database credentials.
        
        Args:
            db_role: Database role name
            ttl: Time-to-live for credentials
            
        Returns:
            dict: Generated credentials or None if failed
        """
        try:
            # Generate dynamic credentials
            response = self.client.secrets.database.generate_credentials(
                name=db_role,
                ttl=ttl
            )
            
            credentials = {
                'username': response['data']['username'],
                'password': response['data']['password'],
                'lease_id': response['lease_id'],
                'lease_duration': response['lease_duration']
            }
            
            # Log audit trail
            self._log_audit_event('db_credentials_generated', db_role, success=True)
            
            logger.info(f"Database credentials generated for role: {db_role}")
            return credentials
            
        except Exception as e:
            self._log_audit_event('db_credentials_generated', db_role, success=False, error=str(e))
            logger.error(f"Failed to generate database credentials for {db_role}: {e}")
            return None
    
    def renew_lease(
        self,
        lease_id: str,
        increment: int = None
    ) -> bool:
        """
        Renew a lease for dynamic secrets.
        
        Args:
            lease_id: Lease ID to renew
            increment: Lease renewal increment in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = self.client.sys.renew_lease(
                lease_id=lease_id,
                increment=increment
            )
            
            # Log audit trail
            self._log_audit_event('lease_renewed', lease_id, success=True)
            
            logger.info(f"Lease renewed: {lease_id}")
            return True
            
        except Exception as e:
            self._log_audit_event('lease_renewed', lease_id, success=False, error=str(e))
            logger.error(f"Failed to renew lease {lease_id}: {e}")
            return False
    
    def revoke_lease(
        self,
        lease_id: str
    ) -> bool:
        """
        Revoke a lease for dynamic secrets.
        
        Args:
            lease_id: Lease ID to revoke
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.client.sys.revoke_lease(lease_id=lease_id)
            
            # Log audit trail
            self._log_audit_event('lease_revoked', lease_id, success=True)
            
            logger.info(f"Lease revoked: {lease_id}")
            return True
            
        except Exception as e:
            self._log_audit_event('lease_revoked', lease_id, success=False, error=str(e))
            logger.error(f"Failed to revoke lease {lease_id}: {e}")
            return False
    
    def get_vault_status(self) -> Dict[str, Any]:
        """
        Get Vault cluster status and health information.
        
        Returns:
            dict: Vault status information
        """
        try:
            status = {
                'initialized': self.client.sys.is_initialized(),
                'sealed': self.client.sys.is_sealed(),
                'authenticated': self.client.is_authenticated(),
                'health': self.client.sys.read_health_status(),
                'leader': self.client.sys.read_leader_status()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get Vault status: {e}")
            return {}
    
    def backup_secrets(
        self,
        backup_path: str,
        encryption_key: str = None
    ) -> bool:
        """
        Backup all secrets to encrypted file.
        
        Args:
            backup_path: Path to store backup file
            encryption_key: Optional encryption key for backup
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get all secrets
            all_secrets = {}
            secret_paths = self.list_secrets("", recursive=True)
            
            for path in secret_paths:
                secret_data = self.get_secret(path, decrypt=False)
                if secret_data:
                    all_secrets[path] = secret_data
            
            # Create backup payload
            backup_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'vault_url': self.vault_url,
                'total_secrets': len(all_secrets),
                'secrets': all_secrets
            }
            
            # Encrypt backup if key provided
            if encryption_key:
                backup_content = self.security.encrypt_data(
                    json.dumps(backup_data).encode(),
                    encryption_key
                )
            else:
                backup_content = json.dumps(backup_data, indent=2).encode()
            
            # Write backup file
            with open(backup_path, 'wb') as f:
                f.write(backup_content)
            
            # Log audit trail
            self._log_audit_event('secrets_backup', backup_path, success=True)
            
            logger.info(f"Secrets backup completed: {backup_path}")
            return True
            
        except Exception as e:
            self._log_audit_event('secrets_backup', backup_path, success=False, error=str(e))
            logger.error(f"Failed to backup secrets: {e}")
            return False
    
    def _log_audit_event(
        self,
        action: str,
        resource: str,
        success: bool,
        error: str = None,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Log audit events for compliance and security monitoring."""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,
            'resource': resource,
            'success': success,
            'user': self.config.service_account,
            'client_ip': self.security.get_client_ip(),
            'vault_url': self.vault_url,
            'namespace': self.namespace,
            'error': error,
            'metadata': metadata or {}
        }
        
        # Log to file and external systems
        logger.info(f"AUDIT: {json.dumps(audit_entry)}")
        
        # Send to external audit systems if configured
        if self.config.audit_webhook_url:
            self.security.send_audit_webhook(audit_entry)


class VaultHealthChecker:
    """Health checker for Vault cluster monitoring."""
    
    def __init__(self, vault_manager: VaultManager):
        self.vault = vault_manager
        
    def check_health(self) -> Dict[str, Any]:
        """Comprehensive Vault health check."""
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # Check Vault connectivity
        try:
            self.vault.client.sys.read_health_status()
            health_status['checks']['connectivity'] = 'ok'
        except Exception as e:
            health_status['checks']['connectivity'] = f'failed: {e}'
            health_status['overall_status'] = 'unhealthy'
        
        # Check authentication
        try:
            if self.vault.client.is_authenticated():
                health_status['checks']['authentication'] = 'ok'
            else:
                health_status['checks']['authentication'] = 'failed: not authenticated'
                health_status['overall_status'] = 'unhealthy'
        except Exception as e:
            health_status['checks']['authentication'] = f'failed: {e}'
            health_status['overall_status'] = 'unhealthy'
        
        # Check seal status
        try:
            if not self.vault.client.sys.is_sealed():
                health_status['checks']['seal_status'] = 'ok'
            else:
                health_status['checks']['seal_status'] = 'failed: vault is sealed'
                health_status['overall_status'] = 'unhealthy'
        except Exception as e:
            health_status['checks']['seal_status'] = f'failed: {e}'
            health_status['overall_status'] = 'unhealthy'
        
        return health_status


class InfluencerVaultManager(VaultManager):
    """
    Specialized Vault manager for IA Influencer Agent platform.
    
    Handles secrets for:
    - AI processing engines
    - Content protection algorithms
    - Multi-platform API credentials  
    - Monetization payment systems
    - Content fingerprinting services
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.influencer_secrets_path = "ia-influencer"
        self.api_credentials_path = f"{self.influencer_secrets_path}/apis"
        self.ai_models_path = f"{self.influencer_secrets_path}/ai-models"
        self.protection_keys_path = f"{self.influencer_secrets_path}/protection"
        self.payment_secrets_path = f"{self.influencer_secrets_path}/payments"
        self.fingerprint_keys_path = f"{self.influencer_secrets_path}/fingerprinting"
        
        logger.info("InfluencerVaultManager initialized for IA platform")
    
    def store_platform_api_credentials(
        self,
        platform: str,
        credentials: Dict[str, str],
        permissions: List[str] = None
    ) -> bool:
        """
        Store API credentials for social media platforms.
        
        Args:
            platform: Platform name (youtube, instagram, tiktok, spotify, etc.)
            credentials: API credentials dictionary
            permissions: Required permissions list
            
        Returns:
            bool: Success status
        """
        try:
            path = f"{self.api_credentials_path}/{platform}"
            
            # Validate platform-specific credentials
            if not self._validate_platform_credentials(platform, credentials):
                raise ValueError(f"Invalid credentials for platform: {platform}")
            
            # Enhance with metadata
            enhanced_data = {
                **credentials,
                'platform': platform,
                'permissions': permissions or [],
                'last_validated': datetime.utcnow().isoformat(),
                'rotation_interval': self._get_platform_rotation_interval(platform)
            }
            
            metadata = {
                'platform': platform,
                'credential_type': 'api_access',
                'scope': permissions,
                'compliance_level': self._get_platform_compliance_level(platform)
            }
            
            return self.store_secret(path, enhanced_data, metadata)
            
        except Exception as e:
            logger.error(f"Failed to store {platform} API credentials: {e}")
            return False
    
    def get_platform_api_credentials(
        self,
        platform: str,
        validate_permissions: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve and validate platform API credentials.
        
        Args:
            platform: Platform name
            validate_permissions: Check if credentials have required permissions
            
        Returns:
            Validated credentials or None
        """
        try:
            path = f"{self.api_credentials_path}/{platform}"
            credentials = self.get_secret(path)
            
            if not credentials:
                return None
            
            # Validate credentials are still active
            if validate_permissions:
                if not self._validate_credential_permissions(platform, credentials):
                    logger.warning(f"Invalid permissions for {platform} credentials")
                    return None
            
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to get {platform} credentials: {e}")
            return None
    
    def store_ai_model_secrets(
        self,
        model_name: str,
        api_keys: Dict[str, str],
        model_config: Dict[str, Any] = None
    ) -> bool:
        """
        Store AI model API keys and configurations.
        
        Args:
            model_name: AI model identifier (openai, anthropic, huggingface, etc.)
            api_keys: API keys and authentication tokens
            model_config: Model-specific configuration
            
        Returns:
            bool: Success status
        """
        try:
            path = f"{self.ai_models_path}/{model_name}"
            
            enhanced_data = {
                **api_keys,
                'model_name': model_name,
                'config': model_config or {},
                'rate_limits': self._get_model_rate_limits(model_name),
                'usage_tracking': True,
                'cost_monitoring': True
            }
            
            metadata = {
                'model_type': model_name,
                'provider': self._get_model_provider(model_name),
                'capabilities': self._get_model_capabilities(model_name),
                'cost_tier': self._get_model_cost_tier(model_name)
            }
            
            return self.store_secret(path, enhanced_data, metadata)
            
        except Exception as e:
            logger.error(f"Failed to store AI model secrets for {model_name}: {e}")
            return False
    
    def store_content_protection_keys(
        self,
        protection_type: str,
        encryption_keys: Dict[str, str],
        algorithm_config: Dict[str, Any] = None
    ) -> bool:
        """
        Store content protection encryption keys and fingerprint secrets.
        
        Args:
            protection_type: Type of protection (audio, video, image, text)
            encryption_keys: Encryption keys for content protection
            algorithm_config: Algorithm-specific configuration
            
        Returns:
            bool: Success status
        """
        try:
            path = f"{self.protection_keys_path}/{protection_type}"
            
            enhanced_data = {
                **encryption_keys,
                'protection_type': protection_type,
                'algorithm_config': algorithm_config or {},
                'key_strength': self._get_protection_key_strength(protection_type),
                'rotation_schedule': self._get_protection_rotation_schedule(protection_type)
            }
            
            metadata = {
                'content_type': protection_type,
                'encryption_algorithm': algorithm_config.get('algorithm') if algorithm_config else 'default',
                'security_level': 'high',
                'compliance_frameworks': ['GDPR', 'CCPA', 'SOX']
            }
            
            return self.store_secret(path, enhanced_data, metadata)
            
        except Exception as e:
            logger.error(f"Failed to store protection keys for {protection_type}: {e}")
            return False
    
    def store_payment_processor_secrets(
        self,
        processor: str,
        payment_secrets: Dict[str, str],
        webhook_config: Dict[str, Any] = None
    ) -> bool:
        """
        Store payment processor secrets and webhook configurations.
        
        Args:
            processor: Payment processor (stripe, paypal, wise, etc.)
            payment_secrets: Payment API secrets
            webhook_config: Webhook configuration
            
        Returns:
            bool: Success status
        """
        try:
            path = f"{self.payment_secrets_path}/{processor}"
            
            enhanced_data = {
                **payment_secrets,
                'processor': processor,
                'webhook_config': webhook_config or {},
                'pci_compliance': True,
                'fraud_detection': True,
                'supported_currencies': self._get_processor_currencies(processor)
            }
            
            metadata = {
                'payment_processor': processor,
                'compliance_level': 'PCI_DSS_L1',
                'transaction_limits': self._get_processor_limits(processor),
                'regional_support': self._get_processor_regions(processor)
            }
            
            return self.store_secret(path, enhanced_data, metadata)
            
        except Exception as e:
            logger.error(f"Failed to store payment secrets for {processor}: {e}")
            return False
    
    def store_fingerprinting_secrets(
        self,
        fingerprint_engine: str,
        algorithm_keys: Dict[str, str],
        vector_config: Dict[str, Any] = None
    ) -> bool:
        """
        Store fingerprinting algorithm secrets and vector database keys.
        
        Args:
            fingerprint_engine: Fingerprinting engine (chromaprint, opencv, clip, etc.)
            algorithm_keys: Algorithm-specific keys and secrets
            vector_config: Vector database configuration
            
        Returns:
            bool: Success status
        """
        try:
            path = f"{self.fingerprint_keys_path}/{fingerprint_engine}"
            
            enhanced_data = {
                **algorithm_keys,
                'engine': fingerprint_engine,
                'vector_config': vector_config or {},
                'similarity_threshold': self._get_similarity_threshold(fingerprint_engine),
                'batch_processing': True,
                'real_time_matching': True
            }
            
            metadata = {
                'fingerprint_type': fingerprint_engine,
                'accuracy_level': self._get_fingerprint_accuracy(fingerprint_engine),
                'processing_speed': self._get_fingerprint_speed(fingerprint_engine),
                'supported_formats': self._get_supported_formats(fingerprint_engine)
            }
            
            return self.store_secret(path, enhanced_data, metadata)
            
        except Exception as e:
            logger.error(f"Failed to store fingerprinting secrets for {fingerprint_engine}: {e}")
            return False
    
    def get_all_platform_credentials(self) -> Dict[str, Dict[str, Any]]:
        """Get all platform API credentials."""
        try:
            credentials = {}
            platforms = self.list_secrets(self.api_credentials_path)
            
            for platform in platforms:
                creds = self.get_platform_api_credentials(platform)
                if creds:
                    credentials[platform] = creds
            
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to get all platform credentials: {e}")
            return {}
    
    def rotate_platform_credentials(
        self,
        platform: str,
        new_credentials: Dict[str, str]
    ) -> bool:
        """
        Rotate platform API credentials with validation.
        
        Args:
            platform: Platform name
            new_credentials: New credentials to store
            
        Returns:
            bool: Success status
        """
        try:
            # Validate new credentials
            if not self._validate_platform_credentials(platform, new_credentials):
                raise ValueError(f"Invalid new credentials for {platform}")
            
            # Test new credentials before rotation
            if not self._test_platform_credentials(platform, new_credentials):
                raise ValueError(f"New credentials for {platform} failed validation")
            
            # Get current permissions
            current_creds = self.get_platform_api_credentials(platform, validate_permissions=False)
            permissions = current_creds.get('permissions', []) if current_creds else []
            
            # Store new credentials
            success = self.store_platform_api_credentials(platform, new_credentials, permissions)
            
            if success:
                logger.info(f"Successfully rotated credentials for {platform}")
                # Log rotation event
                self._log_audit_event(
                    'credential_rotation',
                    f"{self.api_credentials_path}/{platform}",
                    success=True,
                    metadata={'platform': platform}
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to rotate credentials for {platform}: {e}")
            self._log_audit_event(
                'credential_rotation',
                f"{self.api_credentials_path}/{platform}",
                success=False,
                error=str(e),
                metadata={'platform': platform}
            )
            return False
    
    # Platform-specific validation methods
    def _validate_platform_credentials(self, platform: str, credentials: Dict[str, str]) -> bool:
        """Validate platform-specific credential format."""
        required_fields = {
            'youtube': ['api_key', 'client_id', 'client_secret'],
            'instagram': ['access_token', 'app_id', 'app_secret'],
            'tiktok': ['access_token', 'client_key', 'client_secret'],
            'spotify': ['client_id', 'client_secret', 'redirect_uri'],
            'twitter': ['api_key', 'api_secret', 'access_token', 'access_token_secret'],
            'facebook': ['app_id', 'app_secret', 'access_token'],
            'linkedin': ['client_id', 'client_secret', 'access_token'],
            'twitch': ['client_id', 'client_secret', 'access_token']
        }
        
        platform_fields = required_fields.get(platform.lower(), [])
        return all(field in credentials for field in platform_fields)
    
    def _validate_credential_permissions(self, platform: str, credentials: Dict[str, Any]) -> bool:
        """Validate that credentials have required permissions."""
        # Implementation would test actual API calls
        # For now, return True if credentials exist
        return bool(credentials)
    
    def _test_platform_credentials(self, platform: str, credentials: Dict[str, str]) -> bool:
        """Test platform credentials with actual API calls."""
        # Implementation would make test API calls
        # For now, return True if credentials are properly formatted
        return self._validate_platform_credentials(platform, credentials)
    
    def _get_platform_rotation_interval(self, platform: str) -> str:
        """Get recommended rotation interval for platform."""
        intervals = {
            'youtube': '90d',
            'instagram': '60d',
            'tiktok': '60d',
            'spotify': '90d',
            'twitter': '30d',
            'facebook': '60d',
            'linkedin': '90d',
            'twitch': '60d'
        }
        return intervals.get(platform.lower(), '60d')
    
    def _get_platform_compliance_level(self, platform: str) -> str:
        """Get compliance level required for platform."""
        levels = {
            'youtube': 'high',
            'instagram': 'high',
            'tiktok': 'medium',
            'spotify': 'high',
            'twitter': 'medium',
            'facebook': 'high',
            'linkedin': 'medium',
            'twitch': 'medium'
        }
        return levels.get(platform.lower(), 'medium')
    
    def _get_model_rate_limits(self, model_name: str) -> Dict[str, int]:
        """Get rate limits for AI model."""
        limits = {
            'openai': {'requests_per_minute': 3000, 'tokens_per_minute': 250000},
            'anthropic': {'requests_per_minute': 1000, 'tokens_per_minute': 100000},
            'huggingface': {'requests_per_minute': 1000, 'tokens_per_minute': 50000},
            'google': {'requests_per_minute': 2000, 'tokens_per_minute': 200000}
        }
        return limits.get(model_name.lower(), {'requests_per_minute': 500, 'tokens_per_minute': 25000})
    
    def _get_model_provider(self, model_name: str) -> str:
        """Get model provider."""
        providers = {
            'openai': 'OpenAI',
            'anthropic': 'Anthropic',
            'huggingface': 'Hugging Face',
            'google': 'Google Cloud AI'
        }
        return providers.get(model_name.lower(), 'Unknown')
    
    def _get_model_capabilities(self, model_name: str) -> List[str]:
        """Get model capabilities."""
        capabilities = {
            'openai': ['text_generation', 'embeddings', 'fine_tuning', 'moderation'],
            'anthropic': ['text_generation', 'analysis', 'reasoning'],
            'huggingface': ['text_generation', 'embeddings', 'classification', 'translation'],
            'google': ['text_generation', 'embeddings', 'vision', 'multimodal']
        }
        return capabilities.get(model_name.lower(), ['text_generation'])
    
    def _get_model_cost_tier(self, model_name: str) -> str:
        """Get model cost tier."""
        tiers = {
            'openai': 'premium',
            'anthropic': 'premium',
            'huggingface': 'standard',
            'google': 'premium'
        }
        return tiers.get(model_name.lower(), 'standard')
    
    def _get_protection_key_strength(self, protection_type: str) -> int:
        """Get encryption key strength for protection type."""
        strengths = {
            'audio': 256,
            'video': 256,
            'image': 256,
            'text': 256
        }
        return strengths.get(protection_type.lower(), 256)
    
    def _get_protection_rotation_schedule(self, protection_type: str) -> str:
        """Get rotation schedule for protection keys."""
        schedules = {
            'audio': '30d',
            'video': '30d',
            'image': '30d',
            'text': '30d'
        }
        return schedules.get(protection_type.lower(), '30d')
    
    def _get_processor_currencies(self, processor: str) -> List[str]:
        """Get supported currencies for payment processor."""
        currencies = {
            'stripe': ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY'],
            'paypal': ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF'],
            'wise': ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF', 'SEK', 'DKK'],
            'square': ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY']
        }
        return currencies.get(processor.lower(), ['USD', 'EUR'])
    
    def _get_processor_limits(self, processor: str) -> Dict[str, Any]:
        """Get transaction limits for payment processor."""
        limits = {
            'stripe': {'daily_limit': 1000000, 'transaction_limit': 99999},
            'paypal': {'daily_limit': 10000, 'transaction_limit': 10000},
            'wise': {'daily_limit': 500000, 'transaction_limit': 100000},
            'square': {'daily_limit': 50000, 'transaction_limit': 5000}
        }
        return limits.get(processor.lower(), {'daily_limit': 10000, 'transaction_limit': 1000})
    
    def _get_processor_regions(self, processor: str) -> List[str]:
        """Get supported regions for payment processor."""
        regions = {
            'stripe': ['US', 'EU', 'UK', 'CA', 'AU', 'JP', 'SG'],
            'paypal': ['US', 'EU', 'UK', 'CA', 'AU', 'JP', 'SG', 'IN', 'BR'],
            'wise': ['US', 'EU', 'UK', 'CA', 'AU', 'JP', 'SG', 'IN', 'BR', 'MX'],
            'square': ['US', 'CA', 'AU', 'JP', 'UK']
        }
        return regions.get(processor.lower(), ['US', 'EU'])
    
    def _get_similarity_threshold(self, fingerprint_engine: str) -> float:
        """Get similarity threshold for fingerprinting engine."""
        thresholds = {
            'chromaprint': 0.85,
            'opencv': 0.90,
            'clip': 0.88,
            'bert': 0.82,
            'imagehash': 0.95
        }
        return thresholds.get(fingerprint_engine.lower(), 0.85)
    
    def _get_fingerprint_accuracy(self, fingerprint_engine: str) -> str:
        """Get accuracy level for fingerprinting engine."""
        accuracies = {
            'chromaprint': 'high',
            'opencv': 'very_high',
            'clip': 'high',
            'bert': 'medium',
            'imagehash': 'very_high'
        }
        return accuracies.get(fingerprint_engine.lower(), 'medium')
    
    def _get_fingerprint_speed(self, fingerprint_engine: str) -> str:
        """Get processing speed for fingerprinting engine."""
        speeds = {
            'chromaprint': 'fast',
            'opencv': 'medium',
            'clip': 'medium',
            'bert': 'slow',
            'imagehash': 'very_fast'
        }
        return speeds.get(fingerprint_engine.lower(), 'medium')
    
    def _get_supported_formats(self, fingerprint_engine: str) -> List[str]:
        """Get supported formats for fingerprinting engine."""
        formats = {
            'chromaprint': ['mp3', 'wav', 'flac', 'aac', 'm4a'],
            'opencv': ['mp4', 'avi', 'mov', 'mkv', 'webm'],
            'clip': ['jpg', 'png', 'gif', 'bmp', 'webp'],
            'bert': ['txt', 'md', 'html', 'pdf'],
            'imagehash': ['jpg', 'png', 'gif', 'bmp', 'tiff']
        }
        return formats.get(fingerprint_engine.lower(), [])
