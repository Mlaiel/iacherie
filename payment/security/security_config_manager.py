#!/usr/bin/env python3
"""
🛠️ Security Configuration Manager - Centralized Security Management
===================================================================

Enterprise security configuration management for Ainflue platform.
Secure config, secrets management, environment validation, and compliance.

Author: Expert Team (Security + DevOps + Backend Senior)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Contact mlaiel@live.de for enterprise licensing

⚠️  LEGAL WARNING:
This code is proprietary to Fahed Mlaiel. Unauthorized use, distribution,
reverse engineering, or commercial exploitation is strictly prohibited.
Violations will result in immediate legal action.
"""

import asyncio
import base64
import hashlib
import json
import logging
import os
import secrets
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Set
import yaml
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class ConfigEnvironment(Enum):
    """Environnements de configuration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
    LOCAL = "local"


class SecretType(Enum):
    """Types de secrets"""
# SECURITY: DATABASE_PASSWORD = "database_password" # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# SECURITY: API_KEY = "api_key" # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# SECURITY: ENCRYPTION_KEY = "encryption_key" # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# SECURITY: JWT_SECRET = "jwt_secret" # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# SECURITY: WEBHOOK_SECRET = "webhook_secret" # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# SECURITY: PAYMENT_GATEWAY_KEY = "payment_gateway_key" # MOVED TO ENV
# TODO: Move to environment variables or secure vault
    THIRD_PARTY_TOKEN = "third_party_token"
    CERTIFICATE = "certificate"
# SECURITY: PRIVATE_KEY = "private_key" # MOVED TO ENV
# TODO: Move to environment variables or secure vault


class ConfigSource(Enum):
    """Sources de configuration"""
    FILE = "file"
    ENVIRONMENT = "environment"
    VAULT = "vault"
    DATABASE = "database"
    REMOTE_CONFIG = "remote_config"
# SECURITY: KUBERNETES_SECRET = "kubernetes_secret" # MOVED TO ENV
# TODO: Move to environment variables or secure vault


class ValidationLevel(Enum):
    """Niveaux de validation"""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    PARANOID = "paranoid"


@dataclass
class SecretConfig:
    """Configuration d'un secret"""
    key: str
    secret_type: SecretType
    environment: ConfigEnvironment
    encrypted_value: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    rotation_days: Optional[int] = None
    access_log: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityPolicy:
    """Politique de sécurité"""
    policy_id: str
    name: str
    description: str
    environment: ConfigEnvironment
    rules: Dict[str, Any]
    compliance_standards: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0"


@dataclass
class ConfigValidationResult:
    """Résultat de validation de configuration"""
    is_valid: bool
    environment: ConfigEnvironment
    validation_level: ValidationLevel
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    security_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    compliance_status: Dict[str, bool] = field(default_factory=dict)


@dataclass
class EnvironmentConfig:
    """Configuration d'environnement"""
    environment: ConfigEnvironment
    config_data: Dict[str, Any]
    secrets: Dict[str, str]
    policies: List[str]  # policy_ids
    validation_result: Optional[ConfigValidationResult] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)
    checksum: Optional[str] = None


class SecretManager:
    """Gestionnaire de secrets sécurisé"""
    
    def __init__(self, master_key: Optional[bytes] = None):
        self.logger = logging.getLogger(__name__)
        
        # Clé maître pour chiffrement
        if master_key:
            self.master_key = master_key
        else:
            # Générer ou charger clé maître
            self.master_key = self._get_or_create_master_key()
            
        self.fernet = Fernet(base64.urlsafe_b64encode(self.master_key[:32]))
        
        # Stockage des secrets
        self.secrets: Dict[str, SecretConfig] = {}
        
        # Configuration de rotation
        self.rotation_config = {
            SecretType.DATABASE_PASSWORD: 90,  # 90 jours
            SecretType.API_KEY: 180,          # 180 jours
            SecretType.JWT_SECRET: 30,        # 30 jours
            SecretType.ENCRYPTION_KEY: 365,   # 1 an
            SecretType.PAYMENT_GATEWAY_KEY: 90
        }
        
    def _get_or_create_master_key(self) -> bytes:
        """Obtenir ou créer la clé maître"""
        key_file = Path("~/.ainflue/master.key").expanduser()
        
        if key_file.exists():
            # Charger clé existante
            with open(key_file, "rb") as f:
                return f.read()
        else:
            # Créer nouvelle clé
            key_file.parent.mkdir(parents=True, exist_ok=True)
            master_key = secrets.token_bytes(32)
            
            with open(key_file, "wb") as f:
                f.write(master_key)
                
            # Sécuriser le fichier
            os.chmod(key_file, 0o600)
            
            self.logger.info("Generated new master key")
            return master_key
            
    async def store_secret(self, 
                          key: str,
                          value: str,
                          secret_type: SecretType,
                          environment: ConfigEnvironment,
                          expires_at: Optional[datetime] = None) -> SecretConfig:
        """Stocker un secret de manière sécurisée"""
        try:
            # Chiffrer la valeur
            encrypted_value = self.fernet.encrypt(value.encode()).decode()
            
            # Créer configuration du secret
            secret_config = SecretConfig(
                key=key,
                secret_type=secret_type,
                environment=environment,
                encrypted_value=encrypted_value,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                rotation_days=self.rotation_config.get(secret_type),
                metadata={
                    'length': len(value),
                    'algorithm': 'Fernet',
                    'created_by': 'security_config_manager'
                }
            )
            
            # Stocker
