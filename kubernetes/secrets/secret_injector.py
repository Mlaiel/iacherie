"""
IA Influencer Agent - Secret Injector
Runtime secret injection for containers and applications

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import os
import logging
import json
import tempfile
import threading
import time
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import subprocess
import shutil
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from .vault_manager import VaultManager
from .config import SecretsConfig
from .utils import SecurityUtils, KubernetesUtils

logger = logging.getLogger(__name__)


class InjectionMethod(Enum):
    """Secret injection methods."""
    ENVIRONMENT_VARIABLES = "environment_variables"
    FILES = "files"
    VOLUME_MOUNTS = "volume_mounts"
    INIT_CONTAINER = "init_container"
    SIDECAR_CONTAINER = "sidecar_container"
    KUBERNETES_SECRETS = "kubernetes_secrets"


class InjectionStatus(Enum):
    """Injection status."""
    PENDING = "pending"
    INJECTING = "injecting"
    COMPLETED = "completed"
    FAILED = "failed"
    REFRESHING = "refreshing"


@dataclass
class SecretMapping:
    """Secret mapping configuration."""
    vault_path: str
    target_key: str
    target_path: Optional[str] = None
    environment_variable: Optional[str] = None
    file_mode: int = 0o600
    template: Optional[str] = None
    required: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InjectionConfig:
    """Secret injection configuration."""
    application_name: str
    namespace: str = "default"
    method: InjectionMethod = InjectionMethod.ENVIRONMENT_VARIABLES
    secret_mappings: List[SecretMapping] = field(default_factory=list)
    refresh_interval: int = 3600  # seconds
    auto_refresh: bool = True
    notification_webhooks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InjectionResult:
    """Secret injection result."""
    success: bool
    injected_secrets: List[str] = field(default_factory=list)
    failed_secrets: List[str] = field(default_factory=list)
    error: Optional[str] = None
    injection_time: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SecretInjector:
    """
    Enterprise secret injector for runtime secret provisioning with support for
    multiple injection methods, automatic refresh, and Kubernetes integration.
    """
    
    def __init__(
        self,
        vault_manager: VaultManager,
        config: SecretsConfig = None
    ):
        """
        Initialize secret injector.
        
        Args:
            vault_manager: Configured VaultManager instance
            config: Optional secrets configuration
        """
        self.vault = vault_manager
        self.config = config or SecretsConfig()
        self.security = SecurityUtils()
        self.k8s_utils = KubernetesUtils()
        
        # Injection state
        self.injection_configs: Dict[str, InjectionConfig] = {}
        self.active_injections: Dict[str, InjectionResult] = {}
        self.refresh_threads: Dict[str, threading.Thread] = {}
        self.is_running = False
        
        # Initialize Kubernetes client
        self._initialize_kubernetes()
        
        logger.info("SecretInjector initialized")
    
    def register_injection(
        self,
        config: InjectionConfig
    ) -> str:
        """
        Register secret injection configuration.
        
        Args:
            config: Injection configuration
            
        Returns:
            str: Injection ID
        """



        try:
            injection_id = f"{config.application_name}_{config.namespace}"
            self.injection_configs[injection_id] = config
            
            # Start auto-refresh if enabled
            if config.auto_refresh:
                self._start_auto_refresh(injection_id)
            
            logger.info(f"Injection registered: {injection_id}")
            return injection_id
            
        except Exception as e:
            logger.error(f"Failed to register injection: {e}")
            raise
    
    def inject_secrets(
        self,
        injection_id: str,
        force_refresh: bool = False
    ) -> InjectionResult:
        """
        Inject secrets for registered configuration.
        
        Args:
            injection_id: Injection configuration ID
            force_refresh: Force secret refresh even if cached
            
        Returns:
            InjectionResult: Result of injection operation
        """



        try:
            config = self.injection_configs.get(injection_id)
            if not config:
                raise ValueError(f"Injection config not found: {injection_id}")
            
            logger.info(f"Starting secret injection for {injection_id}")
            
            # Retrieve secrets from Vault
            secrets_data = {}
            failed_secrets = []
            
            for mapping in config.secret_mappings:
                try:
                    secret = self.vault.get_secret(mapping.vault_path)
                    if secret:
                        secrets_data[mapping.target_key] = {
                            'data': secret['data'],
                            'mapping': mapping
                        }
                    elif mapping.required:
                        failed_secrets.append(mapping.vault_path)
                        logger.error(f"Required secret not found: {mapping.vault_path}")
                    else:
                        logger.warning(f"Optional secret not found: {mapping.vault_path}")
                        
                except Exception as e:
                    logger.error(f"Failed to retrieve secret {mapping.vault_path}: {e}")
                    if mapping.required:
                        failed_secrets.append(mapping.vault_path)
            
            if failed_secrets:
                return InjectionResult(
                    success=False,
                    failed_secrets=failed_secrets,
                    error=f"Failed to retrieve required secrets: {failed_secrets}"
                )
            
            # Inject secrets based on method
            if config.method == InjectionMethod.ENVIRONMENT_VARIABLES:
                result = self._inject_environment_variables(config, secrets_data)
            elif config.method == InjectionMethod.FILES:
                result = self._inject_files(config, secrets_data)
            elif config.method == InjectionMethod.VOLUME_MOUNTS:
                result = self._inject_volume_mounts(config, secrets_data)
            elif config.method == InjectionMethod.INIT_CONTAINER:
                result = self._inject_init_container(config, secrets_data)
            elif config.method == InjectionMethod.SIDECAR_CONTAINER:
                result = self._inject_sidecar_container(config, secrets_data)
            elif config.method == InjectionMethod.KUBERNETES_SECRETS:
                result = self._inject_kubernetes_secrets(config, secrets_data)
            else:
                raise ValueError(f"Unsupported injection method: {config.method}")
            
            # Store result
            self.active_injections[injection_id] = result
            
            # Send notifications
            if result.success:
                self._send_injection_notification(injection_id, result, "success")
            else:
                self._send_injection_notification(injection_id, result, "failure")
            
            return result
            
        except Exception as e:
            error_result = InjectionResult(
                success=False,
                error=str(e)
            )
            self.active_injections[injection_id] = error_result
            logger.error(f"Secret injection failed for {injection_id}: {e}")
            return error_result
    
    def remove_injection(
        self,
        injection_id: str,
        cleanup: bool = True
    ) -> bool:
        """
        Remove secret injection configuration.
        
        Args:
            injection_id: Injection configuration ID
            cleanup: Whether to clean up injected secrets
            
        Returns:
            bool: True if successful
        """



        try:
            config = self.injection_configs.get(injection_id)
            if not config:
                logger.warning(f"Injection config not found: {injection_id}")
                return False
            
            # Stop auto-refresh
            if injection_id in self.refresh_threads:
                thread = self.refresh_threads[injection_id]
                thread.join(timeout=5)
                del self.refresh_threads[injection_id]
            
            # Cleanup injected secrets
            if cleanup:
                self._cleanup_injection(config)
            
            # Remove from state
            del self.injection_configs[injection_id]
            if injection_id in self.active_injections:
                del self.active_injections[injection_id]
            
            logger.info(f"Injection removed: {injection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove injection {injection_id}: {e}")
            return False
    
    def get_injection_status(self, injection_id: str) -> Optional[Dict[str, Any]]:
        """
        Get injection status.
        
        Args:
            injection_id: Injection configuration ID
            
        Returns:
            dict: Injection status information
        """
        config = self.injection_configs.get(injection_id)
        result = self.active_injections.get(injection_id)
        
        if not config:
            return None
        
        return {
            'injection_id': injection_id,
            'application_name': config.application_name,
            'namespace': config.namespace,
            'method': config.method.value,
            'auto_refresh': config.auto_refresh,
            'refresh_interval': config.refresh_interval,
            'last_injection': result.injection_time.isoformat() if result else None,
            'last_success': result.success if result else None,
            'injected_secrets': result.injected_secrets if result else [],
            'failed_secrets': result.failed_secrets if result else [],
            'error': result.error if result else None
        }
    
    def list_injections(self) -> List[Dict[str, Any]]:
        """
        List all registered injections.
        
        Returns:
            list: List of injection status information
        """



        return [
            self.get_injection_status(injection_id)
            for injection_id in self.injection_configs.keys()
        ]
    
    def _inject_environment_variables(
        self,
        config: InjectionConfig,
        secrets_data: Dict[str, Any]
    ) -> InjectionResult:
        """Inject secrets as environment variables."""



        try:
            injected_secrets = []
            
            for target_key, secret_info in secrets_data.items():
                mapping = secret_info['mapping']
                secret_data = secret_info['data']
                
                if mapping.environment_variable:
                    # Single environment variable
                    env_var = mapping.environment_variable
                    
                    if mapping.template:
                        # Apply template
                        value = self._apply_template(mapping.template, secret_data)
                    else:
                        # Use specific key or entire secret as JSON
                        if mapping.target_key in secret_data:
                            value = str(secret_data[mapping.target_key])
                        else:
                            value = json.dumps(secret_data)
                    
                    os.environ[env_var] = value
                    injected_secrets.append(env_var)
                    
                else:
                    # Multiple environment variables from secret keys
                    for key, value in secret_data.items():
                        env_var = f"{config.application_name.upper()}_{key.upper()}"
                        os.environ[env_var] = str(value)
                        injected_secrets.append(env_var)
            
            return InjectionResult(
                success=True,
                injected_secrets=injected_secrets,
                metadata={'method': 'environment_variables'}
            )
            
        except Exception as e:
            logger.error(f"Environment variable injection failed: {e}")
            return InjectionResult(success=False, error=str(e))
    
    def _inject_files(
        self,
        config: InjectionConfig,
        secrets_data: Dict[str, Any]
    ) -> InjectionResult:
        """Inject secrets as files."""



        try:
            injected_secrets = []
            
            for target_key, secret_info in secrets_data.items():
                mapping = secret_info['mapping']
                secret_data = secret_info['data']
                
                if not mapping.target_path:
                    logger.warning(f"No target path specified for {target_key}")
                    continue
                
                file_path = Path(mapping.target_path)
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Prepare content
                if mapping.template:
                    content = self._apply_template(mapping.template, secret_data)
                elif mapping.target_key in secret_data:
                    content = str(secret_data[mapping.target_key])
                else:
                    content = json.dumps(secret_data, indent=2)
                
                # Write file securely
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    dir=file_path.parent,
                    delete=False
                ) as temp_file:
                    temp_file.write(content)
                    temp_path = temp_file.name
                
                # Set permissions and move to final location
                os.chmod(temp_path, mapping.file_mode)
                shutil.move(temp_path, file_path)
                
                injected_secrets.append(str(file_path))
            
            return InjectionResult(
                success=True,
                injected_secrets=injected_secrets,
                metadata={'method': 'files'}
            )
            
        except Exception as e:
            logger.error(f"File injection failed: {e}")
            return InjectionResult(success=False, error=str(e))
    
    def _inject_volume_mounts(
        self,
        config: InjectionConfig,
        secrets_data: Dict[str, Any]
    ) -> InjectionResult:
        """Inject secrets as volume mounts."""



        try:
            # Create temporary directory for secrets
            secrets_dir = Path(f"/tmp/secrets/{config.application_name}")
            secrets_dir.mkdir(parents=True, exist_ok=True)
            
            injected_secrets = []
            
            for target_key, secret_info in secrets_data.items():
                mapping = secret_info['mapping']
                secret_data = secret_info['data']
                
                file_name = mapping.target_path or f"{target_key}.json"
                file_path = secrets_dir / file_name
                
                # Prepare content
                if mapping.template:
                    content = self._apply_template(mapping.template, secret_data)
                elif mapping.target_key in secret_data:
                    content = str(secret_data[mapping.target_key])
                else:
                    content = json.dumps(secret_data, indent=2)
                
                # Write file
                with open(file_path, 'w') as f:
                    f.write(content)
                
                os.chmod(file_path, mapping.file_mode)
                injected_secrets.append(str(file_path))
            
            return InjectionResult(
                success=True,
                injected_secrets=injected_secrets,
                metadata={
                    'method': 'volume_mounts',
                    'secrets_directory': str(secrets_dir)
                }
            )
            
        except Exception as e:
            logger.error(f"Volume mount injection failed: {e}")
            return InjectionResult(success=False, error=str(e))
    
    def _inject_init_container(
        self,
        config: InjectionConfig,
        secrets_data: Dict[str, Any]
    ) -> InjectionResult:
        """Inject secrets using init container."""



        try:
            # Create init container script
            script_content = self._generate_init_script(config, secrets_data)
            
            # Create ConfigMap for init script
            configmap_name = f"{config.application_name}-secret-init"
            self._create_configmap(
                name=configmap_name,
                namespace=config.namespace,
                data={'init-secrets.sh': script_content}
            )
            
            # Update deployment with init container
            self._add_init_container_to_deployment(config, configmap_name)
            
            return InjectionResult(
                success=True,
                injected_secrets=[configmap_name],
                metadata={
                    'method': 'init_container',
                    'configmap': configmap_name
                }
            )
            
        except Exception as e:
            logger.error(f"Init container injection failed: {e}")
            return InjectionResult(success=False, error=str(e))
    
    def _inject_sidecar_container(
        self,
        config: InjectionConfig,
        secrets_data: Dict[str, Any]
    ) -> InjectionResult:
        """Inject secrets using sidecar container."""



        try:
            # Create sidecar configuration
            sidecar_config = self._generate_sidecar_config(config, secrets_data)
            
            # Update deployment with sidecar container
            self._add_sidecar_container_to_deployment(config, sidecar_config)
            
            return InjectionResult(
                success=True,
                injected_secrets=[f"{config.application_name}-sidecar"],
                metadata={
                    'method': 'sidecar_container',
                    'sidecar_name': f"{config.application_name}-sidecar"
                }
            )
            
        except Exception as e:
            logger.error(f"Sidecar container injection failed: {e}")
            return InjectionResult(success=False, error=str(e))
    
    def _inject_kubernetes_secrets(
        self,
        config: InjectionConfig,
        secrets_data: Dict[str, Any]
    ) -> InjectionResult:
        """Inject secrets as Kubernetes secrets."""



        try:
            injected_secrets = []
            
            # Create Kubernetes secret for each mapping
            for target_key, secret_info in secrets_data.items():
                mapping = secret_info['mapping']
                secret_data = secret_info['data']
                
                secret_name = f"{config.application_name}-{target_key}"
                
                # Prepare secret data
                k8s_secret_data = {}
                if mapping.template:
                    content = self._apply_template(mapping.template, secret_data)
                    k8s_secret_data[mapping.target_key] = content
                else:
                    for key, value in secret_data.items():
                        k8s_secret_data[key] = str(value)
                
                # Create Kubernetes secret
                self._create_kubernetes_secret(
                    name=secret_name,
                    namespace=config.namespace,
                    data=k8s_secret_data
                )
                
                injected_secrets.append(secret_name)
            
            return InjectionResult(
                success=True,
                injected_secrets=injected_secrets,
                metadata={'method': 'kubernetes_secrets'}
            )
            
        except Exception as e:
            logger.error(f"Kubernetes secrets injection failed: {e}")
            return InjectionResult(success=False, error=str(e))
    
    def _apply_template(self, template: str, secret_data: Dict[str, Any]) -> str:
        """Apply template to secret data."""



        try:
            # Simple template replacement
            content = template
            for key, value in secret_data.items():
                placeholder = f"{{{key}}}"
                content = content.replace(placeholder, str(value))
            
            return content
            
        except Exception as e:
            logger.error(f"Template application failed: {e}")
            return json.dumps(secret_data)
    
    def _generate_init_script(
        self,
        config: InjectionConfig,
        secrets_data: Dict[str, Any]
    ) -> str:
        """Generate init container script."""
        script_lines = [
            "#!/bin/bash",
            "set -e",
            "echo 'Initializing secrets...'",
            "",
            "# Create secrets directory",
            "mkdir -p /shared/secrets",
            ""
        ]
        
        for target_key, secret_info in secrets_data.items():
            mapping = secret_info['mapping']
            secret_data = secret_info['data']
            
            file_path = f"/shared/secrets/{mapping.target_path or target_key}"
            
            if mapping.template:
                content = self._apply_template(mapping.template, secret_data)
            else:
                content = json.dumps(secret_data, indent=2)
            
            # Escape content for shell
            escaped_content = content.replace("'", "'\"'\"'")
            
            script_lines.extend([
                f"# Write {target_key}",
                f"cat > '{file_path}' << 'EOF'",
                escaped_content,
                "EOF",
                f"chmod {oct(mapping.file_mode)[2:]} '{file_path}'",
                ""
            ])
        
        script_lines.append("echo 'Secrets initialization completed'")
        
        return '\n'.join(script_lines)
    
    def _generate_sidecar_config(
        self,
        config: InjectionConfig,
        secrets_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate sidecar container configuration."""



        return {
            'name': f"{config.application_name}-sidecar",
            'image': 'alpine:latest',
            'command': ['/bin/sh'],
            'args': ['-c', 'while true; do sleep 3600; done'],
            'volumeMounts': [
                {
                    'name': 'shared-secrets',
                    'mountPath': '/shared/secrets'
                }
            ],
            'env': [
                {
                    'name': 'VAULT_ADDR',
                    'value': self.vault.vault_url
                }
            ]
        }
    
    def _create_configmap(
        self,
        name: str,
        namespace: str,
        data: Dict[str, str]
    ) -> None:
        """Create Kubernetes ConfigMap."""



        try:
            v1 = client.CoreV1Api()
            
            configmap = client.V1ConfigMap(
                metadata=client.V1ObjectMeta(name=name, namespace=namespace),
                data=data
            )
            
            try:
                v1.create_namespaced_config_map(namespace, configmap)
            except ApiException as e:
                if e.status == 409:  # Already exists
                    v1.replace_namespaced_config_map(name, namespace, configmap)
                else:
                    raise
                    
        except Exception as e:
            logger.error(f"Failed to create ConfigMap {name}: {e}")
            raise
    
    def _create_kubernetes_secret(
        self,
        name: str,
        namespace: str,
        data: Dict[str, str]
    ) -> None:
        """Create Kubernetes Secret."""



        try:
            v1 = client.CoreV1Api()
            
            # Encode data to base64
            encoded_data = {}
            for key, value in data.items():
                encoded_data[key] = value.encode('utf-8')
            
            secret = client.V1Secret(
                metadata=client.V1ObjectMeta(name=name, namespace=namespace),
                data=encoded_data,
                type='Opaque'
            )
            
            try:
                v1.create_namespaced_secret(namespace, secret)
            except ApiException as e:
                if e.status == 409:  # Already exists
                    v1.replace_namespaced_secret(name, namespace, secret)
                else:
                    raise
                    
        except Exception as e:
            logger.error(f"Failed to create Kubernetes Secret {name}: {e}")
            raise
    
    def _add_init_container_to_deployment(
        self,
        config: InjectionConfig,
        configmap_name: str
    ) -> None:
        """Add init container to deployment."""



        try:
            apps_v1 = client.AppsV1Api()
            
            # Get current deployment
            deployment = apps_v1.read_namespaced_deployment(
                name=config.application_name,
                namespace=config.namespace
            )
            
            # Add init container
            init_container = client.V1Container(
                name='secret-init',
                image='alpine:latest',
                command=['/bin/sh'],
                args=['/scripts/init-secrets.sh'],
                volume_mounts=[
                    client.V1VolumeMount(
                        name='init-scripts',
                        mount_path='/scripts'
                    ),
                    client.V1VolumeMount(
                        name='shared-secrets',
                        mount_path='/shared'
                    )
                ]
            )
            
            # Add volumes
            volumes = deployment.spec.template.spec.volumes or []
            volumes.extend([
                client.V1Volume(
                    name='init-scripts',
                    config_map=client.V1ConfigMapVolumeSource(
                        name=configmap_name,
                        default_mode=0o755
                    )
                ),
                client.V1Volume(
                    name='shared-secrets',
                    empty_dir=client.V1EmptyDirVolumeSource()
                )
            ])
            
            # Update deployment
            deployment.spec.template.spec.init_containers = [init_container]
            deployment.spec.template.spec.volumes = volumes
            
            apps_v1.replace_namespaced_deployment(
                name=config.application_name,
                namespace=config.namespace,
                body=deployment
            )
            
        except Exception as e:
            logger.error(f"Failed to add init container: {e}")
            raise
    
    def _add_sidecar_container_to_deployment(
        self,
        config: InjectionConfig,
        sidecar_config: Dict[str, Any]
    ) -> None:
        """Add sidecar container to deployment."""



        try:
            apps_v1 = client.AppsV1Api()
            
            # Get current deployment
            deployment = apps_v1.read_namespaced_deployment(
                name=config.application_name,
                namespace=config.namespace
            )
            
            # Create sidecar container
            sidecar_container = client.V1Container(**sidecar_config)
            
            # Add to containers
            containers = list(deployment.spec.template.spec.containers)
            containers.append(sidecar_container)
            deployment.spec.template.spec.containers = containers
            
            # Update deployment
            apps_v1.replace_namespaced_deployment(
                name=config.application_name,
                namespace=config.namespace,
                body=deployment
            )
            
        except Exception as e:
            logger.error(f"Failed to add sidecar container: {e}")
            raise
    
    def _cleanup_injection(self, config: InjectionConfig) -> None:
        """Clean up injected secrets."""



        try:
            if config.method == InjectionMethod.ENVIRONMENT_VARIABLES:
                # Remove environment variables
                for mapping in config.secret_mappings:
                    if mapping.environment_variable and mapping.environment_variable in os.environ:
                        del os.environ[mapping.environment_variable]
                        
            elif config.method == InjectionMethod.FILES:
                # Remove files
                for mapping in config.secret_mappings:
                    if mapping.target_path and Path(mapping.target_path).exists():
                        Path(mapping.target_path).unlink()
                        
            elif config.method == InjectionMethod.KUBERNETES_SECRETS:
                # Delete Kubernetes secrets
                v1 = client.CoreV1Api()
                for mapping in config.secret_mappings:
                    secret_name = f"{config.application_name}-{mapping.target_key}"
                    try:
                        v1.delete_namespaced_secret(secret_name, config.namespace)
                    except ApiException:
                        pass  # Ignore if not found
                        
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def _start_auto_refresh(self, injection_id: str) -> None:
        """Start auto-refresh thread for injection."""
        def refresh_loop():
            config = self.injection_configs[injection_id]
            while injection_id in self.injection_configs:
                try:
                    time.sleep(config.refresh_interval)
                    if injection_id in self.injection_configs:
                        self.inject_secrets(injection_id, force_refresh=True)
                except Exception as e:
                    logger.error(f"Auto-refresh failed for {injection_id}: {e}")
        
        thread = threading.Thread(target=refresh_loop, daemon=True)
        thread.start()
        self.refresh_threads[injection_id] = thread
    
    def _send_injection_notification(
        self,
        injection_id: str,
        result: InjectionResult,
        status: str
    ) -> None:
        """Send injection notification."""



        try:
            config = self.injection_configs[injection_id]
            
            notification_data = {
                'event': 'secret_injection',
                'injection_id': injection_id,
                'application_name': config.application_name,
                'namespace': config.namespace,
                'status': status,
                'method': config.method.value,
                'injected_secrets': result.injected_secrets,
                'failed_secrets': result.failed_secrets,
                'error': result.error,
                'timestamp': result.injection_time.isoformat()
            }
            
            # Send to configured webhooks
            for webhook_url in config.notification_webhooks:
                self.security.send_webhook(webhook_url, notification_data)
                
        except Exception as e:
            logger.error(f"Failed to send injection notification: {e}")
    
    def _initialize_kubernetes(self) -> None:
        """Initialize Kubernetes client."""



        try:
            if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount'):
                # Running inside cluster
                config.load_incluster_config()
            else:
                # Running outside cluster
                config.load_kube_config()
                
            logger.info("Kubernetes client initialized")
            
        except Exception as e:
            logger.warning(f"Kubernetes client initialization failed: {e}")


