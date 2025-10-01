"""Secret Management Template for iacherie Platform
Enterprise-grade secret management and encryption templates using HashiCorp Vault and AWS Secrets Manager.

⚠️ PROTECTION PROPRIÉTÉ INTELLECTUELLE
© 2025 Fahed Mlaiel <mlaiel@live.de>
Tous droits réservés - Utilisation commerciale interdite sans autorisation écrite explicite

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2024-09-18
"""

import logging
import yaml
import json
import base64
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class SecretBackend(Enum):
    """Secret storage backends"""
    VAULT = "hashicorp_vault"
    AWS_SECRETS = "aws_secrets_manager"
    AZURE_KEYVAULT = "azure_key_vault"
    GCP_SECRET_MANAGER = "gcp_secret_manager"
    KUBERNETES_SECRETS = "kubernetes_secrets"


class SecretType(Enum):
    """Types of secrets"""
    DATABASE_CREDENTIALS = "database"
    API_KEYS = "api_keys"
    CERTIFICATES = "certificates"
    ENCRYPTION_KEYS = "encryption_keys"
    OAUTH_TOKENS = "oauth_tokens"
    PAYMENT_CREDENTIALS = "payment"
    AI_MODEL_KEYS = "ai_models"
    STORAGE_CREDENTIALS = "storage"


@dataclass
class SecretManagementConfig:
    """Secret management configuration"""
    project_name: str
    environment: str
    backend: SecretBackend
    
    # Vault configuration
    vault_address: str = "https://vault.iacherie.com"
    vault_namespace: str = "iacherie"
    
    # AWS configuration
    aws_region: str = "us-west-2"
    
    # Encryption settings
    enable_encryption_at_rest: bool = True
    enable_encryption_in_transit: bool = True
    rotation_enabled: bool = True
    rotation_interval_days: int = 90
    
    # iacherie specific secrets
    secrets_to_manage: List[SecretType] = None
    
    def __post_init__(self):
        if self.secrets_to_manage is None:
            self.secrets_to_manage = [
                SecretType.DATABASE_CREDENTIALS,
                SecretType.API_KEYS,
                SecretType.CERTIFICATES,
                SecretType.ENCRYPTION_KEYS,
                SecretType.AI_MODEL_KEYS,
                SecretType.PAYMENT_CREDENTIALS
            ]