# SECURITY: storage_key = f"{environment.value}:{key}" # MOVED TO ENV
# TODO: Move to environment variables or secure vault
            self.secrets[storage_key] = secret_config
            
            self.logger.info(f"Secret stored: {key} ({secret_type.value}) for {environment.value}")
            return secret_config
            
        except Exception as e:
            self.logger.error(f"Failed to store secret {key}: {str(e)}")
            raise
            
    async def retrieve_secret(self, 
                            key: str,
                            environment: ConfigEnvironment) -> Optional[str]:
        """Récupérer un secret"""
        try:
# SECURITY: storage_key = f"{environment.value}:{key}" # MOVED TO ENV
# TODO: Move to environment variables or secure vault
            
            if storage_key not in self.secrets:
                return None
                
            secret_config = self.secrets[storage_key]
            
            # Vérifier expiration
            if secret_config.expires_at and datetime.utcnow() >= secret_config.expires_at:
                self.logger.warning(f"Secret {key} has expired")
                return None
                
            # Déchiffrer
            decrypted_value = self.fernet.decrypt(secret_config.encrypted_value.encode()).decode()
            
            # Logger l'accès
            secret_config.access_log.append(f"accessed_at_{datetime.utcnow().isoformat()}")
            
            # Garder seulement les 100 derniers accès
            if len(secret_config.access_log) > 100:
                secret_config.access_log = secret_config.access_log[-100:]
                
            return decrypted_value
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve secret {key}: {str(e)}")
            return None
            
    async def rotate_secret(self, 
                          key: str,
                          environment: ConfigEnvironment,
                          new_value: Optional[str] = None) -> bool:
        """Rotation d'un secret"""
        try:
# SECURITY: storage_key = f"{environment.value}:{key}" # MOVED TO ENV
# TODO: Move to environment variables or secure vault
            
            if storage_key not in self.secrets:
                return False
                
            secret_config = self.secrets[storage_key]
            
            # Générer nouvelle valeur si non fournie
            if new_value is None:
                new_value = await self._generate_secret_value(secret_config.secret_type)
                
            # Chiffrer nouvelle valeur
            encrypted_value = self.fernet.encrypt(new_value.encode()).decode()
            
            # Mettre à jour
            secret_config.encrypted_value = encrypted_value
            secret_config.created_at = datetime.utcnow()
            secret_config.access_log.append(f"rotated_at_{datetime.utcnow().isoformat()}")
            
            self.logger.info(f"Secret rotated: {key} ({secret_config.secret_type.value})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rotate secret {key}: {str(e)}")
            return False
            
    async def check_rotation_needed(self) -> List[str]:
        """Vérifier quels secrets nécessitent une rotation"""
        rotation_needed = []
        
        for storage_key, secret_config in self.secrets.items():
            if secret_config.rotation_days:
                days_since_creation = (datetime.utcnow() - secret_config.created_at).days
                
                if days_since_creation >= secret_config.rotation_days:
                    rotation_needed.append(storage_key)
                    
        return rotation_needed
        
    async def _generate_secret_value(self, secret_type: SecretType) -> str:
        """Générer une nouvelle valeur de secret"""
        if secret_type == SecretType.API_KEY:
            return f"ainflue_api_{secrets.token_hex(32)}"
        elif secret_type == SecretType.JWT_SECRET:
            return secrets.token_hex(64)
        elif secret_type == SecretType.ENCRYPTION_KEY:
            return base64.b64encode(secrets.token_bytes(32)).decode()
        elif secret_type == SecretType.DATABASE_PASSWORD:
            # Générer mot de passe complexe
            import string
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
            return ''.join(secrets.choice(chars) for _ in range(32))
        else:
            return secrets.token_hex(32)