class SecretTemplate:
    """Template processor for secret injection."""
    
    @staticmethod
    def render_config_file(template_path: str, secrets: Dict[str, Any]) -> str:
        """Render configuration file template with secrets."""



        try:
            with open(template_path, 'r') as f:
                template_content = f.read()
            
            # Simple variable substitution
            for key, value in secrets.items():
                template_content = template_content.replace(f"${{{key}}}", str(value))
                template_content = template_content.replace(f"${key}", str(value))
            
            return template_content
            
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            raise
    
    @staticmethod
    def render_environment_file(secrets: Dict[str, Any], prefix: str = "") -> str:
        """Render environment file with secrets."""
        lines = []
        for key, value in secrets.items():
            env_key = f"{prefix}{key.upper()}" if prefix else key.upper()
            # Escape value if contains special characters
            if any(char in str(value) for char in [' ', '"', "'", '$', '`']):
                escaped_value = str(value).replace('"', '\\"')
                lines.append(f'{env_key}="{escaped_value}"')
            else:
                lines.append(f'{env_key}={value}')
        
        return '\n'.join(lines)
    
    @staticmethod
    def render_json_config(secrets: Dict[str, Any], template: Dict[str, Any] = None) -> str:
        """Render JSON configuration with secrets."""
        if template:
            config = template.copy()
            # Replace placeholders in template
            config_str = json.dumps(config)
            for key, value in secrets.items():
                config_str = config_str.replace(f"${{{key}}}", str(value))
            return json.loads(config_str)
        else:
            return secrets


