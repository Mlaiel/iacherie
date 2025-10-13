#!/usr/bin/env python3
"""
🔐 Multi Tenant Key Isolator - Enterprise Multi-Tenancy Cryptographic Isolation System
Production-grade tenant isolation for IA Chérie Creator Economy Platform

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import hashlib
import secrets
import base64
import json
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import yaml
from pathlib import Path
import uuid

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

logger = logging.getLogger(__name__)


class TenantTier(Enum):
    """Tenant service tiers."""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    PREMIUM_CREATOR = "premium_creator"


class IsolationLevel(Enum):
    """Cryptographic isolation levels."""
    LOGICAL = "logical"          # Shared infrastructure, logical separation
    PHYSICAL = "physical"        # Dedicated hardware
    GEOGRAPHIC = "geographic"    # Geographic separation
    REGULATORY = "regulatory"    # Regulatory compliance isolation
    QUANTUM_SAFE = "quantum_safe"  # Post-quantum isolation


class TenantType(Enum):
    """Types of tenants in the system."""
    INDIVIDUAL_CREATOR = "individual_creator"
    CREATOR_COLLECTIVE = "creator_collective"
    ENTERPRISE_CLIENT = "enterprise_client"
    PLATFORM_PARTNER = "platform_partner"
    GOVERNMENT_ENTITY = "government_entity"
    EDUCATIONAL_INSTITUTION = "educational_institution"


class KeyScope(Enum):
    """Scope of cryptographic keys."""
    TENANT_GLOBAL = "tenant_global"        # Accessible across tenant
    CREATOR_SPECIFIC = "creator_specific"  # Specific to one creator
    CONTENT_SPECIFIC = "content_specific"  # Specific to content type
    SESSION_SPECIFIC = "session_specific"  # Specific to user session
    TRANSACTION_SPECIFIC = "transaction_specific"  # One-time use


@dataclass
class TenantProfile:
    """Multi-tenant profile configuration."""
    tenant_id: str
    tenant_name: str
    tenant_type: TenantType
    tier: TenantTier
    isolation_level: IsolationLevel
    geographic_region: str
    compliance_requirements: List[str]
    data_residency_rules: Dict[str, str]
    key_management_policy: Dict[str, Any]
    creator_count: int
    storage_quota_gb: int
    api_rate_limits: Dict[str, int]
    encryption_algorithms: List[str]
    created_at: datetime
    updated_at: datetime
    active: bool = True


@dataclass
class TenantKeyNamespace:
    """Tenant key namespace definition."""
    tenant_id: str
    namespace_id: str
    namespace_name: str
    scope: KeyScope
    encryption_domain: str  # Cryptographic domain identifier
    key_derivation_path: str  # BIP32-style derivation path
    isolation_boundaries: List[str]
    allowed_operations: List[str]
    access_policies: Dict[str, Any]
    created_at: datetime
    last_accessed: Optional[datetime] = None


@dataclass
class TenantKey:
    """Isolated tenant key."""
    key_id: str
    tenant_id: str
    namespace_id: str
    key_scope: KeyScope
    key_material: bytes
    algorithm: str
    key_metadata: Dict[str, Any]
    derivation_info: Dict[str, Any]
    isolation_tags: List[str]
    access_count: int
    created_at: datetime
    expires_at: Optional[datetime]
    creator_id: Optional[str] = None
    content_type: Optional[str] = None


@dataclass
class CrossTenantAccessRequest:
    """Cross-tenant access request."""
    request_id: str
    source_tenant_id: str
    target_tenant_id: str
    requested_resource: str
    access_type: str
    justification: str
    requester_id: str
    approval_status: str
    created_at: datetime
    expires_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


class MultiTenantKeyIsolator:
    """
    🔐 Multi Tenant Key Isolator - Enterprise Cryptographic Tenant Isolation
    
    Provides comprehensive multi-tenant key isolation for IA Chérie Creator Economy:
    - Cryptographic isolation between tenants
    - Creator-specific key namespaces within tenants
    - Content-type specific isolation boundaries
    - Cross-tenant access controls and monitoring
    - Compliance-driven data residency enforcement
    - Performance-optimized tenant key management
    - Geographic and regulatory isolation support
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize Multi Tenant Key Isolator."""
        self.config = self._load_configuration(config_path)
        self.tenant_profiles: Dict[str, TenantProfile] = {}
        self.tenant_namespaces: Dict[str, Dict[str, TenantKeyNamespace]] = {}
        self.tenant_keys: Dict[str, Dict[str, TenantKey]] = {}
        self.cross_tenant_requests: Dict[str, CrossTenantAccessRequest] = {}
        self.isolation_metrics: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Master tenant derivation key (in production, stored in HSM)
        self.master_tenant_key = self._derive_master_tenant_key()
        
        # Initialize default tenant configurations
        self._initialize_default_configurations()

    def _load_configuration(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load multi-tenant isolator configuration."""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f).get('multi_tenant_config', {})
        
        # Default configuration
        return {
            "default_isolation_level": IsolationLevel.LOGICAL.value,
            "cross_tenant_access_enabled": False,
            "geographic_isolation_enabled": True,
            "compliance_isolation_enabled": True,
            "key_derivation_depth": 5,
            "namespace_auto_creation": True,
            "isolation_monitoring": True,
            "audit_all_operations": True,
            "tenant_key_rotation_days": 90,
            "emergency_access_enabled": True
        }

    def _derive_master_tenant_key(self) -> bytes:
        """Derive master tenant isolation key."""
        # In production, this would come from HSM or secure key store
        seed = b"iacherie_multi_tenant_master_key_v1_2025"
        return hashlib.pbkdf2_hmac('sha256', seed, b'tenant_isolation_salt', 100000)

    def _initialize_default_configurations(self):
        """Initialize default tenant type configurations."""
        # Creator-specific configurations
        self.creator_tier_configs = {
            TenantTier.FREE: {
                "max_creators": 1,
                "max_storage_gb": 1,
                "isolation_level": IsolationLevel.LOGICAL,
                "key_retention_days": 365,
                "cross_tenant_access": False
            },
            TenantTier.BASIC: {
                "max_creators": 5,
                "max_storage_gb": 10,
                "isolation_level": IsolationLevel.LOGICAL,
                "key_retention_days": 730,
                "cross_tenant_access": False
            },
            TenantTier.PROFESSIONAL: {
                "max_creators": 25,
                "max_storage_gb": 100,
                "isolation_level": IsolationLevel.PHYSICAL,
                "key_retention_days": 1825,
                "cross_tenant_access": True
            },
            TenantTier.ENTERPRISE: {
                "max_creators": 1000,
                "max_storage_gb": 1000,
                "isolation_level": IsolationLevel.GEOGRAPHIC,
                "key_retention_days": 2555,
                "cross_tenant_access": True
            },
            TenantTier.PREMIUM_CREATOR: {
                "max_creators": 1,
                "max_storage_gb": 500,
                "isolation_level": IsolationLevel.PHYSICAL,
                "key_retention_days": 1825,
                "cross_tenant_access": False
            }
        }

    async def register_tenant(self,
                             tenant_name: str,
                             tenant_type: TenantType,
                             tier: TenantTier,
                             geographic_region: str,
                             compliance_requirements: List[str],
                             data_residency_rules: Dict[str, str]) -> str:
        """
        Register a new tenant with isolation configuration.
        
        Args:
            tenant_name: Human-readable tenant name
            tenant_type: Type of tenant (creator, enterprise, etc.)
            tier: Service tier
            geographic_region: Geographic region for data residency
            compliance_requirements: Required compliance frameworks
            data_residency_rules: Data residency requirements
            
        Returns:
            Tenant ID
        """
        try:
            tenant_id = f"tenant_{secrets.token_hex(16)}"
            
            # Determine isolation level based on tier and compliance
            isolation_level = self._determine_isolation_level(tier, compliance_requirements)
            
            # Get tier configuration
            tier_config = self.creator_tier_configs.get(tier, self.creator_tier_configs[TenantTier.BASIC])
            
            # Create tenant profile
            tenant_profile = TenantProfile(
                tenant_id=tenant_id,
                tenant_name=tenant_name,
                tenant_type=tenant_type,
                tier=tier,
                isolation_level=isolation_level,
                geographic_region=geographic_region,
                compliance_requirements=compliance_requirements,
                data_residency_rules=data_residency_rules,
                key_management_policy=self._create_key_management_policy(tier, compliance_requirements),
                creator_count=0,
                storage_quota_gb=tier_config["max_storage_gb"],
                api_rate_limits=self._create_api_rate_limits(tier),
                encryption_algorithms=self._get_allowed_algorithms(compliance_requirements),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store tenant profile
            self.tenant_profiles[tenant_id] = tenant_profile
            
            # Initialize tenant key storage
            self.tenant_keys[tenant_id] = {}
            self.tenant_namespaces[tenant_id] = {}
            
            # Create default namespaces
            await self._create_default_namespaces(tenant_id)
            
            # Log tenant registration
            await self._log_tenant_operation("TENANT_REGISTERED", tenant_id, "system", {
                "tenant_name": tenant_name,
                "tenant_type": tenant_type.value,
                "tier": tier.value,
                "isolation_level": isolation_level.value,
                "geographic_region": geographic_region
            })
            
            self.logger.info(f"Tenant registered: {tenant_id} ({tenant_name})")
            return tenant_id
            
        except Exception as e:
            self.logger.error(f"Tenant registration failed: {e}")
            raise

    def _determine_isolation_level(self, tier: TenantTier, compliance_requirements: List[str]) -> IsolationLevel:
        """Determine appropriate isolation level."""
        # High-security compliance requirements
        if any(req in ["FIPS_140_2", "Common_Criteria", "FedRAMP"] for req in compliance_requirements):
            return IsolationLevel.PHYSICAL
        
        # Geographic requirements
        if "GDPR" in compliance_requirements:
            return IsolationLevel.GEOGRAPHIC
        
        # Tier-based isolation
        tier_isolation = {
            TenantTier.FREE: IsolationLevel.LOGICAL,
            TenantTier.BASIC: IsolationLevel.LOGICAL,
            TenantTier.PROFESSIONAL: IsolationLevel.PHYSICAL,
            TenantTier.ENTERPRISE: IsolationLevel.GEOGRAPHIC,
            TenantTier.PREMIUM_CREATOR: IsolationLevel.PHYSICAL
        }
        
        return tier_isolation.get(tier, IsolationLevel.LOGICAL)

    def _create_key_management_policy(self, tier: TenantTier, compliance_requirements: List[str]) -> Dict[str, Any]:
        """Create key management policy for tenant."""
        tier_config = self.creator_tier_configs.get(tier, self.creator_tier_configs[TenantTier.BASIC])
        
        return {
            "key_rotation_interval_days": tier_config["key_retention_days"] // 10,
            "key_backup_enabled": tier in [TenantTier.PROFESSIONAL, TenantTier.ENTERPRISE],
            "hsm_required": "FIPS_140_2" in compliance_requirements,
            "quantum_safe_required": "POST_QUANTUM" in compliance_requirements,
            "key_escrow_required": "LEGAL_HOLD" in compliance_requirements,
            "cross_region_replication": tier == TenantTier.ENTERPRISE,
            "audit_logging": True,
            "compliance_frameworks": compliance_requirements
        }

    def _create_api_rate_limits(self, tier: TenantTier) -> Dict[str, int]:
        """Create API rate limits for tenant tier."""
        rate_limits = {
            TenantTier.FREE: {"requests_per_minute": 100, "key_operations_per_hour": 50},
            TenantTier.BASIC: {"requests_per_minute": 500, "key_operations_per_hour": 200},
            TenantTier.PROFESSIONAL: {"requests_per_minute": 2000, "key_operations_per_hour": 1000},
            TenantTier.ENTERPRISE: {"requests_per_minute": 10000, "key_operations_per_hour": 5000},
            TenantTier.PREMIUM_CREATOR: {"requests_per_minute": 1000, "key_operations_per_hour": 500}
        }
        
        return rate_limits.get(tier, rate_limits[TenantTier.BASIC])

    def _get_allowed_algorithms(self, compliance_requirements: List[str]) -> List[str]:
        """Get allowed encryption algorithms based on compliance."""
        base_algorithms = ["AES-256-GCM", "ChaCha20-Poly1305", "RSA-4096", "ECDSA-P384"]
        
        if "FIPS_140_2" in compliance_requirements:
            return ["AES-256-GCM", "RSA-4096", "ECDSA-P384"]  # FIPS-approved only
        
        if "POST_QUANTUM" in compliance_requirements:
            base_algorithms.extend(["Kyber-768", "Dilithium-3", "Falcon-1024"])
        
        return base_algorithms

    async def _create_default_namespaces(self, tenant_id: str):
        """Create default key namespaces for tenant."""
        default_namespaces = [
            {
                "name": "user_authentication",
                "scope": KeyScope.TENANT_GLOBAL,
                "domain": "auth",
                "operations": ["encrypt", "decrypt", "sign", "verify"]
            },
            {
                "name": "content_protection",
                "scope": KeyScope.CREATOR_SPECIFIC,
                "domain": "content",
                "operations": ["encrypt", "decrypt", "watermark"]
            },
            {
                "name": "financial_transactions",
                "scope": KeyScope.TRANSACTION_SPECIFIC,
                "domain": "finance",
                "operations": ["encrypt", "decrypt", "sign"]
            },
            {
                "name": "session_management",
                "scope": KeyScope.SESSION_SPECIFIC,
                "domain": "session",
                "operations": ["encrypt", "decrypt"]
            }
        ]
        
        for ns_config in default_namespaces:
            await self.create_key_namespace(
                tenant_id=tenant_id,
                namespace_name=ns_config["name"],
                scope=ns_config["scope"],
                encryption_domain=ns_config["domain"],
                allowed_operations=ns_config["operations"]
            )

    async def create_key_namespace(self,
                                  tenant_id: str,
                                  namespace_name: str,
                                  scope: KeyScope,
                                  encryption_domain: str,
                                  allowed_operations: List[str],
                                  access_policies: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new key namespace within a tenant.
        
        Args:
            tenant_id: Target tenant ID
            namespace_name: Name of the namespace
            scope: Scope of keys in this namespace
            encryption_domain: Cryptographic domain identifier
            allowed_operations: Permitted operations
            access_policies: Optional access control policies
            
        Returns:
            Namespace ID
        """
        try:
            if tenant_id not in self.tenant_profiles:
                raise ValueError(f"Tenant not found: {tenant_id}")
            
            namespace_id = f"ns_{tenant_id}_{secrets.token_hex(8)}"
            
            # Create key derivation path
            derivation_path = self._create_derivation_path(tenant_id, namespace_name, scope)
            
            # Define isolation boundaries
            isolation_boundaries = self._define_isolation_boundaries(tenant_id, scope, encryption_domain)
            
            namespace = TenantKeyNamespace(
                tenant_id=tenant_id,
                namespace_id=namespace_id,
                namespace_name=namespace_name,
                scope=scope,
                encryption_domain=encryption_domain,
                key_derivation_path=derivation_path,
                isolation_boundaries=isolation_boundaries,
                allowed_operations=allowed_operations,
                access_policies=access_policies or {},
                created_at=datetime.utcnow()
            )
            
            # Store namespace
            if tenant_id not in self.tenant_namespaces:
                self.tenant_namespaces[tenant_id] = {}
            
            self.tenant_namespaces[tenant_id][namespace_id] = namespace
            
            # Log namespace creation
            await self._log_tenant_operation("NAMESPACE_CREATED", tenant_id, "system", {
                "namespace_id": namespace_id,
                "namespace_name": namespace_name,
                "scope": scope.value,
                "encryption_domain": encryption_domain
            })
            
            self.logger.info(f"Key namespace created: {namespace_id} for tenant {tenant_id}")
            return namespace_id
            
        except Exception as e:
            self.logger.error(f"Namespace creation failed: {e}")
            raise

    def _create_derivation_path(self, tenant_id: str, namespace_name: str, scope: KeyScope) -> str:
        """Create BIP32-style key derivation path."""
        # Create deterministic path based on tenant and namespace
        tenant_hash = hashlib.sha256(tenant_id.encode()).hexdigest()[:8]
        namespace_hash = hashlib.sha256(namespace_name.encode()).hexdigest()[:8]
        scope_index = list(KeyScope).index(scope)
        
        return f"m/44'/0'/{tenant_hash}/{namespace_hash}/{scope_index}'"

    def _define_isolation_boundaries(self, tenant_id: str, scope: KeyScope, domain: str) -> List[str]:
        """Define cryptographic isolation boundaries."""
        boundaries = [f"tenant:{tenant_id}"]
        
        if scope == KeyScope.CREATOR_SPECIFIC:
            boundaries.append("creator:*")
        elif scope == KeyScope.CONTENT_SPECIFIC:
            boundaries.extend(["creator:*", "content_type:*"])
        elif scope == KeyScope.SESSION_SPECIFIC:
            boundaries.extend(["user:*", "session:*"])
        elif scope == KeyScope.TRANSACTION_SPECIFIC:
            boundaries.extend(["user:*", "transaction:*"])
        
        boundaries.append(f"domain:{domain}")
        
        return boundaries

    async def generate_tenant_key(self,
                                 tenant_id: str,
                                 namespace_id: str,
                                 algorithm: str,
                                 key_purpose: str,
                                 creator_id: Optional[str] = None,
                                 content_type: Optional[str] = None,
                                 expires_in_days: Optional[int] = None) -> str:
        """
        Generate a new isolated key for a tenant.
        
        Args:
            tenant_id: Target tenant ID
            namespace_id: Target namespace ID
            algorithm: Encryption algorithm
            key_purpose: Purpose of the key
            creator_id: Optional creator ID for creator-specific keys
            content_type: Optional content type
            expires_in_days: Optional expiration in days
            
        Returns:
            Key ID
        """
        try:
            # Validate tenant and namespace
            if tenant_id not in self.tenant_profiles:
                raise ValueError(f"Tenant not found: {tenant_id}")
            
            if (tenant_id not in self.tenant_namespaces or 
                namespace_id not in self.tenant_namespaces[tenant_id]):
                raise ValueError(f"Namespace not found: {namespace_id}")
            
            namespace = self.tenant_namespaces[tenant_id][namespace_id]
            tenant_profile = self.tenant_profiles[tenant_id]
            
            # Validate algorithm is allowed
            if algorithm not in tenant_profile.encryption_algorithms:
                raise ValueError(f"Algorithm not allowed for tenant: {algorithm}")
            
            # Validate scope requirements
            if namespace.scope == KeyScope.CREATOR_SPECIFIC and not creator_id:
                raise ValueError("Creator ID required for creator-specific namespace")
            
            # Generate key ID
            key_id = f"key_{tenant_id}_{namespace_id}_{secrets.token_hex(12)}"
            
            # Derive tenant-specific key material
            key_material = await self._derive_tenant_key(
                tenant_id, namespace_id, key_id, algorithm, creator_id, content_type
            )
            
            # Create isolation tags
            isolation_tags = self._create_isolation_tags(tenant_id, namespace.scope, creator_id, content_type)
            
            # Set expiration
            expires_at = None
            if expires_in_days:
                expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            
            # Create tenant key
            tenant_key = TenantKey(
                key_id=key_id,
                tenant_id=tenant_id,
                namespace_id=namespace_id,
                key_scope=namespace.scope,
                key_material=key_material,
                algorithm=algorithm,
                key_metadata={
                    "purpose": key_purpose,
                    "derivation_path": namespace.key_derivation_path,
                    "isolation_level": tenant_profile.isolation_level.value,
                    "compliance_requirements": tenant_profile.compliance_requirements
                },
                derivation_info={
                    "master_key_version": "v1",
                    "derivation_method": "HKDF-SHA256",
                    "context": f"{tenant_id}:{namespace_id}:{key_purpose}"
                },
                isolation_tags=isolation_tags,
                access_count=0,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                creator_id=creator_id,
                content_type=content_type
            )
            
            # Store key
            self.tenant_keys[tenant_id][key_id] = tenant_key
            
            # Log key generation
            await self._log_tenant_operation("KEY_GENERATED", tenant_id, "system", {
                "key_id": key_id,
                "namespace_id": namespace_id,
                "algorithm": algorithm,
                "purpose": key_purpose,
                "creator_id": creator_id,
                "content_type": content_type
            })
            
            self.logger.info(f"Tenant key generated: {key_id} for tenant {tenant_id}")
            return key_id
            
        except Exception as e:
            self.logger.error(f"Tenant key generation failed: {e}")
            raise

    async def _derive_tenant_key(self,
                                tenant_id: str,
                                namespace_id: str,
                                key_id: str,
                                algorithm: str,
                                creator_id: Optional[str],
                                content_type: Optional[str]) -> bytes:
        """Derive cryptographically isolated key material."""
        # Create derivation context
        context_parts = [tenant_id, namespace_id, key_id, algorithm]
        
        if creator_id:
            context_parts.append(f"creator:{creator_id}")
        if content_type:
            context_parts.append(f"content:{content_type}")
        
        context = ":".join(context_parts).encode()
        
        # Derive key using HKDF
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,  # 256-bit key
            salt=b"iacherie_tenant_isolation_salt_v1",
            info=context
        )
        
        derived_key = hkdf.derive(self.master_tenant_key)
        
        return derived_key

    def _create_isolation_tags(self,
                              tenant_id: str,
                              scope: KeyScope,
                              creator_id: Optional[str],
                              content_type: Optional[str]) -> List[str]:
        """Create isolation tags for access control."""
        tags = [f"tenant:{tenant_id}", f"scope:{scope.value}"]
        
        if creator_id:
            tags.append(f"creator:{creator_id}")
        if content_type:
            tags.append(f"content_type:{content_type}")
        
        return tags

    async def get_tenant_key(self,
                            tenant_id: str,
                            key_id: str,
                            requester_id: str,
                            access_context: Dict[str, Any]) -> Optional[TenantKey]:
        """
        Retrieve a tenant key with isolation enforcement.
        
        Args:
            tenant_id: Tenant ID
            key_id: Key ID to retrieve
            requester_id: ID of the requesting entity
            access_context: Context for access control
            
        Returns:
            TenantKey if authorized, None otherwise
        """
        try:
            # Validate tenant exists
            if tenant_id not in self.tenant_profiles:
                raise ValueError(f"Tenant not found: {tenant_id}")
            
            # Validate key exists
            if (tenant_id not in self.tenant_keys or 
                key_id not in self.tenant_keys[tenant_id]):
                return None
            
            tenant_key = self.tenant_keys[tenant_id][key_id]
            
            # Check key expiration
            if tenant_key.expires_at and tenant_key.expires_at < datetime.utcnow():
                self.logger.warning(f"Attempted access to expired key: {key_id}")
                return None
            
            # Enforce isolation boundaries
            if not await self._check_isolation_access(tenant_key, requester_id, access_context):
                self.logger.warning(f"Isolation boundary violation: {key_id} by {requester_id}")
                return None
            
            # Update access count
            tenant_key.access_count += 1
            
            # Log access
            await self._log_tenant_operation("KEY_ACCESSED", tenant_id, requester_id, {
                "key_id": key_id,
                "access_count": tenant_key.access_count,
                "access_context": access_context
            })
            
            return tenant_key
            
        except Exception as e:
            self.logger.error(f"Tenant key retrieval failed: {e}")
            return None

    async def _check_isolation_access(self,
                                     tenant_key: TenantKey,
                                     requester_id: str,
                                     access_context: Dict[str, Any]) -> bool:
        """Check if access violates isolation boundaries."""
        # Check tenant boundary
        requester_tenant = access_context.get("tenant_id")
        if requester_tenant != tenant_key.tenant_id:
            # Cross-tenant access requires special authorization
            return await self._check_cross_tenant_access(tenant_key, requester_id, access_context)
        
        # Check scope-specific boundaries
        if tenant_key.key_scope == KeyScope.CREATOR_SPECIFIC:
            requester_creator = access_context.get("creator_id")
            if requester_creator != tenant_key.creator_id:
                return False
        
        elif tenant_key.key_scope == KeyScope.CONTENT_SPECIFIC:
            requester_creator = access_context.get("creator_id")
            requester_content_type = access_context.get("content_type")
            if (requester_creator != tenant_key.creator_id or 
                requester_content_type != tenant_key.content_type):
                return False
        
        elif tenant_key.key_scope == KeyScope.SESSION_SPECIFIC:
            requester_session = access_context.get("session_id")
            expected_session = tenant_key.key_metadata.get("session_id")
            if requester_session != expected_session:
                return False
        
        return True

    async def _check_cross_tenant_access(self,
                                        tenant_key: TenantKey,
                                        requester_id: str,
                                        access_context: Dict[str, Any]) -> bool:
        """Check cross-tenant access authorization."""
        if not self.config.get("cross_tenant_access_enabled", False):
            return False
        
        source_tenant = access_context.get("tenant_id")
        target_tenant = tenant_key.tenant_id
        
        # Check if there's an approved cross-tenant access request
        for request in self.cross_tenant_requests.values():
            if (request.source_tenant_id == source_tenant and
                request.target_tenant_id == target_tenant and
                request.approval_status == "approved" and
                request.expires_at > datetime.utcnow()):
                return True
        
        return False

    async def request_cross_tenant_access(self,
                                         source_tenant_id: str,
                                         target_tenant_id: str,
                                         requested_resource: str,
                                         access_type: str,
                                         justification: str,
                                         requester_id: str,
                                         duration_hours: int = 24) -> str:
        """
        Request cross-tenant access permission.
        
        Args:
            source_tenant_id: Requesting tenant ID
            target_tenant_id: Target tenant ID
            requested_resource: Resource being requested
            access_type: Type of access (read, write, etc.)
            justification: Business justification
            requester_id: ID of requester
            duration_hours: Duration of access in hours
            
        Returns:
            Request ID
        """
        try:
            request_id = f"cross_tenant_{secrets.token_hex(8)}"
            
            request = CrossTenantAccessRequest(
                request_id=request_id,
                source_tenant_id=source_tenant_id,
                target_tenant_id=target_tenant_id,
                requested_resource=requested_resource,
                access_type=access_type,
                justification=justification,
                requester_id=requester_id,
                approval_status="pending",
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=duration_hours)
            )
            
            self.cross_tenant_requests[request_id] = request
            
            # Log request
            await self._log_tenant_operation("CROSS_TENANT_REQUEST", source_tenant_id, requester_id, {
                "request_id": request_id,
                "target_tenant_id": target_tenant_id,
                "requested_resource": requested_resource,
                "justification": justification
            })
            
            self.logger.info(f"Cross-tenant access requested: {request_id}")
            return request_id
            
        except Exception as e:
            self.logger.error(f"Cross-tenant access request failed: {e}")
            raise

    async def isolate_tenant_keys(self, tenant_id: str) -> Dict[str, Any]:
        """
        Perform immediate isolation of all tenant keys.
        
        Args:
            tenant_id: Tenant to isolate
            
        Returns:
            Isolation results
        """
        try:
            if tenant_id not in self.tenant_profiles:
                raise ValueError(f"Tenant not found: {tenant_id}")
            
            isolated_count = 0
            namespace_count = 0
            
            # Mark tenant as inactive
            self.tenant_profiles[tenant_id].active = False
            
            # Revoke all cross-tenant access
            revoked_requests = []
            for request_id, request in self.cross_tenant_requests.items():
                if (request.source_tenant_id == tenant_id or 
                    request.target_tenant_id == tenant_id):
                    request.approval_status = "revoked"
                    revoked_requests.append(request_id)
            
            # Count isolated keys and namespaces
            if tenant_id in self.tenant_keys:
                isolated_count = len(self.tenant_keys[tenant_id])
            
            if tenant_id in self.tenant_namespaces:
                namespace_count = len(self.tenant_namespaces[tenant_id])
            
            isolation_result = {
                "tenant_id": tenant_id,
                "isolation_timestamp": datetime.utcnow().isoformat(),
                "keys_isolated": isolated_count,
                "namespaces_isolated": namespace_count,
                "cross_tenant_requests_revoked": len(revoked_requests),
                "isolation_status": "complete"
            }
            
            # Log isolation
            await self._log_tenant_operation("TENANT_ISOLATED", tenant_id, "system", isolation_result)
            
            self.logger.info(f"Tenant isolated: {tenant_id}")
            return isolation_result
            
        except Exception as e:
            self.logger.error(f"Tenant isolation failed: {e}")
            raise

    async def monitor_isolation_boundaries(self) -> Dict[str, Any]:
        """Monitor tenant isolation boundary violations."""
        try:
            violations = []
            metrics = {
                "total_tenants": len(self.tenant_profiles),
                "total_keys": sum(len(keys) for keys in self.tenant_keys.values()),
                "cross_tenant_requests": len(self.cross_tenant_requests),
                "isolation_violations": 0,
                "boundary_checks_performed": 0
            }
            
            # Check for potential isolation violations
            for tenant_id, tenant_keys in self.tenant_keys.items():
                for key_id, tenant_key in tenant_keys.items():
                    metrics["boundary_checks_performed"] += 1
                    
                    # Check for cross-tenant key access patterns
                    if tenant_key.access_count > 1000:  # High access threshold
                        violation = {
                            "type": "high_access_pattern",
                            "tenant_id": tenant_id,
                            "key_id": key_id,
                            "access_count": tenant_key.access_count,
                            "risk_level": "medium"
                        }
                        violations.append(violation)
                        metrics["isolation_violations"] += 1
                    
                    # Check for expired keys still being accessed
                    if (tenant_key.expires_at and 
                        tenant_key.expires_at < datetime.utcnow() and
                        tenant_key.access_count > 0):
                        violation = {
                            "type": "expired_key_access",
                            "tenant_id": tenant_id,
                            "key_id": key_id,
                            "expires_at": tenant_key.expires_at.isoformat(),
                            "risk_level": "high"
                        }
                        violations.append(violation)
                        metrics["isolation_violations"] += 1
            
            # Check cross-tenant request patterns
            pending_requests = [r for r in self.cross_tenant_requests.values() 
                              if r.approval_status == "pending"]
            
            if len(pending_requests) > 10:  # Too many pending requests
                violation = {
                    "type": "excessive_cross_tenant_requests",
                    "pending_count": len(pending_requests),
                    "risk_level": "medium"
                }
                violations.append(violation)
                metrics["isolation_violations"] += 1
            
            metrics["violations"] = violations
            metrics["monitoring_timestamp"] = datetime.utcnow().isoformat()
            
            # Store metrics
            self.isolation_metrics = metrics
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Isolation monitoring failed: {e}")
            raise

    async def get_tenant_isolation_status(self, tenant_id: str) -> Dict[str, Any]:
        """Get detailed isolation status for a tenant."""
        try:
            if tenant_id not in self.tenant_profiles:
                raise ValueError(f"Tenant not found: {tenant_id}")
            
            tenant_profile = self.tenant_profiles[tenant_id]
            
            # Count keys by scope
            key_counts = {}
            total_keys = 0
            
            if tenant_id in self.tenant_keys:
                for key in self.tenant_keys[tenant_id].values():
                    scope = key.key_scope.value
                    key_counts[scope] = key_counts.get(scope, 0) + 1
                    total_keys += 1
            
            # Count namespaces
            namespace_count = len(self.tenant_namespaces.get(tenant_id, {}))
            
            # Cross-tenant access info
            cross_tenant_info = {
                "outbound_requests": len([r for r in self.cross_tenant_requests.values() 
                                        if r.source_tenant_id == tenant_id]),
                "inbound_requests": len([r for r in self.cross_tenant_requests.values() 
                                       if r.target_tenant_id == tenant_id]),
                "active_grants": len([r for r in self.cross_tenant_requests.values() 
                                    if (r.source_tenant_id == tenant_id or r.target_tenant_id == tenant_id) 
                                    and r.approval_status == "approved"])
            }
            
            return {
                "tenant_id": tenant_id,
                "tenant_name": tenant_profile.tenant_name,
                "tier": tenant_profile.tier.value,
                "isolation_level": tenant_profile.isolation_level.value,
                "active": tenant_profile.active,
                "total_keys": total_keys,
                "keys_by_scope": key_counts,
                "total_namespaces": namespace_count,
                "cross_tenant_access": cross_tenant_info,
                "geographic_region": tenant_profile.geographic_region,
                "compliance_requirements": tenant_profile.compliance_requirements,
                "last_updated": tenant_profile.updated_at.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get tenant isolation status: {e}")
            raise

    async def _log_tenant_operation(self, operation: str, tenant_id: str, actor_id: str, details: Dict[str, Any]):
        """Log tenant operation for audit trail."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "tenant_id": tenant_id,
            "actor_id": actor_id,
            "details": details
        }
        
        # In production, send to audit system
        self.logger.info(f"Tenant operation logged: {operation} for tenant {tenant_id}")

    async def cleanup(self):
        """Cleanup multi-tenant isolator resources."""
        try:
            # Securely clear sensitive data
            for tenant_keys in self.tenant_keys.values():
                for key in tenant_keys.values():
                    key.key_material = b""
            
            self.tenant_keys.clear()
            self.tenant_namespaces.clear()
            self.cross_tenant_requests.clear()
            
            # Clear master key
# SECURITY: # SECURITY: self.master_tenant_key = b"" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
            
            self.logger.info("Multi Tenant Key Isolator cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Multi-tenant isolator cleanup failed: {e}")


# Creator Economy Integration Functions
async def setup_creator_tenant_isolation(creator_id: str,
                                         creator_type: str,
                                         tier: TenantTier,
                                         content_types: List[str],
                                         isolator: MultiTenantKeyIsolator) -> Dict[str, Any]:
    """Setup tenant isolation for creator."""
    # Register creator as individual tenant
    tenant_id = await isolator.register_tenant(
        tenant_name=f"Creator_{creator_id}",
        tenant_type=TenantType.INDIVIDUAL_CREATOR,
        tier=tier,
        geographic_region="US",  # Would be determined by creator location
        compliance_requirements=["GDPR", "CCPA", "DMCA"],
        data_residency_rules={"user_data": "same_region", "content": "global"}
    )
    
    # Create content-specific namespaces
    namespace_ids = {}
    for content_type in content_types:
        namespace_id = await isolator.create_key_namespace(
            tenant_id=tenant_id,
            namespace_name=f"{content_type}_protection",
            scope=KeyScope.CONTENT_SPECIFIC,
            encryption_domain=content_type,
            allowed_operations=["encrypt", "decrypt", "watermark", "sign"]
        )
        namespace_ids[content_type] = namespace_id
    
    return {
        "tenant_id": tenant_id,
        "namespace_ids": namespace_ids,
        "isolation_level": isolator.tenant_profiles[tenant_id].isolation_level.value
    }


# Export main classes and functions
__all__ = [
    "MultiTenantKeyIsolator",
    "TenantTier",
    "IsolationLevel",
    "TenantType",
    "KeyScope",
    "TenantProfile",
    "TenantKeyNamespace",
    "TenantKey",
    "CrossTenantAccessRequest",
    "setup_creator_tenant_isolation"
]