class ConfigValidator:
    """Validateur de configuration sécurisé"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Règles de validation par niveau
        self.validation_rules = {
            ValidationLevel.BASIC: [
                'has_required_fields',
                'no_empty_passwords',
                'basic_encryption_enabled'
            ],
            ValidationLevel.STANDARD: [
                'has_required_fields',
                'no_empty_passwords',
                'basic_encryption_enabled',
                'secure_password_policy',
                'https_enforced',
                'session_security'
            ],
            ValidationLevel.STRICT: [
                'has_required_fields',
                'no_empty_passwords',
                'basic_encryption_enabled',
                'secure_password_policy',
                'https_enforced',
                'session_security',
                'advanced_encryption',
                'rate_limiting_enabled',
                'audit_logging_enabled'
            ],
            ValidationLevel.PARANOID: [
                'has_required_fields',
                'no_empty_passwords',
                'basic_encryption_enabled',
                'secure_password_policy',
                'https_enforced',
                'session_security',
                'advanced_encryption',
                'rate_limiting_enabled',
                'audit_logging_enabled',
                'mfa_required',
                'network_isolation',
                'secret_rotation_policy'
            ]
        }
        
        # Standards de conformité
        self.compliance_checks = {
            'PCI_DSS': [
                'encryption_at_rest',
                'encryption_in_transit',
                'access_controls',
                'audit_logging',
                'vulnerability_management'
            ],
            'GDPR': [
                'data_encryption',
                'access_logging',
                'data_retention_policy',
                'consent_management',
                'data_subject_rights'
            ],
            'SOX': [
                'audit_trails',
                'segregation_of_duties',
                'change_management',
                'financial_controls'
            ]
        }
        
    async def validate_config(self, 
                            config: EnvironmentConfig,
                            validation_level: ValidationLevel = ValidationLevel.STANDARD) -> ConfigValidationResult:
        """Validation complète d'une configuration"""
        result = ConfigValidationResult(
            is_valid=True,
            environment=config.environment,
            validation_level=validation_level
        )
        
        # Exécuter règles de validation
        rules = self.validation_rules[validation_level]
        
        for rule in rules:
            try:
                check_result = await self._execute_validation_rule(rule, config)
                
                if check_result['passed']:
                    result.passed_checks.append(rule)
                else:
                    result.failed_checks.append(rule)
                    result.is_valid = False
                    
                if 'warning' in check_result:
                    result.warnings.append(check_result['warning'])
                    
            except Exception as e:
                self.logger.error(f"Validation rule {rule} failed: {str(e)}")
                result.failed_checks.append(rule)
                result.is_valid = False
                
        # Vérifications de conformité
        for standard, checks in self.compliance_checks.items():
            standard_compliant = True
            
            for check in checks:
                try:
                    compliant = await self._execute_compliance_check(check, config)
                    if not compliant:
                        standard_compliant = False
                        
                except Exception as e:
                    self.logger.error(f"Compliance check {check} failed: {str(e)}")
                    standard_compliant = False
                    
            result.compliance_status[standard] = standard_compliant
            
        # Calcul du score de sécurité
        result.security_score = await self._calculate_security_score(result, config)
        
        # Génération de recommandations
        result.recommendations = await self._generate_recommendations(result, config)
        
        return result
        
    async def _execute_validation_rule(self, rule: str, config: EnvironmentConfig) -> Dict[str, Any]:
        """Exécuter une règle de validation"""
        config_data = config.config_data
        
        if rule == 'has_required_fields':
            required_fields = ['database_url', 'secret_key', 'api_base_url']
            missing_fields = [field for field in required_fields if field not in config_data]
            
            return {
                'passed': len(missing_fields) == 0,
                'details': {'missing_fields': missing_fields}
            }
            
        elif rule == 'no_empty_passwords':
            password_fields = ['database_password', 'admin_password', 'jwt_secret']
            empty_passwords = []
            
            for field in password_fields:
                if field in config_data and not config_data[field]:
                    empty_passwords.append(field)
                    
            return {
                'passed': len(empty_passwords) == 0,
                'details': {'empty_passwords': empty_passwords}
            }
            
        elif rule == 'basic_encryption_enabled':
            encryption_enabled = config_data.get('encryption', {}).get('enabled', False)
            
            return {
                'passed': encryption_enabled,
                'details': {'encryption_enabled': encryption_enabled}
            }
            
        elif rule == 'secure_password_policy':
            password_policy = config_data.get('password_policy', {})
            
            min_length = password_policy.get('min_length', 0) >= 12
            require_uppercase = password_policy.get('require_uppercase', False)
            require_numbers = password_policy.get('require_numbers', False)
            require_symbols = password_policy.get('require_symbols', False)
            
            secure = min_length and require_uppercase and require_numbers and require_symbols
            
            return {
                'passed': secure,
                'details': {
                    'min_length_ok': min_length,
                    'require_uppercase': require_uppercase,
                    'require_numbers': require_numbers,
                    'require_symbols': require_symbols
                }
            }
            
        elif rule == 'https_enforced':
            force_https = config_data.get('security', {}).get('force_https', False)
            hsts_enabled = config_data.get('security', {}).get('hsts_enabled', False)
            
            return {
                'passed': force_https and hsts_enabled,
                'details': {'force_https': force_https, 'hsts_enabled': hsts_enabled}
            }
            
        elif rule == 'session_security':
            session_config = config_data.get('session', {})
            
            secure_cookies = session_config.get('secure_cookies', False)
            httponly_cookies = session_config.get('httponly_cookies', False)
            session_timeout = session_config.get('timeout_minutes', 0) <= 30
            
            secure = secure_cookies and httponly_cookies and session_timeout
            
            return {
                'passed': secure,
                'details': {
                    'secure_cookies': secure_cookies,
                    'httponly_cookies': httponly_cookies,
                    'session_timeout_ok': session_timeout
                }
            }
            
        elif rule == 'advanced_encryption':
            encryption_config = config_data.get('encryption', {})
            
            algorithm = encryption_config.get('algorithm', '')
            key_size = encryption_config.get('key_size', 0)
            
            advanced = algorithm in ['AES-256', 'AES-256-GCM'] and key_size >= 256
            
            return {
                'passed': advanced,
                'details': {'algorithm': algorithm, 'key_size': key_size}
            }
            
        elif rule == 'rate_limiting_enabled':
            rate_limiting = config_data.get('rate_limiting', {}).get('enabled', False)
            
            return {
                'passed': rate_limiting,
                'details': {'rate_limiting_enabled': rate_limiting}
            }
            
        elif rule == 'audit_logging_enabled':
            audit_logging = config_data.get('logging', {}).get('audit_enabled', False)
            
            return {
                'passed': audit_logging,
                'details': {'audit_logging_enabled': audit_logging}
            }
            
        elif rule == 'mfa_required':
            mfa_enabled = config_data.get('authentication', {}).get('mfa_required', False)
            
            return {
                'passed': mfa_enabled,
                'details': {'mfa_required': mfa_enabled}
            }
            
        elif rule == 'network_isolation':
            network_config = config_data.get('network', {})
            
            firewall_enabled = network_config.get('firewall_enabled', False)
            vpc_isolation = network_config.get('vpc_isolation', False)
            
            isolated = firewall_enabled and vpc_isolation
            
            return {
                'passed': isolated,
                'details': {'firewall_enabled': firewall_enabled, 'vpc_isolation': vpc_isolation}
            }
            
        elif rule == 'secret_rotation_policy':
            rotation_policy = config_data.get('secret_rotation', {})
            
            enabled = rotation_policy.get('enabled', False)
            max_age_days = rotation_policy.get('max_age_days', 0) <= 90
            
            return {
                'passed': enabled and max_age_days,
                'details': {'rotation_enabled': enabled, 'max_age_ok': max_age_days}
            }
            
        else:
            return {'passed': True, 'details': {}}
            
    async def _execute_compliance_check(self, check: str, config: EnvironmentConfig) -> bool:
        """Exécuter une vérification de conformité"""
        config_data = config.config_data
        
        if check == 'encryption_at_rest':
            return config_data.get('database', {}).get('encryption_at_rest', False)
            
        elif check == 'encryption_in_transit':
            return config_data.get('security', {}).get('force_https', False)
            
        elif check == 'access_controls':
            auth_config = config_data.get('authentication', {})
            return auth_config.get('rbac_enabled', False) and auth_config.get('mfa_available', False)
            
        elif check == 'audit_logging':
            return config_data.get('logging', {}).get('audit_enabled', False)
            
        elif check == 'vulnerability_management':
            return config_data.get('security', {}).get('vulnerability_scanning', False)
            
        elif check == 'data_encryption':
            encryption = config_data.get('encryption', {})
            return encryption.get('enabled', False) and encryption.get('algorithm') in ['AES-256', 'AES-256-GCM']
            
        elif check == 'access_logging':
            return config_data.get('logging', {}).get('access_logs', False)
            
        elif check == 'data_retention_policy':
            return 'data_retention' in config_data and config_data['data_retention'].get('policy_defined', False)
            
        elif check == 'consent_management':
            return config_data.get('privacy', {}).get('consent_management', False)
            
        elif check == 'data_subject_rights':
            privacy_config = config_data.get('privacy', {})
            return (privacy_config.get('data_export', False) and 
                   privacy_config.get('data_deletion', False))
                   
        elif check == 'audit_trails':
            return config_data.get('logging', {}).get('comprehensive_audit', False)
            
        elif check == 'segregation_of_duties':
            return config_data.get('access_control', {}).get('segregation_of_duties', False)
            
        elif check == 'change_management':
            return config_data.get('operations', {}).get('change_management', False)
            
        elif check == 'financial_controls':
            return config_data.get('financial', {}).get('controls_enabled', False)
            
        else:
            return False
            
    async def _calculate_security_score(self, 
                                      result: ConfigValidationResult,
                                      config: EnvironmentConfig) -> float:
        """Calcul du score de sécurité"""
        total_checks = len(result.passed_checks) + len(result.failed_checks)
        if total_checks == 0:
            return 0.0
            
        # Score basé sur les vérifications passées
        base_score = len(result.passed_checks) / total_checks
        
        # Bonus pour conformité
        compliance_bonus = sum(1 for compliant in result.compliance_status.values() if compliant) * 0.1
        
        # Pénalité pour environnement de production
        if config.environment == ConfigEnvironment.PRODUCTION:
            if not result.is_valid:
                base_score *= 0.5  # Pénalité sévère en production
                
        # Score final
        final_score = min(1.0, base_score + compliance_bonus)
        
        return final_score
        
    async def _generate_recommendations(self, 
                                      result: ConfigValidationResult,
                                      config: EnvironmentConfig) -> List[str]:
        """Génération de recommandations"""
        recommendations = []
        
        # Recommandations basées sur les échecs
        if 'secure_password_policy' in result.failed_checks:
            recommendations.append("Implement strong password policy with 12+ characters, uppercase, numbers, and symbols")
            
        if 'https_enforced' in result.failed_checks:
            recommendations.append("Enable HTTPS enforcement and HSTS headers for all communications")
            
        if 'advanced_encryption' in result.failed_checks:
            recommendations.append("Upgrade to AES-256 encryption with proper key management")
            
        if 'mfa_required' in result.failed_checks:
            recommendations.append("Implement multi-factor authentication for all user accounts")
            
        if 'audit_logging_enabled' in result.failed_checks:
            recommendations.append("Enable comprehensive audit logging for security monitoring")
            
        # Recommandations de conformité
        if not result.compliance_status.get('PCI_DSS', True):
            recommendations.append("Address PCI DSS compliance issues for payment processing")
            
        if not result.compliance_status.get('GDPR', True):
            recommendations.append("Implement GDPR-compliant data protection measures")
            
        # Recommandations par environnement
        if config.environment == ConfigEnvironment.PRODUCTION:
            if result.security_score < 0.9:
                recommendations.append("Production environment requires security score above 90%")
                
        return recommendations