class SecretManagementTemplate:
    """Enterprise Secret Management Template for iacherie Platform"""
    
    def __init__(self, config: SecretManagementConfig):
        self.config = config
        
    def generate_vault_configuration(self) -> Dict[str, Any]:
        """Generate HashiCorp Vault configuration"""
        return {
            "listener": [
                {
                    "tcp": {
                        "address": "0.0.0.0:8200",
                        "tls_cert_file": "/vault/certs/vault.crt",
                        "tls_key_file": "/vault/certs/vault.key",
                        "tls_min_version": "tls12"
                    }
                }
            ],
            "storage": [
                {
                    "consul": {
                        "address": "consul:8500",
                        "path": "vault/",
                        "service": "vault",
                        "scheme": "https",
                        "tls_ca_file": "/vault/certs/ca.crt",
                        "tls_cert_file": "/vault/certs/consul.crt",
                        "tls_key_file": "/vault/certs/consul.key"
                    }
                }
            ],
            "seal": [
                {
                    "awskms": {
                        "region": self.config.aws_region,
                        "kms_key_id": f"alias/{self.config.project_name}-vault-seal"
                    }
                }
            ],
            "api_addr": self.config.vault_address,
            "cluster_addr": "https://vault:8201",
            "ui": True,
            "log_level": "INFO",
            "pid_file": "/vault/vault.pid",
            "disable_mlock": False
        }
    
    def generate_vault_policies(self) -> Dict[str, str]:
        """Generate Vault access policies for different services"""
        policies = {}
        
        # Admin policy
        policies["admin"] = '''
# Admin policy for full Vault access
path "*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}
'''
        
        # Application policy for iacherie services
        policies["iacherie-app"] = f'''
# Application policy for iacherie platform services
path "secret/data/{self.config.environment}/*" {{
  capabilities = ["read"]
}}

path "database/creds/{self.config.environment}-*" {{
  capabilities = ["read"]
}}

path "pki/issue/{self.config.environment}" {{
  capabilities = ["create", "update"]
}}

path "transit/encrypt/{self.config.environment}" {{
  capabilities = ["update"]
}}

path "transit/decrypt/{self.config.environment}" {{
  capabilities = ["update"]
}}
'''
        
        # CI/CD pipeline policy
        policies["cicd"] = f'''
# CI/CD pipeline policy for deployments
path "secret/data/{self.config.environment}/cicd/*" {{
  capabilities = ["read"]
}}

path "auth/kubernetes/role/{self.config.environment}-deployer" {{
  capabilities = ["read", "update"]
}}
'''
        
        # Monitoring policy
        policies["monitoring"] = f'''
# Monitoring services policy
path "secret/data/{self.config.environment}/monitoring/*" {{
  capabilities = ["read"]
}}
'''
        
        return policies
    
    def generate_secret_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Generate secret definitions for iacherie platform"""
        secrets = {}
        
        if SecretType.DATABASE_CREDENTIALS in self.config.secrets_to_manage:
            secrets["database"] = {
                "path": f"secret/{self.config.environment}/database",
                "data": {
                    "postgres_host": "{{ postgres_host }}",
                    "postgres_port": "5432",
                    "postgres_database": "iacherie",
                    "postgres_username": "{{ postgres_username }}",
                    "postgres_password": "{{ postgres_password }}",
                    "redis_host": "{{ redis_host }}",
                    "redis_port": "6379",
                    "redis_password": "{{ redis_password }}",
                    "mongodb_uri": "{{ mongodb_connection_string }}"
                },
                "rotation": {
                    "enabled": self.config.rotation_enabled,
                    "interval": f"{self.config.rotation_interval_days}d"
                }
            }
        
        if SecretType.API_KEYS in self.config.secrets_to_manage:
            secrets["api_keys"] = {
                "path": f"secret/{self.config.environment}/api_keys",
                "data": {
                    "openai_api_key": "{{ openai_api_key }}",
                    "stripe_secret_key": "{{ stripe_secret_key }}",
                    "stripe_publishable_key": "{{ stripe_publishable_key }}",
                    "sendgrid_api_key": "{{ sendgrid_api_key }}",
                    "twilio_account_sid": "{{ twilio_account_sid }}",
                    "twilio_auth_token": "{{ twilio_auth_token }}",
                    "facebook_app_secret": "{{ facebook_app_secret }}",
                    "google_client_secret": "{{ google_client_secret }}",
                    "spotify_client_secret": "{{ spotify_client_secret }}"
                }
            }
        
        if SecretType.ENCRYPTION_KEYS in self.config.secrets_to_manage:
            secrets["encryption"] = {
                "path": f"secret/{self.config.environment}/encryption",
                "data": {
                    "jwt_secret_key": "{{ jwt_secret_key }}",
                    "session_secret_key": "{{ session_secret_key }}",
                    "content_encryption_key": "{{ content_encryption_key }}",
                    "backup_encryption_key": "{{ backup_encryption_key }}",
                    "file_encryption_passphrase": "{{ file_encryption_passphrase }}"
                }
            }
        
        if SecretType.CERTIFICATES in self.config.secrets_to_manage:
            secrets["certificates"] = {
                "path": f"secret/{self.config.environment}/certificates",
                "data": {
                    "ssl_certificate": "{{ ssl_certificate_pem }}",
                    "ssl_private_key": "{{ ssl_private_key_pem }}",
                    "ca_certificate": "{{ ca_certificate_pem }}",
                    "client_certificate": "{{ client_certificate_pem }}",
                    "client_private_key": "{{ client_private_key_pem }}"
                }
            }
        
        if SecretType.AI_MODEL_KEYS in self.config.secrets_to_manage:
            secrets["ai_models"] = {
                "path": f"secret/{self.config.environment}/ai_models",
                "data": {
                    "huggingface_token": "{{ huggingface_token }}",
                    "anthropic_api_key": "{{ anthropic_api_key }}",
                    "cohere_api_key": "{{ cohere_api_key }}",
                    "stability_api_key": "{{ stability_api_key }}",
                    "elevenlabs_api_key": "{{ elevenlabs_api_key }}",
                    "model_encryption_key": "{{ model_encryption_key }}"
                }
            }
        
        if SecretType.STORAGE_CREDENTIALS in self.config.secrets_to_manage:
            secrets["storage"] = {
                "path": f"secret/{self.config.environment}/storage",
                "data": {
                    "aws_access_key_id": "{{ aws_access_key_id }}",
                    "aws_secret_access_key": "{{ aws_secret_access_key }}",
                    "s3_bucket_name": "{{ s3_bucket_name }}",
                    "cloudfront_distribution_id": "{{ cloudfront_distribution_id }}",
                    "azure_storage_account": "{{ azure_storage_account }}",
                    "azure_storage_key": "{{ azure_storage_key }}"
                }
            }
        
        return secrets
    
    def generate_kubernetes_secret_manifests(self) -> List[Dict[str, Any]]:
        """Generate Kubernetes secret manifests with Vault integration"""
        manifests = []
        
        # Vault auth ConfigMap
        vault_config = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self.config.project_name}-vault-config",
                "namespace": f"{self.config.project_name}-{self.config.environment}"
            },
            "data": {
                "vault_addr": self.config.vault_address,
                "vault_namespace": self.config.vault_namespace,
                "vault_role": f"{self.config.environment}-app",
                "vault_auth_path": "auth/kubernetes"
            }
        }
        manifests.append(vault_config)
        
        # Service Account for Vault authentication
        service_account = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": f"{self.config.project_name}-vault-auth",
                "namespace": f"{self.config.project_name}-{self.config.environment}",
                "annotations": {
                    "vault.hashicorp.com/role": f"{self.config.environment}-app"
                }
            }
        }
        manifests.append(service_account)
        
        # Vault Secret Store (using External Secrets Operator)
        secret_store = {
            "apiVersion": "external-secrets.io/v1beta1",
            "kind": "SecretStore",
            "metadata": {
                "name": f"{self.config.project_name}-vault-store",
                "namespace": f"{self.config.project_name}-{self.config.environment}"
            },
            "spec": {
                "provider": {
                    "vault": {
                        "server": self.config.vault_address,
                        "path": "secret",
                        "version": "v2",
                        "namespace": self.config.vault_namespace,
                        "auth": {
                            "kubernetes": {
                                "mountPath": "kubernetes",
                                "role": f"{self.config.environment}-app",
                                "serviceAccountRef": {
                                    "name": f"{self.config.project_name}-vault-auth"
                                }
                            }
                        }
                    }
                }
            }
        }
        manifests.append(secret_store)
        
        # External Secrets for each secret type
        for secret_name, secret_config in self.generate_secret_definitions().items():
            external_secret = {
                "apiVersion": "external-secrets.io/v1beta1",
                "kind": "ExternalSecret",
                "metadata": {
                    "name": f"{self.config.project_name}-{secret_name}",
                    "namespace": f"{self.config.project_name}-{self.config.environment}"
                },
                "spec": {
                    "refreshInterval": "1h",
                    "secretStoreRef": {
                        "name": f"{self.config.project_name}-vault-store",
                        "kind": "SecretStore"
                    },
                    "target": {
                        "name": f"{self.config.project_name}-{secret_name}",
                        "creationPolicy": "Owner"
                    },
                    "data": []
                }
            }
            
            # Add data mappings
            for key, _ in secret_config["data"].items():
                external_secret["spec"]["data"].append({
                    "secretKey": key,
                    "remoteRef": {
                        "key": secret_config["path"],
                        "property": key
                    }
                })
            
            manifests.append(external_secret)
        
        return manifests
    
    def generate_vault_init_script(self) -> str:
        """Generate Vault initialization script"""
        return f'''#!/bin/bash
# Vault Initialization Script for iacherie Platform
# Environment: {self.config.environment}

set -e

VAULT_ADDR="{self.config.vault_address}"
VAULT_NAMESPACE="{self.config.vault_namespace}"

echo "Initializing Vault for iacherie Platform..."

# Initialize Vault if not already initialized
if ! vault status >/dev/null 2>&1; then
    echo "Initializing Vault..."
    vault operator init -key-shares=5 -key-threshold=3 -format=json > vault-keys.json
    
    # Unseal Vault
    echo "Unsealing Vault..."
    UNSEAL_KEY_1=$(cat vault-keys.json | jq -r '.unseal_keys_b64[0]')
    UNSEAL_KEY_2=$(cat vault-keys.json | jq -r '.unseal_keys_b64[1]')
    UNSEAL_KEY_3=$(cat vault-keys.json | jq -r '.unseal_keys_b64[2]')
    
    vault operator unseal $UNSEAL_KEY_1
    vault operator unseal $UNSEAL_KEY_2
    vault operator unseal $UNSEAL_KEY_3
    
    # Login with root token
    ROOT_TOKEN=$(cat vault-keys.json | jq -r '.root_token')
    vault auth -token=$ROOT_TOKEN
else
    echo "Vault is already initialized"
fi

# Enable secret engines
echo "Enabling secret engines..."
vault secrets enable -path=secret kv-v2 || true
vault secrets enable -path=database database || true
vault secrets enable -path=pki pki || true
vault secrets enable -path=transit transit || true

# Enable auth methods
echo "Enabling auth methods..."
vault auth enable kubernetes || true
vault auth enable userpass || true

# Configure PKI
echo "Configuring PKI..."
vault write pki/config/urls \\
    issuing_certificates="{self.config.vault_address}/v1/pki/ca" \\
    crl_distribution_points="{self.config.vault_address}/v1/pki/crl"

vault write pki/config/ca pem_bundle=@ca-bundle.pem || true

vault write pki/roles/{self.config.environment} \\
    allowed_domains="iacherie.com,{self.config.environment}.iacherie.com" \\
    allow_subdomains=true \\
    max_ttl=8760h \\
    ttl=720h

# Configure Kubernetes auth
echo "Configuring Kubernetes authentication..."
vault write auth/kubernetes/config \\
    token_reviewer_jwt="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \\
    kubernetes_host="https://kubernetes.default.svc:443" \\
    kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

# Create Kubernetes role
vault write auth/kubernetes/role/{self.config.environment}-app \\
    bound_service_account_names="{self.config.project_name}-vault-auth" \\
    bound_service_account_namespaces="{self.config.project_name}-{self.config.environment}" \\
    policies="iacherie-app" \\
    ttl=24h

# Configure database secrets engine
echo "Configuring database secrets..."
vault write database/config/postgres \\
    plugin_name=postgresql-database-plugin \\
    connection_url="postgresql://vault:{{{{password}}}}@postgres:5432/iacherie?sslmode=require" \\
    allowed_roles="{self.config.environment}-readonly,{self.config.environment}-readwrite" \\
    username="vault" \\
    password="$POSTGRES_VAULT_PASSWORD"

vault write database/roles/{self.config.environment}-readonly \\
    db_name=postgres \\
    creation_statements="CREATE ROLE \\"{{{{name}}}}\\" WITH LOGIN PASSWORD '{{{{password}}}}' VALID UNTIL '{{{{expiration}}}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \\"{{{{name}}}}\\";" \\
    default_ttl="1h" \\
    max_ttl="24h"

vault write database/roles/{self.config.environment}-readwrite \\
    db_name=postgres \\
    creation_statements="CREATE ROLE \\"{{{{name}}}}\\" WITH LOGIN PASSWORD '{{{{password}}}}' VALID UNTIL '{{{{expiration}}}}'; GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \\"{{{{name}}}}\\";" \\
    default_ttl="1h" \\
    max_ttl="24h"

# Configure transit encryption
echo "Configuring transit encryption..."
vault write transit/keys/{self.config.environment} type=aes256-gcm96

echo "Vault initialization complete!"
'''
    
    def generate_secret_rotation_script(self) -> str:
        """Generate secret rotation script"""
        return f'''#!/bin/bash
# Secret Rotation Script for iacherie Platform
# Environment: {self.config.environment}

set -e

VAULT_ADDR="{self.config.vault_address}"
VAULT_NAMESPACE="{self.config.vault_namespace}"

echo "Starting secret rotation for {self.config.environment}..."

# Function to rotate database credentials
rotate_database_secrets() {{
    echo "Rotating database secrets..."
    
    # Generate new password
    NEW_PASSWORD=$(openssl rand -base64 32)
    
    # Update in Vault
    vault kv put secret/{self.config.environment}/database \\
        postgres_password="$NEW_PASSWORD" \\
        redis_password="$(openssl rand -base64 24)"
    
    echo "Database secrets rotated successfully"
}}

# Function to rotate API keys (manual verification required)
rotate_api_keys() {{
    echo "API key rotation requires manual intervention"
    echo "Please update the following keys in external services:"
    echo "- OpenAI API Key"
    echo "- Stripe Secret Key"
    echo "- SendGrid API Key"
    echo "Then update them in Vault manually"
}}

# Function to rotate encryption keys
rotate_encryption_keys() {{
    echo "Rotating encryption keys..."
    
    # Generate new JWT secret
    NEW_JWT_SECRET=$(openssl rand -base64 64)
    NEW_SESSION_SECRET=$(openssl rand -base64 32)
    
    vault kv put secret/{self.config.environment}/encryption \\
        jwt_secret_key="$NEW_JWT_SECRET" \\
        session_secret_key="$NEW_SESSION_SECRET"
    
    echo "Encryption keys rotated successfully"
}}

# Function to rotate certificates
rotate_certificates() {{
    echo "Rotating certificates..."
    
    # Generate new certificate from PKI
    vault write -format=json pki/issue/{self.config.environment} \\
        common_name="{self.config.environment}.iacherie.com" \\
        alt_names="api.{self.config.environment}.iacherie.com,app.{self.config.environment}.iacherie.com" \\
        ttl=720h > new_cert.json
    
    # Extract certificate data
    CERTIFICATE=$(cat new_cert.json | jq -r '.data.certificate')
    PRIVATE_KEY=$(cat new_cert.json | jq -r '.data.private_key')
    CA_CHAIN=$(cat new_cert.json | jq -r '.data.ca_chain[0]')
    
    # Update in Vault
    vault kv put secret/{self.config.environment}/certificates \\
        ssl_certificate="$CERTIFICATE" \\
        ssl_private_key="$PRIVATE_KEY" \\
        ca_certificate="$CA_CHAIN"
    
    echo "Certificates rotated successfully"
}}

# Check if rotation is due
LAST_ROTATION=$(vault kv get -field=last_rotation secret/{self.config.environment}/rotation_info 2>/dev/null || echo "0")
CURRENT_TIME=$(date +%s)
ROTATION_INTERVAL=$((60 * 60 * 24 * {self.config.rotation_interval_days}))  # Convert days to seconds

if [ $((CURRENT_TIME - LAST_ROTATION)) -gt $ROTATION_INTERVAL ]; then
    echo "Rotation is due. Starting rotation process..."
    
    # Rotate secrets
    rotate_database_secrets
    rotate_encryption_keys
    rotate_certificates
    
    # Update rotation timestamp
    vault kv put secret/{self.config.environment}/rotation_info \\
        last_rotation="$CURRENT_TIME" \\
        next_rotation="$((CURRENT_TIME + ROTATION_INTERVAL))"
    
    # Restart services to pick up new secrets
    kubectl rollout restart deployment/{self.config.project_name}-api-gateway -n {self.config.project_name}-{self.config.environment}
    kubectl rollout restart deployment/{self.config.project_name}-auth-service -n {self.config.project_name}-{self.config.environment}
    
    echo "Secret rotation completed successfully"
else
    echo "Rotation not due. Next rotation: $(date -d @$((LAST_ROTATION + ROTATION_INTERVAL)))"
fi
'''
    
    def save_secret_management_configs(self, output_dir: str) -> None:
        """Save all secret management configurations"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Vault configuration
        vault_dir = output_path / "vault"
        vault_dir.mkdir(exist_ok=True)
        
        with open(vault_dir / "config.hcl", 'w') as f:
            # Convert dict to HCL format (simplified)
            config = self.generate_vault_configuration()
            f.write(self._dict_to_hcl(config))
        
        # Vault policies
        policies_dir = vault_dir / "policies"
        policies_dir.mkdir(exist_ok=True)
        
        for policy_name, policy_content in self.generate_vault_policies().items():
            with open(policies_dir / f"{policy_name}.hcl", 'w') as f:
                f.write(policy_content)
        
        # Secret definitions
        with open(vault_dir / "secrets.yml", 'w') as f:
            yaml.dump(self.generate_secret_definitions(), f, default_flow_style=False, indent=2)
        
        # Kubernetes manifests
        k8s_dir = output_path / "kubernetes" / "secrets"
        k8s_dir.mkdir(parents=True, exist_ok=True)
        
        manifests = self.generate_kubernetes_secret_manifests()
        with open(k8s_dir / "secrets.yaml", 'w') as f:
            yaml.dump_all(manifests, f, default_flow_style=False, indent=2)
        
        # Scripts
        scripts_dir = output_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        with open(scripts_dir / "vault-init.sh", 'w') as f:
            f.write(self.generate_vault_init_script())
        
        with open(scripts_dir / "rotate-secrets.sh", 'w') as f:
            f.write(self.generate_secret_rotation_script())
        
        # Make scripts executable
        (scripts_dir / "vault-init.sh").chmod(0o755)
        (scripts_dir / "rotate-secrets.sh").chmod(0o755)
        
        logger.info(f"Secret management configurations saved to {output_dir}")
    
    def _dict_to_hcl(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Convert dictionary to HCL format (simplified)"""
        hcl_lines = []
        indent_str = "  " * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                hcl_lines.append(f"{indent_str}{key} {{")
                hcl_lines.append(self._dict_to_hcl(value, indent + 1))
                hcl_lines.append(f"{indent_str}}}")
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        hcl_lines.append(f"{indent_str}{key} {{")
                        hcl_lines.append(self._dict_to_hcl(item, indent + 1))
                        hcl_lines.append(f"{indent_str}}}")
                    else:
                        hcl_lines.append(f'{indent_str}{key} = "{item}"')
            elif isinstance(value, bool):
                hcl_lines.append(f'{indent_str}{key} = {str(value).lower()}')
            else:
                hcl_lines.append(f'{indent_str}{key} = "{value}"')
        
        return "\n".join(hcl_lines)


# Example usage
def create_production_secret_config() -> SecretManagementConfig:
    """Create production secret management configuration"""
    return SecretManagementConfig(
        project_name="iacherie-platform",
        environment="production",
        backend=SecretBackend.VAULT,
        vault_address="https://vault.iacherie.com",
        enable_encryption_at_rest=True,
        enable_encryption_in_transit=True,
        rotation_enabled=True,
        rotation_interval_days=90
    )


if __name__ == "__main__":
    config = create_production_secret_config()
    template = SecretManagementTemplate(config)
    
    print("Secret Management Template for iacherie Platform")
    print("Configuration:")
    print(f"- Backend: {config.backend.value}")
    print(f"- Environment: {config.environment}")
    print(f"- Rotation Enabled: {config.rotation_enabled}")
    print(f"- Secrets Managed: {[s.value for s in config.secrets_to_manage]}")