class InfluencerSecretInjector(SecretInjector):
    """
    Specialized secret injector for IA Influencer Agent platform.
    
    Handles injection of:
    - Platform API credentials
    - AI model access keys
    - Content protection encryption keys
    - Payment processor secrets
    - Fingerprinting algorithm configurations
    """
    
    def __init__(self, vault_manager: VaultManager, config: SecretsConfig = None):
        super().__init__(vault_manager, config)
        self.platform_injection_configs = {}
        self.ai_model_injection_configs = {}
        
        logger.info("InfluencerSecretInjector initialized")
    
    def inject_platform_credentials(
        self,
        application_name: str,
        platform: str,
        namespace: str = "ia-influencer",
        injection_method: InjectionMethod = InjectionMethod.ENVIRONMENT_VARIABLES
    ) -> str:
        """
        Inject platform API credentials for specific application.
        
        Args:
            application_name: Target application name
            platform: Platform name (youtube, instagram, etc.)
            namespace: Kubernetes namespace
            injection_method: Injection method to use
            
        Returns:
            str: Injection configuration ID
        """



        try:
            # Define platform-specific secret mappings
            secret_mappings = self._get_platform_secret_mappings(platform)
            
            # Create injection configuration
            injection_config = InjectionConfig(
                application_name=application_name,
                namespace=namespace,
                method=injection_method,
                secret_mappings=secret_mappings,
                refresh_interval=3600,  # 1 hour
                auto_refresh=True,
                metadata={
                    'platform': platform,
                    'injection_type': 'platform_credentials',
                    'created_by': 'influencer_injector'
                }
            )
            
            # Register and inject
            injection_id = self.register_injection_config(injection_config)
            result = self.inject_secrets(injection_id)
            
            # Store for platform-specific tracking
            self.platform_injection_configs[f"{platform}_{application_name}"] = injection_id
            
            logger.info(f"Platform credentials injected for {platform} -> {application_name}")
            return injection_id
            
        except Exception as e:
            logger.error(f"Failed to inject platform credentials for {platform}: {e}")
            raise
    
    def inject_ai_model_secrets(
        self,
        application_name: str,
        model_names: List[str],
        namespace: str = "ia-influencer",
        injection_method: InjectionMethod = InjectionMethod.FILES
    ) -> str:
        """
        Inject AI model API keys and configurations.
        
        Args:
            application_name: Target application name
            model_names: List of AI model names
            namespace: Kubernetes namespace
            injection_method: Injection method to use
            
        Returns:
            str: Injection configuration ID
        """



        try:
            # Create secret mappings for all AI models
            secret_mappings = []
            
            for model_name in model_names:
                vault_path = f"ia-influencer/ai-models/{model_name}"
                
                # API key mapping
                secret_mappings.append(SecretMapping(
                    vault_path=vault_path,
                    target_key="api_key",
                    target_path=f"/etc/secrets/ai-models/{model_name}/api_key",
                    environment_variable=f"{model_name.upper()}_API_KEY",
                    file_mode=0o600,
                    required=True,
                    metadata={'model': model_name, 'secret_type': 'api_key'}
                ))
                
                # Configuration mapping
                secret_mappings.append(SecretMapping(
                    vault_path=vault_path,
                    target_key="config",
                    target_path=f"/etc/secrets/ai-models/{model_name}/config.json",
                    file_mode=0o644,
                    template="json",
                    required=False,
                    metadata={'model': model_name, 'secret_type': 'config'}
                ))
            
            # Create injection configuration
            injection_config = InjectionConfig(
                application_name=application_name,
                namespace=namespace,
                method=injection_method,
                secret_mappings=secret_mappings,
                refresh_interval=1800,  # 30 minutes
                auto_refresh=True,
                metadata={
                    'models': model_names,
                    'injection_type': 'ai_model_secrets',
                    'created_by': 'influencer_injector'
                }
            )
            
            # Register and inject
            injection_id = self.register_injection_config(injection_config)
            result = self.inject_secrets(injection_id)
            
            # Store for AI model tracking
            self.ai_model_injection_configs[application_name] = injection_id
            
            logger.info(f"AI model secrets injected for {model_names} -> {application_name}")
            return injection_id
            
        except Exception as e:
            logger.error(f"Failed to inject AI model secrets: {e}")
            raise
    
    def inject_content_protection_keys(
        self,
        application_name: str,
        content_types: List[str],
        namespace: str = "ia-influencer",
        user_specific: bool = False
    ) -> str:
        """
        Inject content protection encryption keys.
        
        Args:
            application_name: Target application name
            content_types: List of content types (audio, video, image, text)
            namespace: Kubernetes namespace
            user_specific: Whether to inject user-specific keys
            
        Returns:
            str: Injection configuration ID
        """



        try:
            secret_mappings = []
            
            for content_type in content_types:
                vault_path = f"ia-influencer/protection/{content_type}"
                
                # Main encryption key
                secret_mappings.append(SecretMapping(
                    vault_path=vault_path,
                    target_key="encryption_key",
                    target_path=f"/etc/secrets/protection/{content_type}/encryption.key",
                    file_mode=0o600,
                    required=True,
                    metadata={'content_type': content_type, 'key_type': 'encryption'}
                ))
                
                # Algorithm configuration
                secret_mappings.append(SecretMapping(
                    vault_path=vault_path,
                    target_key="algorithm_config",
                    target_path=f"/etc/secrets/protection/{content_type}/algorithm.json",
                    file_mode=0o644,
                    template="json",
                    required=True,
                    metadata={'content_type': content_type, 'key_type': 'config'}
                ))
                
                if user_specific:
                    # Master key for user-specific derivation
                    secret_mappings.append(SecretMapping(
                        vault_path=vault_path,
                        target_key="master_key",
                        target_path=f"/etc/secrets/protection/{content_type}/master.key",
                        file_mode=0o600,
                        required=True,
                        metadata={'content_type': content_type, 'key_type': 'master'}
                    ))
            
            injection_config = InjectionConfig(
                application_name=application_name,
                namespace=namespace,
                method=InjectionMethod.FILES,
                secret_mappings=secret_mappings,
                refresh_interval=900,  # 15 minutes
                auto_refresh=True,
                metadata={
                    'content_types': content_types,
                    'user_specific': user_specific,
                    'injection_type': 'content_protection_keys',
                    'created_by': 'influencer_injector'
                }
            )
            
            injection_id = self.register_injection_config(injection_config)
            result = self.inject_secrets(injection_id)
            
            logger.info(f"Content protection keys injected for {content_types} -> {application_name}")
            return injection_id
            
        except Exception as e:
            logger.error(f"Failed to inject content protection keys: {e}")
            raise
    
    def inject_payment_processor_secrets(
        self,
        application_name: str,
        processors: List[str],
        namespace: str = "ia-influencer",
        pci_compliant: bool = True
    ) -> str:
        """
        Inject payment processor secrets with PCI compliance.
        
        Args:
            application_name: Target application name
            processors: List of payment processors
            namespace: Kubernetes namespace
            pci_compliant: Enable PCI compliance features
            
        Returns:
            str: Injection configuration ID
        """



        try:
            secret_mappings = []
            
            for processor in processors:
                vault_path = f"ia-influencer/payments/{processor}"
                
                # API credentials
                secret_mappings.append(SecretMapping(
                    vault_path=vault_path,
                    target_key="api_credentials",
                    target_path=f"/etc/secrets/payments/{processor}/credentials.json",
                    file_mode=0o600,
                    template="json",
                    required=True,
                    metadata={'processor': processor, 'secret_type': 'credentials'}
                ))
                
                # Webhook configuration
                secret_mappings.append(SecretMapping(
                    vault_path=vault_path,
                    target_key="webhook_config",
                    target_path=f"/etc/secrets/payments/{processor}/webhooks.json",
                    file_mode=0o644,
                    template="json",
                    required=False,
                    metadata={'processor': processor, 'secret_type': 'webhooks'}
                ))
                
                if pci_compliant:
                    # PCI-specific configurations
                    secret_mappings.append(SecretMapping(
                        vault_path=vault_path,
                        target_key="pci_config",
                        target_path=f"/etc/secrets/payments/{processor}/pci.json",
                        file_mode=0o600,
                        template="json",
                        required=True,
                        metadata={'processor': processor, 'secret_type': 'pci_config'}
                    ))
            
            injection_config = InjectionConfig(
                application_name=application_name,
                namespace=namespace,
                method=InjectionMethod.FILES,
                secret_mappings=secret_mappings,
                refresh_interval=3600,  # 1 hour
                auto_refresh=True,
                metadata={
                    'processors': processors,
                    'pci_compliant': pci_compliant,
                    'injection_type': 'payment_secrets',
                    'created_by': 'influencer_injector'
                }
            )
            
            injection_id = self.register_injection_config(injection_config)
            result = self.inject_secrets(injection_id)
            
            logger.info(f"Payment processor secrets injected for {processors} -> {application_name}")
            return injection_id
            
        except Exception as e:
            logger.error(f"Failed to inject payment processor secrets: {e}")
            raise
    
    def _get_platform_secret_mappings(self, platform: str) -> List[SecretMapping]:
        """Get platform-specific secret mappings."""
        vault_path = f"ia-influencer/apis/{platform}"
        
        # Common mappings for all platforms
        mappings = [
            SecretMapping(
                vault_path=vault_path,
                target_key="api_key",
                environment_variable=f"{platform.upper()}_API_KEY",
                target_path=f"/etc/secrets/platforms/{platform}/api_key",
                required=True,
                metadata={'platform': platform, 'credential_type': 'api_key'}
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="client_id",
                environment_variable=f"{platform.upper()}_CLIENT_ID",
                target_path=f"/etc/secrets/platforms/{platform}/client_id",
                required=True,
                metadata={'platform': platform, 'credential_type': 'client_id'}
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="client_secret",
                environment_variable=f"{platform.upper()}_CLIENT_SECRET",
                target_path=f"/etc/secrets/platforms/{platform}/client_secret",
                required=True,
                metadata={'platform': platform, 'credential_type': 'client_secret'}
            )
        ]
        
        # Platform-specific additional mappings
        platform_specific = {
            'youtube': [
                SecretMapping(
                    vault_path=vault_path,
                    target_key="access_token",
                    environment_variable="YOUTUBE_ACCESS_TOKEN",
                    target_path="/etc/secrets/platforms/youtube/access_token",
                    required=True,
                    metadata={'platform': 'youtube', 'credential_type': 'access_token'}
                ),
                SecretMapping(
                    vault_path=vault_path,
                    target_key="refresh_token",
                    environment_variable="YOUTUBE_REFRESH_TOKEN",
                    target_path="/etc/secrets/platforms/youtube/refresh_token",
                    required=True,
                    metadata={'platform': 'youtube', 'credential_type': 'refresh_token'}
                )
            ],
            'instagram': [
                SecretMapping(
                    vault_path=vault_path,
                    target_key="access_token",
                    environment_variable="INSTAGRAM_ACCESS_TOKEN",
                    target_path="/etc/secrets/platforms/instagram/access_token",
                    required=True,
                    metadata={'platform': 'instagram', 'credential_type': 'access_token'}
                ),
                SecretMapping(
                    vault_path=vault_path,
                    target_key="app_secret",
                    environment_variable="INSTAGRAM_APP_SECRET",
                    target_path="/etc/secrets/platforms/instagram/app_secret",
                    required=True,
                    metadata={'platform': 'instagram', 'credential_type': 'app_secret'}
                )
            ],
            'tiktok': [
                SecretMapping(
                    vault_path=vault_path,
                    target_key="access_token",
                    environment_variable="TIKTOK_ACCESS_TOKEN",
                    target_path="/etc/secrets/platforms/tiktok/access_token",
                    required=True,
                    metadata={'platform': 'tiktok', 'credential_type': 'access_token'}
                ),
                SecretMapping(
                    vault_path=vault_path,
                    target_key="client_key",
                    environment_variable="TIKTOK_CLIENT_KEY",
                    target_path="/etc/secrets/platforms/tiktok/client_key",
                    required=True,
                    metadata={'platform': 'tiktok', 'credential_type': 'client_key'}
                )
            ],
            'spotify': [
                SecretMapping(
                    vault_path=vault_path,
                    target_key="access_token",
                    environment_variable="SPOTIFY_ACCESS_TOKEN",
                    target_path="/etc/secrets/platforms/spotify/access_token",
                    required=True,
                    metadata={'platform': 'spotify', 'credential_type': 'access_token'}
                ),
                SecretMapping(
                    vault_path=vault_path,
                    target_key="refresh_token",
                    environment_variable="SPOTIFY_REFRESH_TOKEN",
                    target_path="/etc/secrets/platforms/spotify/refresh_token",
                    required=True,
                    metadata={'platform': 'spotify', 'credential_type': 'refresh_token'}
                )
            ]
        }
        
        # Add platform-specific mappings
        if platform.lower() in platform_specific:
            mappings.extend(platform_specific[platform.lower()])
        
        return mappings
    
    def bulk_inject_platform_credentials(
        self,
        application_name: str,
        platforms: List[str],
        namespace: str = "ia-influencer"
    ) -> Dict[str, str]:
        """
        Bulk inject credentials for multiple platforms.
        
        Args:
            application_name: Target application name
            platforms: List of platform names
            namespace: Kubernetes namespace
            
        Returns:
            dict: Mapping of platform to injection ID
        """
        injection_ids = {}
        
        for platform in platforms:
            try:
                injection_id = self.inject_platform_credentials(
                    application_name=application_name,
                    platform=platform,
                    namespace=namespace
                )
                injection_ids[platform] = injection_id
                
            except Exception as e:
                logger.error(f"Failed to inject credentials for {platform}: {e}")
                injection_ids[platform] = None
        
        logger.info(f"Bulk platform injection completed: {len(injection_ids)} platforms")
        return injection_ids
    
    def refresh_all_platform_credentials(self) -> Dict[str, bool]:
        """
        Refresh all platform credentials.
        
        Returns:
            dict: Refresh results by platform
        """
        results = {}
        
        for platform_app, injection_id in self.platform_injection_configs.items():
            try:
                result = self.inject_secrets(injection_id, force_refresh=True)
                results[platform_app] = result.success
                
            except Exception as e:
                logger.error(f"Failed to refresh {platform_app}: {e}")
                results[platform_app] = False
        
        return results
    
    def get_platform_injection_status(self) -> Dict[str, Any]:
        """
        Get status of all platform credential injections.
        
        Returns:
            dict: Status information
        """
        status = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_platforms': len(self.platform_injection_configs),
            'platforms': {},
            'overall_health': 'healthy'
        }
        
        for platform_app, injection_id in self.platform_injection_configs.items():
            try:
                if injection_id in self.injection_configs:
                    config = self.injection_configs[injection_id]
                    status['platforms'][platform_app] = {
                        'injection_id': injection_id,
                        'method': config.method.value,
                        'auto_refresh': config.auto_refresh,
                        'refresh_interval': config.refresh_interval,
                        'last_injection': 'active',
                        'namespace': config.namespace
                    }
                else:
                    status['platforms'][platform_app] = {
                        'injection_id': injection_id,
                        'status': 'configuration_missing',
                        'health': 'degraded'
                    }
                    status['overall_health'] = 'degraded'
                    
            except Exception as e:
                status['platforms'][platform_app] = {
                    'injection_id': injection_id,
                    'status': 'error',
                    'error': str(e),
                    'health': 'error'
                }
                status['overall_health'] = 'error'
        
        return status
            return config_str
        else:
            return json.dumps(secrets, indent=2)
    
    @staticmethod
    def render_yaml_config(secrets: Dict[str, Any], template: Dict[str, Any] = None) -> str:
        """Render YAML configuration with secrets."""
        if template:
            config = template.copy()
            # Replace placeholders in template
            config_str = yaml.dump(config)
            for key, value in secrets.items():
                config_str = config_str.replace(f"${{{key}}}", str(value))
            return config_str
        else:
            return yaml.dump(secrets, default_flow_style=False)