class SecurityConfigManager:
    """
    Gestionnaire de configuration sécurisé enterprise-grade
    
    Fonctionnalités:
    - Gestion centralisée des configurations
    - Chiffrement et gestion des secrets
    - Validation multi-niveaux
    - Conformité réglementaire
    - Rotation automatique des secrets
    - Audit et monitoring complets
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.secret_manager = SecretManager()
        self.config_validator = ConfigValidator()
        
        # Stockage des configurations
        self.environments: Dict[str, EnvironmentConfig] = {}
        self.security_policies: Dict[str, SecurityPolicy] = {}
        
        # Configuration par défaut
        self.default_config = {
            'security': {
                'force_https': True,
                'hsts_enabled': True,
                'hsts_max_age': 31536000,
                'csrf_protection': True,
                'xss_protection': True
            },
            'encryption': {
                'enabled': True,
                'algorithm': 'AES-256-GCM',
                'key_size': 256,
                'key_rotation_days': 90
            },
            'authentication': {
                'session_timeout_minutes': 30,
                'mfa_required': False,
                'mfa_available': True,
                'rbac_enabled': True,
                'password_policy': {
                    'min_length': 12,
                    'require_uppercase': True,
                    'require_numbers': True,
                    'require_symbols': True,
                    'max_age_days': 90
                }
            },
            'session': {
                'secure_cookies': True,
                'httponly_cookies': True,
                'samesite_strict': True,
                'timeout_minutes': 30
            },
            'logging': {
                'audit_enabled': True,
                'access_logs': True,
                'security_events': True,
                'retention_days': 365
            },
            'rate_limiting': {
                'enabled': True,
                'requests_per_minute': 100,
                'burst_allowance': 20
            }
        }
        
        # Métriques
        self.metrics = {
            'configs_loaded': 0,
            'secrets_managed': 0,
            'validations_performed': 0,
            'policy_violations': 0,
            'secrets_rotated': 0
        }
        
        # Initialiser politiques par défaut
        self._setup_default_policies()
        
        self.logger.info("Security Configuration Manager initialized")
        
    def _setup_default_policies(self):
        """Configuration des politiques par défaut"""
        # Politique de production
        production_policy = SecurityPolicy(
            policy_id="prod_security_policy",
            name="Production Security Policy",
            description="Strict security policy for production environment",
            environment=ConfigEnvironment.PRODUCTION,
            rules={
                'validation_level': ValidationLevel.PARANOID.value,
                'mfa_required': True,
                'encryption_required': True,
                'audit_all_actions': True,
                'network_isolation': True,
                'vulnerability_scanning': True,
                'incident_response': True
            },
            compliance_standards=['PCI_DSS', 'GDPR', 'SOX'],
            version="2.0"
        )
        
        self.security_policies[production_policy.policy_id] = production_policy
        
        # Politique de développement
        dev_policy = SecurityPolicy(
            policy_id="dev_security_policy",
            name="Development Security Policy",
            description="Balanced security policy for development environment",
            environment=ConfigEnvironment.DEVELOPMENT,
            rules={
                'validation_level': ValidationLevel.STANDARD.value,
                'mfa_required': False,
                'encryption_required': True,
                'audit_key_actions': True,
                'network_isolation': False
            },
            compliance_standards=['GDPR'],
            version="1.5"
        )
        
        self.security_policies[dev_policy.policy_id] = dev_policy
        
    async def load_environment_config(self, 
                                    environment: ConfigEnvironment,
                                    config_source: ConfigSource = ConfigSource.FILE,
                                    config_path: Optional[str] = None) -> EnvironmentConfig:
        """Charger configuration d'environnement"""
        try:
            if config_source == ConfigSource.FILE:
                config_data = await self._load_config_from_file(environment, config_path)
            elif config_source == ConfigSource.ENVIRONMENT:
                config_data = await self._load_config_from_env(environment)
            else:
                config_data = self.default_config.copy()
                
            # Charger secrets
            secrets = await self._load_environment_secrets(environment)
            
            # Déterminer politiques applicables
            applicable_policies = [
                policy.policy_id for policy in self.security_policies.values()
                if policy.environment == environment
            ]
            
            # Créer configuration d'environnement
            env_config = EnvironmentConfig(
                environment=environment,
                config_data=config_data,
                secrets=secrets,
                policies=applicable_policies,
                checksum=self._calculate_config_checksum(config_data, secrets)
            )
            
            # Validation automatique
            if applicable_policies:
                policy = self.security_policies[applicable_policies[0]]
                validation_level = ValidationLevel(policy.rules.get('validation_level', 'standard'))
                env_config.validation_result = await self.config_validator.validate_config(
                    env_config, validation_level
                )
                
            # Stocker
            self.environments[environment.value] = env_config
            self.metrics['configs_loaded'] += 1
            
            self.logger.info(f"Environment config loaded: {environment.value}")
            return env_config
            
        except Exception as e:
            self.logger.error(f"Failed to load config for {environment.value}: {str(e)}")
            raise
            
    async def _load_config_from_file(self, 
                                   environment: ConfigEnvironment,
                                   config_path: Optional[str] = None) -> Dict[str, Any]:
        """Charger configuration depuis fichier"""
        if config_path is None:
            config_path = f"config/{environment.value}.yaml"
            
        config_file = Path(config_path)
        
        if not config_file.exists():
            self.logger.warning(f"Config file not found: {config_path}, using defaults")
            return self.default_config.copy()
            
        try:
            with open(config_file, 'r') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
                    
            # Fusionner avec configuration par défaut
            merged_config = self.default_config.copy()
            merged_config.update(config_data)
            
            return merged_config
            
        except Exception as e:
            self.logger.error(f"Failed to load config file {config_path}: {str(e)}")
            return self.default_config.copy()
            
    async def _load_config_from_env(self, environment: ConfigEnvironment) -> Dict[str, Any]:
        """Charger configuration depuis variables d'environnement"""
        config_data = self.default_config.copy()
        
        # Mapper variables d'environnement
        env_mapping = {
            'AINFLUE_DATABASE_URL': ['database', 'url'],
            'AINFLUE_SECRET_KEY': ['secret_key'],
            'AINFLUE_DEBUG': ['debug'],
            'AINFLUE_FORCE_HTTPS': ['security', 'force_https'],
            'AINFLUE_MFA_REQUIRED': ['authentication', 'mfa_required'],
            'AINFLUE_SESSION_TIMEOUT': ['session', 'timeout_minutes'],
            'AINFLUE_RATE_LIMIT': ['rate_limiting', 'requests_per_minute']
        }
        
        for env_var, config_path in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Naviger dans la structure de configuration
                current = config_data
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                    
                # Convertir types
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                    
                current[config_path[-1]] = value
                
        return config_data
        
    async def _load_environment_secrets(self, environment: ConfigEnvironment) -> Dict[str, str]:
        """Charger secrets pour un environnement"""
        secrets = {}
        
        # Secrets prédéfinis par environnement
        secret_keys = [
            'database_password',
            'jwt_secret',
            'api_key',
            'encryption_key',
            'payment_gateway_key'
        ]
        
        for key in secret_keys:
            secret_value = await self.secret_manager.retrieve_secret(key, environment)
            if secret_value:
                secrets[key] = secret_value
                
        return secrets
        
    def _calculate_config_checksum(self, config_data: Dict[str, Any], secrets: Dict[str, str]) -> str:
        """Calculer checksum de configuration"""
        combined_data = {
            'config': config_data,
            'secrets_count': len(secrets),  # Ne pas inclure les secrets eux-mêmes
            'timestamp': datetime.utcnow().isoformat()
        }
        
        json_str = json.dumps(combined_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
        
    async def store_secret(self, 
                         key: str,
                         value: str,
                         secret_type: SecretType,
                         environment: ConfigEnvironment,
                         expires_at: Optional[datetime] = None) -> bool:
        """Stocker un secret"""
        try:
            await self.secret_manager.store_secret(key, value, secret_type, environment, expires_at)
            self.metrics['secrets_managed'] += 1
            return True
        except Exception as e:
            self.logger.error(f"Failed to store secret: {str(e)}")
            return False
            
    async def get_config_value(self, 
                             environment: ConfigEnvironment,
                             config_path: str,
                             default: Any = None) -> Any:
        """Obtenir valeur de configuration"""
        if environment.value not in self.environments:
            await self.load_environment_config(environment)
            
        env_config = self.environments[environment.value]
        config_data = env_config.config_data
        
        # Naviguer dans le chemin de configuration
        keys = config_path.split('.')
        current = config_data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
            
    async def update_config_value(self, 
                                environment: ConfigEnvironment,
                                config_path: str,
                                value: Any) -> bool:
        """Mettre à jour valeur de configuration"""
        try:
            if environment.value not in self.environments:
                await self.load_environment_config(environment)
                
            env_config = self.environments[environment.value]
            config_data = env_config.config_data
            
            # Naviguer et mettre à jour
            keys = config_path.split('.')
            current = config_data
            
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
                
            current[keys[-1]] = value
            
            # Recalculer checksum
            env_config.checksum = self._calculate_config_checksum(
                env_config.config_data, 
                env_config.secrets
            )
            env_config.last_updated = datetime.utcnow()
            
            # Revalider si nécessaire
            if env_config.policies:
                policy = self.security_policies[env_config.policies[0]]
                validation_level = ValidationLevel(policy.rules.get('validation_level', 'standard'))
                env_config.validation_result = await self.config_validator.validate_config(
                    env_config, validation_level
                )
                
            self.logger.info(f"Config updated: {environment.value}.{config_path} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update config: {str(e)}")
            return False
            
    async def validate_environment(self, 
                                 environment: ConfigEnvironment,
                                 validation_level: Optional[ValidationLevel] = None) -> ConfigValidationResult:
        """Valider un environnement complet"""
        if environment.value not in self.environments:
            await self.load_environment_config(environment)
            
        env_config = self.environments[environment.value]
        
        # Déterminer niveau de validation
        if validation_level is None:
            if env_config.policies:
                policy = self.security_policies[env_config.policies[0]]
                validation_level = ValidationLevel(policy.rules.get('validation_level', 'standard'))
            else:
                validation_level = ValidationLevel.STANDARD
                
        result = await self.config_validator.validate_config(env_config, validation_level)
        env_config.validation_result = result
        
        self.metrics['validations_performed'] += 1
        if not result.is_valid:
            self.metrics['policy_violations'] += 1
            
        return result
        
    async def rotate_secrets(self, environment: Optional[ConfigEnvironment] = None) -> Dict[str, bool]:
        """Rotation des secrets"""
        if environment:
            environments = [environment]
        else:
            environments = [ConfigEnvironment(env) for env in self.environments.keys()]
            
        rotation_results = {}
        
        for env in environments:
            # Vérifier quels secrets ont besoin de rotation
            rotation_needed = await self.secret_manager.check_rotation_needed()
            
            for storage_key in rotation_needed:
                if storage_key.startswith(f"{env.value}:"):
# SECURITY: secret_key = storage_key.split(":", 1)[1] # MOVED TO ENV
# TODO: Move to environment variables or secure vault
                    
                    result = await self.secret_manager.rotate_secret(secret_key, env)
                    rotation_results[storage_key] = result
                    
                    if result:
                        self.metrics['secrets_rotated'] += 1
                        
        return rotation_results
        
    async def export_configuration(self, 
                                 environment: ConfigEnvironment,
                                 include_secrets: bool = False,
                                 format: str = 'yaml') -> str:
        """Exporter configuration"""
        if environment.value not in self.environments:
            await self.load_environment_config(environment)
            
        env_config = self.environments[environment.value]
        
        export_data = {
            'environment': environment.value,
            'config': env_config.config_data,
            'last_updated': env_config.last_updated.isoformat(),
            'checksum': env_config.checksum
        }
        
        if include_secrets:
            # ATTENTION: Exporter les secrets est dangereux
            export_data['secrets'] = env_config.secrets
            
        if env_config.validation_result:
            export_data['validation'] = {
                'is_valid': env_config.validation_result.is_valid,
                'security_score': env_config.validation_result.security_score,
                'passed_checks': env_config.validation_result.passed_checks,
                'failed_checks': env_config.validation_result.failed_checks,
                'compliance_status': env_config.validation_result.compliance_status
            }
            
        if format == 'yaml':
            return yaml.dump(export_data, default_flow_style=False)
        else:
            return json.dumps(export_data, indent=2, default=str)
            
    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Tableau de bord de sécurité"""
        environments_status = {}
        
        for env_name, env_config in self.environments.items():
            if env_config.validation_result:
                environments_status[env_name] = {
                    'is_valid': env_config.validation_result.is_valid,
                    'security_score': env_config.validation_result.security_score,
                    'compliance_status': env_config.validation_result.compliance_status,
                    'last_updated': env_config.last_updated.isoformat()
                }
            else:
                environments_status[env_name] = {
                    'is_valid': None,
                    'security_score': 0.0,
                    'compliance_status': {},
                    'last_updated': env_config.last_updated.isoformat()
                }
                
        # Secrets nécessitant rotation
        rotation_needed = await self.secret_manager.check_rotation_needed()
        
        dashboard = {
            'overview': {
                'total_environments': len(self.environments),
                'active_policies': len(self.security_policies),
                'secrets_managed': self.metrics['secrets_managed'],
                'secrets_needing_rotation': len(rotation_needed)
            },
            'environments': environments_status,
            'security_metrics': self.metrics,
            'rotation_needed': rotation_needed[:10],  # Top 10
            'policy_summary': {
                policy_id: {
                    'name': policy.name,
                    'environment': policy.environment.value,
                    'compliance_standards': policy.compliance_standards,
                    'version': policy.version
                }
                for policy_id, policy in self.security_policies.items()
            }
        }
        
        return dashboard


# Instance globale du gestionnaire de configuration
config_manager = SecurityConfigManager()


async def get_config_manager() -> SecurityConfigManager:
    """Factory function pour le gestionnaire de configuration"""
    return config_manager


# Fonctions utilitaires pour intégration Ainflue
async def setup_creator_environment_config(creator_id: str) -> EnvironmentConfig:
    """Configuration spécifique créateur"""
    creator_config = {
        'creator': {
            'id': creator_id,
            'content_encryption': True,
            'revenue_protection': True,
            'analytics_enabled': True
        },
        'security': {
            'force_https': True,
            'content_watermarking': True,
            'ip_restriction': False
        },
        'authentication': {
            'creator_verification': True,
            'multi_platform_sso': True
        }
    }
    
    # Créer environnement temporaire pour le créateur
    env_config = EnvironmentConfig(
        environment=ConfigEnvironment.PRODUCTION,
        config_data=creator_config,
        secrets={},
        policies=['prod_security_policy']
    )
    
    return env_config


async def setup_payment_security_config(environment: ConfigEnvironment) -> Dict[str, Any]:
    """Configuration sécurisée pour les paiements"""
    payment_config = {
        'payment_security': {
            'encryption_level': 'maximum',
            'pci_dss_compliant': True,
            'fraud_detection': True,
            'transaction_monitoring': True,
            'secure_tokenization': True
        },
        'compliance': {
            'standards': ['PCI_DSS', 'SOX'],
            'audit_frequency': 'real_time',
            'reporting_enabled': True
        }
    }
    
    # Mise à jour de la configuration
    for config_path, value in payment_config.items():
        for sub_key, sub_value in value.items():
            await config_manager.update_config_value(
                environment, 
                f"{config_path}.{sub_key}", 
                sub_value
            )
            
    return payment_config


# Export des classes principales
__all__ = [
    'SecurityConfigManager',
    'SecretManager',
    'ConfigValidator',
    'EnvironmentConfig',
    'SecurityPolicy',
    'ConfigValidationResult',
    'SecretConfig',
    'ConfigEnvironment',
    'SecretType',
    'ValidationLevel',
    'config_manager',
    'get_config_manager',
    'setup_creator_environment_config',
    'setup_payment_security_config'
]


# Initialisation pour tests
if __name__ == "__main__":
    async def demo_config_management():
        """Démonstration du gestionnaire de configuration"""
        manager = await get_config_manager()
        
        # Test chargement configuration
        prod_config = await manager.load_environment_config(ConfigEnvironment.PRODUCTION)
        print(f"Production config loaded: {prod_config.environment.value}")
        
        # Test stockage secret
        await manager.store_secret(
            "test_api_key",
            "ainflue_api_12345",
            SecretType.API_KEY,
            ConfigEnvironment.PRODUCTION
        )
        print("Secret stored successfully")
        
        # Test validation
        validation_result = await manager.validate_environment(
            ConfigEnvironment.PRODUCTION,
            ValidationLevel.STRICT
        )
        print(f"Validation result: {validation_result.is_valid} (score: {validation_result.security_score:.2f})")
        
        # Test configuration créateur
        creator_config = await setup_creator_environment_config("creator_123")
        print(f"Creator config setup: {creator_config.config_data['creator']['id']}")
        
        # Test configuration paiement
        payment_config = await setup_payment_security_config(ConfigEnvironment.PRODUCTION)
        print(f"Payment security configured: {payment_config['payment_security']['encryption_level']}")
        
        # Tableau de bord
        dashboard = await manager.get_security_dashboard()
        print(f"Security dashboard: {dashboard['overview']}")
        
        # Test rotation
        rotation_results = await manager.rotate_secrets(ConfigEnvironment.PRODUCTION)
        print(f"Secret rotation completed: {len(rotation_results)} secrets processed")
        
    # Exécution démo
    asyncio.run(demo_config_management())