class InfluencerSecretInjector(SecretInjector):
    """
    Specialized secret injector for IA Influencer Agent platform.
    
    Handles injection of:
    - Platform API credentials for social media integration
    - AI model access tokens for content processing
    - Payment processor secrets for monetization
    - Content protection keys for fingerprinting
    - User-specific encryption keys
    """
    
    def __init__(self, vault_manager: VaultManager, config: SecretsConfig = None):
        super().__init__(vault_manager, config)
        self.platform_injections = {}
        self.ai_model_injections = {}
        self.user_content_injections = {}
        
        # Platform-specific injection configurations
        self.platform_injection_configs = {
            'youtube': self._create_youtube_injection_config,
            'instagram': self._create_instagram_injection_config,
            'tiktok': self._create_tiktok_injection_config,
            'spotify': self._create_spotify_injection_config,
            'twitter': self._create_twitter_injection_config,
            'facebook': self._create_facebook_injection_config,
            'linkedin': self._create_linkedin_injection_config,
            'twitch': self._create_twitch_injection_config
        }
        
        logger.info("InfluencerSecretInjector initialized")
    
    def inject_platform_credentials(
        self,
        platform: str,
        application_name: str,
        namespace: str = "ia-influencer",
        method: InjectionMethod = InjectionMethod.ENVIRONMENT_VARIABLES,
        user_id: Optional[str] = None
    ) -> str:
        """
        Inject platform API credentials for social media integration.
        
        Args:
            platform: Platform name (youtube, instagram, etc.)
            application_name: Target application name
            namespace: Kubernetes namespace
            method: Injection method
            user_id: Optional user-specific credentials
            
        Returns:
            str: Injection ID
        """



        try:
            # Generate injection ID
            injection_id = f"platform_{platform}_{application_name}"
            if user_id:
                injection_id += f"_{user_id}"
            
            # Create platform-specific injection configuration
            if platform in self.platform_injection_configs:
                injection_config = self.platform_injection_configs[platform](
                    application_name, namespace, method, user_id
                )
            else:
                injection_config = self._create_generic_platform_injection_config(
                    platform, application_name, namespace, method, user_id
                )
            
            # Configure injection
            config_id = self.configure_injection(injection_config)
            
            # Perform injection
            result = self.inject_secrets(config_id)
            
            if result.success:
                self.platform_injections[injection_id] = {
                    'config_id': config_id,
                    'platform': platform,
                    'user_id': user_id,
                    'last_injection': datetime.utcnow(),
                    'status': 'active'
                }
                logger.info(f"Platform credentials injected for {platform}")
            else:
                logger.error(f"Failed to inject {platform} credentials: {result.error}")
            
            return injection_id
            
        except Exception as e:
            logger.error(f"Platform credential injection failed for {platform}: {e}")
            raise
    
    def inject_ai_model_credentials(
        self,
        model_name: str,
        application_name: str,
        namespace: str = "ia-influencer",
        method: InjectionMethod = InjectionMethod.ENVIRONMENT_VARIABLES,
        usage_limits: Dict[str, int] = None
    ) -> str:
        """
        Inject AI model API credentials for content processing.
        
        Args:
            model_name: AI model name (openai, anthropic, etc.)
            application_name: Target application name
            namespace: Kubernetes namespace
            method: Injection method
            usage_limits: Optional usage limits
            
        Returns:
            str: Injection ID
        """



        try:
            injection_id = f"ai_model_{model_name}_{application_name}"
            
            # Create AI model injection configuration
            injection_config = self._create_ai_model_injection_config(
                model_name, application_name, namespace, method, usage_limits
            )
            
            # Configure injection
            config_id = self.configure_injection(injection_config)
            
            # Perform injection
            result = self.inject_secrets(config_id)
            
            if result.success:
                self.ai_model_injections[injection_id] = {
                    'config_id': config_id,
                    'model_name': model_name,
                    'usage_limits': usage_limits,
                    'last_injection': datetime.utcnow(),
                    'status': 'active'
                }
                logger.info(f"AI model credentials injected for {model_name}")
            else:
                logger.error(f"Failed to inject {model_name} credentials: {result.error}")
            
            return injection_id
            
        except Exception as e:
            logger.error(f"AI model credential injection failed for {model_name}: {e}")
            raise
    
    def inject_content_protection_keys(
        self,
        content_type: str,
        application_name: str,
        namespace: str = "ia-influencer",
        method: InjectionMethod = InjectionMethod.FILES,
        user_id: Optional[str] = None
    ) -> str:
        """
        Inject content protection encryption keys.
        
        Args:
            content_type: Type of content (audio, video, image, text)
            application_name: Target application name
            namespace: Kubernetes namespace
            method: Injection method
            user_id: Optional user-specific keys
            
        Returns:
            str: Injection ID
        """



        try:
            injection_id = f"protection_{content_type}_{application_name}"
            if user_id:
                injection_id += f"_{user_id}"
            
            # Create content protection injection configuration
            injection_config = self._create_content_protection_injection_config(
                content_type, application_name, namespace, method, user_id
            )
            
            # Configure injection
            config_id = self.configure_injection(injection_config)
            
            # Perform injection
            result = self.inject_secrets(config_id)
            
            if result.success:
                logger.info(f"Content protection keys injected for {content_type}")
            else:
                logger.error(f"Failed to inject protection keys for {content_type}: {result.error}")
            
            return injection_id
            
        except Exception as e:
            logger.error(f"Content protection injection failed for {content_type}: {e}")
            raise
    
    def inject_payment_secrets(
        self,
        processor: str,
        application_name: str,
        namespace: str = "ia-influencer",
        method: InjectionMethod = InjectionMethod.ENVIRONMENT_VARIABLES
    ) -> str:
        """
        Inject payment processor secrets with PCI compliance.
        
        Args:
            processor: Payment processor name
            application_name: Target application name
            namespace: Kubernetes namespace
            method: Injection method
            
        Returns:
            str: Injection ID
        """



        try:
            injection_id = f"payment_{processor}_{application_name}"
            
            # Create payment injection configuration
            injection_config = self._create_payment_injection_config(
                processor, application_name, namespace, method
            )
            
            # Configure injection
            config_id = self.configure_injection(injection_config)
            
            # Perform injection
            result = self.inject_secrets(config_id)
            
            if result.success:
                logger.info(f"Payment secrets injected for {processor}")
            else:
                logger.error(f"Failed to inject payment secrets for {processor}: {result.error}")
            
            return injection_id
            
        except Exception as e:
            logger.error(f"Payment secret injection failed for {processor}: {e}")
            raise
    
    def inject_user_specific_secrets(
        self,
        user_id: str,
        application_name: str,
        secret_types: List[str],
        namespace: str = "ia-influencer",
        method: InjectionMethod = InjectionMethod.FILES
    ) -> str:
        """
        Inject user-specific secrets for personalized content protection.
        
        Args:
            user_id: User identifier
            application_name: Target application name
            secret_types: Types of secrets to inject
            namespace: Kubernetes namespace
            method: Injection method
            
        Returns:
            str: Injection ID
        """



        try:
            injection_id = f"user_{user_id}_{application_name}"
            
            # Create user-specific injection configuration
            injection_config = self._create_user_injection_config(
                user_id, application_name, secret_types, namespace, method
            )
            
            # Configure injection
            config_id = self.configure_injection(injection_config)
            
            # Perform injection
            result = self.inject_secrets(config_id)
            
            if result.success:
                self.user_content_injections[injection_id] = {
                    'config_id': config_id,
                    'user_id': user_id,
                    'secret_types': secret_types,
                    'last_injection': datetime.utcnow(),
                    'status': 'active'
                }
                logger.info(f"User-specific secrets injected for user {user_id}")
            else:
                logger.error(f"Failed to inject user secrets for {user_id}: {result.error}")
            
            return injection_id
            
        except Exception as e:
            logger.error(f"User secret injection failed for {user_id}: {e}")
            raise
    
    def bulk_inject_platform_credentials(
        self,
        platforms: List[str],
        application_name: str,
        namespace: str = "ia-influencer",
        method: InjectionMethod = InjectionMethod.ENVIRONMENT_VARIABLES
    ) -> Dict[str, str]:
        """
        Bulk inject credentials for multiple platforms.
        
        Args:
            platforms: List of platform names
            application_name: Target application name
            namespace: Kubernetes namespace
            method: Injection method
            
        Returns:
            dict: Mapping of platform to injection ID
        """
        results = {}
        
        try:
            for platform in platforms:
                try:
                    injection_id = self.inject_platform_credentials(
                        platform, application_name, namespace, method
                    )
                    results[platform] = injection_id
                    
                except Exception as e:
                    logger.error(f"Bulk injection failed for {platform}: {e}")
                    results[platform] = None
            
            logger.info(f"Bulk platform injection completed for {len(platforms)} platforms")
            return results
            
        except Exception as e:
            logger.error(f"Bulk platform injection failed: {e}")
            return results
    
    # Platform-specific injection configuration creators
    def _create_youtube_injection_config(
        self,
        application_name: str,
        namespace: str,
        method: InjectionMethod,
        user_id: Optional[str]
    ) -> InjectionConfig:
        """Create YouTube injection configuration."""
        vault_path = f"ia-influencer/apis/youtube"
        if user_id:
            vault_path += f"/{user_id}"
        
        secret_mappings = [
            SecretMapping(
                vault_path=vault_path,
                target_key="client_id",
                environment_variable="YOUTUBE_CLIENT_ID"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="client_secret",
                environment_variable="YOUTUBE_CLIENT_SECRET"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="access_token",
                environment_variable="YOUTUBE_ACCESS_TOKEN"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="refresh_token",
                environment_variable="YOUTUBE_REFRESH_TOKEN"
            )
        ]
        
        return InjectionConfig(
            application_name=application_name,
            namespace=namespace,
            method=method,
            secret_mappings=secret_mappings,
            metadata={
                "platform": "youtube",
                "user_id": user_id,
                "content_type": "platform_credentials"
            }
        )
    
    def _create_instagram_injection_config(
        self,
        application_name: str,
        namespace: str,
        method: InjectionMethod,
        user_id: Optional[str]
    ) -> InjectionConfig:
        """Create Instagram injection configuration."""
        vault_path = f"ia-influencer/apis/instagram"
        if user_id:
            vault_path += f"/{user_id}"
        
        secret_mappings = [
            SecretMapping(
                vault_path=vault_path,
                target_key="app_id",
                environment_variable="INSTAGRAM_APP_ID"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="app_secret",
                environment_variable="INSTAGRAM_APP_SECRET"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="access_token",
                environment_variable="INSTAGRAM_ACCESS_TOKEN"
            )
        ]
        
        return InjectionConfig(
            application_name=application_name,
            namespace=namespace,
            method=method,
            secret_mappings=secret_mappings,
            metadata={
                "platform": "instagram",
                "user_id": user_id,
                "content_type": "platform_credentials"
            }
        )
    
    def _create_tiktok_injection_config(
        self,
        application_name: str,
        namespace: str,
        method: InjectionMethod,
        user_id: Optional[str]
    ) -> InjectionConfig:
        """Create TikTok injection configuration."""
        vault_path = f"ia-influencer/apis/tiktok"
        if user_id:
            vault_path += f"/{user_id}"
        
        secret_mappings = [
            SecretMapping(
                vault_path=vault_path,
                target_key="client_key",
                environment_variable="TIKTOK_CLIENT_KEY"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="client_secret",
                environment_variable="TIKTOK_CLIENT_SECRET"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="access_token",
                environment_variable="TIKTOK_ACCESS_TOKEN"
            )
        ]
        
        return InjectionConfig(
            application_name=application_name,
            namespace=namespace,
            method=method,
            secret_mappings=secret_mappings,
            metadata={
                "platform": "tiktok",
                "user_id": user_id,
                "content_type": "platform_credentials"
            }
        )
    
    def _create_spotify_injection_config(
        self,
        application_name: str,
        namespace: str,
        method: InjectionMethod,
        user_id: Optional[str]
    ) -> InjectionConfig:
        """Create Spotify injection configuration."""
        vault_path = f"ia-influencer/apis/spotify"
        if user_id:
            vault_path += f"/{user_id}"
        
        secret_mappings = [
            SecretMapping(
                vault_path=vault_path,
                target_key="client_id",
                environment_variable="SPOTIFY_CLIENT_ID"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="client_secret",
                environment_variable="SPOTIFY_CLIENT_SECRET"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="access_token",
                environment_variable="SPOTIFY_ACCESS_TOKEN"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="refresh_token",
                environment_variable="SPOTIFY_REFRESH_TOKEN"
            )
        ]
        
        return InjectionConfig(
            application_name=application_name,
            namespace=namespace,
            method=method,
            secret_mappings=secret_mappings,
            metadata={
                "platform": "spotify",
                "user_id": user_id,
                "content_type": "platform_credentials"
            }
        )
    
    def _create_twitter_injection_config(
        self,
        application_name: str,
        namespace: str,
        method: InjectionMethod,
        user_id: Optional[str]
    ) -> InjectionConfig:
        """Create Twitter injection configuration."""
        vault_path = f"ia-influencer/apis/twitter"
        if user_id:
            vault_path += f"/{user_id}"
        
        secret_mappings = [
            SecretMapping(
                vault_path=vault_path,
                target_key="api_key",
                environment_variable="TWITTER_API_KEY"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="api_secret",
                environment_variable="TWITTER_API_SECRET"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="access_token",
                environment_variable="TWITTER_ACCESS_TOKEN"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="access_token_secret",
                environment_variable="TWITTER_ACCESS_TOKEN_SECRET"
            )
        ]
        
        return InjectionConfig(
            application_name=application_name,
            namespace=namespace,
            method=method,
            secret_mappings=secret_mappings,
            metadata={
                "platform": "twitter",
                "user_id": user_id,
                "content_type": "platform_credentials"
            }
        )
    
    def _create_facebook_injection_config(
        self,
        application_name: str,
        namespace: str,
        method: InjectionMethod,
        user_id: Optional[str]
    ) -> InjectionConfig:
        """Create Facebook injection configuration."""
        vault_path = f"ia-influencer/apis/facebook"
        if user_id:
            vault_path += f"/{user_id}"
        
        secret_mappings = [
            SecretMapping(
                vault_path=vault_path,
                target_key="app_id",
                environment_variable="FACEBOOK_APP_ID"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="app_secret",
                environment_variable="FACEBOOK_APP_SECRET"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="access_token",
                environment_variable="FACEBOOK_ACCESS_TOKEN"
            )
        ]
        
        return InjectionConfig(
            application_name=application_name,
            namespace=namespace,
            method=method,
            secret_mappings=secret_mappings,
            metadata={
                "platform": "facebook",
                "user_id": user_id,
                "content_type": "platform_credentials"
            }
        )
    
    def _create_linkedin_injection_config(
        self,
        application_name: str,
        namespace: str,
        method: InjectionMethod,
        user_id: Optional[str]
    ) -> InjectionConfig:
        """Create LinkedIn injection configuration."""
        vault_path = f"ia-influencer/apis/linkedin"
        if user_id:
            vault_path += f"/{user_id}"
        
        secret_mappings = [
            SecretMapping(
                vault_path=vault_path,
                target_key="client_id",
                environment_variable="LINKEDIN_CLIENT_ID"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="client_secret",
                environment_variable="LINKEDIN_CLIENT_SECRET"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="access_token",
                environment_variable="LINKEDIN_ACCESS_TOKEN"
            )
        ]
        
        return InjectionConfig(
            application_name=application_name,
            namespace=namespace,
            method=method,
            secret_mappings=secret_mappings,
            metadata={
                "platform": "linkedin",
                "user_id": user_id,
                "content_type": "platform_credentials"
            }
        )
    
    def _create_twitch_injection_config(
        self,
        application_name: str,
        namespace: str,
        method: InjectionMethod,
        user_id: Optional[str]
    ) -> InjectionConfig:
        """Create Twitch injection configuration."""
        vault_path = f"ia-influencer/apis/twitch"
        if user_id:
            vault_path += f"/{user_id}"
        
        secret_mappings = [
            SecretMapping(
                vault_path=vault_path,
                target_key="client_id",
                environment_variable="TWITCH_CLIENT_ID"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="client_secret",
                environment_variable="TWITCH_CLIENT_SECRET"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="access_token",
                environment_variable="TWITCH_ACCESS_TOKEN"
            )
        ]
        
        return InjectionConfig(
            application_name=application_name,
            namespace=namespace,
            method=method,
            secret_mappings=secret_mappings,
            metadata={
                "platform": "twitch",
                "user_id": user_id,
                "content_type": "platform_credentials"
            }
        )
    
    def _create_generic_platform_injection_config(
        self,
        platform: str,
        application_name: str,
        namespace: str,
        method: InjectionMethod,
        user_id: Optional[str]
    ) -> InjectionConfig:
        """Create generic platform injection configuration."""
        vault_path = f"ia-influencer/apis/{platform}"
        if user_id:
            vault_path += f"/{user_id}"
        
        secret_mappings = [
            SecretMapping(
                vault_path=vault_path,
                target_key="api_key",
                environment_variable=f"{platform.upper()}_API_KEY"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="secret_key",
                environment_variable=f"{platform.upper()}_SECRET_KEY"
            )
        ]
        
        return InjectionConfig(
            application_name=application_name,
            namespace=namespace,
            method=method,
            secret_mappings=secret_mappings,
            metadata={
                "platform": platform,
                "user_id": user_id,
                "content_type": "platform_credentials"
            }
        )
    
    def _create_ai_model_injection_config(
        self,
        model_name: str,
        application_name: str,
        namespace: str,
        method: InjectionMethod,
        usage_limits: Optional[Dict[str, int]]
    ) -> InjectionConfig:
        """Create AI model injection configuration."""
        vault_path = f"ia-influencer/ai-models/{model_name}"
        
        secret_mappings = [
            SecretMapping(
                vault_path=vault_path,
                target_key="api_key",
                environment_variable=f"{model_name.upper()}_API_KEY"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="organization",
                environment_variable=f"{model_name.upper()}_ORGANIZATION",
                required=False
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="endpoint",
                environment_variable=f"{model_name.upper()}_ENDPOINT",
                required=False
            )
        ]
        
        if usage_limits:
            secret_mappings.append(
                SecretMapping(
                    vault_path="config/usage_limits",
                    target_key="limits",
                    target_path="/etc/ia-influencer/usage_limits.json",
                    template=json.dumps(usage_limits)
                )
            )
        
        return InjectionConfig(
            application_name=application_name,
            namespace=namespace,
            method=method,
            secret_mappings=secret_mappings,
            metadata={
                "model_name": model_name,
                "usage_limits": usage_limits,
                "content_type": "ai_model_credentials"
            }
        )
    
    def _create_content_protection_injection_config(
        self,
        content_type: str,
        application_name: str,
        namespace: str,
        method: InjectionMethod,
        user_id: Optional[str]
    ) -> InjectionConfig:
        """Create content protection injection configuration."""
        vault_path = f"ia-influencer/protection/{content_type}"
        
        secret_mappings = [
            SecretMapping(
                vault_path=vault_path,
                target_key="encryption_key",
                target_path=f"/etc/ia-influencer/protection/{content_type}_encryption.key",
                file_mode=0o600
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="fingerprint_key",
                target_path=f"/etc/ia-influencer/protection/{content_type}_fingerprint.key",
                file_mode=0o600
            )
        ]
        
        if user_id:
            secret_mappings.append(
                SecretMapping(
                    vault_path=f"{vault_path}/users/{user_id}",
                    target_key="user_key",
                    target_path=f"/etc/ia-influencer/protection/user_{user_id}.key",
                    file_mode=0o600
                )
            )
        
        return InjectionConfig(
            application_name=application_name,
            namespace=namespace,
            method=method,
            secret_mappings=secret_mappings,
            metadata={
                "content_type": content_type,
                "user_id": user_id,
                "protection_level": "high"
            }
        )
    
    def _create_payment_injection_config(
        self,
        processor: str,
        application_name: str,
        namespace: str,
        method: InjectionMethod
    ) -> InjectionConfig:
        """Create payment processor injection configuration."""
        vault_path = f"ia-influencer/payments/{processor}"
        
        secret_mappings = [
            SecretMapping(
                vault_path=vault_path,
                target_key="publishable_key",
                environment_variable=f"{processor.upper()}_PUBLISHABLE_KEY"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="secret_key",
                environment_variable=f"{processor.upper()}_SECRET_KEY"
            ),
            SecretMapping(
                vault_path=vault_path,
                target_key="webhook_secret",
                environment_variable=f"{processor.upper()}_WEBHOOK_SECRET"
            )
        ]
        
        return InjectionConfig(
            application_name=application_name,
            namespace=namespace,
            method=method,
            secret_mappings=secret_mappings,
            metadata={
                "processor": processor,
                "pci_compliance": True,
                "content_type": "payment_credentials"
            }
        )
    
    def _create_user_injection_config(
        self,
        user_id: str,
        application_name: str,
        secret_types: List[str],
        namespace: str,
        method: InjectionMethod
    ) -> InjectionConfig:
        """Create user-specific injection configuration."""
        secret_mappings = []
        
        for secret_type in secret_types:
            vault_path = f"ia-influencer/users/{user_id}/{secret_type}"
            
            secret_mappings.append(
                SecretMapping(
                    vault_path=vault_path,
                    target_key="user_key",
                    target_path=f"/etc/ia-influencer/users/{user_id}/{secret_type}.key",
                    file_mode=0o600
                )
            )
        
        return InjectionConfig(
            application_name=application_name,
            namespace=namespace,
            method=method,
            secret_mappings=secret_mappings,
            metadata={
                "user_id": user_id,
                "secret_types": secret_types,
                "content_type": "user_specific_credentials"
            }
        )
    
    def get_platform_injection_status(self) -> Dict[str, Any]:
        """Get status of all platform injections."""
        status = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_injections': len(self.platform_injections),
            'active_injections': 0,
            'platforms': {}
        }
        
        for injection_id, injection_info in self.platform_injections.items():
            platform = injection_info['platform']
            if injection_info['status'] == 'active':
                status['active_injections'] += 1
            
            status['platforms'][platform] = {
                'injection_id': injection_id,
                'status': injection_info['status'],
                'last_injection': injection_info['last_injection'].isoformat(),
                'user_id': injection_info.get('user_id')
            }
        
        return status
    
    def refresh_all_platform_credentials(self) -> Dict[str, bool]:
        """Refresh all platform credential injections."""
        results = {}
        
        for injection_id, injection_info in self.platform_injections.items():
            try:
                config_id = injection_info['config_id']
                result = self.inject_secrets(config_id, force_refresh=True)
                results[injection_id] = result.success
                
                if result.success:
                    injection_info['last_injection'] = datetime.utcnow()
                    logger.info(f"Refreshed platform injection: {injection_id}")
                else:
                    logger.error(f"Failed to refresh platform injection {injection_id}: {result.error}")
                    
            except Exception as e:
                logger.error(f"Platform injection refresh failed for {injection_id}: {e}")
                results[injection_id] = False
        
        return results
